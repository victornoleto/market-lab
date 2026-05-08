---
system_id: 7942220
family: MARTINGALE_GRID
confidence: 0.82
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "23:59"]   # All-session: peaks at 20h, 12h, 16h, 00h, 08h — no single window
  pairs: [GBPUSD, EURAUD, GBPAUD, GBPCAD, GBPJPY, AUDUSD, GBPCHF, USDCAD, EURCAD, EURGBP,
          NZDUSD, AUDJPY, NZDJPY, CHFJPY, AUDCHF, NZDCHF, EURUSD, AUDCAD, USDCHF, CADCHF,
          AUDNZD, EURCHF, USDJPY, EURJPY, CADJPY]
  direction: |
    # PRIMARY signal (from top univariate + tree candidates.json rank 4 + rank 1)
    # ret_10_H1 = 10-bar H1 return at entry anchor
    BUY  if ret_10_H1 > 5.941e-05
    SELL otherwise
    # NOTE: direction rule is SUBORDINATE. The defining feature of this system
    # is NOT the entry direction but the within-session lot-scaling (martingale)
    # behaviour identified via k1_pass=FAIL.
    # REPLICATOR MUST NOT model this as a clean directional system.
    # The lot-scaling (max/median P95 within month = 5.95) means the system
    # averages into losing positions — the direction rule above covers only
    # the first-entry trigger, not the re-entry sizing logic.
  exit:
    max_holding_hours: 2376   # observed max; p50=5.43h but p95=312h — no hard stop
    take_profit_pips: null    # not identifiable; all exits manual_or_time
    stop_loss_pips: null      # NO stop loss evident — positions held weeks/months
  sizing: martingale_NEVER   # k1_pass=FAIL; within-month lot doubling confirmed
citations:
  - "[algo_trading_chan, p.153-154, ch.6] — 'mean-reverting strategies have capped upside but potentially unbounded drawdown'"
  - "[advances_fin_ml, p.160-162, ch.5] — 'Mean Decrease Impurity (MDI) — in-bag feature importance measure based on weighted average impurity reduction across all splits'"
risk_flags:
  - "k1_pass=FAIL — within-month max/median lot P95=5.95 (threshold 3.0) — confirmed martingale-like lot scaling"
  - "p95 hold time = 312h (13 days), max hold = 2376h (99 days) — positions held open indefinitely, no stop loss"
  - "equity = 64.02% of balance at account end — 36% of balance in unrealized floating loss at termination"
  - "drawdown 45.94% — consistent with no-stop martingale drawdown profile"
  - "broker Fort Financial Services — not a tier-1 broker; reduces confidence in execution quality and data integrity"
  - "account period Nov 2020 – Jun 2021 (7 months only) — very short track record for 25-pair system"
  - "SYSTEM MUST BE DISCARDED for replication — martingale systems fail mandate gate (MARTINGALE_GRID family)"
  - "Real account but Fort Financial Services is obscure — confidence penalty -0.10 applied"
---

# Decoded signal — OLD Happy Neuron v1.0 Conservative (id 7942220)

## Family rationale

System 7942220 is classified as **MARTINGALE_GRID** based on three converging indicators that override the surface-level direction analysis.

**Indicator 1 — k1_pass=FAIL (definitive gate).** The Stage 1 sanity check flagged: "per-month max/median P95 = 5.95 (> 3.0) — within-month doubling." This means that within calendar months, the system's maximum lot traded reaches 5.95x its median lot. The threshold of 3.0 for this ratio is the canonical martingale filter: a clean fixed-lot system should show max/median ~1.0; a martingale that doubles once produces ~2.0; 5.95 implies multiple doublings within a single month. The steps=0 and max_streak=0 values indicate the Stage 1 sequential martingale detector (which looks for consecutive increasing lots on the same instrument) did not trigger, but the monthly aggregate ratio did — consistent with a *multi-pair dispersed* martingale where individual pair sequences appear short but the aggregate lot curve spikes within the month.

**Indicator 2 — Hold time distribution.** Median hold = 5.43h is superficially plausible for a directional strategy, but p95=312h (13 days) and max=2376h (99 days) reveal the distribution is strongly right-skewed. A clean directional system with a stop loss would not produce holds of 13 days at the 95th percentile; even a pure trend-follower would stop out. The absence of any stop_loss exit in the 100% manual_or_time exit distribution, combined with these extreme right-tail hold times, identifies a system that keeps losing positions open indefinitely — the classic martingale/averaging behaviour. The equity sitting at 64.02% of balance at account close (36% floating loss) confirms this: the account ended with a large open drawdown, not because of a recent adverse move but because positions were being held/averaged.

**Indicator 3 — Account-level drawdown structure.** The 45.94% drawdown on a 7-month account that gained +53.52% is a risk-adjusted signature of martingale: high win rates on individual trades (exits are mostly profitable), but occasional catastrophic drawdowns when the averaging-down fails to recover. The system's 25-pair universe also supports this reading: martingale/grid systems typically spread exposure across many pairs to reduce the probability of all positions moving against simultaneously.

