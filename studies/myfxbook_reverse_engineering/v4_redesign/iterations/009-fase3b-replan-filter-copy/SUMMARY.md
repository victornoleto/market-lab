# SUMMARY — 009-fase3b-replan-filter-copy

## Verdict

DONE. O pivot para Fase 3b/filter-and-copy foi replanejado em contrato explicito antes de qualquer scoring.

## O que foi feito

- Criei `FILTER_COPY_PLAN.md` com escopo, universo audit-only, gates de copiabilidade, formula pre-registrada de `copyability_score`, kill-switches e proximas tasks propostas.
- Mantive os 21 `pre_screen_go_systems` como universo audit-only, sem trata-los como survivors de decode-self ou autorizacao de deploy.
- Nao rodei ranking, scoring, monitor, paper trading ou AutoTrade real.
- Reescrevi `next_prompt.md` para STOP, porque `PROGRESS.md` ainda nao contem uma task de scoring do novo pivot com dependencia em 009.

## Citacoes usadas

- MCPT no track record do EA: `[evidence_based_ta, p.325-328]`.
- PSR para serie unica de EA: `[advances_fin_ml, p.260-263]`.
- DSR/multiple testing quando ranking seleciona sistemas: `[advances_fin_ml, p.273-275]`.
- Custos/slippage em copia de estrategias curtas: `[systematic_trading, p.182-197]`.
- Risco de data-mining em selecao de sistemas: `[evidence_based_ta, p.247-260]`.

## Caveats / decisoes nao-obvias

- O plano define pesos do `copyability_score`, mas a task 009 nao calcula ranking para evitar olhar resultado antes do contrato.
- Real vs Demo continua warning/label, nao hard gate, mas recebe penalidade no score futuro.
- A sequencia antiga `025 -> 026 -> 027` depende de `019`, que ficou inacessivel apos Fase 1 STOP. Por isso o plano propoe uma sequencia pequena nova para scoring/report/monitor diagnostico, mas nao altera `TASKS.md` nesta sessao.
- Se todos falharem os gates de copiabilidade na task futura, o kill-switch e encerrar v4, nao relaxar thresholds.

## Verificacao

- `FILTER_COPY_PLAN.md` criado.
- `RESULTS.json` parseavel.
- Verificacoes shell registradas em `run.log`.
- Sem testes unitarios adicionados, porque a task foi documental e nao alterou modulos compartilhados.

## Licao para a proxima task

A proxima sessao precisa de decisao/governanca para adicionar ou autorizar `010-fase3b-copyability-score`. Essa task deve implementar exatamente os gates e pesos de `FILTER_COPY_PLAN.md`, sem ajustar threshold apos ver ranking.
