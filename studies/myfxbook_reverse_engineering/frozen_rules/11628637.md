---
system_id: 11628637
family: UNCATEGORIZED
confidence: 0.55
reason_code: taxonomy_gap
candidate_new_family: H1_MOMENTUM_CRYPTO
generated: 2026-05-02
rule:
  entry_window_utc: ["15:00", "19:00"]
  pairs: [BTCUSD]
  direction: |
    # Source: tree (rank 1, match_rate_cv=0.874 ± 0.045, coverage=1.0).
    # Top features (importance): ema_dist_20_H1=0.93, bb_pos_20_2_H1=0.06, atr_ratio_M5=0.01.
    # Tree text:
    #   |--- ema_dist_20_H1 <= 0.46
    #   |   |--- bb_pos_20_2_H1 <= -0.53 -> class 0
    #   |   |--- bb_pos_20_2_H1 >  -0.53 -> class 0
    #   |--- ema_dist_20_H1 >  0.46
    #   |   |--- atr_ratio_M5 <= 0.28 -> class 1
    #   |   |--- atr_ratio_M5 >  0.28 -> class 1
    # Both sub-splits collapse to the parent class -> the tree is effectively a
    # single threshold on ema_dist_20_H1 at 0.46. The bb_pos / atr_ratio splits
    # are ornamental; reported feature importances overstate multivariate structure.
    BUY  if ema_dist_20_H1 >  0.46
    SELL if ema_dist_20_H1 <= 0.46
    # Cross-check (independent miner) — univariate rank 3, CV 87.1%, p_corr=4.3e-30,
    # coverage 0.60: ema_dist_20_H1 > -0.4477 ⇒ Buy. Same feature, different (lower)
    # threshold, same direction → confirms H1-frame momentum is real, not a tree
    # mining artefact. Univariates rank 4-10 (ret_10_H1, ret_3_H4, bb_pos_20_2_H1/H4/M15,
    # ema_dist_20_H4, ret_10_H4) all confirm the same momentum-Buy bias on correlated
    # features. Replicator should NOT add them as independent gates — they restate
    # the same signal.
  exit:
    max_holding_hours: 2.5
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[algo_trading_chan, p.95, ch.4] — \"Apply a momentum filter (price above long-term moving average) as a gate\" (Chan). Tree's effective rule (ema_dist_20_H1 > 0.46 ⇒ Buy, else Sell) is exactly this primitive applied at the H1 timeframe with a normalised distance instead of a raw cross."
  - "[stocks_on_the_move, p.81-82] — \"Stock must trade above its 100-day moving average to be a buy candidate\" (Clenow). Same primitive (price-above-MA → long-only candidate), here adapted to the H1 timeframe with a two-sided variant (below-MA → short)."
  - "[evidence_based_ta, p.281, p.345] — \"NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run\" (Aronson). Univariate p_corr (1e-22 to 1e-30) is Bonferroni-style over n_tests=516, so the H1-momentum direction edge is not pure data-mining noise; the tree CV (0.874 ± 0.045) is the audit-grade evidence used for the rule."
  - "[advances_fin_ml, p.160-162, ch.5] — MDI/MDA feature importance: \"Mean Decrease Impurity (MDI) ... biased toward high-cardinality features\" (López de Prado). The 0.93 / 0.06 / 0.01 split here is MDI-style; the tree's degenerate sub-splits confirm the MDI bias warning — only ema_dist_20_H1 is a real gate."
  - "[machine_trading, p.202, ch.7] — \"for bitcoin trading, remember ~45% of exchanges fail due to thefts/hacks — credit risk, not just market risk\" (Chan). Replicator must price BTCUSD CFD venue risk (Vantage Markets, MT4) separately; signal-side reliability does not absolve broker-side risk."
