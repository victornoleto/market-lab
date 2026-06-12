# I tested US-only vs global return-stacked portfolios. International exposure did not improve the backtest, but it may still be future insurance.

**Not financial advice.** This is a research post, not a recommendation. All long histories are simulated proxies, gross of taxes/costs, monthly rebalanced. Several funds/proxies did not exist for the full history. The managed-futures sleeve is the most proxy-sensitive piece, so treat exact crisis magnitudes as directional, not precise.

The question I wanted to answer:

> If I already have a US-centric return-stacked core, does adding international equity exposure improve the portfolio, or is it just lower-return diversification?

The short answer from my tests:

> In the backtest, international exposure did **not** improve the US-only core. It either reduced CAGR, worsened drawdown, or both. But external forward-looking evidence still gives a rational reason to hold some international exposure: US valuations and concentration are unusually high, and the next 10-20 years may not look like 2009-2024.

Suggested chart order if uploading as a Reddit gallery:

| # | Chart | What it shows |
|---:|---|---|
| 1 | Global portfolios vs VT | All return-stacked versions beat VT; US core still leads. |
| 2 | Drawdowns | Global exposure does not automatically improve drawdowns. |
| 3 | Price of globalness | Forcing more international exposure progressively costs Sharpe. |
| 4 | Worst VT months | International equity falls with equity; gold/MF/ZROZ do the crisis work. |
| 5 | 1970+ low-fidelity extension | The strongest counterargument: in older regimes, moderate intl was almost free. |
| 6 | 60/40 and 66/34 constrained frontier | If you force global geography, the best designs route intl through RSIT and raise ZROZ. |

## The setup

My US-only core is:

```text
35% GDE / 40% RSST / 25% ZROZ
```

Approximate look-through exposure:

```text
~72% US equity
~40% managed futures
~32% gold
~25% long zero-coupon Treasuries
~1.68x positive exposure per $1
```

The global variants use the same basic idea, but replace part of the US equity wrapper with international wrappers:

```text
GDE  = US equity + gold stack
RSST = US equity + managed futures stack
NTSD = US + developed ex-US equity stack
RSIT = international equity + managed futures stack
ZROZ = long-duration Treasury convexity
```

The main global candidate I started with was:

```text
20% GDE / 15% NTSD / 20% RSST / 20% RSIT / 25% ZROZ
```

That is roughly `64% US / 36% international` as a share of equity exposure.

Benchmarks:

```text
100% SPY
100% VT
66% VTI / 34% VEA
```

I included `66/34 VTI/VEA` because some of the global variants are closer to US + developed ex-US than true VT, and largely ignore EM.

## Main result: 2000-2026, higher-fidelity window

This is the cleanest common window for the current managed-futures proxy.

| Portfolio | CAGR | Max DD | Sharpe | Read |
|---|---:|---:|---:|---|
| 100% SPY | 8.5% | -55.1% | 0.52 | US equity benchmark |
| 100% VT | 7.2% | -58.4% | 0.46 | global equity benchmark |
| 66/34 VTI/VEA | 7.6% | -56.9% | 0.48 | US/dev ex-US benchmark |
| **US core: 35 GDE / 40 RSST / 25 ZROZ** | **12.5%** | **-30.8%** | **0.85** | best performance-first result |
| Balanced global: 27.5 / 7.5 / 30 / 10 / 25 | 11.7% | -33.4% | 0.80 | moderate intl, still trails US core |
| Core-global: 20 / 15 / 20 / 20 / 25 | 10.9% | -36.8% | 0.75 | maximum-diversification expression |
| Ratio-constrained 66/34: 30 GDE / 15 RSST / 20 RSIT / 35 ZROZ | 11.2% | **-28.4%** | 0.82 | better drawdown, lower CAGR |

![Global return-stacked portfolios vs VT](figures/g02_global_portfolios_vs_vt.png)

**Chart 1 read:** the global return-stacked variants are not failing against VT. They beat VT by a lot. The relevant loss is against the US-only core, which keeps the highest terminal wealth and CAGR in the modern window.

