# Iteration 076 — iter 064 + LEVERED GLD/TLT trend sleeve ensemble (CAGR-floor mechanical-fix attempt)

## Hypothesis

Iter 075 closed at **81 STRONG / 4-of-5 winner conds met, CAGR-floor sole
gap**: GLD/TLT trend sleeve at unlevered `target_vol = 0.10` had ρ(064,
sleeve) = 0.241 spy ✅ (3.4× lower than iter 074's 0.81) but standalone
sleeve CAGR was only 3.28 / 2.78 / 2.33% on edu/spy/ndx — too low to lift
the combined CAGR past the strict-winner floors 9.18 / 11.98 / 15.35%.

The mechanical iter-075 lesson predicted that **scaling the sleeve's
target vol up by 2.5–3× (~10% → 25-30%) would lift its standalone CAGR
proportionally** (since Sharpe stays ~0.5 in the leverage-invariant
limit), pushing combined CAGR over the spy_real 11.98% floor and
unlocking the 5th strict winner condition.

This iteration tests that prediction directly with **honest borrow-cost
modeling**. The pre-committed math says the Sharpe-of-sleeve will
collapse from ~0.50 toward ~0.20 once borrow drag is paid, and combined
Sharpe will REGRESS vs iter 064's 1.33 spy. If this kill (KILL C) fires,
the "leverage is the CAGR-floor fix" axis is closed for the entire
iter-064-anchored ensemble family. If, against expectation, leverage
clears Sharpe regression AND clears CAGR floor simultaneously, iter 076
is a 🏆 WINNER candidate.

The hypothesis is therefore a **pre-committed leverage-mechanism
falsification attempt**, with the secondary value of producing a clean
0-borrow / futures-borrow / retail-borrow trichotomy on the same 4×5
weight × vol grid.

## Primary citation

`[leverage_for_the_long_run, ch.5]` — Hsiao-Williams 2017 NTSX-style
analysis of futures-implied financing achieving leverage at T-bill +
30-50bps vs retail Reg-T (T-bill + 150bps) and the resulting
Sharpe-impact of the borrow cost on a Sharpe-0.5-class trend strategy.
The chapter directly informs the "Sharpe-of-leverage = Sharpe -
(lev-1)·spread/σ" identity that drives iter 076's pre-committed kill.

## Additional citations

- **Faber, M.** (2007). "A Quantitative Approach to Tactical Asset
  Allocation." SSRN 962461. — Inherited from iter 075: SMA-200 long-only
  trend filter on multi-asset basket.
- **Frazzini, A., & Pedersen, L. H.** (2014). "Betting Against Beta."
  *Journal of Financial Economics* 111(1), 1-25.
  DOI 10.1016/j.jfineco.2013.10.005 — borrow-frictions on levered
  low-vol strategies. Cited in iter 056/060 as the empirical anchor for
  ETF-margin-spread modeling. Iter 076 applies the same primitive at
  the sleeve-leg level rather than at the post-stream level.
- `[stocks_on_the_move, p.81]` — Inherited from iter 075: trend lookback
  rationale.
- `[risk_parity, ch.5]` — Asness, Frazzini, Pedersen (2012) FAJ 68(1).
  Risk-parity-style equal-weighting of GLD+TLT sleeve legs and the
  documented levered-decorrelation-benefit theory; iter 076 applies
  leverage as a mechanical CAGR scaler on already-risk-parity-balanced
  legs.
- **Erb, C., & Harvey, C.** (2006). FAJ 62(2). Inherited from iter 075.
  DOI 10.2469/faj.v62.i2.4084.
- **Markowitz, H.** (1952). JoF 7(1). Inherited from iter 075/074.
  DOI 10.1111/j.1540-6261.1952.tb01525.x.
- **Sinclair, E.** (2013). `[volatility_trading, p.218]` — inverse-vol
  sizing primitive (now applied at higher target_vol with leg_cap=3.0).
- `[advances_fin_ml, p.222-223]` — DSR with per-iter `n_trials = 20`
  (v2 convention).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (numpy reference).
- `[advances_fin_ml, p.208-211]` — PBO via CSCV.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).

