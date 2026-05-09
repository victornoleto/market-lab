# Winner Deep Dive 03 — QLD Vote-K2 SMA Buffer 5% + ZROZ

## Resumo Executivo

Esta e a melhor variante anti-whipsaw do threshold sweep: `t3d_k2_smabuf_5pct`. Na janela comum contra os dois benchmarks obrigatorios, ela entrega CAGR de **27.56%**, Sortino **1.152** e MDD **-70.02%**. O SPY buy-and-hold fica em CAGR **11.35%** / Sortino **0.884**, enquanto o Plano C B4 original fica em CAGR **14.62%** / Sortino **1.464**.

Nota de leitura: as metricas deste relatorio sao recalculadas na janela comum contra B4 (`1988-2026`). Elas podem divergir dos numeros do `STUDY_FINAL_REPORT.md`, que por vezes usa `lh_56y` completo ou janelas especificas por sub-estudo.

A leitura honesta: a estrategia domina SPY em acumulacao de riqueza e tem forte comportamento em varias janelas, mas e muito mais agressiva que o Plano C B4. O B4 e o benchmark correto de alocacao real porque e a carteira passiva ativa do mandato; esta estrategia continua sendo pesquisa de Plano B, sem autorizacao de deploy.

## Definicao Operacional

- Familia: T3d Vote-K=2 com buffer simetrico de 5% nas SMAs para reduzir whipsaw.
- Risk-on: `QLD`.
- Risk-off: `ZROZ`.
- Sinal: Vote-of-K com `K=2` sobre quatro sinais diarios.
- Sinal 1: preco do QQQ/NDX acima da SMA200.
- Sinal 2: preco do QQQ/NDX acima da SMA50.
- Sinal 3: volatilidade realizada de 21 dias abaixo de 40% anualizado.
- Sinal 4: AR(1) de 30 dias acima de 0.
- Buffer: sinal de SMA exige margem simetrica de 5% para reduzir whipsaw.
- Regra ON: ficar 100% `QLD` quando pelo menos 2 dos 4 sinais estao ON.
- Regra OFF: ficar 100% `ZROZ` caso contrario.

O uso de Sortino como metrica primaria e adequado porque LETF rotation busca capturar upside convexo e nao deve penalizar volatilidade positiva simetricamente como Sharpe `[advances_fin_ml, p.275]`. A familia SMA/LETF vem da tese de trend-following aplicada a leveraged ETFs `[leverage_for_the_long_run, p.5-6, p.16]`. ZROZ como OFF asset preserva a convexidade defensiva de duration longa, com ressalva de choque de juros como 2022 `[leverage_for_the_long_run, p.21]`.

## Benchmark Set

- `SPY buy&hold`: `SPYSIM`, comprado e mantido.
- `Plano C B4 original`: 25% `NTSXSIM`, 25% `GDESIM`, 25% `RSSTSIM`, 25% `ZROZSIM`.
- Janela comum: `1988-01-04` a `2026-04-17`.
- Capital inicial normalizado: `$10,000`.

O B4 e capital-efficient stacking: NTSX empilha equity + Treasuries, GDE empilha equity + ouro, RSST empilha equity + managed futures, e ZROZ adiciona duration convexa `[risk_parity, ch.5, p.10]`.

## Metricas Principais

| series | start | end | years | cagr | mdd | sharpe | sortino | calmar | vol_ann | final_equity |
|---|---|---|---|---|---|---|---|---|---|---|
| Strategy | 1988-01-04 | 2026-04-17 | 38.3 | 27.56% | -70.02% | 0.852 | 1.152 | 0.394 | 36.72% | $119,358,729 |
| SPY buy&hold | 1988-01-04 | 2026-04-17 | 38.3 | 11.35% | -55.14% | 0.691 | 0.884 | 0.206 | 18.06% | $635,573 |
| Plano C B4 original | 1988-01-04 | 2026-04-17 | 38.3 | 14.62% | -28.38% | 1.027 | 1.464 | 0.515 | 14.35% | $1,889,198 |

## Equity E Relativo Aos Benchmarks

![Equity vs SPY e B4](plots/03_t3d_k2_smabuf_5pct_equity_vs_spy_b4.png)

![Relativo vs SPY e B4](plots/03_t3d_k2_smabuf_5pct_relative_to_spy_b4.png)

![Drawdown vs SPY e B4](plots/03_t3d_k2_smabuf_5pct_drawdown_vs_spy_b4.png)

