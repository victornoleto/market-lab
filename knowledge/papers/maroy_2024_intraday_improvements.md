# Improvements to Intraday Momentum Strategies Using Parameter Optimization and Different Exit Strategies

## Metadata

- **Author:** Ákos Maróy
- **Year:** 2024
- **Venue:** SSRN working paper (abstract_id=5095349)
- **Source URL (primary):** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5095349
- **Slug:** `paper.maroy_2024_intraday_improvements`
- **Topic:** T3 — Short-hold intraday momentum (exit refinement)
- **Raw access:** N/A — no local raw; extraction based on abstract + secondary review
- **Citation format:** `[paper.maroy_2024_intraday_improvements, §exit_strategies]`

## Core thesis

Direct extension of Zarattini-Aziz-Barbon 2024 noise-boundary framework with improved **exit strategies** (VWAP, Ladder, VWAP+Ladder) and parameter optimization. Reports headline Sharpe > 3.0 and annualized return > 50% for best config — but **overfit-risk is material** given parameter grid search on the same universe.

## Methodology snapshot

- **Base signal:** noise-boundary framework inherited from Zarattini 2024
- **Added features:** exit variants (VWAP, Ladder hybrid); parameter grid optimization
- **Period / assets:** coincident with base paper (SPY intraday)
- **Cost model:** inherited from Zarattini 2024 (commission + slippage as explicit per-share costs)
- **OOS / PBO / DSR:** NOT explicitly described — the parameter optimization over the same backtest window introduces selection bias that CSCV/PBO was designed to detect

## Key results

- **Best config: Sharpe > 3.0, annualized return > 50%**
- Best exit strategies: VWAP, VWAP+Ladder, Ladder
- **⚠ Reported numbers are IS-biased until independently validated with CSCV/PBO on the same instrument.**

## Applicability to ai-trade

- **Secondary lead for Phase 3.7-3 hunt (H1 refinement).** Should ONLY be tested as extension of H1 Zarattini 2024 baseline, not as standalone.
- Must be subjected to the Phase 3.6 13-gate stack rigorously — headline Sharpe > 3 is **exactly the pattern** (e.g., V2-L2 Gayed Sharpe 2.28 → 0.56 honest) that the engine look-ahead investigation exposed.
- Pepperstone-universe fit: same as Zarattini 2024 (SPX500 CFD).

## Related knowledge-base entries

- `paper.zarattini_2024_intraday_spy` — parent framework; this paper is a delta.
- `books/advances_fin_ml.md` (CSCV/PBO, p.208-211) — apply before trusting this paper's numbers.
