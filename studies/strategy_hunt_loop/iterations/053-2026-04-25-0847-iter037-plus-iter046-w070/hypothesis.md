# Iteration 053 — iter 037 + iter 046 reverse-weight Markowitz Pareto-optimum at w_037=0.70

## Hypothesis

iter 052 closed the iter 041 + iter 026 family at Pareto 79 and confirmed
that **iter 037 strictly dominates iter 041 as the saved-stream anchor**.
The remaining recommended path #1 in BASE_MEMORY is to substitute
iter 046 (TOP-K #1, 85/100, the 50/50 blend of iter 041 + iter 039) for
iter 026 as the second component on the iter 037 anchor. The
hypothesis: **at the score-Pareto-optimum weight, the higher Sharpe of
iter 046 (1.20 vs iter 026's 1.13 on edu) lifts the combined Sharpe
into the [1.10, 1.20] range, which crosses the 0.10 DSR score-bucket
boundary and yields score 86-90**, while iter 037's higher CAGR
(13-18% across datasets) preserves 3/3 CAGR floor pass at
high-w_037 weights.

The Markowitz pre-screen artifact (`markowitz_prescreen.txt`) computed
empirical correlations and weight-sweep predictions on the saved
streams BEFORE running the backtest. The pre-screen reveals the
structural risk of this composition.

## Primary citation

`[risk_parity, ch.5]` (Asness-Frazzini-Pedersen 2013, archived Roncalli
*Introduction to Risk Parity and Budgeting*) — risk-parity stack
architecture used by both iter 037 (3-leg static stack) and iter 041
(regime-modulated stack, embedded in iter 046).

## Additional citations

- **Markowitz, H. (1952)**, *Portfolio Selection*, Journal of Finance
  7(1), 77-91 — convex-combination Sharpe identity used to derive
  w_037 = 0.70 (validated to 4 decimals on 12/12 datasets across iter
  049-052).
- `[volatility_trading, p.218]` (Sinclair 2013) — VRP harvest
  architecture inside iter 039 (basket put-cs) which is embedded in
  iter 046 at 50% weight.
- **Whaley, R.E. (2009)**, *Understanding the VIX*, Journal of
  Portfolio Management 35(3) 98-105 — VIX regime classifier inside
  iter 041 (calm/stress weights), embedded in iter 046 at 50% weight.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials. At
  n_trials = 4320 (4319 + 1), the binding edu Sharpe needed for DSR
  p < 0.05 is approximately 1.18.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).

## Edge source

iter 046's high standalone Sharpe (1.20/1.32/1.38 — TOP-K #1) lifts
the combined return per unit of risk; iter 037's higher CAGR component
(14-18% across datasets) lifts the combined CAGR floor pass-rate to
3/3. The score function rewards this trade-off if combined Sharpe
crosses the DSR 0.10 score-bucket boundary (need Sharpe ≥ ~1.10
empirically, per iter 052's interpolation).

## Pre-screen finding (CRITICAL)

**Empirical correlation corr(iter 037, iter 046) = 0.9554/0.9574/0.9304
on educational/spy_real/ndx_real** — far above the Kill F threshold
(0.85). This is a structural consequence: iter 046 = 0.5 * iter 041 +
0.5 * iter 039, and iter 041 is itself a regime-modulated stack of
SPY+IEF+GLD — the exact same instruments as iter 037. The two streams
share roughly 91-95% of their daily-return variance.

This means the iter 037 + iter 046 combo is **near-degenerate** as a
Markowitz combination: the diversification gain is essentially zero,
and the combined Sharpe is bounded above by the higher-Sharpe
component (iter 046's 1.20 on edu). The pre-screen sweep confirms
this:

```
w_037   edu_S    edu_C   spy_S    spy_C   ndx_S    ndx_C   c1  c4  c1+c4
0.05  +1.1866   9.43%  +1.3121   9.76%  +1.3690  10.24%   25   5     30
0.50  +1.0683  11.73%  +1.2240  12.51%  +1.2588  13.90%   25  10     35
0.70  +1.0294  12.73%  +1.1926  13.72%  +1.2201  15.51%   25  15     40 ←
0.95  +0.9896  13.94%  +1.1596  15.22%  +1.1806  17.50%   25  15     40
```

The score-Pareto-optimum sits at w_037 ∈ [0.70, 0.95] (c1+c4 = 40
plateau), and within the plateau, the highest combined edu Sharpe is
at **w_037 = 0.70** (1.029).

**Pre-committed weight: w_037 = 0.70, w_046 = 0.30**.

## Datasets

- **educational** (SPYSIM synth 40y): iter 037 + iter 046 streams
  cover 2006-01 → 2026-04 (5101 bars overlap). Includes 2008 GFC,
  2020 COVID, 2022 rate-hike. Most stress regimes available.
- **spy_real** (SPY/Tiingo 17y): iter 037 + iter 046 streams cover
  2009-06 → 2026-04 (4226 bars overlap). Post-GFC primary validation.
- **ndx_real** (QQQ/Tiingo 16y): iter 037 + iter 046 streams cover
  2010-02 → 2026-04 (4066 bars overlap). Highest CAGR benchmark.

## Kill criteria (pre-committed)

| kill | criterion | threshold | rationale |
|---|---|---|---|
| **A** Sharpe regression | observed Sharpe < pre-screen prediction − 0.10 on ≥ 2 ds | engine bug or formula mispredict | Markowitz residual = 0.0000 on 12/12 prior datasets |
| **B** DSR worst-p ≥ 0.10 | DSR worst-p across 3 datasets | bucket boundary | iter 052 stuck at 0.118 in same bucket |
| **C** CAGR floor < 3 of 3 | per-dataset CAGR ≥ 0.8 × benchmark | floor pass | predicted 3/3 at w_037=0.70 |
| **D** Markowitz residual ≥ 0.05 | observed − predicted Sharpe on ≥ 2 ds | formula validation | 4-decimal accuracy on 12/12 prior datasets |
| **E** G7 cross-lib > 3 pp | per-dataset CAGR diff between pandas/numpy | engine parity | iter 047-052 all 0.0000 pp |
| **F** corr(037, 046) ≥ 0.85 on any ds | empirical corr on overlapping bars | structural diversification | **PRE-FIRED by pre-screen** (0.93/0.96) |

**Kill F is already FIRED by the pre-screen** — the corr is 0.95
average across datasets, well above 0.85. This iteration proceeds as
a documented confirmation: we expect score ~84 (tie iter 051) and
will close the iter 037 + iter 046 saved-stream-anchor permutation
axis as a structural dead-end (iter 046's iter 041 sub-component
shares > 90% of its return variance with iter 037).

## Expected budget

- Configs to test: **1** (single pre-committed cfg, no Bonferroni)
- Wall-time: ~25 min (saved streams already exist, no re-simulation)
- Files to create: 6 (combined module + numpy reference + run +
  compute + tests + final_report)

## Implementation plan

1. `combined_037_046.py` — fixed-weight convex combination of the two
   saved streams (linear, no time-varying weights).
2. `numpy_reference_iter053.py` — pure-numpy reference for G7 parity.
3. `run_backtests.py` — single-cfg driver at w_037=0.70, w_046=0.30.
4. `tests/test_iter_053_combo.py` — TDD specs covering linearity,
   bounds, Markowitz residual, edge reductions, monotonicity.
5. `compute_gates_and_score.py` — gates + scoring + 6-kill evaluation.
6. `final_report.md` — verdict, headline metrics, kill firings, lesson.
7. `verdict.json` — score artifact via `score_strategy()`.

## Predicted outcome

| dataset | predicted Sharpe | predicted CAGR | predicted DSR p (rough) |
|---|---|---|---|
| educational | 1.029 | 12.73% | ~0.13-0.15 |
| spy_real | 1.193 | 13.72% | ~0.08-0.12 |
| ndx_real | 1.220 | 15.51% | ~0.07-0.10 |

| criterion | predicted points | rationale |
|---|---|---|
| 1 Sharpe edge | 25/25 | 3/3 datasets beat bench + 0.10 |
| 2 Gates | 19/25 | G2 DSR fails 3/3, others pass; cross-ds threshold met |
| 3 DSR | 5/15 | worst-p in [0.10, 0.20) bucket |
| 4 CAGR floor | 15/15 | **3/3 floor pass** (first time at this anchor pair) |
| 5 MDD ceiling | 15/15 | predicted MDD < benchmark + 5pp on all 3 |
| 6 Robustness | 5/5 | both components 9/9 sub-windows positive |
| **Total** | **84/100** | tied with iter 051 (TOP-K #2) |

Strict winner conditions met: **4/5** (DSR p < 0.05 fails). Same gap
as iter 051/052.

## Why proceed despite Kill F pre-firing

1. **Documented structural finding**: Kill F at corr 0.95 confirms
   iter 046's iter 041 sub-component shares > 90% return variance
   with iter 037. This is a NEW structural dead-end worth recording in
   `DEAD_ENDS.md`.
2. **3/3 CAGR floor pass at this weight**: a new feature for the
   iter 037 anchor family (iter 045 had 1/3, iter 051 had 3/3 with
   iter 026 at w=0.80). Confirms the score-function plateau analysis
   identified by the pre-screen.
3. **Score prediction (84) ties TOP-K #2**: validates the methodology
   without regression. Same number of strict winner conditions (4/5)
   as the prior best.
4. **Closes the iter 037 + iter 046 axis cleanly**: future iterations
   need not re-test this combo. With this closure, all iter 037
   anchor + saved-stream-2nd-component permutations are exhausted
   (iter 026, iter 039, iter 046 all tested).

## Markowitz pre-screen

See `markowitz_prescreen.txt` for the full sweep + correlation
measurement (Pareto plateau identification + score function
projection).
