# KILL Rules — pre-registered (anti-p-hacking)

Per spec §3.4: KILL rules are **informational tags** (loop continues regardless).
Inheritance fallback applies when KILL fires: T<N+1> uses last valid winner.

| Transition | Threshold | Justification |
|---|---|---|
| KILL T0 (study viability) | T1-best Sharpe < SPY_BH + 0.05 (lh_56y) | Single LETF + SMA does not beat SPY+0.05 → rotation has no value. Tag CLOSE_NO_VALUE. |
| KILL T1→T2 | T2-best < T1-best + 0.05 | Basket adds no value. T3 inherits T1-best. |
| KILL T2→T3 | T3-best < T2-best + 0.05 | Composite signal adds nothing. T4 inherits T2 or T1. |
| KILL T3→T4 | T4-best < T3-best + 0.05 | Cross-sectional adds nothing. T5 inherits last valid winner. |
| KILL T4→T5 | T5-best < T4-best + 0.10 | Carver is much more complex; demands a larger margin. |
| DEPLOY ESCALATION (relaxed 2026-05-06) | Sharpe_net > SPY_net + 0.15 AND DSR cumulative pass AND score ≥ 90 AND all 7 gates pass | Mandate §7 review trigger. |

These thresholds are **frozen** at study start, with one exception:

**2026-05-06 deploy threshold revision (user decision):** The deploy
escalation Sharpe edge requirement was relaxed from `+0.20` to `+0.15` net
edge vs SPY. Rationale: a sustained `+0.15` net Sharpe edge over
multi-decade rolling windows is a meaningful and economically significant
edge — particularly when validated across the 37k-rolling-window robustness
analysis (`STUDY_ROBUSTNESS_ANALYSIS.md`). The spec §3.4 `+0.20` was a
margin-of-safety choice; user (governance) decision is to accept `+0.15`
as the deploy bar. KILL rules T0-T5 remain unchanged (those are
anti-curve-fit Sharpe-based gates, separate from deploy escalation).

Spec ref: pre-publication agent spec §3.4 (removed from the public tree) +
user governance decision 2026-05-06, summarized in `docs/PROJECT_HISTORY.md`.
