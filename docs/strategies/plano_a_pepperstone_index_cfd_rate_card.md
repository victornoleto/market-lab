# Pepperstone Razor Index CFD — Rate Card Empírico (T1)

**Propósito:** validar que os custos reais de Pepperstone cTrader em US500/
NAS100/XAUUSD estão dentro do envelope de viabilidade do Caminho 3
(ver `reports/phase4_0/index_cfd_validation/cost_sensitivity.md`).

**Status:** ✅ **T1 pull executado 2026-04-20** via Open API Protobuf
(ver `scripts/pull_ctrader_rate_card.py`). Scope = "accounts" (read-only).
Broker: Pepperstone SCB (account 46981202, demo, $50k balance).

**Pendentes:** T1.2 spread em live quotes; T2 dividend adjustment em
próximo ciclo ex-div SPY (~mid-Jun 2026).

---

## 1. US500 (proxy SPY/SPX)

### 1.1 Specs do instrumento (observados via API)

| Campo | Valor |
|---|---:|
| symbolId | 10013 |
| symbolCategoryId | 3 (Indices) |
| description | US 500 Index |
| digits | 1 |
| pipPosition | 0 |
| enableShortSelling | true |
| minVolume | 10 (= 0.1 lot) |
| stepVolume | 10 (= 0.1 lot increment) |
| maxVolume | 10000 (= 100 lots) |
| lotSize | 100 |
| **Notional por lot @ SPX 6000** | **~$6,000** ($1/point × 6000 points) |
| **Notional mínimo (0.1 lot)** | **~$600** |

### 1.2 Custos (observados)

| Campo | Valor | Interpretação |
|---|---:|---|
| commission | 0 | ✅ **commission-free** |
| commissionType | 1 (USD per million) | (but value = 0) |
| swapLong | -6.14 | -6.14%/yr (swapCalcType=1 PERCENTAGE) |
| swapShort | +1.14 | +1.14%/yr |
| swapCalculationType | 1 (PERCENTAGE) | Annualized % |
| swapPeriod | 24 (hours) | Daily accrual |
| skipRolloverDays | 3 (Wed triple charge) | Standard pattern |
| spread_half_bps (estimate) | TBD | Pendente T1.2 live quote |

**Interpretação swap long:** -6.14%/yr ≈ **-0.0168%/day** applied to levered
notional. Fed rate ~5% + Pepperstone broker spread ~1% = 6.14% coerente.

### 1.3 Viabilidade a $1k notional target

- Min lot = 0.1 → $600 notional (mercado SPX 6000).
- Target $1000 → 0.1-0.2 lot feasible → **40% rounding error**.
- ⚠️ Marginalmente operável mas com weighting off do backtest.

---

## 2. NAS100 (proxy QQQ/NDX) — **cash spot CFD (NÃO o -F futures)**

### 2.1 Specs do instrumento

| Campo | Valor |
|---|---:|
| symbolId | 10014 |
| symbolCategoryId | 3 (Indices) |
| description | US Tech 100 Index |
| minVolume | 10 (= 0.1 lot) |
| stepVolume | 10 |
| lotSize | 100 |
| **Notional por lot @ NDX 20000** | **~$20,000** |
| **Notional mínimo (0.1 lot)** | **~$2,000** |

### 2.2 Custos

| Campo | Valor |
|---|---:|
| commission | 0 ✅ |
| swapLong | -6.14%/yr |
| swapShort | +1.14%/yr |
| Variant futures (`NAS100-F`) | 0 swap mas min 1 lot = **$20,000** |

### 2.3 Viabilidade a $1k

- Min 0.1 lot = $2,000 → **2× overshoot** do target $1k.
- Força over-exposição de 2× no leg NAS100 vs target equal-weight.
- ⚠️ **Quebra equal-weight do backtest.** Força re-config ou re-backtest.
- Futures variant (NAS100-F, zero swap) pior: $20k min = **20× overshoot**.

---

## 3. XAUUSD (proxy GLD/spot gold)

### 3.1 Specs do instrumento

| Campo | Valor |
|---|---:|
| symbolId | 41 |
| symbolCategoryId | 2 (Metals) |
| description | Gold vs US Dollar |
| minVolume | 100 (= 0.01 lot) |
| stepVolume | 100 (= 0.01 lot increment) |
| lotSize | 10000 (= 100 oz per std lot) |
| **Notional por lot @ $2700/oz** | **~$270,000** (100 oz × $2,700) |
| **Notional mínimo (0.01 lot = 1 oz)** | **~$2,700** |

### 3.2 Custos

| Campo | Valor | Interpretação |
|---|---:|---|
| commission | 0 ✅ | |
| swapLong | -8.84 pips | swapCalcType=0 (PIPS); ~1.2-12%/yr dep. interpretation |
| swapShort | +3.99 pips | Short earns back some |
| Variant futures (`XAUUSD-F`) | 0 swap, min 0.1 lot = **$27,000** | Inacessível a $1k |

