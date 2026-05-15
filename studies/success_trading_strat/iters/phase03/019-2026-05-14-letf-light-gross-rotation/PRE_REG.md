# PRE_REG - Phase 3 Iteration 019

## Hypothesis

Test an always-invested LETF-light/high-beta relative-rotation mechanism: rank
`QLD`, `SSO`, `SMH` and `SOXX` by lagged total-return momentum, hold the top
asset or top two assets, and optionally use modest gross exposure with an explicit
5% annual financing drag. The return engine is stronger exposure selection plus
controlled leverage, not a defensive long/flat cash filter `[stocks_on_the_move,
p.66-67]`, `[trading_systems_methods, p.542-544]`, `[systematic_trading,
p.137-148]`.

This is research-only. Capital remains 100% Plano C; no deploy, no paper-trade
claim.

## Data And Window

Physical daily parquet files required before testing:

- Traded universe: `QLD`, `SSO`, `SMH`, `SOXX`.
- Benchmarks/context: `SPY`, `QQQ`, `SHV`.

Use adjusted close where available. Align all assets on common trading dates and
start after the first valid lagged momentum signal. Record rows, first/last date,
columns, timezone and missing-business-day rate in `audit.json`. If any required
file is absent, close `data_blocked` without substituting a proxy.

## Exact Configs

Four strategy configs, all monthly rebalance using lagged signals:

1. `top1_m63_g100`: top-1 by 63-day momentum, gross 1.00, equal weight.
2. `top2_m63_g125`: top-2 by 63-day momentum, gross 1.25, equal weight, 5% annual financing on gross above 1.00.
3. `top1_m126_g100`: top-1 by 126-day momentum, gross 1.00, equal weight.
4. `top2_m126_g125`: top-2 by 126-day momentum, gross 1.25, equal weight, 5% annual financing on gross above 1.00.

No local tuning after results. These four configs consume four DSR trials.

## Benchmark Hierarchy

Primary Phase 3 economic benchmark:

- Equal-weight buy-and-hold of the opportunity universe `QLD/SSO/SMH/SOXX` on the
  aligned dates.

Required opportunity benchmark:

- `SPY` buy-and-hold on the same aligned dates.

Context benchmarks:

- `QQQ` buy-and-hold.
- Individual `QLD`, `SSO`, `SMH`, `SOXX` buy-and-hold.

## Economic Kill Rule

If the selected best config has CAGR <= primary equal-weight B&H CAGR or terminal
wealth <= primary equal-weight B&H terminal wealth, the iteration status is `fail`.
If it does not also beat `SPY` buy-and-hold CAGR, the iteration status is `fail`.
No `economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate`
or `strict_winner` label is allowed without the primary CAGR and terminal wealth
beats `[systematic_trading, p.40]`.

## Planned Gates

- IS MCPT: fixed-rule joint row permutation, 200 reps, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: preserve first 756 observations, permute the tail jointly, 100 reps,
  pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO: 10-block PBO across the four configs, pass `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: best config using cumulative `n_trials=292`, pass `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: 756 train / 252 test / 252 step, at least 6 positive windows and
  at least 8 windows total `[testing_tuning, p.148-150]`.
- OOS: final 20% compounded return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 trading days positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/reference parity: vectorized reference CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Missing required physical daily files => `data_blocked`.
- CAGR or terminal wealth <= primary equal-weight buy-and-hold => `fail`.
- CAGR <= `SPY` opportunity buy-and-hold => `fail`.
- Any hard validation failure blocks `strict_winner`; if economic gates pass but
  validation fails, status may be only `economic_beater_not_validated`.
- Gross exposure and financing assumptions must be reported; no tax model is
  claimed.

## Trial Accounting

- `cumulative_n_trials` before: 288.
- `n_trials` this iteration: 4.
- `cumulative_n_trials` after: 292.
