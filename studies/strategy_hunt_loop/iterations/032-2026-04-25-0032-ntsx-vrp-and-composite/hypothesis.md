# Iteration 032 — NTSX 90/60 SPY+IEF base + iter 031 AND-composite VRP overlay

## Hypothesis

Combine two STRONG-tier mechanisms from prior iterations into a single
multi-asset return-stacked portfolio that targets the score-rubric
ceiling at 76 from a structurally different angle (criterion 4 — CAGR
floor — at 0/15 is the only remaining headroom on iter 026 family).

**Mechanism**:

```
combined[t] = 0.9·r_SPY[t] + 0.6·r_IEF[t] − cost_eq[t] − cost_bd[t]
              + harvest_notional · (−overlay_AND_composite[t])
```

where:

* `0.9·r_SPY + 0.6·r_IEF` is the iter 015 NTSX 90/60 static stack
  (top-K #4, STRONG 77; Sharpe 0.83/1.04/1.16 cross-ds; CAGR floor
  3/3).
* `−overlay_AND_composite` is the iter 031 short put-credit-spread
  overlay (5/10% OTM, 21-DTE monthly roll) gated by the AND-composite
  R-1 ∧ R-2 (`VIX≥35 for 3 days` AND `z(VIX,60d)≥2`); top-K #5 tied at
  STRONG 76 with first-ever all-3-DSR < 0.10 (edu 0.054 / spy 0.070 /
  ndx 0.050).
* No funding cost on the 0.5x extra leverage (matches iter 015
  convention; iter 018 quantified the omission as ≈ −93 to −148 bps/yr,
  Sharpe haircut ≈ −0.05 to −0.10).

Multi-source edge composition: equity beta + bond duration risk-premium
(Asness-Frazzini-Pedersen 2012) + variance-risk-premium (Bondarenko
2014) + AND-composite regime gate that catches only Sep-Oct 2008 GFC,
Mar-2020 COVID, and 2011-08 US debt-downgrade — exactly where Sinclair
(p.217-218) flags hedging short-vol writers as essential.

## Primary citation

