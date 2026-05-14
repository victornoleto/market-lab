# SUMMARY — 020-2026-05-14-elder-ray-triple-screen

## Verdict

`fail`. The best Elder-Ray Triple Screen proxy config
(`xau_eray_12_26_9_ema13_bear3_h10`) failed the Phase 2 same-asset CAGR floor
and failed IS MCPT, WF MCPT and WF-window sufficiency. No deploy implication;
capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: weekly MACD histogram direction as the trend screen, daily Elder-Ray Bear
  Power rising from negative territory as the timing screen, and `SHV` while flat
  `[trading_systems_methods, p.835-838]`, `[trading_systems_methods, p.837]`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`/`QQQ`/`GLD`/`xauusd`/`SHV` files exist.
  `1hour/prices` still has 0 parquet files and `15min/prices` is absent, so no
  intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `xau_eray_12_26_9_ema13_bear3_h10`.

- Strategy: CAGR 2.85%, Sharpe 3.106, MDD -1.03%.
- `xauusd` buy-and-hold: CAGR 14.18%, Sharpe 0.909, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 12.10%, Sharpe 0.825.
- Same-asset total return: strategy +20.25% vs `xauusd` buy-and-hold +138.71%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold. Lower drawdown and high Sharpe do not compensate for the lower
compound return under this study's rules.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: FAIL (`p=0.870`, 200 reps).
- WF MCPT: FAIL (`p=0.920`, 100 reps).
- PBO: PASS (`0.302`).
- DSR: PASS (`p=0.000815`, cumulative trials after iteration = 180).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+4.15%`).
- Latest 63d FWD stress: PASS (`+0.69%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`+0.0000757`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Elder-Ray timing created a very low-volatility gold exposure, but it mostly
  parked in `SHV` and sacrificed too much `xauusd` compounded return.
- The strong Sharpe and DSR are not enough: MCPT strongly rejects the edge versus
  permuted paths, and the short `xauusd` data window gives too few WF windows.
- Do not tune MACD periods, EMA13, Bear Power lookback or hold length locally
  after this fail `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different daily swing mechanism, or restore and audit true
`1h`/`15m` files before testing short-swing hybrids. Avoid local tuning of the
Elder-Ray Triple Screen parameters.
