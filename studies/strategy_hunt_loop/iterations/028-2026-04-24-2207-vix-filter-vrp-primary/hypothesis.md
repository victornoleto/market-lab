# Iteration 028 — VIX-filter VRP-primary (V-3): only OPEN credit-spread when VIX < 35

## Hypothesis

Iter 026 demonstrated that a stand-alone VRP harvester (T-bill collateral
+ short 5/10% OTM put-credit spread, 21-DTE, monthly roll) delivers
+0.38–0.45 Sharpe alpha cross-dataset and the **first-ever DSR PASS**
(`ndx_real` p=0.0376) — but worst-p across datasets stays at 0.083, so
the strict winner gate (p<0.05 cross-dataset) misses by ~0.03 on
educational. Iter 027 then proved that **simple leverage cannot close
the gap**: linearly scaling the harvest dilutes the rf-bonus and
collapses both Sharpe and DSR.

The path forward is therefore to **lift the harvest's intrinsic
`overlay_sharpe`** (currently 0.67 / 0.77 / 0.93 edu/spy/ndx) — the
component that **survives** under leverage and that drives DSR via the
realised Sharpe of the underlying signal.

This iteration adds **one binary regime gate** straight from
Sinclair's `[volatility_trading, p.217]`:

> **Open new put-credit-spread positions only when `VIX < 35`.**
> If `VIX ≥ 35` at the natural roll bar, **skip the open** and earn
> `rf_daily` until the next scheduled roll bar. Existing positions
> continue to expiry as before (no premature close).

The mechanism: high-VIX opens correspond to spreads written **into**
realised-vol regime shifts (2008-Q4, 2020-Q1, 2022 mini-spikes). The
short-writer's cap (≈ 4-4.5% per roll) is most likely to be hit
**from a high-VIX open** because the implied↔realised gap can flip sign
when realised vol is already shocked. Filtering removes the worst tail
losses **without** sacrificing many positive carry rolls — VIX ≥ 35
historically covers only **2.4 % – 4.9 %** of bars across the three
datasets.

## Primary citation

`[volatility_trading, p.217]` — Sinclair (2013) "Volatility Trading"
ch. 8 (Hedging) §"Hedging short volatility positions" recommends a
**VIX < 35 entry filter** for short index-option strategies, citing the
asymmetric tail-loss risk of writing premium into a high-IV regime.

## Additional citations

- `[volatility_trading, ch.3]` — VRP mechanics (the harvest signal
  itself, unchanged from iter 026).
- `[volatility_trading, p.41]` — SPX excess kurtosis 21.3 → tail
  truncation rationale (the cap that the filter aims to keep
  unbreached).
- `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials`.
- Web: **Bondarenko, O. (2014). "Why Are Put Options So Expensive?"**
  *Quarterly Journal of Finance* 4(3): 1450015.
  DOI: 10.1142/S2010139214500153 — documents that VRP harvest
  Sharpe is regime-dependent and that **conditioning on low-IV
  regimes** lifts the per-trade Sharpe (their Table 3:
  high-IV-regime puts have lower realised Sharpe than low-IV-regime
  puts on capped spreads).
- Web: **Carr, P. & Wu, L. (2009). "Variance Risk Premiums."**
  *Review of Financial Studies* 22(3): 1311-1341.
  DOI: 10.1093/rfs/hhn038 — establishes the IV-regime-dependence of
  realised VRP; the implied↔realised gap is wider in low-IV regimes.

## Edge source

SPY 1× buy-and-hold sells nothing; iter 026's stand-alone VRP harvest
already captured the unconditional implied-vs-realised gap. **This
iteration captures the conditional gap**: the additional alpha from
*not writing premium when realised-vol is already shocked*. The signal
is uncorrelated with SPY direction (the filter activates on
volatility-of-volatility, not price drawdown), so the diversification
property of iter 026 is preserved.

## Datasets

- **educational** (SPY+VIX 2006-01-03 → 2026-04-14, 5130 bars,
  iter-020-aligned): contains 2008-09 GFC (VIX ≥ 35 covers ~5 % of
  bars) — the strongest filter-test regime; Q1 2020 + 2022 are also
  included.
- **spy_real** (SPY+VIX 2009-06-25 → 2026-04-14, 4255 bars, post-GFC):
  filter triggers ~2.4 % of bars (mostly 2020-Q1 + 2022). Tests whether
  the filter still adds value when 2008 is excluded — i.e., whether
  the V-3 lift is structural or 2008-specific.
- **ndx_real** (QQQ+VIX×1.1 2010-02-12 → 2026-04-14, 4095 bars):
  filter triggers ~2.5 % of bars; tests whether the IV-scale-1.1
  adjustment for tech-heavy NDX preserves the filter's effect.

The same windows as iter 026 are used so the comparison is direct.

## Kill criteria (pre-committed)

If any of the following triggers, the V-3 hypothesis is falsified
(regardless of how other metrics behave):

- **Kill A**: Sharpe regresses by **> 0.05** vs iter 026 on **≥ 2 / 3**
  datasets. The filter is supposed to lift `overlay_sharpe`, not lower
  total Sharpe; a negative move on most datasets means the filter is
  either too aggressive (cuts profitable rolls) or wrong sign (filters
  the wrong regime).
