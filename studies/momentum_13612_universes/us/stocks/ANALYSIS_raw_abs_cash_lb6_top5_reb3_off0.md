# Focused Analysis - `mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0`

Status: research-only. No deployment, paper-trade label or mandate change.

## Verdict

- Full-period after-tax metrics: CAGR `59.66%`, MDD `-59.04%`, Sharpe `1.386` versus SPY CAGR `10.87%` and SPY MDD `-55.19%`.
- Rolling relative dominance is high: score `96.28%`, p25 `95.17%`, min `19.18%`, terminal/SPY `190415.221`.
- Cash-filter audit: `no holding change` versus the raw equal-weight variant. The target is therefore not a distinct cash-filter improvement on this path.
- Portfolio-sleeve conclusion: not efficient enough for real allocation today. In the biased backtest a small sleeve improves SPY blends, but the evidence is not investable because the signal is current-universe yfinance, the cash filter is inactive, and drawdown remains equity-crisis sized. Operational weight under the mandate remains `0%`.
- Risk remains severe: worst strategy drawdown `-59.04%` and GFC MDD `-59.04%`.
- This remains non-promotable because the run uses yfinance/current S&P 500 constituents without true PIT/delisted returns `[advances_fin_ml, p.208-211]`.

## Setup

- Start: `1990-01-01`
- End: `2026-06-15`
- US source: `yfinance`
- US stock universe: `sp500`
- Max US stocks: `9999`
- Max abs daily return filter: `None`
- Dropped extreme-return tickers: `0`
- Target parameters: raw 6-month cross-sectional momentum, top 5, quarterly rebalance, offset 0, equal weight, absolute filter enabled `[stocks_on_the_move, p.60]`, `[stocks_on_the_move, p.98-99]`.
- Heatmap trial count used for DSR context: `4092` `[advances_fin_ml, p.273-275]`.

This is a focused rerun from the current local yfinance cache, not a static read of `heatmap_results.csv`; small metric drift can occur when the cache is refreshed.

## Algoritmo E Implementacao

A estrategia e uma rotacao cross-sectional de momentum de 6 meses em acoes do S&P 500 atual. Ela nao usa previsao macro, stop, leverage ou overlay de regime. A decisao e puramente relativa: a cada rebalance, compra as 5 acoes com maior retorno ajustado de 6 meses, desde que o score absoluto seja positivo `[stocks_on_the_move, p.60]`. O rebalance e trimestral no offset 0, isto e, nos fechamentos mensais de janeiro, abril, julho e outubro `[stocks_on_the_move, p.98-99]`.

Passos operacionais:

1. Definir o universo negociavel. Nesta analise: S&P 500 atual via yfinance. Em implementacao real, isso precisa ser substituido por universo point-in-time com delisted returns; caso contrario o resultado segue enviesado e nao promovivel `[advances_fin_ml, p.208-211]`.
2. Carregar precos diarios ajustados por dividendos/splits para todos os ativos e para o benchmark SPY. Usar adjusted close, nao close bruto.
3. Converter os precos diarios em precos de fechamento mensal (`resample('ME').last()`).
4. Em cada mes de rebalance, calcular `score = price_t / price_{t-6m} - 1`. O lookback `6m`, `top_n=5` e `rebalance=3m` sao parametros escolhidos apos o heatmap, logo carregam risco de data mining `[advances_fin_ml, p.273-275]`.
5. Ordenar os ativos por score decrescente, com desempate alfabetico estavel.
6. Selecionar os 5 primeiros e aplicar o filtro absoluto: manter apenas nomes com `score > 0`. Se menos de 5 nomes passarem, o peso nao usado fica em cash. Nesta estrategia especifica, o filtro nunca reduziu exposicao: sempre houve 5 nomes positivos.
7. Pesar igualmente os nomes selecionados. Com 5 nomes, cada ativo recebe `20%`; se somente 3 nomes passassem no filtro, a exposicao seria `60%` e cash `40%`.
8. Aplicar os pesos somente aos retornos futuros. Na implementacao do estudo, isso e feito com `daily_weights.shift(1)`, evitando usar o fechamento do proprio dia como se fosse executavel antes de conhecido `[advances_fin_ml, p.31-34]`.
9. Rebalancear apenas nas datas trimestrais elegiveis; entre rebalances, manter os pesos-alvo forward-filled.
10. Para metricas after-tax, aplicar o modelo anual aproximado de 15% sobre ganho realizado positivo, com compensacao/carrego de perdas. O modelo nao e lot-level e nao forca liquidacao final.

