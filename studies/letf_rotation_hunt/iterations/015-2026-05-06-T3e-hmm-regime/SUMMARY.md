# 015-2026-05-06-T3e-hmm-regime — SUMMARY

**Tier:** T3e
**Hypothesis:** HMM 2-state regime classifier (bull/bear) on QLD underlying returns; gate ON in bull state. Sticky 3-day transition prevents whipsaw. Optional sub-fase per spec §2.4.
**Primary citation:** [knowledge/indicators/regime_hmm]; [ml_for_algo_trading, ch.9]
**Engine SHA:** `ad8bab2`
**Datetime UTC:** 2026-05-06T18:11:02.979822+00:00
**Configs tested:** 1

## TL;DR

Best config: **`qld_hmm2_sticky3_off_zroz`** (MARGINAL, score 44.5/100). lh_56y: Sharpe 0.559 (edge vs SPY -0.123), CAGR 16.66%, MDD -98.7%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `qld_hmm2_sticky3_off_zroz` | QLD | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `qld_hmm2_sticky3_off_zroz` | 0.559 | 0.522 | 0.743 | 0.915 | 16.66% | 14.48% | 24.08% | 32.05% | -98.7% | -98.7% | -80.2% | -63.5% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `qld_hmm2_sticky3_off_zroz` | nan | 0.0012 | 3/8 >SPY (MDD 99% warn) | 0.847 | 0.814 | 0.215 | 0.00pp | MARGINAL |

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

- **Best config:** `qld_hmm2_sticky3_off_zroz` (MARGINAL, score 44.5)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 400
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.559 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

