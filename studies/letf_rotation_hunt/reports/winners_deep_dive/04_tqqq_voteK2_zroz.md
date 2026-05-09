# Winner Deep Dive 04 — TQQQ Vote-K2 + ZROZ

## Resumo Executivo

Esta e a alternativa agressiva nao-QLD com maior CAGR e risco maior: `tqqq_voteK2_off_zroz`. Na janela comum contra os dois benchmarks obrigatorios, ela entrega CAGR de **28.15%**, Sortino **0.976** e MDD **-74.03%**. O SPY buy-and-hold fica em CAGR **11.35%** / Sortino **0.884**, enquanto o Plano C B4 original fica em CAGR **14.62%** / Sortino **1.464**.

Nota de leitura: as metricas deste relatorio sao recalculadas na janela comum contra B4 (`1988-2026`). Elas podem divergir dos numeros do `STUDY_FINAL_REPORT.md`, que por vezes usa `lh_56y` completo ou janelas especificas por sub-estudo.

A leitura honesta: a estrategia domina SPY em acumulacao de riqueza e tem forte comportamento em varias janelas, mas e muito mais agressiva que o Plano C B4. O B4 e o benchmark correto de alocacao real porque e a carteira passiva ativa do mandato; esta estrategia continua sendo pesquisa de Plano B, sem autorizacao de deploy.

## Definicao Operacional

- Familia: T3d Vote-K=2 aplicado a TQQQ 3x Nasdaq-100 com ZROZ como OFF.
- Risk-on: `TQQQ`.
- Risk-off: `ZROZ`.
- Sinal: Vote-of-K com `K=2` sobre quatro sinais diarios.
- Sinal 1: preco do QQQ/NDX acima da SMA200.
- Sinal 2: preco do QQQ/NDX acima da SMA50.
- Sinal 3: volatilidade realizada de 21 dias abaixo de 40% anualizado.
- Sinal 4: AR(1) de 30 dias acima de 0.
- Regra ON: ficar 100% `TQQQ` quando pelo menos 2 dos 4 sinais estao ON.
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
| Strategy | 1988-01-04 | 2026-04-17 | 38.3 | 28.15% | -74.03% | 0.760 | 0.976 | 0.380 | 48.80% | $147,200,235 |
| SPY buy&hold | 1988-01-04 | 2026-04-17 | 38.3 | 11.35% | -55.14% | 0.691 | 0.884 | 0.206 | 18.06% | $635,573 |
| Plano C B4 original | 1988-01-04 | 2026-04-17 | 38.3 | 14.62% | -28.38% | 1.027 | 1.464 | 0.515 | 14.35% | $1,889,198 |

## Equity E Relativo Aos Benchmarks

![Equity vs SPY e B4](plots/04_tqqq_voteK2_zroz_equity_vs_spy_b4.png)

![Relativo vs SPY e B4](plots/04_tqqq_voteK2_zroz_relative_to_spy_b4.png)

![Drawdown vs SPY e B4](plots/04_tqqq_voteK2_zroz_drawdown_vs_spy_b4.png)

Interpretacao: a estrategia tem compounding muito superior ao SPY, mas a comparacao contra B4 e mais exigente. O B4 reduz drawdown por diversificacao estrutural; a estrategia aceita drawdown LETF severo em troca de maior convexidade de retorno.

## Rolling Windows

![Rolling CAGR](plots/04_tqqq_voteK2_zroz_rolling_cagr.png)

![Rolling relative equity](plots/04_tqqq_voteK2_zroz_rolling_relative_equity_vs_spy_b4.png)

![Rolling pct days above benchmark](plots/04_tqqq_voteK2_zroz_rolling_pct_days_above_benchmark.png)

![Rolling win-rate](plots/04_tqqq_voteK2_zroz_rolling_winrate_vs_spy_b4.png)

