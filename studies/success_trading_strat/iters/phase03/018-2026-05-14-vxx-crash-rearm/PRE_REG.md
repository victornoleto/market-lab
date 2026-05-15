# PRE_REG - Phase 3 Iteration 018

## Hypothesis

Test a volatility-spike crash-rearm mechanism: stay invested in `QQQ`, detect a
crash/stress regime with physically available `VXX`, then temporarily re-risk into
`QLD` or `TQQQ` only after volatility has partially normalized. This differs from
the prior drawdown/SMA rearm families by using a volatility-stress sensor rather
than price drawdown and recovery triggers. The return engine is controlled embedded
LETF exposure after stress, not defensive cash timing `[leverage_for_the_long_run,
p.16-17]`, `[systematic_trading, p.119]`, `[leverage_space, p.149-167]`.

Validation keeps MCPT, PBO, DSR, walk-forward, OOS, FWD, bootstrap and cross-lib as
hard controls `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

## Data And Window

Physical daily parquets to audit before testing: `QQQ`, `QLD`, `TQQQ`, `VXX`,
`SPY`, `SHV`. Use the aligned intersection of available adjusted closes. `VXX` is
signal-only; traded exposures are `QQQ`, `QLD` or `TQQQ`.

If any required physical file or close column is absent, close `data_blocked` with
`n_trials=0`. Do not substitute another volatility proxy after preregistration.

## Exact Configs

Four configs, all one-bar lagged:

1. `qqq_qld_vxx90_norm60_h63`: trigger when lagged `VXX` is above its 252d 90th percentile, arm when it falls below 60% of its 21d max, then hold `QLD` for 63 sessions.
2. `qqq_qld_vxx90_norm70_h126`: same trigger, normalize below 70% of 21d max, hold `QLD` for 126 sessions.
3. `qqq_tqqq_vxx95_norm60_h63`: trigger above 252d 95th percentile, normalize below 60% of 21d max, hold `TQQQ` for 63 sessions.
4. `qqq_tqqq_vxx95_norm70_h126`: trigger above 252d 95th percentile, normalize below 70% of 21d max, hold `TQQQ` for 126 sessions.

No local tuning after seeing results. `n_trials=4`.

## Benchmarks

Primary buy-and-hold benchmark: `QQQ` buy-and-hold on the exact aligned dates,
per Phase 3 Nasdaq LETF/crash-rearm mapping.

Opportunity benchmark: `SPY` buy-and-hold on the exact aligned dates.

Context benchmarks: same traded booster buy-and-hold (`QLD` or `TQQQ`) and `SHV`.

## Economic Kill Rule

If best strategy CAGR <= primary `QQQ` buy-and-hold CAGR or terminal wealth <=
primary `QQQ` buy-and-hold terminal wealth, status must be `fail`. No
`economic_beater_not_validated`, `candidate_watchlist`, `paper_trade_candidate` or
`strict_winner` label is allowed.

## Planned Gates

- IS MCPT with 200 reps on fixed best rule, pass `p <= 0.01`.
- WF MCPT with 100 reps, pass `p <= 0.05`.
- PBO `< 0.5` across the four pre-registered configs.
- DSR `p < 0.05` using cumulative trials after this iteration.
- Walk-forward: at least 6 positive windows and at least 8 windows when available.
- OOS: final 20% compounded return positive.
- FWD stress: latest 63 sessions positive.
- Bootstrap: 99.9% daily mean-return CI low > 0.
- Cross-lib/reference parity: CAGR delta <= 3pp.

## Trial Accounting

- `cumulative_n_trials` before: 284.
- `n_trials`: 4.
- `cumulative_n_trials` after: 288.

## Conservative Ambiguities

The prompt state says this is iteration 018 with `total_iterations=17`, while
`docs/CURRENT_STATE.md` contains later-looking public lines for this same study.
Conservative choice: follow `MEMORY.md`, the injected loop state and the latest
physical Phase 3 artifact (`017`) as the operational source for this iteration.
