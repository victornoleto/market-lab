# [SHORT-HOLD CFD] Phase 3.5a — T6 Rebalance meta Plano A: mandate override §7

**Data:** 2026-04-18 ~21:00 BRT
**Path:** A (Pepperstone CFD, short-hold ≤ 5 dias) — meta task, cross-lead
**Phase:** 3.5a — investigação Plano A (Lead T6 atomic)
**Iteração do loop:** 41
**Verdict:** Meta mandate target 5–10%/mês **empiricamente inviável**
com o universo Tiingo IEX 1h + famílias MR/breakout/pair/session/regime
testadas. Override §7 registrado. Decisão de abandono preservada para T7.

---

## TL;DR

Phase 3 + Phase 3.5a juntas investigaram **5 famílias de strategy ×
12 + 6 tickers + 30 configs = 102 runs 1h**, fora a baseline original
BollingerMR_GARCH SPY 1h. **0 winners novos.** O ceiling empírico de
Plano A é a própria baseline (BollingerMR_GARCH SPY 1h L=2, CAGR 5.9%
net / 10.76% raw pre-GARCH/friction ajuste, OOS Sharpe 0.945, MaxDD
−34.1%) — **5× menor que a meta §2** (60–120%/yr) e **4.3× menor que
Plano B** (25.56%/yr, 3-leg EW). A hierarquia mandate §1 *A > B* é
matematicamente irrealizável neste universe/search budget.

T6 registra (a) o ceiling empírico, (b) o gap vs mandate, (c) a
override §7 propondo duas rotas (downshift de target **ou** abandono
Plano A + re-alocação §4.7). Decisão final de abandono fica delegada
ao Lead T7 (summary) + user buy-in; T6 apenas documenta o pivô
necessário.

---

## 1. Universo testado Phase 3 + 3.5a

| Lead | Família | Universo | Runs | PASS | Status |
|------|---------|----------|-----:|-----:|:------:|
| A1 (Phase 3) | BollingerMR + leverage sweep | SPY 1h | 5 | 1 (L=2) | ★ BASELINE |
| A3a (Phase 3) | BollingerMR transport | XLF 1h | 1 | 0 | DEAD |
| T0 (3.5a) | Tiingo FX/metals bulk | 12 tickers daily+1h | — | — | DONE |
| T1 (3.5a) | BollingerMR canonical | 12 FX/metals 1h (3 dir × 12) | 36 | 0 | DEAD |
| T2 (3.5a) | Donchian 10/5 + 20/10 + ATR-Chandelier | 12 FX/metals 1h | 36 | 0 | DEAD |
| T3 (3.5a) | Pair-trade OLS + Kalman | 6 pares FX/equity 1h | 18 | 0 | DEAD |
| T4 (3.5a) | Session-based FX (ORB/NY-MR/Asian) | 6 tickers FX 1h | 18 | 0 | DEAD |
| T5 (3.5a) | Regime-filter hybrid sobre BollingerMR | 6 ativos mistos 1h | 30 | 0 | DEAD |
| **Total** | 5 famílias + seed | 12 FX + 5 equity + 1 metal | **143** | **1** | — |

Único survivor: **BollingerMR_GARCH SPY 1h L=2** (frozen baseline,
imutável per memory.md).

---

## 2. Ceiling empírico Plano A

### 2.1 Baseline BollingerMR_GARCH SPY 1h (post-Phase 3)

| Métrica | Valor | Fonte |
|---------|------:|-------|
| Sharpe IS | 0.995 | memory.md winners_short_hold |
| Sharpe OOS | 0.945 | idem |
| CAGR net (GARCH sizing + Pepperstone costs) | **5.9%/yr** | idem |
| CAGR raw (leverage sweep L=2, pre-GARCH adjustment) | 10.76%/yr | `2026-04-16-2310-a1-leverage-sweep-bollinger-mr-spy-1h.md` |
| MaxDD (L=2 raw) | −34.1% | A1 jornada |
| Leverage ótimo empírico | **L=2** | A1 jornada — L=5 fura DD, L=10 PoR 99.8%, L=20 ruína |
| Hold mediano | ≤ 5 d | Phase 3 gates verified |
| Multi-asset transport (A3a) | ❌ XLF fail | `2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md` neighbourhood |

**Ceiling empírico = CAGR ∈ [5.9%, 10.76%]/yr dependendo de como GARCH
sizing + Pepperstone Razor stack (5–7 bps × 200–500 trades/ano) são
aplicados.** Mesmo no upper-bound raw, fica abaixo do target mandate
§2 Plano A em **5.6–10.8×**.

### 2.2 Gap vs mandate atual

