# Iter 014 — Hypothesis: International equity tilt on iter 011 base (NTSX + VXUSSIM + GDE + KMLM)

## Hypothesis (one paragraph)

Inject a **broad international ex-US equity sleeve** (`VXUSSIM`, the
testfolio synth analog of Vanguard VXUS — Total International ex-US Stock
Market) into iter 011's NTSX + GDE + KMLM static capital-efficient stack
at 4 intensity levels (10/20/25/30% VXUSSIM). This tests **Direction A.3**
from `BASE_MEMORY.md` — the cleanest residual axis after iter 012 closed
the RSSB-style intl exposure (Treasury overlap with NTSX, DE-013) and
iter 013 closed constant-weight US small-cap value (post-2008 "death of
value", DE-014). Iter 011 has **zero international equity** — the
incumbent is a pure-US capital-efficient stack — yet the user's explicit
investment thesis is "exposição global + fatores". `VXUSSIM` isolates
**pure intl-equity diversification** because it is **1× notional with
zero embedded Treasury exposure**, sidestepping iter 012's failure mode,
and it is **broad-market beta** rather than a factor sleeve, sidestepping
iter 013's regime-mismatch failure mode. If intl diversification adds a
genuine Sharpe edge to the iter 011 stack on the long-history window
(1986-2026, 40y eff), at least one config should beat iter 011's lh_56y
gross Sharpe of 1.046 — and ideally at least 1 of vt_real (0.960) or
ndx_real (1.104) too.

## Primary citation

- `[risk_parity, ch.5, p.10]` — Carlson capital-efficient stacking (NTSX/GDE core retained)
- `[ilmanen, ch.19]` — global equity diversification rationale (intl-eq as risk premium)
- `[stocks_on_the_move, p.21-30]` — KMLM crisis-alpha component retained
- Gates: `[advances_fin_ml, p.208-211]` (PBO), `[p.222-223]` (DSR), `[p.196-202]` (bootstrap), `[p.31-34]` (cross-lib)

## Edge source (1 sentence)

avg(SPY, VT) buy-hold misses **(a)** the capital efficiency of stacking
Treasury and gold leverage on top of equity (NTSX+GDE), **(b)** managed-
futures crisis alpha (KMLM), AND **(c)** a clean broad ex-US equity sleeve
that historically diversifies US equity factor risk during US-large-cap
underperformance regimes (1970s, 2002-2007).

## Datasets to test

- `lh_56y` (1970-2026, 40y eff window — SPYSIM-bounded 1986+; KMLMSIM
  splice-aware via FF MoM proxy pre-1988 — disclosure required)
- `vt_real` (2008-06 → 2026-04, 17y, VTSIM proxy)
- `ndx_real` (2010-02 → 2026-04, 16y, QQQ stretch)

## Pre-committed kill criteria

**KILL #1 (structural, intl-equity dead-end)**: If the **best-of-grid**
config on `lh_56y` produces gross Sharpe **< 1.046** (iter 011's lh_56y
Sharpe), then international equity diversification is structurally
subordinate to iter 011 on long-history evidence — close Direction A
entirely; pivot to Direction B.5 (UMD momentum overlay) or B.6
(regime-filtered factor) for iter 015.

**KILL #2 (cross-config monotonic regression)**: If Sharpe on **both
vt_real and ndx_real** monotonically decreases with VXUSSIM weight
(10% > 20% > 25% > 30%), and the regression is steeper than +0.05 per
+10% VXUSSIM, the answer is the same as iter 013: a constant-weight
non-US sleeve drags every live window. Document and close.

**Both kills firing → Direction A is closed**; iter 015 must move to
Direction B variants or international-with-regime-filter.

## Configs (pre-committed grid)

All weights sum to 100%. NTSX + GDE + KMLM stays close to iter 011's
35/25/40 base, with VXUSSIM swapped in proportionally:

| config | NTSX | VXUSSIM | GDE | KMLM | rationale |
|---|---:|---:|---:|---:|---|
| `intl_lite_35253010`    | 35% | 10% | 25% | 30% | smallest VXUS swap; closest to iter 011 |
| `intl_moderate_30202525` | 30% | 20% | 25% | 25% | moderate; equal GDE/KMLM defense |
| `intl_balanced_25252525` | 25% | 25% | 25% | 25% | equal-weight 4-asset |
| `intl_heavy_25302025`    | 25% | 30% | 20% | 25% | heaviest VXUS swap; stress-test |

**Selection rule** (matches iters 012 / 013 for cross-iter consistency):
`max mean(gross_Sharpe / avg(SPY,VT)_Sharpe)` across the 3 datasets.

**N_CONFIGS = 4** → DSR n_trials = 4 (per-iter convention,
`WINNER_AND_RANKING.md` §3).

## Implementation plan

Direct adaptation of `iterations/013-*/backtest.py` (clean template).
Changes vs iter 013:

1. Replace `VBRSIM` with `VXUSSIM` in CONFIGS dict.
2. Update CONFIGS to the 4 grids above.
3. Update slug + citations + kill criteria.
4. Re-run on the 3 datasets; reuse all gate / scoring / robustness logic.
5. Generate plots via `plot_helper.py --iter 014`.

No new simulator / no new gate logic / no new mathematical primitive →
**no TDD spec required** (per PROMPT.md Stage 3: "Build new modules ONLY
when the mechanism is qualitatively new"). Pytest baseline (461 tests)
unchanged.

## Expected budget

- Implementation: ~10 min (adapt iter 013's `backtest.py`).
- Run wall-time: ~5 min (4 configs × 3 datasets, bootstrap n=2000).
- Plots + report: ~10 min.
- Memory updates: ~5 min.
- **Total: ~30-40 min** — well under 90 min cap.

## What "advances incumbent" looks like for iter 014

- **Strict ADVANCE**: total_score > 91 OR Sharpe edge ≥ +0.10 vs iter 011
  on ≥ 2 of 3 datasets → set `beats_incumbent: true`, become new incumbent.
- **Tier WINNER but not ADVANCE**: clears all 5 strict winner conditions
  vs avg(SPY,VT) but ≤ iter 011 on ≥ 2 datasets → log as STRONG/WINNER
  tier per scoring rubric, keep iter 011 as incumbent.
- **STRONG/PROMISING/MARGINAL**: log + add to top-K + structural lesson.
- **FAIL** (kill #1 or #2 fires): close Direction A, document DE-015.

## Risk: this hypothesis MAY just close Direction A

iter 012 (RSSB) lost on lh_56y (1.011 vs iter 011's 1.046) AND every live
window. RSSB is ~50% intl-equity + 50% Treasury. If the failure was
PRIMARILY Treasury overlap (DE-013 hypothesis), VXUSSIM should beat. If
the failure was PRIMARILY intl-equity drag in the 2010-2026 regime,
VXUSSIM will fail similarly on vt_real / ndx_real. Either way, iter 014's
result resolves the ambiguity in DE-013 — high information value
regardless of verdict.

## Probability assessment (honest)

- **P(strict ADVANCE)**: ~15% — iter 011 is a tight winner across all 3
  datasets; intl-equity has been a US-vs-world dominant-US regime for
  17 years.
- **P(tier WINNER, no ADVANCE)**: ~25% — likely if VXUSSIM helps lh_56y
  (longer window has more US-underperformance regimes) but doesn't move
  vt_real / ndx_real enough.
- **P(STRONG, no winner conds)**: ~25% — small-but-real drag.
- **P(FAIL/kill fires)**: ~35% — most likely if VXUSSIM imports the same
  intl-equity drag as RSSB minus the Treasury part.

This iter has **high diagnostic value** even at low probability of
ADVANCE, because it isolates the iter 012 failure mode.
