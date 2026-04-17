# Spec — Post-Winners Cleanup

Executable plan para enxugar o repositório ai-trade após encontrar os 2
winners production-ready (iter 27, 2026-04-16). Cada tarefa tem checkbox
e campo **Conclusion** (preencher ao executar). **DO NOT EXECUTE sem
leitura completa deste spec.**

**Branch de trabalho:** `cleanup/post-winners-20260416` (criar a partir de
`main` após o merge da Task 2).

---

## 0. Contexto

Ao final do loop auto-dirigido do dia 2026-04-16, o projeto acumulou:
- ~40 jornadas (muitas com `⚠️ RETRACTED` pela data-bug da Tiingo IEX).
- ~25 scripts em `scripts/` (maioria one-shots de iters retratadas).
- ~30 diretórios em `reports/` (pré e pós-cleanup misturados).
- 33 summaries em `books/summaries/` (nem todos citados nos winners).
- Código em `src/ai_trade/backtest/strategies/` com strategies
  descartadas (Clenow, Ehlers, Kalman pairs, Chan pairs, Vol-Expansion).

Objetivo: reduzir para o **mínimo necessário pra reproduzir e operar os
2 winners + manter a infra pra futuras buscas**, SEM perder qualquer
informação relevante para:
1. Reprodução dos 2 winners (código + dados + citações).
2. Entendimento histórico de *por que* chegamos a eles (jornada, memory).
3. Infra do backtest engine + validation (nenhum desses layers é removido).

---

## 1. Scope

### Dentro do scope

- Merge da branch `self-improve/post-cleanup-20260416` em `main`.
- Apagar/arquivar código-fonte de strategies não-winners.
- Apagar/arquivar scripts one-shot de iters retratadas.
- Consolidar jornadas retratadas em 1 arquivo de archive.
- Audit de citações: listar quais dos 33 books foram de fato citados nos
  winners; mover summaries não-citados para `books/summaries/_archive/`.
- Reduzir `reports/` aos diretórios dos 2 winners + Phase B.
- Atualizar `ROADMAP.md` e `jornada/README.md` para refletir estado
  pós-cleanup.

### Fora do scope

- Otimização de alavancagem (Pepperstone 1:5/1:10/1:20/.../1:200) do
  BollingerMR — flag em §8 como Phase 3 Lead A1.
- Paper/live trading — fases 3-4 do ROADMAP, fora.
- Remoção de livros do diretório físico `books/raw/` e `books/extracted/`
  (só summaries; os raw continuam no disco como material-fonte).
- Alterações no engine `src/ai_trade/backtest/{data,engine,validation,metrics}/`
  — mantém tudo, é infra reutilizável.
- Execução dos 5 Phase 3 leads listados em §8 — esses rodam DEPOIS do
  cleanup, em branch separada.

---

## 2. Preservation mandate — MUST NOT DELETE

Lista absoluta. Qualquer tarefa que tocar esses arquivos falha o spec.

### 2.1 Winners — código

- `src/ai_trade/backtest/strategies/bollinger_mr.py` (ou o nome atual)
- `src/ai_trade/backtest/strategies/etf_rotation.py` (ou o nome atual)
- `src/ai_trade/backtest/strategies/base.py`
- Quaisquer helpers citados por esses 2 arquivos (GARCH sizing,
  regime filter, SMA utils).
- Testes correspondentes em `tests/` (grep `BollingerMR`, `ETFRotation`).

### 2.2 Winners — jornadas

- `jornada/2026-04-16-1347-bollinger-mr-garch-spy-1h-PASS.md`
- `jornada/2026-04-16-1420-etf-rotation-monthly-PASS.md`
- `jornada/2026-04-16-1416-etf-rotation-top2-PASS.md` (variante NO-GO, mas
  contexto científico útil)
- Todas as 5 Phase B jornadas: `1435-cost-ablation-*`, `1458-regime-decomp-*`,
  `1507-vol-sizing-account-sensitivity-*`, `1520-mc-bootstrap-ci-*`,
  `1549-cross-asset-transport-correlation-*`.
- `jornada/2026-04-16-1600-production-readiness-summary.md` (o consolidado).

### 2.3 Winners — reports

- `reports/bollinger_mr_*/` (grids do winner 1)
- `reports/etf_rotation_*/` (grids + MC do winner 2)
- `reports/*_phase_b/` (todos os reports Phase B)

### 2.4 Winners — scripts

