# Iter 029 — PBO-decoupled LRS1.20× ratevol-gated **stress-only** overlay (symmetry diagnostic to iter 028)

| Field | Value |
|---|---|
| **iter_id** | `029-2026-05-10-pbo-decoupled-lrs120-ratevol-gated-stress` |
| **slug** | `pbo-decoupled-lrs120-ratevol-gated-stress` |
| **phase** | 4 — iter 017 focused validation/refinement |
| **n_configs** | 6 (≤ 8 cap; mechanism-mix-diverse, identical layout to iter 028 except slot 6 gate inversion) |
| **cumulative_n_trials_global before** | 594 |
| **cumulative_n_trials_global after** | 600 |
| **cumulative_n_trials_loop before** | 168 |
| **cumulative_n_trials_loop after** | 174 |
| **datetime_utc (started)** | 2026-05-10 |
| **engine_version** | `loop_iter_029` |

## Hypothesis (PRIMARY)

Iter 028 applied LRS1.20× ONLY during **calm rate-vol regimes** (ratevol_gate==0,
~70% of ON days; ~51% of all bars active) and **falsified** the key
hypothesis that calm-regime conditioning would lift modern-era subperiod
Sortino above the Phase 3 floor 1.20: 1990-2009 = 1.139 (iter 027 uncond
1.124, +0.015 marginal lift) and 2010-2026 = 1.132 (iter 027 uncond 1.144,
−0.012 marginal regression). Iter 028's interpretation: "modern-era
softness is structural to the rearm primitive, not to LRS overlay magnitude
or application gating".

This iter runs the **complementary symmetry diagnostic** — apply the SAME
LRS1.20× factor on the SAME rearm-only base, but ONLY during **stress
rate-vol regimes** (ratevol_gate==1, complementary ~30% of ON days; ~22% of
all bars active by construction). This is the binary inverse of iter 028's
gate condition.

**KEY HYPOTHESIS (PRE-REGISTERED):** if iter 028's structural diagnosis is
correct, iter 029 should ALSO fail to lift modern-era subperiod Sortino
above Phase 3 floor 1.20 on either of {1990_2009, 2010_2026}. A symmetric
falsification — both calm-only AND stress-only LRS conditioning failing —
**conclusively closes the LRS regime-conditioning axis** as a path to
modern-era Sortino lift on the rearm primitive.

**Counter-falsification:** if iter 029 DOES lift modern Sortino above 1.20
on at least one subperiod, we've discovered an asymmetric regime effect
(stress-period LRS uniquely valuable) that **overturns iter 027/028's
"structural to rearm" diagnosis** — high-information outcome either way.

## Hypothesis (SECONDARY)

Phase 4 axis closure — REGIME after MAGNITUDE, then complementary regime.
With iter 027 closing the LRS magnitude axis (5-point scan complete) and
iter 028 closing the LRS calm-regime axis (key hypothesis falsified), iter
029 closes the LRS stress-regime axis with the **mathematically symmetric
inverse**. After this iter, the rearm-primitive's LRS regime-conditioning
axis is mapped on both sides of the binary regime split — a pre-condition
for the iter 028 next-iter recommendation (a) "PIVOT to non-rearm Phase 4
family" with full diagnostic confidence.

## Hypothesis (TERTIARY)

PBO mechanism-orthogonality preserved. Iter 028 demonstrated that bond-vol
regime-gated LRS preserves PBO at 0.4127 (= iter 026's value, structural
PBO-decoupled framework holds). Iter 029 inverts only the gate condition
(`==0` → `==1`), not the gate signal — so the mechanical orthogonality to
equity-rearm signal is identical. Pre-register: PBO should remain in the
same regime as iter 026/028 (~0.41), NOT blow up like iter 023's 0.6548
(which used a rearm-window-gated overlay correlated with the equity-rearm
signal).

## Primary citation

`[advances_fin_ml, p.208-211]` CSCV PBO mechanism-mix diversity — the
inverse regime gate uses the SAME mechanically-orthogonal bond-vol signal
as iter 028, just with the complementary subset of bars selected. Both
subsets together exhaust the binary regime split.

## Secondary citations

- `[volatility_trading, p.58-60]` Sinclair vol cones — symmetry diagnostic
  on regime-percentile signal (calm vs stress = inverse subsets of the same
  bond-vol percentile).
