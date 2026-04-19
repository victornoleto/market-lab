# Spec — Phase 3.5a-V2 (Plano A — LAST ATTEMPT with corrected framework)

**Data:** 2026-04-18
**Branch de trabalho:** `phase3.5a-v2/plano-a-last-attempt-20260418`
  (criar a partir de `phase3.5a/plano-a-short-hold-20260418`)
**Execução:** `scripts/self_improve_loop.sh` com `SWEEP_MODE=fanout`,
  `CLAUDE_MODEL=claude-opus-4-7`, `MAX_ITER=80`, `ITER_TIMEOUT=1800s`,
  `SCOPE=code`.
**ETA:** ~6-8 horas autônomas.

---

## 0. Por que V2 existe (contexto crítico)

### 0.1 V1 não foi V2 — foi o "V1 clássico"

Phase 3.5a V1 (executada 2026-04-18, 42 iters, 143 runs) testou
**exatamente o framework que tínhamos diagnosticado como falho**: 1h FX
retail + universe pequeno + hold curto + custos focados em swap. O
agente autônomo concluiu "abandon Plano A" e escreveu T6/T7 tratando
3.5a como se fosse a "V2". **Isso foi erro de framing** — a V2 nunca
rodou. Este spec é a V2 real, corrigida pela conversa usuário↔assistant
pós-V1.

### 0.2 V2 é a última tentativa — contrato binding

Memória do usuário (`project_plano_a_v2_last_attempt.md`, 2026-04-18):

> *"Phase 3.5a-V2 is the LAST attempt to find a valid Plano A strategy.
> If V2 also produces 0 PASS after ~80 iters: abandon Plano A entirely,
> focus exclusively on refining Plano B. No V3. Mandate rewrite."*

Este spec implementa esse contrato. Se V2 acabar com 0 PASS, T7 escreve
a jornada de abandono formal e o mandate §7 registra o pivot. **Não há
V3**, mesmo que o agente identifique "uma família a mais para testar".

### 0.3 O que V2 corrige

| Dimensão | V1 (que rodou e falhou) | **V2 (este spec)** |
|----------|--------------------------|---------------------|
| Timeframe | 1h fixo | **Livre** — daily, 4h, weekly, multi-day |
| Hold | ≤ 5 dias (para "evitar swap") | **≥ 3 dias** — cost economics invertidas |
| Universe | 12 FX + 2 metais (1h only) | **≥ 30 multi-asset CFDs** (equity/sector/commodity/FX/crypto/FI) |
| Data source | Tiingo IEX 1h (gaps, janela curta) | **Tiingo daily** (Tudo disponível, longest window) |
| Cost focus | Swap-dominant (errado) | **Spread+commission dominant** (corrigido) |
| CAGR target | 60-120%/yr (fantasia) | **30-45%/yr** (realista) |
| Families | MR, Donchian, pairs-FX, session, regime | **TSMOM multi-asset, Gayed transport, AFML meta-label, Carver risk-parity, equity pairs, vol breakout** |
| Hierarquia mandate §1 (A > B) | Mantida (e empiricamente falhou) | Mantida (mas com target realista: CAGR ≥ 30% vs B 25.56%) |

---

## 1. Mandate revision (V2-específico — não altera mandate global)

As regras §1-§6 do `docs/investment-mandate.md` continuam autoritativas.
V2 apenas **relaxa constraints operacionais** em 3 pontos, documentados
via §7 override antes do launch:

1. **Hold:** mandate §3 "median hold ≤ 5 days" é **sobrescrito** para
   "median hold ≥ 3 days" em V2. Razão: cost economics (§3 deste spec).
   Carver `[systematic_trading, p.185-188]` **cita o opposite do que
   achávamos**: o hold ≤ 5d era recomendação *contra swap acumulando*,
   mas para retail com spread+commission dominantes, hold ≥ 1-4 semanas
   é o ótimo. Correção necessária.
2. **Timeframe:** mandate §3 implícito "intraday multi-asset" é
   **relaxado** para "qualquer timeframe daily-or-slower que passe os
   gates". Não é mandatório intraday — é mandatório que funcione.
