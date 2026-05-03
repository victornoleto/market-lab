---
system_id: 8397136
family: UNCATEGORIZED
confidence: 0.38
generated: 2026-05-02
rule:
  entry_window_utc: ["12:50", "13:15"]   # 13:00 UTC peak (254/432 trades at 13:00 sharp)
  pairs: [EURUSD, USDCHF]                # exact universe from fingerprint (216 each)
  direction: |
    # WARNING: all candidate match_rate_cv ≤ 0.583 vs baseline 0.523 — near-zero discriminative
    # power. Rule below is the best single candidate by match_rate*sqrt(coverage) but
    # its cross-validated accuracy barely exceeds the Always-Sell baseline.
    #
    # Best available composite (tree rank 3):
    BUY if hour_utc <= 12.50
    BUY if hour_utc > 12.50 AND ema_dist_20_H4 > -0.95 AND range_norm_M15 <= 0.84
    BUY if hour_utc > 12.50 AND ema_dist_20_H4 > -0.95 AND range_norm_M15 > 0.84 AND ret_3_H4 <= 0.0
    SELL if hour_utc > 12.50 AND ema_dist_20_H4 <= -0.95
    SELL if hour_utc > 12.50 AND ema_dist_20_H4 > -0.95 AND range_norm_M15 > 0.84 AND ret_3_H4 > 0.0
    NONE otherwise
    #
    # Alternative univariate (rank 6, match_rate_cv=0.572, coverage=0.60, p_corr=0.856):
    # BUY if bb_pos_20_2_H4 > -0.1559
    # (only partially Bonferroni-corrected; p_corr not < 0.05)
  exit:
    max_holding_hours: 744    # p95 hold = 744h; p50 = 36h — extremely wide, no tight time-exit
    take_profit_pips: null    # no TP evidence in fingerprint (exit_kind = manual_or_time only)
    stop_loss_pips: null      # no SL evidence
  sizing: proportional_equity_2pct   # lot fixed 0.01 throughout; p95/p50 ratio = 1.00 (no martingale)
citations:
  - "[advances_fin_ml, p.160-162] — 'Mean Decrease Accuracy (MDA) — out-of-bag feature importance measured by performance drop after column permutation; unbiased but slower' — hour_utc importance=0.53 in tree is the strongest feature signal, consistent with MDA/MDI ranking hierarchy"
  - "[evidence_based_ta, p.283-287] — 'Selecting the best rule without adjusting for data-mining bias — the observed performance of the best of N rules systematically overestimates expected performance' — all 10 candidates tested; p_value_corrected=1.0 for 7/10 univariates confirms no significant edge after Bonferroni correction"
risk_flags:
  - "direction signal indistinguishable from noise: top match_rate_cv=0.583 vs baseline=0.523; no candidate survives Bonferroni correction (p_corr < 0.05)"
  - "hold p50=36h and p95=744h are inconsistent with all intraday session families — system behaves more like a swing trader than a session scalper; family taxonomy does not cover this regime"
  - "broker Fort Financial Services — niche/low-tier broker; confidence penalty -0.10 applied"
  - "track record covers only 2020-12-22 to 2021-06-16 (~6 months); insufficient for walk-forward validation"
  - "RIPPER rank-1 rule fires on hour_utc < 10.1 (pre-London/Asian sessions) which CONTRADICTS the dominant timing peak at 13:00 UTC — internal contradiction between miners suggests multi-rule system or noisy signal"
  - "system name 'OLD Happy Algorithm PRO v1.4' confirms vendor-deprecated status; edge persistence unknown"
---

# Decoded signal — OLD Happy Algorithm PRO v1.4 - REAL SET2 (id 8397136)

## Family rationale

This system does not cleanly fit any of the eight defined families. The dominant entry timing
peak is 13:00 UTC (282 of 432 trades, 65.3%), with 254/432 trades firing at exactly 13:00:00
— a mechanical, clock-triggered entry consistent with an automated EA firing at the London/NY
overlap open. This timing would nominally suggest `OVERLAP_NY_LONDON_RANGE` (12-16 UTC) or
`NY_SESSION_REVERSAL`.

However, two key fingerprint signatures disqualify these families as high-confidence matches:

