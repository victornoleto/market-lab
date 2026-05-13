# SUMMARY — 004-vol-targeted-lrs

## Verdict

`fail`. The volatility-targeted LRS overlay reduced drawdown versus full UPRO LRS
and the 25% target beat SPY economically, but it failed hard validation gates:
walk-forward, final 3y forward stress, and 99.9% bootstrap. Capital remains 100%
Plano C; this has no deployment implication.

## What Was Tested

Two pre-fixed volatility-targeted variants over the common `SPYSIM`/`UPROSIM`/
`CASHX` long-history window, 1986-01-03 to 2026-04-17:

- `vt_lrs_upro_target20`: `SPYSIM > SMA200` then UPRO exposure scaled to 20%
  annualized vol, else `CASHX`.
- `vt_lrs_upro_target25`: same rule with 25% annualized vol target.

The regime signal and 63-day realized-vol estimate are lagged one trading day.
The family is citable as Carver-style volatility standardisation applied to
Gayed LRS `[systematic_trading, p.40]`, `[systematic_trading, p.137-148]`,
`[volatility_trading, p.14]`, `[leverage_for_the_long_run, p.13]`.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.47%.
- MDD: -55.14%.
- Sharpe: 0.682.
- Terminal equity: 79.86x.

Best config: `vt_lrs_upro_target25`.

- CAGR: 12.41%.
- MDD: -36.44%.
- Sharpe: 0.638.
- Terminal equity: 111.19x, or 1.39x SPY.
- Rolling CAGR win rates vs SPY: 3y 60.47%, 5y 62.51%, 10y 76.77%.

The lower 20% target did not beat SPY: CAGR 11.07%, terminal 0.86x SPY.

## Gates

- Economic gate: pass for `vt_lrs_upro_target25`.
- PBO: pass, `0.000 < 0.5`, but explicitly unstable with only two configs
  `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.00540` with cumulative `n_trials=8`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: fail, 5/8 windows beat SPY; required 6/8
  `[testing_tuning, ch.12]`.
- OOS final 25%: pass, candidate CAGR 16.67% vs SPY 15.32%.
- FWD final 3y: fail, candidate CAGR 20.28% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-7.40%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- Vol targeting directly fixed much of the drawdown problem: MDD improved from the
  prior full-UPRO LRS -71.20% to -36.44%.
- The price of that risk control was weaker edge: only +0.94pp CAGR over SPY, not
  enough to survive bootstrap or every walk-forward block.
- This is a useful control result, but not a winner. More local target-vol tuning
  would be a threshold grid around a failed family and should be avoided without a
  distinct mechanism.
- Conservative ambiguity handling: public docs were not updated because
  `docs/CURRENT_STATE.md` and `docs/PROJECT_HISTORY.md` already have pre-existing
  unstaged modifications not made in this iteration. The required v2 artifacts
  plus `MEMORY.md` were updated instead.

## Next Step

Try a distinct long-history mechanism rather than another LRS sizing tweak. A
reasonable next family is a non-LRS trend-following control such as one or two
pre-fixed Carver EWMAC variants on SPY/UPRO with cash risk-off, keeping
`n_trials <= 2` and enforcing the same gates.
