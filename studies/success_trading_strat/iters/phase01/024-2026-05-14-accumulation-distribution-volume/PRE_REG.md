# PRE_REG — 024 accumulation/distribution volume

## Hypothesis

OBV failed MCPT in iteration 023, so this iteration pivots to a different volume
information source rather than tuning OBV. The test asks whether daily
close-location volume pressure, via Accumulation/Distribution and Intraday
Intensity, provides timing information for `SPY`/`QQQ` exposure versus `SHV`.
Kaufman defines volume accumulation indicators that weight volume by where the
close lands inside the high-low range, which is different from OBV's close-to-
close signed volume `[trading_systems_methods, p.540-541]`. MCPT remains a
required best-of-many anti-selection-bias gate `[testing_tuning, p.318-320]`,
and PBO/DSR remain hard-block controls `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Data And Window

- Source: local Tiingo daily parquet cache under `data/tiingo/daily/prices/`.
- Required tickers: `SPY`, `QQQ`, `SHV`.
- Required columns: adjusted OHLC and volume for `SPY`/`QQQ`; adjusted close for
  `SHV`.
- Window: common daily history from `2010-01-01` through the latest common date.
- Staleness kill rule: block if common data end is before `2026-03-31`.
- Signals are lagged one trading day to avoid same-close look-ahead
  `[testing_tuning, p.17]`.

## Exact Configs

Four configs, no expansion after seeing results:

| name | asset | indicator | lookback | rule |
|---|---|---:|---:|---|
| `spy_ad21` | `SPY` | accumulation/distribution | 21 | risk-on if 21d AD delta > 0 |
| `qqq_ad21` | `QQQ` | accumulation/distribution | 21 | risk-on if 21d AD delta > 0 |
| `spy_ii21` | `SPY` | intraday intensity | 21 | risk-on if 21d II delta > 0 |
| `qqq_ii21` | `QQQ` | intraday intensity | 21 | risk-on if 21d II delta > 0 |

Lookback 21 is a one-trading-month horizon, fixed before testing as a minimal
volume-pressure window rather than optimized. Indicator definitions follow
Kaufman's formulas: Accumulation/Distribution weights volume by
`(close - open) / (high - low)`, while Intraday Intensity weights volume by
close location inside the daily range `[trading_systems_methods, p.541]`.

## Benchmark

Each config is compared against same-window buy-and-hold of its risk asset
(`SPY` or `QQQ`). Economic pass requires strategy Sharpe > benchmark Sharpe.
CAGR and MDD are reported as tiers/diagnostics, not hard blocks per mandate.

## Planned Gates

- Data freshness: latest common date >= `2026-03-31`.
- Economic Sharpe vs same-asset benchmark.
- IS MCPT: fixed best config, 200 reps, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: fixed best config, 100 reps, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO: 8 blocks across the 4 config return series, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: pass if `p < 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: annual windows after 4y train, pass if at least 6 positive
  windows when >=8 windows exist `[testing_tuning, p.148-150]`.
- OOS: final 20% total return > 0 `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 observations total return > 0
  `[advances_fin_ml, p.196-202]`.
- Bootstrap: stationary bootstrap 99.9% mean daily CI low > 0
  `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy-style implementation CAGR delta <= 3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If required OHLCV columns are unavailable, status is `data_blocked` and
  `n_trials=0`.
- If any hard gate fails, status is `fail`; no local tuning of AD/II lookbacks,
  thresholds, or price filters inside this iteration.
- If the result is only economically interesting but MCPT/PBO/DSR fails, add the
  family to dead ends and pivot to a different mechanism next iteration
  `[testing_tuning, p.327-335]`.

## Trial Accounting

- `cumulative_n_trials` before: 80.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if data are available: 84.
