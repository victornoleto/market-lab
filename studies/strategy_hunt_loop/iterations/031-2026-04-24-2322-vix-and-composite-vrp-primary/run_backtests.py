"""Iter 031 — Run VIX AND-composite VRP-primary on 3 datasets.

Single pre-committed cfg ``vrp_and_v3p35_z2_h1_5_10_1m``. No grid, no
sweep, no post-hoc selection. Cumulative n_trials advance: 4283 → 4284.

Filter: at every natural roll bar i, open new spread only if NOT (
``vix[i] >= 35 for 3 consecutive days`` AND ``z(vix,60)[i] >= 2.0``).
NaN z (warmup) → R-2 = False → AND = False → default-to-open.

The z-score is computed over a 60-bar trailing window on the FULL VIX
history (loaded from 1990-01-02), so the warmup is fully populated by
the dataset start dates.

Citations
---------
* `[volatility_trading, p.217-218]` — Sinclair level + sustained.
* `[volatility_trading, p.39, p.58-59]` — VIX vol-of-vol + cone.
* `[volatility_trading, ch.3, p.41]` — VRP mechanics.
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

from vrp_and_composite import compute_vrp_and_composite_returns  # noqa: E402
from numpy_reference_and_composite import (  # noqa: E402
    compute_vrp_and_composite_returns_np,
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
# Pre-committed single config — anchored to literature, not data-mined
# ---------------------------------------------------------------------------
CFG: dict = {
    "cfg_id": "vrp_and_v3p35_z2_h1_5_10_1m",
    "rf": 0.02,
    "harvest_notional": 1.0,
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    "vix_threshold": 35.0,        # Sinclair p.217 hard threshold
    "persistence_days": 3,         # Bondarenko 2014 §3 empirical persistence
    "z_threshold": 2.0,            # Whaley 2009 standardized 2σ shock
    "z_window": 60,                # Sinclair p.58 cone middle horizon
    "rebalance": (
        "daily MtM, monthly roll, "
        "gated open at NOT ((VIX>=35 for 3d) AND (VIX z-score over 60d >= 2.0))"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-14",
        "role": "SPY+VIX ~20y (iter 020-aligned, includes 2008/2020/2022)",
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


def _is_persistent_high_arr(
    vix: np.ndarray, i: int, threshold: float, persistence_days: int,
) -> bool:
    if i < persistence_days - 1:
        return False
    for j in range(i - persistence_days + 1, i + 1):
        if vix[j] < threshold:
            return False
    return True


def filter_diagnostic(
    vix: pd.Series,
    z: pd.Series,
    dte_days: int,
    vix_threshold: float,
    persistence_days: int,
    z_threshold: float,
) -> dict:
    """Composite + per-axis activation rate at natural roll bars.

    Reports R-1 alone, R-2 alone, AND-composite, and OR-composite for
    diagnostic comparison. Composite-fire = SKIP.
    """
    n = len(vix)
    vix_arr = vix.to_numpy()
    z_arr = z.to_numpy()
    roll_idx = np.arange(0, n, dte_days)

    composite_skipped: list[int] = []
    r1_only: list[int] = []
    r2_only: list[int] = []
    or_skipped: list[int] = []
    for ri in roll_idx:
        idx = int(ri)
        r1 = _is_persistent_high_arr(vix_arr, idx, vix_threshold, persistence_days)
        zi = z_arr[idx]
        r2 = (zi == zi) and (zi >= z_threshold)
        if r1:
            r1_only.append(idx)
        if r2:
            r2_only.append(idx)
        if r1 and r2:
            composite_skipped.append(idx)
        if r1 or r2:
            or_skipped.append(idx)

    n_total = int(len(roll_idx))
    return {
        "natural_rolls": n_total,
        "rolls_skipped_composite_AND": int(len(composite_skipped)),
        "rolls_skipped_R1_only": int(len(r1_only)),
        "rolls_skipped_R2_only": int(len(r2_only)),
        "rolls_skipped_OR_diagnostic": int(len(or_skipped)),
        "skip_rate_composite_AND": (
            len(composite_skipped) / n_total if n_total else 0.0
        ),
        "skip_rate_R1_only": (
            len(r1_only) / n_total if n_total else 0.0
        ),
        "skip_rate_R2_only": (
            len(r2_only) / n_total if n_total else 0.0
        ),
        "vix_mean_at_rolls": float(vix.iloc[roll_idx].mean()),
        "vix_max_at_rolls": float(vix.iloc[roll_idx].max()),
        "z_max_at_rolls": float(np.nanmax(z_arr[roll_idx])),
        "composite_skip_dates": [
            str(vix.index[i].date()) for i in composite_skipped
        ],
        "composite_skip_vix": [float(vix_arr[i]) for i in composite_skipped],
        "composite_skip_z": [float(z_arr[i]) for i in composite_skipped],
    }


def run_single_cfg(
    prices: pd.Series, vix: pd.Series, z: pd.Series, iv_scale: float,
) -> tuple[dict, pd.Series]:
    net = compute_vrp_and_composite_returns(
        prices, vix, z,
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
    spy_ret = prices.pct_change().dropna()
    common = net.index.intersection(spy_ret.index)
    corr_spy = float(net.loc[common].corr(spy_ret.loc[common]))

    rolling21_min = float(net.rolling(21).sum().min())

    rf_daily = (1.0 + CFG["rf"]) ** (1.0 / 252.0) - 1.0
    overlay = net - rf_daily
    overlay_cum = float((1.0 + overlay).prod() - 1.0)
    overlay_cagr = float((1.0 + overlay).prod() ** (252.0 / len(overlay)) - 1.0)
    overlay_sharpe = (
        float(_sharpe(overlay)) if overlay.std() > 0 else float("nan")
    )

    aligned = pd.concat(
        {"price": prices, "vix": vix, "z": z}, axis=1, join="inner",
    ).dropna(subset=["price", "vix"])
    filt_diag = filter_diagnostic(
        aligned["vix"], aligned["z"], CFG["dte_days"],
        CFG["vix_threshold"], CFG["persistence_days"], CFG["z_threshold"],
    )

    m = {
        "cfg_id": CFG["cfg_id"],
        "rf": CFG["rf"],
        "harvest_notional": CFG["harvest_notional"],
        "k_long_pct": CFG["k_long_pct"],
        "k_short_pct": CFG["k_short_pct"],
        "dte_days": CFG["dte_days"],
        "vix_threshold": CFG["vix_threshold"],
        "persistence_days": CFG["persistence_days"],
        "z_threshold": CFG["z_threshold"],
        "z_window": CFG["z_window"],
        "iv_scale": iv_scale,
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_spy_daily": corr_spy,
        "rolling21_worst": rolling21_min,
        "overlay_cum_return": overlay_cum,
        "overlay_annualized": overlay_cagr,
        "overlay_sharpe": overlay_sharpe,
        "overlay_frac_positive_bars": float((overlay > 0).mean()),
        "filter_diagnostic": filt_diag,
    }
    return m, net


def cross_lib_check(
    prices: pd.Series, vix: pd.Series, z: pd.Series, iv_scale: float,
) -> dict:
    net_pd = compute_vrp_and_composite_returns(
        prices, vix, z,
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
        {"p": prices, "v": vix, "z": z},
        axis=1, join="inner",
    ).dropna(subset=["p", "v"])
    arr_p = aligned["p"].to_numpy(float)
    arr_v = aligned["v"].to_numpy(float)
    arr_z = aligned["z"].to_numpy(float)
    net_np = compute_vrp_and_composite_returns_np(
        arr_p, arr_v, arr_z,
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
        "iter_label": "031-2026-04-24-2322-vix-and-composite-vrp-primary",
    }

    vix_full = load_vix_full()
    print(
        f"VIX history: {vix_full.index.min().date()} → "
        f"{vix_full.index.max().date()} ({len(vix_full)} bars; "
        f"warmup buffer for educational ≈ "
        f"{(pd.Timestamp('2006-01-03') - vix_full.index.min()).days // 365}y)"
    )

    for ds_name, ds in DATASETS.items():
        prices = load_prices(ds["equity_symbol"], ds["start"], ds["end"])
        vix, z = vix_z_aligned(prices.index, vix_full, CFG["z_window"])
        bench_series = prices.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"\n[{ds_name}] {ds['equity_symbol']}+VIX×{ds['iv_scale']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} VIX[mean/med]={vix.mean():.1f}/{vix.median():.1f}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, net = run_single_cfg(prices, vix, z, ds["iv_scale"])
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
            f"  {m['cfg_id']:38s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr_SPY={m['corr_spy_daily']:+.3f}"
        )
        fd = m["filter_diagnostic"]
        print(
            f"    overlay: ann={m['overlay_annualized']:+.2%} "
            f"Sharpe={m['overlay_sharpe']:+.3f} pos_bars={m['overlay_frac_positive_bars']:.1%} "
            f"| 21d worst={m['rolling21_worst']:+.2%}"
        )
        print(
            f"    AND-composite: "
            f"{fd['rolls_skipped_composite_AND']}/{fd['natural_rolls']} rolls "
            f"({fd['skip_rate_composite_AND']*100:.2f}%) | "
            f"R-1 only: {fd['rolls_skipped_R1_only']} ({fd['skip_rate_R1_only']*100:.2f}%) | "
            f"R-2 only: {fd['rolls_skipped_R2_only']} ({fd['skip_rate_R2_only']*100:.2f}%) | "
            f"OR-diag: {fd['rolls_skipped_OR_diagnostic']}"
        )
        if fd["composite_skip_dates"]:
            comp_str = ", ".join(
                f"{d}(VIX={v:.0f},z={z:.1f})"
                for d, v, z in zip(
                    fd["composite_skip_dates"],
                    fd["composite_skip_vix"],
                    fd["composite_skip_z"],
                )
            )
        else:
            comp_str = "NONE"
        print(f"    composite-fired: {comp_str}")

        cl = cross_lib_check(prices, vix, z, ds["iv_scale"])
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
