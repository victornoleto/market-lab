# Phase 3.5a-V2 encerrada — WINNER FOUND (1 PASS / 5 DEAD) [SHORT-HOLD CFD]

**Data:** 2026-04-19 05:10
**Iteration do loop autônomo:** 81 (V2-L7 atomic verdict)
**Branch:** `phase3.5a-v2/plano-a-last-attempt-20260418`
**Tag:** `[SHORT-HOLD CFD]` — Plano A
**Spec:** `specs/phase_3_5a_v2.md`
**Aggregate cross-lead:** `reports/phase3_5a_v2/AGGREGATE.md`

---

## TL;DR (1 parágrafo)

Plano A sobrevive. Depois de V1 ter queimado 143 runs em 1h FX/metais sem achar
ninguém, a **V2 (framework corrigido: daily, hold ≥3d, multi-asset CFD, custos
spread+commission-dominant)** rodou 82 iters / 58 runs em 6 famílias e produziu
**exatamente 1 winner gate-passing**: `gayed_ema100_L2_off_gld` — regime rotation
Gayed transportada para CFD Pepperstone, leverage 2×, SPY+QQQ risk-on, GLD
risk-off. Sharpe OOS **2.285** / CAGR líquido **79%** / MaxDD **−21%** / hold
mediano 6 dias. Os outros 5 leads (TSMOM V2-L1, AFML meta-label V2-L3, Carver
risk-parity V2-L4, equity pairs V2-L5, vol-breakout V2-L6) morreram todos, cada
um por motivo estrutural orgulhoso e não-operacional. A stop rule binding (V2 =
última tentativa, 0 PASS → abandono permanente) **não dispara** — Plano A
continua vivo como 2ª perna do bucket ativo, lado a lado com Plano B (3-leg EW).
Próxima fase: `specs/phase_4_paper_trading.md` (dual-path paper trading, Banco
Inter Global para B + Pepperstone cTrader Demo para A).

---

## Contexto — o que é "V2 = última tentativa"

**V1 (3.5a V1, 2026-04-18, 42 iters)** rodou um framework que em retrospecto
estava mal especificado: 1h fixo, FX + 2 metais, hold ≤ 5d para "evitar swap",
targets de CAGR 60-120%/ano. 143 runs em 6 famílias (BollingerMR canônico,
Donchian, pairs-FX Kalman, session-based FX, regime-filter linear sobre MR)
produziram **0 winners novos**. Ceiling empírico = BollingerMR GARCH SPY 1h L=2
com CAGR 5.9% — pior que CDI BR.

O agente autônomo da V1 concluiu "abandon Plano A" e escreveu o verdict T7 como
se o projeto fosse pivotar. **O usuário rejeitou esse framing**, identificou que
o erro era estrutural (framework V1 errado, não Plano A impossível), e lançou
**V2 como última tentativa** com contrato binding: se V2 produzir 0 PASS,
Plano A é abandonado permanentemente (sem V3). Spec `specs/phase_3_5a_v2.md`
é o contrato executado aqui.

V2 corrigiu 6 dimensões do V1:

| Dim | V1 (errado) | V2 (corrigido) |
|---|---|---|
| Timeframe | 1h fixo | livre (daily venceu) |
| Hold | ≤ 5d | ≥ 3d (carver `[systematic_trading, p.185-188]`) |
| Universe | 12 FX + 2 metais | 40 CFDs multi-asset daily |
| Cost focus | swap-dominant | spread+commission+slippage+swap round-trip |
| CAGR target | 60-120%/yr | 30%/yr realista |
| Families | MR, Donchian, pair, session, regime-filter | TSMOM, Gayed-transport, AFML meta, Carver RP, pairs, vol breakout |

---

## Execução V2 (iter 0 → iter 81)

### Iter budget previsto vs realizado (82 iters)

Todos os 8 leads consumiram exatamente o orçamento planejado no spec §5. Zero
overshoot, zero commit corrompido, zero mis-write no registry JSON. Fan-out
protocol (`docs/self_improvement/fanout_protocol.md`) aguentou 82 iters sem
drift.

