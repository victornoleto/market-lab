# SUMMARY — 024 accumulation/distribution volume

## Verdict

`fail`. The close-location volume family was weaker than OBV and failed multiple
hard gates. No winner claim.

## What Was Tested

Four pre-registered Accumulation/Distribution and Intraday Intensity rules on
`SPY` and `QQQ`, using `SHV` as the defensive sleeve and one-bar-lagged signals.
This was a different volume source from OBV because it weights volume by the
close's location inside the daily range `[trading_systems_methods, p.540-541]`.

## Benchmark Comparison

- Best `qqq_ad21`: CAGR 9.21%, Sharpe 0.700, MDD -39.94%.
- Same-window `QQQ` buy-and-hold: CAGR 19.25%, Sharpe 0.958, MDD -35.12%.
- The strategy lost to QQQ on CAGR, Sharpe and drawdown.

## Gates

- Data freshness: pass, common data ended 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.700 < 0.958.
- IS MCPT: fail, `p=0.530` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.830` with 100 reps and 12 WF windows.
- PBO: fail, `0.900` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.3641` using cumulative `n_trials=84` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 11/12 positive versus required 6.
- OOS: pass, final 20% return +54.58%.
- FWD stress: pass, latest 63 observations +4.52%.
- Bootstrap: fail, 99.9% mean daily CI low `-0.0000976`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

Close-location volume pressure did not rescue the volume-confirmation mechanism.
The high PBO and MCPT p-values suggest the family is selection/noise-sensitive,
not a robust edge.

## Next Step

Do not tune AD/II lookbacks, thresholds or add price filters locally. Pivot to a
new mechanism or pause if no genuinely different information source is available
`[testing_tuning, p.327-335]`.

## Ambiguity Note

The worktree already had unrelated modified/untracked files before this
iteration, including public docs, Tiingo files/scripts and the broader untracked
study scaffold. I did not revert them and only wrote iteration artifacts plus the
required study/public state updates.
