---
system_id: 2421356
family: H1_MOMENTUM_GOLD
confidence: 0.60
generated: 2026-05-02
rule:
  entry_window_utc: ["09:00", "17:59"]   # London + NY overlap on Gold; top hours {15,16,10,17,09} UTC = 51% of trades; 5-min peak 15:30 UTC (NY economic-data window)
  pairs: [XAUUSD]
  direction: |
    # Tree rank-1 (CV=0.875 ± 0.016, 5 folds 0.852-0.898; coverage=1.0). Top-feature
    # importance is concentrated on H1 momentum/trend descriptors:
    #   bb_pos_20_2_H1 = 0.73 (dominant), ret_3_H1 = 0.12, ema_dist_20_H1 = 0.05,
    #   ret_10_H1 = 0.04, ret_10_H4 = 0.03  (cumulative 0.97 on H1+H4 trend features).
    #
    # Walking the literal tree (decoder/candidates.json rank 1):
    #
    #   bb_pos_20_2_H1 > -0.09:
    #     ema_dist_20_H1 > 0.76                        ⇒ BUY  (5/5 leaves class 1)
    #     ema_dist_20_H1 <= 0.76 AND ret_3_H1 <= 0     ⇒ BUY  (2/2 leaves class 1)
    #     ema_dist_20_H1 <= 0.76 AND ret_3_H1 >  0     ⇒ SELL (2/2 leaves class 0)
    #   bb_pos_20_2_H1 <= -0.09:
    #     ret_10_H4 > 0                                ⇒ SELL (1/1 leaf class 0)
    #     ret_10_H4 <= 0:
    #       ret_3_H1 <= 0 AND ret_10_H1 in (-0.01, 0]  ⇒ BUY  (narrow capitulation)
    #       otherwise                                  ⇒ SELL
    #
    # The tree mixes two regimes: (a) trend-continuation BUY when price is far above
    # H1 EMA20 (ema_dist_H1>0.76); (b) pullback-in-trend BUY when not oversold on H1
    # BB and last 3 H1 bars dipped non-positive. Both modes resolve to BUY on
    # H1 momentum context (cumulative H1 features = 0.94 importance).
    #
    # The cleanest single-feature approximation is rank-4 univariate, with CV=0.853
    # and Bonferroni-corrected p=1.8e-210 over 518 tests:

    BUY  if bb_pos_20_2_H1 > 0.07135
    SELL if bb_pos_20_2_H1 <= 0.07135

    # Optional refinement to recover tree's ema_dist branch (rank-5 univariate,
    # CV=0.850, Bonferroni p=6.4e-206): also BUY when ema_dist_20_H1 > 0.1122.
    # Combined OR-rule:
    #   BUY  if (bb_pos_20_2_H1 > 0.07135) OR (ema_dist_20_H1 > 0.1122)
    #   SELL otherwise
    # Stage 3 must A/B test single-feature vs OR-combined vs full-tree.
    #
    # Feature names match decoder/features.parquet exactly:
    #   bb_pos_20_2_H1 — Bollinger position (period=20, k=2) on H1 (importance 0.73)
    #   ema_dist_20_H1 — distance from EMA20 on H1 (z-score-like)
    #   ret_3_H1, ret_10_H1, ret_10_H4 — log returns
  exit:
    max_holding_hours: null   # exit_kind=manual_or_time only; sanity hold p50=0.00h, p95=0.32h, max=12.69h — sub-M5 sensitive, see risk_flags
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct  # lot p50=0.62, p95=11.57, p99=24.73, max=35.89 from $200 seed → equity-proportional compounding; sanity martingale=PASS (steps=0, max_streak=0)
citations:
  - "[systematic_trading, p.118-119, ch.7] — Carver: \"buy when the fast EWMA is above the slow EWMA, with the crossover volatility-standardised\" — EWMAC defines the canonical moving-average-distance momentum rule. ema_dist_20_H1 (top-3 tree feature) and bb_pos_20_2_H1 (top-1, midline-distance proxy) are direct EWMAC analogues on H1."
  - "[evidence_based_ta, p.397, p.415] — Aronson defines the Channel Breakout Operator (long when price crosses above the n-period max, short below the min) and the Moving Average operator (MA_t = Σ P_{t-i+1}/n). H1-scale BB-position + EMA-distance features used here are objective, computerizable instances of these operators, satisfying the EBTA rigor bar (Part I, ch.1-7)."
  - "[advances_fin_ml, p.159, p.160-167, ch.8] — López de Prado: \"Backtesting is not a research tool. Feature importance is.\" Tree feature importance is concentrated 0.94 on the four H1 momentum/trend features (bb_pos_H1, ret_3_H1, ema_dist_H1, ret_10_H1) — single-timeframe dominance corroborated by parallel univariate ranking (rank-4 bb_pos_H1, rank-5 ema_dist_H1) is the AFML substitution-effect cross-check."
  - "[machine_trading, p.159-160, ch.6] — Chan: \"for intraday strategies use compiled languages (C++, C#, Java)... due to ~10x latency difference\" and warns that \"intraday strategy with holding minutes can become impossible at scale\". Direct relevance: hold p50=0.00h (sub-minute) means latency-sensitive replication; M1 review is mandatory before any live test."