3. **CAGR target:** mandate §2 "5-10%/mês (60-120%/yr)" é **realista-mente
   reescrito** para "CAGR líquido OOS ≥ 30%/yr" para V2. Acima de
   Plano B (25.56%) + margem material, abaixo do pico Medallion Fund
   (39% institucional). Justificativa: retail cap estrutural
   `[systematic_trading, p.~105-130]`.

**Gates continuam inflexíveis:**
- PBO < 0.5 `[advances_fin_ml, p.208-211]`
- DSR p-value < 0.05 `[advances_fin_ml, ch.14]`
- Walk-forward ≥ 6/8 windows profitable `[advances_fin_ml, ch.11]`
- Single-block OOS Sharpe > 0
- Forward-window stress Sharpe > 0
- Bootstrap 99.9% CI low > 0

**Winner criteria (acumulativo — todos precisam):**
| Critério | Threshold | Rationale |
|----------|-----------|-----------|
| PBO | < 0.5 | AFML |
| DSR p-value | < 0.05 | AFML |
| WF windows | ≥ 6/8 | AFML |
| Bootstrap 99.9% CI low | > 0 | conservative |
| **CAGR OOS net** | **≥ 30%** | hierarquia mandate §1 (A > B=25.56%) + ≥ 4pp margem |
| **Sharpe OOS net** | **≥ 2.0** | matchar Plano B baseline |
| **MaxDD OOS** | **≤ 25%** | 2× Plano B (10.86%) é aceitável para bucket alavancado |
| **Median hold** | **≥ 3 days** | cost economics |
| **Benchmark IR vs SPY** | ≥ 0.5 | SPY é base universal |

---

## 2. Universo V2 (≥ 30 instrumentos daily Tiingo)

Universe pré-validado em Tiingo cache `data/tiingo/` (verificado
2026-04-18 — 28 ETF/crypto hits + 12 FX daily pre-existentes = **40 slots
disponíveis**).

### 2.1 Equity index proxies (CFD ≈ ETF)
| Ticker | Proxy Pepperstone | Role |
|--------|-------------------|------|
| SPY | US500 | Base beta — benchmark universal |
| QQQ | USTEC | Growth/tech |
| DIA | US30 | Old-economy |
| IWM | US2000 | Small caps |
| EFA | EUSTX50 (aprox) | Developed ex-US |
| EEM | — (no CFD 1:1) | Emerging markets proxy |

### 2.2 Sector ETFs (US)
XLK, XLF, XLE, XLV, XLI, XLY, XLP, XLU, XLB, XLRE, XLC
(11 sectors — diversificação intra-market requisito Carver `[systematic_trading, ch.8]`)

### 2.3 Commodities
| Ticker | Proxy | Use |
|--------|-------|-----|
| GLD | XAUUSD | Gold |
| SLV | XAGUSD | Silver |
| USO | WTI CFD | Oil |
| UNG | Nat gas CFD | Natural gas |
| DBA | Soft commodity basket | Agriculture |

### 2.4 Fixed income
| Ticker | Role |
|--------|------|
| TLT | 20y+ Treasury (interest rate macro) |
| IEF | 7-10y Treasury |
| HYG | High yield corporate |
| LQD | Investment grade corporate |

### 2.5 FX majors (daily, já em cache)
EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD, USDCHF, EURJPY, EURGBP, GBPJPY + XAUUSD, XAGUSD (12 total).

### 2.6 Crypto
BTCUSD (ETHUSD indisponível em Tiingo — aceitar ou pullar via alternative source em V2-L0)

**Total universe V2 = 40 instrumentos.**

### 2.7 Pre-screening (V2-L0 task)
Reportar por instrumento (sem gating automático — informa escolhas):
- Avg daily dollar volume ≥ $10M (liquidity sanity)
- ≥ 1500 daily bars (≥ 6y window)
- Hurst exponent 100d (trend vs MR tendency)
- Correlation matrix vs SPY (usado por Carver RP)
- Annualized vol 252d

Output: `data/universe_plano_a_v2.json` + `reports/phase3_5a_v2/L0_universe_screener.md`.

