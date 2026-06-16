"""Tabela de apoio que acompanha cada gráfico (valores + resultado final).

Compartilhada pelos dois relatórios: no Markdown as curvas estáticas ficam coladas
e no HTML evita ter que "passar o mouse" para ver o valor final. Devolve
``(legenda, headers, rows)`` em strings já formatadas.
"""

from __future__ import annotations

import pandas as pd

from . import chartdata as C
from .util import brl


def _checkpoints(n: int, k: int = 6) -> list[int]:
    if n <= k:
        return list(range(n))
    return sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})


def _datestr(x) -> str:
    return pd.Timestamp(x).strftime("%Y-%m")


def _is_constant(y) -> bool:
    lo, hi = float(min(y)), float(max(y))
    return hi - lo <= 1e-6 * max(1.0, abs(hi))


def _fmt(v, money: bool) -> str:
    return brl(float(v)) if money else f"{float(v):.3f}"


def table_for(chart) -> tuple[str, list[str], list[list[str]]] | None:
    if isinstance(chart, C.LineChart):
        lines = [ln for ln in chart.lines if not _is_constant(ln.y)]
        if not lines:
            return None
        n = min(len(ln.x) for ln in lines)
        ref_x = lines[0].x
        headers = ["Data"] + [ln.short or ln.label for ln in lines]
        rows = [[_datestr(ref_x[i])] + [_fmt(ln.y[i], chart.money) for ln in lines]
                for i in _checkpoints(n)]
        return "*Valores ao longo do tempo (última linha = resultado final):*", headers, rows

    if isinstance(chart, C.BreakevenChart):
        n = min(len(chart.br.x), len(chart.us.x), len(chart.diff_y))
        headers = ["Data", chart.br.short or chart.br.label, chart.us.short or chart.us.label, "Vantagem US−BR"]
        rows = [[_datestr(chart.br.x[i]), brl(float(chart.br.y[i])), brl(float(chart.us.y[i])),
                 f"{float(chart.diff_y[i]):+.2f}%"] for i in _checkpoints(n)]
        return "*Valores ao longo do tempo (última linha = resultado final):*", headers, rows

    if isinstance(chart, C.WaterfallChart):
        headers = ["Componente"] + chart.categories
        rows = [[label] + [brl(float(v)) for v in vals] for label, _cor, vals in chart.components]
        rows.append(["**Custo total**"] + [brl(float(t)) for t in chart.totals])
        return "*Custo por componente (BRL no horizonte):*", headers, rows

    if isinstance(chart, C.SensitivityChart):
        headers = ["Capital"] + [ln.short or ln.label for ln in chart.lines]
        rows = [[size] + [f"{float(ln.y[j]):.2f}%" for ln in chart.lines]
                for j, size in enumerate(chart.xticklabels)]
        return "*CAGR líquido (% a.a.) por tamanho de capital:*", headers, rows

    if isinstance(chart, C.ValidationChart):
        headers = ["Painel", "Sintético (fim, base 1,0)", "Real (fim, base 1,0)"]
        rows = [[nome, f"{float(syn[-1]):.3f}", f"{float(real[-1]):.3f}"]
                for nome, _x, syn, real in chart.panels]
        return "*Valor final normalizado (base 1,0):*", headers, rows

    return None
