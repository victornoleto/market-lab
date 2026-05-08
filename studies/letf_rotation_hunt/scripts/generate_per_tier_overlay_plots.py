#!/usr/bin/env python3
"""Generate per-tier all-configs equity and relative-to-SPY overlay plots.

For each tier (T1, T2, T3, T4, T5), collects all configs that appeared in
that tier's iters, recomputes their equity curves, and produces a single
plots: normalized equity growth and renormalised ratio to SPY. Top-5 configs
(by lh_56y Sharpe) are colored bold; rest are faded.

Output:
    reports/tier_1_plots/tier1_all_configs_equity.png
    reports/tier_1_plots/tier1_all_configs_relative_to_spy.png
    reports/tier_2_plots/tier2_all_configs_equity.png
    reports/tier_2_plots/tier2_all_configs_relative_to_spy.png
    ...
    reports/tier_5_plots/tier5_all_configs_relative_to_spy.png

Mirrors ``STUDY_top20_relative_to_spy.png`` but per tier, per user request
2026-05-06.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from studies.letf_rotation_hunt.data_loader import load_ffr_daily, load_testfolio_series
from studies.letf_rotation_hunt.plot_helper import plot_tier_equity_overlay, plot_tier_relative_to_spy
from studies.letf_rotation_hunt.run_iter_t1 import _run_single_config
from studies.letf_rotation_hunt.run_iter_t2 import _run_single_basket_config
from studies.letf_rotation_hunt.run_iter_t3 import _run_single_composite_config
from studies.letf_rotation_hunt.run_iter_t4 import _run_single_xs_config
from studies.letf_rotation_hunt.run_iter_t5 import _run_single_voltarget_config

ITER_DIR = PROJECT_ROOT / "studies/letf_rotation_hunt/iterations"
REPORTS_DIR = PROJECT_ROOT / "studies/letf_rotation_hunt/reports"

DISPATCH_BY_TIER = {
    "T1": _run_single_config,
    "T2": _run_single_basket_config,
    "T3": _run_single_composite_config,
    "T4": _run_single_xs_config,
    "T5": _run_single_voltarget_config,
}

# Output filenames per tier prefix
TIER_OUT_DIRS = {
    "T1": ("tier_1_plots", "tier1_all_configs_equity.png", "tier1_all_configs_relative_to_spy.png"),
    "T2": ("tier_2_plots", "tier2_all_configs_equity.png", "tier2_all_configs_relative_to_spy.png"),
    "T3": ("tier_3_plots", "tier3_all_configs_equity.png", "tier3_all_configs_relative_to_spy.png"),
    "T4": ("tier_4_plots", "tier4_all_configs_equity.png", "tier4_all_configs_relative_to_spy.png"),
    "T5": ("tier_5_plots", "tier5_all_configs_equity.png", "tier5_all_configs_relative_to_spy.png"),
}

# Friendly tier title
TIER_TITLES = {
    "T1": "T1 — Single-LETF Gayed rotation",
    "T2": "T2 — HFEA basket family",
    "T3": "T3 — Composite signal family + extended grids",
    "T4": "T4 — Cross-sectional rotation",
    "T5": "T5 — Carver vol-target",
}


def collect_tier_configs(tier_prefix: str) -> list[dict]:
    """Walk iterations/, return list of config dicts that ran in tier_prefix."""
    out: list[dict] = []
    seen_names: dict[str, dict] = {}  # de-dup by config_name (keep highest Sharpe)
    for d in sorted(ITER_DIR.glob("0*-*")):
        vp = d / "verdict.json"
        if not vp.exists():
            continue
        try:
            v = json.loads(vp.read_text())
        except json.JSONDecodeError:
            continue
        tier = v.get("tier", "?")
        if not tier.startswith(tier_prefix):
            continue
        configs_lookup = {c["name"]: c for c in v.get("configs_tested", [])}
        for r in v.get("results", []):
            if "error" in r:
                continue
            name = r.get("config_name", "?")
            sh = r.get("metrics_gross", {}).get("lh_56y", {}).get("sharpe")
            if sh is None or not isinstance(sh, (int, float)) or sh != sh:
                continue
            cfg = configs_lookup.get(name)
            if cfg is None:
                continue
            entry = {
                "name": name,
                "tier": tier,
                "sharpe_lh56y": float(sh),
                "cfg": cfg,
            }
            prev = seen_names.get(name)
            if prev is None or entry["sharpe_lh56y"] > prev["sharpe_lh56y"]:
                seen_names[name] = entry
    out = sorted(seen_names.values(), key=lambda r: -r["sharpe_lh56y"])
    return out


def recompute_equity(entry: dict, ffr_daily) -> object:
    tier_prefix = entry["tier"][:2]
    dispatch = DISPATCH_BY_TIER.get(tier_prefix)
    if dispatch is None:
        return None
    try:
        result = dispatch(entry["cfg"], ["lh_56y"], ffr_daily, n_trials_local=1)
        return result.get("_equity")
    except Exception as e:
        print(f"  FAIL {entry['name']}: {type(e).__name__}: {e}")
        return None


def main() -> int:
    print("Loading FFR + SPY...")
    ffr = load_ffr_daily()
    spy = load_testfolio_series("SPYSIM").dropna()

    for tier_prefix in ["T1", "T2", "T3", "T4", "T5"]:
        print(f"\n=== Tier {tier_prefix} ===")
        configs = collect_tier_configs(tier_prefix)
        print(f"  {len(configs)} unique configs")
        if not configs:
            continue

        equities: dict[str, "pd.Series"] = {}
        rank_by: dict[str, float] = {}
        for c in configs:
            eq = recompute_equity(c, ffr)
            if eq is None:
                continue
            equities[c["name"]] = eq
            rank_by[c["name"]] = c["sharpe_lh56y"]
        print(f"  Recomputed {len(equities)} equities")

        out_subdir, equity_name, relative_name = TIER_OUT_DIRS[tier_prefix]
        out_dir = REPORTS_DIR / out_subdir
        out_dir.mkdir(parents=True, exist_ok=True)
        equity_path = out_dir / equity_name
        relative_path = out_dir / relative_name
        plot_tier_equity_overlay(
            equity_curves=equities,
            spy_equity=spy,
            out_path=equity_path,
            title=f"{TIER_TITLES[tier_prefix]} (all configs equity growth)",
            top_n_bold=5,
            rank_by=rank_by,
        )
        plot_tier_relative_to_spy(
            equity_curves=equities,
            spy_equity=spy,
            out_path=relative_path,
            title=f"{TIER_TITLES[tier_prefix]} (all configs ratio to SPY)",
            top_n_bold=5,
            rank_by=rank_by,
        )
        print(f"  Wrote: {equity_path} ({equity_path.stat().st_size} bytes)")
        print(f"  Wrote: {relative_path} ({relative_path.stat().st_size} bytes)")

    print("\n✓ Per-tier overlay plots complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
