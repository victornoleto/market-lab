# Iteration 063 — Internal-LETF UPRO substitution on iter 058 (DSR-clearing) anchor

## Hypothesis

iter 062 closed the internal-LETF axis on iter 037 anchor (CAGR-clearing
branch, 79-STRONG ceiling) at preserved-equity weighting (0.20 UPRO +
0.65 IEF + 0.65 GLD). Sharpe-lift hypothesis was falsified: combined
Sharpe LOWER on 3/3 datasets (Δ −0.029 / −0.088 / −0.073 vs iter 037)
because UPRO/TQQQ daily-reset vol decay (CAGR ≈ 3·CAGR_SPY −
½·9·var_SPY) plus internal swap+expense (~1.86%/yr baked in) drag
exceeded the diversifier-overweight contribution at this weight scheme.
However, the **CAGR uplift hypothesis was confirmed** (+1.3-2.1 pp on
3/3 datasets) and **MDD ceiling was preserved** (3/3).

The natural follow-up — **direction #1 from BASE_MEMORY** — is to apply
the same internal-LETF substitution to the **DSR-clearing** branch
anchor (iter 058 = iter 046 + HYG_TSM at w=0.10, score 85), where:

1. **Sharpe headroom is much higher**: iter 058's edu Sharpe 1.22 vs
   iter 037's 0.96 → a 0.03-0.09 Sharpe drag would still leave Sharpe
   well above iter 062's combined Sharpe.
2. **DSR is already cleared**: iter 058's worst-p 0.0494 (edu)
   vs iter 037's 0.222 → at fixed cumulative n_trials, lower DSR has
   more room to absorb Sharpe regression before crossing 0.05.
3. **CAGR floor is the binding constraint** on iter 058 (0/15, sole
   gap to WINNER): iter 058 CAGR 8.69/9.01/9.27% vs floors
   9.18/11.98/15.35%. iter 062's CAGR uplift mechanism (+1.3-2.1 pp
   via diversifier overweight) could potentially unlock edu floor
   (8.69% + 1.0-1.5 pp ≥ 9.18%), winning 5 pts and lifting score
   to 85+5 = 90.

The mechanism is the **smallest possible structural perturbation**
of iter 058: only the iter 041 sub-component (regime-weighted
SPY+IEF+GLD) is modified to use synth/real UPRO at preserved equity
exposure. iter 039 (VRP basket — options on SPY/QQQ/IWM) stays
unchanged because options structure does NOT linearly transform
under LETF substitution. iter 058's HYG_TSM 3rd stream and combine
weights (0.50 / 0.50 / 0.10 effective top-level on iter_041_LETF /
iter_039 / HYG_TSM, after factoring 0.90 × 0.50 = 0.45 each on
iter_046 components) are preserved verbatim.

```
iter 058 (canonical):  0.90 · (0.50 · iter_041 + 0.50 · iter_039) + 0.10 · HYG_TSM
iter 063 (this iter):  0.90 · (0.50 · iter_041_LETF + 0.50 · iter_039) + 0.10 · HYG_TSM
                                 ↑ preserved-equity UPRO substitution
```

Where `iter_041_LETF` uses the same regime-weighted-3leg engine as
iter 041, but with:

- **Equity leg**: synth_UPRO (3·r_SPY − 0.91%/252) pre-2009-06-25 +
  real UPRO post; for ndx_real, real TQQQ from 2010-02-12
- **Calm regime weights** (VIX < 20): eq_w=0.2333, bd_w=0.6333,
  gld_w=0.6333 → 1.50 NAV (preserves iter 041's calm 0.70 SPY-equiv
  via 0.2333 × 3, redirects 0.4667 NAV equally to bonds+gold)
- **Stress regime weights** (VIX ≥ 20): eq_w=0.10, bd_w=0.65,
  gld_w=0.65 → 1.40 NAV (preserves iter 041's stress 0.30 SPY-equiv
  via 0.10 × 3, redirects 0.20 NAV equally to bonds+gold)

## Primary citation

`[leverage_for_the_long_run, p.19-25]` — Hsiao & Williams (2017),
*J. Index Investing*, daily-reset LETF formula `r_LETF = leverage·r_base
− daily_expense` and Itô-correction-derived path drift
`CAGR_LETF ≈ leverage·CAGR_base − ½·leverage²·var_base − daily_expense·252`.
Establishes the preserved-leverage zone (1.5-2.0×) where vol decay is
empirically smaller than diversifier diversification benefit.

