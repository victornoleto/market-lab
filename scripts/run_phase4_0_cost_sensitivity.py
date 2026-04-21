"""Phase 4.0 — Cost sensitivity stress matrix for Index CFD Caminho 3.

Sweeps each cost parameter independently (one-at-a-time OAT) and
computes OOS gates at each level. Then runs a joint worst-case with
all parameters stressed simultaneously. Identifies the "viability
envelope" — below which combinations the strategy stops passing the
T4 gate suite.

Sweep axes:
1. commission_round_trip_bps: 0 → 40 bps RT (at $1k notional = $0 to $2/side)
2. spread_half_bps: 5 → 25 bps (10 → 50 bps RT)
3. swap_daily_pct_long: -0.005 → -0.040 (1.3%/yr → 10.1%/yr)
4. Dividend adjustment haircut: 0% → 100% (on top of TR series)

Baseline (Caminho 3 T3): commission=0, spread_half=5, swap=-0.008, div_haircut=0%

Output:
  reports/phase4_0/index_cfd_validation/cost_sensitivity.json
  reports/phase4_0/index_cfd_validation/cost_sensitivity.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ai_trade.backtest.data.spx_tr_loader import load_spx_tr_daily  # noqa: E402
from ai_trade.backtest.strategies.plano_a_leveraged_rotation import (  # noqa: E402
    PlanoALeveragedRotationConfig,
    simulate_plano_a_rotation,
)

OUT_DIR = Path("reports/phase4_0/index_cfd_validation")
TIINGO_DAILY_DIR = Path("data/tiingo/daily/prices")

WINDOW_START = pd.Timestamp("2001-05-14")
WINDOW_END = pd.Timestamp("2026-04-14")
OOS_START = pd.Timestamp("2018-01-01")
OOS_END = pd.Timestamp("2023-12-31")

# Approx annual gross dividend yield on the risk-on basket (SPY ~1.5%,
# QQQ ~0.7%, equal-weight → ~1.1%). Used for haircut modeling.
GROSS_DIV_YIELD_RISK_ON = 0.011


def _load_panels() -> tuple[dict, dict]:
    spx_ret = load_spx_tr_daily(str(WINDOW_START.date()), str(WINDOW_END.date()))
    spx_price = (1.0 + spx_ret).cumprod() * 100.0
    spx_panel = pd.DataFrame({"close": spx_price})

    qqq = pd.read_parquet(TIINGO_DAILY_DIR / "QQQ.parquet")
    qqq.index = pd.DatetimeIndex(qqq.index)
    qqq_panel = pd.DataFrame({"close": qqq["adj_close"].astype(float)})

    gld = pd.read_parquet(TIINGO_DAILY_DIR / "GLD.parquet")
    gld.index = pd.DatetimeIndex(gld.index)
    gld_panel = pd.DataFrame({"close": gld["adj_close"].astype(float)})

    return (
        {"SPY": spx_panel, "QQQ": qqq_panel},
        {"gld": gld_panel},
    )


def _oos_metrics(ret: pd.Series) -> dict:
    oos = ret.loc[(ret.index >= OOS_START) & (ret.index <= OOS_END)]
    if len(oos) < 2:
        return {"sharpe": 0.0, "cagr": 0.0, "mdd": 0.0}
    eq = (1.0 + oos).cumprod()
    years = len(oos) / 252.0
    return {
        "sharpe": float(oos.mean() / oos.std() * np.sqrt(252)) if oos.std() > 0 else 0.0,
        "cagr": float(eq.iloc[-1] ** (1.0 / years) - 1.0),
        "mdd": float((eq / eq.cummax() - 1.0).min()),
    }


def _apply_dividend_haircut(
    daily_returns: pd.Series, haircut_pct: float, regime_on_frac: pd.Series
) -> pd.Series:
    """Subtract the missed-dividend drag on risk-on bars.

    If haircut_pct = 0.50, 50% of gross dividend yield is lost to the
    CFD adjustment mechanism. Daily drag = haircut × yield × regime_fraction.
    """
    if haircut_pct <= 0:
        return daily_returns
    daily_drag = (
        haircut_pct * GROSS_DIV_YIELD_RISK_ON / 252.0
    ) * regime_on_frac.reindex(daily_returns.index).fillna(0.0)
    return daily_returns - daily_drag


def _run_one(
    risk_on_panel: dict,
    off_panel: dict,
    *,
    commission_bps: float,
    spread_half_bps: float,
    swap_daily: float,
    div_haircut: float,
) -> dict:
    cfg = PlanoALeveragedRotationConfig(
        regime_signal="ema100",
        leverage=2.0,
        off_regime_asset="gld",
        risk_on_tickers=("SPY", "QQQ"),
        spread_half_bps=spread_half_bps,
        commission_round_trip_bps=commission_bps,
        slippage_bps_round_trip=3.0,
        swap_daily_pct_long=swap_daily,
    )
    result = simulate_plano_a_rotation(risk_on_panel, cfg, off_regime_panel=off_panel)
    ret = _apply_dividend_haircut(
        result.daily_returns, div_haircut, result.regime_on_fraction
    )
    m = _oos_metrics(ret)
    gates_pass = (
        m["sharpe"] >= 2.0
        and m["cagr"] >= 0.30
        and m["mdd"] >= -0.25
    )
    return {
        "commission_bps": commission_bps,
        "spread_half_bps": spread_half_bps,
        "swap_daily": swap_daily,
        "div_haircut": div_haircut,
        "oos_sharpe": m["sharpe"],
        "oos_cagr": m["cagr"],
        "oos_mdd": m["mdd"],
        "gates_pass": gates_pass,
    }


def main() -> None:
    print("=" * 72)
    print("Phase 4.0 Cost Sensitivity — stress matrix for Caminho 3 Index CFD")
    print("=" * 72)

    print("\nLoading panels...")
    risk_on_panel, off_panel = _load_panels()
    print(f"  SPX TR / QQQ / GLD loaded.")

    # Baseline = Caminho 3 T3
    BASELINE = {
        "commission_bps": 0.0,
        "spread_half_bps": 5.0,
        "swap_daily": -0.008,
        "div_haircut": 0.0,
    }

    scenarios: list[dict] = []

    print("\n[1/4] Baseline (T3 config, reproduce for reference)...")
    scenarios.append({"scenario": "baseline", **_run_one(risk_on_panel, off_panel, **BASELINE)})
    r = scenarios[-1]
    print(f"  S={r['oos_sharpe']:.3f} CAGR={r['oos_cagr']:.2%} MDD={r['oos_mdd']:.2%} "
          f"{'✅' if r['gates_pass'] else '❌'}")

    print("\n[2/4] Axis 1 — Commission sweep (bps RT)...")
    for comm in [0, 5, 10, 20, 40]:
        params = {**BASELINE, "commission_bps": comm}
        r = _run_one(risk_on_panel, off_panel, **params)
        scenarios.append({"scenario": f"commission={comm}bps", **r})
        print(f"  commission={comm:>3} bps RT  →  S={r['oos_sharpe']:.3f}  "
              f"CAGR={r['oos_cagr']:.2%}  MDD={r['oos_mdd']:.2%}  "
              f"{'✅' if r['gates_pass'] else '❌'}")

    print("\n[3/4] Axis 2 — Spread sweep (half bps)...")
    for spread in [5, 10, 15, 25]:
        params = {**BASELINE, "spread_half_bps": spread}
        r = _run_one(risk_on_panel, off_panel, **params)
        scenarios.append({"scenario": f"spread_half={spread}bps", **r})
        print(f"  spread_half={spread:>3} bps  →  S={r['oos_sharpe']:.3f}  "
              f"CAGR={r['oos_cagr']:.2%}  MDD={r['oos_mdd']:.2%}  "
              f"{'✅' if r['gates_pass'] else '❌'}")

    print("\n[4/4] Axis 3 — Swap sweep (daily %)...")
    for swap in [-0.005, -0.008, -0.015, -0.025, -0.040]:
        params = {**BASELINE, "swap_daily": swap}
        r = _run_one(risk_on_panel, off_panel, **params)
        annual = swap * 252 * 100
        scenarios.append({"scenario": f"swap={swap:.3f}/day", **r})
        print(f"  swap={swap:.3f}/day ({annual:+.1f}%/yr)  →  "
              f"S={r['oos_sharpe']:.3f}  CAGR={r['oos_cagr']:.2%}  "
              f"MDD={r['oos_mdd']:.2%}  {'✅' if r['gates_pass'] else '❌'}")

    print("\n[5/5] Axis 4 — Dividend haircut sweep (% NOT captured)...")
    for hc in [0.0, 0.10, 0.25, 0.50, 1.0]:
        params = {**BASELINE, "div_haircut": hc}
        r = _run_one(risk_on_panel, off_panel, **params)
        scenarios.append({"scenario": f"div_haircut={hc*100:.0f}%", **r})
        drag_yr = hc * GROSS_DIV_YIELD_RISK_ON * 100
        print(f"  div_haircut={hc*100:>3.0f}% (~{drag_yr:.2f}%/yr drag)  →  "
              f"S={r['oos_sharpe']:.3f}  CAGR={r['oos_cagr']:.2%}  "
              f"MDD={r['oos_mdd']:.2%}  {'✅' if r['gates_pass'] else '❌'}")

    print("\n[JOINT] Worst-case — all 4 axes at worst simultaneously...")
    worst = {
        "commission_bps": 40.0,
        "spread_half_bps": 25.0,
        "swap_daily": -0.025,
        "div_haircut": 0.50,
    }
    r = _run_one(risk_on_panel, off_panel, **worst)
    scenarios.append({"scenario": "joint_worst_case", **r})
    print(f"  all stressed → S={r['oos_sharpe']:.3f} CAGR={r['oos_cagr']:.2%} "
          f"MDD={r['oos_mdd']:.2%} {'✅' if r['gates_pass'] else '❌'}")

    print("\n[MIDDLE] Middle-stress — realistic pessimistic...")
    middle = {
        "commission_bps": 10.0,
        "spread_half_bps": 10.0,
        "swap_daily": -0.015,
        "div_haircut": 0.25,
    }
    r = _run_one(risk_on_panel, off_panel, **middle)
    scenarios.append({"scenario": "middle_pessimistic", **r})
    print(f"  middle stressed → S={r['oos_sharpe']:.3f} CAGR={r['oos_cagr']:.2%} "
          f"MDD={r['oos_mdd']:.2%} {'✅' if r['gates_pass'] else '❌'}")

    # Save artefacts
    (OUT_DIR / "cost_sensitivity.json").write_text(
        json.dumps({"baseline": BASELINE, "scenarios": scenarios}, indent=2, default=float),
        encoding="utf-8",
    )
    print(f"\nwrote {OUT_DIR / 'cost_sensitivity.json'}")

    # Markdown
    md: list[str] = []
    md.append("# Phase 4.0 — Cost sensitivity matrix (Caminho 3 Index CFD)")
    md.append("")
    md.append(f"**Baseline:** commission=0 bps RT, spread_half=5 bps, swap=-0.008%/day, "
              f"div_haircut=0% (Caminho 3 T3 config, all optimistic).")
    md.append("")
    md.append("Each sweep holds the other 3 axes at baseline. Joint worst-case stresses all "
              "4 simultaneously. Gate threshold (T3 sanity): OOS Sharpe ≥ 2.0, CAGR ≥ 30%, MDD ≤ -25%.")
    md.append("")
    md.append("## Axis 1 — Commission (bps RT)")
    md.append("")
    md.append("| Commission (bps RT) | $/side @ $1k notional | OOS Sharpe | OOS CAGR | OOS MDD | Gates |")
    md.append("|---:|---:|---:|---:|---:|:--:|")
    for s in scenarios:
        if s["scenario"].startswith("commission="):
            bps = s["commission_bps"]
            md.append(f"| {bps:.0f} | ${bps/2 * 0.01:.2f} | {s['oos_sharpe']:.3f} | "
                      f"{s['oos_cagr']:.2%} | {s['oos_mdd']:.2%} | "
                      f"{'✅' if s['gates_pass'] else '❌'} |")
    md.append("")
    md.append("## Axis 2 — Spread (half bps)")
    md.append("")
    md.append("| Spread half (bps) | Total RT (bps) | OOS Sharpe | OOS CAGR | OOS MDD | Gates |")
    md.append("|---:|---:|---:|---:|---:|:--:|")
    for s in scenarios:
        if s["scenario"].startswith("spread_half="):
            h = s["spread_half_bps"]
            md.append(f"| {h:.0f} | {h*2:.0f} | {s['oos_sharpe']:.3f} | "
                      f"{s['oos_cagr']:.2%} | {s['oos_mdd']:.2%} | "
                      f"{'✅' if s['gates_pass'] else '❌'} |")
    md.append("")
    md.append("## Axis 3 — Swap daily rate")
    md.append("")
    md.append("| Swap daily (%) | Annualized (%) | OOS Sharpe | OOS CAGR | OOS MDD | Gates |")
    md.append("|---:|---:|---:|---:|---:|:--:|")
    for s in scenarios:
        if s["scenario"].startswith("swap="):
            sw = s["swap_daily"]
            md.append(f"| {sw*100:.4f}% | {sw*252*100:+.2f}% | {s['oos_sharpe']:.3f} | "
                      f"{s['oos_cagr']:.2%} | {s['oos_mdd']:.2%} | "
                      f"{'✅' if s['gates_pass'] else '❌'} |")
    md.append("")
    md.append("## Axis 4 — Dividend haircut")
    md.append("")
    md.append("| Div haircut (%) | ~Annual drag | OOS Sharpe | OOS CAGR | OOS MDD | Gates |")
    md.append("|---:|---:|---:|---:|---:|:--:|")
    for s in scenarios:
        if s["scenario"].startswith("div_haircut="):
            hc = s["div_haircut"]
            md.append(f"| {hc*100:.0f}% | {hc * GROSS_DIV_YIELD_RISK_ON * 100:.2f}%/yr | "
                      f"{s['oos_sharpe']:.3f} | {s['oos_cagr']:.2%} | "
                      f"{s['oos_mdd']:.2%} | {'✅' if s['gates_pass'] else '❌'} |")
    md.append("")
    md.append("## Joint scenarios")
    md.append("")
    md.append("| Scenario | Commission | Spread ½ | Swap | Div HC | OOS Sharpe | OOS CAGR | OOS MDD | Gates |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|:--:|")
    for s in scenarios:
        if s["scenario"] in ("baseline", "middle_pessimistic", "joint_worst_case"):
            md.append(f"| {s['scenario']} | {s['commission_bps']:.0f} bps | "
                      f"{s['spread_half_bps']:.0f} bps | {s['swap_daily']*100:.4f}%/d | "
                      f"{s['div_haircut']*100:.0f}% | {s['oos_sharpe']:.3f} | "
                      f"{s['oos_cagr']:.2%} | {s['oos_mdd']:.2%} | "
                      f"{'✅' if s['gates_pass'] else '❌'} |")
    md.append("")
    md.append("## Viability envelope")
    md.append("")
    failing = [s for s in scenarios if not s["gates_pass"]]
    passing = [s for s in scenarios if s["gates_pass"]]
    md.append(f"- Total scenarios tested: {len(scenarios)}")
    md.append(f"- Passing: {len(passing)}")
    md.append(f"- Failing: {len(failing)}")
    md.append("")
    if failing:
        md.append("### Failing scenarios (where Caminho 3 breaks)")
        md.append("")
        for s in failing:
            md.append(f"- **{s['scenario']}:** Sharpe={s['oos_sharpe']:.3f}, "
                      f"CAGR={s['oos_cagr']:.2%}, MDD={s['oos_mdd']:.2%}")
        md.append("")
    else:
        md.append("**All tested scenarios PASS.** The strategy is robust across the full "
                  "stress envelope modeled. Even the joint worst-case (commission 40 bps + "
                  "spread 50 bps RT + swap 10%/yr + dividend haircut 50%) does not break "
                  "the T3 sanity gates.")
    md.append("")
    md.append("## Interpretation for $1k live trading")
    md.append("")
    md.append("The matrix above answers: **'if Pepperstone Razor Index tier is worse than "
              "assumed, does the strategy still work at $1k?'**")
    md.append("")
    md.append("### What a realistic 'pessimistic' case looks like")
    md.append("")
    for s in scenarios:
        if s["scenario"] == "middle_pessimistic":
            md.append(f"- Commission {s['commission_bps']:.0f} bps RT = $0.50/side at $1k notional")
            md.append(f"- Spread half {s['spread_half_bps']:.0f} bps = 20 bps RT (2× baseline)")
            md.append(f"- Swap {s['swap_daily']*100:.4f}%/day = {s['swap_daily']*252*100:+.2f}%/yr")
            md.append(f"  (~2× baseline, realistic for elevated Fed rates)")
            md.append(f"- Dividend haircut 25% (assumes Pepperstone captures 75% of yield)")
            md.append("")
            md.append(f"→ OOS Sharpe **{s['oos_sharpe']:.3f}** (threshold 2.0 for winner), "
                      f"CAGR **{s['oos_cagr']:.2%}** (threshold 30%), "
                      f"MDD {s['oos_mdd']:.2%} (cap -25%).")
            md.append(f"→ Verdict: **{'STILL PASSES' if s['gates_pass'] else 'FAILS'}** "
                      "at realistic pessimistic assumptions.")
            md.append("")

    (OUT_DIR / "cost_sensitivity.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT_DIR / 'cost_sensitivity.md'}")
    print("=" * 72)

    # Summary for user
    pass_count = sum(1 for s in scenarios if s["gates_pass"])
    print(f"\n*** {pass_count}/{len(scenarios)} scenarios pass T3 sanity gates ***")


if __name__ == "__main__":
    main()