**1. Hold time distribution is incompatible with intraday session families.** The hold p50 is
36 hours and p95 is 744 hours (31 days), with a maximum of 1296 hours (54 days). Every named
session family (`LATE_NY_BREAKOUT`, `LONDON_OPEN_*`, `NY_SESSION_REVERSAL`,
`OVERLAP_NY_LONDON_RANGE`) expects exits within 1-8 hours. A p50 of 36h places most trades
fully outside the same trading session they entered. The exit_kind is 100% `manual_or_time`,
but the "time" component, if present, operates on a multi-day or multi-week scale — not the
intraday scale that defines these families.

**2. Direction signal has no actionable edge.** The baseline Always-Sell rule achieves
match_rate_cv = 0.523 (the natural imbalance: 52.3% of trades are SELL). The best univariate
rule (`ema_dist_20_H4 > 0.5305 → Buy`) reaches match_rate_cv = 0.583 at coverage 0.40 — a
lift of only +6pp over baseline, with p_value_corrected = 0.161 (not significant after
Bonferroni correction over 520 tests). As Aronson notes in Evidence-Based Technical Analysis
[p.283-287], selecting the best of N rules without correction systematically overstates
expected performance; here, all 10 candidates have p_corr = 1.0 or 0.856, meaning none
survive multiple-comparison adjustment. The direction component of this system cannot be
reliably decoded from the fingerprint data.

**3. RIPPER internal contradiction.** The top RIPPER rule fires on `hour_utc < 10.1` — before
the London open — as a BUY condition, directly contradicting the dominant 13:00 UTC peak in
the EDA. This inconsistency suggests either (a) the system runs multiple independent sub-rules
at different times, (b) the RIPPER rule is capturing a minority secondary pattern (the hour=9
and hour=10 bins show 71-87% BUY rates but represent only 30 trades total), or (c) the
RIPPER rule is overfit to noise given the high match_rate_std (0.172) across folds.

**Alternative families considered and rejected:**

- `OVERNIGHT_GAP_FADE`: entry at 13:00 UTC is incompatible; no weekend/Monday clustering.
- `FACTOR_SCALPING`: durations are far too long (p50=36h vs <30min requirement).
- `LATE_NY_BREAKOUT`: timing peak is 13:00, not 21-01 UTC.
- `LONDON_OPEN_MOMENTUM` / `LONDON_OPEN_MR`: timing peak 13:00 is post-London open by 6h.
- `MARTINGALE_GRID`: explicitly PASS on sanity check; lot ratio p95/p50 = 1.00.

Conclusion: `UNCATEGORIZED` with confidence 0.38. The system fires mechanically at NY-overlap
open (13:00 UTC) on EURUSD and USDCHF with no detectable directional signal above noise and
anomalously long holding periods. The most plausible interpretation is a discretionary-or-EWS
hybrid swing system that uses 13:00 UTC as an execution window but does not follow any of
the canonical session-edge families.

## Rule derivation

**Entry window**: Derived directly from fingerprint Top entry hour (UTC): 13:00 with 282 trades
(65.3% of all 432 trades). Sub-5min granularity confirms 254/432 at exactly 13:00. Window
set conservatively to 12:50-13:15 to capture the 13:00 canonical EA behavior.

**Pairs**: Directly from fingerprint — EURUSD 216 trades, USDCHF 216 trades. No other pair
present. EURUSD and USDCHF have a natural negative correlation (USD denominator vs numerator),
which is consistent with a dollar-index-directional system. The RIPPER rule's
`dollar_index_proxy=1.0` feature supports this: when the dollar is strong (proxy=1), the
prior H1 bar is down (-1), the system fires BUY before 10:00 UTC. This is a micro-fragment
of the system's logic but it has low generalization quality.

