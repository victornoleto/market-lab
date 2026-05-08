"""Shared helper for B4-reallocation + global-fork sweeps via testfol.io API.

Used by:
    studies/long_term_portfolio/iterations/056-* (B4 reallocation, Part A)
    studies/long_term_portfolio/iterations/057-* (Global hybrid fork, Part B)

Workflow per iter:
    1. Define list[Portfolio] with allocation_real = [(weight_pct, ticker), ...]
    2. Call run_sweep(portfolios, start_date) -> hits testfol.io API in batches
       and returns parsed responses + raw equity curves.
    3. Call attach_window_metrics(results, bench_slug='SPY_1x', ...) ->
       computes % rolling-windows where each portfolio Sharpe > benchmark Sharpe
       at 3y/5y/10y/15y, using studies.long_term_portfolio.rolling_windows.
    4. Call write_verdict(iter_dir, results) -> persists verdict.json +
       final_report.md.

Why testfol.io API instead of long_term_portfolio.run_iter?
    - BTCSIM has 2010-07+ history in testfol.io but is NOT in our parquet cache
      (cache lacks BTC; Tiingo BTC starts 2014, losing 4 years).
    - iter 047 (B4+BTC5) is the user's anchor: 22.01% CAGR / -27.90% MDD /
      Sharpe 1.311 — reproducing exactly requires same engine.
    - testfol.io supports raw ETF tickers (AVUV, SPMO, MTUM) when needed and
      SIM proxies (VBRSIM, VEASIM, VWOSIM) for long-history backfill.

Citations:
    - Capital-efficient stacking blueprint (NTSX/GDE/RSST):
      [risk_parity, ch.5, p.10] — Carlson on cap-efficient stacking.
    - Avantis SCV/value tilts:
      [risk_parity, ch.2, p.37-41] Fama-French SCV; personal Plano C notes moved outside the public repo.
    - Momentum tilts (SPMO/MTUM/IDMO):
      [stocks_on_the_move, p.21-30] Clenow time-series momentum;
      Frazzini-Israel-Moskowitz 2018 long-only momentum capture (60% literature).
    - BTC sizing as speculative satellite:
      `[machine_trading, p.202, ch.7]` Chan on crypto venue/operational risk.
    - BTGD synth: WisdomTree BTGD prospectus 2024-08 (50/50 BTC futures + gold).
    - RSSX synth: ReturnStacked RSSX whitepaper 2025-01 (100/100 SPY + BTC stack).
    - DSR / cumulative n_trials: [advances_fin_ml, p.222-223].
"""

from __future__ import annotations

import datetime as dt
import json
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from studies.long_term_portfolio.rolling_windows import (
    DEFAULT_WINDOWS_YEARS,
    rolling_outperformance_pct,
)


API_BACKTEST = "https://testfol.io/api/backtest"
INITIAL = 10_000.0
TRADING_DAYS_PER_YEAR = 252
DEFAULT_BATCH_SIZE = 5  # testfol.io tolerated batch size from iter 047/052


