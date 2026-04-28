# Bestfolio Hunt Loop

**Status**: ACTIVE — launched 2026-04-27.

**Mission**: Find ONE strategy that Pareto-advances iter 009 HAA+Gold
(Sharpe 1.120 edu / 1.061 vt_real / 0.954 ndx_real) — the Sharpe
frontier from `global_factor_tilt_loop` (13 iters, FROZEN).

Gap to bestfolio.app #1 (HAA SmartStack, Sharpe 1.18): **−0.06 Sharpe**.

---

## Context

`global_factor_tilt_loop` found 6 winners in 13 iters. Best gross
result: iter 009 HAA+KMLM10+GLD5 (S=1.120 edu). The loop converged on
the HAA architecture as dominant — the 0.06 gap to bestfolio #1 likely
requires either a wider offensive universe or a more defensive canary.

This loop explores:
1. **BAA (Bold Asset Allocation)** — 12-asset dual-canary, bestfolio #5
2. **NTSX + GDE + KMLM static** — user's capital-efficient architecture
3. **Composite Momentum Standard** — bestfolio #2 (Sharpe 1.17)
4. **HAA + global factor tilt** — AVDV/VBRSIM in offensive
5. **HAA + RSIT** (deferred — awaiting launch ~mai/2026)

---

## Key differences vs global_factor_tilt_loop

| Item | global_factor_tilt_loop | bestfolio_hunt_loop |
|---|---|---|
| Tax model | DarfCostBasisEngine (monthly) | **AnnualDarfEngine** (Lei 14.754/2023) |
| Scoring benchmark | VTSIM b&h (edu S=0.66) | **iter 009 HAA+Gold (edu S=1.120)** |
| Top benchmark source | bestfolio theoretical | **iter 009 empirical (our code)** |
| RSIT | not available | RSIT synth available (INCOMPLETE) |
| Mission | beat VT/PlanC/V_HYBRID | **beat iter 009 Sharpe frontier** |

---

## Scoring benchmark

Any strategy tested here is scored against **iter 009 HAA+Gold**:

| dataset | Sharpe | CAGR | MDD |
|---|---|---|---|
| educational (56y) | 1.120 | 13.89% | 20.81% |
| vt_real (~17y) | 1.061 | 12.87% | 14.20% |
| ndx_real (16y) | 0.954 | 10.55% | 14.20% |

Winner requires beating iter 009 by ≥ 0.10 Sharpe on ≥ 2 datasets
(minimum Sharpe: edu 1.220 / vt_real 1.161 / ndx_real 1.054).

---

## How to run

```bash
# Default 5 iterations
bash studies/bestfolio_hunt_loop/run_loop.sh

# 10 iterations, 2h per iter, opus model
MAX_ITER=10 ITER_TIMEOUT=7200 CLAUDE_MODEL=opus bash studies/bestfolio_hunt_loop/run_loop.sh

# Dry run (print prompt only)
DRY_RUN=1 bash studies/bestfolio_hunt_loop/run_loop.sh
```

---

## Files

| file | purpose |
|---|---|
| `BASE_MEMORY.md` | loop state: frontmatter + hypothesis queue + iteration log |
| `INFRASTRUCTURE.md` | simulators, data loaders, validation, tax engine |
| `DEAD_ENDS.md` | proven dead-ends (forbidden re-tests) |
| `WINNER_AND_RANKING.md` | strict winner conditions + score rubric |
| `EXTERNAL_INSTRUMENTS.md` | capital-efficient ETFs reference |
| `scoring.py` | score_strategy() with BENCHMARKS = iter 009 |
| `plot_helper.py` | equity-vs-benchmark chart per iter |
| `run_loop.sh` | shell orchestrator |
| `PROMPT.md` | per-iter prompt (template with {{ITERATION_N}}) |
| `iterations/` | one dir per iter |

---

## Tax model

Always use `AnnualDarfEngine` (Lei 14.754/2023) from
`studies/global_factor_tilt_loop/tax_engine_v2.py` for any
net-of-tax analysis. The old `DarfCostBasisEngine` (monthly DARF)
was incorrect — iter 014 confirmed the annual model produces a
slightly different result for high-turnover strategies.

---

## Mandate

Loop operates under mandate §1 MAINTENANCE MODE (2026-04-23). Any
winner found is a candidate for mandate §7 override — not auto-deploy.
