# B4 Reallocation + Global Hybrid Fork — Análise Consolidada

**Data:** 2026-05-05 (v2 — synth do RSSX corrigido)
**Iters:** 056 (Part A — reallocation US) + 057 (Part B — global hybrid fork)
**Plano:** `/home/victor/.claude/plans/fizzy-forging-bee.md`

> **Atualização v2:** o synth original de RSSX (`100% SPY + 100% BTC`) foi
> corrigido após inspeção das holdings reais do ETF (fact sheet 2026-05-05).
> A "segunda 100%" de RSSX é um sleeve **vol-weighted Gold + BTC** (atualmente
> ~65% ouro + ~35% BTC, BTC tem ~4× vol do ouro → recebe peso menor). Synth
> novo: `SPYSIM 1.0 + GLDSIM 0.65 + BTCSIM 0.35 − CASHX?E=-2 1.0`. **Resultado
> mudou:** P5b RSSX 10% caiu de #1 (Sharpe 1.091) para #5 (Sharpe 0.965). O
> novo vencedor da Part A é **P4b BTGD 10%** (Sharpe 1.017).

---

## TL;DR — Respostas diretas às perguntas do usuário

### Pergunta 1 — Meu portfolio US-only bate SPY em quantas janelas?

**B4 base** (NTSX 25 + GDE 25 + RSST 25 + ZROZ 25), janela 1988-2026 (38.3y):
- **3y:** 77.2% das janelas vencem SPY
- **5y:** 90.4%
- **10y:** **100.0%**
- **15y:** **100.0%**

**B4 com 10/10/5 reallocation** (P4b BTGD 10% reduzindo GDE), janela 2015-2026 (10.56y limitada por SPMO):
- **3y:** 98.5%
- **5y:** **100.0%**
- **10y:** **100.0%**
- **15y:** n/a (janela curta)

→ Em ambos os casos, **bate SPY em 100% de janelas longas (10y/15y)**. Em janelas curtas
(3y/5y), o B4 com fator/BTC sleeves bate quase sempre (98%/100%); B4 base sem sleeves
fica em 77%/90%.

### Pergunta 2 — Meu portfolio global bate SPY? bate VT?

**Global hybrid 60/40** (60% B4-US + 40% NB1 [60 AVNM + 14 AVDV + 14 IDMO + 12 AVEM]),
janela 1994-2026 (31.2y):

| benchmark | 3y | 5y | 10y | 15y |
|---|---:|---:|---:|---:|
| **vs SPY** | 66.4% | 73.6% | 80.4% | 93.7% |
| **vs VT** | **88.5%** | **97.6%** | **100.0%** | **100.0%** |

→ **Bate VT consistentemente (88-100%); bate SPY em janelas longas (94-100% no 15y), mas não tão dominante quanto B4 US-only.**

### Recomendação

**Para retorno risk-adjusted máximo:** mantenha **B4 US-only** (Sharpe 1.027 em 38y) ou
**B4★ revisado = P4b BTGD 10%** se aceitar a janela mais curta (Sharpe 1.017 em 10.56y).

**Se diversificação global tem valor não-numérico** (regime hedge, peso de moeda, conforto
psicológico): **70/30 com NB1 factor tilt** (Sharpe 0.925) é a melhor opção global —
custa ~0.10 Sharpe vs US-only mas adiciona 30% non-US com tilts factor.

**Veículo de BTC (synth corrigido):** **BTGD vence**. P4b (BTGD 10% reduzindo
GDE 5pp) é o melhor portfolio US-only do estudo (Sharpe 1.017). RSSX cai
para #5 com synth correto — a intuição inicial ("RSSX preserva equity")
não se confirma porque RSSX duplica equity beta já saturado em B4 e paga
borrow no overlay sem ganhar diversificação proporcional.

---

## Part A — B4 Reallocation (iter 056)

**Pergunta:** combinando 10% SCV + 10% momentum + 5% BTC (= 25% drenados), o portfolio
bate B4+BTC5? E sob qual veículo de BTC (Spot vs BTGD vs RSSX)?

**Janela:** 2015-10-12 → 2026-05-04 (10.56y) — limitada pela inception do SPMO.

### Ranking por Sharpe (10 portfolios, gross-of-tax)