- `scripts/run_grid_bollinger_mr.py` (ou nome atual)
- `scripts/run_grid_etf_rotation.py`
- `scripts/run_oos_bollinger_mr.py`
- `scripts/run_oos_etf_rotation.py`
- `scripts/run_cost_ablation_*.py`
- `scripts/run_mc_bootstrap_*.py`
- `scripts/run_regime_decomp_phase_b.py`
- `scripts/run_vol_sizing_etf_rotation_phase_b.py`
- `scripts/run_account_size_sensitivity_bollinger_mr.py`
- `scripts/run_cross_asset_transport_phase_b.py`
- `scripts/run_cross_strategy_correlation_phase_b.py`
- `scripts/self_improve_loop.sh` (infra reutilizável)
- `scripts/clean_intraday_orphans.py` (defesa de cache ativa)

### 2.5 Data & cache — imutável

- `data/tiingo/**` (1660 tickers, 145 MB) — nunca remover.
- `data/tiingo/manifest.json` — fonte-de-verdade para janelas.

### 2.6 Infra & governance

- `knowledge/SKILL.md` — skill agregada, regenerar após §7 se mudar.
- `CLAUDE.md` — convenções do projeto (inclui §📌 Investment Mandate).
- `README.md` + `ROADMAP.md` — atualizados em §9.
- `docs/self_improvement/memory.md` — histórico do loop (congelar,
  não deletar).
- `jornada/README.md` — índice humano (atualizado em §5).
- Engine completo em `src/ai_trade/backtest/{data,engine,validation,metrics}/`.

### 2.7 Investment Mandate & strategy evolution references

- `docs/investment-mandate.md` — regras permanentes de capital
  allocation, CAGR targets, leverage policy, threading model.
  **Nunca deletar.**
- `portfolio-aposentadoria.md` — compartimento passive (60-80%) do
  capital. Root-level file. Referenciada pelo mandate.
- `books/raw/leverage_for_the_long_run.pdf` — fonte PDF.
- `books/extracted/leverage_for_the_long_run/` — extração (gitignored).
- `books/summaries/leverage_for_the_long_run.md` — summary absorvido
  em Task 0. Referência primária para Strategy B LETF rotation.
- `docs/reference/letf_rotation_testfol_payload.json` — config
  testfol.io que gerou os seed params (stripado de auth). Lead B1 input.
- `docs/reference/letf_rotation_reddit_analysis.md` — análise pessoal
  do usuário no Reddit /r/LETFs: top-10 ranked configs, chosen config
  stats (EMA 125 5% Lev 3x Gold 0% CAGR 17.19%), regra exata de
  rotação, críticas dos comentaristas a endereçar (block bootstrap,
  splits mutuamente exclusivos, multi-market robustness).
- `docs/reference/letf_rotation_reddit_post.pdf` — print original do
  post (24pp, 4.6MB) fornecido pelo usuário via Shift+P 2026-04-16.
- `docs/reference/testfolio_letf_spy_ema_125_response.json` — payload
  12MB da resposta testfol.io pra config chosen (1968-2026 cashflow +
  equity curve + trade stats). Usado como ground-truth pro Lead B1
  validar que a implementação bate numericamente ao testfol.io na
  mesma janela.

---

## 3. Pre-merge checklist

Antes de qualquer coisa, validar que a branch `self-improve/post-cleanup-20260416`
está mergeable e limpa:

- [x] `git status` limpo (só `reports/bollinger_mr_regime_decomp/` untracked é
  ok — mover pra dentro dos commits ou `.gitignore` em §4.1).
- [x] `.venv/bin/pytest -q` → 520 passed, 2 skipped.
- [x] `git log --oneline main..self-improve/post-cleanup-20260416` mostra
  10 commits (iter 19-27 + chore inicial).
- [x] `docs/self_improvement/memory.md` tem `status: done`, `iteration: 27`,
  `phase: B`, winners populados.
- [x] `jornada/2026-04-16-1600-production-readiness-summary.md` existe.
- [x] Nenhum commit da branch tocou `main`-only files (CLAUDE.md,
  ROADMAP.md sem necessidade) — diff review.

**Conclusion (2026-04-16):** Pre-flight all green. Validation expandida
descobriu que (a) `reports/bollinger_mr_regime_decomp/` já estava
tracked (commit 79f1378 iter 19) e (b) a contagem de commits ahead era
13 (não 10 — incluía os 3 commits pré-cleanup do mandate). Nenhum
secret real no diff (matches só em docs sobre como NÃO commitar).