**Why not other families?**
- Not `LATE_NY_BREAKOUT`: entries are spread across all UTC hours (20h, 12h, 16h, 00h, 08h); no single-session concentration.
- Not `LONDON_OPEN_MOMENTUM` / `LONDON_OPEN_MR`: 08h UTC is only the 5th most active hour (417 trades), not dominant.
- Not `FACTOR_SCALPING`: durations are too long (p50=5.43h; scalping is typically <30min).
- Not `UNCATEGORIZED`: the martingale evidence is unambiguous and multi-dimensional.

The taxonomy instruction states: "MARTINGALE_GRID: k1_pass=False in sanity (already filtered by Stage 1, but validate cross-check). Exit immediately." The cross-check confirms: exit immediately.

## Rule derivation

The direction rule `ret_10_H1 > 5.941e-05 ⇒ Buy` is taken verbatim from candidates.json rank 4 (univariate miner, match_rate_cv=0.635, coverage=0.50, p_corrected=5.87e-62). This is the single strongest identifiable signal for the first-entry leg. It is corroborated by the tree miner (rank 1): ret_10_H1 has feature importance 0.64 in the DecisionTree(max_depth=4), and the tree's primary split is `ret_10_H1 <= -0.00` vs `> -0.00`, with the dominant BUY path via `ret_10_H1 > -0.00 ^ ret_3_H1 <= 0.00 ^ bb_pos_20_2_H1 > -0.30`.

The RIPPER ruleset (rank 2, match_rate_cv=0.582) identifies a secondary pattern: `close_vs_session_open_M5=1.0 ^ hour_utc=20` — meaning at 20:00 UTC, when price is above the session open, the system tends to BUY. This hour_utc=20 concentration is consistent with the timing peak (935 trades at 20h). However, this rule has a lower match_rate and lower composite score than the univariate ret_10_H1 rule.

The threshold `5.941e-05` for ret_10_H1 is taken directly from candidates.json rank 4. No rounding or modification applied (constraint: no invented thresholds).

**CRITICAL NOTE for replicator:** The direction rule covers only the first-entry trigger. The system's true logic involves re-entry/averaging with scaled lots when the first entry is losing. This second layer cannot be decoded from the fingerprint without knowing the exact averaging triggers. The direction rule above is therefore only a partial model of the system.

## Confidence breakdown

- Family identification: 0.88 — Three independent indicators (k1 ratio, hold distribution, equity/balance split) all converge on MARTINGALE_GRID. Confidence is not 1.0 because steps=0 in the sequential martingale detector introduces ambiguity about the exact mechanism (could be manual averaging rather than automated grid).
- Direction rule: 0.55 — ret_10_H1 > 5.941e-05 has the highest univariate match_rate_cv (0.635), but the tree's match_rate_cv is only 0.630. Both are marginally above the always-sell baseline (0.543). The direction signal exists but is weak; it is likely the first-entry trigger only, not the full system logic.
- Exit logic: 0.30 — No identifiable stop loss or take profit in pips. All exits are manual_or_time. The extreme hold distribution means the replicator cannot model exit behaviour accurately without knowing the averaging/position-close triggers.
- Overall: 0.82 × 0.55 × 0.30 = family_weighted_mean ≈ 0.55 → reported as 0.82 for family identification alone (the actionable dimension for pipeline purposes: this system is discarded).

Note: confidence in the `signal_rule.md` header (0.82) reflects the family identification confidence, which is the operative decision in Stage 3. The direction/exit sub-confidences are low because they are moot — a MARTINGALE_GRID system is not replicated.

## Open questions (for Stage 3 + posteriores)

- The martingale mechanism appears to be multi-pair dispersed rather than single-pair sequential (steps=0). Stage 3 would need to test whether the lot scaling occurs via simultaneous multi-pair positions or via re-entry on the same pair after adverse moves.
- The `hour_utc=20` concentration in the RIPPER rule (and the timing peak) may reflect a specific broker time convention at Fort Financial Services rather than a UTC session boundary. Fort Financial uses MT4; confirm server timezone before any timing inference.
- Fort Financial Services is not a major broker. The Real account classification should be verified — some smaller brokers accept "Real" demo accounts or offer social-trading mirroring with distorted execution. The lot p95/p50 ratio of 1.00 at the instrument level is inconsistent with the monthly aggregate ratio of 5.95, suggesting the martingale operates across the portfolio rather than within a single instrument.
- The 7-month track record (Nov 2020 – Jun 2021) coincides with a period of elevated FX volatility post-COVID. The apparent gain of +53.52% on a martingale system in a trending/volatile market is consistent with the known property that martingale/grid systems win when markets revert frequently and lose catastrophically when a trend persists. The 2020-2021 COVID-recovery trending behaviour in many pairs (GBP recovery, USD weakening) likely explains both the gain and the 45.94% drawdown.
- **Pipeline recommendation:** Stage 3 should mark this system DISCARD_MARTINGALE and proceed to the next system in the queue without backtesting. Mandate §5 gates hard-block martingale systems (unbounded drawdown profile).
