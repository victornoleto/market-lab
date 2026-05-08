# Iter 040 — Baseline ajustada (Monthly rebal + ERs reais)

**Date:** 2026-05-01
**Source:** testfol.io API, common start 1987-12-31 → 2026-04-30 (38.33y)
**Trigger:** feedback do Reddit Post 1 (u/perky_python, u/laurenthu)

---

## TL;DR

| Mudança aplicada | Resultado |
|---|---|
| Top-level rebal **Yearly → Monthly** | MDD do **Popular 50/25/25 piorou -10.71pp** (blowup). Stacks NTSX/GDE/RSST quase imunes (<0.5pp). LRS sem mudança (signal-driven). |
| ERs reais via `drag` no testfol.io | CAGR caiu -0.5 a -0.9pp em todos os stacks (esperado). SPY 1x apenas -0.11pp. |
| Sharpe combinado | -0.05 a -0.06 em todos os stacks NTSX/GDE/RSST. Popular cai -0.06. **Ranking Pareto preservado.** |

**Conclusão:** ajuste metodológico **não altera a hierarquia** das 4 estratégias do Post 1. **Popular 50/25/25 cai mais um degrau** no ranking (já era o pior dos 5 stacks; agora o gap aumenta). LRS Gayed permanece dominado por todos os stacks em Sharpe.

---

## Metodologia

### Mudanças vs iter 039

1. **Rebalance freq top-level:** `Yearly` → `Monthly` em todos os 6 portfolios multi-asset (SPY 1× fica `None` por ser single-asset).
   - Justificativa: o **rebal interno** dos ETFs (NTSX/GDE quarterly, RSST daily) é responsabilidade do emissor [WisdomTree NTSX FAQ, ReturnStacked RSST page]. O **rebal top-level** é nosso e foi forçado para mensal por aderência ao mandate (`docs/investment-mandate.md` §1) e ao fluxo Inter Internacional (aporte mensal natural).

2. **ERs reais via `drag` do testfol.io API:**

| ETF | ER (% a.a.) | Fonte |
|---|---|---|
| NTSX | 0.20 | WisdomTree NTSX Fund page |
| GDE  | 0.20 | WisdomTree GDE Fund page |
| RSST | 0.99 | ReturnStackedETFs.com / SEC 497K |
| KMLM | 0.92 | KraneShares prospectus |
| GLD  | 0.40 | State Street prospectus |
| TLT  | 0.15 | iShares prospectus |
| ZROZ | 0.15 | PIMCO prospectus |
| IEF  | 0.15 | iShares prospectus |
| SPY  | 0.0945 | State Street SPDR |
| SSO  | 0.89 | ProShares (já no `SPYSIM?L=2&E=0.89`) |
| UPRO | 0.91 | ProShares (já no `SPYSIM?L=3&E=0.91`) |
| TMF  | 1.05 | Direxion (já no `TLTSIM?L=3&E=1.05`) |

   ERs já bakeados nos SIMs leveraged (SSO/UPRO/TMF) **não foram duplicados** no `drag` per-portfolio.

   Fórmula: `drag_portfolio = Σ(weight_i × ER_i)` para os ETFs não-leveraged.

   Drag aplicado por portfolio:
   - SPY 1x: 0.094%
   - Popular 50/25/25: 0.138%
   - L1 Sleeping pills: 0.317%
   - L2 Bogleheads: 0.296%
   - **B4 Conservative: 0.385%**
   - **B2 Balanced: 0.417%**
   - **T1 Aggressive: 0.358%**

### O que NÃO mudou

- Lista das 9 portfolios (mesmas alocações)
- Decomposição via SIM tickers
- Janela de comum start (1987-12-31, limitada por KMLMSIM)
- Métricas (CAGR/MDD/Sharpe Rf-adjusted) extraídas de `stats[i]` da resposta testfol.io

---

## Comparação iter 039 vs iter 040