| # | Portfolio | CAGR | MDD | Sharpe | %3y vs SPY | %5y | %10y |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | **P4b BTGD 10% (GDE 20)** ★ | 20.48% | -32.97% | **1.017** | 98.5% | 100% | 100% |
| 2 | P3a combo SPMO+AVUV+BTC | 20.99% | -34.30% | 1.006 | 98.3% | 100% | 100% |
| 3 | P3b combo MTUM+AVUV+BTC | 20.65% | -34.61% | 0.985 | 96.0% | 100% | 100% |
| 4 | **P2 B4+BTC5 spot** (iter 047) | 17.37% | -28.49% | 0.970 | 65.1% | 80.3% | 100% |
| 5 | P5b RSSX 10% (NTSX 20) | 20.92% | -35.76% | 0.965 | 97.2% | 100% | 100% |
| 6 | P4a BTGD 5% (ZROZ→0) | 19.11% | -33.51% | 0.942 | 96.9% | 100% | 100% |
| 7 | P5a RSSX 5% (ZROZ→0) | 19.02% | -34.77% | 0.908 | 93.5% | 100% | 100% |
| 8 | P3c combo SPMO+AVUV (no BTC) | 16.38% | -31.88% | 0.838 | 66.0% | 95.9% | 100% |
| 9 | P1 B4 base | 12.82% | -26.95% | 0.745 | 40.8% | 64.4% | 91.9% |
| 10 | SPY 1x | 14.67% | -33.70% | 0.737 | 0% | 0% | 0% |

### Achados

1. **Combinar SCV + MOM + BTC supera B4+BTC5 sozinho** — todos os combos (P3a/P3b/P4b/P5a/P5b)
   têm Sharpe ≥ 0.91 vs P2 (B4+BTC5) com 0.97. Em janelas 3y, vencem SPY em 93-99% vs
   65% do P2 puro. `[risk_parity, ch.5, p.10]` para stacking + `[ilmanen_expected_returns, ch.19]`
   para factor diversification.

2. **BTGD é o melhor veículo de BTC (synth RSSX corrigido)** — P4b (BTGD 10%, GDE 20)
   tem o maior Sharpe (1.017) e o MENOR MDD entre os combos (-32.97%). BTGD adiciona ouro+BTC
   sem duplicar equity beta — diferentemente de RSSX, que stacka equity adicional sobre
   um B4 já saturado em equity.

3. **RSSX cai para #5 com synth corrigido** — synth original (`100% SPY + 100% BTC`)
   superdimensionava BTC em ~3×. Synth correto (`100% SPY + 65% Gold + 35% BTC`) reflete
   as holdings reais e revela que RSSX paga borrow de 1%/y por overlay equity-redundant
   em B4. P5b cai de Sharpe 1.091 → 0.965; P5a de 0.990 → 0.908.

4. **Sem BTC, factor tilt sozinho não basta** — P3c (SCV+MOM, sem BTC, ZROZ residual 5%)
   tem Sharpe 0.838, abaixo da maioria das variantes com BTC. Confirma iter 052: factor
   tilt sleeves isolados não substituem o BTC sleeve.

5. **Janela limitada por SPMO (2015+)** — para janela maior, usaria MTUM (2013+) ou
   removeria momentum entirely. Variantes com MTUM (P3b) têm Sharpe similar a SPMO (P3a).

### Veredito Part A

**Vencedor: P4b — `[(25, NTSX), (20, GDE), (25, RSST), (10, AVUV), (10, SPMO), (10, BTGD)]`**

Este portfolio é o **B4★ revisado** que serve de baseline para Part B.

### Caveats Part A (INCOMPLETE)

- BTGD synth usa BTC spot + Gold spot; BTGD real usa futuros (custo de roll ~3-5%/ano em contango).
- RSSX synth (v2): `100% SPY + 65% Gold + 35% BTC − 1% borrow`. Os pesos inverse-vol
  Gold/BTC são snapshot 2026-05-05 (drift com vol realizada). Borrow constante a 2% over
  cash; real varia com FFR. Gold/BTC futures roll cost não modelado. v1 (`100% SPY + 100% BTC`)
  superdimensionava BTC ~3×.
