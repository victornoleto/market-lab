# PRE_REG — 029-fase3b-copyability-score

## Task

- ID: `029-fase3b-copyability-score`
- Source: `TASKS.md` section `029-fase3b-copyability-score` and `tasks/029-fase3b-copyability-score.md`
- Dependency checked: `009-fase3b-replan-filter-copy` is `DONE` in `PROGRESS.md`

## Scope

Implement the minimum offline scorer for the 21 audit-only `pre_screen_go_systems` fixed in `FILTER_COPY_PLAN.md`. The scorer applies the blocking copyability gates first, then computes `copyability_score` only for systems with `copyability_status=PASS` using the exact components and weights already pre-registered in `FILTER_COPY_PLAN.md`.

This is diagnostic only: no paper/live, no AutoTrade real, no order placement, no threshold change after observing the ranking, and no deploy recommendation.

## Inputs

- `studies/myfxbook_reverse_engineering/v4_redesign/FILTER_COPY_PLAN.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/RESULTS.json`
- `studies/myfxbook_reverse_engineering/_diagnostics/batch_summary_fase1.json`
- `studies/myfxbook_reverse_engineering/systems/<id>/decoding_v4_fase1/pre_decode_screen.json`
- Existing read-only trade caches under `studies/myfxbook_reverse_engineering/data/trades/<id>/`

## Outputs

- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.json`
- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/029-fase3b-copyability-score/run.log`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/029-fase3b-copyability-score/RESULTS.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/029-fase3b-copyability-score/SUMMARY.md`

## Pre-Registered Rules

- Universe gate: evaluate exactly the 21 IDs fixed in `FILTER_COPY_PLAN.md` to avoid ex-post cherry-pick and data-mining `[evidence_based_ta, p.247-260]`.
- Keep Fase 1 pre-screen gates: `pre_screen_decision=GO`, `mcpt_p < 0.05`, `psr_p < 0.05`, and `concentration_top5 < 0.50`; MCPT is the pre-screen track-record test `[evidence_based_ta, p.325-328]`, while PSR is the correct single-series EA track-record statistic `[advances_fin_ml, p.260-263]`.
- Monthly stability gate: STOP if fewer than 60% of closed months have positive net PnL, or if there is an operational no-trade gap greater than 90 days after track-record start `[evidence_based_ta, p.247-260]`.
- Recent drawdown gate: STOP if the last-90-day drawdown exceeds 1.25x the historical max closed drawdown.
- Trade-frequency gate: STOP if median monthly closed trades is `< 5` or `> 300`; high short-horizon turnover is sensitive to implementation frictions `[systematic_trading, p.182-197]`.
- Cost/slippage gate: model 2.0 pips round-trip per trade; STOP if this cost consumes `>= 50%` of gross edge or makes average expectancy `<= 0` `[systematic_trading, p.182-197]`.
- Real-vs-Demo: warning/score penalty only, not a blocking gate.
- Single-asset gate: STOP operationally if more than 80% of PnL comes from one symbol; this remains diagnostic and does not authorize deploy.
- Ranking-selection warning is mandatory because selecting top systems from multiple EAs creates multiple-testing risk requiring DSR/ranking-selection disclosure `[advances_fin_ml, p.273-275]`.

## Acceptance

- JSON parses and contains exactly 21 systems.
- MD contains a table and conclusion.
- No system outside the fixed 21-ID universe is evaluated.
- `copyability_score` is numeric only for `PASS`; it is `null` for `STOP`.
- `next_prompt.md` points to report/STOP according to the result; it does not relax thresholds or start monitor/paper/live.

## Kill-Switches

- Mark `BLOCKED` if required metrics need credentials, live API, AutoTrade real, order execution, or writing prohibited paths.
- Mark `FAILED` cleanly if all systems fail the pre-registered copyability gates; do not alter thresholds.
- Stop if implementation would require modifying `frozen_rules/`, `docs/investment-mandate.md`, frozen trade data, or other studies.
