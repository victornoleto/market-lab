# Sweep de redução de drawdown — `us_stocks` `from_2000`

Research-only, `promotion_eligible=false`. After-tax (BR 15%), bruto de custos, benchmark SPY. Alavancas: SPY SMA200 (Clenow/Gayed) e vol-targeting (escala a exposição pela vol da carteira, só de-risk, lag anti-look-ahead) `[systematic_trading, p.137-148]`, `[advances_fin_ml, p.31-34]`, `[stocks_on_the_move, p.66-67]`, `[leverage_for_the_long_run, p.9, p.13, p.16]`. Vol-targeting é aplicado sobre a série after-tax (aproximação de diagnóstico).

## `clenow_trend_lb1_3_6_12_top10_reb1`
Baseline MDD `-58.94%` / CAGR `47.49%`. Melhor MDD full: **vol-target 15%** -> `-25.15%` (CAGR `17.62%`, Sharpe `1.100`, Calmar `0.701`).

### Alavancas (overlay sobre o mesmo pick, ordenado por MDD full)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| vol-target 15% | 17.62% | -25.15% | -23.68% | -17.13% | 15.90% | 1.100 | 0.701 |
| vol-target 20% | 23.47% | -32.63% | -30.53% | -22.29% | 21.21% | 1.100 | 0.719 |
| vol-target 25% | 29.06% | -39.57% | -36.93% | -27.20% | 26.44% | 1.097 | 0.734 |
| SMA200: market_sma200_daily_stock_sma100 | 34.08% | -43.99% | -26.41% | -4.80% | 35.12% | 1.010 | 0.775 |
| SMA200: market_sma200_monthly | 39.37% | -45.59% | -17.57% | -5.50% | 36.84% | 1.084 | 0.863 |
| SMA200: market_sma200_daily | 36.01% | -45.59% | -26.33% | -4.84% | 35.99% | 1.034 | 0.790 |
| SMA200: market_sma200_monthly_stock_sma100 | 37.38% | -45.79% | -17.72% | -5.50% | 36.02% | 1.061 | 0.816 |
| baseline (sem overlay) | 47.49% | -58.94% | -58.94% | -33.69% | 42.42% | 1.128 | 0.806 |
| SMA200: stock_sma100 | 43.05% | -66.65% | -66.65% | -31.31% | 41.30% | 1.073 | 0.646 |

### Referência: estratégias alternativas (do broad_results)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| low-vol composite (top10) | 9.84% | -39.80% | -33.35% | -15.36% | 17.53% | 0.624 | 0.247 |
| peso inverse-vol (clenow_trend) | 40.90% | -59.85% | -59.01% | -32.73% | 40.54% | 1.049 | 0.683 |
| diversificação top3 | 50.79% | -76.18% | -57.38% | -50.47% | 66.13% | 0.940 | 0.667 |
| diversificação top5 | 54.50% | -63.08% | -54.35% | -44.12% | 55.03% | 1.060 | 0.864 |
| diversificação top10 | 47.49% | -58.94% | -58.94% | -33.69% | 42.42% | 1.128 | 0.806 |

Plots das variantes do headline em `plots/drawdown_sweep/` (baseline, SMA200 mensal, vol-target 15%).

## `clenow_trend_lb1_3_6_12_top5_reb1`
Baseline MDD `-63.08%` / CAGR `54.50%`. Melhor MDD full: **vol-target 15%** -> `-27.83%` (CAGR `16.77%`, Sharpe `1.037`, Calmar `0.603`).

