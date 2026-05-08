# Winner conditions + ranking tiers — Long-Term Portfolio Loop

Two separate mechanisms:

1. **WINNER conditions** — must hold for a strategy to be declared winner.
   This is what halts the shell loop.
2. **Ranking score (0-100) + tiers** — every strategy gets a score,
   so "semi-optimal" strategies are tracked, compared across
   iterations, and fed back into future research directions.

Implementation: `studies/long_term_portfolio/scoring.py`.

> **Mandate reframing 2026-04-29** (user-approved A.1-A.4): SPY-only baseline
> (was avg(SPY,VT)), Sharpe edge **+0.05** (was +0.10), CAGR floor **WARNING-ONLY**
> (does not block winner_conditions_met), MDD ≤ SPY **strictly** (was +5pp
> slack). Iters 001-022 retain LEGACY scoring (cross-iter consistency); iter
> 023+ uses NEW. Citations: `[advances_fin_ml, p.222-223]` (DSR), `[risk_parity, ch.5]`.

---

## Dataset benchmarks — SPY-only (NEW primary) and avg(SPY,VT) (LEGACY)

`scoring.py` `BENCHMARKS` dict is the single source of truth (per-dataset
{spy, vt|qqq}); values below echo for human reference.

### NEW primary — SPY-only (mandate reframing 2026-04-29)

| dataset | window | benchmark | Sharpe | CAGR | MDD |
|---|---|---|---|---|---|
| **lh_56y** | 1970-01 → 2026-04 (56y synth) | SPYSIM 40y synth | **0.680** | 11.47% | 55.14% |
| **vt_real** | 2008-06 → 2026-04 (~17y) | SPY Tiingo 17y | **0.900** | 14.97% | 33.70% |
| **ndx_real** | 2010-02 → 2026-04 (16y) | SPY Tiingo 16y | **0.900** | 14.97% | 33.70% |

Used by `primary_benchmarks()` for iter 023+ scoring.

### LEGACY — avg(SPY 1× b&h, VT 1× b&h) (gross-of-tax)

| dataset | window | benchmark (avg of) | Sharpe | CAGR | MDD (worst) |
|---|---|---|---|---|---|
| **lh_56y** | 1970-01 → 2026-04 (56y synth) | VTSIM 56y + SPYSIM 40y synth | **0.671** | 10.73% | 58.35% |
| **vt_real** | 2008-06 → 2026-04 (~17y) | VTSIM proxy 17y + SPY Tiingo 17y | **0.707** | 11.89% | 50.21% |
| **ndx_real** | 2010-02 → 2026-04 (16y) | QQQ Tiingo 16y + SPY Tiingo 16y | **0.924** | 16.98% | 35.12% |

Used by `legacy_benchmarks()` — kept for cross-iter compat (iters 001-022).

(Legacy `educational` is a deprecated alias for `lh_56y`; same numbers.)

**Why avg(SPY,VT) and not iter 009?** iter 009 came from the predecessor
`global_factor_tilt_loop` (gross-only) and the comparison was apples-to-oranges
once net-of-tax got involved. The user's actual deploy reference is "beat the
average of buy-and-hold SPY and VT by ≥0.10 Sharpe gross", which is what
`scoring.py` now enforces. **iter 011** (NTSX+GDE+KMLM 35/25/40 static) cleared
this bar 2026-04-28 (Sharpe 1.021/0.960/1.104 gross, +0.35/+0.25/+0.18 vs
avg(SPY,VT)) and became the substantive incumbent; **iter 014** (intl-equity
tilt) holds the rule-mechanical incumbent slot per `BASE_MEMORY` but loses
Sharpe to iter 011 on 2/3 datasets — see BASE_MEMORY caveat.

---

## Substantive context references (Pareto-advance check, not gating)

A WINNER tier here is enough to halt the shell loop. For mandate §7 override
deliberation, additionally Pareto-compare the candidate vs these 3 strategy
references (informational, not gating):

| reference | window context | Sharpe | CAGR | MDD | source |
|---|---|---|---|---|---|
| **VT 1× b&h** (passive global) | vt_real 17y | 0.51 | 8.8% | 50.2% | scoring.BENCHMARKS["vt_real"]["vt"] |
| **Plano C V3_1 v3.5** | educational 31y net | 0.671 | 10.94% | 52.43% | `deploy_studies/v1_vs_planoc/` |
| **iter 011 NTSX+GDE+KMLM** (substantive incumbent) | lh_56y 40y / vt_real 17y / ndx_real 16y gross | 1.046 / 0.960 / 1.104 | 11.78% / 10.95% / 11.64% | 29.5% / 21.2% / 14.1% | `iterations/011-*/verdict.json` |
| **iter 014 NTSX+VXUS+GDE+KMLM** (mechanical incumbent) | lh_56y 40y / vt_real 17y / ndx_real 16y gross | 1.055 / 0.885 / 1.052 | 11.78% / 11.14% / 12.11% | 29.5% / 28.0% / 18.4% | `iterations/014-*/verdict.json` |
| ~~iter 009 HAA+Gold~~ (predecessor loop ref, retained for cross-loop continuity) | edu 31y / vt_real 17y / ndx_real 16y net | 1.120 / 1.061 / 0.954 | 13.89% / 12.87% / 10.55% | 20.81% / 14.20% / 14.20% | `global_factor_tilt_loop iter 009` |

