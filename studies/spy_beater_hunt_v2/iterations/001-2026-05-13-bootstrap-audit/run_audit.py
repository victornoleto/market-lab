"""Bootstrap audit for spy_beater_hunt_v2 iteration 001.

This iteration deliberately tests zero strategy configs. It only checks whether
the data and validation stack are ready for later pre-registered hypotheses.
Trial-accounting and hard-gate discipline follow AFML's backtest overfit rules
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`, and the audit
separation principle `[advances_fin_ml, p.276]`.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from market_lab.backtest.metrics.performance import cagr, max_drawdown, sharpe, sortino
from market_lab.backtest.data.testfolio_loader import load_testfolio_series


ITERATION = "001-2026-05-13-bootstrap-audit"
OUT_DIR = Path(__file__).resolve().parent

DATA_TICKERS = [
    "SPYSIM",
    "QQQSIM",
    "QLDSIM",
    "TQQQSIM",
    "ZROZSIM",
    "CASHX",
    "GLDSIM",
    "NTSX",
    "GDE",
    "RSST",
    "KMLMSIM",
]

VALIDATION_MODULES = {
    "pbo": "market_lab.backtest.validation.pbo",
    "dsr": "market_lab.backtest.validation.dsr",
    "walk_forward": "market_lab.backtest.validation.walk_forward",
    "bootstrap": "market_lab.backtest.validation.bootstrap",
    "cpcv": "market_lab.backtest.validation.cpcv",
    "permutation": "market_lab.backtest.validation.permutation",
}


def _load_inventory() -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    for ticker in DATA_TICKERS:
        try:
            series = load_testfolio_series(ticker).dropna().sort_index()
        except Exception as exc:  # noqa: BLE001 - inventory should capture blockers.
            inventory[ticker] = {"available": False, "error": str(exc)}
            continue
        returns = series.pct_change().dropna()
        inventory[ticker] = {
            "available": True,
            "start": str(series.index.min().date()),
            "end": str(series.index.max().date()),
            "n_prices": int(len(series)),
            "n_returns": int(len(returns)),
            "cagr": cagr(series),
            "mdd": max_drawdown(series),
            "sharpe": sharpe(returns),
            "sortino": sortino(returns),
        }
    return inventory


def _rolling_win_rates(series: pd.Series, benchmark: pd.Series) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    aligned = pd.concat([series.rename("candidate"), benchmark.rename("benchmark")], axis=1).dropna()
    for years in (3, 5, 10):
        window = years * 252
        if len(aligned) <= window:
            out[f"rolling_{years}y_cagr_win_rate_vs_spy"] = None
            continue
        cand = aligned["candidate"].rolling(window).apply(_window_cagr, raw=False).dropna()
        spy = aligned["benchmark"].rolling(window).apply(_window_cagr, raw=False).dropna()
        joined = pd.concat([cand.rename("candidate"), spy.rename("spy")], axis=1).dropna()
        out[f"rolling_{years}y_cagr_win_rate_vs_spy"] = float((joined["candidate"] > joined["spy"]).mean())
    return out


def _window_cagr(window: pd.Series) -> float:
    if len(window) < 2 or float(window.iloc[0]) <= 0:
        return np.nan
    return float((float(window.iloc[-1]) / float(window.iloc[0])) ** (252 / (len(window) - 1)) - 1)


def _module_inventory() -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    for name, module_path in VALIDATION_MODULES.items():
        try:
            module = importlib.import_module(module_path)
        except Exception as exc:  # noqa: BLE001 - inventory should capture blockers.
            inventory[name] = {"available": False, "module": module_path, "error": str(exc)}
            continue
        inventory[name] = {
            "available": True,
            "module": module_path,
            "public_callables": sorted(k for k, v in vars(module).items() if callable(v) and not k.startswith("_")),
        }
    return inventory


def main() -> None:
    data_inventory = _load_inventory()
    module_inventory = _module_inventory()

    spy_info = data_inventory.get("SPYSIM", {})
    data_blocked = not spy_info.get("available", False)
    spy_benchmark: dict[str, Any] = {}

    if not data_blocked:
        spy = load_testfolio_series("SPYSIM").dropna().sort_index()
        spy_returns = spy.pct_change().dropna()
        spy_benchmark = {
            "ticker": "SPYSIM",
            "source": "data/testfolio/cache/history.parquet",
            "start": str(spy.index.min().date()),
            "end": str(spy.index.max().date()),
            "n_prices": int(len(spy)),
            "cagr": cagr(spy),
            "mdd": max_drawdown(spy),
            "sharpe": sharpe(spy_returns),
            "sortino": sortino(spy_returns),
            "terminal_equity": float(spy.iloc[-1] / spy.iloc[0]),
        }
        spy_benchmark.update(_rolling_win_rates(spy, spy))

    artifacts = [
        "PRE_REG.md",
        "run_audit.py",
        "RESULTS.json",
        "audit_inventory.json",
    ]
    audit = {
        "iteration": ITERATION,
        "data_inventory": data_inventory,
        "validation_modules": module_inventory,
        "prior_dead_end_clusters_to_avoid": [
            "technical vote local grids/GA without diversity: repeated DSR/PBO failures",
            "modern-window-only Tiingo QQQ/LETF leads without 1986+ support",
            "same-family parameter sensitivity around iter030 after PBO/DSR fail",
        ],
        "recommended_next_hypotheses": [
            "Small static factor/diversifier stack re-baseline vs SPY using pre-fixed weights and HRP diagnostics `[advances_fin_ml, p.302-308]`.",
            "Single canonical Gayed LRS baseline as control only, not a grid `[leverage_for_the_long_run, p.13, p.16, p.21]`.",
            "Cross-asset trend/carry sleeve with one fixed Carver-style forecast family and strict trial budget `[systematic_trading, ch.3]`.",
        ],
    }
    (OUT_DIR / "audit_inventory.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")

    gates = {
        "pbo": {"computed": False, "reason": "no strategy panel; n_trials=0"},
        "dsr": {"computed": False, "reason": "no candidate returns; cumulative_n_trials remains 0"},
        "walk_forward": {"computed": False, "reason": "infrastructure audit only"},
        "oos": {"computed": False, "reason": "infrastructure audit only"},
        "fwd": {"computed": False, "reason": "infrastructure audit only"},
        "bootstrap": {"computed": False, "reason": "infrastructure audit only"},
        "cross_lib": {"computed": False, "reason": "infrastructure audit only"},
    }
    missing_modules = [name for name, info in module_inventory.items() if not info.get("available")]
    kill_switches: list[str] = []
    if data_blocked:
        kill_switches.append("SPYSIM benchmark unavailable")
    if missing_modules:
        kill_switches.append(f"validation modules unavailable: {', '.join(missing_modules)}")

    results = {
        "iteration": ITERATION,
        "status": "data_blocked" if data_blocked else "infrastructure_only",
        "pre_registered": True,
        "n_trials": 0,
        "best_config": None,
        "beats_spy_cagr": False,
        "winner": False,
        "metrics": {
            "data_sources_available": sum(1 for info in data_inventory.values() if info.get("available")),
            "data_sources_checked": len(data_inventory),
            "validation_modules_available": sum(1 for info in module_inventory.values() if info.get("available")),
            "validation_modules_checked": len(module_inventory),
        },
        "spy_benchmark": spy_benchmark,
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": artifacts,
        "notes": "Bootstrap/audit only. No strategy configs were tested and no winner can be declared.",
    }
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
