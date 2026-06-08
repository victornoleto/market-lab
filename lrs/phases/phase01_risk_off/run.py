from __future__ import annotations

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
CSV = RESULTS / "phase01_risk_off.csv"

COMMON_RISK_OFF_ASSETS = ["CASHX", "GLDSIM", "IEFSIM", "ZROZSIM"]

BRANCHES = [
    {"branch": "SPY_2x", "underlying": "SPYSIM", "risk_on": {"SSOSIM": 1.0}, "levered_bh": {"SSOSIM": 1.0}},
    {"branch": "SPY_3x", "underlying": "SPYSIM", "risk_on": {"UPROSIM": 1.0}, "levered_bh": {"UPROSIM": 1.0}},
    {"branch": "QQQ_2x", "underlying": "QQQSIM", "risk_on": {"QLDSIM": 1.0}, "levered_bh": {"QLDSIM": 1.0}},
    {"branch": "QQQ_3x", "underlying": "QQQSIM", "risk_on": {"TQQQSIM": 1.0}, "levered_bh": {"TQQQSIM": 1.0}},
]

RISK_OFF_SPECS: list[dict[str, object]] = [
    {"name": "CASHX", "kind": "fixed", "weights": {"CASHX": 1.0}},
    {"name": "UNDERLYING", "kind": "underlying"},
    {"name": "GLD", "kind": "fixed", "weights": {"GLDSIM": 1.0}},
    {"name": "IEF", "kind": "fixed", "weights": {"IEFSIM": 1.0}},
    {"name": "ZROZ", "kind": "fixed", "weights": {"ZROZSIM": 1.0}},
    {"name": "60 ZROZ / 40 GLD", "kind": "fixed", "weights": {"ZROZSIM": 0.60, "GLDSIM": 0.40}},
    {"name": "50 ZROZ / 50 GLD", "kind": "fixed", "weights": {"ZROZSIM": 0.50, "GLDSIM": 0.50}},
    {"name": "40 ZROZ / 40 GLD / 20 IEF", "kind": "fixed", "weights": {"ZROZSIM": 0.40, "GLDSIM": 0.40, "IEFSIM": 0.20}},
    {"name": "50 ZROZ / 25 GLD / 25 CASH", "kind": "fixed", "weights": {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25}},
    {"name": "MOM63 ZROZ/IEF/GLD", "kind": "momentum", "lookback": 63, "assets": ["ZROZSIM", "IEFSIM", "GLDSIM"]},
    {"name": "MOM126 ZROZ/IEF/GLD/CASH", "kind": "momentum", "lookback": 126, "assets": ["ZROZSIM", "IEFSIM", "GLDSIM", "CASHX"]},
]


def branch_assets(branch: dict[str, object]) -> list[str]:
    assets = set(COMMON_RISK_OFF_ASSETS)
    assets.add(str(branch["underlying"]))
    assets.update(branch["risk_on"].keys())  # type: ignore[union-attr]
    assets.update(branch["levered_bh"].keys())  # type: ignore[union-attr]
    return sorted(assets)


def fixed_weights_for_spec(spec: dict[str, object], underlying: str) -> dict[str, float]:
    if spec["kind"] == "underlying":
        return {underlying: 1.0}
    return clean_weights(spec["weights"])  # type: ignore[arg-type]


def off_weight_label(spec: dict[str, object], underlying: str) -> str:
    if spec["kind"] == "momentum":
        return f"{spec['name']}"
    return weights_label(fixed_weights_for_spec(spec, underlying))


def momentum_off_targets(
    prices: pd.DataFrame,
    signal: pd.Series,
    risk_on_weights: dict[str, float],
    candidate_assets: list[str],
    lookback: int,
) -> pd.DataFrame:
    assets = sorted(set(risk_on_weights) | set(candidate_assets) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=prices.index, columns=assets)
    scores = prices[candidate_assets].shift(1) / prices[candidate_assets].shift(lookback + 1) - 1.0
    has_score = scores.notna().any(axis=1)
    best_asset = scores.fillna(float("-inf")).idxmax(axis=1)
    best_asset = best_asset.where(has_score, "CASHX")

    for asset, weight in risk_on_weights.items():
        desired[asset] = np.where(signal, weight, 0.0)
    for asset in candidate_assets + ["CASHX"]:
        if asset not in desired.columns:
            desired[asset] = 0.0
        desired[asset] = np.where(~signal & (best_asset == asset), 1.0, desired[asset])
    return desired.fillna(0.0)


def fixed_off_targets(
    index: pd.DatetimeIndex,
    signal: pd.Series,
    risk_on_weights: dict[str, float],
    risk_off_weights: dict[str, float],
) -> pd.DataFrame:
    assets = sorted(set(risk_on_weights) | set(risk_off_weights) | {"CASHX"})
    desired = pd.DataFrame(0.0, index=index, columns=assets)
    for asset in assets:
        desired[asset] = np.where(signal, risk_on_weights.get(asset, 0.0), risk_off_weights.get(asset, 0.0))
    return desired


