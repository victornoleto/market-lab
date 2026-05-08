---
system_id: 7603723
family: FACTOR_SCALPING
confidence: 0.52
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]   # entries distributed across all sessions; filtered by 4-hour fixed schedule (00, 04, 08, 12, 16, 20 UTC)
  pairs:
    - GBPUSD
    - EURAUD
    - GBPAUD
    - GBPJPY
    - USDCAD
    - AUDUSD
    - GBPCAD
    - GBPCHF
    - EURCAD
    - EURGBP
    - EURUSD
    - NZDUSD
    - AUDCHF
    - AUDJPY
    - NZDCHF
    - NZDJPY
    - CHFJPY
    - AUDCAD
    - USDCHF
    - CADCHF
    - AUDNZD
    - EURJPY
    - EURCHF
    - CADJPY
    - USDJPY
  direction: |
    # Primary gate: H1 momentum direction (ret_10_H1 is feature importance rank 1, weight 0.66 in tree)
    # Secondary gate: short-term H1 momentum confirmation (ret_3_H1, weight 0.14 in tree)
    # Tertiary: Bollinger Band position filter on H1 (bb_pos_20_2_H1)
    # RIPPER confirms: price must be above session open (close_vs_session_open_M5=1.0) for BUY
    #
    # Executable rule derived from tree (rank 1) + univariate rules (ranks 4-5):
    # NOTE: ret_3_H1 threshold is sign-only (zero crossing) from tree — the univariate
    #       threshold -9.83e-06 (rank 7) belongs to ret_3_H4, not ret_3_H1, and is NOT used here.
    #
    BUY if ret_10_H1 > -2.651e-05 AND ret_3_H1 > 0.0 AND bb_pos_20_2_H1 > -0.23
    SELL if ret_10_H1 <= -2.651e-05 AND ret_3_H1 <= 0.0
    NONE otherwise
    #
    # Additional constraint from RIPPER (rank 2): BUY only when close_vs_session_open_M5 = 1.0
    # (i.e., current price is above M5 session open — confirms intrabar momentum)
    # RIPPER BUY thresholds for ret_10_H1: 0.001-0.002, 0.002-0.0032, 0.0032-0.0047 (exact from candidates.json)
  exit:
    max_holding_hours: 264   # p95 hold = 264h; p50 = 5.54h; system uses manual_or_time exit
    take_profit_pips: null   # not detectable from track record; exit is discretionary/time-based
    stop_loss_pips: null     # not detectable; wide hold distribution implies no hard SL
  sizing: fixed_lot_0.01    # lot p50=0.01, p95=0.01, p95/p50 ratio=1.00 (flat sizing confirmed)
citations:
  - "[algo_trading_chan, p.133-134, ch.6] — 'Cross-sectional momentum: an instrument outperforming its peers continues to outperform' — justifies momentum direction rule across 25 pairs using ret_10_H1 as the cross-sectional signal"
  - "[algo_trading_chan, p.153-154, ch.6] — 'momentum strategies have limited downside (via natural stop loss) but unlimited upside, making them complementary in a diversified portfolio' — supports the no-hard-SL wide hold time design"
  - "[advances_fin_ml, p.160-162, ch.5] — 'Mean Decrease Accuracy (MDA) — out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower' — the tree importance scores (ret_10_H1=0.66, ret_3_H1=0.14) are MDI-style; their concentration validates using ret_10_H1 as the primary rule feature"
risk_flags:
  - "martingale_flag FAIL: k1 per-month max/median P95=5.10 (>3.0) — within-month lot doubling detected; however p95/p50 lot ratio=1.00 globally contradicts classic martingale; may reflect intra-month averaging-up rather than doubling grid — replicator must validate"
  - "hold_time_max=2016h (84 days): extreme outliers distort p95 to 264h; system is NOT pure intraday despite multi-session entries — Stage 3 must test both intraday-exit and hold-to-signal-flip variants"
  - "broker=Fort Financial Services (obscure, non-Tier-1): confidence reduced 0.10 for vendor selection bias; account is Real but broker may have spread/slippage profile different from Pepperstone/IC Markets"
  - "track_record=6 months only (2020-12-15 to 2021-06-16): insufficient for multi-regime validation; blackout 2021-2026 means edge persistence unknown"
  - "drawdown=72.66% on real account with 1:500 leverage — excessive risk profile; gain=87.79% but absolute_gain=48.44% (difference suggests compounding from large DD periods)"
  - "direction signal is moderately weak: tree match_rate_cv=0.642, ripper=0.562; both are only marginally above always-sell baseline (0.534); Stage 3 reliability threshold should require Sharpe > 0.5 OOS before trusting"
  - "25 pairs with near-equal buy_pct across all (range 25%-68%) suggests direction rule is pair-agnostic; no pair-specific direction conditioning detected"
---

# Decoded signal — OLD Happy Neuron v1.0 (Aggressive Risk) (id 7603723)

