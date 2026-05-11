# Iter 023 — Rearm-window leverage overlay AND K4 ELSE rearm mutex

**Date:** 2026-05-10
**Phase:** 4 — iter 017 focused validation/refinement
**Slug:** `rearm-leverage-overlay-and-k4mutex`
**n_configs:** 6 (mechanism-mix-diverse with 6 distinct upgrade-axis topologies)

**cumulative_n_trials_global:** 558 → **564** (after this iter)
**cumulative_n_trials_loop:**   132 → **138** (after this iter)

## Hypothesis

**PRIMARY hypothesis (slot 5).** Iter 022's rearm-only INDEP IMPL produced
Sortino 1.4176 (+0.0146 vs iter 017 anchor 1.4030) but at -0.22pp CAGR
(32.44% vs 32.66%) and 0.936× terminal equity vs iter 017 — a Sortino-better-
CAGR-worse Pareto-NON-improvement. Hypothesize that **scaling the rearm-window
TQQQ on-leg by a modest leverage factor (1.15×, synthetic ~3.45× nominal)
recovers the CAGR shortfall while preserving the Sortino lift**, breaking the
Pareto trade-off and producing the loop's first formal `phase4_anchor_improved=
True` candidate. The 1.15× scaler is small enough to control TQQQ volatility-
drag amplification; the rearm window is short (60 days) which limits compounding
exposure to ~9.7% of trading days.

**SECONDARY hypothesis (slot 6).** Iter 021's mechanism diagnosis showed that
K4_AND_lv25 base trades Sortino for CAGR (slot 4: K4 alone Sortino 1.3951 /
CAGR 31.47%; slot 5: rearm-only Sortino 1.4176 / CAGR 32.44%). Hypothesize
that the **LRS1.15× overlay composes ADDITIVELY** when stacked onto the iter
017 OR-anchor base (K4_AND_lv25 OR rearm) — preserving K4 CAGR pump in
pure-trend regimes + adding rearm-window leverage scaling on streak days.
Mechanically distinct from slot 5 (which has rearm-only base, no K4). Tests
whether base-mechanism choice (rearm-only vs K4-OR-rearm) interacts with the
LRS-during-rearm overlay.

(Note: the originally-intended `K4 ELSE rearm` mutex composition was
considered but is algebraically identical to OR-composition when both gates
are binary 0/1 — produces bit-identical strategy returns to slot 3, so
testing it would be redundant for CSCV PBO purposes. Slot 6 is therefore
re-cast as the K4-base × LRS-overlay additive stack, providing a genuine
mechanism difference vs slot 5.)

**Combined directional bet.** Both hypotheses share the goal of breaking
iter 022's Sortino-CAGR Pareto trade-off but via topologically distinct
mechanisms (multiplicative leverage scalar vs disjoint state composition).
At least one should produce a Phase 4 anchor improvement (`cagr_lh56y > 0.3266
OR end_equity_ratio_vs_iter017 > 1.00`, with Sortino ≥ 1.35, PBO < 0.5,
DSR_global p < 0.05). If neither passes, the trade-off is structural and
Phase 4 should pivot to family change.

## Configs (6 — mechanism-mix-diverse)

| # | name | ON-leg | upgrade axis | rearm impl | T_crash | D_arm | LRS in rearm | mutex |
|---|---|---|---|---|--:|--:|---|---|
| 1 | `..._lrsmx_baseline_qld_zroz` | single QLD | none | — | — | — | — | — |
| 2 | `..._lrsmx_single_K4lv25_g25_rvp70_cashx` | single QLD/TQQQ | K4_AND_QLDlv25 | — | — | — | — | — |
| 3 | `..._lrsmx_single_K4lv25_g25_rvp70_cashx_T40D60` ← iter 017 OR-anchor replica | single QLD/TQQQ | K4_AND_lv25 OR rearm | iter017 module | 40 | 60 | — | — |
| 4 | `..._lrsmx_single_rearmonly_g25_rvp70_cashx_T40D60` ← iter 021/022 calib anchor | single QLD/TQQQ | rearm only | INDEPENDENT | 40 | 60 | — | — |
| 5 | 🆕 `..._lrsmx_single_rearmonly_g25_rvp70_cashx_T40D60_lrs115` ← **PRIMARY** | single QLD/TQQQ | rearm only + LRS1.15× | INDEPENDENT | 40 | 60 | **1.15×** | — |
| 6 | 🆕 `..._lrsmx_single_K4lv25_OR_rearm_g25_rvp70_cashx_T40D60_lrs115` ← **SECONDARY** | single QLD/TQQQ | K4_AND_lv25 OR rearm + LRS1.15× | INDEPENDENT | 40 | 60 | **1.15×** | — |

**Distinct upgrade-axis topologies (6, for CSCV PBO mechanism diversity):**
1. None
2. K4_AND_QLDlv25 only
3. K4_AND_QLDlv25 OR rearm (additive composition; iter 017 OR-anchor)
4. rearm only (replace base)
5. rearm only + LRS1.15× (replace base + multiplicative leverage scalar) — NEW
6. K4_AND_QLDlv25 OR rearm + LRS1.15× (additive base + multiplicative scalar) — NEW

Slots 1-4 are calibration anchors (drift KILL_LOOPs). Slots 5+6 are NEW
mechanisms — both share the LRS1.15× overlay BUT on mechanically distinct
bases (rearm-only vs K4-OR-rearm). Mechanism diversity across slots 3-6:
additive base (3), disjoint replace base (4), replace + LRS overlay (5),
additive base + LRS overlay (6) — 4 distinct gate-composition algebraic
forms. Avoids iter 018-style narrow parametric sweep that clustered ranks
and inflated PBO to 0.8135.

## Datasets

`lh_56y` (1970-01..2026-04), `modern_1990` (1990-01..2026-04),
`spy_real` (2003-01..2026-04), `ndx_real` (2010-02..2026-04). Same as
iter 022 for comparability.

## Mechanism details

### Slot 5 (PRIMARY): LRS1.15× during rearm window

Implementation in iter-local helper `lrs_overlay_leg.py`:

```
on_leg_t = build_single_asset_on_leg(qld, tqqq, upgrade=rearm_gate)   # iter 014 module
lrs_scalar_t = 1.0 + (LRS_FACTOR - 1.0) * rearm_gate.shift(1).fillna(0.0)
on_leg_lrs_t = on_leg_t * lrs_scalar_t
```

When `rearm_gate=1` (rearm window active, on-leg = TQQQ): `on_leg_lrs = TQQQ * 1.15`
(synthetic effective leverage ~3.45× of QQQ daily, no daily-rebal-cost model
adjustment in this MVP — gross approximation).

When `rearm_gate=0` (outside rearm, on-leg = QLD): `on_leg_lrs = QLD * 1.0` (unchanged).

LRS factor 1.15× chosen as conservative midpoint:
- 1.0× = slot 4 baseline (no scaling)
- 1.15× = +15% TQQQ daily return scaling on rearm days (~9.7% of trading days)
- 1.30× = aggressive (risk of vol-drag amplification + PBO clustering with slot 5)

We test 1.15× only (not 1.0×/1.15×/1.30× sweep) to avoid PBO-clustering risk
while still answering whether modest in-rearm leverage breaks the trade-off.
1.30× requires a separate iter once 1.15× signal is established.

**Citation:** `[leverage_for_the_long_run, ch.4-5, p.40-60]` Husson-Trifoni
LRS leverage scaling — leverage applied during streak-window regimes
captures asymmetric upside; modest scaling (≤1.5×) preserves vol-drag-vs-
expected-return positive expected value.

### Slot 6 (SECONDARY): K4_AND_lv25 OR rearm base + LRS1.15× during rearm

Implementation:

```
upg = combine_OR(K4_AND_lv25_gate, rearm_gate)             # iter 011 helper
on_leg_t = build_single_asset_on_leg(qld, tqqq, upgrade=upg)  # iter 014
on_leg_lrs_t = apply_lrs_during_rearm_overlay(on_leg_t, rearm_gate, lrs_factor=1.15)
```

When `rearm_gate=1` (inside rearm window): `upg=1` (rearm forces upgrade) AND
on_leg = TQQQ × 1.15 (LRS overlay applies).
When `rearm_gate=0` AND `K4_AND_lv25=1`: `upg=1` (K4 fires) AND on_leg = TQQQ × 1.0
(no LRS — outside rearm window).
When `rearm_gate=0` AND `K4_AND_lv25=0`: `upg=0` AND on_leg = QLD × 1.0.

This composes the iter 017 OR-anchor base (K4 + rearm additive) with the
LRS1.15× overlay restricted to the rearm window only. Mechanism-distinct
from slot 5 in two ways:
1. Base mechanism: K4-OR-rearm (slot 6) vs rearm-only (slot 5)
2. K4 still pumps independently outside rearm window (slot 6) vs no K4
   contribution at all (slot 5)

If LRS overlay composes ADDITIVELY with K4 base: slot 6 should produce
higher CAGR than slot 5 (preserves K4 outside-rearm CAGR pump + adds
LRS-during-rearm CAGR boost). If LRS overlay SUBSTITUTES for K4
contribution: slot 6 ≈ slot 5.

**Citation:** `[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking
(additive overlay composition); `[leverage_for_the_long_run, ch.4-5,
p.40-60]` LRS leverage scaling.

## Pre-registered KILL_LOOP conditions (this iter)

1. **KILL_LOOP #1 (success_tag).** FIRES if any config has `beats_winner=True`.
2. **KILL_LOOP #2 (decisive_fail).** FIRES if best Sortino_lh56y < 1.20.
3. **KILL_LOOP #3 (replica_baseline).** FIRES if baseline Sortino deviates
   from iter 011-022 baseline 1.3240 by > 0.005. Target: 14th-gen reproducibility.
4. **KILL_LOOP #4 (replica_single_K4lv25_g25).** FIRES if slot 2 Sortino
   deviates from iter 014/022 strict_superset 1.3951 by > 0.005. Target:
   11th-gen reproducibility.
5. **KILL_LOOP #5 (replica_T40D60_OR_iter017).** FIRES if slot 3 Sortino
   deviates from iter 017 NEW strict_superset 1.4030 by > 0.005. Target:
   6th-gen reproducibility (iter 017 module replica).
6. **KILL_LOOP #6 (replica_rearmonly_T40D60).** FIRES if slot 4 Sortino
   deviates from iter 021/022 INDEP IMPL 1.4176 by > 0.005. Target:
   3rd-gen reproducibility (independent module).
7. **KILL_LOOP #7 (PBO_blowup).** FIRES if G1 PBO ≥ 0.55 (mechanism-mix
   diversity collapse).
