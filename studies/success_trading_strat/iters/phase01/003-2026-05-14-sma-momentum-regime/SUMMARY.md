# SUMMARY — 003 sma momentum regime

## Verdict

`fail`. The family was economically cleaner than buy-and-hold on drawdown and
Sharpe for the best config, but it failed the hard anti-overfit stack: PBO,
IS-MCPT and WF-MCPT.

## What Was Tested

Four pre-registered daily long-only configs were tested over Tiingo daily data
from 2008-01-01 through 2026-05-13: `SPY` or `QQQ` risk-on when close was above
SMA(100/200) and 63-day momentum was positive, otherwise `SHV`/cash. Signals were
lagged one bar to avoid same-close lookahead `[leverage_for_the_long_run, p.13,
p.16]`, `[stocks_on_the_move, p.76-77]`, `[advances_fin_ml, p.31-34]`.

## Benchmark Comparison

Best config: `qqq_sma200_mom63`.

| metric | best config | QQQ buy-hold |
|---|---:|---:|
| CAGR | 11.43% | 16.51% |
| Sharpe | 0.862 | 0.795 |
| MDD | -18.60% | -49.40% |
| terminal multiple | 7.27x | 16.45x |

The rule improved risk-adjusted return and drawdown but sacrificed too much
absolute compounding versus QQQ buy-and-hold.

## Gates

| gate | result |
|---|---|
| IS MCPT | FAIL, `p=0.045` vs required `<=0.01` |
| WF MCPT | FAIL, `p=0.170` vs required `<=0.05` |
| PBO | FAIL, `0.871` vs required `<0.5` |
| DSR | PASS, `p=0.00486` with `n_trials=4` |
| WF windows | PASS, `13/18` positive |
| OOS holdout | PASS, `+95.82%` |
| FWD 63d stress | PASS, `+14.99%` |
| Bootstrap 99.9% mean CI low | PASS, `+0.000095` daily |
| Cross-lib | not computed, so no promotion possible |

## Lessons

The high PBO says the best in-sample variant is not stable across CSCV splits,
and both MCPT tests say the serial structure is not exceptional enough after
permutation `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
This is a classic defensive timing profile: lower drawdown, lower terminal
wealth, and no honest edge.

## Next Step

Do not locally tune SMA/momentum lengths. If continuing, use a different
mechanism, such as cross-sectional asset selection or volatility targeting, with
fresh pre-registration and explicit trial accounting `[testing_tuning,
p.327-335]`.