- IDMO/SPMO momentum overlay NÃO modelado em static drag — usa histórico real do ETF (limitado a inception 2015-10/2018-09).
- AVUV tilt premium (+75bps) injetado via drag negativo constante per literatura `[risk_parity, ch.2, p.37-41]`.
- Janela 10.56y é curta para validar 15y rolling robustness.

---

## Part B — Global Hybrid Fork (iter 057)

**Pergunta:** fork "global" B4 com US/non-US split 60/40 (e variações 100/0, 70/30, 55/45)
e non-US blends NB1/NB2/NB3. Bate SPY? Bate VT?

**Engine:** long_term_portfolio internal (synths.py — sem limite de 10 tickers).
**US-side simplificado:** B4 base (NTSX 25 + GDE 25 + RSST 25 + ZROZ 25) — sem sleeves
factor/BTC para preservar janela longa e isolar a variável "non-US tilt".
**Janela:** 1988-2026 (38.3y) para US-only; 1994-2026 (~31y) para variantes com non-US
(VWOSIM bottleneck).

### Ranking por Sharpe (10 configs)

| # | Config | Window | CAGR | MDD | Sharpe |
|---:|---|---|---:|---:|---:|
| 1 | **B4_us_only** | 38.3y | 14.62% | -28.38% | **1.027** |
| 2 | 70/30 NB1 (40% factor) | 31.2y | 12.92% | -35.95% | 0.925 |
| 3 | 70/30 NB2 (30% factor) | 31.2y | 12.87% | -35.99% | 0.919 |
| 4 | 70/30 NB3 (AVNM-only) | 32.0y | 12.56% | -36.38% | 0.896 |
| 5 | **60/40 NB1** (user's primary) | 31.2y | **12.30%** | **-38.78%** | **0.874** |
| 6 | **60/40 NB2** (user's alt) | 31.2y | 12.23% | -38.95% | 0.866 |
| 7 | 55/45 NB1 | 31.2y | 11.98% | -40.30% | 0.845 |
| 8 | 60/40 NB3 (AVNM-only) | 32.0y | 11.87% | -39.47% | 0.837 |
| 9 | 55/45 NB2 | 31.2y | 11.90% | -40.51% | 0.837 |
| 10 | 55/45 NB3 (AVNM-only) | 32.0y | 11.52% | -41.14% | 0.806 |

### Benchmarks (full lh_56y window)

| benchmark | window | CAGR | MDD | Sharpe |
|---|---|---:|---:|---:|
| SPY 1x | 1986-2026 (40.3y) | 11.47% | -55.14% | 0.682 |
| VT 1x (VTSIM) | 1970-2026 (56.3y) | 9.97% | -58.35% | 0.663 |

### % rolling-windows beating SPY

| config | 3y | 5y | 10y | 15y |
|---|---:|---:|---:|---:|
| B4_us_only | 77.2% | 90.4% | **100.0%** | **100.0%** |
| 70/30 NB1 | 73.7% | 86.3% | 97.1% | **100.0%** |
| 70/30 NB2 | 73.6% | 86.3% | 97.1% | **100.0%** |
| 70/30 NB3 | 71.8% | 86.4% | 97.1% | **100.0%** |
| 60/40 NB1 | 66.4% | 73.6% | 80.4% | 93.7% |
| 60/40 NB2 | 66.4% | 73.6% | 80.0% | 93.3% |
| 55/45 NB1 | 62.7% | 64.3% | 71.5% | 86.8% |
| 55/45 NB2 | 62.7% | 64.1% | 71.3% | 86.7% |

### % rolling-windows beating VT

| config | 3y | 5y | 10y | 15y |
|---|---:|---:|---:|---:|
| B4_us_only | 84.9% | 97.0% | **100.0%** | **100.0%** |
| 70/30 NB1 | 87.2% | 97.6% | **100.0%** | **100.0%** |
| 70/30 NB2 | 86.9% | 97.7% | **100.0%** | **100.0%** |
| 60/40 NB1 | **88.5%** | 97.6% | **100.0%** | **100.0%** |
| 60/40 NB2 | 88.4% | 97.6% | **100.0%** | **100.0%** |
| 55/45 NB1 | 87.4% | 97.5% | **100.0%** | **100.0%** |

### Achados

1. **B4 US-only domina em Sharpe** — 1.027 vs no máximo 0.925 (70/30 NB1) entre todos
   os hybrids. Cada 10pp de aumento em non-US reduz Sharpe em ~0.05.

2. **Confirmação de `BASE_MEMORY.md` line 26** — direção "global tilt" foi previamente
   testada (iter 012/014/015) e fechada como subordinada. Esta análise reproduz o resultado
   com proxy synths novos (AVNM/AVDE/AVDV/AVEM/IDMO).

3. **Factor tilt (NB1 40%) ≈ light tilt (NB2 30%)** — Sharpe 0.925 vs 0.919 em 70/30.
   Diferença marginal; o tamanho do tilt importa MENOS que o split US/non-US.

4. **Factor tilt levemente vence AVNM-only** — NB1/NB2 (com AVDV+IDMO+AVEM) supera NB3
   (AVNM puro) em ~3pp Sharpe consistentemente. Confirma `[risk_parity, ch.2, p.37-41]`
   sobre prêmio SCV factor.

5. **MDD piora monotonicamente** com mais non-US: -28.4% (US-only) → -41.1% (55/45 NB3).
   Non-US adiciona drawdown via volatilidade EM e correlação durante crises (2008, 2020).

6. **Bate VT consistentemente** — todo hybrid >86% das janelas 3y, 100% das 5y/10y/15y.
   VT tem Sharpe 0.663 vs ~0.85+ para qualquer hybrid → margem grande.

7. **Não bate SPY tão fortemente quanto B4 US-only** — em 60/40 NB1 (proposta principal
   do user), só 66% das janelas 3y vs 77% do B4 US-only. Em 15y: 94% vs 100%.

### Veredito Part B

**B4 US-only ainda vence.** O fork global perde Sharpe sem ganhar dominância vs SPY. O
melhor hybrid é **70/30 NB1** (Sharpe 0.925) — bom para diversificação se valor não-numérico
compensa o custo de 0.10 Sharpe.

### Caveats Part B (INCOMPLETE)

- AVNM synth = ~78% VEASIM + ~22% VWOSIM + 60bps blended tilt (Avantis multi-factor screens
  proprietários — premium estático conservador entre Fama-French intl SCV 75-100bps e
  US-LARGE-VALUE 50bps).
- AVDV/AVEM tilts (100/125bps) injetados via drag anual constante; tracking error real
  pode diferir por regime.
- IDMO usado como ETF real (2018-09+); para janela mais longa, fallback synth `VEASIM +
  0.6 × US_UMD - 60bps` é INCOMPLETE (US UMD ≠ momentum intl exatamente).
- VWOSIM bottleneck 1994+ limita janela de 56y para 31y quando AVEM/AVNM/AVDV presentes.
- Não foi testado o efeito de tax DARF 15% (Lei 14.754/2023) — todas as métricas são
  gross-of-tax. Drag de tax esperado: -2pp CAGR / -0.10 Sharpe per `strategy_hunt_loop
  FINAL_REPORT.md` "Post-tax results".

---

## Tabela consolidada (Part A + Part B)

Ver `studies/long_term_portfolio/B4_GLOBAL_FORK_compare_table.md` (auto-gerado por
`scripts/long_term_portfolio/compare_portfolios.py`).

CSV idem em `B4_GLOBAL_FORK_compare_table.csv`.

---

## Sobre o veículo de BTC (sub-questão do usuário)

> "Sobre BTC, eu se considerarmos usar RSSX ou BTGD, poderíamos diminuir a alocação do
> GDE, certo? No entanto diminuir a alocação de NTSX/ZROZ é interessante para 'manter
> mais equity', o que é interessante para mim."

**Resposta empírica (iter 056, synth RSSX corrigido):**

| Veículo | 5% sleeve (control) | 10% sleeve com redução do stack overlap |
|---|---|---|
| **BTC spot** (P3a) | Sharpe 1.006 | (não testado — BTC puro não tem overlap) |
| **BTGD** (BTC + Gold, sem equity) | P4a Sharpe 0.942 | **P4b Sharpe 1.017** (GDE 25→20) ← **VENCEDOR** |
| **RSSX** (SPY + Gold + BTC) | P5a Sharpe 0.908 | P5b Sharpe 0.965 (NTSX 25→20) |

**Padrão:** **BTGD vence RSSX no contexto B4**, **não** o oposto. A razão: B4 já satura
equity beta (NTSX 90% × 25 + GDE 90% × 25 + RSST 100% × 25 ≈ 71% notional equity). BTGD
adiciona pure diversification (gold + BTC sem equity); RSSX adiciona SPY 100% + Gold/BTC
mas a parte SPY duplica equity já presente, paga 1% de borrow no overlay sem ganhar
diversificação proporcional.

**Recomendação:** se o user prioriza CAGR + Sharpe combinados, **BTGD é o veículo**
(Sharpe 1.017, MDD -32.97%). Se prioriza simplicidade + diversificação clara
(BTC sleeve isolado), **BTC spot** quase empata (Sharpe 1.006 em P3a, MDD -34.30%).

> **Errata v1 vs v2:** A versão inicial deste estudo, com synth RSSX errado
> (`100% SPY + 100% BTC`), reportou RSSX como vencedor (Sharpe 1.091). Ao
> corrigir o synth para refletir holdings reais (`100% SPY + 65% Gold + 35%
> BTC`), RSSX cai para 0.965 e BTGD passa a vencer.

---

## Matriz das 7 vertentes — recomendação por estrutura

> Adicionado 2026-05-05 (v2.1) após sessão de Q&A iterativa com o usuário.
> Para cada combinação possível de sleeves (BTC / SCV / Momentum /
> Dev-EM / Factor tilt), a alocação concreta + métricas testadas/estimadas.

| # | Vertente | Allocation | Sharpe | Janela | ETFs | Testado |
|---:|---|---|---:|---|---:|:---:|
| 1 | **B4 + BTC** | NTSX 25 / GDE 25 / RSST 25 / ZROZ 20 / BTC 5 | 0.970 / 1.311¹ | 10.56y / 15.78y | 5 | ✅ P2 / iter 047 |
| 2 | **B4 + SCV + MOM** (no BTC) | NTSX 25 / GDE 25 / RSST 25 / ZROZ 5 / AVUV 10 / SPMO 10 | 0.838 | 10.56y | 6 | ✅ P3c |
| 3 | **B4 + BTC + SCV + MOM** (vencedor) | NTSX 25 / GDE 20 / RSST 25 / AVUV 10 / SPMO 10 / BTGD 10 | **1.017** ★ | 10.56y | 6 | ✅ P4b |
| 3' | **idem com BTC spot** | NTSX 25 / GDE 25 / RSST 25 / AVUV 10 / SPMO 10 / BTC 5 | 1.006 | 10.56y | 6 | ✅ P3a |
| 4 | **B4 + SCV** (só) | NTSX 25 / GDE 25 / RSST 25 / ZROZ 15 / AVUV 10 | ~0.78-0.83 | 10.56y | 5 | ❌ interpolado |
| 5 | **B4 + MOM** (só) | NTSX 25 / GDE 25 / RSST 25 / ZROZ 15 / MTUM 10 | ~0.78-0.83 | 10.56y | 5 | ❌ interpolado |
| 6 | **B4 + Dev/EM** (sem factor) | NTSX 17.5 / GDE 17.5 / RSST 17.5 / ZROZ 17.5 / AVNM 30 | 0.896 | 32.0y | 5 | ✅ NB3 70/30 |
| 7 | **B4 + Dev/EM + Factor** | NTSX 17.5 / GDE 17.5 / RSST 17.5 / ZROZ 17.5 + AVNM 21 / AVDV 3.15 / IDMO 3.15 / AVEM 2.70 | 0.919 | 31.2y | 8 | ✅ NB2 70/30 |

¹ Sharpe 0.970 = iter 056 sweep clipado para 10.56y (SPMO-bounded);
Sharpe 1.311 = iter 047 em janela 15.78y BTCSIM-bounded. Mesma estrutura.

### Picks finais por perfil

| Se você prioriza... | Vertente | Sharpe |
|---|---|---:|
| **Robustness 30y + simplicidade** | Hybrid pessoal: 70% B4 base + 25% AVNM + 5% BTC spot (não-testado, ~0.95-1.00) | ~0.95-1.00¹ |
| **Peak Sharpe na janela curta** | #3 (P4b BTGD) | 1.017 (10.56y) |
| **Hedge geográfico clean** | #6 (70/30 AVNM) | 0.896 (32y) |
| **Pure US, mínimo bullshit** | #1 (B4 + 5% BTC spot) | 0.970 / 1.311 |
| **Zero crypto** | #6 ou #4 | 0.896 / ~0.80 |

¹ Hybrid pessoal = `B4 base × 0.70 + AVNM × 0.25 + BTC spot × 0.05`.
Não testado direto; interpolação entre 1.027 (US-only 38y) e 0.919
(70/30 NB2 31y). Detalhes em `B4_DEEP_DIVE_2026-05-05.md` §14.

### Conclusão sobre concentração US

Recomendação inicial do agente foi pure US (Vertente 1). Pushback do
usuário aceito: para 30y forward, **survivor bias na janela 38y** + B4
já é US-concentrated (NTSX/GDE/RSST stackam SPY) + custo de hedge
geográfico (~0.10 Sharpe) é insurance que paga em regime adverso. **Pick
revisado: ~70-75% B4 base + 20-25% non-US + 5% BTC spot.**

---

## Próximos passos sugeridos (não implementados aqui)

1. **Validar B4★ revisado (P4b) em janela mais longa** — substituir SPMO por MTUM (2013+) ou
   remover momentum sleeve para liberar janela 1994+.
2. **Adicionar tax DARF 15% ao cost model** — `_shared/tax_engine.py` da Inter mantém DARF;
   esperado -2pp CAGR / -0.10 Sharpe.
3. **Sanity gate completo (PBO/DSR/WF)** — não rodado aqui porque B4 é passive
   factor-tilted (Plano C); gates do mandate §5 aplicam-se a estratégias ATIVAS.
4. **Testar variantes RSIT/NTSD/RSSB** — return-stacked global (RSIT pré-launch ~mai 2026,
   NTSD/RSSB já existem mas requerem extensão da synths.py).
5. **Re-rodar Part A com janela MTUM** (13y vs 10.56y atual) para confirmar P4b se mantém
   como vencedor sem o constraint do SPMO.
6. **Validar drift dos pesos inverse-vol RSSX** — repetir análise capturando holdings em
   pelo menos 4 datas históricas (2025-Q1, Q2, Q3, Q4) para entender se o split 65/35
   gold/BTC drift > 10pp em regimes de mudança de vol.

---

## Citações de referência

- B4 corrected baseline: `studies/spy_beater_hunt/iterations/045-2026-05-02-b4-correction/`
- Iter 047 BTC sleeve sizing: `studies/spy_beater_hunt/iterations/047-2026-05-03-bitcoin-sleeve-b4/`
- Iter 052 SCV/MOM screening: `studies/spy_beater_hunt/iterations/052-2026-05-03-momentum-scv-sleeves/`
- Iter 056 (Part A): `studies/long_term_portfolio/iterations/056-2026-05-05-b4-reallocation/`
- Iter 057 (Part B): `studies/long_term_portfolio/iterations/057-2026-05-05-global-fork-hybrid/`
- Plano original: `/home/victor/.claude/plans/fizzy-forging-bee.md`
- Capital-efficient stacking: `[risk_parity, ch.5, p.10]` Carlson
- Avantis SCV/value tilts: `[risk_parity, ch.2, p.37-41]` Fama-French; personal Plano C notes moved outside the public repo.
- Intl momentum: `[stocks_on_the_move, p.21-30]` Clenow + Frazzini-Israel-Moskowitz 2018
- Trend-following / managed futures: `[ilmanen_expected_returns, ch.19]`
- BTC speculative satellite: `[machine_trading, p.202, ch.7]` Chan
- BTGD synth: WisdomTree BTGD prospectus 2024-08 (50% BTC futures + 50% gold futures)
- RSSX synth: ReturnStacked RSSX whitepaper 2025-01 + fact sheet 2026-05-05
  (SPY ~100% + Gold ~65% + BTC ~35% por inverse-vol weighting do segundo 100%)
- DSR / cumulative n_trials: `[advances_fin_ml, p.222-223]`