# ---------------------------------------------------------------------------
# Decomposition: real ticker -> testfol.io primitives + portfolio-level drag
# ---------------------------------------------------------------------------
#
# Conventions:
#   - Positive drag entry = expense ratio (cost to investor).
#   - Negative drag entry = tilt premium credited (e.g. Avantis SCV).
#   - Net portfolio drag = weight-summed; testfol.io applies it monthly.
#
# Avantis tilt premiums per Fama-French SCV literature midpoints documented in
# studies/long_term_portfolio/synths.py (factor_tilt_synth_returns):
#     AVUV: +75bps tilt − 25bps ER -> NET −50bps (premium > cost)
#     AVDV: +100bps tilt − 36bps ER -> NET −64bps
#     AVEM: +125bps tilt − 33bps ER -> NET −92bps
#     AVNM: +60bps blended tilt − 38bps ER -> NET −22bps (Avantis cap-weighted multi-factor)
#     IDMO: +60% × momentum_premium − 25bps ER ~ NET roughly flat to −20bps
#         (Frazzini-Israel-Moskowitz capture; modeled as flat 0bps net here
#         because intl momentum is hard to inject via static drag — accepted
#         limitation, documented INCOMPLETE).
#     SPMO: similar -- modeled as 0bps net (US momentum overlay not available
#         as testfol.io factor; INCOMPLETE).
#
# BTGD: WisdomTree 2024 ETF, 50% BTC futures + 50% gold futures stacked, 0.55%
# ER. Approximated as 50% BTCSIM (spot, no futures roll) + 50% GLDSIM.
# INCOMPLETE: real BTGD uses CME BTC futures with quarterly roll cost ~3-5%/y
# during contango. Spot proxy understates roll drag in steep-contango regimes.
#
# RSSX: Newfound/ReSolve 2025 ETF, 100% SPY + 100% "BTC/Gold inverse-vol
# stack", 1.05% ER. Reading actual holdings (2026-05-05 fact sheet):
#     SPY ETF + S&P futures   → ~100% SPY notional
#     Gold futures            → ~66% notional
#     BTC futures + IBIT      → ~35% notional
#     Cash/Treasury           → collateral for futures
# The "second 100%" is split between gold and BTC by inverse-volatility
# weighting (gold gets ~65% because BTC vol is ~4× gold vol). Earlier
# synth (100% SPY + 100% BTC − borrow) was wrong: it overstated BTC
# exposure ~3× and ignored the gold leg. New synth approximates the
# observed allocation as SPYSIM 1.0 + GLDSIM 0.65 + BTCSIM 0.35 − CASHX?E=-2 1.0.
# INCOMPLETE: (a) inverse-vol weights drift with realized vol (snapshot
# only); (b) gold/BTC futures roll cost not modeled (~3-5%/y in contango);
# (c) CASHX?E=-2 borrow is constant 2% over cash, real cost varies w/ FFR.
NET_DRAG_BPS: dict[str, float] = {
    # Core B4 sleeves
    "NTSX": 0.20,
    "GDE": 0.20,
    "RSST": 0.99,
    "ZROZ": 0.15,
    # Bond/cash duration
    "TLT": 0.15,
    "IEF": 0.15,
    # Single-asset
    "SPY": 0.0945,
    "BTC": 0.25,  # IBIT-like spot ETF placeholder
    "GLD": 0.40,
    "QQQ": 0.20,
    # Stacked variants of BTC/Gold
    "BTGD": 0.55,
    "RSSX": 1.05,
    # Factor sleeves (NET = ER − tilt premium)
    "AVUV": -0.50,   # 25bps ER − 75bps SCV tilt
    "AVDV": -0.64,   # 36bps ER − 100bps tilt
    "AVEM": -0.92,   # 33bps ER − 125bps tilt
    "AVNM": -0.22,   # 38bps ER − 60bps blended tilt
    "AVDE": -0.32,   # 23bps ER − 55bps DM ex-US blended tilt
    "VBR": 0.07,
    "IDMO": 0.25,    # ER only; momentum overlay not modeled (INCOMPLETE)
    "SPMO": 0.13,    # idem
    "MTUM": 0.15,
    "FMTM": 0.15,
}


