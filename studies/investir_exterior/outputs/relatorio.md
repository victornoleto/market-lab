# Investir no exterior: pelo Brasil ou mandando dólares para fora?

*Comparação de custos e tributação · dados até 2026-06-15 · gerado em 2026-06-16*

> **TL;DR.** Os dois caminhos (ETF na B3 ou ETF lá fora) capturam **a mesma valorização do dólar** — um IVVB11 sobe em reais quando o dólar sobe, igual a um VOO. A diferença real **não é câmbio**, é **fricção**: taxa de administração, spread + IOF, retenção de 30% sobre dividendos dos EUA, IR na venda e risco de imposto sucessório americano. No S&P 500, ao longo de 22 anos, o ETF brasileiro (**11.17%** a.a.) praticamente **empata** com comprar VOO via Inter (**11.15%**) ou IBKR (**11.27%**). Mas há um quarto caminho que costuma ser o **mais eficiente**: comprar o **UCITS irlandês direto na IBKR** (CSPX no S&P 500, VWRA no global) — 15% de retenção de dividendos, acumula e **sem imposto sucessório dos EUA**. No S&P 500 ele **ganha de todos** (**11.51%** a.a.), porque o ETF brasileiro de S&P (IVVB11) embrulha um fundo *americano* e sofre 30% — **não existe um IVVB irlandês na B3**. Já no índice **global** o **VWRA11 da B3 empata/ganha** (**14.82%** vs **14.78%** do VWRA na IBKR), porque ele já embrulha o mesmo UCITS irlandês (15%) e ainda evita o pedágio do câmbio.

## 1. Patrimônio ao longo do tempo (aporte único)

Aporte único de R$ 100.000, líquido de tudo (taxas, spread, IOF, retenção de dividendos e IR na venda). Quatro caminhos por exposição: ETF na B3, ETF americano via Inter, ETF americano via IBKR e **UCITS irlandês via IBKR** (CSPX/VWRA). *Escala logarítmica:* em horizontes longos ela revela diferenças que a escala linear achata — mas a tabela embaixo de cada gráfico traz os números, já que as curvas ficam quase coladas.

![wealth_sp500](plots/wealth_sp500.png)

*Valores ao longo do tempo (última linha = resultado final):*

| Data | BR — IVVB11 | Inter — VOO | IBKR — VOO | IBKR — CSPX |
| :--- | :--- | ---: | ---: | ---: |
| 2004-01 | R$ 99.936 | R$ 95.591 | R$ 97.934 | R$ 97.934 |
| 2009-10 | R$ 49.161 | R$ 47.412 | R$ 48.574 | R$ 49.087 |
| 2013-12 | R$ 117.496 | R$ 114.677 | R$ 117.120 | R$ 119.389 |
| 2018-02 | R$ 235.527 | R$ 231.246 | R$ 236.547 | R$ 243.833 |
| 2022-04 | R$ 531.980 | R$ 526.195 | R$ 538.726 | R$ 560.944 |
| 2026-06 | R$ 1.077.213 | R$ 1.074.021 | R$ 1.099.982 | R$ 1.153.538 |

![wealth_mundo](plots/wealth_mundo.png)

*Valores ao longo do tempo (última linha = resultado final):*

| Data | BR — WRLD11 | BR — VWRA11 | Inter — VT | IBKR — VT | IBKR — VWRA |
| :--- | :--- | ---: | ---: | ---: | ---: |
| 2008-07 | R$ 98.467 | R$ 98.467 | R$ 94.188 | R$ 96.496 | R$ 96.495 |
| 2012-02 | R$ 107.149 | R$ 108.243 | R$ 104.062 | R$ 106.245 | R$ 106.637 |
| 2015-09 | R$ 276.851 | R$ 284.010 | R$ 270.719 | R$ 276.988 | R$ 280.135 |
| 2019-04 | R$ 385.468 | R$ 401.057 | R$ 380.561 | R$ 389.523 | R$ 396.586 |
| 2022-11 | R$ 633.912 | R$ 668.551 | R$ 632.108 | R$ 647.235 | R$ 662.842 |
| 2026-06 | R$ 1.117.669 | R$ 1.194.365 | R$ 1.125.764 | R$ 1.152.993 | R$ 1.187.369 |

## 2. Para onde vai o dinheiro: decomposição de custos

Partindo do "teto bruto" (índice × dólar sem nenhum custo), quanto cada fricção retira até o resgate. No caminho de fora, os dois maiores vilões de longo prazo são a **retenção de dividendos** (R$ 155.761 neste exemplo) e o **IR na venda** (R$ 171.886); o custo de **câmbio** (spread + IOF, ida e volta) soma R$ 57.471 — relevante, mas menor do que muita gente imagina ao diluir num horizonte longo.

