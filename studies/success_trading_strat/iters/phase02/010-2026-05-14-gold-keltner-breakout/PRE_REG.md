# PRE_REG — 010-2026-05-14-gold-keltner-breakout

## Hypothesis

Gold trends sometimes expand after closing above an EMA plus ATR envelope. Test a
small daily Keltner/ATR breakout family on `GLD` and `xauusd`, holding `SHV` when
flat. The mechanism is different from prior Donchian/CCI/MACD gold tests because
entry is volatility-normalized around a moving average rather than raw channel or
oscillator state `[trading_systems_methods, p.352-353]`, `[trading_systems_methods,
p.1057-1059]`.

## Data And Audit Plan

- Required physical files before any backtest: `data/tiingo/daily/prices/GLD.parquet`,
  `data/tiingo/daily/prices/xauusd.parquet`, `data/tiingo/daily/prices/SHV.parquet`
  and `data/tiingo/daily/prices/SPY.parquet`.
- Audit each required daily file for row count, first/last timestamp, timezone,
  columns and business-day missing rate.
- Audit `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/` for physical
  parquet count. If intraday files are absent, do not synthesize intraday bars and
  keep this as a daily-only Track A/C test `[testing_tuning, p.327-335]`.

## Exact Configs

Four configs, all shifted one completed daily bar before returns are earned to
avoid same-close lookahead `[advances_fin_ml, p.31-34]`:

| name | asset | ema | atr | entry_mult | exit_mult |
|---|---:|---:|---:|---:|---:|
| `gld_kel20_15_exit0` | `GLD` | 20 | 20 | 1.5 | 0.0 |
| `gld_kel40_20_exit0` | `GLD` | 40 | 20 | 2.0 | 0.0 |
| `xau_kel20_15_exit0` | `xauusd` | 20 | 20 | 1.5 | 0.0 |
| `xau_kel40_20_exit0` | `xauusd` | 40 | 20 | 2.0 | 0.0 |

Rule: enter/hold long when close is above `EMA(ema) + entry_mult * ATR(atr)`;
exit to `SHV` when close is below `EMA(ema) + exit_mult * ATR(atr)`. ATR uses true
range on adjusted OHLC where available `[trading_systems_methods, p.353]`.

## Benchmark

- Primary benchmark: same-asset buy-and-hold over the aligned strategy window.
- Context benchmark: `SPY` buy-and-hold over the aligned strategy window.

## Planned Gates

- Same-asset Sharpe comparison.
- IS MCPT with 200 close-path permutations, strict pass `p <= 0.01`
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, pass `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` across the four configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` with cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 8 windows and at least 6 positive windows
  `[testing_tuning, p.148-150]`.
- OOS final 20% positive, latest 63 trading days positive, bootstrap 99.9% mean
  daily CI low > 0 and vector parity within +/-3pp CAGR.

## Kill Rules

- If any required daily physical file is missing, stop as `data_blocked` with
  `n_trials=0`.
- If intraday physical files are absent, do not substitute manifest entries or
  synthesize 1h/15m bars.
- If strict gates fail, do not tune EMA/ATR/multipliers inside this iteration;
  record the family as a dead end unless it qualifies only for watchlist review.

## Trial Accounting

- `cumulative_n_trials` before: 136.
- New strategy configs: 4.
- `cumulative_n_trials` after planned run: 140.
