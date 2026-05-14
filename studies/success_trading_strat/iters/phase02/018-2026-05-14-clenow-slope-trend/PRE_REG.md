# PRE_REG — 018-2026-05-14-clenow-slope-trend

## Hypothesis

Daily close-only linear-regression momentum can act as a parsimonious swing trend
filter: hold an asset only when its 90-day log-price regression slope annualized
and penalized by `R^2` is positive, with a 200-day SMA long-term regime filter.
The indicator is Clenow's adjusted slope concept `[stocks_on_the_move, p.77]`;
the 90-day window and 200-day regime filter are deliberately canonical rather
than optimized `[stocks_on_the_move, p.66-67]`, `[stocks_on_the_move, p.219-220]`.
All signals are shifted one completed daily bar before returns are earned to
avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Exact Configs

Four configs, no local tuning after results:

1. `spy_slope90_sma200`: `SPY`, 90-day adjusted slope > 0 and close > SMA200.
2. `qqq_slope90_sma200`: `QQQ`, 90-day adjusted slope > 0 and close > SMA200.
3. `gld_slope90_sma200`: `GLD`, 90-day adjusted slope > 0 and close > SMA200.
4. `xau_slope90_sma200`: `xauusd`, 90-day adjusted slope > 0 and close > SMA200.

## Data And Window

Use local physical Tiingo daily parquet files under `data/tiingo/daily/prices/`
for `SPY`, `QQQ`, `GLD`, `xauusd` and `SHV`. Audit physical file existence,
first/last timestamp, timezone, columns and missing business-day rate before
testing. Also audit `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/`;
do not synthesize intraday files if absent.

## Benchmarks

Primary benchmark: same-asset buy-and-hold over each config's aligned post-warmup
daily window. Opportunity-cost benchmark: `SPY` buy-and-hold over the same
aligned window.

## Kill Rules

- If strategy CAGR <= same-asset buy-and-hold CAGR, verdict must be `fail`; no
  `candidate_watchlist`, `paper_trade_candidate` or `strict_winner`.
- If any required daily physical file is missing, close `data_blocked` before
  consuming trials.
- Do not tune the 90-day slope window, SMA200 regime filter or slope threshold
  after seeing validation results `[testing_tuning, p.327-335]`.
- PBO >= 0.5 or DSR p-value >= 0.05 blocks strict winner status
  `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

## Planned Gates

- Same-asset CAGR and Sharpe comparison.
- IS MCPT with 200 permutations on the selected fixed rule
  `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations, train/test/step = 756/252/252 when feasible
  `[testing_tuning, p.148-150]`, `[testing_tuning, p.318-320]`.
- PBO over the 4 pre-registered config return streams.
- DSR with cumulative trial accounting.
- Walk-forward positive windows, OOS last 20%, latest 63-day FWD stress,
  bootstrap 99.9% mean-daily CI low and vector parity.

## Trial Accounting

- `cumulative_n_trials` before: 168.
- `n_trials` this iteration: 4.
- `cumulative_n_trials` after if tested: 172.
