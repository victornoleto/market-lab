# Plano C v2 — TLDR (leia isso primeiro)

> Pra ler em 2 minutos. Detalhes técnicos em `ANALYSIS.md` (~750 linhas com
> backtest, citações de livros, pesquisa web 2024-2026, metodologia).

## O que eu fiz

1. Baixei dados reais de 37 ETFs + sintéticos pra back de 100 anos.
2. Revisei 17 livros do projeto + 30+ papers/posts 2023-2026 (AQR/Resolve/
   WisdomTree/PWL/Morningstar/Cederburg).
3. Testei 12 carteiras-candidatas em 3 janelas (real 2020-26, proxy 2006-26,
   long 1926-26) com bootstrap 30 anos + SWR.
4. Sintetizei as 4 carteiras finais, uma por função objetivo.

## Sua pergunta sobre SSO 50%: não faça

Seu plano atual (`P0`) vs SSO 50% (`P1`) no backtest 2006-2026:

|  | P0 Atual | P1 Seu SSO | Delta |
|--|----------|-------------|-------|
| CAGR | 7,5% | 9,4% | +1,9pp ✅ |
| Sharpe | 0,39 | 0,35 | **PIOR** ❌ |
| MDD | -50% | -69% | **+19pp pior** ❌ |
| P(MDD>50% em 30y) | 4% | **53%** | **13× pior** ❌ |
| SWR aposentadoria | 4,1% | 2,7% | -1,4pp ❌ |

**Kernel bom, execução ruim.** O princípio (eficiência de capital) é correto,
mas SSO é pura leverage sobre beta. A alternativa certa é **return stacking**:
NTSX (90% SPX + 60% Treasury futures, ER 0,20%) ou RSST (100% US + 100% MF).

Exemplo: NTSX 100% vs SSO 100% em 2006-2026:
- NTSX: CAGR 11,50% / Sharpe **0,71** / MDD -41%
- SSO:  CAGR 12,91% / Sharpe 0,37 / MDD -81%

NTSX entrega quase o mesmo CAGR com **metade do drawdown e quase 2× o Sharpe**.

## As 4 carteiras finais

Todas em `ANALYSIS.md` §6 com pesos detalhados.

| Carteira | Objetivo | CAGR | Sharpe | MDD | p50 TW 30y | Quando usar |
|----------|----------|------|--------|-----|------------|-------------|
| **FINAL_1** | Max CAGR | 9,1% | 0,61 | -35% | **$2,23M** | Acumulação 30-45 anos |
| **FINAL_2** | Max Sharpe | 9,2% | **0,70** | -28% | $1,47M | Pré-aposentadoria 55-60 |
| **FINAL_3** | Max TW c/ MDD≤50% | **9,4%** | 0,64 | -36% | $1,81M | **Meu default, 30-60 anos** |
| **FINAL_4** | Max SWR | 8,6% | 0,73 | -24% | $1,11M | Aposentadoria 60+ |

Todas batem seu plano atual simultaneamente em CAGR, Sharpe e MDD. Bootstrap
30 anos com inicial $10k + aporte $1k/mês.

## Estrutura comum das 4

```
Equity beta (levered 90/60 via NTSX/NTSI/NTSE): 40-70%
Factor tilts (AVUV + AVDV + SPMO): 15-30%
Managed futures diversifier (RSBT + DBMF): 0-25% (mais em aposentadoria)
Bonds diretos: 0-20% (mais em aposentadoria)
Alts (IBIT + GLDM): 3-12%
```

Leverage efetivo varia 1,15× (FINAL_4) a 1,55× (FINAL_1). **Nenhuma** usa
SSO/UPRO/QLD/TQQQ puros — porque return stacking dominou em todos os
backtests.

## Glidepath recomendado

- 30-45 anos: **FINAL_1** (agressivo)
- 45-55 anos: **FINAL_3** (bounded)
- 55-60 anos: **FINAL_2** (Sharpe maximizer)
- 60+: **FINAL_4** (retirement income)

OU se você acredita em Cederburg 2024 (evidência 38 países, 1M bootstraps
mostra all-equity domina TDF em retirement): **fica em FINAL_1 ou FINAL_3
a vida toda**.

## ⚠️ Alerta crítico: US Estate Tax

**Você não estava ciente disso, provavelmente.** ETFs US-domiciliados contam
como "US situs assets" para estate tax federal US. Brasileiros (non-resident
aliens) têm exemption de **apenas $60.000** (vs $15M cidadãos US). Tudo
acima é taxado até **40%**.

Exemplo: na sua morte com $1,5M em AVUV/AVUS/NTSX/etc, herdeiros pagam
~$576k. Quase **40% da sua riqueza some**.

Soluções (detalhe em `ANALYSIS.md` §8):
1. **UCITS irlandeses na IBKR** (CSPX, IWDA, VWCE, EIMI) para 60% do bucket
   equity. Não são US situs. Solução primária.
2. Foreign corporation (BVI/HK) pra >$500k US situs.
3. Cap US-domiciled a $60k via rebalanceamento estratégico.

**Isso deve estar no seu top-3 de prioridades** antes de dormir em cima dessa
carteira 30 anos.

## Operacional

- **Inter**: ok pra começar; spread FX 0,99-1,50% é o killer (~15-25% drag
  acumulado em 30 anos).
- **Migrar pra IBKR** quando aporte mensal passar $500-1k USD. ACAT entre
  corretoras US é grátis/barato.
- Aporte mensal = zero DARF (rebalance por compra).
- Venda ETFs US = 15% sobre ganho líquido (DAA anual), sem isenção R$35k.

## Próximo passo

1. Leia `ANALYSIS.md` completo quando tiver 20 min.
2. Responda o checklist §10 (6 perguntas-chave).
3. Defina: FINAL_1 ou FINAL_3 como ponto de partida.
4. Decida estate tax mitigation (UCITS vs limite $60k vs foreign corp).
5. Implementação em 3-6 meses, com teste em paper trading IBKR primeiro.