![waterfall](plots/waterfall.png)

*Custo por componente (BRL no horizonte):*

| Componente | BR — IVVB11 | Inter — VOO | IBKR — VOO |
| :--- | :--- | ---: | ---: |
| Taxa adm. | R$ 68.327 | R$ 9.089 | R$ 9.089 |
| Retenção dividendos | R$ 149.439 | R$ 155.761 | R$ 155.761 |
| Câmbio entrada (spread+IOF) | R$ 400 | R$ 33.673 | R$ 18.204 |
| Câmbio saída (spread+IOF) | R$ 400 | R$ 23.798 | R$ 8.725 |
| IR na venda | R$ 172.449 | R$ 171.886 | R$ 176.467 |
| **Custo total** | R$ 391.015 | R$ 394.207 | R$ 368.246 |

## 3. Break-even: quando vale a pena "dolarizar"?

Comprar lá fora paga um pedágio de entrada (spread + IOF). A taxa de administração menor do VOO (0,03% vs 0,23% do IVVB11) tenta recuperar isso com o tempo — mas a retenção de 30% sobre dividendos trabalha contra. O painel de baixo mostra a vantagem líquida do caminho de fora; perto de zero = empate técnico.

![breakeven](plots/breakeven.png)

*Valores ao longo do tempo (última linha = resultado final):*

| Data | BR — IVVB11 | Inter — VOO | Vantagem US−BR |
| :--- | :--- | ---: | ---: |
| 2004-01 | R$ 99.936 | R$ 95.591 | -4.35% |
| 2009-10 | R$ 49.161 | R$ 47.412 | -1.75% |
| 2013-12 | R$ 117.496 | R$ 114.677 | -2.82% |
| 2018-02 | R$ 235.527 | R$ 231.246 | -4.28% |
| 2022-04 | R$ 531.980 | R$ 526.195 | -5.79% |
| 2026-06 | R$ 1.077.213 | R$ 1.074.021 | -3.19% |

## 4. Aportes mensais (DCA): o pedágio que se repete

Quem aporta R$ 1.000 por mês paga o spread + IOF **a cada remessa** no caminho de fora — enquanto na B3 não há câmbio explícito. Para tarifas fixas (Wise), aportes pequenos doem mais.

![dca_sp500](plots/dca_sp500.png)

*Valores ao longo do tempo (última linha = resultado final):*

| Data | Aportado | BR — IVVB11 | Inter — VOO | IBKR — VOO | IBKR — CSPX |
| :--- | :--- | ---: | ---: | ---: | ---: |
| 2004-01 | R$ 1.000 | R$ 1.000 | R$ 974 | R$ 986 | R$ 986 |
| 2009-10 | R$ 52.000 | R$ 37.435 | R$ 36.612 | R$ 37.058 | R$ 37.265 |
| 2013-12 | R$ 102.000 | R$ 184.823 | R$ 181.609 | R$ 183.822 | R$ 186.027 |
| 2018-02 | R$ 152.000 | R$ 469.046 | R$ 463.894 | R$ 469.545 | R$ 478.976 |
| 2022-04 | R$ 202.000 | R$ 1.170.531 | R$ 1.166.105 | R$ 1.180.311 | R$ 1.213.425 |
| 2026-06 | R$ 252.000 | R$ 2.480.102 | R$ 2.489.271 | R$ 2.519.598 | R$ 2.605.180 |

![dca_mundo](plots/dca_mundo.png)

*Valores ao longo do tempo (última linha = resultado final):*

| Data | Aportado | BR — WRLD11 | BR — VWRA11 | Inter — VT | IBKR — VT | IBKR — VWRA |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| 2008-07 | R$ 1.000 | R$ 985 | R$ 985 | R$ 960 | R$ 972 | R$ 972 |
| 2012-02 | R$ 44.000 | R$ 48.788 | R$ 49.161 | R$ 47.803 | R$ 48.386 | R$ 48.563 |
| 2015-09 | R$ 87.000 | R$ 217.430 | R$ 221.357 | R$ 214.503 | R$ 217.117 | R$ 219.080 |
| 2019-04 | R$ 130.000 | R$ 364.642 | R$ 375.138 | R$ 362.519 | R$ 366.936 | R$ 372.073 |
| 2022-11 | R$ 173.000 | R$ 659.157 | R$ 685.403 | R$ 660.963 | R$ 669.015 | R$ 681.422 |
| 2026-06 | R$ 216.000 | R$ 1.234.458 | R$ 1.297.331 | R$ 1.248.593 | R$ 1.263.804 | R$ 1.292.894 |

