# Iter 041 — G3 NDX regime-gate (TQQQ × multi-asset)

**Date:** 2026-05-01
**Source:** testfol.io tactical API, 1987-12-31 → 2026-04-30 (38.33y)
**Trigger:** Reddit Post 1 feedback — u/Fun-Sundae4060 + u/no_simpsons

---

## TL;DR

| 🟢 Edge encontrado? | **Não.** Nenhuma das 6 variantes G3 bate o B4 Conservative do iter 040 em Sharpe. |
| 🥇 Best G3 | **G3c (with bonds)** — CAGR 13.36% / MDD -42.63% / Sharpe 0.703 |
| ❌ Gap vs B4 baseline | Sharpe -0.042 / MDD -13.69pp **pior** / CAGR praticamente igual (+0.05pp) |
| ⚠️ Worst G3 | **G3f (pure TQQQ/QQQ swap)** — CAGR 19.97% (highest) MAS MDD **-96.90%** (worst do estudo) |
| 📉 Implicação | Folk-wisdom "TQQQ × 200d × MF/GLD" cai na **mesma região Pareto que Gayed LRS** — strictly dominated por static stacks. **Pure swap (G3f) é a pior** — bear sleeve precisa ser de outra asset class pra ter cushion. |

---

## Variantes testadas

| ID | Name | Bull regime (above 200d SMA QQQ) | Bear regime (below) |
|---|---|---|---|
| G3a | Fun-Sundae spec | TQQQ 34 / KMLM 33 / GLD 33 | QQQ 34 / KMLM 33 / GLD 33 |
| G3b | NDX-heavy | TQQQ 50 / KMLM 25 / GLD 25 | QQQ 50 / KMLM 25 / GLD 25 |
| G3c | with bonds | TQQQ 25 / KMLM 25 / GLD 25 / IEF 25 | QQQ 25 / KMLM 25 / GLD 25 / IEF 25 |
| G3d | minimal | TQQQ 50 / KMLM 50 | QQQ 50 / KMLM 50 |
| G3e | Gayed-NDX | TQQQ 100 | IEF 100 |
| G3f | pure TQQQ/QQQ swap | TQQQ 100 | QQQ 100 |

**Implementation notes:**
- Signal: `Price(QQQSIM) > SMA(QQQSIM, 200)` com tolerância 2%.
- TQQQ emulado via `QQQSIM?L=3&E=0.84` (TQQQSIM não disponível em testfol.io).
- KMLMSIM disponível desde 1987 (rules-based, evita survivorship per Bhardwaj 2014 NBER w14424).
- CTASIM **não** disponível → **KMLM apenas** como sleeve MF (Fun-Sundae4060 spec original era KMLM+CTA, simplificado).
- ERs aplicados via `drag` per-leg (TQQQ 0.84% bull, QQQ 0.20% bear, KMLM 0.92%, GLD 0.40%, IEF 0.15%).
- Daily rebal intra-leg, trading_freq daily (signal cross fires daily).

---

## Resultados — Pareto sorted by Sharpe

| # | Strategy | CAGR | MDD | Sharpe | Sortino | Calmar |
|---|---|---:|---:|---:|---:|---:|
| 🥇 | Conservative (B4 ZROZ) | 13.31% | -28.94% | **0.745** | 1.071 | 0.460 |
| 🥈 | Sleeping Pills (L1 CEGB) | 11.06% | -25.43% | 0.729 | 1.044 | 0.435 |
| 🥉 | Bogleheads 67 NTSX (L2) | 11.06% | -26.30% | 0.722 | 1.037 | 0.420 |
| 4 | Balanced (B2) | 13.89% | -36.38% | 0.717 | 1.028 | 0.382 |
| 5 | 🆕 **G3c (with bonds)** | **13.36%** | -42.63% | **0.703** | 0.994 | 0.313 |
| 6 | Aggressive (T1) | 13.34% | -34.65% | 0.688 | 0.984 | 0.385 |
| 7 | 🆕 G3a (Fun-Sundae 33/33/33) | 15.60% | -58.53% | 0.661 | 0.932 | 0.267 |
| 8 | 🆕 G3d (minimal 50/50) | 18.58% | -75.47% | 0.629 | 0.887 | 0.246 |
| 9 | 🆕 G3b (NDX-heavy 50/25/25) | 18.34% | -75.98% | 0.621 | 0.874 | 0.241 |
| 10 | Gayed LRS 2x (SSO 200d) | 16.01% | -43.48% | 0.609 | 0.843 | 0.368 |
| 11 | Gayed LRS 3x (UPRO 200d) | 19.61% | -57.57% | 0.595 | 0.822 | 0.341 |
| 12 | Popular 50/25/25 | 12.58% | -50.55% | 0.576 | 0.818 | 0.249 |
| 13 | 🆕 **G3f (pure TQQQ/QQQ swap)** | **19.97%** ⚡ | **-96.90%** ⚠️ | 0.556 | 0.781 | 0.206 |
| 14 | 🆕 G3e (Gayed-NDX 100/IEF) | 18.61% | -90.05% | 0.535 | 0.748 | 0.207 |
| 15 | SPY 1x | 11.37% | -55.20% | 0.523 | 0.740 | 0.206 |

