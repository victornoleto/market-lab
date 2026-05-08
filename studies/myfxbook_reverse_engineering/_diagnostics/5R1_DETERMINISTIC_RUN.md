# 5R-1 Deterministic Run — replicator/comparator/score

Data: 2026-05-03

Escopo aprovado pelo usuario: **5R-1 deterministico somente** (`replicator/comparator/score`).
Os pause gates de R1 permanecem bloqueantes para qualquer ranking final, decisao de estrategia,
Wave C/D, 6R, Stage 3 ou paper trading.

Este arquivo nao e ranking final. E apenas um resumo auditavel da execucao mecanica.

Citação metodologica: o score mede fidelidade de uma regra congelada contra trades reais, nao edge economico; qualquer inferencia de estrategia exigiria validacao anti-overfit posterior `[advances_fin_ml, p.196-211]`.

## Guardrails

| Guardrail | Estado |
|---|---|
| Ranking final permitido | `false` |
| Decisao estrategica permitida | `false` |
| Capital | 100% Plano C |
| Plano A | DORMANT |
| Outputs permitidos | `systems/<id>/decoding/*` + `_diagnostics/batch_summary.json` |
| Outputs proibidos nesta fase | `ranking/DECODING_FIDELITY_RANKING.md`, 6R, Stage 3, paper trading |

Pause gates preservados:

| Gate | Estado |
|---|---|
| `NEWS_RELEASE_MOMENTUM` n=1 | Bloqueante para ranking final |
| `needs_m1_review` 13/30 | Bloqueante para ranking final |

## Comandos

Smoke inicial:

```bash
uv run python -m studies.myfxbook_reverse_engineering.scripts.run_replicator_batch --only 10224499 --force --timeout-per-system 120
```

Teste de escopo R1:

```bash
uv run python -m studies.myfxbook_reverse_engineering.scripts.run_replicator_batch --r1-pool --limit 2 --force --timeout-per-system 120
```

Batch deterministico 30 R1 v3:

```bash
uv run python -m studies.myfxbook_reverse_engineering.scripts.run_replicator_batch --r1-pool --force --timeout-per-system 600
```

Validacoes finais:

```bash
uv run python -m py_compile studies/myfxbook_reverse_engineering/scripts/run_replicator_batch.py studies/myfxbook_reverse_engineering/shared/replicator.py
uv run python -m studies.myfxbook_reverse_engineering.scripts.validate_taxonomy --strict
```

## Resultado Do Batch

Fonte parseable: `_diagnostics/batch_summary.json`.

| Metrica | Valor |
|---|---:|
| Scope | `r1_pool_v3_30` |
| Systems processados | 30 |
| Passed | 30 |
| Skipped | 0 |
| Failed | 0 |
| Wallclock | 1284.9 s |
| `fidelity_score >= 0.60` | 0 |
| LOW band | 2 |
| NONE band | 28 |

Distribuicao de bandas:

| Band | Count |
|---|---:|
| LOW | 2 |
| NONE | 28 |

## Diagnostico Nao-Ranking

Lista abaixo e ordenacao diagnostica local para auditoria da rodada. Nao e ranking final e nao autoriza nenhuma proxima fase.

| system_id | family | fidelity_score | band | n_real | n_synthetic | n_matched |
|---|---|---:|---|---:|---:|---:|
| 11171596 | UNCATEGORIZED | 0.4816 | LOW | 1083 | 816 | 427 |
| 11155858 | UNCATEGORIZED | 0.4004 | LOW | 197 | 106 | 10 |
| 10192401 | UNCATEGORIZED | 0.3589 | NONE | 420 | 614 | 3 |
| 2421356 | H1_MOMENTUM_GOLD | 0.3589 | NONE | 1763 | 1773 | 19 |
| 11206045 | UNCATEGORIZED | 0.2992 | NONE | 212 | 87 | 1 |
| 2373850 | UNCATEGORIZED | 0.2967 | NONE | 1691 | 366 | 172 |
| 10224499 | LATE_NY_BREAKOUT | 0.2524 | NONE | 221 | 2358 | 5 |
| 10281851 | H1_MOMENTUM_GOLD | 0.2518 | NONE | 652 | 1651 | 13 |
| 10734338 | UNCATEGORIZED | 0.2385 | NONE | 591 | 1648 | 22 |
| 11628637 | UNCATEGORIZED | 0.2378 | NONE | 232 | 617 | 7 |

## Observacoes

- Nenhum system atingiu `fidelity_score >= 0.60` nesta execucao mecanica.
- O batch nao criou `ranking/DECODING_FIDELITY_RANKING.md`.
- Cada `decoding_score.json` recebeu `phase_guard.final_ranking_allowed=false` e `phase_guard.strategy_decision_allowed=false`.
- `1407880` levou 730.5s apesar de `--timeout-per-system 600`; o timeout baseado em `SIGALRM` nao interrompeu chamadas longas dentro da stack de fetch/IO. A execucao completou e foi registrada; se re-rodar com cold cache, usar timeout externo de processo por system.
- Como ha 0 systems >=0.60, qualquer leitura substantiva seria no maximo um kill-switch candidato, mas esta sessao preserva sua restricao: pause gates bloqueiam decisao final.

### Nota sobre `11171596` (top score 0.4816 LOW)

Adicionado pos-auditoria 2026-05-03: o system com maior fidelity_score do batch e `11171596` (`UNCATEGORIZED`, candidate `PAIR_HEDGED_DAILY_FX_SHORT`). A leitura ingenua poderia sugerir candidato mais proximo de "decodificado". A decomposicao em `systems/11171596/decoding/decoding_score.json` mostra:

- `entry_timing_f1 = 0.4497` (alto vs batch)
- `direction_acc_at_matched = 0.7283`
- `count_ratio_proximity = 1.0` (ratio 0.75)
- **`lift_vs_baseline_pp = -25.67`** → `baseline_lift_normalized = 0`

A regra recuperada perde 25.67pp de combined-hit-rate para o melhor baseline trivial (always-buy / hour-majority / pair-hour-majority). O system trada EURUSD+USDCHF em pares simultaneos com vies Sell — estrutura pair-hedged sobre par anti-correlacionado. F1 alto vem do matching mecanico do hedge, nao de edge informacional. A formula de score frozen `[evidence_based_ta, p.247-260]` puniu corretamente via `baseline_lift_normalized=0`. Conclusao: o top score e artefato estrutural, **confirma** a leitura "nao decodificavel" em vez de contesta-la.

## Validacao

| Check | Resultado |
|---|---|
| `py_compile` batch + replicator | PASS |
| `validate_taxonomy.py --strict` | PASS=30 WARN=0 FAIL=0 |
| `_diagnostics/batch_summary.json` guard contract | PASS |

Conclusao: 5R-1 deterministico foi executado para os 30 R1 v3. Ranking final e decisao de estrategia permanecem bloqueados.