- `[systematic_trading, ch.13, p.212]` Carver vol-scaled regime thresholds
  — supports both directions of regime conditioning depending on edge
  attribution (where does the alpha live?).
- `[leverage_for_the_long_run, p.13, ch.3]` canonical RISK_ON LRS rule
  preserved; inverse regime gating is a within-RISK_ON conditional
  refinement on the COMPLEMENTARY regime subset.
- `[leverage_for_the_long_run, ch.4-5, p.40-60]` Husson-Trifoni LRS scaling
  (1.20× sweet-spot ceiling on 2× QLD on-leg = effective ~2.40× of QQQ —
  unchanged from iter 027/028).
- `[leverage_for_the_long_run, p.5-6]` ann-vol-<40% sweet spot motivation
  — note that stress regimes typically have HIGHER realized vol, so this
  iter intentionally tests applying LRS DURING the high-vol windows iter
  028 explicitly excluded.
- `[advances_fin_ml, p.222-223]` DSR cumulative (n_global=600 after this
  iter).
- `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.
- `[risk_parity, ch.5, p.10]` Carlson stacking (LRS overlay composition).

## Configs (6, mechanism-mix-diverse — identical layout to iter 028 except slot 6 gate INVERTED)

| # | name | upgrade_mode | rearm | LRS mode | LRS factor | LRS gating | role |
|--:|---|---|---|---|--:|---|---|
| 1 | `..._unclrs_baseline_qld_zroz` | none | NO | off | 1.00 | n/a | calibration anchor (20th-gen) |
| 2 | `..._unclrs_single_K4lv25_g25_rvp70_cashx` | K4_AND_lv25 | NO | off | 1.00 | n/a | calibration anchor (17th-gen) |
| 3 | `..._unclrs_single_K4lv25_g25_rvp70_cashx_unclrs105` | K4_AND_lv25 | NO | uncond_on | 1.05 | unconditional during ON | calibration anchor (6th-gen) |
| 4 | `..._unclrs_single_K4lv25_g25_rvp70_cashx_T40D60` | K4_OR_rearm_iter017 | YES (iter017) | off | 1.00 | n/a | iter 017 OR-anchor replica (12th-gen) |
| 5 | `..._unclrs_single_rearmonly_g25_rvp70_cashx_T40D60` | rearmonly_indep | YES (INDEP) | off | 1.00 | n/a | iter 022 INDEP IMPL replica (9th-gen) |
| 6 | 🥇 `..._unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_rvgtdlrs120stress` (NEW) | rearmonly_indep | YES (INDEP) | rvgtdlrs120stress | **1.20** | when `ratevol_gate==1` (stress; ~22% of all bars active) | NEW probe |

Naming convention `rvgtdlrs120stress` mirrors iter 028's `rvgtdlrs120calm`
in everything except the 4-letter suffix that encodes the regime subset.
The factor (1.20×), threshold (rvp70), and base (rearm-only INDEP IMPL +
T40D60) are bit-identical to iter 028's slot 6.

## Datasets

Same set as iter 011-028 for direct comparability:
- `lh_56y` (1970-01 → 2026-04) — primary headline window.
- `modern_1990` (1990-01 → 2026-04) — modern-era diagnostic.
- `spy_real` (2003-01 → 2026-04) — Tiingo SPY post-inception.
- `ndx_real` (2010-02 → 2026-04) — Tiingo QQQ post-inception.

Subperiod tables compute `1970_1989`, `1990_2009`, `2010_2026` for slot 6
(modern-era Sortino lift KEY HYPOTHESIS test).

## Pre-registered KILL_LOOP conditions

Numbered KILL_LOOP slots — same accounting style as iter 028:

1. **KILL_LOOP #1 (success_tag):** any config has `beats_winner=True`.
2. **KILL_LOOP #2 (decisive_fail):** best Sortino_lh56y < 1.20 (Phase 3 floor).
3. **KILL_LOOP #3 (replica_baseline):** baseline Sortino deviates from
   iter 011-028 1.3240 by > 0.005 (20th-gen target).
4. **KILL_LOOP #4 (replica_single_K4lv25_g25):** slot 2 Sortino deviates
   from iter 014-028 1.3951 by > 0.005 (17th-gen target).
5. **KILL_LOOP #5 (replica_T40D60_OR_iter017):** slot 4 Sortino deviates
   from iter 017-028 1.4030 by > 0.005 (12th-gen target).
6. **KILL_LOOP #6 (replica_rearmonly_T40D60):** slot 5 Sortino deviates
   from iter 021-028 1.4176 by > 0.005 (9th-gen target).
7. **KILL_LOOP #7 (replica_K4_unclrs105):** slot 3 Sortino deviates from
   iter 024-028 1.3842 by > 0.005 (6th-gen target).
8. **KILL_LOOP #8 (PBO_blowup):** G1 PBO ≥ 0.55 (NEW PBO mode like iter
   023's 0.6548 — would falsify mechanical orthogonality of stress-regime
   gating).
9. **KILL_LOOP #9 (PBO_held — POSITIVE TAG):** G1 PBO < 0.50 hard gate.
   Confirms inverse regime-gating preserves PBO-decoupled framework.
10. **KILL_LOOP #10 (rvgtdlrs120stress_phase4_anchor_improved):** slot 6
    achieves `phase4_anchor_improved=True`. Pre-registered EXPECTATION:
    LIKELY FALSE since stress-only LRS active on only ~22% of bars produces
    much smaller CAGR boost than calm-only's ~51% (iter 028 slot 6 CAGR
    35.11% — most of which came from calm-regime LRS exposure on the
    ascending leg). With ~22% LRS-active fraction, expected slot 6 CAGR
    in 32-33% range (close to iter 017 anchor 32.66% — borderline anchor
    improvement on CAGR axis alone).
11. **KILL_LOOP #11 (rvgtdlrs120stress_strict_superset):** slot 6 achieves
    `strict_superset=True` (`beats_winner` AND `phase3_performance_candidate`).
12. **KILL_LOOP #12 (rvgtdlrs120stress_modern_sortino_lift) — KEY HYPOTHESIS:**
    slot 6 modern subperiod Sortino ≥ 1.20 on AT LEAST ONE of {1990_2009,
    2010_2026}. Pre-registered EXPECTATION: LIKELY FALSE (consistent with
    iter 027/028 structural diagnosis). If FIRES → asymmetric regime
    effect found; iter 028's structural conclusion overturned.
13. **KILL_LOOP #13 (rvgtdlrs120stress_residual_lift):** slot 6 CAGR_lh56y
    > 32.66% (iter 017 anchor) — proves stress-only LRS on ~22% of bars
    contributes ANY CAGR lift over the rearm-only baseline. If FALSE,
    LRS-during-stress contributes nothing — overlay is mostly absorbed by
    daily-rebalance vol drag during high-realised-vol windows.
14. **KILL_LOOP #14 (rvgtdlrs120stress_sortino_collapse):** slot 6
    Sortino_lh56y < 1.35 (Phase 4 improved floor). LRS during stress
    regimes amplifies daily-rebalance vol drag asymmetry — Sortino could
    drop substantially. Pre-register as a plausible failure mode.
15. **KILL_LOOP #15 (regime_axis_symmetric_falsification):** if BOTH iter
    028's KILL_LOOP #12 (calm modern-Sortino lift) AND iter 029's
    KILL_LOOP #12 (stress modern-Sortino lift) report `fired=False`,
    declare REGIME-CONDITIONING AXIS CLOSED. Symmetry diagnostic complete
    — modern-era softness is independently confirmed structural to rearm
    on TWO complementary regime subsets, not removable by either polarity
    of regime-gating.

## Pre-registered expected outcomes

| metric | slot 6 expected | rationale |
|---|---|---|
| `lrs_active_pct` (slot 6) | ~0.21 (= 0.7258 × 0.2986) | ON × stress = inverse complement of iter 028's 0.5091 |
| Sortino_lh56y (slot 6) | 1.32-1.40 range | smaller LRS exposure than iter 028's 1.3860; vol-drag during stress could drop floor |
| CAGR_lh56y (slot 6) | 32-34% range (≈ iter 017 anchor ± a few pp) | far smaller boost than iter 028's 35.11%; LRS active on ~22% of bars vs ~51% |
| end_eq vs T3d-K2 (slot 6) | 1.5-2.0× | between rearm-only INDEP IMPL (1.516×) and iter 028 slot 6 (3.385×) |
| end_eq vs iter 017 (slot 6) | 0.95-1.20× | borderline anchor improvement on terminal compounding |
| MDD (slot 6) | -48 to -52% | similar to rearm-only baseline since most stress bars cluster around the same crash episodes |
| G1 PBO | 0.39-0.45 | same regime as iter 026/027/028 (~0.41-0.43); PBO-decoupled framework should hold |
| modern_1990_2009 Sortino (slot 6) | 1.05-1.20 (likely below 1.20 floor) | symmetric falsification consistent with iter 028 |
| modern_2010_2026 Sortino (slot 6) | 1.05-1.18 (likely below 1.20 floor) | symmetric falsification consistent with iter 028 |
| `phase4_anchor_improved` (slot 6) | borderline (depends on CAGR vs 32.66%) | could fail if LRS-during-stress contributes ≤ 0 net CAGR |
| `beats_winner` (slot 6) | likely True | Sortino target 1.32-1.40 includes > 1.3746 outcome |
| `strict_superset` (slot 6) | likely True if beats_winner AND CAGR > 31.08% | depends on G1/G2 |
| `phase3_performance_candidate` (slot 6) | likely True if CAGR > 31.08% | depends on whether LRS-stress is net-additive |

**Comparison plan vs winner:** beats_winner requires `sortino > 1.3746
AND winner_conditions_met AND pct_time_above_benchmark_lh56y ≥ 0.95`.

**Phase 3 performance plan:** `phase3_performance_candidate` requires
`cagr_lh56y > 0.3108 AND end_equity_ratio_vs_winner > 1.05 AND
sortino_lh56y >= 1.20 AND PBO < 0.5 AND DSR global p < 0.05`.

**Phase 4 anchor plan:** `phase4_anchor_improved` requires
`(cagr_lh56y > 0.3266 OR end_equity_ratio_vs_iter017 > 1.00) AND
sortino_lh56y >= 1.35 AND PBO < 0.5 AND DSR global p < 0.05`.

## INCOMPLETE / caveat flags

- **Synth caveat:** QLDSIM/TQQQSIM/UPROSIM/UGLSIM/ZROZSIM/IEFSIM all use
  testfolio Gayed-style synthetics for the pre-real-ETF window. The on-leg
  is a 2× simulated QLD; the LRS overlay multiplies that synthetic
  exposure. Real-ETF window (post-2006 for QLD) untouched by the synth
  assumption.
- **`ratevol_gate` warmup:** ZROZ-based bond rate-vol percentile needs the
  full pct_window (1260 days = 5y) before producing a non-NaN signal.
  Approximately 13% of all bars pre-1975 fall in the warmup; LRS is
  conservatively OFF on those (matches iter 028 convention bit-exactly).
- **Stress regime threshold (rvp70 = 70th percentile):** flips only when
  bond rate-vol exceeds the 70th-percentile of its own 5y rolling history,
  by construction targeting the upper-tercile vol windows. Sensitivity to
  alternative thresholds (rvp60, rvp80) NOT tested in this iter — that's a
  follow-up if iter 029's KEY HYPOTHESIS fires.
- **LRS factor (1.20×):** held constant at iter 027/028 magnitude to keep
  the diagnostic clean. The point is the gate inversion, not magnitude.
- **n_trials_global = 600** after this iter — DSR global cumulative
  denominator increases by 6 (`[advances_fin_ml, p.222-223]`).
- **Repository state:** at iter start, `data/tiingo/manifest.json` and
  `tests/test_tiingo_storage.py` carry pre-existing modifications unrelated
  to letf_rotation_hunt. Per LOOP_PROTOCOL §"Commit conventions", iter 029
  uses `git add` with specific paths only and does NOT pull these orphan
  changes into its commit; pytest baseline 1094 ≥ 813 unaffected.

## Mandate §1 reinforcement

This iter runs read-only against shared modules (`gates.py`, `scoring.py`,
`plot_helper.py`, `data_loader.py`, `signals.py`, `signals_carry.py`,
`synths.py`, `tax_layer.py`, `kill_rules.py`, `verdict_schema.json`,
`run_iter*.py`, `configs/`, `iterations/`). New helper
`inverse_regime_gated_lrs_overlay.py` lives INSIDE the iter dir per
LOOP_PROTOCOL §"Scope limits". `BASE_MEMORY.md` not modified. No deploy
trigger; capital remains 100% Plano C per mandate §1 even if
`beats_winner=True`.
