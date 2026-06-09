# Phase 5 - RSC + LRS/T3d Overlay Rebuilt-Sleeve Diagnostic

Status: research-only / diagnostic. This report does NOT authorize deployment, paper trading or a mandate change.

This phase answers whether the failed standalone LRS line deserves a smaller role as a satellite around the RSC-US `35/40/25` core. The RSC core is now rebuilt from `GDESIM`, `ZROZSIM`, and an `RSSTSIM` tracking proxy in `studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet`. The current `RSSTSIM` follows the user-provided Testfol.io payload: `SPYSIM + 70% DBMFSIM + 30% KMLMSIM - (CASHX + 200 bps/year)`, equivalent to `100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2` `[testing_tuning, p.327-335]`, `[risk_parity, p.80-81]`, `[systematic_trading, p.185-188]`.

Monthly fixed-weight rebalancing is used for both the RSC sleeve mix and the core/satellite allocation control, with turnover reported separately; it is not a deployable account-level tax simulation `[systematic_trading, p.185-188]`. Local LRS satellites are after-tax under the annual DARF model; the RSC core remains a gross/static portfolio diagnostic.

## Executive Conclusion

Rebuilt-sleeve overlays passing the strict RSC-improvement screen: **0/9**. Strict means higher CAGR than same-window RSC, no worse MDD, no worse Calmar, no worse time underwater and no worse max recovery time. No overlay cleared the strict screen. The highest-CAGR overlay overall is `rsc_70_t3d_k2_saved_30` with CAGR 14.24% but MDD -48.65%, so it is a growth-for-drawdown trade-off rather than a strict improvement. Baseline RSC in this diagnostic window is CAGR 12.40%, MDD -30.76%, Sharpe 0.838, Calmar 0.403.

