"""Phase 3A - sparse risk-on confirmation vote over the Phase 2 geometry.

Research-only. This runner does NOT authorize deployment, paper trading or any
mandate change. It tests whether a few *structurally distinct* risk-on
confirmation filters, each ANDed onto the Phase 2 base signal and compared
against a ``none`` control, improve the frontier without opening a broad
multi-indicator grid `[trading_systems_methods, p.939]`, `[advances_fin_ml,
p.208-211]`.

Signal per row::

    signal = sma_signal & vol_gate(base.vol) & confirm_gate(filter)

``filter = none`` reproduces the Phase 2 result for that base+lag exactly, which
doubles as a sanity check against ``lrs/results/phase02_target_leverage_vol.csv``.
Filters are tested one-at-a-time (no composite/vote-of-K combination yet).

Grid: 2 branches x 3 branch-specific bases x 9 filters x lag 0..5 = 324 rows.
"""
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
from lrs.lib.indicators import (  # noqa: E402
    adx_gate,
    clenow_gate,
    roc_gate,
    trend_hysteresis_gate,
)


PHASE_ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
REPORT = PHASE_ROOT / "REPORT.md"
PLOTS = PHASE_ROOT / "plots"
CSV = RESULTS / "phase03_sparse_risk_on_vote.csv"

BRANCHES = {
    "SPY": {"branch": "SPY", "underlying": "SPYSIM", "lev2": "SSOSIM", "lev3": "UPROSIM"},
    "QQQ": {"branch": "QQQ", "underlying": "QQQSIM", "lev2": "QLDSIM", "lev3": "TQQQSIM"},
}

# Named risk-off sleeves and vol throttles reused verbatim from Phase 2.
RISK_OFF_LIBRARY: dict[str, dict[str, float]] = {
    "50 ZROZ / 25 GLD / 25 CASH": {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25},
    "40 ZROZ / 40 GLD / 20 IEF": {"ZROZSIM": 0.40, "GLDSIM": 0.40, "IEFSIM": 0.20},
}

VOL_LIBRARY: dict[str, dict[str, object]] = {
    "RV21 <= 30%": {"name": "RV21 <= 30%", "window": 21, "threshold": 0.30},
    "RV63 <= 40%": {"name": "RV63 <= 40%", "window": 63, "threshold": 0.40},
}

