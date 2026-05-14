# SUMMARY — 027-2026-05-14-williams-r-exhaustion

## Verdict

`fail`. The best Williams %R exhaustion-reversal config (`qqq_wr14_os90_x50_sma200_h10`) improved Sharpe and drawdown versus `QQQ` buy-and-hold, but failed the Phase 2 same-asset CAGR floor and failed strict robustness gates. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: enter when Williams %R(14) is `<= -90` while price is above `SMA200`; exit at `%R >= -50` or after 10 bars; otherwise hold `SHV` `[trading_systems_methods, p.385-386]`, `[trading_systems_methods, p.172]`.
- Signals were shifted one completed daily bar before returns were earned `[advances_fin_ml, p.31-34]`.
- Physical audit confirmed required daily OHLC files exist. `data/tiingo/1hour/prices/` still has 0 parquet files and `data/tiingo/15min/prices/` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `qqq_wr14_os90_x50_sma200_h10`.

- Strategy: CAGR 6.07%, Sharpe 0.788, MDD -15.45%.
- `QQQ` buy-and-hold: CAGR 9.38%, Sharpe 0.469, MDD -82.97%.
- Same-asset total return: strategy +371.33% vs `QQQ` buy-and-hold +956.42%.
- `SPY` opportunity context on the same window: CAGR 8.52%, Sharpe 0.520.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset buy-and-hold. Lower drawdown and higher Sharpe do not compensate for lower compound return under this non-hedge hypothesis `[systematic_trading, p.40]`, `[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: PASS (`p=0.005`, 200 reps).
- WF MCPT: PASS (`p=0.010`, 100 reps).
- PBO: FAIL (`0.651`).
- DSR: FAIL (`p=0.0918`, cumulative trials after iteration = 208).
- WF windows: PASS (`17/23` positive).
- OOS: PASS (`+35.19%`).
- Latest 63d FWD stress: FAIL (`-1.96%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`+0.0000469`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Williams %R exhaustion behaves like another defensive equity entry filter: it improves realized risk but gives up too much compound return versus simply holding `QQQ`.
- Unlike many prior daily swing attempts, both MCPT gates passed; the remaining failures were economic CAGR, PBO, DSR and recent FWD stress.
- Do not locally tune Williams %R length, entry/exit thresholds, hold length or the `SMA200` filter after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different mechanism that can plausibly increase compound exposure/returns rather than only filtering risk, or restore and audit true `1h`/`15m` files before testing short-swing hybrids.
