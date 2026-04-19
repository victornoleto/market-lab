# 2026-04-17 2315 — Phase 3.5b addendum Task C4: threshold rebalance sweep [PLANO B] [SWING BROKER]

## Verdict

**PASS — fallback operacional documentado, winner intocado.** O sweep de
cadências drift-triggered sobre o 3-leg EW winner (LETF + QQQ + GLD)
responde a pergunta operacional do usuário sobre frequência de DARFs:

> "Rebalance mensal = 12 DARFs/ano + bookkeeping. Inside-leg já gera
> ~12 trades taxáveis/ano só da lógica. Monthly-sell dobra pra ~24/ano
> — inviável operacionalmente."

Threshold 5pp preserva **95% do Sharpe diário** (2.002 vs 2.108) a
apenas **1.31 DARFs/ano** do rebal layer — 9× menos que monthly_sell.
Threshold 10pp oferece 0.61 DARFs/ano a 94% do Sharpe. Production
default continua **inalterado**: 3-leg EW daily (Sharpe 2.108, CAGR
25.56%, MaxDD 10.86%).

## Contexto

Phase 3.5b main (iter 15) + Phase 3.5b-addendum Tasks A/B/C1-3/D
fecharam com 8 tasks PASS e 28 unit tests para o módulo
`rebalance_modes.py`. Três cadências de calendário cobertas:
`daily` / `monthly_sell` / `monthly_cashflow`. Falta uma cadência
**event-driven**, que é o padrão institucional real `[advances_fin_ml,
p.275-278]` — rebalancear só quando o portfólio realmente precisa
(drift ultrapassa threshold), não por relógio.

Task C4 preencheu essa lacuna. Single PR, single commit-equivalente
(auto-commit da iter 24 do loop).

## O que foi feito

### 1. Módulo — nova 4ª função em `rebalance_modes.py`

```python
def apply_threshold_rebalance(
    returns_df, target_weights, threshold_pp,
    initial_capital=1.0, tax_rate=0.15,
) -> RebalanceResult
```

* Mesma shape de retorno das outras 3 funções (`RebalanceResult`
  {equity, leg_equity, weights, drift, taxable_events,
  total_tax_paid, total_deposits=0}).
* Mecânica idêntica ao `apply_monthly_sell_rebalance` **exceto** o
  gatilho: em vez de "último dia do mês", rebalança quando
  `max|actual_w - target_w| > threshold_pp/100` pós-aplicação do
  retorno da barra.
* Cost basis proporcional, 15% IR BR no ganho realizado do overweight
  vendido, pool de proceeds líquido de tax distribuído aos
  underweights.
* Duas degeneracies documentadas + testadas:
  - `threshold_pp = 0` → rebalanceia toda barra (mas paga tax, diferente
    do `apply_daily_rebalance` que é tax-free no rebal layer).
  - `threshold_pp = ∞` (ou valor grande que nunca cruza) → pure
    buy-and-hold, zero eventos.
* Validação rejeita `threshold_pp < 0` e `tax_rate ∉ [0, 1)`.

Regra de ouro respeitada: **nenhuma alteração** nas 3 funções
pré-existentes. Apenas append, zero mudança de lógica.

### 2. Tests — 11 novos cases em `tests/test_rebalance_modes.py`

Classe `TestThresholdRebalance`:

1. `test_zero_threshold_rebalances_on_every_drifted_bar` — threshold=0
   com dispersão positiva dispara quase toda barra.
2. `test_infinite_threshold_equals_buy_and_hold` — threshold=1e9
   reproduz exatamente o caminho BH (pct-change-by-pct-change).
3. `test_trigger_cross_is_strict_greater_than` — gatilho é `>`,
   não `≥` (evita disparos fantasma quando drift chega exatamente
   no limite).
4. `test_higher_threshold_reduces_events` — 5pp > 10pp > 20pp em
   número de eventos numa série estocástica longa (750 barras).
5. `test_tax_per_event_matches_realized_gain` — todo `TaxableEvent`
   satisfaz `tax_paid = 0.15 × max(0, realized_gain)`; soma bate
   com `total_tax_paid`.
6. `test_drift_resets_on_rebalance_dates` — com `tax_rate=0`, drift
   pós-rebal vai a zero exato nas datas dos eventos.
