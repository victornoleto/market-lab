#!/usr/bin/env python3
"""Build local stacked-ETF SIM proxies from cached Testfol.io components.

Constructs synthetic price series for six stacked ETFs by daily-return
composition with CASHX financing applied to gross leverage above 1.0.
This is a **discovery-only** proxy: it ignores fund-level fees,
internal rebalancing, vol-targeting, and tracking error vs. the real
ETF. Use for triage GA only; promote survivors to Testfol.io SIMs via
`scripts/testfolio_pull.py` before any validation claim.

Formula (per proxy)::

    notional = sum(weights)
    excess   = max(notional - 1.0, 0.0)
    r_proxy  = sum(w_i * r_component_i) - excess * r_CASHX
    P_proxy  = 10_000 * cumprod(1 + r_proxy)

Output: appends/replaces the proxy columns in
``data/testfolio/cache/history.parquet`` and writes a JSON sidecar at
``data/testfolio/cache/stacked_proxies.meta.json`` documenting formulas
and date ranges.

Citations
---------
* Capital efficiency / financing model: ``[leverage_for_the_long_run, p.13]``.
* Discovery-only flag and "no promotion" gate: ``[testing_tuning, p.327-335]``,
  ``[advances_fin_ml, p.208-211]``.
"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

log = logging.getLogger("build_stacked_sim_proxies")

REPO_ROOT = Path(__file__).resolve().parents[1]
PARQUET_PATH = REPO_ROOT / "data/testfolio/cache/history.parquet"
META_PATH = REPO_ROOT / "data/testfolio/cache/stacked_proxies.meta.json"
START_VAL = 10_000.0

# Proxy spec: target ticker -> ordered dict of component_ticker -> weight.
# Financing on excess notional (gross - 1) is debited against CASHX.
PROXIES: dict[str, dict] = {
    "CTAPSIM": {
        "real_etf": "CTAP (Simplify US Equity PLUS Managed Futures)",
        "real_definition": "100% SPY + 100% CTA (Simplify Managed Futures)",
        "proxy_components": {"SPYSIM": 1.0, "DBMFSIM": 1.0},
        "proxy_note": "DBMFSIM proxies Simplify CTA; real CTA uses vol-target trend.",
    },
    "RSBTSIM": {
        "real_etf": "RSBT (Return Stacked Bonds + Managed Futures)",
        "real_definition": "100% GOVT + 100% MF",
        "proxy_components": {"IEFSIM": 1.0, "DBMFSIM": 1.0},
        "proxy_note": "IEFSIM (7-10y) substitutes GOVT (broad UST 1-30y).",
    },
    "RSITSIM": {
        "real_etf": "RSIT (Return Stacked Intl + Managed Futures)",
        "real_definition": "100% VXUS + 100% MF",
        "proxy_components": {"VXUSSIM": 1.0, "DBMFSIM": 1.0},
        "proxy_note": "Direct components; DBMFSIM proxies MF sleeve.",
    },
    "HOLDSIM": {
        "real_etf": "HOLD (Alpha Architect 1-3 Month Box ETF variant) "
                    "OR (Tidal 75% SPY + 75% MF) — see Tidal stack",
        "real_definition": "75% SPY + 75% MF",
        "proxy_components": {"SPYSIM": 0.75, "DBMFSIM": 0.75},
        "proxy_note": "Less levered than RSST; gross 1.5.",
    },
    "MATESIM": {
        "real_etf": "MATE (Themes/Tidal 100% SPY + 100% AHLT)",
        "real_definition": "100% SPY + 100% AHLT (Man AHL Target Risk)",
        "proxy_components": {"SPYSIM": 1.0, "KMLMSIM": 1.0},
        "proxy_note": "KMLMSIM proxies AHLT; both are rules-based trend.",
    },
    "ESBGSIM": {
        "real_etf": "ESBG (WisdomTree Efficient Core Global Stacked)",
        "real_definition": "70% SPY + 70% IEI + 70% Gold",
        "proxy_components": {"SPYSIM": 0.7, "IEISIM": 0.7, "GLDSIM": 0.7},
        "proxy_note": "Direct IEISIM (3-7y) matches IEI duration band.",
    },
    "GDTSIM": {
        "real_etf": "GDT (Wisdom Tree Efficient Gold Plus Treasuries Strategy)",
        "real_definition": "90% STIP + 90% Gold",
        "proxy_components": {"STIPSIM": 0.9, "GLDSIM": 0.9},
        "proxy_note": "Direct STIPSIM (short-TIPS) + GLDSIM; gross 1.8.",
    },
    "ALLWSIM": {
        "real_etf": "ALLW (SPDR Bridgewater All Weather ETF)",
        "real_definition": "37% DBC + 42% VT + 72% BND + 32% TIPZ",
        "proxy_components": {
            "GSGSIM": 0.37, "VTSIM": 0.42, "BNDSIM": 0.72, "LTPZSIM": 0.32,
        },
        "proxy_note": "GSGSIM proxies DBC (both broad commodity); LTPZSIM proxies TIPZ (long-TIPS).",
    },
    "RSSXSIM": {
        "real_etf": "RSSX (Return Stacked US Stocks & Bitcoin/Gold)",
        "real_definition": "100% SPY + 80% Gold + 20% BTC",
        "proxy_components": {"SPYSIM": 1.0, "GLDSIM": 0.8, "BTCSIM": 0.2},
        "proxy_note": (
            "BTCSIM history starts 2010-07; window will bind there. "
            "BTCSIM has structural survivorship and non-stationarity bias "
            "(pre-ETF/pre-institutional regime). Use for discovery only."
        ),
    },
}

FINANCING_TICKER = "CASHX"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--parquet", type=Path, default=PARQUET_PATH,
        help=f"Path to history parquet (default: {PARQUET_PATH}).",
    )
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _daily_returns(series: pd.Series) -> pd.Series:
    """Simple arithmetic daily returns from a wealth/price series."""
    return series.pct_change()


def _build_proxy(
    df: pd.DataFrame, components: dict[str, float], financing_ticker: str,
) -> tuple[pd.Series, dict]:
    """Compose a stacked proxy as weighted daily returns minus financing.

    Returns a wealth series starting at ``START_VAL`` and a meta dict.
    """
    notional = sum(components.values())
    excess_lev = max(notional - 1.0, 0.0)

    needed = list(components.keys())
    if excess_lev > 0:
        needed.append(financing_ticker)
    missing = [t for t in needed if t not in df.columns]
    if missing:
        raise KeyError(f"missing components in parquet: {missing}")

    sub = df[needed].dropna()
    if sub.empty:
        raise ValueError(f"no aligned dates for components {needed}")

    rets = sub.apply(_daily_returns).dropna(how="all")
    proxy_ret = sum(w * rets[t] for t, w in components.items())
    if excess_lev > 0:
        proxy_ret = proxy_ret - excess_lev * rets[financing_ticker]

    proxy_ret = proxy_ret.dropna()
    wealth = (1.0 + proxy_ret).cumprod() * START_VAL
    # Anchor first bar to START_VAL pre-cumprod so the series begins at
    # exactly 10_000 on the first valid date.
    first_idx = proxy_ret.index[0]
    wealth = pd.concat([
        pd.Series([START_VAL], index=[sub.index[sub.index.get_loc(first_idx) - 1]]
                  if sub.index.get_loc(first_idx) > 0 else [first_idx]),
        wealth,
    ])
    wealth = wealth[~wealth.index.duplicated(keep="first")].sort_index()

    years = (wealth.index[-1] - wealth.index[0]).days / 365.25
    cagr = (wealth.iloc[-1] / wealth.iloc[0]) ** (1.0 / years) - 1.0 if years > 0 else 0.0
    running_max = wealth.cummax()
    mdd = float(((wealth - running_max) / running_max).min())

    meta = {
        "components": components,
        "gross_notional": notional,
        "excess_leverage_financed": excess_lev,
        "financing_ticker": financing_ticker if excess_lev > 0 else None,
        "first_date": wealth.index[0].strftime("%Y-%m-%d"),
        "last_date": wealth.index[-1].strftime("%Y-%m-%d"),
        "bars": int(len(wealth)),
        "first_value": float(wealth.iloc[0]),
        "last_value": float(wealth.iloc[-1]),
        "cagr": float(cagr),
        "mdd": mdd,
    }
    return wealth, meta


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    df = pd.read_parquet(args.parquet)
    log.info("loaded parquet: %d bars × %d cols (%s..%s)",
             len(df), len(df.columns),
             df.index[0].strftime("%Y-%m-%d"), df.index[-1].strftime("%Y-%m-%d"))

    proxy_meta: dict[str, dict] = {}
    new_cols: dict[str, pd.Series] = {}
    for target, spec in PROXIES.items():
        components = spec["proxy_components"]
        log.info("building %s = %s", target, components)
        series, meta = _build_proxy(df, components, FINANCING_TICKER)
        meta["real_etf"] = spec["real_etf"]
        meta["real_definition"] = spec["real_definition"]
        meta["proxy_note"] = spec["proxy_note"]
        proxy_meta[target] = meta
        new_cols[target] = series
        log.info("  %s  %s..%s  %d bars  CAGR %.2f%%  MDD %.2f%%",
                 target, meta["first_date"], meta["last_date"], meta["bars"],
                 meta["cagr"] * 100, meta["mdd"] * 100)

    for target, series in new_cols.items():
        df[target] = series.reindex(df.index)
    df = df[sorted(df.columns)]
    df.to_parquet(args.parquet, compression="snappy")
    log.info("wrote parquet: %d bars × %d cols", len(df), len(df.columns))

    META_PATH.parent.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(json.dumps({
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "parquet": str(args.parquet),
        "financing_ticker": FINANCING_TICKER,
        "start_val": START_VAL,
        "proxies": proxy_meta,
        "caveats": [
            "Discovery-only proxies via daily-return composition.",
            "Ignores fund-level fees, internal rebalancing, vol-targeting.",
            "DBMFSIM proxies the MF sleeve for CTAP/RSBT/RSIT/HOLD; real funds may differ.",
            "KMLMSIM proxies AHLT for MATE; both are rules-based trend.",
            "Financing on excess leverage uses CASHX (short-term cash) returns.",
            "Do not promote a proxy to a validated/deployable strategy.",
        ],
    }, indent=2), encoding="utf-8")
    log.info("wrote meta: %s", META_PATH)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
