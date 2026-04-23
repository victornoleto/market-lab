"""Projeção Victor v2 — atualizada com Lancer HL-T 2018.

Incorpora informação nova: Victor tem Lancer HL-T 2018 que pode vender por
R$ 85-100k (FIPE 2026 ~R$ 70k, mais R$ 15-30k de modifications premium).

Impactos na projeção anterior:
1. Target Mustang bucket reduzido: R$ 320k - R$ 85k venda Lancer = R$ 235k
   (vs R$ 320k anterior)
2. Manutenção MUSTANG vira INCREMENTAL (vs Lancer) = R$ 1.500/mês em vez de
   R$ 2.500/mês absoluto (Lancer já estava na vida atual)

Resultado: Mustang viável BEM mais cedo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path("/var/www/pessoal/ai-trade")
OUT_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "projecao_victor"

# Premissas (iguais a 10_projection_victor.py)
AGE_START = 30
START_YEAR = 2026
START_MONTH = 5
RET_APOSENTADORIA = 0.06
RET_RESERVA = 0.02
RET_IMOVEL_BUCKET = 0.03
RET_MUSTANG_BUCKET = 0.03
DEPRECIACAO_MUSTANG = -0.08
VALOR_IMOVEL = 500_000
ENTRADA_PCT = 0.30
ENTRADA_VICTOR = VALOR_IMOVEL * ENTRADA_PCT / 2
FINANC_VICTOR = VALOR_IMOVEL * (1 - ENTRADA_PCT) / 2
PARCELA_FINANC = 1_600
APORTE_FASE1 = 12_500
APORTE_FASE2 = 13_100
MES_COMPRA_IMOVEL = 36
VIDA_DESEJADA_MES = 12_500

# NOVAS premissas
LANCER_SALE_CONSERV = 85_000   # conservador
LANCER_SALE_BASE = 92_500       # base (médio de R$ 85-100k)
LANCER_SALE_OTIMISTA = 100_000  # otimista

# Mustang list price
VALOR_MUSTANG = 320_000

# Manutenção INCREMENTAL (Mustang vs Lancer)
# Lancer HL-T 2018: ~R$ 1k/mês (já em vida atual R$ 12,5k)
# Mustang 2018 (imported, V8 ou 4cil turbo): ~R$ 2,5k/mês absoluto
# INCREMENTAL: ~R$ 1.500/mês extra vs Lancer
MANUT_MUSTANG_INCR = 1_500


def run_scenario(
    scenario_name: str,
    mustang_strategy: str = "split",
    lancer_sale: float = LANCER_SALE_BASE,
    manut_incr: float = MANUT_MUSTANG_INCR,
    horizon_years: int = 35,
) -> tuple[pd.DataFrame, list]:
    """Simulação mensal com Lancer sale + incremental maintenance."""
    target_mustang = VALOR_MUSTANG - lancer_sale  # R$ 235k base, 220 optim, 250 cons

    state = {
        "reserva": 75_000,
        "imovel_bucket": 45_000,
        "aposentadoria": 0,
        "mustang_bucket": 0,
        "imovel_owned": False,
        "mustang_owned": False,
        "mustang_value": 0,
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
        if state["mustang_owned"]:
            state["mustang_value"] *= (1 + DEPRECIACAO_MUSTANG / 12)

        # Financing
        if state["financing_balance"] > 0:
            juros = state["financing_balance"] * 0.05 / 12
            amort = PARCELA_FINANC - juros
            if amort > 0:
                state["financing_balance"] = max(0, state["financing_balance"] - amort)

        # Monthly contribution
        aporte_total = APORTE_FASE1 if month <= 6 else APORTE_FASE2
        aporte_liq = (
            aporte_total
            - (PARCELA_FINANC if state["financing_balance"] > 0 else 0)
            - (manut_incr if state["mustang_owned"] else 0)
        )

        # Allocate
        if not state["imovel_owned"]:
            state["imovel_bucket"] += 833
            state["aposentadoria"] += aporte_total - 833
        else:
            if mustang_strategy == "split":
                if not state["mustang_owned"]:
                    state["mustang_bucket"] += aporte_liq * 0.5
                    state["aposentadoria"] += aporte_liq * 0.5
                else:
                    state["aposentadoria"] += aporte_liq
            elif mustang_strategy == "priority":
                if not state["mustang_owned"]:
                    state["mustang_bucket"] += aporte_liq
                else:
                    state["aposentadoria"] += aporte_liq
            elif mustang_strategy == "delay":
                months_since = month - MES_COMPRA_IMOVEL
                if months_since < 120:
                    state["aposentadoria"] += aporte_liq
                elif not state["mustang_owned"]:
                    state["mustang_bucket"] += aporte_liq
                else:
                    state["aposentadoria"] += aporte_liq
            elif mustang_strategy == "none":
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

        # Buy Mustang when bucket >= target (lancer_sale supplements at purchase)
        if (state["imovel_owned"] and not state["mustang_owned"]
                and state["mustang_bucket"] >= target_mustang):
            # Supplement with Lancer sale
            total_available = state["mustang_bucket"] + lancer_sale
            state["mustang_bucket"] -= target_mustang
            state["mustang_value"] = VALOR_MUSTANG
            state["aposentadoria"] += state["mustang_bucket"]
            state["mustang_bucket"] = 0
            state["mustang_owned"] = True
            events.append((month, f"Vende Lancer R$ {lancer_sale/1000:.0f}k + compra Mustang R$ {VALOR_MUSTANG/1000:.0f}k"))

        rows.append({
            "month": month, "age": age,
            "reserva": state["reserva"], "imovel_bucket": state["imovel_bucket"],
            "aposentadoria": state["aposentadoria"], "mustang_bucket": state["mustang_bucket"],
            "imovel_eq": VALOR_IMOVEL / 2 if state["imovel_owned"] else 0,
            "mustang_value": state["mustang_value"],
            "financing_balance": state["financing_balance"],
            "mustang_owned": state["mustang_owned"],
        })

    df = pd.DataFrame(rows)
    df["scenario"] = scenario_name
    return df, events


def analyze(df: pd.DataFrame, label: str, lancer_sale: float):
    mustang_buy_row = df[df["mustang_owned"] & (df["mustang_owned"].shift(1).fillna(False) == False)]
    mustang_age = mustang_buy_row["age"].iloc[0] if len(mustang_buy_row) > 0 else None

    apos_55 = df[df["age"] >= 55].iloc[0] if (df["age"] >= 55).any() else None
    apos_60 = df[df["age"] >= 60].iloc[0] if (df["age"] >= 60).any() else None

    result = {
        "label": label, "lancer_sale": lancer_sale,
        "mustang_age": float(mustang_age) if mustang_age is not None else None,
        "apos_55_nest": float(apos_55["aposentadoria"]) if apos_55 is not None else None,
        "apos_55_renda": float(apos_55["aposentadoria"] * 0.04 / 12) if apos_55 is not None else None,
        "apos_60_nest": float(apos_60["aposentadoria"]) if apos_60 is not None else None,
        "apos_60_renda": float(apos_60["aposentadoria"] * 0.04 / 12) if apos_60 is not None else None,
    }
    return result


def main() -> None:
    print("=" * 80)
    print("PROJEÇÃO v2 — com Lancer HL-T 2018 na equação")
    print(f"FIPE fev/2026: R$ 70k | Venda modificada: R$ 85-100k")
    print(f"Target Mustang bucket reduzido: R$ 235k (era R$ 320k)")
    print(f"Manutenção Mustang INCREMENTAL: R$ 1.500/mês (era R$ 2.500 absoluto)")
    print("=" * 80)

    # Cenários x Lancer sale values x strategies
    results = {}
    scenarios_meta = [
        ("SPLIT 50/50 (Lancer R$ 85k conserv)", "split", 85_000),
        ("SPLIT 50/50 (Lancer R$ 92,5k base)", "split", 92_500),
        ("SPLIT 50/50 (Lancer R$ 100k otim)", "split", 100_000),
        ("MUSTANG priority (Lancer R$ 92,5k)", "priority", 92_500),
        ("DELAY +10y (Lancer R$ 92,5k)", "delay", 92_500),
        ("SEM MUSTANG (baseline)", "none", 0),
    ]

    for name, strat, lancer in scenarios_meta:
        df, events = run_scenario(name, mustang_strategy=strat, lancer_sale=lancer)
        results[name] = {"df": df, "events": events}
        r = analyze(df, name, lancer)
        print(f"\n### {name}")
        if r["mustang_age"]:
            print(f"  Mustang aos {r['mustang_age']:.1f} anos (era 37,7 sem Lancer no SPLIT)")
        else:
            print(f"  Mustang: sem compra")
        if r["apos_55_nest"]:
            print(f"  Aos 55y: R$ {r['apos_55_nest']/1e6:.2f}M → R$ {r['apos_55_renda']/1000:.1f}k/mês "
                  f"(vs R$ 21,0k SPLIT v1)")
        if r["apos_60_nest"]:
            print(f"  Aos 60y: R$ {r['apos_60_nest']/1e6:.2f}M → R$ {r['apos_60_renda']/1000:.1f}k/mês")

    # ====================================================================
    # Gráfico comparativo v1 vs v2 (mustang timing)
    # ====================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Left: Mustang bucket growth — compare v1 (no Lancer) vs v2 (with Lancer)
    from importlib import import_module
    sys.path.insert(0, str(REPO / "reports" / "portfolio_aposentadoria_v2" / "scripts"))
    v1_mod = import_module("10_projection_victor")
    v1_df, _ = v1_mod.run_scenario("v1 SPLIT (sem Lancer)", mustang_strategy="split", horizon_years=15)

    # v2 SPLIT base
    v2_df = results["SPLIT 50/50 (Lancer R$ 92,5k base)"]["df"].head(180)

    ax1.plot(v1_df["age"], v1_df["mustang_bucket"] / 1000,
             label="v1: SEM Lancer (target R$ 320k)", color="red", linewidth=2.2, linestyle="--")
    ax1.plot(v2_df["age"], v2_df["mustang_bucket"] / 1000,
             label="v2: COM Lancer R$ 92,5k (target R$ 227,5k)", color="green", linewidth=2.2)
    ax1.axhline(y=320, color="red", linestyle=":", alpha=0.5, label="Target v1: R$ 320k")
    ax1.axhline(y=227.5, color="green", linestyle=":", alpha=0.5, label="Target v2: R$ 227,5k")
    ax1.set_title("Crescimento do Mustang bucket — SPLIT 50/50\nv1 (sem Lancer) vs v2 (com Lancer R$ 92,5k)",
                  fontsize=12)
    ax1.set_xlabel("Idade (anos)")
    ax1.set_ylabel("R$ mil em Mustang bucket (reais de 2026)")
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(30, 45)

    # Right: Aposentadoria comparativa v1 vs v2 variantes
    colors = {"SPLIT 50/50 (Lancer R$ 85k conserv)": "#F18F01",
              "SPLIT 50/50 (Lancer R$ 92,5k base)": "#C73E1D",
              "SPLIT 50/50 (Lancer R$ 100k otim)": "#6FBF73",
              "SEM MUSTANG (baseline)": "#2E86AB"}
    for name, color in colors.items():
        if name in results:
            df = results[name]["df"]
            ax2.plot(df["age"], df["aposentadoria"] / 1e6, label=name, linewidth=2.0, color=color)

    # Add v1 SPLIT for comparison
    v1_full, _ = v1_mod.run_scenario("v1 SPLIT (sem Lancer)", mustang_strategy="split", horizon_years=35)
    ax2.plot(v1_full["age"], v1_full["aposentadoria"] / 1e6,
             label="v1 SPLIT (sem Lancer)", linewidth=2.0, color="black", linestyle="--", alpha=0.7)

    ax2.axhline(y=3.75, color="gray", linestyle="--", alpha=0.5, label="R$ 12,5k/mês @ SWR 4%")
    ax2.axvline(55, color="green", linestyle=":", alpha=0.5)
    ax2.axvline(60, color="green", linestyle=":", alpha=0.5)
    ax2.set_title("Aposentadoria comparativa — v1 vs v2 (c/ Lancer)",
                  fontsize=12)
    ax2.set_xlabel("Idade (anos)")
    ax2.set_ylabel("R$ milhões em aposentadoria")
    ax2.legend(loc="upper left", fontsize=8, framealpha=0.9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(30, 65)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "projecao_v2_com_lancer.png", dpi=130, bbox_inches="tight")
    print(f"\nGráfico salvo: {OUT_DIR / 'projecao_v2_com_lancer.png'}")

    # Save summary CSV
    summary_rows = []
    for name, strat, lancer in scenarios_meta:
        df = results[name]["df"]
        r = analyze(df, name, lancer)
        summary_rows.append(r)
    pd.DataFrame(summary_rows).to_csv(OUT_DIR / "scenarios_v2_summary.csv", index=False)


if __name__ == "__main__":
    main()
