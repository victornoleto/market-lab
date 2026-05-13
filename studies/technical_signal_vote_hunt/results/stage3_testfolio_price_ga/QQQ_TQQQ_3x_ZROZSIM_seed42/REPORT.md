# Stage 3 Testfolio Price-Only GA

Status: discovery search, not a validation verdict.

## Purpose

Search the long-history testfolio panel first, using only close-derived price signals, before treating Tiingo 2006/2010+ as modern confirmation.

## Run

- Branch/risk-on: `QQQ` / `TQQQ_3x`
- Off leg: `ZROZSIM`
- Signal subset range: `n=8..14` from 33 available signals
- Population/generations/elite: `256` / `120` / `24`
- Unique candidates observed: 5,576
- Elapsed seconds: 15.6

## Anchors

| label                    |   sortino |   cagr |     mdd |   calmar |   end_mult |
|:-------------------------|----------:|-------:|--------:|---------:|-----------:|
| QQQ_TQQQ_3x_t3d_k2       |    0.9558 | 0.2964 | -0.9529 |   0.3110 | 34714.0587 |
| QQQ_TQQQ_3x_iter030_like |    0.9628 | 0.3010 | -0.9554 |   0.3150 | 40049.2833 |

## Top Candidates

|   fitness | branch   | risk_on   |   n |   k |   sortino |   cagr |     mdd |   calmar |   edge_sortino_vs_best_anchor |   edge_cagr_vs_best_anchor | beats_t3d_k2   | beats_iter030_like   | signals                                                                                                                                                      |
|----------:|:---------|:----------|----:|----:|----------:|-------:|--------:|---------:|------------------------------:|---------------------------:|:---------------|:---------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|
|    3.1535 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2680 | 0.4028 | -0.6424 |   0.6270 |                        0.3052 |                     0.1018 | True           | True                 | px_gt_sma10<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                        |
|    3.1326 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2576 | 0.3943 | -0.6242 |   0.6317 |                        0.2949 |                     0.0933 | True           | True                 | px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                     |
|    3.1326 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2576 | 0.3943 | -0.6242 |   0.6317 |                        0.2949 |                     0.0933 | True           | True                 | px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                     |
|    3.1128 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2579 | 0.3919 | -0.6522 |   0.6010 |                        0.2951 |                     0.0909 | True           | True                 | px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                 |
|    3.1128 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2579 | 0.3919 | -0.6522 |   0.6010 |                        0.2951 |                     0.0909 | True           | True                 | px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                 |
|    3.0940 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2435 | 0.3919 | -0.6410 |   0.6114 |                        0.2807 |                     0.0909 | True           | True                 | px_gt_sma10<br>px_gt_sma150<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                                       |
|    3.0790 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2491 | 0.3927 | -0.6877 |   0.5711 |                        0.2863 |                     0.0917 | True           | True                 | px_gt_sma10<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                    |
|    3.0787 | QQQ      | TQQQ_3x   |  10 |   7 |    1.2490 | 0.3956 | -0.6424 |   0.6158 |                        0.2862 |                     0.0946 | True           | True                 | px_gt_sma10<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>sma20_gt_sma100<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50   |
|    3.0601 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2321 | 0.3848 | -0.6456 |   0.5960 |                        0.2693 |                     0.0838 | True           | True                 | px_gt_sma10<br>px_gt_ema100<br>px_gt_ema200<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                        |
|    3.0586 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2350 | 0.3832 | -0.6526 |   0.5872 |                        0.2722 |                     0.0822 | True           | True                 | px_gt_sma20<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                        |
|    3.0563 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2346 | 0.3822 | -0.6526 |   0.5857 |                        0.2718 |                     0.0812 | True           | True                 | px_gt_ema20<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                        |
|    3.0496 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2293 | 0.3853 | -0.6568 |   0.5866 |                        0.2665 |                     0.0843 | True           | True                 | px_gt_sma10<br>px_gt_sma150<br>px_gt_ema200<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                        |
|    3.0383 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2154 | 0.3746 | -0.6052 |   0.6189 |                        0.2526 |                     0.0736 | True           | True                 | px_gt_ema100<br>px_gt_ema200<br>px_gt_ema250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                     |
|    3.0383 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2154 | 0.3746 | -0.6052 |   0.6189 |                        0.2526 |                     0.0736 | True           | True                 | px_gt_ema100<br>px_gt_ema200<br>px_gt_ema250<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                     |
|    3.0367 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2212 | 0.3809 | -0.6424 |   0.5930 |                        0.2584 |                     0.0799 | True           | True                 | px_gt_sma10<br>px_gt_sma200<br>px_gt_ema200<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                        |
|    3.0352 | QQQ      | TQQQ_3x   |   9 |   7 |    1.2232 | 0.3736 | -0.6052 |   0.6172 |                        0.2604 |                     0.0726 | True           | True                 | px_gt_ema100<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                 |
|    3.0352 | QQQ      | TQQQ_3x   |   9 |   7 |    1.2232 | 0.3736 | -0.6052 |   0.6172 |                        0.2604 |                     0.0726 | True           | True                 | px_gt_ema100<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                 |
|    3.0314 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2212 | 0.3749 | -0.6346 |   0.5907 |                        0.2584 |                     0.0739 | True           | True                 | px_gt_sma100<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>rsi14_gt_50                                |
|    3.0311 | QQQ      | TQQQ_3x   |  10 |   8 |    1.2302 | 0.3771 | -0.6173 |   0.6109 |                        0.2674 |                     0.0762 | True           | True                 | px_gt_ema100<br>px_gt_ema150<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_gt_signal<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50 |
|    3.0311 | QQQ      | TQQQ_3x   |  10 |   8 |    1.2302 | 0.3771 | -0.6173 |   0.6109 |                        0.2674 |                     0.0762 | True           | True                 | px_gt_ema100<br>px_gt_ema150<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50 |
|    3.0309 | QQQ      | TQQQ_3x   |   8 |   5 |    1.2151 | 0.3859 | -0.6476 |   0.5959 |                        0.2523 |                     0.0849 | True           | True                 | px_gt_sma10<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50<br>rv21_pct_lt_50                                      |
|    3.0295 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2301 | 0.3792 | -0.6784 |   0.5589 |                        0.2673 |                     0.0782 | True           | True                 | px_gt_ema20<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                    |
|    3.0262 | QQQ      | TQQQ_3x   |   9 |   7 |    1.2183 | 0.3733 | -0.6052 |   0.6168 |                        0.2555 |                     0.0723 | True           | True                 | px_gt_ema150<br>px_gt_ema200<br>px_gt_ema250<br>sma100_gt_sma250<br>macd_hist_gt_0<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                 |
|    3.0252 | QQQ      | TQQQ_3x   |   8 |   6 |    1.2168 | 0.3797 | -0.6456 |   0.5882 |                        0.2540 |                     0.0787 | True           | True                 | px_gt_sma10<br>px_gt_ema150<br>px_gt_ema200<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                                        |
|    3.0248 | QQQ      | TQQQ_3x   |   9 |   7 |    1.2223 | 0.3811 | -0.6410 |   0.5946 |                        0.2595 |                     0.0801 | True           | True                 | px_gt_sma10<br>px_gt_ema150<br>px_gt_ema200<br>px_gt_sma250<br>px_gt_ema250<br>roc20_gt_0<br>roc60_gt_0<br>roc120_gt_0<br>rsi14_gt_50                        |

## Method Notes

- Uses the same close-only signal library as Stage 1: moving averages, MACD, ROC, RSI/StochRSI, realized-vol percentiles and AR(1).
- Signals are lagged one trading day before returns are earned to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- Fitness rewards Sortino/CAGR/Calmar and explicit edge versus the best T3d-K2/iter030-like anchor, while penalizing drawdown and excess complexity.
- This is candidate discovery only; any survivor must still clear WF/OOS/FWD/bootstrap/PBO/DSR with cumulative GA trial accounting `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
