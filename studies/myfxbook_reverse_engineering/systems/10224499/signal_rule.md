---
system_id: 10224499
family: LATE_NY_BREAKOUT
confidence: 0.72
generated: 2026-05-02
rule:
  entry_window_utc: ["22:00", "00:59"]
  pairs: [USDCAD, EURUSD, GBPUSD]
  direction: |
    # Decision logic — rank-1 tree (CV acc 0.688 ± 0.070), cross-confirmed by
    # rank-9 univariate (bb_pos_20_2_M15 > 0.0768 ⇒ Sell, p_corr=9.0e-8) and
    # rank-3 (bb_pos_20_2_H1 > -0.3409 ⇒ Sell, p_corr=6.6e-5).
    #
    # Class encoding inferred from baseline rank-7 (y_buy mean = 0.4842) and
    # univariate sign: class 0 = Sell, class 1 = Buy. So tree leaves read as
    # "high bb_pos ⇒ Sell, low bb_pos ⇒ Buy" — fade BB position toward mid-band
    # at the late-NY / pre-Tokyo handover window.

    SELL if bb_pos_20_2_M15 > 0.15
    BUY  if bb_pos_20_2_M15 <= 0.15
    # Tie-breaker fallback (rank-2 RIPPER conjunction) when M15 BB-pos ~ 0.15:
    # SELL also if (prior_bar_sign_H4 == -1 AND hour_utc == 23)
    # SELL also if ema_dist_20_M15 in [-1.08, -0.50]
  exit:
    max_holding_hours: 5.0     # p95 hold = 5.03h; p50 = 1.74h; max = 12.38h
    take_profit_pips: null      # exit_kind = manual_or_time only — no TP/SL fingerprint
    stop_loss_pips: null
  sizing: fixed_lot_0.01        # lot p50 = p95 = p99 = max = 0.01; martingale flag PASS
citations:
  - "[algo_trading_chan, p.71-73, ch.3] — Bollinger Band Pairs Strategy: 'longsEntry = zScore < -entryZscore; shortsEntry = zScore > entryZscore'. The bb_pos_20_2_M15 fade rule (SELL above mid, BUY below) is the same construct expressed as a bounded BB position instead of a z-score (entryZscore≈0.15 in normalized BB-position units)."
  - "[algo_trading_chan, p.47, ch.2] — 'Set the lookback for moving average and standard deviation in a mean-reversion strategy to a small multiple of the half-life of mean reversion.' M15 BB(20) on FX is consistent with intraday FX half-life (~1-3h) given p50 hold of 1.74h."
  - "[evidence_based_ta, p.341-344] — Monte Carlo Permutation Method controls data-mining bias; rank-3 (p_corr=6.6e-5 across 540 tests) and rank-9 (p_corr=9.0e-8) survive the full multiple-comparison correction, satisfying Aronson's MCP test."
  - "[advances_fin_ml, ch.5] — Tree feature importance (bb_pos_20_2_M15=0.72, ret_10_H1=0.19, ret_10_M15=0.09) gives MDA-style ranking; the top feature dominates by ~4×, characteristic of a single-edge strategy rather than an ensemble."
risk_flags:
  - "Vendor selection / live performance: stats show gain -50% / DD 52.89% on real $50 ForexMart account — not a profitable live system. The decoded rule may be statistically real but commercially unprofitable after costs."
  - "ForexMart is a B-book / folkloric retail broker — slippage and execution quality questionable; pair-level direction tilts (EURUSD 36% Buy, USDCAD 55% Buy) may partially be broker-model artifacts. Reduce confidence by ≥0.10 if replicating on a regulated venue."
  - "Sample n = 221 trades over ~3 years with max gap 41 days — sample is small and may straddle a regime/parameter change. Stage 3 should split pre/post-gap and verify rule stability."
  - "Vendor blackout 2021-2026 forward (HappyForex commercial product) — edge persistence in live conditions is unverified."
  - "Family-description vs direction-logic semantic note: the LATE_NY_BREAKOUT taxonomy entry describes 'capture overnight breakout do range Asian' but the empirically supported direction here is BB-fade (mean-reversion). Empirical criteria (entry 21-01 UTC, exit 1-3h, USD/EUR pairs) all match LATE_NY_BREAKOUT and the partner system 1407880 is already locked to this family in 5R-1-hardening — taxonomy refinement deferred to ranking-phase review (see Open Questions)."
