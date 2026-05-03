---
system_id: 9912554
family: UNCATEGORIZED
confidence: 0.30
reason_code: insufficient_evidence
generated: 2026-05-03
rule:
  entry_window_utc: ["12:00", "20:00"]
  pairs: [EURGBP]
  direction: |
    # Best-effort reconstruction. Rank-1 univariate is the only candidate with
    # any signal: p_corr=0.087 (510-test correction). All other ranks 3-9 have
    # p_corr ∈ {0.38, 1.0}; rank-10 tree CV match=0.482 < always-Buy baseline
    # (0.573), i.e., negative discriminative power. Replicator must treat this
    # as a weak prior and report low edge.
    BUY if ret_10_H1 > -0.00361
    SELL otherwise
  exit:
    max_holding_hours: 4930.81  # p95 — empirical, NOT a parameter; see risk_flag (max=12582h ≈ 17 months)
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_0.87
citations:
  - "[evidence_based_ta, p.183-185] — \"start from the null hypothesis that every rule is useless ... only reject Ho if the backtested return falls in the right tail of the sampling distribution (p-value < 0.05)\"; here best p_corr=0.087 fails this gate."
  - "[evidence_based_ta, p.291, p.315 Fig.6.33] — \"the magnitude of data-mining bias grows dramatically with small sample size — e.g., best-of-1,024 rules with 10 obs → bias ~84% per year; with 1,000 obs → bias ~12% per year\"; n=103 trades against 510 candidate features puts this system in the high-bias regime."
  - "[advances_fin_ml, ch.3, p.78-80] — triple-barrier labeling and consistent label spaces; the 5R-1 closed-enum contract demands UNCATEGORIZED with a reason_code rather than force-fitting a provisional family that R1 review would later downgrade."
risk_flags:
  - "extreme_long_tail_hold — p50=162.55h (~6.8d), p95=4930h (~205d), max=12582h (~524d ≈ 17 months); positions are held through multiple regime shifts. Replicator must NOT treat max_holding_hours as a programmable parameter; it is a measured percentile, not a rule."
  - "degenerate_tree — rank-10 DecisionTree CV match-rate 0.482 (std 0.225, fold accuracies [0.60, 0.45, 0.85, 0.25, 0.26]) is BELOW the always-Buy baseline 0.573, i.e., the tree carries negative discriminative power."
  - "marginal_univariate — only rank-1 rule (ret_10_H1 > -0.00361 ⇒ Buy) reaches p_corr=0.087 across 510 tests; ranks 3-9 all p_corr ∈ {0.38, 1.0}. Top rule is essentially \"BUY unless H1 10-bar return is sharply negative\", a momentum-of-weakness filter rather than a discriminative signal."
  - "single_pair_fragility — EURGBP only (103/103 trades); no cross-asset confirmation possible; family heuristics in the closed enum assume FX-major rotation at sessions, which this system does not exhibit."
  - "name_flag_event_thematic — system name \"Happy Brexit FM - REAL\" suggests an EURGBP event-driven thesis. The clock-anchor (12/16/20 UTC = H4 bar opens during London/NY) is purely OHLC-derived; there is no evidence the live bot reads an economic calendar, and the replicator must NOT assume one. Hold distribution (p50 ~6.8d) is incompatible with NEWS_RELEASE_MOMENTUM, which the provisional spec defines around p50 ≈ <5min."
  - "irregular_activity — max gap 63.3 days, ~26 trades/yr; intermittent posture inconsistent with both intraday families (which expect daily clock anchors with high coverage) and pure swing/trend (which expects steadier participation)."
  - "broker_forexmart_1_500 — ForexMart at 1:500 leverage on a USD 2,000 deposit; non-Tier-1 venue with vendor selection-bias risk."
---

# Decoded signal — Happy Brexit FM - REAL (id 9912554)

## Family rationale

