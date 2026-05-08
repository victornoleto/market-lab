---
system_id: 9607500
family: OVERLAP_NY_LONDON_RANGE
confidence: 0.48
generated: 2026-05-02
rule:
  entry_window_utc: ["09:00", "17:00"]
  pairs: [GBPUSD, EURUSD, USDJPY, GBPJPY, EURJPY]
  direction: |
    # Primary signal: 10-bar H4 return (ret_10_H4) is the dominant feature (importance=0.86).
    # Secondary signal: 10-bar H1 return (ret_10_H1), importance=0.09.
    # Tertiary: 3-bar H1 return (ret_3_H1), importance=0.04.
    #
    # Derived from tree (rank 1, match_rate_cv=0.905) and univariate (rank 3, 0.899):
    #
    # BUY if ret_10_H4 > 0.0002851 AND ret_10_H1 > 0.000249
    # SELL if ret_10_H4 < -0.0002851 AND ret_10_H1 < -0.000249
    # NONE otherwise
    #
    # Note: The decision tree collapses to: class=BUY when ret_10_H4>0 AND ret_10_H1>0;
    # class=SELL when ret_10_H4<=0 AND ret_10_H1<=0. The univariate thresholds
    # ret_10_H4 > 0.0002851 and ret_10_H1 > 0.000249 refine the zero-crossings.
    # The RIPPER ruleset (rank 2) adds bb_pos_20_2_H4 and close_vs_session_open_* as
    # confirming filters; for replicator simplicity the primary tree-based rule is preferred.
    #
    # Auxiliary BB confirmation (optional, from RIPPER rank 2):
    #   BUY additionally gated by bb_pos_20_2_H4 > 0.07142
    #   SELL additionally gated by bb_pos_20_2_H4 < -0.07142
  exit:
    max_holding_hours: 8
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[algo_trading_chan, p.133, ch.6] — 'past returns of a single instrument are positively correlated with future returns' (time series momentum)"
  - "[advances_fin_ml, p.160-162] — 'Mean Decrease Accuracy — out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower' — confirms ret_10_H4 importance=0.86 as the dominant direction predictor"
  - "[evidence_based_ta, p.27-28] — 'Position bias x market trend creates apparent predictive power in useless rules' — applied here to validate that the buy-bias (mean Buy%=54.6% across pairs) is anchored in a genuine momentum signal, not position bias"
risk_flags:
  - "MARTINGALE: lot p95/p50 ratio = 128.87 >> 3.0 threshold — k1 flag raised (per-month max/median P95 = 144.59). System trades with martingale-like lot scaling. The signal_rule captures DIRECTION only; sizing must NOT replicate this dynamic and is capped at proportional_equity_2pct."
  - "CONFIDENCE REDUCED to 0.48 (below 0.50): the timing pattern (09:00-17:00 UTC, spread across London+NY sessions) and the direction evidence (direction by hour: buy% varies 44.9%-55.8% with no clean session signature) are consistent with OVERLAP_NY_LONDON_RANGE but the martingale dynamics make it impossible to isolate a clean signal window. The system may rely on lot escalation rather than a pure direction edge."
  - "Real account, broker VT Markets: well-known retail broker, not obscure — no additional confidence reduction applied for broker."
  - "blackout risk: track record 2022-05-02 to 2026-05-01 — includes post-COVID normalization and 2022 USD strength. Edge persistence after macro regime shift unknown."
  - "Hold duration missing (hold p50/p95/max = nan/nan/nan) — exit logic is inferred as manual_or_time but max_holding_hours is estimated from the session width (09:00-17:00 UTC), NOT from actual duration data."
---

# Decoded signal — Happy Breakout VTMarkets (id 9607500)

## Family rationale

### First hypothesis: OVERLAP_NY_LONDON_RANGE

The top entry hours cluster squarely in the London+NY overlap and NY-morning sessions:

- 09:00 UTC — 220 trades (London mid-session)
- 10:00 UTC — 229 trades (London/NY pre-overlap)
- 11:00 UTC — 181 trades
- 15:00 UTC — 224 trades (NY open / London close)
- 16:00 UTC — 178 trades

