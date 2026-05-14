# SUMMARY — 004 cross-sectional ETF momentum

## Verdict

`fail`. The family reduced drawdown versus the equal-weight ETF benchmark, but it
failed the pre-registered economic Sharpe screen, IS-MCPT, WF-MCPT and recent FWD
stress. Cross-lib was intentionally not computed in this minimal iteration, so
promotion was impossible regardless.

## What Was Tested

Four monthly cross-sectional ETF momentum configs were tested on Tiingo daily
adjusted closes from 2008-07-02 through 2026-05-13. The universe was `SPY`,
`QQQ`, `IWM`, `TLT`, `GLD`; the defensive asset was `SHV`. Configs ranked ETFs
by lookback return divided by realized volatility using 63 or 126 trading days,
then held top 1 or top 2 ETFs with one-bar execution lag `[stocks_on_the_move,
p.76-77]`, `[systematic_trading, p.185-188]`, `[advances_fin_ml, p.31-34]`.

Implementation note: an initial run exposed a position-carry bug where month-end
weights were forward-filled per asset instead of replacing the full portfolio.
The runner was corrected before recording final `RESULTS.json`; this preserves
the pre-registered configs and avoids inflated leverage.

## Benchmark Comparison

Best config: `mom126_top2`.

| metric | best config | equal-weight ETF benchmark | SPY buy-hold |
|---|---:|---:|---:|
| CAGR | 10.83% | 11.56% | 12.49% |
| Sharpe | 0.824 | 0.898 | 0.693 |
| MDD | -19.96% | -28.72% | -47.17% |
| terminal multiple | 6.26x | 7.04x | 8.16x |

The rule improved drawdown versus both benchmarks but did not beat the primary
benchmark on Sharpe or CAGR.

## Gates

| gate | result |
|---|---|
| IS MCPT | FAIL, `p=0.075` vs required `<=0.01` |
| WF MCPT | FAIL, `p=0.29` vs required `<=0.05` |
| PBO | PASS, `0.343` vs required `<0.5` |
| DSR | PASS, `p=0.0229` with cumulative `n_trials=8` |
| WF windows | PASS, `10/14` positive |
| OOS holdout | PASS, `+78.02%` |
| FWD 63d stress | FAIL, `-0.32%` |
| Bootstrap 99.9% mean CI low | PASS, `+0.00008899` daily |
| Cross-lib | not computed, so no promotion possible |

## Lessons

Cross-sectional ETF rotation is more stable than the prior single-index timing
family on PBO, but the MCPT results say the observed path is not exceptional
after destroying serial order `[testing_tuning, p.318-320]`. The best rule is a
defensive allocator, not a benchmark-beating strategy.

## Next Step

Do not tune this local ETF momentum family. If continuing, pivot to a distinct
mechanism such as volatility-targeted static sleeves or carry/term-structure
signals, with 1-6 configs and explicit cumulative trial accounting
`[testing_tuning, p.327-335]`.
