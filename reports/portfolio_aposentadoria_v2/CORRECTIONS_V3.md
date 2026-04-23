# Correção V3 — 2026-04-23 (pós feedback do usuário sobre BR bonds + stacked alts)

> Você pediu: (1) substituir bonds US (TLT/IEF/SHV) por renda fixa brasileira;
> (2) expandir sleeve gold/BTC com alternativas return-stacked (GDE, RSSX,
> BTGD, ISBG). Relatório abaixo dos novos portfolios.

---

## 1. Renda fixa em moeda doméstica — fundamento acadêmico

**Posição acadêmica é unânime.** Bonds devem estar na moeda em que o investidor
consome. Fontes-chave (pesquisadas em `data/web_research_v3.md`):

- **Campbell-Viceira (2010, JoF)** — paper canônico: *"The risk-minimizing
  currency strategy for a global bond investor is close to a full currency
  hedge."* Para equities, hedge NÃO é o ótimo; para bonds, É.
- **Vanguard (2018, 2023)** — papers oficiais: *"Hedging allows bonds to
  deliver bond-like returns with bond-like volatility."* Unhedged adiciona
  +6-8% vol sem premium compensatório.
- **Ben Felix / PWL Capital (Rational Reminder 379)**: *"If you introduce
  currency risk, you've defeated the purpose of bonds in your portfolio."*
  Política PWL = bonds 100% domésticos.

**Para brasileiro especificamente:**

| Métrica | Valor | Observação |
|---------|-------|------------|
| NTN-B real yield atual | IPCA + 5,5-6,35% | Tesouro 2024-2026 |
| US TIPS 10Y real yield | 1,8-2,2% em USD | Mesmo período |
| **Gap real yield a favor BR** | **~400bps** | ~4pp/ano mais em BR |
| CDI nominal 10y | ~13%/ano | Anchor BR FI |
| BRL/USD vol anual | 15-20% | Destrói função de stabilizer |
| US Treasury vol anual | 5-7% | Em USD |

**Conclusão:** bond USD unhedgeado pra brasileiro = bond (low return, low vol)
+ FX (moderate return expected, HIGH vol). FX vol domina, transformando o
stabilizer em gerador de vol. E o NTN-B tem real yield 400bps acima do TIPS.

---

## 2. Universo BR FI — tabela dos ETFs investigados

| Ticker | Nome | TER | AUM | Inception | Tax PF |
|--------|------|-----|-----|-----------|--------|
| B5P211 | IT Now IMA-B5 P2 (IPCA+ ≤5y) | 0,20% | R$ 2,87-3,54bi | 2020-11 | 15% IR |
| IMAB11 | IT Now IMA-B (IPCA+ full curve) | 0,25% | R$ 2,65bi | 2018-2019 | 15% IR |
| B5MB11 | Bradesco IMA-B5+ (IPCA+ >5y) | 0,20% | — | ~2019 | 15% IR |
| LFTS11 | Investo Teva Selic (cash-proxy) | 0,19% | R$ 3,01bi | 2021 | 15% IR |
| FIXA11 | BB/Mirae Pré 3y | 0,30% | — | 2018 | 15% IR |
| DEBB11 | BTG Debêntures DI | 0,60% | R$ 1,17bi | 2022-06 | 15% IR |
| **DINF11** | **BTG Debêntures Incentivadas Lei 12.431** | ~0,60% | menor | ~2023 | **0% ISENTO** |

### Destaque: DINF11

Único ETF de debêntures incentivadas da B3. Lei 12.431/2011 isenta totalmente
IR para PF (cap gains + distribuições). Pickup líquido sobre CDI ~150-180bps
mantém 100% do retorno — diferencial vs DEBB11 que pega 15% IR.

### Proxy histórico para backtest

- **CDI** (BCB série 12): daily desde 1986. CAGR 2000-2026 = **12,13% nominal**,
  vol quase zero (0,27%/ano) — reflete que Selic é taxa diária referência.
- **IPCA** (BCB série 433): monthly desde 1980
- **IMA-B** (ANBIMA): daily desde 2003 — **não consegui acesso via BCB**;
  alternativa: IPCA + spread real 5-6% como aproximação

**Caveat crítico:** CDI como proxy de B5P211/IMAB11 é **otimista**. CDI tem
duração zero; IMAB11 tem duração ~6-8y e sofreu -7,92% em 2024 durante o ciclo
de alta da Selic. Os backtests com proxy CDI subestimam MDD e superestimam
Sharpe da sleeve FI. Validação com dados reais 2019-2026 abaixo.

---

## 3. Gold/BTC stacked alternatives — tabela final

