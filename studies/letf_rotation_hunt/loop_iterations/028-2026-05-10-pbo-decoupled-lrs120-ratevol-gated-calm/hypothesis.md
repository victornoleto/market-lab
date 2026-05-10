# Iter 028 — PBO-decoupled LRS1.20× ratevol-gated calm-only overlay

**Phase:** 4 — iter 017 focused validation/refinement
**Slug:** `pbo-decoupled-lrs120-ratevol-gated-calm`
**Datetime UTC (start):** 2026-05-10
**n_configs:** 6
**cumulative_n_trials_global before:** 588
**cumulative_n_trials_global after:** 594
**cumulative_n_trials_loop before:** 162
**cumulative_n_trials_loop after:** 168

## PRIMARY hypothesis (regime-conditioned LRS — modern-era Sortino lift)

Iter 027 closed the 5-point LRS magnitude scan (1.00, 1.05, 1.10, 1.15, 1.20)
on the rearm base within the iter 024-027 PBO-decoupled mechanism-mix layout.
Slot 6 LRS1.20× delivered the loop's strongest formal Phase 4 improvement
(Sortino 1.3786, CAGR 36.22%, end_eq vs iter 017 = 2.908×, **third
consecutive Pareto improvement** on the Phase 4 anchor frontier) but its
**modern-era subperiod Sortino (1.124-1.144 across 1990-2009 / 2010-2026)
landed BELOW the Phase 3 floor 1.20** by -0.056 to -0.076. Iter 027 explicitly
flagged "modern-era softness is structural to the rearm primitive" and that
LRS magnitude alone scales CAGR uniformly across subperiods without
addressing the modern-era softness.

**This iter pivots the LRS axis from MAGNITUDE to REGIME CONDITIONING.**
Specifically: apply LRS1.20× to the on-leg ONLY when the bond rate-vol
percentile gate (`ratevol_gate(rvp70, vol_window=60, pct_window=1260)`)
reports 0 (calm rate regime, ~70% of bars by construction; the 70th-percentile
threshold means the gate fires on ~30% of the time). On bars where ratevol
fires (high rate-vol regime), the on-leg keeps the bare 2× QLD exposure with
no LRS overlay.

Mechanically:
- ratevol fires on high bond-rate-volatility regimes — historically clustered
  in stress windows (1980s Volcker, 1994 rate-shock, 2008 GFC, 2020 COVID,
  2022 hike cycle). These are precisely the periods where LRS overlay
  amplifies drawdown disproportionately to the daily-rebalance vol-drag
  asymmetry (cf. Husson-Trifoni `[leverage_for_the_long_run, p.5-6]`
  ann-vol-<40% sweet spot — modern-era subperiods cluster vol around 35-45%
  on 2× equity).
- ratevol gating uses the BOND-vol signal (zroz returns), which is mechanically
  ORTHOGONAL to the equity-crash rearm signal. Low expected correlation →
  preserves PBO-decoupled framework. CSCV PBO mechanism diversity
  `[advances_fin_ml, p.208-211]`.
- Conservative regime conditioning preserves the canonical Husson-Trifoni
  "leverage only when above MA daily" rule `[leverage_for_the_long_run, p.13,
  ch.3]` and adds a vol-regime overlay á la Carver `[systematic_trading,
  p.212, ch.13]` — vol-scaled regime thresholds.

**Pre-registered prediction (slot 6):**
- Modern-era subperiod Sortino lifts to **≥ 1.20 (above Phase 3 floor)** on at
  least one of {1990-2009, 2010-2026} subperiods — **KEY HYPOTHESIS**.
- CAGR_lh56y lands between **slot 5 baseline (32.44%)** and **slot 6
  unconditional (36.22%)**, expected ≈ 33.5-35.5% (LRS active ~70% of ON
  days vs ~100% in iter 027 slot 6). This produces partial CAGR lift at
  ~50-80% efficiency vs unconditional LRS.
