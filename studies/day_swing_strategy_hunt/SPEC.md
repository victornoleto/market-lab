# SPEC — Day/Swing Strategy Hunt

Status: bootstrap. Esta spec define o contrato inicial do loop. Ela nao autoriza capital, paper trading ou live trading.

## Mandato Operacional

- Plano A permanece DORMANT e com 0% de capital.
- Capital permanece 100% Plano C.
- O estudo e research-only.
- Nao modificar `docs/investment-mandate.md`.
- Nao modificar `frozen_rules/`.
- Toda escolha de estrategia, indicador, parametro ou gate precisa de citacao no formato `[book.slug, p.X]` ou `[book.slug, ch.Y]`.

## Universo Inicial

| Classe | Simbolos |
|---|---|
| FX majors | EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD |
| Gold | XAUUSD |
| Crypto | BTCUSD, ETHUSD |

Multi-asset e obrigatorio para qualquer candidato deployavel porque single-asset edge nao e aceito pelo mandato. XAU-only ou crypto-only pode existir apenas como diagnostico.

## Frequencias Permitidas

| Frequencia | Status | Motivo |
|---|---|---|
| D1 | Permitida no ciclo inicial | Swing primeiro reduz dominio relativo de custos `[systematic_trading, p.182-197]`. |
| H4 | Permitida no ciclo inicial | Horizonte principal de day/swing sem cair em microestrutura curta `[systematic_trading, p.182-197]`. |
| H1 | Adiada | So entra se H4/D1 mostrarem sinal e custos suportarem stress `[systematic_trading, p.182-197]`. |
| M1/M5 | Proibidas, exceto diagnostico | Usar apenas para diagnostico de execucao/custos, nao para treino ou hunt inicial. |

## Familias Candidatas Iniciais

### A. Time-Series Momentum H4/D1

Tese: trend following/time-series momentum e uma das anomalias mais robustas em mercados liquidos e horizontes intermediarios `[systematic_trading, ch.10]`.

Grade inicial permitida, sempre pre-registrada:

| Parametro | Valores |
|---|---|
| Lookback | 20, 60, 120 barras `[systematic_trading, ch.10]` |
| Frequencia | H4, D1 `[systematic_trading, p.182-197]` |
| Entrada | retorno do lookback > 0 `[systematic_trading, ch.10]` |
| Saida | sinal cruza 0 ou time stop pre-registrado `[systematic_trading, ch.10]` |
| Sizing | sem vol target ou inverse-vol pre-registrado `[systematic_trading, ch.12]` |

Kill especifico: se nao bater buy-and-hold e random-entry matched-turnover por Sharpe liquido em pelo menos 2 classes de ativos, encerrar a familia.

### B. Volatility Breakout H4

Tese: expansao de range apos compressao pode capturar movimentos direcionais, mas breakouts exigem teste honesto de falsos rompimentos, custos e churn `[trading_systems_methods, ch.14]`.

Grade inicial permitida, sempre pre-registrada:

| Parametro | Valores |
|---|---|
| Canal | Donchian 20, 55 barras `[trading_systems_methods, ch.14]` |
| Filtro ATR | percentil ATR > 50 ou > 70 `[trading_systems_methods, ch.14]` |
| Direcao | rompimento de maxima/minima do canal `[trading_systems_methods, ch.14]` |
| Saida | canal oposto ou holding fixo pre-registrado `[trading_systems_methods, ch.14]` |
| Frequencia | H4 `[systematic_trading, p.182-197]` |

Kill especifico: se turnover/custos eliminarem o edge no stress de spread/slippage 2x, encerrar a familia.

### C. Carry/Trend FX

Tese: FX pode combinar tendencia com diferencial de juros/carry; carry isolado pode sofrer reversoes abruptas, entao o filtro de tendencia deve ser pre-registrado `[quant_trading_chan, ch.6]`.

Restricao: so testar se houver dados confiaveis de carry/rates. Nao improvisar proxy.

Parametros iniciais permitidos:

| Parametro | Valores |
|---|---|
| Assets | FX majors somente |
| Trend filter | D1 60 ou 120 barras `[quant_trading_chan, ch.6]` |
| Carry proxy | differential de juros confiavel, documentado antes do teste `[quant_trading_chan, ch.6]` |
| Position | carry alinhado com tendencia |
| Rebalance | diario |

Kill especifico: se os dados de carry/rates nao forem confiaveis, pular a familia.

### D. Gold Regime Trend/MR Split

