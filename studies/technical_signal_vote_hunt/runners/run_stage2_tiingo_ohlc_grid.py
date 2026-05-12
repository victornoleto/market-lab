"""Stage 2 Tiingo OHLC exact-grid runner.

This runner evaluates capped `n`/`k` grids over Stage 2 Tiingo adjusted-OHLC
signals and keeps only the top-N rows in memory. It is still discovery, not a
validation verdict; all evaluated configs must be counted in later DSR trial
accounting `[advances_fin_ml, p.222-223]`.
"""
from __future__ import annotations

import argparse
import heapq
import itertools
import json
import math
import time
from pathlib import Path
from dataclasses import replace

import numpy as np
import pandas as pd

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import (
    FIELDNAMES,
    _metrics_row_np,
    _simulate_on_off_np,
)
from studies.technical_signal_vote_hunt.runners.run_stage2_tiingo_ohlc import (
    BRANCHES,
    OUT_ROOT,
    Prepared,
    _prepare,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Stage 2 Tiingo OHLC exact grid")
    p.add_argument("--branch", choices=["SPY", "QQQ"], default="QQQ")
    p.add_argument("--risk-ons", default="QLD_2x,TQQQ_3x")
    p.add_argument("--off-leg", choices=["ZROZ", "BIL", "CASH_USD"], default="ZROZ")
    p.add_argument("--extra-lag-days", type=int, default=0)
    p.add_argument("--allow-redundant-signals", action="store_true")
    p.add_argument("--min-n", type=int, default=1)
    p.add_argument("--max-n", type=int, default=5)
    p.add_argument("--top", type=int, default=200)
    p.add_argument("--progress-every", type=int, default=100_000)
    p.add_argument("--storage-root", type=Path, default=REPO_ROOT / "data/tiingo")
    p.add_argument("--out-name", default=None)
    p.add_argument("--allow-huge", action="store_true")
    p.add_argument("--huge-threshold", type=int, default=20_000_000)
    p.add_argument("--estimate", action="store_true")
    p.add_argument("--start-date", default=None)
    p.add_argument("--end-date", default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    risk_ons = [x.strip() for x in args.risk_ons.split(",") if x.strip()]
    specs = []
    for risk_on in risk_ons:
        key = (args.branch, risk_on)
        if key not in BRANCHES:
            raise SystemExit(f"Unsupported branch/risk-on pair: {key}")
        specs.append(BRANCHES[key])

    storage = TiingoStorage(args.storage_root)
    prepared = [_window_prepared(_prepare(spec, args.off_leg, storage), args.start_date, args.end_date) for spec in specs]
    if not prepared:
        raise SystemExit("No risk-ons selected")
    if args.extra_lag_days < 0:
        raise SystemExit("--extra-lag-days must be >= 0")

    if not args.allow_redundant_signals:
        prepared = [_dedupe_prepared(p) for p in prepared]

    n_signals = len(prepared[0].signal_names)
    if any(len(p.signal_names) != n_signals for p in prepared):
        raise SystemExit("Prepared branches have inconsistent signal counts")
    if args.min_n < 1 or args.max_n < args.min_n or args.max_n > n_signals:
        raise SystemExit(f"Require 1 <= min_n <= max_n <= {n_signals}")

    estimated_per_branch = estimate_config_count(
        prepared[0].signal_names,
        args.min_n,
        args.max_n,
        allow_redundant=args.allow_redundant_signals,
    )
    estimated = estimated_per_branch * len(prepared)
    print(
        f"signals={n_signals} branches={len(prepared)} n={args.min_n}..{args.max_n} "
        f"estimated_configs={estimated:,}",
        flush=True,
    )
    if args.estimate:
        return 0
    if estimated > args.huge_threshold and not args.allow_huge:
        raise SystemExit(
            f"Estimated {estimated:,} configs exceeds threshold {args.huge_threshold:,}. "
            "Re-run with --allow-huge if intentional."
        )

    out_dir = OUT_ROOT / (args.out_name or f"{args.branch}_{'_'.join(risk_ons)}_{args.off_leg}_grid_n{args.min_n}_{args.max_n}")
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    top_path = tables_dir / "stage2_grid_top.csv"
    checkpoint_path = tables_dir / "stage2_grid_top_checkpoint.csv"

    started = time.perf_counter()
    heap: list[tuple[tuple[float, float, float], int, dict]] = []
    counter = 0
    processed = 0
    for branch in prepared:
        for row in _iter_grid_rows(branch, args.min_n, args.max_n, args.extra_lag_days, args.allow_redundant_signals):
            processed += 1
            counter += 1
            _push_top(heap, row, args.top, counter)
            if args.progress_every > 0 and processed % args.progress_every == 0:
                elapsed = max(time.perf_counter() - started, 1e-9)
                rate = processed / elapsed
                best = max(heap, key=lambda x: x[0])[2] if heap else row
                print(
                    f"processed={processed:,}/{estimated:,} rate={rate:,.0f}/s "
                    f"elapsed={elapsed:,.1f}s best={best['branch']}:{best['risk_on']} "
                    f"sortino={best['sortino']:.4f} cagr={best['cagr']:.2%}",
                    flush=True,
                )
                _write_top(heap, checkpoint_path)

    full_top = _materialize_top(heap, prepared, args.extra_lag_days)
    full_top.to_csv(top_path, index=False)
    top = pd.read_csv(top_path)
    report = _report(top, prepared, args, estimated, processed, time.perf_counter() - started)
    (out_dir / "REPORT.md").write_text(report, encoding="utf-8")
    manifest = {
        "stage": "stage2_tiingo_ohlc_grid",
        "branch": args.branch,
        "risk_ons": risk_ons,
        "off_leg": args.off_leg,
        "extra_lag_days": args.extra_lag_days,
        "allow_redundant_signals": args.allow_redundant_signals,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "min_n": args.min_n,
        "max_n": args.max_n,
        "signal_count": n_signals,
        "estimated_configs": estimated,
        "configs_tested": processed,
        "top": args.top,
        "elapsed_seconds": time.perf_counter() - started,
        "primary_citation": "[advances_fin_ml, p.222-223]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"done configs={processed:,} output={out_dir / 'REPORT.md'}", flush=True)
    return 0


def estimate_config_count(signal_names: list[str] | int, min_n: int, max_n: int, allow_redundant: bool = False) -> int:
    if isinstance(signal_names, int):
        return sum(math.comb(signal_names, n) * n for n in range(min_n, max_n + 1))
    if allow_redundant:
        return sum(math.comb(len(signal_names), n) * n for n in range(min_n, max_n + 1))
    coeffs = [1]
    for group in _nonredundant_signal_groups(signal_names):
        choices = len(group)
        coeffs.append(0)
        for i in range(len(coeffs) - 2, -1, -1):
            coeffs[i + 1] += coeffs[i] * choices
    return sum(n * coeffs[n] for n in range(min_n, min(max_n, len(coeffs) - 1) + 1))


def _window_prepared(prepared: Prepared, start_date: str | None, end_date: str | None) -> Prepared:
    if start_date is None and end_date is None:
        return prepared
    mask = np.ones(len(prepared.dates), dtype=bool)
    if start_date is not None:
        mask &= prepared.dates >= pd.Timestamp(start_date)
    if end_date is not None:
        mask &= prepared.dates <= pd.Timestamp(end_date)
    if not mask.any():
        raise SystemExit(f"Date window produced no rows: {start_date=} {end_date=}")
    return replace(
        prepared,
        dates=prepared.dates[mask],
        signal_matrix=prepared.signal_matrix[mask, :],
        on_returns=prepared.on_returns[mask],
        off_returns=prepared.off_returns[mask],
        benchmark_returns=prepared.benchmark_returns[mask],
    )


def _iter_grid_rows(branch: Prepared, min_n: int, max_n: int, extra_lag_days: int, allow_redundant: bool):
    if allow_redundant:
        combos = (
            combo
            for n in range(min_n, max_n + 1)
            for combo in itertools.combinations(range(len(branch.signal_names)), n)
        )
    else:
        combos = _iter_nonredundant_combos(branch.signal_names, min_n, max_n)
    for combo in combos:
        n = len(combo)
        combo_names = [branch.signal_names[i] for i in combo]
        sub = branch.signal_matrix[:, combo]
        valid = ~np.isnan(sub).any(axis=1)
        counts = np.nansum(sub, axis=1)
        signal_names = "|".join(combo_names)
        for k in range(1, n + 1):
            raw_signal = np.where(valid, counts >= k, False)
            returns = _simulate_on_off_lag_np(raw_signal, branch.on_returns, branch.off_returns, extra_lag_days)
            row = _quick_row(returns, branch.benchmark_returns, branch.dates)
            row.update({
                "label": "stage2_grid",
                "branch": branch.spec.branch,
                "risk_on": branch.spec.risk_on_label,
                "n": n,
                "k": k,
                "signals": signal_names,
            })
            yield row


def _quick_row(returns: np.ndarray, benchmark_returns: np.ndarray, dates: pd.DatetimeIndex) -> dict:
    """Cheap scan metrics; full MDD/Calmar are recomputed only for retained top rows."""
    mask = np.isfinite(returns) & np.isfinite(benchmark_returns)
    r = returns[mask]
    b = benchmark_returns[mask]
    d = dates[mask]
    if len(r) == 0:
        return {
            "cagr": np.nan,
            "sharpe": 0.0,
            "sortino": 0.0,
            "mdd": np.nan,
            "calmar": np.nan,
            "vol_annual": np.nan,
            "end_mult": np.nan,
            "end_rel_to_benchmark": np.nan,
            "pct_above_benchmark": np.nan,
            "start": "",
            "end": "",
            "n_days": 0,
        }
    years = len(r) / 252.0
    total = float(np.exp(np.log1p(r).sum())) if np.all(r > -1.0) else np.nan
    bench_total = float(np.exp(np.log1p(b).sum())) if np.all(b > -1.0) else np.nan
    cagr = total ** (1.0 / years) - 1.0 if years > 0 and total > 0 else np.nan
    vol = float(np.std(r, ddof=1) * np.sqrt(252.0)) if len(r) > 1 else np.nan
    mean = float(np.mean(r))
    std = float(np.std(r, ddof=1)) if len(r) > 1 else np.nan
    sharpe = mean / std * np.sqrt(252.0) if std and std > 0 else 0.0
    downside = r[r < 0.0]
    down_std = float(np.std(downside, ddof=1)) if len(downside) > 1 else 0.0
    sortino = mean / down_std * np.sqrt(252.0) if down_std > 0 else 0.0
    return {
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "mdd": np.nan,
        "calmar": np.nan,
        "vol_annual": vol,
        "end_mult": total,
        "end_rel_to_benchmark": total / bench_total if bench_total and bench_total > 0 else np.nan,
        "pct_above_benchmark": np.nan,
        "start": str(d[0].date()),
        "end": str(d[-1].date()),
        "n_days": int(len(r)),
    }


def _score(row: dict) -> tuple[float, float, float]:
    return (float(row["sortino"]), float(row["cagr"]), float(row["calmar"]))


def _push_top(heap: list[tuple[tuple[float, float, float], int, dict]], row: dict, top: int, counter: int) -> None:
    item = (_score(row), counter, row)
    if len(heap) < top:
        heapq.heappush(heap, item)
    elif item[0] > heap[0][0]:
        heapq.heapreplace(heap, item)


def _write_top(heap: list[tuple[tuple[float, float, float], int, dict]], path: Path) -> None:
    rows = [item[2] for item in sorted(heap, key=lambda x: x[0], reverse=True)]
    cols = FIELDNAMES
    pd.DataFrame(rows, columns=cols).to_csv(path, index=False)


def _materialize_top(heap: list[tuple[tuple[float, float, float], int, dict]], prepared: list[Prepared], extra_lag_days: int) -> pd.DataFrame:
    by_risk_on = {p.spec.risk_on_label: p for p in prepared}
    rows = []
    for _, _, quick in sorted(heap, key=lambda x: x[0], reverse=True):
        branch = by_risk_on[quick["risk_on"]]
        signals = str(quick["signals"]).split("|")
        idx = [branch.signal_names.index(s) for s in signals]
        sub = branch.signal_matrix[:, idx]
        valid = ~np.isnan(sub).any(axis=1)
        counts = np.nansum(sub, axis=1)
        raw_signal = np.where(valid, counts >= int(quick["k"]), False)
        returns = _simulate_on_off_lag_np(raw_signal, branch.on_returns, branch.off_returns, extra_lag_days)
        rows.append(_metrics_row_np(
            returns=returns,
            benchmark_returns=branch.benchmark_returns,
            dates=branch.dates,
            label="stage2_grid",
            branch=branch.spec.branch,
            risk_on=branch.spec.risk_on_label,
            n=int(quick["n"]),
            k=int(quick["k"]),
            signals=quick["signals"],
        ))
    return pd.DataFrame(rows, columns=FIELDNAMES).sort_values(
        ["sortino", "cagr", "calmar"], ascending=[False, False, False]
    )


def _simulate_on_off_lag_np(signal: np.ndarray, on_returns: np.ndarray, off_returns: np.ndarray, extra_lag_days: int) -> np.ndarray:
    """Apply base close-to-close lag plus optional execution delay `[advances_fin_ml, p.31-34]`."""
    if extra_lag_days == 0:
        return _simulate_on_off_np(signal, on_returns, off_returns)
    lag = 1 + extra_lag_days
    sig_lag = np.zeros_like(signal, dtype=bool)
    if lag < len(signal):
        sig_lag[lag:] = signal[:-lag]
    return np.where(sig_lag, on_returns, off_returns)


REDUNDANT_SIGNAL_GROUPS: dict[str, str] = {
    "macd_gt_signal": "macd_equivalent",
    "macd_hist_gt_0": "macd_equivalent",
    "rv21_pct_lt_50": "rv21_pct_threshold",
    "rv21_pct_lt_70": "rv21_pct_threshold",
    "adx14_gt_20": "adx14_threshold",
    "adx14_gt_25": "adx14_threshold",
    "atr14_pct_lt_3": "atr14_pct_threshold",
    "atr14_pct_lt_5": "atr14_pct_threshold",
    "stoch14_gt_50": "stoch14_threshold",
    "stoch14_gt_80": "stoch14_threshold",
    "cci20_gt_0": "cci20_threshold",
    "cci20_gt_100": "cci20_threshold",
    "close_gt_prior_high20": "prior_high_threshold",
    "close_gt_prior_high55": "prior_high_threshold",
    "bull_power_gt_0": "elder_power_threshold",
    "bear_power_gt_0": "elder_power_threshold",
}

DROP_EQUIVALENT_SIGNALS = {"macd_gt_signal"}


def _dedupe_prepared(prepared: Prepared) -> Prepared:
    keep_idx = [i for i, name in enumerate(prepared.signal_names) if name not in DROP_EQUIVALENT_SIGNALS]
    names = [prepared.signal_names[i] for i in keep_idx]
    ohlc_names = [name for name in prepared.ohlc_signal_names if name in names]
    return Prepared(
        spec=prepared.spec,
        off_leg=prepared.off_leg,
        dates=prepared.dates,
        signal_names=names,
        ohlc_signal_names=ohlc_names,
        signal_matrix=prepared.signal_matrix[:, keep_idx],
        on_returns=prepared.on_returns,
        off_returns=prepared.off_returns,
        benchmark_returns=prepared.benchmark_returns,
    )


def _nonredundant_signal_groups(signal_names: list[str]) -> list[list[int]]:
    groups: dict[str, list[int]] = {}
    for i, name in enumerate(signal_names):
        group = REDUNDANT_SIGNAL_GROUPS.get(name, name)
        groups.setdefault(group, []).append(i)
    return list(groups.values())


def _iter_nonredundant_combos(signal_names: list[str], min_n: int, max_n: int):
    groups = _nonredundant_signal_groups(signal_names)
    for n in range(min_n, max_n + 1):
        for selected_groups in itertools.combinations(groups, n):
            for combo in itertools.product(*selected_groups):
                yield tuple(sorted(combo))


def _combo_is_nonredundant(signal_names: list[str]) -> bool:
    seen: set[str] = set()
    for name in signal_names:
        group = REDUNDANT_SIGNAL_GROUPS.get(name)
        if group is None:
            continue
        if group in seen:
            return False
        seen.add(group)
    return True


def _report(
    top: pd.DataFrame,
    prepared: list[Prepared],
    args: argparse.Namespace,
    estimated: int,
    processed: int,
    elapsed: float,
) -> str:
    windows = ", ".join(
        f"{p.spec.risk_on_label}: {p.dates.min().date()}..{p.dates.max().date()} ({len(p.dates):,} bars)"
        for p in prepared
    )
    lines = [
        "# Stage 2 Tiingo OHLC Grid Results",
        "",
        "Status: capped exact-grid discovery. This is not a validation verdict.",
        "",
        f"Branch: `{args.branch}`",
        f"Risk-ons: `{args.risk_ons}`",
        f"Off leg: `{args.off_leg}`",
        f"Extra execution lag days: `{args.extra_lag_days}`",
        f"Redundant signals allowed: `{args.allow_redundant_signals}`",
        f"Date window: `{args.start_date or 'full'}` to `{args.end_date or 'full'}`",
        f"Signal subset range: n={args.min_n}..{args.max_n}",
        f"Estimated/configs tested: {estimated:,} / {processed:,}",
        f"Windows: {windows}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "## Top Configs",
        "",
        top[["branch", "risk_on", "n", "k", "sortino", "cagr", "sharpe", "mdd", "calmar", "signals"]].head(args.top).to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Method Notes",
        "",
        "- Top rows are retained by Sortino, then CAGR, then Calmar.",
        "- Signals are lagged one base bar before returns to avoid same-close look-ahead; `extra_lag_days` adds operational execution delay `[advances_fin_ml, p.31-34]`.",
        "- Redundant signal groups are excluded by default, including equivalent MACD forms and nested thresholds.",
        "- All evaluated configs must be included in later DSR trial accounting `[advances_fin_ml, p.222-223]`.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
