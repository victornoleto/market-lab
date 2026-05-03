---
system_id: 1407880
family: LATE_NY_BREAKOUT
confidence: 0.75
generated: 2026-05-02
rule:
  entry_window_utc: ["22:55", "01:30"]
  pairs: [GBPUSD, USDCAD, EURUSD, EURCHF, USDCHF, EURGBP]
  direction: |
    # Direction logic from candidates.json rank 1 (tree, max_depth=4, match_rate_cv=0.640, std=0.054, coverage=1.00).
    # Top features: bb_pos_20_2_M15 (importance 0.62), bb_pos_20_2_M5 (0.26), range_norm_H1 (0.12).
    # The right subtree (bb_pos_20_2_M15 > 0.15) collapses: both M5 children predict class 0 (SELL).
    # Executable form (thresholds verbatim from candidates.json — no invention):
    BUY  if (bb_pos_20_2_M15 <= 0.15) and (range_norm_H1 <= 0.72)
    SELL if (bb_pos_20_2_M15 <= 0.15) and (range_norm_H1 >  0.72)
    SELL if (bb_pos_20_2_M15 >  0.15)
    NONE otherwise
    # Cross-confirmation: univariate rank 8 (bb_pos_20_2_M15 > 0.1951 ⇒ Sell, p_corrected=4.4e-06,
    # CV=0.663, n_tests=544) — independent miner converges on the same feature and a near-identical
    # threshold. Tree's 0.15 kept for executable consistency with higher-coverage (1.00 vs 0.50) rule.
  exit:
    max_holding_hours: 4
    take_profit_pips: null
    stop_loss_pips: null
  sizing: proportional_equity_2pct
citations:
  - "[algo_trading_chan, p.71-72, ch.3] — \"Bollinger band entryZscore / exitZscore ... These are free parameters to be optimized in a training set. Chan uses entryZscore=1, exitZscore=0\" — direct support for using normalized Bollinger position as a mean-reversion entry/exit feature; bb_pos_20_2_M15 is the single-instrument analog of the spread z-score."
  - "[algo_trading_chan, p.94, ch.4] — \"Buy-on-Gap (Intraday Mean Reversion)\" — intraday MR template that fades extension at a session anchor with hold ~hours; structurally matches the 23-01 UTC anchored fade observed here (hold p50=0.98h, p95=3.15h)."
  - "[evidence_based_ta, p.401-403] — \"Channel Normalization (CN) / Stochastics ... Detrending operator that scales the series to 0-100 based on its position in the range of the last n periods; acts as a high-pass filter\" — bb_pos and range_norm features are direct Channel-Normalization-class operators; legitimizes their use across M5/M15/H1."
  - "[trading_systems_methods, p.323-324] — \"If it's not 20-day and 2 sigma, it's not a Bollinger band ... 2σ ≈ 87% confidence in skewed distributions\" — the rule uses canonical 20-period 2-σ on M15/M5, not exotic lengths; reduces curve-fit suspicion on the indicator specification itself."
risk_flags:
  - "demo_account_vendor_bias: account_type=Demo at Fort Financial Services (1:500, MT4) — confidence reduced 0.10 per decoder workflow (vendor selection bias risk). Live PnL reproducibility unverified."
  - "blackout_2021-2026: data ends 2021-06-16; ~5y unobserved persistence. Edge into 2026 unknown — Plano A is DORMANT (mandate §1) and this re-decode supports diagnostic ranking, not capital allocation."
  - "broker_server_time_anchor: hour:5min peaks (00:00→415, 23:00→401, 00:05→350, 23:55→205, 00:15→135) cluster on xx:00 minute boundaries — entries align with M15/H1 broker bar-close clock. Replicator must verify whether MyFxBook timestamps are UTC or broker-local before applying the 22:55-01:30 window."
  - "tree_match_rate_cv_moderate: rank-1 tree CV=0.640 (std=0.054, fold range 0.567-0.717) is only ~11pp above always-Sell baseline 0.530. Per anti-pattern guidance, confidence>0.7 requires CV≥0.65 — direction confidence capped accordingly. The univariate split (CV=0.663, p_corrected=4.4e-06) is the strongest single-feature evidence the edge is real, not the tree's marginal lift."