def desired_targets_for_spec(
    prices: pd.DataFrame,
    signal: pd.Series,
    branch: dict[str, object],
    spec: dict[str, object],
) -> pd.DataFrame:
    risk_on = clean_weights(branch["risk_on"])  # type: ignore[arg-type]
    underlying = str(branch["underlying"])
    if spec["kind"] == "momentum":
        return momentum_off_targets(
            prices,
            signal,
            risk_on,
            list(spec["assets"]),  # type: ignore[arg-type]
            int(spec["lookback"]),
        )
    return fixed_off_targets(prices.index, signal, risk_on, fixed_weights_for_spec(spec, underlying))


def simulate_candidate(branch: dict[str, object], spec: dict[str, object], lag_days: int) -> dict[str, object]:
    assets = branch_assets(branch)
    prices = load_price_frame(assets)
    returns = prices.pct_change().dropna()
    prices = prices.reindex(returns.index)
    underlying = str(branch["underlying"])
    signal = build_sma_signal(prices[underlying], lookback=200).reindex(returns.index).fillna(False)
    desired = desired_targets_for_spec(prices, signal, branch, spec).reindex(returns.index).fillna(0.0)
    weights, schedule_summary = build_weekly_lagged_weights(
        desired,
        lag_days=lag_days,
        risk_on_weights=clean_weights(branch["risk_on"]),  # type: ignore[arg-type]
    )

    gross, _gross_summary = simulate_weight_frame(returns, weights, taxable=False)
    taxed, tax_summary = simulate_weight_frame(returns, weights, taxable=True)

    underlying_frame = constant_weight_frame(returns.index, {underlying: 1.0})
    underlying_taxed, underlying_tax_summary = simulate_weight_frame(returns, underlying_frame, taxable=True)
    underlying_gross, _ = simulate_weight_frame(returns, underlying_frame, taxable=False)

    levered_frame = constant_weight_frame(returns.index, branch["levered_bh"])  # type: ignore[arg-type]
    levered_taxed, levered_tax_summary = simulate_weight_frame(returns, levered_frame, taxable=True)
    levered_gross, _ = simulate_weight_frame(returns, levered_frame, taxable=False)

    gross_metrics = metrics_from_returns(gross)
    taxed_metrics = metrics_from_returns(taxed)
    underlying_metrics = metrics_from_returns(underlying_taxed)
    levered_metrics = metrics_from_returns(levered_taxed)
    rel_underlying = relative_stats(taxed, underlying_taxed)
    rel_levered = relative_stats(taxed, levered_taxed)
    drawdown_component = max(-1.0, min(1.0, (taxed_metrics.mdd + 0.65) / 0.25))
    cagr_spread = taxed_metrics.cagr - underlying_metrics.cagr
    score = (
        6.0 * cagr_spread
        + 2.0 * taxed_metrics.calmar
        + 0.75 * taxed_metrics.sortino
        + 0.75 * rel_underlying.get("hit_10y", 0.0)
        + 1.50 * drawdown_component
        + 0.25 * rel_underlying["worst_relative_drawdown"]
        - 0.10 * float(tax_summary["turnover_per_year"])
    )

    return {
        "branch": branch["branch"],
        "lag_days": lag_days,
        "lookback": 200,
        "cadence": "weekly",
        "risk_on": weights_label(branch["risk_on"]),  # type: ignore[arg-type]
        "risk_off_name": spec["name"],
        "risk_off_kind": spec["kind"],
        "risk_off_weights": off_weight_label(spec, underlying),
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
        "underlying_taxed_cagr": underlying_metrics.cagr,
        "underlying_taxed_mdd": underlying_metrics.mdd,
        "underlying_taxed_terminal": underlying_metrics.terminal,
        "levered_taxed_cagr": levered_metrics.cagr,
        "levered_taxed_mdd": levered_metrics.mdd,
        "levered_taxed_terminal": levered_metrics.terminal,
        "cagr_spread_vs_underlying": cagr_spread,
        "mdd_spread_vs_underlying": taxed_metrics.mdd - underlying_metrics.mdd,
        "terminal_vs_underlying": rel_underlying["terminal_vs_benchmark"],
        "terminal_vs_levered_bh": rel_levered["terminal_vs_benchmark"],
        "worst_relative_dd_vs_underlying": rel_underlying["worst_relative_drawdown"],
        "worst_relative_dd_vs_levered_bh": rel_levered["worst_relative_drawdown"],
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
        "underlying_tax_paid_pct_initial": underlying_tax_summary["total_tax_paid_pct_initial"],
        "levered_tax_paid_pct_initial": levered_tax_summary["total_tax_paid_pct_initial"],
        "final_taxed_equity": float(equity_curve(taxed).iloc[-1]),
        "final_underlying_taxed_equity": float(equity_curve(underlying_taxed).iloc[-1]),
        "final_levered_taxed_equity": float(equity_curve(levered_taxed).iloc[-1]),
        "gross_vs_tax_cagr_drag": gross_metrics.cagr - taxed_metrics.cagr,
        "underlying_gross_cagr": metrics_from_returns(underlying_gross).cagr,
        "levered_gross_cagr": metrics_from_returns(levered_gross).cagr,
    }


