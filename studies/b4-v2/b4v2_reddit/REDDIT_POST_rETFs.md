# Building a diversified return-stacked ETF portfolio, step by step

This is not financial advice. I am posting this as a research process, not as a recommendation. The benchmark is **100% SPY**.

The basic idea is to use capital-efficient ETFs to keep equity exposure while adding diversifiers: gold, managed futures and long-duration Treasuries.

The charts are embedded inline below in the same order I would upload them to a Reddit gallery.

## The Core Result

I started with an equal-weight B4-style portfolio:

```text
25% NTSX / 25% GDE / 25% RSST / 25% ZROZ
```

Then I tested nearby allocations and ended up with this simpler core:

```text
35% GDE / 40% RSST / 25% ZROZ
```

What the sleeves represent:

- `GDE`: U.S. stocks + gold
- `RSST`: U.S. stocks + managed futures
- `ZROZ`: long-duration zero-coupon Treasuries

Backtest context:

| Portfolio               | Window                 | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   |
|:------------------------|:-----------------------|:-------|:--------|---------:|---------:|:-----------|
| 100% SPY                | 1988-01-04..2026-04-17 | 11.46% | -55.14% |    0.691 |    0.208 | 64x        |
| B4 original 25/25/25/25 | 1988-01-04..2026-04-17 | 14.43% | -27.92% |    1.018 |    0.517 | 174x       |
| B4-v2 35/40/25          | 1988-01-04..2026-04-17 | 15.70% | -29.94% |    1.04  |    0.524 | 265x       |

The main attraction is not just higher CAGR. It is that the drawdown was much lower than SPY in the tested history.

Chart 1 shows the long-sample equity curves. This is the high-level result before getting into implementation details.

![1988+ equity curves: SPY vs B4 equal-weight vs B4-v2](plots/01_full_equity_log.png)

Chart 2 shows relative wealth versus SPY. This is a more direct way to see whether the portfolio actually compounded ahead of the benchmark over time.

![1988+ relative wealth vs SPY](plots/02_full_equity_vs_spy.png)

## Implementation Variants

The clean research version is:

```text
35% GDE / 40% RSST / 25% ZROZ
```

For implementation, I am considering two changes.

First, split managed futures exposure:

```text
40% RSST  ->  20% RSST / 20% CTAP
```

This is not meant to change the thesis. It is just diversification across managed-futures models/managers.

Second, maybe add RSSX as part of the gold sleeve.

RSSX is not simply a static BTC fund. It is closer to:

```text
100% U.S. stocks + 100% Gold/BTC volatility-balanced sleeve
```

I modeled it with a simple risk-parity proxy and intentionally nerfed BTC returns, because using raw historical BTC CAGR is too optimistic.

Post-2010 comparison, with BTC drift reduced to a 10% CAGR assumption:

| Portfolio                                             | Window                 | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   |
|:------------------------------------------------------|:-----------------------|:-------|:--------|---------:|---------:|:-----------|
| 100% SPY                                              | 2010-10-18..2026-05-21 | 14.69% | -33.69% |    0.891 |    0.436 | 8.4x       |
| 35 GDE / 40 RSST / 25 ZROZ                            | 2010-10-18..2026-05-21 | 14.81% | -21.46% |    1.062 |    0.69  | 8.6x       |
| 35 GDE / 20 RSST / 20 CTAP / 25 ZROZ                  | 2010-10-18..2026-05-21 | 15.14% | -23.45% |    1.062 |    0.646 | 9.0x       |
| 25 GDE / 10 RSSX_RP / 20 RSST / 20 CTAP / 25 ZROZ     | 2010-10-18..2026-05-21 | 16.06% | -24.28% |    1.098 |    0.662 | 10.2x      |
| 17.5 GDE / 17.5 RSSX_RP / 20 RSST / 20 CTAP / 25 ZROZ | 2010-10-18..2026-05-21 | 16.73% | -25.28% |    1.115 |    0.662 | 11.1x      |

Approximate effective exposure by implementation:

| Version | US equity | MF Newfound | MF Simplify | Gold | BTC | ZROZ | Positive exposure | Gross leverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 35 GDE / 40 RSST / 25 ZROZ | 71.5% | 40.0% | 0.0% | 31.5% | 0.0% | 25.0% | 168.0% | 1.68x |
| 35 GDE / 20 RSST / 20 CTAP / 25 ZROZ | 71.5% | 20.0% | 20.0% | 31.5% | 0.0% | 25.0% | 168.0% | 1.68x |
| 25 GDE / 10 RSSX / 20 RSST / 20 CTAP / 25 ZROZ | 72.5% | 20.0% | 20.0% | 30.7% | 1.8% | 25.0% | 170.0% | 1.70x |
| 17.5 GDE / 17.5 RSSX / 20 RSST / 20 CTAP / 25 ZROZ | 73.3% | 20.0% | 20.0% | 30.2% | 3.1% | 25.0% | 171.5% | 1.72x |

For the RSSX rows, BTC and gold use the historical average BTC sleeve weight of roughly `17.6%` inside the RSSX Gold/BTC sleeve.

Chart 3 shows the same post-2010 implementation comparison as equity curves.

![Post-2010 implementation equity curves](plots/03_implementation_equity_log.png)

Chart 4 shows those variants as relative wealth versus SPY.

![Post-2010 implementation relative wealth vs SPY](plots/04_implementation_equity_vs_spy.png)

Chart 5 is the drawdown check. The implementation variants add complexity, so I want the risk cost visible, not hidden behind a higher CAGR row.

![Implementation drawdowns](plots/05_implementation_drawdowns.png)

## Rolling Check

The next two charts are the holding-period sanity check. The result is strongest over longer windows, but short rolling windows can still underperform SPY.

Chart 6 shows rolling relative wealth over 3/5/10/15-year windows.

![Rolling relative wealth 3/5/10/15](plots/06_rolling_relative_wealth_2x2.png)

Chart 7 shows the same idea as rolling CAGR spread versus SPY.

![Rolling CAGR spread 3/5/10/15](plots/07_rolling_cagr_spread_2x2.png)

## Where I Am Leaning

Cleanest version:

```text
35% GDE / 40% RSST / 25% ZROZ
```

More diversified implementation:

```text
25% GDE / 10% RSSX / 20% RSST / 20% CTAP / 25% ZROZ
```

More aggressive RSSX implementation:

```text
17.5% GDE / 17.5% RSSX / 20% RSST / 20% CTAP / 25% ZROZ
```

I prefer leading with the clean `35/40/25` version and treating RSSX as optional. The RSSX version may be attractive, but I do not want the thesis to depend on optimistic Bitcoin assumptions.

## Monte Carlo Sequence-Risk Simulation

I also ran a simple Monte Carlo sequence-risk simulation.

Method: 1,000 simulated 20-year paths using 21-trading-day block bootstrap. Returns were resampled in paired daily blocks across all portfolios, so each simulated path keeps the cross-portfolio co-movement from the historical data.

| Portfolio | p10 terminal | median terminal | p10 CAGR | median MDD | Prob. terminal < SPY |
|---|---:|---:|---:|---:|---:|
| 100% SPY | 3.17x | 7.93x | 5.93% | -35.62% | — |
| B4-v2 35/40/25 | 7.91x | 18.81x | 10.89% | -24.49% | 6.2% |
| B4 original 25/25/25/25 | 6.49x | 14.26x | 9.80% | -23.95% | 11.2% |

This is not a forecast and not a formal validation gate. It is a sequence-risk sanity check. The useful read is that the B4-v2 result is not just one lucky chronological ordering of the full sample `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

Chart 8 shows the Monte Carlo median paths, with 10th-90th percentile bands.

![Monte Carlo 20-year sequence-risk simulation](plots/08_monte_carlo_20y_sequence_risk.png)

## Caveats

- Simulated/proxy histories are not live ETF histories.
- Return-stacked ETFs use embedded leverage, even if the portfolio weights add to 100%.
- Taxes, fees, spreads, fund closure risk and tracking error matter.
- The RSSX comparison starts in 2010 because of Bitcoin data.
- This is research only, not a portfolio recommendation.

Would you keep the cleaner `35/40/25`, or use the RSSX/CTAP implementation variant?
