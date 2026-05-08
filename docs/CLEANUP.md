# CLEANUP.md — playbook de consolidação de repo

Procedimento padrão pra rodar um cleanup agressivo no `ai-trade` sem
perder informação relevante. Baseado no cleanup de 2026-04-24
(reduziu ~40% dos tests, removeu ~150 arquivos, zero regressão em
core engine). Log forense daquele run: `docs/CLEANUP_2026-04-24_LOG.md`.

Usar quando:
- Há acúmulo visível de fases/experiments DORMANT (arquivos que não
  são mais load-bearing no workflow ativo).
- Repo sente "pesado" (>50 arquivos soltos em uma pasta, >20 subpastas
  em reports/, etc.).
- User pede explicitamente consolidação.

NÃO usar:
- Se o projeto está no meio de um hunt ativo (estratégia sendo testada).
- Se há múltiplas sessões paralelas mexendo em áreas amplas — cleanup
  só em áreas que o user confirma estar "fechadas".

---

## Prompt pro executor (copiar/colar numa nova sessão)

> Rode um cleanup agressivo no repo ai-trade seguindo
> `docs/CLEANUP.md`. Baseline atual: quantos tests? Quantos arquivos em
> cada pasta-alvo? Crie tag `pre-cleanup-YYYY-MM-DD` antes de qualquer
> delete. Commits isolados por área. HANDS-OFF: liste pastas que estão
> ativas antes de começar (verifique com user se tem sessão paralela
> rodando em studies/, app/, ou outra área). Preserve integralmente
> Plano C (portfolio-aposentadoria) + core engine (backtest/
> engine/grid/data/validation/metrics/portfolio/costs). No fim, gere
> `docs/CLEANUP_YYYY-MM-DD_LOG.md` com audit trail completo.

---

## Princípios (em ordem de prioridade)

1. **Nada que é Plano C pode sumir.** `portfolio-aposentadoria.md`,
   `reports/portfolio_aposentadoria_v2/`, `docs/investment-mandate.md`,
   qualquer doc de rationale factor-tilted — PRESERVE integral.

2. **Core engine (src/ai_trade/backtest/) é intocável.** Módulos:
   `engine/`, `grid/` (core runners: runner, observers, result, report,
   walk_forward, gates, diagnostic), `data/`, `validation/`, `metrics/`
   (core: performance, rebalance_modes, report, stress_periods,
   vol_target, standard_report, _fmt), `portfolio/`, `costs/`,
   `indicators/`, `signals/`, `helpers/`, `sweeps/`, `screener/`,
   `meta/`, `bootstrap/`, `stress/`, `strategies/base.py`.

3. **HANDS-OFF sempre confirmar com user.** Pastas que podem estar
   sendo editadas por sessão paralela: `studies/`, `app/`, ou outras.
   Perguntar explicitamente. Se untracked files `??` existirem em
   src/tests/jornada/docs, checar com user antes de assumir DORMANT.

4. **Git tag antes de tudo.** Tag `pre-cleanup-YYYY-MM-DD` aponta pro
   HEAD atual. Tudo recuperável via
   `git checkout pre-cleanup-YYYY-MM-DD -- <path>`.

5. **Commits isolados por área.** Um commit por pasta-alvo. Permite
   `git revert <sha>` cirúrgico se algo quebrar em produção futura.

6. **Consolidar + delete em vez de archive.** User prefere "agressivo":
   criar 1-2 docs de overview + git rm originais. Git history preserva
   tudo. Archive dentro do repo só pra `_archive/` quando o conteúdo
   precisa ser navegável sem git (ex: `specs/_archive/` pra specs que
   podem ser reativadas).

7. **Validar baseline de tests antes e depois.** Baseline pre = X tests
   coletados. Baseline post deve ser X − (tests DORMANT deletados), com
   **zero failures**. Usar `.venv/bin/pytest --collect-only -q` pra
   coleta rápida.

---

## Workflow padrão (10 etapas)

### Etapa 0 — Baseline + tag (OBRIGATÓRIO)

```bash
cd /var/www/pessoal/ai-trade
git status                                  # working tree limpo? (ou confirmar)
git log --oneline -5                        # último commit conhecido
git tag pre-cleanup-YYYY-MM-DD              # snapshot recovery
.venv/bin/pytest --collect-only -q | tail -2  # baseline tests
du -sh . --exclude=.venv --exclude=.git     # tamanho total
ls -ld <target-dirs>                        # snapshot estrutural
```

