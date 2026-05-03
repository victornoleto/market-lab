---
system_id: 3568877
family: UNCATEGORIZED
confidence: 0.28
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]   # no dominant window identified — trades distributed across all 24h
  pairs: [GBPUSD, USDCAD, EURGBP, USDJPY, EURCHF, EURUSD, EURJPY, USDCHF, AUDUSD]
  direction: |
    # WARNING: no candidate achieves match_rate_cv > 0.55 (best = 0.547, rank-10 univariate).
    # Best performing composite rule from tree (rank 1, match_rate_cv=0.524, barely above
    # baseline 0.507). Direction signal is NOT reliably identified.
    #
    # Best available approximation from top univariate candidates (ranks 4-6, 10):
    BUY if ret_10_H1 > 0.001077 AND ret_3_H4 > -0.001184 AND bb_pos_20_2_H1 > -0.5348
    SELL if bb_pos_20_2_M5 > 0.002064
    NONE otherwise
    #
    # REPLICATOR NOTE: these thresholds come directly from candidates.json ranks 4,5,7,10
    # but their combined match_rate is only marginally above chance. Do not deploy.
  exit:
    max_holding_hours: 288   # p95 hold time from fingerprint; p50=3.14h, max=7392h
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_0.02
citations:
  - "[algo_trading_chan, p.153-154, ch.6] — 'mean-reverting strategies have capped upside but potentially unbounded drawdown' — the 73.97% drawdown and p95 hold of 288h are consistent with mean-reversion trades left open for days/weeks without a stop-loss"
  - "[advances_fin_ml, p.159] — 'Backtesting is not a research tool. Feature importance is.' — the top tree feature is ema_dist_20_H4 (importance=0.29) but MDA/SFI agreement is unavailable; family cannot be reliably identified from match_rate alone"
  - "[evidence_based_ta, p.283-287] — 'the observed performance of the best of N rules systematically overestimates expected performance' — with 558 tested features and best match_rate=0.547 (raw_p 1.47e-09, Bonferroni-corrected p=8.20e-07), the direction edge is marginal and may be noise after data-mining correction"
risk_flags:
  - "direction_unidentified: best candidate match_rate_cv=0.524 vs baseline=0.507; delta=+0.017 — below the 0.65 threshold required for confidence > 0.5"
  - "extreme_hold_times: p95=288h (12 days), max=7392h (308 days) — system is NOT a pure intraday strategy; exit logic is unknown"
  - "high_drawdown: 73.97% drawdown on a REAL account suggests long-duration adverse open trades without hard stop; potential slow martingale-like equity curve even though lot ratio=1.00"
  - "obscure_broker: Fort Financial Services is not a top-tier regulated broker; confidence reduced by 0.10"
  - "system_labeled_OLD: vendor marks this as 'OLD Happy Frequency v1.1'; likely deprecated/replaced; edge persistence unknown"
  - "blackout: data ends 2021-06-16; no post-2021 evidence available"
  - "timing_distribution_flat: entry hours span all 24h with no peak above 331/3998=8.3% share; no session window is dominant"
---

# Decoded signal — OLD Happy Frequency v1.1 (id 3568877)

## Family rationale

**UNCATEGORIZED** is the mandatory classification. All seven named families in the taxonomy require a dominant entry window aligned with a known FX session, and all require a direction rule that can be recovered with confidence. Neither condition is met here.

The five top entry hours (03:00, 10:00, 17:00, 18:00, 16:00 UTC) span four distinct FX sessions: Asian open (03:00), London mid-session (10:00), NY/London overlap and NY afternoon (16:00-18:00). No single session accounts for more than ~8.3% of the 3,998 trades (331 trades at hour 03:00). This flat distribution rules out `LATE_NY_BREAKOUT` (requires ≥21:00-01:00 UTC concentration), `LONDON_OPEN_MOMENTUM` and `LONDON_OPEN_MR` (require 06:00-09:00 UTC cluster), `NY_SESSION_REVERSAL` and `OVERLAP_NY_LONDON_RANGE` (require 12:00-16:00 UTC cluster), and `OVERNIGHT_GAP_FADE` (requires Friday-close / Monday-open pattern). `FACTOR_SCALPING` would require p50 holding time < 30 min; the observed p50 = 3.14h disqualifies it. `MARTINGALE_GRID` is excluded by the sanity check (lot p95/p50 ratio = 1.00, martingale flag = PASS).

The extreme p95 hold time (288h = 12 days) and max hold time (7,392h = 308 days) suggest some trades were carried for months, consistent with a multi-session swing system that has no hard stop-loss. The 73.97% drawdown on a real account supports this: as Chan notes in *Algorithmic Trading* [p.153-154], "mean-reverting strategies have capped upside but potentially unbounded drawdown" — the equity curve profile (gain +1,281% gross but drawdown 73.97% at close) is consistent with a system that harvested frequent small wins while occasionally holding large losing positions for extended periods without a stop.

The four alternatives considered and rejected:

