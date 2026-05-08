# 002-2026-05-06-T1b-qld-period-sweep — SUMMARY

**Tier:** T1b
**Hypothesis:** Among QLD 2× NDX rotation params, no period beats SMA200 by ≥0.05 Sharpe (lh_56y) — anti-curve-fit pre-registered. T1a winner (QLD SMA200) Sharpe 0.678; threshold to claim T1b winner = 0.728.
**Primary citation:** [leverage_for_the_long_run, p.13]
**Engine SHA:** `ad8bab2`
**Datetime UTC:** 2026-05-06T18:10:23.494526+00:00
**Configs tested:** 10

## TL;DR

Best config: **`qld_sma50_off_bil`** (MARGINAL, score 47.0/100). lh_56y: Sharpe 0.688 (edge vs SPY +0.006), CAGR 18.11%, MDD -68.1%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `qld_sma50_off_bil` | QLD | BIL | sma | 50 |
| `qld_sma100_off_bil` | QLD | BIL | sma | 100 |
| `qld_sma150_off_bil` | QLD | BIL | sma | 150 |
| `qld_sma200_off_bil` | QLD | BIL | sma | 200 |
| `qld_sma250_off_bil` | QLD | BIL | sma | 250 |
| `qld_ema50_off_bil` | QLD | BIL | ema | 50 |
| `qld_ema100_off_bil` | QLD | BIL | ema | 100 |
| `qld_ema150_off_bil` | QLD | BIL | ema | 150 |
| `qld_ema200_off_bil` | QLD | BIL | ema | 200 |
| `qld_ema250_off_bil` | QLD | BIL | ema | 250 |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `qld_sma50_off_bil` | 0.688 | 0.660 | 0.653 | 0.772 | 18.11% | 17.23% | 14.82% | 17.88% | -68.1% | -68.1% | -41.5% | -37.9% |
| `qld_sma100_off_bil` | 0.669 | 0.653 | 0.581 | 0.663 | 17.55% | 17.30% | 13.06% | 15.46% | -60.4% | -60.4% | -50.2% | -39.2% |
| `qld_sma150_off_bil` | 0.580 | 0.570 | 0.545 | 0.676 | 14.48% | 14.26% | 12.28% | 16.43% | -79.4% | -79.4% | -56.6% | -47.6% |
| `qld_sma200_off_bil` | 0.678 | 0.687 | 0.816 | 0.904 | 18.63% | 19.34% | 21.78% | 25.24% | -75.6% | -75.6% | -44.5% | -44.5% |
| `qld_sma250_off_bil` | 0.678 | 0.685 | 0.738 | 0.817 | 19.01% | 19.67% | 19.13% | 22.45% | -69.7% | -69.7% | -44.5% | -44.5% |
| `qld_ema50_off_bil` | 0.561 | 0.537 | 0.589 | 0.704 | 13.35% | 12.59% | 12.87% | 16.01% | -79.0% | -79.0% | -40.5% | -40.5% |
| `qld_ema100_off_bil` | 0.648 | 0.646 | 0.628 | 0.707 | 16.72% | 16.88% | 14.60% | 17.05% | -68.7% | -68.7% | -43.7% | -43.7% |
| `qld_ema150_off_bil` | 0.677 | 0.673 | 0.628 | 0.776 | 18.04% | 18.19% | 14.85% | 19.94% | -58.7% | -58.7% | -52.5% | -40.2% |
| `qld_ema200_off_bil` | 0.625 | 0.625 | 0.633 | 0.805 | 16.47% | 16.74% | 15.27% | 21.68% | -72.7% | -72.7% | -47.5% | -39.2% |
| `qld_ema250_off_bil` | 0.600 | 0.588 | 0.599 | 0.737 | 15.77% | 15.48% | 14.28% | 19.67% | -78.5% | -78.5% | -44.7% | -44.7% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `qld_sma50_off_bil` | 0.873 | 0.0028 | 6/8 >SPY (MDD 68% warn) | 0.708 | 0.796 | 0.348 | 0.00pp | MARGINAL |
| `qld_sma100_off_bil` | 0.873 | 0.0040 | 7/8 >SPY (MDD 60% warn) | 0.570 | 0.725 | 0.311 | 0.00pp | NEAR_FAIL |
| `qld_sma150_off_bil` | 0.873 | 0.0182 | 6/8 >SPY (MDD 78% warn) | 0.760 | 0.815 | 0.182 | 0.00pp | MARGINAL |
| `qld_sma200_off_bil` | 0.873 | 0.0035 | 7/8 >SPY (MDD 76% warn) | 0.947 | 0.936 | 0.296 | 0.00pp | MARGINAL |
| `qld_sma250_off_bil` | 0.873 | 0.0034 | 7/8 >SPY (MDD 70% warn) | 0.833 | 0.876 | 0.315 | 0.00pp | MARGINAL |
| `qld_ema50_off_bil` | 0.873 | 0.0246 | 5/8 >SPY (MDD 79% warn) | 0.669 | 0.809 | 0.190 | 0.00pp | MARGINAL |
| `qld_ema100_off_bil` | 0.873 | 0.0058 | 6/8 >SPY (MDD 69% warn) | 0.662 | 0.802 | 0.282 | 0.00pp | NEAR_FAIL |
| `qld_ema150_off_bil` | 0.873 | 0.0035 | 7/8 >SPY (MDD 58% warn) | 0.823 | 0.886 | 0.298 | 0.00pp | NEAR_FAIL |
| `qld_ema200_off_bil` | 0.873 | 0.0089 | 7/8 >SPY (MDD 71% warn) | 0.850 | 0.892 | 0.243 | 0.00pp | NEAR_FAIL |
| `qld_ema250_off_bil` | 0.873 | 0.0135 | 7/8 >SPY (MDD 79% warn) | 0.731 | 0.807 | 0.208 | 0.00pp | NEAR_FAIL |

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

- **Best config:** `qld_sma50_off_bil` (MARGINAL, score 47.0)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 16
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.688 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

**T1c** — OFF-state sweep on best (LETF, period): {BIL, IEF, TLT, TMF, ZROZ, EDV} = 6 configs. Anti-curve-fit: BIL is reference; leveraged OFF (TMF) only wins if Sharpe > BIL_OFF + 0.10 AND MDD ≤ TMF_buy-hold_MDD/2.
