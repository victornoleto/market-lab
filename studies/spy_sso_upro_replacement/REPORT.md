# SPY/SSO/UPRO Replacement - Static Phase 1 Report

Status: research-only static-grid execution. This report does not authorize deployment, paper trading or mandate changes.

Method references: rolling-window robustness and parameter sensitivity are diagnostics against overfit and regime dependence `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. LETF exposure and volatility-decay caveats follow `[leverage_for_the_long_run, p.13]`.

## Executive Conclusion

The first monthly static run did not pass the preferred target, but lower-frequency static rebalancing did. The lead candidate is `80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD` with `quarterly` rebalance, CAGR 11.47%, MDD -55.18%, minimum 10y+ hit rate 93.3% and terminal wealth 1.37x versus SPY.

Practical conclusion: static SPY/SSO/UPRO mixes can improve long-horizon return versus SPY, but five-year windows remain too regime-sensitive for a static strategy to claim near-always outperformance. The current lead is cadence-sensitive, so quarterly/annual rebalancing must be part of the specification.

## Source Data

| Item | Value |
|---|---|
| Testfol.io cache | `data/testfolio/cache/history.parquet` |
| Daily common window | `1968-04-02` to `2026-05-21` |
| Assets | `SPYSIM, SSOSIM, UPROSIM, ZROZSIM, GLDSIM, IEFSIM, CASHX` |
| SPY baseline | CAGR 10.87%, MDD -55.14%, Sharpe 0.690 |
| Grid candidates after constraints | `72,427` |
| Monthly-triage preferred pass count | `0` |
| Exact preferred rows across cadences | `39` |
| Exact monthly preferred rows | `0` |
| Exact finalist rows | `888` including rebalance cadence variants |

The broad grid uses monthly returns for scalable triage. The finalist table below is recomputed with daily returns and exact monthly/quarterly/annual rebalancing.

## Top Exact Daily Finalists

Analysis: This table is the primary result. It ranks finalist portfolios after daily exact recomputation, not just monthly triage. `Preferred=yes` means CAGR beats SPY, 10y+ rolling hit rate is at least 90%, and drawdown is no worse than SPY by more than 5pp or better than -60%.

Conclusion: Preferred candidates exist only after allowing lower-frequency static rebalancing. The lead is a modest-leverage S&P mix with small ZROZ/GLD sleeves, not an aggressive HFEA-style portfolio.

| Name | Rebal | Weights | CAGR | Spread | MDD | MDD vs SPY | 10y+ hit min | 5y+ hit min | 10y+ p10 min | Terminal/SPY | Preferred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | quarterly | 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | 11.47% | +0.60pp | -55.18% | -0.04pp | 93.3% | 79.7% | 0.8% | 1.37x | yes |
| 70 SPY / 20 SSO / 5 ZROZ / 5 GLD | annual | 70 SPY / 20 SSO / 5 ZROZ / 5 GLD | 11.62% | +0.75pp | -55.58% | -0.44pp | 92.4% | 79.8% | 0.7% | 1.48x | yes |
| 75 SPY / 15 SSO / 5 ZROZ / 5 GLD | quarterly | 75 SPY / 15 SSO / 5 ZROZ / 5 GLD | 11.46% | +0.59pp | -55.36% | -0.22pp | 92.1% | 79.4% | 0.7% | 1.36x | yes |
| 65 SPY / 15 UPRO / 10 ZROZ / 10 GLD | quarterly | 65 SPY / 15 UPRO / 10 ZROZ / 10 GLD | 12.03% | +1.16pp | -55.08% | +0.06pp | 92.0% | 78.9% | 1.1% | 1.83x | yes |
| 75 SPY / 10 SSO / 5 UPRO / 5 ZROZ / 5 GLD | annual | 75 SPY / 10 SSO / 5 UPRO / 5 ZROZ / 5 GLD | 11.63% | +0.76pp | -55.05% | +0.09pp | 91.9% | 79.6% | 0.5% | 1.49x | yes |
| 60 SPY / 10 SSO / 10 UPRO / 10 ZROZ / 10 GLD | quarterly | 60 SPY / 10 SSO / 10 UPRO / 10 ZROZ / 10 GLD | 12.01% | +1.15pp | -55.26% | -0.12pp | 91.6% | 78.8% | 1.1% | 1.82x | yes |
| 65 SPY / 5 SSO / 10 UPRO / 10 ZROZ / 10 GLD | quarterly | 65 SPY / 5 SSO / 10 UPRO / 10 ZROZ / 10 GLD | 11.89% | +1.02pp | -53.14% | +2.00pp | 91.5% | 79.4% | 0.5% | 1.70x | yes |
| 75 SPY / 15 SSO / 5 ZROZ / 5 GLD | annual | 75 SPY / 15 SSO / 5 ZROZ / 5 GLD | 11.49% | +0.63pp | -53.70% | +1.44pp | 91.5% | 79.8% | 0.4% | 1.39x | yes |
| 55 SPY / 20 SSO / 5 UPRO / 10 ZROZ / 10 GLD | quarterly | 55 SPY / 20 SSO / 5 UPRO / 10 ZROZ / 10 GLD | 12.00% | +1.13pp | -55.44% | -0.30pp | 91.4% | 78.7% | 0.9% | 1.81x | yes |
| 60 SPY / 15 SSO / 5 UPRO / 10 ZROZ / 10 GLD | quarterly | 60 SPY / 15 SSO / 5 UPRO / 10 ZROZ / 10 GLD | 11.88% | +1.01pp | -53.32% | +1.82pp | 91.4% | 79.4% | 0.5% | 1.69x | yes |
| 60 SPY / 15 UPRO / 15 ZROZ / 10 GLD | quarterly | 60 SPY / 15 UPRO / 15 ZROZ / 10 GLD | 12.09% | +1.22pp | -51.60% | +3.54pp | 91.4% | 78.6% | 1.2% | 1.89x | yes |
| 55 SPY / 10 SSO / 10 UPRO / 15 ZROZ / 10 GLD | quarterly | 55 SPY / 10 SSO / 10 UPRO / 15 ZROZ / 10 GLD | 12.08% | +1.21pp | -51.78% | +3.36pp | 91.1% | 78.4% | 0.9% | 1.87x | yes |
| 50 SPY / 30 SSO / 10 ZROZ / 10 GLD | quarterly | 50 SPY / 30 SSO / 10 ZROZ / 10 GLD | 11.99% | +1.12pp | -55.62% | -0.47pp | 90.9% | 78.3% | 0.6% | 1.79x | yes |
| 75 SPY / 10 UPRO / 5 ZROZ / 5 GLD / 5 IEF | quarterly | 75 SPY / 10 UPRO / 5 ZROZ / 5 GLD / 5 IEF | 11.47% | +0.61pp | -54.60% | +0.54pp | 90.9% | 78.1% | 0.4% | 1.37x | yes |
| 55 SPY / 25 SSO / 10 ZROZ / 10 GLD | quarterly | 55 SPY / 25 SSO / 10 ZROZ / 10 GLD | 11.87% | +1.00pp | -53.51% | +1.63pp | 90.9% | 79.4% | 0.4% | 1.68x | yes |
| 45 SPY / 5 SSO / 20 UPRO / 15 ZROZ / 15 GLD | quarterly | 45 SPY / 5 SSO / 20 UPRO / 15 ZROZ / 15 GLD | 12.52% | +1.65pp | -55.22% | -0.08pp | 90.8% | 77.9% | 0.8% | 2.36x | yes |
| 55 SPY / 5 SSO / 15 UPRO / 10 ZROZ / 10 GLD / 5 IEF | quarterly | 55 SPY / 5 SSO / 15 UPRO / 10 ZROZ / 10 GLD / 5 IEF | 12.01% | +1.14pp | -54.69% | +0.45pp | 90.8% | 77.4% | 0.5% | 1.81x | yes |
| 40 SPY / 15 SSO / 15 UPRO / 15 ZROZ / 15 GLD | quarterly | 40 SPY / 15 SSO / 15 UPRO / 15 ZROZ / 15 GLD | 12.51% | +1.64pp | -55.40% | -0.26pp | 90.7% | 77.8% | 0.6% | 2.34x | yes |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | annual | 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | 11.50% | +0.63pp | -53.16% | +1.98pp | 90.6% | 78.6% | 0.1% | 1.39x | yes |
| 50 SPY / 20 SSO / 5 UPRO / 15 ZROZ / 10 GLD | quarterly | 50 SPY / 20 SSO / 5 UPRO / 15 ZROZ / 10 GLD | 12.06% | +1.20pp | -51.97% | +3.17pp | 90.6% | 78.2% | 0.5% | 1.86x | yes |
| 50 SPY / 20 UPRO / 15 ZROZ / 15 GLD | quarterly | 50 SPY / 20 UPRO / 15 ZROZ / 15 GLD | 12.40% | +1.53pp | -53.14% | +2.00pp | 90.5% | 78.4% | 0.4% | 2.22x | yes |
| 35 SPY / 25 SSO / 10 UPRO / 15 ZROZ / 15 GLD | quarterly | 35 SPY / 25 SSO / 10 UPRO / 15 ZROZ / 15 GLD | 12.49% | +1.63pp | -55.59% | -0.45pp | 90.5% | 77.6% | 0.5% | 2.33x | yes |
| 50 SPY / 15 SSO / 10 UPRO / 10 ZROZ / 10 GLD / 5 IEF | quarterly | 50 SPY / 15 SSO / 10 UPRO / 10 ZROZ / 10 GLD / 5 IEF | 12.00% | +1.13pp | -54.87% | +0.27pp | 90.5% | 77.3% | 0.3% | 1.80x | yes |
| 40 SPY / 5 SSO / 20 UPRO / 20 ZROZ / 15 GLD | quarterly | 40 SPY / 5 SSO / 20 UPRO / 20 ZROZ / 15 GLD | 12.55% | +1.68pp | -51.92% | +3.22pp | 90.5% | 78.1% | 0.4% | 2.40x | yes |
| 45 SPY / 35 SSO / 10 ZROZ / 10 GLD | annual | 45 SPY / 35 SSO / 10 ZROZ / 10 GLD | 12.19% | +1.32pp | -54.22% | +0.92pp | 90.5% | 79.9% | 0.2% | 1.98x | yes |

## Rebalance Cadence Sensitivity

Analysis: Rebalance cadence matters because LETF drawdowns interact with when the portfolio buys back into the levered sleeve. Quarterly and annual variants can materially change drawdown and terminal wealth.

Conclusion: Static does not mean cadence-free. Any implementation candidate must specify rebalance frequency explicitly.

| Name | Rebal | Weights | CAGR | Spread | MDD | MDD vs SPY | 10y+ hit min | 5y+ hit min | 10y+ p10 min | Terminal/SPY | Preferred |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 SSO / 25 ZROZ / 25 GLD | annual | 50 SSO / 25 ZROZ / 25 GLD | 12.83% | +1.96pp | -47.13% | +8.02pp | 77.3% | 70.2% | -7.6% | 2.76x | no |
| 50 SSO / 25 ZROZ / 25 GLD | monthly | 50 SSO / 25 ZROZ / 25 GLD | 12.09% | +1.22pp | -50.34% | +4.80pp | 70.8% | 65.5% | -9.0% | 1.89x | no |
| 50 SSO / 25 ZROZ / 25 GLD | quarterly | 50 SSO / 25 ZROZ / 25 GLD | 12.68% | +1.81pp | -46.26% | +8.88pp | 79.4% | 69.1% | -6.1% | 2.57x | no |
| 60 SSO / 40 ZROZ | annual | 60 SSO / 40 ZROZ | 12.23% | +1.36pp | -64.80% | -9.66pp | 77.8% | 67.6% | -35.3% | 2.03x | no |
| 60 SSO / 40 ZROZ | monthly | 60 SSO / 40 ZROZ | 11.81% | +0.94pp | -65.46% | -10.32pp | 79.0% | 64.0% | -37.0% | 1.63x | no |
| 60 SSO / 40 ZROZ | quarterly | 60 SSO / 40 ZROZ | 12.49% | +1.62pp | -65.26% | -10.12pp | 80.7% | 70.2% | -35.6% | 2.32x | no |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | annual | 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | 11.50% | +0.63pp | -53.16% | +1.98pp | 90.6% | 78.6% | 0.1% | 1.39x | yes |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | monthly | 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | 11.28% | +0.41pp | -56.31% | -1.17pp | 85.8% | 73.6% | -0.8% | 1.24x | no |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | quarterly | 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | 11.47% | +0.60pp | -55.18% | -0.04pp | 93.3% | 79.7% | 0.8% | 1.37x | yes |
| SPY buy-hold | annual | 100 SPY | 10.87% | -0.00pp | -55.14% | -0.00pp | 0.0% | 0.0% | 0.0% | 1.00x | no |
| SPY buy-hold | monthly | 100 SPY | 10.87% | +0.00pp | -55.14% | -0.00pp | 0.0% | 0.0% | 0.0% | 1.00x | no |
| SPY buy-hold | quarterly | 100 SPY | 10.87% | +0.00pp | -55.14% | -0.00pp | 0.0% | 0.0% | 0.0% | 1.00x | no |

## Named-Regime Stress

Analysis: The preferred static mixes tend to improve long-run terminal wealth but can still suffer hard in equity-led crashes. ZROZ helps in classic equity crashes, but 2022-style stock/bond correlation shocks remain the key static-portfolio weakness.

Conclusion: Static LETF replacement candidates must be judged mainly by whether their 2022 and recent-window behavior is tolerable, not only by full-history CAGR.

| Name | Rebal | Regime | Window | Return | SPY | Spread | MDD | SPY MDD |
|---|---|---|---|---|---|---|---|---|
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | monthly | Dot-com bust | 2000-03-24..2002-10-09 | -48.66% | -47.06% | -1.59pp | -48.93% | -47.38% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | monthly | GFC | 2007-10-09..2009-03-09 | -55.86% | -54.72% | -1.14pp | -56.31% | -55.14% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | monthly | Covid crash | 2020-02-19..2020-03-23 | -33.80% | -33.38% | -0.42pp | -34.15% | -33.69% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | monthly | Inflation/rates shock | 2022-01-03..2022-10-14 | -27.59% | -23.78% | -3.81pp | -27.88% | -24.44% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | monthly | Recent recovery | 2022-10-14..2026-05-21 | 122.74% | 113.43% | +9.32pp | -19.51% | -18.74% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | quarterly | Dot-com bust | 2000-03-24..2002-10-09 | -47.95% | -47.06% | -0.89pp | -48.21% | -47.38% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | quarterly | GFC | 2007-10-09..2009-03-09 | -54.72% | -54.72% | -0.00pp | -55.18% | -55.14% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | quarterly | Covid crash | 2020-02-19..2020-03-23 | -32.71% | -33.38% | +0.66pp | -33.07% | -33.69% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | quarterly | Inflation/rates shock | 2022-01-03..2022-10-14 | -27.61% | -23.78% | -3.83pp | -27.90% | -24.44% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | quarterly | Recent recovery | 2022-10-14..2026-05-21 | 122.52% | 113.43% | +9.10pp | -19.49% | -18.74% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | annual | Dot-com bust | 2000-03-24..2002-10-09 | -46.75% | -47.06% | +0.32pp | -47.01% | -47.38% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | annual | GFC | 2007-10-09..2009-03-09 | -52.68% | -54.72% | +2.04pp | -53.16% | -55.14% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | annual | Covid crash | 2020-02-19..2020-03-23 | -32.71% | -33.38% | +0.66pp | -33.07% | -33.69% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | annual | Inflation/rates shock | 2022-01-03..2022-10-14 | -27.05% | -23.78% | -3.28pp | -27.34% | -24.44% |
| 80 SPY / 5 SSO / 5 UPRO / 5 ZROZ / 5 GLD | annual | Recent recovery | 2022-10-14..2026-05-21 | 122.58% | 113.43% | +9.15pp | -19.24% | -18.74% |
| SPY buy-hold | monthly | Dot-com bust | 2000-03-24..2002-10-09 | -47.06% | -47.06% | +0.00pp | -47.38% | -47.38% |
| SPY buy-hold | monthly | GFC | 2007-10-09..2009-03-09 | -54.72% | -54.72% | -0.00pp | -55.14% | -55.14% |
| SPY buy-hold | monthly | Covid crash | 2020-02-19..2020-03-23 | -33.38% | -33.38% | +0.00pp | -33.69% | -33.69% |
| SPY buy-hold | monthly | Inflation/rates shock | 2022-01-03..2022-10-14 | -23.78% | -23.78% | -0.00pp | -24.44% | -24.44% |
| SPY buy-hold | monthly | Recent recovery | 2022-10-14..2026-05-21 | 113.43% | 113.43% | -0.00pp | -18.74% | -18.74% |
| SPY buy-hold | quarterly | Dot-com bust | 2000-03-24..2002-10-09 | -47.06% | -47.06% | +0.00pp | -47.38% | -47.38% |
| SPY buy-hold | quarterly | GFC | 2007-10-09..2009-03-09 | -54.72% | -54.72% | -0.00pp | -55.14% | -55.14% |
| SPY buy-hold | quarterly | Covid crash | 2020-02-19..2020-03-23 | -33.38% | -33.38% | -0.00pp | -33.69% | -33.69% |
| SPY buy-hold | quarterly | Inflation/rates shock | 2022-01-03..2022-10-14 | -23.78% | -23.78% | -0.00pp | -24.44% | -24.44% |
| SPY buy-hold | quarterly | Recent recovery | 2022-10-14..2026-05-21 | 113.43% | 113.43% | +0.00pp | -18.74% | -18.74% |
| SPY buy-hold | annual | Dot-com bust | 2000-03-24..2002-10-09 | -47.06% | -47.06% | +0.00pp | -47.38% | -47.38% |
| SPY buy-hold | annual | GFC | 2007-10-09..2009-03-09 | -54.72% | -54.72% | -0.00pp | -55.14% | -55.14% |
| SPY buy-hold | annual | Covid crash | 2020-02-19..2020-03-23 | -33.38% | -33.38% | -0.00pp | -33.69% | -33.69% |
| SPY buy-hold | annual | Inflation/rates shock | 2022-01-03..2022-10-14 | -23.78% | -23.78% | -0.00pp | -24.44% | -24.44% |
| SPY buy-hold | annual | Recent recovery | 2022-10-14..2026-05-21 | 113.43% | 113.43% | -0.00pp | -18.74% | -18.74% |
| 50 SSO / 25 ZROZ / 25 GLD | monthly | Dot-com bust | 2000-03-24..2002-10-09 | -43.24% | -47.06% | +3.83pp | -43.29% | -47.38% |
| 50 SSO / 25 ZROZ / 25 GLD | monthly | GFC | 2007-10-09..2009-03-09 | -49.03% | -54.72% | +5.69pp | -50.34% | -55.14% |
| 50 SSO / 25 ZROZ / 25 GLD | monthly | Covid crash | 2020-02-19..2020-03-23 | -29.34% | -33.38% | +4.03pp | -31.08% | -33.69% |
| 50 SSO / 25 ZROZ / 25 GLD | monthly | Inflation/rates shock | 2022-01-03..2022-10-14 | -36.25% | -23.78% | -12.47pp | -35.83% | -24.44% |
| 50 SSO / 25 ZROZ / 25 GLD | monthly | Recent recovery | 2022-10-14..2026-05-21 | 132.88% | 113.43% | +19.45pp | -18.40% | -18.74% |
| 50 SSO / 25 ZROZ / 25 GLD | quarterly | Dot-com bust | 2000-03-24..2002-10-09 | -40.80% | -47.06% | +6.26pp | -42.14% | -47.38% |
| 50 SSO / 25 ZROZ / 25 GLD | quarterly | GFC | 2007-10-09..2009-03-09 | -44.84% | -54.72% | +9.88pp | -46.26% | -55.14% |
| 50 SSO / 25 ZROZ / 25 GLD | quarterly | Covid crash | 2020-02-19..2020-03-23 | -25.37% | -33.38% | +8.00pp | -28.38% | -33.69% |
| 50 SSO / 25 ZROZ / 25 GLD | quarterly | Inflation/rates shock | 2022-01-03..2022-10-14 | -36.55% | -23.78% | -12.77pp | -36.14% | -24.44% |
| 50 SSO / 25 ZROZ / 25 GLD | quarterly | Recent recovery | 2022-10-14..2026-05-21 | 133.16% | 113.43% | +19.74pp | -18.30% | -18.74% |
| 50 SSO / 25 ZROZ / 25 GLD | annual | Dot-com bust | 2000-03-24..2002-10-09 | -37.01% | -47.06% | +10.06pp | -39.65% | -47.38% |
| 50 SSO / 25 ZROZ / 25 GLD | annual | GFC | 2007-10-09..2009-03-09 | -37.36% | -54.72% | +17.36pp | -38.96% | -55.14% |
| 50 SSO / 25 ZROZ / 25 GLD | annual | Covid crash | 2020-02-19..2020-03-23 | -25.37% | -33.38% | +8.00pp | -28.38% | -33.69% |
| 50 SSO / 25 ZROZ / 25 GLD | annual | Inflation/rates shock | 2022-01-03..2022-10-14 | -35.83% | -23.78% | -12.05pp | -35.41% | -24.44% |
| 50 SSO / 25 ZROZ / 25 GLD | annual | Recent recovery | 2022-10-14..2026-05-21 | 136.51% | 113.43% | +23.08pp | -17.41% | -18.74% |
| 60 SSO / 40 ZROZ | monthly | Dot-com bust | 2000-03-24..2002-10-09 | -49.32% | -47.06% | -2.25pp | -50.60% | -47.38% |
| 60 SSO / 40 ZROZ | monthly | GFC | 2007-10-09..2009-03-09 | -57.35% | -54.72% | -2.63pp | -57.99% | -55.14% |
| 60 SSO / 40 ZROZ | monthly | Covid crash | 2020-02-19..2020-03-23 | -32.55% | -33.38% | +0.83pp | -34.10% | -33.69% |
| 60 SSO / 40 ZROZ | monthly | Inflation/rates shock | 2022-01-03..2022-10-14 | -43.54% | -23.78% | -19.76pp | -43.17% | -24.44% |
| 60 SSO / 40 ZROZ | monthly | Recent recovery | 2022-10-14..2026-05-21 | 95.21% | 113.43% | -18.21pp | -25.62% | -18.74% |
| 60 SSO / 40 ZROZ | quarterly | Dot-com bust | 2000-03-24..2002-10-09 | -46.47% | -47.06% | +0.59pp | -49.70% | -47.38% |
| 60 SSO / 40 ZROZ | quarterly | GFC | 2007-10-09..2009-03-09 | -53.21% | -54.72% | +1.51pp | -53.91% | -55.14% |
| 60 SSO / 40 ZROZ | quarterly | Covid crash | 2020-02-19..2020-03-23 | -27.42% | -33.38% | +5.96pp | -31.02% | -33.69% |
| 60 SSO / 40 ZROZ | quarterly | Inflation/rates shock | 2022-01-03..2022-10-14 | -43.90% | -23.78% | -20.12pp | -43.53% | -24.44% |
| 60 SSO / 40 ZROZ | quarterly | Recent recovery | 2022-10-14..2026-05-21 | 97.60% | 113.43% | -15.83pp | -25.52% | -18.74% |
| 60 SSO / 40 ZROZ | annual | Dot-com bust | 2000-03-24..2002-10-09 | -42.41% | -47.06% | +4.65pp | -47.54% | -47.38% |
| 60 SSO / 40 ZROZ | annual | GFC | 2007-10-09..2009-03-09 | -45.14% | -54.72% | +9.58pp | -45.88% | -55.14% |
| 60 SSO / 40 ZROZ | annual | Covid crash | 2020-02-19..2020-03-23 | -27.42% | -33.38% | +5.96pp | -31.02% | -33.69% |
| 60 SSO / 40 ZROZ | annual | Inflation/rates shock | 2022-01-03..2022-10-14 | -44.12% | -23.78% | -20.34pp | -43.75% | -24.44% |
| 60 SSO / 40 ZROZ | annual | Recent recovery | 2022-10-14..2026-05-21 | 101.12% | 113.43% | -12.31pp | -24.66% | -18.74% |

## Static Phase Verdict

| Question | Verdict |
|---|---|
| Does a static candidate beat SPY CAGR? | Yes; best monthly exact finalist CAGR is 12.81%. |
| Does a static candidate pass the preferred 10y+ target? | Yes. |
| Does a static candidate pass strict 5y+ 90% hit with no worse MDD than SPY? | No. |
| Is this enough to claim a guaranteed SPY replacement? | No. It is enough to continue with focused robustness, not to deploy. |

Recommended next step: run Phase 1b around the lead static family with finer weights, explicit fee/drag stress and rolling daily drawdown diagnostics. If strict 5y+ behavior remains impossible, move to Phase 2 low-turnover LRS overlay.
