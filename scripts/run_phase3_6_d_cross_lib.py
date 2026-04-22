"""Phase 3.6 Family D — cross-lib concordance check (gate 9).

Reconciles canonical Chan MR-pairs daily returns against a hand-rolled
pure-pandas reimplementation on the OOS split. The two implementations
are independent of each other: the canonical one uses pandas rolling
primitives and a custom coint cycle; the hand-rolled one recomputes OLS
window-by-window without rolling helpers.

Since Family D verdict is FAIL (OOS Sharpe −0.511, OOS CAGR −0.33%, OOS
bootstrap CI [−1.37, 0.50] straddling zero, and DSR p=0.996), this
cross-lib run is documentary: ±3pp tolerance is trivially satisfied
when both return streams are close to zero, but the result cannot
rescue the edge-side failures. Scaffolding preserved to match the
template the winner candidates will use.

Citations
---------
* Cross-lib concordance requirement: `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.strategies.phase3_6_d_chan_mr_pairs import (  # noqa: E402
    ChanPairsConfig,
    DEFAULT_PAIRS,
    simulate_chan_pairs,
)

OUT_DIR = ROOT / "reports/phase_3_6/d_chan_mr_pairs"
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"
OOS_RANGE = ("2018-01-01", "2023-12-31")
TICKERS = ["XLE", "USO", "TLT", "IEF", "HYG", "LQD", "GLD", "SLV", "XLU", "XLP"]


def _load_tiingo(ticker: str) -> pd.DataFrame:
    fp = TIINGO_DAILY / f"{ticker}.parquet"
    df = pd.read_parquet(fp)
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


def _hand_rolled_one_pair(
    py: pd.Series,
    px: pd.Series,
    ry: pd.Series,
    rx: pd.Series,
    lookback: int,
    entry_z: float,
    exit_z: float,
    stop_z: float,
    per_pair_gross: float,
    spread: float,
    commission: float,
    swap: float,
) -> pd.Series:
    """Hand-rolled implementation of one pair's daily return.

    Intentionally avoids pandas rolling helpers — instead loops with
    explicit window slices each bar. Skips the EG coint gate (sets
    `coint_ok = True` always) to isolate the signal/cost/alignment
    mechanics from the coint test. This means cross-lib checks the
    hedge-ratio + z-score + entry/exit engine but not the rolling coint
    decision.
    """
    log_y = np.log(py.values.astype(float))
    log_x = np.log(px.values.astype(float))
    n = len(log_y)
    beta = np.full(n, np.nan)
    alpha = np.full(n, np.nan)
    resid = np.full(n, np.nan)
    zsc = np.full(n, np.nan)
    for t in range(lookback - 1, n):
        lo = t - lookback + 1
        yw = log_y[lo : t + 1]
        xw = log_x[lo : t + 1]
        mx = np.mean(xw)
        my = np.mean(yw)
        vx = np.var(xw, ddof=1)
        if vx == 0:
            continue
        cxy = np.mean((xw - mx) * (yw - my)) * lookback / (lookback - 1)
        b = cxy / vx
        a = my - b * mx
        beta[t] = b
        alpha[t] = a
        # residual series over the whole window
        rw = yw - a - b * xw
        rmu = np.mean(rw)
        rsd = np.std(rw, ddof=1)
        if rsd == 0:
            continue
        resid[t] = rw[-1]
        zsc[t] = (rw[-1] - rmu) / rsd

    beta_s = pd.Series(beta, index=py.index)
    z_s = pd.Series(zsc, index=py.index)
    # shift by 1 for look-ahead discipline
    z_lag = z_s.shift(1)
    beta_lag = beta_s.shift(1)

    # position logic — matches canonical
    pos = np.zeros(n)
    prev = 0.0
    for i in range(n):
        z = z_lag.iloc[i]
        if np.isnan(z):
            pos[i] = 0.0
            prev = 0.0
            continue
        if abs(z) > stop_z:
            new = 0.0
        elif prev == 0.0:
            if z < -entry_z:
                new = 1.0
            elif z > entry_z:
                new = -1.0
            else:
                new = 0.0
        elif prev > 0:
            new = 0.0 if z >= -exit_z else 1.0
        else:
            new = 0.0 if z <= exit_z else -1.0
        pos[i] = new
        prev = new
    position = pd.Series(pos, index=py.index)

    beta_for_ret = beta_lag.fillna(0.0).clip(-5.0, 5.0)
    ry_a = ry.reindex(py.index).fillna(0.0)
    rx_a = rx.reindex(py.index).fillna(0.0)
    spread_ret = ry_a - beta_for_ret * rx_a

    pos_lag = position.shift(1).fillna(0.0)
    gross = pos_lag * spread_ret * per_pair_gross

    pos_change = (position - position.shift(1)).abs().fillna(0.0)
    cost_impact = pos_change * 2.0 * (spread + commission) * per_pair_gross
    swap_impact = position.abs() * 2.0 * swap * per_pair_gross
    return gross - cost_impact - swap_impact


def main() -> None:
    print("=" * 80)
    print("Phase 3.6 Family D — cross-lib concordance")
    print("=" * 80)

    # Load pair panel
    prices: dict[str, pd.Series] = {}
    returns: dict[str, pd.Series] = {}
    for t in TICKERS:
        df = _load_tiingo(t)
        prices[t] = df["adj_close"].astype(float)
        returns[t] = prices[t].pct_change()

    cfg = ChanPairsConfig(
        lookback=126, entry_z=2.0, exit_z=0.0, stop_z=4.0,
        # Disable coint gate for cross-lib: we're checking signal+cost+
        # alignment engine, not the EG test itself. Canonical also run
        # with coint_pvalue_gate=1.0 for apples-to-apples comparison.
        coint_pvalue_gate=1.0,
    )
    canonical = simulate_chan_pairs(
        prices, returns, cfg, pairs=DEFAULT_PAIRS
    ).daily_returns

    # Hand-rolled per-pair sum
    idx = canonical.index
    hand_total = pd.Series(0.0, index=idx)
    for p in DEFAULT_PAIRS:
        py = prices[p.y].reindex(idx).astype(float)
        px = prices[p.x].reindex(idx).astype(float)
        ry = returns[p.y].reindex(idx).astype(float)
        rx = returns[p.x].reindex(idx).astype(float)
        hand_total = hand_total + _hand_rolled_one_pair(
            py, px, ry, rx,
            lookback=cfg.lookback,
            entry_z=cfg.entry_z, exit_z=cfg.exit_z, stop_z=cfg.stop_z,
            per_pair_gross=cfg.per_pair_gross_pct,
            spread=cfg.spread_one_way_pct,
            commission=cfg.commission_per_trade_pct,
            swap=cfg.swap_per_night_pct,
        )

    c_oos = _slice(canonical, *OOS_RANGE)
    h_oos = _slice(hand_total, *OOS_RANGE)

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
        "# Cross-lib concordance — Family D Chan MR pairs (non-Kalman)\n\n"
        f"- Winner cell: **lookback=126, entry_z=2.0, exit_z=0.0, stop_z=4.0, "
        f"coint_gate=1.0 (disabled for cross-lib)**\n"
        f"- OOS window: {OOS_RANGE[0]} → {OOS_RANGE[1]}\n"
        f"- Canonical OOS CAGR: **{cagr_c*100:+.3f}%**\n"
        f"- Hand-rolled (pure-numpy) OOS CAGR: **{cagr_h*100:+.3f}%**\n"
        f"- |Δ|: **{delta_pp:.3f}pp** (tolerance ≤ 3pp)\n"
        f"- Gate 9 verdict: **{'PASS' if pass_tol else 'FAIL'}**\n\n"
        "## Notes\n\n"
        "Two independent implementations of the Chan pairs mechanics:\n\n"
        "- **Canonical:** pandas rolling helpers (`.rolling().mean()`, "
        "`.rolling().var()`, covariance via `E[xy] - E[x]E[y]`) in "
        "`src/ai_trade/backtest/strategies/phase3_6_d_chan_mr_pairs.py`.\n"
        "- **Hand-rolled:** explicit window slices with numpy mean/var "
        "(Bessel-corrected) per bar. No pandas rolling primitives.\n\n"
        "The EG cointegration gate is disabled for the comparison "
        "(coint_gate=1.0) — we are checking the signal + hedge-ratio + "
        "entry/exit + cost engine, not the stat test. That isolates the "
        "arithmetic reconciliation from stochastic branches.\n\n"
        "vectorbt / bt / backtrader ports were not produced because the "
        "OOS verdict is FAIL across every binding edge gate (Sharpe, "
        "CAGR, DSR p-value, bootstrap CI, IR vs SPY, cost×2 sensitivity). "
        "Additional library ports cannot rescue a family that has no "
        "edge under any clean implementation.\n\n"
        "## Citations\n\n"
        "- Lookahead audit: `[advances_fin_ml, p.31-34]`.\n"
        "- Chan pairs mechanics: `[algo_trading_chan, p.51-54, p.71-73]`.\n"
    )
    print(f"[write] {out_md}")

    out_json = OUT_DIR / "cross_lib_check.json"
    out_json.write_text(
        json.dumps(
            {
                "winner_cell": "lb126_enter2.0_exit0.0_stop4.0_coint_off",
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
