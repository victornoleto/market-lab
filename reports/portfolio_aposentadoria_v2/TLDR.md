# Plano C — TLDR (leia isso primeiro)

> 2 minutos de leitura. Detalhes completos em `ANALYSIS.md`. Histórico de
> revisões em `REVISIONS.md` (3 iterações 2026-04-23).

## O que é

Revisão do seu `portfolio-aposentadoria.md` (Plano C) baseada em factor
investing + return stacking + renda fixa em moeda doméstica. 4 carteiras
finais otimizadas, uma por função objetivo.

## Sua proposta SSO 50%: não faça

Plano atual (P0) vs SSO 50% no backtest 2007-2026 (18,5y):

|  | P0 Atual | Sua SSO 50% | Delta |
|--|----------|-------------|-------|
| CAGR | 7,52% | 9,53% | +2,01pp ✅ |
| Sharpe | 0,37 | 0,34 | PIOR ❌ |
| MDD | -53,6% | **-71,1%** | +17,5pp pior ❌ |
| P(MDD>50% em 30y) | 30% | **79%** | 2,6× pior ❌ |
| SWR | 3,48% | 2,48% | -1,00pp ❌ |

**Kernel correto (capital efficiency), execução ruim.** SSO é leverage puro
sobre beta, sem diversificador no overlay. A alternativa certa é **return
stacking**: NTSX (90%eq+60%bond) ou **GDE** (90%eq+90%gold) — entregam
eficiência de capital com overlay descorrelacionado, não amplificado.

Comparação direta 2006-2026:

| Ativo 100% | CAGR | Sharpe | MDD |
|------------|------|--------|-----|
| SPY | 9,84% | 0,54 | -51% |
| **NTSX_syn** (0,9 SPY + 0,6 IEF) | **11,50%** | **0,71** | -41% |
| SSO (LETF puro com fees) | 12,91% | 0,37 | -81% |

NTSX entrega quase SSO-CAGR com **metade do MDD**.

## As 4 carteiras finais

Janela de backtest 2007-2026 (18,5y) usando proxies long-history.
Validação com dados reais 2020-2026 (veja caveat abaixo).

| Carteira | Objetivo | CAGR | Sharpe | MDD | p50 TW 30y | SWR | BR FI% | Quando usar |
|----------|----------|------|--------|-----|------------|-----|--------|-------------|
| **V3_1** | Max CAGR | **18,3%*** | 0,93 | -30% | **$12,4M** | 9,6% | 0% | Acumulação 30-45 |
| **V3_2** | Max Sharpe | 12,5% | 1,12 | -18% | $3,7M | 8,3% | 35% | Pré-aposentadoria 55-60 |
| **V3_3** | Max TW/MDD≤50% | 11,7% | 0,79 | -36% | $3,3M | 6,7% | 18% | **Default, 30-60 anos** |
| **V3_4** | Max SWR | 11,7% | **1,36** | **-12%** | $3,1M | **8,6%** | 52% | Aposentadoria 60+ |

(*) V3_1 janela 2014-2026 por BTGD_syn; os demais 2007-2026.

Bootstrap 30 anos, $10k inicial + $1k/mês = $370k contribuídos.

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

## O que mudou do Plano C atual

| | Plano atual (P0) | V3_3 (meu default) |
|--|------------------|---------------------|
| Estrutura | 100% equity long-only factor | Return stacking + factor + BR FI |
| Alavancagem | 1,0× | 1,35× via NTSX/GDE overlay |
| Fixed income | 0% | 18% BR FI (BRL em moeda de consumo) |
| Gold/BTC | 5% (IBIT+GLDM) | 22% (GDE integrado + GLDM + IBIT) |
| Managed futures | 0% | 5% DBMF |
| CAGR esperado (18y) | 7,5% | **11,7%** (+4,2pp) |
| Sharpe | 0,37 | **0,79** (+0,42) |
| Terminal wealth 30y p50 | $1,50M | **$3,31M** (+120%) |

## Três decisões estruturais (evidência-based)

