# A return-stacked ETF portfolio I built step by step: from B4 equal-weight to GDE/RSST/ZROZ, then optional RSSX/CTAP

This is not financial advice. I am sharing the research process because I think the construction is more interesting than the final weights. All numbers below are backtests using simulated/proxy histories, so the usual caveats apply: pre-inception data, fund tracking, fees, taxes, and model risk.

The benchmark throughout is simple: **100% SPY buy-and-hold**.

The charts are embedded inline below in the same order I would upload them to a Reddit gallery.

## 1. Starting Point: B4 Equal Weight

The first version was the familiar return-stacked style allocation:

```text
25% NTSX / 25% GDE / 25% RSST / 25% ZROZ
```

The idea is simple:

- `NTSX`: S&P 500 + intermediate Treasuries
- `GDE`: S&P 500 + Gold
- `RSST`: S&P 500 + Managed Futures
- `ZROZ`: long-duration zero-coupon Treasuries

The point is not to maximize equity beta. It is to stack equity exposure with diversifiers that can help in different regimes.

Backtest context:

| Portfolio               | Window                 | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   |
|:------------------------|:-----------------------|:-------|:--------|---------:|---------:|:-----------|
| 100% SPY                | 1988-01-04..2026-04-17 | 11.46% | -55.14% |    0.691 |    0.208 | 64x        |
| B4 original 25/25/25/25 | 1988-01-04..2026-04-17 | 14.43% | -27.92% |    1.018 |    0.517 | 174x       |
| B4-v2 35/40/25          | 1988-01-04..2026-04-17 | 15.70% | -29.94% |    1.04  |    0.524 | 265x       |

The equal-weight B4 version already did what I wanted: higher CAGR than SPY and much lower max drawdown.

Chart 1 is the full-sample compounding view. This is the first sanity check: does the B4 idea actually compound differently from SPY over the long sample?

![1988+ equity curves: SPY vs B4 equal-weight vs B4-v2](plots/01_full_equity_log.png)

## 2. Moving From 25/25/25/25 To 35/40/25

After testing variations around B4, the strongest no-external-margin core I found was:

```text
35% GDE / 40% RSST / 25% ZROZ
```

Effective exposure is roughly:

```text
71.5% US large-cap equity
40.0% managed futures
31.5% gold
25.0% zero-coupon Treasury duration
168.0% positive exposure = 1.68x gross leverage
```

This is still a 100% allocation by fund weights. The leverage is embedded inside the products, not external margin.

Why I prefer this over the original equal-weight B4:

- It removes the NTSX sleeve, which was redundant once GDE/RSST already supplied equity stacking.
- It puts more weight on the two most useful return-stacked diversifiers: Gold and Managed Futures.
- It gives up only about 2 percentage points of max drawdown versus B4 original, while improving CAGR and terminal wealth.

The important comparison is still SPY. The 35/40/25 core had about `15.70%` CAGR and `-29.94%` MDD versus SPY at `11.46%` CAGR and `-55.14%` MDD over the same 1988-2026 window.

Chart 2 shows the same result as relative wealth versus SPY. This is where I check whether the result is just a higher terminal number or whether the portfolio spends meaningful time ahead of the benchmark.

![1988+ relative wealth vs SPY](plots/02_full_equity_vs_spy.png)

## 3. Update: Comparing Against A Recent r/LETFs Thread

After building this, I compared it against a recent r/LETFs thread claiming a strong long-term leveraged strategy:

https://www.reddit.com/r/LETFs/comments/1txmoat/this_is_the_best_strategy_for_long_term/

I ran the Testfol.io payloads from that discussion and deduplicated the repeated portfolios. The most relevant comparison was against the `35% GDE / 40% RSST / 25% ZROZ` core above.

The headline result:

- The best raw backtest from that thread was a **4-3-2-1 portfolio at 2x**.
- But that version uses `CASHX = -100%`, which means it is an explicit margin/borrow portfolio, not a simple ETF-only allocation.
- The best Reddit portfolio without explicit negative cash was the "mine" portfolio using small-cap value, 3x QQQ, 3x Gold, managed futures, and 3x TLT.
- That "mine" portfolio is the only non-margin Reddit candidate that slightly beat my `35/40/25` core over the full synthetic 1988+ window.

Full-window comparison:

