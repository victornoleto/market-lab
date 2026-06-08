# Phase 4 - Mandate Validation Gates (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome.

Per `lrs/NEXT_STEPS.md`, Phase 4 is a diagnostic to decide whether the family deserves to continue - not a promotion. It runs the canonical mandate §5 gate suite on the 6 SMA200 bases (3 SPY + 3 QQQ, each at its best-score lag), wrapping `market_lab.backtest.validation`. CAGR/MDD remain warning-only tiers, not gates `[advances_fin_ml, p.208-211]`.

DSR `n_trials = 3876` (direct lineage: Phase 2 2400 + 3A 324 + 3A-2 216 + 3C 936). The spun-off `studies/lrs/`/`letf-lab` sweeps are excluded (separate repo), so the truly-honest count is higher; 3876 is the defensible in-repo figure `[advances_fin_ml, p.273-275]`. PBO trial matrix = the Phase 2 geometry grid at SMA200 (8 leverages x 5 risk-off x 5 vol = 200 configs/branch, fixed lag).

## Executive Conclusion

Bases passing ALL seven gates (hard-block, zero bypass): **0/6**. Binding gates: G3 WF>=6/8 fails 6/6, G1 PBO<0.5 fails 3/6, G2 DSR p<.05 fails 3/6, G4 OOS fails 1/6. Gate definitions: G1 PBO<0.5; G2 DSR p<0.05; G3 walk-forward >=6/8 OOS windows beat underlying (per-window MDD diagnostic, no cap); G4 single-block OOS (last 30%) Sharpe>0 and beats underlying; G5 FWD stress (post-2020) Sharpe>0; G6 stationary-bootstrap 99.9% CI low of annualized Sharpe >0; G7 cross-lib CAGR |delta|<=3pp `[advances_fin_ml, p.208-211, p.273-275]`, `[testing_tuning, p.318-320, p.327-335]`.

## Source And Rules

| Item | Value |
|---|---|
| Data | `data/testfolio/cache/history.parquet` (close-only equity curves) |
| Strategy | SMA200 LRS base (signal = SMA200 & vol_gate), after-tax weekly |
| DSR n_trials | 3876 (direct lineage) |
| PBO matrix | Phase 2 geometry grid @ SMA200, lag 0, ~200 configs/branch |
| Walk-forward | is=1764d / oos=756d / step=756d, >=8 windows, >=6/8 beat underlying |
| Bootstrap | stationary block, 99.9% CI, block 21, 5000 resamples |
| Verdict | G1 AND G2 AND ... AND G7 (hard-block) |


## Plots

| Plot | File |
|---|---|
| Gate pass/fail heatmap | [plots/phase04_gate_heatmap.png](plots/phase04_gate_heatmap.png) |
| Walk-forward OOS spread (headliners) | [plots/phase04_wf_spread.png](plots/phase04_wf_spread.png) |

## Gate Results (per base)

| Branch | Base | G1 PBO | G2 DSR p | G3 WF | G4 OOS | G5 FWD | G6 Boot | G7 xlib | Overall |
|---|---|---|---|---|---|---|---|---|---|
| SPY | spy_top | 0.016 P | 0.034 P | 12/17 F | P | P | 0.32 P | 0 P | FAIL |
| SPY | spy_lower_lev | 0.016 P | 0.024 P | 10/17 F | F | P | 0.34 P | 0 P | FAIL |
| SPY | spy_alt_off | 0.016 P | 0.029 P | 12/17 F | P | P | 0.34 P | 0 P | FAIL |
| QQQ | qqq_top | 0.643 F | 0.164 F | 6/11 F | P | P | 0.30 P | 0 P | FAIL |
| QQQ | qqq_lower_lev | 0.643 F | 0.145 F | 4/11 F | P | P | 0.31 P | 0 P | FAIL |
| QQQ | qqq_alt_vol | 0.643 F | 0.164 F | 7/11 F | P | P | 0.28 P | 0 P | FAIL |

## Metrics (warning-only tiers, NOT gates)

| Branch | Base | L | Lag | CAGR | MDD | Sharpe | Calmar | Obs SR (daily-ann) |
|---|---|---|---|---|---|---|---|---|
| SPY | spy_top | 2.00 | 3 | 15.44% | -39.28% | 0.718 | 0.393 | 0.718 |
| SPY | spy_lower_lev | 1.75 | 3 | 14.60% | -37.38% | 0.737 | 0.391 | 0.737 |
| SPY | spy_alt_off | 2.00 | 3 | 15.72% | -40.19% | 0.728 | 0.391 | 0.728 |
| QQQ | qqq_top | 1.75 | 0 | 19.46% | -42.58% | 0.725 | 0.457 | 0.725 |
| QQQ | qqq_lower_lev | 1.50 | 0 | 17.96% | -40.63% | 0.738 | 0.442 | 0.738 |
| QQQ | qqq_alt_vol | 1.75 | 0 | 18.32% | -42.80% | 0.725 | 0.428 | 0.725 |

## Phase Verdict

| Question | Verdict |
|---|---|
| Bases passing all 7 gates? | 0/6. |
| Binding (most-failed) gates? | G3 WF>=6/8 fails 6/6, G1 PBO<0.5 fails 3/6, G2 DSR p<.05 fails 3/6, G4 OOS fails 1/6. |
| Did we promote anything? | No - diagnostic only. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |

No base passes all seven gates - the LRS family does NOT clear the mandate validation gates. Consistent with the restart's prior (geometry is the driver; 3C fragility; the repo's 113/113 honest-FAIL history), record the family as a research-only, negative-leaning line and close/shelve it pending new literature or regime. No mandate change. `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`, `[leverage_for_the_long_run, p.4-7]`.