### Lead-by-lead

| Lead | Família | Configs | Verdict | Best OOS Sharpe | Iters |
|---|---|---:|:--:|---:|---:|
| V2-L0 | Universe screener | — | ✅ manifest 40 CFDs | — | 1 |
| V2-L1 | TSMOM monthly | 12 | ❌ DEAD | n/a (swap drag 74-166%) | 14 |
| **V2-L2** | **Gayed regime rotation CFD** | **27** | **★ PASS** | **2.285** (ema100 L2 gld) | **29** |
| V2-L3 | AFML triple-barrier + RF meta | 12 | ❌ DEAD | 1.213 XLF (CAGR 2.5%) | 14 |
| V2-L4 | Carver risk-parity blend | 1 | ❌ DEAD | 1.856 blend (CAGR 16%) | 1 |
| V2-L5 | Kalman equity pairs | 6 | ❌ DEAD | — (0/6 cointegrated) | 8 |
| V2-L6 | Vol-breakout Donchian 1/N | 12 | ❌ DEAD | −0.217 (12/12 OOS negative) | 14 |
| V2-L7 | Summary + verdict + flip done | — | ✅ atomic | — | 1 |

**Resultado:** 1 PASS / 5 DEAD / 2 infra. Pass rate famílias: 1/6 (17%). Pass
rate runs: 1/58 (1.7%) — um n razoável para o gate DSR que corrige exatamente
isso.

---

## O que venceu — `gayed_ema100_L2_off_gld`

A família **Gayed LETF rotation** (`[leverage_for_the_long_run, p.11-21]`),
originalmente encontrada por nós em Plano B como o sinal de regime do 3-leg EW
de Path B (SSO=LETF2× S&P via EMA100, QLD=LETF2× NASDAQ, UGL=LETF2× Gold),
foi **transportada** para o contexto CFD Pepperstone Razor — sem LETFs
sintéticas, só SPY+QQQ com leverage 2× via alavancagem CFD, usando GLD como
risk-off quando o sinal EMA100(SPY) sai.

Isto sobrevive 13/13 gates da framework V2:

| Gate | Threshold | Observado |
|---|---:|---:|
| PBO (CSCV 10-block, 27 configs) | < 0.5 | **0.103** |
| PBO (CSCV 16-block) | < 0.5 | **0.036** |
| DSR p-value (n_trials=27) | < 0.05 | **0.000288** |
| OOS Sharpe net | > 0 | **2.285** |
| FWD Sharpe 2024-2026 | > 0 | **1.821** |
| Bootstrap 99.9% CI low | > 0 | **0.962** |
| Walk-forward profitable | ≥ 6/8 | **8/8** |
| WF max-window DD | ≤ 25% | **22.7%** |
| CAGR OOS net | ≥ 30% | **79.14%** |
| Sharpe OOS | ≥ 2.0 | **2.285** |
| MaxDD OOS | ≤ 25% | **−21.02%** |
| Median hold | ≥ 3 days | **6** |
| IR vs SPY | ≥ 0.5 | **2.161** |

Detalhes estão no AGGREGATE do L2 (`reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md`)
e no jornada de PASS (`2026-04-19-0020-phase3.5a-v2-L2-gayed-transported-PASS.md`).

---

## Por que os 5 DEADs morreram (1 linha cada)

- **V2-L1 TSMOM monthly**: swap drag 74-166% em holds de 41-160d. FX 3-pack attractor. `[hurst_2017]`.
- **V2-L3 AFML meta-label**: meta-labeling é filtro, não edge. EMA-50 single-asset primary thin; RF dropa 70-95% eventos; CAGR residual 2.5% morre no custo. `[advances_fin_ml, p.50]`.
- **V2-L4 Carver RP blend**: vol-parity só ajuda se TODAS pernas positivas; L1 negativo + L3 quase-flat diluem L2 alpha de 79% para 16%. `[advances_fin_ml, ch.16]`.
- **V2-L5 Kalman pairs**: 0/6 pares ADF-cointegrados. Pair arb em ETF líquido extinguido por HFT. Universo Pepperstone blue-chip não tem micro-cap. `[algo_trading_chan, p.42]`.
- **V2-L6 Vol-breakout 1/N**: 12/12 OOS Sharpe NEGATIVA. Regime 2022-2024 letal pra trend-follow (bear curto + recovery rápido + tech-narrow + correções 2024). Universo 10 ETFs pequeno demais. `[trend_following_covel, ch.4]`.

