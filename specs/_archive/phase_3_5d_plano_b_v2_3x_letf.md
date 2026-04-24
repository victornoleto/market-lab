# Phase 3.5d — Plano B V2, 3× LETF swing (search spec)

> **Status:** draft autoritativo para o self-improve loop.
> **Criado:** 2026-04-20.
> **Antecessor:** Phase 3.5b (Plano B V4) — rejeitado em 2026-04-20 por
> cross-lib divergence. Ver `jornada/2026-04-20/03-phase-3-5c-cross-lib-exposed-baseline-mismatch.md` e `04-plano-b-v4-rejected-3-5d-launch.md`.
> **Execução:** self-improve loop autônomo (branch dedicada, não `main`).

---

## 0. Por que Phase 3.5d existe

O winner Phase 3.5b (3-leg EW SSO+QLD+UGL threshold 10pp) foi rejeitado
porque:

1. A validação interna usou dados proprietários testfol.io
   (SSOSIM/QLDSIM/UGLSIM) que não reproduzem no nosso stack
   (`synthesize_letf_returns_ffr_aware` + yfinance). 3 libs independentes
   (bt, vectorbt, backtrader) concordam em CAGR ≈ 11.6% / max_dd ≈
   -28.8%, não nos 37.92% / -16.91% da Phase 3.5b.
2. O winner não supera SSO buy-and-hold real pós-inception (nosso
   10.23% vs buy-and-hold 14.96% canonical). Regime filter troca CAGR
   por DD reduction em trade-off Sharpe-neutro.
3. Indicator picks não-homogêneos entre as 3 legs (EMA100 na SPY,
   Donchian nas outras) expandiram silenciosamente o search space sem
   controle formal.

**Diagnóstico:** precisamos de um novo winner com (a) dado replicável,
(b) validação multi-engine desde o dia 1, (c) discipline de
indicator-family escolhida com citação de livro por leg, (d) gate que
**exige superar SPY buy-and-hold pós-imposto**.

---

## 1. Objetivo (north star)

Encontrar **uma configuração de estratégia swing trade** sobre 3×
LETFs (UPRO ou SPXL, TQQQ, TMF opcional) que:

1. Passe gates internos de overfit (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8).
2. **Supere SPY buy-and-hold** em CAGR líquido pós 15% IR BR na janela
   pós-inception (UPRO: 2009-06-25+; SPXL: 2008-11-05+; TQQQ:
   2010-02-09+) — janela limitante = comum pós-2010.
3. Seja validada cross-library em no mínimo 2 de 3 engines
   (bt, vectorbt, backtrader) concordando dentro de ±3pp de CAGR.
4. Tenha max_dd aceitável — pode ser > 25% desde que **Calmar =
   CAGR / |max_dd| > 0.5** e Sharpe pós-imposto > 0.8.
5. Cite book+página por cada parâmetro, filter, rebalance rule, e
   asset choice.

---

## 2. Universe (3× LETFs)

### 2.1 Primary universe (obrigatório)

Todos têm histórico real ≥ 16 anos em 2026-04-20:

| Ticker | Underlying | Leverage | Inception | ER |
|---|---|---|---|---|
| UPRO | S&P 500 | 3× | 2009-06-25 | 0.91% |
| SPXL | S&P 500 | 3× | 2008-11-05 | 1.00% |
| TQQQ | NASDAQ-100 | 3× | 2010-02-09 | 0.84% |
| TMF | 20+ Treasury | 3× | 2009-04-16 | 1.06% |

UPRO e SPXL são duplicatas 3× SPY (escolher **UPRO** como default por
ER mais baixo; rodar SPXL só em sensitivity analysis).

### 2.2 Extended universe (secundário — opt-in se primary produzir winner)

| Ticker | Underlying | Leverage | Inception |
|---|---|---|---|
| TNA | Russell 2000 | 3× | 2008-11-05 |
| UDOW | Dow 30 | 3× | 2010-02-09 |
| UGL | Gold (GLD) | 2× | 2008-12-03 |
| TYD | 7-10Y Treasury | 3× | 2009-04-16 |

**Não incluir inverse LETFs** (SQQQ, SPXS). Decay faz inverse
sistematicamente pior — fora do mandate.

### 2.3 Benchmark universe (comparação obrigatória)

- **SPY** (buy-and-hold) — baseline a superar. Post-tax 15% sobre CAGR.
- **QQQ** (buy-and-hold) — benchmark tech.
- **60/40 SPY/TLT** — benchmark conservador.
- **Static 3-leg EW UPRO+TQQQ+TMF buy-and-hold** — referência
  "naive LETF portfolio" sem regime.

