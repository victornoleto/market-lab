# PRE_REG - Phase 3 Iteration 029

## Hypothesis

Audit all Phase 3 `RESULTS.json` files available through iteration 028 to test a
conservative closure hypothesis: despite several economic beaters, no Phase 3
candidate should receive any promotional label unless it both beats the
pre-registered buy-and-hold benchmark in CAGR and terminal wealth and passes the
hard validation stack. This is an out-of-family audit, not a new strategy search,
because iteration 028 already showed the latest `QLD/TLT/GLD` beater is fragile
under rolling-window robustness and prior MCPT/DSR failures remain binding
`[testing_tuning, p.327-335]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.222-223]`.

## Exact Config

- Scope: parse `studies/success_trading_strat/iters/phase03/001-*` through
  `028-*` only.
- Inputs: each iteration `RESULTS.json`; no strategy return recomputation and no
  parameter reselection.
- Trial accounting: `n_trials=0` because this is audit/stress accounting only,
  not a new configuration trial `[advances_fin_ml, p.222-223]`.
- Promotional-block logic:
  - count `winner=true` or `status=strict_winner` as a strict candidate only if
    all reported hard gates pass;
  - count `status=economic_beater_not_validated` as economically interesting but
    blocked;
  - count `candidate_watchlist` or `paper_trade_candidate` as invalid for this
    audit unless the strict gates are explicitly all passing.

## Data And Window

This audit uses saved iteration artifacts only. It does not touch market data and
does not create new aligned price windows. The underlying tested windows remain
the windows registered inside the source iterations.

## Benchmarks

- Primary benchmark: each source iteration's pre-registered primary buy-and-hold
  benchmark as recorded in its own `RESULTS.json` and `PRE_REG.md`.
- SPY opportunity benchmark: each source iteration's own SPY opportunity benchmark
  when present.
- Same-asset buy-and-hold: each source iteration's own same-asset or opportunity
  universe benchmark when present.

## Kill Rule

If any source iteration lacks explicit proof that CAGR and terminal wealth beat
its primary B&H benchmark, treat it as not promotable. If any economic beater
fails MCPT, PBO, DSR, WF, OOS, FWD, bootstrap or cross-lib, close this iteration
as `fail` and do not assign `economic_beater_not_validated`, `candidate_watchlist`,
`paper_trade_candidate` or `strict_winner` to this audit.

## Planned Gates

- Artifact completeness: `RESULTS.json` exists and parses for every directory
  001-028.
- Strict winner audit: zero strict winners unless all hard gates pass
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- Promotional-label audit: zero `candidate_watchlist` and zero
  `paper_trade_candidate` promoted by automation.
- Trial reconciliation: sum source `n_trials` and report the difference versus
  `MEMORY.md` `cumulative_n_trials`; do not rewrite history if prior state is
  ambiguous.

## Cumulative Trials

- Before: `312` per user-supplied state and `MEMORY.md`.
- This iteration: `0`.
- After: `312`.

## Ambiguity Handling

`docs/CURRENT_STATE.md` contains public lines that appear ahead of the supplied
loop state. Conservatively, this iteration follows the user-supplied state and
`MEMORY.md` (`total_iterations=28`, `cumulative_n_trials=312`) and records any
artifact/history mismatch in `SUMMARY.md` without reverting unrelated files.