The hold distribution (post-R4 fix) is the single most decisive piece of evidence. With p50 = 162.55h (~6.8 days), p95 = 4930.81h (~205 days), and max = 12582.48h (~524 days = ~17 months), every intraday family in the closed enum is disqualified by the explicit anti-pattern in `decoder.md`: "Atribuir família intraday quando hold p50 > 24h confirmado pós-R4 — use UNCATEGORIZED + reason_code=hold_mismatch ou SWING_TREND_MOMENTUM provisional se aplicável." So `LATE_NY_BREAKOUT`, `LONDON_OPEN_MOMENTUM`, `LONDON_OPEN_MR`, `NY_SESSION_REVERSAL`, `OVERLAP_NY_LONDON_RANGE` (Sonnet's prior call), `OVERNIGHT_GAP_FADE`, and `FACTOR_SCALPING` are eliminated upfront. `MARTINGALE_GRID` is excluded by sanity: martingale flag PASS, lot p95/p50 ratio = 1.03, max_streak = 0.

The remaining candidates inside the closed enum are the three provisionals and `UNCATEGORIZED`. `H1_MOMENTUM_GOLD` requires Gold/XAU — EURGBP rules it out. `NEWS_RELEASE_MOMENTUM` requires p50 hold ≈ <5min and a clock-anchor ≥1 bucket >30% with sign momentum-following; the name is event-themed ("Brexit") and 16:00 UTC has 31.1% of trades, but the hold is 162.55h, not <5min, so the criterion fails by ~6 orders of magnitude. `SWING_TREND_MOMENTUM` requires median hold >72h (✓ 162.55h), top hour <15% (✗ — top hour 16:00 = 31.1%), and H4/D1 trend/momentum features dominating the tree. The H4 features do dominate (rank-10 tree uses ret_3_H4 importance=1.00; ranks 3, 4, 5, 8, 9 are all H4 univariates), but two problems prevent a clean fit: (a) entry timing is clock-anchored to H4 bar opens during London/NY active hours (12/16/20 UTC sum to 85.4% of trades), violating the "no clock anchor" spirit of the provisional; (b) the tree itself is degenerate (CV match-rate 0.482 < always-Buy baseline 0.573 with std 0.225 across 5 folds), so "H4/D1 trend features dominate the tree" is technically true but vacuous — the tree carries no edge to dominate with.

What remains is a system that is multi-day in hold, single-pair (EURGBP), clock-anchored to H4 opens during London/NY, with a name suggesting Brexit-event thematics, and a top candidate rule whose multiple-testing-corrected p-value is 0.087 (out of 510 tests). By Aronson's threshold this rule fails the formal significance gate `[evidence_based_ta, p.183-185]`, and the small sample size (n=103) places the system in the regime where data-mining bias is empirically severe `[evidence_based_ta, p.291, p.315 Fig.6.33]`. López de Prado's argument for closed-enum, consistency-first label spaces `[advances_fin_ml, ch.3, p.78-80]` says the honest action is to mark the system UNCATEGORIZED rather than force-fit a provisional that R1 review would later downgrade. `reason_code = insufficient_evidence` captures this exactly: the fingerprint and candidates do not permit a confident family decision.

I considered `mixed_strategy` (three H4 anchors at 12/16/20 with different Buy% by hour) and `taxonomy_gap` (a hypothetical "SWING_H4_CLOCKED_EURGBP" family). I rejected `mixed_strategy` because the directional split by hour (16:00 → 59.4% Buy, 12:00 → 65.5% Buy, 20:00 → 59.3% Buy) is consistent with one weak Buy bias plus statistical noise on n≈30 per bucket, not two coexisting sub-strategies. I rejected `taxonomy_gap` because proposing a new family requires a coherent strategy outside the enum, and the data here are too weak to assert coherence — the tree is below baseline and only one univariate rule reaches marginal significance. Proposing a new family from a single weak n=103 system would violate the ≥1 system + literature support + provisional review gate `[5R-1-hardening §1]`.

## Rule derivation

The `direction:` field encodes the rank-1 univariate rule from `candidates.json` literally: `ret_10_H1 > -0.00361 ⇒ Buy`. CV match-rate 0.6796, coverage 0.7961, raw p=0.000170, p_corr=0.0870 (510 tests). This rule is essentially "Buy unless the H1 10-bar return is sharply negative" and its lift over the always-Buy baseline (0.5728) is ~10pp — meaningful but not multiple-testing significant. No combination across ranks 3-9 was attempted because all rank ≥3 rules have p_corr ∈ {0.38, 1.0} and would amplify rather than reduce the multiple-testing inflation.

The `entry_window_utc: ["12:00", "20:00"]` covers the three observed H4-bar-open peaks (12/16/20 UTC), which sum to 85.4% of trades. The 00:00 (9 trades) and 04:00 (4 trades) buckets are sparse enough that they may be artifacts of broker timestamping or weekend rollovers — including them would dilute the window without supporting evidence; their direction biases (33% / 25% Buy) are also inverted relative to the day-session clusters, suggesting noise on tiny n.

The `exit:` is descriptive, not prescriptive. 100% of trades exit `manual_or_time` (no SL/TP touch), and the hold distribution is so heavy-tailed (max ≈ 17 months) that I do not assert a time-based cap. Setting `max_holding_hours: 4930.81` records the empirical 95th percentile so downstream tooling has a concrete number, but the replicator should NOT treat this as a hard rule — it is a measurement, not a parameter. Both `take_profit_pips` and `stop_loss_pips` are `null`: there is no evidence in the fingerprint that the live system uses either.

The `sizing: fixed_lot_0.87` reflects lot p50=0.87 with p95/p50=1.03 — essentially constant size, consistent with no martingale and no equity-proportional adjustment. (Equity grew ~3.6× over the period while lots stayed flat — implying fixed-USD risk per trade, not fixed-fraction-of-equity.)

## Confidence breakdown

- Family identification: **0.30** — UNCATEGORIZED is the honest call given hold disqualifies all intraday families and provisionals each fail a hard criterion (Gold; <5min; clock-anchor + degenerate tree). Confidence is not lower because the elimination logic itself is solid; not higher because the residual hypothesis space (taxonomy_gap candidates) is non-empty and we cannot rule it out.
- Direction rule: **0.25** — Rank-1 univariate p_corr=0.087 is marginal at best and the tree is below baseline. Replicator will likely produce a noisy backtest with low edge.
- Exit logic: **0.20** — `manual_or_time` only tells us SL/TP didn't fire; the 17-month max hold makes any time-based cap arbitrary.
- Sizing: **0.80** — lot p95/p50 = 1.03 is robust evidence of a flat-lot regime.
- Overall: **0.30** (weighted toward family/direction since exit/sizing are downstream of the family decision; sizing high but doesn't compensate for the structural family/direction uncertainty).

## Open questions (for Stage 3 + later)

- Is the live bot calendar-aware (Brexit / UK news releases / EUR-zone events) despite no calendar feature being observable in OHLC-only fingerprint? The replicator must not assume so; flag as a known unmodelable factor for any cross-validation result interpretation.
- Why does the system close at all if hold can reach 17 months? Hypothesis: discretionary or external close (vendor-side intervention), broker-side stop-out via margin call at 1:500 leverage, or hidden very-wide TP. None can be confirmed without per-trade exit-reason metadata.
- Could this system actually be a long-only EURGBP positional bias dressed up with an H4 momentum filter? 57.3% Buy with weak ret_10_H1 filter and multi-month hold is consistent with that. Worth a baseline of "always-buy EURGBP, time-stop at p95 hold" in the comparator (5R-1-hardening Wave C baseline-expansion item).
- ForexMart at 1:500 leverage with 34.93% drawdown on $2k deposits is a high-leverage retail venue; vendor selection bias is plausible. This argues against treating any backtest match as endorsement absent extensive replication.
- If R1 ever surfaces a 2nd EURGBP-only multi-day H4-clocked system, revisit whether a new provisional family ("SWING_H4_CLOCKED" or similar) is justified. Alone, n=1 is not enough — `[5R-1-hardening §1]` requires user approval + literature support + at least 1 supporting system with citation.
- Single-block OOS feasibility: n=103 over 2022-2026; even an 80/20 split yields ~21 OOS trades — far below any robust gate threshold. System is structurally under-powered regardless of decoded rule.
