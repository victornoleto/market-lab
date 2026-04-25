# Iteration 027 — Final Report

## Verdict

🥈 **PROMISING** (score **74/100**, winner_conditions_met=**False**,
**4/5** strict winner conditions met). **Kill A TRIGGERED**: Sharpe
regressed by 0.31-0.37 across all 3 datasets vs iter 026, falsifying
the leverage-neutrality assumption that justified the iter 027
hypothesis.

**Headline finding**: Levering iter 026's VRP harvester from
`harvest_notional=1.0` → `3.5` **clears CAGR floor on 3/3 datasets
(11.43%/12.05%/16.82% vs floors 9.18%/11.98%/15.35%)** but
**collapses DSR significance** (worst p 0.083→0.517) and **erodes
Sharpe edge** (cross-dataset Δ +0.45/+0.38/+0.41 → +0.12/+0.01/+0.10).
Net score regression: 76 → 74.

**The mechanism that broke**: Total-return Sharpe converges toward
the overlay's intrinsic Sharpe (`overlay_sharpe` = 0.67/0.77/0.93)
as `harvest_notional → ∞`. iter 026 at N=1 had Sharpe boosted by the
rf bonus (rf-bearing capital adds zero variance but positive return);
at N=3.5 the rf return is diluted relative to the now 3.5×-larger
harvest variance. Algebraically:

    Sharpe_N = (rf_d + N × mean_h) / (N × σ_h) × √252
             = (rf_d/N + mean_h) / σ_h × √252
             = overlay_sharpe + rf_d/(N × σ_h) × √252

For iter 026 spy_real: `overlay_sharpe = 0.767`, `rf bonus at N=1`
adds ≈ +0.51 to give the observed 1.28; at N=3.5 the rf bonus is
diluted to +0.15, giving 0.91. The same math applies to all 3
datasets with consistent direction.

**This is the iter 027 boundary finding**: linear leverage on a
T-bill-collateral + harvest strategy is **NOT** Sharpe-neutral on
total-return Sharpe (it IS neutral on excess-return Sharpe — the
TDD test `test_iter027_sharpe_invariant_under_leverage` correctly
verified this on the excess form). The hunt-loop scoring uses
total-return Sharpe (criterion 1 + DSR + benchmarks all measured on
total returns), so the rf-dilution effect bites.

The strategy still **clears 4/5 strict winner conditions** (Sharpe
edge ≥ +0.10 on edu/ndx; gates 6/6/6; CAGR floor 3/3; MDD ceiling
3/3). The sole gap is DSR — the same gap as iter 026, but worse
because the lower Sharpe at higher N inflates DSR p-value.

## Headline metrics (top candidate: `vrp_primary_h3_5_5_10_1m`)

| dataset | Sharpe (Δ frozen) | CAGR | MDD | corr_SPY | gates |
|---|---|---|---|---|---|
| educational | **0.8014 (+0.1214)** | 11.43% | 50.68% | +0.774 | **6/7** |
| spy_real    | **0.9140 (+0.0140)** | 12.05% | 23.14% | +0.735 | **6/7** |
| ndx_real    | **1.0566 (+0.1016)** | 16.82% | 28.81% | +0.761 | **6/7** |

Sharpe edge clears +0.10 gate on **2/3 datasets** (edu, ndx). spy_real
(+0.014) misses by ~0.09 — at N=3.5 the rf-dilution narrows the SPY
edge below the gate.

CAGR floor clears **3/3** (was 0/3 at iter 026 — the headline gain).
MDD ceiling clears **3/3** (preserved from iter 026, well within
margin).

Diagnostic data:

| dataset | overlay ann | overlay Sharpe | pos bars | 21d worst | n_bars |
|---|---|---|---|---|---|
| educational | +9.25% | +0.669 | 70.3% | −26.50% | 5100 |
| spy_real    | +9.86% | +0.767 | 70.6% | −17.43% | 4225 |
| ndx_real    | +14.54% | +0.932 | 69.6% | −20.44% | 4065 |