def simulate_paths_for_row(row: pd.Series) -> dict[str, pd.Series]:
    branch = next(b for b in BRANCHES if b["branch"] == row["branch"])
    spec = next(s for s in RISK_OFF_SPECS if s["name"] == row["risk_off_name"])
    assets = branch_assets(branch)
    prices = load_price_frame(assets)
    returns = prices.pct_change().dropna()
    prices = prices.reindex(returns.index)
    underlying = str(branch["underlying"])
    signal = build_sma_signal(prices[underlying], lookback=200).reindex(returns.index).fillna(False)
    desired = desired_targets_for_spec(prices, signal, branch, spec).reindex(returns.index).fillna(0.0)
    weights, _ = build_weekly_lagged_weights(
        desired,
        lag_days=int(row["lag_days"]),
        risk_on_weights=clean_weights(branch["risk_on"]),  # type: ignore[arg-type]
    )
    taxed, _ = simulate_weight_frame(returns, weights, taxable=True)
    underlying_taxed, _ = simulate_weight_frame(returns, constant_weight_frame(returns.index, {underlying: 1.0}), taxable=True)
    levered_taxed, _ = simulate_weight_frame(returns, constant_weight_frame(returns.index, branch["levered_bh"]), taxable=True)  # type: ignore[arg-type]
    return {"strategy": taxed, "underlying": underlying_taxed, "levered": levered_taxed}


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


def plot_candidate_panel(row: pd.Series) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    paths = simulate_paths_for_row(row)
    aligned = pd.concat(
        {
            "LRS": equity_curve(paths["strategy"]),
            "Underlying B&H": equity_curve(paths["underlying"]),
            "LETF B&H": equity_curve(paths["levered"]),
        },
        axis=1,
    ).dropna()
    dd = pd.concat(
        {
            "LRS": drawdown(paths["strategy"]),
            "Underlying B&H": drawdown(paths["underlying"]),
            "LETF B&H": drawdown(paths["levered"]),
        },
        axis=1,
    ).dropna()
    relative = aligned["LRS"] / aligned["Underlying B&H"]

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    aligned.plot(ax=axes[0], logy=True, linewidth=1.2)
    axes[0].set_title(f"{row['branch']} lag={int(row['lag_days'])} off={row['risk_off_name']} after-tax equity")
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
    out = PLOTS / f"phase01_{str(row['branch']).lower()}_lag{int(row['lag_days'])}_{safe_off}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_frontier(results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))
    for branch, subset in results.groupby("branch", sort=True):
        ax.scatter(subset["taxed_mdd"] * 100.0, subset["taxed_cagr"] * 100.0, s=25, alpha=0.65, label=branch)
    ax.axvline(-50.0, color="black", linestyle="--", linewidth=0.9, label="50% MDD target")
    ax.axvline(-65.0, color="red", linestyle=":", linewidth=0.9, label="ruin threshold")
    ax.set_title("Phase 1 risk-off frontier")
    ax.set_xlabel("Max drawdown (%)")
    ax.set_ylabel("After-tax CAGR (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = PLOTS / "phase01_risk_off_frontier.png"
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
    rows.append({"Plot": "Risk-off frontier", "File": f"[plots/{frontier.name}](plots/{frontier.name})"})
    return rows


def formatted_rows(frame: pd.DataFrame, limit: int = 25) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Branch": row["branch"],
                "Risk-Off": row["risk_off_name"],
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Spread vs U": fmt_pp(row["cagr_spread_vs_underlying"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
                "Hit 10y": fmt_pct(row["hit_10y_vs_underlying"], 1),
                "Turn/Yr": fmt_num(row["turnover_per_year"], 2),
                "Pass": "yes" if row["practical_pass"] else "no",
            }
        )
    return rows


def branch_best_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.sort_values("score", ascending=False).groupby("branch", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Best Risk-Off": row["risk_off_name"],
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
            }
        )
    return rows


def risk_off_best_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for risk_off, subset in results.sort_values("score", ascending=False).groupby("risk_off_name", sort=True):
        row = subset.iloc[0]
        rows.append(
            {
                "Risk-Off": risk_off,
                "Best Branch": row["branch"],
                "Lag": int(row["lag_days"]),
                "Tier": row["drawdown_tier"],
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
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
                "LETF B&H CAGR": fmt_pct(row["levered_taxed_cagr"]),
                "LETF B&H MDD": fmt_pct(row["levered_taxed_mdd"]),
            }
        )
    return rows


