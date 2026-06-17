#!/usr/bin/env python3
"""Portfolio export — the data layer the momentum_v2 web-app consumes.

The funnel persists only *scalar* per-config metrics; the holdings timeline,
current portfolio, per-name contribution and return/equity series live in memory
during a run and are discarded. This module re-simulates a chosen set of an
existing window's strategies (reusing the exact engine, so results are identical)
and writes, per strategy, JSON/CSV artifacts a UI can read:

    universes/<universe>/<window>/portfolio/<strategy>/
        meta.json          config + mechanism + headline metrics + gate verdict + disclaimer
        current.json       {as_of, holdings:[{ticker, weight}]}  (latest rebalance)
        history.json       [{date, holdings, entered:[...], exited:[...]}]  per rebalance
        contribution.json  [{ticker, contribution, last_weight}]  arithmetic return attribution
        series.csv         date, ret_after_tax, equity_after_tax, ret_gross, equity_gross,
                           <bench>_ret, <bench>_equity[, spmo_ret, spmo_equity]

Plus a per-window ``portfolio/index.json`` listing the exported strategies.

Research-only, ``promotion_eligible=false``; nothing here changes a verdict.
Citations: dominance lens `[testing_tuning, p.327-335]`; no look-ahead
`[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
for _c in (REPO_ROOT, REPO_ROOT / "src"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from studies.momentum_v2 import config as cfg  # noqa: E402
from studies.momentum_v2 import run  # noqa: E402
from studies.momentum_v2.core import (  # noqa: E402
    PanelCache,
    StrategyConfig,
    apply_br_foreign_annual_tax,
    build_panel_cache,
    equity_from_returns,
    metrics_from_returns,
    precompute_scores,
    simulate_config,
)
from studies.momentum_v2.overlays import market_regime, simulate_evolved, stock_trend_ok  # noqa: E402
from studies.momentum_v2.report import DISCLAIMER, write_json  # noqa: E402

STUDY_DIR = Path(__file__).resolve().parent
WEIGHT_EPS = 1e-9


# --- artifact builders ------------------------------------------------------

def _holdings(row: pd.Series) -> list[dict]:
    """Non-zero holdings of one rebalance row, as [{ticker, weight}] desc by weight."""
    held = [(str(t), float(w)) for t, w in row.items() if float(w) > WEIGHT_EPS]
    held.sort(key=lambda kv: (-kv[1], kv[0]))
    return [{"ticker": t, "weight": w} for t, w in held]


def build_history(rebalance_weights: pd.DataFrame) -> list[dict]:
    """Per-rebalance holdings with entered/exited diffs vs the previous rebalance."""
    out: list[dict] = []
    prev: set[str] = set()
    for date in rebalance_weights.index:
        row = rebalance_weights.loc[date]
        holdings = _holdings(row)
        names = {h["ticker"] for h in holdings}
        out.append({
            "date": pd.Timestamp(date).date().isoformat(),
            "holdings": holdings,
            "entered": sorted(names - prev),
            "exited": sorted(prev - names),
        })
        prev = names
    return out


def build_current(rebalance_weights: pd.DataFrame) -> dict:
    """Latest rebalance holdings (what to hold now)."""
    if rebalance_weights.empty:
        return {"as_of": None, "holdings": []}
    last = rebalance_weights.index[-1]
    return {"as_of": pd.Timestamp(last).date().isoformat(), "holdings": _holdings(rebalance_weights.loc[last])}


def build_contribution(daily_weights: pd.DataFrame, asset_returns: pd.DataFrame) -> list[dict]:
    """Arithmetic per-ticker return attribution: sum_t w_{t-1,i} * r_{t,i}.

    Summing over tickers reproduces the arithmetic sum of daily portfolio returns,
    so each ticker's share is its honest contribution to that total.
    """
    cols = list(daily_weights.columns)
    rets = asset_returns.reindex(columns=cols).reindex(index=daily_weights.index).fillna(0.0)
    contrib = (daily_weights.shift(1).fillna(0.0) * rets).sum(axis=0)
    last_w = daily_weights.iloc[-1] if len(daily_weights) else pd.Series(0.0, index=cols)
    rows = [
        {"ticker": str(t), "contribution": float(contrib[t]), "last_weight": float(last_w.get(t, 0.0))}
        for t in cols
        if abs(float(contrib[t])) > WEIGHT_EPS or float(last_w.get(t, 0.0)) > WEIGHT_EPS
    ]
    rows.sort(key=lambda r: -r["contribution"])
    return rows


def build_series(
    returns_after: pd.Series, returns_gross: pd.Series, benchmarks: dict[str, pd.Series]
) -> pd.DataFrame:
    """date + after-tax/gross returns & equity, aligned with benchmark returns & equity."""
    after = returns_after.dropna().astype(float)
    if after.empty:
        return pd.DataFrame()
    frame = pd.DataFrame({"ret_after_tax": after})
    frame["equity_after_tax"] = (1.0 + after).cumprod()
    gross = returns_gross.reindex(after.index).fillna(0.0).astype(float)
    frame["ret_gross"] = gross
    frame["equity_gross"] = (1.0 + gross).cumprod()
    for name, bench_ret in benchmarks.items():
        br = bench_ret.reindex(after.index).fillna(0.0).astype(float)
        frame[f"{name}_ret"] = br
        frame[f"{name}_equity"] = (1.0 + br).cumprod()
    frame.index.name = "date"
    return frame


# --- per-strategy simulation + export ---------------------------------------

def _bench_returns(benchmark: pd.DataFrame, symbol: str) -> pd.Series:
    """Daily simple returns of one benchmark column (case-insensitive match)."""
    cols = {str(c).upper(): c for c in benchmark.columns}
    col = cols.get(symbol.upper())
    if col is None:
        return pd.Series(dtype=float)
    s = benchmark[col].astype(float).sort_index()
    s.index = pd.DatetimeIndex(s.index).tz_localize(None)
    return s.pct_change(fill_method=None).fillna(0.0)


def export_strategy(
    out_dir: Path,
    *,
    config: StrategyConfig,
    sim,
    contribution: list[dict],
    benchmark: pd.DataFrame,
    benchmark_symbol: str,
    metrics_row: dict | None,
    gate_verdict: dict | None,
    extra_bench: dict[str, pd.Series] | None = None,
) -> dict:
    """Write all artifacts for one simulated strategy; return its index entry."""
    out_dir.mkdir(parents=True, exist_ok=True)
    tax = apply_br_foreign_annual_tax(sim.returns, sim.daily_weights)

    rebalance = sim.rebalance_weights
    current = build_current(rebalance)
    write_json(out_dir / "current.json", current)
    write_json(out_dir / "history.json", build_history(rebalance))
    write_json(out_dir / "contribution.json", contribution)

    benches = {benchmark_symbol.lower(): _bench_returns(benchmark, benchmark_symbol)}
    for name, ser in (extra_bench or {}).items():
        if ser is not None and not ser.empty:
            benches[name] = ser
    series = build_series(tax.returns, sim.returns, benches)
    if not series.empty:
        series.to_csv(out_dir / "series.csv")

    after_metrics = metrics_from_returns(tax.returns)
    meta = {
        "name": config.name,
        "mechanism": config.mechanism,
        "score_mode": config.score_mode,
        "lookback": config.lookback.label,
        "top_n": config.top_n,
        "rebalance_months": config.rebalance_months,
        "weight_mode": config.weight_mode,
        "absolute_filter": config.absolute_filter,
        "metrics": metrics_row or {k: after_metrics[k] for k in ("cagr", "mdd", "sharpe", "calmar")},
        "gate_verdict": gate_verdict,
        "promotion_eligible": False,
        "disclaimer": DISCLAIMER.strip(),
        "as_of": current["as_of"],
        "n_rebalances": int(len(rebalance)),
    }
    write_json(out_dir / "meta.json", meta)
    return {
        "name": config.name,
        "mechanism": config.mechanism,
        "top_n": config.top_n,
        "rebalance_months": config.rebalance_months,
        "as_of": current["as_of"],
        "cagr": float(after_metrics["cagr"]),
        "mdd": float(after_metrics["mdd"]),
        "sharpe": float(after_metrics["sharpe"]),
        "gate_pass": bool((gate_verdict or {}).get("all_pass", False)),
    }


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - thin CLI/orchestration
    args = _parse(argv)
    conf = cfg.load_config(args.universe)
    from argparse import Namespace

    load_args = Namespace(
        start=args.start, end=None, membership="none", max_symbols=None,
        cache_panels=True, refresh_cache=False,
    )
    _src, _total, result, benchmark, benchmark_symbol, start, window = run._load_panel(conf, args.universe, load_args)
    base, results_dir, _plots, _reports = run.universe_dirs(args.universe, window)
    prices = result.prices
    assets = tuple(prices.columns)
    features = conf.get("features", {})
    panel = build_panel_cache(prices)

    broad = pd.read_csv(results_dir / "broad_results.csv") if (results_dir / "broad_results.csv").exists() else pd.DataFrame()
    evo = pd.read_csv(results_dir / "evolution_results.csv") if (results_dir / "evolution_results.csv").exists() else pd.DataFrame()
    verdict = {}
    vpath = results_dir / "validate_verdict.json"
    if vpath.exists():
        import json
        verdict = json.loads(vpath.read_text(encoding="utf-8"))
    verdict_by_name = {v["name"]: v for v in verdict.get("per_config", [])}

    # extra benchmark: SPMO (momentum ETF) buy-hold returns, where available
    extra_bench = {}
    try:
        spmo = _src.fetch_symbols(("SPMO",), start=start, end=None)
        extra_bench["spmo"] = _bench_returns(spmo, "SPMO")
    except Exception as exc:  # noqa: BLE001
        print(f"[export] SPMO unavailable: {exc}")

    out_root = base / "portfolio"
    index: list[dict] = []

    # market-regime inputs for evolution strategies (once per window)
    daily = panel.daily
    daily_market_ok, monthly_market_ok = market_regime(benchmark, pd.DatetimeIndex(daily.index))
    monthly_stock_ok = stock_trend_ok(prices)

    featured = _select_featured(broad, evo, args.top)
    print(f"[export] {args.universe} {window}: exporting {len(featured)} strategies -> {out_root}")
    for kind, row in featured:
        if kind == "broad":
            config = run._config_from_row(row, assets, features)
            bundle = precompute_scores(prices, assets, config.vol_window_days, config.trend_window_days, config.lookback.months)
            sim = simulate_config(prices, bundle, config, panel=panel)
        else:  # evolution
            base_cfg = run._config_from_row(pd.Series({**row.to_dict(), "name": str(row["base_name"])}), assets, features)
            bundle = precompute_scores(prices, assets, base_cfg.vol_window_days, base_cfg.trend_window_days, base_cfg.lookback.months)
            config = StrategyConfig(
                name=str(row["name"]), universe=args.universe, assets=assets, top_n=base_cfg.top_n,
                rebalance_months=base_cfg.rebalance_months, rebalance_offset=base_cfg.rebalance_offset,
                score_mode=base_cfg.score_mode, lookback=base_cfg.lookback, weight_mode=base_cfg.weight_mode,
                absolute_filter=base_cfg.absolute_filter, vol_window_days=base_cfg.vol_window_days,
                trend_window_days=base_cfg.trend_window_days,
            )
            sim = simulate_evolved(
                prices, bundle, config, str(row.get("overlay", "none")), str(row.get("offset_mode", "fixed")),
                daily_market_ok, monthly_market_ok, monthly_stock_ok, panel=panel,
            )
        if sim.returns.empty:
            continue
        contribution = build_contribution(sim.daily_weights, panel.asset_returns)
        metrics_row = {c: (float(row[c]) if c in row and pd.notna(row[c]) else None)
                       for c in ("after_tax_cagr", "after_tax_mdd", "after_tax_sharpe", "after_tax_calmar",
                                 "rolling_rel_score", "annual_turnover", "spy_cagr", "excess_cagr")}
        entry = export_strategy(
            out_root / config.name, config=config, sim=sim, contribution=contribution, benchmark=benchmark,
            benchmark_symbol=benchmark_symbol, metrics_row=metrics_row,
            gate_verdict=verdict_by_name.get(config.name), extra_bench=extra_bench,
        )
        entry["kind"] = kind
        index.append(entry)

    write_json(out_root / "index.json", {
        "universe": args.universe, "window": window, "benchmark": benchmark_symbol,
        "strategies": index, "disclaimer": DISCLAIMER.strip(),
    })
    print(f"[export] wrote {len(index)} strategies -> {out_root / 'index.json'}")
    return 0


def _select_featured(broad: pd.DataFrame, evo: pd.DataFrame, top: int) -> list[tuple[str, pd.Series]]:
    """Headline broad picks by rolling dominance + the evolution finalists."""
    out: list[tuple[str, pd.Series]] = []
    seen: set[str] = set()
    if not broad.empty and "rolling_rel_score" in broad.columns:
        for _, row in broad.nlargest(top, "rolling_rel_score").iterrows():
            if row["name"] not in seen:
                out.append(("broad", row)); seen.add(row["name"])
    if not evo.empty and "rolling_rel_score" in evo.columns:
        for _, row in evo.nlargest(min(top, 8), "rolling_rel_score").iterrows():
            if row["name"] not in seen:
                out.append(("evolution", row)); seen.add(row["name"])
    return out


def _parse(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export per-strategy portfolio artifacts for the web-app")
    p.add_argument("--universe", default="us_stocks")
    p.add_argument("--start", default="1990-01-01")
    p.add_argument("--top", type=int, default=12, help="Headline broad strategies (by rolling_rel_score) to export")
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
