# PRE_REG — 009-seasonal-hirsch-window

## Hypothesis

Test a pre-fixed Hirsch/Kaeppel seasonal window: hold leveraged SPY exposure only
during the historically favorable November-April window and hold cash during
May-October. Kaufman summarizes Hirsch's seasonal rule as buying the first
trading day of November and selling the last trading day of April
`[trading_systems_methods, p.480]`; the test keeps that calendar mechanism fixed
and does not optimize months, entry days, or exits.

## Exact Configs

Two configs, both one-bar/day executable with return applied only after the
calendar state is known:

- `hirsch_nov_apr_sso_cash`: `SSOSIM` during months 11, 12, 1, 2, 3, 4; `CASHX`
  during months 5, 6, 7, 8, 9, 10.
- `hirsch_nov_apr_upro_cash`: `UPROSIM` during months 11, 12, 1, 2, 3, 4; `CASHX`
  during months 5, 6, 7, 8, 9, 10.

No local tuning is allowed after seeing results. The month set is fixed by the
published seasonal rule `[trading_systems_methods, p.480]`.

## Data And Window

- Source: `data/testfolio/cache/history.parquet` via `load_testfolio_series`.
- Required labels: `SPYSIM`, `SSOSIM`, `UPROSIM`, `CASHX`.
- Expected common window: approximately 1986-01-03 through 2026-04-17, using the
  intersection of all required series.
- Benchmark: same-window `SPYSIM` buy-and-hold.

## Gates Planned

- Economic: candidate CAGR > same-window SPY CAGR and terminal equity ratio > 1.
- PBO `< 0.5` using the two pre-registered configs, with the same small-N
  instability warning used in prior two-config iterations `[advances_fin_ml,
  p.208-211]`.
- DSR `p < 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 windows beat SPY `[testing_tuning, ch.12]`.
- OOS final 25% and FWD final 3y must beat SPY `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% daily excess-return CI low must be positive
  `[advances_fin_ml, p.196-202]`.
- Cross-lib parity: vectorized implementation and explicit-loop implementation
  CAGR within +/-3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If best config does not beat SPY CAGR and terminal wealth, mark `fail`.
- If any hard gate fails, mark `fail`; PBO/DSR are not optional diagnostics.
- If the family only works in a narrow modern window or fails OOS/FWD, do not
  continue local seasonal date tuning.
- If required labels are unavailable, mark `data_blocked` and do not substitute.

## Trial Accounting

- `cumulative_n_trials` before: 16.
- `n_trials` planned: 2.
- `cumulative_n_trials` after: 18.

## Conservative Ambiguity Handling

There are pre-existing unrelated worktree changes in public docs and other
studies. This iteration will not revert them. Public docs will not be edited in
this iteration unless required by the loop artifacts; the conservative record is
kept here, `RESULTS.json`, `SUMMARY.md`, and `MEMORY.md`.
