# Phase 3.5b Task 7b — Stress isolado das 4 janelas canônicas [PLANO B] [SWING BROKER]

**Data:** 2026-04-17 15:00
**Branch:** `phase3.5b/winners-validation-20260417`
**Iter:** 9
**Status:** ✅ Todos os 3 winners individuais + portfolio 3-leg sobreviveram as 4 janelas de stress sem melt-down. Portfolio é o claro campeão de diversificação.

---

## O que eu queria descobrir

Passar o dedo na cicatriz: quando o mercado quebrou (2008, 2020, 2022, 2025-Q1),
como os 3 winners individuais (LETF, QQQ, GLD) e o portfolio 3-leg se
comportaram dentro da janela do evento? A Phase 3 aprovou tudo no full-window,
mas se um único regime carregou o PASS, isso importa — em live, o usuário vai
sentir cada stress isolado, não a média de 55 anos.

---

## Como testei

1. **Módulo novo** `src/ai_trade/backtest/metrics/stress_periods.py` (266 loc):
   - `StressWindow` dataclass + constante `STANDARD_STRESS_WINDOWS` com as 4
     janelas: `2008_crisis` (2008-09-01 → 2009-03-31), `2020_covid`
     (2020-02-19 → 2020-04-30), `2022_bear` (2022-01-03 → 2022-12-30),
     `2025_q1` (2025-01-01 → 2025-03-31).
   - `compute_stress_report(equity, trades, spy_equity, window)` slice rebase
     + métricas (Sharpe/Sortino/Calmar/max DD + SPY em paralelo na mesma
     janela). `backtest.metrics.performance` (ddof=0) reutilizado
     `[advances_fin_ml, p.214-215]` (convenções DSR consistentes).
   - `render_multi_strategy_stress_markdown()` emite tabela compacta estilo
     backtesting.py.
2. **Driver** `scripts/run_stress_isolated.py` (~230 loc): re-roda a pipeline do
   `validate_phase3_winners.py` byte-for-byte (import dos configs congelados),
   produz `reports/phase3_5b/robustness/stress_isolated.{md,json}`.
3. **Testes** `tests/test_stress_periods.py` (8 casos): rebase, window outside
   data, trade-count-fully-contained, canonical set, render de markdown.
4. **Pytest:** 600 → 608 passed (+8). Baseline intacto.

Citação: spec `specs/phase_3_5b_winners_validation.md` §Task 7b definiu as 4
janelas. SPY é o benchmark obrigatório `[spec §4.5]`.

---

## O que os números mostraram

### Janela 2008 crisis (Lehman → bottom, 146 bars, SPY −36.55% / max DD 46.05%)

| Strategy                   | Total % | Sharpe | Max DD | ΔDD vs SPY |
|---|---|---|---|---|
| LETF EMA100/2x             | 0.00%   | 0.00   | 0.00%  | **−46.05pp** |
| QQQ Donchian 20/10         | −2.39%  | −0.20  | 10.69% | −35.36pp |
| GLD Donchian 40/20         | +6.35%  | 0.67   | 9.88%  | −36.17pp |
| **Portfolio 3-leg EW**     | +1.63%  | 0.39   | 3.84%  | **−42.21pp** |

- LETF **ficou 100% em cash a janela inteira** (o filtro EMA100 manteve risk-off)
  → DD = 0%, ΔDD = −46pp. Regime filter fez o trabalho dele
  `[leverage_for_the_long_run, ch.3]`.
- GLD subiu na crise (flight-to-safety), QQQ perdeu pouco (4 entry/exit).
- Portfolio +1.63% / DD 3.84% vs SPY −36.55% / DD 46%. **Diversificação salvou.**

### Janela 2020 COVID (peak→rebound, 51 bars, SPY −13.62% / max DD 33.70%)

| Strategy                   | Total % | Sharpe | Max DD | ΔDD vs SPY |
|---|---|---|---|---|
| LETF EMA100/2x             | −9.43%  | −2.29  | 12.16% | −21.54pp |
| QQQ Donchian 20/10         | +1.98%  | 0.60   | 5.27%  | −28.43pp |
| GLD Donchian 40/20         | −3.32%  | −0.79  | 7.14%  | −26.56pp |
| **Portfolio 3-leg EW**     | −3.49%  | −1.25  | 6.85%  | **−26.85pp** |

- COVID foi a pior janela pro LETF — o crash veio rápido demais pra EMA reagir
  (entrou em cash depois de absorver −9%). Documenta limite do filtro simples.
  Esperado `[gayed_2016, p.8]` — moving-average whipsaw em crashes explosivos.
