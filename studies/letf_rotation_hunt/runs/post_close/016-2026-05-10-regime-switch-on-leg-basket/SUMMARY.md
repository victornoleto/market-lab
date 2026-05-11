# 016-2026-05-10-regime-switch-on-leg-basket — SUMMARY

**Iter:** 016 / 50 (loop)
**Phase:** 3 — performance-first beater hunt
**Tier:** loop_iter (post-close hunt)
**Hypothesis:** Regime-conditional ON-leg basket switching — switch
between iter 014's two endpoints (single QLD/TQQQ for high CAGR vs
basket3-invvol QLD/UPRO/UGL for crisis cushion) based on a regime
indicator (lowvol50 percentile, K=4 vote of 4 signals). Tests whether
dynamic switching can recover Phase 3 CAGR floor (>31.08%) while
retaining basket3-invvol's crisis 3/4 cushion — the structural trade-
off that iter 015's static fixed-weight eqtilt could not unlock.
Targets the loop's first crisis-≥2/4 strict_superset.
**Primary citation:** `[risk_parity, p.80-81, ch.4]` Qian RORO regime-
conditional master-gate.
**Secondary citations:** `[risk_parity, p.110, ch.5]` Qian fixed-weight
diversification (frames dynamic vs static); `[risk_parity, p.11, ch.1]`
Qian invvol over-allocation; `[risk_parity, ch.5, p.10]` Carlson cap-
efficient stacking; `[volatility_trading, p.58-60]` Sinclair vol cone
(lowvol50 regime); `[stocks_on_the_move, p.98]` Clenow trend-strength
(K=4 regime); `[systematic_trading, ch.10]` Carver inverse-vol;
`[leverage_for_the_long_run, ch.4-5, p.40-60]` Husson-Trifoni LRS;
`[advances_fin_ml, p.208-211]` CSCV PBO; `[advances_fin_ml, p.222-223]`
DSR cumulative (n_global=522).
**Datetime UTC:** see `verdict.json["datetime_utc"]`
**Engine version:** loop_iter_016
**n_configs:** 6
**cumulative_n_trials_global:** 516 → **522**

## TL;DR

