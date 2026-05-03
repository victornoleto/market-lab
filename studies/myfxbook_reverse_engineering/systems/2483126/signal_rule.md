---
system_id: 2483126
family: UNCATEGORIZED
confidence: 0.22
generated: 2026-05-02
rule:
  entry_window_utc: ["12:00", "20:00"]   # NY+London overlap; flat peak 12-19 UTC, no narrow spike
  pairs: [EURJPY, AUDUSD, USDJPY, NZDUSD, EURUSD]
  direction: |
    # WARNING: no stable direction rule found. All univariate candidates
    # at coverage=0.80 produce match_rate_cv ≤ 0.556, barely above the
    # Always-Buy baseline of 0.560. Direction appears to be predominantly
    # long-biased across all pairs (buy_pct 50-58%).
    #
    # Best non-baseline candidate (rank 2):
    BUY if ret_1_M5 > -0.0002731
    # This fires on 80% of trades (coverage 0.80) and produces match_rate 0.555.
    # Because match_rate < baseline (0.560), this rule is WORSE than always-Buy.
    # No rule from any miner produces match_rate_cv > baseline; direction signal
    # cannot be decoded from available features. Placeholder below:
    BUY if ret_1_M5 > -0.0002731
    SELL otherwise
    # Stage 3 MUST test: always-Buy as the direction null; skip direction search.
  exit:
    max_holding_hours: 6192    # p99/max observed; p50=48h, p95=1800h (75 days)
    take_profit_pips: null     # no TP/SL barrier detected; all exits manual_or_time
    stop_loss_pips: null
  sizing: fixed_lot_0.02       # lot p50/p95/p99/max = 0.02/0.02/0.02/0.02 — no variation
citations:
  - "[math_money_mgmt, p.13] — 'Never use money management to salvage a system with negative mathematical expectation. Money management only amplifies what is already there — positive or negative.'"
  - "[advances_fin_ml, p.159] — 'Backtesting is not a research tool. Feature importance is.' (Marcos First Law) — top feature atr_ratio_H4=0.21 in tree (rank 7) does not produce stable direction; MDA/MDI signal is absent."
  - "[algo_trading_chan, p.5] — 'make the model as simple as possible, with as few parameters as possible' — no candidate beats the trivial always-Buy baseline, suggesting no extractable rule exists."
risk_flags:
  - "MARTINGALE_GRID NAME FLAG: system name is 'OLD Happy MartiGrid v1.9.1' — vendor explicitly labels this a MartiGrid. Stage 1 lot-check passes (p95/p50=1.00) only because lot size is fixed at 0.02 across all 1910 trades. Grid mechanics may manifest as position accumulation (multiple open trades at different price levels) rather than lot doubling — Stage 1 k1 test does not catch position-count grids."
  - "EQUITY UNDERWATER: equity=48.66% of balance at account close (equity $5,927 vs balance $12,182). Consistent with a grid system holding large unrealized losses at termination."
  - "EXTREME HOLDING TIME DISPERSION: hold p50=48h, p95=1800h (75 days), max=6192h (258 days). A strategy that holds some trades for 8+ months cannot be classified as intraday or session-based. This is inconsistent with all well-defined taxonomy families except MARTINGALE_GRID."
  - "NO DIRECTION EDGE: best direction rule match_rate_cv=0.556 < Always-Buy baseline 0.560. All candidates are either below or statistically indistinguishable from the unconditional long bias. No extractable signal exists."
  - "HIGH DRAWDOWN: 62.97% maximum drawdown, consistent with grid/martingale accumulation of losing positions."
  - "OBSCURE BROKER: Fort Financial Services — not a tier-1 regulated broker. Confidence penalty -0.10 applied."
  - "BLACKOUT 2021-2026: account stopped updating 2021-06-16. Edge persistence unknown. Vendor labeled 'OLD'."
  - "FAMILIES CONSIDERED AND REJECTED: (1) NY_SESSION_REVERSAL — hours 12-19 UTC match but exit is not time-based 1-3h (p50=48h), no reversal signal found; (2) OVERLAP_NY_LONDON_RANGE — hours partially overlap but holding times incompatible; (3) FACTOR_SCALPING — durations >> 30min (median 48h), not a scalper; (4) LATE_NY_BREAKOUT — peak hours 17-19 UTC not 21-01 UTC; (5) LONDON_OPEN_MOMENTUM/MR — peak hours are afternoon NY not London open."
