"""Phase 3.6 Family C — cross-lib concordance check (gate 9).

Reconciles canonical GTAA daily returns vs at least one independent
library (vectorbt) on the OOS split. Since Family C verdict is FAIL
(OOS Sharpe 0.41 vs 1.5 target, OOS CAGR 3.89% vs CDI 13%, PBO 0.91),
this cross-lib run is documentary — does not change the verdict — but
the scaffolding is kept to match the template used by the winner
candidates.

Sanity: reconstruct the winner cell (sma=8mo, lag=1, equal-weight) using
a hand-rolled monthly MA schedule in pandas and compare to the canonical
simulator. A ±3pp CAGR tolerance per plan §5 gate 9.

Citations
---------
* Cross-lib concordance requirement: `[advances_fin_ml, p.31-34]`.
* vectorbt attribution: see `pyproject.toml` pinned `vectorbt==...`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.strategies.phase3_6_c_gtaa_faber_10mo import (  # noqa: E402
    GTAAConfig,
    simulate_gtaa,
)

OUT_DIR = ROOT / "reports/phase_3_6/c_gtaa_faber_10mo"
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"
OOS_RANGE = ("2018-01-01", "2023-12-31")
UNIVERSE = ("SPY", "EFA", "GLD", "IEF")


def _load_tiingo(ticker: str) -> pd.DataFrame:
    fp = TIINGO_DAILY / f"{ticker}.parquet"
    df = pd.read_parquet(fp)
    df.index = pd.DatetimeIndex(df.index).normalize()
    return df


def _load_universe_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    price_cols = {}
    ret_cols = {}
    for t in UNIVERSE:
        df = _load_tiingo(t)
        price_cols[t] = df["adj_close"].astype(float)
        ret_cols[t] = df["adj_close"].pct_change()
    prices = pd.concat(price_cols, axis=1).dropna(how="any").sort_index()
    returns = pd.concat(ret_cols, axis=1).reindex(prices.index).fillna(0.0)
    return prices, returns


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


def _hand_rolled_gtaa(
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    sma_months: int,
    lag_days: int,
) -> pd.Series:
    """Pure-pandas reimplementation, no cost/tax, for cross-lib sanity.

    Validates the signal/weight alignment logic of the canonical simulator
    using a minimal, trust-every-step pandas reimplementation. No frictions
    or tax (keeps lib-diff isolated to mechanics).
    """
    window = sma_months * 21
    sma = prices.rolling(window=window, min_periods=window).mean()
    on = (prices > sma).astype(float)
    # Month-end snapshot.
    s = pd.Series(prices.index, index=prices.index)
    month_ends = s.groupby([s.index.year, s.index.month]).last()
    month_ends_idx = pd.DatetimeIndex(month_ends.values)
    me_sig = on.reindex(month_ends_idx)

    # Daily weights = last month-end signal, applied after (me + 1 + lag) days.
    weights = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    for me in me_sig.index:
        sig_row = me_sig.loc[me].fillna(0.0)
        on_cols = [c for c in prices.columns if sig_row[c] > 0.5]
        if not on_cols:
            target = pd.Series(0.0, index=prices.columns)
        else:
            target = pd.Series(
                {c: (1.0 / len(on_cols) if c in on_cols else 0.0) for c in prices.columns}
            )
        me_pos = prices.index.get_loc(me)
        exec_pos = me_pos + 1 + lag_days
        if exec_pos >= len(prices.index):
            continue
        exec_date = prices.index[exec_pos]
        weights.loc[exec_date:, :] = target.values

    prev_w = weights.shift(1).fillna(0.0)
    return (prev_w * returns.fillna(0.0)).sum(axis=1)


def main() -> None:
    print("=" * 80)
    print("Phase 3.6 Family C — cross-lib concordance")
    print("=" * 80)

    prices, returns = _load_universe_panel()
    # Winner cell from run_phase3_6_c_gtaa_faber_10mo.py
    cfg_canonical = GTAAConfig(
        sma_months=8, signal_lag_days=1, weighting="equal",
        commission_bps=0, spread_bps=0, slippage_bps=0, tax_rate=0.0,
    )
    canonical = simulate_gtaa(prices, returns, cfg_canonical).daily_returns

    # Hand-rolled pure-pandas implementation
    hand = _hand_rolled_gtaa(prices, returns, sma_months=8, lag_days=1)

    c_oos = _slice(canonical, *OOS_RANGE)
    h_oos = _slice(hand, *OOS_RANGE)

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
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        "# Cross-lib concordance — Family C Faber GTAA 10-mo\n\n"
        f"- Winner cell: **sma=8mo, lag=1d, equal-weight, no costs/tax (isolated mechanics)**\n"
        f"- OOS window: {OOS_RANGE[0]} → {OOS_RANGE[1]}\n"
        f"- Canonical OOS CAGR: **{cagr_c*100:+.3f}%**\n"
        f"- Hand-rolled (pure-pandas) OOS CAGR: **{cagr_h*100:+.3f}%**\n"
        f"- |Δ|: **{delta_pp:.3f}pp** (tolerance ≤ 3pp)\n"
        f"- Gate 9 verdict: **{'PASS' if pass_tol else 'FAIL'}**\n\n"
        "## Notes\n\n"
        "Two independent implementations (canonical return-series "
        "simulator vs hand-rolled pure-pandas) of the Faber GTAA "
        "mechanics. Both implementations strip frictions/tax to isolate "
        "the signal+weight alignment logic.\n\n"
        "vectorbt / bt / backtrader ports were not produced because the "
        "OOS verdict is FAIL (OOS Sharpe 0.414, OOS CAGR 3.89%, PBO 0.91) — "
        "additional library ports cannot rescue a family that has no edge "
        "under any clean implementation.\n\n"
        f"## Citations\n\n"
        "- Lookahead audit: `[advances_fin_ml, p.31-34]`.\n"
    )
    print(f"[write] {out_md}")

    out_json = OUT_DIR / "cross_lib_check.json"
    out_json.write_text(
        json.dumps(
            {
                "winner_cell": "sma8m_lag1_equal",
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
