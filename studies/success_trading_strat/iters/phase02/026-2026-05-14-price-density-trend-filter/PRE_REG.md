# PRE_REG — 026-2026-05-14-price-density-trend-filter

## Hypothesis

Kaufman's Price Density measures how much intrawindow path length is consumed per unit of net high-low range; lower density implies cleaner directional movement and should favor trend participation, while high-noise markets should be avoided `[trading_systems_methods, p.12]`, `[trading_systems_methods, p.13]`. This iteration tests a daily long-only participation filter: hold the asset only when lagged Price Density is below a fixed threshold and the asset is above a slow SMA trend filter `[trading_systems_methods, p.284]`.

This is not a hedge/cash-parking mandate. Lower drawdown cannot compensate for lower CAGR versus same-asset buy-and-hold `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Data And Window

- Physical daily cache files required before testing: `SPY`, `QQQ`, `GLD`, `SHV`, `xauusd` under `data/tiingo/daily/prices/`.
- Required columns: adjusted close or close, plus `high` and `low` for Price Density.
- Intraday audit: report whether `data/tiingo/1hour/prices/` and `data/tiingo/15min/prices/` contain physical files. Manifest entries alone are not enough.
- Execution: one completed daily bar lag before returns are earned to avoid same-close lookahead `[advances_fin_ml, p.31-34]`.

## Exact Configs

1. `spy_pd20_lt4_sma200`: `SPY`, Price Density lookback 20, `PD < 4.0`, `close > SMA200`.
2. `qqq_pd20_lt4_sma200`: `QQQ`, Price Density lookback 20, `PD < 4.0`, `close > SMA200`.
3. `gld_pd20_lt4_sma200`: `GLD`, Price Density lookback 20, `PD < 4.0`, `close > SMA200`.
4. `xau_pd20_lt4_sma200`: `xauusd`, Price Density lookback 20, `PD < 4.0`, `close > SMA200`.

The threshold is intentionally sparse: no local tuning of PD thresholds, SMA lengths, or asset-specific overrides after results are known `[testing_tuning, p.327-335]`.

## Benchmarks

- Primary benchmark: same-asset buy-and-hold over the aligned strategy window.
- Opportunity-cost benchmark: `SPY` buy-and-hold over the aligned strategy window.
- Gold context: `GLD` and `xauusd` buy-and-hold where applicable.

## Gates Planned

- Phase 2 economic floor: strategy CAGR must exceed same-asset buy-and-hold CAGR.
- Same-asset Sharpe comparison.
- IS MCPT with 200 permutations when data are sufficient `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations when data are sufficient `[testing_tuning, p.318-320]`.
- PBO across the 4 pre-registered configs `[advances_fin_ml, p.208-211]`.
- DSR with cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward positive-window count, OOS holdout, latest 63d FWD stress, bootstrap 99.9% mean-daily CI, and cross-lib/vector parity.

## Kill Rules

- If any required daily file or OHLC column is missing, close `data_blocked` with `n_trials=0`.
- If CAGR <= same-asset buy-and-hold CAGR, close `fail`; do not assign `candidate_watchlist`, `paper_trade_candidate`, or `strict_winner`.
- If PBO >= 0.5 or DSR p >= 0.05, no strict promotion.
- If MCPT, WF, OOS, FWD, bootstrap or cross-lib gates fail, record the failure and close at most `fail` unless all strict gates pass.

## Trial Accounting

- `cumulative_n_trials` before: 200.
- `n_trials` planned: 4.
- `cumulative_n_trials` after if tested: 204.
