# 020-2026-05-06-T5a-voltarget-qld — SUMMARY

**Tier:** T5a
**Hypothesis:** Carver vol-targeted single-asset QLD with EWMAC composite forecast (16/64+64/256, FDM=1.41), σ_target=0.25 (Half-Kelly), IDM=1.0 (single-asset), position inertia 10%. Tests if continuous sizing > T3d K=2 binary signal.
**Primary citation:** [systematic_trading, ch.7-12 p.98-202]; spec §2.6 T5a
**Engine SHA:** `ad8bab2`
**Datetime UTC:** 2026-05-06T18:11:46.575136+00:00
**Configs tested:** 1

## TL;DR

Best config: **`voltarget_qld_sigma025_idm1_off_zroz`** (NEAR_FAIL, score 37.0/100). lh_56y: Sharpe 0.587 (edge vs SPY -0.095), CAGR 13.91%, MDD -55.8%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `voltarget_qld_sigma025_idm1_off_zroz` | ? | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `voltarget_qld_sigma025_idm1_off_zroz` | 0.587 | 0.567 | 0.455 | 0.611 | 13.91% | 13.20% | 9.31% | 13.90% | -55.8% | -55.8% | -55.8% | -55.8% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `voltarget_qld_sigma025_idm1_off_zroz` | nan | 0.0008 | 4/8 >SPY (MDD 55% warn) | 0.494 | 0.359 | 0.256 | 0.00pp | NEAR_FAIL |

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

- **Best config:** `voltarget_qld_sigma025_idm1_off_zroz` (NEAR_FAIL, score 37.0)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** no
- **Cumulative n_trials:** 405
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.587 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

