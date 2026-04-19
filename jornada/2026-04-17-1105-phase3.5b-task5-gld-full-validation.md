# Phase 3.5b · Task 5 — GLD Donchian 40/20 full validation [PLANO B] [SWING BROKER]

**Data:** 2026-04-17 · **Iter loop:** 5 · **Branch:** `phase3.5b/winners-validation-20260417`

## TL;DR

GLD Donchian 40/20 re-rodado na janela longest-available Tiingo
(2004-11-18 → 2026-04-15, **5384 bars / ~21.4 anos**). Sharpe full-window
**0.937**, CAGR 11.46%, MaxDD 14.35%, 48 trades, WR 62.5%, PF 7.87.
Número bate deterministicamente com o smoke de Iter 2 (task 2) — 0 bytes
de diff em `summary.json`. Perna gold do portfolio 3-leg EW confirma
contribuição: Sharpe sub-1.0 standalone compensado por correlação ~zero
com as outras 2 pernas (ρ vs LETF +0.063 · vs QQQ +0.033).

**Verdict:** GLD leg PRESERVED as Phase 3 portfolio component. ⚠️ 3 FLAGs
documentais (sem reversão de winner) + 1 heads-up de concentração recente.

## Contexto / escopo

Task 5 do `specs/phase_3_5b_winners_validation.md`. Terceira das 4 validações
de winners Phase 3 (depois de LETF iter 3, QQQ iter 4). Objetivo: emitir
trade log + standard report full-window + SPY benchmark + comparison, sem
alterar a lógica do winner (`strategies/tsmom.py` intocado — apenas o hook
aditivo `get_trades()` de Iter 2).

## O que foi feito

1. Conferido manifest Tiingo daily GLD: `first_dt=2004-11-18`,
   `last_dt=2026-04-15`, 5384 bars — janela longest-available confirmada.
2. `.venv/bin/python scripts/validate_phase3_winners.py --output-dir
   reports/phase3_5b --initial-capital 100000` re-rodado (saída
   determinística vs Iter 2).
3. Inspeção trade log (`reports/phase3_5b/gld_donchian_40_20/trade_log.csv`,
   48 linhas de trades) + sub-period breakdown ano-a-ano e por regime.
4. `standard_report.md` full-window + SPY benchmark 2004-11 → 2026-04
   (overlap 100%, SPY também começa 2001-05 no Tiingo).
5. Pytest 587 passed (sem mudança de código).

## Métricas (full-window 2004-11-18 → 2026-04-15)

```
Duration                  7818 days (21.42y)
Exposure Time [%]         43.28%  (56.72% cash)
Equity Final [$]          1,015,916.08
CAGR [%]                  11.46%
Volatility (Ann.) [%]     12.41%
Sharpe Ratio              0.937
Sortino Ratio             1.363
Calmar Ratio              0.799
Max. Drawdown [%]         14.35%
Max. Drawdown Duration    899 days (~2.5y)
# Trades                  48
Win Rate [%]              62.50%   (30W / 18L)
Best Trade [%]            +39.82%
Worst Trade [%]           -4.59%
Avg. Trade [%]            +4.84%
Profit Factor             7.866
SQN                       3.77
Kelly Criterion           0.541
Median Hold (days)        61
Max Hold (days)           201   (last trade 2025-08-29 → 2026-03-18)
```

**vs SPY buy&hold (mesma janela, mesmo capital):**
```
Strategy Final    $1,015,916   vs  SPY $869,206
Strategy CAGR       11.46%     vs  SPY 10.66%   (+0.81pp)
Strategy MaxDD      14.35%     vs  SPY 55.20%   (−40.85pp ← diferença brutal)
Strategy Sharpe      0.937     vs  SPY 0.629
Correlation (daily)  -0.001  · Beta 0.000 · IR -0.013
```

Ponto chave: **Sharpe +0.31 vs SPY, MaxDD 4× menor, correlação
essencialmente zero** → papel de diversificador ouro no portfolio
(exatamente o que A3d esperava). Sozinha bate SPY por ~80bps/ano mas
com vol comparável e DD dramaticamente menor.

## Comparação com Phase 3 a3b/a3d

| Métrica           | Phase 3 IS | Phase 3 OOS | Phase 3 Stress | Task 5 full |
|-------------------|-----------:|------------:|---------------:|------------:|
| Sharpe            | 0.803      | 1.010       | 1.324          | **0.937**   |
| CAGR              | —          | 9.76%       | —              | **11.46%**  |

Full-window 0.937 cai entre IS (0.803) e OOS (1.010) — consistente, sem
divergência suspeita. OOS Phase 3 superior ao IS é esperado (bloco 2016+
pegou início do bull 2024-25).

