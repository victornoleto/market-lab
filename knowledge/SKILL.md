---
name: trading-knowledge
description: Knowledge base for algorithmic swing trading built from 22 absorbed books. Use when designing strategies, selecting indicators, sizing positions, validating backtests, or reviewing any trading decision for the ai-trade project. Every recommendation MUST cite its source summary (knowledge/books/<slug>.md#section).
---

# Trading Knowledge — ai-trade Phase 0 Deliverable

This skill aggregates the extracted knowledge from the books absorbed in
Phase 0 of the `ai-trade` project. Use it when giving advice on:

- Strategy design (momentum, cycles, regime-aware)
- Indicator selection (Ehlers DSP, Clenow momentum, HMM)
- Position sizing (fractional Kelly, optimal f, risk of ruin)
- Backtest validation (CPCV, permutation tests, DSR, walk-forward)

## Inviolable Rules (enforce before any recommendation)

These rules are aggregated from the books and cannot be overridden without explicit
justification citing a source:

1. **Never recommend a strategy without citing its source** — every concept points to
   `books/<slug>.md` (and ideally a page: `books/<slug>.md#section`).
2. **Max 4 parameters per strategy** unless each extra parameter has economic/physical
   justification (source: `systematic_trading`, `advances_fin_ml`).
3. **Reject any backtest with PBO > 50%** (Probability of Backtest Overfitting).
   Compute via CPCV (see `validation/cpcv.md`).
4. **Apply Deflated Sharpe Ratio** when N strategies were tested — raw Sharpe is biased.
   See `validation/deflated_sharpe.md`.
5. **Walk-forward must cover ≥8 windows**, ≥6 profitable, none with drawdown > 25%.
   See `validation/walk_forward.md`.
6. **Fractional Kelly (≤ 0.25 × Kelly)** for live sizing — full Kelly is mathematically
   optimal but practically reckless. See `strategies/money_management.md`.
7. **Paper trade ≥3 months** before any live capital, regardless of backtest quality.
   See `TRADING_SYSTEM_PLAN.md` section 11.

## Navigation

### Thematic indexes (start here for strategy questions)

- **Strategies**
  - [`strategies/anti_overfitting.md`](strategies/anti_overfitting.md) — 7-layer defense
  - [`strategies/momentum.md`](strategies/momentum.md)
  - [`strategies/cycle_detection.md`](strategies/cycle_detection.md)
  - [`strategies/regime_change.md`](strategies/regime_change.md)
  - [`strategies/money_management.md`](strategies/money_management.md)
- **Indicators**
  - [`indicators/ehlers_indicators.md`](indicators/ehlers_indicators.md)
  - [`indicators/custom_momentum.md`](indicators/custom_momentum.md)
  - [`indicators/regime_hmm.md`](indicators/regime_hmm.md)
- **Validation**
  - [`validation/cpcv.md`](validation/cpcv.md)
  - [`validation/permutation.md`](validation/permutation.md)
  - [`validation/deflated_sharpe.md`](validation/deflated_sharpe.md)
  - [`validation/walk_forward.md`](validation/walk_forward.md)

### Per-book summaries

**Tier S — Essentials (0 absorbed):**

**Tier A — Technical foundation (0 absorbed):**

**Tier B — Depth and complement (0 absorbed):**

**Tier C — Reference (0 absorbed):**

**Not yet absorbed (22):**
- `books/advances_fin_ml.md` — Framework anti-overfit completo; CPCV, meta-labeling, DSR.
- `books/systematic_trading.md` — Parcimônia + position sizing robusto; design de sistemas.
- `books/trading_systems_methods.md` — Referência enciclopédica de métodos clássicos.
- `books/testing_tuning.md` — Validação estatística prática em C++.
- `books/stocks_on_the_move.md` — Momentum com 2 parâmetros — baseline.
- `books/rocket_science.md` — DSP para trading; Hilbert transform, MAMA.
- `books/cybernetic_analysis.md` — Continuação DSP; Fisher transform, Cyber Cycle.
- `books/cycle_analytics.md` — Ciclos adaptativos — últimos refinements de Ehlers.
- `books/math_money_mgmt.md` — Optimal f, risk of ruin, Kelly adaptado.
- `books/trading_evolved.md` — Sistemas em Python — ponte direta para o stack.
- `books/ml_for_algo_trading.md` — Guia pragmático ML + Python (Jansen).
- `books/stat_sound_indicators.md` — Aronson+Masters TSSB; rigor em indicadores.
- `books/evidence_based_ta.md` — Base estatística de Aronson; vies de data mining.
- `books/ml_for_asset_managers.md` — AFML condensado para portfolio management.
- `books/leverage_space.md` — Sizing multi-asset — extensão Kelly para portfolios.
- `books/regime_change.md` — HMM + regime change em finanças computacionais.
- `books/cybernetic_trading.md` — Intermarket + NN (Ruggiero 1997).
- `books/numerical_recipes.md` — Referência numérica (SVD, FFT, otimização).
- `books/data_driven_science.md` — Brunton & Kutz — PCA, SVD, dynamical systems.
- `books/tech_analysis_patterns.md` — Padrões de TA tratados algoritmicamente.
- `books/trading_on_sentiment.md` — Filtros de sentimento como complemento.
- `books/universal_trend_tactics.md` — Penfold — táticas de trend trading.

## Companion code (C++)

Reference implementations from Timothy Masters' books:

- `books/code/masters-assessing/` — prediction/classification quality (bootstrap, entropy)
- `books/code/masters-testing-tuning/` — backtest validation (MCPT, CSCV, drawdown bounds)

Use these as authoritative pseudocode when porting algorithms to Python in Phase 4/5.

## How to answer a trading question using this skill

1. Identify which thematic index is most relevant (strategies/ vs indicators/ vs validation/).
2. Read that file — it cross-references the specific books.
3. If needed, drill into `books/<slug>.md` for full context.
4. Cite your sources in the response: `books/<slug>.md#section [p.X]`.
5. If the knowledge base doesn't cover the question, say so explicitly — do NOT extrapolate
   or invent. That protects the user from advice not grounded in the literature.
