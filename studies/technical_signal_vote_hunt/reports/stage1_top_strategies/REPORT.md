# Stage 1 Top Strategies Deep Dive

Status: exploratory report from the Stage 1 close-only exact grid. This is not a deploy verdict.

Selection: top 3 by Sortino per `(branch, risk_on)` from `/var/www/github/finances/market-lab/studies/technical_signal_vote_hunt/results/stage1_close_only_fast/tables/stage1_results_fast.csv`.
Off leg: `ZROZSIM`.

## Selected Candidates

| branch   | risk_on   |   n |   k |   sortino |   cagr |   sharpe |     mdd |   calmar | signals                                                                 |
|:---------|:----------|----:|----:|----------:|-------:|---------:|--------:|---------:|:------------------------------------------------------------------------|
| QQQ      | QLD_2x    |   5 |   4 |    1.3375 | 0.3021 |   0.9565 | -0.6230 |   0.4850 | px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0          |
| QQQ      | QLD_2x    |   5 |   4 |    1.3354 | 0.3022 |   0.9550 | -0.6071 |   0.4978 | px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| QQQ      | QLD_2x    |   5 |   4 |    1.3325 | 0.3056 |   0.9575 | -0.6071 |   0.5033 | px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0           |
| QQQ      | TQQQ_3x   |   5 |   4 |    1.2312 | 0.3762 |   0.9263 | -0.6852 |   0.5491 | px_gt_ema200|px_gt_ema250|macd_gt_signal|roc20_gt_0|roc60_gt_0          |
| QQQ      | TQQQ_3x   |   5 |   4 |    1.2218 | 0.3733 |   0.9193 | -0.6720 |   0.5556 | px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0             |
| QQQ      | TQQQ_3x   |   5 |   4 |    1.2133 | 0.3791 |   0.9177 | -0.7225 |   0.5247 | px_gt_sma20|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc120_gt_0            |
| SPY      | SSO_2x    |   5 |   3 |    1.2986 | 0.2348 |   0.9082 | -0.5552 |   0.4230 | px_gt_ema20|px_gt_ema50|sma100_gt_sma250|sma50_gt_sma150|rv21_pct_lt_70 |
| SPY      | SSO_2x    |   3 |   2 |    1.2866 | 0.2286 |   0.8952 | -0.5647 |   0.4049 | px_gt_ema20|sma50_gt_sma150|rv21_pct_lt_70                              |
| SPY      | SSO_2x    |   4 |   3 |    1.2829 | 0.2278 |   0.8926 | -0.5647 |   0.4034 | px_gt_ema20|sma50_gt_sma150|rv21_lt_40|rv21_pct_lt_70                   |
| SPY      | UPRO_3x   |   5 |   3 |    1.1711 | 0.2763 |   0.8433 | -0.6191 |   0.4464 | px_gt_ema20|px_gt_ema50|sma100_gt_sma250|sma50_gt_sma150|rv21_pct_lt_70 |
| SPY      | UPRO_3x   |   3 |   2 |    1.1673 | 0.2696 |   0.8359 | -0.6158 |   0.4378 | px_gt_ema20|sma50_gt_sma150|rv21_pct_lt_70                              |
| SPY      | UPRO_3x   |   4 |   3 |    1.1632 | 0.2683 |   0.8331 | -0.6158 |   0.4357 | px_gt_ema20|sma50_gt_sma150|rv21_lt_40|rv21_pct_lt_70                   |

## Headline Metrics

