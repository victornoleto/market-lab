# FILTER_COPY_PLAN — MyFxBook v4 Fase 3b

## 1. Escopo

Este plano substitui a continuacao automatica de decode-self por uma trilha diagnostica de filter-and-copy. O objetivo e avaliar se algum EA externo parece copiavel sob regras pre-registradas, sem reverse engineering, sem paper trading, sem AutoTrade real e sem qualquer ordem em conta real.

O capital formal permanece 100% Plano C; Plano A segue DORMANT. Qualquer uso futuro de AutoTrade, paper/live, capital, broker ou conta exige nova decisao humana e novo contrato fora desta task.

Fora de escopo nesta fase:

- nao reabrir Fase 2A/decode-self, porque `n_fase2_eligible_survivors=0`;
- nao alterar `frozen_rules/`, `docs/investment-mandate.md`, `data/trades/` ou outputs R1 congelados;
- nao otimizar thresholds depois de ver ranking;
- nao usar PnL futuro, oracle ou cherry-pick;
- nao aceitar winner single-asset como autorizacao de deploy.

## 2. Universo

O universo inicial e exatamente os 21 `pre_screen_go_systems` da Fase 1. Eles passaram K1/MCPT/PSR/concentration no pre-screen, mas sao apenas audit-only: nao sao `fase2_eligible_survivors`, nao autorizam decode-self, paper/live ou AutoTrade real.

IDs travados para a primeira task de scoring futura:

| system_id | status |
|---|---|
| 10062918 | audit-only pre-screen GO |
| 10067081 | audit-only pre-screen GO |
| 10249298 | audit-only pre-screen GO |
| 10281851 | audit-only pre-screen GO |
| 10563761 | audit-only pre-screen GO |
| 10734338 | audit-only pre-screen GO |
| 11155858 | audit-only pre-screen GO |
| 11206045 | audit-only pre-screen GO |
| 11207608 | audit-only pre-screen GO |
| 1152318 | audit-only pre-screen GO |
| 11628637 | audit-only pre-screen GO |
| 1407880 | audit-only pre-screen GO |
| 1612420 | audit-only pre-screen GO |
| 2421356 | audit-only pre-screen GO |
| 6541963 | audit-only pre-screen GO |
| 8577442 | audit-only pre-screen GO |
| 8647517 | audit-only pre-screen GO |
| 9375654 | audit-only pre-screen GO |
| 9830783 | audit-only pre-screen GO |
| 9841939 | audit-only pre-screen GO |
| 9912554 | audit-only pre-screen GO |

MCPT e PSR continuam sendo apenas evidencias de track record do EA: MCPT rejeita que a sequencia seja explicavel por permutacoes aleatorias `[evidence_based_ta, p.325-328]`; PSR e o teste correto para uma unica serie de retornos do vendor `[advances_fin_ml, p.260-263]`.

## 3. Gates De Copiabilidade

A task futura de scoring deve aplicar primeiro gates bloqueantes. Sistemas reprovados nao entram no ranking final; ficam reportados como `copyability_status=STOP`.

Gates bloqueantes pre-registrados:

| Gate | Regra | Racional |
|---|---|---|
| Universo auditado | `system_id` precisa estar nos 21 IDs acima | Evita cherry-pick fora do universo decidido antes do scoring `[evidence_based_ta, p.247-260]`. |
| K1 sanity | manter `pre_screen_decision=GO`; qualquer evidencia nova de martingale/grid agressivo vira STOP | Dependencia de martingale/grid degrada copiabilidade e risco operacional. |
| MCPT | manter `mcpt_p < 0.05` | Track record precisa sobreviver ao pre-screen estatistico `[evidence_based_ta, p.325-328]`. |
| PSR | manter `psr_p < 0.05` | Serie unica de EA usa PSR, nao DSR com `M=1` `[advances_fin_ml, p.260-263]`. |
| Concentration | manter `concentration_top5 < 0.50` | Evita sistema cujo PnL depende de poucos trades. |
| Estabilidade mensal | STOP se menos de 60% dos meses fechados tiverem PnL liquido positivo ou se houver buraco operacional maior que 90 dias sem trade apos inicio do track record | Copia precisa de persistencia temporal, nao um cluster isolado de ganhos; regra travada antes do ranking para reduzir data-mining `[evidence_based_ta, p.247-260]`. |
| Drawdown recente | STOP se drawdown dos ultimos 90 dias exceder 1.25x o max drawdown historico fechado observado no proprio track record | Evita copiar sistema em degradacao recente sem usar PnL futuro. |
| Trade frequency | STOP se mediana mensal de trades fechados for `< 5` ou `> 300` | Frequencia baixa torna a estimativa instavel; frequencia alta aumenta sensibilidade a spread/slippage. Custos curtos importam explicitamente `[systematic_trading, p.182-197]`. |
| Slippage/cost sensitivity | STOP se custo modelado de 2.0 pips por round-trip consumir `>= 50%` do profit factor bruto estimado ou tornar expectancy media por trade `<= 0` | Copia de estrategia curta precisa sobreviver a spread, comissao e slippage `[systematic_trading, p.182-197]`. |
| Real vs Demo | `is_live=false` nao bloqueia, mas aplica label `demo_warning` e penalidade de score | Demo pode ser util para diagnostico, mas nao autoriza deploy. |
| Single-asset | STOP para recomendacao operacional se mais de 80% do PnL vier de um unico simbolo; ainda pode aparecer em diagnostico | Mandato nao aceita single-asset winner como reativacao. |

