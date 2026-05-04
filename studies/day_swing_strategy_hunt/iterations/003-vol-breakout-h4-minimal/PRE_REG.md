# PRE_REG — Iteracao 003 Volatility Breakout H4 Minimal

## Hipotese

Familia B, Volatility Breakout H4 minima. A tese e que rompimentos de canais apos expansao de range podem capturar movimentos direcionais, mas precisam ser testados contra falsos rompimentos, churn e custo de transacao `[trading_systems_methods, ch.14]`. A frequencia H4 e escolhida por ser horizonte day/swing permitido sem cair em microestrutura M1/M5, embora continue sensivel a custos `[systematic_trading, p.182-197]`.

Esta iteracao nao usa qualquer ajuste derivado do resultado TSMOM D1 da iteracao 002.

## Citacoes

- Canais Donchian, breakout de maxima/minima, filtro ATR e saidas por canal/time stop: `[trading_systems_methods, ch.14]`.
- Frequencia H4 e sensibilidade a spread/slippage/turnover: `[systematic_trading, p.182-197]`.
- Baselines random-entry matched-turnover e uniform-frequency para separar edge de sorte/churn: `[evidence_based_ta, p.247-260]`.
- OOS single-block, bootstrap full/OOS, DSR e PBO como controles anti-overfit quando ha selecao entre configs: `[advances_fin_ml, p.31-34, p.196-211]`.

## Universo Congelado

- FX majors: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD.
- Gold: XAUUSD.
- Crypto: BTCUSD, ETHUSD.

Qualquer melhor resultado single-asset e diagnostico apenas; nao pode ser winner.

## Frequencia Congelada

- H4 somente.

M1/M5 nao entram, exceto diagnostico futuro de execucao/custos.

## Dados Esperados

Fonte: Dukascopy BID via `dukascopy-python`, janela fixa 2018-01-01 a 2026-05-01, a mesma auditada na iteracao 001. Se algum simbolo H4 essencial nao retornar OHLC suficiente, marcar `inconclusive` ou `dead-end`; nao improvisar proxy.

Caveat pre-registrado: BID-only, sem historico broker-specific de swap/commission; custos sao overlay de pesquisa, nao modelo deployavel.

## Custos Pre-Registrados

Custos iguais aos da iteracao 001, em bps round-trip sobre notional. H4 e sensivel a custos e turnover; portanto stress de spread/slippage e gate hard-block `[systematic_trading, p.182-197]`.

| Classe | Base | Conservador | Stress |
|---|---:|---:|---:|
| FX majors | 2 bps | 5 bps | 10 bps |
| XAUUSD | 5 bps | 10 bps | 20 bps |
| BTCUSD/ETHUSD | 10 bps | 25 bps | 50 bps |

Swap/overnight nao sera modelado por falta de fonte broker por data. Isto bloqueia qualquer conclusao deployavel.

## Parametros E Grade Congelados

Grade minima, sem ajuste apos ver resultado:

| Parametro | Valores |
|---|---|
| Canal Donchian | 20, 55 barras `[trading_systems_methods, ch.14]` |
| ATR lookback | mesmo comprimento do canal `[trading_systems_methods, ch.14]` |
| Filtro ATR | percentil historico de ATR > 50 ou > 70, usando apenas dados passados `[trading_systems_methods, ch.14]` |
| Direcao | long em rompimento da maxima do canal; short em rompimento da minima do canal `[trading_systems_methods, ch.14]` |
| Entrada | sinal calculado com canal deslocado uma barra, execucao no retorno da proxima barra para evitar lookahead |
| Saida | canal oposto; sem holding fixo nesta iteracao para manter a variante minima pre-registrada `[trading_systems_methods, ch.14]` |
| Sizing | posicao -1/0/+1 por ativo, equal-weight no portfolio; sem vol target nesta iteracao |

Configuracoes congeladas: 4 variantes = canal 20/55 x ATR p50/p70. Se houver selecao por Sharpe entre essas variantes, aplicar PBO `[advances_fin_ml, p.208-211]`.

## Baselines Obrigatorios

Comparar cada variante contra baselines H4 da iteracao 001 `[evidence_based_ta, p.247-260]`:

- Buy-and-hold por asset e equal-weight multi-asset.
- Always-flat.
- Uniform-frequency control.
- Random-entry matched-turnover.

Para random-entry matched-turnover da estrategia, gerar controle com mesmo numero de entradas por ativo da variante selecionada, seed fixa 20260503, 200 simulacoes, e hold medio aproximado pelo periodo medio das trades da estrategia, limitado a minimo 1 barra.

## Gates Obrigatorios Nesta Iteracao

- K1 dados H4 disponiveis para o universo congelado.
- Cost stress: CAGR e Sharpe do portfolio selecionado permanecem positivos sob stress `[systematic_trading, p.182-197]`.
- OOS single-block pre-registrado: 2024-01-01 em diante, CAGR e Sharpe positivos `[advances_fin_ml, p.31-34]`.
- Bootstrap full 99.9%: `ci_low > 0` para media anualizada `[advances_fin_ml, p.31-34]`.
- Bootstrap OOS 99.9%: `ci_low > 0` para media anualizada `[advances_fin_ml, p.31-34]`.
- PBO < 0.5 se houver selecao entre as 4 configs `[advances_fin_ml, p.208-211]`.
- Bater buy-and-hold equal-weight H4 em Sharpe base.
- Bater random-entry matched-turnover equal-weight H4 em Sharpe base.
- Bater random-entry em pelo menos 2 classes de ativos.
- Nao declarar winner se o melhor resultado vier de um unico asset.

DSR fica registrado como aplicavel em tese por haver multiplas configs, mas esta iteracao minima usa PBO como gate computado principal; se DSR nao for calculado, `RESULTS.json` deve marcar explicitamente `not_computed_minimal_scope`.

## Kill-Switches Relevantes

- K1: dados/custos nao confiaveis.
- K2: baseline random-entry iguala ou supera a estrategia.
- K3: PBO >= 0.5.
- K4: bootstrap OOS 99.9% low <= 0.
- K5: edge some em custo stress.
- K6: melhor resultado e single-asset; diagnostico apenas.
- K8: proibido oracle/top-K ex-post.
- K9: proibido edge por reduzir turnover sem filtro observavel pre-registrado.

## Verdicts

- `positive`: todos os gates minimos passam no portfolio multi-asset, sem dependencia single-asset e sem paper/live.
- `negative`: a estrategia roda, mas falha gates nao estruturais ou fica abaixo de baselines.
- `inconclusive`: dados/fonte impedem teste honesto do universo congelado.
- `dead-end`: falha PBO, OOS bootstrap, random-entry, custo stress estrutural ou evidencia de que a Familia B minima nao deve ser reaberta sem tese nova.
