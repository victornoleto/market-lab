# Iteration 066 — Final Report

## Verdict

📉 **NEAR_FAIL** — score **37/100** (regression **−53** vs iter 064 base 90),
**winner_conditions_met=False** (1/5 strict — only MDD ceiling),
**5/8 kills fired (A + B + C + D + H)**.

This iteration tested **tree-based meta-labeling** as the
fundamentally different mechanism that iter 065's final report
recommended. A 5-feature Random Forest (n=200, depth=4, seed=42,
class_weight='balanced') was trained via 5-fold purged k-fold CV
with 21-day embargo on bar-level features
(`roll21_sharpe`, `roll63_mdd`, `vix`, `t10y3m`, `sma200_dist`)
to predict `r_064[t] > 0`. Out-of-fold probabilities were thresholded
at 0.5 to produce a binary trade/cash gate, then applied with 5 bps
cost-per-flip.

```
iter 064:  r_064[t]
iter 066:  r_066[t] = pred[t-1] * r_064[t]  -  cost * |pred[t]-pred[t-1]|
           pred[t]  = 1 if RF_OOF.predict_proba(X[t-1])[1] > 0.5 else 0
```

**Hypothesis: comprehensively falsified**.

- **Average OOF AUC = 0.503 / 0.503 / 0.492** across edu / spy / ndx —
  **classifier is at chance**. Per-fold AUCs cluster tightly around 0.5
  (range 0.462-0.534). The 5 features carry **no predictable signal**
  about iter 064's daily-bar return sign.
- **Sharpe drops 0.48-0.72 absolute** vs iter 064 — KILL A fired 3/3
  datasets. Frozen-bench Sharpe is now BELOW SPY/QQQ buy-hold on edu
  (0.66 < 0.78 threshold) and ndx (0.65 < 1.055), and only just clears
  spy threshold by 0.81 < 1.00 (also fail).
- **CAGR drops 5.4-6.9 pp absolute** — gating away even random bars
  destroys CAGR even when the gate is uninformative because it
  introduces 622-703 round-trip transaction-cost flips and converts
  ~33-57% of bars to cash (rf=0).
- **DSR worst-p = 0.85** (spy_real) and edu/ndx are 0.75/0.85 — KILL B
  fired (2.5× iter 064's 0.039 ceiling).
- **edu CAGR = 4.10% < 9.18% floor** — KILL D fired. iter 064's 1st-
  ever non-LETF unlock of the educational floor is **completely
  destroyed** by the noisy gate.
- **Score 37 < 79** — KILL C fired.
- **Avg AUC < 0.52** on 3/3 — KILL H fired.

What survived:
- **G7 cross-lib parity = 0.000000 pp** (3/3) — pandas == numpy on the
  post-prediction transform. Engine is correct; the failure is purely
  about the meta-label being uninformative.
- **F (corr 0.70-0.82)** — gate IS firing meaningfully; not a no-op.
- **G (pct_traded 43-67%)** — within bounds; not over-aggressive.
- **MDD ceiling 3/3** — gating to cash mechanically reduces realised
  variance, lifting MDD from iter 064's 15-17% to 12-14%. Pyrrhic.

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen / Δ064) | CAGR (Δ064) | MDD (Δ064) | DSR p | gates | AUC | pct_traded |
|---|---|---|---|---|---|---|---|
| educational | **0.6615** (−0.0185 / **−0.5560** ❌) | 4.10% (−5.39pp ❌) | 13.65% (−3.62pp) | 0.7539 ❌ | **5/7** | 0.503 | 66.5% |
| spy_real    | **0.8102** (−0.0898 / **−0.5211** ❌) | 4.54% (−5.43pp ❌) | 11.99% (−3.34pp) | 0.6386 ❌ | **6/7** | 0.503 | 54.1% |
| ndx_real    | **0.6547** (−0.3003 / **−0.7208** ❌) | 3.28% (−6.90pp ❌) | 12.49% (−2.25pp) | 0.8498 ❌ | **5/7** | 0.492 | 43.2% |

**Per-dataset gate detail** (G1234567):

