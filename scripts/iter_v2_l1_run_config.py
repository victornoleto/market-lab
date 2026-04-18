"""Run ONE V2-L1 TSMOM-multi-asset config over the 30-instrument universe.

Invoked by the self-improve loop agent inside a fan-out iter. Reads the
registry at ``reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/registry.json``,
pops ``tickers_pending[0]`` (which is a config name in this sweep —
``work_unit_kind: "config"``), runs the full 30-asset backtest for that
config, writes ``<config>.json`` + ``<config>.md`` atomically, then
updates the registry.

Citations:
* ``[systematic_trading, ch.8-9]`` — Carver TSMOM family.
* ``[trend_following_covel, ch.5-6]`` — CTA breadth/monthly rebalance.
* ``[advances_fin_ml, p.162-164]`` — no-look-ahead vol sizing.
* ``[advances_fin_ml, ch.11]`` — walk-forward verdict logic.
* Pepperstone retail cost model: Phase 3.5a-V2 spec §3.

Usage:
  .venv/bin/python scripts/iter_v2_l1_run_config.py

The agent argument source is the registry, so no CLI args besides the
registry path (hard-coded for this lead).
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
    TRADING_DAYS,
    compute_split_metrics,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.strategies.tsmom_multi_asset import (  # noqa: E402
    TSMOMMultiAssetConfig,
    TSMOMMultiAssetResult,
    default_asset_class,
    simulate_tsmom_multi_asset,
)
from ai_trade.backtest.sweeps.registry import (  # noqa: E402
    append_done,
    atomic_write_registry,
    advance_status,
    load_registry,
    pop_pending,
)


REGISTRY_PATH = Path(
    "reports/phase3_5a_v2/v2_l1_tsmom_multi_asset_daily/registry.json"
)
UNIVERSE_PATH = Path("data/universe_plano_a_v2.json")
TIINGO_DAILY_DIR = Path("data/tiingo/daily/prices")

# Canonical IS/OOS/FWD splits for V2-L1. Rationale in iter doc:
# * IS: 2001-05-14 → 2017-12-31 — longest start (SPY first_dt), covers
#   dot-com recovery, GFC, post-GFC regime.
# * OOS: 2018-01-01 → 2023-12-31 — 2018 VIX blow-up, COVID, 2022 bear,
#   2023 AI rally. Full-universe (all 30 instruments) from 2020.
# * FWD stress: 2024-01-01 → 2026-04-14 — AI rally + 2024 correction +
#   2025-2026.
IS_RANGE = ("2001-05-14", "2017-12-31")
OOS_RANGE = ("2018-01-01", "2023-12-31")
FWD_RANGE = ("2024-01-01", "2026-04-14")


def load_universe_tickers() -> list[str]:
    """Read data/universe_plano_a_v2.json, returning the 30 tickers V2-L1
    bootstrapped into the registry (which is a subset of the 39-total
    screener output)."""
    reg = load_registry(REGISTRY_PATH)
    return list(reg["universe"])


def load_price_panel(tickers: list[str]) -> dict[str, pd.DataFrame]:
    """Load each Tiingo daily parquet. Forex parquet keys are lower-case."""
    universe = json.loads(UNIVERSE_PATH.read_text())
    key_by_ticker = {i["ticker"]: i["parquet_key"] for i in universe["instruments"]}

    panel: dict[str, pd.DataFrame] = {}
    for t in tickers:
        key = key_by_ticker.get(t, t)
        path = TIINGO_DAILY_DIR / f"{key}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"missing parquet for {t}: {path}")
        df = pd.read_parquet(path)
        df.index = pd.DatetimeIndex(df.index)
        panel[t] = df
    return panel


def build_config_from_registry_entry(entry: dict) -> TSMOMMultiAssetConfig:
    return TSMOMMultiAssetConfig(
        lookback_days=int(entry["lookback_days"]),
        vol_target_annual=float(entry["vol_target_annual"]),
    )


def _slice(series: pd.Series, start: str, end: str) -> pd.Series:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    return series.loc[(series.index >= s) & (series.index <= e)]


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


def run_one_config(
    config_name: str,
    config_entry: dict,
    universe_tickers: list[str],
    price_panel: dict[str, pd.DataFrame],
    iter_num: int,
) -> dict:
    """Execute one sweep unit end-to-end. Returns the summary dict that
    :func:`append_done` expects (schema v1 §5.1)."""
    cfg = build_config_from_registry_entry(config_entry)
    class_map = {t: default_asset_class(t) for t in universe_tickers}

    t0 = time.time()
    result: TSMOMMultiAssetResult = simulate_tsmom_multi_asset(
        price_panel, cfg, asset_class_lookup=class_map
    )
    elapsed = time.time() - t0

    # Metrics per split.
    ret = result.daily_returns
    is_m = compute_split_metrics("IS", _slice(ret, *IS_RANGE))
    oos_m = compute_split_metrics("OOS", _slice(ret, *OOS_RANGE))
    fwd_m = compute_split_metrics("FWD", _slice(ret, *FWD_RANGE))

    # Walk-forward over the FULL window (returns indexed by trading day).
    # Drop leading bars where returns are exactly 0 (warmup+inactive)
    # to avoid the 8-window split being polluted by all-zero IS years.
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

    # Per-asset summary at last bar.
    last_weights = result.weights.iloc[-1]
    last_longs = [
        (t, float(w)) for t, w in last_weights.items() if w > 0
    ]

    # Costs as pct of starting equity (cum_cost / cum_swap in
    # TSMOMMultiAssetResult are fractions of unit starting equity).
    json_payload = {
        "config_name": config_name,
        "config_entry": dict(config_entry),
        "universe": universe_tickers,
        "universe_size": len(universe_tickers),
        "window": {
            "start": str(ret.index[0].date()),
            "end": str(ret.index[-1].date()),
            "n_bars": int(len(ret)),
            "n_rebalances": int(result.n_rebalances),
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
            "n_long_bar_positions": int(result.n_long_bar_positions),
            "n_rebalances": int(result.n_rebalances),
        },
        "costs": {
            "cum_transaction_cost_pct": float(result.cum_cost_pct),
            "cum_swap_cost_pct": float(result.cum_swap_pct),
            "swap_daily_bps": 5.0,
            "round_trip_bps_by_class": {
                "etf": 10.0,
                "forex": 8.0,
                "commodity_etf": 13.0,
                "crypto": 20.0,
            },
        },
        "last_bar_longs": [
            {"ticker": t, "weight": w} for t, w in last_longs
        ],
        "daily_returns_compact": {
            "head": {
                str(d.date()): float(v)
                for d, v in ret.head(3).items()
            },
            "tail": {
                str(d.date()): float(v)
                for d, v in ret.tail(3).items()
            },
        },
        "runtime_seconds": round(elapsed, 1),
        "iter": iter_num,
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verdict_per_config": _per_config_verdict(
            is_m, oos_m, fwd_m, wf_pass, result.median_hold_days
        ),
    }

    # Also persist the compact daily-return series for the aggregator
    # (PBO / DSR need all 12 configs' returns aligned at that stage).
    daily_series_path = (
        REGISTRY_PATH.parent / f"{config_name}_daily_returns.parquet"
    )
    daily_series_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = daily_series_path.with_suffix(".parquet.tmp")
    ret.to_frame("ret").to_parquet(tmp)
    os.replace(tmp, daily_series_path)

    return json_payload


def _metrics_dict(m) -> dict:
    return {
        "n_bars": int(m.n_bars),
        "sharpe": float(m.sharpe),
        "cagr": float(m.cagr),
        "max_drawdown": float(m.max_drawdown),
        "final_equity": float(m.final_equity_from_unit),
    }


def _per_config_verdict(
    is_m, oos_m, fwd_m, wf_pass: bool, median_hold: float
) -> dict:
    """Per-config winner-criteria evaluation (subset of V2 spec §1).

    PBO/DSR are NOT applied here — they require the cross-config
    (T, N) matrix that only exists at the aggregator stage. Winner
    criteria applied: OOS Sharpe > 0, FWD Sharpe > 0, WF ≥ 6/8,
    median hold ≥ 3 days, CAGR OOS ≥ 30%, Sharpe OOS ≥ 2.0,
    MaxDD OOS ≤ 25%.
    """
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


def render_markdown(summary: dict) -> str:
    """Human-readable per-config markdown report."""
    name = summary["config_name"]
    lb = summary["config_entry"]["lookback_days"]
    vt = summary["config_entry"]["vol_target_annual"]
    is_s = summary["splits"]["IS"]
    oos_s = summary["splits"]["OOS"]
    fwd_s = summary["splits"]["FWD"]
    wf = summary["walk_forward"]
    hm = summary["hold_metrics"]
    cs = summary["costs"]
    vd = summary["verdict_per_config"]

    all_pass = vd["all_pass_except_cross_config_gates"]
    badge = "✅ PASS subset" if all_pass else f"❌ FAIL ({len(vd['failed_subset_gates'])} gates)"

    lines: list[str] = []
    lines.append(f"# V2-L1 TSMOM multi-asset — `{name}` (iter {summary['iter']})")
    lines.append("")
    lines.append(f"**Path tag:** [SHORT-HOLD CFD]  |  **Status:** {badge}")
    lines.append(
        f"**Config:** lookback={lb}d, vol_target={vt:.0%}, "
        f"binary long/flat, monthly EOM rebalance, 30-asset universe"
    )
    lines.append(
        f"**Window:** {summary['window']['start']} → {summary['window']['end']} "
        f"({summary['window']['n_bars']} bars, {summary['window']['n_rebalances']} rebalances)"
    )
    lines.append("")

    lines.append("## Split metrics")
    lines.append("")
    lines.append("| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |")
    lines.append("|-------|-------|-------:|-------:|-----:|------:|-------------:|")
    for s, label in ((is_s, "IS"), (oos_s, "OOS"), (fwd_s, "FWD")):
        lines.append(
            f"| {label} | {s['range'][0]} → {s['range'][1]} | "
            f"{s['n_bars']} | {s['sharpe']:.3f} | "
            f"{s['cagr']:.2%} | {s['max_drawdown']:.2%} | {s['final_equity']:.3f} |"
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

    lines.append("## Hold / trade diagnostics")
    lines.append("")
    lines.append(
        f"- Median hold: **{hm['median_hold_days']:.1f} days** (target ≥ 3d, V2 spec §1)"
    )
    lines.append(f"- Long bar-positions: {hm['n_long_bar_positions']:,}")
    lines.append(f"- Rebalances: {hm['n_rebalances']}")
    lines.append("")

    lines.append("## Cost breakdown")
    lines.append("")
    lines.append(
        f"- Cumulative transaction cost: **{cs['cum_transaction_cost_pct']:.3%}** of starting equity"
    )
    lines.append(
        f"- Cumulative overnight swap: **{cs['cum_swap_cost_pct']:.3%}** of starting equity"
    )
    lines.append(
        f"- Daily swap (long): {cs['swap_daily_bps']:.1f} bps | "
        f"round-trip: ETF {cs['round_trip_bps_by_class']['etf']} bps, "
        f"FX {cs['round_trip_bps_by_class']['forex']} bps, "
        f"commodity-ETF {cs['round_trip_bps_by_class']['commodity_etf']} bps, "
        f"crypto {cs['round_trip_bps_by_class']['crypto']} bps"
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
        lines.append(
            f"**Failed gates:** {', '.join(vd['failed_subset_gates'])}"
        )
    else:
        lines.append(
            "**All subset gates passed.** Final PASS requires aggregator PBO/DSR verdict."
        )
    lines.append("")

    lines.append("## Last-bar long positions")
    lines.append("")
    if summary["last_bar_longs"]:
        lines.append("| Ticker | Weight |")
        lines.append("|--------|------:|")
        for lng in summary["last_bar_longs"]:
            lines.append(f"| {lng['ticker']} | {lng['weight']:.4f} |")
    else:
        lines.append("_Portfolio fully flat on the last bar._")
    lines.append("")

    lines.append("## Citations")
    lines.append("")
    lines.append(
        "- Time-series momentum family: `[algo_trading_chan, p.133, ch.6]`, "
        "`[systematic_trading, ch.8-9]` (Carver), `[trend_following_covel, ch.5-6]`."
    )
    lines.append(
        "- Vol-target no-look-ahead sizing: `[advances_fin_ml, p.162-164]`."
    )
    lines.append(
        "- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`, "
        "Pardo (2008) ch.10-11, ai-trade gate convention."
    )
    lines.append(
        "- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iter", type=int, default=3, help="Current iteration number"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    reg = load_registry(REGISTRY_PATH)
    if reg["status"] not in {"pending", "sweeping"}:
        print(
            f"[iter_v2_l1_run_config] registry status is {reg['status']!r}, "
            "nothing to sweep",
            file=sys.stderr,
        )
        return 1
    if not reg["tickers_pending"]:
        print(
            "[iter_v2_l1_run_config] no pending work units — aggregator next",
            file=sys.stderr,
        )
        return 2

    config_name = reg["tickers_pending"][0]
    cfg_entry = next(c for c in reg["configs"] if c["name"] == config_name)

    universe = list(reg["universe"])
    print(
        f"[iter {args.iter}] running {config_name} over {len(universe)} instruments"
    )
    panel = load_price_panel(universe)

    summary = run_one_config(
        config_name=config_name,
        config_entry=cfg_entry,
        universe_tickers=universe,
        price_panel=panel,
        iter_num=args.iter,
    )

    # Write per-config .json and .md atomically (both under
    # reports/phase3_5a_v2/v2_l1_.../).
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

    # Report.
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
