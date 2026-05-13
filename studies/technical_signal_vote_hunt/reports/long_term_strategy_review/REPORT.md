# Long-Term Strategy Review

Status: consolidated active review of `technical_signal_vote_hunt` after reproducing the final T/D sensitivity report and auditing the validation tables.

## Verdict

The best long-term reference strategy in this study is still **iter030 canonical QLD/ZROZ LRS1.20**. It is not deploy-authorized under the project mandate, but it is the strongest robust long-history anchor after comparing known strategies, modern technical-vote leads, Stage4 hybrids and local iter030 parameter sensitivities.

For an economic-first research view, **T20D90** is the best balanced local challenger and **T20D120** is the best terminal-equity challenger. Both remain research-only: the family still fails DSR/PBO after cumulative trial accounting `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

## Active Checks Performed

1. Re-ran the final T/D comparison runner:

```bash
uv run python -m studies.technical_signal_vote_hunt.runners.run_iter030_td_sensitivity
```

2. Audited the main generated tables:

- `reports/iter030_td_sensitivity/tables/comparison_metrics.csv`
- `reports/iter030_td_sensitivity/tables/comparison_rolling_windows.csv`
- `reports/iter030_param_ga/validation/tables/gates.csv`
- `reports/stage2_tiingo_validation/*/tables/candidate_metrics.csv`

3. Ran a direct hard-gate check for `T20D90`, because it is the best Sortino candidate in the constrained T/D grid but was not explicitly selected in the prior strict-Pareto GA validation report.

## Ranking

| Rank | Strategy | Role | Long-term status | Key reason |
|---:|---|---|---|---|
| 1 | `iter030 canonical QLD/ZROZ LRS1.20` | Core anchor | Best long-term reference | Strong long-history return with better drawdown than T3d-K2 and no successful strict-Pareto replacement. |
| 2 | `iter030 T20D90` | Balanced local challenger | Research-only | Best Sortino in the T/D grid; passes OOS/FWD/WF/bootstrap but fails DSR and inherits failed PBO panel. |
| 3 | `iter030 T20D120` | Performance-first local challenger | Research-only | Highest CAGR/terminal equity in the T/D grid; formally validated and failed DSR/PBO. |
| 4 | `T3d-K2 canonical QLD/ZROZ` | Older robust anchor | Preserved reference | Higher Sortino than iter030 in the comparison table, but lower CAGR and worse MDD. |
| 5 | `Stage3 shared QLD/TQQQ` | Long-history technical-vote clue | Not a winner | Strong in-sample Sortino/CAGR, but Stage 3 validation closed 0/400 pass with PBO near 1. |
| 6 | `Stage4 QLD/TQQQ base vote` | Modern-regime monitor | Not a long-history anchor | Excellent Tiingo 2010+ behavior, but weakens materially in the 1986+ testfolio stress. |

## Headline Metrics

Window for the main long-history comparison: `1986-01-03..2026-04-17`.

| Strategy | Sortino | CAGR | Sharpe | MDD | Calmar | End multiple |
|---|---:|---:|---:|---:|---:|---:|
| Stage3 shared QLD | 1.3747 | 32.05% | 0.9826 | -57.81% | 0.5543 | 72,857x |
| Stage3 shared TQQQ | 1.2680 | 40.26% | 0.9510 | -64.24% | 0.6267 | 828,856x |
| T3d-K2 canonical | 1.2575 | 31.06% | 0.9187 | -64.50% | 0.4816 | 53,861x |
| iter030 T20D90 | 1.2278 | 38.99% | 0.9752 | -55.48% | 0.7029 | 574,998x |
| iter030 T20D120 | 1.2074 | 39.01% | 0.9606 | -55.48% | 0.7032 | 577,835x |
| iter030 canonical | 1.2073 | 36.66% | 0.9624 | -55.48% | 0.6608 | 290,557x |
| Stage4-inside iter030 turbo | 1.0838 | 38.46% | 0.8721 | -64.54% | 0.5959 | 492,025x |
| Stage4 QLD base vote | 0.9074 | 19.38% | 0.6685 | -70.07% | 0.2766 | 1,256x |
| Stage4 TQQQ base vote | 0.8328 | 21.48% | 0.6374 | -87.69% | 0.2449 | 2,532x |

The Stage3 shared QLD/TQQQ rows rank highly by raw Sortino/CAGR, but they are not better long-term choices because their validation failure is severe: Stage 3 closed 0/400 pass with PBO `0.9881` for QLD and `0.9643` for TQQQ.

## Rolling-Window Stress

Minimum rolling CAGR by window length:

| Strategy | 3y min | 5y min | 10y min | 15y min |
|---|---:|---:|---:|---:|
| iter030 canonical | -15.27% | 1.48% | 8.76% | 16.89% |
| iter030 T20D120 | -16.58% | 1.94% | 10.18% | 18.59% |
| T3d-K2 canonical | -15.52% | -0.89% | 5.41% | 14.95% |
| Stage3 shared QLD | -2.90% | 5.04% | 14.00% | 17.33% |
| Stage3 shared TQQQ | -7.66% | 7.34% | 19.74% | 21.15% |
| Stage4 QLD base vote | -23.22% | -7.72% | -0.96% | 6.66% |
| Stage4 TQQQ base vote | -41.46% | -17.57% | -8.30% | 3.69% |

Rolling windows alone would make Stage3 look attractive. The reason it does not win is validation, not temporal headline behavior. Dense technical-vote neighborhoods repeatedly produced high PBO and weak DSR once the search budget was accounted for `[advances_fin_ml, p.222-223]`.

## Validation Evidence

### Iter030 Parameter Family

The formal validation of the strict-Pareto iter030 parameter candidates used `n_trials=136,784,569`, 2,000 bootstrap paths and a 195-gene PBO panel. It closed 0/7 pass:

| Strategy | OOS | FWD | WF | Bootstrap | DSR p | PBO | All hard gates |
|---|---|---|---|---|---:|---:|---|
| iter030 baseline | pass | pass | pass | pass | 0.3663 | 0.6190 | fail |
| T20D120 GA candidate | pass | pass | pass | pass | 0.3705 | 0.6190 | fail |

Manual `T20D90` check, using the same `n_trials=136,784,569` and the same PBO-panel interpretation:

| Strategy | OOS | FWD | WF | Bootstrap | DSR p | PBO panel | All hard gates |
|---|---|---|---|---|---:|---:|---|
| T20D90 | pass | pass | 8/8 pass | pass | 0.3364 | 0.6190 | fail |

This supports `T20D90` as an economic sensitivity, not as a promotion candidate.

### Stage2 Modern Tiingo Leads

The best modern Tiingo operational leads are strong but not robust enough:

| Strategy | Sortino | CAGR | MDD | Validation result |
|---|---:|---:|---:|---|
| QQQ->QLD `CASH_USD lag1` | 1.4209 | 36.26% | -37.54% | 0/200 pass; DSR/PBO fail |
| QQQ->TQQQ `CASH_USD lag1` | 1.4124 | 53.00% | -51.03% | 0/200 pass; DSR/PBO fail |

These are credible **modern-regime challengers**, but the testfolio 1986+ reproduction shows they do not displace iter030/T3d-K2 across older crash regimes.

## Decision Logic

The final choice depends on which constraints matter:

| Objective | Best choice | Reason |
|---|---|---|
| Long-term robustness under unknown regimes | iter030 canonical | Best combination of long-history strength, lower MDD than T3d-K2, and resistance to replacement by Stage4 hybrid searches. |
| Highest local economic score inside the iter030 family | T20D90 | Best Sortino in the constrained T/D grid with nearly the same CAGR as T20D120. |
| Highest terminal wealth in the local T/D grid | T20D120 | Highest CAGR and end multiple, but slightly worse balanced profile than T20D90. |
| Modern 2010+ aggressive performance | Stage4 TQQQ base vote | Very strong Tiingo 2010+, but unacceptable as long-history anchor due to 1986+ degradation. |

## Final Recommendation

Use **iter030 canonical QLD/ZROZ LRS1.20** as the study's best long-term strategy reference.

Keep **T20D90** and **T20D120** as named research sensitivities:

- `T20D90`: best balanced local variant.
- `T20D120`: best performance-first local variant.

Do not promote either variant unless a future pre-registered validation panel solves the DSR/PBO problem. Under the current mandate, no strategy in this study authorizes capital allocation.

## Why Not Run More Search Now

More unconstrained GA/grid work in this folder is unlikely to change the answer. The repeated failure mode is already clear: similar technical-vote candidates cluster tightly, pass temporal checks, and then fail PBO/DSR after accumulated trial accounting. A new search would need a genuinely new hypothesis, such as ex-ante regime segmentation or panel-diversity constraints, not another local sweep `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
