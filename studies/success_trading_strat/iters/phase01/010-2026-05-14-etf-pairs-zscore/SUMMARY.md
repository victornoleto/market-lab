# SUMMARY — 010 ETF pairs z-score

## Verdict

`fail`. The market-neutral ETF pairs pivot produced one mildly positive bond-pair
config, but it did not beat SHV on Sharpe and failed IS MCPT, WF MCPT, DSR and
bootstrap.

## What Was Tested

Four pre-registered ratio z-score pair configs: `GLD/SLV` with 60d and 120d
lookbacks, `TLT/IEF` with 60d, and `SPY/QQQ` with 60d. Entry was `|z| > 1`, exit
was z-score crossing zero, and positions were equal-notional long/short with a
one-bar execution lag. The design follows Chan's pairs/z-score template while
avoiding fitted hedge ratios in this first smoke `[algo_trading_chan, p.65-66]`,
`[algo_trading_chan, p.71-73]`.

## Benchmark Comparison

- Best `tlt_ief_z60_e1`: CAGR 0.69%, Sharpe 0.183, MDD -12.05%.
- SHV benchmark: CAGR 1.39%, Sharpe 5.425, MDD -0.45%.
- SPY opportunity-cost benchmark: CAGR 14.19%, Sharpe 0.859, MDD -33.70%.
- The best pair had positive CAGR but no compelling risk-adjusted edge versus a
  cash-like benchmark.

## Gates

- Economic Sharpe vs SHV: fail, 0.183 < 5.425.
- IS MCPT: fail, `p=0.365` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.53` with 100 reps and 12 WF windows.
- PBO: pass, `0.429 < 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.9049` using cumulative `n_trials=28`
  `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 8/12 positive.
- OOS: pass, final 20% return +15.59%.
- FWD stress: pass, last 63 trading days +1.02%.
- Bootstrap: fail, 99.9% mean daily CI low `-0.0000926`.
- Cross-lib: pass, NumPy CAGR delta 0.00pp.

## Lessons

Simple ETF pairs mean reversion is structurally different from prior long-only
families, but the edge is economically too small and indistinguishable from the
permutation null. The bond pair's positive OOS/FWD is not enough to overcome DSR
and MCPT rejection.

## Next Step

Do not tune pairs lookbacks or z-score thresholds locally. Continue with a new
mechanism, preferably one that is not another price-only technical rule over the
same broad ETFs `[testing_tuning, p.327-335]`.