---

## 3.5. Task 0 — Pre-cleanup mandate & book absorb (executada 2026-04-16)

Bloqueante para §7 (citation audit) — se `leverage_for_the_long_run`
não estiver absorvido, o audit classifica como "unused" e arquiva por
engano. Também prepara o mandate em `docs/investment-mandate.md` +
`.claude/CLAUDE.md` para que os 5 Phase 3 leads em §8 já nasçam
ancorados em regras permanentes.

- [x] 3.5.1 Extrair `books/raw/leverage_for_the_long_run.pdf` via
  `scripts/extract_pdfs.py --slug leverage_for_the_long_run`.
- [x] 3.5.2 Absorber via `Skill absorb-book leverage_for_the_long_run`
  (modelo sonnet — 13k tokens, single_pass).
- [x] 3.5.3 Validar via `/validate-summary leverage_for_the_long_run`
  (3 camadas).
- [x] 3.5.4 Atualizar `books/README.md` + `books/MAPPING.md` (34/34
  catalog).
- [x] 3.5.5 Criar `docs/investment-mandate.md` com as 7 regras
  invioláveis.
- [x] 3.5.6 Injetar §📌 Investment Mandate em `.claude/CLAUDE.md` +
  item 5 em "Leituras iniciais obrigatórias".
- [x] 3.5.7 Criar `docs/reference/letf_rotation_testfol_payload.json`
  (JSON sem Bearer token — usuário cola payload stripado manualmente
  na primeira vez que precisar pra Lead B1).
- [x] 3.5.8 Criar `docs/reference/letf_rotation_reddit_analysis.md`
  placeholder (WebFetch do Reddit falhou; usuário cola manualmente
  antes de começar Lead B1).

**Conclusion (2026-04-16):** Book absorvido BORDERLINE (J1 PASS 92% /
J2 BORDER 75%, 3 halluc de page-off menores, non-blocking). Mandate
escrito em 7 regras cobrindo capital allocation (60-80%/20-40%), CAGR
mínimo (CDI BR), Strategy A (multi-asset + sweep leverage 1:1→1:200),
Strategy B (LETF rotation via Gayed), gates invioláveis, threading
model, dynamic sizing. Todos os artefatos commitados num único
commit pré-cleanup.

---

## 4. Task 1 — Merge para main (NO squash)

Preservar a granularidade dos 10 commits — são o registro histórico do
loop autônomo.

- [x] 4.1 Commitar `reports/bollinger_mr_regime_decomp/` (se relevante
  para Phase B) ou adicionar ao `.gitignore`. Decidir caso-a-caso lendo
  o conteúdo. → **N/A:** já tracked desde iter 19 (commit 79f1378).
- [x] 4.2 `git checkout main && git pull --ff-only origin main`.
- [x] 4.3 `git merge --no-ff self-improve/post-cleanup-20260416 -m
  "merge: autonomous loop iter 19-27 — 2 production winners
  (BollingerMR SPY 1h + ETFRotation monthly top-1)"` → commit `e881076`.
- [x] 4.4 `.venv/bin/pytest -q` pós-merge → 520 passed, 2 skipped em 14.51s.
- [ ] 4.5 `git push origin main` (com autorização explícita do usuário —
  é merge em branch protegida de facto). **Pendente: aguardando autorização.**
- [x] 4.6 **Não deletar** a branch `self-improve/post-cleanup-20260416`
  ainda — é ponto-de-retorno se cleanup der errado. Branch preservada.

**Conclusion (2026-04-16):** Merge `--no-ff` aplicado preservando os 13
commits (iter 19-27 + 3 mandate). Pytest 520/2 estável pós-merge.
Branch `cleanup/post-winners-20260416` criada a partir do main mergeado
para o restante do trabalho. Push pendente de autorização explícita.

---

## 5. Task 2 — Consolidar jornadas retratadas

As ~10 entradas `⚠️ RETRACTED` ou `⚠️ DATA TAINTED` ficam como ruído no
índice. Consolidar sem perder conteúdo.

- [x] 5.1 Criar `jornada/_archive/2026-04-16-retracted-entries.md` com
  TOC linkando cada entry retratada. Cabeçalho explicativo (data-bug
  Tiingo IEX, magnitude, fix em `_filter_orphan_intraday_bars`).
