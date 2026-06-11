#!/usr/bin/env python3
"""s05 — ablation battery: what each sleeve buys you, plus LETF/HFEA baselines.

All configs monthly-rebalanced (HFEA also has a quarterly sensitivity row —
the canonical HFEA convention). Three tables:

- ``tables/ablations_primary.csv`` — primary window (2000+), daily configs
  without BTC/RSSY dependencies.
- ``tables/ablations_btc_window.csv`` — ALL daily configs recomputed on the
  BTC-bound window (2010-07-20+) so RSSX rows compare apples-to-apples.
- ``tables/ablations_monthly_rssy.csv`` — MONTHLY-frequency table (sqrt(12)
  Sharpe, monthly MDD) for every member, the only place RSSY appears
  (monthly-native carry proxy; daily mixing would fabricate vol).

Also exports ``series/portfolio_equity_primary.parquet`` (daily equity curves
of headline configs) for s07 figures.

Capital-efficiency framing: DIY-SSO replicates the core's look-through with
explicit LETF leverage at lower gross notional — the gap narrates what
stacking buys `[leverage_for_the_long_run, p.13]`, `[risk_parity, ch.5]`.
No config here is a recommendation; multiple-testing discipline applies
`[testing_tuning, p.327-335]`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402
from studies.return_stacked_core.discussion import engine  # noqa: E402

# (id, label, weights, frequency, needs_btc)
CONFIGS: list[tuple[str, str, dict[str, float], str, bool]] = [
    ("A0", "CORE 35/40/25", {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}, "M", False),
    ("A1", "Equal-weight", {"GDESIM": 1 / 3, "RSSTSIM": 1 / 3, "ZROZSIM": 1 / 3}, "M", False),
    ("A2", "No-ZROZ renorm", {"GDESIM": 0.467, "RSSTSIM": 0.533}, "M", False),
    ("A3", "ZROZ->cash", {"GDESIM": 0.35, "RSSTSIM": 0.40, "CASHX": 0.25}, "M", False),
    ("A4", "NTSX swap", {"NTSXSIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}, "M", False),
    ("A5", "DIY-SSO", {"SSOSIM": 0.35, "GLDSIM": 0.20, "MFBLEND": 0.25, "ZROZSIM": 0.20}, "M", False),
    ("A6", "100% SSO", {"SSOSIM": 1.0}, "M", False),
    ("A7", "100% UPRO", {"UPROSIM": 1.0}, "M", False),
    ("A8", "60/40 SSO/ZROZ", {"SSOSIM": 0.60, "ZROZSIM": 0.40}, "M", False),
    ("A9", "HFEA 55/45 (monthly)", {"UPROSIM": 0.55, "TMFSIM_D": 0.45}, "M", False),
    ("A9q", "HFEA 55/45 (quarterly)", {"UPROSIM": 0.55, "TMFSIM_D": 0.45}, "Q", False),
    ("A10", "RSSX swap", {"RSSXSIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}, "M", True),
    ("A11", "RSSX tilt", {"GDESIM": 0.175, "RSSXSIM": 0.175, "RSSTSIM": 0.40, "ZROZSIM": 0.25}, "M", True),
    ("A14", "100% SPY", {"SPYSIM": 1.0}, "M", False),
    ("A15", "100% GDE", {"GDESIM": 1.0}, "M", False),
    ("A16", "100% RSST", {"RSSTSIM": 1.0}, "M", False),
    ("A17", "100% NTSX", {"NTSXSIM": 1.0}, "M", False),
]

RSSY_CONFIGS = [
    ("A0", "CORE 35/40/25", {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}),
    ("A12", "RSSY swap", {"GDESIM": 0.35, "RSSYSIM": 0.40, "ZROZSIM": 0.25}),
    ("A13", "RSSY split", {"GDESIM": 0.35, "RSSTSIM": 0.20, "RSSYSIM": 0.20, "ZROZSIM": 0.25}),
    ("A14", "100% SPY", {"SPYSIM": 1.0}),
]

EQUITY_EXPORT = ["A0", "A4", "A5", "A9", "A2", "A8", "A14", "A6", "A7", "A15", "A16", "A17"]


def run_battery(daily: pd.DataFrame, window_label: str, start: str | None) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    data = daily.loc[start:] if start else daily
    rows = []
    curves: dict[str, pd.Series] = {}
    base: dict | None = None
    for cfg_id, label, weights, freq, needs_btc in CONFIGS:
        if needs_btc and start is None:
            continue  # RSSX rows only on the BTC window
        equity = engine.rebalanced_equity(data, weights, frequency=freq)
        m = engine.compute_metrics(equity)
        row = {"id": cfg_id, "config": label, "window": window_label, **m}
        if cfg_id == "A0":
            base = m
        rows.append(row)
        curves[cfg_id] = equity
    frame = pd.DataFrame(rows)
    assert base is not None
    for key in ("cagr", "mdd", "sharpe"):
        frame[f"d_{key}_vs_core"] = frame[key] - base[key]
    return frame, curves


def main() -> int:
    primary = pd.read_parquet(dd.SERIES_DIR / "primary_returns.parquet")
    proxies = pd.read_parquet(dd.SERIES_DIR / "proxy_returns.parquet")
    daily = primary.join(proxies)
    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)

    prim, curves = run_battery(daily, "primary 2000+", None)
    prim.to_csv(dd.TABLES_DIR / "ablations_primary.csv", index=False)

    btc_start = str(daily["RSSXSIM"].dropna().index[0].date())
    btc, _ = run_battery(daily, f"btc {btc_start}+", btc_start)
    btc.to_csv(dd.TABLES_DIR / "ablations_btc_window.csv", index=False)

    # Monthly-frequency RSSY table (the only table RSSY may appear in).
    rssy_path = dd.SERIES_DIR / "rssy_monthly.parquet"
    if rssy_path.exists():
        monthly = pd.read_parquet(rssy_path)
        rows = []
        base = None
        for cfg_id, label, weights in RSSY_CONFIGS:
            cols = list(weights)
            sub = monthly[cols].dropna(how="any")
            port = sum(w * sub[c] for c, w in weights.items())
            m = engine.compute_metrics(
                engine.equity_from_returns(port), periods_per_year=12
            )
            if cfg_id == "A0":
                base = m
            rows.append({"id": cfg_id, "config": label,
                         "window": "monthly rssy", **m})
        frame = pd.DataFrame(rows)
        for key in ("cagr", "mdd", "sharpe"):
            frame[f"d_{key}_vs_core"] = frame[key] - base[key]
        frame.to_csv(dd.TABLES_DIR / "ablations_monthly_rssy.csv", index=False)
    else:
        print("WARNING: rssy_monthly missing — RSSY ablation table skipped.",
              file=sys.stderr)

    # Export headline equity curves for figures.
    export = pd.DataFrame(
        {cfg_id: curves[cfg_id] for cfg_id in EQUITY_EXPORT if cfg_id in curves}
    )
    labels = {cfg_id: label for cfg_id, label, *_ in CONFIGS}
    export.columns = [f"{c}|{labels[c]}" for c in export.columns]
    export.to_parquet(dd.SERIES_DIR / "portfolio_equity_primary.parquet")

    cols = ["id", "config", "cagr", "mdd", "sharpe", "d_sharpe_vs_core"]
    print(prim[cols].round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
