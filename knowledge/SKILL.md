---
name: trading-knowledge
description: Knowledge base for algorithmic swing trading built from 33 absorbed books. Use when designing strategies, selecting indicators, sizing positions, validating backtests, or reviewing any trading decision for the ai-trade project. Every recommendation MUST cite its source summary (knowledge/books/<slug>.md#section).
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
6. **Position sizing must apply Sharpe shrinkage before computing Kelly** — true SR is
   estimated, not known; raw Kelly on an estimated edge is mathematically optimal but
   practically reckless (source: `systematic_trading`, capítulos de target vol / position
   sizing). Also validate regime-conditionality of Kelly (`advances_fin_ml`, ch.10) and
   risk-of-ruin under the assumed return distribution (`math_money_mgmt`, `leverage_space`).
   **Full Kelly unshrunk + unconditioned = reject on sight.** No fixed fractional multiplier
   is mandated by this skill — the factor is a per-strategy parameter, defended in backtest.
   See `strategies/money_management.md`.
7. **Paper trade ≥3 months** before any live capital, regardless of backtest quality.
   See `../ROADMAP.md` §Phase 4 (paper trading gate).

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

**Tier S — Essentials (7 absorbed):**
- [`books/advances_fin_ml.md`](books/advances_fin_ml.md) — Complete anti-overfit framework; CPCV, meta-labeling, DSR.
- [`books/systematic_trading.md`](books/systematic_trading.md) — Parsimony + robust position sizing; systems design.
- [`books/trading_systems_methods.md`](books/trading_systems_methods.md) — Encyclopedic reference of classical methods.
- [`books/testing_tuning.md`](books/testing_tuning.md) — Practical statistical validation in C++.
- [`books/stocks_on_the_move.md`](books/stocks_on_the_move.md) — Momentum with 2 parameters — baseline.
- [`books/eval_opt_strategies.md`](books/eval_opt_strategies.md) — Pardo — classical walk-forward; anti-overfit optimization framework.
- [`books/quant_trading_chan.md`](books/quant_trading_chan.md) — Chan — practical mean-reversion/momentum baseline and infra.

**Tier A — Technical foundation (8 absorbed):**
- [`books/rocket_science.md`](books/rocket_science.md) — DSP for trading; Hilbert transform, MAMA.
- [`books/cybernetic_analysis.md`](books/cybernetic_analysis.md) — DSP continuation; Fisher transform, Cyber Cycle.
- [`books/cycle_analytics.md`](books/cycle_analytics.md) — Adaptive cycles — Ehlers' latest refinements.
- [`books/math_money_mgmt.md`](books/math_money_mgmt.md) — Optimal f, risk of ruin, adapted Kelly.
- [`books/trading_evolved.md`](books/trading_evolved.md) — Systems in Python — direct bridge to the stack.
- [`books/ml_for_algo_trading.md`](books/ml_for_algo_trading.md) — Pragmatic ML + Python guide (Jansen).
- [`books/algo_trading_chan.md`](books/algo_trading_chan.md) — Chan — mean-reversion, momentum and practical execution.
- [`books/machine_trading.md`](books/machine_trading.md) — Chan — ML/quant strategies focused on execution.

**Tier B — Depth and complement (9 absorbed):**
- [`books/stat_sound_indicators.md`](books/stat_sound_indicators.md) — Aronson+Masters TSSB; rigor in indicators.
- [`books/evidence_based_ta.md`](books/evidence_based_ta.md) — Aronson's statistical foundation; data-mining bias.
- [`books/ml_for_asset_managers.md`](books/ml_for_asset_managers.md) — AFML condensed for portfolio management.
- [`books/leverage_space.md`](books/leverage_space.md) — Multi-asset sizing — Kelly extension for portfolios.
- [`books/regime_change.md`](books/regime_change.md) — HMM + regime change in computational finance.
- [`books/volatility_trading.md`](books/volatility_trading.md) — Sinclair — vol modeling, options and vol-based sizing.
- [`books/trading_exchanges.md`](books/trading_exchanges.md) — Harris — market microstructure, costs, liquidity.
- [`books/fin_time_series_tsay.md`](books/fin_time_series_tsay.md) — Tsay — academic reference for financial time series.
- [`books/big_data_ml_quant.md`](books/big_data_ml_quant.md) — Guida collection — ML applications in quant.

**Tier C — Reference (9 absorbed):**
- [`books/cybernetic_trading.md`](books/cybernetic_trading.md) — Intermarket + NN (Ruggiero 1997).
- [`books/numerical_recipes.md`](books/numerical_recipes.md) — Numerical reference (SVD, FFT, optimization).
- [`books/data_driven_science.md`](books/data_driven_science.md) — Brunton & Kutz — PCA, SVD, dynamical systems.
- [`books/tech_analysis_patterns.md`](books/tech_analysis_patterns.md) — TA patterns handled algorithmically.
- [`books/universal_trend_tactics.md`](books/universal_trend_tactics.md) — Penfold — trend-trading tactics.
- [`books/sentiment_analysis_handbook.md`](books/sentiment_analysis_handbook.md) — Mitra & Yu — sentiment in finance as overlay.
- [`books/time_series_hamilton.md`](books/time_series_hamilton.md) — Hamilton — classical time-series reference.
- [`books/adaptive_markets.md`](books/adaptive_markets.md) — Lo — adaptive markets hypothesis; theoretical context.
- [`books/risk_parity.md`](books/risk_parity.md) — Qian — portfolio construction by risk parity.

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
