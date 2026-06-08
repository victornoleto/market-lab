# Equity + Managed Futures return-stacked ETFs: which one is worth watching?

Not financial advice. I am trying to map the new wave of ETFs that combine **equity beta + managed futures / trend / futures overlays** in one wrapper.

Basic idea:

```text
100% stocks
+ 100% managed futures / trend / futures overlay
= ~200% gross exposure inside one ETF
```

I am not trying to pick a winner from short live histories. Most of these are too new. I mostly want to know which ones people here think are worth watching.

## The Tickers

| Ticker | What it roughly does | Why I care |
|---|---|---|
| `RSST` | U.S. stocks + managed futures trend | Current reference ETF for this category. |
| `CTAP` | U.S. large-cap equity + systematic managed futures | Main RSST alternative; possible manager/process diversification. |
| `MATE` | S&P 500 + Man-managed trend-following futures | Interesting because of Man/AHL pedigree. Very new. If the ticker should be `MATEP`, please correct me. |
| `JPFP` | U.S. equity + JPMorgan managed futures plus | Interesting because JPMorgan could scale the product if it gains traction. Very new. |
| `SPXP` | S&P 500 + managed futures trend | Direxion version of the same broad concept. Very new. |
| `HOLD` | Alpha layering / equity plus alternatives | Adjacent idea, but I am not sure it belongs in the clean equity+MF bucket. |
| `RSIT` | International stocks + managed futures trend | Not a U.S. equity replacement, but relevant for global allocation. |
| `RSSY` | U.S. stocks + futures yield/carry | Related, but futures carry/yield is not the same as trend managed futures. |

## Why Managed Futures?

Managed futures can be useful because they are not just another equity factor. A real trend-following futures sleeve can go long/short across rates, currencies, commodities and equity indexes. That means it can sometimes make money in regimes where stocks and bonds are both struggling.

That does not mean it always works. Trend can be late in fast crashes, can bleed in choppy markets, and can disappoint if the implementation is weak. But as a portfolio diversifier, it is one of the few categories that can be structurally different from plain equity beta.

## Why Return-Stack It With Equity?

The normal way to add managed futures is to sell some stocks and buy a managed-futures fund:

```text
50% SPY / 50% KMLM or DBMF
```

That can lower drawdowns, but it also cuts your equity exposure in half.

The return-stacked version tries to do this instead:

```text
100% SPY
+ 100% managed futures
- embedded financing / collateral cost
```

So the trade-off is different:

| Approach | Main benefit | Main problem |
|---|---|---|
| `50/50 SPY/MF` | Lower drawdown, simpler, no embedded leverage | Gives up a lot of equity beta and upside |
| `100/100 equity+MF stack` | Keeps full equity beta and adds a diversifier | Depends on leverage, financing, fees, tracking and manager skill |

That is why I think this ETF category is worth discussing. It is not just "buy managed futures." It is "can I add managed futures without shrinking my equity allocation?"

## Quick Testfol.io Comparison

Testfol.io does not accept `RSSTSIM` directly, so I used rough long-history proxies:

```text
RSST-style KMLM stack = 100% SPYSIM + 100% KMLMSIM - 100% CASHX
RSST-style DBMF stack = 100% SPYSIM + 100% DBMFSIM - 100% CASHX
Mixed MF stack       = 100% SPYSIM + 50% KMLMSIM + 50% DBMFSIM - 100% CASHX
```

Common window: `2000-01-03` to `2026-06-05`, limited by `DBMFSIM`. Yearly rebalance. This is a rough concept check, not a product-level validation.

| Portfolio | CAGR | Max DD | Calmar | My read |
|---|---:|---:|---:|---|
| `100% SPY` | 8.33% | -55.14% | 0.151 | Baseline. |
| `100% SPY + 100% KMLM - cash` | 11.89% | -57.83% | 0.206 | More return, but drawdown not improved in this proxy. |
| `50% SPY / 50% KMLM` | 7.20% | -29.99% | 0.240 | Much lower drawdown, but lower CAGR than SPY. |
| `100% SPY + 100% DBMF - cash` | 13.59% | -44.64% | 0.304 | Best stacked result in this quick test. |
| `50% SPY / 50% DBMF` | 8.11% | -23.21% | 0.349 | Best drawdown/Calmar, but much less growth than the stack. |
| `100% SPY + 50% KMLM + 50% DBMF - cash` | 12.93% | -44.46% | 0.291 | Mixed MF stack; lower CAGR than DBMF-only stack, similar drawdown. |

Equity curves:

![Equity + managed futures stacked exposure vs 50/50 blends](return_stacked_etf_universe/plots/equity_mf_stack_vs_blend_equity_curves.png)

This is exactly the trade-off I am thinking about:

```text
50/50 blends look safer.
Return-stacked versions preserve more growth.
The best choice depends on whether the managed-futures sleeve earns enough to justify the embedded leverage and fees.
```

## My Current Bias

Right now my simple ranking is:

| Bucket | Tickers |
|---|---|
| Most practical today | `RSST`, `CTAP` |
| Very interesting but too new | `MATE`, `JPFP`, `SPXP` |
| Adjacent / needs more understanding | `HOLD`, `RSSY` |
| Useful for global allocation | `RSIT` |

If I were using this category today, I would probably start by comparing:

```text
100% RSST
vs
50% RSST / 50% CTAP
```

Not because I know `CTAP` is better, but because I like the idea of diversifying the managed-futures engine instead of relying on one model.

## CTAP Cost Caveat

One thing I would not do is describe `CTAP` as just a `0.10%` or `0.28%` expense-ratio product.

From Simplify's public pages/holdings, my rough read is:

```text
CTAP wrapper fee:       0.10% current net / 0.28% gross
CTA embedded fee:       about 0.75%
CTA swap spread:        about SOFR + 0.95%, based on current holdings labels
```

So the visible non-SOFR drag looks closer to roughly `1.8%-2.0%` before taxes, tracking and exact collateral mechanics. That does not automatically make it bad. It just means `CTAP` is a clean packaged implementation, not obviously a cheap one.

The DIY version is also not a perfect substitute. `33% SPXL + 100% CTA` does not fit inside 100% capital unless you add margin somewhere, and `33% SPXL + 67% CTA` fits but no longer gives the full managed-futures sleeve. Plus SPXL has daily reset/path dependency and its own embedded costs.

That is why my current bias is: use `CTAP` only if you want manager/process diversification versus `RSST`, not because it obviously wins on fees.

## Questions For The Sub

1. Which equity+managed-futures wrapper do you think is best designed?
2. Would you hold only `RSST`, or split between `RSST`/`CTAP`/`MATE`/others?
3. Does anyone understand the methodology differences between `RSST`, `CTAP`, `MATE`, `JPFP`, and `SPXP` well enough to compare them?
4. Is `RSSY` worth pairing with trend managed futures, or is futures carry/yield a totally different bucket?
5. Am I missing any other equity + MF return-stacked ETFs?
6. If you had to choose one of these to age best over the next decade, which would it be and why?

Internal note for my research log: the comparison above is a seed diagnostic only, not a validation pass. Short live histories and external backtester simulations are hypothesis generators, not proof `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`; leverage/financing/cost realism is central when comparing stack vs blend `[systematic_trading, p.185-188]`, `[leverage_for_the_long_run, p.21]`. CTAP cost snapshot saved in `return_stacked_etf_universe/derived/ctap_trs_cost_snapshot.csv`.
