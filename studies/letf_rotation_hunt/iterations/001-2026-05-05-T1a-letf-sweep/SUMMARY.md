# 001-2026-05-05-T1a-letf-sweep — SUMMARY

**Tier:** T1a
**Hypothesis:** Gayed canonical SMA200 LRS reproducible em SSO/UPRO/QLD/TQQQ/SOXL/UGL — single LETF rotation com BIL como OFF-state.
**Primary citation:** [leverage_for_the_long_run, p.13, p.17 Table 8]
**Engine SHA:** `ad8bab2`
**Datetime UTC:** 2026-05-06T18:10:18.834664+00:00
**Configs tested:** 6

## TL;DR

Best config: **`qld_sma200_off_bil`** (MARGINAL, score 48.5/100). lh_56y: Sharpe 0.678 (edge vs SPY -0.004), CAGR 18.63%, MDD -75.6%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `sso_sma200_off_bil` | SSO | BIL | sma | 200 |
| `upro_sma200_off_bil` | UPRO | BIL | sma | 200 |
| `qld_sma200_off_bil` | QLD | BIL | sma | 200 |
| `tqqq_sma200_off_bil` | TQQQ | BIL | sma | 200 |
| `soxl_sma200_off_bil` | SOXL | BIL | sma | 200 |
| `ugl_sma200_off_bil` | UGL | BIL | sma | 200 |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|
| `sso_sma200_off_bil` | 0.636 | 0.645 | 0.710 | 12.50% | 12.39% | 14.30% | -43.4% | -42.2% | -42.2% |
| `upro_sma200_off_bil` | 0.550 | 0.635 | 0.689 | 13.28% | 16.14% | 18.40% | -79.2% | -60.2% | -60.2% |
| `qld_sma200_off_bil` | 0.678 | 0.816 | 0.904 | 18.63% | 21.78% | 25.24% | -75.6% | -44.5% | -44.5% |
| `tqqq_sma200_off_bil` | 0.594 | 0.645 | 0.829 | 18.35% | 20.09% | 30.07% | -80.6% | -76.7% | -54.5% |
| `soxl_sma200_off_bil` | 0.627 | 0.680 | 0.809 | 21.09% | 22.97% | 30.46% | -94.3% | -63.3% | -57.7% |
| `ugl_sma200_off_bil` | 0.335 | 0.535 | 0.557 | 5.47% | 12.30% | 11.87% | -72.2% | -57.2% | -57.2% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `sso_sma200_off_bil` | 0.560 | 0.0035 | 4/8 >SPY (MDD 43% warn) | 0.590 | 0.629 | 0.291 | 0.00pp | NEAR_FAIL |
| `upro_sma200_off_bil` | 0.560 | 0.0153 | 5/8 >SPY (MDD 79% warn) | 0.554 | 0.636 | 0.185 | 0.00pp | NEAR_FAIL |
| `qld_sma200_off_bil` | 0.560 | 0.0015 | 7/8 >SPY (MDD 76% warn) | 0.947 | 0.936 | 0.296 | 0.00pp | MARGINAL |
| `tqqq_sma200_off_bil` | 0.560 | 0.0072 | 6/8 >SPY (MDD 70% warn) | 0.877 | 0.864 | 0.209 | 0.00pp | NEAR_FAIL |
| `soxl_sma200_off_bil` | 0.560 | 0.0039 | 7/8 >SPY (MDD 94% warn) | 0.842 | 0.948 | 0.276 | 0.00pp | NEAR_FAIL |
| `ugl_sma200_off_bil` | 0.560 | 0.2050 | 1/8 >SPY (MDD 49% warn) | 0.526 | 0.808 | -0.053 | 0.00pp | NEAR_FAIL |

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

- **Best config:** `qld_sma200_off_bil` (MARGINAL, score 48.5)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 6
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.678 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

**T1b** — period sweep on best LETF (`QLD`): {SMA, EMA} × {50, 100, 150, 200, 250} = 10 configs. Anti-curve-fit: SMA200 is reference; alt period only "wins" if Sharpe > SMA200 + 0.05.
