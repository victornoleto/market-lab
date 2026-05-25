# SPY/SSO/UPRO Replacement - Phase 1b Robustness Report

Status: research-only focused robustness. This report does not authorize deployment, paper trading or mandate changes.

Method references: fine-grid parameter sensitivity, implementation drag and rolling-window diagnostics are robustness checks, not proof of future performance `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.208-211]`. LETF exposure remains an embedded-leverage caveat `[leverage_for_the_long_run, p.13]`.

## Executive Conclusion

Phase 1b improved the local static search but still did not solve the strict 5y+ target. The top exact row is `89 SPY / 1 SSO / 4 UPRO / 3 ZROZ / 3 GLD` with `quarterly` rebalance: CAGR 11.24%, MDD -55.13%, minimum 10y+ hit rate 93.9%, minimum 5y+ hit rate 79.8% and terminal wealth 1.21x versus SPY.

Practical conclusion: treat the static branch as a robust near-miss if it keeps preferred 10y+ behavior under reasonable drag, but do not claim near-always SPY replacement unless 5y+ rolling behavior improves materially.

## Source Data

| Item | Value |
|---|---|
| Testfol.io cache | `data/testfolio/cache/history.parquet` |
| Daily common window | `1968-04-02` to `2026-05-21` |
| Assets | `SPYSIM, SSOSIM, UPROSIM, ZROZSIM, GLDSIM, IEFSIM, CASHX` |
| SPY baseline | CAGR 10.87%, MDD -55.14%, Sharpe 0.690 |
| Fine local grid rows | `722,791` |
| Monthly fine-grid preferred rows | `0` |
| Exact finalist rows | `1,260` including cadence variants |
| Exact preferred rows | `647` |
| Exact strict rows | `0` |
| Drag stress rows | `3,235` |
| Drag preferred rows | `717` total; `70` at 10 bps; `0` at 25 bps; `0` at 50 bps |


## Top Fine-Grid Exact Finalists

Analysis: These portfolios were found by 1% local-grid monthly triage and recomputed with daily exact monthly/quarterly/annual rebalancing. `Strict=yes` requires the 5y+ hit-rate target and no worse MDD than SPY.

Conclusion: The focused static family still fails strict 5y+ robustness; any viable static interpretation remains a 10y+ preferred-target result only.

