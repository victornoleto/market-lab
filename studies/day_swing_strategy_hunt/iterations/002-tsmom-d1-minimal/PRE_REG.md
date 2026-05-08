# PRE_REG — Iteracao 002 TSMOM D1 Minimal

Criado antes de qualquer teste desta iteracao. Estudo research-only; nao autoriza capital, paper trading ou live trading.

## Hipotese

Time-Series Momentum D1 long/flat simples pode gerar sinal multi-asset liquido acima dos baselines mecanicos da iteracao 001. A tese e trend following em horizontes intermediarios `[systematic_trading, ch.10]`, usando D1 para reduzir o peso relativo de custo/friccao `[systematic_trading, p.182-197]`.

## Universo Congelado

EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, XAUUSD, BTCUSD, ETHUSD.

Multi-asset e obrigatorio para qualquer leitura positiva; melhor asset isolado e apenas diagnostico, nunca winner.

## Dados E Frequencia

- Fonte: Dukascopy BID via `dukascopy-python`, mesma janela da iteracao 001: 2018-01-01 a 2026-05-01.
- Frequencia: D1 apenas.
- Caveat: BID-only, sem historico broker-specific de swap/commission; custos sao overlay de pesquisa.

## Custos Congelados

Mesmo modelo da iteracao 001, em custo proporcional por mudanca de posicao `[systematic_trading, p.182-197]`:

| Classe | Base | Conservador | Stress |
|---|---:|---:|---:|
| FX | 2 bps | 5 bps | 10 bps |
| XAU | 5 bps | 10 bps | 20 bps |
| Crypto | 10 bps | 25 bps | 50 bps |

## Regra Congelada

Para cada ativo e lookback `L` em 20, 60, 120 barras `[systematic_trading, ch.10]`:

- Calcular retorno de close D1 sobre `L` barras.
- Posicao long = 1 se retorno de lookback > 0; flat = 0 caso contrario.
- Sinal aplicado na barra seguinte via posicao defasada em 1 barra; sem lookahead.
- Sem threshold otimizado e sem short.
- Portfolio equal-weight = media simples dos retornos dos 10 streams por data.

## Parametros Congelados

- Lookbacks: 20, 60, 120.
- Frequencia: D1.
- Sizing: 1/N equal-weight entre ativos disponiveis; sem vol target nesta iteracao `[systematic_trading, ch.12]`.
- OOS single-block: 2024-01-01 ate fim da amostra; treino/IS antes de 2024 apenas para comparacao, nao para otimizar threshold `[advances_fin_ml, p.31-34]`.
- Bootstrap: 2.000 amostras com seed 20260503; criterio CI 99.9% low > 0 para media de retorno anualizada full e OOS `[advances_fin_ml, p.31-34]`.

## Baselines Obrigatorios

Comparar cada variante contra baselines D1 da iteracao 001 `[evidence_based_ta, p.247-260]`:

- Buy-and-hold por asset e equal-weight.
- Always-flat.
- Uniform-frequency control.
- Random-entry matched-turnover.

## Gates Obrigatorios

- Cost stress: melhor variante pre-registrada precisa manter retorno/Sharpe liquido positivo sob stress `[systematic_trading, p.182-197]`.
- OOS single-block: OOS precisa ter CAGR e Sharpe positivos, sem reinterpretar janela apos resultado `[advances_fin_ml, p.31-34]`.
- Full bootstrap: CI 99.9% low anualizado > 0 `[advances_fin_ml, p.31-34]`.
- OOS bootstrap: CI 99.9% low anualizado > 0 `[advances_fin_ml, p.31-34]`.
- PBO: aplicar sobre a grade congelada de 3 lookbacks; PBO < 0.5 para qualquer selecao entre lookbacks `[advances_fin_ml, p.208-211]`.
- Baseline superiority: portfolio deve bater buy-and-hold EW e random-entry matched-turnover EW por Sharpe liquido no cenario base; por asset, sinal precisa superar random-entry em pelo menos 2 classes de ativos para nao acionar kill especifico da Familia A.

## Kill-Switches Relevantes

- K1: dados/custos D1 indisponiveis ou inconsistentes.
- K2: random-entry matched-turnover iguala ou supera a estrategia no portfolio.
- K3: PBO >= 0.5.
- K4: OOS bootstrap low <= 0.
- K5: edge some em stress.
- K6: melhor leitura depende de single-asset.
- K8: qualquer dependencia de oracle/top-K por PnL futuro.
- K9: edge depende apenas de reduzir turnover sem filtro observavel.

## Verdicts

- `positive`: portfolio multi-asset passa cost stress, OOS, bootstrap full/OOS, PBO e supera buy-and-hold/random-entry em Sharpe base; sem dependencia single-asset.
- `negative`: regra roda, mas falha um ou mais gates sem matar toda a Familia A.
- `inconclusive`: provider/dados impedem conclusao ou gates ficam estatisticamente indeterminados por amostra insuficiente.
- `dead-end`: Familia A D1 minima falha por PBO >= 0.5, random-entry domina, stress elimina edge, ou sinal depende apenas de single-asset.
