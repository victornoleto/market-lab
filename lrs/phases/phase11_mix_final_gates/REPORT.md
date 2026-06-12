# Phase 11 - Final Gates for `mix_lrs_spy_headline_20` (DIAGNOSTIC)

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading, capital allocation, or a mandate change. Maintenance mode remains unchanged.

Candidate: `mix_lrs_spy_headline_20` = 80% Phase 6A after-tax RSC leg + 20% `lrs_spy_headline` after-tax satellite, using Phase 6A's two-account contribution-funded convention. Benchmark: `bench_rsc`.

Pre-registered suite: canonical mandate SS5 wrappers (`lrs.lib.validation.run_gate_suite`), **DSR n_trials = 4569**, **+0 new trials**, PBO matrix = all Phase 6A mixes (**18 configs**, 6635 common observations), WF = 5y IS / 2y OOS / 2y step to keep >=8 OOS windows on the 2000+ RSC window `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`.

## Executive Conclusion

Configs passing ALL seven gates: **0/1**. Failing gates: G1 PBO<0.5, G2 DSR p<.05, G3 WF>=75%. The candidate fails the pre-registered hard-block suite. Per the rule, no threshold changes, no re-runs and no promotion.


## Gate Results

| Config | G1 PBO | G2 DSR p | G3 WF | G4 OOS | G5 FWD | G6 Boot | G7 xlib | Overall |
|---|---|---|---|---|---|---|---|---|
| mix_lrs_spy_headline_20 | 0.933 F | 0.306 F | 6/10 F | P | P | 0.19 P | 2.2e-14 P | FAIL |

## Metrics (warning-only tiers, NOT gates)

| Series | CAGR | MDD | Sharpe | Calmar |
|---|---|---|---|---|
| mix_lrs_spy_headline_20 | 12.12% | -25.18% | 0.815 | 0.481 |
| bench_rsc | 11.74% | -30.76% | 0.789 | 0.382 |
| Spread vs RSC | 0.38% | 5.58% |  | 0.100 |

## Diagnostics

| Diagnostic | Value |
|---|---|
| DSR stress incl. RSC evolution raw trials | n=100170, p=0.582, FAIL |
| WF canonical 7y/3y low-power check | 5/6, FAIL |
| Phase 6A CSV sanity | max abs diff 8.33e-17 |

## PBO Family

The PBO matrix uses every Phase 6A mix row, not a narrowed post-result grid: `mix_lrs_qqq_voltarget_05, mix_lrs_qqq_voltarget_10, mix_lrs_qqq_voltarget_15, mix_lrs_qqq_voltarget_20, mix_lrs_qqq_voltarget_25, mix_lrs_qqq_voltarget_30, mix_lrs_spy_headline_05, mix_lrs_spy_headline_10, mix_lrs_spy_headline_15, mix_lrs_spy_headline_20, mix_lrs_spy_headline_25, mix_lrs_spy_headline_30, mix_t3d_k2_saved_05, mix_t3d_k2_saved_10, mix_t3d_k2_saved_15, mix_t3d_k2_saved_20, mix_t3d_k2_saved_25, mix_t3d_k2_saved_30`.


## Plots

| Plot | File |
|---|---|
| Gate pass/fail heatmap | [plots/phase11_gate_heatmap.png](plots/phase11_gate_heatmap.png) |
| Walk-forward OOS spread | [plots/phase11_wf_spread.png](plots/phase11_wf_spread.png) |
| Relative equity vs RSC | [plots/phase11_relative_equity.png](plots/phase11_relative_equity.png) |

## Phase Verdict

| Question | Verdict |
|---|---|
| Candidate passes all 7 gates? | No. |
| Failing gates? | G1 PBO<0.5, G2 DSR p<.05, G3 WF>=75%. |
| Did we promote anything? | No. This is research-only and mandate §1 remains unchanged. |
| Is this deployment-ready? | No. No deploy, no paper trade, no capital movement. |

The candidate fails the pre-registered hard-block suite. Per the rule, no threshold changes, no re-runs and no promotion.