- [x] 5.2 **Mover** (git mv) as 9 entries retratadas para `jornada/_archive/`.
- [x] 5.3 **Manter** `2026-04-16-1245-data-bug-winners-retracted.md` fora
  do archive — é o postmortem e documento histórico de primeira ordem.
- [x] 5.4 Atualizar `jornada/README.md`:
  - "Onde estamos hoje (2026-04-16 evening)" reescrito refletindo 2
    winners production-ready + Investment Mandate registrado + Phase 3
    leads.
  - "O que vem a seguir" reescrito como tabela dos 5 leads (A1-A3
    Path A, B1-B2 Path B), substituindo a lista antiga
    Chan/Vol-Expansion/Ehlers BP.
  - Lista "Entradas (mais recente primeiro)" enxugada (12 entries top-
    level + pointer para archive).
  - Bloco "⚠️ Avisos de retratação" removido (substituído pelo pointer).
  - Glossário ampliado: Path A/B, SHORT-HOLD CFD, SWING BROKER, LETF
    rotation, Investment Mandate, CDI BR.

**Conclusion (2026-04-16):** 9 entries movidas via `git mv` (rename
preservada no histórico). Archive index escrito com TOC + magnitude do
bug + lições preservadas (`_filter_orphan_intraday_bars`,
`scripts/clean_intraday_orphans.py`, sniff-test convention). README
top-level enxugado de 31 entries para 12 entries + pointer; seções
"Onde estamos hoje" e "O que vem a seguir" reescritas pra refletir
estado pós-loop. Glossário cresceu 6 termos novos.

---

## 6. Task 3 — Apagar strategies descartadas

Strategies que não viraram winner **nem** são cobertas pelos 2 winners:

### 6.1 Inventário a remover

- [ ] 6.1.1 Listar `src/ai_trade/backtest/strategies/*.py` e identificar:
  - **KEEP:** `base.py`, `bollinger_mr.py`, `etf_rotation.py` + helpers
    compartilhados.
  - **DELETE:** `clenow_momentum.py`, `ehlers_bp_swing.py` (se existir),
    `kalman_pairs.py` (se existir), `chan_pairs.py` (se existir),
    `vol_expansion_breakout.py` (se existir). Confirmar cada um via `git ls-files`.
- [ ] 6.1.2 Deletar **tests correspondentes** em `tests/` (grep pelos
  nomes de classe; remover os arquivos inteiros quando testam só strategy
  removida).
- [ ] 6.1.3 Deletar **scripts one-shot** dessas strategies em `scripts/`:
  `run_clenow_replication.py`, `run_ehlers_*.py`, `run_chan_*.py`, etc.
  — NÃO remover qualquer script listado em §2.4.

### 6.2 Validação

- [ ] 6.2.1 `.venv/bin/pytest -q` pós-remoção → deve cair para ~X passed
  (subtrair testes deletados). Baseline novo documentado aqui.
- [ ] 6.2.2 `grep -rn "ClenowMomentum\|EhlersBPSwing\|KalmanPairs\|ChanPairs\|VolExpansion" src/ tests/ scripts/`
  → zero hits. Se houver, é import residual.
- [ ] 6.2.3 Rodar os grids dos 2 winners novamente em modo smoke (1
  config cada) pra garantir que não quebrei imports implícitos.

**Conclusion:**

---

## 7. Task 4 — Audit de citações de livros

Dos **34** books em `books/summaries/` (33 originais + leverage_for_the_long_run
absorvido em Task 0), listar quais foram de fato citados no
código/jornadas dos winners + no `docs/investment-mandate.md`.

- [ ] 7.1 Rodar grep agregado em tudo que sobrou após §5 e §6:
  ```
  grep -rhoE '\[[a-z_]+(,\s*(p|ch)\.[0-9-]+)?\]' \
    src/ tests/ scripts/ jornada/ knowledge/ ROADMAP.md CLAUDE.md \
    docs/investment-mandate.md \
    | grep -oE '\[[a-z_]+' | sort -u
  ```
- [ ] 7.2 Cruzar com `books/MAPPING.md` (slug ↔ título). Produzir uma
  tabela `used` vs `unused` e inserir em `books/CITATION_AUDIT.md`
  (novo arquivo).
