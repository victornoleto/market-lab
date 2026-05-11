# 015-2026-05-10-equity-tilted-basket-cagr-recovery — SUMMARY

**Iter:** 015 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Fixed-weight equity-tilted baskets (basket3-eqtilt66 with
weights 2/3+1/6+1/6; basket3-eqtilt85 with 0.85+0.075+0.075; basket2_QU
invvol QLD/UPRO without UGL) test whether reducing UGL weight from
basket3-invvol's ~45% (Carver/Clenow inverse-vol) down to 16.7%, 7.5%, or
0% recovers CAGR_lh56y above the 31.08% Phase 3 floor while preserving
2022_rates / 2000_dotcom crisis cushion. Six configs preserve mechanism-
mix-diverse 5-topology grid (iter 014 PBO-0.4405 recipe). Targets the
loop's first crisis-≥2/4 strict_superset.
**Primary citation:** `[risk_parity, p.110, ch.5]` Qian — diversification
return for fixed-weight rebalanced basket; foundation for fixed-weight
equity-tilt vs invvol Carver/Clenow.
**Secondary citations:** `[risk_parity, p.11, ch.1]` Qian invvol over-
allocation pathology; `[risk_parity, p.80-81, ch.4]` Qian RORO graded
master-gate; `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking;
`[stocks_on_the_move, p.98]` Clenow vol-parity; `[systematic_trading,
ch.10]` Carver inverse-vol; `[volatility_trading, p.58-60]` Sinclair vol
cone; `[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS leverage;
`[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml, p.222-223]`
DSR cumulative (n_global=516).
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_015
**n_configs:** 6
**cumulative_n_trials_global:** 510 → **516**

## TL;DR

- ⚠️ **EQUITY-TILT HYPOTHESIS REJECTED.** Reducing UGL weight from
  basket3-invvol's ~45% (KILL_LOOP #5 anchor 1.4689 / CAGR 22.65% / crisis
  3/4) down to 16.7% (eqtilt66), 7.5% (eqtilt85), or 0% (basket2_QU)
  recovers some CAGR (22.65% → 27.81% → 30.05% → 28.99%) but **NEVER
  clears the 31.08% Phase 3 floor** AND collapses crisis attribution
  (3/4 → 1/4 → 1/4 → 2/4). The gold-weight ↔ crisis-rescue trade-off
  is structural — there is no sweet spot that simultaneously clears
  Phase 3 CAGR floor AND retains the basket3-invvol crisis cushion.
  KILL_LOOP #8/#9/#12 ALL NOT FIRED — no eqtilt variant achieves
  Phase 3 candidate, strict_superset, or crisis-≥2/4 strict_superset.
