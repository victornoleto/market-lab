"""Testes do estudo studies/investir_exterior (custos puros + sanidades da simulação).

Usa dados sintéticos em memória — não toca a rede/yfinance.
"""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from studies.investir_exterior import config as cfg
from studies.investir_exterior import costs, report, simulate as S
from studies.investir_exterior.costs import Canal
from studies.investir_exterior.data import Bundle, Exposicao


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #
def _synthetic_expo(nome: str = "sp500", n: int = 252 * 6, fx_drift: float = 0.0) -> Exposicao:
    idx = pd.bdate_range("2010-01-01", periods=n)
    r_total = pd.Series(0.0004, index=idx)   # ~10,6%/ano total
    r_price = pd.Series(0.00032, index=idx)  # parte de preço
    div = (r_total - r_price).clip(lower=0)  # ~0,008%/dia de dividendo
    fx = pd.Series(5.0 * (1.0 + fx_drift) ** np.arange(n), index=idx)
    return Exposicao(nome=nome, r_total=r_total, r_price=r_price, div=div, fx=fx, taxa_proxy=0.000945)


def _synthetic_bundle() -> Bundle:
    """Bundle em memória (sem rede) para testar render dos relatórios."""
    sp = _synthetic_expo("sp500", n=252 * 8, fx_drift=0.0002)
    mundo = _synthetic_expo("mundo", n=252 * 6, fx_drift=0.0002)
    reais = {
        "IVVB11": sp.fx.iloc[-800:].copy(),
        "WRLD11": mundo.fx.iloc[-600:].copy(),
        "ACWI11": mundo.fx.iloc[-600:].copy(),
    }
    return Bundle(exposicoes={"sp500": sp, "mundo": mundo}, reais=reais, fx_full=sp.fx)


@pytest.fixture(scope="module")
def config() -> dict:
    return cfg.load_config()


# --------------------------------------------------------------------------- #
# costs.py — funções puras
# --------------------------------------------------------------------------- #
def test_conversao_canal_zero_sem_perda():
    zero = Canal("zero")
    assert costs.brl_para_usd(1000.0, 5.0, zero) == pytest.approx(200.0)
    assert costs.usd_para_brl(200.0, 5.0, zero) == pytest.approx(1000.0)


def test_spread_e_iof_reduzem_usd():
    zero = Canal("zero")
    com_spread = Canal("c", spread=0.015, iof_ida=0.011)
    base = costs.brl_para_usd(1000.0, 5.0, zero)
    menos = costs.brl_para_usd(1000.0, 5.0, com_spread)
    assert menos < base
    # spread 1,5% + IOF 1,1% ~ 2,6% de perda
    assert menos == pytest.approx(base * (1 - 0.015) * (1 - 0.011), rel=1e-9)


def test_tarifa_fixa_morde_valores_pequenos():
    wise = Canal("wise", spread=0.005, fixo_usd=6.96, fixo_pct=0.0053, iof_ida=0.011)
    pequeno = costs.brl_para_usd(1000.0, 5.0, wise) / (1000.0 / 5.0)   # fração recebida
    grande = costs.brl_para_usd(100000.0, 5.0, wise) / (100000.0 / 5.0)
    assert pequeno < grande  # tarifa fixa pesa mais no aporte pequeno


def test_retencao_dividendos_estruturas(config):
    trib = config["tributos"]
    b3_us_wrap = {"listagem": "B3", "retencao_dividendos": 0.30}
    b3_irish = {"listagem": "B3", "retencao_dividendos": 0.15}
    us_direct = {"listagem": "US", "retencao_dividendos": 0.30}
    assert costs.retencao_dividendos(b3_us_wrap, trib) == pytest.approx(0.70)
    assert costs.retencao_dividendos(b3_irish, trib) == pytest.approx(0.85)
    # US com crédito (default): efetivo = max(0.30, 0.15) => retém 0.70
    assert costs.retencao_dividendos(us_direct, {**trib, "credito_imposto_exterior": True}) == pytest.approx(0.70)
    # US sem crédito: cascata (1-0.30)(1-0.15) = 0.595
    assert costs.retencao_dividendos(us_direct, {**trib, "credito_imposto_exterior": False}) == pytest.approx(0.595)


def test_ir_ganho_capital():
    assert costs.ir_ganho_capital(1500.0, 1000.0, 0.15) == pytest.approx(75.0)
    assert costs.ir_ganho_capital(900.0, 1000.0, 0.15) == 0.0          # prejuízo
    assert costs.ir_ganho_capital(15000.0, 10000.0, 0.15, isencao=20000.0) == 0.0  # venda isenta


def test_er_diaria_compoe_para_anual():
    d = costs.er_diaria(0.0023)
    assert (1 - d) ** 252 == pytest.approx(1 - 0.0023, rel=1e-6)


# --------------------------------------------------------------------------- #
# simulate.py — sanidades do plano
# --------------------------------------------------------------------------- #
def test_net_index_custos_reduzem(config):
    expo = _synthetic_expo()
    inst = config["instrumentos"]["IVVB11"]
    bruto = S.net_usd_index(expo, inst, config["tributos"], apply_er=False, apply_div=False)
    com_div = S.net_usd_index(expo, inst, config["tributos"], apply_er=False, apply_div=True)
    com_tudo = S.net_usd_index(expo, inst, config["tributos"], apply_er=True, apply_div=True)
    assert com_div.iloc[-1] < bruto.iloc[-1]      # retenção de dividendos reduz
    assert com_tudo.iloc[-1] < com_div.iloc[-1]   # taxa adm reduz ainda mais


