---
system_id: 9375654
family: OVERLAP_NY_LONDON_RANGE
confidence: 0.55
generated: 2026-05-02
rule:
  entry_window_utc: ["13:00", "17:00"]
  pairs: [XAUUSD]
  direction: |
    # Decision tree (max_depth=4) — top features by MDI:
    #   bb_pos_20_2_H1 (0.75), ret_3_H1 (0.13), ema_dist_20_H1 (0.06),
    #   ret_10_H1 (0.05), ema_dist_20_M5 (0.01).
    # Translated literally from candidates.json rank 1 (CV match=0.867±0.040,
    # coverage=1.0). The split at bb_pos_20_2_H1=-0.16 partitions the H1
    # Bollinger envelope into "lower-half" vs "rest"; secondary splits use
    # H1 momentum to refine direction within each partition.
    BUY if (bb_pos_20_2_H1 <= -0.16 AND ret_3_H1 <= 0 AND ret_10_H1 > -0.01)
    BUY if (bb_pos_20_2_H1 >  -0.16 AND ema_dist_20_H1 <= 0.63 AND ret_3_H1 <= 0)
    BUY if (bb_pos_20_2_H1 >  -0.16 AND ema_dist_20_H1 >  0.63)
    SELL otherwise
    # NONE if outside entry_window_utc.
  exit:
    max_holding_hours: 4
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[algo_trading_chan, p.71-73, ch.3] — Bollinger Band pairs strategy: BB position is the canonical directional gate for mean-reversion entries; bb_pos_20_2_H1 dominating MDI here (0.75) maps onto the same primitive."
  - "[advances_fin_ml, p.160-164] — Mean Decrease Impurity (MDI): 'in-bag feature importance measure based on weighted average impurity reduction across all splits'; bb_pos_20_2_H1 MDI=0.75 is far above the next feature (0.13), satisfying López de Prado's single-feature-dominance regime where MDI is reliable rather than noisy."
  - "[evidence_based_ta, p.264-271] — Multiple Comparison Procedure / data-mining bias: with 516 univariate tests and tree depth-4 + RIPPER 18 conjunctions on n=915, the observed match_rate is positively biased; replicator must validate on a single-block OOS window."
risk_flags:
  - needs_m1_review
  - calendar_aware_replication_risk_15_30_utc
  - cross_asset_gold_only_family_originally_fx
  - vendor_selection_bias_happyforex_tmgm
  - secondary_morning_cluster_09_11_utc_unmodeled
  - hold_p50_zero_anomalous_for_range_fade
---

# Decoded signal — Happy Gold - TMGM (M30) (id 9375654)

## Family rationale

Post-R4 fingerprint (hold-extraction NaN bug fixed) gives a much sharper picture than the v2-era classification:

- **Timing.** Top entry hours UTC: 15 (126 trades), 16 (123), 17 (86), 10 (72), 9 (63). The 15-17 cluster holds 335/915 = 36.6% of trades. The 5-min granular peak is **15:30 UTC** with 42 trades (~4.6%, ≈2× the next bucket). This sits at the late edge of the canonical NY/London overlap (13-16 UTC) plus the post-overlap NY-only hour 17.
- **Hold (post-R4 corrected).** p50 = **0.00 h**, p95 = **0.11 h** (~6.6 min), max = **2.14 h**. Exit kind 100% `manual_or_time`. This is intraday with extremely fast exits — far shorter than typical "session range fade" reversion windows (1-3 h), but consistent with a tight TP or fast time-stop applied to BB-position entries.
- **Direction.** Decision tree (rank 1, CV match 0.867 ± 0.040, full coverage) is overwhelmingly driven by `bb_pos_20_2_H1` (MDI = 0.75). Secondary features are H1 returns and H1 EMA distance. Two independent miners (univariate rank 4: `bb_pos_20_2_H1 > 0.1209 ⇒ Buy`, CV 0.860, p_corr 5.9e-114) recover the same primary feature on the same timeframe — strong cross-method agreement that BB position on H1 is the true directional anchor.

Mapped against `decoder_taxonomy.Family` (closed enum):

