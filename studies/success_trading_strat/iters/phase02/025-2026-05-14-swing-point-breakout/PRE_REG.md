# PRE_REG — 025-2026-05-14-swing-point-breakout

## Hypothesis

Test a conservative daily swing-point breakout: after a completed upswing/downtrend
sequence, go long only when price breaks the prior upswing high, and hold `SHV`
otherwise. Kaufman describes swing filters as event-driven trend definitions using
minimum percentage reversals and notes the conservative long entry as a break above
the previous upswing high `[trading_systems_methods, p.165]`,
`[trading_systems_methods, p.168]`. This is a distinct Phase 2 mechanism from the
prior MA/ATR, Bollinger, Donchian, RSI/Stochastic, ASI, regression-channel and
volume-flow dead ends.

## Configs

Exactly 4 configs, no local tuning after results:

- `spy_swing5_break_prev_high`: `SPY`, swing reversal filter `5%`, long on break of previous upswing high, otherwise `SHV`.
- `qqq_swing7_break_prev_high`: `QQQ`, swing reversal filter `7%`, long on break of previous upswing high, otherwise `SHV`.
- `gld_swing5_break_prev_high`: `GLD`, swing reversal filter `5%`, long on break of previous upswing high, otherwise `SHV`.
- `xau_swing5_break_prev_high`: `xauusd`, swing reversal filter `5%`, long on break of previous upswing high, otherwise `SHV`.

All signals are computed on completed daily bars and shifted one bar before returns
are earned to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Data And Window

Physical audit required before testing:

- Daily adjusted OHLC: `data/tiingo/daily/prices/{SPY,QQQ,GLD,SHV,xauusd}.parquet`.
- Intraday audit: `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/` file counts, timestamp range if files exist, timezone/session convention and missing-bar rate. Manifest-only coverage is insufficient.
- Window: maximum common daily history per ticker after indicator warmup and signal lag.

If any required daily OHLC file is missing, close `data_blocked` with `n_trials=0`.
Do not synthesize intraday bars from daily data.

## Benchmarks

Primary benchmark is same-asset buy-and-hold over the aligned strategy window:

- `SPY` config vs `SPY` buy-and-hold.
- `QQQ` config vs `QQQ` buy-and-hold.
- `GLD` config vs `GLD` buy-and-hold.
- `xauusd` config vs `xauusd` buy-and-hold.

Also report `SPY` buy-and-hold as opportunity-cost benchmark for every config.

## Kill Rules

- Phase 2 economic kill: if best strategy CAGR is `<=` same-asset buy-and-hold CAGR on the aligned window, status must be `fail`; lower MDD alone cannot promote `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.
- Any PBO `>= 0.5` or DSR p-value `>= 0.05` blocks `strict_winner` `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
- IS MCPT must pass `p <= 0.01`; WF MCPT must pass `p <= 0.05` for this short-window Phase 2 test `[testing_tuning, p.318-320]`.
- Do not tune swing filters, thresholds, assets or exits after seeing results.

## Planned Gates

- Same-asset CAGR and Sharpe comparison.
- IS MCPT: 200 reps on the best fixed rule.
- WF MCPT: 100 reps on the best fixed rule.
- PBO over the 4 pre-registered configs.
- DSR with cumulative trial count after this iteration.
- Walk-forward yearly windows, OOS last 20%, latest 63d FWD stress.
- Bootstrap 99.9% mean-daily CI low.
- Cross-lib/vector parity within +/-3pp CAGR.

## Trial Accounting

- `cumulative_n_trials` before: 196.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 200.
- If data-blocked before testing: 196.
