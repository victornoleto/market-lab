# Iteration 040 — Final Report

## Verdict

🥈 **PROMISING (score 69/100, winner_conditions_met=False)** — strict
regression vs iter 039 base (76 → 69). **3/6 pre-committed kill
criteria FIRED**: A (basket-corrupts-Sharpe), B (DSR-no-improvement),
E (score-regression-vs-iter-039). Hypothesis **FALSIFIED**: Moreira-
Muir 2017 vol-target wrapper applied to iter 039's cross-asset VRP
basket overlay variance ABSORBS the basket harvest into σ²
cancellation — Sharpe ↓ on 2/3 datasets (Δ −0.075 / −0.10 / −0.25),
DSR worst-p ↑ from 0.075 → 0.168, score −7. MDD improved on edu/ndx
(−5pp / −0.4pp) but not enough to compensate the harvest dilution.
Confirms BASE_MEMORY note "vol-target wrapper ABSORBS short-vol
overlays (Sharpe-neutral)" — actually slightly negative on basket.

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen) | CAGR (Δ vs 0.8×bench) | MDD (Δ bench+5pp) | gates | DSR p |
|---|---|---|---|---|---|
| educational | **1.036** (+0.356) | 5.48% (−3.70pp) ❌ | 9.04% (−51.10pp) ✅ | 6/7 | 0.168 ❌ |
| spy_real    | **1.213** (+0.313) | 6.40% (−5.58pp) ❌ | 8.94% (−29.76pp) ✅ | 6/7 | 0.112 ❌ |
| ndx_real    | **1.308** (+0.353) | 6.77% (−8.58pp) ❌ | 6.42% (−28.70pp) ✅ | 6/7 | 0.070 ❌ |

vs **iter 039 baseline** (the reference being defended):

| dataset | iter 039 Sharpe | iter 040 Sharpe | Δ | iter 039 DSR p | iter 040 DSR p | Δ |
|---|---|---|---|---|---|---|
| educational | 1.140 | 1.036 | **−0.104** ❌Kill A | 0.075 | 0.168 | **+0.094** ❌Kill B |
| spy_real    | 1.288 | 1.213 | −0.075 (under threshold) | 0.061 | 0.112 | +0.051 |
| ndx_real    | **1.561** | 1.308 | **−0.253** ❌Kill A | **0.006** | 0.070 | +0.064 |

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 25 | 25 | 3/3 datasets beat bench by ≥+0.10 (perfect) |
| 2 Gates | 19 | 25 | edu 6/7, spy 6/7, ndx 6/7 → 5+5+5+4 cross-bonus = 19 (G2 DSR is the sole fail across all 3) |
| 3 DSR | 5 | 15 | worst p=0.1684 (edu) → 5 pts (p<0.20 tier). vs iter 039 worst p=0.075 → 10 pts. **5 pt loss** |
| 4 CAGR floor | 0 | 15 | All 3 datasets fail 0.8 × bench CAGR (T-bill collateral mechanic preserved) |
| 5 MDD ceiling | 15 | 15 | All 3 datasets clean (MDD 6.4-9.0% well below benchmark+5pp) |
| 6 Robustness | 5 | 5 | 9/9 sub-windows Sharpe > 0 (preserved from iter 039) |
| **total** | **69** | **100+5** | tier: **🥈 PROMISING** |

## Configuration tested

```python
CFG = {
    "cfg_id": "vrp_basket_vt_eq3_5_10_1m_t05_L21_cap20",
    # Inherited from iter 039 (preserved verbatim):
    "rf": 0.02,
    "harvest_notional": 1.0,
    "weights": {"SPY": 1/3, "QQQ": 1/3, "IWM": 1/3},
    "iv_scales": {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    # NEW — Moreira-Muir 2017 vol-target wrapper:
    "target_vol": 0.05,    # 5% ann
    "lookback": 21,
    "max_lev": 2.0,
}
```

Single pre-committed config. No grid, no sweep, no post-hoc tuning.
Cumulative n_trials advance: 4304 → 4305.

## What worked / what didn't

**What worked**

- **MDD reduction** on 2/3 datasets (edu −5.3pp, ndx −0.4pp): MM
  scaling did exactly what it was designed to do — shrink exposure
  during high-realized-vol regimes. This is consistent with MM 2017
  Table 4's MDD-improvement column.
- **G7 cross-lib parity at 0.0000pp** on all 3 datasets — pandas and
  numpy implementations agree to floating-point precision (max abs
  return diff < 1e-12).