Overlay annualized scaled exactly 3.5× from iter 026 (2.80→9.25,
2.92→9.86, 4.23→14.54) — confirming linear leverage on the
harvest portion. `overlay_sharpe` is **identical** to iter 026 (the
overlay-only Sharpe is leverage-invariant by construction). The
21d-worst loss scaled ~3.5× from iter 026's −7.45/−4.86/−5.72%
(so −26.5/−17.4/−20.4% — well under the 30% Kill B floor, but
notably riskier).

DSR detail (cumulative n_trials = 4280):

| dataset | Sharpe | DSR p (iter 027) | iter 026 reference | gate? |
|---|---|---|---|---|
| educational | 0.8014 | **0.5166** | 0.0828 | FAIL |
| spy_real    | 0.9140 | **0.4643** | 0.0698 | FAIL |
| ndx_real    | 1.0566 | **0.2806** | 0.0376 | FAIL |

DSR collapsed across all 3 datasets — leveraging diluted Sharpe and
DSR p ≈ tail probability of "Sharpe at this magnitude under chance".
Lower Sharpe → higher p; the deflator no longer admits significance
on any dataset. **iter 026's DSR breakthrough on ndx_real (p=0.038)
is reversed at higher leverage**. This is the structural cost of
the CAGR-clear path tested here.

Kill-criteria check:

| kill | criterion | result | triggered |
|---|---|---|---|
| **A** Sharpe regresses > 0.05 vs iter 026 | edu −0.33, spy −0.37, ndx −0.31 | 3/3 | **YES** |
| **B** Per-roll loss > 30% | edu −26.5%, spy −17.4%, ndx −20.4% | 0/3 | NO |
| **C** MDD ceiling fails on ≥ 2 | edu/spy/ndx all clear | 0/3 | NO |
| **D** CAGR floor 0/3 | edu/spy/ndx all clear | 0/3 | NO |
| **E** Engine dirty (G7 > 3pp) | 0.0000 pp | 0/3 | NO |

Kill A's trigger is the **central informative finding** of this iter.
Kills B/C/D/E are all clean — the strategy mechanics scale cleanly,
the engine is correct, and the hypothesis specifically about CAGR-floor
clearing is **CONFIRMED** (Kill D NOT triggered — leverage works for
CAGR). The unexpected failure is on a dimension the pre-commit treated
as "theory-given" (Kill A's leverage-neutrality assumption).

## Score breakdown (frozen benchmarks, canonical)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **20** | 25 | beats bench+0.10 on **2/3** (edu +0.12, ndx +0.10; spy +0.01 misses) |
| 2 Gates | **19** | 25 | edu 6/7 (+5) + spy 6/7 (+5) + ndx 6/7 (+5) + cross-bonus (+4) |
| 3 DSR | **0** | 15 | worst p=0.517 (worse than 0.20 threshold) |
| 4 CAGR floor | **15** | 15 | 3/3 clear (11.43% / 12.05% / 16.82% vs floors 9.18 / 11.98 / 15.35%) |
| 5 MDD ceiling | **15** | 15 | 3/3 (50.68% / 23.14% / 28.81% vs ceilings 60.14% / 38.70% / 40.12%) |
| 6 Robustness | **5** | 5 | 9/9 sub-windows Sharpe > 0 (ties iter 013/024/025/026 record) |
| **total** | **74** | **100+5** | tier: **🥈 PROMISING** (just below STRONG threshold 75) |

**Score regression: 76 → 74** (−2 net). Decomposition:

| criterion | iter 026 | iter 027 | Δ |
|---|---|---|---|
| 1 Sharpe edge | 25 (3/3) | 20 (2/3) | **−5** |
| 2 Gates | 21 | 19 (ndx 7→6) | **−2** |
| 3 DSR | 10 (worst p=0.083) | 0 (worst p=0.517) | **−10** |
| 4 CAGR floor | 0 | 15 (3/3 ✓) | **+15** |
| 5 MDD ceiling | 15 | 15 | 0 |
| 6 Robustness | 5 | 5 | 0 |
| **total** | **76** | **74** | **−2** |

The CAGR-floor +15 gain was insufficient to compensate the combined
−10 DSR + −5 Sharpe + −2 Gates losses.

## Configuration tested

Single pre-committed cfg `vrp_primary_h3_5_5_10_1m` — identical to
iter 026 except `harvest_notional`. Cumulative n_trials advances
4279 → 4280 (+1).

```python
CFG = {
    "cfg_id": "vrp_primary_h3_5_5_10_1m",
    "rf": 0.02,
    "harvest_notional": 3.5,        # iter 027: levered (iter 026 used 1.0)
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    "rebalance": "daily MtM, monthly roll",
}
```

## What worked / what didn't

**Worked — convincingly**

- **Linear scaling of harvest** (CAGR & overlay annualized): exact
  3.5× scale from iter 026's measured values (overlay 2.80→9.25,
  2.92→9.86, 4.23→14.54). The TDD test
  `test_iter027_h35_scales_iter026_h10_linearly` predicted this and
  the iter 026 test `test_harvest_scales_linearly` formally proved
  the linearity to 1e-12 precision.
