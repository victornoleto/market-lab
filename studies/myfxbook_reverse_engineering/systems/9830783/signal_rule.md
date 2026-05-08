---
system_id: 9830783
family: UNCATEGORIZED
confidence: 0.30
reason_code: hold_mismatch
generated: 2026-05-02
rule:
  entry_window_utc: ["11:00", "20:00"]
  pairs: [USDCAD, GBPCHF, EURCHF, AUDNZD]
  direction: |
    # Best-fit reconstruction from candidates.json. Tree CV match=0.527 is
    # statistically indistinguishable from baseline always-Sell (0.526),
    # so this rule is reported for replicator wiring only — direction edge
    # is NOT confirmed. Univariates (rank 4-10) all point to momentum-following
    # but each only covers 30-50% of trades.
    #
    # Tree-derived (rank 2 of candidates.json) — class 1 = Buy, class 0 = Sell:
    BUY  if bb_pos_20_2_H1 <= 0.77 and ret_10_H4 <= -0.02
    BUY  if bb_pos_20_2_H1 <= 0.77 and ret_10_H4 > -0.02 and ema_dist_20_H1 > -2.09 and ema_dist_20_H4 <= -1.64
    BUY  if bb_pos_20_2_H1 > 0.77 and atr_ratio_M15 <= 0.78 and bb_pos_20_2_H4 <= 0.85 and atr_ratio_H4 <= 1.63
    BUY  if bb_pos_20_2_H1 > 0.77 and atr_ratio_M15 <= 0.78 and bb_pos_20_2_H4 > 0.85 and ret_1_H4 <= 0.0
    BUY  if bb_pos_20_2_H1 > 0.77 and atr_ratio_M15 > 0.78
    SELL otherwise
  exit:
    max_holding_hours: 720
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_1.12
citations:
  - "[advances_fin_ml, p.39-40] — Table 1.2 lists pitfall #5 'Fixed-time horizon labeling [classification]' and pitfall #6 'Learning side and size simultaneously [classification]' as systemic ML-finance failure modes; forcing a family label on a system whose direction rules do not exceed baseline is exactly the regime this warning targets."
  - "[evidence_based_ta, p.26-28] — 'Expected Return of a binary reversal rule (no-predictive-power baseline)': when a candidate rule's match rate is indistinguishable from the unconditional class prior, the rule has no demonstrated predictive power; here tree CV 0.527 vs always-Sell 0.526 fails to separate from the null."
  - "[evidence_based_ta, p.34] — 'Noise rule — A rule whose +1/−1 signals are randomly paired with market returns; used as benchmark by Monte Carlo Permutation [p.239-240].' This is the methodological null the candidates fail to reject."
  - "[algo_trading_chan, p.153-154] — 'mean-reverting strategies have capped upside but potentially unbounded drawdown, while momentum strategies have limited downside (via natural stop loss) but unlimited upside.' The 70.88% drawdown plus p95 hold of 675h (~28d) is the unbounded-drawdown failure mode of an MR-style 'let losers run' position management, but not enough evidence is present to commit to an MR family classification."
risk_flags:
  - "hold_mismatch — p50 hold = 16.22h is past the intraday norm (UncatReason.hold_mismatch defines hold<24h as disqualifying for swing classification) AND p95 = 675.62h (~28d) and max = 25617h (~3y) far exceed the 168h intraday upper bound. SWING_TREND_MOMENTUM provisional criterion (p50>72h) is also failed. No single family in the closed enum fits the observed hold distribution."
  - "direction_degenerate — tree CV match_rate=0.527 is essentially identical to baseline always-Sell match_rate=0.526 (Δ=0.001, well inside std=0.021). RIPPER (rank 1) CV=0.535 is also tight to baseline. Univariates (ranks 4-10) reach 0.55-0.56 but each covers only 30-50% of trades. Direction is not demonstrated to be predictable from OHLC features."
  - "high_drawdown_distress — 70.88% reported drawdown; live equity 39.33% of balance. p95/p50 hold ratio ≈ 42x suggests asymmetric position management (winners closed quickly, losers held weeks-to-years). This is a behavioural pattern flag, not a strategy family."
  - "broker_obscure — ForexMart, MT4, leverage 1:500 (consistent with the offshore retail FX ecosystem repeatedly flagged in the HappyForex vendor cohort)."
  - "no_name_flag_news — vendor name 'Happy Galaxy FM' carries no NEWS/HF News string; top entry hour bucket (18:00 UTC) carries 9.9% of trades, well below the 30% threshold for clock-anchored classification, so NEWS_RELEASE_MOMENTUM provisional is not applicable. Per task brief: no economic-calendar/news-feed implementation is assumed; calendar-aware replication is left as an open question."
  - "broad_entry_window — top 5 hours (18, 17, 19, 11, 12 UTC) span London-afternoon through NY-afternoon continuously, with no isolated peak. This rules out every session-anchored intraday family (LATE_NY_BREAKOUT, LONDON_OPEN_*, NY_SESSION_REVERSAL, OVERLAP_NY_LONDON_RANGE)."
