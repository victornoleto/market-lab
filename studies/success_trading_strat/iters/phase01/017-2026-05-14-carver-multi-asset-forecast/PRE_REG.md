# PRE_REG — 017 Carver Multi-Asset Forecast

## Hypothesis

Test a diversified long-only multi-asset forecast-combination mechanism rather
than another binary equity beta throttle. Each asset receives a volatility-
standardised EWMAC forecast, only positive forecasts are eligible, and portfolio
weights are inverse-volatility normalised before a conservative volatility target
is applied. The design follows Carver's modular forecast, volatility targeting and
portfolio position framework `[systematic_trading, p.40]`, `[systematic_trading,
p.118-119]`, `[systematic_trading, p.137-148]`, `[systematic_trading,
p.159-173]`. EWMAC parameter pairs use the canonical 4:1 family rather than local
tuning `[systematic_trading, p.284-285]`.

## Data And Window

- Source: local Tiingo daily adjusted close parquet files.
- Tickers: `SPY`, `QQQ`, `TLT`, `IEF`, `GLD`, `SHV`.
- Window: common daily overlap from 2010-01-01 onward.
- Staleness kill: common data must end on or after 2026-03-31.
- Execution lag: forecasts and volatility estimates are shifted one trading day.

## Exact Configs

1. `risk4_ewmac8_32_vt10`: universe `SPY/QQQ/TLT/GLD`, EWMAC 8/32 scalar 5.3,
   target vol 10%, cap 1.5.
2. `risk4_ewmac16_64_vt10`: universe `SPY/QQQ/TLT/GLD`, EWMAC 16/64 scalar 3.75,
   target vol 10%, cap 1.5.
3. `risk5_ewmac8_32_vt10`: universe `SPY/QQQ/TLT/IEF/GLD`, EWMAC 8/32 scalar 5.3,
   target vol 10%, cap 1.5.
4. `risk5_ewmac16_64_vt15`: universe `SPY/QQQ/TLT/IEF/GLD`, EWMAC 16/64 scalar
   3.75, target vol 15%, cap 1.5.

If every forecast is non-positive, the strategy holds `SHV`.

## Benchmark

Benchmark is same-window static equal-weight over each config's risky universe,
without volatility targeting. Winner requires strategy Sharpe > benchmark Sharpe.

## Planned Gates

- Data freshness.
- Economic Sharpe versus benchmark.
- IS MCPT with 200 permutations `[testing_tuning, p.318-320]`.
- WF MCPT with 100 permutations `[testing_tuning, p.318-320]`.
- PBO with 8 blocks, pass `<0.5` `[advances_fin_ml, p.208-211]`.
- DSR with cumulative trials after this iteration, pass `p<0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward positive windows, OOS, latest 63d FWD stress, bootstrap 99.9% CI
  low and independent NumPy-style cross-check.

## Kill Rules

- If required data are unavailable or stale, stop as `data_blocked`.
- If benchmark Sharpe, IS/WF MCPT, PBO or DSR fail, no winner claim.
- Do not add configs after seeing results.
- Do not tune EWMAC lookbacks, vol target or asset universe inside this iteration.

## Trial Accounting

- `cumulative_n_trials` before: 52.
- `n_trials` planned: 4.
- `cumulative_n_trials` after: 56.