| Target | CAGR |
|--------|-----:|
| Mandate §2 Plano A (target) | **60–120%/yr** (5–10%/mês) |
| Mandate §2 benchmark mínimo (CDI BR) | 13–14%/yr |
| Plano B atual (3-leg EW) | **25.56%/yr** OOS |
| Plano A ceiling empírico (BMR_GARCH SPY 1h L=2 net) | 5.9%/yr |
| Plano A ceiling empírico (raw, leverage-max-gate) | 10.76%/yr |
| Hierarquia mandate §1 (A > B) implica A ≥ | ~29%/yr |

**Conclusão numérica:** Plano A ceiling 5.9% < CDI 13–14% < Plano B
25.56% < hierarchy-target 29% < mandate §2 Plano A 60%. **4 ordens
de grandeza separam o achievable do prescrito.**

---

## 3. Causas raíz (por que não conseguimos)

1. **Granularidade Tiingo IEX 1h é a fronteira.** 1h Razor-tier spread
   (5–7 bps round-trip em FX, 10 bps em metais) consome MR/breakout/
   pair/session/regime edges quando trade-count cresce pra ≥ 150–300/yr
   (trades_oos × 2 bps ≈ 3–6% drag no CAGR, que é maior que o edge).
   Documentado cross-lead em T1+T2+T3+T4+T5 (100% fail FX 1h).
   `[systematic_trading, p.185-188]`.
2. **Universe Tiingo gaps conhecidos:** índices spot EU/US (DE40/UK100/
   JP225/SPX500/NAS100) todos 404; FX pré-2020 400; frequência < 1h
   não servida. Isto remove o universe Pepperstone index-CFD
   (`[docs/investment-mandate.md §3.1]` listou SPX500/NAS100 como core
   — Tiingo não fornece). Ver `2026-04-18-0105-phase3.5a-T0-tiingo-fx-pull.md`.
3. **MR/breakout/pair clássico 1h é regime-legacy.** O edge existia
   pre-2020 mas secou pós-2023 em todos os 6 tickers testados em T5
   (OOS Sharpe uniformemente negativo, FWD tambem em 5/6). Regime
   filter linear (SMA/RV/combo) não ressuscita — só achata a perda.
4. **Leverage é o único multiplicador viável, mas cap Pepperstone +
   gate PoR limita a L=2.** Leverage não cria edge (`[leverage_space,
   Vince]`); L=5 fura DD −69.8%, L=10 PoR 99.8%, L=20 ruína intra-
   barra. Cross-check Kelly f/2 satura no cap por fat-left-tail.
   Upper-bound empírico teórico = L=2 × Sharpe 0.945 × σ ≈ 10.76%/yr
   raw — **já atingido**.

**Leitura integrada:** Plano A precisaria de (a) granularidade < 1h
(5m/tick-level news-aware), (b) universe expansion (índices CFD EU +
crypto OHLC tick), (c) família não-linear (meta-labeling AFML ch.18-19
ou ML-driven regime detection) para potencialmente quebrar o ceiling.
Nenhuma está disponível no escopo atual de ferramentas.

---

## 4. Opções de pivot (mandate override)

### Opção A — Downshift target + abandonar hierarquia A > B

- Target NOVO Plano A: **≥ CDI BR (13–14%/yr)** — chão inviolável §2
  preservado.
- Plano A re-framed: **satélite uncorrelated**, não "motor agressivo".
- Sizing Plano A: preservar alocação ~5pp §4.7 (vs re-alocar tudo).
- Justificativa científica: uncorrelation pode ser valiosa mesmo com
  CAGR baixo (`[advances_fin_ml, p.275-278]` — correlation structure).
- Requer: BollingerMR_GARCH SPY 1h passa o novo target (5.9% < 13%),
  então **mesmo esta opção exige um winner novo ou refinamento**.
- Risco: refinamento (vol-sizing, meta-label) abre buraco pra V3 que
  viola a regra do usuário "no V3".

### Opção B — Abandonar Plano A, re-alocar §4.7

- Re-alocar os ~5pp Plano A → **todo vai pra Plano B** (25pp + 5pp =
  30pp) ou **parcial Plano B + parcial passive** (60-80% → 65-85%).
- Justificativa do usuário: memória explícita (`project_plano_a_v2_last_attempt.md`)
  — "if Phase 3.5a-V2 fails, abandon Plano A entirely; no V3, focus on
  refining Plano B only". **Phase 3.5a é a V2.**
- Mandate §4.7 já contempla explicitamente:
  > "Se Strategy A não produzir winner em Phase 3, re-alocar os 5 pts
  > de volta para o bucket passive (total ativo cai para 25 pts)."
- Implicação operacional: cTrader OAuth, threading Phase 4 per-asset,
  leverage sweep infra → **todo o trabalho Plano A é arquivado**.
  BollingerMR_GARCH SPY 1h fica como artefato de pesquisa (mandate §2:
  "Fica registrada como histórico de pesquisa, não como produto").
- Risco: perdemos a opcionalidade de um edge short-hold se mercado
  mudar. Mitigação: opção A pode ser revisitada se (a) Tiingo expandir
  universe, (b) usuario autorizar V3 explicitamente, (c) nova família
  (AFML meta-label, ML regime) for proposta.

