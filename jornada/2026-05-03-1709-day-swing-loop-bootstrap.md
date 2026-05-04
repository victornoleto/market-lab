# Day/swing strategy hunt: loop operacional criado

Foi criado o bootstrap do novo estudo `studies/day_swing_strategy_hunt/` para procurar, ou rejeitar cedo, estrategias simples de day/swing trade em FX, Gold e Crypto.

O loop nasce research-only: capital continua 100% Plano C, Plano A segue DORMANT, sem paper/live, sem uso de HappyForex como treino e sem mexer em `docs/investment-mandate.md` ou `frozen_rules/`.

Arquivos criados:

- `README.md`: como usar o estudo e quais arquivos ler em cada sessao.
- `SPEC.md`: universo inicial, frequencias D1/H4, familias candidatas, custos, baselines, gates e kill-switches K1-K9.
- `LOOP_PROTOCOL.md`: uma hipotese por iteracao, pre-registro antes de teste, `RESULTS.json`, `SUMMARY.md`, memoria curta e proximo prompt.
- `MEMORY.md`: contexto curto para sessoes futuras.
- `DEAD_ENDS.md`: dead-ends herdados de HappyForex/Gold/oracle.
- `next_prompt.md`: prompt da iteracao 001, focado em DATA_AUDIT + baselines para Time-Series Momentum H4/D1.

Nenhuma hipotese foi testada ainda. O proximo passo recomendado e a iteracao 001: auditar dados/custos D1/H4 e criar baselines minimos antes de testar a estrategia completa.
