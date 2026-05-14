# SUMMARY — 022 KAMA efficiency regime

## Verdict

`fail`. The best config reduced drawdown versus QQQ buy-and-hold, but lost Sharpe
and failed IS MCPT, WF MCPT and DSR. No winner claim.

## What Was Tested

Four pre-registered KAMA/Efficiency Ratio regime rules on `SPY` and `QQQ`, using
`SHV` as the defensive sleeve and one-bar-lagged signals. The family used
Kaufman's ER/KAMA adaptive smoothing idea rather than retuning prior SMA, EWMAC,
Ehlers, VIX, carry, calendar or intraday component rules `[trading_systems_methods,
p.10-11]`, `[trading_systems_methods, p.780-782]`, `[testing_tuning,
p.327-335]`.

## Benchmark Comparison

- Best `qqq_kama_er20`: CAGR 8.63%, Sharpe 0.889, MDD -16.57%.
- Same-window `QQQ` buy-and-hold: CAGR 19.25%, Sharpe 0.958, MDD -35.12%.
- The ER filter materially reduced drawdown but gave up too much return and did
  not beat the pre-registered Sharpe benchmark.

## Gates

- Data freshness: pass, common data ended 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.889 < 0.958.
- IS MCPT: fail, `p=0.110` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.520` with 100 reps and 12 WF windows.
- PBO: pass, `0.257` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.1264` using cumulative `n_trials=76` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 9/12 positive versus required 6.
- OOS: pass, final 20% return +67.27%.
- FWD stress: pass, latest 63 observations +18.53%.
- Bootstrap: pass, 99.9% mean daily CI low `0.0000433`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

KAMA/ER acted mainly as a drawdown reducer, not an efficient timing edge. The
positive PBO/WF/OOS diagnostics are insufficient because the family fails the
economic benchmark and the MCPT/DSR hard controls.

## Next Step

Do not tune KAMA lengths or ER thresholds locally. If continuing, use a genuinely
different information source, preferably one whose timing decisions are stronger
under MCPT rather than another price-only smoother `[testing_tuning, p.327-335]`.

## Ambiguity Note

The worktree already had unrelated modified/untracked files before this
iteration, including public docs, Tiingo files/scripts and the broader untracked
study scaffold. I did not revert them and only wrote iteration artifacts plus the
required study/public state updates.