![Global portfolio drawdowns](figures/g03_global_underwater.png)

**Chart 2 read:** globalizing the equity sleeve does not automatically make the drawdown profile better. The maximum-diversification global version has worse MDD than the US core; the 66/34 constrained version improves drawdown only by giving up CAGR.

The important comparison is not global vs VT. The return-stacked global portfolios crush VT. The important comparison is **global vs the US-only return-stacked core**.

Against the US core:

- The balanced global version loses about `0.8pp/year` of CAGR and has a deeper drawdown.
- The more global `20/15/20/20/25` version loses about `1.6pp/year` and has a much deeper drawdown.
- The best 66/34 ratio-constrained version improves drawdown by about `2.4pp`, but gives up about `1.3pp/year` of CAGR.

So I do **not** see international exposure as a free lunch in this construction. It is not giving me higher CAGR with lower drawdown. It is mostly a policy choice: accept some drag to reduce single-country dependence.

## The globalness price curve

I also scanned a 10,626-node simplex over:

```text
GDE / NTSD / RSST / RSIT / ZROZ
```

At 5% weight increments.

The unconstrained optimizer always picked a US-only mix. On the 2000+ window:

```text
Best unconstrained node: 45 GDE / 0 NTSD / 25 RSST / 0 RSIT / 30 ZROZ
Sharpe: 0.866
```

Then I forced minimum international sleeves and measured the cost:

| Forced NTSD+RSIT floor | Best Sharpe | Best CAGR | Best MDD |
|---:|---:|---:|---:|
| 0% | 0.866 | 12.8% | -29.7% |
| 10% | 0.850 | 12.5% | -31.0% |
| 15% | 0.840 | 12.3% | -31.7% |
| 20% | 0.830 | 12.2% | -32.5% |
| 35% | 0.788 | 11.1% | -33.6% |
| 50% | 0.725 | 10.4% | -37.2% |

![The price of forcing international exposure](figures/g08_intl_price_curve.png)

**Chart 3 read:** this is the central chart for the post. In the 2000+ window, the best portfolio with no international constraint is US-only. As I force more NTSD+RSIT, the best available Sharpe steadily falls. The price is not huge at 10-20%, but it is real.

The rough cost was about `-0.01 Sharpe` per additional `5pp` of forced international allocation in the 2000+ window. That cost was smaller on the 1988+ window.

## Why international equity did not help much in this backtest

The main issue is that international equity is still equity.

Monthly correlations, 2000-2026:

```text
SPY vs VXUS: 0.854
SPY vs VEA:  0.861
VT  vs VXUS: 0.963
```

In VT's worst 32 months:

| Asset | Avg monthly return in VT worst-decile months |
|---|---:|
| VT | -8.5% |
| SPY | -7.7% |
| VEA | -8.8% |
| VXUS | -8.8% |
| VWO | -9.4% |
| Gold | +0.6% |
| Managed futures | +2.3% |
| ZROZ | +3.7% |

