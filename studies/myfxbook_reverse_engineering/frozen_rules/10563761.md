---
system_id: 10563761
family: UNCATEGORIZED
confidence: 0.62
reason_code: taxonomy_gap
candidate_new_family: H1_MOMENTUM_BTC
generated: 2026-05-02
rule:
  entry_window_utc: ["15:00", "20:00"]
  pairs: [BTCUSD]
  direction: |
    # Tree (rank 1, CV 0.858, std 0.036, coverage 1.00) — bb_pos_20_2_H1 importance 0.89
    # dominates; all sub-leaves below the root resolve to the same class as the root,
    # so the rule reduces cleanly to a single-threshold momentum-continuation split.
    BUY  if bb_pos_20_2_H1 > 0.23
    SELL if bb_pos_20_2_H1 <= 0.23
  exit:
    max_holding_hours: 1.5
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[advances_fin_ml, p.160-167] — \"Use all three feature importance methods (MDI, MDA, SFI) and report only features ranked important by at least two methods\" — single-feature tree dominance (bb_pos_20_2_H1 = 0.89) is corroborated by univariate rank 6 (match_rate_cv 0.867, p_corrected 3.4e-56) on the same feature, so the H1 momentum signal is not a high-cardinality MDI artifact."
  - "[evidence_based_ta, p.264-265, p.271, p.287] — Multiple Comparison Procedure / data-mining bias: 518 univariate tests with corrected p-values 1e-50…1e-59 still survive Bonferroni-style correction, supporting that the rule exists in the trade record (a separate question from forward edge)."
  - "[machine_trading, p.204-205, ch.7] — Bollinger Band logic on price extremes (Chan describes BB mean-reversion: \"buy when price < MA − k·MSTD, sell when > MA + k·MSTD\"). This system inverts that sign (BUY at upper-band region) consistent with momentum-continuation, applied to BTCUSD."
  - "[machine_trading, p.202, ch.7] — \"~45% of [bitcoin] exchanges fail due to thefts/hacks — credit risk, not just market risk\" — relevant venue/credit risk for any BTCUSD CFD replication of the rule."
risk_flags:
  - "needs_m1_review — hold p50 = 0.00h, p95 = 0.18h (~10.8 min), max 1.23h: timing is sub-M5 sensitive. Replicator should re-derive entry/exit logic on M1 OHLC before publishing a reliability score. (Project timeframe is NOT being changed; this is a per-system replication note.)"
  - "calendar_aware_unverified — top 5min bucket includes 15:30 UTC (12/436 = 2.75%, tied for #1) which is the canonical 08:30 ET US data-release slot; the production EA may consult an economic calendar that this signal_rule does not encode. Per decoder protocol, classifying ONLY from observed trade/OHLC evidence — not assuming a live calendar/news-reading implementation."
  - "single_asset_universe — BTCUSD only (436/436); no cross-pair generalization is observable. Taxonomy enum has no crypto-anchored family; provisional H1_MOMENTUM_GOLD is asset-restricted to Gold/XAU."
  - "regime_breadth_limited — track record 2024-05-13 → 2026-01-29 (~21 months) covers a single BTC regime; edge persistence outside this window is unknown."
  - "vendor_selection_bias — HappyForex public catalogue with strong gain framing; broker DecodeFX is outside the audited Pepperstone/Inter set. Confidence capped accordingly."
---

# Decoded signal — Happy Bitcoin - DecodeFX (id 10563761)

## Family rationale

The system is a **single-pair BTCUSD intraday momentum-continuation rule on H1**. The Stage 1 candidate set is decisively dominated by one feature: the rank-1 decision tree (`match_rate_cv = 0.858`, std 0.036, coverage 1.00) puts 89% of split importance on `bb_pos_20_2_H1`, and three independent univariate rules (ranks 6, 7, 8: `bb_pos_20_2_H1 > 0.20`, `ema_dist_20_H1 > 0.33`, `ret_10_H1 > 0.002`, all `match_rate_cv ≥ 0.85`, `p_corrected < 1e-50`) describe the same H1-momentum-up → BUY structure. Per López de Prado [advances_fin_ml, p.160-167], a single-feature tree win is suspicious until corroborated by a second importance method; here univariate corroborates the H1 momentum direction independently, so the signal is not just an MDI high-cardinality artifact.

