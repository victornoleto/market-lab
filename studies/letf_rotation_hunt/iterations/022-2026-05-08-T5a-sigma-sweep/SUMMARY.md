# 022-2026-05-08-T5a-sigma-sweep — SUMMARY

**Tier:** T5a
**Hypothesis:** Sweep sigma_target over {0.15, 0.20, 0.25, 0.30, 0.35} on T5a single-asset
QLD vol-target. 0.25 = Half-Kelly Carver baseline [systematic_trading, ch.10 p.198].
Tests if T5a Sharpe 0.587 was driven by sigma choice or by structural
under-allocation (per TIER_5_REPORT §3).

**Primary citation:** [systematic_trading, ch.10 p.198]; spec §2.6 T5a; T5-expansion §3.1
**Engine SHA:** `c0e1285`
**Datetime UTC:** 2026-05-08T13:45:27.562949+00:00
**Configs tested:** 5

## TL;DR

Best config: **`voltarget_qld_sigma035`** (NEAR_FAIL, score 38.5/100). lh_56y: Sharpe 0.598 (edge vs SPY -0.084), CAGR 15.08%, MDD -56.7%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `voltarget_qld_sigma015` | ? | ZROZ | ? | ? |
| `voltarget_qld_sigma020` | ? | ZROZ | ? | ? |
| `voltarget_qld_sigma025` | ? | ZROZ | ? | ? |
| `voltarget_qld_sigma030` | ? | ZROZ | ? | ? |
| `voltarget_qld_sigma035` | ? | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `voltarget_qld_sigma015` | 0.574 | 0.555 | 0.435 | 0.595 | 12.17% | 11.49% | 8.22% | 12.33% | -54.3% | -54.3% | -54.3% | -54.3% |
| `voltarget_qld_sigma020` | 0.582 | 0.559 | 0.443 | 0.600 | 13.16% | 12.35% | 8.73% | 13.14% | -54.8% | -54.8% | -54.8% | -54.8% |
| `voltarget_qld_sigma025` | 0.587 | 0.567 | 0.455 | 0.611 | 13.91% | 13.20% | 9.31% | 13.90% | -55.8% | -55.8% | -55.8% | -55.8% |
| `voltarget_qld_sigma030` | 0.596 | 0.581 | 0.471 | 0.635 | 14.66% | 14.10% | 9.95% | 14.98% | -56.5% | -56.5% | -56.5% | -56.5% |
| `voltarget_qld_sigma035` | 0.598 | 0.589 | 0.492 | 0.657 | 15.08% | 14.69% | 10.77% | 16.00% | -56.7% | -56.7% | -56.7% | -56.7% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `voltarget_qld_sigma015` | 0.810 | 0.0081 | 4/8 >SPY (MDD 53% warn) | 0.444 | 0.294 | 0.243 | 0.00pp | NEAR_FAIL |
| `voltarget_qld_sigma020` | 0.810 | 0.0072 | 4/8 >SPY (MDD 54% warn) | 0.461 | 0.316 | 0.245 | 0.00pp | NEAR_FAIL |
| `voltarget_qld_sigma025` | 0.810 | 0.0066 | 4/8 >SPY (MDD 55% warn) | 0.494 | 0.359 | 0.256 | 0.00pp | NEAR_FAIL |
| `voltarget_qld_sigma030` | 0.810 | 0.0057 | 5/8 >SPY (MDD 56% warn) | 0.529 | 0.403 | 0.269 | 0.00pp | MARGINAL |
| `voltarget_qld_sigma035` | 0.810 | 0.0055 | 5/8 >SPY (MDD 56% warn) | 0.568 | 0.451 | 0.273 | 0.00pp | NEAR_FAIL |

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

- **Best config:** `voltarget_qld_sigma035` (NEAR_FAIL, score 38.5)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** no
- **Cumulative n_trials:** 411
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.598 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

