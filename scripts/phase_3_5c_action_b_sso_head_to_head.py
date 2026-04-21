"""Ação B — Head-to-head analysis: leg_sso_only (regime-filtered) vs SSO buy-and-hold.

Question: is our low CAGR (~10-14%) because the regime filter is eating value,
or because of a strategy bug, or is the Phase 3.5b baseline inflated?

Method: use ONLY real post-inception data (yfinance SSO from 2006-06-21). Both
our cross-lib results and a naive buy-and-hold baseline are on the same source.
Divergence between them isolates the strategy logic's effect from data quality.

No investment decisions here — pure diagnostic.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from reports.phase_3_5c.cross_lib.data.reference_prices import load_reference_parquet


def cagr(equity: pd.Series) -> float:
    years = (equity.index[-1] - equity.index[0]).days / 365.25
    return (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1


def max_dd(equity: pd.Series) -> float:
    cummax = equity.cummax()
    dd = (equity - cummax) / cummax
    return dd.min()


def sharpe(returns: pd.Series) -> float:
    return (returns.mean() / returns.std()) * np.sqrt(252)


def analyze_window(label: str, sso_prices: pd.Series, our_equity: pd.Series) -> dict:
    """Compare SSO buy-and-hold vs our leg_sso_only strategy on the same window."""
    # Align windows
    start = max(sso_prices.index[0], our_equity.index[0])
    end = min(sso_prices.index[-1], our_equity.index[-1])
    sso = sso_prices.loc[start:end]
    ours = our_equity.loc[start:end]

    # Buy-and-hold SSO equity (normalized to $1)
    bh_equity = sso / sso.iloc[0]

    # Our equity (normalized to $1)
    ours_norm = ours / ours.iloc[0]

    bh_returns = bh_equity.pct_change().dropna()
    our_returns = ours_norm.pct_change().dropna()

    result = {
        "window": label,
        "start": str(start.date()),
        "end": str(end.date()),
        "years": (end - start).days / 365.25,
        "sso_buy_and_hold": {
            "cagr_pct": cagr(bh_equity) * 100,
            "max_dd_pct": max_dd(bh_equity) * 100,
            "sharpe": sharpe(bh_returns),
            "final_mult": float(bh_equity.iloc[-1]),
        },
        "our_leg_sso_only": {
            "cagr_pct": cagr(ours_norm) * 100,
            "max_dd_pct": max_dd(ours_norm) * 100,
            "sharpe": sharpe(our_returns),
            "final_mult": float(ours_norm.iloc[-1]),
        },
    }
    result["strategy_vs_bh_cagr_gap_pp"] = (
        result["our_leg_sso_only"]["cagr_pct"] - result["sso_buy_and_hold"]["cagr_pct"]
    )
    result["strategy_vs_bh_maxdd_gap_pp"] = (
        result["our_leg_sso_only"]["max_dd_pct"] - result["sso_buy_and_hold"]["max_dd_pct"]
    )
    return result


def spy_buy_and_hold_2x_naive(spy_prices: pd.Series) -> dict:
    """Naive 2× SPY buy-and-hold (ignoring decay/drag) — upper bound proxy for a perfect SSO."""
    spy = spy_prices / spy_prices.iloc[0]
    spy_returns = spy.pct_change().dropna()
    # Naive 2× daily returns (no cost)
    levered_returns = 2.0 * spy_returns
    levered_equity = (1 + levered_returns).cumprod()
    return {
        "cagr_pct": cagr(levered_equity) * 100,
        "max_dd_pct": max_dd(levered_equity) * 100,
        "sharpe": sharpe(levered_returns),
        "final_mult": float(levered_equity.iloc[-1]),
        "note": "Theoretical 2x SPY returns, no decay/drag. Actual SSO will be lower.",
    }


def main() -> None:
    # Load reference prices
    df = load_reference_parquet()

    sso = df[df["ticker"] == "SSO"].set_index("date")["close"].sort_index()
    sso.index = pd.to_datetime(sso.index)

    spy = df[df["ticker"] == "SPY"].set_index("date")["close"].sort_index()
    spy.index = pd.to_datetime(spy.index)

    print("=" * 78)
    print("Ação B: Head-to-head analysis — leg_sso_only vs SSO buy-and-hold")
    print("=" * 78)

    # Load our leg_sso_only equity curves
    windows_to_test = [
        ("canonical (stage_1)", "results/stage_1/bt/leg_sso_only/2004-10-01_2026-04-18"),
        ("extended (stage_1)", "results/stage_1/bt/leg_sso_only/1986-01-02_2026-04-18"),
        ("post_2009 (stage_1)", "results/stage_1/bt/leg_sso_only/2009-01-01_2026-04-18"),
        ("post_2009 (stage_2 yfinance)", "results/stage_2/bt/leg_sso_only/2009-01-01_2026-04-18"),
    ]

    root = Path("reports/phase_3_5c/cross_lib")

    all_results = []
    for label, rel in windows_to_test:
        parquet = root / rel / "equity.parquet"
        if not parquet.exists():
            print(f"\n[SKIP] {label}: equity.parquet not found at {parquet}")
            continue

        our_eq = pd.read_parquet(parquet)["equity"]
        our_eq.index = pd.to_datetime(our_eq.index)

        analysis = analyze_window(label, sso, our_eq)
        all_results.append(analysis)

        print(f"\n--- {label} ({analysis['start']} → {analysis['end']}, {analysis['years']:.1f}y) ---")
        bh = analysis["sso_buy_and_hold"]
        ours = analysis["our_leg_sso_only"]
        print(f"  SSO buy-and-hold:       CAGR = {bh['cagr_pct']:6.2f}%, max_dd = {bh['max_dd_pct']:7.2f}%, Sharpe = {bh['sharpe']:.2f}, final_mult = {bh['final_mult']:.2f}×")
        print(f"  Our leg_sso_only:       CAGR = {ours['cagr_pct']:6.2f}%, max_dd = {ours['max_dd_pct']:7.2f}%, Sharpe = {ours['sharpe']:.2f}, final_mult = {ours['final_mult']:.2f}×")
        print(f"  Strategy vs B&H gap:    CAGR {analysis['strategy_vs_bh_cagr_gap_pp']:+.2f} pp, max_dd {analysis['strategy_vs_bh_maxdd_gap_pp']:+.2f} pp")

    # Also the theoretical 2× SPY benchmark over the "all-real" SSO window
    print("\n" + "=" * 78)
    print("Benchmarks for context (SSO real inception window 2006-06-21 → 2026-04-18)")
    print("=" * 78)
    real_start = pd.Timestamp("2006-06-21")
    sso_real = sso.loc[real_start:]
    spy_same = spy.loc[real_start:sso_real.index[-1]]

    print(f"\nSSO buy-and-hold pure (real prices only, {real_start.date()} → {sso_real.index[-1].date()}):")
    bh_real = {
        "cagr_pct": cagr(sso_real) * 100,
        "max_dd_pct": max_dd(sso_real) * 100,
        "sharpe": sharpe(sso_real.pct_change().dropna()),
        "final_mult": float(sso_real.iloc[-1] / sso_real.iloc[0]),
    }
    print(f"  CAGR = {bh_real['cagr_pct']:.2f}%, max_dd = {bh_real['max_dd_pct']:.2f}%, Sharpe = {bh_real['sharpe']:.2f}, final_mult = {bh_real['final_mult']:.2f}×")

    naive_2x = spy_buy_and_hold_2x_naive(spy_same)
    print(f"\nNaive 2× SPY (daily, no decay) {real_start.date()} → {sso_real.index[-1].date()}:")
    print(f"  CAGR = {naive_2x['cagr_pct']:.2f}%, max_dd = {naive_2x['max_dd_pct']:.2f}%, Sharpe = {naive_2x['sharpe']:.2f}, final_mult = {naive_2x['final_mult']:.2f}×")
    print(f"  ({naive_2x['note']})")

    spy_bh = spy_same / spy_same.iloc[0]
    print(f"\nSPY buy-and-hold {real_start.date()} → {sso_real.index[-1].date()}:")
    print(f"  CAGR = {cagr(spy_bh)*100:.2f}%, max_dd = {max_dd(spy_bh)*100:.2f}%, Sharpe = {sharpe(spy_bh.pct_change().dropna()):.2f}, final_mult = {float(spy_bh.iloc[-1]):.2f}×")

    # --- Interpretation prints ---
    print("\n" + "=" * 78)
    print("Interpretation heuristics")
    print("=" * 78)
    print("""
Rule-of-thumb expectations over post-inception window (2006-06 → 2026-04, ~19.8y):
  - SPY buy-and-hold: ~10% CAGR, max_dd ~-55% (2008 GFC).
  - SSO buy-and-hold: ~11-14% CAGR (2× SPY with decay, real ETF), max_dd ~-85%.
  - EMA100-filtered SSO (skips worst drawdowns): ~15-25% CAGR, max_dd much lower.
  - Phase 3.5b letf_rotation_ema100_2x over 1970-2026: 44.69% CAGR — highly suspicious for a real ETF strategy.

If our leg_sso_only CAGR is near SSO buy-and-hold:
  → Regime filter neither helps nor hurts. Possibly our SSO implementation is
    just holding SSO always. Check trade count.

If our leg_sso_only CAGR is much lower than SSO buy-and-hold:
  → Regime filter is hurting (spending time in cash during bull periods)
    OR there's a bug (e.g., signal applied with wrong sign, or executed on wrong bar).

If our leg_sso_only max_dd is much better than SSO buy-and-hold:
  → Filter works for drawdown protection but maybe at too high a cost in return.
""")


if __name__ == "__main__":
    main()