---

## 3. Cost model V2 (retail Pepperstone Razor — universal)

Modelagem honesta por round-trip, aplicável a todos os backtests:

| Componente | Valor | Aplica quando |
|------------|-------|---------------|
| Spread (half × 2) | 2-5 bps × 2 = **4-10 bps** | Toda entrada+saída |
| Commission | $3.50/side × 2 = $7 round | Por trade |
| Slippage (retail) | **1-3 bps** round | Por trade |
| Swap daily | 0.005%-0.02% on notional | Para cada dia com posição overnight |

**Totais aproximados por round-trip:**
- Equity/ETF (SPY, QQQ...): **7-11 bps**
- FX majors (EURUSD...): **6-10 bps**
- Metais/commodity (GLD, USO...): **10-15 bps**
- Crypto (BTCUSD): **15-25 bps** (spread maior)

**Hold-aware daily cost:**
- Hold ≤ 2d: swap ≈ 0, spread+comm domina (edge por trade ≥ 10-15 bps)
- Hold 3-10d: swap 2-10 bps cumulative, spread+comm amortiza (edge ≥ 20 bps)
- Hold 10-30d: swap 10-40 bps cumulative, spread+comm ruído (edge ≥ 50 bps)

**Edge mínimo sobrevivente:** 15 bps por round-trip. Strategies com edge médio
< 15 bps **não passam**, por design. Carver `[systematic_trading, p.185]`.

**Implementação:** reusar `src/ai_trade/backtest/metrics/standard_report.py`
(não duplicar) + adicionar `CostModel` helper em `src/ai_trade/backtest/costs/`
se não existir.

---

## 4. Strategy Leads

Cada lead = 1+ iter do loop fan-out. Types:
- **[atomic]** — 1 iter fecha o lead (bootstrap + backtest + aggregator tudo junto)
- **[sweep-tickers]** — 1 iter = 1 ticker (usa fan-out registry)
- **[sweep-configs]** — 1 iter = 1 config (fan-out registry com configs como "tickers")

Citação obrigatória `[book.slug, p.X]` em toda decisão de parâmetro
(CLAUDE.md regra 2).

### V2-L0 — Universe screener [atomic]
**Goal:** Validar coverage Tiingo, gerar manifest, produzir screener report.
**Output:**
- `data/universe_plano_a_v2.json` — manifest com first_dt/last_dt/vol/hurst/corr_spy por instrumento
- `reports/phase3_5a_v2/L0_universe_screener.md` — tabela + comentários
**Iter budget:** 1
**Citation:** `[advances_fin_ml, ch.2]` (data integrity) + `[systematic_trading, p.~90-100]` (universe selection).

### V2-L1 — TSMOM multi-asset daily [sweep-configs]
**Family:** Time-series momentum (Moskowitz, Ooi, Pedersen 2012 →
Carver retail adaptation).
**Universe:** Top N ≤ 30 instrumentos (filtrados por liquidez em V2-L0).
**Configs (sweep):**
- Lookback window: 1m, 3m, 6m, 12m (4 variações)
- Vol-target annualized: 10%, 15%, 20% (3 variações)
- Signal: binary long/flat per instrument (not long/short — retail simplification)
- Rebalance cadence: monthly EOM
- Total configs: 4 × 3 = **12 configs**

**Fan-out strategy:** 1 bootstrap iter + 12 sweep iters (1 config por iter,
cada config roda sobre o universe inteiro de V2-L0) + 1 aggregator iter =
**14 iters**.

**Gates:** 5-layer + winner criteria §1.
**Citation:** `[systematic_trading, ch.8-9]` (Carver), `[trend_following_covel]`,
`[advances_fin_ml, ch.8]` (meta-strategy feature engineering).

