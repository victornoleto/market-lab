"""Retro re-backtest of iters 001-011 on the new lh_56y dataset.

Each iter's `backtest.py` already exposes `DATASETS`, `CONFIGS`/`EFF_CONFIGS`,
and `run_dataset(ds, prices_full)`. We import each module, monkey-patch its
`DATASETS` to add an `lh_56y` entry whose start date is automatically set to
the first date where ALL of the iter's needed tickers have non-NaN values
(per-iter effective lh_56y window — iters using SPYSIM start in 1986, iters
using only VTSIM+bonds start in 1970, HAA-style iters using VWOSIM start in
~1994), then call `run_dataset("lh_56y", spliced_prices)` and merge the
returned `returns_series["lh_56y"]` + `runs["lh_56y"]` into the iter's
existing `results.json`.

Existing keys (`educational`, `vt_real`, `ndx_real`) are preserved untouched
— this is purely additive. Plotting downstream picks up the new key
automatically.

CLI:
    uv run python studies/long_term_portfolio/retro_rebacktest.py --iter 011
    uv run python studies/long_term_portfolio/retro_rebacktest.py --all
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from studies.long_term_portfolio.datasets import load_prices  # noqa: E402

ITER_ROOT = Path(__file__).parent / "iterations"
LH56_END = "2026-04-24"


def _find_entry_point(iter_dir: Path) -> Path:
    """Find the iter's main entry-point .py file.

    Convention: prefer ``backtest.py`` if present (iters 003+), otherwise
    fall back to the only non-``__init__`` .py file in the dir
    (iters 001-002 use bespoke names like ``baa_g12.py``).
    """
    bt = iter_dir / "backtest.py"
    if bt.exists():
        return bt
    candidates = [p for p in iter_dir.glob("*.py") if not p.name.startswith("_")]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise FileNotFoundError(f"no .py entry-point in {iter_dir}")
    raise ValueError(f"ambiguous entry-point in {iter_dir}: {[c.name for c in candidates]}")


def _load_iter_module(iter_dir: Path):
    """Import the iter's entry-point .py as a fresh module (one per call)."""
    bt_path = _find_entry_point(iter_dir)
    spec = importlib.util.spec_from_file_location(
        f"retro_iter_{iter_dir.name}", bt_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {bt_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_TICKER_LIKE_ATTRS = (
    "RAW_TICKERS", "ALL_TICKERS", "TICKERS",
    "OFFENSIVE_ASSETS", "DEFENSIVE_ASSETS", "DEFENSIVE_RISK_ASSETS",
    "OFFENSIVE", "DEFENSIVE", "CANARY",
    "CANARY_ASSETS", "CANARIES", "RISK_ASSETS",
)


def _needed_tickers(mod) -> set[str]:
    """Extract the union of tickers used by all of the iter's CONFIGS / module-level lists."""
    out: set[str] = set()
    eff = getattr(mod, "EFF_CONFIGS", None) or getattr(mod, "CONFIGS", None)
    if eff is not None:
        for v in eff.values():
            if isinstance(v, dict):
                out.update(v.keys())
            elif isinstance(v, (list, tuple)):
                out.update(v)
    # Always also union with module-level ticker-like attrs (catches HAA-style iters).
    for attr in _TICKER_LIKE_ATTRS:
        v = getattr(mod, attr, None)
        if isinstance(v, (list, tuple, set)):
            out.update(x for x in v if isinstance(x, str))
    if not out:
        raise AttributeError(
            f"could not infer needed tickers from {mod.__name__} "
            f"(no CONFIGS/EFF_CONFIGS dict and no recognised module-level list)"
        )
    return out


def _first_valid_date(prices: pd.DataFrame, tickers: set[str]) -> pd.Timestamp:
    """First date where ALL of the iter's needed *raw* tickers have non-NaN values.

    Iters that build SYNTHETIC tickers at runtime (e.g. NTSXSIM = 0.9 SPY +
    0.6 IEF − 0.5 cash) declare the synthetic name in their OFFENSIVE list
    even though only the underlying real tickers exist in the testfolio cache.
    We silently filter to columns that exist in `prices` — the synthetic
    will be constructed by the iter's own `build_prices()` from the
    underlying tickers, whose first-valid date IS in `prices`.
    """
    missing = [t for t in tickers if t not in prices.columns]
    cols = [t for t in tickers if t in prices.columns]
    if not cols:
        raise ValueError(
            f"no requested tickers in prices (missing all of {sorted(tickers)})"
        )
    if missing:
        # Heuristic: NTSX/NTSI/NTSE synths require SPYSIM/VEASIM/VWOSIM + IEFSIM + CASHX.
        for t in missing:
            if t.upper() in {"NTSXSIM", "NTSX_PROXY"}:
                cols.extend(["SPYSIM", "IEFSIM", "CASHX"])
            elif t.upper() in {"NTSI", "NTSISIM"}:
                cols.extend(["VEASIM", "IEFSIM", "CASHX"])
            elif t.upper() in {"NTSE", "NTSESIM"}:
                cols.extend(["VWOSIM", "IEFSIM", "CASHX"])
        cols = [c for c in dict.fromkeys(cols) if c in prices.columns]
    df = prices[cols].dropna(how="any")
    if df.empty:
        raise ValueError(f"no rows with all of {cols} non-NaN")
    return df.index[0]


def _json_default(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, pd.Timestamp):
        return str(obj)
    return str(obj)


def retro_iter(iter_prefix: str) -> None:
    matches = sorted(ITER_ROOT.glob(f"{iter_prefix}-*"))
    if not matches:
        raise FileNotFoundError(f"no iter dir for prefix {iter_prefix}")
    iter_dir = matches[0]
    print(f"\n=== retro re-backtest: {iter_dir.name} ===")

    mod = _load_iter_module(iter_dir)
    needed = _needed_tickers(mod)
    print(f"  needed tickers: {sorted(needed)}")

    prices_lh = load_prices("lh_56y")
    first = _first_valid_date(prices_lh, needed)
    print(f"  effective lh_56y start: {first.date()} → {LH56_END}")

    if not hasattr(mod, "DATASETS"):
        raise AttributeError(f"{iter_dir.name} has no DATASETS dict")
    # Mirror the schema used by the iter's existing 'educational' entry, if any
    # (some iters have extra keys like 'label' that run_dataset reads).
    template = mod.DATASETS.get("educational") or next(iter(mod.DATASETS.values()), {})
    new_entry = dict(template) if isinstance(template, dict) else {}
    new_entry.update({
        "start": str(first.date()),
        "end": LH56_END,
        "benchmark": template.get("benchmark", "VTSIM"),
        "label": f"lh_56y ({first.year}-{LH56_END[:4]})",
    })
    mod.DATASETS["lh_56y"] = new_entry

    if not hasattr(mod, "run_dataset"):
        raise AttributeError(f"{iter_dir.name}/backtest.py has no run_dataset()")
    ds_result = mod.run_dataset("lh_56y", prices_lh)

    new_returns_series: dict[str, dict] = {}
    new_runs: dict[str, dict] = {}

    # Shape A — iter 003+ (backtest.py): result["configs"][cfg_id] = {gross_returns, net_returns, ...}
    for cfg_id, cfg_data in ds_result.get("configs", {}).items():
        gr = cfg_data.get("gross_returns")
        nr = cfg_data.get("net_returns")
        if gr is None:
            continue
        gm = cfg_data.get("gross_metrics", {})
        nm = cfg_data.get("net_metrics", {})
        new_returns_series[cfg_id] = {
            "index": [str(d.date()) for d in gr.index],
            "gross_returns": [float(x) for x in gr.tolist()],
            "net_returns": [float(x) for x in (nr.tolist() if nr is not None else gr.tolist())],
        }
        new_runs[cfg_id] = {
            "sharpe": float(gm.get("sharpe", float("nan"))),
            "cagr": float(gm.get("cagr", float("nan"))),
            "mdd": float(gm.get("mdd", float("nan"))),
            "net_sharpe": float(nm.get("sharpe", float("nan"))) if nm else float("nan"),
            "net_cagr": float(nm.get("cagr", float("nan"))) if nm else float("nan"),
            "net_mdd": float(nm.get("mdd", float("nan"))) if nm else float("nan"),
        }

    # Shape B — iter 001/002 (single-config): result["returns_series"][cfg_id] = {index, net_returns}
    if not new_returns_series and "returns_series" in ds_result:
        gross_metrics = ds_result.get("gross_metrics", {})
        net_metrics = ds_result.get("metrics", {})
        for cfg_id, payload in ds_result["returns_series"].items():
            idx = pd.to_datetime(payload["index"])
            net = pd.Series(payload.get("net_returns", []), index=idx)
            gross = pd.Series(payload.get("gross_returns", net.values), index=idx)
            new_returns_series[cfg_id] = {
                "index": [str(d.date()) for d in idx],
                "gross_returns": [float(x) for x in gross.tolist()],
                "net_returns": [float(x) for x in net.tolist()],
            }
            new_runs[cfg_id] = {
                "sharpe": float(gross_metrics.get("sharpe", float("nan"))),
                "cagr": float(gross_metrics.get("cagr", float("nan"))),
                "mdd": float(gross_metrics.get("mdd", float("nan"))),
                "net_sharpe": float(net_metrics.get("sharpe", float("nan"))),
                "net_cagr": float(net_metrics.get("cagr", float("nan"))),
                "net_mdd": float(net_metrics.get("mdd", float("nan"))),
            }

    if not new_returns_series:
        print("  WARNING: no returns_series produced; skipping merge")
        return

    results_path = iter_dir / "results.json"
    if results_path.exists():
        results = json.loads(results_path.read_text())
    else:
        results = {}
    results.setdefault("returns_series", {})["lh_56y"] = new_returns_series
    results.setdefault("runs", {})["lh_56y"] = new_runs
    if "datasets" in results:
        # Add a slim datasets entry too so reports can reference it.
        results["datasets"]["lh_56y"] = {
            "start": str(first.date()),
            "end": LH56_END,
            "benchmark": new_entry["benchmark"],
            "selected_config": next(iter(new_runs.keys())),
            "configs": {c: {"gross_metrics": new_runs[c], "net_metrics": {}} for c in new_runs},
            "top5_by_sharpe": sorted(
                new_runs.keys(), key=lambda c: new_runs[c]["sharpe"], reverse=True
            )[:5],
            "pbo": ds_result.get("pbo", {}),
        }
    results_path.write_text(json.dumps(results, indent=2, default=_json_default) + "\n")

    top_cfg = max(new_runs, key=lambda c: new_runs[c]["sharpe"])
    print(f"  wrote {len(new_runs)} configs to results.json[lh_56y]")
    print(f"  top cfg: {top_cfg}  S={new_runs[top_cfg]['sharpe']:.3f}  "
          f"CAGR={new_runs[top_cfg]['cagr']*100:.2f}%  MDD={new_runs[top_cfg]['mdd']*100:.2f}%")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", default=None, help="iter prefix (e.g. 011); omit with --all")
    ap.add_argument("--all", action="store_true",
                    help="run for all iter dirs 001-NNN")
    args = ap.parse_args()

    if args.all:
        prefixes = sorted(p.name.split("-")[0] for p in ITER_ROOT.glob("[0-9][0-9][0-9]-*"))
        for p in prefixes:
            try:
                retro_iter(p)
            except Exception as e:
                print(f"  FAIL on iter {p}: {e}")
    elif args.iter:
        retro_iter(args.iter)
    else:
        ap.error("provide --iter NNN or --all")


if __name__ == "__main__":
    main()
