# [SHORT-HOLD CFD] Phase 3.5a — T7 Summary: encerramento + recomendação abandono Plano A

**Data:** 2026-04-18 ~22:00 BRT
**Path:** A (Pepperstone CFD short-hold) — fechamento Phase 3.5a
**Phase:** 3.5a — investigação Plano A V2 (Lead T7 atomic, **final**)
**Iteração do loop:** 42
**Verdict:** **NO-GO formal Plano A V2.** Recomendação endossada: **Opção B
— abandonar Plano A + re-alocar 5pp via mandate §4.7**. Decisão sujeita
a ratificação user; `memory.md status: done` flipado ao final desta iter.

---

## TL;DR

Phase 3.5a (Plano A V2) executou **7 Leads / 42 iterações / 143 runs /
6 famílias de strategy / 18 ativos Tiingo IEX** e produziu **zero
winners novos**. Único survivor permanece o baseline Phase 3
(BollingerMR_GARCH SPY 1h L=2, CAGR **5.9%/yr net**), que já estava no
`winners_short_hold` antes da Phase 3.5a começar. Esse ceiling é **5–10×
menor que o target mandate §2** (60–120%/yr) e **4.3× menor que Plano B**
(25.56%/yr). A hierarquia mandate §1 *A > B* é empiricamente
irrealizável com o stack atual.

User memory explícita (`project_plano_a_v2_last_attempt.md`) já
autorizava o pivô: *"if Phase 3.5a-V2 fails, abandon Plano A entirely;
no V3, focus on refining Plano B only"*. Phase 3.5a é a V2; V2 falhou.
Mandate §4.7 já contempla o abandono: *"Se Strategy A não produzir
winner em Phase 3, re-alocar os 5 pts de volta para o bucket passive"*.
T7 formaliza o pivô via checklist de arquivamento + handoff Phase 4
Plano B puro.

---

## 1. Lead-by-lead verdict (Phase 3.5a completo)

| Lead | Escopo | Runs | PASS | Dia | Jornada | Verdict |
|------|--------|-----:|-----:|-----|---------|:-------:|
| **T0** | Tiingo FX/metais bulk pull (12 tickers daily+1h) | — | — | 2026-04-18 | `2026-04-18-0105-phase3.5a-T0-tiingo-fx-pull.md` | ✅ DONE (infra) |
| **T1** | BollingerMR canonical 20/2σ × 12 FX/metais 1h × 3 dir | 36 | 0 | 2026-04-18 | `2026-04-18-0130-phase3.5a-T1-bollinger-mr-fx-metals-DEAD.md` | 💀 DEAD |
| **T2** | Donchian 10/5 + 20/10 + ATR-Chandelier × 12 tickers 1h | 36 | 0 | 2026-04-18 | `2026-04-18-1500-phase3.5a-T2-donchian-breakout-DEAD.md` | 💀 DEAD |
| **T3** | Pair-trade OLS + Kalman × 6 pares 1h | 18 | 0 | 2026-04-18 | `2026-04-18-1420-phase3.5a-T3-pairs-statarb-DEAD.md` | 💀 DEAD |
| **T4** | Session-based FX (ORB, NY-MR, Asian-fade) × 6 FX 1h | 18 | 0 | 2026-04-18 | `2026-04-18-1545-phase3.5a-T4-session-based-fx-DEAD.md` | 💀 DEAD |
| **T5** | Regime-filter hybrid BollingerMR × 5 configs × 6 ativos 1h | 30 | 0 | 2026-04-18 | `2026-04-18-1800-phase3.5a-T5-regime-filter-hybrid-DEAD.md` | 💀 DEAD |
| **T6** | Rebalance meta + mandate §7 override | 0 | — | 2026-04-18 | `2026-04-18-2100-phase3.5a-T6-rebalance-meta-mandate-override.md` | 📝 META |
| **T7** | **Summary + flip done (este)** | 0 | — | 2026-04-18 | este arquivo | ✅ CLOSED |
| — | **TOTAIS 3.5a** | **138** | **0** | — | — | — |
| — | **+ seed Phase 3 (A1/A3a)** | **+5** | **+1 baseline** | — | — | — |
| — | **CROSS-LEAD TOTAL** | **143** | **1 (baseline)** | — | — | — |

---

## 2. Comparativo pré/pós-3.5a

### 2.1 Universo explorado

