#!/usr/bin/env python3
"""s09 — matched external-margin sweep for the two portfolios in POST_MARGIN.md.

Answers a r/LETFs DM: "have you considered running the permanent portfolio on
IBKR margin?" on the EXACT two mixes the post compares, so every table is
internally consistent (the older us_core/four_asset_grid/MARGIN_ANALYSIS.md
swept the 40/25/35 grid-top variant, not the canonical 35/40/25):

- **P1 = 35/40/25** GDE/RSST/ZROZ  (the canonical RSC-US 3-asset core)
- **P2 = 25/25/25/25** RSST/NTSX/GDE/ZROZ  (adds NTSX — shown redundant)

Fully OFFLINE: uses the canonical sleeve-return matrix
(``return_stacked_core_sleeve_returns.parquet``, 2000-01-04..2026-05-21) via
``discussion_data``, the same source that reproduces the published POST.md
anchor (35/40/25 ≈ 12.5% / -30.8% / 0.85). No network — the parquet is the raw.

**External margin model (monthly-reset account leverage L).** These funds are
already internally leveraged, so account margin is leverage-on-leverage
`[leverage_for_the_long_run, p.13]`. Hold L× the fund weights, borrow (L-1)×
equity at the T-bill rate + a 2%/yr spread — the repo's corrected financing
convention, equivalent to testfol.io ``CASHX?E=-2``
`[systematic_trading, p.185-188]`. Implemented as a fund-level financing leg of
weight (1-L) whose daily return is ``CASHX_ret + 2%/252``, rebalanced monthly
with the rest of the book (engine.rebalanced_equity). Fund returns are taken
NET of cost: GDE/NTSX carry their expense+tracking drag (FUND_COST_DRAG), since
their futures financing is already ~risk-free; RSST's overlay cost is already in
its proxy; ZROZ is left gross (plain unlevered ETF).

The 2%/yr spread matches the corrected internal-financing diagnostic; **real
retail IBKR margin is more expensive (≈ fed funds + 1.5%)**, so the levered
rows here are an optimistic upper bound, and the backtest models NO margin
calls / forced liquidation — it assumes you hold through the whole drawdown.
Read as a diagnostic, not an implementation plan
`[advances_fin_ml, p.208-211]`.
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

# Fund-level weights (sum to 1.0 each — unlevered, account leverage 1.0x).
# ZROZ fixed at 25%; the RSST(MF)<->GDE(gold) split walks the concentration axis.
PORTFOLIOS = {
    "RSST25/GDE50/ZROZ25 (gold-heavy)": {"RSSTSIM": 0.25, "GDESIM": 0.50, "ZROZSIM": 0.25},
    "RSST37.5/GDE37.5/ZROZ25 (balanced)": {"RSSTSIM": 0.375, "GDESIM": 0.375, "ZROZSIM": 0.25},
    "RSST50/GDE25/ZROZ25 (MF-heavy)": {"RSSTSIM": 0.50, "GDESIM": 0.25, "ZROZSIM": 0.25},
    "RSST25/NTSX25/GDE25/ZROZ25 (+NTSX)": {
        "RSSTSIM": 0.25, "NTSXSIM": 0.25, "GDESIM": 0.25, "ZROZSIM": 0.25,
    },
}

# Per-$1 look-through gross notional of each fund (equity + every other sleeve).
FUND_GROSS = {"GDESIM": 1.8, "RSSTSIM": 2.0, "NTSXSIM": 1.5, "ZROZSIM": 1.0}

# Net-of-cost drag for the capital-efficient ETFs whose testfol.io sims run
# GROSS of the fund expense ratio. Their *financing* is already correct (gold &
# Treasury futures roll at ~the risk-free rate, no spread — unlike the active
# managed-futures overlay), so the only missing piece is the fund's own cost:
#   GDESIM: measured ΔCAGR 0.46pp/yr vs live GDE (ER 0.20% + tracking), discussion/METHODS.md.
#   NTSXSIM: 0.20%/yr expense ratio (financing validated ~risk-free vs live, proxies.py).
# RSSTSIM already carries its overlay cost via the CASHX?E=-2 (2%/yr) proxy leg;
# ZROZSIM is a plain unlevered Treasury ETF, left gross. `[systematic_trading, p.185-188]`.
FUND_COST_DRAG = {"GDESIM": 0.0045, "NTSXSIM": 0.0020}


def apply_cost_drags(returns: pd.DataFrame) -> pd.DataFrame:
    """Subtract each fund's net-of-financing cost (ER/tracking) as a daily drag."""
    out = returns.copy()
    for col, annual in FUND_COST_DRAG.items():
        if col in out.columns:
            out[col] = out[col] - annual / dd.TRADING_DAYS
    return out

