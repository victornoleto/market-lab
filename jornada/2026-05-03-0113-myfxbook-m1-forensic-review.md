# MyFxBook: teste forense M1 nao recuperou a decodificacao

Rodei o ultimo teste forense pedido para os 13 systems que o R1 tinha marcado como `needs_m1_review`. A ideia era checar se trocar a granularidade publica de M5 para M1 melhoraria a capacidade do pipeline de reproduzir os trades reais.

Resultado: 13/13 processados, 0 falhas, 0 skips. Nenhum system chegou a `fidelity_score >= 0.60`; todos ficaram na banda `NONE`. O melhor M1 foi 0.3589, igual ao melhor M5 dentro desse subconjunto.

Os outputs M5 existentes foram preservados em `systems/<id>/decoding/`. A rodada M1 foi gravada separadamente em `systems/<id>/decoding_m1/`, e o resumo parseavel ficou em `studies/myfxbook_reverse_engineering/_diagnostics/batch_summary_decoding_m1.json`.

Conclusao provisoria: **decodificacao operacional nao recuperavel com OHLC publico M5/M1 pelo pipeline atual**. Isso encerra a hipotese de reverse engineering operacional neste pipeline, mas nao prova nada sobre possivel valor economico das regras como ideias derivadas. Se houver continuidade, precisa ser uma trilha separada de `derived_strategy_backtest`, sem alegar equivalencia ao EA original e com gates anti-overfit completos `[advances_fin_ml, p.208-211]`.

Guardrails seguem iguais: `final_ranking_allowed=false`, `strategy_decision_allowed=false`, sem 6R, sem Stage 3, sem paper trading, capital 100% Plano C e Plano A DORMANT.

Relatorio auditavel: `studies/myfxbook_reverse_engineering/_diagnostics/5R1_M1_FORENSIC_REVIEW.md`.
