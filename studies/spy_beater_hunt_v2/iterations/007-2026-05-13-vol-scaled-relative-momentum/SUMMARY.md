# SUMMARY — 007-vol-scaled-relative-momentum

## Verdict

`fail`. The volatility-scaled relative-momentum variant beats SPY economically and
improves drawdown versus the unscaled 3x relative-momentum control, but it fails
the final-3y FWD stress and bootstrap 99.9% hard gate. No winner; capital remains
100% Plano C.

## What Was Tested

Two pre-fixed configs over `SPYSIM`, `QQQSIM`, `UPROSIM`, `TQQQSIM`, and `CASHX`,
1986-01-03 to 2026-04-17:

- `relmom90_3x_vt20_cash`: 90-day adjusted-slope rank between `SPYSIM` and
  `QQQSIM`; if `SPYSIM > SMA200`, hold selected 3x LETF scaled to 20% annualized
  vol using lagged 63-day realized volatility; otherwise `CASHX`.
- `relmom90_3x_vt25_cash`: same, scaled to 25% annualized vol.

Adjusted-slope rank follows Clenow `[stocks_on_the_move, p.75-77, p.82]`; the
SMA200 broad regime filter follows Clenow `[stocks_on_the_move, p.66-67]`; vol
scaling follows Carver/Sinclair `[systematic_trading, p.40]`,
`[systematic_trading, p.137-148]`, `[volatility_trading, p.14]`; all signals and
sizing are lagged one bar `[advances_fin_ml, p.31-34]`.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.47%.
- MDD: 55.14% absolute drawdown.
- Sharpe: 0.682.
- Terminal equity: 79.86x.

Best config: `relmom90_3x_vt25_cash`.

- CAGR: 14.69%.
- MDD: 41.75% absolute drawdown.
- Sharpe: 0.718.
- Terminal equity: 249.30x, or 3.12x SPY.
- Rolling CAGR win rates vs SPY: 3y 70.16%, 5y 76.82%, 10y 89.04%.

The 20% target was more conservative: CAGR 12.84%, MDD 33.80%, Sharpe 0.753,
terminal 1.63x SPY.

## Gates

- Economic gate: pass, best CAGR and terminal equity both beat SPY.
- PBO: pass, `0.000 < 0.5`, but unstable with only two pre-registered configs
  `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.00280` with cumulative `n_trials=14`; required `<0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: pass, 6/8 windows beat SPY; required 6/8 `[testing_tuning, ch.12]`.
- OOS final 25%: pass, candidate CAGR 18.17% vs SPY 15.32%.
- FWD final 3y: fail, candidate CAGR 20.36% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-5.49%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- Volatility scaling reduced drawdown materially versus unscaled 3x relative
  momentum, but the reduction also weakened the recent-window edge.
- The bootstrap failure is worse than iteration 006, so this is not a robust fix
  for the relative-momentum family.
- Conservative ambiguity handling: public docs were not updated because they had
  pre-existing unstaged changes not made in this iteration. Required v2 artifacts
  plus `MEMORY.md` were updated instead.

## Next Step

Do not continue local volatility-target tuning around this family. A better next
hypothesis should be a distinct, citable mechanism, preferably not another local
variant of SPY/QQQ relative momentum or Gayed-style trend exposure.
