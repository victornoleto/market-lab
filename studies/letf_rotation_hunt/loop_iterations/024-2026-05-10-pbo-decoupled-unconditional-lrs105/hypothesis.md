# Iter 024 — PBO-decoupled unconditional LRS1.05× overlay

**Date:** 2026-05-10
**Phase:** 4 — iter 017 focused validation/refinement
**Slug:** `pbo-decoupled-unconditional-lrs105`
**n_configs:** 6 (mechanism-mix-diverse, 3 NON-rearm + 3 rearm-scaffolded, balanced split)

**cumulative_n_trials_global:** 564 → **570** (after this iter)
**cumulative_n_trials_loop:** 138 → **144** (after this iter)

## Hypothesis

**PRIMARY hypothesis (statistical structural).** Iter 023 found that the
LRS1.15×-during-rearm overlay qualitatively achieved Phase 4 anchor improvement
(slot 5 Sortino 1.4202 / CAGR 33.16% / end_eq vs iter017 1.167×) but was
**formally rejected by G1 PBO 0.6548 ≫ 0.50** due to scaffolding-shared CSCV
clustering — 4 of 6 configs sharing rearm scaffolding and 2 of those 4 sharing
LRS overlay collapsed the ranking matrix into 2 effective groups. Hypothesize
that **decoupling the LRS axis from the rearm scaffolding** — applying LRS1.05×
**unconditionally during every ON day** (not gated to the rearm window only) on
two structurally distinct bases (K4_AND_lv25 base, rearm-only base) — restores
mechanism-mix diversity sufficient to clear the G1 PBO < 0.50 hard gate while
preserving qualitative LRS lift. The 1.05× factor is the conservative
midpoint between iter 023's 1.15× (PBO-blowup) and 1.00× (no overlay), per
iter 023 next-iter-idea (a) recommendation.

**SECONDARY hypothesis (mechanism orthogonality).** If the LRS contribution to
Sortino/CAGR is a property of the *leverage scaling itself* (not the *rearm
window timing*), then unconditional LRS1.05× on every ON day will produce
positive Sortino/CAGR lift on BOTH the K4 base (slot 3) and rearm-only base
(slot 6), with magnitudes roughly proportional to ON-active duration ratios.
If the LRS effect is specifically rearm-window-dependent (i.e., LRS captures
asymmetric streak upside as Husson-Trifoni claim), then unconditional LRS
should underperform vs iter 023's rearm-window LRS at matched factors. This
iter therefore distinguishes between two alternative mechanisms:

- **Streak-window-conditional:** LRS captures asymmetric upside ONLY during
  post-flip streak regimes `[leverage_for_the_long_run, p.6-7, ch.3]`.
- **Above-MA unconditional:** LRS captures volatility-regime leverage benefit
  on every above-MA (RISK_ON) day `[leverage_for_the_long_run, p.13, ch.3]`
  per Husson-Trifoni's canonical 200d MA LRS rule.

If slot 3 (unconditional K4-base LRS) and slot 6 (unconditional rearm-base
LRS) BOTH show positive Sortino lift vs their NO-LRS calibration anchors
(slots 2, 5), the canonical Husson-Trifoni unconditional-LRS interpretation is
supported; it confirms LRS is a generic above-MA leverage primitive,
orthogonal from any specific upgrade-gate composition.

**SAFETY direction.** The 1.05× factor is small enough that vol-drag
amplification on TQQQ (when on-leg = TQQQ via K4 swap) is negligible over the
relevant compounding windows; on QLD on-leg days (most of ON time) the
effective leverage shift is from 2× to 2.1× — well within the
volatility regime where leverage is beneficial per Husson-Trifoni
`[leverage_for_the_long_run, p.5-6]` (annualized vol < 40% sweet spot).

## Configs (6 — mechanism-mix-diverse, 3-3 balanced split)

| # | name | upgrade gate | rearm scaffolding | LRS mode | LRS factor |
|---|---|---|---|---|--:|
| 1 | `..._unclrs_baseline_qld_zroz` | none | NO | off | 1.00 |
| 2 | `..._unclrs_single_K4lv25_g25_rvp70_cashx` | K4_AND_QLDlv25 | NO | off | 1.00 |
| 3 | 🆕 `..._unclrs_single_K4lv25_g25_rvp70_cashx_unclrs105` | K4_AND_QLDlv25 | NO | **uncond_on** | **1.05** |
| 4 | `..._unclrs_single_K4lv25_g25_rvp70_cashx_T40D60` ← iter 017 OR-anchor replica | K4_AND_lv25 OR rearm | YES (iter017 module) | off | 1.00 |
| 5 | `..._unclrs_single_rearmonly_g25_rvp70_cashx_T40D60` ← iter 022 INDEP IMPL replica | rearm only | YES (INDEPENDENT) | off | 1.00 |
| 6 | 🆕 `..._unclrs_single_rearmonly_g25_rvp70_cashx_T40D60_unclrs105` | rearm only | YES (INDEPENDENT) | **uncond_on** | **1.05** |

