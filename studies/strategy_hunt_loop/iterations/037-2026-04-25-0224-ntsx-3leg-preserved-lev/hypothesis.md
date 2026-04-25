# Iteration 037 — Leverage-preserved 3-leg static stack: 0.6 SPY + 0.45 IEF + 0.45 GLD (1.50× lev)

## Hypothesis

Iter 036 demonstrated empirically that **a 3rd diversifier extracts
additional Sharpe** (+0.05 cross-ds vs the 2-leg GLD baseline iter 035,
+0.10-0.14 vs iter 015's 2-leg IEF baseline) — confirming Asness-
Moskowitz-Pedersen 2013 cross-asset orthogonality at the third leg.
But iter 036 paid for it with a +0.30× leverage uptick (0.9/0.6/0.3 =
1.8×), which broke the ndx MDD ceiling by +1.41pp and netted
72 PROMISING — the same band as iter 032/033/034 (72), 5 points below
iter 015/035 (77).

The open question this leaves is **whether the 3-leg additive Sharpe
benefit survives at iter 015's preserved 1.5× total leverage**. The
only way to add a 3rd leg at preserved 1.5× is to redistribute weights
from the existing 2-leg base. The minimal, **mechanism-faithful**
re-weighting that preserves the orthogonality argument is to halve the
"diversifier sleeve" between IEF and GLD at equal notional, **and**
shrink equity from 0.9 to 0.6 to keep total leverage at 1.5×:

| leg | iter 015 (2-leg IEF) | iter 035 (2-leg GLD) | iter 036 (3-leg, 1.8×) | **iter 037 (3-leg, 1.5×)** |
|---|---|---|---|---|
| SPY | 0.90 | 0.90 | 0.90 | **0.60** |
| IEF | 0.60 | 0.00 | 0.60 | **0.45** |
| GLD | 0.00 | 0.60 | 0.30 | **0.45** |
| total | 1.50 | 1.50 | 1.80 | **1.50** |

This iteration tests the single pre-committed cfg
`ntsx_3leg_preserved_60_45_45_spy_ief_gld`. The architecture
preserves iter 015's total leverage verbatim while replacing the
IEF-only diversifier sleeve with an equal-notional IEF/GLD split.

The trade-off is structural and pre-known:

- **Equity sleeve cut by 33%** (0.90 → 0.60). SPY is the dominant
  Sharpe contributor across iter 015/035/036 (the levered base's
  growth driver). Cutting equity weight by 33% is expected to reduce
  the absolute return from the equity premium proportionally — **a
  drop of ~3-4 pp/yr CAGR vs iter 036**.
- **Diversifier sleeve gains a 3rd asset class** at constant total
  notional (0.60 → 0.45 + 0.45). Per AMP 2013, the variance
  contribution of the diversifier sleeve at avg pairwise ρ ≈ +0.25
  (ρ_bd_gld measured by iter 036 at +0.21-0.28) drops by ~30-40%
  vs a single-asset 0.6 sleeve, since the two safe-haven legs are not
  perfectly correlated. **Sleeve variance reduction is the only path
  this hypothesis has to overcome the equity-cut Sharpe drag.**
- **Net Sharpe outcome**: depends on whether the variance-reduction
  benefit on the diversifier sleeve compensates for the equity-cut
  drag. The pre-registered prediction is that the 3-leg architecture
  at 1.5× will be **between iter 015 (Sharpe 0.78/1.04/1.06) and
  iter 036 (Sharpe 0.92/1.15/1.15)**, most plausibly closer to iter 015
  with a 0.05-0.10 Sharpe uplift over the 2-leg IEF baseline.
- **Net MDD outcome**: ndx MDD should drop materially below iter 036's
  41.5% (the +0.30× leverage cost is removed) and below iter 035's
  37.0% (one diversifier replaced by a less-correlated pair). Likely
  in the 35-38% range — **clears the 40.12% benchmark+5pp ceiling**.

**Three pre-committed possible outcomes** (per BASE_MEMORY recommended
direction):

1. **Score ≥ 80** (1st ceiling break): Sharpe edge ≥ +0.10 cross-ds
   AND ndx MDD ≤ 40%. Implies the 3-leg orthogonality benefit survives
   the equity-weight reduction. Closes the static-stack family with a
   first 80+ data point and shifts iter 038 priority to refining
   weights (e.g., 0.7/0.4/0.4) or pivoting to non-static for DSR
   PASS at Sharpe ≥ 1.30.
2. **Score 72-77 (tied or marginal regress)**: 3-leg orthogonality
   benefit and equity-cut drag roughly cancel — the static-stack
   family is **leverage-bound at 77 absolute regardless of leg
   count or weight distribution**. Closes static-stack family
   completely. Iter 038 must pivot to non-static or VRP basket.
3. **Score < 70 (regress)**: equity-cut drag dominates the 3-leg
   diversification benefit. Closes both the lev-preserved 3-leg path
   AND the broader claim that 3-leg orthogonality is exploitable on
   a long-only static base. Iter 038 must pivot.

This is a **single most informative remaining cheap test in the
static-stack family** — it definitively classifies the ceiling-break
potential of static return-stacking. ~30 min wall-time, single cfg,
minimal change to iter 036's code.

## Primary citation

`[risk_parity, ch.5]` — multi-leg risk-parity decomposition. Risk-
parity is the limiting case of inverse-variance weighting where each
leg contributes equal **risk** (not equal notional). The 3-leg
0.6/0.45/0.45 weights are NOT risk-parity (equity dominates risk
contribution), but the architectural lesson that increasing leg count
at preserved total leverage shifts variance contribution toward the
lower-variance legs is taken from this chapter.

## Additional citations

- `[risk_parity, p.5, p.10-11, ch.1]` — Asness, Frazzini & Pedersen
  (2012). "Leverage Aversion and Risk Parity." *FAJ* 68(1): 47-59.
  SSRN 1728082. The static-stack mechanism (preserved from iter 015).
- `[risk_parity, p.80-84]` — funding-cost framework (preserved from
  iter 018). Total funding cost scales with total notional (1.5×),
  identical to iter 015. Equity sleeve borrows at libor; bond + gold
  sleeves at futures basis (~0).
- `[leverage_for_the_long_run, p.19-20]` — Hsiao, Williams (2017).
  *J. Index Investing.* Leverage on a diversified base captures
  diversification benefit at minimum funding cost. 1.5× is the
  Hsiao-Williams optimal-leverage zone for a 3-asset base (SPY/IEF/GLD).
- `[advances_fin_ml, p.31-34]` — Lopez de Prado (2018). Cross-library
  parity (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- **Asness, C.S., Moskowitz, T.J. & Pedersen, L.H. (2013).** "Value
  and Momentum Everywhere." *JF* 68(3): 929-985. DOI
  10.1111/jofi.12021. SSRN 1363476. Cross-asset orthogonality across
  3-asset baskets — the core hypothesis tested here. Iter 036 measured
  pairwise ρ ≈ −0.04 average for SPY/IEF/GLD; this iter preserves
  those underlying correlations and tests whether they can extract
  edge at lower leg-weights.
- **Erb, C.B. & Harvey, C.R. (2006).** "The Strategic and Tactical
  Value of Commodity Futures." *FAJ* 62(2): 69-97. DOI
  10.2469/faj.v62.n2.4084. Gold's strategic role on a 60/40 base.
  Halving the gold weight from iter 035's 0.6 to 0.45 still preserves
  the sleeve's "real-yield-decline hedge" function.
- **Koijen, R.S.J., Moskowitz, T.J., Pedersen, L.H. & Vrugt, E.B.
  (2018).** "Carry." *JFE* 127(2): 197-225. §3 — gold's spot-forward
  basis ≈ 0; bond carry term-premium decomposition.
- **Ilmanen (2011).** *Expected Returns.* Wiley. ch.6 (term premium),
  ch.10 (commodity premium magnitudes — gold's standalone Sharpe ~0.55
  on the 21y window matches iter 035's measurement).
- WisdomTree NTSX prospectus — 90/60 weights NOT preserved here; this
  iter departs from the prospectus to test whether the 3-leg
  additivity argument requires the 90% equity weight or works at lower
  weights. The departure is necessary because the prospectus weights
  push total leverage to 1.8× when a 3rd leg is added.

## Edge source

SPY 1x b&h misses the orthogonal diversification across **three**
asset classes at moderate leverage (1.5×). Iter 036 proved the
orthogonality benefit is real (+0.05 average Sharpe vs 2-leg GLD at
1.5× — i.e., the marginal 3rd-leg variance contribution divided by
total stack variance is positive). The question this iter answers is
whether that benefit can survive shrinking equity from 0.9 to 0.6 — a
necessary cost of preserving the leverage budget. If yes, iter 037
delivers the SAME orthogonality edge as iter 036 with iter 015's MDD
behavior, breaking the 77 ceiling.

## Datasets

- **educational** (SPYSIM-substitute SPY+IEF+GLD via GLD-aligned 21y
  window, 2004-11-19 → 2026-04-15): preserves iter 035/036 window so
  all 3-leg iters span identical bars. Tests structural hypothesis on
  the longest available real-data window for the 3-asset basket
  (educational and synthetic windows are not used here because a
  natural SPY+IEF+GLD synth requires three coherent series; no
  testfolio synth covers all three at the same vintage).
- **spy_real** (2009-06-25 → 2026-04-15): post-GFC SPY+IEF+GLD; the
  primary real-data window matching iter 015 / 026 / 034 / 035 / 036
  verbatim.
- **ndx_real** (2010-02-12 → 2026-04-15): tech-heavy QQQ + IEF + GLD;
  the dataset where iter 036's MDD breach occurred. The KEY dataset to
  watch — the equity-cut from 0.9 to 0.6 should drop ndx MDD below
  the +5pp benchmark ceiling (40.12%).

## Kill criteria (pre-committed)

- **Kill A — Sharpe edge < +0.10 vs frozen benchmark on ≥ 2 datasets**:
  the equity-cut drag dominates the orthogonality benefit. **Closes
  the lev-preserved 3-leg path AND the static-stack family within
  ≤ 1.5× lev.** Threshold: count datasets where (Sharpe < bench + 0.10).
  If ≥ 2 fire, kill triggers. Bench: 0.78 / 1.00 / 1.055 (frozen).
- **Kill B — Sharpe regress vs iter 015 (2-leg IEF) by < −0.05 on ≥ 2
  datasets**: the 3-leg architecture at preserved leverage actively
  destroys the 2-leg edge. Closes the "more legs at preserved
  leverage" path. Iter 015 ref: 0.7835 / 1.0442 / 1.0638. Threshold
  per ds: (Sharpe < ref − 0.05). Fire if ≥ 2 of 3.
- **Kill C — DSR worst-p > 0.20**: 77 ceiling holds; the static-stack
  family is leverage-bound at Sharpe ~1.05-1.10. Closes static stack
  completely.
- **Kill D — G7 cross-lib > 3 pp CAGR**: engine bug in 3-leg primitive
  (iter 034 verified at 0.087pp; iter 036 at 0.142pp; iter 037 should
  be similar — same simulator).
- **Kill E — total score < 60 (MARGINAL or worse)**: regress vs both
  iter 015 (77) and iter 036 (72). Closes static-stack family.
- **Kill F — robustness < 7/9 sub-windows positive**: instability from
  reduced equity exposure (regime-dependence on bond+gold).
- **Kill G — ndx MDD > 40%**: even at preserved 1.5× leverage, the
  3-leg architecture breaks tail-risk on tech-heavy data. Closes the
  argument that "lower equity weight → lower tail risk". Threshold
  matches the strict winner condition (frozen benchmark + 5pp =
  40.12%).

## Expected budget

- Configs to test: **1** (single pre-committed cfg, NO grid, NO sweep)
- Wall-time: ~5-15 min (3 datasets × single 3-leg backtest, identical
  scope to iter 034 / 035 / 036)
- Files to create:
  - `synth_stacked_etf_3leg.py` — verbatim copy of iter 036's primitive
    (asset-agnostic; weights set in `run_backtests.py`)
  - `numpy_reference_stacked_3leg.py` — verbatim copy of iter 036's
    numpy reference for G7
  - `run_backtests.py` — adapted from iter 036 (only weights change:
    0.90/0.60/0.30 → 0.60/0.45/0.45)
  - `compute_gates_and_score.py` — adapted from iter 036 (cumulative
    n_trials += 3, kill criteria updated)
  - `tests/test_iter037_3leg_preserved_lev.py` — TDD spec with ≥ 3
    unit tests (load, weights sum to 1.5, invariant under reweighting)
  - `results.json` + `verdict.json` + `final_report.md`
  - `plot_vs_benchmark_spy_real.png` + `plot_vs_benchmark_ndx_real.png`

## Implementation plan

1. Vendor `synth_stacked_etf_3leg.py` and `numpy_reference_stacked_3leg.py`
   from iter 036 verbatim (asset-agnostic, no changes needed).
2. Author `tests/test_iter037_3leg_preserved_lev.py` first (TDD) —
   verify GLD/IEF parquet still load, the 0.60/0.45/0.45 weight set
   gives total leverage 1.50× (matching iter 015), and the simulator
   reduces to a 2-leg case when one weight is set to 0.
3. Adapt `run_backtests.py` from iter 036: change weights to
   0.60/0.45/0.45. Pre-commit single cfg
   `ntsx_3leg_preserved_60_45_45_spy_ief_gld`.
4. Run backtests on all 3 datasets. Save `results.json` with
   `returns_series` key (plot helper requirement).
5. `compute_gates_and_score.py`: 7 gates per dataset (G1 vacuous PASS
   for N=1, same convention as iter 015/034/035/036), DSR with
   `n_trials = 4297 + 3 = 4300`, WF/OOS/FWD/Bootstrap/G7 standard.
   Pre-committed kills A-G evaluated per the thresholds above.
6. Score via `scoring.score_strategy` — output `verdict.json`.
7. Run `plot_helper.py --iter 037` to generate plots vs SPY/QQQ b&h.
8. Write `final_report.md` (verdict, headline metrics, score
   breakdown, what worked / didn't, lesson, dead-ends if any, next iter).
9. Update `BASE_MEMORY.md` per prompt rules (entry, top-K refresh,
   directions update, frontmatter increments, auto-prune if > 18 KB).
