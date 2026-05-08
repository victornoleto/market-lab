---
system_id: 1603276
family: UNCATEGORIZED
confidence: 0.45
reason_code: taxonomy_gap
candidate_new_family: INTRADAY_TREND_SCALP
generated: 2026-05-02
rule:
  entry_window_utc: ["09:00", "17:59"]
  pairs: [EURUSD, GBPUSD, USDJPY, XAUUSD]
  direction: |
    # Tree (rank 1, CV 0.827, coverage 1.0). Simplified to the dominant first-level
    # split + single H1-momentum confirmation. Lower-importance leaves
    # (range_norm_H4, atr_ratio_M15, bb_pos_20_2_M5) drop because their importance
    # is <=0.04 and they do not change the leaf class outcome (every leaf inside
    # ema_dist_20_H1 > -0.27 AND ret_3_H1 <= 0 is class 1).
    #
    # Feature names match Stage 1 features.parquet schema.
    BUY  if ema_dist_20_H1 > -0.27 and (ret_3_H1 <= 0.0 or ret_10_H1 > 0.0)
    SELL if ema_dist_20_H1 <= -0.27
    SELL if ema_dist_20_H1 > -0.27 and ret_3_H1 > 0.0 and ret_10_H1 <= 0.0
  exit:
    max_holding_hours: 1.1
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_0_31
citations:
  - "[evidence_based_ta, p.397] — \"Channel Breakout Operator (CBO) — Trend-following operator: long signal when the series crosses above the maximum of the last n periods; short when it crosses below the minimum.\""
  - "[evidence_based_ta, p.271, p.287] — \"Data-mining bias — Systematic positive bias in the observed performance of the best rule when several are tested; observed performance exceeds expected performance.\""
  - "[algo_trading_chan, p.133, ch.6] — \"Time series momentum — past returns of a single instrument are positively correlated with future returns.\""
  - "[algo_trading_chan, p.153-154, ch.6] — \"two broad strategy families — mean reversion and momentum — each with distinct risk-return signatures.\""
risk_flags:
  - "needs_m1_review — hold p50=0.00h, p95=0.06h (~3.6min), max=1.06h. Sub-M5 sensitive: replicator must consume M1 OHLC (or tick proxy) for a meaningful entry/exit fit. Project timeframe unchanged; this is a per-system data-grain ask, not a code-level change."
  - "single-factor edge — tree importance concentrated in ema_dist_20_H1 (0.71); other features <=0.16. Distinct from FACTOR_SCALPING which decoder_taxonomy.py describes as multi-factor (vol-targeting / pair-trading)."
  - "vendor name says 'Breakout' but timing/direction signature does not match LATE_NY_BREAKOUT (21-01 UTC) or any classical channel-breakout fingerprint — name is marketing, not mechanics."
  - "short track ~1.6y (2016-01-25 → 2017-09-07, account closed). Insufficient horizon to fight data-mining bias on Stage-1 best-of-K candidate selection [evidence_based_ta, p.271, p.287]."
  - "calendar-aware replication unverified — fingerprint shows no clock-anchor bucket > 5.2% (top is 15:30 UTC at 31/594), so a live economic-calendar feed is NOT assumed; flagged here as Open Question for replicator if downstream evidence reverses this read."
---

# Decoded signal — Happy Breakout v1.0 (Closed AU account) (id 1603276)

## Family rationale

The closed `decoder_taxonomy.Family` enum does not have a clean fit for this fingerprint, and forcing one of the existing labels would be unfaithful to the evidence. Walking the enum:

- **Session-anchored intraday families don't fit timing.** `LATE_NY_BREAKOUT` requires entry concentration 21-01 UTC; here the top-5 hours are 10, 15, 09, 17, 11 UTC — pure London/NY-session bulk, no late-NY peak. `LONDON_OPEN_MOMENTUM`/`LONDON_OPEN_MR` need 06-09 UTC; here the 09 bucket is only 57/594 (9.6%) and 10 UTC dominates (72/594 = 12.1%). `OVERLAP_NY_LONDON_RANGE` (12-16 UTC) catches part of the mass but fails the direction test — the family is BB-position / range-fade driven, while this tree is trend-driven (ema_dist_20_H1 = 0.71 importance) and the simple univariates are all "X > threshold ⇒ Buy" momentum-following. `NY_SESSION_REVERSAL` is empty post-Wave 1+2+3 vendor finding and direction here is not reversal-shaped.
- **Provisional families don't fit either.** XAUUSD is only 16/594 trades (2.7%) — this is not `H1_MOMENTUM_GOLD` (gold-centric, n=1 system 6541963). `NEWS_RELEASE_MOMENTUM` requires ≥1 hour-bucket >30%; here the top 5-min bucket is 15:30 at 31/594 = 5.2% and the top hour is 12.1%, both far below threshold; the vendor name is "Breakout", not "News". `SWING_TREND_MOMENTUM` needs median hold >72h; here p50=0.00h and max=1.06h — the inverse pattern.
- **`FACTOR_SCALPING` was the closest existing label by hold + entry-distribution criteria** (entry distributed across multiple London/NY hours; p50 hold confirmed sub-30min post-R4 fix). But (a) `decoder_taxonomy.py` describes it as multi-factor / vol-targeting / pair-trading intraday; here a *single* feature (ema_dist_20_H1) carries 71% of tree importance with the rest <=0.16, so the "multi-factor" core is absent. (b) The 5R-1-hardening hardening note explicitly warns that the family was emptied 6→0 in the Opus re-decode because Sonnet "errava aqui sistematicamente" pre-R4. With only one strong factor and no vol/pair-trade structure, claiming `FACTOR_SCALPING` would re-introduce the same Sonnet failure mode against the spirit of the hardening.
- **`MARTINGALE_GRID` is ruled out by Stage 1** (k1_pass=PASS, lot p95/p50=1.29, max_streak=1).

Coherent pattern + no clean enum fit ⇒ honest output is `UNCATEGORIZED` with `reason_code=taxonomy_gap` and `candidate_new_family=INTRADAY_TREND_SCALP` per the 5R-1-hardening Wave B contract. The pattern this proposes — distributed entries during liquid London/NY hours, ultra-short hold, single dominant H1 trend-filter direction logic — is conceptually adjacent to but distinct from FACTOR_SCALPING (which is multi-factor by definition in `decoder_taxonomy.py`). Whether `INTRADAY_TREND_SCALP` graduates from `candidate_new_family` to a real Family entry is a downstream R1 decision, contingent on a 2nd independent system showing the same signature [`5R-1-hardening.md` §1].

The vendor name is "Happy Breakout v1.0" — Aronson's classical breakout primitive is the Channel Breakout Operator [evidence_based_ta, p.397], which signals on a price crossing the max/min of the last n periods. The fingerprint shows nothing of that shape: no clock-anchor consistent with a daily/session-range break, no `range_norm` or `prior_bar_sign` features at the top of the tree, just a price-vs-EMA20 trend filter on H1. The "breakout" naming is marketing; the mechanics are intraday trend-following scalp.

## Rule derivation

Direction logic comes from the rank-1 tree (CV match 0.827 ± 0.018, coverage 1.0). I kept the dominant first split (`ema_dist_20_H1` at -0.27, importance 0.71) and the second-tier H1 momentum confirmations (`ret_3_H1`, `ret_10_H1` at 0.0; combined importance 0.22). The deeper leaves (`atr_ratio_M15 <= 0.76`, `range_norm_H4 <= 1.41/0.83`, `bb_pos_20_2_M5 <= 0.43`) were dropped because they do not change the leaf class — every leaf inside `ema_dist_20_H1 > -0.27 AND ret_3_H1 <= 0.0` is class 1 (Buy), every leaf inside `ema_dist_20_H1 > -0.27 AND ret_3_H1 > 0.0 AND ret_10_H1 > 0.0` is class 1, and every leaf inside `ema_dist_20_H1 <= -0.27` is class 0 (Sell). The simplification preserves the deterministic part of the tree.

I deliberately did **not** import the rank-2 RIPPER ruleset (CV 0.742, 19 conjunctions). Its CV is materially below tree (-0.085) and the rule count plus its appeal to `dollar_index_proxy=-0.333` and tight bins like `ret_10_H1=0.0038-0.0055` smell like data-mining noise that Aronson explicitly warns against [evidence_based_ta, p.271, p.287]. The univariates rank 3-10 are all directional confirmations of the same H1/H4 trend-momentum gradient already captured by the tree (`ema_dist_20_H1 > -0.3842 ⇒ Buy`, `bb_pos_20_2_H1 > -0.3283 ⇒ Buy`, `ret_10_H1 > -0.0007909 ⇒ Buy`, etc.) — they reinforce that the edge is "trade in the direction the H1 is leaning", consistent with Chan's time-series-momentum primitive [algo_trading_chan, p.133, ch.6]. Using the tree alone keeps the rule executable without redundant rules.