risk_flags:
  - needs_m1_review
  - "hold p50 = 0.01h (~36s), p95 = 0.23h (~14min), max = 2.08h — sub-M5 timing. Fingerprint OHLC features are anchored on M5+ bars, so true entry/exit micro-timing is unobserved at this scale. M1 (or tick) re-anchor required before any replication score is taken seriously."
  - "Calendar-aware replication NOT assumed. The combination 'p50 hold ~36s' + 'entry concentrated 15-19 UTC (NY afternoon)' is consistent with US-data-release sniping (FOMC/CPI/NFP cluster around US morning/early afternoon UTC), but: (a) name 'Happy Bitcoin - VM' has NO NEWS/HF News flag; (b) top hourly bucket 17:00 UTC = 35/232 = 15.1%, well below the >30% NEWS_RELEASE_MOMENTUM threshold; (c) entries spread across 15-19 UTC, not single-bucket. Per instruction §8, classify only on observed trade/OHLC evidence — do not assume a live economic-calendar reader. If Stage 3 wants a calendar-aware variant, declare it as a separate hypothesis with explicit calendar source and report match-rate lift."
  - "ASSET MISMATCH vs taxonomy: BTCUSD is a 24/7 crypto pair on a CFD venue; the closed enum (LATE_NY_BREAKOUT, LONDON_OPEN_*, NY_SESSION_*, OVERLAP_NY_LONDON_RANGE, OVERNIGHT_GAP_FADE) is FX-session-centric. None of the 9 originals fit cleanly. Proposed candidate_new_family=H1_MOMENTUM_CRYPTO is a structural sibling of provisional H1_MOMENTUM_GOLD (same rule mechanics, different asset class)."
  - "TREE DEGENERACY — DecisionTree(max_depth=4) returns the SAME class on both children of every secondary split (left ⇒ class=0 always; right ⇒ class=1 always). The tree is effectively depth-1 on ema_dist_20_H1; reported feature importances (0.06 for bb_pos, 0.01 for atr_ratio) overstate multivariate structure (cf. AFML p.160-162 on MDI bias)."
  - "Single-asset BTCUSD edge (n_pairs=1). Strategy A mandate (CLAUDE.md §3) explicitly rejects single-asset edge for capital allocation; this signal_rule.md is a replication hypothesis for the reverse-engineering study, not a candidate for production."
  - "VENDOR / BROKER — vendor = HappyForex (folclore-known). Account is Real Vantage Markets (offshore-leaning, leverage 1:500, MT4); track record 2025-06-25 → 2026-05-01 ≈ 10 months. Real account does not absolve selection bias on high-leverage offshore brokers; OOS window is short and crypto regime changes are abrupt."
---

# Decoded signal — Happy Bitcoin - VM (id 11628637)

## Family rationale

This is the R1 (Opus 4.7) re-decode using the post-R4 fingerprint, in which
hold-time extraction was fixed (parser now uses `(closetime_ms - opentime_ms)/1000`
instead of positional column lookup; see `_diagnostics/5R-1-hardening.md` §R4).
For this system the fix changed `hold p50/p95/max` from `NaN/NaN/NaN` to
`0.01/0.23/2.08 h`, which is decisive: the prior decode could not test
intraday-vs-swing sanity, this one can.

The fingerprint shows a coherent mechanical pattern: BTCUSD only, n=232 over
~10 months, martingale PASS, lot p95/p50 = 1.24, sub-minute median hold
(~36 s), entry concentrated 15-18 UTC, tree CV match rate 0.874 driven almost
entirely by `ema_dist_20_H1 > 0.46 ⇒ Buy`. Univariate ranks 3-10 (ret_10_H1,
ret_3_H4, bb_pos_20_2_H1/H4/M15, ema_dist_20_H4, ret_10_H4) all corroborate
the same H1-frame momentum-Buy direction.

Within the closed `decoder_taxonomy.Family` enum (12 values), I checked every
candidate and ruled them out:

- **FACTOR_SCALPING.** Hold p50 = 0.01 h is now confirmed sub-30 min post-R4,
  so the family's hold criterion is met. But the spec
  (`decoder_taxonomy.py` L139-147) describes the edge as "vol-targeting ou
  pair-trading intraday" with "entry distribuído". Here the edge is a single
  H1 EMA-distance filter on a single asset (no pair-trade, no vol-targeting),
  and entry is concentrated 15-19 UTC (top 4 hours = 105/232 = 45.3%), not
  distributed. Combined with the post-5R-0 finding that 6/6 prior FACTOR_SCALPING
  labels were reclassified, prior against this label is high.
  (Decoder anti-pattern, `.claude/agents/decoder.md` L65, also warns.)
- **LATE_NY_BREAKOUT.** Timing wrong (15-18 UTC vs spec 21-01 UTC), asset
  wrong (BTC vs FX majors).
