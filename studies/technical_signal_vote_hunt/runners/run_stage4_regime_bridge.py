"""Stage 4 regime-gated bridge for modern QQQ/LETF vote leads.

This runner intentionally separates an economic-first research verdict from the
mandate verdict. PBO/DSR are not used to block `economic_pass`; they remain
deployment gates elsewhere. The hypothesis is that a simple, pre-registered
regime gate can identify when the modern QQQ/LETF technical vote is valid across
rolling cycles `[leverage_for_the_long_run, p.13]`, `[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from studies.technical_signal_vote_hunt.core import daily_returns, ema, realized_vol, sma
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np
from studies.technical_signal_vote_hunt.runners.run_stage2_tiingo_ohlc import (
    BRANCHES,
    Prepared,
    _prepare,
    _simulate_on_off_lag_np,
    _window_prepared,
)
from studies.technical_signal_vote_hunt.runners.validate_stage1_candidates import (
    _bootstrap,
    _fwd_post_2020,
    _oos_70_30,
    _sharpe,
    _walk_forward,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = REPO_ROOT / "studies/technical_signal_vote_hunt/results/stage4_regime_bridge"
DEFAULT_BASE_SIGNALS = "sma100_gt_sma250|roc10_gt_0|roc120_gt_0|stochrsi14_gt_50|rv21_pct_lt_70"
TRADING_DAYS_PER_YEAR = 252


@dataclass(frozen=True)
class GateSpec:
    name: str
    family: str
    citation: str
    signal: pd.Series


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Stage 4 regime-gated bridge")
    p.add_argument("--branch", choices=["QQQ", "SPY"], default="QQQ")
    p.add_argument("--risk-on", choices=["QLD_2x", "TQQQ_3x", "SSO_2x", "UPRO_3x"], default="QLD_2x")
    p.add_argument("--off-leg", choices=["CASH_USD", "ZROZ", "BIL"], default="CASH_USD")
    p.add_argument("--extra-lag-days", type=int, default=1)
    p.add_argument("--base-signals", default=DEFAULT_BASE_SIGNALS)
    p.add_argument("--base-k", type=int, default=3)
    p.add_argument("--start-date", default="2010-02-12")
    p.add_argument("--end-date", default=None)
    p.add_argument("--storage-root", type=Path, default=REPO_ROOT / "data/tiingo")
    p.add_argument("--bootstrap-n", type=int, default=500)
    p.add_argument("--bootstrap-block", type=int, default=21)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--wf-windows", type=int, default=8)
    p.add_argument("--out-name", default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.extra_lag_days < 0:
        raise SystemExit("--extra-lag-days must be >= 0")
    key = (args.branch, args.risk_on)
    if key not in BRANCHES:
        raise SystemExit(f"Unsupported branch/risk-on pair: {key}")

    started = time.perf_counter()
    out_dir = OUT_ROOT / (args.out_name or f"{args.branch}_{args.risk_on}_{args.off_leg}_lag{args.extra_lag_days}")
    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    storage = TiingoStorage(args.storage_root)
    prepared = _window_prepared(_prepare(BRANCHES[key], args.off_leg, storage), args.start_date, args.end_date)
    signal_close = _load_close(storage, prepared.spec.signal_ticker).reindex(prepared.dates).ffill()
    spy_close = _load_close(storage, "SPY").reindex(prepared.dates).ffill() if args.branch == "QQQ" else None
    gates = _build_regime_gates(signal_close, spy_close)
    base_signal = _base_vote(prepared, args.base_signals, args.base_k)

    rng = np.random.default_rng(args.seed)
    metric_rows: list[dict] = []
    gate_rows: list[dict] = []
    rolling_rows: list[dict] = []
    wf_rows: list[dict] = []
    boot_rows: list[dict] = []

    for gate in gates:
        combined = base_signal & _series_to_bool(gate.signal, prepared.dates)
        returns = _simulate_on_off_lag_np(combined, prepared.on_returns, prepared.off_returns, args.extra_lag_days)
        label = f"base_and_{gate.name}"
        series = pd.Series(returns, index=prepared.dates, name=label)
        bench = pd.Series(prepared.benchmark_returns, index=prepared.dates, name="benchmark")

        metrics = _metrics_row_np(
            returns=returns,
            benchmark_returns=prepared.benchmark_returns,
            dates=prepared.dates,
            label=label,
            branch=prepared.spec.branch,
            risk_on=prepared.spec.risk_on_label,
            n=len(args.base_signals.split("|")),
            k=args.base_k,
            signals=f"{args.base_signals} AND {gate.name}",
        )
        metrics["gate"] = gate.name
        metrics["gate_family"] = gate.family
        metrics["gate_citation"] = gate.citation
        metric_rows.append(metrics)

        oos = _oos_70_30(series)
        fwd = _fwd_post_2020(series)
        wf = _walk_forward(series, bench, args.wf_windows)
        boot = _bootstrap(series, args.bootstrap_n, args.bootstrap_block, rng)
        rolling = _rolling_summary(series)
        rolling_rows.extend({"label": label, "gate": gate.name, **row} for row in rolling)
        wf_rows.extend({"label": label, "gate": gate.name, **row} for row in wf["windows"])
        boot_rows.append({"label": label, "gate": gate.name, **boot})

        rolling_gate = _rolling_economic_pass(rolling)
        economic_pass = bool(oos["pass"] and fwd["pass"] and wf["pass"] and boot["pass"] and rolling_gate)
        gate_rows.append({
            "label": label,
            "gate": gate.name,
            "gate_family": gate.family,
            "oos_pass": oos["pass"],
            "oos_sharpe": oos["sharpe"],
            "fwd_pass": fwd["pass"],
            "fwd_sharpe": fwd["sharpe"],
            "wf_pass": wf["pass"],
            "wf_pass_windows": wf["pass_windows"],
            "wf_n_windows": wf["n_windows"],
            "bootstrap_pass": boot["pass"],
            "bootstrap_ci_low_sharpe": boot["ci_low_sharpe"],
            "rolling_economic_pass": rolling_gate,
            "economic_pass": economic_pass,
            "mandate_pass": False,
            "mandate_note": "PBO/DSR intentionally not computed here; economic-first research only.",
        })

    metrics_df = pd.DataFrame(metric_rows).sort_values(["economic_pass" if False else "sortino", "cagr"], ascending=[False, False])
    gates_df = pd.DataFrame(gate_rows)
    rolling_df = pd.DataFrame(rolling_rows)
    wf_df = pd.DataFrame(wf_rows)
    boot_df = pd.DataFrame(boot_rows)
    metrics_df.to_csv(tables_dir / "metrics.csv", index=False)
    gates_df.to_csv(tables_dir / "economic_gates.csv", index=False)
    rolling_df.to_csv(tables_dir / "rolling_windows.csv", index=False)
    wf_df.to_csv(tables_dir / "walk_forward.csv", index=False)
    boot_df.to_csv(tables_dir / "bootstrap.csv", index=False)

    _write_report(prepared, metrics_df, gates_df, rolling_df, args, time.perf_counter() - started, out_dir)
    _write_manifest(args, len(gates_df), time.perf_counter() - started, out_dir)
    print(f"done candidates={len(gates_df)} output={out_dir / 'REPORT.md'}", flush=True)
    return 0


def _load_close(storage: TiingoStorage, ticker: str) -> pd.Series:
    raw = storage.read(ticker, frequency="daily")
    return raw["adj_close"].astype(float)


def _base_vote(prepared: Prepared, signals: str, k: int) -> np.ndarray:
    names = [s for s in signals.split("|") if s]
    missing = [s for s in names if s not in prepared.signal_names]
    if missing:
        raise SystemExit(f"Unknown base signal(s): {missing}")
    idx = [prepared.signal_names.index(name) for name in names]
    sub = prepared.signal_matrix[:, idx]
    valid = ~np.isnan(sub).any(axis=1)
    counts = np.nansum(sub, axis=1)
    return np.where(valid, counts >= k, False)


def _series_to_bool(signal: pd.Series, dates: pd.DatetimeIndex) -> np.ndarray:
    aligned = signal.reindex(dates)
    return aligned.fillna(0.0).astype(float).to_numpy() >= 1.0


def _build_regime_gates(close: pd.Series, spy_close: pd.Series | None) -> list[GateSpec]:
    px = close.astype(float)
    ret = daily_returns(px)
    sma200 = sma(px, 200)
    sma250 = sma(px, 250)
    ema200 = ema(px, 200)
    dd_252 = px / px.rolling(252, min_periods=126).max() - 1.0
    rv21 = realized_vol(ret, 21)
    rv_pct = rv21.rolling(1260, min_periods=252).rank(pct=True)
    gates = [
        GateSpec("none", "none", "[advances_fin_ml, p.208-211]", pd.Series(1.0, index=px.index)),
        GateSpec("px_gt_sma200", "trend", "[leverage_for_the_long_run, p.13]", (px > sma200).astype(float).where(sma200.notna())),
        GateSpec("px_gt_sma250", "trend", "[leverage_for_the_long_run, p.13]", (px > sma250).astype(float).where(sma250.notna())),
        GateSpec("px_gt_ema200", "trend", "[trading_systems_methods, p.548-550]", (px > ema200).astype(float).where(ema200.notna())),
        GateSpec("sma200_slope_21_gt_0", "trend_slope", "[leverage_for_the_long_run, p.13]", (sma200.diff(21) > 0.0).astype(float).where(sma200.notna())),
        GateSpec("dd252_gt_m20", "crash_distance", "[leverage_for_the_long_run, p.5-7]", (dd_252 > -0.20).astype(float).where(dd_252.notna())),
        GateSpec("dd252_gt_m30", "crash_distance", "[leverage_for_the_long_run, p.5-7]", (dd_252 > -0.30).astype(float).where(dd_252.notna())),
        GateSpec("rv21_pct_lt_70", "volatility", "[leverage_for_the_long_run, p.5-7]", (rv_pct < 0.70).astype(float).where(rv_pct.notna())),
        GateSpec("rv21_pct_lt_50", "volatility", "[leverage_for_the_long_run, p.5-7]", (rv_pct < 0.50).astype(float).where(rv_pct.notna())),
    ]
    if spy_close is not None:
        rs = px / spy_close.astype(float)
        rs_sma50 = sma(rs, 50)
        rs_sma200 = sma(rs, 200)
        gates.append(GateSpec(
            "qqq_spy_rs_sma50_gt_sma200",
            "relative_strength",
            "[dual_momentum_investing, ch.3]",
            (rs_sma50 > rs_sma200).astype(float).where(rs_sma50.notna() & rs_sma200.notna()),
        ))
    return gates


def _rolling_summary(returns: pd.Series) -> list[dict]:
    r = returns.dropna().astype(float)
    rows = []
    for years in (3, 5, 10, 15):
        window = years * TRADING_DAYS_PER_YEAR
        cagr_vals: list[float] = []
        mdd_vals: list[float] = []
        sharpe_vals: list[float] = []
        if len(r) >= window:
            for end in range(window, len(r) + 1, 21):
                sub = r.iloc[end - window:end].to_numpy(dtype=float)
                eq = np.cumprod(1.0 + sub)
                total = float(eq[-1] / eq[0]) if len(eq) else np.nan
                cagr_vals.append(total ** (1.0 / years) - 1.0 if total > 0 else np.nan)
                peak = np.maximum.accumulate(eq)
                mdd_vals.append(-float(np.max((peak - eq) / peak)))
                sharpe_vals.append(_sharpe(sub))
        vals = np.asarray(cagr_vals, dtype=float)
        mdds = np.asarray(mdd_vals, dtype=float)
        sharpes = np.asarray(sharpe_vals, dtype=float)
        rows.append({
            "window_years": years,
            "n_windows": int(np.isfinite(vals).sum()),
            "min_cagr": float(np.nanmin(vals)) if len(vals) else np.nan,
            "median_cagr": float(np.nanmedian(vals)) if len(vals) else np.nan,
            "pct_positive_cagr": float(np.nanmean(vals > 0.0)) if len(vals) else np.nan,
            "worst_mdd": float(np.nanmin(mdds)) if len(mdds) else np.nan,
            "min_sharpe": float(np.nanmin(sharpes)) if len(sharpes) else np.nan,
        })
    return rows


def _rolling_economic_pass(rows: list[dict]) -> bool:
    by_year = {int(row["window_years"]): row for row in rows}
    required = {
        3: 0.70,
        5: 0.80,
        10: 0.90,
        15: 0.95,
    }
    for years, pct in required.items():
        row = by_year.get(years)
        if not row or row["n_windows"] <= 0 or float(row["pct_positive_cagr"]) < pct:
            return False
    return True


def _write_report(
    prepared: Prepared,
    metrics: pd.DataFrame,
    gates: pd.DataFrame,
    rolling: pd.DataFrame,
    args: argparse.Namespace,
    elapsed: float,
    out_dir: Path,
) -> None:
    merged = metrics.merge(gates[["label", "economic_pass", "wf_pass_windows", "bootstrap_ci_low_sharpe"]], on="label", how="left")
    top_cols = ["label", "gate", "gate_family", "economic_pass", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "wf_pass_windows", "bootstrap_ci_low_sharpe"]
    rolling_pivot = rolling.pivot(index="label", columns="window_years", values="pct_positive_cagr").reset_index()
    rolling_pivot.columns = ["label"] + [f"rolling_{int(c)}y_pct_pos" for c in rolling_pivot.columns[1:]]
    top = merged.merge(rolling_pivot, on="label", how="left").sort_values(["economic_pass", "sortino", "cagr"], ascending=[False, False, False])
    lines = [
        "# Stage 4 Regime-Gated Bridge",
        "",
        "Status: economic-first research report. PBO/DSR are intentionally not used to block `economic_pass`; mandate deployment remains blocked without them.",
        "",
        f"Branch: `{prepared.spec.branch}`",
        f"Risk-on: `{prepared.spec.risk_on_label}` (`{prepared.spec.risk_on_ticker}`)",
        f"Off leg: `{prepared.off_leg}`",
        f"Extra lag days: `{args.extra_lag_days}`",
        f"Window: `{prepared.dates.min().date()}` to `{prepared.dates.max().date()}` ({len(prepared.dates):,} bars)",
        f"Base rule: `{args.base_signals}`, `k={args.base_k}`",
        f"Candidates: {len(gates)}",
        f"Bootstrap paths: {args.bootstrap_n:,}",
        f"Elapsed seconds: {elapsed:.1f}",
        "",
        "## Top Economic Results",
        "",
        top[[*top_cols, "rolling_3y_pct_pos", "rolling_5y_pct_pos", "rolling_10y_pct_pos", "rolling_15y_pct_pos"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Economic Gate Summary",
        "",
        gates[["label", "gate", "oos_pass", "fwd_pass", "wf_pass", "bootstrap_pass", "rolling_economic_pass", "economic_pass", "mandate_pass"]].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Rolling Window Detail",
        "",
        rolling.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Method Notes",
        "",
        "- Regime gates are simple overlays on the fixed modern vote, not a new broad optimization grid.",
        "- Signals earn returns only after `1 + extra_lag_days` bars to avoid same-close look-ahead `[advances_fin_ml, p.31-34]`.",
        "- `economic_pass` requires OOS, FWD, WF, bootstrap and rolling-window coverage. It deliberately ignores PBO/DSR for this exploratory view.",
        "- `mandate_pass` is always false in this runner because deployment still requires PBO and DSR elsewhere `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, candidates: int, elapsed: float, out_dir: Path) -> None:
    manifest = {
        "stage": "stage4_regime_bridge",
        "branch": args.branch,
        "risk_on": args.risk_on,
        "off_leg": args.off_leg,
        "extra_lag_days": args.extra_lag_days,
        "base_signals": args.base_signals,
        "base_k": args.base_k,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "candidates": candidates,
        "elapsed_seconds": elapsed,
        "economic_first": True,
        "mandate_pass_requires_external_pbo_dsr": True,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
