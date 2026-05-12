# Stage 1 Candidate Validation

Status: validation report for selected Stage 1 close-only candidates. This is still research-only.

Candidates: 2
DSR n_trials: 7,554,054
Bootstrap paths: 2,000
PBO group: branch
Elapsed seconds: 4.5

## Gate Summary

| label                   | oos_pass   | fwd_pass   | wf_pass   | bootstrap_pass   | dsr_pass   | pbo_pass   | all_hard_gates_pass   |   dsr_p_value |    pbo |
|:------------------------|:-----------|:-----------|:----------|:-----------------|:-----------|:-----------|:----------------------|--------------:|-------:|
| QQQ_QLD_2x_n7k5_rank01  | True       | True       | True      | True             | False      | True       | False                 |        0.1444 | 0.2302 |
| QQQ_TQQQ_3x_n8k6_rank02 | True       | True       | True      | True             | False      | True       | False                 |        0.2260 | 0.2302 |

## Headline Metrics

| label                   | branch   | risk_on   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                                          |
|:------------------------|:---------|:----------|----:|----:|----------:|-------:|---------:|--------:|---------:|:-------------------------------------------------------------------------------------------------|
| QQQ_QLD_2x_n7k5_rank01  | QQQ      | QLD_2x    |   7 |   5 |    1.3776 | 0.3279 |   0.9954 | -0.5638 |   0.5815 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| QQQ_TQQQ_3x_n8k6_rank02 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2557 | 0.3971 |   0.9469 | -0.6558 |   0.6055 | px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0 |

## Interpretation

A candidate passes this validation only if all hard gates pass. DSR uses conservative global trial accounting from the Stage 1 exact grid `[advances_fin_ml, p.222-223]`.
Candidate-panel PBO is diagnostic over the selected top-k set; it is not a literal PBO over all evaluated configs.

## Output Tables

- `tables/candidate_metrics.csv`
- `tables/gates.csv`
- `tables/walk_forward.csv`
- `tables/bootstrap.csv`
- `tables/pbo_panel.csv`
