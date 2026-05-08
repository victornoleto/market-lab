# Iter 014 — Final report: International equity tilt on iter 011 base (NTSX + VXUSSIM + GDE + KMLM)

**Date**: 2026-04-28
**Hypothesis**: see `hypothesis.md`
**Slug**: `intl-equity-tilt-on-iter011`
**Selected config**: `intl_lite_35253010` = 35% NTSX_PROXY + 10% VXUSSIM + 25% GDE + 30% KMLM
**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets

---

## Verdict

**Tier**: 🏆 **WINNER** (score **93/100**, all 5 strict winner conditions met vs avg(SPY,VT))

**Beats incumbent**: ⚠️ **`true` mechanically (score 93 > 91), `false` substantively** —
iter 014 LOSES Sharpe to iter 011 on 2 of 3 datasets. The score advance is
partially a benchmark-comparison artifact (iter 011 was scored on legacy
`educational` window benchmarks, iter 014 on the new lh_56y framework).

Per the prompt rule, beats_incumbent fires when EITHER `latest_score >
incumbent_winner_score` OR Sharpe edge ≥ +0.10 vs incumbent on ≥ 2 of 3
datasets. The first OR clause is satisfied (93 > 91); the Sharpe-edge
clause fails on all 3 datasets (best edge +0.009 on lh_56y, both live
windows regress). I follow the rule and set `beats_incumbent: true`, but
this report calls out the substantive caveat.

---

## Headline metrics — selected config (gross-of-tax, gating dimension)

| dataset | gross Sharpe | gross CAGR | gross MDD | benchmark avg(SPY,VT) Sh | edge vs bench | gates |
|---|---:|---:|---:|---:|---:|---:|
| **lh_56y**   | **1.055** | 11.78% | 29.52% | 0.671 | **+0.384** | 6/7 |
| **vt_real**  | **0.885** | 11.14% | 27.99% | 0.707 | **+0.178** | 7/7 |
| **ndx_real** | **1.052** | 12.11% | 18.40% | 0.924 | **+0.129** | 7/7 |

3/3 datasets clear the +0.10 Sharpe-edge gate vs avg(SPY,VT) →
criterion 1 = 25/25 (full).

## Headline metrics — selected config (net-of-tax, informational)

| dataset | net Sharpe | net CAGR | net MDD |
|---|---:|---:|---:|
| lh_56y    | 1.055 | 11.78% | 29.52% |
| vt_real   | 0.885 | 11.14% | 27.99% |
| ndx_real  | 1.052 | 12.11% | 18.40% |

Static stack + year-end DARF + daily-Sharpe is tax-neutral on returns
series (Lei 14.754/2023 effect rounded to zero at the daily-grain
Sharpe level; small CAGR drag is invisible at 2-decimal precision).
Confirmed via `AnnualDarfEngine` per `studies/_shared/tax_engine.py`.

---

## Comparison vs iter 011 incumbent

| dataset | iter 014 sel S | **iter 011 S** | Δ vs iter 011 | sign |
|---|---:|---:|---:|---|
| lh_56y    | 1.055 | 1.046 | **+0.009** | tied (within noise) |
| vt_real   | 0.885 | 0.960 | **−0.075** | LOSES |
| ndx_real  | 1.052 | 1.104 | **−0.052** | LOSES |

**0/3 datasets clear the +0.10 incumbent edge gate.** On the deploy-
relevant live windows (vt_real, ndx_real), iter 014 is materially
worse than iter 011.

---

## Per-config grid (cross-config monotonic finding)

| config | VXUS % | lh_56y S | Δ iter011 | vt_real S | Δ iter011 | ndx_real S | Δ iter011 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `intl_lite_35253010`     | 10% | **1.055** | **+0.009** | **0.885** | **−0.075** | **1.052** | **−0.052** |
| `intl_moderate_30202525` | 20% | 1.004 | −0.042 | 0.811 | −0.149 | 0.985 | −0.119 |
| `intl_balanced_25252525` | 25% | 0.995 | −0.051 | 0.781 | −0.179 | 0.953 | −0.151 |
| `intl_heavy_25302025`    | 30% | 0.989 | −0.057 | 0.744 | −0.216 | 0.917 | −0.187 |