# Mapping a "real ticker" the user thinks in -> testfol.io primitives + weights.
# Weights sum to 1.0 within each mapping (i.e. sleeve-level decomposition);
# portfolio-level multiplication happens in expand().
MAPPINGS: dict[str, list[tuple[str, float]]] = {
    # --- B4 core sleeves (testfol.io primitives where available) ----------
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    # RSST simplified to 100% DBMF (dropping KMLM 30% allocation) so that
    # combined portfolios using BTGD/RSSX stay under testfol.io's 10-ticker/portfolio
    # limit. iter 047's "corrected RSST" used 70/30 DBMF/KMLM (5 tickers when
    # combined with NTSX+GDE+ZROZ); switching to 100% DBMF saves 1 ticker
    # slot and remains a literature-faithful trend-following proxy
    # (DBMF tracks SG CTA Index, the primary multi-strategy MF benchmark
    # [ilmanen_expected_returns, ch.19]). Expected B4 Sharpe drift ≈ ±2bps.
    "RSST": [("SPYSIM", 1.00), ("DBMFSIM", 1.00), ("CASHX?E=-2", -1.00)],
    "GDE": [("GDESIM", 1.0)],
    "ZROZ": [("ZROZSIM", 1.0)],
    "TLT": [("TLTSIM", 1.0)],
    "IEF": [("IEFSIM", 1.0)],
    "SPY": [("SPYSIM", 1.0)],
    "QQQ": [("QQQSIM", 1.0)],
    "GLD": [("GLDSIM", 1.0)],
    # --- Bitcoin variants -------------------------------------------------
    "BTC": [("BTCSIM", 1.0)],
    # BTGD = 50% BTC futures + 50% gold futures stacked. Spot-proxy here.
    # Source: WisdomTree BTGD prospectus 2024-08.
    "BTGD": [("BTCSIM", 0.50), ("GLDSIM", 0.50)],
    # RSSX = 100% SPY + 100% (vol-weighted Gold + BTC) stacked − borrow leg.
    # Source: ReturnStacked RSSX whitepaper 2025-01 + fact sheet 2026-05-05
    # (gold ~65%, BTC ~35% of the second 100% by inverse-vol weighting).
    "RSSX": [("SPYSIM", 1.00), ("GLDSIM", 0.65), ("BTCSIM", 0.35), ("CASHX?E=-2", -1.00)],
    # --- Factor sleeves (synth via testfol.io primitives) -----------------
    # AVUV = US small-cap value, proxied by VBRSIM (Russell 2000 Value).
    # Tilt premium injected via NET_DRAG_BPS[AVUV] = -0.50 (negative drag).
    "AVUV": [("VBRSIM", 1.0)],
    # AVDV = developed ex-US SCV, proxied by VSSSIM.
    "AVDV": [("VSSSIM", 1.0)],
    # AVEM = EM core, proxied by VWOSIM.
    "AVEM": [("VWOSIM", 1.0)],
    # AVDE = developed ex-US core, proxied by VEASIM.
    "AVDE": [("VEASIM", 1.0)],
    # AVNM = "All Non-US" Avantis, blend ~78% developed + 22% EM by mkt-cap.
    # Source: Avantis AVNM factsheet 2024 + personal Plano C notes moved outside the public repo.
    "AVNM": [("VEASIM", 0.78), ("VWOSIM", 0.22)],
    # VBR — passthrough for direct comparison (no tilt premium).
    "VBR": [("VBRSIM", 1.0)],
    # SPMO/MTUM/FMTM/IDMO use real testfol.io tickers when available;
    # else SIM passthroughs. testfol.io accepts raw tickers like SPMO,
    # MTUM directly (ETF history limited to inception, but we accept that
    # for momentum sleeves where literature factor synth is harder to model
    # cleanly via static drag).
    "SPMO": [("SPMO", 1.0)],
    "MTUM": [("MTUM", 1.0)],
    "FMTM": [("FMTM", 1.0)],
    "IDMO": [("IDMO", 1.0)],
}


# ---------------------------------------------------------------------------
# Portfolio expansion + drag
# ---------------------------------------------------------------------------


Portfolio = dict[str, Any]
Allocation = list[tuple[float, str]]


def expand(weight_pct: float, ticker: str) -> list[tuple[str, float]]:
    ticker = ticker.upper()
    if ticker in MAPPINGS:
        return [(token, weight_pct * mult) for token, mult in MAPPINGS[ticker]]
    return [(ticker, weight_pct)]


def decompose(allocation: Allocation) -> dict[str, float]:
    """Aggregate sleeve-level weights into testfol.io primitive weights."""
    agg: defaultdict[str, float] = defaultdict(float)
    for pct, ticker in allocation:
        for token, weight_pct in expand(pct, ticker):
            agg[token] += weight_pct
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def compute_drag(allocation: Allocation) -> float:
    """Sum sleeve-level NET drag (positive = cost, negative = tilt credit).

    Returned in PERCENT units (testfol.io convention: 0.50 means 0.50%/y).
    """
    return round(
        sum((pct / 100.0) * NET_DRAG_BPS.get(ticker.upper(), 0.0)
            for pct, ticker in allocation),
        4,
    )


def make_portfolio(slug: str, label: str, allocation_real: Allocation) -> Portfolio:
    return {
        "slug": slug,
        "label": label,
        "allocation_real": allocation_real,
        "allocation_sim": decompose(allocation_real),
        "drag_pct": compute_drag(allocation_real),
    }