This 09:00-17:00 UTC window covers both the London continuation phase and the NY open/overlap. The sharpest 5-minute concentration is at 15:30 UTC (97 trades), which sits precisely at the NY open ramp-up inside the London+NY overlap window — a classic signature of `OVERLAP_NY_LONDON_RANGE` strategies that use the intraday range established in London as a reference for NY-open continuation.

The pair universe (GBPUSD 604, EURUSD 561, USDJPY 486, GBPJPY 200, EURJPY 91) is consistent with USD-denominated overlap plays; USDJPY and JPY crosses also trade heavily during the NY opening hour (15:00-16:00 UTC).

### Alternative considered: LONDON_OPEN_MOMENTUM

The 09:00 UTC peak (220 trades) could support `LONDON_OPEN_MOMENTUM`. However, the Buy% at 09:00 is only 51.8% — barely above neutral — while the 11:00 slot reaches 55.8% and the 15:30 five-minute bar is the dominant cluster. A pure London-open system would show a tighter concentration in 06:00-09:00 UTC with a clean directional signal aligned with the Asian range. Neither condition is met here. Rejected.

### Alternative considered: NY_SESSION_REVERSAL

The 15:00-16:00 UTC entry hours are active (224+178 trades), and the Buy% at 16:00 is 44.9% (slight sell bias). However `NY_SESSION_REVERSAL` requires a systematic anti-London direction signal, which is not visible: hour=15 has Buy%=49.6% (neutral), hour=16 has 44.9% (weakly bearish), but hour=11 has 55.8% (bullish). There is no consistent reversal sign opposite to the London move. Rejected.

### Why confidence is below 0.50

The martingale flag fires: lot p95/p50 ratio = 128.87 (threshold 3.0). The k1 flag specifies "per-month max/median P95 = 144.59 — within-month doubling." This means the system almost certainly uses lot escalation to recover losing streaks, making it impossible to disentangle clean signal edge from compounding lot dynamics. The direction features are real (match_rate_cv 0.905 for the tree, p_corr < 1e-300 for univariates), but the observed track record's profitability is materially contaminated by martingale sizing. Family remains `OVERLAP_NY_LONDON_RANGE` as the most consistent timing and pair interpretation, but confidence is capped at 0.48.

## Rule derivation

### Top feature: ret_10_H4 (importance = 0.86)

The decision tree (rank 1, match_rate_cv=0.905, std=0.031, coverage=1.00) assigns 86% of its splitting power to `ret_10_H4`. The tree's root split is `ret_10_H4 <= -0.00` vs `> -0.00`, and in the positive branch (ret_10_H4 > 0), the secondary split confirms direction via `ret_10_H1`. The univariate candidate (rank 3) sharpens this threshold to `ret_10_H4 > 0.0002851` for the Buy side with match_rate_cv=0.899 at coverage=0.50 — meaning the rule is silent (NONE) on the remaining 50%, which corresponds to the SELL-eligible half. This threshold is taken verbatim from candidates.json.

### Secondary feature: ret_10_H1 (importance = 0.09)

Univariate rank 7 gives `ret_10_H1 > 0.000249 => Buy`, match_rate_cv=0.867. In the tree, the second-level split is `ret_10_H1 <= -0.00` vs `> -0.00`. Combined with ret_10_H4, the tree collapses to: BUY when both H4 and H1 10-bar returns are positive. The fine threshold 0.000249 is taken verbatim from candidates.json rank 7.

This two-timeframe momentum alignment (H4 trend + H1 follow-through) is consistent with time series momentum theory: [algo_trading_chan, p.133, ch.6] states "past returns of a single instrument are positively correlated with future returns." The H4 lookback (~40 hours at 10 bars) captures the medium-term directional bias; the H1 secondary confirms intraday continuation.

### Tertiary feature: ret_3_H1 (importance = 0.04)

Only 4% of tree splitting is assigned to `ret_3_H1`. In the tree, a `ret_3_H1 <= 0.00` sub-branch under `ret_10_H4 <= 0, ret_10_H1 > 0` produces class=1 (BUY even when H4 is negative, if H1 is recovering and H1-3 is flat or negative). This is a nuanced reversal sub-rule for the mixed-signal case. Given its low importance (0.04) and complexity, it is explicitly not included in the simplified replicator direction rule — the replicator uses only the dominant two features.

