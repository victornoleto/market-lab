# PRE_REG - Phase 3 Iteration 017

## Hypothesis

Prior Phase 3 economic beaters may be start-date robust at coarse inception points
but still fail when evaluated across rolling investor holding windows. This
iteration audits the already-tested economic beaters from Phase 3 iterations 010,
011, 012, 013 and 014 over rolling 3-year and 5-year windows, without changing any
strategy rule, weight, rebalance cadence, trigger, volatility cap or financing
assumption. Rolling stress is a robustness check against local overfit and fragile
selection after discovery `[testing_tuning, p.327-335]`; leveraged sleeve and
crash-rearm mechanisms remain path-dependent and must be stress-tested across
regimes `[leverage_for_the_long_run, p.4-7]`, `[leverage_for_the_long_run, p.13]`,
`[leverage_space, p.149-167]`.

## Configs

No new strategy configs are introduced. The audit consumes `n_trials=0`.

- Iter 010: `upro50_tlt25_gld25_quarterly` from saved `returns.csv`.
- Iter 011: `sso75_tlt15_gld10_quarterly` from saved `returns.csv`.
- Iter 012: `upro50_tmf30_gld20_quarterly` from saved `returns.csv`.
- Iter 013: `qld_tqqq_dd25_recover_sma50_rv40` from saved `returns.csv`.
- Iter 014: `upro125_tlt25_sma200` from saved `returns.csv`.

## Data And Window

Use saved Phase 3 return series for the audited configs and physical Tiingo daily
parquets for the aligned benchmark assets. Required physical files: `SPY`, `QQQ`,
`UPRO`, `SSO`, `QLD`, `TQQQ`, `TLT`, `TMF`, `GLD`, `SHV`.

Rolling windows:

- 3 years: 756 trading observations.
- 5 years: 1260 trading observations.
- Step: 63 observations.

## Benchmarks

Primary benchmark hierarchy per original iteration:

- Iter 010: must beat both `SPY` buy-and-hold and equal-weight `UPRO/TLT/GLD`.
- Iter 011: must beat both `SPY` buy-and-hold and equal-weight `SSO/TLT/GLD`.
- Iter 012: must beat both `SPY` buy-and-hold and equal-weight `UPRO/TMF/GLD`.
- Iter 013: must beat both `QQQ` buy-and-hold and equal-weight `QQQ/QLD/TQQQ`.
- Iter 014: must beat both `SPY` buy-and-hold and equal-weight `UPRO/TLT/SHV`.

SPY buy-and-hold is retained as opportunity-cost context for all candidates, but
for iter 013 the stricter primary already includes `QQQ` plus its opportunity
universe `[systematic_trading, p.40]`.

## Kill Rule

If any audited candidate has rolling-window CAGR or terminal wealth less than or
equal to any pre-registered primary buy-and-hold benchmark, the audit closes
`fail`. Prior validation failures (MCPT/PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib) are
not erased by rolling economic success; they remain binding hard blockers
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Gates Planned

- Rolling 3y and 5y economic CAGR vs primary B&H benchmarks.
- Rolling 3y and 5y terminal wealth vs primary B&H benchmarks.
- Physical daily-file audit for required benchmark assets.
- MCPT, PBO, DSR, WF, OOS, FWD, bootstrap and cross-lib are not recomputed; the
  original failures remain binding.

## Trial Accounting

- `cumulative_n_trials` before: 284.
- New strategy trials: 0.
- `cumulative_n_trials` after: 284.
