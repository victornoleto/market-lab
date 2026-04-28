# Winner conditions + ranking tiers — Bestfolio Hunt Loop

Two separate mechanisms:

1. **WINNER conditions (strict, binary)** — ALL 5 must hold for a
   strategy to be declared winner. This is what halts the shell loop.
2. **Ranking score (0-100) + tiers** — every strategy gets a score,
   so "semi-optimal" strategies are tracked, compared across
   iterations, and fed back into future research directions.

Implementation: `studies/bestfolio_hunt_loop/scoring.py`.

---

## Dataset benchmarks — iter 009 HAA+Gold (gross, global_factor_tilt_loop Sharpe frontier)

| dataset | window | benchmark | Sharpe | CAGR | MDD |
|---|---|---|---|---|---|
| educational | 1970-2026 (56y synth) | iter009 HAA+Gold edu | **1.120** | 13.89% | 20.81% |
| vt_real | 2008-06 → 2026-04 (~17y) | iter009 HAA+Gold vt_real | **1.061** | 12.87% | 14.20% |
| ndx_real | 2010-02 → 2026-04 (16y) | iter009 HAA+Gold ndx_real | **0.954** | 10.55% | 14.20% |

**Why iter 009 as benchmark?** iter 009 (HAA+KMLM10+GLD5) is the Sharpe
Pareto frontier of the global_factor_tilt_loop (13 iters, 6 winners).
The bestfolio.app #1 strategy (HAA SmartStack) is reported at Sharpe 1.18
over 33y — gap to iter 009 is −0.06. This loop aims to close that gap.

---

## Strategy benchmarks (must beat ALL three for full WINNER status)

For mandate-grade candidate (§7 override deliberation), the strategy
must additionally **dominate or Pareto-trade-off favorably** vs these
3 strategy references:

| reference | Sharpe | CAGR | MDD | source |
|---|---|---|---|---|
| **VT 1x b&h** (passive global) | 0.51 | 8.8% | 50.2% | scoring.BENCHMARKS["vt_real"] (global_factor_tilt_loop) |
| **Plano C V3_1 v3.5** | 0.671 | 10.94% | 52.43% | `deploy_studies/v1_vs_planoc/` |
| **iter 009 HAA+Gold** | 1.120 / 1.061 / 0.954 | 13.89% / 12.87% / 10.55% | 20.81% / 14.20% / 14.20% | `global_factor_tilt_loop iter 009` |

Any WINNER here must Pareto-advance iter 009: higher Sharpe on ≥ 2
datasets (criterion 1), or Sharpe within −0.01 AND CAGR ≥ +2pp, or
MDD ≤ 15% on vt_real while preserving Sharpe.

---

## Part 1 — WINNER conditions (strict)

A strategy counts as **winner** if AND ONLY IF all 5 conditions hold
simultaneously. Near-misses (4/5) still get ranked, but do NOT set
`status: winner`.

### 1. Sharpe edge vs iter 009

`Sharpe_candidate ≥ Sharpe_benchmark + 0.10` on ≥ **2 of 3 datasets**.

| dataset | minimum Sharpe (iter009 + 0.10) |
|---|---|
| educational | 1.220 |
| vt_real | 1.161 |
| ndx_real | 1.054 |

### 2. 7-gate battery (spec §0 cross-dataset)

Simultaneously:

- educational: **≥ 5/7** gates
- vt_real: **≥ 4/7** gates
- ndx_real: **≥ 4/7** gates

Gates (reminder):

- G1 PBO grid-level < 0.5 `[advances_fin_ml, p.208-211]`
- G2 DSR p-value < 0.05 with n_trials = configs tested this iteration `[p.222-223]` (relaxed convention; see §3 below)
- G3 Walk-Forward 6/8 windows, MDD < 25% per window `[ch.12]`
- G4 OOS 70/30 Sharpe > 0
- G5 FWD stress post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0 `[p.196-202]`
- G7 Cross-lib ±3 pp CAGR (numpy-pure reference) `[p.31-34]`

**Note on G3**: iter 009 MDD=20.81% on edu → new benchmark MDD=20.81%.
G3 window MDD ≤ 25% is already tighter than benchmark. Use G3' (adapted
gate) for stacked portfolios (notional > 1.05×): `ref_mdd = iter009_mdd ×
notional_factor`.

### 3. DSR with per-iteration n_trials (relaxed)

