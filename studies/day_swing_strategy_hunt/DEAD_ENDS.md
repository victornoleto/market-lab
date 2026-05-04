# DEAD_ENDS — Day/Swing Strategy Hunt

Ideias mortas ou proibidas para nao reabrir por esquecimento.

## Herdados De MyFxBook

### DE-001 — HappyForex Reverse Engineering Via OHLC Publico M5/M1

Status: morto.

Motivo: M5/M1 publico nao recuperou fidelidade operacional suficiente; nao usar como dataset de treino. Pode ser citado apenas como evidencia negativa.

### DE-002 — Gold Derived Rules / Over-Fire

Status: morto.

Motivo: regras Gold derivadas nao sobreviveram custos, bootstrap e OOS; reduzir frequencia depois de ver resultado nao salva uma regra que dispara demais sem filtro observavel pre-registrado.

### DE-003 — Oracle / Top-K Por PnL Futuro

Status: proibido como estrategia.

Motivo: selecionar trades por PnL futuro e diagnostico nontradeable. Pode aparecer apenas como upper bound rotulado explicitamente, nunca como filtro, ranking ou regra executavel.

## Regras Para Novos Dead-Ends

Adicionar uma entrada quando uma familia falhar por gate estrutural, custo, dado inviavel, single-asset-only ou dependencia de oracle. Incluir:

- Iteracao.
- Hipotese.
- Kill-switch acionado.
- Evidencia curta.
- Condicao concreta que permitiria reabrir, se existir.

## Day/Swing Hunt

### DE-004 — TSMOM D1 Minimal 20/60/120

Status: morto para a grade minima D1 testada na iteracao 002.

Hipotese: Time-Series Momentum D1 long/flat com lookbacks 20, 60 e 120 barras `[systematic_trading, ch.10]`.

Kill-switch acionado: K3 PBO >= 0.5 e K4 OOS bootstrap low <= 0 `[advances_fin_ml, p.31-34, p.208-211]`.

Evidencia curta: melhor lookback por Sharpe base foi 60 barras com 13.35% CAGR, Sharpe 0.988 e MDD -24.58%, mas PBO = 0.557 e bootstrap OOS 99.9% low = -10.64% anualizado. Resultado pontual positivo nao passa gate hard-block.

Condicao para reabrir: somente com OOS novo independente ou hipotese literaria nova pre-registrada antes do teste. Nao reabrir para ajustar threshold/lookback apos ver este resultado.

### DE-005 — Volatility Breakout H4 Minimal Donchian/ATR

Status: morto para a grade minima H4 testada na iteracao 003.

Hipotese: Volatility Breakout H4 long/short com canais Donchian 20 e 55 barras, filtro ATR percentil >50 ou >70, entrada por rompimento de maxima/minima e saida por canal oposto `[trading_systems_methods, ch.14]`.

Kill-switch acionado: K4 OOS bootstrap low <= 0 `[advances_fin_ml, p.31-34]`.

Evidencia curta: melhor config por Sharpe base foi `donchian55_atrp50` com 8.07% CAGR, Sharpe 0.477 e MDD -31.24%. PBO passou (0.000) e stress de custo ficou positivo, mas a estrategia nao bateu buy-and-hold H4 em Sharpe, bootstrap full 99.9% low = -7.19% anualizado e bootstrap OOS 99.9% low = -21.86% anualizado.

Condicao para reabrir: somente com tese literaria nova pre-registrada ou OOS independente novo. Nao reabrir para ajustar canal Donchian, percentil ATR ou holding apos ver este resultado.

### DE-006 — Carry/Trend FX Sem Dataset Confiavel De Rates/Carry

Status: data-blocked.

Hipotese: combinar carry FX com tendencia D1, com posicao apenas quando diferencial de juros/carry estiver alinhado com tendencia `[quant_trading_chan, ch.6]`.

Kill-switch acionado: K1 dados/custos nao confiaveis.

Evidencia curta: iteracao 004 exigiu fonte historica confiavel de rates/carry para EUR, GBP, USD, JPY, CHF, CAD, AUD e NZD antes do backtest. O repo tinha spot FX Dukascopy e caches Tiingo/testfolio, mas nao uma matriz documentada de rates/carry por moeda. A estrategia nao foi rodada.

