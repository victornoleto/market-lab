# Pesquisa v3 — Bonds em moeda doméstica + BR Fixed Income + Return Stacked Alts

Gerado por agente de pesquisa em 2026-04-23, pós feedback do usuário. Fonte
primária para `ANALYSIS.md` v3.

---

## 1. "Bonds should be in consumption currency" — evidência

### Ben Felix / PWL Capital (posição mais clara)

Do episode 379 do Rational Reminder (PWL Capital), Dan Bortolotti:

> "If you introduce currency risk, then you've kind of defeated the purpose.
> Because if the goal of bonds in your portfolio is to reduce volatility, once
> you introduce currency exposure, you lose that."

Mark McGrath (PWL) na mesma sessão:
> "If you have international bonds, you have either one of two things. You
> have an additional currency risk usually, or you've hedged that risk, which
> usually comes with an additional cost."

Política PWL: **bonds 100% domésticos** para residentes Canadá/EUA. Não usam
bonds internacionais em portfolios de clientes. Hedging consome o yield pickup.

### Vanguard Research (posição institucional)

Papers 2012, 2018 e 2023 da Vanguard — todos convergem:

> "Hedging the currency volatility allows the bonds to deliver bond-like
> returns with bond-like volatility."

Figure 2 do paper 2018: bonds hedgeados mantêm vol ~5%/ano, unhedged adiciona
+6-8% de vol sem premium equivalente.

### Campbell-Viceira (2010, Journal of Finance) — papel canônico

