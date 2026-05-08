# Strategy Hunt Loop — Available Infrastructure

**Reuse, don't rebuild.** Each iteration should compose from these
modules. Build new modules only when the mechanism is qualitatively new
(then add a TDD spec under `tests/test_<slug>.py` first).

## Simulators

- `src/market_lab/backtest/strategies/ema_sma_threshold_educational.py`
- `src/market_lab/backtest/strategies/stop_loss_and_risk_signals.py`
  (stop + risk + combined + numpy cross-lib)

## Data loaders

- `src/market_lab/backtest/data/testfolio_loader.py` (SPYSIM synth 1986+)
- `src/market_lab/backtest/data/macro_data_loader.py` (EBP / T10Y3M / CAPE / VIX)
- `src/market_lab/backtest/grid/real_etf_regime_runner.py` (SPY/UPRO, QQQ/TQQQ bundles)

## Validation

- `src/market_lab/backtest/validation/pbo.py` (PBO via CSCV)
- `src/market_lab/backtest/validation/dsr.py` (Deflated Sharpe Ratio)
- `src/market_lab/backtest/validation/walk_forward.py`
- `src/market_lab/backtest/validation/cpcv.py`
- `src/market_lab/backtest/validation/permutation.py`

## Metrics

- `src/market_lab/backtest/metrics/performance.py` (CAGR / Sharpe / MDD / etc.)

## Signals

- `src/market_lab/backtest/signals/risk_score.py` (z-score sigmoid composite)

## Data cache

- `data/tiingo/daily/prices/*.parquet` — SPY, SSO, UPRO, QQQ, QLD,
  TQQQ, sector ETFs, factor ETFs, bonds
- `data/external/macro/*.parquet` — EBP / T10Y3M / CAPE / VIX
- `data/testfolio/cache/history.parquet` — SPYSIM synth 40y+

## Knowledge base

- `books/summaries/` — 33 absorbed books (slug ↔ title in `books/MAPPING.md`)
- `knowledge/SKILL.md` — aggregated quick-reference

## Iteration-specific code (reusable across iters)

- `studies/strategy_hunt_loop/iterations/006-*/` — 2-leg vol-managed blend
  (inverse-variance + Moreira-Muir variance-scaling)
- `studies/strategy_hunt_loop/iterations/008-*/` — single ex-ante cfg
  variant of the iter 006 blend
- `studies/strategy_hunt_loop/iterations/009-*/` — T10Y3M binary-haircut
  overlay scaffold (haircut wiring on existing blend)
- `studies/strategy_hunt_loop/iterations/010-*/three_leg_blend.py` +
  `numpy_reference_3leg.py` — 3-leg generalisation of inverse-variance
  weighting and the cross-lib parity check
- `studies/strategy_hunt_loop/iterations/011-*/weekly_three_leg_blend.py` +
  `numpy_reference_weekly.py` — weekly-cadence wrapper around the 3-leg
  blend (preserve as cadence-comparison reference)
