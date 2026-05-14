# PRE_REG — 020-2026-05-14-elder-ray-triple-screen

## Hypothesis

Test a daily proxy for Elder's Triple Screen using weekly MACD histogram direction
as the long-term trend screen and daily Elder-Ray Bear Power rising from negative
territory as the pullback timing screen. The rule is long-only and uses `SHV`
while flat. Elder's Triple Screen explicitly combines a higher-timeframe trend,
an intermediate pullback oscillator and a fast entry; because local `1h` bars are
absent, this iteration tests only the daily proxy and records Track B as blocked
`[trading_systems_methods, p.835-838]`. Signals are shifted one completed daily
bar before returns are earned to avoid same-bar lookahead `[advances_fin_ml,
p.31-34]`.

## Configs

Four configs, no local tuning after results:

| name | ticker | weekly MACD | EMA | bear lookback | max hold |
|---|---|---:|---:|---:|---:|
| `spy_eray_12_26_9_ema13_bear3_h10` | `SPY` | 12/26/9 | 13 | 3 | 10 |
| `qqq_eray_12_26_9_ema13_bear3_h10` | `QQQ` | 12/26/9 | 13 | 3 | 10 |
| `gld_eray_12_26_9_ema13_bear3_h10` | `GLD` | 12/26/9 | 13 | 3 | 10 |
| `xau_eray_12_26_9_ema13_bear3_h10` | `xauusd` | 12/26/9 | 13 | 3 | 10 |

MACD 12/26/9 is the Appel default and Elder-Ray uses EMA13 in the book summary
`[trading_systems_methods, p.382]`, `[trading_systems_methods, p.837]`.

## Data And Window

Required daily files: `SPY`, `QQQ`, `GLD`, `xauusd`, `SHV` under
`data/tiingo/daily/prices/`. Physical audit will record rows, first/last date,
timezone, columns and missing business-day rate. Intraday audit will check
`data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/`; manifest entries
alone are insufficient.

Use each ticker's aligned available daily window after indicator warmup. Do not
synthesize `1h` or `15m` bars from daily data.

## Benchmarks

Primary benchmark: same-asset buy-and-hold over the exact strategy return window.
Opportunity benchmark: `SPY` buy-and-hold over the same dates.
Gold context: both `GLD` and `xauusd` are reported when the best config is a gold
asset.

## Planned Gates

- Phase 2 economic floor: strategy CAGR must exceed same-asset buy-and-hold CAGR;
  otherwise status is `fail` and cannot be `candidate_watchlist`,
  `paper_trade_candidate` or `strict_winner` `[systematic_trading, p.40]`,
  `[testing_tuning, p.327-335]`.
- Strategy Sharpe must exceed same-asset buy-and-hold Sharpe for any watchlist
  classification `[testing_tuning, p.327-335]`.
- IS MCPT with 200 reps, pass `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 reps, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO on the 4-config panel with 10 blocks, pass `< 0.5`
  `[advances_fin_ml, p.208-211]`.
- DSR on best config with cumulative strategy trials after this iteration,
  pass `p < 0.05` `[advances_fin_ml, p.222-223]`.
- WF windows, OOS, latest 63d FWD stress, bootstrap 99.9% mean-daily CI low and
  cross-lib/vector parity per study spec `[advances_fin_ml, p.196-202]`,
  `[testing_tuning, p.246-247]`.

## Kill Rules

- If any required daily file is missing, close `data_blocked` with `n_trials=0`.
- If intraday physical files are missing, do not test any `1h`/`15m` hybrid.
- If CAGR <= same-asset buy-and-hold, close `fail` even if drawdown improves.
- If any strict gate fails, `winner=false`.
- Do not tune MACD periods, EMA length, Bear Power timing window or hold length
  after seeing results.

## Trial Accounting

`cumulative_n_trials` before: 176.
Planned `n_trials`: 4.
`cumulative_n_trials` after if tested: 180.
