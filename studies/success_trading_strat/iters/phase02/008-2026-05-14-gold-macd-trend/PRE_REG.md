# PRE_REG — 008-2026-05-14-gold-macd-trend

## Hypothesis

Daily gold trend continuation may be cleaner than the failed Phase 2 gold
breakout/oscillator families if entries require MACD momentum confirmation and
one-bar signal lag. MACD is a classical moving-average momentum oscillator
`[trading_systems_methods, p.382]`; the study keeps the Phase 2 gold/XAUUSD track
and avoids local retuning of Donchian, RSI or CCI dead ends
`[testing_tuning, p.327-335]`.

## Data And Audit Plan

- Assets: `GLD`, `xauusd`, `SHV` from `data/tiingo/daily/prices/`.
- Window: full overlapping daily adjusted-close history available after physical
  file audit.
- Intraday: audit `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/` for
  physical files, range, timezone/session and missing bars; do not synthesize 1h
  or 15m if unavailable.
- Benchmark: same-asset buy-and-hold for the selected best config, plus SPY
  context when available.

## Exact Configs

1. `gld_macd_12_26_9`: `GLD`, MACD 12/26/9, no SMA regime filter.
2. `gld_macd_12_26_9_sma200`: `GLD`, MACD 12/26/9, require close > SMA200.
3. `xau_macd_12_26_9`: `xauusd`, MACD 12/26/9, no SMA regime filter.
4. `xau_macd_12_26_9_sma200`: `xauusd`, MACD 12/26/9, require close > SMA200.

Rule: long risk asset when `MACD > signal` and optional lagged SMA regime is true;
otherwise hold `SHV`. Signal is shifted one completed bar before earning returns
to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Gates

- Same-asset benchmark Sharpe and total-return context.
- IS MCPT: pass only if `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT: pass only if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration
  `[advances_fin_ml, p.222-223]`.
- WF windows: at least 6 positive of at least 8 windows.
- OOS positive, latest 63d FWD positive, bootstrap 99.9% mean-daily CI low > 0,
  and vector/loop cross-lib CAGR delta <= 3pp.

## Kill Rules

- If any required daily physical file is missing, stop as `data_blocked` with
  `n_trials=0`.
- If intraday files remain missing, record Track B as blocked and do not make any
  intraday claim.
- If MCPT/PBO/DSR fail, do not tune MACD fast/slow/signal periods or add filters
  in this iteration `[testing_tuning, p.327-335]`.
- `candidate_watchlist` is not deploy; capital remains 100% Plano C.

## Trial Accounting

- `cumulative_n_trials` before: 128.
- Planned new strategy configs: 4.
- `cumulative_n_trials` after if all configs test: 132.
