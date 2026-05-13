# SUMMARY — 008-kaufman-kama-er-trend

## Verdict

`fail`. The Kaufman KAMA/ER adaptive SPY trend gate badly underperformed SPY and
failed the economic, DSR, walk-forward, OOS, FWD and bootstrap gates. No winner;
capital remains 100% Plano C.

## What Was Tested

Two pre-fixed configs over `SPYSIM`, `SSOSIM`, `UPROSIM`, and `CASHX`,
1986-01-03 to 2026-04-17:

- `kama10_2_30_sso_cash`: hold `SSOSIM` when `SPYSIM > KAMA(ER=10, fast=2,
  slow=30)`, else `CASHX`.
- `kama10_2_30_upro_cash`: same gate, holding `UPROSIM` when on.

The ER/KAMA mechanism follows Kaufman `[trading_systems_methods, p.10-11]`,
`[trading_systems_methods, p.780-781]`; all signals were lagged one bar to avoid
same-close look-ahead `[advances_fin_ml, p.31-34]`.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.47%.
- MDD: 55.14% absolute drawdown.
- Sharpe: 0.682.
- Terminal equity: 79.86x.

Best config: `kama10_2_30_sso_cash`.

- CAGR: 2.96%.
- MDD: 85.76% absolute drawdown.
- Sharpe: 0.243.
- Terminal equity: 3.24x, or 0.04x SPY.
- Rolling CAGR win rates vs SPY: 3y 12.62%, 5y 10.91%, 10y 0.00%.

The 3x variant was worse: CAGR 0.44%, MDD 96.51%, terminal 0.01x SPY.

## Gates

- Economic gate: fail, best CAGR and terminal equity both trail SPY.
- PBO: pass, `0.000 < 0.5`, but unstable with only two pre-registered configs
  `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.6019` with cumulative `n_trials=16`; required `<0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: fail, 1/8 windows beat SPY; required 6/8 `[testing_tuning, ch.12]`.
- OOS final 25%: fail, candidate CAGR 12.85% vs SPY 15.32%.
- FWD final 3y: fail, candidate CAGR 18.51% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-15.96%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- KAMA/ER as a standalone SPY adaptive trend gate is not competitive on the
  long-history panel; it misses too much equity upside while preserving severe
  leveraged drawdown.
- This should be treated as a dead-end family, not a candidate for local KAMA
  threshold/parameter tuning.
- Conservative ambiguity handling: public docs were not updated because they had
  pre-existing unstaged changes not made in this iteration. Required v2 artifacts
  plus `MEMORY.md` were updated instead.

## Next Step

Run iteration 009 with a distinct, citable mechanism. Avoid local KAMA/ER
parameter tuning, fixed SMA/LRS variants, EWMAC speed tuning, and SPY/QQQ
relative-momentum variants already tested.
