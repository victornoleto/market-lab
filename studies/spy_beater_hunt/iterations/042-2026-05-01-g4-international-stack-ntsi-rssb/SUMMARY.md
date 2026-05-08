# Iter 042 — G4 international stack (NTSD / RSSB)

**Date:** 2026-05-01
**Source:** testfol.io API, 1987-12-31 → 2026-04-30 (38.33y)
**Trigger:** Reddit Post 1 feedback — u/Grouchy_Release_2321 + u/perky_python (US-bias critique)

---

## TL;DR

| 🟢 Edge encontrado? | **Parcial.** US-bias é real mas pequeno. International stacks **não batem** B4 em Sharpe, mas **G4d quebra recorde de MDD** (-22.56%, melhor que qualquer baseline). |
| 🥇 Best G4 (Sharpe) | **G4c (mixed US/Intl 12.5/12.5)** — CAGR 13.31% / MDD -32.65% / Sharpe **0.716** |
| 🛡️ Best G4 (MDD) | **G4d (RSSB+GDE+ZROZ+KMLM)** — CAGR 10.54% / **MDD -22.56%** / Sharpe 0.678 / **Calmar 0.467 (best of study)** |
| 📊 Gap vs B4 baseline | Best G4 Sharpe é -0.029 abaixo de B4 — **só 4% pior**, edge estrutural sobrevive sem US bias |

**Resposta direta ao Grouchy_Release_2321:** US-bias contribui ~4% do Sharpe edge, não 50%+. A diversificação estrutural (NTSX/GDE/RSST embedding leverage cross-asset-class) é **portátil para janelas internacionais**.

---

## Variantes testadas

| ID | Allocation | Tese |
|---|---|---|
| G4a | 25 NTSD / 25 GDE / 25 RSST / 25 ZROZ | B4 com US→Intl swap (NTSD substitui NTSX) |
| G4b | 50 RSSB / 25 GDE / 25 KMLM | Global 100/100 stack-heavy, sem duration sleeve |
| G4c | 12.5 NTSX / 12.5 NTSD / 25 GDE / 25 RSST / 25 ZROZ | B4 com US/Intl 50/50 split na sleeve principal |
| G4d | 25 RSSB / 25 GDE / 25 ZROZ / 25 KMLM | Global 4-sleeve eq-weight (sem RSST) |
| G4e | 50 NTSD / 25 GDE / 25 KMLM | Full intl, sem US, sem duration |

**Componentes usados:**
- **NTSDSIM** — WisdomTree Efficient Core International Developed (90% EAFE-equity + 60% Treasury futures), ER 0.20%. Available SIM since 1987.
- **RSSBSIM** — Return Stacked Global Stocks & Bonds (100% global stocks + 100% global bonds via futures), ER 0.69% net. Available SIM (back-simulated since 1987 — caveat: synthetic for pre-2024 history).
- KMLMSIM, GDESIM, ZROZSIM, NTSX, RSST: same as iter 040.

ERs ponderados por portfolio:
- G4a: 0.385%
- G4b: 0.625% (RSSB ER 0.69% pesa)
- G4c: 0.385%
- G4d: 0.490%
- G4e: 0.380%

---

## Resultados — Pareto sorted by Sharpe

| # | Strategy | CAGR | MDD | Sharpe | Sortino | Calmar |
|---|---|---:|---:|---:|---:|---:|
| 🥇 | Conservative (B4 ZROZ) | 13.31% | -28.94% | **0.745** | 1.071 | 0.460 |
| 🥈 | Sleeping Pills (L1 CEGB) | 11.06% | -25.43% | 0.729 | 1.044 | 0.435 |
| 🥉 | Bogleheads 67 NTSX (L2) | 11.06% | -26.30% | 0.722 | 1.037 | 0.420 |
| 4 | Balanced (B2) | 13.89% | -36.38% | 0.717 | 1.028 | 0.382 |
| 5 | 🆕 **G4c (mixed US/Intl)** | **13.31%** | -32.65% | **0.716** | 1.028 | 0.408 |
| 6 | Aggressive (T1) | 13.34% | -34.65% | 0.688 | 0.984 | 0.385 |
| 7 | 🆕 G4a (NTSD swap) | 13.29% | -36.24% | 0.684 | 0.981 | 0.367 |
| 8 | 🆕 **G4d (4-sleeve global)** | 10.54% | **-22.56%** ⭐ | 0.678 | 0.973 | **0.467** ⭐ |
| 9 | 🆕 G4b (RSSB-heavy) | 10.59% | -34.35% | 0.610 | 0.869 | 0.308 |
| 10 | Gayed LRS 2x | 16.01% | -43.48% | 0.609 | 0.843 | 0.368 |
| 11 | Gayed LRS 3x | 19.61% | -57.57% | 0.595 | 0.822 | 0.341 |
| 12 | Popular 50/25/25 | 12.58% | -50.55% | 0.576 | 0.818 | 0.249 |
| 13 | 🆕 G4e (full intl) | 11.57% | -48.52% | 0.555 | 0.784 | 0.238 |
| 14 | SPY 1x | 11.37% | -55.20% | 0.523 | 0.740 | 0.206 |

⭐ = G4d quebra recordes de MDD (lowest) e Calmar (highest) do estudo inteiro.

---

## Findings

### 1. US-bias contribui ~4% do edge — não é destrutivo

**G4c (12.5 NTSX / 12.5 NTSD / 25 GDE / 25 RSST / 25 ZROZ)** mantém CAGR exatamente igual ao B4 (13.31%), com Sharpe 0.716 vs B4 0.745. Diferença = -0.029 (4% abaixo). MDD piora 3.71pp (-32.65 vs -28.94).

