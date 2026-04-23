# Plano C — TLDR (leia isso primeiro)

> 2 minutos de leitura. Detalhes completos em `ANALYSIS.md`. Histórico de
> revisões em `REVISIONS.md`.

## Glidepath por fase da vida (recomendação atual)

```
30-45 anos (acumulação)    → V3_1 Max CAGR       [0% BR FI, leverage 1,75×, SCV 25%]
45-55 anos (transição)     → V3_3 Bounded Growth [18% BR FI, leverage 1,35×, SCV 25%]
55-60 anos (pré-retirement)→ V3_2 Max Sharpe     [35% BR FI, leverage 1,25×]
60+   anos (retirement)    → V3_4 Max SWR        [52% BR FI, leverage 1,15×]
```

**Racional:** nos primeiros ~15 anos, foco total em max equity + factor tilts
(zero BR FI); BR FI entra só a partir dos 45 anos quando sequence risk começa
a importar, e escala progressivamente até virar 52% na aposentadoria.

## Sua proposta SSO 50%: não faça

Plano atual (P0) vs SSO 50% no backtest 2007-2026 (18,5y):

|  | P0 Atual | Sua SSO 50% | Delta |
|--|----------|-------------|-------|
| CAGR | 7,52% | 9,53% | +2,01pp ✅ |
| Sharpe | 0,37 | 0,34 | PIOR ❌ |
| MDD | -53,6% | **-71,1%** | +17,5pp pior ❌ |
| P(MDD>50% em 30y) | 30% | **79%** | 2,6× pior ❌ |
| SWR | 3,48% | 2,48% | -1,00pp ❌ |

**Kernel correto (capital efficiency), execução ruim.** Alternativa real é
**return stacking com overlay descorrelacionado**: **NTSX** (90%eq+60%bond) ou
**GDE** (90%eq+90%gold) — entregam eficiência de capital sem amplificar beta
puro.

Comparação direta 2006-2026:

| Ativo 100% | CAGR | Sharpe | MDD |
|------------|------|--------|-----|
| SPY | 9,84% | 0,54 | -51% |
| **NTSX_syn** (0,9 SPY + 0,6 IEF) | **11,50%** | **0,71** | -41% |
| SSO (LETF puro c/ fees) | 12,91% | 0,37 | -81% |

## As 4 carteiras finais (v3.2 revisada)

Janela backtest 2007-2026 (18,5y) usando proxies. Validação com dados reais
2020-2026.

| Carteira | Objetivo | CAGR | Sharpe | MDD | p50 TW 30y | SWR | BR FI% | Quando usar |
|----------|----------|------|--------|-----|------------|-----|--------|-------------|
| **V3_1 v3.2** | Max CAGR | **18,3%*** | **1,01** | **-28%** | **$12,3M** | 9,8% | 0% | **Acumulação 30-45** |
| **V3_2** | Max Sharpe | 12,5% | **1,12** | -18% | $3,7M | 8,3% | 35% | Pré-aposentadoria 55-60 |
| **V3_3** | Max TW/MDD≤50% | 11,7% | 0,79 | -36% | $3,3M | 6,7% | 18% | Transição 45-55 |
| **V3_4** | Max SWR | 11,7% | 1,36 | **-12%** | $3,1M | **8,6%** | 52% | Retirement 60+ |

(*) V3_1 em janela 2014-2026; sem BTGD em 2007-2026 o CAGR cai pra ~13,4% e
MDD -44,7% (vs -52% da versão com SSO). Real-world esperado: **13-15% CAGR
com MDD 35-45%**.