- [ ] 7.3 **Força inclusão obrigatória (não arquivar mesmo se unused):**
  - `leverage_for_the_long_run` — referenciado pelo mandate §4 (LETF rotation).
  - `math_money_mgmt` — referenciado pelo mandate §3.3 (Kelly f/2).
  - `leverage_space` — referenciado pelo mandate §3.3 (ruin/drawdown).
  - `advances_fin_ml` — framework de gates (PBO/DSR/CPCV) em mandate §2.
- [ ] 7.4 Para slugs **unused** fora da lista §7.3 (provavelmente ~15-18
  dos 34):
  - Mover `books/summaries/<slug>.md` → `books/summaries/_archive/`.
  - Atualizar `books/MAPPING.md` marcando `[archived]` na linha.
  - **NÃO** remover `books/raw/<slug>.pdf` nem `books/extracted/<slug>/`.
- [ ] 7.5 Regenerar `knowledge/SKILL.md` a partir apenas dos summaries
  mantidos (usar a skill `absorb-all-books` ou um script agregador — não
  reescrever manualmente).
- [ ] 7.6 Atualizar `knowledge/SKILL.md` header com "Regenerado
  2026-04-16 após cleanup: N slugs citados nos winners de Fase 2.5
  + 4 slugs protegidos pelo Investment Mandate".

**Conclusion (preencher com):** N slugs usados / 34 total. Lista exata
em `books/CITATION_AUDIT.md`.

---

## 8. Task 5 — Registrar 5 Phase 3 leads (derivados do Investment Mandate)

Os leads abaixo derivam diretamente do `docs/investment-mandate.md` e
substituem a lista genérica "leverage sweep" original. Cada lead
corresponde a 1 iteração do self-improve loop (SCOPE=code,
ITER_TIMEOUT=1800s). Budget total estimado: ~5 iters.

Esta task **apenas registra** os leads em `ROADMAP.md` e
`docs/self_improvement/memory.md`. **NÃO executa.** Execução é em branch
separada (`phase3/letf-and-multi-asset-<date>`), após o cleanup merged.

### Leads

| # | Path | Título | Pré-requisitos | Cita |
|---|------|--------|----------------|------|
| A1 | A | **BollingerMR leverage sweep SPY 1h** — risk_pct ∈ {0.95, 2.0, 5.0, 10.0, 20.0} simulando margin-call bar-a-bar; Kelly f/2 cross-check; prob-of-ruin MC 10k paths. | nenhum | `[math_money_mgmt, Vince]`, `[leverage_space, Vince]`, `[leverage_for_the_long_run, p.7]` |
| A2 | A | **Multi-asset universe screener** SPY+QQQ+GLD+BTC+ETH+FX majors: implementar `ai_trade/screener/` com Hurst/ATR/spread/volume; pre-screener roda antes do backtest e filtra ativos "propícios" para BollingerMR. | A1 opcional | `[machine_trading, Chan]`, `[volatility_trading, Sinclair]` |
| A3 | A | **Per-asset BollingerMR + threading-ready code** — refactor do runner pra state-isolated per-ticker; perks opcionais (FX session filter, equity pre/post-market, crypto 24/7, gold news filter); output multi-asset portfolio metrics + correlation. | A2 | `[advances_fin_ml, ch.7/11]` (CPCV multi-asset) |
| B1 | B | **LETF rotation — design a partir do zero (base Gayed)** — Objetivo: encontrar UMA config simples da família LETF rotation que passe rigorosamente os gates. Grid 360 configs (EMA/SMA × {100,125,150,200} × band {0,3%,5%} × lev {1x,2x,3x} × gold {0,25,50,75,100%}). Priorizar Gayed canonical (SMA 200, band 0%, Gold 0%) como base científica; params do Reddit (EMA 125, band 5%) são 1 seed entre outros, NÃO gospel a validar. Splits mutuamente exclusivos IS 1970-2000 / OOS 2001-2015 / Stress 2016-2026. Stationary block bootstrap a 0.001. UPRO/SSO sintéticos pre-2009/2006. 15% IR BR por switch. Winner pode ser Gayed canonical, pode ser Reddit-like, ou outra combinação — decidido pelos gates, não por afinidade. | Task 0 (book) + `docs/reference/letf_rotation_reddit_analysis.md` (contexto ilustrativo) | `[leverage_for_the_long_run, p.13, p.17, p.21]` |
| B2 | B | **LETF rotation vs. ETFRotation benchmark** — correlação dos sinais, blend risk-parity, MAR ratio comparison; decidir se ambos coexistem na carteira ou se LETF substitui ETFRotation como winner Path B. | B1 | `[advances_fin_ml, p.196-202]` (PSR), `[stocks_on_the_move, p.81]` |

