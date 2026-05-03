---
system_id: 11155858
family: UNCATEGORIZED
confidence: 0.30
reason_code: degenerate
generated: 2026-05-02
rule:
  entry_window_utc: ["12:00", "20:00"]
  pairs: [EURGBP]
  direction: |
    # The depth-4 decision tree (rank-1 candidate, CV match=0.8076) collapses
    # every leaf to class=1 (Buy) regardless of the ret_1_H4 split:
    #   |--- ret_1_H4 <= -0.00 → class: 1
    #   |--- ret_1_H4 >  -0.00 → ret_1_H4 <= 0.00 → class: 1
    #                          → ret_1_H4 >  0.00 → class: 1
    # Its CV match is within 0.0005 of the Always-Buy baseline (0.8071, rank 2).
    # No miner produced a candidate that recovers the 38/197 Sell trades from
    # any feature; ranks 4-10 are all "Buy unless the prior return is extremely
    # negative" — i.e. the long bias re-encoded through different lookbacks.
    # Buy-rate by hour (12=86%, 16=84%, 20=80%, 04=71%, 00=62%) never reverses
    # sign, so even the weakest hours stay net-Buy.
    BUY if hour_utc in {12, 16, 20} and pair == "EURGBP"
    NONE otherwise
    # The rank-3 univariate (hour_utc > 4 ⇒ Buy, p_corr=7.9e-11, coverage=0.85)
    # is consistent with this gate but its match_rate_std=0 is suspect on a
    # heavily skewed dependent variable; the explicit 3-bucket gate above
    # mirrors the empirical top hours (16:00 28.9%, 20:00 25.9%, 12:00 25.4%
    # — 158/197 = 80% coverage) and is more conservative.
  exit:
    max_holding_hours: 120
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_0.85
citations:
  - "[evidence_based_ta, p.23-28] — \"Position bias x market trend creates apparent predictive power in useless rules. A long-biased rule in a bull market produces profit without any skill.\" Direct fit: 80.7% Buy on a single pair (EURGBP) over 2024-03→2026-04, with the tree's CV match indistinguishable from Always-Buy."
  - "[advances_fin_ml, p.84-89] — \"Meta-labeling — secondary binary classifier placed on top of a primary side-prediction model; learns when the primary model is correct and scales bet size accordingly.\" When the primary direction is dominated by a single class (Always-Buy=0.8071 ≈ tree=0.8076), no direction model adds information; meaningful structure could only live in entry timing or sizing — neither candidate miner surfaced such structure here."
  - "[evidence_based_ta, p.291] — Small-sample data-mining bias is dramatic at low n: best-of-1024 rules with 10 obs → ~84%/yr inflation; 1000 obs → ~12%/yr. n=197 over 2y on a single pair, with the univariate miner running 516 tests, places this firmly in small-sample territory. Treat any standalone univariate edge as suspect even after Bonferroni correction."
  - "[algo_trading_chan, p.114, ch.5] — \"Excess Return with Rollover Interest\". For an 80%-Buy EURGBP system with hold p50≈5d / p95≈40d, swap/rollover dominates a non-trivial slice of multi-week PnL; replicator must net carry before claiming any directional edge."
risk_flags:
  - "tree_degenerate: depth-4 DecisionTree converges every leaf to class=1; CV match (0.8076) within 0.0005 of Always-Buy baseline (0.8071) — the rank-1 candidate carries no direction signal beyond the unconditional class prior."
  - "directional_bias_eurgbp_brexit_regime: 80.7% Buy on a single pair over 2024-03→2026-04 sits inside the post-Brexit GBP-weakness regime. Vendor name 'Happy Brexit FM' implies a thesis-driven directional script tied to GBP weakness, not a learned signal; out-of-regime persistence unknown."
  - "hold_swing_not_intraday: hold p50/p95/max = 115.26h / 972.58h / 1642.79h (~5 / ~40 / ~68 days). Every hour-anchored intraday family in the closed enum is disqualified; replicator must support multi-day positions and FX overnight swap costs."
  - "small_sample_single_pair: n=197 trades on EURGBP only; with 80.7% Buy prior, ~38 informative Sell trades are far below any reliable rule-mining floor."
  - "vendor_marketing_bias: HappyForex catalog system on ForexMart (tier-2 retail broker, MT4, 1:500). account_type=Real but vendor selection bias is real (HappyForex publishes many EAs; survivor effect on this single track)."
  - "scheduled_entry_clock_anchor_unexplained: 12/16/20 UTC top-of-hour buckets (~25-29% each) on a multi-day-hold script suggest a scheduled-trigger MT4 EA on an hourly cron, not a market-condition entry. Calendar-aware replication (e.g. macro release windows) is plausible but cannot be confirmed from trade/OHLC evidence alone — flagged as Open Question, not assumed in the rule."
---

# Decoded signal — Happy Brexit FM (HR) (id 11155858)

## Family rationale

