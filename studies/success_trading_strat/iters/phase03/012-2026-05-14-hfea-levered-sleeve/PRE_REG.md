# PRE_REG - Phase 3 Iteration 012

## Hypothesis

Test a distinct controlled-leverage sleeve using real embedded-leverage ETFs:
`UPRO` for equity beta, `TMF` for leveraged Treasury crisis convexity and `GLD`
as a non-equity diversifier. The return engine is persistent leveraged equity
exposure plus imperfectly correlated leveraged bond/gold sleeves, not a daily
long/flat defensive filter `[leverage_for_the_long_run, p.13]`,
`[systematic_trading, p.137-148]`, `[leverage_space, p.149-167]`.

This is a different mechanism from iteration 011 because the defensive sleeve is
itself leveraged (`TMF`) rather than unlevered `TLT`. This raises path-dependency
risk, so validation remains hard-blocking `[testing_tuning, p.327-335]`.

## Data And Window

Required physical daily parquet files before testing: `UPRO`, `TMF`, `GLD`,
`SPY`, `SHV`. Manifest entries alone are insufficient. If any required file or
close column is absent, close `data_blocked` without substituting synthetic TMF.

Aligned test window is the intersection of available daily adjusted-close series.
The script must record rows, first/last date, columns, timezone and missing
business-day rate in `audit.json`.

## Exact Configs

Four fixed-weight sleeves, no local tuning after results:

- `upro40_tmf40_gld20_quarterly`: 40% `UPRO`, 40% `TMF`, 20% `GLD`, quarterly rebalance.
- `upro45_tmf35_gld20_quarterly`: 45% `UPRO`, 35% `TMF`, 20% `GLD`, quarterly rebalance.
- `upro50_tmf30_gld20_quarterly`: 50% `UPRO`, 30% `TMF`, 20% `GLD`, quarterly rebalance.
- `upro45_tmf45_gld10_monthly`: 45% `UPRO`, 45% `TMF`, 10% `GLD`, monthly rebalance.

Trial count: `n_trials=4` `[advances_fin_ml, p.222-223]`.

## Benchmarks

Primary Phase 3 economic benchmark is conservative dual buy-and-hold:

- `SPY` buy-and-hold on the same aligned dates.
- Equal-weight `UPRO/TMF/GLD` buy-and-hold on the same aligned dates.

Opportunity/context benchmarks: `UPRO`, `TMF`, `GLD`, `SHV` buy-and-hold.

## Kill Rules

- If strategy CAGR <= primary benchmark CAGR for either `SPY` or equal-weight
  `UPRO/TMF/GLD`, status must be `fail`.
- If strategy terminal wealth <= primary benchmark terminal wealth for either
  primary benchmark, status must be `fail`.
- If `TMF` is missing physically, status must be `data_blocked`; do not synthesize.
- If economic gates pass but any hard validation gate fails, status can be at most
  `economic_beater_not_validated`; no `candidate_watchlist`, `paper_trade_candidate`
  or `strict_winner` `[testing_tuning, p.318-320]`.
- If MDD is worse than 1.5x the worse primary benchmark MDD, block `strict_winner`
  even if return is high.

## Planned Gates

- IS MCPT, fixed-rule joint row permutation, 200 reps, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT, first 756 observations fixed, 252-observation test windows, 100 reps,
  pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` on the four config return matrix `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward at least 6 positive windows with at least 8 total windows
  `[testing_tuning, p.148-150]`.
- Single-block OOS positive, latest 63d FWD positive, bootstrap 99.9% mean daily
  CI low > 0 and cross-lib/reference CAGR delta <= 3pp `[advances_fin_ml,
  p.196-202]`, `[testing_tuning, p.246-247]`, `[advances_fin_ml, p.31-34]`.

## Trial Accounting

- `cumulative_n_trials_before=268`.
- `n_trials=4`.
- `cumulative_n_trials_after=272`.

## Guardrails

Capital remains 100% Plano C; no deploy, no paper trade, no commit/push. Existing
dirty worktree changes are not part of this iteration and are not reverted.