## Family rationale

The system trades 25 FX pairs simultaneously with entries uniformly distributed across five daily time slots separated by approximately four hours each (00:05, 04:00, 12:00, 16:00, 20:00 UTC). This schedule-based multi-session entry pattern is the single strongest discriminator against all session-specific families in the taxonomy. LATE_NY_BREAKOUT requires concentration in the 21-01 UTC window — here 20:00 UTC alone accounts for 848 trades but 12:00 (725) and 16:00 (720) are nearly identical in volume, ruling out a session-concentrated system. LONDON_OPEN_MOMENTUM/MR requires clustering at 06-09 UTC, which is entirely absent. NY_SESSION_REVERSAL requires 12-16 UTC as the primary window — while 12:00 and 16:00 are prominent, 20:00 dominates and 00:05/04:00 add approximately 850 more trades that cannot be explained by a pure NY reversal. OVERNIGHT_GAP_FADE requires weekend timing, absent here. The missing hour slots (08:00 UTC) would complete a perfect 4-hour grid; the fingerprint shows hour=08 has lower volume, suggesting some session filter suppresses it.

The 25-pair universe (including exotic crosses CADCHF, CHFJPY, AUDNZD, NZDCHF) further distinguishes this from session-window families that typically focus on 4-8 USD/EUR majors. With 3,558 trades over approximately 6 months across 25 pairs, each pair averages approximately 142 trades — consistent with a scheduled, automated system entering all pairs at each clock trigger rather than selecting pairs opportunistically.

The direction logic is momentum-based across timeframes: `ret_10_H1` (10-period hourly return) dominates the tree with 0.66 importance weight, and all four top univariate rules independently confirm the same signal — `ret_10_H1 > -2.651e-05` predicts BUY with match_rate 0.634. This is consistent with the time-series momentum paradigm described in [algo_trading_chan, p.133, ch.6]: "Time series momentum — past returns of a single instrument are positively correlated with future returns." The system appears to ride short-to-medium term momentum on each pair independently, entering when the recent H1 trend is upward and exiting via a time-based or signal-reversal mechanism.

FACTOR_SCALPING is chosen over UNCATEGORIZED because: (1) the entry distribution and pair breadth match a factor-style systematic rule applied uniformly across many instruments, (2) the direction rule is empirically extractable from candidates.json with match_rate meaningfully above baseline (0.642 vs 0.534), and (3) the fixed micro-lot sizing (0.01 flat, p95/p50=1.00) rules out martingale amplification despite the k1 flag. Confidence is held at 0.52 rather than higher because the hold time distribution is extraordinarily wide (p50=5.54h, p95=264h, max=84 days) — a genuine scalper has p50 << 1h, suggesting this may be a medium-term momentum system with multi-session re-entry, which the FACTOR_SCALPING label does not fully capture. Alternatives considered and rejected: LATE_NY_BREAKOUT (hour concentration mismatch), NY_SESSION_REVERSAL (cannot explain 00:05/04:00 volume), MARTINGALE_GRID (lot ratio=1.00 contradicts, though k1 flag is a concern).

## Rule derivation

**Primary feature: `ret_10_H1`**
The tree (rank 1, match_rate_cv=0.642) assigns 66% of importance to `ret_10_H1`. The first split is at `ret_10_H1 <= -0.00` (zero crossing). When `ret_10_H1 > 0`, the tree consistently routes to BUY (class=1) across most sub-branches, unless `ret_3_H1 > 0` AND `ret_10_H1 > 0.01` simultaneously — suggesting a mean-reversion overlay for extreme momentum cases where the system avoids chasing. The univariate threshold from rank 4 gives the precise breakpoint: `ret_10_H1 > -2.651e-05`, which is near-zero and effectively means "10-bar H1 return is non-negative = BUY signal."

**Secondary feature: `ret_3_H1`**
Ranked second with 14% importance in the tree. Acts as momentum confirmation at a shorter horizon (3 bars H1 = 3 hours). The tree uses `ret_3_H1 <= 0.00` and `> 0.00` as a zero-crossing branching condition. The univariate rank-7 rule `ret_3_H4 > -9.83e-06` is for a different feature (`ret_3_H4`), not `ret_3_H1`, and is therefore NOT applied to the direction rule for `ret_3_H1`. I use only the tree's sign condition: `ret_3_H1 > 0.0`.

**Tertiary feature: `bb_pos_20_2_H1`**
Fourth in tree importance (0.04). The tree splits at `bb_pos_20_2_H1 <= -0.23` — values above -0.23 generate BUY when `ret_10_H1 > 0` and `ret_3_H1 <= 0`. This acts as a Bollinger Band floor filter: do not buy if price is more than 23% below the lower band (extremely oversold). Univariate rank 5 gives the standalone threshold: `bb_pos_20_2_H1 > 0.01547 => Buy` — a tighter entry-only threshold. I use the tree value (-0.23) in the direction rule because it comes from the multi-feature context where this feature acts as a guard against extreme oversold entries.

