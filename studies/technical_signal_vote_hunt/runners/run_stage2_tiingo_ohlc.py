"""Stage 2 Tiingo OHLC local diagnostic for technical vote candidates.

Stage 2 is real-ETF/inception-window research. It uses Tiingo adjusted OHLC for
the signal asset and adjusted-close returns for risk-on/off legs. The default
workflow replays a Stage 1 QQQ incumbent and tests a one-edit OHLC neighborhood;
it is discovery, not a deploy verdict `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import itertools
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from studies.technical_signal_vote_hunt.core import (
    adjusted_ohlc,
    build_close_only_signals,
    build_ohlc_signals,
    daily_returns,
)
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import (
    _metrics_row_np,
    _simulate_on_off_np,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = REPO_ROOT / "studies/technical_signal_vote_hunt/results/stage2_tiingo_ohlc"

DEFAULT_BASE_SIGNALS = "px_gt_sma10|px_gt_sma20|px_gt_ema100|px_gt_ema200|px_gt_ema250|roc20_gt_0|roc60_gt_0"


@dataclass(frozen=True)
class Stage2Branch:
    branch: str
    signal_ticker: str
    risk_on_ticker: str
    benchmark_ticker: str
    risk_on_label: str


BRANCHES: dict[tuple[str, str], Stage2Branch] = {
    ("SPY", "SSO_2x"): Stage2Branch("SPY", "SPY", "SSO", "SPY", "SSO_2x"),
    ("SPY", "UPRO_3x"): Stage2Branch("SPY", "SPY", "UPRO", "SPY", "UPRO_3x"),
    ("QQQ", "QLD_2x"): Stage2Branch("QQQ", "QQQ", "QLD", "QQQ", "QLD_2x"),
    ("QQQ", "TQQQ_3x"): Stage2Branch("QQQ", "QQQ", "TQQQ", "QQQ", "TQQQ_3x"),
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Stage 2 Tiingo OHLC local diagnostic")
    p.add_argument("--branch", choices=["SPY", "QQQ"], default="QQQ")
    p.add_argument("--risk-on", choices=["SSO_2x", "UPRO_3x", "QLD_2x", "TQQQ_3x"], default="QLD_2x")
    p.add_argument("--off-leg", choices=["ZROZ", "BIL", "CASH_USD"], default="ZROZ")
    p.add_argument("--base-signals", default=DEFAULT_BASE_SIGNALS)
    p.add_argument("--base-k", type=int, default=5)
    p.add_argument("--storage-root", type=Path, default=REPO_ROOT / "data/tiingo")
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--out-name", default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    key = (args.branch, args.risk_on)
    if key not in BRANCHES:
        raise SystemExit(f"Unsupported branch/risk-on pair: {key}")

    started = time.perf_counter()
    storage = TiingoStorage(args.storage_root)
    spec = BRANCHES[key]
    out_dir = OUT_ROOT / (args.out_name or f"{args.branch}_{args.risk_on}_{args.off_leg}_local")
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    prepared = _prepare(spec, args.off_leg, storage)
    rows = list(_iter_local_rows(prepared, args.base_signals, args.base_k))
    results = pd.DataFrame(rows).sort_values(["sortino", "cagr", "calmar"], ascending=[False, False, False])
    results.to_csv(tables_dir / "stage2_local_results.csv", index=False)

    summary = _summary(prepared, results, args, elapsed=time.perf_counter() - started)
    (out_dir / "REPORT.md").write_text(summary, encoding="utf-8")
    manifest = {
        "stage": "stage2_tiingo_ohlc",
        "branch": args.branch,
        "risk_on": args.risk_on,
        "off_leg": args.off_leg,
        "base_signals": args.base_signals,
        "base_k": args.base_k,
        "configs_tested": int(len(results)),
        "signal_count": int(len(prepared.signal_names)),
        "ohlc_signal_count": int(len(prepared.ohlc_signal_names)),
        "start": str(prepared.dates.min().date()),
        "end": str(prepared.dates.max().date()),
        "elapsed_seconds": time.perf_counter() - started,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"done configs={len(results):,} output={out_dir / 'REPORT.md'}", flush=True)
    return 0


@dataclass(frozen=True)
class Prepared:
    spec: Stage2Branch
    off_leg: str
    dates: pd.DatetimeIndex
    signal_names: list[str]
    ohlc_signal_names: list[str]
    signal_matrix: np.ndarray
    on_returns: np.ndarray
    off_returns: np.ndarray
    benchmark_returns: np.ndarray


def _prepare(spec: Stage2Branch, off_leg: str, storage: TiingoStorage) -> Prepared:
    signal_raw = storage.read(spec.signal_ticker, frequency="daily")
    on_raw = storage.read(spec.risk_on_ticker, frequency="daily")
    bench_raw = storage.read(spec.benchmark_ticker, frequency="daily")

    signal_ohlc = adjusted_ohlc(signal_raw)
    close_signals = build_close_only_signals(signal_ohlc["close"])
    ohlc_signals = build_ohlc_signals(signal_ohlc)
    signal_map = {**close_signals, **ohlc_signals}
    names = list(signal_map)

    on_returns = daily_returns(on_raw["adj_close"])
    if off_leg == "CASH_USD":
        off_returns = pd.Series(0.0, index=on_raw.index, name="CASH_USD")
    else:
        off_raw = storage.read(off_leg, frequency="daily")
        off_returns = daily_returns(off_raw["adj_close"])
    bench_returns = daily_returns(bench_raw["adj_close"])
    aligned = pd.concat(
        {
            "on": on_returns,
            "off": off_returns,
            "bench": bench_returns,
            **{f"s_{name}": signal_map[name] for name in names},
        },
        axis=1,
        sort=False,
    ).dropna(subset=["on", "off", "bench"])
    sig_cols = [f"s_{name}" for name in names]
    return Prepared(
        spec=spec,
        off_leg=off_leg,
        dates=aligned.index,
        signal_names=names,
        ohlc_signal_names=list(ohlc_signals),
        signal_matrix=aligned[sig_cols].to_numpy(dtype=np.float32),
        on_returns=aligned["on"].to_numpy(dtype=np.float64),
        off_returns=aligned["off"].to_numpy(dtype=np.float64),
        benchmark_returns=aligned["bench"].to_numpy(dtype=np.float64),
    )


def _iter_local_rows(prepared: Prepared, base_signals: str, base_k: int):
    base = [s for s in base_signals.split("|") if s]
    missing = [s for s in base if s not in prepared.signal_names]
    if missing:
        raise SystemExit(f"Unknown base signal(s): {missing}")
    seen: set[tuple[str, int, str]] = set()
    all_names = prepared.signal_names
    candidates: list[tuple[str, str, list[str]]] = [("base", "none", base)]
    candidates += [("drop1", f"-{sig}", [s for s in base if s != sig]) for sig in base]
    candidates += [("add1_ohlc", f"+{sig}", base + [sig]) for sig in prepared.ohlc_signal_names if sig not in base]
    for old, new in itertools.product(base, prepared.ohlc_signal_names):
        if new not in base:
            candidates.append(("swap1_ohlc", f"-{old}+{new}", [new if s == old else s for s in base]))

    for neighborhood, change, signals in candidates:
        if not signals:
            continue
        ordered = [s for s in all_names if s in set(signals)]
        n = len(ordered)
        idx = [prepared.signal_names.index(s) for s in ordered]
        sub = prepared.signal_matrix[:, idx]
        valid = ~np.isnan(sub).any(axis=1)
        counts = np.nansum(sub, axis=1)
        for k in range(1, n + 1):
            key = ("|".join(ordered), k, neighborhood)
            if key in seen:
                continue
            seen.add(key)
            raw_signal = np.where(valid, counts >= k, False)
            returns = _simulate_on_off_np(raw_signal, prepared.on_returns, prepared.off_returns)
            row = _metrics_row_np(
                returns=returns,
                benchmark_returns=prepared.benchmark_returns,
                dates=prepared.dates,
                label="stage2_local",
                branch=prepared.spec.branch,
                risk_on=prepared.spec.risk_on_label,
                n=n,
                k=k,
                signals="|".join(ordered),
            )
            row["neighborhood"] = neighborhood
            row["change"] = change
            yield row


def _summary(prepared: Prepared, results: pd.DataFrame, args: argparse.Namespace, elapsed: float) -> str:
    base_mask = (results["neighborhood"] == "base") & (results["k"] == args.base_k)
    base = results.loc[base_mask].head(1)
    lines = [
        "# Stage 2 Tiingo OHLC Local Results",
        "",
        "Status: real-inception Tiingo OHLC diagnostic. This is not a validation verdict.",
        "",
        f"Branch: `{prepared.spec.branch}`",
        f"Risk-on: `{prepared.spec.risk_on_label}` (`{prepared.spec.risk_on_ticker}`)",
        f"Off leg: `{prepared.off_leg}`",
        f"Window: `{prepared.dates.min().date()}` to `{prepared.dates.max().date()}` ({len(prepared.dates):,} bars)",
        f"Signals: {len(prepared.signal_names)} total, {len(prepared.ohlc_signal_names)} OHLC-derived",
        f"Configs tested: {len(results):,}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "## Base Replay",
        "",
        base[["neighborhood", "change", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].to_markdown(index=False, floatfmt=".4f") if len(base) else "Base row not found.",
        "",
        "## Top Local Candidates",
        "",
        results.head(args.top)[["neighborhood", "change", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Method Notes",
        "",
        "- Tiingo OHLC is adjusted with `adj_close / close` before high/low indicators `[quant_trading_chan, p.37]`.",
        "- Vote signals are lagged one bar before earning returns to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.",
        "- This is local discovery on a shorter real-ETF window; final claims still require DSR/PBO/WF/OOS/FWD/bootstrap `[advances_fin_ml, p.208-211]`.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
