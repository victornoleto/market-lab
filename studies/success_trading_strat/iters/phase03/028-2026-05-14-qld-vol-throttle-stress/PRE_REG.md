# PRE_REG - Phase 3 Iteration 028

## Hypothesis

Stress the Phase 3 iteration 027 best `QLD/TLT/GLD` volatility-throttled sleeve without changing parameters or selecting a new config. If the economic edge is robust rather than a full-window artifact, it should keep beating the pre-registered buy-and-hold benchmarks after conservative rolling-window and friction stresses `[testing_tuning, p.327-335]`, `[leverage_for_the_long_run, p.4-7]`.

The mechanism remains controlled LETF exposure: leverage can magnify returns only in favorable low-volatility/streak regimes, while high-volatility path dependency can destroy daily-levered compounding `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`. Stressing the selected result is required because DSR/PBO/MCPT are hard anti-overfit controls and prior validation failures remain binding `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`, `[testing_tuning, p.318-320]`.

## Exact Config

No new strategy configs are tested. Recompute only the previously selected iteration 027 config:

- `qld70_tlt15_gld15_rv126_q30_70_b50_c20`
- Monthly rebalance.
- Base weights: `QLD=70%`, `TLT=15%`, `GLD=15%`.
- QQQ realized-volatility lookback: `126` trading days.
- Rolling quantile window: `756` trading days, lagged one bar.
- If lagged realized volatility <= 30th percentile: add `+50%` QLD gross exposure.
- If lagged realized volatility >= 70th percentile: cut `-20%` QLD exposure.
- Annual financing drag on gross exposure above `1.0`: `5%`.
- Extra stress drags: `25`, `50`, `100` bps/year subtracted from strategy returns only.

All signals are lagged and evaluated only at month boundaries. No parameter will be changed after seeing results `[testing_tuning, p.327-335]`.

## Data And Window

Required physical daily parquets before running:

- `data/tiingo/daily/prices/QLD.parquet`
- `data/tiingo/daily/prices/TLT.parquet`
- `data/tiingo/daily/prices/GLD.parquet`
- `data/tiingo/daily/prices/QQQ.parquet`
- `data/tiingo/daily/prices/SPY.parquet`
- `data/tiingo/daily/prices/SHV.parquet`

Use the aligned daily adjusted-close window from all required files. Record rows, first/last date, columns, timezone and missing-business-day rate. No manifest-only data and no intraday synthesis.

## Benchmarks

Primary benchmark hierarchy from `PHASE3_BH_BEATER_SPEC.md`:

- Primary 1: `QQQ` buy-and-hold on aligned dates.
- Primary 2: equal-weight `QLD/TLT/GLD` buy-and-hold on aligned dates.
- Opportunity benchmark: `SPY` buy-and-hold on aligned dates.
- Context: raw `QLD`, `TLT`, `GLD`, `SHV` buy-and-hold.

## Planned Gates

This is a stress-only iteration, not a new candidate optimization.

- Full-window strategy CAGR and terminal wealth must beat both primary benchmarks and SPY opportunity benchmark.
- Under each extra drag (`25`, `50`, `100` bps/year), full-window strategy CAGR and terminal wealth must still beat both primary benchmarks.
- Rolling 3-year windows, stepped monthly: at least 90% of windows must beat both primary benchmarks in CAGR and terminal wealth.
- Rolling 5-year windows, stepped monthly: at least 90% of windows must beat both primary benchmarks in CAGR and terminal wealth.
- Previous strict gates from iteration 027 remain binding: IS MCPT, WF MCPT and DSR failed, so this iteration cannot become `strict_winner`, `candidate_watchlist` or `paper_trade_candidate` even if stress passes `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.

MCPT/PBO/DSR are not recomputed because no new config is selected; previous failures are carried forward conservatively.

## Kill Rules

- If any full-window economic benchmark gate fails, status is `fail`.
- If any extra-drag stress loses to either primary benchmark in CAGR or terminal wealth, status is `fail`.
- If rolling 3-year or 5-year pass rate is below 90% versus either primary benchmark, status is `fail`.
- If data are missing, stale or physically absent for a required ticker, status is `data_blocked`.
- No label above `fail` is allowed unless all economic and validation gates pass; previous MCPT/DSR failures block promotion.

## Trial Accounting

- `cumulative_n_trials` before: `312`.
- New strategy configs: `0`.
- `cumulative_n_trials` after: `312`.