8. **KILL_LOOP #8 (PBO_held).** FIRES (POSITIVE) if G1 PBO < 0.50.
9. **KILL_LOOP #9 (lrs_phase4_anchor_improved).** FIRES (POSITIVE) if slot 5
   (LRS1.15) achieves `phase4_anchor_improved=True` (CAGR > 0.3266 OR
   end_eq_iter017 > 1.0; Sortino ≥ 1.35; PBO < 0.5; DSR_global p < 0.05).
   **CORE WEAK HYPOTHESIS — directly tests Pareto trade-off break via leverage scaling.**
10. **KILL_LOOP #10 (k4base_lrs_phase4_anchor_improved).** FIRES (POSITIVE) if
    slot 6 (K4 OR rearm + LRS1.15×) achieves `phase4_anchor_improved=True`.
    **STRONG HYPOTHESIS — tests Pareto trade-off break via additive K4-base
    + LRS-overlay composition.**
11. **KILL_LOOP #11 (lrs_strict_superset).** FIRES (POSITIVE) if slot 5
    achieves `strict_superset=True`. STRONGEST HYPOTHESIS for slot 5.
12. **KILL_LOOP #12 (k4base_lrs_strict_superset).** FIRES (POSITIVE) if
    slot 6 achieves `strict_superset=True`. STRONGEST HYPOTHESIS for slot 6.