---

## O que V2 provou estruturalmente (além do winner)

### 1. Plano A edge é regime-driven, não breakout/pair/meta

Das 6 famílias ortogonais testadas em V2, **só a família regime-rotation
passou** todos os gates. Isso é consistente com V1 (onde BollingerMR GARCH —
uma variação de regime-like vol-size — foi a única Sharpe-positive) e explica
por que V2-L6 (vol-breakout puro sem regime) morreu catastrófico.

**Inferência**: para uma conta CFD retail Pepperstone em cadência daily com
hold mediano ~1-2 semanas, o único vencedor é **condicionar alavancagem num
sinal de regime** — não momentum puro, não arbitragem de pares, não
meta-labeling sobre primários fracos.

### 2. Três invariantes de leverage (descobertas no sweep L2 27-config)

1. **MaxDD escala super-linear com leverage**, independente de off-regime:
   L=2 → 20-23% | L=3 → 29-32% | L=5 → 45-49%. Em L=5 o off-regime asset não
   importa (MDD idêntico cross-{cash,TLT,GLD} a 2 decimais) — Vince PoR
   empírico confirmado `[leverage_space]`.
2. **Sharpe por adaptividade do sinal**: SMA-200 (teto ~1.65) < LRS (~2.10) <
   EMA-100 (~2.29). EMA-100 exit/entry mais cedo vale o 2× switch cost
   `[leverage_for_the_long_run, p.11-14]`.
3. **Off-regime ranking em L=2**: GLD > cash > TLT (spread ~0.1 Sharpe).
   GLD drift positivo + asimetria dólar-hedge em crises vale ~7pp/yr vs cash.
   TLT lag porque OOS 2022 é o pior ano fixed-income do século.

### 3. V1 não estava "quebrado" — estava mis-specificado

V1 não conseguiu nenhum winner porque testou o framework errado, não porque
Plano A é impossível. A V2 com o framework corrigido achou 1 winner decisivo.
Isso reforça a doutrina (ver CLAUDE.md): **especificar o espaço correto antes
de varrer é mais importante do que varrer mais**.

---

## Comparação dual-path mandate §1

| Métrica | Plano B (V4, 3-leg EW) | Plano A (V2-L2 CFD) |
|---|---:|---:|
| Sharpe OOS net | 2.251 | **2.285** |
| CAGR OOS net | 25.56% | **79.14%** |
| MaxDD OOS | −10.86% | **−21.02%** |
| CAGR/MDD ratio | 2.36 | **3.76** (mais reward-denso) |
| IR vs SPY OOS | ~alto (3-leg diversificação) | 2.161 |
| Broker | Banco Inter Global | Pepperstone cTrader |
| Cost regime | 15% IR BR @ rebalance | Razor RT ~11 bps + swap 1.25 bps/d |
| Median hold | ~semanas (threshold 10pp) | 6 dias |

Nenhum domina o outro em todos eixos. O mandate §1 posiciona os dois como
**bucket ativo dual-path**, 50/50 default dentro dos 20-40% ativo. Se ρ(A,B)
medido em Phase 4 for alto (> 0.7 devido a SPY/GLD comum), re-ponderar a favor
do mais complementar.

---

## Stop rule binding NÃO disparou

O contrato V2 dizia: *"se V2 produzir 0 PASS após ~80 iters: abandonar Plano A
permanentemente, focar exclusivamente em refinar Plano B. Nada de V3.
Mandate rewrite."*

