# Iter 016 — Final report: B.5 — UMD (Fama-French momentum) overlay direto sobre iter 011

**Date**: 2026-04-28
**Hypothesis**: see `hypothesis.md`
**Slug**: `B5-UMD-overlay`
**Selected config**: `umd_heavy_3025_20_25` = 30% NTSX + 25% GDE + 20% KMLM + 25% UMD
**Selection rule**: max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets

---

## Verdict

**Tier**: 🏆 **WINNER** (score **91/100**, all 5 strict winner conditions met vs avg(SPY,VT))

**Beats incumbent**: ⚠️ **`false`** (mechanically) **— but substantively a real positive signal**:
- Score 91 < iter 014's 93 → fails score gate.
- Sharpe edge vs iter 014 ≥ +0.10 only on 1/3 datasets (lh_56y +0.168). Fails ≥2/3.
- **HOWEVER**: vs iter 011 substantive incumbent, ALL 4 configs win 2/3 datasets
  (lh_56y + ndx_real positive, vt_real within ±0.02). Strict-window check on selected:
  +0.088 / −0.016 / +0.047 — narrowly misses the +0.10 strict hurdle on lh_56y.
- **Critically**: this is the **first iter (out of 5 since iter 011) where live
  windows do NOT monotonically regress** as the new factor weight rises.

**No KILL fires.** First positive structural signal since iter 011.

---

## Headline metrics — selected config (gross-of-tax, gating dimension)

| dataset | gross Sharpe (loose) | gross Sharpe (strict) | gross CAGR | gross MDD | benchmark avg(SPY,VT) Sh | edge vs bench | gates |
|---|---:|---:|---:|---:|---:|---:|---:|
| **lh_56y**   | **1.223** | **1.133** | 12.19% | 22.09% | 0.671 | **+0.551** | 7/7 |
| **vt_real**  | **0.943** | **0.944** | 10.09% | 22.09% | 0.707 | **+0.237** | 6/7 |
| **ndx_real** | **1.150** | **1.151** | 11.77% | 13.60% | 0.924 | **+0.227** | 6/7 |

3/3 datasets clear the +0.10 Sharpe-edge gate vs avg(SPY,VT) → criterion 1 = 25/25.

**Net = Gross** (static stack, AnnualDarfEngine tax-perfect; same property as iter 011/014/015).

---

## Comparison vs incumbents (loose convention)

| dataset | iter 016 sel S | iter 014 (mech inc) S | Δ vs iter 014 | iter 011 (subst inc) S | Δ vs iter 011 |
|---|---:|---:|---:|---:|---:|
| lh_56y    | **1.223** | 1.055 | **+0.168** ✅ | 1.046 | **+0.177** ✅ |
| vt_real   | 0.943 | 0.885 | +0.058 | 0.960 | −0.017 |
| ndx_real  | 1.150 | 1.052 | +0.098 | 1.104 | +0.046 |

Strict-window comparison (all configs, lh_56y):

| config | UMD % | lh_56y loose | lh_56y **strict** | iter 011 strict | strict edge |
|---|---:|---:|---:|---:|---:|
| `umd_lite_3525_30_10`     | 10% | 1.161 | 1.072 | 1.045 | +0.027 |
| `umd_mod_3525_25_15`      | 15% | 1.170 | 1.080 | 1.045 | +0.035 |
| `umd_balanced_3525_20_20` | 20% | 1.175 | 1.085 | 1.045 | +0.040 |
| `umd_heavy_3025_20_25` ✅ | 25% | 1.223 | **1.133** | 1.045 | **+0.088** |

Strict-window edge of selected config (+0.088) is below the +0.10 hurdle but
**substantively positive on 2 of 3 datasets** (lh_56y +0.088, ndx_real +0.047,
vt_real −0.016). This is the first iter where the strict accounting also
shows a positive edge on the long-history window.

---

## Per-config grid — monotonic finding

| config | UMD % | lh_56y S | vt_real S | ndx_real S |
|---|---:|---:|---:|---:|
| `umd_lite_3525_30_10`     | 10% | 1.161 | **0.970** | 1.145 |
| `umd_mod_3525_25_15`      | 15% | 1.170 | 0.965 | 1.155 |
| `umd_balanced_3525_20_20` | 20% | 1.175 | 0.954 | 1.156 |
| `umd_heavy_3025_20_25` ✅ | 25% | **1.223** | 0.943 | 1.150 |

**Cross-config pattern (NEW for this loop):**
- **lh_56y**: monotonic UPWARD as UMD weight rises (1.161 → 1.223, +0.062 over 15pp UMD).
- **vt_real**: very gentle monotonic decline (0.970 → 0.943, −0.027 over 15pp UMD; all > 0.94).
- **ndx_real**: peaks at UMD=20% (1.156), comes back to 1.150 at UMD=25% — essentially flat.

