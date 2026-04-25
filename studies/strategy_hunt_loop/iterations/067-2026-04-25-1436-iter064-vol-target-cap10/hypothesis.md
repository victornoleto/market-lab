# Iteration 067 — Moreira-Muir variance-targeting overlay on iter 064 saved stream (cap ≤ 1.0, σ_target = σ_064)

## Hypothesis

Take iter 064's saved combined return stream (the current TOP-K #1
strategy: 0.9 × iter_046 + 0.1 × QQQ_200d_trend, score 90 STRONG,
0/7 KILLS) and wrap it with the **Moreira-Muir (2017)** σ⁻²
variance-targeting overlay using the saturated composite's own
realized rolling variance:

> r_strategy[t] = scale[t] · r_064[t]  −  cost_bps · |scale[t] − scale[t-1]|
>
> σ̂²_064[t-1] = (rolling-21-day std of r_064)² × 252,  shifted by 1 bar
>
> scale[t]    = clip( σ_target² / σ̂²_064[t-1], 0, **cap** )
>
> σ_target    = annualised σ of r_064 over the dataset window (constant per ds)
>
> **cap = 1.0** (no leverage)

The cap is the critical structural choice. With cap = 1.0:

- **Calm bars** (σ̂_064[t-1] < σ_target) → scale would call for > 1
  but is capped at 1.0; effectively **NO leverage upside**.
- **Stress bars** (σ̂_064[t-1] > σ_target) → scale < 1.0; the
  strategy **de-risks**, reducing exposure proportional to σ_target² / σ̂².

This is a **one-sided Moreira-Muir** — captures only the de-risk side
of the σ⁻² scaling. iter 016 (60:40 × MM, scored 79) and iter 040
(VRP basket × MM, scored 79) used `max_lev` ≥ 2.0; iter 067 uses
`max_lev = 1.0`, which is structurally NEW: not "vol-target with
allowance for leverage" but "vol-cap with leverage forbidden".

The mechanism: iter 064's composite has measured σ_ann ≈ 7.3-7.7% but
exhibits **conditional variance clustering** — calm regimes (e.g.
2017, 2021Q1) cluster at σ̂ ≈ 5%; stress regimes (e.g. 2020Q1, 2022)
cluster at σ̂ ≈ 12-15%. By cutting exposure when σ̂ > σ_target, the
overlay removes the right tail of the realised return distribution
without adding leverage to the left tail. Moreira & Muir (2017) §IV
proves the Sharpe-lever property holds for ANY return stream whose
conditional variance is autocorrelated.

**iter 064 is already a Markowitz-saturated composite** — its
stream's mean reverts to its full-sample annualised σ ~7.5%, but has
periods where σ̂ ranges 4-15%. The σ⁻² overlay is structurally
orthogonal to the closed axes:

- saved-stream-pair recombination (045/051/052/053): linear convex combos
- internal LETF substitution (062/063): asset-level leverage substitution
- output VIX gate (048): binary VIX ON/OFF
- calm-conditional ext lev (065): asymmetric +leverage (opposite of cap=1.0)
- bar-level RF meta-label (066): 1-day-sign binary classification

iter 067 is the FIRST overlay on iter 064 that uses the **dynamics of
iter_064's own variance** as the only signal, without leverage and
without external regime indicators (VIX/T10Y3M/etc.). It tests
specifically whether the **autocorrelation of conditional variance**
in the saturated composite is exploitable as a Sharpe lever.

## Primary citation

`[volatility_trading, p.218]` — Sinclair (2013), *Volatility Trading*
2nd ed., Wiley — variance-target sizing in vol harvesting; canonical
σ⁻² scaling rule.

**+ Moreira & Muir (2017)**, *Journal of Finance* 72(4): 1611-1644.
DOI 10.1111/jofi.12513. "Volatility-Managed Portfolios" — the
canonical MM 2017 paper; Table 4 reports +0.10 to +0.30 Sharpe gain on
equity vol-managed (with leverage). With cap = 1.0 we expect roughly
**half** that — the de-risk side carries most of the Sharpe-protective
benefit per Moreira-Muir Figure 3.

## Additional citations

- `[advances_fin_ml, p.162-164]` — López de Prado: σ̂_{t-1} strict
  shift(1) (no look-ahead) for risk overlays.
- `[systematic_trading, p.40, ch.2]` — Carver volatility standardisation
  primitive.
- `[systematic_trading, p.170-171, ch.11]` — Carver IDM cap; we set
  max_lev = 1.0 (well below IDM ≤ 2.5).
