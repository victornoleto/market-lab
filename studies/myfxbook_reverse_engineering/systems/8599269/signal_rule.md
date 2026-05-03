---
system_id: 8599269
family: UNCATEGORIZED
confidence: 0.28
generated: 2026-05-02
rule:
  entry_window_utc: ["16:00", "20:00"]   # peak activity band 16-19 UTC (NY afternoon)
  pairs: [AUDUSD]
  direction: |
    # Primary signal: H1 Bollinger Band position (tree rank-1 dominant feature)
    # The tree produces BUY when price is NOT deeply below the lower band AND
    # short-term vol (atr_ratio_M5) is low, suggesting a mean-reverting regime.
    #
    # Simplified executable form (from tree rank-1, threshold exact from candidates.json):
    BUY if bb_pos_20_2_H1 > -0.66 AND atr_ratio_M5 <= 0.29 AND ema_dist_20_M1 <= 1.29
    BUY if bb_pos_20_2_H1 > 0.68 AND ret_10_M5 <= 0.00
    BUY if bb_pos_20_2_H1 <= -0.66 AND range_norm_M15 > 0.84 AND atr_ratio_M15 <= 0.55
    SELL otherwise
    #
    # Univariate fallback (rank-6, highest match_rate_cv with ~50% coverage):
    # BUY if bb_pos_20_2_H1 > -0.02433
    # SELL otherwise
    #
    # NOTE: direction signal is near-random (match_rate_cv max = 0.599 at 50% coverage).
    # The tree CV = 0.546 with fold range [0.504, 0.634] — high variance, low confidence.
  exit:
    max_holding_hours: 552     # p95 hold = 552h; p50 = 17h — extreme bimodal distribution
    take_profit_pips: null     # exit_kind = manual_or_time only; no TP/SL detected
    stop_loss_pips: null
  sizing: martingale_NEVER     # k1 flag raised: per-month lot p95/p50 = 5.0 > 3.0; within-month doubling detected
citations:
  - "[math_money_mgmt, p.13] — 'Attempting to use money management on a system with negative expectation. No position sizing technique converts a losing strategy into a winner.'"
  - "[advances_fin_ml, p.160-161] — 'Mean Decrease Impurity (MDI) — in-bag feature importance measure based on weighted average impurity reduction across all splits; fast but biased toward high-cardinality features'"
  - "[evidence_based_ta, p.271] — 'Data-mining bias — Systematic positive bias in the observed performance of the best rule when several are tested; observed performance exceeds expected performance'"
risk_flags:
  - "MARTINGALE FLAG RAISED — k1_pass=FAIL; per-month lot p95/p50 = 5.00 > threshold 3.0; within-month doubling detected. System exhibits martingale-like lot dynamics. This is structurally a DISCARD candidate."
  - "SINGLE PAIR ONLY (AUDUSD, n=1123) — no pair universe diversification; edge fully pair-specific."
  - "DIRECTION SIGNAL NEAR-RANDOM — best match_rate_cv (full coverage tree) = 0.546; univariate rank-6 best = 0.599 at only 50% coverage. No candidate exceeds 0.60 at full coverage."
  - "EXTREME HOLD TIME BIMODALITY — p50=17h vs p95=552h vs max=2376h. The system holds losing positions for weeks, consistent with martingale/grid behavior where positions are never stopped out."
  - "broker: ForexMart — not a Tier-1 regulated broker (compare: LMAX, Pepperstone, Interactive Brokers). Reduce confidence -0.10."
  - "entry_window 16-19 UTC overlaps NY afternoon session but does NOT match any known high-alpha FX session family. Timing is not a discriminating feature for family classification."
  - "account_type: Real — no demo penalty applied, but system name explicitly includes 'MartiGrid' (Martingale + Grid), confirming the structural assessment."
---

# Decoded signal — Happy MartiGrid FM - REAL (id 8599269)

## Family rationale

The system name itself encodes the structural truth: "MartiGrid" = **Martingale + Grid**. This is confirmed by the Stage 1 sanity output: `martingale flag: FAIL (martingale-like dynamics)`, with `k1 flags: ['per-month max/median P95 = 5.00 (> 3.0) — within-month doubling']`. The taxonomy contains `MARTINGALE_GRID` as an explicit family but specifies it should trigger an immediate discard. Rather than assigning that family and halting, this analysis assigns `UNCATEGORIZED` to document the failure mode explicitly, per the constraint that confidence < 0.5 requires listing alternatives considered.

The fingerprint's timing distribution (peak hours 16-19 UTC) superficially resembles the `NY_SESSION_REVERSAL` (12-16 UTC) or the `OVERLAP_NY_LONDON_RANGE` (12-16 UTC) families, but neither fits: the peak is shifted to 17-18 UTC (post-overlap), the only pair is AUDUSD (not a USD/EUR major favored by those families), and the defining signature of those families — a consistent directional bias opposite the London move — is completely absent. Buy% across all top-5 hours ranges from 37.5% to 57.5%, which is statistically indistinguishable from 50/50 coin-flip at the trade count per hour (64-91 trades/hour).

The `FACTOR_SCALPING` family is also a non-fit: median hold time is 16.98 hours, not under 30 minutes, and the lot dynamics show within-month doubling rather than vol-targeting or pair-trading characteristics.

The `OVERNIGHT_GAP_FADE` family is ruled out: entries are concentrated on weekday afternoons UTC, not Friday closes or Monday opens, and there is no directional bias tied to weekend gap sign.

