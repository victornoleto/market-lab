"""Projeção de vida financeira — Victor (30 anos, R$ 120k atual).

Simula 3 objetivos integrados:
1. Imóvel R$ 500k em 2029 (entrada Victor R$ 75k, financiamento R$ 175k)
2. Ford Mustang 2018 R$ 320k (pós-imóvel)
3. Aposentadoria 55-60 anos com qualidade de vida ≥ R$ 12,5k/mês

Todas as valores em R$ REAIS (termos de 2026, descontando inflação).

Premissas de retorno real anual:
- Aposentadoria (V3_1 v3.5): 6% real (conservador pro 10-12% nominal USD - 5% inflação BR)
- Reserva emergência (CDI líquido): 2% real
- RF imóvel/Mustang (pré-fixado): 3% real
- Imóvel físico: 0% real (preserva valor, não produz return)
- Mustang: -8% real/ano depreciação

Inflação estimada: IPCA 5%/ano (implícita, não aplicada aos valores reais)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

REPO = Path("/var/www/pessoal/ai-trade")
OUT_DIR = REPO / "reports" / "portfolio_aposentadoria_v2" / "projecao_victor"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Premissas
# ============================================================================
AGE_START = 30
START_YEAR = 2026
START_MONTH = 5  # Maio 2026 (início da Fase 1 conforme plano caixinhas)

# Retornos reais anuais (conservadores)
RET_APOSENTADORIA = 0.06   # V3_1 v3.5 (6% real BRL, conservador)
RET_RESERVA = 0.02          # CDI líquido pós-IR
RET_IMOVEL_BUCKET = 0.03   # Pré-fixado bom emissor
RET_MUSTANG_BUCKET = 0.03  # RF similar
DEPRECIACAO_MUSTANG = -0.08  # 8% ao ano (carro usado)

# Objetivos em R$ reais de 2026
VALOR_IMOVEL = 500_000
ENTRADA_PCT = 0.30
ENTRADA_VICTOR = VALOR_IMOVEL * ENTRADA_PCT / 2  # 75k (esposa paga metade)
FINANC_VICTOR = VALOR_IMOVEL * (1 - ENTRADA_PCT) / 2  # R$ 175k (metade do financiamento)
TAXA_FINANC = 0.105  # 10.5% a.a. nominal típico; ~5% real
PRAZO_FINANC_ANOS = 30

VALOR_MUSTANG = 320_000
MANUT_MUSTANG_MES = 2_500  # IPVA + seguro + gasolina + manutenção mensal

VIDA_DESEJADA_MES = 12_500  # Qualidade de vida atual

# Aportes mensais por fase (do plano caixinhas)
APORTE_FASE1 = 12_500     # Mai-Out/26
APORTE_FASE2 = 13_100     # Nov/26+

# Compra imóvel
MES_COMPRA_IMOVEL = 36    # Abr/2029 (3 anos após Mai/26)

# Parcela financiamento Victor (SAC 30 anos, ~R$ 175k a 10,5%)
# Primeira parcela SAC ~= (175k/360) + 175k × 10,5%/12 = 486 + 1531 = 2017
# Vou usar Price simplificado pra ter parcela constante real
# Price: PMT = P × [i(1+i)^n] / [(1+i)^n - 1]
# i = 0,105/12 = 0,00875; n = 360
# PMT = 175000 × 0,00875 × 1,00875^360 / (1,00875^360 - 1) ≈ R$ 1600
# Em termos reais (descontando 5% inflação): parcela real decresce com tempo
# Simplificação: usar R$ 1.600 nominal constante; em termos reais começa R$ 1.600 e decai
# Vou usar R$ 1.600 como parcela real do mês 36 (start financing)
PARCELA_FINANC = 1_600  # R$ mensal, parcela real média nos primeiros 10 anos


@dataclass
class State:
    reserva: float = 75_000
    imovel_bucket: float = 45_000     # Pra entrada
    aposentadoria: float = 0
    mustang_bucket: float = 0          # Pra compra Mustang
    imovel_owned: bool = False
    mustang_owned: bool = False
    mustang_value: float = 0            # Valor atual do carro (deprecia)
    financing_balance: float = 0        # Saldo devedor financiamento
    month: int = 0
    events: list = field(default_factory=list)

    def total_patrimonio(self) -> float:
        """Patrimônio líquido = invested + imovel - saldo devedor + mustang value."""
        imovel_eq = VALOR_IMOVEL / 2 if self.imovel_owned else 0  # metade é do Victor
        return (
            self.reserva
            + self.imovel_bucket
            + self.aposentadoria
            + self.mustang_bucket
            + imovel_eq
            + self.mustang_value
            - self.financing_balance
        )


def apply_monthly_return(val: float, ann_return: float) -> float:
    """Aplica retorno mensal composto."""
    return val * (1 + ann_return / 12)


def run_scenario(
    scenario_name: str,
    mustang_strategy: str = "split",  # 'split', 'priority', 'delay', 'none'
    amortizacao_pct: float = 0.0,      # % do aporte mensal pós-imóvel que vai pra amortização extra (0.0 = zero amortization extra)
    aposentadoria_age: int = 55,
    horizon_years: int = 35,
) -> pd.DataFrame:
    """Roda simulação mensal."""
    state = State()
    rows = []

    total_months = horizon_years * 12

    for month in range(1, total_months + 1):
        state.month = month
        year = START_YEAR + (START_MONTH - 1 + month - 1) // 12
        month_of_year = ((START_MONTH - 1 + month - 1) % 12) + 1
        age = AGE_START + (START_MONTH - 1 + month - 1) // 12

        # 1) Apply returns (growth)
        state.reserva = apply_monthly_return(state.reserva, RET_RESERVA)
        state.imovel_bucket = apply_monthly_return(state.imovel_bucket, RET_IMOVEL_BUCKET)
        state.aposentadoria = apply_monthly_return(state.aposentadoria, RET_APOSENTADORIA)
        state.mustang_bucket = apply_monthly_return(state.mustang_bucket, RET_MUSTANG_BUCKET)

        # Mustang depreciation (if owned)
        if state.mustang_owned and state.mustang_value > 0:
            state.mustang_value = apply_monthly_return(state.mustang_value, DEPRECIACAO_MUSTANG)

        # Financing balance: real rate ~5% (10.5% nominal - 5% inflation)
        # Saldo devedor REDUCES by paying amortização embutida na parcela
        if state.financing_balance > 0:
            # Juros mensal real 5%/12 = 0.0042
            juros = state.financing_balance * 0.05 / 12
            amortizacao_embutida = PARCELA_FINANC - juros
            if amortizacao_embutida > 0:
                state.financing_balance = max(0, state.financing_balance - amortizacao_embutida)
            else:
                # Juros > parcela (não deveria acontecer com esses valores)
                state.financing_balance += (juros - PARCELA_FINANC)

        # 2) Determine monthly contribution
        # Fase 1: meses 1-6 (Mai-Out/2026)
        # Fase 2: meses 7+ (Nov/2026+)
        if month <= 6:
            aporte_total = APORTE_FASE1
        else:
            aporte_total = APORTE_FASE2

        # Reduzir aporte por parcela de financiamento (se estiver pagando)
        # Também reduzir por manutenção Mustang (se owned)
        aporte_liquido = aporte_total - (PARCELA_FINANC if state.financing_balance > 0 else 0) - (MANUT_MUSTANG_MES if state.mustang_owned else 0)

        # 3) Allocate contribution
        # Pré-compra imóvel: R$ 833 imóvel + resto aposentadoria
        if not state.imovel_owned:
            state.imovel_bucket += 833
            state.aposentadoria += (aporte_total - 833)
        else:
            # Pós-imóvel: dinâmica depende de strategy
            if mustang_strategy == "split":
                # 50/50 aposentadoria vs mustang até comprar Mustang
                if not state.mustang_owned:
                    state.mustang_bucket += aporte_liquido * 0.5
                    state.aposentadoria += aporte_liquido * 0.5
                else:
                    # Pós-Mustang: 100% aposentadoria
                    state.aposentadoria += aporte_liquido
            elif mustang_strategy == "priority":
                # 100% Mustang até comprar, depois aposentadoria
                if not state.mustang_owned:
                    state.mustang_bucket += aporte_liquido
                else:
                    state.aposentadoria += aporte_liquido
            elif mustang_strategy == "delay":
                # Aposentadoria primeiro por 10 anos pós-imóvel, depois Mustang
                months_since_imovel = month - MES_COMPRA_IMOVEL
                if months_since_imovel < 120:  # 10 anos aposentadoria prio
                    state.aposentadoria += aporte_liquido
                elif not state.mustang_owned:
                    state.mustang_bucket += aporte_liquido
                else:
                    state.aposentadoria += aporte_liquido
            elif mustang_strategy == "none":
                # Sem Mustang — tudo pra aposentadoria
                state.aposentadoria += aporte_liquido
            else:
                raise ValueError(f"Unknown strategy: {mustang_strategy}")

            # Amortização extra (se aplicável)
            if amortizacao_pct > 0 and state.financing_balance > 0:
                amort_extra = aporte_liquido * amortizacao_pct
                # Redirecionar amort_extra da aposentadoria pra amortização
                state.aposentadoria -= amort_extra
                state.financing_balance = max(0, state.financing_balance - amort_extra)

        # 4) Events: compra imóvel
        if month == MES_COMPRA_IMOVEL and not state.imovel_owned:
            # Entrada saí do imovel_bucket
            if state.imovel_bucket >= ENTRADA_VICTOR:
                state.imovel_bucket -= ENTRADA_VICTOR
                # Sobra do imovel_bucket vai pra aposentadoria
                state.aposentadoria += state.imovel_bucket
                state.imovel_bucket = 0
                state.financing_balance = FINANC_VICTOR
                state.imovel_owned = True
                state.events.append((month, f"Compra imóvel: R$ {ENTRADA_VICTOR/1000:.0f}k entrada + R$ {FINANC_VICTOR/1000:.0f}k financiamento"))
            else:
                # Não tinha dinheiro suficiente — atrasa
                state.events.append((month, "ATRASO: não tem dinheiro pra entrada"))

        # 5) Compra Mustang quando tem R$ 320k
        if state.imovel_owned and not state.mustang_owned and state.mustang_bucket >= VALOR_MUSTANG:
            state.mustang_bucket -= VALOR_MUSTANG
            state.mustang_value = VALOR_MUSTANG
            state.aposentadoria += state.mustang_bucket  # Sobra vai pra aposentadoria
            state.mustang_bucket = 0
            state.mustang_owned = True
            state.events.append((month, f"Compra Mustang: R$ {VALOR_MUSTANG/1000:.0f}k"))

        # Record row
        rows.append({
            "month": month,
            "year": year + (month_of_year - 1) / 12,
            "age": age + (month_of_year - 1) / 12,
            "reserva": state.reserva,
            "imovel_bucket": state.imovel_bucket,
            "aposentadoria": state.aposentadoria,
            "mustang_bucket": state.mustang_bucket,
            "imovel_eq": VALOR_IMOVEL / 2 if state.imovel_owned else 0,
            "mustang_value": state.mustang_value,
            "financing_balance": state.financing_balance,
            "total_liquido": state.total_patrimonio(),
            "imovel_owned": state.imovel_owned,
            "mustang_owned": state.mustang_owned,
        })

    df = pd.DataFrame(rows)
    df["scenario"] = scenario_name
    return df, state.events


def simulate_aposentadoria_at(df: pd.DataFrame, age_retire: int) -> dict:
    """Dado um cenário, calcula quanto de aposentadoria por mês via SWR 4%."""
    df_at_age = df[df["age"] >= age_retire].iloc[0] if (df["age"] >= age_retire).any() else None
    if df_at_age is None:
        return {"age": age_retire, "patrimonio_aposentadoria": None, "renda_mensal_swr4": None}
    patrimonio_nest = df_at_age["aposentadoria"]
    renda_anual_swr4 = patrimonio_nest * 0.04
    return {
        "age": age_retire,
        "patrimonio_aposentadoria": patrimonio_nest,
        "patrimonio_total_liquido": df_at_age["total_liquido"],
        "renda_mensal_swr4": renda_anual_swr4 / 12,
        "renda_vs_vida_desejada": (renda_anual_swr4 / 12) / VIDA_DESEJADA_MES,
    }


def main() -> None:
    print("=== Projeção Victor — 3 objetivos integrados ===\n")

    scenarios = {
        "SPLIT 50/50 (Mustang + Apos)": "split",
        "MUSTANG priority (pós imóvel)": "priority",
        "DELAY Mustang (+10y apos)": "delay",
        "SEM MUSTANG": "none",
    }

    all_results = {}
    for name, strat in scenarios.items():
        df, events = run_scenario(name, mustang_strategy=strat, horizon_years=35)
        all_results[name] = {"df": df, "events": events}

        # Encontra quando Mustang foi comprado
        mustang_purchase_row = df[df["mustang_owned"] & (df["mustang_owned"].shift(1).fillna(False) == False)]
        mustang_month = mustang_purchase_row["month"].iloc[0] if len(mustang_purchase_row) > 0 else None
        mustang_age = mustang_purchase_row["age"].iloc[0] if len(mustang_purchase_row) > 0 else None

        # Aposentadoria aos 55 e 60
        apos_55 = simulate_aposentadoria_at(df, 55)
        apos_60 = simulate_aposentadoria_at(df, 60)

        print(f"\n### {name}")
        if mustang_month:
            print(f"  Mustang comprado: mês {int(mustang_month)} (idade {mustang_age:.1f})")
        else:
            print(f"  Mustang: NÃO comprado nesse horizonte")
        if apos_55["patrimonio_aposentadoria"] is not None:
            print(f"  Aos 55 anos: R$ {apos_55['patrimonio_aposentadoria']/1e6:.2f}M aposentadoria → "
                  f"R$ {apos_55['renda_mensal_swr4']/1000:.1f}k/mês (SWR 4%) "
                  f"= {apos_55['renda_vs_vida_desejada']:.1f}× vida atual")
        if apos_60["patrimonio_aposentadoria"] is not None:
            print(f"  Aos 60 anos: R$ {apos_60['patrimonio_aposentadoria']/1e6:.2f}M aposentadoria → "
                  f"R$ {apos_60['renda_mensal_swr4']/1000:.1f}k/mês (SWR 4%) "
                  f"= {apos_60['renda_vs_vida_desejada']:.1f}× vida atual")

    # Save results
    summary = []
    for name, res in all_results.items():
        df = res["df"]
        mustang_row = df[df["mustang_owned"] & (df["mustang_owned"].shift(1).fillna(False) == False)]
        summary.append({
            "scenario": name,
            "mustang_month": int(mustang_row["month"].iloc[0]) if len(mustang_row) > 0 else None,
            "mustang_age": float(mustang_row["age"].iloc[0]) if len(mustang_row) > 0 else None,
            "apos_55_nest": simulate_aposentadoria_at(df, 55)["patrimonio_aposentadoria"],
            "apos_55_renda_mes": simulate_aposentadoria_at(df, 55)["renda_mensal_swr4"],
            "apos_60_nest": simulate_aposentadoria_at(df, 60)["patrimonio_aposentadoria"],
            "apos_60_renda_mes": simulate_aposentadoria_at(df, 60)["renda_mensal_swr4"],
        })
    pd.DataFrame(summary).to_csv(OUT_DIR / "scenarios_summary.csv", index=False)

    # ========================================================================
    # GRÁFICO 1: Projeção 35 anos — 4 cenários em grid
    # ========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle("Projeção Victor — 30 anos → 65 anos\n(R\\$ reais de 2026; aposentadoria @ 6% real / reserva 2% / RF 3%)", fontsize=14, y=1.00)

    for ax, (name, res) in zip(axes.flat, all_results.items()):
        df = res["df"]
        ax.stackplot(
            df["age"],
            df["reserva"] / 1000,
            df["imovel_bucket"] / 1000,
            df["aposentadoria"] / 1000,
            df["mustang_bucket"] / 1000,
            df["imovel_eq"] / 1000,
            df["mustang_value"] / 1000,
            labels=["Reserva emergência", "Imóvel bucket (pré-compra)",
                    "Aposentadoria (investido)", "Mustang bucket",
                    "Imóvel (equity, pós-compra)", "Mustang (valor, deprecia)"],
            colors=["#2E86AB", "#A23B72", "#6FBF73", "#F18F01",
                    "#C73E1D", "#8A4F7D"],
            alpha=0.85,
        )

        # Linha de patrimônio líquido (total - dívida)
        ax.plot(df["age"], df["total_liquido"] / 1000, color="black", linewidth=2.2, label="Patrimônio líquido", zorder=10)

        # Markers de eventos
        for mon, evt in res["events"]:
            age_evt = 30 + (mon - 1) / 12
            ax.axvline(age_evt, color="gray", linestyle="--", alpha=0.4, linewidth=0.8)
            ax.text(age_evt, ax.get_ylim()[1] * 0.92, evt.split(":")[0], rotation=90, fontsize=8, verticalalignment="top", alpha=0.7)

        # Linhas de aposentadoria
        ax.axvline(55, color="green", linestyle=":", alpha=0.5, linewidth=1.2)
        ax.axvline(60, color="green", linestyle=":", alpha=0.5, linewidth=1.2)
        ax.text(55, ax.get_ylim()[1] * 0.98, "55", fontsize=9, color="green")
        ax.text(60, ax.get_ylim()[1] * 0.98, "60", fontsize=9, color="green")

        ax.set_title(name, fontsize=11, fontweight="bold")
        ax.set_xlabel("Idade (anos)")
        ax.set_ylabel("R$ mil (reais de 2026)")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(30, 65)

        # Legend só no primeiro plot
        if ax is axes[0, 0]:
            ax.legend(loc="upper left", fontsize=8, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "projecao_4_cenarios.png", dpi=130, bbox_inches="tight")
    print(f"\nGráfico salvo: {OUT_DIR / 'projecao_4_cenarios.png'}")

    # ========================================================================
    # GRÁFICO 2: Aposentadoria comparativa (bucket só)
    # ========================================================================
    fig2, ax2 = plt.subplots(figsize=(14, 7))
    colors = {"SPLIT 50/50 (Mustang + Apos)": "#F18F01",
              "MUSTANG priority (pós imóvel)": "#C73E1D",
              "DELAY Mustang (+10y apos)": "#6FBF73",
              "SEM MUSTANG": "#2E86AB"}

    for name, res in all_results.items():
        df = res["df"]
        ax2.plot(df["age"], df["aposentadoria"] / 1e6, label=name, linewidth=2.2, color=colors[name])

    ax2.axhline(y=3.75, color="gray", linestyle="--", alpha=0.5, label="R$ 3,75M = R$ 12,5k/mês @ SWR 4% (vida atual)")
    ax2.axhline(y=7.5, color="gray", linestyle="-.", alpha=0.5, label="R$ 7,5M = R$ 25k/mês @ SWR 4% (2× vida atual)")

    ax2.axvline(55, color="green", linestyle=":", alpha=0.5)
    ax2.axvline(60, color="green", linestyle=":", alpha=0.5)
    ax2.text(55.2, ax2.get_ylim()[1]*0.95, "Aposenta 55", fontsize=9, color="green")
    ax2.text(60.2, ax2.get_ylim()[1]*0.95, "Aposenta 60", fontsize=9, color="green")

    ax2.set_title("Patrimônio investido em aposentadoria — 4 estratégias\n(sem contar imóvel, Mustang ou reserva)",
                  fontsize=13)
    ax2.set_xlabel("Idade (anos)")
    ax2.set_ylabel("R$ milhões (reais de 2026)")
    ax2.legend(loc="upper left", fontsize=10, framealpha=0.9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(30, 65)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "aposentadoria_comparativa.png", dpi=130, bbox_inches="tight")
    print(f"Gráfico salvo: {OUT_DIR / 'aposentadoria_comparativa.png'}")

    # ========================================================================
    # GRÁFICO 3: Amortizar vs Investir (só pra cenário SPLIT)
    # ========================================================================
    print("\n=== Amortizar vs Investir — comparação ===\n")
    amort_scenarios = {}
    for pct, label in [(0.0, "0% amortiza (tudo investe)"),
                       (0.2, "20% amortiza"),
                       (0.5, "50% amortiza"),
                       (1.0, "100% amortiza (paga rápido)")]:
        df, _ = run_scenario(f"Amort {int(pct*100)}%",
                             mustang_strategy="split",
                             amortizacao_pct=pct,
                             horizon_years=35)
        amort_scenarios[label] = df
        apos_55 = simulate_aposentadoria_at(df, 55)
        print(f"  {label}: aos 55y → R$ {apos_55['patrimonio_aposentadoria']/1e6:.2f}M nest "
              f"(R$ {apos_55['renda_mensal_swr4']/1000:.1f}k/mês)")

    fig3, ax3 = plt.subplots(figsize=(14, 7))
    for label, df in amort_scenarios.items():
        ax3.plot(df["age"], df["aposentadoria"] / 1e6, label=label, linewidth=2.2)

    ax3.axvline(55, color="green", linestyle=":", alpha=0.5)
    ax3.axvline(60, color="green", linestyle=":", alpha=0.5)
    ax3.set_title("Amortizar financiamento vs Continuar investindo\n(cenário SPLIT 50/50 Mustang+Apos; financiamento R$ 175k a 5% real/10,5% nominal)",
                  fontsize=13)
    ax3.set_xlabel("Idade (anos)")
    ax3.set_ylabel("R$ milhões em aposentadoria (reais de 2026)")
    ax3.legend(loc="upper left", fontsize=10, framealpha=0.9)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(30, 65)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "amortizar_vs_investir.png", dpi=130, bbox_inches="tight")
    print(f"\nGráfico salvo: {OUT_DIR / 'amortizar_vs_investir.png'}")

    print(f"\n{'='*80}\nArtefatos em: {OUT_DIR}\n{'='*80}")


if __name__ == "__main__":
    main()
