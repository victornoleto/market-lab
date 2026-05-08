# Momentum and Trend Following Trading Strategies for Currencies Revisited — Combining Academia and Industry

## Metadata

- **Authors:** Janick Rohrbach, Silvan Suremann, Joerg Osterrieder
- **Year:** 2017 (most-cited version; 2022-era update exists as companion extension)
- **Venue:** SSRN working paper (abstract_id=2949379); University of Twente / ZHAW research
- **Source URL (primary):** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2949379
- **Alt URL (ZHAW):** https://digitalcollection.zhaw.ch/handle/11475/15965
- **Slug:** `paper.rohrbach_2017_fx_momentum`
- **Topic:** T6 — FX momentum (G10 vs EM vs crypto)
- **Raw access:** N/A — extraction based on secondary summaries
- **Citation format:** `[paper.rohrbach_2017_fx_momentum, §g10_death]`

## Core thesis

EMA-based momentum / trend-following applied to currencies decomposes into different edge profiles across buckets. **Key verdict:** momentum **worked well on G10 majors until the 2008 financial crisis, and has not been profitable since**. Sharpe ratios higher for more volatile currencies — edge survives in **emerging-market fiat and cryptocurrencies**, not in G10.

## Methodology snapshot

- **Assets:** G10 majors (9 pairs), emerging-market currencies, Bitcoin (added in updated versions)
- **Signal:** EMA-based trend, crossover variants
- **Cost model:** standard retail (pips) — not explicit CSCV/PBO
- **OOS:** implicit via long series

## Key results

- **G10 momentum: profitable pre-2008, flat/negative post-2008** — explicitly reported
- EM and crypto: momentum Sharpe materially higher (volatile currencies favor TSMOM)
- Time-series momentum superior in fiat; cross-sectional superior in crypto

## Applicability to market-lab

- **HIGH relevance as anti-pattern reference.** If Phase 3.7-3 ever considers G10 FX momentum as standalone, cite this paper as **literature-level null finding**.
- **EM FX leads (H6)** can be considered — but Tiingo FX pre-2020 is limited, so Phase 3.7-2 data sprint would need additional feed (Dukascopy / OANDA historical).
- Pepperstone serves ~25 EM pairs as CFD; spreads are wide (USDTRY 5-15 pips).

## Related knowledge-base entries

- `paper.fan_2025_currency_factors` — modern framework that accepts G10 decay and optimizes around it.
- `books/systematic_trading.md` (Carver) — vol-target context for currency subsets.