- **Robustness 9/9 sub-windows Sharpe > 0** preserved (matches iter
  039's perfect score).
- **Sharpe edge vs benchmarks still positive** (+0.31 to +0.36) — the
  basket VRP edge is structurally robust, just diluted by MM scaling.
- **All 6 TDD specs pass** (zero-harvest = rf identity; max_lev=1
  reduces to iter 039; no-lookahead identity; G7 parity; param domain
  errors). Implementation is mathematically sound.

**What didn't (the absorption mechanism)**

- **Sharpe LOSS on 2/3 datasets**: edu Δ −0.104 (just over 0.10
  threshold), ndx Δ −0.253 (well over). The MM scaling's
  inverse-variance weighting moves capital away from the basket
  precisely when realized basket vol is high — but high basket vol is
  CORRELATED with high VRP harvest (because put-spread payoffs scale
  with IV, and IV is correlated with realized vol). So the scaling
  removes harvest from the bars where it would be largest. Net
  effect: variance ↓, mean ↓ proportionally MORE → Sharpe ↓.
- **DSR worst-p degrades from 0.075 → 0.168** — losing 5 score points.
  The dilution of the harvest signal makes the strategy less
  statistically distinguishable from random short-vol exposure under
  the cumulative n_trials = 4305 deflator.
- **CAGR floor stays 0/15** (T-bill collateral structurally caps annual
  return at ~5-7% net). MM scaling did not raise CAGR — in fact CAGR
  edged up only +0.4 to +1.2pp because the cap=2.0× engages only
  briefly in calm regimes (2017 H2, late 2021).
- **Score regression −7 vs iter 039** confirms Kill E.

**The structural lesson**

Moreira-Muir 2017's σ⁻²-scaling Sharpe-lever theorem requires that
the conditional **mean** of the return stream be APPROXIMATELY
CONSTANT across vol regimes. For equity returns that's broadly true
(Sharpe slightly negatively correlated with realized vol but not
catastrophically). For **short-put-spread basket returns**, this
condition is **violated**: VRP harvest mean scales positively with IV
because put-spread premium = f(IV); when IV is high (high realized
vol), the harvest is LARGER per unit notional — so MM is removing
exposure precisely when the harvest expected return is highest. The
result is a structural Sharpe-degrader, not a Sharpe-lever.

This is the same mechanism that closed iter 020/021 (MM-stacked vol-
managed equity + put-spread overlay → Sharpe-neutral): iter 040 is
the cleanest possible test of the same absorption, with NO equity
stack underneath the overlay. The result confirms: **σ²-target
scaling on any short-vol harvest stream is structurally
Sharpe-absorbing, not Sharpe-leveraging.**

## Main lesson (for future iterations)

The VRP-harvester family ceiling at **76 STRONG** is now confirmed
across **four** structurally distinct attacks (iter 026 single-asset,
iter 031 AND-VIX-gate composite, iter 039 cross-asset basket, iter
040 MM-vol-target wrapper). The CAGR-floor 0/15 (T-bill collateral)
+ DSR-bound (cumulative-n_trials deflator + cluster-correlated tails
in 2008Q4) appear to be structural — not parametric — and resist
*any* sizing modulation that tries to lever the existing harvest
signal. **Break-76 in-family will require either (a) replacing
T-bill collateral with a positive-CAGR base layer (raises CAGR floor
score from 0 → 5-15) without re-introducing iter 032's σ²_port
absorption, or (b) introducing an ML meta-label that orthogonally
predicts open/skip on the basket and improves the worst-DSR p-value
without modifying notional sizing.**

Out-of-family: the static-stack family at 79 (iter 037/038) remains
the loop-record STRONG ceiling; iter 040 does not change this.

## Structural dead-ends discovered

**New entry for `DEAD_ENDS.md`** (full text below; 1-line summary
also goes into `BASE_MEMORY.md`):

### MM 2017 σ⁻²-target wrapper on cross-asset VRP basket (iter 040)

- **Pattern**: applying Moreira-Muir 2017's inverse-realized-variance
  scaling to the basket overlay returns (target_vol=0.05, lookback=21d,
  max_lev=2.0×) on iter 039's pre-committed cross-asset VRP basket.
- **Why it fails**: MM 2017's Sharpe-lever theorem requires E[r|σ̂²]
  ≈ constant across vol regimes. Short-put-spread returns violate
  this — VRP harvest mean SCALES POSITIVELY with IV (put-spread
  premium = f(IV)), so σ⁻² scaling removes exposure precisely when
  expected harvest is largest. Net: variance ↓, mean ↓ MORE →
  Sharpe ↓.
- **Empirical evidence (iter 040)**: Sharpe Δ −0.104 / −0.075 / −0.253
  on edu/spy/ndx vs iter 039; DSR worst-p degrades 0.075 → 0.168;
  score 76 → 69. MDD improves modestly but doesn't compensate.
- **What this closes**: any constant-window MM-style σ⁻² scaling
  (target_vol ∈ [3-10%], lookback ∈ [10-60d], max_lev ∈ [1.5-2.5×])
  applied to short-vol-harvest streams. Different windows tune the
  sensitivity but cannot reverse the sign of the absorption mechanism
  (MM theorem applies pointwise per bar).
- **Doesn't close**: ML meta-label (orthogonal classifier predicting
  open/skip rather than scaling notional); base-layer replacement
  (positive-CAGR collateral instead of T-bill); regime-WEIGHT
  modulation across legs (rather than total-notional scaling).

