# Phase 3.5b Task 7d [PLANO B] [SWING BROKER] — Allocation EW kept (5-way)

**Data:** 2026-04-17 16:45
**Branch:** `phase3.5b/winners-validation-20260417`
**Iter:** 11

## Contexto

Task 7d do `specs/phase_3_5b_winners_validation.md` pede para re-blendar
o portfolio 3-leg (LETF EMA100/2x + QQQ Donchian 20/10 + GLD Donchian
40/20) com cinco esquemas de pesos — EW, IVP, HRP, Risk-Parity (ERC) e
Min-Variance — e decidir se o EW continua sendo o default de produção.
Phase 3 A3d já tinha rodado os três primeiros (com Sharpe(OOS) EW ≈ 2.25
batendo IVP/HRP); aqui adicionamos os dois métodos faltantes para fechar
a Task 7d.

## O que foi feito

1. **Módulo `src/ai_trade/backtest/metrics/allocation_comparison.py`**
   (~430 loc):
   - `erc_weights(cov)` — ERC via formulação convexa log-barreira
     `min ½ wᵀΣw − (1/n)Σ log w_i` com L-BFGS-B (Spinu 2013 / Bourgeron
     et al. 2018). Optei pela log-barreira porque a iteração ingênua
     `w ← 1/(Σw)` **oscila para Σ diagonal** (alterna entre EW e IVP
     a cada passo). KKT da formulação convexa dá exatamente
     `w_i (Σw)_i = const`, a condição ERC de Maillard-Roncalli 2010.
   - `min_variance_weights(cov)` — long-only via SLSQP com `Σw=1, w≥0`.
   - `blend_risk_parity_3()` / `blend_min_variance_3()` — fitam pesos
     **só no IS** (`a.index ≤ is_end`), aplicam forward ao common window;
     mesmo contrato dos blenders existentes em `grid/portfolio_3leg.py`.
   - `compare_allocations_3()` — roda os 5 métodos, devolve
     `AllocationComparison` com pesos, Sharpe full/IS/OOS, CAGR, MaxDD,
     Vol, Diversification Ratio (Choueifaty-Coignard 2008) e equity final.
   - `select_default_allocation()` — regra de promoção: EW só perde se
     desafiante bater EW em **AMBOS** OOS Sharpe (≥ +0.05) **E** DR
     (≥ +0.05). Margem dupla protege contra ganhos cosméticos por
     estimation noise [advances_fin_ml, p.298-299].
   - `render_allocation_comparison_markdown()` — tabela única + bloco
     "Decision".
   - 15 testes unitários (`tests/test_allocation_comparison.py`):
     ERC para Σ diagonal vira inverse-vol; MV para Σ diagonal vira
     IVP; long-only constraint respeitado; ordem dos 5 métodos fixa;
     `to_dict()` round-trip; renderer; regra de promoção.

2. **Script `scripts/run_allocation_comparison.py`** (~150 loc):
   - Reusa `validate_phase3_winners` para configs winners + dados.
   - Common window = intersecção LETF (1970-) ∩ QQQ (2001-) ∩ GLD
     (2004-) → **5383 bars 2004-11-18 → 2026-04-14** (GLD-limited).
   - IS-end = `start + 0.60·duration` = **2017-09-21**, mesma fórmula
     do `run_a3d_3leg_portfolio._splits_for_window` (60/25/15).
   - Emite `reports/phase3_5b/robustness/allocation_comparison.{md,json}`.

## Resultados — EW domina OOS Sharpe; nenhum desafiante passa o filtro duplo