### Alavancas (overlay sobre o mesmo pick, ordenado por MDD full)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| vol-target 15% | 16.77% | -27.83% | -15.63% | -17.66% | 16.22% | 1.037 | 0.603 |
| vol-target 20% | 22.26% | -35.90% | -20.83% | -22.94% | 21.63% | 1.037 | 0.620 |
| vol-target 25% | 27.64% | -43.36% | -25.98% | -27.95% | 27.03% | 1.037 | 0.637 |
| SMA200: market_sma200_monthly | 43.20% | -54.44% | -21.52% | -6.48% | 48.67% | 0.974 | 0.794 |
| SMA200: market_sma200_daily | 39.51% | -58.86% | -26.85% | -8.08% | 47.66% | 0.930 | 0.671 |
| SMA200: market_sma200_daily_stock_sma100 | 35.65% | -61.04% | -27.02% | -7.42% | 47.20% | 0.875 | 0.584 |
| SMA200: market_sma200_monthly_stock_sma100 | 39.73% | -62.69% | -21.52% | -6.48% | 48.25% | 0.928 | 0.634 |
| baseline (sem overlay) | 54.50% | -63.08% | -54.35% | -44.12% | 55.03% | 1.060 | 0.864 |
| SMA200: stock_sma100 | 48.25% | -70.54% | -68.79% | -43.47% | 54.23% | 0.991 | 0.684 |

### Referência: estratégias alternativas (do broad_results)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| low-vol composite (top5) | 9.54% | -43.05% | -41.93% | -15.11% | 18.66% | 0.582 | 0.222 |
| peso inverse-vol (clenow_trend) | 44.53% | -62.10% | -58.24% | -44.16% | 52.92% | 0.959 | 0.717 |
| diversificação top3 | 50.79% | -76.18% | -57.38% | -50.47% | 66.13% | 0.940 | 0.667 |
| diversificação top5 | 54.50% | -63.08% | -54.35% | -44.12% | 55.03% | 1.060 | 0.864 |
| diversificação top10 | 47.49% | -58.94% | -58.94% | -33.69% | 42.42% | 1.128 | 0.806 |

## `raw_13612_lb6_top5_reb6`
Baseline MDD `-66.81%` / CAGR `68.70%`. Melhor MDD full: **vol-target 15%** -> `-25.98%` (CAGR `19.27%`, Sharpe `1.027`, Calmar `0.742`).

### Alavancas (overlay sobre o mesmo pick, ordenado por MDD full)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| vol-target 15% | 19.27% | -25.98% | -20.94% | -19.95% | 18.79% | 1.027 | 0.742 |
| vol-target 20% | 25.61% | -33.79% | -27.28% | -25.80% | 25.05% | 1.027 | 0.758 |
| vol-target 25% | 31.77% | -41.11% | -33.30% | -31.29% | 31.29% | 1.025 | 0.773 |
| SMA200: market_sma200_monthly | 62.27% | -64.77% | -31.54% | n/a | 103.77% | 0.726 | 0.961 |
| SMA200: stock_sma100 | 65.17% | -64.90% | -63.66% | -39.67% | 101.13% | 0.766 | 1.004 |
| baseline (sem overlay) | 68.70% | -66.81% | -66.81% | -36.41% | 101.31% | 0.787 | 1.028 |
| SMA200: market_sma200_monthly_stock_sma100 | 57.62% | -67.60% | -31.54% | n/a | 103.60% | 0.697 | 0.852 |
| SMA200: market_sma200_daily_stock_sma100 | 51.26% | -72.28% | -26.89% | -5.21% | 98.27% | 0.656 | 0.709 |
| SMA200: market_sma200_daily | 55.87% | -74.27% | -27.26% | -5.21% | 98.35% | 0.687 | 0.752 |

### Referência: estratégias alternativas (do broad_results)
| Variante | CAGR | MDD full | GFC MDD | Dotcom MDD | Vol | Sharpe | Calmar |
|---|---|---|---|---|---|---|---|
| low-vol composite (top5) | 12.97% | -56.01% | -42.00% | -24.87% | 19.33% | 0.728 | 0.232 |
| peso inverse-vol (raw_13612) | 49.64% | -76.50% | -76.50% | -34.57% | 58.73% | 0.959 | 0.649 |
| diversificação top3 | 64.11% | -77.74% | -77.74% | -54.43% | 158.22% | 0.625 | 0.825 |
| diversificação top5 | 68.70% | -66.81% | -66.81% | -36.41% | 101.31% | 0.787 | 1.028 |
| diversificação top10 | 50.95% | -68.21% | -68.21% | -34.31% | 60.64% | 0.907 | 0.747 |
