# PRE_REG — Task 004: gates-dsr-hard

**Criado ANTES de codar logica.** Contrato congelado da task.

## Identificacao

- **Task ID:** 004-gates-dsr-hard
- **Fase:** 1
- **Sessao:** 2026-05-04
- **Citacao em TASKS.md:**
  > "Refatorar `shared/gates.py` — promover DSR de informativo para hard gate
  > (p<0.05 bloqueia). Adicionar PBO via cpcv.py como gate. Manter CAGR/MDD
  > warning-only conforme mandate §2.2/§2.3. Atualizar testes existentes."
- **Spec detalhado:** `tasks/004-gates-dsr-hard.md`
- **Depende de:** task 003 DONE (cpcv.py com `cscv_pbo`, `CPCVResult`,
  `PBO_THRESHOLD`).

## Escopo (minimo)

1. Estender `shared/gates.py` `GateStats` com novos campos:
   - `pbo: float | None` — preenchido a partir de `CPCVResult`
   - `pbo_pass: bool | None`
   - `wf_purged_n_positive: int | None`, `wf_purged_total: int | None`,
     `wf_purged_pass: bool | None`
   - propriedades de leitura compativeis com a interface ideal do task spec
     (`dsr_p`, `sharpe_bootstrap_ci_low_999`, `oos_bootstrap_ci_low_999`,
     `wf_simple_positive`, `wf_simple_total`)
   - `cagr` / `max_drawdown` placeholders (warning-only, retornam `None` em
     gates baseados em pips — preserva contrato semantico mandate §2.2/§2.3)

2. Implementar `GateStats.passes_mandate_24() -> tuple[bool, list[str]]`
   avaliando os 5 hard gates §2.4:
   | Gate | Threshold |
   |---|---|
   | `sharpe_bootstrap_ci_low_999` | `> 0` `[advances_fin_ml, p.196-211]` |
   | `oos_bootstrap_ci_low_999` | `> 0` (idem) |
   | `dsr_p` | `< 0.05` `[advances_fin_ml, p.273-275]` |
   | `pbo` | `< 0.50` `[advances_fin_ml, p.208-222]` |
   | `wf_purged_positive` | `>= 6` quando aplicavel `[testing_tuning, p.148-162]` |

3. Estender `compute_gates()` com parametros opcionais:
   - `cpcv_result: CPCVResult | None = None` — se fornecido, popula `pbo` e
     `pbo_pass`
   - `wf_purged: tuple[int, int] | None = None` — se fornecido como
     `(n_positive, total)`, popula campos `wf_purged_*`

4. Adicionar testes unitarios em `tests/myfxbook_pipeline/test_gates_v4.py`
   cobrindo (`>= 7` testes):
   - DSR p < 0.05 → passes
   - DSR p >= 0.05 → falha com `dsr_p` em failed_gate_names
   - PBO < 0.50 → passes
   - PBO >= 0.50 → falha
   - Combinacao parcial (Sharpe ok + DSR fail → fail total)
   - CAGR/MDD altos NAO bloqueiam (warning-only)
   - WF purgado None NAO bloqueia (opcional)
   - Smoke test integrado: `compute_gates()` aceita `cpcv_result` e popula `pbo`.

NAO mexer em outros modulos. NAO criar `tests/test_gates.py` (referencia
incorreta no spec; arquivo nao existe — `test_grid_gates.py` e modulo distinto
no Plano A DORMANT).

## Inputs esperados

- `studies/myfxbook_reverse_engineering/shared/cpcv.py` (task 003 DONE)
- `studies/myfxbook_reverse_engineering/shared/gates.py` (versao atual)
- Para testes: dataclass `GateStats` instanciada com `GateBlock` minimal
  (sem trades reais — testes diretos em metricas).

## Outputs esperados

### Codigo

- `studies/myfxbook_reverse_engineering/shared/gates.py` — extensao com:
  - import `from .cpcv import CPCVResult, PBO_THRESHOLD`
  - novos campos optional em `GateStats`
  - propriedades de leitura
  - `passes_mandate_24()` method
  - `compute_gates()` aceita kwargs novos opcionais
  - documentacao com citacoes em todas decisoes

- `tests/myfxbook_pipeline/test_gates_v4.py` — preenche skeleton com >=7
  testes unitarios.

