---
system_id: 9841939
family: UNCATEGORIZED
confidence: 0.65
reason_code: degenerate
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]   # no clock-anchor; top hour 17 UTC is only 10.3% of 4000 trades
  pairs: [EURCHF]
  direction: |
    # CLASSIFIER DEGENERATE — no executable direction rule recoverable.
    # Evidence (candidates.json + fingerprint.md):
    #   - Always-Sell baseline match_rate_cv = 0.504
    #   - RIPPER rank-1 match_rate_cv = 0.506 (Δ=0.002, fold std=0.008)
    #   - DecisionTree rank-3 match_rate_cv = 0.496 (BELOW baseline)
    #   - All 7 univariate rules: p_value_corrected = 1.000 (n_tests=528, Bonferroni)
    #   - Empirical Buy share = 49.6% (perfectly balanced; no directional bias by pair or by hour)
    #
    # The rank-1 RIPPER rule is reproduced verbatim for audit only;
    # the replicator MUST treat this system as direction-blind and delegate
    # ranking to lift-over-baseline tests (always_sell + random_frequency_matched
    # + permutation), per 5R-1-hardening Wave C item 2.
    #
    # Verbatim rank-1 RIPPER (audit copy, not for production direction):
    # BUY if (ema_dist_20_M1 in [0.30, 0.66]
    #         AND prior_bar_sign_M15 == 1.0
    #         AND ret_3_M5 in [6.5e-05, 1.5e-04]
    #         AND atr_ratio_M1 in [0.074, 0.087])
    # SELL otherwise
    NONE  # no validated direction rule
  exit:
    max_holding_hours: 730   # p95 hold = 726.25h (~30 days); p50 = 22.09h, max = 1481h (~62 days)
    take_profit_pips: null   # not recoverable from track record
    stop_loss_pips: null     # not recoverable from track record
  sizing: fixed_lot_0.93     # lot p50=0.93, p95/p50=1.01 (near-constant; no martingale, no vol-targeting)
citations:
  - "[evidence_based_ta, p.407-408] — 'Do not use rules from prior research by others without knowing how many rules that author tested (data-snooping bias). Prefer building the rule universe by combinatorial enumeration of parameters defined a priori.' — applies inversely here: 528 rules were tested by Stage 1 miners, 0 cleared Bonferroni (all p_corrected = 1.000)."
  - "[advances_fin_ml, p.208-211] — 'Estimate PBO via CSCV before finalizing any strategy. A PBO > 0.5 means the strategy is more likely overfit than valid.' — when in-sample top rule sits 0.002 above baseline with fold std 0.008, the implicit PBO is essentially 1.0; classifying as a positive family would be overfit attribution."
  - "[advances_fin_ml, ch.3] — label consistency: 'forced labels degrade downstream validation' — UNCATEGORIZED is the honest label here; choosing a positive family on noise would contaminate the ranking baselines."
risk_flags:
  - "DIRECTION UNRESOLVABLE: best candidate (match_rate_cv=0.506) is within 0.002 of Always-Sell baseline (0.504); fold std=0.008 swamps the signal; tree CV (0.496) is below baseline."
  - "HOLD DISTRIBUTION DOES NOT FIT ANY FAMILY POST-R4: p50=22.09h disqualifies all sub-day intraday families (LATE_NY_BREAKOUT, OVERLAP_NY_LONDON_RANGE, NY_SESSION_REVERSAL, FACTOR_SCALPING, LONDON_OPEN_*, NEWS_RELEASE_MOMENTUM) AND fails the SWING_TREND_MOMENTUM provisional gate (requires p50 > 72h; 22.09h < 72h). p95=726h tail (~30d) shows multi-day positions exist but are not the modal regime."
  - "NO CLOCK ANCHOR: top entry hour (17 UTC) is only 10.3% of 4000 trades; entries are distributed across at least 5 sessions (17, 10, 15, 00, 11) with all top hours <11%. Fails NEWS_RELEASE_MOMENTUM threshold (>30% in one bucket)."
  - "EURCHF tail risk: SNB peg removal (Jan 2015) caused ~15-30% gap in minutes; 1:500 leverage on a single quasi-pegged cross has catastrophic exposure to a repeat policy event. Training window 2025-04-10 to 2026-05-01 contains no analogous shock."
  - "ForexMart broker: offshore retail, non-Tier-1 regulated; vendor selection bias — 'Real (USD)' track is publishable but unverifiable independently."
  - "Headline gain inflation: gain +1,008.45% vs absolute_gain +47.42%; balance moves driven by $37k deposits / $36k withdrawals; true return is ~47% over ~13 months, modest at this leverage."
  - "Single pair EURCHF: zero cross-pair diversification; entire P&L hostage to one quasi-pegged instrument regime."
  - "Stage 3 advisory: replicator should treat this system as a NULL ENTRY in lift-over-baseline ranking (5R-1-hardening Wave C item 2). Direction-blind replication will at best match always_sell baseline."
