# 007-2026-05-06-T2c-hfea-ndx — SUMMARY

**Tier:** T2c
**Hypothesis:** HFEA-NDX TQQQ+TMF {55/45, 60/40} with SMA200 on QQQ signal, full-off cash. NDX-based HFEA basket for tech-heavy regime.
**Primary citation:** [risk_parity, ch.5]; [leverage_for_the_long_run, ch.4] (NDX LETF rotation)
**Engine SHA:** `ad8bab2`
**Datetime UTC:** 2026-05-06T18:10:40.649418+00:00
**Configs tested:** 2

## TL;DR

Best config: **`hfea_ndx_tqqq_tmf_55_45`** (MARGINAL, score 51.0/100). lh_56y: Sharpe 0.653 (edge vs SPY -0.029), CAGR 15.70%, MDD -49.4%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `hfea_ndx_tqqq_tmf_55_45` | ? | BIL | sma | 200 |
| `hfea_ndx_tqqq_tmf_60_40` | ? | BIL | sma | 200 |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `hfea_ndx_tqqq_tmf_55_45` | 0.653 | 0.696 | 0.735 | 0.921 | 15.70% | 17.37% | 16.56% | 22.85% | -49.4% | -49.4% | -49.0% | -39.0% |
| `hfea_ndx_tqqq_tmf_60_40` | 0.652 | 0.690 | 0.739 | 0.932 | 16.38% | 17.97% | 17.36% | 24.11% | -52.9% | -52.9% | -52.8% | -37.9% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `hfea_ndx_tqqq_tmf_55_45` | 0.976 | 0.0002 | 6/8 >SPY (MDD 45% warn) | 0.823 | 0.725 | 0.296 | 0.00pp | MARGINAL |
| `hfea_ndx_tqqq_tmf_60_40` | 0.976 | 0.0002 | 7/8 >SPY (MDD 48% warn) | 0.853 | 0.763 | 0.291 | 0.00pp | MARGINAL |

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

- **Best config:** `hfea_ndx_tqqq_tmf_55_45` (MARGINAL, score 51.0)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 389
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.653 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

