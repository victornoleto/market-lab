# LOOP_PROMPT — success_trading_strat

This prompt is injected by `loop.sh` into each fresh backend session.

```text
Estamos no repo `/var/www/github/finances/market-lab` rodando o
`success_trading_strat`. Esta é uma sessão limpa de OpenCode/GPT-5.5 para UMA
iteração. Não espere resposta humana no meio da iteração.

Objetivo do estudo: encontrar uma estratégia eficiente usando o processo do
vídeo `NLBXgSmRBgU`: in-sample excellence, in-sample MCPT, walk-forward e
walk-forward MCPT. Estes gates complementam, mas não substituem, PBO, DSR, WF,
OOS, FWD, bootstrap e cross-lib `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.

PASSO 1 — Leia estado em ordem, antes de rodar qualquer teste:
1. CLAUDE.md
2. docs/PUBLIC_SUMMARY.md
3. docs/CURRENT_STATE.md
4. docs/investment-mandate.md
5. studies/success_trading_strat/MEMORY.md
6. studies/success_trading_strat/SPEC.md
7. studies/success_trading_strat/LOOP_PROTOCOL.md
8. studies/success_trading_strat/PHASE2_INTRADAY_SWING_SPEC.md
9. O último `studies/success_trading_strat/iters/phase02/*/SUMMARY.md`, se existir
10. Um livro relevante em `books/summaries/` ou `knowledge/SKILL.md`

PASSO 2 — Verifique baseline operacional:
- `git status --short`
- `uv run pytest --collect-only -q`

Se `docs/investment-mandate.md` estiver modificado, pare. Se houver mudanças
não relacionadas em outros arquivos, não reverta; apenas não toque nelas.

PASSO 3 — Escolha UMA hipótese:
- Esta é Phase 2: priorize estratégias 15m/1h/1d conforme
  `PHASE2_INTRADAY_SWING_SPEC.md`, com foco em gold/XAUUSD, short swing 1h/daily
  hybrid e daily swing. Antes de qualquer teste intraday, audite arquivo físico,
  range temporal, timezone/sessão e missing bars; manifesto sozinho não basta.
- Regra econômica Phase 2: se a estratégia não bate o buy-and-hold do ativo
  relevante em CAGR na mesma janela, ela deve fechar `fail` e não pode receber
  `candidate_watchlist`, `paper_trade_candidate` ou `strict_winner`. Melhor MDD
  sozinho não compensa CAGR menor, exceto se a hipótese for explicitamente de
  hedge/cash-parking e isso tiver sido pré-registrado.
- Se a iteração anterior encontrou `winner` ou `promising_not_validated`, não
  pare o estudo: escolha entre (a) stress/otimizar a mesma família com novos
  trials explícitos ou (b) seguir por mecanismo diferente se houver fragilidade
  `[testing_tuning, p.327-335]`.
- Toda escolha de indicador, parâmetro, gate ou estratégia precisa de citação.
- Evite grids grandes; DSR usa cumulative_n_trials.

PASSO 4 — Crie `PRE_REG.md` antes de testar:
- hipótese e citações;
- configs exatos;
- dados e janela;
- benchmark same-asset buy-and-hold e SPY buy-and-hold de oportunidade;
- kill rule explícita: CAGR <= same-asset buy-and-hold => `fail`;
- gates planejados, incluindo MCPT quando aplicável;
- kill rules;
- cumulative_n_trials antes/depois.

PASSO 5 — Implemente e rode o mínimo necessário:
- Use infraestrutura existente quando seguro.
- Código específico da iteração fica dentro da pasta da iteração.
- Helpers reutilizáveis podem ir em `studies/success_trading_strat/scripts/`.
- Não faça refactor amplo.
- Não faça commit nem push.

PASSO 6 — Produza `RESULTS.json`:
Campos mínimos:
{
  "iteration": "NNN-slug",
  "status": "strict_winner|candidate_watchlist|paper_trade_candidate|promising_not_validated|fail|infrastructure_only|data_blocked",
  "pre_registered": true,
  "n_trials": 0,
  "mcpt_reps": {},
  "best_config": null,
  "winner": false,
  "metrics": {},
  "benchmark": {},
  "gates": {},
  "kill_switches": [],
  "artifacts": [],
  "notes": ""
}

PASSO 7 — Produza `SUMMARY.md` curto:
- verdict;
- o que foi testado;
- comparação com benchmark;
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

PASSO 9 — Pare. Não rode a próxima iteração nesta sessão.

Guardrails finais:
- Capital segue 100% Plano C; sem deploy.
- PBO/DSR são hard-blocks.
- MCPT é gate adicional, não substituto.
- `candidate_watchlist` não é deploy; é apenas triagem pragmática para revisão ou
  paper trading futuro.
- Não promova estratégia que troca CAGR por drawdown menor sem bater buy-and-hold
  no retorno composto alinhado.
- Não modificar `docs/investment-mandate.md`.
- Não commit/push.
```