| Dimensão | Pré-3.5a (Phase 3 fechado) | Pós-3.5a (este summary) |
|----------|----------------------------|-------------------------|
| Tickers equity | SPY, XLF (fail transport) | + QQQ testado em T5 (fail) |
| Tickers FX | 0 | **12** majors/crosses daily + 1h (2020-2026) |
| Tickers metais | 0 | **2** (XAUUSD, XAGUSD, 1h) |
| Tickers índices CFD | — | **5 tentados, 5 404** (DE40/UK100/JP225/SPX500/NAS100) |
| Famílias strategy | 1 (BollingerMR) | **6** (BMR, Donchian, ATR-Chandelier, pairs/Kalman, session FX, regime-hybrid) |
| Granularidades | daily + 1h | 1h only (Tiingo IEX ceiling) |
| Gates | 5-layer PBO/DSR/WF/OOS/FWD | idem + bootstrap CI 99.9% |

### 2.2 Gates fail/pass (somente 3.5a, excluindo seed)

| Gate | Fail | Pass | Taxa pass |
|------|-----:|-----:|:---------:|
| Hold ≤ 5 d | 0/138 | **138/138** | 100% |
| PBO < 0.5 | ~18 | ~15 (pontuais) | ~45% |
| DSR p < 0.05 | 138 | **0** | **0%** |
| WF ≥ 6/8 | 138 | **0** | **0%** |
| OOS Sharpe > 0 | ~120 | ~15 | ~11% |
| FWD Sharpe > 0 | ~110 | ~28 | ~20% |
| **All 5 simultâneos** | **138** | **0** | **0%** |

Leitura: o único gate *saudável* na 3.5a é o hold ≤ 5d (100% pass — as
families escolhidas são de fato short-hold). Todos os demais degradam
simultaneamente por **friction Razor + regime decay pós-2023 + universe
gaps**. DSR e WF têm taxa de pass absoluta zero em 138 runs — sinal
inequívoco de que nenhuma família testada atravessa o crivo Phase 3.5a.

### 2.3 Deltas de conhecimento absorvido

| Lição | Status pré | Status pós |
|-------|-----------|------------|
| FX 1h Razor-tier tem edge em MR clássico? | Conjectura | **Refutada** (T1: 0/36 PASS) |
| Breakout 1h (Donchian/ATR) salva FX? | Conjectura | **Refutada** (T2: 0/36 PASS) |
| Pair-trade 1h sobrevive custos 2-legs? | Conjectura | **Refutada** (T3: 0/18 PASS, hold violated) |
| Session structure FX extrai edge Razor? | Conjectura | **Refutada** (T4: 0/18 PASS, edge 3-8 bps < piso 5-10 bps) |
| Regime filter linear ressuscita MR? | Conjectura | **Refutada** (T5: 0/30 PASS, filtros achatam sem inverter) |
| 1h FX/metais/equity Razor-tier é "mercado morto" para strategies clássicas? | Hipótese | **Empiricamente confirmada** (102 runs 1h, 0 winner) |
| Tiingo fornece universe Pepperstone index-CFD? | Assumido | **Falso** (DE40/UK100/JP225/SPX500/NAS100 todos 404) |
| FX pré-2020 disponível via Tiingo? | Assumido | **Falso** (API 400 startDate < 2020) |
| Ceiling empírico Plano A (SPY 1h L=2) | Sharpe 0.945 | **Confirmado** (nenhuma família superou) |

---

## 3. Recomendação formal — Opção B (abandono Plano A)

### 3.1 Justificativa consolidada

| Eixo | Evidência |
|------|-----------|
| **Empírica** | 143 runs / 6 famílias / 0 winners novos. Ceiling 5.9%/yr é 5–10× menor que §2 target e 4.3× menor que Plano B. |
| **Arquitetural** | Tiingo IEX 1h + universe gaps + Razor friction = 3 constraints estruturais simultâneos, nenhum removível no escopo atual. |
| **User-explicit** | `project_plano_a_v2_last_attempt.md`: *"no V3, focus on refining Plano B only"*. Phase 3.5a é a V2 explicitamente. |
| **Mandate-consistent** | §4.7 literalmente prevê: *"Se Strategy A não produzir winner em Phase 3, re-alocar os 5 pts de volta para o bucket passive"*. |
| **Opcionalidade preservada** | Baseline BollingerMR_GARCH SPY 1h permanece arquivado como research-artifact. Pode ser revisitado se (a) Tiingo expandir universe, (b) user autorizar V3 explicitamente, (c) nova família ML-driven for proposta. |

### 3.2 Checklist de arquivamento (T7 → Phase 4 handoff)

Ações mecânicas para ratificar pós-aprovação do user. **T7 NÃO
executa** as seções ⚠️ marcadas — elas exigem confirmação humana
antes (respeita `feedback_autonomous_technical_decisions` — sub-decisões
de implementação são automáticas, decisões de alocação e pivot mandate
ficam pro user ratificar).

