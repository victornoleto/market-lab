from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lrs.lib.backtest import (  # noqa: E402
    fmt_num,
    fmt_pct,
    fmt_pp,
    fmt_x,
    build_sma_signal,
    build_weekly_lrs_weights,
    constant_weight_frame,
    equity_curve,
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
CSV = RESULTS / "phase00_gayed_baseline.csv"

BRANCHES = [
    {
        "branch": "SPY_2x",
        "underlying": "SPYSIM",
        "risk_on": {"SSOSIM": 1.0},
        "risk_off": {"CASHX": 1.0},
        "levered_bh": {"SSOSIM": 1.0},
    },
    {
        "branch": "SPY_3x",
        "underlying": "SPYSIM",
        "risk_on": {"UPROSIM": 1.0},
        "risk_off": {"CASHX": 1.0},
        "levered_bh": {"UPROSIM": 1.0},
    },
    {
        "branch": "QQQ_2x",
        "underlying": "QQQSIM",
        "risk_on": {"QLDSIM": 1.0},
        "risk_off": {"CASHX": 1.0},
        "levered_bh": {"QLDSIM": 1.0},
    },
    {
        "branch": "QQQ_3x",
        "underlying": "QQQSIM",
        "risk_on": {"TQQQSIM": 1.0},
        "risk_off": {"CASHX": 1.0},
        "levered_bh": {"TQQQSIM": 1.0},
    },
]


def branch_assets(branch: dict[str, object]) -> list[str]:
    assets = {str(branch["underlying"]), "CASHX"}
    for key in ["risk_on", "risk_off", "levered_bh"]:
        assets.update((branch[key]).keys())  # type: ignore[union-attr]
    return sorted(assets)


def evaluate_branch(branch: dict[str, object], lag_days: int) -> dict[str, object]:
    paths = simulate_branch_paths(branch, lag_days)
    gross = paths["gross"]
    taxed = paths["taxed"]
    underlying_taxed = paths["underlying_taxed"]
    underlying_gross = paths["underlying_gross"]
    levered_taxed = paths["levered_taxed"]
    levered_gross = paths["levered_gross"]
    tax_summary = paths["tax_summary"]
    underlying_tax_summary = paths["underlying_tax_summary"]
    levered_tax_summary = paths["levered_tax_summary"]
    schedule_summary = paths["schedule_summary"]

    gross_metrics = metrics_from_returns(gross)
    taxed_metrics = metrics_from_returns(taxed)
    underlying_metrics = metrics_from_returns(underlying_taxed)
    levered_metrics = metrics_from_returns(levered_taxed)
    rel_underlying = relative_stats(taxed, underlying_taxed)
    rel_levered = relative_stats(taxed, levered_taxed)

    tax_turnover = float(tax_summary["turnover_per_year"])
    score = (
        5.0 * (taxed_metrics.cagr - underlying_metrics.cagr)
        + 1.5 * taxed_metrics.calmar
        + 0.75 * taxed_metrics.sortino
        + 0.5 * rel_underlying.get("hit_10y", 0.0)
        + 0.3 * rel_underlying.get("hit_5y", 0.0)
        + 0.5 * rel_underlying["worst_relative_drawdown"]
        - 0.10 * tax_turnover
    )

    return {
        "branch": branch["branch"],
        "lag_days": lag_days,
        "lookback": 200,
        "cadence": "weekly",
        "risk_on": weights_label(branch["risk_on"]),  # type: ignore[arg-type]
        "risk_off": weights_label(branch["risk_off"]),  # type: ignore[arg-type]
        "start": taxed_metrics.start,
        "end": taxed_metrics.end,
        "years": taxed_metrics.years,
        "score": score,
        "gross_cagr": gross_metrics.cagr,
        "gross_mdd": gross_metrics.mdd,
        "gross_terminal": gross_metrics.terminal,
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
        "cagr_spread_vs_underlying": taxed_metrics.cagr - underlying_metrics.cagr,
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
        "turnover_per_year": tax_turnover,
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


def simulate_branch_paths(branch: dict[str, object], lag_days: int) -> dict[str, object]:
    assets = branch_assets(branch)
    prices = load_price_frame(assets)
    returns = prices.pct_change().dropna()
    prices = prices.reindex(returns.index)

    underlying = str(branch["underlying"])
    signal = build_sma_signal(prices[underlying], lookback=200).reindex(returns.index).fillna(False)
    weights, schedule_summary = build_weekly_lrs_weights(
        returns.index,
        signal,
        branch["risk_on"],  # type: ignore[arg-type]
        branch["risk_off"],  # type: ignore[arg-type]
        lag_days=lag_days,
    )
    gross, _gross_summary = simulate_weight_frame(returns, weights, taxable=False)
    taxed, tax_summary = simulate_weight_frame(returns, weights, taxable=True)

    underlying_weights = {underlying: 1.0}
    underlying_frame = constant_weight_frame(returns.index, underlying_weights)
    underlying_taxed, underlying_tax_summary = simulate_weight_frame(returns, underlying_frame, taxable=True)
    underlying_gross, _ = simulate_weight_frame(returns, underlying_frame, taxable=False)

    levered_frame = constant_weight_frame(returns.index, branch["levered_bh"])  # type: ignore[arg-type]
    levered_taxed, levered_tax_summary = simulate_weight_frame(returns, levered_frame, taxable=True)
    levered_gross, _ = simulate_weight_frame(returns, levered_frame, taxable=False)

    return {
        "gross": gross,
        "taxed": taxed,
        "underlying_taxed": underlying_taxed,
        "underlying_gross": underlying_gross,
        "levered_taxed": levered_taxed,
        "levered_gross": levered_gross,
        "tax_summary": tax_summary,
        "underlying_tax_summary": underlying_tax_summary,
        "levered_tax_summary": levered_tax_summary,
        "schedule_summary": schedule_summary,
    }


def formatted_rows(frame: pd.DataFrame, limit: int = 24) -> list[dict[str, object]]:
    rows = []
    for _, row in frame.head(limit).iterrows():
        rows.append(
            {
                "Branch": row["branch"],
                "Lag": int(row["lag_days"]),
                "CAGR": fmt_pct(row["taxed_cagr"]),
                "MDD": fmt_pct(row["taxed_mdd"]),
                "Calmar": fmt_num(row["taxed_calmar"]),
                "Sortino": fmt_num(row["taxed_sortino"]),
                "Spread vs U": fmt_pp(row["cagr_spread_vs_underlying"]),
                "Terminal/U": fmt_x(row["terminal_vs_underlying"]),
                "Terminal/LETF": fmt_x(row["terminal_vs_levered_bh"]),
                "Hit 10y": fmt_pct(row["hit_10y_vs_underlying"], 1),
                "Rel DD U": fmt_pct(row["worst_relative_dd_vs_underlying"]),
                "Risk-On": fmt_pct(row["pct_risk_on_days"], 1),
                "Turn/Yr": fmt_num(row["turnover_per_year"], 2),
                "Tax Paid": fmt_pct(row["tax_paid_pct_initial"], 1),
            }
        )
    return rows


def lag_sensitivity_rows(frame: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in frame.groupby("branch", sort=True):
        best = subset.sort_values("score", ascending=False).iloc[0]
        lag0 = subset[subset["lag_days"] == 0].iloc[0]
        lag5 = subset[subset["lag_days"] == 5].iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Best Lag": int(best["lag_days"]),
                "Best CAGR": fmt_pct(best["taxed_cagr"]),
                "Lag0 CAGR": fmt_pct(lag0["taxed_cagr"]),
                "Lag5 CAGR": fmt_pct(lag5["taxed_cagr"]),
                "Lag5-Lag0": fmt_pp(lag5["taxed_cagr"] - lag0["taxed_cagr"]),
                "Best MDD": fmt_pct(best["taxed_mdd"]),
                "Best Terminal/U": fmt_x(best["terminal_vs_underlying"]),
            }
        )
    return rows


def drawdown(returns: pd.Series) -> pd.Series:
    equity = equity_curve(returns)
    return equity / equity.cummax() - 1.0


def branch_by_name(name: str) -> dict[str, object]:
    for branch in BRANCHES:
        if branch["branch"] == name:
            return branch
    raise KeyError(name)


def plot_branch_panel(row: pd.Series) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    branch = branch_by_name(str(row["branch"]))
    lag_days = int(row["lag_days"])
    paths = simulate_branch_paths(branch, lag_days)
    strategy = paths["taxed"]
    underlying = paths["underlying_taxed"]
    levered = paths["levered_taxed"]

    aligned = pd.concat(
        {
            "LRS": equity_curve(strategy),
            "Underlying B&H": equity_curve(underlying),
            "LETF B&H": equity_curve(levered),
        },
        axis=1,
    ).dropna()
    relative = aligned["LRS"] / aligned["Underlying B&H"]
    dd = pd.concat(
        {
            "LRS": drawdown(strategy),
            "Underlying B&H": drawdown(underlying),
            "LETF B&H": drawdown(levered),
        },
        axis=1,
    ).dropna()

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    aligned.plot(ax=axes[0], logy=True, linewidth=1.2)
    axes[0].set_title(f"{row['branch']} lag={lag_days} after-tax equity")
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
    out = PLOTS / f"phase00_{str(row['branch']).lower()}_lag{lag_days}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_lag_sensitivity(results: pd.DataFrame) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for branch, subset in results.sort_values(["branch", "lag_days"]).groupby("branch"):
        axes[0].plot(subset["lag_days"], subset["taxed_cagr"] * 100.0, marker="o", label=branch)
        axes[1].plot(subset["lag_days"], subset["taxed_mdd"] * 100.0, marker="o", label=branch)
    axes[0].set_title("Settlement lag sensitivity - after-tax CAGR")
    axes[0].set_ylabel("CAGR (%)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[1].set_title("Settlement lag sensitivity - max drawdown")
    axes[1].set_xlabel("Lag n (daily bars in CASHX before entry)")
    axes[1].set_ylabel("MDD (%)")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    out = PLOTS / "phase00_lag_sensitivity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def make_plots(results: pd.DataFrame) -> list[dict[str, str]]:
    PLOTS.mkdir(parents=True, exist_ok=True)
    plot_rows: list[dict[str, str]] = []
    for _, row in results.sort_values("score", ascending=False).groupby("branch", sort=True).head(1).iterrows():
        path = plot_branch_panel(row)
        plot_rows.append(
            {
                "Plot": f"{row['branch']} best lag {int(row['lag_days'])}",
                "File": f"[plots/{path.name}](plots/{path.name})",
            }
        )
    lag_path = plot_lag_sensitivity(results)
    plot_rows.append({"Plot": "Lag sensitivity", "File": f"[plots/{lag_path.name}](plots/{lag_path.name})"})
    return plot_rows


def start_window_rows(results: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    for branch, subset in results.groupby("branch", sort=True):
        first = subset.iloc[0]
        rows.append(
            {
                "Branch": branch,
                "Start": first["start"],
                "End": first["end"],
                "Years": fmt_num(first["years"], 1),
                "Underlying CAGR": fmt_pct(first["underlying_taxed_cagr"]),
                "Underlying MDD": fmt_pct(first["underlying_taxed_mdd"]),
                "LETF B&H CAGR": fmt_pct(first["levered_taxed_cagr"]),
                "LETF B&H MDD": fmt_pct(first["levered_taxed_mdd"]),
            }
        )
    return rows


def write_report(results: pd.DataFrame, plot_rows: list[dict[str, str]]) -> None:
    top = results.iloc[0]
    pass_vs_underlying = results[results["terminal_vs_underlying"] > 1.0]
    branches = ", ".join(sorted(results["branch"].unique()))
    sections = [
        "# Phase 0 - Original Gayed Weekly Baseline\n\n"
        "Status: research-only baseline. This report does not authorize deployment, paper trading or a mandate change.\n\n"
        "Method references: original LRS rule from Gayed uses leveraged equity when the underlying closes above its moving average and defensive exposure otherwise `[leverage_for_the_long_run, p.13]`. SMA200 is used as the starting point because Gayed recommends it for low turnover practicality `[leverage_for_the_long_run, p.16]`. Weekly execution, lag sensitivity and rolling-window diagnostics are implementation robustness checks `[testing_tuning, p.327-335]`.\n\n"
        "## Executive Conclusion\n\n"
        f"Phase 0 evaluated `{len(results):,}` baseline rows across `{branches}` and settlement lags `0..5`. "
        f"The top score row is `{top['branch']}` with lag `{int(top['lag_days'])}`: after-tax CAGR {fmt_pct(top['taxed_cagr'])}, MDD {fmt_pct(top['taxed_mdd'])}, Calmar {fmt_num(top['taxed_calmar'])}, terminal {fmt_x(top['terminal_vs_underlying'])} vs its underlying and {fmt_x(top['terminal_vs_levered_bh'])} vs leveraged buy-and-hold. "
        f"Rows beating underlying terminal wealth after tax: `{len(pass_vs_underlying):,}` of `{len(results):,}`.\n\n"
        "Practical read: this is the original baseline only. It establishes the comparison surface for future risk-off, sparse indicator and bear-market sleeves; it is not a validation claim.\n\n"
        "## Source And Rules\n\n"
        "| Item | Value |\n|---|---|\n"
        "| Data | `data/testfolio/cache/history.parquet` |\n"
        "| Signal | `underlying.shift(1) > SMA200.shift(1)` |\n"
        "| Cadence | first trading day of each week |\n"
        "| Risk-off | `CASHX` |\n"
        "| Settlement lag | `n = 0..5` daily bars in `CASHX` before entering the new sleeve |\n"
        "| Tax | annual 15% DARF on realized net gains plus final liquidation |\n"
        "| XLK status | deferred until leveraged XLK/TECL synthetic series is present |\n\n"
    ]
    sections.append(
        "## Test Windows\n\n"
        "Analysis: SPY and QQQ use different history lengths because the Testfol.io cache has long SPY synthetic history but QQQ starts in 1986. Cross-branch comparisons should account for this window difference.\n\n"
        + md_table(
            start_window_rows(results),
            ["Branch", "Start", "End", "Years", "Underlying CAGR", "Underlying MDD", "LETF B&H CAGR", "LETF B&H MDD"],
        )
    )
    sections.append(
        "## Plots\n\n"
        "Each phase should emit plots as the study evolves. Phase 0 saves best-branch panels and lag sensitivity under `plots/`.\n\n"
        + md_table(plot_rows, ["Plot", "File"])
    )
    columns = [
        "Branch", "Lag", "CAGR", "MDD", "Calmar", "Sortino", "Spread vs U",
        "Terminal/U", "Terminal/LETF", "Hit 10y", "Rel DD U", "Risk-On", "Turn/Yr",
        "Tax Paid",
    ]
    sections.append(
        "## Ranked Baselines\n\n"
        "Analysis: ranking uses after-tax CAGR vs underlying, Calmar, Sortino, rolling hit-rate and relative drawdown. Leveraged buy-and-hold is not the target to beat on CAGR; it is the risk-of-ruin comparator.\n\n"
        + md_table(formatted_rows(results, 24), columns)
    )
    sections.append(
        "## Lag Sensitivity\n\n"
        "Analysis: `n` models settlement or operational delay. With `risk-off=CASHX`, the main drag appears on re-entry from cash into the leveraged sleeve.\n\n"
        + md_table(
            lag_sensitivity_rows(results),
            ["Branch", "Best Lag", "Best CAGR", "Lag0 CAGR", "Lag5 CAGR", "Lag5-Lag0", "Best MDD", "Best Terminal/U"],
        )
    )
    sections.append(
        "## Phase Verdict\n\n"
        "| Question | Verdict |\n|---|---|\n"
        "| Did we implement the original Gayed baseline? | Yes: SMA200, leveraged risk-on, `CASHX` risk-off. |\n"
        "| Is weekly execution implemented? | Yes, first trading day of week, signal lagged one bar. |\n"
        "| Is settlement lag implemented? | Yes, `n=0..5`. |\n"
        "| Is Brazil annual tax modeled? | Yes, via `AnnualDarfEngine`. |\n"
        "| Is this a deployable strategy? | No. This is only the restart baseline. |\n\n"
        "Next step: Phase 1 should replace `CASHX` with defensive sleeves and momentum off-leg candidates before adding risk-on indicators.\n"
    )
    REPORT.write_text("\n".join(sections), encoding="utf-8")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for branch in BRANCHES:
        for lag_days in range(6):
            rows.append(evaluate_branch(branch, lag_days))
    results = pd.DataFrame(rows).sort_values(
        ["score", "terminal_vs_underlying", "taxed_calmar"], ascending=[False, False, False]
    )
    results.to_csv(CSV, index=False)
    plot_rows = make_plots(results)
    write_report(results, plot_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
