# MyFxBook catalogo geral e PipsHunterFx rejeitado

Em 2026-05-03, expandi a triagem MyFxBook alem do catalogo HappyForex:
o scraper de ranking geral baixou 255 systems reais em
`studies/myfxbook_reverse_engineering/data/catalog/systems_rank/systems_gain_desc.*`.
O filtro operacional inicial separou 13 candidatos com `gain_pct >= 500` e
`drawdown_pct <= 30`; isto e apenas triagem de pesquisa, nao evidencia de edge.

O primeiro candidato testado foi `11986417` (`PipsHunterFx-AI`), escolhido por
alto ganho historico e drawdown reportado baixo. O download completo precisou de
rate limit de 5s por pagina para evitar `403` do MyFxBook, mas terminou com
246/246 paginas, 4.901 linhas e 4.899 trades.

O workbench rejeitou o decode. A melhor regra automatica foi uma arvore simples
em `ret_3_H4` para `XAUUSD`, mas a fidelidade operacional ficou `NONE`:
`fidelity_score=0.1481`, `entry_timing_f1=0.0153`, `count_ratio=0.038` e apenas
39 matches em +-5min contra 4.899 trades reais. A economia tambem ficou
negativa: `efficacy_score=0.0250`, `total_net_pips=-14448.9`, Sharpe diario
`-1.2617`, bootstrap 99.9% low `-7.7488`, profit factor `0.8812` e walk-forward
`2/8`.

Conclusao: `11986417` e mais um caso de sistema visualmente atrativo no ranking
publico, mas nao recuperavel pelo pipeline OHLC publico atual. Sem paper/live,
sem `frozen_rules/`, sem decisao de estrategia. Os proximos candidatos naturais
do catalogo sao `3534905`, `12000793`, `9493882` e outros baixo-DD, sempre sob o
mesmo criterio anti-overfit: timing real, baseline honesto, bootstrap e
walk-forward importam mais que retorno bruto exibido no ranking
`[advances_fin_ml, p.196-211]` `[evidence_based_ta, p.247-260]`.
