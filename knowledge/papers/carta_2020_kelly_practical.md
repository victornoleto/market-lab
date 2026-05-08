# Practical Implementation of the Kelly Criterion: Optimal Growth Rate, Number of Trades, and Rebalancing Frequency for Equity Portfolios

## Metadata

- **Authors:** Andrea Carta, Claudio Conversano
- **Year:** 2020
- **Venue:** Frontiers in Applied Mathematics and Statistics (Mathematical Finance section)
- **Source URL (primary):** https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2020.577050/full
- **Alt URL (PDF):** https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2020.577050/pdf
- **Slug:** `paper.carta_2020_kelly_practical`
- **Topic:** T4 — Kelly implementation / rebalancing frequency
- **Raw access:** N/A — no local raw; extraction based on abstract + WebFetch
- **Citation format:** `[paper.carta_2020_kelly_practical, §rebalancing]`

## Core thesis

Full Kelly yields **highest median terminal wealth** in long-horizon simulations (40k+ trades) — but with **drawdowns materially larger** than mean-variance. Daily rebalance with 24-month rolling optimization window dominates monthly in European equities; concentration in 2–3 assets is characteristic (vs 8+ for diversified alternatives).

## Methodology snapshot

- **Assets:** 42 equities from EuroStoxx50 index
- **Period:** January 2000 – December 2018 (daily)
- **Rolling OOS:** 24-month lookback windows, monthly/daily rebalance comparison
- **Single-stock case study:** Banca Intesa 2007–2018
- **Cost model:** **NO transaction costs** — hard limitation for direct transport to market-lab mandate (gate 13 cost-sensitivity binding)

## Key results

- Kelly daily rebalance, 2-yr window: **CAGR 15.01% vs 10.55% min-variance**
- But **MDD 24.52% vs 15.74%** — Kelly pays for the return with drawdown
- Kelly portfolios lie on efficient frontier but concentrate in 2–3 assets
- Longer rolling windows hurt; monthly rebalance degrades daily's edge

## Applicability to market-lab

- **MEDIUM relevance.** Frictionless assumption prevents direct use. Insight **usable**: Kelly on equities rewards daily rebalance + 2-yr rolling vol estimation, at the cost of elevated drawdown.
- For Phase 3.7-3, combine with Wysocki 2024 fractional-Kelly × VIX scaling (H4) to cap drawdown back to acceptable range.

## Related knowledge-base entries

- `books/math_money_mgmt.md` (Vince) — canonical Kelly / optimal-f.
- `paper.wysocki_2024_kelly_vix` — modern hybrid with cost awareness.
- `paper.downey_2023_fractional_kelly` — Monte-Carlo guidance on fractional scaling.
