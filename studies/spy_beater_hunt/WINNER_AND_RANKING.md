# Winner conditions + ranking tiers — spy_beater_hunt

Two separate mechanisms (same pattern as long_term_portfolio):

1. **WINNER conditions** — must hold for a strategy to be declared winner. This is what halts the hunt.
2. **Ranking score (0-100) + tiers** — every strategy gets a score, so "semi-optimal" strategies are tracked, compared across iterations, and fed back into future research.

---

## Part 1 — WINNER conditions (3 strict bars, ALL must hold)

### Bar 1: CAGR bar — mean CAGR ≥ SPY mean (13.80%)

`mean(CAGR_lh_56y, CAGR_vt_real, CAGR_ndx_real) ≥ 0.1380`

This is the **primary user-facing criterion**. SPY mean CAGR across our 3 datasets is 13.80% (lh_56y 11.47% + vt_real 14.97% + ndx_real 14.97%, divided by 3).

### Bar 2: MDD bar — mean MDD ≤ SPY mean (40.85%)

`mean(MDD_lh_56y, MDD_vt_real, MDD_ndx_real) ≤ 0.4085`

SPY MDD across 3 datasets is 40.85% (lh_56y 55.14% + vt_real 33.70% + ndx_real 33.70%, divided by 3). Strategies that beat CAGR bar but explode in MDD are not winners.

### Bar 3: 7-gate battery (≥ 2/3 datasets)

Same as long_term_portfolio:
- lh_56y: ≥ 5/7 gates
- vt_real: ≥ 4/7 gates  
- ndx_real: ≥ 4/7 gates

Where gates are:
- G1 PBO grid-level < 0.5 `[advances_fin_ml, p.208-211]`
- G2 DSR p-value < 0.05 with cumulative_n_trials `[p.222-223]`
- G3 Walk-Forward 6/8 windows, MDD < 25% per window `[ch.12]`
- G4 OOS 70/30 Sharpe > 0
- G5 FWD stress post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0 `[p.196-202]`
- G7 Cross-lib ±3 pp CAGR `[p.31-34]`

---

## Part 2 — Ranking score (0-100) + tiers

### Scoring rubric (0-100 + 5 bonus)

| # | criterion | max pts | rule |
|---|---|---|---|
| 1 | **CAGR vs SPY** | 30 | 30 × clamp((mean_cagr − 0.05) / (0.20 − 0.05), 0, 1) — anchored on 5%/20% range, SPY 13.80% gives 0.5867 × 30 = 17.6 |
| 2 | **MDD vs SPY** | 20 | 20 × clamp((0.50 − mean_mdd) / (0.50 − 0.10), 0, 1) — anchored on 50%/10% range, SPY 40.85% gives 0.229 × 20 = 4.6 |
| 3 | Gate pass | 20 | 3 pts at min threshold per dataset, +5 bonus if cross-dataset spec §0 met |
| 4 | DSR | 10 | 10 @ p<0.05 / 7 @ p<0.10 / 3 @ p<0.20 (worst across datasets) |
| 5 | Sharpe quality | 10 | 10 × clamp((mean_sharpe − 0.50) / 1.50, 0, 1) — anchored on 0.5/2.0 range |
| 6 | Robustness bonus | 10 | rolling 5y window % positive Sharpe |
| 7 | Bonus | +5 | caller-provided (regime-spread, breadth, etc.) |

Score is clamped to [0, 100]. Note: this rubric **prioritizes CAGR (30pts) over Sharpe (10pts)** intentionally — opposite of long_term_portfolio's Sharpe-first rubric.

### Tier mapping

| score | tier (3 bars met) | tier (1-2 bars met) | tier (0 bars met) |
|---|---|---|---|
| ≥ 90 | 🏆 **WINNER** | 🥇 STRONG (near-miss) | 🥇 STRONG |
| 75-89 | 🥇 STRONG | 🥇 STRONG | 🥈 PROMISING |
| 60-74 | 🥈 PROMISING | 🥈 PROMISING | 🥉 MARGINAL |
| 40-59 | 🥉 MARGINAL | 🥉 MARGINAL | 📉 NEAR_FAIL |
| < 40 | 📉 NEAR_FAIL | ❌ FAIL | ❌ FAIL |

**WINNER tier requires BOTH score ≥ 90 AND all 3 strict bars met simultaneously.**

---

## Decision rules

- **All 3 bars + score ≥ 90 → WINNER**: set `status: winner` in `BASE_MEMORY.md`, halt hunt, write final report comparing vs F1+SPLIT.
- **2/3 bars OR score 75-89 → STRONG**: continue hunt; this is a candidate that proved possibility.
- **1/3 bars OR score 60-74 → PROMISING**: document, possibly extend.
- **0 bars OR score < 60 → MARGINAL/FAIL**: close direction, log lesson.

---

## Mandatory reporting per iteration (verdict.json schema)

```json
{
  "status": "winner" | "strong" | "promising" | "marginal" | "near_fail" | "fail",
  "tier": "WINNER" | "STRONG" | "PROMISING" | "MARGINAL" | "NEAR_FAIL" | "FAIL",
  "total_score": 0-100,
  "winner_conditions_met": true | false,
  "bars": {
    "cagr_bar": true | false,
    "mdd_bar": true | false,
    "gates_bar": true | false
  },
  "criteria": {
    "1_cagr": {"points": X, "max": 30, "mean_cagr": ...},
    "2_mdd":  {"points": X, "max": 20, "mean_mdd": ...},
    "3_gates": {"points": X, "max": 20, "per_dataset": {...}},
    "4_dsr": {"points": X, "max": 10, "worst_p_value": ...},
    "5_sharpe": {"points": X, "max": 10, "mean_sharpe": ...},
    "6_robustness": {"points": X, "max": 10, "pct_positive": ...},
    "7_bonus": {"points": X, "max": 5}
  },
  "metrics_used": {"lh_56y": {...}, "vt_real": {...}, "ndx_real": {...}},
  "spy_benchmark": {"cagr_mean": 0.1380, "mdd_mean": 0.4085},
  "cumulative_n_trials": X,
  "configs_tested": X,
  "primary_citation": "[book.slug, p.X]"
}
```

---

## What "winner" means here (and doesn't)

**Means**:
- Strategy beats SPY in BOTH CAGR (≥ 13.80%) AND MDD (≤ 40.85%) on a 3-dataset mean basis
- Statistical evidence of edge survives PBO/DSR/WF gates on ≥ 2/3 datasets
- Is a candidate for mandate §7 override request

**Does NOT mean**:
- Auto-deploy live trading — still requires mandate §7 override signed
- Free of all risk; regime changes can invalidate edge
- Strictly better than F1+SPLIT in all scenarios — F1+SPLIT might still be preferable for risk-averse deployment given lower MDD

---

## Anchor notes

- The CAGR bar (13.80%) is **dragged up by 2008-2024 vt_real/ndx_real** (14.97% each). lh_56y SPY is 11.47% only. F1+SPLIT lh_56y CAGR 11.52% **already beats SPY** in 40y window.
- This means the hunt is mostly looking for strategies that match SPY's CAGR in **the recent 17y bull**, which is a US-equity-dominance bet. Strategies that work post-2024 may differ.
- Honest expectation: this hunt may **not** find a winner in 6-12 iters. The bar is high, and 43 prior iters of long_term_portfolio couldn't produce it (different mission, but architectural lessons apply).
