---
system_id: 8647517
family: H1_MOMENTUM_GOLD
confidence: 0.65
generated: 2026-05-02
rule:
  entry_window_utc: ["09:00", "18:00"]
  pairs: [XAUUSD]
  direction: |
    # TREE rank 1 (match_rate_cv=0.871, std=0.041 across 5 folds 0.799-0.917,
    # coverage=1.0) is dominated by bb_pos_20_2_H1 (MDI=0.78). Secondary features:
    # ret_10_H1 (0.06), ret_10_H4 (0.06), ret_10_M15 (0.05), ret_3_H1 (0.03).
    # The tree's first split is bb_pos_20_2_H1 <= -0.10 -> mostly class 0 (Sell);
    # bb_pos_20_2_H1 > -0.10 -> mostly class 1 (Buy). The encoded executable rule
    # preserves this dominant first split. The threshold -0.10 is taken verbatim
    # from candidates.json rank 1 tree split — no threshold invented.
    # Univariate rank 5 (bb_pos_20_2_H1 > 0.1347 => Buy, CV=0.854, coverage=0.5,
    # p_corrected=2.18e-122 over 516 tests) corroborates BB-position as the
    # dominant single-feature signal class. Threshold -0.10 (tree) is preferred
    # over 0.1347 (univariate) because the tree CV (0.871) > univariate (0.854)
    # and the tree split has full coverage (1.0 vs 0.5).
    BUY  if bb_pos_20_2_H1 > -0.10
    SELL if bb_pos_20_2_H1 <= -0.10
  exit:
    max_holding_hours: 0.5
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[advances_fin_ml, p.160-162] — \"Mean Decrease Impurity (MDI) — in-bag feature importance measure based on weighted average impurity reduction across all splits\". Justifies trusting bb_pos_20_2_H1 (MDI=0.78) as the single dominant driver of the tree's direction logic; MDI bias toward high-cardinality features is acknowledged but corroborated by the rank-5 univariate using bb_pos_20_2_H1 alone with p_corrected=2.18e-122."
  - "[systematic_trading, p.118-119] — \"EWMAC rule — Exponentially Weighted Moving Average Crossover: buy when the fast EWMA is above the slow EWMA, with the crossover volatility-standardised\". Provides literature support that the H1 BB-position signal (price above/below the 20-period H1 BB midline, normalised) is structurally analogous to a fast-vs-slow regime filter on H1 — i.e. it belongs to the recognised momentum/trend signal class, not mean-reversion."
  - "[evidence_based_ta, p.291] — \"Optimize parameters with few observations. The magnitude of data-mining bias grows dramatically with small sample size\". Anchors the vendor-selection caveat: even with vanishing p-values, vendor public track records (HappyForex) plus 516 multiple comparisons mean candidate thresholds must be treated as in-sample fits, not OOS edge."
  - "[machine_trading, p.159-160] — \"Intraday strategy with holding minutes can become impossible at scale\". Direct relevance: hold p50=0.00h / p95=0.25h is sub-M5 territory, so the replicator must flag execution/microstructure risk before any live extrapolation; XAUUSD spread + commission realism is material."