**Across the entire grid, intl-equity tilt monotonically REDUCES Sharpe
on ALL 3 datasets** as VXUSSIM weight rises 10% → 30%. The lightest
config (10%) is the only one that ties iter 011 on lh_56y; the heavier
configs are strictly subordinate to iter 011 on every dataset.

This is a stronger structural signal than iter 013's pattern: in iter
013, factor tilt **helped** lh_56y monotonically (+0.060 → +0.085) and
hurt the live windows. In iter 014, intl tilt **hurts** every dataset
monotonically — including lh_56y. The win on lh_56y at 10% VXUS is a
single grid point, not a robust direction.

---

## Score breakdown (per `scoring.py`)

| # | criterion | iter 014 pts / max | iter 013 pts | iter 011 pts (legacy) |
|---|---|---:|---:|---:|
| 1 | Sharpe edge vs avg(SPY,VT) +0.10 | **25 / 25** | 25 | 25 |
| 2 | Gate pass + cross-dataset bonus | **23 / 25** (lh_56y 6/7, vt 7/7, ndx 7/7, +4 cross-ds) | 21 | 21 |
| 3 | DSR worst p < 0.05 (n_trials=4) | **15 / 15** (worst p=3.66e-3) | 15 | 15 |
| 4 | CAGR floor (0.8 × bench, ≥ 2/3) | **10 / 15** (lh_56y ✓, vt ✓, ndx ✗) | 10 | 10 |
| 5 | MDD ceiling (bench + 5pp, ≥ 2/3) | **15 / 15** (3/3 pass) | 15 | 15 |
| 6 | Robustness bonus (rolling 5y) | **5 / 5** (52/52 windows positive) | 5 | n/a |
| **total** | | **93 / 100** | 91 | 91 |

iter 014 vs iter 013: +2 pts on gate criterion (lh_56y 6/7 vs 5/7 — one
more gate passes on long-history because intl-equity slightly cuts
extreme drawdown risk in some walk-forward windows).

iter 014 vs iter 011 (legacy): not directly comparable due to scoring
benchmark migration on 2026-04-28. iter 011 has not been re-scored under
the new lh_56y framework. **The score advance 93 > 91 should be read with
the substantive caveat above** (iter 014 loses Sharpe on 2/3 datasets vs
iter 011).

---

## Gate detail — selected config

| dataset | G1 PBO | G2 DSR p | G3 WF (max win MDD) | G4 OOS Sh | G5 FWD Sh | G6 boot CI low | G7 cross-lib |
|---|---:|---:|---:|---:|---:|---:|---:|
| lh_56y    | **0.028** ✓ | **7.74e-12** ✓ | ✗ (max=29.5% > 25%) | 1.083 ✓ | 1.111 ✓ | 0.667 ✓ | ✓ (Δ ≤ 1pp) |
| vt_real   | **0.000** ✓ | **3.66e-03** ✓ | ✓ (max=18.4%)         | 1.176 ✓ | 1.111 ✓ | 0.274 ✓ | ✓ |
| ndx_real  | **0.000** ✓ | **8.53e-04** ✓ | ✓ (max=18.4%)         | 1.046 ✓ | 1.111 ✓ | 0.382 ✓ | ✓ |

**Only failure**: G3 walk-forward on lh_56y (one window MDD 29.5% > 25%
threshold). Same failure mode as iter 013 — the 1986-2026 long history
includes 1987 crash + 2008 GFC + 2022 rate hike windows where any
reasonable static stack has a 25%+ window-MDD. Adapted G3' with stacked
notional adjustment would likely pass; documented limitation.

---

## Pareto comparison

