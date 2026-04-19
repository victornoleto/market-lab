# Phase 3.5a-V2 Lead V2-L5 [SHORT-HOLD CFD] — XLF/HYG último par FAIL, sweep 6/6 completo (iter 65)

**Data:** 2026-04-19 02:40
**Iter:** 65 (V2-L5 sweep-tickers, último par antes do aggregator)
**Path tag:** [SHORT-HOLD CFD] — Pepperstone Razor cost model
**Pair:** XLF (Financial Select Sector SPDR) vs HYG (iShares iBoxx $ High Yield Corp Bond)
**Window:** 2014-01-02 → 2026-04-14 (3088 bars, ~12 anos — limitado pela inception do HYG)
**Verdict:** ❌ FAIL — cointegração falha (p=0.0746 > α=0.05), 0 trades, 6/7 subset gates FAIL
**Sweep status:** `sweeping → aggregating` (todos 6 pares done; 0 cointegrados; 0 PASS).

---

## O que foi testado

Config idêntica aos 5 pares anteriores (GLD/SLV, QQQ/XLK, SPY/IWM, TLT/IEF, XLE/USO):

- **Cointegration gate:** Engle-Granger duas etapas (OLS log-log → ADF on residuals),
  α=0.05 `[algo_trading_chan, p.42-46]`.
- **Dynamic hedge:** Kalman filter (δ=1e-5, V_e=1e-3) sobre β `[machine_trading_chan, ch.3]`.
- **Signal:** z-score das residuais com `window=60d`, entry=±2.0σ, exit=0.0σ,
  stop=±4.0σ `[algo_trading_chan, p.47-54]`.
- **Hold cap:** 30d; direction = market-neutral (long y / short β·x ou vice-versa).
- **Splits chronologic:** 70/20/10 IS/OOS/FWD.

---

## Resultados

### Cointegration (full-series 2014-2026)

- OLS: `log(XLF) = -7.659 + 2.666 * log(HYG) + residuals`
- ADF on residuals: stat = **−2.697**, p-value = **0.0746** → **FAIL** (α=0.05,
  mas é o par **mais próximo** de passar entre os 6 testados).
- Final Kalman β = **1.563**.

### Splits

| Split | Range | n_bars | Sharpe | CAGR | MaxDD |
|-------|-------|-------:|-------:|-----:|------:|
| IS | 2014-01-02 → 2022-08-02 | 2161 | 0.000 | 0.00% | 0.00% |
| OOS | 2022-08-03 → 2025-01-17 | 618 | 0.000 | 0.00% | 0.00% |
| FWD | 2025-01-21 → 2026-04-14 | 309 | 0.000 | 0.00% | 0.00% |

### Gates

- WF 0/8 profitable, 0% MDD (0 trades).
- 6/7 subset gates FAIL: `oos_sharpe_gt_0`, `fwd_sharpe_gt_0`, `wf_pass`,
  `median_hold_ge_3d`, `oos_cagr_ge_30pct`, `oos_sharpe_ge_2`. Único PASS:
  `oos_maxdd_le_25pct` (trivial a zero trades).

---

## Diagnóstico: XLF e HYG têm drivers que se anulam

XLF e HYG compartilham sensibilidade a **credit quality / spread** mas divergem
em **rate duration / NIM**:

- Fed hikes 2022-2024: HYG price ↓ (duration ~3-4y), XLF ↑ (Net Interest Margin
  expansion em bancos). Sinal oposto.
- COVID shock 2020-Q1: HYG −20% (liquidez + default fear), XLF −30% (loan loss
  provisions). Co-direcional mas magnitudes diferentes.
- 2023-Q1 SVB/regional bank crisis: XLF −10% súbito, HYG flat (não concentra em
  regional bank debt). Desalinhamento específico.

O coeficiente β = 2.67 (log-log) também é economicamente anômalo — XLF responde
cerca de 2.7× mais a log(HYG) do que 1:1 sugere; esse scale enorme + p=0.0746
borderline são sintomas de **dois processos integrados **com overlap parcial
mas não relação cointegrada formal `[algo_trading_chan, p.44]`.

---

## Contexto: V2-L5 sweep completo 6/6, zero cointegração

