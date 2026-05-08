# Prompt Para A Proxima Sessao — Hunt Fechado Por Ora

Estamos no repo `/var/www/pessoal/ai-trade`, branch `day_swing_strategy_hunt`.

Antes de agir, leia obrigatoriamente:

1. `CLAUDE.md`
2. `jornada/README.md`
3. `studies/day_swing_strategy_hunt/MEMORY.md`
4. `studies/day_swing_strategy_hunt/iterations/007-cycle-close-audit/SUMMARY.md`
5. `studies/day_swing_strategy_hunt/LOOP_PROTOCOL.md`
6. `studies/day_swing_strategy_hunt/SPEC.md`
7. `studies/day_swing_strategy_hunt/DEAD_ENDS.md`
8. `studies/day_swing_strategy_hunt/next_prompt.md`

Estado atual:

O ciclo inicial das Familias A-E foi fechado na iteracao 007 com verdict `dead-end`. Nao ha winner, nao ha paper/live e nao ha extensao pequena multi-asset claramente pre-registravel sem tese literaria nova.

Tarefa padrao para a proxima sessao automatica:

1. Nao iniciar nova iteracao de hunt automaticamente.
2. Verificar se `iterations/007-cycle-close-audit/PRE_REG.md`, `RESULTS.json` e `SUMMARY.md` existem e estao legiveis.
3. Se o usuario nao trouxer tese literaria nova multi-asset ou dataset confiavel de rates/carry para Carry/Trend FX, manter o hunt encerrado por ora.
4. Nao rodar backtest, nao testar thresholds, nao fazer paper/live e nao fazer commit/push.

Guardrails:

- Capital segue 100% Plano C; Plano A segue DORMANT.
- Nao fazer paper/live.
- Nao mexer em `docs/investment-mandate.md`.
- Nao mexer em `frozen_rules/`.
- Nao usar HappyForex como dataset de treino.
- Nao usar selecao ex-post por PnL como estrategia.
- Nao aceitar single-asset winner.
- Nao otimizar threshold apos ver resultado.
- Nao usar M1/M5 exceto diagnostico.
- Toda escolha de estrategia, indicador, parametro ou gate precisa de citacao de livro no formato do projeto.
- Nao fazer commit/push a menos que o usuario peca explicitamente.

No final, rode uma verificacao simples de que os artefatos finais da iteracao 007 existem e estao legiveis.