### Iteracao

- `iterations/004-gates-dsr-hard/PRE_REG.md` (este arquivo)
- `iterations/004-gates-dsr-hard/run.log` (saida pytest)
- `iterations/004-gates-dsr-hard/RESULTS.json`
- `iterations/004-gates-dsr-hard/SUMMARY.md`

## Citacoes obrigatorias

| Decisao | Citacao |
|---|---|
| DSR p < 0.05 hard gate | `[advances_fin_ml, p.273-275]` (Bailey & Lopez 2014) |
| Sharpe bootstrap CI 99.9% low > 0 | `[advances_fin_ml, p.196-211]` |
| PBO < 0.50 hard gate | `[advances_fin_ml, p.208-222]` |
| WF purgado >= 6/8 | `[testing_tuning, p.148-162]` |
| CAGR / MDD warning-only | `docs/investment-mandate.md §2.2/§2.3` |
| PBO complementa WF (nao substitui) | `DEAD_ENDS.md` ("PBO substituindo WF8 rejeitado") |

## Decision rules (frozen)

- `dsr_p` is None → falha (`dsr_p` em failed list — sem dado, gate nao
  validavel)
- `dsr_p >= 0.05` → falha
- `pbo` is None → opcional, nao bloqueia (nao ha mining em Fase 1)
- `pbo >= 0.50` → falha
- `wf_purged_n_positive` is None → opcional, nao bloqueia
- `wf_purged_n_positive < 6` → falha
- `boot_lo` (full or oos) is None ou <= 0 ou nao finito → falha
- `cagr` / `max_drawdown` NUNCA aparecem em failed_gate_names (warning-only)

## Backward-compat preservada

Call sites existentes (`shared/_smoke_test.py`, `data/trades/11504701/`)
acessam:
- `compute_gates(df, system_id)` sem kwargs novos → continua funcionando
- `g.full.{n_days, n_trades, daily_mean, daily_std, sharpe, boot_lo, boot_hi,
  dsr_p}`
- `g.oos.{...}` ou `g.oos is None`
- `g.n_wf_positive`, `g.gate2_pass`, `g.gate3_pass`, `g.gate4_pass`,
  `g.gate6_pass`, `g.sharpe_optimistic`
- `gates.format_gates_report(g, generated=...)`

Nenhum desses contratos quebra. Novos campos sao opcionais com default `None`.

## Criterios de aceite (verificaveis)

1. `tests/myfxbook_pipeline/test_gates_v4.py` adicionado, >= 7 testes, todos
   passam.
2. Baseline 768 testes pre-existentes nao regride (3 falhas pre-existentes em
   `test_macro_data_loader.py` toleradas — heranca da 001-003).
3. `tests/test_grid_gates.py` (modulo distinto Plano A DORMANT) continua
   passando sem mudanca.
4. `compute_gates()` chamada sem novos kwargs → comportamento identico ao
   anterior em campos compartilhados.
5. `passes_mandate_24()` retorna `(False, ['dsr_p'])` quando `dsr_p=0.10`.
6. `passes_mandate_24()` retorna `(False, ['pbo'])` quando `pbo=0.6` e demais
   gates passam.
7. CAGR / MDD altos jamais aparecem em `failed_gate_names`.

## Kill-switches (a task FALHA se ocorrer)

- Quebra em `shared/_smoke_test.py` (executado manualmente; manter
  retrocompat).
- Test `test_grid_gates.py` quebra → contaminacao com modulo errado, fix.
- Numero de testes < 768 ou nova falha em modulo nao tocado → regressao.
- `passes_mandate_24()` aceita CAGR como gate → bug semantico mandate §2.2.

## Allow-list de paths tocados

- `studies/myfxbook_reverse_engineering/shared/gates.py` (extensao)
- `tests/myfxbook_pipeline/test_gates_v4.py` (preenche skeleton)
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/004-gates-dsr-hard/**`
- `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md` (linha 004)
- `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md` (rewrite)
- `jornada/2026-05-04-XXXX-myfxbook-v4-task-004-*.md` (entrada nova)
- `jornada/README.md` (lista atualizada)

NADA fora dessa lista. `frozen_rules/`, `docs/investment-mandate.md`,
`src/ai_trade/backtest/grid/gates.py` (Plano A) nao tocados.
