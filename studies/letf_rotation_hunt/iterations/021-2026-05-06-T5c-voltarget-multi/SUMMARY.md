# 021-2026-05-06-T5c-voltarget-multi — SUMMARY

**Tier:** T5c
**Hypothesis:** Carver vol-targeted multi-asset {UPRO, QLD, UGL, TMF}. EWMAC composite per asset. IDM=2.5 (max per Carver [p.170-171]). σ_target=0.25. Tests if multi-asset diversification (Carver ch.10-11) lifts Sharpe vs single-asset T5a.
**Primary citation:** [systematic_trading, ch.10-11]; spec §2.6 T5c
**Engine SHA:** `ad8bab2`
**Datetime UTC:** 2026-05-06T18:11:52.551302+00:00
**Configs tested:** 1

## TL;DR

Best config: **`voltarget_multi4_sigma025_idm25_off_zroz`** (PROMISING, score 68.5/100). lh_56y: Sharpe 0.740 (edge vs SPY +0.058), CAGR 19.39%, MDD -62.9%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `voltarget_multi4_sigma025_idm25_off_zroz` | ? | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `voltarget_multi4_sigma025_idm25_off_zroz` | 0.740 | 0.744 | 0.725 | 0.914 | 19.39% | 19.54% | 18.77% | 24.40% | -62.9% | -48.2% | -47.4% | -46.3% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `voltarget_multi4_sigma025_idm25_off_zroz` | nan | 0.0000 | 6/8 >SPY (MDD 47% warn) | 0.807 | 0.906 | 0.386 | 0.00pp | PROMISING |

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

- **Best config:** `voltarget_multi4_sigma025_idm25_off_zroz` (PROMISING, score 68.5)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** no
- **Cumulative n_trials:** 406
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.740 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

