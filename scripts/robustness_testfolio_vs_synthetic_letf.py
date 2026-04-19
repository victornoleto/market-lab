"""Phase 3.5b Task 7a — Testfolio vs synthetic LETF cross-check.

Compares:
  (1) synthesize_letf_returns(spx_tr, L=2, fee=0.01)  — Gayed p.16 flat-fee model
  (2) testfolio spy_2x_equity (time-varying FFR-aware cost)
  (3) UPRO/SSO real ETFs — NOT AVAILABLE in Tiingo cache as of 2026-04-17
      (manifest inspection: UPRO/SSO/SPXL missing). Report flags this as
      a data gap; comparison reduces to 2-way synthetic vs testfolio.

Citations
---------
* Synthetic LETF formula `r = L*r_spx - fee/252`
  `[leverage_for_the_long_run, p.16]` (footnote 22).
* Testfolio cost model `cost = SW*(L-1)*(FFR + SP)`: `data/external/README.md`
  lines 24-33.
* Comparison window starts 1962-01-01 per `data/external/README.md` lines
  75-83 (pre-1962 testfolio uses Schwert reconstruction; not comparable
  to KF market factor).

Outputs
-------
reports/phase3_5b/robustness/testfolio_vs_synthetic_letf.md
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.spx_tr_loader import (
    fetch_ken_french_daily,
    load_spx_tr_daily,
)
from ai_trade.backtest.helpers.synthetic_letf import (
    TRADING_DAYS_PER_YEAR,
    synthesize_letf_returns,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)


TESTFOLIO_PARQUET = Path("data/external/testfolio_spysim_leverage.parquet")
COMPARE_START = pd.Timestamp("1962-01-01")
OUT_DIR = Path("reports/phase3_5b/robustness")


def cagr(series: pd.Series) -> float:
    """CAGR from an equity curve using trading-day convention."""
    if len(series) < 2:
        return float("nan")
    total = float(series.iloc[-1] / series.iloc[0])
    years = (len(series) - 1) / TRADING_DAYS_PER_YEAR
    if years <= 0 or total <= 0:
        return float("nan")
    return total ** (1.0 / years) - 1.0


def build_equity_from_returns(rets: pd.Series, start_value: float = 10_000.0) -> pd.Series:
    """Cumulative equity curve from daily decimal returns."""
    return (1.0 + rets.fillna(0.0)).cumprod() * start_value


def annualized_ffr_series(kf_df: pd.DataFrame) -> pd.Series:
    """Annualized FFR proxy from Ken French RF column (decimal/yr)."""
    return kf_df["rf"] * TRADING_DAYS_PER_YEAR


def year_bucket(ffr_yearly_mean: float) -> str:
    """FFR bucket label per spec (§data/external/README.md Task 7a)."""
    if ffr_yearly_mean < 0.02:
        return "FFR<2%"
    if ffr_yearly_mean < 0.05:
        return "2≤FFR<5%"
    return "FFR≥5%"


def run_analysis(out_dir: Path = OUT_DIR) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Testfolio
    log.info("Loading testfolio parquet...")
    tf = pd.read_parquet(TESTFOLIO_PARQUET)
    tf.index = pd.to_datetime(tf.index)
    tf = tf.sort_index()
    tf_2x_full = tf["spy_2x_equity"]

    # 2. KF factors (for FFR + pre-2001 SPX TR)
    log.info("Loading Ken French factors...")
    kf_df = fetch_ken_french_daily()
    kf_end = kf_df.index.max()
    log.info("KF last date: %s", kf_end.date())

    compare_end = min(tf.index.max(), kf_end)
    log.info("Comparison window: %s → %s", COMPARE_START.date(), compare_end.date())

    # 3. SPX TR stitched (KF pre-2001-05-14 + Tiingo SPY post)
    spx_tr = load_spx_tr_daily(start=COMPARE_START, end=compare_end)

    # 4. Synthetic 2x LETF with flat 1% fee (Gayed)
    synth_2x_rets = synthesize_letf_returns(spx_tr, leverage=2.0, annual_fee=0.01)
    synth_2x_eq = build_equity_from_returns(synth_2x_rets)

    # 5. Testfolio 2x, converted to returns on its own grid, then aligned
    tf_2x = tf_2x_full.loc[
        (tf_2x_full.index >= COMPARE_START) & (tf_2x_full.index <= compare_end)
    ]
    tf_2x_rets = tf_2x.pct_change().dropna()

    # Align on intersection of dates
    common_idx = synth_2x_rets.index.intersection(tf_2x_rets.index)
    if len(common_idx) < 100:
        raise RuntimeError(
            f"alignment too sparse: {len(common_idx)} common days"
        )
    synth_aligned = synth_2x_rets.loc[common_idx]
    tf_aligned = tf_2x_rets.loc[common_idx]

    # Re-base equity curves on the aligned index (same start)
    synth_eq = build_equity_from_returns(synth_aligned)
    tf_eq = build_equity_from_returns(tf_aligned)

    # 6. CAGR whole window
    full_synth_cagr = cagr(synth_eq)
    full_tf_cagr = cagr(tf_eq)
    full_gap = full_synth_cagr - full_tf_cagr
    log.info(
        "Full window [%s → %s, %d days]: synth=%.4f tf=%.4f gap=%.4f",
        common_idx[0].date(),
        common_idx[-1].date(),
        len(common_idx),
        full_synth_cagr,
        full_tf_cagr,
        full_gap,
    )

    # 7. Per-FFR-bucket CAGR (grouped by calendar year)
    ffr = annualized_ffr_series(kf_df).loc[common_idx]

    df = pd.DataFrame(
        {"synth_r": synth_aligned, "tf_r": tf_aligned, "ffr_ann": ffr}
    )
    df["year"] = df.index.year
    yearly = (
        df.groupby("year")
        .agg(
            days=("synth_r", "size"),
            ffr_mean=("ffr_ann", "mean"),
            synth_total=("synth_r", lambda s: float((1 + s.fillna(0)).prod())),
            tf_total=("tf_r", lambda s: float((1 + s.fillna(0)).prod())),
        )
        .reset_index()
    )
    yearly["bucket"] = yearly["ffr_mean"].apply(year_bucket)

    # Aggregate each bucket as: CAGR of the concatenated return path
    bucket_rows = []
    for bucket, grp in df.assign(
        bucket=lambda x: (x["ffr_ann"].rolling(252, min_periods=252).mean())
    ).dropna().groupby("bucket"):
        # Not used; we aggregate by yearly bucket instead to respect the
        # "≥5 years of data" requirement of the gate.
        pass

    bucket_summary_rows = []
    for bucket in ["FFR<2%", "2≤FFR<5%", "FFR≥5%"]:
        sub = yearly[yearly["bucket"] == bucket]
        if sub.empty:
            continue
        years = len(sub)
        total_days = int(sub["days"].sum())
        synth_prod = float(sub["synth_total"].prod())
        tf_prod = float(sub["tf_total"].prod())
        b_synth_cagr = synth_prod ** (TRADING_DAYS_PER_YEAR / total_days) - 1
        b_tf_cagr = tf_prod ** (TRADING_DAYS_PER_YEAR / total_days) - 1
        bucket_summary_rows.append(
            {
                "bucket": bucket,
                "years": years,
                "days": total_days,
                "ffr_mean": sub["ffr_mean"].mean(),
                "synth_cagr": b_synth_cagr,
                "tf_cagr": b_tf_cagr,
                "gap": b_synth_cagr - b_tf_cagr,
            }
        )
    bucket_summary = pd.DataFrame(bucket_summary_rows)

    # Gate decision: any bucket with years≥5 and |gap| > 2%/yr
    gate_triggered = bool(
        (
            (bucket_summary["years"] >= 5)
            & (bucket_summary["gap"].abs() > 0.02)
        ).any()
    )

    # 8. Export artifacts
    yearly_csv = out_dir / "testfolio_vs_synth_yearly.csv"
    yearly.to_csv(yearly_csv, index=False)
    bucket_csv = out_dir / "testfolio_vs_synth_buckets.csv"
    bucket_summary.to_csv(bucket_csv, index=False)

    # 9. Markdown report
    md_path = out_dir / "testfolio_vs_synthetic_letf.md"
    lines: list[str] = []
    lines.append("# Testfolio vs Synthetic LETF Cross-Check — Phase 3.5b Task 7a")
    lines.append("")
    lines.append(f"**Window:** {common_idx[0].date()} → {common_idx[-1].date()} ")
    lines.append(f"({len(common_idx)} trading days, "
                 f"{len(common_idx)/TRADING_DAYS_PER_YEAR:.1f} yrs)")
    lines.append("")
    lines.append(
        "**Purpose:** validate `synthesize_letf_returns(spx_tr, L=2, fee=0.01)` "
        "against testfolio's FFR-aware cost model, to decide whether to "
        "swap the Gayed flat-1% fee for a time-varying model."
    )
    lines.append("")
    lines.append("## Data sources")
    lines.append("")
    lines.append(
        "- (1) **Synthetic 2x:** `synthesize_letf_returns(spx_tr_daily, "
        "leverage=2.0, annual_fee=0.01)` — Gayed flat-fee per "
        "`[leverage_for_the_long_run, p.16]`. SPX TR stitched via "
        "`load_spx_tr_daily` (KF pre-2001-05-14 + Tiingo SPY post)."
    )
    lines.append(
        "- (2) **Testfolio 2x:** `spy_2x_equity` column of "
        "`data/external/testfolio_spysim_leverage.parquet`, truncated to "
        "1962-01-01+ (pre-1962 uses Schwert reconstruction, not "
        "comparable — see `data/external/README.md`)."
    )
    lines.append(
        "- (3) **UPRO/SSO real ETFs — NOT AVAILABLE.** Tiingo manifest "
        "inspection (2026-04-17) confirms these tickers are missing from "
        "`data/tiingo/daily/prices/`. The 3-way comparison of the spec "
        "reduces to 2-way. **⚠️ FLAG:** to complete the 3-way, a future "
        "iteration must add UPRO (2009-06+) and SSO (2006-06+) to the "
        "Tiingo cache."
    )
    lines.append("")
    lines.append("## Full-window CAGR")
    lines.append("")
    lines.append("| Series | CAGR |")
    lines.append("|--------|------|")
    lines.append(f"| Synthetic 2x (flat 1% fee) | {full_synth_cagr*100:.3f}% |")
    lines.append(f"| Testfolio 2x (FFR-aware)   | {full_tf_cagr*100:.3f}% |")
    lines.append(f"| **Gap (synth − testfolio)** | **{full_gap*100:+.3f}%** |")
    lines.append("")
    lines.append(
        "A positive gap means our Gayed model **overstates** LETF return "
        "(under-models real cost). A negative gap means we under-state "
        "return (over-model cost)."
    )
    lines.append("")
    lines.append("## FFR-bucket stratified CAGR")
    lines.append("")
    lines.append(
        "Years grouped by their mean annualized FFR; CAGR within each "
        "bucket computed from the concatenated product of yearly total "
        "returns. Buckets follow §7a of `specs/phase_3_5b_winners_validation.md`."
    )
    lines.append("")
    lines.append("| Bucket | Years | Days | FFR mean | Synth CAGR | Testfolio CAGR | Gap (synth−tf) |")
    lines.append("|--------|------:|-----:|---------:|-----------:|---------------:|---------------:|")
    for _, r in bucket_summary.iterrows():
        lines.append(
            f"| {r['bucket']} | {int(r['years'])} | {int(r['days'])} | "
            f"{r['ffr_mean']*100:.2f}% | {r['synth_cagr']*100:.3f}% | "
            f"{r['tf_cagr']*100:.3f}% | {r['gap']*100:+.3f}% |"
        )
    lines.append("")
    lines.append("## Gate decision")
    lines.append("")
    lines.append(
        f"Gate: any bucket with ≥5 years and |gap| > 2%/yr → **implement "
        f"`synthesize_letf_returns_ffr_aware()`** and re-run B1c gates."
    )
    lines.append("")
    if gate_triggered:
        worst = bucket_summary.loc[bucket_summary["gap"].abs().idxmax()]
        lines.append(
            f"**GATE TRIGGERED.** Worst bucket: `{worst['bucket']}` "
            f"({int(worst['years'])} years, gap {worst['gap']*100:+.3f}%/yr). "
            f"Action: build FFR-aware synthesizer in a follow-up iteration."
        )
    else:
        lines.append(
            "**GATE NOT TRIGGERED.** All buckets with ≥5 years of data "
            "show |gap| ≤ 2%/yr. The Gayed flat-1% model is empirically "
            "close enough to testfolio's FFR-aware model for the "
            "1962-present window — no re-validation needed for B1c. "
            "Follow-up work (UPRO/SSO real cache, stress over Volcker "
            "years isolated) remains open."
        )
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(
        f"- `{yearly_csv.name}` — per-year CAGR + FFR mean."
    )
    lines.append(
        f"- `{bucket_csv.name}` — per-bucket summary (matches the table above)."
    )
    lines.append("")
    lines.append(
        f"Generated by `scripts/robustness_testfolio_vs_synthetic_letf.py` "
        f"on 2026-04-17."
    )
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    log.info("Wrote %s", md_path)

    return {
        "md_path": str(md_path),
        "yearly_csv": str(yearly_csv),
        "bucket_csv": str(bucket_csv),
        "full_gap": full_gap,
        "gate_triggered": gate_triggered,
        "bucket_summary": bucket_summary.to_dict(orient="records"),
        "window": (str(common_idx[0].date()), str(common_idx[-1].date())),
        "n_days": int(len(common_idx)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()
    result = run_analysis(out_dir=args.out_dir)
    print("\n=== Summary ===")
    print(f"Window:        {result['window'][0]} → {result['window'][1]} "
          f"({result['n_days']} days)")
    print(f"Full-win gap:  {result['full_gap']*100:+.3f}%/yr")
    print(f"Gate trigger:  {result['gate_triggered']}")
    for b in result["bucket_summary"]:
        print(
            f"  {b['bucket']:10s}  years={int(b['years']):3d}  "
            f"gap={b['gap']*100:+.3f}%/yr"
        )


if __name__ == "__main__":
    main()
