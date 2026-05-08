"""CLI orchestrator for the cohort_robustness sub-study (spec §6).

Runs three analyses in sequence:
  1. Per-cohort entry-date analysis (8 cohorts × top-3 + SPY).
  2. Regime-stratified entry analysis (4 regimes × top-3, forward 5y).
  3. Forward-N-year Sharpe heatmap (3 configs).

Outputs:
  studies/letf_rotation_hunt/reports/COHORT_ROBUSTNESS_REPORT.md
  studies/letf_rotation_hunt/reports/cohort_robustness/cohort_<NN>_<date>.png × 8
  studies/letf_rotation_hunt/reports/cohort_robustness/regime_stratified_violin.png
  studies/letf_rotation_hunt/reports/cohort_robustness/heatmap_<config>.png × 3
  data/cohort_robustness/cohort_metrics.csv
  data/cohort_robustness/regime_stratified.csv
  data/cohort_robustness/forward_heatmap.csv
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.data_loader import load_testfolio_series
from studies.letf_rotation_hunt.tax_comparison.reconstruct import reconstruct_strategy
from studies.letf_rotation_hunt.tax_comparison.select_top10 import select_top10
from studies.letf_rotation_hunt.cohort_robustness.cohort_dates import COHORT_DATES
from studies.letf_rotation_hunt.cohort_robustness.regime_classifier import classify_regimes
from studies.letf_rotation_hunt.cohort_robustness.slice_equity import (
    slice_forward_window, time_to_beat_spy, time_to_recovery,
)
from studies.letf_rotation_hunt.cohort_robustness.plot_cohort import plot_cohort
from studies.letf_rotation_hunt.cohort_robustness.plot_regime import plot_regime_violin
from studies.letf_rotation_hunt.cohort_robustness.plot_heatmap import plot_forward_heatmap

INITIAL_CAPITAL = 10_000.0
TRADING_DAYS_PER_YEAR = 252
SPY_ANCHOR_SHARPE_LH56Y = 0.682

TOP_3_NAMES = [
    "qld_vote_k2_off_zroz",
    "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz",
    "tqqq_voteK2_off_zroz",
]


def _annualised_sharpe(returns: pd.Series) -> float:
    if returns.std() == 0 or len(returns) < 2:
        return float("nan")
    return float(returns.mean() / returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def _cagr(eq: pd.Series) -> float:
    if len(eq) < 2:
        return float("nan")
    n_years = (eq.index[-1] - eq.index[0]).days / 365.25
    if n_years <= 0:
        return float("nan")
    return float((eq.iloc[-1] / eq.iloc[0]) ** (1.0 / n_years) - 1.0)


def _max_drawdown(eq: pd.Series) -> float:
    if len(eq) < 2:
        return float("nan")
    rolling_max = eq.cummax()
    return float((eq / rolling_max - 1.0).min())


def _normalise_to_capital(eq: pd.Series, capital: float = INITIAL_CAPITAL) -> pd.Series:
    if len(eq) == 0:
        return eq
    return capital * (eq / eq.iloc[0])


def _select_top_3(iterations_root: Path) -> list[dict]:
    """Pull the top-3 records from select_top10 — filter by name to ensure
    we always get the same canonical / sma250 / tqqq trio."""
    top10 = select_top10(iterations_root)
    by_name = {r["config_name"]: r for r in top10}
    selected = []
    for name in TOP_3_NAMES:
        rec = by_name.get(name)
        if rec is None:
            raise RuntimeError(
                f"Required config {name!r} not found in top10. Run select_top10 "
                f"on iterations dir {iterations_root}."
            )
        selected.append(rec)
    return selected


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cohort robustness sub-study")
    parser.add_argument(
        "--iterations-root", type=Path,
        default=Path("studies/letf_rotation_hunt/iterations"),
    )
    parser.add_argument(
        "--robustness-parquet", type=Path,
        default=Path("data/robustness/all_windows.parquet"),
    )
    parser.add_argument(
        "--out-report-dir", type=Path,
        default=Path("studies/letf_rotation_hunt/reports/cohort_robustness"),
    )
    parser.add_argument(
        "--out-data-dir", type=Path,
        default=Path("data/cohort_robustness"),
    )
    args = parser.parse_args(argv)

    args.out_report_dir.mkdir(parents=True, exist_ok=True)
    args.out_data_dir.mkdir(parents=True, exist_ok=True)
    report_md_path = args.out_report_dir.parent / "COHORT_ROBUSTNESS_REPORT.md"

    # Reconstruct top-3 once (SLOW step — runs the dispatchers)
    print(f"[cohort_robustness] selecting top-3 from {args.iterations_root}")
    selected = _select_top_3(args.iterations_root)
    rebuilt: dict[str, dict] = {}
    for sel in selected:
        print(f"[cohort_robustness] reconstructing {sel['config_name']}")
        rebuilt[sel["config_name"]] = reconstruct_strategy(sel, datasets=["lh_56y"])

    spy_full = load_testfolio_series("SPYSIM").dropna()
    qqq_underlying = load_testfolio_series("QQQSIM").dropna()

    # ----- Sub-study 1: Cohort plots + table -----
    print(f"[cohort_robustness] running sub-study 1 (cohort plots)")
    cohort_rows = _run_cohort_analysis(
        rebuilt=rebuilt, spy_full=spy_full,
        out_dir=args.out_report_dir,
    )
    cohort_csv = args.out_data_dir / "cohort_metrics.csv"
    pd.DataFrame(cohort_rows).to_csv(cohort_csv, index=False)
    print(f"[cohort_robustness] cohort CSV: {cohort_csv}")

    # ----- Sub-study 2: Regime-stratified -----
    print(f"[cohort_robustness] running sub-study 2 (regime stratified)")
    regime_rows = _run_regime_analysis(
        rebuilt=rebuilt, spy_full=spy_full, qqq_underlying=qqq_underlying,
    )
    regime_csv = args.out_data_dir / "regime_stratified.csv"
    pd.DataFrame(regime_rows).to_csv(regime_csv, index=False)
    print(f"[cohort_robustness] regime CSV: {regime_csv}")
    plot_regime_violin(
        pd.DataFrame(regime_rows),
        out_path=args.out_report_dir / "regime_stratified_violin.png",
    )

    # ----- Sub-study 3: Forward-N-year heatmap -----
    print(f"[cohort_robustness] running sub-study 3 (heatmap)")
    if not args.robustness_parquet.exists():
        print(f"WARNING: {args.robustness_parquet} not found; skipping sub-study 3")
        heatmap_csv_written = False
    else:
        rob_df = pd.read_parquet(args.robustness_parquet)
        rob_top3 = rob_df[rob_df["config"].isin(TOP_3_NAMES)].copy()
        heatmap_csv = args.out_data_dir / "forward_heatmap.csv"
        rob_top3.to_csv(heatmap_csv, index=False)
        print(f"[cohort_robustness] heatmap CSV: {heatmap_csv}")
        heatmap_csv_written = True
        worst_dates = [c["date"] for c in COHORT_DATES if c["tier"] == "worst"]
        for cfg in TOP_3_NAMES:
            plot_forward_heatmap(
                df=rob_top3, config_name=cfg,
                out_path=args.out_report_dir / f"heatmap_{cfg}.png",
                spy_anchor=SPY_ANCHOR_SHARPE_LH56Y,
                annotate_cohort_dates=worst_dates,
            )

    # ----- Combined report -----
    report_md_path.write_text(_render_report(
        cohort_rows=cohort_rows,
        regime_rows=regime_rows,
        heatmap_csv_written=heatmap_csv_written,
    ))
    print(f"[cohort_robustness] report: {report_md_path}")
    return 0


def _run_cohort_analysis(
    rebuilt: dict[str, dict], spy_full: pd.Series, out_dir: Path,
) -> list[dict]:
    """For each of the 8 cohorts, slice forward 10y of equity per config and SPY,
    normalise to $10k, plot, and compute metrics."""
    rows: list[dict] = []
    for cohort in COHORT_DATES:
        eq_per_config_10y: dict[str, pd.Series] = {}
        eq_per_config_5y: dict[str, pd.Series] = {}
        for cfg_name, r in rebuilt.items():
            gross_eq = r["gross_equity"]
            sliced_10y = slice_forward_window(gross_eq, cohort["date"], years=10)
            sliced_5y = slice_forward_window(gross_eq, cohort["date"], years=5)
            if len(sliced_10y) < 2:
                continue
            eq_per_config_10y[cfg_name] = _normalise_to_capital(sliced_10y)
            if len(sliced_5y) >= 2:
                eq_per_config_5y[cfg_name] = _normalise_to_capital(sliced_5y)

        spy_sliced_10y = slice_forward_window(spy_full, cohort["date"], years=10)
        spy_sliced_5y = slice_forward_window(spy_full, cohort["date"], years=5)
        eq_spy_10y = _normalise_to_capital(spy_sliced_10y) if len(spy_sliced_10y) >= 2 else None
        eq_spy_5y = _normalise_to_capital(spy_sliced_5y) if len(spy_sliced_5y) >= 2 else None

        if eq_spy_10y is not None and eq_per_config_10y:
            plot_cohort(
                cohort=cohort,
                eq_per_config=eq_per_config_10y,
                eq_spy=eq_spy_10y,
                out_path=out_dir / f"cohort_{cohort['cohort_id']}_{cohort['date']}.png",
            )

        # Per-config metrics
        for cfg_name, eq_10y in eq_per_config_10y.items():
            eq_5y = eq_per_config_5y.get(cfg_name)
            row = {
                "cohort_id": cohort["cohort_id"],
                "entry_date": cohort["date"],
                "event": cohort["event"],
                "tier": cohort["tier"],
                "config_name": cfg_name,
                "forward_1y_cagr":  _cagr(slice_forward_window(eq_10y, eq_10y.index[0], 1)),
                "forward_3y_cagr":  _cagr(slice_forward_window(eq_10y, eq_10y.index[0], 3)),
                "forward_5y_cagr":  _cagr(eq_5y) if eq_5y is not None else float("nan"),
                "forward_10y_cagr": _cagr(eq_10y),
                "forward_5y_sharpe": _annualised_sharpe(eq_5y.pct_change().dropna()) if eq_5y is not None else float("nan"),
                "forward_5y_mdd":   _max_drawdown(eq_5y) if eq_5y is not None else float("nan"),
                "time_to_recovery_days": time_to_recovery(eq_10y),
                "time_to_beat_spy_days": time_to_beat_spy(eq_10y, eq_spy_10y) if eq_spy_10y is not None else float("nan"),
                "final_5y_ratio_vs_spy": float(eq_5y.iloc[-1] / eq_spy_5y.iloc[-1])
                                          if (eq_5y is not None and eq_spy_5y is not None) else float("nan"),
            }
            rows.append(row)

        # SPY row for reference
        if eq_spy_10y is not None:
            rows.append({
                "cohort_id": cohort["cohort_id"],
                "entry_date": cohort["date"],
                "event": cohort["event"],
                "tier": cohort["tier"],
                "config_name": "SPY",
                "forward_1y_cagr":  _cagr(slice_forward_window(eq_spy_10y, eq_spy_10y.index[0], 1)),
                "forward_3y_cagr":  _cagr(slice_forward_window(eq_spy_10y, eq_spy_10y.index[0], 3)),
                "forward_5y_cagr":  _cagr(eq_spy_5y) if eq_spy_5y is not None else float("nan"),
                "forward_10y_cagr": _cagr(eq_spy_10y),
                "forward_5y_sharpe": _annualised_sharpe(eq_spy_5y.pct_change().dropna()) if eq_spy_5y is not None else float("nan"),
                "forward_5y_mdd":   _max_drawdown(eq_spy_5y) if eq_spy_5y is not None else float("nan"),
                "time_to_recovery_days": time_to_recovery(eq_spy_10y),
                "time_to_beat_spy_days": float("nan"),  # by definition 0 vs itself; left NaN for clarity
                "final_5y_ratio_vs_spy": 1.0,
            })
    return rows


def _run_regime_analysis(
    rebuilt: dict[str, dict], spy_full: pd.Series, qqq_underlying: pd.Series,
) -> list[dict]:
    """For each month-end, classify regime; for each top-3 config, compute
    forward 5y metrics; aggregate per (regime × config)."""
    regimes_df = classify_regimes(qqq_underlying)
    regimes_df = regimes_df.dropna(subset=["k_count"])
    rows: list[dict] = []

    for entry_date in regimes_df.index:
        regime = regimes_df.loc[entry_date, "regime"]
        entry_str = entry_date.strftime("%Y-%m-%d")

        spy_5y = slice_forward_window(spy_full, entry_str, years=5)
        if len(spy_5y) < 252 * 4:  # at least 4 years to qualify
            continue
        spy_5y = _normalise_to_capital(spy_5y)
        spy_final = float(spy_5y.iloc[-1])

        for cfg_name, r in rebuilt.items():
            eq_5y = slice_forward_window(r["gross_equity"], entry_str, years=5)
            if len(eq_5y) < 252 * 4:
                continue
            eq_5y = _normalise_to_capital(eq_5y)
            rets = eq_5y.pct_change().dropna()
            rows.append({
                "entry_date": entry_str,
                "regime": regime,
                "k_count": int(regimes_df.loc[entry_date, "k_count"]),
                "config_name": cfg_name,
                "forward_5y_sharpe": _annualised_sharpe(rets),
                "forward_5y_cagr": _cagr(eq_5y),
                "forward_5y_mdd": _max_drawdown(eq_5y),
                "final_5y_ratio_vs_spy": float(eq_5y.iloc[-1] / spy_final),
                "beats_spy_at_5y": bool(eq_5y.iloc[-1] > spy_final),
            })
    return rows


def _render_report(
    cohort_rows: list[dict],
    regime_rows: list[dict],
    heatmap_csv_written: bool,
) -> str:
    """Render the combined COHORT_ROBUSTNESS_REPORT.md."""
    cohort_df = pd.DataFrame(cohort_rows)
    regime_df = pd.DataFrame(regime_rows)

    out: list[str] = []
    out.append("# LETF Cohort Robustness — Top-3 Swing Strategies")
    out.append("")
    out.append(f"_Generated {datetime.now(timezone.utc).isoformat()}_")
    out.append("")
    out.append("Spec: pre-publication agent spec removed from the public tree.")
    out.append("")

    # Section 1: Cohort
    out.append("## 1. Cohort entry-date analysis (worst + control)")
    out.append("")
    out.append("Per-cohort plots in `cohort_robustness/cohort_<NN>_<date>.png` (8 PNGs).")
    out.append("")
    out.append("**Forward 5y CAGR by cohort × config:**")
    out.append("")
    if not cohort_df.empty:
        pivot = cohort_df.pivot_table(
            index=["cohort_id", "entry_date", "event", "tier"],
            columns="config_name", values="forward_5y_cagr", aggfunc="first",
        )
        out.append(pivot.to_markdown(floatfmt=".1%"))
        out.append("")
        out.append("**Time to beat SPY (days from entry):**")
        out.append("")
        ttb = cohort_df[cohort_df["config_name"] != "SPY"].pivot_table(
            index=["cohort_id", "entry_date"],
            columns="config_name", values="time_to_beat_spy_days", aggfunc="first",
        )
        out.append(ttb.to_markdown(floatfmt=".0f"))
        out.append("")

    # Section 2: Regime
    out.append("## 2. Regime-stratified entry analysis")
    out.append("")
    out.append("![Regime violin](cohort_robustness/regime_stratified_violin.png)")
    out.append("")
    if not regime_df.empty:
        agg = regime_df.groupby(["regime", "config_name"]).agg(
            n=("forward_5y_sharpe", "count"),
            median_sharpe=("forward_5y_sharpe", "median"),
            p10_sharpe=("forward_5y_sharpe", lambda s: s.quantile(0.10)),
            p90_sharpe=("forward_5y_sharpe", lambda s: s.quantile(0.90)),
            pct_beat_spy=("beats_spy_at_5y", "mean"),
        ).reset_index()
        out.append(agg.to_markdown(index=False, floatfmt=".3f"))
        out.append("")

    # Section 3: Heatmap
    out.append("## 3. Forward-N-year Sharpe heatmap")
    out.append("")
    if heatmap_csv_written:
        for cfg in TOP_3_NAMES:
            out.append(f"![{cfg}](cohort_robustness/heatmap_{cfg}.png)")
            out.append("")
    else:
        out.append("_(skipped — robustness parquet missing)_")
        out.append("")

    # Synthesis
    out.append("## 4. Synthesis")
    out.append("")
    out.append("Path-dependence empirical findings — auto-generated. Cross-reference cohort table for individual entry dates and regime table for aggregate behavior across all monthly entries.")
    out.append("")

    # Citations
    out.append("## Citations")
    out.append("")
    out.append("- `[advances_fin_ml, p.31-34, p.222-223]` — multi-window backtest validation.")
    out.append("- `[leverage_for_the_long_run, p.16, p.21]` — LETF path-dependence.")
    out.append("- `[trading_systems_methods, ch.21]` — regime sensitivity testing.")
    out.append("- Parent study protocol: `README.md`, `BASE_MEMORY.md` and `KILL_RULES.md`.")
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
