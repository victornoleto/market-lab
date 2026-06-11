# Stacked-ETF portfolio (GDE/RSST/ZROZ): I tested how each piece behaved in every drawdown since 2000, and whether the exact weights even matter

**Not financial advice** — sharing research, not a recommendation. Benchmark: 100% SPY.

**Simulation disclosure up front:** GDE/RSST only launched in 2022/2023. All long histories are simulated proxies (index sims + the funds' published compositions: GDE ≈ 90% SPY + 90% gold; RSST ≈ 100% SPY + 100% managed futures, each minus cash financing). Real funds add fees and tracking error. Taxes/costs ignored, monthly rebalancing, gross returns. The managed-futures proxy is the most fragile assumption — crisis numbers are directional, not precise.

## The idea

Capital-efficient ETFs let one dollar hold more than one asset: GDE is $0.90 stocks + $0.90 gold; RSST is $1 stocks + $1 managed futures; ZROZ is plain long-duration Treasuries. A 35/40/25 mix holds ~75% stocks, ~32% gold, ~40% managed futures, ~25% long Treasuries per dollar — diversification without giving up equity exposure.

## Headline (2000–2026, simulated)

| | CAGR | Max drawdown | Growth of $1 |
|---|---|---|---|
| 35% GDE / 40% RSST / 25% ZROZ | **12.5%** | **−30.8%** | **$22.5** |
| 100% SPY | 8.5% | −55.1% | $8.7 |

## Who shows up in each crisis

| Episode | SPY | Gold | Mgd futures | ZROZ | Portfolio |
|---|---|---|---|---|---|
| Dot-com bust | −47% | +12% | +44% | +50% | **−21%** |
| GFC | −55% | +25% | +34% | +50% | **−23%** |
| 2022 | −24% | −9% | **+38%** | −40% | **−21%** |

Different crisis, different hero — 2022 is the row that matters: stocks AND bonds fell together, and only trend-following carried. In SPY's 32 worst months (avg −7.9%), gold averaged +1.8%, managed futures +2.4%, ZROZ +3.8% per month. Monthly correlations to SPY: +0.06 / −0.22 / −0.15.

The honest rows: in melt-ups the portfolio lags — 2013 taper tantrum: SPY +17.5%, portfolio −2.4%. This strategy trades upside in the best years for survival in the worst ones.

## Do the exact weights matter? (my favorite result)

I backtested **all 231 possible 5%-step allocations** of the three funds. The best Sharpe (0.866) sits at 45/25/30 — but the entire region within 95% of the best is one **contiguous 60-portfolio plateau**, and 35/40/25 is inside it from every one of 8 start dates tested. The "optimal" corner moves every time you change the window; the plateau doesn't.

So: anywhere in the broad middle (GDE 30-60%, RSST 10-45%, ZROZ 20-40%) gets you essentially the same portfolio. Don't agonize over 35/40/25 vs 40/40/20.

What moves the needle is *removing* a sleeve: dropping ZROZ → +1.4pp CAGR but −45% drawdowns; swapping gold out for more bonds (NTSX) → −2.7pp CAGR over this window. Equal-weight 33/33/33 performs the same as the "tuned" mix — which is the plateau speaking.

## What I'm NOT claiming

Not that these returns repeat forward (this sample had gold and bond tailwinds), not that 35/40/25 is optimal (explicitly the opposite), not that small new ETFs are risk-free wrappers (closure/tracking/fee risk are real).

**Questions:** Anyone holding GDE or RSST live — how's the tracking? Anyone using EDV/GOVZ instead of ZROZ? How many flat managed-futures years would make you capitulate?
