# Phase 3 — Summary (5 leads verdictados) ★ CLOSED

**Tag:** `[SHORT-HOLD CFD]` + `[SWING BROKER]` · **Fase 3:** CLOSED em iter 39 ·
**Decisão overall:** GO para Phase 4 com 2 strategies production-ready
(1 por path) + 1 portfolio blend como Strategy B alvo.

## Por que Phase 3

Winners da Phase 2.5 (BollingerMR GARCH SPY 1h + ETFRotation monthly top-1)
passaram os gates mas ficaram abaixo da meta do Investment Mandate:

- CAGR ~5.9% (BollingerMR) e ~9.1-9.6% (ETFRotation) < CDI BR ~13-14%/ano.
- Strategy A era **single-asset** (SPY-only) quando o mandate exige multi-asset.
- Strategy B não era **LETF-based**, quando o mandate cita
  `[leverage_for_the_long_run]` como base científica ÚNICA.

Phase 3 = 5 leads para fechar esse gap: A1 (leverage sweep), B1 (LETF),
A2 (screener), B2 (benchmark), A3 (per-asset + portfolio).

## Lead-by-lead — verdict + GO/NO-GO

### Lead A1 — BollingerMR leverage sweep SPY 1h — ⚠️ PARTIAL-GO

Sweep L∈{1,2,3,5,10} com Kelly f/2 cross-check. Só **L=2** passa gates
(Sharpe 0.592, CAGR 10.76%). L=5 viola drawdown ceiling; L≥10 prob-of-ruin
elevada. CAGR L=2 ainda < CDI BR.

**GO/NO-GO:** NO-GO produção stand-alone. GO como ingrediente de portfolio
(se A2 screener encontrar assets descorrelatos). Resolução: A3a testou
transport — FAIL em IWM/TLT/xrpusd. **BollingerMR permanece SPY-only**
e não entra em Phase 4 sem blend.

Jornada: `2026-04-16-2310-a1-leverage-sweep-bollinger-mr-spy-1h.md`.

### Lead B1 — LETF rotation (Gayed LRS) — ✅ PASS

Base ÚNICA: `books/summaries/leverage_for_the_long_run.md` (Gayed 2016/2020).
Sintéticos UPRO/SSO pre-2009/2006 via `r = L·r_SPX_TR - drag - expense`.
SPX TR stitched KF+Tiingo 1970-2026 (14,191 bars).

Grid 72 configs × 5 gates. **13/72 passam.** ★ Winner **EMA100 band=0%
lev=2x** (cid=37):

- IS Sharpe 1.854 / OOS 1.724 / Stress 2.004
- CAGR 41.06%
- WF 8/8, DSR p=0, PBO=0, bootstrap 99.9% CI [1.037, 2.468]
- Gayed canonical (SMA200/1x) também passa (Sharpe 1.14, CAGR 12.3%).

**GO/NO-GO:** ★ GO produção. **Substitui ETFRotation como Strategy B
operacional** (ver B2 decisão REPLACE_B_WITH_A). ETFRotation fica como
benchmark científico.

Jornada: `2026-04-17-0055-b1c-letf-rotation-gates-PASS.md`.

### Lead A2 — Multi-asset universe screener — ✅ PASS

Módulo `src/ai_trade/backtest/screener/{hurst,metrics,universe}.py` sobre
14 candidatos (5 ETFs + 9 cryptos), longest history per ticker (daily).
Composite score Hurst + ATR% + RealizedVol + $Vol.

Top 5: **IWM** (H=0.447, $9B/d) > SPY > TLT (H=0.470) > QQQ > GLD. BTC/ETH
H~0.585 trending — **excluídos de MR strategies** (usam em momentum/breakout).

Gap documentado: **FX majors ausentes do daily Tiingo cache** (pull bulk
pendente para Phase 4 pre-live).

**GO/NO-GO:** GO como infra reusável. Resultado informou A3a (per-asset
BollingerMR transport — FAIL) e A3b (per-asset Donchian — QQQ PASS).

Jornada: `2026-04-16-2353-a2-multi-asset-screener.md`.

