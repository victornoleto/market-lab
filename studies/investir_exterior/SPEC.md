# SPEC — Investir no Exterior: Brasil vs. Dólar

## Natureza do estudo

Estudo **educacional/comparativo**, **não é estratégia de investimento**: não busca
alpha, não aloca capital, não passa por gates (PBO/DSR/WF/bootstrap). Está **fora** do
framework A/B/C/D e **não conflita com o MAINTENANCE MODE** do mandate (mandate §1/§7).

**Saídas (português):** `outputs/relatorio.html` com gráficos **interativos** (Plotly via CDN — dep
`plotly>=5.0` no `pyproject.toml`; fonte IBM Plex Sans via Google Fonts) e `outputs/relatorio.md` +
`outputs/plots/*.png` (markdown com gráficos matplotlib). A prosa vive uma única vez em `content.py`,
consumida pelos dois renderers (`report_html.py`, `report_md.py`).

### Nota sobre a Regra 2 do CLAUDE.md (citação de livro)

A Regra 2 exige citar um dos 33 livros para cada escolha de *indicador/gate/parâmetro
de estratégia*. Aqui **não há** decisão de trading: as premissas são **regulatórias e de
mercado** (taxas de ETF, spreads de câmbio, IOF, alíquotas de IR). Portanto cito por
**fonte primária (URL / lei)**, não por livro. Esta é a forma correta de "citação
obrigatória" para este tipo de estudo.

---

## Pergunta central

> "Vale mais a pena investir no exterior pelo Brasil (ETFs na B3) ou mover o dinheiro
> para dólar e comprar lá fora (ETFs US via Inter / Interactive Brokers)?"

**Tese testada:** os dois caminhos capturam a *mesma* valorização do dólar; a diferença é
**fricção** (taxa adm, spread, IOF, retenção de dividendos, IR, imposto sucessório).

---

## Metodologia

Simulação determinística. Para cada exposição usamos um ETF-proxy de longo histórico e
decompomos o retorno diário:

```
r_total = adj_close.pct_change()    # retorno total bruto (reinveste dividendos)
r_price = close.pct_change()        # retorno só de preço
div     = (r_total - r_price).clip(lower=0)   # rendimento de dividendos do dia
```

Somamos de volta a taxa do proxy (`taxa_proxy`) para aproximar o índice puro; cada
instrumento desconta a SUA taxa de administração e a retenção sobre dividendos conforme a
estrutura do fundo. ETFs B3 (BRL) = `índice_usd_líquido × USD/BRL` (acumulam; IR só na
venda). ETFs US (USD) = converte BRL→USD na entrada e USD→BRL na saída (spread+IOF).

ETFs B3 são jovens, então as curvas longas são **reconstruções sintéticas**, validadas
contra a cotação real (gap de CAGR pequeno; ver seção 7 do relatório). Tracking error é
medido em base **mensal** (pregões B3 × EUA criam ruído diário espúrio).

---

## Premissas e fontes (jun/2026)

Todos os números vivem em `config/base.yaml`. ⚠️ = volátil/incerto em 2025–2026.

### Taxas de administração
| ETF | Taxa adm | Estrutura | Fonte |
|-----|----------|-----------|-------|
| IVVB11 | 0,23% | feeder de IVV (US-domiciliado) | BlackRock Brasil |
| WRLD11 | 0,36% | wrap de VT (US-domiciliado) | Investo/VanEck |
| VWRA11 | 0,30% | wrap de UCITS irlandês (FTSE All-World) | Investo |
| ACWI11 | 0,30% | MSCI ACWI | Trend/XP Asset |
| VOO | 0,03% | Vanguard S&P 500 (US-domiciliado, distribui) | Vanguard |
| VT | 0,06–0,07% | Vanguard Total World (US-domiciliado, distribui) | Vanguard |
| CSPX | 0,07% | iShares Core S&P 500 UCITS (Irlanda, acumula) `IE00B5BMR087` | justETF/BlackRock |
| VWRA | 0,22% | Vanguard FTSE All-World UCITS (Irlanda, acumula) `IE00BK5BQT80` | justETF/Vanguard |

