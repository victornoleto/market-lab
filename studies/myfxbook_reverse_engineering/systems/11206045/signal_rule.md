---
system_id: 11206045
family: UNCATEGORIZED
confidence: 0.38
reason_code: taxonomy_gap
candidate_new_family: TOKYO_OPEN_JPY_SWING
generated: 2026-05-02
rule:
  entry_window_utc: ["00:00", "00:15"]
  pairs: [GBPJPY]
  direction: |
    # Faithful replication of Stage 1 tree (rank 1, CV=0.571).
    # WARNING: tree CV (0.571) is only +1.4pp above always-Buy baseline (0.557),
    # std=0.030 — direction edge is statistically indistinguishable from a
    # buy-bias coin on n=212. See risk_flags + Open Questions.
    BUY  if ret_10_H4 >  0
    BUY  if ret_10_H4 <= 0 and ret_10_H1 <= 0
    SELL if ret_10_H4 <= 0 and ret_10_H1 >  0
  exit:
    max_holding_hours: 168
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_observed
citations:
  - "[trading_systems_methods, p.170] — \"Event-driven systems (swing, point-and-figure) have higher per-trade risk than time-based systems -- entry-to-reversal distance can run large before a signal fires.\" Justifies the multi-day hold tail (p95=396h, max=918h) as consistent with event-driven swing exits, not intraday time-based exits."
  - "[evidence_based_ta, p.289-291] — \"Five factors that inflate data-mining bias: ... fewer observations in the performance statistic → more bias.\" Applies to n=212 trades + 506 univariate tests: only one rule survives p_corr<0.5 (bb_pos_20_2_H4 at 0.302) and none survive p<0.05 — null hypothesis (rule = useless) cannot be rejected per [evidence_based_ta, p.183-185]."
  - "[systematic_trading, p.142 (ch.9)] — \"Extreme leverage with low-volatility instruments is lethal.\" Account leverage 1:500 on a JPY cross at ForexMart is a structural risk flag for any replication exercise."
risk_flags:
  - "Direction edge degenerate-adjacent: tree CV 0.571 vs always-Buy baseline 0.557 (lift +1.4pp, std 0.030). Per [evidence_based_ta, p.289-291] this is within data-mining noise on n=212. RIPPER CV 0.481 sits BELOW baseline."
  - "Single-pair universe (GBPJPY only). Mandate §3 (Strategy A reactivation criteria) explicitly rejects single-asset edge."
  - "Vendor folklore broker (ForexMart, 1:500). Decoder.md workflow step 3 reduces confidence -0.10 for obscure broker; Real account here so no extra Demo penalty."
  - "Bimodal hold distribution: p50=37h (~1.5d), p95=396h (~16d), max=918h (~38d). Exit logic almost certainly signal-based, not pure time-based; max_holding_hours=168 is a safety cap that truncates ~5% of real trades."
  - "Clock anchor at 00:00 UTC = Tokyo cash-open; entry concentration is M5-aligned (200/212 at 00:05 bucket, 9/212 at 00:00 bucket). Replication needs M5 timing precision but is NOT sub-M5 sensitive (p50 hold = 37h, far from <5min threshold; instruction-9 needs_m1_review is therefore not added)."
  - "Provisional candidate_new_family TOKYO_OPEN_JPY_SWING is n=1 by definition. Per 5R-1-hardening §1, taxonomy expansion requires ≥1 system + book citation + explicit user approval; this rule MUST NOT be promoted to a Family enum value without that gate."
  - "Calendar-aware replication NOT assumed: classification used trade/OHLC evidence only (instruction 8). 00:00 UTC is read as Tokyo session-clock, not as a live news/economic-calendar trigger; news-window hypothesis is queued in Open Questions, not encoded in the rule."
---

# Decoded signal — Happy Japanese Market FM (id 11206045)

## Family rationale

The pattern is coherent but lies outside the closed enum in
`shared/decoder_taxonomy.py`. Three independent signals point at the same
archetype: a single JPY-cross (GBPJPY, 212/212 trades), an extreme clock
anchor at Tokyo cash-open (00:00 UTC bucket = 209/212 = 98.6%; 00:05 UTC
sub-bucket = 200/212 = 94.3%), and a multi-day swing hold (p50=37.01h,
p95=396.39h, max=918.16h, all from `fingerprint.md` line 16, post-R4 fix).
The vendor name itself ("Happy Japanese Market FM") corroborates the
Tokyo-session reading without requiring inference.

