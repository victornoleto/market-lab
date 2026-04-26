# Winner conditions + ranking tiers

Two separate mechanisms:

1. **WINNER conditions (strict, binary)** — ALL 5 must hold for a
   strategy to be declared winner. This is what halts the shell loop.
2. **Ranking score (0-100) + tiers** — every strategy gets a score,
   so "semi-optimal" strategies are tracked, compared across
   iterations, and fed back into future research directions.

Implementation: `studies/strategy_hunt_loop/scoring.py`
(tests: `tests/test_strategy_scoring.py`).

---

## Benchmarks (real data, measured 2026-04-24)

| dataset | window | benchmark | Sharpe | CAGR | MDD |
|---|---|---|---|---|---|
| educational | 1986-2026 (40y synth) | SPY SPYSIM b&h | **0.68** | 11.47% | 55.14% |
| spy_real | 2009-06-25 → 2026-04-20 | SPY b&h (Tiingo) | **0.90** | 14.97% | 33.70% |
| ndx_real | 2010-02-12 → 2026-04-20 | QQQ b&h (Tiingo) | **0.955** | 19.18% | 35.12% |

---

## Part 1 — WINNER conditions (strict)

A strategy counts as **winner** if AND ONLY IF all 5 conditions hold
simultaneously. Near-misses (4/5) still get ranked, but do NOT set
`status: winner`.

### 1. Sharpe edge on real data

`Sharpe_candidate ≥ Sharpe_benchmark + 0.10` on ≥ **2 of 3 datasets**.

| dataset | minimum Sharpe |
|---|---|
| educational | 0.78 |
| spy_real | 1.00 |
| ndx_real | 1.055 |

### 2. 7-gate battery (spec §0 cross-dataset)

Simultaneously:

- educational: **≥ 5/7** gates
- spy_real: **≥ 4/7** gates
- ndx_real: **≥ 4/7** gates

Gates (reminder):

- G1 PBO grid-level < 0.5 `[advances_fin_ml, p.208-211]`
- G2 DSR p-value < 0.05 with n_trials = configs tested this iteration `[p.222-223]` (relaxed 2026-04-25; see §3 below)
- G3 Walk-Forward 6/8 windows, MDD < 25% per window `[ch.12]`
- G4 OOS 70/30 Sharpe > 0
- G5 FWD stress post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0 `[p.196-202]`
- G7 Cross-lib ±3 pp CAGR (numpy-pure reference) `[p.31-34]`

### 3. DSR with per-iteration n_trials (relaxed 2026-04-25)

Worst p-value across the 3 datasets < 0.05, using
**`n_trials = configs_tested_this_iteration`** (i.e. the size of the
hyperparameter grid scanned within ONE iteration's hypothesis).

**Rationale for the change**: the previous convention used
`cumulative_n_trials` summed across the entire hunt loop's history.
That conflates **independent hypotheses** (each iter tests a fundamentally
different mechanism — sector momentum vs vol-target vs static stack)
into a single multiple-comparison budget, which is statistically incorrect.
DSR is meant to deflate the Sharpe estimate by the number of trials
within the SAME hypothesis class, not across structurally orthogonal
hypotheses. By iter 074 the cumulative budget reached 4 381, requiring
Sharpe ≈ 1.4 to clear p<0.05, which is a 3.5σ bar over the noise floor
— masochistic and not aligned with academic DSR usage.

The new convention treats each iteration as an independent experiment.
Iters from 075 onwards use this convention natively; iters 002-074 are
re-scored retroactively in `verdict_v2.json` files alongside the
original `verdict.json`. The Top-K table in `BASE_MEMORY.md` reflects
the v2 (relaxed) scores from 2026-04-25 onwards.

The historical `cumulative_n_trials` field is preserved in verdicts
for audit and is still tracked in `BASE_MEMORY.md` frontmatter, but it
no longer enters the DSR p-value calculation.

### 4. CAGR not catastrophically below benchmark

`CAGR_candidate ≥ 0.8 × CAGR_benchmark` on ≥ **2 of 3 datasets**.

| dataset | minimum CAGR |
|---|---|
| educational | 9.18% |
| spy_real | 11.98% |
| ndx_real | 15.35% |

### 5. MDD not catastrophically worse

`MDD_candidate ≤ MDD_benchmark + 5 pp` on ≥ **2 of 3 datasets**.

| dataset | maximum MDD |
|---|---|
| educational | 60.14% |
| spy_real | 38.70% |
| ndx_real | 40.12% |

---

## Part 2 — Ranking score + tiers

Purpose: make "semi-optimal" strategies visible across iterations.
A strategy scoring 78 today may inform the design of the eventual
winner in iteration N+5.

### Scoring rubric (0-100 + 5 bonus)

The `score_strategy()` helper in `scoring.py` computes a 100-point
base score + up to 5 bonus points (robustness):

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
winner status.

### Reading the tiers

- **🏆 WINNER** — deployment-grade (still needs paper trading + mandate
  §7 override). Shell loop halts here.
- **🥇 STRONG** — 1-2 conditions shy of winner; may become winner with
  minor refinement (parameter tune, different data window). Investigate.
- **🥈 PROMISING** — clear signal of edge on some dimension but broken
  on 1-2 important criteria. Likely informs future iterations.
- **🥉 MARGINAL** — some credit on some criteria, but overall weak.
  Log for pattern recognition; not actionable.
- **📉 NEAR_FAIL** — one or two sub-metrics ok, rest broken. Close to
  pure noise.
- **❌ FAIL** — no credit. Direction is a dead-end; add to `DEAD_ENDS.md`.

### Example: iter 001 crash-protected candidate

Top candidate `EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05`
(`studies/ema_sma_threshold_crash_protected/analysis_top_candidate/`):

| dataset | Sharpe | CAGR | MDD | gates |
|---|---|---|---|---|
| educational | 0.87 | 24.01% | 44.55% | 6/7 |
| spy_real | 0.68 | 18.09% | 43.77% | 3/7 |
| ndx_real | ~0.70 | ~19% | ~50% | 3/7 |

Scoring breakdown:

- Criterion 1 (Sharpe edge): only educational beats (0.87 > 0.78);
  spy/ndx fail → **10 pts**
- Criterion 2 (Gates): edu 6/7 → 5 pts; spy 3/7 → 0 pts (< 4 min);
  ndx 3/7 → 0 pts. No cross-dataset bonus. → **5 pts**
- Criterion 3 (DSR): worst p > 0.20 → **0 pts**
- Criterion 4 (CAGR floor): all 3 datasets pass → **15 pts**
- Criterion 5 (MDD ceiling): edu 44.55% ≤ 60.14% ✓; spy 43.77% >
  38.70% ✗; ndx ~50% > 40.12% ✗. 1/3 passes → **5 pts**
- **Total ≈ 35 → 📉 NEAR_FAIL**

(See `tests/test_strategy_scoring.py::TestNearMiss` for exact
verified approximation.)

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
- Survives strict cross-dataset validation with cumulative n_trials penalty
- Behaves structurally differently from known dead-ends
- Is a candidate for mandate §7 override to Path B

**Does NOT mean**:

- Auto-deploy live trading — still requires mandate §7 override signed
- Free of all risk — 5 pp MDD above SPY is still painful
- Repeatable forever — regime changes can invalidate edge
- Clean in paper trading — real-data slippage / execution not tested
