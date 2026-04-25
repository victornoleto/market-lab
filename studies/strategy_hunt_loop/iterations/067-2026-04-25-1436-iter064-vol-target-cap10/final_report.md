# Iteration 067 — Final Report

## Verdict

🥈 **PROMISING** — score **74/100** (regression **−16** vs iter 064 base 90),
**winner_conditions_met=False** (3/5 strict — Sharpe edge, MDD ceiling,
gates cross-ds met; CAGR floor and DSR fail), **3/8 kills fired
(A + C + D)**.

This iteration tested the **Moreira-Muir (2017) σ⁻² variance-target
overlay** with **cap = 1.0** (no leverage) on iter 064's saved combined
return stream (the current TOP-K #1 strategy). The overlay's σ_target
was set to the dataset's full-window annualised σ of r_064 (≈ 7.3-7.7%).

```
σ̂²_064[t-1] = (rolling-21-day std of r_064)² × 252,  shifted by 1 bar
scale[t]    = clip( σ_target² / σ̂²_064[t-1], 0, 1.0 )    # cap = 1.0
r_067[t]    = scale[t] · r_064[t]  −  cost_bps · |scale[t] − scale[t-1]|
```

**Hypothesis: partially confirmed but bounded by structural cost asymmetry**.

- The overlay **does reduce realised variance** (MDD drops 2-4 pp on all
  3 ds, from 17/15/15% → 13/13/12%; rolling 1y vol is meaningfully
  damped).
- The overlay **has corr 0.94-0.96** with iter 064 — not a no-op (KILL F
  clean) and not a near-replica.
- **Sharpe vs SPY/QQQ frozen benchmarks remains very strong** (1.17/1.26/1.28
  vs frozen 0.78/1.00/1.055) — criterion 1 = **25/25** pts.
- **BUT Sharpe REGRESSES vs iter 064** by 0.04-0.09 absolute on all 3 ds
  (KILL A fires 2/3). The mean exposure (0.88) drops faster than the
  realised σ drops, because cap = 1.0 caps the upside while de-risking
  binds in stress — average exposure < 1.0 leaks ~2 pp of CAGR.
- **CAGR drops 1.9-2.2 pp absolute** on all 3 ds (KILL D fires on edu:
  7.61% < 9.18% floor, losing iter 064's 1st-ever non-LETF unlock).
- **Score 74 < 79** triggers KILL C (PROMISING regression).
- **DSR worst-p 0.0757 (spy_real)** — close to 0.05 but fails. The
  Sharpe drop isn't catastrophic; cumulative n_trials advance to 4337
  costs only ~+0.0001 absolute on the t-stat penalty.

What survived:
- **G7 cross-lib parity = 0.000000 pp** on all 3 ds — pandas vs numpy
  reference exact to fp tolerance. Engine is correct; the failure is
  about the mechanism's inherent cost asymmetry, not numerical bug.
- **G3 walk-forward 8/8** profitable on edu, 7/8 on spy/ndx — same as
  iter 064 (variance-target preserves window-level positivity).
- **G4 OOS, G5 FWD post-2020** all positive — overlay doesn't break
  any individual sub-window.
- **G6 bootstrap CI low > 0** on all 3 ds.
- **Robustness 9/9 sub-windows positive** — overlay is monotonically
  positive across regimes; it just trims everything ~12%.
- **MDD ceiling 3/3** with ~22 pp slack on edu, ~25 pp on spy, ~28 pp
  on ndx.

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen / Δ064) | CAGR (Δ064) | MDD (Δ064) | DSR p | gates | scale_mean | corr |
|---|---|---|---|---|---|---|---|
| educational | **1.1716** (+0.4916 / −0.0459) ❌A | 7.61% (−1.88pp ❌D) | 13.25% (−4.02pp ✓) | 0.0583 | **6/7** | 0.8880 | 0.9445 |
| spy_real    | **1.2555** (+0.3555 / −0.0758) ❌A | 7.93% (−2.04pp) | 13.32% (−2.01pp ✓) | 0.0757 | **6/7** | 0.8844 | 0.9551 |
| ndx_real    | **1.2828** (+0.3278 / −0.0927) ❌A | 7.93% (−2.24pp) | 11.95% (−2.79pp ✓) | 0.0744 | **6/7** | 0.8832 | 0.9529 |

**Per-dataset gate detail** (G1234567):

| dataset | G1 | G2 | G3 | G4 | G5 | G6 | G7 | total |
|---|---|---|---|---|---|---|---|---|
| edu | ✓ vac | ✗ p=0.058 | ✓ 8/8 | ✓ S=1.18 | ✓ S=1.21 | ✓ ci_low=+0.20 | ✓ 0pp | 6/7 |
| spy | ✓ vac | ✗ p=0.076 | ✓ 7/8 | ✓ S=1.10 | ✓ S=1.21 | ✓ ci_low=+0.34 | ✓ 0pp | 6/7 |
| ndx | ✓ vac | ✗ p=0.074 | ✓ 7/8 | ✓ S=1.20 | ✓ S=1.18 | ✓ ci_low=+0.35 | ✓ 0pp | 6/7 |

**Scale distribution**:

| dataset | min | q05 | mean | median | q95 | max | pct_at_cap | n_flips |
|---|---|---|---|---|---|---|---|---|
| edu | 0.127 | 0.417 | 0.888 | 1.000 | 1.000 | 1.000 | 67.5% | 1752 |
| spy | 0.115 | 0.428 | 0.884 | 1.000 | 1.000 | 1.000 | 65.6% | 1524 |
| ndx | 0.138 | 0.441 | 0.883 | 1.000 | 1.000 | 1.000 | 65.1% | 1493 |

The cap binds 65-68% of the time (calm bars where σ̂_064 < σ_target). The
de-risk side bites in the remaining 32-35% of bars, with bottom-5%
exposure at ~0.42 (≈ 60% capital reduction in stress periods like
2008Q4, 2020Q1, 2022Q3). Total turnover ~65-77 (× 5 bps overlay cost
≈ 3-4 pp drag spread across 17-20 years).

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | 3/3 datasets ≥ frozen + 0.10 (edu +0.49 / spy +0.36 / ndx +0.33) |
| 2 Gates | **19** | 25 | edu 6/7 → 5pts; spy 6/7 → 5pts; ndx 6/7 → 5pts; cross-ds met → +4 = 19 |
| 3 DSR | **10** | 15 | Worst-p 0.0757 (spy) ∈ [0.05, 0.10) → 10 pts; cumulative n_trials=4337 |
| 4 CAGR floor | **0** | 15 | 0/3: edu 7.61% < 9.18%; spy 7.93% < 11.98%; ndx 7.93% < 15.35% |
| 5 MDD ceiling | **15** | 15 | All 3 well under bench+5pp; 22-28 pp of slack each |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (Sharpe 1.07-1.47 across all 9) |
| **total** | **74** | **100+5** | tier: **PROMISING** (regression −16 vs iter 064) |

Strict winner conditions: **3/5 met** —
1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✓ (3/3 vs frozen)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (6/6/6)
3. DSR p < 0.05 (worst): ✗ (0.076)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✗ (0/3)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

## Configuration tested

```python
CFG = {
    "cfg_id": "iter064_vt_cap10_lookback21_target_full",
    "lookback": 21,         # Moreira-Muir 2017 canonical
    "cap": 1.0,             # NO LEVERAGE — one-sided overlay
    "cost_bps": 5.0,        # overlay friction
    "rf": 0.0,              # iter 064 stream is already net of rf treatment
    "sigma_target": "full-window σ_064 per dataset",
    # σ_target_edu  = 0.0770
    # σ_target_spy  = 0.0735
    # σ_target_ndx  = 0.0729
}
```

cumulative_n_trials advance: 4336 → **4337** (+1).

## Pre-committed kills

| # | kill | fired? | observation |
|---|---|---|---|
| **A** | Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 ds | **❌ FIRED** | 2/3 (Δ −0.046 / −0.076 / −0.093). Edu just barely below 0.05 threshold. |
| B | DSR worst-p ≥ 0.10 | ✓ clean | 0.076 (spy) — fails 0.05 cut but stays under 0.10 |
| **C** | Score < 79 | **❌ FIRED** | 74 < 79 — PROMISING regression |
| **D** | edu CAGR < 9.18% | **❌ FIRED** | 7.61% — loses iter 064's non-LETF unlock |
| E | G7 cross-lib > 0.5 pp | ✓ clean | 0.000000 pp (3/3) |
| F | corr(067, 064) > 0.995 on ≥ 2 ds | ✓ clean | max 0.955 — overlay fires meaningfully |
| G | scale > 1.0 cap violation | ✓ clean | max=1.000 strict (3/3) |
| H | mean(scale) ≥ 0.99 (no-op) | ✓ clean | 0.88 (3/3) — overlay binds 32-35% of bars |

**3/8 kills fired (A + C + D)** — not catastrophic (vs iter 066's 5/8)
but conclusive: the σ⁻² overlay with cap = 1.0 is **structurally
inferior** to the unwrapped iter 064 base for the score function as
defined.

## What worked / what didn't

**Worked**:

- **Engine is correct**. 11/11 TDD tests pass; G7 cross-lib parity
  0.000000 pp on all 3 datasets; pandas vs numpy reference identical to
  fp tolerance. The cap = 1.0 invariant strictly enforced.
- **σ_target derivation honest**. Full-window σ avoids cherry-picking;
  same closed-form on each dataset. No hyperparameter tuning happened
  on this iteration.
- **Sharpe vs SPY frozen benchmarks**: edu +0.49, spy +0.36, ndx +0.33
  — these are HUGE Sharpe edges by absolute standards; the strategy
  is **risk-adjustedly** dominant over buy-and-hold.
- **MDD reduction confirms the de-risk hypothesis**. The overlay shaves
  2-4 pp of MDD without breaking any individual gate window.
- **Robustness 9/9** sub-windows positive — overlay never destroys a
  3-year segment.

**Didn't**:

- **Sharpe regresses vs iter 064**. The mean drops faster than σ when
  cap = 1.0 because:
  1. Capping at 1.0 sacrifices the calm-regime "lever-up" half of the
     Moreira-Muir benefit (which is responsible for ~50% of MM's
     measured Sharpe boost).
  2. The de-risk-only half is **conservative on average exposure** —
     mean(scale) = 0.88 means we lose 12% of the underlying mean.
  3. iter 064 is **already a saturated multi-stream composite** —
     its conditional variance is already dampened by the inner
     iter_046 (vol-managed-via-iter-016) machinery. The residual
     autocorrelation in σ̂_064 is too weak to deliver a Sharpe lift
     from σ⁻² scaling on top.
  4. The overlay turnover is meaningful (1500-1750 flips × 5 bps ≈
     3-4 pp friction).
- **CAGR floor binding on edu**. iter 064 had 9.49% > 9.18% floor by
  31 bps; the overlay's −1.88 pp drag drops it to 7.61% — well below
  floor. KILL D fires.
- **DSR worst-p inflates from 0.039 → 0.076**. Mostly because the
  Sharpe estimator's mean dropped while σ also dropped — the t-stat
  on (μ/σ) compounds in a way that doesn't favour the overlay.
- **iter 064's 90 = strict LOCAL OPTIMUM in 7 mechanism axes**.
  saved-stream-pair (045/051/052/053 → 84), internal LETF substitution
  (062/063 → 79-81), QQQ-trend weight sweep (047 → 79), output-VIX
  gate (048 → 83), calm-conditional ext lev (065 → 74), bar-level
  meta-labeling (066 → 37), AND now σ⁻² cap-1.0 overlay (067 → 74).

## Main lesson (for future iterations)

**iter 067 = STRUCTURAL CLOSURE of "one-sided σ⁻² variance-target
overlay (cap = 1.0) on iter 064 saturated composite"**. Score 74
PROMISING (regression −16). 3/8 kills (A Sharpe + C score + D edu CAGR)
fired.

The mechanism is partially valid (MDD drops, regime-positive
robustness preserved) but **fails the Sharpe-and-CAGR joint test**
because the iter 064 base is itself a vol-managed-via-iter-016
saturated stream. Its conditional variance autocorrelation is too
weak (after inner iter_046 / iter_039 / iter_041 dampening) for a σ⁻²
overlay with cap = 1.0 to do anything more than evenly trim 12% of
average exposure.

This generalises iter 016's MM closure ("vol-target × 60:40 → 79
ceiling") to **the saturated-composite anchor** with cap = 1.0:

| iter | base | cap | score | finding |
|---|---|---|---|---|
| 016 | raw 60:40 SPY/AGG | 2.5× | 79 | MM with leverage on simple base |
| 040 | iter 039 VRP | 2.0× | 79 | MM with leverage on overlay |
| **067** | **iter 064 saturated** | **1.0** | **74** | **MM no-leverage on saturated** |
| 065 | iter 064 saturated | 1.5× (calm-only) | 74 | calm-conditional ext lev |

Both leverage variants (065 +1.5× calm; 067 cap-1.0 σ⁻²) saturate at
**74 PROMISING ceiling** when applied to iter 064. The ceiling is set
by the **friction-cost asymmetry** (overlay turnover at daily cadence
on a saturated composite is structurally Sharpe-negative when capped).

Three observations that constrain future hunts:

1. **σ⁻² overlay on a saturated composite is closed for cap ≤ 1.5×**.
   Both directions (with leverage 1.5× → 74 in iter 065, without
   leverage 1.0 → 74 in iter 067) hit the same ceiling. The mechanism
   IS exploitable on raw equity (iter 016 → 79 with cap 2.5×), but
   iter 064's pre-vol-managed composite leaves no residual conditional-
   variance signal at daily cadence.

2. **Friction binds the same way at 21-bar lookback**. iter 067's 5 bps
   × 65-77 turnover ≈ 3-4 pp drag is meaningful but small; the more
   binding constraint is the **average exposure < 1.0** when cap = 1.0
   (12% mean drag from cap = full CAGR loss × 0.12 ≈ −1.8 pp on 9.5%
   base). This is a **structural cap** on cap-1.0 overlays, not a
   tunable.

3. **iter 064's 90 holds across 7 closed mechanism axes**. The path
   forward is structurally NEW universe / cadence / regime, not new
   overlays on iter 064. Specifically:
   - **Lower-cadence regime label** (forward 5d / 21d Sharpe) — could
     break iter 066's daily-bar-meta-label closure.
   - **Different anchor strategy** (not iter 046-derived) — fresh
     base whose conditional variance has stronger autocorrelation.
   - **Dynamic σ_target** (rolling instead of full-window) —
     adaptive target that tracks regime; harder to close cleanly.

## Structural dead-ends discovered

iter 067 closes **one new axis**:

- **iter 067 (🥈 PROMISING 74, 3/8 KILLS A+C+D) — Moreira-Muir
  variance-target overlay (cap = 1.0, lookback = 21d, σ_target =
  full-window σ_064) on iter 064 saturated composite return stream**:
  overlay reduces MDD 2-4 pp and preserves Sharpe edge vs SPY frozen
  bench (+0.33-0.49) BUT regresses Sharpe vs iter 064 by 0.04-0.09 due
  to mean-exposure cap and turnover friction. CAGR drops 1.9-2.2 pp
  uniformly, killing edu's 9.18% non-LETF floor unlock. **Closes σ⁻²
  cap-1.0 overlay axis on iter 064 saturated composite anchor**, which
  combined with iter 065's cap-1.5× closure means the σ⁻² overlay
  family on iter 064 saturates at 74 PROMISING for any cap ∈ [1.0, 1.5].
  Generalises iter 016's MM closure to the saturated-composite case
  with the additional constraint that **mean(scale) drag dominates
  variance-reduction benefit** at the iter 064 level of internal
  vol-management saturation.

What is **OPEN** for iter 068+:

- **Forward 5-day Sharpe meta-label on iter 064** (instead of iter 066's
  1-day sign): 5d regime classification with persistence ≥ 5d → ~120
  flips/yr (vs 700/yr in 066) → much less friction. AFML-canonical
  pattern. **Predicted 60-85** with high variance.
- **Regime-conditional QQQ_TREND component WEIGHT** (NOT output lev,
  NOT ext lev): 0.20 calm / 0.05 stress on inner combiner; anchor weight
  floats 0.80 calm / 0.95 stress; total combined stays at 1.0. No
  leverage. Different from iter 048 (output VIX gate), iter 065 (calm
  ext lev), iter 067 (σ⁻² overlay) because it **adjusts the inner
  Markowitz weight, not the output scale**. **Predicted 85-93**.
- **Fresh anchor (not iter 046-derived)** — search for a strategy where
  conditional variance autocorrelation > iter 046's residual. Strong
  candidates: cross-asset trend (Hurst-based regime), credit-spread
  regime, emerging-market value-momentum.
- **Plano C sleeve direction** — strategic pivot to passive factor-
  tilted from active hunt. Capped at ~70 by mandate §1 wording.
- **CRSP/Norgate cross-sectional momentum** — survivorship-clean data
  layer would unblock iter 054's closure. Not feasible without data
  budget.

## Citations used

- `[volatility_trading, p.218]` — Sinclair (2013), *Volatility Trading*
  2nd ed. — variance-target sizing primitive; canonical σ⁻² rule.
- **Moreira & Muir (2017)**, *Journal of Finance* 72(4): 1611-1644.
  DOI 10.1111/jofi.12513. "Volatility-Managed Portfolios" — σ⁻²
  scaling with leverage; we use cap = 1.0 variant. Their Table 4
  reports +0.10 to +0.30 Sharpe gain on equity vol-managed — we
  observe 0 to slightly negative on iter 064 saturated composite.
- `[advances_fin_ml, p.162-164]` — López de Prado (2018), *Advances
  in Financial Machine Learning*, Wiley. Strict shift(1) on σ̂ for
  no-look-ahead.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials = 4337.
  Worst-p 0.0757 — fails 0.05 cut by ~0.026.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (0.000000
  pp on all 3 datasets — pandas vs numpy reference exact).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6 (5000
  resamples, stationary block bootstrap with mean block 5).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- `[systematic_trading, p.40, ch.2]` — Carver (2015) σ standardisation.
- `[systematic_trading, p.170-171, ch.11]` — Carver IDM ≤ 2.5; we set
  cap = 1.0 well below IDM.
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen; preserved via
  iter_046 inside iter 064.
- Bondarenko (2014) *QJF* 4(3): 1450015 — variance autocorrelation
  in vol-harvesting P&L (rationale for predictability assumption).

## Next iteration suggestions

iter 067 = **STRUCTURAL CLOSURE 74 PROMISING** of σ⁻² cap-1.0 overlay
on iter 064 saturated composite. Three structurally distinct
directions for iter 068:

1. **Regime-conditional QQQ_TREND component WEIGHT** (NOT output lev,
   NOT ext lev): 0.20 calm / 0.05 stress on the inner combiner;
   anchor weight floats 0.80 calm / 0.95 stress; total combined
   stays at 1.0 (no leverage). Different from iter 048 (output VIX
   gate), iter 065 (calm ext lev), iter 067 (σ⁻² overlay) because
   it **adjusts the inner Markowitz weight, not the output scale**.
   **Predicted 85-93**. ~45 min budget. **Recommended pick** —
   orthogonal to leverage / σ-overlay axes both now closed.

2. **Forward 5-day Sharpe meta-label** on iter 064 (instead of iter
   066's 1-day sign): convert label to `Sharpe(r_064[t:t+5]) > 0`
   and gate accordingly. ~120 flips/yr (vs 700/yr in 066) → much
   less friction. AFML-canonical "regime label" pattern. **Predicted
   60-85** with high variance. ~60 min budget.

3. **Fresh anchor (not iter 046-derived)** — search for a strategy
   where conditional variance autocorrelation > iter 046's residual.
   Cross-asset trend on Hurst-based regime classification, or credit-
   spread regime as the primary signal (not as overlay). High
   exploration cost; reward unclear.

**Recommended pick for iter 068**: **direction #1 (regime-conditional
inner-weight adjustment)**. It's the cleanest mechanism not yet
tested on iter 064 and operates on an axis orthogonal to both
leverage (065) and σ-overlay (067), both now closed at 74. The Markowitz
weight adjustment is mechanically distinct from output scaling — it
preserves total exposure at 1.0 and shifts the inner mix toward QQQ-
trend in calm regimes (where Faber 2007's 200d-trend filter is most
informative) and toward iter 046 in stress (where iter 016's vol-
management is most defensive). Expected Sharpe lift +0.05-0.15 with
no leverage and no friction asymmetry.

iter 064 stays at **TOP-K #1** with score 90 STRONG, 4/5 winner
conditions, 0/7 kills.
