# 016-2026-05-10-regime-switch-on-leg-basket — HYPOTHESIS (pre-commit)

**Iter:** 016 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Family:** regime-conditional ON-leg basket switching (NEW mechanism)
**n_configs:** 6
**cumulative_n_trials_global:** 516 → **522** (516 + 6)
**cumulative_n_trials_loop:** 90 → **96**
**closed_study_cumulative_n_trials:** 426 (frozen)

## Hypothesis

Iter 015 closed the **fixed-weight equity-tilt** path to recovering CAGR
above 31.08% Phase 3 floor. Across the entire UGL-weight spectrum
{0%, 7.5%, 16.7%, 45%}, **no static fixed-weight tilt simultaneously
clears Phase 3 CAGR floor AND retains basket3-invvol's crisis 3/4**:

| UGL weight | CAGR | crisis | Phase 3? |
|---:|---:|:---:|:---:|
| 0% (basket2_QU) | 28.99% | 2/4 | F (CAGR -2.09pp) |
| 7.5% (eqtilt85) | 30.05% | 1/4 | F (CAGR -1.03pp) |
| 16.7% (eqtilt66) | 27.81% | 1/4 | F (CAGR -3.27pp) |
| ~45% invvol (basket3-invvol) | 22.65% | 3/4 | F (CAGR -8.43pp) |

The trade-off is **structural, not parametric** — iter 015 explicit verdict.

