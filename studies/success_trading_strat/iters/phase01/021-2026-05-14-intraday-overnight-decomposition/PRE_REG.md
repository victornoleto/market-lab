# PRE_REG — 021 intraday/overnight decomposition

## Hypothesis

Daily OHLC may expose a distinct intraday/overnight return component: hold only
the close-to-next-open leg or only the open-to-close leg in `SPY`/`QQQ`, with
`SHV` for idle close-to-close days. The mechanism is a conservative daily-data
proxy for intraday momentum/overnight decomposition rather than another local
retune of VIX, carry, credit, crypto, Ehlers, calendar or EWMAC families
`[paper.zarattini_2024_intraday_spy, §methodology]`,
`[trading_systems_methods, p.939]`, `[testing_tuning, p.327-335]`.

## Data And Window

- Source: local Tiingo daily OHLC parquet files in `data/tiingo/daily/prices/`.
- Required tickers: `SPY`, `QQQ`, `SHV`.
- Window: common adjusted OHLC history from `2010-01-01` through the latest common
  date available.
- Data freshness kill: latest common date must be at least `2026-03-31`.
- Price adjustment: adjusted OHLC uses `adj_close / close` when available.

## Exact Configs

1. `spy_close_to_open`: `SPY` close-to-next-open return, otherwise no risky intraday exposure.
2. `qqq_close_to_open`: `QQQ` close-to-next-open return, otherwise no risky intraday exposure.
3. `spy_open_to_close`: `SPY` open-to-close return, idle capital earns `SHV` close-to-close return.
4. `qqq_open_to_close`: `QQQ` open-to-close return, idle capital earns `SHV` close-to-close return.

No volatility, trend or calendar filters are added. This keeps the family at one
mechanism and four configs, consistent with parsimony warnings
`[trading_systems_methods, p.939]`.

## Benchmark

- Same-asset buy-and-hold close-to-close return on the same adjusted OHLC window.
- Economic pass requires strategy Sharpe greater than benchmark Sharpe. CAGR/MDD
  are recorded as tiers/warnings, not hard gates per mandate.

## Planned Gates

- Data freshness: latest common date >= `2026-03-31`.
- IS MCPT: fixed best config, 200 permutations, pass if `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT: fixed best config, 100 permutations, pass if `p <= 0.05`
  `[testing_tuning, p.318-320]`.
- PBO: 8-block PBO over the 4 configs, pass if `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR: cumulative `n_trials=72` after this iteration, pass if `p < 0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: annual OOS windows after 4-year train, pass if at least 6 positive
  windows when >=8 windows exist `[testing_tuning, p.148-150]`.
- OOS: final 20% return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 observations positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib: independent NumPy-style implementation CAGR within +/-3pp
  `[advances_fin_ml, p.31-34]`.

## Kill Rules

- If any required OHLC file or adjusted OHLC column is unavailable, close as
  `data_blocked` with `n_trials=0`; do not substitute tickers after pre-reg.
- If the family fails MCPT, PBO or DSR, do not tune session definitions or add
  filters locally; record it as a dead end `[testing_tuning, p.327-335]`.
- No live/deploy claim regardless of result; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 68.
- New configs: 4.
- `cumulative_n_trials` after if data load succeeds: 72.
- `cumulative_n_trials` after if data-blocked before testing: 68.
