# 022-2026-05-06-T3d-extended-grid — SUMMARY

**Tier:** T3d
**Hypothesis:** T3d-extended (12-config grid for G1 PBO statistical power). 6 diverse signal-subsets × K∈{2,3} on QLD/ZROZ. Pre-registered per spec §3.4: T3d-extended winner only beats T3d K=2 if Sharpe > 0.853 + 0.05 = 0.903; goal is G1 PBO statistical power, not param-sweep curve-fit.
**Primary citation:** spec §2.4 T3d composite (extended grid for G1 PBO power per advances_fin_ml p.208-211)
**Engine SHA:** `255e5d8`
**Datetime UTC:** 2026-05-08T14:15:34.215383+00:00
**Configs tested:** 12

## TL;DR

Best config: **`qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`** (STRONG, score 76.5/100). lh_56y: Sharpe 0.919 (edge vs SPY +0.237), CAGR 31.09%, MDD -64.5%.  **KILL T0:** PASS (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK3_sma250_100_vol21_40_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK2_ema200_50_vol21_40_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK3_sma200_50_vol21_30_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK3_sma200_50_vol42_40_ar30_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | QLD | ZROZ | ? | ? |
| `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | QLD | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | 0.853 | 0.786 | 0.842 | 0.976 | 27.93% | 24.75% | 24.88% | 29.39% | -74.9% | -74.9% | -60.5% | -60.5% |
| `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | 0.798 | 0.727 | 0.594 | 0.751 | 21.66% | 18.78% | 14.08% | 18.95% | -53.1% | -53.1% | -53.1% | -53.1% |
| `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | 0.919 | 0.855 | 0.777 | 0.921 | 31.09% | 28.05% | 22.55% | 27.62% | -64.5% | -64.5% | -64.5% | -64.5% |
| `qld_voteK3_sma250_100_vol21_40_ar30_off_zroz` | 0.745 | 0.640 | 0.523 | 0.659 | 19.98% | 15.92% | 11.85% | 16.17% | -55.8% | -55.8% | -55.8% | -55.8% |
| `qld_voteK2_ema200_50_vol21_40_ar30_off_zroz` | 0.753 | 0.675 | 0.672 | 0.817 | 23.11% | 19.59% | 18.15% | 23.13% | -67.6% | -67.6% | -63.4% | -63.4% |
| `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | 0.776 | 0.665 | 0.520 | 0.697 | 20.90% | 16.60% | 11.63% | 17.15% | -56.4% | -56.4% | -56.4% | -56.4% |
| `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | 0.843 | 0.769 | 0.810 | 0.996 | 27.04% | 23.61% | 23.04% | 29.74% | -74.9% | -74.9% | -60.5% | -60.5% |
| `qld_voteK3_sma200_50_vol21_30_ar30_off_zroz` | 0.769 | 0.687 | 0.577 | 0.673 | 19.77% | 16.61% | 13.06% | 15.65% | -51.0% | -51.0% | -51.0% | -51.0% |
| `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | 0.846 | 0.784 | 0.828 | 0.943 | 27.72% | 24.74% | 24.50% | 28.39% | -74.9% | -74.9% | -60.0% | -60.0% |
| `qld_voteK3_sma200_50_vol42_40_ar30_off_zroz` | 0.772 | 0.707 | 0.643 | 0.742 | 20.67% | 17.97% | 15.77% | 18.79% | -50.5% | -50.5% | -50.5% | -50.5% |
| `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | 0.836 | 0.767 | 0.740 | 0.875 | 27.16% | 23.91% | 20.83% | 25.51% | -62.2% | -62.2% | -62.2% | -62.2% |
| `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | 0.818 | 0.756 | 0.541 | 0.583 | 22.48% | 19.85% | 12.36% | 13.22% | -53.5% | -53.5% | -53.5% | -53.5% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | 0.421 | 0.0001 | 6/8 >SPY (MDD 75% warn) | 0.849 | 0.636 | 0.490 | 0.00pp | STRONG |
| `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | 0.421 | 0.0003 | 6/8 >SPY (MDD 51% warn) | 0.606 | 0.453 | 0.422 | 0.00pp | PROMISING |
| `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | 0.421 | 0.0000 | 6/8 >SPY (MDD 64% warn) | 0.822 | 0.708 | 0.554 | 0.00pp | STRONG |
| `qld_voteK3_sma250_100_vol21_40_ar30_off_zroz` | 0.421 | 0.0011 | 7/8 >SPY (MDD 51% warn) | 0.503 | 0.361 | 0.385 | 0.00pp | PROMISING |
| `qld_voteK2_ema200_50_vol21_40_ar30_off_zroz` | 0.421 | 0.0010 | 6/8 >SPY (MDD 68% warn) | 0.816 | 0.611 | 0.396 | 0.00pp | PROMISING |
| `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | 0.421 | 0.0006 | 5/8 >SPY (MDD 55% warn) | 0.493 | 0.436 | 0.397 | 0.00pp | PROMISING |
| `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | 0.421 | 0.0001 | 6/8 >SPY (MDD 75% warn) | 0.815 | 0.666 | 0.469 | 0.00pp | STRONG |
| `qld_voteK3_sma200_50_vol21_30_ar30_off_zroz` | 0.421 | 0.0007 | 4/8 >SPY (MDD 51% warn) | 0.511 | 0.459 | 0.412 | 0.00pp | MARGINAL |
| `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | 0.421 | 0.0001 | 6/8 >SPY (MDD 75% warn) | 0.777 | 0.674 | 0.475 | 0.00pp | STRONG |
| `qld_voteK3_sma200_50_vol42_40_ar30_off_zroz` | 0.421 | 0.0006 | 6/8 >SPY (MDD 50% warn) | 0.621 | 0.492 | 0.416 | 0.00pp | PROMISING |
| `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | 0.421 | 0.0002 | 6/8 >SPY (MDD 62% warn) | 0.768 | 0.612 | 0.483 | 0.00pp | STRONG |
| `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | 0.421 | 0.0002 | 6/8 >SPY (MDD 53% warn) | 0.457 | 0.249 | 0.463 | 0.00pp | PROMISING |

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

- **Best config:** `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (STRONG, score 76.5)
- **KILL T0:** PASS (study viable)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 418
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.919 (lh_56y) clears SPY+0.05 — single-LETF Gayed rotation has prima-facie edge in this universe. Proceeding to T1b period sweep.

## Next iter

