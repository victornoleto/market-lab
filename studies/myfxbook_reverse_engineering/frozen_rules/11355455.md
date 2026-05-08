---
system_id: 11355455
family: H1_MOMENTUM_GOLD
confidence: 0.70
generated: 2026-05-02
rule:
  entry_window_utc: ["08:00", "18:59"]   # 5 of top-5 entry hours fall in this window; 16-18 UTC is dominant cluster
  pairs: [XAUUSD]
  direction: |
    # Tree rank-1 (CV=0.923 ± 0.029, 5 folds = 0.935, 0.935, 0.870, 0.957, 0.918) collapses
    # to a SINGLE-feature decision on bb_pos_20_2_H1 — the ret_1_M15 split below the
    # positive root reunites both child leaves to class 1, so the tree reduces to:
    #
    #   bb_pos_20_2_H1 <= -0.19  ⇒  class 0 (SELL)
    #   bb_pos_20_2_H1 >  -0.19  ⇒  class 1 (BUY)
    #
    # Threshold -0.19 is the literal cut returned by Stage 1 mining. Class polarity
    # (1=Buy) is corroborated by 7 of the top-10 univariate rules sharing the
    # signature "<momentum_feature> > <threshold> ⇒ Buy" (e.g. rank 3
    # ema_dist_20_H1 > -0.2642 ⇒ Buy at CV=0.906; rank 6 ret_10_H1 > 0.0004 ⇒ Buy
    # at CV=0.880; rank 7 ret_3_H4 > 0.0005 ⇒ Buy at CV=0.845).
    #
    # bb_pos_20_2_H1 is the H1 Bollinger position (period=20, k=2) feature in
    # decoder/features.parquet (named exactly).

    SELL if bb_pos_20_2_H1 <= -0.19
    BUY  if bb_pos_20_2_H1 >  -0.19

    # Optional confirmation gate (rank-3 univariate, CV=0.906, coverage=0.60,
    # Bonferroni p=1.6e-37 over 524 tests): require ema_dist_20_H1 > -0.2642 to
    # take BUY, else NONE. Stage 3 should A/B test gated vs ungated to see
    # whether redundancy with bb_pos_20_2_H1 helps precision.
  exit:
    max_holding_hours: 0.5    # observed max=0.33h (~20min); 0.5h cap above empirical max
    take_profit_pips: null    # exit_kind=manual_or_time only; no recoverable TP
    stop_loss_pips: null      # idem; no recoverable SL
  sizing: proportional_equity_2pct  # lot p95/p50=1.51 (modest equity scaling); martingale=PASS, steps=0, max_streak=0
citations:
  - "[algo_trading_chan, p.133, ch.6] — \"Time series momentum — past returns of a single instrument are positively correlated with future returns.\" Direct support for using H1 BB position / H1 returns as Buy/Sell signal on a single instrument (XAUUSD)."
  - "[stocks_on_the_move, p.58, p.60] — \"When a stock has been going up for a while, the likelihood of it continuing up is greater than for it to turn around\"; cross-asset evidence (Levy 1967, Jegadeesh-Titman 1993) that price-continuation is one of the few statistically robust effects."
  - "[advances_fin_ml, p.159, p.160-167] — Snippet 8.1 First Law of Backtesting: \"Backtesting is not a research tool. Feature importance is.\" Tree assigns 0.97 importance to bb_pos_20_2_H1 with 0.03 to ret_1_M15 — single dominant feature meets MDI dominance signal; AFML rule [p.160-167] requires reporting features ranked by ≥2 methods; bb_pos_20_2_H1 is corroborated by univariate rank-4 (same feature, threshold -0.285, CV=0.906)."
  - "[evidence_based_ta] — Aronson's Multiple Comparison Procedure: 524 univariate tests run; rank-3 ema_dist_20_H1 > -0.2642 has Bonferroni-corrected p=1.6e-37 — survives multiplicity correction with overwhelming margin."