| window_years | n_windows | median_sharpe | p10_sharpe | p90_sharpe | median_cagr | p10_cagr | p90_cagr | winrate_sharpe_vs_spy | winrate_sharpe_vs_b4 | winrate_cagr_vs_spy | winrate_cagr_vs_b4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 8890 | 0.808 | 0.109 | 1.330 | 28.99% | -4.87% | 70.38% | 51.61% | 21.84% | 75.35% | 69.27% |
| 5 | 8386 | 0.751 | 0.316 | 1.184 | 27.01% | 3.63% | 62.32% | 52.72% | 18.30% | 83.83% | 73.83% |
| 10 | 7126 | 0.783 | 0.496 | 1.091 | 29.59% | 12.82% | 44.75% | 73.88% | 6.02% | 98.95% | 92.08% |
| 15 | 5866 | 0.736 | 0.610 | 0.950 | 27.26% | 19.95% | 36.62% | 86.87% | 2.51% | 100.00% | 100.00% |

Leitura: as janelas curtas mostram a variancia real do trade. Em horizontes maiores, o edge de compounding aparece com mais clareza, mas a comparacao contra B4 e deliberadamente dura: B4 e diversificado e menos dependente de um unico regime Nasdaq.

### Psicologia Da Equity Relativa

Esta tabela mede cada start date mensal como se o investidor tivesse começado ali e segurado por 3/5/10/15 anos. `pct_days_above_benchmark` responde quanto do caminho a estrategia ficou acima do benchmark. `min_relative_equity` responde quao ruim ficou quando ficou abaixo. `max_consecutive_days_below_benchmark` aproxima quanto tempo demorou para recuperar em termos relativos.

| benchmark | horizon_years | n_windows | median_pct_days_above_benchmark | p10_pct_days_above_benchmark | median_min_relative_equity | p10_min_relative_equity | median_max_consecutive_days_below_benchmark | p90_max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|---|---|
| B4 | 3 | 423 | 73.45% | 7.93% | 0.760 | 0.462 | 114 | 573 |
| B4 | 5 | 399 | 80.02% | 10.55% | 0.740 | 0.399 | 128 | 918 |
| B4 | 10 | 339 | 81.32% | 38.06% | 0.663 | 0.363 | 225 | 1384 |
| B4 | 15 | 279 | 81.30% | 54.31% | 0.577 | 0.356 | 313 | 1431 |
| SPY | 3 | 423 | 79.66% | 11.52% | 0.792 | 0.476 | 91 | 500 |
| SPY | 5 | 399 | 84.93% | 16.05% | 0.768 | 0.457 | 102 | 601 |
| SPY | 10 | 339 | 90.64% | 52.87% | 0.749 | 0.455 | 116 | 601 |
| SPY | 15 | 279 | 92.09% | 66.51% | 0.715 | 0.435 | 138 | 972 |

Piores janelas contra B4 por profundidade relativa:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 1999-12-31 | 2015-01-12 | 15 | 9.68% | 1.562 | 0.178 | 3356 |
| 1999-12-31 | 2010-01-08 | 10 | 0.16% | 0.293 | 0.178 | 2461 |
| 2000-02-29 | 2010-03-09 | 10 | 0.63% | 0.328 | 0.210 | 2500 |
| 2000-02-29 | 2015-03-11 | 15 | 15.47% | 2.056 | 0.210 | 3007 |
| 2000-03-31 | 2015-04-14 | 15 | 17.35% | 2.168 | 0.222 | 2994 |
| 2000-03-31 | 2010-04-12 | 10 | 0.00% | 0.382 | 0.222 | 2520 |
| 2003-07-31 | 2008-08-01 | 5 | 1.03% | 0.293 | 0.271 | 1223 |
| 2003-07-31 | 2013-08-05 | 10 | 19.28% | 1.598 | 0.271 | 1835 |
| 2003-07-31 | 2018-08-06 | 15 | 46.18% | 5.025 | 0.271 | 1835 |
| 2003-08-29 | 2018-09-05 | 15 | 47.66% | 5.226 | 0.278 | 1802 |

