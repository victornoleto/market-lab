# SPY Leveraged Rotation GA Evolution Report

Window: `1986-01-03..2026-04-17`
Completed evolutions: `6`
Unique candidates in final manifests: `7008`

## Executive Read

Initial economic screen beaters vs `SPY buy_hold`: `5` among GA best candidates.
Best tempo acima: `evo02_spy_upro_performance best` with pct-above `83.78%` and mean relative equity `1.7258x`.
Best magnitude relativa: `evo05_diversity_low_corr best` with pct-above `80.84%` and mean relative equity `1.7681x`.
SPY: best `evo01_spy_sso_repair best` with Sortino `0.9738`, CAGR `16.71%`, Sharpe `0.7542`, MDD `-35.86%`, Calmar `0.4661`.
SSO: best `evo05_diversity_low_corr best` with Sortino `1.1487`, CAGR `17.26%`, Sharpe `0.8058`, MDD `-43.23%`, Calmar `0.3994`.

Interpretation: `evo02` is the performance-first/most-often-ahead candidate, while `evo05` is the strongest average relative-equity candidate. The best clean `SPY` underlying-signal candidate remains `evo01`; the strongest overall economic candidate uses `SSO` self-regime, so it carries the same conceptual caveat identified in the prior QLD audit `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.5-7]`.