---

# Decoded signal — OLD Happy MartiGrid v1.9.1 Multipairs (id 2483126)

## Family rationale

This system cannot be reliably assigned to any taxonomy family with confidence >= 0.5.
The primary reason is a combination of four disqualifying signals that, taken together,
point to a MARTINGALE_GRID archetype but cannot be confirmed with the available data:

**1. System name contains "MartiGrid."** The vendor (HappyForex) explicitly labels this
system "MartiGrid." In the HappyForex product line, this naming convention refers to a
combined martingale + grid strategy — a system that opens multiple trades at staggered
price levels (grid) and may scale position count or lot size (martingale) as price moves
against the open positions. The Stage 1 lot-check (k1_pass=True, p95/p50=1.00) does not
refute this: it tests whether individual trade lot sizes are doubled, which a pure grid
with fixed per-order sizing would pass even while accumulating grid layers.

**2. Equity deeply underwater at account close.** The account ended with equity of $5,927
against a balance of $12,182 — 48.66% of balance. This means approximately $6,255 in
open unrealized losses were being carried at the final snapshot. Grid systems characteristically
accumulate large unrealized floating drawdowns from positions opened at adverse price levels
and never exited via stop-loss. The 62.97% maximum drawdown recorded by MyFxBook is
consistent with this mechanics.

**3. Extreme holding time dispersion.** The hold-time distribution (p50=48h, p95=1800h,
max=6192h) is not consistent with any intraday or session-based family. A p50 of 2 days
with a maximum of 258 days indicates that a subset of positions are held for months — the
hallmark of a grid system waiting for price to return to entry level. In contrast, all
well-defined families in the taxonomy (LATE_NY_BREAKOUT, LONDON_OPEN_*, NY_SESSION_REVERSAL,
FACTOR_SCALPING) require exit within hours. Even OVERNIGHT_GAP_FADE closes within 1-2
trading days.

**4. No extractable direction edge.** All 10 candidates produce match_rate_cv <= 0.556.
The Always-Buy baseline yields 0.560, which means no mined rule beats the trivial
directional prior. This is consistent with a grid system whose direction signal is
effectively "open in the direction of the current grid layer" — a function of unrealized
P&L state that is not represented in the Stage 1 feature matrix (which captures price
momentum and volatility, not portfolio state). As noted in `advances_fin_ml` [p.159]:
"Feature importance is the research tool" — and here, every feature's importance collapses
to zero when compared against the unconditional long-bias baseline.

The MARTINGALE_GRID family was considered as the classification, but the mandate
instructions state "k1_pass=False in sanity (already filtered by Stage 1) — exit
immediately." Since Stage 1 returned k1_pass=True (lot-level martingale not detected),
the system was not pre-filtered. However, the convergent evidence above (name, equity
underwater, holding time dispersion, high DD) all point to grid mechanics. The
appropriate action is UNCATEGORIZED with full risk flags, rather than assigning a
family whose signal logic cannot be replicated.

For the avoidance of doubt: alternatives considered were NY_SESSION_REVERSAL (entry
hours 12-19 UTC partially match, but exit times are incompatible and no reversal rule
found), OVERLAP_NY_LONDON_RANGE (similar hour argument, same exit incompatibility),
and FACTOR_SCALPING (durations are orders of magnitude too long). All were rejected.

## Rule derivation

No stable rule was derived because no candidate from any miner beats the baseline:

- **Rank 1 (baseline):** Always-Buy, match_rate_cv=0.560. This is the unconditional
  long bias of the trade universe (56% Buy trades). Any rule that does worse than this
  is adding noise.

- **Rank 2 (univariate):** `ret_1_M5 > -0.0002731 => Buy`, match_rate_cv=0.555,
  coverage=0.80, p_corr=0.00037. This is statistically significant (corrected p < 0.05)
  but economically useless: it fires on 80% of trades and produces a lower match rate
  than always buying. The threshold -0.0002731 is taken directly from candidates.json
  and is NOT invented.

