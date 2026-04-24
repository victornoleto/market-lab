# Iteration 012 — Asymmetric T10Y3M equity-leg-only haircut overlay on iter 008 daily blend (Option B')

## Hypothesis

Apply a binary macro-regime haircut on top of iter 008's daily
vol-managed SPY+TLT blend (`vt15_L21_cap20`) using the canonical 10Y−3M
Treasury yield-curve spread (T10Y3M). **Two structural distinctions vs
iter 009 (dead-end)**:

1. **Light smoothing (5-day EMA)** — not 21-day. The 21d EMA in iter 009
   lagged by ~1 month and destroyed the 6-18 month recession lead-time
   that is the indicator's entire value. At 5-day EMA the zero-crossing
   count drops from 958 (raw, 22/yr flicker) to 44 over the same 44-year
   window (~1/yr episodes) — still ~1 episode per business cycle, so
   lead-time is preserved while execution-noise is controlled.

2. **Asymmetric haircut (equity leg ONLY)** — not symmetric. During
   inversion the SPY leg is halved (0.5×); the TLT leg keeps full
   weight. Rationale: SPY-TLT correlation ≈ −0.30 means TLT typically
   *rallies* during recession (flight-to-quality), so a symmetric
   haircut — as in iter 009 — forfeits exactly that rally. Keeping the
   bond leg unhalved captures the yield-curve's canonical "bond wins
   when stocks lose" dynamic.

Single pre-committed configuration `vt15_L21_cap20 × ts_inv5_h50_eq`;
NO grid, NO parameter sweep.

## Primary citation

`[regime_change, p.5-6, ch.2]` — regime-change principle: observable
statistical shifts (volatility, correlation) that characterise
transition between "normal" and "abnormal" market states; T10Y3M
inversion is a canonical macroeconomic regime-change proxy.

## Additional citations

- `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure de-lever
  (haircut = 0.5 is Carver's canonical tier-2 response).
- `[risk_parity, p.10-11, ch.1]` + `[risk_parity, p.80-81, ch.4]` —
  naïve risk parity base weighting; negative SPY-TLT correlation is the
  diversification axis that the asymmetric (equity-only) haircut
  deliberately preserves.
- `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag; extended here to macro
  series T10Y3M_{t-1} (no look-ahead).
- `[advances_fin_ml, p.208-211]` — G1 PBO N=1 vacuous-PASS.
- `[advances_fin_ml, p.222-223]` — G2 DSR deflator with cumulative
  n_trials.
- `[advances_fin_ml, p.31-34]` — G7 cross-lib ±3 pp CAGR parity (numpy
  reference mandated since new gate-logic introduced).
- Moreira & Muir (2017), *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://doi.org/10.1111/jofi.12513) — variance-
  scaling form applied portfolio-level.
- Estrella & Mishkin (1998), *Review of Economics and Statistics* 80(1),
  45-61. DOI
  [10.1162/003465398557320](https://doi.org/10.1162/003465398557320) —
  10Y−3M spread as canonical recession leading indicator, 6-18 month
  lead.
- Estrella & Hardouvelis (1991), *Journal of Finance* 46(2), 555-576.
  DOI
  [10.1111/j.1540-6261.1991.tb02674.x](https://doi.org/10.1111/j.1540-6261.1991.tb02674.x)
  — earlier establishment of term-spread predictive power for real
  activity.

## Edge source

What SPY 1× buy-hold (Sharpe 0.90 on spy_real) fails to capture: **it
does not de-lever equity exposure ahead of recession regimes**. This
strategy combines (a) iter 008's vol-adaptive diversified base (already
Sharpe ~1.00) with (b) an *orthogonal* macro signal that fires **before
realized vol spikes** (T10Y3M leads recession by 6-18 months) and
halves **only the equity** leg while keeping bond flight-to-quality
exposure intact. The iter 009 diagnostic (100% gate-fire/bottom-20%-
scale overlap on edu+spy) showed the 21d-smoothed signal was redundant
with variance-scaling; a 5d-smoothed signal must fire **earlier than
realized vol acceleration** for the overlay to contribute new
information.

## Datasets

- **educational (SPYSIM/SPY+TLT 24y, 2002-07-26 → 2026-04-15)** —
  broadest window covering 2008 GFC + 2020 COVID + 2022 rate cycle;
  best window for observing multiple T10Y3M inversion-recovery cycles.
- **spy_real (SPY+TLT 17y, 2009-06-25 → 2026-04-15)** — benchmark
  window; covers 2019 and 2022-2024 inversions.
- **ndx_real (QQQ+TLT 16y, 2010-02-12 → 2026-04-15)** — tech-heavy
  equity leg; tests whether the macro regime signal transfers to a
  universe already near its buy-hold Sharpe ceiling.

## Kill criteria (pre-committed, binding — no post-hoc rationalisation)

**Kill #1 — Thesis falsification**: if Sharpe regresses vs iter 008
(base blend without overlay) on **BOTH** real-data slots (spy_real Δ
< 0 AND ndx_real Δ < 0), the asymmetric-equity-only-haircut principle
is empirically falsified. The remaining Option B'' quadrants (haircut
= 0.3, threshold ≠ 0, 3d smoothing) are inside the same dead-end
pattern and must not be re-tested.

**Kill #2 — CAGR collapse**: any dataset's CAGR falls below 0.75 ×
benchmark (stricter than winner-gate 0.8 × for clearer signal).

**Kill #3 — Score < 70**: if `score_strategy` returns < 70, the direction
is "done" for the iter 008 blend-mechanism family, with no further
minor variations justified.

**Kill #4 — Signal redundancy metric**: if the overlap between
gate-fire bars and bottom-20% blend-scale bars is ≥ 60% on any dataset,
the 5d signal is STILL redundant with variance-scaling (iter 009 had
100% overlap on edu+spy); overlay information is not orthogonal enough
to compound. This is the technical version of Kill #1.

**Kill #5 — Cross-lib > 3 pp CAGR** (G7 non-negotiable on new
simulator logic).

