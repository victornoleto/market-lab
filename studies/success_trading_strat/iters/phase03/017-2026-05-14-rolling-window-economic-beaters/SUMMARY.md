# SUMMARY - Phase 3 Iteration 017

## Verdict

`fail`. No winner, no candidate/watchlist label, no paper-trade label, no deploy
implication, mandate remains 100% Plano C.

## Tested

Pre-registered rolling-window economic stress across five prior Phase 3 economic
beaters from iterations 010-014. No strategy rule, weight, trigger, rebalance
cadence, volatility cap or financing assumption was changed; this was a robustness

Windows tested: rolling 3y and 5y, stepped every 63 observations. `n_trials=0`,
so cumulative trials remain 284.

## Benchmark Comparison

Each candidate had to beat its original dual primary B&H benchmark in both CAGR and
terminal wealth for every rolling window. The audit produced 534 candidate-window
rows; 128 failed the economic gate.

Failed-window counts:

- `010_upro_tlt_gld`: 8/104 failed.
- `011_sso_tlt_gld`: 21/124 failed.
- `012_upro_tmf_gld`: 21/104 failed.
- `013_nasdaq_rearm`: 52/98 failed.
- `014_upro_tlt_spread`: 26/104 failed.

## Gates

- Physical daily files: pass for `SPY`, `QQQ`, `UPRO`, `SSO`, `QLD`, `TQQQ`, `TLT`, `TMF`, `GLD`, `SHV`.
- Rolling CAGR vs primary B&H: fail.
- Rolling terminal wealth vs primary B&H: fail.
- MCPT/PBO/DSR/WF/OOS/FWD/bootstrap/cross-lib: not recomputed; prior validation failures remain binding.

## Lessons

The apparent Phase 3 economic beaters are not robust across ordinary 3y/5y holding
windows. Even before considering the original MCPT/DSR/PBO failures, rolling
economic fragility blocks promotion. The Nasdaq rearm candidate is especially
window-fragile, failing 52 of 98 rows.

## Next Step

Do not promote, paper-trade or locally tune the audited economic beaters. Continue
only with a genuinely different Phase 3 mechanism or a closure/consolidation audit;
do not tune balanced-sleeve weights, HFEA weights, crash-rearm triggers, recovery
SMA windows, volatility caps, gross `UPRO/TLT` weights or financing assumptions.