| Name | Rebal | Weights | CAGR | Spread | MDD | MDD vs SPY | 10y+ hit min | 5y+ hit min | 10y+ p10 min | Terminal/SPY | Preferred | Strict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 89 SPY / 1 SSO / 4 UPRO / 3 ZROZ / 3 GLD | quarterly | 89 SPY / 1 SSO / 4 UPRO / 3 ZROZ / 3 GLD | 11.24% | +0.37pp | -55.13% | +0.02pp | 93.9% | 79.8% | 0.6% | 1.21x | yes | no |
| 89 SPY / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 89 SPY / 4 UPRO / 4 ZROZ / 3 GLD | 11.23% | +0.36pp | -54.00% | +1.14pp | 93.9% | 80.3% | 0.5% | 1.21x | yes | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | 11.35% | +0.48pp | -54.02% | +1.13pp | 93.9% | 80.3% | 0.8% | 1.29x | yes | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | 11.23% | +0.36pp | -54.04% | +1.10pp | 93.8% | 80.2% | 0.5% | 1.21x | yes | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | 11.38% | +0.51pp | -54.40% | +0.74pp | 93.8% | 80.8% | 0.9% | 1.31x | yes | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | 11.26% | +0.39pp | -54.43% | +0.71pp | 93.8% | 81.0% | 0.7% | 1.23x | yes | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | 11.24% | +0.37pp | -55.16% | -0.02pp | 93.8% | 79.9% | 0.6% | 1.21x | yes | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | 11.36% | +0.49pp | -55.10% | +0.04pp | 93.8% | 79.8% | 0.8% | 1.29x | yes | no |
| 84 SPY / 3 SSO / 4 UPRO / 5 ZROZ / 4 GLD | quarterly | 84 SPY / 3 SSO / 4 UPRO / 5 ZROZ / 4 GLD | 11.35% | +0.48pp | -54.05% | +1.09pp | 93.7% | 80.3% | 0.8% | 1.28x | yes | no |
| 87 SPY / 4 SSO / 2 UPRO / 4 ZROZ / 3 GLD | quarterly | 87 SPY / 4 SSO / 2 UPRO / 4 ZROZ / 3 GLD | 11.23% | +0.36pp | -54.08% | +1.07pp | 93.7% | 80.1% | 0.5% | 1.21x | yes | no |
| 85 SPY / 2 SSO / 5 UPRO / 4 ZROZ / 4 GLD | quarterly | 85 SPY / 2 SSO / 5 UPRO / 4 ZROZ / 4 GLD | 11.36% | +0.49pp | -55.13% | +0.01pp | 93.7% | 79.7% | 0.7% | 1.29x | yes | no |
| 82 SPY / 7 UPRO / 6 ZROZ / 5 GLD | quarterly | 82 SPY / 7 UPRO / 6 ZROZ / 5 GLD | 11.47% | +0.60pp | -53.99% | +1.15pp | 93.7% | 80.4% | 0.9% | 1.37x | yes | no |
| 84 SPY / 2 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 84 SPY / 2 SSO / 5 UPRO / 5 ZROZ / 4 GLD | 11.38% | +0.51pp | -54.44% | +0.70pp | 93.7% | 80.8% | 0.8% | 1.30x | yes | no |
| 90 SPY / 4 UPRO / 3 ZROZ / 3 GLD | quarterly | 90 SPY / 4 UPRO / 3 ZROZ / 3 GLD | 11.21% | +0.34pp | -54.71% | +0.44pp | 93.6% | 80.4% | 0.5% | 1.20x | yes | no |
| 81 SPY / 2 SSO / 6 UPRO / 6 ZROZ / 5 GLD | quarterly | 81 SPY / 2 SSO / 6 UPRO / 6 ZROZ / 5 GLD | 11.47% | +0.60pp | -54.03% | +1.11pp | 93.6% | 80.4% | 0.9% | 1.37x | yes | no |
| 87 SPY / 5 SSO / 2 UPRO / 3 ZROZ / 3 GLD | quarterly | 87 SPY / 5 SSO / 2 UPRO / 3 ZROZ / 3 GLD | 11.23% | +0.36pp | -55.20% | -0.06pp | 93.6% | 79.9% | 0.5% | 1.21x | yes | no |
| 83 SPY / 5 SSO / 3 UPRO / 5 ZROZ / 4 GLD | quarterly | 83 SPY / 5 SSO / 3 UPRO / 5 ZROZ / 4 GLD | 11.35% | +0.48pp | -54.09% | +1.05pp | 93.6% | 80.3% | 0.7% | 1.28x | yes | no |
| 84 SPY / 4 SSO / 4 UPRO / 4 ZROZ / 4 GLD | quarterly | 84 SPY / 4 SSO / 4 UPRO / 4 ZROZ / 4 GLD | 11.35% | +0.48pp | -55.17% | -0.03pp | 93.6% | 79.8% | 0.7% | 1.29x | yes | no |
| 86 SPY / 6 SSO / 1 UPRO / 4 ZROZ / 3 GLD | quarterly | 86 SPY / 6 SSO / 1 UPRO / 4 ZROZ / 3 GLD | 11.23% | +0.36pp | -54.11% | +1.03pp | 93.5% | 80.0% | 0.5% | 1.21x | yes | no |
| 86 SPY / 1 SSO / 5 UPRO / 4 ZROZ / 4 GLD | quarterly | 86 SPY / 1 SSO / 5 UPRO / 4 ZROZ / 4 GLD | 11.33% | +0.46pp | -54.72% | +0.43pp | 93.5% | 80.5% | 0.7% | 1.27x | yes | no |
| 87 SPY / 3 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 87 SPY / 3 SSO / 3 UPRO / 4 ZROZ / 3 GLD | 11.26% | +0.39pp | -54.46% | +0.68pp | 93.5% | 81.1% | 0.7% | 1.23x | yes | no |
| 89 SPY / 2 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 89 SPY / 2 SSO / 3 UPRO / 3 ZROZ / 3 GLD | 11.21% | +0.34pp | -54.74% | +0.40pp | 93.5% | 80.5% | 0.5% | 1.19x | yes | no |
| 80 SPY / 4 SSO / 5 UPRO / 6 ZROZ / 5 GLD | quarterly | 80 SPY / 4 SSO / 5 UPRO / 6 ZROZ / 5 GLD | 11.46% | +0.59pp | -54.06% | +1.08pp | 93.5% | 80.4% | 0.9% | 1.36x | yes | no |
| 88 SPY / 4 SSO / 2 UPRO / 3 ZROZ / 3 GLD | quarterly | 88 SPY / 4 SSO / 2 UPRO / 3 ZROZ / 3 GLD | 11.21% | +0.34pp | -54.78% | +0.36pp | 93.5% | 80.6% | 0.5% | 1.19x | yes | no |
| 85 SPY / 3 SSO / 4 UPRO / 4 ZROZ / 4 GLD | quarterly | 85 SPY / 3 SSO / 4 UPRO / 4 ZROZ / 4 GLD | 11.33% | +0.46pp | -54.75% | +0.39pp | 93.4% | 80.4% | 0.6% | 1.27x | yes | no |

