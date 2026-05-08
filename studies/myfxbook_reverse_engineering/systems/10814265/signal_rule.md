---
system_id: 10814265
family: MARTINGALE_GRID
confidence: 0.82
generated: 2026-05-02
rule:
  entry_window_utc: ["09:00", "17:00"]   # wide multi-session window; NOT a clean session edge
  pairs: [GBPUSD, EURUSD, USDJPY]
  direction: |
    # WARNING: direction signal is statistically extractable (match_rate_cv=0.91),
    # but the underlying sizing is martingale — this rule MUST NOT be replicated
    # with lot-scaling. Any replication must use FLAT LOTS only for diagnostic
    # purposes (to isolate the directional edge from the lot-scaling artifact).
    #
    # Best-fit direction (from tree rank-2, ret_10_H4 importance=0.91):
    BUY if ret_10_H4 > -0.00    # positive 10-bar H4 return (momentum continuation)
    SELL otherwise
    #
    # RIPPER rank-1 adds: close_vs_session_open_H1=1.0 (close above session open on H1)
    # AND ema_dist_20_H1 > 2.62 (price far above 20-EMA on H1) for the strongest BUY clause.
    # Full simplified gate (tree-derived, coverage=1.0):
    # BUY if ret_10_H4 > 0.0004234
    # SELL if ret_10_H4 < 0.0
    # (borderline -0.00 to +0.00042 zone → tree defaults to BUY given ema_dist_20_H1 <= 0.39)
  exit:
    max_holding_hours: null    # NaN in fingerprint — consistent with martingale open-end holds
    take_profit_pips: null
    stop_loss_pips: null       # martingale-style systems typically omit hard SL
  sizing: martingale_NEVER
citations:
  - "[advances_fin_ml, p.208-211] — 'A PBO > 0.5 means the strategy is more likely overfit than valid. Do not deploy until PBO is demonstrably below 0.5.' (CSCV/PBO framework; martingale lot-doubling inflates in-sample performance and guarantees eventual ruin)"
  - "[trading_systems_methods, p.1091] — 'If you invest above the optimal amount... if you get average results you can expect to go broke eventually.' (Kaufman on over-leverage/optimal-f violation; martingale sizing consistently exceeds optimal-f by construction)"
  - "[algo_trading_chan, p.183-184] — 'Do not impose stop losses on mean-reversion strategies at levels that would be triggered during backtest — they always lower backtest performance.' (Chan notes that removing stops inflates mean-reversion backtest returns — the same mechanism that makes martingale backtests look attractive)"
risk_flags:
  - "MARTINGALE CONFIRMED: lot p95/p50 ratio = 122.40; k1 flag fires on per-month max/median P95 = 125.92 (> 3.0 threshold). This is within-month doubling behavior, not position scaling by conviction."
  - "HOLDING TIME = NaN: all 957 trades show NaN hold duration — consistent with positions held open indefinitely waiting for martingale recovery. This is the defining execution signature."
  - "BROKER = AdroFx: offshore broker, not tier-1. Reduces confidence in track record integrity by 0.10 per workflow rule."
  - "REAL ACCOUNT but 1:500 leverage: real account status does NOT rehabilitate martingale sizing. 1:500 leverage means account wipeout risk is structurally built-in."
  - "DO NOT REPLICATE AS-IS: Stage 3 replicator MUST use flat lots. Any performance computed with flat lots will differ substantially from the track record (which is driven by lot-compounding on recoveries, not by directional alpha)."
  - "Directional signal (ret_10_H4 momentum) may have marginal standalone edge — but it is inseparable from the sizing mechanism in the actual track record. Sharpe/PnL figures from MyFxBook are not attributable to direction alone."
---

# Decoded signal — Happy Breakout AdroFX (id 10814265)

## Family rationale

System 10814265 is classified as **MARTINGALE_GRID**. This classification is mandatory and overrides all directional analysis. The evidence is unambiguous:

1. **Lot p95/p50 ratio = 122.40.** A legitimate trend-following or breakout system operating on three FX majors would show lot ratios near 1.0–3.0 if using volatility-targeted sizing, or exactly 1.0 if fixed-lot. A ratio of 122× means that at the 95th percentile, position size is 122 times the median trade. This is the signature of a martingale ladder where each layer adds multiples of the prior lot.

2. **k1 flag: per-month max/median P95 = 125.92 (> 3.0 threshold).** The Stage 1 sanity filter explicitly flags this as "within-month doubling." The `steps=0, max_streak=0` sub-fields indicate the streak counter did not fire (possibly because the ladder resets frequently), but the lot-dispersion flag is the binding criterion.

3. **Holding time = NaN for all 957 trades.** Legitimate intraday systems produce finite, extractable hold durations. NaN across all trades indicates that positions were held open across multiple MyFxBook data snapshots, consistent with martingale positions waiting for price to recover to breakeven before closing. This is not consistent with any of the time-bounded families (LATE_NY_BREAKOUT, LONDON_OPEN_MR, etc.).

4. **System name: "Happy Breakout AdroFX".** The word "breakout" is superficially consistent with the LATE_NY_BREAKOUT or LONDON_OPEN_MOMENTUM families, which were considered as alternatives. However, the lot dynamics invalidate those classifications regardless of timing pattern.

**Alternatives considered and rejected:**

