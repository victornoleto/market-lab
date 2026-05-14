# PRE_REG — 017-2026-05-14-woodshedder-roc

## Hypothesis

Test a daily Woodshedder ROC swing rule: enter long when 5-day ROC is below
252-day ROC for two consecutive completed bars, and exit to `SHV` when 5-day ROC
is above 252-day ROC for two consecutive completed bars. Kaufman records this as
an explicit ROC rule `[trading_systems_methods, p.355]`. Signals are lagged one
completed daily bar before returns are earned to avoid same-close lookahead
`[advances_fin_ml, p.31-34]`.

This is a different mechanism from the dead-ended TRIX/MACD/ADX/Keltner/Bollinger
families: it is a long-cycle ROC state rule rather than smoothed trend following
or band breakout. The validation stack remains MCPT, WF-MCPT, PBO, DSR, WF, OOS,
FWD, bootstrap and cross-lib `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Configs

Exactly 4 configs, no local tuning after results:

- `spy_roc5_252_x2`: `SPY`, short ROC 5, long ROC 252, confirmation 2 bars.
- `qqq_roc5_252_x2`: `QQQ`, short ROC 5, long ROC 252, confirmation 2 bars.
- `gld_roc5_252_x2`: `GLD`, short ROC 5, long ROC 252, confirmation 2 bars.
- `xau_roc5_252_x2`: `xauusd`, short ROC 5, long ROC 252, confirmation 2 bars.

## Data And Window

- Daily physical files required before testing: `SPY`, `QQQ`, `GLD`, `xauusd`,
  `SHV` under `data/tiingo/daily/prices/`.
- Audit physical file existence, timestamp range, timezone and missing business-day
  rate before strategy metrics.
- Audit `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/` file counts;
  manifest alone is insufficient. No intraday synthetic data will be created.
- Use the aligned post-warmup daily window per config.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold over the exact aligned strategy dates.
- Opportunity benchmark: `SPY` buy-and-hold over the exact aligned strategy dates.

## Kill Rules

- If any required daily physical file is missing, stop as `data_blocked` before
  consuming trials.
- If strategy CAGR is `<=` same-asset buy-and-hold CAGR, close `fail`; it cannot
  receive `candidate_watchlist`, `paper_trade_candidate` or `strict_winner`.
- Any failed hard gate blocks `strict_winner`.
- Do not tune ROC lengths, confirmation count or exits after this iteration.

## Planned Gates

- IS MCPT: 200 reps, pass if `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: 100 reps, pass if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO: 10 blocks, pass if `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: use cumulative strategy trials after this iteration `[advances_fin_ml, p.222-223]`.
- WF: at least 8 windows and at least 6 positive `[testing_tuning, p.148-150]`.
- OOS: final 20% total return positive `[advances_fin_ml, p.196-202]`.
- FWD stress: latest 63 daily bars positive `[advances_fin_ml, p.196-202]`.
- Bootstrap: 99.9% mean-daily CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity: CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Trial Accounting

- cumulative_n_trials before: 164.
- n_trials planned: 4.
- cumulative_n_trials after if data are testable: 168.