| Family | Fit | Reason |
|---|---|---|
| `OVERLAP_NY_LONDON_RANGE` | **best fit** | Criterion: "Entry 12-16 UTC, BUY/SELL determinado por posição na BB ou range, exit time-based." Timing 15-17 UTC overlaps the 12-16 window's late tail; bb_pos dominates direction; exit_kind = manual_or_time. |
| `LATE_NY_BREAKOUT` | rejected | Requires 21-01 UTC peak; observed peak is 15-17. |
| `LONDON_OPEN_MOMENTUM` / `LONDON_OPEN_MR` | rejected | Require 06-09 UTC peak; only a secondary 09-11 cluster (~22%) here, dominated by the afternoon cluster. |
| `NY_SESSION_REVERSAL` | rejected | Empty post-Wave 1+2+3 of 5R-0; also direction is not "opposite to London move" — bb_pos drives direction without a London-move sign reference. |
| `OVERNIGHT_GAP_FADE` | rejected | No Friday/Monday concentration in the trade timestamps. |
| `FACTOR_SCALPING` | rejected | Hold p50 = 0 satisfies the <30 min sub-criterion, but the family requires *distributed* entry timing. Here entries cluster sharply at 15-17 UTC. |
| `MARTINGALE_GRID` | rejected | Sanity flag PASS; lot p95/p50 = 2.28; max_streak = 0. |
| `H1_MOMENTUM_GOLD` (provisional, n=1, 6541963) | runner-up | Asset XAUUSD ✅; tree balanced ✅; dir_acc 0.867 > 0.7 ✅. But the dominant H1 feature here is `bb_pos` (a range/MR indicator, MDI 0.75), not pure momentum (`ret_3_H1`+`ret_10_H1` combined MDI ≈ 0.18). decoder.md prefers the family with stronger literary support — `OVERLAP_NY_LONDON_RANGE` (BB-position fade, Aronson+Chan) over `H1_MOMENTUM_GOLD` (provisional, n=1, no second supporter). |
| `NEWS_RELEASE_MOMENTUM` (provisional) | rejected | Per task req #8: classify only from observed evidence. The 15:30 5-min peak holds only ~4.6% of trades — far below the >30% single-bucket criterion. System name is "Happy Gold TMGM (M30)", **not** "Happy News". The 15:30 / 10:30 ET coincidence with US data releases is a *replication risk* (see risk_flags), not an established family signature. |
| `SWING_TREND_MOMENTUM` (provisional) | rejected | Requires median hold >72 h; observed p50 = 0 h. |
| `UNCATEGORIZED` | rejected | Family identification has positive evidence on three independent axes (timing, feature dominance, exit kind). The pattern is coherent enough that `taxonomy_gap` would not be honest, and `mixed_strategy` is dispreferred because the morning cluster is dispersed (no second sharp peak inside it). |

## Rule derivation

The rank-1 tree (depth-4, CV match 0.867 ± 0.040 across 5 folds: 0.81 / 0.83 / 0.87 / 0.92 / 0.92) is the highest-quality candidate and is encoded literally in the `direction:` block. Three reasons to prefer the tree over univariates:

1. **Two independent miners agree** on `bb_pos_20_2_H1` as the primary directional feature: tree gives MDI 0.75; univariate rank 4 hits match 0.860 with p_corr 5.9e-114 on a threshold (0.12) close to the tree's split (-0.16). Per `[advances_fin_ml, p.160-167]`, agreement across MDI and SFI-style probes is the standard for treating a feature as causal rather than substitution-effect.
2. **Tree handles the lower-band exhaustion pocket** (`bb_pos ≤ -0.16 AND ret_3_H1 ≤ 0 AND ret_10_H1 > -0.01 ⇒ BUY`) that the rank-4 univariate would mis-label as SELL. This pocket is small but observable and consistent with a "fade after small downside exhaustion" sub-rule.
3. **RIPPER (rank 2, 18 conjunctions, CV 0.825) was rejected** as a secondary source — it relies on `close_vs_session_open_*` whose anchor depends on which session-open the replicator uses, introducing reproducibility ambiguity. The tree uses anchor-free features only.

`entry_window_utc` is set to `[13:00, 17:00]` to bracket the dominant cluster plus the 13-14 lead-in that RIPPER's clause 11 (`hour_utc=13.0-15.0`) explicitly references. The 09-11 UTC secondary cluster (~22% of trades) is intentionally **not** modeled — see Open Questions.

`max_holding_hours: 4` is a hard backstop above the observed `max = 2.14 h`. p95 = 0.11 h means the typical exit is much faster, suggesting either a tight TP or a synchronous time-cap not visible from the public track. The replicator must sweep TP/SL pip levels because manual_or_time exits don't expose them.