Todas essas rodam na mesma janela pra comparação apples-to-apples.

---

## 3. Data pipeline

### 3.1 Source discipline

**Stage 1 (same-data replication test):** usar
`reports/phase_3_5c/cross_lib/data/reference_prices.parquet` (a
seam-corrigida). Pré-inception: `synthesize_letf_returns_ffr_aware`
com scaling à primeira close real (fix commit `b27ccb0`).

**Stage 2 (independent-data replication test):** usar yfinance direto
(fresh fetch no início da sessão) para janela pós-inception de cada
LETF.

**Stage 3 (manual testfol.io cross-check):** opcional, só pra o
winner shortlist. Exportar CSV testfol.io para o winner, rodar via
`testfolio_extract.py` (ja existe), ver se dá uma terceira evidência.

### 3.2 Reference_prices updates necessários antes de iniciar

Faltam em `reference_prices.parquet`:

- UPRO (não presente), inception 2009-06-25, ER 0.91%
- SPXL (não presente), inception 2008-11-05, ER 1.00%
- TQQQ (não presente), inception 2010-02-09, ER 0.84%
- TMF (não presente), inception 2009-04-16, ER 1.06%

**Task zero do Phase 3.5d:** adicionar esses 4 LETFs aos `LETF_SPECS`
em `reports/phase_3_5c/cross_lib/data/reference_prices.py` com
inception/ER/underlying corretos, rebuild parquet, smoke test.

---

## 4. Strategy families a testar (ordem de prioridade)

Cada família abaixo é um **Lead** no vocabulário do self-improve loop.
O loop consume em ordem. Cada Lead produz aggregator (PASS/DEAD/PENDING)
com cross-lib evidence.

### Lead D1 — Buy-and-hold 3× LETF puro (baseline defensivo)

**Citação:** `[leverage_for_the_long_run, p.16]` — synthetic formula
valida que 3× SPY decay não destrói o CAGR em bull markets longos.

**Objetivo:** estabelecer "can buy-and-hold UPRO beat SPY B&H after
tax?" como floor. Se sim, regime-filter tem que bater esse floor. Se
não, regime-filter vira obrigatório.

**Configs:**
- Full buy-and-hold UPRO.
- Full buy-and-hold TQQQ.
- EW 50/50 UPRO+TQQQ, daily rebalance.
- EW 50/50 UPRO+TQQQ, monthly rebalance.
- EW 33/33/33 UPRO+TQQQ+TMF (risk-parity-ish), daily.
- EW 33/33/33 UPRO+TQQQ+TMF, monthly.

**Janela:** pós-2010-02-09 (todas as 3 existem) até 2026-04-18.
~16 anos.

**Gates:** passar os 5 gates padrão + cross-lib (Section 6).

### Lead D2 — MA regime filter homogêneo (Gayed canonical, um indicador em TODAS as legs)

**Citação:** `[leverage_for_the_long_run, p.13, p.16]` — MA regime é
a ÚNICA família que Gayed prova rigorosamente para LRS filtering.

**Objetivo:** responder "se filter MA é bom pra SPY, é bom pra QQQ e
pra TMF também?". Força indicator homogeneity.

**Configs (variando lookback + off-leg):**
- SMA200 regime, off=cash, 3× UPRO long-only (single-leg).
- EMA100 regime, off=cash, 3× UPRO (Gayed variant).
- LRS (200d low/high) regime, off=cash, 3× UPRO.
- SMA200 regime em SPY → UPRO, paralelo SMA200 em QQQ → TQQQ, EW 50/50.
- EMA100 em SPY → UPRO, EMA100 em QQQ → TQQQ, EW.
- Idem com off=TMF (Gayed `[p.60]` off-leg opcional).
- Idem com off=GLD.

**Janela:** pós-inception + pré-inception synthetic (scaling
aplicado). Canonical: 2010-02-09 → 2026-04-18 (16y).

### Lead D3 — Donchian breakout homogêneo (Kaufman/Clenow)

**Citação:** `[trading_systems_methods, p.353]` — Donchian canonical.
`[stocks_on_the_move, p.81]` — lookback 90-120 para equity momentum.

**Objetivo:** responder "se Donchian é melhor que MA para ação
Equity breakout, opera na SPY também?". Força indicator homogeneity
na outra direção.

**Configs:**
- Donchian 20/10 entry/exit em UPRO (direct).
- Donchian 40/20 em UPRO.
- Donchian 60/30 em UPRO (long equity trend).
- Idem em TQQQ.
- EW 50/50 UPRO+TQQQ com Donchian em cada.

