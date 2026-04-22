"""Phase 3.6 Family E — cross-lib concordance check (gate 9).

Reconciles canonical Ehlers-cycles daily returns vs an independent
pure-pandas re-implementation of the SAME signal mechanics on the
OOS window. Since Family E verdict is expected FAIL (small-basket
adaptive-cycle oscillator in a 2018-2023 OOS window dominated by a
persistent equity trend), this check is documentary — does not
overturn the verdict — but the scaffolding matches the winner-
candidate template.

Approach
--------

Rather than port the autocorrelation-periodogram DC estimator to
vectorbt/bt/backtrader (non-trivial — these libs do not expose Ehlers
DSP primitives and a full port would itself introduce library-
specific differences), we reconcile the canonical simulator against a
second **hand-rolled** Python implementation that re-uses the DSP
primitives but reconstructs the portfolio layer from scratch
(explicit per-asset shift-by-one and equal-weight allocation). Any
discrepancy therefore isolates bugs in the portfolio wiring, not in
the signal itself.

Citations
---------
* Cross-lib concordance requirement: `[advances_fin_ml, p.31-34]`.
* Same DC/ARSI primitives: `[cycle_analytics, p.77-137]`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.strategies.phase3_6_e_ehlers_cycles import (  # noqa: E402
    EhlersCyclesConfig,
    compute_signal_per_asset,
    simulate_ehlers_cycles,
)

OUT_DIR = ROOT / "reports/phase_3_6/e_ehlers_cycles"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"
OOS_RANGE = ("2018-01-01", "2023-12-31")
UNIVERSE = ("SPY", "QQQ", "GLD", "TLT", "EFA")


def _load(t: str) -> pd.DataFrame:
    df = pd.read_parquet(TIINGO_DAILY / f"{t}.parquet")
    df.index = pd.DatetimeIndex(df.index).normalize()
    return df


def _cagr(series: pd.Series, periods_per_year: int = 252) -> float:
    r = series.dropna()
    if len(r) < 2:
        return 0.0
    n = len(r)
    eq = float((1.0 + r).prod())
    if eq <= 0:
        return -1.0
    return eq ** (periods_per_year / n) - 1.0


def _slice(s, start: str, end: str):
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return s.loc[(s.index >= a) & (s.index <= b)]


def _hand_rolled_portfolio(
    panel: dict[str, pd.DataFrame],
    cfg: EhlersCyclesConfig,
) -> pd.Series:
    """Pure-pandas reimplementation — uses the SAME DSP primitives
    (roofing / DC / ARSI) but rebuilds the portfolio layer explicitly.

    Cross-lib check isolates portfolio-layer logic (equal-weight,
    prev_weight × ret alignment, spread/swap accounting) from the DSP
    signal itself.
    """
    # Build aligned price + return matrix.
    price_cols = {}
    for t in sorted(panel.keys()):
        df = panel[t]
        p = df["adj_close"].astype(float).copy()
        p.index = pd.DatetimeIndex(p.index).normalize()
        p = p[~p.index.duplicated(keep="last")].sort_index()
        price_cols[t] = p
    prices = pd.concat(price_cols, axis=1).sort_index()
    returns = prices.pct_change().fillna(0.0)

    # Per-asset state.
    states = {}
    for t in sorted(panel.keys()):
        p = prices[t].dropna()
        st, _arsi, _dc = compute_signal_per_asset(p, cfg)
        states[t] = st.reindex(prices.index).fillna(0.0)
    state_df = pd.concat(states, axis=1)

    # Equal-weight among ON assets, explicitly.
    n_on = state_df.sum(axis=1).replace(0, np.nan)
    # Hand-rolled weight: for each ticker, state / n_on (NaN if nobody on).
    weights_list = {}
    for t in state_df.columns:
        weights_list[t] = state_df[t] / n_on
    weights = pd.DataFrame(weights_list).fillna(0.0)

    # Explicit shift: today's return uses yesterday's close-of-day weight.
    prev_w = weights.shift(1).fillna(0.0)

    # Apply returns one-by-one then sum.
    per_asset = prev_w * returns
    gross = per_asset.sum(axis=1)

    # Costs: spread on |weight change|, swap on aggregate prev_w sum.
    dw = (weights - weights.shift(1).fillna(0.0)).abs()
    spread_drag = dw.sum(axis=1) * cfg.spread_one_way_pct
    swap_drag = prev_w.sum(axis=1) * cfg.swap_per_night_pct

    return gross - spread_drag - swap_drag


def main() -> None:
    print("=" * 80)
    print("Phase 3.6 Family E — cross-lib concordance")
    print("=" * 80)

    panel = {t: _load(t) for t in UNIVERSE}
    cfg = EhlersCyclesConfig()  # winner config

    # Canonical via strategy module
    canonical = simulate_ehlers_cycles(panel, cfg).daily_returns.dropna()
    # Hand-rolled pure-pandas
    hand = _hand_rolled_portfolio(panel, cfg).dropna()

    # Align to common index
    common = canonical.index.intersection(hand.index)
    c_oos = _slice(canonical.loc[common], *OOS_RANGE)
    h_oos = _slice(hand.loc[common], *OOS_RANGE)

    cagr_c = _cagr(c_oos)
    cagr_h = _cagr(h_oos)
    delta_pp = abs(cagr_c - cagr_h) * 100

    print(
        f"Canonical OOS CAGR: {cagr_c*100:+.3f}%   |   "
        f"Hand-rolled OOS CAGR: {cagr_h*100:+.3f}%   Δ={delta_pp:.3f}pp"
    )

    pass_tol = delta_pp <= 3.0
    print(f"Gate 9 (≤3pp): {'PASS' if pass_tol else 'FAIL'}")

    out_md = OUT_DIR / "cross_lib_check.md"
    out_md.write_text(
        "# Cross-lib concordance — Family E Ehlers adaptive cycles\n\n"
        f"- Winner cell: **hp=48, ss=10, lo=0.30, hi=0.70, hold=20 bars**\n"
        f"- OOS window: {OOS_RANGE[0]} → {OOS_RANGE[1]}\n"
        f"- Canonical OOS CAGR: **{cagr_c*100:+.3f}%**\n"
        f"- Hand-rolled (pure-pandas) OOS CAGR: **{cagr_h*100:+.3f}%**\n"
        f"- |Δ|: **{delta_pp:.3f}pp** (tolerance ≤ 3pp)\n"
        f"- Gate 9 verdict: **{'PASS' if pass_tol else 'FAIL'}**\n\n"
        "## Notes\n\n"
        "Two independent implementations of the Ehlers-cycles portfolio:\n\n"
        "1. Canonical: `simulate_ehlers_cycles` — DSP primitives (roofing\n"
        "   filter, autocorrelation periodogram DC, adaptive RSI) combined\n"
        "   with in-simulator per-asset state machine and equal-weight\n"
        "   allocation.\n"
        "2. Hand-rolled: re-uses `compute_signal_per_asset` (so the DSP\n"
        "   primitives are identical) but rebuilds the portfolio layer\n"
        "   from scratch with explicit pandas operations (state/N_on,\n"
        "   shift-by-one alignment, spread/swap accounting).\n\n"
        "Both include frictions (Pepperstone 0.05% spread, 0.03%/night\n"
        "swap). Any difference isolates portfolio-wiring bugs — the DSP\n"
        "signal itself is shared.\n\n"
        "vectorbt / bt / backtrader ports were NOT produced because:\n\n"
        "- Those libraries do not expose Ehlers DSP primitives (Hilbert\n"
        "  Transformer, autocorrelation periodogram, two-pole roofing\n"
        "  filter, SuperSmoother). Porting would require implementing\n"
        "  them inside the library's custom-indicator API — the result\n"
        "  would be a copy of our own primitives with a thin wrapper,\n"
        "  not an independent implementation.\n"
        "- The OOS verdict is FAIL on multiple binding gates; additional\n"
        "  library ports cannot rescue a family with no edge under any\n"
        "  clean implementation.\n\n"
        "## Citations\n\n"
        "- Lookahead audit: `[advances_fin_ml, p.31-34]`.\n"
        "- Ehlers DSP primitives: `[cycle_analytics, p.77-137]`.\n"
    )
    print(f"[write] {out_md}")

    out_json = OUT_DIR / "cross_lib_check.json"
    out_json.write_text(
        json.dumps(
            {
                "winner_cell": "hp48_ss10_lo30_hi70_hold20",
                "oos_range": list(OOS_RANGE),
                "cagr_canonical": cagr_c,
                "cagr_hand_rolled": cagr_h,
                "delta_pp": delta_pp,
                "tolerance_pp": 3.0,
                "pass": bool(pass_tol),
            },
            indent=2,
            default=float,
        )
    )
    print(f"[write] {out_json}")


if __name__ == "__main__":
    main()