UCITS irlandês comprado **direto na IBKR** (USD): retenção de dividendos **15%** (tratado EUA–Irlanda),
acumula (IR brasileiro só na venda, Lei 14.754) e **fora** do imposto sucessório dos EUA (situs irlandês).
É a 4ª via do estudo (`ibkr_ucits`). Tickers de validação no yfinance: `CSPX.L`, `VWRA.L`.

### Câmbio (spread sobre a taxa comercial)
| Canal | Spread | Tarifa fixa | Fonte |
|-------|--------|-------------|-------|
| Inter Digital/One | 1,50% | — | Exiap / Inter |
| Inter Black | 1,25% | — | Exiap |
| Inter WIN (≥ R$1M) | 0,99% | — | Inter / Passageiro de Primeira |
| Transfer Bank (IBKR) | 0,30% | — | transferbank.com.br |
| Wise | ~0,50% | US$6,96 + 0,53% | Exiap / Wise |
| Remessa Online | 0,70–1,64% (regressivo) | — | Exiap / Remessa |
| IBKR (conversão interna) | 0,002% (mín US$2) | — | Interactive Brokers |

### IOF câmbio ⚠️
- Remessa de investimento (ida): **1,1%**. Repatriamento (volta): **0,38%**.
- Fonte: Safra "O Especialista", Agência Brasil (decisão STF jul/2025). **Muito volátil**:
  mudou 4× em 2 meses em 2025.

### Tributos
- ETF de renda variável B3: ganho de capital **15%** (sensibilidade **17,5%** — proposta da
  MP 1.303/2025 rejeitada para ações, mas a discussão sobre ETF persiste), **sem** isenção de
  R$20 mil, **sem** come-cotas; DARF auto-recolhido. Fontes: B3 (Bora Investir), XP, Receita.
- Investimento direto no exterior (pessoa física): **Lei 14.754/2023** (vigente desde 2024) —
  ganho (em BRL, inclui variação cambial) e dividendos a **15%** no ajuste anual; **acaba** a
  isenção de R$35 mil/mês para aplicações financeiras. Fontes: Mayer Brown, EY, Trench Rossi,
  Vialto Partners. Lei 15.270/2025 (IRPFM) pode afetar rendas altas (> R$600k) — fora do
  escopo do investidor típico.
- Retenção de dividendos: EUA **30%** para residente no Brasil (sem tratado; W-8BEN não
  reduz). UCITS irlandês **15%** (tratado EUA–Irlanda). Crédito do imposto pago no exterior:
  reciprocidade BR–EUA reconhecida pela RFB ⇒ retenção efetiva ≈ max(30%, 15%) = **30%**;
  excesso perdido. Fontes: IRS Pub 515, Bogleheads, State Street (US vs Irish UCITS).
- Imposto sucessório dos EUA (estate tax) para não-residente: até **40%** sobre ativos
  US-situs acima de **US$60 mil**. Evitado por ETFs B3 e UCITS irlandês. Fonte: IRS, 360 Financial.

### Custos B3
- Corretagem **zero** (Inter/Rico/C6/NuInvest/Clear/...); emolumentos + liquidação ~**0,03%**.

---

## Dados

- Fonte: Yahoo Finance via `YFinanceSource` (cache em `.cache/yfinance/`). Uso pessoal/educacional.
- Proxies: `SPY` (S&P 500, desde 2004) e `VT` (mundo, desde 2008). Câmbio: `BRL=X` (desde dez/2003).
- Reais (validação): `IVVB11.SA` (2014+), `WRLD11.SA` (2021+), `ACWI11.SA` (2021+),
  `VWRA11.SA` (2025+, curto demais — só premissas).
- Janela limitada por `BRL=X` (S&P 500: ~2004; mundo: ~2008).

## Limitações

- Reconstrução sintética para o longo prazo (validada, mas não é a cota real).
- Premissas de IOF/IR voláteis (2025–2026) — **confirmar com contador**.
- Dividend yield estimado da decomposição `adj_close − close`, não do fluxo nominal por ação.
- Não modela: corretagem variável de IBKR (assumida zero p/ VOO/VT), rebalanceamento,
  custo de oportunidade de caixa, nem o IRPFM da Lei 15.270/2025.