risk_flags:
  - "needs_m1_review — hold p50=0.00h, p95=0.03h (~108s), max=0.33h (~20min). All trades exit within ~M5; a replicator on M5 OHLC may not capture the actual entry/exit timing. Stage 3 must verify direction-rule fitness on M1 bars before declaring match."
  - "calendar_aware_replication_open — top hour 16:00 UTC + secondary 16:35/17:00 5min buckets coincide with US data-release window (CPI, retail sales, FOMC minutes typically released 12:30/14:00/18:00 UTC) and London PM Gold fix (15:00 UTC). The fingerprint does NOT prove a calendar-driven mechanism (entries are also distributed across 08, 15, 18 UTC), but Stage 3 cannot assume the system reads an economic calendar live — replication must work from observed trade/OHLC evidence only. Tag as Open Question."
  - "second_supporter_for_provisional_family — H1_MOMENTUM_GOLD currently provisional with n=1 (ref system 6541963). This system is a candidate n=2 supporter (Gold + H1 momentum tree primary + tree balanced + dir_acc 0.92). Promotion of the provisional family requires confirming this is an INDEPENDENT instance, not a same-codebase clone of 6541963 (both are HappyForex Gold). Stage 3 should compare lot-sizing curve, hourly distribution, and 2025-2026 overlap window for codebase-twin diagnosis."
  - "vendor_selection_bias — HappyForex public catalog system; vendor publishes only winners, blackout/withdrawal of underperformers expected. -0.05 confidence applied."
  - "short_live_track_16mo — date range 2024-12-31 → 2026-04-30 = ~16 months on real account; one regime cycle insufficient to validate edge persistence (compare reference 6541963 = 7y track on Demo)."
  - "gold_only_concentration — single instrument (XAUUSD); 3 ARCHIV entries are stub/artifacts (ignore in replicator). 2024-2026 spans Fed-cut + Gold all-time-high regime; stationarity not assumed beyond observed window."
  - "broker_obscurity — D Prime is a lower-tier offshore broker; pip cost / spread on XAUUSD likely higher than IC Markets / Pepperstone reference. Replicator cost model should stress-test on 1.5x baseline spread."
---

# Decoded signal — Happy Gold - DooPrime (id 11355455)

## Family rationale

The fingerprint matches the provisional `H1_MOMENTUM_GOLD` family on all four registered criteria from `decoder_taxonomy.TAXONOMY` (D7 of user 2026-05-02; `_diagnostics/5R-1-hardening.md` §1):

1. **Gold/XAU** — 233 of 236 trades on XAUUSD (98.7%); the 3 `ARCHIV` entries are pipeline stubs and are ignored.
2. **Entry-on-H1-momentum** — tree rank-1 places **0.97 importance on `bb_pos_20_2_H1`** with `ret_1_M15`=0.03; the next 5 univariate ranks are all H1 or H4 momentum/trend descriptors (`ema_dist_20_H1`, `ret_10_H1`, `ema_dist_20_H4`, `ret_3_H4`, `bb_pos_20_2_H4`) at CV≥0.82. The H1 timeframe dominates the signal layer regardless of intra-trade hold being sub-M5.
3. **Tree balanced** — Buy% on XAUUSD = 53.2% (127 Buy / 109 Sell). No always-Buy / always-Sell collapse.
4. **dir_acc > 0.7** — tree rank-1 CV match-rate = **0.923 ± 0.029** across 5 folds (min 0.870, max 0.957). Univariate ranks 3 and 4 both at 0.906. Comfortably above the 0.7 floor.

This system is therefore a **candidate n=2 supporter** for the H1_MOMENTUM_GOLD provisional family (registered with n=1 on system 6541963, Happy Gold Tickmill M15). If Stage 3 confirms it is not a same-codebase clone, the provisional flag in `decoder_taxonomy.py` may be cleared after R1.

**Why not FACTOR_SCALPING.** Hold p50=0.00h / p95=0.03h / max=0.33h does meet the post-R4 sub-M5 hold criterion, but the family description requires "edge typically vol-targeting or pair-trading intraday". This system has neither: single instrument (XAUUSD), no vol-targeting feature in the tree (`atr_*` and `vol_*` columns are absent from the top-10 candidates), no pair-trading. The edge is direct H1 directional momentum, executed in a sub-M5 window. The 5R-0 finding noted FACTOR_SCALPING was over-applied by Sonnet on Gold/BTC high-frequency systems precisely because hold was NaN pre-R4; with R4 fix and confirmed sub-M5 hold, the family STILL doesn't fit because the signal mechanics are H1 momentum, not multi-factor scalping.

