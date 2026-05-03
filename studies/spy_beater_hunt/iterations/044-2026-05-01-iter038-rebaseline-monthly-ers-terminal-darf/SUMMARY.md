# Iter 044 — re-baseline iter 038 sweep com Monthly + ERs + terminal DARF

**Date:** 2026-05-01
**Source:** testfol.io API
**Trigger:** user feedback 2026-05-01 — "use Monthly rebal in all contexts. Tax = 1 DARF/year on net profit, losses offset gains within year."

---

## TL;DR

Re-rodei os **14 configs do iter 038 sweep** com a **mesma metodologia** dos iter 040/041/042 (Monthly rebal + ERs reais via testfol.io). Aplicquei tax model **lazy-rebal terminal DARF** (user contribui mensalmente mas NUNCA vende → realized gains = 0 durante accumulation → DARF 15% só no terminal sobre lucro acumulado).

**Ranking unificado** substitui as duas tabelas inconsistentes anteriores (iter 038 Yearly + no-ER + post-tax vs iter 040 Monthly + ERs + pre-tax).

**Update 2026-05-02 — superseded for RSST by iter 045:** esta tabela expandiu `RSST` como `SPYSIM + KMLMSIM - CASHX` com ER real de RSST no `drag`. O iter 045 re-rodou os mesmos configs com `SPY + 70% DBMF + 30% KMLM - CASHX?E=-2` em janela comum 2000+. Use `iterations/045-2026-05-02-rsst-proxy-7030-rebaseline/SUMMARY.md` como leitura corrigida para RSST. Fundamento: return stacking `[risk_parity, ch.5, p.10]` + diversificação de managed-futures engines `[ilmanen_expected_returns, ch.19]`.

| # | strategy | window | gross CAGR | **net CAGR** | MDD | Sharpe | Calmar |
|---|---|---|---:|---:|---:|---:|---:|
| 🥇 | **B4 ZROZ** | 38.33y | 13.31% | **12.84%** | **-28.94%** | **0.745** | 0.460 |
| 🥈 | B3 TLT instead of TMF | 38.33y | 12.44% | 11.98% | -30.06% | 0.735 | 0.414 |
| 🥉 | L1 CEGB proxy | 38.33y | 11.06% | 10.60% | **-25.43%** | 0.729 | 0.435 |
| 4 | L2 Bogleheads 67% NTSX | 38.33y | 11.06% | 10.60% | -26.30% | 0.722 | 0.420 |
| 5 | B2 TMF10 balanced | 38.33y | 13.89% | **13.42%** | -36.38% | 0.717 | 0.382 |
| 6 | T2 equity-heavy | 38.33y | 13.40% | 12.93% | -33.14% | 0.708 | 0.404 |
| 7 | T1 gold-heavy | 38.33y | 13.34% | 12.87% | -34.65% | 0.688 | 0.385 |
| 8 | B5 no duration | 38.33y | **14.22%** | **13.74%** | -41.12% | 0.687 | 0.346 |
| 9 | B1 user baseline 25 TMF | 38.33y | 12.93% | 12.46% | -38.78% | 0.665 | 0.333 |
| 10 | M4 RSST+KMLM blend | 38.33y | 11.85% | 11.38% | -37.27% | 0.645 | 0.318 |
| 11 | T3 RSSB global | 38.33y | 12.31% | 11.85% | -41.39% | 0.623 | 0.298 |
| 12 | M2 DBMF no RSST ⚠ | 26.32y | 9.76% | 9.15% | -37.97% | 0.610 | 0.257 |
| 13 | M1 KMLM no RSST | 38.33y | 10.74% | 10.29% | -35.92% | 0.610 | 0.299 |
| 14 | M3 KMLM+DBMF blend ⚠ | 26.32y | 9.56% | 8.95% | -36.94% | 0.600 | 0.259 |
| — | **SPY 1× buy-hold** | 38.33y | 11.37% | **10.91%** | -55.20% | 0.523 | 0.206 |

⚠ M2 e M3 contêm DBMF (DBMFSIM start 2000-01) → janela 26.32y vs 38.33y dos outros. Não comparáveis diretamente em CAGR absoluto.

---

## Beats SPY on BOTH net CAGR AND MDD (9 strategies)

| strategy | net CAGR | MDD | Sharpe | comentário |
|---|---:|---:|---:|---|
| **B4 ZROZ** ⭐ | 12.84% | -28.94% | **0.745** | best Sharpe; ZROZ removes LETF decay tax |
| B3 TLT | 11.98% | -30.06% | 0.735 | TLT 1× backup se ZROZ não disponível |
| B2 TMF10 balanced | 13.42% | -36.38% | 0.717 | high CAGR, +13pp MDD vs B4 |
| T2 equity-heavy | 12.93% | -33.14% | 0.708 | NTSX 35%, less duration |
| T1 gold-heavy | 12.87% | -34.65% | 0.688 | era Post 1 pick, demoted |
| B5 no duration | 13.74% | -41.12% | 0.687 | high CAGR mas borderline MDD |
| B1 user baseline 25 TMF | 12.46% | -38.78% | 0.665 | user's original spec — TMF 25% custa MDD |
| M4 RSST+KMLM blend | 11.38% | -37.27% | 0.645 | dual MF source ok |
| T3 RSSB global | 11.85% | -41.39% | 0.623 | global stack, MDD inflado |

