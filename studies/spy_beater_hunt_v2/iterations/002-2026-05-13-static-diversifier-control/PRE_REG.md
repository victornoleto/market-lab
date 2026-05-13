# PRE_REG — 002-static-diversifier-control

## Hypothesis

Pre-fixed static multi-asset diversifier stacks may improve risk-adjusted long-run
returns versus SPY buy-and-hold, but must first beat SPY CAGR before any
promotional claim. The family uses Carver's asset-allocating investor archetype:
constant long exposure, diversification before rule mining, and no forecast
optimization `[systematic_trading, p.9-11]`, `[systematic_trading, p.72-85]`,
`[systematic_trading, p.116]`.

## Exact Configs

Daily constant-weight portfolios over the common data window, with weights fixed
before running:

| config | SPYSIM | ZROZSIM | GLDSIM | KMLMSIM |
|---|---:|---:|---:|---:|
| static_60_20_10_10 | 60% | 20% | 10% | 10% |
| static_50_25_15_10 | 50% | 25% | 15% | 10% |
| static_40_30_20_10 | 40% | 30% | 20% | 10% |
| static_25_25_25_25 | 25% | 25% | 25% | 25% |

These are not selected from data. They are a small ex-ante control panel to keep
DSR trial accounting conservative `[advances_fin_ml, p.222-223]`.

## Data And Window

- Source: `data/testfolio/cache/history.parquet` via `load_testfolio_series`.
- Required labels: `SPYSIM`, `ZROZSIM`, `GLDSIM`, `KMLMSIM`.
- Window: common non-null overlap across all four labels.
- Benchmark: SPY buy-and-hold (`SPYSIM`) over the same common window.

## Planned Gates

- Economic screen: candidate CAGR > same-window SPY CAGR and terminal equity
  ratio > 1.0.
- PBO over the four pre-fixed configs with 10 CSCV blocks; pass iff `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on best candidate with cumulative trials after this iteration; pass iff
  `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward: 8 equal chronological windows; pass iff at least 6 windows have
  positive excess return versus SPY `[testing_tuning, ch.12]`.
- OOS: final 25% of common window; candidate excess CAGR versus SPY must be
  positive `[advances_fin_ml, p.196-202]`.
- FWD stress: final 3 years of common window; candidate excess CAGR versus SPY
  must be positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary/bootstrap-style resampling of daily excess returns;
  99.9% CI low must be positive `[advances_fin_ml, p.196-202]`.
- Cross-lib: pandas vector return and explicit loop return CAGR must agree within
  +/-3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If no config beats SPY CAGR, verdict is `fail` regardless of risk metrics.
- If PBO or DSR fails, no winner claim even if economic metrics are attractive.
- If any required data label is unavailable, verdict is `data_blocked`.
- If cross-lib parity fails, stop and mark infrastructure issue.

## Trial Accounting

- `cumulative_n_trials` before: 0.
- `n_trials` this iteration: 4.
- `cumulative_n_trials` after if script runs: 4.
