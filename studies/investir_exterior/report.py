"""Orquestrador dos relatórios: monta o contexto (números, tabelas, gráficos)
uma única vez e delega o render para report_html (interativo) e report_md (PNGs).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from . import chartdata, config as cfg, report_html, report_md, simulate as S
from .data import Bundle
from .util import brl, pct


@dataclass
class Context:
    numbers: dict[str, Any]
    tables: dict[str, tuple[list[str], list[list[str]]]]
    charts: dict[str, Any]


def _find(runs: list[S.RunSpec], cenario: str, inst: str) -> S.RunSpec:
    return next(r for r in runs if r.cenario_key == cenario and r.instrumento == inst)


def build_context(config: dict[str, Any], bundle: Bundle, today: date) -> Context:
    runs = S.build_runs(config)
    A0 = float(config["aportes"]["inicial_brl"])
    mensal = float(config["aportes"]["mensal_brl"])
    sizes = [float(s) for s in config["aportes"]["sensibilidade_brl"]]
    tributos = config["tributos"]
    sp, mundo = bundle.exposicoes["sp500"], bundle.exposicoes["mundo"]
    yrs_sp, yrs_m = S.years_of(sp), S.years_of(mundo)

    sp_specs = [_find(runs, "brasil", "IVVB11"), _find(runs, "inter", "VOO"),
                _find(runs, "ibkr", "VOO"), _find(runs, "ibkr_ucits", "CSPX")]
    mundo_specs = [_find(runs, "brasil", "WRLD11"), _find(runs, "brasil", "VWRA11"),
                   _find(runs, "inter", "VT"), _find(runs, "ibkr", "VT"), _find(runs, "ibkr_ucits", "VWRA")]

    decomps = [
        ("BR — IVVB11", S.cost_decomposition(sp, sp_specs[0].inst_cfg, "br", None, A0, config)),
        ("Inter — VOO", S.cost_decomposition(sp, sp_specs[1].inst_cfg, "us", sp_specs[1].canal, A0, config)),
        ("IBKR — VOO", S.cost_decomposition(sp, sp_specs[2].inst_cfg, "us", sp_specs[2].canal, A0, config)),
    ]

    charts = {
        "wealth_sp500": chartdata.wealth(sp, sp_specs, config, A0, "wealth_sp500",
                                         f"Patrimônio líquido — aporte único de {brl(A0)} (S&P 500, {yrs_sp:.0f} anos)"),
        "wealth_mundo": chartdata.wealth(mundo, mundo_specs, config, A0, "wealth_mundo",
                                         f"Patrimônio líquido — aporte único de {brl(A0)} (mundo, {yrs_m:.0f} anos)"),
        "waterfall": chartdata.waterfall(decomps),
        "breakeven": chartdata.breakeven(sp, sp_specs[0], sp_specs[1], config, A0),
        "dca_sp500": chartdata.dca(sp, sp_specs, config, mensal, "dca_sp500",
                                   f"Aportes mensais de {brl(mensal)} (S&P 500) — valor de mercado"),
        "dca_mundo": chartdata.dca(mundo, mundo_specs, config, mensal, "dca_mundo",
                                   f"Aportes mensais de {brl(mensal)} (mundo) — valor de mercado"),
        "sensibilidade": chartdata.sensitivity(sp, config, sizes),
        "cambio": chartdata.currency(bundle, config),
        "validacao": chartdata.validation(bundle, config),
    }

    # tabelas
    lump_rows = []
    for r in runs:
        expo = bundle.exposicoes[r.expo_nome]
        yrs = S.years_of(expo)
        dec = S.cost_decomposition(expo, r.inst_cfg, r.path, r.canal, A0, config)
        fin = dec["liquido"]
        lump_rows.append([r.cenario_rotulo, r.instrumento, r.expo_nome, f"{yrs:.0f}",
                          pct(S.cagr(fin, A0, yrs)), brl(fin), pct(1.0 - fin / dec["bruto"])])
    dca_rows = []
    for r in runs:
        expo = bundle.exposicoes[r.expo_nome]
        res = S.dca_result(expo, r.inst_cfg, r.path, r.canal, mensal, config)
        dca_rows.append([r.cenario_rotulo, r.instrumento, brl(res.total_investido), brl(res.final_liquido),
                         f"{res.final_liquido/res.total_investido:.2f}x", pct(res.irr_anual)])
    valid_rows = []
    for nome in ["IVVB11", "WRLD11", "ACWI11"]:
        inst = config["instrumentos"][nome]
        expo = bundle.exposicoes[inst["exposicao"]]
        syn = S.net_usd_index(expo, inst, tributos) * expo.fx
        real = bundle.reais.get(nome)
        if real is None or real.empty:
            continue
        cs, cr, gap = S.cagr_gap(syn, real)
        valid_rows.append([nome, f"{real.index[0].date()} → {real.index[-1].date()}",
                           pct(cs), pct(cr), f"{gap*100:+.2f} pp", pct(S.tracking_error_annual(syn, real))])

    tables = {
        "lump": (["Cenário", "Ativo", "Exposição", "Anos", "CAGR líq.", "Patrimônio final", "Custo total"], lump_rows),
        "dca": (["Cenário", "Ativo", "Aportado", "Final líq.", "Múltiplo", "TIR a.a."], dca_rows),
        "valid": (["ETF", "Período real", "CAGR sintético", "CAGR real", "Gap", "TE mensal (a.a.)"], valid_rows),
    }

    def fin_cagr(cen, inst):
        r = _find(runs, cen, inst)
        e = bundle.exposicoes[r.expo_nome]
        return S.cagr(float(S.lump_curve(e, r.inst_cfg, r.path, r.canal, A0, config).iloc[-1]), A0, S.years_of(e))

    numbers = {
        "data_hoje": today.isoformat(),
        "fim_dado": max(sp.index[-1], mundo.index[-1]).date().isoformat(),
        "yrs_sp": f"{yrs_sp:.0f}", "yrs_m": f"{yrs_m:.0f}", "a0": brl(A0), "mensal": brl(mensal),
        "cagr_ivvb": pct(fin_cagr("brasil", "IVVB11")), "cagr_voo_inter": pct(fin_cagr("inter", "VOO")),
        "cagr_voo_ibkr": pct(fin_cagr("ibkr", "VOO")), "cagr_vwra": pct(fin_cagr("brasil", "VWRA11")),
        "cagr_vt_inter": pct(fin_cagr("inter", "VT")),
        "cagr_cspx": pct(fin_cagr("ibkr_ucits", "CSPX")), "cagr_vwra_irish": pct(fin_cagr("ibkr_ucits", "VWRA")),
        "ret_div_brl": brl(decomps[1][1]["retencao_dividendos"]), "ir_brl": brl(decomps[1][1]["ir_venda"]),
        "cambio_brl": brl(decomps[1][1]["cambio_entrada"] + decomps[1][1]["cambio_saida"]),
        "aliq_etf": f"{tributos['etf_b3_ganho_capital']*100:.1f}%",
        "aliq_etf_sens": f"{tributos['etf_b3_ganho_capital_sensibilidade']*100:.1f}%",
    }
    return Context(numbers, tables, charts)


def generate_all(config: dict[str, Any], bundle: Bundle, today: date,
                 out_dir: Path | None = None, formats: Iterable[str] = ("html", "md")) -> dict[str, Path]:
    out_dir = out_dir or cfg.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx = build_context(config, bundle, today)
    formats = set(formats)
    out: dict[str, Path] = {}
    if "html" in formats:
        path = out_dir / "relatorio.html"
        path.write_text(report_html.render(ctx), encoding="utf-8")
        out["html"] = path
    if "md" in formats:
        path = out_dir / "relatorio.md"
        path.write_text(report_md.render(ctx, out_dir / "plots"), encoding="utf-8")
        out["md"] = path
    return out
