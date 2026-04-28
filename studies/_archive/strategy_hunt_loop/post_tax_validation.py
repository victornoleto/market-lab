"""Apply Lei 14.754 tax model to top-K long-window strategies.

Re-runs the unified driver from `long_window_validator.py` and applies
the 15% annual mark-to-market tax to compute post-tax (Sharpe, CAGR,
MDD). Generates `POST_TAX_VALIDATION.md` with side-by-side comparison.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studies/strategy_hunt_loop"))

from long_window_validator import (load_synth, returns_from_prices, metrics,  # noqa
                                    strat_iter004_vol_managed_spy,
                                    strat_iter005_variance_managed_spy,
                                    strat_iter006_vol_managed_60_40,
                                    strat_iter015_ntsx_static_90_60,
                                    strat_iter016_static_stack_vm,
                                    strat_iter035_static_stack_3leg,
                                    strat_iter074_ensemble_simplified)
from long_window_iter079 import run_scenario as run_iter079_scenario  # noqa
from tax_model import (apply_annual_mtm_tax, apply_entry_costs,  # noqa
                       EntryCosts, post_tax_metrics, LEI_14754_RATE)


STRATEGIES = {
    "iter004 vol_managed_spy": strat_iter004_vol_managed_spy,
    "iter005 variance_managed_spy": strat_iter005_variance_managed_spy,
    "iter006 vol_managed_60_40": strat_iter006_vol_managed_60_40,
    "iter015 ntsx_static_90_60": strat_iter015_ntsx_static_90_60,
    "iter016 static_stack_vm_hybrid": strat_iter016_static_stack_vm,
    "iter035 static_stack_3leg_SPY_ZROZ_GLD": strat_iter035_static_stack_3leg,
    "iter074 ensemble_simplified_to_iter016": strat_iter074_ensemble_simplified,
}


def _iter079_returns(df: pd.DataFrame) -> pd.Series:
    """iter 079 returns under scenario A (real proxies, BNDSIM/IEFSIM/VEASIM)."""
    import importlib.util
    p = ROOT / "studies/strategy_hunt_loop/iterations/079-2026-04-26-1100-multi-asset-topk-momentum/multi_asset_topk_momentum.py"
    spec = importlib.util.spec_from_file_location("iter079_mod", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    synth_map = {"SPY": "SPYSIM", "QQQ": "QQQSIM", "EFA": "VEASIM",
                 "TLT": "IEFSIM", "GLD": "GLDSIM", "AGG": "BNDSIM"}
    selectable = ["SPY", "QQQ", "EFA", "TLT", "GLD"]
    mod.SELECTABLE_ASSETS = selectable
    mod.ALL_SLEEVES = selectable + ["AGG"]

    daily_returns = {a: returns_from_prices(df[synth_map[a]])
                     for a in selectable + ["AGG"]}
    common = None
    for s in daily_returns.values():
        common = s.index if common is None else common.intersection(s.index)
    daily_returns = {k: v.loc[common] for k, v in daily_returns.items()}

    monthly_dates = mod.compute_monthly_rebalance_dates(common)
    monthly_prices = {}
    for a, ret in daily_returns.items():
        eq = (1.0 + ret).cumprod()
        eq.iloc[0] = 1.0
        monthly_prices[a] = eq.reindex(monthly_dates, method="ffill").dropna()
    lookback_df = mod.compute_lookback_returns_multi(monthly_prices, 12)
    signal_df = mod.top_k_signal(lookback_df, 1, 0.0)
    net = mod.compute_topk_returns(daily_returns, signal_df, trans_cost_bps=10.0)
    return net.dropna() if isinstance(net, pd.Series) else pd.Series(net, index=common).dropna()


STRATEGIES["iter079 multi_asset_topk (real proxies)"] = _iter079_returns


def compare_pre_post(label: str, returns: pd.Series, bench: pd.Series) -> dict:
    pre = {"sharpe": metrics(returns)["sharpe"],
           "cagr": metrics(returns)["cagr"],
           "mdd": metrics(returns)["mdd"]}
    post = post_tax_metrics(returns, rate=LEI_14754_RATE)
    bench_pre = metrics(bench)
    bench_post = post_tax_metrics(bench, rate=LEI_14754_RATE)
    return {
        "label": label,
        "pre": pre,
        "post": post,
        "bench_pre": bench_pre,
        "bench_post": bench_post,
        "edge_pre_sharpe": pre["sharpe"] - bench_pre["sharpe"],
        "edge_post_sharpe": post["sharpe"] - bench_post["sharpe"],
        "edge_pre_cagr_pp": (pre["cagr"] - bench_pre["cagr"]) * 100,
        "edge_post_cagr_pp": (post["cagr"] - bench_post["cagr"]) * 100,
    }


def main() -> None:
    df = load_synth()
    bench_spy = returns_from_prices(df["SPYSIM"])

    rows = []
    print(f"\n{'='*80}\nPost-tax (Lei 14.754, 15% annual MTM) on 40y SPYSIM benchmark\n{'='*80}")
    print(f"\nBenchmark SPYSIM:")
    bp = metrics(bench_spy)
    bpst = post_tax_metrics(bench_spy, rate=LEI_14754_RATE)
    print(f"  pre-tax:  Sharpe {bp['sharpe']:.3f}  CAGR {bp['cagr']*100:.2f}%  MDD {bp['mdd']*100:.2f}%")
    print(f"  post-tax: Sharpe {bpst['sharpe']:.3f}  CAGR {bpst['cagr']*100:.2f}%  MDD {bpst['mdd']*100:.2f}%")
    print(f"  → CAGR drag: {(bp['cagr']-bpst['cagr'])*100:.2f}pp")
    print()

    for label, fn in STRATEGIES.items():
        try:
            r = fn(df)
        except Exception as e:
            print(f"{label}: FAILED — {e}")
            continue
        cmp = compare_pre_post(label, r, bench_spy)
        rows.append(cmp)
        print(f"{label}:")
        print(f"  pre-tax:  Sharpe {cmp['pre']['sharpe']:.3f} (Δ {cmp['edge_pre_sharpe']:+.3f}) | CAGR {cmp['pre']['cagr']*100:.2f}% (Δ {cmp['edge_pre_cagr_pp']:+.2f}pp)")
        print(f"  post-tax: Sharpe {cmp['post']['sharpe']:.3f} (Δ {cmp['edge_post_sharpe']:+.3f}) | CAGR {cmp['post']['cagr']*100:.2f}% (Δ {cmp['edge_post_cagr_pp']:+.2f}pp)")

    # Cost projections
    print(f"\n{'='*80}\nEntry-cost projections ($10k initial + $1.5k/mo, 30y)\n{'='*80}")
    inter_costs = EntryCosts(iof_pct=0.0038, fx_spread_pct=0.0125,
                              ibkr_fixed_usd=0.0, etf_bid_ask_pct=0.0002)
    ibkr_costs = EntryCosts(iof_pct=0.0038, fx_spread_pct=0.0030,
                             ibkr_fixed_usd=2.0, etf_bid_ask_pct=0.0002)
    for label, costs in [("Inter Internacional (FX 1.25%)", inter_costs),
                          ("IBKR Lite + TransferBank (FX 0.30%)", ibkr_costs)]:
        cost = apply_entry_costs(initial_usd=10_000, monthly_aporte_usd=1500,
                                  costs=costs, n_years=30)
        print(f"{label}:")
        print(f"  total drag over 30y: ${cost['total_drag_usd']:,.0f} on ${cost['total_invested_usd']:,.0f} invested ({cost['drag_pct_of_invested']*100:.2f}%)")
        print(f"  initial drag (one-time): ${cost['initial_drag_usd']:,.2f}")
        print(f"  annual aporte drag: ${cost['annual_aporte_drag_usd']:,.2f}/yr")

    # Write report
    out = ROOT / "studies/strategy_hunt_loop/POST_TAX_VALIDATION.md"
    with out.open("w") as fh:
        fh.write("# Post-tax validation (Lei 14.754, 15% annual MTM)\n\n")
        fh.write(f"Generated: {pd.Timestamp.now().isoformat()}\n\n")
        fh.write("Applies 15% annual mark-to-market tax (Lei 14.754/2023, "
                 "effective 2024-01-01) to long-window 40y synth returns. "
                 "Loss years pay no tax; no carryforward across years.\n\n")
        fh.write("## Benchmark SPYSIM 40y — pre vs post tax\n\n")
        fh.write("| metric | pre-tax | post-tax | Δ |\n|---|---|---|---|\n")
        fh.write(f"| Sharpe | {bp['sharpe']:.3f} | {bpst['sharpe']:.3f} | {(bpst['sharpe']-bp['sharpe']):+.3f} |\n")
        fh.write(f"| CAGR | {bp['cagr']*100:.2f}% | {bpst['cagr']*100:.2f}% | {(bpst['cagr']-bp['cagr'])*100:+.2f}pp |\n")
        fh.write(f"| MDD | {bp['mdd']*100:.2f}% | {bpst['mdd']*100:.2f}% | {(bpst['mdd']-bp['mdd'])*100:+.2f}pp |\n\n")
        fh.write(f"**CAGR drag from tax: {(bp['cagr']-bpst['cagr'])*100:.2f}pp** "
                 f"({(bp['cagr']-bpst['cagr'])/bp['cagr']*100:.1f}% of pre-tax CAGR)\n\n")

        fh.write("## Strategy results (post-tax)\n\n")
        fh.write("| strategy | pre-tax (Sh / CAGR) | post-tax (Sh / CAGR) | post-tax edge vs SPYSIM |\n")
        fh.write("|---|---|---|---|\n")
        for r in rows:
            sh_pre = r['pre']['sharpe']; cg_pre = r['pre']['cagr']*100
            sh_post = r['post']['sharpe']; cg_post = r['post']['cagr']*100
            sh_edge = r['edge_post_sharpe']; cg_edge = r['edge_post_cagr_pp']
            dom = "✅ Sh+CAGR" if (sh_edge > 0 and cg_edge > 0) else (
                  "🟡 Sh-only" if sh_edge > 0 else "❌ neither")
            fh.write(f"| `{r['label']}` | {sh_pre:.3f} / {cg_pre:.2f}% | "
                     f"**{sh_post:.3f} / {cg_post:.2f}%** | Δ Sh {sh_edge:+.3f} / CAGR {cg_edge:+.2f}pp {dom} |\n")

        fh.write("\n## Entry-cost projections — $10k initial + $1.5k/mo over 30y\n\n")
        fh.write("| broker | total cost drag | as % of invested | initial cost | annual aporte cost |\n")
        fh.write("|---|---|---|---|---|\n")
        for label, costs in [("**Inter Internacional** (FX 1.25%)", inter_costs),
                              ("**IBKR Lite + TransferBank** (FX 0.30%)", ibkr_costs)]:
            cost = apply_entry_costs(initial_usd=10_000, monthly_aporte_usd=1500,
                                      costs=costs, n_years=30)
            fh.write(f"| {label} | ${cost['total_drag_usd']:,.0f} | "
                     f"{cost['drag_pct_of_invested']*100:.2f}% | "
                     f"${cost['initial_drag_usd']:,.2f} | "
                     f"${cost['annual_aporte_drag_usd']:,.2f}/yr |\n")
        fh.write("\nDifference: IBKR Lite + TransferBank saves "
                 f"${apply_entry_costs(10_000, 1500, inter_costs, 30)['total_drag_usd'] - apply_entry_costs(10_000, 1500, ibkr_costs, 30)['total_drag_usd']:,.0f} "
                 "over 30y (compounds in invested principal).\n\n")

        fh.write("## Caveats\n\n")
        fh.write("1. **Lei 14.754 regime confirmation**: this model assumes annual "
                 "MTM rate of 15%. For PF (individual) accounts at IBKR/Inter, "
                 "the regime may differ — consult contador.\n")
        fh.write("2. **Loss carryforward**: this model does NOT carry forward "
                 "losses across years. Real Lei 14.754 PJ rules allow it; PF rules don't.\n")
        fh.write("3. **MDD unchanged**: tax is annual, so peak-to-trough MDD within "
                 "a year is unaffected by tax (tax bites at year-end on net positive).\n")
        fh.write("4. **Sharpe slightly improves**: tax is asymmetric (positive years taxed, "
                 "negative years not), so post-tax volatility drops by more than mean → "
                 "Sharpe sometimes higher post-tax (counterintuitive but real).\n")
        fh.write("5. **30% US dividend withholding** NOT modeled separately because "
                 "synth tickers are total-return (dividends pre-reinvested into NAV).\n")

    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
