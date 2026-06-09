# LRS Top-20 By CAGR

Status: research-only diagnostic. This ranking deliberately ignores drawdown filters so the user can inspect the highest-return rows before choosing any follow-up. It is **not** a validation result, winner label, paper-trade label or mandate change `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`.

Source rows scanned: `4183` from `lrs/results/*.csv`. Ranking metric: CAGR descending, with no MDD/Calmar/underwater gate. `after_tax` rows use `taxed_cagr`; Phase 5 rows use the phase's reported `cagr`.

## Top 20

| Rank | Candidate | Phase | CAGR | MDD | Sharpe | Calmar | Terminal | Basis | Years |
|---|---|---|---|---|---|---|---|---|---|
| 1 | QQQ / L3.00 / off ZROZ / RV63 <= 40% / lag 5 | phase02_target_leverage_vol | 25.84% | -71.05% | 0.707 | 0.364 | 10727.48x | after_tax | 40.4 |
| 2 | QQQ / L3.00 / off ZROZ / RV63 <= 40% / lag 1 | phase02_target_leverage_vol | 25.48% | -66.12% | 0.697 | 0.385 | 9550.69x | after_tax | 40.4 |
| 3 | QQQ / L3.00 / off ZROZ / RV63 <= 40% / lag 0 | phase02_target_leverage_vol | 25.48% | -68.12% | 0.696 | 0.374 | 9532.36x | after_tax | 40.4 |
| 4 | QQQ / L2.75 / off ZROZ / RV63 <= 40% / lag 5 | phase02_target_leverage_vol | 25.08% | -69.28% | 0.709 | 0.362 | 8396.40x | after_tax | 40.4 |
| 5 | QQQ / L3.00 / off ZROZ / RV21 <= 30% / lag 0 | phase02_target_leverage_vol | 24.94% | -65.74% | 0.699 | 0.379 | 8030.06x | after_tax | 40.4 |
| 6 | QQQ / L3.00 / off ZROZ / RV63 <= 40% / lag 4 | phase02_target_leverage_vol | 24.92% | -71.55% | 0.691 | 0.348 | 7960.23x | after_tax | 40.4 |
| 7 | QQQ / L3.00 / off ZROZ / RV63 <= 40% / lag 3 | phase02_target_leverage_vol | 24.85% | -67.58% | 0.689 | 0.368 | 7788.65x | after_tax | 40.4 |
| 8 | QQQ / L2.75 / off ZROZ / RV63 <= 40% / lag 1 | phase02_target_leverage_vol | 24.82% | -64.61% | 0.699 | 0.384 | 7722.84x | after_tax | 40.4 |
| 9 | QQQ / L3.00 / off ZROZ / RV63 <= 40% / lag 2 | phase02_target_leverage_vol | 24.82% | -65.89% | 0.688 | 0.377 | 7713.13x | after_tax | 40.4 |
| 10 | QQQ / L2.75 / off ZROZ / RV63 <= 40% / lag 0 | phase02_target_leverage_vol | 24.79% | -66.49% | 0.698 | 0.373 | 7647.63x | after_tax | 40.4 |
| 11 | QQQ / L3.00 / off 50 ZROZ / 50 GLD / RV63 <= 40% / lag 5 | phase02_target_leverage_vol | 24.58% | -64.34% | 0.691 | 0.382 | 7137.18x | after_tax | 40.4 |
| 12 | QQQ / L3.00 / off 50 ZROZ / 50 GLD / RV63 <= 40% / lag 1 | phase02_target_leverage_vol | 24.49% | -64.40% | 0.686 | 0.380 | 6935.40x | after_tax | 40.4 |
| 13 | QQQ / L3.00 / off ZROZ / RV21 <= 40% / lag 0 | phase02_target_leverage_vol | 24.47% | -69.35% | 0.680 | 0.353 | 6892.35x | after_tax | 40.4 |
| 14 | QQQ / L3.00 / off 50 ZROZ / 50 GLD / RV63 <= 40% / lag 0 | phase02_target_leverage_vol | 24.46% | -63.86% | 0.685 | 0.383 | 6857.10x | after_tax | 40.4 |
| 15 | QQQ_3x / 100 TQQQ / off ZROZ / lag 0 | phase01_risk_off | 24.45% | -88.31% | 0.672 | 0.277 | 6844.72x | after_tax | 40.4 |
| 16 | QQQ / L3.00 / off ZROZ / none / lag 0 | phase02_target_leverage_vol | 24.45% | -88.31% | 0.672 | 0.277 | 6844.72x | after_tax | 40.4 |
| 17 | QQQ / L3.00 / off 50 ZROZ / 25 GLD / 25 CASH / RV63 <= 40% / lag 5 | phase02_target_leverage_vol | 24.38% | -62.84% | 0.689 | 0.388 | 6690.95x | after_tax | 40.4 |
| 18 | QQQ / L3.00 / off 40 ZROZ / 40 GLD / 20 IEF / RV63 <= 40% / lag 5 | phase02_target_leverage_vol | 24.37% | -63.87% | 0.689 | 0.382 | 6662.19x | after_tax | 40.4 |
| 19 | QQQ / L2.75 / off ZROZ / RV63 <= 40% / lag 4 | phase02_target_leverage_vol | 24.28% | -69.66% | 0.694 | 0.348 | 6467.52x | after_tax | 40.4 |
| 20 | QQQ / L3.00 / off 50 ZROZ / 25 GLD / 25 CASH / RV63 <= 40% / lag 0 | phase02_target_leverage_vol | 24.26% | -63.42% | 0.683 | 0.383 | 6441.29x | after_tax | 40.4 |


## Reading

The table is intentionally return-first. Large MDD rows are not excluded; they are shown so the trade-off is explicit. Any selected follow-up still needs a fresh pre-registration, account-level frictions/tax where applicable, and the mandate gates before any promotion claim `[advances_fin_ml, p.273-275]`.
