"""Renderers Plotly → fragmentos HTML interativos (para o relatório HTML).

plotly.js entra via CDN (incluído uma única vez, no primeiro gráfico). Escala
log nas curvas de crescimento; legenda interativa (clique para ocultar séries),
fonte IBM Plex Sans.
"""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from . import chartdata as C

FONT = "IBM Plex Sans, -apple-system, Segoe UI, Roboto, sans-serif"
_CONFIG = {"displaylogo": False, "responsive": True,
           "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"]}


def _to_html(fig: go.Figure, include_js: bool) -> str:
    return pio.to_html(fig, include_plotlyjs=("cdn" if include_js else False),
                       full_html=False, config=_CONFIG, default_height="460px")


def _base_layout(fig: go.Figure, title: str, ylabel: str, *, log_y: bool, money: bool,
                 legend_bottom: bool = True) -> None:
    fig.update_layout(
        title=dict(text=title, font=dict(size=15)),
        template="plotly_white",
        font=dict(family=FONT, size=12),
        margin=dict(l=70, r=30, t=55, b=70),
        hovermode="x unified",
        legend=(dict(orientation="h", yanchor="top", y=-0.16, x=0) if legend_bottom
                else dict(yanchor="top", y=1, x=1.02)),
    )
    fig.update_yaxes(title_text=ylabel, type=("log" if log_y else "linear"))
    if money:
        fig.update_yaxes(tickprefix="R$ ", tickformat=",.0f")


def render(chart, include_js: bool = False) -> str:
    if isinstance(chart, C.LineChart):
        return _line(chart, include_js)
    if isinstance(chart, C.WaterfallChart):
        return _waterfall(chart, include_js)
    if isinstance(chart, C.BreakevenChart):
        return _breakeven(chart, include_js)
    if isinstance(chart, C.SensitivityChart):
        return _sensitivity(chart, include_js)
    if isinstance(chart, C.ValidationChart):
        return _validation(chart, include_js)
    raise TypeError(f"tipo de chart desconhecido: {type(chart)}")


def _line(c: C.LineChart, include_js: bool) -> str:
    fig = go.Figure()
    hov = "%{y:,.0f}" if c.money else "%{y:.3f}"
    for ln in c.lines:
        fig.add_trace(go.Scatter(
            x=list(ln.x), y=list(ln.y), name=ln.label, mode="lines",
            line=dict(color=ln.color, width=1.1 if ln.dash else 2.0, dash="dot" if ln.dash else "solid"),
            hovertemplate=f"{ln.label}: {hov}<extra></extra>",
        ))
    _base_layout(fig, c.title, c.ylabel, log_y=c.log_y, money=c.money)
    return _to_html(fig, include_js)


def _waterfall(c: C.WaterfallChart, include_js: bool) -> str:
    fig = go.Figure()
    for label, cor, vals in c.components:
        fig.add_trace(go.Bar(x=c.categories, y=vals, name=label, marker_color=cor,
                             hovertemplate=f"{label}: R$ %{{y:,.0f}}<extra></extra>"))
    fig.update_layout(barmode="stack")
    for cat, total in zip(c.categories, c.totals):
        fig.add_annotation(x=cat, y=total, text=f"R$ {total:,.0f}".replace(",", "."),
                           showarrow=False, yshift=10, font=dict(size=11))
    _base_layout(fig, c.title, c.ylabel, log_y=False, money=True)
    return _to_html(fig, include_js)


def _breakeven(c: C.BreakevenChart, include_js: bool) -> str:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.66, 0.34],
                        vertical_spacing=0.06)
    for ln in (c.br, c.us):
        fig.add_trace(go.Scatter(x=list(ln.x), y=list(ln.y), name=ln.label, mode="lines",
                                 line=dict(color=ln.color, width=2.0),
                                 hovertemplate=f"{ln.label}: R$ %{{y:,.0f}}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=list(c.diff_x), y=list(c.diff_y), name="Vantagem US−BR (%)",
                             mode="lines", line=dict(color="black", width=1.2), fill="tozeroy",
                             fillcolor="rgba(57,73,171,0.18)",
                             hovertemplate="US−BR: %{y:+.2f}%<extra></extra>"), row=2, col=1)
    fig.update_yaxes(title_text=c.ylabel, type="log", tickprefix="R$ ", tickformat=",.0f", row=1, col=1)
    fig.update_yaxes(title_text="US−BR (% aporte)", row=2, col=1)
    fig.update_layout(title=dict(text=c.title, font=dict(size=15)), template="plotly_white",
                      font=dict(family=FONT, size=12), margin=dict(l=70, r=30, t=55, b=50),
                      legend=dict(orientation="h", yanchor="top", y=-0.08, x=0), hovermode="x unified")
    return _to_html(fig, include_js)


def _sensitivity(c: C.SensitivityChart, include_js: bool) -> str:
    fig = go.Figure()
    for ln in c.lines:
        fig.add_trace(go.Scatter(x=c.xticklabels, y=list(ln.y), name=ln.label, mode="lines+markers",
                                 line=dict(color=ln.color, width=2.0),
                                 hovertemplate=f"{ln.label}: %{{y:.2f}}%<extra></extra>"))
    _base_layout(fig, c.title, c.ylabel, log_y=False, money=False)
    fig.update_xaxes(title_text=c.xlabel)
    return _to_html(fig, include_js)


def _validation(c: C.ValidationChart, include_js: bool) -> str:
    n = max(1, len(c.panels))
    fig = make_subplots(rows=1, cols=n, subplot_titles=[p[0] for p in c.panels], horizontal_spacing=0.07)
    for i, (_nome, x, syn, real) in enumerate(c.panels, start=1):
        showleg = i == 1
        fig.add_trace(go.Scatter(x=list(x), y=syn, name="sintético", legendgroup="s",
                                 showlegend=showleg, line=dict(color="#3949ab", width=1.5),
                                 hovertemplate="sintético: %{y:.3f}<extra></extra>"), row=1, col=i)
        fig.add_trace(go.Scatter(x=list(x), y=real, name="real (B3)", legendgroup="r",
                                 showlegend=showleg, line=dict(color="#d32f2f", width=1.2),
                                 hovertemplate="real: %{y:.3f}<extra></extra>"), row=1, col=i)
        fig.update_yaxes(type="log", row=1, col=i)
    fig.update_layout(title=dict(text=c.title, font=dict(size=15)), template="plotly_white",
                      font=dict(family=FONT, size=12), margin=dict(l=50, r=20, t=70, b=40),
                      legend=dict(orientation="h", yanchor="top", y=-0.12, x=0), hovermode="x unified")
    return _to_html(fig, include_js)
