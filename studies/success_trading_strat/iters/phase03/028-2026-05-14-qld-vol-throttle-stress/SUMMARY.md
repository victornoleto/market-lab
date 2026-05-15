# SUMMARY - Phase 3 Iteration 028

## Verdict

`fail`. The prior `QLD/TLT/GLD` volatility-throttle economic beater remained strong
on the full aligned window, including extra drag stresses, but failed the
pre-registered rolling-window robustness gates. No `strict_winner`, no
`candidate_watchlist`, no `paper_trade_candidate`, no deploy implication. Capital
remains 100% Plano C.

## Tested

Stress-only retest of the Phase 3 iteration 027 best config
`qld70_tlt15_gld15_rv126_q30_70_b50_c20`. No new strategy configs were selected and
`n_trials=0`. The stress recomputed the fixed monthly `QLD/TLT/GLD` sleeve with
lagged `QQQ` realized-volatility throttle, 5% financing on gross exposure above
1.0, additional 25/50/100 bps annual drag, and rolling 3y/5y window checks
`[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.4-7]`,
`[testing_tuning, p.327-335]`.

Required physical daily files for `QLD`, `TLT`, `GLD`, `QQQ`, `SPY` and `SHV`
existed through 2026-05-13.

## Benchmark Comparison

Aligned window: 2007-01-12 to 2026-05-13.

- Strategy base: CAGR 25.34%, terminal wealth 78.26x, Sharpe 0.845, MDD -57.17%.
- `QQQ` B&H: CAGR 16.31%, terminal wealth 18.46x, MDD -53.41%.
- Equal-weight `QLD/TLT/GLD` B&H: CAGR 15.78%, terminal wealth 16.90x.
- `SPY` opportunity B&H: CAGR 10.97%, terminal wealth 7.45x.
- 100 bps extra drag: CAGR 24.10%, terminal wealth 64.53x, still above both primary benchmarks.

## Gates

- Full-window economic gate: pass.
- Extra drag 25/50/100 bps: pass/pass/pass.
- Rolling 3y robustness: fail, 170/196 windows passed both primary benchmarks (`86.73%`, required `>=90%`).
- Rolling 5y robustness: fail, 154/172 windows passed both primary benchmarks (`89.53%`, required `>=90%`).
- Prior strict gates carried forward from iteration 027: IS MCPT fail, WF MCPT fail, DSR fail.

Kill switches: rolling 3y pass rate below 90%, rolling 5y pass rate below 90%, and
prior MCPT/DSR failures remain binding `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.222-223]`.

## Lessons

The full-period CAGR is attractive, but the edge is path-dependent: early rolling
windows lose to equal-weight `QLD/TLT/GLD`, and the prior MCPT/DSR failures already
blocked promotion. Do not locally tune `QLD/TLT/GLD` volatility lookbacks,
quantiles, weights, boost/cut sizes, rebalance cadence, rolling-window thresholds
or financing assumptions after this stress failure `[testing_tuning, p.327-335]`.

## Ambiguity Note

The worktree and public docs contained pre-existing Phase 3 artifacts beyond the
user-supplied operational state. Conservatively, this iteration followed
`MEMORY.md` and the user-specified state (`total_iterations=27`,
`cumulative_n_trials=312`) and did not revert unrelated changes.

## Next Step

Prefer final Phase 3 closure/audit over more local LETF-sleeve tuning. If one more
iteration is required before the 30-iteration cap, use an out-of-family audit or a
genuinely new mechanism with pre-registered rationale, not another nearby
`QLD/TLT/GLD` variant.