This iter tests the iter 015 #1 next-iter idea (highest expected value):
**dynamic regime-conditional switching between single-asset ON-leg
(high CAGR, crisis 1/4) and basket3-invvol ON-leg (lower CAGR, crisis 3/4)**.
A regime gate decides each day: when "bull" regime → single QLD/TQQQ
ON-leg (captures iter 014 strict_superset's CAGR 31.47%); when
"defensive" regime → basket3-invvol ON-leg (captures iter 014 triple-
stack's crisis 3/4 cushion via UGL gold sleeve).

If a regime gate exists that activates `single` during high-CAGR equity-
bull regimes (most of the equity-rally time) and switches to `basket3-
invvol` during high-vol or low-conviction regimes (where the gold cushion
matters), the two iter 014 endpoints can be **mechanically composed
rather than fixed-weight averaged**. This is the discrete analog of iter
010's graded master-bridge (gamma-blending two endpoints) but applied to
the ON-leg topology dimension instead of the OFF-leg blend cell.

**Goal:** loop's **first crisis-≥2/4 strict_superset** — i.e., a config
that simultaneously satisfies `beats_winner=True` (Sortino > 1.3746,
WC=True, pct_above ≥ 0.95) AND `phase3_performance_candidate=True`
(CAGR > 31.08%, end_eq > 1.05×, Sortino ≥ 1.20, PBO < 0.50, DSR_global
< 0.05) AND crisis_attribution ≥ 2/4. Iter 014's two strict_supersets
(`K4lv25_g0_rvp70_cashx`, `K4lv25_g25_rvp70_cashx`) both have crisis
1/4; iter 014's triple-stack basket3 has crisis 3/4 but fails Phase 3
on CAGR. The regime-switch is the obvious candidate to bridge the gap.

## Primary citation

`[risk_parity, p.80-81, ch.4]` — Qian RORO (Risk-On / Risk-Off)
regime-conditional master-gate. The Qian RORO framework explicitly
prescribes switching the active risk-budget composition between distinct
endpoints based on a regime indicator, rather than weight-averaging
them statically. This iter applies the same primitive to the ON-leg
composition (single vs basket3-invvol).

## Secondary citations

- `[risk_parity, p.110, ch.5]` — Qian fixed-weight diversification
  return (frames the dynamic switch vs iter 015's static eqtilt).
- `[risk_parity, p.11, ch.1]` — Qian invvol over-allocation pathology
  (motivates switching AWAY from invvol when equity-favorable).
- `[risk_parity, ch.5, p.10]` — Carlson cap-efficient stacking (regime
  switch composes orthogonally with the iter 014 K4_AND_lv25 upgrade
  gate and ratevol-OFF override).
- `[volatility_trading, p.58-60]` — Sinclair vol cone (lowvol50 regime
  is the same realised-vol primitive as the lowvol25 upgrade gate but
  at a less restrictive threshold; well-defined statistical regime).
- `[stocks_on_the_move, p.98]` — Clenow trend-strength (K=4 vote
  regime is a trend-conviction primitive orthogonal to vol regime).
- `[leverage_for_the_long_run, ch.4-5, p.40-60]` — Husson-Trifoni LRS
  leverage (K=4 vote = highest-conviction regime where leveraged
  single-asset is structurally favored).
- `[advances_fin_ml, p.208-211]` — CSCV PBO (mechanism-mix-diversity
  via 4 distinct ON-leg topology buckets keeps G1 PBO controlled).
- `[advances_fin_ml, p.222-223]` — DSR cumulative
  (n_trials_global=522).

## Configs (6, mechanism-mix-diverse, 4-distinct-ON-leg-topology)

ON-leg topologies in this iter:
- **single** (QLD/TQQQ swap on K4_AND_lv25) — slots 1, 2
- **basket3-invvol** (QLD/UPRO/UGL invvol60 with QLD↔TQQQ swap) — slot 3
- **regime-switch on lowvol50** (single when vol_21d_pct < 0.50; else basket3-invvol) — slots 4, 6
- **regime-switch on K=4 vote** (single when K=4 fires; else basket3-invvol) — slot 5

Mechanism-mix audit:
- ON-leg: 4 distinct topology buckets (single, basket3-invvol, regsw-vol, regsw-K4)
- Upgrade gate: 2 distinct (none, K4_AND_lv25)
- Gamma: 2 distinct (0.0, 0.25)
- Ratevol: 3 distinct (none, p70, p80)
- Alt-OFF: 3 distinct (none, CASHX, IEFSIM)

Slots 4 and 6 share regsw-vol50 ON-leg but differ on gamma + ratevol +
alt-OFF axes — this is the same parametric-variant pattern as iter 014
(slots 2 and 4 shared single ON-leg + K4lv25/g0 but differed on ratevol
+ alt-OFF axes). Iter 014 PBO 0.4405; iter 015 with 4-of-6 sharing
K4lv25/g25/p70/CASHX axis got PBO 0.3333. Pattern: ON-leg topology
diversity dominates the PBO recipe.

| # | Name (suffix after `qld_voteK2_sma250_100_vol21_40_ar30_regsw_`) | ON-leg | regime gate | upgrade | gamma | ratevol | alt-OFF | role |
|---|---|---|---|---|--:|---|---|---|
| 1 | `baseline_qld_zroz` | single | — | none | 0.00 | none | — | replica anchor (1.3240) |
| 2 | `single_K4lv25_g25_rvp70_cashx` | single | — | K4_AND_lv25 | 0.25 | p70 | CASHX | iter 014 strict_superset replica (1.3951) |
| 3 | `basket3invvol_K4lv25_g25_rvp70_cashx` | basket3-invvol60 | — | K4_AND_lv25 | 0.25 | p70 | CASHX | iter 014 triple-stack replica (1.4689) |
| 4 | **`lv50_K4lv25_g25_rvp70_cashx`** ← PRIMARY | regsw-vol50 (single↔basket3) | vol_21d < 50th pct | K4_AND_lv25 | 0.25 | p70 | CASHX | NEW regime switch — lowvol50 |
| 5 | **`K4_K4lv25_g25_rvp70_cashx`** ← ORTHOGONAL | regsw-K4 (single↔basket3) | K=4 vote fires | K4_AND_lv25 | 0.25 | p70 | CASHX | NEW regime switch — K=4 conviction |
| 6 | **`lv50_K4lv25_g0_rvp80_ief`** ← MECH-DIV | regsw-vol50 (single↔basket3) | vol_21d < 50th pct | K4_AND_lv25 | 0.0 | p80 | IEFSIM | mechanism-diversity (alt OFF/gamma/rv) |

## Datasets (same as iter 015 for comparability)

| Dataset | Window |
|---|---|
| lh_56y | 1970-01-01..2026-04-30 |
| modern_1990 | 1990-01-01..2026-04-30 |
| spy_real | 2003-01-01..2026-04-30 |
| ndx_real | 2010-02-01..2026-04-30 |

## Pre-registered KILL_LOOP conditions

| # | Rule | Direction |
|---|---|---|
| 1 | success_tag — ANY config beats_winner=True | POSITIVE TAG |
| 2 | decisive_fail — best Sortino_lh56y < 1.20 (Phase 3 floor) | NEGATIVE TAG (kills hypothesis) |
| 3 | replica_sanity_baseline — drift > 0.005 vs 1.3240 (iter 011-015 baseline) | KEEP NOT FIRED (calibration) |
| 4 | replica_sanity_single_K4lv25_g25 — drift > 0.005 vs 1.3951 (iter 014 strict_superset) | KEEP NOT FIRED (calibration) |
| 5 | replica_sanity_basket3invvol_K4lv25_g25 — drift > 0.005 vs 1.4689 (iter 014 triple-stack) | KEEP NOT FIRED (calibration) |
| 6 | PBO_blowup — G1 PBO ≥ 0.55 | NEGATIVE TAG |
| 7 | PBO_held — G1 PBO < 0.50 | POSITIVE TAG (recipe held) |
| 8 | regsw_phase3_perf_candidate — ANY regime-switch variant achieves phase3=True | POSITIVE TAG (CORE hypothesis) |
| 9 | regsw_strict_superset — ANY regime-switch variant achieves strict_superset=True | POSITIVE TAG (STRONGEST hypothesis) |
| 10 | regsw_crisis_2or3_of_4 — ANY regime-switch achieves crisis ≥ 2/4 | POSITIVE TAG |
| 11 | regsw_strict_superset_with_crisis — ANY regime-switch achieves strict_superset AND crisis ≥ 2/4 | POSITIVE TAG (LOOP'S FIRST crisis-≥2/4 strict_superset!) |
| 12 | regsw_lv50_dominates_K4 — Sortino lv50 > Sortino K4 (regime-gate ablation) | DIAGNOSTIC (validates lowvol regime over trend regime) |

## Expected outcomes

### Quantitative pre-registered ranges

| Metric | Expected range | Threshold | Notes |
|---|---|---|---|
| Best Sortino_lh56y | 1.36–1.47 | 1.3746 (beats) | Between iter 014 single 1.3951 and triple-stack 1.4689 |
| Best CAGR_lh56y | 23–32% | > 31.08% (Phase 3) | If lv50 regime spends most time in single → CAGR closer to 31.47%; if mostly in basket3 → CAGR drops to ~23% |
| Best end_eq_ratio_vs_baseline | 0.3×–1.2× | > 1.05× (Phase 3) | Highly dependent on lv50/K4 activation rate |
| Best crisis count | 2/4–3/4 | ≥ 2/4 | If regime switch correctly routes to basket3-invvol during 2008/2020/2022 |
| G1 PBO | 0.30–0.45 | < 0.50 (Phase 3) | 4-distinct-ON-leg-topology recipe should hold |
| Best score | 79–82 | < 90 (deploy) | Below deploy threshold per LOOP_PROTOCOL §"Mandate §1 reinforcement" |

### Win condition (any of these → iter 016 is a positive Phase 3 result)

- **Strongest:** loop's first **crisis-≥2/4 strict_superset** (KILL_LOOP #11 fires positively).
- **Strong:** any regime-switch variant achieves `strict_superset=True`
  (KILL_LOOP #9 fires positively).
- **Moderate:** any regime-switch variant achieves `phase3_performance_
  candidate=True` (KILL_LOOP #8 fires positively).
- **Calibration only:** all 3 anchor configs preserve bit-exact returns
  (KILL_LOOP #3, #4, #5 NOT FIRED).

### Failure modes / sanity prediction

- If regime switch spends > 70% time in basket3 → CAGR collapses to
  ~23% (iter 014 triple-stack) and Phase 3 fails on CAGR.
- If regime switch spends > 90% time in single → reduces to iter 014
  strict_superset and crisis stays at 1/4.
- The "sweet spot" requires the regime gate to (a) activate single
  during equity-bull cumulative-CAGR-positive periods (most of 1995-
  2000, 2003-2007, 2009-2020, 2023+) and (b) activate basket3 during
  equity-distressed periods (2000-2002, 2008, 2020-Q1, 2022). The
  lowvol50 gate has historical activation around 50% by construction;
  K=4 around 20-25% per iter 011 stats.

## Comparação plan vs winner T3d-K2

For `beats_winner=True`:
- Sortino_lh56y > 1.3746
- winner_conditions_met = True (G1, G2, G6, G7 pass + Sortino edge ≥ +0.05 + pct_above ≥ 0.95)
- pct_time_above_benchmark_lh56y ≥ 0.95

For `phase3_performance_candidate=True`:
- cagr_lh56y > 0.3108
- end_equity_ratio_vs_baseline > 1.05
- sortino_lh56y ≥ 1.20
- G1 PBO < 0.50
- G2 DSR_p_cumulative (n_global=522) < 0.05

For `strict_superset=True`: BOTH above must hold simultaneously.

## Comparações vs prior loop iters

| Anchor | iter 014 strict_superset (single K4lv25 g25) | iter 014 triple-stack (basket3-invvol K4lv25 g25) | this iter target |
|---|---|---|---|
| Sortino_lh56y | 1.3951 | 1.4689 | 1.40–1.47 (regime mix) |
| CAGR_lh56y | 31.47% | 22.65% | recover toward 31.08% |
| MDD | -47.69% | -32.82% (LOOP MIN) | -35% to -50% |
| Crisis | 1/4 (only 2008) | 3/4 (2000+2008+2022) | **≥ 2/4 needed for win** |
| Phase 3 candidate | T | F (CAGR fails) | T (target) |
| beats_winner | T | T | T |
| **strict_superset** | **T** | **F** | **T (target — would be loop's 4th)** |
| **strict_superset + crisis ≥ 2/4** | F (crisis 1/4) | F (Phase 3 fails) | **T (target — LOOP'S FIRST)** |

## Phase 3 performance plan

For `phase3_performance_candidate=True`, the regime-switch must on
average spend enough time in `single` ON-leg to keep CAGR > 31.08%.
The lv50 regime gate has structurally ~50% activation rate (vol below
its trailing-5y median by construction in steady state). At 50/50 mix,
expected CAGR is roughly the geometric mean of (31.47%, 22.65%) ≈ 26.6%
— BELOW the floor. Therefore, the lv50 regime is unlikely to clear
Phase 3 unless the regime gate's activation skews positive during high-
return periods (which empirically it does: vol is low DURING bull
regimes, so lv50 should over-activate during 1995-2000, 2003-2007,
2009-2020, 2023+ and under-activate during crashes).

The K=4 vote regime has lower activation (~20-25% per iter 011), so
expected CAGR_K4 ≈ 0.20 × 31.47% + 0.80 × 22.65% ≈ 24.4% — likely
below floor. Lower probability of clearing Phase 3.

The PRIMARY config is `lv50_K4lv25_g25_rvp70_cashx`; the K4 ablation
slot 5 is included to test the regime-gate-axis ablation per
KILL_LOOP #12.

## INCOMPLETE flags

- **Synth caveat:** UPRO/UGL synth inception ~1985 (per BASE_MEMORY +
  iter 014 finding) truncates basket3-effective evaluation window;
  pre-1985 contribution to lh_56y comes from single-asset configs only.
  This biases the regime-switch toward single during early decades
  (basket3 unavailable) — the lv50 activation analysis above only
  applies post-1985.
- **Regime gate uses lagged 1-day signal** (matches iter 011
  conditional-leg convention; no look-ahead).
- **Both internal legs use the same upgrade gate** (K4_AND_lv25) for
  QLD↔TQQQ swap — preserves iter 014 single's calibration anchor at
  Sortino 1.3951 when regime gate is constant 1, AND iter 014 basket3
  triple-stack's calibration anchor at Sortino 1.4689 when regime gate
  is constant 0. Tested via slots 2 and 3 (which use a constant-1 and
  constant-0 regime gate respectively, by selecting `single` or
  `basket3` ON-leg unconditionally).
- **Tax/fees impact NOT scored** in this iter (gross metrics only;
  matches study convention for SUMMARY tables — net diagnostic
  deferred per iter 015 idea (e)).
- **Regime gate transitions add turnover** beyond the iter 014
  single-asset estimate (5.38/y); will be quantified per-config.
- **Mandate §1 reinforcement:** even if loop's first crisis-≥2/4
  strict_superset fires, capital remains 100% Plano C. CURRENT_STATE
  "Active Hunts" entry only updated if score ≥ 90 (none expected).
