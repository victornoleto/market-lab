# Sweep de redução de drawdown — `us_stocks` `from_1990`

Research-only, `promotion_eligible=false`. After-tax (BR 15%), bruto de custos, benchmark SPY. Alavancas: SPY SMA200 (Clenow/Gayed) e vol-targeting (escala a exposição pela vol da carteira, só de-risk, lag anti-look-ahead) `[systematic_trading, p.137-148]`, `[advances_fin_ml, p.31-34]`, `[stocks_on_the_move, p.66-67]`, `[leverage_for_the_long_run, p.9, p.13, p.16]`. Vol-targeting é aplicado sobre a série after-tax (aproximação de diagnóstico).

## `clenow_trend_lb1_3_6_12_top10_reb1`
Baseline MDD `-63.00%` / CAGR `51.13%`. Melhor MDD full: **vol-target 15%** -> `-25.15%` (CAGR `20.93%`, Sharpe `1.268`, Calmar `0.832`).

### Alavancas (overlay sobre o mesmo pick, ordenado por MDD full)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| vol-target 15% | 20.93% | -25.15% | -23.68% | -17.13% | 16.00% | 1.268 | 0.832 |
| vol-target 20% | 27.86% | -32.63% | -30.53% | -22.55% | 21.27% | 1.262 | 0.854 |
| vol-target 25% | 33.97% | -39.57% | -36.93% | -27.85% | 26.31% | 1.244 | 0.858 |
| baseline (sem overlay) | 51.13% | -63.00% | -58.94% | -63.00% | 41.60% | 1.201 | 0.812 |
| SMA200: market_sma200_monthly | 40.85% | -63.00% | -17.57% | -63.00% | 36.20% | 1.127 | 0.648 |
| SMA200: market_sma200_daily | 38.13% | -63.00% | -26.33% | -63.00% | 35.65% | 1.084 | 0.605 |
| SMA200: market_sma200_monthly_stock_sma100 | 38.02% | -64.30% | -17.72% | -64.30% | 35.34% | 1.088 | 0.591 |
| SMA200: market_sma200_daily_stock_sma100 | 34.74% | -65.82% | -26.41% | -65.82% | 34.74% | 1.032 | 0.528 |
| SMA200: stock_sma100 | 45.57% | -66.65% | -66.65% | -64.30% | 40.48% | 1.130 | 0.684 |

### Referência: estratégias alternativas (do broad_results)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| low-vol composite (top10) | 12.37% | -39.80% | -33.35% | -16.03% | 22.66% | 0.610 | 0.311 |
| peso inverse-vol (clenow_trend) | 44.59% | -63.88% | -59.01% | -63.88% | 39.69% | 1.129 | 0.698 |
| diversificação top3 | 56.35% | -76.18% | -57.38% | -69.44% | 65.86% | 0.998 | 0.740 |
| diversificação top5 | 59.08% | -67.79% | -54.35% | -67.79% | 54.07% | 1.124 | 0.872 |
| diversificação top10 | 51.13% | -63.00% | -58.94% | -63.00% | 41.60% | 1.201 | 0.812 |

Plots das variantes do headline em `plots/drawdown_sweep/` (baseline, SMA200 mensal, vol-target 15%).

## `clenow_trend_lb1_3_6_12_top5_reb1`
Baseline MDD `-67.79%` / CAGR `59.08%`. Melhor MDD full: **vol-target 15%** -> `-27.83%` (CAGR `19.06%`, Sharpe `1.155`, Calmar `0.685`).

