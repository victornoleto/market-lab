# 013-2026-05-10-triple-stack-K4lv25-graded-master — HYPOTHESIS

**Iter:** 013 / 50 (loop)
**Phase:** 3 — performance-first beater hunt (synthesis of iter 010 graded
master ON-blend + iter 012 strict-superset triple stacking)
**Tier:** loop_iter (post-close hunt)
**Slug:** `triple-stack-K4lv25-graded-master`
**n_configs:** 6
**cumulative_n_trials_global before:** 498
**cumulative_n_trials_global after:** 504

## Hypothesis (one sentence)

Triple stacking iter 012's K4_AND_lv25 conditional ON-leg leverage upgrade
(strict-superset Sortino 1.3769 / CAGR 32.50% / crisis 1/4) with iter 010's
graded master-scope ON-blend (gamma=0.25 g25_cashx Sortino 1.4670 / crisis
3/4) on top of the iter 006/007 ratevol-OFF override (CASHX p70) targets
the loop's first **strict-superset config that ALSO rescues 2022_rates** —
preserving the iter 012 strict-superset (`beats_winner=True` AND
`phase3_performance_candidate=True`) while adding the structural
2022-rates rescue mechanism iter 010 g25 demonstrated at single-asset
QLD scope.

## Primary citation

`[risk_parity, p.80-81, ch.4]` Qian RORO (Risk-On / Risk-Off) graded
master-gate — partial weights between full risk-on and full risk-off
during regime transition cells smooth the trade-off between equity
compounding and crisis defense. Iter 010 confirmed this on the
QLD-only ON-leg with gamma=0.25 hitting Sortino 1.4670 (loop max) +
crisis 3/4 (added 2022_rates rescue).

