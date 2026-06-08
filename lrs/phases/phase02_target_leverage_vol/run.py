from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lrs.lib.backtest import (  # noqa: E402
    build_sma_signal,
    build_weekly_lagged_weights,
    clean_weights,
    constant_weight_frame,
    equity_curve,
    fmt_num,
    fmt_pct,
    fmt_pp,
    fmt_x,
    load_price_frame,
    md_table,
    metrics_from_returns,
    relative_stats,
    simulate_weight_frame,
    weights_label,
)


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase02_target_leverage_vol.csv"

TARGET_LEVERAGES = [1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00]

RISK_OFF_SPECS: list[dict[str, object]] = [
    {"name": "CASHX", "weights": {"CASHX": 1.0}},
    {"name": "ZROZ", "weights": {"ZROZSIM": 1.0}},
    {"name": "50 ZROZ / 50 GLD", "weights": {"ZROZSIM": 0.50, "GLDSIM": 0.50}},
    {"name": "40 ZROZ / 40 GLD / 20 IEF", "weights": {"ZROZSIM": 0.40, "GLDSIM": 0.40, "IEFSIM": 0.20}},
    {"name": "50 ZROZ / 25 GLD / 25 CASH", "weights": {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25}},
]

VOL_SPECS: list[dict[str, object]] = [
    {"name": "none", "window": 0, "threshold": None},
    {"name": "RV21 <= 40%", "window": 21, "threshold": 0.40},
    {"name": "RV63 <= 40%", "window": 63, "threshold": 0.40},
    {"name": "RV21 <= 30%", "window": 21, "threshold": 0.30},
    {"name": "RV63 <= 30%", "window": 63, "threshold": 0.30},
]

BRANCHES = [
    {
        "branch": "SPY",
        "underlying": "SPYSIM",
        "lev2": "SSOSIM",
        "lev3": "UPROSIM",
    },
    {
        "branch": "QQQ",
        "underlying": "QQQSIM",
        "lev2": "QLDSIM",
        "lev3": "TQQQSIM",
    },
]


@dataclass
class BranchContext:
    branch: dict[str, str]
    prices: pd.DataFrame
    returns: pd.DataFrame
    sma_signal: pd.Series
    underlying_taxed: pd.Series
    underlying_gross: pd.Series
    underlying_metrics: object
    benchmark_by_l: dict[float, pd.Series]
    benchmark_metrics_by_l: dict[float, object]


def branch_assets(branch: dict[str, str]) -> list[str]:
    assets = {branch["underlying"], branch["lev2"], branch["lev3"], "CASHX", "GLDSIM", "IEFSIM", "ZROZSIM"}
    return sorted(assets)


def target_leverage_weights(branch: dict[str, str], target_leverage: float) -> dict[str, float]:
    """Map target leverage to adjacent ETF sleeves without external margin.

    This keeps the leverage mechanism explicit while avoiding negative cash;
    the LRS premise remains Gayed-style levered risk-on exposure
    `[leverage_for_the_long_run, p.13]`.
    """

    if target_leverage < 1.0 or target_leverage > 3.0:
        raise ValueError(f"target leverage out of range: {target_leverage}")
    if target_leverage <= 2.0:
        return clean_weights(
            {
                branch["underlying"]: 2.0 - target_leverage,
                branch["lev2"]: target_leverage - 1.0,
            }
        )
    return clean_weights(
        {
            branch["lev2"]: 3.0 - target_leverage,
            branch["lev3"]: target_leverage - 2.0,
        }
    )


def drawdown_tier(mdd: float) -> str:
    if mdd >= -0.40:
        return "preferred"
    if mdd >= -0.50:
        return "tolerable"
    if mdd >= -0.65:
        return "warning"
    return "ruin"


def drawdown(returns: pd.Series) -> pd.Series:
    equity = equity_curve(returns)
    return equity / equity.cummax() - 1.0


