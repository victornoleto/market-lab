# Iter 016 — Hypothesis: B.5 — UMD (Fama-French momentum) overlay direto sobre iter 011

## Hypothesis (one paragraph)

After 4 consecutive failures (012/013/014/015) on the **size+value** and
**geographic-diversification** axes — all subordinate to iter 011 in the
2010-2026 US-large-cap regime — this iter pivots to a **structurally
different factor**: **UMD** (Up Minus Down, Fama-French academic momentum
factor, 1926-2026). UMD is **cross-sectional equity momentum**, structurally
distinct from value (VBRSIM) and geographic diversification (VXUSSIM/NTSI),
and historically had a **strong 2017-2024 run** when value lagged ("momentum
crash" recoveries 2009/2016/2020 aside). The hypothesis: a 10-25% UMD
overlay added to iter 011's NTSX+GDE+KMLM stack adds Sharpe via a third
distinct return source (after equity + crisis-alpha + duration), filling
the empty "factor" axis that the iter 013 VBRSIM tilt failed to deliver.

## Primary citation

- `[stocks_on_the_move, p.21-30]` — Clenow, *Stocks on the Move*: momentum
  premium ~7%/yr historical (cross-sectional equity momentum), low correlation
  to value factor.
- `[advances_fin_ml, ch.3]` — López de Prado: factor-based feature
  engineering, momentum as orthogonal premium.
- `[risk_parity, ch.2, p.37-41]` — Carlson: factor framework as
  diversifier vs traditional asset-class allocation.
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`.

## Edge source (1 sentence)

avg(SPY, VT) buy-hold misses **(a)** capital-efficient stacking (NTSX+GDE);
**(b)** managed-futures crisis-alpha (KMLM); AND **(c)** academic momentum
premium (UMD, ~7%/yr historical, structurally orthogonal to value).

## Datasets to test

- `lh_56y` — UMD+RF 1926+ available (full history, no splice needed).
  Effective window aligned with NTSX SPYSIM bottleneck 1986+.
- `vt_real` (2008-06+) — UMD live in this period; full data on all legs.
- `ndx_real` (2010-02+) — UMD live; full data.

## Pre-committed kill criteria

**KILL #1**: If best-of-grid loses iter 011 Sharpe (1.046/0.960/1.104) on
≥ 2 of 3 datasets, UMD-as-overlay is structurally subordinate. Closes the
"direct factor overlay" sub-direction; iter 017 (regime-gated factor) takes
priority.

**KILL #2**: If UMD weight monotonically reduces Sharpe across the grid on
≥ 2 datasets (10% > 15% > 20% > 25%), UMD is a return-cap, not a Sharpe-
enhancer in this stack. Same lesson as iter 014's VXUSSIM monotonic
finding.

## Configs (pre-committed grid)

All weights sum to 100%. UMD substitutes from the KMLM portion (preserving
the cap-efficient core NTSX+GDE):

| config | NTSX | GDE | KMLM | UMD | rationale |
|---|---:|---:|---:|---:|---|
| `umd_lite_3525_30_10`   | 35% | 25% | 30% | 10% | smallest UMD swap (KMLM 40→30, +10 UMD) |
| `umd_mod_3525_25_15`    | 35% | 25% | 25% | 15% | moderate (KMLM 40→25, +15 UMD) |
| `umd_balanced_3525_20_20` | 35% | 25% | 20% | 20% | UMD = KMLM, equal MF/MOM weight |
| `umd_heavy_3025_20_25`  | 30% | 25% | 20% | 25% | heavy UMD, slightly less NTSX |

**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets.
**N_CONFIGS = 4** → DSR n_trials = 4.

## Implementation plan

Adapt iter 015's backtest.py. Key changes:
1. Inject `UMD_PROXY` column into prices DataFrame post-load: build from
   `ff_momentum_proxy()` returns via `cumprod(1+r) * 10000`.
2. CONFIGS: 4 grids above.
3. `expand_capital_efficient` extended to handle `UMD_PROXY` as raw column
   (no expansion — direct use).
4. Reuse all gate / scoring / robustness logic.

No new module; UMD synth handled in backtest.py as one-off price-curve
construction. Pytest baseline (461 tests) unchanged.

## Expected budget

- Implementation: ~10 min.
- Run wall-time: ~5-8 min.
- Plots + report: ~10 min.
- Total: ~30 min.

## Probability assessment (honest)

- **P(strict ADVANCE vs iter 011)**: ~25% — UMD has the strongest
  long-history Sharpe of any factor we've tested (0.75 raw vs VBRSIM ~0.5),
  and momentum premium had several positive years 2017-2024 when value
  lagged. Higher than iter 013 (VBRSIM).
- **P(mechanical ADVANCE only, ties iter 014)**: ~20% — likely if UMD
  helps lh_56y but doesn't materially shift live windows.
- **P(tier WINNER, no ADVANCE)**: ~25%.
- **P(STRONG, no winner conds)**: ~15%.
- **P(FAIL/kill fires)**: ~15%.