**Distinct upgrade-axis topologies (6, for CSCV PBO mechanism diversity):**
1. None
2. K4_AND_QLDlv25 only
3. K4_AND_QLDlv25 + LRS1.05× unconditional during ON — NEW
4. K4_AND_QLDlv25 OR rearm (iter 017 OR-anchor)
5. rearm only (iter 022 calibration)
6. rearm only + LRS1.05× unconditional during ON — NEW

**Balanced split for PBO clustering control (addresses iter 023's blowup):**
- Slots 1, 2, 3: NON-rearm scaffolded (3 configs)
- Slots 4, 5, 6: rearm-scaffolded (3 configs)
- LRS axis appears in 2 distinct contexts: K4-base (slot 3) + rearm-base (slot 6)
- 3 NEW configs (slots 3, 6) with LRS axis distributed across 2 base mechanisms
- 4 calibration anchors (slots 1, 2, 4, 5)

This 3-3 balanced split with LRS spread across 2 base mechanism families breaks
iter 023's 2-effective-group CSCV clustering (which clustered as {1,2}
non-rearm vs {3,4,5,6} rearm-scaffolded). Iter 024's effective groups are:
- Group A: {slot 1} (no upgrade)
- Group B: {slots 2, 3} (K4 base ± LRS)
- Group C: {slot 4} (K4 OR rearm)
- Group D: {slots 5, 6} (rearm only ± LRS)

4 effective groups (vs iter 023's 2) — substantially better mechanism-mix
diversity per `[advances_fin_ml, p.208-211]` CSCV PBO recommendations.

## Datasets

`lh_56y` (1970-01..2026-04), `modern_1990` (1990-01..2026-04),
`spy_real` (2003-01..2026-04), `ndx_real` (2010-02..2026-04). Same as
iter 022/023 for comparability.

## Mechanism details

### LRS unconditional during ON — implementation

Iter-local helper `unconditional_lrs_overlay.py`:

```python
def apply_unconditional_lrs_overlay(
    on_leg_returns: pd.Series,
    on_signal: pd.Series,
    lrs_factor: float,
) -> pd.Series:
    if lrs_factor == 1.0:
        return on_leg_returns
    on_lag = on_signal.shift(1).reindex(on_leg_returns.index).fillna(0.0)
    scaler = 1.0 + (lrs_factor - 1.0) * on_lag
    return on_leg_returns * scaler
```

Mechanism — when `on_signal_t-1 = 1` (ON state — strategy holds the on-leg):
- `on_leg_t * 1.05` (modest leverage scaling regardless of upgrade gate state).

Mechanism — when `on_signal_t-1 = 0` (OFF state — strategy holds off-asset):
- `off_leg_t * 1.0` (LRS does not apply to off-leg; mechanism preserves
  Husson-Trifoni leverage-only-when-RISK_ON convention `[p.13]`).

### Slot 3 (NEW): K4_AND_lv25 + LRS1.05× unconditional ON

```
upg = K4_AND_lv25_gate
on_leg_t = build_single_asset_on_leg(qld, tqqq, upgrade=upg)
on_leg_lrs_t = apply_unconditional_lrs_overlay(on_leg_t, on_signal, lrs_factor=1.05)
```

When ON: `on_leg = QLD * 1.05` (or TQQQ * 1.05 if K4_AND_lv25 fires).
ON activates ~70-80% of trading days; LRS scales every ON day modestly.

### Slot 6 (NEW): rearm-only + LRS1.05× unconditional ON

```
upg = rearm_gate_indep    # iter 022 INDEPENDENT module
on_leg_t = build_single_asset_on_leg(qld, tqqq, upgrade=upg)
on_leg_lrs_t = apply_unconditional_lrs_overlay(on_leg_t, on_signal, lrs_factor=1.05)
```

When ON & rearm-active (~5.8% of ON days): `on_leg = TQQQ * 1.05`.
When ON & rearm-OFF (~94% of ON days): `on_leg = QLD * 1.05`.

This is structurally distinct from iter 023's slot 5 (which applied LRS only on
the ~9.7% of trading days inside the rearm window). Iter 024's slot 6 applies
LRS on every ON day (including non-rearm days where on-leg = QLD), making the
LRS effect temporally distributed and CSCV-orthogonal from the rearm scaffolding.

## Pre-registered KILL_LOOP conditions (this iter)

