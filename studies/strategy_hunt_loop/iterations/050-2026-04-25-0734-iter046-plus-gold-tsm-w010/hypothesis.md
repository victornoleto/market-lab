# Iteration 050 — iter 046 + Gold TSM (90d) at Markowitz-optimum weight w_gold = 0.10

## Hypothesis

Iter 049 falsified the **50/50 additive 3rd-stream thesis** for any
component with Sharpe meaningfully below iter 046's combined Sharpe
(S_046 = 1.32 vs S_gold_tsm = 0.69). The iter 049 post-mortem derived
the closed-form Markowitz optimum weight on gold TSM under quadratic
utility:

    w*_gold = (S_a σ_b - ρ S_b σ_a) / (S_a σ_b + S_b σ_a - ρ (S_a σ_b + S_b σ_a))

Plugging the iter 049 measured values (S_a = 1.32, σ_a = 0.072,
S_b = 0.69, σ_b = 0.129, ρ = 0.53) yields **w*_gold ≈ 0.09** — i.e., the
Markowitz-optimum weight is roughly 9%, NOT 50%. Iter 049's hypothesis
was sound; only the **weight was mathematically wrong**.

**Iter 050 hypothesis**: at `w_gold = 0.10` (the Markowitz-rounded
optimum), the iter 046 + gold TSM combination should:

1. **Preserve iter 046's Sharpe within ≤ 0.05 dilution** on all 3 datasets
   (Markowitz-formula prediction at ρ = 0.53: combined Sharpe ≈ 1.29 vs
   iter 046's 1.32 — a 0.03 drop, well below the kill threshold).
2. **Keep DSR worst-p below iter 046's 0.044** (small Sharpe drop +
   n_trials += 1 should NOT push past the 0.05 gate).
3. **Slightly improve MDD** (gold TSM's cash exposure during gold
   bear markets contributes 1-2 pp tail-risk reduction even at w = 0.10).

The combination is a 90/10 convex combo of iter 046's saved combined
stream and gold TSM (90-day boolean trend filter on GLD, cash@rf=2%):

    r_combined[t] = 0.90 * r_046[t] + 0.10 * r_gold_tsm[t]

Single pre-committed cfg `iter046_plus_gold_tsm_w010_lookback90`. No
grid, no sweep. cumulative_n_trials advances by exactly 1
(4316 → 4317) — no Bonferroni cost (lesson from iter 047).

This iteration is the **direct mathematical follow-up** to iter 049's
Markowitz post-mortem and the **5th and likely final test** of the
iter 046-base enhancement axes (input-gate 044, weight-asymmetry 047,
output-leverage 048, additive-50/50 049, additive-low-weight 050).

## Primary citation

