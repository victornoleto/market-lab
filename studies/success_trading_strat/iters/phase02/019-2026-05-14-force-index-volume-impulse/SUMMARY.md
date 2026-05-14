# SUMMARY — 019-2026-05-14-force-index-volume-impulse

## Verdict

`fail`. The best Force Index volume impulse config
(`gld_fi13_z126_e05_x0_sma200_h20`) did not beat `GLD` buy-and-hold on CAGR or
Sharpe and failed IS MCPT, WF MCPT, PBO, DSR and bootstrap. No deploy implication;
capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily Force Index configs on `SPY`, `QQQ` and `GLD`.
- Rule: enter when smoothed Force Index z-score confirms positive volume impulse
  and close is above SMA200; exit on z-score decay, SMA break or max hold
  `[trading_systems_methods, p.836]`, `[trading_systems_methods, p.13]`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`/`QQQ`/`GLD`/`SHV`/`xauusd` files exist;
  `1hour/prices` still has 0 parquet files and `15min/prices` is absent, so no
  intraday bars were synthesized.
- `xauusd` was benchmark context only because the hypothesis requires volume and
  `GLD` is the conservative gold ETF proxy.

## Benchmark Comparison

Best config: `gld_fi13_z126_e05_x0_sma200_h20`.

- Strategy: CAGR 5.63%, Sharpe 0.601, MDD -21.96%.
- `GLD` buy-and-hold: CAGR 11.44%, Sharpe 0.683, MDD -45.56%.
- `SPY` opportunity benchmark: CAGR 11.22%, Sharpe 0.650.
- `xauusd` context benchmark: CAGR 5.39%, Sharpe 0.569.
- Same-asset total return: strategy +208.70% vs `GLD` buy-and-hold +830.21%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.445`, 200 reps).
- WF MCPT: FAIL (`p=0.880`, 100 reps).
- PBO: FAIL (`0.663`).
- DSR: FAIL (`p=0.4985`, cumulative trials after iteration = 176).
- WF windows: PASS (`13/17` positive).
- OOS: PASS (`+69.06%`).
- Latest 63d FWD stress: PASS (`+0.85%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0000694`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Volume impulse plus trend filtering reduced drawdown versus `GLD`, but again
  exchanged too much same-asset compounded return for Phase 2 promotion.
- MCPT and PBO strongly reject the selected edge, so Force Index EMA length,
  z-score windows/thresholds and hold length should not be locally tuned
  `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune Force Index volume impulse parameters locally. Continue Phase 2 with a
different daily swing mechanism, or restore and audit true 1h/15m data before any
short-swing hybrid.
