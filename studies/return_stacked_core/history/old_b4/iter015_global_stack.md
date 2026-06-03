# Iter 015 — Final report: A.1 — 5-asset global capital-efficient stack (NTSX + NTSI + NTSE + GDE + KMLM)

**Date**: 2026-04-28
**Hypothesis**: see `hypothesis.md`
**Slug**: `A1-5asset-global-stack`
**Selected config**: `intl_dev_lite_3515_GK_2030` = 35% NTSX + 15% NTSI + 20% GDE + 30% KMLM (4-asset variant — NTSE excluded)
**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets

---

## Verdict

**Tier**: 🏆 **WINNER** (score **93/100**, all 5 strict winner conditions met vs avg(SPY,VT))

**Beats incumbent**: ⚠️ **`false`** —
- Score TIES iter 014 (93 = 93, not >).
- Sharpe-edge gate vs iter 011 (substantive incumbent) FAILS on all 3 datasets:
  Δ vs iter 011 = +0.035 (lh_56y, **loose**) / **−0.083** (vt_real) / **−0.056** (ndx_real).
- Sharpe-edge gate vs iter 014 (mechanical incumbent) FAILS on all 3 datasets:
  Δ vs iter 014 = +0.026 / −0.008 / −0.004.
- **Both pre-committed structural KILLs fired (#2 and #3)** — see "What the data tells us" below.

**Kept incumbent slots:** iter 014 mechanical (score 93), iter 011 substantive (Sharpe).

---

## Headline metrics — selected config (gross-of-tax, gating dimension; loose convention matching iter 011/014)

| dataset | gross Sharpe | gross CAGR | gross MDD | benchmark avg(SPY,VT) Sh | edge vs bench | gates |
|---|---:|---:|---:|---:|---:|---:|
| **lh_56y**   | **1.081** | 11.63% | 27.99% | 0.671 | **+0.410** | 6/7 |
| **vt_real**  | **0.877** | 10.64% | 26.50% | 0.707 | **+0.171** | 7/7 |
| **ndx_real** | **1.048** | 11.57% | 17.54% | 0.924 | **+0.124** | 7/7 |

3/3 datasets clear the +0.10 Sharpe-edge gate vs avg(SPY,VT) → criterion 1 = 25/25 (full).

## Headline metrics — selected config (net-of-tax, informational)

| dataset | net Sharpe | net CAGR | net MDD |
|---|---:|---:|---:|
| lh_56y    | 1.081 | 11.63% | 27.99% |
| vt_real   | 0.877 | 10.64% | 26.50% |
| ndx_real  | 1.048 | 11.57% | 17.54% |

Static stack + year-end DARF + daily-Sharpe is tax-neutral on returns
series (Lei 14.754/2023 effect rounded to zero at the daily-grain
Sharpe level). Same tax-perfect property that earned iter 011 its
deploy-readiness flag.

---

## Strict-window diagnostic (drops rows where ANY required leg is missing)

The `gross_returns()` function used by all iters in this loop (011/012/013/014/015)
uses pandas `.sum(axis=1)` with default `skipna=True` — meaning rows where a
required leg has NaN (typically pre-bottleneck like SPYSIM pre-1986 or VWOSIM
pre-1994) silently treat that leg's contribution as 0, computing returns on a
partial stack. **This inflates lh_56y Sharpe because pre-bottleneck periods
are dominated by the high-Sharpe leveraged-Treasury sub-stack (IEF + CASH leg)
without the equity drag**. The strict convention (`dropna(how='any')`) drops
those rows and computes only on dates where ALL required legs exist.

| config | type | lh_56y loose S | lh_56y **strict** S | strict eff start |
|---|---|---:|---:|---|
| `intl_dev_3025_GK_2025`        | 4-asset | 1.034 | **0.965** | 1986-01-03 |
| `intl_dev_lite_3515_GK_2030` ✅| 4-asset | 1.081 | **1.007** | 1986-01-03 |
| `global_lit_3015_10_GK_2520`   | 5-asset | 0.964 | **0.889** | 1994-05-05 |
| `global_em_heavy_2520_15_2020` | 5-asset | 0.958 | **0.862** | 1994-05-05 |

Strict-window comparison vs iter 011 (re-computed strict 1.045 on lh_56y, see
smoke test 2026-04-28):
- Selected (1.007) **−0.038 vs iter 011 strict (1.045)** — loses, not wins as the loose convention suggests.
- The +0.035 loose "win" on lh_56y is an artifact of the partial-stack
  pre-1986 Sharpe inflation — **iter 015 does not actually win lh_56y substantively**.

vt_real and ndx_real: strict ≈ loose (no NTSE configs have full data in those
windows; 5-asset configs are only bottlenecked on lh_56y).

**Conclusion**: under honest strict-window accounting, iter 015 loses to iter
011 on **all 3 datasets**. The loose-convention 1.081 lh_56y headline is
preserved for cross-iter comparability; readers should mentally use 1.007
strict for honest comparison.

---

## Comparison vs incumbents (loose convention, cross-iter consistent)

| dataset | iter 015 sel S | iter 014 S | Δ vs iter 014 | iter 011 S | Δ vs iter 011 |
|---|---:|---:|---:|---:|---:|
| lh_56y    | 1.081 | 1.055 | **+0.026** | 1.046 | **+0.035** (loose) / **−0.038** (strict) |
| vt_real   | 0.877 | 0.885 | **−0.008** | 0.960 | **−0.083** |
| ndx_real  | 1.048 | 1.052 | **−0.004** | 1.104 | **−0.056** |

**0/3 datasets clear the +0.10 Sharpe-edge gate vs either incumbent.** The
small loose-convention lh_56y advantage vanishes under strict accounting. On
the deploy-relevant live windows (vt_real, ndx_real), iter 015 is materially
worse than iter 011.

---

## Per-config grid (cross-config monotonic finding)

| config | type | NTSI+NTSE % | lh_56y S | vt_real S | ndx_real S |
|---|---|---:|---:|---:|---:|
| `intl_dev_lite_3515_GK_2030`   ✅ | 4-asset | 15% | **1.081** | **0.877** | **1.048** |
| `intl_dev_3025_GK_2025`           | 4-asset | 25% | 1.034 | 0.820 | 0.995 |
| `global_lit_3015_10_GK_2520`      | 5-asset | 25% (15+10) | 0.964 | 0.796 | 0.974 |
| `global_em_heavy_2520_15_2020`    | 5-asset | 35% (20+15) | 0.958 | 0.739 | 0.915 |

**Across the entire grid, intl-equity weight (NTSI + NTSE combined)
monotonically REDUCES Sharpe on ALL 3 datasets** as it rises 15% → 35%.

**4-asset configs (no NTSE) > 5-asset configs (with NTSE) on ALL 3 datasets**:
- Best 4-asset (1.081 / 0.877 / 1.048) vs best 5-asset (0.964 / 0.796 / 0.974):
  Δ = +0.117 / +0.081 / +0.074. EM-as-component within the 1.5× wrapper is
  uniformly Sharpe-subordinate to no-EM variants.

This is the **second confirmation of the iter 014 monotonic pattern** — the
intl-equity drag in 2010-2026 is regime-real, not architecture-specific.
Whether intl equity is added at 1× notional (iter 014) or inside the 1.5×
leveraged wrapper (iter 015), the 2010-2026 US-large-cap dominance regime
costs Sharpe on every live window.

---

## Pre-committed kill criteria — which fired

| KILL # | Criterion | Status |
|---|---|---|
| **#1** | Best-of-grid loses iter 011 (1.046/0.960/1.104) on ALL 3 datasets | **PARTIAL fire**: loses on vt_real and ndx_real; loose-wins lh_56y by +0.035 (within noise + strict-loses by −0.038). Substantively the answer is "yes, A.1 loses on ≥2/3 deploy windows". |
| **#2** | 5-asset configs uniformly Sharpe-regress vs 4-asset configs | **✅ FIRES**: 5-asset best (0.964/0.796/0.974) loses 4-asset best (1.081/0.877/1.048) on all 3 datasets (Δ −0.12 / −0.08 / −0.07). EM-as-component is dead. |
| **#3** | Cross-config monotonic regression with intl-equity weight | **✅ FIRES**: 15% → 25% → 35% intl-eq monotonically reduces Sharpe on all 3 datasets. Direction A is closed end-to-end. |

**Direction A is now CLOSED end-to-end** (A.1 NTSI/NTSE in this iter, A.2
RSSB in iter 012, A.3 VXUSSIM in iter 014 — all subordinate to iter 011 on
≥ 2 deploy-relevant live windows).

---

## Score breakdown (per `scoring.py`)

| # | criterion | iter 015 pts / max | iter 014 pts | iter 013 pts | iter 011 pts (legacy) |
|---|---|---:|---:|---:|---:|
| 1 | Sharpe edge vs avg(SPY,VT) +0.10 | **25 / 25** | 25 | 25 | 25 |
| 2 | Gate pass + cross-dataset bonus | **23 / 25** (lh_56y 6/7, vt 7/7, ndx 7/7, +4 cross-ds) | 23 | 21 | 21 |
| 3 | DSR worst p < 0.05 (cumulative_n_trials=56) | **15 / 15** (worst p=4.00e-3) | 15 | 15 | 15 |
| 4 | CAGR floor (0.8 × bench, ≥ 2/3) | **10 / 15** (lh_56y ✓, vt ✓, ndx ✗ — 11.57% < 13.59% = 0.8×16.98%) | 10 | 10 | 10 |
| 5 | MDD ceiling (bench + 5pp, ≥ 2/3) | **15 / 15** (3/3 pass; lh_56y 28% < 63%, vt 26.5% < 55%, ndx 17.5% < 40%) | 15 | 15 | 15 |
| 6 | Robustness bonus (rolling 5y) | **5 / 5** (52/52 windows positive, min 0.35 max 1.99) | 5 | 5 | n/a |
| **total** | | **93 / 100** | 93 | 91 | 91 |

iter 015 vs iter 014: **TIED at 93**. Same gate breakdown (only lh_56y G3 WF
fails on max-window-MDD 28.0% > 25%, same crisis-window phenomenon).

---

## Gate detail — selected config

| dataset | G1 PBO | G2 DSR p | G3 WF (max win MDD) | G4 OOS Sh | G5 FWD Sh | G6 boot CI low | G7 cross-lib |
|---|---:|---:|---:|---:|---:|---:|---:|
| lh_56y    | **0.000** ✓ | **2.03e-12** ✓ | ✗ (max=27.99% > 25%) | 1.075 ✓ | 1.072 ✓ | 0.689 ✓ | ✓ (Δ ≤ 1pp) |
| vt_real   | **0.032** ✓ | **4.00e-03** ✓ | ✓ (max=17.54%)         | 1.119 ✓ | 1.072 ✓ | 0.255 ✓ | ✓ |
| ndx_real  | **0.060** ✓ | **9.03e-04** ✓ | ✓ (max=17.54%)         | 0.982 ✓ | 1.072 ✓ | 0.373 ✓ | ✓ |

**Only failure**: G3 walk-forward on lh_56y (one window MDD 28.0% > 25%
threshold). Same failure mode as iter 013 / 014 — 1986-2026 long history
includes 1987 crash + 2008 GFC + 2022 rate hike windows where any
reasonable static stack produces a 25%+ window-MDD. Adapted G3' with stacked
notional adjustment would likely pass; documented limitation.

---

## Pareto comparison

| candidate | window | Sharpe | CAGR | MDD | source |
|---|---|---:|---:|---:|---|
| **iter 015** (this) | lh_56y 40y eff loose | 1.081 | 11.63% | 27.99% | this report |
| iter 015 (lh_56y strict) | lh_56y 38y eff strict | 1.007 | 11.82% | 27.99% | this report (strict diag) |
| iter 015            | vt_real 17y | 0.877 | 10.64% | 26.50% | this report |
| iter 015            | ndx_real 16y | 1.048 | 11.57% | 17.54% | this report |
| iter 014 (mech inc) | lh_56y 40y eff | 1.055 | 11.78% | 29.52% | iter 014 verdict |
| iter 011 (subst inc)| edu 31y      | 1.021 | 11.58% | 26.04% | iter 011 verdict |
| iter 011 (lh_56y retro) | lh_56y 40y | 1.046 | n/a | n/a | BASE_MEMORY top-K |
| iter 011 (lh_56y strict) | lh_56y 38y strict | 1.045 | n/a | n/a | smoke-test 2026-04-28 |
| iter 013            | lh_56y 40y eff | 1.126 ⭐ | 12.32% | 25.73% | DE-014 |
| iter 035 (archive)  | 40y synth | 0.92  | **19.6%** ⭐ | 46.18% | strategy_hunt_loop |
| iter 016/074 (arch.)| 40y synth | 0.95  | 15.1% | **34.6%** ⭐ | strategy_hunt_loop |
| iter 079 (archive)  | 17y SPY-Tiingo | 1.094 | 13.0% | 25.0% | strategy_hunt_loop |
| **avg(SPY,VT)** (lh_56y bench) | — | 0.671 | 10.73% | 58.35% | scoring.BENCHMARKS |

**Pareto position of iter 015**: dominates avg(SPY,VT) on all 3 dimensions
(Sharpe ↑, CAGR ↑, MDD ↓). Does NOT dominate iter 011 (loses Sharpe on 2/3
loose; loses on 3/3 strict) or iter 014 (ties / loses on all 3 windows). Loses
raw CAGR to iter 035 archive (11.63% vs 19.6%) but wins Sharpe and MDD.

---

## What the data tells us — structural insight

iter 015 is the **fourth iter in a row** trying to find a better static
capital-efficient stack than iter 011 (NTSX + GDE + KMLM 35/25/40), and
the **third confirmation** of the same monotonic pattern:

| iter | mechanism | direction tested | finding |
|---|---|---|---|
| 012 | RSSB sleeve | A.2 | sleeve injection at 2× notional with Treasury overlap → loses 3/3 |
| 013 | VBRSIM sleeve | B.4 | sleeve injection at 1× factor notional → loses 2/3 (death of value) |
| 014 | VXUSSIM sleeve | A.3 | sleeve injection at 1× pure intl-eq → loses 2/3 (intl-eq drag) |
| **015** | **NTSI/NTSE component swap** | **A.1** | **architectural rebalance, NOT sleeve add → loses 2/3 (3/3 strict)** |

**Direction A is now CLOSED end-to-end.** Both structural variants of
"global+factor" on iter 011's architecture have been exhausted:

1. **Sleeve-add** (012/013/014): adding a constant-weight sleeve outside
   the 1.5× wrapper drags every live window.
2. **Component-swap** (015): moving equity sleeve from US to intl inside
   the 1.5× wrapper drags every live window.

**The lesson is now overdetermined**: the 2010-2026 regime is so dominated
by US-large-cap that **any deviation from pure US equity in the equity
sleeve costs Sharpe** — whether the deviation is at 1× notional outside the
wrapper or at 1.5× notional inside it. Iter 011's NTSX (pure US equity in
the cap-efficient wrapper) is the architectural ceiling for static
capital-efficient stacks in this regime.