![What happens in VT's worst months](figures/g07_vt_down_months.png)

**Chart 4 read:** this is why I separate geographic diversification from crisis diversification. VEA/VXUS/VWO are useful for country exposure, but in global equity drawdowns they still behave like equity. The left-tail ballast came from gold, managed futures and ZROZ.

International equity diversified *who issues my equity risk*. It did not diversify *whether I own equity risk*.

The crisis work in this portfolio came from gold, managed futures and long-duration Treasuries, not from geography. This is consistent with the risk-parity / return-stacking intuition: the value comes from stacking genuinely different return streams, not simply owning more countries.

## But the future case for international is not dead

This is where I think the discussion gets interesting.

The backtest says: "do not add international if your only objective is to maximize the historical CAGR/Sharpe of this return-stacked core."

But several forward-looking arguments point the other way.

### 1. Vanguard expects higher 10-year returns outside the US

Vanguard's September 30, 2025 VCMM forecasts, in USD terms:

| Asset class | 10-year nominal return forecast range | Median volatility |
|---|---:|---:|
| US equities | 2.8%-4.8% | 15.1% |
| Global ex-US equities | 4.9%-6.9% | 18.8% |
| Developed markets ex-US equities | 5.3%-7.3% | 18.1% |
| Emerging markets equities | 3.2%-5.2% | 25.4% |

Vanguard also says US equity valuations remain significantly above long-term fair value, and recommends at least 20% international exposure, with about 40% of the stock allocation international to get the full diversification benefit.

### 2. AQR says extrapolating US dominance is dangerous

AQR's 2023 paper *International Diversification - Still Not Crazy after All These Years* makes the argument directly:

- international diversification has hurt US-based investors for 30+ years;
- the long-run case is still relevant;
- post-1990 US outperformance should not be extrapolated;
- much of the outperformance came from rising relative valuations;
- today's rich US valuations may point to prospective underperformance.

### 3. Morningstar points to concentration and valuation risk

Morningstar notes that US stocks rose from about `40%` of the Morningstar Global Markets Index in 2008 to about `63%` today. Nvidia alone exceeded the value of the entire Canadian and UK stock markets at the time of the article.

Morningstar's case is not that international stocks are magical diversifiers. They explicitly note that US and international correlations have risen. Their point is more modest: the US market is now expensive, concentrated and top-heavy relative to the rest of the world.

### 4. My own long-window stress agrees with the regime argument

On the lower-fidelity 1970-2026 extension, which includes the 1970s-80s international/outside-US cycle:

| Portfolio | CAGR | Max DD | Sharpe |
|---|---:|---:|---:|
| US core | 14.0% | -39.7% | 0.893 |
| Half-intl 27.5/7.5/30/10/25 | 13.6% | -38.2% | **0.894** |
| Core-global 20/15/20/20/25 | 13.3% | -37.0% | 0.878 |
| VT | 10.0% | -58.4% | 0.664 |

![1970+ low-fidelity global extension](figures/g11_global_extended_1970.png)

**Chart 5 read:** this is the honest counterweight to the 2000+ result. The 1970+ extension is lower fidelity, but it includes regimes that the modern US-dominance sample misses. In that longer view, moderate international exposure nearly ties the US core on Sharpe and slightly improves drawdown.

This does not prove that international wins. The 1970+ extension is lower fidelity. But it does show that the "international drag" is not a law of nature. In a different regime, moderate international exposure can be close to free.

## My current conclusion

I would frame the decision like this:

```text
If I am choosing purely from the backtest:
    US core wins.

If I am worried that 2009-2024 US exceptionalism will not repeat:
    a 10-20% international sleeve is defensible insurance.

If I want maximum country diversification regardless of backtest Sharpe:
    Core-global 20/15/20/20/25 is valid, but I should admit I am paying for it.
```

My preferred global compromise is not the 35% international version anymore. It is closer to:

```text
27.5 GDE / 7.5 NTSD / 30 RSST / 10 RSIT / 25 ZROZ
```

or the cleaner 5% grid version:

```text
30 GDE / 5 NTSD / 30 RSST / 10 RSIT / 25 ZROZ
```

That keeps international sleeves around `15-20%`, routes most of the international exposure through RSIT, and preserves the three real crisis diversifiers.

If I force a strict 66/34 US/international equity geography, the best structure I found was:

```text
30 GDE / 15 RSST / 20 RSIT / 35 ZROZ
```

![Ratio-constrained global frontier](figures/g10_ratio_constrained_frontier.png)

**Chart 6 read:** if I force a 60/40 or 66/34 US/international equity mix, the best designs do not simply add generic international equity. They prefer RSIT, drop NTSD, and raise ZROZ. That says the construction needs international equity plus real diversifiers, not international equity by itself.

Notice what happens: NTSD drops out entirely, international exposure enters through RSIT, and ZROZ rises to 35%. In other words, if I add international equity, I need *more* convex duration, not less.

## What I am not claiming

- I am not claiming these returns repeat forward.
- I am not claiming the live ETFs will match the proxies.
- I am not claiming international is useless.
- I am not claiming the US will outperform forever.
- I am not claiming a 10,626-node grid gives an optimized portfolio. The scan is descriptive, not a selection rule. Picking the highest-Sharpe node after testing thousands of combinations would be classic backtest overfitting.

What I am claiming is narrower:

> In this return-stacked setup, ex-US exposure did not create a better historical portfolio than the US-only core. The best argument for international is forward-looking humility, not backtest improvement.

## Question for the sub

Would you accept roughly `0.8-1.5pp/year` lower backtested CAGR for less single-country risk?

Or, if you believe current US concentration/valuation is a real forward risk, what international allocation would you use in a return-stacked core: 10%, 20%, market weight, or zero?

## Source notes

This post is self-contained. The tables above are the complete results I am using for the Reddit discussion: no external spreadsheet or private report is required to follow the argument. The numbers come from an offline simulation using the proxy formulas stated at the top of the post, monthly rebalancing, gross returns, and the common windows shown in each section.

External sources I used for the broader "100% US vs global diversification" question:

| Source | URL | What I used it for |
|---|---|---|
| Vanguard Capital Markets Model forecasts, September 30 2025 | https://www.vanguardsouthamerica.com/en/home/insights/economic-market-outlook/vanguard-capital-markets-model-forecasts | Vanguard's 10-year nominal return forecast ranges were higher for global ex-US equities (`4.9%-6.9%`) and developed ex-US equities (`5.3%-7.3%`) than for US equities (`2.8%-4.8%`). This supports the forward-looking valuation argument for not extrapolating recent US dominance. |
| Vanguard, `International Investments: Stocks, Bonds, & ETFs` | https://investor.vanguard.com/investor-resources-education/understanding-investment-types/why-invest-internationally | Vanguard's general diversification case: foreign markets do not always move exactly with the US, international funds broaden exposure, and Vanguard suggests at least `20%` international exposure, with about `40%` of the stock allocation international to capture full diversification benefits. It also lists the risks: currency, country/regional, political and emerging-market risk. |
| AQR, Asness / Ilmanen / Villalon, `International Diversification - Still Not Crazy after All These Years` | https://www.aqr.com/Insights/Research/Journal-Article/International-Diversification-Still-Not-Crazy-after-All-These-Years | AQR's argument that international diversification has hurt US-based investors for 30+ years, but the long-run case remains relevant. The key point I used: it is dangerous to extrapolate post-1990 US outperformance because much of it came from rising relative valuations, and current US richness may point to prospective underperformance. |
| Morningstar, `Why 2025 Is the Year to Invest in International Stocks` | https://www.morningstar.com/markets/why-2025-is-year-invest-international-stocks | Morningstar's tactical and strategic international case: US stocks grew from about `40%` of the Morningstar Global Markets Index in 2008 to about `63%`; the US market is top-heavy, expensive and low-yielding relative to many non-US markets; global leadership has historically moved in cycles. Morningstar also notes the counterpoint: US/international correlations have risen, so international equity is not a reliable crash hedge by itself. |
| AQR, `2026 Capital Market Assumptions for Major Asset Classes` | https://www.aqr.com/Insights/Research/Alternative-Thinking/2026-Capital-Market-Assumptions-for-Major-Asset-Classes | Used only as background on expected-return formation: AQR says medium-term expected returns are valuation-based and risk premia remain compressed. This supports treating forward-looking expected returns as uncertain distributions, not point forecasts. |
| BlackRock Investment Institute, `Capital market assumptions` | https://www.blackrock.com/institutions/en-us/insights/thought-leadership/capital-market-assumptions | Used only as background on uncertainty/scenario framing. BlackRock emphasizes that long-run asset-class assumptions should include multiple scenarios and uncertainty around central estimates. I did not use BlackRock for the specific US-vs-ex-US numeric return claims above. |

My synthesis of those sources:

- The **historical backtest** favors the US-only return-stacked core.
- The **forward-looking valuation literature** favors at least considering non-US exposure.
- The **risk evidence** says international equity is not a crisis diversifier like managed futures, gold or convex duration.
- Therefore, international exposure is best framed as **regime insurance against US exceptionalism failing**, not as something that improved this particular backtest.
