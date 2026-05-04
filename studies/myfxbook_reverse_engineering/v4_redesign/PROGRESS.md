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
| 004-gates-dsr-hard | 1 | PENDING | - | - | 003 | - | - |
| 005-adversarial-validator | 1 | PENDING | - | - | 001 | - | - |
| 006-pipeline-wire-fase1 | 1 | PENDING | - | - | 002,003,004,005 | - | - |
| 007-fase1-batch-run | 1 | PENDING | - | - | 006 | - | - |
| 008-fase1-document | 1 | PENDING | - | - | 007 | - | - |
| 009-news-calendar | 2A | PENDING | - | - | 008 | - | - |
| 010-cross-asset-features | 2A | PENDING | - | - | 008 | - | - |
| 011-tick-volume-features | 2A | PENDING | - | - | 008 | - | - |
| 012-realized-vol-regime | 2A | PENDING | - | - | 010 | - | - |
| 013-decoder-features-wire-2a | 2A | PENDING | - | - | 009,010,011,012 | - | - |
| 014-fase2a-batch-run | 2A | PENDING | - | - | 013 | - | - |
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

## Decision gate

| Gate | Quando | Veredito | Decidido em |
|---|---|---|---|
| Fase 1 GO/STOP (apos task 008) | sem 2 | - | - |
| Fase 2→3 (apos task 019) | sem 6 | - | - |
| Fase 3 final (apos task 028) | sem 12 | - | - |

## Counters

- Tasks total: 28
- Tasks DONE: 3
- Tasks FAILED: 0
- Tasks BLOCKED: 0
- Sessoes consumidas: 3
- Sessoes estimadas restantes: ~47 (variavel)