- **LONDON_OPEN_MOMENTUM / LONDON_OPEN_MR.** Timing wrong (06-09 UTC).
- **NY_SESSION_REVERSAL.** Timing partial-fit (15-16 UTC overlaps the lower
  bound of 12-16 UTC), but direction is momentum-following, not reversal.
  Family is also flagged empty post-Wave 1+2+3 (vendor library has no genuine
  reversal).
- **OVERLAP_NY_LONDON_RANGE.** Timing partial-fit, but spec calls for direction
  determined by BB or range position (range-fade). Here the BB-pos univariates
  (rank 6, 8, 9) are co-linear with ema_dist (all positive thresholds ⇒ Buy),
  i.e. they are restating the same momentum signal, not an independent
  range-position gate.
- **OVERNIGHT_GAP_FADE.** No weekend-gap structure; entries are intraday
  NY-afternoon, not Friday-tail / Monday-open.
- **MARTINGALE_GRID.** Sanity PASS, steps=0, max_streak=0.
- **SWING_TREND_MOMENTUM (provisional).** Disqualifies cleanly: criterion
  hold p50 > 72 h, observed p50 = 0.01 h.
- **NEWS_RELEASE_MOMENTUM (provisional).** Criterion (`decoder_taxonomy.py`
  L188-191): "Clock-anchored ≥1 bucket horário com >30% trades + name-flag
  NEWS/HF News". Observed: top hour 17:00 UTC = 35/232 = 15.1% (below 30%);
  name "Happy Bitcoin - VM" carries no NEWS/News flag. Disqualifies cleanly,
  even though sub-minute hold is reminiscent of news-window sniping (handled
  via risk_flag, not via family — instruction §8 of the brief).
- **H1_MOMENTUM_GOLD (provisional).** Criterion: "Gold/XAU + entry-on-H1-momentum
  + tree balanced + dir_acc>0.7". The asset criterion (Gold/XAU) is the defining
  one — BTCUSD fails it. The other three (H1 momentum, balanced Buy/Sell ≈ 50.4%,
  tree CV 0.874 > 0.7) all match. The natural reading is that H1_MOMENTUM_GOLD
  describes a Gold-specific instance of a more general pattern, and BTCUSD here
  is a *crypto* sibling.

This is what the contract calls a `taxonomy_gap`: a coherent strategy outside
the current enum. Per `5R-1-hardening.md` §1 and `.claude/agents/decoder.md`
L88-92, the honest output is `family=UNCATEGORIZED + reason_code=taxonomy_gap +
candidate_new_family=H1_MOMENTUM_CRYPTO`. The proposed name mirrors
H1_MOMENTUM_GOLD's structure and signals the registrar that — if a 2nd
crypto-momentum HappyForex system surfaces in a later wave (Happy Bitcoin
appears to be a multi-broker/multi-config product line) — the taxonomy could
absorb it as a provisional sibling under the same n=1 + citation +
user-approval criterion.

## Rule derivation

All thresholds are quoted from `decoder/candidates.json` directly — none invented.

- **Direction (primary):** Tree (rank 1, CV 0.874 ± 0.045, fold accs 0.804 /
  0.848 / 0.891 / 0.891 / 0.938, coverage 1.0). The tree's secondary splits on
  `bb_pos_20_2_H1` (at -0.53) and `atr_ratio_M5` (at 0.28) do not flip the
  class — both subtrees under `ema_dist_20_H1 ≤ 0.46` resolve to class 0, both
  subtrees under `> 0.46` resolve to class 1. So the rule reduces to a single
  threshold. I keep the tree threshold (0.46) because it has coverage 1.0;
  the univariate threshold (-0.4477) is on a different operating point and
  would invert typical/atypical proportions.

- **Direction (cross-checks):** ranks 3-10 univariates all "indicator above
  small-magnitude threshold ⇒ Buy", on H1 / H4 / M15 momentum and BB-position
  features. They are co-linear (correlated features restating the same H1
  momentum direction); replicator should NOT chain them as independent gates.

