"""CLI orchestrator for the threshold_sweep sub-study (spec §6).

For each of the 12 variants:
  1. Run dispatcher → gross equity / strategy returns / positions / asset returns.
  2. Apply tax_comparison.per_swing.simulate_per_swing → net equity Modelo 1.
  3. Apply tax_layer.apply_annual_darf(annual_realize) → net equity Modelo 2.
  4. Compute Sharpe / CAGR / MDD / trade count for all three.

Outputs:
  studies/letf_rotation_hunt/reports/THRESHOLD_SWEEP_REPORT.md
  studies/letf_rotation_hunt/reports/threshold_sweep/{sharpe_bar_gross, sharpe_bar_net_m1,
                                                       sharpe_bar_net_m2, trade_count_bar,
                                                       equity_overlay_top4}.png
  data/threshold_sweep/variant_metrics.csv
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_ffr_daily, load_testfolio_series
from studies.letf_rotation_hunt.runners.run_iter_t3 import _run_single_composite_config
from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing
from studies.letf_rotation_hunt.core.tax_layer import apply_annual_darf
from studies.letf_rotation_hunt.analyses.threshold_sweep.plot_threshold_sweep import (
    plot_equity_overlay_top4, plot_sharpe_bar, plot_trade_count_bar,
)
from studies.letf_rotation_hunt.analyses.threshold_sweep.variant_grid import VARIANTS

INITIAL_CAPITAL = 10_000.0
TAX_RATE = 0.15
TRADING_DAYS_PER_YEAR = 252

# Anti-curve-fit thresholds per spec §3.1 / §3.2
SPY_ANCHOR_SHARPE = 0.682
CANONICAL_GROSS_SHARPE = 0.853
CANONICAL_M1_SHARPE = 0.687
CANONICAL_M2_SHARPE = 0.768
TRACK_A_THRESHOLD = CANONICAL_GROSS_SHARPE + 0.05  # 0.903
TRACK_B_M1_THRESHOLD = CANONICAL_M1_SHARPE + 0.05  # 0.737
TRACK_B_M2_THRESHOLD = CANONICAL_M2_SHARPE + 0.05  # 0.818


def _annualised_sharpe(returns: pd.Series) -> float:
    if returns.std() == 0 or len(returns) < 2:
        return float("nan")
    return float(returns.mean() / returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def _cagr_from_equity(eq: pd.Series) -> float:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Threshold sweep sub-study")
    parser.add_argument(
        "--out-report-dir", type=Path,
        default=Path("studies/letf_rotation_hunt/reports/threshold_sweep"),
    )
    parser.add_argument(
        "--out-data-dir", type=Path,
        default=Path("data/threshold_sweep"),
    )
    args = parser.parse_args(argv)

    args.out_report_dir.mkdir(parents=True, exist_ok=True)
    args.out_data_dir.mkdir(parents=True, exist_ok=True)
    report_md_path = args.out_report_dir.parent / "THRESHOLD_SWEEP_REPORT.md"

    ffr_daily = load_ffr_daily()

    print(f"[threshold_sweep] running {len(VARIANTS)} variants")
    rows: list[dict] = []
    equity_curves: dict[str, dict[str, pd.Series]] = {}

    for i, variant in enumerate(VARIANTS, start=1):
        print(f"[threshold_sweep] [{i}/{len(VARIANTS)}] {variant['name']}")
        result = _run_single_composite_config(
            variant, datasets=["lh_56y"], ffr_daily=ffr_daily, n_trials_local=len(VARIANTS),
        )
        gross_eq = result["_equity"]
        gross_returns = result["_strategy_returns"]
        positions = result["_positions"]
        asset_returns = result["_asset_returns_aligned"]

        # Modelo 1 (per-swing FIFO): align by reindexing to gross_eq.index
        m1 = simulate_per_swing(
            positions, asset_returns,
            initial_capital=INITIAL_CAPITAL, tax_rate=TAX_RATE,
        )
        eq_m1 = m1["net_equity"].reindex(gross_eq.index)

        # Modelo 2 (annual realize)
        eq_m2 = apply_annual_darf(
            gross_eq, gross_returns, mode="annual_realize", initial=INITIAL_CAPITAL,
        )

        # Compute metrics for each tax model
        rets_gross = gross_eq.pct_change().dropna()
        rets_m1 = eq_m1.pct_change().dropna()
        rets_m2 = eq_m2.pct_change().dropna()

        rows.append({
            "name": variant["name"],
            "sma_long_buf_on": variant["sma_long_buffer_on"],
            "sma_long_buf_off": variant["sma_long_buffer_off"],
            "ar1_buffer": variant["ar1_buffer"],
            "trade_count_m1": int(m1["n_taxable_swings"]),
            "tax_paid_m1": float(m1["tax_paid_total"]),
            # Gross
            "gross_sharpe": _annualised_sharpe(rets_gross),
            "gross_cagr": _cagr_from_equity(gross_eq),
            "gross_mdd": _max_drawdown(gross_eq),
            "gross_final_equity": float(gross_eq.iloc[-1]),
            # M1
            "m1_sharpe": _annualised_sharpe(rets_m1),
            "m1_cagr": _cagr_from_equity(eq_m1),
            "m1_mdd": _max_drawdown(eq_m1),
            "m1_final_equity": float(eq_m1.iloc[-1]),
            # M2
            "m2_sharpe": _annualised_sharpe(rets_m2),
            "m2_cagr": _cagr_from_equity(eq_m2),
            "m2_mdd": _max_drawdown(eq_m2),
            "m2_final_equity": float(eq_m2.iloc[-1]),
            # Edges
            "gross_edge_vs_canonical": _annualised_sharpe(rets_gross) - CANONICAL_GROSS_SHARPE,
            "m1_edge_vs_canonical": _annualised_sharpe(rets_m1) - CANONICAL_M1_SHARPE,
            "m2_edge_vs_canonical": _annualised_sharpe(rets_m2) - CANONICAL_M2_SHARPE,
            # Track flags
            "track_a_pass": bool(_annualised_sharpe(rets_gross) >= TRACK_A_THRESHOLD),
            "track_b_m1_pass": bool(_annualised_sharpe(rets_m1) >= TRACK_B_M1_THRESHOLD),
            "track_b_m2_pass": bool(_annualised_sharpe(rets_m2) >= TRACK_B_M2_THRESHOLD),
        })

        equity_curves[variant["name"]] = {
            "gross": gross_eq, "m1": eq_m1, "m2": eq_m2,
        }

    # Write CSV
    csv_path = args.out_data_dir / "variant_metrics.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"[threshold_sweep] CSV: {csv_path}")

    # Plots
    df = pd.DataFrame(rows)
    plot_sharpe_bar(
        df, metric="gross_sharpe", reference=TRACK_A_THRESHOLD,
        title="Gross Sharpe (lh_56y) — Track A threshold 0.903",
        out_path=args.out_report_dir / "sharpe_bar_gross.png",
    )
    plot_sharpe_bar(
        df, metric="m1_sharpe", reference=TRACK_B_M1_THRESHOLD,
        title="Net M1 (per-swing) Sharpe — Track B threshold 0.737",
        out_path=args.out_report_dir / "sharpe_bar_net_m1.png",
    )
    plot_sharpe_bar(
        df, metric="m2_sharpe", reference=TRACK_B_M2_THRESHOLD,
        title="Net M2 (annual) Sharpe — Track B threshold 0.818",
        out_path=args.out_report_dir / "sharpe_bar_net_m2.png",
    )
    plot_trade_count_bar(
        df, out_path=args.out_report_dir / "trade_count_bar.png",
    )
    # Top-4 equity overlay: top by m1_sharpe
    top_4_names = df.nlargest(4, "m1_sharpe")["name"].tolist()
    spy_full = load_testfolio_series("SPYSIM").dropna()
    plot_equity_overlay_top4(
        equity_curves={n: equity_curves[n] for n in top_4_names},
        spy_full=spy_full,
        out_path=args.out_report_dir / "equity_overlay_top4.png",
    )

    # Markdown report
    report_md_path.write_text(_render_report(df))
    print(f"[threshold_sweep] report: {report_md_path}")
    return 0


def _render_report(df: pd.DataFrame) -> str:
    out: list[str] = []
    out.append("# LETF Threshold Sweep — T3d K=2 with hysteresis buffers")
    out.append("")
    out.append(f"_Generated {datetime.now(timezone.utc).isoformat()}_")
    out.append("")
    out.append("Spec: pre-publication agent spec removed from the public tree.")
    out.append("")

    out.append("## 1. Methodology")
    out.append("")
    out.append(f"- Universe: 12 variants of `qld_vote_k2_off_zroz` (canonical T3d K=2)")
    out.append(f"- Track A threshold (gross Sharpe): **{TRACK_A_THRESHOLD:.3f}** "
               f"(canonical {CANONICAL_GROSS_SHARPE} + 0.05)")
    out.append(f"- Track B M1 threshold (per-swing 15%): **{TRACK_B_M1_THRESHOLD:.3f}** "
               f"(canonical {CANONICAL_M1_SHARPE} + 0.05)")
    out.append(f"- Track B M2 threshold (annual 15%): **{TRACK_B_M2_THRESHOLD:.3f}** "
               f"(canonical {CANONICAL_M2_SHARPE} + 0.05)")
    out.append("")

    out.append("## 2. Track A — Gross results")
    out.append("")
    out.append("![Gross Sharpe](threshold_sweep/sharpe_bar_gross.png)")
    out.append("")
    cols_a = ["name", "gross_sharpe", "gross_cagr", "gross_mdd",
              "trade_count_m1", "gross_edge_vs_canonical", "track_a_pass"]
    out.append(df[cols_a].to_markdown(index=False, floatfmt=".3f"))
    out.append("")
    n_a = int(df["track_a_pass"].sum())
    out.append(f"**Track A winners: {n_a} of {len(df)}** "
               f"(Sharpe ≥ {TRACK_A_THRESHOLD:.3f}).")
    out.append("")

    out.append("## 3. Track B — Net results (M1 / M2)")
    out.append("")
    out.append("![Net M1 Sharpe](threshold_sweep/sharpe_bar_net_m1.png)")
    out.append("")
    out.append("![Net M2 Sharpe](threshold_sweep/sharpe_bar_net_m2.png)")
    out.append("")
    out.append("![Trade count](threshold_sweep/trade_count_bar.png)")
    out.append("")
    cols_b = ["name", "m1_sharpe", "m2_sharpe", "trade_count_m1",
              "m1_edge_vs_canonical", "m2_edge_vs_canonical",
              "track_b_m1_pass", "track_b_m2_pass"]
    out.append(df[cols_b].to_markdown(index=False, floatfmt=".3f"))
    out.append("")
    n_b_m1 = int(df["track_b_m1_pass"].sum())
    n_b_m2 = int(df["track_b_m2_pass"].sum())
    out.append(f"**Track B-M1 winners: {n_b_m1} of {len(df)}** "
               f"(M1 Sharpe ≥ {TRACK_B_M1_THRESHOLD:.3f}).")
    out.append(f"**Track B-M2 winners: {n_b_m2} of {len(df)}** "
               f"(M2 Sharpe ≥ {TRACK_B_M2_THRESHOLD:.3f}).")
    out.append("")

    out.append("## 4. Synthesis")
    out.append("")
    out.append("![Equity overlay top-4](threshold_sweep/equity_overlay_top4.png)")
    out.append("")
    if n_a > 0 and n_b_m1 > 0:
        winners_both = df[df["track_a_pass"] & df["track_b_m1_pass"]]["name"].tolist()
        out.append(f"**Both tracks pass:** {winners_both} — unambiguous winners. "
                   f"Recommend full 7-gate re-run + cohort_robustness rerun.")
    elif n_b_m1 > 0:
        winners_b = df[df["track_b_m1_pass"]]["name"].tolist()
        out.append(f"**Track B only:** {winners_b} — net deploy improvement, gross neutral. "
                   f"Document but do NOT replace canonical (per spec §3.3).")
    elif n_a > 0:
        winners_a = df[df["track_a_pass"]]["name"].tolist()
        out.append(f"**Track A only:** {winners_a} — suspicious, run extra OOS validation.")
    else:
        out.append("**Neither track passes:** thresholds are wash. Canonical T3d K=2 stands.")
    out.append("")

    out.append("## Citations")
    out.append("")
    out.append("- `[trading_systems_methods, Kaufman ch.6, ch.21]` — signal smoothing, regime sensitivity.")
    out.append("- `[systematic_trading, Carver p.122-133, p.174]` — EWMAC smoothing, asymmetric exit.")
    out.append("- `[advances_fin_ml, p.208-211, p.275]` — CSCV PBO, deflated SR.")
    out.append("- Parent: `STUDY_FINAL_REPORT.md` §3.4.")
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
