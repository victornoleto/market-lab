# TIEBREAK_RESULT — MyFxBook v4 Fase 3b

## Verdict

`DONE` — a regra lexicografica de `TIEBREAK_PLAN.md` foi aplicada aos 4 sistemas `PASS` travados, sem alterar o plano, buscar novos dados, mudar thresholds, iniciar monitor/cron, paper/live, broker integration ou AutoTrade real.

Este resultado e diagnostico. Nao e recomendacao operacional, nao autoriza capital, nao reativa Plano A e nao aceita single-asset winner como tese de deploy.

## Ordem Diagnostica

| rank | system_id | activity_staleness_days | cost_drag_ratio | avg_net_pips_per_trade | n_symbols_with_positive_pnl | top_symbol_pnl_share | positive_month_ratio | recent_dd_ratio | copyability_score |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | `10067081` | 3.610718 | 0.145648 | 5.000975 | 6 | 0.415179 | 1.000000 | 0.446976 | 0.896255 |
| 2 | `8577442` | 6.897743 | 0.034807 | 28.501713 | 5 | 0.421647 | 0.966102 | 0.388926 | 0.958673 |
| 3 | `10062918` | 166.406192 | 0.055332 | 18.843092 | 2 | 0.575223 | 0.900000 | 0.122590 | 0.892554 |
| 4 | `1152318` | 1798.430058 | 0.061327 | 9.142150 | 2 | 0.526551 | 0.897436 | 0.035461 | 0.940662 |

Shortlist diagnostica: `10067081`, `8577442`, `10062918`.

## Como A Regra Foi Aplicada

A chave do plano e lexicografica: primeiro `activity_staleness_days` crescente, depois custo/slippage, folga de pips, diversificacao, concentracao, estabilidade mensal, drawdown recente, score e `system_id`. Nesta aplicacao, o primeiro campo ja separou todos os 4 sistemas, entao nenhum campo posterior mudou a ordem. Os campos posteriores ficam registrados apenas para auditoria.

O foco em atividade e custos evita transformar o `copyability_score` observado em selecao top-N automatica. Esse cuidado e necessario porque escolher entre 21 EAs apos ver 4 `PASS` adiciona risco de multiple-testing/DSR e data-mining `[advances_fin_ml, p.273-275]` `[evidence_based_ta, p.247-260]`.

Custos e slippage continuam caveat central para copia: o primeiro colocado (`10067081`) tem atividade recente e ampla diversificacao, mas tambem baixo `avg_net_pips_per_trade` e maior `cost_drag_ratio`, fragilidade operacional relevante `[systematic_trading, p.182-197]`.

MCPT/PSR continuam apenas evidencias limitadas de plausibilidade historica do track record dos EAs, nao prova de performance futura nem autorizacao de deploy `[evidence_based_ta, p.325-328]` `[advances_fin_ml, p.260-263]`.

## Guardrails

- Capital permanece 100% Plano C; Plano A permanece DORMANT.
- Sem paper/live.
- Sem AutoTrade real.
- Sem monitor/cron.
- Sem broker/API ou dados novos.
- Sem alteracao de `TIEBREAK_PLAN.md`, `FILTER_COPY_PLAN.md`, gates, pesos ou thresholds.
- Sem PnL futuro, oracle ou cherry-pick.
- Shortlist e somente diagnostica.