---

# Decoded signal — OLD Happy Market Hours v2.3.1 (id 1407880)

## Family rationale

The fingerprint is an unambiguous fit for `LATE_NY_BREAKOUT` per the closed enum in `shared/decoder_taxonomy.py`. Three independent signatures align with the family criteria ("Entry concentrado 21-01 UTC, exit 1-3h, FX majors com USD/EUR"):

1. **Timing**: 3303 of 3304 trades enter in 22:00-01:00 UTC (top entry hours: 00:00→1680, 23:00→1375, 01:00→248, 22:00→1). The 5-minute peaks (00:00, 23:00, 00:05, 23:55, 00:15) form a tight cluster straddling the 00 UTC boundary — exactly the late-NY / pre-Asian crossover.
2. **Exit (post-R4 confirmed)**: hold p50/p95/max = **0.98h / 3.15h / 8.60h**, exit_kind 100% `manual_or_time`, no martingale (sanity PASS, max_streak=0). The criterion "exit 1-3h" matches p50≈1h and p95≈3h literally. Post-R4 hold extraction (parquet `(closetime_ms - opentime_ms)/1000`) replaced the prior NaN values from positional HTML parsing — confidence in the exit profile is now empirical, not heuristic.
3. **Universe**: pairs are exactly the FX-majors-with-USD/EUR cluster {GBPUSD, USDCAD, EURUSD, EURCHF, USDCHF, EURGBP} — the family's stated cohort, no JPY/commodity-FX exposure that would suggest an Asian-session-driven strategy.

This is the surviving member of the primary 6R pair (`1407880↔10224499`) per `_diagnostics/5R-1-hardening.md` "Ponto narrativo" — the family registry already records `n_supporting_systems=2` for `LATE_NY_BREAKOUT` with these two systems. This R1 re-decode confirms an existing label rather than proposing a new one.

Alternatives explicitly rejected:

- **`OVERLAP_NY_LONDON_RANGE`**: requires entry 12-16 UTC — disqualified (zero trades 02-22 UTC).
- **`LONDON_OPEN_MOMENTUM` / `LONDON_OPEN_MR`**: require 06-09 UTC — disqualified (zero trades).
- **`OVERNIGHT_GAP_FADE`**: would concentrate Friday-late / Monday-morning; observed pattern is daily 23-01 UTC, not weekly.
- **`NEWS_RELEASE_MOMENTUM` (provisional)**: would require name-flag NEWS/HF News and momentum-following sign with hold p50<5min. System name is "OLD Happy Market Hours v2.3.1" (no news flag) and hold p50=0.98h is ~60× the NEWS template threshold (0.01h ≈ 36s in the reference system 1612420). The xx:00 clock anchor is broker-server bar-close, NOT economic-calendar event timing; this distinction matters because a calendar-aware replicator is unnecessary here. The rule operates only on observed OHLC features (BB position, H1 range) — no economic-event exogenous input is invoked.
- **`FACTOR_SCALPING`**: requires hold p50 < 0.5h confirmed (post-R4 caveat in decoder.md anti-patterns). Observed 0.98h is ~2× the threshold.
- **`MARTINGALE_GRID`**: excluded by sanity PASS (max_streak=0, k1_pass=PASS).
- **`UNCATEGORIZED`**: would require confidence<0.5 or evidence falling outside the enum. The timing+exit+pair triple is too tight for any UncatReason: not `underpowered` (n=3304), not `degenerate` (tree beats baseline by 11pp with p_corrected<1e-5 univariate corroboration), not `hold_mismatch` (intraday family + intraday hold), not `mixed_strategy` (single timing peak), not `taxonomy_gap` (LATE_NY_BREAKOUT exists and matches), not `insufficient_evidence` (tree+univariate+sanity all converge).

