# SUMMARY — 019 yield-carry rotation

## Verdict

`fail`. The yield/carry mechanism loaded and ran, but the best config failed
benchmark Sharpe, MCPT, PBO, DSR and latest FWD stress. No winner claim.

## What Was Tested

Four pre-registered carry/yield configs allocated among `SPY`, `TLT`/`IEF` and
`SHV` using lagged dividend-yield-vs-cash and term-spread signals. This was a
non-local-technical pivot motivated by Carver carry forecasts and the need to
avoid tuning failed price-signal families `[systematic_trading, p.32-35]`,
`[systematic_trading, p.119]`, `[systematic_trading, p.288]`,
`[testing_tuning, p.327-335]`.

## Benchmark Comparison

- Best `spy_div_gt_cash_ief_term`: CAGR 11.15%, Sharpe 0.783, MDD -33.70%.
- Pre-registered 60/40 `SPY/IEF` benchmark: CAGR 9.95%, Sharpe 1.004, MDD -21.02%.
- The strategy improved CAGR but took materially worse drawdown and lower Sharpe,
  so it failed the economic benchmark gate.

## Gates

- Data freshness: pass, common data ended 2026-05-08.
- Economic Sharpe vs benchmark: fail, 0.783 < 1.004.
- IS MCPT: fail, `p=0.415` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.460` with 100 reps and 12 WF windows.
- PBO: fail, `0.629 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.2194` using cumulative `n_trials=64` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 11/12 positive versus required 6.
- OOS: pass, final 20% return +17.72%.
- FWD stress: fail, latest 63 observations -0.21%.
- Bootstrap: pass, 99.9% mean daily CI low `0.0000746`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

The carry/yield pivot avoided another technical overlay but produced a classic
carry-profile failure: acceptable long-run return with weak permutation evidence,
high drawdown and negative recent stress. The term-spread/dividend-yield proxy is
not a useful winner path in this simple ETF form.

## Next Step

Do not tune these carry thresholds or tenors locally. Prefer a genuinely new
mechanism, or pause the study if no clean, non-redundant data source is available
`[testing_tuning, p.327-335]`.
