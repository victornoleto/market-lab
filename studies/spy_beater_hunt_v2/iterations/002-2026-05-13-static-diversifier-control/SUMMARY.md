# SUMMARY — 002-static-diversifier-control

## Verdict

`fail`. Four pre-fixed static diversifier stacks were tested. No winner was
declared and no deployment implication exists; capital remains 100% Plano C.

## What Was Tested

Daily constant-weight portfolios over the common `SPYSIM`/`ZROZSIM`/`GLDSIM`/
`KMLMSIM` window, 1988-01-04 to 2026-04-17. The family was a Carver-style
asset-allocation control with constant long exposure, not a technical signal or
local grid `[systematic_trading, p.72-85]`, `[systematic_trading, p.116]`.

Configs tested: `static_60_20_10_10`, `static_50_25_15_10`,
`static_40_30_20_10`, and `static_25_25_25_25`. Trial count: `n_trials=4`,
cumulative trials now `4` `[advances_fin_ml, p.222-223]`.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.36%.
- MDD: -55.14%.
- Sharpe: 0.691.
- Sortino: 0.984.
- Terminal equity: 63.56x.

Best config: `static_60_20_10_10`.

- CAGR: 11.01%, below SPY by ~0.35pp.
- MDD: -26.16%, much lower than SPY.
- Sharpe: 0.977; Sortino: 1.427.
- Terminal equity: 55.50x, or 0.873x SPY.
- Rolling CAGR win rates vs SPY: 3y 40.67%, 5y 42.45%, 10y 55.84%.

## Gates

- Economic gate: fail. Best config did not beat SPY CAGR or terminal equity.
- PBO: fail, `0.6071 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=3.12e-07` with `n_trials=4` `[advances_fin_ml, p.222-223]`.
- Walk-forward: fail, 3/8 windows beat SPY; required 6/8 `[testing_tuning, ch.12]`.
- OOS final 25%: fail, candidate CAGR 10.70% vs SPY 15.40%.
- FWD final 3y: fail, candidate CAGR 14.54% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-6.30%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- Simple static diversification materially reduced drawdown and improved
  risk-adjusted metrics, but did not beat SPY's long-run compound return.
- The weak recent/OOS relative performance makes this unsuitable as the first
  v2 lead despite a strong DSR value.
- PBO over only four pre-fixed configs is still harsh but directionally useful:
  the IS-best does not translate consistently enough OOS.
- Conservative ambiguity handling: I did not update public docs because
  `docs/CURRENT_STATE.md` and `docs/PROJECT_HISTORY.md` already have
  pre-existing unstaged modifications not made in this iteration. The required
  v2 artifacts plus `MEMORY.md` were updated instead.

## Next Step

Try one distinct, citable mechanism rather than another static allocation panel:
a single canonical trend/risk-on rule or cross-asset trend control with no local
parameter grid, strict `n_trials <= 2`, and long-history SPY comparison.
