"""Phase 3.6 Family K — cross-lib concordance check (gate 9).

Reconciles the canonical Family K daily returns against an independent
pure-pandas reimplementation of the Donchian + ATR-trail portfolio
layer. Gate 9 requires that an independent implementation re-produce
the canonical OOS CAGR within ±3pp.

Approach
--------

Two implementations of the portfolio layer, sharing the same ATR
primitive (``compute_atr_wilder``) but rebuilding the Donchian breakout
detection, trail-stop loop, and cost decomposition from scratch:

1. **Canonical** (``simulate_universal_trend``): vectorized numpy per-bar
   loop with in-simulator entry/exit + ATR-distance trail + gross cap +
   spread/swap/commission decomposition.

2. **Hand-rolled**: re-uses :func:`compute_atr_wilder` (so the ATR
   primitive is identical) but rebuilds Donchian-channel computation,
   trail-stop state machine, and cost decomposition with explicit
   pandas operations (rolling.max().shift(1), explicit prev_weight ×
   ret alignment, separate spread/commission/swap series).

Any |Δ CAGR| > 3pp isolates portfolio-wiring bugs (not signal bugs).

vectorbt / bt / backtrader ports are not produced: those libraries do
not expose primitives for ATR-distance trailing stops with risk-fraction
position sizing on a multi-asset basket — porting would re-implement the
pipeline inside the library's custom-indicator API, yielding a copy of
our own code with a thin wrapper rather than independent verification.
This matches the methodology used by Family E, F, H, J in this same
phase.

Citations
---------
* Cross-lib concordance requirement: [advances_fin_ml, p.31-34].
* Penfold Donchian + ATR trail primitives: [universal_trend_tactics,
  p.295-299, p.338-343].
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.strategies.phase3_6_k_universal_trend import (  # noqa: E402
    UniversalTrendConfig,
    compute_atr_wilder,
    simulate_universal_trend,
)

OUT_DIR = ROOT / "reports/phase_3_6/k_universal_trend"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"
OOS_RANGE = ("2018-01-01", "2023-12-31")

UNIVERSE = ("SPY", "QQQ", "EFA", "EEM", "TLT", "IEF", "GLD", "SLV", "USO")

WINNER_CFG = UniversalTrendConfig(
    donchian_lookback=50,
    atr_period=14,
    atr_multiplier=3.0,
    risk_per_position=0.005,
    rebalance_days=1,
    max_gross_exposure=1.0,
)


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


def _slice(s: pd.Series, start: str, end: str) -> pd.Series:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return s.loc[(s.index >= a) & (s.index <= b)]


def _hand_rolled_portfolio(
    panel: dict[str, pd.DataFrame],
    cfg: UniversalTrendConfig,
) -> pd.Series:
    """Pure-pandas reimplementation of the Donchian + ATR-trail portfolio.

    Re-uses the canonical :func:`compute_atr_wilder` primitive only — the
    rest of the portfolio loop is rewritten from scratch using explicit
    pandas operations + a per-asset Python state machine, with no shared
    code paths to ``simulate_universal_trend``.
    """
    tickers = sorted(panel.keys())
    union_idx_set: set[pd.Timestamp] = set()
    closes_raw: dict[str, pd.Series] = {}
    highs_raw: dict[str, pd.Series] = {}
    lows_raw: dict[str, pd.Series] = {}
    adj_raw: dict[str, pd.Series] = {}
    for t in tickers:
        d = panel[t].copy()
        d.index = pd.DatetimeIndex(d.index).normalize()
        d = d[~d.index.duplicated(keep="last")].sort_index()
        closes_raw[t] = d["close"].astype(float)
        highs_raw[t] = d["high"].astype(float)
        lows_raw[t] = d["low"].astype(float)
        adj_raw[t] = d["adj_close"].astype(float)
        union_idx_set.update(d.index.tolist())

    union_idx = pd.DatetimeIndex(sorted(union_idx_set))
    union_idx = union_idx[union_idx.dayofweek < 5]

    close_df = pd.DataFrame(
        {t: closes_raw[t].reindex(union_idx) for t in tickers}, index=union_idx
    )
    high_df = pd.DataFrame(
        {t: highs_raw[t].reindex(union_idx) for t in tickers}, index=union_idx
    )
    low_df = pd.DataFrame(
        {t: lows_raw[t].reindex(union_idx) for t in tickers}, index=union_idx
    )
    adj_df = pd.DataFrame(
        {t: adj_raw[t].reindex(union_idx) for t in tickers}, index=union_idx
    )
    ret_df = adj_df.pct_change(fill_method=None)

    # ATR per asset (Wilder, shared primitive — only line in common).
    atr_cols: dict[str, pd.Series] = {}
    for t in tickers:
        atr_cols[t] = compute_atr_wilder(
            high_df[t].dropna(),
            low_df[t].dropna(),
            close_df[t].dropna(),
            period=cfg.atr_period,
        ).reindex(union_idx)
    atr_df = pd.DataFrame(atr_cols, index=union_idx)
    atr_prev = atr_df.shift(1)

    # Donchian channel high (from highs, exclusive of bar t).
    don_cols: dict[str, pd.Series] = {}
    for t in tickers:
        don_cols[t] = (
            high_df[t]
            .rolling(window=cfg.donchian_lookback, min_periods=cfg.donchian_lookback)
            .max()
            .shift(1)
        )
    don_df = pd.DataFrame(don_cols, index=union_idx)

    # Per-asset state machine (independent loop, distinct from canonical).
    n_bars = len(union_idx)
    n_assets = len(tickers)
    weight_arr = np.zeros((n_bars, n_assets), dtype=float)
    in_pos = [False] * n_assets
    trail_max = [0.0] * n_assets

    close_v = close_df.to_numpy()
    atr_p_v = atr_prev.to_numpy()
    don_v = don_df.to_numpy()

    last_signal = -cfg.rebalance_days
    for ti in range(n_bars):
        signal_bar = (ti - last_signal) >= cfg.rebalance_days
        if signal_bar:
            last_signal = ti
        for i in range(n_assets):
            c = close_v[ti, i]
            ap = atr_p_v[ti, i]
            dn = don_v[ti, i]
            if not np.isfinite(c):
                if in_pos[i]:
                    in_pos[i] = False
                continue
            if in_pos[i]:
                # Stop check (always live).
                if np.isfinite(ap) and ap > 0:
                    stop = trail_max[i] - cfg.atr_multiplier * ap
                    if c < stop:
                        in_pos[i] = False
                        weight_arr[ti, i] = 0.0
                        continue
                # Hold + update trail.
                weight_arr[ti, i] = weight_arr[ti - 1, i] if ti > 0 else 0.0
                if c > trail_max[i]:
                    trail_max[i] = c
            else:
                if not signal_bar:
                    weight_arr[ti, i] = 0.0
                    continue
                if (
                    np.isfinite(dn)
                    and np.isfinite(ap)
                    and ap > 0
                    and c > dn
                ):
                    in_pos[i] = True
                    trail_max[i] = c
                    pos_w = (
                        cfg.risk_per_position * c / (cfg.atr_multiplier * ap)
                    )
                    weight_arr[ti, i] = pos_w
                else:
                    weight_arr[ti, i] = 0.0

    weights = pd.DataFrame(weight_arr, index=union_idx, columns=tickers)
    gross = weights.abs().sum(axis=1)
    scale = np.minimum(1.0, cfg.max_gross_exposure / gross.replace(0.0, np.nan))
    scale = scale.fillna(1.0)
    weights = weights.mul(scale, axis=0)

    prev_w = weights.shift(1).fillna(0.0)
    per_asset = prev_w * ret_df.fillna(0.0)
    gross_ret = per_asset.sum(axis=1)

    w_change = (weights - weights.shift(1).fillna(0.0)).abs()
    spread_drag = pd.Series(0.0, index=union_idx)
    for t in tickers:
        s_one_way = float(cfg.spread_one_way.get(t, 0.00025))
        spread_drag = spread_drag + w_change[t] * s_one_way
    commission_drag = w_change.sum(axis=1) * cfg.commission_round_trip
    long_ex = prev_w.clip(lower=0.0).sum(axis=1)
    swap_drag = long_ex * abs(cfg.swap_daily_long)

    return gross_ret - spread_drag - commission_drag - swap_drag


def main() -> None:
    print("=" * 80)
    print("Phase 3.6 Family K — cross-lib concordance (gate 9)")
    print("=" * 80)

    panel = {t: _load(t) for t in UNIVERSE}
    cfg = WINNER_CFG

    canonical = simulate_universal_trend(panel, cfg).daily_returns.dropna()
    hand = _hand_rolled_portfolio(panel, cfg).dropna()

    common = canonical.index.intersection(hand.index)
    c_oos = _slice(canonical.loc[common], *OOS_RANGE)
    h_oos = _slice(hand.loc[common], *OOS_RANGE)

    cagr_c = _cagr(c_oos)
    cagr_h = _cagr(h_oos)
    delta_pp = abs(cagr_c - cagr_h) * 100

    print(
        f"Canonical OOS CAGR:  {cagr_c*100:+.3f}%   |   "
        f"Hand-rolled OOS CAGR: {cagr_h*100:+.3f}%   Δ={delta_pp:.3f}pp"
    )

    pass_tol = delta_pp <= 3.0
    print(f"Gate 9 (≤3pp): {'PASS' if pass_tol else 'FAIL'}")

    out_md = OUT_DIR / "cross_lib_check.md"
    out_md.write_text(
        "# Cross-lib concordance — Family K Universal Trend Tactics\n\n"
        f"- Winner cell: **Donchian-50, ATR(14)×3.0, risk 0.5%/leg, 1d cadence**\n"
        f"- OOS window: {OOS_RANGE[0]} → {OOS_RANGE[1]}\n"
        f"- Canonical OOS CAGR: **{cagr_c*100:+.3f}%**\n"
        f"- Hand-rolled (pure-pandas) OOS CAGR: **{cagr_h*100:+.3f}%**\n"
        f"- |Δ|: **{delta_pp:.3f}pp** (tolerance ≤ 3pp)\n"
        f"- Gate 9 verdict: **{'PASS' if pass_tol else 'FAIL'}**\n\n"
        "## Notes\n\n"
        "Two independent implementations of the Family K portfolio layer:\n\n"
        "1. Canonical: `simulate_universal_trend` — vectorized numpy per-bar\n"
        "   loop with in-simulator entry / ATR-trail exit / gross cap +\n"
        "   swap/spread/commission decomposition.\n"
        "2. Hand-rolled: re-uses `compute_atr_wilder` (so the ATR primitive\n"
        "   is identical) but rebuilds Donchian-channel detection, trail-\n"
        "   stop state machine, and cost decomposition with explicit pandas\n"
        "   operations.\n\n"
        "Both implementations apply the Pepperstone Razor cost model (plan\n"
        "§3.1): per-ticker spread, 3.5e-5 round-trip commission, 0.03%/night\n"
        "swap on long notional. Any non-trivial Δ isolates portfolio-wiring\n"
        "bugs (not signal bugs).\n\n"
        "vectorbt / bt / backtrader ports were NOT produced because:\n\n"
        "- Those libraries do not expose primitives for ATR-distance\n"
        "  trailing stops with risk-fraction position sizing on a multi-\n"
        "  asset basket. Porting would re-implement the pipeline inside\n"
        "  the library's custom-indicator API — yielding a copy of our own\n"
        "  code with a thin wrapper, not independent verification.\n"
        "- The OOS verdict is FAIL on 10 binding gates — additional\n"
        "  library ports cannot rescue a family where the basket of\n"
        "  Donchian breakouts produces only Sharpe ≈ 0.39 / CAGR ≈ 1.9%\n"
        "  OOS after Pepperstone retail costs.\n\n"
        "## Citations\n\n"
        "- Lookahead audit: `[advances_fin_ml, p.31-34]`.\n"
        "- Penfold Donchian + ATR trail primitives: `[universal_trend_\n"
        "  tactics, p.295-299, p.338-343]`.\n"
    )
    print(f"[write] {out_md}")

    out_json = OUT_DIR / "cross_lib_check.json"
    out_json.write_text(
        json.dumps(
            {
                "winner_cell": "don50_k3.0_r0050bp_rb1",
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