- [x] Override §7 em `docs/investment-mandate.md` executado em T6 (iter 41).
- [x] Ceiling empírico documentado em 4 artefatos (memory + T6 jornada + README index + esta T7).
- [x] `winners_short_hold:` preserva BollingerMR_GARCH SPY 1h L=2 como registro histórico (NÃO deletar).
- [x] `active_lead_registry: null` em memory.md (T5 aggregator limpou).
- [x] Pytest 765 preservado — zero regressão.
- [ ] ⚠️ **User ratifica** Opção B via leitura deste T7 + T6. Se Opção A for preferida, abrir Phase 3.5a' com target ≥ CDI e estratégia de refinamento (BollingerMR_GARCH vol-sizing ou meta-label AFML) — mas isso **contraria** `plano_a_v2_last_attempt` e reabre V3.
- [ ] ⚠️ **Re-alocação §4.7** (pós-ratificação): mover 5pp Path A → Path B (25+5 = 30pp) OU Path A → passive (bucket ativo cai para 25pp). Decisão operacional: 30pp Path B 3-leg daily é preferível (mantém exposure alavancado uncorrelated + evita subir passive que já é 65-80%). Escrever em `docs/phase3_winners_allocation.md` pós-ratificação.
- [ ] ⚠️ **ROADMAP.md update**: Phase 4 remove Plano A branch; Phase 3.5a marcada closed com link para este T7. Phase 4 = paper trading + live Plano B puro (SSO+QQQ+GLD daily threshold 5pp).
- [ ] ⚠️ **cTrader OAuth + threading Phase 4 infra**: arquivar (não deletar) em `src/ai_trade/broker/ctrader/` sob `_archive/` ou flag `DISABLED_PLANO_A_ABANDONED`. Avaliar remoção de dependencies cTrader no `pyproject.toml` só se nenhuma nova iniciativa depender.
- [x] `src/ai_trade/backtest/strategies/bollinger_mr.py` preservado (imutável per memory.md).
- [x] `src/ai_trade/helpers/momentum.py` preservado (seed BollingerMR).
- [x] Reports Phase 3.5a preservados (`reports/phase3_5a/t1...t5/AGGREGATE.md`) — research log completo.

### 3.3 O que NÃO muda

- **Plano B 3-leg EW daily (SSO+QQQ+GLD, threshold 5pp)** permanece o
  production default. Sharpe 2.108, CAGR 25.56%, MaxDD 10.86%.
- **Bucket passivo** (60-80%) permanece dominante; re-alocação proposta
  é apenas dentro do bucket ativo (20-40%) ou marginal pro passivo.
- **Skill knowledge base** (`knowledge/SKILL.md`, 34 livros) permanece
  intacta — aprendizado é permanente mesmo com strategy abandonada.
- **Gates framework 5-layer** (PBO/DSR/WF/OOS/FWD + bootstrap CI)
  permanece o padrão; provou-se efetivo ao rejeitar 138/138 fraudes.
- **User memories + feedback** permanecem autoritativos.

---

## 4. Handoff Phase 4 — Plano B puro

Recomendação operacional (pós-ratificação):

1. **Phase 4.1 — Paper trading** do 3-leg EW daily em conta real BR
   (~$10k equivalente). Threshold rebalance 5pp, monitor ρ 252d,
   alertar se 3 ρ ≥ 0.70 por ≥ 10 barras.
2. **Phase 4.2 — Threading model** simplificado (antes: 1 thread/asset
   per Plano A multi-asset; agora: 1 processo daily EOD para Plano B).
3. **Phase 4.3 — Live deploy** gradual ($10k → $50k → alocação total).
4. **Phase 4.4 — Monitoria contínua** de regime-break signals (ρ,
   VIX, SPY 200-SMA cruzamentos).

**Explicitamente removido do escopo Phase 4:** cTrader OAuth, leverage
sweep infra, universe pre-screener Hurst/ATR/spread/volume,
threading 1-thread-por-ativo. Todos eram pré-requisitos Plano A.

**Mantido no escopo Phase 4:** Tiingo daily cache (SSO/QQQ/GLD),
`standard_report.py`, gates 5-layer (re-aplicados ao Plano B como
contínua verificação pós-deploy), CI/CD + pytest 765+.

---

## 5. Citações finais

- **Gate framework 5-layer** (validou todas as rejeições 3.5a):
  `[advances_fin_ml, p.196-211]` (DSR+PBO), `[advances_fin_ml, ch.7]`
  (CPCV), `[advances_fin_ml, p.275-278]` (correlation structure).
- **Hold ≤ 5d como proxy swap**: `[systematic_trading, p.185-188]`.
  Gate respeitado 138/138 runs — o problema não é hold, é edge ausente.
- **Friction consome MR/breakout sub-daily**: `[machine_trading,
  p.204-205]`, `[algo_trading_chan, p.28-30, ch.2]`.
