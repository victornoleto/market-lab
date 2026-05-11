# 006-2026-05-06-T2b-weight-sweep — SUMMARY

**Tier:** T2b
**Hypothesis:** UPRO+TMF weight sweep {60/40, 65/35, 70/30} with SMA200 SPY signal, full-off cash. Higher equity tilts trade off Sharpe for CAGR; finds optimal point on efficient frontier.
**Primary citation:** [risk_parity, ch.5, p.10]
**Engine SHA:** `255e5d8`
**Datetime UTC:** 2026-05-08T14:15:14.651681+00:00
**Configs tested:** 3

## TL;DR

Best config: **`hfea_70_30_full_off`** (NEAR_FAIL, score 34.5/100). lh_56y: Sharpe 0.583 (edge vs SPY -0.099), CAGR 11.70%, MDD -66.6%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `hfea_60_40_full_off` | ? | BIL | sma | 200 |
| `hfea_65_35_full_off` | ? | BIL | sma | 200 |
| `hfea_70_30_full_off` | ? | BIL | sma | 200 |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `hfea_60_40_full_off` | 0.572 | 0.561 | 0.653 | 0.695 | 10.75% | 10.29% | 11.91% | 13.20% | -61.7% | -61.7% | -50.5% | -50.5% |
| `hfea_65_35_full_off` | 0.580 | 0.564 | 0.671 | 0.719 | 11.25% | 10.66% | 12.67% | 14.12% | -64.2% | -64.2% | -48.8% | -48.8% |
| `hfea_70_30_full_off` | 0.583 | 0.563 | 0.680 | 0.732 | 11.70% | 10.96% | 13.37% | 14.97% | -66.6% | -66.6% | -47.2% | -47.2% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `hfea_60_40_full_off` | 0.794 | 0.0029 | 4/8 >SPY (MDD 61% warn) | 0.526 | 0.366 | 0.215 | 0.00pp | NEAR_FAIL |
| `hfea_65_35_full_off` | 0.794 | 0.0026 | 4/8 >SPY (MDD 63% warn) | 0.548 | 0.421 | 0.216 | 0.00pp | NEAR_FAIL |
| `hfea_70_30_full_off` | 0.794 | 0.0024 | 4/8 >SPY (MDD 66% warn) | 0.562 | 0.470 | 0.223 | 0.00pp | NEAR_FAIL |

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

- **Best config:** `hfea_70_30_full_off` (NEAR_FAIL, score 34.5)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 387
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.583 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

