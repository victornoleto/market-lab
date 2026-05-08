# Hypothesis — Iter 004: Global Momentum + MF Sleeve

**Date**: 2026-04-27  
**Slug**: `momentum-mf-sleeve`  
**Direction consumed**: BASE_MEMORY `## Promising unexplored directions` — Tier 1, item 1b

---

## Hypothesis paragraph

The WINNER from iter 002 (K=2, lb=6m global cross-sectional momentum) scores 90/100
across all three datasets with 7/7 gates. Its only structural ceiling is the ndx_real
CAGR benchmark (QQQ 18.99% — structurally unreachable for a globally diversified
strategy). The hypothesis here is that adding a fixed 10% allocation to KMLMSIM
(managed futures) alongside the momentum signal produces a Pareto improvement:
Sharpe rises via diversification (MF is near-zero correlated with equity momentum in
crises) while MDD stays flat or falls. This mirrors the empirical result in
`deploy_studies` where adding 10% MF to V_HYBRID raised Sharpe from 0.709 → 0.743
with lower MDD. The portfolio rebalances monthly: 10% KMLMSIM always, 90% distributed
equal-weight among top-K positive-momentum assets (or CASHX when all signals negative).
Single pre-committed config (K=2, lb=6m), identical parameters to the iter 002 WINNER.

---

## Primary citation

`[trading_evolved, p.197]` — managed futures as "alternative risk premium":
uncorrelated with equity in tail events; adding an orthogonal return stream raises
portfolio Sharpe through diversification even when MF standalone Sharpe is lower.

`[stocks_on_the_move, p.21-30]` — Clenow pre-committed top-K lookback momentum,
canonical K=2 / lb=6m.

---

## Edge source

VT b&h: 100% passive cap-weighted, no trend filter.  
Plano C V3_1 v3.5: static factor-tilted (no dynamic signal), no MF diversification.  
V_HYBRID+MF: US-centric momentum rotation + 10% MF, no global multi-asset breadth.

This iter: **global** top-K momentum (4-5 assets across equity regions, bonds, gold)
+ permanent MF sleeve → combines trend-following breadth with uncorrelated diversifier
in a globally-diversified portfolio. Not tested in any prior iter or benchmark.

---

## Datasets to test

| dataset | window | universe | KMLM available? |
|---|---|---|---|
| educational | 1988-01-01 → 2026-04-24 (~38y) | VTISIM/VEASIM/VXUSSIM/IEFSIM | Yes (inception 1987-12-31) |
| vt_real | 2008-06-01 → 2026-04-24 (~17y) | VTISIM/VEASIM/VWOSIM/IEFSIM/GLDSIM | Yes |
| ndx_real | 2010-02-01 → 2026-04-24 (16y) | VTISIM/VEASIM/VWOSIM/IEFSIM/GLDSIM | Yes |

Note: educational window shortened from iter 002's 56y to ~38y because KMLMSIM
inception is 1987-12-31. The universe tickers for educational are unchanged from
iter 002 (they all predate 1988).

---

## Pre-committed kill criteria

**Falsifies the hypothesis**: portfolio Sharpe drops > 0.05 below iter 002 pure
momentum on BOTH educational AND vt_real simultaneously. That would indicate the
MF sleeve degrades rather than diversifies the return stream.

**Expected pre-kill to survive**: combined Sharpe stays within ±0.05 of iter 002
values, with lower or equal MDD. Diversification argument holds if this condition
is met.

---

## Implementation plan

1. Create `backtest.py` based on iter 002 code:
   - Add `KMLM_WEIGHT = 0.10`, `MOMENTUM_WEIGHT = 0.90`
   - `simulate_momentum_mf_sleeve()`: same monthly top-K logic, but weights are
     KMLM_WEIGHT to KMLMSIM + MOMENTUM_WEIGHT distributed to top-K (or CASHX)
   - `simulate_momentum_mf_numpy()`: cross-lib reference with KMLM blended in
   - Update `DATASETS["educational"]["start"]` to `"1988-01-01"` (KMLMSIM binding)
2. Run all 3 datasets, collect metrics and gate results
3. Score via `scoring.py` with `cumulative_n_trials=21` (20 + 1 this iter)
4. Save `results.json` + `verdict.json`
5. Generate plots via `plot_helper.py --iter 004`

---

## Expected budget

- Configs: 1 (pre-committed, no grid)
- Wall-time: ~10-15 min (3 datasets, 1 config, no expensive cross-validation)
- cumulative_n_trials after this iter: 21

---

## Citations

- `[trading_evolved, p.197]` — MF free lunch, uncorrelated return
- `[stocks_on_the_move, p.21-30]` — momentum mechanism and K/lb parameters
- `[advances_fin_ml, p.208-211]` — PBO: N/A with single pre-committed config
- `[advances_fin_ml, p.222-223]` — DSR with n_trials=1
- `[advances_fin_ml, p.196-202]` — Bootstrap CI
- `[advances_fin_ml, p.31-34]` — Cross-lib ±3pp CAGR parity
