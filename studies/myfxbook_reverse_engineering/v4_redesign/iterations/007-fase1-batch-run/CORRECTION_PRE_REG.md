# CORRECTION_PRE_REG — 007-fase1-batch-run survivor contract

## ID e Nome

- Task afetada: `007-fase1-batch-run`
- Correcao: separar `pre_screen_go_systems` de `fase2_eligible_survivors`
- Inicio pre-registrado UTC: `2026-05-04T10:45:00Z`

## Decisao humana

O usuario pediu explicitamente: "Faca a correcao antes de irmos para a proxima
fase." Esta correcao registra a decisao de nao avancar para Fase 2 usando a lista
bruta de 21 systems com `pre_screen_decision=GO`.

## Problema

A validacao bloqueante apontou que `survivors=[]` em `RESULTS.json` substituia o
contrato original da task 007, em que survivors eram `pre_screen_decision=GO`.
Isso criava dois riscos:

- Subcontar os 21 systems que passaram o pre-screen `[evidence_based_ta, p.325-328]`.
- Avancar task 008 como se o criterio `N<=10` tivesse sido satisfeito.

## Correcao pre-registrada

Sem rerodar batch e sem ajustar thresholds apos ver resultado:

- `pre_screen_go_systems`: lista operacional dos 21 systems com `decision=GO`.
- `fase2_eligible_survivors`: lista para entrar em Fase 2, definida como
  `pre_screen_decision=GO AND adversarial_auc<0.65 AND mandate_24_pass=true`.
- `survivors`: alias de `fase2_eligible_survivors` para o restante do pipeline.

Esta definicao usa thresholds ja existentes no SPEC: adversarial AUC < 0.65 para
synthetic indistinguivel do real `[advances_fin_ml, ch.5]` e hard gates
`mandate_24`/DSR `[advances_fin_ml, p.273-275]`. PBO continua ausente/opcional
nesta Fase 1 porque ainda nao ha CPCV sobre candidatos Fase 2B
`[advances_fin_ml, p.208-222]`.

## Criterio de aceite

- `RESULTS.json` parseavel.
- `n_pre_screen_pass == len(pre_screen_go_systems) == 21`.
- `n_fase2_eligible_survivors == len(fase2_eligible_survivors) == len(survivors) == 0`.
- `PROGRESS.md` volta a marcar 007 como `DONE`, mas com nota explicita de STOP
  para Fase 2 por `N=0` eligible.
- `next_prompt.md` aponta task 008 como report de Fase 1 STOP, nao como entrada
  automatica em Fase 2.

## Kill-switch

Se qualquer contador divergir dos artefatos de batch, manter 007 `FAILED` e pedir
nova intervencao humana.
