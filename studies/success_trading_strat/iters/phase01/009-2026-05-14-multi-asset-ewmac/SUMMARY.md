# SUMMARY — 009 multi-asset EWMAC

## Verdict

`fail`. The EWMAC mechanism pivot produced positive returns, but did not beat the
equal-weight benchmark on Sharpe and failed IS MCPT, WF MCPT, PBO and DSR.

## What Was Tested

Four pre-registered EWMAC configs ranked `SPY/QQQ/TLT` or
`SPY/QQQ/TLT/IEF/GLD` by fixed 16/64 or 32/128 EMA forecast, holding the strongest
positive forecast or `SHV` defensively. Signals were shifted one bar to avoid
same-close lookahead `[quant_trading_chan, p.51]`; EWMAC spans followed Carver's
fixed trend forecast family `[systematic_trading, p.118-119]`.

## Benchmark Comparison

- Best `ewmac_16_64_risk3`: CAGR 11.40%, Sharpe 0.814, MDD -24.97%.
- Same-universe equal-weight `SPY/QQQ/TLT`: CAGR 12.72%, Sharpe 1.049, MDD -30.06%.
- SPY buy-and-hold: CAGR 14.10%, Sharpe 0.854, MDD -33.70%.
- The strategy reduced drawdown versus both benchmarks, but gave up too much return
  and risk-adjusted performance.

## Gates

- Economic Sharpe vs equal-weight: fail, 0.814 < 1.049.
- IS MCPT: fail, `p=0.165` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.43` with 100 reps and 12 WF windows.
- PBO: fail, `0.814 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: fail, `p=0.1017` using cumulative `n_trials=24`
  `[advances_fin_ml, p.222-223]`.
- WF windows: pass, 9/12 positive.
- OOS: pass, final 20% return +58.67%.
- FWD stress: pass, last 63 trading days +9.33%.
- Bootstrap: pass, 99.9% mean daily CI low `+0.0000925`.
- Cross-lib: pass, NumPy CAGR delta 0.00pp.

## Lessons

Simple EWMAC ranking over liquid ETF assets behaves like another defensive trend
filter: drawdown improves, but benchmark-relative Sharpe and permutation robustness
do not. The high PBO suggests the best span/universe choice is unstable even in the
small four-config panel.

## Next Step

Do not tune EWMAC spans locally. Next iteration should pivot to a different
mechanism, preferably one with a structural source not already covered by trend,
volatility targeting, mean reversion, ETF momentum or volatility-ETP carry
`[testing_tuning, p.327-335]`.