Interpretation rule: strict rebuilt-sleeve passes are diagnostic leads only. They do not reverse the Phase 4 LRS gate failure and would need account-level tax/friction plus mandate gates with honest accumulated trial accounting before any promotion claim `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

## Source And Rules

| Item | Value |
|---|---|
| RSC core | `studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet` with weights `35% GDESIM / 40% RSSTSIM / 25% ZROZSIM` |
| RSSTSIM formula | `SPYSIM + 0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)`; local proxy for `CASHX?E=-2` financing. |
| Saved RSC audit | terminal ratio `0.792647`, CAGR diff `-1.000pp`, MDD diff `-0.820pp`, max relative deviation `22.668%` vs `studies/return_stacked_core/us_core/series/full_equity_curves.csv` column `B4-v2 35/40/25` |
| T3d-K2 source | `/var/www/victor/finances/letf-lab/studies/lrs/phases/phase_12_cross_study/results/equity_curves.csv` column `T3d-K2 (QLD/ZROZ)` if present |
| Local LRS satellites | Rebuilt from Phase 4 headline geometries in `lrs/` |
| Overlay weights | `90/10`, `80/20`, `70/30` RSC/satellite |
| Overlay rebalance | Monthly fixed-weight diagnostic |
| Strict screen | CAGR up; MDD, Calmar, underwater and recovery no worse than same-window RSC |
| Promotion status | None; diagnostic only, no gates, no mandate change |


## Series Sources

| Series | Source | Use | Note |
|---|---|---|---|
| RSC core | studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet | core baseline | Monthly `35/40/25` rebuild from `GDESIM/RSSTSIM/ZROZSIM` sleeve returns. |
| Saved RSC curve | studies/return_stacked_core/us_core/series/full_equity_curves.csv | audit only | Column `B4-v2 35/40/25` checks rebuilt core drift against the prior saved curve. |
| lrs_spy_headline | local_lrs_phase04_geometry | satellite | risk_on=100 SSO; risk_off=50 ZROZ / 25 GLD / 25 CASHX |
| lrs_qqq_headline | local_lrs_phase04_geometry | satellite | risk_on=25 QQQ / 75 QLD; risk_off=40 ZROZ / 40 GLD / 20 IEF |
| t3d_k2_saved | letf_lab_phase12_saved_equity | satellite | Saved Phase 12 equity curve; T3d-K2 not recomputed inside market-lab. |

## Plots

| Plot | File |
|---|---|
| Equity top overlays | [plots/phase05_equity_top_overlays.png](plots/phase05_equity_top_overlays.png) |
| Drawdowns top overlays | [plots/phase05_drawdowns_top_overlays.png](plots/phase05_drawdowns_top_overlays.png) |
| Relative wealth vs RSC | [plots/phase05_relative_vs_rsc.png](plots/phase05_relative_vs_rsc.png) |
| Risk/return frontier | [plots/phase05_frontier.png](plots/phase05_frontier.png) |

## Overlay Ranking

| Candidate | Type | CAGR | MDD | Sharpe | Calmar | CAGR vs RSC | MDD vs RSC | Terminal/RSC | Rel DD | Strict |
|---|---|---|---|---|---|---|---|---|---|---|
| rsc_70_t3d_k2_saved_30 | overlay | 14.24% | -48.65% | 0.783 | 0.293 | +1.84pp | -17.89pp | 1.53x | -39.00% | no |
| rsc_80_t3d_k2_saved_20 | overlay | 13.73% | -41.39% | 0.822 | 0.332 | +1.33pp | -10.63pp | 1.36x | -27.33% | no |
| rsc_70_lrs_qqq_headline_30 | overlay | 13.25% | -28.14% | 0.826 | 0.471 | +0.85pp | +2.62pp | 1.22x | -25.45% | no |
| rsc_90_t3d_k2_saved_10 | overlay | 13.12% | -33.47% | 0.844 | 0.392 | +0.72pp | -2.70pp | 1.18x | -14.32% | no |
| rsc_80_lrs_qqq_headline_20 | overlay | 13.01% | -27.70% | 0.847 | 0.470 | +0.61pp | +3.06pp | 1.15x | -17.50% | no |
| rsc_90_lrs_qqq_headline_10 | overlay | 12.73% | -28.32% | 0.852 | 0.450 | +0.33pp | +2.44pp | 1.08x | -9.02% | no |
| rsc_70_lrs_spy_headline_30 | overlay | 12.69% | -26.68% | 0.837 | 0.476 | +0.29pp | +4.08pp | 1.07x | -15.50% | no |
| rsc_80_lrs_spy_headline_20 | overlay | 12.63% | -25.18% | 0.851 | 0.502 | +0.23pp | +5.58pp | 1.06x | -10.49% | no |
| rsc_90_lrs_spy_headline_10 | overlay | 12.53% | -27.12% | 0.852 | 0.462 | +0.13pp | +3.64pp | 1.03x | -5.32% | no |

## Underwater And Relative Pain

| Candidate | UW days | Max recovery | RSC max recovery | Days below RSC | Longest below RSC | Max deficit | Est turnover/y |
|---|---|---|---|---|---|---|---|
| rsc_70_t3d_k2_saved_30 | 90.38% | 1186 | 679 | 51.48% | 3389 | -32.28% | 2.14 |
| rsc_80_t3d_k2_saved_20 | 90.10% | 950 | 679 | 51.03% | 3349 | -21.97% | 1.44 |
| rsc_70_lrs_qqq_headline_30 | 90.38% | 684 | 679 | 60.41% | 1806 | -20.52% | 1.02 |
| rsc_90_t3d_k2_saved_10 | 90.16% | 913 | 679 | 50.52% | 3328 | -11.15% | 0.73 |
| rsc_80_lrs_qqq_headline_20 | 90.19% | 681 | 679 | 58.64% | 1245 | -13.75% | 0.69 |
| rsc_90_lrs_qqq_headline_10 | 90.34% | 680 | 679 | 57.38% | 1240 | -6.89% | 0.35 |
| rsc_70_lrs_spy_headline_30 | 89.87% | 799 | 679 | 60.26% | 1094 | -13.91% | 1.78 |
| rsc_80_lrs_spy_headline_20 | 89.89% | 797 | 679 | 57.62% | 1094 | -9.29% | 1.19 |
| rsc_90_lrs_spy_headline_10 | 90.16% | 793 | 679 | 54.71% | 1083 | -4.65% | 0.60 |

## References And Standalone Satellites

| Candidate | Type | CAGR | MDD | Sharpe | Calmar | CAGR vs RSC | MDD vs RSC | Terminal/RSC | Rel DD | Strict |
|---|---|---|---|---|---|---|---|---|---|---|
| t3d_k2_saved | satellite_reference | 14.65% | -84.04% | 0.546 | 0.174 | +2.26pp | -53.28pp | 1.69x | -87.05% | no |
| lrs_qqq_headline | satellite_reference | 13.64% | -42.56% | 0.593 | 0.320 | +1.24pp | -11.80pp | 1.33x | -66.72% | no |
| rsc_core | core | 12.40% | -30.76% | 0.838 | 0.403 | +0.00pp | +0.00pp | 1.00x | 0.00% | no |
| lrs_spy_headline | satellite_reference | 12.09% | -39.28% | 0.598 | 0.308 | -0.31pp | -8.52pp | 0.93x | -48.16% | no |

## Phase Verdict

| Question | Verdict |
|---|---|
| Did any rebuilt-sleeve overlay strictly improve RSC? | No (0/9). |
| Did this reconstruct RSC sleeves? | Yes, inside repo provenance: `GDESIM/RSSTSIM/ZROZSIM` monthly `35/40/25`. `RSSTSIM` is a documented RSST tracking proxy, not a live ETF backfill. |
| Did this run mandate gates? | No. This is a small diagnostic overlay screen only. |
| Is anything deployment-ready? | No. No deploy, no paper-trade label, no mandate change. |

Next engineering step, if further precision is desired: add account-level tax/friction handling and then run the mandate validation gates with honest accumulated trial accounting.
