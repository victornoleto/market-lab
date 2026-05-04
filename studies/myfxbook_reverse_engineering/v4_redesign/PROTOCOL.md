# PROTOCOL — Como cada sessao limpa deve operar

Este protocolo define o **contrato de comportamento** de uma sessao de Claude
Code rodando uma task do v4 redesign. Cada sessao **e zerada** — nao tem memoria
da anterior. Toda continuidade vem de arquivos.

## Leitura obrigatoria no inicio (nessa ordem)

1. `CLAUDE.md` — instrucoes do projeto (Regras 1-3, mandate, citacoes)
2. `jornada/README.md` — estado humano do projeto (last "Onde estamos hoje")
3. `studies/myfxbook_reverse_engineering/v4_redesign/PROTOCOL.md` — este arquivo
4. `studies/myfxbook_reverse_engineering/v4_redesign/SPEC.md` — contrato frozen
5. `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md` — onde estamos
6. `studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md` — lista completa
7. `studies/myfxbook_reverse_engineering/v4_redesign/DEAD_ENDS.md` — abordagens descartadas
8. `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md` — prompt da sessao

Nao carregar todo o historico de iterations/. Use apenas o ultimo SUMMARY.md
quando relevante.

## Identificar a proxima task

1. Ler `PROGRESS.md` — encontrar a primeira task com `status=PENDING` cuja
   coluna `depends_on` esta toda `DONE`
2. Validar contra `TASKS.md` que a definicao bate
3. Ler `tasks/NNN-slug.md` para o spec detalhado
4. Se o spec estiver marcado como STUB, **detalhar o spec antes de implementar**
   (escolha pequena conservadora, citar livro, registrar no spec antes de codar)

Se nao houver task PENDING elegivel:
- Ou todas estao DONE → escrever em `next_prompt.md` "STOP — todas as tasks
  concluidas, ver PIPELINE_V4_FINAL.md"
- Ou ha bloqueio (BLOCKED, FAILED, dependencies em FAILED) → escrever em
  `next_prompt.md` "STOP — bloqueio em task NNN, intervencao humana necessaria"

## Executar a task

### Passo 1 — Pre-registro

Antes de codar/medir nada, criar `iterations/NNN-slug/PRE_REG.md` contendo:

- ID e nome da task
- Citacao da task em `TASKS.md` e `tasks/NNN-slug.md`
- O que sera implementado (escopo minimo)
- Inputs esperados (paths de arquivos existentes)
- Outputs esperados (paths novos a criar)
- Citacoes de livro para qualquer escolha tecnica
- Criterio de aceite (verificavel)
- Kill-switches (o que faz a task falhar)

### Passo 2 — Implementar minimo necessario

Regras:
- Nao criar framework grande
- Reutilizar infraestrutura existente em `studies/myfxbook_reverse_engineering/shared/`
- Nao tocar `frozen_rules/`, `data/trades/`, `_diagnostics/` antigos
- Nao mexer em outras parts do repo (backtest/, app/, jornada/ entries de outras hunts)
- Adicionar testes unitarios em `tests/myfxbook_pipeline/test_<modulo>.py` quando aplicavel
- Nao quebrar baseline 461 testes — rodar `pytest -x tests/` se mexer em modulo compartilhado

### Passo 3 — Verificar

Rodar:
- Os testes que vc adicionou
- Smoke test concreto descrito no spec (ex: rodar pipeline em system 1407880 e
  verificar que output existe)

Capturar saida em `iterations/NNN-slug/run.log`.

### Passo 4 — Documentar

Criar dois arquivos:

`iterations/NNN-slug/RESULTS.json` (parseable):
```json
{
  "task_id": "NNN-slug",
  "status": "DONE | FAILED | BLOCKED",
  "started_utc": "2026-MM-DDTHH:MM:SSZ",
  "completed_utc": "2026-MM-DDTHH:MM:SSZ",
  "files_created": [],
  "files_modified": [],
  "tests_added": [],
  "tests_passing": 0,
  "tests_total": 0,
  "metrics": {},
  "notes": "..."
}
```

`iterations/NNN-slug/SUMMARY.md` (humano, curto, ~1 pagina):
- Verdict (DONE/FAILED/BLOCKED)
- O que foi feito
- Citacoes usadas
- Caveats / decisoes nao-obvias
- Licao para a proxima task

### Passo 5 — Atualizar PROGRESS.md

Atualizar a linha da task: `PENDING` → `DONE` (ou `FAILED`/`BLOCKED`),
preencher `started`, `completed`, `notes`.

### Passo 6 — Atualizar next_prompt.md

Reescrever `next_prompt.md` apontando para a proxima task elegivel. Se a proxima
task for STUB, escolher um nivel de detalhe minimo viavel para a sessao seguinte
(nao fazer todo o spec; deixar um TODO claro).

### Passo 7 — Atualizar jornada (se progresso relevante)

Se a task entregou algo que conta como progresso (verdict, decisao de
arquitetura, modulo novo public-facing, decision gate), criar
`jornada/YYYY-MM-DD-HHMM-slug.md` e atualizar `jornada/README.md`.

Tasks puramente "scaffolding" ou "test-only" nao precisam de jornada.

