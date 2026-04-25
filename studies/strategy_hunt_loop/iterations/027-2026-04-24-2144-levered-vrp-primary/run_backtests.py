"""Iter 027 — Levered VRP-primary on 3 datasets (`harvest_notional=3.5`).

Single pre-committed cfg ``vrp_primary_h3_5_5_10_1m``. The mechanism is
identical to iter 026; only the harvest_notional changes from 1.0 to
3.5. Cumulative n_trials advance: 4279 → 4280 (+1).

Reuses iter 026's `vrp_primary.py` (function
``compute_vrp_primary_returns``) and `numpy_reference_vrp.py` for G7
parity — both accept ``harvest_notional`` as a parameter, no fork
needed.

Citations
---------
* `[volatility_trading, ch.3]` — VRP mechanics.
* `[volatility_trading, p.41]` — capped-tail.
* `[risk_parity, p.5]` — Asness-Frazzini-Pedersen 2012 levered low-vol.
* `[advances_fin_ml, p.31-34]` — cross-library parity.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]

# Reuse iter 026's primary + numpy reference modules — no copy needed.
ITER_026_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "026-2026-04-24-2122-vrp-primary-portfolio"
sys.path.insert(0, str(ITER_026_DIR))

from vrp_primary import compute_vrp_primary_returns  # noqa: E402
from numpy_reference_vrp import (  # noqa: E402
    compute_vrp_primary_returns_np,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed single config — only `harvest_notional` differs from iter 026
# ---------------------------------------------------------------------------
CFG: dict = {
    "cfg_id": "vrp_primary_h3_5_5_10_1m",
    "rf": 0.02,
    "harvest_notional": 3.5,        # iter 027: levered (iter 026 used 1.0)
    "k_long_pct": 0.95,             # 5% OTM long
    "k_short_pct": 0.90,            # 10% OTM short
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    "rebalance": "daily MtM, monthly roll",
    "funding_cost_modeled": True,
    "leverage_justification": (
        "minimum half-integer notional clearing CAGR floor 3/3 datasets "
        "under linear scaling of iter 026 harvest_ann (2.80/2.92/4.23%/yr); "
        "MDD ceiling preserved 3/3 (edu 58.9% < 60.14%; spy 22.2%; ndx 28.6%); "
        "per-roll loss bounded at ~14-16% (3.5 × spread cap)"
    ),
}

# ---------------------------------------------------------------------------
# Datasets — IDENTICAL to iter 026 for direct comparability
# ---------------------------------------------------------------------------
DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-14",
        "role": "SPY+VIX ~20y (iter 020/026-aligned)",
        "iv_scale": 1.0,
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-14",
        "role": "SPY+VIX 17y post-GFC",
        "iv_scale": 1.0,
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-14",
        "role": "QQQ+VIX×1.1 16y tech-heavy",
        "iv_scale": 1.1,
    },
}


def load_prices(eq: str, start: str, end: str) -> pd.Series:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    m = (df_eq.index >= start) & (df_eq.index <= end)
    return df_eq.loc[m, "adj_close"].astype(float)


def load_vix_aligned(index: pd.DatetimeIndex) -> pd.Series:
    vix = pd.read_parquet(VIX_PATH)["VIX"]
    vix_aligned = vix.reindex(index).ffill().bfill()
    if vix_aligned.isna().any():
        raise ValueError("VIX alignment left NaN after ffill/bfill")
    return vix_aligned.astype(float)


def benchmark_metrics(returns: pd.Series) -> dict:
    eq = (1.0 + returns).cumprod()
    return {
        "sharpe": float(_sharpe(returns)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "n_bars": int(len(returns)),
        "first": str(returns.index[0].date()),
        "last": str(returns.index[-1].date()),
    }


def run_single_cfg(
    prices: pd.Series, vix: pd.Series, iv_scale: float,
) -> tuple[dict, pd.Series]:
    """Apply CFG to (prices, vix); return diagnostics + net returns."""
    net = compute_vrp_primary_returns(
        prices, vix,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
    )
    eq_curve = (1.0 + net).cumprod()
    spy_ret = prices.pct_change().dropna()
    common = net.index.intersection(spy_ret.index)
    corr_spy = float(net.loc[common].corr(spy_ret.loc[common]))

    rolling21_min = net.rolling(21).sum().min()

    rf_daily = (1.0 + CFG["rf"]) ** (1.0 / 252.0) - 1.0
    overlay = net - rf_daily   # the harvest portion (post-leverage)
    overlay_cagr = float((1.0 + overlay).prod() ** (252.0 / len(overlay)) - 1.0)
    overlay_sharpe = float(_sharpe(overlay)) if overlay.std() > 0 else float("nan")

    m = {
        "cfg_id": CFG["cfg_id"],
        "rf": CFG["rf"],
        "harvest_notional": CFG["harvest_notional"],
        "k_long_pct": CFG["k_long_pct"],
        "k_short_pct": CFG["k_short_pct"],
        "dte_days": CFG["dte_days"],
        "iv_scale": iv_scale,
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_spy_daily": corr_spy,
        "rolling21_worst": float(rolling21_min),
        "overlay_annualized": overlay_cagr,
        "overlay_sharpe": overlay_sharpe,
        "overlay_frac_positive_bars": float((overlay > 0).mean()),
    }
    return m, net


def cross_lib_check(prices: pd.Series, vix: pd.Series, iv_scale: float) -> dict:
    """G7 parity: pandas vs pure-numpy reference at h=3.5."""
    net_pd = compute_vrp_primary_returns(
        prices, vix,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
    )
    aligned = pd.concat({"p": prices, "v": vix}, axis=1, join="inner").dropna()
    arr_p = aligned["p"].to_numpy(float)
    arr_v = aligned["v"].to_numpy(float)
    net_np = compute_vrp_primary_returns_np(
        arr_p, arr_v,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
    )
    eq_pd = (1.0 + net_pd).cumprod()
    eq_np = (1.0 + pd.Series(net_np, index=net_pd.index)).cumprod()
    cagr_pd = float(_cagr(eq_pd))
    cagr_np = float(_cagr(eq_np))
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(net_pd.values - net_np))),
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "crosslib": {},
        "pre_committed": True,
        "iter_label": "027-2026-04-24-2144-levered-vrp-primary",
    }

    for ds_name, ds in DATASETS.items():
        prices = load_prices(ds["equity_symbol"], ds["start"], ds["end"])
        vix = load_vix_aligned(prices.index)
        bench_series = prices.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] {ds['equity_symbol']}+VIX×{ds['iv_scale']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} (h={CFG['harvest_notional']}) ===")
        m, net = run_single_cfg(prices, vix, ds["iv_scale"])
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
        }
        bench_sharpe = bench["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  {m['cfg_id']:32s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr_SPY={m['corr_spy_daily']:+.3f}"
        )
        print(
            f"    overlay: ann={m['overlay_annualized']:+.2%} "
            f"Sharpe={m['overlay_sharpe']:+.3f} pos_bars={m['overlay_frac_positive_bars']:.1%} "
            f"| 21d worst={m['rolling21_worst']:+.2%}"
        )

        cl = cross_lib_check(prices, vix, ds["iv_scale"])
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 cross-lib: CAGR pd={cl['cagr_pandas']:+.4%} "
            f"np={cl['cagr_numpy']:+.4%} Δ={cl['abs_diff_pp']:.4f} pp"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
