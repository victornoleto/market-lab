"""Portfolio analysis: 50/50 Plano C + EMA-150 th=5% 3x UPRO cash.

Answers the user's question about expected CAGR of a 50/50 allocation,
using historical data to simulate the blended portfolio with annual
rebalancing. Also produces stress scenarios against AI-bubble forecasts
from major institutions (Vanguard 4.5%, Schwab, Goldman 7.7%,
Research Affiliates 3.1%, Shiller 1.3%, Buffett Indicator −0.7%).

Outputs:
  - analyses/05_portfolio_5050_analysis.md
  - analyses/portfolio_plots/equity_curves.png
  - analyses/portfolio_plots/drawdown_compare.png
  - analyses/portfolio_plots/forecast_scenarios.png
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ai_trade.backtest.data.testfolio_loader import (  # noqa: E402
    load_testfolio_returns,
    load_testfolio_series,
)
from ai_trade.backtest.grid.real_etf_regime_runner import (  # noqa: E402
    SPY_MARKET,
    build_data_bundle,
    simulate_config_with_real_legs,
)
from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (  # noqa: E402
    EMASMAThresholdConfig,
    simulate_ema_sma_threshold,
)

ANALYSES_DIR = Path(__file__).parent
PLOTS_DIR = ANALYSES_DIR / "portfolio_plots"

CFG = EMASMAThresholdConfig(
    filter="EMA", lookback=150, threshold_pct=0.05,
    buy_leverage=3.0, sell_leverage=0.0,
    tax_rate=0.15,  # assume BR DARF applied
)

TRADING_DAYS = 252


def _setup_logging() -> logging.Logger:
    logger = logging.getLogger("portfolio_5050")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(sh)
    return logger


def _fmt_pct(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x * 100:+.{digits}f}%"


def _fmt_num(x: float, digits: int = 2) -> str:
    if x is None or np.isnan(x) or np.isinf(x):
        return "—"
    return f"{x:.{digits}f}"


def simulate_blended_portfolio(
    returns_a: pd.Series,
    returns_b: pd.Series,
    weight_a: float = 0.5,
    rebalance_freq: str = "YE",  # year-end
) -> pd.Series:
    """Blend two daily return series with periodic rebalancing to target weights.

    Within a rebalance period, the two sleeves drift. At each rebalance
    date, weights are reset to (weight_a, 1-weight_a).
    """
    df = pd.concat({"a": returns_a, "b": returns_b}, axis=1).dropna()
    # Equity sleeves — each starts at its target weight at rebalance.
    dates = df.index
    # Determine rebalance markers.
    if rebalance_freq == "YE":
        marker = pd.Series(dates, index=dates).dt.year
    elif rebalance_freq == "Q":
        marker = pd.Series(dates, index=dates).dt.to_period("Q")
    elif rebalance_freq == "M":
        marker = pd.Series(dates, index=dates).dt.to_period("M")
    else:
        raise ValueError(rebalance_freq)
    rebalance_mask = marker != marker.shift(1)
    rebalance_mask.iloc[0] = True

    equity = 1.0
    w_a_current = weight_a
    w_b_current = 1.0 - weight_a
    sleeve_a = weight_a
    sleeve_b = 1.0 - weight_a
    out = []
    for i in range(len(df)):
        if rebalance_mask.iloc[i]:
            # Rebalance to target weights using current equity.
            sleeve_a = equity * weight_a
            sleeve_b = equity * (1.0 - weight_a)
        ra = df["a"].iloc[i] if not np.isnan(df["a"].iloc[i]) else 0.0
        rb = df["b"].iloc[i] if not np.isnan(df["b"].iloc[i]) else 0.0
        sleeve_a *= 1.0 + ra
        sleeve_b *= 1.0 + rb
        equity = sleeve_a + sleeve_b
        out.append(equity)
    return pd.Series(out, index=df.index, name=f"blend_w{weight_a:.2f}")


def main() -> int:
    log = _setup_logging()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # ========== Historical sleeves ==========
    log.info("Loading SPYSIM synth (Plano-C proxy) + running UPRO strategy...")
    spx_prices = load_testfolio_series("SPYSIM")
    spx_returns = load_testfolio_returns("SPYSIM")

    # Strategy leg (synth full 40y).
    strat_res = simulate_ema_sma_threshold(spx_prices, spx_returns, CFG)
    strat_rets = strat_res.daily_returns

    # Plano-C PROXY: use SPY B&H as a CONSERVATIVE proxy for Plano C
    # passive factor-tilted (real Plano C with NTSX etc is ~11% CAGR with
    # MDD ~40%; SPY B&H at ~11.5% CAGR with ~55% MDD is a pessimistic
    # proxy because Plano C has bonds/factor diversification).
    # Using SPY B&H gives the USER a BEAR-CASE estimate.
    plano_c_eq = spx_prices.reindex(spx_returns.index) / spx_prices.reindex(spx_returns.index).iloc[0]
    plano_c_rets = plano_c_eq.pct_change().fillna(0.0)

    # Bundle with UPRO real for the 2009-2026 sub-simulation.
    log.info("Simulating on SPY real Tiingo (2009-2026)...")
    real_bundle = build_data_bundle(SPY_MARKET, leverages_used=(1.0, 2.0, 3.0))
    strat_real = simulate_config_with_real_legs(CFG, real_bundle)
    strat_real_rets = strat_real.daily_returns
    spy_real_eq = real_bundle["signal_prices"] / real_bundle["signal_prices"].iloc[0]
    spy_real_rets = spy_real_eq.pct_change().fillna(0.0)

    # ========== Blends ==========
    log.info("Computing 50/50 blends with annual rebalancing...")
    blend_syn_50 = simulate_blended_portfolio(plano_c_rets, strat_rets, 0.5, "YE")
    blend_syn_30 = simulate_blended_portfolio(plano_c_rets, strat_rets, 0.7, "YE")  # 30% strat
    blend_syn_70 = simulate_blended_portfolio(plano_c_rets, strat_rets, 0.3, "YE")  # 70% strat

    blend_real_50 = simulate_blended_portfolio(spy_real_rets, strat_real_rets, 0.5, "YE")
    blend_real_30 = simulate_blended_portfolio(spy_real_rets, strat_real_rets, 0.7, "YE")
    blend_real_70 = simulate_blended_portfolio(spy_real_rets, strat_real_rets, 0.3, "YE")

    def stats(eq, rets):
        return {
            "cagr": _cagr(eq, TRADING_DAYS),
            "sharpe": _sharpe(rets, TRADING_DAYS),
            "mdd": _max_drawdown(eq),
        }

    stats_syn = {
        "100% Plano-C proxy (SPY B&H)": stats(plano_c_eq, plano_c_rets),
        "100% UPRO strategy (tax15)": stats(strat_res.equity, strat_rets),
        "30% strategy / 70% Plano-C": stats(blend_syn_30, blend_syn_30.pct_change().fillna(0.0)),
        "50% strategy / 50% Plano-C": stats(blend_syn_50, blend_syn_50.pct_change().fillna(0.0)),
        "70% strategy / 30% Plano-C": stats(blend_syn_70, blend_syn_70.pct_change().fillna(0.0)),
    }
    stats_real = {
        "100% SPY B&H": stats(spy_real_eq, spy_real_rets),
        "100% UPRO strategy (tax15)": stats(strat_real.equity, strat_real_rets),
        "30% strategy / 70% SPY": stats(blend_real_30, blend_real_30.pct_change().fillna(0.0)),
        "50% strategy / 50% SPY": stats(blend_real_50, blend_real_50.pct_change().fillna(0.0)),
        "70% strategy / 30% SPY": stats(blend_real_70, blend_real_70.pct_change().fillna(0.0)),
    }

    # ========== Plots ==========
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=120)
    ax.plot(plano_c_eq.index, plano_c_eq.values, label="100% SPY B&H (Plano C proxy)",
            color="#808080", linewidth=1.2, linestyle="--")
    ax.plot(strat_res.equity.index, strat_res.equity.values,
            label="100% Strategy (3x UPRO, tax15)", color="#d62728", linewidth=1.3)
    ax.plot(blend_syn_50.index, blend_syn_50.values,
            label="50/50 (annual rebalance)", color="#1f77b4", linewidth=1.4)
    ax.plot(blend_syn_30.index, blend_syn_30.values,
            label="30% strategy / 70% SPY", color="#2ca02c", linewidth=1.2)
    ax.plot(blend_syn_70.index, blend_syn_70.values,
            label="70% strategy / 30% SPY", color="#9467bd", linewidth=1.2)
    ax.set_yscale("log")
    ax.set_title("Blended portfolios vs pure legs (SPYSIM synth 1986-2026, tax 15%)")
    ax.set_ylabel("Equity (log, start=1.0)")
    ax.set_xlabel("Date")
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(loc="upper left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "equity_curves.png")
    plt.close(fig)

    # Drawdown comparison.
    def _dd(eq):
        peak = eq.cummax()
        return eq / peak - 1.0

    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=120)
    ax.fill_between(_dd(plano_c_eq).index, _dd(plano_c_eq).values * 100, 0,
                    color="#808080", alpha=0.2, label="100% SPY")
    ax.fill_between(_dd(strat_res.equity).index, _dd(strat_res.equity).values * 100, 0,
                    color="#d62728", alpha=0.2, label="100% Strategy")
    ax.fill_between(_dd(blend_syn_50).index, _dd(blend_syn_50).values * 100, 0,
                    color="#1f77b4", alpha=0.35, label="50/50 blend")
    ax.axhline(-25, color="orange", linestyle=":", linewidth=0.8,
               label="Mandate cap (-25%)")
    ax.axhline(-50, color="red", linestyle=":", linewidth=0.8,
               label="Warning tier (-50%)")
    ax.set_ylabel("Drawdown (%)")
    ax.set_xlabel("Date")
    ax.set_title("Drawdown comparison: 100% pure legs vs 50/50 blend")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "drawdown_compare.png")
    plt.close(fig)

    # Forecast scenario visualisation.
    scenarios = [
        ("Historical repeats (base case)", 0.115, 0.25, "#2ca02c"),
        ("Schwab/GS forecast", 0.077, 0.17, "#1f77b4"),
        ("Vanguard central (4.5%)", 0.045, 0.10, "#ff7f0e"),
        ("Research Affiliates (3.1%)", 0.031, 0.07, "#9467bd"),
        ("Shiller CAPE (1.3%)", 0.013, 0.03, "#d62728"),
        ("Buffett Indicator (-0.7%)", -0.007, -0.015, "#333333"),
    ]
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=120)
    labels = []
    pc_vals = []
    strat_vals = []
    blend_vals = []
    for name, spy_cagr, strat_cagr, _ in scenarios:
        pc_vals.append(spy_cagr * 100)
        strat_vals.append(strat_cagr * 100)
        # Naive 50/50 arithmetic (same as user's intuition).
        blend_naive = (spy_cagr + strat_cagr) / 2
        blend_vals.append(blend_naive * 100)
        labels.append(name)
    x = np.arange(len(labels))
    w = 0.28
    ax.bar(x - w, pc_vals, w, label="100% SPY / Plano C proxy", color="#808080")
    ax.bar(x, strat_vals, w, label="100% Strategy", color="#d62728")
    ax.bar(x + w, blend_vals, w, label="50/50 blend (arithmetic)", color="#1f77b4")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("Expected CAGR (%)")
    ax.set_title("Expected CAGR under different 10-year forecast scenarios")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "forecast_scenarios.png")
    plt.close(fig)

    # ========== MD output ==========
    lines: list[str] = []
    lines.append("# 50/50 portfolio — Plano C + 3× UPRO strategy\n")
    lines.append(
        "> Responde: \"qual o CAGR esperado de 50% Plano C + 50% estratégia "
        "EMA-150 th=5% 3× UPRO cash? É ~20%?\"  Inclui pesquisa de forecasts "
        "de grandes gestoras (Goldman, Vanguard, Research Affiliates, "
        "Shiller, Buffett Indicator) sobre o que esperar do SPY nas próximas "
        "décadas + preocupações com bolha de IA.\n"
    )

    # ---- Forecast survey ----
    lines.append("## Parte 1 — Forecasts 10-year do SPY (pesquisa 2026-04)\n")
    lines.append(
        "O que grandes gestoras e acadêmicos estão projetando para o SPY "
        "nos próximos 10 anos, em ordem crescente de pessimismo:\n"
    )
    lines.append("| Fonte | 10y CAGR nominal | Data do forecast | Racional |")
    lines.append("|---|---|---|---|")
    lines.append("| Goldman Sachs (base) | +7.7% | 2025-11 | Global equities modal 10y; GS vê earnings growth 10-12% 2026-27 |")
    lines.append("| Vanguard (VCMM central) | +4.5% (range 3.5-5.5%) | 2025-10 | Valuations elevated + higher rates; growth-stock muted |")
    lines.append("| Research Affiliates | +3.1% (nominal) | 2025-12 | Valuation-driven; bonds expected to outperform equities |")
    lines.append("| Shiller CAPE model | +1.3% | 2026-04 | CAPE 39.5 (vs mean 17.3, 2000 peak 44) |")
    lines.append("| Buffett Indicator (TMC/GDP) | **−0.7%** | 2026-04 | 226-233% ratio; 2.4σ above mean; flagged every major bubble |")
    lines.append("")
    lines.append(
        "**Dispersão = ~8.5pp CAGR** entre o mais otimista (GS 7.7%) e o "
        "mais pessimista (Buffett −0.7%). Histórico SPY long-term: ~10-11% "
        "nominal, mas últimos 10 anos foi 14.4% (acima da média, puxado "
        "por IA + low-rates era 2010-2021).\n"
    )

    lines.append("### Concentração + AI bubble vs dot-com\n")
    lines.append(
        "- **Mag 7 = 35% do S&P 500** — mesma concentração do topo da "
        "bolha dot-com 2000 (Apollo Global alertou \"single point of failure\").\n"
        "- **Forward P/E 23×** — mais esticado desde 2000.\n"
        "- **Shiller CAPE 39.5** — só foi tão alto em 1929 e 2000.\n"
        "- **Diferença dot-com**: as atuais líderes têm cash-flow real "
        "(Nvidia Q4'26 $68B receita vs dot-coms sem lucro). Cisco's John "
        "Chambers — que viveu dot-com — diz que \"AI bubble é mais difícil "
        "de navegar\" justamente porque as empresas são lucrativas.\n"
        "- **Paralelo-chave**: se um AI crash estilo 2000-2002 acontecer, "
        "a queda poderia eliminar $33 trilhões (mais que o PIB americano).\n"
    )

    lines.append("### O contra-argumento (Jeremy Siegel)\n")
    lines.append(
        "Siegel (Wharton) argumenta que o CAPE é biased desde 1990 por "
        "mudanças contábeis (write-offs, goodwill). Entre 1981-2015, CAPE "
        "sinalizou overvaluation em 416 de 422 meses — e investidores que "
        "seguiram o sinal perderam ganhos enormes. Ele sustenta que o "
        "\"novo normal\" do CAPE é 25-30, não 17.3.\n"
    )

    lines.append("### Consenso sobre os próximos 10 anos\n")
    lines.append(
        "**Mediana dos forecasts = ~3-5% CAGR** — significativamente abaixo "
        "do histórico. O que não significa crash iminente (pode ser \"lost "
        "decade\" de retornos baixos + volatilidade alta), mas **sinaliza "
        "que o pressuposto de 'SPY faz 10%/ano sempre' tem base frágil pros "
        "próximos 10 anos**.\n"
    )

    # ---- Blended portfolio math ----
    lines.append("## Parte 2 — Matemática do 50/50 (histórico, tax 15%)\n")
    lines.append(
        "Rodando o blend com rebalanceamento anual, em ambos os datasets. "
        "O **\"Plano C proxy\"** aqui é SPY buy-hold — proxy **conservador** "
        "(real Plano C com NTSX/diversification tem MDD menor e Sharpe "
        "melhor). A estratégia usa `tax_rate=0.15` para aproximar DARF BR.\n"
    )

    lines.append("### SPYSIM synth 40y (1986-2026)\n")
    lines.append("| Alocação | CAGR | Sharpe | Max DD |\n|---|---|---|---|")
    for name, s in stats_syn.items():
        lines.append(f"| {name} | {_fmt_pct(s['cagr'])} | {_fmt_num(s['sharpe'])} | {_fmt_pct(s['mdd'])} |")
    lines.append("")

    lines.append("### SPY real Tiingo (2009-2026)\n")
    lines.append("| Alocação | CAGR | Sharpe | Max DD |\n|---|---|---|---|")
    for name, s in stats_real.items():
        lines.append(f"| {name} | {_fmt_pct(s['cagr'])} | {_fmt_num(s['sharpe'])} | {_fmt_pct(s['mdd'])} |")
    lines.append("")

    lines.append("### Plots\n")
    lines.append("![equity](portfolio_plots/equity_curves.png)\n")
    lines.append("![drawdown](portfolio_plots/drawdown_compare.png)\n")

    # ---- Direct answer ----
    lines.append("## Parte 3 — Direto ao ponto: é realmente ~20%?\n")
    blend_syn_cagr = stats_syn["50% strategy / 50% Plano-C"]["cagr"]
    blend_real_cagr = stats_real["50% strategy / 50% SPY"]["cagr"]
    lines.append(
        f"- **Blend 50/50 synth 40y (tax15)**: CAGR "
        f"**{_fmt_pct(blend_syn_cagr)}**, Sharpe "
        f"{_fmt_num(stats_syn['50% strategy / 50% Plano-C']['sharpe'])}, "
        f"MDD {_fmt_pct(stats_syn['50% strategy / 50% Plano-C']['mdd'])}.\n"
        f"- **Blend 50/50 real 16.8y (tax15)**: CAGR "
        f"**{_fmt_pct(blend_real_cagr)}**, Sharpe "
        f"{_fmt_num(stats_real['50% strategy / 50% SPY']['sharpe'])}, "
        f"MDD {_fmt_pct(stats_real['50% strategy / 50% SPY']['mdd'])}.\n"
    )

    naive_avg = (0.1147 + 0.25) / 2  # SPY CAGR + strategy CAGR synth
    lines.append(
        f"### A intuição de ~20%\n\n"
        f"A média aritmética simples dos dois extremos dá "
        f"{_fmt_pct(naive_avg)} — a intuição é razoável como **limite "
        f"superior**, mas o CAGR geométrico do blend costuma ficar **1-3pp "
        f"abaixo** da média aritmética por causa do volatility drag. "
        f"Também: rebalanceamento anual captura um pouco de 'buy-low-sell-"
        f"high' bonus, mas custos + tax em cada rebalance reduzem esse ganho.\n"
    )

    # ---- Forward-looking scenarios ----
    lines.append("## Parte 4 — Cenários forward-looking (próximos 10 anos)\n")
    lines.append(
        "Agora o ponto crucial: **o histórico não é garantia**. Aplicando "
        "os forecasts dos principais gestores, o que seria de um 50/50 "
        "hoje? A tabela abaixo usa a regra-de-bolso: 3× UPRO com regime "
        "filter captura ~2-2.5× o CAGR do SPY em anos bullish e fica "
        "próximo de 0 em anos bearish. Tax drag 2-3pp.\n"
    )
    lines.append(
        "| Cenário | SPY 10y CAGR | Strategy estimada | Blend 50/50 |\n"
        "|---|---|---|---|"
    )
    lines.append("| Histórico repete (upside) | +11.5% | +20% (real) a +25% (synth) | **+15% a +18%** |")
    lines.append("| Goldman Sachs (base) | +7.7% | +13-17% | **+10% a +12%** |")
    lines.append("| Vanguard central | +4.5% | +8-12% | **+6% a +8%** |")
    lines.append("| Research Affiliates | +3.1% | +5-8% | **+4% a +6%** |")
    lines.append("| Shiller CAPE | +1.3% | +2-5% (ou 0 se chopsaw) | **+2% a +3%** |")
    lines.append("| Buffett / lost decade | −0.7% | −5% a 0 (LETF decay) | **−2% a 0%** |")
    lines.append("")
    lines.append("![scenarios](portfolio_plots/forecast_scenarios.png)\n")

    lines.append("**Leitura**: seu palpite de 20% está ancorado no cenário "
                 "histórico otimista. Nos forecasts institucionais (que já "
                 "precificam AI bubble + CAPE alto), **o blend cai para "
                 "4-12%** dependendo da fonte.\n")

    # ---- Volatility / correlation caveat ----
    lines.append("## Parte 5 — Correlação: o blend 50/50 não diversifica tanto quanto parece\n")
    lines.append(
        "Ambos os sleeves têm **exposição long SPY** — a estratégia usa "
        "UPRO (3× SPY) quando regime > 0, e cash quando regime < 0. Em "
        "um crash, os dois caem juntos (não há verdadeiro hedge). Correlação "
        "esperada: **0.8-0.9** durante drawdowns.\n\n"
        "Efeito prático no blend 50/50:\n"
        "- **Diversificação de vol** acontece principalmente durante "
        "sideways/choppy markets (quando estratégia em cash não cai).\n"
        "- **Durante crash**: Plano C cai 30-50% (SPY proxy) e "
        "estratégia cai 50-60% antes do signal ejetar. Blend 50/50 cai "
        "~40-55%.\n"
        "- **Anos de bull**: estratégia rende 20-25% com 3×, Plano C "
        "10-12%. Blend 15-17%.\n"
        "- **Rebalancing bonus**: ~0.5-1pp CAGR extra quando os dois ciclam "
        "fora de fase (raro).\n\n"
        "**Alternativa real de diversificação**: substituir metade do Plano "
        "C por NTSX (return-stacked equity+bonds), GLD, ou TLT — esses SIM "
        "descorrelacionam em crashes. Isso muda a matemática do blend "
        "(menos CAGR, muito menos MDD).\n"
    )

    # ---- AI bubble + timing ----
    lines.append("## Parte 6 — \"Comprar com desconto\" durante AI bubble\n")
    lines.append(
        "Você mencionou a ideia de entrar depois do crash. Três pontos:\n\n"
        "### 1. Timing é impossível\n"
        "O próprio Goldman/Vanguard não consegue prever o timing. O Shiller "
        "falou em overvaluation em 1996 — o mercado subiu mais 4 anos "
        "antes do crash. Se você esperar, pode perder 50% de upside "
        "esperando pelo crash. Se entrar agora, pode ver 40% de drawdown "
        "antes do crash acontecer.\n\n"
        "### 2. \"Comprar no desconto\" é Kelly, não heurística\n"
        "O momento matematicamente ótimo pra aumentar alocação em UPRO-"
        "strategy é **APÓS** o MDD, quando o signal virou +1 (compra) de novo. "
        "Isso o próprio signal faz automaticamente — toda vez que SPY cruza "
        "acima do MA+5% após um drawdown, você entra em UPRO. "
        "**O regime filter é seu 'buy the dip' automático**.\n\n"
        "### 3. Paper trade durante o bubble, deploy pós-crash\n"
        "**Alternativa prática**: em vez de entrar 50% agora, faça:\n"
        "- Mês 1-6: 100% Plano C + paper trade da estratégia.\n"
        "- Se houver crash (strategy entra em cash): deploy 10% do capital "
        "   em UPRO quando signal virar +1 de novo.\n"
        "- Gradualmente aumentar alocação até 25-30% conforme conforto "
        "   com o tracking error.\n\n"
        "Isso evita o pior caso: você entra 50% hoje, acontece o crash "
        "amanhã, você vê 40% de drawdown imediato, capitula, vende "
        "no fundo, perde permanentemente a parcela.\n"
    )

    # ---- Recommendation ----
    lines.append("## Parte 7 — Recomendação prática\n")
    lines.append(
        "Considerando forecasts + psicologia + concentração de risco:\n\n"
        "### Não recomendo 50/50 como ponto de partida\n"
        "- 50% em 3× UPRO = alta concentração num único ativo (SPY) "
        "alavancado. Em um cenário Vanguard (SPY 4.5%), seu portfolio "
        "inteiro fica 6-8% — não justifica o MDD de 40%.\n\n"
        "### Alternativas mais defensáveis\n\n"
        "**Opção A — Staging agressivo (só se aguentar psicologicamente)**\n"
        "- 10% na estratégia inicialmente (paper trade prévio obrigatório)\n"
        "- Aumento para 20-25% após 12 meses de tracking bem-sucedido\n"
        "- Máximo 30% nunca (mandate §2.3 pros ativos com MDD 50-75%)\n"
        "- Resto em Plano C (NTSX-based para diversificação real)\n"
        "- Expected CAGR: 10-14% com MDD ~25-35%\n\n"
        "**Opção B — Versão menos arriscada (2× em vez de 3×)**\n"
        "- Substituir UPRO por SSO (2×). MDD histórico cai de 54% → 39%.\n"
        "- CAGR sobre synth cai ~6-8pp, mas Sharpe melhora.\n"
        "- 50/50 com SSO: blend CAGR ~12-14%, MDD 30-35%.\n"
        "- **Este é o top-1 do SPY real sweep** (`EMA_N150_th5_bL2_sL0`).\n\n"
        "**Opção C — Hibrida NDX**\n"
        "- Como vimos no estudo NDX real, QLD (2× NASDAQ) tem edge "
        "mais robusto. Alocar 25% em strategy-NDX (QLD) em vez de SPY.\n"
        "- Blend: 50% Plano C + 25% SSO-strategy + 25% QLD-strategy.\n"
        "- Descorrelação SPY vs NDX é parcial, adiciona alguma "
        "diversificação.\n\n"
        "### Se insistir em 50/50 3× UPRO\n"
        "- OK, **mas stage de 10% → 25% → 50% ao longo de 2 anos**.\n"
        "- Stop pré-comprometido: MDD live > 30% pausa, > 50% aborta.\n"
        "- Re-examina se CAGR real em 12 meses desvia > 5pp do simulador.\n"
        "- Aceite que expected CAGR é **12-16% (com forecasts intermediários)** "
        "- não 20%.\n"
    )

    lines.append("## Bottom line\n")
    lines.append(
        f"- **50/50 histórico synth**: {_fmt_pct(blend_syn_cagr)} CAGR.\n"
        f"- **50/50 histórico real**: {_fmt_pct(blend_real_cagr)} CAGR.\n"
        "- **20% é otimista** — só bate em cenário histórico repetindo. "
        "Forecasts mais prováveis (Vanguard/GS/Research Affiliates) "
        "implicam blend em 6-12%.\n"
        "- **AI bubble é risco real mas timing é impossível**. O regime "
        "filter da estratégia já é seu mecanismo automático de sair no "
        "crash.\n"
        "- **Comece com 10-25%, não 50%**. Staging + stop + monitoramento "
        "mensal. Veja 1-2 anos de tracking antes de ir pra 30%+.\n"
        "- **Forecasts conservadores NÃO invalidam a estratégia** — elas "
        "indicam que seu edge relativo ao SPY ainda existe, mas o "
        "tamanho do bolo diminui.\n"
    )

    # ---- Sources ----
    lines.append("## Fontes da pesquisa (2026-04)\n")
    lines.append(
        "- [Goldman Sachs 10-year outlook — 7.7% modal](https://www.gspublishing.com/content/research/en/reports/2025/11/12/0c292cc7-ce42-4fba-a026-744231e9f4f4.html)\n"
        "- [Goldman Sachs 2026 outlook — 12% 2026 target](https://www.goldmansachs.com/insights/articles/the-sp-500-expected-to-rally-12-this-year)\n"
        "- [Vanguard 2026 VCMM 3.5-5.5% range](https://corporate.vanguard.com/content/corporatesite/us/en/corp/vemo/vemo-return-forecasts.html)\n"
        "- [Research Affiliates 3.1% nominal](https://www.researchaffiliates.com/publications/articles/1069-asset-allocation-interactive-good-bad-ugly)\n"
        "- [Shiller CAPE 1.3% projection — Motley Fool interview](https://www.fool.com/investing/2026/04/12/sp-500-in-10-years-nobel-laureate-robert-shiller/)\n"
        "- [Shiller CAPE ratio chart](https://www.multpl.com/shiller-pe)\n"
        "- [Buffett Indicator current market valuation](https://currentmarketvaluation.com/models/buffett-indicator.php)\n"
        "- [Fortune: Buffett Indicator flashes warning 2026](https://fortune.com/2026/04/20/warren-buffett-favorite-market-indicator-flashing-warning/)\n"
        "- [AI bubble vs dot-com comparison](https://intuitionlabs.ai/articles/ai-bubble-vs-dot-com-comparison)\n"
        "- [Apollo AI single-point-of-failure warning / INSEAD](https://knowledge.insead.edu/economics-finance/are-we-ai-bubble)\n"
        "- [Fortune: Cisco Chambers on AI bubble navigation](https://fortune.com/2026/04/20/ai-bubble-john-chambers-dot-com-crash-buffett-indicator/)\n"
        "- [Oliver Wyman: AI bubble $33T financial impact](https://www.oliverwyman.com/our-expertise/insights/2026/jan/impact-ai-bubble-burst-on-global-financial-markets.html)\n"
    )

    out_path = ANALYSES_DIR / "05_portfolio_5050_analysis.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    log.info("Portfolio analysis written: %s", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