---

# Decoded signal — Happy Galaxy FM - REAL (id 9830783)

## Family rationale

The closed taxonomy in `shared/decoder_taxonomy.py` (12 values) is exhausted by elimination, and `UNCATEGORIZED` is the only honest output. Walking the enum:

- **Intraday session-anchored families** (`LATE_NY_BREAKOUT`, `LONDON_OPEN_MOMENTUM`, `LONDON_OPEN_MR`, `NY_SESSION_REVERSAL`, `OVERLAP_NY_LONDON_RANGE`): all require an entry-hour concentration in a specific 3-4h window. The fingerprint shows top-5 hours `{18: 395, 17: 329, 19: 325, 11: 322, 12: 254}` — the largest single bucket (18 UTC) carries only 395/4000 = 9.9% of trades, and the top five span London-afternoon through NY-afternoon continuously. There is no isolated 3-4h anchor. Additionally, post-R4 hold data (`p50 = 16.22h`, `p95 = 675.62h ≈ 28d`, `max ≈ 3 years`) violates the intraday hold expectation; per `decoder.md` anti-patterns, "atribuir família intraday … quando hold p50 > 24h confirmado pós-R4" is forbidden. p95 itself is ~4× the 168h ceiling, so even the day-side of the bimodal distribution leaks deep into multi-week swing territory.
- **`OVERNIGHT_GAP_FADE`**: requires Friday-late / Monday-early concentration; not present in fingerprint EDA (peaks are mid-week mid-day UTC).
- **`FACTOR_SCALPING`**: requires `hold p50 < 30 min CONFIRMADO` post-R4. Here `p50 = 16.22h`, three orders of magnitude away — explicit ❌ in `decoder.md` anti-patterns.
- **`MARTINGALE_GRID`**: explicitly excluded by Stage 1 sanity (`martingale flag: PASS (no martingale), steps=0, max_streak=0`, lot p95/p50 ratio 1.23).
- **`H1_MOMENTUM_GOLD`** (provisional D7): requires Gold/XAU. Universe here is `USDCAD/GBPCHF/EURCHF/AUDNZD/CADCHF` — no Gold.
- **`NEWS_RELEASE_MOMENTUM`** (provisional D5): requires (i) name-flag NEWS/HF News and (ii) clock-anchored ≥1 bucket >30%. Vendor name "Happy Galaxy FM" has no news flag, and no hour bucket exceeds 9.9%. Both conjunctive criteria fail; per the task brief, calendar-aware replication is *not* assumed.
- **`SWING_TREND_MOMENTUM`** (provisional D6): requires `p50 hold > 72h` AND `top hour < 15%` AND H4/D1 features dominating. `top hour = 9.9% ✓` and tree feature importance has H4 representation (`ret_10_H4 = 0.17`, `bb_pos_20_2_H4 = 0.11`), but `p50 hold = 16.22h ≪ 72h` — the family criterion fails. The bimodal distribution (median 16h, p95 28d) is the textbook `hold_mismatch` signature: too long for intraday, too short on the median for swing.

The hold distribution is the most direct disqualifier: `p95/p50 ≈ 42×` and `max hold ≈ 3 years` indicate asymmetric position management ("let losers run") rather than a coherent timeframe family. This is consistent with the failure mode Chan describes — "mean-reverting strategies have capped upside but potentially unbounded drawdown" `[algo_trading_chan, p.153-154]` — but it does not convert into a positive family classification, since the rule miners do not deliver evidence of a coherent MR rule (the BB-position split in the tree is offset by tree CV ≈ baseline).

`reason_code = hold_mismatch` is the cleanest of the six `UncatReason` values: the *primary* obstruction is the hold distribution being internally inconsistent with every family in the enum. `degenerate` (tree CV ≈ baseline) and `mixed_strategy` (timing peaks span 11-19 UTC continuously) are real secondary issues, captured as `risk_flags` rather than the primary reason. Per `_diagnostics/5R-1-hardening.md` §1, `taxonomy_gap` is reserved for *coherent* strategies outside the enum — this system is not coherent enough to merit a `candidate_new_family` proposal, since direction itself is not separable from baseline.

