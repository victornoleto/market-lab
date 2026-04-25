# Iteration 060 — Iter 058 levered 1.5× via futures-implied financing (2.5% borrow)

## Hypothesis

iter 058 (TOP-K #1, score 85) has Sharpe 1.22/1.35/1.40 and MDD
16.74/13.71/13.12% — leaving **22pp of MDD slack** on spy/ndx vs
benchmark+5pp ceilings (38.70/40.12%) but failing CAGR floor 0/3
(8.69/9.01/9.27% vs floors 9.18/11.98/15.35%). Iter 056 attempted
to convert that MDD slack into CAGR via 1.3× external leverage on iter
046 at **3.5% retail Reg-T margin** and FAILED (score 74, DSR collapse
on all 3 datasets) because the 1.5pp spread above T-bill compounded
into a ~0.10 Sharpe drag.

This iteration tests whether **futures-implied financing at 2.5%
borrow rate** (T-bill ~2.0% + 0.5% Treasury futures roll cost,
NTSX-style mechanism per Hsiao-Williams 2017) breaks the iter 056
closure pattern when applied to **iter 058's saved combined stream**
(the DSR-clearing variant with HYG_TSM 3rd-stream).

The 1.0pp lower borrow rate vs iter 056 reduces the spread from 1.5pp
to 0.5pp, **cutting Sharpe drag by ~3×** (from ~0.10 to ~0.030 at
lev=1.5×, σ_annual≈5.5%). At that drag level:
- Sharpe edge survives (1.22-0.030 = 1.19 ≥ bench+0.10 = 0.78 on edu)
- DSR worst-p increases from iter 058's 0.0494 to ~0.07-0.09 (still
  below the 0.10 secondary cutoff for criterion 3 = 10 pts)
- CAGR scales by lev=1.5× minus borrow drag minus geometric drag:
  ≈ 1.5 × CAGR_unlev - 0.5 × 0.025 - lev(lev-1) × σ²/2

Predicted score: **84-89 STRONG**, with the CAGR-DSR Pareto trace
moving along the same boundary as iter 058's 85 (no clear breakout to
WINNER without borrow rate dropping to exactly rf, which is
structurally infeasible).

## Primary citation

`[leverage_for_the_long_run, ch.5]` — Hsiao & Williams 2017 *J. Index
Investing*. NTSX-style Treasury-futures financing achieves leverage at
~T-bill + 30-50bps (futures roll cost) instead of retail Reg-T margin
spread (typically T-bill + 150bps).

## Additional citations

- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 risk-parity
  stack (iter 041 base architecture, preserved verbatim via iter 046,
  preserved verbatim via iter 058 saved stream).
- `[volatility_trading, p.218]` — Sinclair 2013 cross-asset VRP (iter
  039 base preserved through iter 058).
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials
  (4329 → 4330).
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- `[systematic_trading]` (Carver) — TSM single-asset rule (HYG_TSM
  engine vendored from iter 058).
- Asvanunt, A. & Richardson, S. 2017, "The Credit Risk Premium",
  JPM 43(2), DOI 10.3905/jpm.2017.43.2.090 — credit risk premium
  thesis (iter 058 HYG component).
- Frazzini-Pedersen (2014), JFE 111(1) 1-25, DOI 10.1016/j.jfineco.2013.10.005
  — borrow frictions on levered low-vol strategies. **Iter 056
  vindicated this empirically at 3.5% retail spread; this iteration
  probes the 2.5% futures-implied analog.**
- IBKR Pro Tier 1 margin schedule (public, 2025-04) — 3.5% reference
  rate (iter 056 datum).
- CME E-mini S&P 500 futures roll cost methodology (Andersen-
  Dobrev-Schaumburg 2015 or BlackRock futures financing literature) —
  rationale for ~T-bill + 30bps achievable financing rate.

## Edge source

In one sentence: **iter 058's MDD slack vs benchmark (22pp on spy/ndx)
represents unused risk capacity, and futures-implied leverage at
T-bill + 50bps borrow rate converts it into +1.7-2.3pp annualized
CAGR with minimal Sharpe drag — what iter 056 attempted at retail
margin spread and failed.**