**Why not LATE_NY_BREAKOUT / LONDON_OPEN_*.** Top entry hours = {16, 17, 15, 08, 18} UTC (no 21-01 UTC concentration → not LATE_NY_BREAKOUT; no 06-09 UTC concentration → not LONDON_OPEN_*). Direction-by-hour Buy% is flat (44-59% across top 5 hours), no session asymmetry.

**Why not OVERLAP_NY_LONDON_RANGE.** Despite 15-18 UTC entries falling in the NY/London overlap, the direction signal is **momentum-following on H1 BB position** (Buy when bb_pos > -0.19, i.e. price near or above midline), not a range fade (which would Buy at lower band and Sell at upper band). The `bb_pos_20_2_H1` cut at -0.19 specifically excludes the lower band region from BUY, opposite of a fade rule.

**Why not NEWS_RELEASE_MOMENTUM.** Provisional criteria require name-flag NEWS/HF News + ≥1 hour bucket >30% of trades. Name is "Happy Gold - DooPrime" (no NEWS), and top hour 16:00 UTC = 31/236 = 13% (well below 30%). Calendar-window coincidence is plausible but unproven; tagged as risk_flag rather than family attribution.

**Why not MARTINGALE_GRID.** Sanity PASS (steps=0, max_streak=0). Lot p95/p50=1.51 is modest equity-proportional scaling, not doubling-on-loss.

**Why not UNCATEGORIZED.** All four H1_MOMENTUM_GOLD criteria are met without forcing. UNCAT would require evidence outside any enum family or insufficient evidence to decide; here the tree CV=0.923 with std=0.029 is the strongest direction signal across the candidate ranks and the family description fits the observed mechanics.

## Rule derivation

**Direction (tree rank-1, CV=0.923 ± 0.029).** The published tree has two split levels but the deeper `ret_1_M15` split is degenerate — both children below the positive `bb_pos_20_2_H1` root return class 1. So the operational rule is single-feature: `bb_pos_20_2_H1 <= -0.19 ⇒ class 0 (SELL); else class 1 (BUY)`. Threshold -0.19 is the literal Stage 1 cut.

Class polarity (1=Buy) is corroborated by seven of the top-ten univariate rules sharing the form `"<momentum_feature> > <threshold> ⇒ Buy"` with CV ranging 0.77-0.91, all with Bonferroni-corrected p < 1e-14 over 524 candidates. Specifically rank-4 univariate `bb_pos_20_2_H1 > -0.285 ⇒ Buy` (CV=0.906) reproduces the tree's primary feature with a slightly looser threshold. The agreement between the tree (multivariate) and rank-4 univariate (single feature) on the same `bb_pos_20_2_H1` cut satisfies AFML's rule [advances_fin_ml, p.160-167] that features ranked important by ≥2 methods are the reliable signal.

**Why not the RIPPER ruleset (rank 2, CV=0.825).** RIPPER is an 8-clause disjunction including narrow conjunctions like `[close_vs_session_open_M1=1.0 ∧ bb_pos_20_2_H1=0.51-0.73]` and `[ema_dist_20_H1=2.06-2.63]`. CV is 10pp below the tree (0.825 vs 0.923) at much higher complexity (8 features vs 1 effective feature). Per Aronson (multiplicity / overfit caution) and AFML First Law (feature parsimony), the tree wins on Occam's razor.

**Entry window.** Top 5 hours = {16, 17, 15, 08, 18} UTC, covering 112 of 236 trades (47%); the broader 08:00-18:59 UTC window covers ~80% of activity. The 16-18 cluster is the NY afternoon (London PM Gold fix at 15:00 UTC, US data window 12:30-18:00 UTC). The 08:00 secondary peak is London open. Direction-by-hour Buy% is flat (44-59%) across all top hours, so the window is execution / liquidity-driven, not asymmetric-edge driven.

**Exit.** Hold p50=0.00h / p95=0.03h (~108 s) / max=0.33h (~20 min). Exit kind is uniformly `manual_or_time` (236/236). No TP/SL recoverable from the fingerprint. Setting `max_holding_hours: 0.5` as the upper guard rail (just above empirical max=0.33), TP/SL=null. **Stage 3 must brute-force exit candidates on M1 OHLC**: (a) fixed N-bar M1 exits for N ∈ {1, 2, 5, 10, 20}, (b) opposite-signal exit (when `bb_pos_20_2_H1` crosses -0.19 from the entry side), (c) ATR-based trailing on M1. Fitness criterion = match the published gain/DD/monthly stats (gain +2,395%, DD 8.16%, monthly 15.50%).

