"""Renderiza o relatório Markdown, com os gráficos como PNGs numa pasta ``plots/``.

Caminha a mesma lista de seções/blocos de content.py do HTML — só muda o render.
Como no markdown os gráficos são estáticos e as curvas ficam muito próximas (até em
escala log), **cada gráfico vem acompanhado de uma tabela** com os valores das curvas
em alguns checkpoints e o resultado final.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from . import content, plots_png
from .chart_tables import table_for
from .content import Box, Bullets, ChartRef, H3, Para, TableRef
from .util import md_table

if TYPE_CHECKING:
    from .report import Context


def render(ctx: "Context", plots_dir: Path) -> str:
    # renderiza todos os PNGs uma vez; guarda o caminho relativo por chave
    png: dict[str, str] = {key: plots_png.render(chart, plots_dir) for key, chart in ctx.charts.items()}

    parts: list[str] = [f"# {content.TITLE}", "", f"*{content.subtitle(ctx.numbers)}*", ""]
    for sec in content.build_layout(ctx.numbers):
        if sec.title:
            parts.append(f"## {sec.title}")
            parts.append("")
        for b in sec.blocks:
            if isinstance(b, Para):
                parts.append(b.text)
                parts.append("")
            elif isinstance(b, H3):
                parts.append(f"### {b.text}")
                parts.append("")
            elif isinstance(b, Bullets):
                parts.extend(f"- {i}" for i in b.items)
                parts.append("")
            elif isinstance(b, Box):
                if b.kind == "disclaimer":
                    parts.append("---")
                    parts.append("")
                parts.append(f"> {b.text}")
                parts.append("")
            elif isinstance(b, ChartRef):
                parts.append(f"![{b.key}]({png[b.key]})")
                parts.append("")
                tbl = table_for(ctx.charts[b.key])
                if tbl:
                    caption, headers, rows = tbl
                    parts.append(caption)
                    parts.append("")
                    parts.append(md_table(headers, rows))
            elif isinstance(b, TableRef):
                headers, rows = ctx.tables[b.key]
                parts.append(md_table(headers, rows))
    return "\n".join(parts).rstrip() + "\n"