| Portfolio | Window | CAGR | MDD | Calmar | Terminal | Note |
|---|---|---:|---:|---:|---:|---|
| 4-3-2-1 unlevered | 1988-01-04..2026-05-21 | 10.62% | -15.85% | 0.670 | 48x | Very defensive, but not enough return for my goal. |
| 4-3-2-1 2x margin | 1988-01-04..2026-05-21 | 17.21% | -27.98% | 0.615 | 443x | Best raw result, but requires margin/borrow. |
| Reddit "mine" QQQ/TLT/Gold 3x | 1988-01-04..2026-05-21 | 16.16% | -27.65% | 0.584 | 314x | Best non-negative-cash Reddit candidate. |
| My 35/40/25 core | 1988-01-04..2026-04-17 | 15.65% | -29.94% | 0.523 | 261x | Cleaner return-stacked implementation. |
| SPY buy-and-hold | 1988-01-04..2026-05-21 | 11.45% | -55.14% | 0.208 | 64x | Benchmark. |

So, yes: on the full synthetic history, the Reddit "mine" portfolio edges out my `35/40/25` core. But I would not immediately switch to it.

Why not?

- It uses `QQQ` rather than broad `SPY`-like equity exposure. That can be a feature if you want a Nasdaq tilt, but I do not love it as a core diversifier.
- It relies on 3x sleeves for QQQ, TLT, and Gold. The Gold 3x assumption is especially awkward because there is no clean, long-lived 3x Gold ETF implementation.
- The best raw 4-3-2-1 version needs explicit leverage through negative cash. That is a different implementation problem than buying return-stacked ETFs.

The post-2010 comparison is also important because it overlaps more with real ETF implementation:

| Portfolio | Window | CAGR | MDD | Calmar | Terminal | Note |
|---|---|---:|---:|---:|---:|---|
| My 35/40/25 core | 2010-10-18..2026-05-21 | 14.72% | -21.46% | 0.686 | 8.5x | Better drawdown-adjusted than Reddit mine. |
| 17.5% RSSX + MF split | 2010-10-18..2026-05-21 | 16.64% | -25.28% | 0.658 | 11.0x | Stronger optional variant, with BTC proxy caveat. |
| 10% RSSX + MF split | 2010-10-18..2026-05-21 | 15.97% | -24.28% | 0.658 | 10.1x | Cleaner optional enhancement than Reddit mine. |
| 4-3-2-1 2x margin | 2010-10-18..2026-05-21 | 15.22% | -25.65% | 0.593 | 9.1x | Good, but still a margin implementation. |
| Reddit "mine" QQQ/TLT/Gold 3x | 2010-10-18..2026-05-21 | 15.02% | -26.30% | 0.571 | 8.9x | No longer dominates the return-stacked core. |
| SPY buy-and-hold | 2010-10-18..2026-05-21 | 14.63% | -33.69% | 0.434 | 8.4x | Benchmark. |

My conclusion from that comparison:

- The 4-3-2-1 2x version is the strongest theoretical idea from the thread, but it is really a margin/borrow portfolio.
- The Reddit "mine" portfolio is a genuinely interesting seed, mostly because it adds small-cap value and more balanced diversifiers.
- I still prefer `35% GDE / 40% RSST / 25% ZROZ` as the clean core because it uses broad equity exposure and packaged return-stacking instead of direct 3x sleeves.
- If I were to research the Reddit idea further, I would not copy it directly. I would try to translate its useful exposures into a no-margin return-stacked version.

The most interesting follow-up is not QQQ, in my view. It is **factor diversification**.

Small-cap value is especially interesting because it gives a different equity risk premium than large-cap beta. The Fama-French factor framework explicitly separates market, size, value, profitability and investment factors, so SCV is not just "more stocks" in the same sense as adding more SPY exposure `[ml_for_algo_trading, ch.7 p.190-191]`.

Momentum is also interesting. It is conceptually different from value, and cross-sectional momentum has its own empirical literature and implementation issues `[stocks_on_the_move, p.60]`, `[ml_for_algo_trading, ch.4 p.86]`.

The trade-off is capital budget:

- Pro: SCV and momentum may diversify the equity sleeve and reduce dependence on plain large-cap beta.
- Con: in a 100% fund-weight portfolio, adding SCV or momentum means giving up some embedded leverage from GDE/RSST/RSSX/ZROZ.
- Therefore the right test is not "does SCV look good?" It is: does the marginal SCV/momentum sleeve improve the whole portfolio after accounting for the leverage it displaces?

I have not promoted any SCV or momentum variant yet. For now, I would treat them as the next research questions, not as part of the headline portfolio.

Follow-up: I did run a rough effective-exposure proxy test after this. Small AVUV/SPMO sleeves raised CAGR/terminal wealth slightly, but they also made the portfolio more equity-like. The baseline proxy was about `15.11%` CAGR / `-27.47%` MDD / `0.550` Calmar. The best factor variants reached about `15.33%` CAGR, but drawdown worsened to roughly `-30%..-31%` and Calmar fell. So I still would not replace the `35/40/25` headline core with an AVUV/SPMO variant.

