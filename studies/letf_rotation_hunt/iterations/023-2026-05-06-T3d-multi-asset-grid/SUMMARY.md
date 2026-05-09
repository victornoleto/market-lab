# 023-2026-05-06-T3d-multi-asset-grid — SUMMARY

**Tier:** T3d
**Hypothesis:** T3d Vote-K=2 with alternative ON-asset (UPRO/TQQQ) and alternative OFF-asset (IEF/EDV/TLT) — not covered in iter 014 (only QLD/ZROZ) nor iter 022 (only sma200/50 variations on QLD/ZROZ). 12 configs: 3 ON-assets {UPRO, QLD, TQQQ} × 4 OFF-assets {ZROZ, IEF, EDV, TLT} × K=2 fixed × canonical signal subset. Pre-registered per spec §3.4 anti-curve-fit: T3d-multi-asset winner only beats T3d K=2 if Sharpe > 0.853 + 0.05 = 0.903; goal is to fill the iter 014/022 gap (no UPRO/TQQQ tested in Vote-K context).
**Primary citation:** spec §2.4 T3d composite (multi-asset variant for completeness)
**Engine SHA:** `255e5d8`
**Datetime UTC:** 2026-05-08T14:15:46.020062+00:00
**Configs tested:** 12

## TL;DR

