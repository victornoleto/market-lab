# SUMMARY - 028 Gayed LETF QQQ rotation

## Verdict

`fail`. Best config `qld_qqq_sma200_rv70` improved Sharpe and drawdown versus
same-window QLD buy-and-hold, but failed IS MCPT, PBO and DSR. No winner claim.

## What Was Tested

Four pre-registered Gayed-style Nasdaq LETF rotation configs were tested from
2010-02-12 through 2026-05-13 using local Tiingo data: `QLD`/`TQQQ` risk-on when
lagged `QQQ > SMA200`, with or without a sparse 21d realized-volatility cap at the
trailing 252d 70th percentile; otherwise `SHV` `[leverage_for_the_long_run, p.13]`,
`[leverage_for_the_long_run, p.16-17]`, `[trading_systems_methods, p.1085-1091]`.

## Benchmark Comparison

Best `qld_qqq_sma200_rv70`: CAGR 22.64%, Sharpe 0.978, MDD -34.54%.

Benchmark QLD buy-and-hold: CAGR 33.80%, Sharpe 0.916, MDD -63.68%.

The rule improves risk-adjusted return and drawdown, but gives up large terminal
growth versus holding QLD through the full window.

## Gates

- Data freshness: pass, common data through 2026-05-13.
- Economic Sharpe vs benchmark: pass, 0.978 vs 0.916.
- IS MCPT: fail, `p=0.035` vs required `<=0.01`.
- WF MCPT: pass, `p=0.010`.
- PBO: fail, `0.686` vs required `<0.5`.
- DSR: fail, `p=0.0816` with cumulative `n_trials=96`.
- Walk-forward: pass, 11/12 positive windows.
- OOS: pass, final 20% return +114.21%.
- FWD 63d: pass, +4.25%.
- Bootstrap 99.9% mean daily low: pass, `0.0002879`.
- Cross-lib numpy/pandas CAGR: pass, delta 0.00pp.

## Lessons

The Gayed-style LETF regime mechanism has useful drawdown control, but still looks
selection-sensitive under PBO and insufficient after DSR trial deflation
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`. The volatility cap
helped Sharpe/MDD versus the plain SMA version, but cannot be locally tuned because
the family already failed hard gates `[testing_tuning, p.327-335]`.

## Next Step

Do not tune `QQQ` SMA lengths, volatility thresholds, bands, or QLD/TQQQ variants
inside this family. If the loop continues, use a genuinely different information
source, or finish the study after the planned 30 iterations if no new mechanism is
available.

## Implementation Note

Before recording final results, the WF calculation was corrected to use the train
window as signal-history context and score only test-window returns. This avoids
the conservative but misleading behavior where a 200-day SMA computed on test data
alone leaves most of each WF year in `SHV`.
