# Review da lista completa de Stacked ETFs (Reddit r/LETFs)

> Análise da lista compartilhada pelo usuário em 2026-04-23, cross-referenced
> com os princípios V3_1 v3.5 finais. Fonte original:
> https://www.reddit.com/r/LETFs/comments/1p6vz8q/comprehensive_list_of_stacked_etfs/

---

## Framework de avaliação

V3_1 v3.5 estabeleceu 2 critérios estruturais para o que é um **stacking
aceitável** no portfolio de um investidor brasileiro:

1. **Overlay com return stream positivo esperado** (não zero/negativo real)
2. **Overlay NÃO tied ao USD** (senão viola o princípio "bonds em moeda de
   consumo" — Campbell-Viceira 2010)

Gold, BTC, managed futures (CTA), carry, merger arb satisfazem (1) e parcialmente (2).
US Treasuries/bonds/TIPS **falham em (2)** para investidor BR.

---

## Classificação da lista completa

### ✅ Consistente com V3_1 v3.5 principles

| Ticker | Estrutura | Uso pra nós |
|--------|-----------|-------------|
| **GDE** | 90% SPY + 90% Gold | ✅ **Usando** — core 25% |
| **BTGD** | 100% BTC + 100% Gold | ✅ **Usando** — satellite 5% |
| RSSX | 100% SPY + 80% Gold + 20% BTC | ⏳ Alternativa a BTGD (novo, AUM $60M, esperar 2-3y) |
| OOSB | 100% SPY + 100% BTC | ❌ Redundante (já temos muito SPY via GDE+AVUS+AVUV+SPMO) |
| OOQB | 100% QQQ + 100% BTC | ❌ Concentração tech, não alinhado |
| BEGS | 75% BTC + 25% ETH + 75% Gold + 25% Silver | ❌ Complexidade sem benefício vs BTGD |
| ISSG | 100% SPY + 100% Gold (income) | ❌ Covered calls cap upside (wrong para acumulação) |
| GDMN | 90% Gold + 90% Gold miners | ❌ Gold concentration só; não adiciona return stream novo |
| HOLD | 75% SPY + 75% MF | 🔄 Considerar pra V3_3/V3_4 (MF overlay) |
| CTAP | 100% SPY + 100% CTA | 🔄 Alternativa simpler ao DBMF standalone em V3_3/V3_4 |
| RSSY | 100% SPY + 100% Carry | 🔄 Interessante para diversification, esperar track record |
| MATE | 100% SPY + 100% AHLT (MF) | 🔄 Alt ao RSST; AUM/AHL track check |
| WTLS | 90% SPY + 90% Long/Short | ❌ Long/short factor overlay complexo |
| ASGM | 70% VT + 70% Macro | ❌ Opaque strategy "macro" |

### ❌ Rejeitados (US bonds/Treasury overlay)

Violam princípio "bonds em moeda de consumo":

| Ticker | Composição rejeitada | Motivo |
|--------|---------------------|--------|
| **NTSI, NTSE, NTSG, NTSX, NTSD** | 90/60 com US Treasury futures | Rate shock 2022 + currency mismatch |
| **RSSB** | VT + GOVT | Mesmo problema |
| RSBA | GOVT + Merger Arb | GOVT = US Treasury |
| RSBT | GOVT + MF | GOVT destrutivo em rate shock |
| RSBY | GOVT + Carry | GOVT = US bonds |
| ESBG | SPY + IEI + Gold (2.1×) | IEI = US Treasury intermediate |
| GDT | STIP + Gold | STIP = US TIPS (USD inflation-linked) |
| WTIP | STIP + CTA + Gold + Silver + BTC + BIL | STIP + BIL = US bonds/cash |
| SPLS | SPY + MINT | MINT = US ultra-short bonds |
| ISTG | BND + Gold (income) | BND = US aggregate bonds |
| ISST | SPY + BND (income) | BND = US bonds |
| ISBT | BND + BTC (income) | BND = US bonds |
| ALLW | VT + BND + TIPZ + DBC | BND + TIPZ = US bonds stack |
| LQPE | SPY + AGG + CTA | AGG = US aggregate bonds |
| RPAR, UPAR | VT + AGG + LTPZ + DBC + Gold | AGG + LTPZ = US bonds |
| ENDW | Treasury-heavy endowment | US bonds |

**Nossa alternativa para US bonds:** zero exposição até 45 anos; depois
BR FI direto (B5P211 + IMAB11 + DINF11 + LFTS11) via corretora BR.

### 🎯 ETFs income (wrong-fit pra acumulação)

Todos os "Income" da família IncomeSTKd (Quantify) usam option premium
(covered calls + short puts) que **cap upside** em bull markets:

- ISSG (SPY + Gold income)
- ISST (SPY + BND income)
- ISBG (BTC + Gold income) — **usuário perguntou; é wrong-fit acumulação**
- ISSB (SPY + BTC income)
- ISBT (BND + BTC income)

**Usecase específico:** só retirement phase (V3_4) se income weekly for
valorizado sobre upside capture. Decay de NAV em bull markets é real.

### ⏳ Upcoming ETFs (mencionados na lista)

- JPM: 100% SPY + 100% MF
- LoCorr: 100% SPY + 100% LCSIX
- Direxion: 100% SPY + 100% MF
- Tidal: 100% VXUS + 100% MF ← interessante se lançar (VXUS é mais
  international-friendly que SPY base)

---

## Comparação: estrutura V3_1 v3.5 vs alternativas integradas

### Nossa escolha: **GDE + BTGD (2 ETFs, 30% allocation total)**

| Produto | Peso | Notional gerado |
|---------|------|------------------|
| GDE 25% | 25% | 22,5% US eq + 22,5% gold |
| BTGD 5% | 5% | 5% BTC + 5% gold |
| **Total alts stacking** | **30% capital** | **22,5% US eq + 27,5% gold + 5% BTC** |

### Alternativa A: RSSX + GDE (integrated)

| Produto | Peso | Notional |
|---------|------|----------|
| GDE 25% | 25% | 22,5% US eq + 22,5% gold |
| RSSX 5% | 5% | 5% US eq + 4% gold + 1% BTC |
| Total | 30% | **27,5% US eq + 26,5% gold + 1% BTC** |

Delta: **RSSX adiciona +5pp US eq mas baixa BTC de 5% pra 1%** (-4pp).

### Alternativa B: RSSX 10% + BTGD 0%

| Produto | Peso | Notional |
|---------|------|----------|
| GDE 25% | 25% | 22,5% US eq + 22,5% gold |
| RSSX 10% | 10% | 10% US eq + 8% gold + 2% BTC |
| Total | 35% | **32,5% US eq + 30,5% gold + 2% BTC** |

Delta: mais US eq, menos BTC.

### Veredito

**Nossa escolha V3_5 (GDE 25 + BTGD 5) é superior** para o perfil da V3_1
porque:

1. **Não redundante com equity:** V3_1 já tem ~52% US equity via
   GDE+AVUS+AVUV+SPMO. Adicionar 5% a mais via OOSB/RSSX seria
   redundante.
2. **Scarcity hedge concentrado:** BTGD 5% dá 5% BTC + 5% gold de ativos
   "não-monetários" (scarcity-driven, não-USD). Esta é a DIVERSIFICATION
   que o portfolio precisa, não mais equity.
3. **BTC ratio preserva consenso (5%):** RSSX 5% daria só 1% BTC — abaixo
   do 3-5% recommended. RSSX 10% daria 2% BTC — ainda abaixo.
4. **Ratio 50/50 gold/BTC em BTGD é clean:** 80/20 gold/BTC do RSSX está
   meio "gold-heavy" + já temos muito gold via GDE.

**Decisão: mantemos GDE + BTGD.**

---

## Reconsiderações pra V3_2/V3_3/V3_4 (fases posteriores)

Na fase de transição e retirement, MF becomes more valuable como crisis
alpha. Opções stacked pra considerar:

### HOLD (75% SPY + 75% MF) — alternativa a DBMF standalone

- Pros: stacked → capital efficiency; MF embedded com SPY exposure
- Cons: AUM ainda modesta; nosso V3_3 já tem 5% DBMF direto
- Verdict: **manter DBMF direto** por enquanto

### CTAP (100% SPY + 100% CTA) — stacking 2× com MF

- Similar ao RSST mas explicit "CTA" vs generic "MF"
- Menor AUM que RSST

### RSST (100% SPY + 100% MF) — já considerado

- Na V3_2/V3_3 atual usamos DBMF+KMLM standalone em vez de RSST stacked
- RSST seria alternativa mas nosso drag tax BR favorece ETFs com menos turnover
- **Mantém DBMF/KMLM standalone**

---

## Conclusão final

**V3_1 v3.5 (GDE + BTGD) é a estrutura stacking correta para acumulação do
investidor brasileiro.** A lista completa do Reddit serve como:

1. **Validação**: nossos 2 stacked ETFs (GDE + BTGD) passam ambos os
   critérios estruturais; a maioria dos outros falha em critério #2
   (US bonds/Treasury overlay).
2. **Radar de futuro**: quando **RSSX** maturar (track record 2-3y), pode
   ser avaliado como alternativa integrada a BTGD. **HOLD** pode substituir
   DBMF standalone na V3_3 se ganhar liquidez.
3. **Evitar armadilhas**: as famílias **Income (IncomeSTKd)** e **NTSX
   family com Treasury overlay** são as principais armadilhas pra investidor
   que não percebe os problemas estruturais.

**Nenhum ETF da lista representa upgrade claro vs V3_1 v3.5 atual.**