Gravar numbers pra depois comparar no CLEANUP_LOG.md.

### Etapa 1 — Pastas standalone removíveis

Se existem pastas standalone que foram substituídas (ex: `ops/` → `app/`):
- Grep confirma zero imports em src/, tests/, scripts/, app/, studies/
- `git rm -r <pasta>/`
- Commit isolado

### Etapa 2 — Root litter

Arquivos temp + screenshots + drafts soltos no root:
- `temp.txt`, `prints/*.png`, `*.draft.md`, arquivos .backup
- `git rm` (ou `rm -rf` se untracked)
- Commit isolado

### Etapa 3 — reports/ (maior economia geralmente)

**Estratégia**: preservar `portfolio_aposentadoria_v2/` + forensic
importantes (ex: phase3_5a_v2 lookahead fix) + infra compartilhada
(ex: phase_3_5c/cross_lib/ se tests/cross_lib/ importa).

**Workflow**:
1. Listar subpastas com `du -sh reports/*/` e classificar.
2. Copiar arquivos-chave (BREADTH_NO_WINNER.md, VERDICT.md,
   ESCALATION_PENDING.md, FORENSIC.md) pra `reports/_archive/`.
3. Criar `reports/_dormant_summary.md` com tabela overview +
   killer gates observados + recovery cheatsheet.
4. `git rm -rq reports/<dormant_subpasta>`.
5. `rm -rf reports/<dir>/__pycache__` pros untracked sobrados.
6. Validar que tests/cross_lib ainda coleta: `.venv/bin/pytest
   tests/cross_lib/ --collect-only -q`.
7. Commit.

### Etapa 4 — jornada/ (maior redução narrativa)

**Estratégia**: preservar Plano C entries + arquiteturais + sessão
studies ativa + architectural decisions (bug forensic, mandate
updates, data pipeline pivots).

**CONSOLIDATE em `jornada/_archive/DORMANT_HUNTS.md`**: todas as
entradas de hunts que foram BREADTH_NO_WINNER. Uma tabela por phase
(Phase 3.5/3.6/3.7/3.8/D-MVP/E-MVP) com colunas: arquivo removido,
família/hipótese, verdict em 1 linha.

**REWRITE `jornada/README.md`**: rewrite completo pra ~200 linhas:
- Header "O que é isso?"
- "Onde estamos hoje" — estado atual (maintenance/hunting/done)
- Pointer pra DORMANT_HUNTS.md
- Glossário mínimo (preservar integral do original)
- Entradas (mais recente primeiro) — só as PRESERVADAS

**Cuidado com sessão paralela**: se jornada/README.md tem `M` status,
verificar `git diff` pra saber que mudança é da sessão paralela. Não
apagar essa edição no rewrite.

### Etapa 5 — scripts/ (cleanup seletivo)

Grep antes de deletar qualquer script:
```bash
grep -rn "<nome_script>\|from scripts\.<nome>\|import scripts" src/ tests/ app/ studies/
```

**PRESERVE**: data pipeline (tiingo_*, data_sprint/), knowledge base
(build_*, extract_*, validate_*, check_citations), self-improvement
(self_improve_loop, smoke_fanout, aggregate_judges).

**DELETE**: runners de phases DORMANT (`run_phase3_*`, `run_plano_a_*`,
`iter_v2_*`, strategy-specific runners cuja strategy foi deletada).

Commit isolado.

### Etapa 6 — specs/ (archive leve)

Move specs DORMANT pra `specs/_archive/` (não delete — specs podem
ser reativados em futuro hunt). Preserve só specs vivos em `specs/`
root.

Comando: `git mv specs/<spec>.md specs/_archive/`.

### Etapa 7 — docs/ (consolidação de prompts)

Hunt prompts (`docs/plans/`), research sprints (`docs/research/`),
strategy specs DORMANT (`docs/strategies/`):
- Criar `docs/_archive/DORMANT_STRATEGIES_SPEC.md` com tabela
  overview (linhas por arquivo + recovery commands).
- `git rm -rq docs/{strategies,plans,research}`.

Mandate overrides (`docs/mandate_overrides/`):
- Move pra `docs/_archive/` se estratégia foi declarada DORMANT.
- Preserve em `docs/mandate_overrides/` se ainda "load-bearing" (ex:
  consolidation-final.md signed).

### Etapa 8+9 — src/ai_trade/ + tests/ (acoplado — fazer juntos)