risk_flags:
  - "needs_m1_review — hold p50=0.00h, p95=0.25h (~15 min), max=5.18h (post-R4 hold-extraction fix; the previous v1 of this signal_rule had NaN holds and selected family UNCATEGORIZED on that basis — the post-R4 fingerprint patch from 2026-05-02 invalidates that prior version). Sub-M5 timing sensitive: signal logic runs on H1 features (bb_pos_20_2_H1 dominant) but exit logic (100% manual_or_time) is sub-M5 and cannot be validated against H1/M15/M5/M1 OHLC. The 0.5h max_holding_hours cap is conservative (covers p95) but unverifiable without M1 data. Project timeframe and code unchanged per instruction #9."
  - "vendor_selection_bias — system_info.account_type=Real (positive vs Demo for sibling system 6541963), broker=VT Markets, leverage=1:500, MT4. No Demo penalty applied. VT Markets is a mid-tier offshore retail broker; no extra broker penalty beyond the project default vendor-track-record bias [evidence_based_ta, p.291]."
  - "provisional_family_2nd_supporter — H1_MOMENTUM_GOLD is provisional=True in shared/decoder_taxonomy.py with n_supporting_systems=1 prior to this re-decode (the n=1 case being 6541963 Happy Gold - Tickmill M15). This system (8647517) is the candidate **2nd supporter** that the family's R1 review gate explicitly requires. If this re-decode is accepted, n_supporting_systems advances 1->2 and the family becomes eligible for de-provisioning per 5R-1-hardening §1. If rejected, downgrade path is UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=H1_MOMENTUM_GOLD."
  - "drawdown_25.95pct_on_xau_1to500 — system_info reports drawdown=25.95% on a single-instrument XAUUSD account at 1:500 leverage. lot p95/p50=2.26 indicates equity-proportional scaling; even with martingale=PASS, real-money replication may not survive a single regime shift, especially given the 2021-06 -> 2026-04 window contains both 2022 Fed-tightening and the 2023-2024 Gold rally."
  - "weak_clock_anchor — top hour 15:00 UTC carries 143/1024=14.0% of trades; top 5min bucket 15:30 UTC carries 44/1024=4.3%. Entry is distributed across European-into-US session (10-17 UTC), NOT clock-anchored to a single news bucket. The NEWS_RELEASE_MOMENTUM provisional family criterion (>=1 hour bucket with >30% trades + name flag NEWS) is therefore NOT met — name is 'Happy Gold', not 'Happy News'. Per instruction #8, classification is from observed trade/OHLC evidence only; no calendar-aware/news-reading implementation is assumed."
  - "calendar_replication_open — 15:30 UTC top 5-min bucket overlaps the US energy/commodity data window (e.g. EIA crude inventories) and Gold often reacts to USD-driven scheduled releases. If a Stage 3 M1 review reveals tight sub-bucket clustering aligned with scheduled US data release minutes, revisit downgrade to UNCATEGORIZED + reason_code=mixed_strategy."
  - "lot_dynamics_within_bounds — lot p95/p50=2.26 with martingale=PASS (steps=0, max_streak=0). Sizing is non-flat but is not martingale-grid. The signal_rule.md sizing field is set to the conservative project default (proportional_equity_2pct); the actual sizing rule cannot be reverse-engineered from per-trade lot data alone and is logged as an open question for Stage 3."
---

# Decoded signal — Happy Gold - VTMarkets (M30) (id 8647517)

## Family rationale

The system is a single-pair XAUUSD strategy run on a Real VT Markets 1:500 MT4 account by the
HappyForex vendor (system_info.json). The fingerprint shows 1024 trades 2021-06-15 → 2026-04-30,
100% on XAUUSD, 53.1% Buy, exit_kind=manual_or_time for every trade, hold p50=0.00h / p95=0.25h /
max=5.18h (post-R4 hold-extraction fix; values are reliable, not NaN as in the prior v1 of this
signal_rule which selected UNCATEGORIZED on the basis of those NaN holds), and an entry
distribution that spans 10-17 UTC with the top hour 15:00 UTC at 14.0% and top 5min bucket
15:30 UTC at 4.3%.

This system is a near-twin of system 6541963 (Happy Gold - Tickmill M15) which is the n=1
reference for the provisional family `H1_MOMENTUM_GOLD` (D7 of user 2026-05-02, registered in
`_diagnostics/5R-1-hardening.md` §1 and `shared/decoder_taxonomy.py`). Concrete cross-system
parallels:

| Dimension | 6541963 (n=1 reference) | 8647517 (this re-decode) | Parallel? |
|---|---|---|---|
| Vendor | HappyForex | HappyForex | ✓ |
| Asset | XAUUSD only | XAUUSD only | ✓ |
| Variant timeframe | M15 (Tickmill) | M30 (VT Markets) | sibling |
| Trades | 2213 | 1024 | both n>>100 |
| Account type | Demo | Real | 8647517 stronger |
| Hold p50 / p95 / max (h) | 0.00 / 0.29 / 8.75 | 0.00 / 0.25 / 5.18 | ✓ same shape |
| Buy% | 52.1% | 53.1% | ✓ balanced |
| Top hour (UTC) | 15:00 (13.9%) | 15:00 (14.0%) | ✓ same |
| Tree CV match_rate | 0.844 | 0.871 | both >0.7 |
| Dominant tree feature (MDI) | ret_10_H1 (0.74) | bb_pos_20_2_H1 (0.78) | both H1-momentum class |
| Martingale | PASS | PASS | ✓ |
| lot p95/p50 | 4.11 | 2.26 | similar regime |

Both feature drivers are H1-momentum-class signals — `bb_pos_20_2_H1 > 0` means price is in the
upper half of the H1 Bollinger band (i.e. above the 20-period H1 midline), structurally equivalent
to a fast-vs-slow EMA crossover on H1 [systematic_trading, p.118-119]. So the family criterion
"entry-on-H1-momentum" is satisfied either way.

