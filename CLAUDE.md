# CLAUDE.md — ai-trade

Instruções de colaboração com o Claude Code neste repositório.

---

## Leituras iniciais obrigatórias

Ao abrir qualquer sessão sobre este projeto, leia nesta ordem:

1. `jornada/README.md` — retrato atual em linguagem humana (estado, diagnóstico,
   próximo passo). **Sempre começa aqui.**
2. `ROADMAP.md` — mapa técnico detalhado das fases 0-7, decisões deferidas
   e "Current status" com verdict dos runs.
3. `README.md` — setup, arquitetura de alto nível, como rodar backtests.
4. `specs/backtest_phase2.md` e `specs/backtest_phase2_5_ehlers.md` —
   specs executáveis com Conclusion field por tarefa.
5. `docs/investment-mandate.md` — **regras permanentes** sobre capital
   allocation, CAGR mínimo, alavancagem, multi-asset, threading model.
   O sumário abaixo é o que sempre carrega em contexto; o mandate
   completo tem a rationale.

---

## 📌 Investment Mandate (ler antes de qualquer discussão de strategy)

**🛑 MODO MAINTENANCE (consolidação 2026-04-23 — mandate §1, §7):** após
113/113 honest FAIL em 2 semanas (Phase 3.5f-3.8 + D-MVP + E-MVP), o
projeto entrou em **modo maintenance**. Alocação consolidada em **100%
Plano C passive factor-tilted**; Strategy A/B/D marcadas **DORMANT**
(0% capital, infra retida para reativação futura). Não há hunt ativo
planejado; revisão em 6-12 meses.

Sumário do `docs/investment-mandate.md`. Regras invioláveis (permanecem
válidas caso algum slot seja reativado no futuro):

1. **Capital allocation (consolidado 2026-04-23):** **100% Plano C passive
   factor-tilted** (`portfolio-aposentadoria.md`). Strategy A, B, D =
   **0% DORMANT** com infra preservada. Strategy E = infra experimental
   retida em `scripts/phase_e_mvp/`. Revisão programada: 6-12 meses.
2. **CAGR e MDD são tiers warning-only (não bloqueantes) desde 2026-04-22
   (mandate §2.2, §2.3, §7).** Benchmarks âncora permanecem válidos pra
   future reativação: **CDI líquido ~11%/ano** (Strategy B/D comparator),
   **SPY buy-hold líquido via Inter ~8,5%/ano**. Tiers por rota:
   Folclore < 11% (B/D) / < 13% (A); Marginal 11-17% (B/D) / 13-25% (A);
   **Válido 17-25% (B/D) / 25-50% (A)**; Forte 25-40% (B/D) / 50-100% (A);
   Extraordinário > 40% (B/D) / > 100% (A, suspect). MDD: A ≤ 25%
   Excelente, ≤ 40% Válido, ≤ 75% Warning, > 75% Reject; B/D ≤ 15%
   Excelente, ≤ 25% Válido, ≤ 50% Warning, > 50% Reject.
3. **Strategy A (Pepperstone CFD) DORMANT.** Caso reativada: multi-asset
   obrigatório (SPY/QQQ/Gold/BTC/ETH/FX majors), alavancagem por sweep
   empírico 1:1→1:200 × Kelly f/2, staging pós-live USD 500-1k inicial
   até cap USD 5-10k (SCB Bahamas Tier-3). Single-asset edge NÃO aceito.
4. **Strategy B (swing broker US LETF rotation) DORMANT.** Caso
   reativada: Inter Internacional (§4.6), tese LETF rotation
   Gayed-anchored `[leverage_for_the_long_run]` única fonte científica.
   CPCV + PBO + splits mutuamente exclusivos + bootstrap 0.001 + 15% DARF
   sempre. Goal tier Válido 17-25% líquido.
4b. **Strategy D (swing BR ranking mensal) DORMANT.** Caso reativada:
   IBrX-100 proxy + cadência mensal + 4 famílias (D1 Clenow / D2 Magic
   Formula / D3 V+M+Q / D4 low-vol+mom) + tax R$20k condicional.
   Phase E-MVP (multi-market extension) já rodou em 2026-04-23 e falhou
   catastroficamente (PBO 0.786) — próxima reativação deve assumir
   literatura/regime novos, não re-rodar mesmos signals. Spec:
   `specs/strategy_d_br_ranking.md`.
