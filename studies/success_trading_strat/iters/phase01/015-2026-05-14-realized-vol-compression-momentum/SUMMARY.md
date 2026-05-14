# SUMMARY — 015 realized volatility compression momentum

## Verdict

`fail`. The realized-volatility compression gate reduced drawdown versus buy-and-
hold, but the best config lost to the same-asset benchmark on Sharpe/CAGR and
failed MCPT, PBO, DSR and bootstrap. No winner claim.

## What Was Tested

Four pre-registered `SPY/QQQ` configs that hold the risk asset only when prior
20-day realized volatility ranks below a prior 252-day percentile threshold and
63-day momentum is positive; otherwise they hold `SHV`. This was a conservative
non-crypto, non-VIX pivot `[volatility_trading, p.36]`,
`[volatility_trading, p.58-59]`, `[quant_trading_chan, p.142-143]`.

## Benchmark Comparison

- Best `qqq_rv20_p60_m63`: CAGR 7.63%, Sharpe 0.727, MDD -21.20%.
- QQQ buy-and-hold same window: CAGR 19.09%, Sharpe 0.948, MDD -35.12%.
- The strategy improved drawdown but sacrificed too much upside and risk-adjusted return.

## Gates

- Data freshness: pass, common cache ended 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.727 < 0.948.
- IS MCPT: fail, `p=0.425` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.490` with 100 reps and 12 WF windows.
- PBO: fail, `0.514 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.2850` using cumulative `n_trials=48` `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 9/12 positive versus required 6.
- OOS: pass, final 20% return +59.60%.
- FWD stress: pass, latest 63 observations +11.14%.
- Bootstrap: fail, 99.9% mean daily CI low `-0.0000428`.
- Cross-lib: pass, NumPy CAGR delta ~0.00pp.

## Lessons

Volatility compression helped risk control but acted mostly as beta throttling;
it did not create a statistically unusual return path under MCPT and did not beat
simple QQQ exposure on Sharpe. The PBO result just above the hard threshold also
argues against tuning the percentile locally.

## Next Step

Do not locally tune realized-volatility percentiles or momentum windows. A
conservative next iteration should test a different mechanism, preferably one with
cross-asset diversification or a non-price input, rather than another equity beta
throttle `[testing_tuning, p.327-335]`.
