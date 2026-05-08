"""Plot strategy equity vs VT/QQQ buy-and-hold benchmark.

Reads `iterations/{iter}-*/results.json` and expects
`results["returns_series"][dataset][cfg_id] = {"index": [...], "net_returns": [...]}`.
Renders two panels per dataset:
  1. Equity curves, log scale (strategy vs benchmark)
  2. Rolling 1-year Sharpe differential (strategy - benchmark)

Saves `iterations/{iter}-*/plot_vs_benchmark_{dataset}.png`.

CLI:
    python studies/global_factor_tilt_loop/plot_helper.py --iter 001
    python studies/global_factor_tilt_loop/plot_helper.py --iter 001 --cfg my_cfg
    python studies/global_factor_tilt_loop/plot_helper.py --iter 001 --datasets vt_real ndx_real

`educational` dataset is skipped by default because different
iterations use different synthetic series as the educational window;
no single on-disk buy-and-hold benchmark covers all of them consistently.

Benchmark sources:
  - vt_real:  VTSIM from testfolio cache (proxy for VT until live pulled)
  - ndx_real: QQQ Tiingo daily parquet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
ITER_ROOT = Path(__file__).parent / "iterations"
TESTFOLIO_CACHE = REPO / "data/testfolio/cache/history.parquet"

# (path, label, source_kind) — source_kind is "tiingo" (price col) or "testfolio" (named col)
BENCHMARKS: dict[str, tuple[Path, str, str]] = {
    "vt_real":  (TESTFOLIO_CACHE, "VTSIM b&h (proxy for VT)", "testfolio:VTSIM"),
    "ndx_real": (REPO / "data/tiingo/daily/prices/QQQ.parquet", "QQQ buy-and-hold", "tiingo"),
}


def _find_iter_dir(iter_prefix: str) -> Path:
    matches = sorted(ITER_ROOT.glob(f"{iter_prefix}-*"))
    if not matches:
        raise FileNotFoundError(f"No iteration dir starting with {iter_prefix}")
    return matches[0]


def _pick_top_cfg(results: dict, ds: str) -> str | None:
    runs = results.get("runs", {}).get(ds, {})
    if not isinstance(runs, dict) or not runs:
        return None
    top_id, _ = max(runs.items(), key=lambda kv: kv[1].get("sharpe", float("-inf")))
    return top_id


def _strategy_returns(results: dict, ds: str, cfg_id: str) -> pd.Series | None:
    payload = results.get("returns_series", {}).get(ds, {}).get(cfg_id)
    if not payload:
        return None
    idx = pd.to_datetime(payload["index"])
    return pd.Series(payload["net_returns"], index=idx)


def _bench_returns(parquet_path: Path, start: str, end: str, source_kind: str = "tiingo") -> pd.Series:
    df = pd.read_parquet(parquet_path)
    df.index = pd.to_datetime(df.index)
    if source_kind.startswith("testfolio:"):
        col = source_kind.split(":", 1)[1]
    else:
        col = "adj_close" if "adj_close" in df.columns else "close"
    return df[col].loc[start:end].astype(float).pct_change().dropna()


def _equity(r: pd.Series) -> pd.Series:
    return (1.0 + r).cumprod()


def _sharpe(r: pd.Series) -> float:
    sd = r.std()
    return float(np.sqrt(252) * r.mean() / sd) if sd > 0 else float("nan")


def _cagr(r: pd.Series) -> float:
    eq = _equity(r)
    years = len(r) / 252.0
    return float(eq.iloc[-1] ** (1 / years) - 1) if years > 0 else float("nan")


def _mdd(r: pd.Series) -> float:
    eq = _equity(r)
    return float((1 - eq / eq.cummax()).max())


def _rolling_sharpe(r: pd.Series, window: int = 252) -> pd.Series:
    mu = r.rolling(window).mean()
    sd = r.rolling(window).std()
    return np.sqrt(252.0) * mu / sd


def plot_dataset(iter_dir: Path, ds: str, cfg_id: str, parquet: Path, bench_label: str,
                 source_kind: str = "tiingo") -> Path | None:
    results = json.loads((iter_dir / "results.json").read_text())
    r_strat = _strategy_returns(results, ds, cfg_id)
    if r_strat is None or len(r_strat) < 60:
        print(f"[{ds}] no usable returns series for cfg={cfg_id}, skip")
        return None

    start, end = str(r_strat.index[0].date()), str(r_strat.index[-1].date())
    r_bench = _bench_returns(parquet, start, end, source_kind)
    common = r_strat.index.intersection(r_bench.index)
    if len(common) < 60:
        print(f"[{ds}] insufficient overlap with {parquet.name}, skip")
        return None
    r_strat, r_bench = r_strat.loc[common], r_bench.loc[common]

    eq_s, eq_b = _equity(r_strat), _equity(r_bench)
    rs_diff = _rolling_sharpe(r_strat) - _rolling_sharpe(r_bench)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [2.2, 1.0]}, sharex=True
    )

    ax1.plot(eq_s.index, eq_s.values, color="#1f6feb", lw=1.8, label=f"Strategy {cfg_id}")
    ax1.plot(eq_b.index, eq_b.values, color="#666", lw=1.4, ls="--", label=bench_label)
    ax1.set_yscale("log")
    ax1.set_ylabel("Equity (growth of $1, log)")
    ax1.grid(True, which="both", alpha=0.25)
    ax1.legend(loc="upper left", fontsize=10)
    ax1.set_title(
        f"{iter_dir.name} — {ds}\n"
        f"strat: Sharpe {_sharpe(r_strat):.3f} · CAGR {_cagr(r_strat)*100:.2f}% · MDD {_mdd(r_strat)*100:.2f}%   |   "
        f"bench: Sharpe {_sharpe(r_bench):.3f} · CAGR {_cagr(r_bench)*100:.2f}% · MDD {_mdd(r_bench)*100:.2f}%",
        fontsize=10,
    )

    ax2.axhline(0, color="#888", lw=0.8)
    ax2.plot(rs_diff.index, rs_diff.values, color="#d35400", lw=1.2)
    ax2.fill_between(rs_diff.index, rs_diff.values, 0, where=rs_diff.values > 0,
                     color="#d35400", alpha=0.25, interpolate=True, label="strat ahead")
    ax2.fill_between(rs_diff.index, rs_diff.values, 0, where=rs_diff.values <= 0,
                     color="#1f6feb", alpha=0.25, interpolate=True, label="bench ahead")
    ax2.set_ylabel("Rolling 1y Sharpe Δ")
    ax2.grid(True, alpha=0.25)
    ax2.legend(loc="upper left", fontsize=9)
    ax2.set_xlabel("Date")

    fig.tight_layout()
    out = iter_dir / f"plot_vs_benchmark_{ds}.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_iter(iter_prefix: str, cfg_id: str | None = None,
              datasets: list[str] | None = None) -> list[Path]:
    iter_dir = _find_iter_dir(iter_prefix)
    results = json.loads((iter_dir / "results.json").read_text())
    targets = datasets or list(BENCHMARKS.keys())
    outs: list[Path] = []
    for ds in targets:
        if ds not in BENCHMARKS:
            print(f"[{ds}] no benchmark parquet registered, skip")
            continue
        if ds not in results.get("returns_series", {}):
            print(f"[{ds}] not in returns_series, skip")
            continue
        target_cfg = cfg_id or _pick_top_cfg(results, ds)
        parquet, label, source_kind = BENCHMARKS[ds]
        p = plot_dataset(iter_dir, ds, target_cfg, parquet, label, source_kind)
        if p is not None:
            print(f"[{ds}] wrote {p}")
            outs.append(p)
    return outs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", required=True, help="iteration prefix (e.g. '016')")
    ap.add_argument("--cfg", default=None,
                    help="config id; if omitted, auto-detect top (highest Sharpe) per dataset")
    ap.add_argument("--datasets", nargs="*", default=None,
                    help=f"subset of {list(BENCHMARKS.keys())}; default: all")
    args = ap.parse_args()
    plot_iter(args.iter, args.cfg, args.datasets)


if __name__ == "__main__":
    main()
