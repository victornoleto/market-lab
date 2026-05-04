# SUMMARY — Iteracao 004 Carry/Trend FX Data Gate

## Verdict

`inconclusive`. A Familia C Carry/Trend FX nao foi backtestada porque nao havia dados confiaveis de rates/carry documentados antes do teste. Nao ha winner, nao ha paper/live e nenhum resultado single-asset foi aceito.

## O Que Foi Testado

Foi testado apenas o data gate pre-registrado. A hipotese Carry/Trend FX so poderia rodar se existisse fonte historica confiavel de carry/rates para EUR, GBP, USD, JPY, CHF, CAD, AUD e NZD; sem isso, o protocolo mandava parar sem estrategia `[quant_trading_chan, ch.6]`.

Se o gate passasse, a regra congelada usaria tendencia D1 60 ou 120 barras e posicao apenas quando carry estivesse alinhado com tendencia `[quant_trading_chan, ch.6]`. Essa regra nao foi executada.

## Dados Usados E Caveats

Nao houve dados de estrategia usados. A verificacao encontrou spot FX D1/H4 via Dukascopy BID das iteracoes 001-003, caches Tiingo/testfolio/ETF e referencias qualitativas a carry/rates em estudos antigos, mas nao uma matriz historica confiavel de policy/cash rates ou carry para as oito moedas exigidas.

Caveat importante: spot FX, retorno passado ou PnL futuro nao foram usados como proxy de carry. Essa escolha preserva o guardrail de nao improvisar proxy e evita lookahead/selecionador ex-post `[quant_trading_chan, ch.6]`.

## Comparacao Contra Baselines

Nao aplicavel. Como o data reliability gate falhou antes do backtest, nao foram rodados buy-and-hold, always-flat, uniform-frequency ou random-entry matched-turnover novos. Os baselines da iteracao 001 permanecem referencia para iteracoes que tenham dados validos `[evidence_based_ta, p.247-260]`.

## Gates Pass/Fail

| Gate | Resultado |
|---|---|
| Data reliability | FAIL; sem rates/carry confiavel para o universo FX majors |
| Cost stress | NOT_RUN; bloqueado por data reliability `[systematic_trading, p.182-197]` |
| OOS single-block 2024+ | NOT_RUN; bloqueado por data reliability `[advances_fin_ml, p.31-34]` |
| Bootstrap full | NOT_RUN; bloqueado por data reliability `[advances_fin_ml, p.31-34]` |
| Bootstrap OOS | NOT_RUN; bloqueado por data reliability `[advances_fin_ml, p.31-34]` |
| PBO | NOT_APPLICABLE; nenhuma selecao entre configs foi rodada `[advances_fin_ml, p.208-211]` |
| No single-asset winner | PASS; nenhum winner declarado |

## Kill-Switches Acionados

- K1 `NO_RELIABLE_CARRY_DATA`: ausencia de dados historicos confiaveis de rates/carry antes do backtest `[quant_trading_chan, ch.6]`.

## Licao Para A Proxima Sessao

Carry/Trend FX fica data-blocked ate existir dataset confiavel de rates/carry por moeda. Nao reabrir a Familia C com proxy improvisado, spot-only ou filtro calibrado por resultado. A proxima iteracao deve mudar para uma familia independente pre-registrada, preservando D1/H4 e os controles estatisticos minimos.