## Edge source

What does SPY 1× miss that this captures? **Same as iter 075** —
cross-asset diversification benefit from a non-equity, non-SPY-co-
exposed 2nd leg. Iter 076 changes ONLY the leg's vol-target (and
borrow-cost honest modeling), preserving the Faber-trend mechanism and
GLD/TLT asset choice. The SPY-1× edge axis is still
"cross-asset diversification at low ρ"; iter 076 augments it with
"+ proportional CAGR scaling via leverage to clear the strict-winner
CAGR floor."

## Datasets

Identical to iter 075:

- **educational** (iter 064 stream constrained by VRP basket to 2006+;
  effective window 2006-01-04 → 2026-04-15 ≈ 20y after inner-join with
  GLD+TLT). Sleeve at target_vol up to 0.30 still uses GLD/TLT inception
  2002-07-26 / 2004-11-18 — full coverage of all 3 windows.
- **spy_real** (2009-06-26 → 2026-04-15 ≈ 17y).
- **ndx_real** (2010-02-16 → 2026-04-15 ≈ 16y).

## Kill criteria (pre-committed)

If any of the following holds at end of Stage 3, the hypothesis is
falsified regardless of secondary metrics:

- **A — Borrow-drag math wrong**: The numpy-reference G7 check shows the
  borrow drag formula deviates from the iter 060 closed-form by > 1e-9
  on any tested cfg. Indicates an implementation bug in leg-level
  borrow modeling.
- **B — Leverage doesn't lift sleeve CAGR**: At `target_vol = 0.30`, sleeve
  standalone CAGR (gross of borrow) ≤ 6% on ≥ 2 of 3 datasets.
  Falsifies the linear-leverage-scaling hypothesis (sleeve is bottlenecked
  by trend-time-in-position, not by per-leg sizing).
- **C — Combined Sharpe regress vs iter 064**: Best combined cfg's
  Sharpe < `iter064_Sharpe - 0.05` on ≥ 2 of 3 datasets. **Predicted
  to fire** (math: borrow drag at lev=2× and rate=4.5% drops sleeve
  Sharpe from ~0.50 → ~0.20; combined Sharpe weighted-averages toward
  the lower-Sharpe sleeve and regresses).
- **D — Score < 75**: Best cfg score < 75 (drops below STRONG into
  PROMISING). Likely if KILL C fires.
- **E — Cross-lib bug**: G7 > 3 pp CAGR difference on ≥ 1 dataset
  between `iter076_sleeve.py` and `numpy_reference_iter076.py`.