### Lead B2 — LETF rotation vs ETFRotation benchmark — ✅ DONE

Overlap 2007-01-04 → 2026-04-14 (4849 bars). Pearson 0.44 (rolling 252d
-0.06 a 0.91). **LETF domina em todos os eixos:**

- LETF: Sharpe 1.90 / CAGR 49.9% / MAR 2.72
- ETFRot: Sharpe 0.75 / CAGR 11.7% / MAR 0.41
- Blend inverse-vol 57.8%/42.2%: Sharpe 1.56 < leg dominante (D=1.18).

**GO/NO-GO:** **REPLACE_B_WITH_A** — Path B operacional passa a ser só
LETF rotation. ETFRotation top-1 mantido no read-only winners frontmatter
(benchmark).

Jornada: `2026-04-17-0005-b2-letf-vs-etf-rotation-benchmark.md`.

### Lead A3 — Per-asset + portfolio (4 sub-leads)

#### A3a — BollingerMR GARCH transport IWM/TLT/xrpusd — ❌ FAIL

Grid 3 assets, longest window each. **0/3 passam.** Melhor IWM Sharpe
0.361/PBO 0.619; TLT Sharpes negativos; xrp DD 94%. Confirma
"BollingerMR = SPY-only" com GARCH também.

**GO/NO-GO:** NO-GO expansão. BollingerMR SPY 1h permanece isolado.

Jornada: `2026-04-17-0008-a3a-bollinger-mr-garch-per-asset-FAIL.md`.

#### A3b — Donchian TSMOM per-asset QQQ/TLT/xrpusd — ✅ PASS (QQQ)

Grid 10 configs × 3 assets daily, longest windows. **4/10 QQQ passam.**
★ Winner **QQQ 20/10 Donchian** (`[trading_systems_methods, p.353]`
Turtle canonical):

- IS 1.180 / OOS 1.738 / Stress 1.710, CAGR 20.38%
- WF 8/8, DSR p=0.0041, PBO 0, boot CI [0.557, 2.954]
- TLT 0/10 (DSR p≥0.44) + xrpusd 0/10 (DD 51-76%).

**GO/NO-GO:** ★ GO como ingrediente. Sharpe OOS 1.738 narrow-beats LETF
1.724 → Path B ganha 2ª strategy uncorrelated candidate.

Jornada: `2026-04-17-0120-a3b-tsmom-donchian-per-asset-PASS.md`.

#### A3c — Portfolio 2-leg {LETF + QQQ-Donchian} — ⚠️ PARTIAL (Sharpe ✅ DR ❌)

Janela comum 2001-05-14 → 2026-04-14. ρ=0.555 long-equity. EW OOS Sharpe
2.098 > baseline 1.990 ✅ mas **4/4 blends FAIL DR** (max 1.124 < 1.2).

**GO/NO-GO:** NO-GO 2-leg → resolvido em A3d via 3ª perna descorrelata.

Jornada: `2026-04-17-0030-a3c-portfolio-letf-donchian-FAIL-DR.md`.

#### A3d — Portfolio 3-leg {LETF + QQQ-Donchian + GLD-Donchian} — ★ PASS

Janela comum 2004-11-18 → 2026-04-14 (5383 bars). ρ(LETF,GLD)=+0.063
screening PASS. **Todos 3 blends (EW/IVP/HRP) passam gates.**
`[advances_fin_ml, p.302-313, ch.16]` (HRP Listing 16.2).

★ Winner por OOS Sharpe: **EW 3-leg**

- OOS Sharpe 2.251 (baseline 2.013 LETF)
- DR 1.376, CAGR(oos) 29.06%, MDD -10.86%
- DSR p=0, WF 8/8, boot CI [0.946, 3.612]
- HRP DR 1.456 (maior DR; OOS 2.128)
- TLT alt passa só EW; Stress Sh -0.12 em 2022-24 hikes (TLT rejeitado).

**GO/NO-GO:** ★★ GO produção como **Strategy B target final**. Substitui
LETF stand-alone como blueprint de Path B pra Phase 4.

