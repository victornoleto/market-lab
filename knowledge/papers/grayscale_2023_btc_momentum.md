# The Trend is Your Friend: Managing Bitcoin's Volatility with Momentum Signals

## Metadata

- **Publisher:** Grayscale Research Team (not peer-reviewed)
- **Year:** 2023 (last updated August 9, 2023)
- **Venue:** Grayscale Research report
- **Source URL (primary):** https://research.grayscale.com/reports/the-trend-is-your-friend-managing-bitcoins-volatility-with-momentum-signals
- **Slug:** `paper.grayscale_2023_btc_momentum`
- **Topic:** T5 — Crypto trend / MA-crossover baseline
- **Raw access:** N/A — no local raw; extraction based on secondary summaries
- **Citation format:** `[paper.grayscale_2023_btc_momentum, §results]`

## Core thesis

Bitcoin exhibits pronounced momentum (gains follow gains, losses follow losses). **Simple moving-average strategies** applied to BTC historically reduce drawdowns vs buy-and-hold while preserving most of the upside.

## Methodology snapshot

- **Asset:** Bitcoin (BTC)
- **Period:** 2012 → August 2023
- **Strategies tested:**
  - Price > 50-day SMA → long, else cash
  - 20-day / 100-day MA crossover → long on bullish cross, cash on bearish
- **Cost model:** not detailed
- **OOS / robustness / PBO:** not documented — practitioner research report

## Key results

- **50-day MA strategy: annualized 126%, Sharpe 1.9** (2012–2023 IS)
- **20d/100d crossover: annualized 116%, Sharpe 1.7** (2012–2023 IS)
- **BTC buy-and-hold benchmark: annualized 110%, Sharpe 1.3**
- Drawdown reduction via filter is the primary source of edge

## Applicability to market-lab

- **LOW–MEDIUM relevance.** Illustrative baseline but **in-sample only**, with no OOS hold-out, no PBO, no CSCV. Numbers are anchored to a BTC era (early adoption) that is not representative going forward.
- Usable as **secondary supporting citation** for Phase 3.7-3 H3, not a primary lead.
- Pepperstone fit: BTCUSD CFD serves the underlying; Tiingo crypto is the data blocker.

## Related knowledge-base entries

- `paper.zarattini_2025_crypto_trends` — peer-reviewed complement with broader universe + survivorship-free data.
- `paper.palazzi_2025_crypto_passive` — Journal of Futures Markets parallel (requires paywall access).
