# PRE_REG - Phase 3 Iteration 026

## Hypothesis

Audit-only consolidation: after multiple Phase 3 economic beaters failed MCPT,
PBO, DSR, bootstrap, MDD or friction stress, the conservative hypothesis is that
no prior Phase 3 result can receive any promotional label unless every saved
`RESULTS.json` both preserves the Phase 3 economic gates and passes all strict
validation gates. This follows the stop/stress discipline for fragile discoveries
`[testing_tuning, p.327-335]`, the MCPT anti-data-mining gate
`[testing_tuning, p.318-320]`, PBO `[advances_fin_ml, p.208-211]` and DSR
selection-bias control `[advances_fin_ml, p.222-223]`.

## Config

One audit config, no strategy optimization and no new trading rule:

- Parse Phase 3 iteration directories `001` through `025`.
- Require `RESULTS.json` and `SUMMARY.md` for each parsed directory.
- Count statuses, winners and labels above `fail`.
- For every result with `status` in `economic_beater_not_validated`,
  `candidate_watchlist`, `paper_trade_candidate` or `strict_winner`, inspect saved
  gate fields and require no failed strict gate.
- Treat missing strict-gate keys on a promotional/economic result as a conservative
  failure, not as pass.

## Data And Window

Inputs are saved Phase 3 artifacts under
`studies/success_trading_strat/iters/phase03/`. This iteration does not read price
data directly and does not consume market-data window degrees of freedom.

## Benchmarks

Primary benchmark: candidate-specific Phase 3 primary buy-and-hold benchmarks as
pre-registered and saved in each prior `RESULTS.json`.

Opportunity benchmark: SPY buy-and-hold context where prior iterations saved it.

No new benchmark series is introduced; the audit only checks whether prior saved
claims remain eligible after their own benchmark and validation records.

## Kill Rule

If any prior result has `winner=true`, `strict_winner`, `candidate_watchlist` or
`paper_trade_candidate` while a required strict validation gate is failed/missing,
or if any `economic_beater_not_validated` remains blocked by failed strict gates,
this iteration must close `fail` and cannot promote a candidate.

Phase 3 economic rule remains binding: CAGR or terminal wealth <= the primary B&H
benchmark implies `fail` for that candidate and blocks any label above `fail`.

## Planned Gates

- Artifact completeness for Phase 3 results: pass only if every parsed prior
  iteration has `RESULTS.json` and `SUMMARY.md`.
- Trial reconciliation: saved `n_trials` sum must reconcile with local Phase 3
  trial count observed in artifacts.
- Promotional-label audit: zero `winner=true`, `strict_winner`,
  `candidate_watchlist` and `paper_trade_candidate` with failed/missing strict
  gates.
- Prior strict validation gates remain binding: MCPT/PBO/DSR/WF/OOS/FWD/bootstrap
  and cross-lib are not recomputed here `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Trial Accounting

- `cumulative_n_trials` before: 308.
- `n_trials` this audit: 0.
- `cumulative_n_trials` after: 308.

## Conservative Ambiguity Note

The working tree already contains modified public docs and Phase 3 artifacts beyond
the `MEMORY.md` state supplied for this session. This iteration treats
`MEMORY.md` (`total_iterations=25`, `cumulative_n_trials=308`) and the latest
Phase 3 `025` summary as the operational state, does not revert or edit unrelated
pre-existing changes, and records the inconsistency in `SUMMARY.md`.
