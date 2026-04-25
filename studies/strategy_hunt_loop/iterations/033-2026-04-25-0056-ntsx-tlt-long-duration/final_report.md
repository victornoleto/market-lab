# Iteration 033 — Final Report

## Verdict

🥈 **PROMISING** (score **72/100**, winner_conditions_met=**False**,
**3/5** strict winner conditions met). **1 of 6 pre-committed kills
fired** (Kill C only); 5 clean (A/B/D/E/F). The hypothesis **partially
falsified**: swapping iter 015's IEF (7-10y) for TLT (20-30y) on the
same NTSX 0.9/0.6 static-stack base does deliver the predicted CAGR
floor unlock (criterion 4: **3/3**, but iter 015 already cleared
2/3 → marginal incremental gain) and preserves Sharpe edge vs frozen
benchmarks (criterion 1: **25/25**, 3/3 datasets clear +0.10), but
**Sharpe is essentially tied with iter 015 on real data** (ΔSh
−0.007/spy, +0.001/ndx) while ndx MDD breaches the +5pp ceiling
(47.04% vs 40.12% — by 6.9pp), and DSR worst-p stays at **0.31**
(criterion 3: **0/15**) — high enough to fire Kill C.

**Headline structural finding**: bond duration choice on the static
NTSX 0.9/0.6 stack is **NOT the axis to break the iter 015 plateau**.
TLT vs IEF buys ~+0.4-1.0 pp CAGR at the cost of ~+7-8pp MDD on real
data, with ZERO Sharpe lift on spy_real and ndx_real. The duration
tilt is **CAGR-MDD-equivalent** to iter 015 (i.e., it trades MDD for
CAGR on the same Sharpe-curve), not Sharpe-additive. The DSR
collapse pattern is **structurally identical to iter 032's**
(criterion 3 = 0/15) but for a completely different reason: iter
032 collapsed DSR via composite higher-moment penalty on a layered
overlay; iter 033 collapses DSR via cumulative_n_trials overhead
(4288 vs iter 015's 4258) on a Sharpe similar to iter 015. Both paths
score 72 — the iter 015 plateau at 77 is **resilient** to bond-axis
variations.

## Headline metrics (top candidate: `ntsx_synth_90_60_spy_tlt`)

Single pre-committed cfg; no grid; cumulative_n_trials advances
**4285 → 4288** (+3).

| dataset | Sharpe (Δ frozen / Δ iter 015) | CAGR (Δ iter 015) | MDD (Δ iter 015) | corr(eq,bd) | gates |
|---|---|---|---|---|---|
| educational | 0.8502 (+0.170 / **+0.067**) | 13.36% (+1.03pp) | 42.60% (**−1.89pp**) | −0.31 | 5/7 |
| spy_real    | 1.0372 (+0.137 / **−0.007**) | 15.95% (+0.41pp) | 38.47% (**+8.15pp**) | −0.30 | 6/7 |
| ndx_real    | 1.0648 (+0.110 / **+0.001**) | 19.83% (+0.59pp) | **47.04%** (**+7.53pp**) | −0.23 | 6/7 |

**Sharpe edge clears +0.10 vs FROZEN benchmarks 3/3** (criterion 1 =
**25/25** — preserved). vs **iter 015 reference** (which is the
direct mechanism-comparison benchmark), Sharpe is **essentially tied**:
edu +0.067 (only meaningful uplift, partly from 4y longer 2002-2026
window catching pre-GFC bond rally), spy −0.007 (tied), ndx +0.001
(tied). **The TLT swap does not improve Sharpe on the post-2009
windows where the strict winner-condition lives** — Kill A (≥2/3 below
iter 015) is clean (only ndx is below by 0.007), but the failure mode
is more subtle: the duration tilt is *Sharpe-neutral*, not
*Sharpe-additive*.

**CAGR**: +0.4-1.0pp vs iter 015. The TLT bond's 2002-2008 rally and
2008-2014 secular bull contribute most of the educational uplift; on
post-2009 spy_real and ndx_real, the carry premium gain is mostly
offset by 2022's −31% TLT crash. Net CAGR uplift is **marginal**.

**MDD ceiling**: criterion 5 = **10/15** (2/3 pass).
- edu 42.60% < 60.14% ✓ (and IMPROVES iter 015's 44.49% by 1.89pp)
- spy 38.47% > 38.70% ceiling barely PASSES (~0.23pp under) ✓
- ndx 47.04% > 40.12% ceiling **breach by 6.93pp** ✗ — driven by
  2022 dual rate-spike + tech selloff (QQQ −33%, TLT −31% concurrent;
  the levered 0.9 QQQ + 0.6 TLT compounds to a deeper drawdown than
  iter 015's 0.6 IEF stack which only lost ~13% in 2022).

DSR detail (cumulative n_trials = **4288**):

| dataset | Sharpe | DSR p (iter 033) | iter 015 ref Sharpe | DSR p ≈ | gate? |
|---|---|---|---|---|---|
| educational | 0.8502 | **0.3129** | 0.7835 | ~0.30 | FAIL |
| spy_real    | 1.0372 | 0.2774 | 1.0442 | ~0.27 | FAIL |
| ndx_real    | 1.0648 | 0.2664 | 1.0638 | ~0.27 | FAIL |

**DSR worst-p 0.31 is in the "no statistical edge after deflator"
tier** (criterion 3 = **0/15**) — virtually identical to iter 015's
DSR profile (Sharpe-tied → DSR-tied) with the slight extra
cumulative_n_trials penalty (+30 trials = ~0.005 p-value drift). Iter
015 itself failed criterion 3 with similar magnitude; this iteration
demonstrates that **bond-duration variations preserve the DSR
collapse on the static stack** — the issue is the *Sharpe ceiling
of the static stack itself*, not the bond ticker choice.

Kill criteria (1 fired, 5 clean):

| kill | criterion | result | triggered |
|---|---|---|---|
| **A** Sharpe < iter 015 on ≥2/3 | edu +0.067 ✓ / spy −0.007 ✗ / ndx +0.001 ✓ → **1/3 below** (need ≥2/3) | falls short of trigger | ✓ NO |
| **B** ndx MDD > 50% | 47.04% < 50% (~3pp below threshold) | borderline but clean | ✓ NO |
| **C** DSR worst-p > 0.20 | 0.3129 (edu) >> 0.20 | far above threshold | ❌ **YES** |
| **D** G7 cross-lib > 3pp CAGR | max 1.0020pp (edu) | 1/3 of threshold | ✓ NO |
| **E** Total score < 60 | 72 vs 60 | 12 above | ✓ NO |
| **F** Robustness < 7/9 sub-windows positive | 9/9 positive | preserved | ✓ NO |

Kill A's clean status is **misleading**: while the strict 2/3
threshold doesn't trigger, the realized ΔSh of {+0.067, −0.007,
+0.001} averages to **+0.020** — i.e., the duration tilt is
~zero-Sharpe-additive on the post-2009 real-data window, with all
the apparent edge concentrated in the pre-2009 educational window.
The "+24y vs 20y" data extension dominates the comparison. On a
matched-window basis (post-2006 IEF, post-2002 TLT), the iter 033
edge over iter 015 is **noise**.

## Score breakdown (frozen benchmarks, canonical)

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | beats bench+0.10 on **3/3** (edu +0.17, spy +0.14, ndx +0.11) |
| 2 Gates | **17** | 25 | edu 5/7 (+3) + spy 6/7 (+5) + ndx 6/7 (+5) + cross-bonus (+4) |
| 3 DSR | **0** | 15 | worst p=0.3129 (edu, > 0.20 threshold → 0 pts) |
| 4 CAGR floor | **15** | 15 | 3/3 (13.36% / 15.95% / 19.83% vs floors 9.18% / 11.98% / 15.35%) |
| 5 MDD ceiling | **10** | 15 | 2/3 (edu+spy ✓; ndx 47.04% > 40.12% ✗ by 6.93pp) |
| 6 Robustness | **5** | 5 | 9/9 sub-windows Sharpe > 0 on all 3 datasets |
| **total** | **72** | **100+5** | tier: **🥈 PROMISING** |

Score is **5 below iter 015 ceiling at 77**, **identical to iter
032's 72 PROMISING**, **4 below iter 026/031 family ceiling at 76**,
**7 below top-K #1 triple-tied ceiling at 79**. The criterion
breakdown is **byte-for-byte identical to iter 032** (25 + 17 + 0 +
15 + 10 + 5 = 72) — both iterations fail at criterion 3 (DSR) and
criterion 5 (MDD ceiling on ndx), but for completely different
mechanism reasons.

## What worked / what didn't

**Worked**

- **TDD discipline**: 6/6 iter-033-specific specs passed first-try,
  including the critical `test_iter033_imports_iter015_stacking_engine`
  which enforces single-source-of-truth on the stacking math.
- **G7 cross-lib parity**: max 1.00pp diff (edu) — well below 3pp
  threshold; iter 015's `numpy_reference_stacked.py` reused verbatim.
- **Sharpe edge vs FROZEN benchmarks**: 3/3 datasets clear +0.10
  (criterion 1 = 25/25, preserved from iter 015).
- **CAGR floor**: 3/3 datasets clear (criterion 4 = 15/15) — same as
  iter 015 on this axis (matched).
- **Educational MDD IMPROVES vs iter 015** (42.60% < 44.49%) — the
  longer 24y window includes the 2002-2008 secular bull in TLT which
  partially offsets equity drawdowns.
- **Robustness 9/9** — every sub-window across every dataset is
  Sharpe-positive, including the harshest 2022 sub-window which
  ndx_real cleanly survives at +0.51 (criterion 6 = 5/5 bonus).
- **Negative correlation preserved**: ρ(eq,bd) = −0.23 to −0.31
  across datasets (TLT slightly less anti-correlated with equities
  than IEF on the post-2009 window; expected because long-duration
  bonds have more idiosyncratic rate-driven moves).
- **Pytest baseline preserved**: 793 → 799 (+6 from iter 033 specs);
  no regressions; iter 015 + iter 032 specs all still green.

**Didn't work as expected — partial falsification**

- **Sharpe is tied with iter 015 on real-data windows**: spy −0.007,
  ndx +0.001. The +0.067 edu uplift is dominated by the 4y window
  extension (2002-2026 vs iter 015's 2006-2026), not by the bond
  ticker swap. **The TLT term-premium hypothesis predicted a clear
  positive Sharpe Δ vs iter 015**; the realized Δ is essentially
  zero on the canonical post-2009 windows. Mechanism: TLT's larger
  term premium (~+150 bps annualized vs IEF historically) is offset
  by TLT's larger volatility drag (vol-of-vol, especially in 2013
  taper, 2018 hikes, 2022 inflation shock) on a static fixed-weight
  stack — no vol-target mechanism to absorb the duration risk.
- **ndx MDD breaches +5pp ceiling by 6.93pp**: 47.04% vs 40.12%.
  2022 was a perfect dual storm (QQQ −33% + TLT −31% concurrent)
  which compounded into a ~50% peak-to-trough on the levered 0.9 QQQ
  + 0.6 TLT stack. iter 015's 0.6 IEF lost only ~13% in 2022 →
  ndx MDD only 39.5%. **Predicted Kill B fires AT THE BORDER (47%
  < 50% by 3pp)**, with criterion 5 falling 15/15 → 10/15.
- **DSR worst-p 0.31 stays in the same band as iter 015 (~0.27-0.31
  cross-ds)**. The 30 extra cumulative_n_trials cost ~0.005 p-value
  drift. With Sharpe essentially tied with iter 015, DSR cannot
  improve. **Predicted Kill C fires** (worst-p 0.31 > 0.20).
- **Total score 72 ties iter 032 at PROMISING**, 5 below iter 015's
  77 STRONG plateau. **Predicted Kill E (score < 60) does NOT fire**,
  but the iteration cleanly demonstrates the bond-axis is exhausted
  on the static-stack family.

## Mechanism: why TLT swap does not break the iter 015 plateau

The hypothesis premise was: TLT (20-30y, ~17-18y duration) earns a
larger annualized term premium than IEF (7-10y, ~6y duration) — per
Cochrane-Piazzesi 2005 and Ilmanen 2011 — and stacking this larger
premium on the same 0.6-weight bond leg should provide a CAGR boost
without changing the equity exposure or leverage profile. The actual
outcome on the iter 015 NTSX architecture:

```
Δ Sharpe (real data, post-2009) = +0.001 to −0.007  → essentially zero
Δ CAGR (real data, post-2009)   = +0.4 to +0.6 pp   → marginal
Δ MDD  (real data, post-2009)   = +7.5 to +8.2 pp   → significantly worse
```

The mechanism: TLT's higher term premium is **offset by TLT's higher
realized vol** on the post-2009 window. The bond leg's annualized
vol jumps from ~7% (IEF) to ~14% (TLT), roughly doubling the bond
contribution to the portfolio variance, which (with the equity-bond
correlation only mildly more negative for TLT vs IEF) produces a
net portfolio variance increase of ~30-50%. The carry premium gain
(~+1.5%/year) is consumed by the variance increase × Sharpe-ratio
trade-off:

```
Sharpe_NTSX_TLT    = (μ_eq + 0.6 × μ_TLT) / sqrt(σ²_port_TLT)
Sharpe_NTSX_IEF    = (μ_eq + 0.6 × μ_IEF) / sqrt(σ²_port_IEF)

μ_TLT − μ_IEF      ≈ +1.5 pp (term premium diff, KMPV 2018)
σ²_TLT − σ²_IEF    ≈ +0.014 (annualized variance, ~doubling)

Net Sharpe Δ       ≈ 0  (numerator and denominator scale ~equally)
```

This is **the static-stack analog of the iter 027 finding**:
"linear leverage on T-bill+harvest is NOT total-Sharpe-neutral" —
here, **substituting longer-duration bond IS total-Sharpe-neutral**
on a fixed-weight static stack, with all the change accumulating in
the higher moments (MDD, skew). 2022 is the singular regime where
the σ²_TLT term dominates and produces the +7-8pp MDD breach.

## Why iter 015's plateau is robust

Iter 015 (0.9 SPY + 0.6 IEF) hit a structural **77 STRONG plateau**
because the architecture optimally trades:
- **Equity beta** (0.9 weight): captures most of the long-term equity
  premium (~+10%/y on real data)
- **Intermediate-duration bond carry** (0.6 weight × IEF ~6y dur):
  captures a modest term premium (~+0.5%/y) at low realized vol (~7%)
- **Negative equity-bond correlation** (ρ ≈ −0.30): provides
  diversification benefit during equity stress

Iter 033 (0.9 SPY + 0.6 TLT) shifts the bond leg to higher-duration:
- **Equity beta** (0.9 weight): unchanged
- **Long-duration bond carry** (0.6 weight × TLT ~18y dur): captures
  a larger term premium (~+1.5%/y) at HIGHER realized vol (~14%) and
  HIGHER tail risk (2022 −31% drawdown)
- **Negative equity-bond correlation** (ρ ≈ −0.23): MARGINALLY
  weaker than IEF's −0.30 — long-duration bonds have more idiosyncratic
  rate-driven moves that decouple from equity

The portfolio-level effect is that the **diversification benefit** is
roughly preserved, the **carry premium** is ~3× larger, but the
**total bond variance contribution** is ~4× larger (vol²) — and
these scale ~proportionally on the Sharpe ratio. Iter 015's 0.6 IEF
weight was approximately Sharpe-optimal for the 0.9-equity stack on
the post-2009 regime; iter 033's 0.6 TLT swap moves to a different
point on the *same Sharpe-curve* (higher CAGR, higher MDD, same
Sharpe).

This is the static-stack analog of the iter 016/021 dead-end finding:
"σ²_port absorption on vol-managed base" — except here, no
vol-management exists, so the absorption is purely *static-Sharpe-
neutral* via the variance term. The iter 015 plateau holds.

## How iter 033 differs from iter 032 despite identical 72 score

Both iterations score 72 PROMISING with the SAME criterion breakdown
(25 + 17 + 0 + 15 + 10 + 5 = 72), but the failure mechanisms are
**structurally distinct**:

| axis | iter 032 (layered comp) | iter 033 (single-mech) |
|---|---|---|
| Architecture | NTSX 0.9/0.6 SPY+IEF + iter 031 VRP overlay | NTSX 0.9/0.6 SPY+TLT (no overlay) |
| corr_combined,SPY | +0.97 (3/3 datasets) | n/a — single-leg static |
| Sharpe vs iter 015 | −0.020 / −0.005 / −0.085 | +0.067 / −0.007 / +0.001 |
| CAGR vs iter 015 | +0.51pp / +2.98pp / +3.69pp | +1.03pp / +0.41pp / +0.59pp |
| MDD vs iter 015 | +X / +X / **+44.4 vs 24** | −1.89pp / +8.15pp / **+7.53pp** |
| DSR worst-p | 0.502 (composite skew/kurt) | 0.313 (cumulative_n_trials only) |
| Mechanism failure | Composite higher-moment penalty on layered overlay | Variance increase on duration tilt offsets term premium gain |
| Closure | "Layer overlay X on base Y" path | "Bond duration tilt on iter 015 stack" path |

**Iter 032 closes "stack short-vol overlay onto static stack"**;
**iter 033 closes "swap longer-duration bond on static stack"**. Both
preserve the iter 015 plateau at 77, both reach 72 PROMISING, both
fail at criterion 3 + criterion 5. The convergence to the SAME score
from two structurally different paths is itself a structural finding:
**the score-rubric trade-off between Sharpe (criterion 1) + CAGR
(criterion 4) on one side and DSR (criterion 3) + MDD (criterion 5)
on the other is sharper than iter-by-iter sweeps reveal**. Single
structural changes on the iter 015 stack generally shift score by
about ±5 points around the plateau without breaking it.

## Main lesson (for future iterations)

**Long-duration UST swap (TLT vs IEF) on the iter 015 NTSX 0.9/0.6
static-stack base produces a 72 PROMISING result — score-tied with
iter 032's layered composition (also 72), 5 below iter 015's 77
plateau, with DSR (criterion 3) and ndx MDD (criterion 5) as twin
bottlenecks. The duration tilt is approximately *static-Sharpe-
neutral* on the post-2009 real-data windows: term premium gain
(~+1.5%/year per KMPV 2018) is offset by variance contribution gain
(~×2 bond vol from 7% to 14%) along the Sharpe curve, with all the
incremental change accumulating in the higher moments (MDD +7-8pp,
skew worse). The educational dataset's apparent +0.067 Sharpe uplift
is dominated by the 4y window extension (2002 vs 2006 inception),
not by the bond ticker swap — on matched-window basis, the iter 033
edge over iter 015 is noise. Three structural closures emerge:
(a) **the iter 015 plateau at 77 is resilient to bond-axis variations**
— neither short-vol overlay (iter 032) nor longer-duration bond
(iter 033) breaks it; both reach 72 from different mechanism paths;
(b) **bond-duration is a CAGR-MDD trade-off, NOT a Sharpe lever** on
fixed-weight static stacks — variance scales with duration² and
offsets carry premium gain on the Sharpe ratio; (c) **DSR is the
binding constraint on the static-stack family** at cumulative_n_trials
≥ ~4288 with Sharpe ≤ ~1.10 — even an exact iter 015 replay would
fail DSR by a small margin at this n_trials level. Future winners
must either: (i) target a CAGR mechanism that is **distribution-
orthogonal AND variance-neutral** to equity beta (e.g., FX/commodity
carry — more decorrelated than bonds in stress; or bond carry SLEEVE
with zero-net-notional duration spread that doesn't add overall
variance); OR (ii) target a Sharpe mechanism that lifts substantially
above 1.10 cross-dataset (closer to 1.30-1.40 to clear DSR with
cumulative_n_trials safety margin) — likely requires a fundamentally
different architecture than the SPY+UST static stack family.**

## Structural finding (for `DEAD_ENDS.md`)

This is a **partial closure** — the specific bond-substitution path
is closed at score 72, but the broader "iter 015 alternative" family
remains open (specifically, FX/commodity carry and zero-net-notional
duration sleeves are untested):

- **CLOSED (iter 033)**: NTSX 0.9 SPY + 0.6 TLT static stack
  (`ntsx_synth_90_60_spy_tlt`). Specific cfg already tested
  (PROMISING 72). Sharpe is tied with iter 015 on real data
  (+0.001/spy, −0.007/ndx); CAGR uplift +0.4-0.6pp negligible vs
  +7-8pp MDD breach on ndx_real. The variance increase from
  doubling bond duration (~7% IEF → ~14% TLT vol) offsets the term
  premium gain (~+0.5pp → ~+1.5pp/year) along the Sharpe curve.

  **Specific cfg closed**: `ntsx_synth_90_60_spy_tlt`.

  **DOES NOT close**:
  - **Bond carry SLEEVE** (zero-net-notional, e.g., +α TLT − α IEF
    on top of iter 015 base): adds duration spread without changing
    aggregate bond notional or leverage. The variance contribution
    is just the spread-vol, not the full TLT-vol — which may
    preserve iter 015's Sharpe AND add carry premium. Untested.
  - **Bond mix** (e.g., 0.9 SPY + 0.3 IEF + 0.3 TLT): rebalances
    bond leg between durations without changing aggregate bond
    notional. Effectively a duration-targeted variant. Untested.
  - **TLT at lower weight** (e.g., 0.9 SPY + 0.4 TLT): preserves
    duration tilt but reduces variance contribution. Less leverage,
    less carry, but possibly Sharpe-additive. Untested.
  - **TLT-funded variant** (iter 018-style): subtract
    r_Tbill × (eq_w + bd_w − 1.0) financing cost. Likely makes
    iter 033 even worse vs iter 015's funded variant (iter 018
    showed −93 to −148 bps drag on iter 015; iter 033 with
    higher-vol bond would have similar or worse drag).
  - **Cross-asset carry (FX/commodity)**: structurally different
    asset class; distribution-orthogonal to equity beta on stress
    days (FX carry: AUDJPY 2008/2020 stress; commodity carry: 2008
    deflation shock — both can decouple from equity stress timing).
    Untested.

- **NEW STRUCTURAL FINDING (iter 033)**: "**Bond-duration is a
  CAGR-MDD trade-off, NOT a Sharpe lever** on fixed-weight static
  stacks at preserved leg notional. Variance scales with duration²
  and offsets carry premium gain on the Sharpe ratio. The iter 015
  plateau at 77 is the static-stack family's true ceiling at the
  prescribed 0.9/0.6 NTSX weights." This generalizes the iter 016/021
  σ²_port-absorption finding to the *static* (no-vol-management)
  case, completing the picture: σ²_port either absorbs overlays
  dynamically (iter 016/021) or compounds them via DSR/MDD on the
  static base (iter 033).

## Citations used

Primary (book):
- `[risk_parity, p.5, p.10-11, ch.1, ch.5]` — Asness-Frazzini-Pedersen
  2012 risk-parity argument; bond term-premium decomposition.
- `[leverage_for_the_long_run, p.19-20]` — leverage on diversified base.
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.

Papers / web:
- **Asness, Frazzini & Pedersen (2012). "Leverage Aversion and Risk
  Parity."** *Financial Analysts Journal* 68(1): 47-59. SSRN: 1728082.
- **Koijen, Moskowitz, Pedersen & Vrugt (2018). "Carry."** *Journal
  of Financial Economics* 127(2): 197-225. DOI:
  10.1016/j.jfineco.2017.11.002. Bond carry premium decomposition;
  20-30y duration band has the largest term premium.
- **Cochrane & Piazzesi (2005). "Bond Risk Premia."** *American
  Economic Review* 95(1): 138-160. DOI: 10.1257/0002828053828581.
  Term-structure factor predicts bond excess returns over cash.
- **Ilmanen (2011). *Expected Returns: An Investor's Guide to
  Harvesting Market Rewards.*** Wiley. Chapters 6-7 — term premium
  + bond carry as primary expected-return source.
- **Bailey & López de Prado (2014). "The Deflated Sharpe Ratio."**
  *Journal of Portfolio Management* 40(5): 94-107. DSR formula.
- WisdomTree NTSX prospectus — 90 % equity + 60 % UST futures
  (manufacturer-prescribed weights, preserved verbatim from iter 015).

## Next iteration suggestions

Iter 033 partially-falsifies the long-duration-bond hypothesis on
the static stack but opens three structurally distinct paths forward:

1. **iter 034: Bond carry SLEEVE (zero-net-notional)** — replace
   iter 033's full bond substitution with a *zero-net-notional*
   duration spread layered on iter 015's base:
   ```
   net = 0.9 SPY + (0.6 - α) IEF + α TLT
   ```
   for α ∈ {0.1, 0.2, 0.3}. Hypothesis: the spread vol (TLT − IEF)
   is much smaller than TLT vol alone (~6-8% vs ~14%) — preserves
   iter 015's Sharpe AND adds carry premium. **Strongest candidate**:
   directly addresses iter 033's variance offset issue. Citation:
   `[risk_parity, ch.5]` + KMPV 2018 (carry decomposition).

2. **iter 034: FX carry overlay** — long AUDUSD short USDJPY
   (synthetic AUDJPY) carry trade as an overlay on iter 015 base.
   FX carry is typically more decorrelated from equity stress than
   bond carry (Lustig-Verdelhan 2007 AER 97(1) — FX carry has its
   OWN crash pattern, not coincident with equity vol spikes).
   Hypothesis: provides distribution-orthogonal CAGR boost without
   the iter 032 short-vol skew/kurt OR iter 033 bond-vol scale-up.
   Citation: Lustig-Verdelhan 2007 + Burnside et al. 2011.

3. **iter 034: Cross-asset VRP on IWM** — write iter 031 AND-composite
   put-spread on **IWM (Russell 2000)** instead of SPY, layered on
   iter 015 NTSX 0.9 SPY + 0.6 IEF base. Hypothesis: small-cap stress
   timing is partially decorrelated from large-cap (e.g., 2022 IWM
   −36% vs SPY −25%; 2018-Q4 IWM −27% vs SPY −20%) — composite
   corr_SPY drops below iter 032's 0.97, allowing DSR to recover.
   Citation: `[volatility_trading, p.218]` + Asness-Moskowitz-
   Pedersen 2013.

**NOT recommended** (confirmed by this iter):

- **TLT at higher weight** (e.g., 0.9 SPY + 1.0 TLT, total leverage
  1.9×): would worsen MDD breach proportionally (ndx 2022 → ~70%
  MDD); kill B fires hard.
- **TLT at lower weight on static stack** (e.g., 0.9 SPY + 0.3 TLT):
  reduces both carry premium AND variance contribution — likely
  preserves the iter 033 score band (70-75) without breaking the
  plateau. Lowest priority.
- **TLT-only stack** (e.g., 0 SPY + 1.5 TLT): kills equity beta,
  Sharpe falls to ~0.4-0.6 (TLT alone), criterion 1 fails 0/25.
- **Iter 015 IEF + TLT mix sweep**: parameter-tweaking on the same
  axis already known to be a CAGR-MDD trade-off; would inflate PBO.
- **Layered iter 033 + iter 031 VRP overlay**: combines two PROMISING
  72-tier mechanisms; predicted to score ≤ 70 (compound of both
  failure modes — DSR worst from iter 032 + MDD worst from iter 033).

## Conclusion

Iter 033 is a **partial-closure iteration with a clean structural
finding**: long-duration UST swap (TLT vs IEF) on the iter 015 NTSX
0.9/0.6 static-stack base produces a composite scoring 72/100
PROMISING — **score-tied with iter 032's layered composition** (also
72) and 5 below iter 015's 77 STRONG plateau. The hypothesis CAGR
prediction is CONFIRMED but at marginal magnitude (criterion 4
preserved at 15/15; CAGR Δ +0.4-1.0pp), Sharpe edge vs FROZEN
benchmarks is preserved (criterion 1 = 25/25), but Sharpe vs **iter
015 reference** is essentially zero on the canonical post-2009
windows (Δ +0.001/ndx, −0.007/spy) and DSR worst-p stays at 0.31
(criterion 3 = 0/15; Kill C fires). 1 of 6 pre-committed kills fired
(C only); 5 clean (A/B/D/E/F).

