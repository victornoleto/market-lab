# SUMMARY — 014-2026-05-14-vidya-adaptive-trend

## Verdict

`fail`. The best VIDYA adaptive-trend config (`xau_vidya9_30`) did not beat XAU
buy-and-hold on CAGR and failed IS MCPT, WF MCPT, DSR, WF sufficiency, latest FWD
stress and bootstrap. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily VIDYA trend-filter configs on `SPY`, `QQQ`, `GLD` and
  `xauusd`.
- Rule: hold the asset when prior close is above VIDYA(9,30, base constant 0.20),
  otherwise hold `SHV`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed required daily files exist. `1hour/prices` still has 0
  parquet files and `15min/prices` is absent, so no intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_vidya9_30`.

- Strategy: CAGR 14.80%, Sharpe 0.989, MDD -21.49%.
- `xauusd` buy-and-hold: CAGR 17.48%, Sharpe 0.987, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 10.02%, Sharpe 0.686.
- Same-asset total return: strategy +152.62% vs `xauusd` buy-and-hold +194.91%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: FAIL (`p=0.350`, 200 reps).
- WF MCPT: FAIL (`p=0.120`, 100 reps).
- PBO: PASS (`0.294`).
- DSR: FAIL (`p=0.5534`, cumulative trials after iteration = 156).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+23.61%`).
- Latest 63d FWD stress: FAIL (`-10.38%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0001760`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- VIDYA reduced little and lagged enough to give up CAGR versus XAU buy-and-hold;
  this violates the Phase 2 economic floor.
- PBO was acceptable, but MCPT/DSR/bootstrap/FWD do not support a robust edge
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune VIDYA volatility windows or add local thresholds. Continue Phase 2
with a different daily swing mechanism, or restore/audit true 1h/15m data before
testing short-swing hybrids.
