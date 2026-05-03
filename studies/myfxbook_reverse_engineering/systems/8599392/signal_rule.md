---
system_id: 8599392
family: FACTOR_SCALPING
confidence: 0.38
generated: 2026-05-02
rule:
  entry_window_utc: ["02:00", "04:00"]   # primary peak 03:00 UTC (300 trades at 03:xx); secondary windows 15-19 UTC are weaker
  pairs: [GBPUSD, EURUSD, AUDUSD, EURCHF, EURGBP, USDCAD]
  direction: |
    # Primary direction signal derived from tree (rank 1) + RIPPER (rank 2)
    # Features are Stage-1 names: bb_pos_20_2_H1, ema_dist_20_H4, atr_ratio_M15,
    # ret_10_M5, close_vs_session_open_M5
    #
    # Simplified executable rule (thresholds from candidates.json exactly):
    BUY if bb_pos_20_2_H1 > -0.5444 AND ret_10_M5 <= 0.00 AND ema_dist_20_H4 <= 0.83
    BUY if bb_pos_20_2_H1 > 0.46 AND atr_ratio_M15 <= 0.55 AND ema_dist_20_H1 <= 2.76 AND ema_dist_20_H4 <= 1.49
    BUY if close_vs_session_open_M5 == 1.0 AND ema_dist_20_H1 > 2.51
    SELL otherwise
    # NOTE: USDCAD has buy_pct=41.6% — primary direction for this pair is SELL-biased.
    # USDCAD override: reverse BUY/SELL labels from above rules.
  exit:
    max_holding_hours: 6      # p50 hold = 5.33h; time-based exit assumed
    take_profit_pips: null    # not recoverable from track record alone
    stop_loss_pips: null      # not recoverable from track record alone
  sizing: fixed_lot_X        # lot p95/p50=1.00 at aggregate level; but per-month max/median=209x — SUSPECTED MARTINGALE (see risk_flags)
citations:
  - "[trading_systems_methods, p.323-324] — 'Bollinger Bands: 20-day MA ± 2σ of closing prices. 2σ ≈ 87% confidence in skewed distributions.'"
  - "[advances_fin_ml, p.160-162] — 'Mean Decrease Impurity (MDI) — in-bag feature importance measure based on weighted average impurity reduction across all splits; fast but biased toward high-cardinality features.' bb_pos_20_2_H1 importance=0.49 interpreted via MDI ranking."
  - "[algo_trading_chan, p.95, ch.4] — 'Apply a momentum filter (price above long-term moving average) as a gate on a mean-reversion entry signal.' close_vs_session_open_M5 in RIPPER plays this role."
  - "[trading_systems_methods, p.13] — 'Low-noise markets (USD crossrates) → trend-following. High-noise markets → mean-reverting.' Mixed BB-position + EMA-distance signals suggest neither pure regime."
risk_flags:
  - "MARTINGALE SUSPECT: k1_flag 'per-month max/median P95=209.40 (>3.0)' — within-month position doubling detected. Lot p95/p50=1.00 at overall level but within-month dynamics reveal compounding. This is NOT a clean signal system."
  - "CONFIDENCE PENALIZED -0.10: broker=ORBEX — non-primary broker, reliability of track record less certain than Tier-1 (Pepperstone/IBKR)."
  - "CONFIDENCE PENALIZED: family identification ambiguous — 03:00 UTC peak does not map cleanly to any canonical session family in taxonomy. Best fit is FACTOR_SCALPING but with low certainty."
  - "hold p95=672h suggests some trades held 28 days — inconsistent with short-term scalping. Possible grid/basket management with extended holdout."
  - "drawdown=64.23% with equity at 49.45% of balance at time of scrape — severe open floating loss. Classic grid/martingale signature."
  - "System name 'Happy Frequency' + 4000 trades over ~18 months = ~7 trades/day — high activity consistent with multi-session scalper or grid."
  - "blackout: system active 2023-11-22 onward (current, real account). Edge persistence unknown post-2025."
  - "max_holding_hours=6 is p50 only; p95=672h makes a fixed exit rule unrepresentative of actual system behavior."
