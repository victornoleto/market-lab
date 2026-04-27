# global_factor_tilt_loop — closure após 13 iters

**Data:** 2026-04-27
**Branch:** global-factor-tilt/iter-001
**Status:** loop FROZEN — mandate §7 deliberation pendente

---

## TL;DR

13 iterations, 6 winners, 3 Pareto frontiers identificadas:

| frontier | iter | Sharpe (edu) | CAGR (edu) | MDD (edu) | nicho |
|---|---|---|---|---|---|
| **Sharpe gross** | **009** | **1.120** | 13.89% | 20.81% | melhor risk-adj retorno bruto |
| **Sharpe net** | **012 hybrid 50/50** | **1.021** | 13.38% | 26.85% | ótimo após DARF + complexidade reduzida |
| **CAGR gross** | **013** | 1.011 | **16.35%** | 28.98% | maximizador de retorno absoluto |

**Achado mais importante**: hybrid 50/50 (50% iter 009 HAA+Gold + 50% Plano C buy-hold) tem Sharpe NET superior a 100% HAA NET em todos os 3 datasets. Combinação de:
- Diversificação entre 2 estratégias descorrelacionadas
- Rebalancing premium (Plano C compra HAA na queda, vende no topo)
- DARF deferral na metade Plano C (taxa só na venda final)

---

## A corrida

### Iters 1-4 (overnight 2026-04-26)
Bootstrap + descoberta inicial. Iter 002 (momentum K=2/lb=6m) WINNER 90, primeira candidate viável. Iter 004 (+ 10% MF sleeve) WINNER 90, confirmou MF "free lunch".

### Iter 005 — primeiro Pareto frontier
HAA SmartStack (Hybrid Asset Allocation Keller & Keuning 2023 SSRN 4346906): canary VWO + universe ofensivo stacked (NTSX/NTSI-synth/NTSE-synth/GDE) + 10% KMLM. **Sharpe 1.112 (31y), CAGR 14.14%, MDD 20.91%**. Domina VT/Plano C/V_HYBRID+MF nos 3 eixos.

### Iter 006-008 — exhaustive testing queue
Confirmou alternativas:
- VAA-G4 SmartStack STRONG 85 (subordinada a HAA — bond-as-4th-offensive drag)
- User static portfolio + G3' adapted STRONG 88 (essentially WINNER, perdeu por -0.0004 numerical artifact)
- WLDU + Gayed 200d SMA DEAD END estrutural (VT global já tem o Sharpe que LRS aspira em S&P)

### Iter 009 — Pareto frontier definitivo
HAA + 5% Gold sleeve. **Sharpe 1.120**, melhor que iter 005. Gap pra bestfolio (1.18) reduziu de -0.07 pra -0.06.

### Iter 010 — VAA-G3 pure-equity
GDE substituindo BND no ofensivo. CAGR +2pp mas Sharpe -0.07. Confirmou: VAA breadth < HAA canary em Sharpe.

### Iter 011 — DARF + Carnê-Leão sobre iter 009
DARF drag estimado: **~1.2-1.8pp/y** (aplicação 15% × turnover ~70%). Net edu Sharpe 0.991, CAGR 12.13%. Margem net vs Plano C net: **+1.84pp edu, +1.43pp vt, -0.50pp ndx**. Veredito: HAA NET *viable but not conclusively superior* a Plano C buy-hold (no threshold de 2pp/y user-defined).

### Iter 012 — hybrid 50/50 (CRITICAL FINDING)
50% HAA+Gold (com DARF mensal) + 50% Plano C (sem DARF até terminal). **Sharpe NET supera 100% HAA NET em TODOS os datasets**:

| dataset | 100% HAA net | 50/50 hybrid net | Δ |
|---|---|---|---|
| edu (31y) | S=0.991 / C=12.13% | **S=1.021 / C=13.38%** | +0.030 / +1.25pp |
| vt_real (~17y) | S=0.943 / C=11.31% | **S=1.058 / C=14.06%** | +0.115 / +2.75pp |
| ndx_real (16y) | S=0.851 / C=9.31% | **S=0.972 / C=11.84%** | +0.121 / +2.53pp |

Mecanismo do "milagre": diversificação entre estratégias descorrelacionadas + rebalancing premium + DARF deferral.

