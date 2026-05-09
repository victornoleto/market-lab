# Winner Deep Dive 05 — ERC Multi4 Sigma 30% + ZROZ

## Resumo Executivo

Esta e a melhor configuracao T5 expandida, mas abaixo do threshold Sortino: `erc_multi4_sigma030`. Na janela comum contra os dois benchmarks obrigatorios, ela entrega CAGR de **19.22%**, Sortino **1.048** e MDD **-48.64%**. O SPY buy-and-hold fica em CAGR **11.35%** / Sortino **0.884**, enquanto o Plano C B4 original fica em CAGR **14.62%** / Sortino **1.464**.

Nota de leitura: as metricas deste relatorio sao recalculadas na janela comum contra B4 (`1988-2026`). Elas podem divergir dos numeros do `STUDY_FINAL_REPORT.md`, que por vezes usa `lh_56y` completo ou janelas especificas por sub-estudo.

A leitura honesta: a estrategia domina SPY em acumulacao de riqueza e tem forte comportamento em varias janelas, mas e muito mais agressiva que o Plano C B4. O B4 e o benchmark correto de alocacao real porque e a carteira passiva ativa do mandato; esta estrategia continua sendo pesquisa de Plano B, sem autorizacao de deploy.

## Definicao Operacional

- Familia: Carver-style vol-target multi-asset com Equal Risk Contribution em UPRO/QLD/UGL/TMF.
- Pool risk-on: `UPRO, QLD, UGL, TMF`.
- Risk-off/cash defensivo: `ZROZ`.
- Forecast: EWMAC padrao do dispatcher T5 com vol targeting.
- Weighting: Equal Risk Contribution (`erc`) sobre o pool.
- Sigma target anual: 30%.
- Position inertia: 10%.
- Regra: alocar continuamente nos ativos do pool conforme forecast/vol alvo; excedente fica em `ZROZ` `[systematic_trading, ch.7-12 p.98-202]`, `[advances_fin_ml, ch.16 p.221-228]`.

O uso de Sortino como metrica primaria e adequado porque LETF rotation busca capturar upside convexo e nao deve penalizar volatilidade positiva simetricamente como Sharpe `[advances_fin_ml, p.275]`. Esta configuracao pertence a familia Carver de forecast + vol targeting, onde forecast, volatilidade realizada, diversificacao e inertia governam sizing `[systematic_trading, ch.7-12 p.98-202]`. O peso ERC substitui IDM uniforme por contribuicao igual de risco, inspirado em alocacao hierarquica/risk-based `[advances_fin_ml, ch.16 p.221-228]`.

## Benchmark Set

- `SPY buy&hold`: `SPYSIM`, comprado e mantido.
- `Plano C B4 original`: 25% `NTSXSIM`, 25% `GDESIM`, 25% `RSSTSIM`, 25% `ZROZSIM`.
- Janela comum: `1988-01-04` a `2026-04-17`.
- Capital inicial normalizado: `$10,000`.

O B4 e capital-efficient stacking: NTSX empilha equity + Treasuries, GDE empilha equity + ouro, RSST empilha equity + managed futures, e ZROZ adiciona duration convexa `[risk_parity, ch.5, p.10]`.

## Metricas Principais

| series | start | end | years | cagr | mdd | sharpe | sortino | calmar | vol_ann | final_equity |
|---|---|---|---|---|---|---|---|---|---|---|
| Strategy | 1988-01-04 | 2026-04-17 | 38.3 | 19.22% | -48.64% | 0.763 | 1.048 | 0.395 | 28.31% | $8,370,007 |
| SPY buy&hold | 1988-01-04 | 2026-04-17 | 38.3 | 11.35% | -55.14% | 0.691 | 0.884 | 0.206 | 18.06% | $635,573 |
| Plano C B4 original | 1988-01-04 | 2026-04-17 | 38.3 | 14.62% | -28.38% | 1.027 | 1.464 | 0.515 | 14.35% | $1,889,198 |

## Equity E Relativo Aos Benchmarks

![Equity vs SPY e B4](plots/05_erc_multi4_sigma030_equity_vs_spy_b4.png)

![Relativo vs SPY e B4](plots/05_erc_multi4_sigma030_relative_to_spy_b4.png)

![Drawdown vs SPY e B4](plots/05_erc_multi4_sigma030_drawdown_vs_spy_b4.png)

Interpretacao: a estrategia tem compounding muito superior ao SPY, mas a comparacao contra B4 e mais exigente. O B4 reduz drawdown por diversificacao estrutural; a estrategia aceita drawdown LETF severo em troca de maior convexidade de retorno.