vs `studies/_archive/strategy_hunt_loop/` winners and current incumbent:

| candidate | window | Sharpe | CAGR | MDD | source |
|---|---|---:|---:|---:|---|
| **iter 014** (this) | lh_56y 40y | 1.055 | 11.78% | 29.52% | this report |
| iter 014           | vt_real 17y | 0.885 | 11.14% | 27.99% | this report |
| iter 014           | ndx_real 16y | 1.052 | 12.11% | 18.40% | this report |
| **iter 011** (incumbent) | edu 31y | **1.021** | 11.58% | 26.04% | BASE_MEMORY top-K |
| iter 011 (lh_56y retro) | lh_56y 40y | **1.046** | n/a | n/a | BASE_MEMORY top-K |
| iter 013           | lh_56y 40y | 1.126 ⭐ | 12.32% | 25.73% | DE-014 |
| iter 035 (archive) | 40y synth | 0.92  | **19.6%** ⭐ | 46.18% | strategy_hunt_loop |
| iter 016/074 (archive) | 40y synth | 0.95  | 15.1% | **34.6%** ⭐ | strategy_hunt_loop |
| iter 079 (archive) | 17y SPY-Tiingo | 1.094 | 13.0% | 25.0% | strategy_hunt_loop |
| **avg(SPY,VT)** (lh_56y bench) | — | 0.671 | 10.73% | 58.35% | scoring.BENCHMARKS |

**Pareto position of iter 014**: dominates avg(SPY,VT) on all 3 dimensions
(Sharpe ↑, CAGR ↑, MDD ↓). Does NOT dominate iter 011 — loses Sharpe on
2 of 3 windows, ties on lh_56y. Does NOT dominate iter 013 lh_56y
(1.126 vs 1.055). Loses raw CAGR to iter 035 archive (11.78% vs 19.6%
on 40y synth) but wins Sharpe and MDD comfortably.

---

## lh_56y caveats

This iter uses the lh_56y dataset which splices the KMLMSIM column with
a Ken French daily momentum factor (UMD + RF) proxy pre-1988. Per
`datasets.py` and `INFRASTRUCTURE.md`:

- **UMD's 1970-87 Sharpe ≈ 1.9** (cross-sectional academic equity
  momentum) **vs KMLM's long-run ~0.5** → pre-1988 returns of any
  KMLM-using config are **OVERSTATED by ~3× in Sharpe terms**.
- iter 014's KMLMSIM weight in the selected config is **30%**, so the
  pre-1988 segment contributes meaningfully to lh_56y's Sharpe.
- **The effective comparable window is 1988-2026 (38y)**, not 1970-2026.
- The +0.384 edge vs avg(SPY,VT) on lh_56y likely shrinks to ~+0.15 to
  +0.25 if KMLM is held flat at long-run Sharpe pre-1988.

This caveat applies equally to iter 011 / iter 012 / iter 013 — same
splice, same overstatement direction. Cross-iter comparisons within the
loop remain valid (all use the same splice); cross-iter vs avg(SPY,VT)
edge claims should mentally haircut by 0.10 to 0.20 Sharpe on lh_56y.

---

## What the data tells us — structural insight

iter 014 is the **third consecutive sleeve-injection test on iter 011's
base**:

| iter | sleeve added | structural mechanism | lh_56y Δ vs iter011 | live windows Δ vs iter011 |
|---|---|---|---:|---:|
| 012 | RSSB (200% notional, ~50% Treasury + ~50% intl-eq) | leveraged global bond+equity | −0.035 | −0.109, −0.083 |
| 013 | VBRSIM (US small-cap value, 1× notional) | factor premium (size + value) | **+0.080** | −0.037, −0.029 |
| 014 | VXUSSIM (intl ex-US equity, 1× notional) | broad equity diversification | **+0.009** | −0.075, −0.052 |

