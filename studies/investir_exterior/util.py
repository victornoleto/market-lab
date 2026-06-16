"""Helpers de formatação e tabelas, compartilhados pelos dois renderers."""

from __future__ import annotations

import re


def pct(x: float) -> str:
    return "—" if x != x else f"{x*100:.2f}%"


def brl(x: float) -> str:
    return f"R$ {x:,.0f}".replace(",", ".")


def brl_short(x: float) -> str:
    """Formato curto para eixos: R$1.2M / R$120k / R$500."""
    if abs(x) >= 1_000_000:
        return f"R${x/1e6:.1f}M"
    if abs(x) >= 1_000:
        return f"R${x/1e3:.0f}k"
    return f"R${x:.0f}"


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Tabela GFM. Alinha as duas primeiras colunas à esquerda, o resto à direita."""
    if not rows:
        return "_sem linhas._\n"
    aligns = [":---" if i < 2 else "---:" for i in range(len(headers))]
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(aligns) + " |"
    body = ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join([head, sep, *body]) + "\n"


_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_CODE = re.compile(r"`(.+?)`")


def md_inline_to_html(s: str) -> str:
    """Converte ênfase markdown inline para HTML (**negrito**, *itálico*, `código`)."""
    s = _CODE.sub(r"<code>\1</code>", s)
    s = _BOLD.sub(r"<b>\1</b>", s)
    s = _ITALIC.sub(r"<i>\1</i>", s)
    return s
