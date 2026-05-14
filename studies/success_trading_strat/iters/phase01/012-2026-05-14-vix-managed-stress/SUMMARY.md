# SUMMARY — 012 VIX-managed stress

## Verdict

`fail`. The VIX-managed stress variants improved CAGR and Sharpe versus iteration
011, but the family still failed hard gates: IS MCPT, PBO and latest 63d FWD
stress. No winner claim.

## What Was Tested

Four pre-registered variants of the VIX-managed mechanism added equity floors,
a longer 42d VIX averaging window, or a diversified `SPY/QQQ` risk sleeve. The
rule kept one-bar VIX signal lag and inverse exposure to previous VIX
`[paper.bozovic_2024_vix_managed, §methodology]`, `[testing_tuning, p.327-335]`.

## Benchmark Comparison

- Best `qqq_vix15_w21_floor50`: CAGR 16.57%, Sharpe 0.954, MDD -30.99%, average exposure 91.82%.
- QQQ buy-and-hold same window: CAGR 18.94%, Sharpe 0.945, MDD -35.12%.
- SHV: CAGR 1.37%, Sharpe 5.329, MDD -0.45%.
- The best config beat QQQ buy-and-hold on Sharpe and drawdown, but still gave up 2.36pp CAGR.

## Gates

- Economic Sharpe vs same-sleeve buy-and-hold: pass, 0.954130 > 0.944895.
- IS MCPT: fail, `p=0.030` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: pass, `p=0.040` with 100 reps and 12 WF windows.
- PBO: fail, `0.729 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.04773` using cumulative `n_trials=36` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 10/12 positive.
- OOS: pass, final 20% return +111.17%.
- FWD stress: fail, last 63 trading days -0.41%.
- FWD diagnostics: 126d +5.71%, 252d +34.08%.
- Bootstrap: pass, 99.9% mean daily CI low `+0.000156`.
- Cross-lib: pass, NumPy CAGR delta 0.00pp.

## Lessons

Adding a partial equity floor reduced the recent FWD failure from -1.18% to
-0.41% and improved full-period Sharpe, but it also worsened PBO and failed the
selection-bias-adjusted IS MCPT. The mechanism remains interesting but fragile;
the prior 011 result was not rescued by simple robustness variants.

## Next Step

Do not continue local tuning of VIX floors/windows. Either pivot to a different
non-price-only mechanism, or perform a non-optimization VIX post-mortem/report
only; any further VIX strategy variant should require a genuinely new economic
hypothesis rather than another nearby parameter stress `[testing_tuning, p.327-335]`.
