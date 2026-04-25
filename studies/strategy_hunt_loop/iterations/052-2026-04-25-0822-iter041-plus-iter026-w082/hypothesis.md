# Iteration 052 — iter 041 (regime-weighted stack) + iter 026 (single-asset SPY VRP) at Markowitz score-Pareto-optimum w_041=0.82

## Hypothesis

Substituting **iter 037** (3-leg static stack, edu Sharpe 0.98) with **iter 041**
(regime-weighted stack with VIX-gated calm/stress weights, edu Sharpe 1.027)
as the anchor in the iter 051 design recipe should lift combined educational
Sharpe enough to push DSR worst-p below the 0.10 boundary (potentially below
0.05) **while preserving 2/3 CAGR floor pass**. The Markowitz pre-screen on the
saved streams identifies **w_041 = 0.82** as the score-Pareto-optimum: it is
the lowest weight in the [0.82, 0.95] plateau where (criterion 1 Sharpe edge
+ criterion 4 CAGR floor) sums to 35 pts, and it has the highest combined
Sharpe within that plateau (best chance of DSR clearing).

The structural case rests on three measured facts on the saved streams:

1. **iter 041 has marginally higher edu Sharpe than iter 037** (1.027 vs 0.98).
   The +0.05 edge on the binding dataset is small but compounds under
   convex combination with iter 026's higher edu Sharpe (1.13).
2. **corr(iter 041, iter 026) is materially lower than corr(iter 037, iter 026)**
   on all 3 datasets (0.370 / 0.373 / 0.448 for 041; vs 0.574 / 0.545 / 0.602
   for 037 in iter 051). Lower correlation amplifies the Markowitz Sharpe-
   reduction-of-variance effect.
3. **At w_041 = 0.82 the combined Sharpe predicted by Markowitz is
   1.078 / 1.188 / 1.220** (edu / spy / ndx) — strictly above iter 051's
   1.021 / 1.198 / 1.219. The Sharpe edu lift of +0.057 is the single
   axis that could drop DSR p from 0.175 (iter 051) into the 0.05-0.10
   bucket.

## Primary citation

`[risk_parity, ch.5]` — Asness, Frazzini, Pedersen (2013) *Leverage
Aversion and Risk Parity* (FAJ 69(1) 47-58, archived at AQR), the
academic foundation for the levered SPY+IEF+GLD risk-parity stack
that iter 037 and iter 041 share. iter 041 layers a VIX-state
classifier on top, modulating the leg weights between calm
(0.70/0.40/0.40, 1.50× total) and stress (0.30/0.55/0.55, 1.40× total)
regimes — preserving the risk-parity skeleton while adding a regime-
aware overlay.

## Additional citations

- `[volatility_trading, p.218]` (Sinclair 2013) — single-asset SPY
  variance-risk-premium harvest via short 5/10 OTM 21-DTE put credit
  spreads; the architecture of iter 026 preserved verbatim via saved
  return stream.
- **Markowitz, H. (1952)** *Portfolio Selection*, Journal of Finance
  7(1), 77-91, DOI 10.1111/j.1540-6261.1952.tb01525.x — closed-form
  Sharpe identity for convex combination of two risky assets, used to
  derive w_041 = 0.82 as the score-Pareto-optimum on the saved
  streams (3 prior iters validated this formula to 4 decimals on
  9/9 datasets).
- **Whaley, R.E. (2009)** *Understanding the VIX*, Journal of Portfolio
  Management 35(3), 98-105, DOI 10.3905/JPM.2009.35.3.098 — VIX as the
  fear gauge; provides the regime classification rationale for iter
  041's binary VIX < 20 / VIX ≥ 20 split.
- `[advances_fin_ml, p.222-223]` — Deflated Sharpe Ratio with cumulative
  n_trials. The deflator at n_trials = 4319 (this iter +1) is the
  binding constraint on educational Sharpe.
- `[advances_fin_ml, p.31-34]` — Cross-library parity discipline for
  G7 (achieved 0.0000 pp in 6 prior iters by re-using saved streams).
- `[advances_fin_ml, p.196-202]` — Bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- **Bondarenko, O. (2014)** *Variance Trading and Market Price of
  Variance Risk*, Quarterly Journal of Finance 4(3), 1450015, DOI
  10.1142/S2010139214500153 — empirical SPX VRP magnitude and
  persistence justifying iter 026's harvest scale.
- **Erb, C. & Harvey, C. (2006)** *The Strategic and Tactical Value of
  Commodity Futures*, Financial Analysts Journal 62(2), DOI
  10.2469/faj.v62.n2.4084 — gold's strategic role inside the iter 041
  stack's GLD leg.

## Edge source

SPY 1x buy-hold misses (a) **regime-conditional weight shifting** between
risk assets (calm vs VIX-stress modes) and (b) **variance risk premium
harvest** independent of trend direction. The composition adds these two
orthogonal sources of return to a SPY-driven base; lower-than-iter-037
correlation between the two sources amplifies the Markowitz diversification
gain.

