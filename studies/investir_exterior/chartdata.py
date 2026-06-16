"""Preparação de dados dos gráficos (pura — não renderiza nada).

Cada função devolve um dataclass que os dois renderers (matplotlib PNG e Plotly)
consomem. Assim a simulação roda uma vez e a prosa/lógica não se duplica.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from . import simulate as S
from .costs import Canal
from .data import Bundle, Exposicao


def _weekly(s: pd.Series) -> pd.Series:
    """Reamostra para semanal (mantém o último ponto real) — corta o tamanho do
    HTML interativo ~5× sem mudança visual perceptível em curvas de anos."""
    w = s.resample("W-FRI").last().dropna()
    if len(s) and (len(w) == 0 or w.index[-1] != s.index[-1]):
        w = pd.concat([w, s.iloc[[-1]]])
    return w

# Paleta consistente por "família" de cenário
COR_BR = "#1b7837"      # verde  (Brasil)
COR_INTER = "#fb8c00"   # laranja (Inter)
COR_IBKR = "#3949ab"    # azul   (IBKR — ETF US)
COR_UCITS = "#8e24aa"   # roxo   (IBKR — UCITS irlandês)
COR_BR2 = "#43a047"     # verde claro (segundo ativo Brasil — VWRA11)
COR_REF = "#9e9e9e"     # cinza  (referência)
CORES_CENARIO = {"brasil": COR_BR, "inter": COR_INTER, "ibkr": COR_IBKR, "ibkr_ucits": COR_UCITS}


@dataclass
class Line:
    label: str                  # rótulo longo (legenda do gráfico)
    x: Any
    y: Any
    color: str | None = None
    dash: bool = False          # linha de referência pontilhada
    short: str | None = None    # rótulo curto (cabeçalho da tabela); cai p/ label se None


# Prefixo curto por cenário (cabeçalhos de tabela)
PREFIXO = {"brasil": "BR", "inter": "Inter", "ibkr": "IBKR", "ibkr_ucits": "IBKR"}


def _short(sp: "S.RunSpec") -> str:
    return f"{PREFIXO.get(sp.cenario_key, sp.cenario_key)} — {sp.instrumento}"


@dataclass
class LineChart:
    key: str
    title: str
    ylabel: str
    lines: list[Line]
    log_y: bool = False
    money: bool = True          # eixo/hover em BRL


@dataclass
class WaterfallChart:
    key: str
    title: str
    ylabel: str
    categories: list[str]
    components: list[tuple[str, str, list[float]]]   # (rótulo, cor, valor por categoria)
    totals: list[float]


@dataclass
class SensitivityChart:
    key: str
    title: str
    ylabel: str
    xlabel: str
    xticklabels: list[str]
    lines: list[Line]           # x = posições 0..n-1


@dataclass
class BreakevenChart:
    key: str
    title: str
    ylabel: str
    br: Line
    us: Line
    diff_x: Any
    diff_y: list[float]         # vantagem US-BR em % do aporte
    us_color: str


@dataclass
class ValidationChart:
    key: str
    title: str
    panels: list[tuple[str, Any, list[float], list[float]]]  # (nome, x, sint_norm, real_norm)


# --------------------------------------------------------------------------- #
def _spec_color(sp: S.RunSpec, second_br: bool = False) -> str:
    if sp.cenario_key == "brasil" and second_br:
        return COR_BR2
    return CORES_CENARIO.get(sp.cenario_key, COR_REF)


def wealth(expo: Exposicao, specs: list[S.RunSpec], config: dict[str, Any], a0: float,
           key: str, titulo: str) -> LineChart:
    lines: list[Line] = []
    seen_br = False
    for sp in specs:
        curve = _weekly(S.lump_curve(expo, sp.inst_cfg, sp.path, sp.canal, a0, config))
        second = sp.cenario_key == "brasil" and seen_br
        if sp.cenario_key == "brasil":
            seen_br = True
        lines.append(Line(f"{sp.cenario_rotulo} · {sp.instrumento}", curve.index, curve.to_numpy(),
                          color=_spec_color(sp, second), short=_short(sp)))
        ref_idx = curve.index
    lines.append(Line("aporte inicial", ref_idx, np.full(len(ref_idx), a0), color=COR_REF, dash=True))
    return LineChart(key, titulo, "Patrimônio líquido (BRL)", lines, log_y=True)


def dca(expo: Exposicao, specs: list[S.RunSpec], config: dict[str, Any], mensal: float,
        key: str, titulo: str) -> LineChart:
    lines: list[Line] = []
    invested_done = False
    seen_br = False
    for sp in specs:
        res = S.dca_result(expo, sp.inst_cfg, sp.path, sp.canal, mensal, config)
        if not invested_done:
            inv = _weekly(res.investido)
            lines.append(Line("total aportado", inv.index, inv.to_numpy(), color=COR_REF, dash=True,
                             short="Aportado"))
            invested_done = True
        second = sp.cenario_key == "brasil" and seen_br
        if sp.cenario_key == "brasil":
            seen_br = True
        val = _weekly(res.valor_mercado)
        lines.append(Line(f"{sp.cenario_rotulo} · {sp.instrumento}", val.index, val.to_numpy(),
                          color=_spec_color(sp, second), short=_short(sp)))
    return LineChart(key, titulo, "Valor de mercado (BRL)", lines, log_y=True)


def waterfall(decomps: list[tuple[str, dict[str, float]]]) -> WaterfallChart:
    labels = ["taxa_adm", "retencao_dividendos", "cambio_entrada", "cambio_saida", "ir_venda"]
    nomes = {
        "taxa_adm": "Taxa adm.",
        "retencao_dividendos": "Retenção dividendos",
        "cambio_entrada": "Câmbio entrada (spread+IOF)",
        "cambio_saida": "Câmbio saída (spread+IOF)",
        "ir_venda": "IR na venda",
    }
    cores = {"taxa_adm": "#8d6e63", "retencao_dividendos": "#d32f2f", "cambio_entrada": "#fb8c00",
             "cambio_saida": "#ffb74d", "ir_venda": "#5e35b1"}
    categories = [nm for nm, _ in decomps]
    components = [(nomes[lab], cores[lab], [d[lab] for _, d in decomps]) for lab in labels]
    totals = [sum(d[lab] for lab in labels) for _, d in decomps]
    return WaterfallChart("waterfall", "Decomposição de custos sobre o teto bruto (S&P 500)",
                          "Custo acumulado no horizonte (BRL)", categories, components, totals)


def breakeven(expo: Exposicao, br_spec: S.RunSpec, us_spec: S.RunSpec,
              config: dict[str, Any], a0: float) -> BreakevenChart:
    br = _weekly(S.lump_curve(expo, br_spec.inst_cfg, "br", None, a0, config))
    us = _weekly(S.lump_curve(expo, us_spec.inst_cfg, "us", us_spec.canal, a0, config))
    diff = ((us - br) / a0 * 100.0)
    return BreakevenChart(
        "breakeven", "Break-even — liquidando tudo a cada data (S&P 500)", "Patrimônio líquido (BRL)",
        Line(f"Brasil · {br_spec.instrumento}", br.index, br.to_numpy(), color=COR_BR,
             short=f"BR — {br_spec.instrumento}"),
        Line(f"{us_spec.cenario_rotulo} · {us_spec.instrumento}", us.index, us.to_numpy(),
             color=CORES_CENARIO.get(us_spec.cenario_key, COR_REF), short=_short(us_spec)),
        diff.index, diff.to_numpy().tolist(), CORES_CENARIO.get(us_spec.cenario_key, COR_REF),
    )


def sensitivity(expo: Exposicao, config: dict[str, Any], sizes: list[float]) -> SensitivityChart:
    canais = config["canais_cambio"]
    instrumentos = config["instrumentos"]
    yrs = S.years_of(expo)

    def cagr_for(inst_name: str, path: str, canal_cfg) -> list[float]:
        out = []
        for a0 in sizes:
            canal = Canal.from_cfg(canal_cfg) if canal_cfg else None
            fin = float(S.lump_curve(expo, instrumentos[inst_name], path, canal, a0, config).iloc[-1])
            out.append(S.cagr(fin, a0, yrs) * 100.0)
        return out

    inter_vals = []
    for a0 in sizes:
        canal_cfg = canais["inter_win"] if a0 >= 1_000_000 else canais["inter_digital"]
        fin = float(S.lump_curve(expo, instrumentos["VOO"], "us", Canal.from_cfg(canal_cfg), a0, config).iloc[-1])
        inter_vals.append(S.cagr(fin, a0, yrs) * 100.0)

    x = list(range(len(sizes)))
    lines = [
        Line("Brasil · IVVB11", x, cagr_for("IVVB11", "br", None), color=COR_BR, short="BR — IVVB11"),
        Line("Inter · VOO (faixa por capital)", x, inter_vals, color=COR_INTER, short="Inter — VOO"),
        Line("IBKR/Transfer Bank · VOO", x, cagr_for("VOO", "us", canais["transfer_bank"]), color=COR_IBKR, short="IBKR — VOO"),
        Line("Wise · VOO (tarifa fixa)", x, cagr_for("VOO", "us", canais["wise"]), color="#00897b", short="Wise — VOO"),
    ]
    from .util import brl_short
    return SensitivityChart("sensibilidade", "CAGR líquido por tamanho de capital (S&P 500, aporte único)",
                            "CAGR líquido (% a.a.)", "Capital investido",
                            [brl_short(s) for s in sizes], lines)


def currency(bundle: Bundle, config: dict[str, Any]) -> LineChart:
    expo = bundle.exposicoes["sp500"]
    fx = _weekly(expo.fx / float(expo.fx.iloc[0]))
    eq = S.net_usd_index(expo, config["instrumentos"]["VOO"], config["tributos"], apply_er=False, apply_div=False)
    eq = _weekly(eq / float(eq.iloc[0]))
    brl = eq * fx
    return LineChart("cambio", "De onde vem o retorno: ação × dólar (base 1,0)", "Crescimento (base 1,0)", [
        Line("S&P 500 em USD (ação)", eq.index, eq.to_numpy(), color="#3949ab"),
        Line("USD/BRL (dólar)", fx.index, fx.to_numpy(), color="#d32f2f"),
        Line("S&P 500 em BRL (ação × dólar)", brl.index, brl.to_numpy(), color="#1b7837"),
    ], log_y=True, money=False)


def validation(bundle: Bundle, config: dict[str, Any]) -> ValidationChart:
    panels = []
    for nome, expo_nome in [("IVVB11", "sp500"), ("WRLD11", "mundo"), ("ACWI11", "mundo")]:
        inst = config["instrumentos"][nome]
        expo = bundle.exposicoes[expo_nome]
        syn = S.net_usd_index(expo, inst, config["tributos"]) * expo.fx
        real = bundle.reais.get(nome)
        if real is None or real.empty:
            continue
        common = syn.index.intersection(real.index)
        if len(common) < 30:
            continue
        s = _weekly(syn.reindex(common) / float(syn.reindex(common).iloc[0]))
        r = _weekly(real.reindex(common) / float(real.reindex(common).iloc[0]))
        _, _, gap = S.cagr_gap(syn, real)
        panels.append((f"{nome} — gap CAGR {gap*100:+.2f}pp", s.index, s.to_numpy().tolist(), r.to_numpy().tolist()))
    return ValidationChart("validacao", "Validação: série sintética × cotação real do ETF B3 (base 1,0)", panels)
