# LOOP_PROTOCOL — Day/Swing Strategy Hunt

Este protocolo existe para cada iteracao caber em uma sessao Codex futura.

## Contexto Curto Por Sessao

No inicio de cada sessao, leia:

1. `CLAUDE.md`
2. `jornada/README.md`
3. `studies/day_swing_strategy_hunt/MEMORY.md`
4. Ultimo `iterations/*/SUMMARY.md`, se existir
5. `studies/day_swing_strategy_hunt/next_prompt.md`

Nao carregar todo o historico. Use `SPEC.md` apenas para conferir contrato completo e `DEAD_ENDS.md` quando a ideia parecer recorrente.

## Passo A Passo Da Iteracao

### 1. Escolher Uma Hipotese

Escolha uma unica hipotese simples. Toda escolha de estrategia, indicador, parametro e gate deve ter citacao de livro no formato do projeto.

Exemplo valido: Time-Series Momentum H4/D1 com lookbacks pre-registrados, tese baseada em trend following `[systematic_trading, ch.10]`.

### 2. Criar Pre-Registration

Antes de rodar qualquer teste, crie:

`studies/day_swing_strategy_hunt/iterations/NNN-slug/PRE_REG.md`

O `PRE_REG.md` deve conter:

- Hipotese.
- Citacoes.
- Universo.
- Frequencias.
- Dados esperados.
- Custos base/conservador/stress.
- Parametros e grade congelados.
- Baselines obrigatorios.
- Gates obrigatorios.
- Kill-switches relevantes.
- O que conta como positive, negative, inconclusive ou dead-end.

Se o pre-registro nao existe, o teste nao vale.

### 3. Implementar E Rodar Apenas O Minimo Necessario

Nao criar framework grande. Preferir scripts pequenos e reutilizar infra existente quando possivel.

Ordem recomendada:

1. `DATA_AUDIT` ou sanity de dados, se a iteracao depender de dados novos.
2. Baselines minimos.
3. Estrategia minima.
4. Gates minimos aplicaveis ao escopo.

Nao ampliar escopo no meio da iteracao. Nova ideia vira proximo `next_prompt.md`.

### 4. Produzir RESULTS.json

Criar:

`studies/day_swing_strategy_hunt/iterations/NNN-slug/RESULTS.json`

Campos minimos:

```json
{
  "iteration": "NNN-slug",
  "status": "positive|negative|inconclusive|dead-end",
  "hypothesis": "short name",
  "pre_registered": true,
  "universe": [],
  "frequencies": [],
  "cost_scenarios": [],
  "baselines": {},
  "strategy_results": {},
  "gates": {},
  "kill_switches": [],
  "n_trials": 0,
  "artifacts": [],
  "notes": ""
}
```

Nao inventar campo com metricas nao calculadas. Use `null` ou omita com nota explicita.

### 5. Produzir SUMMARY.md

Criar:

`studies/day_swing_strategy_hunt/iterations/NNN-slug/SUMMARY.md`

O resumo deve ser curto e conter:

- Verdict.
- O que foi testado.
- Dados usados e caveats.
- Comparacao contra baselines.
- Gates pass/fail.
- Kill-switches acionados.
- Licao para a proxima sessao.

### 6. Atualizar MEMORY.md E DEAD_ENDS.md

Atualize `MEMORY.md` para manter contexto curto:

- Hipoteses testadas.
- Ultimo resultado.
- Licoes novas.
- Proximo passo recomendado.

Atualize `DEAD_ENDS.md` se uma ideia/familia nao deve ser reaberta sem evidencia nova.

### 7. Escrever next_prompt.md

Reescreva `studies/day_swing_strategy_hunt/next_prompt.md` com o prompt exato para a proxima sessao Codex.

O prompt deve:

- Mandar ler `CLAUDE.md`, `jornada/README.md`, `MEMORY.md`, ultimo `SUMMARY.md` e `next_prompt.md`.
- Definir uma unica tarefa pequena.
- Repetir guardrails criticos.
- Pedir pre-registro antes de teste.
- Pedir verificacao simples no final.

## Regras De Escopo

- Uma hipotese por iteracao.
- Uma familia por iteracao, salvo `DATA_AUDIT` comum.
- Nao fazer paper/live.
- Nao fazer commit/push sem pedido explicito do usuario.
- Nao otimizar threshold apos ver resultado.
- Nao aceitar single-asset winner.
- Nao usar HappyForex como treino.
- Nao usar oracle/top-K por PnL futuro como estrategia.
