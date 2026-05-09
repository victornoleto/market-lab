# QLD Nasdaq ATH Gate Report

## Strategy

- Rule: hold `QQQSIM?L=2` when `QQQSIM` is above `85%` of its trailing `46` weekly closes high-watermark; otherwise hold `CASHX`.
- Signal proxy: `QQQSIM` long-history Nasdaq-100 proxy from testfol.io; risk-on asset: `QQQSIM?L=2`; comparison leverage: `QQQSIM?L=3`; risk-off asset: `CASHX`.
- Timing: weekly signal is forward-filled and shifted one trading day before allocation to avoid same-close look-ahead.
- Source rationale: leveraged equity above a risk gate and cash/T-bills below follows the LRS family `[leverage_for_the_long_run, p.13, p.21]`.
- High-watermark/breakout-style filters are a classic trend-following family `[trading_systems_methods, p.353]`.

## Result Summary

- Date range: `1986-11-14` to `2026-04-17`.
- Trade events: `54`.
- Strategy CAGR: `23.42%` vs QQQSIM `14.66%` vs QQQSIM?L=2 `17.44%` vs QQQSIM?L=3 `12.28%`.
- Strategy MDD: `-63.67%` vs QQQSIM `-82.97%` vs QQQSIM?L=2 `-98.85%` vs QQQSIM?L=3 `-99.98%`.
- Strategy Sharpe: `0.744` vs QQQSIM `0.658` vs QQQSIM?L=2 `0.570` vs QQQSIM?L=3 `0.541`.
- Terminal wealth vs QQQSIM: `18.15x`; vs QQQSIM?L=2: `7.07x`; vs QQQSIM?L=3: `41.55x`.

## Metrics

| metric | Strategy | QQQSIM | QQQSIM?L=2 | QQQSIM?L=3 | CASHX |
|---|---:|---:|---:|---:|---:|
| total_return | 398635.18% | 21870.78% | 56325.24% | 9497.00% | 231.89% |
| cagr | 23.42% | 14.66% | 17.44% | 12.28% | 3.09% |
| mdd | -63.67% | -82.97% | -98.85% | -99.98% | -0.00% |
| sharpe | 0.744 | 0.658 | 0.570 | 0.541 | 20.109 |
| sortino | 1.045 | 0.944 | 0.815 | 0.772 | 68205.780 |
| calmar | 0.368 | 0.177 | 0.176 | 0.123 | 8664.216 |
| vol_annual | 38.21% | 25.88% | 51.76% | 77.64% | 0.15% |
| best_day | 24.69% | 16.84% | 33.65% | 50.46% | 0.04% |
| worst_day | -30.19% | -15.08% | -30.19% | -45.30% | -0.00% |

## Rolling Windows

Rolling windows test whether the full-period result survives different start/end regimes `[trading_systems_methods, ch.21]`.

|   window_years |     n_obs |   strategy_median_cagr |   signal_median_cagr |   risk_on_median_cagr |   comparison_median_cagr |   win_rate_vs_signal |   win_rate_vs_risk_on |   win_rate_vs_comparison |   median_edge_vs_signal |   median_edge_vs_risk_on |   median_edge_vs_comparison |   worst_edge_vs_signal |   worst_edge_vs_risk_on |   worst_edge_vs_comparison |
|---------------:|----------:|-----------------------:|---------------------:|----------------------:|-------------------------:|---------------------:|----------------------:|-------------------------:|------------------------:|-------------------------:|----------------------------:|-----------------------:|------------------------:|---------------------------:|
|         1.0000 | 9678.0000 |                 0.2125 |               0.1771 |                0.2755 |                   0.3300 |               0.6329 |                0.3641 |                   0.3413 |                  0.0736 |                  -0.0000 |                     -0.1174 |                -0.4702 |                 -1.6290 |                    -3.6623 |
|         3.0000 | 9174.0000 |                 0.2403 |               0.1593 |                0.2561 |                   0.2968 |               0.8479 |                0.3680 |                   0.4004 |                  0.0800 |                  -0.0000 |                     -0.0587 |                -0.2109 |                 -0.5184 |                    -1.3299 |
|         5.0000 | 8670.0000 |                 0.2429 |               0.1604 |                0.2363 |                   0.2479 |               0.9368 |                0.4125 |                   0.4262 |                  0.0890 |                  -0.0108 |                     -0.0288 |                -0.1139 |                 -0.2978 |                    -0.7546 |
|        10.0000 | 7410.0000 |                 0.2670 |               0.1417 |                0.1727 |                   0.1599 |               0.9996 |                0.5965 |                   0.5829 |                  0.0997 |                   0.0264 |                      0.0324 |                -0.0014 |                 -0.1786 |                    -0.3389 |

## Plots

![Equity](plots/equity.png)

![Drawdown](plots/drawdown.png)

![Signal Line](plots/signal_line.png)

![Rolling Sharpe](plots/rolling_sharpe_1y.png)

![Rolling Windows](plots/rolling_windows_1_3_5_10y.png)

## Recent Trades

| date       | target     |   risk_on_weight |
|:-----------|:-----------|-----------------:|
| 2020-03-16 | CASHX      |                0 |
| 2020-04-20 | QQQSIM?L=2 |                1 |
| 2022-02-22 | CASHX      |                0 |
| 2022-02-28 | QQQSIM?L=2 |                1 |
| 2022-03-07 | CASHX      |                0 |
| 2022-03-21 | QQQSIM?L=2 |                1 |
| 2022-04-25 | CASHX      |                0 |
| 2023-02-06 | QQQSIM?L=2 |                1 |
| 2023-02-13 | CASHX      |                0 |
| 2023-02-21 | QQQSIM?L=2 |                1 |
| 2025-04-07 | CASHX      |                0 |
| 2025-04-28 | QQQSIM?L=2 |                1 |

## Caveats

- This is a fast diagnostic, not a deployable strategy verdict.
- testfol.io `QQQSIM` extends Nasdaq-100 proxy history before live QQQ/QLD/TQQQ inception; pre-inception bars are modelled approximations, not directly tradeable history.
- Leveraged specs such as `QQQSIM?L=2` and `QQQSIM?L=3` are resolved to local cache aliases (`QLDSIM`, `TQQQSIM`) when available.
- Costs, taxes, slippage, market impact and operational execution are not modeled.
- No PBO, DSR, walk-forward, bootstrap or cross-library gate is run here, so mandate promotion is not implied.
- CASHX is a testfol.io cash/T-bill proxy and not a broker-specific cash sweep implementation.
