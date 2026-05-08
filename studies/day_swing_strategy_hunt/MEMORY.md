# MEMORY — Day/Swing Strategy Hunt

Memoria curta para sessoes futuras. Nao substitui `SPEC.md`.

## Estado Atual

Iteracao 007 concluiu auditoria/fechamento do ciclo inicial Familias A-E. Verdict `dead-end`: nenhuma familia produziu winner deployavel e nao ha extensao pequena claramente multi-asset/pre-registravel sem tese literaria nova. Capital segue 100% Plano C; Plano A segue DORMANT; sem paper/live.

## Decisoes Permanentes

- Nao usar HappyForex como dataset de treino.
- Nao usar selecao ex-post por PnL futuro como estrategia.
- Nao aceitar winner single-asset.
- Nao otimizar threshold apos ver resultado.
- Ciclo inicial usa D1/H4; H1 so depois; M1/M5 apenas diagnostico.
- Toda estrategia, indicador, parametro e gate precisa de citacao de livro.
- Gates estatisticos sao hard-block, especialmente DSR/PBO/OOS bootstrap `[advances_fin_ml, p.196-211]`.

## Licoes Negativas Herdadas De MyFxBook

- HappyForex reverse engineering com OHLC publico M5/M1 nao recuperou fidelidade operacional.
- Regras Gold derivadas dispararam demais e nao sobreviveram custos/OOS/bootstrap.
- Reduzir trades para `k = n_real_trades` sem filtro observavel nao e estrategia.
- Oracle/top-K por PnL futuro e upper bound nontradeable, nao regra executavel.

## Hipoteses Testadas

- Iteracao 001: auditoria de dados e baselines minimos para Time-Series Momentum H4/D1. Dados Dukascopy BID disponiveis para 10/10 simbolos em D1 e H4 na janela 2018-01-01 a 2026-05-01. Baselines gravados; verdict `positive` apenas para infraestrutura/auditoria, sem winner.
- Iteracao 002: TSMOM D1 long/flat com lookbacks pre-registrados 20/60/120. Melhor Sharpe base foi lookback 60 com 13.35% CAGR, Sharpe 0.988 e MDD -24.58%, mas falhou PBO 0.557 e bootstrap OOS 99.9% low -10.64% anualizado; verdict `dead-end` para a grade D1 minima `[advances_fin_ml, p.31-34, p.208-211]`.
- Iteracao 003: Volatility Breakout H4 long/short com Donchian 20/55 e ATR percentil >50/>70. Melhor config `donchian55_atrp50` teve 8.07% CAGR, Sharpe 0.477 e MDD -31.24%, mas nao bateu buy-and-hold H4 em Sharpe, bootstrap full 99.9% low foi -7.19% anualizado e bootstrap OOS low foi -21.86%; verdict `dead-end` para a grade minima `[trading_systems_methods, ch.14]` `[advances_fin_ml, p.31-34]`.
- Iteracao 004: Carry/Trend FX data gate para EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD e NZDUSD. Sem fonte historica confiavel de rates/carry para as oito moedas exigidas antes do backtest; verdict `inconclusive`, sem estrategia rodada `[quant_trading_chan, ch.6]`.
- Iteracao 005: Gold Regime Trend/MR Split XAUUSD-only D1 diagnostico. Regra unica pre-registrada com tendencia SMA100/retorno100 e regime ATR(14)/close percentil 252 falhou: base CAGR -6.18%, Sharpe -0.442, MDD -51.14%; OOS 2024+ CAGR -5.92%, stress CAGR -11.48%, bootstrap full/OOS 99.9% lows negativos; verdict `dead-end` `[trading_systems_methods, p.13-14]` `[advances_fin_ml, p.31-34]`.
- Iteracao 006: Crypto Momentum With Volatility Throttle BTCUSD/ETHUSD-only D1 diagnostico. Regra unica pre-registrada momentum 60d + volatilidade realizada 20d percentil 252 com throttle 1.0/0.5/0.0 teve base CAGR 33.02%, Sharpe 1.016, MDD -54.73%, stress positivo e superou baselines em Sharpe, mas bootstrap OOS 99.9% low foi -19.66% anualizado; verdict `dead-end` e crypto-only diagnostico apenas `[volatility_trading, ch.2]` `[advances_fin_ml, p.31-34]`.
- Iteracao 007: auditoria/fechamento conservador das Familias A-E. Revisou apenas `SUMMARY.md` e `RESULTS.json` das iteracoes 001-006, sem backtest novo. Verdict `dead-end` para o ciclo inicial: A falhou PBO/OOS bootstrap, B falhou bootstrap/buy-and-hold, C ficou data-blocked, D falhou custo/OOS/bootstrap e single-asset, E falhou OOS bootstrap e crypto-only. Nao ha reabertura sem tese literaria nova multi-asset ou dados carry confiaveis `[advances_fin_ml, p.208-211]`.

