# SUMMARY — Iteracao 005 Gold Regime Split Diagnostic

## Verdict

`dead-end`. A regra minima XAUUSD D1 Gold Regime Trend/MR Split falhou de forma clara: retorno, Sharpe, OOS, bootstrap full/OOS e custo stress ficaram negativos. Nao ha winner, nao ha paper/live e XAUUSD-only permanece diagnostico apenas `[trading_systems_methods, p.13-14]`.

## O Que Foi Testado

Foi testada uma unica configuracao pre-registrada para evitar selecao ex-post: tendencia via `close > SMA(100)` com retorno 100 barras positivo/negativo, regime por percentil trailing de ATR(14)/close em 252 barras, modo trend quando percentil >= 60 e modo range quando percentil <= 40, com bandas `SMA(20) +/- 1 * ATR(14)` `[trading_systems_methods, p.13-14]`.

A frequencia foi D1, escolhida antes do teste para reduzir dominio relativo de custos frente a horizontes intraday curtos `[systematic_trading, p.182-197]`. Custos XAUUSD foram os da iteracao 001: base 5 bps, conservador 10 bps e stress 20 bps round-trip `[systematic_trading, p.182-197]`.

## Dados Usados E Caveats

Fonte: Dukascopy BID via `dukascopy-python`, XAUUSD D1, 2593 barras entre 2018-01-01 e 2026-05-01. Sem timestamps duplicados, sem `close` ausente; gaps de fim de semana/feriado esperados.

Caveat: nao ha swap/overnight historico broker-specific. Isto ja bloquearia deployabilidade mesmo se o diagnostico fosse positivo.

## Comparacao Contra Baselines

Base cost, XAUUSD D1:

| Serie | CAGR | Sharpe | MDD |
|---|---:|---:|---:|
| Gold regime split | -6.18% | -0.442 | -51.14% |
| Buy-and-hold XAUUSD | 13.04% | 0.889 | -21.38% |
| Always-flat | 0.00% | n/a | 0.00% |
| Uniform-frequency iter 001 | 10.61% | 1.042 | -14.46% |
| Random-entry iter 001 | 5.98% | 0.803 | -12.34% |
| Random-entry strategy-matched | -1.67% | -2.383 | -16.07% |

A regra bateu apenas o random-entry strategy-matched por Sharpe, mas perdeu para buy-and-hold, always-flat, uniform-frequency e random-entry da iteracao 001 `[evidence_based_ta, p.247-260]`.

## Gates Pass/Fail

| Gate | Resultado |
|---|---|
| Data reliability | PASS; XAUUSD D1 legivel |
| Cost stress | FAIL; stress CAGR -11.48%, Sharpe -0.900 |
| OOS single-block 2024+ | FAIL; base OOS CAGR -5.92%, Sharpe -0.261 |
| Bootstrap full | FAIL; 99.9% CI low -18.38% anualizado |
| Bootstrap OOS | FAIL; 99.9% CI low -36.18% anualizado |
| PBO | NOT_APPLICABLE; uma unica configuracao pre-registrada, sem selecao `[advances_fin_ml, p.208-211]` |
| Baselines obrigatorios | FAIL; perdeu para buy-and-hold, always-flat, uniform-frequency e random-entry iter 001 |
| No single-asset winner | PASS; nenhum winner declarado |

## Kill-Switches Acionados

- K4 `OOS_BOOTSTRAP_LOW_LE_0`: bootstrap OOS 99.9% low negativo `[advances_fin_ml, p.31-34]`.
- K5 `COST_STRESS_ELIMINATES_EDGE`: resultado stress negativo `[systematic_trading, p.182-197]`.
- K6 `XAUUSD_ONLY_DIAGNOSTIC_NO_WINNER`: universo single-asset, diagnostico apenas `[trading_systems_methods, p.13-14]`.

## Licao Para A Proxima Sessao

Nao tentar salvar esta regra ajustando SMA, ATR, percentis ou bandas apos ver o resultado. Familia D XAU-only minima fica morta como diagnostico isolado; qualquer reabertura exigiria tese literaria nova e melhoria multi-asset pre-registrada, nao threshold tuning nem single-asset winner.