- **Kill B**: filter triggers in **< 0.5 % of opens** on ≥ 2 / 3
  datasets. This would mean the threshold is so loose that the
  filter is functionally vacuous (effectively iter 026), and the
  iteration provides no new evidence.
- **Kill C**: 21-day worst loss exceeds **30 %** on any dataset (same
  Kill B as iter 027 — catastrophic per-cycle risk; iter 026 had
  worst -7.45 / -4.86 / -5.72 %).
- **Kill D**: G7 cross-lib CAGR Δ **> 3 pp** on any dataset (engine
  dirty; ±3 pp is the standing G7 threshold).

Each of these is checked in `compute_gates_and_score.py` and reported
in `verdict.json["kill_criteria"]`.

## Expected budget

- Configs to test: **1** (single pre-committed cfg `vrp_primary_vix35_h1_5_10_1m`).
  No grid, no sweep, no post-hoc selection.
- Cumulative `n_trials` advance: **4280 → 4281 (+1)**.
- Wall-time: ~2-4 minutes per dataset (BS pricer + filter loop, same
  scale as iter 026/027).
- Files to create:
  1. `vrp_filtered.py` — pandas engine adding VIX<threshold filter
     gate to `compute_vrp_primary_returns`.
  2. `numpy_reference_filtered.py` — pure-numpy reference for G7.
  3. `run_backtests.py` — runner across 3 datasets.
  4. `compute_gates_and_score.py` — 7-gate battery + scoring (mirrors
     iter 026/027 structure exactly).
  5. `tests/test_iter028_vix_filter.py` — TDD spec (checks: filter
     skips opens at VIX≥35, threshold = 35 deterministic, parity vs
     iter 026 when threshold = ∞, cross-lib parity to 1e-12).
  6. `results.json`, `verdict.json`, `final_report.md`,
     `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`.

## Implementation plan

1. **TDD spec** (`tests/test_iter028_vix_filter.py`) — write 4 tests
   FIRST:
   - `test_filter_off_at_high_threshold_matches_iter026` — when
     `vix_threshold = 1e9`, the engine must reproduce iter 026 exactly
     (every roll opens unfiltered, returns identical to 1e-12).
   - `test_filter_skips_open_when_vix_above_threshold` — synthetic
     scenario where VIX is forced ≥ threshold at a roll bar; the bar's
     return should be `rf_daily` (no spread P&L) and the next roll
     bar should re-evaluate.
   - `test_iter028_vix_filter_pandas_numpy_parity_iter026_window` —
     pandas vs numpy engine on real iter 026 SPY+VIX window must
     differ by < 1e-12 in maximum return.
   - `test_iter028_filter_reduces_worst_21d_vs_iter026` — on the
     iter 026 spy_real window, `vrp_filtered` 21-day rolling worst must
     be ≤ `vrp_primary` 21-day rolling worst (filter cannot make tail
     loss worse — sanity check on the mechanism's sign).

2. **Implement `vrp_filtered.py`** — add a `vix_threshold: float`
   parameter (default `35.0`) to a new `compute_vrp_filtered_returns`.
   Logic: at each natural roll bar `i`, if `vix[i] >= vix_threshold`,
   skip the open, set `prev_value = 0`, and the next `dte_days`
   bars deliver `rf_daily` only (no MtM stream because no position is
   held). Re-evaluate at the next scheduled roll bar.

3. **Implement `numpy_reference_filtered.py`** — exact numpy mirror.

4. **Run on 3 datasets**, save full `results.json` with
   `returns_series` for the Stage 5 plot helper.

5. **G7 cross-lib check**: 0.0000 pp expected (deterministic engine).

6. **Compute 7-gate battery + scoring** identical to iter 026
   (`compute_gates_and_score.py`); cumulative `n_trials = 4281`.

7. **Generate plots** via `plot_helper.py --iter 028`.

8. **Final report** with score breakdown, score regression vs
   iter 026, and the **structural finding** (whether the VIX filter
   lifts `overlay_sharpe` and DSR p as predicted, or — if Kill A
   triggers — what that says about Sinclair's rule on the
   capped-spread variant of his framework).

## Why iter 028 is structurally novel vs all DEAD_ENDS entries

The closest DEAD_ENDS entry is iter 019 (HMM ρ stock-bond regime, pre-val
rejected because ρ enters σ²_port as a cross-term). Iter 028 differs:

- **No σ²_port absorber**: iter 026 (the base) has no equity stack,
  no vol-target wrapper. The only state is T-bill + 1 short put-spread.
  The filter affects the harvest SIGNAL directly, not a hedge-overlay
  on a vol-managed portfolio.
- **VIX as absolute IV regime, not relative ρ**: the filter conditions
  on the absolute level of implied vol (the input the strategy is
  pricing against), not on a derived correlation that cointegrates with
  σ²_port.
- **Binary on/off, not continuous tilt**: the iter 019 dead-end was
  about *modulating* a vol-managed weight via ρ_z; iter 028 is **gate
  on / gate off** for a discrete entry decision. A single threshold,
  not a continuous transformation.
- **Sinclair-anchored rule, not data-mined**: VIX = 35 is the exact
  threshold from `[volatility_trading, p.217]`. Not optimised on this
  dataset. There is no parameter sweep — one cfg, one threshold,
  pre-committed.

Iter 028 is also distinct from iter 020/021/022/027 closures (those
are about the equity-leg vol-target absorption family — none of them
test a regime gate on the harvest itself).
