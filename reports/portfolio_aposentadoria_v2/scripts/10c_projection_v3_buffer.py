"""Projeção v3 — realista com Lancer + buffer R$ 50k Mustang + manutenção R$ 2k incr.

Novas premissas vs v2:
1. Buffer Mustang: R$ 50k no momento da compra (emergency fund Mustang-
   specific). Fica em CDI (2% real), consumido em imprevistos.
2. Manutenção INCREMENTAL Mustang: R$ 2.000/mês (mais realista que v2 R$ 1.500)
   - Seguro + IPVA + combustível premium + manutenção regular + pneus
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path("/var/www/pessoal/ai-trade")
OUT_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "projecao_victor"

# Premissas
AGE_START = 30
START_MONTH = 5
RET_APOSENTADORIA = 0.06
RET_RESERVA = 0.02
RET_IMOVEL_BUCKET = 0.03
RET_MUSTANG_BUCKET = 0.03
DEPRECIACAO_MUSTANG = -0.08
VALOR_IMOVEL = 500_000
ENTRADA_VICTOR = 75_000
FINANC_VICTOR = 175_000
PARCELA_FINANC = 1_600
APORTE_FASE1 = 12_500
APORTE_FASE2 = 13_100
MES_COMPRA_IMOVEL = 36
VIDA_DESEJADA_MES = 12_500

# v3 novas
LANCER_SALE = 92_500
VALOR_MUSTANG = 320_000
MUSTANG_BUFFER = 50_000          # reserva imprevistos Mustang
MANUT_MUSTANG_INCR = 2_000        # R$ 2k/mês incremental (mais realista)

# Target total no bucket antes de comprar:
# valor_mustang + buffer - lancer_sale
# = 320k + 50k - 92.5k = R$ 277.5k
TARGET_BUCKET = VALOR_MUSTANG + MUSTANG_BUFFER - LANCER_SALE


def run_scenario(name: str, strategy: str = "split",
                 lancer: float = LANCER_SALE,
                 buffer: float = MUSTANG_BUFFER,
                 manut: float = MANUT_MUSTANG_INCR,
                 horizon_years: int = 35) -> tuple[pd.DataFrame, list]:
    target_bucket = VALOR_MUSTANG + buffer - lancer

    state = {
        "reserva": 75_000, "imovel_bucket": 45_000, "aposentadoria": 0,
        "mustang_bucket": 0, "mustang_reserve": 0,  # reserve separada pós-compra
        "imovel_owned": False, "mustang_owned": False, "mustang_value": 0,
        "financing_balance": 0,
    }
    events = []
    rows = []

    for month in range(1, horizon_years * 12 + 1):
        age = AGE_START + (START_MONTH - 1 + month - 1) / 12

        # Returns
        state["reserva"] *= (1 + RET_RESERVA / 12)
        state["imovel_bucket"] *= (1 + RET_IMOVEL_BUCKET / 12)
        state["aposentadoria"] *= (1 + RET_APOSENTADORIA / 12)
        state["mustang_bucket"] *= (1 + RET_MUSTANG_BUCKET / 12)
        state["mustang_reserve"] *= (1 + RET_RESERVA / 12)  # buffer rende como reserva
        if state["mustang_owned"]:
            state["mustang_value"] *= (1 + DEPRECIACAO_MUSTANG / 12)

        # Financing
        if state["financing_balance"] > 0:
            juros = state["financing_balance"] * 0.05 / 12
            amort = PARCELA_FINANC - juros
            if amort > 0:
                state["financing_balance"] = max(0, state["financing_balance"] - amort)

        # Contribution
        aporte_total = APORTE_FASE1 if month <= 6 else APORTE_FASE2
        aporte_liq = (aporte_total
                      - (PARCELA_FINANC if state["financing_balance"] > 0 else 0)
                      - (manut if state["mustang_owned"] else 0))

        # Allocate
        if not state["imovel_owned"]:
            state["imovel_bucket"] += 833
            state["aposentadoria"] += aporte_total - 833
        else:
            if strategy == "split":
                if not state["mustang_owned"]:
                    state["mustang_bucket"] += aporte_liq * 0.5
                    state["aposentadoria"] += aporte_liq * 0.5
                else:
                    state["aposentadoria"] += aporte_liq
            elif strategy == "priority":
                if not state["mustang_owned"]:
                    state["mustang_bucket"] += aporte_liq
                else:
                    state["aposentadoria"] += aporte_liq
            elif strategy == "none":
                state["aposentadoria"] += aporte_liq

        # Events
        if month == MES_COMPRA_IMOVEL and not state["imovel_owned"]:
            if state["imovel_bucket"] >= ENTRADA_VICTOR:
                state["imovel_bucket"] -= ENTRADA_VICTOR
                state["aposentadoria"] += state["imovel_bucket"]
                state["imovel_bucket"] = 0
                state["financing_balance"] = FINANC_VICTOR
                state["imovel_owned"] = True
                events.append((month, f"Compra imóvel: R$ {ENTRADA_VICTOR/1000:.0f}k + fin. R$ {FINANC_VICTOR/1000:.0f}k"))

        # Buy Mustang when bucket + lancer_sale cover valor + buffer
        if (state["imovel_owned"] and not state["mustang_owned"]
                and state["mustang_bucket"] >= target_bucket):
            # Vende Lancer + compra Mustang + separa buffer
            state["mustang_bucket"] -= (VALOR_MUSTANG - lancer)  # gastou em compra
            state["mustang_reserve"] = buffer                    # buffer separado
            state["mustang_bucket"] -= buffer                    # tira do bucket
            state["mustang_value"] = VALOR_MUSTANG
            state["aposentadoria"] += state["mustang_bucket"]    # sobra pra apos
            state["mustang_bucket"] = 0
            state["mustang_owned"] = True
            events.append((month, f"Vende Lancer R$ {lancer/1000:.0f}k + Mustang R$ {VALOR_MUSTANG/1000:.0f}k + buffer R$ {buffer/1000:.0f}k"))

        rows.append({
            "month": month, "age": age,
            "reserva": state["reserva"], "imovel_bucket": state["imovel_bucket"],
            "aposentadoria": state["aposentadoria"], "mustang_bucket": state["mustang_bucket"],
            "mustang_reserve": state["mustang_reserve"],
            "imovel_eq": VALOR_IMOVEL / 2 if state["imovel_owned"] else 0,
            "mustang_value": state["mustang_value"],
            "financing_balance": state["financing_balance"],
            "mustang_owned": state["mustang_owned"],
        })

    df = pd.DataFrame(rows)
    df["scenario"] = name
    return df, events


def analyze(df: pd.DataFrame, label: str) -> dict:
    buy = df[df["mustang_owned"] & (df["mustang_owned"].shift(1).fillna(False) == False)]
    age_buy = float(buy["age"].iloc[0]) if len(buy) > 0 else None
    a55 = df[df["age"] >= 55].iloc[0] if (df["age"] >= 55).any() else None
    a60 = df[df["age"] >= 60].iloc[0] if (df["age"] >= 60).any() else None
    return {
        "label": label, "mustang_age": age_buy,
        "apos_55": float(a55["aposentadoria"]) if a55 is not None else None,
        "apos_55_mes": float(a55["aposentadoria"] * 0.04 / 12) if a55 is not None else None,
        "apos_60": float(a60["aposentadoria"]) if a60 is not None else None,
        "apos_60_mes": float(a60["aposentadoria"] * 0.04 / 12) if a60 is not None else None,
    }


def main() -> None:
    print("=" * 80)
    print("PROJEÇÃO v3 — Lancer R$ 92,5k + Buffer Mustang R$ 50k + Manut R$ 2k/mês")
    print(f"Target Mustang bucket: R$ {(VALOR_MUSTANG + MUSTANG_BUFFER - LANCER_SALE)/1000:.0f}k")
    print("=" * 80)

    results = {}
    scenarios = [
        ("SPLIT v3 (Lancer + Buffer + R$ 2k manut)", "split", 92_500, 50_000, 2_000),
        ("SPLIT v3 — Buffer R$ 70k conservador", "split", 92_500, 70_000, 2_000),
        ("SPLIT v3 — Buffer R$ 50k + sinking fund", "split", 92_500, 50_000, 2_500),  # manut inclui sinking
        ("SPLIT v2 baseline (sem buffer)", "split", 92_500, 0, 1_500),
        ("SEM MUSTANG", "none", 0, 0, 0),
    ]

    for name, strat, lancer, buf, manut in scenarios:
        df, events = run_scenario(name, strategy=strat, lancer=lancer, buffer=buf, manut=manut)
        results[name] = {"df": df, "events": events}
        r = analyze(df, name)
        print(f"\n### {name}")
        print(f"  Target bucket: R$ {(VALOR_MUSTANG + buf - lancer)/1000:.0f}k | Buffer: R$ {buf/1000:.0f}k | Manut: R$ {manut}/mês")
        if r["mustang_age"]:
            print(f"  Mustang aos {r['mustang_age']:.1f} anos")
        if r["apos_55"]:
            print(f"  Aos 55y: R$ {r['apos_55']/1e6:.2f}M → R$ {r['apos_55_mes']/1000:.1f}k/mês")
        if r["apos_60"]:
            print(f"  Aos 60y: R$ {r['apos_60']/1e6:.2f}M → R$ {r['apos_60_mes']/1000:.1f}k/mês")

    # Gráfico
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    ax1 = axes[0]
    colors = {
        "SPLIT v3 (Lancer + Buffer + R$ 2k manut)": "#C73E1D",
        "SPLIT v3 — Buffer R$ 70k conservador": "#F18F01",
        "SPLIT v2 baseline (sem buffer)": "#2E86AB",
        "SEM MUSTANG": "#6FBF73",
    }

    for name, color in colors.items():
        if name in results:
            df = results[name]["df"]
            ax1.plot(df["age"], df["aposentadoria"] / 1e6,
                     label=name.replace(" (Lancer + Buffer + R$ 2k manut)", " RECOMENDADO")
                          .replace(" (sem buffer)", ""),
                     linewidth=2.0, color=color)

    ax1.axhline(y=3.75, color="gray", linestyle="--", alpha=0.5,
                label="R$ 3,75M = R$ 12,5k/mês (vida atual)")
    ax1.axvline(55, color="green", linestyle=":", alpha=0.5)
    ax1.axvline(60, color="green", linestyle=":", alpha=0.5)
    ax1.set_title("Aposentadoria — impacto do buffer Mustang + manutenção realista",
                  fontsize=12)
    ax1.set_xlabel("Idade (anos)")
    ax1.set_ylabel("R$ milhões em aposentadoria")
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(30, 65)

    # Right: Mustang bucket + reserve evolution
    ax2 = axes[1]
    best_df = results["SPLIT v3 (Lancer + Buffer + R$ 2k manut)"]["df"]
    ax2.plot(best_df["age"], best_df["mustang_bucket"] / 1000,
             label="Mustang bucket (pré-compra)", linewidth=2, color="#F18F01")
    ax2.plot(best_df["age"], best_df["mustang_reserve"] / 1000,
             label="Mustang reserve (R$ 50k buffer pós-compra)", linewidth=2, color="#C73E1D")
    ax2.plot(best_df["age"], best_df["mustang_value"] / 1000,
             label="Valor Mustang (depreciando 8%/ano)", linewidth=2, color="#6FBF73")
    ax2.axhline(y=277.5, color="orange", linestyle=":", alpha=0.5,
                label="Target bucket: R$ 277,5k")
    ax2.axhline(y=50, color="red", linestyle=":", alpha=0.5,
                label="Buffer: R$ 50k")
    ax2.set_title("Dinâmica do Mustang v3 — bucket → compra → reserve",
                  fontsize=12)
    ax2.set_xlabel("Idade (anos)")
    ax2.set_ylabel("R$ mil")
    ax2.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(30, 50)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "projecao_v3_buffer.png", dpi=130, bbox_inches="tight")
    print(f"\nGráfico salvo: {OUT_DIR / 'projecao_v3_buffer.png'}")

    # CSV
    summary = [analyze(results[n]["df"], n) for n in results]
    pd.DataFrame(summary).to_csv(OUT_DIR / "scenarios_v3_summary.csv", index=False)


if __name__ == "__main__":
    main()
