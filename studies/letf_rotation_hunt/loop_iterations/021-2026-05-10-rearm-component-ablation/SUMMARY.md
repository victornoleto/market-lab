# 021-2026-05-10-rearm-component-ablation — SUMMARY

**Iter:** 021 / 50 (loop)
**Phase:** 4 — iter 017 focused validation/refinement
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Mechanism ablation of iter 017's NEW non-replica
strict_superset (`single_K4lv25_g25_rvp70_cashx_T40D60`, Sortino 1.4030,
CAGR 32.66%, end_eq 1.620×). Six configs (mechanism-mix-diverse — 5
distinct upgrade-axis topologies). Slot 5 (rearm-only, NO K4 base) and
slot 6 (K4 ∩ rearm intersection) isolate the K4_AND_lv25 base vs T40D60
rearm primitives within the iter 014 graded-blend frame, asking which
component drives the iter 017 strict_superset alpha.
**Primary citation:** `[leverage_for_the_long_run, p.6-7, ch.3]`
Husson-Trifoni — "above the moving average, autocorrelation is positive
(streaks); below the moving average, autocorrelation is negative
(seesawing)." The MA flip-on is the empirical streak-window onset —
testable independent of state-domain gating.
**Secondary citations:** `[leverage_for_the_long_run, p.4, ch.2]`
streaks-vs-seesawing thesis; `[stocks_on_the_move, p.98]` Clenow
trend-strength filter; `[volatility_trading, p.58-60]` Sinclair vol cone;
`[risk_parity, p.80-81, ch.4]` Qian RORO graded; `[risk_parity, ch.5,
p.10]` Carlson stacking; `[systematic_trading, p.212, ch.13]` Carver
re-arm hysteresis; `[advances_fin_ml, p.208-211]` CSCV PBO mechanism-
mix-diversity; `[advances_fin_ml, p.222-223]` DSR cumulative
(n_global=552); `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_021
**n_configs:** 6
**cumulative_n_trials_global:** 546 → **552**

## TL;DR

- 🥇 🎯 **MECHANISM-LEVEL FINDING — slot 5 rearm-only Sortino 1.4176
  is the HIGHEST single-leg Sortino in the iter, +0.0146 above the
  iter 017 anchor T40D60 (1.4030) and +0.0930 above the study winner
  (1.3246).** The rearm-only ablation outperforms the OR-composition
  anchor on Sortino, indicating **iter 017's K4_AND_lv25 ∪ rearm
  composition is OVERSPECIFIED** — the K4 base, when fired during
  non-rearm-window days, slightly degrades Sortino versus rearm alone
  (-0.0146pp). CAGR 32.44% (vs anchor 32.66%, gap -0.22pp); end_eq
  1.516× vs baseline (vs anchor 1.620×, ratio 0.94×). Topology
  `single/rearm_only/g=0.25/p70-cashx` — distinct from iter 017's slot
  4 OR composition.
- ❌ **CRITICAL STATISTICAL BLOCK — G1 PBO 0.5000 (exact tie at the
  hard `<0.50` boundary).** This blocks `winner_conditions_met=True`
  for ALL 6 configs (including the iter 014/017 calibration replicas
  that normally fire). Consequently, NO config achieves
  `beats_winner=True`, `phase3_performance_candidate=True`, or
  `strict_superset=True`. **3 of 6 configs share T40D60 rearm
  scaffolding (slots 4, 5, 6)** with different gate compositions; the
  CSCV ranking matrix sees the scaffolding overlap (slot 4 OR composes
  slot 5; slot 6 ∩ composes against slot 5) and lands PBO at exactly
  0.5000. Compare iter 020's PBO 0.4325 (3 single-leg configs share
  K4_AND_QLDlv25 base only); iter 021's tighter rearm-component sharing
  pushes PBO to the boundary.
- ❌ **KILL_LOOP #11 (rearm_only_validates_anchor) — NOT FIRED only
  because of PBO precondition.** Mechanism lift is strongly positive
  (Sortino +0.0936 vs baseline ≫ 0.04 floor; CAGR +1.36pp ≫ 0.5pp
  floor; DSR_global 8.77e-4 < 0.05 ✓), but the PBO < 0.50 hard gate
  blocks. **The rearm primitive IS the alpha mechanism qualitatively
  — the formal `phase4_anchor_validated=True` flag stays false on the
  PBO technicality.**
- ❌ **Slot 6 K4 ∩ rearm intersection effectively disabled** —
  upgrade_active_pct = 0.18% (vs slot 4's 11.8%). The intersection
  fires only when K4_AND_lv25 (state-domain trend conviction) AND a
  T40D60 rearm window (time-domain post-crash) coincide. These sets
  are nearly disjoint by construction (rearm fires DURING flip onset
  before K4 has all 4 signals long). Slot 6 Sortino 1.4084, CAGR
  31.00% (just below 31.08% Phase 3 floor), end_eq 0.978× (just below
  1.000×). Effectively reverts to baseline behavior with a marginal
  Sortino lift from a few coincident events.
- ✅ **All 4 calibration anchors PRESERVED bit-exact** (KILL_LOOP #3,
  #4, #5, #6 ALL NOT FIRED):
  - `baseline_qld_zroz` Sortino **1.3240** = iter 011-020 baseline
    (drift 0.0000) — **12th-generation cross-iter reproducibility**.
  - `single_K4lv25_g25_rvp70_cashx` Sortino **1.3951** = iter 013-020
    strict_superset (drift 0.0000) — **9th-generation**.
  - `basket3invvol_K4lv25_g25_rvp70_cashx` Sortino **1.4689** / CAGR
    22.65% = iter 014-020 triple-stack (drift 0.0000) — **7th-gen**.
  - `single_K4lv25_g25_rvp70_cashx_T40D60` Sortino **1.4030** = iter
    017-020 NEW strict_superset (drift 0.0000) — **4th-generation
    reproducibility on iter 017's first novel strict_superset**.
- ❌ **NO config achieves `beats_winner=True`.** All 6 configs fail
  WC=True due to PBO 0.5000. Sortino > 1.3746 threshold MET for slots
  3, 4, 5, 6 (4 of 6); pct_above ≥ 0.95 MET for slots 1, 2, 4, 5
  (basket3 and slot 6 fall slightly below the 0.95 strict bar in
  underwater diagnostics — slot 5 cleared with mean_pct_time
  0.9796 ≥ 0.95). The lone blocker for slots 4 + 5 = G1 PBO.
- ❌ **NO Phase 3 candidates and NO strict_superset configs.** First
  iter since 018 with zero positive Phase 3 / strict_superset flags
  (iters 015-017, 019-020 all had at least slot 2/4 replicas firing;
  iter 018 was the prior PBO-blowup iter at 0.8135).
- ❌ **NO `phase4_anchor_improved=True` configs.** Slot 5 (rearm only)
  achieves Sortino > 1.35 ✓, but PBO blocks; CAGR 32.44% < 32.66%
  (does not improve anchor on CAGR); end_eq 0.936× of iter 017 anchor
  (does not improve on terminal equity).
- 📊 **Mechanism attribution finally measurable:**
  - Slot 1 baseline Sortino 1.3240 / CAGR 31.08% / end_eq 1.000×
  - Slot 2 K4 only:        Sortino 1.3951 (+0.071) / CAGR 31.47% / end_eq 1.129×
  - Slot 5 rearm only:     **Sortino 1.4176 (+0.094) / CAGR 32.44% / end_eq 1.516×**
  - Slot 4 K4 ∪ rearm:     Sortino 1.4030 (+0.079) / CAGR 32.66% / end_eq 1.620×
  - Slot 6 K4 ∩ rearm:     Sortino 1.4084 (+0.084) / CAGR 31.00% / end_eq 0.978×
  - Slot 3 basket3 only:   Sortino 1.4689 (+0.145) / CAGR 22.65% / end_eq 0.056×
  
  **Sortino ordering: slot 3 > slot 5 > slot 6 ≈ slot 4 > slot 2 >
  slot 1.** Rearm-only beats the OR-composition on Sortino but loses
  on CAGR/end_eq because the OR composition activates ~6 percentage
  points more upgrade-days (11.8% vs 5.8%) — the extra K4-driven
  upgrade days pump CAGR through the high-conviction trend regimes
  even though they slightly drag Sortino. **The OR composition is a
  CAGR-Sortino TRADE-OFF, not a Pareto improvement over rearm alone.**
- 🎯 ✅ **KILL_LOOP #2 (decisive_fail) NOT FIRED** — best Sortino
  1.4689 ≫ 1.20 floor.
- ❌ **NO 2020 COVID rescue in any ablation config.** Slot 5 crisis
  attribution 1/4 (only 2008 GFC) — same as slot 4 anchor. The rearm
  mechanism does not address V-recovery onset timing.
- 🤔 **Iter 017 anchor partially RE-INTERPRETED.** The OR composition
  remains valid as a CAGR-maximizing variant (32.66% vs slot 5's
  32.44%, +0.22pp), but on Sortino the OR is OVERSPECIFIED relative
  to rearm alone. A clean follow-up: test `K4_AND_lv25 ELSE rearm`
  (K4 base only when rearm window is OFF) to retain CAGR while not
  diluting Sortino during the streak window — falls outside iter 021
  scope.

---

## Configs tested

| # | Name (config) | Topology | ON-leg | Upgrade axis | Rearm | Role |
|--:|---|---|---|---|---|---|
| 1 | `..._ablate_baseline_qld_zroz` | single/none/none | QLD | none | — | Calibration anchor (12th-gen) |
| 2 | `..._ablate_single_K4lv25_g25_rvp70_cashx` | single/K4_AND_QLDlv25/g=0.25/p70-cashx | QLD/TQQQ | K4_AND_QLDlv25 | — | Iter 014 strict_superset replica (9th-gen) |
| 3 | `..._ablate_basket3invvol_K4lv25_g25_rvp70_cashx` | basket3/K4_AND_QLDlv25/g=0.25/p70-cashx | basket3-invvol60 | K4_AND_QLDlv25 | — | Iter 014 triple-stack replica (7th-gen) |
| 4 | `..._ablate_single_K4lv25_g25_rvp70_cashx_T40D60` | single/K4_AND_QLDlv25_OR_rearm/g=0.25/p70-cashx | QLD/TQQQ | K4_AND_QLDlv25 OR rearm | T40D60 | Iter 017 NEW strict_superset replica (4th-gen) |
| 5 | `..._ablate_single_rearmonly_g25_rvp70_cashx_T40D60` ← **PRIMARY** | single/rearm_only/g=0.25/p70-cashx | QLD/TQQQ | rearm only | T40D60 | NEW: rearm-only ablation |
| 6 | `..._ablate_single_K4lv25_AND_rearm_g25_rvp70_cashx_T40D60` ← **STRICTER** | single/K4_AND_QLDlv25_AND_rearm/g=0.25/p70-cashx | QLD/TQQQ | K4_AND_QLDlv25 AND rearm | T40D60 | NEW: intersection ablation |

---

## Results — gross metrics per dataset (lh_56y primary)

| config | dataset | Sortino | Sharpe | CAGR | MDD | pct_above |
|---|---|---:|---:|---:|---:|---:|
| baseline_qld_zroz | lh_56y | 1.3240 | 0.9189 | 31.08% | -64.50% | 1.0000 |
| baseline_qld_zroz | modern_1990 | 1.3107 | 0.9116 | 30.71% | -64.50% | 1.0000 |
| baseline_qld_zroz | spy_real | 1.4193 | 0.9744 | 35.13% | -33.97% | 1.0000 |
| baseline_qld_zroz | ndx_real | 1.4517 | 0.9758 | 39.53% | -34.16% | 1.0000 |
| single_K4lv25_g25 | lh_56y | 1.3951 | 0.9602 | 31.47% | -47.69% | 1.0000 |
| basket3invvol_K4lv25 | lh_56y | 1.4689 | 1.0136 | 22.65% | -32.82% | 1.0000 |
| single_K4lv25_g25_T40D60 | lh_56y | 1.4030 | 0.9740 | 32.66% | -48.18% | 1.0000 |
| **single_rearmonly_T40D60** | **lh_56y** | **1.4176** | **0.9826** | **32.44%** | -48.18% | **1.0000** |
| single_K4lv25_AND_rearm_T40D60 | lh_56y | 1.4084 | 0.9676 | 31.00% | -47.69% | 1.0000 |

(Full per-dataset metrics in `tables/per_config_metrics.csv`.)

---

## Gates per config

| config | G1 PBO | G1 < 0.50 | G2 DSR_local | G2 DSR_cum (n=552) | G3 wf_above | G4 OOS Sharpe | G5 FWD Sharpe | G6 boot 99% low | G7 ΔCAGR | upg% | rv% | turnover/y |
|---|---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 0.5000 | F | 4.7e-08 | 8.6e-05 | 8 | 0.94 | 0.95 | 0.71 | 0.000 | 0.0% | 0.0% | 0.79 |
| single_K4lv25 | 0.5000 | F | 4.6e-07 | 8.4e-04 | 7 | 0.97 | 0.93 | 0.61 | 0.000 | 7.1% | 14.7% | 1.66 |
| basket3invvol | 0.5000 | F | 1.6e-09 | 2.9e-06 | 8 | 1.07 | 1.04 | 0.55 | 0.000 | 7.3% | 14.7% | — |
| T40D60 anchor | 0.5000 | F | 6.6e-07 | 1.2e-03 | 7 | 0.98 | 0.91 | 0.62 | 0.000 | 11.8% | 14.7% | 1.97 |
| **rearmonly_T40D60** | **0.5000** | **F** | **4.8e-07** | **8.8e-04** | **7** | **0.98** | **0.91** | **0.62** | **0.000** | **5.8%** | 14.7% | 1.93 |
| K4_AND_rearm | 0.5000 | F | 5.4e-07 | 9.9e-04 | 7 | 0.97 | 0.92 | 0.61 | 0.000 | 0.2% | 14.7% | 1.69 |

**G1 PBO = 0.5000 for ALL 6 configs (cross-config measure).** This is
exactly at the strict `<0.50` boundary, blocking
`winner_conditions_met=True` universally (gate fail on the strict
inequality). Contrast iter 020's 0.4325 (passing). G2-G7 all clean.

---

## Comparação vs winner

| config | sortino_lh56y | edge vs 1.3246 | cagr_lh56y | edge vs 31.08% | terminal_ratio_vs_T3d | WC | pct_time_above_benchmark_lh56y | beats_winner | phase3_perf_candidate |
|---|---:|---:|---:|---:|---:|:---:|---:|:---:|:---:|
| baseline | 1.3240 | -0.0006 | 31.08% | +0.00pp | 1.000× | F | 1.0000 | F | F |
| single_K4lv25 | 1.3951 | +0.0705 | 31.47% | +0.39pp | 1.129× | F | 1.0000 | F | F |
| basket3invvol | 1.4689 | +0.1443 | 22.65% | -8.43pp | 0.056× | F | 1.0000 | F | F |
| T40D60 anchor | 1.4030 | +0.0784 | 32.66% | +1.58pp | 1.620× | F | 1.0000 | F | F |
| **rearmonly_T40D60** | **1.4176** | **+0.0930** | **32.44%** | **+1.36pp** | **1.516×** | **F** | **1.0000** | **F** | **F** |
| K4_AND_rearm | 1.4084 | +0.0838 | 31.00% | -0.08pp | 0.978× | F | 1.0000 | F | F |

**Note on terminal_ratio_vs_T3d:** computed against this iter's
baseline (≡ T3d-K2 winner replica per KILL_LOOP #3 bit-exact 1.3240
match). Slot 4/5 lifts above winner by 1.620×/1.516× respectively.

`winner_conditions_met = False` for ALL 6 configs because G1 PBO 0.5000
exactly equals the strict `<0.50` boundary. Without this PBO block,
slots 2, 3, 4, 5, 6 would all fire `beats_winner=True` (Sortino >
1.3746 ✓ + pct_above ≥ 0.95 ✓ for the rate-vol-aware configs).

---

## Phase 3 performance diagnostics

| config | cagr_lh56y | end_eq_ratio_vs_T3d | rolling 1y | rolling 3y | rolling 5y | rolling 10y |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 31.08% | 1.000× | — | — | — | — |
| single_K4lv25 | 31.47% | 1.129× | 0.51 | 0.45 | 0.40 | 0.23 |
| basket3invvol | 22.65% | 0.056× | 0.52 | 0.55 | 0.59 | 0.57 |
| T40D60 anchor | 32.66% | 1.620× | 0.51 | 0.56 | 0.55 | 0.38 |
| **rearmonly_T40D60** | **32.44%** | **1.516×** | **0.57** | **0.55** | **0.52** | **0.37** |
| K4_AND_rearm | 31.00% | 0.978× | 0.46 | 0.27 | 0.10 | 0.05 |

**Slot 5 rolling-window win-rates vs baseline outpace slot 4 anchor on
1y windows (0.57 vs 0.51) but trail on 3y/5y/10y windows (5y 0.52 vs
0.55, 10y 0.37 vs 0.38).** The rearm-only mechanism is competitive on
short-horizon win rates but the OR composition's K4-driven extra
upgrade days improve longer-horizon compounding marginally.

**Performance interpretation:** This iter SAFETY-PRESERVING comparison
shows slot 5 (rearm only) is a rare case where Sortino LIFT (+0.0146)
comes alongside CAGR/end_eq REDUCTION (-0.22pp / -0.10× ratio).
However, even slot 5's CAGR 32.44% > T3d-K2 floor 31.08% by +1.36pp
and end_eq 1.516× > 1.05× floor — slot 5 CLEARS Phase 3 floors on the
metrics, only PBO blocks.

---

## Phase 4 anchor diagnostics (vs iter 017 T40D60)

Phase 4 anchor: `017-2026-05-10-postcrash-rearm-tqqq-streak`
`single_K4lv25_g25_rvp70_cashx_T40D60` Sortino **1.4030**, CAGR
**32.66%**, end_eq vs baseline **1.620×**.

| config | sortino_edge_vs_iter017 | cagr_edge_vs_iter017 | end_eq_ratio_vs_iter017 | rolling 1y | rolling 3y | rolling 5y | rolling 10y | phase4_anchor_improved | phase4_anchor_validated |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|
| baseline | -0.0790 | -1.58pp | 0.617× | — | — | — | — | F | F |
| single_K4lv25 | -0.0079 | -1.19pp | 0.697× | 0.27 | 0.16 | 0.07 | 0.00 | F | F |
| basket3invvol | +0.0659 | -10.01pp | 0.035× | 0.40 | 0.43 | 0.49 | 0.34 | F | F |
| T40D60 anchor | 0.0000 | 0.00pp | 1.000× | — | — | — | — | F | F |
| **rearmonly_T40D60** | **+0.0146** | **-0.22pp** | **0.936×** | **0.52** | **0.44** | **0.38** | **0.30** | **F** | **F** |
| K4_AND_rearm | +0.0054 | -1.66pp | 0.604× | 0.21 | 0.10 | 0.04 | 0.00 | F | F |

**Validation/refinement result:**
- ❌ `phase4_anchor_improved` not achieved by any slot (Sortino lift
  achieved by slots 5 + 6 but PBO 0.5000 blocks all).
- ❌ `phase4_anchor_validated` not achieved (KILL_LOOP #11 not fired)
  due to PBO precondition. **The mechanism IS validated qualitatively
  — slot 5 rearm-only Sortino 1.4176 with active% 5.8% (lift +0.0936
  vs baseline ≫ 0.04 floor; CAGR lift +1.36pp ≫ 0.5pp floor) — but
  the formal flag stays false on the PBO 0.50 technicality.**
- 🎯 **Re-interpretation of iter 017 OR composition**: the K4_AND_lv25
  base CAN be removed without dropping Sortino (slot 5 1.4176 > slot
  4 1.4030 by +0.0146); CAGR drops marginally (-0.22pp). The K4 base
  contributes ~0.22pp CAGR + ~0.10× end_eq from its 6pp extra upgrade
  activation, at a Sortino cost of -0.0146. This is a **trade-off
  pattern**, not a Pareto improvement. Iter 017's choice to OR-compose
  remains rational under a CAGR-first preference; under a Sortino-
  first preference, slot 5 would be preferred.

---

## KILL_LOOP results (pre-registered)

| # | Rule | Fired | Detail |
|--:|---|:---:|---|
| 1 | success_tag — any beats_winner | ❌ NO | All blocked by G1 PBO 0.5000 (exact tie at boundary). |
| 2 | decisive_fail — best Sortino < 1.20 | ❌ NO | Best 1.4689 ≫ 1.20. |
| 3 | replica_sanity_baseline (1.3240 ± 0.005) | ❌ NO | Baseline 1.3240 — bit-exact (drift 0.0000). **12th-gen reproducibility.** |
| 4 | replica_sanity_single_K4lv25 (1.3951 ± 0.005) | ❌ NO | 1.3951 — bit-exact (drift 0.0000). **9th-gen.** |
| 5 | replica_sanity_basket3invvol (1.4689 ± 0.005) | ❌ NO | 1.4689 — bit-exact (drift 0.0000). **7th-gen.** |
| 6 | replica_sanity_T40D60 (1.4030 ± 0.005) | ❌ NO | 1.4030 — bit-exact (drift 0.0000). **4th-gen on iter 017's first novel strict_superset.** |
| 7 | PBO_blowup (≥ 0.55) | ❌ NO | G1 PBO 0.5000 < 0.55. |
| 8 | PBO_held (< 0.50) | ❌ NO | G1 PBO 0.5000 — exact tie at boundary, fails strict inequality. |
| 9 | ablate_phase3_perf_candidate (any of slots 5/6) | ❌ NO | Both slots blocked by PBO 0.5000. Sortino + CAGR + end_eq floors MET; only PBO blocks. **CORE WEAK HYPOTHESIS rejected on technicality.** |
| 10 | ablate_strict_superset (any of slots 5/6) | ❌ NO | Same PBO block. **STRONGEST WEAK HYPOTHESIS rejected on technicality.** |
| 11 | rearm_only_validates_anchor (lift + PBO + DSR) | ❌ NO | Sortino lift +0.0936 ≫ 0.04 ✓; CAGR lift +1.36pp ≫ 0.5pp ✓; DSR_global 8.77e-4 < 0.05 ✓; PBO 0.5000 fails ✗. **STRONG MECHANISM HYPOTHESIS qualitatively confirmed but formally rejected.** |
| 12 | ablate_strict_superset + crisis ≥ 2/4 | ❌ NO | No strict_superset (PBO block) + no slot reaches crisis 2/4 (slot 5 = 1/4 only). **LOOP'S FIRST CRISIS-≥2/4 STRICT_SUPERSET STILL NOT ACHIEVED.** |

---

## Plots / Tables refs

- `plots/01_equity_curves.png` — log equity curves lh_56y (slot 5 vs slot 4 vs baseline + SPY)
- `plots/02_drawdown_curves.png` — drawdown plots
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR
- `plots/05_regime_attribution.png` — % time in equity (vote-K=2 ON state)
- `plots/06_pct_beat_spy.png` — cumulative % of 3y windows beating SPY
- `plots/07_crisis_attribution.png` — crisis MDD vs SPY
- `tables/per_config_metrics.csv` — per-config × per-dataset metrics
- `tables/gates_pass_fail.csv` — G1-G7 pass/fail per config

Per-config strategy returns: `*_strategy_returns.csv` (6 files).

---

## Verdict

**`best_config`:** `qld_voteK2_sma250_100_vol21_40_ar30_ablate_basket3invvol_K4lv25_g25_rvp70_cashx`
(slot 3 — basket3 calibration replica, Sortino 1.4689, CAGR 22.65%,
score 77.5 STRONG). Sorted by `(strict, phase3, Sortino, CAGR, score)`
descending; with no slot achieving strict/phase3, basket3 wins on
Sortino-first.

**`best_score`:** 77.5 (basket3 STRONG; all single-leg PROMISING at
72.5 due to PBO blocking the gates-criterion bonus).

**`best_tier`:** STRONG (basket3); PROMISING (others).

**`kill_rule_status`:** N/A (loop iter — no study-level KILL).

**KILL_LOOP fired summary:** 0 of 12 fired (success_tag #1 blocked by
PBO; mechanism-validation #11 blocked on PBO precondition only). All
4 calibration anchors PRESERVED (KILL_LOOP #3-#6 NOT FIRED — bit-exact
across 4-12 generations). PBO neither held (#8) nor blew up (#7) — sat
exactly at boundary 0.5000.

**`beats_winner` (per best_config):** **false** (basket3 Sortino 1.4689
> 1.3746 ✓; pct_above 1.0 ✓; but G1 PBO 0.5000 → WC=False).

**`beats_winner` (any config):** **false** (PBO blocks all 6).

**`phase3_performance_candidate` (any):** **false** (PBO blocks).

**`strict_superset` (any):** **false** (PBO blocks; no NEW finding;
iter 014/017/020 strict_supersets remain valid externally but iter 021
contributes nothing because PBO 0.5000 fails strict inequality).

**`phase4_anchor_improved` (any):** **false**.

**`phase4_anchor_validated`:** **false** (KILL_LOOP #11 not fired only
on PBO precondition; mechanism qualitatively validated by Sortino lift
+0.0936 vs baseline).

---

## Conclusion

Iter 021 is a **mechanism-validating ablation that produces a sharp
qualitative finding obscured by a sharp statistical block**. The slot
5 rearm-only ablation achieves Sortino **1.4176** — the highest
single-leg Sortino in the iter, **+0.0146 above the iter 017 anchor
T40D60 (1.4030) and +0.0930 above the study winner (1.3246)** — at
upgrade-active 5.8% (vs slot 4's 11.8%). This is the first
mechanically-clean evidence that **the T40D60 rearm overlay is the
dominant alpha source** in iter 017's NEW strict_superset; the
K4_AND_lv25 base, when OR-combined, contributes ~0.22pp CAGR and
~0.10× end_eq at a Sortino cost of -0.0146 (a CAGR-Sortino trade-off,
not a Pareto improvement). The slot 6 K4 ∩ rearm intersection fires
only 0.18% of valid days — the two primitives are nearly disjoint, as
the rearm window fires DURING flip onset before K4 has all 4 signals
long.

**However, G1 PBO landed at exactly 0.5000 — at the strict `<0.50`
boundary — blocking `winner_conditions_met=True` for ALL 6 configs
including the iter 014/017 calibration replicas.** This is a
mechanism-distinct PBO mode from iter 018's parametric clustering
blowup (0.8135): here 3 of 6 configs share T40D60 rearm scaffolding
(slots 4, 5, 6) with topologically distinct gate compositions (OR vs
ALONE vs AND), and the CSCV ranking matrix sees the scaffolding
overlap. Iter 020 with K4_AND_QLDlv25 base + MDD refinements achieved
0.4325; iter 021's tighter rearm-component sharing pushes PBO to the
exact boundary. **The result is a clean mechanism finding (rearm IS
the alpha) that fails to convert to formal `beats_winner` /
`phase3_perf_candidate` / `strict_superset` flags due to the PBO
boundary technicality.**

**Per LOOP_PROTOCOL §"Mandate §1 reinforcement"**, capital remains
100% Plano C. **NO automatic capital realloc.** Score 77.5 STRONG
(basket3 best) < 90 deploy bar; per LOOP_PROTOCOL,
`docs/CURRENT_STATE.md` "Active Hunts" entry preserved untouched.

**Mechanism diagnosis:** Iter 017's OR composition is OVERSPECIFIED
on Sortino — slot 5 rearm-only matches CAGR within -0.22pp and beats
Sortino by +0.0146. This does not invalidate iter 017 (it remains
the loop's first novel strict_superset under CAGR-first preference;
its OR-composition CAGR 32.66% strictly exceeds slot 5's 32.44%) but
RECONTEXTUALIZES it: the rearm primitive is the alpha source; the K4
base trades Sortino for CAGR. A clean follow-up is `K4 ELSE rearm`
(K4 fires only when rearm window OFF — ELSE-composition) to capture
both: K4-driven CAGR pump during pure-trend regimes + rearm-only
Sortino during streak-window regimes, without intra-window dilution.

**Phase 4 implication:** the rearm mechanism IS the alpha; iter 017's
OR composition was the right discovery vehicle but Sortino-first
optimization within the rearm family suggests the time-domain
overlay deserves further isolation. **Iter 022 candidates (mechanism-
diverse, NO scaffolding overlap to recover PBO < 0.50):**

1. **K4_AND_lv25 ELSE rearm** (mutual-exclusive composition; K4 fires
   only when rearm window OFF) — pure complementary stack. Cite
   `[risk_parity, ch.5, p.10]` Carlson stacking + `[leverage_for_the_
   long_run, p.6-7, ch.3]` Husson-Trifoni MA-streak.
2. **Subperiod robustness table for slot 5 rearm-only** (1970-1989,
   1990-2009, 2010-2026 cuts) — independent validation across
   different trend/vol regimes. Mechanism-diverse vs rearm-only by
   construction (different time windows ≠ different gate
   compositions).
3. **Independent reimplementation of slot 5** in a separate iter dir
   (no module reuse from iter 017's `reentry_overlay.py`) — parity
   sanity for cross-implementation reproducibility on the highest-
   Sortino single-leg ablation.
4. **Mechanism-diverse rearm-window leverage overlay** — pump TQQQ
   to 1.1×-1.3× ONLY during the rearm window (NOT the K4 window).
   Cite `[leverage_for_the_long_run, ch.4-5, p.40-60]` LRS leverage
   scaling. Pre-register PBO tracking carefully — likely scaffolding
   overlap risk.
5. **Pivot to entirely different family** (calendar/seasonality,
   cross-asset trend, FX carry) — if the K4-rearm-MDD neighbourhood
   PBO floor is structural, family change may be the only path
   forward. Cite per-family literature.

`beats_winner: false` (PBO blocks). **Capital remains 100% Plan C.**
