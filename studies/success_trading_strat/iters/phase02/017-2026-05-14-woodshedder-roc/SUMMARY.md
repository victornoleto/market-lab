# SUMMARY — 017-2026-05-14-woodshedder-roc

## Verdict

`fail`. The best Woodshedder ROC config (`xau_roc5_252_x2`) did not beat XAU
buy-and-hold on CAGR or Sharpe and failed IS MCPT, WF MCPT, PBO, DSR, WF
sufficiency, latest 63d FWD stress and bootstrap. No deploy implication; capital
remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily ROC configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: enter long when 5-day ROC is below 252-day ROC for two consecutive
  completed bars; exit to `SHV` when 5-day ROC is above 252-day ROC for two
  consecutive completed bars `[trading_systems_methods, p.355]`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed required daily files exist. `1hour/prices` still has 0
  parquet files and `15min/prices` is absent, so no intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_roc5_252_x2`.

- Strategy: CAGR 14.64%, Sharpe 0.960, MDD -20.09%.
- `xauusd` buy-and-hold: CAGR 18.00%, Sharpe 1.094, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 10.64%, Sharpe 0.725.
- Same-asset total return: strategy +121.66% vs `xauusd` buy-and-hold +162.29%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.305`, 200 reps).
- WF MCPT: FAIL (`p=0.460`, 100 reps).
- PBO: FAIL (`0.905`).
- DSR: FAIL (`p=0.6476`, cumulative trials after iteration = 168).
- WF windows: FAIL (`2/2` positive, fewer than 8 windows).
- OOS: PASS (`+38.31%`).
- Latest 63d FWD stress: FAIL (`-13.26%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0001985`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- The Woodshedder ROC rule improved some equity configs versus their own
  buy-and-hold, but selection by Sharpe picked XAU and that failed the mandatory
  Phase 2 same-asset CAGR floor `[systematic_trading, p.40]`.
- PBO/DSR and MCPT strongly reject the selected edge, so ROC lengths/confirmation
  should not be locally tuned `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune Woodshedder ROC lengths, confirmation count or exits locally. Continue
Phase 2 with a different daily swing mechanism, or restore/audit true 1h/15m data
before testing short-swing hybrids.
