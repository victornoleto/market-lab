"""Iter 032 — Run NTSX 90/60 + iter 031 AND-composite VRP overlay on 3 datasets.

Single pre-committed cfg ``ntsx_vrp_and_v3p35_z2_eq09_bd06_h1``.
No grid, no sweep. Cumulative n_trials advance: 4284 → 4285 (+1).

Citations
---------
* `[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen 2012.
* `[volatility_trading, p.41, ch.3]` — VRP mechanics + SPX kurtosis.
* `[volatility_trading, p.217-218]` — Sinclair short-vol-writer regime.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_030_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "030-2026-04-24-2259-vix-zscore-vrp-primary"
sys.path.insert(0, str(ITER_DIR))
sys.path.insert(0, str(ITER_030_DIR))

from ntsx_vrp_combined import compute_ntsx_vrp_combined_returns  # noqa: E402
from numpy_reference_combined import (  # noqa: E402
    compute_ntsx_vrp_combined_returns_np,
)
from vrp_zscore import rolling_zscore  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------
CFG: dict = {
    "cfg_id": "ntsx_vrp_and_v3p35_z2_eq09_bd06_h1",
    # NTSX leg (iter 015 anchored)
    "eq_w": 0.90,
    "bd_w": 0.60,
    "cost_bps_per_leg": 0.0002,
    # VRP leg (iter 031 anchored — literature, not data-mined)
    "rf": 0.02,
    "harvest_notional": 1.0,
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    # AND-composite gate (iter 031 anchored)
    "vix_threshold": 35.0,
    "persistence_days": 3,
    "z_threshold": 2.0,
    "z_window": 60,
    "rebalance": (
        "daily MtM, monthly roll, "
        "static eq_w/bd_w + harvest gated at NOT ((VIX>=35 for 3d) AND (VIX z(60d)>=2.0))"
    ),
    "funding_cost_modeled": False,
}

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2006-01-03",
        "end": "2026-04-14",
        "role": "SPY+IEF+VIX ~20y (IEF-inception-aligned, includes GFC + COVID + 2022)",
        "iv_scale": 1.0,
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2009-06-25",
        "end": "2026-04-14",
        "role": "SPY+IEF+VIX 17y post-GFC",
        "iv_scale": 1.0,
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "IEF",
        "start": "2010-02-12",
        "end": "2026-04-14",
        "role": "QQQ+IEF+VIX×1.1 16y tech-heavy",
        "iv_scale": 1.1,
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_vix_full() -> pd.Series:
    return pd.read_parquet(VIX_PATH)["VIX"].astype(float)


def vix_z_aligned(
    price_index: pd.DatetimeIndex,
    vix_full: pd.Series,
    window: int,
) -> tuple[pd.Series, pd.Series]:
    z_full = rolling_zscore(vix_full, window=window)
    vix_aligned = vix_full.reindex(price_index).ffill().bfill()
    z_aligned = z_full.reindex(price_index).ffill()
    if vix_aligned.isna().any():
        raise ValueError("VIX alignment left NaN after ffill/bfill")
    return vix_aligned, z_aligned


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
    eq_prices: pd.Series,
    bd_prices: pd.Series,
    vix: pd.Series,
    z: pd.Series,
    iv_scale: float,
) -> tuple[dict, pd.Series]:
    net = compute_ntsx_vrp_combined_returns(
        eq_prices, bd_prices, vix, z,
        eq_w=CFG["eq_w"],
        bd_w=CFG["bd_w"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
        vix_threshold=CFG["vix_threshold"],
        persistence_days=CFG["persistence_days"],
        z_threshold=CFG["z_threshold"],
    )
    eq_curve = (1.0 + net).cumprod()

    spy_ret = eq_prices.pct_change().dropna()
    common = net.index.intersection(spy_ret.index)
    corr_spy = float(net.loc[common].corr(spy_ret.loc[common]))

    bd_ret = bd_prices.pct_change().dropna()
    common_bd = net.index.intersection(bd_ret.index)
    corr_bd = float(net.loc[common_bd].corr(bd_ret.loc[common_bd]))

    rolling21_min = float(net.rolling(21).sum().min())

    m = {
        "cfg_id": CFG["cfg_id"],
        "eq_w": CFG["eq_w"],
        "bd_w": CFG["bd_w"],
        "harvest_notional": CFG["harvest_notional"],
        "vix_threshold": CFG["vix_threshold"],
        "persistence_days": CFG["persistence_days"],
        "z_threshold": CFG["z_threshold"],
        "iv_scale": iv_scale,
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_spy_daily": corr_spy,
        "corr_ief_daily": corr_bd,
        "rolling21_worst": rolling21_min,
    }
    return m, net


def cross_lib_check(
    eq_prices: pd.Series,
    bd_prices: pd.Series,
    vix: pd.Series,
    z: pd.Series,
    iv_scale: float,
) -> dict:
    net_pd = compute_ntsx_vrp_combined_returns(
        eq_prices, bd_prices, vix, z,
        eq_w=CFG["eq_w"],
        bd_w=CFG["bd_w"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
        vix_threshold=CFG["vix_threshold"],
        persistence_days=CFG["persistence_days"],
        z_threshold=CFG["z_threshold"],
    )
    aligned = pd.concat(
        {"eq": eq_prices, "bd": bd_prices, "iv": vix, "z": z},
        axis=1, join="inner",
    ).dropna(subset=["eq", "bd", "iv"])
    arr_eq = aligned["eq"].to_numpy(float)
    arr_bd = aligned["bd"].to_numpy(float)
    arr_iv = aligned["iv"].to_numpy(float)
    arr_z = aligned["z"].to_numpy(float)
    net_np = compute_ntsx_vrp_combined_returns_np(
        arr_eq, arr_bd, arr_iv, arr_z,
        eq_w=CFG["eq_w"],
        bd_w=CFG["bd_w"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
        vix_threshold=CFG["vix_threshold"],
        persistence_days=CFG["persistence_days"],
        z_threshold=CFG["z_threshold"],
    )
    eq_pd = (1.0 + net_pd).cumprod()
    eq_np = (1.0 + pd.Series(net_np, index=net_pd.index)).cumprod()
    cagr_pd = float(_cagr(eq_pd))
    cagr_np_v = float(_cagr(eq_np))
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np_v,
        "abs_diff_pp": abs(cagr_pd - cagr_np_v) * 100.0,
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
        "leg_correlations": {},
        "pre_committed": True,
        "iter_label": "032-2026-04-25-0032-ntsx-vrp-and-composite",
    }

    vix_full = load_vix_full()
    print(
        f"VIX history: {vix_full.index.min().date()} → "
        f"{vix_full.index.max().date()} ({len(vix_full)} bars)"
    )

    for ds_name, ds in DATASETS.items():
        eq_prices = load_prices(ds["equity_symbol"], ds["start"], ds["end"])
        bd_prices = load_prices(ds["bond_symbol"], ds["start"], ds["end"])
        joined = pd.concat({"eq": eq_prices, "bd": bd_prices}, axis=1, join="inner").dropna()
        joined_index = joined.index
        vix, z = vix_z_aligned(joined_index, vix_full, CFG["z_window"])

        bench_series = eq_prices.reindex(joined_index).pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr_eq_bd = float(joined.pct_change().dropna().corr().iloc[0, 1])
        all_results["leg_correlations"][ds_name] = {"eq_bd": corr_eq_bd}

        print(
            f"\n[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']}+VIX×{ds['iv_scale']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} ρ(eq,bd)={corr_eq_bd:+.3f}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, net = run_single_cfg(
            joined["eq"], joined["bd"], vix, z, ds["iv_scale"],
        )
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
            f"  {m['cfg_id']:42s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr_SPY={m['corr_spy_daily']:+.3f} corr_IEF={m['corr_ief_daily']:+.3f}"
        )
        print(f"    21d worst rolling-sum return: {m['rolling21_worst']:+.2%}")

        cl = cross_lib_check(joined["eq"], joined["bd"], vix, z, ds["iv_scale"])
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