risk_flags:
  - "demo_account_vendor_selection_bias — IC Markets Demo (1:500 MT4); -0.10 confidence applied per workflow rule (system_info.json account_type=Demo)"
  - "needs_m1_review — hold p50=0.00h (sub-minute median), p95=0.32h (~19 min), max=12.69h. M5/M15 OHLC anchors used in Stage 1 features cannot resolve sub-minute exit logic. Stage 3 should re-extract on M1 (or tick) before scoring exit."
  - "intraday_news_window_unmodeled — top 5-min bucket is 15:30 UTC (69 trades, ~1.7x the next bucket at 17:00 UTC with 40 trades), aligning with US economic-data release timing on Gold. Replicator currently has no economic-calendar feed; momentum sign was inferred from observed trades only. If real strategy reads news, replication will diverge during data days. Treat as observed-trade-evidence only, not a calendar-aware implementation."
  - "exit_logic_unrecoverable — exit_kind=manual_or_time only; the actual exit trigger (time, target, indicator) is not in the fingerprint. Replicator must brute-force candidates against vendor equity curve (gain +220,189%, monthly 7.57%, DD 22.6%)."
  - "extreme_lot_scaling — lot p95/p50=18.65 (vs ~4 for sister Gold system 6541963); from $200 seed → max lot 35.89 implies ~180,000x compounding scale. Equity-proportional inferred but exact rule (volatility-target? fixed-fractional? Kelly?) unknown; Stage 3 must verify."
  - "gold_only_concentration — single instrument (XAUUSD); 1 stray SUMMAR trade ignored (likely parser artifact / summary row, not real position). 2017-09 → 2026-04 spans pre-COVID, 2020 spike, 2022-2024 Fed/inflation regimes — stationarity not assumed."
  - "max_gap_63_9_days — single 63.9d gap suggests broker change, code update, or paused tracking; edge persistence across the gap unverified."
  - "provisional_family — H1_MOMENTUM_GOLD is provisional=True in shared/decoder_taxonomy.py (n=1 prior support: 6541963). This system is the first independent candidate to confirm the family signature; per 5R-1-hardening §1, R1 must validate the n≥2 promotion criterion before removing provisional flag."
---

# Decoded signal — Happy Gold ICMarkets M30 (id 2421356)

## Family rationale

The fingerprint matches the provisional family `H1_MOMENTUM_GOLD` on every published criterion in `shared/decoder_taxonomy.py` (TAXONOMY[Family.H1_MOMENTUM_GOLD]):

| Criterion | Evidence | Met |
|---|---|---|
| Gold/XAU instrument | 1762/1763 trades XAUUSD; 1 stray SUMMAR row treated as parser noise | ✓ |
| Entry-on-H1-momentum | Tree top features bb_pos_H1 (0.73) + ret_3_H1 (0.12) + ema_dist_H1 (0.05) + ret_10_H1 (0.04) = 0.94 importance on H1 trend/momentum | ✓ |
| Tree balanced | 5-fold CV 0.875 ± 0.016; folds 0.852, 0.875, 0.866, 0.852, 0.898 — tight spread, no degeneracy; Buy% = 52.1% (near-balanced, not always-Buy) | ✓ |
| dir_acc > 0.7 | match_rate_cv = 0.875 > 0.7 | ✓ |

The system is also lineage-consistent with the family's prior anchor: same vendor (HappyForex), same instrument family ("Happy Gold" series), same H1-feature dominance pattern, mirror Demo-account selection bias. This system therefore qualifies as the n=2 supporting case the family needs to lose its `provisional=True` flag, pending R1 confirmation by the orchestrator (the decoder cannot promote unilaterally; that decision belongs to the user per 5R-1-hardening §1).

