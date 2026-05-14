# SUMMARY — 018-2026-05-14-clenow-slope-trend

## Verdict

`fail`. The best Clenow adjusted-slope config (`xau_slope90_sma200`) did not beat
XAU buy-and-hold on CAGR or Sharpe and failed IS MCPT, WF MCPT, PBO, DSR, WF
sufficiency, latest 63d FWD stress and bootstrap. No deploy implication; capital
remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily adjusted-slope trend configs on `SPY`, `QQQ`, `GLD` and
  `xauusd`.
- Rule: hold the asset when 90-day log-price regression slope annualized and
  penalized by `R^2` is positive, and close is above SMA200; otherwise hold `SHV`
  `[stocks_on_the_move, p.66-67]`, `[stocks_on_the_move, p.77]`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed required daily files exist. `1hour/prices` still has 0
  parquet files and `15min/prices` is absent, so no intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_slope90_sma200`.

- Strategy: CAGR 14.57%, Sharpe 0.994, MDD -20.09%.
- `xauusd` buy-and-hold: CAGR 17.36%, Sharpe 1.070, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 11.21%, Sharpe 0.765.
- Same-asset total return: strategy +127.44% vs `xauusd` buy-and-hold +162.95%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.145`, 200 reps).
- WF MCPT: FAIL (`p=0.320`, 100 reps).
- PBO: FAIL (`0.885`).
- DSR: FAIL (`p=0.6040`, cumulative trials after iteration = 172).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+44.41%`).
- Latest 63d FWD stress: FAIL (`-11.54%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0001432`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- The adjusted-slope/SMA200 filter reduced drawdown versus buy-and-hold for the
  equity and gold ETFs, but it again traded away too much compounded return for
  Phase 2 promotion `[systematic_trading, p.40]`.
- PBO, DSR and MCPT reject the selected edge, so slope window, SMA length and
  threshold should not be locally tuned `[testing_tuning, p.327-335]`,
  `[advances_fin_ml, p.208-211]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune Clenow slope window, SMA200 regime filter or positive-score threshold
locally. Continue Phase 2 with a different daily swing mechanism, or restore and
audit true 1h/15m data before testing short-swing hybrids.
