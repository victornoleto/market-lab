# MyFxBook v4 Fase 1 — STOP codificado no PROGRESS

A validacao bloqueante apos a task 008 encontrou um problema de estado: apesar de
`next_prompt.md` dizer para nao iniciar task 009, `PROGRESS.md` ainda deixava
`009-news-calendar` como `PENDING` com dependencia `008 DONE`. Pelo protocolo do
loop, isso tornava 009 automaticamente elegivel.

Corrigi `PROGRESS.md` marcando as tasks Fase 2A `009-014` como `BLOCKED`, todas
com nota de que a Fase 1 parou por `n_fase2_eligible_survivors=0`. As tasks
posteriores ficam `PENDING`, mas nao sao elegiveis porque dependem da cadeia
bloqueada. O STOP agora esta no estado mutavel, nao apenas no prompt.

Plano C segue 100%, Plano A DORMANT, sem paper/live e sem `frozen_rules/`.