**Why not LATE_NY_BREAKOUT.** Requires 21-01 UTC concentration; here the top hour is 15 UTC (13.2%) and the 21-01 UTC range carries < 5% of trades combined. Direction is also balanced (Buy% 49-58% across top 5 hours), not breakout-typical asymmetry.

**Why not OVERLAP_NY_LONDON_RANGE.** Although top hours 15-17 UTC fall inside the canonical 12-16 UTC NY/London overlap, the family expects "BUY/SELL determined by position in BB or range" — a fade behaviour. The actual tree fires BUY when bb_pos_H1 > -0.09 (i.e. above lower band, including extended), not when price is near band extremes — that is trend/pullback continuation, not range-fade. Sign-check fails.

**Why not LONDON_OPEN_MOMENTUM/MR.** Requires 06-09 UTC concentration. Hour 09 has only 7.7% of trades; 06-08 UTC are not in the top 5. Window mismatch.

**Why not NEWS_RELEASE_MOMENTUM.** Family requires "≥1 bucket horário com >30% trades + name-flag NEWS/HF News". Top hour bucket (15 UTC) has only 13.2%, and the system name is "Happy Gold", not "Happy News" / "HF News". The 15:30 UTC 5-min peak is suggestive but does not meet the 30% threshold — kept as `risk_flag: intraday_news_window_unmodeled` rather than family.

**Why not FACTOR_SCALPING.** Hold p50=0.00h would by itself be compatible with sub-30-min scalping, BUT the load-bearing features are H1-scale (bb_pos_20_2_H1, ret_3_H1, ema_dist_20_H1, ret_10_H1 — sum 0.94 importance), not micro-timeframe. The taxonomy also flags FACTOR_SCALPING as "vazia pós-5R-0 — usar com cuidado" because Sonnet systematically misclassified Gold systems into it. H1_MOMENTUM_GOLD is the corrected slot.

**Why not SWING_TREND_MOMENTUM.** Requires median hold > 72h; here p50=0.00h, max=12.69h. Hold mismatch decisive.

**Why not MARTINGALE_GRID.** Sanity martingale=PASS, steps=0, max_streak=0. Lot scaling is equity-proportional on a compounding $200 → $438k account, not loss-doubling.

**Why not UNCATEGORIZED.** All four published H1_MOMENTUM_GOLD criteria are met simultaneously with strong tree CV (0.875) and surviving Bonferroni p < 1e-200 univariate confirmation — this is a positive identification, not absence of evidence. UNCAT would be honest only if a criterion failed; none did.

## Rule derivation

**Direction (rank-1 tree, CV=0.875 ± 0.016).** Tree topology has 9 features but feature-importance is concentrated 0.94 on the four H1 features. Walking the literal tree, BUY paths cluster on `bb_pos_20_2_H1 > -0.09` AND (`ema_dist_20_H1 > 0.76` OR `ret_3_H1 ≤ 0`). The cleanest single-feature reduction is rank-4 univariate `bb_pos_20_2_H1 > 0.07135 ⇒ Buy` (CV=0.853, coverage=0.50, Bonferroni-corrected p=1.8e-210 over 518 tests). The threshold 0.07135 is the literal Stage-1 cutoff (not invented). For higher recall, an OR-combination with rank-5 `ema_dist_20_H1 > 0.1122` (CV=0.850, p=6.4e-206) approximates the tree's ema_dist branch.

**Why not the RIPPER ruleset (rank-2, CV=0.840 ± 0.029).** RIPPER is a 34-clause disjunction — substantially more complex than the tree's 9 features and lower CV. Per Aronson [evidence_based_ta, p.287-288] more clauses → more overfit risk; per AFML First Law [advances_fin_ml, p.159] feature importance concentration (0.94 on 4 H1 features) is the parsimony signal. Tree wins on Occam's razor.

**Entry window.** Top 5 hours = {15, 16, 10, 17, 09} UTC, covering 912/1763 trades (51.7%). The 09-17 UTC window covers ~85% of activity — London + NY overlap on Gold (highest liquidity period). Direction by hour is near-flat (46-58% Buy); window is execution-quality / liquidity driven, not signal-asymmetry driven. The 15:30 UTC 5-min peak (69 trades, 3.9%) is ~1.7x the next bucket (17:00 UTC, 40 trades) — possibly aligned with US economic-data release timing, but kept as risk_flag (see above) since current evidence is observed-trade only, not calendar-aware.

