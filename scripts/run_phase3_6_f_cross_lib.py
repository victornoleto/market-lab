"""Phase 3.6 Family F — cross-lib concordance check (gate 9).

Reconciles the canonical Family F daily returns against a second,
independent pure-pandas implementation of the same vol-target-MF
pipeline. Gate 9 requires that an independent implementation re-produce
the canonical OOS CAGR within ±3pp.

Approach
--------

Two implementations of the portfolio layer, sharing the same Carver
EWMAC forecast primitive (`compute_ewmac_forecast`):

1. **Canonical** (`simulate_vol_target_mf`): vectorized numpy per-bar
   loop applying inertia + cadence + gross-leverage cap + swap/spread/
   commission decomposition as per module docstring.

2. **Hand-rolled**: separate pure-pandas re-implementation that
   re-computes EWMAC forecasts (shared primitive), rolls its own σ
   EWMA, builds targets with the same Carver sizing formula, then
   rebuilds the portfolio-layer state loop from scratch with explicit
   pandas operations (per-bar shift-by-one, explicit weight-change
   cost, no in-loop optimization).

Any |Δ CAGR| > 3pp isolates portfolio-wiring bugs (not signal bugs),
since the DSP primitive is shared. This matches the Phase 3.6 gate 9
methodology demonstrated by Family E.

vectorbt / bt / backtrader ports are not produced: these libs do not
expose a primitive for Carver vol-target sizing with IDM + position
inertia, so a port would re-implement the pipeline from scratch in
the library's indicator-API style — no additional independence gained
vs a pure-pandas reimplementation.

Citations
---------
* Cross-lib concordance requirement: [advances_fin_ml, p.31-34].
* Carver EWMAC + vol-target primitives: [systematic_trading, p.282-285,
  p.159-173].
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

from ai_trade.backtest.strategies.phase3_6_f_vol_target_managed_futures import (  # noqa: E402
    EWMAC_SCALARS,
    VolTargetMFConfig,
    compute_ewmac_forecast,
    simulate_vol_target_mf,
)

OUT_DIR = ROOT / "reports/phase_3_6/f_vol_target_managed_futures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TIINGO_DAILY = ROOT / "data/tiingo/daily/prices"
OOS_RANGE = ("2018-01-01", "2023-12-31")

UNIVERSE = ("SPY", "TLT", "GLD", "USO", "EFA", "IEF")

WINNER_CFG = VolTargetMFConfig(
    fast_span=16,
    slow_span=64,
    target_vol_annual=0.15,
    rebalance_days=10,
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
    cfg: VolTargetMFConfig,
) -> pd.Series:
    """Pure-pandas reimplementation of Family F portfolio layer.

    Shares :func:`compute_ewmac_forecast` with the canonical simulator
    (signal primitive) but rebuilds target-sizing + portfolio state
    from scratch. Any |Δ| in CAGR isolates portfolio-wiring bugs.
    """
    tickers = sorted(panel.keys())

    # Build prices + returns matrix (weekdays only).
    price_cols = {}
    for t in tickers:
        p = panel[t]["adj_close"].astype(float).copy()
        p.index = pd.DatetimeIndex(p.index).normalize()
        p = p[~p.index.duplicated(keep="last")].sort_index()
        price_cols[t] = p
    prices = pd.concat(price_cols, axis=1).sort_index()
    prices = prices[prices.index.dayofweek < 5]
    returns = prices.pct_change(fill_method=None)

    # Forecasts (shared primitive).
    f_cols = {}
    for t in tickers:
        p = prices[t].dropna()
        f = compute_ewmac_forecast(
            p,
            cfg.fast_span,
            cfg.slow_span,
            cfg.ewmac_scalar,
            cfg.sigma_ewma_span,
            cfg.forecast_cap,
        )
        f_cols[t] = f.reindex(prices.index)
    forecasts = pd.concat(f_cols, axis=1)

    # Annualised EWMA σ of returns.
    sigma_cols = {}
    for t in tickers:
        sigma_cols[t] = returns[t].ewm(span=cfg.sigma_ewma_span, adjust=False).std() * np.sqrt(252)
    sigmas = pd.concat(sigma_cols, axis=1)

    # Shift by 1 to avoid lookahead.
    f_prev = forecasts.shift(1)
    s_prev = sigmas.shift(1)

    active = (
        f_prev.notna()
        & s_prev.notna()
        & (s_prev > 0)
        & returns.notna()
    )
    n_active = active.sum(axis=1)
    idm = n_active.astype(float).pow(0.5).clip(upper=cfg.idm_cap)

    # Target weights (Carver formula).
    raw = (
        cfg.target_vol_annual * f_prev * idm.values.reshape(-1, 1)
    ) / (
        n_active.replace(0, np.nan).values.reshape(-1, 1)
        * s_prev.replace(0, np.nan)
        * 10.0
    )
    raw = raw.where(active, 0.0).fillna(0.0)
    raw = raw.clip(lower=-cfg.max_per_leg, upper=cfg.max_per_leg)
    raw.loc[n_active < cfg.min_active_assets] = 0.0

    # Gross-leverage cap.
    gross = raw.abs().sum(axis=1)
    scale = np.minimum(
        1.0, cfg.max_gross_leverage / gross.replace(0.0, np.nan)
    ).fillna(1.0)
    raw = raw.mul(scale, axis=0)

    # Cadence + inertia loop (hand-rolled).
    n_bars = len(prices.index)
    n_assets = len(tickers)
    current = np.zeros(n_assets, dtype=float)
    last_rebal = -cfg.rebalance_days
    weights_arr = np.zeros((n_bars, n_assets), dtype=float)
    raw_arr = raw.values
    for t_idx in range(n_bars):
        target = raw_arr[t_idx]
        if (t_idx - last_rebal) >= cfg.rebalance_days:
            delta = target - current
            significance = np.maximum(np.abs(current), np.abs(target))
            threshold = cfg.inertia_frac * significance
            near_zero = significance < 1e-10
            move_mask = (np.abs(delta) > threshold) | near_zero
            new_w = np.where(move_mask, target, current)
            if np.any(new_w != current):
                last_rebal = t_idx
            current = new_w
        weights_arr[t_idx] = current

    weights = pd.DataFrame(weights_arr, index=prices.index, columns=tickers)
    prev_w = weights.shift(1).fillna(0.0)

    # Per-asset gross contribution.
    per_asset = prev_w * returns.fillna(0.0)
    gross_ret = per_asset.sum(axis=1)

    # Cost: spread on |Δw|, commission on |Δw|, swap on long/short notional.
    w_change = (weights - weights.shift(1).fillna(0.0)).abs()
    spread_drag = pd.Series(0.0, index=prices.index)
    for t in tickers:
        s_t = cfg.spread_one_way.get(t, 0.00025)
        spread_drag = spread_drag + w_change[t] * s_t
    commission_drag = w_change.sum(axis=1) * cfg.commission_round_trip
    long_ex = prev_w.clip(lower=0.0).sum(axis=1)
    short_ex = (-prev_w.clip(upper=0.0)).sum(axis=1)
    swap_drag = (
        long_ex * abs(cfg.swap_daily_long)
        + short_ex * abs(cfg.swap_daily_short)
    )
    return gross_ret - spread_drag - commission_drag - swap_drag


def main() -> None:
    print("=" * 80)
    print("Phase 3.6 Family F — cross-lib concordance (gate 9)")
    print("=" * 80)

    panel = {t: _load(t) for t in UNIVERSE}
    cfg = WINNER_CFG

    canonical = simulate_vol_target_mf(panel, cfg).daily_returns.dropna()
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
        "# Cross-lib concordance — Family F vol-target managed futures basket\n\n"
        f"- Winner cell: **EWMAC 16:64, vol_target=15%, rebal=10d**\n"
        f"- OOS window: {OOS_RANGE[0]} → {OOS_RANGE[1]}\n"
        f"- Canonical OOS CAGR: **{cagr_c*100:+.3f}%**\n"
        f"- Hand-rolled (pure-pandas) OOS CAGR: **{cagr_h*100:+.3f}%**\n"
        f"- |Δ|: **{delta_pp:.3f}pp** (tolerance ≤ 3pp)\n"
        f"- Gate 9 verdict: **{'PASS' if pass_tol else 'FAIL'}**\n\n"
        "## Notes\n\n"
        "Two independent implementations of the Family F portfolio layer:\n\n"
        "1. Canonical: `simulate_vol_target_mf` — vectorized numpy per-bar\n"
        "   loop with in-simulator inertia + cadence + gross-leverage cap\n"
        "   + swap/spread/commission decomposition.\n"
        "2. Hand-rolled: re-uses `compute_ewmac_forecast` (so the Carver\n"
        "   EWMAC primitive is identical) but rebuilds σ-EWMA, target\n"
        "   sizing, cadence loop, and cost decomposition from scratch using\n"
        "   pure-pandas ops.\n\n"
        "Both implementations apply the Pepperstone Razor cost model (plan\n"
        "§3.1): per-ticker spread, 3.5e-5 round-trip commission, 0.03%/night\n"
        "swap on long notional. Any non-trivial Δ isolates portfolio-wiring\n"
        "bugs (not signal bugs).\n\n"
        "vectorbt / bt / backtrader ports were NOT produced because:\n\n"
        "- Those libraries do not expose a primitive for Carver vol-target\n"
        "  sizing with IDM (instrument diversification multiplier) and\n"
        "  position inertia. Porting would require implementing the full\n"
        "  pipeline inside the library's custom-indicator API — yielding a\n"
        "  copy of our own code with a thin wrapper, not an independent\n"
        "  implementation.\n"
        "- The OOS verdict is FAIL on 12 binding gates (swap drag dominates:\n"
        "  311% cumulative swap cost over 25 years at 2.22× average gross\n"
        "  leverage). Additional library ports cannot rescue a family where\n"
        "  the gross-return Sharpe is 0.60 pre-cost and the cost model\n"
        "  erases it.\n\n"
        "## Citations\n\n"
        "- Lookahead audit: `[advances_fin_ml, p.31-34]`.\n"
        "- Carver EWMAC + vol-target primitives: `[systematic_trading,\n"
        "  p.282-285, p.159-173]`.\n"
    )
    print(f"[write] {out_md}")

    out_json = OUT_DIR / "cross_lib_check.json"
    out_json.write_text(
        json.dumps(
            {
                "winner_cell": "ewmac16_64_vt15_rb10",
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
