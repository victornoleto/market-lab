---
system_id: 10970107
family: MARTINGALE_GRID
confidence: 0.95
generated: 2026-05-02
rule:
  entry_window_utc: ["15:00", "17:00"]   # NY session / London close overlap
  pairs: [USDJPY, GBPUSD, EURUSD, AUDUSD]
  direction: |
    # MARTINGALE_GRID: direction logic is NOT the edge source.
    # Lot sizing escalates geometrically within losing streaks (lot p95/p50 = 121.97).
    # The nominal direction signal from tree miner (for record only — do NOT replicate):
    BUY if ema_dist_20_H1 > -0.39 AND ret_1_H1 <= -0.00
    BUY if ema_dist_20_H1 > -0.39 AND bb_pos_20_2_M5 <= -0.33
    BUY if ema_dist_20_H1 > -0.39 AND ema_dist_20_M15 > 1.30
    SELL otherwise
    # WARNING: replication of this rule WITHOUT reproducing the lot-doubling ladder
    # will yield near-zero edge (direction rule match_rate_cv ~= 0.649; baseline = 0.502).
  exit:
    max_holding_hours: null   # hold times all NaN in fingerprint — no OHLC at close
    take_profit_pips: null
    stop_loss_pips: null      # no SL visible — typical of pure martingale (no stops)
  sizing: martingale_NEVER   # lot p95/p50 = 121.97; within-month max/median P95 = 127.98
citations:
  - "[math_money_mgmt, p.13] — 'Mathematical expectation is the amount you expect to make or lose, on average, each bet ... No position sizing technique converts a losing strategy into a winner.'"
  - "[advances_fin_ml, p.160-161] — 'Mean Decrease Impurity (MDI) — in-bag feature importance measure ... biased toward high-cardinality features'; top tree feature ema_dist_20_H1=0.48 reflects MDI bias, not causal edge."
  - "[leverage_space, p.161, eq.7.03] — 'z < -0.5 → Martingale effect (bet more as equity falls)'; lot p95/p50 ratio 121.97 is consistent with z- << -0.5 migration function."
risk_flags:
  - "MARTINGALE_GRID confirmed: lot p95/p50 = 121.97 (>>3.0 threshold); k1 flag 'within-month doubling'; Stage 3 replication BLOCKED per pipeline rules."
  - "Broker DecodeFX: small/folklorically obscure broker — reduce confidence by 0.10 (applied)."
  - "System name 'Happy News' implies fundamental/news-event entries at 15:00-17:00 UTC (US macro releases); this is schedule-driven timing, not a purely technical signal."
  - "Hold times are NaN/absent in fingerprint — no close timestamps available, so exit logic cannot be validated."
  - "Gain +8,462% from $1,000 starting balance is consistent with martingale survivorship: one account that did not blow up yet; distribution of outcomes is catastrophically left-skewed."
  - "Real account confirmed but single account; no ensemble of accounts to estimate ruin probability."
---

# Decoded signal — Happy News - DecodeFx (id 10970107)

## Family rationale

The system is classified as `MARTINGALE_GRID` based on three independent lines of evidence
that converge unambiguously.

**Line 1 — Lot size dispersion (primary, decisive).** The fingerprint reports lot p50 = 1.28
and lot p95 = 156.33, yielding p95/p50 = 121.97. The Stage 1 sanity module explicitly flags
`k1_pass = FAIL` with the annotation "per-month max/median P95 = 127.98 (> 3.0) — within-month
doubling." A ratio above 3.0 is the pipeline threshold for martingale detection; a ratio of 121.97
exceeds it by a factor of 40. This is not leverage variation — lot size variation of this magnitude
is the defining signature of a geometric lot-doubling ladder.

The `leverage_space` book by Vince formalizes this mathematically: at Martingale exponent z < -0.5,
the sizing function `f$_{k,i}` in eq.7.03 grows as equity falls, meaning bets increase after losses
[leverage_space, p.161, eq.7.03]. A lot p95/p50 ratio of 121.97 corresponds to a highly negative
z exponent (deep into the martingale regime), consistent with a system that opens progressively
larger positions after each losing trade until a recovery trade closes the whole stack.

**Line 2 — Direction statistics (confirmatory).** The direction-by-pair table shows BUY% between
44.6% (USDJPY) and 60.3% (AUDUSD) — close to 50/50 for all pairs. The direction-by-hour table
at the peak hour (15:00) shows BUY% = 51.4%, essentially coin-flip. In a martingale system,
direction of individual trades is largely irrelevant: the system recovers through lot escalation,
not through directional accuracy. A near-50/50 split is precisely what one expects when direction
is chosen by a low-signal rule and the system relies on lot-doubling to manufacture account gains.
The tree miner's match_rate_cv = 0.649 is only marginally above baseline (0.502), and the RIPPER
match_rate_cv drops to 0.562, barely above baseline. These low margins confirm that directional
alpha is minimal.

**Line 3 — Account performance fingerprint.** +8,462% gain from a $1,000 account over approximately
two years, with a reported maximum drawdown of only 11.23% — this equity curve profile is the
canonical martingale survivor. The combination of extreme gain and low drawdown is only achievable
under martingale sizing when the account has not yet drawn its ruinous losing streak. The Vince
framework explains this precisely: at aggressive martingale exponents, short-term TWR can be
spectacular, but the probability of ruin at any future horizon approaches 1 as trading continues
[math_money_mgmt, p.13: "No position sizing technique converts a losing strategy into a winner"].

