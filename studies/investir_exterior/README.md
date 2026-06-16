# Investir no Exterior: Brasil vs. Dólar

Estudo **educacional** que compara formas de um residente brasileiro ter exposição
internacional, em três caminhos:

1. **Brasil** — ETF cotado na B3 (IVVB11, WRLD11, VWRA11), corretora sem corretagem;
2. **Inter** — Conta Global, comprando ETF US lá fora (VOO, VT), spread 1,5%→0,99% + IOF;
3. **Interactive Brokers — ETF US** — VOO/VT, câmbio via casa de câmbio (Transfer Bank/Wise/Remessa);
4. **Interactive Brokers — UCITS irlandês** — CSPX (S&P 500) / VWRA (global): 15% de retenção de
   dividendos, acumula e sem imposto sucessório dos EUA.

A pergunta: *vale a pena investir no exterior pelo Brasil ou mandar dólares para fora?*
Saída em português, para divulgação (r/investimentos), em **dois formatos**:

- `outputs/relatorio.html` — gráficos **interativos** (Plotly via CDN, fonte IBM Plex Sans);
- `outputs/relatorio.md` + `outputs/plots/*.png` — markdown com os gráficos como imagens.

Em **ambos**, cada gráfico vem com uma **tabela de valores** logo abaixo (as curvas em alguns
pontos no tempo + o resultado final), para ler os números sem depender do hover.

> ⚠️ **Não é estratégia de investimento nem recomendação.** É uma comparação determinística
> de custos e tributação. Premissas (taxas, spread, IOF, IR) e fontes em `SPEC.md`.
> IOF e alíquotas mudaram muito em 2025–2026 — **confirme com um contador.**

## Como rodar

```bash
uv run python -m studies.investir_exterior.run                 # gera HTML + Markdown
uv run python -m studies.investir_exterior.run --format html    # só o HTML interativo
uv run python -m studies.investir_exterior.run --format md      # só o Markdown + plots/
uv run python -m studies.investir_exterior.run --open           # gera e abre o HTML
uv run python -m studies.investir_exterior.run --today 2026-06-16 -v
```

Na primeira execução, baixa e cacheia as séries do Yahoo Finance (`.cache/yfinance/`):
`SPY`, `VT`, `BRL=X` e os ETFs B3 reais (`IVVB11.SA`, `WRLD11.SA`, `ACWI11.SA`, `VWRA11.SA`).

## Estrutura

| Arquivo | Função |
|---------|--------|
| `config/base.yaml` · `config.py` | todas as premissas (taxas, spreads, IOF, IR) — ajustáveis |
| `data.py` | baixa séries e decompõe retorno em preço + dividendo |
| `costs.py` · `simulate.py` | funções puras de custo/IR; curvas (aporte único + DCA), decomposição, break-even |
| `chartdata.py` | prep de dados dos gráficos (puro, sem render) |
| `plots_png.py` · `plots_plotly.py` | renderers: matplotlib (PNG p/ markdown) e Plotly (interativo p/ HTML) |
| `content.py` | prosa em PT estruturada — fonte única dos dois relatórios |
| `report_html.py` · `report_md.py` · `report.py` | render HTML / render Markdown / orquestrador `generate_all` |
| `util.py` · `run.py` | formatadores e tabelas / CLI (`--format html\|md\|all`) |
| `SPEC.md` | metodologia, premissas e **fontes** de cada número |

## Política de dados

Fonte de preços: **Yahoo Finance** (yfinance), uso pessoal/educacional. As curvas longas dos
ETFs B3 são **reconstruções sintéticas** (índice × dólar × custos), validadas contra a cotação
real na seção 7 do relatório. Ver `SPEC.md` §Limitações.
