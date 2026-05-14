# SUMMARY — 006 RSI(2) mean reversion

## Verdict

`fail`. The family reduced drawdown versus buy-and-hold but did not beat the
same-asset benchmark on Sharpe and failed both MCPT gates. Cross-lib was not
computed in this minimal iteration, so promotion was impossible regardless.

## What Was Tested

Four pre-registered `RSI(2)` mean-reversion configs traded `SPY` or `QQQ` after
oversold closes, exiting after `RSI(2) > 70` and holding `SHV` while flat. Signals
were lagged one bar before returns were applied to avoid look-ahead bias
`[quant_trading_chan, p.51]`. No stop loss was used because stops are a known
anti-pattern for mean-reversion systems `[quant_trading_chan, p.142-143]`.

## Benchmark Comparison

Best config: `qqq_rsi2_e5_x70`.

| metric | best config | QQQ buy-hold | SPY buy-hold |
|---|---:|---:|---:|
| CAGR | 8.47% | 16.81% | 11.52% |
| Sharpe | 0.795 | 0.807 | 0.649 |
| MDD | -16.09% | -49.37% | -51.49% |
| terminal multiple | 4.43x | 17.23x | 7.37x |

The rule improved drawdown materially, but gave up too much compounded return and
did not clear the primary Sharpe comparison versus QQQ buy-and-hold.

## Gates

| gate | result |
|---|---|
| IS MCPT | FAIL, `p=0.05` vs required `<=0.01` |
| WF MCPT | FAIL, `p=0.35` vs required `<=0.05` |
| PBO | PASS, `0.214` vs required `<0.5` |
| DSR | PASS, `p=0.0441` with cumulative `n_trials=16` |
| WF windows | PASS, `12/14` positive |
| OOS holdout | PASS, `+58.09%` |
| FWD 63d stress | PASS, `+4.26%` |
| Bootstrap 99.9% mean CI low | PASS, `+0.00010655` daily |
| Cross-lib | not computed, so no promotion possible |

## Lessons

This small mean-reversion family is economically defensive, not superior. The
MCPT failures indicate that the apparent Sharpe is not exceptional once temporal
ordering is destroyed `[testing_tuning, p.318-320]`, and the benchmark comparison
does not justify further local tuning of RSI thresholds.

## Next Step

Do not tune this RSI(2) branch locally. Continue with a different mechanism such
as a carry/term-structure proxy or a single literature-anchored rule with fewer
selection degrees of freedom `[testing_tuning, p.327-335]`.