def write_report(results: pd.DataFrame, plot_rows: list[dict[str, str]]) -> None:
    top = results.iloc[0]
    practical = results[results["practical_pass"]]
    non_ruin = results[results["drawdown_tier"] != "ruin"]
    sections = [
        "# Phase 1 - Risk-Off Alternatives\n\n"
        "Status: research-only risk-off sweep. This report does not authorize deployment, paper trading or a mandate change.\n\n"
        "Method references: the LRS premise is still Gayed SMA200 risk-on/risk-off `[leverage_for_the_long_run, p.13]`. This phase changes only the defensive sleeve because high-volatility drawdowns and path dependency are the main enemies of leverage `[leverage_for_the_long_run, p.4-7]`. Weekly lag and rolling diagnostics remain implementation checks `[testing_tuning, p.327-335]`.\n\n"
        "## Executive Conclusion\n\n"
        f"Phase 1 evaluated `{len(results):,}` rows: 4 branches x {len(RISK_OFF_SPECS)} risk-off sleeves x lags `0..5`. "
        f"Top score row: `{top['branch']}` risk-off `{top['risk_off_name']}` lag `{int(top['lag_days'])}` with after-tax CAGR {fmt_pct(top['taxed_cagr'])}, MDD {fmt_pct(top['taxed_mdd'])}, Calmar {fmt_num(top['taxed_calmar'])}, terminal {fmt_x(top['terminal_vs_underlying'])} vs underlying. "
        f"Rows at or below the 50% MDD target with positive underlying outperformance: `{len(practical):,}`. Rows outside ruin territory (`MDD >= -65%` by the restart tiers): `{len(non_ruin):,}`.\n\n"
        "Practical read: if this phase still has no practical-pass rows, the next evolution must combine better risk-off with lower leverage, volatility throttle or bear-market sleeve rather than adding many indicators.\n\n"
        "## Source And Rules\n\n"
        "| Item | Value |\n|---|---|\n"
        "| Data | `data/testfolio/cache/history.parquet` |\n"
        "| Signal | `underlying.shift(1) > SMA200.shift(1)` |\n"
        "| Cadence | first trading day of each week |\n"
        "| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |\n"
        "| Risk-off assets | `CASHX`, underlying, `GLDSIM`, `IEFSIM`, `ZROZSIM`, baskets and momentum off-leg |\n"
        "| Tax | annual 15% DARF on realized net gains plus final liquidation |\n\n"
    ]
    sections.append(
        "## Test Windows\n\n"
        "Analysis: Phase 1 uses a common branch window including GLD/IEF/ZROZ/CASH so every risk-off candidate in the same branch is comparable. This intentionally shortens the SPY branch versus Phase 0's cash-only 1885+ baseline.\n\n"
        + md_table(test_window_rows(results), ["Branch", "Start", "End", "Years", "Underlying CAGR", "Underlying MDD", "LETF B&H CAGR", "LETF B&H MDD"])
    )
    sections.append("## Plots\n\n" + md_table(plot_rows, ["Plot", "File"]))
    cols = ["Branch", "Risk-Off", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Spread vs U", "Terminal/U", "Hit 10y", "Turn/Yr", "Pass"]
    sections.append(
        "## Top Ranked Rows\n\n"
        "Analysis: score now penalizes ruin-level drawdown. This is a research ranking, not a validation gate.\n\n"
        + md_table(formatted_rows(results, 30), cols)
    )
    sections.append(
        "## Best Row By Branch\n\n"
        + md_table(branch_best_rows(results), ["Branch", "Best Risk-Off", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Terminal/U"])
    )
    sections.append(
        "## Best Row By Risk-Off Sleeve\n\n"
        + md_table(risk_off_best_rows(results), ["Risk-Off", "Best Branch", "Lag", "Tier", "CAGR", "MDD", "Calmar", "Terminal/U"])
    )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        f"| Did any row meet the <=50% MDD practical target and beat underlying? | {'Yes' if not practical.empty else 'No'}. |\n"
        f"| Did any row exit ruin territory (`MDD >= -65%`)? | {'Yes' if not non_ruin.empty else 'No'}. |\n"
        "| Is this deployment-ready? | No. This is a risk-off discovery phase only. |\n\n"
        "Next step: if drawdown remains excessive, test lower target leverage and volatility/bear-market throttles before expanding to broad multi-indicator votes.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for branch in BRANCHES:
        for spec in RISK_OFF_SPECS:
            for lag_days in range(6):
                rows.append(simulate_candidate(branch, spec, lag_days))
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