---

## Key changes vs iter 038 (Yearly + no-ER + post-tax) e iter 040 (Monthly + ERs + pre-tax)

| metric | iter 038 reported | iter 044 (this) | reason |
|---|---|---|---|
| T1 NET CAGR | 15.82% | **12.87%** | +ER drag (0.36pp) + Monthly rebal effect (~0.85pp on T1's TMF 20%) + different tax timing assumption |
| T1 NET MDD | 33.42% | **34.65%** | Monthly rebal magnifies TMF leverage drawdowns (-1.23pp) |
| T1 NET Sharpe | 0.990 | **0.688** | metodologias e Sharpe definitions diferentes (testfol.io Rf-adjusted vs internal raw) |
| B4 NET CAGR | 13.79% | **12.84%** | small drag, near-identical ranking |
| B4 NET MDD | 28.02% | **28.94%** | virtually unchanged |
| Winner | T1 gold-heavy | **B4 ZROZ** | T1 demoted (TMF 20% × monthly hurts); B4 promoted |

**Conclusão**: o ranking T1 → B4 swap é **real e robusto** quando testado com metodologia realista (Monthly rebal ≈ user behavior + ERs reais + tax model honest).

---

## Tax model — terminal DARF (lazy rebal via aportes)

User confirmou behavior: contribui mensalmente, **nunca vende** durante accumulation. Implicação:
- Realized gains durante o ano = 0
- DARF anual = 0 (nada a tributar)
- DARF total = 15% × lucro acumulado **no terminal** quando vender tudo

Fórmula:
```
gross_final = $10k × (1 + gross_CAGR)^years
profit = gross_final - $10k
darf_terminal = 0.15 × profit  (apenas se profit > 0)
net_final = gross_final - darf_terminal
       = 0.85 × gross_final + 0.15 × $10k
net_CAGR = (net_final / $10k)^(1/years) - 1
```

**Drag observado na tabela**: net CAGR ≈ gross CAGR − 0.46pp para janelas de ~38y. Para janelas mais longas, drag amortiza menor (compounded vs single-shot).

**Caveat**: se rebal forçado (não-lazy) gera realized gains intra-ano → DARF anual recorrente → drag maior (~1.5-2pp como reportado em iter 038's NET para LRS strategies). Static buy-hold com aportes é o caso favorável.

---

## Methodology consistency check

Verificação L1 entre iter 040 e iter 044:
- iter 040 L1: CAGR=11.06% MDD=-25.43% Sharpe=0.7293 ✓
- iter 044 L1 (após refetch_b): CAGR=11.06% MDD=-25.43% Sharpe=0.7293 ✓

**Apples-to-apples confirmed.** Diferença anterior era artifact de DBMFSIM (start 2000-01) clipping batch_b para 26y. Resolved via refetch_b.py — DBMF configs (M2, M3) agora rodam em batch separado (`backtest_d.json`) com janela honesta 26.32y.

---

## Implications

1. **B4 Conservative (25 NTSX / 25 GDE / 25 RSST / 25 ZROZ) é o deploy candidate canônico.** net CAGR 12.84% / MDD -28.94% / Sharpe 0.745.

   Caveat 2026-05-02: canônico sob proxy RSST antigo (`KMLM-only`). O re-run corrigido está no iter 045: B4 gross 11.00% / net 10.36% / MDD -29.60% / Sharpe 0.671 em janela comum 2000+.

2. **Paretto frontier (CAGR vs MDD)** com 9 estratégias dominantes vs SPY. B4 está na ponta de melhor Sharpe; B5/B2/T2 oferecem mais CAGR ao custo de MDD; L1/L2 oferecem menos MDD ao custo de CAGR.

3. **MF-source matters menos do que pensávamos**: M1 (KMLM) e M4 (RSST+KMLM) janela 38y comparable, ambos fazem o trabalho. M2/M3 tem janela curta — não fair compare.

4. **TMF 25% original (B1) é Pareto-suboptimal**: net CAGR 12.46% / MDD -38.78% — pior em ambos vs B4. TMF dose-down (B2 10%) ou ZROZ swap (B4) Pareto-improve.

---

## Próximos passos

- Atualizar `TOP_STRATEGIES.md` removendo "SUPERSEDED" da seção iter 038, substituindo pela tabela unificada deste iter 044.
- Atualizar `REDDIT_POST_2_technical.md` com tabela única (gross + net) substituindo as duas anteriores.
- Atualizar `WINNER_AND_RANKING.md` com novo ranking canônico.