- Sortino_lh56y full-window between **slot 5 (1.4176)** and **slot 6 iter
  027 (1.3786)** — expected ≈ 1.39-1.42 (regime conditioning should
  improve Sortino full-window since stress-period LRS gets pruned).
- end_eq vs iter 017 > 1.0× (Phase 4 anchor improvement bar).
- G1 PBO < 0.50 (Phase 3 hard gate); the bond-vol gate is mechanically
  orthogonal to the equity-rearm signal — should preserve PBO-decoupled
  framework.

## SECONDARY hypothesis (Phase 4 axis pivot — REGIME after MAGNITUDE)

With iter 027 closing the LRS magnitude axis (practical claimable ceiling
identified at LRS1.20×), the next mechanically distinct improvement axis
is REGIME CONDITIONING. This iter probes the FIRST regime gate beyond the
ON-only gate established in iter 024-027. Three orthogonal regime gates
remain available for future iters:
- ratevol (this iter — bond-vol percentile)
- equity-vol regime (e.g., 21d realised vol percentile)
- term-structure regime (e.g., 10y-2y yield curve sign)

If this iter's slot 6 fires `phase4_anchor_improved=True` with a modern-era
Sortino lift, it validates the regime-conditioning axis as productive Phase
4 work and seeds 2-3 follow-on iters. If it FAILS to lift modern-era
Sortino while preserving CAGR, it provides falsification of the
regime-conditioning thesis on this gate and redirects effort to alternate
regime axes or non-rearm Phase 4 families (per iter 027 next-iter idea (d)).

## TERTIARY hypothesis (mechanism-diversity preservation)

Five preserved calibration anchors (slots 1-5) provide bit-exact
reproducibility checks against iters 011-027 baseline (18→19th-gen),
single_K4lv25_g25 (15→16th-gen), K4 + LRS1.05 (4→5th-gen), iter 017 OR-anchor
(10→11th-gen), and rearm-only INDEP IMPL (7→8th-gen). This iter must extend
the multi-iter reproducibility track record while introducing the new
regime-gated overlay only on slot 6.

## Configs (6, mechanism-mix-diverse — identical iter 024-027 layout except slot 6 LRS application gating)