**Why not NY_SESSION_REVERSAL or OVERLAP_NY_LONDON_RANGE?** The 15:00-17:00 UTC timing peak
is consistent with those families. The RIPPER rule explicitly encodes `hour_utc=15.8-17.0`,
and the system name "Happy News" strongly suggests US macro news releases (15:30 UTC = US economic
data, 17:00 UTC = US oil inventory / Fed speakers). However, timing and direction patterns become
secondary once martingale lot-doubling is confirmed. The family assigned must be `MARTINGALE_GRID`
because the sizing mechanism dominates the edge decomposition entirely. Classifying it as a
direction-based family while ignoring the lot ladder would be methodologically incorrect — the
replicator would diverge from the real account regardless of how well direction rules are tuned.

## Rule derivation

The direction thresholds below come directly from candidates.json rank-1 tree output without
modification. They are recorded here for audit completeness, NOT because they represent a
replicable edge independent of the lot-doubling ladder.

**Tree (rank 1, match_rate_cv = 0.649, coverage = 1.00):**
- Primary split: `ema_dist_20_H1 <= -0.39` (importance 0.48 in tree)
- Within `ema_dist_20_H1 > -0.39`: BUY dominant unless `ema_dist_20_M15 <= 1.30` AND
  `ret_1_H1 > -0.00` (i.e., positive H1 return with moderate M15 EMA position → SELL)
- The tree uses thresholds: `ema_dist_20_H1 = -0.39`, `ret_3_M15 = 0.00`,
  `ema_dist_20_H1 = -1.15`, `range_norm_H4 = 1.52`, `bb_pos_20_2_M15 = -0.24`,
  `bb_pos_20_2_M5 = -0.33`, `ret_10_M15 = -0.00`, `ema_dist_20_M15 = 1.30`,
  `ret_1_H1 = -0.00`, `bb_pos_20_2_M15 = 0.73`

**RIPPER (rank 2, match_rate_cv = 0.562, coverage = 1.00):**
- Rule 1 (BUY): `close_vs_session_open_H4=1.0 AND prior_bar_sign_H1=-1.0 AND
  is_first_min_of_hour=1 AND dollar_index_proxy=1.0 AND hour_utc=15.8-17.0`
- Rule 2 (BUY): `close_vs_session_open_H4=1.0 AND ema_dist_20_M15 > 1.6`
- Rule 4 (BUY): `prior_bar_sign_H4=1.0 AND hour_utc=10.0-15.0 AND close_vs_session_open_M1=-1.0`
- The RIPPER explicitly confirms the 15:00-17:00 UTC entry window and the dollar index proxy
  as a condition — consistent with US news event timing.

**Univariate top features (rank 6-8, all with coverage ~0.50 and BUY direction):**
- `ema_dist_20_H1 > -0.02232` → Buy (match_rate_cv = 0.654)
- `ret_10_H1 > -0.000106` → Buy (match_rate_cv = 0.651)
- `bb_pos_20_2_H1 > -0.02139` → Buy (match_rate_cv = 0.649)

All univariate rules are near-zero threshold (slightly above -0.02): they essentially say
"buy when price is not clearly below the H1 EMA/BB band" — a trivially weak momentum signal.
The p-values are statistically significant only due to sample size (n=835) and the multiple-test
correction context explained in [advances_fin_ml, p.160-161]: MDI-based importances are biased
toward continuous features with many split points, making `ema_dist_20_H1` appear dominant when
the real effect may be spurious under data-mining bias [evidence_based_ta, p.281].

The feature `ema_dist_20_H1` with importance 0.48 dominates the tree by a factor of ~3 over
the next feature (`ema_dist_20_M15` at 0.14). Per [advances_fin_ml, p.160-161], MDI is biased
toward high-cardinality continuous features, so this dominance cannot be taken at face value
without MDA/SFI cross-validation — which Stage 1 did not perform.

## Confidence breakdown

- Family identification (MARTINGALE_GRID): 0.97 — lot p95/p50 = 121.97 is decisive; k1_pass=FAIL is unambiguous; no alternative family explains this lot distribution
- Direction rule: 0.30 — tree match_rate_cv 0.649 is marginally above baseline 0.502; near-zero thresholds suggest weak signal; direction is not the system's edge mechanism
- Exit logic: 0.10 — hold times entirely NaN; no close timestamps in track record; exit mechanism unknown (likely manual close of the entire martingale stack when recovered)
- Overall: 0.46 (weighted: family 0.97 × 0.50 + direction 0.30 × 0.30 + exit 0.10 × 0.20) — note: overall confidence is for the decoded rule as a REPLICABLE SIGNAL, which is LOW because martingale sizing cannot be replicated (sizing = martingale_NEVER)

## Open questions (para Stage 3 + posteriores)

- **Stage 3 BLOCKED**: per pipeline rules, `MARTINGALE_GRID` systems exit immediately. No replicator run should be attempted. The sizing ladder cannot be reproduced ethically or safely.
- **News event hypothesis**: system name "Happy News" and RIPPER `hour_utc=15.8-17.0` suggest entries at US macro releases (15:30 UTC = Non-Farm Payrolls, CPI, Retail Sales; 17:00 UTC = Fed speakers). A future probe could test whether a news-momentum skeleton (without martingale sizing) has any residual edge — but that is a different system entirely.
- **Survivorship confirmation**: a single Real account with +8,462% gain is strong survivorship evidence. If DecodeFX hosts multiple HappyForex accounts, the cross-account lot distribution (multiple accounts with different starting dates, some presumably blown up) would confirm/deny the ruin hypothesis.
- **Dollar index proxy feature**: `dollar_index_proxy=1.0` appears in RIPPER rule 1 as a conditioning variable. This feature's construction should be verified in features.parquet before any reuse in other systems' Stage 2 analyses.
- **Exit NaN issue**: the absence of hold times in the fingerprint (`hold p50/p95/max: nan`) is anomalous. Stage 1 may need a fix to extract close timestamps for this system, or the data export may be incomplete. This should be logged for the Stage 1 maintainer.