No candidate is deploy-authorized. These are discovery results only until OOS/FWD/WF/bootstrap/PBO/DSR validation is run with cumulative trial accounting `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Plots

### Equity

![Equity](ga_consolidated/plots/comparison_equity.png)

### Relative Equity vs SPY

![Relative equity vs SPY](ga_consolidated/plots/comparison_relative_to_spy.png)

### Drawdown

![Drawdown](ga_consolidated/plots/comparison_drawdown.png)

## Quick Rankings

### Candidate Metrics

| label                            |   cagr |   sharpe |   sortino |     mdd |   calmar |   end_rel_to_benchmark |
|:---------------------------------|-------:|---------:|----------:|--------:|---------:|-----------------------:|
| evo05_diversity_low_corr best    | 0.1726 |   0.8058 |    1.1487 | -0.4323 |   0.3994 |                 7.6479 |
| evo06_conservative_drawdown best | 0.1514 |   0.7895 |    1.0614 | -0.3624 |   0.4178 |                 3.6617 |
| evo03_sso_self_balanced best     | 0.1671 |   0.7745 |    1.0033 | -0.3904 |   0.4280 |                 6.3122 |
| evo01_spy_sso_repair best        | 0.1671 |   0.7542 |    0.9738 | -0.3586 |   0.4661 |                 6.3255 |
| evo04_execution_lag_robust best  | 0.1547 |   0.7419 |    0.9625 | -0.4195 |   0.3688 |                 4.1095 |
| evo02_spy_upro_performance best  | 0.2088 |   0.6918 |    0.8628 | -0.6921 |   0.3016 |                25.9480 |

### Relative Equity Overall Scores

| label                            |   pct_above_score |   mean_relative_equity_score |   n_monthly_windows |
|:---------------------------------|------------------:|-----------------------------:|--------------------:|
| evo02_spy_upro_performance best  |            0.8378 |                       1.7258 |           2293.0000 |
| evo05_diversity_low_corr best    |            0.8084 |                       1.7681 |           2293.0000 |
| evo03_sso_self_balanced best     |            0.7813 |                       1.4924 |           2293.0000 |
| evo01_spy_sso_repair best        |            0.7485 |                       1.4805 |           2293.0000 |
| evo04_execution_lag_robust best  |            0.7452 |                       1.3767 |           2293.0000 |
| LRS SPY->SSO                     |            0.6956 |                       1.1281 |           2293.0000 |
| evo06_conservative_drawdown best |            0.6908 |                       1.3457 |           2293.0000 |
| LRS SPY->UPRO                    |            0.6758 |                       1.2717 |           2293.0000 |
| SSO buy_hold                     |            0.6276 |                       1.1387 |           2293.0000 |
| UPRO buy_hold                    |            0.5321 |                       1.2157 |           2293.0000 |

## Evolution Manifests

| name                        | objective             |   seed |   evaluated_unique |   generations |   elapsed_minutes | best_label                                                  | best_signal_asset   |   best_fitness |   best_sortino |   best_cagr |   best_sharpe |   best_mdd |   best_calmar |   best_corr_to_spy | beats_spy_economic   |
|:----------------------------|:----------------------|-------:|-------------------:|--------------:|------------------:|:------------------------------------------------------------|:--------------------|---------------:|---------------:|------------:|--------------:|-----------:|--------------:|-------------------:|:---------------------|
| evo05_diversity_low_corr    | diversity_low_corr    |   1091 |               1424 |            29 |            3.0016 | SSO_s75_225_vw10_vt0.25_ar20_k3_T20D150_nw0.00_rw1.00_z0.75 | SSO                 |         5.8659 |         1.1487 |      0.1726 |        0.8058 |    -0.4323 |        0.3994 |             0.2631 | True                 |
| evo06_conservative_drawdown | conservative_drawdown |   2091 |               1253 |            28 |            2.5989 | SSO_s75_225_vw21_vt0.30_ar20_k3_T20D45_nw0.00_rw0.50_z0.50  | SSO                 |         3.2217 |         1.0614 |      0.1514 |        0.7895 |    -0.3624 |        0.4178 |             0.3655 | True                 |
| evo04_execution_lag_robust  | execution_lag_robust  |   4091 |               1109 |            21 |            6.5503 | SSO_s150_180_vw42_vt0.45_ar40_k3_T15D60_nw0.00_rw0.00_z0.50 | SSO                 |         4.4965 |         1.0101 |      0.1648 |        0.7756 |    -0.4534 |        0.3881 |             0.4887 | True                 |
| evo03_sso_self_balanced     | sso_self_balanced     |   3091 |               1172 |            28 |            2.4414 | SSO_s150_225_vw42_vt0.45_ar40_k3_T60D45_nw0.00_rw1.00_z0.50 | SSO                 |         4.2758 |         1.0033 |      0.1671 |        0.7745 |    -0.3904 |        0.4280 |             0.4927 | True                 |
| evo01_spy_sso_repair        | spy_sso_repair        |   1091 |               1134 |            27 |            2.4132 | SPY_s75_225_vw21_vt0.30_ar40_k3_T30D60_nw0.00_rw0.50_z0.50  | SPY                 |         3.5102 |         0.9738 |      0.1671 |        0.7542 |    -0.3586 |        0.4661 |             0.5340 | True                 |
| evo02_spy_upro_performance  | spy_upro_performance  |   2091 |                916 |            21 |            1.8969 | SPY_s20_200_vw63_vt0.50_ar60_k2_T10D120_nw0.50_rw1.00_z0.25 | SPY                 |         4.1845 |         0.8628 |      0.2088 |        0.6918 |    -0.6921 |        0.3016 |             0.7936 | False                |

## Candidate vs Benchmarks

| label                            |   cagr |   sharpe |   sortino |     mdd |   calmar |   end_mult |   end_rel_to_benchmark |   pct_above_benchmark |
|:---------------------------------|-------:|---------:|----------:|--------:|---------:|-----------:|-----------------------:|----------------------:|
| evo05_diversity_low_corr best    | 0.1726 |   0.8058 |    1.1487 | -0.4323 |   0.3994 |   610.7372 |                 7.6479 |                1.0000 |
| evo06_conservative_drawdown best | 0.1514 |   0.7895 |    1.0614 | -0.3624 |   0.4178 |   292.4097 |                 3.6617 |                1.0000 |
| evo03_sso_self_balanced best     | 0.1671 |   0.7745 |    1.0033 | -0.3904 |   0.4280 |   504.0692 |                 6.3122 |                1.0000 |
| evo01_spy_sso_repair best        | 0.1671 |   0.7542 |    0.9738 | -0.3586 |   0.4661 |   505.1312 |                 6.3255 |                1.0000 |
| evo04_execution_lag_robust best  | 0.1547 |   0.7419 |    0.9625 | -0.4195 |   0.3688 |   328.1729 |                 4.1095 |                1.0000 |
| evo02_spy_upro_performance best  | 0.2088 |   0.6918 |    0.8628 | -0.6921 |   0.3016 |  2072.1159 |                25.9480 |                0.9491 |
| SPY buy_hold                     | 0.1149 |   0.6819 |    0.8418 | -0.5514 |   0.2083 |    79.8565 |                 1.0000 |                0.0000 |
| LRS SPY->SSO                     | 0.1388 |   0.6643 |    0.7586 | -0.5167 |   0.2686 |   187.5242 |                 2.3483 |                0.9890 |
| LRS SPY->UPRO                    | 0.1640 |   0.6048 |    0.6907 | -0.7120 |   0.2303 |   452.7404 |                 5.6694 |                0.9957 |
| SSO buy_hold                     | 0.1459 |   0.5564 |    0.6889 | -0.8827 |   0.1653 |   241.1824 |                 3.0202 |                0.8514 |
| UPRO buy_hold                    | 0.1351 |   0.5145 |    0.6375 | -0.9831 |   0.1374 |   164.4419 |                 2.0592 |                0.4258 |

## GA Candidate Rolling Windows

| label                            |   3y_min |   5y_min |   10y_min |   15y_min |
|:---------------------------------|---------:|---------:|----------:|----------:|
| evo01_spy_sso_repair best        |  -0.0998 |  -0.0119 |    0.0251 |    0.0844 |
| evo02_spy_upro_performance best  |  -0.1890 |  -0.1147 |   -0.0265 |    0.0845 |
| evo03_sso_self_balanced best     |  -0.0948 |  -0.0310 |    0.0348 |    0.0847 |
| evo04_execution_lag_robust best  |  -0.1117 |  -0.0404 |    0.0096 |    0.0883 |
| evo05_diversity_low_corr best    |  -0.0969 |   0.0048 |    0.0397 |    0.0911 |
| evo06_conservative_drawdown best |  -0.0703 |  -0.0158 |    0.0250 |    0.0969 |

## Relative Equity Method

Definition: for every possible monthly-ended rolling window, strategy and `SPY buy_hold` are rebased to 1 at the window start. `pct_above_score` is the average fraction of days where strategy equity is above SPY. `mean_relative_equity_score` is the average within-window strategy/SPY equity ratio. Overall score weights horizons as `1y=5%`, `3y=10%`, `5y=15%`, `10y=20%`, `15y=25%`, `20y=25%`.

### Pct Above By Horizon

| label                            |     1y |     3y |     5y |    10y |    15y |    20y |   overall |
|:---------------------------------|-------:|-------:|-------:|-------:|-------:|-------:|----------:|
| evo02_spy_upro_performance best  | 0.6413 | 0.6900 | 0.7785 | 0.8535 | 0.8876 | 0.9093 |    0.8378 |
| evo05_diversity_low_corr best    | 0.5587 | 0.6200 | 0.6915 | 0.7680 | 0.8907 | 0.9536 |    0.8084 |
| evo03_sso_self_balanced best     | 0.5753 | 0.5881 | 0.6379 | 0.7521 | 0.8701 | 0.9203 |    0.7813 |
| evo01_spy_sso_repair best        | 0.5768 | 0.5618 | 0.6116 | 0.7128 | 0.8234 | 0.8934 |    0.7485 |
| evo04_execution_lag_robust best  | 0.5474 | 0.5575 | 0.5977 | 0.7099 | 0.8359 | 0.8859 |    0.7452 |
| LRS SPY->SSO                     | 0.5744 | 0.5945 | 0.6427 | 0.6961 | 0.7249 | 0.7625 |    0.6956 |
| evo06_conservative_drawdown best | 0.5278 | 0.5333 | 0.5388 | 0.6559 | 0.7813 | 0.8150 |    0.6908 |
| LRS SPY->UPRO                    | 0.5718 | 0.6076 | 0.6504 | 0.6821 | 0.6951 | 0.7147 |    0.6758 |
| SSO buy_hold                     | 0.6455 | 0.6802 | 0.6860 | 0.6258 | 0.6176 | 0.5795 |    0.6276 |
| UPRO buy_hold                    | 0.6211 | 0.6452 | 0.6481 | 0.5570 | 0.4882 | 0.4236 |    0.5321 |

### Mean Relative Equity By Horizon

| label                            |     1y |     3y |     5y |    10y |    15y |    20y |   overall |
|:---------------------------------|-------:|-------:|-------:|-------:|-------:|-------:|----------:|
| evo05_diversity_low_corr best    | 1.0358 | 1.1086 | 1.2028 | 1.4900 | 1.9634 | 2.5446 |    1.7681 |
| evo02_spy_upro_performance best  | 1.0549 | 1.1440 | 1.2539 | 1.5769 | 1.9382 | 2.2826 |    1.7258 |
| evo03_sso_self_balanced best     | 1.0306 | 1.0831 | 1.1425 | 1.3286 | 1.6237 | 1.9581 |    1.4924 |
| evo01_spy_sso_repair best        | 1.0305 | 1.0812 | 1.1389 | 1.3163 | 1.5970 | 1.9502 |    1.4805 |
| evo04_execution_lag_robust best  | 1.0256 | 1.0698 | 1.1196 | 1.2714 | 1.4995 | 1.6856 |    1.3767 |
| evo06_conservative_drawdown best | 1.0265 | 1.0705 | 1.1139 | 1.2606 | 1.4711 | 1.6015 |    1.3457 |
| LRS SPY->UPRO                    | 1.0405 | 1.1035 | 1.1651 | 1.2958 | 1.3564 | 1.3453 |    1.2717 |
| UPRO buy_hold                    | 1.0378 | 1.1088 | 1.1969 | 1.3935 | 1.3378 | 1.0409 |    1.2157 |
| SSO buy_hold                     | 1.0199 | 1.0573 | 1.1001 | 1.1891 | 1.1966 | 1.1198 |    1.1387 |
| LRS SPY->SSO                     | 1.0192 | 1.0473 | 1.0733 | 1.1256 | 1.1612 | 1.1838 |    1.1281 |

## SPY-Signal vs SSO-Self-Signal

| Signal family | Best candidate | Read |
|---|---|---|
| `SPY` | `evo01_spy_sso_repair best`: CAGR 16.71%, Sortino 0.9738, MDD -35.86% | Cleaner underlying-regime interpretation. |
| `SSO` | `evo05_diversity_low_corr best`: CAGR 17.26%, Sortino 1.1487, MDD -43.23% | Stronger economics here, but LETF self-regime caveat. |

The SPY-underlying candidate is conceptually cleaner because the regime is measured on the unlevered S&P 500 proxy `[leverage_for_the_long_run, p.13]`. The SSO candidate must be labeled as LETF self-regime because SSO's own trend/volatility state drives exposure `[leverage_for_the_long_run, p.5-7]`.

## Files

- `reports/baseline/REPORT.md` for simple baselines.
- `reports/ga_consolidated/tables/comparison_metrics.csv` for metrics.
- `reports/ga_consolidated/tables/comparison_rolling_windows.csv` for rolling windows.
- `reports/ga_consolidated/tables/rolling_relative_scores.csv` for monthly-ended relative-equity scores.
- `reports/ga_consolidated/plots/` for equity, drawdown and relative-equity plots.
