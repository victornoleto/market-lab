# SUMMARY — Iteracao 002 TSMOM D1 Minimal

## Verdict

`dead-end` para a grade minima TSMOM D1 20/60/120. Nao ha winner, nao ha paper/live e nenhum resultado single-asset foi aceito como candidato.

## O Que Foi Testado

Foi testada uma regra Time-Series Momentum D1 long/flat: posicao long quando o retorno do lookback e positivo, flat caso contrario, com lookbacks congelados 20, 60 e 120 barras `[systematic_trading, ch.10]`. A frequencia D1 foi mantida para reduzir dominio relativo de custos `[systematic_trading, p.182-197]`.

A selecao diagnostica do melhor lookback por Sharpe base do portfolio apontou `60` barras, mas essa selecao ficou sujeita ao gate PBO `[advances_fin_ml, p.208-211]`.

## Dados Usados E Caveats

Fonte: Dukascopy BID via `dukascopy-python`, D1, janela 2018-01-01 a 2026-05-01, simbolos EURUSD, GBPUSD, USDJPY, USDCHF, USDCAD, AUDUSD, NZDUSD, XAUUSD, BTCUSD e ETHUSD.

Todos os 10 simbolos retornaram dados. Caveat inalterado: BID-only, sem historico broker-specific de swap/commission; custos sao overlay de pesquisa, nao modelo deployavel.

## Comparacao Contra Baselines

Portfolio equal-weight, cenario base:

| Regra | CAGR | Sharpe | MDD |
|---|---:|---:|---:|
| TSMOM D1 lb=20 | 10.67% | 0.894 | -14.97% |
| TSMOM D1 lb=60 | 13.35% | 0.988 | -24.58% |
| TSMOM D1 lb=120 | 12.71% | 0.931 | -24.65% |
| Buy-and-hold EW iter001 | 14.19% | 0.807 | -32.79% |
| Random-entry EW iter001 | 6.44% | 0.711 | -18.61% |
| Uniform-frequency EW iter001 | 5.45% | 0.489 | -28.50% |
| Always-flat | 0.00% | n/a | 0.00% |

O lookback 60 bateu buy-and-hold e random-entry em Sharpe base, mas nao em CAGR. Sob stress, o mesmo lookback ainda ficou positivo: 11.00% CAGR, Sharpe 0.832, MDD -26.72%.

OOS pre-registrado 2024+: lb=60 ficou positivo em ponto estimado: 6.75% CAGR, Sharpe 0.704, MDD -11.14%. Porem o bootstrap OOS 99.9% teve `ci_low = -10.64%` anualizado, falhando o hard gate `[advances_fin_ml, p.31-34]`.

## Gates Pass/Fail

| Gate | Resultado |
|---|---|
| K1 dados disponiveis | PASS |
| Cost stress positivo | PASS |
| OOS single-block ponto estimado positivo | PASS |
| Bootstrap full CI low > 0 | PASS |
| Bootstrap OOS CI low > 0 | FAIL |
| PBO < 0.5 | FAIL, PBO = 0.557 |
| Bate buy-and-hold EW em Sharpe base | PASS |
| Bate random-entry EW em Sharpe base | PASS |
| Bate random-entry em pelo menos 2 classes | PASS |
| No single-asset winner | PASS |

## Kill-Switches Acionados

- K3 `PBO_GE_0_5`: selecao entre lookbacks ficou acima do limite hard-block `[advances_fin_ml, p.208-211]`.
- K4 `OOS_BOOTSTRAP_LOW_LE_0`: OOS bootstrap 99.9% low cruzou zero `[advances_fin_ml, p.31-34]`.

## Licao Para A Proxima Sessao

TSMOM D1 simples tem ponto estimado interessante, mas nao robusto o suficiente: a selecao 20/60/120 parece instavel e o OOS nao passa bootstrap severo. Nao otimizar threshold/lookback apos ver resultado. A proxima iteracao deve mudar familia ou testar uma extensao pre-registrada que nao seja ajuste ex-post desta grade; candidato natural e Familia B Volatility Breakout H4 com canal Donchian pre-registrado `[trading_systems_methods, ch.14]`.
