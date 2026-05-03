# Overnight validation — status snapshot

**Lançado:** 2026-05-02 00:28 UTC (PID em `/tmp/overnight_validation.pid`)
**Modelo Stage 2:** Sonnet 4.6 via `claude --dangerously-skip-permissions --model sonnet -p "/decode-system <id>"`
**Estimativa:** ~9-12h (52 systems × ~10-15min/system; cache OHLC compartilhado entre systems acelera depois das primeiras iterações)

## Como acompanhar / despertar

```bash
# Status do processo
ps -p $(cat /tmp/overnight_validation.pid) -o pid,etime,stat

# Tail do log do loop (incluindo stdout do Stage 1 + claude CLI)
tail -f /tmp/overnight_validation.out

# Log unificado do projeto
tail -f logs/myfxbook_reverse_engineering.log

# Aggregate report (atualizado após CADA system)
cat studies/myfxbook_reverse_engineering/ranking/OVERNIGHT_VALIDATION_REPORT.md

# Quantos systems já processados:
ls studies/myfxbook_reverse_engineering/systems/*/validation_report.md | wc -l
```

## Outputs por system

```
systems/<id>/decoder/{features.parquet, candidates.json, fingerprint.md}  ← Stage 1 (Python)
systems/<id>/signal_rule.md                                                ← Stage 2 (Sonnet via claude CLI)
systems/<id>/validation_report.md                                          ← per-system PASS/FAIL + componentes
systems/<id>/reliability_score.json                                        ← machine-readable
```

## Aggregate output

```
ranking/OVERNIGHT_VALIDATION_REPORT.md  — HIGH/MEDIUM/LOW + ranking + "what worked / didn't"
ranking/overnight_results.json          — machine-readable
```

## Reliability proxy (Stage 3-lite — não é o full Stage 3 do plano)

`reliability ∈ [0,1]` combinação de:

| componente | peso | fonte |
|---|---:|---|
| direction_predictability | 0.25 | top candidate match_rate_cv normalizado vs 0.5 |
| family_clarity | 0.20 | confidence do signal_rule.md (LLM) |
| timing_concentration | 0.20 | fração trades em top-3 hours |
| sanity_pass | 0.10 | k1_pass binary |
| age_freshness | 0.10 | dias desde último trade (5y → 0) |
| vendor_quality | 0.10 | Real > Demo + n_trades coverage |
| pair_coverage | 0.05 | fração de trades em pares Dukascopy-supported |

Bandas:
- **HIGH ≥ 0.65** → candidato a paper-trading (após `/decode-system <id>` com Opus + Stage 3 replicator)
- **MEDIUM 0.45-0.65** → investigar, possível false-negative
- **LOW < 0.45** → folclore / unrecoverable / off-criteria

## Próximos passos (quando você acordar)

1. **Cheque** `ranking/OVERNIGHT_VALIDATION_REPORT.md` — ranking final.
2. **Top-3 HIGH systems:** invoque `/decode-system <id>` com **Opus** (mude `.claude/agents/decoder.md` model: opus de volta) pra refinar signal_rule.md com qualidade superior.
3. **Próximo spec:** Stage 3 proper (replicator + gates §2.4 + cost-sensitivity) per plano `/home/victor/.claude/plans/resilient-wandering-clock.md`.
4. **Se loop morreu antes de terminar:** verifique `tail -100 /tmp/overnight_validation.out`. Aggregate é incremental, então parciais já são úteis. Pra retomar: `uv run python -m studies.myfxbook_reverse_engineering.shared.run_overnight_validation` (não usa --force, então pula systems já feitos).

## Custo estimado Sonnet

~$10-15 total para 51 systems × ~$0.20 cada (Stage 2 LLM). Stage 1 e 3-lite são Python puro sem LLM.

## Caveats explícitos

- **Reliability proxy ≠ Stage 3 do plano.** Não tem replicator OHLC, não roda gates §2.4 estatísticos. É um ranking heurístico pra você priorizar manualmente amanhã.
- **Sonnet pode over-classify como UNCATEGORIZED em casos ambíguos** (timing peaks split entre London e NY). Re-rodar top-N com Opus dá nuance.
- **Citações Sonnet talvez menos rigorosas** que Opus — o anti-padrão "citar sem ler" é mais provável. Re-rodar top-N com Opus pra validar literatura.