| branch   | risk_on   | label                    |   sortino |   cagr |   sharpe |     mdd |   calmar |   end_rel_to_benchmark |   pct_above_benchmark |
|:---------|:----------|:-------------------------|----------:|-------:|---------:|--------:|---------:|-----------------------:|----------------------:|
| QQQ      | QLD_2x    | QQQ_QLD_2x_top01_n5k4    |    1.3375 | 0.3021 |   0.9565 | -0.6230 |   0.4850 |               171.9513 |                1.0000 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top02_n5k4    |    1.3354 | 0.3022 |   0.9550 | -0.6071 |   0.4978 |               172.2293 |                1.0000 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top03_n5k4    |    1.3325 | 0.3056 |   0.9575 | -0.6071 |   0.5033 |               191.0215 |                1.0000 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_iter030_like  |    1.0581 | 0.2764 |   0.7975 | -0.8272 |   0.3342 |                77.0115 |                1.0000 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_t3d_k2        |    1.0513 | 0.2729 |   0.7925 | -0.8215 |   0.3321 |                68.7664 |                1.0000 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_lrs_sma200    |    0.9386 | 0.2169 |   0.6981 | -0.7788 |   0.2785 |                11.2571 |                1.0000 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_buy_hold      |    0.8660 | 0.1459 |   0.6583 | -0.8297 |   0.1759 |                 1.0000 |                0.0000 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top01_n5k4   |    1.2312 | 0.3762 |   0.9263 | -0.6852 |   0.5491 |              1596.9393 |                1.0000 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top02_n5k4   |    1.2218 | 0.3733 |   0.9193 | -0.6720 |   0.5556 |              1466.6475 |                1.0000 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top03_n5k4   |    1.2133 | 0.3791 |   0.9177 | -0.7225 |   0.5247 |              1735.2111 |                1.0000 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_iter030_like |    0.9628 | 0.3010 |   0.7419 | -0.9554 |   0.3150 |               165.8534 |                1.0000 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_t3d_k2       |    0.9558 | 0.2964 |   0.7367 | -0.9529 |   0.3110 |               143.7590 |                1.0000 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_buy_hold     |    0.8660 | 0.1459 |   0.6583 | -0.8297 |   0.1759 |                 1.0000 |                0.0000 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_lrs_sma200   |    0.8536 | 0.2335 |   0.6568 | -0.9286 |   0.2515 |                19.4141 |                1.0000 |
| SPY      | SSO_2x    | SPY_SSO_2x_top01_n5k3    |    1.2986 | 0.2348 |   0.9082 | -0.5552 |   0.4230 |                60.9800 |                1.0000 |
| SPY      | SSO_2x    | SPY_SSO_2x_top02_n3k2    |    1.2866 | 0.2286 |   0.8952 | -0.5647 |   0.4049 |                49.7991 |                1.0000 |
| SPY      | SSO_2x    | SPY_SSO_2x_top03_n4k3    |    1.2829 | 0.2278 |   0.8926 | -0.5647 |   0.4034 |                48.3987 |                1.0000 |
| SPY      | SSO_2x    | SPY_SSO_2x_iter030_like  |    0.9581 | 0.2012 |   0.7423 | -0.6332 |   0.3177 |                20.0445 |                1.0000 |
| SPY      | SSO_2x    | SPY_SSO_2x_lrs_sma200    |    0.9574 | 0.1707 |   0.6973 | -0.5780 |   0.2953 |                 7.1181 |                1.0000 |
| SPY      | SSO_2x    | SPY_SSO_2x_t3d_k2        |    0.9490 | 0.1986 |   0.7361 | -0.6332 |   0.3137 |                18.3999 |                1.0000 |
| SPY      | SSO_2x    | SPY_SSO_2x_buy_hold      |    0.8418 | 0.1147 |   0.6819 | -0.5514 |   0.2080 |                 1.0000 |                0.0000 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top01_n5k3   |    1.1711 | 0.2763 |   0.8433 | -0.6191 |   0.4464 |               230.8642 |                1.0000 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top02_n3k2   |    1.1673 | 0.2696 |   0.8359 | -0.6158 |   0.4378 |               186.7428 |                1.0000 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top03_n4k3   |    1.1632 | 0.2683 |   0.8331 | -0.6158 |   0.4357 |               178.9285 |                1.0000 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_lrs_sma200   |    0.8766 | 0.1966 |   0.6567 | -0.6726 |   0.2923 |                17.1852 |                1.0000 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_iter030_like |    0.8563 | 0.2208 |   0.6762 | -0.8256 |   0.2675 |                38.5253 |                0.9999 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_t3d_k2       |    0.8471 | 0.2171 |   0.6699 | -0.8256 |   0.2630 |                34.0855 |                0.9955 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_buy_hold     |    0.8418 | 0.1147 |   0.6819 | -0.5514 |   0.2080 |                 1.0000 |                0.0000 |