Pseudocodigo:

```text
for each month_end in calendar:
    if month_end is not Jan/Apr/Jul/Oct:
        continue
    scores = adjusted_monthly_price[month_end] / adjusted_monthly_price[month_end - 6 months] - 1
    ranked = sort_desc(scores)
    chosen = first 5 tickers from ranked where score > 0
    target_weight = 1 / 5 for each chosen ticker
    cash_weight = 1 - sum(target_weight)
    hold target weights until next eligible rebalance
daily_return[t] = weights[t-1] * asset_returns[t]
```

Regras de implementacao pratica:

- Executar no primeiro pregao depois do fechamento mensal usado no sinal, ou usar explicitamente o close seguinte como preco de execucao. Nao executar no mesmo close usado para calcular o ranking.
- Usar lotes inteiros e caixa residual; o backtest assume pesos fracionarios continuos, entao uma implementacao real deve registrar tracking error por arredondamento.
- Registrar ordens de venda antes das compras para medir realizacao fiscal e turnover.
- Nao tratar o filtro cash como defesa comprovada: neste path ele ficou inativo.
- Antes de qualquer paper/live, reimplementar em dataset PIT/delisted, custos reais, imposto lot-level, e validar em OOS/WF/PBO/DSR. Sem isso, a alocacao operacional permanece `0%` `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

## Full-Period Metrics

| Name | CAGR | MDD | Sharpe | Vol | Calmar | Terminal/SPY | RollRel | RollP25 | Turnover/Yr |
|---|---|---|---|---|---|---|---|---|---|
| raw_equal_lb6_top5_reb3_off0 | 59.66% | -59.04% | 1.386 | 39.41% | 1.011 | 190415.221 | 96.28% | 95.17% | 2.668 |
| raw_abs_cash_lb6_top5_reb3_off0 | 59.66% | -59.04% | 1.386 | 39.41% | 1.011 | 190415.221 | 96.28% | 95.17% | 2.668 |
| raw_inverse_vol_lb6_top5_reb3_off0 | 56.22% | -54.99% | 1.362 | 38.13% | 1.022 | 92146.552 | 96.61% | 95.38% | 2.905 |
| SPY benchmark | 10.87% | -55.19% | 0.649 | 18.58% | n/a | 1.000 | n/a | n/a | 0.000 |

SPY metrics are the adjusted-close buy-hold benchmark without applying the annual DARF approximation. Strategy metrics are after the study's annual 15% realized-gain tax approximation.

## Portfolio-Sleeve Conclusion

Direct answer: **no, not for real capital in the current evidence state**. As a research signal, the backtest is strong enough to keep as an aggressive diagnostic. As an implementable sleeve, it fails the practical bar: the data are current-universe yfinance, the absolute/cash filter never reduced risk on this path, GFC drawdown was worse than SPY, turnover is high, and the result was selected after a large heatmap `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

The table below shows why the temptation exists: in this biased sample, small SPY blends improve CAGR and terminal wealth. That is useful for sizing intuition, but it is not allocation evidence. A real sleeve would require a PIT/delisted dataset, independent validation, real taxes/costs and a portfolio-level test against the actual core portfolio, not just SPY. Until then, recommended portfolio weight is `0%`.

