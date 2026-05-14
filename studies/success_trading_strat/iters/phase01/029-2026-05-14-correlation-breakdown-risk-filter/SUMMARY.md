# SUMMARY - 029 Correlation Breakdown Risk Filter

## Verdict

`fail`. Best config `spy_corr63_lt0` did not clear the full gate stack. No winner claim.

## What Was Tested

Four pre-registered filters held `SPY` or `QQQ` only when lagged rolling equity/Treasury correlation was negative; otherwise they held `SHV` `[risk_parity, p.80-81]`, `[systematic_trading, p.170-171]`.

## Benchmark Comparison

Best `spy_corr63_lt0`: CAGR 9.03%, Sharpe 0.562, MDD -55.20%.
Benchmark buy-and-hold: CAGR 10.97%, Sharpe 0.627, MDD -55.20%.

## Gates

- Data freshness: pass, common data 2007-01-11 through 2026-05-13.
- Economic Sharpe vs benchmark: fail, 0.562 vs 0.627.
- IS MCPT: fail, `p=0.810` vs required `<=0.01`.
- WF MCPT: fail, `p=0.580` vs required `<=0.05`.
- PBO: pass, `0.103` vs required `<0.5`.
- DSR: fail, `p=0.5240` with cumulative `n_trials=100`.
- Walk-forward: pass, 14/16 positive windows.
- OOS: pass, final 20% return 57.40%.
- FWD 63d: pass, 0.85%.
- Bootstrap 99.9% mean daily low: fail, `-0.00002050`.
- Cross-lib numpy/pandas CAGR: pass, delta 0.00pp.

## Lessons

The correlation-breakdown filter is plausible as a risk diagnostic, but this sparse version did not produce enough economic edge or statistical robustness. Per kill rules, do not tune correlation windows, thresholds, or add local overlays inside this family `[testing_tuning, p.327-335]`.

## Next Step

Use the final planned iteration only for a genuinely different information source or a closure/audit iteration; do not continue local parameter search on this family.
