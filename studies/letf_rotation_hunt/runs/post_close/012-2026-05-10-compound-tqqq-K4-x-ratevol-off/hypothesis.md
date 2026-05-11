# 012-2026-05-10-compound-tqqq-K4-x-ratevol-off — HYPOTHESIS

**Iter:** 012 / 50 (loop)
**Phase:** 3 — performance-first beater hunt (compound iter 011 × iter 007)
**Tier:** loop_iter (post-close hunt)
**Slug:** `compound-tqqq-K4-x-ratevol-off`
**n_configs:** 6
**cumulative_n_trials_global before:** 492
**cumulative_n_trials_global after:** 498

## Hypothesis (one sentence)

Stacking iter 011's conditional TQQQ K=4 leverage upgrade (CAGR
amplifier on the ON leg) with iter 006/007's ratevol-OFF override
(CASHX/IEFSIM diversion when ZROZ vol percentile > p70) produces a
strict-superset Phase 3 candidate that simultaneously (a) lifts CAGR
above T3d-K2 31.08% via TQQQ during high-conviction risk-on regimes
AND (b) rescues 2022_rates by replacing duration with cash/short-bond
when bond vol regime is hostile, plausibly clearing both
`phase3_performance_candidate=True` AND `beats_winner=True` for the
first time in the loop.

## Primary citation

