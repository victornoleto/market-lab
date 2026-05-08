# CLAUDE.md — market-lab

## Leituras obrigatórias (nesta ordem)

1. `docs/PUBLIC_SUMMARY.md` — resumo público do projeto.
2. `docs/CURRENT_STATE.md` — snapshot técnico atual.
3. `README.md` — setup e estrutura pública.
4. `docs/PROJECT_HISTORY.md` — histórico público condensado.
5. `docs/investment-mandate.md` — regras permanentes (capital, CAGR, alavancagem, threading). O sumário abaixo é o operacional; o mandate completo tem rationale e §7 (overrides).

---

## 📌 Investment Mandate — sumário operacional

**🛑 MAINTENANCE MODE (2026-04-23, mandate §1, §7):** após 113/113 honest FAIL em 2 semanas (Phase 3.5f-3.8 + D-MVP + E-MVP), alocação consolidada em **100% Plano C passive factor-tilted**. Strategy A/B/D **DORMANT** (0% capital, infra retida). Sem hunt ativo; revisão em 6-12 meses.

Regras invioláveis (válidas se algum slot reativar):

1. **Capital:** 100% Plano C (documentação pessoal movida para `victor-ia/verticals/investments/`). A/B/D = 0% DORMANT. E = infra experimental em `scripts/phase_e_mvp/`.
2. **CAGR e MDD = tiers warning-only** desde 2026-04-22 (mandate §2.2/§2.3). Benchmarks: CDI líquido ~11%/ano (B/D), SPY buy-hold via Inter ~8,5%/ano. Tier "Válido": A 25-50%, B/D 17-25%. Tabela completa de tiers e MDD: `docs/investment-mandate.md` §2.
3. **Strategy A (Pepperstone CFD) DORMANT.** Reativação exige: multi-asset (SPY/QQQ/Gold/BTC/ETH/FX majors), alavancagem por sweep 1:1→1:200 × Kelly f/2, staging USD 500-1k → cap 5-10k (SCB Bahamas Tier-3). Single-asset edge **não** aceito.
4. **Strategy B (swing US LETF rotation) DORMANT.** Reativação: Inter Internacional, tese Gayed-anchored `[leverage_for_the_long_run]` única fonte, CPCV+PBO+splits mutex+bootstrap 0.001+15% DARF. Tier alvo: Válido 17-25% líquido.
4b. **Strategy D (swing BR ranking mensal) DORMANT.** Reativação: IBrX-100 proxy, mensal, 4 famílias (D1 Clenow / D2 Magic Formula / D3 V+M+Q / D4 low-vol+mom), tax R$20k condicional. Phase E-MVP (2026-04-23) falhou catastroficamente (PBO 0.786) — próxima reativação assume literatura/regime novos. Novas specs devem viver em `docs/specs/`.
5. **Gates hard-block (zero bypass):** PBO<0.5, DSR p<0.05, WF≥6/8, single-block OOS, FWD stress, bootstrap 99.9% CI low > 0, cross-lib ±3pp CAGR. CAGR/MDD são tiers (não bloqueantes). "Quase lá" não passa.
6. **Threading model live (Phase 4) pausado.** Se retomado, escrever spec nova em `docs/specs/`.
7. **Dynamic sizing preservado:** position size decresce com equity (agressiva até 2× inicial, preservação depois).

Divergir do mandate = bug de raciocínio. Consultar §7 (overrides) antes.

---

## Regra 1 — docs públicos atualizados

Sempre que houver progresso relevante que mude o estado público do projeto,
atualizar `docs/CURRENT_STATE.md` e, se for uma mudança histórica ou narrativa,
também `docs/PROJECT_HISTORY.md`.

**Conta como progresso:** verdict de Run, decisão de arquitetura, commit que muda estado público, pivot/mudança de prioridade.

**Não conta:** detalhes de implementação (vão em `docs/specs/` ou commit messages), refactor interno, conteúdo que não muda o entendimento público do projeto.

---

## Regra 2 — Citação obrigatória

**Toda escolha de indicador, parâmetro, gate ou estratégia cita um livro:** `[book.slug, p.X]` (ou `[ch.Y]` se sem página).

- ✅ "PBO > 0.5 ⇒ descarta `[advances_fin_ml, p.208-211]`"
- ❌ "Lookback 90 dias porque costuma funcionar" (sem citação)

Citações vão em docstrings, comentários de decisão, PR descriptions, reports e docs técnicos. Fonte: 33 livros em `books/summaries/` (Skill agregada em `knowledge/SKILL.md`).

---

## Regra 3 — docs públicos são complementares

`docs/PROJECT_HISTORY.md` e `docs/PUBLIC_SUMMARY.md` são vistas públicas resumidas. Quando técnico diverge da narrativa, técnico ganha e os docs públicos precisam ser atualizados. Novas specs técnicas devem viver em `docs/specs/`.

---

## Convenções

- Python 3.12, `pyproject.toml` com `uv`, tipagem gradual (`typing`).
- Testes: `pytest`, baseline 813 testes — **não quebrar.**
- LLM SDK proibido em runtime: inteligência LLM roda no Claude Code CLI (subagents + slash commands).
- Estratégias herdam `backtest/strategies/base.py`. Sources herdam interface `backtest/data/`.
- Reports incluem disclaimer survivorship se fonte = yfinance/Wikipedia. Tiingo storage libera.
- Commits: Conventional (`feat:`, `fix:`, `docs:`, `chore:`).

---

## Referências rápidas

- Estado atual snapshot: `docs/CURRENT_STATE.md`
- Cleanup playbook: `docs/CLEANUP.md`; logs forenses em `docs/CLEANUP_*_LOG.md`
- Skill loadable: `knowledge/SKILL.md`
- Inventário livros (slug ↔ título): `books/MAPPING.md`
- Logs unificados: `logs/grid.log`, `logs/tiingo.log`
