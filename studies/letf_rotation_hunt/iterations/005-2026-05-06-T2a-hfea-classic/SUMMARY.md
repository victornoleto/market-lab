# 005-2026-05-06-T2a-hfea-classic — SUMMARY

**Tier:** T2a
**Hypothesis:** HFEA classic UPRO+TMF 55/45 with SMA200 on SPY: full-off (cash) and half-off (zero LETF, keep bond) variants. Tests Carlson capital-efficient stacking at the canonical HFEA weight.
**Primary citation:** [risk_parity, ch.5, p.10] (Carlson HFEA basis); [leverage_for_the_long_run, p.13] (signal asset)
**Engine SHA:** `ad8bab2`
**Datetime UTC:** 2026-05-06T18:10:34.323020+00:00
**Configs tested:** 2

## TL;DR

Best config: **`hfea_55_45_half_off`** (MARGINAL, score 44.5/100). lh_56y: Sharpe 0.571 (edge vs SPY -0.111), CAGR 14.59%, MDD -79.6%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `hfea_55_45_full_off_bil` | ? | BIL | sma | 200 |
| `hfea_55_45_half_off` | ? | BIL | sma | 200 |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `hfea_55_45_full_off_bil` | 0.559 | 0.552 | 0.625 | 0.660 | 10.20% | 9.87% | 11.08% | 12.20% | -59.2% | -59.2% | -52.2% | -52.2% |
| `hfea_55_45_half_off` | 0.571 | 0.506 | 0.483 | 0.484 | 14.59% | 11.94% | 11.78% | 11.38% | -79.6% | -79.6% | -79.6% | -79.6% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `hfea_55_45_full_off_bil` | 0.905 | 0.0013 | 4/8 >SPY (MDD 58% warn) | 0.496 | 0.306 | 0.195 | 0.00pp | NEAR_FAIL |
| `hfea_55_45_half_off` | 0.905 | 0.0009 | 6/8 >SPY (MDD 80% warn) | 0.274 | 0.040 | 0.246 | 0.00pp | MARGINAL |

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

- **Best config:** `hfea_55_45_half_off` (MARGINAL, score 44.5)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 384
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.571 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

