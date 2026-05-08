---
system_id: 6541963
family: H1_MOMENTUM_GOLD
confidence: 0.60
generated: 2026-05-02
rule:
  entry_window_utc: ["09:00", "17:59"]
  pairs: [XAUUSD]
  direction: |
    # TREE rank 1 (match_rate_cv=0.844, std=0.026 over 5 folds 0.814-0.890,
    # coverage=1.0) is dominated by ret_10_H1 (MDI=0.74) with secondary support from
    # ret_3_H1 (0.07), bb_pos_20_2_H1 (0.05), ema_dist_20_H1 (0.04), ret_1_H1 (0.03).
    # Univariate ret_10_H1 > -0.001083 ⇒ Buy reaches match_rate_cv=0.808 alone with
    # coverage=0.60 and Bonferroni-corrected p ≈ 5.7e-195 (520 tests). The encoded
    # rule preserves the dominant H1 momentum split. The threshold -0.001083 is
    # taken verbatim from candidates.json rank 3 — no threshold invented.
    BUY  if ret_10_H1 > -0.001083
    SELL if ret_10_H1 <= -0.001083
  exit:
    max_holding_hours: 1.0
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[advances_fin_ml, p.160-162] — \"Mean Decrease Impurity (MDI) — in-bag feature importance measure based on weighted average impurity reduction across all splits\". Justifies trusting ret_10_H1 (MDI=0.74) as the single dominant driver of the tree's direction logic; MDI bias toward high-cardinality features is acknowledged but corroborated by the rank-3 univariate that uses ret_10_H1 in isolation."
  - "[systematic_trading, p.118-119] — \"EWMAC rule — Exponentially Weighted Moving Average Crossover: buy when the fast EWMA is above the slow EWMA\". Provides literature support that an H1 multi-bar return signal (ret_10_H1) belongs to the recognised momentum/trend signal class; the binarised BUY/SELL decision here is structurally analogous to a fast-vs-slow regime filter on H1."
  - "[evidence_based_ta, p.291,p.315] — \"Optimize parameters with few observations. The magnitude of data-mining bias grows dramatically with small sample size\". Anchors the demo-account caveat: even with vanishing p-values, vendor-side selection bias plus 520 multiple comparisons mean candidate thresholds must be treated as in-sample fits, not OOS edge."
  - "[machine_trading, p.159-160,p.282] — \"Intraday strategy with holding minutes can become impossible at scale\" and \"for intraday strategies use compiled languages (C++, C#, Java)\". Direct relevance: hold p50=0.00h / p95=0.29h is sub-M5 territory, so the replicator must flag execution/microstructure risk before any live extrapolation."
risk_flags:
  - "needs_m1_review — hold p50 = 0.00h, p95 = 0.29h (~17 min), max = 8.75h (post-R4 hold-extraction fix). Sub-M5 timing sensitive: signal logic runs on H1 features but exit logic (100% manual_or_time) is sub-M5 and cannot be validated against the available H1/M15/M5/M1 OHLC. The 1h max_holding_hours cap is conservative (covers p95) but unverifiable without M1 data. Do NOT change project timeframe or any code; flag M1 review as a Stage 3 prerequisite."
  - "demo_account — system_info.account_type=Demo, broker=Tickmill, leverage=1:500, MT4. Decoder workflow §3 (decoder.md) mandates a 0.10 confidence reduction for Demo accounts due to vendor selection bias. Already applied to overall confidence."
  - "blackout_2021_2026 — date range 2019-03-05 → 2026-04-30 with max_gap_days=63.8 indicates extended pause periods. The bulk of the +129,771% gain curve is from a window with no live forward verification."
  - "drawdown_54.8pct_on_xau_1to500 — system_info reports drawdown=54.81% on a single-instrument XAUUSD account at 1:500 leverage. lot p95/p50=4.11 indicates equity-proportional scaling that compounds drawdown; even with martingale=PASS, real-money replication may not survive a single regime shift."
  - "provisional_family — H1_MOMENTUM_GOLD is provisional=True in shared/decoder_taxonomy.py with n_supporting_systems=1 (this system). 5R-1-hardening §1 mandates downgrade to UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=H1_MOMENTUM_GOLD if R1 (re-decode of the 30 non-rechecked systems) fails to surface a 2nd independent supporter."
  - "weak_clock_anchor — top hour 15:00 UTC carries 307/2213 = 13.9% of trades; top 5min bucket 15:30 UTC carries 67/2213 = 3.0%. Entry is distributed across European-into-US session (09-17 UTC), NOT clock-anchored to a single news bucket. The NEWS_RELEASE_MOMENTUM provisional family criterion (≥1 hour bucket with >30% trades + name flag NEWS) is therefore NOT met, despite p50 hold <5min being a partial signal in that direction."
  - "lot_dynamics_within_bounds — lot p95/p50 ratio = 4.11 with martingale=PASS (steps=0, max_streak=0). Sizing is non-flat but is not martingale-grid. The signal_rule.md sizing field is set to the conservative project default (proportional_equity_2pct); the actual sizing rule cannot be reverse-engineered from per-trade lot data alone and is logged as an open question for Stage 3."