7. `test_zero_tax_rate_produces_tax_free_events` — `tax_rate=0`
   com eventos disparando tem `ev.tax_paid == 0` em todos.
8. `test_returns_RebalanceResult_with_event_dates_in_index` —
   tipo correto; toda `ev.date` está no índice do input.
9. `test_three_leg_threshold_preserves_sum_of_leg_equity` — invariante:
   `sum(leg_equity, axis=1) == equity` em toda barra, mesmo com
   redistribuição de rebal.
10. `test_rejects_negative_threshold` (em TestValidation).
11. `test_rejects_bad_threshold_tax_rate` (em TestValidation).

Plus adicionei 2 cases de input-validation no `TestValidation`.

**Pytest: 698 → 709** (+11, zero regressão). Janela de tempo:

```
.venv/bin/pytest -q  →  709 passed in 10.11s
```

### 3. Sweep script — `scripts/run_phase3_5b_task_c4_threshold_rebalance.py`

Rodado na janela LONGEST-available GLD-limited **2004-11-18 →
2026-04-14** (21.36 yrs, 5383 barras), capital inicial $100k, 15% IR
BR. Cadências testadas:

* `daily` (winner, referência)
* `threshold_5pp`, `threshold_10pp`, `threshold_15pp`, `threshold_20pp`
* `annual_only` (monthly_sell com freq="Y")
* `never` (threshold=1e9)

### 4. Tabela consolidada (do `threshold_sweep.md`)

| Mode             | CAGR    | Sharpe | ΔSharpe | MaxDD   | Max drift | Mean drift | Events | Dates/yr | IR/yr    | Total IR  |
|------------------|---------|--------|---------|---------|-----------|------------|--------|----------|----------|-----------|
| daily (winner)   | 25.56%  | **2.108** | +0.000 | 10.86% | 0.00%   | 0.00%      | 0      | 0.00     | $0       | $0        |
| threshold 5pp    | 24.66%  | 2.002  | −0.106  | 11.10%  | 4.99%     | 2.27%      | 31     | **1.31** | $23,815  | $508,715  |
| threshold 10pp   | 25.47%  | 1.990  | −0.118  | 11.12%  | 10.00%    | 4.08%      | 14     | 0.61     | $20,978  | $448,116  |
| threshold 15pp   | 26.35%  | 1.972  | −0.136  | 12.24%  | 14.97%    | 7.64%      | 8      | 0.37     | $17,582  | $375,579  |
| threshold 20pp   | 27.15%  | 1.972  | −0.136  | 12.32%  | 19.99%    | 9.46%      | 6      | 0.28     | $21,680  | $463,099  |
| annual only      | 25.07%  | 1.967  | −0.141  | 11.56%  | 13.39%    | 3.36%      | 28     | 1.08     | $22,001  | $469,973  |
| never (BH)       | 40.33%* | 1.881  | −0.226  | 17.99%  | 65.62%    | 43.89%     | 0      | 0.00     | $0       | $0        |

*`never`'s CAGR é inflado pela deriva não-limitada do LETF (que cresce
para ~56% do portfólio no fim da janela). É "return alpha" só no papel
— na prática é concentração.

### 5. Findings operacionais

* **Threshold 5pp é o melhor-Sharpe event-driven**: 2.002 (95.0% do
  daily) a 1.31 DARFs/yr do rebal layer. Comparado ao C1's
  `monthly_sell` (Sharpe 1.964, 17.9 events/yr, IR/yr $30,740), é
  estritamente superior em Sharpe, tax drag e bookkeeping.
* **Threshold 10-15pp são os aggressive-low-DARF**: 0.4-0.6
  rebal-dates/yr a ~94% do Sharpe diário. CAGR marginalmente *maior*
  que daily porque a deriva acumula na perna de maior compounding
  (LETF), mas custo em Sharpe aparece.
* **`annual_only` é dominado**: Sharpe 1.967 a 1.08 dates/yr, pior que
  threshold 5pp na mesma escala de DARFs (2.002 a 1.31 dates/yr).
  Tempo-triggered desperdiça rebals quando o portfólio está perto do
  target e ignora rebals necessários no meio do ano. Information-driven
  vence time-driven no mesmo budget de DARFs.