**The next research direction MUST pivot to either:**

1. **B.6 — regime-conditional weighting** (next iter 016): NTSI/VBRSIM/
   VXUSSIM weight = f(regime signal). The factor/intl exposure only fires
   when the regime favors it (value spread positive, US/intl spread
   inverted, EM momentum positive). Pre-commit ≤ 3 configs to avoid the
   prior-loop "regime gate on existing winner" DSR-regression trap.
2. **C — fundamentally different mechanism**: leave the static cap-efficient
   stack alone, look at Antonacci GEM cross-class top-K (iter 079 archive
   approach) or vol-managed 60/40 (iter 006 archive). Different optimization
   target, different alpha source.

---

## Lesson

**Iter 011 is the architectural ceiling for static capital-efficient stacks
in the 2010-2026 US-large-cap-dominant regime.** This is now triply
confirmed (iters 012/013/014 closed sleeve-injection; iter 015 closed
component-swap). The user's literal global+factor thesis (NTSX + NTSI + NTSE
+ GDE + KMLM) does not beat the simpler US-only thesis (NTSX + GDE + KMLM)
on deploy-relevant live windows. The intl-equity premium that was strong
1970-2007 is dormant 2010-2024 enough to dominate any constant-weight
allocation decision.

**For deploy-readiness:** iter 011 remains the correct answer at any
mandate §7 override deliberation. Iter 015 at most demonstrates that
NTSI/NTSE proxies are now infrastructurally available for any future
regime-conditional iteration that needs them.