---

# Decoded signal — Happy Power FM (id 9841939)

## Family rationale

This system is classified `UNCATEGORIZED` with `reason_code: degenerate` because every Stage 1 rule miner collapses to the always-sell baseline:

- **Always-Sell baseline**: `match_rate_cv = 0.504` (rank 2 in candidates.json).
- **RIPPER rank-1**: `match_rate_cv = 0.506` (Δ = +0.002 over baseline; fold std = 0.008, so the signal is buried inside fold-to-fold noise — fold accs span 0.497-0.518).
- **DecisionTree rank-3**: `match_rate_cv = 0.496` — *below* baseline.
- **All 7 univariate rules**: `p_value_corrected = 1.000` (n_tests = 528 with Bonferroni). None of them survive multiple-testing correction.

Per Aronson `[evidence_based_ta, p.407-408]`, exhaustive rule mining without significance correction generates apparent edges that vanish under proper multiple-testing accounting: in his case study, 6,402 rules tested, 0 significant after WRC. Stage 1 here ran 528 rules and got the same outcome — none significant, top survivor is 0.002 above always-sell. This is the textbook signature of `degenerate` per the taxonomy contract: "tree/ripper colapsa para always-Buy/Sell baseline (CV ≈ baseline)" (`shared/decoder_taxonomy.py` UncatReason.DEGENERATE).

I considered every closed-enum family before settling on UNCATEGORIZED:

- **LATE_NY_BREAKOUT**: requires entry concentrated 21-01 UTC. Top hours here are 17 (10.3%), 10 (8.5%), 15 (7.8%), 00 (7.3%), 11 (6.7%); 00 UTC is on the edge of the band but only 7.3%, and the cluster is dispersed. **Fail.**
- **LONDON_OPEN_MOMENTUM / LONDON_OPEN_MR**: require 06-09 UTC peak. Hour 06-09 does not appear in top 5; top is 17 UTC. **Fail.**
- **NY_SESSION_REVERSAL**: 12-16 UTC peak with directional sign opposite the London move. Hours 15 and 17 are present but buy_pct at hour=15 is 48.9% and hour=17 is 49.4% (no directional bias). Family also flagged "vazia pós-Wave 1+2+3 — usar com cuidado". **Fail.**
- **OVERLAP_NY_LONDON_RANGE**: 12-16 UTC + range/BB position rule. No range-position univariate clears correction (`range_norm_M1 > 0.6222 ⇒ Sell` has p_corrected = 1.000). Top hour 17 is outside the 12-16 window. **Fail.**
- **OVERNIGHT_GAP_FADE**: max_gap_days = 3.7 is consistent with normal weekend inactivity, not a Friday/Monday cluster. **Fail.**
- **FACTOR_SCALPING**: requires `hold p50 < 0.5h` confirmed post-R4. Post-R4 hold p50 = **22.09h** — two orders of magnitude above the threshold. The previous v2 frozen rule classified this as FACTOR_SCALPING when hold was NaN; that classification is invalidated by R4 (`_diagnostics/5R-1-hardening.md` §R4). **Hard fail.**
- **MARTINGALE_GRID**: martingale flag PASS, lot ratio p95/p50 = 1.01, max_streak = 0. **Correctly excluded.**
- **H1_MOMENTUM_GOLD** (provisional): pair is EURCHF, not Gold/XAU. **Fail.**
- **NEWS_RELEASE_MOMENTUM** (provisional): requires ≥1 hour bucket with >30% trades + name flag. Top hour is 10.3%; system name is "Happy Power FM", no NEWS flag. **Fail.**
- **SWING_TREND_MOMENTUM** (provisional): requires hold p50 > 72h + top hour <15% + H4/D1 trend/momentum features dominant. Top hour < 15% ✓; H4 features present (ret_3_H4 = 0.10 importance) but tree is dominated by **M1/M5** features (ret_1_M1=0.28, ret_1_M5=0.13, ret_3_M1=0.13) with H4/D1 secondary; and **hold p50 = 22.09h, far below the 72h gate.** **Fail.**