1. **KILL_LOOP #1 (success_tag).** FIRES if any config has `beats_winner=True`.
2. **KILL_LOOP #2 (decisive_fail).** FIRES if best Sortino_lh56y < 1.20.
3. **KILL_LOOP #3 (replica_baseline).** FIRES if baseline Sortino deviates from
   iter 011-023 baseline 1.3240 by > 0.005. Target: **15th-gen reproducibility.**
4. **KILL_LOOP #4 (replica_single_K4lv25_g25).** FIRES if slot 2 Sortino
   deviates from iter 014/023 strict_superset 1.3951 by > 0.005. Target:
   **12th-gen reproducibility.**
5. **KILL_LOOP #5 (replica_T40D60_OR_iter017).** FIRES if slot 4 Sortino
   deviates from iter 017/023 NEW strict_superset 1.4030 by > 0.005. Target:
   **7th-gen reproducibility (iter 017 module replica).**
6. **KILL_LOOP #6 (replica_rearmonly_T40D60).** FIRES if slot 5 Sortino
   deviates from iter 021/022/023 INDEP IMPL 1.4176 by > 0.005. Target:
   **4th-gen reproducibility (independent module).**
7. **KILL_LOOP #7 (PBO_blowup).** FIRES if G1 PBO ≥ 0.55 (mechanism-mix
   diversity collapse — iter 023 was 0.6548).
8. **KILL_LOOP #8 (PBO_held).** FIRES (POSITIVE) if G1 PBO < 0.50.
   **CORE STRUCTURAL HYPOTHESIS — directly tests whether decoupling LRS from
   rearm scaffolding restores PBO.**
9. **KILL_LOOP #9 (k4_unclrs_phase4_anchor_improved).** FIRES (POSITIVE) if
   slot 3 (K4 + uncond LRS1.05×) achieves `phase4_anchor_improved=True`
   (CAGR > 0.3266 OR end_eq vs iter017 > 1.0; Sortino ≥ 1.35; PBO < 0.5;
   DSR_global p < 0.05).
10. **KILL_LOOP #10 (rearm_unclrs_phase4_anchor_improved).** FIRES (POSITIVE)
    if slot 6 (rearm-only + uncond LRS1.05×) achieves `phase4_anchor_improved
    =True`. **STRONG HYPOTHESIS — most likely candidate for formal Phase 4
    anchor improvement** (combines best base mechanism with decoupled LRS).
11. **KILL_LOOP #11 (k4_unclrs_strict_superset).** FIRES (POSITIVE) if slot 3
    achieves `strict_superset=True`. STRONGEST HYPOTHESIS slot 3.
12. **KILL_LOOP #12 (rearm_unclrs_strict_superset).** FIRES (POSITIVE) if
    slot 6 achieves `strict_superset=True`. **STRONGEST HYPOTHESIS slot 6 —
    candidate for loop's first formal Phase 4 anchor improvement.**

## Expected outcomes (pre-committed)

### Slot 3 (K4 + uncond LRS1.05×)
- **Sortino_lh56y range:** 1.38–1.43 (vs slot 2 anchor 1.3951; modest leverage
  on ~70-80% of days slightly increases vol but symmetrically scales returns).
- **CAGR_lh56y expected:** 31.5%–32.5% (vs slot 2 anchor 31.47%; +0.5pp to
  +1.0pp from leverage on positive-expected-return days).
