# DATA_GATE — Iteracao 004 Carry/Trend FX

## Resultado

`FAIL` para data reliability. A Familia C nao foi backtestada.

## Criterio Pre-Registrado

O `PRE_REG.md` exigiu, antes de qualquer backtest, fonte confiavel e documentada de rates/carry por EUR, GBP, USD, JPY, CHF, CAD, AUD e NZD, com cobertura historica suficiente e sem derivar carry de PnL, retorno futuro ou proxy improvisado `[quant_trading_chan, ch.6]`.

## Verificacao Feita

Foram inspecionados artefatos e dados versionados no repo por nomes/conteudo relacionados a `carry`, `rates`, `interest`, `cash rate`, `policy rate`, `central bank`, `FRED` e equivalentes.

Achados:

- Existem dados de spot FX D1/H4 via Dukascopy BID nas iteracoes 001-003.
- Existem caches Tiingo/testfolio/ETF e algumas series macro antigas em outros estudos, mas nao uma matriz historica confiavel de policy/cash rates para as oito moedas do universo FX majors.
- Referencias a `carry` em estudos antigos sao qualitativas ou ligadas a bonds/portfolios, nao dataset de treino para FX carry.
- Nao ha historico broker-specific de swap/commission/carry; as iteracoes anteriores registram explicitamente que custos sao overlay de pesquisa, nao modelo deployavel.

## Decisao Conservadora

Sem fonte confiavel de rates/carry documentada antes do backtest, aciona-se K1 `NO_RELIABLE_CARRY_DATA`. A iteracao termina `inconclusive`, sem estrategia, sem baselines novos, sem PBO, sem bootstrap e sem cost stress aplicado.

Isto preserva o guardrail de nao improvisar proxy de carry e evita transformar retorno spot ou PnL futuro em sinal de carry `[quant_trading_chan, ch.6]`.