`[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen (2012)
"Leverage Aversion and Risk Parity," *Financial Analysts Journal* 68(1):
47-59. SSRN 1728082. Risk-parity argument: leveraging a diversified
base produces higher Sharpe per unit total risk than concentrated
equity. Iter 015 base directly applies this principle.

## Additional citations

* `[volatility_trading, p.41, ch.3]` — Sinclair (2013), VRP mechanics
  + SPX excess kurtosis 21.3 → put-side OTM is "expensive" (premium
  bid up by tail-aversion).
* `[volatility_trading, p.217]` — Sinclair §"Hedging short volatility
  positions": VIX < 35 entry filter (R-1 level component).
* `[volatility_trading, p.218]` — Sinclair §"VIX-VXV term structure":
  *sustained* high IV is the warning sign for short-vol writers
  (R-2 z-score motivation).
* `[volatility_trading, p.39, p.58-59]` — VIX vol-of-vol regime
  dependence + 60-day cone (z_window anchor).
* `[leverage_for_the_long_run, p.19-20]` — leverage on a diversified
  base captures duration risk-premium without market-timing.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
* WisdomTree NTSX prospectus — 90/60 SPY+IEF weights (manufacturer-
  prescribed). https://www.wisdomtree.com/investments/etfs/asset-allocation/ntsx
* **Bondarenko, O. (2014). "Why Are Put Options So Expensive?"**
  *Quarterly Journal of Finance* 4(3): 1450015.
  DOI: 10.1142/S2010139214500153 — §3 establishes that *both* level
  AND persistence dimensions matter (motivation for AND-composite gate).
* **Carr, P. & Wu, L. (2009). "Variance Risk Premiums."** *Review of
  Financial Studies* 22(3): 1311-1341. DOI: 10.1093/rfs/hhn038 — VRP
  level/persistence/innovation decomposition (theoretical anchor).
* **Whaley, R. E. (2009). "Understanding the VIX."** *Journal of
  Portfolio Management* 35(3): 98-105. DOI: 10.3905/JPM.2009.35.3.098
  — VIX standardized-deviation analysis (z-score anchor).
* **Asness, C. S., Frazzini, A. & Pedersen, L. H. (2012). "Leverage
  Aversion and Risk Parity."** *Financial Analysts Journal* 68(1):
  47-59. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1728082
  — risk-parity argument for the NTSX-style base.

## Edge source

SPY 1× misses three orthogonal premiums simultaneously:
1. **Bond duration risk-premium** (term premium) on the 7-10y Treasury
   leg — a genuine risk-on/risk-off diversifier;
2. **Variance risk-premium** from systematically writing 5/10% OTM
   put-credit spreads when neither level nor z-score regime indicates
   sustained vol stress;
3. **Conditional crash protection** via the AND-composite gate that
   abstains during Sep-Oct 2008, Mar-2020 COVID, and 2011-08 debt-
   downgrade events — the regimes literature flags as the warning
   signs for short-vol writers.

## Datasets

* **educational** (SPY+IEF+VIX, 2006-01-03 → 2026-04-14, ~20y):
  Includes GFC + COVID + 2022 vol regime. Forces the AND-composite
  to fire on Sep-Oct 2008 (iter 031 confirmed) and 2020-03-11 — the
  iter 015 base alone delivered Sharpe 0.83 here; expect overlay to
  lift this without breaking MDD.
* **spy_real** (SPY+IEF+VIX, 2009-06-25 → 2026-04-14, 17y):
  Post-GFC regime where iter 031 composite *never fires* (no day in
  17y had both VIX≥35-for-3d AND z≥2 simultaneously) → on this
  dataset the harvest layer behaves identically to iter 026 baseline
  on top of iter 015 base. Expected: clean stack of iter 015 spy 1.04
  Sharpe + iter 026 spy 1.28 harvest premium.
* **ndx_real** (QQQ+IEF+VIX×1.1, 2010-02-12 → 2026-04-14, 16y):
  iter 031 composite caught 2011-08-12 + 2020-03-19 here (only
  dataset where ndx still has 7/7 gates + DSR PASS). Tests whether
  the 90/60 stack on QQQ+IEF preserves the iter 031 ndx regime
  performance.

## Kill criteria (pre-committed)

If ANY of the following hold at end of Stage 4, the hypothesis is
falsified:

* **Kill A — Sharpe absorbed by base**: combined Sharpe < `max(iter015,
  iter031) − 0.05` on ≥2/3 datasets (i.e., the overlay is absorbed
  by NTSX leverage rather than additive). Reference Sharpes:
  - educational: max(0.83, 1.19) − 0.05 = 1.14
  - spy_real:    max(1.04, 1.28) − 0.05 = 1.23
  - ndx_real:    max(1.16, 1.33) − 0.05 = 1.28
* **Kill B — MDD blowout**: combined MDD > 40% on any dataset
  (bond+equity correlation breakdown — iter 015 had 23% / 19% / 24%
  MDD; iter 031 had 14% / 6% / 8%; combined should sit between).
* **Kill C — Score < 79**: total score ties or is below the top-K #1
  ceiling (iter 016/018/021 all at 79). The iteration is structurally
  novel only if it BREAKS the 79 ceiling (reaches ≥ 80).
* **Kill D — G7 cross-lib > 3 pp CAGR** (engine bug in composition).
* **Kill E — DSR distribution worsens**: worst-p across 3 datasets
  > 0.10 (iter 031 achieved 0.070 worst-p; combined should not
  regress to single-axis 71-tier worst-p).
* **Kill F — Robustness < 9/9**: any sub-window across 3 datasets has
  Sharpe ≤ 0 (iter 015 + iter 031 both delivered 9/9; if combined
  doesn't preserve, the harvest is destabilizing).

If 4-5 kills clean and only 1-2 fire (specifically B/D), the result
may still inform future iterations — those would be implementation-
recoverable issues. If A/C/E/F fire, the structural premise is wrong.

## Expected budget

* Configs to test: **1 pre-committed cfg** (`ntsx_vrp_and_v3p35_z2_eq09_bd06_h1`)
* Wall-time: ~10-15 minutes (single cfg × 3 datasets × ~5000 bars each;
  reuses iter 015 + iter 031 primitives — no new heavy computation).
* Files to create:
  - `ntsx_vrp_combined.py` — pandas wrapper composing iter 015 +
    iter 031 primitives.
  - `numpy_reference_combined.py` — numpy-pure parity via composition
    of iter 015's `apply_static_stack_np` and iter 031's
    `compute_vrp_and_composite_returns_np`.
  - `run_backtests.py` — runs 3 datasets, writes `results.json`.
  - `compute_gates_and_score.py` — gate battery + score (frozen
    benchmarks) + custom-bench educational fallback.
  - `tests/test_iter032_ntsx_vrp_combined.py` — TDD specs:
    1. `harvest_notional=0` reduces to iter 015 exactly.
    2. `eq_w=bd_w=0` reduces to iter 031's overlay-only (= iter 026
       minus rf_daily).
    3. cross-lib parity at machine-precision (max abs diff < 1e-10).
    4. AND-composite skip diagnostic matches iter 031's per-dataset
       skip dates exactly.

## Implementation plan

1. **TDD first**: write `tests/test_iter032_ntsx_vrp_combined.py` with
   the 4 reduction-property tests.
2. **Implement `ntsx_vrp_combined.py`**:
   - Inner-join SPY/QQQ + IEF + VIX + z series.
   - Compute pct_change for equity and bond.
   - Call iter 015's `apply_static_stack` for the NTSX leg.
   - Call iter 031's `compute_vrp_and_composite_returns`; subtract
     `rf_daily` to extract the harvest overlay only.
   - Sum on the intersected index.
3. **Implement `numpy_reference_combined.py`**: compose the two
   existing numpy references into a single `compute_combined_returns_np`.
4. **Run TDD tests** — must all pass before backtests.
5. **Run `run_backtests.py`** on 3 datasets; persist `results.json`
   with `returns_series` (Stage-5 plot helper depends on this key).
6. **Run `compute_gates_and_score.py`** — produces `verdict.json`.
7. **Generate plots** via `plot_helper.py --iter 032`.
8. **Write `final_report.md`**, update `BASE_MEMORY.md`,
   `DEAD_ENDS.md` if structural finding emerges.

## Cumulative n_trials advance

`4284 → 4285` (+1; matches iter 026/028/029/030/031 single-cfg
convention).

## Why this is structurally distinct from iter 020/021

Iter 020/021 tested options-on-equity-leg overlays on top of iter 016's
**vol-managed** static stack. Iter 016's wrapper makes `σ²_port`
quadratic in `w_eq` because `w_eq[t] = vol_target / σ̂[t-1]` responds
to recent realized volatility — when the put-spread fires (vol spike),
`w_eq` shrinks, mechanically absorbing the put-spread P&L.

Iter 015 base is **STATIC** weights (`eq_w=0.9, bd_w=0.6` constant).
No vol-target wrapper, no inverse-variance scaling, no σ²_port
quadratic absorption. The harvest layer is genuinely additive, just
as iter 026 (T-bill collateral, no equity) demonstrated.

The combined return decomposes cleanly:

```
combined Sharpe ≈ √( Sh_NTSX² + Sh_VRP² + 2·ρ·Sh_NTSX·Sh_VRP ) / scale
```

where ρ ≈ 0.7-0.75 (iter 031 reported corr_SPY for VRP harvest);
Sh_NTSX ≈ 0.83-1.16; Sh_VRP ≈ 1.19-1.33. Even with high correlation,
the floor combination (mean Sharpe) is ≈ 1.0-1.3 cross-ds. This
hypothesis tests whether the empirical combination delivers the
predicted floor or shows unexpected absorption.

## Falsifiability commitment

Any of {Kill A, C, E, F} firing means the structural premise is
falsified — the layered composition does NOT cleanly add Sharpe in
practice. Adding {Kill B} or {Kill D} as additional fail modes is
implementation-quality (covered by tests).

If 0/6 kill, this iteration likely SCORES ≥ 80 and produces the
**first iteration to beat the iter 016/018/021 79 ceiling** since
iter 015. If 1-2/6 kill (B/D), the iteration informs without breaking.
