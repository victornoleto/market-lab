# Iter 015 — Hypothesis: A.1 — 5-asset global capital-efficient stack (NTSX + NTSI + NTSE + GDE + KMLM)

## Hypothesis (one paragraph)

Build the **literal user thesis from BASE_MEMORY direction A.1**: a 5-asset
global capital-efficient stack pairing iter 011's US capital-efficient core
(NTSX + GDE) and crisis-alpha sleeve (KMLM) with two sister WisdomTree
"Efficient Core" ETFs synthesized testfolio-style for the first time —
**NTSI** (intl-developed equity stacked on Treasuries, 1.5× notional) and
**NTSE** (EM equity stacked on Treasuries, 1.5× notional). After 3
consecutive sleeve-injection iterations on iter 011's base failed (012 RSSB,
013 VBRSIM, 014 VXUSSIM — all DEAD-END with structural lessons), the next
viable axis is **architectural replacement, not augmentation**: instead of
adding a constant-weight sleeve to the iter 011 stack, this iter
**rebalances the equity sleeve geographically** while preserving the
capital-efficient stacking architecture that earned iter 011 its winner
status. Iter 014's intl-equity sleeve hurt because it added a 1× notional
intl-equity drag to an already 100%-allocated portfolio; **NTSI/NTSE
deliver the same geographic diversification within the 1.5× cap-efficient
wrapper** (intl equity AND Treasury duration AND zero financing cost),
matching iter 011's structural mechanism. If the WisdomTree leverage
architecture transports across geographies — the literature says it should
— the 5-asset stack should at minimum tie iter 011 on lh_56y while opening
upside on global-equity-weighted live windows (vt_real).

## Primary citation

- `[risk_parity, ch.5, p.10]` — Carlson, *Capital Efficiency*: WisdomTree
  Efficient Core ETF family (NTSX/NTSI/NTSE) is the canonical implementation
  of return-stacking; same 90/60/−50 prospectus blueprint across the family,
  only the equity index differs.
- `[ilmanen, ch.19]` — Ilmanen, *Expected Returns*: global equity premium
  is structurally distinct from US equity premium, especially in regimes
  where USD strengthens or US-large-cap breadth narrows (1970s, 2002-2007).
- `[stocks_on_the_move, p.21-30]` — Clenow: KMLM-style managed-futures
  trend as crisis-alpha diversifier (retained from iter 011).
- Gates: `[advances_fin_ml, p.208-211]` (PBO), `[p.222-223]` (DSR),
  `[p.196-202]` (bootstrap), `[p.31-34]` (cross-lib).

## Edge source (1 sentence)

avg(SPY, VT) buy-hold misses **(a)** the 1.5× capital-efficient stacking
of equity + Treasury duration (NTSX for US, NTSI for intl-developed, NTSE
for EM); **(b)** the GDE gold-stacked overlay; AND **(c)** managed-futures
crisis-alpha (KMLM) — together giving global equity + duration + gold +
crisis-alpha all in a wrapper that pays no retail margin and has zero
daily decay.

## Datasets to test

- `lh_56y` — 4-asset configs (no NTSE) reach 1986+ via SPYSIM bottleneck;
  5-asset configs reach 1994+ via VWOSIM bottleneck. Per-config effective
  windows reported in `results.json`. Window-aware caveat in final_report.
- `vt_real` (2008-06 → 2026-04, 17y) — full data on all 5 legs.
- `ndx_real` (2010-02 → 2026-04, 16y) — full data on all 5 legs.

## Pre-committed kill criteria

**KILL #1 (architectural — A.1 closed)**: If the **best-of-grid** config on
ALL 3 datasets produces gross Sharpe **< iter 011** (1.046 / 0.960 / 1.104),
then geographic equity rebalancing within the cap-efficient stack does NOT
help on any window. Closes Direction A entirely (A.1, A.2 RSSB, A.3 VXUSSIM
all closed). Pivot to B.6 (regime-conditional factor) for iter 016.

**KILL #2 (NTSE drag confirms intl-equity dead-end)**: If the **5-asset
configs (with NTSE)** uniformly Sharpe-regress vs the **4-asset configs (no
NTSE)** on all datasets, EM exposure within the 1.5× wrapper is structurally
subordinate. Closes EM-as-component direction; iter 016 may revisit
NTSI-only (intl-developed) variants.

**KILL #3 (cross-config monotonic regression like iter 014)**: If
intl-equity weight (NTSI + NTSE combined) monotonically reduces Sharpe
across the grid on ≥ 2 datasets, the geographic mechanism doesn't transport
into the cap-efficient wrapper either — close Direction A and pivot to B.6.

**Any KILL firing → Direction A is closed end-to-end; iter 016 pivots to
B.6 regime-conditional factor.**

## Configs (pre-committed grid)

All weights sum to 100%. Grid mixes 4-asset (no NTSE, full lh_56y) with
5-asset (with NTSE, 32y eff) so we can isolate the NTSE contribution
cleanly:

| config | NTSX | NTSI | NTSE | GDE | KMLM | type | eff window |
|---|---:|---:|---:|---:|---:|---|---|
| `intl_dev_4030_GK_2030`   | 30% | 25% | 0%  | 20% | 25% | 4-asset | full lh_56y (1988+) |
| `intl_dev_lite_3015_GK_2530` | 35% | 15% | 0%  | 20% | 30% | 4-asset | full lh_56y (1988+) |
| `global_lit_3015_10_GK_2520` | 30% | 15% | 10% | 25% | 20% | 5-asset | 1994+ (32y eff) |
| `global_em_heavy_2520_15_2020` | 25% | 20% | 15% | 20% | 20% | 5-asset | 1994+ (32y eff) |