Entry window: `[09:00, 17:59]` UTC covers the 5 top hours that account for 51% of trades (10:72 + 15:69 + 09:57 + 17:56 + 11:47 = 301/594). It deliberately spans both London bulk and NY morning rather than picking a session — the fingerprint shows no single clock anchor, just liquid-hours bias. Exit `max_holding_hours=1.1` is empirical from `hold max=1.06h`; TP/SL pips left null because the fingerprint has 100% `manual_or_time` exit kind and no candidate captured a pip threshold. Sizing fixed at 0.31 lot (matches `lot p50=0.31`, `p95=0.40`, `p99=0.41`) — no martingale, no equity-proportional behavior detected (lot p95/p50 = 1.29).

The tree CV match rate of 0.827 looks strong but must be discounted for data-mining bias because Stage 1 selected this rule from the best-of-K of three miners over 56 candidate features [evidence_based_ta, p.271, p.287]. Unbiased Stage 3 replicator + comparator with baselines (5R-1 Wave C item 2) is the real test. The 1.6-year track and account closure also caps how much horizon there is to fight overfitting.

## Confidence breakdown

- Family identification: 0.45 — pattern is coherent and well-mined, but no closed-enum family fits cleanly; `taxonomy_gap` is the honest call rather than a forced fit. Lower than 0.50 because if a 2nd system in R1 lands on the same signature, the candidate family graduates; if not, the right downgrade is still UNCAT.
- Direction rule: 0.65 — tree CV 0.827 ± 0.018 is stable across 5 folds (range 0.805-0.847), and the simplification preserves the class outcome at every leaf. Discounted for data-mining bias.
- Exit logic: 0.40 — only `manual_or_time` is observed; the actual exit mechanism (TP/SL pip thresholds, M1 trail, time stop) is unobservable from MyFxBook trade list. Replicator must treat `max_holding_hours=1.1` as upper bound and try TP-only / time-only variants.
- Overall: 0.45 — direction quality cannot exceed family-identification quality because a strong direction rule on the wrong family is still mis-classified. The weighted mean (0.40 × family + 0.40 × direction + 0.20 × exit = 0.52) is therefore capped at family confidence and rounded to 0.45.

## Open questions (para Stage 3 + posteriores)

- **M1 OHLC**: with hold p50=0.00h and p95=0.06h (~3.6min), any replicator running on M5 or coarser will mis-time entries and exits. Stage 3 must consume M1 (and ideally tick) for this system. Project timeframe stays unchanged for the rest of the pipeline; this is a per-system data-grain ask. (`risk_flag: needs_m1_review`)
- **Calendar-aware replication**: if subsequent inspection (or an R1 sibling system on the same vendor) shows a real news-release linkage, the replicator may need an economic-calendar feed. Current evidence does **not** support a live calendar reading (no clock-anchor bucket > 5.2%, name is "Breakout" not "News") — this stays as Open Question, not assumption.
- **Direction simplification**: can the rule collapse further to `ema_dist_20_H1 > -0.27 ⇒ Buy else Sell` (single-feature univariate)? The univariate rank-3 already gets CV 0.835 with coverage 0.60 — Stage 3 should A/B the simplified vs the tree-derived form to detect overfit-by-tree-depth.
- **Vendor-naming validity**: "Happy Breakout v1.0" is a HappyForex product. The 5R-0/5R-1 finding is that vendor name often does not predict mechanics. R1 should look for sibling HappyForex products with the same `INTRADAY_TREND_SCALP` signature (distributed London/NY hours + sub-30min hold + single H1-trend-filter direction) to either graduate the candidate family or downgrade this entry permanently.
- **Edge persistence**: account closed 2017-09-07, ~7.7 years before today (2026-05-02). Even if the Stage 3 replicator reproduces 2016-2017 trades, OOS edge is unknown — the closure itself is mild evidence the strategy stopped working or hit a drawdown threshold the operator could not tolerate. Survives as historical reverse-engineering target, not as live-tradable hypothesis.