**Exit.** Cannot recover deterministically. Hold p50=0.00h (sub-minute median), p95=0.32h (~19 min), max=12.69h. exit_kind=manual_or_time only. Stage 3 must brute-force candidates: (a) immediate next-M5-close, (b) fixed N-bar M1 exits, (c) tight ATR/percent target, (d) session-end at 17 UTC. Fitness criterion = match vendor's monthly 7.57% / DD 22.6% / total +220,189% over 8.7 years. Note: M5-anchored OHLC features in Stage 1 cannot validate sub-M5 exit timing — see `needs_m1_review` risk_flag.

**Sizing.** lot p50=0.62, p95=11.57, p99=24.73, max=35.89 from $200 deposit. Sanity martingale=PASS rules out loss-doubling. Equity-proportional compounding inferred (lot scales monotonically with compounding equity: $200 → $438,740 = ~2,194x; lot 0.62 → 35.89 = ~58x — broadly proportional with leverage-multiplier adjustment). p95/p50=18.65 is far higher than sister system 6541963 (4.11), suggesting more aggressive scaling rule; exact form unknown.

## Confidence breakdown

- **Family identification: 0.70** — All 4 H1_MOMENTUM_GOLD criteria met simultaneously; lineage-consistent with the family anchor (6541963). Provisional flag caps at 0.70 (cannot exceed established families until n≥2 promotion is ratified by R1).
- **Direction rule: 0.75** — Tree CV=0.875 ± 0.016 (5 folds tight 0.852-0.898) is highly stable; rank-4 univariate Bonferroni p=1.8e-210 over 518 tests is overwhelming. Strong, audited signal.
- **Exit logic: 0.30** — sub-minute hold p50 with manual_or_time only; Stage 3 must brute-force on M1; M5 features can't verify sub-M5 exit.
- **Sizing: 0.55** — non-martingale confirmed; equity-proportional compounding inferred but exact rule unknown.
- **Overall: 0.60** = weighted (family 0.20·0.70 + direction 0.40·0.75 + exit 0.25·0.30 + sizing 0.15·0.55) = 0.140 + 0.300 + 0.075 + 0.083 = **0.598**, then -0.10 Demo penalty, then +0.10 credit for n=1763 + 8.7-yr track + tight tree CV. Net **0.60**.

## Open questions (for Stage 3 + posteriores)

- **M1 re-extraction (blocker before exit scoring).** Hold p50=0.00h means median trade closes within the same M1 bar. Stage 1 features at M5/M15/H1 anchors cannot resolve sub-minute exit logic. Re-run the feature extractor with M1 OHLC anchors for this system before any replicator exit fit; otherwise exit_kind brute-force will be guessing on the wrong grid.
- **Calendar-aware variant.** 15:30 UTC peak coincides with the canonical US-data release window (NFP 12:30 UTC, FOMC/CPI/PPI 12:30-14:30 UTC, sometimes 14:00 UTC; 15:30 UTC = ~30 min post-release Gold reaction). Test whether masking US economic-event windows (±15 min) materially changes match-rate. If yes, family promotion to NEWS_RELEASE_MOMENTUM would need re-evaluation; if no, current H1_MOMENTUM_GOLD label stands.
- **Provisional family promotion.** With this system added to 6541963, H1_MOMENTUM_GOLD has 2 supporters. R1 orchestrator should evaluate: do both share enough mechanical signature (Gold + H1 dominance + tree balanced) to remove `provisional=True`? Or are they two superficially-similar but mechanically-distinct strategies that share a vendor heuristic?
- **Direction rule simplification.** Empirically test single-feature rule `bb_pos_H1 > 0.07135` vs OR-combined `bb_pos_H1 > 0.07135 OR ema_dist_H1 > 0.1122` vs full-tree replication. Lower complexity preferable per [advances_fin_ml, p.196-211] DSR/PBO.
- **Sister-system sizing-rule diff.** Why is lot p95/p50 = 18.65 here vs 4.11 on 6541963? Stage 3 should fit volatility-target / fixed-fractional / Kelly variants and pick the one that reproduces the lot trajectory.
- **Regime stationarity (3 sub-windows).** 2017-09 → 2020-03 (pre-COVID Gold), 2020-03 → 2022-03 (COVID spike + low rates), 2022-03 → 2026-04 (Fed hiking cycle, BRICS gold accumulation). Split match-rate by regime; if drop > 10pp post-2022, edge is regime-bound.
- **63.9d max gap.** Identify exact dates and likely cause (broker change, paused tracking after drawdown, code update). Material for replicator's reliability score.
- **Live viability under 1:500 leverage on Gold + 22.6% DD.** Even if signal replicates, real-money slippage on sub-minute holds at peak NY data times is severe. Tag as live-replication warning when ranking.