The qualitatively novel finding is that **bond-duration is a CAGR-
MDD trade-off, NOT a Sharpe lever** on fixed-weight static stacks at
preserved leg notional. Variance scales with duration² and offsets
carry premium gain on the Sharpe ratio. The iter 015 plateau at 77
is the static-stack family's true ceiling at the prescribed 0.9/0.6
NTSX weights — confirmed independently by iter 032 (layered short-
vol overlay) and iter 033 (longer-duration bond), both of which
score 72 with identical criterion breakdowns.

The convergence to score 72 from two structurally different mechanism
paths (composition vs duration substitution) is itself a structural
finding: **the score-rubric trade-off between criteria 1+4 and
criteria 3+5 is sharper than parameter sweeps reveal** — single
structural changes on the iter 015 stack shift score by ~±5 points
around the plateau without breaking it. Future winners require
*non-static-stack* architecture or *Sharpe-substantive* mechanisms
(target Sharpe ≥ 1.30 cross-dataset to clear DSR with cumulative_n_trials
≥ 4288 safety margin).

The iteration adds 3 trials (`n_trials = 4288`) and **establishes
that the iter 015 NTSX 0.9/0.6 stack is bond-axis exhausted at
score 72-77**. Future iterations should target **(a) bond carry
SLEEVE** (zero-net-notional duration spread on iter 015 base,
preserves variance + adds carry premium), or **(b) FX/commodity
carry** (truly distribution-orthogonal to equity beta), or **(c)
cross-asset VRP on IWM** (decorrelated underlying for the iter 031
AND-composite put-spread).

Top-K rankings are unchanged: iter 016/018/021 triple-tied at 79,
iter 015 at 77, iter 026/031 tied at 76, iter 032/033 tied at 72.
Iter 033 enters the iteration log at score 72 PROMISING.
