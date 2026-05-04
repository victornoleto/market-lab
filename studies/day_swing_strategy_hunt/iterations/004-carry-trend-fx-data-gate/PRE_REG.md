# PRE_REG — Iteracao 004 Carry/Trend FX Data Gate

## Hipotese

Familia C testa apenas a viabilidade de uma regra FX Carry/Trend. FX pode combinar diferencial de juros/carry com tendencia, mas carry isolado pode sofrer reversoes abruptas; por isso a posicao so pode existir quando carry e tendencia estiverem alinhados `[quant_trading_chan, ch.6]`.

Esta iteracao tem um data gate hard-block: a estrategia so pode ser backtestada se dados confiaveis de carry/rates estiverem disponiveis e documentados antes do backtest. Nao sera improvisado proxy de carry, nao sera usado resultado de TSMOM D1 ou Vol Breakout H4 para ajustar parametros, e ausencia de dados confiaveis implica verdict `inconclusive` sem backtest `[quant_trading_chan, ch.6]`.

## Universo Congelado

FX majors somente:

| Simbolo | Par |
|---|---|
| EURUSD | EUR/USD |
| GBPUSD | GBP/USD |
| USDJPY | USD/JPY |
| USDCHF | USD/CHF |
| USDCAD | USD/CAD |
| AUDUSD | AUD/USD |
| NZDUSD | NZD/USD |

Single-asset winner nao pode ser aceito; qualquer destaque por par isolado e diagnostico apenas.

## Frequencia E Janela

- Preco: D1, por ser horizonte swing e menos dominado por custos de execucao que intraday curto `[systematic_trading, p.182-197]`.
- Rebalance: diario, somente se o data gate passar `[quant_trading_chan, ch.6]`.
- OOS single-block: bloco final 2024-01-01 em diante, congelado antes do teste `[advances_fin_ml, p.31-34]`.

## Data Gate De Carry/Rates

Antes do backtest, deve existir fonte confiavel e documentada de rates/carry por moeda base/quote, com cobertura historica suficiente para EUR, GBP, USD, JPY, CHF, CAD, AUD e NZD.

Dados aceitaveis:

- Series historicas oficiais ou institucionais de juros/cash rates por moeda.
- Dados ja versionados no repo ou baixaveis de fonte reprodutivel sem depender de resultado de estrategia.
- Cobertura temporal alinhada ao periodo de precos D1 usado.
- Sem derivar carry de PnL, retorno futuro, ranking ex-post ou ajuste calibrado apos ver resultado.

Se esses criterios nao forem satisfeitos, parar a iteracao com `inconclusive`; nao rodar estrategia, baselines novos, PBO, bootstrap ou cost stress.

## Regra Congelada Se O Data Gate Passar

Parametros permitidos:

| Elemento | Valor Congelado |
|---|---|
| Trend filter | D1 60 ou 120 barras `[quant_trading_chan, ch.6]` |
| Carry signal | Diferencial de juros confiavel documentado antes do backtest `[quant_trading_chan, ch.6]` |
| Posicao | Long quando carry estiver positivo para a direcao do par e tendencia 60/120 barras confirmar; short quando carry estiver positivo para a direcao inversa e tendencia confirmar; flat quando desalinhado `[quant_trading_chan, ch.6]` |
| Selecionador | Se 60 e 120 forem ambos testados, melhor config por Sharpe full pre-cost/base sera apenas selecionador de pesquisa e exigira PBO `[advances_fin_ml, p.208-211]` |

## Custos Congelados

Usar os mesmos cenarios base, conservador e stress documentados na iteracao 001. A sensibilidade a custos e obrigatoria porque spread/slippage/swap podem dominar estrategias CFD de curto prazo `[systematic_trading, p.182-197]`.

Se o data gate passar, copiar para `RESULTS.json` os nomes dos cenarios de custo da iteracao 001 e aplicar a mesma convencao de custo por trade/turnover. Se o data gate falhar, registrar que os custos foram pre-registrados mas nao aplicados.

## Baselines Obrigatorios Se O Data Gate Passar

Comparar contra os controles da iteracao 001, sem escolher baseline ex-post `[evidence_based_ta, p.247-260]`:

- Buy-and-hold equal-weight FX majors.
- Always-flat.
- Uniform-frequency control.
- Random-entry matched-turnover.

## Gates Obrigatorios

| Gate | Regra |
|---|---|
| Data reliability | PASS somente se rates/carry forem confiaveis e documentados antes do backtest `[quant_trading_chan, ch.6]` |
| Cost stress | Resultado permanece positivo sob custo stress `[systematic_trading, p.182-197]` |
| OOS single-block | Bloco 2024-01-01 em diante positivo em ponto estimado `[advances_fin_ml, p.31-34]` |
| Bootstrap full | CI 99.9% low > 0 `[advances_fin_ml, p.31-34]` |
| Bootstrap OOS | CI 99.9% low > 0 no bloco OOS `[advances_fin_ml, p.31-34]` |
| PBO | Aplicar se houver selecao entre 60 e 120 barras; exigir PBO < 0.5 `[advances_fin_ml, p.208-211]` |
| Baselines | Bater buy-and-hold, always-flat, uniform-frequency e random-entry matched-turnover em Sharpe/retorno liquido cabivel `[evidence_based_ta, p.247-260]` |
| No single-asset winner | Melhor resultado por par isolado nao autoriza winner |

## Kill-Switches

- K1 `NO_RELIABLE_CARRY_DATA`: parar sem backtest e verdict `inconclusive`.
- K2 `COST_STRESS_FAIL`: se dados passarem mas custo stress eliminar edge, verdict `dead-end`.
- K3 `PBO_GE_0_5`: se houver selecao entre configs e PBO falhar, verdict `dead-end`.
- K4 `OOS_BOOTSTRAP_LOW_LE_0`: se OOS bootstrap low cruzar zero, verdict `dead-end`.
- K6 `SINGLE_ASSET_ONLY`: diagnostico apenas, sem winner.

## Criterios De Verdict

- `positive`: data gate passa e a regra multi-asset passa todos os gates minimos; nao autoriza paper/live.
- `negative`: data gate passa, mas a regra e fraca antes de gates estatisticos profundos.
- `inconclusive`: data gate falha por ausencia de dados confiaveis de rates/carry antes do backtest.
- `dead-end`: data gate passa, mas qualquer hard gate falha.

Capital permanece 100% Plano C; Plano A permanece DORMANT; sem paper/live; sem tocar `docs/investment-mandate.md` ou `frozen_rules/`.
