---
system_id: 2123808
family: UNCATEGORIZED
confidence: 0.38
generated: 2026-05-02
rule:
  entry_window_utc: ["13:00", "18:00"]   # NY session entry cluster; no tight sub-hour peak
  pairs: [USDCAD, AUDCHF, AUDCAD, CADCHF, AUDUSD]
  direction: |
    # Primary signal: H4 10-bar momentum fade (from univariate rank 8, p_corrected=0.0004)
    SELL if ret_10_H4 > 0.004779
    # Secondary: Bollinger Band position (from tree rank 1, top features)
    SELL if ret_10_H4 > -0.01 AND bb_pos_20_2_H4 > 0.90 AND atr_ratio_M1 > 0.09
    BUY  if ret_10_H4 <= -0.01
    # Fallback (no strong BUY rule confirmed by corrected p-value)
    NONE otherwise
  exit:
    max_holding_hours: 336    # p50 hold = 168h; p95 = 1896h; use 2×p50 as soft cap
    take_profit_pips: null    # no TP/SL detected; exit kind = manual_or_time only
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[algo_trading_chan, p.153-154, ch.6] — mean-reverting strategies have capped upside but potentially unbounded drawdown, while momentum strategies have limited downside"
  - "[advances_fin_ml, p.160-162, ch.5] — Mean Decrease Accuracy (MDA): out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower"
  - "[algo_trading_chan, p.47, ch.2] — Set the lookback for moving average and standard deviation in a mean-reversion strategy to a small multiple of the half-life of mean reversion"
risk_flags:
  - "UNCATEGORIZED: no taxonomy family fits cleanly — swing multi-day mean-reversion on AUD/CAD commodity bloc does not match any session-based intraday family"
  - "broker Fort Financial Services — obscure/non-tier-1; possible slippage model mismatch in replicator; reduce confidence by 0.10 applied"
  - "hold p50=168h (7 days), p95=1896h (79 days) — replicator must use daily bar backtesting, not hourly"
  - "match_rate_cv of top candidate = 0.556 (tree) and 0.583 (univariate ret_10_H4, coverage 30%) — weak directional signal; high probability of no real edge"
  - "all p_corrected values for directional rules either NaN or > 0.05 except rank 8 (ret_10_H4 > 0.004779, p_corrected=0.000372); single significant rule with only 30% coverage"
  - "date range 2017-05-16 to 2021-06-15 — includes COVID 2020 vol regime; edge persistence to present unknown"
  - "equity/balance discrepancy at end: equity 88.22% of balance ($37,970 vs $43,041) — open floating loss at close of record; drawdown 32.31% is unusually large for a REAL account"
---

# Decoded signal — OLD Happy Way v1.2 - REAL (id 2123808)

## Family rationale

No taxonomy family from the standard set fits this system cleanly. The top entry hours
are 17:00 (101 trades), 15:00 (70), 16:00 (66), 13:00 (42) UTC — a broad NY session
window, not the tight 21-01 cluster required for LATE_NY_BREAKOUT, and not the 06-09
cluster required for any London family. The critical disqualifier for all session-based
intraday families is the hold time: p50=168 hours (7 days) and p95=1896 hours (79 days).
Every intraday family in the taxonomy (LATE_NY_BREAKOUT, LONDON_OPEN_MOMENTUM,
LONDON_OPEN_MR, NY_SESSION_REVERSAL, OVERLAP_NY_LONDON_RANGE) presupposes exits within
hours, not days or weeks.

NY_SESSION_REVERSAL (12-16 UTC entry, exit 1-3h, sign opposite to London move) was the
closest intraday candidate given the entry timing, but the multi-week hold instantly
disqualifies it. FACTOR_SCALPING requires durations under 30 minutes — this system's
median hold is over 7 days. OVERNIGHT_GAP_FADE would require Friday/Monday clustering,
which is not observed. MARTINGALE_GRID is explicitly ruled out (lot p95/p50=1.00, no
martingale steps).

The system is most accurately classified as a multi-day swing mean-reversion strategy on
AUD/CAD commodity FX pairs, with entries triggered during NY session hours. The pair
universe (USDCAD, AUDCHF, AUDCAD, CADCHF, AUDUSD) represents exclusively the commodity
currency bloc (AUD = Australian dollar, CAD = Canadian dollar), which is known for
sensitivity to commodity price cycles. Chan [algo_trading_chan, p.153-154, ch.6] describes
mean-reverting strategies as having "capped upside but potentially unbounded drawdown" —
consistent with this system's 32.31% maximum drawdown on a live REAL account.

The assignment of UNCATEGORIZED is deliberate and not a lazy default. The alternatives
considered were: (1) NY_SESSION_REVERSAL — rejected on hold duration; (2)
OVERLAP_NY_LONDON_RANGE — rejected on hold duration and pair universe (no EUR/GBP/CHF
with EUR base); (3) inventing a new "SWING_MR_COMMODITY_FX" family — rejected because
the mandate requires using defined taxonomy only and marking unknown cases as UNCATEGORIZED.

## Rule derivation

The direction rule is built from two sources in candidates.json:

**Rank 8 (univariate, statistically validated):** `ret_10_H4 > 0.004779 => Sell`
- match_rate_cv = 0.583, coverage = 0.30, p_corrected = 0.000372
- This is the only candidate that survives Bonferroni-style correction across 544 tests
  (p_corrected < 0.05). It says: when the 10-bar H4 return (approximately 40 trading hours
  or ~5 sessions of momentum) is positive and above 0.48%, fade it — go short.