---

# Decoded signal — Happy Frequency Orbex - REAL (id 8599392)

## Family rationale

The primary timing peak at 03:00 UTC (431 trades, 300 at 03:xx specifically) places entries in the mid-Asian session — roughly the overlap of Tokyo and early Sydney. This does not correspond to any of the named high-confidence families in the taxonomy:

- `LATE_NY_BREAKOUT` requires entry concentration at 21-01 UTC — this system's 03:00 UTC peak is outside that window.
- `LONDON_OPEN_MOMENTUM` and `LONDON_OPEN_MR` require 06-09 UTC — absent here.
- `NY_SESSION_REVERSAL` and `OVERLAP_NY_LONDON_RANGE` require 12-16 UTC — present as secondary peaks (15:00=282, 17:00=335, 18:00=292) but not dominant.

The entry distribution is unusually flat across the trading day: top-5 hours account for only (431+335+295+292+282)/4000 = 40% of trades, meaning 60% of activity is spread across the remaining 19 hours. This poly-modal, session-agnostic pattern is the hallmark of `FACTOR_SCALPING` — a system that enters on price/volatility-band conditions regardless of session, not on session-specific timing events.

The system name "Happy Frequency" further signals a frequency-targeting approach (maximize trade count, diversify across many entry opportunities) rather than a session-edge approach. With 4000 trades over ~18 months (≈7 trades/day across 6 pairs), the cadence is consistent with a continuous-monitoring scalper.

However, confidence in even `FACTOR_SCALPING` is substantially reduced by the martingale warning flag (within-month position doubling, k1_pass=FAIL). A pure martingale grid would have been filtered by Stage 1, but the "soft" within-month doubling signature and the extreme hold time distribution (p95=672h, max=13752h) suggest the system may be managing a grid of open positions, not individual independent scalps. The 64.23% drawdown with current equity at 49.45% of balance is a classic symptom of an open floating grid. `MARTINGALE_GRID` was considered but not confirmed because the lot p95/p50=1.00 at aggregate level and max streak=0 suggest the grid is not strictly geometric — it may be a fixed-lot grid without compounding, which explains why Stage 1 did not hard-block it.

`UNCATEGORIZED` was considered but rejected because there is sufficient structure in the candidate rules (BB position + EMA distance + ATR ratio) to formulate a hypothesis, even if confidence is low.

**Final classification: FACTOR_SCALPING with confidence 0.38.** The low confidence reflects: (a) non-canonical session timing, (b) suspected grid management contaminating the signal structure, (c) ORBEX broker reducing track record reliability.

## Rule derivation

**Top candidate analysis (ranked by match_rate_cv * sqrt(coverage)):**

1. **Tree (rank 1)**: match_rate_cv=0.5855, coverage=1.0 → score=0.5855. The decision tree identifies `bb_pos_20_2_H1` as the dominant feature (MDI importance=0.49). The primary split is at bb_pos_20_2_H1 ≤ 0.46 / > 0.46. Within the lower branch, a secondary split at bb_pos_20_2_H1 ≤ -0.75 routes to BUY (below lower Bollinger band → mean-reversion buy). Within -0.75 to 0.46, BUY when ema_dist_20_H4 ≤ 0.83 AND ret_10_M5 ≤ 0.00 (price not trending up on M5). Above 0.46, BUY when atr_ratio_M15 ≤ 0.55 AND ema_dist_20_H4 ≤ 1.49.

2. **RIPPER (rank 2)**: match_rate_cv=0.531, coverage=1.0. All three clauses require `close_vs_session_open_M5=1.0` (price above session open) as the primary condition. Secondary conditions include `ema_dist_20_H1 > 2.51` (rank-6 univariate threshold of -0.9961 not directly applicable here — this is a different condition) or specific ret_1_H4 / ret_3_M1 / ret_1_M1 ranges on DOW=0 (Monday). This confirms intraday momentum (price above session open) as a secondary BUY trigger.