| # | name | upgrade_mode | LRS mode | LRS factor | LRS gating | gen target | role |
|---|---|---|---|--:|---|---|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_baseline_qld_zroz` | none | off | 1.00 | n/a | 19th-gen | calibration anchor (replica) |
| 2 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx` | K4_AND_lv25 | off | 1.00 | n/a | 16th-gen | calibration anchor (replica) |
| 3 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx_unclrs105` | K4_AND_lv25 | uncond_on | 1.05 | unconditional during ON | 5th-gen | calibration anchor (replica) |
| 4 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_K4lv25_g25_rvp70_cashx_T40D60` | K4_OR_rearm_iter017 | off | 1.00 | n/a | 11th-gen | iter 017 OR-anchor replica |
| 5 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60` | rearmonly_indep | off | 1.00 | n/a | 8th-gen | iter 022 INDEP IMPL replica |
| 6 | `qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_rvgtdlrs120calm` (NEW) | rearmonly_indep | rvgtdlrs120calm | 1.20 | when ratevol_gate==0 (calm; ~70% of ON days) | n/a | NEW probe — regime-gated LRS |

Slot 6 mechanism: on a given day t with on_signal[t-1]==1 (RISK_ON), apply
LRS factor 1.20× to on-leg returns ONLY if ratevol_gate[t-1]==0 (calm rate
regime). When ratevol fires (high rate-vol regime), on-leg keeps unchanged
returns. When on_signal==0 (RISK_OFF), no LRS. This combines the canonical
Husson-Trifoni RISK_ON LRS rule `[leverage_for_the_long_run, p.13]` with a
Sinclair vol-cone regime gate `[volatility_trading, p.58-60]` /
Carver vol-scaled threshold `[systematic_trading, p.212, ch.13]`.

## Datasets

Same 4 datasets as iter 024-027 for direct comparability:
- `lh_56y` (1970-01-01 → 2026-04-30) — primary
- `modern_1990` (1990-01-01 → 2026-04-30) — modern era
- `spy_real` (2003-01-01 → 2026-04-30) — SPY tape
- `ndx_real` (2010-02-01 → 2026-04-30) — NDX tape

## Pre-registered KILL_LOOP conditions

| ID | name | rule | direction |
|---|---|---|---|
| 1 | success_tag | Any config has beats_winner=True (Sortino>1.3746 AND winner_conditions_met=True AND pct_above>=0.95) | POSITIVE |
| 2 | decisive_fail | Best Sortino_lh56y < 1.20 (Phase 3 floor) | NEGATIVE |
| 3 | replica_baseline | Baseline Sortino deviates from iter 011-027 baseline 1.3240 by > 0.005 (19th-gen) | NEGATIVE |
| 4 | replica_single_K4lv25_g25 | single_K4lv25_g25 deviates from iter 014-027 1.3951 by > 0.005 (16th-gen) | NEGATIVE |
| 5 | replica_T40D60_OR_iter017 | Slot 4 (iter 017 OR-anchor) deviates from 1.4030 by > 0.005 (11th-gen) | NEGATIVE |
| 6 | replica_rearmonly_T40D60 | Slot 5 (rearm-only INDEP IMPL) deviates from 1.4176 by > 0.005 (8th-gen) | NEGATIVE |
| 7 | replica_K4_unclrs105 | Slot 3 (K4 + LRS1.05) deviates from iter 024-027 anchor 1.3842 by > 0.005 (5th-gen) | NEGATIVE |
| 8 | PBO_blowup | G1 PBO ≥ 0.55 (NEW PBO mode like iter 023's 0.6548 — falsifies regime-gating's PBO-decoupled property) | NEGATIVE |
| 9 | PBO_held | G1 PBO < 0.50 (Phase 3 hard gate) — confirms regime-gating preserves PBO-decoupled framework | POSITIVE |
| 10 | rgtdlrs120calm_phase4_anchor_improved | Slot 6 phase4_anchor_improved=True (CAGR>32.66% OR end_eq_iter017>1.0× AND Sortino≥1.35 AND PBO<0.50 AND DSR<0.05) | POSITIVE |
| 11 | rgtdlrs120calm_strict_superset | Slot 6 strict_superset=True (Sortino>1.3746 AND winner_conditions_met AND phase3_perf_candidate) | POSITIVE |
| 12 | rgtdlrs120calm_modern_sortino_lift | Slot 6 modern subperiod Sortino ≥ 1.20 on AT LEAST ONE of {1990_2009, 2010_2026} — **KEY HYPOTHESIS** | POSITIVE |
| 13 | rgtdlrs120calm_partial_lift | Slot 6 CAGR_lh56y > 33.43% (iter 024 LRS1.05 baseline) — proves overlay isn't washed out by gating | POSITIVE |
| 14 | rgtdlrs120calm_sortino_collapse | Slot 6 Sortino_lh56y < 1.35 (Phase 4 improved floor) | NEGATIVE |

## Expected outcomes

- Sortino_lh56y range: best config Sortino ∈ [1.39, 1.43] (slots 4-5 known
  ~1.40-1.42; slot 6 new prediction ≈ 1.40-1.42 with regime gating).
- CAGR_lh56y range: best config CAGR ∈ [32%, 35%]; slot 6 new ≈ 33.5-35.5%.
- end_eq_ratio_vs_iter017: best ≥ 1.0×; slot 6 ≈ 1.1-1.6× (between iter 027
  slot 5 0.936× and slot 6 LRS1.20 unconditional 2.908×).
- Modern-era Sortino lift: ≥ 1 of {1990_2009, 2010_2026} ≥ 1.20 (vs iter 027
  slot 6 unconditional 1.124-1.144).
- Beats winner: ≥ 4 of 6 configs (slots 2-5 + likely slot 6).
- Phase3 performance candidate: ≥ 4 of 6 configs.
- phase4_anchor_improved: 1 (slot 6) — IF the regime-conditioning thesis
  holds; otherwise 0 (negative result for this regime axis).
- PBO < 0.50 maintained.

## INCOMPLETE flags

- **Bond rate-vol gate uses ZROZ returns proxy.** ZROZ is a long-duration
  Treasury LETF synth; bond-rate-vol percentile is computed on its daily
  returns. This is the canonical bond-vol primitive used in iter 006 onward
  and across iters 011-027 ratevol-off topology. Caveat: a true rate-vol
  signal would be from yields directly (e.g., MOVE index or 10y/30y yield
  realised vol), not LETF prices. Document for future refinement.
- **Gross-return LRS approximation.** As iter 024-027, on-leg LRS overlay
  uses multiplicative scalar on daily returns (no daily-rebalance
  vol-drag asymmetry of true synthetic LETF). At LRS1.20× over multi-decade
  horizons this approximation is reasonable; documented (iter 024 caveat
  preserved verbatim).
- **Regime gate has 5y warmup (1260d pct_window).** Same warmup as iter 006
  ratevol gate; pre-1975 data emits NaN gate values. The slot 6 LRS overlay
  defaults to OFF (1.0×) when the gate is NaN — strictly conservative
  treatment that may underweight pre-1975 LRS exposure. Documented; matches
  iter 024-027 ratevol treatment.
- **No new external data sources introduced.** Reuses
  `data/testfolio/{QLDSIM,TQQQSIM,UPROSIM,UGLSIM,ZROZSIM,IEFSIM,CASHX,SPYSIM}`
  series via `data_loader.load_testfolio_series()`.

## Comparison vs winner — beats_winner test (frozen)

```python
beats_winner = (
    sortino_lh56y > 1.3746          # 1.3246 + 0.05 anti-curve-fit margin
    and winner_conditions_met       # all WINNER strict bars met
    and pct_time_above_benchmark_lh56y >= 0.95
)
```

## Comparison vs Phase 4 anchor (iter 017 T40D60)

```python
phase4_anchor_improved = (
    (cagr_lh56y > 0.3266 or end_equity_ratio_vs_iter017 > 1.00)
    and sortino_lh56y >= 1.35
    and pbo < 0.50
    and dsr_global_p < 0.05
)
```

## Comparison vs Phase 3 performance bar (T3d-K2 winner)

```python
phase3_performance_candidate = (
    cagr_lh56y > 0.3108
    and end_equity_ratio_vs_winner > 1.05
    and sortino_lh56y >= 1.20
    and pbo < 0.50
    and dsr_global_p < 0.05
)
```

## Citations

- **Primary:** `[advances_fin_ml, p.208-211]` CSCV PBO mechanism-mix diversity
  — motivates introducing a mechanically-orthogonal regime gate (bond-vol vs
  equity-rearm) without re-introducing the iter 023 PBO clustering pattern.
- **Secondary (regime gating mechanism):**
  - `[volatility_trading, p.58-60]` Sinclair on volatility cones — current
    realised vol placed against historical percentile distribution as
    regime-detection primitive (the iter 006 ratevol gate is a direct
    implementation).
  - `[systematic_trading, ch.13, p.212]` Carver on vol-scaled regime
    thresholds — supports gating leverage application to calm regimes.
- **Secondary (LRS scaling):**
  - `[leverage_for_the_long_run, p.13, ch.3]` canonical RISK_ON LRS rule —
    "leverage only when above MA daily" — preserves the canonical rule;
    regime gating ONLY adds a within-RISK_ON conditional gate.
  - `[leverage_for_the_long_run, ch.4-5, p.40-60]` Husson-Trifoni LRS
    leverage scaling at 1.25x/2x/3x — 1.20× is at the boundary of the
    ann-vol-<40% sweet spot on QLD on-leg.
  - `[leverage_for_the_long_run, p.5-6]` ann-vol-<40% sweet spot motivation
    for vol-regime gating of LRS.
- **DSR / bootstrap controls:**
  - `[advances_fin_ml, p.222-223]` DSR cumulative trials (n_global=594).
  - `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.
- **Risk-parity / overlay composition:**
  - `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking.
