# PRE_REG — 023-2026-05-14-money-flow-pullback

## Hypothesis

Daily Money Flow Index pullbacks can identify volume-confirmed exhaustion in liquid ETFs, then hold the recovery for a short swing while a slow trend filter avoids structurally weak regimes. MFI uses typical price times volume split into up/down flows `[trading_systems_methods, p.540]`; the trend filter uses a 200-day stock-market macro benchmark `[trading_systems_methods, p.285]`; the short-swing premise follows Kaufman's guidance that high-noise equity indices favor shorter countertrend methods while metals can support trend/flow tests when matched to market noise `[trading_systems_methods, p.13-14]`.

This is not a hedge/cash-parking hypothesis. The Phase 2 economic floor applies: CAGR must beat same-asset buy-and-hold on the aligned window before any `candidate_watchlist`, `paper_trade_candidate` or `strict_winner` label `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Configs

Four configs, fixed before testing:

| name | ticker | mfi_period | oversold | exit_level | trend_sma | max_hold |
|---|---:|---:|---:|---:|---:|---:|
| `spy_mfi14_os20_x50_sma200_h10` | `SPY` | 14 | 20 | 50 | 200 | 10 |
| `qqq_mfi14_os20_x50_sma200_h10` | `QQQ` | 14 | 20 | 50 | 200 | 10 |
| `gld_mfi14_os20_x50_sma200_h10` | `GLD` | 14 | 20 | 50 | 200 | 10 |
| `gld_mfi20_os30_x50_sma200_h20` | `GLD` | 20 | 30 | 50 | 200 | 20 |

Signals are shifted one completed daily bar before returns are earned to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Data And Window

Required physical daily parquet files: `SPY`, `QQQ`, `GLD`, `SHV`, `xauusd` under `data/tiingo/daily/prices/`. `SPY`/`QQQ`/`GLD` must include non-empty volume because MFI is volume-based. `xauusd` is context only, not a configured strategy ticker.

Before testing, audit:

- physical daily file existence, rows, date range, timezone, OHLCV columns and missing-business-day rate;
- physical `data/tiingo/1hour/prices/*.parquet` count and per-ticker existence;
- physical `data/tiingo/15min/prices/*.parquet` count and per-ticker existence.

Manifest entries alone are not accepted. If intraday files are absent, no intraday hybrid will be synthesized `[testing_tuning, p.327-335]`.

## Benchmarks

Primary benchmark: same-asset buy-and-hold (`SPY`, `QQQ` or `GLD`) over each config's aligned strategy window.

Opportunity benchmark: `SPY` buy-and-hold over the same aligned dates. `xauusd` buy-and-hold is also reported as gold context for `GLD` configs.

## Kill Rules

- If required daily data or volume are missing, close `data_blocked` with `n_trials=0`.
- If best config CAGR <= same-asset buy-and-hold CAGR, close `fail`; no watchlist or paper-trade label.
- If PBO >= 0.5 or DSR p-value >= 0.05, strict promotion is blocked `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- If IS MCPT p-value > 0.01 or WF MCPT p-value > 0.05, strict promotion is blocked `[testing_tuning, p.318-320]`.
- If WF has fewer than 8 windows or fewer than 6 positive windows, strict promotion is blocked `[testing_tuning, p.148-150]`.
- If OOS, latest 63d FWD stress, bootstrap 99.9% CI low or cross-lib parity fails, strict promotion is blocked `[advances_fin_ml, p.196-202]`.

## Planned Gates

- IS MCPT: 200 reps.
- WF MCPT: 100 reps.
- PBO across the 4 configs with 10 blocks.
- DSR using `cumulative_n_trials` after this iteration.
- Walk-forward yearly windows, single-block OOS, latest 63-trading-day FWD stress, bootstrap 99.9% mean-daily CI, vector/loop cross-lib parity.

## Trial Accounting

- `cumulative_n_trials` before: 188.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if data are testable: 192.
