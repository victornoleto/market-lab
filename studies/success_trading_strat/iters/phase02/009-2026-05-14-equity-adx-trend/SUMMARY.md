# SUMMARY — 009-2026-05-14-equity-adx-trend

## Verdict

`fail`. The best daily equity ADX/Directional Movement config reduced drawdown
versus SPY buy-and-hold, but underperformed same-asset Sharpe and failed MCPT,
PBO and DSR. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily `SPY`/`QQQ` ADX trend-continuation configs.
- Rule: long risk asset when lagged `+DI > -DI` and lagged `ADX(14)` is above
  20 or 25; otherwise hold `SHV`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `SPY`, `QQQ` and `SHV` files through
  2026-05-13. `1hour` exists but has 0 parquet files; `15min` is absent. No
  intraday bars were synthesized.

## Benchmark Comparison

Best config: `spy_adx14_t25`.

- Strategy: CAGR 2.86%, Sharpe 0.547, MDD -15.90%.
- `SPY` buy-and-hold: CAGR 10.80%, Sharpe 0.644, MDD -55.20%.
- Same-asset total return: strategy +153.98% vs `SPY` buy-and-hold +2,873.12%.

The rule avoided major drawdowns but gave up too much equity risk premium and did
not beat buy-and-hold Sharpe.

## Gates

- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.680`, 200 reps; strict gate `<=0.01`).
- WF MCPT: FAIL (`p=0.830`, 100 reps).
- PBO: FAIL (`0.635`).
- DSR: FAIL (`p=0.3040`, cumulative trials after iteration = 136).
- WF windows: PASS (`20/30` positive).
- OOS: PASS (`+43.08%`).
- Latest 63d FWD stress: PASS (`+5.11%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`+0.0000121`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- ADX trend-strength gating was too sparse/defensive for daily equity swing: it
  reduced MDD but did not produce enough return or Sharpe versus buy-and-hold.
- PBO and MCPT reject the family despite decent WF/OOS/FWD diagnostics, consistent
  with selection-bias controls `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.208-211]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune ADX thresholds/lengths or add local filters. Continue Phase 2 with a
different daily swing mechanism, or restore true 1h/15m data before testing
short-swing hybrids.