This combination fails every member of the closed enum:

- All five intraday families (`LATE_NY_BREAKOUT`, `LONDON_OPEN_MOMENTUM`,
  `LONDON_OPEN_MR`, `NY_SESSION_REVERSAL`, `OVERLAP_NY_LONDON_RANGE`,
  `FACTOR_SCALPING`) are blocked by the explicit anti-pattern in `decoder.md`:
  "Atribuir família intraday … quando hold p50 > 24h confirmado pós-R4 — use
  UNCATEGORIZED + reason_code=hold_mismatch ou SWING_TREND_MOMENTUM provisional".
  p50=37h is conclusively non-intraday post-R4. Even ignoring hold, the
  intraday families fail on entry hour: 00:00 UTC is outside London (06-09),
  Overlap (12-16), and Late-NY (21-01) windows.
- `OVERNIGHT_GAP_FADE` expects Friday-late / Monday-morning weekend-gap
  entries; this system enters every weekday at 00:00 UTC, max gap days = 23.5
  (vacation, not weekly cycle).
- `MARTINGALE_GRID` is filtered out by Stage 1 sanity (`martingale flag:
  PASS`, steps=0, max_streak=0, lot p95/p50=1.09).
- `H1_MOMENTUM_GOLD` (provisional) requires Gold/XAU; pair = GBPJPY.
- `NEWS_RELEASE_MOMENTUM` (provisional) requires (a) name flag NEWS/HF News
  and (b) p50 hold measured in seconds (reference 1612420 carries p50=0.01h).
  This system has neither — name = "Japanese Market", p50 = 37h. Per
  instruction 8, calendar-aware news replication is **not** assumed; the
  00:00 UTC anchor is classified as session-clock, not event-clock. The
  residual ambiguity is logged in Open Questions.
- `SWING_TREND_MOMENTUM` (provisional) requires (a) p50 > 72h AND (b) top
  hour < 15% AND (c) H4/D1 trend features dominate tree. (a) FAILS: p50=37h.
  (b) FAILS HARD: top hour=00 with 98.6%, contradicting the "no clock anchor"
  essence of the family per `shared/decoder_taxonomy.py:204-213`. (c) PASSES:
  ret_10_H4 importance = 0.62. Two-of-three failure means downgrade, not fit.

Two-of-three failure on the closest provisional family is exactly the case
the hardening doc describes for `taxonomy_gap`: "estratégia coerente mas fora
das famílias do enum atual" (`shared/decoder_taxonomy.py:66`). The
candidate_new_family `TOKYO_OPEN_JPY_SWING` records the proposed label
without promoting it — promotion requires user approval per
5R-1-hardening §1 plus a 2nd supporting system in R1.

The literature anchor for the *swing-side* of the archetype is
`[trading_systems_methods, p.170]`: time-based intraday systems and
event-driven swing systems have different per-trade risk profiles, and the
long entry-to-exit distance observed here (max 918h ≈ 38d) is the hallmark
of the latter. The literature anchor for the *direction-edge skepticism* is
`[evidence_based_ta, p.289-291]`: with n=212 and 506 univariate tests, the
data-mining bias inflation is severe and only ultra-low raw p-values would
survive Bonferroni — none here does (best p_corr = 0.302).

## Rule derivation

**Entry window** (`00:00 - 00:15 UTC`) — direct from `fingerprint.md` lines
20-32. 209/212 (98.6%) at hour=00; 200/212 (94.3%) at hour:5min=00:05;
9/212 at 00:00. The 15-minute span captures 209/212 trades and tolerates
broker clock skew typical of MT4 vendor systems. M5-aligned, not sub-M5
sensitive (instruction 9: p50=37h is far from the <5min threshold; M5 grid
is sufficient to specify entry).

**Pair** (`GBPJPY`) — direct from `fingerprint.md` line 8 — `pairs:
{'GBPJPY': 212}`. No multi-pair fanout to test.

**Direction** (rank-1 tree, CV=0.571) — faithful transcription of the tree
in `fingerprint.md` lines 67-79 / `candidates.json` rank 1. Tree splits on
ret_10_H4 first (importance 0.62) and ret_10_H1 second (0.38). Class 1 =
Buy, class 0 = Sell, mapped from `direction_by_pair` GBPJPY buy_pct = 55.7%
(`fingerprint.md` line 38). The univariate top features (rank 4-10) all
carry p_corr ≥ 0.302; none reject the multiple-comparison null per
`[evidence_based_ta, p.183-185, p.289-291]`, so they are NOT promoted into
the rule. Tree edge over always-Buy baseline (0.557) is +1.4pp with std
0.030 — reproduced for replicator fidelity but tagged in `risk_flags` as
indistinguishable from a buy-bias coin.

