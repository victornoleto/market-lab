# Winner Deep Dive 01 — QLD Vote-K2 SMA250/100 + ZROZ

## Resumo Executivo

Esta e a vencedora operacional Sortino-first do estudo LETF: `qld_voteK2_sma250_100_vol21_40_ar30_off_zroz`. Na janela comum contra os dois benchmarks obrigatorios, ela entrega CAGR de **28.10%**, Sortino **1.164** e MDD **-64.50%**. O SPY buy-and-hold fica em CAGR **11.35%** / Sortino **0.884**, enquanto o Plano C B4 original fica em CAGR **14.62%** / Sortino **1.464**.

Nota de leitura: o estudo final reportou Sortino **1.325** para esta estrategia no dataset `lh_56y` completo. Aqui, a metrica cai para **1.164** porque a comparacao principal e forçada para a intersecao com B4 (`1988-2026`). Isso evita comparar a estrategia em uma janela e o Plano C em outra.

A leitura honesta: a estrategia domina SPY em acumulacao de riqueza e tem forte comportamento em varias janelas, mas e muito mais agressiva que o Plano C B4. O B4 e o benchmark correto de alocacao real porque e a carteira passiva ativa do mandato; esta estrategia continua sendo pesquisa de Plano B, sem autorizacao de deploy.

## Definicao Operacional

- Familia: T3d Vote-K=2 com SMAs longas; melhor configuracao Sortino-first.
- Risk-on: `QLD`.
- Risk-off: `ZROZ`.
- Sinal: Vote-of-K com `K=2` sobre quatro sinais diarios.
- Sinal 1: preco do QQQ/NDX acima da SMA250.
- Sinal 2: preco do QQQ/NDX acima da SMA100.
- Sinal 3: volatilidade realizada de 21 dias abaixo de 40% anualizado.
- Sinal 4: AR(1) de 30 dias acima de 0.
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
| Strategy | 1988-01-04 | 2026-04-17 | 38.3 | 28.10% | -64.50% | 0.859 | 1.164 | 0.436 | 36.74% | $130,921,531 |
| SPY buy&hold | 1988-01-04 | 2026-04-17 | 38.3 | 11.35% | -55.14% | 0.691 | 0.884 | 0.206 | 18.06% | $635,573 |
| Plano C B4 original | 1988-01-04 | 2026-04-17 | 38.3 | 14.62% | -28.38% | 1.027 | 1.464 | 0.515 | 14.35% | $1,889,198 |

## Equity E Relativo Aos Benchmarks

![Equity vs SPY e B4](plots/01_qld_voteK2_sma250_100_zroz_equity_vs_spy_b4.png)

![Relativo vs SPY e B4](plots/01_qld_voteK2_sma250_100_zroz_relative_to_spy_b4.png)

![Drawdown vs SPY e B4](plots/01_qld_voteK2_sma250_100_zroz_drawdown_vs_spy_b4.png)

Interpretacao: a estrategia tem compounding muito superior ao SPY, mas a comparacao contra B4 e mais exigente. O B4 reduz drawdown por diversificacao estrutural; a estrategia aceita drawdown LETF severo em troca de maior convexidade de retorno.

## Rolling Windows

![Rolling CAGR](plots/01_qld_voteK2_sma250_100_zroz_rolling_cagr.png)

![Rolling relative equity](plots/01_qld_voteK2_sma250_100_zroz_rolling_relative_equity_vs_spy_b4.png)

![Rolling pct days above benchmark](plots/01_qld_voteK2_sma250_100_zroz_rolling_pct_days_above_benchmark.png)

![Rolling win-rate](plots/01_qld_voteK2_sma250_100_zroz_rolling_winrate_vs_spy_b4.png)

| window_years | n_windows | median_sharpe | p10_sharpe | p90_sharpe | median_cagr | p10_cagr | p90_cagr | winrate_sharpe_vs_spy | winrate_sharpe_vs_b4 | winrate_cagr_vs_spy | winrate_cagr_vs_b4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 8890 | 0.880 | 0.359 | 1.364 | 27.87% | 6.51% | 54.70% | 55.14% | 31.77% | 88.86% | 82.03% |
| 5 | 8386 | 0.873 | 0.478 | 1.248 | 27.90% | 11.12% | 53.96% | 61.83% | 24.86% | 96.30% | 86.73% |
| 10 | 7126 | 0.899 | 0.613 | 1.094 | 28.26% | 16.56% | 44.41% | 88.62% | 18.55% | 100.00% | 98.95% |
| 15 | 5866 | 0.846 | 0.738 | 0.953 | 27.30% | 21.43% | 35.82% | 99.15% | 2.34% | 100.00% | 100.00% |

