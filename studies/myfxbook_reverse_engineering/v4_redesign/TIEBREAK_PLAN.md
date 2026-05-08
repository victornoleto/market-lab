# TIEBREAK_PLAN — MyFxBook v4 Fase 3b

## 1. Escopo

Este e um plano de desempate diagnostico, nao deploy. Ele existe porque a task 029 produziu 4 sistemas `PASS`, acima da shortlist diagnostica planejada de 1-3, e a task 030 parou para governanca humana.

Este documento apenas pre-registra uma regra para uma task futura. Esta task 031 nao aplica o desempate, nao escolhe top-3, nao inicia monitor, nao cria cron, nao conecta broker, nao usa AutoTrade real e nao autoriza paper/live.

Capital permanece 100% Plano C; Plano A permanece DORMANT. Qualquer etapa operacional futura exigiria nova decisao humana e novo contrato.

## 2. Universo Travado

O universo de desempate futuro fica travado exatamente nos 4 sistemas que tiveram `copyability_status=PASS` na task 029 e foram documentados na task 030:

| system_id | origem |
|---|---|
| `8577442` | PASS em `COPYABILITY_SCOREBOARD.json` e review 030 |
| `1152318` | PASS em `COPYABILITY_SCOREBOARD.json` e review 030 |
| `10067081` | PASS em `COPYABILITY_SCOREBOARD.json` e review 030 |
| `10062918` | PASS em `COPYABILITY_SCOREBOARD.json` e review 030 |

Nenhum sistema fora desses 4 pode entrar no desempate futuro. Se uma task futura encontrar universo diferente, sistemas PASS adicionais, sistemas PASS ausentes ou campos essenciais ausentes, deve parar como `BLOCKED` em vez de adaptar a regra.

MCPT e PSR continuam sendo evidencias limitadas de plausibilidade historica do track record do EA; nao sao autorizacao operacional nem prova de copiabilidade futura `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

## 3. Regra De Desempate

A task futura de aplicacao deve usar somente campos ja existentes em `COPYABILITY_SCOREBOARD.json` e `COPYABILITY_REVIEW.md`. Nao pode buscar novos trades, consultar broker/API, usar PnL futuro, alterar thresholds da task 029 ou recalibrar pesos apos ver o resultado.

Para cada um dos 4 sistemas travados, calcular a seguinte chave lexicografica, em ordem de prioridade. A ordenacao final sera crescente nos campos marcados como `menor melhor` e decrescente nos campos marcados como `maior melhor`.

| Ordem | Campo derivado | Fonte permitida | Direcao | Racional |
|---:|---|---|---|---|
| 1 | `activity_staleness_days = generated_utc - operational_metrics.last_close` | `COPYABILITY_SCOREBOARD.json` | menor melhor | Evita priorizar track record sem atividade recente; se `last_close` estiver ausente, `BLOCKED`. |
| 2 | `cost_drag_ratio` | `operational_metrics.cost_drag_ratio` | menor melhor | Copia e sensivel a spread/slippage; menor drag operacional e preferivel `[systematic_trading, p.182-197]`. |
| 3 | `avg_net_pips_per_trade` | `operational_metrics.avg_net_pips_per_trade` | maior melhor | Mais pips liquidos por trade deixa mais folga para erro de execucao e slippage `[systematic_trading, p.182-197]`. |
| 4 | `n_symbols_with_positive_pnl` | `operational_metrics.n_symbols_with_positive_pnl` | maior melhor | Reduz dependencia de winner single-asset; ainda nao autoriza deploy. |
| 5 | `top_symbol_pnl_share` | `operational_metrics.top_symbol_pnl_share` | menor melhor | Menor concentracao por simbolo reduz risco de tese estreita. |
| 6 | `positive_month_ratio` | `operational_metrics.positive_month_ratio` | maior melhor | Persistencia mensal e preferida a ganhos concentrados. |
| 7 | `recent_dd_ratio` | `operational_metrics.recent_dd_ratio` | menor melhor | Menor drawdown recente relativo reduz risco de degradacao operacional. |
| 8 | `copyability_score` | `copyability_score` | maior melhor | Usado apenas como ultimo desempate, preservando o score pre-registrado da task 029 sem mudar seus pesos. |
| 9 | `system_id` | `system_id` | crescente | Desempate deterministico final, sem interpretacao financeira. |

A shortlist diagnostica futura sera composta pelos primeiros 3 sistemas apos essa ordenacao, se e somente se uma task futura for explicitamente autorizada a aplicar a regra. Se houver empate exato ate `system_id`, a task futura deve marcar `BLOCKED`, pois isso indicaria ambiguidade no dado de entrada.

Esta regra nao cria novo gate de rejeicao. Ela e apenas uma ordenacao operacional entre sistemas que ja passaram os gates da task 029. Usar `copyability_score` apenas no fim reduz a chance de transformar a primeira ordenacao observada em selecao automatica top-N, risco associado a multiple testing/DSR quando varios candidatos sao comparados `[advances_fin_ml, p.273-275]`.

## 4. Justificativa

Escolher 1-3 sistemas depois de observar 21 candidatos e 4 PASS e uma decisao estatistica adicional. Se a regra for ajustada para favorecer um sistema visto no review, o estudo vira selecao ex-post e data-mining `[evidence_based_ta, p.247-260]`.

Por isso, a regra acima e deterministica, usa somente campos ja existentes, nao altera gates ou pesos de `FILTER_COPY_PLAN.md`, e prioriza criterios operacionais antes do score final. O foco em atividade, custo, pips por trade e diversificacao reflete o risco de que uma estrategia historicamente lucrativa deixe de ser copiavel quando spread, comissao, slippage e atraso de execucao entram no caminho `[systematic_trading, p.182-197]`.

O plano tambem evita tratar MCPT/PSR como evidencia conclusiva: esses testes apoiam a plausibilidade do track record observado, mas nao removem o risco de selecao entre varios sistemas nem substituem validacao futura `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

## 5. Kill-Switches

Uma task futura de aplicacao deve parar como `BLOCKED` ou `FAILED` se ocorrer qualquer caso abaixo:

- O universo nao for exatamente `8577442`, `1152318`, `10067081`, `10062918`.
- Qualquer campo requerido pela chave lexicografica estiver ausente, nulo onde nao permitido, ou tiver tipo invalido.
- A aplicacao exigir dado novo, novos trades, broker/API, AutoTrade, conta paper/live, monitor, cron ou qualquer integracao operacional.
- A aplicacao tentar mudar gates, pesos ou thresholds de `FILTER_COPY_PLAN.md` ou task 029.
- A aplicacao usar PnL futuro, oracle, cherry-pick ou recalibracao apos ver a ordem resultante.
- A aplicacao tratar a shortlist diagnostica como recomendacao operacional, autorizacao de capital, reativacao do Plano A ou aceitacao de single-asset winner.

## 6. Proxima Task

Proxima acao permitida: STOP para decisao humana ou uma nova task separada, por exemplo `032-fase3b-apply-tiebreak`, autorizada explicitamente pelo usuario.

Essa task futura, se autorizada, deve apenas aplicar a regra deste arquivo aos 4 PASS, gravar artefatos parseaveis e continuar sem monitor/cron, sem paper/live, sem AutoTrade real, sem broker integration e sem capital. Ela nao deve ampliar escopo para observacao forward ou deploy.