## Licoes Novas

- Dukascopy direto por simbolo/frequencia funcionou para D1/H4; o loader mensal cacheado foi lento demais para a janela 2018-2026 e excedeu 15 minutos.
- H4 e sensivel a custo: uniform/random matched-turnover ficam negativos sob stress. Qualquer H4 futuro precisa superar controles de turnover e cost stress `[systematic_trading, p.182-197]`.
- D1 buy-and-hold equal-weight ficou forte na janela 2018-2026 por beta Gold/Crypto; TSMOM futuro precisa comparar contra portfolio multi-asset, nao contra single-asset winner.
- TSMOM D1 simples teve ponto estimado bom, mas nao robusto: selecao entre 20/60/120 foi instavel por PBO e o OOS 2024+ nao passou bootstrap severo. Nao tentar salvar ajustando lookback/threshold depois do resultado.
- Vol Breakout H4 simples teve sinal pontual acima de random-entry e passou PBO/cost stress, mas nao teve robustez estatistica nem superou buy-and-hold H4. Nao tentar salvar ajustando canal/ATR depois do resultado.
- Carry/Trend FX nao deve ser testado com spot-only, PnL futuro ou proxy improvisado de carry. Reabrir apenas com dataset confiavel de rates/carry documentado antes do teste.
- Gold Regime Split XAU-only com thresholds SMA100/ATR percentil 60/40 nao mostrou nem sinal bruto; perdeu para buy-and-hold, always-flat, uniform-frequency e random-entry da iteracao 001. Nao ajustar SMA/ATR/percentis/bandas apos ver o resultado.
- Crypto Momentum Vol Throttle BTC/ETH mostrou sinal pontual forte, mas nao robusto no OOS bootstrap severo. Nao ajustar lookback 60, vol 20d, percentis 80/95 ou janela 252 apos ver o resultado; crypto-only continua diagnostico, nao winner.
- O ciclo inicial A-E esta fechado como sem winner. Resultado pontual nao deve ser resgatado por threshold tuning; reabertura exige tese literaria nova multi-asset ou, para Carry/Trend FX, dataset confiavel de rates/carry antes do teste.

## Hipoteses Pendentes

1. Nenhuma hipotese pendente no ciclo inicial A-E.
2. Familia C pode ser considerada apenas se surgir dataset confiavel de rates/carry documentado antes do teste.
3. Qualquer novo hunt exige tese literaria nova, multi-asset e pre-registro limpo; nao usar A-E como tuning.

## Ultimo Resultado

Iteracao 007 `dead-end`: `studies/day_swing_strategy_hunt/iterations/007-cycle-close-audit/` contem `PRE_REG.md`, `RESULTS.json` e `SUMMARY.md`. A auditoria fechou o ciclo inicial A-E sem winner e sem extensao pre-registravel conservadora; sem paper/live `[advances_fin_ml, p.208-211]`.

## Proximo Passo Recomendado

Hunt encerrado por ora. Proxima sessao nao deve iniciar iteracao nova automaticamente; reabrir apenas com pedido explicito do usuario e tese literaria nova multi-asset ou dados carry/rates confiaveis pre-documentados.
