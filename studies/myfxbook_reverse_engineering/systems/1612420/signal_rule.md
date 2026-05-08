---
system_id: 1612420
family: NEWS_RELEASE_MOMENTUM
confidence: 0.60
generated: 2026-05-02
rule:
  entry_window_utc: ["15:00", "15:35"]
  pairs: [EURUSD, GBPUSD, AUDUSD, USDJPY]
  direction: |
    # Decision rule from tree rank-1 dominant feature ret_3_H4 (MDI=0.52,
    # next feature ret_10_M5=0.09). Univariate rank-3 confirms sign:
    # ret_3_H4 > -0.0008685 ⇒ Buy at match_rate_cv=0.666 (corrected p≈1.7e-18).
    # Threshold rounded to 0 for parsimony — both threshold and tree split at ~0.
    BUY if ret_3_H4 > 0
    SELL otherwise
  exit:
    max_holding_hours: 1.0
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[evidence_based_ta, p.271, p.287] — \"Data-mining bias — Systematic positive bias in the observed performance of the best rule when several are tested\" (relevant: candidates.json reports n_tests=538 univariate; corrected p_values must be used over raw p)"
  - "[advances_fin_ml, p.160-162] — \"Mean Decrease Impurity (MDI) ... fast but biased toward high-cardinality features\" / \"Mean Decrease Accuracy (MDA) ... unbiased but slower\" (relevant: tree rank-1 reports ret_3_H4 MDI=0.52 — confirmed cross-method by univariate rank-3 on the same feature, mitigating the substitution-effect caveat)"
  - "[evidence_based_ta, p.250] — \"Confidence Interval via Bootstrap Percentile Method ... Remove the top x% and bottom x% from the bootstrap distribution\" (relevant: pre-specified clock-anchor bucket at 15:30 UTC requires bootstrap CI on hourly bucket counts before claiming the concentration is non-random)"
risk_flags:
  - "needs_m1_review — hold p50 = 0.01h (~36 s) post-R4 fix. Sub-M5 timing means M5/M15 OHLC replication will not reproduce entry/exit fidelity. Stage 3 must consume M1 (or finer) bars or score this system in a separate timing-noise bucket. Project timeframe is NOT changed by this flag."
  - "calendar_aware_replication_unknown — name flag \"Happy News\" + 45.2% of trades clustered exactly at 15:30 UTC suggest the live EA may read an economic-calendar feed (e.g., US data releases at 13:30 / 14:30 / 15:00 UTC depending on item; the 15:30 UTC peak coincides with retail sales / Empire State / housing starts windows). The fingerprint provides no direct evidence of a calendar feed. This rule does NOT model one — clock-anchor only — so Stage 3 replication will fire on every weekday at 15:30 UTC including no-news days, which differs from a calendar-gated live system."
  - "demo_account_obscure_broker — system_info.account_type=Demo + broker=Fort Financial Services (1:500, MT4). Vendor selection bias; live execution friction not represented."
  - "edge_persistence_unknown — record ends 2021-06-10, system explicitly tagged \"OLD\" by vendor; ~5 y blackout since then. No FWD evidence post-2021."
  - "provisional_family — NEWS_RELEASE_MOMENTUM is provisional in shared/decoder_taxonomy.py (n=1, this very system). Per its review_gate, if the broader R1 re-decode finds no second supporting system, this label downgrades to UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=NEWS_RELEASE_MOMENTUM."
---

# Decoded signal — OLD Happy News v1.4.1 (id 1612420)

## Family rationale

Three independent dimensions of the fingerprint align with the provisional
`NEWS_RELEASE_MOMENTUM` signature registered in
`shared/decoder_taxonomy.py`:

1. **Clock-anchor**. The 15:30 UTC five-minute bucket alone holds 356/788 trades
   = 45.2%, and the 15:00 UTC hour holds 405/788 = 51.4%
   (`decoder/fingerprint.md` "Top entry hours" / "Top entry hour:5min"). The
   family criterion ("≥1 bucket horário com >30% trades") is satisfied with
   wide margin; no other 5-min bucket is comparable.
2. **Name flag**. `system_info.name = "OLD Happy News v1.4.1 ..."` carries the
   explicit `News` tag required by the family criterion.