**Sizing.** lot p50=3392, p95=5122, max=5595, p95/p50 ratio=1.51. Modest scaling around the median; not martingale (sanity PASS, steps=0, max_streak=0). Inferred equity-proportional. Note: lot units here are MyFxBook's raw lot ledger — interpret with the system's $1k seed → $19k equity context, ratios > absolutes.

## Confidence breakdown

- **Family identification: 0.80** — all four `H1_MOMENTUM_GOLD` registered criteria met without forcing. Provisional family — if Stage 3 confirms this is the n=2 supporter, this contributes evidence for promoting the family out of provisional status. -0.05 for the codebase-twin risk (same vendor as the n=1 reference 6541963).
- **Direction rule: 0.85** — tree CV=0.923 ± 0.029 across 5 folds (min 0.870) is the strongest tree signal in the system; rank-4 univariate independently confirms the same feature; rule reduces to a single-feature cut.
- **Exit logic: 0.40** — `manual_or_time` only; no recoverable TP/SL. Sub-M5 hold means even M5 replication may misalign. Replicator will need M1 OHLC and brute-force candidates.
- **Sizing: 0.65** — non-martingale confirmed, lot p95/p50=1.51 fits proportional equity scaling, but exact rule (fixed % vs lot-from-equity formula) not recovered.
- **Overall: 0.70** ≈ weighted mean (family 0.20 × 0.80 + direction 0.40 × 0.85 + exit 0.25 × 0.40 + sizing 0.15 × 0.65) = 0.160 + 0.340 + 0.100 + 0.0975 = **0.70**. Penalties offset by direction-rule strength and clean H1_MOMENTUM_GOLD criteria match.

## Open questions (for Stage 3 + posteriores)

- **Codebase-twin diagnosis vs system 6541963 (the provisional H1_MOMENTUM_GOLD anchor).** Both are HappyForex Gold strategies. To count as an *independent* n=2 supporter (and clear `provisional=True` per the review gate in `decoder_taxonomy`), Stage 3 should compare: (a) full hourly entry distribution overlap; (b) lot-sizing curve shape; (c) entry-time clustering during the 2025-2026 overlap window where both systems were active. If trade timestamps align beyond chance, treat as same-codebase clone and keep provisional.
- **Calendar-aware replication.** The 16:00 UTC top hour and 16:35 / 17:00 5-min buckets coincide with US PM data and London Gold fix (15:00). The fingerprint does NOT prove a live calendar feed is consumed — entries spread across 08, 15, 18 UTC make a name-flag NEWS_RELEASE_MOMENTUM classification inappropriate (no NEWS in name; no >30% bucket concentration). Replicator must work from observed OHLC + clock alone; do not implement an economic-calendar reader.
- **M1 OHLC fitness.** Sub-M5 hold requires M1 bars to evaluate direction-rule match honestly. M5 evaluation will likely overstate match rate by collapsing entry-and-exit into a single bar. `risk_flag: needs_m1_review` carries this.
- **bb_pos_20_2_H1 threshold stability.** Cut -0.19 is fitted on 2024-12 → 2026-04. Gold spent that window in a Fed-cut / all-time-high regime. Stage 3 should resample the threshold on a rolling 6-month window and verify the optimal cut is stationary; if it drifts > 0.10 across windows, the rule is regime-bound.
- **Exit-rule recovery.** Sweep M1 candidates: fixed N-bar exit (N ∈ {1, 2, 5, 10, 20}), opposite-signal exit (when `bb_pos_20_2_H1` re-crosses -0.19), ATR-trail. Best variant = closest to vendor's gain +2,395% / DD 8.16% / monthly 15.50%.
- **Cost-model stress.** D Prime broker is offshore Tier-3; replicator should test 1.0x / 1.5x / 2.0x baseline XAUUSD spread and confirm the 8.16% DD is achievable under realistic costs.
- **Lot / signal-strength correlation.** Test whether lot size correlates with `|bb_pos_20_2_H1 + 0.19|` (signal-strength sizing) or is flat-equity. Affects replicator sizing rule.
