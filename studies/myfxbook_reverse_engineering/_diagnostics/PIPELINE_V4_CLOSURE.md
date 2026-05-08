# PIPELINE_V4_CLOSURE -- MyFxBook Reverse Engineering v4

## Veredito Final

`CLOSED_NO_OPERABLE_EDGE`.

O estudo MyFxBook Pipeline v4 Redesign esta encerrado. A conclusao pratica e que, com os dados disponiveis e os gates pre-registrados, nao conseguimos fazer engenharia reversa robusta dos EAs do MyFxBook a ponto de gerar uma estrategia propria operavel.

Isso nao prova que engenharia reversa de qualquer EA seja impossivel em abstrato. Prova que, neste protocolo, neste universo e com esta governanca anti-overfit, nao ha base suficiente para continuar tentando transformar MyFxBook em estrategia, monitor operacional, paper/live ou AutoTrade.

Capital permanece 100% Plano C. Plano A permanece DORMANT. Nenhum broker, API, cron, monitor, paper/live ou AutoTrade real esta autorizado.

## O Que Foi Tentado

### Fase 1 -- Tighten The Diagnostic Loop

Tasks `001` a `008` construiram e conectaram a nova camada diagnostica:

- `001-skeleton-setup`: stubs e estrutura de modulos.
- `002-pre-decode-screen`: pre-screen com sanity, MCPT, PSR, concentracao e live/demo warning.
- `003-cpcv-pbo`: CSCV/PBO para medir risco de overfitting na selecao `[advances_fin_ml, p.208-222]`.
- `004-gates-dsr-hard`: DSR e PBO promovidos a hard gates; CAGR/MDD preservados como warning-only conforme mandate.
- `005-adversarial-validator`: classificador real-vs-synthetic para testar se os synthetics pareciam dados reais `[advances_fin_ml, ch.5]`.
- `006-pipeline-wire-fase1`: flags opt-in no pipeline.
- `007-fase1-batch-run`: batch nos sistemas disponiveis.
- `008-fase1-document`: documentacao da Fase 1 e STOP.

Resultado da Fase 1:

- 55 systems avaliados no batch.
- 21 `pre_screen_go_systems` audit-only.
- 27 `PRE_SCREEN_STOP`.
- 7 falhas por `frozen_rules/<id>.md` ausente.
- 0 `fase2_eligible_survivors`.

O ponto decisivo foi que nenhum sistema passou simultaneamente os criterios completos de elegibilidade: `pre_screen_decision=GO`, `adversarial_auc < 0.65` e `mandate_24_pass=true`. Os synthetics continuaram distinguiveis do real, entao o decoder nao estava capturando uma regra verdadeira de forma robusta.

### Fase 2A/2B/3A -- Decode-Self Path

A trilha original de engenharia reversa direta ficou bloqueada:

- `009-news-calendar`
- `010-cross-asset-features`
- `011-tick-volume-features`
- `012-realized-vol-regime`
- `013-decoder-features-wire-2a`
- `014-fase2a-batch-run`

Essas tasks foram marcadas `BLOCKED` porque a Fase 1 terminou com `n_fase2_eligible_survivors=0`. Sem universo elegivel, seguir para features ricas, meta-labeling, mineracao LightGBM, Transformer/HMM ou validacao final seria fabricar trabalho em cima de candidatos que ja falharam os gates.

As tasks `015` a `028` continuam historicamente listadas como `PENDING`, mas nao sao elegiveis: dependem da cadeia bloqueada em `014`/`019` ou de outputs que nunca existiram.

### Pivot Fase 3B -- Filter-And-Copy Diagnostico

Por decisao humana, abrimos um pivot separado, audit-only, sem deploy:

- `009-fase3b-replan-filter-copy`: criou `FILTER_COPY_PLAN.md`, travando universo, gates e score antes de ranking.
- `029-fase3b-copyability-score`: aplicou o scoring offline aos 21 `pre_screen_go_systems`.
- `030-fase3b-copyability-report`: documentou 4 `PASS` e parou por governanca.
- `031-fase3b-tiebreak-pre-reg`: pre-registrou regra lexicografica de desempate.
- `032-fase3b-apply-tiebreak`: aplicou exatamente a regra pre-registrada.

