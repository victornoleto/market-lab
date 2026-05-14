# SUMMARY — 007-2026-05-14-equity-bollinger-reversion

## Verdict

`fail`. The best daily SPY Bollinger mean-reversion config reduced drawdown versus
SPY buy-and-hold, but it underperformed on CAGR and Sharpe and failed MCPT, PBO,
DSR, latest 63d FWD stress and bootstrap. No deploy implication; capital remains
100% Plano C.

## What Was Tested

- 4 pre-registered daily close-only Bollinger lower-band reversion configs on
  `SPY` and `QQQ`.
- Rule: only enter above lagged `SMA200`, buy a close below the lower Bollinger
  Band, exit at the middle band or max hold, otherwise hold `SHV`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`, `QQQ` and `SHV` files through
  2026-05-13. `1hour/prices` exists but has 0 parquet files; `15min/prices` is
  absent. No intraday bars were synthesized.

## Benchmark Comparison

Best config: `spy_bb20_2_hold10`.

- Strategy: CAGR 3.38%, Sharpe 0.551, MDD -17.17%.
- `SPY` buy-and-hold: CAGR 10.92%, Sharpe 0.621, MDD -54.67%.
- Same-asset total return: strategy +84.92% vs `SPY` buy-and-hold +580.72%.

The rule is defensive and too underinvested to compete with the same-asset
benchmark.

## Gates

- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.230`, 200 reps; strict gate `<=0.01`).
- WF MCPT: FAIL (`p=0.330`, 100 reps).
- PBO: FAIL (`0.734`).
- DSR: FAIL (`p=0.5942`, cumulative trials after iteration = 128).
- WF windows: PASS (`12/15` positive).
- OOS: PASS (`+23.30%`).
- Latest 63d FWD stress: FAIL (`-2.56%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0000386`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Volatility-normalized Bollinger entries did not improve the Phase 2 equity
  pullback family; lower drawdown came with a large opportunity-cost penalty.
- PBO and MCPT both reject the panel, so local tuning of band windows, sigma or
  exits is not justified `[testing_tuning, p.327-335]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files, so no
  short-swing claim is allowed.

## Recommended Next Step

Do not tune local Bollinger parameters. Continue Phase 2 with a different daily
swing mechanism, preferably away from equity pullback/reversion, or restore true
1h/15m data before testing short-swing Track B.
