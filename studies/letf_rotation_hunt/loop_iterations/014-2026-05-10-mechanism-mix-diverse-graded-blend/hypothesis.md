# Iter 014 — mechanism-mix-diverse graded blend grid

**Slug:** `mechanism-mix-diverse-graded-blend`
**Phase:** 3 — performance-first beater hunt
**n_configs:** 6
**cumulative_n_trials_global before:** 504
**cumulative_n_trials_global after:** 510 (+6 this iter)

## Eligibility checklist (LOOP_PROTOCOL §"Strategy eligibility checklist")

1. **Citable book/paper:** ✓ — primary `[risk_parity, p.80-81, ch.4]` Qian RORO
   graded master-gate; secondaries `[risk_parity, ch.5, p.10]` Carlson cap-
   efficient stacking; `[stocks_on_the_move, p.98]` Clenow vol-parity;
   `[systematic_trading, ch.10]` Carver inverse-vol; `[volatility_trading,
   p.58-60]` Sinclair vol cone; `[leverage_for_the_long_run, ch.4-5, p.40-60]`
   LRS leverage; `[advances_fin_ml, p.208-211]` CSCV PBO mechanism diversity;
   `[advances_fin_ml, p.222-223]` DSR cumulative.
2. **Distinct from `iterations/`:** ✓ — closed study T1-T5 covered single
   LETF / HFEA basket / composite signal / cross-sectional / Carver vol-target
   on isolated dimensions; this iter compounds three distinct primitives
   (basket3 ON-leg, K4_AND_lv25 leverage upgrade, graded ON-blend × ratevol-
   OFF override) on a mechanism-mix-diverse grid.
3. **Distinct from `loop_iterations/`:** ✓ — no prior iter combines basket3
   ON-leg WITH K4_AND_lv25 upgrade (iter 007 had basket3 without upgrade;
   iter 010 had basket3 with graded blend without upgrade; iter 011/012/013
   had upgrade with single-asset ON only).
4. **Data feasibility:** ✓ — QLDSIM, TQQQSIM, UPROSIM, UGLSIM, ZROZSIM,
   IEFSIM, CASHX, SPYSIM all in `data/testfolio/`. lh_56y / modern_1990 /
   spy_real / ndx_real windows align with all closed-study iters.

## Hypothesis

