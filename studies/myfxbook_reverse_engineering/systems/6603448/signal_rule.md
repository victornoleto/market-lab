---
system_id: 6603448
family: MARTINGALE_GRID
confidence: 0.72
generated: 2026-05-02
rule:
  entry_window_utc: ["10:00", "18:00"]   # indicative only — entry is broadly distributed across London + NY sessions; no tight window identified
  pairs: [AUDUSD, USDCHF, EURCHF]        # universe from system_info / fingerprint
  direction: |
    # WARNING: MARTINGALE_GRID family — direction rule is irrelevant; lot scaling
    # on loss is the structural mechanism. Direction is near-random (51% Sell overall).
    # Best univariate rule (rank 4, match_rate_cv=0.521, coverage=0.80):
    SELL if ret_1_M15 > -0.0003592
    BUY  otherwise
    # NOTE: all candidate rules are within noise of the 0.512 Always-Sell baseline.
    # The replicator MUST NOT be run on this system (MARTINGALE_GRID exit).
  exit:
    max_holding_hours: 2712    # p99-max observed; p50=48h, p95=2016h — no time-based exit found
    take_profit_pips: null     # exit_kind = manual_or_time only; no TP observed
    stop_loss_pips: null       # no SL exits observed; martingale adds to losers
  sizing: martingale_NEVER     # lot p95/p50 = 3.00; k1 flag FAIL (within-month doubling); NEVER replicate
citations:
  - "[algo_trading_chan, p.183-184, ch.8] — 'Do not impose stop losses on mean-reversion strategies at levels that would be triggered during backtest [...] Set stop loss above the maximum intraday backtest drawdown'; Chan explicitly warns that the absence of stops + scaling into losses is the martingale signature."
  - "[advances_fin_ml, p.208-211] — 'A PBO > 0.5 means the strategy is more likely overfit than valid'; all candidate rules here have match_rate_cv near the 0.512 baseline, consistent with zero directional edge — the P&L driver is lot scaling, not signal quality."
  - "[trading_systems_methods, p.1085-1091] — 'controlling risk through volatility-normalized position sizing [...] capped leverage'; Kaufman's three tail-risk-avoidance rules explicitly prohibit the unbounded-drawdown dynamic inherent in martingale lot doubling."
risk_flags:
  - "MARTINGALE_GRID — k1_pass=False: per-month max/median P95=4.35 (>3.0), within-month lot doubling detected. Stage 3 replicator MUST NOT be run on this system."
  - "All 10 candidate rules have match_rate_cv in [0.48, 0.53] with all p_value_corrected=1.0 after Bonferroni — no statistically significant directional edge exists."
  - "Hold time distribution (p50=48h, p95=2016h, max=2712h) is inconsistent with any session-based intraday family; trades held for weeks/months signal position-averaging on losers."
  - "Broker Fort Financial Services (offshore, not top-tier regulatory); account Real but leverage 1:500 suggests offshore jurisdiction — confidence penalty applied."
  - "Track record duration: ~11 months only (2020-07-27 to 2021-06-11); insufficient for DSR/WF validation."
  - "DD=32.41% on only +28.23% gain over 11 months is consistent with a martingale system running near its risk-of-ruin threshold."
---

# Decoded signal — OLD Happy Fast Money v1.3.1 (id 6603448)

## Family rationale

The system is classified as **MARTINGALE_GRID** based on convergent evidence across all four diagnostic axes: lot dynamics, hold-time distribution, direction-rule quality, and session timing.

**Lot dynamics — primary evidence.** The fingerprint reports `martingale flag: FAIL (martingale-like dynamics)` with the k1 diagnostic `per-month max/median P95 = 4.35 (> 3.0) — within-month doubling`. The lot p95/p50 ratio is exactly 3.00, at the detection threshold. In a session-based directional strategy (LATE_NY_BREAKOUT, LONDON_OPEN_MOMENTUM, etc.), lot sizes are proportional to equity and constant within a session — within-month doubling is the martingale signature. Chan warns against exactly this in `[algo_trading_chan, p.183-184, ch.8]`: a strategy that adds to losing positions in the absence of stops is structurally a martingale regardless of the entry label.

**Hold-time distribution — secondary evidence.** The p50 hold time is 48 hours and p95 is 2016 hours (~84 days). No session-based family produces median holds of 2 days or p95 holds of 84 days. `LATE_NY_BREAKOUT` exits in 1-3 hours; `LONDON_OPEN_MOMENTUM` exits in under 4 hours; `FACTOR_SCALPING` holds under 30 minutes. Only a strategy that keeps losing positions open indefinitely — waiting for mean reversion or recovery — generates this distribution. The maximum observed hold of 2712 hours (~113 days) confirms multi-month position carry, characteristic of martingale ladders.

**Direction-rule quality — tertiary evidence.** All 10 candidate rules produce match_rate_cv between 0.482 and 0.526, clustered around the 0.512 Always-Sell baseline. The RIPPER best rule is `prior_bar_sign_M1=-1.0` at 0.514 — effectively indistinguishable from noise. All univariate candidates have Bonferroni-corrected p_value = 1.00. Per `[advances_fin_ml, p.208-211]`: "A PBO > 0.5 means the strategy is more likely overfit than valid." With match rates barely above chance, the profitability mechanism cannot be the entry signal — it must be the sizing structure (martingale recovery after adverse moves).