[NBER w13088](https://www.nber.org/papers/w13088) / [JoF 2010](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2009.01524.x):

> **Bonds:** "The risk-minimizing currency strategy for a global bond
> investor is close to a full currency hedge, with a modest long position
> in the US dollar."
>
> **Equities:** "Full hedge is often NOT the risk-minimizing approach" — USD,
> EUR, CHF funcionam como safe-haven hedges contra equities.

**Assimetria deliberada:** bonds devem ser hedgeados (=home currency); equities
podem/devem ser unhedged.

### Para brasileiro — números concretos

| Métrica | Valor histórico | Fonte |
|---------|-----------------|-------|
| CDI nominal 10y avg | ~13%/ano | Tesouro Direto |
| CDI líquido (pós-15% IR) | ~11%/ano | Cálculo |
| IPCA 10y avg | ~5-6%/ano | IBGE |
| NTN-B real yield atual | IPCA+5,5 a +6,35% | InfoMoney 2024, XP 2024 |
| US 10Y Treasury nominal | ~4,0-4,5% em USD | 2025-2026 |
| US TIPS 10Y real yield | ~1,8-2,2% em USD | 2025-2026 |
| BRL/USD vol anual | ~15-20% | Histórico |

**Diferencial de real yield a favor do BR: ~400bps/ano** (IPCA+6% vs TIPS 2%).
Adicionar FX vol 15-20% sobre bond de vol 5-7% **triplica a vol do stabilizer**.

**Conclusão:** para brasileiro, bonds domésticos (BR FI) são estritamente
dominantes sobre US bonds. A única ressalva teórica é risco soberano BR — mas
é preço pequeno comparado ao estrago da FX vol.

---

## 2. Brazilian Fixed Income ETFs — tabela completa

| Ticker | Nome | Gestor | Índice | TER | AUM | Inception | Tax PF |
|--------|------|--------|--------|-----|-----|-----------|--------|
| **B5P211** | IT Now IMA-B5 P2 | Itaú | IMA-B5 (NTN-B ≤5y) | 0,20% | R$ 2,87-3,54bi | 2020 | 15% IR fixo |
| **B5MB11** | Bradesco IMA-B5+ | Bradesco | IMA-B5+ (NTN-B >5y) | 0,20% | N/A | ~2019 | 15% IR fixo |
| **IMAB11** | It Now IMA-B | Itaú | IMA-B full curve | 0,25% | R$ 2,65bi | 2018 | 15% IR fixo |
| **LFTS11** | Investo Teva Selic | Investo | Teva LFT | 0,19% | R$ 3,01bi | 2021 | 15% IR fixo |
| **FIXA11** | BB/Mirae Renda Fixa Pré | Mirae | DI 3y | 0,30% | N/A | 2018 | 15% IR fixo |
| **DEBB11** | BTG Debêntures DI | BTG | ITDB DI | 0,60% | R$ 1,17bi | 2022-06 | 15% IR (NÃO isento) |
| **DINF11** | BTG Debêntures Incentivadas | BTG | ITDB Infra | ~0,60% | Menor | ~2023 | **0% ISENTO (Lei 12.431)** |

### Observações críticas

- **B5P211** vs **IMAB11**: B5P211 tem duração curta (~2,5y), MDD limitado;
  IMAB11 longa (~6-8y), MDD -7,92% em 2024 (ciclo Selic). Para stabilizer
  prefira B5P211; para match IPCA-aposentadoria longo prazo, IMAB11.
- **LFTS11**: cash-proxy funcional. TER 0,19% é alto vs Tesouro Selic direto
  (0% custódia até R$10k), mas zero come-cotas.
- **DEBB11**: atenção — **NÃO é isento de IR**. Pickup líquido sobre CDI
  ~130-150bps após 15% tax.
- **DINF11**: **único ETF de debêntures incentivadas isento de IR na B3**
  (Lei 12.431 infraestrutura). Isento em ganhos E distribuições. Alternativa
  tax-efficient de alta qualidade.

### Tax model consolidado

- **ETFs RF BR (B5P211, LFTS11, IMAB11, FIXA11, DEBB11):** 15% IR fixo sobre
  capital gains na venda. Sem come-cotas. Sem IOF após 30d.
- **DINF11 (debênture incentivada):** isento em tudo para PF.
- **Tesouro Direto**: regressivo 22,5→15% após 720d. ETF bate TD para holds
  curtos, empata no longo.

### Proxies históricos para backtest

- **CDI**: BCB série 12 desde 1986 (daily)
- **Selic over**: BCB série 1178
- **IPCA**: BCB série 433 desde 1980 (monthly)
- **IMA-B**: ANBIMA desde jan/2003 (daily); pré-2003 via NTN-B individual
- **ITDB DI / ITDB Infra**: Teva desde ~2020

---

## 3. Return Stacked Gold/BTC — tabela comparativa

| Ticker | Estrutura | TER | Inception | AUM | Track record |
|--------|-----------|-----|-----------|-----|--------------|
| **GDE** | 90% SPX + 90% gold futures (1.8x) | **0,20%** | 2022-03 | **~US$ 629M** | 4 anos ✅ |
| **RSSX** | $1 SPX + $1 gold/BTC risk-parity | 0,68% | 2025-05 | ~US$ 60-64M | <1 ano |
| **BTGD** | 100% BTC + 100% gold | 1,05% | 2024-10 | ~US$ 41-94M | 1,5 anos |
| **ISBG** | 1x BTC + 1x gold + option premium | 1,14% net | 2026-01 | ~US$ 1-4M | 3 meses ❌ |

### Análise por produto

**GDE** — produto mais maduro. 90% equity + 90% gold futures via subsidiária
Cayman. Backtest WisdomTree 2000-2022: CAGR 14,71%/StDev 20,25%,
outperformed S&P em 2001/2002/2008. Risco path dependency: em 2013
(stocks +32%/gold -28%) a sleeve gold teria sido disastrosa.
**Recomendação: core holding para quem quer gold exposure sem reduzir
equity exposure.**

**RSSX** — framework Hoffstein/Gordillo puro (100% SPX + 100% gold/BTC
risk-parity). Composição atual: SPY 72% + Gold Micro fut 67% + SPX E-Mini
31% + BTC fut 26% + IBIT 8% + cash 18%. **Conceitualmente sofisticado,
mas muito novo — esperar 2-3 anos de track record antes de posição
relevante.**

**BTGD** — stacking puro de scarcity assets. Sem exposição equity.
2024-2025 bull de gold+BTC entregou +26% YTD. Leverage via swaps + options
+ futures. **Use case: satellite 5-10% para debasement hedge; NÃO core.**

**ISBG** — NOVO, MICROSCÓPICO, DESCARTAR. AUM <$5M, estrutura
option-heavy (long FLEX calls + short listed calls/puts) que erode NAV em
bull markets. 100% do distribution é return of capital (não yield real).
**Não recomendo para aposentadoria.**

### Manual stacking vs integrated

**Manual stacking** (70% NTSX + 20% GLDM + 10% IBIT):
- Exposição ~63% equity + 42% bonds + 20% gold + 10% BTC = 135% total
- TER composto ~0,17%
- Flexibilidade rebalance; mais taxable events
- **Bonds US internos no NTSX: problemático pra quem quer strict home-currency**

**Integrated** (80% GDE + 20% IBIT):
- 72% equity + 72% gold + 20% BTC = 164% exposure
- TER composto ~0,21%
- Rebalanceamento interno GDE cuida do equity/gold ratio
- Menos taxable events pra brasileiro (DARF anual)
- **Zero bond exposure — compatível com "BR FI separado"**

### Estate Tax — alerta crítico mantido

Todos (GDE, RSSX, BTGD, ISBG, IBIT, GLD, GLDM, FBTC, BITB, NTSX) são
**US-domiciled = US-situs**. Threshold non-resident alien = US$ 60.000.
Acima: estate tax até 40%. Brasil não tem treaty com US.

Mitigação: (i) limite US$ 60k por conta, (ii) contas conjuntas (2× threshold),
(iii) UCITS irlandeses onde disponíveis — MAS **nem GDE nem RSSX nem BTGD nem
ISBG** têm versão UCITS.

---

## Síntese operacional

1. **Bonds sleeve 20-40% do portfolio**: 100% BRL. Mix sugerido — 40%
   B5P211 (IPCA+ curto, stabilizer), 30% IMAB11 ou B5MB11 (IPCA+ longo),
   20% LFTS11 (cash), 10% DINF11 (crédito isento).
2. **Equity + gold core sleeve** (US-exposed via Inter): GDE como
   capital-efficient core — se respeitar threshold estate tax US$ 60k.
3. **Gold/BTC satellite 5-10%**: BTGD para stacking concentrado OR manual
   GLDM + IBIT. ISBG descartar.
4. **Cuidado estrutural**: limite US$ 60k total US-domiciled por conta
   individual; usar conta conjunta ou UCITS alternatives onde existem.

---

## Sources — consolidadas

### Bonds home currency
- [PWL Episode 379 — Currency Hedging, Bond Misconceptions](https://pwlcapital.com/episode-379-ama-9-covered-call-etfs-currency-hedging-and-bond-misconceptions/)
- [Rational Reminder 349: AMA #4](https://rationalreminder.ca/podcast/349)
- [Vanguard 2018 PDF — The portfolio currency-hedging decision](https://passiveinvestingaustralia.com/wp-content/uploads/downloads/ISGPCH.pdf)
- [Vanguard UK — Going global with bonds (2023)](https://www.vanguard.co.uk/content/dam/intl/europe/documents/en/going-global-with-bonds-the-benefits-of-a-more-global-fixed-income-allocation-eu-en-pro.pdf)
- [Global Currency Hedging NBER w13088](https://www.nber.org/papers/w13088)
- [Global Currency Hedging JoF 2010](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2009.01524.x)
- [Expected Returns — Ilmanen CFA PDF](https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2012/rf-v2012-n1-1-pdf.PDF)

### BR Fixed Income
- [B5P211 fact — Morningstar](https://www.morningstar.com/etfs/bvmf/b5p211/quote)
- [IMAB11 — Morningstar](https://www.morningstar.com/etfs/bvmf/imab11/quote)
- [LFTS11 — Investo](https://www.investoetf.com/etf/lfts11/)
- [DEBB11 tax confirmação — Clube dos Poupadores](https://clubedospoupadores.com/etf/debb11.html)
- [DINF11 — BTG Pactual](https://www.btgpactual.com/asset-management/etf-debentures-infra)
- [Tesouro Direto histórico](https://www.tesourodireto.com.br/en/produtos/dados-sobre-titulos/historico-de-precos-e-taxas)

### Return Stacked alts
- [GDE WisdomTree Investment Case PDF](https://www.wisdomtree.com/-/media/us-media-files/documents/resource-library/investment-case/the-case-for-efficient-gold-plus-equity-strategy-fund-gde.pdf)
- [RSSX — Return Stacked ETFs](https://www.returnstackedetfs.com/rssx-return-stacked-us-stocks-gold-bitcoin/)
- [BTGD — Quantify Funds](https://quantifyfunds.com/stackedbitcoingoldetf/btgd/)
- [ISBG — Quantify Funds](https://quantifyfunds.com/optionsbasedincome/isbg/)
- [Return Stacking paper — Catalyst/ReSolve](https://catalyst-insights.com/wp-content/uploads/2021/09/Return-Stacking-Paper-ReSolve-Newfound.pdf)

### Brazilian investor + estate tax
- [Inter&Co Global](https://inter.co/pt/us/investments/)
- [Bogleheads non-US guide](https://www.bogleheads.org/wiki/Non-US_investor's_guide_to_navigating_US_tax_traps)
- [IRS Estate Tax NRA](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax-for-nonresidents-not-citizens-of-the-united-states)
