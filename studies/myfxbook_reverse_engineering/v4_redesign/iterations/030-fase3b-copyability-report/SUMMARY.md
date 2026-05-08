# SUMMARY — 030-fase3b-copyability-report

## Verdict

`DONE` with governance verdict `TOO_MANY_PASS_REQUIRES_HUMAN_GOVERNANCE`.

Task 029 found 4 `PASS` systems among 21 audit-only candidates. Task 030 documented that result as a STOP-for-human-decision state, not as an automatic shortlist.

## What Was Done

- Created `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_REVIEW.md`.
- Summarized the 4 PASS systems: `8577442`, `1152318`, `10067081`, `10062918`.
- Documented selection risk, concentration risk, cost/slippage caveats, and governance options.
- Rewrote `next_prompt.md` to stop for human decision.
- Updated `PROGRESS.md` and `jornada/`.

## Citations Used

- MCPT remains only pre-screen evidence for track-record plausibility `[evidence_based_ta, p.325-328]`.
- PSR remains the correct test for a single EA return series `[advances_fin_ml, p.260-263]`.
- Selecting top-N among 21 systems creates multiple-testing/ranking-selection risk `[advances_fin_ml, p.273-275]`.
- Copying short-horizon systems is sensitive to spread/slippage and modeled costs `[systematic_trading, p.182-197]`.
- Changing emphasis after seeing the scoreboard would be data-mining `[evidence_based_ta, p.247-260]`.

## Caveats

- No top-3, top-1, or operational candidate was selected.
- No monitor/cron, paper/live, broker action, real AutoTrade, or capital allocation was started.
- `1152318` appears stale in the task 029 data; this is documented as a caveat, not used as an ex-post disqualifier.
- `10067081` is near the upper frequency gate and cost-sensitive; this is documented as a caveat, not used as an ex-post disqualifier.

## Lesson For The Next Session

The loop must stop until a human chooses one of: end v4 Fase 3b, authorize a pre-registered tie-breaker task, or authorize a read-only/manual monitor-plan task. A future task must be explicit before execution and must not reuse this report as permission to deploy.