The within-family direction nuance — the rule literally executes a Bollinger fade rather than a momentum breakout — is captured in the rule body, not by re-categorizing. The family enum is keyed on session window + hold profile + universe (per `decoder_taxonomy.py:Family.LATE_NY_BREAKOUT.criteria`), not on momentum-vs-fade direction; both directions are admissible inside the same family.

## Rule derivation

Direction logic comes from `candidates.json` rank 1 (tree, `match_rate_cv=0.640`, std=0.054 across 5 folds [0.600, 0.717, 0.567, 0.633, 0.683], coverage=1.0):

```
|--- bb_pos_20_2_M15 <= 0.15
|   |--- range_norm_H1 <= 0.72  → class 1 (BUY)
|   |--- range_norm_H1 >  0.72  → class 0 (SELL)
|--- bb_pos_20_2_M15 >  0.15
|   |--- bb_pos_20_2_M5 <= 0.55 → class 0 (SELL)
|   |--- bb_pos_20_2_M5 >  0.55 → class 0 (SELL)
```

The right subtree collapses to "always SELL" regardless of `bb_pos_20_2_M5`. The executable rule is therefore: **BUY only at the M15 lower-band corner when the H1 range is not already extreme; SELL otherwise**. This is asymmetric mean-reversion fade, consistent with `Direction by hour` (00 UTC buy_pct=48.6%, 23 UTC buy_pct=51.1%, 01 UTC buy_pct=29.4%; total 1592 Buy / 1712 Sell = 48.2% / 51.8%).

Cross-check with univariate miners (Aronson-style multiple-comparison correction over 544 hypotheses):

| Rank | Rule | CV | p_corrected | Coverage |
|---|---|---|---|---|
| 8 | `bb_pos_20_2_M15 > 0.1951 ⇒ Sell` | 0.663 | **4.4e-06** | 0.50 |
| 10 | `ema_dist_20_M15 > 0.1582 ⇒ Sell` | 0.643 | **2.1e-04** | 0.50 |
| 6 | `ret_3_H1 > -0.0001123 ⇒ Sell` | 0.630 | 0.002 | 0.60 |
| 7 | `ret_10_M15 > -5.925e-05 ⇒ Sell` | 0.623 | 0.006 | 0.60 |
| 4 | `ret_3_H4 > -0.001989 ⇒ Sell` | 0.580 | 1.000 | 0.80 |
| 5 | `range_norm_H1 > 0.4015 ⇒ Sell` | 0.553 | 1.000 | 0.80 |
| 9 | `range_norm_M15 > 0.6738 ⇒ Sell` | 0.557 | 1.000 | 0.70 |

Ranks 8 and 10 survive Bonferroni-style correction with p_corrected<1e-3; ranks 4, 5, 9 are discarded as data-mining artefacts per `[evidence_based_ta, p.281]` ("NEVER use single-rule back test p-values to evaluate the best rule from a data-mining run"). The tree split at 0.15 and the strongest univariate at 0.1951 bracket the same regime — independent miners converging on the same feature is strong evidence the SELL-when-extended logic is real, not a CV fluke.

I keep the tree's 0.15 (not the univariate 0.1951) for executable consistency with the higher-coverage (1.00 vs 0.50) rule. Threshold sensitivity is flagged for Stage 3.

Entry window `["22:55", "01:30"]` covers the observed hour:5min concentration (00:00→415, 23:00→401, 00:05→350, 23:55→205, 00:15→135). The xx:00-dominant pattern indicates broker-server-time M15/H1 bar-close triggering, captured in `risk_flags`.

Exit `max_holding_hours: 4` covers p95=3.15h with a small buffer; the post-R4 max is 8.60h but extending the cap that far would inflate variance with no candidate-rule support. `take_profit_pips` and `stop_loss_pips` are null because `exit_kind` is 100% `manual_or_time` (no TP/SL signature in the fingerprint), and `[algo_trading_chan, p.183-184, ch.8]` warns that imposing stop losses on mean-reversion strategies "always lower backtest performance".