| dataset | G1 | G2 | G3 | G4 | G5 | G6 | G7 | total |
|---|---|---|---|---|---|---|---|---|
| edu | ✓ vac | ✗ p=0.75 | ✓ 8/8 | ✓ S=1.10 | ✓ S=1.01 | ✗ ci_low=−0.04 | ✓ 0pp | 5/7 |
| spy | ✓ vac | ✗ p=0.64 | ✓ 7/8 | ✓ S=0.82 | ✓ S=0.76 | ✓ ci_low=+0.04 | ✓ 0pp | 6/7 |
| ndx | ✓ vac | ✗ p=0.85 | ✓ 8/8 | ✓ S=0.69 | ✓ S=0.76 | ✗ ci_low=−0.13 | ✓ 0pp | 5/7 |

Note: G3 walk-forward and G4/G5 OOS still pass because **gating away
half the bars to rf=0 leaves a positive but very small Sharpe** in
each window — the realised mean isn't negative, just much smaller. The
gates G3-G5 don't measure *quality* of the filter, only that residual
windows are positive on net.

**Feature importance avg** (across folds):

| feature | edu | spy | ndx |
|---|---|---|---|
| `sma200_dist` | 0.249 | 0.227 | 0.249 |
| `vix` | 0.214 | 0.208 | 0.218 |
| `t10y3m` | 0.213 | 0.227 | 0.209 |
| `roll21_sharpe` | 0.200 | 0.201 | 0.200 |
| `roll63_mdd` | 0.123 | 0.137 | 0.124 |

The flat distribution (all features 13-25%, no dominant signal) is the
classifier's structural admission: there is **no informative non-linear
boundary** in this 5-feature space for the 1-day-forward sign of iter
064.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **0** | 25 | 0/3 datasets ≥ frozen + 0.10 (Sharpe 0.66 / 0.81 / 0.65 vs 0.78 / 1.00 / 1.055) |
| 2 Gates | **17** | 25 | edu 5/7 → 5pts; spy 6/7 → 5pts; ndx 5/7 → 5pts; cross-ds met → +4 = 19, capped 17 by per-bucket cap |
| 3 DSR | **0** | 15 | Worst-p 0.8498 (ndx) > 0.20 → 0 pts; cumulative n_trials=4336 |
| 4 CAGR floor | **0** | 15 | 0/3: edu 4.10% < 9.18%; spy 4.54% < 11.98%; ndx 3.28% < 15.35% |
| 5 MDD ceiling | **15** | 15 | All 3 well under bench+5pp; gating to cash mechanically lowers realised vol |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (mechanical: any positive Sharpe yields this) |
| **total** | **37** | **100+5** | tier: **NEAR_FAIL** (regression −53 vs iter 064) |

Strict winner conditions: **1/5 met** —
1. Sharpe edge ≥ +0.10 on ≥ 2 ds: ✗ (0/3 vs frozen bench)
2. Gates cross-ds (edu ≥5, spy/ndx ≥4): ✓ (5/6/5)
3. DSR p < 0.05 (worst): ✗ (0.85)
4. CAGR ≥ 0.8×bench on ≥ 2 ds: ✗ (0/3)
5. MDD ≤ bench+5pp on ≥ 2 ds: ✓ (3/3)

Gates pass formally because the classifier is approximately random
(pred ≈ 0.5 on most bars at threshold 0.5 ⇒ ~50% pass-through). The
CAGR/Sharpe destruction comes from the cost on ~620-700 flips per
dataset (5 bps each) plus the half-time-in-cash compounding penalty.

## Configuration tested

```python
CFG = {
    "cfg_id": "iter064_meta_rf_n200_d4_purged5_emb21",
    "rf_params": {
        "n_estimators": 200, "max_depth": 4, "random_state": 42,
        "n_jobs": 1, "class_weight": "balanced",
    },
    "n_folds": 5,
    "embargo": 21,
    "threshold": 0.5,
    "cost_bps": 5.0,
    "feature_cols": ["roll21_sharpe", "roll63_mdd", "vix",
                     "t10y3m", "sma200_dist"],
}
```

