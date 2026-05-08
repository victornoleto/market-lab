# PRE_REG — 030-fase3b-copyability-report

## Task

- ID: `030-fase3b-copyability-report`
- Phase: `3b`
- Depends on: `029-fase3b-copyability-score`
- Task source: `TASKS.md` lines defining task 030 and `tasks/030-fase3b-copyability-report.md`.

## Scope

Write the governance report for task 029's `TOO_MANY_PASS_REQUIRES_REPORT_REVIEW` result. The minimum scope is documentation only: explain the 4 `PASS` systems, concentration/operational caveats, and human governance options.

This task will not choose a top-3, will not change thresholds, will not start monitor/cron, and will not authorize paper/live or real AutoTrade.

## Inputs

- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.json`
- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/FILTER_COPY_PLAN.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/029-fase3b-copyability-score/SUMMARY.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/029-fase3b-copyability-score/RESULTS.json`

## Outputs

- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_REVIEW.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/030-fase3b-copyability-report/run.log`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/030-fase3b-copyability-report/RESULTS.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/030-fase3b-copyability-report/SUMMARY.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md`
- `jornada/2026-05-04-1316-myfxbook-v4-copyability-review-stop.md`
- `jornada/README.md`

## Technical Decisions And Citations

- Keep MCPT as pre-screen evidence for the EA track record; it remains evidence, not deployment authorization `[evidence_based_ta, p.325-328]`.
- Keep PSR as the proper test for a single EA series; do not recast the vendor track record as DSR with `M=1` `[advances_fin_ml, p.260-263]`.
- Treat selecting top-N among 21 EAs as multiple-testing/ranking-selection risk; a human decision or pre-registered tie-breaker is required before any shortlist is operationalized `[advances_fin_ml, p.273-275]`.
- Highlight 2.0-pip cost/slippage sensitivity for copy trading of short-horizon systems `[systematic_trading, p.182-197]`.
- Preserve the frozen universe and thresholds to avoid data-mining after seeing the score distribution `[evidence_based_ta, p.247-260]`.

## Acceptance Criteria

- `COPYABILITY_REVIEW.md` exists and contains the 6 required sections: verdict, 4 PASS summary, selection risk, concentration/operational caveats, governance options, and guardrails.
- The report does not automatically choose top-3 or any winner.
- No monitor, cron, paper/live, real AutoTrade, broker action, or capital allocation is initiated.
- `next_prompt.md` stops for human governance decision.
- `RESULTS.json` is valid JSON.

## Kill-Switches

- Any attempt to break the 4-way PASS set without a newly pre-registered rule marks the task `FAILED`.
- Any attempt to start monitoring, copy, paper/live, or AutoTrade marks the task `FAILED`.