1. `LATE_NY_BREAKOUT` — entry peak at 03:00 UTC is 6 hours before the 21:00-01:00 window. The 5-minute granularity shows 03:00 (164 trades) and 02:00 (111 trades) as the sharpest intra-hour peaks but these map to early Tokyo open, not the NY-overnight breakout window associated with the named family.
2. `LONDON_OPEN_MOMENTUM` — hour 10:00 (326 trades) is active but it falls within London mid-session, not the 06:00-09:00 London open cluster required by the family definition. Buy rates at hour 10:00 are exactly 50.0%, giving no directional bias signal.
3. `OVERLAP_NY_LONDON_RANGE` — hours 16:00-18:00 are active (285-294 trades each) but collectively they still represent only ~22% of total trades while being spread over 3 hours.
4. `FACTOR_SCALPING` — the p50 hold of 3.14h is too long; factor scalping requires sub-30-minute durations.

## Rule derivation

The best candidate across all three miners is the decision tree at rank 1 with `match_rate_cv = 0.524` (std = 0.017). The baseline (Always-Buy) achieves `match_rate_cv = 0.507`. The incremental edge is only +1.7 percentage points, with fold accuracy ranging from 0.499 to 0.544 — highly unstable. The RIPPER ruleset (rank 3) achieves 0.504 with std = 0.046, which is even worse: the high standard deviation indicates the ruleset overfits individual folds.

The top univariate rules do slightly better in isolation:
- Rank 10: `ret_10_H1 > 0.001077 => Buy` — match_rate_cv = 0.547, coverage = 0.40, Bonferroni-corrected p = 8.20e-07. This is the strongest single feature.
- Rank 5: `ret_3_H4 > -0.001184 => Buy` — match_rate_cv = 0.546, coverage = 0.60, p_corr = 1.46e-06.
- Rank 4: `bb_pos_20_2_H1 > -0.5348 => Buy` — match_rate_cv = 0.544, coverage = 0.70, p_corr = 6.47e-06.

All three are statistically significant after Bonferroni correction (558 tests), consistent with Aronson's data-mining correction framework [evidence_based_ta, p.283-287]. However, their match rates are only 3.7-4.0pp above chance. As Aronson states [p.283-287], when many rules are tested, "the observed performance of the best of N rules systematically overestimates expected performance." With 558 features, a raw p of ~1e-9 is required to survive correction — all three survive, but their *economic* edge (< 5pp lift) is insufficient to build a reliable replicator rule.

The decision tree top feature is `ema_dist_20_H4` (importance = 0.29), meaning roughly 29% of the direction signal in the tree comes from the H4 EMA distance. However, the tree's overall CV accuracy of 52.4% is only marginally better than Always-Buy (50.7%), confirming that even the best composite model cannot reliably discriminate direction. López de Prado [advances_fin_ml, p.159] notes that "Backtesting is not a research tool. Feature importance is" — in this case, even feature importance analysis fails to produce a useful signal.

The direction rule in the YAML front-matter uses the exact thresholds from candidates.json (ranks 4, 5, 7, 10) but is marked explicitly as insufficient for replication. The thresholds are preserved for Stage 3 diagnostic backtesting, not for deployment.

## Confidence breakdown

- Family identification: 0.85 — the flat timing distribution and the multi-session evidence strongly confirm UNCATEGORIZED; the main uncertainty is whether 03:00 UTC could represent a Tokyo-session breakout family not currently in the taxonomy.
- Direction rule: 0.10 — all candidates have match_rate_cv within 0.02 of baseline; the direction signal cannot be reliably decoded from the available features.
- Exit logic: 0.25 — p50 hold of 3.14h provides a lower bound; p95 hold of 288h shows many trades are held much longer; the exit mechanism is clearly not purely time-based for all trades.
- Broker penalty applied: -0.10 (Fort Financial Services is non-top-tier broker; REAL account but confidence reduced)
- Overall: 0.28 = weighted mean applying 0.25 weight to family, 0.50 weight to direction, 0.25 weight to exit; then applying broker penalty

## Open questions (for Stage 3 + posteriores)

- **Is there a hidden session filter?** The 03:00 UTC peak is curious — it is 2 hours after midnight UTC, aligning with 12:00 JST (Tokyo mid-session). Stage 3 should test whether separating the 02:00-04:00 UTC sub-population produces a distinct and better-characterized direction rule.
- **What drives the extreme hold times?** Some trades are held 12+ days. This is likely a consequence of no stop-loss and the EA waiting for the trade to return to profit. Stage 3 should examine whether the long-hold trades are losers being carried, or a different trade type (e.g., longer-horizon swing entries mixed with intraday entries).
- **Is the direction rule pair-specific?** The Buy% by pair varies from 13.7% (AUDUSD, heavily short) to 65.9% (USDCAD, heavily long). A pair-specific direction rule (not a universal rule) might recover signal that the pooled miner misses. Stage 3 should test pair-stratified direction models.
- **Can the 73.97% drawdown be explained by position accumulation?** Lot ratio = 1.00 rules out classical martingale doubling, but the system could accumulate multiple positions on the same pair (grid-like but fixed-lot). Stage 3 should check max simultaneous open trades per pair.
- **Is the dollar_index_proxy feature in RIPPER rule 3 meaningful?** The RIPPER clause `close_vs_session_open_H4=1.0^dollar_index_proxy=>0.67^bb_pos_20_2_H1=>0.94^ret_3_H4=>0.0064` is the only candidate that mentions `dollar_index_proxy`. If this feature has real information content, it would suggest a USD-strength conditional rule. Stage 3 should test this feature in isolation.
