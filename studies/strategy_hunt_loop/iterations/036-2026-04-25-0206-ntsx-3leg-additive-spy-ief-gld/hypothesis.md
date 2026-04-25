# Iteration 036 — 3-leg additive static stack: SPY + IEF + GLD (1.8× lev)

## Hypothesis

Iter 015's static-stack mechanism (0.9 SPY + 0.6 IEF, 1.5× leverage)
captures cross-asset diversification between equity and bonds and
clears the +0.10 Sharpe edge cross-dataset. Iter 035 confirmed the
77-point ceiling is **architecture-bound, not bond-specific** by
substituting GLD for IEF at the same weights with near-identical
score (Sharpe 1.07 spy / 1.10 ndx, DSR worst-p 0.344 vs 0.548 — best
static-stack DSR ever, but still capped at 77). The open question
that closure of single-asset substitution leaves: do **two**
orthogonal diversifiers stacked **additively** (bonds keep iter 015's
0.6 weight; gold added as a third leg at 0.3) compound, saturate, or
regress relative to the 2-leg ceiling?

This iteration tests `eq_w=0.9, bd_w=0.6 (IEF), gld_w=0.3` — total
leverage 1.8× (a 0.3× uptick over iter 015's 1.5×). The architecture
pre-commits to **preserving iter 015 verbatim** on the equity+bond
sleeve and adding gold as a **parallel** diversifier (NOT a
substitution). Bond carry (term premium per Ilmanen ch.6) and gold
(real-yield-decline hedge per Erb-Harvey 2006, AMP 2013 cross-asset
orthogonality) are economically distinct return sources with
near-zero pairwise correlation — the additive stack tests whether
these two orthogonal sleeves compound risk-adjusted return or
saturate at the 77 ceiling because the marginal diversification
benefit per unit of added leverage shrinks.

Three pre-committed possible outcomes — score binning per BASE_MEMORY:

- **Score ≥ 80**: first ceiling break. Implies diversification
  compounds — directly motivates iter 037 to test 4-leg
  (SPY+IEF+GLD+commodity-broad or SPY+IEF+GLD+REIT) or 3-leg with
  larger gold weight.
- **Score ~77 (tied)**: the 77 ceiling is **leverage-bound** at
  Sharpe ~1.05-1.10 regardless of asset count. Closes 3-leg static
  ADDITIVE. Iter 037 must pivot to non-static (regime/ML/CS) or VRP
  basket extension (iter 026 architecture on multiple indices).
- **Score < 75 (regress)**: 1.8× leverage degrades the architecture
  via tail-risk concentration. Closes the entire "more leverage on
  static stack" path. Iter 037 must reduce to ≤1.5× and pivot to
  non-static or VRP.

## Primary citation

`[risk_parity, ch.5]` — multi-asset risk-parity decomposition;
risk-parity is a generalization of inverse-variance weighting to
N legs. The book covers 3+ leg stacks explicitly with bond-equity-
commodity baskets as canonical examples, and demonstrates that
adding orthogonal sleeves to a 2-leg base extends the efficient
frontier when pairwise correlations stay below ~0.30.

## Additional citations

- `[risk_parity, p.5, p.10-11, ch.1]` — Asness, Frazzini & Pedersen
  (2012). "Leverage Aversion and Risk Parity." *FAJ* 68(1): 47-59.
  SSRN 1728082. The static-stack mechanism (preserved from iter 015).
- `[risk_parity, p.80-84]` — funding-cost framework (preserved from
  iter 018 — gold leg has zero coupon, IEF has positive carry, so
  total funding cost still scales with total notional).
- `[leverage_for_the_long_run, p.19-20]` — Hsiao, Williams (2017).
  *J. Index Investing.* Leverage on a diversified base captures the
  full diversification benefit; 1.8× still well below the 2-3× regime
  where margin call probability dominates.
- `[advances_fin_ml, p.31-34]` — Lopez de Prado (2018). Cross-library
  parity (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (G2).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[volatility_trading, ch.10]` — gold's vol regime characteristics
  (background; not used as gating signal here).
- **Erb, C.B. & Harvey, C.R. (2006).** "The Strategic and Tactical
  Value of Commodity Futures." *FAJ* 62(2): 69-97. DOI
  10.2469/faj.v62.n2.4084. Gold's contango ~−1%/yr; commodity
  diversification benefit on a 60/40 base. Iter 035 cite preserved.
- **Asness, C.S., Moskowitz, T.J. & Pedersen, L.H. (2013).** "Value
  and Momentum Everywhere." *JF* 68(3): 929-985. DOI
  10.1111/jofi.12021. SSRN 1363476. Cross-asset orthogonality
  argument (gold ⊥ bonds and ⊥ equity at low correlation).
- **Koijen, R.S.J., Moskowitz, T.J., Pedersen, L.H. & Vrugt, E.B.
  (2018).** "Carry." *JFE* 127(2): 197-225. §3 — gold's spot-forward
  basis ≈ zero or slightly negative; bond carry term-premium decomposition.
- **Ilmanen (2011).** *Expected Returns.* Wiley. ch.6 (term premium),
  ch.10 (commodity premium magnitudes — gold's real-yield-decline
  hedge property).
- WisdomTree NTSX prospectus — 90/60 weights (preserved verbatim);
  this iter ADDS gold rather than substituting.

## Edge source

SPY 1x b&h misses the orthogonal diversification across **three**
asset classes simultaneously: equity (growth), bonds (term premium +
recession hedge), gold (inflation/currency-debasement hedge). At low
pairwise correlations ((+0.05 SPY-GLD, −0.27 SPY-IEF, near-zero
GLD-IEF on the spy_real window), the stacked portfolio's Sharpe
should exceed any 2-leg subset by a margin proportional to the
additional sleeve's variance contribution divided by total stack
variance — the AMP 2013 cross-asset additivity principle.

## Datasets

- **educational** (SPYSIM synth via TLT-aligned 24y window
  2002-07-26 → 2026-04-15): preserves iter 034's window so all 3-leg
  iters (034, 036) span identical bars. Tests the structural
  hypothesis on a longer window than spy_real, including the full
  2003-2007 commodity bull plus the 2013 gold crash.
- **spy_real** (2009-06-25 → 2026-04-15): post-GFC SPY+IEF+GLD; the
  primary real-data window matching iter 015 / iter 026 / iter 034 /
  iter 035 verbatim.
- **ndx_real** (2010-02-12 → 2026-04-15): tech-heavy QQQ + IEF + GLD;
  the dataset where iter 026 achieved 7/7 + DSR PASS (the only
  DSR-clearing benchmark in loop history); preserves the iter-stack
  comparison protocol.

## Kill criteria (pre-committed)

- **Kill A (Sharpe regress vs iter 015 by < −0.05 on ≥ 2 datasets)**:
  the 3-leg destroys the 2-leg edge → over-leveraged + tail-risk
  drag dominates. Closes the "more legs at higher leverage" path.
- **Kill B (ndx MDD > 45%)**: extra 0.3× leverage breaks tail-risk
  ceiling (iter 035's ndx margin was +3.17pp clear; iter 034's was
  −1.99pp breach). With gold added on top of bonds, cumulative
  stress windows compound.
- **Kill C (DSR worst-p > 0.20 across all 3 datasets)**: 77 ceiling
  holds and IS leverage-bound at Sharpe ~1.05-1.10 regardless of
  leg count. Closes 3-leg static ADDITIVE.
- **Kill D (G7 cross-lib ±3pp CAGR breach)**: engine bug in 3-leg
  primitive (iter 034 verified at 0.087pp; iter 036 should be
  similar since same simulator, different ticker).
- **Kill E (total score < 60, MARGINAL or worse)**: regress vs both
  iter 015 (77) and iter 035 (77) — implies leverage cost > diversification benefit.
- **Kill F (robustness < 7/9 sub-windows positive)**: instability
  from gold's regime-dependence (e.g., 2013 −30% taper tantrum,
  2022 −20% rate-hike).

## Expected budget

- Configs to test: **1** (single pre-committed cfg, NO grid, NO sweep)
- Wall-time: ~5-10 min (3 datasets × single 3-leg backtest, identical
  scope to iter 034 / iter 035; primary cost is gate evaluation)
- Files to create:
  - `synth_stacked_etf_3leg.py` — copy of iter 034's verbatim
    primitive (renamed semantically; the function is asset-agnostic)
  - `numpy_reference_stacked_3leg.py` — copy of iter 034's numpy
    reference for G7
  - `run_backtests.py` — adapted from iter 034 (only ticker
    + weight changes)
  - `compute_gates_and_score.py` — copy from iter 035 (templated)
  - `tests/test_iter036_3leg_additive_spy_ief_gld.py` — TDD spec
    with ≥3 unit tests (load, weights, leverage invariant)
  - `results.json` + `verdict.json` + `final_report.md`
  - `plot_vs_benchmark_spy_real.png` + `plot_vs_benchmark_ndx_real.png`

## Implementation plan

1. Vendor `synth_stacked_etf_3leg.py` and `numpy_reference_stacked_3leg.py`
   from iter 034 (asset-agnostic — function signature accepts any
   3 return streams).
2. Author `tests/test_iter036_3leg_additive_spy_ief_gld.py` first
   (TDD) — verify GLD parquet loads, the `0.9/0.6/0.3` weight set
   gives total leverage 1.8×, the apply function reduces to iter 015's
   2-leg case when `bd_long_w=0`.
3. Adapt `run_backtests.py` from iter 034: change ticker symbol
   `bond_long_symbol: TLT → GLD` and weights `(0.9, 0.4, 0.2) →
   (0.9, 0.6, 0.3)`. Pre-commit single cfg `ntsx_3leg_add_90_60_30_spy_ief_gld`.
4. Run backtests on all 3 datasets. Save `results.json` with the
   `returns_series` key the plot helper requires.
5. `compute_gates_and_score.py`: 7 gates per dataset (PBO at the
   degenerate single-config grid is set to 0.5 floor, since 1 cfg
   has no overfit — same convention as iter 015/034/035), DSR with
   `n_trials = 4294 + 1 = 4295`, WF/OOS/FWD/Bootstrap/G7 standard.
6. Score via `scoring.score_strategy` — output `verdict.json`.
7. Run `plot_helper.py --iter 036` to generate
   plots vs SPY/QQQ b&h. Verify both PNGs present.
8. Write `final_report.md` (verdict, headline metrics, score
   breakdown, what worked / didn't, lesson, dead-ends, next iter).
9. Update `BASE_MEMORY.md` per prompt rules (entry, top-K refresh,
   directions update, frontmatter increments).