Janelas contra B4 com maior sequencia abaixo do benchmark:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 1999-12-31 | 2015-01-12 | 15 | 9.68% | 1.562 | 0.178 | 3356 |
| 2000-02-29 | 2015-03-11 | 15 | 15.47% | 2.056 | 0.210 | 3007 |
| 2000-03-31 | 2015-04-14 | 15 | 17.35% | 2.168 | 0.222 | 2994 |
| 2000-03-31 | 2010-04-12 | 10 | 0.00% | 0.382 | 0.222 | 2520 |
| 2000-02-29 | 2010-03-09 | 10 | 0.63% | 0.328 | 0.210 | 2500 |
| 1999-12-31 | 2010-01-08 | 10 | 0.16% | 0.293 | 0.178 | 2461 |
| 2003-07-31 | 2018-08-06 | 15 | 46.18% | 5.025 | 0.271 | 1835 |
| 2003-07-31 | 2013-08-05 | 10 | 19.28% | 1.598 | 0.271 | 1835 |
| 2003-08-29 | 2018-09-05 | 15 | 47.66% | 5.226 | 0.278 | 1802 |
| 2003-08-29 | 2013-09-04 | 10 | 21.50% | 1.623 | 0.278 | 1802 |

## Entry-Date Analysis

![Entry heatmap](plots/04_tqqq_voteK2_zroz_entry_date_forward_returns_heatmap.png)

Piores entradas contra B4, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 2007-06-29 | 2008-06-30 | 1 | -45.15% | 13.37% | -58.52% |
| 1999-12-31 | 2000-12-29 | 1 | -46.20% | 10.52% | -56.72% |
| 2007-07-31 | 2008-07-30 | 1 | -45.43% | 10.14% | -55.57% |
| 1994-01-31 | 1995-01-31 | 1 | -50.87% | -2.16% | -48.71% |
| 2022-02-28 | 2023-03-01 | 1 | -61.88% | -13.34% | -48.54% |
| 2007-05-31 | 2008-05-30 | 1 | -34.36% | 14.09% | -48.45% |
| 1992-11-30 | 1993-11-29 | 1 | -19.88% | 27.80% | -47.69% |
| 1992-12-31 | 1993-12-30 | 1 | -17.17% | 29.30% | -46.47% |
| 2021-11-30 | 2022-11-30 | 1 | -59.16% | -13.78% | -45.37% |
| 1993-03-31 | 1994-03-29 | 1 | -35.40% | 8.86% | -44.26% |

Piores entradas contra SPY, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | spy_cagr | strategy_edge_vs_spy |
|---|---|---|---|---|---|
| 2022-02-28 | 2023-03-01 | 1 | -61.88% | -8.04% | -53.84% |
| 1994-01-31 | 1995-01-31 | 1 | -50.87% | 0.37% | -51.24% |
| 2021-11-30 | 2022-11-30 | 1 | -59.16% | -9.07% | -50.09% |
| 2021-10-29 | 2022-10-31 | 1 | -60.90% | -14.55% | -46.35% |
| 1993-12-31 | 1994-12-30 | 1 | -45.07% | 0.50% | -45.57% |
| 2022-01-31 | 2023-02-01 | 1 | -50.86% | -7.12% | -43.74% |
| 2021-12-31 | 2023-01-03 | 1 | -58.53% | -18.44% | -40.09% |
| 1994-02-28 | 1995-02-28 | 1 | -31.42% | 7.61% | -39.03% |
| 1993-05-28 | 1994-05-27 | 1 | -34.30% | 4.14% | -38.45% |
| 2005-05-31 | 2006-05-31 | 1 | -29.31% | 8.71% | -38.02% |

Melhores entradas contra B4:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 1998-01-30 | 1999-02-01 | 1 | 373.69% | 40.05% | 333.64% |
| 2010-02-26 | 2011-02-25 | 1 | 230.76% | 26.92% | 203.84% |
| 2010-01-29 | 2011-01-28 | 1 | 211.42% | 25.40% | 186.02% |
| 1990-08-31 | 1991-08-30 | 1 | 206.43% | 24.80% | 181.63% |
| 1997-12-31 | 1998-12-31 | 1 | 219.86% | 41.30% | 178.56% |
| 1990-09-28 | 1991-09-27 | 1 | 192.31% | 24.25% | 168.06% |
| 1997-06-30 | 1998-06-30 | 1 | 205.07% | 38.00% | 167.08% |
| 1996-07-31 | 1997-07-30 | 1 | 210.28% | 44.82% | 165.46% |
| 1997-04-30 | 1998-04-30 | 1 | 200.55% | 43.95% | 156.60% |
| 2010-04-30 | 2011-04-29 | 1 | 180.85% | 25.93% | 154.92% |

