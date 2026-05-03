---
system_id: 10475089
family: UNCATEGORIZED
confidence: 0.42
generated: 2026-05-02
reason_code: taxonomy_gap
candidate_new_family: TOKYO_OPEN_SWING
rule:
  entry_window_utc: ["00:00", "00:05"]
  pairs: [GBPJPY]
  direction: |
    # Universe is single-pair (GBPJPY) and direction signal is weak:
    # baseline buy_rate=0.6154; best univariate rule (rank 2-4)
    # match_rate_cv=0.6496 -> only +3.4pp lift over Always-Buy, with
    # p_value_corrected=0.392 (NOT significant after Bonferroni n_tests=504).
    # Aronson [p.281, p.345] forbids using single-rule p-values
    # post data-mining -> no enforceable directional rule.
    BUY if hour_utc == 0 and minute_utc < 5
    NONE otherwise
    # Buy bias is the only honest claim. Any threshold from candidates
    # (ret_1_M1 > -0.000178, bb_pos_20_2_M5 > -0.598, etc.) is post-hoc
    # noise -- all 9 univariate rules tie at coverage 0.795 with identical
    # raw_p, characteristic of degenerate "almost-always-true" predicates
    # that just recover the buy bias.
  exit:
    max_holding_hours: 627.89    # p95 of empirical hold (post-R4 fix); not a TP/SL exit
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct  # lot p95/p50=1.09, no martingale (k1_pass)
citations:
  - "[evidence_based_ta, p.281, p.345] -- 'NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run.' Top candidate p_corrected=0.392 -> null cannot be rejected."
  - "[evidence_based_ta, p.367-380] -- session/hour-of-day FX framework. 97.4% trades fire at 00:00 UTC = Tokyo open on GBPJPY (yen-cross), suggesting clock-anchored Asian-session entry, but session-FX literature is on intraday closings (1-3h holds), not 2.8-day median holds."
  - "[advances_fin_ml, p.276 -- Law 3] -- 'Every backtest result must be reported in conjunction with all the trials involved.' 9 univariate candidates collapse to identical match_rate via 79.5% coverage of the buy-baseline -> false-discovery posture demands UNCAT."
  - "[advances_fin_ml, ch.3, p.78-80] -- triple-barrier labeling: exit_kind=manual_or_time over 100% of trades + p50_hold=66h means no TP/SL barrier exists; only the vertical time barrier is observed (and it is wide)."
risk_flags:
  - "DD live = 40.56% on real-money ForexMart 1:500; consistent with stop-less hold-the-loser behavior on multi-day yen-cross positions."
  - "n=117 over ~13 months on a single pair (GBPJPY) -- underpowered for any pair-specific rule."
  - "97.4% clock anchor on 00:00 UTC + 2.8d median hold is a coherent novel pattern (Tokyo-session-anchored swing on yen cross), but no enum family covers it cleanly. Provisional SWING_TREND_MOMENTUM (D6) requires top_hour<15% -- FAIL: top_hour=97.4%. So this is taxonomy_gap, not insufficient_evidence."
  - "Equity status '(79.70%) $7,360.81' with last update 2024-07-31 suggests system entered drawdown phase; HappyForex vendor blackout 2021-2026 -- out-of-sample edge persistence unknown."
  - "ForexMart broker (offshore) at 1:500 leverage -- execution-quality and spread assumptions for replicator are uncertain; widen GBPJPY spread to 3-5 pips for Stage 3."
---

# Decoded signal -- Happy Japanese Market FM (id 10475089)

## Family rationale

**Why UNCATEGORIZED + taxonomy_gap -> candidate_new_family=TOKYO_OPEN_SWING.**

The fingerprint shows a *coherent* pattern that the closed enum cannot host:

