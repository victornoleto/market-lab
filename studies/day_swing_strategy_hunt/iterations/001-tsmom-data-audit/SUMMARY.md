# SUMMARY — Iteracao 001 TSMOM Data Audit

## Verdict

`positive` para escopo de auditoria/baselines. Nao ha winner, nao ha estrategia completa e nao ha autorizacao de paper/live.

## O Que Foi Testado

Foi feito apenas o `DATA_AUDIT` e os baselines minimos pre-registrados para a Familia A, Time-Series Momentum H4/D1. A estrategia TSMOM em si ficou para iteracao futura, conforme tese de trend following `[systematic_trading, ch.10]` e escolha de frequencias D1/H4 para reduzir dominio relativo de custos `[systematic_trading, p.182-197]`.

Baselines calculados:

- Buy-and-hold por asset e equal-weight multi-asset.
- Always-flat.
- Uniform-frequency control com hold mecanico de 20 barras.
- Random-entry matched-turnover com 200 simulacoes e seed fixa 20260503 `[evidence_based_ta, p.247-260]`.

## Dados Usados E Caveats

Fonte: Dukascopy BID via `dukascopy-python`, janela fixa 2018-01-01 a 2026-05-01, simbolos EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, XAUUSD, BTCUSD e ETHUSD.

Todos os 20 pares simbolo/frequencia retornaram dados:

- D1: 2.593 a 2.987 barras por ativo.
- H4: 13.323 a 17.486 barras por ativo.
- Timezone: requisitado em UTC; timestamps retornados pelo provider.
- Caveat principal: BID-only, sem historico broker-specific de swap/commission; custos sao overlay de pesquisa, nao modelo deployavel.
- O primeiro fetch tentou usar o loader mensal cacheado e excedeu 15 minutos; o script final usa chamadas diretas por simbolo/frequencia e nao grava cache OHLC.

## Comparacao Contra Baselines

Portfolio equal-weight, custos base:

| Frequencia | Baseline | CAGR | Sharpe | MDD |
|---|---:|---:|---:|---:|
| D1 | Buy-and-hold EW | 14.19% | 0.807 | -32.79% |
| D1 | Uniform-frequency EW | 5.45% | 0.489 | -28.50% |
| D1 | Random-entry EW mean | 6.44% | 0.711 | -18.61% |
| H4 | Buy-and-hold EW | 12.29% | 0.590 | -41.58% |
| H4 | Uniform-frequency EW | 3.34% | 0.300 | -28.08% |
| H4 | Random-entry EW mean | 2.74% | 0.278 | -27.53% |

Sob custo stress, H4 random/uniform ficaram negativos, reforcando que qualquer H4 futuro precisa superar custos e controles de turnover antes de gates estatisticos `[systematic_trading, p.182-197]`.

## Gates Pass/Fail

- K1 dados disponiveis: PASS para auditoria D1/H4.
- Baselines sem lookahead: PASS pelo escopo mecanico pre-registrado.
- DSR/PBO/WF/OOS bootstrap: nao aplicavel nesta iteracao porque nao houve estrategia nem selecionador; continuam hard-block futuros `[advances_fin_ml, p.31-34, p.196-211]`.
- No-winner: PASS.

## Kill-Switches

Nenhum kill-switch acionado. K6 permanece relevante: qualquer resultado single-asset futuro sera diagnostico, nao winner.

## Licao Para A Proxima Sessao

Dados D1/H4 existem para o universo inicial e baselines estao gravados. A iteracao 002 pode testar a estrategia minima TSMOM D1 com lookbacks pre-registrados 20/60/120, comparando contra estes baselines, sem otimizar thresholds depois de ver resultado.