- This is a classical momentum fade / mean-reversion signal operating at the H4 timeframe.
  The 10 H4 bars correspond to roughly 40 hours of elapsed time (2 trading days), consistent
  with the ADF half-life concept from Chan [algo_trading_chan, p.47, ch.2]: "Set the lookback
  for moving average and standard deviation in a mean-reversion strategy to a small multiple
  of the half-life of mean reversion."
- Coverage is only 30%: the signal fires on fewer than 1 in 3 trades. For the 70% not
  covered, no corrected-p-significant rule exists.

**Rank 1 (tree, max_depth=4):** Top features ret_10_H4=0.27, bb_pos_20_2_H4=0.22,
  bb_pos_20_2_M15=0.18, bb_pos_20_2_M5=0.13, atr_ratio_M5=0.12
- The tree uses bb_pos_20_2_H4 (Bollinger Band position on H4 with 20-period, 2-sigma bands)
  as the secondary split. When ret_10_H4 > -0.01 AND bb_pos_20_2_H4 > 0.90 (price near or
  above upper band), the terminal split on atr_ratio_M1 determines direction: if atr_ratio_M1
  > 0.09, class = 0 (Sell). This is a classic "overbought on BB" fade filter.
- However, the tree's fold_accs range from 0.503 to 0.649 with std=0.053 — high variance,
  consistent with noise rather than a stable signal. López de Prado [advances_fin_ml,
  p.160-162, ch.5] notes that MDA feature importance, being out-of-bag, provides an
  unbiased importance ranking — the tree top features (ret_10_H4, bb_pos_20_2_H4) should
  be taken as the most informative pair, not as a reliable standalone rule.

**Rank 3 (univariate):** `dow > 0 => Buy` — match_rate_cv=0.550, p_corrected=0.991.
  Despite a raw p-value of 0.0018, after correction across 544 tests this does NOT survive.
  Excluded from the rule.

**Rank 5 (RIPPER):** `ret_10_H4 <= -0.014 AND ret_1_M15 <= -0.0007 => Sell (class 1)`
  — match_rate_cv = 0.485 (below baseline 0.542). This underperforms the naive Always-Buy
  baseline. Excluded.

The BUY rule is the complement of the primary SELL signal. When ret_10_H4 <= -0.01, the
tree consistently predicts class 1 (Buy) regardless of the BB_pos_H4 sub-branch (both
branches in that subtree → class 1). This is coherent: fade the downside move too.

The direction rule captures ~30-40% of trades with marginal statistical backing (only one
candidate passes corrected significance), and defaults to NONE for the uncovered cases.
Stage 3 should evaluate both versions: (a) only the significant ret_10_H4 rule; (b) the
full tree rule. The replicator should NOT treat NONE as a hold signal — it means no trade.

## Confidence breakdown

- Family identification: 0.65 — the system clearly does NOT fit any intraday session family
  due to multi-day holds; UNCATEGORIZED is the only honest assignment. The uncertainty (not
  1.0) reflects the possibility that the "real" system uses a session filter we cannot observe
  from the trade history alone.
- Direction rule: 0.35 — only one candidate (rank 8) survives multiple-comparison correction,
  and its coverage is 30%. The tree (rank 1) has high fold-accuracy variance (std=0.053).
  The RIPPER rule underperforms baseline. The directional signal is weak.
- Exit logic: 0.20 — all exits are "manual_or_time" with no TP/SL detected. The p50 hold
  of 168h and p95 of 1896h suggest the system operator uses discretionary or EA-managed
  exits; we cannot reconstruct this rule from the trade log alone.
- Overall: 0.38 = weighted mean (family 0.30 weight, direction 0.40 weight, exit 0.30 weight)

## Open questions (for Stage 3 + posteriores)

- **Hold time model**: replicator must decide between (a) fixed max_holding_hours=336 (2×p50),
  (b) volatility-adaptive hold (ATR multiple), (c) mean-reversion exit when bb_pos crosses
  zero. The current fingerprint gives no clue; Stage 3 should test all three.
- **Commodity factor overlay**: AUD and CAD are commodity currencies correlated with iron ore,
  oil, and gold prices. A commodity momentum or carry filter (e.g., CRB index direction)
  might gate entries. This is not in candidates.json but would explain the multi-week holds.
- **BUY rule robustness**: the BUY signal (ret_10_H4 <= -0.01) comes from the tree complement,
  not from a statistically validated univariate rule. Stage 3 should test BUY-only, SELL-only,
  and symmetric strategies separately.
- **Fort Financial Services slippage**: this is a non-tier-1 broker. The replicator should
  model 2-3 pip slippage on entry/exit and test sensitivity to spread assumptions.
- **Regime break at 2021**: the track record ends 2021-06-15 with open floating loss of ~12%
  of balance. If the system was still running trades at that date, the true performance may
  be worse than the +44.79% headline gain. Stage 3 should be aware of truncation bias.
- **Direction by pair heterogeneity**: AUDCHF has 58.6% buy rate, CADCHF only 49.6%, USDCAD
  52.3%. The system may use pair-specific direction logic that the pooled feature matrix
  cannot recover. Stage 3 should evaluate per-pair models separately.
- **bb_pos_20_2_H4 > 0.90 threshold**: this is the tree split point from rank 1 candidate.
  Stage 3 should test sensitivity: does the edge survive at 0.80 or 1.00? If the threshold
  is a backtest artifact, it will not be robust across regimes.
