# 2026-04-17 22:00 — Phase 3.5b-addendum Task C1 [PLANO B] [SWING BROKER]: módulo `rebalance_modes.py` + 28 testes (670 → 698)

**Verdict:** ✅ módulo pronto; zero regressão no baseline; C2/C3 agora podem consumir as 3 funções puras. Tests +28, `.venv/bin/pytest -q` → **698 passed**.

## O que foi feito

Criado `src/ai_trade/backtest/metrics/rebalance_modes.py` (~320 loc) com 3 funções puras e dois data classes:

1. **`apply_daily_rebalance(returns_df, target_weights, initial_capital=1.0)`**
   Replica exatamente a convenção de `portfolio_combiner.blend_equal_weight`: `port_r_t = Σ w_j · r_{j,t}`, equity = `(1+port_r).cumprod() · initial_capital`. Drift ≡ 0, zero eventos tributários. É o **baseline teórico** do winner 3-leg EW. Citação `[advances_fin_ml, p.298-299]`.

2. **`apply_monthly_sell_rebalance(returns_df, target_weights, tax_rate=0.15, rebalance_freq='M')`**
   Per-bar aplica o retorno a cada perna; no último bar de cada mês calcula `Δ_j = w_target · T - E_j`, vende as overweights (Δ<0) realizando ganho = `sold · (1 − basis/equity)`, paga `max(0, gain) · tax_rate`, e aloca o pool líquido pro-rata aos underweights. Cost basis rastreado por perna (proporcional, não FIFO — documentado como simplificação). Tax reduz portfolio total — post-rebal weights não chegam exato ao target quando tax > 0 (residual drift mensurável).

3. **`apply_monthly_cashflow_rebalance(returns_df, target_weights, monthly_deposit, rebalance_freq='M')`**
   Sem sells, sem tax. No último bar de cada mês, deposita `monthly_deposit` **100% na perna mais subponderada** (`argmax(target - actual_w)`). Quando `monthly_deposit=0`, degenera em puro buy-and-hold (weights drift, zero rebalance). Model de disciplined monthly contribution retail no broker BR.

Todas as 3 retornam `RebalanceResult`:

- `equity` (Series), `leg_equity` (DataFrame), `weights` (DataFrame post-rebal), `drift` (DataFrame `|actual − target|` per leg per bar), `taxable_events` (list[`TaxableEvent`]), `total_tax_paid`, `total_deposits`, properties `returns` e `max_drift`.

## Tests (`tests/test_rebalance_modes.py`, 28 total — spec exige ≥15)

- **Validation (9)**: rejeita não-DataFrame, índice não-datetime, empty, NaN, weights não somando 1, weights negativos, colunas mismatch, tax_rate fora de [0, 1), deposit negativo.
- **Rebalance dates (2)**: escolhe último bar real de cada mês; robusto a holidays/meses faltantes.
- **Daily (5)**: equity coincide com `(1 + Σ w·r).cumprod()` a rtol 1e-12; weights pinned; drift ≡ 0; zero taxable events; 3-leg portfolio arithmetic verified.
- **Monthly-sell (7)**: zero returns ⇒ zero tax; tax fires só em rebal dates; drift cai em rebal dates; ganho realizado = 0 ⇒ zero tax; ganho > 0 ⇒ tax exatamente `0.15 · gain`; `tax_rate=0.15` reduz equity final vs `tax_rate=0.0`; retorna `RebalanceResult`/`TaxableEvent` types.
- **Monthly-cashflow (5)**: `deposit=0` ⇒ buy-and-hold exato; deposit vai pra perna subponderada (leg0 +1%/dia vs leg1 flat ⇒ todos os $100 ao leg1); zero tax; drift cai em rebal dates; equity total cresce por `n_rebal × deposit` em cenário flat.

## Pytest

```
$ .venv/bin/pytest -q
698 passed in 9.63s
```

670 → 698 (+28). Zero regressão nos 670 existentes.

## Constraints respeitadas

- ❌ Sem modificar lógica de `strategies/*.py`, `portfolio_3leg.py`, `portfolio_combiner.py`, `synthetic_letf.py`. ✅ Apenas adicionado módulo novo.
- ✅ Citações `[advances_fin_ml, p.298-299]` (baseline fixed weights), Investment Mandate §4 (15 % IR BR), `[leverage_for_the_long_run, p.17, Table 8]` (drift-vs-tax framing).
- ✅ Tag `[PLANO B]` / `[SWING BROKER]` no header + docstring.
- ✅ Winners imutáveis — nenhum report de `reports/phase3_5b/*` tocado.
- ✅ Branch `phase3.5b/winners-validation-20260417` (loop auto-commita).

## Decisão deferida para C2/C3

O módulo deixa 4 pontos em aberto para os scripts downstream:

1. **Janela e capital inicial default** para comparison_3leg.md e comparison_2leg.md — C2/C3 especificam via spec §Task C `reports/phase3_5b/variants/rebalance_modes/`.
2. **Métricas de saída** da tabela comparativa: {CAGR, Sharpe, MaxDD, Max drift %, # taxable events/ano, IR paid/ano} — trivial via `RebalanceResult` + `metrics/performance.py` existente.
3. **Hipótese 2-leg menos sensível a drift** — a testar em C3 (ρ alta entre LETF e QQQ deve manter weights próximos mesmo com deriva mensal).
4. **Valor operacional `monthly_deposit`**: spec sugere `0.5 % · initial_capital` (~$50/mo para $10k). Script C2 fixará esse parâmetro; tests cobrem edge cases incluindo $0.

## Próximo passo

Iteração 21 → Task C2: `reports/phase3_5b/variants/rebalance_modes/comparison_3leg.md` com tabela 3 modes × 6 métricas + plot drift-per-leg sobre 21 anos (janela LETF+QQQ+GLD comum 2004-11 → 2026-04, ou 1970-2026 se GLD dropado).

## Arquivos

- `src/ai_trade/backtest/metrics/rebalance_modes.py` (novo, +320 loc)
- `tests/test_rebalance_modes.py` (novo, 28 tests)

## Referências

- `specs/phase_3_5b_addendum_operational.md` §Task C1
- `[advances_fin_ml, p.298-299]`
- `[leverage_for_the_long_run, p.17, Table 8]`
- Investment Mandate §4 (BR 15 % IR em swing)
