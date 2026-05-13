# LOOP_PROMPT — spy_beater_hunt_v2

This prompt is injected by `loop.sh` into each fresh backend session.

```
Estamos no repo `/var/www/github/finances/market-lab` rodando o
`spy_beater_hunt_v2`. Esta é uma sessão limpa de OpenCode/GPT-5.5 para UMA
iteração. Não espere resposta humana no meio da iteração.

Objetivo do estudo: encontrar uma estratégia de longo prazo que bata SPY
buy-and-hold e passe gates honestos de overfit: PBO, DSR, WF, OOS, FWD,
bootstrap e cross-lib `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.

PASSO 1 — Leia estado em ordem, antes de rodar qualquer teste:
1. CLAUDE.md
2. docs/PUBLIC_SUMMARY.md
3. docs/CURRENT_STATE.md
4. docs/investment-mandate.md
5. studies/spy_beater_hunt_v2/MEMORY.md
6. studies/spy_beater_hunt_v2/SPEC.md
7. studies/spy_beater_hunt_v2/LOOP_PROTOCOL.md
8. O último `studies/spy_beater_hunt_v2/iterations/*/SUMMARY.md`, se existir
9. Um livro relevante em `books/summaries/` ou `knowledge/SKILL.md`

PASSO 2 — Verifique baseline operacional:
- `git status --short`
- `uv run pytest --collect-only -q`

Se `docs/investment-mandate.md` estiver modificado, pare. Se houver mudanças
não relacionadas em outros arquivos, não reverta; apenas não toque nelas.

PASSO 3 — Escolha UMA hipótese:
- Iteração 001 deve ser bootstrap/audit: inventário de dados/runners/gates,
  benchmark SPY e direção inicial. Não declare winner.
- Iterações posteriores devem escolher uma família citable e distinta das já
  refutadas em MEMORY.
- Toda escolha de indicador, parâmetro, gate ou estratégia precisa de citação.
- Evite grids grandes; DSR usa cumulative_n_trials.

PASSO 4 — Crie `PRE_REG.md` antes de testar:
- hipótese e citação;
- configs exatos;
- dados e janela;
- gates planejados;
- kill rules;
- cumulative_n_trials antes/depois.

PASSO 5 — Implemente e rode o mínimo necessário:
- Use infraestrutura existente quando seguro.
- Código novo específico da iteração fica dentro da pasta da iteração.
- Não faça refactor amplo.
- Não faça commit nem push.

PASSO 6 — Produza `RESULTS.json`:
Campos mínimos:
{
  "iteration": "NNN-slug",
  "status": "winner|promising_not_validated|fail|infrastructure_only|data_blocked",
  "pre_registered": true,
  "n_trials": 0,
  "best_config": null,
  "beats_spy_cagr": false,
  "winner": false,
  "metrics": {},
  "spy_benchmark": {},
  "gates": {},
  "kill_switches": [],
  "artifacts": [],
  "notes": ""
}

PASSO 7 — Produza `SUMMARY.md` curto:
- verdict;
- o que foi testado;
- comparação com SPY;
- gates pass/fail ou por que não foram computados;
- lições;
- próximo passo recomendado.

PASSO 8 — Atualize `MEMORY.md`:
- total_iterations++;
- cumulative_n_trials += n_trials;
- latest_*;
- hipótese testada;
- dead-ends se aplicável;
- próximo passo.

PASSO 9 — Pare. Não rode a próxima iteração nesta sessão. O `loop.sh` abrirá a
próxima sessão limpa.

Guardrails finais:
- Capital segue 100% Plano C; sem deploy.
- PBO/DSR são hard-blocks.
- Não modificar `docs/investment-mandate.md`.
- Não commit/push.
```