| # | Pair | ADF stat | p-value | Kalman β | Window | Verdict |
|---|------|---------:|--------:|---------:|--------|---------|
| 1 | GLD_SLV | -2.17 | 0.192 | 0.98 | 2006-2026 | FAIL |
| 2 | QQQ_XLK | -1.24 | 0.658 | 0.94 | 2003-2026 | FAIL |
| 3 | SPY_IWM | -2.50 | 0.115 | 0.80 | 2001-2026 | FAIL |
| 4 | TLT_IEF | +0.82 | 0.992 | 1.67 | 2014-2026 | FAIL |
| 5 | XLE_USO | -1.55 | 0.511 | 0.54 | 2006-2026 | FAIL |
| 6 | XLF_HYG | **-2.70** | **0.0746** | 1.56 | 2014-2026 | FAIL (closest) |

**6/6 pares pre-selecionados falham Engle-Granger ADF α=0.05.** Todos têm
β Kalman economicamente plausível (1 par negativo: XLE_USO, bizarro), mas
nenhum resíduo log-log é estacionário em 12-25 anos.

---

## Por que V2-L5 não entrega winner Plano A

Carver e AFML advertem que pair trading em ETFs líquidos de mercados
maduros é a primeira coisa que arbitragem institucional (Renaissance, DE Shaw,
HFs quantitativos) extingue `[algo_trading_chan, p.42]`, `[machine_trading_chan,
ch.3]`. Os 6 pares testados são exatamente a lista de livros-texto (setor-vs-índice,
small-vs-large, metais gêmeos, duration duro, energia cash/futures, financials vs
credit). O sinal que o market-maker ainda não caçou vive em:

- **Micro-caps ou pares idiossincráticos** (Pepperstone não oferece nem metade
  — CFD universe é blue-chip global).
- **Pairs com barreiras regulatórias** (ADRs vs local, cross-border A/H shares).
- **Structural pairs** (specific event-driven: M&A arb, index-rebalance arb).

Nenhum desses está no escopo Pepperstone CFD. **V2-L5 refuta a família de
equity pairs como fonte de edge em Plano A.**

---

## Efeito no Plano A portfolio

Plano A winner permanece `gayed_ema100_L2_off_gld` standalone (iter 43):

- Sharpe OOS 2.285 / CAGR 79.14% / MDD -21.02% / hold 6d.
- PBO 0.103 / DSR p=0.000288 / WF 8/8 / IR-SPY 2.16.

L1 (TSMOM) DEAD, L3 (AFML triple-barrier) DEAD, L4 (Carver RP blend) DEAD,
**L5 (pairs) DEAD**. Restam:

- **L6 — Vol breakout multi-asset daily** (12 configs em índices + commodities
  + FI, sem FX).
- **L7 — Summary + verdict + flip done.**

Mesmo que L6 entregue 0 PASS, V2 já tem **1 winner Plano A** (L2 Gayed) + Plano B
(4 winners). O stop rule "abandonar Plano A se 0 PASS" não dispara. L7 aplica
verdict final sobre o conjunto L1-L6.

---

## Próxima iter (66)

**Processar aggregator V2-L5** (status `aggregating` no registry,
`tickers_pending=[]`, 6 tickers done, 0 PASS). Per fan-out protocol:

1. Escrever `reports/phase3_5a_v2/v2_l5_equity_pairs/AGGREGATE.md` com
   consolidação dos 6 pares (tabela ADF + diagnóstico família).
2. Escrever jornada `2026-04-19-HHMM-phase3.5a-v2-L5-aggregator-DEAD.md`
   (pode reutilizar conteúdo desta entry expandido — evitar duplicação).
3. Flip `registry.status = done`; zerar `active_lead_registry` em memory.md;
   mover V2-L5 para `## Dead ends`.
4. Bootstrap V2-L6 (vol breakout) na iter seguinte.

---

## Código / testes

- Zero mudança em código. Driver `scripts/iter_v2_l5_run_pair.py` reusado.
- Módulo `kalman_pair_cointegration.py` imutável desde iter 60.
- Pytest: **796 passed** (sem regressão).
- Artefatos: `reports/phase3_5a_v2/v2_l5_equity_pairs/XLF_HYG.{md,json,parquet}`.

---

## Citações

- Engle-Granger + ADF on residuals: `[algo_trading_chan, p.42-46]`.
- Kalman dynamic hedge ratio: `[machine_trading_chan, ch.3]`.
- Z-score ±2σ entry/exit: `[algo_trading_chan, p.47-54]`.
- Walk-forward 6/8 + MDD 25% cap: `[advances_fin_ml, ch.11]`.
- Hold economics retail: `[systematic_trading, p.185-188]`.
- Pair arbitrage saturated in liquid ETFs: `[algo_trading_chan, p.42]`,
  `[machine_trading_chan, ch.3 intro]`.
