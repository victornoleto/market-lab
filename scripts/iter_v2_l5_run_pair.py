"""Run the V2-L5 Kalman pair-cointegration sweep on ONE pair per iter.

Invoked by the self-improve loop agent inside a fan-out iter for lead
V2-L5 (``reports/phase3_5a_v2/v2_l5_equity_pairs/registry.json``).
Pops ``tickers_pending[0]`` (pair label, e.g. ``GLD_SLV``), loads the
two legs from the Tiingo daily cache, runs the pipeline, writes
``<pair>.json`` + ``<pair>.md`` atomically, then updates the registry.

The per-pair chronological split is 70/20/10 IS/OOS/FWD, same as
V2-L3, so the aggregator can compare verdicts apples-to-apples across
leads. Walk-forward uses 8 windows with 6/8 profitable + MaxDD 25% cap
(``[advances_fin_ml, ch.11]``).

Citations
---------

* Engle-Granger cointegration, ADF-on-residuals: ``[algo_trading_chan, p.42-46]``.
* Kalman dynamic hedge ratio: ``[machine_trading_chan, ch.3]``;
  ``[algo_trading_chan, p.47-54]``.
* Walk-forward 6/8 + MaxDD 25%: ``[advances_fin_ml, ch.11]``.
* Hold economics (median hold ≥ 3d target): ``[systematic_trading, p.185-188]``.
* Pepperstone Razor retail cost model: Phase 3.5a-V2 spec §3.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ai_trade.backtest.grid.letf_rotation_b1c import (  # noqa: E402
    compute_split_metrics,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.strategies.kalman_pair_cointegration import (  # noqa: E402
    KalmanPairConfig,
    KalmanPairResult,
    run_kalman_pair_pipeline,
)
from ai_trade.backtest.sweeps.registry import (  # noqa: E402
    advance_status,
    append_done,
    atomic_write_registry,
    load_registry,
    pop_pending,
)

log = logging.getLogger(__name__)

REGISTRY_PATH = Path(
    "reports/phase3_5a_v2/v2_l5_equity_pairs/registry.json"
)
TIINGO_DAILY_DIR = Path("data/tiingo/daily/prices")

IS_FRAC = 0.70
OOS_FRAC = 0.20
FWD_FRAC = 0.10


def _load_parquet(ticker: str) -> pd.Series:
    path = TIINGO_DAILY_DIR / f"{ticker}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"missing parquet: {path}")
    df = pd.read_parquet(path)
    df.index = pd.DatetimeIndex(df.index)
    # Prefer adjusted close when available (total-return basis).
    for col in ("adjClose", "adj_close", "close", "Close"):
        if col in df.columns:
            return df[col].rename(ticker)
    raise KeyError(f"{path}: no close column found in {list(df.columns)[:6]}")


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _atomic_write_json(path: Path, payload: dict) -> None:
    _atomic_write_text(path, json.dumps(payload, indent=2, default=str))


def _chronological_splits(
    daily_returns: pd.Series,
) -> tuple[pd.Series, pd.Series, pd.Series, list[str], list[str], list[str]]:
    r = daily_returns.dropna()
    if r.empty:
        empty = pd.Series(dtype=float)
        return empty, empty, empty, ["", ""], ["", ""], ["", ""]
    n = len(r)
    i1 = int(n * IS_FRAC)
    i2 = int(n * (IS_FRAC + OOS_FRAC))
    is_r = r.iloc[:i1]
    oos_r = r.iloc[i1:i2]
    fwd_r = r.iloc[i2:]
    is_range = (
        [str(is_r.index[0].date()), str(is_r.index[-1].date())] if len(is_r) else ["", ""]
    )
    oos_range = (
        [str(oos_r.index[0].date()), str(oos_r.index[-1].date())] if len(oos_r) else ["", ""]
    )
    fwd_range = (
        [str(fwd_r.index[0].date()), str(fwd_r.index[-1].date())] if len(fwd_r) else ["", ""]
    )
    return is_r, oos_r, fwd_r, is_range, oos_range, fwd_range


def _metrics_dict(m) -> dict:
    return {
        "n_bars": int(m.n_bars),
        "sharpe": float(m.sharpe),
        "cagr": float(m.cagr),
        "max_drawdown": float(m.max_drawdown),
        "final_equity": float(m.final_equity_from_unit),
    }


def _per_config_verdict(is_m, oos_m, fwd_m, wf_pass: bool, median_hold: float) -> dict:
    """V2 winner-criteria subset gates (PBO/DSR deferred to aggregator)."""
    checks = [
        ("oos_sharpe_gt_0", oos_m.sharpe > 0, f"{oos_m.sharpe:.3f}"),
        ("fwd_sharpe_gt_0", fwd_m.sharpe > 0, f"{fwd_m.sharpe:.3f}"),
        ("wf_pass", wf_pass, "6/8"),
        ("median_hold_ge_3d", median_hold >= 3, f"{median_hold:.1f}d"),
        ("oos_cagr_ge_30pct", oos_m.cagr >= 0.30, f"{oos_m.cagr:.1%}"),
        ("oos_sharpe_ge_2", oos_m.sharpe >= 2.0, f"{oos_m.sharpe:.3f}"),
        ("oos_maxdd_le_25pct", oos_m.max_drawdown >= -0.25, f"{oos_m.max_drawdown:.1%}"),
    ]
    failed = [name for name, ok, _ in checks if not ok]
    return {
        "checks": [
            {"name": name, "pass": bool(ok), "value": val}
            for name, ok, val in checks
        ],
        "n_passed": sum(1 for _, ok, _ in checks if ok),
        "n_total": len(checks),
        "all_pass_except_cross_config_gates": not failed,
        "failed_subset_gates": failed,
    }


def run_one_pair(pair_label: str, config_entry: dict, iter_num: int) -> dict:
    y_sym, x_sym = pair_label.split("_", 1)
    y_close = _load_parquet(y_sym)
    x_close = _load_parquet(x_sym)

    cfg = KalmanPairConfig(
        adf_alpha=float(config_entry.get("adf_alpha", 0.05)),
        delta=float(config_entry.get("kalman_delta", 1e-5)),
        observation_variance=float(config_entry.get("kalman_ve", 1e-3)),
        entry_z=float(config_entry.get("entry_z", 2.0)),
        exit_z=float(config_entry.get("exit_z", 0.0)),
        stop_z=float(config_entry.get("stop_z", 4.0)),
        hold_cap_days=int(config_entry.get("hold_cap_days", 30)),
    )

    t0 = time.time()
    result: KalmanPairResult = run_kalman_pair_pipeline(
        y_close, x_close, pair_name=pair_label, cfg=cfg
    )
    elapsed = time.time() - t0

    ret = result.daily_returns
    is_r, oos_r, fwd_r, is_range, oos_range, fwd_range = _chronological_splits(ret)
    is_m = compute_split_metrics("IS", is_r)
    oos_m = compute_split_metrics("OOS", oos_r)
    fwd_m = compute_split_metrics("FWD", fwd_r)

    ret_clean = ret.dropna()
    # WF only makes sense when the series has non-trivial activity; fall
    # through to a deterministic no-pass if the pair never traded.
    if ret_clean.abs().sum() > 0 and len(ret_clean) >= 8:
        wf_ratio, wf_max_dd, wf_pass = walk_forward_verdict_from_returns(
            ret_clean,
            n_windows=8,
            min_profitable_ratio=6 / 8,
            max_drawdown_cap=0.25,
        )
    else:
        wf_ratio, wf_max_dd, wf_pass = 0.0, 0.0, False

    # Persist returns for potential downstream combiner / aggregator use.
    daily_series_path = REGISTRY_PATH.parent / f"{pair_label}_daily_returns.parquet"
    daily_series_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = daily_series_path.with_suffix(".parquet.tmp")
    ret.to_frame("ret").to_parquet(tmp)
    os.replace(tmp, daily_series_path)

    payload = {
        "pair": pair_label,
        "frequency": "daily",
        "config_entry": dict(config_entry),
        "window": {
            "start": str(ret.index[0].date()),
            "end": str(ret.index[-1].date()),
            "n_bars": int(len(ret)),
        },
        "cointegration": {
            **result.cointegration,
            "pass": bool(result.cointegration["pass"]),
        },
        "splits": {
            "IS": {"range": is_range, **_metrics_dict(is_m)},
            "OOS": {"range": oos_range, **_metrics_dict(oos_m)},
            "FWD": {"range": fwd_range, **_metrics_dict(fwd_m)},
        },
        "walk_forward": {
            "n_windows": 8,
            "profitable_ratio": float(wf_ratio),
            "max_window_drawdown": float(wf_max_dd),
            "pass": bool(wf_pass),
            "min_profitable_ratio": 6 / 8,
            "max_drawdown_cap": 0.25,
        },
        "hold_metrics": {
            "median_hold_days": float(result.median_hold_days),
            "n_events_total": int(result.n_events_total),
            "n_events_taken": int(result.n_events_taken),
            "n_trades": int(len(result.trade_ledger)),
        },
        "costs": {
            "cum_transaction_cost_pct": float(result.cum_transaction_cost_pct),
            "cum_swap_cost_pct": float(result.cum_swap_cost_pct),
            "spread_half_bps": cfg.spread_half_bps,
            "commission_round_trip_bps": cfg.commission_round_trip_bps,
            "slippage_bps_round_trip": cfg.slippage_bps_round_trip,
            "swap_daily_pct_long_per_leg": cfg.swap_daily_pct_long,
        },
        "kalman_final_beta": float(result.kalman_final_beta),
        "runtime_seconds": round(elapsed, 2),
        "iter": iter_num,
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verdict_per_config": _per_config_verdict(
            is_m, oos_m, fwd_m, wf_pass, result.median_hold_days
        ),
    }

    return payload


def render_markdown(summary: dict) -> str:
    pair = summary["pair"]
    ce = summary["config_entry"]
    coint = summary["cointegration"]
    is_s = summary["splits"]["IS"]
    oos_s = summary["splits"]["OOS"]
    fwd_s = summary["splits"]["FWD"]
    wf = summary["walk_forward"]
    hm = summary["hold_metrics"]
    cs = summary["costs"]
    vd = summary["verdict_per_config"]

    all_pass = vd["all_pass_except_cross_config_gates"]
    badge = (
        "✅ PASS subset"
        if all_pass
        else f"❌ FAIL ({len(vd['failed_subset_gates'])} gates)"
    )

    out: list[str] = []
    out.append(
        f"# {pair} daily — V2-L5 Kalman pair cointegration (iter {summary['iter']})"
    )
    out.append("")
    out.append(f"**Path tag:** [SHORT-HOLD CFD]  |  **Status:** {badge}")
    out.append(
        f"**Config:** `{ce.get('name', 'kalman_eg_2sigma_30d')}` — "
        f"EG ADF alpha={ce.get('adf_alpha', 0.05)}, Kalman delta={ce.get('kalman_delta', 1e-5)}, "
        f"V_e={ce.get('kalman_ve', 1e-3)}, entry=±{ce.get('entry_z', 2.0)}σ, "
        f"exit={ce.get('exit_z', 0.0)}σ, stop=±{ce.get('stop_z', 4.0)}σ, "
        f"hold cap={ce.get('hold_cap_days', 30)}d"
    )
    out.append(
        f"**Window:** {summary['window']['start']} → {summary['window']['end']} "
        f"({summary['window']['n_bars']} bars)"
    )
    out.append("")
    out.append("## Cointegration gate (Engle-Granger two-step, full-series)")
    out.append("")
    out.append(f"- OLS: `log(y) = {coint['ols_alpha']:.4f} + {coint['ols_beta']:.4f} * log(x) + residuals`")
    out.append(
        f"- ADF on residuals: stat={coint['adf_stat']:.3f}, "
        f"p-value={coint['adf_p_value']:.4f} → "
        f"**{'PASS' if coint['pass'] else 'FAIL'}** (alpha={ce.get('adf_alpha', 0.05)})"
    )
    out.append(f"- Final Kalman beta: {summary['kalman_final_beta']:.4f}")
    out.append("")
    out.append("## Split metrics")
    out.append("")
    out.append("| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |")
    out.append("|-------|-------|-------:|-------:|-----:|------:|-------------:|")
    for lbl, s in (("IS", is_s), ("OOS", oos_s), ("FWD", fwd_s)):
        out.append(
            f"| {lbl} | {s['range'][0]} → {s['range'][1]} | {s['n_bars']} | "
            f"{s['sharpe']:.3f} | {s['cagr']*100:.2f}% | {s['max_drawdown']*100:.2f}% | "
            f"{s['final_equity']:.3f} |"
        )
    out.append("")
    out.append("## Walk-forward (8 windows)")
    out.append("")
    out.append(f"- Profitable windows: **{wf['profitable_ratio']:.2f}** (target ≥ 0.75)")
    out.append(f"- Max window drawdown: **{wf['max_window_drawdown']*100:.1f}%** (cap 25%)")
    out.append(f"- Pass: **{'YES' if wf['pass'] else 'NO'}**")
    out.append("")
    out.append("## Hold / event diagnostics")
    out.append("")
    out.append(f"- Median hold: **{hm['median_hold_days']:.1f} days** (target ≥ 3d, V2 spec §1)")
    out.append(f"- Entry signals observed: {hm['n_events_total']}")
    out.append(f"- Round-trips executed: {hm['n_trades']}")
    out.append("")
    out.append("## Cost breakdown (Pepperstone Razor retail, both legs)")
    out.append("")
    out.append(
        f"- Cumulative transaction cost: **{cs['cum_transaction_cost_pct']*100:.3f}%** of starting equity"
    )
    out.append(
        f"- Cumulative overnight swap: **{cs['cum_swap_cost_pct']*100:.3f}%** of starting equity"
    )
    out.append(
        f"- Spread half: {cs['spread_half_bps']} bps | "
        f"commission RT per leg: {cs['commission_round_trip_bps']} bps | "
        f"slippage RT per leg: {cs['slippage_bps_round_trip']} bps | "
        f"swap daily per leg: {cs['swap_daily_pct_long_per_leg']*100:.4f}%"
    )
    out.append("")
    out.append("## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)")
    out.append("")
    out.append("| Gate | Value | Pass |")
    out.append("|------|------:|:----:|")
    for check in vd["checks"]:
        flag = "✅" if check["pass"] else "❌"
        out.append(f"| {check['name']} | {check['value']} | {flag} |")
    out.append("")
    if all_pass:
        out.append(
            "**All subset gates passed.** Final PASS requires aggregator PBO/DSR verdict."
        )
    else:
        out.append(
            f"**Subset FAIL** — {len(vd['failed_subset_gates'])} gate(s): "
            f"{', '.join(vd['failed_subset_gates'])}."
        )
    out.append("")
    out.append("## Citations")
    out.append("")
    out.append("- Engle-Granger cointegration, ADF on residuals: `[algo_trading_chan, p.42-46]`.")
    out.append("- Kalman dynamic hedge ratio for pair trading: `[machine_trading_chan, ch.3]`.")
    out.append("- Z-score entry/exit at ±2σ: `[algo_trading_chan, p.47-54]`.")
    out.append("- Walk-forward 6/8 + MaxDD 25%: `[advances_fin_ml, ch.11]`.")
    out.append("- Hold economics (retail cost amortization): `[systematic_trading, p.185-188]`.")
    out.append("- Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.")
    out.append("")
    return "\n".join(out) + "\n"


def _as_py(v):
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, dict):
        return {k: _as_py(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_as_py(x) for x in v]
    return v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", type=int, required=True, help="current iter number (for provenance).")
    ap.add_argument("--registry", type=str, default=str(REGISTRY_PATH))
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    reg_path = Path(args.registry)
    reg = load_registry(reg_path)
    if reg["status"] not in ("pending", "sweeping"):
        raise RuntimeError(
            f"registry status is {reg['status']!r}; expected pending/sweeping"
        )
    if not reg["tickers_pending"]:
        raise RuntimeError("tickers_pending is empty — nothing to sweep")
    if len(reg["configs"]) != 1:
        raise RuntimeError(
            f"V2-L5 expects exactly 1 config, got {len(reg['configs'])}"
        )

    pair_label = reg["tickers_pending"][0]
    config_entry = reg["configs"][0]
    log.info("V2-L5 iter %d — sweeping pair %s", args.iter, pair_label)

    summary = run_one_pair(pair_label, config_entry, iter_num=args.iter)

    md_path = reg_path.parent / f"{pair_label}.md"
    json_path = reg_path.parent / f"{pair_label}.json"
    _atomic_write_json(json_path, _as_py(summary))
    _atomic_write_text(md_path, render_markdown(summary))

    popped, reg = pop_pending(reg)
    assert popped == pair_label, (popped, pair_label)
    reg = append_done(
        reg,
        {
            "ticker": pair_label,
            "frequency": "daily",
            "window_start": summary["window"]["start"],
            "window_end": summary["window"]["end"],
            "iter": args.iter,
            "n_configs_tested": 1,
            "best_config": config_entry["name"],
            "best_sharpe_oos": summary["splits"]["OOS"]["sharpe"],
            "best_cagr": summary["splits"]["OOS"]["cagr"],
            "best_maxdd": summary["splits"]["OOS"]["max_drawdown"],
            "any_pass_5gate": bool(
                summary["verdict_per_config"]["all_pass_except_cross_config_gates"]
            ),
            "median_hold_days": summary["hold_metrics"]["median_hold_days"],
            "result_file_md": str(md_path),
            "result_file_json": str(json_path),
        },
    )
    reg = advance_status(reg)
    atomic_write_registry(reg_path, reg)

    log.info(
        "wrote %s + %s (Sharpe OOS %.3f, subset PASS=%s); registry status=%s",
        md_path.name,
        json_path.name,
        summary["splits"]["OOS"]["sharpe"],
        summary["verdict_per_config"]["all_pass_except_cross_config_gates"],
        reg["status"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
