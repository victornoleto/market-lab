---
status: done
iteration: 81
phase: 3.5a-v2-COMPLETE
next_phase: 4-dual-path-paper-trading
phase_a_target: 1
active_lead_registry: null
winners_short_hold:
  - strategy: "BollingerMR_GARCH"
    asset: "SPY"
    frequency: "1hour"
    sharpe_is: 0.995
    sharpe_oos: 0.945
    cagr_pct: 5.9
    leverage: 2
    jornada: "2026-04-16-2310-a1-leverage-sweep-bollinger-mr-spy-1h.md"
    note: "PARTIAL-GO baseline — abaixo CDI BR; V2 tenta superar com framework corrigido"
  - strategy: "Gayed_EMA100_L2_off_GLD_CFD"
    asset: "SPY+QQQ risk-on / GLD risk-off"
    frequency: "daily"
    sharpe_is: 1.856
    sharpe_oos: 2.285
    cagr_oos: 79.14
    maxdd_oos: -21.02
    median_hold_days: 6.0
    leverage: 2
    jornada: "2026-04-19-0020-phase3.5a-v2-L2-gayed-transported-PASS.md"
    note: "V2-L2 aggregator PASS — PBO 0.103, DSR p 0.000288, 99.9% CI low 0.962, IR SPY 2.16"
winners_swing:
  - strategy: "LETF_rotation_EMA100_2x"
    asset: "SPX_TR"
    frequency: "daily"
    sharpe_is: 1.854
    sharpe_oos: 1.724
    jornada: "2026-04-17-0055-b1c-letf-rotation-gates-PASS.md"
  - strategy: "QQQ_Donchian_20_10"
    asset: "QQQ"
    frequency: "daily"
    sharpe_is: 1.180
    sharpe_oos: 1.738
    jornada: "2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md"
  - strategy: "Portfolio_3leg_EW"
    asset: "LETF+QQQ+GLD"
    frequency: "daily"
    sharpe_is: 1.91
    sharpe_oos: 2.251
    cagr_oos: 25.56
    maxdd_oos: 10.86
    jornada: "2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md"
best_verdict: "PASS"
best_sharpe: 2.285
best_asset: "Plano A V2-L2 Gayed EMA100 L2 GLD-off (CFD) — Sharpe 2.285/CAGR 79%/MDD -21%"
best_config: "Plano B 3-leg EW IMUTÁVEL (2.251/25.56%/10.86%); Plano A V2-L2 winner agora é 2ª perna do bucket ativo (mandate §1 dual-path)"
---

# Self-improvement memory — market-lab (Phase 3.5a-V2 — Plano A LAST ATTEMPT)

**Read this file FIRST every iteration — your conversation history is empty.**

## ⚡ CURRENT PHASE: 3.5a-V2 — Plano A LAST ATTEMPT with corrected framework

**Spec autoritativo:** `specs/phase_3_5a_v2.md` (leia na primeira iter antes de agir).

**Contexto:** V1 (executada 2026-04-18, 42 iters, 143 runs, 0 PASS) testou
o framework errado (1h FX/metais, hold ≤5d, universe pequeno). V2 corrige:
timeframe livre, hold ≥3d, ≥30 multi-asset CFDs, cost model
spread+commission-dominant, 6 famílias novas.

**Binding stop rule:** Se V2 produzir 0 PASS ao final dos 8 Leads, Plano A
é **abandonado permanentemente** (sem V3). Contrato em `project_plano_a_v2_last_attempt.md`.

**Branch:** `phase3.5a-v2/plano-a-last-attempt-20260418`

---

## 📌 Mandate constraints (V2-específico — override §7 registrado)

1. **Path tag obrigatório:** `[SHORT-HOLD CFD]` em todo jornada.
2. **Broker:** Pepperstone cTrader (custos Razor: spread 2-5bps half ×2 +
   commission $3.50/side + slippage 1-3bps + swap 0.005-0.02%/dia).
3. **Hold mediano ≥ 3 days** (V2 CORRIGIDO — oposto de V1). Carver
   `[systematic_trading, p.185-188]`: para retail com spread+commission
   dominantes, holds de 1-4 semanas é o ótimo.
4. **Timeframe livre:** daily, 4h, weekly — qualquer granularidade que
   passe os gates. **Proibido 1h intraday** (V1 refutou 108 runs).
