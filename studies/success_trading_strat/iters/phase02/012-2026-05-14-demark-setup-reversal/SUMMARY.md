# SUMMARY — 012-2026-05-14-demark-setup-reversal

## Verdict

`fail`. The best DeMark setup reversal config (`xau_demark9_sma200_hold13`)
improved Sharpe and drawdown versus XAU buy-and-hold, but failed the Phase 2 CAGR
floor, IS MCPT, WF MCPT, PBO, DSR and WF window sufficiency. No deploy
implication; capital remains 100% Plano C.

## What Was Tested

- 4 pre-registered daily DeMark-style 9-count exhaustion configs on `SPY`, `QQQ`,
  `GLD` and `xauusd`.
- Rule: enter long after 9 consecutive closes below the close 4 bars earlier,
  only when price is above `SMA200`; exit on recovery above `close[t-4]`, trend
  break or 13-bar max hold.
- Signals were shifted one completed daily bar before returns were earned.
- Physical audit confirmed daily files exist. `1hour/prices` still has 0 parquet
  files and `15min/prices` is absent, so no intraday bars were synthesized.

## Benchmark Comparison

Best config: `xau_demark9_sma200_hold13`.

- Strategy: CAGR 3.38%, Sharpe 1.512, MDD -2.33%.
- `xauusd` buy-and-hold: CAGR 17.30%, Sharpe 1.061, MDD -20.36%.
- Same-asset total return: strategy +21.84% vs `xauusd` buy-and-hold +157.92%.

The rule de-risked aggressively, but the pre-registered kill rule fired because
CAGR did not beat same-asset buy-and-hold.

## Gates

- Economic CAGR vs same asset: FAIL.
- Economic Sharpe vs same asset: PASS.
- IS MCPT: FAIL (`p=0.460`, 200 reps).
- WF MCPT: FAIL (`p=0.340`, 100 reps).
- PBO: FAIL (`0.730`).
- DSR: FAIL (`p=0.1483`, cumulative trials after iteration = 148).
- WF windows: FAIL (`2/2` positive, fewer than 8 windows).
- OOS: PASS (`+5.09%`).
- Latest 63d FWD stress: PASS (`+2.33%`).
- Bootstrap 99.9% mean-daily CI low: PASS (`+0.0000280`).
- Cross-lib/vector parity: PASS (`0.00pp` CAGR delta).

## Lessons

- DeMark-style exhaustion setups are primarily a drawdown-reduction mechanism in
  this implementation; they do not preserve enough compounded return for Phase 2's
  non-hedge mandate.
- The high PBO and weak MCPT results indicate the best config is not statistically
  robust despite attractive raw Sharpe `[advances_fin_ml, p.208-211]`,
  `[testing_tuning, p.318-320]`.
- Intraday Track B remains blocked by missing physical 1h/15m cache files.

## Recommended Next Step

Do not tune DeMark setup counts, 4-bar comparisons or hold lengths locally.
Continue Phase 2 with a different daily swing mechanism, or restore true 1h/15m
data before testing short-swing hybrids.