def test_sanidade_gross_br_igual_us(config):
    """Mesma exposição: o teto bruto (sem custos) é idêntico para B3 e US."""
    expo = _synthetic_expo()
    A0 = 100000.0
    flags = dict(apply_er=False, apply_div=False, apply_entry=False, apply_exit=False, apply_tax=False)
    gb = S.lump_curve(expo, config["instrumentos"]["IVVB11"], "br", None, A0, config, **flags)
    canal = Canal.from_cfg(config["canais_cambio"]["transfer_bank"])
    gu = S.lump_curve(expo, config["instrumentos"]["VOO"], "us", canal, A0, config, **flags)
    assert float(gb.iloc[-1]) == pytest.approx(float(gu.iloc[-1]), rel=1e-9)


def test_decomposicao_soma_fecha(config):
    expo = _synthetic_expo()
    canal = Canal.from_cfg(config["canais_cambio"]["inter_digital"])
    dec = S.cost_decomposition(expo, config["instrumentos"]["VOO"], "us", canal, 100000.0, config)
    soma_custos = sum(dec[k] for k in ["taxa_adm", "retencao_dividendos", "cambio_entrada", "cambio_saida", "ir_venda"])
    assert dec["bruto"] - soma_custos == pytest.approx(dec["liquido"], rel=1e-9)
    assert dec["liquido"] < dec["bruto"]


def test_spread_maior_piora_us(config):
    expo = _synthetic_expo()
    inst = config["instrumentos"]["VOO"]
    A0 = 100000.0
    barato = Canal("barato", spread=0.003, iof_ida=0.011, iof_volta=0.0038)
    caro = Canal("caro", spread=0.020, iof_ida=0.011, iof_volta=0.0038)
    fin_barato = float(S.lump_curve(expo, inst, "us", barato, A0, config).iloc[-1])
    fin_caro = float(S.lump_curve(expo, inst, "us", caro, A0, config).iloc[-1])
    assert fin_caro < fin_barato


def test_dca_roda_e_irr_finita(config):
    expo = _synthetic_expo()
    canal = Canal.from_cfg(config["canais_cambio"]["transfer_bank"])
    res = S.dca_result(expo, config["instrumentos"]["VOO"], "us", canal, 1000.0, config)
    assert res.total_investido > 0
    assert res.final_liquido > 0
    assert np.isfinite(res.irr_anual)


def test_build_runs_cobre_cenarios(config):
    runs = S.build_runs(config)
    chaves = {(r.cenario_key, r.instrumento) for r in runs}
    assert ("brasil", "IVVB11") in chaves
    assert ("inter", "VOO") in chaves
    assert ("ibkr", "VT") in chaves
    # caminho correto por cenário
    assert all(r.path == "br" for r in runs if r.cenario_key == "brasil")
    assert all(r.path == "us" for r in runs if r.cenario_key in {"inter", "ibkr"})


# --------------------------------------------------------------------------- #
# report.py — contexto + geração dos dois outputs (sem rede)
# --------------------------------------------------------------------------- #
def test_build_context_charts_e_tabelas(config):
    ctx = report.build_context(config, _synthetic_bundle(), date(2026, 6, 16))
    esperados = {"wealth_sp500", "wealth_mundo", "waterfall", "breakeven",
                 "dca_sp500", "dca_mundo", "sensibilidade", "cambio", "validacao"}
    assert esperados <= set(ctx.charts)
    assert len(ctx.tables["lump"][1]) == len(S.build_runs(config))  # 1 linha por run
    assert ctx.numbers["cagr_ivvb"].endswith("%")


def test_generate_all_escreve_html_e_md(tmp_path, config):
    out = report.generate_all(config, _synthetic_bundle(), date(2026, 6, 16),
                              out_dir=tmp_path, formats=("html", "md"))
    assert out["html"].exists() and out["md"].exists()
    pngs = sorted((tmp_path / "plots").glob("*.png"))
    assert len(pngs) == 9
    html = out["html"].read_text(encoding="utf-8")
    assert "cdn.plot.ly" in html        # plotly via CDN (uma vez)
    assert "IBM+Plex+Sans" in html      # Google Fonts
    assert html.count("cdn.plot.ly") == 1
    md = out["md"].read_text(encoding="utf-8")
    assert "](plots/" in md and "## 1." in md
    # cada gráfico vem com uma tabela de apoio (curvas + resultado final)
    assert "Valores ao longo do tempo" in md
    assert "Custo total" in md


def test_table_for_cobre_tipos(config):
    from studies.investir_exterior import report_md
    ctx = report.build_context(config, _synthetic_bundle(), date(2026, 6, 16))
    # line chart: tem coluna Data + 1+ séries, última linha = resultado final
    cap, headers, rows = report_md.table_for(ctx.charts["wealth_sp500"])
    assert headers[0] == "Data" and len(headers) >= 2 and len(rows) >= 2
    # waterfall: última linha é o custo total
    _, wh, wr = report_md.table_for(ctx.charts["waterfall"])
    assert wr[-1][0].startswith("**Custo total")
    # breakeven traz a coluna de vantagem
    _, bh, _ = report_md.table_for(ctx.charts["breakeven"])
    assert any("Vantagem" in h for h in bh)