- **G7 cross-library parity**: 0.0000 pp on all 3 datasets (perfect
  pandas vs numpy match — same as iter 026).
- **G3 walk-forward**: 7/8/8 (was 8/8/8 at iter 026) — minor
  regression in stress windows but well above the 6/8 gate.
- **G6 bootstrap**: CI low +0.07/+0.15/+0.35 — all 3 still positive,
  passes gate (was iter 026 +0.38/+0.48/+0.64; weaker but not broken).
- **G4 OOS 70/30**: Sharpe +1.07/+0.70/+0.80 — the held-out 30%
  retains positive Sharpe.
- **G5 FWD post-2020**: Sharpe +0.86/+0.82/+0.94 — survives 2020
  COVID + 2022 rate-hike + 2025 stress with positive Sharpe (lower
  than iter 026's 1.16/1.13/1.21 but solidly positive).
- **Robustness 9/9**: every sub-window Sharpe > 0 across all 3 datasets
  (range 0.50-1.60). Ties iter 013/024/025/026 robustness record.
- **CAGR floor clear 3/3**: 11.43%/12.05%/16.82% vs floors 9.18 /
  11.98 / 15.35% — the iter 027 hypothesis on CAGR mechanics is
  confirmed. Note spy_real clears with only 7 bps of margin (12.05 vs
  11.98); a small additional drag would push it under.
- **MDD ceiling clear 3/3**: 50.68%/23.14%/28.81% — even at 3.5×
  educational MDD (50.68%) clears the 60.14% ceiling with 9.5pp
  margin. Spy/ndx clear by very wide margins.
- **Per-roll loss capped 3/3**: −26.50%/−17.43%/−20.44% all under 30%
  Kill B floor. Credit-spread cap respects leverage.

**Didn't work — Kill A trigger**

- **Total-return Sharpe is NOT leverage-neutral**. Theory says yes
  for excess-return Sharpe, but iter 026's harvest+rf composition
  has a non-trivial rf component that adds positive numerator with
  ZERO variance. As N grows, the rf bonus is diluted relative to
  the now-N×-larger harvest variance, and Sharpe converges to the
  overlay's intrinsic Sharpe.
  - iter 026 N=1.0: Sharpe edu 1.13 = `0.669 (overlay) + 0.46 (rf bonus)`
  - iter 027 N=3.5: Sharpe edu 0.80 = `0.669 (overlay) + 0.13 (rf bonus)`
  - Asymptote N→∞: Sharpe → `overlay_sharpe = 0.67/0.77/0.93`
- **DSR collapsed across all 3 datasets**. The Sharpe drop maps to
  higher DSR p-values: with `cumulative_n_trials = 4280`, the
  deflator now requires a Sharpe magnitude that the levered strategy
  doesn't deliver. The first-ever DSR pass on ndx_real (iter 026
  p=0.038) is reversed at iter 027 (p=0.281).