**Mandatório rodar em sequência** porque imports quebrados em
strategies fazem collection de tests falhar.

**Workflow**:

1. Listar strategies DORMANT:
   ```bash
   ls src/ai_trade/backtest/strategies/*.py | grep -E "phase3_|plano_a|bollinger|donchian|etf_rotation|kalman|ranking_br|regime|session|tsmom"
   ```

2. Grep cascata pra verificar imports em `app/` e `studies/` **antes
   de deletar**:
   ```bash
   for mod in <list>; do
     grep -rn "strategies\.$mod\b" src/ tests/ scripts/ app/ studies/ | head -3
   done
   ```
   **Se match em `app/` ou `studies/`: NÃO deletar**. Sessão paralela
   depende.

3. Delete strategies + infra correlata (grid/, metrics/ que só os
   dormant usam):
   ```bash
   git rm -q src/ai_trade/backtest/strategies/<dormant>.py ...
   git rm -q src/ai_trade/backtest/grid/<dormant_infra>.py ...
   git rm -q src/ai_trade/backtest/metrics/<dormant_infra>.py ...
   ```

4. Atualizar `src/ai_trade/backtest/strategies/__init__.py` — remover
   imports stale (senão pytest quebra em collection).

5. Delete tests correspondentes:
   ```bash
   git rm -q tests/test_<dormant>.py ...
   rm -rf src/ai_trade/backtest/{strategies,grid,metrics}/__pycache__
   ```

6. **Ciclo de validação iterativo** (crítico):
   ```bash
   .venv/bin/pytest --collect-only -q 2>&1 | tail -5
   ```
   Se houver erros de import, há 2 opções por erro:
   - (a) O test importa dormant que foi deletada → deletar o test.
   - (b) O módulo que quebrou é dependência de sessão studies/app →
     **RESTAURAR** o módulo via
     `git checkout pre-cleanup-YYYY-MM-DD -- <path>` e documentar
     no LOG.
   Repetir até zero erros.

7. Run full pytest:
   ```bash
   .venv/bin/pytest --tb=no -q 2>&1 | tail -5
   ```
   Deve mostrar `N passed, M skipped, 0 failed`.

8. Commit isolado (ou commit combinado "src + tests" se acoplou).

### Etapa 10 — CLEANUP_YYYY-MM-DD_LOG.md (audit trail)

Criar em `docs/CLEANUP_YYYY-MM-DD_LOG.md`:

- **Baseline** (pre): tests count, repo size, files per area.
- **Final state** (post): tests count, repo size, files per area.
- **Commits por etapa**: tabela # / SHA / subject.
- **Por etapa**: lista detalhada de PRESERVED / REMOVED / ARCHIVED /
  CONSOLIDATED / RESTORED.
- **Verification**: studies/ untouched? app/ untouched? tests 0 failed?
  Plano C integral?
- **Resumo numérico**: tabela Antes / Depois / % redução por área.
- **Recovery cheatsheet**: git checkout + git show + git reset (com
  warning de destrutivo).
- **Sign-off**: executor + user checkbox.

Commit final:
```bash
git commit -m "chore(cleanup): add CLEANUP_YYYY-MM-DD_LOG.md audit trail"
```

---

## Safety rails invioláveis

1. **Nunca usar `git reset --hard`, `git push --force`, ou
   `git clean -fdx`** sem pedido explícito.
2. **Nunca deletar pasta HANDS-OFF**: `studies/`, `app/`, qualquer
   área que o user confirmou estar em uso ativo.
3. **Sempre rodar `.venv/bin/pytest --collect-only` ANTES de commit
   final de cada etapa 8+**. Se tem erro de import, corrigir
   ANTES de commitar.
