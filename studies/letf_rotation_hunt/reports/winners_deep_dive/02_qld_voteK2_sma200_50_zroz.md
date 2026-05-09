# Winner Deep Dive 02 — QLD Vote-K2 SMA200/50 + ZROZ

## Resumo Executivo

Esta e a vencedora canonica historica sob Sharpe; supersedida por SMA250/100 sob Sortino: `qld_voteK2_sma200_50_vol21_40_ar30_off_zroz`. Na janela comum contra os dois benchmarks obrigatorios, ela entrega CAGR de **24.99%**, Sortino **1.068** e MDD **-74.88%**. O SPY buy-and-hold fica em CAGR **11.35%** / Sortino **0.884**, enquanto o Plano C B4 original fica em CAGR **14.62%** / Sortino **1.464**.

Nota de leitura: as metricas deste relatorio sao recalculadas na janela comum contra B4 (`1988-2026`). Elas podem divergir dos numeros do `STUDY_FINAL_REPORT.md`, que por vezes usa `lh_56y` completo ou janelas especificas por sub-estudo.

A leitura honesta: a estrategia domina SPY em acumulacao de riqueza e tem forte comportamento em varias janelas, mas e muito mais agressiva que o Plano C B4. O B4 e o benchmark correto de alocacao real porque e a carteira passiva ativa do mandato; esta estrategia continua sendo pesquisa de Plano B, sem autorizacao de deploy.

## Definicao Operacional

- Familia: T3d Vote-K=2 canonica do estudo original, com SMA200/50.
- Risk-on: `QLD`.
- Risk-off: `ZROZ`.
- Sinal: Vote-of-K com `K=2` sobre quatro sinais diarios.
- Sinal 1: preco do QQQ/NDX acima da SMA200.
- Sinal 2: preco do QQQ/NDX acima da SMA50.
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
| Strategy | 1988-01-04 | 2026-04-17 | 38.3 | 24.99% | -74.88% | 0.797 | 1.068 | 0.334 | 36.73% | $54,697,612 |
| SPY buy&hold | 1988-01-04 | 2026-04-17 | 38.3 | 11.35% | -55.14% | 0.691 | 0.884 | 0.206 | 18.06% | $635,573 |
| Plano C B4 original | 1988-01-04 | 2026-04-17 | 38.3 | 14.62% | -28.38% | 1.027 | 1.464 | 0.515 | 14.35% | $1,889,198 |

## Equity E Relativo Aos Benchmarks

![Equity vs SPY e B4](plots/02_qld_voteK2_sma200_50_zroz_equity_vs_spy_b4.png)

![Relativo vs SPY e B4](plots/02_qld_voteK2_sma200_50_zroz_relative_to_spy_b4.png)

![Drawdown vs SPY e B4](plots/02_qld_voteK2_sma200_50_zroz_drawdown_vs_spy_b4.png)

Interpretacao: a estrategia tem compounding muito superior ao SPY, mas a comparacao contra B4 e mais exigente. O B4 reduz drawdown por diversificacao estrutural; a estrategia aceita drawdown LETF severo em troca de maior convexidade de retorno.

## Rolling Windows

![Rolling CAGR](plots/02_qld_voteK2_sma200_50_zroz_rolling_cagr.png)

![Rolling relative equity](plots/02_qld_voteK2_sma200_50_zroz_rolling_relative_equity_vs_spy_b4.png)

![Rolling pct days above benchmark](plots/02_qld_voteK2_sma200_50_zroz_rolling_pct_days_above_benchmark.png)

![Rolling win-rate](plots/02_qld_voteK2_sma200_50_zroz_rolling_winrate_vs_spy_b4.png)

| window_years | n_windows | median_sharpe | p10_sharpe | p90_sharpe | median_cagr | p10_cagr | p90_cagr | winrate_sharpe_vs_spy | winrate_sharpe_vs_b4 | winrate_cagr_vs_spy | winrate_cagr_vs_b4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 8890 | 0.904 | 0.325 | 1.355 | 27.21% | 4.70% | 47.82% | 52.95% | 26.96% | 85.52% | 81.92% |
| 5 | 8386 | 0.803 | 0.461 | 1.278 | 25.53% | 10.37% | 42.97% | 61.52% | 21.76% | 93.99% | 90.39% |
| 10 | 7126 | 0.844 | 0.549 | 1.145 | 26.58% | 15.29% | 37.17% | 83.43% | 11.18% | 100.00% | 95.09% |
| 15 | 5866 | 0.756 | 0.625 | 0.997 | 24.26% | 18.75% | 30.88% | 95.64% | 4.42% | 100.00% | 100.00% |