| sleeve | strategy_weight | cagr | mdd | vol | sharpe | terminal_vs_spy |
|---|---|---|---|---|---|---|
| 5% strategy / 95% SPY | 5.00% | 13.20% | -54.01% | 18.86% | 0.752 | 1.997 |
| 10% strategy / 90% SPY | 10.00% | 15.54% | -52.98% | 19.27% | 0.846 | 3.954 |
| 20% strategy / 80% SPY | 20.00% | 20.28% | -52.50% | 20.45% | 1.005 | 15.091 |
| 30% strategy / 70% SPY | 30.00% | 25.08% | -52.18% | 22.06% | 1.125 | 55.601 |

## Cash-Filter Audit

| Metric | Value |
|---|---|
| Max daily L1 weight diff vs raw_equal | 0.000000 |
| Differing daily weight rows | 0 |
| Differing rebalance rows | 0 |
| Avg daily gross exposure | 100.00% |
| Min daily gross exposure | 100.00% |
| Rebalances below full exposure | 0 |
| Avg names at rebalance | 5.000 |

Interpretation: for this exact `lb6/top5/reb3/off0` path, every selected top-5 stock had positive 6-month momentum at each active rebalance, so the absolute filter did not create cash exposure.

## Rolling Relative Dominance

| horizon_years | windows | above_mean | above_p25 | above_min | terminal_median | terminal_p25 | terminal_min | relative_mdd_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 365 | 88.96% | 85.56% | 19.18% | 2.666 | 1.766 | 0.991 | -30.06% |
| 5 | 341 | 93.36% | 91.59% | 42.97% | 5.603 | 2.535 | 1.318 | -31.54% |
| 10 | 281 | 96.30% | 94.80% | 71.50% | 19.373 | 8.442 | 2.903 | -38.13% |
| 15 | 221 | 98.03% | 97.70% | 80.99% | 61.128 | 30.571 | 15.473 | -38.13% |
| 20 | 161 | 99.19% | 99.03% | 94.50% | 390.385 | 252.473 | 115.519 | -49.56% |

Worst reset-window starts by time spent above SPY:

| horizon_years | start | end | pct_time_above_benchmark | terminal_relative | min_relative_equity | relative_mdd |
|---|---|---|---|---|---|---|
| 3 | 2014-01-31 | 2017-01-31 | 19.18% | 1.220 | 0.706 | -34.36% |
| 3 | 2014-02-28 | 2017-02-28 | 20.11% | 1.125 | 0.705 | -34.36% |
| 3 | 2013-09-30 | 2016-09-30 | 20.58% | 0.991 | 0.725 | -34.36% |
| 3 | 2010-11-30 | 2013-11-30 | 20.77% | 1.336 | 0.739 | -26.14% |
| 3 | 2008-06-30 | 2011-06-30 | 21.24% | 1.012 | 0.647 | -38.13% |
| 3 | 2013-10-31 | 2016-10-31 | 25.13% | 1.040 | 0.737 | -34.36% |
| 3 | 2008-07-31 | 2011-07-31 | 28.31% | 0.998 | 0.685 | -31.54% |
| 3 | 2013-12-31 | 2016-12-31 | 33.82% | 1.253 | 0.746 | -34.36% |
| 3 | 2014-03-31 | 2017-03-31 | 34.83% | 1.260 | 0.741 | -27.07% |
| 3 | 2008-04-30 | 2011-04-30 | 35.54% | 1.223 | 0.731 | -38.13% |

## Stress Windows

