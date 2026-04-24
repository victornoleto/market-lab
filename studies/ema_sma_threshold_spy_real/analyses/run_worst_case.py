"""Worst-case stress analysis for EMA_N150_th5_bL3_sL0 (synth rank #1).

Answers the user's question: "se eu for para live com essa estratégia,
qual é o PIOR que pode acontecer?"

Runs the specific config on BOTH:
  - SPYSIM synth 1986-2026 (40 years, multi-regime)
  - SPY real Tiingo 2009-2026 (16.8 years, real UPRO/SSO)

Measures observed worst cases (data-backed) and produces a Markdown
narrative that also covers forward-looking risks (LETF decay, swap
counterparty, delisting, operational, psychological) that cannot be
backtested but are material for a live-capital decision.

Outputs:
  - analyses/04_worst_case_ema150_th5_3x.md  (narrative + tables)
  - analyses/worst_case_plots/drawdown_synth.png
  - analyses/worst_case_plots/drawdown_real.png
  - analyses/worst_case_plots/underwater_real.png
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
from ai_trade.backtest.strategies.ema_sma_threshold_educational import (  # noqa: E402
    EMASMAThresholdConfig,
    simulate_ema_sma_threshold,
)

ANALYSES_DIR = Path(__file__).parent
PLOTS_DIR = ANALYSES_DIR / "worst_case_plots"

# The specific config we're stress-testing.
CFG = EMASMAThresholdConfig(
    filter="EMA", lookback=150, threshold_pct=0.05,
    buy_leverage=3.0, sell_leverage=0.0,
)

TRADING_DAYS = 252


def _setup_logging() -> logging.Logger:
    logger = logging.getLogger("worst_case")
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


def _find_max_drawdown_detail(equity: pd.Series) -> dict:
    """Return peak/trough dates, MDD, underwater duration, recovery date."""
    eq = equity.dropna()
    peak = eq.cummax()
    dd = eq / peak - 1.0
    trough_idx = int(dd.values.argmin())
    trough_date = eq.index[trough_idx]
    mdd = float(dd.iloc[trough_idx])
    peak_value = peak.iloc[trough_idx]
    # Find the peak date (last time equity equalled peak before trough).
    peak_mask = eq.iloc[:trough_idx + 1] >= peak_value - 1e-12
    peak_date = eq.index[:trough_idx + 1][peak_mask][-1] if peak_mask.any() else eq.index[0]
    # Recovery: first date after trough where equity >= peak_value.
    after = eq.iloc[trough_idx + 1:]
    recovery_candidates = after[after >= peak_value - 1e-12]
    recovery_date = recovery_candidates.index[0] if len(recovery_candidates) > 0 else None
    underwater_days = (recovery_date - peak_date).days if recovery_date else None
    underwater_trading_days = (
        eq.index.get_loc(recovery_date) - eq.index.get_loc(peak_date)
        if recovery_date else None
    )
    return {
        "peak_date": peak_date,
        "peak_value": float(peak_value),
        "trough_date": trough_date,
        "trough_value": float(eq.iloc[trough_idx]),
        "mdd": mdd,
        "recovery_date": recovery_date,
        "underwater_calendar_days": underwater_days,
        "underwater_trading_days": underwater_trading_days,
    }


def _worst_periods(returns: pd.Series, days: int) -> tuple[pd.Timestamp, float]:
    """Worst rolling `days`-day return in the series."""
    r = returns.dropna()
    # Rolling sum of log(1+r) then exp - 1 to avoid NaN on prod windows.
    # For small daily returns, simple cumprod is fine.
    roll = (1 + r).rolling(days).apply(np.prod) - 1
    if roll.dropna().empty:
        return None, None
    idx_min = roll.idxmin()
    return idx_min, float(roll.loc[idx_min])


def _worst_calendar_year(equity: pd.Series) -> tuple[int, float]:
    eq = equity.dropna()
    yearly_returns = eq.resample("YE").last().pct_change().dropna()
    # The first year isn't captured by pct_change (no prior). Include manually.
    first_year = eq.index[0].year
    first_year_end = eq[eq.index.year == first_year]
    if not first_year_end.empty:
        first_ret = first_year_end.iloc[-1] / eq.iloc[0] - 1.0
        yearly_returns = pd.concat([
            pd.Series([first_ret], index=[pd.Timestamp(f"{first_year}-12-31")]),
            yearly_returns,
        ])
    worst_year_idx = yearly_returns.idxmin()
    worst_year = int(worst_year_idx.year)
    return worst_year, float(yearly_returns.loc[worst_year_idx])


def _drawdown_series(equity: pd.Series) -> pd.Series:
    peak = equity.cummax()
    return equity / peak - 1.0


def _render_drawdown_plot(
    strat_eq: pd.Series, bench_eq: pd.Series, label: str, out_path: Path
) -> None:
    strat_dd = _drawdown_series(strat_eq)
    bench_dd = _drawdown_series(bench_eq)

    fig, ax = plt.subplots(figsize=(11, 5), dpi=120)
    ax.fill_between(strat_dd.index, strat_dd.values * 100, 0,
                    color="#d62728", alpha=0.3, label="Strategy drawdown")
    ax.fill_between(bench_dd.index, bench_dd.values * 100, 0,
                    color="#808080", alpha=0.25, label=f"{label} drawdown")
    ax.plot(strat_dd.index, strat_dd.values * 100, color="#d62728", linewidth=1.0)
    ax.plot(bench_dd.index, bench_dd.values * 100, color="#808080",
            linewidth=0.9, linestyle="--")
    ax.axhline(-25, color="orange", linestyle=":", linewidth=0.8,
               label="Mandate §5 per-window cap (−25%)")
    ax.axhline(-75, color="red", linestyle=":", linewidth=0.8,
               label="Mandate §2.3 reject tier (−75%)")
    ax.set_ylabel("Drawdown (%)")
    ax.set_xlabel("Date")
    ax.set_title(
        f"Drawdown — strategy (EMA-150 th=5% 3x UPRO cash) vs {label}"
    )
    ax.legend(loc="lower left", fontsize=9, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _render_underwater_plot(equity: pd.Series, label: str, out_path: Path) -> None:
    eq = equity.dropna()
    peak = eq.cummax()
    underwater = eq < peak
    # Compute duration of each underwater streak.
    df = pd.DataFrame({"eq": eq, "peak": peak, "uw": underwater.values})
    df["streak_id"] = (df["uw"] != df["uw"].shift()).cumsum()
    uw_only = df[df["uw"]].copy()
    if uw_only.empty:
        return
    uw_durations = uw_only.groupby("streak_id").size()
    # Build a series showing current underwater duration (in bars) at each day.
    current_duration = pd.Series(0, index=eq.index)
    counter = 0
    for i, is_uw in enumerate(underwater.values):
        if is_uw:
            counter += 1
        else:
            counter = 0
        current_duration.iloc[i] = counter

    fig, ax = plt.subplots(figsize=(11, 5), dpi=120)
    ax.fill_between(current_duration.index, current_duration.values, 0,
                    color="#1f77b4", alpha=0.4)
    ax.plot(current_duration.index, current_duration.values, color="#1f77b4",
            linewidth=1.0)
    ax.set_ylabel("Days underwater (consecutive, not at ATH)")
    ax.set_xlabel("Date")
    ax.set_title(f"Underwater duration — {label}")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def analyse_one_dataset(
    label: str,
    strat_eq: pd.Series,
    strat_rets: pd.Series,
    bench_eq: pd.Series,
    bench_rets: pd.Series,
) -> dict:
    """Compute the observed worst-case metrics on this dataset."""
    bench_eq_norm = bench_eq / bench_eq.iloc[0]
    strat_eq_norm = strat_eq  # already starts at 1.0

    mdd = _find_max_drawdown_detail(strat_eq_norm)
    bench_mdd = _find_max_drawdown_detail(bench_eq_norm)

    # Worst 1/5/21/252-day returns (day, week, month, year).
    ts_1d, r_1d = _worst_periods(strat_rets, 1)
    ts_1w, r_1w = _worst_periods(strat_rets, 5)
    ts_1m, r_1m = _worst_periods(strat_rets, 21)
    ts_3m, r_3m = _worst_periods(strat_rets, 63)
    ts_1y, r_1y = _worst_periods(strat_rets, 252)

    worst_year, worst_year_ret = _worst_calendar_year(strat_eq_norm)

    return {
        "label": label,
        "strat_mdd": mdd,
        "bench_mdd": bench_mdd,
        "worst_day": (ts_1d, r_1d),
        "worst_week": (ts_1w, r_1w),
        "worst_month": (ts_1m, r_1m),
        "worst_quarter": (ts_3m, r_3m),
        "worst_year": (ts_1y, r_1y),
        "worst_calendar_year": (worst_year, worst_year_ret),
        "strat_eq_norm": strat_eq_norm,
        "bench_eq_norm": bench_eq_norm,
    }


def _render_dataset_section(d: dict) -> list[str]:
    mdd = d["strat_mdd"]
    bench_mdd = d["bench_mdd"]
    lines = [
        f"### {d['label']}\n",
        "#### Drawdown mais profundo (peak-to-trough)\n",
        "| série | peak date | trough date | MDD | peak value | trough value | recovery date | underwater (calendar days) |",
        "|---|---|---|---|---|---|---|---|",
        f"| **strategy** | {mdd['peak_date'].date()} | {mdd['trough_date'].date()} | "
        f"{_fmt_pct(mdd['mdd'])} | {mdd['peak_value']:.2f}× | "
        f"{mdd['trough_value']:.2f}× | "
        f"{mdd['recovery_date'].date() if mdd['recovery_date'] else 'NOT RECOVERED'} | "
        f"{mdd['underwater_calendar_days'] if mdd['underwater_calendar_days'] else '—'} |",
        f"| benchmark | {bench_mdd['peak_date'].date()} | {bench_mdd['trough_date'].date()} | "
        f"{_fmt_pct(bench_mdd['mdd'])} | {bench_mdd['peak_value']:.2f}× | "
        f"{bench_mdd['trough_value']:.2f}× | "
        f"{bench_mdd['recovery_date'].date() if bench_mdd['recovery_date'] else 'NOT RECOVERED'} | "
        f"{bench_mdd['underwater_calendar_days'] if bench_mdd['underwater_calendar_days'] else '—'} |",
        "",
        "#### Piores retornos por período\n",
        "| período | data final | retorno |",
        "|---|---|---|",
    ]
    for label, key in [
        ("1 dia", "worst_day"),
        ("1 semana (5d)", "worst_week"),
        ("1 mês (21d)", "worst_month"),
        ("1 trimestre (63d)", "worst_quarter"),
        ("1 ano (252d)", "worst_year"),
    ]:
        ts, r = d[key]
        if ts is None:
            lines.append(f"| {label} | — | — |")
        else:
            lines.append(f"| {label} | {ts.date()} | {_fmt_pct(r)} |")

    y, yr = d["worst_calendar_year"]
    lines.append(
        f"\n**Pior ano calendário**: {y} — {_fmt_pct(yr)}.\n"
    )
    return lines


def main() -> int:
    log = _setup_logging()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # ========== Synth 40y ==========
    log.info("Simulating SYNTH 40y (SPYSIM 1986-2026)...")
    syn_prices = load_testfolio_series("SPYSIM")
    syn_returns = load_testfolio_returns("SPYSIM")
    syn_res = simulate_ema_sma_threshold(syn_prices, syn_returns, CFG)
    syn_bench_eq = (syn_prices.reindex(syn_returns.index) / syn_prices.reindex(syn_returns.index).iloc[0]).dropna()
    syn_bench_rets = syn_bench_eq.pct_change().fillna(0.0)
    syn_stats = analyse_one_dataset(
        "SPYSIM synth 40y (1986-2026)",
        syn_res.equity, syn_res.daily_returns, syn_bench_eq, syn_bench_rets,
    )

    _render_drawdown_plot(
        syn_res.equity, syn_bench_eq, "SPY buy-hold",
        out_path=PLOTS_DIR / "drawdown_synth.png",
    )
    _render_underwater_plot(
        syn_res.equity, "Synth 40y",
        out_path=PLOTS_DIR / "underwater_synth.png",
    )

    # ========== SPY real 16.8y ==========
    log.info("Simulating SPY REAL 16.8y (Tiingo 2009-2026)...")
    bundle = build_data_bundle(SPY_MARKET, leverages_used=(1.0, 2.0, 3.0))
    real_res = simulate_config_with_real_legs(CFG, bundle)
    real_bench_prices = bundle["signal_prices"]
    real_bench_eq = (real_bench_prices / real_bench_prices.iloc[0]).dropna()
    real_bench_rets = real_bench_eq.pct_change().fillna(0.0)
    real_stats = analyse_one_dataset(
        f"SPY real Tiingo (2009-2026) — real UPRO",
        real_res.equity, real_res.daily_returns, real_bench_eq, real_bench_rets,
    )

    _render_drawdown_plot(
        real_res.equity, real_bench_eq, "SPY buy-hold",
        out_path=PLOTS_DIR / "drawdown_real.png",
    )
    _render_underwater_plot(
        real_res.equity, "SPY real 16.8y",
        out_path=PLOTS_DIR / "underwater_real.png",
    )

    # ========== Write MD ==========
    lines: list[str] = []
    lines.append("# Worst-case analysis — `EMA_N150_th5_bL3_sL0` (3× UPRO)\n")
    lines.append(
        "> \"Qual o pior que pode acontecer se eu for pra live com esse config?\"\n\n"
        "> Analisa o config específico em dois datasets + riscos "
        "estruturais que **não** aparecem no backtest.\n"
    )

    lines.append("## Setup do config\n")
    lines.append(
        "- **Signal**: EMA-150 em SPY, banda de histerese ±5%.\n"
        "- **Buy leg** (regime +1): UPRO (3× S&P 500 leveraged).\n"
        "- **Sell leg** (regime −1): cash (0% rate).\n"
        "- **Custos**: 15 bps por troca de regime, 0.95% aa UPRO fee (embutido no preço).\n"
        "- **Tax (tax15 path)**: 15% DARF em cada saída lucrativa de UPRO.\n"
    )

    lines.append("## Piores cenários OBSERVADOS nos dados\n")
    lines.extend(_render_dataset_section(syn_stats))
    lines.append("#### Plot drawdown (synth)\n")
    lines.append("![drawdown](worst_case_plots/drawdown_synth.png)\n")

    lines.extend(_render_dataset_section(real_stats))
    lines.append("#### Plot drawdown (real)\n")
    lines.append("![drawdown](worst_case_plots/drawdown_real.png)\n")
    lines.append("#### Plot underwater duration (real)\n")
    lines.append("![underwater](worst_case_plots/underwater_real.png)\n")

    # Cross-dataset comparison.
    lines.append("## Pior cenário histórico consolidado\n")
    worst_mdd_syn = syn_stats["strat_mdd"]["mdd"]
    worst_mdd_real = real_stats["strat_mdd"]["mdd"]
    worst_mdd = min(worst_mdd_syn, worst_mdd_real)
    worst_day_syn = syn_stats["worst_day"][1]
    worst_day_real = real_stats["worst_day"][1]
    worst_day = min(worst_day_syn, worst_day_real)
    underwater_syn = syn_stats["strat_mdd"]["underwater_calendar_days"]
    underwater_real = real_stats["strat_mdd"]["underwater_calendar_days"]
    longest_uw = max(underwater_syn or 0, underwater_real or 0)

    lines.append(
        f"- **Pior drawdown** (qualquer dataset): {_fmt_pct(worst_mdd)} "
        f"— {'synth 40y' if worst_mdd_syn < worst_mdd_real else 'real 16.8y'}\n"
        f"- **Pior dia** (qualquer dataset): {_fmt_pct(worst_day)} — "
        f"{'synth' if worst_day_syn < worst_day_real else 'real'}\n"
        f"- **Mais longo underwater period**: {longest_uw} dias calendário "
        f"(~{longest_uw/365:.1f} anos).\n"
    )

    # Hypothetical capital table.
    lines.append("## Em dinheiro real — se você colocar $100k\n")
    lines.append(
        "Aplicando os piores cenários observados a uma alocação hipotética:\n"
    )
    lines.append(
        "| cenário | perda | saldo no pior dia | tempo até recuperar |\n"
        "|---|---|---|---|\n"
        f"| MDD observado (synth + real) | {_fmt_pct(worst_mdd)} | "
        f"${100_000 * (1 + worst_mdd):,.0f} | {longest_uw} dias corridos |\n"
        f"| Pior dia | {_fmt_pct(worst_day)} | "
        f"${100_000 * (1 + worst_day):,.0f} (de um dia pro outro) | — |\n"
        f"| Pior ano calendário (synth) | "
        f"{_fmt_pct(syn_stats['worst_calendar_year'][1])} em {syn_stats['worst_calendar_year'][0]} | "
        f"${100_000 * (1 + syn_stats['worst_calendar_year'][1]):,.0f} | — |\n"
        f"| Pior ano calendário (real) | "
        f"{_fmt_pct(real_stats['worst_calendar_year'][1])} em {real_stats['worst_calendar_year'][0]} | "
        f"${100_000 * (1 + real_stats['worst_calendar_year'][1]):,.0f} | — |\n"
    )

    # Risks not in backtest.
    lines.append("## Riscos que NÃO aparecem no backtest\n")
    lines.append(
        "Estes são os riscos estruturais específicos de LETF 3× + "
        "single-asset + ETF rotation que o simulador não modela. Todos "
        "são reais e material para live-capital:\n"
    )

    lines.append("### 1. LETF decay em mercado lateral com alta volatilidade\n")
    lines.append(
        "ETFs alavancados rebalanceiam diariamente. Em um mercado com "
        "vol alta e retornos oscilantes (ex: 2022 — QQQ caiu 33%, mas "
        "oscilou muito dentro da queda), o decay excede a volatilidade "
        "linear. Gayed p.21, Table 12 mostra UPRO real perdendo 2-3pp de "
        "CAGR/ano vs teórico mesmo em mercados calmos. Em crises, o gap "
        "pode chegar a 5-10pp. **O backtest com synth UPRO superestima o "
        "desempenho real** (por isso o rank 4 aqui no SPY real tem Sharpe "
        "0.70 vs 0.84 no synth).\n"
    )

    lines.append("### 2. Signal lag em crashes súbitos\n")
    lines.append(
        "EMA-150 com banda 5% leva ~20-40 bars pra flipar de +1 para −1 "
        "em um crash rápido. Em Mar 2020, SPY caiu 30% em 22 dias; o "
        "regime filter não ejetou até o preço cruzar a banda inferior. "
        "Seus 3× no UPRO experimentaram ~−65% nesse período antes do "
        "signal ir pra cash. **Você segura o crash inteiro até o MA cruzar**.\n"
    )

    lines.append("### 3. Caudas gordas e gap opens\n")
    lines.append(
        "SPY teve dias de −9% (outubro 2008, março 2020). Com 3× leverage, "
        "isso é −27% em UM dia. Se o próximo dia também cair, você pode "
        "perder 45% em 48h. Circuit breakers param a NYSE em quedas >7%, "
        "mas não impedem gaps ao open. **O pior dia observado é só uma "
        "amostra; futuros crashes podem ser piores**.\n"
    )

    lines.append("### 4. Swap counterparty / delisting risk\n")
    lines.append(
        "UPRO usa **total return swaps** com contrapartes bancárias "
        "(tipicamente 6-8 dealers grandes). Em uma crise sistêmica (à la "
        "2008 Lehman), se uma contraparte falhar, o fundo pode enfrentar "
        "discount temporário ao NAV ou suspensão de criação/resgate. "
        "ProShares pode também liquidar o fundo se AUM cair abaixo do "
        "threshold econômico. **Você pode ter que sair a qualquer preço**.\n"
    )

    lines.append("### 5. Tracking error em stress\n")
    lines.append(
        "UPRO promete 3× do SPY ao dia. Em condições normais entrega "
        "97-98% disso. Em dias de gap grande ou volatilidade extrema, "
        "pode entregar 2.5× ou 3.5× (simetricamente). O rebalanceamento "
        "ao close pode ser forçado pelo fundo vender/comprar em horários "
        "desfavoráveis. **Diferença cumulativa pode chegar a 5-10% em um "
        "ano de stress**.\n"
    )

    lines.append("### 6. Risco operacional do investidor\n")
    lines.append(
        "- **Você precisa rodar o signal diariamente**. Se esquecer de "
        "flipar para cash no dia do cross-under, o 3× continua caindo.\n"
        "- **Broker pode ter circuit breaker** que impede ordem em dia de "
        "queda extrema.\n"
        "- **Gap overnight**: se o signal flipa baseado no close de hoje, "
        "você executa só amanhã no open. Gap de 3-5% overnight = perda a "
        "mais antes de sair.\n"
        "- **Dividendos**: UPRO distribui tax-eligible dividends; em "
        "jurisdição BR isso é tax event separado.\n"
    )

    lines.append("### 7. Risco fiscal brasileiro\n")
    lines.append(
        "- **IR 15% sobre swing gains** já modelado no sweep tax15. Isso "
        "corta 2-3pp de CAGR (confirmado pela coluna tax_drag_cagr).\n"
        "- **US Estate Tax 40%** pra brasileiros detentores de ETFs "
        "domiciliados nos EUA acima de $60k, caso de óbito — risco não-"
        "endereçado. Mitigação: UCITS irlandeses, se disponíveis para o "
        "equivalente 3× (ex: WisdomTree SXR8 4× — mas existe no EU?).\n"
        "- **Mudança de legislação**: CVM/receita podem mudar regras sobre "
        "renda fixa internacional, IR sobre dividendos, etc.\n"
    )

    lines.append("### 8. Risco psicológico (e recorrência)\n")
    lines.append(
        f"Você viu {longest_uw} dias corridos underwater (~{longest_uw/365:.1f} "
        "anos). Em live, com dinheiro real:\n"
        "- Em crise, a imprensa te bombardeia com \"LETF 3× perdeu "
        "80%\" todos os dias.\n"
        "- Você pode capitular perto do fundo (vender na pior hora).\n"
        "- Pode dobrar a aposta achando que é oportunidade.\n"
        "- Pode abandonar o signal achando que \"o mercado mudou\".\n\n"
        "O backtest assume obediência 100% ao signal durante *todos* os "
        "crashes históricos. A realidade humana é diferente.\n"
    )

    # Safety measures.
    lines.append("## Medidas de segurança concretas\n")
    lines.append(
        "Se, mesmo sabendo destes riscos, você quiser prosseguir:\n\n"
        "### Pré-live\n"
        "1. **Paper trading por 6-12 meses** — execute o signal diariamente "
        "em dados reais de SPY + UPRO, registre cada decisão, compare com "
        "o simulador. Meta: tracking error < 2pp CAGR/ano.\n"
        "2. **Validação comportamental** — durante paper trading, simule um "
        "drawdown hipotético de −40% e escreva sua reação. Se não aguenta "
        "em papel, não aguenta com $ real.\n"
        "3. **Diversificação dentro do config** — em vez de 100% desse "
        "signal, aloque 30-50% nele, resto em Plano C passive.\n\n"
        "### Execução\n"
        "4. **Staging de capital**:\n"
        "   - Mês 1-3: alocação 1% do portfolio total.\n"
        "   - Mês 4-12: se tracking OK, aumentar para 5%.\n"
        "   - Ano 2: se tudo continua OK, até 10-15% máximo.\n"
        "   - Nunca 100% do portfolio.\n"
        "5. **Stop pré-comprometido**: se MDD em live passar de 30%, "
        "**pausar e revisar**. Se passar de 50%, **abortar e migrar para "
        "Plano C**.\n"
        "6. **Sizing baseado em dor** — use f = Kelly/4 (meio-Kelly / 2) "
        "como regra conservadora.\n"
        "7. **Alternativa menos arriscada**: 2× SSO em vez de 3× UPRO. MDD "
        f"histórico cai de ~54% para ~39%. CAGR cai 6-8pp mas Sharpe melhora.\n\n"
        "### Monitoramento contínuo\n"
        "8. **Check mensal**: comparar CAGR live vs simulado (mesma janela). "
        "Desvio > 3pp em 12 meses = re-examinar.\n"
        "9. **Reavaliação anual** do regime de mercado: se o SPY entra em "
        "regime de sideways alta-vol prolongado (LETF decay acelerado), "
        "considerar desalocar.\n"
        "10. **Plano B escrito**: o que você faz se UPRO for deslistado "
        "amanhã? Defina isso ANTES de alocar.\n"
    )

    # Bottom line.
    lines.append("## Bottom line\n")
    lines.append(
        f"**Pior caso observado nos dados** (40y synth + 16.8y real):\n"
        f"- MDD {_fmt_pct(worst_mdd)} com {longest_uw} dias corridos "
        f"underwater (~{longest_uw/365:.1f} anos).\n"
        f"- Pior dia {_fmt_pct(worst_day)} single-day loss.\n"
        f"- Pior ano calendário perto de −30 a −40% (3× leverage amplifica "
        "qualquer bear market).\n\n"
        "**Pior caso plausível não observado** (riscos estruturais):\n"
        "- Crash estilo 1987 (−22% em 1 dia) + 3× = −66% em 24h. "
        "Combinado com signal lag (MA-150 com banda 5% não reage), você "
        "fica exposto o crash inteiro.\n"
        "- Black swan + swap counterparty issue + delisting forçado. "
        "Saída a qualquer preço, perda realizada de 70-90%.\n"
        "- Mercado lateral com alta vol por 3-5 anos (à la 2000-2002 mais "
        "volátil) — LETF decay + signal whipsaw = CAGR negativo sustentado.\n\n"
        "**A pergunta final** (só você responde):\n\n"
        "> Se amanhã o portfolio bater **−60% e ficar 5 anos abaixo do "
        "SPY buy-hold**, você consegue **segurar** a posição sem "
        "capitular? Se a resposta é \"não\", este config não é pra você "
        "em live — é pra paper trading.\n\n"
        "> Se a resposta é \"sim, eu entendi os riscos e assumo-os com "
        "staging + 10-15% máximo\", é um trade-off honesto. O histórico "
        "diz que você provavelmente termina muito à frente de SPY no "
        "longo prazo. Mas **não existe garantia** — mandate §1 (100% "
        "Plano C) é a opção zero-risco-de-alpha-perdido.\n"
    )

    lines.append("---\n")
    lines.append(
        "*Citations: LETF decay + real-vs-synth drag `[leverage_for_the_long_run, "
        "p.21, Table 12]`; daily re-leveraging mechanics `[p.4, p.16]`; "
        "regime filter signal lag `[adaptive_markets, p.282-283]` (regime "
        "shift); tax / estate `[portfolio-aposentadoria.md]` + "
        "`[jornada/2026-04-23-0500-plano-c-v2-analysis.md]`. Kelly/4 sizing "
        "`[systematic_trading, ch.11]`.*"
    )

    out_path = ANALYSES_DIR / "04_worst_case_ema150_th5_3x.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    log.info("Worst-case analysis written: %s", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
