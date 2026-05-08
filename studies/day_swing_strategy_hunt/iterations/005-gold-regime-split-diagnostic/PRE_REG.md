# PRE_REG — Iteracao 005 Gold Regime Split Diagnostic

## Hipotese

Familia D, Gold Regime Trend/MR Split, testada apenas como diagnostico XAUUSD-only. A tese e que mercados alternam entre regimes de tendencia e range, entao uma regra minima deve escolher modo trend ou mean-reversion antes de observar resultados `[trading_systems_methods, p.13-14]`.

Este teste nao pode declarar winner. Qualquer resultado positivo em XAUUSD e diagnostico apenas; um winner exigiria melhoria futura em portfolio multi-asset, nunca single-asset `[trading_systems_methods, p.13-14]`.

## Citacoes

- Separacao pre-definida de regimes por tendencia e volatilidade: `[trading_systems_methods, p.13-14]`.
- Frequencia D1 para reduzir dominio relativo de custos em comparacao com horizontes intraday curtos: `[systematic_trading, p.182-197]`.
- Custos base/conservador/stress precisam ser testados porque custos podem eliminar alpha aparente em CFD short-hold: `[systematic_trading, p.182-197]`.
- Buy-and-hold, always-flat, uniform-frequency e random-entry matched-turnover sao controles obrigatorios contra sorte e turnover mecanico: `[evidence_based_ta, p.247-260]`.
- OOS single-block, bootstrap full/OOS e PBO quando houver selecao entre configs sao gates anti-overfit obrigatorios: `[advances_fin_ml, p.31-34, p.196-211]`.

## Universo Congelado

- XAUUSD apenas.

Restricao: XAUUSD-only e diagnostico. Nenhum resultado single-asset pode virar winner, paper ou live.

## Frequencia Congelada

- D1 apenas.

Justificativa: D1 reduz churn e dominio relativo de spread/slippage vs H4/M1/M5, preservando o objetivo de day/swing sem microestrutura curta `[systematic_trading, p.182-197]`.

## Dados Esperados

- Fonte: dados OHLC de XAUUSD ja auditados no loop, preferencialmente Dukascopy BID usado nas iteracoes 001-003.
- Janela minima esperada: 2018-01-01 a 2026-05-01, conforme auditoria da iteracao 001.
- Colunas minimas: timestamp/date, open, high, low, close.

Se XAUUSD D1 nao estiver legivel ou tiver lacunas impeditivas, parar com `inconclusive` sem backtest.

## Custos Pre-Registrados

Custos iguais aos da iteracao 001, em bps round-trip sobre notional `[systematic_trading, p.182-197]`.

| Classe | Base | Conservador | Stress |
|---|---:|---:|---:|
| XAUUSD | 5 bps | 10 bps | 20 bps |

Swap/overnight nao sera modelado por falta de fonte broker por data; isso bloqueia qualquer conclusao deployavel.

## Regra De Regime Congelada

Sem grade de parametros. Uma unica regra sera testada para evitar selecao ex-post:

- Tendencia D1: `close > SMA(100)` e retorno de 100 barras positivo define viés de tendencia; `close < SMA(100)` e retorno de 100 barras negativo define viés de queda; demais casos sao neutros `[trading_systems_methods, p.13-14]`.
- Volatilidade/ATR: calcular ATR(14) dividido pelo close e seu percentil trailing de 252 barras. Percentil >= 60 define regime trend-capable; percentil <= 40 define regime range; percentis intermediarios ficam flat `[trading_systems_methods, p.13-14]`.
- Modo trend: se regime trend-capable e viés de tendencia positivo, ficar long; se viés negativo, ficar short; caso contrario flat `[trading_systems_methods, p.13-14]`.
- Modo range: se regime range e o close estiver abaixo da banda inferior `SMA(20) - 1 * ATR(14)`, ficar long; se estiver acima da banda superior `SMA(20) + 1 * ATR(14)`, ficar short; caso contrario flat `[trading_systems_methods, p.13-14]`.
- Execucao: sinal calculado no fechamento D1 e aplicado na proxima barra, sem lookahead.
- Sizing: 100% notional long/short/flat, sem alavancagem e sem vol target nesta iteracao.

## Baselines Obrigatorios

Comparar contra os controles da iteracao 001, recalculados ou reutilizados para XAUUSD D1 quando necessario `[evidence_based_ta, p.247-260]`:

- Buy-and-hold XAUUSD D1 long-only.
- Always-flat.
- Uniform-frequency control: agenda mecanica long/flat com hold fixo de 20 barras, como iteracao 001.
- Random-entry matched-turnover: mesmo numero de entradas/turnover da estrategia, seed fixa 20260503, 200 simulacoes, hold/posicoes matched quando cabivel.

## Gates Obrigatorios Nesta Iteracao

- Data reliability: XAUUSD D1 precisa estar legivel, sem gaps impeditivos, e com janela suficiente.
- Cost stress: resultado precisa permanecer positivo sob custo stress para ser diagnostico positivo `[systematic_trading, p.182-197]`.
- OOS single-block: bloco OOS pre-registrado de 2024-01-01 em diante `[advances_fin_ml, p.31-34]`.
- Bootstrap full: CI 99.9% low anualizado precisa ser > 0 para passar `[advances_fin_ml, p.31-34]`.
- Bootstrap OOS: CI 99.9% low anualizado precisa ser > 0 para passar `[advances_fin_ml, p.31-34]`.
- PBO: nao aplicavel se apenas uma configuracao congelada for executada; se qualquer selecao entre configs ocorrer por acidente, calcular PBO e nao aceitar resultado com PBO >= 0.5 `[advances_fin_ml, p.208-211]`.
- No single-asset winner: sempre PASS apenas se nenhum winner for declarado.

## Kill-Switches Relevantes

- K1: dados/custos nao confiaveis.
- K2: random-entry matched-turnover iguala ou supera a estrategia.
- K4: OOS bootstrap low <= 0.
- K5: edge some em custo stress.
- K6: melhor resultado e single-asset; diagnostico apenas, sem deploy.
- K8: proibido oracle/top-K ex-post.
- K9: proibido edge por reduzir turnover sem filtro observavel pre-registrado.

## Verdicts

- `positive`: estrategia XAUUSD D1 passa data reliability, custo stress, baselines, bootstrap full/OOS e fica registrada como diagnostico promissor, sem winner.
- `negative`: estrategia roda, mas fica abaixo de baselines ou perde edge em custos, sem fechar necessariamente a familia.
- `inconclusive`: dados insuficientes, falha operacional ou resultado nao permite conclusao limpa.
- `dead-end`: regra minima falha gates estatisticos/custos de forma clara; nao reabrir com ajuste de thresholds derivados deste resultado.
