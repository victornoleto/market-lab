# Phase 8 - Final Mandate Gate Suite on the Round Survivors (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change, regardless of outcome - even a 7/7 pass only makes a config eligible for a separate mandate SS7 decision.

User-chosen configs (2026-06-10): `spy_7a_ensemble` (7A ensemble, `spy_alt_off / narrow {150,175,200,225} / lag 2`) and `qqq_7d_quadratic` (7D quadratic vol-target, `sigma 40% / RV21 / lag 2`). Honest prior recorded in the pre-registration: QQQ at 8/11 (72.7%) was EXPECTED to fail G3; it is validated for the record.

Suite: canonical mandate SS5 wrappers (`lrs/lib/validation.run_gate_suite`), Phase 4 geometry verbatim. **DSR n_trials = 4377** (full in-repo lineage through 7F; letf-lab excluded = honest undercount). PBO matrix = winning family grid per branch (36 configs each). **+0 trials; ledger stays 4377** `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`.

**Built-in sanity (recomputed CAGR/MDD vs committed Phase 7 CSV rows):** spy_7a_ensemble: max abs diff 8.33e-17; qqq_7d_quadratic: max abs diff 2.78e-17.

## Executive Conclusion

Configs passing ALL seven gates (hard-block, zero bypass): **0/2**. Failing gates: G1 PBO<0.5 fails 1/2, G2 DSR p<.05 fails 2/2, G3 WF>=6/8 fails 1/2. No config passes all seven gates. Per the pre-registered rule, both configs are re-closed with the ledger as-is; the family returns to the shelf pending new literature or regime. No re-runs, no threshold adjustments.


## Gate Results

| Config | G1 PBO | G2 DSR p | G3 WF | G4 OOS | G5 FWD | G6 Boot | G7 xlib | Overall |
|---|---|---|---|---|---|---|---|---|
| spy_7a_ensemble | 0.397 P | 0.052 F | 13/17 P | P | P | 0.29 P | 0 P | FAIL |
| qqq_7d_quadratic | 0.651 F | 0.138 F | 8/11 F | P | P | 0.27 P | 0 P | FAIL |

## Metrics (warning-only tiers, NOT gates)

| Config | CAGR | MDD | Sharpe | Calmar | Obs SR (ann) |
|---|---|---|---|---|---|
| spy_7a_ensemble | 14.49% | -43.16% | 0.695 | 0.336 | 0.695 |
| qqq_7d_quadratic | 19.53% | -42.63% | 0.747 | 0.458 | 0.747 |

## Plots

| Plot | File |
|---|---|
| Gate pass/fail heatmap | [plots/phase08_gate_heatmap.png](plots/phase08_gate_heatmap.png) |
| Walk-forward OOS spread | [plots/phase08_wf_spread.png](plots/phase08_wf_spread.png) |

## Phase Verdict

| Question | Verdict |
|---|---|
| Configs passing all 7 gates? | 0/2. |
| Failing gates? | G1 PBO<0.5 fails 1/2, G2 DSR p<.05 fails 2/2, G3 WF>=6/8 fails 1/2. |
| Did we promote anything? | No - even a pass is research-only pending mandate SS7. |
| Is this deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |

No config passes all seven gates. Per the pre-registered rule, both configs are re-closed with the ledger as-is; the family returns to the shelf pending new literature or regime. No re-runs, no threshold adjustments.
