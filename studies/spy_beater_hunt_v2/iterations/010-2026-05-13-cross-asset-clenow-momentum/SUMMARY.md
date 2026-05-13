# SUMMARY — 010-cross-asset-clenow-momentum

## Verdict

`fail`. The pre-fixed Clenow-style cross-asset momentum family did not beat SPY
on long-term CAGR or terminal wealth and failed WF, OOS, final-3y FWD and
bootstrap hard gates. No winner; capital remains 100% Plano C.

## What Was Tested

Two pre-fixed weekly Wednesday configs over `SPYSIM`, `ZROZSIM`, `GLDSIM`,
`KMLMSIM`, and `CASHX`, with test window 1988-10-17 to 2026-04-17:

- `clenow_xasset_top1_cash`: hold 100% of the top-ranked asset by 90-day adjusted
  slope when `SPYSIM > SMA200`, else `CASHX`.
- `clenow_xasset_top2_invvol_cash`: hold the top 2 ranked assets weighted by
  inverse 63-day realized volatility when `SPYSIM > SMA200`, else `CASHX`.

The ranking follows Clenow's adjusted slope `[stocks_on_the_move, p.75-77]`, the
regime filter follows his long-term index filter `[stocks_on_the_move, p.66-67]`,
and the inverse-vol variant follows the risk-allocation principle behind ATR risk
parity `[stocks_on_the_move, p.83-89]`. No parameter tuning was performed.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.30%.
- MDD: 55.14% absolute drawdown.
- Sharpe: 0.684.
- Terminal equity: 55.43x.

Best config: `clenow_xasset_top1_cash`.

- CAGR: 11.07%.
- MDD: 30.29% absolute drawdown.
- Sharpe: 0.768.
- Sortino: 1.087.
- Terminal equity: 51.09x, or 0.92x SPY.
- Rolling CAGR win rates vs SPY: 3y 40.12%, 5y 47.63%, 10y 59.54%.

The inverse-vol top-2 variant had better Sharpe/Sortino and lower drawdown, but
lower CAGR: 9.53%, terminal 0.55x SPY.

## Gates

- Economic gate: fail, best CAGR and terminal equity did not beat SPY.
- PBO: pass, `0.167 < 0.5`, but unstable with only two pre-registered configs
  `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.00281` with cumulative `n_trials=20`; required `<0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: fail, 4/8 windows beat SPY; required 6/8 `[testing_tuning,
  ch.12]`.
- OOS final 25%: fail, candidate CAGR 6.10% vs SPY 15.27%.
- FWD final 3y: fail, candidate CAGR 1.91% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-11.30%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- Cross-asset Clenow-style momentum improved risk-adjusted metrics and reduced
  drawdown, but did not preserve enough equity upside to beat SPY over the full
  long-history panel.
- Recent-window weakness is severe: final 3y underperformance is a hard kill for
  a standalone claim.
- Do not continue by tuning `top_k`, lookback, rebalance weekday, or the same
  asset set locally; that would be local optimization after economic and hard-gate
  failure.
- Conservative ambiguity handling: pre-existing unrelated changes remain untouched;
  this iteration updated only required v2 artifacts plus `MEMORY.md`.

## Next Step

Run iteration 011 with a distinct citable mechanism. Prefer a mechanism outside
static allocation, LRS/SMA trend, SPY/QQQ relative momentum, KAMA/ER, simple
calendar seasonality, and this cross-asset adjusted-slope momentum/risk-parity
family.
