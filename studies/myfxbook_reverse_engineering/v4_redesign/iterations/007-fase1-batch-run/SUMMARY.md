# SUMMARY — 007-fase1-batch-run

## Verdict

DONE apos correcao de contrato.

## O que foi feito

- Criei `PRE_REG.md` antes do batch, inicialmente tratando survivors como systems com `pre_screen_decision=GO`; a validacao bloqueante mostrou que isso deixava 21 systems e violava o aceite `N<=10`.
- Apos decisao humana explicita, criei `CORRECTION_PRE_REG.md` separando `pre_screen_go_systems` (evidencia operacional) de `fase2_eligible_survivors` (universo downstream para Fase 2).
- Rodei `run_replicator_batch` com `--enable-pre-screen --enable-adversarial --output-dir-name decoding_v4_fase1 --summary-name batch_summary_fase1.json --timeout-per-system 300` nos system IDs numericos disponiveis.
- O batch processou 55 systems em 351.2s: 21 completaram decode apos pre-screen `GO`, 27 pararam em `PRE_SCREEN_STOP`, 7 falharam porque nao existe `frozen_rules/<id>.md`.
- Gerei `_diagnostics/batch_summary_fase1.json` e consolidei `RESULTS.json` com pre-screen, adversarial e `mandate_24` calculado sobre `synthetic_trades.parquet` quando havia synthetic.
- Validei que `batch_summary_fase1.json` e `RESULTS.json` sao JSON parseaveis e que existem 55 `pre_decode_screen.json` sob `systems/*/decoding_v4_fase1/`.

## Resultado

- `n_pre_screen_pass=21`.
- `n_pre_screen_stop=27`.
- Stop reasons: `k1_sanity_fail=15`, `mcpt_p_high=8`, `psr_p_high=6`, `concentration_high=6`.
- `adversarial_auc_lt_065_count=0`; todos os systems com AUC calculavel ficaram ~1.0, ou seja, real e synthetic continuam trivialmente separaveis.
- `mandate_24_pass_count=0`; os synthetics com gates calculaveis falharam principalmente bootstrap/DSR.
- `n_pre_screen_survivors=21` pelo criterio `pre_screen_decision=GO`.
- `n_fase2_eligible_survivors=0` sob a definicao corrigida para downstream: `pre_screen_decision=GO AND adversarial_auc<0.65 AND mandate_24_pass=true`.
- `survivors=[]` agora e alias de `fase2_eligible_survivors`, para impedir que a Fase 2 receba os 21 systems que so passaram o pre-screen.
- Veredito da task: `DONE` operacional, com Fase 1 STOP para Fase 2 por `N=0` eligible.

## Citacoes usadas

- MCPT no pre-screen: `[evidence_based_ta, p.325-328]`.
- Adversarial real-vs-synthetic AUC: `[advances_fin_ml, ch.5]`.
- DSR hard gate via `mandate_24`: `[advances_fin_ml, p.273-275]`.
- PBO/CSCV continua ausente/opcional nesta fase porque ainda nao ha mining de multiplos candidatos: `[advances_fin_ml, p.208-222]`.

## Caveats / decisoes nao-obvias

- A correcao nao ajusta thresholds apos ver resultado: usa `adversarial_auc<0.65` ja definido no SPEC para identificabilidade `[advances_fin_ml, ch.5]` e `mandate_24_pass=true` para os hard gates/DSR `[advances_fin_ml, p.273-275]`. PBO segue ausente/opcional nesta fase `[advances_fin_ml, p.208-222]`.
- Os 21 `pre_screen_go_systems` devem aparecer no report de auditoria da task 008, mas nao entram automaticamente na Fase 2.
- O runner de batch atual nao grava `mandate_24_*` diretamente no summary; consolidei esses campos em `RESULTS.json` calculando `compute_gates(...).passes_mandate_24()` sobre os synthetics ja gerados, sem rerodar o decode.
- Systems com `n_synthetic=0` tem `adversarial_auc=null` e `mandate_24_pass=null`, nao PASS.
- Os 7 failures por `frozen_rules` ausente nao foram corrigidos porque `frozen_rules/` e read-only pelo protocolo.

## Verificacao

- Batch completo registrado em `run.log`.
- Verificacao parseavel corrigida: `results_status='DONE'`, `n_pre_screen_survivors=21`, `n_fase2_eligible_survivors=0`, `survivors=[]`.
- Nao adicionei testes unitarios e nao rodei baseline geral porque nao alterei modulo de codigo compartilhado; apenas executei batch e gerei artefatos da iteracao.

## Licao para a proxima task

Task 008 deve iniciar como documentacao de Fase 1 STOP: reportar 21 systems que passaram pre-screen, zero eligible para Fase 2, e escrever `PIPELINE_V4_FASE1_REPORT.md` sem detalhar specs 009-013 como se houvesse universo reduzido.
