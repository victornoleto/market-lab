# SUMMARY — Iteracao 003 Volatility Breakout H4 Minimal

## Verdict

`dead-end` para a grade minima Volatility Breakout H4. Nao ha winner, nao ha paper/live e nenhum resultado single-asset foi aceito como candidato.

## O Que Foi Testado

Foi testada uma regra H4 de rompimento Donchian long/short com canais 20 e 55 barras, filtro ATR percentil > 50 ou > 70, entrada por rompimento de maxima/minima do canal e saida/reversao por canal oposto `[trading_systems_methods, ch.14]`.

A grade foi congelada antes do teste: `donchian20_atrp50`, `donchian20_atrp70`, `donchian55_atrp50`, `donchian55_atrp70`. A frequencia H4 manteve o escopo day/swing, com custos base/conservador/stress iguais aos da iteracao 001 por sensibilidade a spread/slippage `[systematic_trading, p.182-197]`.

## Dados Usados E Caveats

Fonte: Dukascopy BID via `dukascopy-python`, H4, janela 2018-01-01 a 2026-05-01, simbolos EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, XAUUSD, BTCUSD e ETHUSD.

Todos os 10 simbolos retornaram dados H4. Caveat inalterado: BID-only, sem historico broker-specific de swap/commission; custos sao overlay de pesquisa, nao modelo deployavel.

As specs legadas `specs/backtest_phase2.md` e `specs/backtest_phase2_5_ehlers.md` citadas por `CLAUDE.md` nao estavam presentes nesta branch; a iteracao seguiu `SPEC.md` e `LOOP_PROTOCOL.md` do estudo atual.

## Comparacao Contra Baselines

Portfolio equal-weight, cenario base:

| Regra | CAGR | Sharpe | MDD |
|---|---:|---:|---:|
| Vol Breakout H4 `donchian20_atrp50` | -2.66% | -0.034 | -50.08% |
| Vol Breakout H4 `donchian20_atrp70` | -6.09% | -0.273 | -52.90% |
| Vol Breakout H4 `donchian55_atrp50` | 8.07% | 0.477 | -31.24% |
| Vol Breakout H4 `donchian55_atrp70` | 1.85% | 0.193 | -32.91% |
| Buy-and-hold EW iter001 H4 | 12.29% | 0.590 | -41.58% |
| Random-entry EW iter001 H4 | 2.74% | 0.278 | -27.53% |
| Uniform-frequency EW iter001 H4 | 3.34% | 0.300 | -28.08% |
| Always-flat | 0.00% | n/a | 0.00% |

A melhor variante por Sharpe base foi `donchian55_atrp50`: 8.07% CAGR / Sharpe 0.477 / MDD -31.24%. Ela bateu random-entry e uniform-frequency da iteracao 001 em Sharpe, mas nao bateu buy-and-hold H4. O random-entry matched-turnover gerado com o turnover da propria estrategia ficou negativo (Sharpe -0.847), reforcando que havia algum sinal acima de churn aleatorio, mas insuficiente para os gates estatisticos `[evidence_based_ta, p.247-260]`.

Sob custo stress, `donchian55_atrp50` ainda ficou positivo: 4.48% CAGR / Sharpe 0.314 / MDD -41.07%. OOS 2024+ tambem foi positivo em ponto estimado: 0.99% CAGR / Sharpe 0.143 / MDD -19.53%.

## Gates Pass/Fail

| Gate | Resultado |
|---|---|
| K1 dados disponiveis | PASS |
| Cost stress positivo | PASS |
| OOS single-block ponto estimado positivo | PASS |
| Bootstrap full CI low > 0 | FAIL, ci_low = -7.19% anualizado |
| Bootstrap OOS CI low > 0 | FAIL, ci_low = -21.86% anualizado |
| PBO < 0.5 | PASS, PBO = 0.000 |
| Bate buy-and-hold EW em Sharpe base | FAIL |
| Bate random-entry EW iter001 em Sharpe base | PASS |
| Bate random-entry matched-turnover proprio em Sharpe base | PASS |
| Bate random-entry em pelo menos 2 classes | PASS, FX e CRYPTO |
| No single-asset winner | PASS; melhor single-asset diagnostico foi ETHUSD |

DSR nao foi computado neste escopo minimo; PBO foi aplicado para a selecao entre as 4 configs `[advances_fin_ml, p.196-211]`.

## Kill-Switches Acionados

- K4 `OOS_BOOTSTRAP_LOW_LE_0`: OOS bootstrap 99.9% low cruzou zero `[advances_fin_ml, p.31-34]`.

## Licao Para A Proxima Sessao

A Familia B minima nao deve ser salva ajustando canal ou ATR depois do resultado. O sinal Donchian 55/ATR p50 teve ponto estimado positivo e passou PBO/cost stress, mas nao bateu buy-and-hold H4 e falhou bootstrap full/OOS severo. Proxima iteracao deve mudar de familia ou testar uma hipotese literaria independente pre-registrada, sem usar este resultado para otimizar thresholds.
