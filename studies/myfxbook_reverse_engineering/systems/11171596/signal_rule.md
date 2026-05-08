---
system_id: 11171596
family: UNCATEGORIZED
confidence: 0.45
reason_code: taxonomy_gap
candidate_new_family: PAIR_HEDGED_DAILY_FX_SHORT
generated: 2026-05-02
rule:
  entry_window_utc: ["13:00", "13:05"]
  pairs: [EURUSD, USDCHF]
  direction: |
    # Empirical: 1083/1083 trades are Sell (100% position bias). No Buy class
    # exists in the dataset, so candidate miners reduce to the always-Sell
    # baseline (rank-1 match_rate=1.0; ranks 2-10 are univariate rules that
    # only re-discover always-Sell coverage). Direction is therefore modelled
    # as unconditional, not feature-driven.
    SELL if hour_utc == 13 and pair in {EURUSD, USDCHF}
    NONE otherwise
  exit:
    max_holding_hours: 24      # p50 hold = 23.33h post-R4; uses median as primary exit anchor
    take_profit_pips: null     # not derivable from fingerprint (exit_kind=100% manual_or_time)
    stop_loss_pips: null       # not derivable from fingerprint
  sizing: fixed_lot_1.0       # lot p50=1.02, p95=1.17, p95/p50=1.15 — flat, no martingale (k1_pass)
citations:
  - "[evidence_based_ta, p.23-27] — \"Position bias — Tendency of a rule to spend more time in one state (long or short) due to asymmetry between its entry conditions\"; this system exhibits maximal position bias (p(Sell)=1.0)."
  - "[advances_fin_ml, p.276] — Law 3: \"Every backtest result must be reported in conjunction with all the trials involved in its production. Absent that information, it is impossible to assess the backtest's 'false discovery' probability.\" — supports honest UNCATEGORIZED label over forced enum fit."
  - "[advances_fin_ml, p.71-72] — CUSUM / event-based sampling motivation; the system's deterministic 13:00 UTC clock anchor is the inverse pattern (time-based, not info-based) — relevant as a contrast for why the rule miners cannot find a feature-driven Sell trigger."
risk_flags:
  - "always_sell_position_bias — 1083/1083 Sell yields zero Buy contrast, so all univariate/tree miners collapse to baseline; cannot disambiguate feature-driven Sell from unconditional Sell."
  - "synthetic_cross_short_hypothesis — symmetric volume on EURUSD (542) + USDCHF (541), both Sell, is consistent with a synthetic short of EUR/CHF (Sell EURUSD + Sell USDCHF nets to short EUR + long CHF; USD legs cancel). Unverified — replicator should test EURUSD-only, USDCHF-only, and paired execution."
  - "bimodal_hold — p50=23.33h vs p95=560.65h vs max=1782h (~74d). Exit logic is not single-mode; replicator using a 24h max-hold will diverge from the long-tail trades. Possibly a hold-until-profit fallback on losers, but evidence is insufficient."
  - "vendor_selection_bias — HappyForex vendor + ForexMart broker (offshore retail); reduce confidence per decoder.md workflow step 3."
  - "calendar_proximity_unverified — 13:00 UTC is adjacent to the 13:30 UTC US data-release bucket (CPI/NFP/Retail Sales). Per decoder workflow rule 8, this signal_rule classifies only from observed trade/OHLC evidence; do NOT assume an economic-calendar-aware implementation when replicating."
---

# Decoded signal — Happy Algorithm PRO FM - REAL (SET1) (id 11171596)

## Family rationale

**No closed-enum family fits.** The fingerprint signature is: (1) a single dominant clock anchor at 13:00 UTC carrying 54.6% of all trades (591/1083) and 49.6% in the single 13:00:xx five-minute bucket (537/1083); (2) unconditional Sell across the entire 1083-trade record (zero Buy); (3) a near-symmetric two-pair universe (EURUSD 542 + USDCHF 541) that, when both legs are short, expresses a synthetic short EUR/CHF (the USD legs cancel: short EUR vs long USD + short USD vs long CHF = short EUR + long CHF); (4) bimodal hold distribution (p50=23.33h, p95=560.65h, max=1782h ≈ 74 days) with `exit_kind=manual_or_time` for all 1083 trades. None of the 12 closed-enum families captures all four traits simultaneously:

- `LATE_NY_BREAKOUT` requires entry 21-01 UTC (peak here is 13:00 UTC).
- `LONDON_OPEN_MOMENTUM` / `LONDON_OPEN_MR` require entry 06-09 UTC.
- `NY_SESSION_REVERSAL` matches the hour band (12-16 UTC) but demands direction conditional on a prior London move; here direction is unconditional.
- `OVERLAP_NY_LONDON_RANGE` matches the hour band but demands direction determined by Bollinger/range position; here direction is unconditional.
- `FACTOR_SCALPING` requires hold p50 < 0.5h confirmed post-R4; this system has p50 = 23.33h (`hold_mismatch` against the post-R4 sanity rule in decoder.md).
- `MARTINGALE_GRID` requires k1_pass=False; here k1_pass=PASS, lot p95/p50=1.15 (flat).
- `H1_MOMENTUM_GOLD` requires Gold/XAU; pair universe is FX majors.
- `NEWS_RELEASE_MOMENTUM` requires (a) name flag NEWS/HF News (name is "Happy Algorithm PRO FM", no news flag) AND (b) hold p50 ≪ 5 min (here 23.33h, three orders of magnitude off the prototype 0.01h on system 1612420).
- `SWING_TREND_MOMENTUM` requires top hour < 15%; top hour here is 54.6%, killing the criterion. Median hold 23h is also far below the >72h provisional threshold.

Per `_diagnostics/5R-1-hardening.md` §1 and the closed-enum contract in `shared/decoder_taxonomy.py`, the honest output is `family=UNCATEGORIZED + reason_code=taxonomy_gap + candidate_new_family=PAIR_HEDGED_DAILY_FX_SHORT`. The candidate label captures the four-trait signature: (a) deterministic daily clock anchor, (b) paired-symbol synthetic-cross expression, (c) unconditional one-sided direction, (d) manual-or-time exit on the order of one day. This pattern would need a 2nd independent supporting system in R1 before promotion (per the provisional-family rule).

The rule miners' degeneracy reinforces the choice: rank-1 in `candidates.json` is literally the always-Sell baseline (`match_rate_cv=1.0`), and ranks 2-10 are univariate features whose `> threshold` clauses each cover ~80% of the dataset only because every label is Sell. With zero Buy contrast, no miner can return a feature-driven Sell rule — the miners are *not* finding edge, they are re-discovering the empty Buy class. This is `degenerate` from a rule-mining artefact perspective, but `taxonomy_gap` is the more accurate root cause: the strategy itself is coherent (single anchor + paired short), it just falls outside the enum. Choosing `taxonomy_gap` over `degenerate` follows the decoder.md guidance that the `UNCATEGORIZED` reason_code should describe the strategy, not the artefact of the miner.

López de Prado's Law 3 [`advances_fin_ml`, p.276] is the methodological warrant: forcing a fit into `OVERLAP_NY_LONDON_RANGE` or `NY_SESSION_REVERSAL` based only on the 12-16 UTC hour band — while ignoring the unconditional-Sell trait that contradicts both — would understate the trial space and inflate spurious match rates downstream. Aronson [`evidence_based_ta`, p.23-27] gives the structural label for the always-Sell behaviour: `position bias` (rule spends 100% of time short due to entry asymmetry). On detrended FX series with $ADC \approx 0$, a binary rule with maximal position bias has expected return zero — meaning the system's edge, if any, must come from the timing or pair-hedge structure, not from the directional choice itself. That is exactly what a `PAIR_HEDGED_DAILY_FX_SHORT` family would describe.

## Rule derivation

**Entry window:** `13:00–13:05 UTC` is taken directly from the fingerprint EDA: top hour:5min bucket is `13:00` with 537/1083 trades (49.6%), followed by `13:05` with 12 trades, `13:40` with 12, and dispersed tail in 14:00–17:00. The 13:00 minute alone accounts for almost half the dataset. No widening to the full 13-17 hour band is justified by the candidates — none of the rule-miner outputs uses an `hour_utc` feature as the splitter (they all collapse to `> threshold ⇒ Sell`-style univariate degenerates).

**Pairs:** `EURUSD` (542) and `USDCHF` (541) — these are the only two symbols with non-trivial trade count, and they are near-perfectly balanced (50.05% / 49.95%). The balance is suggestive of paired execution rather than two independent bets.

**Direction:** unconditional `SELL`. Justification: 1083/1083 trades are Sell; `direction_by_pair` shows `EURUSD: buy_pct=0.0%, USDCHF: buy_pct=0.0%`; `direction_by_hour` shows `buy_pct=0.0%` for all top-5 hours. No candidate rule in `candidates.json` is anything other than the always-Sell baseline or a univariate that re-discovers it. The `dow > 0 ⇒ Sell` rule at rank 2 (cv=0.804) is misleading — its 80.4% coverage is purely the dow>0 base rate × 100% Sell, not a dow-conditional edge.