Leitura: as janelas curtas mostram a variancia real do trade. Em horizontes maiores, o edge de compounding aparece com mais clareza, mas a comparacao contra B4 e deliberadamente dura: B4 e diversificado e menos dependente de um unico regime Nasdaq.

### Psicologia Da Equity Relativa

Esta tabela mede cada start date mensal como se o investidor tivesse começado ali e segurado por 3/5/10/15 anos. `pct_days_above_benchmark` responde quanto do caminho a estrategia ficou acima do benchmark. `min_relative_equity` responde quao ruim ficou quando ficou abaixo. `max_consecutive_days_below_benchmark` aproxima quanto tempo demorou para recuperar em termos relativos.

| benchmark | horizon_years | n_windows | median_pct_days_above_benchmark | p10_pct_days_above_benchmark | median_min_relative_equity | p10_min_relative_equity | median_max_consecutive_days_below_benchmark | p90_max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|---|---|
| B4 | 3 | 423 | 82.69% | 23.25% | 0.846 | 0.603 | 64 | 355 |
| B4 | 5 | 399 | 88.58% | 37.34% | 0.840 | 0.596 | 66 | 344 |
| B4 | 10 | 339 | 94.09% | 57.77% | 0.839 | 0.589 | 67 | 346 |
| B4 | 15 | 279 | 95.45% | 69.92% | 0.806 | 0.577 | 91 | 458 |
| SPY | 3 | 423 | 88.51% | 32.68% | 0.880 | 0.661 | 49 | 319 |
| SPY | 5 | 399 | 91.75% | 58.64% | 0.864 | 0.676 | 51 | 289 |
| SPY | 10 | 339 | 96.55% | 81.69% | 0.879 | 0.704 | 48 | 232 |
| SPY | 15 | 279 | 97.20% | 85.37% | 0.862 | 0.686 | 51 | 284 |

Piores janelas contra B4 por profundidade relativa:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 2000-02-29 | 2005-03-07 | 5 | 6.11% | 0.813 | 0.451 | 634 |
| 2000-02-29 | 2010-03-09 | 10 | 3.29% | 0.771 | 0.451 | 1231 |
| 2000-02-29 | 2015-03-11 | 15 | 15.63% | 1.664 | 0.451 | 1231 |
| 2000-02-29 | 2003-03-06 | 3 | 2.25% | 0.764 | 0.451 | 634 |
| 2000-03-31 | 2003-04-08 | 3 | 1.19% | 0.752 | 0.469 | 619 |
| 2000-03-31 | 2015-04-14 | 15 | 18.59% | 1.727 | 0.469 | 857 |
| 2000-03-31 | 2010-04-12 | 10 | 4.88% | 0.842 | 0.469 | 857 |
| 2000-03-31 | 2005-04-08 | 5 | 8.49% | 0.804 | 0.469 | 619 |
| 2021-11-30 | 2024-12-03 | 3 | 10.96% | 1.123 | 0.470 | 612 |
| 2021-12-31 | 2025-01-06 | 3 | 14.93% | 1.205 | 0.475 | 611 |

Janelas contra B4 com maior sequencia abaixo do benchmark:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 2003-10-31 | 2013-11-05 | 10 | 7.26% | 1.361 | 0.490 | 2047 |
| 2003-10-31 | 2018-11-06 | 15 | 38.16% | 2.916 | 0.490 | 2047 |
| 2000-02-29 | 2015-03-11 | 15 | 15.63% | 1.664 | 0.451 | 1231 |
| 2000-02-29 | 2010-03-09 | 10 | 3.29% | 0.771 | 0.451 | 1231 |
| 2004-01-30 | 2014-02-04 | 10 | 9.44% | 1.430 | 0.500 | 1230 |
| 2003-11-28 | 2013-12-03 | 10 | 8.73% | 1.471 | 0.501 | 1230 |
| 2004-01-30 | 2019-02-06 | 15 | 39.62% | 3.136 | 0.500 | 1230 |
| 2004-01-30 | 2009-02-02 | 5 | 0.48% | 0.861 | 0.500 | 1230 |
| 2003-11-28 | 2018-12-04 | 15 | 39.14% | 3.159 | 0.501 | 1230 |
| 2003-12-31 | 2014-01-06 | 10 | 9.68% | 1.497 | 0.504 | 1229 |