| period | start | end | strategy_cagr | strategy_mdd | strategy_sharpe | spy_cagr | spy_mdd | spy_sharpe | mdd_delta |
|---|---|---|---|---|---|---|---|---|---|
| dotcom | 2000-03-01 | 2002-10-31 | 9.70% | -49.48% | 0.438 | -14.14% | -47.52% | -0.512 | -1.96% |
| gfc | 2007-10-01 | 2009-03-31 | -11.66% | -59.04% | 0.031 | -33.66% | -55.19% | -0.879 | -3.85% |
| covid | 2020-02-01 | 2020-04-30 | 356.84% | -26.30% | 2.878 | -32.39% | -33.72% | -0.364 | 7.42% |
| inflation_2022 | 2022-01-01 | 2022-12-31 | 4.87% | -26.95% | 0.327 | -18.24% | -24.50% | -0.711 | -2.46% |

## Calendar Years

- Strategy beat SPY in `85.29%` of calendar years.
- Best excess year: `2024` with excess `204.15%`.
- Worst excess year: `2014` with excess `-16.15%`.

| year | strategy_return | spy_return | excess_return | strategy_won |
|---|---|---|---|---|
| 2026 | 155.99% | 10.99% | 144.99% | True |
| 2025 | 129.47% | 17.72% | 111.75% | True |
| 2024 | 229.04% | 24.89% | 204.15% | True |
| 2023 | 32.82% | 26.18% | 6.65% | True |
| 2022 | 4.85% | -18.18% | 23.03% | True |
| 2021 | 55.24% | 28.73% | 26.51% | True |
| 2020 | 180.72% | 18.33% | 162.39% | True |
| 2019 | 48.25% | 31.22% | 17.02% | True |
| 2018 | 56.13% | -4.57% | 60.70% | True |
| 2017 | 33.94% | 21.71% | 12.24% | True |
| 2016 | 46.36% | 12.00% | 34.36% | True |
| 2015 | 13.20% | 1.23% | 11.97% | True |

Full calendar-year table is in the annual returns CSV.

## Drawdowns

Strategy top drawdowns:

| peak | start | valley | recovery | depth | underwater_days |
|---|---|---|---|---|---|
| 2008-06-17 | 2008-06-18 | 2009-03-03 | 2010-11-03 | -59.04% | 869 |
| 2000-03-06 | 2000-03-07 | 2000-04-14 | 2001-05-02 | -49.48% | 422 |
| 2025-02-14 | 2025-02-18 | 2025-04-04 | 2025-06-30 | -42.19% | 136 |
| 2001-07-19 | 2001-07-20 | 2001-09-18 | 2001-11-09 | -40.75% | 113 |
| 1998-08-18 | 1998-08-19 | 1998-10-08 | 1998-11-17 | -38.80% | 91 |
| 2002-04-19 | 2002-04-22 | 2002-10-07 | 2003-05-14 | -34.80% | 390 |
| 2014-03-06 | 2014-03-07 | 2014-10-13 | 2015-04-20 | -33.72% | 410 |
| 2018-09-11 | 2018-09-12 | 2018-12-24 | 2019-03-21 | -33.71% | 191 |
| 2021-11-29 | 2021-11-30 | 2022-01-21 | 2022-11-10 | -33.00% | 346 |
| 2011-02-17 | 2011-02-18 | 2011-08-08 | 2012-04-25 | -31.92% | 433 |

SPY top drawdowns over the aligned window:

| peak | start | valley | recovery | depth | underwater_days |
|---|---|---|---|---|---|
| 2007-10-09 | 2007-10-10 | 2009-03-09 | 2012-08-16 | -55.19% | 1773 |
| 2000-03-24 | 2000-03-27 | 2002-10-09 | 2006-10-26 | -47.52% | 2407 |
| 2020-02-19 | 2020-02-20 | 2020-03-23 | 2020-08-10 | -33.72% | 173 |
| 2022-01-03 | 2022-01-04 | 2022-10-12 | 2023-12-13 | -24.50% | 709 |
| 2018-09-20 | 2018-09-21 | 2018-12-24 | 2019-04-12 | -19.35% | 204 |

## Holdings And Turnover

- Rebalance rows: `144`
- Annual turnover: `2.668`
- Avg turnover per rebalance: `0.665`
- Avg names changed: `6.657`
- Avg holding months: `4.475`

