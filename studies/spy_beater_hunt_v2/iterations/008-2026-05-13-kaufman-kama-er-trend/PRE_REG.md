# PRE_REG — 008-kaufman-kama-er-trend

## Hypothesis

Kaufman's Efficiency Ratio measures trend efficiency versus noise, and KAMA uses
that ER to adapt its smoothing speed `[trading_systems_methods, p.10-11]`,
`[trading_systems_methods, p.780-781]`. A long-history SPY trend gate based on
`SPYSIM > KAMA(default)` may avoid noisy equity-index periods better than a fixed
SMA while preserving upside through pre-fixed 2x/3x exposure.

This is distinct from the failed fixed SMA Gayed control and Carver EWMAC family:
the signal is a single adaptive moving average whose smoothing constant is driven
by ER, not a fixed moving-average threshold or EWMAC forecast.

## Exact Configs

- `kama10_2_30_sso_cash`: compute KAMA on `SPYSIM` with ER lookback 10,
  fastest equivalent 2 days, slowest equivalent 30 days; if `SPYSIM > KAMA`, hold
  `SSOSIM`, otherwise `CASHX` `[trading_systems_methods, p.780-781]`.
- `kama10_2_30_upro_cash`: same KAMA gate; if on, hold `UPROSIM`, otherwise
  `CASHX` `[trading_systems_methods, p.780-781]`.

All signals are shifted by one trading day before applying returns to avoid
same-close look-ahead `[advances_fin_ml, p.31-34]`.

## Data And Window

- Source: `data/testfolio/cache/history.parquet` through
  `load_testfolio_series`.
- Required labels: `SPYSIM`, `SSOSIM`, `UPROSIM`, `CASHX`.
- Window: common non-null history after KAMA warmup, expected long-history
  1986-01-03 through 2026-04-17.
- Benchmark: same-window `SPYSIM` buy-and-hold.

## Planned Gates

- Economic: candidate CAGR > same-window SPY and terminal equity ratio > 1.
- PBO `< 0.5` over the two pre-registered configs; marked unstable because only
  two configs are tested `[advances_fin_ml, p.208-211]`.
- DSR p-value `< 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 6/8 windows beat SPY `[testing_tuning, ch.12]`.
- OOS final 25% and FWD final 3y must beat SPY `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% daily excess-return CI low > 0 `[advances_fin_ml, p.196-202]`.
- Cross-lib parity: vectorized and explicit-loop CAGR delta <= 3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If either required ticker is unavailable, mark `data_blocked`; do not
  substitute another asset.
- If the best config fails to beat SPY CAGR or terminal equity, stop the family.
- If PBO or DSR fails, no winner regardless of economic metrics.
- If bootstrap 99.9% CI low is <= 0, no winner.
- If KAMA behaves like a local SMA trend variant with no improvement, add the
  family to dead ends rather than tuning thresholds.

## Trial Accounting

- `cumulative_n_trials` before: 14.
- New pre-registered configs: 2.
- `cumulative_n_trials` after: 16.