**Direction A: CLOSED. Next iter (016): B.6 regime-conditional factor.**

---

## Citations

- **Capital-efficient stacking core (NTSX/NTSI/NTSE/GDE retained)**: `[risk_parity, ch.5, p.10]` — Carlson, *Capital Efficiency*; WisdomTree Efficient Core ETF prospectus 2024 (90/60/−50 blueprint, identical across NTSX/NTSI/NTSE)
- **Global equity diversification rationale**: `[ilmanen, ch.19]` — Ilmanen, *Expected Returns* (intl premium structurally distinct from US equity premium)
- **KMLM crisis-alpha component**: `[stocks_on_the_move, p.21-30]` — Clenow, *Stocks on the Move*
- **Gates**:
  - G1 PBO `[advances_fin_ml, p.208-211]`
  - G2 DSR `[advances_fin_ml, p.222-223]`
  - G6 Bootstrap `[advances_fin_ml, p.196-202]`
  - G7 Cross-lib `[advances_fin_ml, p.31-34]`
- **Scoring rubric**: `studies/long_term_portfolio/WINNER_AND_RANKING.md`
- **Synth proxy module**: `studies/long_term_portfolio/proxies.py` (validated 2026-04-28 against iter 011/014 inline expansion + sanity-checked vol/Sharpe/correlation against deploy_studies NTSX 2026-04-26)