## Crises E Regimes

![Crise relativa](plots/04_tqqq_voteK2_zroz_crisis_relative_equity.png)

| crisis | start | end | Strategy_return | Strategy_mdd | SPY buy&hold_return | SPY buy&hold_mdd | Plano C B4 original_return | Plano C B4 original_mdd |
|---|---|---|---|---|---|---|---|---|
| dotcom | 2000-03-24 | 2002-10-09 | -53.97% | -72.91% | -47.38% | -47.38% | -17.88% | -28.38% |
| gfc | 2007-10-09 | 2009-03-09 | -37.89% | -58.72% | -55.14% | -55.14% | -17.05% | -27.66% |
| covid | 2020-02-19 | 2020-06-30 | -2.59% | -38.70% | -7.86% | -33.69% | 5.93% | -19.25% |
| rates_2022 | 2021-12-27 | 2022-12-30 | -61.34% | -65.45% | -18.49% | -24.44% | -20.31% | -24.21% |

O ponto estrutural continua sendo 2000: a troca de SMA200/50 para SMA250/100 reduziu o dano do dotcom versus a canonica, porque o filtro longo sai antes da parte mais destrutiva da bolha. Em 2022, ZROZ deixa de ser hedge perfeito porque duration longa tambem sofre com alta de juros.

## Comportamento ON/OFF

| metric | value |
|---|---|
| pct_days_on_qld | 0.641 |
| pct_days_off_zroz | 0.359 |
| switch_count | 578.000 |
| avg_qld_weight | n/a |
| avg_zroz_weight | 0.359 |
| avg_on_run_days | 21.334 |
| avg_off_run_days | 11.965 |

O numero de switches e a duracao media de regimes ajudam a separar duas coisas: edge de sinal e friccao operacional. Quanto mais trocas, maior o risco de imposto per-swing e slippage; por isso os estudos posteriores de buffer/histerese continuam relevantes `[systematic_trading, Carver p.122-133]`.

## Limitacoes E Veredito

- Este relatorio e gross-first; nao e autorizacao de deploy.
- A comparacao principal e limitada pela janela comum com B4, que comeca em 1988 por causa do historico efetivo dos sleeves do B4.
- QLD/NDX e uma aposta concentrada em Nasdaq; o estudo mostrou que o mesmo Vote-K nao generaliza bem para UPRO/SPX.
- MDD permanece warning-only no mandato, mas drawdowns de LETF continuam psicologicamente e operacionalmente relevantes.
- Capital segue 100% Plano C; Strategy B permanece DORMANT.

Veredito: alternativa agressiva com maior potencial de CAGR e maior carga psicologica; util para comparacao, nao como substituta automatica da QLD winner.

## Artefatos Gerados

- `data/04_tqqq_voteK2_zroz_daily_series.csv`
- `data/04_tqqq_voteK2_zroz_summary_metrics.csv`
- `data/04_tqqq_voteK2_zroz_rolling_summary.csv`
- `data/04_tqqq_voteK2_zroz_rolling_relative_windows.csv`
- `data/04_tqqq_voteK2_zroz_entry_forward_returns.csv`
- `data/04_tqqq_voteK2_zroz_crisis_windows.csv`
- `data/04_tqqq_voteK2_zroz_regime_stats.csv`
- `plots/04_tqqq_voteK2_zroz_equity_vs_spy_b4.png`
- `plots/04_tqqq_voteK2_zroz_relative_to_spy_b4.png`
- `plots/04_tqqq_voteK2_zroz_drawdown_vs_spy_b4.png`
- `plots/04_tqqq_voteK2_zroz_rolling_cagr.png`
- `plots/04_tqqq_voteK2_zroz_rolling_relative_equity_vs_spy_b4.png`
- `plots/04_tqqq_voteK2_zroz_rolling_pct_days_above_benchmark.png`
- `plots/04_tqqq_voteK2_zroz_rolling_winrate_vs_spy_b4.png`
- `plots/04_tqqq_voteK2_zroz_entry_date_forward_returns_heatmap.png`
- `plots/04_tqqq_voteK2_zroz_crisis_relative_equity.png`
