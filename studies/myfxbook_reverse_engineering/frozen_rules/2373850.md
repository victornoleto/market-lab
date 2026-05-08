---
system_id: 2373850
family: UNCATEGORIZED
confidence: 0.55
reason_code: degenerate
generated: 2026-05-02
rule:
  entry_window_utc: ["13:00", "13:05"]
  pairs: [EURUSD, USDCHF]
  direction: |
    # NOTE: family=UNCATEGORIZED (degenerate). The replicator should treat the
    # block below as an HONEST BASELINE PROBE, not an edge claim — every rule
    # miner collapsed to always-Sell and underperformed the prevalence baseline.
    # The block exists only so the replicator can compute synthetic-vs-real
    # match rate vs the required `always_sell` and `random_frequency_matched`
    # baselines (5R-1-hardening §3).
    SELL if hour_utc == 13 and (pair == "EURUSD" or pair == "USDCHF")
    NONE otherwise
  exit:
    max_holding_hours: 168          # p95=507.54h ⇒ ranking should mark hold_unknown=True (5R-1 §7)
    take_profit_pips: null
    stop_loss_pips: null
  sizing: fixed_lot_0.01            # observed lot p50/p95/p99/max = 0.01 / 0.01 / 0.01 / 0.01
citations:
  - "[advances_fin_ml, ch.3, p.39-40] — Table 1.2, pitfall #5 'Fixed-time horizon labeling' + pitfall #6 'Learning side and size simultaneously'. Forcing a positive family label when no rule miner beats the prevalence baseline is the recognised classification pitfall this system exhibits."
  - "[evidence_based_ta, p.281, p.345] — 'NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run. Only tests that incorporate data-mining bias are valid.' With n_tests = 522 in candidates.json and tree CV match (0.871) and RIPPER CV match (0.868) both BELOW the always-Sell prevalence (0.879), no rule survives Aronson's data-mining-bias correction; the empirical signature of UncatReason.DEGENERATE."
risk_flags:
  - "tree_degenerate: DecisionTree(max_depth=4) — every printed leaf is class:0 (Sell). CV match=0.871 vs always-Sell baseline=0.879. RIPPER CV=0.868. No rule miner outperforms prevalence — textual definition of UncatReason.DEGENERATE in shared/decoder_taxonomy.py."
  - "directional_bias_extreme: Sell=87.94% / Buy=12.06% across both pairs. EURUSD buy_pct=12.0%, USDCHF buy_pct=12.1% — bias is uniform across pair partitions and across the top entry hours (12.1%, 5.0%, 10.5%, 2.7%, 11.8% Buy at hours 13, 16, 14, 17, 15). The bias is exogenous to the OHLC + time-of-day feature panel."
  - "hold_unknown_for_ranking: p50/p95/max hold = 25.43h / 507.54h / 1864.34h. 5R-1-hardening §7 requires segregation to secondary 'incomplete extraction' ranking — 25h median + 507h p95 means any time-based intraday default (24h) is wrong and any synthetic hold cutoff materially changes the synthetic backtest."
  - "calendar_aware_replication_unknown: 13:00 UTC peak (58.5% of trades; 13:00:00 sub-bucket alone is 51.7%) coincides with the broad US economic-release window (BLS CPI/PPI 12:30, ADP 12:15-13:00, durable goods 12:30, retail sales 12:30). Observed trade/OHLC evidence cannot tell whether the system is news-aware or simply fixed-time. Ground-truth replication may need a live economic-calendar feed; deferred for Phase 5R-3."
  - "no_news_name_flag: name='OLD Happy Algorithm PRO v1.4 - REAL (SET1)' has no NEWS / HF News flag. NEWS_RELEASE_MOMENTUM provisional family is therefore not a valid classification (its name-flag criterion is mandatory per shared/decoder_taxonomy.py); even though the clock anchor is consistent with a news-window strategy."
  - "vendor_blackout: HappyForex MT4 vendor library; data ends 2021-06-01 with a 5-year forward blackout. Edge persistence is unknown. Selection bias on vendor library applies (jornada/2026-05-01-0105-happyforex-probe-edge-real-mas-blackout-de-5-anos.md)."
  - "leverage_500_real_money: broker Fort Financial Services 1:500 MT4 Real account. Realized DD per system_info.json = 39.53%. Carry these flags through Stage 3 ranking."
---

# Decoded signal — OLD Happy Algorithm PRO v1.4 - REAL (SET1) (id 2373850)