def build_context(branch: dict[str, str]) -> BranchContext:
    prices = load_price_frame(branch_assets(branch))
    returns = prices.pct_change().dropna()
    prices = prices.reindex(returns.index)
    sma_signal = build_sma_signal(prices[branch["underlying"]], 200).reindex(returns.index).fillna(False)
    underlying_frame = constant_weight_frame(returns.index, {branch["underlying"]: 1.0})
    underlying_taxed, _ = simulate_weight_frame(returns, underlying_frame, taxable=True)
    underlying_gross, _ = simulate_weight_frame(returns, underlying_frame, taxable=False)
    benchmark_by_l: dict[float, pd.Series] = {}
    benchmark_metrics_by_l: dict[float, object] = {}
    for target_leverage in TARGET_LEVERAGES:
        frame = constant_weight_frame(returns.index, target_leverage_weights(branch, target_leverage))
        taxed, _ = simulate_weight_frame(returns, frame, taxable=True)
        benchmark_by_l[target_leverage] = taxed
        benchmark_metrics_by_l[target_leverage] = metrics_from_returns(taxed)
    return BranchContext(
        branch=branch,
        prices=prices,
        returns=returns,
        sma_signal=sma_signal,
        underlying_taxed=underlying_taxed,
        underlying_gross=underlying_gross,
        underlying_metrics=metrics_from_returns(underlying_taxed),
        benchmark_by_l=benchmark_by_l,
        benchmark_metrics_by_l=benchmark_metrics_by_l,
    )


def vol_gate(context: BranchContext, spec: dict[str, object]) -> pd.Series:
    if spec["threshold"] is None:
        return pd.Series(True, index=context.returns.index)
    window = int(spec["window"])
    threshold = float(spec["threshold"])
    underlying_returns = context.returns[context.branch["underlying"]]
    realized_vol = underlying_returns.rolling(window).std(ddof=0).shift(1) * np.sqrt(252.0)
    return (realized_vol <= threshold).reindex(context.returns.index).fillna(False)