`[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking — independent
mechanically-orthogonal lifts compound additively when their information
content is uncorrelated. The TQQQ-leverage axis (ON-leg amplification
during equity-bull regimes) is structurally orthogonal to the
ratevol-OFF axis (OFF-leg diversion during bond-bear regimes) — they
operate on disjoint state cells and target different crisis regimes
(2008 GFC stays defensive; 2022 rates gets rescued; 2020 COVID
unaddressed by either; 2000 dotcom unaddressed by either).

## Secondary citations

- `[volatility_trading, p.58-60]` Sinclair vol cone — applied to the
  ratevol gate (ZROZ realised-vol percentile > p70/p80 over trailing 5y)
  AND validates the iter 011 lowvol25 upgrade gate (low percentile =
  pump leverage regime; high bond percentile = retreat from duration).
- `[stocks_on_the_move, p.98]` Clenow trend-strength filter — vote count
  = 4 of 4 is the cleanest "high conviction" signal for the upgrade gate.
- `[leverage_for_the_long_run, ch.4-5, p.40-60]` Husson-Trifoni LRS
  leverage scaling — leverage pumps when trend is firm AND vol is low.
- `[advances_fin_ml, p.208-211]` CSCV PBO via combinatorially-symmetric
  cross-validation — structural mechanism diversity gives clean PBO.
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials — global
  trials denominator (n=498 after this iter).

## Strategy eligibility checklist (per LOOP_PROTOCOL.md §"Strategy
eligibility checklist")

1. **Citable book/paper:** ✓ primary `[risk_parity, ch.5, p.10]` Carlson
   stacking; multiple secondary citations all in `books/summaries/`.
2. **Distinct from `runs/original/` (T1-T5 closed study):** ✓ T3 was
   single-asset QLD/ZROZ vote-K=2 only; no compound TQQQ-leverage ×
   ratevol-OFF override. T1c/T1d had alt-OFF assets but no leverage
   scaling. T4 cross-sectional ranking does not stack with OFF override.
3. **Distinct from `runs/post_close/` (006-011):** ✓ Iter 006 was
   single-asset ratevol-only with QLD baseline (no leverage upgrade).
   Iter 007 was multi-asset basket (QLD/UPRO/UGL invvol) × ratevol —
   uses basket sizing, NOT leverage upgrade. Iter 011 was conditional
   TQQQ leverage with ZROZ-only OFF leg (no ratevol). The compound is
   genuinely novel — first time leverage upgrade and ratevol override
   are stacked.
4. **Data feasibility:** ✓ TQQQSIM, QLDSIM, ZROZSIM, CASHX, IEFSIM,
   SPYSIM all in `data/testfolio/` (used in iter 007 and iter 011).

## Configs (6, mechanism-mix structural-diversity grid)

| # | Name (suffix after `qld_voteK2_sma250_100_vol21_40_ar30_clegrv_`) | upgrade gate | ratevol gate | alt-OFF | topology |
|---|---|---|---|---|---|
| 1 | `baseline_qld_zroz` | (none) | (none) | — | none/none (replica anchor) |
| 2 | `tqqq_K4_zroz` | K=4 of 4 | (none) | — | leverage-only (iter 011 K4 anchor) |
| 3 | `tqqq_K4_rvp70_cashx` ← **PRIMARY** | K=4 of 4 | ZROZ vol pct > 70 | CASHX | leverage × ratevol-CASHX |
| 4 | `tqqq_K4_rvp70_ief` | K=4 of 4 | ZROZ vol pct > 70 | IEFSIM | leverage × ratevol-IEF |
| 5 | `tqqq_K4_rvp80_cashx` | K=4 of 4 | ZROZ vol pct > 80 | CASHX | leverage × stricter ratevol |
| 6 | `tqqq_K4_AND_lv25_rvp70_cashx` | K=4 AND vol_21d<25th pct 5y | ZROZ vol pct > 70 | CASHX | most-selective leverage × ratevol |

**6 distinct mechanism topologies in 6 configs** — preserves the iter
011 structural-diversity recipe (loop minimum PBO 0.3056). Configs vary
in EXACTLY ONE dimension at a time (anchor / +leverage / +ratevol
threshold / alt-OFF asset / upgrade gate selectivity). All configs share
K=2 entry signal (vote ≥ 2 of 4) per iter 022 winner replica.

**Why K=4 (not the iter 011 AND or OR variants) for slots 3-5?** Iter 011
showed `tqqq_K4` is the best Sortino-vs-CAGR trade-off among non-AND
configs (Sortino 1.2911, CAGR 32.36% +1.28pp, end_eq 1.48× — see
SUMMARY.md "Comparação vs winner"). Slot 6 tests whether the most
selective AND gate compounds even better with ratevol.

## Datasets

Same as the closed study + iter 005-011: `lh_56y` (1970-01 → 2026-04),
`modern_1990` (1990-01 → 2026-04), `spy_real` (2003-01 → 2026-04),
`ndx_real` (2010-02 → 2026-04). Comparability with the T3d-K2 winner
benchmark requires keeping these windows.

## Pre-registered KILL conditions (loop iter)

- **KILL_LOOP #1 (`success_tag`):** any config achieves
  `beats_winner=True` (Sortino_lh56y > 1.3746 AND
  winner_conditions_met=True AND pct_time_above_benchmark_lh56y >= 0.95).
  Loop continues regardless. Phase 3 explicitly seeks this co-condition
  with phase3_performance_candidate.
- **KILL_LOOP #2 (`decisive_fail`):** best Sortino_lh56y < 1.20 (Phase 3
  floor — compound stack fails to preserve Sortino). Hypothesis dead.
- **KILL_LOOP #3 (`replica_sanity_baseline`):** baseline_qld_zroz
  Sortino_lh56y deviates from the iter 011 calibration baseline 1.3240
  by > 0.005. Per iter 011 KILL_LOOP #3 disclosure, this iter's helper
  reuses the iter 011 `build_conditional_strategy_returns` convention,
  so baseline should match the iter 011 baseline 1.3240, NOT the iter
  001-010 1.2841 (alignment artifact in iter 007's
  `build_compound_strategy_returns`). FIRES if drift > ±0.005 vs 1.3240.
- 🎯 **KILL_LOOP #4 (`phase3_perf_candidate`):** at least one config
  achieves `phase3_performance_candidate=True` (cagr_lh56y > 0.3108 AND
  end_equity_ratio_vs_baseline > 1.05 AND sortino_lh56y >= 1.20 AND
  G1 PBO < 0.50 AND G2 DSR_global < 0.05). Positive tag — Phase 3
  objective continues to be hit.
- **KILL_LOOP #5 (`PBO_blowup`):** G1 PBO >= 0.55 (regression vs iter
  011's loop-min 0.3056). 6-topology grid is intentionally diverse to
  preserve the loop-min PBO trajectory.
- **KILL_LOOP #6 (`compound_collapse`):** any compound config (slots
  3-6) Sortino_lh56y < `tqqq_K4_zroz` Sortino - 0.05. Tests whether
  adding ratevol HURTS the iter 011 K4 anchor by more than 0.05 Sortino
  drop. Hypothesis premise (compounding lifts the anchor) dead if fired.
- 🎯 **KILL_LOOP #7 (`strict_superset`):** any compound config achieves
  BOTH `beats_winner=True` AND `phase3_performance_candidate=True`. The
  strict-superset goal — never achieved in the loop. Positive tag if
  fired (loop's first strict-superset config).
- **KILL_LOOP #8 (`crisis_2022_rescue`):** at least one compound config
  beats SPY in the 2022_rates window (per `crisis_beats_benchmark`).
  Positive tag — confirms the ratevol mechanism rescues 2022 even when
  composed with TQQQ leverage upgrade. Iter 011 had crisis 1/4 across
  all configs (only 2008 GFC); compound ratevol rescue should lift to
  2/4 (+2022 rates) per iter 007 precedent.

## Expected outcomes

### Sortino_lh56y range (lh_56y)

- baseline_qld_zroz: ~1.32 (iter 011 calibration baseline)
- tqqq_K4_zroz: ~1.29 (iter 011 K4 figure)
- tqqq_K4_rvp70_cashx: **~1.30-1.40 expected** (TQQQ amplifier preserved
  + ratevol rescue; Sortino lift mechanism is similar to iter 007's
  basket3_x_ratevol_p70_cashx Sortino 1.4068 vs basket3_only 1.3340)
- tqqq_K4_rvp70_ief: ~1.30-1.40 (alt-OFF variant; iter 007 IEF version
  was Sortino ~1.40 too)
- tqqq_K4_rvp80_cashx: ~1.30-1.40 (stricter threshold = less ratevol
  activation; smaller crisis rescue but cleaner Sortino)
- tqqq_K4_AND_lv25_rvp70_cashx: **~1.35-1.45 expected** (most selective
  upgrade preserves Sortino best per iter 011 AND result of 1.3247;
  compound with ratevol may lift further)

### CAGR_lh56y and gap vs T3d-K2 31.08%

- baseline_qld_zroz: 0.3108 (T3d-K2 replica)
- tqqq_K4_zroz: ~0.3236 (+1.28pp; iter 011 K4 figure)
- tqqq_K4_rvp70_cashx: **0.32-0.35 expected (+1.0pp to +4.0pp)** —
  TQQQ lift preserved; ratevol activation (~28% of OFF-state days)
  trades minor return for crisis rescue
- tqqq_K4_rvp80_cashx: closer to ~0.33 (less ratevol, more ZROZ
  carry retained)
- tqqq_K4_AND_lv25_rvp70_cashx: ~0.32 (smaller TQQQ exposure)

### Terminal equity ratio vs baseline (Phase 3 floor 1.05)

- All compound configs expected end_equity_ratio_vs_baseline > 1.10,
  ideally > 1.20 for K4_zroz (iter 011 1.48×).

### Rolling-window win rates vs baseline (1y/3y/5y/10y)

Should resemble iter 011 K4: ~45-55% win-rate across windows. Compound
with ratevol may lift the 2022-2024 segment specifically (the rolling
windows that include the 2022 rate-vol regime).

### Phase 3 + beats_winner co-condition

For a compound config to be the loop's first strict-superset:

```
sortino_lh56y > 1.3746            # +0.05 anti-curve-fit margin over T3d-K2
AND winner_conditions_met = True
AND pct_time_above_benchmark_lh56y >= 0.95
AND cagr_lh56y > 0.3108
AND end_equity_ratio_vs_baseline > 1.05
AND g1_pbo < 0.50
AND g2_dsr_p_cumulative < 0.05    # n_trials_global = 498
```

This is the bar iter 011 missed (Sortino 1.3247 < 1.3746 by 0.05) and
iter 010 missed in the opposite direction (Sortino 1.4670 ✓ but CAGR
below T3d-K2). The compound stack is the highest-probability path.

## INCOMPLETE flags / caveats

- **TQQQSIM synth caveat (pre-1985):** testfolio synthetic proxy
  reconstructed from NDX returns × 3 × daily-rebal × FFR borrow.
  Conditional-leverage primitive is a binary state machine, robust to
  absolute-level synth miscalibration via state quantisation.
- **CASHX warmup**: pre-1971 fed funds rate data is sparse;
  `data_loader.load_testfolio_series('CASHX')` handles this. lh_56y
  start 1970-01 may have CASHX NaN for first ~30 days.
- **5y warmup for ratevol**: pct_window = 1260 trading days = ~5y.
  ratevol fires NaN for ~5y of warmup; per iter 007 convention, this
  falls back to baseline ZROZ (no override). Affects ~5% of lh_56y
  span (1970-1975).
- **5y warmup for lowvol25 upgrade gate (slot 6)**: same convention —
  upgrade NaN → no upgrade (baseline QLD). Slot 6 has compound 5y
  warmup (max of K=4 250d + lowvol25 1260d + ratevol 1260d).
- **Cross-iter baseline drift**: per iter 011 KILL_LOOP #3 disclosure,
  iter 011's `build_conditional_strategy_returns` produces baseline
  Sortino 1.3240 (matches T3d-K2 official 1.3246 to 4 decimals); iter
  001-010 baseline 1.2841 was an iter 007 alignment artifact. **Iter
  012 reuses iter 011's helper as the canonical baseline reference.**
  Sanity replica vs iter 011 baseline expected drift < 0.005.
- **DSR p_value reported**: local (n=6) is diagnostic only;
  cumulative DSR (n_trials_global = 498) is the canonical denominator
  per `[advances_fin_ml, p.222-223]` and LOOP_PROTOCOL §"Trial
  accounting".
- **Phase 3 strict bar uses `end_equity_ratio_vs_baseline_qld`** (this
  iter's baseline replica), not vs the iter 022 official series (not
  loaded in this iter's pipeline). Per iter 011 convention; the
  baseline replica matches T3d-K2 official to 4 decimals on Sortino
  and exactly on CAGR.
- **Crisis attribution unchanged for slots 1-2** (no ratevol → 1/4 like
  iter 011 K4). Slots 3-6 expected 2/4 (+2022 rates rescue) per iter
  007 ratevol precedent.
- **Mandate §1 invariant**: even if a strict-superset config is found,
  capital remains 100% Plan C. Score 76.5 < 90 deploy bar likely
  unchanged (even with crisis rescue +5pts → score 81.5; deploy
  requires score ≥ 90 + WC=Y + beats_winner=true + user-driven mandate
  §7 override). NO automatic capital realloc.

## Comparison plan vs winner

For each config, compute:

```python
sortino_edge_vs_winner = sortino_lh56y - 1.3246
cagr_edge_vs_winner = cagr_lh56y - 0.3108
end_equity_ratio_vs_baseline = candidate_end_equity / baseline_end_equity
rolling_win_rates_vs_baseline = {"1y": ..., "3y": ..., "5y": ..., "10y": ...}

beats_winner = (
    sortino_lh56y > 1.3746
    and winner_conditions_met
    and pct_time_above_benchmark_lh56y >= 0.95
)

phase3_performance_candidate = (
    cagr_lh56y > 0.3108
    and end_equity_ratio_vs_baseline > 1.05
    and sortino_lh56y >= 1.20
    and g1_pbo < 0.50
    and g2_dsr_p_cumulative < 0.05
)

strict_superset = beats_winner and phase3_performance_candidate
```

`strict_superset` is the headline metric this iter targets — never
achieved in the loop's first 11 iters. KILL_LOOP #7 fires positively
if any config hits it.
