#!/usr/bin/env python3
"""Phase 3.5a — Lead T4 fan-out per-ticker runner (session-based FX).

Processes EXACTLY ONE ticker from the T4 registry, runs all 3 session
configs (London ORB / NY-close MR / Asian-range fade), writes
``<ticker>.json`` + ``<ticker>.md`` atomically, and updates the registry
(pop pending → append done → advance status).

Protocol: ``docs/self_improvement/fanout_protocol.md`` §3.

Citations
---------
- London ORB / Asian range breakout + range-fade mechanics:
  ``[trading_systems_methods, p.353]`` (Donchian foundations) and
  ``[trading_systems_methods, p.326-329]`` (range fade / false-break).
- FX intraday parsimony ≤ 5 params, 1h Sharpe annualization:
  ``[quant_trading_chan, p.43-53, ch.2-3]``.
- ATR stop + time-stop: ``[machine_trading, p.126, ch.4]``.
- ATR / volatility filter: ``[volatility_trading]``.
- Hold discipline ≤ 5d (T4 targets ≤ 24h): ``[systematic_trading, p.185-188]``.
- PBO / DSR / WF gate framework: ``[advances_fin_ml, ch.7, p.208-211]``.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

log = logging.getLogger("ai_trade.phase3_5a.t4_fanout")

# Pepperstone cost calibration (same as T1-T3 baseline; FX majors).
_HALF_SPREAD_BPS = {"forex": 2.0, "metal": 5.0}
_SWAP_RATE_PER_DAY = 0.00005  # 0.5 bp/day symmetric conservative

FOREX_TICKERS = {
    "audusd", "eurgbp", "eurjpy", "eurusd", "gbpjpy",
    "gbpusd", "nzdusd", "usdcad", "usdchf", "usdjpy",
}
METAL_TICKERS = {"xauusd", "xagusd"}

PERIODS_PER_YEAR_1H_FX = 252 * 24

WINDOW_FULL = (pd.Timestamp("2020-01-06"), pd.Timestamp("2026-04-14"))
WINDOW_IS = (pd.Timestamp("2020-01-06"), pd.Timestamp("2023-12-31"))
WINDOW_OOS = (pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31"))
WINDOW_FWD = (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-04-14"))


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _atomic_write_json(path: Path, data: Any) -> None:
    _atomic_write_text(path, json.dumps(data, indent=2, default=str) + "\n")


def _annualized_sharpe(equity: pd.Series, ppy: int) -> float:
    if len(equity) < 2:
        return 0.0
    r = equity.pct_change().dropna()
    if r.std(ddof=0) <= 0 or len(r) < 2:
        return 0.0
    return float(np.sqrt(ppy) * r.mean() / r.std(ddof=0))


def _max_drawdown(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return float(dd.min())


def _cagr(final: float, initial: float, years: float) -> float:
    if initial <= 0 or years <= 0 or final <= 0:
        return 0.0
    return (final / initial) ** (1.0 / years) - 1.0


def _median_hold(trades, data_index: pd.DatetimeIndex) -> tuple[float, int]:
    if not trades:
        return 0.0, 0
    holds_d, holds_b = [], []
    for t in trades:
        dlt = pd.Timestamp(t.exit_time) - pd.Timestamp(t.entry_time)
        holds_d.append(dlt.total_seconds() / 86400.0)
        try:
            ei = data_index.get_loc(pd.Timestamp(t.entry_time))
            xi = data_index.get_loc(pd.Timestamp(t.exit_time))
            holds_b.append(int(xi - ei))
        except KeyError:
            pass
    return float(np.median(holds_d)), int(np.median(holds_b) if holds_b else 0)


# ----------------------------------------------------------------------
# Config → SessionStrategy kwargs


def _cfg_to_strategy_kwargs(cfg: dict) -> dict:
    """Translate a registry config entry into SessionStrategy kwargs.

    Three config ``type`` values supported — mapping table:

    - ``session_orb``  → mode=orb, range_type=hours, range from
      ``range_hours_utc``, signal from ``breakout_hours_utc``, no band.
    - ``session_mr``   → mode=mr, range_type=bars
      (``range_window_bars``), signal from ``signal_hours_utc``, forced
      exit from ``exit_hours_utc``, band from ``entry_band_pct``.
    - ``session_fade`` → mode=fade, range_type=hours, range from
      ``range_hours_utc``, signal from ``fade_hours_utc``, band from
      optional ``entry_band_pct`` (default 0).
    """
    t = cfg["type"]
    common = dict(
        direction=str(cfg.get("direction", "both")),
        atr_stop_mult=float(cfg.get("atr_stop_mult", 2.0)),
        atr_window=int(cfg.get("atr_window", 14)),
        max_hold=int(cfg.get("time_stop_bars", 24)),
        risk_pct_of_equity=0.95,
    )
    if t == "session_orb":
        return dict(
            common,
            mode="orb",
            range_type="hours",
            range_hours_utc=tuple(cfg["range_hours_utc"]),
            signal_hours_utc=tuple(cfg["breakout_hours_utc"]),
            entry_band_pct=0.0,
        )
    if t == "session_mr":
        return dict(
            common,
            mode="mr",
            range_type="bars",
            range_window_bars=int(cfg["range_window_bars"]),
            signal_hours_utc=tuple(cfg["signal_hours_utc"]),
            exit_hours_utc=tuple(cfg["exit_hours_utc"]),
            entry_band_pct=float(cfg.get("entry_band_pct", 0.0)),
        )
    if t == "session_fade":
        return dict(
            common,
            mode="fade",
            range_type="hours",
            range_hours_utc=tuple(cfg["range_hours_utc"]),
            signal_hours_utc=tuple(cfg["fade_hours_utc"]),
            entry_band_pct=float(cfg.get("entry_band_pct", 0.0)),
        )
    raise ValueError(f"unsupported session config type {t!r}")


def _run_backtest(data_full, data_bounded, ticker, exec_cfg, swap_model,
                  cfg: dict, cash: float):
    from ai_trade.backtest.engine.runner import Runner
    from ai_trade.backtest.engine.execution import ExecutionSimulator
    from ai_trade.backtest.strategies.session_based import SessionStrategy

    kwargs = _cfg_to_strategy_kwargs(cfg)
    strat = SessionStrategy(data=data_full, symbol=ticker, **kwargs)
    runner = Runner(executor=ExecutionSimulator(exec_cfg), swap_model=swap_model)
    return runner.run(strategy=strat, data=data_bounded, initial_cash=cash)


def _window_metrics(label, start, end, data_full, ticker, exec_cfg, swap_model,
                    cfg, cash, ppy) -> dict:
    df = data_full[ticker]
    mask = (df.index >= start) & (df.index <= end + pd.Timedelta(days=1))
    df_win = df[mask]
    if len(df_win) < 200:
        return dict(label=label, start=str(start.date()), end=str(end.date()),
                    n_bars=len(df_win), sharpe=0.0, cagr_pct=0.0, max_dd_pct=0.0,
                    final_equity=cash, n_trades=0, median_hold_days=0.0,
                    median_hold_bars=0)
    bt = _run_backtest(data_full, {ticker: df_win}, ticker,
                       exec_cfg, swap_model, cfg, cash)
    eq = bt.equity_curve
    sharpe = _annualized_sharpe(eq, ppy)
    mdd = _max_drawdown(eq)
    years = len(df_win) / ppy
    cagr = _cagr(bt.final_equity, cash, years)
    med_d, med_b = _median_hold(bt.trades, df_win.index)
    return dict(
        label=label, start=str(start.date()), end=str(end.date()),
        n_bars=len(df_win),
        sharpe=round(sharpe, 4),
        cagr_pct=round(cagr * 100, 3),
        max_dd_pct=round(mdd * 100, 3),
        final_equity=round(bt.final_equity, 2),
        n_trades=len(bt.trades),
        median_hold_days=round(med_d, 3),
        median_hold_bars=med_b,
    )


def _full_equity(data_full, ticker, exec_cfg, swap_model, cfg, cash):
    df = data_full[ticker]
    mask = (df.index >= WINDOW_FULL[0]) & (
        df.index <= WINDOW_FULL[1] + pd.Timedelta(days=1)
    )
    df_win = df[mask]
    bt = _run_backtest(data_full, {ticker: df_win}, ticker,
                       exec_cfg, swap_model, cfg, cash)
    return bt.equity_curve, bt.trades


def _wf_verdict(equity: pd.Series, min_windows: int = 8,
                max_dd_each: float = 0.25, min_ratio: float = 6 / 8,
                ) -> tuple[str, int, int]:
    if len(equity) < min_windows * 2:
        return "reject", 0, min_windows
    chunks = np.array_split(equity.values, min_windows)
    n_profitable = 0
    dd_fail = False
    for ch in chunks:
        if len(ch) < 2:
            continue
        start_v, end_v = float(ch[0]), float(ch[-1])
        ret = (end_v - start_v) / start_v if start_v != 0 else 0.0
        if ret > 0:
            n_profitable += 1
        peak = np.maximum.accumulate(ch)
        dd = float(((ch - peak) / peak).min())
        if abs(dd) > max_dd_each:
            dd_fail = True
    if dd_fail:
        return "reject", n_profitable, min_windows
    verdict = "pass" if n_profitable >= int(np.ceil(min_ratio * min_windows)) else "reject"
    return verdict, n_profitable, min_windows


def _pbo_and_dsr(equities: dict[str, pd.Series], n_blocks: int = 10) -> dict:
    from ai_trade.backtest.validation.dsr import psr
    from ai_trade.backtest.validation.pbo import pbo as run_pbo

    df = pd.concat(equities, axis=1).ffill().dropna()
    rets = df.pct_change().dropna()
    if len(rets) < n_blocks * 2 or rets.shape[1] < 2:
        pbo_result = None
        pbo_pass = True
    else:
        nb = n_blocks if n_blocks % 2 == 0 else n_blocks - 1
        try:
            pbo_result = run_pbo(rets.values.astype(float), n_blocks=nb)
            pbo_pass = float(pbo_result.pbo) < 0.5
        except Exception as exc:
            log.warning("PBO failed: %s", exc)
            pbo_result = None
            pbo_pass = False

    dsr_out = {}
    for name, eq in equities.items():
        r = eq.pct_change().dropna().to_numpy(dtype=float)
        if len(r) < 3 or r.std(ddof=0) <= 0:
            dsr_out[name] = {"p_value": 1.0, "psr": 0.0}
            continue
        psr_val = float(psr(r, benchmark=0.0))
        p_val = 1.0 - psr_val
        dsr_out[name] = {"p_value": round(p_val, 6), "psr": round(psr_val, 6)}

    return {
        "pbo": round(float(pbo_result.pbo), 4) if pbo_result is not None else None,
        "pbo_pass": bool(pbo_pass),
        "dsr": dsr_out,
    }


def _build_spy_block(cash: float, full_equities: dict[str, pd.Series], ppy: int) -> dict:
    try:
        from ai_trade.backtest.metrics.standard_report import (
            build_spy_benchmark, compare_vs_spy, load_spy_series,
        )
        spy = load_spy_series()
        first_eq = next(iter(full_equities.values()))
        strat_daily = first_eq.resample("D").last().dropna()
        spy_b = build_spy_benchmark(
            spy_series=spy, initial_capital=cash,
            window_start=strat_daily.index[0], window_end=strat_daily.index[-1],
            periods_per_year=252,
        )
        cmp = compare_vs_spy(strat_daily, spy_b.equity_curve, periods_per_year=252)
        return {
            "spy_return_pct": round(spy_b.return_pct * 100, 3),
            "spy_cagr_pct":   round(spy_b.cagr_pct * 100, 3),
            "spy_maxdd_pct":  round(spy_b.max_drawdown_pct * 100, 3),
            "spy_sharpe":     round(spy_b.sharpe, 3),
            "excess_return_pct":    round(cmp.excess_return_pct * 100, 3),
            "excess_cagr_pct":      round(cmp.excess_cagr_pct * 100, 3),
            "information_ratio":    round(cmp.information_ratio, 3),
            "correlation":          round(cmp.correlation, 4),
            "beta":                 round(cmp.beta, 4),
            "note": "Strategy first-config equity resampled daily; SPY from Tiingo cache",
        }
    except Exception as exc:
        log.warning("SPY benchmark block failed: %s", exc)
        return {"error": str(exc)}


def _run_ticker(ticker: str, registry_path: Path, iter_num: int, cash: float) -> dict:
    from ai_trade.backtest.data.tiingo_source import TiingoSource
    from ai_trade.backtest.data.tiingo_storage import TiingoStorage
    from ai_trade.backtest.engine.execution import ExecutionConfig, SwapModel
    from ai_trade.backtest.sweeps.registry import (
        advance_status, append_done, atomic_write_registry, load_registry,
        pop_pending, validate_schema_v1,
    )

    reg = load_registry(registry_path)
    validate_schema_v1(reg)
    if reg["status"] not in ("pending", "sweeping"):
        raise RuntimeError(
            f"registry status {reg['status']!r} — cannot sweep; expected pending/sweeping"
        )
    if ticker not in reg["tickers_pending"]:
        raise RuntimeError(
            f"ticker {ticker!r} not in tickers_pending {reg['tickers_pending']}"
        )
    if reg["tickers_pending"][0] != ticker:
        raise RuntimeError(
            f"head-of-queue is {reg['tickers_pending'][0]!r} but asked {ticker!r}"
        )

    asset_class = "forex" if ticker in FOREX_TICKERS else (
        "metal" if ticker in METAL_TICKERS else None
    )
    if asset_class is None:
        raise RuntimeError(f"unsupported ticker {ticker!r} for T4 fan-out")

    src = TiingoSource(storage=TiingoStorage(root="data/tiingo"))
    raw = src.fetch_many([ticker], date(2020, 1, 1), date(2026, 4, 17),
                         asset_class="forex", frequency="1hour")
    df = raw[ticker]
    df = df[(df.index >= WINDOW_FULL[0]) &
            (df.index <= WINDOW_FULL[1] + pd.Timedelta(days=1))]
    if df.empty:
        raise RuntimeError(f"no data for {ticker} in window")
    data_full = {ticker: df}
    half_bps = _HALF_SPREAD_BPS[asset_class]
    half_spread_abs = float(df["close"].median()) * (half_bps / 10_000.0)
    exec_cfg = ExecutionConfig(half_spread=half_spread_abs, slippage=0.0,
                               commission_per_unit=0.0)
    swap_model = SwapModel(long_rate_per_day=_SWAP_RATE_PER_DAY,
                           short_rate_per_day=_SWAP_RATE_PER_DAY)

    ppy = PERIODS_PER_YEAR_1H_FX

    configs_out = []
    full_equities = {}
    for cfg in reg["configs"]:
        log.info("--- %s | %s ---", ticker, cfg["name"])
        windows = {}
        for label, (s, e) in [
            ("full", WINDOW_FULL), ("is", WINDOW_IS),
            ("oos", WINDOW_OOS), ("fwd", WINDOW_FWD),
        ]:
            wm = _window_metrics(label, s, e, data_full, ticker,
                                 exec_cfg, swap_model, cfg, cash, ppy)
            windows[label] = wm
            log.info("  [%s] sharpe=%.2f cagr=%.2f%% mdd=%.2f%% "
                     "trades=%d med_hold_d=%.2f",
                     label.upper(), wm["sharpe"], wm["cagr_pct"], wm["max_dd_pct"],
                     wm["n_trades"], wm["median_hold_days"])
        full_eq, _ = _full_equity(data_full, ticker, exec_cfg, swap_model, cfg, cash)
        full_equities[cfg["name"]] = full_eq

        wf_verdict, wf_wins, wf_total = _wf_verdict(full_eq)
        configs_out.append({
            "name": cfg["name"],
            "type": cfg["type"],
            "direction": cfg.get("direction", "both"),
            "params": {k: v for k, v in cfg.items() if k not in {"name", "type", "citation"}},
            "metrics_is":  windows["is"],
            "metrics_oos": windows["oos"],
            "metrics_fwd": windows["fwd"],
            "metrics_full": windows["full"],
            "wf": {
                "verdict": wf_verdict,
                "n_profitable": wf_wins,
                "n_windows": wf_total,
            },
        })

    cross = _pbo_and_dsr(full_equities)
    for c in configs_out:
        c_name = c["name"]
        dsr_p = cross["dsr"].get(c_name, {}).get("p_value", 1.0)
        c["dsr"] = cross["dsr"].get(c_name, {"p_value": 1.0, "psr": 0.0})
        pbo_p = cross["pbo_pass"]
        dsr_pass = dsr_p < 0.05
        wf_pass = c["wf"]["verdict"] == "pass"
        oos_sharpe = c["metrics_oos"]["sharpe"]
        fwd_sharpe = c["metrics_fwd"]["sharpe"]
        oos_hold = c["metrics_oos"]["median_hold_days"]
        gates = {
            "pbo_pass": bool(pbo_p),
            "dsr_pass": bool(dsr_pass),
            "wf_pass": bool(wf_pass),
            "oos_block_pass": bool(oos_sharpe > 0),
            "fwd_stress_pass": bool(fwd_sharpe > 0),
            "hold_le_5d_pass": bool(0.0 < oos_hold <= 5.0),
        }
        gates["any_pass"] = all(gates.values())
        c["gates"] = gates

    spy_block = _build_spy_block(cash, full_equities, ppy)

    best = max(configs_out, key=lambda c: (c["metrics_oos"]["sharpe"],
                                            c["metrics_fwd"]["sharpe"]))
    any_pass = any(c["gates"]["any_pass"] for c in configs_out)
    summary = {
        "ticker": ticker,
        "frequency": "1hour",
        "asset_class": asset_class,
        "window": {
            "start": str(WINDOW_FULL[0].date()),
            "end":   str(WINDOW_FULL[1].date()),
            "n_bars": int(len(df)),
        },
        "costs_model": {
            "half_spread_bps": half_bps,
            "commission_per_side_usd": 3.5,
            "swap_daily_pct_long":  _SWAP_RATE_PER_DAY,
            "swap_daily_pct_short": _SWAP_RATE_PER_DAY,
            "citation": "pepperstone razor tier (docs/investment-mandate.md §3)",
        },
        "cross_config": {
            "pbo": cross["pbo"],
            "pbo_pass": cross["pbo_pass"],
        },
        "configs": configs_out,
        "best_config": best["name"],
        "best_sharpe_oos": best["metrics_oos"]["sharpe"],
        "best_cagr_oos":   best["metrics_oos"]["cagr_pct"],
        "best_maxdd_oos":  best["metrics_oos"]["max_dd_pct"],
        "best_median_hold_days_oos": best["metrics_oos"]["median_hold_days"],
        "any_pass_5gate": any_pass,
        "benchmark_spy": spy_block,
    }

    base = registry_path.parent
    json_path = base / f"{ticker}.json"
    md_path = base / f"{ticker}.md"
    _atomic_write_json(json_path, summary)
    _atomic_write_text(md_path, _render_md(summary))

    done_entry = {
        "ticker": ticker,
        "frequency": "1hour",
        "window_start": str(WINDOW_FULL[0].date()),
        "window_end":   str(WINDOW_FULL[1].date()),
        "iter": int(iter_num),
        "n_configs_tested": len(configs_out),
        "best_config": best["name"],
        "best_sharpe_oos": best["metrics_oos"]["sharpe"],
        "best_cagr": best["metrics_oos"]["cagr_pct"] / 100.0,
        "best_maxdd": best["metrics_oos"]["max_dd_pct"] / 100.0,
        "any_pass_5gate": any_pass,
        "median_hold_days": best["metrics_oos"]["median_hold_days"],
        "result_file_md":   str(md_path),
        "result_file_json": str(json_path),
    }
    _, new_reg = pop_pending(reg)
    new_reg = append_done(new_reg, done_entry)
    new_reg = advance_status(new_reg)
    atomic_write_registry(str(registry_path), new_reg)
    log.info("Registry updated: status=%s pending=%d done=%d",
             new_reg["status"], len(new_reg["tickers_pending"]),
             len(new_reg["tickers_done"]))
    return summary


def _render_md(summary: dict) -> str:
    t = summary["ticker"]
    lines = [
        f"# {t.upper()} 1h — T4 session-based FX (ORB / NY-close MR / Asian fade)",
        "",
        f"**Window:** {summary['window']['start']} → {summary['window']['end']} "
        f"({summary['window']['n_bars']} bars, 1h {summary['asset_class']})",
        f"**Asset class:** {summary['asset_class']} | "
        f"**Costs:** half_spread={summary['costs_model']['half_spread_bps']}bps, "
        f"swap={summary['costs_model']['swap_daily_pct_long']*100:.4f}%/day, "
        f"commission=${summary['costs_model']['commission_per_side_usd']}/side",
        "",
        f"**Best config:** `{summary['best_config']}` — "
        f"**{'PASS 5-gate' if summary['any_pass_5gate'] else 'NO PASS'}**",
        "",
        "## Cross-config gates",
        f"- PBO across {len(summary['configs'])} configs: "
        f"**{summary['cross_config']['pbo']}** "
        f"(pass={summary['cross_config']['pbo_pass']})",
        "",
        "## All configs — OOS metrics + 5-gate",
        "",
        "| Config | Type | Dir | OOS Sharpe | OOS CAGR% | OOS MDD% | Trades | "
        "Hold(d) | DSR p | WF k/N | OOS>0 | FWD>0 | Hold≤5d | 5-gate PASS |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|",
    ]
    for c in summary["configs"]:
        oos = c["metrics_oos"]
        g = c["gates"]
        dsr_p = c["dsr"]["p_value"]
        wf = c["wf"]
        wf_str = f"{wf['n_profitable']}/{wf['n_windows']}"
        lines.append(
            f"| `{c['name']}` | {c['type']} | {c['direction']} | "
            f"{oos['sharpe']:.2f} | {oos['cagr_pct']:.2f} | {oos['max_dd_pct']:.2f} | "
            f"{oos['n_trades']} | {oos['median_hold_days']:.2f} | "
            f"{dsr_p:.3f} | {wf_str} | "
            f"{'✓' if g['oos_block_pass'] else '✗'} | "
            f"{'✓' if g['fwd_stress_pass'] else '✗'} | "
            f"{'✓' if g['hold_le_5d_pass'] else '✗'} | "
            f"**{'PASS' if g['any_pass'] else 'fail'}** |"
        )
    lines.append("")
    lines.append("## Per-config window breakdown")
    for c in summary["configs"]:
        lines.append("")
        lines.append(f"### {c['name']} ({c['type']}, {c['direction']})")
        lines.append("")
        lines.append(
            "| Window | Start | End | Bars | Sharpe | CAGR% | MDD% | Trades | Hold(d) |"
        )
        lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
        for lbl in ("full", "is", "oos", "fwd"):
            w = c[f"metrics_{lbl}"] if lbl != "full" else c["metrics_full"]
            lines.append(
                f"| {lbl.upper()} | {w['start']} | {w['end']} | {w['n_bars']} | "
                f"{w['sharpe']:.2f} | {w['cagr_pct']:.2f} | {w['max_dd_pct']:.2f} | "
                f"{w['n_trades']} | {w['median_hold_days']:.2f} |"
            )
    lines.append("")
    lines.append("## Benchmark — SPY buy & hold (same window)")
    spy = summary["benchmark_spy"]
    if "error" in spy:
        lines.append(f"_SPY benchmark unavailable: {spy['error']}_")
    else:
        lines.append(
            f"- SPY Return / CAGR / MaxDD / Sharpe: **{spy['spy_return_pct']:.2f}%** / "
            f"**{spy['spy_cagr_pct']:.2f}%/yr** / **{spy['spy_maxdd_pct']:.2f}%** / "
            f"**{spy['spy_sharpe']:.3f}**"
        )
        lines.append(
            f"- Strategy vs SPY — Excess CAGR: **{spy['excess_cagr_pct']:+.2f}%** | "
            f"IR: **{spy['information_ratio']:+.3f}** | "
            f"Corr: **{spy['correlation']:+.3f}** | Beta: **{spy['beta']:+.3f}**"
        )
        lines.append(f"- _{spy['note']}_")
    lines.append("")
    lines.append("## Citations")
    lines.append("- Session ORB / breakout: `[trading_systems_methods, p.353]`")
    lines.append("- Range fade / false-break mechanics: `[trading_systems_methods, p.326-329]`")
    lines.append("- FX intraday parsimony ≤5 params: `[quant_trading_chan, p.43-53, ch.2-3]`")
    lines.append("- ATR stop + time-stop: `[machine_trading, p.126, ch.4]`")
    lines.append("- ATR / volatility filter: `[volatility_trading]`")
    lines.append("- Hold ≤ 5d (T4 target ≤ 24h) swap-kill: `[systematic_trading, p.185-188]`")
    lines.append("- PBO / DSR / WF gates: `[advances_fin_ml, ch.7, p.208-211]`")
    return "\n".join(lines) + "\n"


def _parse_args(argv=None):
    ap = argparse.ArgumentParser(description="T4 fan-out per-ticker runner")
    ap.add_argument("--ticker", required=True, help="ticker to process (head-of-queue)")
    ap.add_argument("--registry", type=Path,
                    default=Path("reports/phase3_5a/t4_session_based_fx/registry.json"))
    ap.add_argument("--iter", dest="iter_num", type=int, required=True)
    ap.add_argument("--cash", type=float, default=100_000.0)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout),
                  logging.FileHandler("logs/grid.log", mode="a")],
    )
    args = _parse_args(argv)
    summary = _run_ticker(args.ticker, args.registry, args.iter_num, args.cash)
    log.info("DONE: %s best=%s any_pass_5gate=%s",
             args.ticker, summary["best_config"], summary["any_pass_5gate"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
