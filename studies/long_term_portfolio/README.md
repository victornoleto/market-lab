# Long-Term Portfolio Loop

**Status**: ACTIVE — launched 2026-04-27 as `bestfolio_hunt_loop`,
**renamed 2026-04-28** to `long_term_portfolio` when the mission was
re-anchored to "beat avg(SPY,VT) gross by ≥0.10 Sharpe on ≥2/3 datasets".
**Mandate reframing 2026-04-29 (A.1-A.4)**: SPY-only baseline +0.05 hurdle,
CAGR warning-only, MDD ≤ SPY strict.

**Mission (NEW iter 023+)**: Find ONE long-term portfolio that beats
**SPY 1× b&h (gross-of-tax)** by ≥ 0.05 Sharpe on ≥ 2 of 3 datasets, with
MDD ≤ SPY on ≥2/3 and passing the 7-gate battery. CAGR floor warning-only.

**Mission (LEGACY iters 001-022)**: beat avg(SPY,VT) by ≥0.10 Sharpe on
≥2/3 with MDD ≤ avg+5pp and CAGR ≥ 0.8 × avg on ≥2/3. Retained for
cross-iter score consistency; published scores anchored here.

Per-dataset NEW benchmarks (SPY-only): lh_56y 0.680 / vt_real 0.900 /
ndx_real 0.900. NEW hurdles (+0.05): 0.730 / 0.950 / 0.950. See
`WINNER_AND_RANKING.md` for full thresholds; `scoring.py` `BENCHMARKS`
is the single source of truth (with `spy_benchmark()` for NEW and
`avg_benchmark()` / `legacy_benchmarks()` for LEGACY).

---

## Status snapshot (updated post-iter 014)

- **Substantive incumbent: iter 011** (NTSX+GDE+KMLM 35/25/40 static) —
  Sharpe 1.046 / 0.960 / 1.104 on (lh_56y / vt_real / ndx_real), 91/100,
  3/3 +0.10 Sharpe edges vs avg(SPY,VT). User's literature thesis from
  Carlson `[risk_parity, ch.5, p.10]`.
- **Mechanical incumbent (rule-defined): iter 014** (35% NTSX + 10%
  VXUSSIM + 25% GDE + 30% KMLM) — Sharpe 1.055 / 0.885 / 1.052, score
  93/100. Beats iter 011's score (93 > 91) but **loses Sharpe to iter
  011 on vt_real and ndx_real** (substantive caveat — see BASE_MEMORY).
- **Constant-weight sleeve injection on iter 011 = closed direction**
  (3 consecutive failures: 012 RSSB / 013 VBRSIM / 014 VXUSSIM). Next
  research must pivot: regime-conditional (B.6), architectural
  replacement (A.1 — NTSI/NTSE), or fundamentally different mechanism.
- bestfolio.app strategies tested in iters 001-010 (BAA-G12, Composite
  Momentum, 5 HAA variants) — **all MARGINAL/PROMISING (54-75 pts);
  none reached WINNER**. Only the user's own literature thesis
  (NTSX+GDE+KMLM, iter 011) cleared the bar.

---

## Original loop directions (history)

The loop initially explored bestfolio.app rankings:
1. ~~BAA (Bold Asset Allocation)~~ — iter 001 MARGINAL, dead-end
2. **NTSX + GDE + KMLM static** — iter 011 WINNER (substantive incumbent)
3. ~~Composite Momentum Standard~~ — iter 002 MARGINAL, dead-end
4. ~~HAA + global factor tilt~~ — iter 004 PROMISING, PBO failure
5. ~~HAA + RSIT (synth)~~ — iter 006 PROMISING, PBO failure

---

## Key differences vs global_factor_tilt_loop

| Item | global_factor_tilt_loop | long_term_portfolio |
|---|---|---|
| Tax model | DarfCostBasisEngine (monthly) | **AnnualDarfEngine** (Lei 14.754/2023) |
| Scoring benchmark | VTSIM b&h (edu S=0.66) | **iter 009 HAA+Gold (edu S=1.120)** |
| Top benchmark source | bestfolio theoretical | **iter 009 empirical (our code)** |
| RSIT | not available | RSIT synth available (INCOMPLETE) |
| Mission | beat VT/PlanC/V_HYBRID | **beat iter 009 Sharpe frontier** |

---

## Scoring benchmark (post-2026-04-29 reframing)

iter 023+ scored against **SPY 1× b&h (gross-of-tax)** per dataset
(NEW primary). iters 001-022 retain LEGACY avg(SPY,VT) scoring for
cross-iter consistency.

### NEW (SPY-only, iter 023+)

| dataset | benchmark | Sharpe | CAGR | MDD |
|---|---|---|---|---|
| lh_56y (1970+) | SPYSIM 40y synth | **0.680** | 11.47% | 55.14% |
| vt_real (~17y) | SPY Tiingo 17y | **0.900** | 14.97% | 33.70% |
| ndx_real (16y) | SPY Tiingo 16y | **0.900** | 14.97% | 33.70% |

Winner requires beating these by ≥ 0.05 Sharpe on ≥ 2 datasets
(minimum Sharpe: lh_56y 0.730 / vt_real 0.950 / ndx_real 0.950).
MDD strict ≤ SPY on ≥2/3. CAGR floor warning-only.

### LEGACY (avg(SPY,VT), iters 001-022)

| dataset | benchmark (avg of) | Sharpe | CAGR | MDD (worst) |
|---|---|---|---|---|
| lh_56y (1970+) | VTSIM 56y + SPYSIM 40y synth | **0.671** | 10.73% | 58.35% |
| vt_real (~17y) | VTSIM 17y + SPY Tiingo 17y | **0.707** | 11.89% | 50.21% |
| ndx_real (16y) | QQQ Tiingo 16y + SPY Tiingo 16y | **0.924** | 16.98% | 35.12% |

LEGACY winner: avg + 0.10 Sharpe on ≥2/3, MDD ≤ avg + 5pp.
See `WINNER_AND_RANKING.md` for the full rubric (NEW + LEGACY tables).

---

## How to run

```bash
# Default 5 iterations
bash studies/long_term_portfolio/run_loop.sh

# 10 iterations, 2h per iter, opus model
MAX_ITER=10 ITER_TIMEOUT=7200 CLAUDE_MODEL=opus bash studies/long_term_portfolio/run_loop.sh

# Dry run (print prompt only)
DRY_RUN=1 bash studies/long_term_portfolio/run_loop.sh
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
`studies/_shared/tax_engine.py` for any net-of-tax analysis. The
old `DarfCostBasisEngine` (monthly DARF, predecessor loop) was
incorrect — the annual model is what the law actually prescribes
and was validated in `global_factor_tilt_loop` post-mortem.

Net-of-tax is reported in `final_report.md` as deploy-readiness
diagnostic; it does **not** influence tier or winner status (mission
is gross-of-tax per `scoring.py` BENCHMARKS).

---

## Mandate

Loop operates under mandate §1 MAINTENANCE MODE (2026-04-23). Any
winner found is a candidate for mandate §7 override — not auto-deploy.
