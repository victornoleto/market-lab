# Phase 3.5b Task 7c [PLANO B] [SWING BROKER] — Slippage sensitivity PASS

**Data:** 2026-04-17 15:45
**Branch:** `phase3.5b/winners-validation-20260417`
**Iter:** 10

## Contexto

Task 7c do `specs/phase_3_5b_winners_validation.md` pede uma tabela
Sharpe/CAGR a 0/1/5/10 bps de slippage round-trip para cada um dos 4
winners Phase 3 (LETF EMA100/2x, QQQ Donchian 20/10, GLD Donchian 40/20
e o Portfolio 3-leg EW). Objetivo: confirmar que o verdict **PASS** dos
leads A1c/A3b/A3d sobrevive a variações realistas no custo de transação
antes de liberar o allocation doc (Task 8).

## O que foi feito

1. **Módulo `src/ai_trade/backtest/metrics/slippage_sensitivity.py`**
   (220 loc) com `SlippageRow`, `summarize_equity()`,
   `make_cost_varied_config()` (usa `dataclasses.replace` para zerar
   `commission_bps` e setar `spread_bps=level`) e renderers Markdown.
   9 testes unitários novos.

2. **Script `scripts/run_slippage_sensitivity.py`** (~170 loc) que
   reusa `validate_phase3_winners` para dados e winner configs.
   Para cada nível L ∈ {0, 1, 5, 10} bps, re-simula as 3 pernas
   (`commission_bps=0, spread_bps=L`), blenda EW, e emite
   `reports/phase3_5b/robustness/slippage_sensitivity.{md,json}`.

3. **Winners congelados** — só mexi em `commission_bps`/`spread_bps`.
   Tax 15%, `annual_fee`, lookbacks, leverage, gold_weight idênticos.

## Resultado — monotonic, small, uniform degradation

**Todas as 4 strategies passam com folga em todas as 4 tiers de custo**
(janelas longest per manifest rule — LETF 56.3y, QQQ 24.9y, GLD 21.4y,
Portfolio 21.4y GLD-limited).

| Strategy             | 0 bps Sharpe | 10 bps Sharpe | Δ Sharpe | 10 bps CAGR |
|----------------------|-------------:|--------------:|---------:|------------:|
| LETF EMA100/2x       |        1.913 |         1.870 |  −0.043  |      45.40% |
| QQQ Donchian 20/10   |        1.486 |         1.421 |  −0.065  |      17.88% |
| GLD Donchian 40/20   |        0.987 |         0.954 |  −0.033  |      11.70% |
| Portfolio 3-leg EW   |        2.208 |         2.141 |  −0.067  |      26.04% |

Sensitivity ≈ −0.004 a −0.007 Sharpe por bp adicional. QQQ é o mais
sensível (mais switches: 213 em 24.9y = ~8.5/y). GLD é o menos sensível
(96 switches em 21.4y = ~4.5/y). A 10 bps de custo por switch:

- Portfolio **Sharpe 2.141 > 2.0** — ainda comfortably acima do
  Phase 3 gate.
- CAGR portfolio cai de 27.00% (0 bps) para 26.04% (10 bps) — drag
  total ~0.96 pp anualizado, ou ~3.6% do CAGR.
- MaxDD portfolio praticamente imune: 10.78% → 10.83% (+5 bps).

**Verdict:** Phase 3.5b Task 7c **PASS** — edge é robusta à variação
de slippage no range retail realista (BR broker Rico/XP típico: 0-5
bps em ETFs grandes via smart routing; 10 bps é cauda pessimista).

## Citações

- Cost ablation methodology: `[advances_fin_ml, p.261-266]`.
- Winner configs frozen per iterações Phase 3 32/36/37/40 (Phase 3
  summary jornada `2026-04-17-0200-phase3-summary.md`).
- 15% IR BR por venda lucrativa: Investment Mandate §4.

## ⚠️ FLAGs documentais

1. **`cum_cost_pct` com valores absurdos em runs longos** (e.g. LETF
   56.3y a 10 bps mostra 2.94B%). Artefato do cálculo em
   `simulate_letf_rotation`/`simulate_tsmom`: `cum_cost += switch_cost_pct
   * equity` soma custo em unidades de equity compounded. Em runs de 56y
   com equity crescendo para trilhões, a "% cumulativa" perde sentido.
   Reportada no Iter 3 (Task 3 FLAG de $108T). Não bloqueia verdict —
   `cagr_pct` e `sharpe` são corretos (cost já foi deduzido da equity).
   Mitigação futura: renomear `cum_cost_pct` → `cum_cost_equity_units`
   ou calcular como `1 - exp(-Σ log(1 - switch_cost_pct)·n_switches)`.

2. **Range do spec (0-10 bps) é simétrico abaixo do baseline 15 bps**
   dos winners. Não testa o caso inverso (20+ bps institutional stress).
   Decisão do spec; se a produção live vir custos mais altos (ex: swap
   CFD Pepperstone em Path A, mas isso é Phase 3.5a), rodar
   `CANONICAL_SLIPPAGE_LEVELS_BPS` estendido é trivial (um arg).

## Pytest

608 → 617 (+9, todos passing slippage_sensitivity).

## Artefatos

- `src/ai_trade/backtest/metrics/slippage_sensitivity.py` (NEW)
- `scripts/run_slippage_sensitivity.py` (NEW)
- `tests/test_slippage_sensitivity.py` (NEW)
- `reports/phase3_5b/robustness/slippage_sensitivity.md`
- `reports/phase3_5b/robustness/slippage_sensitivity.json`

## Próximo

Task 7d — Allocation alternativa (EW vs IVP/HRP/RP/MV) re-rodando o
3-leg com weights alternativos. EW já é o PASS; confirmar ou trocar.