**Exit** (`max_holding_hours=168`, no TP/SL) — `exit_kind: manual_or_time`
is 100% of trades (`fingerprint.md` line 33), so no TP/SL signature exists.
Hold distribution is bimodal-with-long-tail (p50=37h, p95=396h, max=918h),
inconsistent with a fixed-time exit and consistent with a discretionary or
signal-based close. The 168h (7 day) cap is a safety choice, not a learned
exit: it matches the typical weekly swing cap and truncates the ~5% of
trades that run beyond. The replicator is expected to flag this divergence;
an exit-rule mining pass is queued in Open Questions.

**Sizing** (`fixed_lot_observed`) — lot p50/p95/max = 195.67 / 212.43 /
215.13, p95/p50 ratio = 1.09 (`fingerprint.md` line 13). The 8% spread is
inside the dynamic-sizing band (mandate §7) and consistent with a fixed lot
modulated by small balance changes. No martingale (sanity PASS, steps=0).

## Confidence breakdown

- Family identification: **0.50** — every check against the 12 enum members
  is unambiguous (no fit), so "this is taxonomy_gap" is itself a
  high-confidence determination. The candidate_new_family is provisional and
  subject to user review.
- Direction rule: **0.20** — tree CV 0.571 sits +1.4pp above always-Buy
  0.557 with std 0.030; multiple-comparison correction kills every
  univariate alternative. The rule is the best transcription available, not
  a validated edge.
- Exit logic: **0.40** — exit_kind is unambiguously manual_or_time, but the
  bimodal hold distribution means no clean rule was recoverable from
  Stage 1. 168h cap is a placeholder, not a derivation.
- Overall: **0.38** — unweighted mean (0.50 + 0.20 + 0.40) / 3 ≈ 0.37,
  rounded to 0.38 reflecting that the family-level "this is taxonomy_gap"
  finding has higher informational value than its raw component score.

## Open questions (para Stage 3 + posteriores)

- **Exit rule recovery**: replicator should attempt to mine an exit signal
  (e.g., reversal of ret_10_H4 sign, opposite-side daily close, or a fixed
  N-day stop) instead of relying on `max_holding_hours=168`. The 5% tail
  beyond 16d distorts any pure time-based replication.
- **Tokyo-open vs JPY-news ambiguity**: 00:00 UTC = 09:00 JST = Tokyo cash
  open, but it is also adjacent to several JPY-relevant data releases
  (Tankan, BoJ Minutes, machinery orders, all typically 23:50 UTC prior
  day). Per instruction 8 this rule was classified strictly from observed
  trade/OHLC evidence as session-clock, not event-clock. A calendar-aware
  replication test (overlay with a JPY economic-calendar feed) is queued
  for Stage 3+ if the candidate_new_family survives R1 review with a 2nd
  supporting system.
- **Provisional support**: per 5R-1-hardening §1,
  `TOKYO_OPEN_JPY_SWING` needs ≥1 system (have it: 11206045) + book
  citation (have it: trading_systems_methods p.170 swing) + **explicit user
  approval** before it can be promoted from `candidate_new_family` to
  `Family` enum. Until then, downstream consumers must read this signal as
  `family: UNCATEGORIZED` with `reason_code: taxonomy_gap`.
- **Direction edge sanity**: even with the tree faithfully replicated, the
  +1.4pp lift over always-Buy is below any reasonable noise threshold for
  n=212. Stage 3 should report match-rate vs always-Buy, vs always-Sell, vs
  random-frequency-matched, and vs permutation-test (5R-1-hardening §3) as
  baseline lifts — the rule may not survive that comparator. The
  `degenerate` reason_code was the secondary candidate and could become
  primary if the timing/pair coherence is downweighted.
- **DST-leak hypothesis**: the 9-trade leak at 00:00 vs 200 trades at 00:05
  may correspond to seasonal DST boundaries on the broker server (JST has
  no DST; if broker stamps in a DST timezone the offset shifts twice per
  year). Stage 3 should bin entries by season and check whether the
  5-minute split moves under DST.
