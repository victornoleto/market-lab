# Iteration 046 — iter 041 (regime-gated stack, TOP-K #1) + iter 039 (cross-asset VRP basket) at 50/50

## Hypothesis

iter 045 vindicated **out-of-family return-stream addition at moderate
correlation** as a structural mechanism for compounding DSR (corr ≈ 0.58
→ DSR worst-p 0.222 → 0.096 = 57% reduction on iter 037 base). That
combination scored 81 vs the iter 041 ceiling of 84.

**iter 046 transplants the same mechanism onto a higher-Sharpe base**:
keep iter 045's architecture (50/50 convex combo with iter 039's VRP
basket) but swap the static stack (iter 037) for the **regime-gated
stack** (iter 041, the loop's TOP-K #1 at score 84). iter 041's
binary-VIX-20 weight modulation already delivers DSR 0.168 (lower than
iter 037's 0.222 baseline) and a higher Sharpe ceiling. If the
iter 045 mechanism replicates, the expected DSR worst-p reduces from
0.168 toward ≈ 0.07-0.08 (below the 10pt → 15pt scoring band cutoff
of 0.05? — borderline) while preserving:

- Sharpe edge across all 3 datasets (iter 041 alone hits +0.10 on all 3;
  iter 039 alone hits +0.46/+0.39/+0.61 vs frozen benchmarks).
- MDD safety from iter 039's T-bill collateral leg.
- Walk-forward 8/8 robustness preserved from both components.

The CAGR-floor blocker that capped iter 045 at 5/15 (1/3 datasets pass)
is **expected to persist** (iter 041 has 13.0/15.7/18.6% CAGR × 0.5 +
iter 039's ≈5.5% × 0.5 = 9.3/10.6/12.1%; spy/ndx still under floor by
1.4 pp / 3.3 pp). This is a **predicted limitation** — same structural
constraint as iter 045 — not a refutation of the hypothesis.

**Predicted score range**: 81–86 STRONG. The 5-pt swing is the DSR
band: if worst-p < 0.05 → 15/15 → 86; if 0.05–0.10 → 10/15 → 81. Either
way iter 046 should match-or-beat iter 045 (81) and reach toward iter
041's 84 ceiling on the orthogonal axis (DSR via diversification rather
than gate amplitude).

## Primary citation

`[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack with
regime-conditional weight tilts at preserved leverage (iter 041 base
architecture).

## Additional citations

- `[volatility_trading, p.218]` — Sinclair (2013) on cross-asset VRP
  harvesting (iter 039 base architecture).
- `[advances_fin_ml, ch.17-18]` — regime detection / Markov-switching
  (iter 041's binary VIX gate).
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with
  cumulative `n_trials`; combining low-correlation strategies with
  positive Sharpes improves the deflated p-value (the empirical recipe
  iter 045 vindicated).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate (G6).
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
  (iter 041's VIX[t-1] convention).
- Whaley (2009), JPM 35(3), 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator.
- Bekaert-Hoerova (2014), J Econometrics 183(2), 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
- Bondarenko (2014), QJF 4(3) 1450015 — empirical SPX VRP magnitude.
- Carr-Wu (2009), RFS 22(3) 1311-1341 — variance risk premia framework.
- Driessen-Maenhout-Vilkov (2009), JoF 64(4) 1377-1406 — cross-sectional
  decomposition of index VRP (justifies 3-leg basket vs single SPY).
- Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold's
  strategic role in long-horizon portfolios.
- Asness-Moskowitz-Pedersen (2013), JF 68(3), DOI 10.1111/jofi.12021 —
  cross-asset orthogonality + diversification.
- Markowitz (1952), JoF 7(1) 77-91 — convex combination minimum-variance.

## Edge source

SPY 1x buy-hold buys EXP(market) only. iter 046 buys two
**independently-positive-Sharpe streams**: (a) regime-gated stack of
SPY+IEF+GLD with weights tilted by VIX[t-1] (defensive in stress, more
equity in calm) at total leverage 1.4–1.5×; and (b) cross-asset VRP
harvest on T-bill + 1/3 SPY+QQQ+IWM short put credit spreads. Both legs
are independently positive (corr(r_041, r_039) ≈ 0.55-0.60 expected
from iter 045 measurement) and converge to a **higher deflated
Sharpe** than iter 041 alone via Markowitz convex-combination
variance-reduction.

## Datasets

- **educational** (2006-01-03 → 2026-04-15, ≈20y): GLD-aligned (iter 037
  inception) + VIX-aligned (iter 039 inception). Includes 2008+2020+2022
  stress; tests that diversification holds across full crisis cycle.
- **spy_real** (2009-06-25 → 2026-04-15, ≈17y): post-GFC. Tests in the
  scoring rubric's primary window.
- **ndx_real** (2010-02-12 → 2026-04-15, ≈16y): bench QQQ. iter 041
  stack STILL uses SPY+IEF+GLD (multi-asset benchmark-agnostic);
  iter 039 basket STILL uses SPY+QQQ+IWM regardless of bench
  (matches iter 045's convention).

## Kill criteria (pre-committed)

| kill | observable | threshold | interpretation |
|---|---|---|---|
| **A** Sharpe regress | datasets with `Sharpe_046 < max(041, 039) − 0.05` | ≥ 2 of 3 | composition destructively interferes with components |
| **B** DSR regress vs iter 041 | `worst_p_046 ≥ iter 041's 0.168` | ≥ 0.168 | composition added trials without compounding edge (iter 045 shouldn't have transplanted) |
| **C** MDD breach | `MDD_046 > bench + 5pp` on any dataset | > 60.14 / 38.70 / 40.12% | iter 032 risk re-trigger (joint negative skew) |
| **D** Score regress vs iter 045 | `score_046 < 81` | < 81 | iter 046 strictly inferior to iter 045 (out-of-family wasn't the gain — iter 037 was the lucky draw) |
| **E** G7 cross-lib | `Δ pp > 3.0` on any dataset | > 3.0 pp | engine bug |
| **F** Correlation breach | `corr(r_041, r_039) > 0.85` on any dataset | > 0.85 | orthogonality premise wrong (iter 032's 0.97 signature) |

If **2 or more** kills fire, hypothesis is falsified. If only kill D
fires (and B is clean), iter 045 retains TOP-K #2 and iter 046 becomes
a STRONG-tier closure on "iter 041 base does NOT improve over iter 037
base in 50/50 with iter 039". If only kill B fires (DSR doesn't
compound on iter 041 base, but it did on iter 037), the structural
finding is "VRP diversification compounds DSR only on un-gated stacks
— gate-conditioning consumes the diversification slack".

## Expected budget

- **Configs to test**: 1 (single pre-committed cfg, no grid)
- **Wall-time**: ~15-25 min for the 3-dataset run + ~10 min for gates
  + score (matches iter 045's profile)
- **Files to create**:
  - `hypothesis.md` (this file)
  - `combined_041_039.py` — pandas engine (calls iter 041 +
    iter 039 helpers, then 50/50 convex combo on inner-join)
  - `numpy_reference_combined.py` — pure-numpy reference (composes
    iter 041 numpy ref + iter 039 numpy ref on tail-anchored slice)
  - `run_backtests.py` — single cfg, 3 datasets driver
  - `compute_gates_and_score.py` — gates + scoring + kill evaluation
  - `tests/test_iter_046_combined.py` — TDD specs
    (reductions: w_039=0 → exact iter 041; w_041=0 → exact iter 039;
    midweight = arithmetic mean)
  - `results.json`, `verdict.json`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`
  - `final_report.md`

## Implementation plan

1. **Build `combined_041_039.py` pandas engine** — mirror iter 045's
   structure, but call iter 041's `apply_regime_weights_3leg` instead
   of iter 037's `apply_static_stack_3leg`. iter 041 already does the
   1-day VIX lag internally; iter 039 takes the same VIX series for BS
   pricing of the put spreads. Inner-join the two return streams on
   their date intersection and apply the convex weight.
2. **Build `numpy_reference_combined.py`** — compose iter 041's
   `apply_regime_weights_3leg_np` (which takes a pre-computed regime
   array) + iter 039's `compute_vrp_basket_returns_np` (which takes IV
   array + price levels). Apply 1-day VIX-lag externally to build the
   regime array, then call iter 041 numpy ref. Tail-anchor combine.
3. **TDD specs** (5–8 tests minimum):
   - `w_039=0` reduces exactly to iter 041 net (within 1e-12)
   - `w_041=0` reduces exactly to iter 039 net (within 1e-12)
   - `w_041=w_039=0.5` equals arithmetic mean
   - Negative weights raise `ValueError`
   - Numpy ref ≡ pandas engine within 3 pp CAGR (G7 spec)
   - Identity reduction at calm_weights == stress_weights matches
     iter 045's static-stack baseline (sanity gate)
4. **Run backtests on 3 datasets** — single pre-committed cfg, no grid.
   Cumulative `n_trials` advances 4310 → 4311.
5. **Compute gates + score** — adapt iter 045's `compute_gates_and_score.py`.
   Replace `iter037_dsr_baseline` with `iter041_dsr_baseline` (0.168) for
   kill B. Add iter 046 vs iter 045 score-comparison for kill D.
6. **Generate plots** via `plot_helper.py --iter 046`.
7. **Write `final_report.md`** + update `BASE_MEMORY.md` (frontmatter
   `cumulative_n_trials = 4310 + 1 = 4311`; iteration log entry; top-K
   refresh; auto-prune if > 18 KB).

## Pre-committed config

```python
CFG = {
    "cfg_id": "iter039_on_iter041_50_50",
    # Convex weights
    "w_041": 0.5,
    "w_039": 0.5,
    # iter 041 sub-strategy params (verbatim from iter 041's TOP-K #1 cfg)
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},  # total 1.50×
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},  # total 1.40×
    "vix_threshold": 20.0,
    "cost_bps_per_leg": 0.0002,
    # iter 039 sub-strategy params (verbatim)
    "rf": 0.02,
    "harvest_notional": 1.0,
    "weights_039": {"SPY": 1/3, "QQQ": 1/3, "IWM": 1/3},
    "iv_scales":   {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95, "k_short_pct": 0.90,    # 5/10 OTM put credit spread
    "dte_days": 21, "cost_bps_per_roll": 5.0,
    "rebalance": "daily, 50/50 convex combo of iter 041 regime-gated stack and iter 039 basket",
    "funding_cost_modeled": False,
    "primary_citation": "[risk_parity, ch.5] + [volatility_trading, p.218]",
}
```

All sub-strategy hyperparameters are VERBATIM from iter 041 and iter
039 (no inheritance perturbation). The 50/50 weighting matches iter
045's symmetric Markowitz default — apples-to-apples comparison on the
substituted base.