`[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking (secondary
primary) — three mechanically-orthogonal lifts (ON-leg leverage upgrade,
graded ON-blend during ratevol+ON cell, OFF-leg ratevol diversion)
compose additively when their information content is uncorrelated.

## Secondary citations

- `[volatility_trading, p.58-60]` Sinclair vol cone — the ratevol gate
  (ZROZ realised-vol percentile > 70 over 5y) is the trigger for both
  the ON-blend cell AND the OFF-leg diversion.
- `[stocks_on_the_move, p.98]` Clenow trend-strength filter — vote count
  K=4 of 4 is the cleanest "high conviction" signal for the leverage
  upgrade gate.
- `[leverage_for_the_long_run, ch.4-5, p.40-60]` Husson-Trifoni LRS
  leverage scaling — leverage pumps when trend is firm AND vol is low
  (the K4 AND lowvol25 conjunction iter 012 found most-selective).
- `[advances_fin_ml, p.208-211]` CSCV PBO — structural mechanism
  diversity gives clean PBO; iter 013 keeps the iter 012 6-topology
  recipe (gamma sweep introduces 4 mechanism endpoints + 2 ablations).
- `[advances_fin_ml, p.222-223]` DSR cumulative n_trials — global
  trials denominator (n=504 after this iter).
- `[systematic_trading, p.212, ch.13]` Carver semi-automatic re-arm —
  graded master scope is structurally compatible with future re-arm
  hysteresis for 2020 COVID rescue (next iter idea).

## Strategy eligibility checklist (per LOOP_PROTOCOL.md §"Strategy
eligibility checklist")

1. **Citable book/paper:** ✓ primary `[risk_parity, p.80-81, ch.4]` Qian
   RORO graded master + `[risk_parity, ch.5, p.10]` Carlson stacking;
   multiple secondary citations all in `books/summaries/`.
2. **Distinct from `iterations/` (T1-T5 closed study):** ✓ T3 was
   single-asset QLD/ZROZ vote-K=2 only; no graded master scope, no
   conditional leverage upgrade, no ratevol gate. T1c/T1d had alt-OFF
   assets but no leverage scaling and no graded blend. T4 cross-sectional
   ranking does not stack with graded master. The triple stack is novel
   to the closed study.
3. **Distinct from `loop_iterations/` (006-012):** ✓ Iter 010 tested
   graded master with single-asset QLD and basket3 ON-leg (no leverage
   upgrade). Iter 012 tested K4_AND_lv25 leverage upgrade × ratevol-OFF
   (no graded master, no ON-blend cell). The synthesis — graded master
   ON-blend + leverage upgrade + ratevol — is genuinely new.
4. **Data feasibility:** ✓ TQQQSIM, QLDSIM, ZROZSIM, CASHX, IEFSIM,
   SPYSIM all in `data/testfolio/` (used in iter 007/010/011/012).

## Configs (6, gamma sweep + upgrade-selectivity ablation grid)

| # | Name (suffix after `qld_voteK2_sma250_100_vol21_40_ar30_tsgm_`) | upgrade gate | gamma | ratevol gate | alt-OFF | topology |
|---|---|---|---|---|---|---|
| 1 | `baseline_qld_zroz` | (none) | — | (none) | — | none/none/none (replica anchor) |
| 2 | `K4lv25_g0_rvp70_cashx` | K=4 AND lowvol25 | 0.00 | ZROZ vol pct > 70 | CASHX | iter 012 strict-superset replica anchor |
| 3 | `K4lv25_g25_rvp70_cashx` ← **PRIMARY** | K=4 AND lowvol25 | 0.25 | ZROZ vol pct > 70 | CASHX | triple-stack hypothesis test |
| 4 | `K4lv25_g50_rvp70_cashx` | K=4 AND lowvol25 | 0.50 | ZROZ vol pct > 70 | CASHX | gamma sensitivity (mid-blend) |
| 5 | `K4_g25_rvp70_cashx` | K=4 only | 0.25 | ZROZ vol pct > 70 | CASHX | upgrade-selectivity ablation |
| 6 | `K4lv25_g100_rvp70_cashx` | K=4 AND lowvol25 | 1.00 | ZROZ vol pct > 70 | CASHX | gamma upper-bound (master-pure endpoint) |

**6 distinct mechanism topologies in 6 configs.** Configs vary in TWO
controlled dimensions: (a) gamma ∈ {0.00, 0.25, 0.50, 1.00} (4-point
sweep of the iter 010 graded master coefficient) and (b) upgrade gate
selectivity (K4 vs K4_AND_lv25). Slot 5 ablates the lowvol25 conjunct
to test whether the most-selective upgrade is required for the strict-
superset to survive graded-blend dilution. All configs share K=2 entry
signal + sma250/100 + vol21_40 + ar30 + ZROZ default OFF (iter 022
winner architecture).

**Why gamma in {0, 0.25, 0.50, 1.00} (not finer)?** Iter 010 showed
non-monotonic Sortino curve: peak at gamma≈0.25, smooth degradation to
gamma=1.00. A 4-point sweep maps the curve at the iter 010 endpoints
plus the mid-blend. Slot 6's gamma=1.00 endpoint is the iter 009
master-pure replica (under the new triple-stack ON-leg) — provides the
WC failure mode reference (iter 009 master_basket3 had WC=False).

## Datasets

Same as the closed study + iter 005-012: `lh_56y` (1970-01 → 2026-04),
`modern_1990` (1990-01 → 2026-04), `spy_real` (2003-01 → 2026-04),
`ndx_real` (2010-02 → 2026-04). Comparability with the T3d-K2 winner
benchmark requires keeping these windows.

## Pre-registered KILL conditions (loop iter)

- 🏆 **KILL_LOOP #1 (`success_tag`):** any config achieves
  `beats_winner=True` (Sortino_lh56y > 1.3746 AND
  winner_conditions_met=True AND pct_time_above_benchmark_lh56y >= 0.95).
  Loop continues regardless. This iter's design targets g25 + g50 to
  preserve `beats_winner=True` from iter 010.
- **KILL_LOOP #2 (`decisive_fail`):** best Sortino_lh56y < 1.20 (Phase 3
  floor). Hypothesis dead.
- **KILL_LOOP #3 (`replica_sanity_baseline`):** baseline_qld_zroz
  Sortino_lh56y deviates from iter 011/012 calibration baseline 1.3240
  by > 0.005. The iter 011 helper convention (build_conditional_strategy_
  returns) is reused inside the new triple-stack helper for the no-
  upgrade/no-graded/no-ratevol cells, so baseline should match 1.3240.
  FIRES if drift > ±0.005.
- 🎯 **KILL_LOOP #4 (`replica_sanity_g0`):** slot 2 (`K4lv25_g0_rvp70_
  cashx`) Sortino_lh56y deviates from iter 012 K4_AND_lv25_rvp70_cashx
  strict-superset baseline 1.3769 by > 0.005. At gamma=0, the triple
  stack helper must reduce bit-exactly to iter 012's
  `build_compound_strategy_returns` (no ON-blend cell). KEY calibration
  test — confirms the new helper does not silently regress iter 012's
  loop's-first strict-superset.
- 🎯 **KILL_LOOP #5 (`phase3_perf_candidate`):** at least one config
  achieves `phase3_performance_candidate=True` (cagr_lh56y > 0.3108 AND
  end_equity_ratio_vs_baseline > 1.05 AND sortino_lh56y >= 1.20 AND
  G1 PBO < 0.50 AND G2 DSR_global < 0.05). Positive tag — Phase 3
  momentum continues (iter 011 5/6, iter 012 5/6).
- **KILL_LOOP #6 (`PBO_blowup`):** G1 PBO >= 0.55 (regression vs iter
  011's loop-min 0.3056). Iter 012 was 0.4960. Triple stack with gamma
  sweep introduces parametric variants — risk of further PBO regression.
- 🎯 **KILL_LOOP #7 (`graded_lifts_strict_superset`):** any g>0 config
  achieves `strict_superset=True`. The KEY hypothesis test — does adding
  the graded ON-blend preserve (or lift) iter 012 strict-superset while
  adding 2022_rates rescue? Positive tag if any of slots 3/4/6 hits
  `strict_superset=True`.
- 🎯 **KILL_LOOP #8 (`crisis_2022_rescue`):** at least one config beats
  SPY in the 2022_rates window (per `crisis_beats_benchmark`). Positive
  tag — confirms graded master ON-blend rescues 2022 even when composed
  with leverage upgrade. Iter 012 had 1/4 across all configs; iter 010
  g25/g50 had 3/4 (added 2022). Expected: slot 3 g25, slot 4 g50, slot 6
  g100 hit 2022; slot 2 g0 stays at 1/4 (calibration anchor, no ON-blend
  cell).
- 🎯 **KILL_LOOP #9 (`graded_score_lift`):** any g>0 config achieves
  `total_score >= 80`. Iter 012 strict-superset hit 76.5; adding crisis
  rescue (criterion 6 +5pts via 2/4 → 3/4 jump) should lift score above
  80, potentially toward 85. Positive tag if iter 013 produces the
  loop's first score >= 80 + strict_superset combination.

## Expected outcomes

### Sortino_lh56y range (lh_56y)

- baseline_qld_zroz: ~1.3240 (iter 011/012 calibration baseline; replica
  anchor, KILL_LOOP #3 sanity)
- K4lv25_g0_rvp70_cashx: ~1.3769 (iter 012 strict-superset replica anchor;
  KILL_LOOP #4 sanity)
- **K4lv25_g25_rvp70_cashx**: **~1.40-1.50 expected** (strongest Phase 3
  prediction — graded ON-blend lifts Sortino per iter 010 g25 dynamic;
  K4_AND_lv25 leverage gate preserved; ratevol-OFF preserved). Conservative:
  ~1.35-1.40 if leverage upgrade dilutes iter 010 g25 dynamic. Optimistic:
  ~1.50 if mechanisms compound super-additively.
- K4lv25_g50_rvp70_cashx: ~1.35-1.45 (iter 010 g50 was -0.0099 vs g25;
  expect similar relative dip with K4_AND_lv25 upgrade)
- K4_g25_rvp70_cashx: ~1.30-1.40 (looser upgrade may dilute graded gain;
  iter 011 K4-only Sortino was 1.2911 vs K4_AND_lv25 1.3247 = -0.034
  selectivity gap)
- K4lv25_g100_rvp70_cashx: ~1.30-1.40 (iter 010 master-pure had
  WC=False; expected to fail beats_winner here too)

### CAGR_lh56y and gap vs T3d-K2 31.08%

- baseline_qld_zroz: 0.3108 (T3d-K2 replica)
- K4lv25_g0_rvp70_cashx: 0.3250 (+1.42pp; iter 012 strict-superset replica)
- K4lv25_g25_rvp70_cashx: **0.30-0.33 expected** — graded ON-blend
  trades equity-bull return for ratevol+ON cell defense; expect 1-2pp
  CAGR drop vs g0 anchor. Could land just above 31.08% (Phase 3 floor)
  or just below (depends on the graded-blend cell hit rate × magnitude).
- K4lv25_g50_rvp70_cashx: ~0.29-0.31 (more graded dilution)
- K4_g25_rvp70_cashx: ~0.30-0.32 (looser upgrade preserves more TQQQ
  exposure; offsets some graded dilution)
- K4lv25_g100_rvp70_cashx: ~0.27-0.29 (master-pure dilutes most)

### Terminal equity ratio vs baseline (Phase 3 floor 1.05)

- All g>0 configs expected end_equity_ratio_vs_baseline in [1.0, 1.5]
  range. The strict-superset prediction requires > 1.05; the iter 010
  g25_cashx single-asset baseline was 1.27× of iter 010 baseline. With
  the K4_AND_lv25 leverage amplifier, expect 1.10-1.40×.

### Rolling-window win rates vs baseline (1y/3y/5y/10y)

Should resemble iter 012 K4_AND_lv25 (~45-50% across windows), with
modest improvement on rolling windows that include 2022_rates regime
due to graded master rescue.

### Phase 3 + beats_winner co-condition (strict_superset goal)

For a config to be the loop's second strict-superset:

```
sortino_lh56y > 1.3746            # +0.05 anti-curve-fit margin over T3d-K2
AND winner_conditions_met = True
AND pct_time_above_benchmark_lh56y >= 0.95
AND cagr_lh56y > 0.3108
AND end_equity_ratio_vs_baseline > 1.05
AND g1_pbo < 0.50
AND g2_dsr_p_cumulative < 0.05    # n_trials_global = 504
```

This iter's PRIMARY (slot 3 K4lv25_g25_rvp70_cashx) is the highest-
expected-value strict-superset path AND adds 2022_rates rescue. Risk:
graded blend cell can erode the CAGR floor (+1.42pp margin in iter 012
is thin). g50 and g100 configs are diagnostic — they map the gamma
sensitivity even if they fail the strict bar.

## INCOMPLETE flags / caveats

- **TQQQSIM synth caveat (pre-1985):** testfolio synthetic proxy from
  NDX × 3 daily-rebal × FFR borrow. Conditional-leverage primitive is
  binary state machine, robust to absolute-level synth miscalibration
  via state quantisation.
- **CASHX warmup**: pre-1971 fed funds data sparse;
  `data_loader.load_testfolio_series('CASHX')` handles this. lh_56y
  start 1970-01 may have CASHX NaN for first ~30 days.
- **5y warmup for ratevol**: pct_window = 1260 trading days = ~5y. Falls
  back to baseline ZROZ pre-warmup. Affects ~5% of lh_56y span.
- **5y warmup for lowvol25 upgrade gate (slots 2-4, 6)**: same
  convention. Slot 6 has compound 5y warmup (max of K=4 250d + lowvol25
  1260d + ratevol 1260d).
- **Cross-iter baseline drift**: iter 011/012 baseline_qld_zroz Sortino
  1.3240 is the canonical T3d-K2 replica reference. Iter 013 reuses
  iter 011 helper for warmup/baseline cells; expected drift < 0.005.
- **Cross-iter g0 sanity**: slot 2 K4lv25_g0_rvp70_cashx must reduce
  bit-exactly to iter 012's strict-superset config when ON-blend cell
  is disabled (gamma=0). Tested via KILL_LOOP #4.
- **DSR p_value reported**: local (n=6) is diagnostic only; cumulative
  DSR (n_trials_global = 504) is the canonical denominator per
  `[advances_fin_ml, p.222-223]` and LOOP_PROTOCOL §"Trial accounting".
- **Graded master ON-blend semantics**: the cell value is gamma *
  alt_off_returns + (1-gamma) * on_leg_returns where on_leg_returns is
  TQQQ when upgrade gate fires else QLD. This is the natural extension
  of iter 010's graded helper to the upgrade-gated ON-leg.
- **Crisis attribution**: slot 1 (no mechanisms) and slot 2 (no graded
  blend) expected 1/4 (only 2008 GFC, mirroring iter 011/012). Slots 3,
  4, 6 (g>0) expected 3/4 (+2022 rates) per iter 010 g25/g50/g100
  precedent. Slot 5 (looser upgrade with g25) expected 3/4.
- **Mandate §1 invariant**: even if a strict-superset config is found
  with score >= 80 (KILL_LOOP #9 fires), capital remains 100% Plan C.
  Score >= 90 deploy bar is still gated on Sharpe_net edge +0.15
  (KILL_RULES.md DEPLOY) AND mandate §7 user-driven override. NO
  automatic capital realloc.

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

`strict_superset` was hit for the first time by iter 012's
K4_AND_lv25_rvp70_cashx. Iter 013 PRIMARY (slot 3) is the highest-
probability path to a SECOND strict-superset that ALSO clears
KILL_LOOP #8 (2022_rates rescue) AND KILL_LOOP #9 (score >= 80).
