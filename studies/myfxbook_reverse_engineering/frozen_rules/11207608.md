---
system_id: 11207608
family: H1_MOMENTUM_GOLD
confidence: 0.65
generated: 2026-05-02
rule:
  entry_window_utc: ["08:00", "16:59"]
  pairs: [XAUUSD]
  direction: |
    # Top tree (rank 1, CV=0.896±0.058 over 5 folds, coverage=1.00) on H1 features.
    # bb_pos_20_2_H1 importance=0.95; ema_dist_20_H1 importance=0.05.
    # The depth-4 tree degenerates at depth 1 — both ema_dist_20_H1 sub-splits
    # under bb_pos_20_2_H1 > -0.19 emit class=1 — so the operative rule is
    # univariate on bb_pos_20_2_H1. Threshold from candidates.json (not invented).
    BUY  if bb_pos_20_2_H1 > -0.19
    SELL if bb_pos_20_2_H1 <= -0.19
  exit:
    max_holding_hours: 0.4   # observed max=0.32h; p95=0.06h. Soft cap; real exits sub-M5.
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[trading_systems_methods, p.323-324] — '20-day Bollinger, 2 sigma ... If it''s not 20-day and 2 sigma, it''s not a Bollinger band' — exact match to feature bb_pos_20_2_H1 (window=20, k=2σ on H1)."
  - "[machine_trading, p.204-205, ch.7] — 'Bollinger Band mean-reversion — buy when price < MA − k·MSTD, sell when > MA + k·MSTD' — establishes BB-position as a directional primitive. The system inverts the MR sign (BUY above midline → trend reading), which is consistent with H1_MOMENTUM_GOLD's momentum-on-BB framing rather than fade."
  - "[advances_fin_ml, ch.5] — feature importance via tree-based methods. The univariate miner independently re-discovered the same bb_pos_20_2_H1 threshold (rank 4, CV=0.886, p_corr=1.0e-28 over n_tests=518) that the tree (rank 1) split on, supporting that the H1 BB-position is the load-bearing feature and not a tree-overfit artifact."
risk_flags:
  - "needs_m1_review — hold p50/p95/max = 0.00 / 0.06 / 0.32 h; p50 below M5 resolution. The H1 feature is the entry trigger but exit dynamics are sub-M5 and may depend on micro-structure (spread fills, broker tick) that a replicator running on H1/M5 OHLC cannot reproduce. Stage 3 should re-run on M1 OHLC if available."
  - "calendar_aware_replication_uncertainty — entry density at 16:00 UTC=15.3% + 15:00 UTC=13.4% overlaps the post-US-data window, but vendor name lacks any NEWS flag and top hour 15.3% is well below the NEWS_RELEASE_MOMENTUM 30%-bucket criterion. Classified strictly from observed trade/OHLC evidence; do NOT assume a live economic-calendar reader. If Stage 3 replication fails on the H1 rule alone, revisit whether vendor uses a calendar gate."
  - "ultra_short_hold_vs_H1_features — H1 features defining direction with sub-minute holds is mechanically odd; the H1 rule may be a *regime filter* with a separate sub-M5 trigger firing the actual entry/exit. Open question for Stage 3."
  - "drawdown_32.94pct — vendor-reported MDD 32.94% on 1:500 leverage with +83.63% gain. Replication on retail leverage will diverge."
  - "small_n — 202 trades over ~12.5 months; per-hour buckets thin (top hour n=31). Bootstrap any per-hour edge with caution."
  - "provisional_family_2nd_supporter — H1_MOMENTUM_GOLD is provisional (D7 2026-05-02; n=1 prior, system 6541963). 11207608 would be the 2nd supporter, a candidate to lift the family from provisional after R1 batch completes; until then this attribution itself is a review hypothesis, not a settled label."
---

# Decoded signal — Happy Gold - BBM (id 11207608)

## Family rationale