Leitura: as janelas curtas mostram a variancia real do trade. Em horizontes maiores, o edge de compounding aparece com mais clareza, mas a comparacao contra B4 e deliberadamente dura: B4 e diversificado e menos dependente de um unico regime Nasdaq.

### Psicologia Da Equity Relativa

Esta tabela mede cada start date mensal como se o investidor tivesse começado ali e segurado por 3/5/10/15 anos. `pct_days_above_benchmark` responde quanto do caminho a estrategia ficou acima do benchmark. `min_relative_equity` responde quao ruim ficou quando ficou abaixo. `max_consecutive_days_below_benchmark` aproxima quanto tempo demorou para recuperar em termos relativos.

| benchmark | horizon_years | n_windows | median_pct_days_above_benchmark | p10_pct_days_above_benchmark | median_min_relative_equity | p10_min_relative_equity | median_max_consecutive_days_below_benchmark | p90_max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|---|---|
| B4 | 3 | 423 | 78.34% | 23.78% | 0.842 | 0.627 | 75 | 395 |
| B4 | 5 | 399 | 84.62% | 42.27% | 0.826 | 0.626 | 101 | 362 |
| B4 | 10 | 339 | 90.52% | 56.20% | 0.814 | 0.623 | 113 | 353 |
| B4 | 15 | 279 | 92.09% | 65.72% | 0.755 | 0.602 | 139 | 515 |
| SPY | 3 | 423 | 85.47% | 29.30% | 0.860 | 0.647 | 62 | 319 |
| SPY | 5 | 399 | 90.25% | 55.54% | 0.851 | 0.674 | 62 | 290 |
| SPY | 10 | 339 | 95.12% | 80.79% | 0.851 | 0.693 | 66 | 269 |
| SPY | 15 | 279 | 95.74% | 84.75% | 0.835 | 0.680 | 75 | 285 |

Piores janelas contra B4 por profundidade relativa:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 2000-02-29 | 2005-03-07 | 5 | 1.27% | 0.444 | 0.280 | 1240 |
| 2000-02-29 | 2003-03-06 | 3 | 2.11% | 0.452 | 0.280 | 736 |
| 2000-02-29 | 2015-03-11 | 15 | 9.44% | 1.181 | 0.280 | 3410 |
| 2000-02-29 | 2010-03-09 | 10 | 0.63% | 0.483 | 0.280 | 2500 |
| 2000-03-31 | 2010-04-12 | 10 | 0.00% | 0.528 | 0.290 | 2520 |
| 2000-03-31 | 2015-04-14 | 15 | 10.02% | 1.226 | 0.290 | 3394 |
| 2000-03-31 | 2003-04-08 | 3 | 0.00% | 0.489 | 0.290 | 756 |
| 2000-03-31 | 2005-04-08 | 5 | 0.00% | 0.448 | 0.290 | 1260 |
| 1999-12-31 | 2005-01-06 | 5 | 3.81% | 0.563 | 0.327 | 1192 |
| 1999-12-31 | 2003-01-07 | 3 | 6.34% | 0.481 | 0.327 | 688 |

Janelas contra B4 com maior sequencia abaixo do benchmark:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 2000-02-29 | 2015-03-11 | 15 | 9.44% | 1.181 | 0.280 | 3410 |
| 2000-03-31 | 2015-04-14 | 15 | 10.02% | 1.226 | 0.290 | 3394 |
| 1999-12-31 | 2015-01-12 | 15 | 11.13% | 1.271 | 0.327 | 3332 |
| 2000-01-31 | 2015-02-10 | 15 | 14.52% | 1.537 | 0.377 | 2699 |
| 2000-03-31 | 2010-04-12 | 10 | 0.00% | 0.528 | 0.290 | 2520 |
| 2000-02-29 | 2010-03-09 | 10 | 0.63% | 0.483 | 0.280 | 2500 |
| 2000-01-31 | 2010-02-08 | 10 | 2.02% | 0.641 | 0.377 | 2469 |
| 1999-12-31 | 2010-01-08 | 10 | 1.90% | 0.629 | 0.327 | 2452 |
| 2003-07-31 | 2013-08-05 | 10 | 17.65% | 1.380 | 0.472 | 1783 |
| 2003-07-31 | 2018-08-06 | 15 | 45.09% | 3.845 | 0.472 | 1783 |