## Interpretive Verdict

The Stage 1 exact grid found a strong research lead, but not a validated replacement for T3d-K2 / iter030.

Best current lead:

```text
Branch: QQQ -> QLD
n=5, k=4
Signals: EMA200, EMA250, MACD, ROC20, ROC60
```

This lead is best understood as a more restrictive trend/momentum confirmation gate. It differs from the T3d-K2 master signal:

```text
T3d-K2: SMA250 + SMA100 + vol21<40 + AR1>0, k=2/4
New lead: EMA200 + EMA250 + MACD + ROC20 + ROC60, k=4/5
```

The empirical read is that, in this close-only grid, NDX/QLD responds better to long-trend plus short/medium momentum confirmation than to the original mixed trend/vol/AR1 vote. The new top lead improves both risk-adjusted return and drawdown versus branch-native transplants:

| Strategy | Sortino | CAGR | MDD | Read |
|---|---:|---:|---:|---|
| QQQ->QLD new `n=5/k=4` | 1.3375 | 30.21% | -62.30% | best in-sample lead |
| QQQ->QLD iter030-like | 1.0581 | 27.64% | -82.72% | branch-native prior reference |
| QQQ->QLD T3d-K2 | 1.0513 | 27.29% | -82.15% | branch-native T3d transplant |
| QQQ->QLD LRS SMA200 | 0.9386 | 21.69% | -77.88% | simple LRS baseline |

For the aggressive QQQ->TQQQ branch, the same signal family also wins, with higher CAGR but a more aggressive leverage profile:

```text
QQQ->TQQQ top01: Sortino 1.2312, CAGR 37.62%, MDD -68.52%
```

The SPY branch produced useful secondary leads, but the central result remains NDX/QQQ-driven. SPY's best signal family is more volatility-filtered and shorter-horizon:

```text
EMA20 + EMA50 + SMA100>SMA250 + SMA50>SMA150 + RV21 percentile<70, k=3/5
```

Current ranking of research leads:

1. QQQ->QLD `EMA200/EMA250/MACD/ROC20/ROC60`, `k=4/5` — strongest balanced lead.
2. QQQ->TQQQ with the same signal — performance-first/aggressive variant.
3. SPY->SSO top signal — interesting cross-underlying confirmation, but secondary.
4. T3d-K2 / iter030 transplants — still the governance reference until validation is complete.

Critical caveat: these candidates were selected in-sample from 5,471,268 exact-grid configs. This is a severe multiple-testing environment, so the correct verdict is **strong lead, not validated winner**. Final claims require walk-forward, OOS, FWD, bootstrap, PBO and DSR `[advances_fin_ml, p.208-211]`.

## Validation Outlook

Expected validation workload for the top candidates is modest if we validate only the selected top-k set. For the current top-3 per branch/risk-on (12 candidates) plus native benchmarks, estimated runtime is likely minutes once a validation runner exists:

| Gate / diagnostic | Expected runtime | Notes |
|---|---:|---|
| OOS 70/30 | seconds | single split per candidate |
| FWD post-2020 | seconds | single recent-window slice |
| Walk-forward | seconds to low minutes | 8 windows per candidate |
| Bootstrap | low minutes | depends on bootstrap count; 2,000 paths is manageable |
| PBO on selected candidate panel | seconds to low minutes | meaningful as a candidate-panel PBO, not full 5.47M-grid PBO |
| DSR with `n_trials>=5.47M` | seconds | computationally cheap but statistically harsh |

Implementation time for a clean validation runner is larger than runtime: roughly 1-2 engineering hours to wire candidate reconstruction, shared metrics, output tables, plots and report.

DSR with `n_trials=5,471,268` is not impossible, but it is intentionally brutal. A quick check on the current top QQQ->QLD candidate gives:

```text
observed_sharpe_per_bar = 0.060255
deflated benchmark sharpe = 0.051555
DSR = 0.8095
p_value = 0.1905
```

So under full-grid DSR accounting, the current top lead **fails** the `p<0.05` hard gate. This does not make the lead useless; it means it should be treated as a research lead unless it can survive either stricter robustness evidence or a more defensible trial-accounting design. The correct interpretation is that the exact grid has found economically interesting structure, but the statistical burden of 5.47M tested variants is high enough that raw Sortino/CAGR dominance is insufficient.

