"""Funções puras de custo e tributação (sem estado, fáceis de testar).

Convenções:
  * ``fx`` é sempre USD/BRL = reais por dólar (ex.: 5,06).
  * ``spread`` é a fração perdida em CADA conversão (markup sobre a taxa comercial).
  * Conversões aplicam, em ordem: spread, IOF, tarifa percentual (multiplicativas)
    e, por fim, a tarifa fixa em USD.

Fontes dos números: ver ``SPEC.md`` (Lei 14.754/2023, IOF 2025-2026, spreads
de mercado jun/2026).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Canal:
    """Canal de câmbio (Inter, Wise, Transfer Bank, ...)."""

    nome: str
    spread: float = 0.0
    fixo_usd: float = 0.0
    fixo_pct: float = 0.0
    iof_ida: float = 0.0
    iof_volta: float = 0.0

    @classmethod
    def from_cfg(cls, cfg: dict[str, Any]) -> "Canal":
        return cls(
            nome=str(cfg.get("nome", "?")),
            spread=float(cfg.get("spread", 0.0)),
            fixo_usd=float(cfg.get("fixo_usd", 0.0)),
            fixo_pct=float(cfg.get("fixo_pct", 0.0)),
            iof_ida=float(cfg.get("iof_ida", 0.0)),
            iof_volta=float(cfg.get("iof_volta", 0.0)),
        )

    def zerado(self, **campos: float) -> "Canal":
        """Cópia com campos zerados/sobrescritos (para decomposição de custos)."""
        base = dict(
            nome=self.nome,
            spread=self.spread,
            fixo_usd=self.fixo_usd,
            fixo_pct=self.fixo_pct,
            iof_ida=self.iof_ida,
            iof_volta=self.iof_volta,
        )
        base.update(campos)
        return Canal(**base)  # type: ignore[arg-type]


def brl_para_usd(amount_brl: float, fx: float, canal: Canal) -> float:
    """Converte BRL -> USD aplicando spread, IOF ida e tarifas (remessa de ida)."""
    if amount_brl <= 0:
        return 0.0
    usd = amount_brl / fx
    usd *= (1.0 - canal.spread)
    usd *= (1.0 - canal.iof_ida)
    usd *= (1.0 - canal.fixo_pct)
    usd -= canal.fixo_usd
    return max(0.0, usd)


def usd_para_brl(amount_usd: float, fx: float, canal: Canal) -> float:
    """Converte USD -> BRL aplicando spread, IOF volta e tarifas (repatriamento)."""
    if amount_usd <= 0:
        return 0.0
    usd = max(0.0, amount_usd - canal.fixo_usd)
    brl = usd * fx
    brl *= (1.0 - canal.spread)
    brl *= (1.0 - canal.iof_volta)
    brl *= (1.0 - canal.fixo_pct)
    return max(0.0, brl)


def retencao_dividendos(inst: dict[str, Any], tributos: dict[str, Any]) -> float:
    """Fração dos dividendos RETIDA pelo investidor (reinvestida) durante o acúmulo.

    * Instrumento que ACUMULA (ETF B3 ou UCITS irlandês): só sofre a retenção
      interna na fonte (30% se embrulha fundo US-domiciliado; 15% se é/embrulha
      UCITS irlandês); o IR brasileiro é diferido para a venda. retenção = 1 - w.
    * Instrumento US que DISTRIBUI (VOO/VT): retenção na fonte dos EUA (w) e, no
      Brasil, IR sobre dividendos (Lei 14.754). Com crédito do imposto pago no
      exterior (reciprocidade BR-EUA), o efetivo é max(w, ir_br) — o excesso de w
      é perdido. Sem crédito, é cascata (1-w)(1-ir_br).
    """
    w = float(inst.get("retencao_dividendos", 0.0))
    acumula = bool(inst.get("acumula", str(inst.get("listagem", "B3")) == "B3"))
    if acumula:
        return 1.0 - w
    ir_br = float(tributos.get("exterior_dividendo", 0.0))
    if bool(tributos.get("credito_imposto_exterior", True)):
        return 1.0 - max(w, ir_br)
    return (1.0 - w) * (1.0 - ir_br)


def ir_ganho_capital(proceeds: float, cost_basis: float, aliquota: float, isencao: float = 0.0) -> float:
    """IR sobre ganho de capital. ``isencao`` = teto de venda isento (0 p/ ETFs)."""
    gain = proceeds - cost_basis
    if gain <= 0:
        return 0.0
    if isencao > 0.0 and proceeds <= isencao:
        return 0.0
    return gain * aliquota


def er_diaria(taxa_anual: float, dias_por_ano: int = 252) -> float:
    """Converte taxa de administração anual em drag diário (geométrico)."""
    return 1.0 - (1.0 - taxa_anual) ** (1.0 / dias_por_ano)
