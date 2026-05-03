# MyFxBook reverse-engineering — 5R-1 deterministico executado com gates bloqueantes

Com aprovacao condicionada do usuario, rodei 5R-1 apenas como fase mecanica de `replicator/comparator/score` nos 30 systems R1 v3. O batch terminou 30/30 sem falhas e escreveu outputs por system em `systems/<id>/decoding/` mais resumo em `_diagnostics/batch_summary.json`.

Isto nao virou ranking final: os pause gates de R1 continuam bloqueando qualquer decisao de estrategia (`NEWS_RELEASE_MOMENTUM` ainda n=1 e 13/30 systems precisam `needs_m1_review`). O batch tambem gravou `final_ranking_allowed=false` e `strategy_decision_allowed=false` no summary e nos score JSONs.

Resultado mecanico: nenhum system atingiu `fidelity_score >= 0.60`; 2 ficaram em banda LOW e 28 em NONE. Isso e diagnostico, nao autorizacao para Stage 3 nem paper trading. Capital segue 100% Plano C; Plano A permanece DORMANT.