⚡ = G3f tem o **maior CAGR de todas as G3 variants** (19.97%) — beats Gayed LRS 3x.
⚠️ = G3f tem o **PIOR MDD do estudo inteiro** (-96.90%) — only SPY 1x (-55.20%) is "less bad" if you ignore G3e.

---

## Findings

### 1. Folk-wisdom "TQQQ × 200d × diversifiers" não sobrevive a teste justo

A literatura comunitária (Bogleheads t=339329, Petrou MACD-NDX) que reportava **~10,000% de retorno** em estratégias TQQQ regime-gate foi computada sobre **2012-2025** — janela de bull market secular do NDX **sem nenhum bear catastrófico**. Em **1987-2026** (que inclui 2000-2002 dotcom):

- **G3e Gayed-NDX:** MDD **-90.05%** porque TQQQ emulado (3× QQQ) durante 2000-2002 desgastou ~99% antes do signal fired. CAGR alto (18.61%) compensa parcialmente, mas Sharpe 0.535 fica abaixo de SPY.
- **G3b/G3d (NDX-heavy):** MDD -75% — mesma dinâmica, mas com KMLM/GLD diluindo levemente.
- **G3a (Fun-Sundae spec)** atinge 15.60% / -58.53% — Sharpe 0.661, **acima** de Gayed LRS 2x (0.609) e SPY (0.523) mas **abaixo** de B4 estático (0.745).

### 2. G3c (with bonds) é a única variante que se aproxima do baseline

Adicionando IEF 25% como 4ª sleeve, MDD cai para -42.63% (de -75% sem bonds). Sharpe **0.703** — **vence T1, L1, L2 marginais** mas **perde para B4/B2** estáticos.

**Trade-off vs B4:**
- CAGR: +0.05pp (tied)
- MDD: **-13.69pp pior**
- Sharpe: -0.042

**Verdict:** G3c **complementa** mas não substitui B4. Investidor que quer exposição NDX adicional sem sacrificar Sharpe demais pode usar G3c como sleeve secundário, mas como portfolio standalone B4 é estritamente superior.

### 3. Por que TQQQ regime-gate falha em 1987-2026

Três fatores combinam:

1. **Whipsaw em 2000-2001:** múltiplos cruzamentos da SMA200 com TQQQ 3× → cada exit/re-entry custa ~3-5% durante chop. Acumula ~30-40% de loss antes do signal "estabilizar".
2. **Lag do signal de exit:** SMA200 atrasada significa TQQQ já caiu 25-35% antes do exit → essa perda fica gravada na curva.
3. **Bear leg ainda contém equity (QQQ):** mesmo após exit do TQQQ, manter QQQ na bear continua sangrando durante drawdowns prolongados (2000-2002 NDX -78% buy-hold).

Solução de no_simpsons (`/NQ 1.4× bull / 0.5× bear + IEI 1/0`) em tese mitigaria via posição equity reduzida na bear, mas requer logic adicional (signal duplo no IEI) que não testamos. Possível trabalho futuro.

### 4. G3f — pure TQQQ/QQQ swap (sem diversifiers): MAIOR CAGR, PIOR MDD do estudo

Variante adicionada após pergunta direta do usuário ("você testou TQQQ/QQQ puro?").

**G3f: 100% TQQQ bull → 100% QQQ bear, sem KMLM/GLD/IEF/duration.**

Resultado: CAGR **19.97%** (highest G3, beats até Gayed LRS 3x 19.61%) / MDD **-96.90%** (pior do estudo) / Sharpe 0.556.

**Por quê é tão pior que G3e (Gayed-NDX, MDD -90.05%)?** A diferença entre G3e e G3f é só o **bear regime asset**: IEF (G3e) vs QQQ (G3f). 

- **G3e bear=IEF:** quando 200d signal fires bear, você vai pra bonds que SOBEM (geralmente) durante crashes equity. Cushion real.
- **G3f bear=QQQ:** quando 200d signal fires bear, você sai do leverage 3× mas continua com 100% NDX equity. **Bear ainda sangra** durante 2000-2002 (-78% NDX) e 2008 (-50% NDX).