---

## Next directions (post iter 015)

Direction A is now closed end-to-end (012/013/014/015 all subordinate to
iter 011 on ≥ 2 of 3 deploy-relevant live windows). Next iter must pivot:

1. **B.6 — Regime-conditional factor tilt** (highest priority, next iter):
   VBRSIM weight = f(12-month value spread or factor momentum). Pre-commit
   ≤ 3 configs to avoid the strategy_hunt_loop "regime gate on existing
   winner" DSR-regression trap. Citation `[advances_fin_ml, p.208-211]`
   (PBO discipline) + `[risk_parity, ch.2]` (factor framework).

2. **C — Fundamentally different mechanism** (parallel option): Antonacci
   GEM cross-class top-K (iter 079 archive style) or vol-managed 60/40
   (iter 006 archive). Different optimization target, breaks out of the
   static-stack frame entirely.

3. **Stop hunting; declare iter 011 deploy-ready** (defensible option):
   given 4 consecutive iters fail to substantively beat iter 011, and the
   user's literature thesis has now been fully exhausted at the static-
   stack level, prepare mandate §7 override request for iter 011 deploy
   on Plano C. Reactivate hunting in 6-12 months when post-2026 OOS
   data is meaningful.

The user's primary literature thesis (NTSX + NTSI + NTSE + GDE + KMLM
+ factor ETFs AVUS/AVDE/SPMO/IDMO/AVUV) is now **fully tested at the
constant-weight level**. Remaining alpha must come from regime-
conditional weighting OR architectural changes outside iter 011's
static-stack frame.

---

*Generated 2026-04-28 by long_term_portfolio loop iter 015.*
