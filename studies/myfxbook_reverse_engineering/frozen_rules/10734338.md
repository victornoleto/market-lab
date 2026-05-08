---
system_id: 10734338
family: UNCATEGORIZED
confidence: 0.50
reason_code: taxonomy_gap
candidate_new_family: CRYPTO_INTRADAY_MOMENTUM
generated: 2026-05-02
rule:
  entry_window_utc: ["15:00", "18:00"]
  pairs: [BTCUSD]
  direction: |
    # Tree rank 1 (CV match 0.860, std 0.023, coverage 1.0).
    # Primary split: bb_pos_20_2_H1 = -0.29 (price relative to H1 Bollinger 20,2 lower band).
    # Secondary splits at ema_dist_20_H1 = 0.55 / 1.12 collapse all upper-branch leaves to class=1 (Buy),
    # so they do not change the realized prediction — keep only the primary split for the executable rule.
    BUY  if bb_pos_20_2_H1 > -0.29
    SELL if bb_pos_20_2_H1 <= -0.29
  exit:
    max_holding_hours: 2
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[advances_fin_ml, p.160-162] — \"Mean Decrease Impurity (MDI) … fast but biased toward high-cardinality features … Mean Decrease Accuracy (MDA) … unbiased but slower\" — justifies trusting the depth-4 tree's importance pattern (bb_pos_20_2_H1 = 0.85 dominates) only because the same feature also wins on a univariate basis (rank 6: bb_pos_20_2_H1 > 0.1203 ⇒ Buy, CV 0.868) — i.e. it is not the high-cardinality MDI artifact AFML warns about."
  - "[algo_trading_chan, p.153-154, ch.6] — \"momentum strategies have limited downside (via natural stop loss) but unlimited upside\" — the BB-position split here is momentum-following (BUY in the upper part of the band, SELL only when price has broken deep below the lower band), so the family signature is intraday momentum-continuation rather than mean-reversion."
  - "[machine_trading, p.12 + p.202, ch.7] — \"~45% of [bitcoin] exchanges fail due to thefts/hacks — credit risk, not just market risk\" — infrastructure caveat any BTCUSD replication must carry forward."
risk_flags:
  - "needs_m1_review — hold p50 = 0.01h (~36s), p95 = 0.26h (~16min); the live execution timeframe is M1 or sub-M1, so an M5-anchored replicator will mis-time entries and exits relative to the live system. Project timeframe is unchanged for this run; flagged for future M1 review."
  - "demo_account — account_type=Demo on IC Markets, vendor selection bias possible (myfxbook ranking incentive); per decoder workflow step 3, family confidence reduced 0.10."
  - "single_asset_universe — BTCUSD only; edge cannot be cross-validated across pairs."
  - "data_window_short — 2024-01-26 → 2026-05-01 (~2.3 years), entirely post-2022 BTC regime; out-of-regime persistence unknown."
  - "calendar_aware_replication_unknown — top entry hours 15-18 UTC overlap US cash-equity open and the canonical US macro release slots. The fingerprint and OHLC features alone cannot decide whether the live system reads an economic-calendar feed. Replicator must NOT assume a calendar feed; if a calendar-aware variant scores meaningfully higher in Stage 3, that is a finding to flag, not a license to inject calendar data into this rule."
---

# Decoded signal — Happy Bitcoin - ICMarkets (id 10734338)

## Family rationale

The closed taxonomy enum (`shared/decoder_taxonomy.Family`) is FX/session-anchored: `LATE_NY_BREAKOUT`, `LONDON_OPEN_MOMENTUM`, `LONDON_OPEN_MR`, `NY_SESSION_REVERSAL`, `OVERLAP_NY_LONDON_RANGE`, `OVERNIGHT_GAP_FADE` all assume FX majors traded around bank-session opens; `H1_MOMENTUM_GOLD` is asset-locked to XAU; `SWING_TREND_MOMENTUM` requires hold > 72h; `NEWS_RELEASE_MOMENTUM` requires a clock-anchored bucket with > 30% of trades. This system is **BTCUSD only**, with hold p50 = 0.01h (post-R4 fix), top hour 17 UTC at 91/591 = 15.4% of trades, and no `NEWS` flag in the system name. None of those families fit without forcing the label.

