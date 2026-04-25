"""Iter 029 — Run VIX-persistence VRP-primary on 3 datasets.

Single pre-committed cfg ``vrp_persistence_v35d3_h1_5_10_1m``. No grid,
no sweep, no post-hoc selection. Cumulative n_trials advance:
4281 → 4282.

Filter: at every natural roll bar, open new spread only if NOT
``is_persistent_high(vix, i, threshold=35, persistence_days=3)``.
Otherwise hold T-bills until next eligible roll bar.

Citations
---------
* `[volatility_trading, p.217]` — Sinclair VIX < 35 entry rule (level).
* `[volatility_trading, p.218]` — sustained vs transient high IV
  (persistence).
* `[volatility_trading, ch.3]` — VRP mechanics (unchanged).
* `[volatility_trading, p.41]` — capped-tail justification.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
sys.path.insert(0, str(ITER_DIR))

from vrp_persistence import (  # noqa: E402
    compute_vrp_persistence_returns,
    is_persistent_high,
)
from numpy_reference_persistence import (  # noqa: E402
    compute_vrp_persistence_returns_np,
)

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
    "cfg_id": "vrp_persistence_v35d3_h1_5_10_1m",
    "rf": 0.02,
    "harvest_notional": 1.0,
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    "vix_threshold": 35.0,        # Sinclair p.217 explicit value
    "persistence_days": 3,        # Bondarenko 2014 §3 sustained def.
    "rebalance": (
        "daily MtM, monthly roll, "
        "gated open at NOT (VIX>=35 for 3 consecutive days)"
    ),
}

# ---------------------------------------------------------------------------
# Datasets — match iter 020/026/028 alignment for direct comparability
# ---------------------------------------------------------------------------
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


def filter_diagnostic(
    vix: pd.Series, dte_days: int, threshold: float, persistence_days: int,
) -> dict:
    """Approximate persistence-gate activation rate at natural roll bars.

    Counts how many natural roll bars (every ``dte_days`` from index 0)
    satisfy ``is_persistent_high`` — i.e. would be SKIPPED.

    Also reports comparison to iter 028's level-only single-bar gate so
    the regime structure is visible.
    """
    n = len(vix)
    vix_arr = vix.to_numpy()
    roll_idx = np.arange(0, n, dte_days)

    persistence_skipped: list[int] = []
    level_only_skipped: list[int] = []  # iter-028-equivalent
    for ri in roll_idx:
        if is_persistent_high(vix_arr, int(ri), threshold, persistence_days):
            persistence_skipped.append(int(ri))
        if vix_arr[int(ri)] >= threshold:
            level_only_skipped.append(int(ri))

    n_total = int(len(roll_idx))
    return {
        "natural_rolls": n_total,
        "rolls_skipped_persistence": int(len(persistence_skipped)),
        "rolls_skipped_level_only_iter028_equiv": int(len(level_only_skipped)),
        "skip_rate_persistence": (
            len(persistence_skipped) / n_total if n_total else 0.0
        ),
        "skip_rate_level_only": (
            len(level_only_skipped) / n_total if n_total else 0.0
        ),
        "vix_mean_at_rolls": float(vix.iloc[roll_idx].mean()),
        "vix_median_at_rolls": float(vix.iloc[roll_idx].median()),
        "vix_max_at_rolls": float(vix.iloc[roll_idx].max()),
        "skipped_dates_persistence": [
            str(vix.index[ri].date()) for ri in persistence_skipped
        ],
    }


def run_single_cfg(
    prices: pd.Series, vix: pd.Series, iv_scale: float,
) -> tuple[dict, pd.Series]:
    """Apply CFG to (prices, vix); return diagnostics + net returns."""
    net = compute_vrp_persistence_returns(
        prices, vix,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
        vix_threshold=CFG["vix_threshold"],
        persistence_days=CFG["persistence_days"],
    )
    eq_curve = (1.0 + net).cumprod()
    spy_ret = prices.pct_change().dropna()
    common = net.index.intersection(spy_ret.index)
    corr_spy = float(net.loc[common].corr(spy_ret.loc[common]))

    rolling21_min = float(net.rolling(21).sum().min())

    rf_daily = (1.0 + CFG["rf"]) ** (1.0 / 252.0) - 1.0
    overlay = net - rf_daily   # the harvest portion (incl. zeros in HOLD-CASH)
    overlay_cum = float((1.0 + overlay).prod() - 1.0)
    overlay_cagr = float((1.0 + overlay).prod() ** (252.0 / len(overlay)) - 1.0)
    overlay_sharpe = (
        float(_sharpe(overlay)) if overlay.std() > 0 else float("nan")
    )

    aligned = pd.concat(
        {"price": prices, "vix": vix}, axis=1, join="inner",
    ).dropna()
    filt_diag = filter_diagnostic(
        aligned["vix"], CFG["dte_days"], CFG["vix_threshold"],
        CFG["persistence_days"],
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
    prices: pd.Series, vix: pd.Series, iv_scale: float,
) -> dict:
    """G7 parity: pure-numpy reference vs pandas engine."""
    net_pd = compute_vrp_persistence_returns(
        prices, vix,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
        vix_threshold=CFG["vix_threshold"],
        persistence_days=CFG["persistence_days"],
    )
    aligned = pd.concat({"p": prices, "v": vix}, axis=1, join="inner").dropna()
    arr_p = aligned["p"].to_numpy(float)
    arr_v = aligned["v"].to_numpy(float)
    net_np = compute_vrp_persistence_returns_np(
        arr_p, arr_v,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
        vix_threshold=CFG["vix_threshold"],
        persistence_days=CFG["persistence_days"],
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
        "iter_label": "029-2026-04-24-2236-vix-persistence-vrp-primary",
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
            f"MDD={bench['mdd']:.2%} VIX[mean/med]={vix.mean():.1f}/{vix.median():.1f}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
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
            f"    persistence-gate: "
            f"{fd['rolls_skipped_persistence']}/{fd['natural_rolls']} rolls "
            f"({fd['skip_rate_persistence']*100:.2f}%) | "
            f"level-only iter028-equiv: "
            f"{fd['rolls_skipped_level_only_iter028_equiv']} "
            f"({fd['skip_rate_level_only']*100:.2f}%)"
        )
        print(
            f"    skipped-dates persistence: {fd['skipped_dates_persistence'][:5]}"
            f"{'...' if len(fd['skipped_dates_persistence']) > 5 else ''}"
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
