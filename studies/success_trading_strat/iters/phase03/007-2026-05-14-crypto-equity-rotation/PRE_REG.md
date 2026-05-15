# PRE_REG - Phase 3 Iteration 007

## Hypothesis

Test a crypto/equity high-beta rotation over `BTCUSD`, `ETHUSD`, `QQQ` and `GLD`. The mechanism can beat buy-and-hold only if it persistently selects the stronger high-volatility return engine while staying invested, rather than using cash as a defensive filter. Cross-sectional momentum and relative strength are grounded in ranking the strongest trends `[stocks_on_the_move, p.66-67]`, `[trading_systems_methods, p.542-544]`; volatility-adjusted sizing/ranking is used only as a risk-normalized score, not as post-hoc tuning `[systematic_trading, p.137-148]`.

## Data And Window

- Required physical daily parquet files before any backtest: `data/tiingo/daily/prices/BTCUSD.parquet`, `ETHUSD.parquet`, `QQQ.parquet`, `GLD.parquet`, `SPY.parquet`.
- Optional audit context: `SHV.parquet` if present, but no cash allocation is configured.
- Use adjusted close when present, otherwise close.
- Aligned window: intersection of all required daily close series after dropping missing values. The script will record rows, first/last date, timezone, columns and missing-business-day rate before testing.
- Crypto/FX endpoint staleness is a known repo caveat; if either crypto file is absent, lacks a close column, or ends before 2026-04-01, close as `data_blocked` without substituting proxies.

## Exact Configs

Six pre-registered configs, all long-only and always invested after warmup:

1. `top1_m63`: top 1 asset by 63-trading-day total return.
2. `top1_m126`: top 1 asset by 126-trading-day total return.
3. `top2_m63`: equal-weight top 2 assets by 63-trading-day total return.
4. `top2_m126`: equal-weight top 2 assets by 126-trading-day total return.
5. `top1_m126_rv63`: top 1 by 126-day total return divided by 63-day realized volatility.
6. `top2_m126_rv63`: equal-weight top 2 by the same volatility-adjusted score.

Signals are lagged one completed daily bar. No leverage, no shorting, no tax/cost model in this smoke iteration; turnover is reported as a caveat `[systematic_trading, p.185-188]`.

## Benchmarks

- Primary benchmark: equal-weight buy-and-hold of `BTCUSD`, `ETHUSD`, `QQQ` and `GLD` on the exact aligned dates.
- Same-asset/context benchmarks: `BTCUSD` buy-and-hold, `ETHUSD` buy-and-hold, `QQQ` buy-and-hold and `GLD` buy-and-hold.
- Opportunity benchmark: `SPY` buy-and-hold on aligned dates.

## Economic Kill Rule

The iteration must close `fail` unless the best pre-registered strategy has both:

- CAGR greater than the primary equal-weight buy-and-hold benchmark.
- Terminal wealth greater than the primary equal-weight buy-and-hold benchmark.

No `economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate` or `strict_winner` label is allowed without both economic gates passing `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Planned Gates

- IS MCPT with 200 joint row permutations; pass threshold `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT with 100 post-initial-train joint row permutations; pass threshold `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO with 10 blocks; pass `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR using cumulative trials after this iteration; pass `p < 0.05` `[advances_fin_ml, p.222-223]`.
- Walk-forward windows: at least 6 positive windows and at least 8 windows total when the aligned data support it `[testing_tuning, p.148-150]`.
- Single-block OOS positive, latest 63-observation FWD stress positive, bootstrap 99.9% mean-return CI low > 0, and cross-lib/vector CAGR delta <= 3pp `[testing_tuning, p.246-247]`, `[advances_fin_ml, p.31-34]`.

## Kill Rules

- Missing required physical data or stale crypto ending before 2026-04-01 => `data_blocked`.
- Any economic kill rule failure => `fail`.
- Any PBO/DSR/MCPT/WF/OOS/FWD/bootstrap/cross-lib failure blocks `strict_winner`.
- If the best result only wins by overfitting crypto endpoint staleness or by excessive turnover, record the caveat and do not promote.

## Trial Accounting

- `cumulative_n_trials` before: 252.
- New strategy configs: 6.
- `cumulative_n_trials` after if data are testable: 258.
- If `data_blocked`, `n_trials=0` and cumulative remains 252.
