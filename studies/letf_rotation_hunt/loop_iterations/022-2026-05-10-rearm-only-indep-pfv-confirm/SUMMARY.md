# 022-2026-05-10-rearm-only-indep-pfv-confirm — SUMMARY

**Iter:** 022 / 50 (loop)
**Phase:** 4 — iter 017 focused validation/refinement
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** PRIMARY — Independent reimplementation of iter 021's slot 5
rearm-only T40D60 (Sortino 1.4176) must produce bit-exact identical
strategy returns vs iter 017's `reentry_overlay.py`. SECONDARY — A
post-flip realised-vol confirmation gate (PFV20) — fire rearm only if first
5d post-flip QLD realised vol < trailing 5y 20th percentile — provides a
quality-confirmation filter topologically distinct from iter 020's pre-flip
MDD rejection.
**Primary citation:** `[advances_fin_ml, p.222-223]` Bailey-Lopez-de-Prado
DSR with cumulative n_trials — independent reimplementation reduces
single-impl risk in DSR claims.
**Secondary citations:** `[advances_fin_ml, p.208-211]` CSCV PBO mechanism-
mix-diversity; `[leverage_for_the_long_run, p.6-7, ch.3]` Husson-Trifoni
MA-streak; `[leverage_for_the_long_run, p.4, ch.2]` streaks-vs-seesawing;
`[volatility_trading, p.58-60]` Sinclair vol cone (PFV); `[stocks_on_the_move,
p.98]` Clenow trend; `[risk_parity, p.80-81, ch.4]` Qian RORO;
`[risk_parity, ch.5, p.10]` Carlson stacking; `[systematic_trading, p.212,
ch.13]` Carver re-arm; `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_022
**n_configs:** 6
**cumulative_n_trials_global:** 552 → **558**

## TL;DR

- 🏆 🎯 **PRIMARY VALIDATION SUCCESS — INDEPENDENT IMPL parity is BIT-EXACT
  ZERO.** `max abs daily-gate diff` between iter 022's
  `rearm_independent.build_postcrash_rearm_gate_independent` (explicit-loop
  numpy from-scratch) and iter 017's `reentry_overlay.build_postcrash_rearm_gate`
  (pandas groupby + rolling-sum) = **0.000e+00** across the entire 56y
  window (n_diff_days=0). KILL_LOOP #8 NOT FIRED. Slot 5
  `single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl` reproduces iter 021
  slot 5's Sortino **1.4176** (drift 0.0000) — **2nd-generation
  reproducibility** of the loop's highest single-leg Sortino finding via a
  structurally distinct algorithm.
- 🏆 🎯 **STRICT_SUPERSET FIRED — PBO 0.4960 passes the 0.50 hard gate
  (vs iter 021's 0.5000 boundary).** Slot 5 INDEP IMPL achieves
  `strict_superset=True` (Sortino 1.4176 > 1.3746 ✓; PBO 0.4960 < 0.50 ✓;
  pct_above_SPY 1.0 ≥ 0.95 ✓; CAGR 32.44% > 31.08% ✓; end_eq 1.516× > 1.05× ✓;
  DSR_global 8.87e-4 < 0.05 ✓). **Iter 021's slot 5 was bit-exact identical
  on returns but was blocked by PBO 0.5000 (boundary tie).** The mechanism
  diversity shift in slot 6 (PFV20 collapsed to zero rearm activation, vs
  iter 021's K4∩rearm at 0.18%) reduces CSCV ranking clustering by exactly
  the bare minimum needed (-0.0040pp PBO). **First iter to convert the
  rearm-only mechanism's qualitative alpha (iter 021) into a formal
  strict_superset.**
- 🏆 🎯 **PHASE 4 ANCHOR VALIDATED — `phase4_anchor_validated=True`.** All
  5 components pass: parity (0.000e+00) ✓; drift vs iter 021 (0.0000) ✓;
  Sortino lift over baseline (+0.0936 ≫ +0.04) ✓; CAGR lift over baseline
  (+1.36pp ≫ +0.5pp) ✓; DSR global (8.87e-4 < 0.05) ✓. **First iter to
  formally validate iter 017's rearm primitive via independent
  implementation + statistical bar combo.**
- ⚠️ **SECONDARY HYPOTHESIS — PFV20 gate REJECTED ON IMPLEMENTATION.**
  KILL_LOOP #11 (`pfv_phase3_perf_candidate`) NOT FIRED; KILL_LOOP #12
  (`pfv_dominates_rearmonly`) NOT FIRED. PFV20 at the 20th-percentile
  threshold filters **0 of 16** duration-qualified flips (post-flip 5d QLD
  realised vol almost never lands in the trailing 5y bottom-quintile —
  immediate post-flip windows are inherently elevated-vol by construction,
  not low-vol). Slot 6 collapses to zero rearm activation, reverting the
  upgrade gate to all-zeros, which on K4_AND_lv25 base settings reduces
  the strategy to QLD/(ZROZ⇄CASHX via rvp70) rotation. This produces
  Sortino 1.4009 / CAGR 30.78% (effectively the rvp70-ratevol-only
  variant) — beats_winner=True (rvp70 lift over baseline) but
  phase3_performance_candidate=False (CAGR 30.78% < 31.08% Phase 3 floor;
  end_eq 0.912× < 1.05× floor).
- ⚠️ **PHASE 4 ANCHOR NOT IMPROVED.** Slot 5 INDEP IMPL CAGR 32.44%
  vs iter 017 anchor 32.66% (-0.22pp); end_eq vs iter017 0.936× < 1.0×.
  Sortino lifts by +0.0146 (1.4176 vs 1.4030) but at the cost of -0.22pp
  CAGR / -6.4% terminal compounding. **This is a Sortino-better-CAGR-
  worse Pareto-NON-improvement, not a Phase 4 strict improvement** per
  protocol §"Phase 4 objective" (a candidate must improve CAGR/equity AND
  preserve Sortino ≥ 1.35). `phase4_anchor_improved=False`.
- 🎯 **SUBPERIOD ROBUSTNESS for slot 5 — edge is TEMPORALLY DISTRIBUTED,
  NOT REGIME-CONCENTRATED.** Per-decade Sortino: 1970-1989 = **2.26**
  (n=1010, CAGR 60.4%, MDD -27.3%, vs SPY CAGR 17.7%); 1990-2009 = **1.17**
  (n=5043, CAGR 31.3%, MDD -48.2%, vs SPY 8.1%); 2010-2026 = **1.16**
  (n=4097, CAGR 27.6%, MDD -36.4%, vs SPY 14.2%). All 3 subperiods clear
  the Phase 3 Sortino floor (1.20)? No — 1990-2009 (1.1673) and 2010-2026
  (1.1596) both miss by 0.03-0.04. Full-period Sortino 1.4176 is partly
  driven by the 1970-1989 super-regime (3 of 16 qualifying flips; CAGR
  60% vs SPY 18% reflects a leveraged-LETF asymmetric harvest in a low-
  inflation post-Volcker rally). **Edge is REAL but FRONT-LOADED into the
  pre-1990 regime; modern-era (1990+) edge is statistically softer.**
  This is a meaningful caveat to the formal `strict_superset=True` flag.
- ✅ **All 4 prior calibration anchors PRESERVED bit-exact** (KILL_LOOP
  #3, #4, #5, #6 ALL NOT FIRED): baseline 1.3240 (13th-gen replica),
  single_K4lv25_g25 1.3951 (10th-gen), basket3invvol 1.4689 (8th-gen),
  T40D60 OR-anchor 1.4030 (5th-gen). **NEW calibration anchor seeded:**
  rearm-only T40D60 INDEP IMPL Sortino 1.4176 (2nd-gen — established by
  iter 022 as the bit-exact match to iter 021 slot 5).

## Configs tested (6, mechanism-mix-diverse with 6 distinct upgrade-axis topologies)

| # | name | ON-leg | upgrade axis | rearm impl | T_crash | D_arm | PFV |
|---|---|---|---|---|--:|--:|---|
| 1 | `..._indep_baseline_qld_zroz` | single QLD | none | — | — | — | — |
| 2 | `..._indep_single_K4lv25_g25_rvp70_cashx` (iter 014 replica) | single QLD/TQQQ | K4_AND_QLDlv25 | — | — | — | — |
| 3 | `..._indep_basket3invvol_K4lv25_g25_rvp70_cashx` (iter 014 LOOP MAX replica) | basket3-invvol60 | K4_AND_QLDlv25 | — | — | — | — |
| 4 | `..._indep_single_K4lv25_g25_rvp70_cashx_T40D60` (iter 017 anchor replica) | single QLD/TQQQ | K4_AND_QLDlv25 OR rearm | iter017 module | 40 | 60 | — |
| 5 | `..._indep_single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl` (PRIMARY) | single QLD/TQQQ | rearm only | INDEPENDENT (rearm_independent.py) | 40 | 60 | — |
| 6 | `..._indep_single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl_pfv20` (NEW) | single QLD/TQQQ | rearm only AND PFV20 | INDEPENDENT (rearm_independent.py) | 40 | 60 | 5d/1260d/p20 |

## Results gross — full table (lh_56y)

| name | sortino | edge_vs_winner_1.3246 | cagr | edge_vs_31.08% | end_eq_vs_baseline | end_eq_vs_iter017 | MDD | upgrade% | crisis | score | tier | beats | phase3 | strict | p4_imp | p4_val |
|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|---:|---|:---:|:---:|:---:|:---:|:---:|
| 1. baseline_qld_zroz | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | 0.617× | -64.5% | 0.0% | 1/4 | 76.5 | STRONG | F | F | F | F | — |
| 2. single_K4lv25_g25 (replica) | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | 0.697× | -47.7% | 7.1% | 1/4 | 76.5 | STRONG | **T** | **T** | **🎯T** | F | — |
| 3. basket3invvol_K4lv25_g25 (replica) | **1.4689** | +0.1443 | 0.2265 | -8.43pp | 0.056× | 0.035× | **-32.8%** | 7.3% | **3/4** | **81.5** | STRONG | **T** | F | F | F | — |
| 4. single_K4lv25_g25_T40D60 (iter 017 replica) | 1.4030 | +0.0784 | **0.3266** | +1.58pp | **1.620×** | 1.000× | -48.2% | 11.8% | 1/4 | 76.5 | STRONG | **T** | **T** | **🎯T** | F | — |
| 5. **single_rearmonly_T40D60_indepimpl** ← 🎯 PRIMARY | single QLD/TQQQ | **1.4176** | **+0.0930** | 0.3244 | +1.36pp | 1.516× | 0.936× | -48.2% | **5.8%** | 1/4 | 76.5 | STRONG | **T** | **T** | **🎯T-VALIDATED** | F | **🏆 T** |
| 6. single_rearmonly_T40D60_indepimpl_pfv20 (collapsed) | 1.4009 | +0.0763 | 0.3078 | -0.30pp | 0.912× | 0.563× | -49.2% | 0.0% | 1/4 | 76.5 | STRONG | **T** | F | F | F | — |

**Best (by tier-strict_superset > phase3 > Sortino > CAGR > score):** slot 5
`single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl` (Sortino 1.4176, score
76.5 STRONG, **strict_superset=True**, **phase4_anchor_validated=True**).

## Gates (all 6 configs)

| name | G1 PBO | G2 DSR_local | G2 DSR_global (n=558) | G3 WF | G4 OOS | G5 FWD | G6 boot99 | G7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. baseline_qld_zroz | **0.4960** ✓ | 3.29e-06 | 3.16e-03 | 14/14 | 0.822 | 0.708 | 0.547 | 0.0000 |
| 2. single_K4lv25_g25 | **0.4960** ✓ | 7.32e-07 | 1.18e-03 | 14/14 | 1.004 | 0.915 | 0.598 | 0.0000 |
| 3. basket3invvol_K4lv25_g25 | **0.4960** ✓ | 2.51e-07 | 5.94e-04 | 14/14 | 1.076 | 1.186 | 0.633 | 0.0000 |
| 4. single_K4lv25_g25_T40D60 | **0.4960** ✓ | 6.20e-07 | 1.05e-03 | 14/14 | 1.016 | 0.934 | 0.608 | 0.0000 |
| 5. **single_rearmonly_T40D60_indepimpl** | **0.4960** ✓ | 4.79e-07 | **8.87e-04** | 14/14 | 0.983 | 0.908 | 0.619 | 0.0000 |
| 6. single_rearmonly_T40D60_indepimpl_pfv20 | **0.4960** ✓ | 6.68e-07 | 1.11e-03 | 14/14 | 0.962 | 0.886 | 0.610 | 0.0000 |

All gates G1-G7 PASS for ALL configs (G1 PBO 0.4960 < 0.50 hard gate; G2
DSR_global p < 0.05; G3 14/14 windows; G4/G5/G6 strictly positive; G7 zero
delta). **First iter since iter 020 with G1 PBO < 0.50 (and 4th non-blowup
PBO < 0.50 since iter 011: 0.3056 → 014 0.4405 → 015 0.3333 → 016 0.3730 →
017 0.4405 → 019 0.1984 → 020 0.4325 → 022 0.4960).**

## KILL_LOOP results

| # | rule | fired | notes |
|---|---|---|---|
| 1 | `success_tag` (any beats_winner=True) | ✅ POSITIVE — 5 of 6 configs (slots 2, 3, 4, 5, 6); 9th loop iter to fire success_tag |
| 2 | `decisive_fail` (best Sortino < 1.20) | ❌ NEGATIVE — best 1.4176 ≫ 1.20 |
| 3 | `replica_baseline` (drift > 0.005 vs 1.3240) | ❌ NEGATIVE — drift 0.0000; **13th-gen reproducibility** |
| 4 | `replica_single_K4lv25_g25` (drift > 0.005 vs 1.3951) | ❌ NEGATIVE — drift 0.0000; **10th-gen** |
| 5 | `replica_basket3invvol_K4lv25_g25` (drift > 0.005 vs 1.4689) | ❌ NEGATIVE — drift 0.0000; **8th-gen** |
| 6 | `replica_T40D60` (drift > 0.005 vs 1.4030) | ❌ NEGATIVE — drift 0.0000; **5th-gen** |
| 7 | `replica_rearmonly_T40D60` (slot 5 drift > 0.005 vs 1.4176) | ❌ NEGATIVE — drift 0.0000; **2nd-gen reproducibility on iter 021's NEW finding** |
| 8 | `parity_check_indep_impl` (max abs gate diff > 1e-12) | ❌ NEGATIVE — **diff=0.000e+00 across 14150 days** ✅ HARD MECHANISM PARITY ESTABLISHED |
| 9 | `PBO_blowup` (G1 PBO ≥ 0.55) | ❌ NEGATIVE — 0.4960 ≪ 0.55 |
| 10 | `PBO_held` (G1 PBO < 0.50) | ✅ POSITIVE — 0.4960 < 0.50 (4th sub-0.50 PBO since iter 020) |
| 11 | `pfv_phase3_perf_candidate` (slot 6 phase3=True) | ❌ NEGATIVE — slot 6 phase3=False (CAGR 30.78% < 31.08%; end_eq 0.912× < 1.05×); PFV20 too restrictive at p20 |
| 12 | `pfv_dominates_rearmonly` (slot 6 Sortino > 1.4176) | ❌ NEGATIVE — slot 6 Sortino 1.4009 < 1.4176; PFV20 collapses to zero rearm activation, reverting to rvp70-only behavior |

## Comparação vs winner (T3d-K2: Sortino 1.3246, CAGR 31.08%, end_eq 1.000×)

| config | sortino_lh56y | edge_vs_1.3246 | cagr_lh56y | edge_vs_31.08% | terminal_ratio_vs_T3d | WC | pct_above_SPY | beats_winner | phase3_perf | strict_superset |
|---|---:|---:|---:|---:|---:|:---:|---:|:---:|:---:|:---:|
| 1. baseline | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | T | 1.000 | F | F | F |
| 2. K4_AND_lv25 (replica) | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | **T** | 1.000 | **T** | **T** | **🎯T** |
| 3. basket3+K4 (replica) | **1.4689** | +0.1443 | 0.2265 | -8.43pp | 0.056× | **T** | 1.000 | **T** | F | F |
| 4. T40D60 OR-anchor (replica) | 1.4030 | +0.0784 | **0.3266** | +1.58pp | **1.620×** | **T** | 1.000 | **T** | **T** | **🎯T** |
| 5. **rearm-only INDEP IMPL** | **1.4176** | **+0.0930** | 0.3244 | +1.36pp | 1.516× | **T** | 1.000 | **T** | **T** | **🏆🎯T-VALIDATED** |
| 6. PFV20 (collapsed) | 1.4009 | +0.0763 | 0.3078 | -0.30pp | 0.912× | **T** | 1.000 | **T** | F | F |

**Rolling win rates vs T3d-K2 (best = slot 5):**
- 1y: 0.5678 (50.0% baseline → 56.8% slot 5; +6.8pp)
- 3y: 0.5526
- 5y: 0.5186
- 10y: 0.3732

## Phase 3 performance diagnostics

Slot 5 (rearm-only INDEP IMPL):
- CAGR_lh56y: 32.44% (+1.36pp vs T3d-K2 31.08% floor) ✓
- end_equity_ratio_vs_winner: 1.516× (>> 1.05× floor) ✓
- Sortino_lh56y: 1.4176 (≥ 1.20 floor) ✓
- G1 PBO: 0.4960 (< 0.50 hard) ✓
- DSR_global: 8.87e-4 (< 0.05) ✓
- All 5 floors pass → `phase3_performance_candidate=True` ✓

The rearm-only mechanism is genuinely a Phase 3 candidate when isolated
from the K4 base. The K4 base (slot 2) trades Sortino for CAGR (+0.0146
vs slot 4 OR-anchor); the rearm primitive (slot 5) trades CAGR for
Sortino (+0.0146 vs OR-anchor with -0.22pp CAGR / -6.4% end_eq).

## Phase 4 anchor diagnostics (vs iter 017 T40D60: Sortino 1.4030, CAGR 32.66%, end_eq 1.620×)

Slot 5 (rearm-only INDEP IMPL):
- **Sortino_edge_vs_iter017:** **+0.0146** ✓ (above iter 017 anchor)
- **CAGR_edge_vs_iter017:** -0.22pp ✗ (below iter 017 anchor)
- **end_eq_ratio_vs_iter017:** 0.936× ✗ (below 1.0)
- **`phase4_anchor_improved`:** **False** (CAGR/equity below anchor; Phase 4 requires improvement on CAGR OR equity, NOT Sortino-only)
- **`phase4_anchor_validated`:** **True** ✓ (parity 0.000e+00; drift 0.0000 vs iter 021 1.4176; Sortino lift +0.0936 vs baseline; CAGR lift +1.36pp; DSR_global 8.87e-4)

**Rolling win rates vs iter 017 anchor (slot 5):**
- 1y: 0.5152 — slot 5 wins 1y window 51.5% of the time vs iter 017
- 3y: 0.4413 — losing edge over 3y windows
- 5y: 0.3845 — losing further over 5y
- 10y: 0.2967 — losing badly over 10y windows

**Diagnosis:** The rearm-only edge is concentrated in 1y windows; over
multi-year windows iter 017's K4-base contribution dominates because K4
fires more frequently than rearm and adds compounding during the K4-only
days (the +0.22pp CAGR / +6.4% end_eq lift). The Pareto frontier between
"rearm-only Sortino-best" (slot 5) and "OR-anchor CAGR-best" (slot 4) is
non-trivial — neither dominates the other on all axes.

### Subperiod robustness (slot 5 rearm-only INDEP IMPL)

| subperiod | n_obs | Sortino | CAGR | MDD | SPY CAGR |
|---|--:|---:|---:|---:|---:|
| **1970-1989** | 1010 | **2.2554** | **0.6043** (60.4%) | -0.2732 | 0.1773 (17.7%) |
| **1990-2009** | 5043 | 1.1673 | 0.3130 (31.3%) | -0.4818 | 0.0815 (8.1%) |
| **2010-2026** | 4097 | 1.1596 | 0.2764 (27.6%) | -0.3636 | 0.1420 (14.2%) |

All 3 subperiods beat SPY CAGR by 8-43pp. **Sortino 1970-1989 is
extraordinary (2.26)** — partially explains the full-period Sortino
1.4176 average. Modern-era (1990+) Sortino is 1.16-1.17 (just below the
Phase 3 floor of 1.20). **The rearm-only edge is REAL but FRONT-LOADED;
modern-era robustness is statistically softer than the full-period
average suggests.** Caveat to publish in any future deploy discussion.

## PFV20 mechanism diagnosis

PFV20 fires 0 of 16 duration-qualified flips. Why?

The trailing 5y 20th-percentile of QLD 5d realised vol is by definition
the bottom 20% of the distribution — i.e., daily vol regimes much quieter
than typical. Post-flip 5d windows are inherently elevated-vol because:
1. The flip itself happens on day t when the SMA200d crosses upward,
   typically during rapidly-rallying markets that exit the SMA crossover
   with high momentum (and hence high realised vol).
2. Post-crash flips (T_crash=40 day OFF preconditions) come AFTER large
   drawdowns, where post-flip volatility persists for 1-3 months while
   markets stabilise.
3. The trailing 5y reference distribution is dominated by quiet/sideways
   days; post-flip windows live deep in the upper-quintile of that
   distribution, NOT the bottom-quintile.

**Implication:** PFV at percentile p20 is mechanically incompatible with
post-crash rearm windows. A meaningful PFV gate would need percentile p50
or higher — i.e., "post-flip vol below MEDIAN" rather than "below 20th".
Even p50 may be too tight; p80 might be needed to get any qualifying
flips. Future iter could test p50/p70/p80 ranges but PBO clustering risk
is high (parametric sweep on percentile, like iter 018's D_arm sweep).

Iter 022 keeps PFV20 as the negative result it is — informational only,
not a Phase 4 improvement candidate.

## Plots

- `plots/01_equity_curves.png` — log-equity curves all 6 configs + SPY
- `plots/02_drawdown_curves.png` — drawdowns
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR
- `plots/05_regime_attribution.png` — % time in equity (vote-K=2 ON state)
- `plots/06_pct_beat_spy.png` — cumulative % of 3y windows beating SPY
- `plots/07_crisis_attribution.png` — crisis MDD vs SPY

## Tables

- `tables/per_config_metrics.csv` — per-dataset metrics for all 6 configs
- `tables/gates_pass_fail.csv` — G1-G7 results per config

## Verdict

| Field | Value |
|---|---|
| Best config | `qld_voteK2_sma250_100_vol21_40_ar30_indep_single_rearmonly_g25_rvp70_cashx_T40D60_indepimpl` |
| Best score | 76.5 |
| Best tier | STRONG |
| beats_winner | true |
| phase3_performance_candidate | true |
| strict_superset | true |
| phase4_anchor_improved | false |
| phase4_anchor_validated | **true** ← 🏆 PHASE 4 MILESTONE |
| any_beats_winner | true |
| any_phase3_performance_candidate | true |
| any_strict_superset | true |
| KILL rule status | N/A (loop iter) |
| KILL_LOOP fired | #1, #10 (positive); #8 NEGATIVE (parity 0.000e+00) |
| cumulative_n_trials_local | 6 |
| cumulative_n_trials_loop (after) | 132 |
| cumulative_n_trials_global (after) | 558 |
| parity_max_abs_diff | 0.000e+00 |
| parity_n_diff_days | 0 |

## Conclusion

**🏆 🎯 PHASE 4 ANCHOR VALIDATED.** Iter 022 establishes bit-exact parity
between the iter 017 module's vectorised rearm primitive and an
independent explicit-loop reimplementation. The rearm-only T40D60
strategy reproduces iter 021's Sortino 1.4176 (drift 0.0000) and — via a
mechanism-diversity shift in slot 6 (PFV20 collapse vs iter 021's K4∩rearm
disjoint intersection) — clears PBO 0.4960 < 0.50 to fire `strict_superset
=True` for the first time. The iter 017 family rearm primitive is
formally validated as `phase4_anchor_validated=True` (all 5 component
tests pass).

**The Pareto trade-off remains unresolved.** Slot 5 rearm-only beats
slot 4 OR-anchor on Sortino (+0.0146) but loses on CAGR (-0.22pp) and
terminal equity (-6.4%). Per Phase 4 protocol §"Phase 4 objective", a
candidate must improve CAGR OR equity to count as a Phase 4 improvement;
slot 5 does not. The rearm-only mechanism is **validated** but not
**improved**.

**Modern-era robustness is softer than full-period suggests.** Subperiod
Sortino (1970-1989: 2.26 / 1990-2009: 1.17 / 2010-2026: 1.16) shows the
full-period Sortino 1.4176 is partially driven by the pre-1990 super-
regime. Modern-era Sortino lands just below the Phase 3 floor of 1.20.

**PFV20 vol-confirmation gate REJECTED at the implementation level.** 0 of
16 qualifying flips pass — post-flip 5d vol almost never falls in the
trailing 5y 20th-percentile (post-flip windows are inherently elevated-
vol). Slot 6 collapses to rvp70-only baseline. Future iters could test
PFV at p50/p70/p80 thresholds, but at PBO-clustering risk (parametric
sweep).

**Capital remains 100% Plano C per mandate §1.** No realloc despite 5 of
6 configs achieving beats_winner=True. Score 76.5 STRONG < 90 deploy bar.

## Next iter ideas

(a) **Mechanism-diverse rearm-window leverage overlay** — pump TQQQ to
1.1×-1.3× ONLY during the rearm window (NOT the K4 window). Tests whether
the rearm-only Sortino lift can be CONVERTED into CAGR/equity improvement
via in-window leverage scaling. **Highest expected value: directly tests
whether iter 022's Pareto trade-off can be broken.** Cite
`[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS leverage scaling.
PBO-clustering risk requires careful pre-registration.

(b) **K4 ELSE rearm with STATE-DEPENDENT graded base** — split K4 into
"K4-during-rearm-window" and "K4-outside-rearm-window" subcomponents.
Test whether DOWNWEIGHTING the K4-during-rearm portion (e.g., 0.5× weight
during rearm window, 1.0× outside) recovers the rearm-only Sortino while
preserving the K4-outside CAGR pump. Distinct topology axis from prior
ELSE/AND/OR variants.

(c) **PFV at higher percentiles (p50 / p70 / p80)** — re-test the post-
flip vol confirmation idea with looser thresholds. Risk of parametric
sweep on percentile axis (like iter 018's D_arm sweep that blew PBO to
0.8135). Requires structural mechanism diversity in 4 of 6 slots to
control PBO.

(d) **Modern-era subperiod stress** — evaluate iter 017 anchor + slot 5
rearm-only on rolling 10y subperiods (1990-1999, 1995-2004, …, 2017-2026).
Tests whether modern-era Sortino softness is structural (mean ~1.17) or
event-driven (concentrated in 2008/2020). **Higher value if the rearm-
only modern Sortino lifts back above 1.20 in some subperiod cuts.**

(e) **Pivot to entirely different family** — calendar/seasonality (post-
FOMC drift, monthly turn, Halloween), cross-asset trend (gold-momentum
pairs), or yield-curve slope. iters 018/019/020/021/022 are all variants
of T40D60; family change may be due. Per LOOP_PROTOCOL §"Soft-halt hint",
no formal soft-halt yet (iter 022 fires positive flags), but the K4-
rearm-MDD-PFV neighbourhood may be approaching diminishing returns.
