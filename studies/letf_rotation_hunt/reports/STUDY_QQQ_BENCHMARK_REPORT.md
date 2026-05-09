# LETF Rotation Hunt — QQQ/NDX Benchmark Supplement

**Status:** Supplemental benchmark-sensitivity report generated 2026-05-09.
**Benchmark:** `QQQSIM` as long-history QQQ/NDX 1x buy-and-hold proxy.
**Universe:** original top-20 strategies ranked by lh_56y Sharpe, plus QQQ/NDX benchmark. No QQQ-specific re-optimization.

> This report answers the Reddit criticism: if QLD is the risk-on asset, QQQ/NDX is the stricter direct benchmark. The methodology intentionally changes only the benchmark to avoid new selection bias [advances_fin_ml, p.31-34; p.208-211].

---

## 1. TL;DR

- Operative winner `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` remains above QQQ/NDX on full-history terminal wealth: **224.31x QQQ**.
- Full-history pct time above QQQ: **100.0%**; minimum relative equity after warmup: **1.78x**.
- Composite rolling robustness vs QQQ rank: **#1 of 21**.
- Rolling-window average end-ratio win rate vs QQQ: **95.8%**; average pct days above QQQ: **90.0%**.
- The benchmark change is much stricter than SPY: short 3y/5y windows contain more relative underperformance during NDX bull recoveries, while 10y+ windows are the key durability check.

---

## 2. Visuals

![Top-N relative to QQQ](qqq_benchmark_plots/top21_relative_to_qqq.png)

![Pct above QQQ](qqq_benchmark_plots/rolling_pct_above_qqq.png)

![Robustness ranking vs QQQ](qqq_benchmark_plots/robustness_ranking_vs_qqq.png)

---

## 3. Full-History Metrics vs QQQ/NDX

Ranked by terminal `strategy_eq / QQQ_eq` on the common lh_56y window.

| Rank | Config | Sortino | Sharpe | CAGR | MDD | pct above QQQ | min rel | end ratio vs QQQ |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `tqqq_voteK2_off_zroz` | 0.777 | 0.814 | 31.9% | -74.0% | 100.0% | 1.62 | 288.19x |
| 2 | `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | 0.887 | 0.919 | 31.1% | -64.5% | 100.0% | 1.78 | 224.31x |
| 3 | `qld_vote_k2_off_zroz` | 0.819 | 0.853 | 27.9% | -74.9% | 100.0% | 1.58 | 84.04x |
| 4 | `qld_voteK2_off_zroz_alt` | 0.819 | 0.853 | 27.9% | -74.9% | 100.0% | 1.58 | 84.04x |
| 5 | `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | 0.819 | 0.853 | 27.9% | -74.9% | 100.0% | 1.58 | 84.04x |
| 6 | `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | 0.811 | 0.847 | 27.7% | -74.9% | 100.0% | 1.58 | 78.69x |
| 7 | `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | 0.802 | 0.836 | 27.2% | -62.2% | 100.0% | 1.54 | 65.83x |
| 8 | `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | 0.810 | 0.843 | 27.0% | -74.9% | 100.0% | 1.58 | 63.51x |
| 9 | `qld_ema150_off_zroz` | 0.755 | 0.787 | 24.4% | -58.0% | 100.0% | 1.57 | 27.68x |
| 10 | `qld_voteK2_off_edv` | 0.751 | 0.794 | 23.9% | -73.9% | 100.0% | 1.16 | 22.83x |
| 11 | `qld_voteK2_off_tlt` | 0.751 | 0.794 | 23.9% | -73.9% | 100.0% | 1.16 | 22.83x |
| 12 | `qld_voteK2_off_ief` | 0.737 | 0.781 | 22.9% | -72.3% | 100.0% | 1.07 | 16.87x |
| 13 | `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | 0.804 | 0.819 | 22.5% | -53.5% | 100.0% | 1.49 | 14.55x |
| 14 | `xs_ewmac_top2_zroz_spysma200` | 0.763 | 0.791 | 22.0% | -55.7% | 100.0% | 1.31 | 12.36x |
| 15 | `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | 0.776 | 0.798 | 21.7% | -53.1% | 100.0% | 1.49 | 11.12x |
| 16 | `qld_vote_k3_off_zroz` | 0.776 | 0.798 | 21.7% | -53.1% | 100.0% | 1.49 | 11.12x |
| 17 | `xs_clenow_top3_zroz_spysma200` | 0.800 | 0.823 | 20.9% | -54.5% | 100.0% | 1.10 | 8.67x |
| 18 | `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | 0.752 | 0.776 | 20.9% | -56.4% | 100.0% | 1.62 | 8.62x |
| 19 | `erc_multi4_sigma030` | 0.770 | 0.800 | 20.6% | -48.6% | 89.4% | 0.48 | 7.73x |
| 20 | `erc_multi4_sigma025` | 0.768 | 0.796 | 20.1% | -47.6% | 91.3% | 0.45 | 6.71x |
| 21 | `QQQ/NDX 1x b&h` | 0.630 | 0.658 | 14.6% | -83.0% | 0.0% | 1.00 | 1.00x |

