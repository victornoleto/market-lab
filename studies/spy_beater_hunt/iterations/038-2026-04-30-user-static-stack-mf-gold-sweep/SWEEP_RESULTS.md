# spy_beater_hunt iter 038 — Sweep results (full table)

**Sweep**: 14 configs static buy-hold, capital-efficient stacking + MF + gold + duration variations. Datasets: lh_56y (1986+, ~40y) + spy_real (2003+, ~22.7y). Tax model: Lei 14.754/2023 (DARF 15% anual, buy-hold defer-to-terminal).

---

## Full results — per-dataset GROSS metrics

| config | lh_56y Sharpe | lh_56y CAGR | lh_56y MDD | spy_real Sharpe | spy_real CAGR | spy_real MDD |
|---|---:|---:|---:|---:|---:|---:|
| T1_gold_heavy | 1.045 | 16.54% | 33.42% | 1.023 | 16.40% | 33.42% |
| B2_tmf10_balanced | 1.024 | 16.20% | 34.68% | 1.013 | 16.16% | 34.44% |
| B1_user_baseline_25tmf | 1.050 | 16.61% | 36.73% | 0.978 | 15.42% | 36.73% |
| B5_no_duration | 0.917 | 15.43% | 41.45% | 0.933 | 16.30% | 41.45% |
| T2_equity_heavy | 1.045 | 16.07% | 31.17% | 1.014 | 15.52% | 31.17% |
| T3_rssb_global | 1.012 | 16.11% | 38.81% | 0.938 | 15.18% | 38.81% |
| M4_rsst_kmlm_blend | 1.045 | 15.14% | 34.61% | 0.956 | 13.96% | 34.61% |
| B4_zroz_instead_of_tmf | 1.027 | 14.62% | 28.38% | 1.024 | 14.22% | 27.66% |
| B3_tlt_instead_of_tmf | 1.033 | 13.67% | 29.41% | 1.023 | 13.64% | 29.31% |
| M1_kmlm_no_rsst | 1.021 | 13.63% | 32.96% | 0.912 | 12.45% | 32.96% |
| M2_dbmf_no_rsst | 0.907 | 12.34% | 34.43% | 0.928 | 12.76% | 34.43% |
| M3_kmlm_dbmf_blend | 0.897 | 12.09% | 33.63% | 0.925 | 12.62% | 33.63% |
| L1_cegb_proxy | 1.025 | 11.57% | 25.83% | 1.034 | 11.88% | 25.83% |
| L2_bogleheads_67ntsx | 1.015 | 11.58% | 24.87% | 0.985 | 10.95% | 24.87% |

## Full results — per-dataset NET metrics (post-Lei 14.754/2023)

| config | lh_56y Sharpe | lh_56y CAGR | lh_56y MDD | spy_real Sharpe | spy_real CAGR | spy_real MDD |
|---|---:|---:|---:|---:|---:|---:|
| T1_gold_heavy | 1.011 | 16.04% | 33.42% | 0.969 | 15.60% | 33.42% |
| B2_tmf10_balanced | 0.989 | 15.71% | 34.68% | 0.959 | 15.36% | 34.44% |
| B1_user_baseline_25tmf | 1.015 | 16.12% | 36.73% | 0.924 | 14.63% | 36.73% |
| B5_no_duration | 0.887 | 14.95% | 41.45% | 0.886 | 15.50% | 41.45% |
| T2_equity_heavy | 1.009 | 15.58% | 31.17% | 0.957 | 14.73% | 31.17% |
| T3_rssb_global | 0.978 | 15.62% | 38.81% | 0.887 | 14.39% | 38.81% |
| M4_rsst_kmlm_blend | 1.006 | 14.66% | 34.61% | 0.898 | 13.19% | 34.61% |
| B4_zroz_instead_of_tmf | 0.987 | 14.14% | 28.38% | 0.959 | 13.45% | 27.66% |
| B3_tlt_instead_of_tmf | 0.989 | 13.19% | 29.41% | 0.956 | 12.88% | 29.31% |
| M1_kmlm_no_rsst | 0.978 | 13.16% | 32.96% | 0.851 | 11.71% | 32.96% |
| M2_dbmf_no_rsst | 0.852 | 11.68% | 34.43% | 0.867 | 12.01% | 34.43% |
| M3_kmlm_dbmf_blend | 0.842 | 11.44% | 33.63% | 0.864 | 11.87% | 33.63% |
| L1_cegb_proxy | 0.972 | 11.11% | 25.83% | 0.954 | 11.15% | 25.83% |
| L2_bogleheads_67ntsx | 0.962 | 11.11% | 24.87% | 0.906 | 10.24% | 24.87% |

## Means across datasets — GROSS

| config | mean Sharpe | mean CAGR | mean MDD |
|---|---:|---:|---:|
| T1_gold_heavy | 1.034 | 16.47% | 33.42% |
| B2_tmf10_balanced | 1.019 | 16.18% | 34.56% |
| B1_user_baseline_25tmf | 1.014 | 16.02% | 36.73% |
| B5_no_duration | 0.925 | 15.87% | 41.45% |
| T2_equity_heavy | 1.029 | 15.80% | 31.17% |
| T3_rssb_global | 0.975 | 15.64% | 38.81% |
| M4_rsst_kmlm_blend | 1.001 | 14.55% | 34.61% |
| B4_zroz_instead_of_tmf | 1.025 | 14.42% | 28.02% |
| B3_tlt_instead_of_tmf | 1.028 | 13.66% | 29.36% |
| M1_kmlm_no_rsst | 0.966 | 13.04% | 32.96% |
| M2_dbmf_no_rsst | 0.917 | 12.55% | 34.43% |
| M3_kmlm_dbmf_blend | 0.911 | 12.35% | 33.63% |
| L1_cegb_proxy | 1.029 | 11.73% | 25.83% |
| L2_bogleheads_67ntsx | 1.000 | 11.27% | 24.87% |