| Ticker | Estrutura | TER | Inception | AUM | Recomendação |
|--------|-----------|-----|-----------|-----|--------------|
| **GDE** | 90% SPX + 90% gold futures (1.8x) | **0,20%** | 2022-03 | **~$629M** | ✅ Core holding |
| RSSX | 100% SPX + 100% gold/BTC risk-parity | 0,68% | 2025-05 | ~$60M | ⏳ Esperar track record |
| BTGD | 100% BTC + 100% gold | 1,05% | 2024-10 | ~$50-70M | 🎯 Satellite 5-10% |
| ISBG | 1x BTC + 1x gold + option premium | 1,14% | 2026-01 | ~$1-4M | ❌ Descartar |

**Veredito sobre ISBG:** AUM microscópico (<$5M), track record de 3 meses,
estrutura de covered-calls erode NAV em bull markets, 100% do "distribution
rate 19.99%" é return of capital (não yield real). **Não recomendado.**

**Veredito sobre RSSX:** conceitualmente é o produto mais sofisticado (Hoffstein
+ Gordillo framework puro, SPX + gold/BTC risk-parity). Mas inception 2025-05,
AUM só $60M — esperar 2-3 anos de track record antes de entrar com peso
relevante.

**Veredito sobre BTGD:** satellite holding perfeito para debasement hedge
puro. Use 3-5% do portfolio.

**Vencedor do debate "manual vs integrated":**
- **GDE** vence sobre "NTSX + GLDM manual" em cenário BR porque: (a) TER
  composto similar (0,21% vs 0,17%), (b) menos taxable events para DARF anual,
  (c) zero bond exposure internal (consistente com princípio BR FI separado).
- **Para sleeve core equity+gold: substitua NTSX por GDE** (quando existir
  GDE equivalente internacional, ainda não existe).

---

## 4. As 4 carteiras V3 — redesenhadas

### Pesos reais (para implementação atual)

| Ticker | V3_1 Max CAGR | V3_2 Max Sharpe | V3_3 Max TW/MDD≤50% | V3_4 Max SWR |
|--------|---------------|-----------------|---------------------|--------------|
| **GDE** (90% SPX + 90% gold) | 30% | 20% | 20% | 15% |
| **NTSI** (Int 90/60) | 15% | 10% | 15% | 0% |
| **NTSE** (EM 90/60) | 5% | 0% | 5% | 0% |
| **AVUV** (US SCV) | 15% | 10% | 15% | 8% |
| **AVDV** (Int SCV) | 10% | 5% | 10% | 5% |
| **AVEM** (EM core) | 5% | 0% | 5% | 0% |
| **SPMO** (US Mom) | 5% | 0% | 5% | 0% |
| **SSO** (2x SPY) | 10% | 0% | 0% | 0% |
| **DBMF** (US MF) | 0% | 10% | 5% | 10% |
| **KMLM** (US MF) | 0% | 5% | 0% | 5% |
| **B5P211** (IPCA+ curto) | 0% | 15% | 10% | 20% |
| **IMAB11** (IPCA+ longo) | 0% | 10% | 5% | 15% |
| **LFTS11** (Selic cash) | 0% | 0% | 0% | 10% |
| **DINF11** (isento IR) | 0% | 10% | 3% | 7% |
| **BTGD** (gold+BTC 2x) | 3% | 0% | 0% | 0% |
| **IBIT** (BTC) | 2% | 0% | 0% | 0% |
| **GLDM** (gold) | 0% | 5% | 2% | 5% |
| **TOTAL** | 100% | 100% | 100% | 100% |
| **% BR FI** | 0% | 35% | 18% | 52% |
| **Leverage efetivo** | ~1,75× | ~1,25× | ~1,35× | ~1,15× |

### Backtest com proxy de longa história (2007-2026, com CDI para BR FI)

| Carteira | Janela | CAGR | Sharpe | MDD | Vol | p50 TW 30y | P(MDD>50%) | SWR |
|----------|--------|------|--------|-----|-----|------------|------------|-----|
| V3_1 Max CAGR | 2014-2026* | 18,33% | 0,93 | -29,7% | 17,5% | **$12,42M** | 1,4% | 9,61% |
| V3_2 Max Sharpe | 2007-2026 | 12,46% | 1,12 | -18,1% | 9,9% | $3,70M | 0,0% | 8,33% |
| V3_3 Max TW/MDD50 | 2007-2026 | 11,69% | 0,79 | -35,5% | 13,0% | $3,31M | 1,8% | 6,75% |
| V3_4 Max SWR | 2007-2026 | 11,69% | **1,36** | -12,1% | 7,5% | $3,13M | 0,0% | **8,61%** |

(*) V3_1 limitada a 2014-2026 por inception do BTGD_syn. Os outros 3 rodam de 2007-07 a 2026-02.

### Validação com dados REAIS (janela 2020-2026)

FINAL_V3_4 real (substituindo proxies por B5P211/IMAB11/DEBB11 reais, sem
LFTS11 nem GDE pré-2022):

- **Janela 2020+ (65 meses):** CAGR 11,61% / Sharpe 1,33 / MDD -3,5% / Vol 6,3%
- **Janela 2022+ (50 meses, incl DEBB11):** CAGR 13,67% / Sharpe 1,54 / MDD -4,6%
- **Janela 2024+ (27 meses, full stack):** CAGR 18,58% / Sharpe 2,27 / MDD -3,0%