**RIPPER confirmation (rank 2, match_rate_cv=0.562)**
RIPPER adds two constraints that narrow the BUY universe: (1) `close_vs_session_open_M5 = 1.0` — current M5 close is above the session open price (intrabar momentum confirmation); (2) `ret_10_H1` in specific magnitude bands: 0.001-0.002, 0.002-0.0032, or 0.0032-0.0047. The RIPPER's lower match_rate (0.562 vs 0.642 tree) and specific magnitude bands suggest it is capturing only the "clean breakout" subset of BUY signals where momentum has a minimum speed. These thresholds are exact from candidates.json RIPPER ruleset and are preserved as an optional overlay in Stage 3.

**Exit logic**
All exits are `manual_or_time`. The bimodal hold distribution (p50=5.54h vs p95=264h) suggests two co-existing behaviors: (a) normal trades exit within 1-2 sessions on signal reversal when `ret_10_H1` crosses below zero, and (b) a fraction of trades are held for days or weeks without a stop, generating the 264h p95 and 2016h max. The 2016h (84-day) max hold is most likely an EA artifact (positions left open during platform downtime or deliberate hold-through) rather than a designed exit. The replicator should implement `max_holding_hours=264` as a hard cap matching the p95, and additionally test a signal-flip exit variant.

**Thresholds sourced directly from candidates.json — none invented:**
- `ret_10_H1 > -2.651e-05`: rank 4 univariate exact value
- `bb_pos_20_2_H1 > -0.23`: rank 1 tree exact split
- `bb_pos_20_2_H1 > 0.01547`: rank 5 univariate exact value
- `ret_3_H1 > 0.0`: tree zero-crossing sign condition
- RIPPER `ret_10_H1` bands: 0.001-0.002, 0.002-0.0032, 0.0032-0.0047 — exact from rank 2 RIPPER ruleset text

## Confidence breakdown

- Family identification: 0.53 — multi-session 4-hour schedule + 25-pair breadth strongly indicates a scheduled factor-style system, but FACTOR_SCALPING does not perfectly describe medium-term hold times; no better taxonomy family available
- Direction rule: 0.65 — `ret_10_H1` dominates with 0.66 MDI importance confirmed by three independent miners (tree, RIPPER, univariate) all agreeing on same feature and BUY direction; match_rate_cv=0.642 is above baseline (0.534) but the margin is modest
- Exit logic: 0.35 — manual_or_time exit with no TP/SL visible; 84-day max hold is anomalous and likely an artifact; replicator cannot reproduce exact exit behavior without additional EA source
- Overall: 0.52 = weighted mean (family 0.30 weight, direction 0.50 weight, exit 0.20 weight)

## Open questions (para Stage 3 + posteriores)

- **Hold time bimodality**: Stage 3 must test two exit variants: (a) signal-flip exit (close when `ret_10_H1` crosses below zero), and (b) max-time exit at 264h. The 2016h max hold should be excluded from the replicator design as an EA anomaly.
- **4-hour schedule confirmation**: Entry hour fingerprint (00, 04, 12, 16, 20 UTC) suggests a 4-hour fixed trigger. Stage 3 should test "enter at any hour when signal fires" vs "enter only at 00/04/08/12/16/20 UTC" to see which better replicates the observed 3,558 trade count distribution.
- **`close_vs_session_open_M5` availability**: Verify this feature exists in `features.parquet` before including it in the replicator direction rule. If absent, the RIPPER layer is dropped and only tree features (`ret_10_H1`, `ret_3_H1`, `bb_pos_20_2_H1`) are used.
- **Lot doubling within month**: The k1 flag (per-month max/median P95=5.10) requires investigation. Stage 3 should check whether flat 0.01 lots reproduce the same intra-month lot variance, or whether the EA adds partial positions on losers — a soft grid behavior that does not appear in the global p95/p50 ratio.
- **Pair selection breadth**: All 25 pairs have buy_pct ranging 25%-68%, suggesting pair-agnostic direction conditioning. Stage 3 should test top-10 pairs by volume vs all 25 to see if the lower-volume pairs (CADJPY=28, USDJPY=24) degrade or improve reliability.
- **Regime sensitivity**: The 6-month track record (Dec 2020 - Jun 2021) covers a specific post-COVID recovery regime. The H1 momentum signal may be regime-sensitive; Stage 3 must test on 2018-2019 data to estimate edge persistence beyond the observed window.
- **`ema_dist_20_H4 > 1.66` interpretation**: The tree splits at this value, which would imply price is 166% above the H4 EMA20 if the feature is in fractional units. Verify the scaling of `ema_dist_20_H4` in `features.parquet` — if the feature is in basis points or another unit, the tree threshold may be reasonable; if in fraction-of-price, this branch is effectively unreachable and can be ignored in the replicator.
