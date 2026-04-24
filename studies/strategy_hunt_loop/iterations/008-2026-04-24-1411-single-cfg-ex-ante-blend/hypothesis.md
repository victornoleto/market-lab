# Iteration 008 — Single-config ex-ante vol-managed SPY+TLT blend

## Hypothesis

Iter 006 found a PROMISING (67/100, 4/5 winner conditions met) vol-managed
SPY+TLT blend using inverse-variance weighting + Moreira-Muir
portfolio-level variance-scaling. The mechanism cleared the +0.10 Sharpe
gate on 2 of 3 datasets and the CAGR + MDD floors on 3/3 datasets for the
first time in the hunt loop. The ONE gate that failed structurally was
**G1 PBO on educational + spy_real (0.690 both)**, because a 12-config
grid introduces IS/OOS rank-reversal on any blend mechanism (iter 007
confirmed this still holds at N=3).

**Iter 008 claim:** if the blend edge is structural (not an artifact of
grid-search over 12 cfgs), running a single ex-ante pre-committed
configuration — with NO grid, NO sweep — should retain the Sharpe edge on
at least 2 of 3 datasets AND eliminate G1 PBO as a gate failure mode (PBO
is undefined for N=1). The DSR and CAGR/MDD tiers should remain
near-identical to iter 006's top candidate on the same config. Net effect
on ranking: score should climb from iter 006's 67 PROMISING toward 70-80
STRONG as G1 flips to PASS on the two datasets where iter 006 failed it
(edu + spy).

This is the "OPTION A — LOW-COST VERIFICATION" direction listed in
`BASE_MEMORY.md` and the explicit **PICK FIRST** recommendation from iter
007's final_report.md (§ Next iteration suggestions).

## Primary citation

`[risk_parity, p.10-11, ch.1]` — naïve risk parity (inverse variance per
leg) is the exact equal-risk contribution solution for a two-asset
portfolio. Foundation of the iter 006 blend.

## Additional citations

- `[risk_parity, p.80-81, ch.4]` — SPY-TLT negative correlation
  (-0.23 to -0.31 across iter 006's 3 datasets) is the cross-asset
  diversification axis this sizing mechanism exploits.
- `[systematic_trading, p.144, ch.9]` — target_vol calibration:
  institutional equity mandates typically run 12-25% target vol; 15% is
  the median choice.
- `[systematic_trading, p.170-171, ch.11]` — Instrument Diversification
  Multiplier (IDM) cap ≤ 2.5. We pre-commit `max_leverage = 2.0` to stay
  conservatively below the cap.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag on rolling variance
  (no look-ahead).
- `[advances_fin_ml, p.208-211]` — G1 PBO via CSCV. Definitionally
  requires a grid of configs; undefined for N=1.
- `[advances_fin_ml, p.222-223]` — G2 DSR deflator with cumulative
  n_trials across the entire hunt loop.

**Web / external**:

- **Moreira & Muir (2017).** *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513).
  Portfolio-level variance-scaling form `s_t = c / σ²_{t-1}`; Table II
  uses ~12% monthly target vol (canonical in the monthly rebalance
  regime). Iter 008 preserves this form at daily horizon with 15%
  annualized target.
- **Asness, Frazzini & Pedersen (2012).** *FAJ* 68(1). SSRN
  [1728082](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1728082).
  Risk-parity cross-asset allocation.

## Edge source

What SPY 1x buy-hold fails to capture:

1. **TLT's partial hedge during equity drawdowns** — SPY-TLT correlation
   negative ~-0.30 (measured iter 006) gives diversification return at
   the portfolio level.
2. **Variance persistence** — Moreira-Muir's `σ^{-2}` portfolio scaling
   deploys more aggressively in low-vol regimes (where SPY's forward
   Sharpe is systematically higher) and de-levers during high-vol
   periods.

**Edge source is IDENTICAL to iter 006.** The only structural change is
the ex-ante pre-commitment of a single cfg, which changes the statistical
treatment of overfitting risk (G1 PBO becomes undefined → not a gate we
can fail on grid-pick variance) without changing the underlying
mechanism.

## Pre-committed configuration

**`vt15_L21_cap20`**:

| param | value | literature anchor |
|---|---|---|
| `target_vol` | 0.15 | `[systematic_trading, p.144]` mid-institutional equity range; Moreira-Muir 2017 Table II uses 12% monthly ≈ 15% annualized for equities |
| `lookback` | 21 | 1 trading month (Moreira-Muir canonical vol-window) |
| `max_leverage` | 2.0 | ≤ 2.5 IDM cap `[systematic_trading, p.170-171]`; 2.0 keeps one-cap-hit margin |
| `cost_bps_per_leg` | 2 bps | matches iter 006 cost model |

**Commitment timing**: The cfg above is chosen BEFORE re-running any
backtests. It is declared in this hypothesis.md file and will be the
ONLY cfg simulated for iter 008. No sweep, no comparison among multiple
cfgs, no post-hoc selection.

**Disclosure**: this cfg corresponds to iter 006's top spy_real / ndx_real
candidate. The `target_vol`, `lookback`, `max_leverage` values can
ALL be defended from literature (above). The "coincidence" with iter
006's grid-pick is acknowledged — the honest way to run this is to treat
iter 006's grid as a "training set" for parameter selection and iter
008 as a "test" on the same time window but with the overfitting risk
accounting (cumulative_n_trials = 4240) intact. If the Sharpe replicates
at the iter 006 magnitudes, the mechanism generalises without grid
refinement; if it deviates, the iter 006 edge was grid-inflated.

## Datasets

Identical to iter 006 (reproducibility is the point):