## Entry-Date Analysis

![Entry heatmap](plots/01_qld_voteK2_sma250_100_zroz_entry_date_forward_returns_heatmap.png)

Piores entradas contra B4, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 2000-02-29 | 2001-02-28 | 1 | -39.05% | 7.79% | -46.84% |
| 2007-06-29 | 2008-06-30 | 1 | -31.47% | 13.37% | -44.84% |
| 2007-07-31 | 2008-07-30 | 1 | -32.57% | 10.14% | -42.71% |
| 2021-11-30 | 2022-11-30 | 1 | -56.37% | -13.78% | -42.58% |
| 2007-05-31 | 2008-05-30 | 1 | -28.26% | 14.09% | -42.36% |
| 1989-09-29 | 1990-09-28 | 1 | -39.66% | 0.22% | -39.88% |
| 2021-10-29 | 2022-10-31 | 1 | -58.84% | -19.07% | -39.78% |
| 2000-03-31 | 2001-04-02 | 1 | -42.69% | -3.74% | -38.95% |
| 2021-12-31 | 2023-01-03 | 1 | -57.49% | -18.96% | -38.54% |
| 2007-04-30 | 2008-04-29 | 1 | -24.15% | 14.22% | -38.37% |

Piores entradas contra SPY, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | spy_cagr | strategy_edge_vs_spy |
|---|---|---|---|---|---|
| 2021-11-30 | 2022-11-30 | 1 | -56.37% | -9.07% | -47.30% |
| 2009-02-27 | 2010-03-01 | 1 | 9.51% | 55.01% | -45.51% |
| 2021-10-29 | 2022-10-31 | 1 | -58.84% | -14.55% | -44.29% |
| 2022-02-28 | 2023-03-01 | 1 | -48.55% | -8.04% | -40.52% |
| 2021-12-31 | 2023-01-03 | 1 | -57.49% | -18.44% | -39.05% |
| 2022-01-31 | 2023-02-01 | 1 | -45.83% | -7.12% | -38.71% |
| 2009-03-31 | 2010-03-31 | 1 | 16.77% | 50.22% | -33.45% |
| 2021-09-30 | 2022-09-30 | 1 | -46.71% | -15.43% | -31.28% |
| 2008-12-31 | 2009-12-31 | 1 | -3.93% | 26.49% | -30.41% |
| 1989-09-29 | 1990-09-28 | 1 | -39.66% | -9.36% | -30.30% |

Melhores entradas contra B4:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 1999-02-26 | 2000-02-25 | 1 | 181.25% | -2.09% | 183.34% |
| 1999-03-31 | 2000-03-29 | 1 | 163.30% | 10.09% | 153.21% |
| 1998-12-31 | 1999-12-31 | 1 | 150.63% | 0.48% | 150.14% |
| 1998-01-30 | 1999-02-01 | 1 | 185.29% | 40.05% | 145.24% |
| 1997-03-31 | 2000-03-28 | 3 | 149.19% | 25.34% | 123.84% |
| 1998-11-30 | 1999-11-30 | 1 | 125.40% | 2.92% | 122.49% |
| 1997-04-30 | 1998-04-30 | 1 | 158.54% | 43.95% | 114.59% |
| 1997-02-28 | 2000-02-29 | 3 | 133.69% | 20.63% | 113.07% |
| 1998-10-30 | 1999-11-01 | 1 | 117.56% | 8.44% | 109.11% |
| 2023-02-28 | 2024-02-29 | 1 | 125.02% | 18.44% | 106.58% |

## Crises E Regimes

![Crise relativa](plots/01_qld_voteK2_sma250_100_zroz_crisis_relative_equity.png)

