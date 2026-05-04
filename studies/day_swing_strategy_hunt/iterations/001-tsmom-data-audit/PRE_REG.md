# PRE_REG — Iteracao 001 TSMOM Data Audit

## Hipotese

Familia A, Time-Series Momentum H4/D1, inicia apenas com auditoria de dados e baselines minimos. Nenhuma estrategia completa sera testada nesta iteracao. A tese futura e que trend following/time-series momentum pode capturar persistencia em mercados liquidos em horizontes intermediarios `[systematic_trading, ch.10]`.

## Citacoes

- Time-series momentum/trend following: `[systematic_trading, ch.10]`.
- Horizonte D1/H4 para reduzir dominio relativo de custos versus intraday curto: `[systematic_trading, p.182-197]`.
- Sizing inverse-vol fica permitido apenas para iteracoes futuras pre-registradas: `[systematic_trading, ch.12]`.
- Random-entry matched-turnover e controles sao obrigatorios para separar edge de sorte/turnover: `[evidence_based_ta, p.247-260]`.
- DSR/PBO/bootstrap sao gates hard-block quando aplicaveis: `[advances_fin_ml, p.31-34, p.196-211]`.

## Universo Congelado

- FX majors: EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD.
- Gold: XAUUSD.
- Crypto: BTCUSD, ETHUSD.

Qualquer resultado single-asset e diagnostico apenas; nao pode ser winner.

## Frequencias Congeladas

- D1.
- H4.

M1/M5 nao entram, exceto diagnostico futuro de execucao/custos.

## Dados Esperados

Auditar, antes de qualquer estrategia completa:

- Fonte disponivel no repo.
- Periodo por simbolo/frequencia.
- Timezone ou inferencia documentada.
- Numero de barras.
- Gaps relevantes.
- Colunas OHLCV ou equivalentes.
- Caveats de fonte.

Se nao houver dados D1/H4 suficientes para o universo multi-asset, parar com `inconclusive` ou `dead-end`; nao improvisar proxy.

## Custos Pre-Registrados

Custos sao aproximacoes de pesquisa para impedir alpha bruto ilusorio; devem ser revisados contra fonte broker antes de qualquer paper/live. Custos entram em bps round-trip sobre notional para baselines de controle e para qualquer estrategia futura `[systematic_trading, p.182-197]`.

| Classe | Base | Conservador | Stress |
|---|---:|---:|---:|
| FX majors | 2 bps | 5 bps | 10 bps |
| XAUUSD | 5 bps | 10 bps | 20 bps |
| BTCUSD/ETHUSD | 10 bps | 25 bps | 50 bps |

Swap/overnight nao sera modelado nesta iteracao por falta de fonte broker por data. Isto bloqueia qualquer conclusao deployavel.

## Parametros E Grade Congelados

Sem grade de estrategia nesta iteracao. Para baselines:

- Buy-and-hold: long-only por asset e portfolio equal-weight rebalanceado por barra disponivel.
- Always-flat: retorno zero.
- Uniform-frequency control: posicao long equal-weight em agenda mecanica sem sinal, com hold fixo pre-registrado de 20 barras por frequencia para criar turnover observavel `[evidence_based_ta, p.247-260]`.
- Random-entry matched-turnover: mesmo numero de entradas do uniform-frequency control, sinais aleatorios gerados com seed fixa 20260503, 200 simulacoes, hold de 20 barras, long/flat equal-weight `[evidence_based_ta, p.247-260]`.

## Baselines Obrigatorios

- Buy-and-hold por asset.
- Buy-and-hold equal-weight multi-asset.
- Always-flat.
- Random-entry matched-turnover.
- Uniform-frequency control.

## Gates Obrigatorios Nesta Iteracao

- K1 dados/custos confiaveis: se falhar, parar.
- Baselines devem ser calculaveis sem lookahead.
- Nenhum winner pode ser declarado.

DSR, PBO, WF, OOS bootstrap e cross-lib sanity nao sao aplicaveis ainda porque nao ha estrategia nem selecionador nesta iteracao; permanecem obrigatorios para iteracoes futuras `[advances_fin_ml, p.31-34, p.196-211]`.

## Kill-Switches Relevantes

- K1: dados/custos nao confiaveis.
- K6: melhor resultado single-asset e diagnostico apenas.
- K8: proibido oracle/top-K ex-post.
- K9: proibido edge por reduzir turnover sem filtro observavel pre-registrado.

## Verdicts

- `positive`: dados D1/H4 multi-asset suficientes e baselines minimos gravados.
- `inconclusive`: dados parciais permitem auditoria mas nao universo/frequencias suficientes para seguir.
- `dead-end`: fonte essencial ausente ou custos impossiveis de documentar sem improviso.
- `negative`: baselines prontos mostram que a proxima estrategia precisara superar controles fortes, mas sem bloquear a familia ainda.