def desired_targets(
    context: BranchContext,
    target_leverage: float,
    risk_off_weights: dict[str, float],
    vol_spec: dict[str, object],
) -> pd.DataFrame:
    risk_on = target_leverage_weights(context.branch, target_leverage)
    signal = context.sma_signal & vol_gate(context, vol_spec)
    assets = sorted(set(risk_on) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    return desired


def simulate_candidate(
    context: BranchContext,
    target_leverage: float,
    risk_off_spec: dict[str, object],
    vol_spec: dict[str, object],
    lag_days: int,
) -> dict[str, object]:
    risk_off_weights = clean_weights(risk_off_spec["weights"])  # type: ignore[arg-type]
    risk_on_weights = target_leverage_weights(context.branch, target_leverage)
    desired = desired_targets(context, target_leverage, risk_off_weights, vol_spec)
    weights, schedule_summary = build_weekly_lagged_weights(
        desired,
        lag_days=lag_days,
        risk_on_weights=risk_on_weights,
    )
    gross, _ = simulate_weight_frame(context.returns, weights, taxable=False)
    taxed, tax_summary = simulate_weight_frame(context.returns, weights, taxable=True)
    taxed_metrics = metrics_from_returns(taxed)
    gross_metrics = metrics_from_returns(gross)
    benchmark = context.benchmark_by_l[target_leverage]
    benchmark_metrics = context.benchmark_metrics_by_l[target_leverage]
    rel_underlying = relative_stats(taxed, context.underlying_taxed)
    rel_benchmark = relative_stats(taxed, benchmark)
    cagr_spread = taxed_metrics.cagr - context.underlying_metrics.cagr
    drawdown_component = max(-1.0, min(1.0, (taxed_metrics.mdd + 0.65) / 0.25))
    score = (
        6.0 * cagr_spread
        + 2.25 * taxed_metrics.calmar
        + 0.75 * taxed_metrics.sortino
        + 1.00 * rel_underlying.get("hit_10y", 0.0)
        + 1.75 * drawdown_component
        + 0.25 * rel_underlying["worst_relative_drawdown"]
        - 0.10 * float(tax_summary["turnover_per_year"])
    )
    return {
        "branch": context.branch["branch"],
        "target_leverage": target_leverage,
        "lag_days": lag_days,
        "lookback": 200,
        "cadence": "weekly",
        "risk_on": weights_label(risk_on_weights),
        "risk_off_name": risk_off_spec["name"],
        "risk_off_weights": weights_label(risk_off_weights),
        "vol_filter": vol_spec["name"],
        "start": taxed_metrics.start,
        "end": taxed_metrics.end,
        "years": taxed_metrics.years,
        "score": score,
        "drawdown_tier": drawdown_tier(taxed_metrics.mdd),
        "practical_pass": bool(cagr_spread > 0.0 and taxed_metrics.mdd >= -0.50 and rel_underlying["terminal_vs_benchmark"] > 1.0),
        "gross_cagr": gross_metrics.cagr,
        "gross_mdd": gross_metrics.mdd,
        "taxed_cagr": taxed_metrics.cagr,
        "taxed_mdd": taxed_metrics.mdd,
        "taxed_sharpe": taxed_metrics.sharpe,
        "taxed_sortino": taxed_metrics.sortino,
        "taxed_calmar": taxed_metrics.calmar,
        "taxed_terminal": taxed_metrics.terminal,
        "underlying_taxed_cagr": context.underlying_metrics.cagr,
        "underlying_taxed_mdd": context.underlying_metrics.mdd,
        "underlying_taxed_terminal": context.underlying_metrics.terminal,
        "levered_taxed_cagr": benchmark_metrics.cagr,
        "levered_taxed_mdd": benchmark_metrics.mdd,
        "levered_taxed_terminal": benchmark_metrics.terminal,
        "cagr_spread_vs_underlying": cagr_spread,
        "mdd_spread_vs_underlying": taxed_metrics.mdd - context.underlying_metrics.mdd,
        "terminal_vs_underlying": rel_underlying["terminal_vs_benchmark"],
        "terminal_vs_levered_bh": rel_benchmark["terminal_vs_benchmark"],
        "worst_relative_dd_vs_underlying": rel_underlying["worst_relative_drawdown"],
        "worst_relative_dd_vs_levered_bh": rel_benchmark["worst_relative_drawdown"],
        "hit_3y_vs_underlying": rel_underlying.get("hit_3y", pd.NA),
        "hit_5y_vs_underlying": rel_underlying.get("hit_5y", pd.NA),
        "hit_10y_vs_underlying": rel_underlying.get("hit_10y", pd.NA),
        "hit_15y_vs_underlying": rel_underlying.get("hit_15y", pd.NA),
        "hit_20y_vs_underlying": rel_underlying.get("hit_20y", pd.NA),
        "turnover_per_year": tax_summary["turnover_per_year"],
        "trade_count": tax_summary["trade_count"],
        "state_changes": schedule_summary["state_changes"],
        "delayed_entries": schedule_summary["delayed_entries"],
        "pct_risk_on_days": schedule_summary["pct_risk_on_days"],
        "tax_paid_pct_initial": tax_summary["total_tax_paid_pct_initial"],
        "tax_events": tax_summary["tax_events"],
        "final_taxed_equity": float(equity_curve(taxed).iloc[-1]),
        "final_underlying_taxed_equity": float(equity_curve(context.underlying_taxed).iloc[-1]),
        "final_levered_taxed_equity": float(equity_curve(benchmark).iloc[-1]),
        "gross_vs_tax_cagr_drag": gross_metrics.cagr - taxed_metrics.cagr,
    }


def simulate_paths_for_row(row: pd.Series) -> dict[str, pd.Series]:
    branch = next(b for b in BRANCHES if b["branch"] == row["branch"])
    context = build_context(branch)
    risk_off_spec = next(spec for spec in RISK_OFF_SPECS if spec["name"] == row["risk_off_name"])
    vol_spec = next(spec for spec in VOL_SPECS if spec["name"] == row["vol_filter"])
    risk_off_weights = clean_weights(risk_off_spec["weights"])  # type: ignore[arg-type]
    desired = desired_targets(context, float(row["target_leverage"]), risk_off_weights, vol_spec)
    weights, _ = build_weekly_lagged_weights(
        desired,
        lag_days=int(row["lag_days"]),
        risk_on_weights=target_leverage_weights(context.branch, float(row["target_leverage"])),
    )
    taxed, _ = simulate_weight_frame(context.returns, weights, taxable=True)
    benchmark = context.benchmark_by_l[float(row["target_leverage"])]
    return {"strategy": taxed, "underlying": context.underlying_taxed, "levered": benchmark}


def plot_candidate_panel(row: pd.Series) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paths = simulate_paths_for_row(row)
    aligned = pd.concat(
        {
            "LRS": equity_curve(paths["strategy"]),
            "Underlying B&H": equity_curve(paths["underlying"]),
            "Target-Lev B&H": equity_curve(paths["levered"]),
        },
        axis=1,
    ).dropna()
    dd = pd.concat(
        {
            "LRS": drawdown(paths["strategy"]),
            "Underlying B&H": drawdown(paths["underlying"]),
            "Target-Lev B&H": drawdown(paths["levered"]),
        },
        axis=1,
    ).dropna()
    relative = aligned["LRS"] / aligned["Underlying B&H"]

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    aligned.plot(ax=axes[0], logy=True, linewidth=1.2)
    axes[0].set_title(
        f"{row['branch']} L={float(row['target_leverage']):.2f} lag={int(row['lag_days'])} "
        f"off={row['risk_off_name']} vol={row['vol_filter']}"
    )
    axes[0].set_ylabel("Growth of $1")
    axes[0].grid(True, alpha=0.3)
    (dd * 100.0).plot(ax=axes[1], linewidth=1.0)
    axes[1].set_title("Drawdown")
    axes[1].set_ylabel("Drawdown (%)")
    axes[1].grid(True, alpha=0.3)
    relative.plot(ax=axes[2], linewidth=1.2, color="tab:blue")
    axes[2].axhline(1.0, color="black", linewidth=0.8, linestyle="--")
    axes[2].set_title("LRS relative equity vs underlying")
    axes[2].set_ylabel("Relative equity")
    axes[2].grid(True, alpha=0.3)
    fig.tight_layout()
    safe_off = str(row["risk_off_name"]).lower().replace(" ", "_").replace("/", "_")
    safe_vol = str(row["vol_filter"]).lower().replace(" ", "_").replace("<=", "le").replace("%", "pct")
    out = PLOTS / f"phase02_{str(row['branch']).lower()}_l{float(row['target_leverage']):.2f}_lag{int(row['lag_days'])}_{safe_off}_{safe_vol}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))
    for branch, subset in results.groupby("branch", sort=True):
        ax.scatter(
            subset["taxed_mdd"] * 100.0,
            subset["taxed_cagr"] * 100.0,
            s=22,
            alpha=0.55,
            label=branch,
        )
    ax.axvline(-40.0, color="green", linestyle="--", linewidth=0.9, label="preferred 40%")
    ax.axvline(-50.0, color="black", linestyle="--", linewidth=0.9, label="tolerable 50%")
    ax.axvline(-65.0, color="red", linestyle=":", linewidth=0.9, label="ruin 65%")
    ax.set_title("Phase 2 target leverage / volatility frontier")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase02_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_leverage_summary(results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    best = results.sort_values("score", ascending=False).groupby(["branch", "target_leverage"], sort=True).head(1)
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for branch, subset in best.groupby("branch", sort=True):
        subset = subset.sort_values("target_leverage")
        axes[0].plot(subset["target_leverage"], subset["taxed_cagr"] * 100.0, marker="o", label=branch)
        axes[1].plot(subset["target_leverage"], subset["taxed_mdd"] * 100.0, marker="o", label=branch)
    axes[0].set_title("Best score by target leverage - CAGR")
    axes[0].set_ylabel("CAGR (%)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[1].set_title("Best score by target leverage - MDD")
    axes[1].set_xlabel("Target leverage")
    axes[1].set_ylabel("MDD (%)")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase02_best_by_leverage.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def make_plots(results: pd.DataFrame) -> list[dict[str, str]]:
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    top_by_branch = results.sort_values("score", ascending=False).groupby("branch", sort=True).head(1)
    for _, row in top_by_branch.iterrows():
        path = plot_candidate_panel(row)
        rows.append({"Plot": f"{row['branch']} best score", "File": f"[plots/{path.name}](plots/{path.name})"})
    frontier = plot_frontier(results)
    rows.append({"Plot": "Risk/return frontier", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    leverage = plot_leverage_summary(results)
    rows.append({"Plot": "Best by target leverage", "File": f"[plots/{leverage.name}](plots/{leverage.name})"})
    return rows


def formatted_rows(frame: pd.DataFrame, limit: int = 30) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Branch": row["branch"],
                "L": fmt_num(row["target_leverage"], 2),
                "Risk-Off": row["risk_off_name"],
                "Vol": row["vol_filter"],
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Spread vs U": fmt_pp(row["cagr_spread_vs_underlying"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
                "Hit 10y": fmt_pct(row["hit_10y_vs_underlying"], 1),
                "Pass": "yes" if row["practical_pass"] else "no",
            }
        )
    return rows


def best_by_branch_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "L": fmt_num(row["target_leverage"], 2),
                "Risk-Off": row["risk_off_name"],
                "Vol": row["vol_filter"],
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
            }
        )
    return rows


def best_by_leverage_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    best = results.sort_values("score", ascending=False).groupby(["branch", "target_leverage"], sort=True).head(1)
    for _, row in best.sort_values(["branch", "target_leverage"]).iterrows():
        rows.append(
            {
                "Branch": row["branch"],
                "L": fmt_num(row["target_leverage"], 2),
                "Risk-Off": row["risk_off_name"],
                "Vol": row["vol_filter"],
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
            }
        )
    return rows


def test_window_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Start": row["start"],
                "End": row["end"],
                "Years": fmt_num(row["years"], 1),
                "Underlying CAGR": fmt_pct(row["underlying_taxed_cagr"]),
                "Underlying MDD": fmt_pct(row["underlying_taxed_mdd"]),
            }
        )
    return rows