**Direction rule**: The decision tree (rank 3, match_rate_cv=0.511) is used as the primary
direction scaffold because it combines multiple features (hour_utc=0.53 importance,
ema_dist_20_H4=0.23, range_norm_M15=0.15, ret_3_H4=0.10) and its fold-accuracy range
(0.419-0.547) is more stable than RIPPER (0.233-0.756, std=0.172). The split at
`hour_utc <= 12.50 → BUY` captures the secondary pattern where trades before 12:30 UTC
are predominantly BUY-directed (hour=10 bin: 87.5% BUY, hour=9 bin: 71.4% BUY). After
12:30, the tree uses ema_dist_20_H4 and range_norm_M15 as secondary filters. Thresholds
used are verbatim from candidates.json:
- ema_dist_20_H4 split: -0.95 (from tree node `ema_dist_20_H4 <= -0.95`)
- range_norm_M15 split: 0.84 (from tree node `range_norm_M15 <= 0.84`, candidates.json
  also has univariate rank 5: `range_norm_M15 > 0.8184 → Sell` — tree value 0.84 is close)
- ret_3_H4 split: 0.0 (from tree node `ret_3_H4 <= -0.00`, i.e., sign of 3-bar H4 return)

No thresholds were invented. All values are taken from candidates.json or from the tree
structure in fingerprint.md.

**Exit**: No TP or SL signals in the fingerprint (exit_kind = 100% manual_or_time with no
price-barrier clusters). Max holding hours set to 744 (p95) as a safety cap. The replicator
should test both p50=36h and p95=744h as alternative max-hold parameters given the extreme
bimodality of the hold distribution.

**Sizing**: Fixed micro-lot (0.01) throughout — lot p95/p50 ratio = 1.00, confirming no
dynamic sizing or martingale. Set as proportional_equity_2pct for Stage 3 replicator as
a reasonable default for a $1,000 real account with 0.01 lots.

## Confidence breakdown

- Family identification: 0.35 — timing at 13:00 UTC is consistent with NY open but hold
  times and weak direction signal prevent confident taxonomy assignment; all five named
  alternatives ruled out on structural grounds
- Direction rule: 0.30 — no candidate survives Bonferroni correction; tree match_rate_cv
  0.511 barely exceeds random (0.500); RIPPER has fold variance so high (std=0.172) that
  any single fold result is unreliable per [advances_fin_ml, p.160-162] MDA principles
- Exit logic: 0.45 — entry at 13:00 UTC is firm; exit timing is ambiguous (p50=36h,
  p95=744h suggest swing behavior, not session-close)
- Overall: 0.38 = weighted mean (direction penalized most heavily as core of strategy edge)

## Open questions (para Stage 3 + posteriores)

- **Hold time bimodality**: the hold distribution (p50=36h, p95=744h, max=1296h) suggests
  two populations of trades — quick closes and very long holds. Stage 3 should separate these
  and test whether they have distinct entry conditions or represent winning vs losing trades.

- **Dollar-index proxy**: the RIPPER rule uses `dollar_index_proxy` as a feature. Stage 3
  should verify this feature exists in the features.parquet schema and test whether
  EURUSD/USDCHF entries are systematically directionally opposed (EURUSD SELL = USDCHF BUY
  on same timestamp), which would confirm a DXY-direction-based system.

- **Secondary timing clusters**: hour=9 (14 trades, 71.4% BUY) and hour=10 (16 trades,
  87.5% BUY) suggest a second entry mode in the London session. Stage 3 should test whether
  splitting by hour (pre-12:30 vs 13:00) captures two distinct sub-strategies.

- **bb_pos_20_2_H4 threshold**: rank 6 univariate (`bb_pos_20_2_H4 > -0.1559 → Buy`,
  match_rate_cv=0.572, p_corr=0.856) is the best single Bonferroni-adjusted candidate.
  While not significant at p<0.05, it is the least data-mined signal. Stage 3 should test
  it as a standalone direction filter for the 13:00 UTC window only.

- **ema_dist_20_H4 regime**: rank 10 univariate (`ema_dist_20_H4 > 0.5305 → Buy`,
  match_rate_cv=0.583) has p_corr=0.161, just outside significance. Stage 3 should test
  whether this threshold is stable across the 6-month sample window or is a regime artifact
  of the 2021 low-volatility FX environment.

- **Broker tier**: Fort Financial Services is a niche FSA-registered Seychelles broker with
  no major-tier regulation. Track record may reflect favorable execution conditions not
  replicable on Pepperstone Razor. Stage 3 cost model should use 1.2 pip spread for EURUSD
  and 1.8 pip for USDCHF (conservative Pepperstone standard spread vs 0.01 lot) to stress-test
  whether the ~9.65% gain over 6 months survives realistic costs.
