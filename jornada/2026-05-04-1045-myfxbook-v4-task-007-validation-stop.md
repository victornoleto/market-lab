# MyFxBook v4 task 007 — validacao STOP corrigiu contrato de survivors

A validacao bloqueante da task 007 apontou que eu tinha substituido o contrato
de survivors por um criterio mais duro depois do resultado. O contrato
pre-registrado dizia que survivors eram os systems com `pre_screen_decision=GO`
`[evidence_based_ta, p.325-328]`; portanto o batch teve 21 survivors, nao zero.

Corrigi `RESULTS.json` para listar os 21 survivors e manter `n_full_gate_survivors=0`
apenas como diagnostico adicional: adversarial AUC ~1.0 indica synthetic ainda
trivialmente distinguivel do real `[advances_fin_ml, ch.5]`, e nenhum synthetic
passou `mandate_24`/DSR `[advances_fin_ml, p.273-275]`. Como o aceite da task 007
exigia `N<=10`, marquei 007 como `FAILED` e reescrevi `next_prompt.md` para nao
iniciar task 008 automaticamente.

Estado correto agora: Fase 1 precisa de decisao humana antes de continuar. Plano C
segue 100%, Plano A DORMANT, sem paper/live e sem `frozen_rules/`.