### V2-L2 — Gayed LETF rotation transportada para CFD [sweep-configs]
**Family:** Regime-conditional leveraged momentum (Gayed 2016/2020 LRS).
**Universe:** Subset do universe V2-L0: SPY, QQQ + 2x-equivalent leverage via
margin CFD (não LETF). Comparar com Plano B Phase 3.5b que usa SSO/UPRO.
**Configs (sweep):**
- Regime signal: SPY 200-SMA, EMA-100, LRS composite (3 variações)
- Leverage: 2×, 3×, 5× via margin CFD (3 variações)
- Off-regime allocation: cash, TLT, GLD (3 variações)
- Total configs: 3 × 3 × 3 = **27 configs**

**Fan-out strategy:** 1 bootstrap + 27 sweeps + 1 aggregator = **29 iters**.

**IMPORTANTE — não tocar em Plano B:** `letf_rotation.py`, `tsmom.py`,
`portfolio_3leg.py` permanecem imutáveis. V2-L2 cria um novo
`src/ai_trade/backtest/strategies/plano_a_leveraged_rotation.py` que
**herda** do LETF rotation mas aplica leverage CFD real (assume
alavancagem unlimited, custos swap daily) em vez de LETF synthetic
(SSO/UPRO com drag fixo).

**Gates:** 5-layer + winner criteria §1.
**Citation:** `[leverage_for_the_long_run]` (Gayed), `[leverage_space, Vince]`
(PoR leverage cap), `[math_money_mgmt, Vince]` (Kelly f/2).

### V2-L3 — AFML triple-barrier + meta-labeling [sweep-tickers]
**Family:** ML-augmented direction + confidence filter (López de Prado ch.3).
**Universe:** 10-15 instrumentos líquidos (SPY, QQQ, GLD, TLT, EFA + 5-10 sector ETFs).
**Configs (fixo, não sweep):**
- Primary model: simple daily trend direction (EMA-50 crossover)
- Triple-barrier: profit-take 2×ATR, stop 1×ATR, time-stop 20 bars
- Meta-label model: sklearn RandomForest (100 trees, depth 5) treinado em
  features {return 5d, vol 20d, RSI 14d, ATR ratio}
- Train/test: walk-forward CPCV 8 folds

**Fan-out strategy:** 1 bootstrap + 10-15 sweeps (1 ticker por iter) + 1 aggregator
= **~14 iters**.

**Gates:** 5-layer + winner criteria §1.
**Citation:** `[advances_fin_ml, ch.3]` (triple-barrier + meta-label),
`[advances_fin_ml, ch.7]` (CPCV).

### V2-L4 — Carver risk-parity multi-strategy portfolio [atomic]
**Family:** Multi-strategy combination via risk budgeting.
**Pre-requisito:** L1, L2, L3 tenham produzido ≥ 2 candidates não-NaN
(não precisa ter PASSed, só ter rodado com metrics válidas).

**Method:**
- Inputs: best config de cada L1, L2, L3 (best por Sharpe OOS, mesmo se não PASS)
- Combine via inverse-volatility weighting (Carver `[systematic_trading, p.~280-310]`)
- Aplicar gates sobre o blend final

**Iter budget:** 1 (atomic — combina em memória, backtesta, gate, escreve).
**Citation:** `[systematic_trading, ch.8-9]` (risk budgeting), `[advances_fin_ml, ch.16]`
(portfolio construction).

### V2-L5 — Equity pairs / cointegration daily [sweep-tickers]
**Family:** Statistical arbitrage on cointegrated equity pairs.
**Universe (pares pre-selecionados por afinidade econômica):**
- QQQ / XLK (tech vs tech sector)
- SPY / IWM (mega vs small cap)
- GLD / SLV (precious metals)
- XLF / HYG (financials vs high yield)
- XLE / USO (energy sector vs oil)
- TLT / IEF (long vs medium duration)

**6 pares.**

**Configs (fixo por par):**
- ADF test on spread; Engle-Granger 2-step cointegration
- Kalman filter dynamic beta
- Entry/exit: 2σ band
- Hold cap: 30 days

**Fan-out strategy:** 1 bootstrap + 6 sweeps + 1 aggregator = **8 iters**.

**Gates:** 5-layer + winner criteria §1.
**Citation:** `[machine_trading_chan, ch.3]` (Kalman pairs), `[algo_trading_chan, p.42-54]`
(ADF + EG), `[advances_fin_ml, ch.7]` (CPCV for time series).