Interpretacao: a estrategia tem compounding muito superior ao SPY, mas a comparacao contra B4 e mais exigente. O B4 reduz drawdown por diversificacao estrutural; a estrategia aceita drawdown LETF severo em troca de maior convexidade de retorno.

## Rolling Windows

![Rolling CAGR](plots/03_t3d_k2_smabuf_5pct_rolling_cagr.png)

![Rolling relative equity](plots/03_t3d_k2_smabuf_5pct_rolling_relative_equity_vs_spy_b4.png)

![Rolling pct days above benchmark](plots/03_t3d_k2_smabuf_5pct_rolling_pct_days_above_benchmark.png)

![Rolling win-rate](plots/03_t3d_k2_smabuf_5pct_rolling_winrate_vs_spy_b4.png)

| window_years | n_windows | median_sharpe | p10_sharpe | p90_sharpe | median_cagr | p10_cagr | p90_cagr | winrate_sharpe_vs_spy | winrate_sharpe_vs_b4 | winrate_cagr_vs_spy | winrate_cagr_vs_b4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 8890 | 0.881 | 0.421 | 1.404 | 26.95% | 8.82% | 56.30% | 52.81% | 33.44% | 93.05% | 87.79% |
| 5 | 8386 | 0.854 | 0.531 | 1.286 | 26.32% | 13.12% | 52.93% | 63.71% | 22.28% | 95.79% | 93.75% |
| 10 | 7126 | 0.875 | 0.668 | 1.105 | 26.92% | 18.95% | 44.17% | 87.62% | 12.18% | 100.00% | 99.20% |
| 15 | 5866 | 0.862 | 0.716 | 0.946 | 26.51% | 21.73% | 36.19% | 97.43% | 3.32% | 100.00% | 100.00% |

Leitura: as janelas curtas mostram a variancia real do trade. Em horizontes maiores, o edge de compounding aparece com mais clareza, mas a comparacao contra B4 e deliberadamente dura: B4 e diversificado e menos dependente de um unico regime Nasdaq.

### Psicologia Da Equity Relativa

Esta tabela mede cada start date mensal como se o investidor tivesse começado ali e segurado por 3/5/10/15 anos. `pct_days_above_benchmark` responde quanto do caminho a estrategia ficou acima do benchmark. `min_relative_equity` responde quao ruim ficou quando ficou abaixo. `max_consecutive_days_below_benchmark` aproxima quanto tempo demorou para recuperar em termos relativos.

| benchmark | horizon_years | n_windows | median_pct_days_above_benchmark | p10_pct_days_above_benchmark | median_min_relative_equity | p10_min_relative_equity | median_max_consecutive_days_below_benchmark | p90_max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|---|---|
| B4 | 3 | 423 | 81.37% | 31.04% | 0.846 | 0.648 | 74 | 330 |
| B4 | 5 | 399 | 88.34% | 53.74% | 0.841 | 0.650 | 71 | 315 |
| B4 | 10 | 339 | 94.53% | 77.53% | 0.848 | 0.652 | 67 | 285 |
| B4 | 15 | 279 | 96.22% | 83.55% | 0.831 | 0.640 | 90 | 341 |
| SPY | 3 | 423 | 88.51% | 38.02% | 0.883 | 0.676 | 46 | 292 |
| SPY | 5 | 399 | 93.34% | 61.41% | 0.886 | 0.697 | 44 | 251 |
| SPY | 10 | 339 | 97.14% | 85.68% | 0.893 | 0.722 | 35 | 197 |
| SPY | 15 | 279 | 97.99% | 89.75% | 0.886 | 0.709 | 39 | 215 |

Piores janelas contra B4 por profundidade relativa:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 2000-02-29 | 2003-03-06 | 3 | 2.11% | 0.596 | 0.334 | 736 |
| 2000-02-29 | 2015-03-11 | 15 | 12.99% | 1.583 | 0.334 | 3011 |
| 2000-02-29 | 2010-03-09 | 10 | 0.63% | 0.745 | 0.334 | 2500 |
| 2000-02-29 | 2005-03-07 | 5 | 1.27% | 0.694 | 0.334 | 1240 |
| 2000-03-31 | 2003-04-08 | 3 | 0.00% | 0.590 | 0.347 | 756 |
| 2000-03-31 | 2005-04-08 | 5 | 0.00% | 0.694 | 0.347 | 1260 |
| 2000-03-31 | 2015-04-14 | 15 | 14.20% | 1.643 | 0.347 | 2191 |
| 2000-03-31 | 2010-04-12 | 10 | 0.28% | 0.814 | 0.347 | 2191 |
| 1999-12-31 | 2010-01-08 | 10 | 9.64% | 1.065 | 0.429 | 829 |
| 1999-12-31 | 2003-01-07 | 3 | 7.40% | 0.697 | 0.429 | 688 |

