# SPY/SSO/UPRO Replacement - Equity Dominance Report

Status: research-only objective pivot. This report does not authorize deployment, paper trading or mandate changes.

Method references: this phase ranks benchmark-relative equity curves and rolling-window dominance rather than max-drawdown gates; rolling diagnostics remain robustness checks `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. The explicit target-leverage ladder follows the LETF leverage premise `[leverage_for_the_long_run, p.13]`.

## Executive Conclusion

The equity-dominance objective changes the picture materially. The top ranked row is `SMA200 L3.00 off 60 ZROZ / 40 GLD daily`: CAGR 19.38%, MDD -63.28%, terminal wealth 73.13x vs SPY, minimum relative equity after 10y 1.31x, and 10y+ rolling hit 95.1%. Drawdown is reported as diagnostic only. `173` candidates met the dominance pass definition.

Practical conclusion: using target leverage directly is the right abstraction. Static and tactical candidates are now judged by whether their portfolio equity stays ahead of SPY equity, especially after a long warmup, while absolute MDD is no longer a hard blocker.

## Source Data And Objective

| Item | Value |
|---|---|
| Testfol.io cache | `data/testfolio/cache/history.parquet` |
| Daily common window | `1968-04-02` to `2026-05-21` |
| SPY baseline | CAGR 10.87%, MDD -55.14%, Sharpe 0.690 |
| Target leverage ladder | `1.00x, 1.25x, 1.50x, 1.75x, 2.00x, 2.25x, 2.50x, 2.75x, 3.00x` |
| Static candidates | `1,107` |
| Tactical candidates | `800` |
| Dominance pass rows | `173` |
| Strict full-period dominance rows | `0` |

Dominance pass means terminal wealth beats SPY, minimum 10y+ rolling hit rate is at least 90%, and relative equity stays at or above SPY after the first 10 years. Full-period MDD can be worse than SPY.

## Top Equity-Dominance Candidates

Analysis: This is the primary ranking. It rewards benchmark-relative equity dominance and allows higher absolute drawdown if the relative equity curve remains ahead.

Conclusion: At least one candidate maintains benchmark-relative dominance after the warmup; inspect relative drawdown before treating it as practical.

| Family | Name | L | CAGR | Spread | MDD | MDD vs SPY | Terminal/SPY | Min Rel 10y+ | Above 10y+ | 10y+ Hit | Rel DD | Sustained Above | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tactical sma target leverage | SMA200 L3.00 off 60 ZROZ / 40 GLD daily | 3.00 | 19.38% | +8.51pp | -63.28% | -8.14pp | 73.13x | 1.31x | 100.0% | 95.1% | -62.19% | 1970-12-04 | yes |
| tactical sma target leverage | SMA200 L3.00 off 50 ZROZ / 50 GLD daily | 3.00 | 19.30% | +8.44pp | -63.74% | -8.59pp | 70.63x | 1.46x | 100.0% | 94.9% | -62.61% | 1970-12-03 | yes |
| tactical sma target leverage | SMA200 L3.00 off 40 ZROZ / 40 GLD / 20 IEF daily | 3.00 | 19.05% | +8.18pp | -63.97% | -8.83pp | 62.42x | 1.40x | 100.0% | 94.7% | -62.53% | 1970-12-02 | yes |
| tactical sma target leverage | SMA200 L2.75 off 60 ZROZ / 40 GLD daily | 2.75 | 18.98% | +8.11pp | -58.93% | -3.79pp | 60.20x | 1.36x | 100.0% | 96.2% | -58.15% | 1970-12-04 | yes |
| tactical sma target leverage | SMA200 L2.75 off 50 ZROZ / 50 GLD daily | 2.75 | 18.91% | +8.04pp | -58.61% | -3.47pp | 58.14x | 1.52x | 100.0% | 96.0% | -57.65% | 1970-12-02 | yes |
| tactical sma target leverage | SMA250 L3.00 off 60 ZROZ / 40 GLD daily | 3.00 | 18.84% | +7.97pp | -64.49% | -9.35pp | 56.31x | 1.22x | 100.0% | 96.3% | -67.10% | 1973-11-26 | yes |
| tactical sma target leverage | SMA300 L3.00 off 60 ZROZ / 40 GLD daily | 3.00 | 18.85% | +7.98pp | -78.25% | -23.11pp | 56.62x | 1.15x | 100.0% | 94.3% | -73.38% | 1973-11-19 | yes |
| tactical sma target leverage | SMA200 L3.00 off 50 ZROZ / 25 GLD / 25 CASH daily | 3.00 | 18.83% | +7.96pp | -65.02% | -9.88pp | 55.92x | 1.24x | 100.0% | 94.3% | -63.81% | 1970-12-01 | yes |
| tactical sma target leverage | SMA300 L3.00 off 60 ZROZ / 40 GLD monthly | 3.00 | 18.70% | +7.83pp | -78.50% | -23.36pp | 52.57x | 1.38x | 100.0% | 97.0% | -72.61% | 1971-12-01 | yes |
| tactical sma target leverage | SMA300 L2.75 off 60 ZROZ / 40 GLD daily | 2.75 | 18.66% | +7.79pp | -73.80% | -18.66pp | 51.50x | 1.21x | 100.0% | 98.2% | -67.27% | 1973-11-19 | yes |
| tactical sma target leverage | SMA200 L2.75 off 40 ZROZ / 40 GLD / 20 IEF daily | 2.75 | 18.65% | +7.78pp | -58.79% | -3.65pp | 51.38x | 1.45x | 100.0% | 95.9% | -57.77% | 1970-12-02 | yes |
| tactical sma target leverage | SMA250 L3.00 off 50 ZROZ / 50 GLD daily | 3.00 | 18.64% | +7.77pp | -64.12% | -8.98pp | 50.99x | 1.34x | 100.0% | 96.5% | -67.05% | 1973-11-26 | yes |
| tactical sma target leverage | SMA300 L2.75 off 60 ZROZ / 40 GLD monthly | 2.75 | 18.60% | +7.73pp | -74.15% | -19.00pp | 50.03x | 1.43x | 100.0% | 98.1% | -67.23% | 1971-12-01 | yes |
| tactical sma target leverage | SMA250 L2.75 off 50 ZROZ / 50 GLD monthly | 2.75 | 18.68% | +7.81pp | -74.15% | -19.00pp | 52.12x | 1.01x | 100.0% | 91.4% | -70.39% | 1974-02-04 | yes |
| tactical sma target leverage | SMA200 L2.50 off 60 ZROZ / 40 GLD daily | 2.50 | 18.48% | +7.61pp | -56.23% | -1.09pp | 47.21x | 1.41x | 100.0% | 97.0% | -53.82% | 1970-12-04 | yes |
| tactical sma target leverage | SMA250 L2.75 off 60 ZROZ / 40 GLD daily | 2.75 | 18.50% | +7.63pp | -60.75% | -5.61pp | 47.75x | 1.28x | 100.0% | 96.6% | -65.33% | 1973-11-26 | yes |
| tactical sma target leverage | SMA300 L3.00 off 50 ZROZ / 50 GLD daily | 3.00 | 18.63% | +7.76pp | -79.57% | -24.43pp | 50.70x | 1.24x | 100.0% | 90.1% | -75.04% | 1973-08-16 | yes |
| tactical sma target leverage | SMA300 L3.00 off 50 ZROZ / 50 GLD monthly | 3.00 | 18.56% | +7.69pp | -78.50% | -23.36pp | 49.03x | 1.55x | 100.0% | 93.3% | -73.54% | 1971-11-30 | yes |
| tactical sma target leverage | SMA300 L2.75 off 50 ZROZ / 50 GLD monthly | 2.75 | 18.46% | +7.59pp | -74.15% | -19.00pp | 46.66x | 1.60x | 100.0% | 96.9% | -67.60% | 1971-12-01 | yes |
| tactical sma target leverage | SMA250 L3.00 off 40 ZROZ / 40 GLD / 20 IEF daily | 3.00 | 18.43% | +7.56pp | -64.41% | -9.27pp | 46.12x | 1.30x | 100.0% | 96.5% | -66.80% | 1973-11-20 | yes |
| tactical sma target leverage | SMA200 L2.50 off 50 ZROZ / 50 GLD daily | 2.50 | 18.41% | +7.54pp | -54.50% | +0.64pp | 45.60x | 1.57x | 100.0% | 96.8% | -53.27% | 1970-12-02 | yes |
| tactical sma target leverage | SMA200 L2.75 off 50 ZROZ / 25 GLD / 25 CASH daily | 2.75 | 18.43% | +7.56pp | -59.99% | -4.85pp | 46.03x | 1.28x | 100.0% | 95.4% | -58.51% | 1970-11-30 | yes |
| tactical sma target leverage | SMA250 L2.75 off 40 ZROZ / 40 GLD / 20 IEF monthly | 2.75 | 18.52% | +7.65pp | -74.15% | -19.00pp | 48.23x | 1.02x | 100.0% | 90.9% | -70.31% | 1974-02-04 | yes |
| tactical sma target leverage | SMA250 L3.00 off 50 ZROZ / 25 GLD / 25 CASH daily | 3.00 | 18.39% | +7.52pp | -64.44% | -9.30pp | 45.25x | 1.17x | 100.0% | 95.9% | -66.76% | 1973-11-20 | yes |
| tactical sma target leverage | SMA300 L2.50 off 60 ZROZ / 40 GLD daily | 2.50 | 18.33% | +7.46pp | -69.21% | -14.07pp | 43.80x | 1.26x | 100.0% | 99.7% | -60.33% | 1973-11-19 | yes |

## Static Target-Leverage Candidates

Analysis: Static rows use explicit target leverage with adjacent ETFs, plus optional diversifier baskets. This removes the redundant free mix of SPY/SSO/UPRO.

Conclusion: Best static row is `static L3.00 E60% GLD annual` with terminal/SPY 5.15x, min relative equity after 10y 0.84x, and MDD -69.89%.

| Family | Name | L | CAGR | Spread | MDD | MDD vs SPY | Terminal/SPY | Min Rel 10y+ | Above 10y+ | 10y+ Hit | Rel DD | Sustained Above | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| static target leverage | static L3.00 E60% GLD annual | 3.00 | 14.04% | +3.17pp | -69.89% | -14.75pp | 5.15x | 0.84x | 94.9% | 59.8% | -71.02% | 2009-03-12 | no |
| static target leverage | static L2.75 E60% GLD annual | 2.75 | 13.89% | +3.02pp | -66.36% | -11.22pp | 4.76x | 0.92x | 98.2% | 60.6% | -69.38% | 2003-05-20 | no |
| static target leverage | static L2.50 E60% GLD annual | 2.50 | 13.67% | +2.80pp | -62.95% | -7.81pp | 4.26x | 0.98x | 99.2% | 61.7% | -68.43% | 2003-04-22 | no |
| static target leverage | static L2.50 E70% GLD annual | 2.50 | 13.62% | +2.76pp | -71.75% | -16.61pp | 4.16x | 0.86x | 93.9% | 65.0% | -58.94% | 2009-07-15 | no |
| static target leverage | static L2.25 E70% GLD annual | 2.25 | 13.42% | +2.55pp | -68.07% | -12.93pp | 3.75x | 0.95x | 98.7% | 65.7% | -56.60% | 2003-04-28 | no |
| static target leverage | static L2.50 E60% 50 ZROZ / 50 GLD annual | 2.50 | 13.58% | +2.71pp | -57.87% | -2.73pp | 4.07x | 0.65x | 80.3% | 79.5% | -50.21% | 1995-02-03 | no |
| static target leverage | static L2.75 E60% 50 ZROZ / 50 GLD annual | 2.75 | 13.76% | +2.89pp | -62.30% | -7.16pp | 4.46x | 0.58x | 73.6% | 76.4% | -53.12% | 2002-10-24 | no |
| static target leverage | static L2.25 E60% 50 ZROZ / 50 GLD annual | 2.25 | 13.34% | +2.47pp | -54.01% | +1.13pp | 3.59x | 0.71x | 90.9% | 82.5% | -47.24% | 1991-07-25 | no |
| static target leverage | static L2.75 E70% GLD annual | 2.75 | 13.74% | +2.87pp | -75.56% | -20.42pp | 4.40x | 0.75x | 76.1% | 63.4% | -62.63% | 2010-07-07 | no |
| static target leverage | static L2.25 E60% GLD annual | 2.25 | 13.39% | +2.52pp | -59.39% | -4.25pp | 3.69x | 1.01x | 100.0% | 58.8% | -67.98% | 1972-05-22 | no |
| static target leverage | static L3.00 E60% 50 ZROZ / 50 GLD annual | 3.00 | 13.88% | +3.01pp | -66.59% | -11.44pp | 4.74x | 0.52x | 67.8% | 74.1% | -55.98% | 2003-08-15 | no |
| static target leverage | static L2.50 E60% 50 ZROZ / 50 GLD quarterly | 2.50 | 13.47% | +2.60pp | -66.36% | -11.22pp | 3.84x | 0.57x | 78.3% | 81.8% | -47.59% | 1992-06-29 | no |
| static target leverage | static L2.00 E60% 50 ZROZ / 50 GLD annual | 2.00 | 13.03% | +2.16pp | -50.03% | +5.11pp | 3.07x | 0.78x | 94.7% | 85.0% | -44.30% | 1985-05-14 | no |
| static target leverage | static L2.00 E70% GLD annual | 2.00 | 13.13% | +2.27pp | -64.12% | -8.97pp | 3.24x | 1.02x | 100.0% | 63.0% | -55.22% | 1972-05-26 | no |
| static target leverage | static L2.75 E60% 50 ZROZ / 50 GLD quarterly | 2.75 | 13.65% | +2.78pp | -70.68% | -15.54pp | 4.21x | 0.50x | 70.1% | 78.7% | -53.55% | 2009-03-12 | no |
| static target leverage | static L2.25 E60% 50 ZROZ / 50 GLD quarterly | 2.25 | 13.22% | +2.35pp | -61.65% | -6.51pp | 3.37x | 0.64x | 85.8% | 84.7% | -44.25% | 1991-01-16 | no |
| static target leverage | static L2.75 E60% GLD quarterly | 2.75 | 13.43% | +2.56pp | -73.42% | -18.28pp | 3.77x | 0.76x | 90.5% | 58.5% | -66.96% | 2010-02-11 | no |
| static target leverage | static L2.75 E60% 60 ZROZ / 40 GLD annual | 2.75 | 13.64% | +2.77pp | -61.60% | -6.46pp | 4.19x | 0.49x | 66.9% | 76.1% | -55.25% | 2003-04-17 | no |
| static target leverage | static L3.00 E60% 50 ZROZ / 50 GLD quarterly | 3.00 | 13.75% | +2.89pp | -74.54% | -19.40pp | 4.45x | 0.44x | 63.5% | 76.6% | -60.29% | 2009-08-20 | no |
| static target leverage | static L3.00 E70% GLD annual | 3.00 | 13.76% | +2.89pp | -80.41% | -25.27pp | 4.45x | 0.60x | 64.1% | 60.8% | -68.09% | 2012-06-05 | no |

## Tactical SMA Candidates

Analysis: Tactical rows hold the target-leverage risk-on sleeve only when lagged SPY is above its SMA; risk-off is a diversifier basket. Signals are lagged to avoid same-close lookahead.

Conclusion: Best tactical row is `SMA200 L3.00 off 60 ZROZ / 40 GLD daily` with terminal/SPY 73.13x, min relative equity after 10y 1.31x, and MDD -63.28%.

| Family | Name | L | CAGR | Spread | MDD | MDD vs SPY | Terminal/SPY | Min Rel 10y+ | Above 10y+ | 10y+ Hit | Rel DD | Sustained Above | Pass |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tactical sma target leverage | SMA200 L3.00 off 60 ZROZ / 40 GLD daily | 3.00 | 19.38% | +8.51pp | -63.28% | -8.14pp | 73.13x | 1.31x | 100.0% | 95.1% | -62.19% | 1970-12-04 | yes |
| tactical sma target leverage | SMA200 L3.00 off 50 ZROZ / 50 GLD daily | 3.00 | 19.30% | +8.44pp | -63.74% | -8.59pp | 70.63x | 1.46x | 100.0% | 94.9% | -62.61% | 1970-12-03 | yes |
| tactical sma target leverage | SMA200 L3.00 off 40 ZROZ / 40 GLD / 20 IEF daily | 3.00 | 19.05% | +8.18pp | -63.97% | -8.83pp | 62.42x | 1.40x | 100.0% | 94.7% | -62.53% | 1970-12-02 | yes |
| tactical sma target leverage | SMA200 L2.75 off 60 ZROZ / 40 GLD daily | 2.75 | 18.98% | +8.11pp | -58.93% | -3.79pp | 60.20x | 1.36x | 100.0% | 96.2% | -58.15% | 1970-12-04 | yes |
| tactical sma target leverage | SMA200 L2.75 off 50 ZROZ / 50 GLD daily | 2.75 | 18.91% | +8.04pp | -58.61% | -3.47pp | 58.14x | 1.52x | 100.0% | 96.0% | -57.65% | 1970-12-02 | yes |
| tactical sma target leverage | SMA250 L3.00 off 60 ZROZ / 40 GLD daily | 3.00 | 18.84% | +7.97pp | -64.49% | -9.35pp | 56.31x | 1.22x | 100.0% | 96.3% | -67.10% | 1973-11-26 | yes |
| tactical sma target leverage | SMA300 L3.00 off 60 ZROZ / 40 GLD daily | 3.00 | 18.85% | +7.98pp | -78.25% | -23.11pp | 56.62x | 1.15x | 100.0% | 94.3% | -73.38% | 1973-11-19 | yes |
| tactical sma target leverage | SMA200 L3.00 off 50 ZROZ / 25 GLD / 25 CASH daily | 3.00 | 18.83% | +7.96pp | -65.02% | -9.88pp | 55.92x | 1.24x | 100.0% | 94.3% | -63.81% | 1970-12-01 | yes |
| tactical sma target leverage | SMA300 L3.00 off 60 ZROZ / 40 GLD monthly | 3.00 | 18.70% | +7.83pp | -78.50% | -23.36pp | 52.57x | 1.38x | 100.0% | 97.0% | -72.61% | 1971-12-01 | yes |
| tactical sma target leverage | SMA300 L2.75 off 60 ZROZ / 40 GLD daily | 2.75 | 18.66% | +7.79pp | -73.80% | -18.66pp | 51.50x | 1.21x | 100.0% | 98.2% | -67.27% | 1973-11-19 | yes |
| tactical sma target leverage | SMA200 L2.75 off 40 ZROZ / 40 GLD / 20 IEF daily | 2.75 | 18.65% | +7.78pp | -58.79% | -3.65pp | 51.38x | 1.45x | 100.0% | 95.9% | -57.77% | 1970-12-02 | yes |
| tactical sma target leverage | SMA250 L3.00 off 50 ZROZ / 50 GLD daily | 3.00 | 18.64% | +7.77pp | -64.12% | -8.98pp | 50.99x | 1.34x | 100.0% | 96.5% | -67.05% | 1973-11-26 | yes |
| tactical sma target leverage | SMA300 L2.75 off 60 ZROZ / 40 GLD monthly | 2.75 | 18.60% | +7.73pp | -74.15% | -19.00pp | 50.03x | 1.43x | 100.0% | 98.1% | -67.23% | 1971-12-01 | yes |
| tactical sma target leverage | SMA250 L2.75 off 50 ZROZ / 50 GLD monthly | 2.75 | 18.68% | +7.81pp | -74.15% | -19.00pp | 52.12x | 1.01x | 100.0% | 91.4% | -70.39% | 1974-02-04 | yes |
| tactical sma target leverage | SMA200 L2.50 off 60 ZROZ / 40 GLD daily | 2.50 | 18.48% | +7.61pp | -56.23% | -1.09pp | 47.21x | 1.41x | 100.0% | 97.0% | -53.82% | 1970-12-04 | yes |
| tactical sma target leverage | SMA250 L2.75 off 60 ZROZ / 40 GLD daily | 2.75 | 18.50% | +7.63pp | -60.75% | -5.61pp | 47.75x | 1.28x | 100.0% | 96.6% | -65.33% | 1973-11-26 | yes |
| tactical sma target leverage | SMA300 L3.00 off 50 ZROZ / 50 GLD daily | 3.00 | 18.63% | +7.76pp | -79.57% | -24.43pp | 50.70x | 1.24x | 100.0% | 90.1% | -75.04% | 1973-08-16 | yes |
| tactical sma target leverage | SMA300 L3.00 off 50 ZROZ / 50 GLD monthly | 3.00 | 18.56% | +7.69pp | -78.50% | -23.36pp | 49.03x | 1.55x | 100.0% | 93.3% | -73.54% | 1971-11-30 | yes |
| tactical sma target leverage | SMA300 L2.75 off 50 ZROZ / 50 GLD monthly | 2.75 | 18.46% | +7.59pp | -74.15% | -19.00pp | 46.66x | 1.60x | 100.0% | 96.9% | -67.60% | 1971-12-01 | yes |
| tactical sma target leverage | SMA250 L3.00 off 40 ZROZ / 40 GLD / 20 IEF daily | 3.00 | 18.43% | +7.56pp | -64.41% | -9.27pp | 46.12x | 1.30x | 100.0% | 96.5% | -66.80% | 1973-11-20 | yes |

## Phase Verdict

| Question | Verdict |
|---|---|
| Did we remove redundant free SPY/SSO/UPRO mixing? | Yes; all equity sleeves use an explicit adjacent target-leverage ladder. |
| Did any candidate pass equity dominance after 10y warmup? | Yes. |
| Did any candidate stay above SPY for the full period? | No. |
| Is worse absolute MDD allowed in this phase? | Yes; MDD is diagnostic only. |
| Is this deployment-ready? | No. This is an objective pivot and still research-only. |

Recommended next step: inspect the top dominance rows manually, then run a narrow validation/stress pass on only the selected static and tactical families.