**This is qualitatively different from iters 013/014/015**, where the new factor
weight monotonically REDUCED Sharpe on live windows. UMD does not have the
"death of value" or "intl-equity drag" failure mode in 2010-2026.

---

## Pre-committed kill criteria — none fired

| KILL # | Criterion | Status |
|---|---|---|
| **#1** | Best-of-grid loses iter 011 on ≥ 2/3 datasets | **NOT FIRED**: best wins lh_56y and ndx_real, loses by −0.017 on vt_real (within noise). |
| **#2** | Monotonic Sharpe regression with UMD weight on ≥ 2 datasets | **NOT FIRED**: lh_56y monotonic UP; vt_real gentle down (−0.03 range); ndx_real flat. |

**No KILL fires** — first iter since iter 011 to clear the structural soundness check.

---

## Score breakdown (per `scoring.py`)

| # | criterion | iter 016 pts / max | iter 015 | iter 014 | iter 011 |
|---|---|---:|---:|---:|---:|
| 1 | Sharpe edge vs avg(SPY,VT) +0.10 | **25 / 25** | 25 | 25 | 25 |
| 2 | Gate pass + cross-dataset bonus | **21 / 25** (lh_56y 7/7, vt 6/7, ndx 6/7, +0 cross-ds) | 23 | 23 | 21 |
| 3 | DSR worst p < 0.05 (cumulative_n_trials=60) | **15 / 15** (worst p=1.78e-3) | 15 | 15 | 15 |
| 4 | CAGR floor (0.8 × bench, ≥ 2/3) | **10 / 15** (lh_56y ✓, vt ✓, ndx ✗ — 11.77% < 13.59%) | 10 | 10 | 10 |
| 5 | MDD ceiling (bench + 5pp, ≥ 2/3) | **15 / 15** (3/3 pass) | 15 | 15 | 15 |
| 6 | Robustness bonus (rolling 5y) | **5 / 5** | 5 | 5 | n/a |
| **total** | | **91 / 100** | 93 | 93 | 91 |