DSR nao substitui PSR no track record de cada EA. Se a proxima task selecionar top-N entre varios EAs, a propria selecao passa a ser multiple testing e deve receber penalidade ou campo DSR/ranking-selection no report `[advances_fin_ml, p.273-275]`.

## 4. Ranking Inicial

A formula abaixo fica travada antes de qualquer novo ranking. A task 009 nao deve calcular rankings; a task futura deve implementar exatamente esta formula ou falhar limpo.

Para sistemas que passam todos os gates bloqueantes, calcular componentes normalizados em `[0, 1]`:

- `psr_component = clamp01(1 - psr_p / 0.05)`.
- `mcpt_component = clamp01(1 - mcpt_p / 0.05)`.
- `concentration_component = clamp01((0.50 - concentration_top5) / 0.50)`.
- `stability_component = clamp01(positive_month_ratio)`.
- `drawdown_component = clamp01(1 - recent_dd_ratio / 1.25)`, onde `recent_dd_ratio = recent_90d_drawdown / historical_max_drawdown`.
- `frequency_component = 1.0` se mediana mensal esta em `[20, 120]`; `0.5` se esta em `[5, 20)` ou `(120, 300]`; `0.0` fora disso.
- `cost_component = clamp01(1 - cost_drag_ratio / 0.50)`, onde `cost_drag_ratio` mede a fracao da edge bruta consumida pelo custo round-trip de 2.0 pips.
- `live_component = 1.0` para Real; `0.5` para Demo.
- `multi_asset_component = clamp01((n_symbols_with_positive_pnl - 1) / 4)`, capped em 1.0.

Formula pre-registrada:

```text
copyability_score =
  0.18 * psr_component +
  0.12 * mcpt_component +
  0.10 * concentration_component +
  0.15 * stability_component +
  0.12 * drawdown_component +
  0.10 * frequency_component +
  0.15 * cost_component +
  0.08 * live_component +
  0.10 * multi_asset_component
```

Justificativa dos pesos:

- PSR/MCPT recebem 30% combinado porque o track record precisa ter evidencia estatistica minima `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.
- Custos recebem 15% e gate proprio porque copia de estrategias curtas e altamente sensivel a spread/slippage `[systematic_trading, p.182-197]`.
- Estabilidade/drawdown/frequencia recebem 37% combinado porque copiabilidade e robustez operacional, nao apenas retorno historico.
- Live/demo e multi-asset recebem 18% combinado por mandato e risco de generalizacao; Demo e single-asset nao autorizam deploy.
- A selecao top-N deve reportar explicitamente que escolher entre varios sistemas cria multiple testing/data-mining risk `[advances_fin_ml, p.273-275]` `[evidence_based_ta, p.247-260]`.

Outputs da task futura de scoring:

- `copyability_status`: `PASS` ou `STOP`.
- `failed_copyability_gates`: lista parseavel.
- `copyability_score`: numero apenas para `PASS`.
- `ranking_selection_warning`: obrigatorio quando houver top-N.

## 5. Kill-Switches

Encerrar Fase 3b v4 com STOP se:

- todos os 21 sistemas falharem os gates de copiabilidade;
- qualquer metrica essencial exigir credencial, AutoTrade real, API live ou execucao de ordem;
- a avaliacao exigir alterar `frozen_rules/`, `docs/investment-mandate.md` ou dados congelados;
- a implementacao tentar mudar pesos/thresholds apos olhar ranking;
- a shortlist tiver apenas winner single-asset como tese operacional;
- o custo/slippage modelado eliminar a edge de todos os candidatos.

Se 1-3 sistemas passarem, o resultado permitido e apenas uma shortlist diagnostica. Shortlist nao significa paper/live, AutoTrade, alocacao ou reativacao do Plano A.

## 6. Proximas Tasks

O fluxo antigo `025 -> 026 -> 027` dependia do gate 019 de decode-self e nao e mais executavel diretamente apos Fase 1 STOP. A sequencia pequena proposta para o pivot e:

| Nova task proposta | Objetivo | Observacao |
|---|---|---|
| `029-fase3b-copyability-score` | Implementar scoring offline dos 21 IDs usando o contrato acima e gerar `COPYABILITY_SCOREBOARD.json/md` | Numeracao 029 evita colisao com tasks antigas 009-014 bloqueadas; exige update explicito de `PROGRESS.md`/`TASKS.md` ou novo prompt humano. |
| `030-fase3b-copyability-report` | Documentar shortlist diagnostica ou STOP se todos falharem | Sem paper/live. |
| `031-fase3b-forward-watch-plan` | Se houver shortlist, escrever plano de monitoramento read-only/manual, sem AutoTrade real | Nao agenda cron real sem nova decisao. |

Como `PROGRESS.md` agora pode conter tasks antigas com numeracao 009-014 bloqueadas,
as novas tasks do pivot usam numeracao 029+ e dependencias explicitas no ID completo
`009-fase3b-replan-filter-copy` para evitar ambiguidade.