Condicao para reabrir: somente com dataset oficial/institucional de policy/cash rates ou carry por moeda, versionado/documentado antes do teste. Nao reabrir com proxy spot-only, PnL futuro, swap inferido ex-post ou ajuste calibrado por resultado.

### DE-007 — Gold Regime Split XAUUSD-Only Minimo

Status: morto para a regra XAUUSD-only D1 testada na iteracao 005.

Hipotese: separar XAUUSD em regimes trend/range usando tendencia D1 e percentil de ATR/volatilidade realizada antes do teste `[trading_systems_methods, p.13-14]`.

Kill-switch acionado: K4 OOS bootstrap low <= 0, K5 custo stress elimina edge e K6 single-asset diagnostico apenas `[advances_fin_ml, p.31-34]` `[systematic_trading, p.182-197]`.

Evidencia curta: regra unica pre-registrada `SMA100/ret100 + ATR(14)/close pct252 60/40 + SMA20 +/- 1ATR` teve base CAGR -6.18%, Sharpe -0.442 e MDD -51.14%; OOS 2024+ CAGR -5.92%; stress CAGR -11.48%; bootstrap full/OOS 99.9% lows negativos. Perdeu para buy-and-hold, always-flat, uniform-frequency e random-entry da iteracao 001.

Condicao para reabrir: somente com tese literaria nova e melhoria multi-asset pre-registrada em iteracao futura. Nao reabrir para ajustar SMA, ATR, percentis, bandas ou modo trend/range apos ver este resultado.

### DE-008 — Crypto Momentum Vol Throttle BTCUSD/ETHUSD-Only Minimo

Status: morto como candidato isolado crypto-only para a regra D1 testada na iteracao 006.

Hipotese: momentum absoluto BTCUSD/ETHUSD D1 com throttle por percentil de volatilidade realizada para reduzir exposicao em regimes extremos `[volatility_trading, ch.2]`.

Kill-switch acionado: K4 OOS bootstrap low <= 0 e K6 crypto-only diagnostico apenas `[advances_fin_ml, p.31-34]` `[volatility_trading, ch.2]`.

Evidencia curta: regra unica pre-registrada `momentum 60d + vol realizada 20d pct252 throttle 80/95` teve base CAGR 33.02%, Sharpe 1.016 e MDD -54.73%; stress ficou positivo e bateu baselines em Sharpe, mas bootstrap OOS 99.9% low foi -19.66% anualizado. Resultado pontual positivo nao supera gate hard-block e nao autoriza single-class winner.

Condicao para reabrir: somente com tese multi-asset nova pre-registrada, em que crypto seja componente de portfolio e nao winner isolado. Nao reabrir para ajustar lookback, janela de volatilidade, percentis 80/95 ou janela 252 apos ver este resultado.

### DE-009 — Ciclo Inicial Familias A-E Sem Winner

Status: fechado por ora.

Hipotese: ciclo inicial day/swing sobre Time-Series Momentum, Volatility Breakout, Carry/Trend FX, Gold Regime Split e Crypto Momentum Vol Throttle em D1/H4.

Kill-switch acionado: K7 0 familias passam como winner; K3/K4/K5/K6 acionados em subfamilias; K1 bloqueou Carry/Trend FX sem dados confiaveis `[advances_fin_ml, p.31-34, p.208-211]`.

Evidencia curta: iteracao 007 revisou apenas artefatos 001-006. A falhou PBO/OOS bootstrap; B falhou bootstrap full/OOS e baseline buy-and-hold; C ficou data-blocked; D falhou custo/OOS/bootstrap e era XAU-only; E falhou bootstrap OOS e era crypto-only.

Condicao para reabrir: pedido explicito do usuario com tese literaria nova, multi-asset e pre-registrada antes de qualquer teste; ou dataset confiavel de rates/carry para Familia C. Nao reabrir para tuning de thresholds, universe cherry-pick, single-asset winner ou selecao ex-post por PnL.
