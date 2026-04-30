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

> **Note (2026-04-29 refactor)**: bars above are the original 3-dataset values. The hunt actually runs on 2 datasets (`lh_56y + spy_real`) since `f414873`. Effective bars used by `scoring.py`: **CAGR ≥ 11.21%** and **MDD ≤ 55.17%**.

---

## Net-of-tax (Lei 14.754/2023) — pre/post tax reporting

Added 2026-04-30 (this session). Each iter now reports **two** scores:

- **Gross score** (the canonical hunt scoring; gates evaluate the strategy's intrinsic alpha)
- **Net score** (post-DARF, deploy-readiness; same rubric using `net_cagr / net_mdd / net_sharpe` from `tax_layer.py`)

Tax model — Lei 14.754/2023 vigente jan/2024 (alíquota 15% flat anual, perdas compensam, carry-forward indefinido). Implementation: `studies/_shared/tax_engine.py:AnnualDarfEngine` wrapped by `studies/spy_beater_hunt/tax_layer.py`.

**Classification per spec.type**:

| spec type | classification | drag observed | rationale |
|---|---|---:|---|
| `static` | buy_hold (defer DARF to terminal liquidation) | 0.59 – 0.74 pp | máximo tax-deferral compounding |
| `lrs` | annual_realize (year-end DARF) | 1.63 – 2.35 pp | regime flips realizam P&L; aggregado anual |
| `vol_target` | annual_realize | ~1.7 pp | rebalance contínuo aggregado anual |
| `blend(non-static)` | annual_realize | herda do constituinte | conservative |

The **gross-vs-net spread** is structurally about **1.5 pp** wider for swing strategies than for buy-hold. This re-shuffles the gross ranking: buy-hold strategies move UP in the net ranking; LRS/vol_target/blend move DOWN.

**Caveat — FX**: `tax_layer.py` assumes flat PTAX (no BRL/USD variation in tributable income). Lei 14.754 includes FX in rendimentos; for long-term holds the FX is approximately symmetric, but for short windows or post-major-FX-moves, the modeled drag may understate by ~0.3-0.7 pp.

---

## Final ranking — gross vs net (iters 001-018, after 2026-04-30 backfill)

Sorted by net_score desc; column "shift" = (gross_rank − net_rank). Positive shift = strategy moved UP after tax accounting (typically buy-hold); negative = moved DOWN (typically LRS/blend with high turnover).

| rank | iter | strategy | gross_score | net_score | gross_tier | net_tier | shift |
|---:|---:|---|---:|---:|---|---|---:|
| 1 | 018 | h1_meta_50a2_50g2ief (blend) | 70 | 64 | PROMISING | PROMISING | — |
| 2 | 009 | b2_hfea_kmlm20 (HFEA static) | 63 | 62 | PROMISING | PROMISING | +6 |
| 3 | 007 | a7_tqqq_split_kmlm40_tlt10 (LRS) | 67 | 61 | PROMISING | PROMISING | -1 |
| 4 | 008 | b1_balanced_5050 (HFEA static) | 63 | 61 | PROMISING | PROMISING | +5 |
| 5 | 006 | a6_tqqq_split_kmlm30_tlt10 (LRS) | 67 | 60 | PROMISING | PROMISING | -2 |
| 6 | 004 | a4_lrs_split_kmlm30 (LRS) | 66 | 60 | PROMISING | PROMISING | -2 |
| 7 | 015 | f1_aw_stack_15x (F1 levered AW) | 61 | 60 | PROMISING | PROMISING | +4 |
| 8 | 014 | e1_tqqq_split_kmlm30_tlt10_tsmom | 65 | 59 | PROMISING | MARGINAL | -3 |
| 9 | 003 | a3_lrs_split_kmlm20 | 64 | 59 | PROMISING | MARGINAL | -3 |
| 10 | 017 | g2_f1_letf_2x_sma200_ief | 64 | 58 | PROMISING | MARGINAL | -3 |
| 11 | 005 | a5_lrs_split_kmlm30_tlt10 | 63 | 58 | PROMISING | MARGINAL | -1 |
| 12 | 016 | g1_f1_stack_sma200_ief | 61 | 57 | PROMISING | MARGINAL | — |
| 13 | 010 | c1_vt20_sso (vol_target) | 60 | 57 | PROMISING | MARGINAL | — |
| 14 | 001 | a1_lrs_split (Gayed LRS UPRO) | 60 | 55 | PROMISING | MARGINAL | — |
| 15 | 013 | d1_qqq_6m_tsmom | 59 | 54 | MARGINAL | MARGINAL | — |
| 16 | 002 | a2_sma200_th2_3xupro | 57 | 52 | MARGINAL | MARGINAL | — |
| 17 | 012 | d2_ntsx_avuv | 52 | 50 | MARGINAL | MARGINAL | — |

**Headline shifts under net rubric**:

- **HFEA family (008/009)** rises from rank 9-10 → rank 2-4. HFEA's combination of high gross CAGR (≥18%) + buy-hold tax-efficiency = best-in-hunt **net-of-tax** competitor. MDD bar still fails (61-67%) so not a WINNER, but **score-relative** they win.
- **F1 stack (015)** rises from rank 11 → rank 7. The previously flagged "Sharpe-king" is now also tax-king among CAGR-bar passers.
- **TQQQ-track LRS (006/007)** stays in top 5 but loses absolute score (≥6pt drag).
- **Iter 018 H1 meta-ensemble** stays #1 by score but its 2.07pp drag means net_score 64 is below the closest gross winner-target (90).
- **No strategy reaches WINNER tier** under either rubric. Gates_bar fails for HFEA (high MDD); CAGR_bar by-margin under net for several LRS configs.

**Implication for deploy**: F1+SPLIT incumbent (Plano C 100%) remains unchanged. The hunt's `closest-to-winner` shifts from "iter 006/007 TQQQ-track LRS" (under gross rubric) to **"iter 009 HFEA+KMLM static"** (under net rubric, score 62 with 0.66pp drag) — but HFEA fails the MDD bar (61.5% vs 55.17%), so it's still not deployable.

The **buy-hold static** family is structurally tax-efficient. Future hunt iters should consider: (a) buy-hold portfolios with concentrated growth (closer to SPY CAGR without LRS gate cost); (b) NOT discount SBuy-hold candidates for being "boring" — they have a structural net-rubric advantage of ~1.5pp.
