# SUMMARY — 017 Carver multi-asset forecast

## Verdict

`fail`. The diversified Carver-style positive EWMAC forecast portfolio reduced
drawdown versus its equal-weight risky benchmark, but it did not beat benchmark
Sharpe and failed MCPT, PBO, DSR and the latest 63-day FWD stress. No winner
claim.

## What Was Tested

Four pre-registered configs combined positive volatility-standardised EWMAC
forecasts across `SPY/QQQ/TLT/GLD` or `SPY/QQQ/TLT/IEF/GLD`, normalised weights by
inverse realized volatility, and applied 10% or 15% volatility targeting with a
1.5x cap. The design follows Carver's diversified forecast and position-sizing
framework `[systematic_trading, p.40]`, `[systematic_trading, p.118-119]`,
`[systematic_trading, p.137-148]`, `[systematic_trading, p.159-173]`.

## Benchmark Comparison

- Best `risk4_ewmac16_64_vt10`: CAGR 9.85%, Sharpe 0.930, MDD -20.92%.
- Equal-weight `SPY/QQQ/TLT/GLD` benchmark: CAGR 12.30%, Sharpe 1.156, MDD
  -25.16%.
- The forecast layer cut drawdown but sacrificed too much return and risk-adjusted
  performance.

## Gates

- Data freshness: pass, common cache ended 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.930 < 1.156.
- IS MCPT: fail, `p=0.250` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.530` with 100 reps and 12 WF windows.
- PBO: fail, `0.600 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.0874` using cumulative `n_trials=56` `[advances_fin_ml,
  p.222-223]`.
- WF windows: pass, 9/12 positive versus required 6.
- OOS: pass, final 20% return +58.74%.
- FWD stress: fail, latest 63 observations -3.62%.
- Bootstrap: pass, 99.9% mean daily CI low `0.0001087`.
- Cross-lib: pass, NumPy-style CAGR delta 0.00pp.

## Lessons

Carver-style diversification improved drawdown and bootstrap behavior, but the
forecast selection did not produce statistically unusual performance under
permutation. The high WF MCPT p-value argues that the apparent risk control is
mostly ordinary multi-asset diversification, not a robust timing edge.

## Next Step

Do not locally tune EWMAC lookbacks, volatility target or this exact universe.
Prefer a genuinely different non-beta mechanism, such as carry/yield data with a
clear economic source, or pause if no clean data source is available
`[testing_tuning, p.327-335]`.