The closed taxonomy in `shared/decoder_taxonomy.Family` has no member that
simultaneously accommodates **(a)** clock-anchored entries at 12/16/20 UTC,
**(b)** hold p50 = 115h (~5 days), and **(c)** a degenerate direction model
where the depth-4 tree collapses to always-class-1 with CV match within
0.0005 of the Always-Buy baseline. Each candidate family fails on at least
one axis:

- **All intraday families** (`LATE_NY_BREAKOUT`, `LONDON_OPEN_MOMENTUM`,
  `LONDON_OPEN_MR`, `NY_SESSION_REVERSAL`, `OVERLAP_NY_LONDON_RANGE`,
  `FACTOR_SCALPING`) are disqualified by the hold distribution. Fingerprint
  (post-R4) reports p50 / p95 / max = 115.26h / 972.58h / 1642.79h, against
  decoder.md's intraday sanity floor: *"hold p50 > 24h confirmado pós-R4
  → use UNCATEGORIZED + reason_code=hold_mismatch ou SWING_TREND_MOMENTUM
  provisional se aplicável."*
- **`SWING_TREND_MOMENTUM`** (provisional, D6) requires "top hour <15%".
  This system's top hour is 16:00 with 57/197 = 28.9%, almost double the
  cap; three buckets (12/16/20) each carry ≥25%. The clock anchor is too
  strong for a swing-trend label whose essence is timing-agnostic H4/D1
  trend following.
- **`OVERNIGHT_GAP_FADE`** would need a Friday-late / Monday-early peak;
  observed peaks are mid-session and hold runs days, not the gap-fade
  window.
- **`NEWS_RELEASE_MOMENTUM`** (provisional, D5) requires (i) a name flag
  containing NEWS/HF News (this is "Happy Brexit", no NEWS flag), (ii) a
  bucket >30% (top bucket here is 28.9%, just under), and crucially
  (iii) an instantaneous hold (the reference system 1612420 has p50=0.01h
  ≈ 36s). Hold p50=115h is ~10⁷× larger.
- **`H1_MOMENTUM_GOLD`** trivially fails (pair = EURGBP, not Gold/XAU).
- **`MARTINGALE_GRID`** is rejected by Stage 1 sanity (k1_pass=PASS, lot
  p95/p50=1.03, max_streak=0).

What remains is a system that *looks* algorithmic on the entry side
(top-of-hour clock anchor on three specific buckets, single pair, single
broker, MT4 EA, fixed ~0.85 lot) but whose direction model degenerates to
"BUY EURGBP". The rank-1 tree returns class=1 on every branch, including
both `ret_1_H4 ≤ -0.00` and `ret_1_H4 > 0.00` sub-branches; CV mean is
0.8076 with std 0.162 and one fold at 0.564, indicating the classifier
is essentially memorising the prior. This is the textbook `degenerate`
reason_code in `shared/decoder_taxonomy.UncatReason`: *"tree/ripper
colapsa para always-Buy/Sell baseline (CV ≈ baseline)."*

`UNCATEGORIZED + reason_code=degenerate` is therefore the honest output.
`taxonomy_gap` was considered but rejected: the issue is not a coherent
novel family the enum is missing — it is that the candidate miners could
not lift the direction signal off the unconditional prior. Proposing a
new family for "always-Buy EURGBP with hourly trigger" would inflate the
taxonomy with an empirically vacuous label.

`hold_mismatch` is also defensible as a secondary reason (clock-anchored
entry at hour buckets vs multi-day hold) but `degenerate` is preferred
because it is the most falsifiable mathematical statement (tree CV ≈
baseline within 0.0005 is a single check); `hold_mismatch` is a softer
sanity argument.

## Rule derivation

The rule below is provided so the Stage 3 replicator has something
executable, but it is **the most defensible thin rule given the absence
of direction signal**, not a refined hypothesis:

- **Direction**: forced `BUY` because the rank-1 tree (CV 0.8076) and
  the baseline Always-Buy (CV 0.8071) are statistically indistinguishable
  on this sample. Using the tree's nominal split on `ret_1_H4` would be
  superstition — every leaf returns class=1. Sells (38/197 = 19.3%) have
  no candidate-rule signature in the top 10 — none of the univariate
  rules predicts Sell, the tree never emits class=0. The replicator
  should treat sells as **unmodelled noise** rather than try to fit them.
- **Entry window / hour gate**: `{12, 16, 20}` UTC, taken directly from
  the empirical top-3 buckets (158/197 = 80% coverage). The rank-3
  univariate `hour_utc > 4 ⇒ Buy` (CV 0.756, coverage 0.85,
  p_corr=7.9e-11) is consistent but its `match_rate_std=0` is a known
  instability mode of univariate splits when the dependent variable is
  heavily skewed — preferring the explicit 3-bucket gate is more
  conservative.
- **Pair**: `EURGBP` only. Fingerprint shows 197/197 trades on EURGBP —
  there is no multi-pair universe to refine against.
