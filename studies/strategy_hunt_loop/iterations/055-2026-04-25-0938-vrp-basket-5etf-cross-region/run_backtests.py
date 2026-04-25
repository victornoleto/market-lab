"""Iter 055 — Run cross-region 5-leg VRP basket on 3 datasets.

Single pre-committed cfg ``vrp_basket_eq5_5_10_1m_5regions``. No grid,
no sweep, no post-hoc selection. Cumulative n_trials advance: 4324 →
4325 (+1).

Reuses iter 039's `vrp_basket.compute_vrp_basket_returns` and
`numpy_reference_basket.compute_vrp_basket_returns_np` directly — both
are already generic over leg count.

Citations
---------
* `[volatility_trading, p.218]` — cross-asset VRP harvest (primary).
* `[volatility_trading, ch.3, p.41, p.217]` — VRP mechanics + capped tail.
* Bondarenko (2014) QJF 4(3); Carr-Wu (2009) RFS 22(3); Driessen et al
  (2009) JoF 64(4); Bakshi-Madan (2006) JFE 81(2); AMP 2013 JoF 68(3).
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
ITER_039_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "039-2026-04-25-0313-vrp-basket-3etf"
sys.path.insert(0, str(ITER_039_DIR))

from vrp_basket import compute_vrp_basket_returns  # noqa: E402
from numpy_reference_basket import (  # noqa: E402
    compute_vrp_basket_returns_np,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed single config — 5-leg cross-region VRP basket
# ---------------------------------------------------------------------------
CFG: dict = {
    "cfg_id": "vrp_basket_eq5_5_10_1m_5regions",
    "rf": 0.02,
    "harvest_notional": 1.0,
    "weights": {
        "SPY": 1.0 / 5, "QQQ": 1.0 / 5, "IWM": 1.0 / 5,
        "EFA": 1.0 / 5, "EEM": 1.0 / 5,
    },
    "iv_scales": {
        "SPY": 1.0, "QQQ": 1.10, "IWM": 1.25,
        "EFA": 1.05, "EEM": 1.30,
    },
    "k_long_pct": 0.95,        # 5% OTM long
    "k_short_pct": 0.90,       # 10% OTM short
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    "rebalance": "daily MtM, monthly roll per leg, basket weight rebalance daily",
    "funding_cost_modeled": True,
}

TICKERS = ("SPY", "QQQ", "IWM", "EFA", "EEM")

# ---------------------------------------------------------------------------
# Datasets — preserve iter 039 windows for direct comparability
# (EFA/EEM start 2003-08-20 in cache so 2006-01-03 educational start is safe)
# ---------------------------------------------------------------------------
DATASETS: dict[str, dict] = {
    "educational": {
        "tickers": TICKERS,
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-14",
        "role": "Basket SPY+QQQ+IWM+EFA+EEM ~20y (iter 039-aligned, 2008+2020+2022)",
    },
    "spy_real": {
        "tickers": TICKERS,
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-14",
        "role": "Basket SPY+QQQ+IWM+EFA+EEM 17y post-GFC",
    },
    "ndx_real": {
        "tickers": TICKERS,
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-14",
        "role": "Basket SPY+QQQ+IWM+EFA+EEM 16y; benchmark QQQ",
    },
}


def load_prices(eq: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


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
    prices: dict[str, pd.Series], vix: pd.Series,
) -> tuple[dict, pd.Series]:
    net = compute_vrp_basket_returns(
        prices, vix,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        weights=CFG["weights"],
        iv_scales=CFG["iv_scales"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
    )
    eq_curve = (1.0 + net).cumprod()

    spy = prices["SPY"]
    spy_ret = spy.pct_change().dropna()
    common = net.index.intersection(spy_ret.index)
    corr_spy = float(net.loc[common].corr(spy_ret.loc[common]))

    rf_daily = (1.0 + CFG["rf"]) ** (1.0 / 252.0) - 1.0
    overlay = net - rf_daily
    overlay_cum = float((1.0 + overlay).prod() - 1.0)
    overlay_cagr = float((1.0 + overlay).prod() ** (252.0 / len(overlay)) - 1.0)
    overlay_sharpe = float(_sharpe(overlay)) if overlay.std() > 0 else float("nan")
    rolling21_min = float(net.rolling(21).sum().min())

    m = {
        "cfg_id": CFG["cfg_id"],
        "rf": CFG["rf"],
        "harvest_notional": CFG["harvest_notional"],
        "weights": CFG["weights"],
        "iv_scales": CFG["iv_scales"],
        "k_long_pct": CFG["k_long_pct"],
        "k_short_pct": CFG["k_short_pct"],
        "dte_days": CFG["dte_days"],
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
    }
    return m, net


def cross_lib_check(prices: dict[str, pd.Series], vix: pd.Series) -> dict:
    """G7 parity: pandas engine vs pure-numpy reference CAGR Δ ≤ 3 pp."""
    net_pd = compute_vrp_basket_returns(
        prices, vix,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        weights=CFG["weights"],
        iv_scales=CFG["iv_scales"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
    )
    aligned = pd.concat(
        {**prices, "v": vix}, axis=1, join="inner",
    ).dropna()
    arrs = {tk: aligned[tk].to_numpy(float) for tk in prices}
    arr_v = aligned["v"].to_numpy(float)
    net_np = compute_vrp_basket_returns_np(
        arrs, arr_v,
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        weights=CFG["weights"],
        iv_scales=CFG["iv_scales"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
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
        "iter_label": "055-2026-04-25-0938-vrp-basket-5etf-cross-region",
    }

    for ds_name, ds in DATASETS.items():
        per_leg = {
            tk: load_prices(tk, ds["start"], ds["end"])
            for tk in ds["tickers"]
        }
        common = per_leg["SPY"].index
        for tk in ds["tickers"]:
            common = common.intersection(per_leg[tk].index)
        per_leg = {tk: s.loc[common] for tk, s in per_leg.items()}

        vix = load_vix_aligned(per_leg["SPY"].index)

        bench_series = per_leg[ds["bench_ticker"]].pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] basket=({','.join(ds['tickers'])}) "
            f"bench={ds['bench_ticker']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} VIX[mean/med]={vix.mean():.1f}/{vix.median():.1f}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, net = run_single_cfg(per_leg, vix)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": [round(float(x), 10) for x in net.tolist()],
            }
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        print(
            f"  {m['cfg_id']:40s} Sharpe={m['sharpe']:+.4f} "
            f"(Δ frozen={edge_frozen:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr_SPY={m['corr_spy_daily']:+.3f}"
        )
        print(
            f"    overlay: ann={m['overlay_annualized']:+.2%} "
            f"Sharpe={m['overlay_sharpe']:+.3f} pos_bars={m['overlay_frac_positive_bars']:.1%} "
            f"| 21d worst={m['rolling21_worst']:+.2%}"
        )

        cl = cross_lib_check(per_leg, vix)
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