**V3_1 REVISTA em 3 mudanças importantes (pós feedback do usuário):**
1. **Removido SSO 10%** (era inconsistente com princípio "stacked overlay >
   LETF puro"). Redirecionado pra GDE+NTSI.
2. **Tilts balanceados em 25% total** (15% SCV + 10% Momentum, antes era
   25% SCV + 5% Mom, desbalanceado 5:1).
3. **Adicionado IDMO 3%** (momentum internacional — AQR: value+momentum
   correlação negativa -0,4 a -0,7, stacking melhora Sharpe).

Delta vs V3_1 original: Sharpe +0,08 / MDD melhor 7pp em 2008 / Leverage
1,51× (de 1,75×) / CAGR praticamente igual.

## Estrutura das 4 (pesos reais — V3_1 v3.2 atualizada)

| Ticker | V3_1 v3.2 | V3_2 | V3_3 | V3_4 |
|--------|-----------|------|------|------|
| **GDE** (90% SPX + 90% gold) | 35% | 20% | 20% | 15% |
| **NTSI/NTSE** (Int/EM 90/60) | 25% | 10% | 20% | 0% |
| **AVUV + AVDV** (SCV, 15% total em V3_1) | 15% | 15% | 25% | 13% |
| **SPMO + IDMO** (Momentum, 10% total em V3_1) | 10% | 0% | 5% | 0% |
| **AVEM** (EM core) | 5% | 0% | 5% | 0% |
| ~~**SSO**~~ | ~~0%~~ | ~~0%~~ | ~~0%~~ | ~~0%~~ |
| **DBMF + KMLM** (MF) | 0% | 15% | 5% | 15% |
| **B5P211 + IMAB11** (IPCA+) | 0% | 25% | 15% | 35% |
| **LFTS11** (Selic cash) | 0% | 0% | 0% | 10% |
| **DINF11** (isento IR) | 0% | 10% | 3% | 7% |
| **BTGD + IBIT + GLDM** (gold/BTC) | 10% | 5% | 2% | 5% |
| **Total factor tilts** | **25%** (15 SCV + 10 Mom) | 15% | 30% | 13% |
| **Leverage efetivo** | **1,51×** | 1,25× | 1,35× | 1,15× |

## Justificativa do balance SCV/Momentum (25% total)

Literatura AQR "Our Model Goes to Six" + "Fact, Fiction, and Momentum":
- Correlação HML vs UMD = **-0,4 a -0,7** (Asness/Frazzini)
- Peso ótimo momentum em portfolio ótimo = **~38%** (AQR French-data analysis)
- Stacking value + momentum melhora Sharpe pela correlação negativa condicional

Seu argumento psicológico também é válido: **Larry Swedroe estima que apenas
~5% dos investidores DIY mantêm tilt de SCV** (tracking error pain). 25% total
balanceado minimiza lag vs SPY nos piores cenários.

**Escolha atual (balanceada e defensável):**
- 15% SCV (AVUV 10% + AVDV 5%)
- 10% Momentum (SPMO 7% + IDMO 3%)
- 5% EM core (AVEM)
- Total factor: 30% (25% efetivo SCV+Mom + 5% EM geographical)

Caveat tax: Momentum tem turnover ~100%/ano → distribuições de cap gains →
15% DARF. Drag real estimado 1-1,5%/ano pra brasileiro (vs 0,3-0,5% do AVUV).
A 10% alocação o premium compensa.

## O que mudou do Plano C atual

| | Plano atual (P0) | V3_1 (acumulação) |
|--|------------------|-------------------|
| Estrutura | 100% equity long-only factor | Return stacking + factor + leverage |
| Alavancagem | 1,0× | 1,75× via GDE + NTSX + SSO |
| Fixed income | 0% | 0% (vem depois, fase transição) |
| Gold/BTC | 5% | 5% (BTGD + IBIT, concentrado) |
| CAGR esperado 30y | 7,5% | 12-14% (real-world) / 18,3% (backtest bull) |
| Sharpe | 0,37 | 0,93 |
| Terminal wealth 30y p50 | $1,50M | $12,4M (backtest bull) / ~$5M (real-world) |

## Três decisões estruturais (evidência-based)

### 1. Bonds em BRL, não em USD (quando entrar em FI)

Campbell-Viceira (2010, JoF), Vanguard (2018, 2023), Ben Felix/PWL: bonds
devem ser na moeda de consumo. Para brasileiro:
- NTN-B real yield IPCA+6% domina TIPS 2% em 400bps
- BRL/USD vol 15-20% destrói função de stabilizer de um bond
- BR FI usado (quando entrar após 45 anos): **B5P211** (IPCA+ curto),
  **IMAB11** (IPCA+ longo), **LFTS11** (Selic cash), **DINF11** (debênture
  incentivada — **isento IR**)

### 2. GDE > NTSX como core de capital efficiency

GDE (WisdomTree 90% SPX + 90% gold, TER 0,20%, AUM $629M, inception
2022-03):
- Capital efficiency 1,8× com overlay em GOLD em vez de bonds
- Gold é descorrelacionado com equity (correlação ~0) E com BRL (hedge
  inflação)
- Compatível com "bonds em BRL separado" — sleeve de bond interna do NTSX é
  em USD; GDE é puro equity + gold

### 3. Stacked alts para BTC/gold

| Ticker | Veredicto | Use |
|--------|-----------|-----|
| GDE | ✅ **Core** (já na carteira) | Equity + gold stacked 1,8× |
| BTGD (100% BTC + 100% gold) | 🎯 **Satellite 3-5%** | Debasement hedge |
| RSSX (100% SPX + 100% gold/BTC) | ⏳ Esperar track record | Inception mai-2025 |
| ISBG | ❌ **Descartar** | AUM <$5M, decay option |

## ⚠️ Risco crítico: US Estate Tax

Brasileiro (non-resident alien) com ETFs US-domiciliados >$60k paga até 40%
de estate tax federal US na morte. Exemplo: $1,5M em AVUV/GDE/NTSX →
herdeiros pagam ~$576k.

Mitigação:
- **UCITS irlandeses na IBKR** (CSPX/IWDA/VWCE/EIMI) para 60%+ do bucket
  equity — não são US situs
- **GDE/BTGD/RSSX não têm UCITS** — manter US-domiciled total perto de $60k
- Foreign corp (BVI/HK) para patrimônio >$500k

## Operacional — dois brokers (a partir dos 45 anos)

| Parte | Moeda | Broker |
|-------|-------|--------|
| BR FI (B5P211, IMAB11, LFTS11, DINF11) | BRL | Inter DTVM, XP, Clear, Rico |
| US equity + GDE + alts | USD | Inter Internacional (start); IBKR quando >$500/mês |

**Para os primeiros 15 anos (V3_1 puro)**: apenas broker US é necessário
(Inter Internacional ou IBKR). Adicionar broker BR quando chegar na fase de
transição (~45 anos).

## Caveats honestos

1. **Proxy CDI é otimista** pro sleeve BR FI. CDI tem duração zero; IMAB11
   real teve -8% em 2024 (ciclo Selic). MDD real BR FI: -5 a -8%, não o
   quase-zero do proxy.
2. **Janela 2007-2026 é bull-biased** (só 1 grande crash 2008). 50-100 anos
   seria ideal.
3. **V3_1 CAGR 18,3% é em janela 2014-2026 bull** (BTGD_syn força janela
   curta). Real-world 30-year expectativa: **12-14% com MDD 40-55%**.
4. **Sharpe 1,36 do V3_4 é artificialmente alto** por proxy CDI. Real-world
   esperado: 0,9-1,1 com duration risk modelado.
5. **Hand-picked weights**, não otimização matemática.
6. **FX risk não modelado** — portfolio mix BRL+USD assumido neutro.

## Próximo passo (se aprovar a v3.2)

1. Ler `ANALYSIS.md` completo (~900 linhas)
2. Setup broker US (Inter Internacional pra começar; IBKR quando aporte >$500/mês)
3. Implementar V3_1 v3.2 exatamente como descrito (11 tickers)
4. Definir estate tax mitigation: UCITS já agora (CSPX/IWDA pra parte do
   bucket equity), ou aceitar risco até patrimônio crescer
5. Testar 12 meses em paper trading antes de escalar aportes
6. Broker BR (Inter DTVM / XP / Clear) entra em cena aos ~45 anos pra BR FI
