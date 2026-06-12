#!/usr/bin/env python3
"""s08 — OPTIONAL network step: CORE vs unlevered "safe" portfolios (testfol.io).

User-chartered comparison (2026-06-11): the RSC-US core against five classic
low-drawdown unlevered portfolios (Golden Butterfly, Permanent Portfolio,
All Weather, a VUG/VBR/TLT/GLD/KMLM barbell, and a REIT/BND/GLD mix), all
fetched from the same Testfol.io engine, on the common window (binds at
DBMFSIM 2000-01-03). Includes the two decisive framing tests:

1. **Dilution test** — CORE blended with T-bills (local CASHX) until it
   matches each safe portfolio's MDD: same-risk CAGR comparison.
2. **Leverage test** — the best safe recipe (B1) levered to CORE's gross
   (x1.65) with the repo financing convention (CASHX+2%/yr): same-leverage
   comparison `[leverage_for_the_long_run, p.13]`.

Anonymous API calls (<= 6 backtests per request — the API rejects larger
batches). Outputs are committed so the offline pipeline never needs this step:

- ``series/safe_portfolios_equity.csv`` — daily curves, common window.
- ``tables/safe_portfolios_metrics.csv`` — full metrics + dilution +
  levered-B1 rows + episode returns.

Caveats recorded with the data: simulated sims; the 2000+ window includes the
gold decade (every mix here holds 16-25% gold); B1 is itself a
backtest-discovered allocation, so its Sharpe carries selection bias
`[advances_fin_ml, p.208-211]`; yearly rebalance for the safe mixes (their
convention), monthly for CORE (ours).
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.return_stacked_core.discussion import discussion_data as dd  # noqa: E402
from studies.return_stacked_core.discussion import engine  # noqa: E402

ENDPOINT = "https://testfol.io/api/backtest"
COMMON_START = "2000-01-03"

SAFE_PORTS = {
    "B1 VUG/VBR/TLT/GLD/KMLM": {"VUGSIM": 21, "VBRSIM": 21, "TLTSIM": 26,
                                "GLDSIM": 16, "KMLMSIM": 10, "CASHX": 6},
    "B2 Golden Butterfly": {"VTISIM": 20, "VBRSIM": 20, "SHYSIM": 20,
                            "TLTSIM": 20, "GLDSIM": 20},
    "B3 Permanent Portfolio": {"SPYSIM": 25, "TLTSIM": 25, "CASHX": 25,
                               "GLDSIM": 25},
    "B4 All Weather": {"VTISIM": 30, "TLTSIM": 40, "IEFSIM": 15,
                       "GSGSIM": 7.5, "GLDSIM": 7.5},
    "B5 REIT/BND/GLD mix": {"VVSIM": 13, "VEASIM": 8, "VWOSIM": 4,
                            "REITSIM": 25, "BNDSIM": 25, "GLDSIM": 25},
}
CORE_FLAT = {"GDESIM": 35, "SPYSIM": 40, "DBMFSIM": 28, "KMLMSIM": 12,
             "ZROZSIM": 25, "CASHX?E=-2": -40}
B1_LEV_165 = {"VUGSIM": 34.65, "VBRSIM": 34.65, "TLTSIM": 42.9, "GLDSIM": 26.4,
              "KMLMSIM": 16.5, "CASHX": 9.9, "CASHX?E=-2": -65.0}

EPISODES = [("GFC", "2007-10-09", "2009-03-09"),
            ("Covid crash", "2020-02-19", "2020-03-23"),
            ("Inflation/rates shock", "2022-01-03", "2022-10-14"),
            ("AI bull", "2022-10-14", None)]
DILUTION_FRACTIONS = [1.0, 0.75, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40]


def _bt(alloc: dict, freq: str) -> dict:
    return {"invest_dividends": True, "rebalance_freq": freq,
            "rebalance_offset": 0, "allocation": alloc,
            "drag": 0, "absolute_dev": 0, "relative_dev": 0}


def _post(backtests: list[dict]) -> dict:
    payload = {
        "start_date": "1800-01-01", "end_date": "2100-01-01", "start_val": 10000,
        "adj_inflation": False, "target_currency": "USD", "cashflow": 0,
        "cashflow_freq": "Yearly", "cashflow_offset": 0,
        "match_first_portfolio_income_cashflows": False, "one_time_cashflows": [],
        "rolling_window": 60, "withdrawal_surface_include": False,
        "withdrawal_surface_projection": "NONE",
        "withdrawal_surface_projection_min_years": 10,
        "withdrawal_surface_start_years": 5, "withdrawal_surface_end_years": 50,
        "withdrawal_surface_step_years": 1, "backtests": backtests,
        "cashflow_legs": [],
    }
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={"content-type": "application/json",
                 "Referer": "https://testfol.io/",
                 "User-Agent": "market-lab/discussion-s08"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        out = json.loads(resp.read())
    if out.get("errors"):
        raise RuntimeError(f"testfol errors: {out['errors']}")
    return out


def _curves(resp: dict, labels: list[str]) -> pd.DataFrame:
    history = resp["charts"]["history"]
    idx = pd.DatetimeIndex(pd.to_datetime(history[0], unit="s", utc=True).tz_convert(None))
    return pd.DataFrame({
        lab: pd.to_numeric(pd.Series(vals, index=idx), errors="coerce")
        for lab, vals in zip(labels, history[1:])
    })


def main() -> int:
    safe = _curves(_post([_bt(a, "Yearly") for a in SAFE_PORTS.values()]),
                   list(SAFE_PORTS))
    ours = _curves(_post([_bt(CORE_FLAT, "Monthly"), _bt({"SPYSIM": 100}, "Yearly"),
                          _bt(B1_LEV_165, "Yearly")]),
                   ["CORE 35/40/25", "100% SPY", "B1 x1.65 (cash+2% financing)"])
    df = safe.join(ours, how="inner").dropna().loc[COMMON_START:]

    dd.SERIES_DIR.mkdir(parents=True, exist_ok=True)
    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(dd.SERIES_DIR / "safe_portfolios_equity.csv", index_label="date")

    rows = []
    for col in df.columns:
        m = engine.compute_metrics(df[col])
        row = {"portfolio": col, "kind": "headline", **m}
        for name, a, b in EPISODES:
            w = df[col].loc[a:b]
            row[f"ep_{name}"] = float(w.iloc[-1] / w.iloc[0] - 1.0)
        rows.append(row)

    # Dilution test: CORE x f + (1-f) T-bills (local CASHX returns).
    cash = (pd.read_parquet(dd.CACHE_PARQUET, columns=["CASHX"])["CASHX"]
            .pct_change().reindex(df.index).fillna(0.0))
    core_r = df["CORE 35/40/25"].pct_change().dropna()
    for f in DILUTION_FRACTIONS:
        r = f * core_r + (1 - f) * cash.loc[core_r.index]
        m = engine.compute_metrics((1 + r).cumprod())
        rows.append({"portfolio": f"CORE {f:.0%} + T-bills {1 - f:.0%}",
                     "kind": "dilution", **m})

    frame = pd.DataFrame(rows)
    frame.to_csv(dd.TABLES_DIR / "safe_portfolios_metrics.csv", index=False)

    head = frame[frame["kind"] == "headline"]
    print(f"common window {df.index[0].date()}..{df.index[-1].date()}")
    print(head[["portfolio", "cagr", "mdd", "vol", "sharpe", "terminal"]]
          .round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
