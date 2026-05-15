# PRE_REG - Phase 3 Iteration 027

## Hypothesis

Test a monthly `QLD/TLT/GLD` sleeve that stays invested but changes gross `QLD`
exposure based on lagged realized volatility of `QQQ`. The return engine is LETF
participation plus controlled gross exposure, not a cash filter. Low realized
volatility permits more gross exposure; high realized volatility cuts gross toward
the base sleeve. This follows the Phase 3 mandate to test controlled leverage and
explicit path-risk controls `[leverage_for_the_long_run, p.13]`, volatility-scaled
position sizing `[systematic_trading, p.137-148]`, and conservative model-selection
discipline `[testing_tuning, p.327-335]`.

## Data And Window

Physical daily parquet files required before testing:

- `data/tiingo/daily/prices/QLD.parquet`
- `data/tiingo/daily/prices/TLT.parquet`
- `data/tiingo/daily/prices/GLD.parquet`
- `data/tiingo/daily/prices/QQQ.parquet`
- `data/tiingo/daily/prices/SPY.parquet`
- `data/tiingo/daily/prices/SHV.parquet`

Use adjusted close where available. Align all series by intersection and do not
substitute missing assets after this pre-registration. If any required file/close
series is missing or the aligned window is too short, close `data_blocked`.

## Exact Configs

Four configs, monthly rebalance, one-day/one-month lag through use of prior monthly
realized volatility state only:

| name | base `QLD` | base `TLT` | base `GLD` | low-vol `QLD` boost | high-vol `QLD` cut | rv lookback | low/high quantiles |
|---|---:|---:|---:|---:|---:|---:|---:|
| `qld60_tlt20_gld20_rv63_q30_70_b25_c10` | 0.60 | 0.20 | 0.20 | 0.25 | 0.10 | 63 | 30% / 70% |
| `qld70_tlt15_gld15_rv63_q30_70_b25_c10` | 0.70 | 0.15 | 0.15 | 0.25 | 0.10 | 63 | 30% / 70% |
| `qld60_tlt20_gld20_rv126_q30_70_b50_c20` | 0.60 | 0.20 | 0.20 | 0.50 | 0.20 | 126 | 30% / 70% |
| `qld70_tlt15_gld15_rv126_q30_70_b50_c20` | 0.70 | 0.15 | 0.15 | 0.50 | 0.20 | 126 | 30% / 70% |

Financing drag: 5% annualized on `gross - 1.0` when gross exposure exceeds 1.0,
deducted daily `[systematic_trading, p.137-148]`.

## Benchmarks

Primary benchmarks, both must be beaten in CAGR and terminal wealth on aligned dates:

- `QQQ` buy-and-hold.
- Equal-weight monthly buy-and-hold of `QLD/TLT/GLD` opportunity universe.

Opportunity benchmark:

- `SPY` buy-and-hold.

Context benchmarks:

- `QLD`, `TLT`, `GLD`, `SHV` buy-and-hold.

## Kill Rules

- CAGR or terminal wealth <= either primary B&H benchmark => `fail`.
- CAGR <= `SPY` B&H opportunity cost => `fail`.
- Missing required physical daily parquet/close data => `data_blocked`.
- PBO >= 0.5, DSR p >= 0.05, IS MCPT p > 0.01, WF MCPT p > 0.05, insufficient WF,
  negative OOS/FWD, bootstrap 99.9% CI low <= 0, or cross-lib delta > 3pp blocks
  `strict_winner` `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- MDD worse than 1.5x `QQQ` B&H blocks `strict_winner` unless human review occurs;
  no human review is available in this loop.

## Planned Gates

- IS MCPT with 200 permutations on the selected config.
- WF MCPT with 100 permutations, train 756 trading days, test 252, step 252.
- PBO over the four configs with 10 blocks.
- DSR using cumulative trials after this iteration.
- WF windows, OOS, latest 63d FWD, bootstrap 99.9% CI, cross-lib reference parity.

## Trial Accounting

- `cumulative_n_trials` before: 308.
- New strategy configs: 4.
- `cumulative_n_trials` after: 312.

## Ambiguity Note

The working tree and public docs contain pre-existing Phase 3 artifacts beyond the
`MEMORY.md` state supplied to this run. Conservatively, this iteration follows the
user-specified operational state (`total_iterations=26`, `cumulative_n_trials=308`)
and does not revert or edit unrelated pre-existing changes.
