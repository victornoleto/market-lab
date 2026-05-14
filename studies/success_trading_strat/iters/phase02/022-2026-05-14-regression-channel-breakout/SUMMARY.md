# SUMMARY — 022-2026-05-14-regression-channel-breakout

## Verdict

`fail`. The best regression-channel breakout config (`xau_regch63_h30`) failed the Phase 2 same-asset CAGR floor and failed same-asset Sharpe, IS MCPT, WF MCPT, DSR, WF sufficiency and bootstrap. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: enter when close breaks above a 63-day projected regression-channel upper band; exit below the projected centerline or after 30 bars `[trading_systems_methods, p.167-169]`, `[trading_systems_methods, p.285]`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`/`QQQ`/`GLD`/`xauusd`/`SHV` files exist and include OHLC columns. `1hour/prices` still has 0 parquet files and `15min/prices` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `xau_regch63_h30`.

- Strategy: CAGR 3.62%, Sharpe 0.787, MDD -10.78%.
- `xauusd` buy-and-hold: CAGR 14.32%, Sharpe 0.916, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 12.31%, Sharpe 0.837.
- Same-asset total return: strategy +26.33% vs `xauusd` buy-and-hold +140.83%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset buy-and-hold. Lower drawdown alone is insufficient under the economic floor `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.460`, 200 reps).
- WF MCPT: FAIL (`p=0.250`, 100 reps).
- PBO: PASS (`0.480`).
- DSR: FAIL (`p=0.7751`, cumulative trials after iteration = 188).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+4.15%`).
- Latest 63d FWD stress: PASS (`+0.69%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0000760`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- The regression channel reduced drawdown but acted mostly as a low-participation gold filter, not a return-compounding replacement for buy-and-hold.
- MCPT and DSR results show the Sharpe improvement was not statistically compelling after trial accounting.
- Do not tune regression window, channel definition, centerline exit or max-hold locally after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different daily mechanism, or restore and audit true `1h`/`15m` files before testing short-swing hybrids. Avoid local tuning of regression-channel parameters.
