# PRE_REG — 009-fase3b-replan-filter-copy

## ID e task

- Task: `009-fase3b-replan-filter-copy`
- Phase: `3b`
- Started UTC: `2026-05-04T12:26:58Z`
- Source em `TASKS.md`: linhas 93-101 definem o pivot apos Fase 1 STOP, usando os 21 `pre_screen_go_systems` como universo audit-only e exigindo contrato antes de qualquer ranking.
- Source em `tasks/009-fase3b-replan-filter-copy.md`: goal, output principal `FILTER_COPY_PLAN.md`, citacoes obrigatorias, verificacao e aceite.

## Escopo minimo

Criar o contrato de Fase 3b/filter-and-copy sem executar scoring, ranking, monitor, paper trading ou AutoTrade real. A task apenas fixa:

- objetivo e fora-de-escopo;
- universo audit-only dos 21 `pre_screen_go_systems`;
- gates de copiabilidade;
- formula pre-registrada de `copyability_score` para uma task futura;
- kill-switches;
- proposta de proximas tasks pequenas.

## Inputs esperados

- `studies/myfxbook_reverse_engineering/_diagnostics/PIPELINE_V4_FASE1_REPORT.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/007-fase1-batch-run/RESULTS.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/008-fase1-document/SUMMARY.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/tasks/009-fase3b-replan-filter-copy.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/TASKS.md`

## Outputs esperados

- `studies/myfxbook_reverse_engineering/v4_redesign/FILTER_COPY_PLAN.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/009-fase3b-replan-filter-copy/PRE_REG.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/009-fase3b-replan-filter-copy/run.log`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/009-fase3b-replan-filter-copy/RESULTS.json`
- `studies/myfxbook_reverse_engineering/v4_redesign/iterations/009-fase3b-replan-filter-copy/SUMMARY.md`
- `studies/myfxbook_reverse_engineering/v4_redesign/PROGRESS.md` atualizado
- `studies/myfxbook_reverse_engineering/v4_redesign/next_prompt.md` reescrito
- nova entrada em `jornada/` e `jornada/README.md` atualizado

## Citacoes tecnicas

- MCPT permanece como evidencia minima de que o track record nao e indistinguivel de permutacao aleatoria `[evidence_based_ta, p.325-328]`.
- PSR e usado no track record de serie unica de EA, sem DSR com `M=1` `[advances_fin_ml, p.260-263]`.
- Se a task futura ranquear sistemas, DSR/multiple testing deve penalizar selecao entre alternativas `[advances_fin_ml, p.273-275]`.
- Copiar estrategias curtas exige penalidade explicita de custos, spread e slippage `[systematic_trading, p.182-197]`.
- Selecao de sistemas e vulneravel a data-mining; pesos e thresholds precisam ficar travados antes de calcular ranking novo `[evidence_based_ta, p.247-260]`.

## Criterio de aceite

- `FILTER_COPY_PLAN.md` existe e contem as 6 secoes obrigatorias da task.
- O plano preserva: 100% Plano C, Plano A DORMANT, sem paper/live, sem AutoTrade real e sem tocar `frozen_rules/`.
- O universo inicial e exatamente os 21 IDs de `pre_screen_go_systems` audit-only.
- `copyability_score` esta pre-registrado antes de qualquer ranking novo.
- `RESULTS.json` e parseavel.
- `next_prompt.md` aponta para STOP ou para uma task de scoring futura; esta sessao nao inicia scoring.

## Kill-switches

- Se avaliar copiabilidade exigir AutoTrade real/API live, marcar `BLOCKED`.
- Se exigir alterar `frozen_rules/` ou `docs/investment-mandate.md`, marcar `BLOCKED`.
- Se for necessario relaxar thresholds da Fase 1 para salvar decode-self, marcar `FAILED`.
- Se a formula precisar ser ajustada apos olhar ranking novo, marcar `FAILED` por data-mining.