## 4. Managed Futures: 40% RSST Or Split RSST/CTAP?

The canonical backtest uses:

```text
40% RSST
```

I think that remains theoretically valid. If you trust RSST as the implementation vehicle, you can stop there.

But for implementation, I started thinking about splitting the managed-futures stack:

```text
40% RSST  ->  20% RSST / 20% CTAP
```

This is not a change in the economic thesis. It is a manager/model diversification choice.

`RSST` and `CTAP` both give a form of:

```text
100% US equity + 100% managed futures
```

But the MF engines are different. For a rough diagnostic, I compared DBMF and KMLM style managed-futures proxies from 2000 onward:

| Portfolio | CAGR | MDD | Sharpe | Calmar |
|---|---:|---:|---:|---:|
| SPY | 8.39% | -55.14% | 0.415 | 0.152 |
| SPY + KMLM stack | 11.84% | -52.59% | 0.548 | 0.225 |
| SPY + DBMF stack | 13.56% | -47.77% | 0.607 | 0.284 |
| SPY + 50/50 DBMF/KMLM stack | 12.91% | -42.68% | 0.603 | 0.303 |

The 50/50 blend did not maximize CAGR, but it improved drawdown/Calmar. That is exactly the reason I like splitting the MF sleeve: I do not know which MF replication model will be better over the next decade.

## 5. RSSX: I Did Not Want To Use Raw BTC History

The next question was whether to split the GDE sleeve with RSSX.

Naively, one might model RSSX as:

```text
100% SPY + 80% Gold + 20% BTC inside a capital-efficient ETF wrapper
```

I do not think that is good enough.

RSSX is closer to:

```text
100% SPY + 100% Gold/BTC sleeve
```

Where the Gold/BTC sleeve uses a volatility/risk-parity process. Per the prospectus, BTC is generally expected to be between 5% and 25% of that sleeve, not a constant portfolio-level 20% BTC bet.

Also, raw BTC backtests are dangerous. BTC's 2010-2026 CAGR is mostly a one-time adoption ramp from experiment to institutional asset. I do not want a portfolio to look good just because it smuggles early-Bitcoin returns into the backtest.

So I built a more conservative RSSX proxy:

```text
RSSX_RP = 100% SPY
        + 100% Gold/BTC risk-parity sleeve
        - 0.67% expense ratio
```

The Gold/BTC sleeve uses lagged 63-day realized volatility. BTC weight is inverse-volatility risk parity, clipped to 5%-25% of the sleeve. I then nerfed BTC drift to several forward-return assumptions while keeping its historical volatility/crash path.

## 6. Post-2010 RSSX/CTAP Comparison

This table starts in 2010 because BTC history constrains the RSSX proxy. The BTC scenario here is a deliberately nerfed `10%` CAGR assumption, not raw BTC history.

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

For the RSSX rows, BTC and gold use the historical average BTC sleeve weight of roughly `17.6%` inside the RSSX Gold/BTC sleeve. In stressed crypto regimes, the BTC notional should be lower; in calmer regimes, higher.

My read:

- The original 35/40/25 core is still the clean result.
- Splitting `40% RSST` into `20% RSST / 20% CTAP` modestly changes the profile, but does not break the portfolio.
- Adding `10% RSSX_RP` improves the post-2010 table, but not enough for me to make BTC the central claim.
- A `17.5% RSSX_RP` allocation is the clean 50/50 split of the GDE sleeve, but it is clearly more of a BTC-convexity choice.

Charts 3-5 are the implementation layer. I separate this from the 1988+ core result because RSSX is constrained by BTC history and the post-2010 window.

![Post-2010 implementation equity curves](plots/03_implementation_equity_log.png)

Chart 4 turns the implementation variants into relative wealth versus SPY, so the question becomes: did the RSSX/CTAP variants add enough versus a simple benchmark to justify the extra moving parts?

![Post-2010 implementation relative wealth vs SPY](plots/04_implementation_equity_vs_spy.png)

Chart 5 shows the drawdown cost of those implementation variants. This is the main reason I keep the clean 35/40/25 core as the headline and treat RSSX as optional.

![Implementation drawdowns](plots/05_implementation_drawdowns.png)

## 7. BTC Sensitivity Check

For the `10% RSSX_RP` version:

```text
25% GDE / 10% RSSX_RP / 20% RSST / 20% CTAP / 25% ZROZ
```

The result under different BTC drift assumptions:

