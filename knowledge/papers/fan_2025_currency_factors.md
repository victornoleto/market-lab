# Optimizing Currency Factors

## Metadata

- **Authors:** Minyou Fan, Fearghal Kearney, Youwei Li, Jiadong Liu
- **Year:** 2025 (published July 2025)
- **Venue:** Financial Review (Wiley, peer-reviewed)
- **Source URL (primary):** https://onlinelibrary.wiley.com/doi/10.1111/fire.70000
- **Alt URL (SSRN):** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4965896
- **Slug:** `paper.fan_2025_currency_factors`
- **Topic:** T6 — FX / currency factor investing
- **Raw access:** N/A — paywalled; extraction based on abstract + WebFetch snippets
- **Citation format:** `[paper.fan_2025_currency_factors, §framework]`

## Core thesis

Introduces a framework that **dynamically optimizes currency factor strategies** (carry, momentum, value, time-series momentum, return-signal momentum) via spot + forward trading. **Key innovation: explicit data-snooping-bias correction** — 24,336 portfolio-optimization approaches tested, only those surviving correction pass.

## Methodology snapshot

- **Data:** G10 currency spot + forward; sample period November 1989 – November 2020
- **Scope:** 24,336 portfolio-optimization configurations
- **Factors covered:** carry, momentum, value, TSMOM, return-signal momentum
- **OOS procedure:** aggregates top performers after data-snooping correction
- **Cost model:** not explicit in public abstract

## Key results

- Optimized currency factors **significantly outperform naïve factors** after correction
- **Carry strategy Sharpe rises from 0.71 (naïve) to 1.29 (after real-time hedging of unpriced risks)**
- Framework applicable to both symmetric and asymmetric (TSMOM) factor portfolios

## Applicability to ai-trade

- **MEDIUM–HIGH relevance.** This is the **state-of-art framework** for G10 FX factor investing 2022-2026.
- **Pepperstone fit: HIGH** for instrument (majors spreads 0.1-0.2 pips Razor + $3.50/lot/side commission)
- **Computational cost:** 24k optimization configs is heavy — Phase 3.7-3 adaptation would require subset.
- **Data blocker (Phase 3.7-2):** Tiingo FX pre-2020 coverage is limited.
- **Supporting context for H6** (FX EM TSMOM) if Phase 3.7-3 explores G10 complementarity.

## Related knowledge-base entries

- `paper.rohrbach_2017_fx_momentum` — evidence that G10 momentum *alone* is dead post-2008; hence Fan 2025's optimization framework is needed.
- `books/systematic_trading.md` (Carver) — classical vol-target framework; currency subset.