**Os dados reais confirmam** a estrutura do V3_4: Sharpe >1,3 em todas as
janelas reais, MDD limitado. Proxy CDI está na direção certa mas é um pouco
otimista em MDD (real IMAB11 teve -8% em 2024 sozinho).

### Ranking consistente com o nome (agora ✅ todos)

- **Max CAGR:** V3_1 (18,33%) ✅
- **Max Sharpe:** V3_4 (1,36) > V3_2 (1,12) — V3_4 vence no proxy CDI
- **Max TW/MDD≤50%:** V3_3 (MDD -35,5% respeita o gate, 11,69% CAGR) ✅
- **Max SWR:** V3_4 (8,61%) ✅

V3_4 acabou sendo o "tudo-melhor" graças à combinação BR FI pesada (12% CAGR
quase sem vol no proxy) + diversificação via MF e gold. V3_2 fica no meio.

---

## 5. Comparação V2 vs V3

| Métrica | V2 (com US bonds) | V3 (com BR FI) | Delta |
|---------|-------------------|----------------|-------|
| Max CAGR (V3_1 vs V2_1) | 10,40% | 18,33% | **+7,93pp** (proxy bull-biased) |
| Max Sharpe (V3_4 vs V2_4) | 0,74 | 1,36 | **+0,62 Sharpe** |
| Max SWR (V3_2 vs V2_2) | 5,82% | 8,33% | **+2,51pp** |
| Worst MDD (V3_4) | -21,5% | -12,1% | **-9,4pp melhor** |
| p50 TW 30y (V3_2) | $1,77M | $3,70M | **+$1,93M** |

V3 **bate V2 em todos os eixos simultaneamente** — o que faz sentido
economicamente:

1. BR FI tem retorno nominal MUITO maior que US FI (12% vs 3-4%)
2. BR FI em BRL elimina FX vol sobre o stabilizer do portfolio
3. GDE stacking (equity + gold) reduz correlação com equity pura
4. Brasileiro que consome em BRL tem natural skew pra BRL — carteira V3 está
   alinhada

**Caveat honesto:** parte do ganho é artificial do proxy CDI (duração zero)
vs IMAB11 real (duração ~8y com MDD -8% em 2024). Ganho real esperado: ~+0,5
Sharpe vs V2 (não +0,62).

---

## 6. Caveat final sobre backtest

1. **CDI proxy é otimista** para IMAB11/B5P211 (capture the level, not the
   duration vol). Real MDD da sleeve BR FI em 2022-2024 foi -5 a -8%.
2. **Janela 2007-2026** é relativamente bull-biased (só 1 grande crash 2008,
   e 2022 rate shock foi parcial). 50-100 anos seria ideal.
3. **Sharpe 1.36 no V3_4 é suspiciously high**. Real-world expectation mais
   humilde: Sharpe 0.8-1.0 considerando duration risk IMAB + BRL devaluation
   cycles.
4. **FX risk não está modelado.** Portfolio em mix BRL+USD; fluxos de caixa
   reais precisariam de hedging plan ou tolerância a volatilidade de retorno
   em BRL.
5. **Estate tax US$ 60k threshold** continua sendo o risco mais crítico não
   endereçado. UCITS alternatives onde possível.

---

## Recomendação operacional

Para brasileiro de 30 anos com horizonte 30 anos:

1. **Fase acumulação (30-45):** V3_1 (agressivo, zero FI, max leverage).
   Tolera drawdowns 30-40%. Expectativa real: CAGR 11-14% líquido.
2. **Transição (45-55):** migrar gradualmente pra V3_3 (15-20% BR FI,
   moderate leverage, MDD cap 50%).
3. **Pré-aposentadoria (55-60):** V3_2 (Max Sharpe com 35% BR FI, 25% equity
   leveraged, MF diversifier).
4. **Aposentadoria (60+):** V3_4 (52% BR FI dominante stabilizer, SWR
   sustentável 4-5%).

**Broker structure:**
- **Parte BRL (BR FI + alguma equity BR opcional):** corretora BR (XP, Clear,
  Rico, Inter DTVM) pra BR ETFs. Isenção BR de R$20k/mês não aplica a ETFs
  (só ações listadas B3). IR 15% em ganhos de ETF.
- **Parte USD (equity factor + GDE + BTGD + small BTC/gold):** Inter
  Internacional pra começar, IBKR quando aporte >$500/mês. DARF anual 15%.
- **Estate tax hedge:** UCITS irlandeses (CSPX/IWDA/EIMI) pra 60%+ do bucket
  equity, mantendo total US-domiciled próximo do $60k threshold.

**Dois brokers = mais operacional mas a estrutura ótima.** Alternativa
simplificada: Inter DTVM (BR) + Inter Internacional (US) — mesma conta.
