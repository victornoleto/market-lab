# PRE_REG - Phase 3 Iteration 009

## Hypothesis

Test a high-beta relative-momentum long/short mechanism over `QQQ`, `SMH`,
`SOXX` and `XLK`: stay long the strongest asset(s), short the weakest asset and
explicitly charge a financing/borrow proxy. The return engine is cross-sectional
relative strength plus modeled gross exposure, not defensive cash timing
`[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`,
`[systematic_trading, p.137-148]`.

## Data And Window

Physical daily parquet files required before testing:

- Traded universe: `QQQ`, `SMH`, `SOXX`, `XLK`.
- Benchmarks/context: `SPY`, `SHV`.

Use the common adjusted-close window after dropping missing rows. Record rows,
first/last date, columns, timezone and missing-business-day rate in `audit.json`.

## Configs

Four pre-registered configs, all one-bar lagged:

| name | lookback | long legs | short legs | gross | financing/borrow proxy |
|---|---:|---:|---:|---:|---:|
| `ls_m63_top1_bottom1_g100` | 63 | 1 | 1 | 1.00 | 5% annual on short notional + gross above 1 |
| `ls_m63_top1_bottom1_g150` | 63 | 1 | 1 | 1.50 | 5% annual on short notional + gross above 1 |
| `ls_m126_top1_bottom1_g150` | 126 | 1 | 1 | 1.50 | 5% annual on short notional + gross above 1 |
| `ls_m126_top2_bottom1_g150` | 126 | 2 | 1 | 1.50 | 5% annual on short notional + gross above 1 |

Weights are scaled so gross exposure equals the configured gross: half gross on
the long book and half gross on the short book. The top-2 config splits the long
book equally.

## Benchmarks

Primary buy-and-hold benchmark: equal-weight `QQQ/SMH/SOXX/XLK` buy-and-hold on
the exact aligned dates, per Phase 3 multi-asset rotation mapping.

SPY opportunity benchmark: `SPY` buy-and-hold on the same aligned dates.

Context benchmarks: individual `QQQ`, `SMH`, `SOXX`, `XLK` buy-and-hold and `SHV`.

## Economic Kill Rule

If best strategy CAGR or terminal wealth is less than or equal to the primary
equal-weight buy-and-hold benchmark on aligned dates, status must be `fail`. No
`economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate` or
`strict_winner` label is allowed without beating both CAGR and terminal wealth.

## Planned Gates

- IS MCPT with joint row-permuted daily returns, 200 reps, pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with preserved initial train and permuted tail, 100 reps, pass
  `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the four configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positives at least 6 positive windows with at least 8 windows
  available `[testing_tuning, p.148-150]`.
- OOS positive, latest 63d FWD positive, bootstrap 99.9% mean daily CI low > 0,
  and vector/reference cross-lib CAGR delta <= 3pp `[advances_fin_ml, p.196-202]`,
  `[testing_tuning, p.246-247]`, `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Missing required physical daily parquet or close column => `data_blocked`.
- Economic B&H gate failure => `fail` even if validation diagnostics improve.
- Any PBO/DSR/MCPT/WF/OOS/FWD/bootstrap/cross-lib failure blocks `strict_winner`.
- Do not tune lookbacks, long/short counts, gross or financing after seeing
  results in this iteration `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 256.
- New strategy configs: 4.
- `cumulative_n_trials` after: 260.
