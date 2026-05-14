# SUMMARY — 025 market breadth proxy

## Verdict

`fail`. Breadth reduced drawdown versus buy-and-hold but did not beat same-asset
Sharpe and failed IS MCPT, PBO and DSR. No winner claim.

## What Was Tested

Four pre-registered breadth-timing rules using a current large-cap adjusted-close
proxy: hold `SPY` or `QQQ` when at least 55% of proxy constituents are above their
63d or 126d SMA, otherwise hold `SHV`. Signals were lagged one bar. Breadth is an
advance/decline-style information source `[trading_systems_methods, p.548-549]`.

## Benchmark Comparison

- Best `spy_breadth_sma63_gt55`: CAGR 8.82%, Sharpe 0.886, MDD -16.25%.
- Same-window `SPY` buy-and-hold: CAGR 15.08%, Sharpe 0.924, MDD -33.70%.
- The strategy improved drawdown but lost to SPY on CAGR and Sharpe.

## Gates

- Data freshness: pass, common data ended 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.886 < 0.924.
- IS MCPT: fail, `p=0.210` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: pass, `p=0.010` with 100 reps and 9 WF windows.
- PBO: fail, `0.829` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.2173` using cumulative `n_trials=88` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 9/9 positive versus required 6.
- OOS: pass, final 20% return +39.07%.
- FWD stress: pass, latest 63 observations +6.91%.
- Bootstrap: pass, 99.9% mean daily CI low `0.0000400`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.
- Survivorship caveat: fail for promotion, because the breadth proxy uses a
  current constituent list rather than point-in-time membership `[trading_systems_methods, p.941]`.

## Lessons

The breadth mechanism behaved like a defensive drawdown reducer, not an edge. The
high PBO and weak IS MCPT indicate that selecting the best breadth variant is still
noise-sensitive, despite good WF/OOS/FWD diagnostics.

## Next Step

Do not tune breadth thresholds, SMA lengths or constituent lists locally. If the
study continues, pivot to a genuinely different information source or pause
`[testing_tuning, p.327-335]`.

## Ambiguity Note

The worktree already contained unrelated modified/untracked files before this
iteration, including public docs, Tiingo files/scripts and the broader untracked
study scaffold. I did not revert them and only wrote iteration artifacts plus the
required study/public state updates.