Janelas contra B4 com maior sequencia abaixo do benchmark:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 2000-02-29 | 2015-03-11 | 15 | 12.99% | 1.583 | 0.334 | 3011 |
| 2000-02-29 | 2010-03-09 | 10 | 0.63% | 0.745 | 0.334 | 2500 |
| 2000-03-31 | 2010-04-12 | 10 | 0.28% | 0.814 | 0.347 | 2191 |
| 2000-03-31 | 2015-04-14 | 15 | 14.20% | 1.643 | 0.347 | 2191 |
| 2000-03-31 | 2005-04-08 | 5 | 0.00% | 0.694 | 0.347 | 1260 |
| 2000-02-29 | 2005-03-07 | 5 | 1.27% | 0.694 | 0.334 | 1240 |
| 2020-08-31 | 2025-09-08 | 5 | 11.58% | 0.956 | 0.504 | 951 |
| 1999-12-31 | 2010-01-08 | 10 | 9.64% | 1.065 | 0.429 | 829 |
| 1999-12-31 | 2005-01-06 | 5 | 6.19% | 0.966 | 0.429 | 829 |
| 1999-12-31 | 2015-01-12 | 15 | 36.47% | 1.873 | 0.429 | 829 |

## Entry-Date Analysis

![Entry heatmap](plots/03_t3d_k2_smabuf_5pct_entry_date_forward_returns_heatmap.png)

Piores entradas contra B4, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 2000-02-29 | 2001-02-28 | 1 | -52.45% | 7.79% | -60.24% |
| 2000-01-31 | 2001-01-30 | 1 | -38.46% | 16.39% | -54.85% |
| 1999-12-31 | 2000-12-29 | 1 | -42.01% | 10.52% | -52.53% |
| 2000-03-31 | 2001-04-02 | 1 | -55.29% | -3.74% | -51.55% |
| 1989-09-29 | 1990-09-28 | 1 | -39.66% | 0.22% | -39.88% |
| 2018-09-28 | 2019-10-01 | 1 | -17.79% | 17.81% | -35.61% |
| 2000-05-31 | 2001-05-31 | 1 | -30.61% | 4.82% | -35.43% |
| 2007-06-29 | 2008-06-30 | 1 | -21.46% | 13.37% | -34.83% |
| 2021-11-30 | 2022-11-30 | 1 | -47.03% | -13.78% | -33.25% |
| 2007-07-31 | 2008-07-30 | 1 | -22.71% | 10.14% | -32.86% |

Piores entradas contra SPY, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | spy_cagr | strategy_edge_vs_spy |
|---|---|---|---|---|---|
| 2009-02-27 | 2010-03-01 | 1 | 9.45% | 55.01% | -45.56% |
| 2000-02-29 | 2001-02-28 | 1 | -52.45% | -8.77% | -43.68% |
| 2000-01-31 | 2001-01-30 | 1 | -38.46% | -0.12% | -38.34% |
| 2021-11-30 | 2022-11-30 | 1 | -47.03% | -9.07% | -37.97% |
| 2022-02-28 | 2023-03-01 | 1 | -45.70% | -8.04% | -37.67% |
| 2021-10-29 | 2022-10-31 | 1 | -50.04% | -14.55% | -35.49% |
| 2009-03-31 | 2010-03-31 | 1 | 16.72% | 50.22% | -33.50% |
| 1999-12-31 | 2000-12-29 | 1 | -42.01% | -9.64% | -32.37% |
| 2000-03-31 | 2001-04-02 | 1 | -55.29% | -23.16% | -32.13% |
| 2022-01-31 | 2023-02-01 | 1 | -39.22% | -7.12% | -32.10% |

Melhores entradas contra B4:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 1998-01-30 | 1999-02-01 | 1 | 257.32% | 40.05% | 217.26% |
| 1999-03-31 | 2000-03-29 | 1 | 139.30% | 10.09% | 129.20% |
| 1997-12-31 | 1998-12-31 | 1 | 169.56% | 41.30% | 128.26% |
| 1990-12-31 | 1991-12-30 | 1 | 136.39% | 25.51% | 110.88% |
| 1997-03-31 | 2000-03-28 | 3 | 135.24% | 25.34% | 109.90% |
| 1996-01-31 | 1997-01-29 | 1 | 121.49% | 12.11% | 109.38% |
| 1997-04-30 | 1998-04-30 | 1 | 152.74% | 43.95% | 108.79% |
| 1996-01-31 | 1999-01-29 | 3 | 135.73% | 27.70% | 108.03% |
| 1998-02-27 | 1999-03-01 | 1 | 133.36% | 27.96% | 105.40% |
| 1990-09-28 | 1991-09-27 | 1 | 129.49% | 24.25% | 105.23% |