Worst p-value across the 3 datasets < 0.05, using
**`n_trials = configs_tested_this_iteration`** (size of the
hyperparameter grid within ONE iteration's hypothesis). Matches
global_factor_tilt_loop convention.

### 4. CAGR not catastrophically below benchmark

`CAGR_candidate ≥ 0.8 × CAGR_benchmark` on ≥ **2 of 3 datasets**.

| dataset | minimum CAGR (0.8 × iter009) |
|---|---|
| educational | 11.11% |
| vt_real | 10.30% |
| ndx_real | 8.44% |

### 5. MDD not catastrophically worse

`MDD_candidate ≤ MDD_benchmark + 5 pp` on ≥ **2 of 3 datasets**.

| dataset | maximum MDD (iter009 + 5pp) |
|---|---|
| educational | 25.81% |
| vt_real | 19.20% |
| ndx_real | 19.20% |

---

## Part 2 — Ranking score + tiers

Score 0-100 + 5 bonus, tiers per score range. WINNER tier requires
BOTH score ≥ 90 AND all 5 strict winner conditions met.

### Scoring rubric (0-100 + 5 bonus)

| # | criterion | max pts | rule |
|---|---|---|---|
| 1 | Sharpe edge | 25 | +10 per dataset where Sharpe ≥ bench + 0.10 (first 2), +5 for all 3 |
| 2 | Gate pass | 25 | 3 pts at min threshold, 5 pts at min+1, 7 pts at 7/7 per dataset; +4 bonus if cross-dataset spec §0 met |
| 3 | DSR | 15 | 15 @ p<0.05 / 10 @ p<0.10 / 5 @ p<0.20 (worst across datasets) |
| 4 | CAGR floor | 15 | 5 pts per dataset where CAGR ≥ 0.8 × bench |
| 5 | MDD ceiling | 15 | 5 pts per dataset where MDD ≤ bench + 5pp |
| 6 | Robustness bonus | 5 | caller-provided (rolling-window consistency) |

Score is clamped to `[0, 100]`.

### Tier mapping

| score | tier (no winner-cond met) | tier (winner-cond met) |
|---|---|---|
| ≥ 90 | 🥇 **STRONG** | 🏆 **WINNER** |
| 75-89 | 🥇 **STRONG** | — |
| 60-74 | 🥈 **PROMISING** | — |
| 40-59 | 🥉 **MARGINAL** | — |
| 20-39 | 📉 **NEAR_FAIL** | — |
| < 20 | ❌ **FAIL** | — |

**WINNER tier requires BOTH score ≥ 90 AND all 5 strict winner
conditions met.**

---

## Decision rules

- **ALL 5 strict conditions + score ≥ 90 → WINNER**: set
  `status: winner` in `BASE_MEMORY.md`, populate `## Winners found`,
  shell loop halts.
- **4/5 conditions OR score 75-89 → STRONG**: document in
  `## Top-K strategies ranked`; investigate further in future iter.
- **3/5 OR score 60-74 → PROMISING**: add to `## Top-K` + note which
  axis was the gap.
- **≤ 2/5 OR score < 60 → not ranked in top-K unless interesting**.

---

## Mandatory reporting per iteration (verdict.json schema)

```json
{
  "status": "winner" | "strong" | "promising" | "marginal" | "near_fail" | "fail",
  "tier": "WINNER" | "STRONG" | "PROMISING" | "MARGINAL" | "NEAR_FAIL" | "FAIL",
  "total_score": 0-100,
  "winner_conditions_met": true | false,
  "criteria": {
    "1_sharpe_edge":     {"points": X, "max": 25, "datasets_beat": N, ...},
    "2_gates":           {"points": X, "max": 25, "per_dataset": {...}, ...},
    "3_dsr":             {"points": X, "max": 15, "worst_p_value": p, ...},
    "4_cagr_floor":      {"points": X, "max": 15, "per_dataset": {...}},
    "5_mdd_ceiling":     {"points": X, "max": 15, "per_dataset": {...}},
    "6_robustness_bonus":{"points": X, "max": 5, ...}
  },
  "metrics_used": {...},
  "benchmarks_used": {...},
  "cumulative_n_trials": X,
  "configs_tested": X,
  "primary_citation": "[book.slug, p.X]"
}
```

Produce by calling `score_strategy(...)` from `scoring.py` and
`.to_dict()` on the result.

---

## What "winner" means (and doesn't)

**Means**:

- Strategy Pareto-advances iter 009 HAA+Gold (global_factor_tilt_loop Sharpe frontier)
- Statistical evidence of edge on real data across 3 datasets
- Survives 7-gate cross-dataset battery
- Is a candidate for mandate §7 override (mandate §1 MAINTENANCE)

**Does NOT mean**:

- Auto-deploy live trading — still requires mandate §7 override signed
- Free of all risk; regime changes can invalidate edge
- Clean in paper trading — real-data slippage / execution not tested
