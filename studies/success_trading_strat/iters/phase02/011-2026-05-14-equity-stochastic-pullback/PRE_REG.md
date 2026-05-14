# PRE_REG — 011-2026-05-14-equity-stochastic-pullback

## Hypothesis

Daily `SPY`/`QQQ` pullbacks whose close is near the bottom of its recent close
range can rebound when the long-term trend remains positive. This uses a
stochastic-style close-location oscillator and a `SMA200` regime filter;
methods, but this iteration treats them as suspect until MCPT, PBO, DSR and
walk-forward validation pass `[trading_systems_methods, p.385-386]`,
`[trading_systems_methods, p.172]`, `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`.

This is a daily-swing Track A/B proxy because physical `1h`/`15m` cache files
have been repeatedly absent. No intraday bars will be synthesized
`[testing_tuning, p.327-335]`.

## Data And Window

- Physical files required before testing: `SPY.parquet`, `QQQ.parquet`,
  `SHV.parquet` and `SPY` context benchmark under `data/tiingo/daily/prices/`.
- Intraday audit required before any short-swing claim:
  `data/tiingo/1hour/prices/*.parquet` and `data/tiingo/15min/prices/*.parquet`.
- Use the full available aligned daily window after warmup for each config.
- Signals are shifted by one completed daily bar before returns are earned to
  avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Exact Configs

1. `spy_stoch14_os20_exit50_hold10`: `SPY`, close-location lookback 14,
   oversold `<=20`, exit `>=50`, max hold 10 bars, `SMA200` regime.
2. `spy_stoch21_os10_exit50_hold10`: `SPY`, close-location lookback 21,
   oversold `<=10`, exit `>=50`, max hold 10 bars, `SMA200` regime.
3. `qqq_stoch14_os20_exit50_hold10`: `QQQ`, close-location lookback 14,
   oversold `<=20`, exit `>=50`, max hold 10 bars, `SMA200` regime.
4. `qqq_stoch21_os10_exit50_hold10`: `QQQ`, close-location lookback 21,
   oversold `<=10`, exit `>=50`, max hold 10 bars, `SMA200` regime.

Parameter count is capped at four configs to limit data mining and DSR burden
`[advances_fin_ml, p.222-223]`.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold (`SPY` for `SPY`, `QQQ` for `QQQ`)
  over the exact aligned strategy window.
- Opportunity-cost benchmark: `SPY` buy-and-hold over the same aligned window.

## Kill Rules

- Hard economic kill: best strategy CAGR `<=` same-asset buy-and-hold CAGR means
  final status must be `fail`; lower drawdown alone cannot promote the strategy.
- Same-asset Sharpe must also beat buy-and-hold for any non-fail triage label.
- Any PBO `>=0.5` or DSR `p>=0.05` blocks `strict_winner`
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- IS MCPT must pass `p<=0.01`; WF MCPT must pass `p<=0.05`
  `[testing_tuning, p.318-320]`.
- WF must have at least 8 windows and 6 positive; OOS, latest 63d FWD,
  bootstrap 99.9% CI low and cross-lib parity must pass for `strict_winner`.

## Planned Gates

- IS MCPT: 200 permutations on the fixed best rule.
- WF MCPT: 100 permutations on adjacent train/test windows.
- PBO: return matrix across the four configs.
- DSR: use cumulative trials after this iteration.
- WF/OOS/FWD/bootstrap/cross-lib as in prior Phase 2 iterations.

## Trial Accounting

- `cumulative_n_trials` before: 140.
- `n_trials` planned: 4.
- `cumulative_n_trials` after: 144.