- **Rank 7 (tree):** DecisionTree with top features atr_ratio_H4=0.21 (H4 ATR ratio),
  range_norm_M15=0.15, ret_3_H4=0.15. CV accuracy 0.466 with std=0.120 across 5 folds
  (fold range: 0.27 to 0.59). This high variance (std 0.12 on a 0-1 scale) indicates
  the tree is fitting noise — not a stable rule. Per `advances_fin_ml` [p.161-162], MDA
  drops to chance when features are permuted; here the OOS folds already show near-chance
  performance.

- **Rank 8 (RIPPER):** `atr_ratio_H4 <= 1.46 AND ema_dist_20_H4 <= -2.62 => Buy`.
  CV accuracy 0.451 with std=0.146 (fold range: 0.31 to 0.70). Worse than baseline,
  extreme variance. The threshold values (1.46 for atr_ratio_H4; -2.62 for ema_dist_20_H4)
  are taken directly from candidates.json.

The entry_window_utc ["12:00", "20:00"] is derived from the fingerprint's top entry
hours: 18:00 (160 trades), 19:00 (152), 17:00 (138), 16:00 (107), 12:00 (104). This
covers the NY session and NY-London overlap — but represents a broad, flat distribution
rather than a meaningful entry spike. No 5-minute-level concentration is visible in
the fingerprint.

The sizing rule is `fixed_lot_0.02` because candidates.json and fingerprint confirm:
lot p50/p95/p99/max = 0.02/0.02/0.02/0.02, ratio=1.00. This is the most certain
element of the decoded rule. However, in a grid system, the number of simultaneously
open lots (position-count) may vary even when per-trade lot size is fixed — a dimension
not captured in the Stage 1 lot-check.

## Confidence breakdown

- Family identification: 0.20 — UNCATEGORIZED; no family fits. MARTINGALE_GRID suspected
  but k1_pass=True prevents formal assignment. Evidence is convergent (name + DD + hold
  times + underwater equity) but no family can be assigned with mechanical certainty.

- Direction rule: 0.15 — no rule beats always-Buy baseline. Direction is effectively
  undecoded. The placeholder rule (ret_1_M5 > -0.0002731) performs worse than baseline
  and should NOT be trusted by Stage 3.

- Exit logic: 0.30 — exit is confirmed as manual_or_time (100% of 1910 trades). The
  range (48h to 6192h) is real but impractical for replication. Stage 3 cannot reproduce
  this without knowing the grid layer close logic.

- Overall: 0.22 = weighted mean, floored by the complete absence of a decodable direction
  signal and the grid-mechanics suspicion.

## Open questions (for Stage 3 + posteriores)

- **Grid layer count vs. lot size**: Stage 1 k1_pass tests lot-doubling per trade. It
  does NOT test whether multiple trades are open simultaneously at different price levels
  (a grid). Stage 3 should check if position-count increases when price moves against
  existing positions — this would confirm MARTINGALE_GRID.

- **Always-Buy as null hypothesis**: Since direction is undecoded and match_rate < baseline,
  Stage 3 should test whether an always-Buy strategy on the 5-pair universe with the
  observed entry hour distribution (12-19 UTC) replicates the reported +192% gain.
  If it does, the direction signal is noise and the gain came from persistent FX long
  drift + leverage, not from a decodable alpha signal.

- **Unrealized loss accounting**: The equity/balance gap ($6,255 unrealized loss at close)
  suggests the system ended with a large open drawdown. Stage 3 should model whether
  the +192% gain reported is purely on closed trades, and what the all-in P&L (including
  open positions at close) looks like.

- **Threshold stability for atr_ratio_H4**: The tree assigns importance 0.21 to
  atr_ratio_H4 and uses thresholds 1.51 (tree, rank 7) and 1.46 (RIPPER, rank 8).
  These two miners agree on the feature but disagree on the threshold by 3.4%. Stage 3
  could test both as a robustness check — but given the low overall match_rate, this
  is low priority.

- **Broker data quality**: Fort Financial Services is not a major regulated broker.
  Spread and execution data used in Stage 1 feature extraction may not reflect real
  trading costs accurately. Stage 3 cost model should stress-test at 2-4x the assumed
  spread.

- **Recommendation**: This system should be assigned LOW PRIORITY in the Stage 3
  replication queue. The combination of undecoded direction, suspected grid mechanics,
  63% drawdown, and equity underwater at close make reliable replication and comparison
  with the HMH v2.3.1 benchmark highly unlikely. If Stage 3 resources are limited,
  skip this system.