`[advances_fin_ml, p.39-40]` Table 1.2's pitfalls #5 and #6 — Fixed-time horizon labeling and Learning side/size simultaneously — and `[evidence_based_ta, p.26-28]`'s no-predictive-power baseline together formalize why a forced label is harmful here: candidate evidence does not exceed the chance baseline, so any non-`UNCATEGORIZED` label would be a fabrication. The previous decode (frozen v2) labelled this system `OVERLAP_NY_LONDON_RANGE` with `confidence 0.42`; that decode was made when Stage 1 hold-extraction returned NaN (R4 root cause). Post-R4 the intraday family is now empirically excluded by the 16.22h / 675h / 25617h triple.

## Rule derivation

The `rule` block is recorded for replicator wiring only — every numeric threshold comes verbatim from `candidates.json`, and the rule is **not** expected to reproduce the system's P&L (see `risk_flags: direction_degenerate`).

- **`entry_window_utc: ["11:00", "20:00"]`** — empirical envelope of the top-5 entry hours (11, 12, 17, 18, 19 UTC). Reported as a description, not as a session anchor.
- **`pairs: [USDCAD, GBPCHF, EURCHF, AUDNZD]`** — top 4 of 5 from the fingerprint pair counter; `CADCHF` (n=49, 1.2%) dropped as too small for any rule miner to fit reliably.
- **`direction:`** — verbatim from the rank-2 DecisionTree(max_depth=4) in `candidates.json`, normalised to `BUY/SELL` predicates per the agent's pseudo-code convention. Top split is `bb_pos_20_2_H1 ≤ 0.77` (BB position on H1 below 77%); the tree leans BUY in most leaves but realised actions are 47.4% BUY / 52.6% SELL — i.e. the tree's BUY-leaning assignment is contradicted by the empirical class prior, which is exactly why CV match_rate 0.527 collapses to baseline.
- **`max_holding_hours: 720`** — set at p95 ≈ 28d ≈ 672h, rounded up to 720h. Vendor's empirical exit kind is 100% `manual_or_time`, with no enforced TP/SL. The 3-year max-hold tail (`max = 25617h`) is intentionally truncated; replicator should weight comparison with `risk_flags: hold_mismatch`.
- **`take_profit_pips: null` / `stop_loss_pips: null`** — `exit_kind` distribution is `{manual_or_time: 4000}` — no SL/TP signature.
- **`sizing: fixed_lot_1.12`** — lot p50 = 1.12, p95/p50 = 1.23 (low dispersion), max_streak = 0 (no martingale escalation).

## Confidence breakdown

- Family identification: 0.40 — `UNCATEGORIZED` is itself a confident call (every other family is excluded by an explicit numeric criterion), but the *reason code* choice between `hold_mismatch` (primary) and `mixed_strategy` / `degenerate` (also defensible) carries judgement uncertainty.
- Direction rule: 0.15 — tree CV 0.527 vs baseline 0.526 is statistically null `[evidence_based_ta, p.26-28; p.34]`; the rule is reported but not believed.
- Exit logic: 0.45 — `manual_or_time` with no TP/SL is unambiguous from the fingerprint, but the bimodal hold distribution means a single `max_holding_hours` is a poor approximation.
- Overall: **0.30** — weighted toward family/exit (well-evidenced) but penalised heavily by direction non-predictability.

## Open questions (para Stage 3 + posteriores)

- **Calendar-aware replication.** The task brief explicitly defers any economic-calendar / news-feed implementation. If a future R1 follow-up wires a calendar source (e.g. ForexFactory event tags), re-test whether entries cluster on macro releases — even at top-bucket 9.9% the residual concentration could be event-driven. Not pursued in this re-decode.
- **Bimodal hold distribution.** The p50/p95 ratio of ~42× suggests two regimes: short tactical entries plus a tail of stuck-loser positions. A clustering of trades by `hold_hours` (k-means on log-hold) inside the replicator could test whether one cluster is a coherent intraday family and the other is a management-failure tail.
- **Vendor cohort comparison.** "Happy Galaxy FM" is part of the same HappyForex vendor library that produced `2373850 ↔ 11171596` (par 6R that evaporated post-R4). If R1 finds another HappyForex system with the same multi-pair / no-anchor / bimodal-hold fingerprint, that would reinforce a vendor-pattern explanation rather than a strategy-family one.
- **Provisional family generalisation.** None of the three provisional families (`H1_MOMENTUM_GOLD`, `NEWS_RELEASE_MOMENTUM`, `SWING_TREND_MOMENTUM`) fits this system, and the case for proposing a new family is weak (direction non-predictive). Therefore no `candidate_new_family` is recorded — `taxonomy_gap` is *not* the right reason_code.
