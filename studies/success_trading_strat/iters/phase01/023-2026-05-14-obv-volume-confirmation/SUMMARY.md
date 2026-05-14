# SUMMARY — 023 OBV volume confirmation

## Verdict

`fail`. The best config was economically interesting and passed PBO/DSR, but it
failed both MCPT gates. No winner claim.

## What Was Tested

Four pre-registered OBV volume-confirmation rules on `SPY` and `QQQ`, using
`SHV` as the defensive sleeve and one-bar-lagged signals. The family used signed
volume accumulation rather than another price-only smoother `[trading_systems_methods,
p.537]`, `[testing_tuning, p.327-335]`.

## Benchmark Comparison

- Best `qqq_obv21`: CAGR 14.09%, Sharpe 1.136, MDD -21.25%.
- Same-window `QQQ` buy-and-hold: CAGR 19.25%, Sharpe 0.958, MDD -35.12%.
- The OBV rule improved Sharpe and drawdown, but gave up CAGR versus QQQ.

## Gates

- Data freshness: pass, common data ended 2026-05-13.
- Economic Sharpe vs benchmark: pass, 1.136 > 0.958.
- IS MCPT: fail, `p=0.020` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.180` with 100 reps and 12 WF windows.
- PBO: pass, `0.086` `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.0173` using cumulative `n_trials=80` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 9/12 positive versus required 6.
- OOS: pass, final 20% return +84.14%.
- FWD stress: pass, latest 63 observations +22.15%.
- Bootstrap: pass, 99.9% mean daily CI low `0.0001989`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

OBV is a better lead than most recent price-only filters: it cleared economic
Sharpe, PBO and DSR simultaneously. However, MCPT says the observed edge is not
extreme enough versus permuted volume/return ordering, so it cannot be promoted.

## Next Step

Do not tune OBV lookbacks or add local filters. If continuing, either stress OBV
with a genuinely different volume confirmation source, or pivot to another data
source whose timing decisions survive MCPT `[testing_tuning, p.327-335]`.

## Ambiguity Note

The worktree already had unrelated modified/untracked files before this
iteration, including public docs, Tiingo files/scripts and the broader untracked
study scaffold. I did not revert them and only wrote iteration artifacts plus the
required study/public state updates.
