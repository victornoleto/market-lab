# SUMMARY — 006-clenow-relative-momentum

## Verdict

`fail`. The Clenow-style SPY/QQQ relative-momentum control is economically
strong, but it fails the bootstrap 99.9% hard gate. No winner; capital remains
100% Plano C.

## What Was Tested

Two pre-fixed configs over the common `SPYSIM`/`QQQSIM`/LETF/`CASHX` long-history
window, 1986-01-03 to 2026-04-17:

- `clenow_relmom_90d_2x_cash`: rank `SPYSIM` vs `QQQSIM` by 90-day adjusted
  slope; if SPY is above SMA200, hold `SSOSIM` or `QLDSIM`; otherwise `CASHX`.
- `clenow_relmom_90d_3x_cash`: same signal, but hold `UPROSIM` or `TQQQSIM`.

The adjusted-slope rank is annualized log-price slope times `R^2`
`[stocks_on_the_move, p.75-77, p.82]`; the broad regime filter is SPY above
SMA200 `[stocks_on_the_move, p.66-67]`; signals are shifted one trading day to
avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.47%.
- MDD: -55.14%.
- Sharpe: 0.682.
- Terminal equity: 79.86x.

Best config: `clenow_relmom_90d_3x_cash`.

- CAGR: 22.12%.
- MDD: -88.88%.
- Sharpe: 0.660.
- Terminal equity: 3125.23x, or 39.14x SPY.
- Rolling CAGR win rates vs SPY: 3y 77.62%, 5y 79.97%, 10y 96.29%.

The 2x variant was less extreme: CAGR 18.90%, MDD -74.02%, Sharpe 0.705,
terminal 13.36x SPY.

## Gates

- Economic gate: pass, best CAGR and terminal equity both beat SPY.
- PBO: pass, `0.000 < 0.5`, but unstable with only two pre-registered configs
  `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.00616` with cumulative `n_trials=12`; required `<0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: pass, 7/8 windows beat SPY; required 6/8
  `[testing_tuning, ch.12]`.
- OOS final 25%: pass, candidate CAGR 30.81% vs SPY 15.32%.
- FWD final 3y: pass, candidate CAGR 35.83% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-0.20%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- Relative momentum between SPY and QQQ is the first v2 family so far with broad
  economic strength and DSR pass after cumulative trial accounting.
- The result is still not a winner because the bootstrap lower bound crosses zero;
  this cannot be rounded away under the mandate.
- The 3x version wins by terminal wealth but carries catastrophic drawdown; the
  2x version has better Sharpe/Sortino but still large drawdown and was not the
  best CAGR config.
- Conservative ambiguity handling: public docs were not updated because
  `docs/CURRENT_STATE.md` and `docs/PROJECT_HISTORY.md` already had pre-existing
  unstaged modifications not made in this iteration. The required v2 artifacts
  plus `MEMORY.md` were updated instead.

## Next Step

Do not run a local lookback/leverage grid around this result. The only reasonable
follow-up is a distinct robustness check of the same economic mechanism, such as a
pre-fixed drawdown-aware or volatility-scaled relative-momentum variant with at
most two configs and full trial accounting.