Jornada: `2026-04-17-0040-a3d-3leg-letf-qqq-gld-PASS.md`.

## Resultado consolidado — entradas e saídas do ciclo

| Lead | Verdict | Entrou Phase 3? | Sai para Phase 4? |
|------|---------|-----------------|-------------------|
| A1 | PARTIAL-GO | BollingerMR GARCH SPY 1h (Phase 2.5) | Isolado, sem blend (NO-GO prod) |
| B1 | ★ PASS | (novo) | LETF rotation EMA100/2x = Strategy B base |
| A2 | PASS | (novo) | Screener module reusável |
| B2 | DONE | LETF vs ETFRot | Decisão REPLACE_B_WITH_A |
| A3a | FAIL | BollingerMR transport | Dead end confirmado |
| A3b | ★ PASS | (novo) | QQQ Donchian 20/10 = leg-2 candidate |
| A3c | PARTIAL | 2-leg blend | Dead end (DR < 1.2) |
| A3d | ★★ PASS | 3-leg blend | **Strategy B produção = {LETF, QQQ Don, GLD Don} EW** |

## Métricas Phase 3 (overall)

- 2 winners novos (B1c LETF, A3b QQQ Donchian) + 1 portfolio blend
  (A3d 3-leg EW) todos com WF 8/8, DSR p<0.01, boot 99.9% CI low > 0.
- OOS Sharpe best: **2.251** (A3d EW) vs Phase 2.5 max 1.477 (ETFRotation OOS).
- CAGR(oos) best: **41.06%** (B1c LETF stand-alone), **29.06%** (A3d blend
  com MDD 10.86% — melhor MAR).
- 205 novos tests entre iter 28-38. Pytest 550 passed (baseline iter 27: 345).
- Livros citados: `leverage_for_the_long_run` (B1), `advances_fin_ml` ch.16
  (A3c/d HRP), `trading_systems_methods` p.353 (A3b Turtle Donchian).
- 3 dead ends confirmados: BollingerMR transport (A3a), 2-leg long-equity
  (A3c DR), TLT como 3ª perna (Stress FAIL em hikes).

## O que flui para Phase 4 (live/paper)

1. **Strategy A = BollingerMR GARCH SPY 1h** (Phase 2.5 winner, L=1 com
   sizing GARCH). Isolado; não expande; hold tempo-curto; CFD Pepperstone.
   Meta 5-10%/mês a partir de $1k **não atingida stand-alone** —
   re-avaliar via sizing dinâmico / filtragem de regime em Phase 4.
2. **Strategy B = portfolio EW 3-leg** {LETF rotation EMA100 band=0% lev=2x,
   QQQ Donchian 20/10, GLD Donchian 40/20}. Swing broker BR, 15% IR
   modelado. MDD 10.86% / CAGR 29% / Sharpe 2.25 OOS.
3. **Gap aberto para Phase 4 pre-live:** FX majors bulk pull Tiingo
   (descoberto no A2 screener) — pré-requisito para testar Strategy A
   fora de SPY sem recorrer a crypto de alta volatilidade.

## Gates obrigatórios — status final

- ✅ PBO < 0.5 em todos os winners (PBO=0 em B1c, A3b, A3d).
- ✅ DSR p < 0.05 em todos os winners.
- ✅ WF ≥ 6/8 em todos (todos os 3 novos ficaram 8/8).
- ✅ Single-block OOS hold-out (25% do total) em todos.
- ✅ Forward-window Stress (15% tail) em todos; TLT alt rejeitado
  justamente por Stress FAIL.
- ✅ Bootstrap stationary block 99.9% CI low > 0 em todos.

**Nenhum "quase lá". Mandate rule 5 respeitada.**

## Decisão final Phase 3

**CLOSED — GO para Phase 4** com as 2 strategies acima. Não há lead Phase 3
aberto. Budget 24 iters externo respeitado (usamos 12: iter 28→iter 39
para summary). Próximo gate = paper trading via cTrader OAuth (bloqueado
por Spotware e-mail) + pull FX majors Tiingo.