- **Entry window:** top hours by activity are 17:00 (35), 16:00 (33), 18:00
  (21), 15:00 (16), 11:00 (15). The contiguous 4-hour block 15:00-18:59 UTC
  captures 105/232 = 45.3% of trades. 11:00 is non-contiguous; including it
  raises coverage only to 51.7% and breaks the contiguity, so I exclude it.
  Direction by hour at the top buckets is mixed (16:00 buy% 45.5, 17:00 buy%
  54.3, 18:00 buy% 33.3), consistent with the rule being driven by the H1
  EMA filter rather than by the hour itself.

- **Exit:** all 232 trades have `exit_kind=manual_or_time`. With p95 hold =
  0.23 h and max = 2.08 h, I set `max_holding_hours = 2.5` (round up from
  observed max). No TP/SL signal in the fingerprint, so both null. Stage 3
  should still sweep time-stops (1h / 2h / 2.5h / 4h) and report sensitivity,
  because `manual_or_time` is opaque to whether the closure was time-based
  or signal-flip (signal-flip would behave indistinguishably when ema_dist
  crosses 0.46).

- **Sizing:** lot p50/p95 = 95890/119045, ratio 1.24, max_streak=0,
  martingale=PASS. Account grew from $1k deposit to $7,167.88 (gain +616.84%,
  monthly 19.55%, drawdown 16.41%). Lot scales roughly with balance (no
  fixed-lot signature). I default to `proportional_equity_2pct` as the closest
  standard sizing — replicator will tune scale.

## Confidence breakdown

- Family identification: 0.45 — pattern is coherent (H1 EMA momentum on BTC
  intraday) and post-R4 hold data lets me rule out provisionals cleanly, but
  no enum family fits; UNCATEGORIZED with taxonomy_gap is the only honest
  call. I weight "is the enum's home for this clear?" (low) more than
  "is the underlying mechanic clear?" (high).
- Direction rule: 0.80 — tree CV 0.874 ± 0.045, three independent univariates
  agreeing on H1 momentum-Buy direction, single dominant feature, robust to
  fold variation.
- Exit logic: 0.50 — `manual_or_time` for all trades is consistent with
  time-based or signal-flip; the rule encodes a time bound but cannot
  discriminate between the two from this fingerprint alone.
- Overall: 0.55 = mean weighted (family 0.45 × 0.4 + direction 0.80 × 0.4
  + exit 0.50 × 0.2 = 0.18 + 0.32 + 0.10 = 0.60), then -0.05 vendor
  adjustment (decoder.md L180: account is Real so no -0.10; broker Vantage
  Markets is offshore folclore-tier, applying -0.05). Net 0.55.

## Open questions (para Stage 3 + posteriores)

- **Sub-M5 micro-timing.** Hold p50 = 36 s is below the M5 grid the fingerprint
  was extracted on. Replicator must re-anchor on M1 (or tick) BTCUSD data
  before scoring, otherwise execution slippage will dominate any measured edge.
  `risk_flag: needs_m1_review` is set per instruction §9 of the decode brief.
- **Calendar-aware variant.** Stage 3 should test the rule both ways: pure-OHLC
  replication (no calendar) AND a calendar-anchored variant with an explicit
  FOMC/CPI/NFP/NFPa source, and report match-rate lift between the two. If
  calendar-anchored adds substantial match, escalate to NEWS_RELEASE_MOMENTUM
  downgrade discussion (the >30% bucket threshold could be wrong for a
  multi-release window).
- **Threshold robustness.** Tree threshold 0.46 has CV std 0.045 (low). But
  univariate rank 3 puts the same feature's threshold at -0.4477 with
  comparable CV. Replicator should grid the threshold and report sensitivity;
  document whether the BTC `ema_dist_20_H1` distribution has structural break
  points around either value.
- **Hour-window filter.** Test whether restricting entries to 15-19 UTC
  degrades match-rate vs running 24/7. If 24/7 entries match equally well,
  the timing concentration is a side-effect of when the EA wakes up / scans,
  not an edge.
- **Regime stability.** Track record is 10 months only. Split into halves and
  test direction-rule match-rate on each — momentum strategies on BTCUSD have
  historically severe regime sensitivity (2022 vs 2023 vs 2024).
- **Family registration.** If R1+ surfaces a 2nd crypto-only system with H1
  momentum and intraday hold, propose `H1_MOMENTUM_CRYPTO` as a provisional
  sibling of `H1_MOMENTUM_GOLD` per the n=1 + citation + user-approval
  criterion in `5R-1-hardening.md` §1.
