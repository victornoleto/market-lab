# SUMMARY — 010-2026-05-14-gold-keltner-breakout

## Verdict

`fail`. The best daily gold Keltner/ATR breakout config reduced drawdown versus
XAU buy-and-hold, but failed same-asset Sharpe, MCPT, DSR, WF sufficiency, latest
FWD stress and bootstrap. No deploy implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily `GLD`/`xauusd` Keltner/ATR breakout configs.
- Rule: long gold when lagged close is above `EMA + ATR envelope`; hold `SHV` when
  flat after the close falls back to the EMA.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily `GLD`, `xauusd`, `SHV` and `SPY` files exist.
  `1hour/prices` exists but has 0 parquet files; `15min/prices` is absent. No
  intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_kel40_20_exit0`.

- Strategy: CAGR 8.94%, Sharpe 0.782, MDD -18.05%.
- `xauusd` buy-and-hold: CAGR 16.97%, Sharpe 1.059, MDD -20.36%.
- Same-asset total return: strategy +72.31% vs `xauusd` buy-and-hold +170.80%.

The rule lowered drawdown slightly but gave up too much trend participation and
did not beat buy-and-hold Sharpe.

## Gates

- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.500`, 200 reps; strict gate `<=0.01`).
- WF MCPT: FAIL (`p=0.530`, 100 reps).
- PBO: PASS (`0.099`).
- DSR: FAIL (`p=0.7391`, cumulative trials after iteration = 140).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+17.12%`).
- Latest 63d FWD stress: FAIL (`-6.27%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0001726`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- Volatility-normalized gold breakout avoided some drawdown but still lagged the
  already-strong gold buy-and-hold regime.
- PBO was acceptable, but MCPT and DSR rejected the apparent edge, consistent with
  the study's overfit controls `[testing_tuning, p.318-320]`,
  `[advances_fin_ml, p.222-223]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune Keltner EMA/ATR multipliers locally. Continue Phase 2 with a different
daily swing mechanism or restore true 1h/15m data before testing short-swing
hybrids.
