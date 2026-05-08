# PRE_REG — 008-fase1-document

## ID e Nome

- Task: `008-fase1-document`
- Nome: Documentar Fase 1
- Inicio pre-registrado UTC: `2026-05-04T10:53:21Z`

## Citacao da Task

- `TASKS.md`: `008-fase1-document` consolida os resultados Fase 1 em `_diagnostics/PIPELINE_V4_FASE1_REPORT.md`, lista `fase2_eligible_survivors` N<=10 e decide GO/STOP para Fase 2.
- `tasks/008-fase1-document.md`: report deve separar `pre_screen_go_systems` audit-only da lista downstream `fase2_eligible_survivors = pre_screen_decision=GO AND adversarial_auc<0.65 AND mandate_24_pass=true`.

## Escopo Minimo

- Gerar `PIPELINE_V4_FASE1_REPORT.md` com 5 secoes exigidas.
- Mostrar os 21 systems `pre_screen_go_systems` como evidencia operacional, ranqueados por `psr_p` ascending.
- Concluir STOP para Fase 2A porque `n_fase2_eligible_survivors=0`.
- Atualizar `PROGRESS.md` com task 008 `DONE` e Decision Gate Fase 1 `STOP`.
- Reescrever `next_prompt.md` pedindo decisao humana para pivot Fase 3b ou encerramento; nao iniciar task 009.
- Criar entrada em `jornada/` e atualizar `jornada/README.md`.

## Inputs Esperados

- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/RESULTS.json`
- `studies/myfxbook_reverse_engineering/_diagnostics/batch_summary_fase1.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/SUMMARY.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/CORRECTION_PRE_REG.md`
- `studies/myfxbook_reverse_engineering/systems/*/decoding_v4_fase1/pre_decode_screen.json`

## Outputs Esperados

- `studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_FASE1_REPORT.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/008-fase1-document/run.log`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/008-fase1-document/RESULTS.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/008-fase1-document/SUMMARY.md`
- `jornada/2026-05-04-1053-myfxbook-v4-fase1-complete.md`
- `jornada/README.md` atualizado
- `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md` atualizado
- `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md` reescrito

## Citacoes Tecnicas

- MCPT no pre-screen: `[evidence_based_ta, p.325-328]`.
- Adversarial real-vs-synthetic AUC: `[advances_fin_ml, ch.5]`.
- DSR hard gate via `mandate_24`: `[advances_fin_ml, p.273-275]`.
- PBO/CSCV ausente/opcional nesta fase porque nao houve mining de multiplos candidatos Fase 2B: `[advances_fin_ml, p.208-222]`.

## Criterio de Aceite

- Report existe e contem as secoes de pre-screen, GO vs eligible, baseline vs Fase 1, decisao e citacoes.
- `RESULTS.json` da task 008 e parseavel e registra `status=DONE`, `n_fase2_eligible_survivors=0`, `decision_gate_fase1=STOP`.
- `PROGRESS.md` marca 008 como `DONE` e Decision Gate Fase 1 como `STOP`.
- `next_prompt.md` contem STOP/decisao humana, nao task 009 automatica.
- Verificacao shell registra existencia do report, jornada e prompt STOP em `run.log`.

## Kill-switches

- Se os contadores de 007 divergirem dos artefatos parseaveis, marcar 008 `FAILED` e pedir correcao da 007.
- Se `n_fase2_eligible_survivors=0`, nao detalhar/iniciar 009-013; documentar STOP e pedir decisao humana.
- Se qualquer path proibido precisar ser alterado, marcar `BLOCKED`.
