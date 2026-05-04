# MyFxBook v4 task 007 — contrato de survivors corrigido

Por decisao humana nesta sessao, corrigi o contrato da task 007 antes de seguir
para a proxima fase. A lista de 21 systems com `pre_screen_decision=GO` fica
preservada como evidencia operacional do pre-screen `[evidence_based_ta,
p.325-328]`, mas nao e mais o universo downstream.

O universo que pode entrar em Fase 2 agora e `fase2_eligible_survivors`:
`pre_screen_decision=GO AND adversarial_auc<0.65 AND mandate_24_pass=true`. Esses
thresholds ja estavam no SPEC, entao nao houve otimizacao apos resultado:
adversarial AUC valida identificabilidade real-vs-synthetic `[advances_fin_ml,
ch.5]` e `mandate_24` inclui DSR/hard gates `[advances_fin_ml, p.273-275]`; PBO
continua ausente/opcional nesta Fase 1 `[advances_fin_ml, p.208-222]`.

Resultado corrigido: `n_pre_screen_survivors=21`, mas
`n_fase2_eligible_survivors=0` e `survivors=[]` para o pipeline. A task 007 volta
a `DONE` operacional, e a task 008 deve documentar Fase 1 STOP, nao iniciar Fase
2A automaticamente. Plano C segue 100%, Plano A DORMANT, sem paper/live e sem
`frozen_rules/`.
