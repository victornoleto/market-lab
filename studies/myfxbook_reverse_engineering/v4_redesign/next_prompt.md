# Prompt da proxima sessao limpa

Estamos no repo `/var/www/pessoal/ai-trade`, branch atual qualquer (NAO faca
commit/push).

Voce esta executando uma sessao automatica do loop do estudo
**MyFxBook Pipeline v4 Redesign**. Esta sessao e zerada — toda continuidade vem
de arquivos.

## Leia (nessa ordem) antes de qualquer acao

1. `CLAUDE.md`
2. `jornada/README.md` (so a secao "Onde estamos hoje")
3. `studies/myfxbook_reverse_engineering/v4_redesign/PROTOCOL.md`
4. `studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md`
5. `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md`
6. `studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md`
7. `studies/myfxbook_reverse_engineering/v4_redesign/DEAD_ENDS.md`

## Tarefa desta sessao

Identifique a primeira task em `PROGRESS.md` com `status=PENDING` cujas
dependencias estao todas `DONE`, e execute-a seguindo `PROTOCOL.md`.

**Tarefas elegiveis (dependencias satisfeitas, 001+002+003 estao DONE):**
- `004-gates-dsr-hard` (depends: 003 ✓)
- `005-adversarial-validator` (depends: 001 ✓)

**Tarefa recomendada: 004-gates-dsr-hard** — destrava 006-pipeline-wire-fase1
que destrava 007/008 (final da Fase 1). 005 fica para uma sessao paralela ou
subsequente.

Spec detalhado em
`studies/myfxbook_reverse_engineering/v4_redesign/tasks/004-gates-dsr-hard.md`.

### Contexto de 004-gates-dsr-hard

`shared/cpcv.py` esta DONE (task 003). Importar `cscv_pbo`, `CPCVResult` e
`PBO_THRESHOLD` diretamente.

Refatorar `shared/gates.py` para promover DSR de informativo para hard gate
e adicionar PBO como gate. Mandate §2.4:

| Gate | Threshold | Source |
|---|---|---|
| Sharpe bootstrap CI 99.9% low | > 0 | `[advances_fin_ml, p.196-211]` |
| OOS bootstrap CI 99.9% low | > 0 | mesmo |
| DSR p | < 0.05 | `[advances_fin_ml, p.273-275]` |
| **PBO (NOVO)** | < 0.50 | `[advances_fin_ml, p.208-222]` |
| WF purgado | >= 6/8 (quando aplicavel) | `[testing_tuning, p.148-162]` |

CAGR e MDD ficam em `GateStats` apenas para reporting (warning-only tiers
mandate §2.2/§2.3).

`GateStats.passes_mandate_24() -> tuple[bool, list[str]]` retorna verdict +
lista de gates que falharam.

**IMPORTANTE — escopo de teste do projeto inteiro:** alem de testes novos em
`tests/myfxbook_pipeline/test_gates_v4.py`, atualizar `tests/test_gates.py`
existente. Verificar `tests/test_grid_gates.py` que ja chama `pbo()` (via
`src/ai_trade/backtest/grid/gates.py`) — esse e codigo de outro ramo (Plano A
DORMANT) e deve continuar funcionando sem mudanca. Se houver colisao de nomes
entre `studies/myfxbook_reverse_engineering/shared/gates.py` e
`src/ai_trade/backtest/grid/gates.py`, manter os dois separados (sao modulos
distintos).

7+ testes unitarios cobrindo:
- DSR p < 0.05 → passes
- DSR p >= 0.05 → fails com 'dsr_p' em failed_gate_names
- PBO < 0.50 → passes
- PBO >= 0.50 → fails
- Combinacoes parciais (Sharpe ok + DSR fail → fail total)
- CAGR/MDD altos NAO bloqueiam (warning-only)
- WF purgado opcional (None nao bloqueia)

## Guardrails permanentes

- Capital 100% Plano C; Plano A DORMANT
- Sem paper/live
- Sem alterar `frozen_rules/`, `docs/investment-mandate.md`, ou outras hunts em paralelo
- Sem otimizar threshold apos ver resultado
- Sem usar PnL futuro / oracle / cherry-pick
- Sem aceitar single-asset winner (regra para tasks Fase 2+ que produzem rules)
- Toda decisao tecnica cita livro `[book.slug, p.X]`
- Sem commit/push

## Output esperado da sessao (checklist do PROTOCOL.md "Output esperado")

- [ ] PROGRESS.md atualizado (task 004 → DONE/FAILED/BLOCKED)
- [ ] iterations/004-gates-dsr-hard/PRE_REG.md
- [ ] iterations/004-gates-dsr-hard/RESULTS.json
- [ ] iterations/004-gates-dsr-hard/SUMMARY.md
- [ ] iterations/004-gates-dsr-hard/run.log
- [ ] next_prompt.md reescrito apontando para proxima task elegivel
- [ ] Baseline ~770 testes preservados (sem novas falhas; 3 em
      test_macro_data_loader.py sao pre-existentes)

NAO INICIE TASK 005 OU 006 NESTA SESSAO. Uma task por sessao.

Se task 004 ja estiver DONE em PROGRESS.md, identifique a proxima elegivel
(005 ou 006), e execute.

Se TODAS as tasks estiverem DONE, escreva em next_prompt.md "STOP — pipeline v4
concluido, ver `_diagnostics/PIPELINE_V4_FINAL.md`" e encerre sem rodar nada.