### Recomendação T6 → T7

**Opção B é a rota tecnicamente honesta e operacionalmente consistente
com a memória explícita do usuário.** T7 (summary) deve formalizar o
abandono com checklist de arquivamento e handoff pra Phase 4 Plano B
puro. T6 **não flipa o abandono sozinho** — registra o override §7 +
as 2 opções para o usuário ratificar via review do summary T7.

---

## 5. Override mandate §7 (executado nesta iter)

Adicionada linha em `docs/investment-mandate.md` §7 tabela:

> | 2026-04-18 | Phase 3.5a (Plano A V2) encerrada sem winner novo. Ceiling empírico Plano A = BollingerMR_GARCH SPY 1h L=2 CAGR 5.9%/yr net (10.76% raw). 143 runs em 6 famílias + 1h FX/metals/equity universe. Hierarquia §1 A > B empiricamente irrealizável; 2 opções pivot (A — downshift target ≥ CDI; B — abandonar Plano A re-alocar §4.7). Decisão final em T7 summary. | BollingerMR_GARCH SPY 1h foi o único survivor; Tiingo IEX 1h ceiling + Razor-tier friction + regime decay pós-2023 = gap 5–10× vs target §2. Universe Pepperstone index-CFD não-servido por Tiingo (DE40/UK100/JP225/SPX500/NAS100 404). | TBD (iter 41 phase3.5a branch) |

---

## 6. Citações

- Gate framework (PBO/DSR/WF/OOS/stress): `[advances_fin_ml, p.196-211]`.
- Hold-time ≤ 5d como proxy swap: `[systematic_trading, p.185-188]`.
- Friction consumindo MR edge em sub-daily: `[machine_trading, p.204-205]`,
  `[algo_trading_chan, p.28-30, ch.2]`.
- Leverage não cria edge + fat-left-tail cap: `[leverage_space, Vince]`,
  `[math_money_mgmt, Vince]`.
- LRS + volatility-vs-leverage (por que Plano B L=2 funciona e Plano A
  L=5 não): `[leverage_for_the_long_run, p.7-8, p.21]`.
- Correlation as value independent of return (Opção A rationale):
  `[advances_fin_ml, p.275-278]`.

---

## 7. Artefatos

- Jornadas Phase 3.5a consumidas:
  - `2026-04-18-0105-phase3.5a-T0-tiingo-fx-pull.md`
  - `2026-04-18-0130-phase3.5a-T1-bollinger-mr-fx-metals-DEAD.md`
  - `2026-04-18-1500-phase3.5a-T2-donchian-breakout-DEAD.md`
  - `2026-04-18-1420-phase3.5a-T3-pairs-statarb-DEAD.md`
  - `2026-04-18-1545-phase3.5a-T4-session-based-fx-DEAD.md`
  - `2026-04-18-1800-phase3.5a-T5-regime-filter-hybrid-DEAD.md`
- Reports agregados:
  - `reports/phase3_5a/t1_bollinger_mr_fx_metals{_long,_short}/`
  - `reports/phase3_5a/t2_donchian_breakout/AGGREGATE.md`
  - `reports/phase3_5a/t3_intraday_pairs_statarb/`
  - `reports/phase3_5a/t4_session_based_fx/`
  - `reports/phase3_5a/t5_regime_filter_hybrid/AGGREGATE.md`
- Baseline imutável Plano A:
  - `src/ai_trade/backtest/strategies/bollinger_mr.py`
  - `src/ai_trade/helpers/momentum.py` (seed)
  - `2026-04-16-1347-bollinger-mr-garch-spy-1h-PASS.md`
  - `2026-04-16-2310-a1-leverage-sweep-bollinger-mr-spy-1h.md`

---

## 8. Próximo passo

**Lead T7 — Summary Phase 3.5a + flip `status: done`**. Conteúdo:

1. Lead-by-lead verdict table (T0–T6).
2. Comparativo pre/post-3.5a (universo, famílias, gates fail/pass).
3. Recomendação formal Opção B (abandono) com checklist de arquivamento:
   - Arquivar `src/ai_trade/backtest/strategies/bollinger_mr.py` como
     research-artifact (NÃO deletar — permanece para posterior revisit).
   - Sinalizar em `docs/investment-mandate.md` §4.7 que re-alocação 5pp
     A → B está autorizada pós-ratificação user.
   - ROADMAP.md → Phase 4 removes Plano A branch; Phase 3.5a → closed.
4. Handoff Phase 4 Plano B puro (SSO + QQQ + GLD daily, threshold 5pp).
5. Flip `memory.md status: done` após jornada T7 escrita.

Eta T7: 1 iter atômica. Phase 3.5a encerra em **42 iters totais**
(1 bootstrap + 32 sweep + 3 aggregator + T6 atomic + T7 atomic).
