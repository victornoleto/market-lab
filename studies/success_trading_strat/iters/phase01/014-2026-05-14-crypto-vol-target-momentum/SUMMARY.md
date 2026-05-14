# SUMMARY — 014 crypto volatility-targeted momentum

## Verdict

`fail`. Volatility-targeted BTC momentum improved risk-adjusted return and fixed
the latest 63d FWD stress that killed iteration 013, but it failed IS MCPT, WF
MCPT, PBO and minimum walk-forward positives. No winner claim.

## What Was Tested

Four pre-registered BTC/ETH trailing-momentum configs with 100d realized-vol
scaling, 20% annualized volatility target and max exposure 1.0. This was a pivot
from Donchian breakouts to volatility-standardized momentum, not a Donchian
lookback tune `[systematic_trading, p.40]`, `[systematic_trading, p.137-148]`,
`[systematic_trading, p.196-197]`.

## Benchmark Comparison

- Best `btc_mom63_vt20`: CAGR 25.57%, Sharpe 1.377, MDD -22.70%.
- BTC buy-and-hold same window: CAGR 68.51%, Sharpe 1.112, MDD -83.15%.
- The strategy improved Sharpe and drawdown, but gave up large crypto beta CAGR.

## Gates

- Data freshness: pass, common cache ended 2026-05-13.
- Economic Sharpe vs benchmark: pass, 1.377 > 1.112.
- IS MCPT: fail, `p=0.015` with 200 reps `[testing_tuning, p.318-320]`.
- WF MCPT: fail, `p=0.110` with 100 reps and 6 WF windows.
- PBO: fail, `0.857 >= 0.5` `[advances_fin_ml, p.208-211]`.
- DSR: pass, `p=0.0189` using cumulative `n_trials=44` `[advances_fin_ml, p.222-223]`.
- WF windows: fail, 5/6 positive versus required 6.
- OOS: pass, final 20% return +20.23%.
- FWD stress: pass, latest 63 observations +0.50%.
- Bootstrap: pass, 99.9% mean daily CI low `+0.000248`.
- Cross-lib: pass, NumPy CAGR delta ~0.00pp.

## Lessons

Volatility targeting solved drawdown and recent FWD stress, but the high PBO says
the selected config is too dependent on which related crypto-momentum variant was
chosen. The family is useful as a risk-control diagnostic, not an honest winner.

## Next Step

Do not tune BTC/ETH momentum lookbacks locally. A conservative next iteration
should pivot away from crypto-only variants or test an infrastructure diagnostic;
if crypto continues, require a broader universe/data-source plan before adding
more trials `[testing_tuning, p.327-335]`.