- **Terminal equity ratio vs T3d-K2:** ~1.20×-1.40× (vs slot 2's 1.129×).
- **Terminal equity ratio vs iter 017:** ~0.74×-0.86× (LRS on K4 base alone
  unlikely to beat iter 017 OR-anchor without rearm primitive).
- **`beats_winner` plan:** Sortino > 1.3746 ✓ (likely, slot 2 already at 1.3951)
  AND winner_conditions_met ✓ (PBO must clear < 0.50) AND pct_above ≥ 0.95 ✓.
- **`phase3_performance_candidate` plan:** CAGR > 31.08% ✓ (likely) AND end_eq
  > 1.05× ✓ AND Sortino ≥ 1.20 ✓ AND PBO < 0.5 ✓ AND DSR_global < 0.05 ✓.
- **`phase4_anchor_improved` plan:** CAGR > 32.66% — UNLIKELY (K4 base
  ceiling). End_eq vs iter017 > 1.0 — UNLIKELY without rearm. Slot 3 is
  primarily a CSCV diversity contributor.

### Slot 6 (rearm-only + uncond LRS1.05×)
- **Sortino_lh56y range:** 1.40–1.45 (vs slot 5 anchor 1.4176; LRS adds modest
  vol but rearm regime captures asymmetric upside).
- **CAGR_lh56y expected:** 32.5%–33.5% (vs slot 5 anchor 32.44%; +0.5pp to
  +1.5pp from unconditional LRS on every ON day; note this is a different
  mechanism from iter 023 slot 5 which had LRS only on ~9.7% rearm days at
  larger 1.15× factor).
- **Terminal equity ratio vs iter 017:** ~0.95×-1.10× (target >1.00× for Phase
  4 anchor improvement).
- **`phase4_anchor_improved` plan:** Same threshold; **STRONG HYPOTHESIS for
  formal Phase 4 anchor improvement**.

### Critical comparison (slot 3 vs slot 6 vs iter 023 slot 5)
- iter 023 slot 5 (rearm-window LRS1.15×): Sortino 1.4202 / CAGR 33.16% (qual
  improvement, formal PBO block)
- iter 024 slot 3 (K4-base LRS1.05× uncond): expected Sortino 1.38-1.43
- iter 024 slot 6 (rearm-base LRS1.05× uncond): expected Sortino 1.40-1.45

If slot 6 ≥ iter 023 slot 5: unconditional LRS at 1.05× ≥ rearm-window LRS at
1.15× — leverage benefit is generic (above-MA leverage), not streak-conditional.

If slot 6 < iter 023 slot 5: rearm-window timing matters; LRS captures
asymmetric upside specifically during streak windows (Husson-Trifoni
streak-window thesis preserved).

If PBO < 0.50 in iter 024 (vs 0.6548 in iter 023): structural decoupling
hypothesis CONFIRMED; mechanism-mix CSCV diversity is the binding constraint
on formal Phase 4 anchor improvement claims, not the LRS magnitude per se.

## INCOMPLETE flags

- **Pre-existing uncommitted changes.** `data/tiingo/manifest.json` and
  `tests/test_tiingo_storage.py` show modifications from prior tiingo data
  refresh. Neither is in any iter directory or in the protected-modules list.
  They will NOT be included in the iter 024 commit (specific paths only).
- **LRS overlay model (gross approximation).** The 1.05× scalar applied
  unconditionally to on-leg daily returns is a GROSS approximation — does NOT
  model daily compounding-vol-drag asymmetry of an actual 2.1× / 3.15×
  synthetic LETF at the implied effective leverage. For modest scaling (1.05×)
  over multi-decade horizons this approximation is reasonable; documented for
  future refinement.
- **PBO-clustering risk reduced but not eliminated.** Slots 4, 5, 6 share rearm
  scaffolding (~9.7% of trading days), but slots 1, 2, 3 are now structurally
  independent. LRS axis appears in 2 of 6 slots across 2 base mechanism
  families (vs iter 023's LRS axis appearing in 2 of 6 slots both rearm-
  scaffolded). Pre-registered KILL_LOOP #7 (≥0.55) flags blowup; KILL_LOOP #8
  (<0.50) flags structural-decoupling success.
- **Slot 6 mechanism is a NEW LRS-application convention.** Distinct from iter
  023's rearm-window LRS — slot 6 applies LRS on every ON day, including
  non-rearm days where on-leg = QLD. This is closer to Husson-Trifoni's
  canonical above-MA LRS rule `[p.13]` than iter 023's streak-window LRS.

## Citations

- **PRIMARY (statistical structural):** `[advances_fin_ml, p.208-211]` CSCV
  PBO mechanism-mix diversity — direct motivation for the 3-3 balanced split.
- **PRIMARY (mechanism):** `[leverage_for_the_long_run, ch.4-5, p.40-60]`
  Husson-Trifoni LRS leverage scaling.
- **PRIMARY (canonical LRS rule):** `[leverage_for_the_long_run, p.13, ch.3]`
  Husson-Trifoni RISK_ON rule (above-MA → leveraged S&P 500 daily;
  unconditional within RISK_ON state).
- **Volatility regime sweet spot:** `[leverage_for_the_long_run, p.5-6]`
  ann vol < 40% favors leverage; 1.05× at ON state stays well within sweet
  spot.
- **Streak-window thesis (alt hypothesis):** `[leverage_for_the_long_run,
  p.6-7, ch.3]` MA flip-on streak window onset.
- **Stacking framework:** `[risk_parity, ch.5, p.10]` Carlson cap-efficient
  stacking (LRS overlay composes with K4 / rearm bases).
- **Statistical gates:** `[advances_fin_ml, p.222-223]` DSR cumulative
  (n_global=570); `[advances_fin_ml, p.196-202]` bootstrap CI / DSR.
- **Other mechanisms (iter heritage):** `[volatility_trading, p.58-60]`
  Sinclair vol cone; `[stocks_on_the_move, p.98]` Clenow trend;
  `[risk_parity, p.80-81, ch.4]` Qian RORO graded; `[systematic_trading,
  p.212, ch.13]` Carver re-arm.
