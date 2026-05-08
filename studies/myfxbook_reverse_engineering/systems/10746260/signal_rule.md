---
system_id: 10746260
family: MARTINGALE_GRID
confidence: 0.97
generated: 2026-05-02
rule:
  entry_window_utc: ["15:00", "17:30"]   # empirical peak from fingerprint — NOT a tradeable window
  pairs: [GBPUSD, USDJPY, EURUSD, AUDUSD]
  direction: |
    # BLOCKED — MARTINGALE_GRID family. No direction rule is produced.
    # Lot scaling with p95/p50 ratio = 121.36 and per-month k1 = 128.08 makes
    # any directional edge analysis meaningless: the system's PnL profile is
    # dominated by lot-ladder dynamics, not price prediction.
    NONE  # replicator must not execute this system
  exit:
    max_holding_hours: null   # hold_p50/p95/max all NaN in fingerprint — holding times not recoverable
    take_profit_pips: null
    stop_loss_pips: null
  sizing: martingale_NEVER
citations:
  - "[leverage_space, p.161, eq.7.03] — 'z < −0.5 → Martingale effect (bet more as equity falls)'"
  - "[math_money_mgmt, p.13] — 'Attempting to use money management on a system with negative expectation. No position sizing technique converts a losing strategy into a winner.'"
risk_flags:
  - "HARD DISCARD — martingale_flag=FAIL, lot p95/p50 ratio=121.36, k1 per-month max/median=128.08 (threshold > 3.0)"
  - "Broker Ultima Markets — obscure/folclore-known, confidence further reduced by -0.10 (already FAIL so moot)"
  - "Holding times all NaN — Stage 1 could not reconstruct hold durations, data integrity concern"
  - "System name 'Happy News' + timing peaks at 15:00/17:30 UTC suggest news-event straddle + lot-doubling on loss"
  - "account_type=Real but gain +1174.99% on $1k balance is consistent with extreme lot-ladder amplification, not edge"
---

# Decoded signal — Happy News - UM (id 10746260)

## Family rationale

This system is classified as **MARTINGALE_GRID** and is immediately discarded per the taxonomy rule ("exit immediately"). The classification is unambiguous and does not require literature-based session analysis.

The primary evidence for martingale classification comes from the sanity block of the fingerprint: the lot size distribution shows a p50 of 1.25 lots and a p95 of 151.43 lots, yielding a p95/p50 ratio of **121.36**. The Stage 1 k1 checker flags "per-month max/median P95 = 128.08 (> 3.0) — within-month doubling." A ratio of 121 between median and 95th-percentile lot sizes is not explainable by proportional equity-based sizing — it is diagnostic of a within-sequence doubling ladder. The `martingale_flag` is explicitly marked `FAIL` in `fingerprint.md`.

The system name "Happy News - UM" provides a narrative hypothesis: entries at 15:00-17:30 UTC correspond to major US economic data releases (non-farm payrolls, FOMC minutes, CPI, retail sales — standard Reuters/Bloomberg release windows). The strategy appears to open positions on news spikes and, when price moves adversely, doubles lot size on the recovery. This is a classic news-straddle-plus-martingale approach, widely documented in the vendor community. However, regardless of the entry mechanism, the lot-scaling regime renders it MARTINGALE_GRID by taxonomy.

For completeness: the timing evidence (15:00 UTC = 345 trades, 17:00 UTC = 151 trades; fingerprint rank 1 tree uses `hour_utc` as 4th-ranked feature at importance 0.09) does not map to any clean session open family in the taxonomy. The 15:00-17:30 UTC window overlaps with NY afternoon session but not with any of the clean breakout or MR families (LATE_NY_BREAKOUT requires 21-01 UTC; LONDON_OPEN families require 06-09 UTC; OVERLAP_NY_LONDON_RANGE requires 12-16 UTC). Even if the martingale flag were absent, the timing fingerprint would land in UNCATEGORIZED — but this distinction is moot given the FAIL flag.