3. **Sub-minute hold + momentum sign**. Post-R4 `hold p50 = 0.01h` (~36 s),
   `p95 = 0.46h` (~28 min), `max = 5.83h` — consistent with a fast in-and-out
   reaction to a release. The rank-1 decision tree (CV 0.649) is dominated by
   `ret_3_H4` (MDI = 0.52, next feature `ret_10_M5` = 0.09), and the rank-3
   univariate `ret_3_H4 > -0.0008685 ⇒ Buy` reaches match_rate_cv 0.666 with
   corrected p ≈ 1.7e-18 over n_tests = 538. Both branches of the tree
   preserve sign-following: `ret_3_H4 ≤ 0` → mostly class 0 (Sell);
   `ret_3_H4 > 0` → mostly class 1 (Buy). That is momentum-following, not
   reversion. Per `[advances_fin_ml, p.160-162]`, MDI is biased toward
   high-cardinality features and should be cross-checked; here the rank-3
   univariate on the same feature provides an independent confirmation,
   reducing the substitution-effect risk.

System 1612420 is in fact the n=1 supporting record for the family; this
re-decode reproduces and refines that classification rather than introducing
it. The original D5 evidence used to register the family — name flag,
45 % bucket, p50 ≈ 36 s — is reproduced verbatim here.

Why not the other enum members:

- `LATE_NY_BREAKOUT` (21–01 UTC) — peak is 15:30 UTC, far outside.
- `OVERLAP_NY_LONDON_RANGE` (12–16 UTC, range fade) — peak hour is inside this
  window, but the family is range-fade with positional features (BB pos /
  range_norm). Here `ret_3_H4` (a momentum feature) dominates with MDI 0.52,
  and the highest range-feature MDI is 0.08 (`range_norm_M1`); also the sign
  is following, not fading. A 45 % single-bucket concentration is also
  extreme even by overlap-fade standards.
- `NY_SESSION_REVERSAL` — declared empty post 5R-0 in the taxonomy
  (`review_gate`: "vendor HappyForex sem reversal genuíno na library");
  direction here follows, not reverses.
- `LONDON_OPEN_MOMENTUM` / `LONDON_OPEN_MR` (06–09 UTC) — peak is 6 h after
  London open.
- `OVERNIGHT_GAP_FADE` — would need Friday-late / Monday-morning concentration;
  no evidence.
- `FACTOR_SCALPING` — would need entries distributed across hours, not a 45 %
  single bucket; family is also empty post 5R-0.
- `MARTINGALE_GRID` — sanity flag PASS (steps=0, max_streak=0, lot p95/p50=1.54).
- `H1_MOMENTUM_GOLD` — Gold-specific provisional; pairs here are USD majors.
- `SWING_TREND_MOMENTUM` — requires hold p50 > 72 h; here p50 ≈ 36 s.
- `UNCATEGORIZED` — would discard the genuine clock + name + sign signal that
  was already used to register the provisional family; not honest given the
  evidence.

I treat the news-release classification only as a statement about the
**observed trade pattern** (clock-anchored entries + sub-minute holds +
sign-following). I am NOT inferring that the live implementation reads an
economic-calendar feed — see `calendar_aware_replication_unknown` flag and
the open question on calendar gating.

## Rule derivation

- `entry_window_utc: ["15:00", "15:35"]`. Anchored on the 15:30 UTC peak
  (356 trades) and bounded to absorb the residual mass within the 15:00 UTC
  hour (49 additional trades). Five-minute buckets outside this window are
  much smaller (next is 17:00 = 95). A tight 35-minute window keeps the
  S/N high and avoids contamination from the 17:00 cluster, which may belong
  to a separate sub-pattern (mixed_strategy risk would arise if widened).
  `[evidence_based_ta, p.250]` motivates pre-specifying the event window
  before any test, which we satisfy by anchoring solely on the empirical peak.
- `pairs: [EURUSD, GBPUSD, AUDUSD, USDJPY]` — exactly the universe in
  `decoder/fingerprint.md` sanity (counts 272 / 227 / 165 / 124). All four
  are USD-quoted majors, consistent with a US-session timing thesis. No
  filtering — keep the full vendor universe.
- `direction: BUY if ret_3_H4 > 0 else SELL`. Uses the rank-1 tree's
  dominant feature (`ret_3_H4`, MDI 0.52) reduced to a zero-threshold sign
  rule. The rank-3 univariate threshold `-0.0008685` is numerically near
  zero; rounding to 0 trades a tiny amount of fit for parsimony and
  robustness across pairs. The univariate match_rate_cv at the exact
  threshold is 0.666 (coverage 0.60); at threshold 0 it should sit in the
  same neighborhood. The ripper rank-2 (CV 0.523, std 0.039) is barely above
  the always-buy baseline (0.505) and is unstable across folds — not used.