### V2-L6 — Vol-breakout multi-asset daily [sweep-configs]
**Family:** Donchian/ATR breakout on non-FX (V1 já refutou FX).
**Universe:** Índices (SPY, QQQ, DIA, IWM) + commodities (GLD, SLV, USO, UNG)
+ fixed income (TLT, HYG) = 10 instrumentos.
**Configs (sweep):**
- Channel lookback: 20d, 50d, 100d (3)
- Exit: trailing ATR-3×, opposite channel (2)
- Direction: long-only, long/short (2)
- Total: 3 × 2 × 2 = **12 configs**

**Fan-out strategy:** 1 bootstrap + 12 sweeps + 1 aggregator = **14 iters**.

**Gates:** 5-layer + winner criteria §1.
**Citation:** `[trading_systems_methods, p.353]` (Donchian), `[volatility_trading]`
(ATR channels), `[trend_following_covel]` (breakout on CTAs).

### V2-L7 — Summary + verdict + flip done [atomic]
**Goal:** Consolidar resultados L1-L6, aplicar stop rule, escrever jornada final.

**Output:**
1. `reports/phase3_5a_v2/AGGREGATE.md` — tabela cross-lead com best per-lead.
2. `jornada/<date>-phase3.5a-v2-summary-<VERDICT>.md` — tag `[SHORT-HOLD CFD]`.
3. Mandate §7 — entry V2 verdict.
4. Memory.md `status: done`, `winners_short_hold:` atualizado se houver.

**Verdict logic:**
- SE ≥ 1 strategy passa TODOS os gates + winner criteria (CAGR ≥ 30%,
  Sharpe ≥ 2.0, MaxDD ≤ 25%, median hold ≥ 3d) → **WINNER FOUND**.
  Escalar para `specs/phase_4_paper_trading.md` draft. Atualizar
  `winners_short_hold:` em memory.md.
- SE 0 strategies passam → **FORMAL ABANDON PLANO A**. T7 aplica:
  - `docs/investment-mandate.md` §7: entry final "Plano A V2 exhausted — Opção B"
  - `docs/investment-mandate.md` §4.7: re-alocação 5pp Path A → Path B (30pp ativo)
  - `memory.md` frontmatter: status done, next_phase: "3.5b refinement + 4 paper trading"
  - ROADMAP.md: Phase 4 = Plano B puro
  - **NÃO propor V3.** Respeitar stop rule.

**Iter budget:** 1 (atomic).
**Citation:** `[advances_fin_ml, p.~250-270]` (ambiguity aversion + model selection stopping).

---

## 5. Iter budget agregado

| Lead | Iters | Tipo |
|------|------:|------|
| V2-L0 universe screener | 1 | atomic |
| V2-L1 TSMOM | 14 | sweep-configs (1 boot + 12 + 1 agg) |
| V2-L2 Gayed transport | 29 | sweep-configs |
| V2-L3 AFML meta-label | 14 | sweep-tickers |
| V2-L4 Carver RP | 1 | atomic |
| V2-L5 equity pairs | 8 | sweep-tickers |
| V2-L6 vol breakout | 14 | sweep-configs |
| V2-L7 summary | 1 | atomic |
| **Total esperado** | **82** | — |

Com `MAX_ITER=80`, corte ~2 iters. Se L2 (Gayed) esgotar cedo (passou ou
falhou com K configs tested), o aggregator fecha antes e libera budget
para L4-L6. Margem de erro operacional aceitável.

**ETA:** 82 iters × ~5 min/iter = **~7 horas autônomas** (margem 6-8h).

---

## 6. Pre-launch checklist (a executar antes do `nohup bash ...`)

Ordem mandatória — skipa 1, loop quebra ou produz output inconsistente.

- [ ] **B1.** Criar branch nova:
  ```bash
  git checkout -b phase3.5a-v2/plano-a-last-attempt-20260418
  ```
