# SPY/SSO/UPRO Replacement - Practical Taxed Selection

Status: research-only practical rerun. Daily rebalance/update is excluded as non-operational. This report does not authorize deployment, paper trading or mandate changes.

Method references: SMA risk-on/off follows the leverage-for-the-long-run premise for levered equity with trend/risk-off filters `[leverage_for_the_long_run, p.13]`; cadence and tax sensitivity are implementation robustness checks `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. Tax model uses the repository `AnnualDarfEngine`: annual settlement on realized net gains, indefinite loss carry-forward, and final liquidation for comparable after-tax terminal wealth (Lei 14.754/2023).

## Executive Conclusion

Daily execution materially overstated practicality, so it was removed. Under monthly/quarterly active updates and monthly/quarterly/annual static rebalancing, the best active risk-on/off row is `SMA300 L2.75 off 60 ZROZ / 40 GLD monthly` with after-tax CAGR 16.76%, MDD -73.74%, terminal 23.75x vs after-tax SPY, min relative equity after 10y 1.28x, and 10y+ hit 92.0%. The best static row is `static L3.00 E60% GLD annual` with after-tax CAGR 13.11%, MDD -70.80%, terminal 3.75x vs after-tax SPY, min relative equity after 10y 0.68x, and 10y+ hit 53.1%.

Practical conclusion: active monthly/quarterly risk-on/off is the only branch that currently produces benchmark-relative equity dominance after tax. Static target-leverage portfolios improve long-run terminal wealth but do not maintain relative equity dominance through adverse regimes.

## Source Data And Tax Model

| Item | Value |
|---|---|
| Testfol.io cache | `data/testfolio/cache/history.parquet` |
| Daily common window | `1968-04-02` to `2026-05-21` |
| Cadence event counts | monthly `698`, quarterly `233`, annual `59` |
| Active cadences | `monthly`, `quarterly` only |
| Static cadences | `monthly`, `quarterly`, `annual` only |
| Tax model | `AnnualDarfEngine`, 15% annual DARF on realized net gains, loss carry-forward, final liquidation |
| SPY benchmark tax paid / initial | 5979.5% |
| Active candidates | `280`; practical passes `3` |
| Static candidates | `567`; practical passes `0` |

Practical pass means after-tax terminal wealth beats after-tax SPY, after-tax relative equity stays above SPY after the first 10 years, and minimum 10y+ rolling hit rate is at least 90%. MDD is diagnostic, not a gate.

## Best Active Risk-On/Off

Analysis: Active candidates only update monthly or quarterly. They may hold levered equity or a risk-off basket for weeks/months, not days.

Conclusion: The active branch has after-tax dominance candidates.

| Family | Name | Cadence | L | Tax CAGR | Spread | Tax MDD | MDD vs SPY | Tax Terminal/SPY | Min Rel 10y+ | 10y+ Hit | Tax Paid | Turnover/Yr | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| active risk on off | SMA300 L2.75 off 60 ZROZ / 40 GLD monthly | monthly | 2.75 | 16.76% | +6.20pp | -73.74% | -18.60pp | 23.75x | 1.28x | 92.0% | 134694.3% | 0.93 | yes |
| active risk on off | SMA300 L2.50 off 60 ZROZ / 40 GLD monthly | monthly | 2.50 | 16.48% | +5.92pp | -68.84% | -13.70pp | 20.69x | 1.32x | 92.2% | 116666.9% | 0.95 | yes |
| active risk on off | SMA300 L2.50 off 50 ZROZ / 25 GLD / 25 CASH monthly | monthly | 2.50 | 16.06% | +5.50pp | -68.84% | -13.70pp | 16.75x | 1.30x | 90.5% | 94457.4% | 0.95 | yes |
| active risk on off | SMA250 L3.00 off ZROZ monthly | monthly | 3.00 | 17.82% | +7.26pp | -78.50% | -23.36pp | 40.11x | 0.52x | 93.2% | 218628.9% | 1.12 | no |
| active risk on off | SMA250 L2.75 off ZROZ monthly | monthly | 2.75 | 17.58% | +7.02pp | -73.74% | -18.60pp | 35.74x | 0.54x | 95.7% | 193986.2% | 1.16 | no |
| active risk on off | SMA250 L3.00 off 60 ZROZ / 40 GLD monthly | monthly | 3.00 | 17.24% | +6.68pp | -78.50% | -23.36pp | 30.09x | 0.81x | 86.6% | 163852.0% | 1.16 | no |
| active risk on off | SMA250 L2.75 off 60 ZROZ / 40 GLD monthly | monthly | 2.75 | 17.01% | +6.45pp | -73.74% | -18.60pp | 26.96x | 0.85x | 89.8% | 146188.2% | 1.21 | no |
| active risk on off | SMA300 L3.00 off ZROZ monthly | monthly | 3.00 | 17.11% | +6.55pp | -78.50% | -23.36pp | 28.29x | 0.76x | 89.0% | 160266.2% | 0.84 | no |
| active risk on off | SMA300 L3.00 off 60 ZROZ / 40 GLD monthly | monthly | 3.00 | 16.90% | +6.34pp | -78.50% | -23.36pp | 25.43x | 1.23x | 88.3% | 144806.0% | 0.89 | no |
| active risk on off | SMA250 L2.50 off ZROZ monthly | monthly | 2.50 | 17.23% | +6.67pp | -68.84% | -13.70pp | 29.99x | 0.57x | 96.3% | 162081.9% | 1.18 | no |
| active risk on off | SMA300 L2.75 off ZROZ monthly | monthly | 2.75 | 16.97% | +6.41pp | -73.74% | -18.60pp | 26.33x | 0.79x | 88.8% | 148561.9% | 0.89 | no |
| active risk on off | SMA250 L3.00 off 50 ZROZ / 50 GLD monthly | monthly | 3.00 | 17.00% | +6.44pp | -78.50% | -23.36pp | 26.82x | 0.81x | 82.6% | 146027.6% | 1.17 | no |
| active risk on off | SMA300 L3.00 off 50 ZROZ / 50 GLD monthly | monthly | 3.00 | 16.77% | +6.21pp | -78.50% | -23.36pp | 23.91x | 1.37x | 83.9% | 136241.2% | 0.89 | no |
| active risk on off | SMA250 L2.75 off 50 ZROZ / 50 GLD monthly | monthly | 2.75 | 16.78% | +6.22pp | -73.74% | -18.60pp | 24.04x | 0.94x | 85.1% | 130327.6% | 1.21 | no |
| active risk on off | SMA250 L3.00 off 50 ZROZ / 25 GLD / 25 CASH monthly | monthly | 3.00 | 16.86% | +6.30pp | -78.50% | -23.36pp | 24.95x | 0.81x | 84.7% | 135871.7% | 1.16 | no |
| active risk on off | SMA300 L2.75 off 50 ZROZ / 50 GLD monthly | monthly | 2.75 | 16.64% | +6.08pp | -73.74% | -18.60pp | 22.34x | 1.42x | 87.6% | 126708.4% | 0.94 | no |
| active risk on off | SMA250 L2.50 off 60 ZROZ / 40 GLD monthly | monthly | 2.50 | 16.66% | +6.10pp | -68.84% | -13.70pp | 22.63x | 0.89x | 91.2% | 122176.6% | 1.22 | no |
| active risk on off | SMA250 L3.00 off 40 ZROZ / 40 GLD / 20 IEF monthly | monthly | 3.00 | 16.85% | +6.29pp | -78.50% | -23.36pp | 24.89x | 0.77x | 81.4% | 135479.0% | 1.16 | no |
| active risk on off | SMA250 L2.75 off 50 ZROZ / 25 GLD / 25 CASH monthly | monthly | 2.75 | 16.64% | +6.08pp | -73.74% | -18.60pp | 22.34x | 0.87x | 88.8% | 121091.1% | 1.21 | no |
| active risk on off | SMA300 L2.50 off ZROZ monthly | monthly | 2.50 | 16.69% | +6.13pp | -68.84% | -13.70pp | 22.92x | 0.81x | 87.8% | 128725.1% | 0.91 | no |
| active risk on off | SMA250 L2.75 off 40 ZROZ / 40 GLD / 20 IEF monthly | monthly | 2.75 | 16.63% | +6.07pp | -73.74% | -18.60pp | 22.30x | 0.91x | 84.0% | 120862.0% | 1.21 | no |
| active risk on off | SMA300 L3.00 off 40 ZROZ / 40 GLD / 20 IEF monthly | monthly | 3.00 | 16.56% | +6.00pp | -78.50% | -23.36pp | 21.54x | 1.27x | 82.6% | 122811.1% | 0.89 | no |
| active risk on off | SMA300 L3.00 off 50 ZROZ / 25 GLD / 25 CASH monthly | monthly | 3.00 | 16.47% | +5.91pp | -78.50% | -23.36pp | 20.58x | 1.21x | 85.7% | 117285.3% | 0.89 | no |
| active risk on off | SMA250 L2.50 off 50 ZROZ / 50 GLD monthly | monthly | 2.50 | 16.43% | +5.87pp | -68.84% | -13.70pp | 20.19x | 0.99x | 87.7% | 108981.3% | 1.22 | no |
| active risk on off | SMA300 L2.75 off 40 ZROZ / 40 GLD / 20 IEF monthly | monthly | 2.75 | 16.43% | +5.87pp | -73.74% | -18.60pp | 20.13x | 1.40x | 86.3% | 114179.7% | 0.93 | no |

## Best Static Buy-And-Hold/Rebalanced

Analysis: Static candidates maintain target proportions using only monthly/quarterly/annual rebalancing; no signal switching is used.

Conclusion: Static target-leverage portfolios do not maintain after-tax relative equity dominance, even when terminal wealth improves.

| Family | Name | Cadence | L | Tax CAGR | Spread | Tax MDD | MDD vs SPY | Tax Terminal/SPY | Min Rel 10y+ | 10y+ Hit | Tax Paid | Turnover/Yr | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| static buy hold rebalanced | static L3.00 E60% GLD annual | annual | 3.00 | 13.11% | +2.55pp | -70.80% | -15.66pp | 3.75x | 0.68x | 53.1% | 21645.3% | 0.10 | no |
| static buy hold rebalanced | static L2.75 E60% GLD annual | annual | 2.75 | 12.97% | +2.41pp | -66.84% | -11.70pp | 3.49x | 0.74x | 54.7% | 20168.8% | 0.10 | no |
| static buy hold rebalanced | static L2.50 E60% GLD annual | annual | 2.50 | 12.77% | +2.21pp | -63.40% | -8.26pp | 3.16x | 0.80x | 53.2% | 18258.7% | 0.09 | no |
| static buy hold rebalanced | static L2.75 E60% 50 ZROZ / 50 GLD annual | annual | 2.75 | 12.88% | +2.32pp | -63.97% | -8.82pp | 3.33x | 0.56x | 71.2% | 19030.0% | 0.10 | no |
| static buy hold rebalanced | static L2.50 E60% 50 ZROZ / 50 GLD annual | annual | 2.50 | 12.71% | +2.15pp | -59.36% | -4.22pp | 3.07x | 0.62x | 73.9% | 17505.4% | 0.09 | no |
| static buy hold rebalanced | static L2.50 E70% GLD annual | annual | 2.50 | 12.80% | +2.24pp | -72.12% | -16.98pp | 3.21x | 0.72x | 55.0% | 18602.9% | 0.08 | no |
| static buy hold rebalanced | static L2.25 E70% GLD annual | annual | 2.25 | 12.62% | +2.06pp | -68.44% | -13.30pp | 2.92x | 0.80x | 55.3% | 16973.9% | 0.07 | no |
| static buy hold rebalanced | static L3.00 E60% 50 ZROZ / 50 GLD annual | annual | 3.00 | 12.99% | +2.43pp | -68.17% | -13.02pp | 3.53x | 0.50x | 68.0% | 20115.2% | 0.10 | no |
| static buy hold rebalanced | static L2.25 E60% 50 ZROZ / 50 GLD annual | annual | 2.25 | 12.49% | +1.93pp | -54.87% | +0.27pp | 2.74x | 0.68x | 76.2% | 15645.5% | 0.09 | no |
| static buy hold rebalanced | static L2.25 E60% GLD annual | annual | 2.25 | 12.52% | +1.96pp | -59.84% | -4.70pp | 2.77x | 0.84x | 52.8% | 16048.6% | 0.08 | no |
| static buy hold rebalanced | static L2.75 E70% GLD annual | annual | 2.75 | 12.90% | +2.34pp | -76.79% | -21.65pp | 3.37x | 0.61x | 53.9% | 19519.8% | 0.09 | no |
| static buy hold rebalanced | static L2.00 E70% GLD annual | annual | 2.00 | 12.36% | +1.80pp | -64.48% | -9.34pp | 2.55x | 0.87x | 55.3% | 14855.3% | 0.07 | no |
| static buy hold rebalanced | static L2.00 E60% 50 ZROZ / 50 GLD annual | annual | 2.00 | 12.22% | +1.66pp | -50.47% | +4.67pp | 2.37x | 0.74x | 77.5% | 13564.3% | 0.08 | no |
| static buy hold rebalanced | static L2.75 E60% 60 ZROZ / 40 GLD annual | annual | 2.75 | 12.77% | +2.21pp | -63.41% | -8.27pp | 3.16x | 0.48x | 72.6% | 17978.9% | 0.10 | no |
| static buy hold rebalanced | static L2.50 E60% 60 ZROZ / 40 GLD annual | annual | 2.50 | 12.62% | +2.06pp | -58.90% | -3.76pp | 2.91x | 0.53x | 75.0% | 16598.5% | 0.09 | no |
| static buy hold rebalanced | static L2.25 E70% 50 ZROZ / 50 GLD annual | annual | 2.25 | 12.56% | +2.00pp | -64.67% | -9.53pp | 2.83x | 0.59x | 71.6% | 16299.1% | 0.07 | no |
| static buy hold rebalanced | static L3.00 E60% 60 ZROZ / 40 GLD annual | annual | 3.00 | 12.87% | +2.31pp | -67.66% | -12.52pp | 3.33x | 0.42x | 69.7% | 18925.3% | 0.10 | no |
| static buy hold rebalanced | static L2.50 E70% 50 ZROZ / 50 GLD annual | annual | 2.50 | 12.71% | +2.15pp | -68.54% | -13.40pp | 3.06x | 0.52x | 69.1% | 17600.7% | 0.08 | no |
| static buy hold rebalanced | static L2.00 E70% 50 ZROZ / 50 GLD annual | annual | 2.00 | 12.33% | +1.77pp | -60.51% | -5.37pp | 2.51x | 0.66x | 75.7% | 14467.9% | 0.07 | no |
| static buy hold rebalanced | static L2.25 E60% 60 ZROZ / 40 GLD annual | annual | 2.25 | 12.40% | +1.84pp | -54.53% | +0.61pp | 2.61x | 0.58x | 77.1% | 14890.9% | 0.08 | no |
| static buy hold rebalanced | static L2.75 E60% 40 ZROZ / 40 GLD / 20 IEF annual | annual | 2.75 | 12.59% | +2.03pp | -64.14% | -9.00pp | 2.88x | 0.55x | 69.3% | 16419.1% | 0.10 | no |
| static buy hold rebalanced | static L3.00 E70% GLD annual | annual | 3.00 | 12.91% | +2.35pp | -81.40% | -26.26pp | 3.40x | 0.49x | 52.1% | 19708.7% | 0.09 | no |
| static buy hold rebalanced | static L2.50 E60% 40 ZROZ / 40 GLD / 20 IEF annual | annual | 2.50 | 12.43% | +1.87pp | -59.54% | -4.40pp | 2.65x | 0.61x | 71.9% | 15093.3% | 0.09 | no |
| static buy hold rebalanced | static L3.00 E60% 40 ZROZ / 40 GLD / 20 IEF annual | annual | 3.00 | 12.70% | +2.14pp | -68.33% | -13.19pp | 3.05x | 0.50x | 65.9% | 17368.1% | 0.10 | no |
| static buy hold rebalanced | static L2.75 E60% 50 ZROZ / 50 GLD quarterly | quarterly | 2.75 | 12.62% | +2.06pp | -71.38% | -16.24pp | 2.92x | 0.49x | 71.4% | 16382.1% | 0.19 | no |

## Phase Verdict

| Question | Verdict |
|---|---|
| Is daily rebalance/update allowed? | No. It is excluded as non-operational. |
| Is 15% annual Brazilian tax modeled? | Yes, via `AnnualDarfEngine` on realized annual net gains plus final liquidation. |
| Best active strategy after tax | `SMA300 L2.75 off 60 ZROZ / 40 GLD monthly`. |
| Best static strategy after tax | `static L3.00 E60% GLD annual`. |
| Does active pass practical after-tax dominance? | Yes. |
| Does static pass practical after-tax dominance? | No. |
| Is either branch deploy-ready? | No. This is selection only; validation/stress remains required. |

Recommended next step: validate only the selected active and static winners with start-date stress, cost sensitivity, subperiod/regime tables, and an explicit tax-event audit.
