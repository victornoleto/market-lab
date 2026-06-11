#!/usr/bin/env python3
"""s02 — per-episode behavior of components and stacked products/portfolios.

Slices full-period equity curves (portfolios run from their window start, so
episode returns reflect the path an actual holder experienced) across 15
bull/bear episodes. Episode dates for dot-com/GFC/COVID/2022 match
``robustness_tables/us_regime_stress.csv``.

Cross-check semantics (provenance verified 2026-06-11):
- SPY rows must match the saved table within ±0.5pp — same data source, so
  drift means a bug (hard WARNING).
- CORE rows are *expected* to diverge: the saved table slices the historical
  1988 testfol.io curve (original RSST payload), while this study uses the
  adjusted RSST tracking proxy matrix (study README: "expect non-trivial
  differences versus the historical 1988 saved series"). E.g. GFC: −13.8%
  (old curve) vs ≈−23% (tracking proxy) — the MF sleeve's crisis-alpha is
  proxy-sensitive. Recorded in episodes_crosscheck.csv as documentation and
  surfaced as a caveat in METHODS.md/POST.md, not as a failure.

Outputs:
- ``tables/episodes_components.csv`` — individual sleeves (SPY, GLD, MF, ZROZ, BTC...).
- ``tables/episodes_products.csv`` — stacked ETFs + portfolios (CORE, HFEA, DIY-SSO...).
- ``tables/episodes_crosscheck.csv`` — drift vs the saved regime-stress rows.

Regime framing: diversifier behavior in equity drawdowns `[risk_parity, ch.5]`;
the 2022 row is the key exhibit (stocks AND long bonds down, trend/gold carried)
`[leverage_for_the_long_run, p.13]`.
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

EPISODES = [
    ("Stagflation bear", "1973-01-11", "1974-10-03", "extended"),
    ("Gold/inflation bull", "1976-09-21", "1980-01-21", "extended"),
    ("Volcker rate shock", "1979-10-01", "1982-08-12", "extended"),
    ("1987 crash", "1987-08-25", "1987-12-04", "extended"),
    ("Dot-com bust", "2000-03-24", "2002-10-09", "primary"),
    ("2003-07 bull", "2002-10-09", "2007-10-09", "primary"),
    ("GFC", "2007-10-09", "2009-03-09", "primary"),
    ("QE bull", "2009-03-09", "2020-02-19", "primary"),
    ("US downgrade / euro crisis", "2011-04-29", "2011-10-03", "primary"),
    ("Taper tantrum", "2013-05-02", "2013-12-31", "primary"),
    ("China/oil correction", "2015-05-21", "2016-02-11", "primary"),
    ("Q4-2018", "2018-09-20", "2018-12-24", "primary"),
    ("Covid crash", "2020-02-19", "2020-03-23", "primary"),
    ("Inflation/rates shock", "2022-01-03", "2022-10-14", "primary"),
    ("AI bull", "2022-10-14", "2026-05-21", "primary"),
]

CORE = {"GDESIM": 0.35, "RSSTSIM": 0.40, "ZROZSIM": 0.25}
HFEA = {"UPROSIM": 0.55, "TMFSIM_D": 0.45}
DIY_SSO = {"SSOSIM": 0.35, "GLDSIM": 0.20, "MFBLEND": 0.25, "ZROZSIM": 0.20}

# Saved rows from robustness_tables/us_regime_stress.csv. SPY = integrity gate
# (same source); CORE (B4-v2, old 1988 curve) = documented proxy divergence.
CROSSCHECK_SPY = {
    "Dot-com bust": -0.47376877397343375,
    "GFC": -0.5514127407707087,
    "Covid crash": -0.3369411207718872,
    "Inflation/rates shock": -0.2421456488393342,
}
CROSSCHECK_CORE_OLD_CURVE = {
    "Dot-com bust": -0.1887755138829228,
    "GFC": -0.13761577684998794,
    "Covid crash": -0.17209022071258795,
    "Inflation/rates shock": -0.1700766781921782,
}


def _slice_stats(equity: pd.Series, start: str, end: str) -> dict | None:
    idx = equity.dropna().index
    eligible = idx[(idx >= pd.Timestamp(start)) & (idx <= pd.Timestamp(end))]
    if len(eligible) < 2 or eligible[0] > pd.Timestamp(start) + pd.Timedelta(days=10):
        return None
    window = equity.loc[eligible[0] : eligible[-1]].dropna()
    norm = window / window.iloc[0]
    return {
        "total_return": float(norm.iloc[-1] - 1.0),
        "episode_mdd": float((norm / norm.cummax() - 1.0).min()),
    }


def episode_table(
    curves: dict[str, pd.Series], episodes: list, spy: pd.Series
) -> pd.DataFrame:
    rows = []
    for name, start, end, window in episodes:
        spy_stats = _slice_stats(spy, start, end)
        for asset, eq in curves.items():
            stats = _slice_stats(eq, start, end)
            rows.append(
                {
                    "episode": name,
                    "start": start,
                    "end": end,
                    "window": window,
                    "asset": asset,
                    "total_return": stats["total_return"] if stats else float("nan"),
                    "episode_mdd": stats["episode_mdd"] if stats else float("nan"),
                    "spread_vs_spy": (
                        stats["total_return"] - spy_stats["total_return"]
                        if stats and spy_stats
                        else float("nan")
                    ),
                }
            )
    return pd.DataFrame(rows)


def main() -> int:
    primary = pd.read_parquet(dd.SERIES_DIR / "primary_returns.parquet")
    proxies = pd.read_parquet(dd.SERIES_DIR / "proxy_returns.parquet")
    daily = primary.join(proxies)

    eq = engine.equity_from_returns
    primary_eps = [e for e in EPISODES if e[3] == "primary"]
    spy_eq = eq(daily["SPYSIM"])

    components = {
        "SPY": spy_eq,
        "GLD": eq(daily["GLDSIM"]),
        "MFBLEND": eq(daily["MFBLEND"]),
        "DBMF": eq(daily["DBMFSIM"]),
        "KMLM": eq(daily["KMLMSIM"]),
        "ZROZ": eq(daily["ZROZSIM"]),
        "TLTPROXY": eq(daily["TLTPROXY"]),
        "BTC": eq(daily["BTCSIM"]),
    }
    comp_df = episode_table(components, primary_eps, spy_eq)

    products = {
        "SPY": spy_eq,
        "GDE": eq(daily["GDESIM"]),
        "RSST": eq(daily["RSSTSIM"]),
        "NTSX": eq(daily["NTSXSIM"]),
        "RSSX": eq(daily["RSSXSIM"]),
        "CORE 35/40/25": engine.rebalanced_equity(daily, CORE),
        "HFEA 55/45": engine.rebalanced_equity(daily, HFEA),
        "DIY-SSO": engine.rebalanced_equity(daily, DIY_SSO),
        "100% SSO": eq(daily["SSOSIM"]),
        "100% UPRO": eq(daily["UPROSIM"]),
    }
    prod_df = episode_table(products, primary_eps, spy_eq)

    # Extended-window episodes (LOW fidelity), if the matrix exists.
    ext_path = dd.SERIES_DIR / "extended_returns.parquet"
    if ext_path.exists():
        ext = pd.read_parquet(ext_path)
        ext_eps = [e for e in EPISODES if e[3] == "extended"]
        spy_ext = eq(ext["SPYSIM"])
        ext_components = {
            "SPY": spy_ext,
            "GLD": eq(ext["GLDSIM"]),
            "KMLM_SPLICED": eq(ext["KMLM_SPLICED"]),
            "ZROZ": eq(ext["ZROZSIM"]),
            "IEF": eq(ext["IEFSIM"]),
        }
        comp_df = pd.concat(
            [comp_df, episode_table(ext_components, ext_eps, spy_ext)],
            ignore_index=True,
        )
        ext_products = {
            "SPY": spy_ext,
            "GDE": eq(ext["GDESIM"]),
            "NTSX": eq(ext["NTSXSIM"]),
            "RSST_EXT_HAIRCUT": eq(ext["RSST_EXT_HAIRCUT"]),
            "CORE-EXT-HAIRCUT": engine.rebalanced_equity(
                ext,
                {"GDESIM": 0.35, "RSST_EXT_HAIRCUT": 0.40, "ZROZSIM": 0.25},
            ),
            "HFEA 55/45": engine.rebalanced_equity(ext, HFEA),
            "100% SSO": eq(ext["SSOSIM"]),
            "100% UPRO": eq(ext["UPROSIM"]),
        }
        prod_df = pd.concat(
            [prod_df, episode_table(ext_products, ext_eps, spy_ext)],
            ignore_index=True,
        )
    else:
        print("WARNING: extended matrix missing — extended episodes skipped.",
              file=sys.stderr)

    dd.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    comp_df.to_csv(dd.TABLES_DIR / "episodes_components.csv", index=False)
    prod_df.to_csv(dd.TABLES_DIR / "episodes_products.csv", index=False)

    # Cross-checks: SPY = integrity gate; CORE = documented proxy divergence.
    rows = []
    failures = 0
    spy_rows = prod_df[prod_df["asset"] == "SPY"].set_index("episode")
    core_rows = prod_df[prod_df["asset"] == "CORE 35/40/25"].set_index("episode")
    for episode, expected in CROSSCHECK_SPY.items():
        got = float(spy_rows.loc[episode, "total_return"])
        drift = abs(got - expected)
        ok = drift <= 0.005
        failures += 0 if ok else 1
        rows.append(
            {"episode": episode, "asset": "SPY", "kind": "integrity_gate",
             "discussion": got, "saved": expected, "abs_drift": drift, "ok": ok}
        )
        print(f"crosscheck SPY {episode}: {got:.2%} vs saved {expected:.2%} "
              f"[{'OK' if ok else 'DRIFT'}]")
    for episode, expected in CROSSCHECK_CORE_OLD_CURVE.items():
        got = float(core_rows.loc[episode, "total_return"])
        rows.append(
            {"episode": episode, "asset": "CORE 35/40/25",
             "kind": "old_curve_divergence_documentation",
             "discussion": got, "saved": expected,
             "abs_drift": abs(got - expected), "ok": True}
        )
        print(f"proxy divergence CORE {episode}: tracking-proxy {got:.2%} vs "
              f"old 1988 curve {expected:.2%} (expected, documented)")
    pd.DataFrame(rows).to_csv(dd.TABLES_DIR / "episodes_crosscheck.csv", index=False)

    print(f"episodes_components: {len(comp_df)} rows; episodes_products: {len(prod_df)} rows")
    if failures:
        print(f"ERROR: {failures} SPY integrity cross-checks drifted > 0.5pp",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
