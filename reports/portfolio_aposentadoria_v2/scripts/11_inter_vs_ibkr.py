"""Comparação Inter Internacional vs Interactive Brokers em 10-30 anos.

Modelo:
- Aporte mensal em R$ convertido pra USD
- Inter: spread FX 0,99-1,50% (usar 1,25% médio) na compra; fees trading zero
- IBKR: spread FX ~0% (interbank mid) + fee fixo $2/conversão; fees trading baixos
- Retorno do portfolio: V3_1 v3.5 @ 6% real em BRL (conservador)

Dimensões testadas:
- Aporte mensal: R$ 2k, R$ 5k, R$ 10k, R$ 13,1k (plano caixinhas)
- Horizonte: 10, 20, 30 anos
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT_DIR = Path("/var/www/pessoal/ai-trade/reports/portfolio_aposentadoria_v2/projecao_victor")

# Premissas
BRL_USD_INITIAL = 5.50  # R$/USD em 2026 (em termos reais, constante)
RET_REAL = 0.06         # 6% real anual do portfolio V3_1 v3.5

# Custos por broker (em % do valor convertido)
# Inter: spread 1,25% (médio entre 0,99-1,50%)
# IBKR: spread ~0.02% (quase zero) + $2 fixo por conversão (trans tiered)
COST_INTER_PCT = 0.0125
COST_IBKR_PCT = 0.0002   # 0,02% (Taxa bem perto do interbank)
COST_IBKR_FIX_USD = 2.0


def simulate(
    aporte_brl: float,
    horizon_years: int,
    broker: str = "inter",
    ret_real_anual: float = RET_REAL,
) -> dict:
    """Simula acumulação mensal num dos dois brokers."""
    months = horizon_years * 12
    ret_mensal = (1 + ret_real_anual) ** (1 / 12) - 1

    patrimonio = 0.0
    custo_total_brl = 0.0

    for m in range(months):
        # Aporte em USD efetivo (pós custo FX)
        aporte_usd_gross = aporte_brl / BRL_USD_INITIAL
        if broker == "inter":
            custo_brl = aporte_brl * COST_INTER_PCT
            aporte_usd_net = (aporte_brl - custo_brl) / BRL_USD_INITIAL
        elif broker == "ibkr":
            custo_brl_pct = aporte_brl * COST_IBKR_PCT
            custo_brl_fix = COST_IBKR_FIX_USD * BRL_USD_INITIAL
            custo_brl = custo_brl_pct + custo_brl_fix
            aporte_usd_net = (aporte_brl - custo_brl) / BRL_USD_INITIAL
        else:
            raise ValueError(broker)

        # Aplicar retorno mensal + adicionar aporte líquido
        patrimonio = patrimonio * (1 + ret_mensal) + aporte_usd_net
        custo_total_brl += custo_brl

    # Valor final em R$ (multiplicando USD por FX constante — real terms)
    patrimonio_brl = patrimonio * BRL_USD_INITIAL
    total_aportado = aporte_brl * months
    total_investido_pos_fx = total_aportado - custo_total_brl

    return {
        "broker": broker,
        "aporte_brl": aporte_brl,
        "horizon_y": horizon_years,
        "patrimonio_usd": patrimonio,
        "patrimonio_brl": patrimonio_brl,
        "total_aportado_brl": total_aportado,
        "custo_fx_total_brl": custo_total_brl,
        "retorno_total_pct": (patrimonio_brl / total_aportado - 1) * 100,
    }


def main() -> None:
    # Cenário principal: aporte R$ 13.100 (plano caixinhas pós imóvel)
    print("=" * 80)
    print("Comparação Inter vs IBKR — aporte mensal plano caixinhas")
    print(f"Premissas: aporte R$ 13.100/mês | FX R$ {BRL_USD_INITIAL:.2f}/USD | retorno {RET_REAL:.0%}/ano real")
    print(f"Inter: spread FX {COST_INTER_PCT:.2%} | IBKR: spread {COST_IBKR_PCT:.2%} + ${COST_IBKR_FIX_USD} fixo/conversão")
    print("=" * 80)

    # Table results
    results = []
    for horizon in [10, 15, 20, 25, 30]:
        for aporte in [2_000, 5_000, 10_000, 13_100]:
            for broker in ["inter", "ibkr"]:
                r = simulate(aporte, horizon, broker)
                results.append(r)

    df = pd.DataFrame(results)

    # Print table for aporte R$ 13.100
    print(f"\n{'Horizonte':<10} {'Inter (R$)':<15} {'IBKR (R$)':<15} {'Diff R$':<15} {'Diff %':<10}")
    for horizon in [10, 15, 20, 25, 30]:
        inter = df[(df['aporte_brl'] == 13_100) & (df['horizon_y'] == horizon) & (df['broker'] == 'inter')].iloc[0]
        ibkr = df[(df['aporte_brl'] == 13_100) & (df['horizon_y'] == horizon) & (df['broker'] == 'ibkr')].iloc[0]
        diff = ibkr['patrimonio_brl'] - inter['patrimonio_brl']
        diff_pct = (ibkr['patrimonio_brl'] / inter['patrimonio_brl'] - 1) * 100
        print(f"{horizon}y{'':<7} R$ {inter['patrimonio_brl']/1e6:.2f}M{'':<5} "
              f"R$ {ibkr['patrimonio_brl']/1e6:.2f}M{'':<5} "
              f"R$ {diff/1e3:.1f}k{'':<6} "
              f"+{diff_pct:.2f}%")

    df.to_csv(OUT_DIR / "inter_vs_ibkr_all.csv", index=False)

    # ====================================================================
    # GRÁFICO 1: Patrimônio total 30 anos — aporte R$ 13.100
    # ====================================================================
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Left: linha do tempo patrimônio Inter vs IBKR (R$ 13.100 aporte)
    ax1 = axes[0]
    years_plot = np.arange(0, 30 * 12 + 1) / 12
    patr_inter = []
    patr_ibkr = []
    patr_inter_cum = 0.0
    patr_ibkr_cum = 0.0
    ret_m = (1 + RET_REAL) ** (1/12) - 1

    for m in range(30 * 12):
        # Inter
        custo_inter = 13_100 * COST_INTER_PCT
        aporte_inter = (13_100 - custo_inter) / BRL_USD_INITIAL
        patr_inter_cum = patr_inter_cum * (1 + ret_m) + aporte_inter
        patr_inter.append(patr_inter_cum * BRL_USD_INITIAL)

        # IBKR
        custo_ibkr = 13_100 * COST_IBKR_PCT + COST_IBKR_FIX_USD * BRL_USD_INITIAL
        aporte_ibkr = (13_100 - custo_ibkr) / BRL_USD_INITIAL
        patr_ibkr_cum = patr_ibkr_cum * (1 + ret_m) + aporte_ibkr
        patr_ibkr.append(patr_ibkr_cum * BRL_USD_INITIAL)

    patr_inter = [0] + patr_inter
    patr_ibkr = [0] + patr_ibkr

    ax1.plot(years_plot, np.array(patr_inter) / 1e6, label="Inter Internacional (spread 1,25%)",
             linewidth=2.2, color="#F18F01")
    ax1.plot(years_plot, np.array(patr_ibkr) / 1e6, label="Interactive Brokers (spread ~0% + $2 fixo)",
             linewidth=2.2, color="#2E86AB")
    ax1.fill_between(years_plot, np.array(patr_inter) / 1e6, np.array(patr_ibkr) / 1e6,
                     alpha=0.15, color="green", label="Economia IBKR")

    ax1.set_title("Patrimônio acumulado — aporte R$ 13.100/mês\n(em R$ reais de 2026, portfolio 6% real/ano)",
                  fontsize=12)
    ax1.set_xlabel("Anos de aporte")
    ax1.set_ylabel("R$ milhões")
    ax1.legend(loc="upper left", fontsize=10, framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 30)

    # Annotate diff at key horizons
    for y in [10, 20, 30]:
        idx = y * 12
        diff = (patr_ibkr[idx] - patr_inter[idx]) / 1000
        ax1.annotate(
            f"+R$ {diff:.0f}k",
            xy=(y, patr_ibkr[idx] / 1e6),
            xytext=(y + 0.5, patr_ibkr[idx] / 1e6 + 0.3),
            fontsize=10, color="green",
            arrowprops=dict(arrowstyle="->", color="green", alpha=0.6),
        )

    # Right: custo FX acumulado por aporte
    ax2 = axes[1]
    aporte_values = [2_000, 5_000, 10_000, 13_100]
    width = 0.35
    x_pos = np.arange(len(aporte_values))

    for horizon, alpha in [(10, 0.4), (20, 0.7), (30, 1.0)]:
        inter_cust = [df[(df['aporte_brl'] == a) & (df['horizon_y'] == horizon) & (df['broker'] == 'inter')].iloc[0]['custo_fx_total_brl']
                      for a in aporte_values]
        ibkr_cust = [df[(df['aporte_brl'] == a) & (df['horizon_y'] == horizon) & (df['broker'] == 'ibkr')].iloc[0]['custo_fx_total_brl']
                     for a in aporte_values]
        economia = [(i - k) / 1000 for i, k in zip(inter_cust, ibkr_cust)]
        ax2.bar(x_pos + (horizon / 40 - 0.5) * width, economia, width * 0.7,
                label=f"{horizon}y", alpha=alpha, color="green")

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([f"R$ {a/1000:.1f}k" for a in aporte_values])
    ax2.set_title("Economia total com IBKR vs Inter (por aporte mensal × horizonte)",
                  fontsize=12)
    ax2.set_xlabel("Aporte mensal")
    ax2.set_ylabel("Economia acumulada (R$ mil)")
    ax2.legend(title="Horizonte", fontsize=10, framealpha=0.9)
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "inter_vs_ibkr.png", dpi=130, bbox_inches="tight")
    print(f"\nGráfico salvo: {OUT_DIR / 'inter_vs_ibkr.png'}")

    # ====================================================================
    # Break-even analysis: em qual aporte IBKR começa a valer?
    # ====================================================================
    print("\n=== Break-even: em qual aporte IBKR começa a superar Inter? ===")
    for aporte in [500, 1_000, 2_000, 3_000, 5_000]:
        r_inter = simulate(aporte, 20, "inter")
        r_ibkr = simulate(aporte, 20, "ibkr")
        diff_pct = (r_ibkr['patrimonio_brl'] / r_inter['patrimonio_brl'] - 1) * 100
        winner = "IBKR" if r_ibkr['patrimonio_brl'] > r_inter['patrimonio_brl'] else "Inter"
        print(f"  Aporte R$ {aporte:>6,.0f}/mês, 20y: diff {diff_pct:+.2f}% — winner {winner}")


if __name__ == "__main__":
    main()