# ---------------------------------------------------------------------------
# testfol.io API call
# ---------------------------------------------------------------------------


def _payload(portfolios: list[Portfolio], start_date: str = "2000-01-01") -> dict:
    return {
        "start_date": start_date,
        "end_date": "2100-01-01",
        "start_val": INITIAL,
        "adj_inflation": False,
        "cashflow": 0,
        "cashflow_freq": "Yearly",
        "cashflow_offset": 0,
        "match_first_portfolio_income_cashflows": False,
        "one_time_cashflows": [],
        "rolling_window": 60,
        "withdrawal_surface_include": False,
        "withdrawal_surface_projection": "NONE",
        "withdrawal_surface_projection_min_years": 10,
        "withdrawal_surface_start_years": 5,
        "withdrawal_surface_end_years": 50,
        "withdrawal_surface_step_years": 1,
        "cashflow_legs": [],
        "cashflow_type": None,
        "backtests": [
            {
                "invest_dividends": True,
                "rebalance_freq": "Monthly",
                "rebalance_offset": 0,
                "allocation": p["allocation_sim"],
                "drag": p["drag_pct"],
                "absolute_dev": 0,
                "relative_dev": 0,
            }
            for p in portfolios
        ],
    }


def _post(data: dict) -> dict:
    body = json.dumps(data).encode("utf-8")
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                API_BACKTEST,
                data=body,
                method="POST",
                headers={"content-type": "application/json", "user-agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            # On 400, try to extract the "errors" field if present
            try:
                err_json = json.loads(err_body)
                err_msg = err_json.get("errors") or err_body[:500]
            except json.JSONDecodeError:
                err_msg = err_body[:500]
            last_err = RuntimeError(f"HTTP {exc.code}: {err_msg}")
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
        time.sleep(2 ** (attempt + 1))
    raise RuntimeError(last_err)


def _equity_curve_to_returns(timestamps: list[float], curve: list[float]) -> pd.Series:
    """Convert testfol.io history pair (ts, equity-curve) into pd.Series of daily pct_change."""
    dates = pd.DatetimeIndex(pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None))
    equity = pd.Series(curve, index=dates, dtype=float).sort_index()
    equity = equity[~equity.index.duplicated(keep="last")]
    return equity.pct_change().dropna()


# ---------------------------------------------------------------------------
# Public sweep API
# ---------------------------------------------------------------------------