## Expected budget

- **Configs tested this iteration**: 1 (single ex-ante pre-committed
  cfg; blend_cfg × overlay_cfg fixed).
- **Trials added to `cumulative_n_trials`**: 1 cfg × 3 datasets = 3.
  4249 → **4252**.
- **Wall-time**: ~45-60 min total (8 min for impl + TDD, 10 min for
  backtests on 3 datasets, 20 min for 7-gate battery, 10 min for
  final_report + memory update).
- **Files to create**:
  - `asymmetric_term_spread_overlay.py` — main simulator module.
  - `overlay_numpy_reference.py` — hand-rolled numpy parity for G7.
  - `run_backtests.py` — driver for 3 datasets.
  - `compute_gates_and_score.py` — gate battery + scoring wrapper.
  - `results.json`, `verdict.json`, `final_report.md`.
  - `tests/test_asymmetric_term_spread_overlay.py` — TDD specs for new
    asymmetric-gate logic.

## Implementation plan

1. **TDD specs first** (`tests/test_asymmetric_term_spread_overlay.py`,
   ~5 tests): (a) gate = 1.0 when ts > threshold, (b) SPY leg halved
   when ts ≤ threshold, TLT leg UNCHANGED, (c) lag prevents
   look-ahead (shift by 1 before EMA), (d) 5-day EMA applied after
   lag, (e) degenerate case haircut=1.0 reduces to iter 008 blend
   exactly.
2. **Implement `asymmetric_term_spread_overlay.py`** — reuses iter 006
   `apply_blend_variance_target` via sys.path import, adds thin wrapper
   that post-multiplies `pos_spy` only (not `pos_tlt`) by the gate.
3. **Implement `overlay_numpy_reference.py`** — hand-rolled numpy-only
   implementation, no pandas dependency for the core loop. Parity
   target ±3 pp CAGR vs the main simulator.
4. **Run backtests on 3 datasets** — produce `results.json` with per-
   dataset Sharpe/CAGR/MDD + gate diagnostics (fire rate, bottom-20%
   overlap, gate-scale correlation).
5. **Run 7-gate battery** — G1 PBO (N=1 vacuous PASS), G2 DSR with
   cumulative n_trials=4252, G3 WF 6/8 per dataset, G4 OOS 70/30, G5
   FWD post-2020, G6 bootstrap 99.9% CI, G7 cross-lib ±3 pp.
6. **Score + tier** via `scoring.score_strategy()` with the 3 dataset
   metric bundles + 3 gate bundles + cumulative n_trials=4252.
7. **Final report** with score breakdown, diagnostics, kill-criterion
   table, and next-iteration suggestions.

## Pre-committed configuration (exact params)

```python
BLEND_CFG = {
    "cfg_id": "vt15_L21_cap20",      # inherits iter 008 exactly
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
}

OVERLAY_CFG = {
    "cfg_id": "ts_inv5_h50_eq",      # 5d EMA + inversion + haircut 0.5 + equity-only
    "indicator": "t10y3m_daily",
    "smoothing_window": 5,           # 5-day EMA — preserves 6-18m lead
                                     # (iter 009 used 21d — dead-end)
    "threshold": 0.0,                # classical yield-curve inversion
    "haircut": 0.5,                  # [systematic_trading, p.144] tier-2
    "applied_to": "equity",          # EQUITY LEG ONLY — iter 009 used
                                     # both (symmetric), dead-end
    "lag_bars": 1,                   # no look-ahead
}

COST_BPS_PER_LEG = 0.0002            # 2 bps per unit of per-leg position change
```

## What would make this iteration a winner vs a dead-end

**Winner path** (score ≥ 75 STRONG, ≥ 90 WINNER):
- Sharpe edge ≥ +0.10 on 2/3 datasets (iter 008 was 2/3, needs to maintain).
- Gate-fire/bottom-20% overlap < 50% on ≥ 2 datasets (orthogonality
  confirmed).
- DSR worst p falls below 0.20 (toward 0.10) — highest priority metric.
- MDD stable or reduced vs iter 008 (expected: equity-leg haircut
  during inversion saves ~2-3 pp MDD).

**Dead-end** (score < 60, Kill #1 or #4 triggered):
- Sharpe regresses on both real slots → asymmetric principle dead.
- Gate-fire/bottom-20% overlap ≥ 60% on 2+ datasets → 5d signal still
  redundant with variance-scaling; the raw-signal quadrant untested but
  likely worse (turnover explosion at 22/yr crossings); all T10Y3M
  overlay variants on this blend base must be archived as structural
  dead-ends and the loop must pivot to Option C (meta-labeling) or
  Option E (EBP overlay, different indicator).