Resultado do pivot:

- 21 systems audit-only avaliados por copiabilidade.
- 4 `PASS`: `8577442`, `1152318`, `10067081`, `10062918`.
- 17 `STOP`.
- O resultado da task 029 foi `TOO_MANY_PASS_REQUIRES_REPORT_REVIEW`, porque 4 PASS excediam a shortlist planejada de 1-3.
- A regra de desempate da task 032 produziu a ordem diagnostica `10067081`, `8577442`, `10062918`, `1152318`.
- A shortlist diagnostica final foi `10067081`, `8577442`, `10062918`.

Essa shortlist nao e recomendacao operacional. Ela nao autoriza capital, paper/live, monitor, broker integration, cron ou AutoTrade real.

## Por Que Nao Virou Operacao

### Engenharia Reversa Direta Falhou

O objetivo original era descobrir regras ou sinais replicaveis por tras de EAs existentes. Esse caminho exigia que os synthetics gerados pelo pipeline fossem suficientemente indistinguiveis do real e que os candidatos passassem gates estatisticos fortes. Isso nao aconteceu.

O classificador adversarial continuou distinguindo real de synthetic, sinal de que a representacao gerada pelo decoder nao capturava a estrutura verdadeira dos trades `[advances_fin_ml, ch.5]`. Alem disso, DSR/PBO e outros gates continuaram bloqueando candidatos sob risco de overfitting e selecao multipla `[advances_fin_ml, p.208-222]` `[advances_fin_ml, p.273-275]`.

### Filter-And-Copy Nao Resolveu O Problema

O pivot Fase 3B respondeu a uma pergunta menor: "ha EAs historicamente plausiveis e talvez copiaveis para observacao diagnostica?". A resposta foi: alguns passaram filtros offline, mas isso ainda nao cria autorizacao operacional.

Selecionar top-N apos observar 21 EAs e 4 PASS adiciona risco de data-mining e multiple testing `[evidence_based_ta, p.247-260]` `[advances_fin_ml, p.273-275]`. MCPT e PSR ajudam a avaliar plausibilidade historica, mas nao provam performance futura nem removem o risco de selecao ex-post `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

Tambem ha risco operacional material: custos, spread, slippage, atraso de execucao, concentracao por simbolo e staleness podem destruir copiabilidade mesmo quando o historico parece bom `[systematic_trading, p.182-197]`.

### Mandate Continua Bloqueando Deploy

O mandate atual esta em maintenance mode: capital consolidado em 100% Plano C, Strategy A/B/D dormant, e qualquer reativacao exigiria evidencia muito mais forte. O v4 nao produziu um winner validado, nem um protocolo de paper/live autorizado.

## Estado Final Das Tasks

- `DONE`: 13 tasks.
- `FAILED`: 0 tasks.
- `BLOCKED`: 6 tasks.
- `PENDING`: 14 tasks historicas, mas nenhuma elegivel.
- `IN_PROGRESS`: 0 tasks.

As 6 `BLOCKED` sao a Fase 2A original (`009-news-calendar` a `014-fase2a-batch-run`), bloqueada por `n_fase2_eligible_survivors=0`.

As 14 `PENDING` pertencem a cadeias downstream que dependem de `014`, `019`, `024` ou `027`. Como a Fase 2A ficou bloqueada e o pivot Fase 3B terminou em diagnostico, elas nao devem ser executadas automaticamente.

## Decisao Humana De Encerramento

Decisao registrada em 2026-05-04: encerrar o MyFxBook Pipeline v4 Redesign.

Conclusao operacional:

- Engenharia reversa direta: `FAIL`.
- Filter-and-copy: `DIAGNOSTIC_ONLY`, nao operacional.
- Shortlist final: diagnostica apenas.
- Monitor/cron: proibido.
- Paper/live: proibido.
- Broker/API/AutoTrade real: proibido.
- Capital: 100% Plano C.
- Plano A: DORMANT.

Qualquer reabertura futura deve ser tratada como novo estudo, com novo contrato, novo escopo, nova decisao humana e sem reutilizar a shortlist diagnostica como autorizacao operacional.