3. **Univariate top performers**: 
   - `ret_10_H1 > -0.000814 ⇒ Buy` (match_rate_cv=0.593, coverage=0.60)
   - `ret_3_H4 > -0.0008216 ⇒ Buy` (match_rate_cv=0.5925, coverage=0.60)
   - `bb_pos_20_2_H1 > -0.5444 ⇒ Buy` (match_rate_cv=0.5875, coverage=0.70)

The thresholds used in the `direction:` block are taken **verbatim** from candidates.json:
- `bb_pos_20_2_H1 > -0.5444` from rank 5 univariate
- `ema_dist_20_H4 <= 0.83` and `ema_dist_20_H4 <= 1.49` from tree branches
- `bb_pos_20_2_H1 <= 0.46` and `> 0.46` from tree split points
- `atr_ratio_M15 <= 0.55` from tree branch
- `ema_dist_20_H1 <= 2.76` and `> 2.51` from tree and RIPPER respectively
- `ret_10_M5 <= 0.00` from tree branch
- `close_vs_session_open_M5 == 1.0` from RIPPER primary condition

The USDCAD directional flip (BUY% only 41.6%) is empirically derived from `direction_by_pair` in the fingerprint. The rules above produce a buy-biased output (consistent with GBPUSD/EURUSD/AUDUSD/EURCHF/EURGBP at 53-57% buy); USDCAD requires label inversion.

**Critical caveat**: The best match_rate_cv is 0.5875 (univariate bb_pos_H1) and 0.5855 (tree). These are only marginally above baseline (0.5285 always-buy). Per Aronson [evidence_based_ta, p.283-287], the observed performance of the best of many tested rules systematically overestimates expected performance — data-mining bias is a concern even with the CV approach. The direction signal is weak.

## Confidence breakdown

- Family identification: 0.40 — FACTOR_SCALPING is the best fit for a poly-modal timing distribution, but the martingale signature and extreme hold times create ambiguity; MARTINGALE_GRID cannot be ruled out.
- Direction rule: 0.45 — BB position + EMA distance features have genuine univariate signal (p_corr < 1e-10 after Bonferroni) but match_rate_cv barely clears 0.59 vs 0.53 baseline; very noisy.
- Exit logic: 0.25 — p50=5.33h used as max_holding_hours but p95=672h suggests the real exit is complex (likely grid management or trailing TP); time-based exit approximation is poor.
- Overall: 0.38 = weighted mean (family 0.40, direction 0.45, exit 0.25, martingale penalty -0.05)

## Open questions (para Stage 3 + posteriores)

- **Grid/martingale confirmation**: Stage 3 should specifically test whether the within-month lot doubling is systematic (i.e., trade N+1 is placed when trade N is losing). If confirmed as grid, system should be re-classified as MARTINGALE_GRID and excluded from the replicator.
- **USDCAD directional inversion**: The pair has 41.6% buy rate vs 53-57% for others. Stage 3 should test whether applying opposite labels for USDCAD improves match rate, or whether USDCAD should be dropped entirely.
- **Secondary timing clusters**: The 15-19 UTC secondary peak (London/NY overlap) may represent a different sub-strategy within the same EA. Stage 3 could test whether splitting by hour_utc bucket improves match rate (03:00 UTC session vs. 15-19 UTC session as separate sub-models).
- **close_vs_session_open_M5 definition**: This feature's session boundary definition (what "session open" means at 03:00 UTC) needs to be confirmed in Stage 1 feature engineering code. If "session" = 00:00 UTC daily open, then close_vs_session_open_M5=1.0 at 03:00 means price has been rising for 3 hours.
- **ATR ratio interpretation**: `atr_ratio_M15` appears in both tree branches as a volatility filter. Stage 3 should test whether a fixed threshold (≤ 0.49 / ≤ 0.55 from tree) or a dynamic vol-regime gate is more stable.
- **Severe equity loss (49.45% of balance)**: The system is currently in a large floating loss. Stage 3 should flag whether the open-position grid is part of the modeled strategy or an anomaly that biases the track record since late 2024.
- **bb_pos thresholds across timeframes**: Three BB features appear (H1, H4, M15) with similar structures. Stage 3 should test whether multi-timeframe BB alignment (e.g., all three above lower band) improves signal consistency.