| Portfolio | CAGR_039 | CAGR_040 | ΔCAGR | MDD_039 | MDD_040 | ΔMDD | Sh_039 | Sh_040 | ΔSh |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SPY 1x | 11.48% | 11.37% | -0.11 | -55.14% | -55.20% | -0.06 | 0.528 | 0.523 | -0.005 |
| **Popular 50/25/25** | 13.47% | 12.58% | -0.89 | -39.84% | **-50.55%** | **-10.71** | 0.637 | 0.576 | -0.061 |
| Sleeping pills (L1) | 11.56% | 11.06% | -0.50 | -22.27% | -25.43% | -3.16 | 0.782 | 0.729 | -0.053 |
| Bogleheads (L2) | 11.55% | 11.06% | -0.49 | -22.48% | -26.30% | -3.83 | 0.778 | 0.722 | -0.056 |
| **Conservative (B4)** | 13.96% | 13.31% | -0.65 | -28.65% | -28.94% | -0.29 | **0.798** | **0.745** | -0.053 |
| **Balanced (B2)** | 14.61% | 13.89% | -0.71 | -36.21% | -36.38% | -0.17 | 0.772 | 0.718 | -0.054 |
| **Aggressive (T1)** | 14.19% | 13.34% | -0.85 | -30.66% | -34.65% | -3.99 | 0.744 | 0.688 | -0.056 |
| Gayed LRS 2x | 15.62% | 16.01% | +0.39 | -43.49% | -43.48% | +0.01 | 0.595 | 0.609 | +0.014 |
| Gayed LRS 3x | 18.77% | 19.61% | +0.84 | -57.59% | -57.57% | +0.02 | 0.575 | 0.595 | +0.019 |

**Pareto shift visualizado:** `plot_3_pareto_shift.png` (círculo = iter 039 Yearly, quadrado = iter 040 Monthly+ER, seta mostra deslocamento).

---

## Findings

### 1. Popular 50/25/25 quebra com monthly rebal — **nova lição**

**MDD passa de -39.84% → -50.55% (-10.71pp)** ao trocar Yearly por Monthly. Porquê:
- Allocation: 50% SSO (2× SPY) + 25% GLD + 25% ZROZ.
- Em bear markets de equity (2008, 2022), SSO 2× cai dobro do SPY. Monthly rebal **força recomprar SSO** mensalmente para manter peso 50%, **acelerando a sangria**.
- Yearly rebal naturalmente "deixa SSO morrer" durante o ano e só recompõe no fim — efeito de mean-reversion benéfico ao PME.

**Implicação prática:** o Popular 50/25/25 é **vulnerável à cadência de rebal** que o usuário escolher. Se você for rebal mensal (aporte mensal típico), o MDD real é -50% não -40%. Isso destroça o argumento "Sharpe similar ao SPY" — ele agora é estritamente pior em risco.

**Aderência ao mandate:** Tier MDD baseline B4/B2/T1 caiu para `Válido` (-25 a -45% per `docs/investment-mandate.md`). Popular 50/25/25 cai para `Marginal`.

### 2. Stacks NTSX/GDE/RSST quase imunes ao monthly rebal

- B4 Conservative: ΔMDD -0.29pp (de -28.65% para -28.94%) — **virtualmente sem efeito**
- B2 Balanced: ΔMDD -0.17pp — sem efeito
- T1 Aggressive: ΔMDD -3.99pp (de -30.66% para -34.65%) — moderado, atribuível ao TMF 20% (alavancado 3× em duration)
- L1, L2: ΔMDD -3 a -4pp — moderado

Por que? Os stacks NTSX/GDE/RSST embedam suas próprias diversifications internamente (cada um tem equity + outro asset class no mesmo ETF). Rebal top-level mensal não cria momentum-against-trend tão forte porque os stacks já contêm a diversificação intra-ETF.

**Implicação:** o argumento estrutural do Post 1 (return-stacking via NTSX/GDE/RSST domina static SSO+diversifier) **se fortalece** quando saímos do regime Yearly idealizado para Monthly realista.

### 3. LRS Gayed melhora levemente — não significativo

LRS 2x: CAGR +0.39pp, Sharpe +0.014. LRS 3x: CAGR +0.84pp, Sharpe +0.019.

Diferença vem de como testfol.io aplica `E=` no SIM ticker (iter 040) vs `drag` no alloc_leg (iter 039). Magnitude pequena, **não muda o ranking** — LRS 2x/3x continuam **abaixo** de todos os stacks B4/B2/T1 em Sharpe (0.609 / 0.595 vs 0.745 / 0.718 / 0.688).

### 4. CAGR drag confirma feedback do u/perky_python

u/perky_python escreveu: *"the CAGR was a full % lower"* ao testar com ERs reais.