### Passo 8 — Atualizar DEAD_ENDS.md (se aplicavel)

Se durante a task alguma abordagem foi tentada e descartada (ex: tentou usar
permutation_test do statsmodels mas teve bug numerico), registrar em
`DEAD_ENDS.md` para evitar reabertura.

## Regras de escopo

- **Uma task por sessao.** Nao iniciar a proxima.
- **Nao expandir escopo no meio.** Nova ideia vira proximo `next_prompt.md`.
- **Nao otimizar threshold apos ver resultado.** Pre-registro e contrato.
- **Nao usar PnL futuro / oracle / cherry-pick.**
- **Nao aceitar single-asset winner sem multi-asset confirmation.**
- **Nao fazer commit/push** a menos que a task explicitamente peca.

## Allow-list de paths que sessao pode modificar

Apenas estes paths podem ser tocados (criados/modificados/deletados):

- `studies/myfxbook_reverse_engineering/v4_redesign/**` (toda a estrutura do estudo)
- `studies/myfxbook_reverse_engineering/shared/**` (modulos novos e refactor)
- `studies/myfxbook_reverse_engineering/workbench/pipeline.py` (wiring tasks 006, 017)
- `studies/myfxbook_reverse_engineering/scripts/**` (run_replicator_batch e novos scripts)
- `studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_*.md` e `*.json` (reports)
- `tests/myfxbook_pipeline/**` (testes novos)
- `tests/test_gates.py` (apenas se task 004 — refactor de gates.py)
- `jornada/YYYY-MM-DD-HHMM-*.md` (entries de progresso)
- `jornada/README.md` (lista atualizada)
- `pyproject.toml` e `uv.lock` (apenas para dependencia LightGBM — task 005,
  decidido em SPEC.md)
- `data/news/**`, `data/ticks/**` (caches Fase 2A — tasks 009, 011)

Paths PROIBIDOS (mesmo com permissao do `--dangerously-skip-permissions`):

- `frozen_rules/**` (read-only, mandate §3)
- `docs/investment-mandate.md`
- Qualquer outro `studies/<other>/**` (parallel sessions hands-off)
- `app/**`, `backtest/**` core (paralelos)
- `data/trades/**`, `data/ohlc/**`, `data/tiingo/**` (cache existente — read-only)
- `systems/<id>/decoder/**`, `systems/<id>/decoding/**`, `systems/<id>/decoding_m1/**`
  (outputs frozen do R1; nao reescrever)

Tasks que precisarem violar allow-list devem **PARAR** e marcar BLOCKED em
PROGRESS.md com nota explicita pedindo intervencao humana.

## Como falhar

Se a task for impossivel (dependencia faltante, bug em modulo upstream,
infraestrutura nao disponivel):

1. Marcar task como `BLOCKED` ou `FAILED` em PROGRESS.md
2. Documentar em SUMMARY.md a razao precisa
3. Adicionar a DEAD_ENDS.md se a abordagem nao deve ser reaberta
4. Escrever `next_prompt.md` apontando para uma task alternativa elegivel ou
   pedindo intervencao humana

Nao tentar workarounds que violem guardrails (ex: usar PnL futuro pra "salvar"
a task). Falhar limpo e melhor que workaround silencioso.

## Validacao bloqueante externa

Quando o loop roda com `VALIDATOR_REQUIRED=1`, uma validacao read-only e executada
apos a sessao concluir a checklist e antes de iniciar a proxima task.

Contrato do validador:

- Ler os artefatos da iteracao (`PRE_REG.md`, `RESULTS.json`, `SUMMARY.md`,
  `run.log`) e os arquivos de governanca.
- Nao editar arquivos, nao commitar, nao fazer push.
- Responder com uma linha parseavel:
  - `VALIDATION_VERDICT: PROCEED` — a proxima task pode iniciar.
  - `VALIDATION_VERDICT: STOP` — o loop aborta com exit 5 para correcao.

Ausencia de verdict parseavel, timeout, ou erro do validador e tratado como
`STOP` fail-safe. Correcoes pos-STOP devem ser feitas em sessao separada e
documentadas no `SUMMARY.md`/`run.log` da task afetada.

## Citacoes obrigatorias (Regra 2 do CLAUDE.md)

Toda escolha tecnica em codigo, comentario, spec ou report cita livro:
`[book.slug, p.X]` ou `[book.slug, ch.Y]`.

Sem citacao, a escolha e invalida e a task falha o gate de qualidade.

## Output esperado da sessao (checklist final)

- [ ] PROGRESS.md atualizado
- [ ] iterations/NNN-slug/PRE_REG.md criado
- [ ] iterations/NNN-slug/RESULTS.json criado
- [ ] iterations/NNN-slug/SUMMARY.md criado
- [ ] iterations/NNN-slug/run.log com saida dos comandos
- [ ] next_prompt.md reescrito para a proxima task
- [ ] jornada/ entry criado (se progresso relevante)
- [ ] DEAD_ENDS.md atualizado (se aplicavel)
- [ ] Testes unitarios passando
- [ ] Baseline 461 testes nao quebrado (se modulo compartilhado tocado)
- [ ] Sem commit/push

Se algum item da checklist falhar, a task volta para `IN_PROGRESS` e a sessao
seguinte completa.