**Common pattern**: iter 011's NTSX + GDE + KMLM stack is so well-tuned
to the 2010-2026 US-large-cap regime that **any sleeve injection
hurts** on the live windows — RSSB hurts most, factor tilt hurts least
on long-history but second-most on live, and intl-equity is in between.

**Conclusion**: **constant-weight sleeve injection on iter 011 is a
closed direction**. The next research must either:

1. **Replace** part of iter 011's base (not augment with a new sleeve) —
   e.g., NTSX → NTSI or NTSE if proxies are synthesized.
2. **Add a regime-conditional sleeve** — e.g., factor tilt only when
   value/size premium signal is positive (Direction B.6 from
   BASE_MEMORY).
3. **Pursue a fundamentally different mechanism** — e.g., Antonacci
   GEM-style cross-class top-K (iter 079 archive) or vol-managed
   60/40 (iter 006 archive).

---

## Lesson

International ex-US equity at 10-30% constant weight is **not the
missing factor on iter 011's base**. The hypothesis was that VXUSSIM
would resolve the iter 012 ambiguity (was failure due to Treasury
overlap or intl-equity drag?). **Answer: BOTH contributed**. Stripping
RSSB's Treasury overlay (going to 1× VXUSSIM) helps on lh_56y (best
config 1.055 vs iter 012's 1.011) but the intl-equity drag in
2010-2026 still costs vt_real / ndx_real Sharpe.

**iter 011 is the architectural ceiling for constant-weight stacks in
this universe.** Future work must either: (a) build a regime gate, or
(b) leave iter 011 alone and look at structurally different mechanisms.

---

## Citations

- **Capital-efficient stacking core (NTSX/GDE retained)**: `[risk_parity, ch.5, p.10]` — Carlson, *Capital Efficiency*
- **Global equity diversification rationale**: `[ilmanen, ch.19]` — Ilmanen, *Expected Returns*
- **KMLM crisis-alpha component**: `[stocks_on_the_move, p.21-30]` — Clenow, *Stocks on the Move*
- **Gates**:
  - G1 PBO `[advances_fin_ml, p.208-211]`
  - G2 DSR `[advances_fin_ml, p.222-223]`
  - G6 Bootstrap `[advances_fin_ml, p.196-202]`
  - G7 Cross-lib `[advances_fin_ml, p.31-34]`
- **Scoring rubric**: `studies/long_term_portfolio/WINNER_AND_RANKING.md`

---

## Next directions (post iter 014)

Three sleeve-injection iters (012, 013, 014) all show iter 011 is the
constant-weight ceiling. Next iter should pivot:

1. **B.6 — Regime-conditional factor tilt** (highest priority): VBRSIM
   weight = f(12-month value spread or factor momentum). Pre-commit ≤ 3
   configs to avoid the strategy_hunt_loop "regime gate on existing
   winner" DSR-regression trap. Citation `[advances_fin_ml, p.208-211]`
   (PBO discipline) + `[risk_parity, ch.2]` (factor framework).

2. **A.1 — NTSI / NTSE proxy synthesis** (deferred dependency): build
   testfolio-style synth for NTSI (1.5× intl developed) and NTSE
   (1.5× EM) so the literal user thesis (NTSX + NTSI + NTSE + GDE +
   KMLM 5-asset global stack) becomes testable. Direction A.1
   blocked on this synthesis. Effort: 1-2 hours.

3. **C — replace iter 011 sleeves, not augment** (architectural): swap
   NTSX out for NTSI (intl-developed leverage stack) entirely; test
   whether the leverage architecture transports across geographies.
   This is structurally different from iter 014 (additive sleeve) —
   it's a 1:1 component swap.

The user's primary literature thesis (NTSX + GDE + KMLM family +
factor ETFs AVUS/AVDE/SPMO/IDMO/AVUV) has been fully tested at the
constant-weight level. Remaining alpha must come from regime-
conditional weighting OR architectural changes to iter 011's base.

---

*Generated 2026-04-28 by long_term_portfolio loop iter 014.*
