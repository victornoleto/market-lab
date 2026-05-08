# Day/Swing Strategy Hunt

Novo loop iterativo para buscar, ou rejeitar rapidamente, estrategias simples e auditaveis de day/swing trade em FX, Gold e Crypto.

Estado atual: bootstrap do loop. Nenhuma hipotese foi testada ainda. Capital segue 100% Plano C; Plano A segue DORMANT; nao ha paper/live autorizado.

## Escopo

O estudo comeca em D1/H4 porque custos, slippage e microestrutura tendem a dominar horizontes curtos `[systematic_trading, p.182-197]`.

O objetivo nao e achar um winner a qualquer custo. Saidas validas incluem:

- `positive`: evidencia inicial robusta o suficiente para aprofundar.
- `negative`: falhou gates ou baselines, mas ensinou algo reaproveitavel.
- `inconclusive`: dados/infra insuficientes para verdict honesto.
- `dead-end`: familia ou ideia nao deve ser reaberta sem evidencia nova.

## Arquivos Para Ler No Comeco De Cada Sessao

Leia nesta ordem:

1. `CLAUDE.md`
2. `jornada/README.md`
3. `studies/day_swing_strategy_hunt/MEMORY.md`
4. Ultimo `studies/day_swing_strategy_hunt/iterations/*/SUMMARY.md`, se existir
5. `studies/day_swing_strategy_hunt/next_prompt.md`
6. `studies/day_swing_strategy_hunt/SPEC.md`, apenas para conferir regras completas
7. `studies/day_swing_strategy_hunt/DEAD_ENDS.md`, se a ideia parecer recorrente

Nao carregue todo o historico em cada sessao. Use `MEMORY.md` + ultimo `SUMMARY.md` + `next_prompt.md` como contexto curto.

## Como Rodar Uma Iteracao

1. Escolha uma unica hipotese simples, com citacao de livro para estrategia, indicador, parametro e gate.
2. Crie `iterations/NNN-slug/PRE_REG.md` antes de qualquer backtest.
3. Rode apenas o minimo necessario para testar dados, baselines e a hipotese.
4. Grave `RESULTS.json` com metricas, gates, custos, baselines e verdict.
5. Grave `SUMMARY.md` com leitura humana curta.
6. Atualize `MEMORY.md` e, se aplicavel, `DEAD_ENDS.md`.
7. Reescreva `next_prompt.md` para a proxima sessao Codex.

## Proibido

- Usar HappyForex como dataset de treino.
- Usar selecao ex-post por PnL futuro como estrategia.
- Aceitar winner single-asset.
- Otimizar threshold depois de ver resultado.
- Usar M1/M5 no ciclo inicial, exceto diagnostico de execucao.
- Fazer paper/live sem autorizacao explicita e override formal.
- Mexer em `docs/investment-mandate.md` ou `frozen_rules/`.