## 5. O tamanho do capital importa

Custos percentuais (spread, IOF, taxa adm, IR) são iguais para qualquer valor — então o CAGR não muda com o tamanho. O que muda: **tarifas fixas** (Wise) pesam mais em capital pequeno, e a **faixa de relacionamento** do Inter melhora o spread (Digital 1,5% → WIN 0,99% acima de R$1M).

![sensibilidade](plots/sensibilidade.png)

*CAGR líquido (% a.a.) por tamanho de capital:*

| Capital | BR — IVVB11 | Inter — VOO | IBKR — VOO | Wise — VOO |
| :--- | :--- | ---: | ---: | ---: |
| R$10k | 11.17% | 11.15% | 11.27% | 11.19% |
| R$100k | 11.17% | 11.15% | 11.27% | 11.20% |
| R$1.0M | 11.17% | 11.20% | 11.27% | 11.20% |

## 6. De onde vem o retorno: ação × dólar

O retorno em reais é o produto de duas forças: a valorização da bolsa (em dólar) e a valorização do dólar frente ao real. **Ambos os caminhos capturam as duas** — por isso "dolarizar" não dá um retorno cambial extra frente a um IVVB11. A desvalorização estrutural do real aparece na linha vermelha.

![cambio](plots/cambio.png)

*Valores ao longo do tempo (última linha = resultado final):*

| Data | S&P 500 em USD (ação) | USD/BRL (dólar) | S&P 500 em BRL (ação × dólar) |
| :--- | :--- | ---: | ---: |
| 2004-01 | 1.000 | 1.000 | 1.000 |
| 2009-10 | 0.858 | 0.593 | 0.509 |
| 2013-12 | 1.580 | 0.819 | 1.294 |
| 2018-02 | 2.566 | 1.122 | 2.878 |
| 2022-04 | 4.333 | 1.607 | 6.962 |
| 2026-06 | 8.344 | 1.760 | 14.682 |

## 7. Validação: o modelo reconstrói os ETFs reais?

Os ETFs da B3 são jovens (IVVB11 ~2014, WRLD11/ACWI11 ~2021), então as curvas de longo prazo são **reconstruções sintéticas** (índice × dólar × custos). Aqui comparamos a reconstrução com a cotação real onde ela existe — o **gap de CAGR** pequeno valida o modelo. O tracking error é medido em base **mensal** de propósito (pregões B3 × EUA criam ruído diário espúrio).

![validacao](plots/validacao.png)

*Valor final normalizado (base 1,0):*

| Painel | Sintético (fim, base 1,0) | Real (fim, base 1,0) |
| :--- | :--- | ---: |
| IVVB11 — gap CAGR +0.30pp | 10.600 | 10.284 |
| WRLD11 — gap CAGR +0.36pp | 1.443 | 1.421 |
| ACWI11 — gap CAGR +0.46pp | 1.708 | 1.670 |

| ETF | Período real | CAGR sintético | CAGR real | Gap | TE mensal (a.a.) |
| :--- | :--- | ---: | ---: | ---: | ---: |
| IVVB11 | 2014-04-29 → 2026-06-15 | 21.49% | 21.19% | +0.30 pp | 5.49% |
| WRLD11 | 2021-10-20 → 2026-06-15 | 8.20% | 7.84% | +0.36 pp | 4.39% |
| ACWI11 | 2021-02-01 → 2026-06-15 | 10.49% | 10.03% | +0.46 pp | 4.37% |

## 8. Resumo numérico

### Aporte único de R$ 100.000

| Cenário | Ativo | Exposição | Anos | CAGR líq. | Patrimônio final | Custo total |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| Brasil — ETF na B3 (sem corretagem) | IVVB11 | sp500 | 22 | 11.17% | R$ 1.077.213 | 26.63% |
| Brasil — ETF na B3 (sem corretagem) | WRLD11 | mundo | 18 | 14.39% | R$ 1.117.669 | 27.88% |
| Brasil — ETF na B3 (sem corretagem) | VWRA11 | mundo | 18 | 14.82% | R$ 1.194.365 | 22.93% |
| Inter — Conta Global (ETF US) | VOO | sp500 | 22 | 11.15% | R$ 1.074.021 | 26.85% |
| Inter — Conta Global (ETF US) | VT | mundo | 18 | 14.44% | R$ 1.125.764 | 27.36% |
| Interactive Brokers — ETF US | VOO | sp500 | 22 | 11.27% | R$ 1.099.982 | 25.08% |
| Interactive Brokers — ETF US | VT | mundo | 18 | 14.59% | R$ 1.152.993 | 25.60% |
| Interactive Brokers — UCITS irlandês | CSPX | sp500 | 22 | 11.51% | R$ 1.153.538 | 21.43% |
| Interactive Brokers — UCITS irlandês | VWRA | mundo | 18 | 14.78% | R$ 1.187.369 | 23.38% |