### Lead D4 — Dual momentum (Antonacci)

**Citação:** `[dual_momentum]` ou `[antonacci_dual_momentum]`, cap.
concreto a ser citado por quem rodar.

**Objetivo:** testar se rankings cross-asset (UPRO vs TQQQ vs TMF
vs SHY) com absolute momentum filter bate buy-and-hold.

**Configs:**
- Monthly rank top-1 entre {UPRO, TQQQ, TMF}.
- Monthly rank top-1 entre {UPRO, TQQQ, TMF, SHY} com SHY como bailout.
- Monthly rank top-2 (split 50/50).

### Lead D5 — Volatility targeting (risk-scaled LETF exposure)

**Citação:** `[advances_fin_ml, cap.14]` — risk-adjusted sizing.
`[volatility_trading]` pode complementar.

**Objetivo:** em vez de regime on/off, escalar a exposição entre 0-100%
UPRO baseado em vol target. LETFs têm vol ~2-3× do underlying, mas o
objetivo é cap o *portfolio* vol, não o ETF vol.

**Configs:**
- Target vol 15%/ano, 20d realized vol lookback, UPRO single-leg.
- Target vol 20%/ano, 60d lookback.
- Target vol 15%, 20d, + SMA200 regime overlay.
- Target vol 20%, 60d, UPRO+TQQQ EW sub-portfolios.

### Lead D6 — Trend + momentum composite

**Citação:** `[stocks_on_the_move, p.81, ch.6]` — Clenow trend ranking.

**Objetivo:** composite score (MA slope + momentum rate + low vol)
para decidir quando LEVERAGE e quando CASH.

**Configs:**
- Score > 0 → UPRO full, else cash. Score = w1·MA_slope + w2·MOM(90d) + w3·(1/vol).
- Variar pesos (3 triplas).

### Lead D7 — Regime-gated dual LETF

**Citação:** `[leverage_for_the_long_run, p.13]` (MA regime) +
`[antonacci_dual_momentum]` (dual mom inter-leg).

**Objetivo:** Two-layer — SMA200 SPY regime decide "risk on" (UPRO ou
TQQQ) vs "risk off" (TMF ou cash). Dentro de "risk on", dual mom
entre UPRO e TQQQ decide qual.

**Configs:**
- SMA200 risk on/off, off=cash, on = max(UPRO mom90, TQQQ mom90).
- SMA200 risk on/off, off=TMF, on = max(UPRO, TQQQ) por mom90.
- EMA100 regime, idem.

### Lead D8 — Tactical bond-equity hedge (stretch)

**Citação:** `[permanent_portfolio]` + `[leverage_for_the_long_run, p.60]`.

**Objetivo:** permament portfolio com LETFs (UPRO + TMF + UGL + cash).
EW ou risk parity.

**Configs:**
- EW 25/25/25/25 daily rebal.
- Risk parity (realized vol inverse).

---

## 5. Rejected (explicitly do NOT revisit)

- **Family V4 3-leg EW SSO+QLD+UGL threshold 10pp** — rejeitado em
  `jornada/2026-04-20/03-*` e `04-*`. Não replicar.
- **LETF rotation EMA100 2× L=2 em CFD** (Plano A V2-L2) — stand-by,
  fora do escopo desta phase.
- **Inverse LETFs (SQQQ, SPXS, SDOW)** — decay estrutural, fora do mandate.
- **Intraday LETF trading** — Plano A é CFD, Plano B é swing. Não misturar.

---

## 6. Gates obrigatórios (todos pass = winner)

Por variant (lead × config × universe × window):

### 6.1 Overfit gates (internos, mesmos da Phase 3.5b)

1. **PBO < 0.5** — combinatorial purged splits `[advances_fin_ml, p.208-211]`.
2. **DSR p < 0.05** — deflated Sharpe, deflate por N_trials_local `[advances_fin_ml, p.298-299]`.
3. **WF ≥ 6/8** — walk-forward, 8 janelas, cada janela profitable.
4. **Single-block OOS hold-out** — 20% final do histórico reservado,
   rodar só no final do lead, gate: OOS Sharpe ≥ 0.5 × IS Sharpe.
5. **Forward-window stress** — última trimestre, Sharpe > 0.

### 6.2 Replicability gates (NOVOS, anti-Phase-3.5b-repeat)

6. **Cross-lib concordance** — rodar no mínimo 2 de 3 engines (bt,
   vectorbt, backtrader). Gate: top 2 libs CAGR dentro de ±3pp, max_dd
   dentro de ±5pp, Sharpe dentro de ±0.15. Usar adapters já prontos em
   `reports/phase_3_5c/cross_lib/adapters/`.
