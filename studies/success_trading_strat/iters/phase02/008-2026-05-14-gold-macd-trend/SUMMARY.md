# SUMMARY — 008-2026-05-14-gold-macd-trend

## Verdict

`fail`. The best daily gold MACD trend config had positive CAGR and reduced
drawdown versus XAUUSD buy-and-hold, but it underperformed same-asset Sharpe and
failed MCPT, DSR, walk-forward sufficiency, latest 63d FWD stress and bootstrap.
No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily `GLD`/`xauusd` MACD 12/26/9 trend configs.
- Rule: long risk asset when lagged `MACD > signal`, optionally requiring close >
  `SMA200`; otherwise hold `SHV`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `GLD`, `xauusd`, `SHV` and `SPY` files. `1hour`
  exists but has 0 parquet files; `15min` is absent. No intraday bars were
  synthesized.

## Benchmark Comparison

Best config: `xau_macd_12_26_9`.

- Strategy: CAGR 12.10%, Sharpe 0.875, MDD -17.83%.
- `xauusd` buy-and-hold: CAGR 16.66%, Sharpe 0.948, MDD -20.36%.
- Same-asset total return: strategy +114.77% vs `xauusd` buy-and-hold +180.53%.

The rule improved drawdown only modestly and gave up too much trend participation.

## Gates

- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.365`, 200 reps; strict gate `<=0.01`).
- WF MCPT: FAIL (`p=0.310`, 100 reps).
- PBO: PASS (`0.099`).
- DSR: FAIL (`p=0.6581`, cumulative trials after iteration = 132).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+17.75%`).
- Latest 63d FWD stress: FAIL (`-6.49%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0001641`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- The MACD gold trend family was not robust enough despite clean PBO; DSR and
  MCPT reject the observed Sharpe as non-promotional `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.222-223]`.
- `xauusd` history starts only in 2020, so WF has too few 1y windows for strict
  promotion even when all are positive.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune MACD periods or add local filters. Continue Phase 2 with a different
daily swing mechanism, or restore true 1h/15m data before testing short-swing
hybrids.
