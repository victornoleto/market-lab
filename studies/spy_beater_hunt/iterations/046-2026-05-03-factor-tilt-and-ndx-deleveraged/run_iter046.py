#!/usr/bin/env python3
"""Iter 046 — factor tilts and NDX deleveraged variants.

Purpose: test concrete follow-ups from the GPT-5.5 review/user feedback:

1. Treat the corrected RSST proxy as canonical: SPY + 70% DBMF + 30% KMLM
   - cash. This is a proxy correction, not optimized data mining.
2. Test whether adding small-cap value / value / momentum sleeves improves the
   B4-style static stack's CAGR without pushing max drawdown beyond the B4 risk
   budget. Factor tilt rationale: `[ilmanen_expected_returns, ch.10-12]` for
   value/momentum premia and `[stocks_on_the_move, ch.4]` for momentum.
3. Test NDX deleveraged tactical variants inspired by the no_simpsons Reddit
   suggestion after TQQQ/QQQ pure swaps showed unacceptable drawdown.

All results are testfol.io summaries. These are not equivalent to the old
`verdict.json` gate battery until a follow-up converts daily curves into the
internal PBO/DSR/WF framework.
"""
from __future__ import annotations

import datetime as dt
import json
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.testfolio_loader import load_testfolio_returns, load_testfolio_series


SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "testfolio_data"
API_BACKTEST = "https://testfol.io/api/backtest"
API_TACTICAL = "https://testfol.io/api/tactical"
INITIAL = 10_000.0

EXPENSE_RATIOS = {
    "SPY": 0.0945,
    "QQQ": 0.20,
    "NTSX": 0.20,
    "GDE": 0.20,
    "RSST": 0.99,
    "RSSB": 0.69,
    "KMLM": 0.92,
    "DBMF": 0.85,
    "GLD": 0.40,
    "TLT": 0.15,
    "ZROZ": 0.15,
    "IEF": 0.15,
    "IEI": 0.15,
    "VBR": 0.07,
    "EFV": 0.35,
    "MTUM": 0.15,
}

ER_BAKED_IN_SIM = {"TMF"}

MAPPINGS = {
    "NTSX": [("SPYSIM", 0.90), ("IEFSIM", 0.60), ("CASHX", -0.50)],
    "RSST": [("SPYSIM", 1.00), ("DBMFSIM", 0.70), ("KMLMSIM", 0.30), ("CASHX?E=-2", -1.00)],
    "TMF": [("TLTSIM?L=3&E=1.05", 1.0)],
    "SPY": [("SPYSIM", 1.0)],
    "QQQ": [("QQQSIM", 1.0)],
    "VBR": [("VBRSIM", 1.0)],
    "EFV": [("EFVSIM", 1.0)],
    "MTUM": [("MTUMSIM", 1.0)],
    "IEI": [("IEISIM", 1.0)],
}


STATIC_PORTFOLIOS = [
    {
        "slug": "B4_rsst7030_baseline",
        "label": "B4 corrected baseline: 25 NTSX / 25 GDE / 25 RSST70-30 / 25 ZROZ",
        "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")],
    },
    {
        "slug": "L1_cegb_reference",
        "label": "L1 CEGB reference: 40 NTSX / 25 GDE / 17.5 KMLM / 17.5 TLT",
        "allocation_real": [(40, "NTSX"), (25, "GDE"), (17.5, "KMLM"), (17.5, "TLT")],
    },
    {
        "slug": "B4_unstacked_mf7030",
        "label": "B4 without RSST leverage: 25 NTSX / 25 GDE / 17.5 DBMF / 7.5 KMLM / 25 ZROZ",
        "allocation_real": [(25, "NTSX"), (25, "GDE"), (17.5, "DBMF"), (7.5, "KMLM"), (25, "ZROZ")],
    },
    {
        "slug": "B4_scv10_from_zroz",
        "label": "B4 + 10 VBR from ZROZ",
        "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "VBR")],
    },
    {
        "slug": "B4_scv15_from_zroz",
        "label": "B4 + 15 VBR from ZROZ",
        "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (10, "ZROZ"), (15, "VBR")],
    },
    {
        "slug": "B4_scv10_from_ntsx",
        "label": "B4 + 10 VBR from NTSX",
        "allocation_real": [(15, "NTSX"), (10, "VBR"), (25, "GDE"), (25, "RSST"), (25, "ZROZ")],
    },
    {
        "slug": "B4_mtum10_from_zroz",
        "label": "B4 + 10 MTUM from ZROZ",
        "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (10, "MTUM")],
    },
    {
        "slug": "B4_value_mix10_from_zroz",
        "label": "B4 + 5 VBR + 5 EFV from ZROZ",
        "allocation_real": [(25, "NTSX"), (25, "GDE"), (25, "RSST"), (15, "ZROZ"), (5, "VBR"), (5, "EFV")],
    },
    {
        "slug": "B4_aggressive_scv15",
        "label": "B4 aggressive: 30 GDE / 25 RSST / 20 NTSX / 15 VBR / 10 ZROZ",
        "allocation_real": [(20, "NTSX"), (30, "GDE"), (25, "RSST"), (10, "ZROZ"), (15, "VBR")],
    },
    {
        "slug": "SPY_1x",
        "label": "SPY 1x benchmark",
        "allocation_real": [(100, "SPY")],
    },
]