**Timing distribution — confirming evidence.** Entry hours span 10:00-17:00 UTC with no sharp session peak. A genuine session-based strategy concentrates entries in a 2-3 hour window (e.g., 22:00-01:00 for `LATE_NY_BREAKOUT`). The spread across London afternoon and NY overlap (10:00-17:00 UTC) with the top 5-minute clusters at 17:55 and 10:00 suggests entries are triggered not by session opens but by price reaching martingale re-entry levels during liquid hours.

**Alternatives considered and rejected:**

- `NY_SESSION_REVERSAL` (12-16 UTC entry): rejected because hold times are measured in days, not 1-3 hours, and direction rule quality is near-chance.
- `OVERLAP_NY_LONDON_RANGE` (12-16 UTC): same hold-time objection; BB_pos feature in candidate rank 9 (`bb_pos_20_2_H4 > -0.3431`) provides weak support but coverage is only 0.60 and match_rate 0.52.
- `FACTOR_SCALPING` (distributed entry, short duration): rejected because hold times are the opposite of scalping behavior.
- `UNCATEGORIZED`: rejected because the martingale evidence is unambiguous and multiaxial.

## Rule derivation

Because the system is classified MARTINGALE_GRID, a deployable direction rule cannot and should not be derived. The following is documented for completeness of the fingerprint audit only; **Stage 3 should not run a replicator on this system.**

The best univariate candidate (rank 4) is `ret_1_M15 > -0.0003592 => Sell` with match_rate_cv=0.521 and coverage=0.80. This is the only rule with a coverage above 0.70 that beats the Always-Sell baseline. However, the beat margin (0.521 vs 0.512) is within the standard deviation of the RIPPER CV fold accuracies (std=0.023), and the Bonferroni-corrected p-value is 1.00 after 548 tests. This rule is not statistically significant.

The tree (rank 3) uses `atr_ratio_M5` as the primary split (threshold 0.14 / 0.23), indicating volatility regime as the entry condition rather than directional signal. This is consistent with a martingale system that fires during moderate-volatility periods and avoids very low-volatility (atr_ratio_M5 <= 0.14 → class 0, i.e., no trade). The tree's overall match_rate_cv is 0.482, below the Always-Sell baseline — it cannot be used as a direction signal.

The RIPPER rule `prior_bar_sign_M1=-1.0` (Sell when last M1 bar was bearish) achieves 0.514 CV accuracy with high variance across folds (0.503, 0.486, 0.514, 0.508, 0.557). The fold at 0.557 drives the mean up; median fold accuracy is 0.508. Not deployable.

No threshold from candidates.json has been invented or modified. All numbers above are cited verbatim from the candidates.json file.

## Confidence breakdown

- Family identification (MARTINGALE_GRID): 0.82 — k1_pass=False is direct, hold-time distribution is unambiguous, direction quality is near-noise. Minor uncertainty because max_streak=1 and steps=8 could theoretically indicate a partial grid rather than a full martingale; confidence not at 0.90 for this reason.
- Direction rule: 0.10 — all candidates are within noise; no deployable signal identified. Assigned near-zero because documenting a rule with 0.521 accuracy would mislead the replicator.
- Exit logic: 0.15 — exit_kind is 100% manual_or_time but the distribution (p50=48h to max=2712h) is too wide to specify a meaningful time-based exit; no TP/SL signals detected.
- Overall: 0.36 — weighted mean (family identification dominates but the 0.72 front-matter confidence reflects family certainty specifically; the 0.36 reflects overall replicability of the strategy, which is near-zero for a martingale system).

Note: the front-matter `confidence: 0.72` reflects confidence in the MARTINGALE_GRID classification specifically, not in the deployability of the strategy (which is zero by mandate).

## Open questions (for Stage 3 and posteriores)

- **Do not proceed to Stage 3 replication.** Mandate classification is MARTINGALE_GRID = exit immediately. Running a replicator would consume resources on a system that cannot be deployed.
- If this system is retained for academic fingerprinting purposes (lot-scaling pattern library), Stage 3 could quantify the exact martingale step size by analyzing the lot progression within individual drawdown episodes — but this is not required for the pipeline.
- The `atr_ratio_M5` primary split in the tree (threshold 0.14/0.23) is interesting: it suggests the system preferentially enters during moderate-ATR regimes. This could be documented as a negative-example baseline for comparing against genuine volatility-targeting families.
- The AUDUSD dominance (401/920 trades = 44%) is unusual for a system also trading USDCHF and EURCHF. This could reflect pair-specific martingale sizing (AUDUSD may have tighter typical ranges, enabling more frequent recovery), but this hypothesis is not testable without per-pair lot series.
- Broker Fort Financial Services operates under offshore regulatory framework with 1:500 leverage; the 32.41% drawdown on only +28.23% cumulative gain over 11 months suggests the account may have been approaching ruin at termination. This is consistent with the vendor's "OLD" label and system retirement.