- [ ] **B2.** Reset memory.md com template V2:
  - `status: in_progress`
  - `iteration: 0`
  - `phase: 3.5a-v2`
  - `active_lead_registry: null`
  - Preservar `winners_short_hold:` e `winners_swing:` (não resetar — Plano B fica intocado)
  - `## Leads` section com L0-L7 em ordem, tagueados `[atomic]` / `[sweep]`
- [ ] **B3.** Append entry §7 em `docs/investment-mandate.md`:
  ```
  | 2026-04-18 | V2 corrigida launched (último test Plano A) | T6/T7 do V1
  interpretaram V1 como "V2"; este é o V2 real com framework corrigido
  (timeframe livre, hold ≥ 3d, ≥30 instrumentos multi-asset CFD,
  cost model spread+commission-dominant, CAGR target 30%/yr). Se V2
  produzir 0 PASS → Opção B do T6/T7 original é ratificada
  (abandon Plano A + 5pp → Path B). Sem V3. | TBD |
  ```
- [ ] **B4.** Verify Tiingo daily cache coverage do universe V2:
  ```bash
  python3 scripts/verify_v2_universe.py   # NEW — a criar pre-launch
  ```
  Fallback: se < 30 hits, pullar faltantes via `tiingo_bulk_download.py`
  para `data/tiingo/` antes de lançar.
- [ ] **B5.** Pytest baseline verification: **≥ 765 passed** (V1 fechou em 765).
- [ ] **B6.** Loop pid cleanup: `rm -f /tmp/loop_3_5a_fanout.pid`
  (V1 pid file obsoleto — evita confusão operacional).
- [ ] **B7.** Launch cmd:
  ```bash
  nohup env CLAUDE_MODEL=claude-opus-4-7 MAX_ITER=80 \
      ITER_TIMEOUT=1800 SCOPE=code SWEEP_MODE=fanout \
      bash scripts/self_improve_loop.sh \
      > logs/loop_3_5a_v2_$(date +%Y%m%d_%H%M).log 2>&1 &
  echo $! > /tmp/loop_3_5a_v2.pid
  ```

---

## 7. Hard rules (não-negociáveis)

1. **Pytest ≥ 765 passed** o tempo todo. V2 pode adicionar testes novos
   (ex: V2-L3 AFML meta-label precisa de testes unitários) mas nunca
   reduzir.
2. **NÃO tocar em Plano B:** `letf_rotation.py`, `tsmom.py`,
   `portfolio_3leg.py`, `synthetic_letf.py`, `rebalance_modes.py`
   permanecem imutáveis.
3. **NÃO modificar BollingerMR seed:** `bollinger_mr.py`, `momentum.py`,
   `standard_report.py` imutáveis.
4. **NÃO push origin nem mexer em `main`.** Loop auto-commit apenas na
   branch V2.
5. **Citação `[book.slug, p.X]`** obrigatória em toda escolha de
   parâmetro/strategy. CLAUDE.md regra 2.
6. **Atomic writes** em registry + per-unit files (via
   `ai_trade.backtest.sweeps.registry` helper). Nunca escrever direto em
   arquivos live.
7. **1 unit por iter em fanout mode.** Bootstrap = 1 iter sem unit.
   Sweep = 1 ticker ou 1 config. Aggregator = 1 iter agregação. NUNCA
   2 units em 1 iter.
8. **Jornadas curtas + tag `[SHORT-HOLD CFD]` no H1** (consistente V1).
9. **Stop rule binding:** T7 aplica verdict. Se 0 PASS → abandon,
   sem proposta de V3. Respeita user memory.
10. **2 iters consecutivas mesmo erro fatal → loop aborta + jornada
    blocker**. Consistent com V1.

---

## 8. Out of scope (V2)

Lista explícita do que V2 **NÃO** faz, para evitar drift:

- **1h intraday FX/metais** — V1 já refutou 108 runs. Não re-testar.
- **BollingerMR canonical 20/2σ** — V1 (T1) refutou 36 runs. Não re-testar.
- **Session-based FX** — V1 (T4) refutou. Não re-testar.
- **Regime-filter linear sobre MR** — V1 (T5) refutou. Não re-testar.
- **Kalman pairs em FX** — V1 (T3) refutou. V2-L5 testa pairs em equity
  (diferente underlying, diferente mechanics).