---

## 4. Rolling End-Ratio Win Rate vs QQQ

Cell = fraction of rolling windows where terminal strategy equity beats terminal QQQ equity.

| Config | 3y | 5y | 10y | 15y | 20y |
|---|---:|---:|---:|---:|---:|
| `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | 88.1% | 91.0% | 100.0% | 100.0% | 100.0% |
| `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | 84.1% | 90.1% | 100.0% | 100.0% | 100.0% |
| `qld_voteK2_off_zroz_alt` | 82.1% | 91.3% | 100.0% | 100.0% | 100.0% |
| `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | 82.1% | 91.3% | 100.0% | 100.0% | 100.0% |
| `qld_vote_k2_off_zroz` | 82.1% | 91.3% | 100.0% | 100.0% | 100.0% |
| `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | 76.7% | 84.2% | 100.0% | 100.0% | 100.0% |
| `qld_voteK2_off_tlt` | 82.3% | 89.6% | 98.3% | 100.0% | 100.0% |
| `qld_voteK2_off_edv` | 82.3% | 89.6% | 98.3% | 100.0% | 100.0% |
| `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | 74.5% | 82.7% | 99.7% | 100.0% | 100.0% |
| `xs_clenow_top3_zroz_spysma200` | 54.4% | 61.2% | 74.9% | 94.7% | 100.0% |
| `xs_ewmac_top2_zroz_spysma200` | 62.0% | 70.4% | 85.7% | 97.7% | 100.0% |
| `qld_voteK2_off_ief` | 81.7% | 91.5% | 98.1% | 100.0% | 100.0% |
| `tqqq_voteK2_off_zroz` | 73.4% | 78.3% | 100.0% | 100.0% | 100.0% |
| `erc_multi4_sigma030` | 50.1% | 57.0% | 79.9% | 97.0% | 100.0% |
| `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | 56.6% | 66.9% | 78.8% | 81.2% | 81.1% |
| `erc_multi4_sigma025` | 49.2% | 55.1% | 79.3% | 94.7% | 100.0% |
| `qld_ema150_off_zroz` | 65.8% | 66.9% | 78.0% | 85.1% | 95.1% |
| `qld_vote_k3_off_zroz` | 61.7% | 64.5% | 77.4% | 90.1% | 84.8% |
| `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | 61.7% | 64.5% | 77.4% | 90.1% | 84.8% |
| `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | 54.1% | 51.1% | 75.8% | 81.2% | 76.1% |
| `QQQ/NDX 1x b&h` | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 5. Rolling Pct Time Above QQQ

Cell = mean fraction of days inside each rolling window where strategy equity is above QQQ equity, after warmup.