- ✅ **All 3 calibration anchors PRESERVED bit-exact** (KILL_LOOP #3,
  #4, #5 ALL NOT FIRED):
  - baseline_qld_zroz Sortino 1.3240 = iter 011-014 baseline
    (drift 0.0000) — **6th-generation reproducibility**.
  - single_K4lv25_g25_rvp70_cashx Sortino 1.3951 = iter 013 g25 / iter
    014 strict_superset (drift 0.0000).
  - basket3invvol_K4lv25_g25_rvp70_cashx Sortino 1.4689 / CAGR 22.65% /
    MDD -32.82% / crisis 3/4 = iter 014 triple-stack (drift 0.0000).
- 🎯 ✅ **G1 PBO 0.3333 — LOOP 2nd-MIN** (after iter 011's 0.3056).
  Iter trajectory: 005 0.881 → 006 0.798 → 007 0.552 → 008 0.5675 →
  009 0.3770 → 010 0.3929 → 011 0.3056 → 012 0.4960 → 013 0.5437 →
  014 0.4405 → **015 0.3333**. Mechanism-mix-diverse 5-distinct-topology
  recipe held bit-exact even when 4 of 6 configs share K4_AND_lv25 ×
  ratevol-p70 × CASHX axis (iter 014 used 5 distinct topologies; iter
  015 uses 5 distinct ON-leg topologies which proved sufficient).
  KILL_LOOP #7 FIRED — POSITIVE TAG.
- 🏆 **best config = single_K4lv25_g25_rvp70_cashx replica** (iter 014
  strict_superset bit-exact). Sortino 1.3951 (+0.0705 vs T3d-K2 1.3246),
  CAGR 31.47% (+0.39pp), end_eq 1.129×, MDD -47.69%, beats_winner=True
  (3rd loop iter to confirm), phase3_performance_candidate=True,
  **strict_superset=True**. Score 76.5 STRONG. **NO NEW finding** —
  this is calibration preservation, not novel discovery.
- 🥈 **basket3-invvol replica** (iter 014 triple-stack bit-exact).
  Sortino 1.4689 (LOOP MAX), Sharpe 1.0097 (LOOP MAX), MDD -32.82%
  (LOOP MIN), G2 DSR p_cum 5.47e-04, G6 99% low 0.633, G4 OOS 1.076,
  G5 FWD 1.186 — all loop-max metrics PRESERVED bit-exact. crisis 3/4
  (2000_dotcom + 2008_GFC + 2022_rates). beats_winner=True but
  phase3_performance_candidate=False (CAGR 22.65% << 31.08% floor;
  end_eq 0.056×). Score 81.5 STRONG.
- ⚠️ **basket3-eqtilt66 (2/3 QLD + 1/6 UPRO + 1/6 UGL):** Sortino
  1.4330, CAGR **27.81%** (+5.16pp vs invvol but still **-3.27pp below
  Phase 3 floor**), end_eq 0.284× (much improved vs invvol's 0.056×
  but still below 1.05 floor), MDD -39.16%, crisis **1/4** (LOST
  2000_dotcom AND 2022_rates — gold cushion at 16.7% insufficient).
  beats_winner=True (Sortino > 1.3746) but phase3=False. Score 79.5.
- ⚠️ **basket3-eqtilt85 (0.85 QLD + 0.075 UPRO + 0.075 UGL) + g0 + p80
  + IEF:** Sortino 1.3603 (just below 1.3746 threshold), CAGR 30.05%
  (closest eqtilt to floor but still -1.03pp below), end_eq 0.563×,
  crisis 1/4. beats_winner=False, phase3=False. Score 76.5.
- 🤔 **basket2_QU (invvol QLD/UPRO; no UGL) — SURPRISE 2/4 crisis:**
  Sortino 1.3434, CAGR 28.99%, end_eq 0.406×, crisis **2/4**
  (2000_dotcom + 2008_GFC). **Without ANY gold sleeve, basket2_QU
  still rescues 2000_dotcom** — the diversification effect of QLD+UPRO
  invvol weighting reduces equity exposure during the dotcom crash
  enough to capture the rescue, even with no gold.
  KILL_LOOP #11 NOT FIRED (basket2_QU crisis count = 2 > 1, contradicting
  the pre-registered ablation expectation). Score 79.0.
- ✅ **Phase 3 momentum:** 1/6 (only single replica). Iter 014 had 3/6.
  This iter's eqtilt experiments **structurally fail Phase 3 across
  the entire UGL-weight spectrum** (0%, 7.5%, 16.7%, 45%).
- 🎯 **strict_superset:** **1/6** — only the single replica
  (calibration; no NEW finding). Loop's strict_superset list unchanged
  in content (still 3 unique configs from iter 012/014; iter 015 adds
  the 4th replica entry but no new strategy).
- 📌 **Capital remains 100% Plan C per mandate §1.** Best score 76.5
  (single replica) and 81.5 (basket3-invvol replica) < 90 deploy bar.
  No automatic capital realloc. Per LOOP_PROTOCOL §"Mandate §1
  reinforcement", `docs/CURRENT_STATE.md` "Active Hunts" entry
  preserved untouched.

## Configs tested

| # | Name (suffix after `qld_voteK2_sma250_100_vol21_40_ar30_eqb_`) | ON-leg | weights | upgrade | gamma | ratevol | alt-OFF | upg% | rv% | blend% | turn/y |
|---|---|---|---|---|--:|---|---|--:|--:|--:|--:|
| 1 | `baseline_qld_zroz` | single QLD | — | none | 0.00 | none | — | 0.0% | 0.0% | 0.0% | 2.61 |
| 2 | `single_K4lv25_g25_rvp70_cashx` | single QLD/TQQQ | — | K4_AND_lv25 | 0.25 | p70 | CASHX | 7.1% | 10.9% | 13.5% | 5.38 |
| 3 | `basket3invvol_K4lv25_g25_rvp70_cashx` | basket3-invvol60 (QLD/UPRO/UGL) with QLD↔TQQQ on upgrade | invvol60 | K4_AND_lv25 | 0.25 | p70 | CASHX | 7.3% | 11.2% | 13.8% | 5.38 |
| 4 | **`basket3eq66_K4lv25_g25_rvp70_cashx`** ← PRIMARY | basket3-eqtilt fixed-weight | (0.667, 0.167, 0.167) | K4_AND_lv25 | 0.25 | p70 | CASHX | 7.3% | 11.2% | 13.8% | 5.38 |
| 5 | `basket3eq85_K4lv25_g0_rvp80_ief` | basket3-eqtilt fixed-weight | (0.850, 0.075, 0.075) | K4_AND_lv25 | 0.00 | p80 | IEFSIM | 7.3% | 9.4% | 7.6% | 5.00 |
| 6 | `basket2QU_K4lv25_g25_rvp70_cashx` | basket2-invvol60 (QLD/UPRO; no UGL) | invvol60 | K4_AND_lv25 | 0.25 | p70 | CASHX | 7.3% | 11.2% | 13.8% | 5.38 |

**Mechanism-mix audit:**

- ON-leg type: 5 distinct (single, basket3-invvol, basket3-eqtilt66,
  basket3-eqtilt85, basket2-QU-invvol)
- Upgrade gate: 2 distinct (none, K4_AND_lv25)
- Gamma: 2 distinct (0, 0.25)
- Ratevol: 3 distinct (none, 70, 80)
- Alt-OFF: 3 distinct (none, CASHX, IEFSIM)

5 distinct ON-leg topology buckets across 6 configs (vs iter 014's 5
buckets / PBO 0.4405; iter 011's 6 buckets / PBO 0.3056). G1 PBO 0.3333
suggests ON-leg structural diversity > 5-axis diversity for CSCV mechanism
diversity.

## Results — gross metrics per dataset

### Sortino_lh56y (annualised, target=0)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| baseline_qld_zroz | 1.3240 | 1.4275 | 1.3525 | 1.6068 |
| single_K4lv25_g25_rvp70_cashx | 1.3951 | 1.4863 | 1.4115 | 1.6553 |
| basket3invvol_K4lv25_g25_rvp70_cashx | **1.4689** | 1.5440 | 1.3919 | 1.4937 |
| basket3eq66_K4lv25_g25_rvp70_cashx | 1.4330 | 1.5097 | 1.4150 | 1.5778 |
| basket3eq85_K4lv25_g0_rvp80_ief | 1.3603 | 1.4554 | 1.3942 | 1.6385 |
| basket2QU_K4lv25_g25_rvp70_cashx | 1.3434 | 1.4244 | 1.3535 | 1.5562 |

### Sharpe_lh56y

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| baseline_qld_zroz | 0.9187 | 0.9851 | 0.9203 | 1.0883 |
| single_K4lv25_g25_rvp70_cashx | 0.9682 | 1.0250 | 0.9576 | 1.1166 |
| basket3invvol_K4lv25_g25_rvp70_cashx | **1.0097** | 1.0568 | 0.9357 | 0.9986 |
| basket3eq66_K4lv25_g25_rvp70_cashx | 0.9928 | 1.0445 | 0.9669 | 1.0681 |
| basket3eq85_K4lv25_g0_rvp80_ief | 0.9466 | 1.0084 | 0.9522 | 1.1038 |
| basket2QU_K4lv25_g25_rvp70_cashx | 0.9398 | 0.9907 | 0.9269 | 1.0533 |

### CAGR_lh56y / MDD_lh56y

| Config | CAGR | MDD | end_eq vs baseline |
|---|---:|---:|---:|
| baseline_qld_zroz | 31.08% | -64.50% | 1.000× |
| single_K4lv25_g25_rvp70_cashx | 31.47% | -47.69% | 1.129× |
| basket3invvol_K4lv25_g25_rvp70_cashx | 22.65% | **-32.82%** | 0.056× |
| basket3eq66_K4lv25_g25_rvp70_cashx | 27.81% | -39.16% | 0.284× |
| basket3eq85_K4lv25_g0_rvp80_ief | 30.05% | -56.04% | 0.563× |
| basket2QU_K4lv25_g25_rvp70_cashx | 28.99% | -43.05% | 0.406× |

## Gates per config

| Config | G1 PBO | G2 DSR_loc | G2 DSR_cum (n=516) | G3 wf%above | G4 OOS | G5 FWD | G6 99%low | G7 |
|---|--:|---:|---:|--:|---:|---:|---:|---:|
| All configs share G1 PBO | **0.3333** | — | — | — | — | — | — | — |
| baseline_qld_zroz | 0.3333 | 3.29e-06 | 2.94e-03 | 7/8 | 0.823 | 0.708 | 0.547 | +0.000 |
| single_K4lv25_g25_rvp70_cashx | 0.3333 | 7.33e-07 | 1.09e-03 | 7/8 | 1.004 | 0.915 | 0.598 | +0.000 |
| basket3invvol_K4lv25_g25_rvp70_cashx | 0.3333 | 2.51e-07 | 5.47e-04 | 7/8 | 1.076 | 1.186 | **0.633** | +0.000 |
| basket3eq66_K4lv25_g25_rvp70_cashx | 0.3333 | 4.77e-07 | 8.25e-04 | 7/8 | 1.067 | 1.038 | 0.626 | +0.000 |
| basket3eq85_K4lv25_g0_rvp80_ief | 0.3333 | 2.08e-06 | 2.16e-03 | 7/8 | 1.007 | 0.971 | 0.579 | +0.000 |
| basket2QU_K4lv25_g25_rvp70_cashx | 0.3333 | 2.62e-06 | 2.50e-03 | 7/8 | 0.966 | 0.926 | 0.575 | +0.000 |

All gates pass for all configs. G1 PBO 0.3333 < 0.50 hard gate (loop
2nd-MIN). G2 DSR cumulative (n_global=516) all < 0.05.

## Comparação vs winner T3d-K2 (Sortino 1.3246 / CAGR 31.08%)

| Config | sortino | edge_vs_1.3246 | cagr | edge_vs_31.08% | end_eq_ratio | crisis | WC | beats_winner | phase3 | strict |
|---|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| baseline_qld_zroz | 1.3240 | -0.0006 | 31.08% | +0.00pp | 1.000× | 1/4 | T | F | F | F |
| **single_K4lv25_g25_rvp70_cashx** ← strict_superset | **1.3951** | **+0.0705** | 31.47% | +0.39pp | 1.129× | 1/4 | **T** | **T** | **T** | **T** |
| basket3invvol_K4lv25_g25_rvp70_cashx | **1.4689** | +0.1443 | 22.65% | -8.43pp | 0.056× | **3/4** | **T** | **T** | F | F |
| **basket3eq66_K4lv25_g25_rvp70_cashx** ← PRIMARY (rejected) | 1.4330 | +0.1084 | **27.81%** | -3.27pp | 0.284× | 1/4 | T | **T** | F | F |
| basket3eq85_K4lv25_g0_rvp80_ief | 1.3603 | +0.0357 | 30.05% | -1.03pp | 0.563× | 1/4 | T | F | F | F |
| basket2QU_K4lv25_g25_rvp70_cashx | 1.3434 | +0.0188 | 28.99% | -2.09pp | 0.406× | **2/4** | T | F | F | F |

## Phase 3 performance diagnostics

**The equity-tilt experiment surfaces the structural CAGR ↔ crisis
trade-off across the entire UGL-weight spectrum:**

| UGL weight | Config | CAGR | crisis | Phase 3 candidate? |
|---:|---|---:|:---:|:---:|
| 0% | basket2_QU | 28.99% | 2/4 | F (CAGR -2.09pp) |
| 7.5% | basket3-eqtilt85 | 30.05% | 1/4 | F (CAGR -1.03pp) |
| 16.7% | basket3-eqtilt66 | 27.81% | 1/4 | F (CAGR -3.27pp) |
| ~45% (invvol) | basket3-invvol | 22.65% | 3/4 | F (CAGR -8.43pp) |

**No monotonic relationship between UGL weight and (CAGR, crisis).**
Adding a small UGL sleeve (7.5% → 16.7%) does NOT add crisis rescue
(stays at 1/4) but DOES lower CAGR (30.05% → 27.81%) — strictly
worse on both axes. The basket3-invvol's 3/4 crisis is structurally
tied to ~45% UGL weight (invvol equilibrium for QLD/UPRO/UGL); below
~25-30% UGL the crisis cushion collapses entirely. The CAGR ceiling
is governed by UPRO/UGL tail effects + post-1985 synth-component
inception (basket3 effective evaluation window starts mid-1980s due
to combined warmup). The single-asset K4_AND_lv25 strategy at CAGR
31.47% (above floor) without basket diversification remains the only
Phase 3-compliant config of the iter — same as iter 014.

**Surprising finding:** basket2_QU (no UGL) rescues 2000_dotcom AND
2008_GFC (crisis 2/4) — the QLD+UPRO invvol diversification alone
provides some structural defense against the dotcom crash. This
contradicts the pre-registered KILL_LOOP #11 expectation that no-UGL
should give crisis ≤ 1/4. Mechanism: invvol weighting on QLD+UPRO
during high-vol regimes reduces total equity exposure (invvol scales
DOWN with rising vol), which captures part of the 2000_dotcom drawdown
even without a defensive sleeve.

**Verdict:** **the equity-tilt-vs-invvol path to crisis-≥2/4
strict_superset is empirically closed.** Future iters should explore
orthogonal mechanisms: (a) DYNAMIC basket weights (regime-conditional
equity-vs-gold tilt); (b) re-entry triggers on the ratevol gate;
(c) VIX-percentile / VRP forward-looking gates; (d) leverage
overlays on iter 014 single-asset strict_superset.

## Plots

- `plots/01_equity_curves.png` — log-scale lh_56y for all 6 configs +
  SPY 1× b&h.
- `plots/02_drawdown_curves.png` — lh_56y drawdowns; basket3-invvol
  has shallowest MDD (-32.82% LOOP MIN).
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe; basket3-invvol
  highest baseline.
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR; single_K4lv25_g25
  highest sustained.
- `plots/05_regime_attribution.png` — % time in equity ON state.
- `plots/06_pct_beat_spy.png` — cumulative % of 3y windows beating SPY.
- `plots/07_crisis_attribution.png` — crisis MDD vs SPY (4 windows).

## Tables

- `tables/per_config_metrics.csv` — gross metrics per (config, dataset).
- `tables/gates_pass_fail.csv` — gates G1-G7 + active% + Phase 3 flags.

## Verdict

- **`best_config`**: `qld_voteK2_sma250_100_vol21_40_ar30_eqb_single_
  K4lv25_g25_rvp70_cashx` (calibration replica; iter 014 strict_superset
  bit-exact). Score 76.5 STRONG. Sortino 1.3951, CAGR 31.47%,
  beats_winner=True, phase3_performance_candidate=True,
  strict_superset=True (sorted by strict_superset → phase3 → Sortino).
- **`any_beats_winner`**: **True** (3 of 6: single replica, basket3-
  invvol replica, basket3eq66 — all > 1.3746 threshold).
- **`any_phase3_performance_candidate`**: **True** (1 of 6: single
  replica only).
- **`any_strict_superset`**: **True** (1 of 6: single replica
  calibration; **NOT a NEW finding**).
- **`any_phase3_eqtilt`**: **False** (0 of 3 eqtilt variants — CORE
  HYPOTHESIS REJECTED).
- **`any_strict_superset_eqtilt`**: **False** (0 of 3 — STRONGEST
  HYPOTHESIS REJECTED).
- **`any_eqtilt_crisis_2or3_of_4`**: **False** (0 of 3 eqtilt achieve
  crisis ≥ 2/4; basket2_QU achieves 2/4 but is the no-UGL ablation,
  not an "eqtilt" variant).
- **`sortino_edge_vs_winner`** (best): +0.0705 (single replica;
  calibration).
- **`cagr_edge_vs_winner`** (best): +0.0039 (+0.39pp; single replica).
- **`end_equity_ratio_vs_baseline`** (best): 1.129× (single replica).

## KILL_LOOP status

| # | Rule | Fired? | Notes |
|---|---|:---:|---|
| 1 | success_tag (any beats_winner) | **FIRED** ✅ | 3 configs; 4th loop iter (after 009/010/012/014) |
| 2 | decisive_fail (best Sortino < 1.20) | NOT FIRED | best 1.3951 >> 1.20 |
| 3 | replica_sanity_baseline (drift > 0.005) | NOT FIRED ✅ | 1.3240 = iter 011-014 (drift 0.0000) — **6th-gen replica** |
| 4 | replica_sanity_single_K4lv25_g25 | NOT FIRED ✅ | 1.3951 = iter 013/014 (drift 0.0000) |
| 5 | replica_sanity_basket3invvol_K4lv25_g25 | NOT FIRED ✅ | 1.4689 = iter 014 triple-stack (drift 0.0000) |
| 6 | PBO_blowup (≥ 0.55) | NOT FIRED | 0.3333 << 0.55 |
| 7 | PBO_held (< 0.50) — POSITIVE TAG | **FIRED** ✅ | 0.3333 LOOP 2nd-MIN |
| 8 | phase3_perf_candidate_eqtilt | NOT FIRED ❌ | 0/3 eqtilt — CORE HYPOTHESIS REJECTED |
| 9 | strict_superset_eqtilt | NOT FIRED ❌ | 0/3 — STRONGEST HYPOTHESIS REJECTED |
| 10 | eqtilt_crisis_2or3_of_4 | NOT FIRED ❌ | 0/3 — gold cushion structurally tied to ~45% UGL weight |
| 11 | basket2_QU_no_crisis | NOT FIRED 🤔 | basket2_QU crisis=2 (>1) — invvol QLD/UPRO surprisingly captures 2000_dotcom |
| 12 | eqtilt_crisis_strict_superset | NOT FIRED ❌ | 0/3 — full hypothesis chain blocked |

## Conclusion

**Iter 015 cleanly REJECTS the equity-tilt-vs-invvol-gold hypothesis.**
Reducing UGL weight from basket3-invvol's ~45% to 16.7% / 7.5% / 0%
recovers some CAGR (22.65% → 27-30%) but never clears the 31.08% Phase
3 floor AND collapses the 3/4 crisis cushion to 1/4 (eqtilt) or 2/4
(no-UGL ablation). The CAGR ↔ crisis-rescue trade-off is **structural,
not parametric** — there is no fixed-weight tilt that simultaneously
clears Phase 3 CAGR floor and retains basket3-invvol's crisis 3/4.

**Methodologically positive:** all 3 calibration anchors (baseline,
single g25, basket3-invvol) preserved bit-exact (drift 0.0000). G1
PBO 0.3333 — LOOP 2nd-MIN — confirms 5-distinct-ON-leg-topology recipe
holds even when 4 of 6 configs share K4lv25/g25/p70/CASHX axis.

**Surprising finding:** basket2_QU (no UGL) rescues 2000_dotcom AND
2008_GFC (crisis 2/4). The QLD+UPRO invvol weighting structurally
de-risks during high-vol regimes, providing some 2000_dotcom defense
without ANY gold sleeve.

**Best config = single_K4lv25_g25 calibration replica** — bit-exact
copy of iter 014's strict_superset. **No NEW strict_superset config**
introduced this iter; loop's strict_superset list content unchanged.

**Capital remains 100% Plan C per mandate §1.** Best score 76.5 < 90
deploy bar. No automatic capital realloc.

## Next iter ideas

(a) **Dynamic regime-conditional basket weights** — switch between
single-QLD (high CAGR, crisis 1/4) and basket3-invvol (lower CAGR,
crisis 3/4) based on regime indicator (e.g., VIX percentile, ratevol,
or Gayed yield-curve gate). When equity-favorable: single QLD;
when defensive regime: basket3-invvol with full UGL weight. Hypothesis:
regime-conditional switching could recover CAGR in bull regimes while
preserving crisis cushion in defensive regimes. **Highest expected
value: addresses the structural trade-off the static eqtilt cannot
unlock.** Cite `[risk_parity, p.80-81, ch.4]` Qian RORO regime;
`[gayed, p.40-50]` yield-curve regime; `[risk_parity, p.110, ch.5]`
fixed-weight diversification return.

(b) **2020 COVID re-entry trigger overlay** on iter 014's strict_
superset — Carver-style re-arm hysteresis on ratevol gate so it
RELEASES exposure when on_signal flips OFF→ON after N days.
`[systematic_trading, p.212, ch.13]`. Targets the 2020_covid hole
in iter 014 single strict_superset (crisis 1/4 → potential 2/4 via
re-entry trigger).

(c) **VIX-percentile / VRP overlay** on the upgrade gate or ON-leg
allocation — forward-looking implied-vol gate orthogonal to all
realised-vol gates currently in the loop. `[volatility_trading, ch.7]`
Sinclair VRP; `[hull_white_options]` for VIX-percentile semantics.

(d) **Leverage overlay on iter 014 strict_superset** — add a 1.1×-
1.5× multiplier on the ON-leg returns when conditions are very
favorable (e.g., K=4 AND lowvol25 AND VIX < 20), conditional on Phase
3 PBO/DSR holding. Risk: parametric clustering may regress G1 PBO.
`[leverage_for_the_long_run, ch.4-5, p.40-60]`.

(e) **Tax / fees stress on iter 014 strict_superset** — turnover
5.38/y; quantify net-of-tax (Lei 14.754 swing tax 15%) impact;
diagnostic only.