The system fits no family in the closed enum. `reason_code: degenerate` is preferred over `taxonomy_gap` because the issue is not a coherent strategy outside the enum — it is the absence of an extractable rule, the textbook degenerate condition. `hold_mismatch` was rejected as second-best because no positive family was ever attributable in the first place; one cannot mismatch what was never matched. `mixed_strategy` was considered (entries spread across 5 sessions) but rejected because the distribution is closer to uniform-noise than to two distinct strategy peaks — a real mixed system would show ≥2 hour buckets each above ~15%.

## Rule derivation

There is no validated direction rule. The `direction:` field is `NONE`. The verbatim RIPPER rank-1 thresholds are reproduced in a comment block for audit only — they are not for production execution. Per López de Prado `[advances_fin_ml, p.208-211]`, when in-sample top performance sits within 1 fold standard deviation of the baseline, the implicit PBO is essentially 1.0 and any positive attribution is overfit.

The exit logic uses the empirical hold distribution as a soft cap: `max_holding_hours = 730` reflects the p95 (726.25h ≈ 30 days). This is not a strategy parameter — it is a guard so the replicator does not attempt to hold positions for the 1481h (~62 day) maximum tail observed in the track. TP/SL pips are not recoverable from the track record.

Sizing is `fixed_lot_0.93` because lot p50 = 0.93 with p95/p50 = 1.01 (near-constant). No martingale (steps = 0, max_streak = 0). No vol-targeting (sizing does not respond to ATR or equity).

## Confidence breakdown

- Family identification (UNCATEGORIZED): **0.85** — the degeneracy evidence is unambiguous (RIPPER 0.506, baseline 0.504, tree 0.496 below baseline, all univariate p_corrected = 1.000). High confidence that no enum family applies.
- Reason code (degenerate): **0.80** — fits the contract definition exactly. `mixed_strategy` was the only competing option but distribution looks closer to uniform-noise than to multi-peak.
- Direction rule: **N/A** — `NONE` returned; classifier degenerate.
- Exit logic: **0.40** — `max_holding_hours = 730` is a soft cap from p95, not a recovered system parameter; TP/SL unknown.
- Broker/data quality penalty: **-0.10** applied (ForexMart offshore, non-Tier-1, vendor track).
- Overall: **0.65** = weighted toward the strong degeneracy diagnosis, penalized by exit-logic uncertainty and broker quality.

## Open questions (for Stage 3 + posteriores)

- **Lift-over-baseline mandatory**: Stage 3 must report this system's match rate against `always_sell`, `random_frequency_matched`, and `permutation_test` (5R-1-hardening Wave C item 2). If lift over always-sell is ≤ 0.005 with bootstrap 99% CI crossing zero, the system has no edge and should drop out of the primary ranking.
- **Calendar-aware replication**: not flagged here (no NEWS flag, no clock anchor, hold p50 = 22.09h ≫ 5min). Skip live calendar lookup; rely on observed trade timestamps only.
- **Hold-time bimodality**: p50 = 22.09h, p95 = 726h, max = 1481h. Stage 3 should plot the hold histogram — if there are two distinct modes (e.g., a sub-24h cluster + a multi-day tail), this might flip from `degenerate` to `mixed_strategy` (two sub-strategies coexisting). Currently insufficient evidence for that switch, but it is the natural follow-up.
- **EURCHF peg risk monitor**: even though the training window contains no SNB shock, any reliability replicator must include a circuit-breaker (halt if spread > 10× normal or single-bar equity drop > 20%) — `[carver_systematic_trading]` p.142-143 documents the 2015 event consequences for leverage > 7×.
- **Provisional-family review trigger**: this system does not contribute n=2 support to any provisional family. R1 review of `H1_MOMENTUM_GOLD`, `NEWS_RELEASE_MOMENTUM`, `SWING_TREND_MOMENTUM` does not change as a result of this system.
- **Frozen-rule update**: the v2 frozen_rule classified this system as FACTOR_SCALPING (pre-R4, NaN hold). R1 should overwrite to UNCATEGORIZED + reason_code=degenerate. CHANGELOG.md must record SHA pre/post and link back to this file.