The alternatives formally considered and rejected are:
- `NY_SESSION_REVERSAL` (12-16 UTC entry, opposite London move): entry peak at 15:00 barely overlaps, but direction_by_pair shows no systematic opposite-to-London bias (buy_pct ~50% for all pairs), and the martingale flag overrides.
- `FACTOR_SCALPING` (distributed entries, sub-30min): entries are highly clustered at specific clock times (15:30 = 308 trades), not distributed, and duration data is unavailable.
- `UNCATEGORIZED`: would apply if martingale flag were False, given the ambiguous 15:00 peak and unclear direction signal.

## Rule derivation

No directional rule is derived. The top candidate from Stage 1 is the decision tree (rank 1, match_rate_cv = 0.604, std = 0.084) with primary split on `bb_pos_20_2_M15 > 0.07`. The RIPPER ruleset (rank 2, match_rate_cv = 0.545) uses `close_vs_session_open_H4 = 1.0` and `hour_utc = 15.0-17.0` as conditions. The univariate top candidate (rank 4) is `ema_dist_20_M15 > 0.02487` with match_rate_cv = 0.662 at 50% coverage.

All of these match_rate_cv values are at best 0.66 on a subset, and the tree has a fold_accs range of [0.488, 0.701] — high variance indicating that the apparent directional signal is likely an artifact of the lot-weighting in label construction (trades with large martingale lots dominate the label signal). In a martingale system, the direction of the large-lot trades that eventually close profitably is correlated with prior-bar momentum by construction (the system keeps doubling until price reverses), which produces spurious feature importance. The `bb_pos_20_2_M15` feature at importance 0.52 in the tree likely captures this: when price is near the middle of the Bollinger Band (bb_pos ~ 0), the system has accumulated unrealized positions across the ladder; when price rises above the band center (bb_pos > 0.07), the ladder closes. This is a P&L artifact, not a directional edge.

The direction_by_pair data confirms no edge: all pairs show buy_pct between 45.9% and 52.4%, statistically indistinguishable from 50%.

Specific candidates not carried forward:
- Rank 1 tree: match_rate_cv = 0.604, std = 0.084 — high variance, MARTINGALE_GRID overrides.
- Rank 2 RIPPER: match_rate_cv = 0.545, std = 0.037 — near baseline (0.502), MARTINGALE_GRID overrides.
- Rank 4 univariate `ema_dist_20_M15 > 0.02487`: match_rate_cv = 0.662 at 50% coverage — coverage too low for reliable rule; MARTINGALE_GRID overrides.

## Confidence breakdown

- Family identification (MARTINGALE_GRID): 0.97 — lot p95/p50 = 121.36, k1 = 128.08, explicit FAIL flag in Stage 1 sanity. The only source of residual uncertainty (0.03) is that Stage 1 does not report step count or max_streak (both show 0 in fingerprint — possible data limitation), though the lot ratio alone is conclusive.
- Direction rule: N/A — rule not produced for MARTINGALE_GRID family.
- Exit logic: N/A — holding times are all NaN; not recoverable.
- Overall: 0.97 = family identification only (other dimensions are vacuous).

Confidence adjustments applied:
- Broker = Ultima Markets (obscure): -0.10 would apply if borderline, but confidence already high from lot-ratio evidence. Net effect: none on final score.
- Account type = Real: no reduction.

## Open questions (for Stage 3 + posteriores)

- Stage 3 replicator should receive a `SKIP` instruction for this system_id — no backtest is warranted.
- The news-event timing hypothesis (15:00-17:30 UTC US data release window) could be investigated independently in a clean (non-martingale) framework: if a news-straddle strategy without lot-doubling were built on the same pairs and entry window, would it pass gates? This is a separate research question not implied by this system's track record.
- Hold durations being fully NaN is unusual and may indicate that Stage 1's hold-time calculation failed on this dataset (possible if open/close pairing was ambiguous due to partial closes in the martingale ladder). Stage 3 infra should flag this as a data quality warning.
- The broker Ultima Markets should be added to a watch-list of obscure/folclore brokers: their permissive lot-scaling policies (leverage 1:500) enable extreme martingale amplification, artificially inflating gain% metrics on MyFxBook (recorded: +1,174.99% on $1k balance with $7,500 withdrawn — consistent with a ladder that ran successfully until it was wound down).