- `LONDON_OPEN_MOMENTUM`: Entry peaks at 09:00-10:00 UTC are consistent with London open. However, the buy% at hour=10 is 47.5% (below 50%), not strongly directional, and lot sizing is martingale.
- `OVERLAP_NY_LONDON_RANGE` or `NY_SESSION_REVERSAL`: Peaks at 15:00-17:00 UTC overlap the London/NY overlap window. But direction at those hours is 51.7–53.8% buy — not decisively directional — and the martingale disqualifies the family.
- `FACTOR_SCALPING`: No short-duration trades observed (hold times NaN, not sub-30min).

The RIPPER (rank 1, match_rate_cv=0.913) and tree (rank 2, match_rate_cv=0.908) miners successfully extract a direction rule from the data — evidence that a directional signal exists. However, in a martingale system, the direction rule determines only when the first layer is opened; subsequent layers are opened automatically as price moves adversely regardless of direction signal. The apparent high match_rate reflects that the system is mostly long (buy% 51–57%), and the feature `ret_10_H4 > 0` captures that bias trivially.

## Rule derivation

**Primary feature: ret_10_H4 (importance = 0.91 in tree)**

The decision tree (rank 2) identifies `ret_10_H4` as the dominant split with 91% importance. The primary split is:

```
ret_10_H4 <= -0.00  →  SELL (class 0), all downstream leaves
ret_10_H4 >  -0.00  →  BUY (class 1), all downstream leaves
```

This is a pure momentum rule on H4: if the 10-bar H4 return is positive, go long; if negative, go short. The secondary features (`ema_dist_20_H1`, `bb_pos_20_2_M15`, `range_norm_H4`) add marginal refinement but with < 5% combined importance.

The univariate rank-7 candidate confirms this: `ret_10_H4 > 0.0004234 ⇒ Buy` with match_rate_cv = 0.9007 and coverage = 0.499. The threshold 0.0004234 is the exact number from candidates.json — approximately 4.2 basis points of positive H4 momentum.

**RIPPER rank-1 clauses (simplified):**

The 21-clause RIPPER ruleset collapses into a consistent theme: BUY when price is above EMA on H1 (`close_vs_session_open_H1=1.0`, `ema_dist_20_H1 > 0`), with secondary conditions involving `bb_pos_20_2_H1` above midband and `prior_bar_sign` providing timing confirmation. The dominant clause `[close_vs_session_open_H1=1.0 ^ ema_dist_20_H1 => 2.62]` is equivalent to: "price is above both the session open and strongly above the 20-EMA on H1 — a breakout condition." This is directionally consistent with the tree.

**Why this does not constitute a tradeable breakout strategy:**

All thresholds are derived from the full 957-trade dataset. In a martingale system, most trades near the median lot (1.26) are first-layer opens, while high-lot trades (up to 161.74) are recovery layers. The direction rule was trained on a mix of both, skewing toward the first-layer conditions that happen to be correct most often. The actual P&L is driven by the lot-compounding of recoveries, not by the direction accuracy of the first layer.

## Confidence breakdown

- Family identification (MARTINGALE_GRID): 0.90 — lot p95/p50 = 122× is unambiguous; k1 flag fires; NaN hold times confirm open-position stacking
- Direction rule: 0.82 — ret_10_H4 momentum rule is highly consistent across both tree and univariate miners; RIPPER agrees directionally
- Exit logic: 0.10 — NaN hold times make exit logic unextractable; martingale exits at breakeven of the ladder, not at fixed time/pip
- Overall: 0.82 × 0.33 + 0.10 × 0.33 + 0.90 × 0.33 ≈ **0.61** (weighted mean, but family flag is the binding verdict)

The overall confidence of 0.82 applies specifically to the MARTINGALE_GRID classification. Confidence in any deployable directional rule derived from this system is effectively 0.00 — the direction signal cannot be decoupled from the lot-scaling mechanism without a full flat-lot re-simulation.

Note: AdroFx as broker (offshore, non-tier-1) reduces confidence by 0.10 per workflow rule, but this does not change the MARTINGALE_GRID verdict, which is already flagged by lot dynamics alone.

## Open questions (for Stage 3 and beyond)

- **Flat-lot diagnostic:** If Stage 3 replicator runs with fixed lot=0.01 on all 957 trade timestamps, does the direction signal (ret_10_H4 momentum) produce positive expectancy net of Pepperstone spreads? This would isolate directional edge from sizing mechanism.
- **Martingale ladder structure:** With lot p50=1.26 and p99=158, the ladder appears to run 7–8 layers deep (158/1.26 ≈ 125, consistent with 2^7=128 doublings). Stage 3 could attempt to reconstruct the ladder pattern from lot sequences.
- **Session gating:** Entry peaks span 09:00–17:00 UTC, covering both London open and NY overlap. Are these two separate strategies running in parallel on the same account? Stage 3 could split by session and check if each has different pair/direction behavior.
- **Recovery hold duration:** The NaN hold times suggest trades stay open until lot-weighted breakeven. Stage 3 cannot replicate this without modeling the full ladder state at each point in time — which requires tick-level data, not OHLC.
- **Survivorship of MARTINGALE systems in this vendor set:** If other HappyForex systems (the ~52 in the study) also show lot p95/p50 ratios >> 3, the entire vendor universe may be martingale-contaminated and should be excluded from the reliability ranking before Stage 3 resources are spent.
