#!/usr/bin/env python3
"""Iter 057 — Global hybrid fork (Part B): 60% B4 US + 40% non-US factor blend.

User question (recorded in plan fizzy-forging-bee):
    Fork the B4 US-only portfolio into a global version using a 60/40
    US/non-US split, with the non-US portion using Avantis-style factor
    tilts (AVNM core + AVDV SCV + IDMO momentum + AVEM EM). User proposed
    two specific non-US blends:
        NB1 = 60 AVNM + 14 AVDV + 14 IDMO + 12 AVEM (40% factor tilt)
        NB2 = 70 AVNM + 10.5 AVDV + 10.5 IDMO + 9 AVEM (30% factor tilt)
    Plus a control NB3 = 100 AVNM (no factor tilt).
    Top-level US/non-US splits: 100/0, 70/30, 60/40, 55/45.

Engine: long_term_portfolio internal engine (synths.py + portfolio_returns_from_config).
        Internal engine bypasses testfol.io's 10-ticker/portfolio limit and
        uses the parquet cache for VEASIM/VWOSIM/VSSSIM (1994+ window) plus
        Avantis tilt synths for AVDV/AVEM/AVNM/AVDE.

US side = B4 base (NTSX 25 + GDE 25 + RSST 25 + ZROZ 25), no BTC/SCV/momentum
        sleeves on US side. This keeps the Part B comparison FOCUSED on the
        non-US factor tilt question (Part A already covered B4 reallocation
        with BTC/SCV/momentum and identified P5b as the US-only winner).

Window: bottleneck = VWOSIM inception 1994-05-04 (~32y). For non-US blends
        with IDMO (real ETF, 2018+), per-portfolio window auto-clips to
        2018-09 (~7.6y) — flagged as INCOMPLETE since rolling 5y/10y windows
        are sparse.

Benchmarks:
    - SPY (1x buy-and-hold) for the user's "beats SPY" question
    - VT (1x buy-and-hold via VTSIM) for the user's "beats VT" question

Citations:
    - Capital-efficient stacking blueprint (B4 US side): [risk_parity, ch.5, p.10]
    - Avantis multi-factor tilts (AVNM/AVDV/AVEM/AVDE):
      [risk_parity, ch.2, p.37-41] Fama-French SCV; personal Plano C notes moved outside the public repo;
      Avantis factsheets 2024-09.
    - Intl momentum (IDMO): [stocks_on_the_move, p.21-30] Clenow time-series
      momentum; Frazzini-Israel-Moskowitz 2018 long-only momentum capture.
    - 60/40 US/non-US allocation rationale: personal Plano C notes moved outside the public repo
      (Bogle, Bernstein, Asness "International Diversification").
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from ai_trade.backtest.data.testfolio_loader import load_testfolio_series
from ai_trade.backtest.metrics.performance import (
    cagr as _cagr_fn,
    max_drawdown as _mdd_fn,
    sharpe as _sharpe_fn,
)
from studies.long_term_portfolio.run_iter import portfolio_returns_from_config
from studies.long_term_portfolio.rolling_windows import rolling_outperformance_pct
from studies.long_term_portfolio.synths import (
    avnm_synth_returns_from_cache,
    avdv_synth_returns_from_cache,
    avem_synth_returns_from_cache,
    idmo_synth_returns_from_cache,
)


SCRIPT_DIR = Path(__file__).parent
ITER_N = 57
HYPOTHESIS_SLUG = "global-fork-hybrid-60-40-us-nonus"
TRADING_DAYS_PER_YEAR = 252
WINDOWS_YEARS = [3, 5, 10, 15]


# ---------------------------------------------------------------------------
# Portfolio definitions
# ---------------------------------------------------------------------------
#
# Internal engine convention: weights as decimals (sum to 1.0).
# Each non-US blend NB1/NB2/NB3 is normalized to sum to 1.0; we apply the
# US/non-US split by multiplying.
#
# US-side (B4 base, no factor sleeves): NTSX/GDE/RSST/ZROZ at 25/25/25/25.
# Internal engine resolves NTSX -> proxies.expand_capital_efficient -> SPYSIM/IEFSIM/CASHX,
# RSST -> synths.rsst_synth_returns_from_cache (SPYSIM + KMLMSIM - 60bps) which
# uses the FULL RSST proxy (KMLM-included) per [ilmanen_expected_returns, ch.19].

US_B4_WEIGHTS = {"NTSXSIM": 0.25, "GDESIM": 0.25, "RSSTSIM": 0.25, "ZROZSIM": 0.25}

NON_US_BLENDS = {
    # NB1 = 60% AVNM + 14% AVDV + 14% IDMO + 12% AVEM (40% factor tilt)
    "NB1_factor40": {"AVNMSIM": 0.60, "AVDVSIM": 0.14, "IDMOSIM": 0.14, "AVEMSIM": 0.12},
    # NB2 = 70% AVNM + 10.5% AVDV + 10.5% IDMO + 9% AVEM (30% factor tilt)
    "NB2_factor30": {"AVNMSIM": 0.70, "AVDVSIM": 0.105, "IDMOSIM": 0.105, "AVEMSIM": 0.09},
    # NB3 = 100% AVNM (control, no tilt)
    "NB3_avnm_only": {"AVNMSIM": 1.0},
}

US_NONUS_SPLITS = [
    (1.00, 0.00, "100_00"),  # US-only baseline
    (0.70, 0.30, "70_30"),   # light global
    (0.60, 0.40, "60_40"),   # user's primary
    (0.55, 0.45, "55_45"),   # closer to global market-cap
]


def build_portfolio_configs() -> dict[str, dict[str, float]]:
    """Return {portfolio_name: {ticker: weight}, ...} (weights decimal, sum 1.0)."""
    configs: dict[str, dict[str, float]] = {}

    # 100% B4 US-only (single control, regardless of NB choice)
    configs["B4_us_only"] = dict(US_B4_WEIGHTS)

    for nb_name, nb_weights in NON_US_BLENDS.items():
        for us_w, non_us_w, split_label in US_NONUS_SPLITS:
            if us_w == 1.0:
                continue  # skip 100/0 — already added as B4_us_only
            cfg: dict[str, float] = {}
            for t, w in US_B4_WEIGHTS.items():
                cfg[t] = cfg.get(t, 0.0) + us_w * w
            for t, w in nb_weights.items():
                cfg[t] = cfg.get(t, 0.0) + non_us_w * w
            configs[f"{split_label}__{nb_name}"] = cfg
    return configs


# ---------------------------------------------------------------------------
# Benchmark series (SPY + VT)
# ---------------------------------------------------------------------------


def load_spy_returns() -> pd.Series:
    """SPY 1x buy-and-hold daily returns from testfolio cache (SPYSIM)."""
    return load_testfolio_series("SPYSIM").pct_change().dropna()


def load_vt_returns() -> pd.Series:
    """VT 1x buy-and-hold daily returns from testfolio cache (VTSIM)."""
    return load_testfolio_series("VTSIM").pct_change().dropna()


# ---------------------------------------------------------------------------
# Per-config metrics
# ---------------------------------------------------------------------------


def _compute_metrics(returns: pd.Series) -> dict[str, float]:
    if len(returns) < 2:
        return {"sharpe": float("nan"), "cagr": float("nan"), "mdd": float("nan"),
                "n_obs": int(len(returns)),
                "start": None, "end": None, "years": float("nan")}
    eq = (1.0 + returns).cumprod() * 10_000.0
    return {
        "sharpe": float(_sharpe_fn(returns, periods_per_year=TRADING_DAYS_PER_YEAR)),
        "cagr": float(_cagr_fn(eq, periods_per_year=TRADING_DAYS_PER_YEAR)),
        "mdd": float(_mdd_fn(eq)),
        "n_obs": int(len(returns)),
        "start": str(returns.index[0].date()),
        "end": str(returns.index[-1].date()),
        "years": float((returns.index[-1] - returns.index[0]).days / 365.25),
    }


def _windows_dict(beats: dict[int, dict[str, float]]) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for w, d in beats.items():
        pct = d["pct_strat_wins"]
        out[str(w)] = {
            "pct_strat_wins": None if (isinstance(pct, float) and np.isnan(pct)) else pct,
            "n_windows": int(d["n_windows"]),
            "mean_sharpe_diff": (
                None if (isinstance(d["mean_sharpe_diff"], float)
                         and np.isnan(d["mean_sharpe_diff"]))
                else d["mean_sharpe_diff"]
            ),
        }
    return out


def main() -> int:
    configs = build_portfolio_configs()
    print(f"[iter057] {len(configs)} configs to evaluate (lh_56y dataset)")

    spy_returns = load_spy_returns()
    vt_returns = load_vt_returns()

    rows: list[dict] = []
    for name, cfg in configs.items():
        try:
            r = portfolio_returns_from_config(cfg, dataset="lh_56y")
        except Exception as exc:  # pragma: no cover - guard
            print(f"[iter057] {name}: FAILED — {exc!r}")
            continue
        m = _compute_metrics(r)
        beats_spy = rolling_outperformance_pct(r, spy_returns, windows_years=WINDOWS_YEARS)
        beats_vt = rolling_outperformance_pct(r, vt_returns, windows_years=WINDOWS_YEARS)
        rows.append({
            "name": name,
            "config": cfg,
            "metrics": m,
            "windows_beat_spy": _windows_dict(beats_spy),
            "windows_beat_vt": _windows_dict(beats_vt),
        })
        print(f"[iter057] {name:<28} CAGR {m['cagr']*100:>6.2f}%  "
              f"MDD {m['mdd']*100:>7.2f}%  Sharpe {m['sharpe']:.3f}  "
              f"n={m['n_obs']:>5}  yr={m['years']:.1f}")

    # Rank by Sharpe (full window)
    ranked = sorted(rows, key=lambda r: -r["metrics"]["sharpe"])

    # Compute SPY/VT benchmark metrics on full lh_56y for context
    spy_meta = _compute_metrics(spy_returns)
    vt_meta = _compute_metrics(vt_returns)

    verdict = {
        "iter_n": ITER_N,
        "hypothesis_slug": HYPOTHESIS_SLUG,
        "engine": "long_term_portfolio internal (synths.py + portfolio_returns_from_config)",
        "dataset": "lh_56y",
        "n_configs": len(rows),
        "selected": ranked[0]["name"] if ranked else None,
        "selection_rule": "max(Sharpe) on lh_56y",
        "benchmarks": {
            "SPY_1x": {"sharpe": spy_meta["sharpe"], "cagr": spy_meta["cagr"],
                       "mdd": spy_meta["mdd"], "n_obs": spy_meta["n_obs"]},
            "VT_1x":  {"sharpe": vt_meta["sharpe"], "cagr": vt_meta["cagr"],
                       "mdd": vt_meta["mdd"], "n_obs": vt_meta["n_obs"]},
        },
        "ranking": ranked,
    }

    (SCRIPT_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")

    # final_report.md
    write_final_report(SCRIPT_DIR, verdict, spy_meta, vt_meta)
    print(f"\n[iter057] wrote verdict.json + final_report.md")
    if ranked:
        print(f"[iter057] selected: {ranked[0]['name']} "
              f"(Sharpe {ranked[0]['metrics']['sharpe']:.3f})")
    return 0


def write_final_report(iter_dir: Path, verdict: dict, spy_meta: dict, vt_meta: dict) -> None:
    lines = [
        f"# Iter {verdict['iter_n']:03d} — `{verdict['hypothesis_slug']}`",
        "",
        f"**Engine:** {verdict['engine']}",
        f"**Dataset:** {verdict['dataset']} (lh_56y; per-config window clips to underlying inception)",
        f"**Selected:** `{verdict['selected']}`",
        "",
        "## Benchmarks (full lh_56y window, gross-of-tax)",
        "",
        "| benchmark | window | CAGR | MDD | Sharpe |",
        "|---|---|---:|---:|---:|",
        f"| SPY (1x) | {spy_meta['start']} → {spy_meta['end']} ({spy_meta['years']:.1f}y) | "
        f"{spy_meta['cagr']*100:.2f}% | {spy_meta['mdd']*100:.2f}% | {spy_meta['sharpe']:.3f} |",
        f"| VT (1x via VTSIM) | {vt_meta['start']} → {vt_meta['end']} ({vt_meta['years']:.1f}y) | "
        f"{vt_meta['cagr']*100:.2f}% | {vt_meta['mdd']*100:.2f}% | {vt_meta['sharpe']:.3f} |",
        "",
        "## Ranking by Sharpe",
        "",
        "| # | config | window | CAGR | MDD | Sharpe |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for i, r in enumerate(verdict["ranking"], 1):
        m = r["metrics"]
        lines.append(
            f"| {i} | `{r['name']}` | "
            f"{m['start']} → {m['end']} ({m['years']:.1f}y) | "
            f"{m['cagr']*100:.2f}% | {m['mdd']*100:.2f}% | {m['sharpe']:.3f} |"
        )

    for bench_label, key in [("SPY", "windows_beat_spy"), ("VT", "windows_beat_vt")]:
        lines += [
            "",
            f"## % rolling-windows beating {bench_label}",
            "",
            "| config | 3y | 5y | 10y | 15y |",
            "|---|---:|---:|---:|---:|",
        ]
        for r in verdict["ranking"]:
            cells = []
            for w in ("3", "5", "10", "15"):
                d = r[key].get(w, {})
                pct = d.get("pct_strat_wins")
                n = d.get("n_windows", 0)
                if pct is None or n == 0:
                    cells.append("n/a")
                else:
                    cells.append(f"{pct*100:.1f}% (n={n})")
            lines.append(f"| `{r['name']}` | " + " | ".join(cells) + " |")

    lines += [
        "",
        "## Configs (US/non-US weight breakdown)",
        "",
    ]
    for r in verdict["ranking"]:
        lines.append(f"### `{r['name']}`")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(r["config"], indent=2))
        lines.append("```")
        lines.append("")

    lines += [
        "## INCOMPLETE flags",
        "",
        "- AVNM synth: ~78% VEASIM + ~22% VWOSIM + 60bps blended tilt premium "
        "(Avantis multi-factor screens proprietary; static premium is conservative midpoint).",
        "- AVDV/AVEM tilt premiums (100/125bps) injected via flat annual drag; "
        "real Avantis ER + tilt may differ by regime.",
        "- IDMO: real ETF history (2018-09+) used directly; synth path uses VEASIM + "
        "0.6×US-UMD as proxy for intl momentum (US UMD ≠ intl momentum exactly).",
        "- VWOSIM bottleneck: 1994+, so per-config window narrows when AVEM/AVNM/AVDV present.",
        "- IDMO real ETF window: 2018-09+ (7.6y); rolling 10y/15y windows return n/a.",
        "",
        "## Lesson",
        "",
        "(Append after manual review.)",
        "",
    ]
    (iter_dir / "final_report.md").write_text("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