---

# Decoded signal — Happy Market Hours FM (id 10224499)

## Family rationale

Sanity-check vs `LATE_NY_BREAKOUT` empirical criteria from `decoder_taxonomy.TAXONOMY[Family.LATE_NY_BREAKOUT].criteria`:

- **Timing**: 221/221 trades fall in the 22:00-00:59 UTC band, with 23:00 UTC owning 127 trades (57.5%). Fingerprint quote: "23:00 — 127 trades / 22:00 — 50 trades / 00:00 — 44 trades / 01:00 — 0 trades / 04:00 — 0 trades". This is the late-NY → pre-Tokyo handover, fully inside the 21-01 UTC criterion. Match.
- **Hold**: p50 1.74h, p95 5.03h, max 12.38h, all `manual_or_time` exits, no TP/SL fingerprint. Intraday — disqualifies SWING_TREND_MOMENTUM (would require p50 > 72h). Match.
- **Pair universe**: USDCAD (93), EURUSD (66), GBPUSD (62). Pure USD/EUR-major roster, the canonical LATE_NY_BREAKOUT universe. Match.
- **Lot/martingale sanity**: lot p50=p95=p99=max=0.01, max_streak=0, k1_pass — disqualifies MARTINGALE_GRID. Match.
- **6R partner**: paired with 1407880 (also Happy Market Hours, p50=0.98h, also LATE_NY_BREAKOUT) — par primário sobrevivente per `_diagnostics/5R-1-hardening.md` line 80. Independent classification here on its own merits, NOT inherited.

Alternative families considered and rejected against this enum:

- `OVERLAP_NY_LONDON_RANGE` — peak hour 23 UTC is **after** the NY equity close (~21 UTC), not inside the 12-16 UTC overlap window. Reject.
- `NY_SESSION_REVERSAL` — its template peaks at 12-16 UTC; ours peaks at 22-00. Reject. (Also documented as "vendor library has no genuine reversal" in `decoder_taxonomy` review_gate.)
- `LONDON_OPEN_MOMENTUM` / `LONDON_OPEN_MR` — both require 06-09 UTC entry. Reject.
- `OVERNIGHT_GAP_FADE` — Friday-close / Monday-open template with hold > 24h. Reject (p50 = 1.74h).
- `FACTOR_SCALPING` — requires confirmed durations < 30 min; ours is p50 1.74h. Reject.
- `NEWS_RELEASE_MOMENTUM` (provisional) — requires name flag NEWS/HF News + p50 < 5 min. The product name is "Happy Market Hours", not "News"; p50 = 1.74h. Reject.
- `H1_MOMENTUM_GOLD` (provisional) — requires Gold/XAU universe. We have only FX majors. Reject.
- `SWING_TREND_MOMENTUM` (provisional) — requires p50 > 72h. We have p50 = 1.74h. Reject.

## Rule derivation

The rank-1 tree is the cleanest readable signal: `bb_pos_20_2_M15 ≤ 0.15 ⇒ class 1` else `class 0`, CV accuracy 0.688 (5-fold std 0.070, fold accs [0.659, 0.591, 0.795, 0.659, 0.733]). Class encoding is inferred from baseline rank-7 (`Always-Buy y_buy mean = 0.4842` → class 1 = Buy) and the rank-9 univariate (`bb_pos_20_2_M15 > 0.0768 ⇒ Sell`), which is consistent with the tree only if class 1 = Buy and class 0 = Sell. The split point 0.15 is read directly from tree text — not invented. Top feature dominance: 0.72 vs 0.19 vs 0.09.

Univariate corroboration (all p_corr-survivors over 540 tests):