This goes alongside the existing iter-021 closure ("vol-target
ABSORBS short-vol overlays"); iter 040 is the cleanest "no equity
stack underneath" version of that test, removing the alternative
explanation that σ²_port absorption was specific to having a stacked
equity leg.

## Citations used

- **Primary**:
  - `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP harvest;
  - **Moreira & Muir (2017)** *JoF* 72(4) 1611-1644 — vol-target scaling.
- **Supporting**:
  - `[volatility_trading, ch.3, p.41, p.217]` — VRP mechanics + capped tail.
  - `[risk_parity, p.10-11, ch.1]` + `[risk_parity, p.80-81, ch.4]` —
    fixed-weight stack + diversification benefit.
  - `[systematic_trading, p.40, ch.2]` + `[systematic_trading, p.170-171, ch.11]`
    — Carver vol standardisation + IDM ≤ 2.5 cap.
  - **Bondarenko (2014)** *QJF* 4(3) 1450015 — empirical SPX VRP magnitude.
  - **Carr & Wu (2009)** *RFS* 22(3) 1311-1341 — variance risk premia.
  - **Driessen, Maenhout & Vilkov (2009)** *J. Finance* 64(4) 1377-1406
    — cross-sectional decomposition of index VRP.
  - **Bakshi & Madan (2006)** *JFE* 81(2) 471-518 — cross-asset implied
    -vol premia.
- **Methodology**:
  - `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
  - `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
  - `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
  - `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag rule (no look-ahead).

## Next iteration suggestions

The VRP family is now confirmed at 76 ceiling across 4 structurally
distinct attacks. Candidates for **iter 041**, structurally novel:

1. **ML meta-label classifier on iter 039 basket** (BASE_MEMORY
   suggestion #3, not #1): binary open/skip prediction using
   orthogonal features (VIX/VXN/RVX/VVIX z-scores, T10Y3M, EBP,
   realized-vol divergence, skew). The mechanism is structurally
   different from notional scaling — it changes the SUPPORT of the
   harvest distribution rather than its sizing. Could break the
   edu DSR=0.075 ceiling without inheriting MM's absorption. Citation:
   `[advances_fin_ml, ch.3 (meta-labelling)]` + LeBaron 2002. ~3-4h
   walltime.

2. **Positive-CAGR base-layer replacement** (out-of-family on VRP
   side, in-family on the static-stack 79 ceiling): replace T-bill
   collateral with iter 037's static stack 0.6 SPY + 0.45 IEF +
   0.45 GLD. Question: does adding the iter 039 basket overlay on
   top of iter 037's stack push score above 79 without re-triggering
   iter 032's σ²_port absorption (the basket has 3 legs vs iter 032's
   1-leg short-spread, so absorption magnitude is 3× smaller per leg)?
   Citation: `[risk_parity, ch.5]` + iter 037 base. ~2h.

3. **Cross-sectional factor timing on factor ETFs (≥10 factors)**
   (deeper backlog, BASE_MEMORY): explicitly STRUCTURALLY OUT of VRP
   family + out of static-stack family. AQR cross-sectional factor
   timing universe (MTUM/QUAL/USMV/SIZE/VLUE/SPLV/IWS/IUSV/SPHQ/
   USMV/QUAL); rank by 12-1 momentum + value composite (Asness 2013
   "Value and Momentum Everywhere"). ≥10 assets → less likely to hit
   iter 003's "≤20-asset homogeneous floor". ~3h.

**Recommended pick: #1 (ML meta-label).** It's the most structurally
novel direction not yet attempted on the basket, and it directly
addresses the failure mode of iter 040 (notional scaling absorbs
harvest; meta-labelling does NOT touch notional, only open/skip).

## Files in this iteration

- `hypothesis.md` — pre-committed hypothesis + kill criteria.
- `vrp_basket_vm.py` — pandas vol-managed basket (180 LoC).
- `numpy_reference_basket_vm.py` — pure-numpy reference (G7 parity).
- `run_backtests.py` — single cfg, 3 datasets.
- `compute_gates_and_score.py` — gates + scoring + kill evaluation.
- `tests/test_iter_040_vrp_basket_vm.py` — 7 TDD specs (all pass).
- `results.json` (630 KB), `verdict.json` (final score artefact).
- `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.
