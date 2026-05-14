# SUMMARY — 025-2026-05-14-swing-point-breakout

## Verdict

`fail`. The best conservative swing-point breakout config (`xau_swing5_break_prev_high`) improved Sharpe and drawdown versus `xauusd` buy-and-hold, but failed the Phase 2 same-asset CAGR floor and failed multiple strict gates. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: define swing direction with a fixed percentage reversal filter, go long after a break above the previous upswing high, otherwise hold `SHV` `[trading_systems_methods, p.165]`, `[trading_systems_methods, p.168]`.
- Signals were shifted one completed daily bar before returns were earned `[advances_fin_ml, p.31-34]`.
- Physical audit confirmed daily OHLC files exist for all required tickers. `data/tiingo/1hour/prices/` still has 0 parquet files and `data/tiingo/15min/prices/` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `xau_swing5_break_prev_high`.

- Strategy: CAGR 10.06%, Sharpe 1.117, MDD -11.13%.
- `xauusd` buy-and-hold: CAGR 17.33%, Sharpe 0.984, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 9.93%, Sharpe 0.683.
- Same-asset total return: strategy +92.36% vs `xauusd` buy-and-hold +197.73%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset buy-and-hold. Lower drawdown and higher Sharpe do not compensate for lower compound return under this non-hedge hypothesis `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: FAIL (`p=0.080`, 200 reps).
- WF MCPT: FAIL (`p=0.320`, 100 reps).
- PBO: PASS (`0.278`).
- DSR: FAIL (`p=0.4410`, cumulative trials after iteration = 200).
- WF windows: FAIL (`2/3` positive, fewer than 8 windows).
- OOS: PASS (`+40.98%`).
- Latest 63d FWD stress: FAIL (`-10.95%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0000419`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- The swing-point breakout behaves as another gold participation filter: it reduces drawdown, but gives up too much of the buy-and-hold CAGR.
- The `xauusd` cache still provides only 3 annual WF windows, which blocks strict promotion even before DSR/MCPT failures.
- Do not locally tune swing filters or breakout/exit definitions after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different mechanism, preferably not another event-driven swing-high/low breakout, or restore and audit true `1h`/`15m` files before testing short-swing hybrids.
