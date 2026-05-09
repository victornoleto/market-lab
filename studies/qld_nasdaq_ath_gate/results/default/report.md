# QLD Nasdaq ATH Gate Report

## Strategy

- Rule: hold `QLD` when `QQQ` is above `85%` of its trailing `46` weekly closes high-watermark; otherwise hold `CASHX`.
- Signal proxy: `QQQ` adjusted close as Nasdaq-100 ETF proxy; risk-on asset: `QLD`; risk-off asset: `CASHX`.
- Timing: weekly signal is forward-filled and shifted one trading day before allocation to avoid same-close look-ahead.
- Source rationale: leveraged equity above a risk gate and cash/T-bills below follows the LRS family `[leverage_for_the_long_run, p.13, p.21]`.
- High-watermark/breakout-style filters are a classic trend-following family `[trading_systems_methods, p.353]`.

## Result Summary

- Date range: `2007-05-04` to `2026-04-14`.
- Trade events: `26`.
- Strategy CAGR: `23.21%` vs QQQ `15.67%` vs QLD `23.48%`.
- Strategy MDD: `-49.33%` vs QQQ `-53.41%` vs QLD `-83.16%`.
- Strategy Sharpe: `0.776` vs QQQ `0.764` vs QLD `0.698`.
- Terminal wealth vs QQQ: `3.30x`; vs QLD: `0.96x`.

## Metrics

| metric | strategy | QQQ | QLD | CASHX |
|---|---:|---:|---:|---:|
| total_return | 5083.54% | 1469.04% | 5299.98% | 31.39% |
| cagr | 23.21% | 15.67% | 23.48% | 1.45% |
| mdd | -49.33% | -53.41% | -83.16% | -0.00% |
| sharpe | 0.776 | 0.764 | 0.698 | 12.805 |
| sortino | 1.075 | 1.088 | 0.990 | 22401.630 |
| calmar | 0.471 | 0.293 | 0.282 | 4074.804 |
| vol_annual | 34.74% | 22.32% | 44.40% | 0.11% |
| best_day | 19.05% | 12.16% | 24.59% | 0.02% |
| worst_day | -18.51% | -11.98% | -24.28% | -0.00% |

## Rolling Windows

Rolling windows test whether the full-period result survives different start/end regimes `[trading_systems_methods, ch.21]`.

|   window_years |     n_obs |   strategy_median_cagr |   qqq_median_cagr |   qld_median_cagr |   win_rate_vs_qqq |   win_rate_vs_qld |   median_edge_vs_qqq |   median_edge_vs_qld |   worst_edge_vs_qqq |   worst_edge_vs_qld |
|---------------:|----------:|-----------------------:|------------------:|------------------:|------------------:|------------------:|---------------------:|---------------------:|--------------------:|--------------------:|
|         1.0000 | 4514.0000 |                 0.2910 |            0.2042 |            0.3686 |            0.6593 |            0.4703 |               0.1034 |              -0.0000 |             -0.3833 |             -1.6241 |
|         3.0000 | 4010.0000 |                 0.2703 |            0.1766 |            0.3170 |            0.9426 |            0.4955 |               0.0844 |               0.0000 |             -0.1385 |             -0.4718 |
|         5.0000 | 3506.0000 |                 0.2854 |            0.1815 |            0.3144 |            0.9894 |            0.2824 |               0.0914 |              -0.0293 |             -0.0267 |             -0.2748 |
|        10.0000 | 2246.0000 |                 0.2760 |            0.1835 |            0.3056 |            1.0000 |            0.1768 |               0.0967 |              -0.0433 |              0.0387 |             -0.1494 |

## Plots

![Equity](plots/equity.png)

![Drawdown](plots/drawdown.png)

![Signal Line](plots/signal_line.png)

![Rolling Sharpe](plots/rolling_sharpe_1y.png)

![Rolling Windows](plots/rolling_windows_1_3_5_10y.png)

## Recent Trades

| date       | target   |   risk_on_weight |
|:-----------|:---------|-----------------:|
| 2020-03-16 | CASHX    |                0 |
| 2020-04-20 | QLD      |                1 |
| 2022-02-22 | CASHX    |                0 |
| 2022-02-28 | QLD      |                1 |
| 2022-03-07 | CASHX    |                0 |
| 2022-03-21 | QLD      |                1 |
| 2022-04-25 | CASHX    |                0 |
| 2023-02-06 | QLD      |                1 |
| 2023-02-13 | CASHX    |                0 |
| 2023-02-21 | QLD      |                1 |
| 2025-04-07 | CASHX    |                0 |
| 2025-04-28 | QLD      |                1 |

## Caveats

- This is a fast diagnostic, not a deployable strategy verdict.
- QQQ is used as a Nasdaq-100 ETF proxy; the test is limited by QLD real-history overlap from 2006 onward.
- Costs, taxes, slippage, market impact and operational execution are not modeled.
- No PBO, DSR, walk-forward, bootstrap or cross-library gate is run here, so mandate promotion is not implied.
- CASHX is a testfol.io cash/T-bill proxy and not a broker-specific cash sweep implementation.