| crisis | start | end | Strategy_return | Strategy_mdd | SPY buy&hold_return | SPY buy&hold_mdd | Plano C B4 original_return | Plano C B4 original_mdd |
|---|---|---|---|---|---|---|---|---|
| dotcom | 2000-03-24 | 2002-10-09 | -25.61% | -59.72% | -47.38% | -47.38% | -17.88% | -28.38% |
| gfc | 2007-10-09 | 2009-03-09 | -11.89% | -43.27% | -55.14% | -55.14% | -17.05% | -27.66% |
| covid | 2020-02-19 | 2020-06-30 | -9.82% | -35.86% | -7.86% | -33.69% | 5.93% | -19.25% |
| rates_2022 | 2021-12-27 | 2022-12-30 | -59.80% | -64.26% | -18.49% | -24.44% | -20.31% | -24.21% |

O ponto estrutural continua sendo 2000: a troca de SMA200/50 para SMA250/100 reduziu o dano do dotcom versus a canonica, porque o filtro longo sai antes da parte mais destrutiva da bolha. Em 2022, ZROZ deixa de ser hedge perfeito porque duration longa tambem sofre com alta de juros.

## Comportamento ON/OFF

| metric | value |
|---|---|
| pct_days_on_qld | 0.743 |
| pct_days_off_zroz | 0.257 |
| switch_count | 363.000 |
| avg_qld_weight | 0.743 |
| avg_zroz_weight | 0.257 |
| avg_on_run_days | 39.363 |
| avg_off_run_days | 13.632 |

O numero de switches e a duracao media de regimes ajudam a separar duas coisas: edge de sinal e friccao operacional. Quanto mais trocas, maior o risco de imposto per-swing e slippage; por isso os estudos posteriores de buffer/histerese continuam relevantes `[systematic_trading, Carver p.122-133]`.

## Limitacoes E Veredito

- Este relatorio e gross-first; nao e autorizacao de deploy.
- A comparacao principal e limitada pela janela comum com B4, que comeca em 1988 por causa do historico efetivo dos sleeves do B4.
- QLD/NDX e uma aposta concentrada em Nasdaq; o estudo mostrou que o mesmo Vote-K nao generaliza bem para UPRO/SPX.
- MDD permanece warning-only no mandato, mas drawdowns de LETF continuam psicologicamente e operacionalmente relevantes.
- Capital segue 100% Plano C; Strategy B permanece DORMANT.

Veredito: excelente candidata de pesquisa e a melhor configuracao Sortino-first encontrada, mas ainda deve ser tratada como monitoramento/paper research, nao como carteira real.

## Artefatos Gerados

- `data/01_qld_voteK2_sma250_100_zroz_daily_series.csv`
- `data/01_qld_voteK2_sma250_100_zroz_summary_metrics.csv`
- `data/01_qld_voteK2_sma250_100_zroz_rolling_summary.csv`
- `data/01_qld_voteK2_sma250_100_zroz_rolling_relative_windows.csv`
- `data/01_qld_voteK2_sma250_100_zroz_entry_forward_returns.csv`
- `data/01_qld_voteK2_sma250_100_zroz_crisis_windows.csv`
- `data/01_qld_voteK2_sma250_100_zroz_regime_stats.csv`
- `plots/01_qld_voteK2_sma250_100_zroz_equity_vs_spy_b4.png`
- `plots/01_qld_voteK2_sma250_100_zroz_relative_to_spy_b4.png`
- `plots/01_qld_voteK2_sma250_100_zroz_drawdown_vs_spy_b4.png`
- `plots/01_qld_voteK2_sma250_100_zroz_rolling_cagr.png`
- `plots/01_qld_voteK2_sma250_100_zroz_rolling_relative_equity_vs_spy_b4.png`
- `plots/01_qld_voteK2_sma250_100_zroz_rolling_pct_days_above_benchmark.png`
- `plots/01_qld_voteK2_sma250_100_zroz_rolling_winrate_vs_spy_b4.png`
- `plots/01_qld_voteK2_sma250_100_zroz_entry_date_forward_returns_heatmap.png`
- `plots/01_qld_voteK2_sma250_100_zroz_crisis_relative_equity.png`
