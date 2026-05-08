---
system_id: 10067081
family: UNCATEGORIZED
reason_code: mixed_strategy
candidate_new_family: null
confidence: 0.55
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]   # no session concentration; top hour 03 UTC = 11.6%
  pairs: [USDJPY, GBPUSD, USDCAD, AUDUSD, EURGBP, EURCHF]
  direction: |
    # WEAK signal — tree CV match_rate=0.562 vs Always-Buy baseline=0.516 (+4.6pp only).
    # RIPPER (0.488) is WORSE than baseline → degenerate.
    # The best one-liner approximation from candidates.json rank 1 (tree max_depth=4):
    #   primary split: ret_3_H4 sign + bb_pos_20_2_H1 + ema_dist_20_H4
    # Replicator should encode the full tree, but the human-readable summary is:
    #   "go long when H4 momentum is non-negative and BB position is not in extreme low,
    #    short otherwise; many trades remain effectively coin-flips."
    BUY if (ret_3_H4 > 0 and bb_pos_20_2_H1 > -1.06 and bb_pos_20_2_M15 > 0.07)
    BUY if (ret_3_H4 > 0 and ret_10_H4 > 0.01 and bb_pos_20_2_H4 <= 1.13 and ema_dist_20_H1 <= 2.05)
    BUY if (ret_3_H4 > 0 and ret_10_H4 > 0.01 and bb_pos_20_2_H4 > 1.13)
    BUY if (ret_3_H4 > 0 and ret_10_H4 <= 0.01 and pair_cluster_dispersion > 0)
    BUY if (ret_3_H4 > 0 and ret_10_H4 <= 0.01 and pair_cluster_dispersion <= 0 and bb_pos_20_2_H1 > 0.54)
    SELL otherwise
  exit:
    max_holding_hours: 213.72         # p95 hold; mediana=3.00h, p95=213.72h, max=4449h
    take_profit_pips: null            # exit_kind=manual_or_time across 4000/4000 trades
    stop_loss_pips: null
  sizing: fixed_lot_0.01              # lot p50/p95/p99/max all = 0.01 (no scaling, no martingale)
citations:
  - "[advances_fin_ml, ch.3, p.78-89] — triple-barrier/meta-labeling: when a primary classifier barely beats the always-buy baseline (here +4.6pp on CV), label noise dominates and the rule cannot be meaningfully separated from class-prior."
  - "[advances_fin_ml, p.207-211] — Law 2 of backtesting + DSR/PBO: under multiple-comparison stress (n_tests=550 for univariates), apparent edges of ~5pp need a much larger CV margin to survive."
  - "[algo_trading_chan, p.16, p.133, ch.6] — momentum vs mean-reversion taxonomy is binary; a system that is simultaneously intraday (median 3h) and swing (p95 ~9 days, max ~6 months) on FX majors with no session concentration is not a clean member of either family."
  - "[testing_tuning, Pardo, p.143-144] — selection bias on multi-peak fingerprints: when no single timing/feature peak dominates, attempting to fit a single rule overstates edge."
risk_flags:
  - "Hold distribution mixed: p50=3h vs p95=213.72h vs max=4449h (~6 months) — 3 orders of magnitude span suggests at least 2 sub-strategies coexist or a discretionary tail of long-held losers."
  - "Tree CV match_rate=0.562 only +4.6pp above Always-Buy baseline (0.516); RIPPER ruleset 0.488 is WORSE than baseline → degenerate ruleset."
  - "Drawdown 80.92% on the live equity curve (system_info.json) with current equity = 29.44% of balance: classic blow-up-in-progress on the long-tail held positions, even though martingale sanity PASSES (no lot escalation)."
  - "No session concentration: top hour 03 UTC = 465/4000 = 11.6%; activity spread across Asian close, late-London, NY overlap → no clock-anchored thesis."
  - "Buy_pct ~50% across every pair and every top hour → no per-pair / per-session directional bias to exploit; replicator must encode the full tree, not a session+sign shortcut."
---

# Decoded signal — Happy Frequency FM (id 10067081)

## Family rationale

The fingerprint does not match any of the 12 closed-taxonomy families and the
violation is not "novel coherent pattern" (which would be `taxonomy_gap`) — it
is **multiple sub-strategies cohabiting in one track-record**, which the
taxonomy explicitly handles via `reason_code=mixed_strategy`.

Evidence against a single-family fit:

1. **No session concentration.** The top entry hour (03 UTC) is only 11.6% of
   trades, and activity is distributed across 03 (11.6%), 10 (6.9%), 17 (6.9%),
   18 (6.4%), 15 (5.9%) — five distinct peaks across Asian close,
   late-London, and NY overlap. None of {LATE_NY_BREAKOUT (21-01),
   LONDON_OPEN_* (06-09), NY_SESSION_REVERSAL (12-16),
   OVERLAP_NY_LONDON_RANGE (12-16), OVERNIGHT_GAP_FADE (Fri/Mon)} fits.
2. **Mixed hold horizon.** p50 = 3h (intraday), p95 = 213.72h (~9 days,
   swing), max = 4449h (~6 months). FACTOR_SCALPING needs <30min holds → fails.
   SWING_TREND_MOMENTUM needs **median >72h** (criterion in
   `decoder_taxonomy.py` line 204) → 3h median fails by 24x.
