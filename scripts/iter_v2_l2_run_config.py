"""Run ONE V2-L2 Gayed-CFD leveraged-rotation config over SPY+QQQ.

Invoked by the self-improve loop agent inside a fan-out iter for lead
V2-L2 (``reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/registry.json``).
Pops ``tickers_pending[0]`` (a config name), runs the full backtest,
writes ``<config>.json`` + ``<config>.md`` atomically, then updates the
registry via the standard helpers.

Citations
---------

* Regime rotation + leverage discipline: ``[leverage_for_the_long_run,
  p.7, p.11, p.13, p.14, p.16, p.17, p.21]`` (Gayed).
* Leverage cap per Vince: ``[leverage_space, Vince]``,
  ``[math_money_mgmt, Vince]``.
* Carver risk-budget + CFD cost model: ``[systematic_trading, ch.8-9]``.
* Walk-forward 6/8 gate: ``[advances_fin_ml, ch.11]``.
* Pepperstone Razor retail model: Phase 3.5a-V2 spec §3.

Usage:
  .venv/bin/python scripts/iter_v2_l2_run_config.py --iter 16
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
from ai_trade.backtest.strategies.plano_a_leveraged_rotation import (  # noqa: E402
    PlanoALeveragedRotationConfig,
    PlanoALeveragedRotationResult,
    simulate_plano_a_rotation,
)
from ai_trade.backtest.sweeps.registry import (  # noqa: E402
    advance_status,
    append_done,
    atomic_write_registry,
    load_registry,
    pop_pending,
)


REGISTRY_PATH = Path(
    "reports/phase3_5a_v2/v2_l2_gayed_transported_cfd/registry.json"
)
UNIVERSE_PATH = Path("data/universe_plano_a_v2.json")
TIINGO_DAILY_DIR = Path("data/tiingo/daily/prices")

# Canonical splits — aligned with V2-L1 for cross-lead comparability.
# IS/OOS/FWD mutually exclusive (spec §4). SPY/QQQ first_dt = 2001-05-14.
IS_RANGE = ("2001-05-14", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")


def _load_parquet(ticker_key: str) -> pd.DataFrame:
    path = TIINGO_DAILY_DIR / f"{ticker_key}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"missing parquet: {path}")
    df = pd.read_parquet(path)
    df.index = pd.DatetimeIndex(df.index)
    return df


def _parquet_key_for(ticker: str) -> str:
    u = json.loads(UNIVERSE_PATH.read_text())
    for inst in u["instruments"]:
        if inst["ticker"] == ticker:
            return inst["parquet_key"]
    return ticker


def _build_panels(
    risk_on_tickers: list[str], off_regime_asset: str
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame] | None]:
    """Load Tiingo daily parquets for risk-on and optional off-regime."""
    risk_on_panel = {t: _load_parquet(_parquet_key_for(t)) for t in risk_on_tickers}
    off_panel: dict[str, pd.DataFrame] | None = None
    if off_regime_asset in ("tlt", "gld"):
        key = _parquet_key_for(off_regime_asset.upper())
        off_panel = {off_regime_asset: _load_parquet(key)}
    return risk_on_panel, off_panel


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


def _slice(series: pd.Series, start: str, end: str) -> pd.Series:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    return series.loc[(series.index >= s) & (series.index <= e)]


def _metrics_dict(m) -> dict:
    return {
        "n_bars": int(m.n_bars),
        "sharpe": float(m.sharpe),
        "cagr": float(m.cagr),
        "max_drawdown": float(m.max_drawdown),
        "final_equity": float(m.final_equity_from_unit),
    }


def _per_config_verdict(is_m, oos_m, fwd_m, wf_pass: bool, median_hold: float) -> dict:
    """Per-config winner-criteria evaluation (subset; PBO/DSR at aggregator)."""
    checks: list[tuple[str, bool, str]] = [
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


def run_one_config(
    config_name: str,
    config_entry: dict,
    iter_num: int,
) -> dict:
    """Execute ONE config end-to-end and build the summary payload."""
    risk_on_tickers = list(config_entry["risk_on_assets"])
    off_regime = str(config_entry["off_regime_asset"]).lower()
    cfg = PlanoALeveragedRotationConfig(
        regime_signal=config_entry["regime_signal"],
        leverage=float(config_entry["leverage"]),
        off_regime_asset=off_regime,  # type: ignore[arg-type]
        risk_on_tickers=tuple(risk_on_tickers),
    )

    risk_on_panel, off_panel = _build_panels(risk_on_tickers, off_regime)

    t0 = time.time()
    result: PlanoALeveragedRotationResult = simulate_plano_a_rotation(
        risk_on_panel, cfg, off_regime_panel=off_panel
    )
    elapsed = time.time() - t0

    ret = result.daily_returns
    is_m = compute_split_metrics("IS", _slice(ret, *IS_RANGE))
    oos_m = compute_split_metrics("OOS", _slice(ret, *OOS_RANGE))
    fwd_m = compute_split_metrics("FWD", _slice(ret, *FWD_RANGE))

    # Walk-forward on the full non-trivial return series.
    ret_clean = ret.loc[ret != 0.0]
    if len(ret_clean) >= 8:
        wf_ratio, wf_max_dd, wf_pass = walk_forward_verdict_from_returns(
            ret_clean,
            n_windows=8,
            min_profitable_ratio=6 / 8,
            max_drawdown_cap=0.25,
        )
    else:
        wf_ratio, wf_max_dd, wf_pass = 0.0, float("inf"), False

    last_weights = result.weights.iloc[-1]
    last_nonzero = [
        (col, float(w)) for col, w in last_weights.items() if abs(w) > 1e-9
    ]

    payload = {
        "config_name": config_name,
        "config_entry": dict(config_entry),
        "universe": risk_on_tickers,
        "universe_size": len(risk_on_tickers),
        "off_regime_asset": off_regime,
        "window": {
            "start": str(ret.index[0].date()),
            "end": str(ret.index[-1].date()),
            "n_bars": int(len(ret)),
            "n_switches_total": int(result.n_switches_total),
        },
        "splits": {
            "IS": {"range": list(IS_RANGE), **_metrics_dict(is_m)},
            "OOS": {"range": list(OOS_RANGE), **_metrics_dict(oos_m)},
            "FWD": {"range": list(FWD_RANGE), **_metrics_dict(fwd_m)},
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
            "n_switches_total": int(result.n_switches_total),
            "switches_by_ticker": {
                t: int(v) for t, v in result.switches_by_ticker.items()
            },
        },
        "costs": {
            "cum_transaction_cost_pct": float(result.cum_cost_pct),
            "cum_swap_cost_pct": float(result.cum_swap_pct),
            "spread_half_bps": cfg.spread_half_bps,
            "commission_round_trip_bps": cfg.commission_round_trip_bps,
            "slippage_bps_round_trip": cfg.slippage_bps_round_trip,
            "swap_daily_pct_long": cfg.swap_daily_pct_long,
        },
        "last_bar_positions": [
            {"leg": col, "weight": w} for col, w in last_nonzero
        ],
        "runtime_seconds": round(elapsed, 2),
        "iter": iter_num,
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verdict_per_config": _per_config_verdict(
            is_m, oos_m, fwd_m, wf_pass, result.median_hold_days
        ),
    }

    # Persist daily returns for aggregator.
    daily_series_path = (
        REGISTRY_PATH.parent / f"{config_name}_daily_returns.parquet"
    )
    daily_series_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = daily_series_path.with_suffix(".parquet.tmp")
    ret.to_frame("ret").to_parquet(tmp)
    os.replace(tmp, daily_series_path)

    return payload


def render_markdown(summary: dict) -> str:
    name = summary["config_name"]
    ce = summary["config_entry"]
    is_s = summary["splits"]["IS"]
    oos_s = summary["splits"]["OOS"]
    fwd_s = summary["splits"]["FWD"]
    wf = summary["walk_forward"]
    hm = summary["hold_metrics"]
    cs = summary["costs"]
    vd = summary["verdict_per_config"]

    all_pass = vd["all_pass_except_cross_config_gates"]
    badge = (
        "✅ PASS subset" if all_pass else f"❌ FAIL ({len(vd['failed_subset_gates'])} gates)"
    )

    lines: list[str] = []
    lines.append(f"# V2-L2 Gayed-CFD rotation — `{name}` (iter {summary['iter']})")
    lines.append("")
    lines.append(f"**Path tag:** [SHORT-HOLD CFD]  |  **Status:** {badge}")
    lines.append(
        f"**Config:** signal={ce['regime_signal']}, leverage={ce['leverage']}x, "
        f"off-regime={ce['off_regime_asset']}, risk-on={','.join(ce['risk_on_assets'])}, "
        f"daily close rebalance"
    )
    lines.append(
        f"**Window:** {summary['window']['start']} → {summary['window']['end']} "
        f"({summary['window']['n_bars']} bars, {summary['window']['n_switches_total']} regime switches)"
    )
    lines.append("")

    lines.append("## Split metrics")
    lines.append("")
    lines.append("| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |")
    lines.append("|-------|-------|-------:|-------:|-----:|------:|-------------:|")
    for s, label in ((is_s, "IS"), (oos_s, "OOS"), (fwd_s, "FWD")):
        lines.append(
            f"| {label} | {s['range'][0]} → {s['range'][1]} | "
            f"{s['n_bars']} | {s['sharpe']:.3f} | {s['cagr']:.2%} | "
            f"{s['max_drawdown']:.2%} | {s['final_equity']:.3f} |"
        )
    lines.append("")

    lines.append("## Walk-forward (8 windows)")
    lines.append("")
    lines.append(
        f"- Profitable windows: **{wf['profitable_ratio']:.2f}** "
        f"(target ≥ {wf['min_profitable_ratio']:.2f})"
    )
    lines.append(
        f"- Max window drawdown: **{wf['max_window_drawdown']:.1%}** "
        f"(cap {wf['max_drawdown_cap']:.0%})"
    )
    lines.append(f"- Pass: **{'YES' if wf['pass'] else 'NO'}**")
    lines.append("")

    lines.append("## Hold / switch diagnostics")
    lines.append("")
    lines.append(
        f"- Median hold: **{hm['median_hold_days']:.1f} days** "
        f"(target ≥ 3d, V2 spec §1)"
    )
    lines.append(f"- Total regime switches: {hm['n_switches_total']}")
    lines.append(
        f"- Switches by ticker: "
        + ", ".join(f"{t}={v}" for t, v in hm["switches_by_ticker"].items())
    )
    lines.append("")

    lines.append("## Cost breakdown (Pepperstone Razor retail)")
    lines.append("")
    lines.append(
        f"- Cumulative transaction cost: **{cs['cum_transaction_cost_pct']:.3%}** of starting equity"
    )
    lines.append(
        f"- Cumulative overnight swap: **{cs['cum_swap_cost_pct']:.3%}** of starting equity"
    )
    lines.append(
        f"- Spread half: {cs['spread_half_bps']:.1f} bps | "
        f"commission RT: {cs['commission_round_trip_bps']:.1f} bps | "
        f"slippage RT: {cs['slippage_bps_round_trip']:.1f} bps | "
        f"swap daily long: {cs['swap_daily_pct_long']:.4f}%"
    )
    lines.append("")

    lines.append("## Subset-gate verdict (per-config; PBO/DSR deferred to aggregator)")
    lines.append("")
    lines.append("| Gate | Value | Pass |")
    lines.append("|------|------:|:----:|")
    for c in vd["checks"]:
        lines.append(
            f"| {c['name']} | {c['value']} | {'✅' if c['pass'] else '❌'} |"
        )
    lines.append("")
    if vd["failed_subset_gates"]:
        lines.append(f"**Failed gates:** {', '.join(vd['failed_subset_gates'])}")
    else:
        lines.append(
            "**All subset gates passed.** Final PASS requires aggregator PBO/DSR verdict."
        )
    lines.append("")

    lines.append("## Last-bar positions")
    lines.append("")
    if summary["last_bar_positions"]:
        lines.append("| Leg | Weight |")
        lines.append("|-----|------:|")
        for pos in summary["last_bar_positions"]:
            lines.append(f"| {pos['leg']} | {pos['weight']:.4f} |")
    else:
        lines.append("_Portfolio fully flat on the last bar._")
    lines.append("")

    lines.append("## Citations")
    lines.append("")
    lines.append(
        "- Regime rotation + MA filter + leverage discipline: "
        "`[leverage_for_the_long_run, p.7, p.11, p.13, p.14, p.16, p.17, p.21]`."
    )
    lines.append(
        "- Leverage cap cross-check via PoR: `[leverage_space, Vince]`, "
        "`[math_money_mgmt, Vince]`."
    )
    lines.append(
        "- Carver CFD cost model + risk budget: `[systematic_trading, ch.8-9]`."
    )
    lines.append(
        "- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`."
    )
    lines.append(
        "- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iter", type=int, required=True)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    reg = load_registry(REGISTRY_PATH)
    if reg["status"] not in {"pending", "sweeping"}:
        print(
            f"[iter_v2_l2_run_config] registry status is {reg['status']!r}, "
            "nothing to sweep",
            file=sys.stderr,
        )
        return 1
    if not reg["tickers_pending"]:
        print(
            "[iter_v2_l2_run_config] no pending work units — aggregator next",
            file=sys.stderr,
        )
        return 2

    config_name = reg["tickers_pending"][0]
    cfg_entry = next(c for c in reg["configs"] if c["name"] == config_name)

    print(f"[iter {args.iter}] running {config_name}")
    summary = run_one_config(
        config_name=config_name,
        config_entry=cfg_entry,
        iter_num=args.iter,
    )

    out_dir = REGISTRY_PATH.parent
    json_path = out_dir / f"{config_name}.json"
    md_path = out_dir / f"{config_name}.md"
    _atomic_write_json(json_path, summary)
    _atomic_write_text(md_path, render_markdown(summary))

    # Registry update — pop + append + advance status.
    popped, reg_after_pop = pop_pending(reg)
    assert popped == config_name, (popped, config_name)

    registry_summary = {
        "ticker": config_name,
        "frequency": "daily",
        "window_start": summary["window"]["start"],
        "window_end": summary["window"]["end"],
        "iter": args.iter,
        "n_configs_tested": 1,
        "best_config": config_name,
        "best_sharpe_oos": summary["splits"]["OOS"]["sharpe"],
        "best_cagr": summary["splits"]["OOS"]["cagr"],
        "best_maxdd": summary["splits"]["OOS"]["max_drawdown"],
        "any_pass_5gate": summary["verdict_per_config"][
            "all_pass_except_cross_config_gates"
        ],
        "median_hold_days": summary["hold_metrics"]["median_hold_days"],
        "result_file_md": str(md_path).replace(os.sep, "/"),
        "result_file_json": str(json_path).replace(os.sep, "/"),
    }
    reg_after = append_done(reg_after_pop, registry_summary)
    reg_after = advance_status(reg_after)
    atomic_write_registry(REGISTRY_PATH, reg_after)

    print(
        f"[iter {args.iter}] {config_name}: "
        f"IS Sharpe={summary['splits']['IS']['sharpe']:.3f} "
        f"OOS Sharpe={summary['splits']['OOS']['sharpe']:.3f} "
        f"FWD Sharpe={summary['splits']['FWD']['sharpe']:.3f} "
        f"MedHold={summary['hold_metrics']['median_hold_days']:.1f}d "
        f"WF={'PASS' if summary['walk_forward']['pass'] else 'FAIL'}"
    )
    print(
        f"[iter {args.iter}] subset-gate verdict: "
        f"{summary['verdict_per_config']['n_passed']}/"
        f"{summary['verdict_per_config']['n_total']} pass; "
        f"failed: {summary['verdict_per_config']['failed_subset_gates']}"
    )
    print(f"[iter {args.iter}] registry status → {reg_after['status']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