## Rolling Windows

![Rolling CAGR](plots/05_erc_multi4_sigma030_rolling_cagr.png)

![Rolling relative equity](plots/05_erc_multi4_sigma030_rolling_relative_equity_vs_spy_b4.png)

![Rolling pct days above benchmark](plots/05_erc_multi4_sigma030_rolling_pct_days_above_benchmark.png)

![Rolling win-rate](plots/05_erc_multi4_sigma030_rolling_winrate_vs_spy_b4.png)

| window_years | n_windows | median_sharpe | p10_sharpe | p90_sharpe | median_cagr | p10_cagr | p90_cagr | winrate_sharpe_vs_spy | winrate_sharpe_vs_b4 | winrate_cagr_vs_spy | winrate_cagr_vs_b4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 8890 | 0.756 | 0.214 | 1.313 | 17.78% | 2.18% | 40.71% | 39.94% | 30.11% | 68.35% | 63.02% |
| 5 | 8386 | 0.803 | 0.416 | 1.094 | 20.01% | 7.69% | 33.06% | 49.12% | 25.73% | 81.24% | 70.22% |
| 10 | 7126 | 0.788 | 0.570 | 0.953 | 20.31% | 13.21% | 25.74% | 81.24% | 8.35% | 95.33% | 85.84% |
| 15 | 5866 | 0.760 | 0.630 | 0.861 | 19.25% | 15.05% | 23.10% | 95.14% | 0.00% | 100.00% | 99.40% |

Leitura: as janelas curtas mostram a variancia real do trade. Em horizontes maiores, o edge de compounding aparece com mais clareza, mas a comparacao contra B4 e deliberadamente dura: B4 e diversificado e menos dependente de um unico regime Nasdaq.

### Psicologia Da Equity Relativa

Esta tabela mede cada start date mensal como se o investidor tivesse começado ali e segurado por 3/5/10/15 anos. `pct_days_above_benchmark` responde quanto do caminho a estrategia ficou acima do benchmark. `min_relative_equity` responde quao ruim ficou quando ficou abaixo. `max_consecutive_days_below_benchmark` aproxima quanto tempo demorou para recuperar em termos relativos.

| benchmark | horizon_years | n_windows | median_pct_days_above_benchmark | p10_pct_days_above_benchmark | median_min_relative_equity | p10_min_relative_equity | median_max_consecutive_days_below_benchmark | p90_max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|---|---|
| B4 | 3 | 423 | 62.75% | 3.30% | 0.849 | 0.618 | 118 | 670 |
| B4 | 5 | 399 | 71.29% | 5.36% | 0.837 | 0.585 | 166 | 1076 |
| B4 | 10 | 339 | 80.80% | 6.14% | 0.800 | 0.541 | 240 | 1939 |
| B4 | 15 | 279 | 82.17% | 22.45% | 0.812 | 0.533 | 234 | 2056 |
| SPY | 3 | 423 | 66.71% | 7.16% | 0.837 | 0.652 | 110 | 650 |
| SPY | 5 | 399 | 78.98% | 11.34% | 0.845 | 0.616 | 105 | 938 |
| SPY | 10 | 339 | 87.43% | 40.36% | 0.828 | 0.604 | 119 | 1161 |
| SPY | 15 | 279 | 91.62% | 57.92% | 0.829 | 0.600 | 145 | 1201 |

Piores janelas contra B4 por profundidade relativa:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 1988-01-29 | 2003-01-23 | 15 | 6.61% | 1.436 | 0.430 | 3433 |
| 1988-01-29 | 1998-01-16 | 10 | 0.36% | 0.557 | 0.430 | 2511 |
| 1988-02-29 | 2003-02-21 | 15 | 7.19% | 1.490 | 0.436 | 3297 |
| 1988-02-29 | 1998-02-17 | 10 | 0.04% | 0.533 | 0.436 | 2517 |
| 2002-09-30 | 2017-10-04 | 15 | 0.13% | 0.914 | 0.436 | 2231 |
| 2002-09-30 | 2012-10-01 | 10 | 0.20% | 0.682 | 0.436 | 2231 |
| 2002-09-30 | 2007-10-02 | 5 | 0.32% | 0.441 | 0.436 | 1252 |
| 1988-01-29 | 1991-01-25 | 3 | 1.19% | 0.496 | 0.467 | 747 |
| 1988-01-29 | 1993-01-22 | 5 | 0.71% | 0.540 | 0.467 | 1251 |
| 2003-05-30 | 2008-06-02 | 5 | 0.40% | 0.563 | 0.468 | 1254 |

