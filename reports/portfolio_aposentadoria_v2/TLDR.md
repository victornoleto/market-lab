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

## As 4 carteiras finais

Janela backtest 2007-2026 (18,5y) usando proxies. Validação com dados reais
2020-2026.

| Carteira | Objetivo | CAGR | Sharpe | MDD | p50 TW 30y | SWR | BR FI% | Quando usar |
|----------|----------|------|--------|-----|------------|-----|--------|-------------|
| **V3_1** | Max CAGR | **18,3%*** | 0,93 | -30% | **$12,4M** | 9,6% | 0% | **Acumulação 30-45** |
| **V3_2** | Max Sharpe | 12,5% | **1,12** | -18% | $3,7M | 8,3% | 35% | Pré-aposentadoria 55-60 |
| **V3_3** | Max TW/MDD≤50% | 11,7% | 0,79 | -36% | $3,3M | 6,7% | 18% | Transição 45-55 |
| **V3_4** | Max SWR | 11,7% | 1,36 | **-12%** | $3,1M | **8,6%** | 52% | Retirement 60+ |

(*) V3_1 em janela 2014-2026 (bull-biased, BTGD_syn); sem BTGD em 2007-2026 o
CAGR cai pra ~13%. Real-world esperado: 12-14% com MDD 40-55%.

## Estrutura das 4 (pesos reais)

| Ticker | V3_1 | V3_2 | V3_3 | V3_4 |
|--------|------|------|------|------|
| **GDE** (90% SPX + 90% gold) | 30% | 20% | 20% | 15% |
| **NTSI/NTSE** (Int/EM 90/60) | 20% | 10% | 20% | 0% |
| **AVUV + AVDV** (SCV) | 25% | 15% | 25% | 13% |
| **AVEM + SPMO** (EM + Mom) | 10% | 0% | 10% | 0% |
| **SSO** (2× SPY) | 10% | 0% | 0% | 0% |
| **DBMF + KMLM** (MF) | 0% | 15% | 5% | 15% |
| **B5P211 + IMAB11** (IPCA+) | 0% | 25% | 15% | 35% |
| **LFTS11** (Selic cash) | 0% | 0% | 0% | 10% |
| **DINF11** (isento IR) | 0% | 10% | 3% | 7% |
| **BTGD + IBIT + GLDM** (gold/BTC) | 5% | 5% | 2% | 5% |

## Opcional: variantes SCV-heavy

Você disse "foco em factor tilts, especialmente SCV". Testei pressionar SCV
mais alto:

| V3_1 variante | SCV% | CAGR (2014-26) | Sharpe | CAGR (2007-26 no-BTGD) |
|---------------|------|----------------|--------|------------------------|
| **V3_1 Current** (default) | 25% | **18,3%** | **0,93** | **13,1%** |
| V3_1 SCV-Heavy | 40% | 16,6% | 0,83 | 11,3% |
| V3_1 Ultra-SCV | 55% | 15,0% | 0,76 | 9,9% |

**Trade-off:** cada 15pp extra de SCV custa ~1,7pp de CAGR no backtest dos
últimos 19 anos. Motivo: SCV ficou **abaixo** de SPX em 2010-2024 ("value
dead").

**Contra-argumento:** value spread hoje está no **percentil 95-100**
(Asness/AQR 2024) — posicionamento mais extremo desde 2000. Se mean reversion
funcionar, SCV deveria outperformar next decade. Backtest dos últimos 15 anos
**subestima** SCV futuro.

**Escolha honesta:**
- **V3_1 Current (25% SCV):** aposta em beta + leverage. Melhor número
  backtest.
- **V3_1 SCV-Heavy (40% SCV):** aposta contrarian no value premium. Pior
  número backtest, maior alpha esperado se mean reversion funciona.

Meu default: **V3_1 Current**. Se você quer apostar forte em SCV, V3_1
SCV-Heavy tem (AVUV 25% + AVDV 15%) em vez de (AVUV 15% + AVDV 10%).

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

## Próximo passo (se aprovar a v3)

1. Ler `ANALYSIS.md` completo (~900 linhas)
2. Decidir: V3_1 Current (25% SCV) ou V3_1 SCV-Heavy (40% SCV)?
3. Setup broker US (Inter Internacional ou IBKR)
4. Definir estate tax mitigation: UCITS já agora, ou aceitar risco até
   patrimônio crescer
5. Testar 12 meses em paper trading antes de escalar
6. Broker BR (Inter DTVM / XP / Clear) entra em cena por volta dos 45 anos