## Expected outcomes (pre-committed)

### Slot 5 (LRS1.15)
- **Sortino_lh56y range:** 1.30–1.45 (LRS adds vol; expect ~10% Sortino reduction
  vs slot 4's 1.4176 if vol scales linearly, but post-flip streak windows tend
  to have asymmetric upside which favors LRS — net could be flat-to-positive).
- **CAGR_lh56y expected:** 32.5%–34.5% (slot 4 was 32.44%; +15% scaling on
  positive-expected-return days adds ~0.5pp–2pp CAGR if LRS doesn't blow up vol).
  Gap vs T3d-K2 (31.08%) expected positive +1.4pp to +3.4pp.
- **Terminal equity ratio vs T3d-K2:** ~1.5×-1.8× (vs iter 022 slot 5's 1.516×).
- **Terminal equity ratio vs iter 017:** ~0.95×-1.10× (target >1.00× for Phase 4
  anchor improvement).
- **Rolling-window win rate vs T3d-K2:** 1y/3y/5y/10y in line with iter 022 slot 5.
- **`beats_winner` plan:** Sortino > 1.3746 ✓ (likely) AND winner_conditions_met
  ✓ (PBO/DSR/G3-G7 stable) AND pct_above ≥ 0.95 ✓.
- **`phase3_performance_candidate` plan:** CAGR > 31.08% ✓ (likely) AND end_eq
  > 1.05× ✓ (likely) AND Sortino ≥ 1.20 ✓ AND PBO < 0.5 ✓ AND DSR_global < 0.05 ✓.
- **`phase4_anchor_improved` plan:** CAGR > 32.66% (target +) OR end_eq_iter017
  > 1.00 (target +); Sortino ≥ 1.35 ✓; PBO < 0.5 ✓; DSR_global < 0.05 ✓.
  **PRIMARY hypothesis success.**

### Slot 6 (K4 OR rearm base + LRS1.15× during rearm)
- **Sortino_lh56y range:** 1.30–1.45 (LRS1.15 adds rearm-window vol; expect
  Sortino reduction vs slot 3's 1.4030, but post-flip streak windows have
  asymmetric upside which favors LRS — net could be flat-to-positive).
- **CAGR_lh56y expected:** 33.0%–35.0% (slot 3 OR-anchor was 32.66%; +15%
  scaling on the rearm window adds CAGR if LRS contributes positive
  expected return; K4-base also pumps outside rearm).
- **Terminal equity ratio vs iter 017:** ~1.00×-1.20× (target >1.00× for
  Phase 4 anchor improvement).
- **`phase4_anchor_improved` plan:** Same threshold; SECONDARY hypothesis success.

### Comparative test (slot 5 vs slot 6)
- If slot 6 CAGR > slot 5 CAGR by ≥ 0.5pp: K4 base contributes additive CAGR
  outside rearm window.
- If slot 6 CAGR ≈ slot 5 CAGR: K4 base contribution is dominated by LRS-
  during-rearm overlay; the overlay alone is sufficient.
- If slot 6 CAGR < slot 5 CAGR: K4 base actively hurts when stacked with LRS
  (intra-window dilution despite mutex semantics).

## INCOMPLETE flags

- **Pre-existing uncommitted changes.** `data/tiingo/manifest.json` and
  `tests/test_tiingo_storage.py` show modifications from prior tiingo data
  refresh (2026-04-15 → 2026-05-10) and unused-import removal. Neither file
  is in any iter directory or in the protected-modules list. They will NOT
  be included in the iter 023 commit (specific paths only). They predate
  iter 022's commit.
- **LRS overlay model.** The 1.15× scalar applied to TQQQ daily returns is a
  GROSS approximation of synthetic LETF rebalancing — does NOT model the
  daily compounding-vol-drag asymmetry of an actual 3.45× ETF. For modest
  scaling (1.15×) over short windows (~60 days) this approximation is
  reasonable but should not be extrapolated to higher leverage factors
  without adjustment. Documented here, not modeled in this iter.
- **PBO-clustering risk.** Slots 4, 5, 6 share rearm-only T40D60 scaffolding
  (rearm independent module). Iter 022 PBO 0.4960 was the boundary case.
  This iter has 4 distinct upgrade-axis composition algebras (additive OR,
  disjoint replace, multiplicative scalar, mutex), but the underlying
  rearm primitive is shared. PBO may cluster again. Pre-registered
  KILL_LOOP #7 (≥0.55) flags blowup; KILL_LOOP #8 (<0.50) flags pass.
- **No daily-rebal cost model adjustment for LRS1.15× synthetic 3.45× ETF.**
  Treats `1.15 × TQQQ daily return` as the LETF return; in practice a true
  3.45× ETF would diverge slightly via vol-drag. For 60-day windows at
  modest scaling this is small; documented for future refinement.

## Citations

- **PRIMARY (slot 5):** `[leverage_for_the_long_run, ch.4-5, p.40-60]`
  Husson-Trifoni LRS leverage scaling.
- **PRIMARY (slot 6):** `[risk_parity, ch.5, p.10]` Carlson cap-efficient
  stacking on disjoint state cells.
- **Phase 4 framework:** `[leverage_for_the_long_run, p.6-7, ch.3]`
  Husson-Trifoni MA-streak window onset.
- **Statistical gates:** `[advances_fin_ml, p.208-211]` CSCV PBO;
  `[advances_fin_ml, p.222-223]` DSR cumulative (n_global=564);
  `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.
- **Mechanism diversity:** `[volatility_trading, p.58-60]` Sinclair vol cone;
  `[stocks_on_the_move, p.98]` Clenow trend; `[risk_parity, p.80-81, ch.4]`
  Qian RORO graded; `[systematic_trading, p.212, ch.13]` Carver re-arm.