def run_sweep(
    portfolios: list[Portfolio],
    *,
    start_date: str = "2000-01-01",
    cache_dir: Path | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[dict]:
    """Run a sweep of portfolios via testfol.io API and return per-portfolio rows.

    Each row has: slug, label, drag_pct, allocation_sim, stats (testfol.io stats),
    window (start->end string), years (float), returns (pd.Series of daily pct_change).

    cache_dir, when set, persists the raw API response per batch to
    cache_dir/backtest_<a..>.json (idempotent re-runs read these).
    """
    if cache_dir is not None:
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for i in range(0, len(portfolios), batch_size):
        batch = portfolios[i:i + batch_size]
        letter = chr(ord("a") + i // batch_size)
        cache_path = (cache_dir / f"backtest_{letter}.json") if cache_dir else None

        # Pause between consecutive API calls — testfol.io anonymous endpoint
        # rate-limits bursts. Iter 047 used 5/min; we conservatively wait 3s
        # between batches.
        if i > 0:
            time.sleep(3)

        if cache_path and cache_path.exists():
            payload_cached = json.loads(cache_path.read_text())
            response = payload_cached["response"]
            cached_portfolios = payload_cached["portfolios"]
            # Sanity: cached batch must match current request signatures
            cached_sig = [(p["slug"], p["allocation_sim"]) for p in cached_portfolios]
            current_sig = [(p["slug"], p["allocation_sim"]) for p in batch]
            if cached_sig != current_sig:
                raise RuntimeError(
                    f"cache mismatch at {cache_path}: signatures differ — "
                    f"delete the cache file to refresh."
                )
        else:
            response = _post(_payload(batch, start_date=start_date))
            if response.get("errors"):
                raise RuntimeError(response["errors"])
            if cache_path:
                cache_path.write_text(
                    json.dumps({"portfolios": batch, "response": response}, indent=2)
                )

        history = response["charts"]["history"]
        if len(history) != len(batch) + 1:
            raise RuntimeError(
                f"history shape mismatch: got {len(history)} arrays, expected "
                f"{len(batch) + 1} (1 ts + {len(batch)} curves)"
            )
        timestamps = history[0]
        start = dt.datetime.fromtimestamp(timestamps[0], tz=dt.UTC).date()
        end = dt.datetime.fromtimestamp(timestamps[-1], tz=dt.UTC).date()
        years = (end - start).days / 365.25
        window_str = f"{start} -> {end} ({years:.2f}y)"

        for j, p in enumerate(batch):
            curve = history[j + 1]
            returns = _equity_curve_to_returns(timestamps, curve)
            stats = response["stats"][j]
            rows.append({
                "slug": p["slug"],
                "label": p["label"],
                "allocation_real": p["allocation_real"],
                "allocation_sim": p["allocation_sim"],
                "drag_pct": p["drag_pct"],
                "window": window_str,
                "years": years,
                "stats": stats,
                "returns": returns,
            })
    return rows


def attach_window_metrics(
    rows: list[dict],
    *,
    bench_slugs: list[str],
    windows_years: list[int] = DEFAULT_WINDOWS_YEARS,
) -> list[dict]:
    """For each row, attach `windows_beat[bench_slug][year_w]` = pct_strat_wins.

    bench_slugs must already exist in rows (the caller is responsible for
    including SPY_1x and any other reference portfolios in the same sweep).
    Each win pct is in [0, 1]; NaN if the dataset is too short for the window.
    """
    by_slug = {r["slug"]: r for r in rows}
    missing = [s for s in bench_slugs if s not in by_slug]
    if missing:
        raise KeyError(
            f"bench slugs {missing} not in sweep rows — include them in portfolios"
        )

    for r in rows:
        r["windows_beat"] = {}
        for bench in bench_slugs:
            br = by_slug[bench]["returns"]
            beats = rolling_outperformance_pct(
                strat_returns=r["returns"],
                bench_returns=br,
                windows_years=windows_years,
            )
            # serialize to nested dict[year_w_str -> pct_strat_wins float|None]
            r["windows_beat"][bench] = {
                str(w): (
                    None if np.isnan(d["pct_strat_wins"]) else d["pct_strat_wins"]
                )
                for w, d in beats.items()
            }
            r[f"windows_beat_{bench}_n"] = {
                str(w): d["n_windows"] for w, d in beats.items()
            }
    return rows


# ---------------------------------------------------------------------------
# Verdict + report writers
# ---------------------------------------------------------------------------


def _row_to_serializable(r: dict) -> dict:
    """Drop the pd.Series before JSON-dump — they're recoverable from the
    cached testfol.io response if needed."""
    out = {k: v for k, v in r.items() if k != "returns"}
    return out


def write_verdict(
    iter_dir: Path,
    iter_n: int,
    hypothesis_slug: str,
    rows: list[dict],
    *,
    bench_slugs: list[str],
    primary_citation: str,
) -> dict:
    """Write verdict.json + final_report.md for an iter."""
    iter_dir = Path(iter_dir)
    iter_dir.mkdir(parents=True, exist_ok=True)

    # Rank by Sharpe desc (then CAGR desc as tiebreaker).
    ranked = sorted(
        rows,
        key=lambda r: (-r["stats"]["sharpe"], -r["stats"]["cagr"]),
    )
    selected_slug = ranked[0]["slug"]

    verdict = {
        "iter_n": iter_n,
        "hypothesis_slug": hypothesis_slug,
        "primary_citation": primary_citation,
        "engine": "testfol.io API (consistent with iter 047/052)",
        "n_portfolios": len(rows),
        "selected_slug": selected_slug,
        "selection_rule": "max(sharpe), tiebreak max(cagr)",
        "bench_slugs": bench_slugs,
        "ranking": [_row_to_serializable(r) for r in ranked],
    }

    (iter_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=_default_json) + "\n"
    )

    _write_final_report(iter_dir, iter_n, hypothesis_slug, primary_citation, ranked, bench_slugs)
    return verdict


def _default_json(obj: Any) -> Any:
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, (pd.Timestamp,)):
        return str(obj.date())
    return str(obj)