* **`never` (pure BH)** mostra o piso: 0.226 de Sharpe perdidos vs
  daily. Threshold recupera a maior parte desse gap a fração do custo
  fiscal do calendar rebal.

### 6. Tradução operacional — DARFs/ano

O investidor BR retail emite DARF por mês com ganho realizado positivo.
**DARFs/yr ≈ datas únicas de rebalance/ano** (múltiplas pernas vendidas
no mesmo dia consolidam em 1 DARF). O rebal layer é **aditivo** aos
~12 inside-leg DARFs/yr já existentes (regime flips LETF + breakouts
Donchian QQQ/GLD).

| Mode             | DARFs/yr (rebal) | Total DARFs/yr est. |
|------------------|------------------|---------------------|
| daily (winner)   | 0.00             | 12.0                |
| threshold 5pp    | 1.31             | 13.3                |
| threshold 10pp   | 0.61             | 12.6                |
| threshold 15pp   | 0.37             | 12.4                |
| threshold 20pp   | 0.28             | 12.3                |
| monthly_sell     | ~18 (C1 ref)     | ~30                 |
| annual only      | 1.08             | 13.1                |
| never (BH)       | 0.00             | 12.0                |

Monthly_sell é efetivamente **2× pior** em DARFs que o pior threshold,
e ainda tem Sharpe inferior. Thresholding domina.

## Decisão final C4

1. **Production default inalterado**: 3-leg EW daily (`portfolio_3leg`
   daily rebal, Sharpe 2.108) continua o recommend deploy.
2. **Fallback operacional preferido**: threshold 5pp no 3-leg EW para
   usuário que considera rebal diário proibitivo.
3. **Aggressive-low-DARF fallback**: threshold 10pp ou 15pp se
   bookkeeping for o constraint dominante.
4. **Rejected**: `monthly_sell` (dominado por threshold em Sharpe, tax
   e DARFs); `annual_only` (dominado por threshold no mesmo DARF
   budget); `never` (pior Sharpe, risco de concentração).

## Artefatos produzidos

- `src/ai_trade/backtest/metrics/rebalance_modes.py` — 4ª função
  `apply_threshold_rebalance` (+147 loc).
- `tests/test_rebalance_modes.py` — +11 testes (classe
  `TestThresholdRebalance` + 2 cases em `TestValidation`).
- `scripts/run_phase3_5b_task_c4_threshold_rebalance.py` — sweep
  executor (~380 loc).
- `reports/phase3_5b/variants/rebalance_modes/threshold_sweep.md` —
  tabela + interpretação + recomendação operacional.
- `reports/phase3_5b/variants/rebalance_modes/threshold_sweep_summary.json`
  — snapshot estruturado.
- `reports/phase3_5b/variants/rebalance_modes/threshold_sweep_events.png`
  — DARFs/yr vs Sharpe vs cadência.
- Updates:
  - `reports/phase3_5b/variants/rebalance_modes/README.md` — seção
    "Threshold-based rebalancing (Task C4)" + production
    recommendation updated.
  - `reports/phase3_5b/variants/rebalance_modes/implementation_notes.md`
    — seção 4.5 "Threshold trigger (C4)" + contratos.
  - `reports/phase3_5b/variants/README.md` — linhas C-5/C-6 na tabela
    comparativa.
  - `reports/phase3_5b/README.md` — 1-line mention + directory map
    atualizado.
  - `jornada/2026-04-17-2045-phase3.5b-full-validation-summary.md` —
    linhas C₅/C₆ na tabela + módulo atualizado pra 4 funções.

## Citações

- Threshold rebalancing como prática institucional:
  `[advances_fin_ml, p.275-278]` (López de Prado, drift-triggered
  trading rules).
- Baseline daily reset: `[advances_fin_ml, p.298-299]`.
- Drift vs tax tradeoff framing:
  `[leverage_for_the_long_run, p.17, Table 8]`.
- 15% IR BR sobre ganhos realizados: Investment Mandate §4.

## Pytest baseline

670 (iter 15) → 698 (iter 20, C1) → **709** (iter 24, C4). Zero
regressão. Winners imutáveis.

## Status

**C4 PASS. Addendum completo. `status: done` no memory.md.**