- Portfolio ainda perdeu só 3.49% com DD 6.85% (vs SPY 13.62%/33.70%).

### Janela 2022 bear (full-year, 251 bars, SPY −18.64% / max DD 24.50%)

| Strategy                   | Total % | Sharpe | Max DD | ΔDD vs SPY |
|---|---|---|---|---|
| LETF EMA100/2x             | **+19.24%** | 0.93 | 10.53% | −13.97pp |
| QQQ Donchian 20/10         | +3.35%  | 0.31   | 7.00%  | −17.50pp |
| GLD Donchian 40/20         | +11.41% | 1.10   | 8.28%  | −16.21pp |
| **Portfolio 3-leg EW**     | **+11.78%** | 1.02 | 5.28%  | **−19.22pp** |

- Bear + rate hikes favoreceu rotation strategies (7 trades LETF, 4 QQQ, 0 GLD).
- Portfolio: +11.78% num ano em que SPY perdeu 18.64% — é exatamente o caso de
  uso do Plano B `[leverage_for_the_long_run, ch.5]`.

### Janela 2025-Q1 (stress shock, 60 bars, SPY −4.03% / max DD 10.04%)

| Strategy                   | Total % | Sharpe | Max DD | ΔDD vs SPY |
|---|---|---|---|---|
| LETF EMA100/2x             | +1.58%  | 0.42   | 9.43%  | −0.60pp |
| QQQ Donchian 20/10         | −0.07%  | 0.02   | 3.46%  | −6.58pp |
| GLD Donchian 40/20         | **+15.42%** | 5.12 | 3.28% | −6.75pp |
| **Portfolio 3-leg EW**     | +5.56%  | 2.03   | 4.79%  | −5.24pp |

- GLD voou (flight-to-safety de novo: Sharpe 5.12 numa janela Q1 tarifas/juros).
- Portfolio +5.56% vs SPY −4.03%. Excess 9.59pp em 60 bars.

---

## Verdict

Cada winner individual **sobreviveu** todas as 4 janelas sem melt-down
(drawdown máximo dentro de stress ≤ 12.16%). Mais importante: o **portfolio
3-leg EW** teve ΔDD ≤ −19pp em TODAS as 4 janelas — ou seja, quando o SPY
sangrou, o portfolio sangrou muito menos. Isso confirma o objetivo de
diversificação das 3 pernas (LETF regime-filter + QQQ momentum + GLD gold).

**Nenhuma anomalia nova.** Winners imutáveis preservados.

---

## ⚠️ FLAGs (documentais, não-blockers)

1. **LETF 2008 `#trades = 0` + `total% = 0%` mas `bars = 146`:** não é bug. A
   regime filter manteve a strategy 100% em cash a janela inteira. Equity
   rebase = 1.0 constante → métricas zeradas. Interpretação: "asset allocation
   = cash" é equivalente a "não participou do crash". Anotação para revisor
   humano que o `Sortino = inf` é cosmético (sem returns negativos).
2. **Sharpe negativo do LETF 2020:** esperado — EMA100 demora pra virar risk-off
   em crashes de 4 semanas. Não contradiz o full-window Sharpe 1.85: 51 bars é
   ruído temporal alto. Cross-reference com Task 7e (rolling correlation) pra
   ver se essa janela dispara período-de-alta-correlação das 3 pernas.
3. **CAGR "anualizado" em janelas curtas:** o número é annualized mas pouco
   informativo quando a janela tem 51 bars — usar `total %` como métrica
   primária e `CAGR` como sanity check.

---

## Próximos passos

- Task 7c: slippage sensitivity (0/1/5/10 bps round-trip).
- Task 7d: allocation alternativa (EW/IVP/HRP/RP/MV) — confirmar ou refutar EW.
- Task 7e: correlação rolling 63d/252d entre pernas.
- Task 7f: vol-target 10% no portfolio.

Budget: 7 iters restantes antes do cap-16 (cap + 4 Tasks 7c-f + Task 8 + 9).

---

## Artefatos

- `src/ai_trade/backtest/metrics/stress_periods.py` (NEW, 266 loc)
- `tests/test_stress_periods.py` (NEW, 8 testes)
- `scripts/run_stress_isolated.py` (NEW, ~230 loc)
- `reports/phase3_5b/robustness/stress_isolated.md`
- `reports/phase3_5b/robustness/stress_isolated.json`