| Config | 3y | 5y | 10y | 15y | 20y |
|---|---:|---:|---:|---:|---:|
| `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | 76.7% | 83.3% | 95.6% | 96.8% | 97.7% |
| `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | 74.2% | 81.1% | 93.7% | 95.4% | 96.1% |
| `qld_voteK2_off_zroz_alt` | 74.9% | 81.2% | 93.1% | 94.8% | 95.5% |
| `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | 74.9% | 81.2% | 93.1% | 94.8% | 95.5% |
| `qld_vote_k2_off_zroz` | 74.9% | 81.2% | 93.1% | 94.8% | 95.5% |
| `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | 71.3% | 76.5% | 89.9% | 92.5% | 93.5% |
| `qld_voteK2_off_tlt` | 71.6% | 78.1% | 89.3% | 91.4% | 92.5% |
| `qld_voteK2_off_edv` | 71.6% | 78.1% | 89.3% | 91.4% | 92.5% |
| `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | 68.0% | 73.7% | 88.6% | 91.6% | 92.5% |
| `xs_clenow_top3_zroz_spysma200` | 51.5% | 54.9% | 67.2% | 82.2% | 85.9% |
| `xs_ewmac_top2_zroz_spysma200` | 57.5% | 62.6% | 75.0% | 86.8% | 88.8% |
| `qld_voteK2_off_ief` | 71.4% | 77.2% | 87.6% | 90.1% | 91.4% |
| `tqqq_voteK2_off_zroz` | 66.9% | 71.9% | 85.1% | 88.8% | 90.3% |
| `erc_multi4_sigma030` | 49.0% | 51.4% | 59.9% | 67.8% | 73.0% |
| `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | 54.5% | 59.9% | 74.8% | 86.6% | 90.6% |
| `erc_multi4_sigma025` | 47.8% | 50.2% | 58.4% | 66.7% | 72.5% |
| `qld_ema150_off_zroz` | 62.5% | 64.6% | 69.2% | 71.1% | 81.9% |
| `qld_vote_k3_off_zroz` | 56.5% | 59.3% | 71.1% | 81.0% | 83.1% |
| `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | 56.5% | 59.3% | 71.1% | 81.0% | 83.1% |
| `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | 53.0% | 53.4% | 65.6% | 78.9% | 80.7% |
| `QQQ/NDX 1x b&h` | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

---

## 6. Worst Relative Windows — `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`

| Start | End | Window | end ratio vs QQQ | pct above QQQ | min rel | Sharpe | Sortino | CAGR |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2018-02-28 | 2023-02-28 | 5y | 0.648x | 34.6% | 0.606x | 0.274 | 0.250 | 3.3% |
| 2017-10-31 | 2022-10-31 | 5y | 0.697x | 73.1% | 0.656x | 0.336 | 0.305 | 5.7% |
| 2008-12-31 | 2011-12-30 | 3y | 0.704x | 0.0% | 0.476x | 0.455 | 0.427 | 10.6% |
| 2018-01-31 | 2023-01-31 | 5y | 0.706x | 27.5% | 0.593x | 0.317 | 0.290 | 4.9% |
| 2017-11-30 | 2022-11-30 | 5y | 0.714x | 67.1% | 0.645x | 0.368 | 0.335 | 6.9% |
| 2020-02-28 | 2023-02-28 | 3y | 0.715x | 67.5% | 0.669x | 0.235 | 0.221 | 1.3% |
| 2019-10-31 | 2022-10-31 | 3y | 0.730x | 83.5% | 0.687x | 0.243 | 0.221 | 1.6% |
| 2005-05-31 | 2008-05-30 | 3y | 0.733x | 41.1% | 0.707x | 0.124 | 0.114 | -0.9% |
| 2002-09-30 | 2005-09-30 | 3y | 0.741x | 0.0% | 0.596x | 0.518 | 0.495 | 12.6% |
| 2020-01-31 | 2023-01-31 | 3y | 0.742x | 53.3% | 0.623x | 0.220 | 0.204 | 0.6% |
| 2019-12-31 | 2022-12-30 | 3y | 0.750x | 62.4% | 0.639x | 0.171 | 0.157 | -1.4% |
| 2019-11-29 | 2022-11-29 | 3y | 0.764x | 73.6% | 0.662x | 0.256 | 0.235 | 2.1% |

---

## 7. Top-N Input Strategies

