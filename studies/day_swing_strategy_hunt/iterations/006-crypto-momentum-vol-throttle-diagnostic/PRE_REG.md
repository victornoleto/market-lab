# PRE_REG — Iteracao 006 Crypto Momentum Vol Throttle Diagnostic

## Hipotese

Familia E testa se BTCUSD/ETHUSD D1 tem momentum absoluto liquido que melhora perfil de risco quando a exposicao e reduzida em regimes de volatilidade extrema. Crypto pode ter momentum forte, mas volatilidade extrema exige throttle para evitar overbet `[volatility_trading, ch.2]`.

Este teste e crypto-only e, portanto, diagnostico apenas. Nenhum resultado em BTCUSD/ETHUSD pode virar winner sozinho; winner exigiria melhoria de portfolio multi-asset em iteracao futura, nunca crypto-only `[volatility_trading, ch.2]`.

## Universo

- BTCUSD
- ETHUSD

## Frequencia

D1 apenas. A frequencia diaria e congelada antes do teste para reduzir o dominio relativo de spread/slippage frente a horizontes intraday curtos `[systematic_trading, p.182-197]`.

## Dados Esperados

Dados Dukascopy BID D1 na janela disponivel comum 2018-01-01 a 2026-05-01. Data gate minimo: arquivo legivel, timestamps unicos, `close` nao ausente, e pelo menos 1000 barras por ativo.

## Custos Congelados

Custos round-trip iguais aos da iteracao 001 para D1 crypto, aplicados quando a posicao muda:

| Ativo | Base | Conservador | Stress |
|---|---:|---:|---:|
| BTCUSD | 10 bps | 25 bps | 50 bps |
| ETHUSD | 10 bps | 25 bps | 50 bps |

Sensibilidade a custos e obrigatoria porque custos e slippage podem dominar estrategias de maior turnover `[systematic_trading, p.182-197]`.

## Regra Congelada

Uma unica configuracao, sem grade:

- Momentum absoluto D1: retorno de 60 barras.
- Volatilidade realizada: desvio padrao anualizado dos retornos diarios em 20 barras.
- Percentil de volatilidade: ranking trailing de 252 barras da volatilidade realizada 20d.
- Sinal bruto por ativo: long se retorno 60d > 0; flat caso contrario.
- Throttle: exposicao 1.0 se percentil de volatilidade <= 80; exposicao 0.5 se percentil > 80; exposicao 0.0 se percentil > 95.
- Portfolio: equal-risk-naive por ativos ativos, com peso alvo bruto maximo 50% por ativo quando ambos ativos estao long; cash recebe o restante.
- Rebalance: diario no close D1.

Momentum e filtro de volatilidade sao escolhas pre-registradas da Familia E `[volatility_trading, ch.2]`. O lookback 60 D1 segue a familia de momentum ja permitida na spec, mas nao e escolhido por resultado da iteracao 002; e usado aqui como horizonte intermediario unico para evitar selecao entre configs `[systematic_trading, ch.10]`.

## Baselines Obrigatorios

Comparar contra:

- Buy-and-hold equal-weight BTCUSD/ETHUSD.
- Buy-and-hold por ativo.
- Always-flat.
- Uniform-frequency da iteracao 001, restrito a BTCUSD/ETHUSD D1 se disponivel.
- Random-entry matched-turnover da iteracao 001, restrito a BTCUSD/ETHUSD D1 se disponivel; se nao houver baseline diretamente reutilizavel, gerar random-entry com turnover/exposicao anual aproximados da estrategia e seed fixa antes do teste.

Controles uniformes/randomizados sao obrigatorios para separar edge de sorte amostral, exposicao mecanica ou reducao de turnover `[evidence_based_ta, p.247-260]`.

## Gates Minimos

- Data reliability: PASS antes de qualquer verdict economico.
- Cost stress: stress CAGR e Sharpe precisam permanecer positivos para qualquer leitura `positive` `[systematic_trading, p.182-197]`.
- OOS single-block: 2024-01-01 em diante, pre-registrado antes do teste `[advances_fin_ml, p.31-34]`.
- Bootstrap full: 99.9% CI low anualizado > 0 para leitura `positive` `[advances_fin_ml, p.31-34]`.
- Bootstrap OOS: 99.9% CI low anualizado > 0 para leitura `positive` `[advances_fin_ml, p.31-34]`.
- PBO: not applicable se somente a configuracao unica acima for rodada; se qualquer selecao entre configs ocorrer, PBO < 0.5 vira hard-block `[advances_fin_ml, p.208-211]`.

## Kill-Switches

- K1: dados crypto D1 nao confiaveis ou ausentes.
- K2: random-entry matched-turnover iguala ou supera a estrategia.
- K4: bootstrap OOS 99.9% low <= 0.
- K5: custo stress elimina edge.
- K6: melhor resultado vem de BTCUSD/ETHUSD crypto-only; registrar diagnostico apenas, sem winner.
- K9: edge depende apenas de reducao de exposicao/turnover sem filtro observavel pre-registrado.

## Verdicts

- `positive`: data gate passa, estrategia supera baselines principais em Sharpe liquido, stress positivo, bootstrap full/OOS positivos; ainda assim sem winner por ser crypto-only.
- `negative`: resultado economico fraco, mas nao conclusivo para matar a familia.
- `inconclusive`: dados/baselines indisponiveis ou amostra insuficiente.
- `dead-end`: falha clara em OOS/bootstrap/stress ou perde para controles obrigatorios; nao reabrir sem tese literaria nova e extensao multi-asset pre-registrada.