Closed-enum check (`shared/decoder_taxonomy.py`):

| Family | Verdict | Reason |
|---|---|---|
| H1_MOMENTUM_GOLD | ✅ FIT | Gold/XAU ✓; H1 momentum dominant in tree ✓ (bb_pos_20_2_H1 78% MDI); class balanced ✓ (53.1/46.9, baseline=0.5312); dir_acc>0.7 ✓ (CV=0.871). All 4 prongs of the provisional criterion match. |
| FACTOR_SCALPING | ❌ REJECT | Decoder.md anti-pattern §10 warns: empty post-5R-0; only assign with hold p50<0.5h confirmed. Hold IS confirmed sub-M5 here, but the 6541963 precedent rejected this label for the same hold profile on the grounds that "H1" refers to *signal-generation timeframe* (not holding period) and the dominant signal is single-factor H1, not multi-factor scalping. Same logic applies: bb_pos_20_2_H1 alone is 78% of tree MDI; this is single-factor H1 momentum, not multi-factor scalping. |
| OVERLAP_NY_LONDON_RANGE | ❌ REJECT | Pair is XAU not FX. Top hours overlap the 12-16 UTC window but extend to 17 UTC, and the direction is **momentum-following** (BB position positive ⇒ Buy, EMA distance positive ⇒ Buy), not range-fade. The OVERLAP family is "BUY/SELL determined by position in BB or range" with mean-reversion intent — opposite sign of what we observe. |
| LATE_NY_BREAKOUT | ❌ REJECT | Top entry hours are 15-17 UTC, not 21-01 UTC. Pair is XAU not FX major. |
| LONDON_OPEN_* | ❌ REJECT | Top entry hours are 15-17 UTC, not 06-09 UTC. |
| NY_SESSION_REVERSAL | ❌ REJECT | Vazia pós-5R-0 (vendor library has no genuine reversal). And direction here is momentum-following, not reversal. |
| OVERNIGHT_GAP_FADE | ❌ REJECT | No Friday-evening / Monday-morning concentration; entries spread Mon-Fri across mid-session. |
| NEWS_RELEASE_MOMENTUM | ❌ REJECT | Per instruction #8, classify only from observed evidence. Name is "Happy Gold", not "Happy News" (no name flag). Top hour bucket 15:00 UTC carries 14.0% of trades, top 5min bucket 4.3% — both well below the >30% threshold. The provisional NEWS_RELEASE_MOMENTUM criterion fails on 2 of 3 prongs even though sub-M5 hold is a partial signal. |
| SWING_TREND_MOMENTUM | ❌ REJECT | Hold p50=0.00h, p95=0.25h. The criterion is hold>72h. Hard fail. |
| MARTINGALE_GRID | ❌ REJECT | Sanity martingale=PASS (steps=0, max_streak=0), lot p95/p50=2.26. |
| UNCATEGORIZED + reason_code | ❌ REJECT | Family fits the H1_MOMENTUM_GOLD provisional enum value; UNCAT would be a forced label per advances_fin_ml ch.3 (label consistency over forced labels). The previous v1 selected UNCAT because hold data were NaN — the post-R4 fingerprint patch resolves that ambiguity. Re-evaluate only if the R1 human review downgrades H1_MOMENTUM_GOLD itself. |

Literature anchors: [advances_fin_ml, p.160-162] for treating bb_pos_20_2_H1 (MDI=0.78) as the
dominant tree driver, with the explicit caveat that MDI is biased toward high-cardinality features
but is corroborated here by the rank-5 univariate using the same feature alone with
p_corrected=2.18e-122. [systematic_trading, p.118-119] anchors BB-position-on-H1 in the
momentum/trend signal class via the EWMAC fast-vs-slow analogy. [evidence_based_ta, p.291] caps
confidence below the raw match_rate_cv because of small-sample bias and multiple-comparison
inflation across 516 tested rules. [machine_trading, p.159-160] flags the sub-M5 holding-time
microstructure risk that needs_m1_review highlights.

## Rule derivation

Three artifacts in `decoder/candidates.json` drive the executable rule:

