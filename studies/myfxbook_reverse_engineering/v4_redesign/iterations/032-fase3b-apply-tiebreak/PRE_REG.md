# PRE_REG — 032-fase3b-apply-tiebreak

## Task

- ID: `032-fase3b-apply-tiebreak`
- Phase: 3b
- Depends on: `031-fase3b-tiebreak-pre-reg` (`DONE` em `PROGRESS.md`)
- Fonte: `TASKS.md` linhas da task 032 e `tasks/032-fase3b-apply-tiebreak.md`

## Escopo Minimo

Aplicar exatamente a regra lexicografica ja pre-registrada em `TIEBREAK_PLAN.md` aos 4 sistemas travados (`8577442`, `1152318`, `10067081`, `10062918`). A task gera apenas ordem diagnostica e shortlist de ate 3 sistemas.

Nao vou alterar `TIEBREAK_PLAN.md`, buscar novos dados, consultar broker/API, iniciar monitor/cron, paper/live, AutoTrade real, nem mudar gates, pesos ou thresholds da task 029.

## Inputs Esperados

- `studies/myfxbook_reverse_engineering/v4_redesign/TIEBREAK_PLAN.md`
- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_SCOREBOARD.json`
- `studies/myfxbook_reverse_engineering/_diagnostics/COPYABILITY_REVIEW.md`

## Outputs Esperados

- `studies/myfxbook_reverse_engineering/_diagnostics/TIEBREAK_RESULT.json`
- `studies/myfxbook_reverse_engineering/_diagnostics/TIEBREAK_RESULT.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/032-fase3b-apply-tiebreak/run.log`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/032-fase3b-apply-tiebreak/RESULTS.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/032-fase3b-apply-tiebreak/SUMMARY.md`

## Regra Tecnica

Usar somente os campos ja existentes no scoreboard e calcular a chave lexicografica do plano: atividade mais recente, menor custo/slippage, maior folga em pips, maior diversificacao positiva, menor concentracao, maior estabilidade mensal, menor drawdown recente, maior score e `system_id` deterministico. Custos e slippage entram como desempate operacional porque podem destruir edges curtos em copia `[systematic_trading, p.182-197]`.

A selecao top-N entre varios EAs e um ponto de multiple-testing/data-mining; portanto a regra deve ser mecanica e pre-registrada, sem ajuste apos ver a ordem `[advances_fin_ml, p.273-275]` `[evidence_based_ta, p.247-260]`.

MCPT/PSR sustentam apenas plausibilidade historica limitada dos tracks dos EAs; nao sao autorizacao operacional nem prova de performance futura `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

## Criterio De Aceite

- JSON parseavel com `universe` exatamente igual a `['8577442', '1152318', '10067081', '10062918']`.
- `ordered_systems` contem os 4 IDs ordenados pela chave do plano.
- `diagnostic_shortlist` contem no maximo 3 IDs.
- MD explica a ordem, campos usados e caveats.
- Nenhum monitor/cron/paper/live/AutoTrade/broker integration iniciado.

## Kill-Switches

- Universo diferente dos 4 IDs travados: `BLOCKED`.
- Campo essencial ausente, nulo ou invalido: `BLOCKED`.
- Necessidade de buscar dado novo ou adaptar regra: `BLOCKED`.
- Tentativa de mudar regra/threshold/peso ou operacionalizar shortlist: `FAILED`.
