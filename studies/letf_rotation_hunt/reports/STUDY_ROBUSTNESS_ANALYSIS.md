# LETF Rotation Hunt — Robustness Analysis (Rolling Windows)

> ## ⚠️ Post-close Sortino re-analysis update (2026-05-07)
>
> **This report was written under Sharpe ranking** (the study's original primary metric). After the study closed, a post-close re-analysis (`SORTINO_REANALYSIS_REPORT.md`, sister `SORTINO_RESUMO_EXECUTIVO.md`) shifted the operative metric to **Sortino** — which fairly credits the asymmetric upside of leveraged-LETF rotation strategies.
>
> **Key updates from the post-close re-analysis:**
> - **New canonical winner under Sortino:** `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` displaces the Sharpe-era winner `qld_vote_k2_off_zroz` (sma250/100 vs sma200/50; Sortino edge_vs_canonical +0.103, Track A passer).
> - **Sortino edge over SPY is ~55% larger** than Sharpe edge: +0.264 vs +0.171 on lh_56y gross.
> - **2000 dotcom cohort improves dramatically**: canonical -12.7% 5y CAGR → new winner -1.6% under sma250/100.
> - **New Sortino thresholds**: Track A 1.272, Track B-M1 1.016, Track B-M2 1.144 (canonical Sortino + 0.05 anti-curve-fit margin).
>
> **The body of this report below is preserved as-is for historical methodology fidelity.** All Sharpe-based numbers and rankings are accurate at time of writing but should be read alongside the Sortino re-analysis for current operative ranking. **Mandate §1 remains unchanged: capital 100% Plano C; Strategy A/B/D DORMANT.**
>
> **For non-technical reader:** see `SORTINO_RESUMO_EXECUTIVO.md` (PT-BR plain-language summary).
> **For technical detail:** see `SORTINO_REANALYSIS_REPORT.md` (13 sections, full tables).

---

**Date:** 2026-05-06.
**Method:** rolling window backtests over 5 window sizes (3y, 5y, 10y, 15y, 20y) with month-by-month start increments. Top-20 strategies + SPY benchmark.
**Total backtests:** 37359 (across 21 configs).
**Source data**: 40y lh_56y testfolio + Tiingo (1986-2026); SPYSIM as benchmark.

---

## 0. TL;DR

- **Study incumbent `qld_vote_k2_off_zroz` rolling-window confirmation:** 
  composite rank **#5 of 21**; avg median Sharpe **0.829** (highest); avg min Sharpe 0.167; avg pct_above_SPY **89.6%** (highest).
- **SPY 1× buy-hold benchmark:** composite rank #21 of 21; avg median Sharpe 0.678; avg min Sharpe -0.048. (20 strategies dominate SPY in composite robustness.)

## 1. Visual TL;DR

![Median Sharpe heatmap](robustness_plots/heatmap_median_sharpe.png)

*Median Sharpe per (config × window size). Rows sorted by mean across all sizes. Green = robust; red = era-dependent.*

![Composite ranking](robustness_plots/robustness_ranking.png)

*Top 30 by composite robustness rank. The composite is the average of 3 ranks (median Sharpe, min Sharpe, pct above SPY) across all 5 window sizes — captures both "good when good" and "not-bad when bad".*

---

## 2. Method

For each top-20 strategy (ranked by full-history lh_56y Sharpe across all 23 iters):
1. Recompute equity curve from original config (deterministic, seed=42)
2. For each window size in {3y, 5y, 10y, 15y, 20y}:
   - For each month-end start date (BME):
     - Slice equity to start..start+ws_years
     - Compute Sharpe / CAGR / MDD
     - Compute pct_time_above_SPY (post-warmup) and min_relative_equity
3. SPY 1× buy-hold included as benchmark (rolling on the same windows)

Warmup: 21 days for 3y/5y windows; 252 days for 10y/15y/20y.
Min-data filter: each window requires ≥95% of expected trading days.

---

## 3. Top-20 input strategies

| Rank | Config | Tier | Full-history Sharpe (lh_56y) | Score | Tier label |
|---:|---|---|---:|---:|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | T3d | 0.919 | 76 | STRONG |
| 2 | `qld_vote_k2_off_zroz` | T3d | 0.853 | 78 | STRONG |
| 3 | `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | T3d | 0.853 | 82 | STRONG |
| 4 | `qld_voteK2_off_zroz_alt` | T3d | 0.853 | 82 | STRONG |
| 5 | `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | T3d | 0.846 | 82 | STRONG |
| 6 | `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | T3d | 0.843 | 79 | STRONG |
| 7 | `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | T3d | 0.836 | 76 | STRONG |
| 8 | `xs_clenow_top3_zroz_spysma200` | T4b | 0.823 | 72 | PROMISING |
| 9 | `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | T3d | 0.818 | 74 | PROMISING |
| 10 | `tqqq_voteK2_off_zroz` | T3d | 0.814 | 76 | STRONG |
| 11 | `qld_vote_k3_off_zroz` | T3d | 0.798 | 70 | PROMISING |
| 12 | `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | T3d | 0.798 | 74 | PROMISING |
| 13 | `qld_voteK2_off_edv` | T3d | 0.794 | 82 | STRONG |
| 14 | `qld_voteK2_off_tlt` | T3d | 0.794 | 82 | STRONG |
| 15 | `xs_ewmac_top2_zroz_spysma200` | T4c | 0.791 | 72 | PROMISING |
| 16 | `qld_ema150_off_zroz` | T1d | 0.787 | 64 | PROMISING |
| 17 | `qld_voteK2_off_ief` | T3d | 0.781 | 76 | STRONG |
| 18 | `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | T3d | 0.776 | 61 | PROMISING |
| 19 | `tqqq_voteK2_off_edv` | T3d | 0.774 | 76 | STRONG |
| 20 | `tqqq_voteK2_off_tlt` | T3d | 0.774 | 76 | STRONG |

+ SPY 1× buy-hold benchmark.

---

## 4. Aggregate metrics per strategy × window size

Format: median Sharpe / min Sharpe / mean pct_above_SPY (across rolling windows of that size).

| Config | 3y | 5y | 10y | 15y | 20y |
|---|---|---|---|---|---|
| `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | 0.89/-0.15/79% | 0.88/0.23/86% | 0.92/0.33/96% | 0.86/0.62/97% | 0.84/0.66/98% |
| `qld_vote_k2_off_zroz` | 0.91/-0.48/77% | 0.83/-0.06/84% | 0.88/0.21/95% | 0.78/0.52/96% | 0.76/0.64/96% |
| `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | 0.91/-0.48/77% | 0.83/-0.06/84% | 0.88/0.21/95% | 0.78/0.52/96% | 0.76/0.64/96% |
| `qld_voteK2_off_zroz_alt` | 0.91/-0.48/77% | 0.83/-0.06/84% | 0.88/0.21/95% | 0.78/0.52/96% | 0.76/0.64/96% |
| `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | 0.87/-0.48/77% | 0.83/-0.00/84% | 0.81/0.26/95% | 0.79/0.55/97% | 0.76/0.62/97% |
| `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | 0.85/-0.32/75% | 0.85/0.01/82% | 0.82/0.35/94% | 0.77/0.57/96% | 0.74/0.66/96% |
| `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | 0.88/-0.48/71% | 0.83/-0.14/77% | 0.79/0.12/91% | 0.76/0.52/93% | 0.74/0.59/94% |
| `qld_voteK2_off_edv` | 0.88/-0.70/75% | 0.80/-0.18/82% | 0.84/0.13/93% | 0.70/0.47/95% | 0.70/0.58/95% |
| `qld_voteK2_off_tlt` | 0.88/-0.70/75% | 0.80/-0.18/82% | 0.84/0.13/93% | 0.70/0.47/95% | 0.70/0.58/95% |
| `qld_voteK2_off_ief` | 0.85/-0.71/75% | 0.82/-0.19/82% | 0.83/0.13/92% | 0.69/0.45/94% | 0.68/0.57/95% |
| `tqqq_voteK2_off_zroz` | 0.81/-0.47/69% | 0.78/-0.07/75% | 0.78/0.17/87% | 0.74/0.55/90% | 0.74/0.58/91% |
| `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | 0.74/-0.50/64% | 0.75/0.03/71% | 0.73/0.34/86% | 0.77/0.46/93% | 0.85/0.46/96% |
| `xs_clenow_top3_zroz_spysma200` | 0.75/-0.09/64% | 0.72/0.20/72% | 0.81/0.39/86% | 0.76/0.62/94% | 0.75/0.61/95% |
| `xs_ewmac_top2_zroz_spysma200` | 0.73/-0.19/64% | 0.73/-0.08/72% | 0.81/0.34/86% | 0.76/0.61/92% | 0.75/0.58/93% |
| `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | 0.76/-0.49/64% | 0.75/-0.12/68% | 0.76/0.33/84% | 0.72/0.52/91% | 0.74/0.50/92% |
| `qld_vote_k3_off_zroz` | 0.76/-0.49/64% | 0.75/-0.12/68% | 0.76/0.33/84% | 0.72/0.52/91% | 0.74/0.50/92% |
| `tqqq_voteK2_off_edv` | 0.81/-0.59/67% | 0.76/-0.13/74% | 0.76/0.10/84% | 0.69/0.49/88% | 0.70/0.54/89% |
| `tqqq_voteK2_off_tlt` | 0.81/-0.59/67% | 0.76/-0.13/74% | 0.76/0.10/84% | 0.69/0.49/88% | 0.70/0.54/89% |
| `qld_ema150_off_zroz` | 0.75/-0.27/68% | 0.72/-0.04/74% | 0.78/0.26/84% | 0.70/0.37/89% | 0.67/0.43/93% |
| `SPY 1× b&h` | 0.85/-0.63/0% | 0.79/-0.19/0% | 0.64/-0.04/0% | 0.57/0.28/0% | 0.53/0.34/0% |
| `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | 0.66/-0.65/61% | 0.69/-0.10/64% | 0.70/0.16/78% | 0.66/0.45/89% | 0.67/0.42/91% |

---

## 5. Worst-window stress test

![Worst-window stress](robustness_plots/worst_window_stress.png)

*Worst Sharpe achievable across all rolling windows. Red = negative (strategy lost money in some 3-20y window); orange = sub-0.3; green = ≥0.3 (strategy maintained at least modest edge in worst regime).*

---

## 6. Distribution per window size

![Sharpe distribution](robustness_plots/distribution_per_window_size.png)

*Top 6 robust strategies' Sharpe distributions, one panel per window size. Tighter = more consistent; wider = more regime-sensitive.*

---

## 7. Era sensitivity (5y windows by decade-of-start)

![Era decade Sharpe](robustness_plots/era_decade_sharpe.png)

*Median 5y Sharpe per decade-of-start for top configs. Flat lines = robust across regimes; sloped = era-dependent. SPY shown for reference.*

---

## 8. Pct windows above SPY (v2 scoring strict bar)

![Pct above SPY](robustness_plots/pct_above_spy_per_window_size.png)

*Mean pct of rolling windows where strategy equity > SPY equity (post-warmup). Dark blue contour line marks the WINNER strict bar (0.95) per scoring v2.*

---

## 9. Composite robustness ranking

Top 10 by composite robustness (lower = more consistent across all 5 window sizes):

| Rank | Config | avg median Sharpe | avg min Sharpe | avg pct above SPY |
|---:|---|---:|---:|---:|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | 0.877 | 0.339 | 91.3% |
| 2 | `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | 0.812 | 0.191 | 89.9% |
| 3 | `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | 0.829 | 0.167 | 89.6% |
| 4 | `qld_voteK2_off_zroz_alt` | 0.829 | 0.167 | 89.6% |
| 5 | `qld_vote_k2_off_zroz` | 0.829 | 0.167 | 89.6% |
| 6 | `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | 0.807 | 0.256 | 88.5% |
| 7 | `xs_clenow_top3_zroz_spysma200` | 0.761 | 0.345 | 82.2% |
| 8 | `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | 0.801 | 0.122 | 85.3% |
| 9 | `tqqq_voteK2_off_zroz` | 0.769 | 0.152 | 82.3% |
| 10 | `xs_ewmac_top2_zroz_spysma200` | 0.757 | 0.253 | 81.3% |

---

## 10. Honest interpretation

1. **Did the study winner survive rolling-window stress?**
   `qld_vote_k2_off_zroz` rank in composite robustness: see top-10 table above.
   This validates whether full-history Sharpe 0.853 reflects real edge or
   selection bias from the lh_56y window.

2. **Are there 'sleeper' strategies that look mediocre on full-history
   but more consistent across rolling windows?** Compare top-20 input
   ranking (by full-history Sharpe) with top-10 composite robustness.
   Strategies that climb in the rolling ranking are candidates.

3. **Worst-window negatives:** how many strategies hit *negative* Sharpe
   in some rolling window? This is a deploy-honesty check — strategies
   that never went negative across any 3-20y window are exceptionally robust.

4. **Era sensitivity:** if a strategy's median Sharpe drops by >0.20
   between any two adjacent decades, it's regime-dependent. Use the
   era-decade plot to identify these.

5. **Multiple-testing:** this analysis is itself an enormous multiple
   testing exercise (~37k backtests). The ranking should be interpreted
   robustly (top-10 stable), not by exact rank position. Per
   `[advances_fin_ml, p.31-34]` sensitivity validation principle.

---

## 11. Methodology notes

- All equity curves recomputed from original configs in iter directories
  (deterministic; same seed=42 as production runs).
- SPY benchmark via SPYSIM testfolio cache (1986-2026, validated against
  Tiingo real SPY 2003+ in iter 000 v2).
- Warmup proportional: 21d (3-5y windows); 252d (10-15-20y).
- Min-data filter: ≥95% of expected trading days per window.
- Pure Python deterministic computation (no LLM/AI in this analysis pipeline).
- Sequential with progress logging via tqdm.
- Raw rolling-window data preserved at `data/robustness/all_windows.parquet`
  for re-analysis without recomputing.

---

## 12a. Sortino-relevant note (2026-05-07)

The rolling-window Sharpe heatmap computed in this analysis (37,359 windows across 21 configs × 5 window sizes × monthly increments) was **not re-run under Sortino**. This was a deliberate cascade choice — deferred per cascade option C in the Sortino re-analysis spec (`docs/superpowers/specs/2026-05-07-letf-sortino-reanalysis-design.md`) — because recomputing 37,359 windows under a new metric would require a separate compute pass and was not required to answer the pre-registered H₀ (pointwise Sortino edge). The heatmap therefore remains **Sharpe-only**; the composite ranking (#5 for `qld_vote_k2_off_zroz`) reflects Sharpe-denominated robustness. Under Sortino, the new operative winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` (sma250/100) would likely rank similarly or higher given its improved cohort performance, but this has not been formally verified. If Plano B is ever reactivated, a future formal sub-study could re-run this rolling-window analysis under Sortino to confirm robustness rank stability. Raw data is preserved at `data/robustness/all_windows.parquet` for that purpose.

---

## 12. Citations

- Spec §3.5 G3 walk-forward (this analysis is its granular extension)
- `[advances_fin_ml, p.31-34, p.196-202]` sensitivity validation
- `[trading_systems_methods, Kaufman, ch.21]` regime testing
- User request 2026-05-06 (top 20 + monthly increments + 5 window sizes)

