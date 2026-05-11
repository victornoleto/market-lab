# 019-2026-05-06-T4d-clenow-vol-gate — SUMMARY

**Tier:** T4d
**Hypothesis:** Clenow ranking + per-asset vol_21d<40% filter, top-2 of {UPRO, QLD, SOXL, UGL, TMF} (5 assets, 2010+ window because SOXL inception). Master SPY>SMA200, OFF=ZROZ. Tests if filtering high-vol assets out of pool improves selection.
**Primary citation:** [stocks_on_the_move]; [leverage_for_the_long_run, p.5-6]; spec §2.5 T4d
**Engine SHA:** `255e5d8`
**Datetime UTC:** 2026-05-08T14:14:31.815705+00:00
**Configs tested:** 1

## TL;DR

Best config: **`xs_clenow_volgate_top2_zroz_spysma200`** (NEAR_FAIL, score 39.5/100). lh_56y: Sharpe 0.511 (edge vs SPY -0.171), CAGR 10.90%, MDD -58.3%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `xs_clenow_volgate_top2_zroz_spysma200` | ? | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `xs_clenow_volgate_top2_zroz_spysma200` | 0.511 | 0.438 | 0.438 | 0.469 | 10.90% | 8.53% | 8.95% | 9.46% | -58.3% | -58.3% | -58.3% | -58.3% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `xs_clenow_volgate_top2_zroz_spysma200` | nan | 0.0033 | 4/8 >SPY (MDD 52% warn) | 0.288 | 0.214 | 0.147 | 0.00pp | NEAR_FAIL |

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

- **Best config:** `xs_clenow_volgate_top2_zroz_spysma200` (NEAR_FAIL, score 39.5)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 404
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.511 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

