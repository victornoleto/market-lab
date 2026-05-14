# SUMMARY — 004-2026-05-14-equity-volatility-system

## Verdict

`fail`. The best daily SPY/QQQ volatility reversal config improved QQQ Sharpe and
drawdown versus buy-and-hold, but failed both MCPT gates and DSR. No deploy
implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily volatility-system configs on `SPY` and `QQQ`.
- Rule: enter risk after an upward reversal from swing low by `k * average True
  Range`; exit after a downward reversal from swing high by the same distance.
- `k` values: 2.5 and 3.0; range lookback: 20 daily bars.
- Signals were shifted one bar before returns were earned; flat sleeve was `SHV`.
- Physical audit confirmed daily `SPY`, `QQQ` and `SHV` files exist through
  2026-05-13. `1hour/prices` exists but has 0 parquet files; `15min/prices` is
  absent. No intraday bars were synthesized.

## Benchmark Comparison

Best config: `qqq_vs20_k30`.

- Strategy: CAGR 9.34%, Sharpe 0.629, MDD -47.42%.
- `QQQ` buy-and-hold: CAGR 10.60%, Sharpe 0.509, MDD -82.97%.
- `SPY` context over aligned window: CAGR 8.39%, Sharpe 0.515.

The rule is a drawdown reducer and modest Sharpe improver, but it gives up CAGR
and the validation profile is not close to promotion.

## Gates

- Economic Sharpe vs `QQQ`: PASS.
- IS MCPT: FAIL (`p=0.940`, 200 reps).
- WF MCPT: FAIL (`p=0.970`, 100 reps).
- PBO: PASS (`0.048`).
- DSR: FAIL (`p=0.2483`, cumulative trials after iteration = 116).
- WF windows: PASS (`21/24` positive).
- OOS: PASS (`+124.99%`).
- Latest 63d FWD stress: PASS (`+18.53%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`+0.0000139`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Volatility reversal on QQQ has usable defensive behavior, but the edge is not
  statistically distinctive under MCPT; the observed ordering is common under
  permuted paths `[testing_tuning, p.318-320]`.
- Low PBO with failed MCPT/DSR suggests stable but weak exposure timing, not an
  exploitable strategy after trial deflation `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.
- Intraday Track B remains blocked by absent physical 1h/15m files; manifest-only
  evidence should continue to be ignored.

## Recommended Next Step

Do not tune `k` or range lookback locally. Either restore/audit true 1h/15m data
for short-swing tests, or pivot to a daily swing mechanism with a different
economic premise than volatility reversal/trailing stops.
