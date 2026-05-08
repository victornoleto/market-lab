# Follow the Leader: Enhancing Systematic Trend-Following Using Network Momentum

## Metadata

- **Authors:** Linze Li (Imperial College London), William Ferreira (UCL Alumni)
- **Year:** 2025
- **Venue:** arXiv preprint (2501.07135v1)
- **Source URL (primary):** https://arxiv.org/abs/2501.07135
- **Alt URL (HTML):** https://arxiv.org/html/2501.07135v1
- **Slug:** `paper.li_ferreira_2025_network_momentum`
- **Topic:** T10 — ML systematic / network momentum
- **Raw access:** N/A — extraction based on abstract + WebFetch
- **Citation format:** `[paper.li_ferreira_2025_network_momentum, §oos_results]`

## Core thesis

**Network Momentum Models (NMM)** combining Signature-based Lévy-area and Dynamic Time Warping variants to detect lead-lag relationships across 28 futures markets, then graph-learning to weight cross-sectional momentum contribution. Reports **26% Sharpe improvement over MACD baseline** — but the absolute Sharpe level remains modest.

## Methodology snapshot

- **Assets:** 28 futures contracts (agriculture, energy, metals, equity indices)
- **Period:** training Jun-2002 → Jun-2024; **OOS Jan-2005 → Jun-2024** (19-year out-of-sample)
- **Signal architecture:** (1) lead-lag detection via signature/DTW; (2) graph learning to sparsify adjacency; (3) ensemble across lookbacks δ ∈ {22, 44, 66, 88, 110, 132}
- **Cost model:** half bid-ask spread; t+1 execution / t+2 pnl recognition
- **Evaluation:** stationary block bootstrap (100 synthetic price paths) + real historical test

## Key results

| Metric | MACD baseline | Best NMM (SDDTW-E) |
|---|---|---|
| Sharpe (bootstrapped avg) | 0.277 | **0.350 (+26%)** |
| Skewness | 0.515 | 0.679 (+32%) |
| Profit/Loss ratio | 1.158 | 1.255 (+8%) |
| Max drawdown | 0.239 | 0.296–0.357 (worse) |

- Real historical Sharpe (NMM-SDDTW-E): **0.328** (below bootstrapped average)
- Transaction costs = 2–3% annualized drag

## Applicability to market-lab

- **LOW relevance for Phase 3.7-3.** Best Sharpe 0.35 net is **far below the Phase 3.6 gate 2 of 1.5** — a 4.3× improvement would be needed for viability.
- **STRONG EVIDENCE supporting the Phase 3.6 null interpretation.** State-of-art ML trend-following in peer-adjacent venue cannot break the gate either — reinforces that the null finding is robust, not an artifact.
- Pepperstone fit: partial — 28 futures subset not all Pepperstone-served.
- Not a candidate lead; archive as **literature-level null** reference.

## Related knowledge-base entries

- `paper.scidirect_2024_backtest_overfit` — complementary evidence that ML strategies are especially vulnerable to overfit.
- `books/advances_fin_ml.md` (López de Prado) — PBO/DSR framework the null-evidence demands.
- `books/evidence_based_ta.md` (Aronson) — 6,402-rule null study (canonical precursor).
