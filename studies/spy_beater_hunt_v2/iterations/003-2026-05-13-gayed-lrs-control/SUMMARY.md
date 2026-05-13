# SUMMARY — 003-gayed-lrs-control

## Verdict

`fail`. The canonical Gayed LRS control was economically strong, but no winner is
allowed because the 99.9% bootstrap excess-return CI failed. Capital remains 100%
Plano C; this has no deployment implication.

## What Was Tested

Two pre-fixed LRS configs over the common `SPYSIM`/`SSOSIM`/`UPROSIM`/`CASHX`
long-history window, 1986-01-03 to 2026-04-17:

- `gayed_lrs_sma200_sso_cash`: `SPYSIM > SMA200` then `SSOSIM`, else `CASHX`.
- `gayed_lrs_sma200_upro_cash`: `SPYSIM > SMA200` then `UPROSIM`, else `CASHX`.

The signal is lagged one trading day. The 200-day filter and 2x/3x variants are
canonical Gayed controls, not tuned locally `[leverage_for_the_long_run, p.13]`,
`[leverage_for_the_long_run, p.16-17]`, `[leverage_for_the_long_run, p.21]`.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.47%.
- MDD: -55.14%.
- Sharpe: 0.682.
- Terminal equity: 79.86x.

Best config: `gayed_lrs_sma200_upro_cash`.

- CAGR: 16.40%.
- MDD: -71.20%.
- Sharpe: 0.605.
- Terminal equity: 452.74x, or 5.67x SPY.
- Rolling CAGR win rates vs SPY: 3y 69.46%, 5y 69.94%, 10y 81.09%.

## Gates

- Economic gate: pass. Best config beat SPY CAGR and terminal equity.
- PBO: pass, `0.000 < 0.5`, but flagged as statistically unstable because only
  two configs were pre-registered `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.00608` with cumulative `n_trials=6`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: pass, 7/8 windows beat SPY `[testing_tuning, ch.12]`.
- OOS final 25%: pass, candidate CAGR 26.57% vs SPY 15.32%.
- FWD final 3y: pass, candidate CAGR 38.46% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-2.70%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- Canonical SPY LRS is a useful long-history benchmark: it beat SPY materially in
  CAGR/terminal wealth, unlike the static diversifier control.
- The result is not robust enough for winner status because the 99.9% bootstrap
  lower bound remains negative; hard gates are zero-bypass.
- The high MDD of the 3x variant means any future LRS branch should treat leverage
  as risk budget, not merely CAGR amplifier.
- Conservative ambiguity handling: I did not update public docs because
  `docs/CURRENT_STATE.md` and `docs/PROJECT_HISTORY.md` already have pre-existing
  unstaged modifications not made in this iteration. The required v2 artifacts
  plus `MEMORY.md` were updated instead.

## Next Step

Try a distinct mechanism that preserves the LRS economic strength but targets the
bootstrap failure and drawdown: one pre-fixed volatility-targeted or defensive
overlay, with `n_trials <= 2`, not a local SMA/leverage grid.