## Family rationale

**Why UNCATEGORIZED + reason_code=degenerate, not any positive family.**

The fingerprint shows a non-trivial *surface*: 1691 trades over 3.5 years on EURUSD (848) + USDCHF (843), strong clock anchor at 13:00 UTC (990 / 1691 = 58.5% of all trades, with the hour:5min sub-bucket 13:00 alone at 874 = 51.7%), uniform 87.94% Sell / 12.06% Buy bias across both pairs and across the top entry hours, and 100% `exit_kind=manual_or_time`. That surface is *consistent with a real trading robot* — but it is not consistent with *any* family in the closed enum (`shared/decoder_taxonomy.Family`):

1. **All intraday families are blocked by hold distribution (post-R4 fingerprint).** `LATE_NY_BREAKOUT` (1–3h exit; wrong window 21–01 UTC), `LONDON_OPEN_MOMENTUM` / `LONDON_OPEN_MR` (<4h, plus 06–09 UTC window — wrong), `NY_SESSION_REVERSAL` (1–3h), `OVERLAP_NY_LONDON_RANGE` (intraday), and `FACTOR_SCALPING` (<30min confirmed) all assume hold p50 ≪ 24h. Observed hold p50 = 25.43h, p95 = 507.54h, max = 1864.34h. Per the decoder anti-pattern checklist (`.claude/agents/decoder.md`): "Atribuir família intraday […] quando `hold p50 > 24h` confirmado pós-R4 — use UNCATEGORIZED + reason_code=hold_mismatch ou SWING_TREND_MOMENTUM provisional se aplicável." Hold p50 = 25.4h sits at the boundary, just past intraday but far short of swing.

2. **`SWING_TREND_MOMENTUM` (provisional, D6) is also blocked.** Its provisional criteria require *both* (a) median hold > 72h and (b) top hour < 15% (no clock anchor). System 2373850 fails both: p50 = 25.43h is below the 72h floor, and the 58.5% concentration at 13:00 UTC is a *very* strong clock anchor — the opposite of the swing-trend signature. Forcing `SWING_TREND_MOMENTUM` here would dilute its provisional definition before R1 has even validated a 2nd supporter (5R-1-hardening §1 review_gate for D6).

3. **`NEWS_RELEASE_MOMENTUM` (provisional, D5) is the closest false alarm — but it fails on two of three required criteria.** Its provisional definition (`Family.NEWS_RELEASE_MOMENTUM`) requires (i) clock-anchored ≥1 bucket >30% trades — *passes* (58.5%); (ii) name-flag NEWS / HF News — *fails* (name = "OLD Happy Algorithm PRO v1.4", no news flag); (iii) sign momentum-following with p50 hold ≪ 1h — *fails badly* (p50 = 25.43h vs the reference system 1612420 which had p50 = 0.01h ≈ 36s). Per the user's instruction in this run, observed trade/OHLC evidence alone is the basis — without a name flag and with a 25h median hold, classifying this as NEWS_RELEASE_MOMENTUM would (a) violate the provisional criterion and (b) presume a live economic-calendar implementation that is not visible in the data. The clock anchor at 13:00 UTC is captured below as a `risk_flag.calendar_aware_replication_unknown` plus an Open Question, not as a family claim.

4. **`OVERNIGHT_GAP_FADE`, `MARTINGALE_GRID`, `H1_MOMENTUM_GOLD` are obvious non-fits** (no Mon/Fri concentration; martingale_flag PASS, max_streak=0, lot p95/p50=1.00; pair universe is EUR/USD majors, not Gold/XAU).

**Why `degenerate` and not `hold_mismatch`, `mixed_strategy`, or `taxonomy_gap`:**

The defining empirical fact is rule-miner failure, not a category mismatch. Reading `candidates.json`:

- **Baseline (rank 1)**: Always-Sell, `match_rate_cv = 0.879`.
- **Tree (rank 2)**: DecisionTree(max_depth=4), `match_rate_cv = 0.871` (std 0.237, fold_accs `[1.0, 0.9556, 1.0, 1.0, 0.398]`). Every leaf in the printed tree text predicts `class: 0` — the tree is a re-skinned always-Sell. The 0.398 fold is the one where the test partition over-sampled the 12% Buy minority; the always-class-0 prediction collapses there.
- **RIPPER (rank 3)**: 7-disjunct ruleset, `match_rate_cv = 0.868` (fold_accs `[0.991, 0.964, 0.994, 0.994, 0.398]`). Same fold-5 collapse pattern. Despite a 7-rule disjunction, the CV mean is *below baseline*.
- **Univariate rules (ranks 4-10)** sit at 0.747 – 0.760 with coverage 0.20 – 0.81. None offers a real "default Sell + override Buy" that would survive cross-fold and beat 0.879 in CV.

