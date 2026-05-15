# PRE_REG - Phase 3 Iteration 003

## Hypothesis

Semiconductor/technology LETFs can beat broad buy-and-hold because leverage is the return engine, while one-bar-lagged volatility targeting attempts to reduce daily-leverage path dependency and crash convexity drag `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.5-7]`, `[systematic_trading, p.137-148]`. This is a distinct universe from Phase 3 iterations 001-002, not a local retune of Nasdaq or S&P LETF parameters `[testing_tuning, p.327-335]`.

## Data And Window

Physical daily parquet files will be audited before testing for `SMH`, `SOXX`, `SOXL`, `TECL`, `XLK`, `QQQ`, `SPY` and `SHV`. The backtest window is the aligned period available after each traded LETF's inception, after warmup.

No intraday data will be synthesized. Rules use adjusted close only.

## Configs

Six pre-registered configs:

- `soxl_vt45_rv63`: `SOXL`, realized-vol lookback 63, target vol 45%, no crash multiplier.
- `soxl_vt60_rv63_dd35_half`: `SOXL`, lookback 63, target vol 60%, halve exposure when LETF drawdown <= -35%.
- `soxl_vt75_rv21_dd35_half`: `SOXL`, lookback 21, target vol 75%, halve exposure when LETF drawdown <= -35%.
- `tecl_vt40_rv63`: `TECL`, lookback 63, target vol 40%, no crash multiplier.
- `tecl_vt55_rv63_dd30_half`: `TECL`, lookback 63, target vol 55%, halve exposure when LETF drawdown <= -30%.
- `tecl_vt70_rv21_dd30_half`: `TECL`, lookback 21, target vol 70%, halve exposure when LETF drawdown <= -30%.

All exposure weights are capped at 100% of the selected LETF and are applied with a one-bar lag. Unused capital goes to `SHV`.

## Benchmarks

Primary economic benchmark is conservative for semiconductor systems:

- `QQQ` buy-and-hold on aligned dates.
- Equal-weight `SMH/SOXX` buy-and-hold on aligned dates.

The strategy must beat both in CAGR and terminal wealth to receive any label above `fail`. Same-LETF buy-and-hold (`SOXL` or `TECL`) and `SPY` buy-and-hold are context only.

## Gates

- IS MCPT `p <= 0.01` `[testing_tuning, p.318-320]`.
- WF MCPT `p <= 0.05` `[testing_tuning, p.318-320]`.
- PBO `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR `p < 0.05` using cumulative trials after this iteration `[advances_fin_ml, p.222-223]`.
- Walk-forward at least 6 positive windows and at least 8 total windows `[testing_tuning, p.148-150]`.
- Single-block OOS positive and latest 63-trading-day FWD positive `[advances_fin_ml, p.196-202]`.
- Bootstrap 99.9% mean daily return CI low > 0 `[testing_tuning, p.246-247]`.
- Cross-lib/vector parity CAGR delta <= 3pp `[advances_fin_ml, p.31-34]`.

## Kill Rules

- CAGR or terminal wealth <= either primary benchmark (`QQQ` or equal-weight `SMH/SOXX`) => `fail`.
- Any missing required traded or benchmark daily parquet file => `data_blocked`.
- Any PBO/DSR/MCPT/WF/OOS/FWD/bootstrap/cross-lib failure blocks `strict_winner`.
- Do not relabel as `candidate_watchlist` or `paper_trade_candidate` inside this iteration.

## Trial Accounting

- `cumulative_n_trials` before: 228.
- `n_trials` planned: 6.
- `cumulative_n_trials` after: 234.