cumulative_n_trials advance: 4335 → **4336** (+1).

## Pre-committed kills

| # | kill | fired? | observation |
|---|---|---|---|
| **A** | Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 ds | **❌ FIRED** | 3/3 (Δ −0.56 / −0.52 / −0.72) |
| **B** | DSR worst-p ≥ 0.10 | **❌ FIRED** | worst-p 0.8498 (ndx) — 21.6× iter 064's 0.039 |
| **C** | Score < 79 | **❌ FIRED** | score 37 — 53 below iter 064's 90 |
| **D** | edu CAGR < 9.18% | **❌ FIRED** | edu CAGR 4.10% < 9.18% (loses iter 064's non-LETF unlock) |
| E | G7 cross-lib > 3 pp | ✓ clean | 0.000000 pp (3/3) — pure linear transform |
| F | corr(iter_066, iter_064) > 0.99 | ✓ clean | max 0.823 (edu) — gate fires meaningfully |
| G | pct_traded < 50% on ≥ 2 ds | ✓ clean | 66.5/54.1/43.2% — only ndx below 50% |
| **H** | avg OOF AUC < 0.52 on ≥ 2 ds | **❌ FIRED** | 3/3 (0.503 / 0.503 / 0.492) — classifier is at chance |

**5/8 kills fired ⇒ hypothesis comprehensively falsified**.

## What worked / what didn't

**Worked**:

- **Engine is correct**. 20/20 TDD tests pass; G7 cross-lib parity
  0.000000 pp on all 3 datasets; the post-prediction transform is
  numerically identical between pandas and pure-numpy implementations.
- **Purged k-fold honestly**. 5-fold contiguous split with 21-bar
  embargo means OOF predictions are computed on data the model
  literally never saw (and never even saw within 21 bars of). The
  AUC at chance therefore reflects the **true** predictability of
  the feature space, not in-sample overfit.
- **Robustness 9/9** sub-windows positive — survives because the
  half-cash net return is at worst small-positive in each window.
  Demonstrates that the gate isn't catastrophically bad on any
  single window, just uniformly uninformative.

**Didn't**:

- **The 5-feature space carries no predictable signal**. Avg AUCs
  cluster around 0.50 with feature importance distributed across all
  5 features (range 0.12-0.25). Both vol/vol-of-vol features
  (roll21_sharpe, roll63_mdd) and macro features (vix, t10y3m) and
  the Faber primitive (sma200_dist) are individually weakly predictive
  in cross-section but their non-linear combination is no better than
  random. This holds across 3 independent test datasets — it is NOT
  a small-sample artifact.
- **iter 013's closure ALSO holds for tree-based classifiers**. iter
  013 closed LR meta-labels as "redundant with variance-scaling" on
  iter 016 base. The current iter 064 base IS itself
  variance-scaling-saturated (via iter_046's iter_039+iter_041 stack
  and iter 016's 60:40×MM). The bar-level information left in iter
  064's residual is beyond what 5 commonly-cited features can capture
  with depth-4 trees.
- **Per-bar transaction cost compounds**. 622-703 flips × 5 bps =
  311-352 bps of friction over the test window. With ~50% pass-
  through, the realised CAGR drops 5-7 pp — mechanically, even a
  perfectly random gate destroys CAGR via friction cost.
- **iter 064's 90 is now confirmed as a strict LOCAL OPTIMUM** under
  bar-level binary gating with depth-≤4 tree classifiers on the
  current feature space. The only paths forward are:
  (a) different feature space (e.g., microstructure / order-book
      features — not feasible without intraday data);
  (b) different label horizon (5d / 21d forward Sharpe instead of
      1d sign — converts the problem from sign prediction to
      regime classification);
  (c) different model class (deep nets, gradient-boosted with much
      higher max_depth + regularisation — but still bounded by the
      information content of the 5 features).

## Main lesson (for future iterations)

**iter 066 = STRUCTURAL CLOSURE of "tree-based meta-labeling on iter
064 daily-bar sign with 5 commonly-cited macro/regime/momentum
features"**. Score 37 NEAR_FAIL (regression −53). 5/8 kills (A
Sharpe + B DSR + C score + D edu CAGR + H AUC) fired. The mechanism
is informationally null because the iter 064 base is itself a
saturated multi-regime composite — its residual bar-level return
sign is **not predictable from the standard regime/vol/momentum
feature canon**.

This generalises iter 013's LR meta-label closure ("redundant with
variance-scaling") to tree-based classifiers and broader feature
sets. The closure now spans **2 model classes (LR, RF) × 2 base
strategies (iter 016 vol-managed, iter 064 saturated composite)**.

Three observations that constrain future hunts:

1. **Daily-bar sign of a Markowitz-saturated composite stream is at
   chance from the standard feature canon**. iter 016 closed the
   simpler base (vol-managed); iter 066 closes the saturated base
   (iter 064 composite) for tree-based classifiers. Future
   meta-labeling attempts on this family should target *forward
   N-day Sharpe* (regime classification, N=5 or N=21), not 1-day sign.

2. **Friction cost is binding for any binary gate at daily cadence**.
   Even an oracle classifier flipping 600+ times over 17y at 5 bps
   per flip costs 30+ pp of cumulative return. Rough constraint:
   binary gates at daily cadence need flip rate ≤ 50 per year
   (i.e., regime-level gates with persistence ≥ 5 trading days)
   to not destroy 5-7 pp CAGR via friction alone.

3. **Path to WINNER 95+ from iter 064 has now closed 6 distinct
   axes**: saved-stream-pair recombination (045/051/052/053 → 84),
   internal LETF substitution (062/063 → 79-81), QQQ-trend weight
   sweep (047 → 79, axis closed via Bonferroni), output-VIX gate
   (048 → 83), calm-conditional ext lev (065 → 74), bar-level
   meta-labeling (this iter → 37). **iter 064's 90 stands as a
   strict LOCAL OPTIMUM in 6-dimensional ambient mechanism space**.

The next attack must:
- target a **mechanism not yet tested** (iter 066's structural
  novelty was real — meta-labeling was untested on iter 064 base
  with tree models, but the result was negative); AND
- **avoid daily-cadence friction** (regime-cadence persistence
  ≥ 5d, e.g., monthly rebalance with flip-cost amortisation
  built in); AND
- **target forward-N-day Sharpe / regime label**, not 1-day
  sign, if any meta-labeling is attempted again.

## Structural dead-ends discovered

iter 066 closes **one new axis** plus generalises iter 013's closure:

- **iter 066 (📉 NEAR_FAIL 37, 5/8 KILLS A+B+C+D+H) — Tree-based
  meta-labeling (RF n=200, depth=4, seed=42) on iter 064 saved
  combined stream with 5 standard features (roll21_sharpe,
  roll63_mdd, vix, t10y3m, sma200_dist) at 1-day forward sign label,
  threshold 0.5, 5-fold purged k-fold embargo=21**: classifier
  delivers AUC 0.49-0.50 across 3 datasets — at chance. Sharpe
  drops 0.48-0.72; CAGR drops 5.4-6.9 pp; DSR worst-p inflates from
  0.039 → 0.85. **Bar-level sign of a Markowitz-saturated composite
  stream is informationally null in the standard regime/vol/momentum
  feature canon, regardless of model class** (extends iter 013's
  LR-meta-label closure to tree-based classifiers).

What is **OPEN** for iter 067+:

- **Forward N-day Sharpe label (N=5 or N=21)**: regime classification
  rather than 1-day sign. Lower flip rate → less friction. Predicted
  outcome unclear.
- **Variance-targeting on iter 064 stream** (no leverage; dynamic
  position sizing inversely proportional to realised σ_064): 2nd-
  order CAGR uplift via Moreira-Muir 2017 compounding. iter 016/040
  closed simpler bases. Predicted 80-90.
- **Regime-conditional QQQ_TREND component WEIGHT** (vary w_qqqt
  by VIX regime, NOT output lev): 0.20 calm / 0.05 stress, total
  combined still 1.0 (anchor weight floats 0.80/0.95). No leverage
  → no DSR drag. Predicted 85-93.
- **Plano C sleeve direction** — strategic pivot to passive factor-
  tilted from active hunt. Capped at ~70 by mandate §1 wording but
  could materially change Top-K interpretation.
- **CRSP/Norgate cross-sectional momentum** — survivorship-clean
  data layer would unblock iter 054's closure. Not feasible without
  data budget.

## Citations used

- `[advances_fin_ml, ch.3]` — López de Prado (2018), *Advances in
  Financial Machine Learning*, Wiley. Meta-labeling pattern with
  primary/secondary model decomposition. **Foundational**.
- `[advances_fin_ml, ch.7]` — purged k-fold cross-validation,
  p.103-110. 5-fold with embargo=21 used here.
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with
  cumulative n_trials = 4336. Worst-p 0.8498 — fails 0.05 cut by
  17×.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (0.000000
  pp on all 3 datasets — pure linear transform).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6 (5000
  resamples, stationary block bootstrap with mean block 5).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- `[advances_fin_ml, p.162-164]` — strict 1-day shift no-peek for
  feature engineering.
- Breiman, L. (2001), *Mach. Learn.* 45(1) 5-32, DOI
  10.1023/A:1010933404324 — Random Forest.
- Lopez de Prado, M. (2020), *Mach. Learn. for Asset Managers*,
  Cambridge — independent confirmation of tree-based meta-label
  out-of-sample edge with proper purging.
- Faber, M. (2007), SSRN 962461 — single-asset 200-day SMA TAA
  primitive (one feature).
- Whaley, R. E. (2009), *JPM* 35(3) 98-105, DOI
  10.3905/JPM.2009.35.3.098 — VIX as ex-ante risk regime indicator
  (one feature).
- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2012); preserved
  via iter_046 inside iter 064.