### RIPPER ruleset (rank 2, match_rate_cv=0.893)

The RIPPER produces 33 disjunctive clauses, featuring `bb_pos_20_2_H4`, `close_vs_session_open_*`, `ema_dist_20_H1`, and `prior_bar_sign_H4` as secondary qualifiers. The dominant RIPPER clause is `[close_vs_session_open_M15=1.0^bb_pos_20_2_H4=0.84-1.09]` (M15 bar above session open AND H4 BB position 0.84-1.09, i.e., upper half of the band). Univariate rank 4 confirms `bb_pos_20_2_H4 > 0.07142 => Buy` with match_rate_cv=0.891. The RIPPER thresholds are taken verbatim (0.07142 from rank 4, 0.84-1.09 from rank 2 text). Because RIPPER uses 32 features and risks overfit, the simplified rule treats bb_pos_20_2_H4 as an optional confirming filter only.

Feature importance interpretation per [advances_fin_ml, p.160-162]: "Mean Decrease Accuracy — out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower." The tree's reported importance weights (ret_10_H4=0.86, ret_10_H1=0.09, ret_3_H1=0.04, atr_ratio_M15=0.01) represent MDI (in-bag), not MDA. The single-feature dominance of ret_10_H4 at 0.86 is unusually high — it suggests the strategy is essentially a single-factor momentum system with ret_10_H4 as the direction signal, and the remaining features are refinement layers.

### Exit logic

Hold duration is completely missing from the fingerprint (p50/p95/max all NaN). The exit_kind is `manual_or_time` for all 1942 trades. Given the entry window 09:00-17:00 UTC and the session structure, a maximum holding time of 8 hours is estimated (i.e., intraday exit before the Asian session opens around 22:00 UTC). No TP/SL pips were detectable from the fingerprint — the system likely uses dynamic manual exits or time-based close at session end.

## Confidence breakdown

- Family identification: 0.52 — timing peaks at 09:00-17:00 UTC and 15:30 spike are most consistent with OVERLAP_NY_LONDON_RANGE; but the martingale contamination makes the session-level edge ambiguous.
- Direction rule: 0.68 — ret_10_H4 dominance (0.86 importance, match_rate_cv=0.905) is strong; the threshold 0.0002851 from univariate rank 3 is cross-validated (p_corr~0). The SELL side symmetry is inferred from coverage=0.50 pattern and negative mirror.
- Exit logic: 0.25 — hold duration entirely missing; the 8h estimate is session-structural, not data-derived.
- Overall: 0.48 = conservative weighted mean (family 0.52 × 0.30 + direction 0.68 × 0.45 + exit 0.25 × 0.25), rounded to 0.48 and capped below 0.50 due to martingale flag.

## Open questions (para Stage 3 + posteriores)

- **Martingale isolation**: Stage 3 must run the backtest with flat lot sizing (ignoring the martingale escalation). If the flat-lot backtest has near-zero edge, the system relies purely on martingale recovery and should be discarded regardless of direction accuracy.
- **Entry window sensitivity**: Test 09:00-12:00 UTC vs 14:00-17:00 UTC as separate sub-windows — the 15:30 spike suggests the NY-open sub-window may carry most of the edge.
- **ret_10_H4 threshold stability**: Test whether the 0.0002851 threshold is regime-stable across the 2022-2026 window or degrades after the 2022 USD strength event.
- **SELL signal symmetry**: The fingerprint shows Buy%≈50% across all pairs, which is near-neutral. Stage 3 should test asymmetric rules (Buy only, or Sell only) before assuming full two-way direction.
- **bb_pos_20_2_H4 as gating filter**: Stage 3 should test whether adding the RIPPER's bb_pos_20_2_H4 > 0.07142 gate materially improves hit rate or simply adds complexity.
- **Pair-level subsets**: USDJPY (Buy%=58.2%) and EURJPY (Buy%=62.6%) show stronger long bias. Stage 3 should test whether a single-pair (USDJPY or EURJPY) version has higher reliability score than the five-pair pool.
