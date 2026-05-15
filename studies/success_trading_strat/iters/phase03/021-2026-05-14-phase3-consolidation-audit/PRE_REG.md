# PRE_REG - Phase 3 Iteration 021

## Hypothesis

Phase 3 has completed 20 local iterations with no `strict_winner`. The most
conservative next hypothesis is not another local parameter tweak, but a
consolidation audit: all prior Phase 3 claims should remain non-promotional if any
candidate lacks strict validation, artifact completeness, or aligned buy-and-hold
economic dominance. This follows the Phase 3 stop-rule discipline against tuning
after failed validation `[testing_tuning, p.327-335]` and preserves PBO/DSR as
hard controls `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Configs

- Audit target: all existing `studies/success_trading_strat/iters/phase03/001-*`
  through `020-*` directories.
- No strategy rule, indicator, weight, lookback, leverage or threshold is changed.
- No new backtest configuration is tested.
- Required artifact check per iteration: `PRE_REG.md`, `RESULTS.json`, `SUMMARY.md`.
- Required result fields: `iteration`, `status`, `pre_registered`, `n_trials`,
  `winner`, `gates`, `kill_switches`, `artifacts`.

## Data And Window

This is a metadata/results audit over saved Phase 3 artifacts, not a market-data
backtest. Market-data windows remain the windows recorded by each prior iteration.
No physical data substitution is allowed after the fact `[testing_tuning,
p.327-335]`.

## Benchmarks

- Primary benchmark: each prior iteration's pre-registered primary buy-and-hold
  benchmark from `RESULTS.json`.
- SPY opportunity benchmark: each prior iteration's recorded SPY buy-and-hold
  opportunity comparison where applicable.
- Phase 3 kill rule remains binding: if a strategy CAGR or terminal wealth is less
  than or equal to its primary B&H benchmark on aligned dates, it is `fail` and
  cannot be `economic_beater_not_validated`, `candidate_watchlist`,
  `paper_trade_candidate` or `strict_winner` `[systematic_trading, p.40]`.

## Planned Gates

- Artifact completeness for 20 prior Phase 3 iterations.
- Result schema completeness for 20 prior `RESULTS.json` files.
- Reconciled local Phase 3 trial sum versus memory expectation: prior local trials
  should sum to 80, taking `cumulative_n_trials` from 216 at Phase 3 start to 296.
- Zero `winner=true` and zero `strict_winner` unless all prior strict gates are
  true.
- Promotional-label guard: no `candidate_watchlist` or `paper_trade_candidate`
  should appear in prior Phase 3 results without explicit human selection.
- MCPT/PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib are not recomputed; their prior
  recorded pass/fail states remain binding `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.222-223]`.

## Kill Rules

- Any missing required artifact or required result field closes this audit as
  `fail`.
- Any prior `winner=true` without `status=strict_winner` and full gate pass closes
  this audit as `fail`.
- Any prior `candidate_watchlist` or `paper_trade_candidate` without a separate
  explicit human decision closes this audit as `fail`.
- Even if audit bookkeeping passes, the phase remains non-promotional unless a
  prior strategy is already a strict winner under recorded gates.

## Trial Accounting

- `cumulative_n_trials` before: 296.
- New strategy configs in this iteration: 0.
- `cumulative_n_trials` after: 296.