Pareto-advance check (informational): higher Sharpe on ≥ 2 datasets vs iter 011
(the substantive incumbent), or Sharpe within −0.01 AND CAGR ≥ +2pp, or MDD
≤ 15% on vt_real while preserving Sharpe.

---

## Part 1 — WINNER conditions (post-reframing 2026-04-29)

A strategy counts as **winner** if 4 active gating conditions hold
simultaneously. CAGR floor (the prior 5th) is now WARNING-ONLY — still
scored 15 pts in the rubric and reported in verdict.json, but does not
block tier=WINNER. Near-misses still get ranked but do NOT set
`status: winner`.

### 1. Sharpe edge vs SPY per dataset (A.2)

`Sharpe_candidate ≥ spy_benchmark.sharpe + 0.05` on ≥ **2 of 3 datasets**
(`spy_benchmark` per `scoring.spy_benchmark()`; default in
`scoring.primary_benchmarks()`).

| dataset | NEW minimum Sharpe (SPY + 0.05) | LEGACY (avg + 0.10, iters 001-022) |
|---|---:|---:|
| lh_56y | 0.730 | 0.771 |
| vt_real | 0.950 | 0.807 |
| ndx_real | 0.950 | 1.024 |

**Note**: NEW vt_real hurdle (0.950) is **substantially harder** than LEGACY
(0.807) because VT proxy 17y was Sharpe 0.51 (intl-equity drag in
2010-2024 regime) and averaging dragged the bar down artificially. SPY
17y (0.90) is the actual investable baseline.

### 2. 7-gate battery (spec §0 cross-dataset)

Simultaneously:

- lh_56y: **≥ 5/7** gates
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

**Note on G3**: avg(SPY,VT) MDD on lh_56y = 58.35% (passive equity through
1973-74, 2000-02, 2008 GFC). G3 window MDD ≤ 25% is much tighter than
benchmark — pure passive can't pass. Use G3' (adapted gate) for stacked
portfolios (notional > 1.05×): `ref_mdd = avg_bm_mdd × notional_factor`.

### 3. DSR (cumulative n_trials, capped per-iter for tractability)

`scoring.score_strategy(...)` is called with **`cumulative_n_trials`** (sum
of all configs tested across the loop's lifetime; iter 014 was 52). Worst
p-value across the 3 datasets must be < 0.05. The relaxed PROMPT.md
convention of `n_trials = configs_this_iter` was superseded once iter 011
established a substantive incumbent.

### 4. CAGR floor (WARNING-ONLY since 2026-04-29 — A.3)

`CAGR_candidate ≥ 0.8 × CAGR_benchmark` on ≥ **2 of 3 datasets**.

| dataset | NEW (SPY × 0.8) | LEGACY (avg × 0.8) |
|---|---:|---:|
| lh_56y | 9.18% | 8.58% |
| vt_real | 11.98% | 9.51% |
| ndx_real | 11.98% | 13.59% |

**WARNING-ONLY (not gating)**: still 15 pts in the rubric, reported in
verdict.json, but does NOT block `winner_conditions_met`. Rationale:
defensive Sharpe-frontier strategies (iter 020 Browne All-Weather, iter 019
vol-managed) deserve WINNER consideration when they trade CAGR for MDD by
design. `[risk_parity, ch.5]` — risk-parity frontier explicitly sacrifices
CAGR for Sharpe.

### 5. MDD ceiling — strict ≤ SPY (A.4)

`MDD_candidate ≤ MDD_benchmark` on ≥ **2 of 3 datasets** (NEW: 0pp slack;
LEGACY had +5pp slack).

| dataset | NEW (SPY MDD strict) | LEGACY (worst-of-bench + 5pp) |
|---|---:|---:|
| lh_56y | 55.14% | 63.35% |
| vt_real | 33.70% | 55.21% |
| ndx_real | 33.70% | 40.12% |

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

- Strategy beats avg(SPY 1× b&h, VT 1× b&h) gross Sharpe by ≥ 0.10 on ≥ 2 of 3 datasets
- Statistical evidence of edge on real data across 3 datasets (DSR / PBO / WF)
- Survives 7-gate cross-dataset battery
- Is a candidate for mandate §7 override (mandate §1 MAINTENANCE)
- Pareto-comparison vs iter 011 (substantive incumbent) is informational, not gating — see "Substantive context references" §

**Does NOT mean**:

- Auto-deploy live trading — still requires mandate §7 override signed
- Free of all risk; regime changes can invalidate edge
- Clean in paper trading — real-data slippage / execution not tested