## Sub-period (ano-a-ano)

| Regime                          | Trades | WR  | Net PnL  | Nota |
|--------------------------------:|-------:|----:|---------:|------|
| 2008-2009 GFC                   | 6      | 33% | +$33.4k  | Muitos false starts mas grandes moves compensam |
| 2011-2013 top/1ᵃ bear           | 6      | 83% | +$24.2k  | Gold peak ($1900) + início queda |
| 2014-2018 chop/bear profundo    | 12     | 42% | +$5.0k   | **Pior regime** — 12 trades, break-even |
| 2020 COVID                      | 3      | 67% | +$9.2k   | Rally pós-março |
| 2022 bear/hikes                 | 1      | 100%| +$3.7k   | Gold flat no ano, 1 trade só |
| 2024-2026 bull recente          | 5      | 100%| +$70.7k  | Dominando — 37% do net PnL total |

⚠️ **Concentração recente:** 2024-26 concentra **37%** do net PnL em ~1/12
da janela. Sem o bull atual, contribuição anual média cai para
~$5.8k/ano sobre $100k → ~5.8% efetivo standalone. Não invalida o winner
(2014-18 chop ainda deu break-even, não prejuízo), mas indica que a perna
gold depende de regime trend-on — exatamente o racional de _Following the
Trend_ [clenow_following_trend, p.149-162].

## FLAGs (não revertem winner)

1. **GLD standalone NÃO é winner de gates Phase 3** — Sharpe full 0.937 <
   1.0, excess CAGR vs SPY só +0.81pp. Entra como _perna_ do portfolio
   3-leg por benefício de correlação, não por edge isolado.
2. **Cash drag 56.72%** — exposição curta 43%. Em broker BR, capital ocioso
   rende CDI (~14%/ano). Task 8 allocation deve modelar: $100k com 43%
   exposição e 57% em renda fixa a CDI = booster adicional que o equity
   atual não captura (mesmo FLAG de Iter 4/QQQ).
3. **Trade log cumulative $292k vs equity curve $1.016M** — trade log usa
   notional fixo $100k/trade (additive view); equity curve reinveste
   (compound view). Ambos corretos, contexto diferente; já flaguei isso
   nas iters 3-4.

## Decisão

- GLD Donchian 40/20 **permanece como perna 3 do portfolio 3-leg EW
  (Phase 3 a3d winner)** — imutabilidade Phase 3.5b §4 respeitada.
- Não promover GLD a winner standalone em `memory.md` — Sharpe 0.937
  sub-gate mandate (CAGR ≥ CDI 13-14% líquido não atingido standalone:
  11.46%−15%IR = efetivo ~9.7% líquido vs CDI 14% = perde).
- Full-window report salvo em `reports/phase3_5b/gld_donchian_40_20/`
  pronto pra Task 6 (3-leg consolidated) + Task 8 (allocation).
- Concentração recente 2024-26 vira insumo pra Task 7b (stress isolado)
  — verificar se Sharpe excl-2024-26 ainda positivo.

## Citações

- Donchian breakout como TF canônico: _Following the Trend_
  [clenow_following_trend, p.149-162].
- Correlação gold-equity ~0 como diversificador: _Expected Returns_
  [ilmanen_expected_returns, p.353-380] (gold factor).
- Exposure time 43% como regime TF ON/OFF esperado: _Systematic Trading_
  [systematic_trading, ch.7].
- CDI booster em cash ocioso: `docs/investment-mandate.md` §4 (Plano B
  CAGR ≥ CDI líquido).

## Artefatos

- `reports/phase3_5b/gld_donchian_40_20/standard_report.md` — full metrics
  + SPY benchmark + Strategy-vs-SPY.
- `reports/phase3_5b/gld_donchian_40_20/trade_log.{csv,md}` — 48 trades
  com 15% IR BR por trade lucrativo.
- `reports/phase3_5b/gld_donchian_40_20/equity_curve.png` — log-scale
  vs SPY.
- `reports/phase3_5b/gld_donchian_40_20/summary.json` — snapshot JSON.

## Próxima iter (Task 6)

Task 6 — Portfolio 3-leg EW **consolidated report**:
- Re-rodar `blend_equal_weight_3()` com trade log agregado (`aggregate_leg_trades`).
- Calcular metrics sobre equity consolidado (NÃO somar pernas).
- 15% IR por venda lucrativa de cada perna individualmente.
- `standard_report.md` + SPY benchmark + `Portfolio_3leg_EW` trade log.
- Jornada `<date>-phase3.5b-task6-portfolio-consolidated.md` [PLANO B].
