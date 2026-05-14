# SUMMARY — 005 volatility-targeted static sleeves

## Verdict

`fail`. The family produced an economically cleaner defensive allocation than
static 60/40, but it failed the pre-registered IS-MCPT, WF-MCPT and PBO gates.
Cross-lib was intentionally not computed in this minimal iteration, so promotion
was impossible regardless.

## What Was Tested

Four fixed ETF sleeves were volatility-targeted to 10% annualized volatility with
a 100-trading-day lookback and 1.5x leverage cap. The mechanism was risk
standardization, not momentum selection: weights were fixed across `SPY`, `QQQ`,
`IEF` and `GLD`, with residual cash in `SHV` when the volatility scale was below
1.0 `[systematic_trading, p.40]`, `[systematic_trading, p.196-197]`,
`[systematic_trading, p.146]`.

An implementation alignment bug in the first run double-dropped the benchmark
lookback. It was corrected before recording `RESULTS.json`; configs and gates
were unchanged from `PRE_REG.md`.

## Benchmark Comparison

Best config: `vt_35spy_15qqq_30ief_20gld`.

| metric | best config | static 60/40 SPY/IEF | SPY buy-hold |
|---|---:|---:|---:|
| CAGR | 10.39% | 8.84% | 11.86% |
| Sharpe | 1.005 | 0.798 | 0.665 |
| MDD | -20.34% | -29.79% | -50.70% |
| terminal multiple | 5.89x | 4.57x | 7.47x |

The result improves Sharpe and drawdown versus 60/40, but does not beat SPY on
terminal wealth.

## Gates

| gate | result |
|---|---|
| IS MCPT | FAIL, `p=0.12` vs required `<=0.01` |
| WF MCPT | FAIL, `p=0.43` vs required `<=0.05` |
| PBO | FAIL, `0.657` vs required `<0.5` |
| DSR | PASS, `p=0.00533` with cumulative `n_trials=12` |
| WF windows | PASS, `11/14` positive |
| OOS holdout | PASS, `+88.88%` |
| FWD 63d stress | PASS, `+1.93%` |
| Bootstrap 99.9% mean CI low | PASS, `+0.00015055` daily |
| Cross-lib | not computed, so no promotion possible |

## Lessons

Volatility targeting is useful as a defensive allocator, but the MCPT failures
say the observed Sharpe is not exceptional after destroying temporal order
`[testing_tuning, p.318-320]`. The PBO failure also shows that picking the best
among only four correlated static sleeves is still unstable `[advances_fin_ml,
p.208-211]`.

## Next Step

Do not tune this local sleeve set. If continuing, pivot again to a genuinely
different mechanism such as carry/term-structure, volatility-risk-premium proxy,
or a single literature-anchored rule with fewer selection degrees of freedom
`[testing_tuning, p.327-335]`.