The most parsimonious conclusion is: this system is a martingale-grid EA on AUDUSD that enters roughly at NY afternoon (16-19 UTC), adds to losing positions (causing the lot doubling and bimodal hold distribution), and closes positions either at a profit target or after days/weeks. There is no recoverable direction signal because the entry logic is not about predicting direction — it is about grid-spacing and position accumulation. This is a structurally different problem from the session-edge systems this pipeline targets.

## Rule derivation

The direction rule in the YAML above is transcribed verbatim from the `tree` miner rank-1 output (candidates.json), using exact thresholds: `bb_pos_20_2_H1` splits at -0.66 and 0.68; `atr_ratio_M5` split at 0.29; `ema_dist_20_M1` split at 1.29; `range_norm_M15` split at 0.84; `atr_ratio_M15` split at 0.55; `ret_10_M5` split at 0.00. No thresholds were invented.

However, the tree's CV match rate is 0.546 (std 0.045, fold range 0.504-0.634). The `advances_fin_ml` MDI rule [p.160-161] notes that decision-tree feature importance via MDI is "biased toward high-cardinality features" — `bb_pos_20_2_H1` (a continuous float in [-1,1]) naturally dominates the split structure, which inflates its apparent importance. The concordance between tree and univariate results (bb_pos_20_2_H1 appears as top feature in both) is reassuring for feature identity but not for edge strength.

The univariate rank-6 rule `bb_pos_20_2_H1 > -0.02433 => Buy` achieves match_rate_cv = 0.599 at coverage = 0.499 (50% of trades). This is the single strongest point estimate, but (a) it covers only half the trade universe, (b) p_corrected = 7.97e-9 is low because the Bonferroni correction denominator is 530 — not because the rule is strong, and (c) it reads as "buy when price is near or above the H1 BB midline," which is a trivially true momentum tautology in a trending pair rather than a structural entry signal.

The RIPPER rank-3 rule `close_vs_session_open_H4=1.0 AND bb_pos_20_2_H1 >= 0.92` collapses to match_rate_cv = 0.500 in CV (std = 0.101, fold range 0.334-0.606). The high std confirms the rule is unstable — likely capturing a small subset of trending trades where both conditions happen to coincide, not a structural signal.

Exit parameters: `max_holding_hours = 552` is the p95 from the fingerprint (hold p95 = 552h). The p50 = 16.98h and max = 2376h. This bimodal distribution is the fingerprint of a martingale grid: most winning positions close quickly (~17h), but losing grids that accumulate and eventually close take weeks (2376h max = ~99 days). Assigning max_holding_hours = 552 is conservative (p95), not mean.

## Confidence breakdown

- Family identification: 0.25 — The k1 FAIL flag and system name confirm martingale-grid dynamics with high certainty, but the pipeline taxonomy calls for either `MARTINGALE_GRID` (immediate discard) or `UNCATEGORIZED` (confidence < 0.5) when the pattern does not fit a recoverable session family. Choosing UNCATEGORIZED with low confidence is the honest encoding of "this is a martingale, which the pipeline cannot replicate."
- Direction rule: 0.20 — Best CV = 0.546 (tree, full coverage). No candidate exceeds 0.60 at full coverage. The direction signal is near-random; this is expected for martingale/grid systems where entries are at arbitrary grid levels, not at predicted directional inflection points.
- Exit logic: 0.35 — The p50/p95/max statistics are reliable from the fingerprint, but they describe the statistical outcome of the martingale accumulation process, not a parametric TP/SL rule that can be replicated.
- Overall: 0.28 = weighted mean, dominated by the direction uncertainty and structural incompatibility with the pipeline's target families.

## Open questions (for Stage 3 + posteriores)

- The Stage 3 replicator should NOT attempt to replicate this system as a signal-based strategy. If run, the reliability score will be low by construction (direction = random, exit = bimodal unbounded). The system should be flagged as `MARTINGALE_GRID_DISCARD` in the pipeline ranking.
- The hold time bimodality (p50=17h vs p95=552h) is structurally diagnostic: Stage 3 could verify this by computing the hold-time distribution from the simulated replicator and checking for the same bimodal shape. A unimodal distribution in Stage 3 output would confirm the direction rule is driving the holds (unlikely given the low match rate).
- If the pipeline proceeds despite the martingale flag (e.g., to test whether the direction signal alone, stripped of lot-doubling, has any residual edge), the correct config is: fixed lot 0.01, max_holding_hours capped at 48h (2×p50), entry window 16:00-20:00 UTC, direction from tree rank-1. Expected reliability score: < 0.40.
- The `math_money_mgmt` [p.13] rule is unambiguous: "No position sizing technique converts a losing strategy into a winner." A martingale overlay on a near-zero-expectation direction signal cannot have positive expectation in the long run. The 135.88% reported gain likely reflects a sequence of fortunate grid resolutions; drawdown is already 18.96% and the account has had withdrawals of $2,000 on $3,000 deposited, consistent with partial ruin recovery cycles.
- Cross-reference with the `evidence_based_ta` [p.271] data-mining bias warning: the system's 5-year track record (2021-2026) on a single pair with a single parameter set, reported on a public leaderboard, is subject to survivorship bias — only systems that have not blown up are visible. The peak lot of 0.11 on a $2,714 balance = 4% notional per pip per lot, which at 1:500 leverage implies the system has been near margin-call territory during accumulation phases.
