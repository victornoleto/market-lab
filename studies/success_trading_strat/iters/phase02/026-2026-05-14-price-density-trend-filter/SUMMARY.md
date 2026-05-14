# SUMMARY — 026-2026-05-14-price-density-trend-filter

## Verdict

`fail`. The best Price Density trend-filter config (`spy_pd20_lt4_sma200`) improved Sharpe and drawdown versus `SPY` buy-and-hold, but failed the Phase 2 same-asset CAGR floor and failed strict robustness gates. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: hold the asset only when 20-day Price Density is below 4.0 and close is above SMA200; otherwise hold `SHV` `[trading_systems_methods, p.12]`, `[trading_systems_methods, p.13]`, `[trading_systems_methods, p.284]`.
- Signals were shifted one completed daily bar before returns were earned `[advances_fin_ml, p.31-34]`.
- Physical audit confirmed required daily OHLC files exist. `data/tiingo/1hour/prices/` still has 0 parquet files and `data/tiingo/15min/prices/` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `spy_pd20_lt4_sma200`.

- Strategy: CAGR 6.45%, Sharpe 0.797, MDD -20.04%.
- `SPY` buy-and-hold: CAGR 10.87%, Sharpe 0.644, MDD -55.20%.
- Same-asset total return: strategy +659.25% vs `SPY` buy-and-hold +2745.15%.
- `GLD` opportunity context on the same window: CAGR 7.25%, Sharpe 0.549.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset buy-and-hold. Lower drawdown and higher Sharpe do not compensate for lower compound return under this non-hedge hypothesis `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: PASS (`p=0.000`, 200 reps).
- WF MCPT: FAIL (`p=0.060`, 100 reps; strict short-window gate is `<=0.05`).
- PBO: FAIL (`0.512`).
- DSR: PASS (`p=0.0413`, cumulative trials after iteration = 204).
- WF windows: PASS (`21/29` positive).
- OOS: PASS (`+50.74%`).
- Latest 63d FWD stress: PASS (`+10.38%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`+0.0000768`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Price Density acts as another equity de-risking filter: it improves risk-adjusted return and drawdown, but sacrifices too much compound return versus simply owning `SPY`.
- The near WF-MCPT miss (`p=0.060`) and PBO just above the hard threshold do not override the CAGR kill rule.
- Do not locally tune Price Density thresholds, lookbacks, or SMA length after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different mechanism, preferably one that can plausibly increase compound exposure/returns rather than only filtering risk, or restore and audit true `1h`/`15m` files before testing short-swing hybrids.