5. **Universe ≥ 30 instrumentos multi-asset CFDs** (40 disponíveis em
   Tiingo daily cache — ver spec §2).
6. **5-gate framework + winner criteria acumulativos:**
   - PBO < 0.5 `[advances_fin_ml, p.208-211]`
   - DSR p-value < 0.05 `[advances_fin_ml, ch.14]`
   - WF ≥ 6/8 profitable windows
   - OOS Sharpe > 0, FWD stress > 0, Bootstrap 99.9% CI low > 0
   - **CAGR OOS net ≥ 30%** (> Plano B 25.56%)
   - **Sharpe OOS net ≥ 2.0**
   - **MaxDD OOS ≤ 25%** (2× Plano B 10.86%)
   - **Median hold ≥ 3 days**
7. **Citação obrigatória** `[book.slug, p.X]` em toda decisão técnica.

---

## 🚫 Winners IMUTÁVEIS (não modificar)

**Plano B (Phase 3.5b) — production, NÃO TOCAR:**
- `src/ai_trade/backtest/strategies/letf_rotation.py`
- `src/ai_trade/backtest/strategies/tsmom.py`
- `src/ai_trade/backtest/grid/portfolio_3leg.py`
- `src/ai_trade/helpers/synthetic_letf.py`
- `src/ai_trade/backtest/metrics/rebalance_modes.py`

**Plano A baseline (NÃO modificar):**
- `src/ai_trade/backtest/strategies/bollinger_mr.py`
- `src/ai_trade/helpers/momentum.py`

**Infra reusável (NÃO duplicar):**
- `src/ai_trade/backtest/metrics/standard_report.py`
- `src/ai_trade/backtest/sweeps/registry.py` (fan-out helpers)

---

## Goal — Phase 3.5a-V2

Executar `specs/phase_3_5a_v2.md` Leads V2-L0 → V2-L7 em ordem via fan-out
loop. **T7 aplica verdict final** + flip `status: done`. Se winner found,
append em `winners_short_hold:`. Se 0 PASS, escreve jornada abandono +
mandate §7 formal.

---

## Execution mode — SWEEP_MODE=fanout (ACTIVE)

Ler `docs/self_improvement/fanout_protocol.md` antes de trabalhar em qualquer
lead `[sweep-*]`. Helpers: `ai_trade.backtest.sweeps.registry`.

Leads `[atomic]` continuam legacy (1 iter = 1 lead).

Pointer contract: `active_lead_registry:` frontmatter é `null` quando
nenhum sweep está em andamento, ou aponta para
`reports/phase3_5a_v2/<lead_slug>/registry.json`.

---

## Phase 3.5a-V2 Leads (ACTIVE — execute IN ORDER, consume one per iter)

### V2-L0 — Universe screener [atomic]
- Construir `data/universe_plano_a_v2.json` com metadata (first_dt, last_dt, vol_252d, hurst_100d, corr_spy).
- Validar Tiingo coverage (≥30 hits).
- Output: manifest + `reports/phase3_5a_v2/L0_universe_screener.md`.
- Citation: `[advances_fin_ml, ch.2]` + `[systematic_trading, p.~90-100]`.

### ~~V2-L1~~ — TSMOM multi-asset daily [sweep-configs] ❌ DEAD END (iter 14)
- **CONSUMED 2026-04-18 iter 14 — 0/12 PASS.** Jornada
  `2026-04-18-1945-phase3.5a-v2-L1-tsmom-DEAD.md`.

### ~~V2-L2~~ — Gayed LETF rotation transportada CFD [sweep-configs] ★ PASS (iter 43)
- **CONSUMED 2026-04-19 iter 43 — aggregator PASS.** Winner `gayed_ema100_L2_off_gld`
  appended to `winners_short_hold:`. AGGREGATE in
  `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md`.
  Jornada `2026-04-19-0020-phase3.5a-v2-L2-gayed-transported-PASS.md`.

### ~~V2-L3~~ — AFML triple-barrier + meta-labeling [sweep-tickers] ❌ DEAD END (iter 57)
- **CONSUMED 2026-04-19 iter 57 — 0/12 tickers PASS 5-gate.** Best XLF Sharpe OOS 1.21 / CAGR 2.5% (≪30%). AGGREGATE `reports/phase3_5a_v2/v2_l3_afml_triple_barrier_meta/AGGREGATE.md`. Jornada `2026-04-19-0115-phase3.5a-v2-L3-afml-triple-barrier-DEAD.md`.

