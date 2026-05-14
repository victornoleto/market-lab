# SUMMARY — 015-2026-05-14-bollinger-compression-breakout

## Verdict

`fail`. The best Bollinger compression breakout config
(`xau_bb20_2_rv20_p30_exit_mid`) did not beat XAU buy-and-hold on CAGR or Sharpe
and failed IS MCPT, WF MCPT, DSR, WF sufficiency and bootstrap. No deploy
implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily upper-Bollinger breakout configs on `SPY`, `QQQ`, `GLD`
  and `xauusd`.
- Rule: enter when prior close is above the upper Bollinger band and realized
  volatility percentile is <= 30; exit when prior close falls below the middle
  band; hold `SHV` while flat.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed required daily files exist. `1hour/prices` still has 0
  parquet files and `15min/prices` is absent, so no intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_bb20_2_rv20_p30_exit_mid`.

- Strategy: CAGR 4.25%, Sharpe 0.699, MDD -9.24%.
- `xauusd` buy-and-hold: CAGR 17.58%, Sharpe 0.994, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 12.26%, Sharpe 0.821.
- Same-asset total return: strategy +31.99% vs `xauusd` buy-and-hold +194.78%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.445`, 200 reps).
- WF MCPT: FAIL (`p=0.530`, 100 reps).
- PBO: PASS (`0.234`).
- DSR: FAIL (`p=0.7957`, cumulative trials after iteration = 160).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+16.74%`).
- Latest 63d FWD stress: PASS (`+0.69%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0001100`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- The compression filter avoided some drawdown but gave up most of the XAU trend,
  violating the Phase 2 economic floor `[systematic_trading, p.40]`.
- PBO alone was acceptable, but MCPT/DSR/bootstrap do not support a robust edge
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune Bollinger length, sigma, volatility percentile or exit threshold.
Continue Phase 2 with a different daily swing mechanism, or restore/audit true
1h/15m data before testing short-swing hybrids.