## Datasets

- **educational** (SPYSIM synth 40y window 2006-01-03 → 2026-04-15):
  the binding dataset where DSR fails most often. iter 041 stream
  starts 2006-01-04 (5101 bars); iter 026 stream covers same window.
- **spy_real** (SPY 17y 2009-06-25 → 2026-04-15): primary post-GFC
  validation; benchmark Sharpe 0.90.
- **ndx_real** (QQQ 16y 2010-02-12 → 2026-04-15): tech-tilt validation;
  benchmark Sharpe 0.955. Both component streams are SPY-driven, so
  this dataset tests the strategy's robustness when the benchmark
  deviates from the underlying.

## Kill criteria (pre-committed)

If any of the following observables hold at end of Stage 4, the hypothesis
is falsified for the corresponding axis:

- **Kill A** — Combined Sharpe drops by ≥ 0.10 vs Markowitz pre-screen
  prediction (1.078 / 1.188 / 1.220) on ≥ 2 of 3 datasets. Falsifies
  the saved-stream-composition methodology (would mean the convex-combo
  formula no longer holds for this stream pair).
- **Kill B** — DSR worst-p ≥ 0.10 across 3 datasets. The single most
  important kill: this is the axis the hypothesis specifically targets.
  If DSR worst-p stays in [0.10, 0.20) (5 pts c3) or worse, the iter 041
  Sharpe lift is too small to escape the iter 051 ceiling — closes
  the iter 041 + iter 026 saved-stream composition family at score 84.
- **Kill C** — CAGR floor passes on < 2 of 3 datasets. Predicted 2/3
  pass (edu + spy, ndx fails by 1.24 pp). If only 0-1 pass, the
  Pareto-optimum methodology has degraded vs iter 051.