- **spy_real Sharpe edge fell below the +0.10 gate** (+0.014). At
  iter 026 spy_real was the strongest absolute Sharpe (1.28); at iter
  027 it dropped to 0.91 — barely above the SPY benchmark 0.90. The
  rf-dilution effect is most painful where the harvest's Sharpe
  edge over the bench-Sharpe was the smallest.
- **Score regression 76 → 74**. The CAGR-floor gain (+15) didn't
  compensate the Sharpe + DSR + Gates loss (−17 net before bonus).

## Mechanism: why leverage broke total-return Sharpe (algebraic detail)

The strategy daily return is exactly:

    r[t] = rf_d + N × h[t]

where `h[t] = -overlay[t]` (short-writer's daily P&L per S_entry,
N=`harvest_notional`). Mean and std:

    mean(r) = rf_d + N × mean(h)
    std(r)  = N × std(h)        (rf_d is constant, contributes 0 variance)

Total-return Sharpe (annualized, what `_sharpe()` computes):

    Sharpe(r, N) = mean(r) / std(r) × √252
                = (rf_d + N × mean(h)) / (N × std(h)) × √252
                = mean(h) / std(h) × √252  +  rf_d / (N × std(h)) × √252
                = Sharpe_overlay  +  rf_d / (N × std(h)) × √252

The first term is invariant in N (it's the overlay's intrinsic Sharpe).
The second term is **inversely proportional to N** — leverage dilutes
the rf bonus.

Excess-return Sharpe (subtract rf_d before computing):

    Sharpe_excess(r, N) = (mean(r) − rf_d) / std(r) × √252
                       = (N × mean(h)) / (N × std(h)) × √252
                       = mean(h) / std(h) × √252
                       = Sharpe_overlay (invariant in N)

The TDD test `test_iter027_sharpe_invariant_under_leverage` correctly
asserts the excess-return form is invariant. But the hunt-loop scoring
uses total-return Sharpe (the full series, no rf subtraction), so
the dilution bites.

Numerical confirmation on iter 026 / iter 027 spy_real:
- iter 026: `mean_h = 1.16e−4`, `std_h = 2.40e−3`, `rf_d = 7.87e−5`
  → `Sharpe = (7.87e−5 + 1×1.16e−4) / (1×2.40e−3) × √252 = 1.288` ✓
- iter 027: same `mean_h`, `std_h`, but `N=3.5`
  → `Sharpe = (7.87e−5 + 3.5×1.16e−4) / (3.5×2.40e−3) × √252 = 0.916` ✓

This boundary is **structural to the strategy as composed** — any
strategy with constant rf-bearing collateral + linearly-leveraged
harvest will have the same dilution. To preserve total-return Sharpe
under leverage, the rf-bearing portion must scale (e.g., if margin
posted reduces rf-earning capital, the total Sharpe stays close to
overlay_sharpe regardless of N).

## Main lesson (for future iterations)

**Linear leverage on a constant-rf collateral + harvest strategy is
NOT Sharpe-neutral on total-return Sharpe — it converges toward the
overlay's intrinsic Sharpe as N grows. iter 026's strong Sharpe
edge (+0.45/+0.38/+0.41) was partially driven by the rf bonus being
maximally weighted at N=1; at N=3.5 the bonus is diluted to ~30% of
its original contribution, and Sharpe degrades to overlay_sharpe +
small. CAGR floor clears 3/3 (the hypothesis-specific test), but
DSR collapses (0.08→0.52) and Sharpe edge drops to 2/3 datasets at
+0.10. Score regresses 76 → 74; 4/5 winner conditions still hold
(DSR sole gap, same as iter 026).**

The path to a winner therefore CANNOT be "lever the harvest" alone.
Either:

1. **Lift `overlay_sharpe` itself** (currently 0.67/0.77/0.93). The
   asymptotic limit of the levered strategy is `overlay_sharpe + ε`,
   so a winner needs `overlay_sharpe ≥ 0.85+` per dataset to clear
   the +0.10 gate cross-dataset. This is what V-3 (VIX filter) and
   strike refinements target — they raise the per-trade Sharpe of
   the harvest itself.
