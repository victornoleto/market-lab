# Backtest Overfitting in the Machine Learning Era: A Comparison of Out-of-Sample Testing Methods in a Synthetic Controlled Environment

## Metadata

- **Authors:** (first-author last-name unresolved in sprint) — ScienceDirect, Knowledge-Based Systems
- **Year:** 2024
- **Venue:** ScienceDirect (Knowledge-Based Systems, Elsevier) — peer-reviewed
- **Source URL (primary):** https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110
- **Slug:** `paper.scidirect_2024_backtest_overfit`
- **Topic:** T10 — Backtest overfitting in ML era / OOS testing methods
- **Raw access:** N/A — abstract only; extraction partial
- **Citation format:** `[paper.scidirect_2024_backtest_overfit, §synthetic]`

## Core thesis

ML strategies are **especially vulnerable to backtest overfitting**. Synthetic controlled-environment comparison of OOS testing methods confirms: **CSCV, PBO, DSR remain essential** regardless of model complexity. Correlation between log(total backtest days) and in-sample-vs-OOS Sharpe shortfall is weak but statistically significant and positive.

## Methodology snapshot

- **Environment:** synthetic data with known data-generating process (enables ground-truth overfit measurement)
- **Strategies tested:** multiple ML model classes (specifics not extracted)
- **Metrics:** PBO, DSR, Sharpe shortfall between IS and OOS
- **Cost model:** N/A (synthetic)
- **OOS:** the whole point — controlled comparison of various OOS methods

## Key results

- Strong evidence that **the more backtests run, the larger the IS-OOS Sharpe shortfall** — confirms López de Prado's DSR framing
- CSCV-based PBO remains a reliable detector in synthetic test
- No single OOS method dominates; triangulation (PBO + DSR + WF) is required

## Applicability to ai-trade

- **HIGH relevance as methodology justification.** This paper validates the Phase 3.6 13-gate stack (gates 11 PBO, 12 DSR, 6 WF) at the synthetic-ground-truth level.
- Complements the Phase 3.6 null interpretation: ML leads that pass the gates are statistically rare; most ML leads don't survive honest testing.
- Can be cited in Phase 3.7-3 gate-defense (if user asks "why PBO+DSR both?").

## Related knowledge-base entries

- `books/advances_fin_ml.md` (López de Prado) — PBO / DSR canonical reference.
- `books/evidence_based_ta.md` (Aronson) — permutation-test / data-mining-bias complement.
- `paper.li_ferreira_2025_network_momentum` — empirical instance of ML below gates in liquid markets.
