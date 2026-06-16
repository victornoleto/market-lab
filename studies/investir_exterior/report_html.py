"""Renderiza o relatório HTML interativo (Plotly via CDN + Google Fonts IBM Plex Sans).

Caminha a mesma lista de seções/blocos de content.py do markdown — só muda o render.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import content, plots_plotly
from .chart_tables import table_for
from .content import Box, Bullets, ChartRef, H3, Para, TableRef
from .util import md_inline_to_html

if TYPE_CHECKING:
    from .report import Context

_BOX_CLASS = {"tldr": "box tldr", "alerta": "box alerta", "disclaimer": "disclaimer"}

_HEAD = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Investir no exterior: Brasil vs. Dólar</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root { --verde:#1b7837; --azul:#3949ab; --laranja:#fb8c00; }
  body { font-family:'IBM Plex Sans', -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         max-width: 960px; margin: 0 auto; padding: 24px 18px 80px; color:#1a1a1a; line-height:1.6; }
  h1 { font-size: 2rem; font-weight:700; line-height:1.2; margin-bottom:4px; }
  h2 { font-size: 1.4rem; font-weight:600; margin-top: 2.2em; border-bottom: 2px solid #eee; padding-bottom:4px; }
  h3 { font-size: 1.1rem; font-weight:600; margin-top:1.6em; }
  .sub { color:#666; font-size:.92rem; margin-top:0; }
  .chart { margin: 16px 0; }
  table { border-collapse: collapse; width:100%; font-size:.86rem; margin:14px 0; }
  th, td { border:1px solid #e2e2e2; padding:6px 9px; text-align:right; }
  th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align:left; }
  thead th { background:#f5f7fa; font-weight:600; }
  .box { background:#f5f7fa; border-left:4px solid var(--azul); padding:12px 16px; border-radius:4px; margin:16px 0; }
  .alerta { background:#fff7e6; border-left-color:var(--laranja); }
  .tldr { background:#eafaef; border-left-color:var(--verde); }
  .disclaimer { color:#777; font-size:.82rem; border-top:1px solid #eee; margin-top:40px; padding-top:14px; }
  code { background:#f0f0f0; padding:1px 4px; border-radius:3px; font-size:.92em; }
  ul { padding-left:1.2em; }
  li { margin: 6px 0; }
  .cap { color:#666; font-size:.82rem; margin:4px 0 2px; }
  .chart table { font-size:.82rem; }
  td.nowrap { white-space: nowrap; }
</style></head><body>
"""


def _table(headers: list[str], rows: list[list[str]]) -> str:
    nowrap = {j for j, h in enumerate(headers) if h == "Data"}
    th = "".join(f"<th>{md_inline_to_html(str(h))}</th>" for h in headers)
    body = []
    for row in rows:
        tds = "".join(
            f'<td class="nowrap">{md_inline_to_html(str(c))}</td>' if j in nowrap
            else f"<td>{md_inline_to_html(str(c))}</td>"
            for j, c in enumerate(row)
        )
        body.append(f"<tr>{tds}</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def render(ctx: "Context") -> str:
    parts: list[str] = [_HEAD]
    parts.append(f"<h1>{content.TITLE}</h1>")
    parts.append(f'<p class="sub">{content.subtitle(ctx.numbers)}</p>')

    js_injected = False
    for sec in content.build_layout(ctx.numbers):
        if sec.title:
            parts.append(f"<h2>{sec.title}</h2>")
        for b in sec.blocks:
            if isinstance(b, Para):
                parts.append(f"<p>{md_inline_to_html(b.text)}</p>")
            elif isinstance(b, H3):
                parts.append(f"<h3>{b.text}</h3>")
            elif isinstance(b, Bullets):
                lis = "".join(f"<li>{md_inline_to_html(i)}</li>" for i in b.items)
                parts.append(f"<ul>{lis}</ul>")
            elif isinstance(b, Box):
                parts.append(f'<div class="{_BOX_CLASS[b.kind]}">{md_inline_to_html(b.text)}</div>')
            elif isinstance(b, ChartRef):
                div = plots_plotly.render(ctx.charts[b.key], include_js=not js_injected)
                js_injected = True
                parts.append(f'<div class="chart">{div}</div>')
                tbl = table_for(ctx.charts[b.key])
                if tbl:
                    caption, headers, rows = tbl
                    parts.append(f'<p class="cap">{md_inline_to_html(caption)}</p>')
                    parts.append(_table(headers, rows))
            elif isinstance(b, TableRef):
                headers, rows = ctx.tables[b.key]
                parts.append(_table(headers, rows))
    parts.append("</body></html>")
    return "\n".join(parts)