5. **Gates hard-block (zero bypass) — permanecem válidos pra reativação**:
   PBO<0.5 + DSR p<0.05 + WF≥6/8 + single-block OOS + FWD stress +
   bootstrap 99.9% CI low > 0 + cross-lib ±3pp CAGR. CAGR e MDD são tiers
   §2.2/§2.3 (warning-only, não bloqueantes). "Quase lá" não passa.
6. **Threading model live (Phase 4) — pausado indefinidamente.** Spec
   preservado em `specs/phase_4_paper_trading.md` se futuro slot reativar.
7. **Dynamic sizing (preservado no spec):** position size decresce com
   equity (fase agressiva até 2× equity inicial, preservação depois).

Qualquer divergência deste mandate é bug de raciocínio — consulte
`docs/investment-mandate.md` §7 (histórico de overrides) antes de
agir contra.

---

## Regra 1 — Manter jornada/ atualizado

**Sempre que houver progresso relevante, crie um novo arquivo em
`jornada/` antes de encerrar a sessão.**

O que conta como "progresso relevante":
- Verdict de um Run de backtest (pass/fail com explicação).
- Decisão de arquitetura ou escolha técnica (ex.: Tiingo vs EOD, manter vs
  pivotar estratégia).
- Commit que muda o estado público do projeto (não toda refatoração interna).
- Pivot / mudança de prioridade no ROADMAP.

Como escrever a entrada:
- Criar arquivo `jornada/YYYY-MM-DD-HHmm-slug.md` com `# título` no topo.
- Linguagem humana, analogias permitidas, sem jargão sem glossário.
- Se introduzir termo novo, adicionar no "Glossário mínimo" em `jornada/README.md`.
- Atualizar a lista de entradas em `jornada/README.md` (newest first).
- Atualizar as seções fixas de `jornada/README.md` (`Onde estamos hoje`,
  `O que vem a seguir`) quando relevante — elas refletem o **estado atual**.

O que **não** escrever nas entradas:
- Detalhes de implementação linha-a-linha (isso vai em `specs/` ou
  commit messages).
- Progresso de testes unitários ou refactoring interno.
- Qualquer coisa que o user não-especialista não conseguiria ler e
  entender.

---

## Regra 2 — Citação obrigatória em toda decisão técnica

Regra inviolável do projeto: **toda escolha de indicador, parâmetro,
gate ou estratégia cita um livro específico** no formato `[book.slug,
p.X]` (ou `[ch.Y]` quando não há página).

Exemplos:
- ✅ "PBO > 0.5 ⇒ descarta `[advances_fin_ml, p.208-211]`"
- ✅ "Lookback 90 dias `[stocks_on_the_move, p.81]`"
- ❌ "Vou usar lookback de 90 dias porque costuma funcionar" (sem citação)
- ❌ "Baseado em experiência, o Sharpe 1.0 é o gate" (palpite)

Citações vão em docstrings, comentários de decisão, PR descriptions,
reports e entradas de JORNADA.md. Os 33 livros absorvidos estão em
`books/summaries/` (e a Skill agregada em `knowledge/SKILL.md`) —
consulte antes de afirmar.

---

## Regra 3 — jornada/ é complementar, não substituto

`jornada/` não substitui:
- `ROADMAP.md` — continua sendo o mapa técnico autoritativo.
- `README.md` — continua sendo o ponto de entrada pra setup.
- `specs/*.md` — continuam sendo os specs executáveis detalhados.
- `books/summaries/*.md` — continuam sendo a fonte de citação.

`jornada/` **é** a vista humana do conjunto. Quando o conteúdo técnico
detalhado diverge da narrativa humana, o conteúdo técnico ganha —
`jornada/README.md` vira "outdated" e precisa de atualização.

---

## Convenções de código (resumo)

- Python 3.12, tipagem gradual via `typing`, `pyproject.toml` com `uv`.
- Testes: `pytest`, meta atual 461 testes. **Não quebrar baseline.**
- LLM SDK é proibido em Python runtime: toda inteligência LLM roda
  dentro do Claude Code CLI (subagents + slash commands).
- Estratégias novas herdam de `backtest/strategies/base.py`. Sources
  de dados herdam de `backtest/data/` interface.
- Reports obrigatoriamente incluem disclaimer de survivorship se a
  fonte for yfinance/Wikipedia. Tiingo storage libera disclaimer.
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).

---

## Referências rápidas

- Plano da sessão atual: `/home/victor/.claude/plans/abstract-juggling-wombat.md`
- Skill loadable: `knowledge/SKILL.md`
- Inventário de livros (slug ↔ título): `books/MAPPING.md`
- Logs unificados: `logs/grid.log`, `logs/tiingo.log`
