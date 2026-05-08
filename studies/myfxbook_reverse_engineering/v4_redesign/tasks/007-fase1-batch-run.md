# Task 007 — Fase 1 batch run nos 30+22 systems

**Phase:** 1 | **Effort:** 1-2 sessoes (dependendo do tempo de scrape) | **Depends on:** 006

## Goal

Rodar `run_replicator_batch` com `--enable-pre-screen --enable-adversarial` em
todos os systems disponiveis em `systems/`. Output: tabela de "EAs sobreviventes"
(decision=GO).

## Comando

```bash
# Lista de systems (52 total: 30 R1 v3 + 22 NOT_DECODED)
SYSTEMS=$(ls studies/myfxbook_reverse_engineering/systems/ | grep -E '^[0-9]+$')

# Batch run
uv run python -m studies.myfxbook_reverse_engineering.scripts.run_replicator_batch \
  --only $SYSTEMS \
  --enable-pre-screen --enable-adversarial \
  --output-dir-name decoding_v4_fase1 \
  --summary-name batch_summary_fase1.json \
  --timeout-per-system 300
```

## Output esperado

- `_diagnostics/batch_summary_fase1.json` — JSON parseable
- `systems/<id>/pre_decode_screen.json` (52 arquivos)
- `systems/<id>/decoding_v4_fase1/pipeline_summary.json` (apenas para os que
  passaram pre-screen)

## Tabela a montar

`iterations/007-fase1-batch-run/RESULTS.json`:

```json
{
  "task_id": "007-fase1-batch-run",
  "status": "DONE",
  "n_systems_total": 52,
  "n_pre_screen_pass": <X>,
  "n_pre_screen_stop": <52-X>,
  "stop_reasons": {
    "mcpt_p_high": <N>,
    "psr_p_high": <N>,
    "concentration_high": <N>,
    "demo_account": <N>
  },
  "survivors": ["<id1>", "<id2>", ...],
  "survivor_metrics": {
    "<id>": {
      "mcpt_p": ...,
      "psr_p": ...,
      "concentration_top5": ...,
      "is_live": ...,
      "adversarial_auc": ...
    }
  }
}
```

## Decision rules apos batch

- **n_survivors > 0:** Fase 1 verdict GO; passa para task 008 (documentar)
- **n_survivors == 0:** Fase 1 verdict STOP severo. Marcar task 008 como BLOCKED
  e abrir decision com usuario: ou ajustar thresholds (NAO recomendado, viola
  pre-registro), ou pivotar direto para Fase 3b (filter-and-copy sem Fase 2).

## Verificacao

```bash
# Confirmar todos os outputs existentes
ls studies/myfxbook_reverse_engineering/systems/*/pre_decode_screen.json | wc -l
# esperado: 52

# Confirmar batch summary parseavel
uv run python -c "import json; d=json.load(open('studies/myfxbook_reverse_engineering/_diagnostics/batch_summary_fase1.json')); print(d.keys())"
```

## Aceite

- [ ] 52 `pre_decode_screen.json` criados
- [ ] `batch_summary_fase1.json` parseavel
- [ ] `iterations/007-fase1-batch-run/RESULTS.json` lista survivors
- [ ] N≤10 survivors (esperado 3-7 baseado em diagnostico anterior)

## Kill-switches

- Tempo de scrape excede 4h → abortar, separar batch em lotes menores
- Pre-screen falha em todos os 52 → bug provavel, investigar antes de marcar
  DONE
- Pre-screen passa em 30+ systems → thresholds frouxos demais, revisitar
  task 002 calibragem

## Notas

- Para systems que ja tem `trades.parquet` em cache, `--enable-pre-screen` nao
  precisa scrape novo
- Para os 22 NOT_DECODED, pode ser necessario rodar Stage 1 antes; se for o
  caso, registrar em SUMMARY como caveat e seguir com 30 R1 v3 apenas