## Crises E Regimes

![Crise relativa](plots/03_t3d_k2_smabuf_5pct_crisis_relative_equity.png)

| crisis | start | end | Strategy_return | Strategy_mdd | SPY buy&hold_return | SPY buy&hold_mdd | Plano C B4 original_return | Plano C B4 original_mdd |
|---|---|---|---|---|---|---|---|---|
| dotcom | 2000-03-24 | 2002-10-09 | -50.68% | -70.02% | -47.38% | -47.38% | -17.88% | -28.38% |
| gfc | 2007-10-09 | 2009-03-09 | -9.14% | -41.50% | -55.14% | -55.14% | -17.05% | -27.66% |
| covid | 2020-02-19 | 2020-06-30 | 16.99% | -29.27% | -7.86% | -33.69% | 5.93% | -19.25% |
| rates_2022 | 2021-12-27 | 2022-12-30 | -51.57% | -56.61% | -18.49% | -24.44% | -20.31% | -24.21% |

O ponto estrutural continua sendo 2000: a troca de SMA200/50 para SMA250/100 reduziu o dano do dotcom versus a canonica, porque o filtro longo sai antes da parte mais destrutiva da bolha. Em 2022, ZROZ deixa de ser hedge perfeito porque duration longa tambem sofre com alta de juros.

## Comportamento ON/OFF

| metric | value |
|---|---|
| pct_days_on_qld | 0.734 |
| pct_days_off_zroz | 0.266 |
| switch_count | 262.000 |
| avg_qld_weight | 0.734 |
| avg_zroz_weight | 0.266 |
| avg_on_run_days | 53.598 |
| avg_off_run_days | 19.618 |

O numero de switches e a duracao media de regimes ajudam a separar duas coisas: edge de sinal e friccao operacional. Quanto mais trocas, maior o risco de imposto per-swing e slippage; por isso os estudos posteriores de buffer/histerese continuam relevantes `[systematic_trading, Carver p.122-133]`.

## Limitacoes E Veredito

- Este relatorio e gross-first; nao e autorizacao de deploy.
- A comparacao principal e limitada pela janela comum com B4, que comeca em 1988 por causa do historico efetivo dos sleeves do B4.
- QLD/NDX e uma aposta concentrada em Nasdaq; o estudo mostrou que o mesmo Vote-K nao generaliza bem para UPRO/SPX.
- MDD permanece warning-only no mandato, mas drawdowns de LETF continuam psicologicamente e operacionalmente relevantes.
- Capital segue 100% Plano C; Strategy B permanece DORMANT.

Veredito: variante interessante para reduzir whipsaw e friccao, especialmente se imposto/slippage forem centrais, mas ainda precisa revalidacao completa antes de qualquer consideracao operacional.

## Artefatos Gerados

- `data/03_t3d_k2_smabuf_5pct_daily_series.csv`
- `data/03_t3d_k2_smabuf_5pct_summary_metrics.csv`
- `data/03_t3d_k2_smabuf_5pct_rolling_summary.csv`
- `data/03_t3d_k2_smabuf_5pct_rolling_relative_windows.csv`
- `data/03_t3d_k2_smabuf_5pct_entry_forward_returns.csv`
- `data/03_t3d_k2_smabuf_5pct_crisis_windows.csv`
- `data/03_t3d_k2_smabuf_5pct_regime_stats.csv`
- `plots/03_t3d_k2_smabuf_5pct_equity_vs_spy_b4.png`
- `plots/03_t3d_k2_smabuf_5pct_relative_to_spy_b4.png`
- `plots/03_t3d_k2_smabuf_5pct_drawdown_vs_spy_b4.png`
- `plots/03_t3d_k2_smabuf_5pct_rolling_cagr.png`
- `plots/03_t3d_k2_smabuf_5pct_rolling_relative_equity_vs_spy_b4.png`
- `plots/03_t3d_k2_smabuf_5pct_rolling_pct_days_above_benchmark.png`
- `plots/03_t3d_k2_smabuf_5pct_rolling_winrate_vs_spy_b4.png`
- `plots/03_t3d_k2_smabuf_5pct_entry_date_forward_returns_heatmap.png`
- `plots/03_t3d_k2_smabuf_5pct_crisis_relative_equity.png`