## Drag Stress

Analysis: Drag is applied to candidate portfolio returns only, not to SPY, so this is a conservative implementation haircut. The stress is generic bps/year drag rather than a claim about exact ETF expense ratios.

Conclusion: Candidates that only barely clear the 10y+ target under zero drag should not be promoted; survival at 25-50 bps is the minimum practical robustness signal. Counts above stress every exact preferred finalist; the table below shows the leading names only.

| Name | Rebal | Drag | CAGR | Spread | MDD | MDD vs SPY | 10y+ hit min | 5y+ hit min | 10y+ p10 min | Terminal/SPY | Preferred | Strict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | annual | 0 bps/yr | 11.37% | +0.50pp | -52.21% | +2.93pp | 90.8% | 76.0% | 0.2% | 1.30x | yes | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | annual | 10 bps/yr | 11.25% | +0.39pp | -52.28% | +2.86pp | 84.5% | 72.3% | -0.8% | 1.22x | no | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | annual | 25 bps/yr | 11.09% | +0.22pp | -52.38% | +2.76pp | 68.9% | 64.3% | -2.6% | 1.12x | no | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | annual | 50 bps/yr | 10.81% | -0.06pp | -52.55% | +2.59pp | 37.9% | 37.9% | -6.5% | 0.97x | no | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | annual | 100 bps/yr | 10.25% | -0.62pp | -52.88% | +2.26pp | 0.0% | 0.0% | -19.6% | 0.72x | no | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 0 bps/yr | 11.35% | +0.48pp | -54.02% | +1.13pp | 93.9% | 80.3% | 0.8% | 1.29x | yes | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 10 bps/yr | 11.24% | +0.37pp | -54.08% | +1.06pp | 88.3% | 75.2% | -0.2% | 1.21x | no | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 25 bps/yr | 11.07% | +0.20pp | -54.18% | +0.96pp | 70.7% | 62.3% | -1.7% | 1.11x | no | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 50 bps/yr | 10.79% | -0.08pp | -54.34% | +0.80pp | 43.4% | 43.4% | -5.8% | 0.96x | no | no |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 100 bps/yr | 10.24% | -0.63pp | -54.66% | +0.48pp | 0.0% | 0.0% | -19.0% | 0.72x | no | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | annual | 0 bps/yr | 11.39% | +0.52pp | -52.49% | +2.65pp | 90.8% | 76.8% | 0.2% | 1.32x | yes | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | annual | 10 bps/yr | 11.28% | +0.41pp | -52.55% | +2.59pp | 85.9% | 72.2% | -0.8% | 1.24x | no | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | annual | 25 bps/yr | 11.12% | +0.25pp | -52.65% | +2.49pp | 73.6% | 65.7% | -2.7% | 1.14x | no | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | annual | 50 bps/yr | 10.84% | -0.03pp | -52.82% | +2.32pp | 39.8% | 39.8% | -6.3% | 0.98x | no | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | annual | 100 bps/yr | 10.28% | -0.59pp | -53.15% | +1.99pp | 0.0% | 0.0% | -19.4% | 0.73x | no | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 0 bps/yr | 11.38% | +0.51pp | -54.40% | +0.74pp | 93.8% | 80.8% | 0.9% | 1.31x | yes | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 10 bps/yr | 11.27% | +0.40pp | -54.47% | +0.67pp | 89.5% | 75.4% | -0.1% | 1.23x | no | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 25 bps/yr | 11.10% | +0.23pp | -54.56% | +0.58pp | 74.5% | 66.2% | -1.6% | 1.13x | no | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 50 bps/yr | 10.82% | -0.05pp | -54.72% | +0.42pp | 43.7% | 43.7% | -5.4% | 0.98x | no | no |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 100 bps/yr | 10.27% | -0.60pp | -55.04% | +0.10pp | 0.0% | 0.0% | -18.6% | 0.73x | no | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | annual | 0 bps/yr | 11.38% | +0.51pp | -53.34% | +1.80pp | 90.3% | 78.2% | 0.0% | 1.31x | yes | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | annual | 10 bps/yr | 11.27% | +0.40pp | -53.40% | +1.74pp | 84.5% | 73.2% | -1.1% | 1.23x | no | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | annual | 25 bps/yr | 11.10% | +0.23pp | -53.50% | +1.64pp | 69.3% | 65.5% | -3.3% | 1.13x | no | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | annual | 50 bps/yr | 10.82% | -0.05pp | -53.67% | +1.47pp | 35.2% | 35.2% | -7.4% | 0.98x | no | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | annual | 100 bps/yr | 10.26% | -0.60pp | -53.99% | +1.15pp | 0.0% | 0.0% | -20.4% | 0.73x | no | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 0 bps/yr | 11.36% | +0.49pp | -55.10% | +0.04pp | 93.8% | 79.8% | 0.8% | 1.29x | yes | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 10 bps/yr | 11.25% | +0.38pp | -55.16% | -0.02pp | 88.4% | 75.7% | -0.2% | 1.22x | no | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 25 bps/yr | 11.08% | +0.21pp | -55.26% | -0.12pp | 71.8% | 68.9% | -1.7% | 1.12x | no | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 50 bps/yr | 10.80% | -0.07pp | -55.41% | -0.27pp | 38.5% | 38.5% | -6.6% | 0.96x | no | no |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 100 bps/yr | 10.24% | -0.62pp | -55.73% | -0.59pp | 0.0% | 0.0% | -19.7% | 0.72x | no | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | annual | 0 bps/yr | 11.27% | +0.40pp | -52.99% | +2.15pp | 91.0% | 76.7% | 0.2% | 1.23x | yes | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | annual | 10 bps/yr | 11.16% | +0.29pp | -53.05% | +2.09pp | 84.6% | 71.3% | -0.8% | 1.16x | no | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | annual | 25 bps/yr | 10.99% | +0.12pp | -53.15% | +1.99pp | 64.2% | 61.7% | -2.6% | 1.07x | no | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | annual | 50 bps/yr | 10.71% | -0.15pp | -53.32% | +1.82pp | 30.3% | 30.3% | -7.8% | 0.92x | no | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | annual | 100 bps/yr | 10.16% | -0.71pp | -53.65% | +1.49pp | 0.0% | 0.0% | -20.7% | 0.69x | no | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 0 bps/yr | 11.26% | +0.39pp | -54.43% | +0.71pp | 93.8% | 81.0% | 0.7% | 1.23x | yes | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 10 bps/yr | 11.15% | +0.28pp | -54.49% | +0.65pp | 87.9% | 73.9% | -0.3% | 1.16x | no | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 25 bps/yr | 10.98% | +0.11pp | -54.59% | +0.55pp | 65.6% | 58.3% | -1.8% | 1.06x | no | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 50 bps/yr | 10.70% | -0.16pp | -54.75% | +0.39pp | 24.2% | 24.2% | -7.2% | 0.92x | no | no |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 100 bps/yr | 10.15% | -0.72pp | -55.07% | +0.07pp | 0.0% | 0.0% | -20.2% | 0.68x | no | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | annual | 0 bps/yr | 11.24% | +0.37pp | -52.71% | +2.43pp | 90.4% | 76.3% | 0.1% | 1.22x | yes | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | annual | 10 bps/yr | 11.13% | +0.26pp | -52.78% | +2.36pp | 80.3% | 71.4% | -0.9% | 1.15x | no | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | annual | 25 bps/yr | 10.96% | +0.10pp | -52.88% | +2.26pp | 60.1% | 57.2% | -2.5% | 1.05x | no | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | annual | 50 bps/yr | 10.69% | -0.18pp | -53.05% | +2.09pp | 25.1% | 25.1% | -8.1% | 0.91x | no | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | annual | 100 bps/yr | 10.13% | -0.74pp | -53.38% | +1.76pp | 0.0% | 0.0% | -21.0% | 0.68x | no | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 0 bps/yr | 11.23% | +0.36pp | -54.04% | +1.10pp | 93.8% | 80.2% | 0.5% | 1.21x | yes | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 10 bps/yr | 11.12% | +0.25pp | -54.10% | +1.04pp | 84.1% | 70.5% | -0.5% | 1.14x | no | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 25 bps/yr | 10.95% | +0.08pp | -54.20% | +0.94pp | 60.6% | 55.1% | -2.0% | 1.05x | no | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 50 bps/yr | 10.68% | -0.19pp | -54.36% | +0.78pp | 19.3% | 19.3% | -7.6% | 0.90x | no | no |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 100 bps/yr | 10.12% | -0.75pp | -54.69% | +0.46pp | 0.0% | 0.0% | -20.6% | 0.67x | no | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | annual | 0 bps/yr | 11.25% | +0.38pp | -53.95% | +1.19pp | 91.5% | 78.9% | 0.2% | 1.22x | yes | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | annual | 10 bps/yr | 11.14% | +0.27pp | -54.01% | +1.13pp | 84.1% | 72.8% | -0.8% | 1.15x | no | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | annual | 25 bps/yr | 10.98% | +0.11pp | -54.11% | +1.03pp | 59.9% | 59.9% | -3.0% | 1.06x | no | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | annual | 50 bps/yr | 10.70% | -0.17pp | -54.27% | +0.87pp | 16.9% | 16.9% | -8.8% | 0.91x | no | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | annual | 100 bps/yr | 10.14% | -0.73pp | -54.60% | +0.55pp | 0.0% | 0.0% | -21.6% | 0.68x | no | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 0 bps/yr | 11.24% | +0.37pp | -55.16% | -0.02pp | 93.8% | 79.9% | 0.6% | 1.21x | yes | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 10 bps/yr | 11.12% | +0.26pp | -55.22% | -0.08pp | 86.0% | 74.1% | -0.4% | 1.14x | no | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 25 bps/yr | 10.96% | +0.09pp | -55.32% | -0.18pp | 62.3% | 61.6% | -1.9% | 1.05x | no | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 50 bps/yr | 10.68% | -0.19pp | -55.48% | -0.34pp | 8.9% | 8.9% | -8.5% | 0.91x | no | no |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 100 bps/yr | 10.12% | -0.75pp | -55.79% | -0.65pp | 0.0% | 0.0% | -21.3% | 0.68x | no | no |