- `[risk_parity, p.10-11, ch.1]` — naïve risk parity as the WITHOUT-
  overlay baseline (iter 064's structure preserved verbatim under cap).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
- Bondarenko (2014) *QJF* 4(3): 1450015 — variance autocorrelation in
  short-vol P&L (predictability rationale).

## Edge source

SPY 1x buy-hold pays the full conditional volatility every bar
including stress regimes (2008Q4, 2020Q1, 2022Q3). Iter 064 already
diversifies across 3 internal streams but has measured σ̂_064 swings
4-15% × the long-run mean. Cutting exposure proportional to σ_target²/σ̂²
when σ̂ > σ_target removes the right tail of bar-level variance —
which historically coincides with negatively-skewed return clusters —
without adding leverage to the left tail.

## Datasets

- **educational** (SPYSIM synth 40y, 5101 bars 2006-2026): tests the
  overlay across the 2008 GFC and 2020 COVID stress windows.
- **spy_real** (SPY/UPRO 17y, 4226 bars 2009-2026): tests post-GFC
  recovery + 2020 + 2022 stress.
- **ndx_real** (QQQ/TQQQ 16y, 4066 bars 2010-2026): tests tech-heavy
  variance autocorrelation, especially 2018Q4 / 2020 / 2022.

All 3 share iter 064's frozen benchmarks (SPYSIM, SPY, QQQ).

## Kill criteria (pre-committed, evaluated end of Stage 3)

| # | Criterion | Threshold |
|---|---|---|
| **A** | Sharpe regress vs iter 064 by ≥ 0.05 on ≥ 2 datasets | KILL |
| **B** | DSR worst-p (across 3 ds) > 0.10 | KILL |
| **C** | Total score < 79 (regression beyond PROMISING ceiling) | KILL |
| **D** | edu CAGR < 9.18% (loses iter 064's first-ever non-LETF unlock) | KILL |
| **E** | G7 cross-lib (pandas vs numpy) > 0.5 pp ΔCAGR on any ds | KILL (engine bug) |
| **F** | corr(iter_067, iter_064) > 0.995 on ≥ 2 ds (overlay no-op) | KILL (mechanism inert) |
| **G** | max(scale) > 1.0 + 1e-6 (cap violation, implementation bug) | KILL |
| **H** | mean(scale) ≥ 0.99 (overlay never binds — no de-risk happens) | KILL |

**A + B simultaneously firing falsifies the entire hypothesis.**
Failing only F or H means the cap is mis-tuned; failing only A means
the de-risk side doesn't generalise; failing only B means the t-stat
is hurt by cumulative n_trials despite Sharpe surviving.

## Expected budget

- Configs: **N = 1** pre-committed (`iter064_vt_cap10_lookback21_target_full`).
  cumulative_n_trials advance: 4336 → 4337.
- Wall-time estimate: ~30 minutes total (load saved stream, vectorised
  rolling, gate battery on small N).
- Files to create:
  - `variance_target_overlay.py` (pandas implementation)
  - `numpy_reference_iter067.py` (numpy reference for G7)
  - `tests/test_iter067_variance_target.py` (TDD; ≥ 8 tests)
  - `run_backtests.py` (load r_064, apply overlay, save results)
  - `compute_gates_and_score.py` (7-gate battery + scoring)
  - `final_report.md`, `verdict.json`
  - `plot_vs_benchmark_spy_real.png`, `plot_vs_benchmark_ndx_real.png`

## Implementation plan

1. **TDD**: write `tests/test_iter067_variance_target.py` first
   - shape/length parity
   - shift(1) no-peek property
   - cap = 1.0 strictly enforced (no scale > 1.0)
   - σ̂ → ∞ ⇒ scale → 0 (fully de-risk)
   - constant series (σ̂ = 0) ⇒ scale = cap (clamped)
   - cost flips proportional to |Δscale|
   - cross-lib pandas vs numpy parity ≤ 1e-9 per-bar
   - σ_target = σ(r_064) full-window when not overridden
2. Implement `variance_target_overlay.apply_variance_target_overlay`
3. Implement `numpy_reference_iter067.apply_variance_target_overlay_np`
4. Hook up `run_backtests.py` to load iter 064 stream and apply
5. Compute G1-G7 gates + score; produce `verdict.json`
6. Plot helper run
7. Final report + BASE_MEMORY update

## Predicted outcome

**Predicted tier**: 🥇 **STRONG (score 80-88)**.

Best-case path to STRONG/WINNER:
- Sharpe lifts +0.04-0.10 across 3 ds (de-risk benefit on autocorrelated
  variance) → criterion 1 ≥ 15 pts
- MDD drops 1-3 pp (cap=1.0 prevents leverage but de-risk in stress
  retains the full benefit) → criterion 5 stays at 15
- Friction cost ~3-8 pp over window from |Δscale| flips
- CAGR drops 0.5-1.5 pp from average exposure < 1.0 (likely loses edu
  floor unlock if drag > 0.3pp on edu where iter 064 has 9.49%)
- DSR: tighter t-stat helps if Sharpe rises > drag-cost; cumulative
  n_trials advances 4336 → 4337 (+0.02% penalty)

Worst-case path to MARGINAL/NEAR_FAIL:
- Conditional variance NOT autocorrelated enough on the saturated
  composite (already de-correlated) → scale moves randomly; friction
  drags Sharpe; KILL A+B fire (fall back into iter 066 territory).

iter 064 stays at 90 unless this passes 95+ AND winner_conditions.