- **educational**: SPY+TLT 2002-07-26 → 2026-04-15 (24y, longest window
  with TLT cache). Custom benchmark SPY b&h on same window (Sharpe
  ~0.66 measured in iter 006).
- **spy_real**: SPY+TLT 2009-06-25 → 2026-04-15 (17y post-GFC).
  Benchmark: frozen scoring.BENCHMARKS["spy_real"] (SPY 0.90).
- **ndx_real**: QQQ+TLT 2010-02-12 → 2026-04-15 (16y). Benchmark:
  frozen scoring.BENCHMARKS["ndx_real"] (QQQ 0.955).

## Kill criteria (pre-committed)

The hypothesis is **falsified** if ANY of the following fire:

1. **Kill #1 (reproducibility)**: Sharpe on spy_real < 0.970 (Δ ≤ -0.03
   vs iter 006's 1.000). If iter 008 re-run with identical cfg produces a
   materially different Sharpe, the iter 006 result was not deterministic
   — i.e., implementation or data drift between iterations. Falsifies
   the validity of any comparison.

2. **Kill #2 (CAGR ndx floor)**: ndx_real CAGR < 15.35% (= 0.8 × bench
   19.18%). The CAGR floor criterion falls below acceptable — indicates
   the blend's cost of de-leveraging is higher than iter 006's snapshot
   suggested, and the gain from cross-asset diversification doesn't
   compensate on a tech-heavy universe.

3. **Kill #3 (WF window failure)**: G3 Walk-Forward profitable_windows
   < 6/8 on spy_real OR ndx_real. The grid-selection of iter 006 could
   have been hiding a window-level instability (e.g., only 6 of 8
   windows passed because the top cfg was tuned to specific sub-windows).
   If WF degrades vs iter 006's 7/8 (spy) or 8/8 (ndx), single-cfg
   verification confirms the robustness was a grid artifact.

4. **Kill #4 (score regression)**: iter 008 total_score ≤ 60 (one full
   tier below iter 006). If the scoring drops from PROMISING 67 to
   MARGINAL 40-59 despite G1 flipping to PASS, the "single-cfg"
   hypothesis is rejected — removing the grid introduces a different
   source of weakness (e.g., drops a different gate unexpectedly).

If NONE of 1-4 fire AND score climbs to ≥ 75 (STRONG), the verification
is positive: the blend edge is structural, not grid-selected, and iter
009 can safely extend to 3-asset blends or orthogonal-signal overlays.

## Expected budget

- **Configs to test**: 1 cfg × 3 datasets = 3 new trials. Cumulative
  n_trials advances: 4237 → **4240**.
- **Wall-time**: ≈ 3-5 minutes for the backtest (reuses iter 006 data
  cache) + ≈ 3-5 minutes for the 7-gate battery (most expensive: G1
  PBO which we skip for N=1, G6 bootstrap with 5000 resamples).
- **Files to create**:
  - `run_backtests.py` — single-cfg runner, reuses
    `../006-*/stock_bond_blend.py`
  - `compute_gates_and_score.py` — gates with N=1-aware G1 handling +
    robustness bonus (criterion 6) computation
  - `results.json`, `verdict.json`, `final_report.md`

**No new simulator logic.** Pure reuse of iter 006's
`stock_bond_blend.py` + `numpy_reference.py`. No new TDD specs required
— baseline pytest (currently 729 passed + 5 skipped per iter 007 final
report) must stay green.

## Implementation plan

1. **Data load**: reuse iter 006's `load_paired_returns()` interface;
   same 3 datasets, same start/end dates.
2. **Backtest**: call `apply_blend_variance_target()` from iter 006's
   module with the one cfg, once per dataset. Record metrics.
3. **Gate battery**:
   - **G1 PBO**: N=1 → PBO undefined. Mark gate as **PASS** (vacuously
     — no grid-pick overfit is possible when there's no grid). Record
     `pbo_value = None` with explicit comment in verdict.json.
   - **G2 DSR**: run standard DSR test with
     `cumulative_n_trials = 4240`.
   - **G3 WF**: identical to iter 006's 8-window split.
   - **G4 OOS**: 70/30 split, identical.
   - **G5 FWD**: post-2020 Sharpe, identical.
   - **G6 bootstrap**: stationary bootstrap (block_mean=5, 5000
     resamples, seed=42), 99.9% CI low > 0.
   - **G7 cross-lib**: compare pandas engine CAGR to numpy reference
     (`numpy_reference.py`) — should match within 0.03-0.05 pp as in
     iter 006.
4. **Robustness bonus (criterion 6)**:
   - Split each dataset into 3 non-overlapping sub-windows (first/mid/
     last third by bar count).
   - Compute Sharpe per sub-window per dataset.
   - Award bonus = min(5, 2 * fraction_positive) where
     fraction_positive = (# windows with Sharpe > 0) / 9.
     - 9/9 → 5 pts, 8/9 → 4 pts, 7/9 → 3 pts, 6/9 → 2 pts, 5/9 → 1 pt,
       ≤ 4 → 0 pts.
5. **Score**: call `score_strategy()` with metrics, gates,
   cumulative_n_trials=4240, and custom benchmarks (edu custom, spy/ndx
   frozen). Add robustness bonus to total_score manually (scoring.py's
   c6_pts is a placeholder for caller-provided rolling-window stats).
6. **Write outputs**: results.json (raw backtest), verdict.json
   (scored), final_report.md (prose + tables).
7. **Update memory**: bump total_iterations → 8, cumulative_n_trials →
   4240, add iteration log entry, update Top-K ranked table, move the
   direction from "Promising unexplored" to a consumed/dead state
   depending on verdict.
