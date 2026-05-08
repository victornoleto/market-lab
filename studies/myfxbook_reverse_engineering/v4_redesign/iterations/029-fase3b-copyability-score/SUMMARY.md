# SUMMARY — 029-fase3b-copyability-score

## Verdict

`DONE` with result verdict `TOO_MANY_PASS_REQUIRES_REPORT_REVIEW`.

The offline scoreboard evaluated exactly the 21 audit-only `pre_screen_go_systems` fixed in `FILTER_COPY_PLAN.md`. It produced 4 `PASS` and 17 `STOP`. Because 4 pass systems exceeds the planned 1-3 diagnostic shortlist, the next step must be a report/human-review STOP path, not monitor setup and not threshold relaxation.

## What Was Done

- Added `studies/myfxbook_reverse_engineering/scripts/copyability_scoreboard.py`.
- Generated `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.json`.
- Generated `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.md`.
- Applied the pre-registered gates before scoring: pre-screen GO/K1, MCPT, PSR, concentration, monthly stability, no-trade gap, recent drawdown, monthly trade frequency, 2.0-pip cost drag, net expectancy, and single-asset concentration.
- Computed `copyability_score` only for systems with `copyability_status=PASS`.

## Key Metrics

- Systems evaluated: `21`.
- PASS: `4` (`8577442`, `1152318`, `10067081`, `10062918`).
- STOP: `17`.
- Main STOP reason: `single_asset_pnl_share_gt_80pct` on 13 systems.
- Other STOP reasons: monthly stability low (`5`), non-positive expectancy after 2-pip cost (`4`), cost drag >= 50% (`3`), operational gap > 90d (`2`), frequency outside [5,300] (`1`).

## Citations Used

- MCPT retained as track-record pre-screen evidence `[evidence_based_ta, p.325-328]`.
- PSR retained for a single EA return series `[advances_fin_ml, p.260-263]`.
- Selecting/ranking among 21 systems disclosed as multiple-testing risk `[advances_fin_ml, p.273-275]`.
- 2.0-pip copy-cost overlay used because short-strategy copy is sensitive to slippage/spread `[systematic_trading, p.182-197]`.
- Fixed universe and no post-ranking threshold changes preserve the anti-data-mining guardrail `[evidence_based_ta, p.247-260]`.

## Caveats

- The result is diagnostic only. It does not authorize paper/live, AutoTrade real, capital allocation, or Plano A reactivation.
- The 4 PASS count is not converted into a top-3 by relaxing or adding thresholds. The report step must explain the excess PASS count under the frozen rules.

## Next Lesson

The next session should write a report/STOP review for task 029's result and decide whether governance should add a formal `030-fase3b-copyability-report` task. It must not start monitor setup.