- Rank-3: `bb_pos_20_2_H1 > -0.3409 ⇒ Sell` (acc 0.674, p_corr 6.6e-5, coverage 70%). H1 BB-pos confirms direction sign at the higher timeframe.
- Rank-9: `bb_pos_20_2_M15 > 0.0768 ⇒ Sell` (acc 0.710, p_corr 9.0e-8, coverage 50%). Same feature as the tree, lower threshold, stronger statistical significance.
- Rank-6: `ema_dist_20_M15 > -0.1344 ⇒ Sell` (acc 0.692, p_corr 2.9e-6, coverage 60%). EMA-distance is collinear with BB-position; same edge re-discovered through a different feature.

These survive Bonferroni-style correction at p_corr < 1e-4, satisfying Aronson's Monte Carlo Permutation criterion `[evidence_based_ta, p.341-344]` for data-mining-aware significance.

The rank-2 RIPPER ruleset adds a useful tie-breaker disjunction: when H4 prior bar is bearish AND hour is exactly 23, Sell is favored — incorporated as a fallback in the executable `direction:` block.

Exit logic is purely time-based — no SL/TP cluster in the fingerprint, so we set `max_holding_hours = 5.0` (matches sanity p95). Entry window 22:00-00:59 UTC captures 100% of observed trades.

## Confidence breakdown

- **Family identification**: 0.85 — timing / pairs / hold / sizing all match the LATE_NY_BREAKOUT enum criteria precisely; every alternative explicitly ruled out; partner 1407880 already in this family.
- **Direction rule**: 0.72 — tree CV 0.688 ± 0.070 is solid for FX intraday; multiple BB-based features converge on the same fade direction; but the tree threshold (0.15) and the strongest univariate (0.077) differ — the unified rule may lose accuracy vs per-miner best at sweep.
- **Exit logic**: 0.55 — `manual_or_time` only; cannot distinguish hidden TP/SL from pure time-exit. p95 = 5.03h is a *boundary* observation, not a known rule. Stage 3 should sweep TP/SL grid and inspect exit-time histogram for clustering.
- **Overall**: 0.72 (mean weighted, with -0.10 broker quality and -0.05 small-n penalties applied to the headline number).

## Open questions (for Stage 3 + posteriors)

- Threshold sweep: the unified `bb_pos_20_2_M15 > 0.15` (tree) vs `> 0.077` (univariate rank-9) differ — replicator should sweep [0.05, 0.10, 0.15, 0.20] and report which preserves CV accuracy on OOS.
- Hidden TP/SL: even with `exit_kind = manual_or_time`, vendors often use TP/SL several × the realized hold variance. Sweep TP ∈ [10, 20, 40] pips, SL ∈ [20, 40, 80] pips; check whether p95 = 5.03h is dominated by TP fills, time-exits, or 02 UTC session boundary.
- ForexMart spread/swap re-cost: re-run with ECN spreads — does the BB-fade edge survive a 0.5 → 1.5 pip spread expansion?
- Pre/post 41-day-gap stability: split sample at the gap, re-run candidates Stage 1, confirm BB-fade is detected on both sides. If only post-gap, the system was likely re-tuned after a regime shift.
- Same-bar overlap with sibling 1407880: does the rule fire on the same calendar bar / pair as the older HMH variant? Strong overlap = identical engine across system_ids; weak overlap = independent strategies despite shared brand.
- **Taxonomy refinement (deferred to ranking phase)**: the LATE_NY_BREAKOUT enum description says "captures breakout do range Asian", but the supported direction here is BB-fade (mean-reversion). If 5R-3 ranking surfaces ≥2 systems with the same late-NY + BB-fade signature, propose splitting LATE_NY_BREAKOUT into a momentum-following sub-family and a `LATE_NY_RANGE_FADE` sub-family per the closed-enum-expansion process in `_diagnostics/5R-1-hardening.md` §1. Not raised as `candidate_new_family` here because the empirical criteria of LATE_NY_BREAKOUT (timing + exit + universe) all match.
- News/event sanity: the system name is "Happy Market Hours", not "Happy News"; timing is broad 22-00 UTC, not a single news anchor. We classify only from observed trade/OHLC evidence. A live calendar-aware replication is **not** assumed; if Stage 3 replication shows direction sensitivity to scheduled releases (FOMC, CPI, NFP) inside the entry window, that would be evidence for a calendar-aware overlay we are not currently modelling.