SPY 1x b&h fails to capture this because it's already at 1.0×
fixed-equity exposure with a single-asset Sharpe (~0.9 spy_real) —
it has no MDD slack to convert.

## Datasets

- **educational** (SPYSIM synth 40y, HYG-windowed to 2007-04+ via
  iter 058's saved stream): sanity-check leverage transform on the
  longest-history sample (iter 058 edu Sharpe 1.222 baseline).
- **spy_real** (SPY/UPRO 17y, 2009-06-25→2026-04-15): primary frozen-
  bench window for winner conditions; iter 058 spy Sharpe 1.347
  baseline.
- **ndx_real** (QQQ/TQQQ 16y, 2010-02-12→2026-04-15): tightest CAGR
  floor (15.35%) — the binding test of whether 1.5× leverage on iter
  058 (CAGR 9.27%) can clear the floor (~13.91% predicted at b=2.5%);
  if not, the leverage axis on iter 058 closes at this rate.

## Kill criteria (pre-committed)

| # | kill | observable | falsification meaning |
|---|---|---|---|
| A | Sharpe regress vs iter 058 by ≥ 0.10 on ≥ 2 datasets | observed Sharpe deltas | leverage drag at 2.5% borrow exceeds analytical prediction (~0.030); axis closes at this borrow rate |
| B | DSR worst-p ≥ 0.10 | DSR_p computed at n=4330 | even 0.5pp futures spread compounds DSR penalty too aggressively |
| C | Score < 78 (iter 050 baseline) | scoring.py output | regress past iter 050 = leverage transform broken or borrow rate effectively higher than predicted |
| D | G7 cross-lib > 3pp | numpy reference vs pandas engine CAGR Δ | engine bug in leverage transform |
| E | MDD breach > bench+5pp on ≥ 2 datasets | levered MDD vs ceilings | leverage too aggressive structurally |
| F | CAGR floor 0/3 (no improvement vs iter 058's 0/3) | levered CAGR vs floors | leverage transform doesn't propagate to CAGR (mechanical bug) |

If ≥ 4 of 6 kills fire → leverage axis on iter 058 at futures-rate
borrow CLOSED. Add to DEAD_ENDS.md.

If ≤ 1 kills fire → iter 058 is Pareto-improvable along the
leverage axis at futures-rate borrow; further iterations may sweep
borrow rates to find the optimum.

## Expected budget

- Configs to test: **1** (single pre-committed cfg, no grid sweep).
- cumulative_n_trials advance: 4329 → **4330** (+1).
- Wall-time: ~5-10 minutes (iter 058 stream is loaded from saved
  series, leverage transform is O(n)).
- Files to create:
  - `levered_iter058.py` (vendored leverage transform from iter 056
    with borrow rate change)
  - `numpy_reference_iter060.py` (G7 parity)
  - `run_backtests.py` (3-dataset runner)
  - `compute_gates_and_score.py` (G1-G7 + scoring)
  - `tests/test_levered_iter058.py` (TDD: leverage transform identity
    + numpy parity + Sharpe preservation at b=rf)
  - `results.json` (per-dataset metrics)
  - `verdict.json` (score + kill resolution)
  - `final_report.md`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`

## Implementation plan

1. **Vendor iter 056's leverage transform** (`levered_iter058.py`).
   Modify only `borrow_rate_annual` default 0.035 → 0.025; preserve
   the linear transform `r_lev = lev × r - (lev-1) × daily_borrow`.
2. **Vendor iter 056's numpy reference** (`numpy_reference_iter060.py`)
   for G7 parity check on the leverage transform alone (since iter
   058's combined stream is loaded from saved JSON, no engine call
   required for the base — only the leverage step needs G7 parity).
3. **Load iter 058's saved combined stream** from `iterations/058-*/
   results.json["returns_series"][ds][cfg_id]` per dataset.
4. **Apply leverage transform** at lev=1.5×, b=2.5%; produce levered
   daily net returns per dataset.
5. **Compute metrics + gates** using the same scaffold as iter 058
   (`compute_gates_and_score.py`):
   - G1 PBO: vacuous PASS at N=1.
   - G2 DSR: cumulative n_trials = 4330.
   - G3 Walk-Forward: 8 windows, MDD < 25% per window.
   - G4 OOS 70/30: train Sharpe → test Sharpe > 0.
   - G5 FWD post-2020: Sharpe of 2020+ subset > 0.
   - G6 Bootstrap 99.9% CI low > 0.
   - G7 Cross-lib: numpy reference within 3pp CAGR.
6. **Score** via `scoring.py::score_strategy()`.
7. **Write `final_report.md`** with kill resolution, headline metrics,
   score breakdown, structural lessons.
8. **Generate plots** via `plot_helper.py --iter 060`.
9. **Update BASE_MEMORY.md** + DEAD_ENDS.md if applicable.

## TDD specs (written FIRST)

- `test_leverage_transform_identity_at_lev_1`: lev=1.0 → returns
  unchanged regardless of borrow rate.
- `test_leverage_transform_zero_borrow`: lev=2.0, b=0 → exactly
  2.0 × r (no drag).
- `test_leverage_transform_at_rf_preserves_sharpe`: lev=1.5, b=rf=0.02
  → levered Sharpe == unlevered Sharpe (exact identity).
- `test_leverage_transform_drag_formula`: lev=1.5, b=0.025, rf=0.02
  → measured Sharpe drag matches `(lev-1)*(b-rf)/(lev*σ_annual)`
  within 1e-6.
- `test_numpy_pandas_parity`: identical inputs → identical levered
  output to 1e-12.
- `test_validation_lev_negative`: lev=-0.5 → ValueError.
- `test_validation_borrow_negative`: b=-0.01 → ValueError.

## Predicted scoring (analytical)

At lev=1.5×, b=2.5%, on iter 058's saved stream (σ_annual ≈ 5.5%):

- **Sharpe drag** = (lev-1)×(b-rf)/(lev×σ_annual) =
  0.5×0.005/(1.5×0.055) ≈ **0.030**.
- **Levered Sharpe** = 1.222-0.030, 1.347-0.030, 1.403-0.030
  ≈ 1.19, 1.32, 1.37 (all 3 ≥ bench+0.10) → **c1 = 25 pts**.
- **DSR p** estimate: edu 0.0494 + ~0.020 ≈ 0.07; spy 0.0337 + 0.020 ≈
  0.054; ndx 0.0258 + 0.020 ≈ 0.046 — worst-p ~0.07 → **c3 = 10 pts**.
- **G2** fails on edu (p>0.05), borderline on spy/ndx. Conservatively
  6/7 each. **c2 = 5+5+5+4 = 19** (cross-ds bonus).
- **CAGR**: edu 1.5×0.0869 - 0.5×0.025 - geo_drag ≈ 11.7%; spy ≈
  12.2%; ndx ≈ 12.6%. Floor pass: edu ✓ (>9.18), spy ✓ (>11.98), ndx
  ✗ (<15.35). 2/3 → **c4 = 10 pts**.
- **MDD**: 16.74×1.5 ≈ 25%, 13.71×1.5 ≈ 21%, 13.12×1.5 ≈ 20%. All
  3 under ceilings. → **c5 = 15 pts**.
- **Robustness**: assume 9/9 sub-windows positive (iter 058 had this).
  → **c6 = 5 pts**.
- **Total predicted**: 25 + 19 + 10 + 10 + 15 + 5 = **84 STRONG**.

Path to WINNER (90+) at this lev/borrow: structurally infeasible
because clearing ndx CAGR floor 15.35% requires lev≥1.66× which adds
~0.040 Sharpe drag, pushing DSR worst-p past 0.10 and dropping c3 to
5 pts (net Δ −5 = score 79).

The iteration is informative regardless of outcome: characterizes the
leverage frontier on iter 058 at futures-rate borrow.
