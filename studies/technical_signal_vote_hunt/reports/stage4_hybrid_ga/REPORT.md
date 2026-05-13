# Stage4 Constrained Hybrid GA

Status: economic-first GA search for a turbo filter that improves iter030 without worsening Sortino/MDD.

Population: 72
Generations: 35
Strict Pareto candidates in top 20: 0

## Iter030 Baseline

| label            |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |
|:-----------------|----------:|-------:|---------:|--------:|---------:|------------:|
| iter030_baseline |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |

## Top Candidates

| label                  |   fitness |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult | include_rearm   | require_stage4   | use_trend   | use_slope   | use_dd   |   dd_threshold | use_rv   |   rv_threshold | use_high_strength   |   weight |   lrs_factor |
|:-----------------------|----------:|----------:|-------:|---------:|--------:|---------:|------------:|:----------------|:-----------------|:------------|:------------|:---------|---------------:|:---------|---------------:|:--------------------|---------:|-------------:|
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.1000 | False    |         0.8000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.1000 | False    |         0.6000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.2500 | False    |         0.9000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.4000 | False    |         0.9000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.2500 | False    |         0.5000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.1000 | False    |         0.9000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.1000 | False    |         0.4000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.4000 | False    |         0.4000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.2500 | False    |         0.4000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.1500 | False    |         0.6000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.4000 | False    |         0.5000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.4000 | False    |         0.7000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.1000 | False    |         0.5000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.1000 | False    |         0.7000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.2000 | False    |         0.7000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.1500 | False    |         0.8000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.2000 | False    |         0.8000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.4000 | False    |         0.8000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.2500 | False    |         0.8000 | False               |   1.0000 |       1.2000 |
| ga_rearm_w1.00_lrs1.20 |    0.0000 |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 | True            | False            | False       | False       | False    |        -0.3000 | False    |         0.8000 | False               |   1.0000 |       1.2000 |

## Best By Generation

|   generation |   fitness |   sortino |   cagr |     mdd | label                  |
|-------------:|----------:|----------:|-------:|--------:|:-----------------------|
|           16 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           17 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           18 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           19 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           20 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           21 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           22 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           23 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           24 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           25 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           26 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           27 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           28 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           29 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           30 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           31 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           32 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           33 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           34 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |
|           35 |    0.0000 |    1.2073 | 0.3666 | -0.5548 | ga_rearm_w1.00_lrs1.20 |

## Plot

![Top equity curves](plots/top_equity_curves.png)
