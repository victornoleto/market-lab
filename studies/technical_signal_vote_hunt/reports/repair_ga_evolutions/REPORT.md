# Repair GA Evolutions

Status: sequential GA repair suite after the QLD-vs-QQQ signal audit.

## Completed Evolutions

| name                         | objective              |   seed |   evaluated_unique |   generations |   elapsed_minutes | best_label                                                             |   best_fitness |   best_sortino |   best_cagr |   best_mdd |   best_calmar |
|:-----------------------------|:-----------------------|-------:|-------------------:|--------------:|------------------:|:-----------------------------------------------------------------------|---------------:|---------------:|------------:|-----------:|--------------:|
| evo01_qqq_mdd_repair         | qqq_mdd_repair         |   1071 |              19213 |           120 |          166.7598 | QQQ_s75_180_vw10_vt0.25_ar20_k4_T30D45_w1.00_lrs1.20_g0.50_rv60_0.70   |         5.4175 |         1.4013 |      0.3081 |    -0.3353 |        0.9189 |
| evo02_qqq_rolling_repair     | qqq_rolling_repair     |   2071 |              16209 |           120 |          139.5689 | QQQ_s50_225_vw42_vt0.25_ar30_k3_T20D60_w1.00_lrs1.00_g0.50_rv60_0.70   |         5.5498 |         1.3459 |      0.3244 |    -0.3997 |        0.8117 |
| evo03_qqq_conservative_turbo | qqq_conservative_turbo |   3071 |              13409 |           120 |          115.6525 | QQQ_s75_180_vw10_vt0.25_ar20_k4_T25D45_w0.50_lrs1.00_g0.10_rv60_0.60   |         4.5259 |         1.4046 |      0.2713 |    -0.3200 |        0.8478 |
| evo04_qld_simplify           | qld_simplify           |   1071 |               7234 |            38 |           22.8845 | QLD_s100_200_vw21_vt0.50_ar30_k2_T15D120_w1.00_lrs1.10_g0.50_rv90_0.80 |         5.5447 |         1.3751 |      0.4342 |    -0.5273 |        0.8233 |
| evo05_execution_robust       | execution_robust       |   2071 |               6531 |            31 |           45.6450 | QLD_s100_225_vw21_vt0.50_ar40_k2_T15D120_w1.00_lrs1.00_g0.25_rv90_0.80 |         6.2739 |         1.2423 |      0.3794 |    -0.5680 |        0.6933 |
| evo06_diversity_search       | diversity_search       |   1071 |               6027 |            31 |           13.3967 | QLD_s50_200_vw42_vt0.50_ar20_k3_T10D45_w1.00_lrs1.20_g0.25_rv90_0.90   |         4.9523 |         1.3329 |      0.4014 |    -0.5032 |        0.7977 |

## Interpretation

All 6 planned GA evolutions completed. The suite evaluated at least `82,623` unique candidates across the six runs, counting only final manifests and not smoke/checkpoint attempts.

The most important result is that the GA **did repair the QQQ-signal family**. The original direct QQQ-signal transplant had MDD around `-91%` to `-94%`; the best QQQ-signal repair candidates now land around `-32%` to `-40%` MDD while keeping CAGR `27%` to `32%`. That confirms the QQQ-underlying path is not dead, but it gives up meaningful CAGR versus the QLD-self-signal family.

The strongest raw economic candidate is `evo04_qld_simplify`:

- `QLD_s100_200_vw21_vt0.50_ar30_k2_T15D120_w1.00_lrs1.10_g0.50_rv90_0.80`
- Sortino `1.3751`, CAGR `43.42%`, MDD `-52.73%`, Calmar `0.8233`

This beats `T20D90` economically in-sample, but it is clearly another QLD-self-signal optimized variant and must be treated as discovery-only until a validation pass is run with cumulative trial accounting `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

The most useful QQQ-signal candidates are:

- `evo01` best: Sortino `1.4013`, CAGR `30.81%`, MDD `-33.53%`.
- `evo02` best: Sortino `1.3459`, CAGR `32.44%`, MDD `-39.97%`, better rolling objective.
- `evo03` best: Sortino `1.4046`, CAGR `27.13%`, MDD `-32.00%`, conservative turbo.

These are lower-CAGR but conceptually cleaner than the QLD-self-signal candidates because the signal asset is `QQQ`, closer to the Gayed underlying-index framing `[leverage_for_the_long_run, p.13]`.

## Current Ranking After GA Discovery

| Rank | Candidate | Role | Read |
|---:|---|---|---|
| 1 | `evo04_qld_simplify` best | Highest economic in-sample | New QLD-self-signal challenger; needs validation. |
| 2 | `T20D90` prior incumbent | Best pre-GA balanced anchor | Still cleaner than evo04 because already audited in long-term review, but now economically displaced in-sample. |
| 3 | `evo05_execution_robust` best | Lag-robust QLD variant | Lower CAGR/Sortino than evo04, but selected under lag stress. |
| 4 | `evo06_diversity_search` best | Alternative QLD variant | Good economics, but still high family similarity; diversity objective did not find a clearly independent winner. |
| 5 | `evo01/evo02/evo03` QQQ-signal leads | Clean-underlying repair | Conceptually important; lower CAGR than QLD-self-signal, much better MDD than the naive QQQ-signal transplant. |

## Next Required Step

Do not promote any GA candidate yet. The correct next step is a validation panel over a small, pre-registered set:

- `T20D90`
- `T20D120`
- `evo04` best
- `evo05` best
- `evo06` best
- best QQQ-signal lead from each of `evo01`, `evo02`, `evo03`

The validation must include OOS/FWD/WF/bootstrap/PBO/DSR with cumulative trials from these GA runs. Until then, this suite is discovery evidence only `[advances_fin_ml, p.222-223]`.