- **Exit**: `max_holding_hours = 120` ≈ p50 (115.26h). No price-based
  exit is observable (`exit_kind = manual_or_time` 197/197). TP/SL=null
  reflects this; replicator must use time-based exit. Note that p95=972h
  means a 120h cap will close ~50% of trades earlier than the system did
  — this is a deliberately conservative cap to bound swap accumulation
  during replication; sensitivity to {120, 240, 480, 960}h should be a
  Stage 3 sweep.
- **Sizing**: `fixed_lot_0.85` directly from lot p50=0.85, p95=0.88
  (variance ~3%); martingale flag PASS, no escalation.
- **Thresholds**: deliberately none. Every univariate threshold in
  candidates.json (e.g. `ret_10_M1 > -0.0003101`) is a near-zero cutoff
  that simply excludes the worst ~20% of bars; using them would be
  curve-fitting noise around the long bias `[evidence_based_ta, p.281,
  p.345]` (rule that single-rule back-test p-values cannot evaluate the
  best rule from a data-mining run — only WRC/MCP can).

## Confidence breakdown

- Family identification: 0.40 — UNCATEGORIZED is structurally correct
  (no enum member fits) but the choice between `degenerate`,
  `mixed_strategy` (3 hour peaks each ≥25%) and `hold_mismatch`
  (hour-anchored entry on multi-day hold) is non-unique. `degenerate`
  is preferred because it is the most falsifiable mathematical
  statement; the other two are softer sanity arguments.
- Direction rule: 0.20 — forced BUY is the only defensible direction
  given the candidate evidence, but a forced BUY rule has no
  information content beyond the directional prior of the dataset.
- Exit logic: 0.35 — `manual_or_time` covers 100% of trades but the
  p50/p95 spread (115h vs 972h) means any single max_holding_hours cap
  is a poor approximation of the underlying close-decision logic.
- Overall: **0.30** — capped low by the degenerate-direction finding,
  which dominates downstream replicator fidelity.

## Sanity-check verdict

**FAIL on intraday-family fit.** Any prior pass that classified this
system into an intraday family (e.g. `FACTOR_SCALPING` from a
pre-R4 NaN-hold pass) is rejected: the post-R4 fingerprint shows
p50=115h, well outside any intraday sanity floor. The hourly entry
distribution (3 peaks across 12-20 UTC) is *consistent* with
intraday-window entries, but the exits are clearly multi-day to
multi-week. The system is best described as **swing/position long-biased
on EURGBP with semi-randomised intraday entry timing** — for which the
closed enum has no slot. UNCATEGORIZED + degenerate is the honest call;
do not promote to any intraday family even though the entry-timing
alone could superficially fit.

## Open questions (for Stage 3 + posteriores)

- **Calendar-event hypothesis (do not assume in rule).** Top hours
  12/16/20 UTC line up loosely with US data-release windows (12:30
  NFP/CPI/Retail, 14:00 FOMC, 18:00 FOMC minutes; 20:00 occasionally
  BoE/ECB minutes). Per the project's instruction to classify only from
  observed trade/OHLC evidence, no news-aware family is asserted. Stage
  3 / future R could test whether a calendar-filtered replicator (gate
  entries to within ±15min of medium- or high-impact macro releases)
  raises lift over the always-Buy baseline. **Until evidence emerges,
  treat the clock anchor as a scheduled MT4 EA cron, not as a
  news-reading system.**
- **Naive-baseline comparison.** Compare the vendor track equity vs a
  naive "always long EURGBP, fixed 0.85 lot, no stop, weekly close"
  — if the naive variant matches within ±10% CAGR over 2024-03→2026-04,
  the system has zero alpha and should be flagged
  `degenerate-baseline-clone`.
- **Tree degeneracy at deeper depth.** Stage 1 used max_depth=4. At
  max_depth=8 with `class_weight='balanced'`, does any non-trivial
  split emerge on the 38 sell trades? If depth-8 also collapses to
  class=1, that confirms the `degenerate` reason_code is structural,
  not a hyperparameter artefact.
- **Hold cap sensitivity.** With p50=115h and p95=972h, the replicator
  result is sensitive to `max_holding_hours`. Sweep {120, 240, 480,
  960, no_cap} and report match-rate against MyFxBook trades; a cap
  that significantly over-performs the system suggests the system
  itself is inefficient on the long tail.
- **Carry/swap netting.** EURGBP long carries a small but
  regime-dependent overnight swap; for a 25-month track with p95=40d
  holds, rollover PnL must be netted before claiming any directional
  edge `[algo_trading_chan, p.114, ch.5]`.
- **Sell-recall expectation.** The 38 Sell trades may correspond to
  vendor-side discretionary overrides (news, weekly close hedging) that
  no feature in `decoder/features.parquet` can reconstruct; Stage 3
  should report Sell-recall and accept low recall as expected.
- **Provisional family reconsideration after R1.** If the broader R1
  re-decode surfaces ≥1 other system with the signature
  *clock-anchored entry hours + multi-day hold + degenerate direction
  tree*, propose a new candidate family
  (`SCHEDULED_DIRECTIONAL_HOLD` or similar) for review. Until then,
  UNCATEGORIZED + degenerate is the contract-correct output.
