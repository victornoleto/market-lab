"""Núcleo de simulação determinística (não é backtest de alpha).

Para cada (cenário × instrumento) construímos a curva de patrimônio em BRL,
líquida de TODOS os custos, em dois modos:

  * lump-sum  — aporte único em t0, valor de liquidação a cada data t;
  * DCA       — aportes mensais, valor de mercado ao longo do tempo + liquidação no fim.

Caminhos:
  * 'br' — ETF cotado na B3 (BRL). Captura índice×câmbio dentro da cota; sem
           spread de câmbio; taxa adm maior; IR só na venda (15%/17,5%, sem isenção).
  * 'us' — ETF cotado em USD lá fora. Converte BRL->USD na entrada (spread+IOF)
           e USD->BRL na saída; taxa adm mínima; EUA não tributa ganho de NRA;
           Brasil tributa 15% (Lei 14.754) sobre o ganho em BRL (inclui câmbio).

Decomposição de custos = "peeling" cumulativo a partir do teto bruto
(índice×câmbio, sem nenhum custo), idêntico para B3 e US da mesma exposição.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from . import costs
from .costs import Canal
from .data import Exposicao


# ---------------------------------------------------------------------------
# Especificação de cada simulação
# ---------------------------------------------------------------------------
@dataclass
class RunSpec:
    cenario_key: str
    cenario_rotulo: str
    instrumento: str
    inst_cfg: dict[str, Any]
    expo_nome: str          # 'sp500' | 'mundo'
    path: str               # 'br' | 'us'
    canal: Canal | None
    nome_inst: str


def build_runs(config: dict[str, Any]) -> list[RunSpec]:
    canais = config["canais_cambio"]
    instrumentos = config["instrumentos"]
    runs: list[RunSpec] = []
    for ck, cen in config["cenarios"].items():
        canal_key = cen.get("canal")
        canal = Canal.from_cfg(canais[canal_key]) if canal_key else None
        path = "us" if canal is not None else "br"
        for inst_name in cen["instrumentos"]:
            inst = instrumentos[inst_name]
            runs.append(
                RunSpec(
                    cenario_key=ck,
                    cenario_rotulo=str(cen["rotulo"]),
                    instrumento=inst_name,
                    inst_cfg=inst,
                    expo_nome=str(inst["exposicao"]),
                    path=path,
                    canal=canal,
                    nome_inst=str(inst.get("nome", inst_name)),
                )
            )
    return runs


# ---------------------------------------------------------------------------
# Índice de retorno total líquido em USD (start = 1.0)
# ---------------------------------------------------------------------------
def net_usd_index(
    expo: Exposicao,
    inst: dict[str, Any],
    tributos: dict[str, Any],
    *,
    apply_er: bool = True,
    apply_div: bool = True,
) -> pd.Series:
    """Índice de retorno total em USD do instrumento (1.0 no início).

    Sempre soma de volta a taxa do proxy (vira índice bruto); ``apply_er`` desconta
    a taxa do INSTRUMENTO; ``apply_div`` desconta a retenção sobre dividendos.
    """
    er_proxy_d = costs.er_diaria(expo.taxa_proxy)
    daily = expo.r_total.fillna(0.0) + er_proxy_d

    if apply_div:
        retencao = costs.retencao_dividendos(inst, tributos)
        daily = daily - expo.div.fillna(0.0) * (1.0 - retencao)
    if apply_er:
        daily = daily - costs.er_diaria(float(inst.get("taxa_adm", 0.0)))

    idx = (1.0 + daily).cumprod()
    idx.iloc[0] = 1.0
    return idx


# ---------------------------------------------------------------------------
# Lump-sum: valor de liquidação em BRL a cada data t
# ---------------------------------------------------------------------------
def lump_curve(
    expo: Exposicao,
    inst: dict[str, Any],
    path: str,
    canal: Canal | None,
    a0_brl: float,
    config: dict[str, Any],
    *,
    apply_er: bool = True,
    apply_div: bool = True,
    apply_entry: bool = True,
    apply_exit: bool = True,
    apply_tax: bool = True,
    etf_rate: float | None = None,
) -> pd.Series:
    tributos = config["tributos"]
    b3 = config["b3"]
    usd_idx = net_usd_index(expo, inst, tributos, apply_er=apply_er, apply_div=apply_div)
    fx = expo.fx
    fx0 = float(fx.iloc[0])

    if path == "br":
        emol = float(b3.get("emolumentos", 0.0)) + float(b3.get("corretagem", 0.0))
        invested = a0_brl * (1.0 - emol) if apply_entry else a0_brl
        # NAV da cota em BRL ~ valor USD subjacente × câmbio
        brl_idx = usd_idx * fx
        brl_idx = brl_idx / float(brl_idx.iloc[0])
        gross_sale = invested * brl_idx
        proceeds = gross_sale * (1.0 - float(b3.get("emolumentos", 0.0))) if apply_exit else gross_sale
        if apply_tax:
            rate = etf_rate if etf_rate is not None else float(tributos["etf_b3_ganho_capital"])
            isencao = float(tributos.get("etf_b3_isencao_brl", 0.0))
            tax = (proceeds - a0_brl).clip(lower=0.0) * rate
            # isenção por mês de venda (0 para ETFs) — aplicada quando proceeds <= isenção
            if isencao > 0.0:
                tax = tax.where(proceeds > isencao, 0.0)
            proceeds = proceeds - tax
        return proceeds

    # path == 'us'
    zero = Canal("zero")
    canal_eff = canal if canal is not None else zero
    canal_in = canal_eff if apply_entry else zero
    canal_out = canal_eff if apply_exit else zero

    usd0 = costs.brl_para_usd(a0_brl, fx0, canal_in)
    usd_value = usd0 * usd_idx  # usd_idx começa em 1.0
    # converte em cada data t (vetorizado)
    proceeds = pd.Series(
        [costs.usd_para_brl(float(v), float(f), canal_out) for v, f in zip(usd_value.to_numpy(), fx.to_numpy())],
        index=usd_value.index,
    )
    if apply_tax:
        rate = float(tributos["exterior_ganho_capital"])
        tax = (proceeds - a0_brl).clip(lower=0.0) * rate
        proceeds = proceeds - tax
    return proceeds


# ---------------------------------------------------------------------------
# Decomposição de custos (waterfall) no horizonte final, em BRL
# ---------------------------------------------------------------------------
COST_STEPS = [
    ("taxa_adm", dict(apply_er=True, apply_div=False, apply_entry=False, apply_exit=False, apply_tax=False)),
    ("retencao_dividendos", dict(apply_er=True, apply_div=True, apply_entry=False, apply_exit=False, apply_tax=False)),
    ("cambio_entrada", dict(apply_er=True, apply_div=True, apply_entry=True, apply_exit=False, apply_tax=False)),
    ("cambio_saida", dict(apply_er=True, apply_div=True, apply_entry=True, apply_exit=True, apply_tax=False)),
    ("ir_venda", dict(apply_er=True, apply_div=True, apply_entry=True, apply_exit=True, apply_tax=True)),
]


def cost_decomposition(
    expo: Exposicao, inst: dict[str, Any], path: str, canal: Canal | None,
    a0_brl: float, config: dict[str, Any], *, etf_rate: float | None = None,
) -> dict[str, float]:
    """Quanto cada custo retirou do teto bruto (índice×câmbio sem custos), em BRL."""
    gross = float(
        lump_curve(expo, inst, path, canal, a0_brl, config,
                   apply_er=False, apply_div=False, apply_entry=False,
                   apply_exit=False, apply_tax=False).iloc[-1]
    )
    out: dict[str, float] = {"bruto": gross}
    prev = gross
    for label, flags in COST_STEPS:
        v = float(lump_curve(expo, inst, path, canal, a0_brl, config, etf_rate=etf_rate, **flags).iloc[-1])
        out[label] = prev - v
        prev = v
    out["liquido"] = prev
    return out


# ---------------------------------------------------------------------------
# DCA: aportes mensais
# ---------------------------------------------------------------------------
def _monthly_first(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    df = pd.Series(index, index=index)
    return pd.DatetimeIndex(df.groupby([index.year, index.month]).first().to_numpy())


@dataclass
class DcaResult:
    valor_mercado: pd.Series   # MTM em BRL ao longo do tempo (gross de IR de saída)
    investido: pd.Series       # total aportado (BRL) ao longo do tempo
    final_liquido: float       # valor líquido se liquidar no fim
    total_investido: float
    irr_anual: float


def dca_result(
    expo: Exposicao, inst: dict[str, Any], path: str, canal: Canal | None,
    mensal_brl: float, config: dict[str, Any], *, etf_rate: float | None = None,
) -> DcaResult:
    tributos = config["tributos"]
    b3 = config["b3"]
    usd_idx = net_usd_index(expo, inst, tributos)
    fx = expo.fx
    index = expo.index
    datas = _monthly_first(index)

    if path == "br":
        emol_buy = float(b3.get("emolumentos", 0.0)) + float(b3.get("corretagem", 0.0))
        brl_idx = usd_idx * fx
        brl_idx = brl_idx / float(brl_idx.iloc[0])
        acc = pd.Series(0.0, index=index)
        for c in datas:
            principal = mensal_brl * (1.0 - emol_buy)
            acc.loc[c] += principal / float(brl_idx.loc[c])
        acc = acc.cumsum()
        valor = acc * brl_idx
        investido = pd.Series(0.0, index=index)
        for c in datas:
            investido.loc[c] += mensal_brl
        investido = investido.cumsum()
        total_inv = float(len(datas) * mensal_brl)
        gross_final = float(valor.iloc[-1]) * (1.0 - float(b3.get("emolumentos", 0.0)))
        rate = etf_rate if etf_rate is not None else float(tributos["etf_b3_ganho_capital"])
        tax = max(0.0, gross_final - total_inv) * rate
        final_liq = gross_final - tax
    else:
        zero = Canal("zero")
        canal_eff = canal if canal is not None else zero
        acc = pd.Series(0.0, index=index)
        for c in datas:
            usd_i = costs.brl_para_usd(mensal_brl, float(fx.loc[c]), canal_eff)
            acc.loc[c] += usd_i / float(usd_idx.loc[c])
        acc = acc.cumsum()
        usd_value = acc * usd_idx
        valor = usd_value * fx  # MTM em BRL no spot (sem custo de saída)
        investido = pd.Series(0.0, index=index)
        for c in datas:
            investido.loc[c] += mensal_brl
        investido = investido.cumsum()
        total_inv = float(len(datas) * mensal_brl)
        proceeds = costs.usd_para_brl(float(usd_value.iloc[-1]), float(fx.iloc[-1]), canal_eff)
        rate = float(tributos["exterior_ganho_capital"])
        tax = max(0.0, proceeds - total_inv) * rate
        final_liq = proceeds - tax

    irr = _irr_monthly(len(datas), mensal_brl, final_liq)
    return DcaResult(valor, investido, final_liq, total_inv, irr)


def _irr_monthly(n_aportes: int, mensal: float, valor_final: float) -> float:
    """TIR anual aproximada para n aportes mensais iguais e um resgate final."""
    if n_aportes <= 0 or valor_final <= 0:
        return float("nan")
    flows = [-mensal] * n_aportes + [valor_final]  # resgate 1 mês após o último aporte

    def npv(rate_m: float) -> float:
        v = 1.0 + rate_m
        if v <= 1e-9:
            return float("inf")
        return float(sum(cf * v ** (-t) for t, cf in enumerate(flows)))

    # NPV decresce com a taxa: bracket conforme o sinal em r=0 (ganho vs perda).
    if npv(0.0) >= 0:
        lo, hi = 0.0, 2.0
    else:
        lo, hi = -0.8, 0.0
    if npv(lo) * npv(hi) > 0:
        return float("nan")
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(lo) * npv(mid) <= 0:
            hi = mid
        else:
            lo = mid
    rate_m = (lo + hi) / 2
    return (1.0 + rate_m) ** 12 - 1.0


# ---------------------------------------------------------------------------
# Estatísticas-resumo
# ---------------------------------------------------------------------------
def years_of(expo: Exposicao) -> float:
    idx = expo.index
    return (idx[-1] - idx[0]).days / 365.25


def cagr(final: float, inicial: float, years: float) -> float:
    if inicial <= 0 or final <= 0 or years <= 0:
        return float("nan")
    return (final / inicial) ** (1.0 / years) - 1.0


def tracking_error_annual(sintetico: pd.Series, real: pd.Series) -> float:
    """Tracking error anualizado em base MENSAL (sint × real).

    Deliberadamente mensal: a série sintética usa pregões dos EUA (SPY/VT) e o
    ETF real negocia na B3 (pregões e horário de fechamento diferentes), o que
    cria ruído diário espúrio que NÃO é erro de réplica. O alinhamento mensal
    remove esse descasamento de sessão.
    """
    common = sintetico.index.union(real.index)
    a = sintetico.reindex(common).ffill()
    b = real.reindex(common).ffill()
    am = a.resample("ME").last().pct_change()
    bm = b.resample("ME").last().pct_change()
    idx = am.dropna().index.intersection(bm.dropna().index)
    if len(idx) < 6:
        return float("nan")
    diff = am.loc[idx] - bm.loc[idx]
    return float(diff.std() * np.sqrt(12))


def cagr_gap(sintetico: pd.Series, real: pd.Series) -> tuple[float, float, float]:
    """CAGR do sintético, CAGR do real e a diferença (no período comum)."""
    common = sintetico.index.intersection(real.index)
    if len(common) < 30:
        return float("nan"), float("nan"), float("nan")
    s = sintetico.reindex(common)
    r = real.reindex(common)
    yrs = (common[-1] - common[0]).days / 365.25
    cs = (s.iloc[-1] / s.iloc[0]) ** (1.0 / yrs) - 1.0
    cr = (r.iloc[-1] / r.iloc[0]) ** (1.0 / yrs) - 1.0
    return float(cs), float(cr), float(cs - cr)