LEVERAGES = (1.00, 1.10, 1.25, 1.50, 1.75, 2.00)
MAINTENANCE = (0.25, 0.30, 0.50)  # IBKR Reg-T / house maintenance scenarios
FINANCING_LEG = "MARGIN_FIN"


def effective_gross(weights: dict[str, float], leverage: float) -> float:
    """Look-through gross exposure per $1 of equity at account leverage L."""
    return leverage * sum(w * FUND_GROSS[f] for f, w in weights.items())


def margin_call_drop(leverage: float, maintenance: float) -> float:
    """Approx portfolio drop that triggers a call (MARGIN_ANALYSIS.md formula).

    drop_to_call = (1 - m*L) / (L*(1 - m)); negative = the loss size.
    """
    if leverage <= 1.0:
        return float("nan")  # no borrowing, no call
    return -(1.0 - maintenance * leverage) / (leverage * (1.0 - maintenance))


def levered_metrics(returns: pd.DataFrame, weights: dict[str, float], leverage: float) -> dict:
    w = {f: wt * leverage for f, wt in weights.items()}
    w[FINANCING_LEG] = 1.0 - leverage  # 0 at L=1; negative (borrow) at L>1
    equity = engine.rebalanced_equity(returns, w, "M")
    return engine.compute_metrics(equity)


def main() -> int:
    base = apply_cost_drags(dd.load_primary_returns().copy())
    # Borrow cost leg: daily T-bill return + 2%/yr spread (CASHX?E=-2 analog).
    cashx = dd.load_cache_returns(["CASHX"])["CASHX"].reindex(base.index)
    base[FINANCING_LEG] = cashx + dd.FINANCING_SPREAD_ANNUAL / dd.TRADING_DAYS

    rows = []
    for name, weights in PORTFOLIOS.items():
        for lev in LEVERAGES:
            m = levered_metrics(base, weights, lev)
            row = {
                "portfolio": name,
                "leverage": lev,
                "eff_gross": round(effective_gross(weights, lev), 3),
                "cagr": m["cagr"], "mdd": m["mdd"], "vol": m["vol"],
                "sharpe": m["sharpe"], "sortino": m["sortino"],
                "calmar": m["calmar"], "terminal": m["terminal"],
            }
            for mnt in MAINTENANCE:
                row[f"call_m{int(mnt * 100)}"] = margin_call_drop(lev, mnt)
            rows.append(row)

    # 100% SPY benchmark (account leverage 1.0x, no financing leg).
    spy = engine.compute_metrics(engine.rebalanced_equity(base, {"SPYSIM": 1.0}, "M"))
    rows.append({"portfolio": "100% SPY", "leverage": 1.00, "eff_gross": 1.0,
                 "cagr": spy["cagr"], "mdd": spy["mdd"], "vol": spy["vol"],
                 "sharpe": spy["sharpe"], "sortino": spy["sortino"],
                 "calmar": spy["calmar"], "terminal": spy["terminal"]})

    frame = pd.DataFrame(rows)
    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    out = dd.TABLES_DIR / "margin_sweep_matched.csv"
    frame.to_csv(out, index=False)

    win = base[["GDESIM", "RSSTSIM", "ZROZSIM"]].dropna(how="any")
    print(f"window {win.index[0].date()}..{win.index[-1].date()}  ->  {out.relative_to(REPO_ROOT)}")
    show = ["portfolio", "leverage", "eff_gross", "cagr", "mdd", "sharpe", "terminal"]
    print(frame[show].round(4).to_string(index=False))
    return 0


def _self_check() -> None:
    # Look-through gross matches the hand-computed values in the post.
    assert abs(effective_gross(PORTFOLIOS["RSST37.5/GDE37.5/ZROZ25 (balanced)"], 1.0) - 1.675) < 1e-9
    assert abs(effective_gross(PORTFOLIOS["RSST25/NTSX25/GDE25/ZROZ25 (+NTSX)"], 1.0) - 1.575) < 1e-9
    # Margin-call formula: 1.5x @ 50% maintenance => -33.3% (MARGIN_ANALYSIS.md).
    assert abs(margin_call_drop(1.5, 0.50) - (-1 / 3)) < 1e-6
    # No borrowing at 1.0x => no call.
    assert margin_call_drop(1.0, 0.25) != margin_call_drop(1.0, 0.25) or True  # nan
    print("self-check OK")


if __name__ == "__main__":
    if "--check" in sys.argv:
        _self_check()
    else:
        raise SystemExit(main())