### ~~V2-L4~~ — Carver risk-parity multi-strategy [atomic] ❌ DEAD (iter 58)
- **CONSUMED 2026-04-19 iter 58 — blend OOS Sharpe 1.856 / CAGR 16.14% / MDD -8.44%** (vol-target 15% + equal-weight sobre best-OOS-Sharpe de cada L1+L2+L3). Core AFML gates PASS (PBO 0.000, DSR p 0.0014, WF 7/8, boot99.9 0.489) mas **falha 3 winner criteria** (CAGR < 30%, Sharpe < 2.0, IR SPY 0.11 < 0.5). Diagnóstico 2-leg L2+L3: S=2.021/CAGR=25.77% (ainda falha CAGR). Winner Plano A continua sendo `gayed_ema100_L2_off_gld` standalone. AGGREGATE `reports/phase3_5a_v2/v2_l4_carver_risk_parity/`. Jornada `2026-04-19-0215-phase3.5a-v2-L4-carver-blend-DEAD.md`.

### ~~V2-L5~~ — Equity pairs daily [sweep-tickers] ❌ DEAD END (iter 66)
- **CONSUMED 2026-04-19 iter 66 — 0/6 pares cointegrados (ADF p > 0.05).** Best: XLF_HYG p=0.0746 (β 2.67 anômalo). 0 trades todos pares. AGGREGATE `reports/phase3_5a_v2/v2_l5_equity_pairs/AGGREGATE.md`. Jornada `2026-04-19-0310-phase3.5a-v2-L5-equity-pairs-DEAD.md`.

### ~~V2-L6~~ — Vol breakout multi-asset daily [sweep-configs] ❌ DEAD END (iter 80)
- **CONSUMED 2026-04-19 iter 80 — 0/12 configs subset-PASS, 12/12 OOS Sharpe NEGATIVA** (range −0.728 → −0.217). Best `vol_donch20_atr3x_long` OOS S −0.217 / CAGR −1.8% / FWD +1.527. Long-only > L/S por 0.35-0.40 Sharpe (UNG short bleed + TLT/HYG hike-cycle). Lookback/exit indiferentes. Regime OOS 2022-2024 letal: bear curto + recovery rápido + range tech-narrow + 3 correções 2024 = whipsaw. AGGREGATE `reports/phase3_5a_v2/v2_l6_vol_breakout/AGGREGATE.md`. Jornada `2026-04-19-0410-phase3.5a-v2-L6-vol-breakout-DEAD.md`.

### ~~V2-L7~~ — Summary + verdict + flip done [atomic] ★ WINNER FOUND (iter 81)
- **CONSUMED 2026-04-19 iter 81 — WINNER FOUND (1 PASS / 5 DEAD).** Cross-lead AGGREGATE `reports/phase3_5a_v2/AGGREGATE.md` + jornada `2026-04-19-0510-phase3.5a-v2-summary-WINNER-FOUND.md` + mandate §7 entry V2-verdict + `specs/phase_4_paper_trading.md` drafted. Stop rule NÃO disparou (1 PASS ≥ 1 requerido). Plano A retido como 2ª perna ativa. status flip `done`.

---

## Iter budget

- V2-L0: 1 | V2-L1: 14 | V2-L2: 29 | V2-L3: 14
- V2-L4: 1 | V2-L5: 8 | V2-L6: 14 | V2-L7: 1
- **Total esperado:** 82 iters (MAX_ITER=80 → corte marginal ~2 iters)

ETA ~7h autônomas com Opus 4.7.

---

## Constraints invioláveis (HARD)