| Rank | Config | Tier | Original lh_56y Sharpe | Score | Label | Source iter |
|---:|---|---|---:|---:|---|---|
| 1 | `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz` | T3d | 0.919 | 76 | STRONG | `022-2026-05-06-T3d-extended-grid` |
| 2 | `qld_vote_k2_off_zroz` | T3d | 0.853 | 78 | STRONG | `014-2026-05-06-T3d-vote-of-k` |
| 3 | `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz` | T3d | 0.853 | 82 | STRONG | `022-2026-05-06-T3d-extended-grid` |
| 4 | `qld_voteK2_off_zroz_alt` | T3d | 0.853 | 82 | STRONG | `023-2026-05-06-T3d-multi-asset-grid` |
| 5 | `qld_voteK2_sma200_50_vol42_40_ar30_off_zroz` | T3d | 0.846 | 82 | STRONG | `022-2026-05-06-T3d-extended-grid` |
| 6 | `qld_voteK2_sma200_50_vol21_30_ar30_off_zroz` | T3d | 0.843 | 79 | STRONG | `022-2026-05-06-T3d-extended-grid` |
| 7 | `qld_voteK2_sma200_50_vol21_40_ar60_off_zroz` | T3d | 0.836 | 76 | STRONG | `022-2026-05-06-T3d-extended-grid` |
| 8 | `xs_clenow_top3_zroz_spysma200` | T4b | 0.823 | 72 | PROMISING | `017-2026-05-06-T4b-clenow-top3` |
| 9 | `qld_voteK3_sma200_50_vol21_40_ar60_off_zroz` | T3d | 0.818 | 74 | PROMISING | `022-2026-05-06-T3d-extended-grid` |
| 10 | `tqqq_voteK2_off_zroz` | T3d | 0.814 | 76 | STRONG | `023-2026-05-06-T3d-multi-asset-grid` |
| 11 | `erc_multi4_sigma030` | T5d | 0.799 | 72 | PROMISING | `025-2026-05-08-T5d-hrp-erc` |
| 12 | `qld_vote_k3_off_zroz` | T3d | 0.798 | 70 | PROMISING | `014-2026-05-06-T3d-vote-of-k` |
| 13 | `qld_voteK3_sma200_50_vol21_40_ar30_off_zroz` | T3d | 0.798 | 74 | PROMISING | `022-2026-05-06-T3d-extended-grid` |
| 14 | `erc_multi4_sigma025` | T5d | 0.796 | 68 | PROMISING | `025-2026-05-08-T5d-hrp-erc` |
| 15 | `qld_voteK2_off_edv` | T3d | 0.794 | 82 | STRONG | `023-2026-05-06-T3d-multi-asset-grid` |
| 16 | `qld_voteK2_off_tlt` | T3d | 0.794 | 82 | STRONG | `023-2026-05-06-T3d-multi-asset-grid` |
| 17 | `xs_ewmac_top2_zroz_spysma200` | T4c | 0.791 | 72 | PROMISING | `018-2026-05-06-T4c-ewmac-top2` |
| 18 | `qld_ema150_off_zroz` | T1d | 0.787 | 64 | PROMISING | `004-2026-05-06-T1d-full-grid` |
| 19 | `qld_voteK2_off_ief` | T3d | 0.781 | 76 | STRONG | `023-2026-05-06-T3d-multi-asset-grid` |
| 20 | `qld_voteK3_ema200_50_vol21_40_ar30_off_zroz` | T3d | 0.776 | 61 | PROMISING | `022-2026-05-06-T3d-extended-grid` |

---

## 8. Methodology Notes

- Benchmark is `QQQSIM`; `NDXSIM` is not available in the local testfolio cache, so QQQSIM is used as the long-history NDX/QQQ proxy.
- Strategy universe is unchanged from the original top-N robustness setup; this avoids benchmark-specific data snooping [advances_fin_ml, p.208-211].
- Rolling windows use 3y/5y/10y/15y/20y horizons with month-end starts and the same warmup convention as the SPY robustness report.
- Relative metrics rebase both strategy and QQQ to 1.0 at each common-window start date.
- This is a supplemental benchmark-sensitivity report, not a new deployment authorization. Mandate §1 remains unchanged.