- **Leverage sweep > 5x** — Vince/Carver `[leverage_space, math_money_mgmt]`
  mostram PoR alto. L=5 é upper bound; acima disso é ruína empírica.
- **Universe < 30 instrumentos** — não atende breadth rule Carver.
- **Timeframe < daily** — cost economics invertidas (V1 lição).
- **Single-asset edges** — mandate §3 obrigatório multi-asset.
- **V3** — binding stop rule. Se 0 PASS, pára.

---

## 9. Pós-V2 (conditional branches)

### 9.1 Se V2 encontrar winner
1. T7 escreve jornada `[SHORT-HOLD CFD] Plano A V2 winner: <strategy>`.
2. `winners_short_hold:` em memory.md recebe novo entry (append, não
   substituir BollingerMR).
3. Abrir `specs/phase_4_paper_trading.md` com foco dual:
   - Plano B (3-leg EW daily) já autorizado (3.5b PRODUCTION.md)
   - Plano A (novo winner) paper trading concurrent
4. Mandate §7: entry ratificando V2 success.

### 9.2 Se V2 NÃO encontrar winner
1. T7 aplica checklist abandon (§4 V2-L7 verdict logic).
2. Branch V2 permanece (git log é evidência).
3. Próximo spec: **`specs/phase_3_5b_refinement.md`** — escopo:
   - Multi-asset transport do 3-leg Plano B para mais instrumentos
     (SSO+QQQ+GLD → SSO+QQQ+GLD+TLT+XLE?)
   - Threshold optimization (5pp, 10pp, volatility-adjusted)
   - Leverage scaling (SSO+UPRO mix, Kelly f/4)
   - Paper trading setup (§4.6 Banco Inter ratificado)
4. Phase 4 lança apenas com Plano B.
5. **Cortar todas as dependências Plano A:** arquivar/remover cTrader
   OAuth infra, threading multi-asset, universe pre-screener Hurst/ATR
   (já implementado mas órfão sem Plano A).

---

## 10. Referências (livros citados neste spec)

- `[advances_fin_ml]` — López de Prado 2018. CPCV, PBO, DSR, meta-labeling, CI tests.
- `[systematic_trading]` — Carver 2015. Multi-asset breadth, cost economics, risk budgeting.
- `[trend_following_covel]` — Covel 2017. TSMOM historical performance.
- `[trading_systems_methods]` — Kaufman 2013. Donchian p.353.
- `[volatility_trading]` — Sinclair. ATR channels, vol regime.
- `[machine_trading_chan]` — Chan 2017. Kalman pairs ch.3.
- `[algo_trading_chan]` — Chan 2013. ADF+EG ch.2.
- `[quant_trading_chan]` — Chan 2009. Session FX ch.2-3 (V1 reference, não usado V2).
- `[leverage_for_the_long_run]` — Gayed 2016/2020. LRS regime rotation (Plano B).
- `[leverage_space]` — Vince. PoR vs leverage.
- `[math_money_mgmt]` — Vince. Kelly f/2 cross-check.

---

## 11. Decision gates (user-ratificáveis)

Antes do launch, usuário ratifica:

- [ ] Spec aprovada (este doc, sem alterações materiais)
- [ ] Pre-launch checklist §6 executado
- [ ] Branch V2 criada
- [ ] Memory reset com template V2
- [ ] Mandate §7 entry adicionada
- [ ] Launch command disparado

Durante V2:
- Loop roda sozinho. User checa via `/loop-status` quando quiser.
- **NÃO interromper a meio** a menos que 2 iters consecutivas falhem
  mesmo erro fatal OU pytest quebre baseline.

Pós-V2:
- T7 escreve verdict.
- User ratifica abandon (se 0 PASS) ou winner (se ≥ 1 PASS).
- Próximo spec em consequência (Phase 4 ou 3.5b refinement).

---

**Este spec é final.** Não adicionar leads, famílias ou ajustes
sem ratificação. V2 é o último teste. Vamos executá-lo com rigor e
respeitar o verdict que ele produzir.