`[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials. Iter 049
demonstrated empirically that simultaneously dropping Sharpe AND
incrementing n_trials moves the deflated p across multiple buckets;
the converse — preserving Sharpe while incrementing n_trials by 1 —
should keep p comfortably below 0.05 if iter 046's anchor (raw p = 0.044
at n = 4311) survives the small dilution.

Markowitz, H. (1952), *Portfolio Selection*, JoF 7(1) 77-91 — convex-
combination Sharpe identity; the 1-of-2 risky asset weight optimum
under quadratic utility. The 0.10 weight is the rounded closed-form
optimum given iter 049's measured (S_a, S_b, σ_a, σ_b, ρ).

## Additional citations

- `[risk_parity, ch.5]` (Asness-Frazzini-Pedersen 2013, archived) —
  iter 046 base architecture preserved verbatim via saved return stream.
- `[volatility_trading, p.218]` (Sinclair 2013) — iter 046's iter 039
  sub-component preserved verbatim.
- `[systematic_trading]` (Carver) — generic time-series momentum rule;
  unchanged from iter 049.
- `[stocks_on_the_move, p.76-77]` (Clenow) — boolean trend on log price.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1).
- Web: Moskowitz-Ooi-Pedersen (2012), JFE 104(2) 228-250,
  DOI 10.1016/j.jfineco.2011.11.003 — single-asset commodity TSM
  documented at +3-4% alpha; informs gold TSM Sharpe expectation.
- Web: Markowitz (1952) — convex-combination Sharpe identity.

## Edge source

Same as iter 049: gold TSM contributes a positive-expected-return,
moderately-correlated stream (ρ ≈ 0.53 measured in iter 049) that
diversifies the iter 046 base's persistent equity exposure, with the
TSM filter avoiding gold's structural drawdowns (1996-2001, 2013-2018).

The structural difference vs iter 049 is **weight, not mechanism**: at
w = 0.10 vs 0.50, the combined Sharpe is dominated by iter 046 rather
than by the dilution average of two unequal-Sharpe streams. The
Markowitz formula predicts:

| ρ      | combined Sharpe (w_gold = 0.10) | combined Sharpe (w_gold = 0.50) |
|---|---|---|
| 0.00   | 1.32 (no dilution)               | 1.25 |
| 0.30   | 1.30                             | 1.16 |
| **0.53** | **1.29** (predicted observed)  | **1.03** (observed iter 049)|
| 0.70   | 1.28                             | 0.99 |

At w = 0.10, even high correlation only modestly reduces the combined
Sharpe (because the variance contribution of the small stream is small).
This is **the small-weight regime Markowitz predicted iter 049 should
have used.**

## Datasets

Identical to iter 049 to enable apples-to-apples comparison:

- **educational** — Tiingo SPY/GLD over `2006-01-03 → 2026-04-15` (the
  iter 046 saved stream's window). Custom benchmark = SPY b&h on this
  exact window (loaded from `data["benchmarks"]["educational"]`).
- **spy_real** (`2009-06-25 → 2026-04-15`) — bench SPY (Tiingo).
- **ndx_real** (`2010-02-12 → 2026-04-15`) — bench QQQ (Tiingo).

Iter 046's saved stream `iter039_on_iter041_50_50` is loaded verbatim
from `iterations/046-*/results.json` (avoiding re-running the iter 046
3-leg simulator). GLD prices loaded from
`data/tiingo/daily/prices/GLD.parquet`.

## Kill criteria (pre-committed)

| kill | rule | rationale |
|---|---|---|
| **A** Combined Sharpe drops by ≥ 0.10 vs iter 046 on ≥ 2 datasets | If even at w=0.10 the dilution is > 0.10, the additive thesis is dead at any weight — need a structurally different 3rd stream | predicts iter 050 doesn't escape iter 049's closure |
| **B** DSR worst-p ≥ 0.10 | Doubling iter 046's worst-p at small Sharpe drop indicates DSR sensitivity dominates the win | confirms iter 046's 85 anchor is on a knife-edge |
| **C** Score < 84 | Score regression of ≥ 1 pt vs iter 046 closes the additive-low-weight axis | mirrors iter 049 closure pattern |
| **D** Markowitz formula mispredicts observed Sharpe by ≥ 0.05 on ≥ 2 datasets | If empirical combined Sharpe disagrees with closed-form by > 0.05, the assumed (μ, σ, ρ) parameters are unstable across windows | validates the post-mortem mechanism |
| **E** G7 cross-lib > 3 pp | Engine bug (must use exact same pandas-vs-numpy methodology) | mandatory all iters |
| **F** MDD increase > 1 pp on ≥ 2 datasets | If adding gold TSM at w=0.10 *worsens* tail risk, the diversification claim fails | low-weight version of iter 049 kill F |

If 0/6 fire and score ≥ 86 → first iter 046+ improvement, additive-low-
weight axis OPEN for further refinement (e.g., w sweep at finer
granularity, or different low-weight 3rd stream).

If ≤ 1/6 fire and score = 85 (tied with iter 046) → confirms iter 046
is genuinely Pareto-optimal across all 5 enhancement axes; future
iterations must abandon iter 046 base.

If ≥ 3/6 fire → additive-low-weight axis CLOSED entirely; future iters
must abandon either the 50/50 symmetry, the gold TSM component, or the
iter 046 base.

## Expected budget

- Configs to test: **1** (single pre-committed cfg)
- Wall-time: ~25-30 min (smaller than iter 049 because gold_tsm.py and
  numpy reference are reused verbatim from iter 049)
- Files to create:
  - `gold_tsm.py` — symlink/copy of iter 049's
  - `numpy_reference_iter050.py` — pure-numpy reference for G7 parity
  - `combined_046_plus_gold.py` — convex combo loader (reused from 049)
  - `run_backtests.py` — driver with w_046=0.9, w_gold=0.10
  - `compute_gates_and_score.py` — gates + score + verdict.json + kill eval
  - `tests/test_iter_050_gold_tsm.py` — TDD specs (≥ 5 tests)

## Implementation plan

1. **Stage 3a (TDD)**: write `tests/test_iter_050_gold_tsm.py` with
   ≥ 5 tests:
   - **Reduction**: w_gold = 0 → combined === iter 046 stream (modulo
     date alignment).
   - **Reduction**: w_gold = 1.0 → combined === gold TSM stream alone.
   - **Linearity**: combined returns are exactly the convex combination
     `w_046 * r_046 + w_gold * r_gold` on the inner-join.
   - **Sign convention**: gold TSM 90d return-sign matches direct
     calculation on raw GLD prices.
   - **Cross-lib**: pandas implementation of gold TSM matches the
     pure-numpy reference to within 1e-9 per bar.
2. **Stage 3b**: copy `gold_tsm.py`, `numpy_reference_iter049.py` →
   `numpy_reference_iter050.py`, and `combined_046_plus_gold.py` from
   iter 049 verbatim. Verify tests pass.
3. **Stage 3c**: write `run_backtests.py` with CFG = w_046=0.9,
   w_gold=0.10, lookback=90, rf=0.02, cost_bps=5.0; load iter 046's
   saved stream + GLD prices; compute combined; save `results.json`
   with the standard schema (incl. `returns_series` for plotting,
   `subcomponent_returns` for diagnostics, `crosslib` for G7).
4. **Stage 3d**: write `compute_gates_and_score.py` running 7-gate
   battery + scoring + 6 pre-committed kill evaluations. Compute
   Markowitz formula prediction explicitly and compare to observed.
5. **Stage 4**: read `verdict.json`; if score ≥ 90 AND winner_conds met
   → set `status: winner` in BASE_MEMORY; else log STRONG/PROMISING.
6. **Stage 5**: write `final_report.md`, update BASE_MEMORY (append
   6-field entry to iteration log; auto-prune if file > 18KB),
   `verdict.json`, generate plots via `plot_helper.py`.

## Why this is structurally novel vs DEAD_ENDS

- **iter 049** closed "**50/50** weighting on additive iter 046 + lower-
  Sharpe stream". The closure is **specifically about w = 0.50**,
  derived from the Markowitz identity. iter 050 uses **w = 0.10** —
  the closed-form Markowitz optimum — which the iter 049 closure
  explicitly leaves OPEN ("OPEN: lower weight (5-20%) variants on the
  same gold TSM component" and "future picks must use w ≤ 0.20 OR find
  S_3rd-comparable stream with verified ρ < 0.30 OR abandon iter 046
  base").
- **iter 047** closed "weight asymmetry sweep on iter 046's 50/50 base".
  iter 047 swept weights w_041 ∈ {0.5, 0.65, 0.8} between iter 041 and
  iter 039 (the two existing components). iter 050 introduces a NEW
  third component (gold TSM); it does NOT sweep weights between iter 046's
  two existing components. Different parameter space.
- **iter 044/048** closed input-gate/output-leverage modulations of
  iter 046. iter 050 is **ADDITIVE** (new uncorrelated stream), not
  modulation — the path iter 048 closure recommended.
- iter 050 uses pre-committed N=1 cfg (no Bonferroni cost; lesson
  from iter 047).

The path forward post-iter-050 depends on the result:

- **Score = 85 ± 1**: iter 046 is Pareto-optimal across all enhancement
  axes. Future iters MUST abandon iter 046 base (e.g., go to iter 037
  base, or iter 026 + iter 037 50/50 with checked Sharpe parity, or
  totally different bases).
- **Score 86-88**: small additive lift confirmed; iter 051 can sweep
  w_gold ∈ {0.05, 0.15, 0.20} or test SLV TSM (silver, ρ ≈ 0.45 to
  iter 046) at w = 0.10.
- **Score < 84**: additive-low-weight axis closes entirely; future
  iters must abandon iter 046 base.

## Predicted outcomes

Markowitz formula prediction at w_gold = 0.10, ρ = 0.53:

    σ²_combined = 0.81 × 0.0052 + 0.01 × 0.0166 + 2 × 0.90 × 0.10 × 0.53 × 0.072 × 0.129
                = 0.00421 + 0.000166 + 0.000885
                = 0.00526
    σ_combined  = 0.0726
    μ_combined  = 0.90 × 0.094 + 0.10 × 0.089 = 0.0935
    Sharpe_predicted = 0.0935 / 0.0726 ≈ 1.288

Predicted measured per dataset (Markowitz, scaled to per-dataset
S_046 since iter 046's Sharpe varies 1.20-1.38 across datasets):

| dataset | iter 046 S | predicted iter 050 S (Δ) | benchmark + 0.10 | edge ✓ |
|---|---|---|---|---|
| educational | 1.20 | **1.18** (−0.02) | 0.78 | +0.40 ✓ |
| spy_real    | 1.32 | **1.29** (−0.03) | 1.00 | +0.29 ✓ |
| ndx_real    | 1.38 | **1.34** (−0.04) | 1.055 | +0.29 ✓ |

All 3 datasets predicted to clear Sharpe edge → c1 = 25/25.

DSR p prediction: at S = 1.18-1.34, n_trials = 4317, p should be
0.044-0.060 (just above iter 046's 0.044) — borderline 15 pts (worst-p
< 0.05) vs 10 pts (worst-p < 0.10). **DSR is the score-pivot uncertainty.**

CAGR prediction: gold TSM CAGR is 8.24-8.89% < iter 046's 9.16-9.76%, so
combined CAGR ≈ 0.9 × iter_046 + 0.1 × gold_tsm = ~9.07% / 9.39% / 9.63%
— still 0/3 floors → c4 = 0. (Same as iter 046.)

MDD prediction: small improvement (1-2 pp) from gold TSM's cash
exposure → still 3/3 ceilings → c5 = 15.

Gates prediction: 7/7 × 3 datasets (G1-G7 all preserved) → c2 = 25.

Robustness prediction: 9/9 sub-windows positive → +5 bonus.

**Predicted score: 85-90** (frozen bench). DSR pivot determines exact:
if p stays < 0.05 on all 3 → 90 (TIE iter 046 effectively, possibly
WINNER if all 5 strict conds hold). If p creeps to 0.06-0.10 on edu
(weakest of the 3) → 85 (TIE iter 046).

Key decision-relevant questions iter 050 answers:

1. **Is the Markowitz formula empirically reliable?** Predict combined
   Sharpe = 1.18/1.29/1.34; verify within ±0.05.
2. **Is iter 046's score 85 robust to small additive perturbations?**
   If iter 050 also scores 85, iter 046 is at a 5-axis stable maximum;
   future iters MUST abandon the base.
3. **Could the additive-low-weight axis still produce a winner?** Only
   if DSR p preservation pushes iter 050 to 90 with all 5 conds met
   (low probability given iter 046 was already 4/5).

If iter 050 scores 90+ AND winner conditions hold → first WINNER in
the loop. The mathematical case is plausible: iter 046 was 1 condition
shy (Sharpe edge ndx +0.42 ✓ at w=0.5; same here but with 0.04 drop
still leaves +0.38 above 0.10 threshold). The CAGR floor was the
binding constraint, and iter 050 doesn't fix that. So most likely
outcome is **STRONG 85-87, NOT winner** — and the value is in
**closing the 5th and final iter 046 enhancement axis**, forcing
iter 051+ to pivot.