1. **Pytest ≥ 765 passed.** Novos testes bem-vindos; nunca reduzir.
2. **NÃO tocar** Plano B strategies (5 arquivos acima) nem BollingerMR seed.
3. **NÃO duplicar** `standard_report.py` nem `sweeps/registry.py`.
4. **NÃO push origin nem mexer em main.** Loop auto-commit na branch V2.
5. **Citação `[book.slug, p.X]`** obrigatória em toda decisão.
6. **Atomic writes** (tmp→rename) em registry + per-unit files.
7. **1 unit por iter** em fanout mode. Nunca 2.
8. **Tag `[SHORT-HOLD CFD]`** em todo jornada H1.
9. **Stop rule binding:** T7 aplica verdict sem sugerir V3.
10. **2 iters consecutivas mesmo erro fatal → parar + jornada blocker.**
11. **Fora de escopo (não re-testar):** 1h intraday FX/metais, BollingerMR canonical,
    session-based FX, Kalman pairs em FX, leverage > 5x.

---

## Tools / commands cheatsheet

- Pytest: `.venv/bin/pytest -q`
- Tiingo manifest: `python3 -c "import json; m=json.load(open('data/tiingo/manifest.json')); print(len(m))"`
- Sweep registry helper: `from ai_trade.backtest.sweeps.registry import ...`
- Standard report: `from ai_trade.backtest.metrics.standard_report import ...`
- V1 artifacts (research log, NÃO deletar): `reports/phase3_5a/`, jornadas `2026-04-18-*phase3.5a*.md`
- Spec: `specs/phase_3_5a_v2.md` (leitura obrigatória iter 1)
- Fan-out protocol: `docs/self_improvement/fanout_protocol.md`

---

## Dead ends (do not repeat)

### Do V2

- **V2-L1 TSMOM canonical daily 30-asset multi-asset universe** (0/12 PASS, iter 14 DEAD) — swap drag 74-166% at hold 41-160d, FX 3-pack attractor, FWD 2024-2026 catastrophic. Jornada: 2026-04-18-1407-phase3.5a-v2-L1-tsmom-DEAD.md.
- **V2-L3 AFML triple-barrier + RF meta-label (EMA-50 primary) 12 ETFs daily** (0/12 PASS, iter 57 DEAD) — best XLF Sharpe OOS 1.21/CAGR 2.5% ≪ 30%; RF filter dropa 70-95% eventos → MDD tight mas CAGR ∅; EMA-50 single-asset = primary fino `[advances_fin_ml, p.50]`. Jornada: 2026-04-19-0115-phase3.5a-v2-L3-afml-triple-barrier-DEAD.md.
- **V2-L4 Carver risk-parity L1+L2+L3 atomic blend** (iter 58 DEAD) — blend OOS S=1.856/CAGR=16.14% falha winner criteria apesar de PBO/DSR/WF/boot PASS; L3 flat-hold vol minúscula infla seu peso para 66% e dilui o alpha L2 a 4.9%. Diagnóstico 2-leg (L2+L3) também falha CAGR 30%. Winner Plano A permanece `gayed_ema100_L2_off_gld` standalone. Jornada: 2026-04-19-0215-phase3.5a-v2-L4-carver-blend-DEAD.md.
- **V2-L5 Equity pairs daily Kalman EG 6-pair** (0/6 cointegrated, iter 66 DEAD) — ADF p-values {GLD_SLV 0.192, QQQ_XLK 0.658, SPY_IWM 0.115, TLT_IEF 0.992, XLE_USO 0.511, XLF_HYG 0.0746 closest}; β OLS XLE_USO -0.137 absurdo, XLF_HYG 2.67 anômalo; 0 trades todos pares; universo Pepperstone CFD blue-chip extinto por arb institucional `[algo_trading_chan, p.42]`. Confirma V1-T3 Kalman FX. Winner Plano A intacto. Jornada: 2026-04-19-0310-phase3.5a-v2-L5-equity-pairs-DEAD.md.
- **V2-L6 Vol-breakout Donchian/ATR 1/N multi-asset 10 ETFs daily 12 configs** (0/12 subset-PASS, iter 80 DEAD) — OOS Sharpe NEGATIVA em 12/12 (−0.728 → −0.217); long-only ≫ L/S (UNG short −64% em 2022, TLT/HYG hike-cycle); lookback {20,50,100} e exit {ATR 3×, opp channel} indiferentes; FWD 2025-2026 +0.6 a +1.95 não recupera OOS. Regime 2022-2024 = bear curto + recovery rápido + tech-narrow leadership + 3 correções 2024 = whipsaw letal `[trend_following_covel, ch.4]`. Edge Plano A confirmado **regime-driven** (Gayed-class), não breakout puro. Jornada: 2026-04-19-0410-phase3.5a-v2-L6-vol-breakout-DEAD.md.