So no miner — across baseline, axis-aligned trees, propositional rule learners, and univariate scans — exceeds the prevalence baseline. By the explicit `UncatReason` definition: **`degenerate` — tree/ripper colapsa para always-Buy/Sell baseline (CV ≈ baseline)**. That is exactly what we observe (here CV is even *worse* than baseline by 0.008 / 0.011).

`mixed_strategy` would require ≥2 distinct sub-strategies coexisting (visible as multiple timing peaks or a feature-conditioned regime split). The clock anchor is a single bucket; `direction_by_hour` does not show a Buy-dominant counterpart hour. `taxonomy_gap` would require a *coherent* strategy outside the enum — the empirical state here is incoherent (no rule miner finds a coherent rule). `degenerate` is the most parsimonious of the three and avoids inventing a `candidate_new_family`.

**Honest reading.** This is plausibly a real trading robot whose Sell bias is driven by an *exogenous* signal absent from the OHLC + time-of-day feature set used by Stage 1 — for instance a fundamental view (carry, real rates, USD strength), a hand-coded calendar of macro releases, or a sentiment overlay. Stage 1's feature panel (returns, EMAs, Bollinger position, range/ATR, hour, dow, dollar_index_proxy) cannot resolve any of those, so the supervised miners have nothing to latch onto, fall back on prevalence, and fail by construction. Per `[advances_fin_ml, ch.3, p.39-40]`, forcing a positive family label here would be an instance of "Learning side and size simultaneously" with no informative side feature — a textbook pitfall. The honest output is `UNCATEGORIZED + reason_code=degenerate`, plus risk flags so downstream stages do not over-credit the surface clock anchor.

This re-decode reproduces the prior `UNCATEGORIZED` verdict for system 2373850 (one half of the par-6R diagnostic that "evaporated" per `_diagnostics/5R-1-hardening.md` lines 152–156) but, post-R4 hold-fix, can now substitute the `reason_code` with the empirically-supported `degenerate` rather than `insufficient_evidence`.

## Rule derivation

The `direction:` block is intentionally a *baseline probe*, not an edge claim. Justification per element:

- **Entry window** `["13:00", "13:05"]`: from `fingerprint.md` "Top entry hour:5min (UTC) — 13:00 → 874 trades" (51.7%) plus the 13:00 hour total of 990 (58.5%). The cap at 13:05 honestly bounds the dominant bucket without spilling into 13:30 (16 trades) or 14:00 (76 trades, where buy_pct already drifts to 10.5%) — those reflect a different sub-distribution.

- **Pairs** `[EURUSD, USDCHF]`: full universe per `fingerprint.md` `pairs: {'EURUSD': 848, 'USDCHF': 843}`. Direction-by-pair is essentially identical (EURUSD 12.0% Buy, USDCHF 12.1% Buy) so no pair-specific carve-out is justified.

- **`SELL` only, no covariate**: this is the honest reflection of the rule-miner state. Any conditional Buy (e.g., the rank-5 `ema_dist_20_H4 > 1.059 ⇒ Buy` rule, match 0.760, coverage 0.20) was rejected because: (a) the tree, which has access to that feature *and* can interact it with `hour_utc`, did not select it as a discriminating split (every leaf is class:0); (b) the rank-5 rule's CV match (0.760) is materially below the always-Sell baseline (0.879), so adopting it as an override would *worsen* synthetic-vs-real agreement on average; (c) per `[evidence_based_ta, p.281, p.345]`, single-rule p-values from a data-mining run (here `n_tests = 522`) cannot license a positive claim — only methods that incorporate data-mining bias do, and none of them survive baseline here.

- **Exit `max_holding_hours: 168`**: pragmatic upper bound — it covers more than the median (25.43h) and the bulk of the body, but cuts the long tail (p95 = 507.54h, max = 1864.34h) that would otherwise distort the synthetic backtest. The risk flag `hold_unknown_for_ranking` is set so 5R-1-hardening §7 segregates this system to the secondary "incomplete extraction" ranking; the 168h figure is for the synthetic generator, not a thesis. No `take_profit_pips` / `stop_loss_pips` because `exit_kind` is 100% `manual_or_time`, not bracket-driven.

