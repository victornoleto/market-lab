# SUMMARY - Phase 3 Iteration 027

## Verdict

`economic_beater_not_validated`. The strategy beat the pre-registered primary
buy-and-hold benchmarks on aligned CAGR and terminal wealth, but failed strict
validation gates. No `strict_winner`, no `candidate_watchlist`, no
`paper_trade_candidate`, no deploy implication. Capital remains 100% Plano C.

## Tested

Four pre-registered monthly `QLD/TLT/GLD` sleeve configs with lagged `QQQ`
realized-volatility throttle and 5% annual financing drag on gross exposure above
1.0. Required physical daily files for `QLD`, `TLT`, `GLD`, `QQQ`, `SPY` and `SHV`
existed through 2026-05-13. The mechanism stayed fully invested and used LETF gross
exposure as the return engine `[leverage_for_the_long_run, p.13]`,
`[systematic_trading, p.137-148]`.

Best config: `qld70_tlt15_gld15_rv126_q30_70_b50_c20`.

## Benchmark Comparison

Aligned window: 2007-01-12 to 2026-05-13.

- Strategy: CAGR 25.34%, terminal wealth 78.26x, Sharpe 0.845, MDD -57.17%.
- `QQQ` B&H: CAGR 16.28%, terminal wealth 18.37x, Sharpe 0.791, MDD -53.41%.
- Equal-weight `QLD/TLT/GLD` B&H: CAGR 15.71%, terminal wealth 16.73x.
- `SPY` opportunity B&H: CAGR 10.92%, terminal wealth 7.40x.
- Context: raw `QLD` B&H was close but lower than the best strategy on this aligned
  window: CAGR 24.77%, terminal wealth 71.64x.

## Gates

- Economic CAGR/terminal vs `QQQ`: pass/pass.
- Economic CAGR/terminal vs equal-weight `QLD/TLT/GLD`: pass/pass.
- SPY opportunity CAGR: pass.
- MDD 1.5x guard vs `QQQ`: pass.
- IS MCPT: fail (`p=0.0746`, required `<=0.01`).
- WF MCPT: fail (`p=0.3267`, required `<=0.05`).
- PBO: pass (`0.377`).
- DSR: fail (`p=0.2121`, cumulative trials after = 312).
- WF windows: pass (`14/16` positive).
- OOS, FWD 63d, bootstrap, cross-lib: pass.

Kill switch: failed one or more strict validation gates. MCPT and DSR failures are
binding `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.222-223]`.

## Lessons

The volatility-throttled `QLD/TLT/GLD` sleeve is another economic beater, but the
edge is not statistically separable from the null under MCPT/DSR. Do not locally tune
`QLD/TLT/GLD` volatility lookbacks, quantiles, weights, boost/cut sizes, rebalance
cadence or financing assumptions after this failure `[testing_tuning, p.327-335]`.

## Ambiguity Note

The working tree and public docs contained pre-existing Phase 3 artifacts beyond the
`MEMORY.md` state supplied to this session. Conservatively, this iteration followed
the user-specified operational state (`total_iterations=26`,
`cumulative_n_trials=308`) and did not revert or edit unrelated changes.

## Next Step

Prefer final closure/audit for Phase 3. Repeated LETF sleeve and gross-exposure
families have produced economic beaters, but MCPT/DSR/PBO or stress gates remain
binding and block promotion.