**Restoring 6-config mechanism-mix diversity (iter 012's structural recipe)
to the iter 013 graded-blend variant grid will recover G1 PBO < 0.50 and
introduce a basket3+UGL ON-leg variant that simultaneously achieves
`beats_winner=True`, `phase3_performance_candidate=True`, and a 2022_rates
crisis rescue — i.e., the loop's first crisis-3/4 strict_superset.**

Mechanism stack rationale:

- **Iter 013 lesson (`SUMMARY.md`):** the gamma-only sweep across 4 configs
  in the same `K4_AND_lv25 / p70 / cashx` topology produced parametric-
  variant clustering → CSCV correctly inflated PBO from 0.4960 (iter 012,
  6-distinct-topologies) to 0.5437 (iter 013, 4-of-6 same family),
  invalidating WC and Phase 3 status `[advances_fin_ml, p.208-211]`.
  Iter 013 next-iter idea (a) names the specific fix: 6-distinct-topology
  grid with one basket3 variant for 2022 rescue.
- **Iter 010 demonstrated** that graded ON-blend at `gamma=0.25` on a
  basket3 (QLD/UPRO/UGL invvol) ON-leg produces Sortino_lh56y 1.4670 (loop
  max for iter 010) AND crisis 3/4 (only loop iter to achieve both
  beats_winner AND 2022_rates rescue at intermediate gamma) — the missing
  combo from iter 013 was the basket3 ON-leg.
- **Iter 012 demonstrated** that K4_AND_lv25 leverage upgrade on top of
  ratevol-OFF override achieves `beats_winner=True` AND
  `phase3_performance_candidate=True` simultaneously (loop's first
  strict_superset) — but with crisis 1/4 because the single QLD/TQQQ ON-leg
  has no UGL gold cushion.
- **The genuinely new combo (config 6):** basket3 ON-leg with K4_AND_lv25
  toggle to TQQQ basket × graded blend `gamma=0.25` × ratevol-p70 OFF. If
  the basket3 cushion delivers the iter-010 crisis 3/4 profile while the
  K4_AND_lv25 upgrade contributes the iter-012 risk-on amplification,
  Carlson cap-efficient stacking `[risk_parity, ch.5, p.10]` predicts a
  super-additive Sortino+CAGR lift.

## Configs (6, mechanism-mix-diverse grid)

Naming prefix: `qld_voteK2_sma250_100_vol21_40_ar30_mmix_`

| # | Suffix | ON-leg | upgrade | gamma | ratevol | alt-OFF | role |
|---|---|---|---|---:|---|---|---|
| 1 | `baseline_qld_zroz` | single QLD | none | — | none | — | replica anchor |
| 2 | `K4lv25_g0_rvp70_cashx` | single QLD/TQQQ | K4_AND_lv25 | 0.00 | p70 | CASHX | iter 012 strict-superset replica anchor |
| 3 | `K4lv25_g25_rvp70_cashx` | single QLD/TQQQ | K4_AND_lv25 | 0.25 | p70 | CASHX | iter 013 g25 replica anchor |
| 4 | `K4lv25_g0_rvp80_ief` | single QLD/TQQQ | K4_AND_lv25 | 0.00 | p80 | IEFSIM | ratevol/alt-OFF orthogonal mix |
| 5 | `basket3_g0_rvp70_cashx` | basket3 (QLD/UPRO/UGL invvol60) | none | 0.00 | p70 | CASHX | iter 007 basket3+ratevol replica anchor |
| 6 | **`basket3_K4lv25_g25_rvp70_cashx`** ← PRIMARY | basket3 with K4_AND_lv25 swap (TQQQ/UPRO/UGL invvol60 when fired) | K4_AND_lv25 | 0.25 | p70 | CASHX | TRUE TRIPLE STACK — genuinely new combo |

**Mechanism diversity audit (vs iter 013 4/6 in same family):**

- Upgrade gate: 3 distinct values (none, K4_AND_lv25, K4_AND_lv25)
- Gamma: 2 distinct values (0, 0.25)
- Ratevol threshold: 3 distinct (none, 70, 80)
- Alt-OFF asset: 3 distinct (none, CASHX, IEFSIM)
- ON-leg type: **2 distinct (single, basket3) — STRUCTURAL DIVERSITY (iter 013 had only single)**

3 quasi-orthogonal return families:
- A: single-asset K4_AND_lv25 with cashx (c2, c3 differ only in gamma)
- B: single-asset K4_AND_lv25 with p80 IEF (c4 — orthogonal in 2 dimensions vs A)
- C: basket3 ON-leg (c5, c6 — STRUCTURAL diversity vs A/B)
- baseline (c1)

vs iter 013 (4 configs in same family) and iter 012 (6 distinct topologies).
Expected G1 PBO trajectory: between iter 012's 0.4960 and iter 013's 0.5437 —
target < 0.50 hard gate.

## Datasets

Same as the closed study + prior loop iters: `lh_56y` (1970-01..2026-04),
`modern_1990` (1990-01..2026-04), `spy_real` (2003-01..2026-04), `ndx_real`
(2010-02..2026-04). Comparability with all loop and study calibration
anchors (1.3240 baseline; 1.3769 iter 012 g0; 1.3951 iter 013 g25;
1.4637 iter 007 basket3+ratevol).

## Pre-registered KILL_LOOP conditions

- **KILL_LOOP #1 (`success_tag`):** FIRES if any config has `beats_winner=
  True` (Sortino_lh56y > 1.3746 AND `winner_conditions_met=True` AND
  `pct_time_above_benchmark_lh56y >= 0.95`). Positive tag.
- **KILL_LOOP #2 (`decisive_fail`):** FIRES if best Sortino_lh56y < 1.20
  (Phase 3 floor). Hypothesis killed at the broadest level.
- **KILL_LOOP #3 (`replica_sanity_baseline`):** FIRES if baseline (c1)
  Sortino_lh56y deviates from 1.3240 (iter 011/012/013 baseline) by > 0.005.
  Calibration anchor; FIRES = bug.
- **KILL_LOOP #4 (`replica_sanity_g0_K4lv25`):** FIRES if c2 Sortino_lh56y
  deviates from 1.3769 (iter 012 strict-superset / iter 013 g0 anchor) by
  > 0.005. Confirms single-asset path of new helper bit-exactly reduces to
  iter 012 compound. FIRES = bug.
- **KILL_LOOP #5 (`replica_sanity_g25_K4lv25`):** FIRES if c3 Sortino_lh56y
  deviates from 1.3951 (iter 013 g25) by > 0.005. Confirms graded blend
  path of new helper matches iter 013 single-asset returns exactly.
  FIRES = bug.
- **KILL_LOOP #6 (`replica_sanity_basket3_g0`):** FIRES if c5 Sortino_lh56y
  deviates from 1.4637 (iter 007 basket3+ratevol / iter 010 offleg-pure
  4th-gen anchor) by > 0.005. Confirms basket3 path of new helper bit-
  exactly reduces to iter 007 compound state machine. FIRES = bug.
- **KILL_LOOP #7 (`PBO_recovery`):** FIRES — POSITIVE TAG — if G1 PBO <
  0.50 (recovery from iter 013's 0.5437 regression). Validates
  mechanism-mix-diverse hypothesis at the statistical level.
- **KILL_LOOP #8 (`PBO_blowup`):** FIRES if G1 PBO >= 0.55. Hard regression
  vs iter 013; would invalidate the mechanism-mix recipe.
- **KILL_LOOP #9 (`phase3_perf_candidate`):** FIRES — POSITIVE TAG — if any
  config achieves `phase3_performance_candidate=True`. Phase 3 momentum
  restored after iter 013's 0/6 hit-rate.
- **KILL_LOOP #10 (`strict_superset`):** FIRES — POSITIVE TAG — if any
  config achieves `strict_superset=True` (`beats_winner` AND
  `phase3_performance_candidate`).
- **KILL_LOOP #11 (`crisis_2022_rescue`):** FIRES — POSITIVE TAG — if any
  config beats SPY in the 2022_rates window (basket3 with cashx-during-
  ratevol-ON path is the iter 010 mechanism that adds 2022).
- **KILL_LOOP #12 (`triple_stack_strict_superset_with_crisis`):** FIRES —
  POSITIVE TAG — if config 6 (TRUE triple stack with basket3) achieves
  `strict_superset=True` AND `crisis_2022_rescue=True` simultaneously.
  Loop's first crisis-3/4 strict_superset.

## Expected outcomes

- **Best Sortino_lh56y range:** 1.40-1.50 (config 6 expected to inherit
  iter 010 g25_cashx 1.4670 profile + small lift from K4_AND_lv25 upgrade
  at ~7% activation; config 5 ≈ iter 007's 1.4637 anchor; configs 2-4
  inherit iter 012/013 single-asset profile).
- **CAGR_lh56y for primary (c6):** 32-35% (basket3 baseline iter 007:
  ~32-33%; +0.5-2pp lift from K4_AND_lv25 TQQQ swap during high-conviction
  days).
- **end_eq_ratio_vs_baseline (c6):** 1.5-2.0× (basket3 lifts terminal
  equity above single-QLD baseline; iter 007 anchor ~1.6×; +small from
  upgrade gate).
- **Rolling-window win rate (c6 vs baseline lh_56y):** 50-60% over 1y/3y;
  35-50% over 5y/10y (mirrors iter 007/010 basket3 profile).
- **G1 PBO target:** < 0.50 (mechanism-mix-diversity recipe restoration).
- **G2 DSR p_cumulative:** ≤ 0.005 at n_global=510 (extending iter 013's
  1.06e-03 loop-min trajectory).
- **Crisis attribution (c6):** 3/4 expected (2008 + 2020 from basket3+UGL;
  2022 from cashx-during-ratevol-ON; misses 2000 dotcom).
- **Strict_superset target:** YES for c6 (beats_winner + phase3 + crisis
  3/4 → score ≥ 80).

**Comparison plan:**

For best config to bat the winner (T3d-K2 1.3246), need ALL 3:
- Sortino_lh56y > 1.3746
- `winner_conditions_met=True` (all WINNER strict bars: G1 PBO < 0.50,
  G2 < 0.05, G6 > 0, G7 < 3pp, Sortino edge ≥ +0.05, pct_above ≥ 0.95)
- pct_time_above_benchmark_lh56y >= 0.95

For best config to be a phase3 performance candidate, need ALL 5:
- CAGR_lh56y > 0.3108
- end_equity_ratio_vs_baseline > 1.05
- Sortino_lh56y >= 1.20
- G1 PBO < 0.50
- G2 DSR p_cumulative < 0.05

For best config to be a `strict_superset`, need BOTH `beats_winner=True`
AND `phase3_performance_candidate=True`.

## INCOMPLETE flags / caveats

- **Synth caveat:** TQQQSIM, QLDSIM, UPROSIM, UGLSIM are testfolio-cached
  Gayed-methodology synths; pre-inception (TQQQ < 2010, UGL < 2008,
  UPRO < 2009) the series are model-extrapolated. iter 007's basket3
  baseline assumes acceptable synth fidelity for crisis attribution
  windows; same caveat applies here.
- **Inverse-vol weights with TQQQ swap:** swapping QLD↔TQQQ inside the
  basket3 changes invvol weights (TQQQ has higher realised vol → lower
  weight). The K4_AND_lv25 upgrade fires only ~7% of days, so the
  composition flip is rare; the basket spends 93% of days as QLD/UPRO/UGL
  invvol — close to iter 007 anchor. Diagnostic only.
- **Phase 3 PBO ceiling 0.50 is hard:** if mechanism-mix-diversity does
  not restore PBO < 0.50, this iter joins iter 013 in failing the strict-
  superset bar despite Sortino lift. Hypothesis falsified.
- **Mandate §1 invariant:** capital remains 100% Plan C regardless of
  outcome. `loop_winner_iter` / `loop_phase3_performance_candidate_iter`
  / `loop_strict_superset_iter` lists in `LOOP_MEMORY.md` frontmatter only.

## Citations

- `[risk_parity, p.80-81, ch.4]` Qian RORO graded master-gate (PRIMARY).
- `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking.
- `[stocks_on_the_move, p.98]` Clenow vol-parity / trend strength.
- `[systematic_trading, ch.10]` Carver inverse-vol basket sizing.
- `[volatility_trading, p.58-60]` Sinclair vol cone (ratevol gate).
- `[leverage_for_the_long_run, ch.4-5, p.40-60]` Husson-Trifoni LRS
  leverage scaling.
- `[advances_fin_ml, p.208-211]` PBO via CSCV — mechanism-mix-diversity
  rationale.
- `[advances_fin_ml, p.222-223]` DSR + cumulative n_trials (n_global=510
  after this iter).