4. **Se restaurar algo via `git checkout pre-cleanup-*`, documentar
   no LOG** — é info crítica pra debug futuro ("por que esse
   módulo dormant ainda está aqui?" → "porque studies/ importa").
5. **Não mergear `.gitignore` modificado** pelo cleanup se a mudança
   veio de sessão paralela. Deixar pra essa sessão commitar junto
   com os arquivos dela.
6. **Nunca tocar em `books/`, `data/`, `knowledge/`, `logs/`** —
   são artefatos de dados, não de cleanup.

---

## Checklist pré-cleanup

Antes de começar:

- [ ] User confirmou quais pastas são HANDS-OFF (perguntar
      explicitamente — memory tem record de studies/ + app/ por padrão,
      mas sessão nova pode ter outras).
- [ ] `git status` mostra apenas mudanças esperadas (ou são da sessão
      paralela e ficam intocadas).
- [ ] Tag `pre-cleanup-YYYY-MM-DD` criada.
- [ ] Baseline de tests gravado.
- [ ] Plan file criado em `/home/victor/.claude/plans/` com escopo
      aprovado.

## Checklist pós-cleanup

- [ ] 9-10 commits isolados, cada um `chore(cleanup): <área> — ...`.
- [ ] `git diff pre-cleanup-YYYY-MM-DD -- <HANDS-OFF dirs>` retorna vazio.
- [ ] `.venv/bin/pytest --tb=no -q` mostra 0 failed.
- [ ] `portfolio-aposentadoria.md` + `reports/portfolio_aposentadoria_v2/`
      intactos (`git diff pre-cleanup-YYYY-MM-DD -- <paths>` vazio).
- [ ] `docs/CLEANUP_YYYY-MM-DD_LOG.md` criado e commitado.
- [ ] Tag recuperável (`git tag | grep pre-cleanup-YYYY-MM-DD`).

---

## Padrões aprendidos (do run 2026-04-24)

### Padrão 1: Dependências cascata

Strategies marcadas DORMANT geralmente têm infra correlata
(`grid/<name>_config.py`, `grid/<name>_grid.py`, `metrics/<name>.py`)
que é compartilhada com estudos educacionais ativos. Sempre grepar
`studies/` e `app/` antes de deletar strategy + sua infra. Exemplo
real: `bollinger_mr_config.py` e `letf_rotation_b1c.py` tinham que
ser RESTAURADAS porque `studies/ema_sma_threshold_grid.py` as
importava.

### Padrão 2: tests/ têm mais tests que arquivos

Baseline 1168 tests em 83 arquivos ≠ 1168÷83 tests/arquivo. Tests
parametrizados (ex: test_letf_rotation_grid.py) contêm dezenas de
casos. Deletar 1 arquivo pode cortar 50+ tests. Esperar redução
maior que count-of-files indicaria.

### Padrão 3: Git rm + untracked stragglers

`git rm -r <pasta>/` remove do index mas deixa `__pycache__/` e
arquivos untracked no disk. Sempre fazer `rm -rf` pós-git-rm pra
limpar a pasta completamente.

### Padrão 4: Sessão paralela modifica .gitignore + README

Sessões paralelas (ex: studies/, app/) geralmente tocam em
`.gitignore` (pra ignorar sub-repo) e `jornada/README.md` (pra
adicionar entrada da sessão). Essas mudanças chegam como `M` status
antes do cleanup. Não misturar com commits do cleanup — deixar
pendente pra sessão paralela commitar.

### Padrão 5: Consolidação agressiva > archive

User prefere 1 MD overview + git history do que 15 arquivos em
`_archive/`. Git é authoritative pro histórico — arquivos archive
são só conveniência de navegação sem checkout. Regra: só archivar
quando o conteúdo vai ser navegado regularmente (specs que podem
reativar; mandate overrides). Outros: consolidar + delete.

---

## Anti-patterns (evitar)

- ❌ **"Limpar tudo que for DORMANT"** sem mapear dependências →
  quebra sessão paralela.
- ❌ **Commit único com tudo** → impossível revert cirúrgico.
- ❌ **`git rm` sem grep prévio** → dead code invisível não é o mesmo
  que código realmente não usado.
- ❌ **Rewrite de README sem ler diff pendente** → apaga trabalho
  de sessão paralela.
- ❌ **Delete de forensic records** (`phase3_5a_v2/`, engine bug
  reports) → perde contexto crítico se regressão futura suspeitar
  de lookahead.
- ❌ **Skipar Etapa 0 baseline** → não dá pra validar "0 regressão"
  no fim.
- ❌ **`uv run pytest` sem confirmar uv no PATH** → fallback é
  `.venv/bin/pytest`.

---

## Referências

- Log forense do run 2026-04-24: `docs/CLEANUP_2026-04-24_LOG.md`
- Plan file do run 2026-04-24: `/home/victor/.claude/plans/sharded-wondering-spindle.md`
- Mandate (não-cleanup rules permanentes): `docs/investment-mandate.md`
- Memory rules: `/home/victor/.claude/projects/-var-www-pessoal-ai-trade/memory/`