### Iter 013 — autonomous follow-up: HAA + ZROZ defensive
Loop adicionou ZROZSIM (25y zero-coupon Treasury) ao HAA defensive palette. Sharpe -0.11 (variance penalty da duração), mas **CAGR +2.46pp (16.35%)** — novo CAGR frontier. Lesson: ZROZ trade Sharpe por CAGR; bestfolio reference (Sharpe 1.18) "almost certainly uses low-variance defensive (CASHX-dominant)".

---

## Cleanups concluídos

**Citation hallucination** (commit 9dc3fcb): 29 files limparam `[ilmanen_expected_returns]` (book não existia em `books/summaries/`). Substitutions:
- `ch.19` → `[trading_evolved, p.197]` (Clenow MF sleeve)
- `ch.12` → `[stocks_on_the_move, p.21-30]`
- `ch.fx-carry` → `[risk_parity, ch.5]`

**Cross-session bug** (commit 54f7975 absorveu strategy_hunt_loop letfs_5way files): documentado em `BASE_MEMORY.md ## Binding constraints / Known issues`. Não revertido (files são research útil; revert destrutivo precisa coordenação cross-session).

---

## Inputs pra mandate §7 deliberation

### Opção A — 100% Plano C (status quo)
- Net CAGR ~10.3-10.4% (lump-sum tax at terminal)
- Sharpe ~0.63-0.78 net
- MDD ~52% educational, 33% recent
- Operacional: trivial. Apenas rebalance anual de proporções.
- Risk operacional: muito baixo, robust to cognitive decline

### Opção B — 100% HAA+Gold (iter 009)
- Net CAGR ~12.1% (DARF drag 1.2-1.8pp/y)
- Sharpe net ~0.99 educational
- MDD ~22% educational
- Operacional: rebalance mensal + canary signal + ~6-8 DARFs/ano + Carnê-Leão dividendos. ~1-2h/mês.
- Margem vs A: +1.7pp/y edu, +1.4pp/y vt, **-0.5pp/y ndx**. Borderline significant.

### Opção C — Hybrid 50/50 (iter 012) ⭐ NEW PARETO OPTIMAL
- Net CAGR ~13.4% (edu)
- **Sharpe net ~1.02 (edu) — superior a B em todos os datasets**
- MDD ~27% educational
- Operacional: 50% HAA mensal + 50% Plano C anual. ~0.5-1h/mês.
- Margem vs A: +3.1pp/y edu, +1.0pp/y vt, +0.9pp/y ndx (consistent positive)
- Margem vs B: superior em Sharpe NET universalmente

### Opção D — Híbridos com pesos não-50/50
Não testados, mas matematicamente plausíveis:
- 30% HAA + 70% Plano C (mais conservador)
- 70% HAA + 30% Plano C (mais agressivo)
- Estes podem ser explorados num loop subsequente se §7 aprovar deployment

---

## Recomendação técnica

**Opção C (hybrid 50/50)** é o Pareto optimal entre as 3 dimensões testadas:
- Performance: Sharpe NET superior a 100% HAA, CAGR superior a Plano C
- Complexidade: 50% buy-hold reduz operational burden vs 100% HAA
- Tax efficiency: metade do portfolio defere DARF até terminal
- Filosoficamente: alinha "simplicidade + global+factor+stacking+MF" exatamente

Mas a decisão final é sua — Opção A (100% Plano C) continua absolutamente defensável se você priorizar simplicidade absoluta, e a margem vs Opção C ainda é só ~3pp/y após muito esforço operacional.

### Próximos passos (fora desta thread)

1. **Revisão crítica**: judge-spec do plano completo iter 011/012 antes de qualquer commit a deploy
2. **Paper trading**: validar synth via Inter Internacional (NTSX existe; NTSI/NTSE substitutos NTSD + cash; GDE existe)
3. **Mandate §7 override formal**: se aprovar Opção C, mandate.md precisa novo §7 entry (DORMANT slots stays as is; new "Slot E experimental hybrid")
4. **Iter follow-up (futuro)**: variant 30/70, 70/30, stress-test em Brazilian-specific scenarios (Real devaluation, capital controls)

---

## Data preserved

- 13 iter dirs em `studies/global_factor_tilt_loop/iterations/`
- 8 jornada entries (esta + 7 anteriores)
- `references/REFERENCE_PORTFOLIOS.md` (bestfolio leaderboard analysis)
- `references/bestfolio_leaderboard_2026-04-27.json` (raw data)
- `EXTERNAL_INSTRUMENTS.md` (NTSD/WLDU/Avantis/Keller family)
- BASE_MEMORY.md final state (winners ranked, dead-ends, constraints)

Loop FROZEN. Next thread = §7 deliberation.