`FACTOR_SCALPING` is the closest enum candidate by duration alone — durations < 30min are now confirmed post-R4 (p95 = 0.26h ≈ 15.6min, max = 2.04h). However, the family description in `decoder_taxonomy.py` is "Scalping multi-fator … edge tipicamente vol-targeting ou pair-trading intraday." The edge here is neither cross-sectional nor vol-targeting: it is a single-asset H1 Bollinger-position rule on one crypto pair, dominated by `bb_pos_20_2_H1` (0.85 importance in the depth-4 tree, also the strongest univariate at CV 0.868). Calling that `FACTOR_SCALPING` would re-introduce exactly the over-fit pattern the 5R-1-hardening §1 collapse warned about (`FACTOR_SCALPING` 6 → 0 supporting systems pre-Opus). I therefore classify `family: UNCATEGORIZED + reason_code: taxonomy_gap` and propose `candidate_new_family: CRYPTO_INTRADAY_MOMENTUM` for review per `_diagnostics/5R-1-hardening.md` §1 acceptance criteria.

The candidate-family signature, drawn only from this system's evidence (n=1; needs ≥1 more independent supporter + user approval to enter the enum even as `provisional=True`):

- Single-asset crypto pair (BTCUSD or similar 24/7 CFD).
- Hold p50 < 5 min, p95 < 30 min, max < 3 h (intraday scalp).
- No martingale (k1_pass=True; here lot p95/p50 = 1.38, max_streak = 0).
- Entry concentrated 15-18 UTC (US cash-equity open / NY afternoon), but top single hour ≤ ~25% of trades — distinct from `NEWS_RELEASE_MOMENTUM`'s > 30% bucket criterion.
- Direction primarily a single-feature H1 Bollinger-position rule with momentum-continuation sign (BUY above the lower band, SELL only on deep break below), CV match-rate ≥ 0.85 on a depth-4 decision tree.

`MARTINGALE_GRID` is explicitly ruled out by Stage 1 sanity: martingale flag PASS, steps = 0, max_streak = 0, lot p95/p50 = 1.38. None of the FX session families fit because the asset is BTCUSD and the system trades 24/7; the 15-18 UTC peak is descriptive, not a session-anchor in the FX sense.

## Rule derivation

**Entry window 15:00-18:00 UTC.** From `fingerprint.md` top entry hours: 17 (91 trades), 16 (86), 18 (44), 15 (42) account for 263 / 591 = 44.5% of all entries; the next biggest is 10 UTC (41 trades, 6.9%). I exclude 10 UTC and earlier hours from the executable window because the cluster mass is unambiguously in the NY afternoon block. This is descriptive of the observed timing distribution, not a claim of FX-session causality.

**Direction rule = primary tree split (rank 1).** From `candidates.json` rank 1: depth-4 decision tree, `match_rate_cv = 0.860`, `std = 0.023`, `coverage = 1.0`, fold accuracies in [0.822, 0.891]. The tree's effective decision is at the root: `bb_pos_20_2_H1 ≤ -0.29 → class 0 (Sell)` versus `bb_pos_20_2_H1 > -0.29 → class 1 (Buy)`. Every leaf under `bb_pos_20_2_H1 > -0.29` collapses to class = 1 regardless of the secondary `ema_dist_20_H1` and `ret_1_M15` splits, so the secondary splits add no executable predictive content — they only refine the model's internal probability estimate. Keeping only the primary split avoids over-specifying the rule. Cross-check: the strongest univariate rule (rank 6) is `bb_pos_20_2_H1 > 0.1203 ⇒ Buy` at CV 0.868 — same feature, slightly different threshold, consistent direction, with `p_value_corrected = 5.0e-77`. The RIPPER ruleset (rank 2, CV 0.837) brings in `ema_dist_20_H1`, `ema_dist_20_H4`, `close_vs_session_open_M5`, `ret_10_H1`, `prior_bar_sign_*`, but its CV is below the simpler tree, so I keep the tree.

**Threshold value −0.29 is taken verbatim from the tree, not invented.** This satisfies the anti-pattern rule "Inventar um threshold (ex.: `ema_dist_20_H1 > 0.5` quando candidates.json diz `> 0.18`)".