- `[volatility_trading, p.218]` — Sinclair (2013); preserved via
  iter_039 inside iter 046.

## Next iteration suggestions

iter 066 = **STRUCTURAL CLOSURE 37 NEAR_FAIL** of tree-based 1-day
sign meta-labeling on iter 064 base. Three structurally distinct
directions for iter 067:

1. **Variance-targeting on iter 064 stream (no leverage, dynamic
   position size, σ_target = σ_064)**: Moreira-Muir 2017 σ⁻²-target
   wrapper around the iter 064 saved combined stream, with hard cap
   at nominal 1.0 (no upside leverage). Distinct from iter 016
   (which was on simpler 60:40 base) and iter 040 (which was on
   iter 039 standalone, not the composite). **Predicted 80-90**.
   Implementation budget ~30 min (extends iter 064 with single σ
   computation + scaler).

2. **Regime-conditional QQQ_TREND component WEIGHT** (NOT output
   lev): 0.20 calm / 0.05 stress on inner combiner; anchor weight
   floats 0.80 calm / 0.95 stress; total combined stays at 1.0.
   Different from iter 048 (output lev) and iter 065 (calm ext lev)
   because no leverage is added; from iter 047 (static weight sweep)
   because regime-conditional. **Predicted 85-93**. ~45 min budget.

3. **Forward 5-day Sharpe meta-label** (instead of 1-day sign):
   convert label from binary `r_064[t] > 0` to `Sharpe(r_064[t:t+5])
   > 0` and gate accordingly. Lower flip rate (~120/yr at 5d
   persistence vs ~700/yr at 1d) → less friction. AFML-canonical
   "regime label" pattern. **Predicted 60-85** with high variance.
   ~60 min budget.

**Recommended pick for iter 067**: **direction #1 (variance-
targeting)**. It's the cleanest mechanism not yet tested on iter
064 specifically, has bounded implementation risk, and operates on
a dimension orthogonal to leverage (which closed in 056/060/065)
and weight (which closed in 047). The Moreira-Muir 2017 Sharpe
uplift (~+0.05-0.15 expected) is exactly the headroom iter 064
needs to break the 90 ceiling without breaking the DSR margin.

iter 064 stays at **TOP-K #1** with score 90 STRONG, 4/5 winner
conditions, 0/7 kills.
