# Spec — Fase 2: Módulo de Backtest

Plano executável do módulo de backtest do ai-trade. Cada task tem checkbox e
campo **Conclusão** que deve ser preenchido antes do commit correspondente.
Este arquivo sobrevive entre sessões — ao abrir o Claude Code, a primeira
coisa a ler é este arquivo + `ROADMAP.md`.

---

## 📖 Como usar este arquivo

1. **Ao iniciar uma sessão**, leia este arquivo inteiro + `ROADMAP.md` §"Backtest em duas etapas".
2. Encontre a próxima task com `[ ]`.
3. Implemente conforme a seção "O que fazer" e os critérios de aceitação.
4. **ANTES DE COMMITAR**, edite este arquivo:
   - Troque `[ ]` por `[x]` na task.
   - Preencha o campo **Conclusão** da task (2-4 linhas) com:
     - O que foi feito (resumo, não copiar descrição)
     - Arquivos criados/modificados (caminhos)
     - Contagem de testes (`N passed` no pytest)
     - Achados/surpresas/decisões não-óbvias (se houver)
5. **Inclua essa edição no mesmo commit** da implementação.
6. Quando **todas** as tasks estiverem `[x]`, o commit final atualiza o
   `ROADMAP.md` marcando Fase 2 ✅ Concluída.

**Não fazer:**
- Nunca remover ou reescrever tasks concluídas — histórico faz parte do valor.
- Nunca pular o campo **Conclusão** — ele é o contrato de resumabilidade.
- Nunca iniciar uma task nova sem marcar a anterior como `[x]` no mesmo commit.

**Exemplo de campo Conclusão preenchido:**
> Portfolio tracking + P&L accounting implementados em `engine/portfolio.py`
> com 12 testes (`12 passed`). Decisão: armazenar posições em `dict[symbol, Position]`
> em vez de DataFrame — acesso O(1) e evita reindexing. Unrealized P&L usa o
> último mark conhecido (campo `mark_price` atualizado via `update_mark()`).

---

## 🎯 Contexto rápido (para sessão nova)

- **Fase 0 / 0.5 concluídas.** 33 livros absorvidos, `knowledge/SKILL.md` gerada, rodando.
- **Fase 1 parcialmente scaffolded.** docker-compose (postgres+grafana) OK;
  cliente cTrader bloqueado aguardando aprovação Spotware do app OAuth.