**Direction interpretation: BUY vs SELL (not BUY vs flat).** Fingerprint reports actions = {Buy: 317, Sell: 274}, i.e. 274 explicit short trades. The tree's class 0 must therefore mean SELL, not flat. So the rule is symmetric: long when `bb_pos_20_2_H1 > -0.29`, short when `≤ -0.29`. Given the deep-below-lower-band trigger for SELL, the SELL leg is best read as a "trend-continuation short on a confirmed H1 break" rather than a mean-reversion long-fade.

**Exit `max_holding_hours = 2`.** Post-R4 fingerprint: hold p50 = 0.01h, p95 = 0.26h, max = 2.04h, and `Exit kind distribution: manual_or_time = 591` (all). I round max up to 2h as a hard time-stop. Replicator should not synthesize TP/SL pips because the live system's `manual_or_time` exits are not pip-anchored in the available evidence, and the fingerprint contains no exit-by-pip features.

**Sizing `proportional_equity_2pct`.** No martingale (k1_pass=True), `lot p95/p50 = 1.38` consistent with proportional sizing on equity drift. I do not have direct equity-curve telemetry to confirm a 2% risk fraction, so this is a replicator-friendly default; the comparator stage should be sensitive to absolute lot mis-scaling and report it.

## Confidence breakdown

- Family identification: **0.40** — the pattern is internally coherent but lies outside the closed enum; assigning `UNCATEGORIZED + taxonomy_gap` is the honest call, and confidence reflects the un-replicated novel-family proposal (n=1).
- Direction rule: **0.65** — primary tree split at `bb_pos_20_2_H1 = -0.29` is the strongest single feature in two independent miners (tree importance 0.85, univariate rank-6 CV 0.868 with `p_value_corrected = 5.0e-77`); CV std 0.023 is tight. Capped below 0.7 because the buy/sell mix is near-balanced (53.6% / 46.4%), so any drift in the live BB threshold materially changes realized direction share.
- Exit logic: **0.45** — `manual_or_time` aggregates several real exit mechanisms; with hold p50 = 36s the live system is almost certainly tick- or M1-driven and the M5-anchored replicator will mis-time exits.
- Overall: **0.50** — weighted mean (0.40 × 0.4 + 0.65 × 0.4 + 0.45 × 0.2 = 0.51), then rounded down 0.01 for `account_type = Demo` selection bias per decoder workflow step 3.

## Open questions (for Stage 3 + posteriores)

- Does the live system read an economic-calendar feed? The 15-18 UTC cluster overlaps US cash-equity open and the canonical 14:30 / 15:30 / 17:00 UTC US macro-release slots. The fingerprint and OHLC features alone cannot decide this. Replicator must use only OHLC-derived features as in this rule and **not** assume a calendar feed; a calendar-aware comparison is a separate Stage-3 experiment.
- The simpler tree threshold `-0.29` is conservative (the BUY side covers ~51% of trades, matching the 53.6% buy share). Stage 3 should test a tighter threshold (e.g. univariate rank 6: `bb_pos_20_2_H1 > 0.1203`) to see whether the lower-coverage / higher-precision rule ports better out-of-sample.
- Hold p50 = 0.01h means the M5 replicator is operating two orders of magnitude above the live execution timeframe. Any large reliability gap is likely an execution-grain artifact, not a rule-shape error. The project timeframe stays unchanged for this run; flagged via `risk_flag: needs_m1_review` for a future M1-anchored replicator pass.
- BB threshold stability across regimes: the rule was trained on the 2024-2026 BTC regime; in 2022-style bear regimes BB positions are structurally lower and the `-0.29` threshold may need regime-adaptive shifting. Stage 3 should sweep `{-0.50, -0.29, 0.00, +0.12}` for sensitivity.
- Lot sizing: `lot p50 = 84408` with p95/p50 = 1.38 is closer to fixed-lot with minor proportional drift than to true equity-percentage sizing. Stage 3 should model both `fixed_lot` and `proportional_equity_2pct` and report which fits the live equity curve better.
- Family proposal `CRYPTO_INTRADAY_MOMENTUM`: needs ≥1 independent supporting system in R1 + explicit user approval before entering the enum even as `provisional=True`. If R1 produces no second supporter, this system stays `UNCATEGORIZED + taxonomy_gap` and the candidate label is simply archived in this file for future review.
