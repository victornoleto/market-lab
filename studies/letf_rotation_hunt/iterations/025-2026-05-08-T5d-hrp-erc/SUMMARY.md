# 025-2026-05-08-T5d-hrp-erc — SUMMARY

**Tier:** T5d
**Hypothesis:** HRP and ERC replace IDM uniform. Tests if cluster-aware weighting
(López de Prado [ch.16]) or Equal Risk Contribution improves over IDM=2.5
on the 4-LETF pool. 2x sigma_target levels (0.25, 0.30) per scheme.

**Primary citation:** [advances_fin_ml, ch.16 p.221-228]; spec §2.6 T5d (optional)
**Engine SHA:** `e7c432a`
**Datetime UTC:** 2026-05-08T14:25:50.490761+00:00
**Configs tested:** 4

## TL;DR

Best config: **`erc_multi4_sigma030`** (PROMISING, score 72.5/100). lh_56y: Sharpe 0.799 (edge vs SPY +0.117), CAGR 20.57%, MDD -48.6%.  **KILL T0:** FIRES (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `hrp_multi4_sigma025` | ? | ZROZ | ? | ? |
| `hrp_multi4_sigma030` | ? | ZROZ | ? | ? |
| `erc_multi4_sigma025` | ? | ZROZ | ? | ? |
| `erc_multi4_sigma030` | ? | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `hrp_multi4_sigma025` | 0.675 | 0.670 | 0.697 | 0.869 | 15.70% | 15.50% | 17.16% | 21.87% | -52.5% | -52.5% | -52.5% | -44.7% |
| `hrp_multi4_sigma030` | 0.677 | 0.673 | 0.708 | 0.889 | 15.89% | 15.76% | 17.68% | 22.74% | -53.5% | -51.4% | -51.4% | -44.0% |
| `erc_multi4_sigma025` | 0.796 | 0.761 | 0.740 | 0.892 | 20.15% | 18.91% | 18.74% | 23.51% | -47.6% | -47.6% | -47.6% | -47.6% |
| `erc_multi4_sigma030` | 0.799 | 0.766 | 0.749 | 0.905 | 20.57% | 19.38% | 19.25% | 24.19% | -48.6% | -47.1% | -47.1% | -47.1% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `hrp_multi4_sigma025` | 0.183 | 0.0006 | 5/8 >SPY (MDD 53% warn) | 0.757 | 0.778 | 0.318 | 0.00pp | MARGINAL |
| `hrp_multi4_sigma030` | 0.183 | 0.0006 | 6/8 >SPY (MDD 51% warn) | 0.787 | 0.819 | 0.319 | 0.00pp | MARGINAL |
| `erc_multi4_sigma025` | 0.183 | 0.0000 | 4/8 >SPY (MDD 48% warn) | 0.904 | 0.770 | 0.414 | 0.00pp | PROMISING |
| `erc_multi4_sigma030` | 0.183 | 0.0000 | 5/8 >SPY (MDD 47% warn) | 0.915 | 0.778 | 0.432 | 0.00pp | PROMISING |

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

- **Best config:** `erc_multi4_sigma030` (PROMISING, score 72.5)
- **KILL T0:** FIRES (edge < 0.05 → tag CLOSE_NO_VALUE)
- **Advance to next tier:** no
- **Cumulative n_trials:** 426
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.799 (lh_56y) sits below SPY+0.05 = 0.732 — single-LETF Gayed rotation does not produce risk-adjusted edge over passive SPY in this universe. Per spec §3.4, KILL T0 is informational: T1b/T1c continue but tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best (spec §3.4 inheritance fallback).

## Next iter

