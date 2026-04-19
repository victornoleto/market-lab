# Lead B1a [SWING BROKER] — módulo LETF rotation pronto para o grid

Hoje (iter 29) não rodei backtest ainda — preparei o **chão** para o Lead B1:
a estratégia-chave da Path B, a rotação de LETF do Gayed.

## O que foi feito

Dois arquivos novos em `src/ai_trade/backtest/`:

- `helpers/synthetic_letf.py` — gera retornos sintéticos de um LETF
  para períodos em que UPRO/SSO ainda não existiam (UPRO=2009, SSO=2006).
  A fórmula é a do paper do Gayed: `r_synth = L·r_SPX_TR − fee/252`,
  onde `fee` é o expense ratio anual (1% pré-2021, 0.95% pós-2021).
  Isso é o que nos permite testar a estratégia de 1970 a 2000 mesmo
  sem ETFs alavancados na época. `[leverage_for_the_long_run, p.16]`

- `strategies/letf_rotation.py` — a estratégia LRS em si, implementada
  como **simulador de série de retornos** (não usa o engine de barras).
  Motivo: Gayed opera em close-to-close puro; pular o engine é ~100x
  mais rápido (essencial pro grid de 360 configs) e replica fielmente
  a tabela do paper. `[leverage_for_the_long_run, p.13, p.21]`

A estratégia tem 3 "knobs" pré-especificados:

1. **Filtro** (SMA ou EMA) com lookback configurável. Gayed só usa
   SMA `[p.8]`; EMA entra no grid como hipótese concorrente do estudo
   do Reddit. O winner é decidido pelos gates, não por afinidade.
2. **Banda de histerese** (0%, 3%, 5%). Banda 0% = cruzamento estrito
   (Gayed); banda 5% = dampening de whipsaw (Reddit). Dentro da banda,
   o sinal mantém o estado anterior.
3. **Off-asset** (cash ou blend cash/gold). Gayed usa cash puro `[p.21]`;
   o mandate pede testar ouro como hedge.

Custos e impostos entram no `LETFRotationConfig` como parâmetros
imutáveis (dataclass frozen), então a ablação de custo vira trivial
— basta trocar um flag e rerodar o grid. A taxa brasileira de 15%
sobre ganho de capital é aplicada em cada saída ON→OFF — é o que
um investidor real na B3 pagaria ao realizar lucro.

## Por que dividi o B1 em sub-leads

Lead B1 completo = estratégia + loader de SPX TR 1970-2026 + grid
360 configs + CPCV/PBO/bootstrap. Num único iter isso estoura muito
além de 30 min. Dividi em:

- **B1a (hoje)** — módulos base + testes unitários. DONE.
- **B1b** — loader de SPX TR sintético pré-2001 (Shiller/Ken French)
  + runner de grid + cache.
- **B1c** — execução completa (360 configs × 3 splits), CPCV, PBO,
  bootstrap, veredito.

Cada um fica no timebox de 30 min do loop.

## Testes

- **36 novos testes** — fórmula do Gayed, ceilings de banda, SMA vs
  EMA, custos por switch, imposto BR só em exit com gain, ouro blend,
  erros de alinhamento.
- **396 passed** na suite completa (antes 360). Baseline holds.

## Próximo passo

Iter 30: B1b — carregar/synthesizer de SPX TR desde 1970 e escrever
`scripts/run_grid_letf_rotation.py` com o grid de 360 configs.

## Citações

- `[leverage_for_the_long_run, p.4, p.7, p.8, p.11, p.13, p.14, p.16,
  p.17, p.21]` — todas as decisões de estratégia.

## Arquivos

- `src/ai_trade/backtest/helpers/synthetic_letf.py` (new, 130 LoC).
- `src/ai_trade/backtest/strategies/letf_rotation.py` (new, 340 LoC).
- `tests/test_helpers_synthetic_letf.py` (new, 10 tests).
- `tests/test_letf_rotation.py` (new, 26 tests).

Verdict do lead B1a: **DONE** (não é pass/fail ainda — é foundation).
Sub-leads B1b/B1c ficam para iter 30-31.