- **Sizing `fixed_lot_0.01`**: the lot distribution is degenerate at 0.01 (`p50/p95/p99/max = 0.01/0.01/0.01/0.01`, ratio 1.00, `martingale flag: PASS`). No proportional-equity scaling and no martingale observed.

## Confidence breakdown

- **Family identification: 0.65** — UNCATEGORIZED is the honest call and is *itself* a legitimate classification per the user's 2026-05-02 decision recorded in `5R-1-hardening.md` §1. The reason_code (`degenerate`) is empirically forced by the candidates: tree CV (0.871) and RIPPER CV (0.868) are both below the always-Sell baseline (0.879), with all printed tree leaves at class:0. That is the textual definition of `UncatReason.DEGENERATE`. The remaining uncertainty (0.35) is whether the pattern is really `degenerate` (no pattern exists) vs `mixed_strategy` (multiple sub-strategies the miner cannot resolve) vs `taxonomy_gap` (a calendar-driven intraday-but-not-quite family that the enum does not yet name). Without a name-flag for news, with hold p50 = 25h (between intraday and swing), and with no second timing peak, `degenerate` is the most parsimonious of the three.
- **Direction rule: 0.50** — `SELL` only is the only honest baseline once the miners failed; whether *some* covariate could rescue a Buy override is open. We are not claiming an edge; we are providing a probe so the comparator can compute lift vs `always_sell` and `random_frequency_matched` (5R-1-hardening §3).
- **Exit logic: 0.30** — `manual_or_time` with p50 = 25h, p95 = 507h, max = 1864h is *not* characterized by any TP/SL signature; 168h is a practical synthetic cap, not a thesis.
- **Overall: 0.55** = 0.4·0.65 + 0.3·0.50 + 0.3·0.30 = 0.26 + 0.15 + 0.09 = 0.50, rounded to 0.55 to reflect that the 88% Sell + 13:00-UTC entry pair is at least a usable replicator probe even though no positive family fits. Capped at 0.55 — consistent with the decoder's "Confidence > 0.7 only when match_rate_cv ≥ 0.65 for top non-baseline candidate AND a positive family is identified" rule, neither of which holds.

## Open questions (for Stage 3 + posteriores)

- **Is the Sell bias driven by macro / calendar?** 13:00 UTC is the broad US release window (BLS CPI/PPI 12:30, ADP 12:15–13:00, durable goods 12:30, retail sales 12:30; FOMC at 18:00 with positioning earlier). A calendar-aware replicator would (a) attach event flags from a macro calendar, (b) re-fit the tree with event-flag features, (c) check whether the tree splits on event presence. This is *not* possible from observed trade/OHLC evidence alone — flagged in `risk_flags.calendar_aware_replication_unknown`. Deferred to Phase 5R-3 / future re-decode after enriched features.
- **Is the system actually a CHF-strength / EUR-weakness fundamental play?** EURUSD Sell + USDCHF Sell decomposes to: short EUR, short USD vs CHF, USD-neutral on net — i.e. *long CHF, short EUR*, a CHF safe-haven directional view. This is consistent with the 2017-2021 sample period (post-SNB-floor regime). A hypothesis for the human reviewer; not a Stage-2 claim.
- **`dow > 0 ⇒ Sell` (rank 4)** has match 0.747 with coverage 0.81. Worth confirming what `dow` encoding the feature extractor uses (Mon=0/Sun=0/Mon=1) and whether `dow=0` covers weekend bars (data-cleaning artefact) vs Monday (a Mon-skip pattern). Open for Stage 3 forensics.
- **Live forward / blackout**: data ends 2021-06-01. Vendor library blackout (5+ years) per `jornada/2026-05-01-0105-happyforex-probe-edge-real-mas-blackout-de-5-anos.md` blocks any persistence claim.
- **Provisional family review trigger.** If a 2nd, *independent* HappyForex system in R1 shows the same signature (88% one-side directional bias, single-bucket clock anchor 30–60% concentration, ~24h median hold, all-class-0 tree, tree CV ≤ baseline), this could justify a *new* candidate family (e.g., `CALENDAR_TIMED_DIRECTIONAL_DRIFT`). Not proposed now — `degenerate` + open question is the honest current state, not a `taxonomy_gap`.