- **Fase 2 (este spec) arrancou** com data layer pronto (commit `517c221`).
- **Princípios não-negociáveis** (de `knowledge/SKILL.md`):
  - Toda regra/parâmetro/gate cita `[livro.slug, p.X]`.
  - Survivorship bias explícito em cada report até migrar pra fonte paga.
  - CPCV/PBO/DSR são **gates obrigatórios**, não "nice to have" (rules #3-5).
- **Etapa 1 só** — dados via `yfinance` + Wikipedia scrape, sem cTrader.
- **Primeiro alvo de replicação:** Clenow `stocks_on_the_move` (2 parâmetros, bem especificado).

---

## ✅ Pré-requisitos concluídos

- [x] **Data layer — yfinance + Wikipedia SPX** (commit `517c221`, 2026-04-14)

  **Conclusão:** Criados `src/ai_trade/backtest/data/yfinance_source.py`
  (OHLCV daily com cache parquet + `_normalize` que achata MultiIndex/strip-tz)
  e `wikipedia_spx.py` (scrape das 2 tabelas SPX + `constituents_on(date)` por
  algoritmo undo-changes-walking-backwards). 15 testes novos (`33 passed`
  total). Conflito detectado em `ctrader-open-api 0.9.2` que hard-pina
  `protobuf==3.20.1` + `Twisted==21.7.0` — movido para
  `[project.optional-dependencies.ctrader]` para não contaminar o stack.

---

## 🔨 Tasks pendentes

### Task 1 — Engine core: portfolio + execução + runner

**O que fazer:**

- [x] **Portfolio** — `src/ai_trade/backtest/engine/portfolio.py`
  - Rastreia posições (long/short, volume, `avg_entry_price`, `mark_price`).
  - P&L realizado e unrealizado por símbolo e total.
  - Eventos: `open_position`, `close_position`, `update_mark`, `apply_cash_flow`.
  - Equity curve como `pd.Series` indexada por timestamp.
  - Operar em moeda base (USD por simplicidade agora; CFD multi-moeda vira
    depois que cTrader destravar).

- [x] **Execution simulator** — `src/ai_trade/backtest/engine/execution.py`
  - CFD-aware: aplica spread bid/ask (fill = quote ± spread/2) + slippage.
  - Swap/overnight: `SwapModel` debita pct/dia por posição aberta no rollover.
  - Interface: `simulate_fill(order, bar) → Fill | None`.
  - Config via `ExecutionConfig(spread_pips, slippage_pips, commission_per_lot)`.

- [x] **Runner** — `src/ai_trade/backtest/engine/runner.py`
  - Bar-by-bar event loop.
  - Protocolo `Strategy`: `on_bar(bar, portfolio, context) → list[Order]`.
  - Orquestra: para cada timestamp, feed bars → strategy → orders →
    execution → portfolio update → mark update.
  - Emite `BacktestResult` (equity curve, trades, fills, orders rejeitados).

- [x] **Testes** — `tests/test_backtest_engine.py`
  - Portfolio: open/close trade em cenário sintético, verifica P&L.
  - Execution: fill com spread conhecido → verifica custo embutido.
  - Runner: strategy "buy-and-hold" → equity curve bate com return bruto − custos.

**Aceito quando:** toda a suite passa; engine roda um cenário sintético
(e.g., compra 100 AAPL em 2020-01-02, marca por 10 dias, fecha) end-to-end
sem erros e com números verificáveis a mão.

**Conclusão:** Engine core completo em `src/ai_trade/backtest/engine/`
(`portfolio.py`, `execution.py`, `runner.py`, `__init__.py`) com 29 testes novos
em `tests/test_backtest_engine.py` (`62 passed` total). Desenvolvido em TDD
estrito: testes falharam por `ModuleNotFoundError` antes de cada implementação.

Decisões não-óbvias:
- **Equity formula correta:** durante TDD a fórmula ingênua `cash + Σ unrealized_pnl`
  revelou-se errada (ignora o cost basis de posições abertas); corrigida para
  `cash + Σ signed_market_value` onde signed_market_value = ±volume×mark
  (+long, −short). Dois testes do Portfolio tiveram expectativas ajustadas.
- **Spread em unidades de preço absoluto, não pips:** `ExecutionConfig.half_spread`/
  `slippage` como preço direto (caller converte pips/bps), mantém o engine
  agnóstico a símbolo — AAPL $0.005 e EURUSD 0.0001 usam a mesma interface.
- **Mark-to-close em duas passadas:** Runner marca antes e depois da strategy
  (antes: equity fresca pra sizing; depois: remove o prêmio de spread do
  mark de posições recém-abertas, reflete o custo imediato no equity).
- **Order dispatch mínimo:** buy vira open_long OU close_short; sell vira
  close_long OU open_short. Long-only (Clenow) exercita metade dos caminhos;
  shorts têm cobertura via testes unitários do Portfolio.
- **Equity = 10_200 verificável a mão:** buy 10 @ 100, mark→120, cash 9_000 +
  position 1_200 = 10_200 ✓ (test_buy_and_hold_no_costs_equity_matches_position_value).

---

### Task 2 — Validação anti-overfit: CPCV + PBO + DSR + walk-forward + permutation

**O que fazer:**

- [x] **CPCV** — `src/ai_trade/backtest/validation/cpcv.py`
  - Algoritmo de `[advances_fin_ml, ch.7, p.104-117]`: gera C(K, N_test) combinações.
  - `purge(labels, train_idx, test_idx, embargo_pct)` remove overlap.
  - Retorna `Iterator[tuple[train_idx, test_idx]]` — compatível com sklearn API.

- [x] **PBO** — `src/ai_trade/backtest/validation/pbo.py`
  - CSCV (Combinatorially Symmetric Cross-Validation) de
    `[advances_fin_ml, ch.11, p.208-211]`.
  - Input: matriz de retornos (T × N_strategies).
  - Output: `pbo: float` ∈ [0, 1].
  - **Gate**: `pbo > 0.5 → reject` (rule #3).
  - Cross-check contra `books/code/masters-testing-tuning/CSCV_MKT/CSCV.CPP`.

- [x] **DSR** — `src/ai_trade/backtest/validation/dsr.py`
  - Deflated Sharpe de `[advances_fin_ml, ch.14, p.261-270]`.
  - Input: SR observado, N tentativas, skew, kurt, sample size, variância cross-sec dos SRs.
  - Output: `(dsr_value, p_value)`.
  - **Gate**: reportar sempre que N > 1 (rule #4).

- [x] **Walk-forward** — `src/ai_trade/backtest/validation/walk_forward.py`
  - Splits deslizantes com reotimização (`[eval_opt_strategies]` +
    `[testing_tuning]`).
  - Config: tamanho in-sample, tamanho out-of-sample, step.
  - Retorna `list[tuple[train_range, test_range]]`.
  - **Gate**: ≥8 janelas, ≥6 lucrativas, DD ≤ 25% em todas (rule #5).

- [x] **Permutation tests** — `src/ai_trade/backtest/validation/permutation.py`
  - Monte Carlo Permutation Test de `[stat_sound_indicators]`.
  - Cross-check contra `books/code/masters-testing-tuning/MCPT_BARS/` e
    `MCPT_TRN/`.
  - p-value: frac. de permutações com Sharpe ≥ observado.

- [x] **Testes com verificação numérica** — `tests/test_validation.py`
  - Exemplos toy do AFML (capítulos citados) onde o número esperado é conhecido.
  - Fixtures de matriz de retornos controlada.
  - Testar gates: matrix com overfit evidente → PBO > 0.5; SR inflado →
    DSR p-value alto.

**Aceito quando:** 5 módulos implementados, verificados numericamente
contra pelo menos 1 exemplo canônico da fonte, testes passam, gates documentados.

**Conclusão:** Framework anti-overfit completo em
`src/ai_trade/backtest/validation/` (`cpcv.py`, `pbo.py`, `dsr.py`,
`walk_forward.py`, `permutation.py`, `__init__.py`) com 52 testes novos em
`tests/test_validation.py` (`114 passed` total). Adicionado `scipy>=1.11` em
`pyproject.toml` para `norm.cdf/ppf` via `scipy.special.ndtr/ndtri`. TDD
estrito: cada módulo teve seus testes criados + verificados RED antes da
implementação.

Decisões não-óbvias:
- **Purge usa contrato `pd.Series[t0→t1]`:** index = t0, values = t1. Para
  labels sem overlap basta `pd.Series(idx, index=idx)`; para triple-barrier
  com overlap o caller passa a t1-series do `getEvents` (AFML p.50). Purge
  mantém train obs *i* se `t1_i < test_t0_min` ou `t0_i > test_t1_max`.
- **Embargo em posições, não tempo:** `h = int(embargo_pct · len(times))`,
  replicando a fórmula de `getEmbargoTimes` em AFML p.151 — mais estável do
  que embargo-por-duração quando o sampling é irregular.
- **CPCV: purge/embargo por bloco, não pela união:** combinações tipo (0, 5)
  têm dois blocos disjuntos → cada um gera seu próprio purge+embargo. Isso
  replica a impl de referência do mlfinlab, evita sub-purga de treino.
- **CSCV: PBO para matriz iid SINGLE trial é ruidoso.** Com N=50, T=500, 8
  blocos, std(PBO) ≈ 0.19 entre seeds (constatado empiricamente). Teste de
  null-case agora usa média de 20 matrizes independentes. Decisão pragmática
  para ter teste determinístico sem perder significância estatística.
- **PBO caso "espelho" dá PBO≈0.91, não 1.0:** Com
  `returns[T/2:] = -returns[:T/2]` e 8 blocos, 6 das 70 partições são uniões
  de pares-espelho (IS mean = 0 para todos) → não contribuem. 64/70 = 0.914,
  verificado a mão. Teste usa `>= 0.90`.
- **E[SR_max] tem ESCALA, não só valor:** formula AFML p.222-223 retorna
  Z-score units (Var(SR)=1). Para comparar com `sharpe_periodic` do PSR, é
  preciso multiplicar por `√V = 1/√(T-1)` sob iid-null. Sem essa escala, DSR
  rejeita todo Sharpe >0 para N>5. `expected_max_sharpe(n, var_sharpe=…)`
  carrega o parâmetro explicitamente; `dsr()` default aplica `1/(T-1)`.
- **Gumbel √(2 ln N) é assintótica DO LIMITE SUPERIOR, não da média.**
  Substituído teste original (tolerância ±15% contra √(2 ln N)) por
  verificação Monte Carlo direta: formula casa com mean(max(N_normals))
  dentro de ±5% para N ∈ {5, 10, 100, 1000}.
- **MCPT usa Masters `prepare_permute`/`do_permute`:** shuffle das `n-1`
  changes preservando prices[0] e prices[-1] (invariante), re-ancorando
  prices[-1] após o cumsum para apagar drift floating-point. Teste AR(1) com
  φ=0.5 confirma que a permutação destrói a auto-correlação como esperado.

---

### Task 3 — Métricas + gerador de relatório

**O que fazer:**

- [x] **Performance metrics** — `src/ai_trade/backtest/metrics/performance.py`
  - Funções puras: `sharpe`, `sortino`, `calmar`, `cagr`, `max_drawdown`, `volatility`, `var`.
  - Input: `pd.Series` de retornos ou equity curve.
  - Anualização por fator configurável (252 daily, 52 weekly, etc.).

- [x] **Report generator** — `src/ai_trade/backtest/metrics/report.py`
  - Recebe `BacktestResult` + saídas de validação.
  - Emite markdown em `reports/<strategy>_<YYYYMMDD-HHMM>.md` com seções:
    - Header + data run
    - **Survivorship bias disclaimer** se fonte for yfinance/wikipedia (obrigatório)
    - Performance summary (todas as métricas)
    - **CPCV** distribution: mean/std/min Sharpe em todos os caminhos + histogram
    - **PBO** + veredicto (pass/reject)
    - **DSR** + p-value + veredicto
    - Walk-forward summary (N janelas, N lucrativas, max DD)
    - Equity curve + drawdown chart (matplotlib PNG em `reports/assets/`)
    - Lista de trades (top 10 winners / losers)

**Aceito quando:** um `BacktestResult` sintético gera um report markdown válido,
com todas as seções, sem crashs, PNG gerado, survivorship disclaimer presente.

**Conclusão:** Métricas + report generator em
`src/ai_trade/backtest/metrics/` (`performance.py`, `report.py`, `__init__.py`)
com 30 testes novos em `tests/test_metrics.py` (`144 passed` total). TDD
estrito — cada módulo teve tests criados e verificados RED (ModuleNotFoundError)
antes da implementação. Adicionado `matplotlib>=3.8` em `pyproject.toml` para
os charts PNG do report.

Decisões não-óbvias:
- **Disclaimer de survivorship é obrigatório por contrato, não opcional.**
  `_needs_disclaimer(source)` inclui `yfinance`, `wikipedia`, `yahoo` como
  *biased* e **qualquer outra fonte** que não contenha marcador explícito de
  survivorship-free. Regra replica o inviolable rule do ROADMAP (*nunca
  esconder o bias do relatório*). O texto do disclaimer inclui "bias",
  "overstated", e cita ROADMAP §"Decisões adiadas" para rastreabilidade.
- **Sortino com downside-dev populacional (denominador = todas as observações),
  não só as downside.** Fórmula Estrada: `√(mean(min(r−target, 0)²))`. Quando
  não há retorno abaixo do target, retorna `+inf` em vez de raise — report
  surface precisa imprimir algo sempre. Teste específico verifica.
- **`_dataframe_to_markdown` inline** em vez de `pd.DataFrame.to_markdown()` —
  este último requer `tabulate` como dep opcional. Escrever ~10 linhas de GFM
  writer evita adicionar dependency só pra formatar tabela de trades.
- **Duas passadas de `max_drawdown`: positive magnitude sempre.** Fórmula
  `(peak − equity) / peak` garante que DD=0 quando monotone e DD=0.5 quando
  preço cai metade. Calmar recebe esse valor cru (não `abs()`), e divide
  CAGR por ele — sem risco de divisão por negativo.
- **VaR com `alpha=0.05` retorna positive magnitude floor at 0.** Se a 5%
  quantile dos retornos for positiva (estratégia que não perde), VaR = 0 por
  convenção — evita reportar "gain of 1.7%" como VaR negativo, que confunde.
- **Chart PNG em 2 painéis (equity + underwater DD)**, `matplotlib.use("Agg")`
  para backend headless (VPS). Dimensões 1200×720 RGBA, ~70KB por chart.
  Pillow-free (PNG direto do Agg backend).

---

### Task 4 — Strategy: Clenow momentum replication

**O que fazer:**

- [ ] **Strategy base** — `src/ai_trade/backtest/strategies/base.py`
  - Protocol/ABC: `Strategy.on_bar(bar, portfolio, context) → list[Order]`.
  - Callback opcional: `on_rebalance(date, portfolio, context)`.
  - Context carrega universo ativo, parâmetros, logger.

- [ ] **Clenow momentum** — `src/ai_trade/backtest/strategies/clenow_momentum.py`

  Regras verbatim do `stocks_on_the_move` (citações obrigatórias no docstring):

  - Rank por **90-day exponential regression slope × R²** `[p.70-72, p.77, p.98]`
  - Universe: SPX 500 point-in-time via `wikipedia_spx.constituents_on(date)`
  - Regime filter: só compra se SPX > 200d MA `[p.66-67, p.98-99]`
  - Top 20% cutoff (rank ≤ 100 em SPX) `[p.95, p.110]`
  - ATR position sizing `[p.82]`
  - Rebalance semanal (quarta-feira) `[p.99, p.110]`
  - NUNCA ranquear por "% above 200d MA" sozinho `[p.68]`

- [ ] **Script CLI** — `scripts/run_clenow_replication.py`
  - Args: `--start`, `--end`, `--cash`, `--output-dir`
  - Carrega data via `YFinanceSource` + `WikipediaSPX`
  - Roda backtest via `engine.Runner`
  - Valida via `cpcv`, `pbo`, `dsr`, `walk_forward`
  - Gera report via `metrics.report`

- [ ] **Integration test** — `tests/test_clenow_integration.py`
  - Range curto (ex.: 2020-01-01 a 2021-12-31) pra teste rápido
  - Roda end-to-end em dados cached (fixtures no repo, sem network)
  - Verifica: equity curve não-vazia, métricas finitas, report gerado

- [ ] **Documento de replicação** — `reports/clenow_replication_notes.md`
  - Números obtidos vs números do livro (Clenow reporta ~CAGR 12% / Sharpe ~1.0
    na versão estendida do sistema) — esperamos **inflação** pelo
    survivorship residual.
  - Se direcionalmente compatível (ex.: Sharpe > 0.5, CAGR positivo), engine OK.
  - Se drasticamente diferente (ex.: Sharpe negativo, CAGR < 0), bug —
    investigar antes de avançar.

**Aceito quando:** script roda sem erros, report gerado, integration test
passa, números sanos, doc de replicação escrito.

**Conclusão:** _(preencher ao finalizar)_

---

### Task 5 — Fechamento da Fase 2

**O que fazer:**

- [ ] **ROADMAP.md** — marcar Fase 2 ✅ Concluída na tabela de status.
- [ ] **README.md** raiz — adicionar seção "Como rodar um backtest" com
      exemplo do `run_clenow_replication.py`.
- [ ] **knowledge/SKILL.md** — se descobrirmos regra ou pegadinha durante o
      trabalho que fortaleceria a skill, registrar (via re-absorção do livro
      relevante ou atualização manual justificada).
- [ ] **Reavaliar** (em seção nova aqui no spec ou em `specs/backtest_phase3.md`):
      as 3 decisões adiadas do ROADMAP §"Decisões adiadas" — dados pagos?
      vectorbt? próxima estratégia? — agora informadas pelos achados do Clenow.

**Aceito quando:** docs atualizadas, estado do projeto reflete Fase 2 concluída,
Fase 3 (backtest rigoroso / validation em produção) começa com decisões novas
tomadas.

**Conclusão:** _(preencher ao finalizar)_

---

## 📌 Referências

- `ROADMAP.md` — estado das fases + decisões adiadas + modelo 2-etapas
- `README.md` — conceitos CPCV/PBO/DSR + universo Clenow + survivorship
- `knowledge/SKILL.md` — inviolable rules #1-7
- `knowledge/books/advances_fin_ml.md` — fonte primária CPCV/PBO/DSR
- `knowledge/books/stocks_on_the_move.md` — fonte primária Clenow
- `books/code/masters-testing-tuning/` — C++ de referência (MCPT, CSCV)
