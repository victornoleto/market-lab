# Cleanup pós-winners completo: repo enxugado, Phase 3 leads registrados

**Tag:** [GOVERNANCE / CLEANUP] · branch `cleanup/post-winners-20260416`

## Resumo executivo

Executei `specs/post-winners-cleanup.md` §3-§10 em uma sessão. O
repositório agora reflete o estado real pós-loop autônomo: **2 winners
production-ready + Investment Mandate + 5 Phase 3 leads registrados**,
sem ruído acumulado. Pytest verde em **345 passed** (de 531 pré-cleanup
após helper-extraction). Branch `self-improve/post-cleanup-20260416`
preservada como rollback.

## O que foi feito

### Task 1 — Merge para main
- 13 commits do loop (iter 19-27 + 3 do mandate) mergeados via `--no-ff`
  pra preservar histórico.
- Push autorizado pelo usuário: `1425f00..e881076` em origin/main.
- Branch nova `cleanup/post-winners-20260416` criada pra o resto do
  trabalho.

### Task 2 — 9 jornadas retratadas arquivadas
- Movidas via `git mv` para `jornada/_archive/`.
- Index novo em `jornada/_archive/2026-04-16-retracted-entries.md` com
  TOC, magnitude do bug Tiingo IEX, e lições preservadas.
- `jornada/README.md` reescrito: "Onde estamos hoje" + "O que vem a
  seguir" refletindo Phase 3; lista enxugada de 31 → 12 entries.
- Glossário cresceu 6 termos: Path A/B, SHORT-HOLD CFD, SWING BROKER,
  LETF rotation, Investment Mandate, CDI BR.

### Task 3 — Strategies descartadas + helper extraction
- `adjusted_slope`, `atr`, `max_gap` migrados de
  `strategies/clenow_momentum.py` → `helpers/momentum.py` (commit
  isolado pré-deletion).
- 6 strategies + 1 sub-package + 1 portfolio sub-package deletados:
  Clenow, Ehlers BP, Ehlers Meta, Kalman pairs, Chan pairs, OU mean-rev,
  Vol-Expansion, F3.D portfolio.
- 18 test files removidos, 13 one-shot scripts removidos, 7 grid configs
  removidos.
- Engine genérico (`grid/runner.py`, `grid/result.py`) migrado: default
  `config_cls` de `ClenowGridConfig` → `BollingerMRGridConfig`.
- 8 test files migrados pra `BollingerMRGridConfig(window=20,
  std_mult=2.0)` canonical.
- Pytest: 531 → 345 passed (-186 tests de strategies descartadas).

### Task 4 — Citation audit + 18 books archived
- Grep agregado pós-cleanup: **16 USED slugs** identificados (vs 12 do
  dry-run pré-Task-3 — mais slugs foram capturados com pattern
  refinado).
- 18 summaries movidos pra `books/summaries/_archive/`.
- `books/CITATION_AUDIT.md` novo: tabela completa USED / ARCHIVED /
  PROTECTED, razão de archive por slug, procedimento de re-promoção.
- `books/MAPPING.md` atualizado: cada arquivado marcado `[archived
  2026-04-16]`.
- `knowledge/SKILL.md` regenerado via `scripts/build_skill.py` (16
  active books); stale copies em `knowledge/books/` removidos.
- Test fixture `test_check_citations.py` migrado de `cybernetic_trading`
  (archived) → `volatility_trading` (USED).

### Task 5 — 5 Phase 3 leads registrados
- ROADMAP §"Post-cleanup evolution (Phase 3 leads)" expandido com
  tabela completa.
- `docs/self_improvement/memory.md` (gitignored, local-only) recebeu
  seção `## Phase 3 leads (registered, NOT yet executed)`.
- **status: done, iteration: 27** preservados — reset apenas no
  momento da execução (em branch separada).
- B1 explicitamente reframed: **"Gayed canonical (SMA 200 / band 0% /
  Cash 100%) priority 1; Reddit (EMA 125, band 5%, Lev 3x, Gold 0%) é
  1 seed entre outros, NÃO gospel a validar. Winner decidido pelos
  gates, não por afinidade."**

### Task 6 — Docs raiz refrescados
- README.md: header, status table, repository structure, "How to run a
  backtest" (exemplos dos 2 winners), "How to run the grid" (Phase 2.5
  result), §"Books" (link pra CITATION_AUDIT.md).
- ROADMAP.md: headline, test counts (520 → 345), Phase 0 (33/33 → 34
  com 16 active + 18 archived), Phase 2 row, §"Books in the knowledge
  base" header.

### Task 7 — Smoke + secret scan + commit
- Pytest final: **345 passed, 0 failed**.
- BollingerMR smoke (--dry-run, 3-month window): grid + walk-forward +
  gates funcionais. Imports OK pós-deletion.
- ETF Rotation smoke (2-year window): Sharpe 0.960 — strategy executa
  end-to-end, sem ImportError.
- Preservation §2 verificado: todos 10 arquivos críticos tracked
  (winners, mandate, portfolio-aposentadoria, docs/reference/*,
  books/summaries/leverage_for_the_long_run.md).
- Secret scan no diff `main..HEAD`: sem matches reais.

## Estado pós-cleanup

```
test count:       520 → 345 (-186 strategy-specific tests)
strategies kept:  bollinger_mr.py + etf_rotation.py + base.py
helpers added:    helpers/momentum.py (adjusted_slope/atr/max_gap)
books active:     16 USED (4 PROTECTED ⊂ USED)
books archived:   18 (raw PDFs + extracted/ preservados)
jornadas top:     12 entries + 1 postmortem + 1 archive index
phase 3 leads:    5 (A1-A3 multi-asset + B1-B2 LETF rotation)
```

## Branches

- `main` — agora com `e881076` (merge do loop) pushed.
- `self-improve/post-cleanup-20260416` — preservada (rollback).
- `cleanup/post-winners-20260416` — onde os 6 commits de cleanup vivem.
  PR pendente.

## Próximo passo (foruma deste cleanup)

1. PR `cleanup/post-winners-20260416` → `main` aberto via `gh`.
2. Após merge: tag `v0.1-phase-2.5-winners`.
3. Phase 3 começa em branch nova (`phase3/letf-and-multi-asset-<date>`)
   com Lead A1 (BollingerMR leverage sweep) ou Lead B1 (LETF rotation
   from scratch).

Investment Mandate (`docs/investment-mandate.md`) é o north star: CAGR
mínimo CDI BR (~13-14%/ano), Strategy A multi-asset alavancada com
sweep 1:1→1:200, Strategy B LETF rotation ancorada em Gayed. Os 2
winners atuais ficam como compartimento intermediário — Strategy A
candidate (BollingerMR) e Strategy B base (ETFRotation, possivelmente
substituída por LETF rotation se B1 superar).