def write_report(results: pd.DataFrame, plot_rows: list[dict[str, str]]) -> None:
    top = results.iloc[0]
    practical = results[results["practical_pass"]]
    preferred = results[results["drawdown_tier"] == "preferred"]
    qqq_practical = practical[practical["branch"] == "QQQ"]
    sections = [
        "# Phase 2 - Target Leverage And Volatility Throttle\n\n"
        "Status: research-only leverage/throttle sweep. This report does not authorize deployment, paper trading or a mandate change.\n\n"
        "Method references: the LRS rule remains Gayed SMA200 risk-on/risk-off `[leverage_for_the_long_run, p.13]`. The volatility throttle uses Gayed's observation that high volatility is the enemy of leveraged compounding and that above roughly 40% annualized volatility the constant leverage trap dominates `[leverage_for_the_long_run, p.4-7]`. Target leverage and vol scaling follow the broader position-sizing principle that leverage should be reduced when risk rises `[systematic_trading, p.137-148]`.\n\n"
        "## Executive Conclusion\n\n"
        f"Phase 2 evaluated `{len(results):,}` rows: SPY/QQQ x {len(TARGET_LEVERAGES)} target leverages x {len(RISK_OFF_SPECS)} risk-off sleeves x {len(VOL_SPECS)} volatility filters x lags `0..5`. "
        f"Top score row: `{top['branch']}` L`{float(top['target_leverage']):.2f}` risk-off `{top['risk_off_name']}` vol `{top['vol_filter']}` lag `{int(top['lag_days'])}` with after-tax CAGR {fmt_pct(top['taxed_cagr'])}, MDD {fmt_pct(top['taxed_mdd'])}, Calmar {fmt_num(top['taxed_calmar'])}, terminal {fmt_x(top['terminal_vs_underlying'])} vs underlying. "
        f"Practical-pass rows (`MDD >= -50%` and after-tax underlying outperformance): `{len(practical):,}`. Preferred drawdown rows (`MDD >= -40%`): `{len(preferred):,}`. QQQ practical-pass rows: `{len(qqq_practical):,}`.\n\n"
        "Practical read: this phase determines whether drawdown can be reduced by changing exposure geometry before adding multi-indicator votes.\n\n"
        "## Source And Rules\n\n"
        "| Item | Value |\n|---|---|\n"
        "| Data | `data/testfolio/cache/history.parquet` |\n"
        "| Signal | `underlying.shift(1) > SMA200.shift(1)` plus optional realized-vol gate |\n"
        "| Target leverage | `1.25x..3.00x`, adjacent ETF ladder, no negative cash |\n"
        "| Risk-off sleeves | selected Phase 1 sleeves |\n"
        "| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |\n"
        "| Tax | annual 15% DARF on realized net gains plus final liquidation |\n\n"
    ]
    sections.append("## Test Windows\n\n" + md_table(test_window_rows(results), ["Branch", "Start", "End", "Years", "Underlying CAGR", "Underlying MDD"]))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    cols = ["Branch", "L", "Risk-Off", "Vol", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Spread vs U", "Terminal/U", "Hit 10y", "Pass"]
    sections.append("## Top Ranked Rows\n\n" + md_table(formatted_rows(results, 35), cols))
    sections.append("## Best Row By Branch\n\n" + md_table(best_by_branch_rows(results), ["Branch", "L", "Risk-Off", "Vol", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Terminal/U"]))
    sections.append("## Best Row By Target Leverage\n\n" + md_table(best_by_leverage_rows(results), ["Branch", "L", "Risk-Off", "Vol", "Lag", "Tier", "CAGR", "MDD", "Calmar"]))
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Did any row meet the <=50% MDD practical target and beat underlying? | {'Yes' if not practical.empty else 'No'}. |\n"
        f"| Did any row meet preferred <=40% MDD? | {'Yes' if not preferred.empty else 'No'}. |\n"
        f"| Did QQQ leave ruin territory under the practical target? | {'Yes' if not qqq_practical.empty else 'No'}. |\n"
        "| Is this deployment-ready? | No. This is an exposure-geometry discovery phase only. |\n\n"
        "Next step: use the best exposure geometry as the base for either a bear-market inverse sleeve or a small pre-registered indicator vote.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    contexts = [build_context(branch) for branch in BRANCHES]
    rows = []
    for context in contexts:
        for target_leverage in TARGET_LEVERAGES:
            for risk_off_spec in RISK_OFF_SPECS:
                for vol_spec in VOL_SPECS:
                    for lag_days in range(6):
                        rows.append(simulate_candidate(context, target_leverage, risk_off_spec, vol_spec, lag_days))
    results = pd.DataFrame(rows).sort_values(
        ["practical_pass", "score", "terminal_vs_underlying", "taxed_calmar"],
        ascending=[False, False, False, False],
    )
    results.to_csv(CSV, index=False)
    plot_rows = make_plots(results)
    write_report(results, plot_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
