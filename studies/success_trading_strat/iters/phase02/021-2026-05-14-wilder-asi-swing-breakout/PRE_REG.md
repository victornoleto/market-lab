# PRE_REG — 021-2026-05-14-wilder-asi-swing-breakout

## Hypothesis

Daily Wilder Accumulated Swing Index (ASI) breakouts may capture swing-level
direction changes that simple close-only momentum/oscillator rules missed. ASI
combines open, high, low and close into a swing-pressure series, with long signals
when ASI breaks prior swing highs and exits when it breaks prior swing lows
`[trading_systems_methods, p.193-195]`. The test remains deliberately sparse to
avoid local tuning after many failed Phase 2 families `[testing_tuning, p.327-335]`.

## Data And Window

Physical file audit before preregistration:

- `SPY`: `data/tiingo/daily/prices/SPY.parquet`, 8379 rows, 1993-01-29 to 2026-05-13.
- `QQQ`: `data/tiingo/daily/prices/QQQ.parquet`, 6837 rows, 1999-03-10 to 2026-05-13.
- `GLD`: `data/tiingo/daily/prices/GLD.parquet`, 5404 rows, 2004-11-18 to 2026-05-13.
- `xauusd`: `data/tiingo/daily/prices/xauusd.parquet`, 1723 rows, 2020-01-02 to 2026-05-14.
- `SHV`: `data/tiingo/daily/prices/SHV.parquet`, 4865 rows, 2007-01-11 to 2026-05-13.
- Required OHLC columns exist for all five daily files: `open`, `high`, `low`, `close`, `adj_close`, `volume`.
- Intraday audit: `data/tiingo/1hour/prices/` exists but has 0 parquet files; `data/tiingo/15min/prices/` is absent. Therefore no 1h/15m hybrid is tested or synthesized.

Execution uses adjusted OHLC for ETF files by scaling O/H/L/C with
`adj_close / close`, then one completed daily bar of signal lag before returns are
earned `[advances_fin_ml, p.31-34]`.

## Exact Configs

Four configs, one per asset, no local parameter grid:

- `spy_asi20_10_h20`: `SPY`, ASI entry breakout over prior 20 bars, exit breakdown over prior 10 bars, max hold 20 bars.
- `qqq_asi20_10_h20`: `QQQ`, same rule.
- `gld_asi20_10_h20`: `GLD`, same rule.
- `xau_asi20_10_h20`: `xauusd`, same rule.

The 20-bar swing horizon approximates one trading month and the 10-bar exit is a
shorter failure stop, consistent with swing-filter logic and monthly technical
cycles `[trading_systems_methods, p.165-172]`, `[trading_systems_methods, p.193-195]`.

## Benchmarks

Primary benchmark for each config: same-asset buy-and-hold over the exact aligned
strategy window. Opportunity benchmark: `SPY` buy-and-hold over the same aligned
window. Gold configs also report both `GLD` and `xauusd` buy-and-hold context.

## Kill Rules

- If best strategy CAGR <= same-asset buy-and-hold CAGR, verdict must be `fail`.
- If required daily OHLC data are missing, verdict is `data_blocked` with `n_trials=0`.
- If PBO >= 0.5 or DSR p-value >= 0.05, no `strict_winner` is allowed
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- IS MCPT and WF MCPT are additional gates, not substitutes for PBO/DSR
  `[testing_tuning, p.318-320]`.
- No `candidate_watchlist`, `paper_trade_candidate` or `strict_winner` label is
  allowed unless the Phase 2 economic floor is met.

## Planned Gates

- Same-asset CAGR and Sharpe comparison.
- IS MCPT with 200 reps on best config.
- WF MCPT with 100 reps on best config.
- PBO over the 4 pre-registered configs using 10 blocks.
- DSR using cumulative trials after this iteration.
- Walk-forward positive windows, OOS holdout, latest 63d FWD stress.
- Bootstrap 99.9% mean-daily return CI.
- Cross-lib/vector parity within +/-3pp CAGR.

## Trial Accounting

- `cumulative_n_trials` before: 180.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 184.
