# SUMMARY — Iteracao 006 Crypto Momentum Vol Throttle Diagnostic

## Verdict

`dead-end`. A regra BTCUSD/ETHUSD D1 Momentum With Volatility Throttle teve resultado economico forte em full sample e stress, mas falhou o gate hard-block de bootstrap OOS 99.9% low. Como o universo e crypto-only, o resultado tambem e diagnostico apenas e nao pode virar winner sozinho `[volatility_trading, ch.2]`.

## O Que Foi Testado

Foi testada uma unica configuracao pre-registrada, sem grade: momentum absoluto D1 de 60 barras, volatilidade realizada 20d anualizada, percentil trailing 252 barras, long se momentum > 0, exposicao 1.0 se vol percentil <= 80, 0.5 se >80 e <=95, e 0.0 se >95. O portfolio e equal-weight BTCUSD/ETHUSD com cash no restante `[volatility_trading, ch.2]` `[systematic_trading, ch.10]`.

A frequencia foi D1 para reduzir dominio relativo de custos. Custos crypto foram exatamente os da iteracao 001: 10 bps base, 25 bps conservador e 50 bps stress round-trip `[systematic_trading, p.182-197]`.

## Dados Usados E Caveats

Fonte: Dukascopy BID via `dukascopy-python`, BTCUSD/ETHUSD D1. BTCUSD teve 2987 barras e ETHUSD 2982 barras entre 2018-01-01 e 2026-05-01. Sem timestamps duplicados e sem `close` ausente.

Caveat: nao ha swap/overnight historico broker-specific. Mesmo com resultado positivo, isso bloquearia deployabilidade CFD sem estudo separado de custos reais.

## Comparacao Contra Baselines

Base cost, portfolio BTCUSD/ETHUSD:

| Serie | CAGR | Sharpe | MDD |
|---|---:|---:|---:|
| Crypto momentum vol throttle | 33.02% | 1.016 | -54.73% |
| Buy-and-hold crypto mean iter 001 | 12.97% | 0.524 | -87.93% |
| Always-flat | 0.00% | n/a | 0.00% |
| Uniform-frequency crypto mean iter 001 | 3.88% | 0.329 | -73.47% |
| Random-entry crypto mean iter 001 | 9.11% | 0.441 | -64.00% |
| Random-entry strategy-matched | 9.49% | 0.471 | -58.01% |

A regra bateu buy-and-hold, uniform-frequency e random-entry em Sharpe base, mas isso nao supera os gates estatisticos nem a restricao crypto-only `[evidence_based_ta, p.247-260]`.

## Gates Pass/Fail

| Gate | Resultado |
|---|---|
| Data reliability | PASS; BTCUSD/ETHUSD D1 legiveis |
| Cost stress | PASS; stress CAGR 26.60%, Sharpe 0.868 |
| OOS single-block 2024+ | PASS; base OOS CAGR 22.37%, Sharpe 0.883 |
| Bootstrap full | PASS; 99.9% CI low +5.93% anualizado |
| Bootstrap OOS | FAIL; 99.9% CI low -19.66% anualizado |
| PBO | NOT_APPLICABLE; uma unica configuracao pre-registrada `[advances_fin_ml, p.208-211]` |
| Baselines obrigatorios | PASS em Sharpe contra buy-and-hold, uniform e random controls |
| No crypto-only winner | PASS; nenhum winner declarado |

## Kill-Switches Acionados

- K4 `OOS_BOOTSTRAP_LOW_LE_0`: bootstrap OOS 99.9% low negativo `[advances_fin_ml, p.31-34]`.
- K6 `CRYPTO_ONLY_DIAGNOSTIC_NO_WINNER`: universo BTCUSD/ETHUSD-only, diagnostico apenas `[volatility_trading, ch.2]`.

## Licao Para A Proxima Sessao

Nao tentar salvar esta regra ajustando lookback, percentis 80/95, janela de volatilidade ou janela de percentil apos ver o resultado. A familia E crypto-only minima fica morta como candidato isolado; qualquer reabertura exigiria tese multi-asset pre-registrada, com crypto como componente de portfolio e nao como winner single-class.