| method        | weights (LETF / QQQ / GLD) | Sharpe (full) | CAGR (full) | MaxDD | Sharpe IS | **Sharpe OOS** | DR (full) |
|---------------|---------------------------:|--------------:|------------:|------:|----------:|---------------:|----------:|
| equal_weight  |     0.333 / 0.333 / 0.333  |         2.108 |      25.56% | 10.86%|     1.971 |      **2.301** |     1.376 |
| ivp_static    |     0.121 / 0.502 / 0.377  |         1.985 |      19.19% |  8.83%|     1.809 |          2.229 |     1.435 |
| hrp           |     0.104 / 0.430 / 0.466  |         1.924 |      18.13% |  8.39%|     1.735 |          2.186 |     1.456 |
| risk_parity   |     0.192 / 0.393 / 0.415  |         2.050 |      20.96% |  9.15%|     1.882 |          2.283 |     1.453 |
| min_variance  |     0.000 / 0.574 / 0.426  |         1.741 |      15.47% |  7.52%|     1.536 |          2.024 |     1.385 |

Leitura:

- **EW vence em OOS Sharpe (2.301)** entre os 5 métodos. Risk-Parity
  (2.283) e IVP (2.229) ficam logo abaixo, e MV (2.024) é o pior.
- Os 4 métodos não-EW concentram peso em QQQ + GLD porque ambos têm σ
  menor que LETF (que carrega a alavancagem 2x). MV chega ao caso
  limite — coloca peso **zero em LETF** — e perde quase 10pp de CAGR.
- DR sobe de 1.376 (EW) para 1.456 (HRP) — diversificação melhor — mas
  o ganho é ≤ +0.08, abaixo da margem +0.05 que precisaria vir
  acompanhada de melhora ≥ +0.05 em OOS Sharpe simultaneamente.
- Risk-Parity é o melhor desafiante balanceado: ganha ΔDR de +0.077 e
  perde só ΔSharpe(OOS) de −0.018. Não atende nenhum dos dois lados
  do filtro.

**Decisão: EW mantido como default de produção.** A regra de promoção
não dispara porque nenhum challenger melhora **ambos** os critérios
simultaneamente. Citação: [advances_fin_ml, p.298-299] — a estimation
error em Σ tipicamente engole ganhos teóricos de IVP/HRP/MV em horizons
< 30y, e o naive 1/n é um Bayesian prior sólido absent strong evidence.

## Por que EW vence aqui

1. **LETF carrega o CAGR** (winner standalone CAGR ≈ 41%, OOS Sharpe
   1.724). Qualquer método baseado em variância (IVP/HRP/MV/RP) penaliza
   sua vol elevada e reduz seu peso, sacrificando retorno. EW é
   "agnóstico" e mantém o peso cheio.
2. **As 3 pernas têm Sharpes individuais positivos e bem separados em
   regime** (LETF on/off equity, QQQ/GLD cada um seu próprio Donchian).
   A diversificação já está embutida nos sinais; pesos extras
   "inteligentes" são marginais.
3. **MV → 0% LETF é caso de bordas**: o min-vol corner mata o CAGR
   sem ganho equivalente de Sharpe. Mostra empiricamente o problema do
   MV puro long-only com um asset alavancado.

## Hard rules respeitadas

- ✅ Janela longest per manifest (5383 bars GLD-limited igual à Task 6).
- ✅ Splits IS/OOS idênticos a Phase 3 A3d (60/40 do common window;
  IS-end 2017-09-21).
- ✅ Pesos não-EW fitados **só no IS** — OOS nunca vê post-IS Σ.
- ✅ Winners imutáveis (configs frozen iter 32/36/37/40).
- ✅ Citação [advances_fin_ml, p.297-313] em todas as decisões técnicas.
- ✅ Pytest 617 → **632 passed** (+15 testes ERC/MV/comparison).
- ✅ Branch isolada `phase3.5b/winners-validation-20260417`; nada em main.

## Próximo passo

Task 7e — correlação rolling 63d e 252d entre as 3 legs, identificar
janelas de alta correlação onde a diversificação quebra. Output:
plot + tabela de períodos críticos.

## Artefatos

- `src/ai_trade/backtest/metrics/allocation_comparison.py` (NEW, ~430 loc)
- `tests/test_allocation_comparison.py` (NEW, 15 tests)
- `scripts/run_allocation_comparison.py` (NEW, ~150 loc)
- `reports/phase3_5b/robustness/allocation_comparison.md` (rendered)
- `reports/phase3_5b/robustness/allocation_comparison.json` (machine)