This pattern **does not fit any closed-enum family**:

- **FX-session families** (`LATE_NY_BREAKOUT`, `LONDON_OPEN_*`, `NY_SESSION_REVERSAL`, `OVERLAP_NY_LONDON_RANGE`): all require an FX-pair universe and FX-session anchoring. Asset is BTCUSD (crypto, 24/7); the entry-hour distribution (top-5 hours 15-19 UTC = 53.4% of trades) is broader and later than `OVERLAP_NY_LONDON_RANGE`'s 12-16 UTC anchor, and the direction logic is momentum-continuation, not session-range fade or reversal.
- **`OVERNIGHT_GAP_FADE`**: weekend-gap mechanism; crypto has no weekend close.
- **`FACTOR_SCALPING`**: the duration criterion (`hold p50 < 0.5h confirmed pós-R4`) is satisfied (p50 = 0.00h), but the family criterion also requires "entry distribuído". This system is concentrated 15-19 UTC and dominated by a *single* feature (importance 0.89), not multi-factor. Per `decoder.md`, this family was emptied 6→0 post-Opus precisely because Sonnet over-attributed to it; honest verdict here is to reject it.
- **`MARTINGALE_GRID`**: PASS on sanity (lot p95/p50 = 1.26, max_streak = 0, steps = 0).
- **`H1_MOMENTUM_GOLD` (provisional)**: matches mechanically (entry-on-H1-momentum, balanced direction 54.6% Buy, tree CV > 0.85), but the registered provisional criterion is **Gold/XAU asset** (n=1, system 6541963). Asset here is BTCUSD; expanding the criterion to "any non-FX risk asset" would dilute the provisional family beyond its registered evidence and pre-empt R1 review.
- **`NEWS_RELEASE_MOMENTUM` (provisional)**: criterion requires a clock-anchored bucket with **>30% trades**. Top hour 17:00 UTC = 70/436 = 16.1% — does not meet the bar (the reference system 1612420 is at ~45% in 15:30 UTC). The 5-min bucket 15:30 UTC has 12 trades (2.75%, tied #1), suggestive of news adjacency but well below the criterion. Name flag also fails (system name "Happy Bitcoin", not "NEWS"/"HF News"). Per task instruction, classifying only from observed trade/OHLC evidence and not assuming a live economic-calendar implementation; the news adjacency is captured as a `risk_flag`.
- **`SWING_TREND_MOMENTUM` (provisional)**: requires hold p50 > 72h; observed p50 = 0.00h.

The pattern is **internally coherent** (high CV, balanced Buy/Sell, no martingale, single-feature mechanism that survives multiple-comparison correction) but **structurally outside the enum**. Per `_diagnostics/5R-1-hardening.md` §1, the honest output is `family: UNCATEGORIZED` + `reason_code: taxonomy_gap` + `candidate_new_family: H1_MOMENTUM_BTC` (a crypto-asset analogue of `H1_MOMENTUM_GOLD`). Whether this becomes a registered family depends on a 2nd independent BTC system surfacing in R1 plus explicit user approval per the §1 acceptance criterion (≥1 system + citation + user approval, with `provisional=True`).

## Rule derivation

- **Entry window** `[15:00, 20:00] UTC`: top-5 hours by trade count (15-19 UTC) cover 233/436 = 53.4% of trades; widening one hour on the right (20:00) absorbs spillover and aligns with the US-cash-session block. Crypto trades 24/7, so this window is a *signal filter* derived empirically from the trade record, not an exchange-session constraint.
- **Pair** `BTCUSD`: the entire trade record is one pair (436/436 = 100%).
- **Direction logic**: taken verbatim from rank-1 tree's primary split (`bb_pos_20_2_H1 ≤ 0.23` → class 0 = SELL across all sub-leaves; `> 0.23` → class 1 = BUY across all sub-leaves). Sub-leaves on `bb_pos_20_2_M5`, `ema_dist_20_H4`, `atr_ratio_H4` do not change the leaf class, so those splits are non-load-bearing and were dropped to keep the rule executable. The `> 0.23` threshold is one tick above the rank-6 univariate BUY threshold (`> 0.2043`, match_rate_cv 0.867) and consistent with rank-7 (`ema_dist_20_H1 > 0.33`, match_rate_cv 0.862) which expresses the same "above H1 trend" condition via a different feature. No threshold was invented; all numbers are taken directly from `candidates.json`.
- **Exit** `max_holding_hours = 1.5`: covers max observed hold (1.23h) with a small safety margin. `take_profit_pips`/`stop_loss_pips` set to `null` because exit_kind = 100% `manual_or_time`; no SL/TP signature is observable in the trade record (would require pip-level draw analysis Stage 1 did not extract for crypto).
- **Sizing** `proportional_equity_2pct`: martingale flag PASS, lot p95/p50 = 1.26 — consistent with proportional sizing decay/recovery, not a doubling grid. (Lot p50 ≈ 93,659 reflects MT4 BTCUSD volume × contract-size convention; not a position-sizing signal in the rule sense.)

## Confidence breakdown

- **Family identification: 0.55** — the *mechanism* (H1 momentum continuation, single-feature dominance, balanced direction) is well-supported, but the *family slot* is empty: no FX-session family fits, the closest provisional (`H1_MOMENTUM_GOLD`) has an asset constraint that excludes BTC, and `NEWS_RELEASE_MOMENTUM` fails its own name+clock-anchor criteria. Output `UNCATEGORIZED` is honest and rejects forced-fit.
- **Direction rule: 0.80** — tree CV 0.858 with std 0.036 (5-fold accs 0.80–0.90) and three independent univariate rules confirm the same H1-up → BUY signal. Bonferroni-corrected p-values < 1e-50 over 518 tests survive aggressive multiple-comparison correction per [evidence_based_ta, p.264-265].
- **Exit logic: 0.55** — only `manual_or_time` is observed and max hold is 1.23h, but no internal exit feature is identified. The 1.5h cap is empirical (max + margin), not derived; the `needs_m1_review` flag captures the sub-M5 sensitivity (p50 = 0.00h).
- **Overall: 0.62** = weighted mean (family 0.4 × 0.55 + direction 0.3 × 0.80 + exit 0.2 × 0.55 + asset/sizing certainty 0.1 × 0.85). Confidence is bounded above by family uncertainty: high mechanistic confidence cannot rescue an out-of-enum classification.

## Open questions (for Stage 3 + posteriores)

- **Calendar-aware replication.** The 15:30 UTC 5-min bucket (12 trades, tied top) is the canonical 08:30 ET US economic-release slot. Stage 3 replicator should test (a) the rule as written above, and (b) an alternative variant masking entries within ±15 min of major US releases. If the masked variant materially underperforms the unmasked, that is empirical evidence of a calendar-aware production logic that this signal_rule does not encode.
- **M1 / sub-minute timing.** With p50 = 0.00h and p95 = 0.18h (~10.8 min), the M5 anchor used in Stage 1 features may already be coarser than the production decision frequency. Replicator should re-derive `bb_pos_20_2_H1` and `ema_dist_20_H1` against M1 OHLC and confirm signal stability across timeframes before publishing a reliability score. This is a per-system replication note; project-wide timeframe is NOT changed here.
- **`H1_MOMENTUM_BTC` as registered family.** The natural analogue of `H1_MOMENTUM_GOLD` for crypto. Should be evaluated for promotion only if R1 surfaces a 2nd independent BTC/ETH system with the same signature (single-feature H1 momentum, balanced direction, sub-hour hold, no clock-anchor >30%) and only with explicit user approval per `_diagnostics/5R-1-hardening.md` §1. Until then, leave `family=UNCATEGORIZED + candidate_new_family=H1_MOMENTUM_BTC`.
- **Vendor / venue risk.** DecodeFX broker on a HappyForex catalogue page: no Pepperstone/Inter equivalence is implied. Even if the rule replicates, executing BTCUSD CFD at the same spread/swap/funding-rate profile is unverified (`[machine_trading, p.202, ch.7]`).
- **Direction vs base-rate.** Sample is 54.6% Buy / 45.4% Sell over a BTC bull regime. Stage 3 must benchmark the rule against `always-Buy` and a frequency-matched-random baseline (5R-1-hardening §3) to confirm edge beyond the regime drift, before any reliability score is reported.