---

# Decoded signal — Happy Gold - Tickmill (M15) (id 6541963)

## Family rationale

The system is a single-pair XAUUSD strategy run on a Demo Tickmill 1:500 MT4 account by the
HappyForex vendor (system_info.json). The fingerprint shows 2213 trades, 100% on XAUUSD, 52.1% Buy,
exit_kind=manual_or_time for every trade, hold p50=0.00h / p95=0.29h / max=8.75h (post-R4
hold-extraction fix; values are now reliable, not NaN as in the v2 frozen rule), and an entry
distribution that spans 09-17 UTC with the top hour 15:00 UTC at 13.9% and top 5min bucket 15:30 UTC
at 3.0%.

Out of the closed taxonomy enum (`shared/decoder_taxonomy.py`, 12 values), the only family whose
defining criterion matches this signature is `H1_MOMENTUM_GOLD` (provisional, D7 2026-05-02 — the
single registered case is this very system). The provisional criterion has four prongs and the
candidates table satisfies all four: (a) Gold/XAU pair → XAUUSD ✅; (b) entry-on-H1-momentum →
TREE rank 1 has ret_10_H1 importance=0.74, ret_3_H1=0.07, bb_pos_20_2_H1=0.05, ema_dist_20_H1=0.04,
ret_1_H1=0.03, all H1-resolution ✅; (c) tree balanced → 52.1% Buy vs 47.9% Sell, baseline
Always-Buy=0.521 ✅; (d) dir_acc>0.7 → tree CV=0.844 with std=0.026 across 5 folds (range
0.814-0.890) ✅.

Alternatives in the enum considered and rejected:

- `UNCATEGORIZED + reason_code=hold_mismatch` — hold p50=0.00h is intraday-scalp territory while
  H1_MOMENTUM_GOLD's name implies hourly resolution. Rejected because the family criterion does NOT
  constrain hold duration; "H1" refers to the *signal-generation timeframe* (features driving entry
  direction), not the holding period. Re-labelling here would invalidate the family and its only n=1
  reference.
- `FACTOR_SCALPING` — empty post-5R-0; decoder.md anti-pattern §10 warns against it without strong
  multi-factor evidence. Here ret_10_H1 alone explains 74% of MDI, which is single-factor momentum,
  not multi-factor scalping. Rejected.
- `NEWS_RELEASE_MOMENTUM` — name is "Happy Gold" not "Happy News" (no NEWS name flag), and no single
  hour bucket exceeds 30% trades (top is 13.9%, criterion is >30%). Even though p50 hold <5min is a
  partial signal, two of three criteria fail. Rejected; instruction #8 requires classifying only from
  observed evidence rather than assuming a calendar-aware implementation.
- `LATE_NY_BREAKOUT` / `OVERLAP_NY_LONDON_RANGE` / `LONDON_OPEN_*` — pair is XAU not FX-major, and the
  entry distribution does not concentrate in the required UTC windows (21-01 / 12-16 / 06-09).
  Rejected.
- `MARTINGALE_GRID` — sanity martingale=PASS (steps=0, max_streak=0). Rejected.

The literature anchor for treating ret_10_H1 as a legitimate momentum-class signal comes from
[systematic_trading, p.118-119] (EWMAC fast-vs-slow as the canonical trend signal class) and from
[advances_fin_ml, p.160-162] (MDI feature importance as evidence the tree's first split is the
dominant driver). Aronson's small-sample bias warning [evidence_based_ta, p.291] is cited as the
reason confidence is held to 0.60 rather than ascending with the raw match_rate_cv.

## Rule derivation

Two artifacts in `decoder/candidates.json` drive the executable rule:

1. **Univariate primary** (rank 3): `ret_10_H1 > -0.001083 ⇒ Buy`, match_rate_cv=0.808,
   coverage=0.60, p_corrected ≈ 5.7e-195. Single-feature, n_features=1; cleanest auditable
   signal. Forms the BUY arm.
2. **Tree primary** (rank 1): DecisionTree(max_depth=4) splits the SELL side primarily on
   `ret_10_H1 <= -0.00`. The encoded SELL condition (`ret_10_H1 <= -0.001083`) is the simplified
   complement of the BUY arm and matches the tree's first split direction. The deeper branches
   (ret_1_H1, ema_dist_20_H1, ret_10_M15) only marginally improve match_rate over the univariate
   primary and are excluded from the executable rule for parsimony — Stage 3 may A/B test the
   gated form.

The threshold `-0.001083` is taken verbatim from candidates.json rank 3 (univariate). No threshold
was invented.

