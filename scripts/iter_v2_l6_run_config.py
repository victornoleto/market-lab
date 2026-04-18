"""Run ONE V2-L6 Donchian/ATR vol-breakout config across 10 ETFs.

Invoked by the self-improve loop agent inside a fan-out iter for lead
V2-L6 (``reports/phase3_5a_v2/v2_l6_vol_breakout/registry.json``).
Pops ``tickers_pending[0]`` (a config name), runs DonchianBreakoutStrategy
on each ticker in the config's universe as an equal-weight 1/N portfolio,
writes ``<config>.json`` + ``<config>.md`` atomically, then updates the
registry via the standard helpers.

Citations
---------

* Donchian channel breakout 20/10 canonical: ``[trading_systems_methods,
  p.353]``.
* Chandelier trailing ATR exit: ``[volatility_trading]``.
* Trend-follow discipline + 1/N multi-asset: ``[trend_following_covel]``.
* Walk-forward 6/8 gate: ``[advances_fin_ml, ch.11]``.
* Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3.

Usage:
  .venv/bin/python scripts/iter_v2_l6_run_config.py --iter 68
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ai_trade.backtest.engine import (  # noqa: E402
    ExecutionConfig,
    ExecutionSimulator,
    Runner,
    SwapModel,
)
from ai_trade.backtest.grid.letf_rotation_b1c import (  # noqa: E402
    compute_split_metrics,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.strategies.donchian_breakout import (  # noqa: E402
    DonchianBreakoutStrategy,
)
from ai_trade.backtest.sweeps.registry import (  # noqa: E402
    advance_status,
    append_done,
    atomic_write_registry,
    load_registry,
    pop_pending,
)


REGISTRY_PATH = Path(
    "reports/phase3_5a_v2/v2_l6_vol_breakout/registry.json"
)
TIINGO_DAILY_DIR = Path("data/tiingo/daily/prices")

# Panel intersection window — set by the latest first_dt across the 10 ETFs
# (DIA/UNG/HYG all start 2014-01-02 per data/tiingo/manifest.json, verified
# 2026-04-19). Splits align with V2 mandate §4 (IS ~66%, OOS ~24%, FWD ~10%).
PANEL_START = "2014-01-02"
PANEL_END = "2026-04-14"
IS_RANGE = ("2014-01-02", "2021-12-31")
OOS_RANGE = ("2022-01-01", "2024-12-31")
FWD_RANGE = ("2025-01-01", "2026-04-14")

# Pepperstone Razor cost model for ETF / Share CFDs (spec §3).
# Conservative calibration: spread + slippage dominate; commission absorbed
# into spread for per-unit ExecutionConfig interface.
SPREAD_HALF_BPS = 2.0      # 2 bps half-spread (Share CFD retail)
SLIPPAGE_BPS = 1.0         # 1 bp slippage per side
SWAP_LONG_DAILY = 0.00005  # 0.5 bps/day long financing
SWAP_SHORT_DAILY = 0.00002  # 0.2 bps/day short credit cost

TRADING_DAYS = 252


@dataclass
class TickerRun:
    ticker: str
    equity_curve: pd.Series          # daily equity starting at 1.0
    daily_returns: pd.Series         # period-by-period returns
    n_trades: int
    median_hold_days: float


# ---------------------------------------------------------------------------
# I/O helpers


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


def _load_parquet(ticker: str) -> pd.DataFrame:
    path = TIINGO_DAILY_DIR / f"{ticker}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"missing parquet: {path}")
    df = pd.read_parquet(path)
    df.index = pd.DatetimeIndex(df.index)
    return df


def _slice(series: pd.Series, start: str, end: str) -> pd.Series:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    return series.loc[(series.index >= s) & (series.index <= e)]


# ---------------------------------------------------------------------------
# Backtest per ticker


def _median_hold_days(trades) -> float:
    if not trades:
        return 0.0
    holds: list[float] = []
    for t in trades:
        dlt = pd.Timestamp(t.exit_time) - pd.Timestamp(t.entry_time)
        holds.append(dlt.total_seconds() / 86400.0)
    return float(np.median(holds)) if holds else 0.0


def _backtest_one(
    ticker: str,
    df: pd.DataFrame,
    config_entry: dict,
    initial_cash: float = 100_000.0,
) -> TickerRun:
    """Run the Donchian strategy on one ticker; return daily equity + returns."""
    direction_in = config_entry["direction"]
    direction = {
        "long_only": "long",
        "long_short": "both",
        "short_only": "short",
    }[direction_in]

    exit_type = config_entry["exit_type"]
    if exit_type == "trailing_atr_3x":
        exit_mode = "chandelier"
        exit_lookback = 1
        atr_stop_mult = 0.0
        atr_exit_mult = float(config_entry["atr_multiplier"])
    elif exit_type == "opposite_channel":
        exit_mode = "donchian"
        exit_lookback = int(config_entry["exit_lookback"])
        atr_stop_mult = 2.0
        atr_exit_mult = 0.0
    else:
        raise ValueError(f"unsupported exit_type {exit_type!r}")

    entry_lookback = int(config_entry["entry_lookback"])
    atr_period = int(config_entry.get("atr_period", 14))

    # Donchian max_hold in DAYS (this is a daily strategy).
    max_hold = 120

    data = {ticker: df}
    strat = DonchianBreakoutStrategy(
        data=data,
        symbol=ticker,
        entry_lookback=entry_lookback,
        exit_lookback=exit_lookback,
        atr_lookback=atr_period,
        atr_stop_mult=atr_stop_mult,
        max_hold=max_hold,
        risk_pct_of_equity=0.95,
        direction=direction,
        exit_mode=exit_mode,
        atr_exit_mult=atr_exit_mult,
    )

    # Cost model: half_spread and slippage in absolute price units.
    med_price = float(df["close"].median())
    half_spread_abs = med_price * (SPREAD_HALF_BPS / 10_000.0)
    slippage_abs = med_price * (SLIPPAGE_BPS / 10_000.0)

    exec_cfg = ExecutionConfig(
        half_spread=half_spread_abs,
        slippage=slippage_abs,
        commission_per_unit=0.0,
    )
    swap = SwapModel(
        long_rate_per_day=SWAP_LONG_DAILY,
        short_rate_per_day=SWAP_SHORT_DAILY,
    )
    runner = Runner(executor=ExecutionSimulator(exec_cfg), swap_model=swap)
    bt = runner.run(strategy=strat, data=data, initial_cash=initial_cash)

    eq = bt.equity_curve.astype(float)
    rets = eq.pct_change().fillna(0.0)
    return TickerRun(
        ticker=ticker,
        equity_curve=eq / initial_cash,  # normalize to start at 1.0
        daily_returns=rets,
        n_trades=len(bt.trades),
        median_hold_days=_median_hold_days(bt.trades),
    )


# ---------------------------------------------------------------------------
# Portfolio aggregation


def _build_portfolio_returns(runs: list[TickerRun]) -> pd.Series:
    """Daily 1/N equal-weight portfolio returns from per-ticker return series."""
    ret_df = pd.concat(
        {r.ticker: r.daily_returns for r in runs}, axis=1
    ).sort_index()
    ret_df = ret_df.fillna(0.0)
    return ret_df.mean(axis=1)


def _metrics_dict(m) -> dict:
    return {
        "n_bars": int(m.n_bars),
        "sharpe": float(m.sharpe),
        "cagr": float(m.cagr),
        "max_drawdown": float(m.max_drawdown),
        "final_equity": float(m.final_equity_from_unit),
    }


def _per_config_verdict(
    oos_m, fwd_m, wf_pass: bool, median_hold: float
) -> dict:
    """Per-config winner-criteria (subset; PBO/DSR deferred to aggregator)."""
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


def run_one_config(
    config_name: str, config_entry: dict, iter_num: int
) -> dict:
    universe = list(config_entry["universe"])
    t0 = time.time()

    per_ticker_runs: list[TickerRun] = []
    per_ticker_diag: list[dict] = []
    for ticker in universe:
        df = _load_parquet(ticker)
        df = df[(df.index >= pd.Timestamp(PANEL_START)) &
                (df.index <= pd.Timestamp(PANEL_END))]
        if df.empty or len(df) < 400:
            per_ticker_diag.append({
                "ticker": ticker,
                "skipped": True,
                "reason": f"too few bars ({len(df)})",
            })
            continue
        run = _backtest_one(ticker, df, config_entry)
        per_ticker_runs.append(run)
        per_ticker_diag.append({
            "ticker": ticker,
            "n_bars": int(len(df)),
            "n_trades": run.n_trades,
            "median_hold_days": run.median_hold_days,
            "final_equity": float(run.equity_curve.iloc[-1]),
            "sharpe_full": float(
                compute_split_metrics("full", run.daily_returns).sharpe
            ),
        })

    if not per_ticker_runs:
        raise RuntimeError(
            f"config {config_name}: all tickers skipped — no portfolio to build"
        )

    port_ret = _build_portfolio_returns(per_ticker_runs)

    is_m = compute_split_metrics("IS", _slice(port_ret, *IS_RANGE))
    oos_m = compute_split_metrics("OOS", _slice(port_ret, *OOS_RANGE))
    fwd_m = compute_split_metrics("FWD", _slice(port_ret, *FWD_RANGE))

    ret_clean = port_ret.loc[port_ret != 0.0]
    if len(ret_clean) >= 8:
        wf_ratio, wf_max_dd, wf_pass = walk_forward_verdict_from_returns(
            ret_clean, n_windows=8, min_profitable_ratio=6 / 8,
            max_drawdown_cap=0.25,
        )
    else:
        wf_ratio, wf_max_dd, wf_pass = 0.0, float("inf"), False

    # Portfolio-level median hold = mean across active tickers
    # (position lifetimes are independent per ticker in this framework).
    active_holds = [r.median_hold_days for r in per_ticker_runs if r.n_trades > 0]
    port_median_hold = float(np.median(active_holds)) if active_holds else 0.0

    n_total_trades = sum(r.n_trades for r in per_ticker_runs)

    verdict = _per_config_verdict(oos_m, fwd_m, wf_pass, port_median_hold)

    elapsed = time.time() - t0

    payload = {
        "config_name": config_name,
        "config_entry": dict(config_entry),
        "universe": universe,
        "universe_size": len(universe),
        "n_active_tickers": len(per_ticker_runs),
        "window": {
            "start": PANEL_START,
            "end": PANEL_END,
            "n_bars": int(len(port_ret)),
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
            "portfolio_median_hold_days": port_median_hold,
            "n_total_trades": int(n_total_trades),
            "per_ticker": per_ticker_diag,
        },
        "costs_model": {
            "spread_half_bps": SPREAD_HALF_BPS,
            "slippage_bps": SLIPPAGE_BPS,
            "swap_daily_pct_long": SWAP_LONG_DAILY,
            "swap_daily_pct_short": SWAP_SHORT_DAILY,
            "weighting": "equal_weight_1_over_N",
            "citation": "pepperstone razor tier (Phase 3.5a-V2 spec §3)",
        },
        "runtime_seconds": round(elapsed, 2),
        "iter": iter_num,
        "produced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verdict_per_config": verdict,
    }

    # Persist portfolio daily returns for aggregator.
    daily_series_path = (
        REGISTRY_PATH.parent / f"{config_name}_daily_returns.parquet"
    )
    daily_series_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = daily_series_path.with_suffix(".parquet.tmp")
    port_ret.to_frame("ret").to_parquet(tmp)
    os.replace(tmp, daily_series_path)

    return payload


# ---------------------------------------------------------------------------
# Markdown rendering


def render_markdown(s: dict) -> str:
    ce = s["config_entry"]
    is_s = s["splits"]["IS"]
    oos_s = s["splits"]["OOS"]
    fwd_s = s["splits"]["FWD"]
    wf = s["walk_forward"]
    hm = s["hold_metrics"]
    cm = s["costs_model"]
    vd = s["verdict_per_config"]

    all_pass = vd["all_pass_except_cross_config_gates"]
    badge = (
        "✅ PASS subset"
        if all_pass
        else f"❌ FAIL ({len(vd['failed_subset_gates'])} gates)"
    )

    lines: list[str] = []
    lines.append(
        f"# V2-L6 vol breakout — `{s['config_name']}` (iter {s['iter']})"
    )
    lines.append("")
    lines.append(f"**Path tag:** [SHORT-HOLD CFD]  |  **Status:** {badge}")
    direction_human = {
        "long_only": "long-only",
        "long_short": "long/short",
        "short_only": "short-only",
    }.get(ce["direction"], ce["direction"])
    lines.append(
        f"**Config:** Donchian entry={ce['entry_lookback']}d, "
        f"exit={ce['exit_type']}"
        + (
            f" (ATR {ce['atr_multiplier']}× on {ce['atr_period']}d)"
            if ce["exit_type"] == "trailing_atr_3x"
            else f" (opposite {ce['exit_lookback']}d channel)"
        )
        + f", direction={direction_human}"
    )
    lines.append(
        f"**Universe:** {', '.join(s['universe'])} "
        f"({s['n_active_tickers']}/{s['universe_size']} active)"
    )
    lines.append(
        f"**Window:** {s['window']['start']} → {s['window']['end']} "
        f"({s['window']['n_bars']} bars, equal-weight 1/N)"
    )
    lines.append("")

    lines.append("## Split metrics (portfolio)")
    lines.append("")
    lines.append("| Split | Range | n_bars | Sharpe | CAGR | MaxDD | Final equity |")
    lines.append("|-------|-------|-------:|-------:|-----:|------:|-------------:|")
    for sp, label in ((is_s, "IS"), (oos_s, "OOS"), (fwd_s, "FWD")):
        lines.append(
            f"| {label} | {sp['range'][0]} → {sp['range'][1]} | "
            f"{sp['n_bars']} | {sp['sharpe']:.3f} | {sp['cagr']:.2%} | "
            f"{sp['max_drawdown']:.2%} | {sp['final_equity']:.3f} |"
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

    lines.append("## Hold / trade diagnostics (per ticker)")
    lines.append("")
    lines.append(
        f"- Portfolio median hold: **{hm['portfolio_median_hold_days']:.1f} days** "
        f"(target ≥ 3d, V2 spec §1)"
    )
    lines.append(f"- Total trades across tickers: {hm['n_total_trades']}")
    lines.append("")
    lines.append("| Ticker | Bars | Trades | Med hold (d) | Final eq | Sharpe (full) |")
    lines.append("|--------|-----:|-------:|-------------:|---------:|--------------:|")
    for row in hm["per_ticker"]:
        if row.get("skipped"):
            lines.append(
                f"| {row['ticker']} | — | — | — | — | _skipped: {row['reason']}_ |"
            )
            continue
        lines.append(
            f"| {row['ticker']} | {row['n_bars']} | {row['n_trades']} | "
            f"{row['median_hold_days']:.1f} | {row['final_equity']:.3f} | "
            f"{row['sharpe_full']:.3f} |"
        )
    lines.append("")

    lines.append("## Cost model (Pepperstone Razor retail, Share CFD)")
    lines.append("")
    lines.append(
        f"- Spread half: {cm['spread_half_bps']:.1f} bps | "
        f"Slippage: {cm['slippage_bps']:.1f} bps/side | "
        f"Swap long: {cm['swap_daily_pct_long']:.4%}/day | "
        f"Swap short: {cm['swap_daily_pct_short']:.4%}/day"
    )
    lines.append(f"- Weighting: {cm['weighting']}")
    lines.append(f"- Citation: {cm['citation']}")
    lines.append("")

    lines.append("## Subset-gate verdict (per-config; PBO/DSR at aggregator)")
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

    lines.append("## Citations")
    lines.append("")
    lines.append(
        "- Donchian channel breakout 20/10 canonical: "
        "`[trading_systems_methods, p.353]`."
    )
    lines.append(
        "- Chandelier trailing ATR exit: `[volatility_trading]`."
    )
    lines.append(
        "- 1/N multi-asset trend-follow discipline: `[trend_following_covel]`."
    )
    lines.append(
        "- Walk-forward 6/8 gate + 25% DD cap: `[advances_fin_ml, ch.11]`."
    )
    lines.append(
        "- Retail Pepperstone Razor cost model: Phase 3.5a-V2 spec §3."
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main


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
            f"[iter_v2_l6_run_config] registry status is {reg['status']!r}, "
            "nothing to sweep",
            file=sys.stderr,
        )
        return 1
    if not reg["tickers_pending"]:
        print(
            "[iter_v2_l6_run_config] no pending work units — aggregator next",
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
        "median_hold_days": summary["hold_metrics"][
            "portfolio_median_hold_days"
        ],
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
        f"MedHold={summary['hold_metrics']['portfolio_median_hold_days']:.1f}d "
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