## Means across datasets — NET (sorted by NET CAGR desc)

| config | mean Sharpe | mean CAGR | mean MDD | $100k → 30y |
|---|---:|---:|---:|---:|
| T1_gold_heavy | 0.990 | 15.82% | 33.42% | $8,195,894 |
| B2_tmf10_balanced | 0.974 | 15.54% | 34.56% | $7,610,472 |
| B1_user_baseline_25tmf | 0.970 | 15.37% | 36.73% | $7,298,701 |
| B5_no_duration | 0.886 | 15.22% | 41.45% | $7,014,300 |
| T2_equity_heavy | 0.983 | 15.16% | 31.17% | $6,896,575 |
| T3_rssb_global | 0.932 | 15.00% | 38.81% | $6,628,730 |
| M4_rsst_kmlm_blend | 0.952 | 13.92% | 34.61% | $4,991,303 |
| B4_zroz_instead_of_tmf | 0.973 | 13.79% | 28.02% | $4,825,308 |
| B3_tlt_instead_of_tmf | 0.973 | 13.04% | 29.36% | $3,948,739 |
| M1_kmlm_no_rsst | 0.914 | 12.43% | 32.96% | $3,362,371 |
| M2_dbmf_no_rsst | 0.860 | 11.84% | 34.43% | $2,872,567 |
| M3_kmlm_dbmf_blend | 0.853 | 11.65% | 33.63% | $2,729,029 |
| L1_cegb_proxy | 0.963 | 11.13% | 25.83% | $2,370,541 |
| L2_bogleheads_67ntsx | 0.934 | 10.68% | 24.87% | $2,097,195 |

## Per-config specs

| config | spec |
|---|---|
| T1_gold_heavy | NTSXSIM=20.0%, GDESIM=35.0%, RSSTSIM=25.0%, TMFSIM=20.0% |
| B2_tmf10_balanced | NTSXSIM=30.0%, GDESIM=30.0%, RSSTSIM=30.0%, TMFSIM=10.0% |
| B1_user_baseline_25tmf | NTSXSIM=25.0%, GDESIM=25.0%, RSSTSIM=25.0%, TMFSIM=25.0% |
| B5_no_duration | NTSXSIM=35.0%, GDESIM=35.0%, RSSTSIM=30.0% |
| T2_equity_heavy | NTSXSIM=35.0%, GDESIM=25.0%, RSSTSIM=25.0%, TMFSIM=15.0% |
| T3_rssb_global | RSSBSIM=25.0%, GDESIM=25.0%, RSSTSIM=25.0%, TMFSIM=25.0% |
| M4_rsst_kmlm_blend | NTSXSIM=25.0%, GDESIM=25.0%, RSSTSIM=12.5%, KMLMSIM=12.5%, TMFSIM=25.0% |
| B4_zroz_instead_of_tmf | NTSXSIM=25.0%, GDESIM=25.0%, RSSTSIM=25.0%, ZROZSIM=25.0% |
| B3_tlt_instead_of_tmf | NTSXSIM=25.0%, GDESIM=25.0%, RSSTSIM=25.0%, TLTSIM=25.0% |
| M1_kmlm_no_rsst | NTSXSIM=25.0%, GDESIM=25.0%, KMLMSIM=25.0%, TMFSIM=25.0% |
| M2_dbmf_no_rsst | NTSXSIM=25.0%, GDESIM=25.0%, DBMFSIM=25.0%, TMFSIM=25.0% |
| M3_kmlm_dbmf_blend | NTSXSIM=25.0%, GDESIM=25.0%, KMLMSIM=12.5%, DBMFSIM=12.5%, TMFSIM=25.0% |
| L1_cegb_proxy | NTSXSIM=40.0%, GDESIM=25.0%, KMLMSIM=17.5%, TLTSIM=17.5% |
| L2_bogleheads_67ntsx | NTSXSIM=67.0%, GLDSIM=11.0%, KMLMSIM=11.0%, ZROZSIM=11.0% |

## Pareto frontier (CAGR vs MDD, NET-of-tax)

Strategies that maximize CAGR for any given MDD (non-dominated points):

| rank | config | NET CAGR | NET MDD | NET Sharpe |
|---|---|---:|---:|---:|
| 1 | L2_bogleheads_67ntsx | 10.68% | 24.87% | 0.934 |
| 2 | L1_cegb_proxy | 11.13% | 25.83% | 0.963 |
| 3 | B4_zroz_instead_of_tmf | 13.79% | 28.02% | 0.973 |
| 4 | T2_equity_heavy | 15.16% | 31.17% | 0.983 |
| 5 | T1_gold_heavy | 15.82% | 33.42% | 0.990 |

## SPY benchmark reference

| metric | lh_56y | spy_real | mean |
|---|---:|---:|---:|
| CAGR  | 11.47% | 10.95% | 11.21% |
| MDD   | 55.14% | 55.20% | 55.17% |
| Sharpe| 0.680  | 0.652  | 0.666  |

All 14 configs **beat SPY in CAGR + MDD** (bars 1+2 PASS).

## Plots

- [equity overlay lh_56y](plot_overlay_lh_56y.png)
- [equity overlay spy_real](plot_overlay_spy_real.png)
- [rolling lh_56y](plot_rolling_lh_56y.png)
- [rolling spy_real](plot_rolling_spy_real.png)
- [CAGR×MDD scatter (Pareto visualization)](plot_cagr_mdd_scatter.png)
- [gate heatmap](plot_gate_heatmap.png)