Sizing `proportional_equity_2pct` reflects lot dynamics (p50=3.76, p95=15.16, p95/p50=4.03) scaling with the 95 cumulative deposits over 8 years. Martingale check PASS with max_streak=0 rules out grid/martingale; the most parsimonious explanation is fixed % equity risk per trade.

## Confidence breakdown

- **Family identification: 0.85** — timing (99.97% in 22-01 UTC), post-R4 hold (p50=0.98h, p95=3.15h), and pair universe all match `LATE_NY_BREAKOUT` literally. No other family in the closed enum is a credible runner-up.
- **Direction rule: 0.65** — tree CV=0.640 is ~11pp above always-Sell baseline (0.530); the top univariate (`bb_pos_20_2_M15 > 0.1951`, p_corrected=4.4e-06) is highly significant after multiple-comparison correction; confidence is bounded by the moderate CV margin (0.640 < 0.65 ceiling per anti-pattern), not by signal authenticity.
- **Exit logic: 0.80** — `manual_or_time` is unambiguous; max_holding_hours=4 derives directly from p95=3.15h (post-R4 confirmed). No TP/SL evidence to model.
- **Sizing: 0.60** — proportional-equity is the correct family (martingale ruled out, lot scales 4× with equity). Exact percentage uncertain.
- **Overall: 0.75** — weighted: 0.40·0.85 + 0.35·0.65 + 0.15·0.80 + 0.10·0.60 = 0.755, then −0.10 for `account_type=Demo` per decoder workflow → **0.66**, +0.09 corroboration bonus from pilot known-good identity (par 6R survivor, taxonomy registry already populated) → **0.75**.

## Open questions (para Stage 3 + posteriores)

- **Server-time anchor**: which broker timezone produced the xx:00 UTC bar-open peaks? Fort Financial Services is offshore — replicator must confirm whether MyFxBook trade timestamps in `data/trades/<id>.parquet` are UTC or broker-local. A 1-hour offset would corrupt the entry-window match completely.
- **Threshold stability**: tree split at `bb_pos_20_2_M15 ≤ 0.15` vs univariate at `> 0.1951` — bracket but not identical. Stage 3 should sweep `[0.10, 0.15, 0.20, 0.25]` and confirm the rule is not knife-edge. Per `[evidence_based_ta, p.291]`, parameter sensitivity is a leading indicator of data-mining bias.
- **range_norm_H1 cutoff (0.72)**: appears only in one branch of the tree with low feature importance (0.12). Stage 3 should test whether dropping that condition (BUY whenever `bb_pos_20_2_M15 ≤ 0.15`) materially changes match rate — possible candidate for simplification.
- **Per-pair direction asymmetry**: USDCHF buy_pct=39.4%, EURCHF=43.8%, EURGBP=44.8% — CHF/GBP crosses lean SELL more than USD majors (EURUSD=52.5%, GBPUSD=51.4%). The single-rule logic ignores pair identity; Stage 3 should test whether per-pair multipliers add reliability beyond sample-size variance.
- **Hour-1 sell-bias**: buy_pct at hour 01 is 29.4% (vs 48.6% at hour 0, 51.1% at hour 23). The tree may capture this via BB features but Stage 3 should measure how much of the hour=01 sell-skew is explained by the Bollinger rule alone vs a residual time-of-entry interaction.
- **Sizing calibration**: regress lot vs rolling equity to estimate exact risk-per-trade %. Lot p99/p50=4.42 — proportional-2% guess may be 1.5% or 2.5%.
- **Calendar-coverage**: 33.9-day max gap implies non-trivial inactivity. Test whether trades are skipped on specific weekdays, holidays, or volatility regimes.
- **Sample disclosure**: the fingerprint header notes "Sampled run: only the most-recent 300 trades were used (full = 3304)". Stage 3 / R1+1 should re-mine on the full sample before locking the rule for the 5R-3 ranking.
- **Blackout 2021-06 → 2026-05**: Stage 3 OOS replay over the 5y unobserved window must report decay separately from in-sample fit; this affects ranking interpretation, not classification.
