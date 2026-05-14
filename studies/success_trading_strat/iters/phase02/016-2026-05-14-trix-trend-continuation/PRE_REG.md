# PRE_REG — 016-2026-05-14-trix-trend-continuation

## Hypothesis

Daily TRIX trend continuation may capture smoother intermediate momentum than a
plain MACD by using triple exponential smoothing and a one-period rate of change
of that smoothed series `[trading_systems_methods, p.334]`. The rule is kept
simple and fully lagged one completed daily bar before returns are earned to
avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

This is a different mechanism from Phase 2 MACD, ADX, VIDYA, Bollinger,
Keltner/ATR, CCI and relative-strength filters because the signal is the slope
of a triple-smoothed log-price series, not a moving-average spread, range band,
directional movement statistic or cross-asset ratio.

## Data And Window

- Physical data required before testing:
  `data/tiingo/daily/prices/{SPY,QQQ,GLD,xauusd,SHV}.parquet`.
- Intraday audit required but no intraday test will be run unless physical `1hour`
  or `15min` files exist; manifest-only entries are insufficient.
- Backtest window: max available daily window after indicator warmup for each
  tested asset.
- Timezone/session audit: record parquet index timezone, first/last timestamp,
  row count and missing business-day rate in `audit.json`.

## Exact Configs

1. `spy_trix18_zero`: `SPY`, TRIX length 18, long when lagged TRIX > 0.
2. `qqq_trix18_zero`: `QQQ`, TRIX length 18, long when lagged TRIX > 0.
3. `gld_trix18_zero`: `GLD`, TRIX length 18, long when lagged TRIX > 0.
4. `xau_trix18_zero`: `xauusd`, TRIX length 18, long when lagged TRIX > 0.

All configs hold `SHV` while flat. TRIX is computed on log price with EMA
smoothing constant `2 / (length + 1)` and signal exposure is shifted by one daily
bar before strategy returns are computed `[trading_systems_methods, p.334]`.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold on exact aligned dates.
- Opportunity-cost benchmark: `SPY` buy-and-hold on exact aligned dates.
- Phase 2 kill rule: if best strategy CAGR <= same-asset buy-and-hold CAGR, close
  `fail` and do not assign `candidate_watchlist`, `paper_trade_candidate` or
  `strict_winner` `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates Planned

- Economic CAGR and Sharpe versus same-asset buy-and-hold.
- IS MCPT with 200 permutations, pass only if `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, pass only if `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` using the four pre-registered configs `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward: at least 8 windows and at least 6 positive windows `[testing_tuning, p.148-150]`.
- OOS, latest 63d FWD stress, bootstrap 99.9% mean-daily CI low > 0 and
  cross-lib/vector parity within 3pp CAGR `[advances_fin_ml, p.196-202]`.

## Kill Rules

- Missing required daily physical file before testing => `data_blocked`, `n_trials=0`.
- Missing intraday physical files => record intraday blocked; do not synthesize bars.
- Best CAGR <= same-asset buy-and-hold CAGR => `fail` regardless of lower drawdown.
- Any failed strict gate => not `strict_winner`.
- Do not locally tune TRIX length, threshold or asset list after results.

## Trial Accounting

- `cumulative_n_trials` before: 160.
- New strategy configs: 4.
- `cumulative_n_trials` after if tested: 164.