1. **Clock anchor at 00:00 UTC (Tokyo open).** 114/117 trades = 97.4% fire in the [00:00, 00:05) UTC bucket. This is the Tokyo session opening for GBPJPY, the canonical yen-cross. The 3 outlier trades (08:00, 14:00, 17:00 UTC) are 1 each -- likely manual interventions or rollovers, not part of the systematic rule.
2. **Multi-day hold incompatible with intraday session families (R4-corrected).** Post-R4 hold p50=66.47h (~2.77 days), p95=627.89h (~26 days), max=870.73h (~36 days). This eliminates LATE_NY_BREAKOUT, LONDON_OPEN_*, NY_SESSION_REVERSAL, OVERLAP_NY_LONDON_RANGE, FACTOR_SCALPING -- all of which require exits within hours per `decoder_taxonomy.py` criteria. Pre-R4 fingerprint had hold=NaN; the corrected p50=66h is the decisive new evidence.
3. **Single pair (GBPJPY).** All 117 trades on one yen cross. This eliminates FACTOR_SCALPING (multi-asset) and is too narrow for SWING_TREND_MOMENTUM as practiced (Clenow's `[stocks_on_the_move]` is cross-sectional rank -- N>>1).
4. **Provisional SWING_TREND_MOMENTUM (D6) FAILS its own gate.** Per `decoder_taxonomy.py:204-207`: criteria require `top_hour < 15%`. Here top_hour = 114/117 = 97.4% -- a clock-anchored execution model, antithetical to swing-trend's signal-driven entries. Reference system 8577442 (Happy Way FM) had p50=213.99h (~9d), 3x our hold; nomenclature alone (FM = "Forex Market"?) does not justify mapping to that family.
5. **Provisional H1_MOMENTUM_GOLD (D7) FAILS asset gate.** Gold-only family; N/A for GBPJPY.
6. **NEWS_RELEASE_MOMENTUM (D5) FAILS hold gate.** Reference system 1612420 had p50=0.01h (~36s); ours is 66h. Wrong order of magnitude.

The pattern (Tokyo-open-anchored + yen-cross + multi-day hold) is internally coherent and could plausibly recur across other "Happy *Japanese* Market"-themed vendor systems. Per the user's contract `decoder_taxonomy.py:65-66, 313-321`, this is exactly when `taxonomy_gap` + `candidate_new_family` applies, not `insufficient_evidence`.

**Why not just `family=UNCATEGORIZED + reason_code=insufficient_evidence`?** Both reason codes are defensible. I chose `taxonomy_gap` because:
- The timing+pair pattern is *unambiguous and reproducible* (97.4% concentration is not noise).
- The hold distribution post-R4 is *consistent* (p50=66h is a real median, not NaN as pre-R4).
- What is missing is *the enum slot*, not the evidence.
- Per the decoder.md contract, `insufficient_evidence` is for cases where the fingerprint itself is ambiguous; here the fingerprint is sharp but no family fits.

If R1 brings a 2nd HappyForex Japanese-themed system (e.g., another *Japan*/*JPY* labelled vendor product) with the same 00:00 UTC anchor + yen-cross + multi-day hold signature, TOKYO_OPEN_SWING graduates to a new provisional family.

## Rule derivation

The candidate table is *informationally degenerate*:

- Rank 1 (baseline) Always-Buy = 0.6154.
- Ranks 2-4 (univariate) all post identical match_rate_cv = 0.6496 with coverage = 0.795 and identical raw_p = 0.000779. This is the canonical signature of a `feature > X` predicate that subsumes the buy-bias: when 79.5% of trades pass the threshold, the rule degenerates to "Buy when this trivial filter is satisfied," recovering the population's 65% Buy rate.
- Ranks 5-10 cluster at match_rate=0.6325 with raw_p=0.00266 and coverage 0.795 -- same degeneracy at slightly lower threshold.
- All 9 univariate rules have `p_value_corrected ∈ {0.392, 1.000}` after Bonferroni for n_tests=504. None survives correction at α=0.05. Per Aronson [p.281, p.345]: data-mining bias forbids treating any of these as "the rule."

Therefore the only rule the agent is willing to assert literally is: **fire at 00:00 UTC on GBPJPY, default Buy with weak bias.** No threshold from the candidate set is enforceable. The replicator should treat this as effectively a coin-flip on direction with a strong clock anchor -- and Stage 3 is expected to surface low reliability accordingly, not to validate a non-existent edge.

Exit logic is not derivable from candidates (which only mine *entry* direction). The empirical hold distribution post-R4 (p50=66.47h, p95=627.89h, max=870.73h) and exit_kind=manual_or_time across 100% of trades indicate no TP/SL is enforced; positions exit either on a wide time barrier or discretionarily. The 40.56% live drawdown is consistent with this hold-and-hope behavior on yen-cross positions through adverse moves.

## Confidence breakdown

- **Family identification: 0.55** -- high confidence the pattern does NOT fit any of the 12 enum families (eliminations are clean post-R4); medium confidence that TOKYO_OPEN_SWING is the right *new* label vs. e.g., ASIAN_SESSION_HOLDER or YEN_CROSS_OVERNIGHT. Single-system support per decoder_taxonomy.py provisional rule.
- **Direction rule: 0.30** -- can only assert the buy-bias (61.5%); no significant threshold rule survives multiple-comparison correction.
- **Exit logic: 0.40** -- empirical distribution is observable (p50=66h, p95=628h post-R4) but no parametric exit (TP/SL) recoverable; replicator must use time-barrier proxy.
- **Overall: 0.42** = weighted mean (0.4*family + 0.3*direction + 0.3*exit). Below 0.5 -> mandates UNCATEGORIZED per project rule, which aligns with the `taxonomy_gap` resolution.

## Delta vs prior label (Sonnet baseline)

- **Prior:** `family=UNCATEGORIZED, confidence=0.38` (no `reason_code`, no `candidate_new_family` -- legacy v2 schema).
- **R1 v3 strict:** `family=UNCATEGORIZED, confidence=0.42, reason_code=taxonomy_gap, candidate_new_family=TOKYO_OPEN_SWING`.
- **Reclass:** False on family, but contract-relevant fields (`reason_code`, `candidate_new_family`) are now populated per `validate_decoder_output` strict mode. Confidence nudged +0.04 on the back of R4 hold-time evidence (no longer NaN), which makes the *negative* taxonomy verdict (none of 12 families fits) more defensible.

## Open questions (para Stage 3 + posteriores)

- Does the replicator at hour_utc==0 + buy-bias-only on GBPJPY reproduce the live equity curve qualitatively (gain trajectory + 40.56% DD)? If yes, the direction rule may genuinely be ~Always-Buy at Tokyo open and the alpha (such as it is) lives entirely in the clock anchor + carry/swap dynamics of GBPJPY at JPY rollover time.
- Is the 00:00 UTC anchor exploiting a JPY rollover / swap-credit mechanic on GBPJPY, rather than a price-pattern edge? GBPJPY has historically positive swap on long side at most retail brokers -- a long-biased Tokyo-open hold for ~2 days could be partially harvesting carry. ForexMart 1:500 leverage amplifies any such mechanic.
- R1 must check whether a *second* HappyForex system (search vendor library for "Japan" / "JPY" / "Tokyo") shows the same 00:00 UTC + yen-cross + multi-day hold signature. If yes -> TOKYO_OPEN_SWING gets 2nd supporter and graduates to provisional. If no -> leave as candidate_new_family on this single system.
- Stage 3 reliability proxy is expected to be low (entry rule is a clock + buy-bias only; no edge surface). This system is likely a `demote` candidate regardless of family resolution. The R1 contribution here is methodological (taxonomy gap discovery), not investable.