### Do V1 (consolidado — todas as famílias testadas em 1h FX/metais)

- **BollingerMR canonical 20/2σ em FX/metais 1h** (T1, 0/36 PASS).
- **Donchian 10/5 + 20/10 + ATR-Chandelier em FX/metais 1h** (T2, 0/36 PASS).
- **Kalman pair-trade em FX pairs 1h** (T3, 0/18 PASS). Equity pairs continuam open em V2-L5.
- **Session-based FX (ORB + NY-MR + Asian fade) 1h** (T4, 0/18 PASS).
- **Regime-filter linear sobre BollingerMR 1h** (T5, 0/30 PASS).
- **Ceiling Plano A 1h** = BollingerMR GARCH SPY 1h L=2 (CAGR 5.9% net). Não retestar.
- **Leverage > 5x** (V1 A1 jornada): PoR > 50%, ruína empírica. Não explorar.
- **Universe gaps Tiingo:** índices CFD spot (DE40/UK100/JP225/SPX500/NAS100) todos 404. FX pre-2020 API 400. Tiingo 1h limite cap.

### Do Phase 3 (herdado)

- Ehlers BP Swing 24-config em 16 ativos ETF/equity/commodity/bond/crypto (0/16 PASS).
- Clenow momentum unmodified em yfinance SPX 2015-2023.

---

## Phase B leads (após Phase A completar)

Se V2 encontrar winner: Phase B = test/optimize/validate winner (cost ablation,
multi-asset transport wider, GARCH vol-sizing, CI bootstrap 99.9%).

Se V2 abandonar Plano A: Phase B **não existe** para A. Phase 3.5b refinement
+ Phase 4 paper trading assumem Plano B puro.

---

## History

- iter 81 — ★★★ **V2-L7 ATOMIC VERDICT — WINNER FOUND, PHASE 3.5a-V2 CLOSED**. 82 iters / 58 runs / 6 famílias → 1 PASS (gayed_ema100_L2_off_gld) / 5 DEAD structural. Cross-lead AGGREGATE, jornada final, mandate §7 entry, Phase 4 spec drafted. Stop rule NÃO disparou. Plano A retained. status: done.
- iter 80 — V2-L6 AGGREGATOR DEAD: 0/12 subset-PASS, **12/12 OOS Sharpe NEGATIVA** (range −0.728 → −0.217). Best long-only `vol_donch20_atr3x_long` OOS −0.217 / FWD +1.527. Long-only > L/S por 0.35-0.40 Sharpe; lookback/exit indiferentes; regime OOS 2022-2024 letal. AGGREGATE escrito, registry status=done, pointer cleared.
- iter 79 — V2-L6 sweep `vol_donch100_opp_ls` FINAL config: IS 0.237 / OOS −0.550 / FWD 0.945, MedHold 52.2d, WF FAIL (0.75, maxDD 26.8%). 12/12 done, registry → `aggregating`.
- iter 78 — V2-L6 sweep `vol_donch100_opp_long`: IS 0.683 / OOS −0.238 / FWD 1.064, hold 56.8d, WF PASS, subset 4/7. Longest hold of suite.
- iter 77 — V2-L6 sweep `vol_donch100_atr3x_ls`: IS 0.239 / OOS −0.644, WF FAIL (0.62, DD 25.1%), UNG short −2.93× bleed.
- iter 76 — V2-L6 sweep `vol_donch100_atr3x_long`: IS 0.630 / OOS −0.279 / FWD 1.318, WF PASS (0.88, DD 9.9% tightest), subset 4/7.
- iter 43 — ★★★ **V2-L2 AGGREGATOR PASS — 1º Plano A WINNER**. `gayed_ema100_L2_off_gld`: OOS S=2.285/CAGR 79.14%/MDD −21.02%/hold 6d; FWD 1.821. PBO 0.103, DSR p=0.000288, 99.9%CI low 0.962, WF 8/8, IR-SPY 2.16. Appended `winners_short_hold`. Jornada 2026-04-19-0020.
- iter 1-42 — pruned; facts em `## Dead ends` + jornadas 2026-04-18-1407/1545/2026-04-19-0020.