def _write_final_report(
    iter_dir: Path,
    iter_n: int,
    slug: str,
    citation: str,
    ranked: list[dict],
    bench_slugs: list[str],
) -> None:
    today = dt.date.today().isoformat()
    lines = [
        f"# Iter {iter_n:03d} — `{slug}`",
        "",
        f"**Date:** {today}",
        f"**Engine:** testfol.io API",
        f"**Primary citation:** {citation}",
        "",
        f"**Selected:** `{ranked[0]['slug']}` ({ranked[0]['label']})",
        f"  CAGR {ranked[0]['stats']['cagr']:.2f}% / "
        f"MDD {ranked[0]['stats']['max_drawdown']:.2f}% / "
        f"Sharpe {ranked[0]['stats']['sharpe']:.3f} "
        f"on {ranked[0]['window']}",
        "",
        "## Ranking by Sharpe",
        "",
        "| # | slug | window | CAGR | MDD | Sharpe | Calmar | drag |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(ranked, 1):
        s = r["stats"]
        lines.append(
            f"| {i} | `{r['slug']}` | {r['window']} | "
            f"{s['cagr']:.2f}% | {s['max_drawdown']:.2f}% | "
            f"{s['sharpe']:.3f} | {s.get('calmar', 0):.3f} | "
            f"{r['drag_pct']:.3f}% |"
        )

    if ranked and "windows_beat" in ranked[0]:
        for bench in bench_slugs:
            lines += [
                "",
                f"## % rolling-windows beating `{bench}` (Sharpe-strat > Sharpe-bench)",
                "",
                "| slug | 3y | 5y | 10y | 15y |",
                "|---|---:|---:|---:|---:|",
            ]
            for r in ranked:
                wb = r["windows_beat"].get(bench, {})
                cells = []
                for w in ("3", "5", "10", "15"):
                    v = wb.get(w)
                    cells.append("n/a" if v is None else f"{v * 100:.1f}%")
                lines.append(f"| `{r['slug']}` | " + " | ".join(cells) + " |")

    lines += [
        "",
        "## Caveats / INCOMPLETE flags",
        "",
        "- BTGD synth uses spot BTC + spot Gold; real BTGD uses futures (roll cost ~3-5%/y in contango).",
        "- RSSX synth: 100% SPY + 100% (Gold 0.65 + BTC 0.35 by inverse-vol) − 1% borrow."
        " Inverse-vol weights are a 2026-05-05 snapshot — they drift with realized vol."
        " Gold/BTC futures roll cost not modeled.",
        "- IDMO/SPMO momentum overlay NOT modeled in static drag (uses real ETF history,"
        " limited to inception).",
        "- AVUV/AVDV/AVEM tilts injected via constant negative drag per literature midpoints"
        " (75/100/125bps); real Avantis ER + tilt may differ in execution.",
        "- AVNM synth blends VEASIM + VWOSIM at market-cap; ignores Avantis profitability"
        " + value tilts proprietary to AVNM.",
        "",
        "## Lesson",
        "",
        "(Append after manual review.)",
        "",
    ]
    (iter_dir / "final_report.md").write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# Convenience: SPY benchmark portfolio for embedding in sweeps
# ---------------------------------------------------------------------------


def spy_benchmark_portfolio() -> Portfolio:
    return make_portfolio("SPY_1x", "SPY 1x buy-and-hold", [(100, "SPY")])


def vt_benchmark_portfolio() -> Portfolio:
    """VT 1x buy-and-hold — uses VTSIM proxy for pre-2008 history."""
    # We use VTSIM directly (testfol.io supports it) rather than mapping
    # through MAPPINGS. ER 0.07% per VT prospectus.
    return {
        "slug": "VT_1x",
        "label": "VT 1x buy-and-hold (VTSIM)",
        "allocation_real": [(100, "VT")],
        "allocation_sim": {"VTSIM": 100.0},
        "drag_pct": 0.07,
    }
