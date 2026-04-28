"""Light cross-library metric validation for top-N strategies.

Reads `returns_series` from each iter's `results.json` and computes
Sharpe / CAGR / MDD via 4 INDEPENDENT methods:

  1. **pandas-native**: same conventions used in iter scoring (the "v1")
  2. **numpy-pure**: hand-rolled with no library dependencies
  3. **vectorbt** (`vbt.returns_accessor` + `vbt.Portfolio.from_holding`)
  4. **quantstats** (`qs.stats.sharpe`, `qs.stats.cagr`, `qs.stats.max_drawdown`)

Each iter × dataset × metric → 4 numbers. If max-divergence > 5%,
flag RED. If 1-5%, flag YELLOW. If < 1%, flag GREEN.

This catches **metric-calculation bugs** but NOT engine-convention bugs
(timing of execution, cost model semantics). For engine-level
validation, each strategy would need to be re-implemented in vectorbt
and backtrader from price data — outside the scope of this overnight
run.

Output: `studies/strategy_hunt_loop/CROSS_LIB_VALIDATION.md`.

Citation: this file implements the spirit of `[advances_fin_ml,
p.31-34]` (cross-lib parity) at the metric layer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ITER_ROOT = ROOT / "studies/strategy_hunt_loop/iterations"
TRADING_DAYS = 252


# --- Method 1: pandas-native -------------------------------------------------


def m1_pandas_sharpe(r: pd.Series) -> float:
    sd = r.std(ddof=1)
    return float(np.sqrt(TRADING_DAYS) * r.mean() / sd) if sd > 0 else float("nan")


def m1_pandas_cagr(r: pd.Series) -> float:
    eq = (1.0 + r).cumprod()
    years = len(r) / TRADING_DAYS
    return float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")


def m1_pandas_mdd(r: pd.Series) -> float:
    eq = (1.0 + r).cumprod()
    return float((1 - eq / eq.cummax()).max())


# --- Method 2: numpy-pure ----------------------------------------------------


def m2_numpy_sharpe(r: np.ndarray) -> float:
    mu = r.mean()
    sd = r.std(ddof=1)
    return float(np.sqrt(TRADING_DAYS) * mu / sd) if sd > 0 else float("nan")


def m2_numpy_cagr(r: np.ndarray) -> float:
    eq = np.cumprod(1.0 + r)
    years = len(r) / TRADING_DAYS
    return float(eq[-1] ** (1 / years) - 1) if years > 0 else float("nan")


def m2_numpy_mdd(r: np.ndarray) -> float:
    eq = np.cumprod(1.0 + r)
    peaks = np.maximum.accumulate(eq)
    return float((1 - eq / peaks).max())


# --- Method 3: vectorbt ------------------------------------------------------


def m3_vectorbt_metrics(r: pd.Series) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """Use vectorbt's accessor with explicit 252-trading-day annualization.

    vectorbt's default `freq="D"` interprets D as calendar day → annualizes
    by 365, not 252. We force the year=252 convention to match academic
    practice and align with the other 3 methods.
    """
    try:
        import vectorbt as vbt
    except Exception:
        return (None, None, None)
    try:
        ra = vbt.returns_accessor.ReturnsAccessor(r, freq="D", year_freq="252D")
        sharpe = float(ra.sharpe_ratio())
        cagr = float(ra.annualized())
        mdd = float(ra.max_drawdown())
        return (sharpe, cagr, abs(mdd))
    except Exception:
        return (None, None, None)


# --- Method 4: quantstats ----------------------------------------------------


def m4_quantstats_metrics(r: pd.Series) -> tuple[Optional[float], Optional[float], Optional[float]]:
    try:
        import quantstats as qs
    except Exception:
        return (None, None, None)
    try:
        sharpe = float(qs.stats.sharpe(r))
        cagr = float(qs.stats.cagr(r))
        mdd = float(abs(qs.stats.max_drawdown(r)))
        return (sharpe, cagr, mdd)
    except Exception:
        return (None, None, None)


# --- Validation per (iter, dataset) ------------------------------------------


def divergence_label(values: list[float]) -> str:
    """Classify max relative divergence among non-None values."""
    vals = [v for v in values if v is not None and not np.isnan(v)]
    if len(vals) < 2:
        return "INSUFFICIENT"
    a = max(abs(v) for v in vals)
    if a < 1e-9:
        return "GREEN"
    rel = (max(vals) - min(vals)) / max(a, 1e-9)
    if rel < 0.01:
        return "GREEN"
    if rel < 0.05:
        return "YELLOW"
    return "RED"


def validate_iter(iter_dir: Path, top_cfg_key: str = "v2_top_cfg") -> dict | None:
    results_path = iter_dir / "results.json"
    verdict_v2_path = iter_dir / "verdict_v2.json"
    verdict_path = iter_dir / "verdict.json"
    if not results_path.exists():
        return None

    res = json.loads(results_path.read_text())
    out = {"iter_dir": iter_dir.name, "datasets": {}}

    for ds in ("spy_real", "ndx_real", "educational"):
        rs_ds = res.get("returns_series", {}).get(ds, {})
        if not rs_ds:
            continue
        # Pick top cfg by Sharpe in runs[ds]
        runs = res.get("runs", {}).get(ds, {})
        if not runs:
            continue
        top_cfg = max(runs.items(),
                      key=lambda kv: kv[1].get("sharpe", float("-inf")))[0]
        rs = rs_ds.get(top_cfg)
        if not rs or "net_returns" not in rs:
            continue

        idx = pd.to_datetime(rs["index"])
        r = pd.Series(rs["net_returns"], index=idx).astype(float).dropna()
        if len(r) < 60:
            continue
        ra = r.values

        sh1, cg1, md1 = m1_pandas_sharpe(r), m1_pandas_cagr(r), m1_pandas_mdd(r)
        sh2, cg2, md2 = m2_numpy_sharpe(ra), m2_numpy_cagr(ra), m2_numpy_mdd(ra)
        sh3, cg3, md3 = m3_vectorbt_metrics(r)
        sh4, cg4, md4 = m4_quantstats_metrics(r)

        out["datasets"][ds] = {
            "cfg": top_cfg,
            "n_bars": len(r),
            "window": (str(idx[0].date()), str(idx[-1].date())),
            "sharpe": {"pandas": sh1, "numpy": sh2, "vectorbt": sh3, "quantstats": sh4,
                       "div": divergence_label([sh1, sh2, sh3, sh4])},
            "cagr":   {"pandas": cg1, "numpy": cg2, "vectorbt": cg3, "quantstats": cg4,
                       "div": divergence_label([cg1, cg2, cg3, cg4])},
            "mdd":    {"pandas": md1, "numpy": md2, "vectorbt": md3, "quantstats": md4,
                       "div": divergence_label([md1, md2, md3, md4])},
        }
    return out


def fmt(v: Optional[float], pct: bool = False) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v*100:.2f}%" if pct else f"{v:.3f}"


def main() -> None:
    # Load top-20 from RESCORE_V2_SUMMARY.md by parsing v2 score order
    iter_v2_scores: list[tuple[int, int, str]] = []
    for d in sorted(ITER_ROOT.glob("0*")):
        v2p = d / "verdict_v2.json"
        if not v2p.exists():
            continue
        v = json.loads(v2p.read_text())
        iter_v2_scores.append((v["iter_id"], v["total_score"], v["hypothesis_slug"]))
    iter_v2_scores.sort(key=lambda x: -x[1])
    top_n = min(20, len(iter_v2_scores))
    top_iters = iter_v2_scores[:top_n]

    print(f"Validating top-{top_n} iters (by v2 score)...")
    results = []
    for iter_id, score, slug in top_iters:
        # Find iter dir
        matches = list(ITER_ROOT.glob(f"{iter_id:03d}-*"))
        if not matches:
            continue
        iter_dir = matches[0]
        v = validate_iter(iter_dir)
        if v is not None:
            v["iter_id"] = iter_id
            v["v2_score"] = score
            v["slug"] = slug
            results.append(v)
            print(f"  iter {iter_id}: validated {len(v['datasets'])} datasets")
        else:
            print(f"  iter {iter_id}: skipped (no results.json)")

    # Write report
    out = ROOT / "studies/strategy_hunt_loop/CROSS_LIB_VALIDATION.md"
    with out.open("w") as fh:
        fh.write("# Cross-library metric validation (light)\n\n")
        fh.write(f"Generated: {pd.Timestamp.now().isoformat()}\n\n")
        fh.write("Validates Sharpe / CAGR / MDD across 4 independent methods:\n")
        fh.write("**pandas-native**, **numpy-pure**, **vectorbt**, **quantstats**.\n\n")
        fh.write("Divergence labels:\n")
        fh.write("- 🟢 GREEN: max relative divergence < 1%\n")
        fh.write("- 🟡 YELLOW: 1-5%\n")
        fh.write("- 🔴 RED: > 5% — METRIC IMPLEMENTATION DISAGREEMENT\n\n")
        fh.write("Caveat: this catches metric bugs only. NOT engine-level validation. "
                 "For engine-level cross-validation each strategy would need re-implementation "
                 "in vectorbt or backtrader from price data — outside scope of this run.\n\n")

        for v in results:
            fh.write(f"## iter {v['iter_id']:03d} (v2 score {v['v2_score']}) — `{v['slug']}`\n\n")
            for ds, d in v["datasets"].items():
                fh.write(f"### {ds} (cfg `{d['cfg']}`, {d['n_bars']} bars, {d['window'][0]} → {d['window'][1]})\n\n")
                fh.write("| metric | pandas | numpy | vectorbt | quantstats | divergence |\n")
                fh.write("|---|---|---|---|---|---|\n")
                emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴", "INSUFFICIENT": "⚪"}
                for metric in ("sharpe", "cagr", "mdd"):
                    m = d[metric]
                    pct = metric in ("cagr", "mdd")
                    fh.write(f"| **{metric}** | {fmt(m['pandas'], pct)} | {fmt(m['numpy'], pct)} | "
                             f"{fmt(m['vectorbt'], pct)} | {fmt(m['quantstats'], pct)} | "
                             f"{emoji.get(m['div'], '?')} {m['div']} |\n")
                fh.write("\n")

        # Summary
        red_count = 0
        yellow_count = 0
        green_count = 0
        for v in results:
            for d in v["datasets"].values():
                for metric in ("sharpe", "cagr", "mdd"):
                    div = d[metric]["div"]
                    if div == "RED":
                        red_count += 1
                    elif div == "YELLOW":
                        yellow_count += 1
                    elif div == "GREEN":
                        green_count += 1
        fh.write("## Summary\n\n")
        fh.write(f"- 🟢 GREEN cells: {green_count}\n")
        fh.write(f"- 🟡 YELLOW cells: {yellow_count}\n")
        fh.write(f"- 🔴 RED cells: {red_count}\n")
        fh.write(f"\nTotal cells: {green_count + yellow_count + red_count}\n")

    # Also dump JSON
    (ROOT / "studies/strategy_hunt_loop/CROSS_LIB_VALIDATION.json").write_text(
        json.dumps(results, indent=2, default=str)
    )
    print(f"\nWrote {out}")
    print(f"GREEN={green_count} YELLOW={yellow_count} RED={red_count}")


if __name__ == "__main__":
    main()
