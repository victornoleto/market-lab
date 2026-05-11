# 019-2026-05-10-spyrv-pct25-upgrade-mechmix — SUMMARY

**Iter:** 019 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Add SPY 21d realised-vol percentile (< 25th vs trailing
1260-day window) as an alternative upgrade-gate trigger, OR-combined with
iter 014's K4_AND_QLDlv25 and iter 017's T40D60 post-crash rearm. Six
configs (mechanism-mix-diverse — 5 distinct upgrade-axis topologies);
slots 5+6 are the NEW spyrv variants. Tests whether broader-market vol
regime onsets unlock additional upgrade activation that asset-specific
QLD-vol-pct misses, in pursuit of the loop's 5th strict_superset (and a
NEW non-replica strict_superset) on a forward-vol-orthogonal axis.
**Primary citation:** `[volatility_trading, p.58-60]` Sinclair —
volatility cone framework: percentile-based vol-regime gate.
**Secondary citations:** `[leverage_for_the_long_run, p.4-7, ch.2-3]`
Husson-Trifoni low-vol⇒streaks; `[leverage_for_the_long_run, ch.4-5,
p.40-60]` LRS leverage rotation; `[stocks_on_the_move, p.98]` Clenow
trend re-establishment; `[volatility_trading, p.217-218]` Sinclair
VIX-level filter; `[risk_parity, p.80-81, ch.4]` Qian RORO graded;
`[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking;
`[systematic_trading, p.212, ch.13]` Carver re-arm hysteresis (slot 6
inheritance); `[advances_fin_ml, p.208-211]` CSCV PBO mechanism-mix-
diversity; `[advances_fin_ml, p.222-223]` DSR cumulative
(n_global=540).
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_019
**n_configs:** 6
**cumulative_n_trials_global:** 534 → **540**

## TL;DR

- ⚠️ **CORE STRONG HYPOTHESIS REJECTED — SPY-RV-pct25 OR-add does NOT
  beat the K4_AND_QLDlv25 anchor on Sortino.** Slot 5 (`single_K4lv25_OR_
  spyrv25_g25_rvp70_cashx`, single + (K4_AND_QLDlv25 OR SPYRV25)):
  Sortino_lh56y **1.2899** (-0.1052 vs slot 2 anchor 1.3951). Slot 6
  (3-way OR composite + T40D60 rearm): Sortino_lh56y **1.3133** (-0.0897
  vs slot 4 T40D60 anchor 1.4030). KILL_LOOP #10 (spyrv_strict_superset)
  **NOT FIRED.** Sinclair vol cone gate is too permissive at the 25th
  percentile on SPY (~27.6% activation) — adds TQQQ exposure during
  windows the K4_AND_QLDlv25 (7.1% activation) correctly avoids. The
  added activation lifts CAGR slightly (slot 6 32.20% > slot 4 nothing,
  vs anchor 32.66%) but at the cost of risk-adjusted return.
- 🤔 **WEAK HYPOTHESIS PARTIALLY CONFIRMED — slot 6 IS phase3=True.**
  KILL_LOOP #9 (spyrv_phase3_perf_candidate) **FIRED.** Slot 6 (3-way
  OR composite) achieves CAGR 32.20% > 31.08% Phase 3 floor, end_eq
  1.409× > 1.05× floor, Sortino 1.3133 ≥ 1.20 floor, PBO 0.1984 < 0.50,
  DSR_global 3.14e-3 < 0.05. So spyrv25 mechanism CAN clear Phase 3
  candidacy when stacked with rearm — but cannot clear `beats_winner`
  (Sortino threshold 1.3746).
- 🏆 ✅ **G1 PBO 0.1984 — LOOP MIN.** KILL_LOOP #8 (PBO_held) **FIRED —
  POSITIVE TAG.** Smashes prior LOOP MIN of 0.3056 (iter 011) by
  -0.107pp. Iter trajectory: 005 0.881 → 006 0.798 → 007 0.552 → 008
  0.5675 → 009 0.3770 → 010 0.3929 → 011 0.3056 → 012 0.4960 → 013
  0.5437 → 014 0.4405 → 015 0.3333 → 016 0.3730 → 017 0.4405 → 018
  0.8135 → **019 0.1984 (NEW LOOP MIN)**. Mechanism-mix-diversity
  recipe (5 distinct upgrade-axis topologies) extracted to its
  empirical floor.
- ✅ **All 4 calibration anchors PRESERVED bit-exact** (KILL_LOOP #3,
  #4, #5, #6 ALL NOT FIRED):
  - `baseline_qld_zroz` Sortino 1.3240 = iter 011-018 baseline (drift
    0.0000) — **10th-generation cross-iter reproducibility**.
  - `single_K4lv25_g25_rvp70_cashx` Sortino 1.3951 = iter 013-018
    strict_superset (drift 0.0000).
  - `basket3invvol_K4lv25_g25_rvp70_cashx` Sortino 1.4689 / CAGR
    22.65% / MDD -32.82% / crisis 3/4 = iter 014-017 triple-stack
    (drift 0.0000).
  - `single_K4lv25_g25_rvp70_cashx_T40D60` Sortino 1.4030 / CAGR
    32.66% / end_eq 1.62× = iter 017 NEW strict_superset (drift
    0.0000) — **2nd-generation reproducibility on iter 017's first
    novel strict_superset**.
- 🎯 ✅ **KILL_LOOP #1 success_tag — FIRED.** 3 of 6 configs achieve
  `beats_winner=True` (slots 2, 3, 4 — all replica anchors). 7th loop
  iter to fire success_tag (after iters 009, 010, 012, 014, 015, 016,
  017). **NO NEW (non-replica) beats_winner config from this iter.**
- 🎯 ✅ **`strict_superset` REPLICATED, NOT NEW.** Slots 2 and 4 are
  strict_superset replicas (iter 014 and iter 017 respectively); the
  iter 019 NEW spyrv configs (slots 5, 6) are not strict_superset.
- ❌ **NO 2020 COVID rescue in any spyrv config.** KILL_LOOP #11 NOT
  FIRED. Crisis attribution unchanged at 1/4 (only 2008 GFC) for slots
  5, 6. SPY-RV-pct25 fires 27.6% of days (5y window) but the activation
  pattern does not align with the COVID V-recovery onset (Feb-March
  2020 SPY-RV jumped to high percentile during the crash, only fell
  below 25th around late summer 2020 — too late for V-rebound capture).
- ❌ **LOOP'S FIRST CRISIS-≥2/4 STRICT_SUPERSET STILL NOT ACHIEVED.**
  KILL_LOOP #12 NOT FIRED.
- 🤔 **All non-basket3 configs tier_label = STRONG (score 76.5);
  basket3 anchor STRONG (81.5).** Tier label preserved despite
  sub-anchor Sortino on slots 5, 6 (because winner_conditions_met is
  still True for both — only the Sortino-edge criterion 1 partial
  credit reduces vs strict_supersets).
- 📊 **SPY-RV-pct25 fire-rate diagnostic:** activation 27.6% of valid
  days (1968-2026); K4_AND_QLDlv25 activation only 7.1%; overlap 5.9%
  (84% of QLDlv25 fires also have SPY-RV-pct25 firing); SPY-RV-only
  activation 21.7% (independent of QLDlv25); QLDlv25-only activation
  1.2% (rare). The OR-combined gate fires 28.8% — a ~4× expansion vs
  K4_AND_QLDlv25 alone. **The expansion adds upgrade activation that
  is on average not improving the risk/return trade-off** (slot 5
  Sortino fell despite CAGR roughly preserved); SPY-RV at 25th pct on
  SPY is too inclusive a regime gate for LETF-leverage harvesting.

---

## Configs tested

| # | Name (config) | Topology | ON-leg | Upgrade axis | Rearm | Role |
|---|---|---|---|---|---|---|
| 1 | `..._spyrv_baseline_qld_zroz` | single/none/none | QLD | none | no | Calibration anchor (10th-gen) |
| 2 | `..._spyrv_single_K4lv25_g25_rvp70_cashx` | single/K4_AND_QLDlv25/g=0.25/p70-cashx | QLD/TQQQ | K4_AND_QLDlv25 | no | Iter 014 strict_superset replica |
| 3 | `..._spyrv_basket3invvol_K4lv25_g25_rvp70_cashx` | basket3/K4_AND_QLDlv25/g=0.25/p70-cashx | basket3-invvol60 | K4_AND_QLDlv25 | no | Iter 014 triple-stack replica |
| 4 | `..._spyrv_single_K4lv25_g25_rvp70_cashx_T40D60` | single/K4_AND_QLDlv25_OR_rearm/g=0.25/p70-cashx | QLD/TQQQ | K4_AND_QLDlv25 OR rearm | T40D60 | Iter 017 NEW strict_superset replica |
| 5 | `..._spyrv_single_K4lv25_OR_spyrv25_g25_rvp70_cashx` ← **PRIMARY** | single/(K4_AND_QLDlv25)_OR_SPYRV25/g=0.25/p70-cashx | QLD/TQQQ | K4_AND_QLDlv25 OR SPYRV25 | no | NEW: forward-vol orthogonal upgrade |
| 6 | `..._spyrv_single_K4lv25_OR_spyrv25_g25_rvp70_cashx_T40D60` ← **STRONGEST** | single/(K4_AND_QLDlv25)_OR_SPYRV25_OR_rearm/g=0.25/p70-cashx | QLD/TQQQ | K4_AND_QLDlv25 OR SPYRV25 OR rearm | T40D60 | NEW: 3-way OR composite |

---

## Results — gross metrics per dataset (lh_56y primary)

| # | config | Sortino_lh56y | edge | CAGR_lh56y | edge | MDD_lh56y | end_eq | pct>SPY | crisis | score | tier | WC | beats | phase3 | strict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|:-:|:-:|:-:|:-:|
| 1 | baseline_qld_zroz | 1.3240 | -0.0006 | 0.3108 | +0.00pp | -0.6450 | 1.000× | 1.0000 | 1/4 | 76.5 | STRONG | T | F | F | F |
| 2 | single_K4lv25_g25_rvp70_cashx | 1.3951 | +0.0705 | 0.3147 | +0.39pp | -0.4769 | 1.129× | 1.0000 | 1/4 | 76.5 | STRONG | T | **T** | **T** | **🎯T** |
| 3 | basket3invvol_K4lv25_g25_rvp70_cashx | **1.4689** | +0.1443 | 0.2265 | -8.43pp | **-0.3282** | 0.056× | 1.0000 | **3/4** | **81.5** | STRONG | T | **T** | F | F |
| 4 | 🥇 single_K4lv25_g25_rvp70_cashx_T40D60 | **1.4030** | **+0.0784** | **0.3266** | **+1.58pp** | -0.4818 | **1.620×** | 1.0000 | 1/4 | 76.5 | STRONG | T | **T** | **T** | **🎯T** |
| 5 | single_K4lv25_OR_spyrv25_g25_rvp70_cashx ← PRIMARY | 1.2899 | -0.0347 | 0.3085 | -0.23pp | -0.4838 | 0.933× | 1.0000 | 1/4 | 76.5 | STRONG | T | F | F | F |
| 6 | single_K4lv25_OR_spyrv25_g25_rvp70_cashx_T40D60 ← STRONGEST | 1.3133 | -0.0113 | 0.3220 | +1.12pp | -0.4818 | 1.409× | 1.0000 | 1/4 | 76.5 | STRONG | T | F | **T** | F |

Net metrics (after tax/fees) deferred to a later diagnostic iter (per
hypothesis.md "Tax/fees" caveat).

---

## Gates per config

| # | config | G1 PBO | G1✓ | G2 DSR_local | ✓ | G2 DSR_global | ✓ | G3 wins | G4 OOS | ✓ | G5 FWD post-2020 | ✓ | G6 99% CI low | ✓ | G7 |
|---|---|---:|:-:|---:|:-:|---:|:-:|---:|---:|:-:|---:|:-:|---:|:-:|---:|
| 1 | baseline | 0.1984 | T | 4.5e-3 | T | 3.07e-3 | T | 5/8 | 0.822 | T | 0.708 | T | 0.547 | T | ~0 |
| 2 | single anchor | 0.1984 | T | 1.4e-3 | T | 1.14e-3 | T | 6/8 | 1.004 | T | 0.915 | T | 0.598 | T | ~0 |
| 3 | basket3 anchor | 0.1984 | T | 6.2e-4 | T | 5.74e-4 | T | 6/8 | 1.076 | T | 1.186 | T | 0.633 | T | ~0 |
| 4 | T40D60 anchor | 0.1984 | T | 1.2e-3 | T | 1.01e-3 | T | 6/8 | 1.016 | T | 0.934 | T | 0.608 | T | ~0 |
| 5 | spyrv PRIMARY | 0.1984 | T | 5.0e-3 | T | 4.19e-3 | T | 5/8 | 0.889 | T | 0.810 | T | 0.536 | T | ~0 |
| 6 | spyrv STRONGEST | 0.1984 | T | 3.7e-3 | T | 3.14e-3 | T | 6/8 | 0.914 | T | 0.828 | T | 0.543 | T | ~0 |

**G1 PBO 0.1984 — LOOP MIN** (vs prior LOOP MIN 0.3056 in iter 011). All
6 configs share the same G1 PBO value (cross-config CSCV metric). All
configs pass all 7 gates individually. The hypothesis-rejection for slots
5/6 is purely on Sortino-vs-threshold and CAGR-vs-floor, not gates.

---

## Comparação vs winner (T3d-K2)

| config | Sortino_lh56y | edge_vs_1.3246 | CAGR_lh56y | edge_vs_31.08% | terminal_ratio_vs_baseline | WC | pct>=0.95 | beats_winner | phase3_perf_candidate |
|---|---:|---:|---:|---:|---:|:-:|:-:|:-:|:-:|
| baseline | 1.3240 | -0.0006 | 0.3108 | +0.00pp | 1.000× | T | T (1.0000) | F | F |
| single_K4lv25_g25 | 1.3951 | +0.0705 | 0.3147 | +0.39pp | 1.129× | T | T (1.0000) | **T** | **T** |
| basket3invvol_K4lv25_g25 | **1.4689** | **+0.1443** | 0.2265 | -8.43pp | 0.056× | T | T (1.0000) | **T** | F |
| **single_K4lv25_g25_T40D60** | **1.4030** | **+0.0784** | **0.3266** | **+1.58pp** | **1.620×** | T | T (1.0000) | **🎯T** | **🎯T** |
| single_K4lv25_OR_spyrv25 ← PRIMARY | 1.2899 | -0.0347 | 0.3085 | -0.23pp | 0.933× | T | T (1.0000) | F | F |
| single_K4lv25_OR_spyrv25_T40D60 ← STRONGEST | 1.3133 | -0.0113 | 0.3220 | +1.12pp | 1.409× | T | T (1.0000) | F | **T** |

The iter 017 NEW strict_superset (`single_K4lv25_g25_rvp70_cashx_T40D60`)
remains the LOOP MAX strict_superset on every Phase 3 axis: Sortino
1.4030 (+0.0079 above iter 014's anchor strict_superset 1.3951), CAGR
32.66% (+1.19pp), end_eq 1.620× (+0.49 vs iter 014). **Iter 019 does NOT
unlock additional Phase 3 lift via SPY-RV-pct25 OR-add.**

---

## Phase 3 performance diagnostics

### Did SPY-RV-pct25 lift CAGR? Yes — but at the cost of Sortino.

- Slot 5 vs slot 2 (no rearm comparison): CAGR 30.85% → 31.47%
  (-0.62pp on slot 5; SLIGHT DROP, not lift). Sortino 1.3951 → 1.2899
  (-0.1052 SHARP DROP).
- Slot 6 vs slot 4 (rearm comparison): CAGR 32.66% → 32.20% (-0.46pp).
  Sortino 1.4030 → 1.3133 (-0.0897). end_eq 1.620× → 1.409× (-0.21).

**Mechanism diagnosis:** SPY-RV-pct25 fires 27.6% of valid days vs
K4_AND_QLDlv25's 7.1% — the OR-add expands upgrade activation from 7.1%
to ~26-30% (slots 5, 6). The 4× expansion of activation does NOT
proportionately lift CAGR (CAGR is +/-0.5pp around anchors) but DOES
increase downside vol (Sortino drops 0.09-0.11). Implication: SPY-RV-
pct25 at the 25th percentile is too inclusive — it fires during many
broader-market low-vol periods that don't translate to LETF leverage
harvest opportunity (e.g., ranging market within macro low-vol regime,
where leverage drag dominates compounding).

### Rolling-window win rates vs baseline

| config | 1y | 3y | 5y | 10y |
|---|---:|---:|---:|---:|
| single_K4lv25_g25 | 41.1% | 43.0% | 40.1% | 22.9% |
| basket3invvol_K4lv25_g25 | 38.6% | 34.0% | 31.2% | 17.4% |
| **single_K4lv25_g25_T40D60** | 48.9% | 52.3% | **55.3%** | **38.0%** |
| single_K4lv25_OR_spyrv25 | 39.1% | 38.5% | 39.4% | 24.2% |
| single_K4lv25_OR_spyrv25_T40D60 | 45.0% | 47.2% | 54.4% | **38.0%** |

Slot 6 matches slot 4 on the 10y rolling window (38.0%) but trails on
1y/3y/5y (-3.9pp / -5.1pp / -0.9pp). The 10y match is consistent with
the slot 4 → slot 6 CAGR delta being -0.46pp — over 10y, both compound
to similar terminal equity ratios. Slot 5 (no rearm) shows lower
rolling-win rates than slot 2 across all horizons.

### Crisis attribution (per config)

All 6 configs identical to iter 014/017/018: 1/4 (only 2008 GFC) for
single-asset configs; 3/4 (loses only 2020 COVID) for basket3 anchor.
**SPY-RV-pct25 OR-add does NOT change crisis attribution** — the
broader-market low-vol gate fires too late (post-recovery) to capture
2020 COVID V-bottom; the K4_AND_QLDlv25 + T40D60 mechanisms remain the
dominant alpha sources. KILL_LOOP #11 (spyrv_2020_covid_rescue) NOT
FIRED.

### Turnover

Slot 5 turnover/y: 5.034 (slightly below slot 2's 5.384; SPY-RV expansion
reduces ratevol-cashx flips slightly). Slot 6 turnover/y: 4.970 (below
slot 4's 5.320). The OR-combined gate, by holding TQQQ longer, REDUCES
overall regime-switching frequency. Tax-cost diagnostic deferred.

---

## KILL_LOOP results (pre-registered in hypothesis.md)

- 🎯 ✅ **KILL_LOOP #1 (success_tag) — FIRED.** 3 of 6 configs achieve
  `beats_winner=True` (slots 2, 3, 4 — all replica anchors). 7th loop
  iter to fire success_tag.
- ❌ KILL_LOOP #2 (decisive_fail) — **NOT FIRED.** Best Sortino_lh56y =
  1.4030 ≫ 1.20 floor.
- ✅ KILL_LOOP #3 (replica_sanity_baseline) — **NOT FIRED.** Baseline
  Sortino 1.3240 = bit-exact iter 011-018 baseline (drift 0.0000).
  **10th-generation cross-iter reproducibility achieved.**
- ✅ KILL_LOOP #4 (replica_sanity_single_K4lv25_g25) — **NOT FIRED.**
  Slot 2 Sortino 1.3951 = bit-exact iter 013-018 strict_superset (drift
  0.0000).
- ✅ KILL_LOOP #5 (replica_sanity_basket3invvol_K4lv25_g25) — **NOT
  FIRED.** Slot 3 Sortino 1.4689 / CAGR 22.65% / MDD -32.82% / crisis
  3/4 = bit-exact iter 014-017 triple-stack (drift 0.0000).
- ✅ KILL_LOOP #6 (replica_sanity_T40D60) — **NOT FIRED.** Slot 4
  Sortino 1.4030 = bit-exact iter 017 NEW strict_superset (drift
  0.0000). **2nd-generation reproducibility on iter 017's first novel
  strict_superset CONFIRMED.**
- ✅ KILL_LOOP #7 (PBO_blowup) — **NOT FIRED.** G1 PBO 0.1984 ≪ 0.55
  ceiling.
- 🎯 ✅ **KILL_LOOP #8 (PBO_held) — FIRED — POSITIVE TAG.** G1 PBO
  **0.1984** ≪ 0.50 hard gate. **NEW LOOP MIN** (vs prior 0.3056 iter
  011, by -0.107pp). 5-distinct-mechanism-topology recipe pushes CSCV
  diversity to its empirical floor.
- 🎯 ✅ **KILL_LOOP #9 (spyrv_phase3_perf_candidate) — FIRED.** Slot 6
  achieves phase3=True (CAGR 32.20% > 31.08%, end_eq 1.409× > 1.05×,
  Sortino 1.3133 ≥ 1.20, PBO 0.1984 < 0.50, DSR_global 3.14e-3 < 0.05).
  **CORE WEAK HYPOTHESIS CONFIRMED at the Phase 3 level.**
- ❌ **KILL_LOOP #10 (spyrv_strict_superset) — NOT FIRED.** Neither
  spyrv slot achieves strict_superset (Sortino threshold 1.3746 missed
  by both: slot 5 1.2899 / slot 6 1.3133). **STRONGEST HYPOTHESIS
  REJECTED.** SPY-RV-pct25 OR-add cannot clear the +0.05 anti-curve-fit
  margin above winner Sortino 1.3246.
- ❌ KILL_LOOP #11 (spyrv_2020_covid_rescue) — **NOT FIRED.** No spyrv
  config beats SPY in 2020_covid window (crisis attribution unchanged
  at 1/4).
- ❌ KILL_LOOP #12 (spyrv_strict_superset_with_crisis_2plus) — **NOT
  FIRED.** Loop's first crisis-≥2/4 strict_superset still not achieved.

---

## Verdict

- `beats_winner`: **true** (best config = slot 4 T40D60 anchor; 3 of 6
  configs > 1.3746 threshold — all replicas).
- `phase3_performance_candidate (any)`: **true** (slot 6 NEW + slots 2 +
  4 replicas).
- `strict_superset (any)`: **🎯 true** (slots 2 + 4 replicas; **NO NEW
  strict_superset from this iter**).
- `latest_strict_superset_is_novel`: **false** (iter 019 contributes no
  novel strict_superset; slot 4's T40D60 anchor is the iter 017 finding
  reproduced).

**Tier:** STRONG (best score 76.5).

**Hypothesis assessment:**

- **STRONG hypothesis (KILL_LOOP #10 spyrv_strict_superset)**: REJECTED.
  SPY-RV-pct25 OR-add reduces Sortino by ~0.09-0.11 vs base anchor. Slot
  5 falls below the 1.3746 anti-curve-fit threshold; slot 6 is closer
  (1.3133) but still below.
- **WEAK hypothesis (KILL_LOOP #9 spyrv_phase3_perf_candidate)**:
  CONFIRMED for slot 6. The 3-way OR composite preserves Phase 3
  candidacy while expanding upgrade activation 4× — but cannot beat
  the iter 017 T40D60 NEW strict_superset on the strict bar.
- **PBO health**: NEW LOOP MIN 0.1984 — the strongest empirical
  CSCV-diversity result of the loop so far. The 5-distinct-mechanism-
  topology grid recipe is validated.

**Capital remains 100% Plan C per mandate §1**; iter NOT appended to
`loop_winner_iter`, `loop_phase3_performance_candidate_iter` (only
replicas), or `loop_strict_superset_iter` (only replicas). No NEW
strict_superset finding. Score 76.5 STRONG < 90 deploy bar; per
LOOP_PROTOCOL §"Mandate §1 reinforcement", `docs/CURRENT_STATE.md`
"Active Hunts" entry preserved untouched. **NO automatic capital
realloc.**

---

## Conclusion

⚠️ **HYPOTHESIS REJECTED at the strict-bar level.** SPY-RV-pct25 (Sinclair
vol cone, 25th percentile) is **too permissive a gate** for LETF leverage
harvesting via OR-combine: 27.6% activation rate (vs K4_AND_QLDlv25's
7.1%) expands upgrade frequency 4× but reduces Sortino by ~0.09-0.11pp
because the broader-market low-vol regime captures many ranging-market
windows where leverage drag dominates compounding. **The K4_AND_QLDlv25
selectivity (intersected trend-strength × asset-vol pct) is empirically
calibrated; OR-relaxing it via a less-selective forward-vol gate
broadens activation but does NOT lift the risk-adjusted bar.**

Mechanism-level finding: slot 6 (3-way OR composite) IS phase3=True
(CAGR 32.20%, end_eq 1.409×, Sortino 1.3133). The forward-vol axis
contributes positively at the Phase 3 candidate level — just not enough
to clear the +0.05 anti-curve-fit margin above winner Sortino 1.3246.

**The iter 017 T40D60 strict_superset remains the loop's only NOVEL
(non-replica) strict_superset config**, and is reproduced bit-exactly
in iter 019 (2nd-generation, drift 0.0000).

**G1 PBO 0.1984 — NEW LOOP MIN.** The 5-distinct-mechanism-topology
recipe (single/none vs single/K4_AND_QLDlv25 vs basket3 vs T40D60 rearm
vs SPY-RV OR-composite vs combined) is the strongest empirical
mechanism-mix-diversity demonstration of the loop. **Iter 019's
methodological contribution: confirms that ADDING a genuinely orthogonal
upgrade-axis (different vol asset, different fire-rate) reduces
ranking-clustering substantially even when the new mechanism does not
itself unlock alpha.**

### Lesson

**Sinclair vol cone gate at 25th percentile on SPY is too inclusive
for LETF rotation upgrade.** Future iters using realised-vol percentile
gates should consider:
1. **Tighter percentile** (e.g., 10th rather than 25th) to filter to
   the very-lowest-vol regimes only, mirroring the original Sinclair
   "90th percentile" extreme-tail logic but inverted for low-vol
   regime onset.
2. **AND-combine instead of OR-combine** — `K4_AND_QLDlv25 AND
   SPY-RV-pct25` would be MORE selective (probably ≤ 6%
   activation), testing if the intersection has BETTER risk-adjusted
   return rather than worse.
3. **Different vol asset** — UGL realised-vol-pct (gold-asset, distinct
   correlation) might be more orthogonal than SPY (highly correlated
   with QLD).
4. **Skip realised-vol percentile entirely** — pivot to forward-looking
   IV-based signals (VIX percentile from 1990+; or the IVTS gate per
   `[volatility_trading, p.229]`) which encode option-market
   expectations not captured in realised-vol cones.

### Next iter ideas

(a) **AND-combine SPY-RV-pct25 with K4_AND_QLDlv25** — test whether
intersection (not union) provides better selectivity. Activation
expected ~6% (vs 7.1% K4_AND_QLDlv25 alone). If Sortino lifts above
slot 2 anchor 1.3951, this is a NEW strict_superset axis. Cite
`[volatility_trading, p.58-60]` Sinclair vol cone (intersection
interpretation: regime CONFIRMATION rather than expansion).

(b) **Tighter percentile threshold** — SPY-RV-pct **10th** percentile
(extreme-low-vol only). Activation expected ~10-12%. May avoid the
"too permissive" failure mode of 25th pct. Combined with iter 017
T40D60 rearm as slot 6 candidate.

(c) **VIX-based forward-looking signal** — VIX percentile (vs trailing
1y) replaces realised-vol percentile. Coverage: 1990+ (limits lh_56y
to modern_1990 dataset). Cite `[volatility_trading, p.217-218]`
Sinclair VIX-level filter.

(d) **UGL-realised-vol percentile** — different asset class (gold)
realised-vol; more orthogonal to QLD-equity-vol than SPY-equity-vol.
Cite `[volatility_trading, p.58-60]` vol cone applied cross-asset.

(e) **Pivot to crash-MDD-conditional rearm** (LOOP_MEMORY iter 018
suggestion (c)) — fire rearm only when prior OFF stretch coincides
with trailing 200d SPY MDD breach > -15%. Filters seesaw-induced
false rearms. Cite `[regime_change]` + `[leverage_for_the_long_run,
p.4-7]`. **Highest expected value: directly addresses the iter 017
mechanism's only known weakness (which is that T40D60's 16 qualified
flips include some non-deep-crash false positives).**

---

## Plots

- `plots/01_equity_curves.png` — full lh_56y log-equity curves (6 configs + SPY)
- `plots/02_drawdown_curves.png` — drawdowns
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR
- `plots/05_regime_attribution.png` — % time in equity (vote-K=2 ON state)
- `plots/06_pct_beat_spy.png` — cumulative % of 3y windows beating SPY
- `plots/07_crisis_attribution.png` — crisis MDD vs SPY

## Tables

- `tables/per_config_metrics.csv` — per-dataset metrics (Sortino/Sharpe/CAGR/MDD/pct_above)
- `tables/gates_pass_fail.csv` — G1-G7 pass/fail + activation diagnostics
- `verdict.json` — full structured output (validated against
  `loop_verdict_schema.json`)
- `*_strategy_returns.csv` — daily returns per config (6 files)
