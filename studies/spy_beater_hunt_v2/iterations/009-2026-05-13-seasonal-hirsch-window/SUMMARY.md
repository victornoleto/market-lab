# SUMMARY — 009-seasonal-hirsch-window

## Verdict

`fail`. The Hirsch November-April seasonal window beat SPY economically and
passed DSR, PBO, WF and cross-lib, but failed OOS, final-3y FWD and bootstrap
99.9% excess-return gates. No winner; capital remains 100% Plano C.

## What Was Tested

Two pre-fixed configs over `SPYSIM`, `SSOSIM`, `UPROSIM`, and `CASHX`,
1986-01-03 to 2026-04-17:

- `hirsch_nov_apr_sso_cash`: hold `SSOSIM` during November-April, else `CASHX`.
- `hirsch_nov_apr_upro_cash`: hold `UPROSIM` during November-April, else `CASHX`.

The seasonal mechanism follows Hirsch/Kaufman: buy the first trading day of
November and sell the last trading day of April `[trading_systems_methods,
p.480]`. No month/date tuning was performed.

## Comparison With SPY

Same-window SPY benchmark:

- CAGR: 11.47%.
- MDD: 55.14% absolute drawdown.
- Sharpe: 0.682.
- Terminal equity: 79.86x.

Best config: `hirsch_nov_apr_upro_cash`.

- CAGR: 15.50%.
- MDD: 81.90% absolute drawdown.
- Sharpe: 0.569.
- Terminal equity: 337.22x, or 4.22x SPY.
- Rolling CAGR win rates vs SPY: 3y 63.80%, 5y 70.23%, 10y 84.00%.

The 2x variant had lower CAGR but materially lower drawdown: CAGR 13.43%, MDD
63.76%, terminal 2.03x SPY.

## Gates

- Economic gate: pass, best CAGR and terminal equity beat SPY.
- PBO: pass, `0.000 < 0.5`, but unstable with only two pre-registered configs
  `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.0408` with cumulative `n_trials=18`; required `<0.05`
  `[advances_fin_ml, p.222-223]`.
- Walk-forward: pass, 6/8 windows beat SPY; required 6/8 `[testing_tuning,
  ch.12]`.
- OOS final 25%: fail, candidate CAGR 12.92% vs SPY 15.32%.
- FWD final 3y: fail, candidate CAGR 15.61% vs SPY 21.45%.
- Bootstrap 99.9% daily excess-return CI: fail, low `-5.71%` annualized.
- Cross-lib parity: pass. Vectorized and explicit loop CAGR matched exactly.

## Lessons

- The November-April seasonal anomaly is economically interesting on the full
  long-history panel, especially in terminal wealth, but it is not robust enough
  for promotion under recent-window and bootstrap hard gates.
- The recent 2021-2026 and final-3y underperformance is a kill rule for any claim
  that this standalone seasonal timing rule currently beats SPY reliably.
- Do not continue by tuning month boundaries or switching entry/exit days; that
  would be local seasonal optimization after failed OOS/FWD/bootstrap.
- Conservative ambiguity handling: public docs had pre-existing unrelated changes,
  so this iteration updated only required v2 artifacts plus `MEMORY.md`.

## Next Step

Run iteration 010 with a distinct, citable mechanism. Prefer something outside
static allocation, LRS/SMA trend, SPY/QQQ relative momentum, KAMA/ER, and simple
calendar month-boundary seasonal timing.
