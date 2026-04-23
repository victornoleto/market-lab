# Pesquisa web 2024-2026 — fonte consolidada

Relatório gerado por agente de pesquisa em 2026-04-23. Cobre 10 tópicos com
links reais e dados numéricos. Usado como referência para o documento
`ANALYSIS.md`.

---

## 1. Leveraged ETF Buy-and-Hold — Evidência Moderna

### Consenso
Consenso acadêmico continua cético sobre buy-hold puro de SSO/UPRO/TQQQ, mas
com nuance: (a) volatility decay é real mas não fatal em bull markets
sustentados; (b) o que mata é alta volatilidade + trend negativo (ex. 2008,
2022); (c) portfólios leverage-com-hedge (HFEA) colapsaram em 2022 quando a
correlação bonds/stocks quebrou.

### Papers canônicos
- Cheng & Madhavan (2009) — "Dynamics of Leveraged and Inverse ETFs"
  [SSRN 1393995](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1393995)
- Leung & Santoli (SIAM J. Fin. Math 2016) — path-dependence
  [SIAM](https://epubs.siam.org/doi/10.1137/090760805)
- "Compounding Effects in Leveraged ETFs: Beyond the Volatility Drag Paradigm"
  [arXiv 2504.20116](https://arxiv.org/html/2504.20116v1) (2025) —
  argumenta que literatura tradicional superestima drag em regimes de
  trend positivo persistente.

### Dados numéricos
- SSO (2x SPY, inception 2006): drawdown histórico -85% em 2008-2009.
- UPRO (3x SPY, inception jun/2009): MDD -76.82% em 23/mar/2020 (COVID);
  -57.2% em 2022.
- Backtest sintético 1950+:
  - 2x: CAGR ~13.2% / MDD 87.3%
  - 3x: CAGR ~16.1% / MDD 97.7%
  - Fonte: [Van Domelen Seeking Alpha](https://seekingalpha.com/instablog/30945655-dane-van-domelen/3802666-performance-of-zero-tracking-error-s-and-p-500-leveraged-etfs-since-1950)
- ERs atuais: SSO 0.91% / UPRO 0.91% / QLD 0.95% / TQQQ 0.88%.
- Borrowing cost implícito: SOFR + spread (~5-6% a.a. com Fed Funds 5%).

### HFEA 55/45 UPRO/TLT post-2022
- Pico-vale 2022: +150% cumulativo (jan/22) para -14% (out/22) — peak-to-trough
  ~65-67% em 9 meses.
- TMF (3x TLT) MDD ~-92% desde inception; precisou 1:10 reverse split em 2022.
- Recuperação: abr/24 +26%, abr/25 +37% (ainda abaixo do pico 2022).
- Fontes: [HFEA Summary](https://hfea.neocities.org/),
  [OptimizedPortfolio](https://www.optimizedportfolio.com/hedgefundie-adventure/),
  [Bogleheads HFEA II](https://www.bogleheads.org/forum/viewtopic.php?t=288192).

### Por que 2022 matou HFEA
Tese HFEA depende da correlação negativa stocks/bonds. Em 2022, Fed tightening +
inflação 9% derrubaram simultaneamente equities (-19.5% SPX) e LTT (-31% TLT,
-71% TMF via 3x + convexidade negativa). O "diversificador" virou
"amplificador". Mecanismo: hedge bonds funciona em regimes de inflação
ancorada — falha em regime shock inflacionário.

---

## 2. WisdomTree Efficient Core (NTSX/NTSI/NTSE)

### Estrutura
- NTSX: 90% S&P 500 + 60% Treasury futures (duração ~7 anos). ER 0.20%.
  Inception 02/ago/2018.
- NTSI: DM ex-US + Treasury futures 90/60. ER 0.26%. Inception 20/mai/2021.
- NTSE: EM + Treasury futures 90/60. ER ~0.32%. Inception 20/mai/2021.

### AUMs (jun/2024)
- NTSX: ~$1B
- NTSI: ~$330M
- NTSE: ~$27M (liquidez limitada — spread pode ser problema)

Fonte: [WisdomTree Efficient Core Family PDF](https://www.wisdomtree.com/-/media/us-media-files/documents/resource-library/investment-case/the-case-for-efficient-core-fund-family.pdf)

### Performance 2022 (stress test)
- NTSX 2022: -9.82% vs 60/40 tradicional -17.39% vs S&P 500 -18%.
- NTSX resistiu melhor que 60/40 porque perna bond intermediária (dur 7) vs longa.
- MDD intra-ano ~>30% — pior que S&P 500 24% (refuta narrativa de
  "melhor que 60/40 em todo cenário").

### Asness update 2021
Cliff Asness 1996 "Why Not 100% Equities": 1926-1993 levered 60/40 a 155%
bateu equities: 11.1% CAGR vs 10.3% em mesma vol 20%.

Update 2021 (WisdomTree): 1926-2021 spread expandiu: **13.1% vs 9.1%**.
Fonte: [ETF Trends Update](https://www.etftrends.com/model-portfolio-content-hub/an-update-to-cliff-asnesss-study-on-the-benefits-of-a-levered-6040/).

---

## 3. Return Stacked ETFs (Hoffstein/ReSolve/Newfound)

### Lista completa (nov/2025)

| Ticker | Nome | Base 100% | Stack 100% | Inception | ER | AUM |
|--------|------|-----------|------------|-----------|-----|-----|
| RSST | US Stocks & Managed Futures | S&P 500 | Trend | 05/set/2023 | 0.99% | $399M |
| RSSY | US Stocks & Futures Yield | S&P 500 | Carry | 28/mai/2024 | 0.98% | $102M |
| RSSX | US Stocks & Gold/BTC | S&P 500 | Gold+BTC | 29/mai/2025 | 0.68% | $64M |
| RSBT | Bonds & Managed Futures | US Bonds | Trend | 07/fev/2023 | 1.02% | $127M |
| RSBY | Bonds & Futures Yield | US Bonds | Carry | 20/ago/2024 | 0.98% | $76M |
| RSBA | Bonds & Merger Arbitrage | US Bonds | Merger | 17/dez/2024 | 0.68% net | $52M |
| RSSB | Global Stocks & Bonds | Global Eq | US Treasuries | 04/dez/2023 | 0.40% net | $471M |

AUM total família ~$1.3B em 24 meses.
Fonte: [returnstackedetfs.com](https://www.returnstackedetfs.com/),
[ETF Express](https://etfexpress.com/2025/12/15/stacked-returns-gain-in-popularity/).

### Mecânica
Cada $100 investidos compra $100 equity/bonds via caixa + $100 exposure via
futures (margem ~10-15%). O stacking está em que futures não consomem capital
além de margem inicial.

### White papers
- Hoffstein & Gordillo (set/2021) — "Return Stacking" [Catalyst Insights PDF](https://catalyst-insights.com/wp-content/uploads/2021/09/Return-Stacking-Paper-ReSolve-Newfound.pdf)
- Newfound Research [thinknewfound.com](https://www.thinknewfound.com/)
- RCM Alternatives podcast (risco de nested leverage):
  [RCM](https://www.rcmalternatives.com/2021/09/researching-the-risks-of-return-stacking-with-corey-hoffstein-rodrigo-gordillo/)

### Performance since inception
- RSSB: 2024 +10.57%, 2025 +26.12%, CAGR inception 18.89%.
  [optimizedportfolio.com/rssb](https://www.optimizedportfolio.com/rssb/)
- RSST: tem sofrido (trend underperformed em 2023-2025 vs equities).
- Amostra <3 anos para maioria — qualquer Sharpe/MDD estatisticamente inútil.

### Caveats
1. Nested leverage risk (RSST + 60/40 tradicional = 1.5-1.8x efetivo).
2. ERs 0.68-1.02%: caros para passive, baratos para multi-strategy.
3. Capacity constraint real: $1B total AUM ainda pequeno.
4. 2025 lesson: equities dominaram, alternatives flat, opportunity cost alto.

---

## 4. Factor Investing 2023-2026

### Value Spread
Asness 2024 (AQR): value spread (expensive/cheap ratio) 95-100 percentil
histórico, mais extremo que 2008, comparável a 2000.
[AQR Is Systematic Value Dead](https://www.aqr.com/Insights/Perspectives/Is-Systematic-Value-Investing-Dead).

### AVUV performance
- 2024: +9.28%, 2025: +7.44% (ambos acima da categoria mas abaixo do SPX).
- ER 0.25%, turnover 4%.
- [Optimized Portfolio AVUV](https://www.optimizedportfolio.com/avuv/)

### SPMO performance
- 2024: +45.81%, 2025: +26.57%.
- 3-year CAGR: 31.89%; since inception 18.02%.
- [Morningstar SPMO](https://www.morningstar.com/etfs/arcx/spmo/performance)

### Fama-French 5-Factor status (Robeco 2024)
Profitability (RMW) é o único factor que sobrevive factor-spanning tests em
todos os mercados. Investment (CMA) fraco. Value (HML) recuperado post-2020.
[Robeco](https://www.robeco.com/en-int/insights/2024/10/fama-french-5-factor-model-five-major-concerns).

### Avantis vs Dimensional
- Avantis: integrated Value × Profitability, cap 30%/sector, mais quality.
- DFA: sequential Value primário, profitability/momentum screens depois.
- Diferenças ex-post <1%/ano — ruído.
- [Lazy Koala DFA vs Avantis](https://lazykoalainvesting.com/dfa-and-avantis/)

---

## 5. Retirement Planning 2024-2026

### Cederburg "Beyond the Status Quo" (AFA 2024)
Anarkulova, Cederburg, O'Doherty — dataset 38 países 1890-2019, 1M bootstrap.
- 100% equities (33% doméstico / 67% internacional) domina TDFs em:
  wealth at retirement, consumo sustentado, risco exaustão, bequests.
- TDF investors precisam de +63% savings pre-retirement para match.
- All-equity: +30% wealth médio vs TDF; 50/50 US/Int: +32%.
- Rising equity glidepath pós-retirement também domina TDF decrescente.
- [SSRN 4590406](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4590406)
- [SSRN 3594660](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3594660)

### Pfau & Kitces — Rising Equity Glidepath (2014)
30% equities → 70% ao longo de 30 anos reduz probabilidade E magnitude de
failure. Mecanismo: se primeiros anos ruins, vende bonds; se bons, não importa.
- [SSRN 2324930](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2324930)
- [Kitces Blog](https://www.kitces.com/blog/should-equity-exposure-decrease-in-retirement-or-is-a-rising-equity-glidepath-actually-better/)

### Bengen 4% Rule updates 2025
- Bengen 2025: 4.7% após rerun histórico (~400 cenários); hoje pode ser 5.25-5.5%.
  [Advisor Perspectives](https://www.advisorperspectives.com/articles/2025/08/29/bill-bengen-boosts-the-4-rule-to-4-7)
- Morningstar 2024: 3.7% baseado em forward-looking (valuations altas).
  2026 update: 3.9%.
  [Morningstar 2026](https://www.morningstar.com/retirement/whats-safe-retirement-withdrawal-rate-2026)

### Diversificação internacional + SWR
Pfau (2014): global diversification aumentou success rate 4% rule de 65.7%
para 78.3%. Consistente com Cederburg 2024.

### Brasileiros vivendo em BRL
Gap de literatura — nenhum paper canônico. Inferência: aporte mensal em USD
durante working years é DCA cambial natural; desacumulação requer hedge
parcial (NTN-B, IPCA+) ou conversão programada paralela.

---

## 6. Managed Futures / Trend Following

### Paper canônico
Hurst, Ooi, Pedersen (2017) — "A Century of Evidence on Trend-Following Investing"
[SSRN 2993026](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2993026).
- Dataset 1880-2016.
- Retornos positivos em cada década desde 1880.
- Performed well em 8 das 10 maiores crises (drawdowns 60/40).
- Correlação com stocks e bonds ≈ 0.
- Funciona em inflação alta/baixa, recessão/expansão.

### DBMF (iMGP DBi Managed Futures, inception 08/mai/2019)
- 2022: +21.4%; 2023: -5%; 2024: +7.25%; 2025 YTD: +13.84%; 12m: +27.30%.
- Since inception: 9.10% CAGR. ER ~0.85%.
- Replicação CTA index (behavior-based, não trend-pure).
- [iMGP fact sheet](https://imgpfunds.com/wp-content/uploads/pdfs/holdings/DBMF_FACTSHEETS_EN.pdf)

### KMLM (KraneShares Mount Lucas, inception 01/dez/2020)
- 2022: +30.37%; 2023: -5.66%; 2024: -1.70%.
- AUM $253M. ER 0.90%.
- Index-based (KFA MLM Index, 22 futures).
- [KFA fact sheet](https://kfafunds.com/resources/factsheet/2024_02_29_kmlm_factsheet.pdf)

### 2022 — crisis alpha validado
Único ano 15+ anos com stocks e bonds caindo juntos. Trend seguiu commodities
+, rates short (Fed hiking), USD long. Exatamente o cenário para o qual foi
construído.

### Alocação ótima (AQR)
AQR "Demystifying Managed Futures":
- 10-20% para crisis alpha sem sacrificar return;
- Mean-variance optimal: 15-25%.
- [AQR PDF](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/Demystifying-Managed-Futures.pdf)

---

## 7. Return Stacking Teórico

### Fundamentos
- Asness et al. (2015) "Investing with Style"
- Israel & Maloney (2014) "Understanding Style Premia"
  [AQR PDF](https://images.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/Understanding-Style-Premia.pdf)
- AQR 2025 "Exploring Capital Efficiency"
  [AQR Alternative Thinking 2025 Issue 3](https://www.aqr.com/-/media/AQR/Documents/Alternative-Thinking/AQR-Alternative-Thinking---Exploring-Capital-Efficiency.pdf)

### Asness "Our Model Goes to Six"
[AQR](https://www.aqr.com/Insights/Perspectives/Our-Model-Goes-to-Six-and-Saves-Value-From-Redundancy-Along-the-Way)
5-factor mata value como redundância. Adicionando UMD (momentum) = 6-factor e
value reviva. **Value + momentum tem correlação negativa — stacking os dois
melhora Sharpe.**

### Quality Minus Junk (Asness, Frazzini, Pedersen 2014)
QMJ long-high-quality/short-junk gera alpha significativo em 24 países.
[SSRN 2312432](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2312432)

---

## 8. Portfolio Optimization

### HRP (Hierarchical Risk Parity, López de Prado 2016)
Monte Carlo: HRP reduz out-of-sample variance vs minimum-variance CLA.
Não requer inversão de covariância. Alocação HRP vs CLA: top 5 receberam
62.57% vs 92.66% — HRP mais diversificado.
[SSRN 2708678](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2708678)

### PWL Capital 5-Factor model (Ben Felix)
Exemplo "5-Factor 80/20":
- 30% VTI (US total)
- 30% VXUS (ex-US total)
- 10% AVUV (US SCV)
- 6% AVDV (Int SCV)
- 4% AVES (Emerging Value)
- 20% BND

**16% total SCV tilt**, sem leverage.
[PWL PDF](https://pwlcapital.com/wp-content/uploads/2024/08/Five-Factor-Investing-with-ETFs.pdf)

---

## 9. Brazilian Investor Specifics

### Taxação US ETFs
- Dividendos: 30% withholding (reduzível a 15% via W-8BEN).
- Em BR: dividendos USD tributáveis como rendimento (carnê-leão mensal);
  imposto US compensável via tax credit.
- Capital gains em ações/ETFs US: US não taxa non-resident aliens;
  BR taxa 15% flat (Lei 14.754/2023), DAA anual em maio.
- **Isenção R$35k/mês só vale para ações listadas na B3, NÃO para ETFs US.**
- [PWC Brazil](https://taxsummaries.pwc.com/brazil/corporate/withholding-taxes)
- [Bogleheads non-US guide](https://www.bogleheads.org/wiki/Non-US_investor's_guide_to_navigating_US_tax_traps)

### Spread FX
- Inter Internacional: 0.99-1.50% (ida e volta dobra).
- IBKR: essentially 0 (interbank + $2 fee).
- Break-even: Inter mais barato até ~USD 500/mês; IBKR ganha acima.

### Hedge cambial BRL/USD
- Contra: aporte mensal é DCA cambial; BRL desvaloriza estruturalmente.
- A favor (parcial): décadas específicas (Real forte 2003-2011) — manter
  20-30% em NTN-B + IPCA+ em fase acumulação como tail risk hedge.

### **US Estate Tax — CRÍTICO (subestimado)**
- NRA com US situs >$60k: estate tax até 40% (vs $15M exemption cidadãos).
- **ETFs US contam como US situs assets.**
- **Solução robusta: ETFs domiciliados na Irlanda** (UCITS tipo CSPX, VWRA,
  IWDA) — NÃO são US situs. IBKR oferece acesso.
- Delaware LLC NÃO resolve (single-member disregarded).
- Foreign corp (BVI/HK/Caymans) pode resolver mas custo compliance
  $2-5k/ano.
- **Recomendação:** 60-70% do bucket USD via UCITS irlandeses + 30-40%
  US-domiciled onde specific exposure (AVUV, NTSX, RSST) não tem UCITS
  equivalente. Total US-domiciled próximo do threshold $60k OU setup foreign
  corp.
- [IRS NRA estate tax](https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax-for-nonresidents-not-citizens-of-the-united-states)
- [AbitOs 2025 Guide](https://abitos.com/the-2025-estate-and-gift-tax-guide-for-foreign-investors/)
- [Guardian Life](https://www.guardianlife.com/individuals-families/life-insurance/foreign-nationals/estate-tax)

---

## 10. Leverage + Factor combinado

### Estado da literatura: gap
Nenhum paper peer-reviewed específico combinando SSO + AVUV long-term.
Bogleheads forums + Portfolio Visualizer backtests disponíveis, amostra
curta (AVUV 2019+, sintético via DFSVX só vai a 1993).

### Estrutura do mercado
Não há **SCV-leveraged ETF puro**. Opções:
1. Margin account com AVUV (IBKR Pro: SOFR + 50bps ~ 5-6%/ano).
2. SSO + AVUV mix (alavancagem efetiva diluída).
3. Futures Russell 2000 Value (pouca liquidez vs E-mini SPX).

### UMDD (ProShares 3x Momentum)
Existe — mas é 3x momentum S&P 500 (large-cap momentum), não SCV.

### Recomendação prática
- **"Levered SCV" não é implementável via ETF público.**
- Proxy viável: NTSX (90/60 LC) + AVUV tilt + RSST stack simultaneamente.
  Aloca leverage onde é eficiente (LC via NTSX) e mantém factor tilt onde é
  aditivo (AVUV).
- Alternativa: portfolio margin em IBKR Pro (1.3-1.5x sobre AVUV a
  SOFR + 50bps — muito mais barato que LETFs).

---

## Gaps honestos

1. Literatura acadêmica peer-reviewed sobre SCV-leveraged é inexistente.
2. SWR específico para retirement em BRL com ativos USD não tem paper
   canônico.
3. HFEA post-2022 continua em recovery mas correlação stocks/bonds permanece
   fator risco estrutural não resolvido.