Confirmamos: CAGR drop médio nos stacks foi **-0.66pp** (range -0.49 a -0.89pp). **Não é "1pp completo"** mas está na ordem certa. A diferença entre nossa correção (0.5-0.9pp) e a dele (1pp) provavelmente vem de:
- Ele usou **UPRO direto** (ER 0.91% × 100% allocation = mais drag) onde nós usamos NTSX (0.20% × 100% allocation = menos drag).
- Detalhes de cadência de rebal interna do testfol.io que não modelamos exatamente.

**Verdict do feedback:** ⚠️ **Validated direção, partial magnitude**.

---

## Pareto ranking ajustado

Sorted by Sharpe (apples-to-apples Monthly + ERs):

| # | Portfolio | CAGR | MDD | Sharpe | Tier |
|---|---|---:|---:|---:|---|
| 🥇 | **Conservative (B4 ZROZ)** | 13.31% | -28.94% | **0.745** | **WINNER** |
| 🥈 | Sleeping pills (L1 CEGB) | 11.06% | -25.43% | 0.729 | bom mas CAGR < SPY |
| 🥉 | Bogleheads (L2) | 11.06% | -26.30% | 0.722 | bom mas CAGR ≈ SPY |
| 4 | **Balanced (B2)** | 13.89% | -36.38% | 0.718 | trade-off |
| 5 | **Aggressive (T1)** | 13.34% | -34.65% | 0.688 | trade-off (gold-heavy) |
| 6 | Gayed LRS 2x | 16.01% | -43.48% | 0.609 | folclore (CAGR alto, MDD ruim) |
| 7 | Gayed LRS 3x | 19.61% | -57.57% | 0.595 | extreme |
| 8 | Popular 50/25/25 | 12.58% | -50.55% | 0.576 | **degradado** vs iter 039 |
| 9 | SPY 1x | 11.37% | -55.20% | 0.523 | benchmark |

**Hierarquia das 4 candidates:** B4 > B2 > T1 (com L1 CEGB próximo se CAGR for sacrificado por MDD ainda menor).

---

## Para o Post 2

Mudanças a refletir vs Post 1:

1. **Tabela de retornos**: re-publicar com valores Monthly + ERs (este SUMMARY.md).
2. **Adicionar caveat** sobre rebal cadence × portfolio type (Popular 50/25/25 caso evidente).
3. **Recomendação de portfolio**: B4 Conservative move para `13.31% / -28.94% / 0.745` (era 13.96% / -28.65% / 0.798). Sharpe ≥ 0.74 ainda passa o threshold do Post 2.
4. **Documento o `drag` por portfolio** (transparência metodológica para responder u/perky_python).
5. **Próximas iters (041-043)** seguem com **mesma metodologia** (Monthly + ERs).

---

## Próximos passos

- **Iter 041** — G3 NDX regime-gate (TQQQ/QQQ × 200d × CTA/KMLM/GLD per Fun-Sundae4060 + no_simpsons). Roda monthly rebal + ERs.
- **Iter 042** — G4 international stack (NTSI/RSSB/VT base per Grouchy_Release_2321 + perky_python). Roda monthly rebal + ERs.
- **Iter 043** — G8 walk-forward weight drift gate (per laurenthu). Re-fit B2/T1/B4 weights rolling 5y.

---

## Referências

- u/perky_python (Reddit): rebal cadence + ERs critique. [Comment](https://www.reddit.com/r/LETFs/comments/1t0i3qm/)
- u/laurenthu (Reddit): walk-forward critique. [bestfolio.app/blog/walk-forward-portfolios](https://bestfolio.app/blog/walk-forward-portfolios)
- u/Grouchy_Release_2321 (Reddit): MF survivorship + VT pushback.
- WisdomTree NTSX FAQ: [PDF](https://www.wisdomtree.com/-/media/us-media-files/documents/resource-library/wisdomtree_ntsx_faq.pdf)
- Return Stacked RSST: [page](https://www.returnstackedetfs.com/rsst-return-stacked-us-stocks-managed-futures/)
- Investment mandate: `docs/investment-mandate.md` §1, §2, §4
- Iter 039 testfolio data (baseline): `iterations/039-2026-04-30-reddit-comparison-spy-lrs-vs-static-stack/testfolio_data/`
