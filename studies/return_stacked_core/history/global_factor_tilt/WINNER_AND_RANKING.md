# Winner conditions + ranking tiers — Global Factor-Tilt Loop

Two separate mechanisms:

1. **WINNER conditions (strict, binary)** — ALL 5 must hold for a
   strategy to be declared winner. This is what halts the shell loop.
2. **Ranking score (0-100) + tiers** — every strategy gets a score,
   so "semi-optimal" strategies are tracked, compared across
   iterations, and fed back into future research directions.

Implementation: `studies/global_factor_tilt_loop/scoring.py`.

---

## Dataset benchmarks (computed 2026-04-26)

| dataset | window | benchmark | Sharpe | CAGR | MDD |
|---|---|---|---|---|---|
| educational | 1970-2026 (56y synth) | VTSIM b&h | **0.6626** | 9.99% | 58.35% |
| vt_real | 2008-06 → 2026-04 (~17y) | VTSIM proxy¹ | **0.5132** | 8.80% | 50.21% |
| ndx_real | 2010-02 → 2026-04 (16y) | QQQ b&h Tiingo | **0.9472** | 18.99% | 35.12% |

¹ VTSIM truncated as proxy for VT live (Tiingo VT.parquet not yet pulled
— TODO: pull VT and re-measure on real data).

---

## Strategy benchmarks (must beat ALL three for full WINNER status)

The scoring rubric below uses dataset benchmarks for points. For full
WINNER status (mandate-grade candidate), the strategy must additionally
**dominate or Pareto-trade-off favorably** vs these 3 strategy
references in long-window comparison (32y window, deploy_studies):

| reference | Sharpe | CAGR | MDD | source |
|---|---|---|---|---|
| **VT 1x b&h** (passive global) | 0.51 | 8.8% | 50.2% | scoring.BENCHMARKS["vt_real"] |
| **Plano C V3_1 v3.5** | 0.671 | 10.94% | 52.43% | `deploy_studies/v1_vs_planoc/` |
| **V_HYBRID + 10% MF** | 0.743 | 10.91% | 44.71% | `deploy_studies/portfolio_variants/` |

V_HYBRID+MF additional metric: `P(rolling 10y CAGR < 5%) = 0.6%` —
candidates must match or beat this robustness.

---

## Part 1 — WINNER conditions (strict)

A strategy counts as **winner** if AND ONLY IF all 5 conditions hold
simultaneously. Near-misses (4/5) still get ranked, but do NOT set
`status: winner`.

### 1. Sharpe edge on real data

`Sharpe_candidate ≥ Sharpe_benchmark + 0.10` on ≥ **2 of 3 datasets**.

| dataset | minimum Sharpe |
|---|---|
| educational | 0.7626 |
| vt_real | 0.6132 |
| ndx_real | 1.0472 |

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

### 3. DSR with per-iteration n_trials (relaxed)

Worst p-value across the 3 datasets < 0.05, using
**`n_trials = configs_tested_this_iteration`** (i.e. the size of the
hyperparameter grid scanned within ONE iteration's hypothesis). This
matches the strategy_hunt_loop 2026-04-25 convention — DSR deflates the
Sharpe estimate by the number of trials within the SAME hypothesis class,
not across structurally orthogonal hypotheses across iterations.

### 4. CAGR not catastrophically below benchmark

`CAGR_candidate ≥ 0.8 × CAGR_benchmark` on ≥ **2 of 3 datasets**.

| dataset | minimum CAGR |
|---|---|
| educational | 7.99% |
| vt_real | 7.04% |
| ndx_real | 15.19% |

### 5. MDD not catastrophically worse

`MDD_candidate ≤ MDD_benchmark + 5 pp` on ≥ **2 of 3 datasets**.

| dataset | maximum MDD |
|---|---|
| educational | 63.35% |
| vt_real | 55.21% |
| ndx_real | 40.12% |

---

## Part 2 — Ranking score + tiers

Same rubric as strategy_hunt_loop. Score 0-100 + 5 bonus, tiers per
score range. WINNER tier requires BOTH score ≥ 90 AND all 5 strict
winner conditions met.

### Scoring rubric (0-100 + 5 bonus)

| # | criterion | max pts | rule |
|---|---|---|---|
| 1 | Sharpe edge | 25 | +10 per dataset where Sharpe ≥ bench + 0.10 (first 2), +5 for all 3 |
| 2 | Gate pass | 25 | 3 pts at min threshold, 5 pts at min+1, 7 pts at 7/7 per dataset; +4 bonus if cross-dataset spec §0 met |
| 3 | DSR | 15 | 15 @ p<0.05 / 10 @ p<0.10 / 5 @ p<0.20 (worst across datasets) |
| 4 | CAGR floor | 15 | 5 pts per dataset where CAGR ≥ 0.8 × bench |
| 5 | MDD ceiling | 15 | 5 pts per dataset where MDD ≤ bench + 5pp |
| 6 | Robustness bonus | 5 | caller-provided (rolling-window consistency) |

Score is clamped to `[0, 100]`. The robustness bonus is optional — if
rolling-window stats aren't computed, criterion 6 = 0 and the max
achievable is 95.

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
conditions met.** This prevents a high score alone from claiming
winner status. For mandate-grade candidate (§7 override deliberation),
the long-window comparison vs the 3 strategy references must
additionally show dominance or favorable Pareto trade-off.

### Reading the tiers

- **🏆 WINNER** — deployment-grade candidate (still needs paper trading
  + mandate §7 override deliberation). Shell loop halts here.
- **🥇 STRONG** — 1-2 conditions shy; investigate further.
- **🥈 PROMISING** — clear edge on some dimension but broken on 1-2
  important criteria. Likely informs future iterations.
- **🥉 MARGINAL** — some credit on some criteria, overall weak.
- **📉 NEAR_FAIL** — close to pure noise.
- **❌ FAIL** — no credit. Add to `DEAD_ENDS.md`.

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

- Strategy has statistical evidence of edge on real data across 3 datasets
- Survives strict cross-dataset validation
- Behaves structurally differently from known dead-ends (this loop's +
  carryover from strategy_hunt_loop)
- Dominates or Pareto-trades-off favorably vs VT, Plano C V3_1 v3.5,
  and V_HYBRID+MF in long-window comparison
- Is a candidate for mandate §7 override to a new path

**Does NOT mean**:

- Auto-deploy live trading — still requires mandate §7 override signed
- Free of all risk
- Repeatable forever — regime changes can invalidate edge
- Clean in paper trading — real-data slippage / execution not tested
