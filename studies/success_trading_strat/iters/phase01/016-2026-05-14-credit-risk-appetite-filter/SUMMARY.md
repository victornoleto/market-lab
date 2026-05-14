# SUMMARY — 016 credit risk appetite filter

## Verdict

`fail`. The `HYG/IEF` credit-risk appetite filter reduced drawdown versus buy-and-
hold, but it did not beat the same-asset benchmark on Sharpe and failed MCPT, PBO,
DSR and bootstrap. No winner claim.

## What Was Tested

Four pre-registered configs held `SPY` or `QQQ` only when lagged `HYG/IEF` ratio
momentum was positive and the risk asset's lagged 63-day momentum was positive;
otherwise they held `SHV`. This was a cross-asset/intermarket risk filter rather
than another local equity volatility threshold `[systematic_trading, p.42]`,
`[trading_systems_methods, p.13]`.

## Benchmark Comparison

- Best `spy_hygief126_m63`: CAGR 6.35%, Sharpe 0.730, MDD -23.25%.
- SPY buy-and-hold same window: CAGR 15.12%, Sharpe 0.913, MDD -33.70%.
- The filter lowered drawdown but sacrificed too much return and risk-adjusted
  performance.

## Gates

- Data freshness: pass, common cache ended 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.730 < 0.913.
- IS MCPT: fail, `p=0.310` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.430` with 100 reps and 12 WF windows.
- PBO: fail, `0.900 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.2749` using cumulative `n_trials=52` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 9/12 positive versus required 6.
- OOS: pass, final 20% return +46.66%.
- FWD stress: pass, latest 63 observations +4.78%.
- Bootstrap: fail, 99.9% mean daily CI low `-0.0000182`.
- Cross-lib: pass, NumPy CAGR delta ~0.00pp.

## Lessons

The credit proxy behaved mostly like a conservative beta timing overlay: it helped
drawdown but did not create statistically unusual returns under permutation tests.
The high PBO argues against local lookback tuning of this exact `HYG/IEF` gate.

## Next Step

Do not tune `HYG/IEF` lookbacks locally. Prefer a genuinely different mechanism,
such as multi-asset forecast combination with explicit diversification or a data
source that is not another risk-on/risk-off beta throttle `[testing_tuning,
p.327-335]`.
