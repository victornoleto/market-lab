# Hypothesis — Iter 002: Fixed-Param Global Momentum (K=2, lb=6m)

**Date**: 2026-04-26  
**Slug**: fixed-momentum-k2-lb6  
**Iteration #**: 002

---

## Hypothesis

Iter 001 identified global cross-sectional momentum (multi-asset top-K) as a
STRONG (81/100) strategy that meets all 5 strict winner conditions but falls
short of the 90-point threshold for WINNER. The gap is purely methodological:
with 9 configs in the grid, G1 PBO fails on educational (PBO=0.74, selection
bias from lb=3 configs). Meanwhile, the 32-year long-window analysis showed
that k=2, lb=6m is the most robust canonical config — Sharpe 1.001, CAGR
13.22%, MDD 21.23%, dominating V_HYBRID+MF on all three dimensions.

**Hypothesis**: Pre-committing to a single config (K=2, lookback=6m) before
seeing the data eliminates selection bias entirely. With no grid search,
PBO is inapplicable (n_configs=1 < MIN_HONEST_N_CONFIGS=4), all 7 gates
should pass on all 3 datasets, and the robustness bonus becomes computable
via rolling-window Sharpe consistency.

**Same mechanism as iter 001; different methodology**: cross-sectional
momentum across global multi-asset universe (VTISIM/VEASIM/VXUSSIM/IEFSIM
core; +VWOSIM/GLDSIM for vt_real and ndx_real). Equal-weight top-2 by
trailing 6-month return. CASHX safe haven when all assets negative.

---

## Primary citation

`[stocks_on_the_move, p.21-30]` — Clenow documents cross-sectional momentum
in ETF universes with pre-committed lookback and top-K parameters. The
6-month lookback is canonical in the cross-asset momentum literature (also
`[stocks_on_the_move, p.21-30]`: 6-12m lookback avoids 1-month reversal
and 36m+ mean-reversion zones).

---

## Edge source

What does VT / Plano C V3_1 / V_HYBRID+MF miss that this captures?

- **VT b&h** misses: momentum rotation to bonds/CASHX during drawdowns
  (MDD 50% VT vs 21% this strategy in edu window).
- **Plano C V3_1**: static factor tilt, no active rotation between asset
  classes based on trailing return signals.
- **V_HYBRID+MF**: targets a different edge (capital efficiency + managed
  futures), no cross-sectional momentum rotation.

This strategy adds an active **inter-asset-class rotation signal** that is
structurally orthogonal to factor tilts and capital efficiency.

---

## Pre-committed kill criteria

1. **Sharpe kill**: If educational Sharpe < 0.7626 → fixed params don't
   generate edge; discard direction (fixed-param momentum is a dead-end).
2. **Stability kill**: If rolling-window positive-Sharpe % < 60% on
   educational (56y data, 5-year windows) → strategy is regime-dependent
   in a way incompatible with deployment; flag as structural dead-end.
3. **Neither triggered** → continue to full gate battery.

---

## Datasets

Same as iter 001:
- **educational**: VTISIM/VEASIM/VXUSSIM/IEFSIM + CASHX, 1970-2026 (56y)
- **vt_real**: VTISIM/VEASIM/VWOSIM/IEFSIM/GLDSIM + CASHX, 2008-06 to 2026-04
- **ndx_real**: Same universe as vt_real, 2010-02 to 2026-04

Benchmark: VTSIM b&h (edu/vt_real); QQQSIM b&h (ndx_real).

---

## Expected budget

- **Configs**: 1 per dataset (single pre-committed config = no grid)
- **n_trials for DSR**: 1 per dataset
- **Wall-time**: ~10 min (single config is ~9× faster than iter 001)

---

## Expected score trajectory (pre-committed)

| criterion | iter 001 | iter 002 (expected) |
|---|---|---|
| Sharpe edge | 20/25 | 20/25 (ndx_real structural ceiling) |
| Gate pass | 21/25 (edu G1 fails) | **25/25** (single config → G1 trivial) |
| DSR | 15/15 | 15/15 (n_trials=1 → near-zero p) |
| CAGR floor | 10/15 | 10/15 (ndx_real structural ceiling) |
| MDD ceiling | 15/15 | 15/15 |
| Robustness bonus | 0/5 | **5/5** (rolling-window computed) |
| **Total** | **81** | **90** → WINNER? |

---

## Implementation plan

1. Reuse `simulate_momentum_portfolio` + `simulate_momentum_numpy` from
   iter 001's `backtest.py` (copy with single-config wrapper).
2. No grid loop — single `(k=2, lb=6)` call per dataset.
3. G1 PBO: skip (n_configs=1 → auto-pass, return `(True, 0.0)`).
4. **Rolling-window robustness** (new): 5-year sliding windows (step=1y)
   on educational dataset. Count % of windows with positive Sharpe.
   ≥ 90% → 5 pts; ≥ 75% → 3 pts; ≥ 60% → 1 pt; < 60% → 0 pts.
5. Pass `robustness_bonus` to modified `score_strategy()`.
6. Save `results.json` with `returns_series` in plot_helper format.