### Alavancas (overlay sobre o mesmo pick, ordenado por MDD full)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| vol-target 15% | 19.06% | -27.83% | -15.63% | -17.78% | 16.25% | 1.155 | 0.685 |
| vol-target 20% | 25.46% | -35.90% | -20.83% | -23.33% | 21.67% | 1.155 | 0.709 |
| vol-target 25% | 31.82% | -43.36% | -25.98% | -28.66% | 27.07% | 1.155 | 0.734 |
| SMA200: market_sma200_monthly | 46.22% | -65.64% | -21.52% | -65.64% | 47.58% | 1.031 | 0.704 |
| SMA200: market_sma200_daily | 43.31% | -65.88% | -26.85% | -65.88% | 46.96% | 0.996 | 0.657 |
| baseline (sem overlay) | 59.08% | -67.79% | -54.35% | -67.79% | 54.07% | 1.124 | 0.872 |
| SMA200: market_sma200_monthly_stock_sma100 | 41.00% | -68.76% | -21.52% | -68.76% | 46.61% | 0.965 | 0.596 |
| SMA200: market_sma200_daily_stock_sma100 | 36.89% | -68.76% | -27.02% | -68.76% | 45.91% | 0.909 | 0.537 |
| SMA200: stock_sma100 | 50.75% | -70.54% | -68.79% | -68.76% | 52.78% | 1.037 | 0.719 |

### Referência: estratégias alternativas (do broad_results)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| low-vol composite (top5) | 9.91% | -43.05% | -41.93% | -15.11% | 18.03% | 0.615 | 0.230 |
| peso inverse-vol (clenow_trend) | 49.02% | -70.09% | -58.24% | -70.09% | 51.67% | 1.030 | 0.699 |
| diversificação top3 | 56.35% | -76.18% | -57.38% | -69.44% | 65.86% | 0.998 | 0.740 |
| diversificação top5 | 59.08% | -67.79% | -54.35% | -67.79% | 54.07% | 1.124 | 0.872 |
| diversificação top10 | 51.13% | -63.00% | -58.94% | -63.00% | 41.60% | 1.201 | 0.812 |

## `raw_13612_lb6_top5_reb6`
Baseline MDD `-71.27%` / CAGR `62.36%`. Melhor MDD full: **vol-target 15%** -> `-25.98%` (CAGR `19.09%`, Sharpe `1.038`, Calmar `0.735`).

### Alavancas (overlay sobre o mesmo pick, ordenado por MDD full)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| vol-target 15% | 19.09% | -25.98% | -20.94% | -19.95% | 18.37% | 1.038 | 0.735 |
| vol-target 20% | 25.38% | -33.79% | -27.28% | -25.80% | 24.49% | 1.038 | 0.751 |
| vol-target 25% | 31.50% | -41.11% | -33.30% | -31.29% | 30.58% | 1.037 | 0.766 |
| SMA200: stock_sma100 | 59.35% | -71.27% | -63.66% | -71.27% | 92.42% | 0.766 | 0.833 |
| baseline (sem overlay) | 62.36% | -71.27% | -66.81% | -71.27% | 92.63% | 0.787 | 0.875 |
| SMA200: market_sma200_monthly | 51.45% | -71.27% | -31.54% | -71.27% | 90.96% | 0.702 | 0.722 |
| SMA200: market_sma200_monthly_stock_sma100 | 48.02% | -71.27% | -31.54% | -71.27% | 90.77% | 0.676 | 0.674 |
| SMA200: market_sma200_daily_stock_sma100 | 46.16% | -72.28% | -26.89% | -72.19% | 88.35% | 0.658 | 0.639 |
| SMA200: market_sma200_daily | 49.86% | -74.27% | -27.26% | -72.19% | 88.47% | 0.686 | 0.671 |

### Referência: estratégias alternativas (do broad_results)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| low-vol composite (top5) | 16.34% | -56.01% | -42.00% | -24.87% | 35.85% | 0.534 | 0.292 |
| peso inverse-vol (raw_13612) | 47.75% | -76.50% | -76.50% | -72.25% | 56.96% | 0.954 | 0.624 |
| diversificação top3 | 54.10% | -77.74% | -77.74% | -77.65% | 142.84% | 0.606 | 0.696 |
| diversificação top5 | 62.36% | -71.27% | -66.81% | -71.27% | 92.63% | 0.787 | 0.875 |
| diversificação top10 | 47.71% | -68.21% | -68.21% | -62.28% | 56.57% | 0.910 | 0.700 |