**Rationale**:
- Configs 1-2 are 4-asset (NTSX + NTSI + GDE + KMLM): direct test of "swap
  some US for intl-developed inside the 1.5× wrapper" with full lh_56y
  apples-to-apples vs iter 011/014.
- Configs 3-4 are 5-asset (add NTSE 10-15%): test the literal user thesis
  including EM exposure on 1994+ window.

**Selection rule** (matches iters 012 / 013 / 014 for cross-iter consistency):
`max mean(gross_Sharpe / avg(SPY,VT)_Sharpe)` across the 3 datasets.

**N_CONFIGS = 4** → DSR n_trials = 4 (per-iter convention,
`WINNER_AND_RANKING.md` §3 cumulative + per-iter).

## Implementation plan

Direct adaptation of `iterations/014-*/backtest.py` (clean template).
Changes vs iter 014:

1. Import `expand_capital_efficient` from
   `studies.long_term_portfolio.proxies` (new shared module). Replaces
   the inline `expand_weights` function in iter 014.
2. CONFIGS dict: 4 grids above (mix of 4-asset / 5-asset).
3. `hypothesis_slug`: `A1-5asset-global-stack`.
4. Update kill-criteria comment block.
5. final_report includes per-config effective window + STRICT-window
   diagnostic Sharpe (per-config) alongside the loose convention used by
   the rest of the loop.
6. Reuse all gate / scoring / robustness logic untouched.

`proxies.py` is a new module but its synth formula is mathematically
identical to iter 011/014's inline `expand_weights` (smoke-test verified
2026-04-28). NO new simulator / NO new gate logic / NO new mathematical
primitive → **no TDD spec required** (per PROMPT.md Stage 3). Pytest
baseline (461 tests) unchanged.

## Expected budget

- Implementation: ~10 min (adapt iter 014 + import proxies module).
- Run wall-time: ~5-8 min (4 configs × 3 datasets, bootstrap n=2000).
- Plots + report: ~15 min (need extra strict-window diagnostic block).
- Memory updates: ~5 min.
- **Total: ~35-45 min** — well under 90 min cap.

## What "advances incumbent" looks like for iter 015

- **Strict ADVANCE (substantive)**: Sharpe edge ≥ +0.10 vs iter 011 on ≥ 2
  of 3 datasets (lh_56y ≥ 1.146, vt_real ≥ 1.060, ndx_real ≥ 1.204) →
  set `beats_incumbent: true`, become NEW substantive incumbent.
- **Mechanical ADVANCE only (like iter 014)**: total_score > 93 AND clears
  5/5 winner conds vs avg(SPY,VT), but Sharpe-edge gate vs iter 011 fails.
  Document the same way iter 014 did — flag the substantive caveat.
- **Tier WINNER but no advance**: ≥ 90 + 5/5 conds vs avg(SPY,VT) but
  ≤ iter 014's score 93 AND no Sharpe edge vs iter 011 → log as STRONG/
  WINNER tier per scoring rubric, keep iter 014 mechanical incumbent +
  iter 011 substantive reference.
- **STRONG/PROMISING/MARGINAL**: log + add to top-K + structural lesson.
- **FAIL** (any kill fires): close Direction A, document DE-016, prepare
  iter 016 = B.6 regime-conditional factor.

## Risk: this hypothesis MAY just close Direction A entirely

iters 012/013/014 closed sleeve-injection. If iter 015 ALSO fails, then
**both** structural variants of the global+factor thesis (sleeve-add AND
geographic-rebalance) on iter 011's architecture are dead. The lesson
would be: **iter 011 is genuinely the architectural ceiling for static
capital-efficient stacks**, and any future Sharpe edge must come from
either regime-conditional weighting (B.6) or a fundamentally different
mechanism (Antonacci GEM cross-class top-K, vol-managed 60/40).

## Probability assessment (honest)

- **P(strict ADVANCE)**: ~20% — NTSI alone (1970-2026 history) is
  attractive: 1.5× intl-developed equity captures the 1970s-1980s intl
  outperformance regime that iter 011 missed via pure-US NTSX. Higher than
  iter 014 (which had no leverage on the intl sleeve).
- **P(mechanical ADVANCE only)**: ~25% — likely if 4-asset configs
  modestly help lh_56y but 5-asset NTSE drag offsets gains in live windows.
- **P(tier WINNER, no ADVANCE)**: ~25% — likely if NTSI helps lh_56y but
  underperforms NTSX in the 2010-2024 US-dominant regime, and NTSE drags
  EM-exposure live windows.
- **P(STRONG, no winner conds)**: ~15% — small-but-real failure.
- **P(FAIL/kill fires)**: ~15% — if KILL #1 fires (best-of-grid loses on
  all 3 datasets), Direction A closes definitively.

This iter has **high diagnostic value** at any outcome:
- WINNER → user's literature thesis validated; new incumbent.
- Mechanical-only → confirms US-large-cap regime dominance independent
  of leverage architecture.
- FAIL → closes Direction A; clears the path to B.6.
