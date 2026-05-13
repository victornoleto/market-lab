# Iter030 T/D Sensitivity and Study Comparison

Status: final constrained sensitivity after the iter030 parameter GA. This is explanatory, not a new optimization branch.

Window: `1986-01-03` to `2026-04-17` (10,150 bars)
T values: `20,35,45`
D values: `60,90,120`

## Verdict

`T20D120` remains the best CAGR/terminal-equity variant in this local T/D grid, but `T20D90` is the best balanced variant by Sortino with nearly identical CAGR and the same full-period MDD. Neither is a validated winner: prior formal validation of the GA strict-Pareto set still failed DSR and PBO. Treat `T20D120` as the performance-first sensitivity and `T20D90` as a local explanatory challenger, not as deployable replacements `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.

## T/D Grid

| td_label   |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |   t_crash |   d_arm | is_ga_winner   |
|:-----------|----------:|-------:|---------:|--------:|---------:|------------:|----------:|--------:|:---------------|
| T20D90     |    1.2278 | 0.3899 |   0.9752 | -0.5548 |   0.7029 | 574998.3713 |        20 |      90 | False          |
| T35D90     |    1.2251 | 0.3824 |   0.9781 | -0.5548 |   0.6894 | 462190.4786 |        35 |      90 | False          |
| T45D120    |    1.2183 | 0.3764 |   0.9699 | -0.5548 |   0.6785 | 387833.5195 |        45 |     120 | False          |
| T35D120    |    1.2177 | 0.3871 |   0.9744 | -0.5548 |   0.6977 | 528830.5971 |        35 |     120 | False          |
| T45D90     |    1.2147 | 0.3704 |   0.9670 | -0.5548 |   0.6677 | 325196.6993 |        45 |      90 | False          |
| T20D60     |    1.2100 | 0.3729 |   0.9623 | -0.5548 |   0.6721 | 349386.7350 |        20 |      60 | False          |
| T20D120    |    1.2074 | 0.3901 |   0.9606 | -0.5548 |   0.7032 | 577835.2849 |        20 |     120 | True           |
| T35D60     |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |        35 |      60 | False          |
| T45D60     |    1.1948 | 0.3576 |   0.9524 | -0.5548 |   0.6446 | 222525.2054 |        45 |      60 | False          |

## Strategy Comparison

| label                       |   sortino |   cagr |   sharpe |     mdd |   calmar |    end_mult |   pct_above_benchmark |
|:----------------------------|----------:|-------:|---------:|--------:|---------:|------------:|----------------------:|
| Stage3 shared QLD           |    1.3747 | 0.3205 |   0.9826 | -0.5781 |   0.5543 |  72857.4343 |                1.0000 |
| Stage3 shared TQQQ          |    1.2680 | 0.4026 |   0.9510 | -0.6424 |   0.6267 | 828855.8110 |                1.0000 |
| T3d-K2 canonical            |    1.2575 | 0.3106 |   0.9187 | -0.6450 |   0.4816 |  53860.6336 |                1.0000 |
| iter030 T20D120 candidate   |    1.2074 | 0.3901 |   0.9606 | -0.5548 |   0.7032 | 577835.2849 |                1.0000 |
| iter030 canonical           |    1.2073 | 0.3666 |   0.9624 | -0.5548 |   0.6608 | 290556.7104 |                1.0000 |
| Stage4-inside iter030 turbo |    1.0838 | 0.3846 |   0.8721 | -0.6454 |   0.5959 | 492025.4559 |                1.0000 |
| Stage4 QLD base vote        |    0.9074 | 0.1938 |   0.6685 | -0.7007 |   0.2766 |   1255.5564 |                0.9544 |
| QQQ buy_hold                |    0.8660 | 0.1458 |   0.6583 | -0.8297 |   0.1757 |    240.2137 |                0.8537 |
| SPY buy_hold                |    0.8418 | 0.1149 |   0.6819 | -0.5514 |   0.2083 |     79.8565 |                0.0000 |
| Stage4 TQQQ base vote       |    0.8328 | 0.2148 |   0.6374 | -0.8769 |   0.2449 |   2531.7669 |                0.8215 |

## Rolling Minimum CAGR

| label                       |   min_3y_cagr |   min_5y_cagr |   min_10y_cagr |   min_15y_cagr |
|:----------------------------|--------------:|--------------:|---------------:|---------------:|
| QQQ buy_hold                |       -0.4016 |       -0.2083 |        -0.0818 |        -0.0013 |
| SPY buy_hold                |       -0.1724 |       -0.0832 |        -0.0410 |         0.0354 |
| Stage3 shared QLD           |       -0.0290 |        0.0504 |         0.1400 |         0.1733 |
| Stage3 shared TQQQ          |       -0.0766 |        0.0734 |         0.1974 |         0.2115 |
| Stage4 QLD base vote        |       -0.2322 |       -0.0772 |        -0.0096 |         0.0666 |
| Stage4 TQQQ base vote       |       -0.4146 |       -0.1757 |        -0.0830 |         0.0369 |
| Stage4-inside iter030 turbo |       -0.1989 |       -0.0414 |         0.0595 |         0.1804 |
| T3d-K2 canonical            |       -0.1552 |       -0.0089 |         0.0541 |         0.1495 |
| iter030 T20D120 candidate   |       -0.1658 |        0.0194 |         0.1018 |         0.1859 |
| iter030 canonical           |       -0.1527 |        0.0148 |         0.0876 |         0.1689 |

## Plots

![Comparison equity](plots/comparison_equity.png)

![Relative to iter030](plots/comparison_relative_to_iter030.png)

![10-year rolling CAGR](plots/comparison_rolling_10y.png)

![T/D CAGR heatmap](plots/td_heatmap_cagr.png)

![T/D Sortino heatmap](plots/td_heatmap_sortino.png)

![T/D MDD heatmap](plots/td_heatmap_mdd.png)

## Interpretation

The local grid shows that longer rearm persistence (`D90`/`D120`) is the main source of the GA improvement, especially when paired with the faster `T20` crash trigger. That is a plausible economic mechanism, but it is also a small parametric move selected on the same long history. Since the honest validation of the strict Pareto candidates closed 0/7 PASS, the correct conclusion is to stop this optimization branch and keep iter030 as the core anchor.
