# Stage 3 Testfolio Price-Only GA

Status: discovery search, not a validation verdict.

## Purpose

Search the long-history testfolio panel first, using only close-derived price signals, before treating Tiingo 2006/2010+ as modern confirmation.

## Run

- Branch/risk-on: `QQQ` / `QLD_2x`
- Off leg: `ZROZSIM`
- Signal subset range: `n=8..14` from 33 available signals
- Population/generations/elite: `256` / `120` / `24`
- Unique candidates observed: 6,250
- Elapsed seconds: 14.5

## Anchors

| label                   |   sortino |   cagr |     mdd |   calmar |   end_mult |
|:------------------------|----------:|-------:|--------:|---------:|-----------:|
| QQQ_QLD_2x_t3d_k2       |    1.0513 | 0.2729 | -0.8215 |   0.3321 | 16605.2868 |
| QQQ_QLD_2x_iter030_like |    1.0581 | 0.2764 | -0.8272 |   0.3342 | 18596.2661 |

## Top Candidates

|   fitness | branch   | risk_on   |   n |   k |   sortino |   cagr |     mdd |   calmar |   edge_sortino_vs_best_anchor |   edge_cagr_vs_best_anchor | beats_t3d_k2   | beats_iter030_like   | signals                                                                                                                                                    |
|----------:|:---------|:----------|----:|----:|----------:|-------:|--------:|---------:|------------------------------:|---------------------------:|:---------------|:---------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
|    3.1793 | QQQ      | QLD_2x    |   8 |   6 |    1.3747 | 0.3206 | -0.5781 |   0.5546 |                        0.3166 |                     0.0442 | True           | True                 | px_gt_sma10<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                      |
|    3.1561 | QQQ      | QLD_2x    |   8 |   6 |    1.3624 | 0.3143 | -0.5633 |   0.5579 |                        0.3044 |                     0.0379 | True           | True                 | px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                   |
|    3.1561 | QQQ      | QLD_2x    |   8 |   6 |    1.3624 | 0.3143 | -0.5633 |   0.5579 |                        0.3044 |                     0.0379 | True           | True                 | px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                   |
|    3.1543 | QQQ      | QLD_2x    |   8 |   6 |    1.3580 | 0.3132 | -0.5505 |   0.5690 |                        0.3000 |                     0.0368 | True           | True                 | px_gt_sma150<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                                  |
|    3.1375 | QQQ      | QLD_2x    |   8 |   6 |    1.3567 | 0.3153 | -0.5807 |   0.5430 |                        0.2986 |                     0.0389 | True           | True                 | px_gt_sma10<br>px_gt_sma150<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                                     |
|    3.1364 | QQQ      | QLD_2x    |   8 |   6 |    1.3588 | 0.3119 | -0.5793 |   0.5385 |                        0.3007 |                     0.0355 | True           | True                 | px_gt_sma150<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                              |
|    3.1310 | QQQ      | QLD_2x    |   8 |   6 |    1.3596 | 0.3114 | -0.5897 |   0.5281 |                        0.3015 |                     0.0350 | True           | True                 | px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                               |
|    3.1267 | QQQ      | QLD_2x    |   8 |   6 |    1.3542 | 0.3139 | -0.5880 |   0.5339 |                        0.2961 |                     0.0375 | True           | True                 | px_gt_sma10<br>px_gt_sma20<br>px_gt_sma150<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0                                     |
|    3.1171 | QQQ      | QLD_2x    |  10 |   7 |    1.3595 | 0.3173 | -0.5781 |   0.5488 |                        0.3014 |                     0.0408 | True           | True                 | px_gt_sma10<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>sma20_gt_sma100<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50 |
|    3.1165 | QQQ      | QLD_2x    |   8 |   6 |    1.3503 | 0.3093 | -0.5803 |   0.5330 |                        0.2922 |                     0.0329 | True           | True                 | px_gt_sma20<br>px_gt_ema20<br>px_gt_sma150<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0                                     |
|    3.1154 | QQQ      | QLD_2x    |   8 |   6 |    1.3437 | 0.3111 | -0.5674 |   0.5483 |                        0.2856 |                     0.0346 | True           | True                 | px_gt_sma10<br>px_gt_sma150<br>px_gt_ema200<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                      |
|    3.1149 | QQQ      | QLD_2x    |   8 |   6 |    1.3504 | 0.3127 | -0.5935 |   0.5268 |                        0.2923 |                     0.0362 | True           | True                 | px_gt_sma10<br>px_gt_sma150<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                                 |
|    3.1114 | QQQ      | QLD_2x    |   8 |   6 |    1.3466 | 0.3108 | -0.5823 |   0.5337 |                        0.2885 |                     0.0343 | True           | True                 | px_gt_sma10<br>px_gt_ema100<br>px_gt_ema200<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                      |
|    3.1048 | QQQ      | QLD_2x    |   8 |   6 |    1.3521 | 0.3128 | -0.6173 |   0.5067 |                        0.2940 |                     0.0363 | True           | True                 | px_gt_sma10<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                  |
|    3.0992 | QQQ      | QLD_2x    |   8 |   6 |    1.3359 | 0.3067 | -0.5594 |   0.5483 |                        0.2778 |                     0.0303 | True           | True                 | px_gt_ema100<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                                  |
|    3.0990 | QQQ      | QLD_2x    |   8 |   6 |    1.3424 | 0.3097 | -0.5880 |   0.5267 |                        0.2843 |                     0.0333 | True           | True                 | px_gt_sma10<br>px_gt_sma100<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0                                  |
|    3.0978 | QQQ      | QLD_2x    |   8 |   6 |    1.3406 | 0.3087 | -0.5817 |   0.5307 |                        0.2825 |                     0.0323 | True           | True                 | px_gt_sma10<br>px_gt_sma20<br>px_gt_ema100<br>px_gt_ema200<br>px_gt_sma250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0                                      |
|    3.0933 | QQQ      | QLD_2x    |   8 |   6 |    1.3448 | 0.3126 | -0.6146 |   0.5086 |                        0.2867 |                     0.0361 | True           | True                 | px_gt_sma10<br>px_gt_sma20<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0                                      |
|    3.0914 | QQQ      | QLD_2x    |   8 |   6 |    1.3484 | 0.3096 | -0.6209 |   0.4987 |                        0.2903 |                     0.0332 | True           | True                 | px_gt_sma20<br>px_gt_ema20<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0                                      |
|    3.0869 | QQQ      | QLD_2x    |   8 |   6 |    1.3397 | 0.3056 | -0.5893 |   0.5186 |                        0.2816 |                     0.0292 | True           | True                 | px_gt_sma20<br>px_gt_ema20<br>px_gt_sma150<br>px_gt_ema200<br>px_gt_ema250<br>sma50_gt_sma200<br>roc20_gt_0<br>roc60_gt_0                                  |
|    3.0862 | QQQ      | QLD_2x    |   8 |   6 |    1.3311 | 0.3042 | -0.5602 |   0.5431 |                        0.2730 |                     0.0278 | True           | True                 | px_gt_sma150<br>px_gt_ema200<br>px_gt_ema250<br>sma50_gt_sma200<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                               |
|    3.0862 | QQQ      | QLD_2x    |   8 |   6 |    1.3311 | 0.3042 | -0.5602 |   0.5431 |                        0.2730 |                     0.0278 | True           | True                 | px_gt_sma150<br>px_gt_ema200<br>px_gt_ema250<br>sma50_gt_sma200<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                               |
|    3.0847 | QQQ      | QLD_2x    |   8 |   6 |    1.3367 | 0.3061 | -0.5850 |   0.5232 |                        0.2786 |                     0.0296 | True           | True                 | px_gt_sma20<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                      |
|    3.0836 | QQQ      | QLD_2x    |   9 |   6 |    1.3364 | 0.3124 | -0.5781 |   0.5403 |                        0.2783 |                     0.0359 | True           | True                 | px_gt_sma10<br>px_gt_sma20<br>px_gt_sma250<br>px_gt_ema250<br>sma20_gt_sma100<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                    |
|    3.0812 | QQQ      | QLD_2x    |   8 |   6 |    1.3355 | 0.3052 | -0.5850 |   0.5217 |                        0.2774 |                     0.0288 | True           | True                 | px_gt_ema20<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                      |

## Method Notes

- Uses the same close-only signal library as Stage 1: moving averages, MACD, ROC, RSI/StochRSI, realized-vol percentiles and AR(1).
- Signals are lagged one trading day before returns are earned to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- Fitness rewards Sortino/CAGR/Calmar and explicit edge versus the best T3d-K2/iter030-like anchor, while penalizing drawdown and excess complexity.
- This is candidate discovery only; any survivor must still clear WF/OOS/FWD/bootstrap/PBO/DSR with cumulative GA trial accounting `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
