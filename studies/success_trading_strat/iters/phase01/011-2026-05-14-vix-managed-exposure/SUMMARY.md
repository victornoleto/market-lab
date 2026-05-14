# SUMMARY — 011 VIX-managed exposure

## Verdict

`fail`. The VIX-managed exposure pivot was the strongest statistical result in
this study so far, but it failed the hard forward-stress gate. No winner claim.

## What Was Tested

Four pre-registered configs scaled `SPY` or `QQQ` exposure by
`clip(vix_anchor / previous_21d_mean_VIX, 0, 1)` and held `SHV` for the residual
cash sleeve. The signal was shifted by one trading day to avoid same-close
lookahead. This follows the VIX-managed portfolio mechanism
`[paper.bozovic_2024_vix_managed, §methodology]` and the MCPT/WF validation
discipline `[testing_tuning, p.318-320]`.

## Benchmark Comparison

- Best `qqq_vix15_w21`: CAGR 14.10%, Sharpe 0.945, MDD -27.01%, average exposure 83.64%.
- QQQ buy-and-hold same window: CAGR 18.94%, Sharpe 0.945, MDD -35.12%.
- SHV: CAGR 1.37%, Sharpe 5.329, MDD -0.45%.
- The best config marginally beat QQQ buy-and-hold on Sharpe and cut drawdown, but
  gave up 4.83pp CAGR.

## Gates

- Economic Sharpe vs same-asset buy-and-hold: pass, 0.945175 > 0.944895.
- IS MCPT: pass, `p=0.000` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: pass, `p=0.010` with 100 reps and 12 WF windows.
- PBO: pass, `0.400 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.04697` using cumulative `n_trials=32`
  `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 10/12 positive.
- OOS: pass, final 20% return +92.81%.
- FWD stress: fail, last 63 trading days -1.18%.
- Bootstrap: pass, 99.9% mean daily CI low `+0.000138`.
- Cross-lib: pass, NumPy CAGR delta 0.00pp.

## Lessons

VIX-managed exposure is materially more promising than prior price-only pivots:
it passed MCPT, PBO and DSR simultaneously. The conservative hard-gate result is
still `fail` because recent forward stress was negative, and DSR passed only
barely after cumulative trial accounting.

## Next Step

Do not declare a winner. The next iteration may stress this same VIX-managed
family with explicitly pre-registered robustness checks, especially a longer FWD
stress horizon or alternative asset sleeves, but any new variants must consume
new trials and preserve the hard FWD gate `[testing_tuning, p.327-335]`.
