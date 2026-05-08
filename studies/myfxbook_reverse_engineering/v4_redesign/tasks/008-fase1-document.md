# Task 008 — Documentar Fase 1

**Phase:** 1 | **Effort:** 1 sessao | **Depends on:** 007

## Goal

Consolidar resultados da Fase 1, escrever report definitivo em `_diagnostics/`,
atualizar jornada, e decidir se Fase 2A pode iniciar com base no universo
`fase2_eligible_survivors` N≤10.

## Output principal

`studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_FASE1_REPORT.md`

Conteudo obrigatorio:

### Section 1 — Pre-screen results
Tabela 52-row com `system_id`, `mcpt_p`, `psr_p`, `concentration_top5`,
`is_live`, `decision`, `notes`.

### Section 2 — Pre-screen GO vs Fase2-eligible survivors
Mostrar os 21 `pre_screen_go_systems` como evidencia operacional, ranqueados por
`psr_p` ascending, mas separar a lista downstream `fase2_eligible_survivors`:
`pre_screen_decision=GO AND adversarial_auc<0.65 AND mandate_24_pass=true`.

### Section 3 — Comparacao baseline vs Fase 1
Quantos systems entravam no decode antes (52) vs passam pre-screen agora (N).
Por que cada um foi cortado (top razoes em STOP).

### Section 4 — Decisao Fase 1 → Fase 2
- Se N >= 3: GO. Lista de `fase2_eligible_survivors` entra em tasks 009-013.
- Se 1 ≤ N < 3: GO mas com nota de cuidado (small sample para Fase 2 statistical
  testing). Considerar relaxar pre-screen thresholds em 1 round, com
  pre-registro novo em DEAD_ENDS.md.
- Se N == 0: STOP. Nao detalhar/iniciar 009-013 automaticamente; documentar
  decisao e pedir autorizacao humana para pivot Fase 3b ou encerramento.

### Section 5 — Citacoes
Listar todas as citacoes usadas em pre_decode_screen, cpcv, gates, adversarial.

## Updates obrigatorios

### jornada/
Criar `jornada/YYYY-MM-DD-HHMM-myfxbook-v4-fase1-complete.md` com:
- Verdict (N survivors, decision)
- O que mudou no pipeline (PSR pre-screen, PBO via CSCV, DSR hard sobre synthetic, adversarial AUC)
- Numero de systems eliminados por gate
- Proximo passo (Fase 2A start se N>0; STOP/pedido de decisao se N==0)

Atualizar `jornada/README.md` "Onde estamos hoje" + entries list.

### v4_redesign/PROGRESS.md
- Marcar 008 como DONE
- Marcar Decision Gate Fase 1 GO/STOP

### v4_redesign/tasks/009-013
Detalhar specs somente se `n_fase2_eligible_survivors > 0`. Se N == 0, deixar
009-013 PENDING/BLOCKED conforme decisao do report e explicar que nao ha universo
valido para Fase 2A.

Se houver survivors, detalhar com base na lista N:
- Quais pairs aparecem mais? (define escopo de cross-asset features)
- Quais hours_utc concentram entradas? (define janela news calendar)
- Quais exchanges de news afetam? (USD-only se EURUSD domina, multi se diverso)
- Volume de tick data necessario (estimar storage)

Cada spec atualizado deve ter aceite verificavel.

### v4_redesign/next_prompt.md
Apontar para task 009 (ou pivot 025 se Fase 1 STOP).

## Verificacao

```bash
# Report criado
test -f studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_FASE1_REPORT.md

# Jornada atualizada
ls jornada/ | grep "myfxbook-v4-fase1-complete"

# next_prompt aponta task 009 se N>0, ou STOP/decisao humana se N==0
grep -E "task 009|STOP|decisao" studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md
```

## Aceite

- [ ] `PIPELINE_V4_FASE1_REPORT.md` com 5 secoes preenchidas
- [ ] Jornada entry criado e README atualizado
- [ ] PROGRESS.md atualizado
- [ ] tasks/009-013 specs detalhados
- [ ] next_prompt.md aponta para proxima task elegivel

## Kill-switches

- N == 0 e usuario nao acessivel → STOP em BLOCKED, registra em SUMMARY pedindo
  intervencao
- Bug na geracao do batch_summary_fase1.json (task 007) → voltar para task 007
  como FAILED + redoradar
