# Catching Crypto Trends: A Tactical Approach for Bitcoin and Altcoins

## Metadata

- **Authors:** Carlo Zarattini, Alberto Pagani, Andrea Barbon
- **Year:** 2025 (last revision April 9, 2025)
- **Venue:** SSRN working paper (abstract_id=5209907); also on author sites
- **Source URL (primary):** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5209907
- **Alt URL (author site):** https://www.abarbon.com/papers/catching-crypto-trends
- **Alt URL (ResearchGate):** https://www.researchgate.net/publication/391508704_Catching_Crypto_Trends_A_Tactical_Approach_for_Bitcoin_and_Altcoins
- **Slug:** `paper.zarattini_2025_crypto_trends`
- **Topic:** T5 — Crypto systematic trend following
- **Raw access:** N/A — no local raw; extraction based on abstract + WebFetch
- **Citation format:** `[paper.zarattini_2025_crypto_trends, §results]`

## Core thesis

A classic breakout methodology (Donchian channel ensemble across multiple lookbacks) applied to a **rotational top-20 crypto portfolio** survives realistic transaction costs, delivering material alpha over BTC buy-and-hold. Survivorship-bias-free dataset addresses the single biggest weakness of prior crypto backtests.

## Methodology snapshot

- **Assets:** Bitcoin + top-20 most liquid coins (rotational portfolio)
- **Dataset coverage:** all cryptos tradable since 2015, **survivorship-bias-free**
- **Strategy:** ensemble of Donchian channel models across multiple lookback periods; volatility-based position sizing
- **Cost model:** "portfolio technique to mitigate transaction costs" (not fully detailed in public abstract)
- **Exchange assumed:** not explicitly stated in abstract

## Key results

- **Sharpe ratio > 1.5 net-of-fees**
- **Annualized alpha 10.8% versus BTC buy-and-hold**
- Positive skewness characteristic of trend-following

## Applicability to ai-trade

- **HIGH relevance.** This is the **Phase 3.7-3 hypothesis H3 anchor** (crypto Donchian ensemble).
- **Pepperstone fit: partial.** Razor crypto CFDs BTC/ETH no commission, spread-only; leverage retail 2:1 (ASIC/CySEC); **swap long −20%/yr** caps holding to ~≤2 days.
- Paper's top-20 crypto rotation exceeds Pepperstone's ~30 crypto catalogue — Phase 3.7-3 implementation should use BTCUSD + ETHUSD subset.
- **Blocker (Phase 3.7-2):** Tiingo crypto has documented stale-data + weekend pollution (see BREADTH_NO_WINNER). Need Kraken / Coinbase / CryptoCompare direct feed.
- **Gap:** abstract does NOT disclose exact Donchian lookback params, PBO/DSR, or OOS window — Phase 3.7-3 implementation must independently validate.

## Related knowledge-base entries

- `paper.grayscale_2023_btc_momentum` — simpler MA-crossover precedent on BTC.
- `paper.palazzi_2025_crypto_passive` — peer-reviewed complement (Journal of Futures Markets).
- `books/universal_trend_tactics.md` (Penfold) — Donchian baseline in canonical trend-following literature.