3. **Pure FX, no Gold.** Excludes provisional H1_MOMENTUM_GOLD.
4. **No name flag + no >30% bucket.** Excludes provisional
   NEWS_RELEASE_MOMENTUM (criterion line 189).
5. **No martingale.** lot p95/p50 = 1.0, max_streak = 0 → MARTINGALE_GRID
   ruled out.
6. **Tree only +4.6pp over Always-Buy baseline** (0.562 vs 0.516); RIPPER is
   *worse* than baseline (0.488). Per López de Prado [advances_fin_ml,
   ch.3], when the primary classifier barely separates from the class prior,
   the labels are dominated by noise and the rule cannot be cleanly
   attributed to any single thesis — exactly the symptom of mixed strategies
   averaging into a near-coin-flip aggregate.

The top tree features (ret_3_H4=0.24, bb_pos_20_2_H1=0.17, bb_pos_20_2_H4=0.13,
ema_dist_20_H4=0.12) DO suggest **H4/H1 multi-timeframe momentum + BB
position** is *one* of the sub-strategies — but the 3h-median hold does not
match an H4-momentum thesis, and the 213h-p95 tail looks more like
discretionary holding of underwater positions than a planned swing leg
(consistent with the 80.92% live drawdown and current equity at 29.44% of
balance — a blow-up-in-progress on the long-tail).

Therefore the honest classification is `UNCATEGORIZED` with
`reason_code=mixed_strategy`. This is the "legitimate UNCAT" branch
(decoder_taxonomy.py line 161, citing [advances_fin_ml, ch.3] on label
consistency over forced labels), not a bucket-de-fuga.

## Rule derivation

The replicator-executable approximation encodes the **full tree from
candidates.json rank 1** (max_depth=4 sklearn DecisionTree, fold_accs=[0.615,
0.5225, 0.55375, 0.57, 0.5475], CV mean 0.562 ± 0.031). I did NOT collapse it
to a univariate "ret_3_H4 > 0 ⇒ Buy" because:

- The univariates in ranks 3-10 all have very low Buy thresholds (e.g.,
  `ema_dist_20_M15 > -1.027 ⇒ Buy`, `bb_pos_20_2_H4 > -0.7121 ⇒ Buy`) — these
  are essentially "if not in extreme negative momentum, BUY," which is just a
  thin slice over the Always-Buy baseline (0.516).
- Coverage of top univariates is 0.6-0.8 with match_rate 0.54-0.56 — not
  meaningfully better than the tree's 1.0 coverage at 0.562.
- The tree's secondary splits (e.g., bb_pos_20_2_H1 ≤ -1.06 → always class 0,
  ret_10_H4 > 0.01 → mostly class 1) are the only place where conditional
  match-rate plausibly exceeds 0.6 — and even then the gains are inside the
  fold-acc spread (0.522-0.615).

`max_holding_hours=213.72` (p95) is set so the replicator captures the swing
leg without amplifying the 6-month outlier max (which is almost certainly a
discretionary held-loser, not a planned exit). `sizing=fixed_lot_0.01` is
literal from the fingerprint (lot p50/p95/p99/max all 0.01).

## Confidence breakdown

- Family identification: **0.65** — high confidence the system does NOT fit
  any of the 12 enum families (each has at least one disqualifying criterion
  documented above). Confidence that `mixed_strategy` is the *correct*
  reason_code (vs `degenerate` or `insufficient_evidence`) is 0.65: the
  3-orders-of-magnitude hold span is the smoking gun for mixed.
- Direction rule: **0.45** — the tree barely separates from the baseline
  (+4.6pp); replicator will likely match ~56% of original trades, which is
  acceptable for a UNCAT system but not strong evidence the rule captured
  the actual logic.
- Exit logic: **0.50** — exit_kind=manual_or_time on 100% of trades and
  6-month max-hold tail strongly suggest the underlying system uses TP/SL
  that we cannot recover from MyFxBook closed trades alone.
- Overall: **0.55** = weighted mean (family identification weighted highest
  since it drives the contract output).

## Open questions (para Stage 3 + posteriores)

- Stage 3 replicator should compare match-rate of (a) full tree from rank 1,
  (b) Always-Buy baseline, (c) "ret_3_H4 > 0 ⇒ Buy". If (a) - (b) < 3pp on
  forward sample, downgrade to `reason_code=degenerate` and confidence < 0.4.
- The 213h p95 vs 3h p50 split begs for a sub-population analysis: cluster
  trades by `hold_hours` (k=2 KMeans) and re-mine candidates per cluster.
  If the short cluster (median ~1-2h) shows clean session signature and the
  long cluster (median ~5-10d) shows H4-trend signature, the system is
  decomposable into two sub-strategies and should be split in the tracker.
- 80.92% drawdown with current equity at 29.44% of balance means we are
  observing the system during/after a blow-up — Stage 3 reliability score
  must NOT confuse "matches MyFxBook trades" with "would be safe to clone."
  This system is a documentation artifact, not a candidate for any
  Plano A/B/C reactivation.