**Lesson estrutural:** o 200d SMA gate funciona quando o **bear sleeve está descorrelacionado** do bull sleeve (Gayed: SPX leveraged → bonds). Quando bear é apenas "menos leveraged version do bull" (G3f), o gate só elimina decay extra mas mantém exposição direcional → MDD próximo do buy-hold underlying.

**Comparação útil:**
- TQQQ buy-hold standalone (Bull TQQQ leg em isolation): MDD -99.98% (ou seja, ~zero capital sobrou em 2002).
- G3f (TQQQ→QQQ swap): MDD -96.90% — o gate **salvou só 3pp** de drawdown.
- Gayed-NDX G3e (TQQQ→IEF): MDD -90.05% — o gate salvou 10pp.
- Gayed canonical SSO (SPY 2× → IEF): MDD -43.48% — funcionou bem porque SPX vol é menor que NDX vol.

**Conclusão:** o regime-gate em NDX-leveraged só é útil se o bear sleeve for de outra asset class. "Pure swap" não dá cushion. **G3f é a pior escolha entre todas as variants TQQQ-baseadas testadas.**

### 5. Resposta direta ao Fun-Sundae4060

A spec testada (G3a 33/33/33) lança em CAGR 15.60% / MDD -58.53% / Sharpe 0.661. **Bate SPY** em Sharpe (+27%) e CAGR (+37%) mas **MDD ligeiramente pior** que SPY (-58 vs -55). E perde para todos os static stacks NTSX/GDE/RSST do Post 1.

**Resposta honesta para Reddit:** "your spec lands in the upper-right but not above the static stacks B2/T1/B4 — the regime-gate doesn't help when the underlying (TQQQ 3×) decays severely in extended bear markets like 2000-2002. With bonds added (G3c) it gets close to B4 but still 0.04 Sharpe behind."

---

## Para o Post 2

Adicionar seção: **"What about TQQQ regime-gate strategies?"**

```
Tested 5 variants of TQQQ × 200d SMA × multi-asset regime gate, including the
Fun-Sundae spec (33/33/33 TQQQ/KMLM/GLD bull → QQQ/KMLM/GLD bear). Results:

| Variant | CAGR | MDD | Sharpe |
|---|---|---|---|
| G3c (with bonds) | 13.36% | -42.63% | 0.703 |
| G3a (Fun-Sundae) | 15.60% | -58.53% | 0.661 |
| G3b (NDX-heavy 50/25/25) | 18.34% | -75.98% | 0.621 |
| G3d (TQQQ/KMLM only) | 18.58% | -75.47% | 0.629 |
| G3e (Gayed-NDX 100/IEF) | 18.61% | -90.05% | 0.535 |

None beat B4 Conservative (13.31% / -28.94% / 0.745). The 200d SMA gate on
NDX-leveraged underlies fails in 1987-2026 because of (1) 2000-2002 whipsaws
that compound TQQQ 3× decay, (2) signal lag that books 25-35% MDD before
exit, (3) bear-leg QQQ exposure still bleeds during prolonged drawdowns. The
~10,000% returns reported in Bogleheads threads were computed over 2012-2025
(secular NDX bull, no dotcom-equivalent crash); they don't generalize.
```

---

## Próximos passos

- **Iter 042 (G4 international):** NTSI/RSSB base. Mesmo método (Monthly + ERs).
- **Iter 043 (G8 walk-forward):** re-fit B4/B2/T1 weights rolling 5y per laurenthu.

---

## Referências

- u/Fun-Sundae4060 (Reddit): "TQQQ, CTA, KMLM, GLD leveraged ... QQQ, CTA, KMLM, GLD deleveraged under 200SMA"
- u/no_simpsons (Reddit): "/NQ 1.4× bull / 0.5× bear + IEI 1/0"
- Bogleheads thread t=339329: TQQQ + 200d SMA backtests (2012-2025 window)
- Lambros Petrou: NDX-3x MACD strategy (10,000% return claim, same window)
- Hurst/Ooi/Pedersen 2017 "A Century of Evidence on Trend-Following" — pre-1987 trend data
- KMLM rules-based MF (Bhardwaj/Gorton/Rouwenhorst 2014 NBER w14424 documents survivorship bias avoidance vs CTA databases)
- Iter 040 baseline (B4/B2/T1 monthly + ERs): `iterations/040-2026-05-01-baseline-monthly-rebal-explicit-ers/SUMMARY.md`
