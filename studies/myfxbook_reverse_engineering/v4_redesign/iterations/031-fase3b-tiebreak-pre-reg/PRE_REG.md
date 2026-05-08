# PRE_REG — 031-fase3b-tiebreak-pre-reg

## ID

- Task: `031-fase3b-tiebreak-pre-reg`
- Nome: Fase 3b tiebreak pre-reg
- Started UTC: `2026-05-04T13:31:32Z`

## Citacao Da Task

- `TASKS.md`: `031-fase3b-tiebreak-pre-reg`, Phase 3b, depends on `030-fase3b-copyability-report`, goal de pre-registrar regra para reduzir 4 PASS para 1-3 candidatos diagnosticos, sem aplicar a regra nesta sessao.
- `tasks/031-fase3b-tiebreak-pre-reg.md`: exige `TIEBREAK_PLAN.md`, universo travado nos 4 PASS, regra usando apenas campos existentes, justificativa anti data-mining/multiple-testing, kill-switches e proxima task separada.

## Escopo Minimo

Criar `TIEBREAK_PLAN.md` com uma regra deterministica de desempate que podera ser aplicada somente em task futura. Esta sessao nao calcula ranking novo, nao escolhe top-3, nao recomenda EA, nao inicia monitor/cron, nao conecta broker e nao altera `FILTER_COPY_PLAN.md` ou os pesos/thresholds da task 029.

## Inputs Esperados

- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_REVIEW.md`
- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/FILTER_COPY_PLAN.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/030-fase3b-copyability-report/SUMMARY.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/tasks/031-fase3b-tiebreak-pre-reg.md`

## Outputs Esperados

- `studies/myfxbook_reverse_engineering/v4_redesign/TIEBREAK_PLAN.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/031-fase3b-tiebreak-pre-reg/PRE_REG.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/031-fase3b-tiebreak-pre-reg/run.log`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/031-fase3b-tiebreak-pre-reg/RESULTS.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/031-fase3b-tiebreak-pre-reg/SUMMARY.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md` atualizado
- `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md` reescrito para STOP ou aplicacao futura autorizada
- `jornada/README.md` e uma entrada `jornada/YYYY-MM-DD-HHMM-*.md`

## Citacoes De Livro

- Selecionar top-N depois de observar varios sistemas cria risco de multiple testing/DSR; o desempate precisa ser pre-registrado antes da aplicacao `[advances_fin_ml, p.273-275]`.
- Ajustar criterio apos olhar o ranking e uma forma de data-mining em selecao de sistemas `[evidence_based_ta, p.247-260]`.
- O desempate operacional deve priorizar fragilidade a custos, frequencia e slippage porque estrategias curtas podem perder edge na execucao copiada `[systematic_trading, p.182-197]`.
- MCPT e PSR continuam evidencias limitadas de plausibilidade do track record, nao autorizacao operacional `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

## Criterio De Aceite

- `TIEBREAK_PLAN.md` existe e contem as 6 secoes obrigatorias da task 031.
- O plano trava o universo exatamente nos 4 PASS: `8577442`, `1152318`, `10067081`, `10062918`.
- O plano define a regra, mas nao aplica a regra, nao calcula top-3 e nao promove nenhum EA.
- O plano preserva Plano C 100%, Plano A DORMANT, sem paper/live, sem AutoTrade real, sem monitor/cron e sem mudanca de thresholds/pesos da task 029.
- `RESULTS.json` e JSON parseavel.

## Kill-Switches

- Se a regra precisar de dado novo, PnL futuro, broker/API, AutoTrade real ou monitor, marcar `BLOCKED`.
- Se a regra alterar gates, pesos ou thresholds de `FILTER_COPY_PLAN.md`/task 029, marcar `FAILED`.
- Se a sessao aplicar o desempate ou escolher top-3, marcar `FAILED`.
- Se o universo dos PASS no scoreboard/review divergir dos 4 IDs travados, marcar `BLOCKED` para decisao humana.