| BTC scenario   | CAGR   | MDD     |   Sharpe |   Calmar | Terminal   |
|:---------------|:-------|:--------|---------:|---------:|:-----------|
| historical_btc | 17.65% | -24.21% |    1.191 |    0.729 | 12.6x      |
| btc_0          | 15.87% | -24.29% |    1.086 |    0.653 | 9.9x       |
| btc_6          | 15.99% | -24.29% |    1.093 |    0.658 | 10.1x      |
| btc_10         | 16.06% | -24.28% |    1.098 |    0.662 | 10.2x      |
| btc_14         | 16.14% | -24.28% |    1.102 |    0.665 | 10.3x      |

This is why I am more comfortable discussing RSSX as optional. Even with BTC drift reduced to 0%-14%, the portfolio does not collapse. But the improvement is not so overwhelming that I would want the whole thesis to depend on BTC.

## 8. Rolling Check vs SPY

The final two charts answer a different question: how often would this have felt bad to hold over normal investor horizons?

Chart 6 looks at rolling relative wealth over 3/5/10/15-year windows. The short windows are not flawless, which is why I would not describe this as an always-on SPY dominator.

![Rolling relative wealth 3/5/10/15](plots/06_rolling_relative_wealth_2x2.png)

Chart 7 converts that into rolling CAGR spread versus SPY. The portfolio's strength is more visible in longer windows than in short tactical windows.

![Rolling CAGR spread 3/5/10/15](plots/07_rolling_cagr_spread_2x2.png)

## 9. Monte Carlo Sequence-Risk Simulation

I also ran a simple Monte Carlo sequence-risk simulation.

Method:

```text
1,000 simulated paths
20 years per path
21-trading-day block bootstrap
daily returns resampled in paired blocks across all portfolios
source window: 1988-2026
```

This is not a forecast. It is a path-ordering stress test: if the same historical return blocks happened in different sequences, how often would the portfolio still beat SPY, and what drawdowns would show up? It does not solve pre-inception proxy risk or fund tracking risk `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.

| Portfolio | p10 terminal | median terminal | p10 CAGR | median MDD | Prob. terminal < SPY |
|---|---:|---:|---:|---:|---:|
| 100% SPY | 3.17x | 7.93x | 5.93% | -35.62% | — |
| B4-v2 35/40/25 | 7.91x | 18.81x | 10.89% | -24.49% | 6.2% |
| B4 original 25/25/25/25 | 6.49x | 14.26x | 9.80% | -23.95% | 11.2% |

Chart 8 shows the Monte Carlo median paths, with 10th-90th percentile bands.

![Monte Carlo 20-year sequence-risk simulation](plots/08_monte_carlo_20y_sequence_risk.png)

My read: the MC result supports the same conclusion as the historical backtest. B4-v2 is not risk-free, but in this resampling test it has materially better downside terminal wealth than SPY and a lower simulated median drawdown.

## 10. Candidate Implementations

Canonical research core:

```text
35% GDE / 40% RSST / 25% ZROZ
```

Implementation with MF manager split, no RSSX:

```text
35% GDE / 20% RSST / 20% CTAP / 25% ZROZ
```

Conservative RSSX implementation:

```text
25% GDE / 10% RSSX / 20% RSST / 20% CTAP / 25% ZROZ
```

Clean 50/50 GDE/RSSX sleeve split:

```text
17.5% GDE / 17.5% RSSX / 20% RSST / 20% CTAP / 25% ZROZ
```

I currently think the canonical `35/40/25` is the cleanest research result, and the `25/10/20/20/25` version is the more conservative implementation variant if someone wants RSSX exposure.

## 11. Caveats

- This is a backtest, not a recommendation.
- Most of the ETF histories are simulated/proxy histories before live inception.
- RSSX, CTAP, GDE and RSST all have implementation details that the proxy cannot perfectly replicate.
- Taxes, spreads, AUM/fund-closure risk and tracking error matter.
- The RSSX comparison is post-2010 only, while the core B4-v2 result has a longer 1988+ window.
- I would not use raw historical BTC CAGR for any serious forward-looking allocation decision.
- The r/LETFs comparison portfolios are seed ideas, not validated replacements. The margin version needs explicit financing/cost analysis, and the QQQ/TLT/Gold 3x version needs real-implementation tracking checks.
- SCV and momentum are attractive factor candidates, but adding them means reducing some other stack. The opportunity cost is embedded leverage.

## 12. Questions

- Would you keep `40% RSST`, or split the sleeve into `20% RSST / 20% CTAP`?
- Would you use RSSX at all, or keep the cleaner `35% GDE / 40% RSST / 25% ZROZ` core?
- If using RSSX, does `10%` feel more reasonable than a full `17.5%` half-sleeve split?
- Would you add a small-cap value sleeve, even if it means reducing embedded leverage elsewhere?
- Would you include momentum as a separate factor sleeve, or is managed futures already enough trend/momentum exposure?
