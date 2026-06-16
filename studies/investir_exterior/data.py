"""Carregamento e preparação das séries.

Para cada EXPOSIÇÃO (S&P 500, mundo) usamos um ETF-proxy de longo histórico
(SPY desde 2003, VT desde 2008) e decompomos o retorno diário em:

    r_total = adj_close.pct_change()      # retorno total bruto (reinveste dividendos)
    r_price = close.pct_change()          # retorno só de preço
    div     = (r_total - r_price)         # rendimento de dividendos do dia (>= 0)

Isso permite aplicar a retenção na fonte sobre dividendos por instrumento sem
precisar da coluna ``dividends`` (que o YFinanceSource normaliza para fora).
Somamos de volta a taxa do proxy (``taxa_proxy``) para aproximar o índice puro.

Câmbio: ``BRL=X`` (USD/BRL = reais por dólar), histórico desde dez/2003.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from market_lab.backtest.data.yfinance_source import YFinanceSource

from . import config as cfg


@dataclass
class Exposicao:
    """Séries diárias alinhadas de uma exposição (já intersectadas com o câmbio)."""

    nome: str                 # 'sp500' | 'mundo'
    r_total: pd.Series        # retorno total bruto (índice, sem taxa do proxy)
    r_price: pd.Series        # retorno só de preço
    div: pd.Series            # rendimento de dividendos diário (>= 0)
    fx: pd.Series             # USD/BRL alinhado (nível)
    taxa_proxy: float

    @property
    def index(self) -> pd.DatetimeIndex:
        return self.r_total.index


@dataclass
class Bundle:
    exposicoes: dict[str, Exposicao]
    reais: dict[str, pd.Series]   # ticker_real -> preço de fechamento (BRL)
    fx_full: pd.Series            # USD/BRL completo (para o gráfico de câmbio)


def _decompose(close: pd.Series, adj: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    r_total = adj.pct_change()
    r_price = close.pct_change()
    div = (r_total - r_price).clip(lower=0.0)
    return r_total, r_price, div


def build(config: dict[str, Any], today: date, source: YFinanceSource | None = None) -> Bundle:
    src = source or YFinanceSource()
    earliest = date(2003, 1, 1)

    fx_full = src.fetch("BRL=X", earliest, today)["close"].dropna()
    if fx_full.empty:
        raise RuntimeError("USD/BRL (BRL=X) vazio — verifique a conexão/yfinance.")

    proxies = config["proxies"]
    exposicoes: dict[str, Exposicao] = {}
    for nome, prox in proxies.items():
        inicio, fim = cfg.window(config, nome, today=today)
        df = src.fetch(str(prox["ticker"]), earliest, fim)
        close = df["close"].dropna()
        adj = df["adj_close"].dropna()
        r_total, r_price, div = _decompose(close, adj)

        # Calendário comum: dias do ETF que também têm câmbio, dentro da janela.
        idx = r_total.dropna().index.intersection(fx_full.index)
        idx = idx[(idx >= pd.Timestamp(inicio)) & (idx <= pd.Timestamp(fim))]
        fx_aligned = fx_full.reindex(idx).ffill()

        exposicoes[nome] = Exposicao(
            nome=nome,
            r_total=r_total.reindex(idx),
            r_price=r_price.reindex(idx),
            div=div.reindex(idx),
            fx=fx_aligned,
            taxa_proxy=float(prox.get("taxa_proxy", 0.0)),
        )

    # Séries reais dos ETFs B3 (validação sintético × real).
    reais: dict[str, pd.Series] = {}
    for nome, inst in config["instrumentos"].items():
        ticker_real = inst.get("ticker_real")
        if not ticker_real:
            continue
        df = src.fetch(str(ticker_real), earliest, today)
        serie = df["close"].dropna()
        if not serie.empty:
            reais[nome] = serie

    return Bundle(exposicoes=exposicoes, reais=reais, fx_full=fx_full)