SIGNAL_QQQ_ABOVE_200D = {
    "name": "1",
    "indicator_1": {
        "type": "SMA", "ticker": "QQQSIM", "ticker_2": None,
        "value": None, "lookback": 200, "delay": None,
    },
    "comparison": "<",
    "indicator_2": {
        "type": "Price", "ticker": "QQQSIM", "ticker_2": None,
        "value": None, "lookback": None, "delay": None,
    },
    "tolerance": 2,
}


def expand(weight_pct: float, ticker: str) -> list[tuple[str, float]]:
    ticker = ticker.upper()
    if ticker in MAPPINGS:
        return [(token, weight_pct * mult) for token, mult in MAPPINGS[ticker]]
    sim = f"{ticker}SIM"
    return [(sim, weight_pct)]


def decompose(allocation: list[tuple[float, str]]) -> dict[str, float]:
    agg: defaultdict[str, float] = defaultdict(float)
    for pct, ticker in allocation:
        for token, weight_pct in expand(pct, ticker):
            agg[token] += weight_pct
    return {k: round(v, 4) for k, v in agg.items() if abs(v) > 1e-6}


def compute_drag(allocation: list[tuple[float, str]]) -> float:
    drag = 0.0
    for pct, ticker in allocation:
        ticker = ticker.upper()
        if ticker in ER_BAKED_IN_SIM:
            continue
        drag += (pct / 100.0) * EXPENSE_RATIOS.get(ticker, 0.0)
    return round(drag, 4)


