# Cleanup geral pós-Phase 3.5a-V2 — reduzir, consolidar, organizar

> **Como usar:** copie o bloco abaixo integralmente e cole numa nova
> sessão do Claude Code rodando em `/var/www/pessoal/ai-trade`.
> Antes de colar, execute o safety protocol no final deste arquivo.

> **Versão:** v2 (2026-04-18 — atualizada pós V2 winner found; corrige
> premissa de V2 abandonado da versão anterior; adiciona referências a
> `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md`).

---

## Prompt (copiar a partir daqui)

```
Você é o Claude Code trabalhando no projeto ai-trade em
`/var/www/pessoal/ai-trade`. O projeto cresceu muito durante as Phases
0-3.5a-V2 e acumulou ruído (reports de dead-ends V1, scripts
experimentais descontinuados, jornadas flat não-organizadas, logs
antigos). Preciso de um cleanup profundo antes de seguirmos para
Phase 4 (paper trading dual-path).

## Contexto crítico (estado em 2026-04-18/19)

- **Phase 3.5b:** EM PRODUÇÃO. Winner = Portfolio 3-leg EW
  (SSO+QLD+UGL threshold 10pp). Sharpe OOS 2.251, CAGR 25.56%,
  MaxDD -10.86%. Intocável.
- **Phase 3.5a-V1:** REFUTADA 2026-04-18 (42 iters, 143 runs, 0 PASS).
  Framework errado — 1h FX retail, hold ≤5d, universe pequeno.
  Prunável conforme `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md` §C.
- **Phase 3.5a-V2:** ★ ENCERRADA COM WINNER 2026-04-19.
  Winner = `gayed_ema100_L2_off_gld` (Gayed regime rotation CFD
  Pepperstone, leverage 2×, SPY+QQQ risk-on, GLD risk-off).
  Sharpe OOS 2.285, CAGR 79.14%, MaxDD -21.02%, hold 6d,
  13/13 gates V2 pass. **INTOCÁVEL** — é produção Plano A.
- **Phase 4:** spec `specs/phase_4_paper_trading.md` drafted pelo
  T7 autônomo. Dual-path paper trading 4 meses.

## Objetivo

Reduzir drasticamente o número de arquivos e reorganizar a estrutura
para que um assistente carregando o projeto do zero consiga entender
rápido o estado atual e o histórico relevante. Manter apenas o que
tem valor pra produção (V2 + 3.5b), aprendizado documentado, ou
referência histórica significativa.

## Leitura obrigatória ANTES de tocar em nada

1. `reports/phase3_5b/_DO_NOT_CLEANUP.md` — regras Phase 3.5b
2. `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md` — **regras Phase 3.5a-V2 + prune V1** ★★★
3. `reports/phase3_5b/PRODUCTION.md` — runbook Plano B
4. `docs/strategies/plano_a_v2_l2_gayed_cfd.md` — living strategy doc Plano A winner
5. `specs/phase_3_5a_v2.md` — contrato V2 executado
6. `specs/phase_4_paper_trading.md` — próxima fase
7. `jornada/README.md` — retrato atual + glossário
8. `jornada/2026-04-18-1900-phase3.5a-v2-WINNER-humana.md` — narrativa arc V1→V2
9. `ROADMAP.md` — mapa técnico
10. `CLAUDE.md` — convenções do projeto
11. `docs/investment-mandate.md` — regras invioláveis de strategy

## Regras invioláveis (violação = rollback completo)

1. **NÃO TOCAR em nada listado em `reports/phase3_5b/_DO_NOT_CLEANUP.md`:**
   - Tudo sob `reports/phase3_5b/`
   - Scripts listados lá (run_phase3_5b_*, run_plano_b_*,
     run_static_sso_zroz_gld.py, run_a3d_3leg_portfolio.py,
     validate_phase3_winners.py, extract_testfolio_json.py,
     run_plano_b_variants_*.py)
   - `src/ai_trade/backtest/data/testfolio_loader.py`
   - `data/testfolio/` completa
   - Jornadas `phase3.5b-*` (todas)

2. **NÃO TOCAR em nada listado em `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md` §A:** ★★★
   - Todo `reports/phase3_5a_v2/` (223 arquivos — winner V2-L2 e 5 DEAD aggregates)
   - `scripts/iter_v2_l[1-6]_*.py` (6 files, geradores V2)
   - `src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` + test
   - `src/ai_trade/backtest/sweeps/` inteiro + `tests/test_sweep_registry.py`
   - `scripts/smoke_fanout_protocol.py`
   - `docs/self_improvement/fanout_protocol.md`
   - `specs/phase_3_5a_v2.md`, `specs/phase_4_paper_trading.md`, `specs/self_improve_fanout_mode.md`
   - `docs/strategies/plano_a_v2_l2_gayed_cfd.md`
   - Jornadas phase3.5a-v2 (20+ arquivos — paths serão pós-reorganização §A)
   - 7 jornadas V1 summary preservadas (T1-T5 DEAD + T6 meta + T7 summary)
   - `data/universe_plano_a_v2.json`

3. **NÃO TOCAR** em `books/`, `knowledge/`, `docs/investment-mandate.md`,
   `CLAUDE.md`, `ROADMAP.md`, `README.md`

4. **NÃO ALTERAR LÓGICA** em `src/ai_trade/` — só pode deletar módulos
   comprovadamente órfãos (zero imports no resto do código + zero
   testes usando). **Exceção controlada:** `src/ai_trade/backtest/strategies/donchian_breakout.py`
   + `tests/test_donchian_breakout.py` são V1 refuted e PODEM ser deletados
   per `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md §C.3` — drop pytest
   esperado ~13 tests (796 → ~783). Validar que nenhum outro teste
   importa donchian_breakout antes de remover.

5. **PRESERVAR HISTÓRICO GIT** — use `git mv` (não `mv`) ao reorganizar.

6. **NÃO DELETAR** `data/tiingo/`, `data/testfolio/`, `data/external/`,
   `data/universe_plano_a_v2.json` — dados custam baixar/computar.

7. **NÃO BYPASS** pytest hooks nem git signing.

## Ordem de execução (IMPORTANTE — afeta paths)

**§A PRIMEIRO** (reorganização de jornadas muda paths), depois §B-F
consecutivamente. Ao final de §A, re-gravar `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md`
com os novos paths das jornadas V2 e V1 summary (substituir o nome
antigo `jornada/YYYY-MM-DD-HHMM-slug.md` pelo novo `jornada/YYYY-MM-DD/NN-slug.md`).

## Reorganizações obrigatórias

### A. `jornada/` em pastas por dia (FAZER PRIMEIRO)

Estrutura atual: flat, ~100 arquivos na raiz de `jornada/`.
Estrutura desejada:

    jornada/
    ├── README.md                   # index atualizado
    ├── _archive/                   # pode ficar como está
    ├── 2026-03-31/                 # 1 pasta por dia com jornadas daquele dia
    │   └── 01-decisoes-fundacionais.md
    ├── 2026-04-11/
    ├── ...
    ├── 2026-04-18/                 # ~31 arquivos (maior dia)
    └── 2026-04-19/                 # 7 arquivos

Dentro de cada pasta do dia: renomear `{YYYY-MM-DD}-{HHMM}-{slug}.md`
para `{NN}-{slug}.md` (NN = 01, 02, 03 por ordem cronológica HHMM).
Para arquivos sem HHMM (pré-abril-15), usar `01-{slug}.md`.

Ex: `2026-04-18-1400-phase3.5b-V4-promoted-gate-verdict.md` →
`2026-04-18/NN-phase3.5b-V4-promoted-gate-verdict.md`.

**Usar `git mv`** para preservar histórico.

**Após `git mv`:**
1. Atualizar `jornada/README.md` com paths novos (mantém bullets descritivos).
2. Atualizar `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md` com paths novos
   para jornadas V2 + V1 summary.
3. Grep global + atualizar links quebrados em `specs/`, `docs/`,
   `reports/phase3_5a_v2/`, `reports/phase3_5b/`:
   ```
   grep -rln "jornada/2026-" specs/ docs/ reports/phase3_5a_v2/ reports/phase3_5b/
   ```
   Atualizar cada referência pro novo path.

Commit atômico: `chore(cleanup): reorganize jornada/ by day folder`.

### B. `reports/` — consolidar dead-ends

**Phase 3.5b: INTOCÁVEL.** Ver `_DO_NOT_CLEANUP.md` correspondente.

**Phase 3.5a-V2 (WINNER): INTOCÁVEL.** Ver
`reports/phase3_5a_v2/_DO_NOT_CLEANUP.md §A` — todos os 223 arquivos
preservados. NADA em `reports/phase3_5a_v2/` é consolidado ou deletado.

**Phase 3.5a-V1 (REFUTED):** prune conforme
`reports/phase3_5a_v2/_DO_NOT_CLEANUP.md §C.1`:

```bash
rm -rf reports/phase3_5a/     # 76 files, ~700 KB
```

V1 story está preservada nas 7 jornadas summary (T1-T5 DEAD + T6 + T7)
— reports per-ticker são redundantes.

Commit atômico: `chore(cleanup): prune V1 reports (story in jornadas)`.

**Phase 2 e 2.5 (backtest module + Tiingo bulk):** se ainda existirem
artefatos de run intermediários, consolide em um `_HISTORICAL.md`
por phase. Preserve: Clenow stocks_on_the_move final report (foi
calibration), Tiingo manifest.

**Phase 3 (pré-3.5b):** vários leads produziram winners que foram
superados pelo 3.5b. Consolide os não-winners em
`reports/phase3/_SUPERSEDED_BY_3_5B.md` — tabela com lead, strategy,
verdict final, e pointer pro artefato de 3.5b que o sucedeu.

**Regra geral de consolidação:**
- Se uma pasta tem SÓ `summary.json` + 1 png → pode virar 1 linha numa
  tabela de `_*.md` consolidado.
- Se uma pasta tem report.md com insights únicos → preservar.
- Se sinal ambíguo → preservar (conservador sempre).
- **Exclusões absolutas:** `reports/phase3_5b/` e `reports/phase3_5a_v2/`
  — NUNCA consolidar/deletar.

### C. `scripts/` — deletar órfãos

Para cada script em `scripts/`:
1. Se está listado em qualquer `_DO_NOT_CLEANUP.md` → **PRESERVAR**
2. Se é referenciado por jornada recente ou report preservado → **PRESERVAR**
3. Se é um one-shot experimental que gerou artefato já consolidado ou
   descartado → **DELETAR**
4. Se ambíguo → **PRESERVAR**

**Prunáveis confirmados** (conforme `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md §C.2`):
```bash
rm scripts/run_bollinger_mr_t1_multi_asset.py    # T1 V1 (refuted)
rm scripts/run_donchian_t2_multi_asset.py        # T2 V1 (refuted)
rm scripts/run_t2_fanout_ticker.py               # T2 V1 fan-out
rm scripts/run_t3_fanout_pair.py                 # T3 V1 fan-out
rm scripts/run_t4_fanout_ticker.py               # T4 V1 fan-out
rm scripts/run_t5_fanout_ticker.py               # T5 V1 fan-out
```

Meta: reduzir `scripts/` em ~40-60% se possível, mas nunca deletando
ao custo de reprodutibilidade.

### D. `logs/` — limpar antigos

Delete todos os logs > 7 dias (`logs/self_improve/*.log`,
`logs/loop_*.log`, etc.) exceto o `logs/grid.log` unificado se
existir (user-preference em memory).

### E. `specs/` — revisar

- Specs de phases completadas (Phase 2/2.5/3/3.5b) → manter só se
  têm "Conclusion" field ainda referenciado.
- **Spec V1 refuted:** `specs/phase_3_5a_plano_a_investigation.md` →
  deletar (conforme `_DO_NOT_CLEANUP.md §C.4`) OU arquivar em
  `specs/_archive/` com header `# [SUPERSEDED by phase_3_5a_v2.md]`.
- **Specs ativos** (V2 winner, Phase 4) → **PRESERVAR** (intocáveis).

### F. `reports/` subpastas vazias ou quase

Qualquer pasta com <3 arquivos úteis → considere consolidar ou deletar.
**Exceção:** nunca tocar em `reports/phase3_5b/` ou `reports/phase3_5a_v2/`.

## Safety protocol obrigatório

1. **Antes de começar:**

        git status  # deve estar limpo
        git tag pre-cleanup-YYYYMMDD main  # snapshot antes
        git checkout -b cleanup/post-3_5a-v2
        .venv/bin/pytest --tb=no -q  # baseline — anotar N tests
        # Esperado: 796 passed (pós V2 completa)

2. **Durante:** commits atômicos por fase (A, B, C, D, E, F acima).
   Mensagem formato: `chore(cleanup): <phase> — <summary>`.

   Nota: donchian_breakout.py + test removal (§B/§C) faz pytest cair
   ~13 tests → esperado ~783 pós remoção. Documentar no commit.

3. **Ao final:**

        .venv/bin/pytest --tb=no -q
        # Esperado: 783 passed (796 - 13 donchian tests). Zero errors.
        git status  # deve estar limpo
        git log --oneline cleanup/post-3_5a-v2 ^main  # review dos commits

## Validação de integridade pós-cleanup

Rode esses checks ao final e reporte no jornada de cleanup:

    # 1. _DO_NOT_CLEANUP compliance — Phase 3.5b
    for p in $(grep -oE '`[^`]+`' reports/phase3_5b/_DO_NOT_CLEANUP.md \
      | tr -d '`' | grep -E '^(reports|scripts|src|data|jornada)/'); do
      test -e "$p" && echo "✓ $p" || echo "✗ MISSING: $p"
    done

    # 2. _DO_NOT_CLEANUP compliance — Phase 3.5a-V2  ★★★
    for p in $(grep -oE '`[^`]+`' reports/phase3_5a_v2/_DO_NOT_CLEANUP.md \
      | tr -d '`' | grep -E '^(reports|scripts|src|data|jornada|specs|docs|tests)/'); do
      test -e "$p" && echo "✓ $p" || echo "✗ MISSING: $p"
    done

    # 3. V2 winner preservation explicit check
    test -d reports/phase3_5a_v2/v2_l2_gayed_transported_cfd && \
      echo "✓ V2 winner dir preserved" || \
      echo "✗ FATAL: V2 winner dir missing"
    test -f reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/gayed_ema100_L2_off_gld.md && \
      echo "✓ V2 winner config preserved" || \
      echo "✗ FATAL: winner config missing"
    test -f docs/strategies/plano_a_v2_l2_gayed_cfd.md && \
      echo "✓ V2 living strategy doc preserved" || \
      echo "✗ FATAL: living strategy doc missing"

    # 4. Links quebrados em markdown
    grep -rEn '\[.+\]\(.+\.md\)' reports/phase3_5b/ reports/phase3_5a_v2/ docs/ jornada/README.md \
      | grep -v http \
      | # ... check each link exists

    # 5. Imports órfãos em Python
    .venv/bin/python -c "import ai_trade.backtest"  # sanity
    .venv/bin/pytest --tb=no -q  # full

## Entregáveis

1. **Commits atômicos** em branch `cleanup/post-3_5a-v2`
2. **Jornada nova**: `jornada/{HOJE}/{NN}-cleanup-post-v2.md` com:
   - Antes vs depois: contagem de arquivos por pasta
   - Estratégias consolidadas (quais dead-ends foram compactados)
   - Scripts deletados com justificativa
   - Validação pytest (baseline 796 vs final ~783 — documentar 13
     tests de donchian_breakout removidos com V1 strategy)
   - Qualquer decisão ambígua que você tomou + motivo
   - **Explicitamente: confirmação de que V2 winner permanece intacto**
3. **Atualizar `jornada/README.md`** com nova estrutura por pasta-dia
4. **Atualizar `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md`** com paths
   novos pós §A reorganização
5. **Atualizar `ROADMAP.md`** Current Status se mudar algo relevante
6. **NÃO MERGEAR em main** — deixar o PR/branch pronto para eu
   revisar e mergear manualmente

## Decisões que você pode tomar sozinho

- Qual granularidade de consolidação (bullet vs parágrafo)
- Se um script ambíguo fica ou sai
- Nomes dos arquivos de consolidação
- Quantas pastas por dia manter em jornada/
- Order dentro de `_*_SUMMARY.md`
- Se V1 spec (§E) vira `specs/_archive/` ou deleta (ambos válidos)

## Decisões que você NÃO pode tomar sozinho

- **Deletar qualquer coisa sob `reports/phase3_5b/`** — intocável
- **Deletar qualquer coisa sob `reports/phase3_5a_v2/`** — V2 winner
- **Deletar qualquer jornada phase3.5a-v2 ou phase3.5b** — intocáveis
- **Alterar código em `src/ai_trade/`** (exceto donchian_breakout.py
  refuted V1, removível com teste correspondente)
- **Mexer em `books/`, `knowledge/`, `docs/investment-mandate.md`,
  `docs/strategies/`**
- **Force push, rebase --no-verify, amend commits já publicados**

## Meta quantitativa (guidance, não gate)

- `reports/` → reduzir contagem total de arquivos em 50-70%
  (principalmente Phase 3.5a V1 e pastas antigas; V2 + 3.5b intocáveis)
- `scripts/` → reduzir em 30-50% (V1 scripts + experimentais antigos)
- `jornada/` → mesma contagem de arquivos, mas distribuídos em
  pastas por dia (§A)
- `logs/` → ~0 arquivos antigos

## Tom da execução

Trabalhe autonomamente. Se encontrar ambiguidade, default = preservar.
Se encontrar algo que parece bug/regressão real → pare, documente no
jornada, e me avise no final (não fix silenciosamente).

Use Conventional Commits. Cite fontes do projeto (`[book.slug, p.X]`)
quando justificar decisões técnicas no jornada. Respeite o mandate.

**Zona de atenção máxima: V2 winner.** Qualquer ambiguidade envolvendo
`reports/phase3_5a_v2/`, `docs/strategies/plano_a_v2_l2_gayed_cfd.md`,
ou as jornadas phase3.5a-v2 → parar e preservar.

Comece agora pela leitura obrigatória (11 arquivos), depois §A.
```

---

## Safety protocol a rodar MANUALMENTE antes de colar o prompt

```bash
cd /var/www/pessoal/ai-trade

# 1. Confirmar que não há mudanças uncommitted
git status

# 2. Snapshot seguro (tag imutável)
git tag pre-cleanup-$(date +%Y%m%d) main

# 3. Branch dedicada (pode ser criada manualmente OU pelo agente)
git checkout -b cleanup/post-3_5a-v2

# 4. Baseline pytest (anote o número N)
.venv/bin/pytest --tb=no -q | tail -2
# Esperado: "796 passed in 11.XXs" → anote 796

# 5. Agora abra nova sessão Claude Code, cole o prompt acima
```

## Ao final (você revisa, não o agent)

```bash
# Review das mudanças
git log --stat cleanup/post-3_5a-v2 ^main | less

# Confirme que pytest continua próximo do baseline (esperado ~783 pós
# remoção dos 13 testes donchian_breakout V1)
.venv/bin/pytest --tb=no -q | tail -2

# Validação explícita V2 preservation
test -d reports/phase3_5a_v2/v2_l2_gayed_transported_cfd && echo "✓ WINNER OK"
test -f docs/strategies/plano_a_v2_l2_gayed_cfd.md && echo "✓ STRATEGY DOC OK"

# Se gostar:
git checkout main
git merge --no-ff cleanup/post-3_5a-v2 -m "chore: cleanup post-Phase 3.5a-V2"

# Se NÃO gostar (descarte branch):
git checkout main
git branch -D cleanup/post-3_5a-v2

# Rollback catastrófico (ignora inclusive commits em main desde o tag):
git reset --hard pre-cleanup-YYYYMMDD
```

## Camadas de proteção

1. **Tag `pre-cleanup-YYYYMMDD`** — snapshot imutável antes do cleanup;
   rollback sempre possível.
2. **Branch `cleanup/post-3_5a-v2`** — isolamento do trabalho;
   `main` intacto até você mergear manualmente.
3. **DOIS `_DO_NOT_CLEANUP.md`** — Phase 3.5b + Phase 3.5a-V2 ambos
   validados no prompt; viola = rollback obrigatório por instrução
   explícita.
4. **Pytest baseline** — número de testes antes/depois documentado;
   drop de ~13 (donchian_breakout V1 refuted) é esperado e aceitável;
   qualquer drop maior = rollback.
5. **Validação explícita V2 winner** — 3 checks dedicados (dir, config,
   living doc) antes de considerar cleanup completo.
6. **Review humana antes do merge** — você bate o olho em `git log`
   antes de puxar pra main.

---

## Changelog deste arquivo

- **v2 (2026-04-18 noite):** correção crítica pós-V2 winner found:
  - §B Phase 3.5a-V2 reescrita de "consolide em _ABANDONED_SUMMARY.md"
    para "INTOCÁVEL — preservar 223 files"
  - Leitura obrigatória estendida de 6 para 11 arquivos
  - Regras invioláveis ganham item 2 específico a
    `reports/phase3_5a_v2/_DO_NOT_CLEANUP.md`
  - Ordem de execução explicitada (§A antes de §B-F pra evitar path
    staleness pós reorganização de jornada)
  - §B ganha "exclusões absolutas" (V2 + 3.5b)
  - §E linha "Specs de V2 abandonada" removida
  - Validação pós-cleanup ganha §2 e §3 específicos a V2
  - Pytest drop de 13 tests (donchian refuted) documentado como
    esperado — qualquer drop maior dispara rollback
  - Adicionado changelog
- **v1 (2026-04-18 manhã):** versão original, assumia que V2 poderia
  ser abandonada igual V1. Premissa refutada pelo verdict V2 (1 PASS).
