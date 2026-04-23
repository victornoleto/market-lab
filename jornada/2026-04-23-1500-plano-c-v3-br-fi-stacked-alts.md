# 2026-04-23 15h00 — Plano C v3: BR FI + return-stacked alts

## Contexto

Pós entrega da v2 (com correção de bug), o usuário leu o TLDR e fez 2 pedidos
específicos:

1. **Renda fixa deve ser em BRL, não em USD.** Argumento: US bonds (TLT/IEF/SHV)
   unhedgeados adicionam FX vol que destrói a função de stabilizer do bond
   sleeve. Pesquisar o argumento acadêmico e substituir por BR FI
   (B5P211/IPCA, LFTS11/Selic, DEBB11/Debenture, etc.).
2. **Expandir sleeve gold/BTC com return-stacked alternatives.** Considerar
   GDE (WisdomTree 90%SPX+90%gold), RSSX (SPX+gold/BTC), ISBG (novo,
   usuário não conhece), BTGD (100%BTC+100%gold).

## Produzido

- `reports/portfolio_aposentadoria_v2/CORRECTIONS_V3.md` — documento principal
  com nova análise v3, tabela comparativa, caveats.
- `reports/portfolio_aposentadoria_v2/data/web_research_v3.md` — pesquisa
  consolidada (Campbell-Viceira 2010, Vanguard 2018/2023, PWL Capital; BR FI
  ETFs; stacked alts).
- `scripts/07_download_br_and_new_alts.py` — downloader BR ETFs + new US ETFs
  + BCB CDI series (26 anos de histórico).
- `scripts/08_extend_panel_v3.py` — extensão do panel com sintéticos
  (GDE_syn, BTGD_syn, RSSX_syn).
- `scripts/09_final_portfolios_v3.py` — 4 carteiras v3 redesenhadas.
- `results/final_portfolios_v3.json` — backtest results.

## Achados principais

### Bonds em moeda doméstica: unanimidade acadêmica

Campbell-Viceira 2010 (JoF), Vanguard (2012/2018/2023), Ben Felix/PWL Capital
todos convergem: **bonds devem ser na moeda de consumo**. Para equities a
regra é relaxada; para bonds é estrita. Para brasileiro:

- NTN-B real yield IPCA+5,5-6,35% vs US TIPS 1,8-2,2% = **+400bps a favor
  BR**
- BRL/USD vol 15-20% > bond vol 5-7% → FX domina, destrói stabilizer

### Universo BR FI

**Ícone descoberto: DINF11** (BTG Pactual Debêntures Incentivadas Lei 12.431)
— único ETF BR de debêntures incentivadas, **isento total de IR pra PF**
(cap gains + distribuições).

### ISBG é descartado

ISBG (Quantify IncomeSTKd 1x BTC+1x Gold Premium): inception jan/2026, AUM
$1-4M, estrutura option-selling erode NAV em bull markets. **Não usar.**

### GDE vence sobre NTSX no sleeve "equity + hedge"

GDE (90% SPX + 90% gold futures, 1,8× leverage) tem TER 0,20% igual ao NTSX,
mas com sleeve de gold em vez de bonds US. Para investidor BR com FI
domiciliado em BRL, GDE é **a escolha correta** para a sleeve de
capital-efficiency.

### 4 carteiras v3 — Sharpe dispara

| | CAGR | Sharpe | MDD | BR FI% |
|--|------|--------|-----|--------|
| V3_1 Max CAGR | 18,3% | 0,93 | -30% | 0% |
| V3_2 Max Sharpe | 12,5% | 1,12 | -18% | 35% |
| V3_3 Max TW/MDD50 | 11,7% | 0,79 | -36% | 18% |
| V3_4 Max SWR | 11,7% | **1,36** | -12% | 52% |

V3 bate V2 em todos os eixos (com caveat: CDI proxy é otimista no MDD da
sleeve BR FI; real IMAB11 teve -8% em 2024).

## Caveats honestos

1. **Proxy CDI é otimista.** CDI tem duração zero; IMAB11 tem duração 6-8y e
   sofre em ciclos de alta Selic. Real MDD da sleeve BR FI: -5 a -8%.
2. **Janela 2007-2026 é bull-biased.** Só 1 crash grande (2008); 50+ anos
   seria ideal.
3. **Estate tax US$ 60k threshold continua sendo o risco não-endereçado mais
   crítico.** UCITS irlandeses onde possível.
4. **Dois brokers necessários:** corretora BR (Inter DTVM / XP / Clear) pra BR
   ETFs + Inter Internacional / IBKR pra US ETFs.

## Próximos passos para o usuário

1. Ler `reports/portfolio_aposentadoria_v2/CORRECTIONS_V3.md` completo
2. Decidir entre V3_1 (agressivo) ou V3_3 (default) pra acumulação 30-45
3. Setup operacional dois brokers (Inter DTVM + Inter Internacional fazem a
   ponte mais fácil; IBKR é mais barato em FX se aporte for >$500/mo)
4. Estate tax mitigation: definir se usa UCITS irlandeses para equity core e
   limita US-domiciled a <$60k