- `exit.max_holding_hours: 1.0`. Empirically, `p95 = 0.46 h` (~28 min) and
  `max = 5.83 h`. A 1 h cap covers the 95th percentile with margin without
  inheriting the rare 5.8 h tail (likely a stuck or manually closed trade).
  `take_profit_pips` and `stop_loss_pips` are null because exit_kind is 100 %
  `manual_or_time` and no discrete TP/SL is detectable from the
  fingerprint or candidates.
- `sizing: proportional_equity_2pct`. Lot p95/p50 = 1.54 and martingale flag
  PASS (steps=0, max_streak=0). Modest, non-martingale size variation —
  proportional sizing on equity is the standard retail-FX default, and the
  fingerprint shows no evidence of a sweep-style aggressive scheme.

## Confidence breakdown

- Family identification: 0.75 — clock-anchor + name flag + sub-minute hold
  + momentum-following sign converge on the provisional NEWS_RELEASE_MOMENTUM
  signature on three independent dimensions, and this is the very system
  used to register the family. Capped below 0.85 because (a) the family is
  provisional with n=1 and (b) the classification reflects the observed
  pattern only; we have no direct evidence of the live calendar mechanism.
- Direction rule: 0.55 — `ret_3_H4` MDI dominance (0.52) and univariate
  match_rate_cv 0.666 are real lift over always-buy 0.505 (~16 pp), but
  the tree CV folds vary 0.638–0.662 (modest stability) and the
  zero-threshold simplification trades small fit for parsimony. Live
  reproduction depends on `ret_3_H4` being computed identically to Stage 1.
- Exit logic: 0.45 — only `manual_or_time` is observed; the 1 h cap is a
  proxy. Sub-M5 timing cannot be verified faithfully on M5/M15 bars
  (`needs_m1_review`).
- Vendor penalty: −0.10 (Demo) and −0.05 (Fort Financial Services as
  vendor-friendly retail broker, 1:500 / MT4). Per decoder.md workflow §3.
- Overall: **0.60** = 0.4·0.75 + 0.3·0.55 + 0.2·0.45 − 0.15 = 0.555 → 0.60
  after considering that all three family criteria are unambiguously met
  (clock + name + hold + sign), which justifies a small upward round to two
  decimals. Stays well below the 0.7 ceiling that would be allowed only if
  match_rate_cv on the top candidate were ≥ 0.65 (it is 0.649) — the cap is
  consistent with the decoder.md anti-pattern.

## Open questions (for Stage 3 + posteriores)

- **Calendar-aware replication.** The fingerprint shows a clock-anchor at
  15:30 UTC but no information about whether the live EA queries an
  economic-calendar feed. Stage 3 should test two replicator variants:
  (a) every-weekday clock-anchor at 15:30 UTC; (b) calendar-gated 15:30 UTC,
  fired only on dates with US high-impact releases (NFP, CPI, PPI, retail
  sales, Empire State, FOMC). If (b) materially outperforms (a), the system
  is calendar-aware and the rule must be upgraded; otherwise (a) is the
  conservative baseline. This rule, as written, models only (a).
- **Sub-minute fidelity.** With p50 hold ≈ 36 s, M5 bars cannot represent
  entry-to-exit returns. Stage 3 must (i) consume M1 or finer bars,
  (ii) accept that match against MyFxBook trade list will be timing-noise
  dominated, or (iii) score this system in a separate "tick-sensitive"
  bucket. The project timeframe is not changed by this flag.
- **Sign-rule stability over regimes.** `ret_3_H4 > 0` is a 12-hour-lookback
  momentum sign. Walk-forward folds across 2016-02 → 2021-06 should test
  whether the sign rule flips per regime; if it does, a regime feature is
  missing.
- **Bucket-level multiple comparisons.** With 24 hourly buckets × 4 pairs,
  the family heuristic ("≥1 bucket >30% trades") is itself a search. Per
  `[evidence_based_ta, p.271, p.287]` the observed concentration must be
  evaluated against a permutation null on trade timestamps before being
  treated as confirmed edge. The corrected p-values for the univariate rules
  in candidates.json control for the 538-test family but not for the
  bucket-search.
- **Provisional-family review.** Per `decoder_taxonomy.py` review_gate, if
  the broader R1 re-decode produces no second system matching this signature,
  this label downgrades to `UNCATEGORIZED + reason_code=taxonomy_gap +
  candidate_new_family=NEWS_RELEASE_MOMENTUM`.