PBO over all 5.47M configs is also not practical as a literal full matrix unless we build a dedicated streaming/blocked implementation. The near-term practical validation should do both:

1. candidate-panel PBO over top-k finalists plus close benchmark variants;
2. DSR with conservative global `n_trials >= 5.47M` to reflect the full search burden.

## Rolling Summary

| branch   | risk_on   | label                    |   window_years |   cagr_mean |   cagr_min |   sortino_mean |   sortino_min |
|:---------|:----------|:-------------------------|---------------:|------------:|-----------:|---------------:|--------------:|
| QQQ      | QLD_2x    | QQQ_QLD_2x_buy_hold      |              3 |      0.1570 |    -0.3289 |         1.1158 |       -0.8711 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_buy_hold      |              5 |      0.1502 |    -0.1369 |         1.0461 |       -0.2007 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_buy_hold      |             10 |      0.1423 |    -0.0564 |         0.9383 |        0.0106 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_buy_hold      |             15 |      0.1259 |     0.0209 |         0.8037 |        0.2952 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_lrs_sma200    |              3 |      0.2211 |    -0.2057 |         0.9607 |       -0.1514 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_lrs_sma200    |              5 |      0.2073 |    -0.0230 |         0.9229 |        0.2548 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_lrs_sma200    |             10 |      0.1993 |     0.0391 |         0.8810 |        0.3935 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_lrs_sma200    |             15 |      0.1860 |     0.0789 |         0.8342 |        0.5090 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_t3d_k2        |              3 |      0.2826 |    -0.2727 |         1.1049 |       -0.3113 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_t3d_k2        |              5 |      0.2674 |    -0.0581 |         1.0715 |        0.1828 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_t3d_k2        |             10 |      0.2665 |     0.0111 |         1.0610 |        0.3217 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_t3d_k2        |             15 |      0.2508 |     0.1279 |         1.0068 |        0.6504 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_iter030_like  |              3 |      0.2858 |    -0.2804 |         1.1121 |       -0.3245 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_iter030_like  |              5 |      0.2693 |    -0.0640 |         1.0756 |        0.1694 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_iter030_like  |             10 |      0.2674 |     0.0096 |         1.0616 |        0.3189 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_iter030_like  |             15 |      0.2514 |     0.1267 |         1.0050 |        0.6444 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top01_n5k4    |              3 |      0.3085 |    -0.0399 |         1.3021 |        0.0437 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top01_n5k4    |              5 |      0.2973 |     0.0896 |         1.2810 |        0.6528 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top01_n5k4    |             10 |      0.2914 |     0.1453 |         1.2661 |        0.8311 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top01_n5k4    |             15 |      0.2899 |     0.1611 |         1.2464 |        0.9488 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top02_n5k4    |              3 |      0.3067 |    -0.0320 |         1.3154 |        0.0887 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top02_n5k4    |              5 |      0.2944 |     0.0989 |         1.2880 |        0.6917 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top02_n5k4    |             10 |      0.2868 |     0.1548 |         1.2581 |        0.8124 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top02_n5k4    |             15 |      0.2820 |     0.1612 |         1.2255 |        0.9536 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top03_n5k4    |              3 |      0.3098 |    -0.0452 |         1.3299 |        0.0149 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top03_n5k4    |              5 |      0.2975 |     0.0940 |         1.2984 |        0.6661 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top03_n5k4    |             10 |      0.2927 |     0.1648 |         1.2664 |        0.8171 |
| QQQ      | QLD_2x    | QQQ_QLD_2x_top03_n5k4    |             15 |      0.2884 |     0.1816 |         1.2346 |        0.9753 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_buy_hold     |              3 |      0.1570 |    -0.3289 |         1.1158 |       -0.8711 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_buy_hold     |              5 |      0.1502 |    -0.1369 |         1.0461 |       -0.2007 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_buy_hold     |             10 |      0.1423 |    -0.0564 |         0.9383 |        0.0106 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_buy_hold     |             15 |      0.1259 |     0.0209 |         0.8037 |        0.2952 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_lrs_sma200   |              3 |      0.2517 |    -0.3981 |         0.8787 |       -0.2457 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_lrs_sma200   |              5 |      0.2300 |    -0.1565 |         0.8529 |        0.1290 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_lrs_sma200   |             10 |      0.2128 |    -0.0465 |         0.8200 |        0.2743 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_lrs_sma200   |             15 |      0.1886 |     0.0348 |         0.7718 |        0.4281 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_t3d_k2       |              3 |      0.3300 |    -0.4915 |         1.0201 |       -0.4309 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_t3d_k2       |              5 |      0.3043 |    -0.2173 |         0.9934 |        0.0708 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_t3d_k2       |             10 |      0.2962 |    -0.0931 |         0.9866 |        0.2115 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_t3d_k2       |             15 |      0.2673 |     0.0890 |         0.9302 |        0.5603 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_iter030_like |              3 |      0.3343 |    -0.5006 |         1.0273 |       -0.4425 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_iter030_like |              5 |      0.3065 |    -0.2258 |         0.9975 |        0.0586 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_iter030_like |             10 |      0.2971 |    -0.0966 |         0.9873 |        0.2099 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_iter030_like |             15 |      0.2674 |     0.0862 |         0.9287 |        0.5550 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top01_n5k4   |              3 |      0.3950 |    -0.0001 |         1.2109 |        0.3187 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top01_n5k4   |              5 |      0.3798 |     0.1123 |         1.1991 |        0.6008 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top01_n5k4   |             10 |      0.3662 |     0.1744 |         1.1818 |        0.7643 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top01_n5k4   |             15 |      0.3608 |     0.1918 |         1.1568 |        0.8823 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top02_n5k4   |              3 |      0.3900 |    -0.0004 |         1.2156 |        0.3387 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top02_n5k4   |              5 |      0.3726 |     0.0916 |         1.1963 |        0.5798 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top02_n5k4   |             10 |      0.3572 |     0.1491 |         1.1669 |        0.6806 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top02_n5k4   |             15 |      0.3465 |     0.1874 |         1.1303 |        0.8703 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top03_n5k4   |              3 |      0.3892 |    -0.0610 |         1.2411 |        0.0878 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top03_n5k4   |              5 |      0.3734 |     0.1241 |         1.2161 |        0.6778 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top03_n5k4   |             10 |      0.3670 |     0.1841 |         1.1806 |        0.7514 |
| QQQ      | TQQQ_3x   | QQQ_TQQQ_3x_top03_n5k4   |             15 |      0.3595 |     0.2371 |         1.1479 |        0.9641 |
| SPY      | SSO_2x    | SPY_SSO_2x_buy_hold      |              3 |      0.1151 |    -0.1304 |         1.0917 |       -0.7409 |
| SPY      | SSO_2x    | SPY_SSO_2x_buy_hold      |              5 |      0.1113 |    -0.0277 |         1.0011 |       -0.0286 |
| SPY      | SSO_2x    | SPY_SSO_2x_buy_hold      |             10 |      0.1055 |    -0.0142 |         0.8678 |        0.0662 |
| SPY      | SSO_2x    | SPY_SSO_2x_buy_hold      |             15 |      0.0951 |     0.0450 |         0.7596 |        0.4182 |
| SPY      | SSO_2x    | SPY_SSO_2x_lrs_sma200    |              3 |      0.1674 |    -0.0555 |         0.9451 |       -0.1394 |
| SPY      | SSO_2x    | SPY_SSO_2x_lrs_sma200    |              5 |      0.1590 |     0.0287 |         0.9238 |        0.3183 |
| SPY      | SSO_2x    | SPY_SSO_2x_lrs_sma200    |             10 |      0.1540 |     0.0453 |         0.8837 |        0.4257 |
| SPY      | SSO_2x    | SPY_SSO_2x_lrs_sma200    |             15 |      0.1408 |     0.0682 |         0.8280 |        0.5184 |
| SPY      | SSO_2x    | SPY_SSO_2x_t3d_k2        |              3 |      0.1953 |    -0.1817 |         0.9997 |       -0.5248 |
| SPY      | SSO_2x    | SPY_SSO_2x_t3d_k2        |              5 |      0.1880 |    -0.0470 |         0.9702 |        0.0375 |
| SPY      | SSO_2x    | SPY_SSO_2x_t3d_k2        |             10 |      0.1846 |     0.0475 |         0.9407 |        0.4189 |
| SPY      | SSO_2x    | SPY_SSO_2x_t3d_k2        |             15 |      0.1761 |     0.1218 |         0.9107 |        0.7099 |
| SPY      | SSO_2x    | SPY_SSO_2x_iter030_like  |              3 |      0.1974 |    -0.1817 |         1.0043 |       -0.5248 |
| SPY      | SSO_2x    | SPY_SSO_2x_iter030_like  |              5 |      0.1894 |    -0.0470 |         0.9741 |        0.0375 |
| SPY      | SSO_2x    | SPY_SSO_2x_iter030_like  |             10 |      0.1857 |     0.0475 |         0.9444 |        0.4189 |
| SPY      | SSO_2x    | SPY_SSO_2x_iter030_like  |             15 |      0.1771 |     0.1228 |         0.9146 |        0.7142 |
| SPY      | SSO_2x    | SPY_SSO_2x_top01_n5k3    |              3 |      0.2267 |    -0.0085 |         1.2946 |        0.2015 |
| SPY      | SSO_2x    | SPY_SSO_2x_top01_n5k3    |              5 |      0.2209 |     0.0121 |         1.2719 |        0.2538 |
| SPY      | SSO_2x    | SPY_SSO_2x_top01_n5k3    |             10 |      0.2235 |     0.1030 |         1.2669 |        0.6844 |
| SPY      | SSO_2x    | SPY_SSO_2x_top01_n5k3    |             15 |      0.2226 |     0.1567 |         1.2589 |        0.9170 |
| SPY      | SSO_2x    | SPY_SSO_2x_top02_n3k2    |              3 |      0.2272 |    -0.0085 |         1.3032 |        0.1667 |
| SPY      | SSO_2x    | SPY_SSO_2x_top02_n3k2    |              5 |      0.2220 |     0.0576 |         1.2892 |        0.4705 |
| SPY      | SSO_2x    | SPY_SSO_2x_top02_n3k2    |             10 |      0.2233 |     0.1270 |         1.2814 |        0.8211 |
| SPY      | SSO_2x    | SPY_SSO_2x_top02_n3k2    |             15 |      0.2204 |     0.1874 |         1.2612 |        1.0701 |
| SPY      | SSO_2x    | SPY_SSO_2x_top03_n4k3    |              3 |      0.2263 |    -0.0085 |         1.2993 |        0.1667 |
| SPY      | SSO_2x    | SPY_SSO_2x_top03_n4k3    |              5 |      0.2211 |     0.0576 |         1.2850 |        0.4705 |
| SPY      | SSO_2x    | SPY_SSO_2x_top03_n4k3    |             10 |      0.2222 |     0.1270 |         1.2763 |        0.8211 |
| SPY      | SSO_2x    | SPY_SSO_2x_top03_n4k3    |             15 |      0.2193 |     0.1874 |         1.2561 |        1.0701 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_buy_hold     |              3 |      0.1151 |    -0.1304 |         1.0917 |       -0.7409 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_buy_hold     |              5 |      0.1113 |    -0.0277 |         1.0011 |       -0.0286 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_buy_hold     |             10 |      0.1055 |    -0.0142 |         0.8678 |        0.0662 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_buy_hold     |             15 |      0.0951 |     0.0450 |         0.7596 |        0.4182 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_lrs_sma200   |              3 |      0.2005 |    -0.1533 |         0.8698 |       -0.2700 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_lrs_sma200   |              5 |      0.1870 |    -0.0043 |         0.8493 |        0.2701 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_lrs_sma200   |             10 |      0.1788 |     0.0133 |         0.8146 |        0.3049 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_lrs_sma200   |             15 |      0.1569 |     0.0412 |         0.7560 |        0.4079 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_t3d_k2       |              3 |      0.2262 |    -0.3185 |         0.9130 |       -0.6370 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_t3d_k2       |              5 |      0.2174 |    -0.1272 |         0.8893 |       -0.0453 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_t3d_k2       |             10 |      0.2112 |    -0.0001 |         0.8595 |        0.3118 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_t3d_k2       |             15 |      0.1952 |     0.1001 |         0.8254 |        0.5954 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_iter030_like |              3 |      0.2289 |    -0.3185 |         0.9176 |       -0.6370 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_iter030_like |              5 |      0.2193 |    -0.1272 |         0.8933 |       -0.0453 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_iter030_like |             10 |      0.2127 |    -0.0001 |         0.8633 |        0.3118 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_iter030_like |             15 |      0.1967 |     0.1016 |         0.8293 |        0.5998 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top01_n5k3   |              3 |      0.2717 |    -0.0019 |         1.1642 |        0.2736 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top01_n5k3   |              5 |      0.2629 |     0.0111 |         1.1452 |        0.2919 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top01_n5k3   |             10 |      0.2648 |     0.1282 |         1.1424 |        0.6743 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top01_n5k3   |             15 |      0.2606 |     0.2151 |         1.1310 |        0.9588 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top02_n3k2   |              3 |      0.2747 |    -0.0935 |         1.1766 |       -0.0203 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top02_n3k2   |              5 |      0.2651 |    -0.0285 |         1.1629 |        0.1829 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top02_n3k2   |             10 |      0.2623 |     0.0961 |         1.1490 |        0.6019 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top02_n3k2   |             15 |      0.2540 |     0.1909 |         1.1210 |        0.9315 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top03_n4k3   |              3 |      0.2733 |    -0.0935 |         1.1726 |       -0.0203 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top03_n4k3   |              5 |      0.2636 |    -0.0368 |         1.1584 |        0.1526 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top03_n4k3   |             10 |      0.2607 |     0.0914 |         1.1436 |        0.5860 |
| SPY      | UPRO_3x   | SPY_UPRO_3x_top03_n4k3   |             15 |      0.2522 |     0.1875 |         1.1156 |        0.9205 |

