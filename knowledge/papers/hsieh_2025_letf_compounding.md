# Compounding Effects in Leveraged ETFs: Beyond the Volatility Drag Paradigm

## Metadata

- **Authors:** Chung-Han Hsieh, Jow-Ran Chang, Hui Hsiang Chen
- **Year:** 2025 (submitted April 28, 2025)
- **Venue:** arXiv preprint (2504.20116v1) — manuscript under review for publication
- **Source URL (primary):** https://arxiv.org/abs/2504.20116
- **Alt URL:** https://arxiv.org/html/2504.20116v1
- **Slug:** `paper.hsieh_2025_letf_compounding`
- **Topic:** T1 — LETF holding-period optimization + vol-decay mitigation
- **Raw access:** N/A — no local raw; extraction based on abstract + page fetch
- **Citation format:** `[paper.hsieh_2025_letf_compounding, §abstract]` or `[paper.hsieh_2025_letf_compounding, §methodology]`

## Core thesis

LETF performance depends fundamentally on **return autocorrelation and return dynamics**, not volatility drag alone. The "natural decay" narrative is incomplete — in markets with independent returns, LETFs exhibit **positive expected compounding effects** on their target multiples; in serially correlated markets, trends amplify returns while mean reversion induces underperformance.

## Methodology snapshot

- **Assets tested:** SPDR S&P 500 ETF (SPY) + Nasdaq-100 ETF (QQQ) across multiple leverage ratios
- **Period:** ~20 years of historical data
- **Framework:** AR(1) and AR-GARCH models, continuous-time regime switching, flexible rebalance frequencies (rolling-window estimates)
- **Cost model:** not detailed in abstract
- **OOS:** not explicitly mentioned in abstract

## Key results

No specific Sharpe ratio, CAGR, or MaxDD figures appear in the abstract. The paper documents empirical confirmation of theoretical predictions; quantitative metrics require full PDF access. Qualitative finding: **LETF outperforms in momentum regimes, underperforms in mean-reverting regimes**; daily rebalance is optimal in former, infrequent rebalance in latter.

## Applicability to market-lab

- **HIGH relevance.** Hypothesis H2 (VIX-gated LETF rotation) in Phase 3.7-3 hunt draws directly from this paper's regime-conditional framing.
- Provides theoretical justification for extending Gayed 2016/2020 with an explicit autocorrelation / regime classifier (AR(1) or HMM).
- Pepperstone-universe fit: direct — SPX500 / NAS100 CFDs with tier-1 retail leverage 20:1 match the paper's underlyings.

## Related knowledge-base entries

- `books/leverage_for_the_long_run.md` (Gayed 2016/2020) — predecessor; this paper extends the regime-filter argument beyond SMA to autocorrelation dynamics.
- `paper.lin_2025_letf_arbitrage` — parallel 2025 LETF paper focused on decay-capture arbitrage rather than rotation.
- `paper.pauchlyova_2025_letf_allocation` — practitioner survey applying LETF in trend-following allocations.
