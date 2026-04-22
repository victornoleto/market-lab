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

Sumário do `docs/investment-mandate.md`. Regras invioláveis:

1. **Capital allocation:** 60-80% passive buy&hold (ver
   `portfolio-aposentadoria.md`), 20-40% split entre 2 strategies
   ativas: **Strategy A (principal, Path A short-hold CFD
   Pepperstone, agressiva alavancada)** e **Strategy B (secundária,
   Path B swing broker BR, moderada).**
2. **CAGR e MDD são tiers warning-only (não bloqueantes) desde 2026-04-22
   (mandate §2.2, §2.3, §7).** Benchmarks âncora: **CDI líquido ~11%/ano**
   (CDI 13% × (1 − 15% IR)) e **SPY buy-hold líquido via Inter ~8,5%/ano**.
   CAGR tiers por rota: **Strategy B (Inter pós-15%-DARF)** — Folclore
   < 11%, Marginal 11-17%, **Válido 17-25%**, Forte 25-40%, Extraordinário
   > 40% (suspect). **Strategy A (Pepperstone, sem DARF modelado por decisão
   usuário 2026-04-22)** — Folclore < 13%, Marginal 13-25%, **Válido
   25-50%**, Forte 50-100%, Extraordinário > 100% (suspect). MDD tiers
   análogos: A Excelente ≤ 25%, Válido ≤ 40%, Warning 40-75%, Reject
   > 75%; B Excelente ≤ 15%, Válido ≤ 25%, Warning 25-50%, Reject > 50%.
   **Folclore/Reject tiers = não-winner, não vai a live**, mas o backtest
   NÃO auto-rejeita no gate-check (antes auto-rejeitava; agora classifica
   + warning pra sign-off do usuário).
3. **Strategy A (Path A Pepperstone CFD) é multi-asset obrigatório**
   (SPY/QQQ/Gold/BTC/ETH/FX majors), com universe pre-screening
   (Hurst/ATR/spread/volume) e alavancagem ótima via sweep empírico
   1:1 → 1:200 cross-checked com Kelly f/2. Goal (não mais gate):
   **5-10%/mês** — continua sendo onde queremos chegar, mas tier "Válido"
   começa em 25% CAGR net. Single-asset edge NÃO é aceito como winner
   final. **Staging obrigatório pós-live (§4.8):** USD 500-1k inicial
   (SCB Bahamas é Tier-3 sem investor compensation), escalada condicional
   em degraus, cap USD 5-10k até 6 meses verdes.
4. **Strategy B (Path B swing broker) é a SEGUNDA strategy do projeto**
   (swing moderado, complementa Strategy A). Tese: **família LETF
   rotation** — regime MA (SMA ou EMA) sobre SPY → LETF (UPRO 3x ou
   SSO 2x) em on-regime, cash (ou gold) em off-regime. **Base
   científica ÚNICA: `books/summaries/leverage_for_the_long_run.md`**
   (Gayed 2016/2020); o Reddit study do usuário
   (`docs/reference/letf_rotation_reddit_analysis.md`) é
   trial-and-error ilustrativo, **NÃO gospel a replicar**. Lead B1
   projeta do zero com base em Gayed, testa grid amplo (360 configs),
   e o winner pode ou não parecer com a config do Reddit. **Overfit
   control:** CPCV + PBO + splits mutuamente exclusivos (IS 1970-2000
   / OOS 2001-2015 / Stress 2016-2026) + stationary block bootstrap
   a 0.001. 15% IR BR sempre; UPRO/SSO sintéticos pre-2009/2006 via
   `r = L × r_SPX_TR - drag - expense`. Goal: tier "Válido" CAGR 17-25%
   líquido (pós-15%-DARF), ideal "Forte" 25-40%.
5. **Gates hard-block (zero bypass)** — `§2.4`: PBO<0.5 + DSR p<0.05 +
   WF≥6/8 + single-block OOS + FWD stress + bootstrap 99.9% CI low > 0 +
   cross-lib concordância ±3pp CAGR. **CAGR e MDD NÃO estão nesta lista**
   (viraram tiers §2.2/§2.3 em 2026-04-22). "Quase lá" nos gates hard-block
   ainda não passa.
6. **Threading model live (Phase 4):** 1 thread/processo por ativo
   monitorado, state isolado, perks por-ativo opcionais (sessão FX,
   pre/post market equity, news filter gold).
7. **Dynamic sizing:** position size decresce com equity (fase
   agressiva até 2× equity inicial, fase preservação depois com
   multiplicador ≤ 1).

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