# Phase 2 top per branch + 2 one-lever neighbours (leverage / risk-off / vol),
# to probe the neighbourhood and avoid single-point fragility `[advances_fin_ml,
# p.208-211]`.
BASE_SPECS: list[dict[str, object]] = [
    {"branch": "SPY", "name": "spy_top", "target_leverage": 2.00, "risk_off": "50 ZROZ / 25 GLD / 25 CASH", "vol": "RV21 <= 30%"},
    {"branch": "SPY", "name": "spy_lower_lev", "target_leverage": 1.75, "risk_off": "50 ZROZ / 25 GLD / 25 CASH", "vol": "RV21 <= 30%"},
    {"branch": "SPY", "name": "spy_alt_off", "target_leverage": 2.00, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV21 <= 30%"},
    {"branch": "QQQ", "name": "qqq_top", "target_leverage": 1.75, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV63 <= 40%"},
    {"branch": "QQQ", "name": "qqq_lower_lev", "target_leverage": 1.50, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV63 <= 40%"},
    {"branch": "QQQ", "name": "qqq_alt_vol", "target_leverage": 1.75, "risk_off": "40 ZROZ / 40 GLD / 20 IEF", "vol": "RV21 <= 30%"},
]

# Risk-on confirmation filters. `none` is the control; each family has two
# variants so the headline grid doubles as the sensitivity view.
FILTER_SPECS: list[dict[str, object]] = [
    {"name": "none", "family": "none", "kind": "none"},
    {"name": "clenow>0 w90", "family": "clenow", "kind": "clenow", "window": 90},
    {"name": "clenow>0 w120", "family": "clenow", "kind": "clenow", "window": 120},
    {"name": "roc126>0", "family": "roc", "kind": "roc", "lookback": 126},
    {"name": "roc252>0", "family": "roc", "kind": "roc", "lookback": 252},
    {"name": "hyst band5%", "family": "hysteresis", "kind": "hysteresis", "lookback": 200, "band": 0.05},
    {"name": "hyst band8%", "family": "hysteresis", "kind": "hysteresis", "lookback": 200, "band": 0.08},
    {"name": "adx>20", "family": "adx", "kind": "adx", "window": 14, "threshold": 20.0},
    {"name": "adx>25", "family": "adx", "kind": "adx", "window": 14, "threshold": 25.0},
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
    filter_gates: dict[str, pd.Series]


def branch_assets(branch: dict[str, str]) -> list[str]:
    assets = {branch["underlying"], branch["lev2"], branch["lev3"], "CASHX", "GLDSIM", "IEFSIM", "ZROZSIM"}
    return sorted(assets)


def target_leverage_weights(branch: dict[str, str], target_leverage: float) -> dict[str, float]:
    """Map target leverage to adjacent ETF sleeves without external margin.

    Same construction as Phase 2: the leverage mechanism stays explicit while
    avoiding negative cash `[leverage_for_the_long_run, p.13]`.
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


def build_filter_gate(prices: pd.Series, spec: dict[str, object]) -> pd.Series:
    """Dispatch a filter spec to its confirmation gate (all `.shift(1)`-lagged)."""
    kind = spec["kind"]
    if kind == "none":
        return pd.Series(True, index=prices.index)
    if kind == "clenow":
        return clenow_gate(prices, int(spec["window"]))
    if kind == "roc":
        return roc_gate(prices, int(spec["lookback"]))
    if kind == "hysteresis":
        return trend_hysteresis_gate(prices, int(spec["lookback"]), float(spec["band"]))
    if kind == "adx":
        return adx_gate(prices, int(spec["window"]), float(spec["threshold"]))
    raise ValueError(f"unknown filter kind: {kind}")


def base_leverages(branch_name: str) -> list[float]:
    return sorted({float(b["target_leverage"]) for b in BASE_SPECS if b["branch"] == branch_name})


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
    for target_leverage in base_leverages(branch["branch"]):
        frame = constant_weight_frame(returns.index, target_leverage_weights(branch, target_leverage))
        taxed, _ = simulate_weight_frame(returns, frame, taxable=True)
        benchmark_by_l[target_leverage] = taxed
        benchmark_metrics_by_l[target_leverage] = metrics_from_returns(taxed)
    underlying_prices = prices[branch["underlying"]]
    filter_gates: dict[str, pd.Series] = {}
    for spec in FILTER_SPECS:
        gate = build_filter_gate(underlying_prices, spec)
        filter_gates[str(spec["name"])] = gate.reindex(returns.index).fillna(False).astype(bool)
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
        filter_gates=filter_gates,
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
    filter_gate: pd.Series,
) -> pd.DataFrame:
    risk_on = target_leverage_weights(context.branch, target_leverage)
    gate = filter_gate.reindex(context.returns.index).fillna(False).astype(bool)
    signal = context.sma_signal & vol_gate(context, vol_spec) & gate
    assets = sorted(set(risk_on) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=context.returns.index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    return desired


def simulate_candidate(
    context: BranchContext,
    base: dict[str, object],
    filter_spec: dict[str, object],
    lag_days: int,
) -> dict[str, object]:
    target_leverage = float(base["target_leverage"])
    risk_off_weights = clean_weights(RISK_OFF_LIBRARY[str(base["risk_off"])])
    vol_spec = VOL_LIBRARY[str(base["vol"])]
    risk_on_weights = target_leverage_weights(context.branch, target_leverage)
    filter_gate = context.filter_gates[str(filter_spec["name"])]
    desired = desired_targets(context, target_leverage, risk_off_weights, vol_spec, filter_gate)
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
    # Phase 2 scoring kept verbatim for cross-phase comparability (user decision).
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
        "base_name": base["name"],
        "filter_name": filter_spec["name"],
        "filter_family": filter_spec["family"],
        "target_leverage": target_leverage,
        "lag_days": lag_days,
        "lookback": 200,
        "cadence": "weekly",
        "risk_on": weights_label(risk_on_weights),
        "risk_off_name": base["risk_off"],
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


def simulate_paths_for_row(row: pd.Series, context: BranchContext) -> dict[str, pd.Series]:
    base = next(b for b in BASE_SPECS if b["name"] == row["base_name"])
    filter_spec = next(spec for spec in FILTER_SPECS if spec["name"] == row["filter_name"])
    risk_off_weights = clean_weights(RISK_OFF_LIBRARY[str(base["risk_off"])])
    vol_spec = VOL_LIBRARY[str(base["vol"])]
    filter_gate = context.filter_gates[str(filter_spec["name"])]
    desired = desired_targets(context, float(base["target_leverage"]), risk_off_weights, vol_spec, filter_gate)
    weights, _ = build_weekly_lagged_weights(
        desired,
        lag_days=int(row["lag_days"]),
        risk_on_weights=target_leverage_weights(context.branch, float(base["target_leverage"])),
    )
    taxed, _ = simulate_weight_frame(context.returns, weights, taxable=True)
    benchmark = context.benchmark_by_l[float(base["target_leverage"])]
    return {"strategy": taxed, "underlying": context.underlying_taxed, "levered": benchmark}


def plot_candidate_panel(row: pd.Series, context: BranchContext) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paths = simulate_paths_for_row(row, context)
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
        f"{row['branch']} base={row['base_name']} filter={row['filter_name']} "
        f"L={float(row['target_leverage']):.2f} lag={int(row['lag_days'])}"
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
    safe_filter = str(row["filter_name"]).lower().replace(" ", "_").replace(">", "gt").replace("%", "pct")
    out = PLOTS / f"phase03_{str(row['branch']).lower()}_{row['base_name']}_{safe_filter}_lag{int(row['lag_days'])}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))
    for family, subset in results.groupby("filter_family", sort=True):
        ax.scatter(
            subset["taxed_mdd"] * 100.0,
            subset["taxed_cagr"] * 100.0,
            s=24,
            alpha=0.6,
            label=family,
        )
    ax.axvline(-40.0, color="green", linestyle="--", linewidth=0.9, label="preferred 40%")
    ax.axvline(-50.0, color="black", linestyle="--", linewidth=0.9, label="tolerable 50%")
    ax.set_title("Phase 3A frontier by filter family")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase03_frontier.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_filter_sensitivity(results: pd.DataFrame) -> Path:
    """Per branch, best-lag CAGR/MDD across filters on that branch's top base."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    filter_order = [str(spec["name"]) for spec in FILTER_SPECS]
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for branch, branch_rows in results.groupby("branch", sort=True):
        top_base = branch_rows.sort_values("score", ascending=False).iloc[0]["base_name"]
        base_rows = branch_rows[branch_rows["base_name"] == top_base]
        best_per_filter = base_rows.sort_values("score", ascending=False).groupby("filter_name", sort=False).head(1)
        best_per_filter = best_per_filter.set_index("filter_name").reindex(filter_order)
        label = f"{branch} ({top_base})"
        axes[0].plot(filter_order, best_per_filter["taxed_cagr"] * 100.0, marker="o", label=label)
        axes[1].plot(filter_order, best_per_filter["taxed_mdd"] * 100.0, marker="o", label=label)
    axes[0].set_title("Filter sensitivity (best lag) - after-tax CAGR")
    axes[0].set_ylabel("CAGR (%)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[1].set_title("Filter sensitivity (best lag) - MDD")
    axes[1].set_ylabel("MDD (%)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    for ax in axes:
        ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    out = PLOTS / "phase03_filter_sensitivity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def make_plots(results: pd.DataFrame, contexts: dict[str, BranchContext]) -> list[dict[str, str]]:
    PLOTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    top_by_branch = results.sort_values("score", ascending=False).groupby("branch", sort=True).head(1)
    for _, row in top_by_branch.iterrows():
        path = plot_candidate_panel(row, contexts[str(row["branch"])])
        rows.append({"Plot": f"{row['branch']} best score", "File": f"[plots/{path.name}](plots/{path.name})"})
    frontier = plot_frontier(results)
    rows.append({"Plot": "Frontier by filter family", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    sensitivity = plot_filter_sensitivity(results)
    rows.append({"Plot": "Filter sensitivity (top base)", "File": f"[plots/{sensitivity.name}](plots/{sensitivity.name})"})
    return rows


def formatted_rows(frame: pd.DataFrame, limit: int = 30) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Branch": row["branch"],
                "Base": row["base_name"],
                "Filter": row["filter_name"],
                "L": fmt_num(row["target_leverage"], 2),
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
                "Base": row["base_name"],
                "Filter": row["filter_name"],
                "L": fmt_num(row["target_leverage"], 2),
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
            }
        )
    return rows


def best_by_filter_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    best = results.sort_values("score", ascending=False).groupby(["branch", "filter_name"], sort=True).head(1)
    for _, row in best.sort_values(["branch", "score"], ascending=[True, False]).iterrows():
        rows.append(
            {
                "Branch": row["branch"],
                "Filter": row["filter_name"],
                "Family": row["filter_family"],
                "Base": row["base_name"],
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Score": fmt_num(row["score"], 3),
            }
        )
    return rows


def filter_vs_none_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    """Per branch, on that branch's top base, compare each filter (best lag) to
    the `none` control on the same base. Answers: does any filter help?"""
    rows = []
    for branch, branch_rows in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        top_base = branch_rows.iloc[0]["base_name"]
        base_rows = branch_rows[branch_rows["base_name"] == top_base]
        best_per_filter = base_rows.sort_values("score", ascending=False).groupby("filter_name", sort=False).head(1)
        none_row = base_rows[base_rows["filter_name"] == "none"].sort_values("score", ascending=False).iloc[0]
        none_cagr = float(none_row["taxed_cagr"])
        none_mdd = float(none_row["taxed_mdd"])
        none_score = float(none_row["score"])
        ordered = best_per_filter.set_index("filter_name").reindex([str(s["name"]) for s in FILTER_SPECS]).dropna(subset=["taxed_cagr"])
        for filter_name, row in ordered.iterrows():
            rows.append(
                {
                    "Branch": branch,
                    "Base": top_base,
                    "Filter": filter_name,
                    "Lag": int(row["lag_days"]),
                    "CAGR": fmt_pct(row["taxed_cagr"]),
                    "dCAGR vs none": fmt_pp(float(row["taxed_cagr"]) - none_cagr),
                    "MDD": fmt_pct(row["taxed_mdd"]),
                    "dMDD vs none": fmt_pp(float(row["taxed_mdd"]) - none_mdd),
                    "dScore vs none": fmt_num(float(row["score"]) - none_score, 3),
                }
            )
    return rows


def hit_rate_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Base": row["base_name"],
                "Filter": row["filter_name"],
                "Hit 3y": fmt_pct(row["hit_3y_vs_underlying"], 1),
                "Hit 5y": fmt_pct(row["hit_5y_vs_underlying"], 1),
                "Hit 10y": fmt_pct(row["hit_10y_vs_underlying"], 1),
                "Hit 15y": fmt_pct(row["hit_15y_vs_underlying"], 1),
                "Hit 20y": fmt_pct(row["hit_20y_vs_underlying"], 1),
            }
        )
    return rows


def operational_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Base": row["base_name"],
                "Filter": row["filter_name"],
                "Turnover/yr": fmt_num(row["turnover_per_year"], 2),
                "Trades": int(row["trade_count"]),
                "Risk-on days": fmt_pct(row["pct_risk_on_days"], 1),
                "Tax paid % init": fmt_pct(row["tax_paid_pct_initial"], 1),
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


def _redundant_vs_none(results: pd.DataFrame, tol: float = 1e-9) -> list[str]:
    """Filters whose after-tax CAGR equals the `none` control for EVERY
    (branch, base, lag). Such a filter is structurally redundant under the AND
    framing: ANDing it onto the SMA200 gate cannot extend risk-on, so it only
    matters on days the SMA gate already blocks (where the AND erases it)."""
    key = ["branch", "base_name", "lag_days"]
    none = results[results["filter_name"] == "none"].set_index(key)["taxed_cagr"]
    redundant: list[str] = []
    for filter_name in [str(s["name"]) for s in FILTER_SPECS if s["name"] != "none"]:
        other = results[results["filter_name"] == filter_name].set_index(key)["taxed_cagr"]
        joined = none.to_frame("none").join(other.to_frame("other"))
        if joined["other"].notna().all() and (joined["none"] - joined["other"]).abs().le(tol).all():
            redundant.append(filter_name)
    return redundant


def _any_filter_beats_none(results: pd.DataFrame) -> dict[str, bool]:
    """Per branch: does any non-`none` filter beat the best `none` score on the
    same top base?"""
    verdict: dict[str, bool] = {}
    for branch, branch_rows in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        top_base = branch_rows.iloc[0]["base_name"]
        base_rows = branch_rows[branch_rows["base_name"] == top_base]
        none_best = base_rows[base_rows["filter_name"] == "none"]["score"].max()
        other_best = base_rows[base_rows["filter_name"] != "none"]["score"].max()
        verdict[str(branch)] = bool(other_best > none_best)
    return verdict


def write_report(results: pd.DataFrame, plot_rows: list[dict[str, str]]) -> None:
    top = results.iloc[0]
    practical = results[results["practical_pass"]]
    preferred = results[results["drawdown_tier"] == "preferred"]
    qqq_practical = practical[practical["branch"] == "QQQ"]
    beats = _any_filter_beats_none(results)
    beats_both = all(beats.values())
    beats_text = ", ".join(f"{branch}: {'yes' if won else 'no'}" for branch, won in sorted(beats.items()))
    top_is_none = top["filter_name"] == "none"
    redundant = _redundant_vs_none(results)
    redundant_text = (
        f"Structurally redundant filters (identical to `none` on every base+lag): {', '.join(redundant)}. "
        "ANDing these onto the SMA200 gate cannot extend risk-on; their only distinct behaviour (e.g. a hysteresis band holding through a dip below the SMA) lives on days the SMA gate already blocks, so the AND erases it. Testing those mechanisms properly requires REPLACING the SMA gate, not ANDing onto it - deferred to a future phase."
        if redundant
        else "No filter was structurally redundant with the base signal."
    )

    sections = [
        "# Phase 3A - Sparse Risk-On Confirmation Vote\n\n"
        "Status: research-only confirmation-filter sweep over the Phase 2 geometry. This report does not authorize deployment, paper trading or a mandate change.\n\n"
        "Method references: the base remains the Gayed SMA200 weekly LRS signal plus a realized-vol throttle `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.4-7]`. "
        "Each row ANDs at most ONE structurally distinct confirmation filter onto that base and is compared against a `none` control; filters are not combined (no vote-of-K yet), keeping the panel small to limit overfit risk `[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`. "
        "Filter families: trend quality (Clenow annualized slope x R^2) `[stocks_on_the_move, p.70-77, p.98]`; simple momentum / ROC `[stocks_on_the_move, p.58, p.60]`; SMA hysteresis band (asymmetric entry/exit to filter whipsaws) `[trading_systems_methods, p.383]`; and trend strength via ADX `[trading_systems_methods, p.387]`.\n\n"
        "ADX caveat: the cache stores close-only equity curves (no intraday high/low), so ADX is a DEGRADED close-only proxy (true range ~ |dclose|). Any ADX-driven read is weaker than the other three families and must not be over-interpreted.\n\n"
        "## Executive Conclusion\n\n"
        f"Phase 3A evaluated `{len(results):,}` rows: SPY/QQQ x {len(BASE_SPECS) // 2} branch-specific bases x {len(FILTER_SPECS)} filters (incl. `none`) x lags `0..5`. "
        f"Top score row: `{top['branch']}` base `{top['base_name']}` filter `{top['filter_name']}` L`{float(top['target_leverage']):.2f}` lag `{int(top['lag_days'])}` with after-tax CAGR {fmt_pct(top['taxed_cagr'])}, MDD {fmt_pct(top['taxed_mdd'])}, Calmar {fmt_num(top['taxed_calmar'])}, terminal {fmt_x(top['terminal_vs_underlying'])} vs underlying. "
        f"The overall top row {'uses the `none` control' if top_is_none else 'uses a confirmation filter'}. "
        f"Does any non-`none` filter beat `none` on the same top base (by score)? {beats_text}. "
        f"Practical-pass rows (`MDD >= -50%` and after-tax underlying outperformance): `{len(practical):,}`. Preferred drawdown rows (`MDD >= -40%`): `{len(preferred):,}`. QQQ practical-pass rows: `{len(qqq_practical):,}`.\n\n"
        f"Practical read: {'at least one filter improves on the control on both branches - candidate for a follow-up vote' if beats_both else 'the `none` control is not beaten on every branch, so added filter complexity is not yet justified'} `[trading_systems_methods, p.939]`.\n\n"
        f"{redundant_text}\n\n"
        "## Source And Rules\n\n"
        "| Item | Value |\n|---|---|\n"
        "| Data | `data/testfolio/cache/history.parquet` (close-only equity curves) |\n"
        "| Base signal | `underlying.shift(1) > SMA200.shift(1)` AND realized-vol gate |\n"
        "| Confirmation filter | at most one of {clenow, roc, hysteresis, adx}, ANDed; `none` = control |\n"
        "| Target leverage | adjacent ETF ladder, no negative cash |\n"
        "| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |\n"
        "| Tax | annual 15% DARF on realized net gains plus final liquidation |\n"
        "| ADX | close-only proxy (no intraday high/low available) |\n\n"
    ]
    sections.append("## Test Windows\n\n" + md_table(test_window_rows(results), ["Branch", "Start", "End", "Years", "Underlying CAGR", "Underlying MDD"]))
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    cols = ["Branch", "Base", "Filter", "L", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Spread vs U", "Terminal/U", "Hit 10y", "Pass"]
    sections.append("## Top Ranked Rows\n\n" + md_table(formatted_rows(results, 30), cols))
    sections.append("## Best Row By Branch\n\n" + md_table(best_by_branch_rows(results), ["Branch", "Base", "Filter", "L", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Terminal/U"]))
    sections.append("## Best Row By Filter\n\n" + md_table(best_by_filter_rows(results), ["Branch", "Filter", "Family", "Base", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Score"]))
    sections.append(
        "## Filter vs `none` (top base per branch, best lag)\n\n"
        + md_table(filter_vs_none_rows(results), ["Branch", "Base", "Filter", "Lag", "CAGR", "dCAGR vs none", "MDD", "dMDD vs none", "dScore vs none"])
    )
    sections.append("## Rolling Hit Rates (top row per branch)\n\n" + md_table(hit_rate_rows(results), ["Branch", "Base", "Filter", "Hit 3y", "Hit 5y", "Hit 10y", "Hit 15y", "Hit 20y"]))
    sections.append("## Operational / Tax (top row per branch)\n\n" + md_table(operational_rows(results), ["Branch", "Base", "Filter", "Turnover/yr", "Trades", "Risk-on days", "Tax paid % init"]))
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Did any non-`none` filter beat the control on both branches? | {'Yes' if beats_both else 'No'} ({beats_text}). |\n"
        f"| Is the overall top row a filter or the control? | {'Control (`none`)' if top_is_none else 'A confirmation filter'}. |\n"
        f"| Did any row meet the <=50% MDD practical target and beat underlying? | {'Yes' if not practical.empty else 'No'}. |\n"
        f"| Did any row meet preferred <=40% MDD? | {'Yes' if not preferred.empty else 'No'}. |\n"
        "| Is this deployment-ready? | No. This is a diagnostic confirmation-vote phase only. No deploy, no paper-trade label, no mandate change. |\n\n"
        f"Next step: {'a follow-up phase may test a small vote-of-K combining the filters that beat the control, then run the mandate validation gates' if beats_both else 'do not add filter complexity as an AND-gate; if a trend-hold mechanism is still wanted, test hysteresis as a REPLACEMENT for the SMA gate, otherwise revisit risk-off / bear-sleeve mechanisms or close the family pending the validation gates'} `[advances_fin_ml, p.208-211]`.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    contexts = {name: build_context(branch) for name, branch in BRANCHES.items()}
    rows = []
    for base in BASE_SPECS:
        context = contexts[str(base["branch"])]
        for filter_spec in FILTER_SPECS:
            for lag_days in range(6):
                rows.append(simulate_candidate(context, base, filter_spec, lag_days))
    results = pd.DataFrame(rows).sort_values(
        ["practical_pass", "score", "terminal_vs_underlying", "taxed_calmar"],
        ascending=[False, False, False, False],
    )
    results.to_csv(CSV, index=False)
    plot_rows = make_plots(results, contexts)
    write_report(results, plot_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