### 1. Bonds em BRL, não em USD

Campbell-Viceira (2010, JoF), Vanguard (2018, 2023), Ben Felix/PWL: bonds
devem ser na moeda de consumo. Para brasileiro:
- NTN-B real yield IPCA+6% domina TIPS 2% em 400bps
- BRL/USD vol 15-20% destrói função de stabilizer de um bond
- BR FI usado: **B5P211** (IPCA+ curto), **IMAB11** (IPCA+ longo),
  **LFTS11** (Selic cash), **DINF11** (debênture incentivada — **isento IR**)

### 2. GDE > NTSX como core de capital efficiency

GDE (90% SPX + 90% gold, WisdomTree, TER 0,20%, AUM $629M, inception
2022-03):
- Capital efficiency 1,8× com overlay em GOLD em vez de bonds
- Gold é descorrelacionado com equity (correlação ~0) E com BRL (hedge
  inflação)
- Compatível com "bonds em BRL separado" (a sleeve bond interna do NTSX é
  em USD; GDE é puro equity + gold)

### 3. Stacked alts para BTC/gold

| Ticker | Veredicto | Use |
|--------|-----------|-----|
| GDE | ✅ **Core** (já na carteira) | Equity + gold stacked 1,8× |
| BTGD (100% BTC + 100% gold) | 🎯 **Satellite 3-5%** | Debasement hedge |
| RSSX (100% SPX + 100% gold/BTC) | ⏳ Esperar track record | Inception mai-2025 |
| ISBG | ❌ **Descartar** | AUM <$5M, decay option |

## ⚠️ Risco crítico: US Estate Tax

Brasileiro (non-resident alien) com ETFs US-domiciliados >$60k paga até 40%
de estate tax federal US na morte. Exemplo: $1,5M em AVUV/NTSX/GDE →
herdeiros pagam ~$576k.

Mitigação:
- **UCITS irlandeses na IBKR** (CSPX/IWDA/VWCE/EIMI) para 60%+ do bucket
  equity — não são US situs
- **GDE/BTGD/RSSX não têm UCITS** — manter US-domiciled total perto de $60k
- Foreign corp (BVI/HK) para patrimônio >$500k

## Operacional — dois brokers

| Parte | Moeda | Broker recomendado |
|-------|-------|---------------------|
| BR FI (B5P211, IMAB11, LFTS11, DINF11) | BRL | Inter DTVM, XP, Clear, Rico |
| US equity + GDE + alts | USD | Inter Internacional (start); IBKR quando >$500/mês |

Inter DTVM + Inter Internacional = mesma conta Inter, setup mais simples.

## Caveats honestos

1. **Proxy CDI é otimista** pro sleeve BR FI. CDI tem duração zero; IMAB11
   real teve -8% em 2024 (ciclo Selic). MDD real BR FI: -5 a -8%, não o
   quase-zero do proxy.
2. **Janela 2007-2026 é bull-biased** (só 1 grande crash 2008). 50-100 anos
   seria ideal.
3. **Sharpe 1,36 do V3_4 é artificialmente alto** por causa do proxy CDI.
   Real-world esperado: Sharpe 0,9-1,1 com duration risk adequadamente
   modelado.
4. **FX risk não está modelado.** O portfolio tem BRL e USD; backtest assume
   retornos em moedas nativas simplesmente combinados. O fluxo de caixa real
   seria em BRL com volatilidade cambial.
5. **Hand-picked weights, não otimização.** As 4 carteiras são designs
   estruturais — pequenas variações de peso não mudam o ranking.

## Próximo passo (se aprovar a v3)

1. Ler `ANALYSIS.md` completo (~750 linhas)
2. Decidir: V3_1 (agressivo) ou V3_3 (meu default) pra acumulação agora
3. Setup dois brokers: Inter DTVM (BR) + Inter Internacional (US)
4. Definir estate tax mitigation: UCITS já agora, ou aceitar risco até
   patrimônio crescer
5. Testar 12 meses em paper trading antes de escalar
