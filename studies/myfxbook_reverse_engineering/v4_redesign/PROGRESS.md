# PROGRESS — Pipeline v4 Redesign

Estado mutavel das 28 tasks. **Atualizar ao final de cada sessao.**

Status validos: `PENDING` (nao iniciada), `IN_PROGRESS` (em execucao na sessao
atual), `DONE` (concluida com criterios de aceite), `FAILED` (tentou e falhou —
ver SUMMARY), `BLOCKED` (dependencia externa, intervencao humana).

Snapshot inicial (2026-05-03 21:30 UTC): tudo PENDING.

| ID | Phase | Status | Started | Completed | Depends | Iter dir | Notes |
|---|---|---|---|---|---|---|---|
| 001-skeleton-setup | 1 | DONE | 2026-05-04T01:00Z | 2026-05-04T01:11Z | - | iterations/001-skeleton-setup | 12 shared stubs + 7 test placeholders; 763 pass no regressions |
| 002-pre-decode-screen | 1 | DONE | 2026-05-04T01:30Z | 2026-05-04T02:05Z | 001 | iterations/002-pre-decode-screen | 5 gates implemented; goldens behave as predicted (10281851 GO, 11504701 STOP via K1+conc, 1407880 GO with is_live warning); 768 pass / 16 skipped / 3 pre-existing fails |
| 003-cpcv-pbo | 1 | DONE | 2026-05-04T03:00Z | 2026-05-04T03:35Z | 001 | iterations/003-cpcv-pbo | cscv_pbo corrigido pos-review GPT-5.5 para usar C(S,S/2)=12870 splits (S=16), nao metade; cenarios sinteticos OK (PBO=0.0 edge / 0.447 noise / 1.0 overfit); 8 testes unitarios |
| 004-gates-dsr-hard | 1 | DONE | 2026-05-04T03:50Z | 2026-05-04T04:25Z | 003 | iterations/004-gates-dsr-hard | DSR promovido a hard (<0.05); PBO via cpcv.cscv_pbo entra como hard (<0.50); WF purgado opcional (>=6/8); CAGR/MDD warning-only fields; passes_mandate_24() -> (bool, list[str]); 14 testes; 790 pass / 15 skip / 3 pre-existing fails; legacy callsites preservados |
| 005-adversarial-validator | 1 | DONE | 2026-05-04T05:00Z | 2026-05-04T05:55Z | 001 | iterations/005-adversarial-validator | LightGBM real-vs-synthetic com paired-kfold (linhas com hash igual no mesmo fold para evitar leakage); 5 sanity tests passam (exact-copy AUC=0.500, sub-amostra AUC=0.503, ruido AUC=1.000, hour-shift AUC=1.000, determinismo delta=0.0); lightgbm 4.6.0 adicionado ao extra myfxbook_decoder; baseline 795 pass / 14 skip / 3 pre-existing fails |
| 006-pipeline-wire-fase1 | 1 | DONE | 2026-05-04T03:12Z | 2026-05-04T03:26Z | 002,003,004,005 | iterations/006-pipeline-wire-fase1 | workbench pipeline flags opt-in: pre_screen json, adversarial AUC, mandate_24 verdict; smoke 1407880 OK (AUC=1.0, Demo warning-only); no-flags schema preserved; tests/myfxbook_pipeline 36 pass / 4 skip; full pytest 799 pass / 14 skip / 3 pre-existing macro cache fails |
| 007-fase1-batch-run | 1 | DONE | 2026-05-04T10:20Z | 2026-05-04T10:50Z | 006 | iterations/007-fase1-batch-run | Corrigido apos validacao STOP: 21 pre_screen_go_systems audit-only, 27 PRE_SCREEN_STOP, 7 failed por frozen_rules ausente; 0 fase2_eligible_survivors sob pre_screen GO + adversarial_auc<0.65 + mandate_24_pass; task 008 deve documentar Fase 1 STOP |
| 008-fase1-document | 1 | DONE | 2026-05-04T10:53Z | 2026-05-04T10:53Z | 007 | iterations/008-fase1-document | Fase 1 reportada como STOP: 21 pre_screen_go_systems audit-only, 0 fase2_eligible_survivors sob adversarial_auc<0.65 + mandate_24_pass; nao iniciar 009-013 sem decisao humana |
| 009-fase3b-replan-filter-copy | 3b | DONE | 2026-05-04T12:26Z | 2026-05-04T12:28Z | 008 | iterations/009-fase3b-replan-filter-copy | FILTER_COPY_PLAN.md criado; contrato de copiabilidade e copyability_score pre-registrados para os 21 pre_screen_go_systems audit-only; nenhum scoring/ranking executado; proxima task do pivot ainda precisa governanca explicita |
| 009-news-calendar | 2A | BLOCKED | - | - | 008 | - | Fase 1 STOP: n_fase2_eligible_survivors=0; nao iniciar Fase 2A sem novo contrato humano |
| 010-cross-asset-features | 2A | BLOCKED | - | - | 008 | - | Fase 1 STOP: n_fase2_eligible_survivors=0; nao iniciar Fase 2A sem novo contrato humano |
| 011-tick-volume-features | 2A | BLOCKED | - | - | 008 | - | Fase 1 STOP: n_fase2_eligible_survivors=0; nao iniciar Fase 2A sem novo contrato humano |
| 012-realized-vol-regime | 2A | BLOCKED | - | - | 010 | - | Fase 1 STOP: upstream Fase 2A bloqueada por N=0 eligible |
| 013-decoder-features-wire-2a | 2A | BLOCKED | - | - | 009,010,011,012 | - | Fase 1 STOP: upstream Fase 2A bloqueada por N=0 eligible |
| 014-fase2a-batch-run | 2A | BLOCKED | - | - | 013 | - | Fase 1 STOP: sem universo Fase 2A para batch |
| 015-lightgbm-miner | 2B | PENDING | - | - | 014 | - | - |
| 016-meta-labeler | 2B | PENDING | - | - | 015 | - | - |
| 017-replicator-wire-2b | 2B | PENDING | - | - | 016 | - | - |
| 018-fase2b-batch-run | 2B | PENDING | - | - | 017 | - | - |
| 019-decision-gate-fase2-fase3 | 2B | PENDING | - | - | 018 | - | - |
| 020-transformer-encoder | 3a | PENDING | - | - | 019 | - | - |
| 021-hmm-regime-mixture | 3a | PENDING | - | - | 019 | - | - |
| 022-out-of-domain-transfer | 3a | PENDING | - | - | 020 | - | - |
| 023-cross-lib-validator | 3a | PENDING | - | - | 022 | - | STUB — detalhar on-demand |
| 024-fase3a-document | 3a | PENDING | - | - | 023 | - | - |
| 025-signal-score-consolidated | 3b | PENDING | - | - | 019 | - | - |
| 026-forward-monitor-setup | 3b | PENDING | - | - | 025 | - | STUB — detalhar on-demand |
| 027-fase3b-document | 3b | PENDING | - | - | 026 | - | - |
| 028-pipeline-v4-final-report | final | PENDING | - | - | 024,027 | - | - |
| 029-fase3b-copyability-score | 3b | DONE | 2026-05-04T12:40Z | 2026-05-04T12:48Z | 009-fase3b-replan-filter-copy | iterations/029-fase3b-copyability-score | COPYABILITY_SCOREBOARD gerado com 21 audit-only systems: 4 PASS, 17 STOP; verdict TOO_MANY_PASS_REQUIRES_REPORT_REVIEW; proximo passo deve ser report/STOP, sem monitor/paper/live |
| 030-fase3b-copyability-report | 3b | DONE | 2026-05-04T13:16Z | 2026-05-04T13:16Z | 029-fase3b-copyability-score | iterations/030-fase3b-copyability-report | COPYABILITY_REVIEW.md criado; 4 PASS documentados como STOP para decisao humana; nenhum top-3, monitor, paper/live, AutoTrade real ou threshold change |
| 031-fase3b-tiebreak-pre-reg | 3b | DONE | 2026-05-04T13:31Z | 2026-05-04T13:31Z | 030-fase3b-copyability-report | iterations/031-fase3b-tiebreak-pre-reg | TIEBREAK_PLAN.md criado; regra lexicografica pre-registrada para aplicacao futura nos 4 PASS; nenhum desempate aplicado, top-3 escolhido, monitor, paper/live ou AutoTrade real |
| 032-fase3b-apply-tiebreak | 3b | DONE | 2026-05-04T16:20Z | 2026-05-04T16:20Z | 031-fase3b-tiebreak-pre-reg | iterations/032-fase3b-apply-tiebreak | TIEBREAK_RESULT gerado aplicando exatamente TIEBREAK_PLAN.md; ordem diagnostica 10067081, 8577442, 10062918, 1152318; shortlist diagnostica <=3; sem monitor/paper/live/AutoTrade |

## Decision gate

| Gate | Quando | Veredito | Decidido em |
|---|---|---|---|
| Fase 1 GO/STOP (apos task 008) | sem 2 | STOP | 2026-05-04T10:53Z |
| Fase 2→3 (apos task 019) | sem 6 | - | - |
| Fase 3 final (apos task 028) | sem 12 | - | - |
| Encerramento v4 | apos task 032 + decisao humana | CLOSED_NO_OPERABLE_EDGE | 2026-05-04T13:37-03:00 |

## Counters

- Tasks total: 33
- Tasks DONE: 13
- Tasks FAILED: 0
- Tasks BLOCKED: 6
- Sessoes consumidas: 13
- Sessoes estimadas restantes: 0 (v4 encerrado; pendentes historicas nao elegiveis)

## Encerramento

Decisao humana em 2026-05-04: encerrar o Pipeline v4. Relatorio final em
`../_diagnostics/PIPELINE_V4_CLOSURE.md`.

Conclusao: engenharia reversa direta `FAIL`; pivot filter-and-copy apenas
diagnostico; nenhuma task `PENDING` esta elegivel; sem monitor/cron, paper/live,
broker/API ou AutoTrade real; capital segue 100% Plano C e Plano A segue
DORMANT.