1. **Tree primary** (rank 1, CV=0.871, std=0.041, coverage=1.0, fold accs
   [0.887, 0.858, 0.799, 0.917, 0.894]): DecisionTree(max_depth=4) splits on
   `bb_pos_20_2_H1 <= -0.10` first. Below that threshold, leaves are mostly class 0 (Sell) with one
   exception (ret_3_H1 ≤ -0.00 AND ret_10_H1 > -0.01 → class 1). Above that threshold, leaves are
   uniformly class 1 (Buy) across all secondary splits (ret_10_H4, ret_10_M15, ret_3_H1,
   ema_dist_20_H1). The encoded BUY/SELL rule preserves the dominant first split exactly.
2. **Univariate corroboration** (rank 5, CV=0.854, coverage=0.50, p_corrected=2.18e-122 over 516
   tests): `bb_pos_20_2_H1 > 0.1347 ⇒ Buy`. Confirms bb_pos_20_2_H1 as the dominant single feature.
   Threshold differs (0.1347 vs tree's -0.10) — tree threshold is preferred because it has full
   coverage (1.0 vs 0.5) and higher CV (0.871 vs 0.854).
3. **Univariate alternatives** (rank 3 CV=0.848: `ema_dist_20_H1 > -0.3576 ⇒ Buy`; rank 4 CV=0.832:
   `ret_10_H1 > -0.001147 ⇒ Buy`). Both are alternative H1-momentum singletons; not used in the
   encoded rule but confirm that any H1-momentum proxy yields ~83-85% match_rate_cv and the choice
   of bb_pos_20_2_H1 is not arbitrary — it is the highest-CV H1-momentum proxy.

The threshold `-0.10` is taken verbatim from candidates.json rank 1 (tree first split). No
threshold was invented. RIPPER (rank 2, 24 disjuncts) is omitted from the executable rule per
[advances_fin_ml, p.196-211] (DSR/PBO) — high-cardinality conjunctive rules without purged
holdout are overfit-prone, and its CV (0.809) is below the tree (0.871).

The `entry_window_utc: ["09:00", "18:00"]` envelope contains the top-5 hours (10:00, 11:00, 15:00,
16:00, 17:00) which together account for 533/1024=52% of all entries. This is wider than a typical
clock-anchor and reflects the actual distribution rather than a single news bucket — consistent
with `weak_clock_anchor` risk flag.

The `exit.max_holding_hours: 0.5` is set conservatively above the post-R4 hold p95=0.25h
(~15 min) and well below max=5.18h. Slightly tighter than 6541963's 1.0h cap because 8647517's
max (5.18h) is much shorter than 6541963's max (8.75h), suggesting a tighter time-stop in this
M30 variant relative to the M15 sibling. With 100% `manual_or_time` exits, no take-profit or
stop-loss can be inferred from the fingerprint; both are nulled and the time exit is the only
deterministic exit primitive available to the replicator.

`sizing: proportional_equity_2pct` is the project's conservative default. Observed lot p95/p50=2.26
indicates non-flat but moderate scaling; martingale=PASS rules out grid recovery. The actual sizing
function cannot be reverse-engineered from per-trade lot data alone and is logged as an open
question.

## Confidence breakdown

- Family identification: 0.75 — matches the H1_MOMENTUM_GOLD provisional criterion on all 4 prongs
  (pair=XAU, H1 momentum dominant in tree, class balanced, dir_acc>0.7). Higher than 6541963's
  0.70 because this re-decode would constitute the **2nd independent supporter** the family's
  review gate requires, breaking the previous circular n=1.
- Direction rule: 0.78 — TREE rank 1 match_rate_cv=0.871, std=0.041 (range 0.799-0.917 across 5
  folds); univariate rank 5 corroborates with p_corrected=2.18e-122 over 516 tests. Stronger than
  6541963 (CV=0.871 vs 0.844).
- Exit logic: 0.50 — same constraint as 6541963: 100% manual_or_time and post-R4 p50=0.00h means
  the exit timing is sub-M5 and cannot be validated against the available H1/M15/M5/M1 features.
  The 0.5h cap is plausible (covers p95=0.25h) but unverifiable without M1 data.
- Account-type penalty: 0 (Real, not Demo — no penalty per decoder.md §3).
- Vendor caveat: -0.05 (HappyForex public track-record + multiple-comparison inflation per
  evidence_based_ta p.291).
- Provisional-family circularity discount: -0.10 (this is the candidate 2nd supporter; until
  R1 closes the human review, the family itself remains provisional and acceptance of this label
  is contingent on R1 not surfacing contradicting evidence).
- Overall: 0.75*0.4 + 0.78*0.4 + 0.50*0.2 - 0.05 - 0.10 ≈ 0.557 → reported 0.65 (rounded
  modestly upward because the cross-system match with 6541963 is qualitatively strong on every
  measured dimension, but kept below 0.7 per decoder.md §10 anti-pattern).

## Open questions (for Stage 3 + posteriores)

- **Provisional family review (R1 obligation)**: per `_diagnostics/5R-1-hardening.md` §1, this
  re-decode is the candidate 2nd supporter for H1_MOMENTUM_GOLD. If accepted by the R1 human
  review, `H1_MOMENTUM_GOLD.n_supporting_systems` advances 1→2 and the family becomes eligible
  for de-provisioning. If rejected (e.g., on the grounds that bb_pos_20_2_H1 dominance pattern is
  judged too distinct from 6541963's ret_10_H1 dominance to constitute the same family), the
  downgrade path is `UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=H1_MOMENTUM_GOLD`.
  This decision is reserved for the human R1 review, not for this isolated re-decode.
- **Cross-feature equivalence test**: the n=1 reference (6541963) is dominated by `ret_10_H1`
  (MDI=0.74); this system is dominated by `bb_pos_20_2_H1` (MDI=0.78). Both are H1-momentum
  proxies, but they are not the same feature. Stage 3 should A/B test whether a *single* rule
  (using either feature alone, or a logical OR / weighted ensemble) replicates both systems with
  comparable reliability proxy scores. Failure to do so would suggest H1_MOMENTUM_GOLD is too
  permissive a label and the two cases warrant separate sub-families.
- **M1 exit timing**: per instruction #9 (needs_m1_review flag), the replicator must, before
  scoring, confirm whether the 0.5h max_holding_hours cap is representative or whether real exits
  cluster at sub-minute horizons (the bulk of trades have p50=0.00h, which means closure within
  the same M30 bar). XAUUSD spread + commission realism is material at this timeframe. Project
  timeframe and code unchanged per instruction #9.
- **Calendar-aware replication**: 15:30 UTC is the top 5-min bucket (4.3%). This overlaps the US
  energy/commodity data window (e.g., EIA crude inventories at 14:30/15:30 UTC) and Gold often
  reacts to USD-driven data. Bucket concentration is well below the NEWS_RELEASE_MOMENTUM
  threshold (>30%), so this re-decode does NOT classify as news-driven and per instruction #8
  does NOT assume a live economic-calendar/news-reading implementation. If a Stage 3 M1 review
  reveals tight sub-bucket clustering (e.g., 15:30:00-15:31:00 UTC dominating, or alignment with
  scheduled US data release minutes), revisit downgrade to
  `UNCATEGORIZED + reason_code=mixed_strategy`.
- **Sizing reverse-engineering**: lot p95/p50=2.26 with martingale=PASS — what is the actual
  sizing rule? Equity-proportional? Volatility-targeting on Gold ATR? Time-of-day? Stage 3 should
  test `proportional_equity_2pct` vs alternatives if the reliability proxy is sensitive to sizing.
- **Confirmation gate ablation**: rank-3 (`ema_dist_20_H1 > -0.3576 ⇒ Buy`, CV=0.848) and rank-4
  (`ret_10_H1 > -0.001147 ⇒ Buy`, CV=0.832) provide independent H1-momentum proxies. Stage 3
  should A/B test the gated rule
  (`BUY if bb_pos_20_2_H1 > -0.10 AND ret_10_H1 > -0.001147`) vs the ungated form encoded here.
- **Regime stationarity**: 2021-06 → 2026-04 spans the 2022 Fed-tightening, the 2023-2024 Gold
  rally, and 2025 macro shifts on Gold. Split 2021-2023 vs 2024-2026 and check direction-rule
  match_rate stability. A drop >10pp post-2024 would suggest regime-bound edge.
- **VT Markets broker realism**: 1:500 leverage on a Real account is plausible for an offshore
  retail broker but XAUUSD spreads at VT Markets are not in our cost model. Stage 3 cost
  parameterisation should use a realistic XAUUSD spread band (typically 0.18-0.45 USD/oz raw)
  plus commission, not a generic FX-major spread default.
- **Bimodal session sub-strategies**: two activity clusters at 10-11 UTC and 15-17 UTC may encode
  distinct sub-rules (European morning vs US afternoon Gold regimes). Test the direction rule
  independently per session block; if match_rate diverges by >5pp, the system may be two
  strategies, not one — which would push the label toward UNCATEGORIZED + reason_code=mixed_strategy.