Resultado: **1 PASS** (gayed_ema100_L2_off_gld). Stop rule não dispara. Plano A
retido como 2ª perna ativa. Mandate §7 recebe entry de fechamento V2 (não
override). `specs/phase_4_paper_trading.md` drafted nesta mesma iter.

---

## O que vem a seguir (Phase 4 paper trading)

Spec: `specs/phase_4_paper_trading.md` (drafted 2026-04-19 iter 81).

Escopo resumido:

1. **Plano B live-ready:** runbook `reports/phase3_5b/PRODUCTION.md` já está
   pronto. Phase 4-B = abrir conta Banco Inter Global, remeter capital inicial
   (R$3-5k via câmbio Inter), executar 3-leg EW com threshold 10pp rebalance,
   paper parallel 3 meses no testfol.io + live com capital mínimo.
2. **Plano A paper adapter:** construir adapter Pepperstone cTrader Open API,
   implementar regime-signal service (EMA-100 close SPY diário), sizing L=2
   com GLD off-regime, 3 meses paper trading em cTrader Demo.
3. **Post-paper gate:** comparar Sharpe/CAGR/MDD realizado vs backtest. Re-
   calibrar L=2 para Plano A se slippage realizado > 30 bps/trade. Re-ponderar
   A/B se ρ > 0.7 ou se realized diverge > 40%.
4. **Orçamento Phase 4:** 3 meses calendário (não iters). Trigger para Phase 5
   live: ambos paper gates pass.

---

## Citações

- Gayed LRS/EMA/SMA regime rotation (a família vencedora V2-L2):
  `[leverage_for_the_long_run, p.7, p.11-14, p.16-17, p.21]`.
- Vince PoR (MDD cap cross-off-regime em L=5): `[leverage_space, Vince]`.
- Kelly f/2 cross-check (L=2 f/2-safe): `[math_money_mgmt, Vince]`.
- Carver risk-parity off-regime: `[systematic_trading, ch.8-9, p.185-188]`.
- PBO / CSCV / DSR: `[advances_fin_ml, p.208-211, ch.14]`.
- Walk-forward 6/8 gate: `[advances_fin_ml, ch.11]`, Pardo (2008) ch.10-11.
- Bootstrap estacionário: `[advances_fin_ml, p.196-202]`.
- Meta-labeling filter not edge: `[advances_fin_ml, p.50]`.
- Pair arb extinção ETF líquido: `[algo_trading_chan, p.42-54]`, `[machine_trading_chan, ch.3]`.
- Trend-follow whipsaw: `[trend_following_covel, ch.3-5]`.
- Portfolio construction (RP precisa all-legs-positive): `[advances_fin_ml, ch.16]`.
- TSMOM Hurst: Hurst et al. (2017).

---

## Links

- **Winner PASS jornada:** `2026-04-19-0020-phase3.5a-v2-L2-gayed-transported-PASS.md`
- **Cross-lead AGGREGATE:** `reports/phase3_5a_v2/AGGREGATE.md`
- **L2 AGGREGATE:** `reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/AGGREGATE.md`
- **Spec V2 (contrato executado):** `specs/phase_3_5a_v2.md`
- **Spec Phase 4 (drafted nesta iter):** `specs/phase_4_paper_trading.md`
- **Mandate §7 atualizado:** `docs/investment-mandate.md`
- **Plano B production runbook:** `reports/phase3_5b/PRODUCTION.md`
- **Jornadas DEAD desta V2:**
  - `2026-04-18-1407-phase3.5a-v2-L1-tsmom-DEAD.md`
  - `2026-04-19-0115-phase3.5a-v2-L3-afml-triple-barrier-DEAD.md`
  - `2026-04-19-0215-phase3.5a-v2-L4-carver-blend-DEAD.md`
  - `2026-04-19-0310-phase3.5a-v2-L5-equity-pairs-DEAD.md`
  - `2026-04-19-0410-phase3.5a-v2-L6-vol-breakout-DEAD.md`
