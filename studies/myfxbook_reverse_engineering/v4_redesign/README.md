# MyFxBook Reverse Engineering — Pipeline v4 Redesign

Estudo task-driven para executar o redesenho aprovado em 2026-05-03 (`jornada/2026-05-03-2107-myfxbook-pipeline-v4-redesign-plan.md`).

## Por que existe

Os 30 systems R1 v3 falharam economicamente. Diagnostico oficial: "decodificacao
operacional nao recuperavel com OHLC publico M5/M1 pelo pipeline atual". A causa
nao e falta de informacao (oracle 7/7 passa) — e falta de **seletividade**. Este
estudo implementa o redesenho em 28 tasks ortogonais (001-028), cada uma
rodando em uma sessao limpa de Claude Code, com continuidade via arquivos.

## Estrutura

```
v4_redesign/
├── README.md         # este arquivo (entry point)
├── SPEC.md           # contrato frozen — copia do plano aprovado
├── PROTOCOL.md       # como cada sessao deve operar (LEIA PRIMEIRO)
├── PROGRESS.md       # estado mutavel — task status table
├── TASKS.md          # lista frozen de 28 tasks com dependencias
├── DEAD_ENDS.md      # mutavel — abordagens descartadas com razao
├── tasks/            # specs detalhados por task (NNN-slug.md)
├── iterations/       # artefatos por task (NNN-slug/PRE_REG.md, RESULTS.json, SUMMARY.md)
├── loop.sh           # orquestrador shell
└── next_prompt.md    # prompt template alimentado a cada sessao limpa
```

## Como rodar

```bash
# uma iteracao (default)
bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh

# 5 iteracoes em sequencia
MAX_ITER=5 bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh

# dry-run: ve o prompt sem rodar
DRY_RUN=1 bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh

# overnight (12 iteracoes, sonnet, timeout 90min cada)
MAX_ITER=12 ITER_TIMEOUT=5400 CLAUDE_MODEL=sonnet bash studies/myfxbook_reverse_engineering/v4_redesign/loop.sh
```

## Guardrails permanentes (toda sessao)

- Capital: 100% Plano C (mandate §1)
- Plano A: DORMANT
- Sem paper/live em qualquer task
- Sem alterar `frozen_rules/`, `docs/investment-mandate.md`
- Sem otimizar threshold apos ver resultado
- Toda decisao tecnica cita livro (`[book.slug, p.X]`)
- Sem commit/push (loop.sh nao faz commit; usuario decide)

## Regras de fim de sessao

Cada sessao DEVE, antes de encerrar:

1. Atualizar `PROGRESS.md` com status da task executada (DONE/FAILED/BLOCKED)
2. Criar `iterations/NNN-slug/RESULTS.json` + `SUMMARY.md`
3. Atualizar `next_prompt.md` apontando para a proxima task (ou STOP se todas DONE)
4. Criar entrada em `jornada/YYYY-MM-DD-HHMM-slug.md` se houver progresso relevante
5. NAO commitar nem fazer push

## Estado atual

Ver `PROGRESS.md` para snapshot. Tasks ordenados em `TASKS.md`.

## Completude do spec (honestidade YAGNI)

- Tasks **001-008 (Fase 1)** tem spec completo em `tasks/NNN-slug.md`,
  prontos para execucao sem detalhamento adicional.
- Tasks **009-028 (Fase 2-3)** tem **stub** em `tasks/STUBS.md` com goal e
  citacao guia, mas nao tem spec executavel. A **sessao que completa a task
  N** detalha o spec da `N+1` antes de encerrar (ou da `N+1` e `N+2` quando ha
  paralelismo). Esta e uma escolha consciente — o universo de Fase 2 depende
  dos sobreviventes da Fase 1, e specs detalhados upfront seriam premature.

Em outras palavras: **este nao e um plano de 12 semanas com 28 specs prontos.
E uma Fase 1 pronta + framework para chain-planning das fases subsequentes.**

## Recomendacao de execucao (apos review GPT-5.5)

- Rodar **task 001 (skeleton) supervisionada** antes de qualquer loop overnight
- Rodar **task 002 (pre-decode-screen) supervisionada** porque envolve PSR/MCPT
  que sao numericamente sensiveis
- Apos 002 verde, considerar `MAX_ITER=3` para tasks 003-005
- `MAX_ITER=12 overnight` apenas apos confiar na qualidade das primeiras 5
  iteracoes