- **F — PBO overfit**: PBO grid-level > 0.5 on ≥ 2 of 3 datasets.
  Mitigated by 4×5 grid (vs iter 075's narrow 7-cfg weight-only grid).
- **G — DSR fails**: Best cfg DSR worst-of-3 p-value > 0.05 with v2
  convention `n_trials = 20`.

**Pass condition that signals winner candidate**: best cfg ALL of
{Sharpe ≥ bench + 0.10 on 2/3 datasets, gates 5+/4+/4+ cross-ds, DSR p
< 0.05, CAGR ≥ 0.8 × bench on 2/3, MDD ≤ bench + 5pp on 2/3, score ≥
90} → 🏆 WINNER under v2 convention.

**Pre-committed honest expectation** (full math in Selection Rationale
below): KILL B unlikely (linear scaling DOES lift CAGR roughly
proportionally up to leg_cap binding). KILL C **likely fires** —
predicted combined Sharpe regression of 0.05-0.15 due to borrow drag.
KILL D likely fires. CAGR floor likely still fails on spy/ndx even at
the highest target_vol. **Predicted score: 65-80 PROMISING-to-STRONG**.

This iteration's primary value is **clean closure** of the
leverage-as-CAGR-floor-fix sub-axis with hard math, freeing iter 077 to
pursue alternative joint-constraint resolutions (DBMF managed-futures,
MTUM-VLUE long-short — both require Tiingo data ops not done in this
iter).

## Expected budget

- Configs to test: **20** (4 target_vol × 5 w_sleeve grid).
  - `target_vol ∈ {0.10, 0.15, 0.20, 0.25, 0.30}`. The `0.10` row
    serves as a baseline sanity check that MUST reproduce iter 075's
    7-cfg results at the matching weight cells (since at target_vol
    = 0.10, leg_cap = 3.0 doesn't bind → borrow drag = 0).
  - `w_sleeve ∈ {0.15, 0.25, 0.35, 0.50}`. Wider span than iter 075
    (0.10-0.40) — addresses iter 075's narrow-grid PBO inflation.
- **Borrow rate**: fixed `borrow_rate_annual = 0.045` (industry-standard
  retail-broker portfolio-margin SOFR + 0.5-1.0% spread). Single value
  to keep cfg count manageable; iter 077 can sweep borrow rates if
  warranted.
- **leg_cap**: fixed `3.0` (allows per-leg leverage up to 3× when
  realized vol is low enough that target_vol/realized_vol exceeds 1).
- Wall-time: **~30-60 min** (sleeve sim + ensemble + gates × 20 cfgs ×
  3 datasets, mostly reusing iter 064 saved streams).
- Files to create:
  - `iter076_sleeve.py` — extended sleeve simulator with borrow drag
    (modifies iter 075's `_single_leg_returns` to deduct
    `(pos - 1)+ × daily_borrow` when `pos > 1`).
  - `numpy_reference_iter076.py` — pure-numpy reference for G7 parity.
  - `tests/test_iter076_sleeve.py` — TDD specs (≥ 14 tests, mirroring
    iter 075 + new borrow-drag tests).
  - `run_backtests.py` — driver across 3 datasets × 20 cfgs.
  - `compute_gates_and_score.py` — gate battery + scoring.
  - `results.json`, `verdict.json` (= `verdict_v2.json` since v2 is
    now native), `final_report.md`, `plot_vs_benchmark_*.png`.

## Implementation plan

1. **Write TDD spec** `tests/test_iter076_sleeve.py` (≥ 14 tests):
   - Sleeve at `target_vol = 0.10, leg_cap = 1.0` reproduces iter 075
     output bit-for-bit (sanity baseline).
   - `borrow_rate = 0` ⇒ same output as `leg_cap = ∞` at any target_vol
     (no drag charged).
   - When `pos[t-1] > 1.0`, leg return = `pos · raw - (pos - 1) ×
     daily_borrow`; when `pos[t-1] ≤ 1.0`, no drag.
   - At `target_vol = 0.30, leg_cap = 3.0`, average leg pos in trend ≈
     1.5-2.5 on GLD/TLT real prices.
   - Linear-leverage CAGR scaling: at `target_vol = 0.20`, sleeve gross
     CAGR ≈ 2× the `target_vol = 0.10` sleeve gross CAGR (within ±20%
     tolerance for vol-cap binding).
   - T-1 signal lag preserved.
   - Equal-weight inner construction (50/50 GLD/TLT).
   - Cross-lib: numpy-pure reference matches main impl ±1e-9 on all 20
     cfgs.
   - Combined ensemble at `w_sleeve = 0` returns iter 064 only.
   - Combined ensemble at `w_sleeve = 1` returns sleeve only.
   - At `target_vol = 0.10` row, all 4 weight cells reproduce iter 075's
     `w_sleeve ∈ {0.15, 0.25, 0.35}` cells exactly (the iter 075 result
     was at slightly different weight grid; intersection cells must
     match within ±1e-9).
   - Borrow drag is non-negative (cannot subsidize the leg).
   - `daily_borrow_from_annual(0.045) ≈ 1.745e-4` (sanity check).
   - Cap binding: when `leg_cap = 1.0` and `target_vol = 0.30`, leg pos
     never exceeds 1.0.

2. **Implement** `iter076_sleeve.py`:
   - Extend iter 075's `_single_leg_returns` to subtract
     `max(pos[t-1] - 1, 0) × daily_borrow_from_annual(borrow_rate)` per
     bar.
   - Reuse `daily_borrow_from_annual` from iter 060 (or replicate
     locally for self-contained iteration code).
   - Sleeve and ensemble functions otherwise identical to iter 075.

3. **Implement** `numpy_reference_iter076.py`:
   - Pure-numpy SMA-200 + vol scaling + borrow drag.
   - Compares vs main impl bar-by-bar (max abs diff ≤ 1e-9 expected).

4. **Run** `run_backtests.py` on all 3 datasets:
   - 20 cfg outputs to `results.json`, including `returns_series` for
     top-cfg-per-dataset (Stage-5 plot helper requirement).
   - Saves cross-cfg correlation matrix for kill-C diagnosis.

5. **Compute gates and score** in `compute_gates_and_score.py`:
   - Gates G1-G7 per dataset on top-5 cfgs by Sharpe.
   - DSR uses `n_trials = 20` (v2 native).
   - Robustness sub-windows (3 chronological thirds × 3 datasets = 9).
   - Outputs `verdict.json` (= `verdict_v2.json`).

6. **Final report** + update BASE_MEMORY + plot via plot_helper.

## Selection rationale

**Why this hypothesis is structurally distinct**:

- vs **iter 075** (unlevered GLD/TLT sleeve at target_vol=0.10, leg_cap
  =1.0): **iter 076 lifts target_vol up to 0.30 with leg_cap=3.0 and
  honest leg-level borrow drag**. The risk mechanism per the prompt's
  "structural novelty" definition changes: iter 075 is a Sharpe-
  preserving inverse-vol sizing without leverage, iter 076 is leverage-
  augmented inverse-vol sizing with non-trivial financing cost. The
  question of "does leverage clear the CAGR floor without regressing
  Sharpe?" is the structurally novel test.

- vs **iter 060** (1.5× external lev on iter 058 saved combined stream
  at 2.5% borrow): iter 060 leverages POST-STREAM (flat daily multiplier
  on combined return). Iter 076 leverages PER-LEG via inverse-vol
  sizing (leverage varies daily based on per-leg realized vol and trend
  state). These are mechanically distinct: post-stream lev preserves
  Sharpe pre-borrow; per-leg vol-targeted lev does too, but the
  application surface is different and the cap-binding behavior differs.

- vs **iter 056** (130% external lev on iter 046 at 3.5% borrow): Same
  distinction as vs iter 060 — post-stream vs per-leg.

- vs **iter 027** (levered VRP primary): VRP has constant rf collateral;
  per `[advances_fin_ml]` p.222-223 closure documented in DEAD_ENDS,
  Sharpe is leverage-invariant in excess-return form for harvest+rf
  strategies. Iter 076's GLD/TLT trend has NO rf collateral and
  position varies daily with vol — completely different mathematical
  behavior under leverage.

**Why the math predicts KILL C will fire**:

For a Sharpe-S strategy with vol-target σ_T and excess-return formula
`r_excess = S × σ_T - (lev - 1) × spread × t_in_position`, the
post-borrow Sharpe is approximately:

```
Sharpe_post_borrow ≈ S - (lev - 1) × spread / σ_T × t_in_position
```

For our sleeve with iter-075-baseline `S ≈ 0.50`, applying `lev = 2.5`
(target_vol = 0.25, avg realized vol ≈ 0.10 on the equal-weight GLD/TLT
basket → avg pos ≈ 2.5 in trend), `spread = 0.045`, `σ_T = 0.25`,
`t_in_position ≈ 0.7`:

```
Sharpe_post ≈ 0.50 - (2.5 - 1) × 0.045 / 0.25 × 0.7
            ≈ 0.50 - 1.5 × 0.18 × 0.7
            ≈ 0.50 - 0.189
            ≈ 0.31
```

Sharpe drops from ~0.50 → ~0.31. Combined Sharpe with iter 064 at
`w_sleeve = 0.30` weighted-averages toward the lower-Sharpe sleeve and
regresses ~0.05-0.10 vs iter 064's 1.33 spy.

**Why this iteration is still worth running** (predicted-to-fail
hypothesis):

1. **Mechanical closure**: pre-committed math says leverage-on-low-Sharpe
   regresses combined Sharpe via borrow drag. Empirical confirmation
   permanently closes the leverage-as-CAGR-fix sub-axis on iter-064
   anchors, freeing iter 077-080 to pursue qualitatively different
   2nd-leg sources (DBMF / MTUM-VLUE / Hurst regime / cross-sectional
   factor pairs).

2. **G7 cross-lib parity** stress-test on a new mechanism (per-leg
   borrow drag) — strengthens the cross-lib discipline track record
   for future iters that need leverage modeling.

3. **PBO grid-design lesson**: iter 075's narrow-grid PBO inflation
   (0.86 edu) was a discomfort signal. Iter 076's 4×5 grid will reveal
   whether wider grid restores PBO < 0.5 (informing iter 077's grid
   design).

4. **20-cfg DSR floor stress**: the v2 convention with n=20 vs iter
   075's n=7 — provides empirical base rate for DSR p-value scaling
   with grid size.

If iter 076 ACTUALLY beats predictions and clears all 5 winner
conditions, this is a 🏆 WINNER candidate (BASE_MEMORY's first win
since loop start) and the leverage-as-CAGR-fix axis becomes
production-relevant.

## Anti-redundancy check vs DEAD_ENDS.md

Key risk: leverage-on-iter-064 is a known dead end family. Confirmed
distinct from prior closures via mechanism specifics:

- **iter 056 (130% post-stream lev iter 046, 3.5% borrow)** — closed at
  74 PROMISING; mechanism is post-stream flat daily multiplier on
  combined return. Iter 076 is **per-leg vol-targeted** lev with
  cap-binding on legs (not post-stream).
- **iter 060 (1.5× post-stream lev iter 058, 2.5% borrow)** — closed at
  79 STRONG; mechanism is post-stream flat multiplier with futures-
  implied borrow. Same distinction as iter 056.
- **iter 027 (levered VRP)** — closed; VRP constant-rf collateral makes
  excess-Sharpe leverage-invariant. Iter 076's GLD/TLT trend is NOT
  rf-collateralized; vol varies daily.
- **iter 005 (variance-managed SPY)** — closed at low score; single-asset
  variance-management without trend filter. Iter 076 is multi-asset
  trend-filtered with per-leg vol-target.
- **iter 075 (unlevered GLD/TLT sleeve at target_vol=0.10)** — closed at
  81 STRONG; **iter 076 is the leverage-augmented variant** answering
  the iter 075 lesson's pre-committed question.

The "iter 064 + non-equity Faber-trend single-vol-target sleeve
ensemble" axis was closed at 81 in iter 075. Iter 076 opens a new
sub-axis: "iter 064 + non-equity Faber-trend MULTI-vol-target leg-
levered sleeve ensemble with honest borrow drag." This is a parameter-
sweep extension that converts iter 075's predicted CAGR-floor fix into
an empirical test with hard borrow modeling. Closure of this sub-axis
informs the JOINT-CONSTRAINT structure exposed in iter 075's lesson.

If KILL C fires (likely), the closure says: **"on iter-064-anchored
ensembles, leverage CANNOT mechanically resolve the CAGR-floor gap
because the borrow drag eats the Sharpe."** This is a permanent
structural finding worth the iteration cost.

If KILL C clears (unlikely but possible if Sharpe-of-sleeve happens to
hold up better than expected on real data), iter 076 may produce a
🏆 WINNER candidate.
