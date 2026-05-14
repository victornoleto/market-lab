# SUMMARY — 018 Ehlers cycle-mode overlay

## Verdict

`fail`. The best Ehlers-style cycle/trend overlay improved QQQ drawdown and
slightly beat same-window QQQ buy-and-hold Sharpe, but failed both MCPT gates.
No winner claim.

## What Was Tested

Four pre-registered configs used Ehlers-inspired smoothing, instantaneous
trendline, Trend Mode override and a fixed-cycle sine/lead-sine phase proxy on
`SPY` or `QQQ`, switching to `SHV` defensively with one-bar lag
`[rocket_science, p.3-4]`, `[rocket_science, p.99-100]`, `[rocket_science,
p.107]`, `[rocket_science, p.114-117]`.

## Benchmark Comparison

- Best `qqq_ehlers_c30_t15`: CAGR 12.51%, Sharpe 1.004, MDD -18.48%.
- Same-asset QQQ buy-and-hold benchmark: CAGR 19.80%, Sharpe 0.980, MDD -35.12%.
- The overlay improved risk-adjusted return and drawdown, but sacrificed too much
  absolute CAGR and was not statistically unusual under permutation.

## Gates

- Data freshness: pass, common cache ended 2026-05-13.
- Economic Sharpe vs benchmark: pass, 1.004 > 0.980.
- IS MCPT: fail, `p=0.075` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.300` with 100 reps and 12 WF windows.
- PBO: pass, `0.314 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.0476` using cumulative `n_trials=60` `[advances_fin_ml,
  p.222-223]`.
- WF windows: pass, 9/12 positive versus required 6.
- OOS: pass, final 20% return +55.01%.
- FWD stress: pass, latest 63 observations +14.21%.
- Bootstrap: pass, 99.9% mean daily CI low `0.00010996`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

The cycle-mode mechanism has better diagnostics than many prior beta filters
because PBO/DSR/WF/OOS/FWD passed, but MCPT rejects it as not rare enough versus
permuted paths. Conservatively, do not tune cycle periods or thresholds locally;
that would only add correlated trials after a failed permutation screen.

## Next Step

Prefer another genuinely different mechanism with clean data, especially carry or
yield-based signals. If no clean source is available, pause rather than continue
local technical-signal variants `[testing_tuning, p.327-335]`.