2. **Hold the harvest at modest leverage (N=1.5-2.0) where the rf
   bonus is mostly preserved AND CAGR clears 1-2/3 floors**. iter
   026's spy_real CAGR was 4.97% (floor 11.98% — fails); at N=2.0
   the projected CAGR is 7.84% (still fails). Modest leverage
   doesn't clear CAGR floor on spy/ndx but might preserve Sharpe.
   This is structurally similar to an iter 027b at N=2.0.
3. **Compose the harvest with an orthogonal return source** (V-4
   VRP+carry). The carry leg adds non-equity-correlated CAGR while
   diluting σ²_strategy modestly; this could produce both CAGR clear
   and Sharpe maintained.

The result also **tightens the iter 026 finding**: the Sharpe edge
+0.38-0.45 was conditional on N=1 specifically. At N>1 the edge
asymptotes downward to overlay_sharpe. This is **not visible** from
iter 026's "What worked" section (which framed the harvest as a
pure-Sharpe edge) — iter 027 reveals the rf-bonus is half the
story.

## Structural finding (for `DEAD_ENDS.md`)

Adding a tightening, NOT a hard dead-end:

- **NEW (iter 027)**: Linear leverage on a T-bill-collateral + capped-
  short-vol harvest strategy is **not** total-return-Sharpe neutral.
  As `harvest_notional` increases from 1.0 to 3.5, total-return Sharpe
  converges from `(overlay_sharpe + rf_bonus)` toward `overlay_sharpe`.
  At N=3.5 the rf bonus is diluted to ~30% of its N=1 contribution,
  and Sharpe degrades by 0.31-0.37 across 3/3 datasets. Cleared:
  CAGR floor 3/3 (the hypothesis-specific gain). Lost: DSR 3/3, Sharpe
  edge 1/3 (+0.10 gate now misses spy_real).

  **Does NOT close** the underlying VRP harvest mechanism. The
  iter 026 finding (VRP harvest delivers Sharpe alpha at N=1) remains
  the top-K record holder. The path to a winner via simple leverage
  is closed; the path via lifting `overlay_sharpe` (VIX filter, strike
  refinement, regime gate) or via mechanism composition (VRP + carry)
  remains open.

- **Tightening of iter 026**: iter 026's reported Sharpe alpha of
  +0.38-0.45 is `overlay_sharpe + rf_bonus_at_N=1`. The harvest's
  intrinsic Sharpe alone (`overlay_sharpe`) is +0.07/−0.13/−0.02 vs
  benchmarks (i.e., NOT a Sharpe edge in 2/3 datasets at N=∞). iter
  026's edge is **partially attributable to the rf bonus**, not
  purely to harvest skill. This does not invalidate iter 026 as a
  STRONG result — the strategy at N=1 still delivers the documented
  metrics — but it does narrow the path forward.

## Citations used

Primary (book):
- `[volatility_trading, ch.3]` — VRP mechanics (Sinclair 2013).
- `[volatility_trading, p.41]` — capped tail (SPX kurtosis 21.3).
- `[volatility_trading, p.217]` — short index vol harvest rule
  (referenced; not yet applied — reserved for iter 028).
- `[risk_parity, p.5]` — Asness-Frazzini-Pedersen 2012 levered low-vol
  argument (the prior that justified the iter 027 hypothesis;
  invalidated empirically here for total-return Sharpe).
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.

Papers / web:
- **Bondarenko, O. (2014). "Why Are Put Options So Expensive?"**
  *Quarterly Journal of Finance* 4(3): 1450015. DOI:
  10.1142/S2010139214500153. Documents 2-3%/yr SPX put-writing VRP
  (with Sharpe ~1.0-1.5 for capped credit spreads). Iter 027 confirms
  the **per-trade Sharpe** is 0.67-0.93 (consistent with Bondarenko's
  range) — the iter 026 1.13-1.37 was per-strategy with rf bonus.