7. **Two-stage data validation** — resultado Stage 1 (reference_prices)
   e Stage 2 (yfinance independent) divergem em ≤ ±3pp CAGR. Se
   divergem mais, investigar synthetic/real seam antes de claim winner.

### 6.3 Economic gates (NOVOS, anti-folclore)

8. **Beat SPY buy-and-hold post-tax** — CAGR_net_tax > SPY_BH_CAGR
   na mesma janela. Net tax = CAGR × (1 - 0.15) para Brasil 15% IR
   sobre ganhos com ETFs USA. Math: se SPY buy-and-hold produziu 10%
   CAGR, strategy precisa > 10%/0.85 = 11.76% CAGR bruto para bater
   pós-imposto. **Se não supera SPY B&H, é folclore (per user
   2026-04-20).**
9. **Calmar > 0.5** — CAGR / |max_dd| > 0.5. Permite max_dd > 25% se
   CAGR compensa.
10. **Sharpe pós-imposto > 0.8.**

### 6.4 Gate order & failure handling

Dentro do loop:
- Se um config falha em gate 1-3 (overfit), abandonar essa config.
- Se falha em gate 4-5 (OOS/stress), abandonar esse variant.
- Se passa 1-5 mas falha 6-7 (replicability), **INVESTIGATE** —
  forensic doc em `reports/phase_3_5d/errors/`, pode indicar bug de
  adapter ou data issue real. Não descartar silenciosamente.
- Se passa 1-7 mas falha 8-10 (economic), documentar em jornada como
  "passou overfit gates mas não supera SPY" — interessante
  metodologicamente, descartado operacionalmente.
- Se passa 1-10, **winner candidato** — vai para shortlist Phase 3.5d
  final arbitration.

---

## 7. Loop protocol (self-improve)

### 7.1 Modo

`SWEEP_MODE=fanout` — usar infra de `specs/self_improve_fanout_mode.md`.
Cada Lead D1-D8 é um registry separado em
`reports/phase_3_5d/<lead_slug>/registry.json`.

Universe por Lead = {UPRO, TQQQ} como minimum + extended opt-in per
Lead como spec do Lead. Cada ticker = 1 iter fanout.

### 7.2 Iter sequence estimado

| Iter | Ação |
|---|---|
| 0 | Task zero: rebuild reference_prices.parquet com UPRO/SPXL/TQQQ/TMF. |
| 1 | Bootstrap D1 registry. |
| 2-7 | D1 sweep (6 configs × 1 ticker = pequeno, pode agregar em 1-2 iters). |
| 8 | D1 aggregator. |
| 9 | Bootstrap D2. |
| 10-17 | D2 sweep. |
| ... | ... |
| ~40-60 | Aggregator D8 + final arbitration. |

Budget estimado: **50-70 iters autônomos**, ~10-15h wallclock em
batches de `MAX_ITER=10` noturnos.

### 7.3 Stop rule

- Encerrar cedo se 3 Leads produzirem winner-candidato (entra em
  Phase 3.5e = arbitration dos 3).
- Encerrar cedo se D1-D4 todos DEAD (famílias canônicas não funcionam
  → mudar premissa: 3× LETF é inviável com regime-filter? Precisa
  abordagem completamente diferente? Escalar ao usuário.).
- Se D1-D8 completos sem winner, escalar ao usuário — Plano B pode
  precisar abandonar LETF como base e voltar para equity ETF simples
  (QQQ buy-and-hold + filter?).

---

## 8. Arbitration final (post-loop)

Após loop terminar, sessão interativa humana decide entre winners
candidatos:

1. Cada winner recebe ficha: CAGR, max_dd, Sharpe, Calmar, cross-lib
   concordance, Stage 1 vs Stage 2 delta, citations, jornada links.
2. Usuário decide prioridade (se mais de 1 winner) baseado em
   simplicidade operacional, tax drag, turnover.
3. Criar `docs/strategies/plano_b_v2_<winner_slug>.md` com living doc
   (tipo `plano_a_v2_l2_gayed_cfd.md`).
4. Phase 3.5e encerra; Phase 4 paper trading dual-path retomada
   (agora com Plano B v2 validado).

---

## 9. Deliverables da Phase 3.5d

Ao final, ter:

- 1 winner **ou** documento "3× LETF swing é inviável em nossa data
  pipeline, migrar para ETF unleveraged" com citações cruzadas.