Top holdings by rebalance count:

| ticker | rebalance_count | pct_rebalances | avg_weight_when_held |
|---|---|---|---|
| MNST | 18 | 12.50% | 20.00% |
| AXON | 15 | 10.42% | 20.00% |
| AMD | 14 | 9.72% | 20.00% |
| FSLR | 12 | 8.33% | 20.00% |
| MU | 12 | 8.33% | 20.00% |
| NVDA | 12 | 8.33% | 20.00% |
| WDC | 12 | 8.33% | 20.00% |
| CVNA | 11 | 7.64% | 20.00% |
| NFLX | 11 | 7.64% | 20.00% |
| SWKS | 11 | 7.64% | 20.00% |
| INCY | 10 | 6.94% | 20.00% |
| REGN | 10 | 6.94% | 20.00% |
| BBY | 9 | 6.25% | 20.00% |
| BIIB | 9 | 6.25% | 20.00% |
| DXCM | 9 | 6.25% | 20.00% |
| SMCI | 9 | 6.25% | 20.00% |
| TPL | 9 | 6.25% | 20.00% |
| ALGN | 8 | 5.56% | 20.00% |
| AMZN | 8 | 5.56% | 20.00% |
| CF | 8 | 5.56% | 20.00% |

## Plots

All equity and relative-equity plots in this report use log scale.

- [mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0_vs_SPY.png](plots/analysis/mom13612_us_stocks_raw_abs_cash_lb6_top5_reb3_off0_vs_SPY.png)
- [analysis_raw_abs_cash_lb6_top5_reb3_off0_adjacent_mechanisms_log_equity.png](plots/analysis/analysis_raw_abs_cash_lb6_top5_reb3_off0_adjacent_mechanisms_log_equity.png)
- [analysis_raw_abs_cash_lb6_top5_reb3_off0_top_20_after-tax_sharpe_log_equity.png](plots/analysis/analysis_raw_abs_cash_lb6_top5_reb3_off0_top_20_after-tax_sharpe_log_equity.png)
- [analysis_raw_abs_cash_lb6_top5_reb3_off0_top_20_rolling_relative_log_equity.png](plots/analysis/analysis_raw_abs_cash_lb6_top5_reb3_off0_top_20_rolling_relative_log_equity.png)
- [analysis_raw_abs_cash_lb6_top5_reb3_off0_sleeve_blends_log_equity.png](plots/analysis/analysis_raw_abs_cash_lb6_top5_reb3_off0_sleeve_blends_log_equity.png)

## Output Files

- [summary JSON](results/analysis_raw_abs_cash_lb6_top5_reb3_off0_summary.json)
- [annual returns CSV](results/analysis_raw_abs_cash_lb6_top5_reb3_off0_annual_returns.csv)
- [rolling windows CSV](results/analysis_raw_abs_cash_lb6_top5_reb3_off0_rolling_windows.csv)
- [rebalances CSV](results/analysis_raw_abs_cash_lb6_top5_reb3_off0_rebalances.csv)
- [top holdings CSV](results/analysis_raw_abs_cash_lb6_top5_reb3_off0_top_holdings.csv)
- [sleeve blends CSV](results/analysis_raw_abs_cash_lb6_top5_reb3_off0_sleeve_blends.csv)
- [top-20 selected CSV](results/analysis_raw_abs_cash_lb6_top5_reb3_off0_top20_selected.csv)

## Notes

- Offsets and lookbacks are heatmap dimensions, so this analysis is a post-selection diagnostic, not a validation pass `[advances_fin_ml, p.273-275]`.
- Current-universe yfinance omits delisted losers and can inflate old US-stock momentum results `[advances_fin_ml, p.208-211]`.
- Rolling relative windows reset both strategy and SPY to 1.0 at each start date; this is a robustness diagnostic, not a promotion gate `[testing_tuning, p.327-335]`.