## Rolling Drawdown Diagnostics

Analysis: This table computes 3y/5y/10y rolling within-window max drawdowns at roughly monthly steps. `Worst Spread` is portfolio rolling MDD minus SPY rolling MDD; negative values mean the candidate was worse.

Conclusion: Full-period MDD near SPY can hide rolling windows where the static LETF mix is meaningfully worse, especially around rate shocks and early-crash timing.

| Name | Rebal | Horizon | Worst MDD | SPY Worst | Worst Spread | Median Spread | Latest Spread | Worse >5pp |
|---|---|---|---|---|---|---|---|---|
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 3y | -54.02% | -55.14% | -5.08pp | -0.29pp | -0.24pp | 0.9% |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 5y | -54.02% | -55.14% | -5.08pp | +0.08pp | -2.78pp | 0.9% |
| 85 SPY / 1 SSO / 5 UPRO / 5 ZROZ / 4 GLD | quarterly | 10y | -54.02% | -55.14% | -4.12pp | +0.16pp | +1.37pp | 0.0% |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 3y | -54.40% | -55.14% | -5.34pp | -0.55pp | -0.41pp | 0.9% |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 5y | -54.40% | -55.14% | -5.34pp | -0.22pp | -3.01pp | 0.9% |
| 85 SPY / 6 UPRO / 5 ZROZ / 4 GLD | quarterly | 10y | -54.40% | -55.14% | -4.52pp | -0.09pp | +1.17pp | 0.0% |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 3y | -55.10% | -55.14% | -4.96pp | -0.69pp | -0.59pp | 0.0% |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 5y | -55.10% | -55.14% | -4.96pp | -0.64pp | -2.84pp | 0.0% |
| 86 SPY / 6 UPRO / 4 ZROZ / 4 GLD | quarterly | 10y | -55.10% | -55.14% | -4.78pp | -0.64pp | +0.62pp | 0.0% |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 3y | -54.43% | -55.14% | -4.07pp | -0.32pp | -0.27pp | 0.0% |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 5y | -54.43% | -55.14% | -4.07pp | -0.09pp | -2.29pp | 0.0% |
| 88 SPY / 1 SSO / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 10y | -54.43% | -55.14% | -3.28pp | +0.00pp | +0.98pp | 0.0% |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 3y | -54.04% | -55.14% | -3.81pp | -0.14pp | -0.10pp | 0.0% |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 5y | -54.04% | -55.14% | -3.81pp | +0.16pp | -2.06pp | 0.0% |
| 88 SPY / 2 SSO / 3 UPRO / 4 ZROZ / 3 GLD | quarterly | 10y | -54.04% | -55.14% | -2.88pp | +0.29pp | +1.18pp | 0.0% |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 3y | -55.16% | -55.14% | -3.72pp | -0.52pp | -0.45pp | 0.0% |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 5y | -55.16% | -55.14% | -3.72pp | -0.50pp | -2.12pp | 0.0% |
| 88 SPY / 3 SSO / 3 UPRO / 3 ZROZ / 3 GLD | quarterly | 10y | -55.16% | -55.14% | -3.59pp | -0.50pp | +0.38pp | 0.0% |
| 89 SPY / 1 SSO / 4 UPRO / 3 ZROZ / 3 GLD | quarterly | 3y | -55.13% | -55.14% | -3.70pp | -0.52pp | -0.44pp | 0.0% |
| 89 SPY / 1 SSO / 4 UPRO / 3 ZROZ / 3 GLD | quarterly | 5y | -55.13% | -55.14% | -3.70pp | -0.48pp | -2.12pp | 0.0% |
| 89 SPY / 1 SSO / 4 UPRO / 3 ZROZ / 3 GLD | quarterly | 10y | -55.13% | -55.14% | -3.58pp | -0.48pp | +0.44pp | 0.0% |
| 89 SPY / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 3y | -54.00% | -55.14% | -3.80pp | -0.13pp | -0.09pp | 0.0% |
| 89 SPY / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 5y | -54.00% | -55.14% | -3.80pp | +0.18pp | -2.06pp | 0.0% |
| 89 SPY / 4 UPRO / 4 ZROZ / 3 GLD | quarterly | 10y | -54.00% | -55.14% | -2.87pp | +0.34pp | +1.25pp | 0.0% |

## Phase 1b Verdict

| Question | Verdict |
|---|---|
| Did finer 1% weights preserve preferred 10y+ candidates? | Yes. |
| Did Phase 1b solve strict 5y+ 90% hit with no worse MDD than SPY? | No. |
| Did any stressed row pass preferred at 10 bps/year drag? | Yes. |
| Did any stressed row pass preferred at 25 bps/year drag? | No. |
| Did any stressed row pass preferred at 50 bps/year drag? | No. |
| Is this deployment-ready? | No. It remains research-only under maintenance mode. |

Recommended next step: if the user still wants a near-always SPY replacement, move to Phase 2 low-turnover tactical/LRS overlay; otherwise keep the static result as a simple 10y+ near-miss reference.
