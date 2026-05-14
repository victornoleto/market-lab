# SUMMARY — 021-2026-05-14-wilder-asi-swing-breakout

## Verdict

`fail`. The best Wilder ASI swing-breakout config (`xau_asi20_10_h20`) failed
the Phase 2 same-asset CAGR floor and failed IS MCPT, WF MCPT, PBO, DSR, latest
63d FWD stress and bootstrap. No deploy implication; capital remains 100% Plano
C.

## What Was Tested

- 4 pre-registered daily configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: Wilder Accumulated Swing Index breakout above the prior 20 bars, exit on
  breakdown below the prior 10 bars or max 20-bar hold `[trading_systems_methods,
  p.193-195]`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`/`QQQ`/`GLD`/`xauusd`/`SHV` files exist and
  include OHLC columns. `1hour/prices` still has 0 parquet files and
  `15min/prices` is absent, so no intraday hybrid was synthesized.

## Benchmark Comparison

Best config: `xau_asi20_10_h20`.

- Strategy: CAGR 8.80%, Sharpe 0.683, MDD -18.68%.
- `xauusd` buy-and-hold: CAGR 17.51%, Sharpe 0.990, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 9.80%, Sharpe 0.673.
- Same-asset total return: strategy +76.53% vs `xauusd` buy-and-hold +196.62%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold. The lower drawdown was too small to offset the large CAGR deficit
under this study's economic floor `[systematic_trading, p.40]`,
`[testing_tuning, p.327-335]`.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.715`, 200 reps).
- WF MCPT: FAIL (`p=0.530`, 100 reps).
- PBO: FAIL (`0.516`).
- DSR: FAIL (`p=0.8587`, cumulative trials after iteration = 184).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+9.37%`).
- Latest 63d FWD stress: FAIL (`-8.17%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.000232`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- ASI breakouts again produced partial participation in the gold trend but not
  enough compounded return to justify replacing buy-and-hold.
- The latest 63d FWD loss and failed bootstrap confirm that the rule is not a
  promotion candidate even before considering PBO/DSR.
- Do not tune ASI entry/exit lookbacks or max-hold lengths locally after this fail
  `[testing_tuning, p.327-335]`.

## Recommended Next Step

Continue Phase 2 with a different mechanism, or restore and audit true `1h`/`15m`
files before testing short-swing hybrids. Avoid local tuning of Wilder ASI
breakout parameters.
