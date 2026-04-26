"""Long-window 40y synth re-run of iter 079 winner with substitutions.

iter 079 uses universe {SPY, QQQ, EFA, TLT, GLD} + AGG (defensive). Synth
data has {SPYSIM, QQQSIM, GLDSIM, ZROZSIM} but NO EFA (international
developed) and NO AGG analog. Two scenarios tested:

  * **Scenario A** (4-asset, ZROZSIM-as-bond): drop EFA, use ZROZSIM
    as both TLT and AGG. Universe shrinks 5→4 selectable.
  * **Scenario B** (5-asset, EFA=QQQSIM-as-proxy): use QQQSIM as the
    international proxy. Highly imperfect (QQQ ≠ EFA), documented.

Both are PARTIAL validation. Cleanest answer requires MSCI-EAFE synth
back to 1986 which testfolio doesn't ship.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies/strategy_hunt_loop"))

from long_window_validator import load_synth, returns_from_prices, metrics  # noqa


def _import_iter079_module():
    p = ROOT / "studies/strategy_hunt_loop/iterations/079-2026-04-26-1100-multi-asset-topk-momentum/multi_asset_topk_momentum.py"
    spec = importlib.util.spec_from_file_location("iter079_mod", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_scenario(scenario: str) -> dict:
    mod = _import_iter079_module()
    df = load_synth()

    # Map iter 079's SELECTABLE_ASSETS (5) + AGG to synth tickers
    if scenario == "A_4asset":
        # Drop EFA. Use ZROZSIM for both TLT and AGG.
        synth_map = {"SPY": "SPYSIM", "QQQ": "QQQSIM", "TLT": "ZROZSIM",
                     "GLD": "GLDSIM", "AGG": "ZROZSIM"}
        selectable = ["SPY", "QQQ", "TLT", "GLD"]
    elif scenario == "B_5asset_qqq_as_efa":
        synth_map = {"SPY": "SPYSIM", "QQQ": "QQQSIM", "EFA": "QQQSIM",
                     "TLT": "ZROZSIM", "GLD": "GLDSIM", "AGG": "ZROZSIM"}
        selectable = ["SPY", "QQQ", "EFA", "TLT", "GLD"]
    else:
        raise ValueError(scenario)

    # Monkey-patch the module globals to use our universe
    mod.SELECTABLE_ASSETS = selectable
    mod.ALL_SLEEVES = selectable + ["AGG"]

    # Build daily returns dict matching iter 079's expected interface
    daily_returns = {a: returns_from_prices(df[synth_map[a]])
                     for a in selectable + ["AGG"]}
    # Align all to common index (intersection)
    common = None
    for s in daily_returns.values():
        common = s.index if common is None else common.intersection(s.index)
    daily_returns = {k: v.loc[common] for k, v in daily_returns.items()}

    # iter 079 best cfg: top_k=1, lookback_months=12 (best per verdict)
    # Per iter 079 verdict: best_cfg_id is "topk1_lb12_th0.0" or similar
    cfg = {"top_k": 1, "lookback_months": 12, "abs_threshold": 0.0,
           "trans_cost_bps": 10.0}

    # Compute monthly rebalance dates + signal
    monthly_dates = mod.compute_monthly_rebalance_dates(common)
    # Build monthly prices dict from daily returns (start at 1.0, compound)
    monthly_prices = {}
    for a, ret in daily_returns.items():
        eq = (1.0 + ret).cumprod()
        eq.iloc[0] = 1.0  # initial price
        monthly_prices[a] = eq.reindex(monthly_dates, method="ffill").dropna()
    lookback_df = mod.compute_lookback_returns_multi(monthly_prices, cfg["lookback_months"])
    signal_df = mod.top_k_signal(lookback_df, cfg["top_k"], cfg["abs_threshold"])
    net = mod.compute_topk_returns(daily_returns, signal_df,
                                    trans_cost_bps=cfg["trans_cost_bps"])
    r = pd.Series(net, index=common).dropna() if not isinstance(net, pd.Series) else net.dropna()

    m = metrics(r, f"iter079_{scenario}")
    bench = metrics(returns_from_prices(df["SPYSIM"]), "SPYSIM b&h")

    return {
        "scenario": scenario,
        "cfg": cfg,
        "selectable": selectable,
        "synth_map": synth_map,
        "metrics": m,
        "bench": bench,
        "sharpe_delta": m["sharpe"] - bench["sharpe"],
        "cagr_delta_pp": (m["cagr"] - bench["cagr"]) * 100,
        "mdd_delta_pp": (m["mdd"] - bench["mdd"]) * 100,
    }


def main() -> None:
    results = []
    for scen in ["A_4asset", "B_5asset_qqq_as_efa"]:
        try:
            r = run_scenario(scen)
            results.append(r)
            m = r["metrics"]
            print(f"\n=== iter 079 — scenario {scen} ===")
            print(f"  selectable: {r['selectable']}")
            print(f"  cfg: top_k={r['cfg']['top_k']}, lookback={r['cfg']['lookback_months']}m, "
                  f"abs_th={r['cfg']['abs_threshold']}, cost={r['cfg']['trans_cost_bps']}bps")
            print(f"  Sharpe {m['sharpe']:.3f} (Δ vs SPYSIM b&h {r['sharpe_delta']:+.3f})")
            print(f"  CAGR   {m['cagr']*100:.2f}% (Δ {r['cagr_delta_pp']:+.2f}pp)")
            print(f"  MDD    {m['mdd']*100:.2f}% (Δ {r['mdd_delta_pp']:+.2f}pp)")
            print(f"  bars   {m['n_bars']} ({m['start']} → {m['end']})")
        except Exception as e:
            print(f"\n=== iter 079 — {scen}: FAILED ===")
            import traceback
            traceback.print_exc()

    # Append to LONG_WINDOW_VALIDATION.md
    if results:
        out = ROOT / "studies/strategy_hunt_loop/LONG_WINDOW_VALIDATION_iter079.md"
        with out.open("w") as fh:
            fh.write("# Long-window iter 079 — winner partial validation\n\n")
            fh.write("iter 079 uses universe {SPY, QQQ, EFA, TLT, GLD} + AGG. "
                     "Synth data lacks EFA + AGG analogs. Two substitution scenarios:\n\n")
            for r in results:
                m = r["metrics"]
                fh.write(f"## Scenario `{r['scenario']}`\n\n")
                fh.write(f"- Selectable: {r['selectable']}\n")
                fh.write(f"- Synth substitutions: `{r['synth_map']}`\n")
                fh.write(f"- Config: top_k={r['cfg']['top_k']}, lookback={r['cfg']['lookback_months']}m, "
                         f"abs_threshold={r['cfg']['abs_threshold']}, cost={r['cfg']['trans_cost_bps']}bps\n\n")
                fh.write(f"| metric | value | Δ vs SPYSIM b&h |\n|---|---|---|\n")
                fh.write(f"| Sharpe | {m['sharpe']:.3f} | {r['sharpe_delta']:+.3f} |\n")
                fh.write(f"| CAGR | {m['cagr']*100:.2f}% | {r['cagr_delta_pp']:+.2f}pp |\n")
                fh.write(f"| MDD | {m['mdd']*100:.2f}% | {r['mdd_delta_pp']:+.2f}pp |\n\n")
            fh.write("## Reading the results\n\n")
            fh.write("- Both scenarios are partial. Scenario A drops the international leg "
                     "(EFA), so it tests the 4-asset variant rather than the original 5-asset. "
                     "Scenario B uses QQQSIM as a stand-in for EFA, which is wrong "
                     "(QQQ is US large-tech, not international developed) but at least "
                     "preserves the 5-asset structure.\n")
            fh.write("- ZROZSIM substitutes for both TLT and AGG (long-bond proxy). "
                     "AGG is shorter duration, so this overstates the bond leg's volatility "
                     "contribution.\n")
            fh.write("- Treat as **directional evidence**, not exact validation.\n")
        print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
