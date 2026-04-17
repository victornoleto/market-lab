# Phase B Lead #2: Ablação de custos — todos os winners [SHORT-HOLD CFD] + [SWING BROKER]

**Iteração 22 — 2026-04-16 14:35**

## O que aconteceu

Confirmamos a robustez a custos reais dos 3 winners encontrados na Phase A. O protocolo foi:

- **Path A [SHORT-HOLD CFD]**: custos Pepperstone Razor para SPY CFD — spread + comissão + swap overnight.
- **Path B [SWING BROKER]**: custos de corretora brasileira — 0,10% round-trip por trade + 15% IR sobre meses positivos.

Script: `scripts/run_cost_ablation_phase_b.py`

---

## Parâmetros de custo

### Path A — Pepperstone Razor CFD (SPY)
| Item | Valor | Fonte |
|------|-------|-------|
| Half-spread | $0,01/ação | SPY CFD Razor, spread mercado ≈ $0,01–0,02 |
| Comissão | $0,0186/ação/lado | $3,50 / $100k ÷ ~188 ações |
| Swap long (anual) | 5,8% | SOFR 5,3% + markup 0,5% |
| Taxa de swap por barra (1h) | 0,0000244 | 5,8% / 365 / 6,5 horas/dia |

### Path B — Corretora brasileira
| Item | Valor |
|------|-------|
| Comissão round-trip | 0,10% por rebalanceamento |
| IR sobre ganho de capital | 15% sobre meses positivos |

---

## Resultados

### [SHORT-HOLD CFD] BollingerMR_GARCH SPY 1h

| Período | Sharpe sem custo | Sharpe com custo | Status |
|---------|-----------------|-----------------|--------|
| IS (2019-11-25 → 2024-12) | 1.149 | 0.801 (Δ=−0.185) | Gates PASS ✓ |
| OOS 2025 | — | 0.474 | Positivo ✓ |
| Stress 2026-Q1 | — | 2.854 | Positivo ✓ |

Gates com custo: DSR p=0.0431 ✓ | WF 6/8 ✓ | PBO trivial ✓ → **OVERALL PASS**

**median_hold ≤ 24 bars = 3,7 trading days ≤ 5 dias** (constraint Pepperstone ✓)

**Veredicto: CUSTO-ROBUSTO** ✓

---

### [SWING BROKER] ETFRotation_top1 (SPY/QQQ/IWM/GLD/TLT, top-1)

| Período | Sharpe gross | Sharpe net | Status |
|---------|-------------|-----------|--------|
| IS (2003 → 2024) | 0.729 | 0.551 | Gates PASS ✓ |
| OOS 2025 | — | 1.570 | Positivo ✓ |
| Stress Q1 2026 | — | +8,34% retorno (net) | Positivo ✓ |

Gates com custo: DSR p=0.0041 ✓ | WF 7/8 ✓ | PBO trivial ✓ → **OVERALL PASS**

Stress Q1 2026 calculado diretamente: +9,93% gross − 0,10% comissão − 1,49% IR = +8,34% net ✓
(nota: a estimativa via resampling mensal apresentou bug para períodos curtos; o cálculo direto é correto)

**Veredicto: CUSTO-ROBUSTO** ✓

---

### [SWING BROKER] ETFRotation_top2 (top-2 igual-ponderado)

| Período | Resultado |
|---------|-----------|
| IS gates com custo | **FAIL** — WF 5/8 (< 6/8 mínimo) |
| OOS 2025 net | 2.056 (positivo) |
| Stress Q1 2026 gross | +3,51% gross → net +2,68% |

Gates com custo: DSR p=0.0054 ✓ | **WF 5/8 ❌** | PBO trivial ✓ → **OVERALL FAIL**

O IS Sharpe bruto era 0,708 (7/8 WF). Com 15% IR + 0,10% comissão, 2 janelas WF que eram marginalmente positivas flipparam para negativo. A estratégia é **sensível a custos** — a adição de um segundo ETF dilui a edge mais do que a diversificação compensa.

**Veredicto: COSTS-SENSITIVE — WF gate fails com custos reais** ❌

---

## Implicações para production readiness

| Winner | Custo-robusto? | Mantido para Phase B? |
|--------|---------------|----------------------|
| BollingerMR_GARCH SPY 1h [SHORT-HOLD CFD] | ✓ SIM | ✓ SIM |
| ETFRotation_top1 [SWING BROKER] | ✓ SIM | ✓ SIM |
| ETFRotation_top2 [SWING BROKER] | ❌ NÃO (WF falha) | ⚠️ Mantido como "caveat" — pode ser recuperado se spread real for menor |

## Próximos leads Phase B

- **Lead #3**: MC bootstrap CI (95% CI em Sharpe/CAGR/MaxDD) para BollingerMR + ETFRotation_top1
- **Lead #4**: Cross-asset transport — outros ETFs aplicam BollingerMR 1h? Outros ETFs candidatos a rotação?
- **Lead #5**: Cross-strategy correlation — PnL diário de Path A vs Path B. Independência do edge?

## Status geral Phase B

**3/9 leads consumidos** (leads 1, 2a/max-window confirma, 2b/cost-ablation). Próximo: Lead #3 (MC bootstrap).