### Subtasks

- [ ] 8.1 Atualizar `ROADMAP.md` §"Post-cleanup evolution (Phase 3)"
  com a tabela acima + link pra `docs/investment-mandate.md`.
- [ ] 8.2 Adicionar `## Phase 3 leads` em `docs/self_improvement/memory.md`
  com os 5 leads acima (formato: 1 linha cada, `# Lead A1: ...` etc.).
  **NÃO** mudar `status` — permanece `done` até execução começar.
- [ ] 8.3 Quando executar (fora deste spec de cleanup):
  - Criar branch `phase3/letf-and-multi-asset-<date>`.
  - Resetar `status: in_progress` e `iteration: 28` no memory.md.
  - Rodar `scripts/self_improve_loop.sh` com SCOPE=code.

**Conclusion:**

---

## 9. Task 6 — Atualizar docs raiz

- [ ] 9.1 `ROADMAP.md` §"Current status":
  - Remover narrativa de iters retratadas.
  - Adicionar bloco "**2026-04-16 evening:** 2 production winners
    encontrados via loop autônomo 2-fase" + links pros jornada PASS.
  - Atualizar contagem de testes.
- [ ] 9.2 `README.md`:
  - Atualizar "Como rodar um backtest" com exemplos dos 2 winners
    (removendo o exemplo de Clenow, se presente).
  - Atualizar contagem de testes / tickers / histórico.
- [ ] 9.3 `jornada/README.md`:
  - Seção "Onde estamos hoje" reflete estado pós-cleanup.
  - Glossário: adicionar "Path A / Path B", "SHORT-HOLD CFD",
    "SWING BROKER" se ainda não estão.

**Conclusion:**

---

## 10. Task 7 — Tests & final validation

- [ ] 10.1 `.venv/bin/pytest -q` → verde, contagem nova documentada.
- [ ] 10.2 Smoke-run de cada winner (1 config cada, latest available
  window por manifest):
  - `scripts/run_grid_bollinger_mr.py --symbol SPY --frequency 1hour --smoke`
  - `scripts/run_grid_etf_rotation.py --smoke`
- [ ] 10.3 `git log --stat` da branch de cleanup — revisar que nenhum
  arquivo do §2 (Preservation) foi tocado.
- [ ] 10.4 Commit final na branch `cleanup/post-winners-20260416`:
  ```
  chore(cleanup): post-winners repo slim — remove N retired strategies,
  archive N retracted jornadas, audit N/33 books cited
  ```
- [ ] 10.5 Abrir PR para `main`. Título: "Post-winners cleanup".
  Descrição linkando este spec + contagens antes/depois (LOC, files,
  tests, slugs citados).

**Conclusion:**

---

## 11. Acceptance criteria

Cleanup está concluído quando **todos** abaixo forem verdade:

1. `pytest -q` verde com contagem nova documentada.
2. Smoke-run dos 2 winners reproduz Sharpe IS dentro de ±0.05 do
   registrado em `2026-04-16-1600-production-readiness-summary.md`.
3. `git log` main mostra merge `self-improve/post-cleanup-20260416` +
   commit de cleanup — histórico navegável.
4. `jornada/README.md` não lista entries retratadas no top-level
   (só em `_archive/`).
5. `books/CITATION_AUDIT.md` existe e lista N slugs usados.
6. `ROADMAP.md` tem lead "BollingerMR leverage sweep" em Phase 3.
7. Todos os arquivos listados em §2 ainda existem e são git-trackeados.
8. **Zero informação perdida:** qualquer fato técnico dos 2 winners
   (parâmetros, gates, citações, CIs, verdicts) continua reconstruível
   lendo o que sobrou em `jornada/`, `src/`, `reports/`, `docs/`.

---

## 12. Rollback plan

Se algo quebrar em qualquer task acima:

- Branch `self-improve/post-cleanup-20260416` permanece intocada (§4.6).
- Todos os `git mv` são reversíveis com `git log --diff-filter=R`.
- Summaries e jornadas arquivados (`_archive/`) continuam no repo —
  re-promovê-los é só `git mv` de volta.
- `books/raw/` e `data/tiingo/` jamais foram tocados.

Se passar por acceptance (§11), tag release: `git tag v0.1-phase-2.5-winners`.
