"""Money-weighted simulation: $10k initial + $1.5k/month aporte over 40y synth.

Applies real-world entry costs (FX spread + IOF Lei 14.754 simbólico + IBKR
fixed fee) on each contribution and tracks final portfolio value vs total
invested.

Variants tested:
  V0 PURE      — IBKR margin direct (SPY+ZROZ+GLD), TransferBank FX 0.30% + $2 fee
  V0_margin    — same but with -4%/yr drag on 80% leverage (margin interest)
  V1 NTSX+GDE  — Inter cash, FX spread 1.25%, no fixed fee
  V2 2x LETF   — Inter cash, FX spread 1.25%
  V3 3x LETF   — Inter cash, FX spread 1.25%
  SPYSIM b&h   — Inter buy-hold benchmark, same Inter cost structure

Tax: NOT applied here — for true buy-and-hold investor with no sells, Lei
14.754 PF direta defers tax until eventual sale (decades from now). The
post-tax MTM-style model in POST_TAX_VALIDATION.md is too pessimistic for
this scenario per `[Lei 14.754/2023, Art. 1-3º]`.

Citations
---------
* `[Lei 14.754/2023, Art. 1-3º]` — PF direta tributação na realização.
* `[advances_fin_ml, p.196-202]` — bootstrap Sharpe CI methodology (reused).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent
RETURNS_PATH = OUT_DIR.parent / "iter035_variants/iter035_variants_returns.parquet"
TF_PATH = ROOT / "data/testfolio/cache/history.parquet"

# Aporte parameters
INITIAL_BRL = 50_000.0  # ~$10k at 5 BRL/USD
MONTHLY_BRL = 7_500.0   # ~$1.5k/month
USD_BRL_RATE = 5.0       # fixed assumption (real-world: PTAX varies)
TRADING_DAYS = 252

# Cost structures by broker
COSTS = {
    "Inter": {"fx_spread": 0.0125, "iof": 0.0038, "fixed_fee_usd": 0.0},
    "IBKR_TransferBank": {"fx_spread": 0.0030, "iof": 0.0038, "fixed_fee_usd": 2.0},
}

# Margin interest on V0 (80% borrowed @ 5%/yr → 4%/yr drag on portfolio)
MARGIN_DAILY_DRAG = 0.04 / TRADING_DAYS


def apply_aporte_simulation(daily_returns: pd.Series,
                            initial_brl: float,
                            monthly_brl: float,
                            fx_spread: float,
                            iof: float,
                            fixed_fee_usd: float,
                            usd_brl_rate: float = USD_BRL_RATE) -> dict:
    """Money-weighted simulation: monthly aportes + daily compounding.

    Returns final stats: equity, total invested BRL/USD, multiplier, IRR.
    """
    r = daily_returns.dropna()
    equity_usd = 0.0
    total_invested_brl = initial_brl
    total_invested_usd_gross = 0.0
    total_fx_cost_brl = 0.0

    # Initial deposit at t=0
    usd_gross = initial_brl / usd_brl_rate
    usd_after_fx = usd_gross * (1 - fx_spread) - fixed_fee_usd
    usd_after_iof = usd_after_fx * (1 - iof)
    equity_usd += usd_after_iof
    total_invested_usd_gross += usd_gross
    total_fx_cost_brl += (usd_gross - usd_after_iof) * usd_brl_rate

    # Track aporte month markers
    months_seen = set()
    months_seen.add((r.index[0].year, r.index[0].month))

    for i, date in enumerate(r.index):
        # Apply daily return first
        equity_usd *= (1 + r.iloc[i])

        # Check for monthly aporte at start of new month
        ym = (date.year, date.month)
        if ym not in months_seen:
            months_seen.add(ym)
            usd_gross = monthly_brl / usd_brl_rate
            usd_after_fx = usd_gross * (1 - fx_spread) - fixed_fee_usd
            usd_after_iof = usd_after_fx * (1 - iof)
            equity_usd += usd_after_iof
            total_invested_brl += monthly_brl
            total_invested_usd_gross += usd_gross
            total_fx_cost_brl += (usd_gross - usd_after_iof) * usd_brl_rate

    final_brl = equity_usd * usd_brl_rate
    multiplier = final_brl / total_invested_brl if total_invested_brl > 0 else 0.0

    # Money-weighted IRR (approx via geometric average over years invested)
    years = len(r) / TRADING_DAYS
    avg_invested_brl = total_invested_brl / 2  # rough avg (capital ramps linearly)
    irr_approx = (final_brl / avg_invested_brl) ** (1 / years) - 1 if years > 0 else 0.0

    return {
        "final_usd": equity_usd,
        "final_brl": final_brl,
        "total_invested_brl": total_invested_brl,
        "total_invested_usd_gross": total_invested_usd_gross,
        "total_fx_cost_brl": total_fx_cost_brl,
        "fx_cost_pct_of_invested": total_fx_cost_brl / total_invested_brl,
        "multiplier_brl": multiplier,
        "irr_approx": irr_approx,
        "years": years,
        "n_aportes": len(months_seen),
    }


def main() -> None:
    series = pd.read_parquet(RETURNS_PATH)
    print(f"Loaded variants returns: {series.index.min().date()} → "
          f"{series.index.max().date()}, {len(series)} bars")

    # SPYSIM benchmark from raw synth
    df = pd.read_parquet(TF_PATH)
    df.index = pd.to_datetime(df.index)
    spy_r = df["SPYSIM"].pct_change().dropna()
    spy_r = spy_r.loc[series.index.min():series.index.max()]

    # Apply margin drag to V0 (4%/yr on 80% leverage)
    v0_with_margin = (series["V0_iter035_pure_SPY_ZROZ_GLD_180notional"]
                      - MARGIN_DAILY_DRAG)

    # Run simulations
    print(f"\n=== Aporte simulation: BRL {INITIAL_BRL:,.0f} initial + "
          f"BRL {MONTHLY_BRL:,.0f}/month over {len(series)/TRADING_DAYS:.1f} years ===\n")

    cases = [
        ("V0_PURE_no_margin_cost",
         series["V0_iter035_pure_SPY_ZROZ_GLD_180notional"], "IBKR_TransferBank",
         "PURE 90/60/30 — assumes free leverage (unrealistic, kept as upper bound)"),
        ("V0_PURE_with_4pct_margin_drag",
         v0_with_margin, "IBKR_TransferBank",
         "PURE 90/60/30 with -4%/yr drag on 80% borrowed (HONEST IBKR cost)"),
        ("V1_NTSX_GDE_67_33",
         series["V1_NTSX_GDE_67_33_Inter_cash"], "Inter",
         "NTSX+GDE Inter cash — no margin, FX 1.25%"),
        ("V2_LETF_2x_SSO_UBT_UGL_BIL",
         series["V2_SSO_UBT_UGL_BIL_2x_Inter"], "Inter",
         "2× LETFs Inter cash"),
        ("V3_LETF_3x_UPRO_TMF_GLD_BIL",
         series["V3_UPRO_TMF_GLD_BIL_3x_Inter"], "Inter",
         "3× LETFs Inter cash"),
        ("BENCH_SPYSIM_buyhold",
         spy_r, "Inter",
         "SPY buy-and-hold via Inter Internacional"),
    ]

    rows = []
    for name, returns, broker, descr in cases:
        cost = COSTS[broker]
        result = apply_aporte_simulation(
            returns, INITIAL_BRL, MONTHLY_BRL,
            cost["fx_spread"], cost["iof"], cost["fixed_fee_usd"]
        )
        result["name"] = name
        result["broker"] = broker
        result["description"] = descr
        rows.append(result)
        print(f"  {name} ({broker})")
        print(f"     {descr}")
        print(f"     Total invested: BRL {result['total_invested_brl']:>15,.0f}")
        print(f"     Final balance:  BRL {result['final_brl']:>15,.0f} "
              f"(USD {result['final_usd']:>12,.0f})")
        print(f"     Multiplier:     {result['multiplier_brl']:>5.2f}× "
              f"(IRR ~{result['irr_approx']*100:>5.2f}%/yr)")
        print(f"     FX cost total:  BRL {result['total_fx_cost_brl']:>15,.0f} "
              f"({result['fx_cost_pct_of_invested']*100:.2f}% of invested)")
        print()

    # Save JSON
    out_json = OUT_DIR / "APORTE_SIMULATION.json"
    out_json.write_text(json.dumps({
        "params": {
            "initial_brl": INITIAL_BRL,
            "monthly_brl": MONTHLY_BRL,
            "usd_brl_rate": USD_BRL_RATE,
            "margin_drag_yr_pct": 4.0,
            "tax_note": "NOT applied — Lei 14.754 PF direta defers tax until "
                        "sale; buy-hold investor has zero realizations during "
                        "accumulation phase",
        },
        "broker_costs": COSTS,
        "results": rows,
    }, indent=2, default=str))
    print(f"Wrote {out_json}")

    # Markdown
    out_md = OUT_DIR / "APORTE_SIMULATION.md"
    with out_md.open("w") as fh:
        fh.write("# Aporte mensal simulation — $10k initial + $1.5k/month over 40y\n\n")
        fh.write(f"Generated: {pd.Timestamp.now().isoformat()}\n\n")
        fh.write(f"Parameters: BRL {INITIAL_BRL:,.0f} initial + BRL {MONTHLY_BRL:,.0f}/month, "
                 f"USD/BRL fixed at {USD_BRL_RATE:.2f}, "
                 f"window {len(series)/TRADING_DAYS:.1f}y "
                 f"({series.index.min().date()} → {series.index.max().date()}).\n\n")

        fh.write("## Cost structures\n\n")
        fh.write("| broker | FX spread | IOF | fixed fee/aporte |\n|---|---|---|---|\n")
        for k, c in COSTS.items():
            fh.write(f"| {k} | {c['fx_spread']*100:.2f}% | {c['iof']*100:.2f}% | "
                     f"${c['fixed_fee_usd']:.2f} |\n")

        fh.write("\n## Results (sorted by final BRL)\n\n")
        rows.sort(key=lambda r: r["final_brl"], reverse=True)
        fh.write("| variant | broker | total invested | final BRL | multiplier | IRR ~ | FX cost % |\n")
        fh.write("|---|---|---|---|---|---|---|\n")
        for r in rows:
            fh.write(f"| `{r['name']}` | {r['broker']} | "
                     f"BRL {r['total_invested_brl']:,.0f} | "
                     f"**BRL {r['final_brl']:,.0f}** | "
                     f"{r['multiplier_brl']:.2f}× | "
                     f"{r['irr_approx']*100:.2f}%/yr | "
                     f"{r['fx_cost_pct_of_invested']*100:.2f}% |\n")

        fh.write("\n## Key observations\n\n")
        # Find V1 and SPYSIM and V0_with_margin
        v1 = next((r for r in rows if r["name"].startswith("V1")), None)
        v0m = next((r for r in rows if "with_4pct_margin" in r["name"]), None)
        v0p = next((r for r in rows if "no_margin_cost" in r["name"]), None)
        spy = next((r for r in rows if "SPYSIM" in r["name"]), None)
        if v1 and spy:
            edge_v1_vs_spy = (v1["final_brl"] - spy["final_brl"]) / spy["final_brl"] * 100
            fh.write(f"- **V1 NTSX+GDE vs SPY buy-hold (mesmo broker)**: "
                     f"V1 termina com **BRL {v1['final_brl']-spy['final_brl']:,.0f}** "
                     f"({edge_v1_vs_spy:+.1f}%) a mais que SPY puro. "
                     f"Mesma cesta de cost (Inter 1.25% FX), V1 entrega ~{v1['irr_approx']*100:.1f}%/yr "
                     f"vs SPY {spy['irr_approx']*100:.1f}%/yr.\n")
        if v0m and v1:
            delta_v0m_v1 = (v0m["final_brl"] - v1["final_brl"]) / v1["final_brl"] * 100
            fh.write(f"- **V0 com margin cost honesto vs V1**: V0 entrega "
                     f"{delta_v0m_v1:+.1f}% vs V1 — diferença real após cobrar "
                     f"juros de margem 4%/yr sobre os 80% emprestados. "
                     f"({v0m['irr_approx']*100:.1f}%/yr vs {v1['irr_approx']*100:.1f}%/yr).\n")
        if v0p and v0m:
            margin_drag_brl = v0p["final_brl"] - v0m["final_brl"]
            fh.write(f"- **Custo real do IBKR margin loan ao longo de 40y**: "
                     f"BRL {margin_drag_brl:,.0f} ({(margin_drag_brl/v0p['final_brl'])*100:.1f}% "
                     f"do balance idealizado). Esse é o que IBKR cobra pra te emprestar 80%.\n")

        fh.write(f"\n## Caveats\n\n")
        fh.write("1. **Tax NÃO aplicado** — buy-and-hold investor com aportes "
                 "mensais e sem vendas tem zero realização durante acumulação; "
                 "Lei 14.754 PF direta defere tax até venda eventual (décadas no "
                 "futuro). Pra estratégias com rotação (iter 079, iter 016 daily), "
                 "haveria tax anual sobre realizações.\n")
        fh.write("2. **USD/BRL fixo em 5.00** — desvalorização BRL não modelada. "
                 "Real-world: BRL desvaloriza ~5-10%/yr historicamente, o que "
                 "**aumenta** o BRL final (você compra USD barato no início e ele vale "
                 "mais BRL no fim). Simulação é conservadora nesse aspecto.\n")
        fh.write("3. **V0 sem margin cost é IRREALISTA** — kept como upper bound "
                 "teórico. Use V0_with_margin pra comparação justa com V1.\n")
        fh.write("4. **40y de aportes BRL 7.5k/mo cumulativo = BRL 3.6M** — "
                 "magnitude bem acima do que single user provavelmente faz. "
                 "Resultados escalam linearmente — pra ver perfil $10k+$500/mo, "
                 "divide tudo por 3.\n")

    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
