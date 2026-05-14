# PRE_REG — 022-2026-05-14-regression-channel-breakout

## Hypothesis

Daily regression-channel breakouts can capture persistent swing trends while avoiding some late entries from simple high/low breakouts. Kaufman's regression channel projects a trend line and bands from recent price action, and conservative swing entries require confirmation beyond prior swing highs `[trading_systems_methods, p.167-169]`, `[trading_systems_methods, p.168]`.

This is a Phase 2 daily-swing test. No live deployment is authorized; mandate capital remains 100% Plano C.

## Data And Window

- Source: local Tiingo parquet cache under `data/tiingo/daily/prices/`.
- Assets: `SPY`, `QQQ`, `GLD`, `xauusd`, with `SHV` as defensive sleeve while flat.
- Physical audit required before testing: file existence, date range, timezone, columns, missing business-day rate, and physical `1hour`/`15min` cache availability.
- Intraday rule: do not synthesize 1h/15m bars if physical files are unavailable.

## Exact Configs

All signals are computed on completed daily bars and shifted one bar before returns are earned to avoid lookahead `[advances_fin_ml, p.31-34]`.

- `spy_regch63_h30`: `SPY`, regression window 63, max hold 30.
- `qqq_regch63_h30`: `QQQ`, regression window 63, max hold 30.
- `gld_regch63_h30`: `GLD`, regression window 63, max hold 30.
- `xau_regch63_h30`: `xauusd`, regression window 63, max hold 30.

Entry: close breaks above the lagged projected upper regression channel. Exit: close falls below the lagged projected regression centerline or max hold expires. The 63-day window maps to a quarterly swing horizon `[trading_systems_methods, p.285]`.

## Benchmarks

- Primary: same-asset buy-and-hold over the exact aligned strategy window.
- Opportunity cost: `SPY` buy-and-hold over the exact aligned window.
- Gold context: `GLD` and `xauusd` buy-and-hold where aligned.

## Kill Rules

- If required daily files or adjusted OHLC columns are missing, close `data_blocked` with `n_trials=0`.
- If physical intraday files are absent, do not synthesize short-swing bars; continue only with the pre-registered daily test.
- If best strategy CAGR is <= same-asset buy-and-hold CAGR, close `fail`; no `candidate_watchlist`, `paper_trade_candidate` or `strict_winner` is allowed.
- Any PBO >= 0.5 or DSR p >= 0.05 blocks `strict_winner` `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- Failed MCPT blocks `strict_winner`; MCPT is an added gate, not a substitute `[testing_tuning, p.318-320]`.
- Do not tune regression window, entry/exit bands or hold length after seeing results `[testing_tuning, p.327-335]`.

## Planned Gates

- Same-asset CAGR and Sharpe comparison.
- IS MCPT using fixed-rule log-price permutations, 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT using fixed-rule walk-forward permutations, 100 reps `[testing_tuning, p.318-320]`.
- PBO with 10 blocks `[advances_fin_ml, p.208-211]`.
- DSR using cumulative trial accounting `[advances_fin_ml, p.222-223]`.
- Walk-forward windows, OOS, latest 63d FWD stress, bootstrap 99.9% mean-daily CI, and cross-lib/vector parity.

## Trial Accounting

- `cumulative_n_trials` before: 184.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 188.
