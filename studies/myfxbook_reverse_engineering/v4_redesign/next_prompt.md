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

**Tarefas elegiveis (dependencias satisfeitas):**
- `006-pipeline-wire-fase1` (depends: 002 ✓ + 003 ✓ + 004 ✓ + 005 ✓) —
  UNICA elegivel agora. Fecha o trio Fase 1 (002+005 expostos no pipeline,
  004 promovido ao veredito agregado) destravando 007 (batch run) e 008
  (final report).

**Tarefa recomendada: 006-pipeline-wire-fase1**

Spec resumido em
`studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md` (linhas 66-74).

### Contexto de 006-pipeline-wire-fase1

Wire `pre_decode_screen` (task 002) e `adversarial_validator` (task 005) em
`studies/myfxbook_reverse_engineering/workbench/pipeline.py` como flags
opcionais. Promover `passes_mandate_24()` (task 004) ao output do pipeline
quando os campos relevantes estao populados. Garantir backward-compat
(pipeline sem flags continua rodando como antes).

Interface alvo:

```bash
uv run python studies/myfxbook_reverse_engineering/workbench/pipeline.py \
    --system-id 1407880 \
    --enable-pre-screen \
    --enable-adversarial \
    --out-dir /tmp/v4_smoke_1407880
```

Comportamento esperado:

- `--enable-pre-screen`: roda `pre_decode_screen.run_screen(system_id, ...)`
  ANTES do mining; serializa `pre_decode_screen.json` no out_dir; se decision
  != "GO" e flag `--abort-on-pre-screen-stop` setada, encerra com exit code
  != 0 e nao gera synthetic. Por padrao, segue o pipeline com warning na
  pipeline_summary.
- `--enable-adversarial`: APOS `run_backtest()` produzir `synthetic_trades`,
  chama `adversarial_validate(real_trades, synthetic_trades)` e adiciona ao
  `pipeline_summary.json`:
  - `adversarial_auc`
  - `adversarial_ci_low_95`, `adversarial_ci_high_95`
  - `adversarial_n_real`, `adversarial_n_synthetic`, `adversarial_n_features`
  - `adversarial_top_features` (lista top-5 keys de feature_importance)
  - `adversarial_notes`
- Veredito agregado §2.4: quando `pipeline_summary` tem campos suficientes,
  computar `passes_mandate_24()` via `gates.compute_gates(...)` e expor em
  `pipeline_summary["mandate_24_pass"]` + `pipeline_summary["mandate_24_failed"]`.
  Em Fase 1, normalmente `pbo` e `wf_purged` ainda sao `None`.

### Smoke test obrigatorio em system 1407880

Apos wire, rodar pipeline com ambas as flags em system 1407880 (o decoy
demo system com is_live warning). Validar:
1. `pipeline_summary.json` contem campos novos.
2. `pre_decode_screen.json` existe.
3. `adversarial_auc` e numero entre 0 e 1.
4. Pipeline sem flags em system 1407880 continua produzindo o mesmo output
   pre-006 (verificar `pipeline_summary.json` schema preserved).

### Backward-compat checks

- `tests/myfxbook_pipeline/` baseline 795 nao quebra.
- Smoke test antigo do pipeline (se houver) continua passando.
- Callers existentes em `scripts/run_replicator_batch.py` (se chamam
  `pipeline.run_pipeline(...)`) nao precisam de mudanca.

### Citacoes obrigatorias

- `[advances_fin_ml, ch.5]` — adversarial validator semantica.
- `[advances_fin_ml, p.273-275]` — DSR como hard gate (via passes_mandate_24).
- `[advances_fin_ml, p.208-222]` — PBO opcional via cpcv_result kwarg.
- `[evidence_based_ta, p.325-328]` — MCPT no pre-screen.

## Guardrails permanentes

- Capital 100% Plano C; Plano A DORMANT
- Sem paper/live
- Sem alterar `frozen_rules/`, `docs/investment-mandate.md`, ou outras hunts
- Sem otimizar threshold apos ver resultado
- Sem usar PnL futuro / oracle / cherry-pick
- Sem aceitar single-asset winner (regra para tasks Fase 2+ que produzem rules)
- Toda decisao tecnica cita livro `[book.slug, p.X]`
- Sem commit/push

## Output esperado da sessao (checklist do PROTOCOL.md "Output esperado")

- [ ] PROGRESS.md atualizado (task 006 → DONE/FAILED/BLOCKED)
- [ ] iterations/006-pipeline-wire-fase1/PRE_REG.md
- [ ] iterations/006-pipeline-wire-fase1/RESULTS.json
- [ ] iterations/006-pipeline-wire-fase1/SUMMARY.md
- [ ] iterations/006-pipeline-wire-fase1/run.log (saida do smoke test 1407880)
- [ ] next_prompt.md reescrito apontando para 007-fase1-batch-run
- [ ] Baseline 795 testes preservados (sem novas falhas; 3 em
      test_macro_data_loader.py sao pre-existentes)
- [ ] Pipeline sem flags em system 1407880 produz output identico ao pre-006

NAO INICIE TASK 007 NESTA SESSAO. Uma task por sessao.

Se task 006 ja estiver DONE em PROGRESS.md, identifique a proxima elegivel
(007-fase1-batch-run) e execute.

Se TODAS as tasks estiverem DONE, escreva em next_prompt.md "STOP — pipeline v4
concluido, ver `_diagnostics/PIPELINE_V4_FINAL.md`" e encerre sem rodar nada.
