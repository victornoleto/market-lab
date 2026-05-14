# SUMMARY — 005-2026-05-14-equity-gap-continuation

## Verdict

`fail`. The best daily SPY/QQQ gap-recovery config reduced drawdown versus
buy-and-hold, but it failed same-asset Sharpe, IS MCPT, DSR and bootstrap. No
deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily OHLC gap-recovery configs on `SPY` and `QQQ`.
- Rule: if the daily open gaps down by at least 0.5% or 1.0% versus previous
  close and closes above the open, hold the same asset on the next close-to-close
  bar; otherwise hold `SHV`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`, `QQQ` and `SHV` files through
  2026-05-13. `1hour/prices` exists but has 0 parquet files; `15min/prices` is
  absent. No intraday bars were synthesized.

## Benchmark Comparison

Best config: `spy_gap10_recover`.

- Strategy: CAGR 1.84%, Sharpe 0.370, MDD -12.70%.
- `SPY` buy-and-hold: CAGR 10.83%, Sharpe 0.646, MDD -55.20%.
- Same-asset total return: strategy +83.09% vs `SPY` buy-and-hold +2,950.48%.

The rule is defensive but gives up too much return and risk-adjusted performance.

## Gates

- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.035`, 200 reps; strict gate `<=0.01`).
- WF MCPT: PASS (`p=0.010`, 100 reps).
- PBO: PASS (`0.171`).
- DSR: FAIL (`p=0.6884`, cumulative trials after iteration = 120).
- WF windows: PASS (`21/30` positive).
- OOS: PASS (`+32.66%`).
- Latest 63d FWD stress: PASS (`+1.13%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0000490`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Down-gap recovery is a drawdown reducer, not a return engine, over the SPY/QQQ
  daily sample.
- The close-path MCPT proxy was conservative because close-only permutations do
  not preserve OHLC gap structure; even a pass would need stricter OHLC MCPT
  before promotion `[testing_tuning, p.318-320]`.
- Low PBO plus high DSR p-value points to a stable but economically weak timing
  rule after trial deflation `[advances_fin_ml, p.208-211]`,
  `[advances_fin_ml, p.222-223]`.

## Recommended Next Step

Do not tune gap thresholds locally. Continue Phase 2 with a different daily swing
mechanism or restore true 1h/15m data before testing short-swing Track B.