Janelas contra B4 com maior sequencia abaixo do benchmark:

| start_date | end_date | horizon_years | pct_days_above_benchmark | final_relative_equity | min_relative_equity | max_consecutive_days_below_benchmark |
|---|---|---|---|---|---|---|
| 1988-01-29 | 2003-01-23 | 15 | 6.61% | 1.436 | 0.430 | 3433 |
| 1988-02-29 | 2003-02-21 | 15 | 7.19% | 1.490 | 0.436 | 3297 |
| 1988-03-31 | 2003-03-26 | 15 | 10.24% | 1.627 | 0.476 | 3257 |
| 1988-04-29 | 2003-04-24 | 15 | 11.95% | 1.696 | 0.502 | 3191 |
| 1988-10-31 | 2003-10-24 | 15 | 15.66% | 1.603 | 0.509 | 2829 |
| 1988-06-30 | 2003-06-25 | 15 | 14.92% | 1.610 | 0.519 | 2824 |
| 1989-05-31 | 2004-05-25 | 15 | 20.87% | 1.403 | 0.521 | 2824 |
| 1989-08-31 | 2004-08-27 | 15 | 23.30% | 1.396 | 0.527 | 2822 |
| 1989-01-31 | 2004-01-27 | 15 | 20.89% | 1.706 | 0.529 | 2822 |
| 1988-09-30 | 2003-09-25 | 15 | 18.54% | 1.777 | 0.527 | 2822 |

## Entry-Date Analysis

![Entry heatmap](plots/05_erc_multi4_sigma030_entry_date_forward_returns_heatmap.png)

Piores entradas contra B4, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 1989-10-31 | 1990-10-30 | 1 | -42.16% | -2.78% | -39.38% |
| 1989-09-29 | 1990-09-28 | 1 | -38.57% | 0.22% | -38.79% |
| 2006-04-28 | 2007-05-01 | 1 | -24.55% | 13.74% | -38.29% |
| 1989-08-31 | 1990-08-30 | 1 | -39.18% | -1.28% | -37.90% |
| 1989-11-30 | 1990-11-29 | 1 | -37.24% | 0.46% | -37.70% |
| 2011-08-31 | 2012-08-30 | 1 | -17.94% | 18.76% | -36.70% |
| 2011-07-29 | 2012-07-30 | 1 | -9.10% | 24.83% | -33.93% |
| 1990-01-31 | 1991-01-30 | 1 | -22.22% | 11.20% | -33.42% |
| 1989-12-29 | 1990-12-28 | 1 | -30.23% | 3.03% | -33.27% |
| 2006-03-31 | 2007-04-03 | 1 | -19.67% | 12.38% | -32.04% |

Piores entradas contra SPY, por CAGR forward:

| entry_date | exit_date | horizon_years | strategy_cagr | spy_cagr | strategy_edge_vs_spy |
|---|---|---|---|---|---|
| 2009-02-27 | 2010-03-01 | 1 | 8.02% | 55.01% | -46.99% |
| 2006-04-28 | 2007-05-01 | 1 | -24.55% | 15.29% | -39.84% |
| 2011-08-31 | 2012-08-30 | 1 | -17.94% | 17.49% | -35.43% |
| 2012-03-30 | 2013-04-04 | 1 | -21.99% | 13.26% | -35.25% |
| 2011-12-30 | 2013-01-03 | 1 | -15.98% | 18.81% | -34.79% |
| 1989-10-31 | 1990-10-30 | 1 | -42.16% | -7.57% | -34.59% |
| 2003-05-30 | 2004-05-28 | 1 | -15.76% | 18.37% | -34.13% |
| 2012-02-29 | 2013-03-04 | 1 | -19.91% | 14.19% | -34.10% |
| 2011-09-30 | 2012-10-01 | 1 | -3.67% | 30.42% | -34.09% |
| 2012-01-31 | 2013-02-01 | 1 | -16.15% | 17.84% | -33.99% |

Melhores entradas contra B4:

| entry_date | exit_date | horizon_years | strategy_cagr | b4_cagr | strategy_edge_vs_b4 |
|---|---|---|---|---|---|
| 2019-02-28 | 2020-02-28 | 1 | 110.14% | 25.37% | 84.76% |
| 2018-11-30 | 2019-12-03 | 1 | 103.33% | 25.45% | 77.88% |
| 2019-01-31 | 2020-01-31 | 1 | 107.29% | 29.58% | 77.71% |
| 2001-08-31 | 2002-09-09 | 1 | 66.48% | -7.05% | 73.52% |
| 2018-10-31 | 2019-11-01 | 1 | 97.51% | 27.63% | 69.88% |
| 2018-12-31 | 2019-12-31 | 1 | 99.94% | 31.06% | 68.88% |
| 2001-07-31 | 2002-08-06 | 1 | 49.02% | -17.98% | 67.00% |
| 2019-03-29 | 2020-03-30 | 1 | 83.99% | 19.90% | 64.09% |
| 2024-12-31 | 2026-01-05 | 1 | 89.88% | 26.47% | 63.41% |
| 2025-01-31 | 2026-02-03 | 1 | 88.35% | 26.52% | 61.83% |

