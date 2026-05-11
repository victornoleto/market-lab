# Iter 025 — pbo-decoupled-lrs110-rearm-magnitude — HYPOTHESIS

**Iter:** `025-2026-05-10-pbo-decoupled-lrs110-rearm-magnitude`
**Tier:** loop_iter
**Phase:** 4 — iter 017 focused validation/refinement
**Datetime UTC:** 2026-05-10
**Engine version:** loop_iter_025
**n_configs:** 6 (mechanism-mix-diverse, 3 NON-rearm + 3 rearm-scaffolded)

---

## Hypothesis

**PRIMARY (LRS magnitude structural test)** — Iter 024 cleared G1 PBO 0.4365 (vs
iter 023's 0.6548 NEW PBO mode blowup) by decoupling the LRS axis from the
rearm scaffolding (3 NON-rearm + 3 rearm split, LRS axis spread across K4 +
rearm bases). Iter 024 SUMMARY explicitly claimed *"the iter 023 PBO block was
structural (scaffolding-shared clustering), NOT magnitude-related"*. This iter
**directly tests that claim** by replacing iter 024 slot 6's LRS factor 1.05×
→ 1.10× (single-degree-of-freedom magnitude step), holding the mechanism-mix
layout constant. If PBO clustering is truly structural, G1 PBO should remain
< 0.50 with LRS1.10×. If magnitude DOES affect rank ordering in CSCV, PBO
should rise toward iter 023's 0.6548 blowup level.

**SECONDARY (Phase 4 magnitude monotonicity)** — Iter 024 slot 6 LRS1.05×
delivered Sortino 1.4068 / CAGR 33.43% / end_eq vs iter 017 1.264× — the
loop's first formal `phase4_anchor_improved=True`. Husson-Trifoni
`[leverage_for_the_long_run, ch.4-5, p.40-60]` predicts LRS scaling within the
ann-vol-<40% sweet spot adds CAGR proportionally with modest Sortino dip. If
this holds, slot 6 with LRS1.10× should improve CAGR (~+1pp linear
extrapolation: 33.43% → ~34.4%) and end_eq vs iter 017 (~1.26× → ~1.55×) at
small Sortino cost (~-0.011 → ~1.396), keeping phase4_anchor_improved=True
provided Sortino stays ≥ 1.35.

**TERTIARY (mechanism-mix preservation)** — Slot 3 (K4 base × LRS1.05×)
remains unchanged from iter 024 — preserves the cross-base orthogonality
calibration anchor seeded by iter 024 (slot 3 K4-base LRS lift Sortino
-0.0109 / CAGR +0.95pp). If iter 025 reproduces slot 3 bit-exactly while
slot 6 advances LRS factor, the magnitude probe is cleanly attributed to
slot 6 alone.

## Primary citation

`[leverage_for_the_long_run, ch.4-5, p.40-60]` — Husson-Trifoni LRS leverage
scaling at 1.25×/2×/3× shows monotonic CAGR pump with Sortino preserved within
ann-vol-<40% sweet spot; 1.10× sits well within sweet spot on 2× QLD on-leg
(effective ~2.20× of QQQ).

**Secondary citations:**
- `[advances_fin_ml, p.208-211]` — CSCV PBO mechanism-mix diversity (motivates
  preserving iter 024's PBO-clearing structural layout).
- `[leverage_for_the_long_run, p.13, ch.3]` — canonical RISK_ON LRS rule
  (above-MA → leveraged S&P 500 daily; unconditional within RISK_ON).
- `[leverage_for_the_long_run, p.5-6]` — ann vol < 40% sweet spot for leverage.
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials (n_global=576).
- `[advances_fin_ml, p.196-202]` — bootstrap CI / DSR.
- `[risk_parity, ch.5, p.10]` — Carlson stacking (LRS overlay composition).

---

## Configs (6, mechanism-mix-diverse — preserves iter 024's PBO-clearing layout)

3 NON-rearm (slots 1, 2, 3) + 3 rearm-scaffolded (slots 4, 5, 6); LRS axis
on 2 of 6 slots distributed across 2 distinct base mechanism families
(K4-base: slot 3; rearm-base: slot 6) — 4 effective CSCV groups identical to
iter 024. ONLY slot 6's LRS factor changes (1.05 → 1.10).

| # | name | upgrade gate | rearm | LRS mode | LRS factor | role |
|---|---|---|---|---|--:|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_baseline_qld_zroz` | none | NO | off | 1.00 | 16th-gen calibration anchor |
| 2 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx` | K4_AND_QLDlv25 | NO | off | 1.00 | 13th-gen calibration anchor |
| 3 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx_unclrs105` | K4_AND_QLDlv25 | NO | uncond_on | 1.05 | 2nd-gen K4-base × LRS1.05 anchor |
| 4 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx_T40D60` | K4_AND_lv25 OR rearm | YES (iter017) | off | 1.00 | 8th-gen iter 017 OR-anchor |
| 5 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60` | rearm only | YES (INDEPENDENT) | off | 1.00 | 5th-gen iter 022 INDEP IMPL |
| 6 | 🥇 🆕 `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_unclrs110` | rearm only | YES (INDEPENDENT) | uncond_on | **1.10** | **NEW** rearm-base × LRS1.10 — magnitude probe |

Slot 6 is the only NEW config; slots 1-5 are calibration replicas covering
the full iter 024 + iter 017 lineage. This minimizes new-degree-of-freedom
exposure (single LRS factor step) while preserving the structural mechanism-
mix that cleared PBO 0.4365 in iter 024.

---

## Datasets

`lh_56y` (1970-01-01..2026-04-30), `modern_1990` (1990-01-01..2026-04-30),
`spy_real` (2003-01-01..2026-04-30), `ndx_real` (2010-02-01..2026-04-30).

## Trial accounting

- closed_study_cumulative_n_trials: 426
- cumulative_n_trials_loop_pre_iter025: 144 (after iter 024)
- cumulative_n_trials_global_pre_iter025: 570
- LOCAL_N_CONFIGS: 6
- cumulative_n_trials_loop_after: **150**
- cumulative_n_trials_global_after: **576**

DSR/p-values must use `cumulative_n_trials_global=576` for any beats_winner /
phase4 / strict_superset claim per `[advances_fin_ml, p.222-223]`.

---

## Pre-registered KILL_LOOP conditions

| # | Description | Threshold | Tag |
|---|---|---|---|
| 1 | success_tag | any config beats_winner=True | informational |
| 2 | decisive_fail | best Sortino_lh56y < 1.20 (Phase 3 floor) | study direction abort |
| 3 | replica_baseline | Sortino_lh56y(slot 1) drift > 0.005 vs 1.3240 (16th-gen) | regression |
| 4 | replica_single_K4lv25_g25 | Sortino_lh56y(slot 2) drift > 0.005 vs 1.3951 (13th-gen) | regression |
| 5 | replica_T40D60_OR_iter017 | Sortino_lh56y(slot 4) drift > 0.005 vs 1.4030 (8th-gen) | regression |
| 6 | replica_rearmonly_T40D60 | Sortino_lh56y(slot 5) drift > 0.005 vs 1.4176 (5th-gen) | regression |
| 7 | replica_K4_unclrs105 | Sortino_lh56y(slot 3) drift > 0.005 vs 1.3842 (2nd-gen iter 024 anchor) | regression |
| 8 | PBO_blowup | G1 PBO ≥ 0.55 (NEW PBO mode like iter 023's 0.6548) | structural failure |
| 9 | PBO_held | G1 PBO < 0.50 (Phase 3 hard gate) | **POSITIVE — PRIMARY hypothesis** |
| 10 | lrs110_phase4_anchor_improved | slot 6 phase4_anchor_improved=True | **POSITIVE — STRONG hypothesis** |
| 11 | lrs110_strict_superset | slot 6 strict_superset=True | **POSITIVE — STRONGEST hypothesis** |
| 12 | lrs110_magnitude_pareto_improvement | slot 6 (LRS1.10) > iter 024 slot 6 (LRS1.05) on BOTH CAGR AND end_eq vs iter 017 | **POSITIVE — magnitude monotonicity** |
| 13 | lrs110_sortino_collapse | slot 6 Sortino_lh56y < 1.35 (Phase 4 floor) | magnitude-too-aggressive |

KILL_LOOP #9 + #10 + #11 are the PRIMARY/STRONG/STRONGEST positive tags; if
all three fire, iter 025 confirms iter 024's structural-not-magnitude PBO
diagnosis AND extends Phase 4 anchor improvement to LRS1.10×. KILL_LOOP #12
is a tighter positive tag: did LRS1.10 produce a strict Pareto improvement
over LRS1.05 on the formally-claimable space? KILL_LOOP #8 + #13 are the
negative tags that would reject the magnitude probe.

---

## Expected outcomes (pre-commit)

**Slot 6 (NEW LRS1.10×) linear extrapolation from iter 024:**

| metric | iter 024 slot 5 (LRS off) | iter 024 slot 6 (LRS1.05) | LRS lift per +0.05 | iter 025 slot 6 expected (LRS1.10) |
|---|---:|---:|---:|---:|
| Sortino_lh56y | 1.4176 | 1.4068 | -0.0108 | ~1.396 |
| CAGR_lh56y | 32.44% | 33.43% | +0.99pp | ~34.4% |
| end_eq vs iter017 | 0.936× | 1.264× | +0.328× | ~1.59× |
| MDD | -48.2% | -48.2%/-50.1% mod1990 | small | ~-50-52% |

Pre-registered ranges (linear extrapolation + uncertainty band):
- `sortino_lh56y(slot 6)`: 1.36 .. 1.42 (Sortino floor 1.35 should hold)
- `cagr_lh56y(slot 6)`: 33.5% .. 35.5%
- `end_equity_ratio_vs_iter017(slot 6)`: 1.40× .. 1.80×
- `g1_pbo`: 0.40 .. 0.50 (PRIMARY: should hold < 0.50 if magnitude-irrelevant)
- `dsr_global p`: < 0.005 (n_global=576)
- `pct_time_above_benchmark_lh56y(slot 6)`: 1.000

**Comparison to winner (T3d-K2):**
For `beats_winner=True` slot 6 needs:
- `sortino_lh56y > 1.3746` AND
- `winner_conditions_met = True` AND
- `pct_time_above_benchmark_lh56y >= 0.95`

Linear extrapolation puts slot 6 at Sortino ~1.396 → comfortably above 1.3746.

**Phase 3 performance candidate:**
- `cagr_lh56y > 0.3108` ✓ (~34.4% expected)
- `end_equity_ratio_vs_winner > 1.05` ✓ (linear extrapolation: ~2.6× vs 2.05×)
- `sortino_lh56y >= 1.20` ✓
- `pbo < 0.50` ?  (PRIMARY hypothesis)
- `dsr_global p < 0.05` ✓

**Phase 4 anchor improvement:**
- `cagr_lh56y > 0.3266 (iter 017) OR end_eq vs iter017 > 1.0` ✓
- `sortino_lh56y >= 1.35` ✓ (linear extrapolation 1.396)
- `pbo < 0.50` ?  (PRIMARY hypothesis — same as Phase 3)
- `dsr_global p < 0.05` ✓

**Pareto improvement test (KILL_LOOP #12):**
slot 6 (LRS1.10) > iter 024 slot 6 (LRS1.05) on CAGR AND end_eq vs iter017
- expected CAGR 34.4% > 33.43% ✓
- expected end_eq vs iter017 1.59× > 1.264× ✓
Pre-registered as positive expectation.

---

## INCOMPLETE flags (synth caveats / data gaps / leverage assumptions)

1. **LRS1.10 gross-return approximation.** `apply_unconditional_lrs_overlay`
   scales on-leg returns by 1.10× without modeling the daily-compounding
   vol-drag asymmetry of a true synthetic LETF at the implied effective
   leverage (~2.20× of QQQ). At LRS1.10 the approximation is slightly less
   conservative than LRS1.05; documented for future refinement. Iter 023
   used LRS1.15 with the same approximation (rearm-window-only).
2. **Modern-era softness inherited.** Iter 024 slot 6 modern-era (1990+)
   Sortino 1.155 lands BELOW Phase 3 floor 1.20 (-0.045) — structural to
   the rearm primitive, not LRS overlay. LRS1.10 will likely add ~+1pp CAGR
   uniformly across subperiods but preserve modern-era Sortino softness.
3. **Synth-only universe.** All series sourced from testfolio cache (QLDSIM,
   TQQQSIM, ZROZSIM, IEFSIM, CASHX, SPYSIM); no Tiingo overlay drift check
   beyond G7 cross-lib delta gate.
4. **6-config CSCV power.** N=6 yields C(6,3)=20 ranking comparisons in CSCV;
   identical to iter 024 (also N=6). Not artificially inflated to manipulate
   PBO; magnitude probe is single-axis change with calibration replicas.

---

## Mandate / guardrail acknowledgement

Capital remains 100% Plano C per mandate §1 (MAINTENANCE MODE since
2026-04-23). Even if all 4 positive KILL_LOOPs fire (PRIMARY + STRONG +
STRONGEST + Pareto), the loop only:
1. Records `beats_winner=True` / `phase4_anchor_improved=True` in verdict.json
2. Appends to `loop_winner_iter` / `loop_strict_superset_iter` /
   `loop_phase4_anchor_improved_iter` lists
3. Score 76.5 STRONG < 90 deploy bar → `docs/CURRENT_STATE.md` "Active Hunts"
   entry remains untouched per LOOP_PROTOCOL §"Mandate §1 reinforcement"

NO automatic capital reallocation. Promotion to deploy requires user-driven
mandate §7 override request, not loop-triggered.

Read-only loop modules NOT modified: `gates.py`, `scoring.py`,
`plot_helper.py`, `data_loader.py`, `signals.py`, `signals_carry.py`,
`synths.py`, `tax_layer.py`, `kill_rules.py`, `verdict_schema.json`,
`run_iter*.py`, `configs/`, `runs/original/`, `BASE_MEMORY.md`. Iter 025 reuses
iter 024's `unconditional_lrs_overlay.py` helper bit-exactly (only the
`lrs_factor` argument changes from 1.05 to 1.10).