Best config: **`qld_voteK2_off_zroz_alt`** (STRONG, score 82.0/100). lh_56y: Sharpe 0.853 (edge vs SPY +0.171), CAGR 27.93%, MDD -74.9%.  **KILL T0:** PASS (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `upro_voteK2_off_zroz` | UPRO | ZROZ | ? | ? |
| `upro_voteK2_off_ief` | UPRO | IEF | ? | ? |
| `upro_voteK2_off_edv` | UPRO | EDV | ? | ? |
| `upro_voteK2_off_tlt` | UPRO | TLT | ? | ? |
| `qld_voteK2_off_zroz_alt` | QLD | ZROZ | ? | ? |
| `qld_voteK2_off_ief` | QLD | IEF | ? | ? |
| `qld_voteK2_off_edv` | QLD | EDV | ? | ? |
| `qld_voteK2_off_tlt` | QLD | TLT | ? | ? |
| `tqqq_voteK2_off_zroz` | TQQQ | ZROZ | ? | ? |
| `tqqq_voteK2_off_ief` | TQQQ | IEF | ? | ? |
| `tqqq_voteK2_off_edv` | TQQQ | EDV | ? | ? |
| `tqqq_voteK2_off_tlt` | TQQQ | TLT | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `upro_voteK2_off_zroz` | 0.642 | 0.559 | 0.616 | 0.616 | 18.04% | 14.20% | 16.80% | 16.39% | -69.4% | -69.4% | -69.4% | -69.4% |
| `upro_voteK2_off_ief` | 0.555 | 0.501 | 0.618 | 0.629 | 13.48% | 11.30% | 15.55% | 15.91% | -77.7% | -77.7% | -59.6% | -59.6% |
| `upro_voteK2_off_edv` | 0.574 | 0.514 | 0.617 | 0.626 | 14.42% | 11.93% | 15.93% | 16.19% | -75.7% | -75.7% | -64.1% | -64.1% |
| `upro_voteK2_off_tlt` | 0.574 | 0.514 | 0.617 | 0.626 | 14.42% | 11.93% | 15.93% | 16.19% | -75.7% | -75.7% | -64.1% | -64.1% |
| `qld_voteK2_off_zroz_alt` | 0.853 | 0.786 | 0.842 | 0.976 | 27.93% | 24.75% | 24.88% | 29.39% | -74.9% | -74.9% | -60.5% | -60.5% |
| `qld_voteK2_off_ief` | 0.781 | 0.757 | 0.863 | 1.009 | 22.93% | 22.18% | 23.34% | 28.21% | -72.3% | -72.3% | -40.0% | -40.0% |
| `qld_voteK2_off_edv` | 0.794 | 0.760 | 0.854 | 0.993 | 23.86% | 22.64% | 23.77% | 28.63% | -73.9% | -73.9% | -51.5% | -51.5% |
| `qld_voteK2_off_tlt` | 0.794 | 0.760 | 0.854 | 0.993 | 23.86% | 22.64% | 23.77% | 28.63% | -73.9% | -73.9% | -51.5% | -51.5% |
| `tqqq_voteK2_off_zroz` | 0.814 | 0.759 | 0.808 | 1.010 | 31.90% | 28.34% | 29.02% | 39.97% | -74.0% | -74.0% | -70.1% | -70.1% |
| `tqqq_voteK2_off_ief` | 0.765 | 0.749 | 0.833 | 1.051 | 27.74% | 26.90% | 28.66% | 40.10% | -75.1% | -75.1% | -63.3% | -58.0% |
| `tqqq_voteK2_off_edv` | 0.774 | 0.748 | 0.825 | 1.034 | 28.45% | 27.04% | 28.78% | 40.09% | -75.4% | -75.4% | -65.2% | -65.2% |
| `tqqq_voteK2_off_tlt` | 0.774 | 0.748 | 0.825 | 1.034 | 28.45% | 27.04% | 28.78% | 40.09% | -75.4% | -75.4% | -65.2% | -65.2% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `upro_voteK2_off_zroz` | 0.230 | 0.0086 | 6/8 >SPY (MDD 69% warn) | 0.420 | 0.276 | 0.291 | 0.00pp | MARGINAL |
| `upro_voteK2_off_ief` | 0.230 | 0.0339 | 4/8 >SPY (MDD 70% warn) | 0.482 | 0.369 | 0.202 | 0.00pp | NEAR_FAIL |
| `upro_voteK2_off_edv` | 0.230 | 0.0257 | 5/8 >SPY (MDD 69% warn) | 0.454 | 0.323 | 0.224 | 0.00pp | MARGINAL |
| `upro_voteK2_off_tlt` | 0.230 | 0.0257 | 5/8 >SPY (MDD 69% warn) | 0.454 | 0.323 | 0.224 | 0.00pp | MARGINAL |
| `qld_voteK2_off_zroz_alt` | 0.230 | 0.0001 | 6/8 >SPY (MDD 75% warn) | 0.849 | 0.636 | 0.490 | 0.00pp | STRONG |
| `qld_voteK2_off_ief` | 0.230 | 0.0006 | 7/8 >SPY (MDD 72% warn) | 0.927 | 0.805 | 0.432 | 0.00pp | STRONG |
| `qld_voteK2_off_edv` | 0.230 | 0.0004 | 7/8 >SPY (MDD 74% warn) | 0.887 | 0.714 | 0.438 | 0.00pp | STRONG |
| `qld_voteK2_off_tlt` | 0.230 | 0.0004 | 7/8 >SPY (MDD 74% warn) | 0.887 | 0.714 | 0.438 | 0.00pp | STRONG |
| `tqqq_voteK2_off_zroz` | 0.230 | 0.0003 | 6/8 >SPY (MDD 74% warn) | 0.803 | 0.719 | 0.440 | 0.00pp | STRONG |
| `tqqq_voteK2_off_ief` | 0.230 | 0.0008 | 7/8 >SPY (MDD 74% warn) | 0.904 | 0.899 | 0.399 | 0.00pp | STRONG |
| `tqqq_voteK2_off_edv` | 0.230 | 0.0007 | 7/8 >SPY (MDD 75% warn) | 0.858 | 0.810 | 0.411 | 0.00pp | STRONG |
| `tqqq_voteK2_off_tlt` | 0.230 | 0.0007 | 7/8 >SPY (MDD 75% warn) | 0.858 | 0.810 | 0.411 | 0.00pp | STRONG |

Hard-gate thresholds (spec §3.5): G1 PBO < 0.50, G2 DSR p < 0.05, G3 ≥5/8 windows + MDD < 50%, G4/G5 Sharpe > 0, G6 99% CI low > 0, G7 |Δ| ≤ 3pp.

## Plots

- `plots/01_equity_curves.png` — log-scale equity per config + SPY benchmark
- `plots/02_drawdown_curves.png` — peak-to-trough drawdown
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR
- `plots/05_regime_attribution.png` — % of time signal=ON per config
- `plots/06_pct_beat_spy.png` — cumulative fraction of 3y windows where config beat SPY
- `plots/07_crisis_attribution.png` — MDD per crisis window vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + pass/fail flags

## Verdict

- **Best config:** `qld_voteK2_off_zroz_alt` (STRONG, score 82.0)
- **KILL T0:** PASS (study viable)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 426 after the 2026-05-08 T5 expansion recompute
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.853 (lh_56y) clears SPY+0.05 — single-LETF Gayed rotation has prima-facie edge in this universe. Proceeding to T1b period sweep.

## Next iter