### Aportes mensais de R$ 1.000

| Cenário | Ativo | Aportado | Final líq. | Múltiplo | TIR a.a. |
| :--- | :--- | ---: | ---: | ---: | ---: |
| Brasil — ETF na B3 (sem corretagem) | IVVB11 | R$ 252.000 | R$ 2.145.213 | 8.51x | 17.52% |
| Brasil — ETF na B3 (sem corretagem) | WRLD11 | R$ 216.000 | R$ 1.081.353 | 5.01x | 15.88% |
| Brasil — ETF na B3 (sem corretagem) | VWRA11 | R$ 216.000 | R$ 1.134.779 | 5.25x | 16.33% |
| Inter — Conta Global (ETF US) | VOO | R$ 252.000 | R$ 2.114.023 | 8.39x | 17.41% |
| Inter — Conta Global (ETF US) | VT | R$ 216.000 | R$ 1.073.812 | 4.97x | 15.82% |
| Interactive Brokers — ETF US | VOO | R$ 252.000 | R$ 2.164.919 | 8.59x | 17.59% |
| Interactive Brokers — ETF US | VT | R$ 216.000 | R$ 1.099.341 | 5.09x | 16.03% |
| Interactive Brokers — UCITS irlandês | CSPX | R$ 252.000 | R$ 2.237.170 | 8.88x | 17.84% |
| Interactive Brokers — UCITS irlandês | VWRA | R$ 216.000 | R$ 1.123.900 | 5.20x | 16.24% |

## 9. O que os números não mostram (mas importa muito)

> **Imposto sucessório dos EUA (estate tax).** Ativos "US-situs" (ações e ETFs listados nos EUA, como VOO/VT) acima de **US$ 60 mil** são tributados em até **40%** no falecimento de um não-residente. ETFs da B3 e ETFs domiciliados na Irlanda (UCITS — ex.: CSPX/VWRA comprados na IBKR) **não** têm essa exposição. É o maior risco qualitativo do caminho "comprar US-domiciliado direto" (VOO/VT) para patrimônios maiores — e um motivo a mais para preferir o UCITS irlandês.

- **Retenção de dividendos (sem tratado BR–EUA):** ETF US-domiciliado retém **30%** dos dividendos; o W-8BEN não reduz (não há tratado). ETF irlandês (UCITS) retém **15%**. ETFs B3 que embrulham fundos US-domiciliados (IVVB11→IVV, WRLD11→VT) também sofrem os 30% internamente; só os de *wrap* irlandês (VWRA11) escapam para 15%. Comprar o **UCITS irlandês direto na IBKR** (CSPX no S&P 500, VWRA no global) dá esses 15% **sem** a camada extra de taxa do wrapper brasileiro — por isso o CSPX vence no S&P 500, onde não há equivalente irlandês na B3.
- **Tributação brasileira.** ETF de renda variável na B3: ganho de capital a **15.0%** (sensibilidade 17.5%), **sem** a isenção de R$20 mil das ações e sem come-cotas; DARF auto-recolhido. Investimento direto no exterior: a Lei 14.754/2023 tributa o ganho (em reais, incluindo variação cambial) a **15%** no ajuste anual, e dividendos a 15% (com crédito do imposto pago nos EUA, limitado — o excesso de 30% é perdido).
- **Burocracia.** Investir fora exige declarar no IRPF (bens e direitos no exterior), apurar ganho de capital e, acima de US$1 mi, a **CBE** ao Banco Central. ETF na B3 cabe no informe da corretora.
- **Complexidade operacional e câmbio de volta.** Trazer o dinheiro de volta tem novo spread + IOF (0,38% na volta). O caminho B3 é "um clique".

---

> **Metodologia.** Simulação determinística (não é recomendação de compra/venda nem estratégia de trading). Subjacentes: SPY (S&P 500, desde 2004) e VT (mundo, desde 2008) como proxies de retorno total; câmbio USD/BRL via `BRL=X`. Curvas de ETFs B3 são reconstruções sintéticas validadas contra a cotação real (seção 7). Premissas de taxas, spreads, IOF e tributos (jun/2026) estão em `config/base.yaml` e `SPEC.md` com fontes. **IOF e a alíquota de ETF mudaram várias vezes em 2025–2026 e podem mudar de novo** — confirme com um contador antes de decidir. Fonte de preços: Yahoo Finance (yfinance), uso pessoal/educacional.