## Additional citations

- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2012) multi-leg
  risk-parity stack architecture; iter 041 regime-weighted variant
  preserved verbatim.
- `[risk_parity, p.5, p.10-11, ch.1]` — AFP 2012 SSRN 1728082, static
  fixed-weight stack mechanism applied to LETF-substituted equity leg.
- `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP
  harvest; iter 039 base architecture preserved verbatim via saved
  return stream from iter 046.
- `[advances_fin_ml, ch.17-18]` — regime detection (iter 041 VIX gate).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (4332 → 4333).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
  (vacuous for static weights, prior-day-only synth formula, and
  prior-bar VIX in regime detection).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- Whaley (2009), JPM 35(3) 98-105, DOI 10.3905/JPM.2009.35.3.098 —
  VIX as ex-ante risk regime indicator.
- Bekaert-Hoerova (2014), J Econometrics 183(2) 181-192,
  SSRN 2294327 — VIX uncertainty/risk-aversion decomposition.
- Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold
  strategic role.
- Asvanunt-Richardson (2017), JPM 43(2) DOI 10.3905/jpm.2017.43.2.090
  — credit risk premium (HYG_TSM 3rd stream preserved verbatim).
- Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe identity
  (used in pre-committed kill D).
- ProShares UPRO prospectus 2024-2025 — expense ratio 0.91%/yr.
- Hsiao-Williams (2017), *J. Index Investing*, "Leverage for the Long
  Run", DOI 10.3905/jii.2017.8.1.039 — LETF strategic allocation.

## Edge source

iter 058's edge: SPY 1x buy-hold misses (a) the term/gold-carry
diversification of iter 041's regime-weighted stack, (b) the cross-
asset VRP harvest of iter 039's basket, and (c) the credit-carry
risk premium of HYG long-only with 90d trend filter (Asvanunt-
Richardson 2017). iter 063 amplifies this same edge by replacing
the cash equity leg in (a) with internal-LETF UPRO/TQQQ at preserved
SPY-equiv exposure, **redirecting the freed NAV (0.4667 in calm,
0.20 in stress) equally to the bond and gold legs**, harvesting
additional term + commodity premium without changing the equity-
factor exposure.

## Datasets

- **educational** (joined synth/real UPRO + IEF + GLD + iter_039
  + HYG_TSM): window starts at the maximum of (UPRO synth requires
  SPY data) ∩ (IEF, GLD, HYG, VIX availability). HYG inception
  2007-04-12 limits the start. Effective window: ~2007-04-12 →
  2026-04-15 (matches iter 058's effective window).
- **spy_real**: 2009-06-25 → 2026-04-15. Real UPRO + IEF + GLD +
  iter_039 + HYG_TSM. Same window as iter 058's spy_real.
- **ndx_real**: 2010-02-12 → 2026-04-15. Real TQQQ (replaces QQQ
  in iter 062's pattern; here applied to the iter 041 equity leg
  within the iter 046 / iter 058 nesting). Same window as iter 058's
  ndx_real.

All 3 datasets use the same pre-committed cfg
`iter058_with_internal_letf_iter041_only`.

## Kill criteria (pre-committed)

If any of the following observable patterns holds at end of Stage 4,
the hypothesis is falsified regardless of secondary metrics:

| # | Kill | Threshold | Rationale |
|---|---|---|---|
| A | Combined Sharpe regress vs iter 058 by ≥ 0.05 on ≥ 2 of 3 datasets | Drop ≥ 0.05 | iter 062 saw 0.03-0.09 drag on iter 037 anchor; iter 058's iter 041 weight is 0.45 (less than half), so drag should be ≤ 0.04. ≥ 0.05 means LETF substitution drag is *worse* on the higher-Sharpe anchor → falsifies "Sharpe headroom absorbs drag" |
| B | DSR worst-p ≥ 0.10 (2× iter 058's effective ceiling) | worst p ≥ 0.10 | iter 058's worst-p 0.0494 with margin 1.2% from cutoff. With Sharpe drag + 1 trial advance (4332→4333), edu p could push to 0.06-0.08 (still under 0.10). ≥ 0.10 means major regression. |
| C | Score < 79 (iter 062 baseline; iter 058's 85 is unconstrained ceiling) | total_score < 79 | If iter 063 can't even match iter 062's 79 on the supposedly higher-Sharpe-headroom anchor, the substitution mechanism is fundamentally drag-dominated regardless of base anchor |
| D | Markowitz residual ≥ 0.05 on ≥ 2 datasets | abs residual ≥ 0.05 | Engine bug or non-stationary correlation; closes the closed-form composition pattern |
| E | G7 cross-lib > 3 pp on any dataset | abs CAGR diff > 3 pp | Engine bug in synth_LETF or 3-leg or combine logic |
| F | corr(combined_063, combined_058) > 0.99 | avg corr > 0.99 | Combined stream is statistically indistinguishable from iter 058 → no novel info, single-trial DSR penalty wasted |

**Falsification threshold**: ≥ 4/6 kills fired = hypothesis refuted.

**Predicted outcome** (per BASE_MEMORY direction #1): score 80-92.
- If kill A clean (Sharpe drag ≤ 0.04 absorbed): 85-90 range
- If kill A fires (drag > 0.05): 78-83 range
- If CAGR floor unlocks edu (8.69% + uplift ≥ 9.18%): +5 to score
- If DSR clearance preserved on edu (p < 0.05): full 15 DSR pts

## Expected budget

- Configs to test: **1** (pre-committed, no grid)
- cumulative_n_trials advance: 4332 → **4333** (+1)
- Wall-time: ~10-15 minutes
  - Reuse synth_letf engine from iter 062 (no new code)
  - Reuse regime_weights engine from iter 041 (no new code)
  - Reuse iter 039 stream from iter 046 saved subcomponent (no rerun)
  - Reuse HYG_TSM stream from iter 058 saved subcomponent (no rerun)
  - Only: combine + scoring + plotting
- Files to create:
  - `iter041_letf.py` — thin wrapper: build the regime-weighted stack
    with synth/real UPRO substitution at preserved equity exposure.
  - `combine_iter058_letf.py` — convex combo wrapper: 0.50 ×
    iter_041_LETF + 0.50 × iter_039, then 0.90 × that + 0.10 ×
    HYG_TSM.
  - `numpy_reference_iter063.py` — pure-numpy reference for the
    composite stream (G7 parity).
  - `tests/test_iter_063_letf_anchor.py` — TDD specs (≥ 12 tests
    covering identity reduction at SPY → UPRO_synth with leverage=1
    + expense=0; equity-exposure preservation; combiner shape;
    G7 parity; iter 058 reproduction at letf_w=eq_w_canonical).
  - `run_backtests.py` — runs the 3 datasets, writes `results.json`.
  - `compute_gates_and_score.py` — 7-gate battery + score, writes
    `verdict.json` with the 6 pre-committed kills evaluated.
  - `final_report.md` — Stage 5 narrative.

## Implementation plan

1. **TDD**: write `tests/test_iter_063_letf_anchor.py` covering:
   - Identity reduction: `iter041_letf` with leverage=1.0, expense=0,
     calm/stress weights matching iter 041 canonical → reduces to
     iter 041 stream (allow ε floating-point tolerance).
   - Synth UPRO formula: r_synth = 3·r_SPY − 0.91%/252 (replicate
     iter 062's primitive test for portability).
   - Preserved equity exposure: 0.2333 UPRO ≈ 0.70 SPY exposure,
     0.10 UPRO ≈ 0.30 SPY exposure (verify via aggregate equity-beta).
   - Combiner: 0.50 × A + 0.50 × B inner-joins indexes.
   - 0.90 × (0.50 A + 0.50 B) + 0.10 × C inner-joins indexes;
     reduces to iter 058 when A = iter_041 (canonical).
   - G7 cross-lib parity ≤ 3 pp on synthetic data.
2. **Build** `iter041_letf.py`: imports `synth_letf_3leg` from iter 062
   for join_real_and_synth_letf, calls `apply_regime_weights_3leg`
   from iter 041 with preserved-equity weights.
3. **Build** `combine_iter058_letf.py`: imports the iter 058 combiner
   pattern (mirrors `combine_046_plus_hyg`).
4. **Numpy reference**: `numpy_reference_iter063.py` — pure-numpy
   reproduction of the composite stream for G7 parity.
5. **Run all tests** — should be 12-16 tests, all passing.
6. **Run backtests**: `run_backtests.py` over 3 datasets, writes
   `results.json` with required `returns_series` schema.
7. **Compute gates + score**: 7-gate battery using `compute_gates.py`
   pattern from iter 058, writes `verdict.json` with the 6
   pre-committed kills evaluated.
8. **Plots**: `uv run python studies/strategy_hunt_loop/plot_helper.py
   --iter 063`.
9. **Final report + memory update + auto-prune**.
