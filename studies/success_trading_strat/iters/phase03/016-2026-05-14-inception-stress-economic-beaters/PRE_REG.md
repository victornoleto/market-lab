# PRE_REG - Phase 3 Iteration 016

## Hypothesis

Prior Phase 3 economic beaters may be artifacts of favorable inception dates rather
than robust buy-and-hold beaters. This iteration performs a conservative
inception-window sensitivity audit across the previously recorded economic beaters,
without changing their rules, weights, lookbacks or rebalance cadence. The stress is
motivated by the requirement to test robustness after a promising result rather than
locally tune a fragile family `[testing_tuning, p.327-335]`, and by the fact that
path-dependent leverage and sizing can depend strongly on return ordering and start
state `[leverage_for_the_long_run, p.13]`, `[leverage_space, p.149-167]`.

This is a stress/consolidation iteration, not a new strategy search. No new
candidate can be promoted from this audit.

## Configs

Pre-registered prior economic beaters to audit from saved `returns.csv` artifacts:

- `010:upro50_tlt25_gld25_quarterly` versus `SPY` and equal-weight `UPRO/TLT/GLD`.
- `011:sso75_tlt15_gld10_quarterly` versus `SPY` and equal-weight `SSO/TLT/GLD`.
- `012:upro50_tmf30_gld20_quarterly` versus `SPY` and equal-weight `UPRO/TMF/GLD`.
- `013:qld_tqqq_dd25_recover_sma50_rv40` versus `QQQ` and equal-weight `QQQ/QLD/TQQQ`.
- `014:upro125_tlt25_sma200` versus `SPY` and equal-weight `UPRO/TLT/SHV`.

Inception stress windows, aligned to each return series and available benchmark
files:

- full saved window;
- start `2010-01-01`;
- start `2015-01-01`;
- start `2020-01-01`.

## Data And Window

Inputs are saved daily strategy returns from Phase 3 iteration artifacts plus local
Tiingo daily adjusted closes for benchmark assets. Required physical files:

- `SPY`, `QQQ`, `UPRO`, `SSO`, `QLD`, `TQQQ`, `TLT`, `TMF`, `GLD`, `SHV`.

If any required benchmark file is physically absent, close `data_blocked` without
substitution. Manifest-only evidence is insufficient.

## Benchmarks

Primary benchmarks are both the same-market buy-and-hold anchor and the equal-weight
opportunity-universe buy-and-hold listed per config above. `SPY` buy-and-hold is the
opportunity benchmark for all rows, including the Nasdaq row, where `QQQ` remains the
same-market anchor.

## Economic Kill Rule

For every config and every stress window with at least 252 observations:

- strategy CAGR must be greater than the same-market buy-and-hold CAGR;
- strategy terminal wealth must be greater than the same-market buy-and-hold terminal wealth;
- strategy CAGR must be greater than the equal-weight opportunity benchmark CAGR;
- strategy terminal wealth must be greater than the equal-weight opportunity benchmark terminal wealth.

Any failure means the prior economic beater is not inception-robust. Because prior
iterations already failed MCPT/DSR or other hard gates, this audit cannot label any
row above `economic_beater_not_validated`; if any inception window fails, the
iteration verdict is `fail`.

## Planned Gates

This stress iteration recomputes economic gates only. It records prior validation
failures as binding context and does not recompute MCPT, PBO, DSR, WF, OOS, FWD,
bootstrap or cross-lib. MCPT/PBO/DSR remain hard controls from the original
iterations `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Trial Accounting

- `cumulative_n_trials_before`: 284.
- New strategy configs: 0, because this is a pre-registered stress audit of already
  counted candidates.
- `cumulative_n_trials_after`: 284.
