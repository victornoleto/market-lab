#!/usr/bin/env python3
"""Declared test: moving-average ENTRY filter + per-stock intra-period EXIT on the two
headline us_stocks families. Targets the undiversifiable ~-58% MDD wall with a *new
mechanism* (not parameter tuning), on a small declared set (not a grid search).

- ENTRY: only buy a top-k name whose price is above its MA at the rebalance (reuses the
  existing ``stock_sma100`` overlay, generalized window/kind).
- EXIT (new): while holding, gate each stock by a short daily MA —
    * ``gate``: weight -> 0 on days price < MA; re-enters if it recovers (de-risk).
    * ``stop``: once below MA within a holding period, stay in cash until the next rebalance.

Judged on risk-adjusted, net-of-cost terms (MDD, Sharpe, Calmar, turnover, CAGR@50bps) —
not CAGR. Research-only, ``promotion_eligible=false``; survivorship still caps absolutes.
Citations: trend gate `[stocks_on_the_move, p.66-67, p.98-99]`; no look-ahead `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import argparse
import sys
from argparse import Namespace
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
for _c in (REPO_ROOT, REPO_ROOT / "src"):
    if str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from studies.momentum_v2 import config as cfg  # noqa: E402
from studies.momentum_v2 import run  # noqa: E402
from studies.momentum_v2.core import (  # noqa: E402
    LookbackProfile,
    PanelCache,
    StrategyConfig,
    _returns_from_daily_weights,
    apply_br_foreign_annual_tax,
    benchmark_returns_for,
    build_panel_cache,
    daily_weights_from_monthly,
    metrics_from_returns,
    monthly_weights,
    precompute_scores,
    turnover_diagnostics,
)
from studies.momentum_v2.dominance import rolling_relative_equity_metrics  # noqa: E402
from studies.momentum_v2.overlays import (  # noqa: E402
    monthly_weights_with_overlay,
    stock_above_ma,
    stock_above_ma_monthly,
)

# (mechanism, lookback months, label, top_n) — the two headline families, reb=2, equal-weight.
FAMILIES = [
    ("clenow_trend", (1, 3, 6, 12), "lb1_3_6_12", 10),
    ("raw_13612", (6,), "lb6", 15),
]

# Declared variant set (label, entry, exit, exit_mode). entry/exit = {"window","kind"} or None.
VARIANTS = [
    ("baseline", None, None, None),
    ("entry SMA200", {"window": 200, "kind": "sma"}, None, None),
    ("entry EMA200", {"window": 200, "kind": "ema"}, None, None),
    ("exit SMA20 gate", None, {"window": 20, "kind": "sma"}, "gate"),
    ("exit SMA50 gate", None, {"window": 50, "kind": "sma"}, "gate"),
    ("exit EMA20 gate", None, {"window": 20, "kind": "ema"}, "gate"),
    ("exit EMA50 gate", None, {"window": 50, "kind": "ema"}, "gate"),
    ("exit SMA20 stop", None, {"window": 20, "kind": "sma"}, "stop"),
    ("exit SMA50 stop", None, {"window": 50, "kind": "sma"}, "stop"),
    ("exit EMA20 stop", None, {"window": 20, "kind": "ema"}, "stop"),
    ("exit EMA50 stop", None, {"window": 50, "kind": "ema"}, "stop"),
    ("both SMA200+exit20gate", {"window": 200, "kind": "sma"}, {"window": 20, "kind": "sma"}, "gate"),
    ("both SMA200+exit50gate", {"window": 200, "kind": "sma"}, {"window": 50, "kind": "sma"}, "gate"),
]


def _apply_exit(dw: pd.DataFrame, ok: pd.DataFrame, monthly_index: pd.Index, mode: str) -> pd.DataFrame:
    """Apply the per-stock intra-period exit to daily weights.

    ``gate``: zero a stock's weight on any day it is below its MA (re-enters on recovery).
    ``stop``: once below its MA within a holding segment, stay at 0 until the next rebalance.
    """
    ok = ok.reindex(index=dw.index, columns=dw.columns).fillna(False)
    if mode == "gate":
        return dw.where(ok, 0.0)
    if mode == "stop":
        seg = pd.Series(range(len(monthly_index)), index=monthly_index).reindex(dw.index, method="ffill")
        alive = ok.astype(int).groupby(seg).cumprod().reindex(dw.index).fillna(0).astype(bool)
        return dw.where(alive, 0.0)
    raise ValueError(f"exit_mode must be 'gate' or 'stop', got {mode!r}")


def simulate_ma_variant(
    prices: pd.DataFrame,
    bundle,
    config: StrategyConfig,
    panel: PanelCache,
    benchmark: pd.DataFrame,
    benchmark_symbol: str,
    *,
    entry: dict | None = None,
    exit: dict | None = None,
    exit_mode: str = "gate",
    cost_bps: float = 0.0,
) -> dict | None:
    """One MA-overlay variant; returns after-tax metrics + turnover (None if empty)."""
    daily = panel.daily
    if entry is None:
        monthly = monthly_weights(bundle, config)
    else:
        mok = stock_above_ma_monthly(prices, entry["window"], entry["kind"])
        market_ok = pd.Series(True, index=bundle.monthly_prices.index)  # unused by stock filter
        monthly = monthly_weights_with_overlay(
            bundle, config, "stock_sma100", monthly_market_ok=market_ok, monthly_stock_ok=mok
        )
    if monthly.empty:
        return None

    dw = daily_weights_from_monthly(daily, monthly)
    if exit is not None:
        dw = _apply_exit(dw, stock_above_ma(prices, exit["window"], exit["kind"]), monthly.index, exit_mode)

    returns = _returns_from_daily_weights(daily, dw, config.name, asset_returns=panel.asset_returns, cost_bps=cost_bps)
    if returns.empty:
        return None
    dw = dw.loc[returns.index]
    changed = dw.diff().abs().sum(axis=1) > 1e-12
    if len(changed):
        changed.iloc[0] = dw.iloc[0].sum() > 1e-12
    turn = turnover_diagnostics(dw.loc[changed], returns.index)
    tax = apply_br_foreign_annual_tax(returns, dw)
    m = metrics_from_returns(tax.returns)
    strat, benchr = benchmark_returns_for(tax.returns, benchmark, benchmark_symbol)
    rr = float("nan")
    if not strat.empty:
        rr = rolling_relative_equity_metrics(strat, benchr).get("rolling_rel_score", float("nan"))
    return {
        "cagr": float(m["cagr"]), "mdd": float(m["mdd"]), "sharpe": float(m["sharpe"]),
        "calmar": float(m["calmar"]), "rolling_rel": float(rr), "turnover": float(turn["annual_turnover"]),
    }


def _load(universe: str, start: str):
    conf = cfg.load_config(universe)
    la = Namespace(start=start, end=None, membership="none", max_symbols=None, cache_panels=True, refresh_cache=False)
    _s, _t, result, bench, bsym, _st, window = run._load_panel(conf, universe, la)
    return result.prices, build_panel_cache(result.prices), bench, bsym, window


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="MA entry-filter + intra-period exit test on the two families")
    p.add_argument("--universe", default="us_stocks")
    p.add_argument("--starts", default="1990-01-01,2000-01-01")
    p.add_argument("--cost-bps", type=float, default=50.0)
    args = p.parse_args(argv)

    for start in [s.strip() for s in args.starts.split(",") if s.strip()]:
        prices, panel, bench, bsym, window = _load(args.universe, start)
        assets = tuple(prices.columns)
        for mech, months, lbl, top_n in FAMILIES:
            bundle = precompute_scores(prices, assets, 126, 126, months)
            base = StrategyConfig(name=f"{mech}_{lbl}", universe=args.universe, assets=assets, top_n=top_n,
                                  rebalance_months=2, rebalance_offset=0, score_mode=mech,
                                  lookback=LookbackProfile(lbl, months), weight_mode="equal")
            print(f"\n================ {args.universe} {window} — {mech}/{lbl} top{top_n} reb2 ================")
            print(f"  {'variante':<24}{'CAGR':>8}{'MDD':>8}{'Sharpe':>8}{'Calmar':>8}{'rollRel':>9}{'turn':>7}{'CAGR@'+str(int(args.cost_bps)):>9}")
            for label, entry, exit, mode in VARIANTS:
                g = simulate_ma_variant(prices, bundle, base, panel, bench, bsym, entry=entry, exit=exit, exit_mode=mode or "gate")
                n = simulate_ma_variant(prices, bundle, base, panel, bench, bsym, entry=entry, exit=exit, exit_mode=mode or "gate", cost_bps=args.cost_bps)
                if g is None:
                    print(f"  {label:<24}  (vazio)"); continue
                print(f"  {label:<24}{g['cagr']:>8.1%}{g['mdd']:>8.1%}{g['sharpe']:>8.2f}{g['calmar']:>8.2f}"
                      f"{g['rolling_rel']:>9.3f}{g['turnover']:>7.2f}{(n['cagr'] if n else float('nan')):>9.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
