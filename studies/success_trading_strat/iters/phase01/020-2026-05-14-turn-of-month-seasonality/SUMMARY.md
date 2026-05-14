# SUMMARY — 020 turn-of-month seasonality

## Verdict

`fail`. The calendar mechanism loaded and ran, but the best config failed the
same-asset Sharpe benchmark, IS MCPT, WF MCPT, PBO and DSR. No winner claim.

## What Was Tested

Four pre-registered turn-of-month configs held `SPY` or `QQQ` only around the
last 1-2 and first 4 trading days of each month, otherwise holding `SHV`. Signals
were shifted one bar for conservative execution. The mechanism was a new calendar
seasonality pivot, not a local retune of failed VIX/carry/credit/technical
families `[trading_systems_methods, p.479-481]`, `[trading_systems_methods,
p.422]`, `[testing_tuning, p.327-335]`.

## Benchmark Comparison

- Best `spy_tom_l1_f4`: CAGR 6.11%, Sharpe 0.744, MDD -16.65%.
- Same-window `SPY` buy-and-hold benchmark: CAGR 14.20%, Sharpe 0.861, MDD -33.70%.
- The strategy reduced drawdown but sacrificed too much return and Sharpe, so it
  failed the economic benchmark gate.

## Gates

- Data freshness: pass, common data ended 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.744 < 0.861.
- IS MCPT: fail, `p=0.205` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.260` with 100 reps and 12 WF windows.
- PBO: fail, `0.500` is not `< 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.2735` using cumulative `n_trials=68` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 9/12 positive versus required 6.
- OOS: pass, final 20% return +17.77%.
- FWD stress: pass, latest 63 observations +4.38%.
- Bootstrap: pass, 99.9% mean daily CI low `0.000000773`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

The turn-of-month effect is not strong enough in this conservative daily ETF form.
It behaves like a drawdown-reducing partial-exposure rule, not an alpha source:
permutation tests and DSR show the Sharpe improvement is not statistically robust.

## Next Step

Do not tune calendar offsets, add holidays or add leverage locally. Use a genuinely
new mechanism with a clean external rationale, or pause if no non-redundant data
source is available `[testing_tuning, p.327-335]`.
