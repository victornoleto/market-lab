"""Prosa do relatório (português), estruturada em blocos e independente de backend.

Fonte única de texto + layout: tanto o HTML quanto o Markdown iteram a mesma
lista de seções/blocos, evitando divergência entre os dois outputs. A ênfase é
escrita em markdown (`**negrito**`, `*itálico*`, `` `código` ``); o renderer HTML
converte para tags via util.md_inline_to_html.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

TITLE = "Investir no exterior: pelo Brasil ou mandando dólares para fora?"


@dataclass
class Para:
    text: str


@dataclass
class H3:
    text: str


@dataclass
class Bullets:
    items: list[str]


@dataclass
class Box:
    kind: str          # 'tldr' | 'alerta' | 'disclaimer'
    text: str


@dataclass
class ChartRef:
    key: str


@dataclass
class TableRef:
    key: str


@dataclass
class Section:
    title: str | None
    blocks: list = field(default_factory=list)


def subtitle(numbers: dict[str, Any]) -> str:
    return f"Comparação de custos e tributação · dados até {numbers['fim_dado']} · gerado em {numbers['data_hoje']}"


def build_layout(numbers: dict[str, Any]) -> list[Section]:
    n = SimpleNamespace(**numbers)
    return [
        Section(None, [Box("tldr",
            f"**TL;DR.** Os dois caminhos (ETF na B3 ou ETF lá fora) capturam **a mesma valorização do "
            f"dólar** — um IVVB11 sobe em reais quando o dólar sobe, igual a um VOO. A diferença real "
            f"**não é câmbio**, é **fricção**: taxa de administração, spread + IOF, retenção de 30% sobre "
            f"dividendos dos EUA, IR na venda e risco de imposto sucessório americano. No S&P 500, ao longo "
            f"de {n.yrs_sp} anos, o ETF brasileiro (**{n.cagr_ivvb}** a.a.) praticamente **empata** com "
            f"comprar VOO via Inter (**{n.cagr_voo_inter}**) ou IBKR (**{n.cagr_voo_ibkr}**). "
            f"Mas há um quarto caminho que costuma ser o **mais eficiente**: comprar o **UCITS irlandês "
            f"direto na IBKR** (CSPX no S&P 500, VWRA no global) — 15% de retenção de dividendos, acumula e "
            f"**sem imposto sucessório dos EUA**. No S&P 500 ele **ganha de todos** (**{n.cagr_cspx}** a.a.), "
            f"porque o ETF brasileiro de S&P (IVVB11) embrulha um fundo *americano* e sofre 30% — **não existe "
            f"um IVVB irlandês na B3**. Já no índice **global** o **VWRA11 da B3 empata/ganha** "
            f"(**{n.cagr_vwra}** vs **{n.cagr_vwra_irish}** do VWRA na IBKR), porque ele já embrulha o mesmo "
            f"UCITS irlandês (15%) e ainda evita o pedágio do câmbio.")]),

        Section("1. Patrimônio ao longo do tempo (aporte único)", [
            Para(f"Aporte único de {n.a0}, líquido de tudo (taxas, spread, IOF, retenção de dividendos e IR "
                 f"na venda). Quatro caminhos por exposição: ETF na B3, ETF americano via Inter, ETF americano "
                 f"via IBKR e **UCITS irlandês via IBKR** (CSPX/VWRA). *Escala logarítmica:* em horizontes "
                 f"longos ela revela diferenças que a escala linear achata — mas a tabela embaixo de cada "
                 f"gráfico traz os números, já que as curvas ficam quase coladas."),
            ChartRef("wealth_sp500"), ChartRef("wealth_mundo")]),

        Section("2. Para onde vai o dinheiro: decomposição de custos", [
            Para(f"Partindo do \"teto bruto\" (índice × dólar sem nenhum custo), quanto cada fricção retira "
                 f"até o resgate. No caminho de fora, os dois maiores vilões de longo prazo são a **retenção "
                 f"de dividendos** ({n.ret_div_brl} neste exemplo) e o **IR na venda** ({n.ir_brl}); o custo "
                 f"de **câmbio** (spread + IOF, ida e volta) soma {n.cambio_brl} — relevante, mas menor do "
                 f"que muita gente imagina ao diluir num horizonte longo."),
            ChartRef("waterfall")]),

        Section("3. Break-even: quando vale a pena \"dolarizar\"?", [
            Para("Comprar lá fora paga um pedágio de entrada (spread + IOF). A taxa de administração menor "
                 "do VOO (0,03% vs 0,23% do IVVB11) tenta recuperar isso com o tempo — mas a retenção de 30% "
                 "sobre dividendos trabalha contra. O painel de baixo mostra a vantagem líquida do caminho de "
                 "fora; perto de zero = empate técnico."),
            ChartRef("breakeven")]),

        Section("4. Aportes mensais (DCA): o pedágio que se repete", [
            Para(f"Quem aporta {n.mensal} por mês paga o spread + IOF **a cada remessa** no caminho de fora — "
                 f"enquanto na B3 não há câmbio explícito. Para tarifas fixas (Wise), aportes pequenos doem mais."),
            ChartRef("dca_sp500"), ChartRef("dca_mundo")]),

        Section("5. O tamanho do capital importa", [
            Para("Custos percentuais (spread, IOF, taxa adm, IR) são iguais para qualquer valor — então o "
                 "CAGR não muda com o tamanho. O que muda: **tarifas fixas** (Wise) pesam mais em capital "
                 "pequeno, e a **faixa de relacionamento** do Inter melhora o spread (Digital 1,5% → WIN "
                 "0,99% acima de R$1M)."),
            ChartRef("sensibilidade")]),

        Section("6. De onde vem o retorno: ação × dólar", [
            Para("O retorno em reais é o produto de duas forças: a valorização da bolsa (em dólar) e a "
                 "valorização do dólar frente ao real. **Ambos os caminhos capturam as duas** — por isso "
                 "\"dolarizar\" não dá um retorno cambial extra frente a um IVVB11. A desvalorização "
                 "estrutural do real aparece na linha vermelha."),
            ChartRef("cambio")]),

        Section("7. Validação: o modelo reconstrói os ETFs reais?", [
            Para("Os ETFs da B3 são jovens (IVVB11 ~2014, WRLD11/ACWI11 ~2021), então as curvas de longo "
                 "prazo são **reconstruções sintéticas** (índice × dólar × custos). Aqui comparamos a "
                 "reconstrução com a cotação real onde ela existe — o **gap de CAGR** pequeno valida o "
                 "modelo. O tracking error é medido em base **mensal** de propósito (pregões B3 × EUA criam "
                 "ruído diário espúrio)."),
            ChartRef("validacao"), TableRef("valid")]),

        Section("8. Resumo numérico", [
            H3(f"Aporte único de {n.a0}"), TableRef("lump"),
            H3(f"Aportes mensais de {n.mensal}"), TableRef("dca")]),

        Section("9. O que os números não mostram (mas importa muito)", [
            Box("alerta",
                "**Imposto sucessório dos EUA (estate tax).** Ativos \"US-situs\" (ações e ETFs listados nos "
                "EUA, como VOO/VT) acima de **US$ 60 mil** são tributados em até **40%** no falecimento de um "
                "não-residente. ETFs da B3 e ETFs domiciliados na Irlanda (UCITS — ex.: CSPX/VWRA comprados na IBKR) "
                "**não** têm essa exposição. É o maior risco qualitativo do caminho \"comprar US-domiciliado "
                "direto\" (VOO/VT) para patrimônios maiores — e um motivo a mais para preferir o UCITS irlandês."),
            Bullets([
                "**Retenção de dividendos (sem tratado BR–EUA):** ETF US-domiciliado retém **30%** dos "
                "dividendos; o W-8BEN não reduz (não há tratado). ETF irlandês (UCITS) retém **15%**. ETFs B3 "
                "que embrulham fundos US-domiciliados (IVVB11→IVV, WRLD11→VT) também sofrem os 30% "
                "internamente; só os de *wrap* irlandês (VWRA11) escapam para 15%. Comprar o **UCITS irlandês "
                "direto na IBKR** (CSPX no S&P 500, VWRA no global) dá esses 15% **sem** a camada extra de taxa "
                "do wrapper brasileiro — por isso o CSPX vence no S&P 500, onde não há equivalente irlandês na B3.",
                f"**Tributação brasileira.** ETF de renda variável na B3: ganho de capital a **{n.aliq_etf}** "
                f"(sensibilidade {n.aliq_etf_sens}), **sem** a isenção de R$20 mil das ações e sem come-cotas; "
                f"DARF auto-recolhido. Investimento direto no exterior: a Lei 14.754/2023 tributa o ganho (em "
                f"reais, incluindo variação cambial) a **15%** no ajuste anual, e dividendos a 15% (com crédito "
                f"do imposto pago nos EUA, limitado — o excesso de 30% é perdido).",
                "**Burocracia.** Investir fora exige declarar no IRPF (bens e direitos no exterior), apurar "
                "ganho de capital e, acima de US$1 mi, a **CBE** ao Banco Central. ETF na B3 cabe no informe "
                "da corretora.",
                "**Complexidade operacional e câmbio de volta.** Trazer o dinheiro de volta tem novo spread + "
                "IOF (0,38% na volta). O caminho B3 é \"um clique\".",
            ])]),

        Section(None, [Box("disclaimer",
            "**Metodologia.** Simulação determinística (não é recomendação de compra/venda nem estratégia de "
            "trading). Subjacentes: SPY (S&P 500, desde 2004) e VT (mundo, desde 2008) como proxies de retorno "
            "total; câmbio USD/BRL via `BRL=X`. Curvas de ETFs B3 são reconstruções sintéticas validadas contra "
            "a cotação real (seção 7). Premissas de taxas, spreads, IOF e tributos (jun/2026) estão em "
            "`config/base.yaml` e `SPEC.md` com fontes. **IOF e a alíquota de ETF mudaram várias vezes em "
            "2025–2026 e podem mudar de novo** — confirme com um contador antes de decidir. Fonte de preços: "
            "Yahoo Finance (yfinance), uso pessoal/educacional.")]),
    ]