- **Carr, P. & Wu, L. (2009). "Variance Risk Premiums."** *RFS* 22(3):
  1311-1341. DOI: 10.1093/rfs/hhn038.

## Next iteration suggestions

The iter 027 boundary finding closes the simplest leverage path. The
forward directions ranked by expected score uplift:

1. **VIX-regime filter on iter 026 (Option V-3)** — Sinclair p.217
   explicit rule: only OPEN new spread when `VIX < 35`. The
   hypothesis is that high-VIX opens are the top-decile losing rolls;
   filtering them lifts `overlay_sharpe` itself. Even a modest
   `overlay_sharpe` lift (e.g., 0.67→0.80, 0.77→0.85, 0.93→1.05)
   would push iter 026's full Sharpe to 1.30+/1.45+/1.50+ and DSR p
   below 0.05 on edu/spy. Single binary param. Best path to a true
   WINNER (n_trials → 4281; if Sharpe rises by ~0.10 the DSR
   clears).

2. **Strike refinement** — test 5/15% spread (wider) or 3/7% (closer
   to ATM). Wider spread = larger credit, larger cap; affects
   `overlay_sharpe` non-trivially. Pre-commit one variant.

3. **VRP + carry composite (Option V-4)** — `0.5 × VRP + 0.5 ×
   iter024_carry`. Carry's bond exposure is uncorrelated with VRP;
   composite σ² should drop modestly (Markowitz diversification) and
   composite mean stays ~equal — Sharpe could rise. Adds CAGR from
   carry leg without diluting VRP.

4. **iter 027 at lower notional N = 2.0 or 1.5** — the iter 027
   finding suggests the "sweet spot" between iter 026 (max Sharpe,
   min CAGR) and iter 027 (max CAGR, mid Sharpe) lies at N ≈ 1.5-2.0.
   Pre-commit one value (e.g., N=1.5 — minimum value where edu CAGR
   clears 1/3 floors). Probably scores 75-77 STRONG.

**NOT recommended** (confirmed by this iter):

- Higher notional (N=4.0+) — would further dilute Sharpe; CAGR
  marginal benefit, MDD risk on educational, DSR worsens.
- Tweaking iter 027 cfg to "rescue" — the rf-dilution boundary is
  structural, not parametric.
- Applying the iter 027 framing to any other constant-collateral +
  harvest strategy (carry, FX, futures basis) — the same dilution
  structure applies. To beat it, the rf or carry-yield must scale
  with leverage (margin financing model).

## Conclusion

Iter 027 is a **boundary-finding iteration**: the hypothesis (linear
leverage clears CAGR floor while preserving Sharpe + DSR) is
**partially confirmed** (CAGR clears 3/3 — the headline gain) but
**partially refuted** (Sharpe drops 0.31-0.37 across 3/3 datasets;
DSR collapses; the rf-bonus effect was uncovered). Score regresses
76 → 74 (PROMISING), but 4/5 winner conditions still hold (Sharpe
edge clear on edu/ndx; gates 6/6/6; CAGR 3/3; MDD 3/3; DSR sole gap).

The iteration adds 1 trial to the cumulative count
(`n_trials = 4280`) and contributes a **structural finding** that
sharpens the iter 026 narrative: the +0.38-0.45 Sharpe edge was
maximally extracted at N=1 specifically, and grows toward the
asymptotic overlay-only Sharpe (0.67/0.77/0.93) at higher leverage.

The forward direction is **NOT to lever harder** but to **lift
`overlay_sharpe` itself** — iter 028 should test the VIX-regime
filter (Option V-3) which targets the harvest-skill itself, the only
component that survives leverage.

Forward direction: Option V-3 VIX-filter VRP-primary on iter 026 base
(N=1, +VIX<35 filter). Expected uplift: `overlay_sharpe` 0.67-0.93 →
0.80-1.05, restoring full Sharpe to 1.30+ across datasets and pushing
DSR p < 0.05 on edu+spy.