**Exit:** `max_holding_hours: 24` mirrors the median hold (p50=23.33h ≈ 1 day). This will mis-fit the long-tail trades — p95=560h means ≥ 5% of trades hold over 23 days — but the fingerprint provides no feature on which to condition the longer holds (TP/SL/trailing all unobserved; `exit_kind=manual_or_time` is the only signal). Both `take_profit_pips` and `stop_loss_pips` are set to `null` rather than guessed; an invented bracket would violate the decoder.md anti-pattern "Inventar um threshold". Stage 3 should test this assumption explicitly (see Open Questions).

**Sizing:** `fixed_lot_1.0`. Lot p50=1.02, p95=1.17, p95/p50=1.15, `martingale flag: PASS, steps=0, max_streak=0`. The vendor sizing is essentially flat — the replicator should not introduce equity-proportional sizing on its own.

## Confidence breakdown

- **Family identification: 0.25** — no enum match; the candidate label `PAIR_HEDGED_DAILY_FX_SHORT` is provisional, n=1, awaits R1 corroboration. The 13:00 UTC anchor superficially overlaps with `OVERLAP_NY_LONDON_RANGE` and `NY_SESSION_REVERSAL` hour bands but contradicts both on direction logic.
- **Direction rule: 0.95** — empirical 1083/1083 Sell is unambiguous; the only doubt is whether the live system would *ever* emit a Buy under conditions not yet observed in the 2-year window (e.g. a regime filter not seen in-sample).
- **Exit logic: 0.30** — bimodal hold distribution is uncharacterized. The 24h max-hold will systematically truncate the long-tail trades the vendor actually held for weeks, biasing the replicator's match rate downward on those trades. Without TP/SL evidence, this is the weakest leg of the rule.
- **Open identifiability: 0.40** — the synthetic-cross hypothesis (short EURUSD + short USDCHF ≈ short EURCHF) is mechanically plausible but unverified; replicator should test the three execution variants (paired, EURUSD-only, USDCHF-only) to distinguish.
- **Overall: ~0.45** — weighted toward family identification (lowest) and exit logic (second-lowest), partially recovered by direction certainty. Vendor selection bias (HappyForex / ForexMart) further caps the ceiling per decoder.md workflow step 3.

## Open questions (para Stage 3 + posteriores)

- **Synthetic-cross verification:** does the system's PnL curve track a synthetic short EURCHF more tightly than the sum of independent EURUSD-short and USDCHF-short PnLs? If yes, the replicator should report the paired execution variant as primary and tag the family `PAIR_HEDGED_DAILY_FX_SHORT` with a `synthetic_target=EURCHF` annotation.
- **Exit-logic decomposition:** the bimodal hold (p50=23h vs p95=560h vs max=1782h) is consistent with a "manual_or_time" rule that closes winners on a daily schedule and holds losers until they recover. Stage 3 should bucket the trades by realized PnL sign and test whether the long-tail trades are systematically the losing trades — if so, this is a hidden hold-until-profit pattern that fundamentally changes the risk profile (drawdown understated).
- **Calendar-aware replication (decoder rule 8):** 13:00 UTC sits one bucket before the 13:30 UTC US data-release window (CPI/NFP/Retail Sales). The current `signal_rule.md` classifies *only* from observed trade/OHLC evidence and does not assume the live EA reads an economic calendar. If the system's true edge depends on news avoidance/exploitation, an OHLC-only replicator will under-represent the edge, biasing the reliability score downward. A second-pass replicator could be tested with a calendar mask (e.g. exclude/include the 13:25-13:35 window around scheduled US releases) and the delta reported as a calendar-sensitivity diagnostic — without changing the canonical `signal_rule.md`.
- **R1 corroboration for `PAIR_HEDGED_DAILY_FX_SHORT`:** if no other system in the 30 non-rechecked R1 batch surfaces with the same four-trait signature (clock anchor + always-one-direction + paired-symbol synthetic cross + manual_or_time bimodal exit), this remains an n=1 taxonomy-gap candidate and should not be promoted to a 4th provisional family. Per `_diagnostics/5R-1-hardening.md` §1, provisional promotion is gated on user approval *and* a 2nd independent supporting system.
- **Position-bias edge null:** per Aronson [`evidence_based_ta`, p.26-28], a binary reversal rule on a detrended series has $ER = 0$ regardless of position bias when $ADC \approx 0$. EURUSD and USDCHF detrended ADCs are very close to zero on the 2024-2026 sample. The implication is that the always-Sell directional choice contributes essentially nothing to expected return — the entire edge (if any) lives in the timing window, the pair-hedge cancellation, and/or the asymmetric exit. Stage 3 score breakdown should attribute realized PnL to those components separately.