- ⚠️ **REGIME-SWITCH HYPOTHESIS REJECTED.** All 3 regime-switch variants
  (lv50 g25, K4 g25, lv50 g0 IEF) preserve basket3-invvol's crisis 3/4
  cushion (KILL_LOOP #10 FIRED ✅) but **NONE clear the 31.08% Phase 3
  CAGR floor**. Best regsw CAGR is K4's 23.61% (-7.47pp); best regsw
  Sortino is K4's 1.3647 (just below 1.3746 beats threshold).
  KILL_LOOP #8/#9/#11 ALL NOT FIRED — no regsw config achieves
  phase3=True, strict_superset=True, or strict_superset+crisis≥2/4.
- 🤔 **STRUCTURAL FINDING:** the basket3-invvol's CAGR penalty is too
  severe to be diluted by dynamic switching. Even at 41.7% single (lv50
  gate steady-state) the basket-leg drag during the other 58.3% of days
  collapses end equity to 0.057×. The CAGR ↔ crisis-rescue trade-off
  remains structural across BOTH static (iter 015) AND dynamic (iter
  016) approaches. Iter 015's `[risk_parity, p.110, ch.5]` Qian
  diversification-return calculus does not help; iter 016's `[risk_
  parity, p.80-81, ch.4]` Qian RORO master-gate does not help either.
- 🤔 **SURPRISE — K4 regime > lv50 regime by Sortino** (1.3647 > 1.2631
  by +0.1016): K4 only switches to single during high-conviction trend
  regimes (~20% of time, matching iter 011 K=4 stats), routing single
  during the equity-bull years where its CAGR boost matters most. lv50
  routes single 41.7% of the time including some choppy-but-low-vol
  windows that don't deliver the CAGR boost. **KILL_LOOP #12 NOT FIRED**
  (pre-registered expectation that lv50 dominates K4 contradicted —
  the "smarter" regime gate is the trend-conviction K=4 vote, NOT the
  vol-percentile gate).
- 🤔 **SURPRISE — slot 6 (lv50 + IEF + g0 + p80) achieves 2020_covid
  rescue** (different from slot 4's 2022_rates rescue): the IEF OFF-leg
  + g=0 (no graded blend) + ratevol-p80 (less aggressive override)
  produces a different crisis profile. Crisis 3/4 = dotcom + GFC + COVID
  (slot 6) vs dotcom + GFC + 2022 (slot 4 / 5). **The COVID-vs-2022
  distinction is governed by the OFF-leg + ratevol mechanics, not the
  regime-switch ON-leg.** First loop iter to surface this attribution.
- ✅ **All 3 calibration anchors PRESERVED bit-exact** (KILL_LOOP #3,
  #4, #5 ALL NOT FIRED):
  - baseline_qld_zroz Sortino 1.3240 = iter 011-015 baseline
    (drift 0.0000) — **7th-generation reproducibility**.
  - single_K4lv25_g25_rvp70_cashx Sortino 1.3951 = iter 013/014/015
    strict_superset (drift 0.0000).
  - basket3invvol_K4lv25_g25_rvp70_cashx Sortino 1.4689 = iter 014/015
    triple-stack (drift 0.0000).
- ✅ **G1 PBO 0.3730** — held below 0.50 (KILL_LOOP #7 FIRED POSITIVE)
  but slightly higher than iter 015's 0.3333 due to slots 4 and 6
  sharing the lv50 regime gate (parametric clustering). Iter trajectory:
  005 0.881 → 006 0.798 → 007 0.552 → 008 0.5675 → 009 0.3770 →
  010 0.3929 → 011 0.3056 → 012 0.4960 → 013 0.5437 → 014 0.4405 →
  015 0.3333 → **016 0.3730**. 4-distinct-ON-leg-topology recipe held.
- 🏆 **best config = single_K4lv25_g25_rvp70_cashx replica** (iter
  013/014/015 strict_superset bit-exact). Sortino 1.3951 (+0.0705 vs
  T3d-K2), CAGR 31.47%, end_eq 1.129×, MDD -47.69%, beats_winner=True
  (4th loop iter), phase3_performance_candidate=True,
  **strict_superset=True**. Score 76.5 STRONG. **NO NEW finding** —
  calibration preservation, not novel discovery.
- 🥈 **basket3-invvol replica** (iter 014/015 triple-stack bit-exact).
  Sortino 1.4689 (LOOP MAX), Sharpe 1.0097 (LOOP MAX), MDD -32.82%
  (LOOP MIN), G2 DSR p_cum 5.54e-04, G6 99% low 0.633 — all loop-max
  metrics PRESERVED bit-exact. Crisis 3/4 (2000+2008+2022).
  beats_winner=True, phase3=False (CAGR floor), score 81.5 STRONG.
- ⚠️ **lv50 regsw PRIMARY (slot 4):** Sortino 1.2631 (just below 1.3746
  beats threshold), CAGR 22.71% (-8.37pp), MDD -33.77% (LOOP-MIN-tier),
  end_eq 0.057×, crisis **3/4** (dotcom + GFC + 2022_rates). The
  regime gate retains crisis cushion bit-exactly with basket3 anchor
  but at zero CAGR benefit — the 41.7% time in single does NOT
  meaningfully shift CAGR (single is concentrated during equity-bull
  years where ALL configs do well; basket3 dominates during the
  drawdown windows that drag the long-run CAGR). beats_winner=False,
  phase3=False. Score 78.5.
- ⚠️ **K4 regsw ORTHOGONAL (slot 5):** Sortino 1.3647, CAGR 23.61%
  (-7.47pp), end_eq 0.076×, crisis 3/4. Despite using single only 20.2%
  of the time, **K4 OUTPERFORMS lv50 on Sortino** because the K=4 vote
  trigger is a stronger conviction signal — when it fires, single's
  CAGR boost is statistically more concentrated in high-Sharpe periods.
  Still fails Phase 3 by CAGR floor; basket3 drag dominates the 79.8%
  basket time. Score 81.5.
- ⚠️ **lv50 g0 IEF (slot 6):** Sortino 1.2412, CAGR 23.33%, end_eq
  0.070×, crisis 3/4 — **but the 3rd crisis is COVID, not 2022_rates**
  (different OFF-leg + g=0 mechanics). Score 78.5.
- ✅ **Phase 3 momentum:** 1/6 (only single replica). Iter 015 also 1/6.
  This iter's regsw experiments **structurally fail Phase 3** as iter
  015's eqtilt did — confirming the trade-off is mechanism-agnostic.
- 🎯 **strict_superset:** **1/6** — only the single replica
  (calibration; no NEW finding). Loop's strict_superset list unchanged
  in content (still 3 unique configs from iter 012/014; iter 016 adds
  the 5th replica entry but no new strategy).
- 📌 **Capital remains 100% Plan C per mandate §1.** Best score 76.5
  (single replica) and 81.5 (basket3-invvol + K4 regsw) < 90 deploy
  bar. No automatic capital realloc. Per LOOP_PROTOCOL §"Mandate §1
  reinforcement", `docs/CURRENT_STATE.md` "Active Hunts" entry
  preserved untouched.

## Configs tested

| # | Name (suffix after `qld_voteK2_sma250_100_vol21_40_ar30_regsw_`) | ON-leg | regime gate | upgrade | gamma | ratevol | alt-OFF | regime single% | turn/y |
|---|---|---|---|---|--:|---|---|--:|--:|
| 1 | `baseline_qld_zroz` | single QLD | — | none | 0.00 | none | — | — | 2.61 |
| 2 | `single_K4lv25_g25_rvp70_cashx` | single QLD/TQQQ | — | K4_AND_lv25 | 0.25 | p70 | CASHX | — | 5.38 |
| 3 | `basket3invvol_K4lv25_g25_rvp70_cashx` | basket3-invvol60 | — | K4_AND_lv25 | 0.25 | p70 | CASHX | — | 5.38 |
| 4 | **`lv50_K4lv25_g25_rvp70_cashx`** ← PRIMARY | regsw-lv50 | vol_21d < 50th pct | K4_AND_lv25 | 0.25 | p70 | CASHX | **41.7%** | 5.38 |
| 5 | **`K4_K4lv25_g25_rvp70_cashx`** ← ORTHOGONAL | regsw-K4 | K=4 vote fires | K4_AND_lv25 | 0.25 | p70 | CASHX | **20.2%** | 5.38 |
| 6 | **`lv50_K4lv25_g0_rvp80_ief`** ← MECH-DIV | regsw-lv50 | vol_21d < 50th pct | K4_AND_lv25 | 0.0 | p80 | IEFSIM | **41.7%** | 5.00 |

**Mechanism-mix audit:**

- ON-leg type: 4 distinct (single, basket3-invvol, regsw-lv50, regsw-K4)
- Upgrade gate: 2 distinct (none, K4_AND_lv25)
- Gamma: 2 distinct (0.0, 0.25)
- Ratevol: 3 distinct (none, p70, p80)
- Alt-OFF: 3 distinct (none, CASHX, IEFSIM)

4 distinct ON-leg topology buckets across 6 configs (vs iter 015's 5 / PBO
0.3333; iter 014's 5 / PBO 0.4405). G1 PBO 0.3730 — slightly worse than
iter 015 due to slots 4 and 6 sharing regsw-lv50 ON-leg (parametric-
variant cluster) but the K4 regsw + basket3 anchor + single anchor +
baseline keep the recipe broadly diverse.

## Results — gross metrics per dataset

### Sortino_lh56y (annualised, target=0)

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| baseline_qld_zroz | 1.3240 | 1.2217 | 1.0911 | 1.2890 |
| single_K4lv25_g25_rvp70_cashx | 1.3951 | 1.2905 | 1.1592 | 1.4071 |
| basket3invvol_K4lv25_g25_rvp70_cashx | **1.4689** | 1.3729 | 1.4352 | 1.5045 |
| lv50_K4lv25_g25_rvp70_cashx | 1.2631 | 1.1726 | 1.2613 | 1.4676 |
| K4_K4lv25_g25_rvp70_cashx | 1.3647 | 1.2752 | 1.2154 | 1.3958 |
| lv50_K4lv25_g0_rvp80_ief | 1.2412 | 1.1554 | 1.2757 | 1.4666 |

### Sharpe_lh56y

| Config | lh_56y | modern_1990 | spy_real | ndx_real |
|---|---:|---:|---:|---:|
| baseline_qld_zroz | 0.9187 | 0.8549 | 0.7768 | 0.9206 |
| single_K4lv25_g25_rvp70_cashx | 0.9682 | 0.9045 | 0.8343 | 1.0124 |
| basket3invvol_K4lv25_g25_rvp70_cashx | **1.0097** | 0.9649 | 1.0232 | 1.0761 |
| lv50_K4lv25_g25_rvp70_cashx | 0.8823 | 0.8320 | 0.9012 | 1.0491 |
| K4_K4lv25_g25_rvp70_cashx | 0.9504 | 0.9044 | 0.8770 | 1.0061 |
| lv50_K4lv25_g0_rvp80_ief | 0.8671 | 0.8184 | 0.9059 | 1.0404 |

### CAGR_lh56y / MDD_lh56y / end_eq

| Config | CAGR | MDD | end_eq vs baseline |
|---|---:|---:|---:|
| baseline_qld_zroz | 31.08% | -64.50% | 1.000× |
| single_K4lv25_g25_rvp70_cashx | 31.47% | -47.69% | 1.129× |
| basket3invvol_K4lv25_g25_rvp70_cashx | 22.65% | **-32.82%** | 0.056× |
| lv50_K4lv25_g25_rvp70_cashx | 22.71% | -33.77% | 0.057× |
| K4_K4lv25_g25_rvp70_cashx | 23.61% | -36.01% | 0.076× |
| lv50_K4lv25_g0_rvp80_ief | 23.33% | -34.75% | 0.070× |

## Gates per config

| Config | G1 PBO | G2 DSR_loc | G2 DSR_cum (n=522) | G3 wf%above | G4 OOS | G5 FWD | G6 99%low | G7 |
|---|--:|---:|---:|--:|---:|---:|---:|---:|
| All configs share G1 PBO | **0.3730** | — | — | — | — | — | — | — |
| baseline_qld_zroz | 0.3730 | 3.29e-06 | 2.97e-03 | 6/8 | 0.823 | 0.708 | 0.547 | +0.000 |
| single_K4lv25_g25_rvp70_cashx | 0.3730 | 7.33e-07 | 1.10e-03 | 7/8 | 1.004 | 0.915 | 0.598 | +0.000 |
| basket3invvol_K4lv25_g25_rvp70_cashx | 0.3730 | 2.51e-07 | 5.54e-04 | 7/8 | 1.076 | 1.186 | **0.633** | +0.000 |
| lv50_K4lv25_g25_rvp70_cashx | 0.3730 | 1.30e-05 | 7.13e-03 | 8/8 | 1.038 | 1.098 | 0.504 | +0.000 |
| K4_K4lv25_g25_rvp70_cashx | 0.3730 | 1.84e-06 | 2.03e-03 | 8/8 | 1.079 | 1.197 | 0.559 | +0.000 |
| lv50_K4lv25_g0_rvp80_ief | 0.3730 | 1.97e-05 | 9.23e-03 | 8/8 | 1.029 | 1.129 | 0.501 | +0.000 |

All gates pass for all configs. G1 PBO 0.3730 < 0.50 hard gate (loop
3rd-MIN after iter 011's 0.3056 and iter 015's 0.3333). G2 DSR
cumulative (n_global=522) all < 0.05.

## Comparação vs winner T3d-K2 (Sortino 1.3246 / CAGR 31.08%)

| Config | sortino | edge_vs_1.3246 | cagr | edge_vs_31.08% | end_eq_ratio | crisis | WC | beats_winner | phase3 | strict |
|---|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|
| baseline_qld_zroz | 1.3240 | -0.0006 | 31.08% | +0.00pp | 1.000× | 1/4 | T | F | F | F |
| **single_K4lv25_g25_rvp70_cashx** ← strict_superset | **1.3951** | **+0.0705** | 31.47% | +0.39pp | 1.129× | 1/4 | **T** | **T** | **T** | **T** |
| basket3invvol_K4lv25_g25_rvp70_cashx | **1.4689** | +0.1443 | 22.65% | -8.43pp | 0.056× | **3/4** | **T** | **T** | F | F |
| **lv50_K4lv25_g25_rvp70_cashx** ← PRIMARY (rejected) | 1.2631 | -0.0615 | 22.71% | -8.37pp | 0.057× | **3/4** | F | F | F | F |
| **K4_K4lv25_g25_rvp70_cashx** ← K4 ablation (best regsw Sortino) | 1.3647 | +0.0401 | 23.61% | -7.47pp | 0.076× | **3/4** | T | F | F | F |
| **lv50_K4lv25_g0_rvp80_ief** ← surprise COVID rescue | 1.2412 | -0.0834 | 23.33% | -7.75pp | 0.070× | **3/4** | F | F | F | F |

## Phase 3 performance diagnostics

**Across the entire regime-switch spectrum, the structural CAGR ↔ crisis
trade-off persists:**

| Regime gate | single activation | CAGR | crisis | Phase 3 candidate? |
|---|---:|---:|:---:|:---:|
| Always single (iter 014 strict_superset) | 100% | 31.47% | 1/4 | **T** |
| K4 vote (slot 5) | 20.2% | 23.61% | 3/4 | F (CAGR -7.47pp) |
| lowvol50 (slot 4) | 41.7% | 22.71% | 3/4 | F (CAGR -8.37pp) |
| lowvol50 + IEF + g0 + p80 (slot 6) | 41.7% | 23.33% | 3/4 | F (CAGR -7.75pp) |
| Always basket3-invvol (iter 014 triple-stack) | 0% | 22.65% | 3/4 | F (CAGR -8.43pp) |

**Non-linear and non-monotonic CAGR vs regime activation:**

- 0% single → CAGR 22.65% (anchor)
- 20% single → CAGR 23.61% (only +0.96pp despite 1/5 of time in
  high-CAGR leg)
- 42% single → CAGR 22.71% (LESS than 20% single — slot 4 routing
  appears to underperform K4 routing)
- 100% single → CAGR 31.47% (recovers anchor)

The CAGR is **dominated by the basket3-invvol leg's structural drag**
during the bulk of the equity-bull years (1995-2000, 2003-2007,
2009-2020, 2023+). Even short single-asset windows during very-high-
return periods cannot pull CAGR above the floor when basket3 holds
during the rest of equity-bull time. The 20% K4 routing happens
disproportionately during high-Sharpe periods (K=4 fires when ALL
4 trend signals align), giving K4 a Sortino edge over lv50 (1.3647
vs 1.2631) but still no Phase 3 candidate.

**Surprising sub-finding:** slot 6 (lv50 + IEF + g0 + p80) achieves
crisis 3/4 with **2020_covid** rescued instead of 2022_rates. The IEF
OFF-leg + g=0 (no graded blend) + ratevol-p80 (less aggressive override)
produces a different crisis profile than slot 4 — same regime-switch
ON-leg but the OFF mechanics decide which 3 of 4 crises get rescued.
First loop iter to surface this attribution explicitly.

**Verdict:** **The dynamic regime-switch path to crisis-≥2/4
strict_superset is empirically closed.** The CAGR ↔ crisis-rescue
trade-off is **mechanism-agnostic** — neither static fixed-weight
(iter 015) nor dynamic regime-conditional (iter 016) approaches resolve
it. Future iters should explore orthogonal axes: (a) **leverage overlay**
on iter 014's strict_superset (multiplicative CAGR boost without basket
drag); (b) **2020 COVID re-entry trigger** on the iter 014
strict_superset (Carver re-arm — pushes crisis 1/4 → 2/4 without
touching basket); (c) **forward-looking VIX-percentile / VRP gates**
(orthogonal to all current realised-vol mechanics); (d) **crisis-
specific basket overlay** that activates ONLY during pre-registered
crisis windows (event-driven instead of regime-conditional).

## Plots

- `plots/01_equity_curves.png` — log-scale lh_56y for all 6 configs +
  SPY 1× b&h.
- `plots/02_drawdown_curves.png` — lh_56y drawdowns; basket3-invvol +
  all 3 regsw configs share shallowest MDD band (-32.82% to -36.01%).
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe; basket3-invvol
  highest baseline.
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR; single_K4lv25_g25
  highest sustained.
- `plots/05_regime_attribution.png` — % time in equity ON state.
- `plots/06_pct_beat_spy.png` — cumulative % of 3y windows beating SPY.
- `plots/07_crisis_attribution.png` — crisis MDD vs SPY (4 windows).

## Tables

- `tables/per_config_metrics.csv` — gross metrics per (config, dataset).
- `tables/gates_pass_fail.csv` — gates G1-G7 + regime activation +
  Phase 3 flags.

## Verdict

- **`best_config`**: `qld_voteK2_sma250_100_vol21_40_ar30_regsw_single_
  K4lv25_g25_rvp70_cashx` (calibration replica; iter 014 strict_superset
  bit-exact). Score 76.5 STRONG. Sortino 1.3951, CAGR 31.47%,
  beats_winner=True, phase3_performance_candidate=True,
  strict_superset=True (sorted by strict_superset → phase3 → Sortino).
- **`any_beats_winner`**: **True** (2 of 6: single replica, basket3-
  invvol replica — both > 1.3746 threshold).
- **`any_phase3_performance_candidate`**: **True** (1 of 6: single
  replica only).
- **`any_strict_superset`**: **True** (1 of 6: single replica
  calibration; **NOT a NEW finding**).
- **`any_phase3_regsw`**: **False** (0 of 3 regsw variants — CORE
  HYPOTHESIS REJECTED).
- **`any_strict_superset_regsw`**: **False** (0 of 3 — STRONGEST
  HYPOTHESIS REJECTED).
- **`any_regsw_crisis_2or3_of_4`**: **True** (3 of 3 regsw variants
  achieve crisis 3/4 — confirms regime-switch retains basket3-invvol
  cushion).
- **`any_regsw_strict_with_crisis`**: **False** (0 of 3 — loop's first
  crisis-≥2/4 strict_superset NOT achieved).
- **`lv50_dominates_K4`**: **False** (Sortino lv50 1.2631 < K4 1.3647 —
  pre-registered expectation contradicted; trend-conviction K=4 vote
  is the smarter regime gate by Sortino).
- **`sortino_edge_vs_winner`** (best): +0.0705 (single replica;
  calibration).
- **`cagr_edge_vs_winner`** (best): +0.0039 (+0.39pp; single replica).
- **`end_equity_ratio_vs_baseline`** (best): 1.129× (single replica).

## KILL_LOOP status

| # | Rule | Fired? | Notes |
|---|---|:---:|---|
| 1 | success_tag (any beats_winner) | **FIRED** ✅ | 2 configs; 5th loop iter (after 009/010/012/014/015) |
| 2 | decisive_fail (best Sortino < 1.20) | NOT FIRED | best 1.3951 >> 1.20 |
| 3 | replica_sanity_baseline (drift > 0.005) | NOT FIRED ✅ | 1.3240 = iter 011-015 (drift 0.0000) — **7th-gen replica** |
| 4 | replica_sanity_single_K4lv25_g25 | NOT FIRED ✅ | 1.3951 = iter 013/014/015 (drift 0.0000) |
| 5 | replica_sanity_basket3invvol_K4lv25_g25 | NOT FIRED ✅ | 1.4689 = iter 014/015 triple-stack (drift 0.0000) |
| 6 | PBO_blowup (≥ 0.55) | NOT FIRED | 0.3730 << 0.55 |
| 7 | PBO_held (< 0.50) — POSITIVE TAG | **FIRED** ✅ | 0.3730 LOOP 3rd-MIN |
| 8 | regsw_phase3_perf_candidate | NOT FIRED ❌ | 0/3 regsw — CORE HYPOTHESIS REJECTED |
| 9 | regsw_strict_superset | NOT FIRED ❌ | 0/3 — STRONGEST HYPOTHESIS REJECTED |
| 10 | regsw_crisis_2or3_of_4 | **FIRED** ✅ | 3/3 regsw achieve crisis 3/4 — cushion retention confirmed |
| 11 | regsw_strict_superset_with_crisis | NOT FIRED ❌ | 0/3 — loop's first crisis-≥2/4 strict_superset NOT achieved |
| 12 | regsw_lv50_dominates_K4 (DIAGNOSTIC) | NOT FIRED 🤔 | lv50 1.2631 < K4 1.3647 — pre-registered expectation contradicted; K4 trend-conviction is smarter regime gate by Sortino (+0.1016 edge) |

## Conclusion

**Iter 016 cleanly REJECTS the dynamic regime-switch hypothesis.**
Switching between iter 014's two endpoints (single QLD/TQQQ for high
CAGR vs basket3-invvol for crisis cushion) based on regime indicators
(lowvol50 percentile, K=4 vote) preserves the crisis 3/4 cushion (3/3
regsw configs achieve crisis 3/4) but never clears the 31.08% Phase 3
CAGR floor. Best regsw config is K4 g25 at CAGR 23.61% (-7.47pp below
floor); best regsw Sortino is 1.3647 (just below 1.3746 beats threshold).

**Combined with iter 015's eqtilt rejection, the loop now has TWO
independent rejections of the CAGR ↔ crisis trade-off resolution
attempt:**

| Approach | iter | CAGR best regsw/eqtilt | Phase 3? | crisis-≥2/4 strict? |
|---|---:|---:|:---:|:---:|
| Static fixed-weight tilt (eqtilt66/eqtilt85/basket2_QU) | 015 | 30.05% | F | F |
| Dynamic regime-switch (lv50/K4/lv50+IEF) | 016 | 23.61% | F | F |

**The CAGR ↔ crisis-rescue trade-off is structural and mechanism-
agnostic.** Future iters should pivot to orthogonal mechanisms that
preserve iter 014's strict_superset (single CAGR 31.47%, crisis 1/4)
without trading CAGR for crisis: leverage overlays, COVID re-entry
triggers, forward-looking VIX gates, or event-driven crisis overlays.

**Methodologically positive:** all 3 calibration anchors (baseline,
single g25, basket3-invvol) preserved bit-exact (drift 0.0000) for the
**7th generation** of cross-iter reproducibility. G1 PBO 0.3730 — LOOP
3rd-MIN — confirms 4-distinct-ON-leg-topology recipe holds even with
slots 4+6 sharing the lv50 regime gate.

**Surprising findings:**

1. **K4 regime > lv50 regime by Sortino** (1.3647 vs 1.2631; +0.1016
   edge). The trend-conviction K=4 vote, despite firing only 20.2% of
   the time, routes single during periods of strongest equity
   compounding — making it more efficient at capturing the high-CAGR
   leg's value than the steady-state 41.7% lv50 routing.
2. **Slot 6 (lv50 + IEF + g0 + p80) achieves COVID rescue instead of
   2022_rates rescue** — the OFF-leg + ratevol mechanics decide which 3
   of 4 crises get rescued, not the regime-switch ON-leg. First loop
   iter to surface this attribution explicitly.

**Best config = single_K4lv25_g25 calibration replica** — bit-exact
copy of iter 014's strict_superset. **No NEW strict_superset config**
introduced this iter; loop's strict_superset list content unchanged
(still 3 unique configs from iter 012/014; iter 016 adds the 5th
replica entry but no new strategy).

**Capital remains 100% Plan C per mandate §1.** Best score 76.5 < 90
deploy bar. No automatic capital realloc.

## Next iter ideas

(a) **Leverage overlay on iter 014 single strict_superset** — add a
1.1×–1.5× multiplier on the ON-leg returns when conditions are very
favorable (K=4 AND lowvol25 AND VIX < 20 OR similar conjunction).
**Highest expected value: directly addresses the structural CAGR
ceiling without trading away the strict_superset.** Risk: parametric
clustering may regress G1 PBO toward 0.50. Cite `[leverage_for_the_
long_run, ch.4-5, p.40-60]` Husson-Trifoni LRS; `[risk_parity, ch.5,
p.10]` Carlson cap-efficient stacking.

(b) **2020 COVID re-entry trigger overlay** on iter 014 single
strict_superset — Carver-style re-arm hysteresis on ratevol gate so it
RELEASES exposure when on_signal flips OFF→ON after N days. Target the
single 1/4 crisis hole (specifically 2020_covid). If successful, lifts
score from 76.5 (5/10 crisis) to ~82 (7.5/10 crisis) and remains within
the strict_superset frame. Cite `[systematic_trading, p.212, ch.13]`
Carver semi-automatic stop re-arm.

(c) **VIX-percentile / VRP overlay** on the upgrade gate (iter 010
idea #3 untouched) — forward-looking implied-vol gate orthogonal to
all realised-vol gates. Could replace the K4_AND_lv25 gate with K4 AND
VIX_pct < 25 AND VRP > 0 dual gate. Cite `[volatility_trading, ch.7]`
Sinclair VRP.

(d) **Event-driven crisis overlay** — a slot that activates basket3-
invvol ONLY during pre-defined crisis windows (e.g., 6m post any 200d
SPY MDD breach > 20%) and falls back to single otherwise. Different
from regime-switch (continuous gate) — the crisis window IS the regime
indicator. Risk: post-hoc crisis windows risk in-sample fitting; would
need rolling out-of-sample validation. Cite `[regime_change, ch.X]`
Chen-Tsang regime detection.

(e) **Tax / fees stress on iter 014 strict_superset** — turnover
5.38/y; quantify net-of-tax (Lei 14.754 swing tax 15%) impact;
diagnostic only.
