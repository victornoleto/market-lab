# SUMMARY — 024-2026-05-14-dual-ma-atr-breakout

## Verdict

`fail`. The best dual MA+ATR breakout config (`xau_ma5_20_atr20_k1`) failed the Phase 2 same-asset CAGR floor and failed most robustness gates. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: enter long when close is above both MA5 and MA20 plus one ATR20; exit when close violates either lower MA-ATR band `[trading_systems_methods, p.352-353]`, `[trading_systems_methods, p.107]`.
- Signals were shifted one completed daily bar before returns were earned `[advances_fin_ml, p.31-34]`.
- Physical audit confirmed daily OHLC files exist for all required tickers. `data/tiingo/1hour/prices/` still has 0 parquet files and `data/tiingo/15min/prices/` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `xau_ma5_20_atr20_k1`.

- Strategy: CAGR 10.89%, Sharpe 0.816, MDD -15.36%.
- `xauusd` buy-and-hold: CAGR 17.41%, Sharpe 0.985, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 9.99%, Sharpe 0.684.
- Same-asset total return: strategy +100.97% vs `xauusd` buy-and-hold +195.51%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset buy-and-hold. Lower drawdown alone is insufficient under the economic floor `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.380`, 200 reps).
- WF MCPT: FAIL (`p=0.580`, 100 reps).
- PBO: FAIL (`0.607`).
- DSR: FAIL (`p=0.7628`, cumulative trials after iteration = 196).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+25.53%`).
- Latest 63d FWD stress: FAIL (`-4.22%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0001691`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- The MA+ATR breakout reduced drawdown on gold but still acted as a lower-return participation filter versus simply holding `xauusd`.
- The short `xauusd` cache window also leaves only 3 annual WF windows, blocking any strict promotion even before MCPT/PBO/DSR failures.
- Do not locally tune MA lengths, ATR length or multiplier after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different mechanism, preferably not another MA/ATR breakout/band variant, or restore and audit true `1h`/`15m` files before testing short-swing hybrids.