- **Leverage cap + fat-left-tail**: `[leverage_space, Vince]`,
  `[math_money_mgmt, Vince]`. L=2 empírico ótimo em SPY 1h, L≥5 PoR-fail.
- **Plano B tese LETF rotation** (que SE MANTÉM em produção):
  `[leverage_for_the_long_run, p.7-8, p.21]` (Gayed 2016/2020 LRS +
  vol-vs-leverage).
- **Pair-trade fundamentals** (T3 rejeição): `[algo_trading_chan,
  p.42-54, ch.2]` (ADF Engle-Granger), `[algo_trading_chan,
  p.71-80, ch.3]` (Bollinger pair + Kalman).
- **Session-based FX intraday** (T4 rejeição):
  `[quant_trading_chan, p.43-53, ch.2-3]`.
- **Donchian/ATR breakout** (T2 rejeição):
  `[trading_systems_methods, p.353]` (Donchian), `[volatility_trading]`
  (ATR-Chandelier).
- **Regime-aware features** (T5 rejeição): `[advances_fin_ml, ch.17]`
  (lição: hard-gate linear não captura regime não-linear).

---

## 6. Artefatos finais

**Jornadas Phase 3.5a (ordenadas, read-only):**

1. `2026-04-18-0105-phase3.5a-T0-tiingo-fx-pull.md` — T0 infra
2. `2026-04-18-0130-phase3.5a-T1-bollinger-mr-fx-metals-DEAD.md` — T1
3. `2026-04-18-1500-phase3.5a-T2-donchian-breakout-DEAD.md` — T2
4. `2026-04-18-1420-phase3.5a-T3-pairs-statarb-DEAD.md` — T3
5. `2026-04-18-1545-phase3.5a-T4-session-based-fx-DEAD.md` — T4
6. `2026-04-18-1800-phase3.5a-T5-regime-filter-hybrid-DEAD.md` — T5
7. `2026-04-18-2100-phase3.5a-T6-rebalance-meta-mandate-override.md` — T6 meta
8. `2026-04-18-2200-phase3.5a-T7-summary-close-PLANO-A-abandoned.md` — T7 (este)

**Reports agregados:**

- `reports/phase3_5a/t1_bollinger_mr_fx_metals{_long,_short}/`
- `reports/phase3_5a/t2_donchian_breakout/AGGREGATE.md`
- `reports/phase3_5a/t3_intraday_pairs_statarb/`
- `reports/phase3_5a/t4_session_based_fx/`
- `reports/phase3_5a/t5_regime_filter_hybrid/AGGREGATE.md`

**Baselines preservados (imutáveis):**

- `src/ai_trade/backtest/strategies/bollinger_mr.py`
- `src/ai_trade/helpers/momentum.py`
- `src/ai_trade/backtest/strategies/letf_rotation.py` (Plano B)
- `src/ai_trade/backtest/strategies/tsmom.py` (Plano B)
- `src/ai_trade/backtest/grid/portfolio_3leg.py` (Plano B)
- `src/ai_trade/helpers/synthetic_letf.py` (Plano B)
- `src/ai_trade/backtest/metrics/rebalance_modes.py` (Plano B)
- `src/ai_trade/backtest/metrics/standard_report.py` (infra comum)

**Metrics ambiente no fechamento:**

- Pytest: **765 passed** (baseline +256 vs Phase 2.5 post-cleanup).
- Branch: `phase3.5a/plano-a-short-hold-20260418` (não merged, auto-commit loop).
- Memory.md: `status → done` flipado nesta iter.

---

## 7. Encerramento

Phase 3.5a encerra em **42 iterações totais** (1 T0 bootstrap + 32 T1-T5 sweep
unitário + 3 T2/T5 aggregators + 6 T1 long/short aggregators inline + 1 T6
atomic + 1 T7 atomic). Cross-lead com Phase 3 (iter 0-9), **51 iters
consumidas** para convergir ao verdict final: **Plano A short-hold CFD
não alcança retorno > Plano B com o stack atual (Tiingo IEX 1h + Razor-tier
friction + universe limitado).**

Next steps bloqueados por ratificação user:

1. Confirmar Opção B (default recomendado) ou Opção A (requer V3,
   viola user memory explícita).
2. Autorizar re-alocação §4.7 (5pp Path A → 25pp Path B = 30pp total).
3. Autorizar arquivamento cTrader/Pepperstone infra.
4. Abrir Phase 4 com escopo revisado (Plano B puro + paper trading).

Sem ratificação, repositório permanece no estado atual: winners B em
produção, winner A baseline-only em `winners_short_hold` como
research-artifact, Phase 3.5a `status: done` mas sem ação operacional.

**Loop autônomo self-improve: encerrado nesta iter 42.**