Provisional family `H1_MOMENTUM_GOLD` (registered 2026-05-02, D7; n=1 prior supporter `6541963`) defines
four criteria in `shared/decoder_taxonomy.py` `TAXONOMY[Family.H1_MOMENTUM_GOLD]`: Gold/XAU + entry-on-H1
-momentum + tree balanced + `dir_acc>0.7`. System 11207608 satisfies all four:

1. **Gold/XAU**: pair universe = `{XAUUSD: 202}` (system_info.json + fingerprint.md sanity).
2. **Entry-on-H1-momentum**: tree rank 1 (CV=0.896, coverage=1.0) is dominated by H1 features —
   `bb_pos_20_2_H1` importance 0.95, `ema_dist_20_H1` importance 0.05 (candidates.json rank 1; fold
   accs `[0.85, 0.825, 0.975, 0.95, 0.881]`). Univariate ranks 3-5 corroborate H1 features
   (`ema_dist_20_H1 > -0.27`, `bb_pos_20_2_H1 > -0.31`, `ret_10_H1 > -0.0013`, all with
   `p_corr < 1e-26` over `n_tests=518`). The cut `bb_pos_20_2_H1 > -0.19 ⇒ BUY` (above midline → long)
   is direction-following on the H1 BB midline — i.e. an H1-timeframe momentum reading of where price
   sits in the H1 BB envelope, not a BB fade.
3. **Tree balanced**: actions `{Buy: 104, Sell: 98}` (51.5%/48.5%); per-pair `buy_pct=51.5%`. No
   degenerate always-Buy/always-Sell baseline.
4. **`dir_acc > 0.7`**: tree CV match rate 0.896, std 0.058. RIPPER (rank 2) at 0.770 also clears.
   Univariate H1 features cluster at 0.886.

Why not the alternatives:

- **`NEWS_RELEASE_MOMENTUM`**: requires (a) clock-anchor with one bucket >30% of trades AND (b) a NEWS
  name flag. Top hour 16 UTC has only 31/202 = 15.3% (far under 30%); top 5min bucket 16:35 has
  7/202 = 3.5%. Vendor name is "Happy Gold - BBM", not Happy News. Both gating criteria fail. The
  user-supplied rule "p50 hold <5min alone is not enough — classify from observed trade/OHLC evidence"
  applies: the H1 tree (CV=0.896) is too strong to discard for an unobserved calendar reader. Recorded
  as `risk_flag: calendar_aware_replication_uncertainty` for Stage 3 audit.
- **`OVERLAP_NY_LONDON_RANGE`** (the v2 frozen-rule label, pre-R4 NaN holds): timing argument was the
  basis of the v2 attribution, but post-R4 hold p95 = 0.06h falsifies the family's "exit time-based 1-3h"
  signature by two orders of magnitude. Top hours include 08, 10, 11 UTC (49/202 = 24% outside the
  12-16 UTC band), further widening the mismatch. This R1 re-decode replaces the v2 OVERLAP attribution
  with H1_MOMENTUM_GOLD; v2 frozen_rules entry should be updated downstream.
- **`FACTOR_SCALPING`**: would match on hold p50 < 0.5h and distributed entry, but its
  `decoder_taxonomy.py` description is "scalping multi-fator — vol-targeting or pair-trading intraday".
  Single-asset Gold + single-feature-dominant tree (bb_pos_20_2_H1 = 95%) is a worse fit than the
  Gold-specific provisional family. decoder.md flags FACTOR_SCALPING as Sonnet-over-attributed (6→0
  in 5R-0); Opus should not re-inflate it.
- **`UNCATEGORIZED + reason_code=hold_mismatch`** considered: hold p50=0h on a system whose primary
  feature is on the H1 timeframe is mechanically unusual. But tree CV=0.896 and balanced classes mean
  the H1 BB position genuinely *predicts direction*; the short hold is an exit-style choice (sub-M5
  micro-structure), not an invalidation of the H1 entry signal. Recorded as
  `risk_flag: ultra_short_hold_vs_H1_features` instead.

## Rule derivation

Tree rank 1 verbatim:

```
bb_pos_20_2_H1 <= -0.19              → SELL (class 0)
bb_pos_20_2_H1 >  -0.19 ∧ ema <=1.42 → BUY  (class 1)
bb_pos_20_2_H1 >  -0.19 ∧ ema  >1.42 → BUY  (class 1)
```

The depth-4 tree degenerates at depth 2 — both `ema_dist_20_H1` sub-branches under
`bb_pos_20_2_H1 > -0.19` classify as `1` (Buy). The *operative* rule is therefore the depth-1 split
on `bb_pos_20_2_H1` at `-0.19`. Univariate rank-3 (`ema_dist_20_H1 > -0.2736`, CV=0.886) and rank-4
(`bb_pos_20_2_H1 > -0.3145`, CV=0.886) confirm the threshold sits near-midline (slightly negative,
matching the system's small Buy bias of 51.5%/48.5%). I take the tree's `-0.19` as the central
estimate (it has the lowest CV variance and balanced tree backing).

`entry_window_utc: [08:00, 16:59]` covers all top-5 entry hours (16, 15, 08, 11, 10 UTC = 106/202 =
52.5% of trades). Top 5-min buckets (16:35, 15:35, 08:45, 15:30, 16:30) span the whole window. No
tighter sub-window is justifiable given how distributed the entries are; a narrower window would
drop coverage below the literature-supported intraday-FX session band.

`max_holding_hours: 0.4` — observed max=0.32h, p95=0.06h. Replicator should treat as a soft cap;
real exits are tick-driven (sub-M5).

`sizing: proportional_equity_2pct` — default per retail cost-model best practice. Vendor's MT4 lots
2728-3416 (likely 0.27-0.34 mini-lot on a 1:500 cents-account) are not directly transferable to a
real retail account, so retail-equivalent sizing is the honest default.

## Confidence breakdown

- **Family identification: 0.65** — All four `H1_MOMENTUM_GOLD` criteria met cleanly. Demerit: the
  family is `provisional` (n=1 prior); 11207608 would be the 2nd supporter, lifting it toward
  non-provisional, but until R1 sample completes that's a forward expectation, not a fact.
- **Direction rule: 0.75** — Tree CV 0.896 ± 0.058 across 5 folds; corroborating univariate
  `p_corr ≈ 1.0e-28` over `n_tests=518` survives Aronson-style multiple-testing adjustment by ~26
  orders of magnitude. The depth-1 effective rule is robust.
- **Exit logic: 0.40** — `manual_or_time` exit_kind in 100% of trades, but actual hold dynamics are
  sub-M5 and the H1/M5 OHLC available to the replicator likely cannot reproduce them.
  `risk_flag: needs_m1_review`.
- **Overall: 0.65** — weighted toward family + direction (the parts with strong evidence), pulled
  down by exit uncertainty and the provisional-family caveat.

## Open questions (for Stage 3 + posteriores)

- Is `bb_pos_20_2_H1 > -0.19` the *entry trigger* or merely a *regime filter* with a separate sub-M5
  signal firing the actual entries within the H1 regime? Stage 3 replication on H1 close will likely
  generate too few signals; M1-with-H1-feature-as-filter is the more plausible architecture.
- Does the vendor use a calendar/news filter? Top hours 15-16 UTC overlap the post-US-data window.
  Without M1 + a calendar feed the replicator can't disambiguate. Compare against a
  `random_frequency_matched` baseline restricted to 08-17 UTC to see if the lift survives.
- Is the `-0.19` threshold (slightly below midline) economically meaningful or CV-tuned? A
  permutation test on the threshold (uniform over `[-0.4, 0.0]`) should retain CV ≥ 0.85 if the
  rule is genuine.
- 32.94% MDD on 1:500 leverage with retail `proportional_equity_2pct` — what is the equivalent retail
  MDD? Stage 3 must report under retail costs/leverage.
- Cross-validate against the 1st `H1_MOMENTUM_GOLD` supporter `6541963` — do the BB/EMA H1 thresholds
  match within ±20%? If yes, family graduates from provisional. If no, both may need a finer split
  (e.g. `H1_BB_GOLD` vs `H1_EMA_GOLD`).
