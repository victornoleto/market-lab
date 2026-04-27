# Hypothesis — Iter 001: Global Multi-Asset Top-K Momentum

**Date**: 2026-04-26  
**Slug**: `global-momentum-topk`  
**Source direction**: BASE_MEMORY.md Tier 1, direction #4

---

## Hypothesis

Monthly cross-sectional momentum applied to a global multi-asset universe
(US equity, Intl Developed equity, EM equity, 7-10y bonds, gold) improves
annualized Sharpe ratio and reduces MDD vs VT buy-and-hold by dynamically
concentrating into the top-K momentum winners and rotating to T-bills
when all assets trend negative.

**Rule**: At each month-end, compute trailing N-month total return for every
asset in the universe. Equal-weight the top-K assets with positive momentum.
If no asset has positive momentum (all negative), hold 100% CASHX.

This is the simplest possible version of the mechanism — no leverage, no
factor overlays, no machine learning.

---

## Primary citation

- `[stocks_on_the_move, p.21-30]` — Clenow's cross-sectional 52-week momentum
  rule applied to ETFs; shows sustained Sharpe improvement over B&H via
  momentum selection + cash rotation.
- `[stocks_on_the_move, p.21-30]` — cross-asset momentum documented as
  one of the most robust alternative risk premia; works across equities,
  bonds, commodities, and currencies.

---

## Edge source

VT b&h, Plano C V3_1 v3.5, and V_HYBRID+MF all hold **static** weights
(or at most a fixed leverage ratio). None dynamically excludes asset classes
with negative trailing price trend. The momentum filter should:
1. **Reduce MDD**: rotation to CASHX avoids holding through multi-year bear
   markets (e.g., 2000-2002, 2008-2009, 2022).
2. **Improve Sharpe**: concentrating in trending assets avoids low-return
   diversifiers during their downtrends.

---

## Datasets to test

| dataset | window | universe | safe_haven |
|---|---|---|---|
| educational | 1970-2026 (56y) | VTISIM, VEASIM, VXUSSIM, IEFSIM | CASHX |
| vt_real | 2008-2026 (~17y) | VTISIM, VEASIM, VWOSIM, IEFSIM, GLDSIM | CASHX |
| ndx_real | 2010-2026 (16y) | VTISIM, VEASIM, VWOSIM, IEFSIM, GLDSIM | CASHX |

**Educational limitation**: GLDSIM starts 1986, VWOSIM starts 1994 — both
excluded from the educational universe to preserve the full 56y window.
IEFSIM starts 1962, CASHX starts 1885 — both available.

**Note**: ndx_real uses the same universe as vt_real but compares against
QQQ b&h (Sharpe 0.9472). A global diversified momentum strategy is
unlikely to beat QQQ Sharpe over this growth-dominated window; winner
status requires beating on ≥ 2/3 datasets.

---

## Configuration grid

| dimension | values |
|---|---|
| K (top-K assets) | 1, 2, 3 |
| lookback (months) | 3, 6, 12 |

Grid size: 3 × 3 = **9 configs per dataset** (same K/lookback applied
to each dataset's universe).  
Total unique configs: 9 (educational core) + 9 (full 5-asset, applied
to vt_real + ndx_real) = **18 configs**, but DSR counts 9 per dataset
(the hyperparameter space for that dataset class).

---

## Pre-committed kill criteria

1. Best (K=2, lookback=12m) config on educational FAILS to beat VTSIM
   Sharpe (0.6626) → mechanism adds no value in this universe → abandon
   direction #4 entirely.
2. PBO > 0.5 on all three datasets simultaneously → evidence of pure
   overfitting, no real edge.

---

## Expected budget

- Configs: 9 per dataset × 3 datasets = 27 backtests  
- Wall-time: ~10-20 min (monthly signal, daily portfolio construction, fast)
- Gate battery: ~15-20 min (PBO CSCV, DSR, WF, OOS, FWD, Bootstrap, G7)
- Total: ~35-40 min (well within 90 min budget)

---

## Implementation plan

1. `backtest.py` — single self-contained script:
   - Load testfolio parquet via `testfolio_loader`
   - Implement `momentum_portfolio(prices, universe, safe_haven, k, lookback)` → daily returns
   - Implement numpy cross-lib reference for G7
   - Run 9-config grid per dataset
   - Run 7-gate battery using existing validation modules
   - Score via `studies/global_factor_tilt_loop/scoring.py`
   - Save `results.json`, `verdict.json`

2. **No new modules needed** — reuses testfolio loader, performance
   metrics, PBO, DSR, walk_forward from existing infra.

3. **TDD**: No new modules → no new test file required. Pytest baseline
   (461) must stay green; will verify before finalizing.
