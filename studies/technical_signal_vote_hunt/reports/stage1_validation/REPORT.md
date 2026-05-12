# Stage 1 Candidate Validation

Status: validation report for selected Stage 1 close-only candidates. This is still research-only.

Candidates: 12
DSR n_trials: 5,471,268
Bootstrap paths: 2,000
Elapsed seconds: 7.2

## Gate Summary

| label                   | oos_pass   | fwd_pass   | wf_pass   | bootstrap_pass   | dsr_pass   | pbo_pass   | all_hard_gates_pass   |   dsr_p_value |    pbo |
|:------------------------|:-----------|:-----------|:----------|:-----------------|:-----------|:-----------|:----------------------|--------------:|-------:|
| QQQ_QLD_2x_n5k4_rank01  | True       | True       | True      | True             | False      | False      | False                 |        0.1905 | 0.9921 |
| QQQ_QLD_2x_n5k4_rank02  | True       | True       | True      | True             | False      | False      | False                 |        0.1931 | 0.9921 |
| QQQ_QLD_2x_n5k4_rank03  | True       | True       | True      | True             | False      | False      | False                 |        0.1890 | 0.9921 |
| QQQ_TQQQ_3x_n5k4_rank04 | True       | True       | True      | True             | False      | False      | False                 |        0.2475 | 0.9762 |
| QQQ_TQQQ_3x_n5k4_rank05 | True       | True       | True      | True             | False      | False      | False                 |        0.2618 | 0.9762 |
| QQQ_TQQQ_3x_n5k4_rank06 | True       | True       | True      | True             | False      | False      | False                 |        0.2651 | 0.9762 |
| SPY_SSO_2x_n5k3_rank07  | True       | True       | True      | True             | False      | False      | False                 |        0.2842 | 0.8095 |
| SPY_SSO_2x_n3k2_rank08  | True       | True       | True      | True             | False      | False      | False                 |        0.3128 | 0.8095 |
| SPY_SSO_2x_n4k3_rank09  | True       | True       | True      | True             | False      | False      | False                 |        0.3186 | 0.8095 |
| SPY_UPRO_3x_n5k3_rank10 | True       | True       | True      | True             | False      | False      | False                 |        0.4376 | 0.8968 |
| SPY_UPRO_3x_n3k2_rank11 | True       | True       | True      | True             | False      | False      | False                 |        0.4559 | 0.8968 |
| SPY_UPRO_3x_n4k3_rank12 | True       | True       | True      | True             | False      | False      | False                 |        0.4631 | 0.8968 |

## Headline Metrics

| label                   | branch   | risk_on   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                 |
|:------------------------|:---------|:----------|----:|----:|----------:|-------:|---------:|--------:|---------:|:------------------------------------------------------------------------|
| QQQ_QLD_2x_n5k4_rank01  | QQQ      | QLD_2x    |   5 |   4 |    1.3375 | 0.3021 |   0.9565 | -0.6230 |   0.4850 | px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0          |
| QQQ_QLD_2x_n5k4_rank02  | QQQ      | QLD_2x    |   5 |   4 |    1.3354 | 0.3022 |   0.9550 | -0.6071 |   0.4978 | px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| QQQ_QLD_2x_n5k4_rank03  | QQQ      | QLD_2x    |   5 |   4 |    1.3325 | 0.3056 |   0.9575 | -0.6071 |   0.5033 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0           |
| QQQ_TQQQ_3x_n5k4_rank04 | QQQ      | TQQQ_3x   |   5 |   4 |    1.2312 | 0.3762 |   0.9263 | -0.6852 |   0.5491 | px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0          |
| QQQ_TQQQ_3x_n5k4_rank05 | QQQ      | TQQQ_3x   |   5 |   4 |    1.2218 | 0.3733 |   0.9193 | -0.6720 |   0.5556 | px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| QQQ_TQQQ_3x_n5k4_rank06 | QQQ      | TQQQ_3x   |   5 |   4 |    1.2133 | 0.3791 |   0.9177 | -0.7225 |   0.5247 | px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc120_gt_0            |
| SPY_SSO_2x_n5k3_rank07  | SPY      | SSO_2x    |   5 |   3 |    1.2986 | 0.2348 |   0.9082 | -0.5552 |   0.4230 | px_gt_ema20|px_gt_ema50|sma100_gt_sma250|sma50_gt_sma150|rv21_pct_lt_70 |
| SPY_SSO_2x_n3k2_rank08  | SPY      | SSO_2x    |   3 |   2 |    1.2866 | 0.2286 |   0.8952 | -0.5647 |   0.4049 | px_gt_ema20|sma50_gt_sma150|rv21_pct_lt_70                              |
| SPY_SSO_2x_n4k3_rank09  | SPY      | SSO_2x    |   4 |   3 |    1.2829 | 0.2278 |   0.8926 | -0.5647 |   0.4034 | px_gt_ema20|sma50_gt_sma150|rv21_lt_40|rv21_pct_lt_70                   |
| SPY_UPRO_3x_n5k3_rank10 | SPY      | UPRO_3x   |   5 |   3 |    1.1711 | 0.2763 |   0.8433 | -0.6191 |   0.4464 | px_gt_ema20|px_gt_ema50|sma100_gt_sma250|sma50_gt_sma150|rv21_pct_lt_70 |
| SPY_UPRO_3x_n3k2_rank11 | SPY      | UPRO_3x   |   3 |   2 |    1.1673 | 0.2696 |   0.8359 | -0.6158 |   0.4378 | px_gt_ema20|sma50_gt_sma150|rv21_pct_lt_70                              |
| SPY_UPRO_3x_n4k3_rank12 | SPY      | UPRO_3x   |   4 |   3 |    1.1632 | 0.2683 |   0.8331 | -0.6158 |   0.4357 | px_gt_ema20|sma50_gt_sma150|rv21_lt_40|rv21_pct_lt_70                   |

## Interpretation

A candidate passes this validation only if all hard gates pass. DSR uses conservative global trial accounting from the Stage 1 exact grid `[advances_fin_ml, p.222-223]`.
Candidate-panel PBO is diagnostic over the selected top-k set; it is not a literal PBO over all 5.47M grid configs.

## Output Tables

- `tables/candidate_metrics.csv`
- `tables/gates.csv`
- `tables/walk_forward.csv`
- `tables/bootstrap.csv`
- `tables/pbo_panel.csv`