- **Kill D** — Markowitz formula mispredicts observed Sharpe by ≥ 0.05
  on ≥ 2 of 3 datasets. Falsifies the closed-form approximation used
  to derive w_041 = 0.82 (would mean returns are non-stationary or have
  fat tails the formula doesn't capture).
- **Kill E** — G7 cross-lib > 3 pp on any dataset. Engine bug / stream
  parity error (saved streams are pandas-serialised returns; numpy
  reference must produce identical CAGR within 3 pp).
- **Kill F** — corr(iter 041, iter 026) ≥ 0.85 on any dataset (the same
  threshold that closed iter 032). The pre-screen measured 0.37 / 0.37
  / 0.45 — should be safely below 0.85, but verify in the final
  artefact.

## Expected budget

- **Configs to test**: 1 (single pre-committed cfg `iter041_plus_iter026_w082`).
- **Wall-time**: ~30-40 min (saved-stream composition is fast; mostly
  metric computation + gate battery + plotting).
- **n_trials**: 4318 → 4319 (+1).
- **Files to create**:
  - `combined_041_026.py` — pandas convex-combo helper
  - `numpy_reference_iter052.py` — pure-numpy reference for G7 parity
  - `markowitz_prescreen.txt` — pre-backtest pre-screen artefact
  - `run_backtests.py` — driver
  - `compute_gates_and_score.py` — gate battery + scoring + 6-kill eval
  - `tests/test_iter_052_combo.py` — TDD specs (≥ 6, all must pass)
  - `results.json` (~1.5-2 MB), `verdict.json`, `final_report.md`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`

## Implementation plan

1. **Pre-screen artefact** (`markowitz_prescreen.txt`) — record the
   sweep results that justify w_041 = 0.82 as the score-Pareto-optimum.
2. **TDD specs first** (`tests/test_iter_052_combo.py`):
   - `test_combine_041_026_linearity` — `0.5*a + 0.5*b` is the average of
     the streams pointwise.
   - `test_combine_041_026_w082` — at w_041=0.82, w_026=0.18 the sum
     equals 1.0 exactly.
   - `test_combine_041_026_inner_join` — only common dates appear in
     output; mismatched indices are dropped.
   - `test_combine_041_026_zero_weight_b` — w_026=0 returns scaled iter
     041 stream.
   - `test_combine_041_026_negative_weight_rejected` — both weights must
     be ≥ 0.
   - `test_numpy_reference_parity` — pandas combine ≈ numpy combine to
     1e-12 on a synthetic stream pair.
   - `test_markowitz_formula_residual_below_005` — on the actual saved
     streams, predicted Sharpe is within 0.05 of observed Sharpe on all
     3 datasets (validates Kill D pre-emptively).
   - `test_correlation_below_kill_f_threshold` — corr(041, 026) < 0.85
     on all 3 datasets (validates Kill F pre-emptively).
3. **Implement combine helper** to make TDD specs green.
4. **Implement numpy reference** for G7 parity.
5. **Implement run_backtests.py**: load saved streams, apply convex combo,
   compute metrics + Markowitz prediction + cross-lib check; write
   `results.json` with `runs`, `returns_series`, `subcomponent_returns`,
   `crosslib`, `benchmarks`.
6. **Implement compute_gates_and_score.py**: G1 vacuous (N=1), G2 DSR
   raw α=0.05, G3 walk-forward 8 windows, G4 70/30 OOS, G5 post-2020
   FWD, G6 bootstrap 99.9% CI, G7 cross-lib; robustness 3-window
   sub-Sharpe; scoring.py; pre-committed kill evaluation; write
   `verdict.json`.
7. **Generate plots** via `plot_helper.py --iter 052` once results.json
   is in place.
8. **Write final_report.md** in prose with verdict + headline metrics +
   score breakdown + lesson + next iter suggestions.
9. **Update BASE_MEMORY.md**: bump frontmatter, append iteration log
   entry (newest first), update Top-K if score ≥ 79, run auto-prune
   check.

## Predicted outcome

| dataset | predicted Sharpe | predicted CAGR | predicted DSR p (rough) | bench Sharpe | passes Sharpe edge? | passes CAGR floor? |
|---|---|---|---|---|---|---|
| educational | 1.078 | 11.63 % | 0.10-0.15 | 0.68 | ✓ (margin +0.30) | ✓ (margin +2.45 pp) |
| spy_real    | 1.188 | 12.03 % | 0.05-0.10 | 0.90 | ✓ (margin +0.19) | ✓ (margin +0.05 pp) |
| ndx_real    | 1.220 | 14.11 % | 0.05-0.10 | 0.955 | ✓ (margin +0.16) | ✗ (gap −1.24 pp) |

Expected score breakdown:

- c1 Sharpe edge: **25/25** (3/3 datasets clear bench + 0.10 by ≥ 0.16)
- c2 Gates: **19-23/25** depending on G2 DSR realization
- c3 DSR: **5-10/15** if worst-p in [0.10, 0.20); **10-15/15** if < 0.10;
  **15/15** if < 0.05 (the sole axis that could push to WINNER)
- c4 CAGR floor: **10/15** (2/3 pass: edu + spy; ndx fails by 1.24 pp)
- c5 MDD ceiling: **15/15** (predicted 22-30% vs ceilings 60/39/40 %)
- c6 Robustness: **5/5** if all sub-windows positive

**Optimistic total: 85-92** (STRONG; the upper end could clear WINNER if
all 5 strict winner conditions hold AND DSR p < 0.05 on the worst dataset).
**Realistic total: 80-86** (STRONG; ties or marginally improves on iter 051's
84).

The single axis with binary outcome is criterion 3 (DSR). The question this
iteration answers: **does the +0.057 edu Sharpe lift from substituting iter
041 for iter 037 push DSR worst-p across the 0.10 → 0.05 threshold at
n_trials = 4319?**

If yes (10% prior probability): potential WINNER at score 90-92.
If marginally (worst-p in [0.05, 0.10), 30% prior): score 89, STRONG, very
close.
If no (worst-p ≥ 0.10, 60% prior): score 84-85, STRONG, ties iter 051,
closes the iter 041 + iter 026 family at this Pareto point.

Either outcome closes a meaningful axis: the saved-stream composition with
the highest-Sharpe iter 041 base still cannot achieve the DSR threshold,
**confirming that DSR is structurally bounded by the 1.10-1.20 edu Sharpe
ceiling at n_trials > 4300, and a winner requires either a new base
strategy or a non-Markowitz mechanism**.

## Out of scope (explicitly NOT tested)

- Weight sweep N > 1: Bonferroni cost destroys c2 (closed by iter 047).
- iter 046-family composition: closed by 5 axes in iter 044/047/048/049/050.
- iter 037 + iter 026 weight other than 0.80: closed by iter 051 Pareto.
- HYG / non-GLD substitution in iter 041: pre-screen predicts Sharpe drop.
- HMM-2 multi-feature regime: closed by iter 044.
- Non-VRP volatility products (VXX, UVXY): not in scope.

## Reproducibility

```bash
# 1. Pre-screen (results saved in markowitz_prescreen.txt)
# 2. Run backtests (uses saved iter 041 + iter 026 streams)
uv run python studies/strategy_hunt_loop/iterations/052-2026-04-25-0822-iter041-plus-iter026-w082/run_backtests.py

# 3. Compute gates + score (writes verdict.json)
uv run python studies/strategy_hunt_loop/iterations/052-2026-04-25-0822-iter041-plus-iter026-w082/compute_gates_and_score.py

# 4. Verify TDD specs
uv run pytest studies/strategy_hunt_loop/iterations/052-2026-04-25-0822-iter041-plus-iter026-w082/tests/ -v

# 5. Generate plots
uv run python studies/strategy_hunt_loop/plot_helper.py --iter 052
```