Tese: mercados alternam regimes; gold pode ter regimes macro de tendencia e regimes de range, mas a regra precisa separar regime antes do teste `[trading_systems_methods, p.13-14]`.

Restricao: se for XAU-only, e diagnostico. Nao pode virar winner sozinho.

Parametros iniciais permitidos:

| Parametro | Valores |
|---|---|
| Regime | percentil de volatilidade realizada + tendencia D1 `[trading_systems_methods, p.13-14]` |
| Trend mode | breakout/trend quando regime permitir `[trading_systems_methods, p.13-14]` |
| MR mode | apenas range-bound pre-definido `[trading_systems_methods, p.13-14]` |
| Frequencia | H4/D1 |

Kill especifico: XAU-only nao pode virar winner; se nao melhorar portfolio multi-asset, registrar como diagnostico ou dead-end.

### E. Crypto Momentum With Volatility Throttle

Tese: crypto pode ter momentum forte, mas drawdowns e volatilidade extrema exigem throttle para evitar overbet `[volatility_trading, ch.2]`.

Parametros iniciais permitidos:

| Parametro | Valores |
|---|---|
| Assets | BTCUSD, ETHUSD |
| Lookback | 20 ou 60 D1 `[volatility_trading, ch.2]` |
| Vol throttle | target vol ou max vol percentile pre-registrado `[volatility_trading, ch.2]` |
| Cash filter | absolute momentum > 0 |
| Rebalance | diario ou semanal |

Kill especifico: se a performance vier apenas de long beta crypto sem reducao robusta de drawdown, descartar como nao-estrategia.

## Custos Obrigatorios

Cada iteracao deve documentar custos por asset e frequencia antes de rodar:

- Spread base.
- Commission, se aplicavel.
- Slippage base.
- Swap/overnight quando o caminho for CFD.
- Cenario conservador.
- Cenario stress com spread/slippage ampliados.

Racional: custos e swap podem dominar short-hold CFD e invalidar alpha aparente `[systematic_trading, p.182-197]`.

## Baselines Obrigatorios

Cada hipotese deve comparar contra:

- Buy-and-hold por asset e portfolio equal-weight.
- Always-flat.
- Random-entry matched turnover.
- Uniform-frequency control.

Random-entry e controles de turnover sao obrigatorios para separar edge real de reducao mecanica de exposicao ou sorte amostral `[evidence_based_ta, p.247-260]`.

## Gates Obrigatorios

| Gate | Regra |
|---|---|
| DSR | p < 0.05 quando houver multiplas tentativas `[advances_fin_ml, p.196-202]`. |
| PBO | < 0.5 quando houver grid/selecionador `[advances_fin_ml, p.208-211]`. |
| WF | Walk-forward com criterio pre-registrado; default minimo 6/8 janelas positivas `[trading_systems_methods, ch.21]`. |
| OOS bootstrap | CI low > 0 no bloco OOS `[advances_fin_ml, p.31-34]`. |
| Full bootstrap | CI low > 0 na amostra completa como sanity, sem substituir OOS `[advances_fin_ml, p.31-34]`. |
| Cost stress | Edge permanece positivo sob custo conservador/stress `[systematic_trading, p.182-197]`. |
| Cross-lib sanity | CAGR dentro de +/-3pp entre implementacoes quando houver backtest completo. |

Gates sao hard-block. Falha nao vira quase-pass.

## Kill-Switches Globais K1-K9

| Kill | Condicao | Acao |
|---|---|---|
| K1 | Dados/custos nao confiaveis | Parar antes de backtest. |
| K2 | Baseline random-entry iguala ou supera a estrategia | DEAD_END da familia ou da variante. |
| K3 | PBO >= 0.5 | DEAD_END da familia/grade. |
| K4 | OOS bootstrap low <= 0 | FAIL sem excecao. |
| K5 | Edge some em spread/slippage stress | FAIL. |
| K6 | Melhor resultado e single-asset | Diagnostico apenas, sem deploy. |
| K7 | 0 familias passam | Encerrar hunt. |
| K8 | Edge depende de oracle/top-K ex-post | Diagnostico nontradeable; proibido como estrategia. |
| K9 | Edge depende de reduzir turnover sem filtro observavel pre-registrado | FAIL. |

## Resultado Por Iteracao

Cada iteracao deve terminar com um dos verdicts:

- `positive`
- `negative`
- `inconclusive`
- `dead-end`

Nao inventar dados, resultados ou metricas ausentes.