`proportional_equity_2pct` is the conservative interpretation of lot p95/p50 = 2.28 over a 4.4-year track with 21 deposits — consistent with risk-fraction sizing scaling on equity (no martingale per sanity gate).

## Confidence breakdown

- **Family identification: 0.55** — `OVERLAP_NY_LONDON_RANGE` is the best closed-enum fit on timing + feature-dominance + exit-kind. Penalties: (a) asset is XAUUSD (Gold), while the family's two existing supporters were FX-tilted in description (criterion does not strictly forbid Gold but the literary anchor for "BB position fade in NY/London overlap" is FX); (b) p50 hold = 0 is anomalous for traditional range-fade semantics — typical range-MR entries hold for 1-3 h to let reversion play out, not seconds; (c) 15:30 UTC peak coincides with US data releases — possible calendar-driven entry that the family criterion does not model.
- **Direction rule: 0.65** — tree CV 0.867 ± 0.040 is strong; cross-method agreement on `bb_pos_20_2_H1` is strong. Penalty: with 56 features × depth-4 tree on n=915, MCP/MDI bias is non-trivial `[evidence_based_ta, p.264-271]`. Threshold values may not generalize ±10%.
- **Exit logic: 0.40** — exit_kind = manual_or_time on 915/915 trades, p50 = 0 h, p95 = 0.11 h. The `max_holding_hours = 4` backstop is conservative but TP/SL pips are unrecoverable from the public track; replicator must sweep.
- **Overall: 0.55** = weighted (0.4·0.55 + 0.4·0.65 + 0.2·0.40).

## Open questions (for Stage 3 + posteriores)

- **Sub-M5 timing sensitivity (`needs_m1_review`).** Hold p50 = 0.00 h, p95 = 6.6 min, max = 2.14 h. A replicator running on M5 OHLC will likely miss intra-bar fills/exits; on M15+ frames the system is unreplicable in fidelity. Per task req #9 this is flagged but the project timeframe is unchanged.
- **15:30 UTC peak / US data release window (`calendar_aware_replication_risk_15_30_utc`).** 15:30 UTC = 10:30 ET coincides with multiple US scheduled releases (EIA crude, weekly economic data) that move Gold sharply. The system name does not flag NEWS, so per task req #8 the family is decided from observed trade evidence only (BB-position fade fits the closed enum). However, replicator must check whether match-rate on the trade log is artificially boosted by post-release liquidity moves — a non-calendar-aware replication may underperform live track on release days, or fit too loosely on non-release days.
- **Hold p50 = 0 anomaly for "range fade".** Stage 3 should test whether the system is actually (a) BB-position fade with a tight 5-10 pip TP (consistent with manual_or_time + fast exits), or (b) a stop-and-reverse pattern at session-open anchors (RIPPER references `close_vs_session_open_M1/M5/M15/H1/H4=1.0` heavily). If (b), family may need downgrade to `UNCATEGORIZED + reason_code=mixed_strategy`.
- **Secondary cluster 09-11 UTC (~22% of trades) is unmodeled.** Stage 3 should test (i) widening window to `[09:00, 17:00]`, (ii) fitting a separate sub-rule for the morning cluster, (iii) accepting the discrepancy. If two distinct sub-strategies are needed, downgrade to `UNCATEGORIZED + reason_code=mixed_strategy`.
- **Tree threshold sensitivity.** With 5-fold CV on n=915, residual selection bias on threshold values is real. Replicator should sweep `bb_pos_20_2_H1` split ∈ {-0.30, -0.20, -0.16, -0.10, 0.00, +0.12, +0.20} and report match-rate stability.
- **Cross-asset extension of `OVERLAP_NY_LONDON_RANGE`.** This is the first XAUUSD-only entry into a family whose canonical members are FX. If R1 produces only this Gold case, taxonomy review should consider (a) keeping the family asset-agnostic with a Gold sub-tag, or (b) splitting into `OVERLAP_NY_LONDON_RANGE_FX` vs `OVERLAP_NY_LONDON_RANGE_METALS`. Per 5R-1-hardening §1, "≥1 system + citation + user approval" is required for new family creation; this is one system and a literature anchor exists, so a future user-decision could split the family.
- **R4 caveat (fingerprint surgical patch).** Per `_diagnostics/5R-1-hardening.md` §R4, fingerprint hold values were patched in-place but Stage 1 was not re-executed. `candidates.json` was not regenerated post-R4 — features in the tree/RIPPER are OHLC-derived and independent of duration, so this is unlikely to affect the decode, but flagged for completeness.