## Entry-Date Analysis

![Entry heatmap](plots/02_qld_voteK2_sma200_50_zroz_entry_date_forward_returns_heatmap.png)

Piores entradas contra B4, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 2000-02-29 | 2001-02-28 | 1 | -56.68% | 7.79% | -64.47% |
| 1999-12-31 | 2000-12-29 | 1 | -51.93% | 10.52% | -62.45% |
| 2000-01-31 | 2001-01-30 | 1 | -43.93% | 16.39% | -60.32% |
| 2000-03-31 | 2001-04-02 | 1 | -59.27% | -3.74% | -55.53% |
| 2003-07-31 | 2004-08-02 | 1 | -25.47% | 21.30% | -46.77% |
| 2000-05-31 | 2001-05-31 | 1 | -41.30% | 4.82% | -46.12% |
| 1999-11-30 | 2000-11-28 | 1 | -32.27% | 11.49% | -43.76% |
| 2000-04-28 | 2001-04-30 | 1 | -37.15% | 4.47% | -41.63% |
| 1989-09-29 | 1990-09-28 | 1 | -40.97% | 0.22% | -41.19% |
| 2007-06-29 | 2008-06-30 | 1 | -25.54% | 13.37% | -38.91% |

Piores entradas contra SPY, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | spy_cagr | strategy_edge_vs_spy |
|---|---|---|---|---|---|
| 2000-02-29 | 2001-02-28 | 1 | -56.68% | -8.77% | -47.91% |
| 2000-01-31 | 2001-01-30 | 1 | -43.93% | -0.12% | -43.81% |
| 2021-11-30 | 2022-11-30 | 1 | -51.43% | -9.07% | -42.37% |
| 1999-12-31 | 2000-12-29 | 1 | -51.93% | -9.64% | -42.28% |
| 2021-10-29 | 2022-10-31 | 1 | -54.19% | -14.55% | -39.64% |
| 2003-07-31 | 2004-08-02 | 1 | -25.47% | 13.63% | -39.11% |
| 2022-02-28 | 2023-03-01 | 1 | -47.01% | -8.04% | -38.97% |
| 2022-01-31 | 2023-02-01 | 1 | -44.50% | -7.12% | -37.38% |
| 2000-03-31 | 2001-04-02 | 1 | -59.27% | -23.16% | -36.11% |
| 2021-12-31 | 2023-01-03 | 1 | -52.45% | -18.44% | -34.01% |

Melhores entradas contra B4:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 1998-01-30 | 1999-02-01 | 1 | 186.13% | 40.05% | 146.07% |
| 1999-03-31 | 2000-03-29 | 1 | 139.58% | 10.09% | 129.48% |
| 1990-09-28 | 1991-09-27 | 1 | 145.51% | 24.25% | 121.26% |
| 1990-10-31 | 1991-10-30 | 1 | 143.82% | 28.83% | 115.00% |
| 1990-08-31 | 1991-08-30 | 1 | 132.62% | 24.80% | 107.82% |
| 1990-12-31 | 1991-12-30 | 1 | 123.34% | 25.51% | 97.82% |
| 2019-08-30 | 2020-08-31 | 1 | 124.42% | 28.40% | 96.03% |
| 1996-07-31 | 1997-07-30 | 1 | 139.91% | 44.82% | 95.09% |
| 1996-01-31 | 1997-01-29 | 1 | 105.69% | 12.11% | 93.58% |
| 1999-02-26 | 2000-02-25 | 1 | 89.26% | -2.09% | 91.34% |

## Crises E Regimes

![Crise relativa](plots/02_qld_voteK2_sma200_50_zroz_crisis_relative_equity.png)