## Crises E Regimes

![Crise relativa](plots/05_erc_multi4_sigma030_crisis_relative_equity.png)

| crisis | start | end | Strategy_return | Strategy_mdd | SPY buy&hold_return | SPY buy&hold_mdd | Plano C B4 original_return | Plano C B4 original_mdd |
|---|---|---|---|---|---|---|---|---|
| dotcom | 2000-03-24 | 2002-10-09 | 86.32% | -23.88% | -47.38% | -47.38% | -17.88% | -28.38% |
| gfc | 2007-10-09 | 2009-03-09 | 49.86% | -36.66% | -55.14% | -55.14% | -17.05% | -27.66% |
| covid | 2020-02-19 | 2020-06-30 | 0.35% | -31.48% | -7.86% | -33.69% | 5.93% | -19.25% |
| rates_2022 | 2021-12-27 | 2022-12-30 | -34.82% | -46.92% | -18.49% | -24.44% | -20.31% | -24.21% |

O ponto estrutural continua sendo 2000: a troca de SMA200/50 para SMA250/100 reduziu o dano do dotcom versus a canonica, porque o filtro longo sai antes da parte mais destrutiva da bolha. Em 2022, ZROZ deixa de ser hedge perfeito porque duration longa tambem sofre com alta de juros.

## Comportamento ON/OFF

| metric | value |
|---|---|
| pct_days_on_qld | 0.861 |
| pct_days_off_zroz | 0.139 |
| switch_count | 165.000 |
| avg_qld_weight | 0.195 |
| avg_zroz_weight | 0.137 |
| avg_on_run_days | 100.096 |
| avg_off_run_days | 16.108 |

O numero de switches e a duracao media de regimes ajudam a separar duas coisas: edge de sinal e friccao operacional. Quanto mais trocas, maior o risco de imposto per-swing e slippage; por isso os estudos posteriores de buffer/histerese continuam relevantes `[systematic_trading, Carver p.122-133]`.

## Limitacoes E Veredito

- Este relatorio e gross-first; nao e autorizacao de deploy.
- A comparacao principal e limitada pela janela comum com B4, que comeca em 1988 por causa do historico efetivo dos sleeves do B4.
- QLD/NDX e uma aposta concentrada em Nasdaq; o estudo mostrou que o mesmo Vote-K nao generaliza bem para UPRO/SPX.
- MDD permanece warning-only no mandato, mas drawdowns de LETF continuam psicologicamente e operacionalmente relevantes.
- Capital segue 100% Plano C; Strategy B permanece DORMANT.

Veredito: melhor representante da familia T5 expandida, util como diversificador metodologico, mas inferior ao threshold Sortino que manteria a familia viva como candidata principal.

## Artefatos Gerados

- `data/05_erc_multi4_sigma030_daily_series.csv`
- `data/05_erc_multi4_sigma030_summary_metrics.csv`
- `data/05_erc_multi4_sigma030_rolling_summary.csv`
- `data/05_erc_multi4_sigma030_rolling_relative_windows.csv`
- `data/05_erc_multi4_sigma030_entry_forward_returns.csv`
- `data/05_erc_multi4_sigma030_crisis_windows.csv`
- `data/05_erc_multi4_sigma030_regime_stats.csv`
- `plots/05_erc_multi4_sigma030_equity_vs_spy_b4.png`
- `plots/05_erc_multi4_sigma030_relative_to_spy_b4.png`
- `plots/05_erc_multi4_sigma030_drawdown_vs_spy_b4.png`
- `plots/05_erc_multi4_sigma030_rolling_cagr.png`
- `plots/05_erc_multi4_sigma030_rolling_relative_equity_vs_spy_b4.png`
- `plots/05_erc_multi4_sigma030_rolling_pct_days_above_benchmark.png`
- `plots/05_erc_multi4_sigma030_rolling_winrate_vs_spy_b4.png`
- `plots/05_erc_multi4_sigma030_entry_date_forward_returns_heatmap.png`
- `plots/05_erc_multi4_sigma030_crisis_relative_equity.png`