## Plot Index

### QQQ->QLD_2x

![Equity](plots/QQQ_QLD_2x_01_equity.png)
![Relative equity](plots/QQQ_QLD_2x_02_relative_equity.png)
![Drawdown](plots/QQQ_QLD_2x_03_drawdown.png)
![Rolling CAGR](plots/QQQ_QLD_2x_04_rolling_cagr.png)
![Rolling Sortino](plots/QQQ_QLD_2x_04_rolling_sortino.png)

### QQQ->TQQQ_3x

![Equity](plots/QQQ_TQQQ_3x_01_equity.png)
![Relative equity](plots/QQQ_TQQQ_3x_02_relative_equity.png)
![Drawdown](plots/QQQ_TQQQ_3x_03_drawdown.png)
![Rolling CAGR](plots/QQQ_TQQQ_3x_04_rolling_cagr.png)
![Rolling Sortino](plots/QQQ_TQQQ_3x_04_rolling_sortino.png)

### SPY->SSO_2x

![Equity](plots/SPY_SSO_2x_01_equity.png)
![Relative equity](plots/SPY_SSO_2x_02_relative_equity.png)
![Drawdown](plots/SPY_SSO_2x_03_drawdown.png)
![Rolling CAGR](plots/SPY_SSO_2x_04_rolling_cagr.png)
![Rolling Sortino](plots/SPY_SSO_2x_04_rolling_sortino.png)

### SPY->UPRO_3x

![Equity](plots/SPY_UPRO_3x_01_equity.png)
![Relative equity](plots/SPY_UPRO_3x_02_relative_equity.png)
![Drawdown](plots/SPY_UPRO_3x_03_drawdown.png)
![Rolling CAGR](plots/SPY_UPRO_3x_04_rolling_cagr.png)
![Rolling Sortino](plots/SPY_UPRO_3x_04_rolling_sortino.png)

## Caveats

- These candidates were selected in-sample from 5,471,268 exact-grid configs.
- DSR trial accounting must include the full grid and any GA evaluations `[advances_fin_ml, p.222-223]`.
- Next validation step: deduplicate candidates and run walk-forward, OOS, FWD, bootstrap, PBO and DSR `[advances_fin_ml, p.208-211]`.