| crisis | start | end | Strategy_return | Strategy_mdd | SPY buy&hold_return | SPY buy&hold_mdd | Plano C B4 original_return | Plano C B4 original_mdd |
|---|---|---|---|---|---|---|---|---|
| dotcom | 2000-03-24 | 2002-10-09 | -56.72% | -74.88% | -47.38% | -47.38% | -17.88% | -28.38% |
| gfc | 2007-10-09 | 2009-03-09 | -12.26% | -40.60% | -55.14% | -55.14% | -17.05% | -27.66% |
| covid | 2020-02-19 | 2020-06-30 | 8.24% | -29.27% | -7.86% | -33.69% | 5.93% | -19.25% |
| rates_2022 | 2021-12-27 | 2022-12-30 | -55.03% | -59.71% | -18.49% | -24.44% | -20.31% | -24.21% |

O ponto estrutural continua sendo 2000: a troca de SMA200/50 para SMA250/100 reduziu o dano do dotcom versus a canonica, porque o filtro longo sai antes da parte mais destrutiva da bolha. Em 2022, ZROZ deixa de ser hedge perfeito porque duration longa tambem sofre com alta de juros.

## Comportamento ON/OFF

| metric | value |
|---|---|
| pct_days_on_qld | 0.735 |
| pct_days_off_zroz | 0.265 |
| switch_count | 434.000 |
| avg_qld_weight | 0.735 |
| avg_zroz_weight | 0.265 |
| avg_on_run_days | 32.500 |
| avg_off_run_days | 11.797 |

O numero de switches e a duracao media de regimes ajudam a separar duas coisas: edge de sinal e friccao operacional. Quanto mais trocas, maior o risco de imposto per-swing e slippage; por isso os estudos posteriores de buffer/histerese continuam relevantes `[systematic_trading, Carver p.122-133]`.

## Limitacoes E Veredito

- Este relatorio e gross-first; nao e autorizacao de deploy.
- A comparacao principal e limitada pela janela comum com B4, que comeca em 1988 por causa do historico efetivo dos sleeves do B4.
- QLD/NDX e uma aposta concentrada em Nasdaq; o estudo mostrou que o mesmo Vote-K nao generaliza bem para UPRO/SPX.
- MDD permanece warning-only no mandato, mas drawdowns de LETF continuam psicologicamente e operacionalmente relevantes.
- Capital segue 100% Plano C; Strategy B permanece DORMANT.

Veredito: forte baseline canonico e referencia historica do estudo, mas a variante SMA250/100 melhora a robustez de cauda e tomou o posto operacional sob Sortino.

## Artefatos Gerados

- `data/02_qld_voteK2_sma200_50_zroz_daily_series.csv`
- `data/02_qld_voteK2_sma200_50_zroz_summary_metrics.csv`
- `data/02_qld_voteK2_sma200_50_zroz_rolling_summary.csv`
- `data/02_qld_voteK2_sma200_50_zroz_rolling_relative_windows.csv`
- `data/02_qld_voteK2_sma200_50_zroz_entry_forward_returns.csv`
- `data/02_qld_voteK2_sma200_50_zroz_crisis_windows.csv`
- `data/02_qld_voteK2_sma200_50_zroz_regime_stats.csv`
- `plots/02_qld_voteK2_sma200_50_zroz_equity_vs_spy_b4.png`
- `plots/02_qld_voteK2_sma200_50_zroz_relative_to_spy_b4.png`
- `plots/02_qld_voteK2_sma200_50_zroz_drawdown_vs_spy_b4.png`
- `plots/02_qld_voteK2_sma200_50_zroz_rolling_cagr.png`
- `plots/02_qld_voteK2_sma200_50_zroz_rolling_relative_equity_vs_spy_b4.png`
- `plots/02_qld_voteK2_sma200_50_zroz_rolling_pct_days_above_benchmark.png`
- `plots/02_qld_voteK2_sma200_50_zroz_rolling_winrate_vs_spy_b4.png`
- `plots/02_qld_voteK2_sma200_50_zroz_entry_date_forward_returns_heatmap.png`
- `plots/02_qld_voteK2_sma200_50_zroz_crisis_relative_equity.png`
