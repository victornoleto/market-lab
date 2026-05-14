# SUMMARY — 013-2026-05-14-gold-relative-strength

## Verdict

`fail`. The best relative-strength config (`xau_rs200_m126`) did not beat XAU
buy-and-hold on CAGR or Sharpe and failed IS MCPT, WF MCPT, DSR, WF sufficiency,
FWD stress and bootstrap. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily gold relative-strength configs on `GLD` and `xauusd`.
- Rule: hold gold when gold/SPY is above its rolling SMA and own trailing momentum
  is positive; otherwise hold `SHV`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed required daily files exist. `1hour/prices` still has 0
  parquet files and `15min/prices` is absent, so no intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_rs200_m126`.

- Strategy: CAGR 14.31%, Sharpe 0.915, MDD -20.09%.
- `xauusd` buy-and-hold: CAGR 22.84%, Sharpe 1.247, MDD -20.51%.
- `SPY` opportunity benchmark: CAGR 13.30%, Sharpe 0.807.
- Same-asset total return: strategy +88.46% vs `xauusd` buy-and-hold +165.08%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.395`, 200 reps).
- WF MCPT: FAIL (`p=0.410`, 100 reps).
- PBO: PASS (`0.484`).
- DSR: FAIL (`p=0.7467`, cumulative trials after iteration = 152).
- WF windows: FAIL (`1/1` positive, fewer than 8 windows).
- OOS: PASS (`+37.79%`).
- Latest 63d FWD stress: FAIL (`-10.44%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0004226`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Gold relative-strength versus SPY is not enough to beat gold buy-and-hold during
  this XAU window; it mostly gates exposure and gives up compounding.
- PBO was barely below the hard threshold, but MCPT/DSR/bootstrap show no robust
  edge `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune gold/SPY SMA lengths or momentum lookbacks locally. Continue Phase 2
with a different daily swing mechanism, or restore true 1h/15m data before testing
short-swing hybrids.