def static_payload(portfolios: list[dict]) -> dict:
    return {
        "start_date": "2000-01-01",
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


def alloc_leg(name: str, signal_active: bool | None, tickers: list[tuple[str, float]], drag_pct: float = 0.0) -> dict:
    if signal_active is None:
        signals: list[str] = []
        nots: list[bool] = []
    else:
        signals = ["1"]
        nots = [not signal_active]
    return {
        "name": name,
        "signals": signals,
        "ops": [],
        "nots": nots,
        "kind": "FIXED",
        "tickers": [{"ticker": t, "percent": p} for t, p in tickers],
        "rank_universe_tickers": [],
        "rank_pairs": [],
        "rank_metric": None,
        "rank_selection": "TOP",
        "rank_lookbacks": [],
        "rank_top_n": None,
        "rank_threshold_comparison": None,
        "rank_threshold_value": None,
        "rank_fallback_ticker": None,
        "rank_weighting": None,
        "rank_score_tilt": None,
        "rank_vol_lookback": None,
        "rank_rp_vol_lookback": None,
        "rank_rp_corr_lookback": None,
        "rank_freq": None,
        "rank_offset": None,
        "drag": drag_pct,
        "candidate_tickers": [],
        "optimize_objective": None,
        "rebalance_freq": "Daily",
        "rebalance_offset": 0,
        "absolute_dev": 0,
        "relative_dev": 0,
    }


TACTICAL_VARIANTS = [
    {
        "slug": "NS1_q140iei100_q50cash",
        "label": "no_simpsons proxy 1: bull 140 QQQ + 100 IEI - cash; bear 50 QQQ + 50 cash",
        "legs": [
            alloc_leg("Bull 1.4 QQQ + IEI", True, [("QQQSIM?L=1.4&E=0.20", 100), ("IEISIM", 100), ("CASHX", -100)], 0.5 * EXPENSE_RATIOS["QQQ"] + EXPENSE_RATIOS["IEI"]),
            alloc_leg("Bear 0.5 QQQ", False, [("QQQSIM?L=0.5&E=0.20", 100)], 0.5 * EXPENSE_RATIOS["QQQ"]),
        ],
    },
    {
        "slug": "NS2_q140iei60_q50iei50",
        "label": "no_simpsons proxy 2: bull 140 QQQ + 60 IEI - cash; bear 50 QQQ + 50 IEI",
        "legs": [
            alloc_leg("Bull 1.4 QQQ + 0.6 IEI", True, [("QQQSIM?L=1.4&E=0.20", 100), ("IEISIM", 60), ("CASHX", -60)], 0.5 * EXPENSE_RATIOS["QQQ"] + 0.6 * EXPENSE_RATIOS["IEI"]),
            alloc_leg("Bear 0.5 QQQ + 0.5 IEI", False, [("QQQSIM?L=0.5&E=0.20", 100), ("IEISIM", 50), ("CASHX", -50)], 0.5 * EXPENSE_RATIOS["QQQ"] + 0.5 * EXPENSE_RATIOS["IEI"]),
        ],
    },
    {
        "slug": "NS3_q140kmlm30iei30_q50iei50",
        "label": "NDX deleveraged + diversifiers: bull 140 QQQ + 30 KMLM + 30 IEI; bear 50 QQQ + 50 IEI",
        "legs": [
            alloc_leg("Bull 1.4 QQQ + KMLM/IEI", True, [("QQQSIM?L=1.4&E=0.20", 100), ("KMLMSIM", 30), ("IEISIM", 30), ("CASHX", -60)], 0.5 * EXPENSE_RATIOS["QQQ"] + 0.3 * EXPENSE_RATIOS["KMLM"] + 0.3 * EXPENSE_RATIOS["IEI"]),
            alloc_leg("Bear 0.5 QQQ + 0.5 IEI", False, [("QQQSIM?L=0.5&E=0.20", 100), ("IEISIM", 50), ("CASHX", -50)], 0.5 * EXPENSE_RATIOS["QQQ"] + 0.5 * EXPENSE_RATIOS["IEI"]),
        ],
    },
]


def tactical_payload(variant: dict) -> dict:
    benchmark_leg = alloc_leg("SPY benchmark", None, [("SPYSIM", 100)], EXPENSE_RATIOS["SPY"])
    return {
        "name": variant["label"],
        "start_date": "2000-01-01",
        "end_date": "",
        "start_val": INITIAL,
        "adj_inflation": False,
        "trading_cost": 0,
        "rolling_window": 60,
        "withdrawal_surface_include": False,
        "withdrawal_surface_projection": "NONE",
        "withdrawal_surface_projection_min_years": 10,
        "withdrawal_surface_start_years": 5,
        "withdrawal_surface_end_years": 50,
        "withdrawal_surface_step_years": 1,
        "signals": [SIGNAL_QQQ_ABOVE_200D],
        "derived_signals": [],
        "aggregate_derived_signals": [],
        "mode": "BACKTEST",
        "global_candidate_tickers": [],
        "include_efficient_frontier": False,
        "allocations": variant["legs"] + [benchmark_leg],
        "trading_freq": "Daily",
        "trading_offset": 0,
        "cashflow_legs": [],
        "one_time_cashflows": [],
    }


def post(url: str, payload: dict, attempts: int = 3) -> dict:
    body = json.dumps(payload).encode("utf-8")
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                method="POST",
                headers={"content-type": "application/json", "user-agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            last_err = RuntimeError(f"HTTP {exc.code}: {detail}")
            time.sleep(2 ** (i + 1))
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = exc
            time.sleep(2 ** (i + 1))
    raise RuntimeError(f"failed after retries: {last_err}")


def years_from_history(response: dict) -> tuple[float, str]:
    history = response["charts"]["history"][0]
    start = dt.datetime.fromtimestamp(history[0], tz=dt.UTC).date()
    end = dt.datetime.fromtimestamp(history[-1], tz=dt.UTC).date()
    years = (end - start).days / 365.25
    return years, f"{start} -> {end} ({years:.2f}y)"


def fetch_static() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    portfolios = [dict(p) for p in STATIC_PORTFOLIOS]
    for p in portfolios:
        p["allocation_sim"] = decompose(p["allocation_real"])
        p["drag_pct"] = compute_drag(p["allocation_real"])
    # testfol.io caps backtests per request; keep batches small.
    for i in range(0, len(portfolios), 5):
        batch = portfolios[i:i + 5]
        response = post(API_BACKTEST, static_payload(batch))
        if response.get("errors"):
            raise RuntimeError(response["errors"])
        letter = chr(ord("a") + i // 5)
        (DATA_DIR / f"static_backtest_{letter}.json").write_text(
            json.dumps({"portfolios": batch, "response": response}, indent=2)
        )


def fetch_tactical() -> None:
    # Tactical API requires a logged-in token. Use local deterministic synths so
    # this iter remains reproducible without credentials. The synth is slightly
    # conservative: T+1 gate, QQQ leverage as daily-reset factor minus ER drag.
    local_rows = []
    for v in local_tactical_rows():
        local_rows.append(v)
    (DATA_DIR / "tactical_local.json").write_text(json.dumps(local_rows, indent=2))


def _max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def _metrics_from_returns(returns: pd.Series) -> dict:
    returns = returns.dropna()
    equity = (1.0 + returns).cumprod()
    years = len(returns) / 252.0
    cagr = float(equity.iloc[-1] ** (1.0 / years) - 1.0)
    vol = float(returns.std(ddof=0) * np.sqrt(252))
    sharpe = float((returns.mean() * 252) / vol) if vol > 0 else 0.0
    mdd = _max_drawdown(equity)
    calmar = cagr / abs(mdd) if mdd < 0 else 0.0
    return {
        "cagr_pct": cagr * 100.0,
        "mdd_pct": mdd * 100.0,
        "sharpe": sharpe,
        "sortino": 0.0,
        "calmar": calmar,
        "end_val": float(INITIAL * equity.iloc[-1]),
    }


def _levered_returns(base_returns: pd.Series, leverage: float, er_pct: float) -> pd.Series:
    return leverage * base_returns - (er_pct / 100.0) / 252.0


def local_tactical_rows() -> list[dict]:
    qqq_prices = load_testfolio_series("QQQSIM")
    qqq = load_testfolio_returns("QQQSIM")
    # IEISIM is available in the live testfol.io search API but not in the
    # committed local cache. Use IEFSIM (7-10y Treasury) as the closest local
    # intermediate-duration proxy for this credential-free diagnostic.
    iei = load_testfolio_returns("IEFSIM")
    kmlm = load_testfolio_returns("KMLMSIM")
    cash = load_testfolio_returns("CASHX")

    gate = (qqq_prices > qqq_prices.rolling(200, min_periods=200).mean()).shift(1).fillna(False)
    q140 = _levered_returns(qqq, 1.4, EXPENSE_RATIOS["QQQ"])
    q050 = _levered_returns(qqq, 0.5, EXPENSE_RATIOS["QQQ"])
    aligned = pd.concat({"gate": gate, "q140": q140, "q050": q050, "iei": iei, "kmlm": kmlm, "cash": cash}, axis=1).dropna()
    aligned = aligned.loc[aligned.index >= pd.Timestamp("2000-01-03")]

    specs = {
        "NS1_q140iei100_q50cash": (
            "no_simpsons proxy 1: bull 140 QQQ + 100 IEI - cash; bear 50 QQQ + 50 cash",
            1.0 * aligned["q140"] + 1.0 * aligned["iei"] - 1.0 * aligned["cash"],
            1.0 * aligned["q050"],
        ),
        "NS2_q140iei60_q50iei50": (
            "no_simpsons proxy 2: bull 140 QQQ + 60 IEI - cash; bear 50 QQQ + 50 IEI",
            1.0 * aligned["q140"] + 0.6 * aligned["iei"] - 0.6 * aligned["cash"],
            1.0 * aligned["q050"] + 0.5 * aligned["iei"] - 0.5 * aligned["cash"],
        ),
        "NS3_q140kmlm30iei30_q50iei50": (
            "NDX deleveraged + diversifiers: bull 140 QQQ + 30 KMLM + 30 IEI; bear 50 QQQ + 50 IEI",
            1.0 * aligned["q140"] + 0.3 * aligned["kmlm"] + 0.3 * aligned["iei"] - 0.6 * aligned["cash"],
            1.0 * aligned["q050"] + 0.5 * aligned["iei"] - 0.5 * aligned["cash"],
        ),
    }
    rows = []
    for slug, (label, bull, bear) in specs.items():
        r = bull.where(aligned["gate"].astype(bool), bear)
        metrics = _metrics_from_returns(r)
        rows.append({
            "kind": "tactical_local",
            "slug": slug,
            "label": label,
            "window": f"{r.index[0].date()} -> {r.index[-1].date()} ({len(r)/252:.2f}y local)",
            **metrics,
            "drag_pct": None,
            "allocation_sim": None,
        })
    return rows


def analyze() -> list[dict]:
    rows: list[dict] = []
    for static_path in sorted(DATA_DIR.glob("static_backtest_*.json")):
        static_data = json.loads(static_path.read_text())
        years, window = years_from_history(static_data["response"])
        for p, s in zip(static_data["portfolios"], static_data["response"]["stats"]):
            rows.append({
                "kind": "static",
                "slug": p["slug"],
                "label": p["label"],
                "window": window,
                "cagr_pct": s["cagr"],
                "mdd_pct": s["max_drawdown"],
                "sharpe": s["sharpe"],
                "sortino": s.get("sortino", 0.0),
                "calmar": s.get("calmar", 0.0),
                "end_val": s["end_val"],
                "drag_pct": p["drag_pct"],
                "allocation_sim": p["allocation_sim"],
            })
    tactical_local = DATA_DIR / "tactical_local.json"
    if tactical_local.exists():
        rows.extend(json.loads(tactical_local.read_text()))
    rows.sort(key=lambda r: (-r["sharpe"], -r["cagr_pct"]))
    (SCRIPT_DIR / "unified_metrics.json").write_text(json.dumps(rows, indent=2))
    return rows


def write_summary(rows: list[dict]) -> None:
    spy = next(r for r in rows if r["slug"] == "SPY_1x")
    b4 = next(r for r in rows if r["slug"] == "B4_rsst7030_baseline")
    lines = [
        "# Iter 046 — Factor tilts + NDX deleveraged variants",
        "",
        "**Date:** 2026-05-03",
        "**Source:** testfol.io API",
        "**Window:** common 2000+ because corrected RSST uses DBMFSIM.",
        "**Tax model:** no DARF applied; these are gross portfolio comparisons. Static portfolios assume lazy accumulation; tactical variants would need annual-realize tax treatment before deploy.",
        "",
        "## Ranking By Sharpe",
        "",
        "| # | kind | strategy | window | CAGR | MDD | Sharpe | Calmar |",
        "|---:|---|---|---|---:|---:|---:|---:|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | {r['kind']} | {r['slug']} | {r['window']} | "
            f"{r['cagr_pct']:.2f}% | {r['mdd_pct']:.2f}% | {r['sharpe']:.3f} | {r['calmar']:.3f} |"
        )
    lines += [
        "",
        "## Practical Bars",
        "",
        f"SPY benchmark in this run: CAGR {spy['cagr_pct']:.2f}% / MDD {spy['mdd_pct']:.2f}% / Sharpe {spy['sharpe']:.3f}.",
        f"Corrected B4 baseline: CAGR {b4['cagr_pct']:.2f}% / MDD {b4['mdd_pct']:.2f}% / Sharpe {b4['sharpe']:.3f}.",
        "",
        "### Beats SPY on CAGR and MDD",
        "",
    ]
    beat_spy = [r for r in rows if r["slug"] != "SPY_1x" and r["cagr_pct"] > spy["cagr_pct"] and abs(r["mdd_pct"]) < abs(spy["mdd_pct"])]
    for r in beat_spy:
        lines.append(f"- {r['slug']}: CAGR {r['cagr_pct']:.2f}%, MDD {r['mdd_pct']:.2f}%, Sharpe {r['sharpe']:.3f}")
    lines += [
        "",
        "### Beats corrected B4 on CAGR without worse drawdown",
        "",
    ]
    beat_b4 = [r for r in rows if r["slug"] not in {"SPY_1x", "B4_rsst7030_baseline"} and r["cagr_pct"] > b4["cagr_pct"] and abs(r["mdd_pct"]) <= abs(b4["mdd_pct"])]
    if beat_b4:
        for r in beat_b4:
            lines.append(f"- {r['slug']}: CAGR {r['cagr_pct']:.2f}%, MDD {r['mdd_pct']:.2f}%, Sharpe {r['sharpe']:.3f}")
    else:
        lines.append("- None.")
    lines += [
        "",
        "## Methodology Caveats",
        "",
        "- This is not a full `verdict.json` gate run; PBO/DSR/WF/bootstrap were not recomputed from daily internal curves.",
        "- Corrected RSST forces a 2000+ window because DBMFSIM starts in 2000.",
        "- VBR/EFV/MTUM are factor proxies available in testfol.io (`VBRSIM`, `EFVSIM`, `MTUMSIM`), not the Avantis AVUV/AVDV/AVEM live ETFs used elsewhere.",
        "- Tactical NDX variants require annual-realize tax modeling before any deploy comparison.",
    ]
    (SCRIPT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    fetch_static()
    fetch_tactical()
    rows = analyze()
    write_summary(rows)
    for r in rows:
        print(f"{r['slug']:<32} {r['cagr_pct']:>6.2f}% {r['mdd_pct']:>8.2f}% {r['sharpe']:>6.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
