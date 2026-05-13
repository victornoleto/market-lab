# Stage 3 Testfolio Price-Only GA

Status: discovery search, not a validation verdict.

## Purpose

Search the long-history testfolio panel first, using only close-derived price signals, before treating Tiingo 2006/2010+ as modern confirmation.

## Run

- Branch/risk-on: `QQQ` / `QLD_2x`
- Off leg: `ZROZSIM`
- Signal subset range: `n=8..8` from 12 available signals
- Population/generations/elite: `12` / `2` / `4`
- Unique candidates observed: 20
- Elapsed seconds: 0.0

## Anchors

| label                   |   sortino |   cagr |     mdd |   calmar |   end_mult |
|:------------------------|----------:|-------:|--------:|---------:|-----------:|
| QQQ_QLD_2x_t3d_k2       |    1.0513 | 0.2729 | -0.8215 |   0.3321 | 16605.2868 |
| QQQ_QLD_2x_iter030_like |    1.0581 | 0.2764 | -0.8272 |   0.3342 | 18596.2661 |

## Top Candidates

|   fitness | branch   | risk_on   |   n |   k |   sortino |   cagr |     mdd |   calmar |   edge_sortino_vs_best_anchor |   edge_cagr_vs_best_anchor | beats_t3d_k2   | beats_iter030_like   | signals                                                                                                                 |
|----------:|:---------|:----------|----:|----:|----------:|-------:|--------:|---------:|------------------------------:|---------------------------:|:---------------|:---------------------|:------------------------------------------------------------------------------------------------------------------------|
|    1.0520 | QQQ      | QLD_2x    |   8 |   4 |    1.0046 | 0.2342 | -0.7783 |   0.3009 |                       -0.0535 |                    -0.0423 | False          | False                | px_gt_sma5<br>px_gt_ema5<br>px_gt_sma10<br>px_gt_ema20<br>px_gt_ema50<br>px_gt_sma100<br>px_gt_ema100<br>px_gt_ema150   |
|    1.0465 | QQQ      | QLD_2x    |   8 |   5 |    1.0114 | 0.2291 | -0.8042 |   0.2849 |                       -0.0467 |                    -0.0473 | False          | False                | px_gt_ema5<br>px_gt_sma10<br>px_gt_ema20<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_sma100<br>px_gt_sma150<br>px_gt_ema150  |
|    1.0370 | QQQ      | QLD_2x    |   8 |   4 |    1.0121 | 0.2347 | -0.8554 |   0.2744 |                       -0.0460 |                    -0.0418 | False          | False                | px_gt_sma5<br>px_gt_ema5<br>px_gt_sma10<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_sma100<br>px_gt_ema100<br>px_gt_sma150   |
|    1.0344 | QQQ      | QLD_2x    |   8 |   4 |    1.0031 | 0.2320 | -0.8092 |   0.2867 |                       -0.0549 |                    -0.0445 | False          | False                | px_gt_ema10<br>px_gt_sma20<br>px_gt_ema20<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_sma100<br>px_gt_ema100<br>px_gt_ema150 |
|    1.0209 | QQQ      | QLD_2x    |   8 |   2 |    0.9873 | 0.2382 | -0.7959 |   0.2992 |                       -0.0708 |                    -0.0383 | False          | False                | px_gt_ema10<br>px_gt_sma20<br>px_gt_ema20<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_sma100<br>px_gt_ema100<br>px_gt_ema150 |
|    1.0103 | QQQ      | QLD_2x    |   8 |   7 |    0.9593 | 0.1839 | -0.5052 |   0.3640 |                       -0.0988 |                    -0.0925 | False          | False                | px_gt_sma10<br>px_gt_ema10<br>px_gt_sma20<br>px_gt_ema20<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_ema100<br>px_gt_sma150  |
|    1.0058 | QQQ      | QLD_2x    |   8 |   5 |    0.9856 | 0.2199 | -0.7562 |   0.2908 |                       -0.0725 |                    -0.0565 | False          | False                | px_gt_sma10<br>px_gt_sma20<br>px_gt_ema20<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_ema100<br>px_gt_sma150<br>px_gt_ema150 |
|    0.9826 | QQQ      | QLD_2x    |   8 |   5 |    0.9863 | 0.2201 | -0.8225 |   0.2676 |                       -0.0717 |                    -0.0563 | False          | False                | px_gt_sma5<br>px_gt_ema10<br>px_gt_sma20<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_ema100<br>px_gt_sma150<br>px_gt_ema150  |
|    0.9226 | QQQ      | QLD_2x    |   8 |   7 |    0.9315 | 0.1763 | -0.5603 |   0.3146 |                       -0.1266 |                    -0.1002 | False          | False                | px_gt_sma5<br>px_gt_ema10<br>px_gt_sma20<br>px_gt_ema20<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_ema100<br>px_gt_sma150   |
|    0.8215 | QQQ      | QLD_2x    |   8 |   7 |    0.8827 | 0.1643 | -0.5503 |   0.2986 |                       -0.1754 |                    -0.1121 | False          | False                | px_gt_sma10<br>px_gt_ema10<br>px_gt_ema20<br>px_gt_sma50<br>px_gt_ema50<br>px_gt_sma100<br>px_gt_ema100<br>px_gt_ema150 |

## Method Notes

- Uses the same close-only signal library as Stage 1: moving averages, MACD, ROC, RSI/StochRSI, realized-vol percentiles and AR(1).
- Signals are lagged one trading day before returns are earned to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.
- Fitness rewards Sortino/CAGR/Calmar and explicit edge versus the best T3d-K2/iter030-like anchor, while penalizing drawdown and excess complexity.
- This is candidate discovery only; any survivor must still clear WF/OOS/FWD/bootstrap/PBO/DSR with cumulative GA trial accounting `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