- `reports/phase_3_5d/<lead_slug>/AGGREGATE.md` para cada Lead.
- `reports/phase_3_5d/VERDICT.md` final.
- `jornada/2026-04-XX-phase-3-5d-verdict.md`.
- Atualização de `docs/investment-mandate.md §4` com winner
  confirmado (ou ausência dele).
- Atualização de `ROADMAP.md` com resultado da phase.
- **Baseline file independente** (não reutilizar Phase 3.5b's
  baseline.json — gerar novo a partir dos próprios winners do loop,
  cross-lib validated).

---

## 10. Anti-patterns explícitos (DO NOT)

1. **Não re-pinar baseline a partir de uma única engine.** Baseline
   de Phase 3.5d = consensus das libs que convergem, não de uma.
2. **Não aceitar gate 1-7 sem gate 8-10.** "Passou overfit" sem
   "supera SPY" é folclore per user decision.
3. **Não mix indicator family entre legs sem citação + teste formal.**
   Se perna A usa EMA e perna B usa Donchian, tem que citar p.X por
   leg + rodar variante homogênea como controle.
4. **Não ignorar divergência Stage 1 vs Stage 2 > 3pp.** Se acontecer,
   parar e investigar synthetic/real split — é o bug que afundou
   Phase 3.5b.
5. **Não fazer commit em `main` durante o loop.** Use feature branch
   `phase3.5d/plano-b-v2-3x-letf-YYYYMMDD`.

---

## 11. Citações seed (livros absorvidos)

- `[leverage_for_the_long_run]` — Gayed, base LRS, synthetic formula
- `[trading_systems_methods]` — Kaufman, Donchian canônico
- `[stocks_on_the_move]` — Clenow, momentum ranking
- `[advances_fin_ml, p.31-34, p.208-211, p.273-275, p.298-299]` — AFML, overfit gates
- `[volatility_trading]` — vol targeting
- `[antonacci_dual_momentum]` — dual momentum
- `[permanent_portfolio]` — risk parity allocation baseline
- `[ivy_portfolio]` — Faber TAA

Cada Lead deve citar ≥ 1 livro específico com página; Leads D2-D8 não
podem existir sem citação formal.

---

## 12. Open questions (para o loop resolver ou escalar)

- **ER drag:** our synthesize_letf_returns_ffr_aware usa ER estático
  (0.91% UPRO); real ER oscila por ano. Sensibility aceitável?
- **Swap cost modeling:** LETFs têm swap interno implícito em
  expense. Stage 2 yfinance já absorbe isso via adj_close. Stage 1
  synthetic deve replicar. Verificar consistency.
- **Tax lot modeling:** Phase 3.5d NÃO modela lot-level DARF timing.
  Aplica 15% flat sobre CAGR. Refinamento lote-a-lote fica para
  Phase 4 paper trading.
- **Rebalance trigger:** Phase 3.5b usou threshold 10pp. Phase 3.5d
  deixa rebalance schedule (daily, monthly, threshold 5/10/15pp) como
  hiperparâmetro dentro de cada config. Não hardcoded.

---

## 13. Execução (pra quando acordar)

```bash
# 1. Criar branch
git checkout main
git pull
git checkout -b phase3.5d/plano-b-v2-3x-letf-20260421

# 2. Archive Phase 3.5a-V2 memory
mv docs/self_improvement/memory.md docs/self_improvement/memory_archive_3_5a_v2_complete.md
cp docs/self_improvement/memory.template.md docs/self_improvement/memory.md
# Edit memory.md to reflect Phase 3.5d goal (lead list, leads in priority order)

# 3. Task zero — atualizar reference_prices.parquet
# Editar reports/phase_3_5c/cross_lib/data/reference_prices.py LETF_SPECS
# Rebuild parquet, smoke test
python -m reports.phase_3_5c.cross_lib.data.reference_prices

# 4. Lançar loop
MAX_ITER=10 SWEEP_MODE=fanout CLAUDE_MODEL=sonnet bash scripts/self_improve_loop.sh
# Iterar com MAX_ITER=10 por sessão. Revisar jornadas entre sessões.
```

---

## 14. Critério de "estou pronto pra começar"

- [ ] Branch criada
- [ ] memory.md fresh (novo) — aponta para este spec
- [ ] reference_prices.parquet contém UPRO/SPXL/TQQQ/TMF
- [ ] Adapters cross-lib (`bt/vectorbt/backtrader`) passam smoke test novo
- [ ] ROADMAP.md referencia Phase 3.5d como ativa
- [ ] jornada/README.md "Onde estamos" reflete estado atual