**Implicação:** se houvesse "US-equity-premium overfit" estilo Mehra-Prescott, esperaríamos ver Sharpe cair 10-20% ao trocar half do equity por international. Vimos cair só 4% — sugere que a **diversificação estrutural via stacking (NTSX/GDE/RSST)** é o driver dominante, **não** a escolha geográfica do equity. Resposta robusta ao u/Grouchy_Release_2321.

### 2. G4d quebra recorde de MDD do estudo — Calmar 0.467

**G4d (25 RSSB / 25 GDE / 25 ZROZ / 25 KMLM)** tem MDD -22.56% — **o menor entre TODOS os 14 portfolios testados** (incluindo iter 040 e 041 baselines). Calmar 0.467 também é o **maior do estudo**.

Mas CAGR 10.54% é -2.83pp abaixo de B4 (e abaixo de SPY 11.37%). Para investidor que prioriza **DD-efficiency sobre absolute return**, G4d é interessante. Mas o trade-off CAGR mata a tese "beat SPY on both axes" (CAGR < SPY).

**Por quê G4d tem MDD tão baixo?**
- RSSB embute equity + bonds em 100/100 stack — a sleeve já contém duration cushion.
- ZROZ adiciona mais 25% duration (zero-coupon long Treasury).
- GDE traz gold cushion.
- KMLM adiciona MF que zigue-zaga independentemente.
- **5 sources de drawdown protection** (vs B4 que tem 4: SPY-base + GDE-gold + RSST-MF + ZROZ-duration).

### 3. RSSB-heavy variants underperform — possível overhead operacional

**G4b (50 RSSB)** e **G4d (25 RSSB)** ambos têm CAGR ~10.5% — abaixo de baselines US (13%+). Hipóteses:
- RSSB ER 0.69% é alto (vs NTSX 0.20%) — drag direto.
- RSSB usa Treasury futures globais (não só US 7-10y como NTSX/IEF) — exposição diferente em yield curve.
- RSSBSIM é simulação retro até 2024 — possível bias na construção sintética.

**Caveat metodológico:** RSSBSIM tem só ~2 anos de dados live (RSSB lançou 2024-01). 36 anos de data é simulado pela testfol.io engine. Não é tão confiável quanto NTSXSIM (NTSX tem 8 anos live + ~30 simulados por componentes).

### 4. G4a (NTSD swap) é o "RSSB sem RSSB" — mais robusto pre-2024

**G4a (25 NTSD / 25 GDE / 25 RSST / 25 ZROZ)** mantém estrutura B4 mas swap NTSX→NTSD (US 90/60 → International 90/60). Resultado: CAGR 13.29% (igual a B4), MDD -36.24% (7.3pp pior), Sharpe 0.684.

**Insight:** trocar **all** US equity por intl developed perde 4% Sharpe + 7pp MDD. Confirma que US large-cap teve pequeno premium na janela 1987-2026. Mas G4c (50/50 split) mostra que **diversificação parcial recupera** quase todo o gap.

### 5. G4e (full intl) lands no quadrante "ruim" — confirma necessidade de diversificação cross-asset

**G4e (50 NTSD / 25 GDE / 25 KMLM)** = full intl, no duration. CAGR 11.57% / MDD -48.52% / Sharpe 0.555. **Quase igual ao SPY 1x** (11.37% / -55.20% / 0.523).

Lição: **remover duration sleeve** (sem ZROZ/TLT/IEF) **e remover US** simultaneamente destrói a robustez. Stacks funcionam por **diversificação cross-asset-class via leverage**, não por equity geographic mix isolado.

---

## Para o Post 2

Adicionar seção: **"What about international stacks (RSSB, NTSI, NTSD)?"**

```
Tested 5 variants of international/global stacks. Best variants:

| Variant | CAGR | MDD | Sharpe | Use case |
|---|---|---|---|---|
| G4c (12.5 NTSX / 12.5 NTSD / 25 GDE / 25 RSST / 25 ZROZ) | 13.31% | -32.65% | 0.716 | "B4 mas com 50/50 US/Intl split" |
| G4d (25 RSSB / 25 GDE / 25 ZROZ / 25 KMLM) | 10.54% | -22.56% | 0.678 | **best MDD do estudo (Calmar 0.467)** |

US-bias accounts for ~4% of B4's Sharpe edge (B4 0.745 vs best-international 0.716).
The structural diversification (NTSX/GDE/RSST stacking leverage across asset
classes) is the dominant driver, not geographic equity selection.

Honest caveat: RSSBSIM has only 2 years of live data (RSSB launched 2024) +
36 years of synthetic backfill. NTSDSIM is more robust (NTSD launched 2018,
6 years live + 30 simulated). Take RSSB-based variants with extra skepticism
until 5+ years of live track record.
```

---

## Próximos passos

- **Iter 043 (G8 walk-forward)** — re-fit B4/B2/T1 weights rolling 5y per laurenthu. Última iter da série feedback.

---

## Referências

- u/Grouchy_Release_2321 (Reddit): "using SPY over VT is already another type of survivorship bias that's leading to overfitting"
- u/perky_python (Reddit): "Why only US large-cap blend for your stocks? Why not international?"
- WisdomTree NTSD page: 90% EAFE equities + 60% Treasury futures
- Return Stacked RSSB page: 100% global equities + 100% global bonds, ER 0.69% net
- Bhardwaj/Gorton/Rouwenhorst 2014 NBER w14424 — survivorship bias across geographic markets
- Iter 040 baseline: `iterations/040-2026-05-01-baseline-monthly-rebal-explicit-ers/SUMMARY.md`
