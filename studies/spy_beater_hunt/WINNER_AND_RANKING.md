# Winner conditions + ranking tiers — spy_beater_hunt

> **Status (2026-04-30 closure)**: hunt fechado em 30 iters. Nenhum WINNER tier (≥90 + bars) emergiu. Para **deploy-readiness** ver `TOP_STRATEGIES.md` que substitui o critério "WINNER tier" por **gate-pass anti-overfit** (decisão usuário 2026-04-30: "se passaram nos gates, por mim tudo certo"). Esta página agora documenta o rubric ORIGINAL pelo qual as iters foram scoreadas e a ranking history pre/post tax — não é mais a referência canônica de deploy.

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

## Final ranking — gross vs net (iters 001-036 closure 2026-04-30)

Hunt fechou em **30 iters substantivas + 1 meta** (iter 011 IMPOSSIBILITY, sem backtest), totalizando **30 verdicts** com pre/post tax. Sorted by net_score desc.

> Para **deploy-readiness ranking** (com gate-audit por iter), ver `TOP_STRATEGIES.md`. Esta tabela é o ranking puro do score CAGR-anchored.

| rank | iter | strategy | gross | net | gross tier | net tier |
|---:|---:|---|---:|---:|---|---|
| 1 | **035** | h15 4-way GLD-mom off var (blend) | **74** | **68** | PROMISING | PROMISING |
| 2 | 034 | h14 4-way + GLD-mom (blend) | 73 | 67 | PROMISING | PROMISING |
| 3 | 036 | h16 4-way A2 off var (blend) | 73 | 67 | PROMISING | PROMISING |
| 4 | **026** | h6 4-way 30/25/25/20 (blend) ⭐ best PBO | 71 | **66** | PROMISING | PROMISING |
| 5 | 030 | h10 4-way TSMOM signal QQQ | 72 | 66 | PROMISING | PROMISING |
| 6 | 031-033 | h11/h12/h13 4-way GLD variations | 72 | 66 | PROMISING | PROMISING |
| 7 | 019 | h2 3-way 33/33/34 (blend) ⭐ simplest | 71 | 65 | PROMISING | PROMISING |
| 8 | 018 | h1 50/50 A2+G2 IEF (blend) | 70 | 64 | PROMISING | PROMISING |
| 9 | 021/025/027 | various 4-way blends | 70 | 64 | PROMISING | PROMISING |
| 10 | 028 | h8 25/50/25 with E1 gate sub | 69 | 64 | PROMISING | PROMISING |
| 11 | 029 | h9 4-way 12m TSMOM | 69 | 64 | PROMISING | PROMISING |
| 12 | 020 | h3 4-way + G1 IEF ⭐ best MDD | 67 | 62 | PROMISING | PROMISING |
| 13 | 009 | b2 hfea_kmlm20 (HFEA static buy-hold) | 63 | 62 | PROMISING | PROMISING |
| 14 | 007 | a7 tqqq+kmlm40+tlt10 (LRS) | 67 | 61 | PROMISING | PROMISING |
| 15 | 008 | b1 hfea 50/50 (HFEA static) | 63 | 61 | PROMISING | PROMISING |
| 16 | 006 | a6 tqqq+kmlm30+tlt10 (LRS) | 67 | 60 | PROMISING | PROMISING |
| 17 | 004 | a4 lrs+kmlm30 | 66 | 60 | PROMISING | PROMISING |
| 18 | 024 | g3 LRS-gated HFEA 40/40 | 66 | 60 | PROMISING | PROMISING |
| 19 | 015 | f1 stack (NTSX/GDE/TLT/KMLM) ⭐ simplest | 61 | 60 | PROMISING | PROMISING |
| 20 | 003/005/014/017 | LRS variants | 63-65 | 58-59 | PROMISING | MARGINAL |
| 21 | 010/016/022/023 | misc passers | 57-61 | 56-57 | various | MARGINAL |
| 22 | 001/002/012/013 | early iters | 52-60 | 50-55 | MARGINAL | MARGINAL |

**Closing observations**:

- **Top 12 todos PROMISING net (≥60)**, dominados por meta-ensemble blends. Teto empírico: gross 74 / net 68 (iter 035). Nenhum WINNER (≥90).
- **Buy-hold static climbs structurally** sob rubric net: HFEA family (008/009), F1 stack (015) sobem 4-6 ranks vs gross.
- **Meta-ensemble axis** (iters 018-036, 19 iters) é a única classe que quebra o teto histórico de 67 atingido por single-axis (iter 006 A2). Saturação confirmada em ~71-74 gross / 64-68 net via 13 iters consecutivas variando dimensões ortogonais.
- **PBO warning emerge** em iters 030-036 (PBO 0.5-0.9 grid-level) — cumulative_n_trials inflation. Iter 026 H6 mantém PBO 0.00 e é o **anchor honesto** para deploy.
- **Implicação para deploy**: F1+SPLIT (Plano C 100% incumbent) inalterado. Para reativar Plano B/D, ver `TOP_STRATEGIES.md` Tier A (iter 026 / 019 / 015 são as recomendações estratificadas por perfil de risco).
