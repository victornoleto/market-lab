# Iteration 047 — Weight sweep on iter 046 base (CAGR-vs-DSR Pareto frontier)

## Hypothesis

iter 046 (50/50 convex combo of iter 041 regime stack + iter 039 VRP basket)
scored 85/100 STRONG and is the new TOP-K #1, with 7/7×3 gates and DSR
sub-0.05×3 — the cleanest robustness profile in the loop. The single
remaining 5-pt gap to a hypothetical 90+ WINNER tier is on **CAGR floor
0/15** (frozen benchmarks): edu 9.16% vs 9.18% floor (under by 0.02pp,
razor-thin), spy 9.45% vs 11.98% (−2.5pp), ndx 9.76% vs 15.35% (−5.6pp).

The CAGR shortfall arises because a 50/50 convex combo arithmetic-averages
component CAGRs: iter 041 ≈ 13% CAGR, iter 039 ≈ 5-6% CAGR ⇒ combo ≈ 9-10%.
**Shifting weight toward the higher-CAGR component (iter 041) recovers
combined CAGR linearly**, but at the cost of variance-reduction
(iter 046's ρ=0.41 corr benefit shrinks as one component dominates) and
therefore at the cost of DSR p-value `[advances_fin_ml, p.222-223]`.

The edge hypothesis: **a small pre-committed 3-point weight grid spans
the CAGR-vs-DSR Pareto frontier between iter 046 (50/50) and iter 041
(100/0), revealing whether a Pareto-optimal point exists that retains
DSR < 0.05 (1/15→15/15) while clearing at least 1 CAGR floor (0/15→5/15)**.
If found, the Pareto-optimal cfg scores ≥ 85 (matching iter 046) and
plausibly higher; if not, the negative result rigorously closes the
"weight asymmetry" axis listed open in `BASE_MEMORY.md`.

The grid is `(w_041 ∈ {0.50, 0.65, 0.80}, w_039 = 1 − w_041)`. Three
configurations × three datasets = 9 evaluations, with Bonferroni
adjustment α' = α/3 ≈ 0.0167 applied to the DSR significance threshold.
N=3 also makes G1 PBO actually computable (iter 046's N=1 was vacuous),
adding a real overfit gate.

## Primary citation

`[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack with
regime-conditional weight tilts (iter 041 base architecture).

## Additional citations

- `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP harvesting
  (iter 039 basket architecture).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV; with N=3 the computation
  becomes meaningful (vs iter 046's vacuous N=1).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials and
  diversification penalty; honest accounting requires Bonferroni
  adjustment for the 3-cfg pre-committed grid.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.162-164]` — no-lookahead lag rule (VIX[t-1] for
  iter 041 regime gate).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- Markowitz (1952), JoF 7(1) 77-91 — convex-combination minimum-variance
  weight is at the inverse-variance ratio; sweeping AWAY from that
  optimum trades variance for higher expected return (Pareto frontier).
- Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098 — VIX as
  ex-ante risk regime indicator (iter 041 regime gate).
- Bondarenko (2014), QJF 4(3) 1450015 — empirical SPX VRP magnitude
  (iter 039 income source).
- Carr-Wu (2009), RFS 22(3) 1311-1341 — variance risk premia framework.
- Erb-Harvey (2006), FAJ 62(2), DOI 10.2469/faj.v62.n2.4084 — gold's
  strategic role in iter 041's stress sleeve.
- Asness-Moskowitz-Pedersen (2013), JoF 68(3) 929-985 — diversification
  premium across asset classes.
- Bonferroni, C. E. (1936), Pubblicazioni del R. Istituto Superiore di
  Scienze Economiche e Commerciali di Firenze 8, 3-62 — closed
  multiple-testing correction; α' = α/k for k pre-committed hypotheses.

## Edge source

iter 046 50/50 collects max diversification benefit (corr 0.41 →
DSR 0.041) but **arithmetically averages CAGR** to ~9-10%, missing 2-3
of the 3 frozen CAGR floors. Sweeping weight toward iter 041 (higher
CAGR) recovers CAGR linearly (≈ +0.65pp per 10pp shift) at the cost of
DSR (variance-reduction shrinks ⇒ Sharpe drops slightly ⇒ deflated
p-value rises). The Pareto-optimal cfg between these extremes — if one
exists — clears more CAGR floor pixels without losing the DSR-PASS
status, lifting overall score above 85.

## Datasets

- **educational** (SPY+IEF+GLD stack 2006-2026): 20y combined window
  matching iter 046's GLD-aligned start (2006-01-03). Tests whether the
  20y synth dataset's CAGR floor (frozen 9.18%, just barely missed by
  iter 046's 9.16%) flips to PASS at 65/35 or 80/20.
- **spy_real** (2009-06-25 → 2026-04-15): 17y post-GFC; CAGR floor
  11.98%, missed by 2.5pp at 50/50. 65/35 projects ≈ 10.6% (still
  short); 80/20 projects ≈ 11.9% (within 0.1pp — edge case).
- **ndx_real** (2010-02-12 → 2026-04-15): 16y; benchmark QQQ has the
  highest CAGR (19.18% → floor 15.35%). Even iter 041 alone (13%) is
  below floor; the ndx CAGR floor is structurally unreachable from
  iter 041+iter 039 components. Honest reporting required.

## Kill criteria (pre-committed)

If ANY of these fires, the iter 047 hypothesis is falsified or the
weight axis is closed:

| kill | trigger | interpretation |
|---|---|---|
| **A** Top-cfg score < iter 046's 85 (frozen) | best of 3 cfgs scores < 85 | weight axis ENTIRELY DOMINATED by 50/50 (iter 046 is Pareto-optimum); weight asymmetry CLOSED |
| **B** All 3 cfgs fail Bonferroni-adjusted DSR (worst-p ≥ α' = 0.0167) on ≥ 2 datasets | each cfg's worst-p across 3 ds ≥ 0.0167 on 2/3 ds | the 3-cfg grid pre-commitment cost is too high; multiple-testing penalty erases the iter 046 edge — closes weight sweep family with Bonferroni |
| **C** PBO grid-level ≥ 0.5 on ≥ 1 dataset | CSCV PBO over 3 cfgs is high | weight grid is itself overfit; iter 046's vacuous-PBO success was specific to N=1 |
| **D** Sharpe of best cfg drops by ≥ 0.10 vs iter 046 50/50 on ≥ 2 datasets | best of 3 cfgs has Sharpe Δ ≤ −0.10 vs iter 046 | variance reduction was the load-bearing mechanism; weight asymmetry destroys it before recovering CAGR |
| **E** G7 cross-lib > 3pp on any cfg | numpy ref ≢ pandas | engine bug; abort and fix before reporting |
| **F** Best cfg's CAGR floor count < iter 046's 0/3 with custom-bench | best cfg passes 0 CAGR floors | weight sweep can't recover even the easiest floor; CAGR axis is uncrosseable |

Pre-committed grid (no post-hoc selection):

```python
SWEEP_CFGS = [
    {"cfg_id": "iter046_w50_50", "w_041": 0.50, "w_039": 0.50},  # baseline = iter 046
    {"cfg_id": "iter046_w65_35", "w_041": 0.65, "w_039": 0.35},  # mid Pareto
    {"cfg_id": "iter046_w80_20", "w_041": 0.80, "w_039": 0.20},  # iter 041-leaning Pareto
]
```

All other iter 041 + iter 039 sub-strategy params VERBATIM from iter 046:
calm `{0.70/0.40/0.40}` ↔ stress `{0.30/0.55/0.55}` at threshold 20.0;
1/3 SPY+QQQ+IWM 5/10 OTM put credit spread, 21d DTE, harvest_notional=1.0.

## Expected budget

- Configs to test: **3** (pre-committed)
- Datasets: 3 (educational + spy_real + ndx_real)
- Wall-time: ~25 minutes (each cfg is ~5 min on 3 datasets; engine reused
  from iter 046 with the parametric `w_041`/`w_039` already exposed)
- Files to create: 4
  - `run_backtests.py` (loops the 3 cfgs, writes results.json)
  - `compute_gates_and_score.py` (PBO/DSR/Bonferroni/score per cfg)
  - `tests/test_iter_047_weight_sweep.py` (TDD: reductions + monotonicity)
  - (`combined_041_039_engine.py` REUSED from iter 046 — no new engine)

## Implementation plan

1. **Reuse iter 046 engine verbatim**: import `compute_combined_returns`
   from `iterations/046-*/combined_041_039.py` and
   `compute_combined_returns_np` from
   `iterations/046-*/numpy_reference_combined_046.py`. Both already
   accept `w_041`/`w_039` parameters; no engine modification needed.
2. **`run_backtests.py`** — loop the 3 cfgs × 3 datasets, call the
   reused engine, write `results.json` with per-cfg metrics + per-cfg
   `returns_series` (top cfg per dataset gets the canonical key).
3. **`compute_gates_and_score.py`**:
   - Compute G1 PBO via CSCV across the 3 cfgs (real PBO with N=3,
     not vacuous like iter 046).
   - G2 DSR with **Bonferroni**: pass threshold = `0.05/3 = 0.01667`
     applied to each cfg's worst-p. Document raw p-values too.
   - G3-G7 per cfg as in iter 046.
   - Score each cfg with `scoring.score_strategy(...)`.
   - Pick the **highest-scoring** cfg as the iter 047 reportable
     (NOT post-hoc selection — pre-commit is on the grid, not on which
     cfg "wins").
4. **TDD specs** (`tests/test_iter_047_weight_sweep.py`):
   - `test_w041_zero_reduces_to_iter039`: `w_041=0` ⇒ combined ≡ iter 039.
   - `test_w039_zero_reduces_to_iter041`: `w_039=0` ⇒ combined ≡ iter 041.
   - `test_50_50_matches_iter_046_baseline`: cfg A produces iter 046's
     headline numbers ±0.005 Sharpe (engine-equivalence sanity).
   - `test_cagr_monotone_in_w041`: combined CAGR is non-decreasing in
     `w_041` on each dataset (mathematical property of convex combo
     when CAGR_041 ≥ CAGR_039 — true on all 3).
   - `test_bonferroni_threshold_constant`: `BONFERRONI_ALPHA == 0.05/3`.
5. **Final report** with honest score per cfg + Pareto frontier table +
   verdict on Pareto-optimum existence.
6. **Update `BASE_MEMORY.md`**: cumulative_n_trials 4311 → 4314 (+3
   cfgs); update top-K with iter 047 best cfg (if score ≥ 79); add
   weight-sweep finding to structural dead-ends section if axis closes;
   keep open if Pareto-optimum found.

## Why this is structurally NEW vs DEAD_ENDS

This is the explicitly recommended #1 direction in `BASE_MEMORY.md` and
iter 046's `final_report.md`. It does **not** match any closed dead-end:

- **iter 042 (combined-regime-lev-weights)** modified iter 041's
  internal weight asymmetry on the iter 041 leg ALONE — DSR regressed.
  That was *intra-component* perturbation. iter 047 is *cross-component*
  weight sweep on a 2-component composite — qualitatively different.
- **iter 043 (hysteretic-vix-regime-weights)** modified iter 041's
  regime-CROSSING frequency — this is gate timing, not composition
  weight.
- **iter 044 (multifeature-regime-vix-t10y3m)** added a 2nd regime
  feature to iter 041's gate — this is feature space, not weight.
- **iter 042/043/044 collectively closed "gate enrichment on iter 041"**;
  iter 047 is "convex-combo weight sweep" — a Markowitz-type sensitivity
  on a 2-stream composite, distinct family.

The structurally novel mechanism: **probe whether the Pareto-optimum on
the (variance, mean) plane between two positive-Sharpe streams exists
strictly between the inverse-variance optimum (≈ 89.5% iter 039) and
the high-CAGR extreme (100% iter 041)**. iter 046's 50/50 is one point
on that frontier; iter 047 maps two more.

## Expected outcome (linear projection from iter 046 sub-component data)

Using iter 046's measured component CAGRs and Sharpes to project:

| cfg | edu CAGR (proj) | spy CAGR (proj) | ndx CAGR (proj) | est. Sharpe spy | est. floors passed |
|---|---|---|---|---|---|
| 50/50 (iter 046 baseline) | 9.16% (msd) | 9.45% (msd) | 9.76% (msd) | 1.32 (msd) | 0/3 frozen |
| 65/35 | 10.23% | 10.62% | 10.65% | ~1.28 | 1/3 (edu) |
| 80/20 | 11.42% | 11.86% | 11.64% | ~1.21 | 1/3 (edu); spy 0.1pp short |

Spy CAGR floor (11.98%) is the prize; ndx (15.35%) is unreachable from
this component pair. Best realistic cfg-A outcome: 1-2 floors passed +
DSR holds → score 90 (WINNER tier-eligible — but cond #4 needs ≥ 2/3
floors so spy must clear). Most likely: 80/20 lands at edu floor PASS
(11.42% > 9.18%) but spy MARGINAL FAIL (11.86% vs 11.98%); DSR drops
into 0.05-0.10 range with Bonferroni penalty pushing all cfgs into
"raw p < 0.05 but adjusted p > 0.0167" zone → DSR scoring 10/15 instead
of 15/15. **Expected best cfg score ≈ 85-90**, with the higher end
contingent on whether spy CAGR clears at 80/20.

## Why bother running if linear projections suggest a wash

Two reasons:

1. **Component variance reduction is non-linear**: Markowitz σ²(w) is
   quadratic in w, with a minimum at the inverse-variance optimum. The
   ACTUAL Sharpe at w_041 = 0.65 may differ from the linear projection
   by 0.05+ in either direction depending on the precise empirical
   covariance — only measurement decides. iter 046's expected envelope
   was 1.36 vs measured 1.32 (0.04 gap), but the measured advantage
   over iter 045 was +0.04 Sharpe vs envelope-predicted parity.
2. **Closing the weight axis is itself valuable**: a NEAR_FAIL or
   FAIL on the entire 3-cfg grid would rigorously close one of the
   three OPEN axes from iter 046's report (weight sweep / 3-leg /
   output-leverage gate), focusing iter 048+ on the remaining two.
   This has scientific value independent of finding a winner.

## Connection to mandate §1

This iteration produces a CANDIDATE strategy at most. Mandate §1
remains MAINTENANCE 100% Plano C; even a hypothetical 90+ WINNER at
iter 047 would still require mandate §7 override per the loop's
operating rules. iter 047's role is purely scientific — map the
CAGR-vs-DSR Pareto frontier of an out-of-family composite.