### 3.3 Viabilidade a $1k

- Min 0.01 lot = 1 oz = ~$2,700 → **2.7× overshoot**.
- ⚠️ Força over-exposição significativa no off-regime.

### 3.4 Alternativas com menor tick (cross-FX gold pairs)

| Símbolo | Min notional | FX exposure introduz | OK? |
|---|---:|---|:--:|
| XAUEUR | ~$30 (1 oz ao FX) | EUR/USD drift | ⚠️ |
| XAUGBP | ~$30 | GBP/USD drift | ⚠️ |
| XAUAUD | ~$20 | AUD/USD drift | ⚠️ |
| XAUCHF | ~$30 | CHF/USD drift | ⚠️ |
| XAUJPY | ~$20 | JPY/USD drift | ⚠️ |
| XAUTUSD (Tether Gold) | ~$27 | Tether Ltd credit risk | ❌ rejeitar |

Cross-FX gold pairs permitem granularidade fina mas adicionam FX risk de ~5-8%/yr
stddev ao leg gold. Fora do escopo Caminho 3 baseline (backtest usou GLD USD).

---

## 4. Dividend adjustment (T2 — pendente)

Status: pendente observação empírica em próximo ciclo ex-div SPY
(aprox. mid-Jun 2026). Procedimento:

1. Abrir 0.1 lot long em US500 pelo menos 5 dias antes do ex-div SPY.
2. Esperar ex-div passar (SPY paga trimestral).
3. Verificar transaction history no cTrader: deve haver crédito cash
   proporcional ao dividend yield × notional.
4. Calcular haircut = 1 − (cash_recebido / expected_dividend_yield).

Gate T2: haircut ≤ 5% (yield capture ≥ 95%).

---

## 5. Verdict T1 final

### 5.1 Gate-by-gate vs sensibility matrix envelope

| Gate | Threshold envelope | Observed | Status |
|---|---|---:|:--:|
| commission ≤ 30 bps RT | envelope max 40 bps | **0 bps** | ✅ PASS massivo |
| swap_long ≥ -0.025%/day | envelope max -0.040%/day | -0.0168%/day (US500) | ✅ PASS |
| spread_half ≤ 15 bps | envelope max 25 bps | **TBD** (T1.2) | ⏳ pending |
| div_haircut ≤ 50% | envelope max 100% | TBD (T2) | ⏳ pending |
| **Lot granularity @ $1k** | ≤ 50% rounding | NAS100 **200%**, XAUUSD **270%** | ❌ **FAIL** |

### 5.2 Overall verdict

**Commission + swap: PASS empiricamente confirmado.** Pepperstone Razor Index
está dentro do envelope validado em Phase 4.0 T3+T4.

**Lot granularity at $1k: FAIL estrutural.** NAS100 e XAUUSD têm min notionals
($2k e $2.7k respectivamente) incompatíveis com target $1k equal-weight.

**Threshold operacional corrigido:**

| Capital | Viabilidade 3-leg Caminho 3 | Motivo |
|---:|:--:|---|
| $1,000 | ❌ **inviável** | NAS100 2× overshoot, XAUUSD 2.7× overshoot |
| $2,500 | ⚠️ marginal | XAUUSD 0.01 lot ainda overshoot 8% |
| **$5,000** | ✅ **viável** | US500 granularity OK, NAS100 40% rounding, XAUUSD 50% rounding |
| $10,000+ | ✅ ótimo | Todas legs com granularidade fina |

### 5.3 Revised recommendation

**Phase 5.1 live: começar com USD $5,000 (não $1,000)** quando todos T1.2, T2
+ Phase 4 paper passarem. O $5k é lot-granularity-constrained, não cost-model.

**Alternatives se capital limitado a $1k:**
- (a) Fallback para Caminho 1 (Plano B only at Banco Inter — sem lot minimum drama).
- (b) Single-leg US500 em Pepperstone Index (requer re-backtest, nova strategy não validada).
- (c) Share CFD path a $10k+ (commission 6.6 bps modelado continua fiel).

---

## 6. Citações

- `[systematic_trading, Carver, p.185-188]` — fixed commission + lot size
  dominance at retail scale.
- `[leverage_for_the_long_run, Gayed, p.11-14]` — EMA-100 signal base.
- Phase 4.0 spec: `specs/phase_4_0_index_cfd_validation.md`.
- Sensibility matrix: `reports/phase4_0/index_cfd_validation/cost_sensitivity.md`.
- Raw API data: `reports/phase4_0/index_cfd_validation/ctrader_rate_card_raw.json`.
- Catalog variants: `reports/phase4_0/index_cfd_validation/pepperstone_catalog_variants.json`.
