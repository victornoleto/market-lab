# SUMMARY — 016-2026-05-14-trix-trend-continuation

## Verdict

`fail`. The best TRIX trend-continuation config (`xau_trix18_zero`) did not beat
XAU buy-and-hold on CAGR or Sharpe and failed IS MCPT, WF MCPT, PBO, DSR, WF
sufficiency, latest 63d FWD stress and bootstrap. No deploy implication; capital
remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily TRIX configs on `SPY`, `QQQ`, `GLD` and `xauusd`.
- Rule: hold the asset when lagged TRIX(18) on log price is above zero; otherwise
  hold `SHV`.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed required daily files exist. `1hour/prices` still has 0
  parquet files and `15min/prices` is absent, so no intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_trix18_zero`.

- Strategy: CAGR 10.99%, Sharpe 0.831, MDD -19.44%.
- `xauusd` buy-and-hold: CAGR 14.30%, Sharpe 0.915, MDD -20.36%.
- `SPY` opportunity benchmark: CAGR 12.26%, Sharpe 0.834.
- Same-asset total return: strategy +97.97% vs `xauusd` buy-and-hold +139.94%.

The pre-registered Phase 2 kill rule fired because CAGR did not beat same-asset
buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: FAIL.
- IS MCPT: FAIL (`p=0.175`, 200 reps).
- WF MCPT: FAIL (`p=0.070`, 100 reps).
- PBO: FAIL (`0.556`).
- DSR: FAIL (`p=0.7106`, cumulative trials after iteration = 164).
- WF windows: FAIL (`3/3` positive, fewer than 8 windows).
- OOS: PASS (`+34.57%`).
- Latest 63d FWD stress: FAIL (`-17.15%`).
- Bootstrap 99.9% mean-daily CI low: FAIL (`-0.0002489`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- TRIX reduced some drawdown versus XAU buy-and-hold but still gave up too much
  compound return, violating the Phase 2 economic floor `[systematic_trading, p.40]`.
- PBO/DSR and MCPT do not support the smoothed-momentum edge
  `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune TRIX length or threshold locally. Continue Phase 2 with a different
daily swing mechanism, preferably one not based on generic trend smoothing, or
restore/audit true 1h/15m data before testing short-swing hybrids.
