# Stage 4 Equity vs Benchmarks

Status: economic-first comparison. QQQ is used as tradable NDX proxy. The table includes both Tiingo QQQ->QLD/CASH proxies and canonical testfolio anchor returns sliced to the same window.

Window: `2010-02-12` to `2026-04-14` (4,066 bars)
Off leg: `CASH_USD`
Extra lag days: `1`
Stage 4 base rule: `sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70`, `k=3`

## Metrics

| label                       |   sortino |   cagr |   sharpe |     mdd |   calmar |   end_mult |   end_rel_to_benchmark |   pct_above_benchmark |
|:----------------------------|----------:|-------:|---------:|--------:|---------:|-----------:|-----------------------:|----------------------:|
| Stage4 QLD base vote        |    1.4209 | 0.3626 |   1.1900 | -0.3754 |   0.9659 |   147.2869 |                17.1449 |                1.0000 |
| Stage4 TQQQ base vote       |    1.4124 | 0.5300 |   1.1849 | -0.5103 |   1.0386 |   955.0132 |               111.1684 |                1.0000 |
| SPY buy_hold                |    1.0627 | 0.1426 |   0.8629 | -0.3370 |   0.4231 |     8.5907 |                 1.0000 |                0.0000 |
| NDX/QQQ buy_hold            |    1.2212 | 0.1900 |   0.9477 | -0.3512 |   0.5410 |    16.5624 |                 1.9279 |                1.0000 |
| T3d-K2 proxy QLD/CASH       |    1.1052 | 0.2805 |   0.8862 | -0.4553 |   0.6162 |    54.0430 |                 6.2909 |                0.8721 |
| iter030-like proxy QLD/CASH |    1.1107 | 0.2827 |   0.8895 | -0.4553 |   0.6209 |    55.5115 |                 6.4618 |                0.8721 |
| T3d-K2 canonical sliced     |    1.2191 | 0.2789 |   0.9233 | -0.6450 |   0.4325 |    52.9700 |                 6.1660 |                1.0000 |
| iter030 canonical sliced    |    1.1933 | 0.3427 |   1.0025 | -0.4255 |   0.8053 |   116.1091 |                13.5157 |                1.0000 |

## Relative Summary

|                             |   end_equity |   end_vs_spy |   end_vs_ndx_qqq |   pct_days_above_spy |   pct_days_above_ndx_qqq |
|:----------------------------|-------------:|-------------:|-----------------:|---------------------:|-------------------------:|
| Stage4 QLD base vote        |     147.2869 |      17.1449 |           8.8929 |               0.9978 |                   0.9914 |
| Stage4 TQQQ base vote       |     955.0132 |     111.1684 |          57.6617 |               0.9988 |                   0.9975 |
| SPY buy_hold                |       8.5907 |       1.0000 |           0.5187 |               0.0000 |                   0.0015 |
| NDX/QQQ buy_hold            |      16.5624 |       1.9279 |           1.0000 |               0.9985 |                   0.0000 |
| T3d-K2 proxy QLD/CASH       |      54.0430 |       6.2909 |           3.2630 |               0.8674 |                   0.8404 |
| iter030-like proxy QLD/CASH |      55.5115 |       6.4618 |           3.3517 |               0.8674 |                   0.8404 |
| T3d-K2 canonical sliced     |      52.9700 |       6.1660 |           3.1982 |               0.9985 |                   0.9973 |
| iter030 canonical sliced    |     116.1091 |      13.5157 |           7.0104 |               0.9990 |                   0.9995 |

## Plots

![Equity curves](plots/equity_curves.png)

![Relative to SPY](plots/relative_to_spy.png)

![Relative to NDX/QQQ](plots/relative_to_ndx_qqq.png)

## Method Notes

- Stage 4 strategies use the same `CASH_USD + extra_lag_days=1` timing from the regime bridge.
- T3d-K2 proxy uses the QQQ T3d-K2 vote into QLD/CASH with the same extra lag.
- iter030-like proxy adds the documented T35D60 rearm and LRS1.20 multiplier to the T3d-K2 proxy `[leverage_for_the_long_run, p.5-7]`.
- Canonical sliced rows come directly from the preserved `letf_rotation_hunt` return CSVs and are included to avoid conflating proxies with original anchors.