The `entry_window_utc: ["09:00", "17:59"]` envelope is the empirical 09-17 UTC band that contains
the top-5 hours (each ≥172 trades, cumulatively ~48% of all entries). It is wider than a typical
clock-anchor and reflects the actual distribution rather than a single bucket — consistent with
weak-clock-anchor risk flag.

The `exit.max_holding_hours: 1.0` is set conservatively above the post-R4 hold p95=0.29h
(~17 min) and well below max=8.75h. With 100% `manual_or_time` exits, no take-profit or stop-loss
can be inferred from the fingerprint; both are nulled and the time exit is the only deterministic
exit primitive available to the replicator. This is a material change vs the prior v2 frozen rule
which had `max_holding_hours: null` due to pre-R4 NaN holds — the post-R4 fingerprint allows a
defensible cap.

`sizing: proportional_equity_2pct` is the project's conservative default. Observed lot p95/p50=4.11
indicates non-flat sizing in the live track but no martingale (steps=0, max_streak=0); the actual
sizing function cannot be reverse-engineered from per-trade lot data alone and is logged as an
open question.

## Confidence breakdown

- Family identification: 0.70 — matches the H1_MOMENTUM_GOLD provisional criterion on all 4 prongs
  (pair=XAU, H1 momentum dominant in tree, class balanced, dir_acc>0.7). Capped at 0.70 because the
  family is `provisional=True` with n=1, and that n=1 is the very system being decoded — the match
  is circular by construction.
- Direction rule: 0.75 — TREE rank 1 match_rate_cv=0.844 with std=0.026 across 5 folds (range
  0.814-0.890); univariate ret_10_H1>-0.001083 reaches 0.808 alone with p_corrected ≈ 5.7e-195
  over 520 tests. Strong, audited.
- Exit logic: 0.50 — 100% manual_or_time and post-R4 p50=0.00h means the exit timing is sub-M5 and
  cannot be validated against the available H1/M15/M5/M1 features. The 1h cap is plausible
  (covers p95=0.29h) but unverifiable without M1 data.
- Demo penalty: -0.10 (decoder.md §3 — Tickmill is reputable so no extra broker penalty).
- Overall: 0.70*0.4 + 0.75*0.4 + 0.50*0.2 - 0.10 ≈ 0.58 → reported 0.60.

## Open questions (para Stage 3 + posteriores)

- **Calendar-aware replication**: 15:30 UTC is the top 5-min bucket (3.0%). This overlaps the US
  energy/commodity data window (e.g., EIA crude inventories at 14:30/15:30 UTC) and gold often
  reacts to USD-driven data. Bucket concentration is well below the NEWS_RELEASE_MOMENTUM threshold
  (>30%), so this re-decode does NOT classify as news-driven. If a Stage 3 M1 review reveals tighter
  sub-bucket clustering (e.g., 15:30:00-15:31:00 UTC dominating, or alignment with scheduled US data
  release minutes), a path to UNCATEGORIZED + reason_code=mixed_strategy or downgrade to
  candidate_new_family may be warranted.
- **M1 exit timing**: per instruction #9 (needs_m1_review flag), the replicator must, before scoring,
  confirm whether the 1h max_holding_hours cap is representative or whether real exits cluster at
  much shorter horizons (e.g., 1-5 min). XAUUSD spreads make this materially affect the cost model.
- **Sizing reverse-engineering**: lot p95/p50=4.11 with martingale=PASS — what is the actual sizing
  rule? Equity-proportional? Volatility-targeting on Gold ATR? Time-of-day? Stage 3 should test
  `proportional_equity_2pct` vs alternatives if the reliability proxy is sensitive to sizing.
- **Confirmation gate ablation**: rank-4 univariate `bb_pos_20_2_H1 > 0.08917 ⇒ Buy` (CV=0.811,
  coverage=0.50) is a continuation filter. Stage 3 should A/B test the gated rule
  (`BUY if ret_10_H1 > -0.001083 AND bb_pos_20_2_H1 > 0.08917`) vs the ungated form encoded here.
- **Provisional family review (R1 obligation)**: per `_diagnostics/5R-1-hardening.md` §1, if R1
  (re-decode of 30 non-rechecked systems) does not surface a 2nd system matching the
  H1_MOMENTUM_GOLD signature, downgrade this label to
  `UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=H1_MOMENTUM_GOLD`.
- **Demo + blackout**: the 2019-2026 track was generated on a Demo account; live forward
  verification is absent. Even a high reliability proxy score should be interpreted as "vendor's
  curve is internally consistent", not "edge will replicate live". A Stage 3 / risk-flag concern
  independent of the decoder.
- **Regime stationarity**: 2019-03 → 2026-04 spans pre-COVID, 2020 spike, and 2022-2024 Fed/inflation
  regimes on Gold. Split 2019-2021 vs 2022-2026 and check direction-rule match_rate stability.
  A drop >10pp post-2022 would suggest regime-bound edge.