**iter 016 vs iter 014 (-2 pts)**: gate 21 vs 23 — vt_real and ndx_real
each lose 1 gate (G1 PBO fails 0.557/0.567 on live windows, similar to
iter 011's selection-within-family PBO failure).

---

## Gate detail — selected config

| dataset | G1 PBO | G2 DSR p | G3 WF (max win MDD) | G4 OOS Sh | G5 FWD Sh | G6 boot CI low | G7 cross-lib |
|---|---:|---:|---:|---:|---:|---:|---:|
| lh_56y    | **0.000** ✓ | **1.78e-15** ✓ | **✓** (max=22.09% < 25%) | 1.245 ✓ | 1.220 ✓ | 0.832 ✓ | ✓ |
| vt_real   | **0.557** ✗ | **1.78e-3** ✓ | ✓ (max=22.09%) | 1.207 ✓ | 1.220 ✓ | 0.305 ✓ | ✓ |
| ndx_real  | **0.567** ✗ | **2.25e-4** ✓ | ✓ (max=13.60%) | 1.057 ✓ | 1.220 ✓ | 0.486 ✓ | ✓ |

**Gate failures**: G1 PBO on vt_real and ndx_real (0.55-0.57 > 0.5 threshold).
**Same family-selection PBO failure mode as iter 011** — the 4 UMD configs
are tightly clustered in Sharpe (vt_real range 0.943-0.970, ndx_real range
1.145-1.156), so PBO sees the ranking noise as overfitting. Signal is
"any UMD overlay 10-25% works", not "specifically 25% works".

**lh_56y G3 WF passes** — first iter with full 7/7 on lh_56y. Max WF window
MDD 22.09% < 25% threshold. UMD's positive performance during the 1973-74,
2008, 2020 crises (momentum is a "loser-shorter") helps cap window MDDs.

---

## Pareto comparison

| candidate | window | Sharpe (loose) | Sharpe (strict) | CAGR | MDD | source |
|---|---|---:|---:|---:|---:|---|
| **iter 016** (this) | lh_56y 40y eff | **1.223** | **1.133** | 12.19% | 22.09% | this report |
| iter 016 | vt_real 17y | 0.943 | 0.944 | 10.09% | 22.09% | this |
| iter 016 | ndx_real 16y | 1.150 | 1.151 | 11.77% | 13.60% | this |
| iter 014 (mech inc) | lh_56y 40y eff | 1.055 | n/a | 11.78% | 29.52% | iter 014 |
| iter 011 (subst inc) | lh_56y 40y | 1.046 | 1.045 | 11.78% | 26.04% | iter 011 / smoke-test |
| iter 015 (last) | lh_56y 40y eff | 1.081 | 1.007 | 11.63% | 27.99% | iter 015 |
| iter 013 (DE-014) | lh_56y 40y eff | 1.126 ⭐ | n/a | 12.32% | 25.73% | DE-014 |
| **avg(SPY,VT)** (lh_56y bench) | — | 0.671 | — | 10.73% | 58.35% | scoring.BENCHMARKS |

**Pareto position**: iter 016 dominates avg(SPY,VT) on all 3 dimensions on
all 3 datasets. **Dominates iter 011** on lh_56y and ndx_real (Sharpe AND
MDD), loses by 0.02 Sharpe on vt_real but with similar MDD. **Strict-window
also positive** (rare in this loop). Best Sharpe found in the long-term
portfolio loop on lh_56y (loose 1.223; strict 1.133 — both higher than any
iter 011-015 strict).

---

## What the data tells us — structural insight

UMD is **a structurally distinct factor** from VBRSIM (size+value) and
VXUSSIM/NTSI (geographic). Three differences:

1. **Long-history Sharpe**: UMD raw 0.75 vs VBRSIM raw ~0.5 vs VXUSSIM raw
   ~0.5. Higher Sharpe per unit of factor weight.
2. **2010-2026 regime behavior**: momentum had multiple positive years
   (2017, 2019, 2020 recovery, 2021, 2023-2024) when value was flat. Less
   regime-mismatch with US-large-cap dominance.
3. **Crisis tail behavior**: cross-sectional momentum has a "long winners,
   short losers" structure that produces convex returns during prolonged
   crises (2008, 2020) — momentum had POSITIVE 2008 (+15% UMD) when value
   tanked (−15% size). This is visible in iter 016's lh_56y G3 WF passing
   (max window MDD 22.09% < 25%) where iter 014/015 failed (28-29%).

**The implication**: factor diversification works when the factor is
qualitatively orthogonal to existing exposures, not just labeled "different".
VBRSIM was correlated to value-cycle drag; VXUSSIM was correlated to intl-
equity drag; **UMD has its own crisis behavior** uncorrelated to either.

**Critical caveat — UMD is academic, not investable as-is**: UMD daily
includes the long-short gross-of-cost premium. Investable momentum products
(MTUM, SPMO, IDMO, AVUS factor sleeves) capture roughly 50-70% of UMD due
to long-only constraint, factor exposure dilution, and trading costs. The
1.223 lh_56y Sharpe likely shrinks to 1.05-1.15 with an investable proxy
(MTUM live since 2013). **Iter 017 (B.6 regime-gated VBRSIM) should test
whether a similar regime-gating signal can be applied to investable momentum
ETFs — that's the deploy-relevant follow-up.**

---

## Lesson

**UMD overlay is the first direction since iter 011 to genuinely improve
Sharpe across multiple datasets without monotonic regression on live
windows.** The selected config (UMD 25%) wins iter 011 by +0.18 lh_56y / +0.05
ndx_real loose (+0.09 / +0.05 strict), with vt_real within −0.02. All 4 UMD
configs share this property — the result is family-level, not config-level.

**However:**
1. Score 91 < iter 014's 93 — gate-count drop on PBO (within-family selection).
2. Strict-window edge +0.088 on lh_56y narrowly misses the +0.10 substantive
   ADVANCE hurdle.
3. UMD is academic; investable momentum captures ~60-70% → real-world deploy
   would shrink the edge to ~+0.05 lh_56y, marginal.

**Verdict**: positive signal, but not a substantive incumbent advance. Two
viable follow-ups:
- **iter 017 (B.6, VBRSIM regime-gated)**: test whether regime-gating
  unlocks a Sharpe edge from value/intl factors (closing the loop on
  why iter 013 and iter 014 failed).
- **investable momentum sub-iter (deferred)**: test MTUM/SPMO live
  series instead of academic UMD; quantify the gap.

---

## Citations

- **UMD academic momentum**: `[stocks_on_the_move, p.21-30]` Clenow;
  Jegadeesh-Titman 1993 momentum effect; Fama-French daily UMD via
  `studies.long_term_portfolio.ff_momentum_proxy`.
- **Capital-efficient stacking core (NTSX/GDE retained)**: `[risk_parity, ch.5, p.10]`
- **Factor framework**: `[risk_parity, ch.2, p.37-41]`
- **Gates**: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`
- **Scoring rubric**: `studies/long_term_portfolio/WINNER_AND_RANKING.md`

---

## Next directions (post iter 016)

iter 016 is the first POSITIVE result in 5 iters. Next iters preserve the
breadth-search plan:

1. **iter 017 — B.6 VBRSIM regime-gated** (next): test whether regime-gating
   recovers the value factor that iter 013 found subordinate. If it works,
   it's a complementary signal to iter 016's UMD; if not, B-direction
   regime-gating is also closed.
2. **iter 018 — C.1 Antonacci GEM cross-class top-K**: qualitatively
   different mechanism (dynamic, not static).
3. **iter 019-022**: continue C-direction breadth.

After all of 016-022, expect a Pareto frontier of 1-3 substantively-WINNER
strategies that the user can then deep-dive into for deploy-readiness.

---

*Generated 2026-04-28 by long_term_portfolio loop iter 016.*
