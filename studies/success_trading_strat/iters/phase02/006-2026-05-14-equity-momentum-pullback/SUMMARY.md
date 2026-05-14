# SUMMARY — 006-2026-05-14-equity-momentum-pullback

## Verdict

`fail`. The best daily SPY pullback config improved Sharpe and drawdown versus
SPY buy-and-hold, and passed IS MCPT, WF MCPT, PBO, WF, OOS and cross-lib, but
failed DSR, latest 63d FWD stress and bootstrap. No deploy implication; capital
remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily close-only pullback configs on `SPY` and `QQQ`.
- Rule: only enter when close is above lagged `SMA200` and the recent 3d/5d
  return is below a fixed negative threshold; hold for 5 or 10 bars, else hold
  `SHV`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`, `QQQ` and `SHV` files through
  2026-05-13. `1hour/prices` exists but has 0 parquet files; `15min/prices` is
  absent. No intraday bars were synthesized.

## Benchmark Comparison

Best config: `spy_pb3_m2_hold5`.

- Strategy: CAGR 5.29%, Sharpe 0.862, MDD -9.58%.
- `SPY` buy-and-hold: CAGR 10.92%, Sharpe 0.621, MDD -54.67%.
- Same-asset total return: strategy +159.77% vs `SPY` buy-and-hold +580.72%.

The rule is a robust drawdown reducer, but it gives up too much CAGR and fails
trial-deflated significance.

## Gates

- Economic Sharpe vs same asset: PASS.
- IS MCPT: PASS (`p=0.010`, 200 reps; strict gate `<=0.01`).
- WF MCPT: PASS (`p=0.010`, 100 reps).
- PBO: PASS (`0.310`).
- DSR: FAIL (`p=0.1414`, cumulative trials after iteration = 124).
- WF windows: PASS (`15/15` positive).
- OOS: PASS (`+35.54%`).
- Latest 63d FWD stress: FAIL (`-2.55%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0000137`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Daily equity pullbacks in a broad uptrend are much stronger than the previous
  gap-continuation rule on risk-adjusted terms, but the edge is still too weak
  after DSR and bootstrap `[advances_fin_ml, p.222-223]`.
- The family is defensive rather than compounding-oriented: lower drawdown comes
  at a large opportunity-cost penalty versus SPY buy-and-hold.
- Intraday Track B remains blocked by missing physical 1h/15m cache files, so no
  short-swing claim is allowed `[testing_tuning, p.327-335]`.

## Recommended Next Step

Do not tune local pullback thresholds. Continue Phase 2 with a different daily
swing mechanism or restore true 1h/15m data before testing short-swing Track B.
