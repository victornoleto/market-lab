"""Iter 046 — Run 50/50 convex combo (iter 041 stack + iter 039 VRP basket) on 3 datasets.

Single pre-committed cfg ``iter039_on_iter041_50_50``. No grid, no sweep,
no post-hoc selection. Cumulative n_trials advance: 4310 → 4311 (+1).

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack with
  regime-conditional weight tilts (iter 041 base architecture).
* `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP (iter 039).
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

from combined_041_039 import compute_combined_returns  # noqa: E402
from numpy_reference_combined_046 import compute_combined_returns_np  # noqa: E402

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
    "cfg_id": "iter039_on_iter041_50_50",
    # Convex combination weights
    "w_041": 0.5,
    "w_039": 0.5,
    # iter 041 sub-strategy params (verbatim from TOP-K #1 cfg)
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},  # 1.50× total
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},  # 1.40× total
    "vix_threshold": 20.0,
    "cost_bps_per_leg": 0.0002,
    # iter 039 sub-strategy params (verbatim)
    "rf": 0.02,
    "harvest_notional": 1.0,
    "weights_039": {"SPY": 1.0 / 3, "QQQ": 1.0 / 3, "IWM": 1.0 / 3},
    "iv_scales": {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
    "rebalance": "daily, 50/50 convex combo of iter 041 regime stack and iter 039 basket",
    "funding_cost_modeled": False,
    "primary_citation": "[risk_parity, ch.5] + [volatility_trading, p.218]",
}

# ---------------------------------------------------------------------------
# Datasets — match iter 045's windows verbatim (GLD-aligned + VIX-aligned)
# ---------------------------------------------------------------------------
DATASETS: dict[str, dict] = {
    "educational": {
        "stack_eq": "SPY",
        "stack_bd": "IEF",
        "stack_gld": "GLD",
        "basket_tickers": ("SPY", "QQQ", "IWM"),
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; iter 041 stack + iter 039 basket; 2008+2020+2022 stress",
    },
    "spy_real": {
        "stack_eq": "SPY",
        "stack_bd": "IEF",
        "stack_gld": "GLD",
        "basket_tickers": ("SPY", "QQQ", "IWM"),
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC combined",
    },
    "ndx_real": {
        # iter 041 stack ALWAYS uses SPY+IEF+GLD regardless of bench;
        # iter 039 basket ALWAYS uses SPY+QQQ+IWM regardless of bench.
        "stack_eq": "SPY",
        "stack_bd": "IEF",
        "stack_gld": "GLD",
        "basket_tickers": ("SPY", "QQQ", "IWM"),
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; bench QQQ; iter 041 stack on SPY + iter 039 basket SPY/QQQ/IWM",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
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
    stack_prices: dict[str, pd.Series],
    basket_prices: dict[str, pd.Series],
    vix: pd.Series,
) -> tuple[dict, pd.Series, pd.Series, pd.Series]:
    combined, r_041, r_039 = compute_combined_returns(
        stack_prices["eq"], stack_prices["bd"], stack_prices["gld"],
        basket_prices, vix,
        w_041=CFG["w_041"], w_039=CFG["w_039"],
        calm_weights=CFG["calm_weights"],
        stress_weights=CFG["stress_weights"],
        vix_threshold=CFG["vix_threshold"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
        rf=CFG["rf"],
        harvest_notional=CFG["harvest_notional"],
        weights=CFG["weights_039"],
        iv_scales=CFG["iv_scales"],
        k_long_pct=CFG["k_long_pct"], k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"], cost_bps_per_roll=CFG["cost_bps_per_roll"],
    )
    eq_curve = (1.0 + combined).cumprod()

    spy = stack_prices["eq"]
    spy_ret = spy.pct_change().dropna()
    common = combined.index.intersection(spy_ret.index)
    corr_combined_spy = float(combined.loc[common].corr(spy_ret.loc[common]))
    corr_041_039 = float(r_041.corr(r_039))

    rolling21_min = float(combined.rolling(21).sum().min())

    m = {
        "cfg_id": CFG["cfg_id"],
        "w_041": CFG["w_041"], "w_039": CFG["w_039"],
        "calm_weights": CFG["calm_weights"],
        "stress_weights": CFG["stress_weights"],
        "vix_threshold": CFG["vix_threshold"],
        "harvest_notional": CFG["harvest_notional"],
        "weights_039": CFG["weights_039"],
        "iv_scales": CFG["iv_scales"],
        "bars": int(len(combined)),
        "sharpe": float(_sharpe(combined)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_combined_spy": corr_combined_spy,
        "corr_041_039": corr_041_039,
        "r_041_sharpe": float(_sharpe(r_041)),
        "r_041_cagr": float(_cagr((1.0 + r_041).cumprod())),
        "r_041_mdd": float(_max_drawdown((1.0 + r_041).cumprod())),
        "r_039_sharpe": float(_sharpe(r_039)),
        "r_039_cagr": float(_cagr((1.0 + r_039).cumprod())),
        "r_039_mdd": float(_max_drawdown((1.0 + r_039).cumprod())),
        "rolling21_worst": rolling21_min,
    }
    return m, combined, r_041, r_039


def cross_lib_check(
    stack_prices: dict[str, pd.Series],
    basket_prices: dict[str, pd.Series],
    vix: pd.Series,
) -> dict:
    """G7 parity: pandas engine vs pure-numpy reference CAGR Δ ≤ 3 pp."""
    net_pd, _, _ = compute_combined_returns(
        stack_prices["eq"], stack_prices["bd"], stack_prices["gld"],
        basket_prices, vix,
        w_041=CFG["w_041"], w_039=CFG["w_039"],
        calm_weights=CFG["calm_weights"],
        stress_weights=CFG["stress_weights"],
        vix_threshold=CFG["vix_threshold"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
        rf=CFG["rf"], harvest_notional=CFG["harvest_notional"],
        weights=CFG["weights_039"], iv_scales=CFG["iv_scales"],
        k_long_pct=CFG["k_long_pct"], k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"], cost_bps_per_roll=CFG["cost_bps_per_roll"],
    )

    # Build aligned numpy arrays. iter 041 ref consumes RETURNS + a regime
    # built from VIX (length matches returns); iter 039 ref consumes
    # PRICES + IV (length n+1, matches prices).
    common = stack_prices["eq"].index
    for s in [stack_prices["bd"], stack_prices["gld"], *basket_prices.values()]:
        common = common.intersection(s.index)
    common = common.intersection(vix.index)

    eq_aligned = stack_prices["eq"].loc[common]
    bd_aligned = stack_prices["bd"].loc[common]
    gld_aligned = stack_prices["gld"].loc[common]
    basket_aligned = {tk: s.loc[common] for tk, s in basket_prices.items()}
    vix_aligned = vix.loc[common]

    r_eq_np = eq_aligned.pct_change().dropna().to_numpy(float)
    r_bd_np = bd_aligned.pct_change().dropna().to_numpy(float)
    r_gld_np = gld_aligned.pct_change().dropna().to_numpy(float)
    basket_np = {tk: s.to_numpy(float) for tk, s in basket_aligned.items()}
    vix_full_np = vix_aligned.to_numpy(float)
    # vix_for_regime aligned to the **return** index (length n-1 = len(r_eq)).
    # iter 041's pandas engine drops the price-only first bar via
    # pct_change().dropna(); the returns index matches dates 1..n-1.
    vix_for_regime_np = vix_aligned.iloc[1:].to_numpy(float)

    net_np, _, _ = compute_combined_returns_np(
        r_eq_np, r_bd_np, r_gld_np,
        vix_for_regime_np,
        basket_np, vix_full_np,
        w_041=CFG["w_041"], w_039=CFG["w_039"],
        calm_weights=CFG["calm_weights"],
        stress_weights=CFG["stress_weights"],
        vix_threshold=CFG["vix_threshold"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
        rf=CFG["rf"], harvest_notional=CFG["harvest_notional"],
        weights=CFG["weights_039"], iv_scales=CFG["iv_scales"],
        k_long_pct=CFG["k_long_pct"], k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"], cost_bps_per_roll=CFG["cost_bps_per_roll"],
    )

    n = min(len(net_pd), len(net_np))
    pd_arr = net_pd.values[-n:]
    np_arr = net_np[-n:]
    eq_pd = np.cumprod(1.0 + pd_arr)
    eq_np = np.cumprod(1.0 + np_arr)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np_val = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np_val,
        "abs_diff_pp": abs(cagr_pd - cagr_np_val) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_arr - np_arr))),
        "n_bars_compared": n,
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "subcomponent_returns": {},
        "crosslib": {},
        "pre_committed": True,
        "iter_label": "046-2026-04-25-0553-iter039-overlay-on-iter041",
    }

    for ds_name, ds in DATASETS.items():
        eq_p = load_prices(ds["stack_eq"], ds["start"], ds["end"])
        bd_p = load_prices(ds["stack_bd"], ds["start"], ds["end"])
        gld_p = load_prices(ds["stack_gld"], ds["start"], ds["end"])
        basket_p = {
            tk: load_prices(tk, ds["start"], ds["end"]) for tk in ds["basket_tickers"]
        }

        common = eq_p.index.intersection(bd_p.index).intersection(gld_p.index)
        for s in basket_p.values():
            common = common.intersection(s.index)
        eq_p = eq_p.loc[common]
        bd_p = bd_p.loc[common]
        gld_p = gld_p.loc[common]
        basket_p = {tk: s.loc[common] for tk, s in basket_p.items()}
        vix = load_vix_aligned(common)

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"]).loc[common]
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] stack=({ds['stack_eq']}+{ds['stack_bd']}+{ds['stack_gld']}) "
            f"basket=({','.join(ds['basket_tickers'])}) bench={ds['bench_ticker']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, combined, r_041, r_039 = run_single_cfg(
            {"eq": eq_p, "bd": bd_p, "gld": gld_p}, basket_p, vix,
        )
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_041": {
                "index": [str(t.date()) for t in r_041.index],
                "net_returns": [round(float(x), 10) for x in r_041.tolist()],
            },
            "r_039": {
                "index": [str(t.date()) for t in r_039.index],
                "net_returns": [round(float(x), 10) for x in r_039.tolist()],
            },
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        print(
            f"  combined Sharpe={m['sharpe']:+.4f} (Δ frozen={edge_frozen:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr_SPY={m['corr_combined_spy']:+.3f} corr(041,039)={m['corr_041_039']:+.3f}"
        )
        print(
            f"  r_041 Sharpe={m['r_041_sharpe']:+.4f} CAGR={m['r_041_cagr']:+.2%} MDD={m['r_041_mdd']:.2%} "
            f"| r_039 Sharpe={m['r_039_sharpe']:+.4f} CAGR={m['r_039_cagr']:+.2%} MDD={m['r_039_mdd']:.2%}"
        )

        cl = cross_lib_check({"eq": eq_p, "bd": bd_p, "gld": gld_p}, basket_p, vix)
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 cross-lib: CAGR pd={cl['cagr_pandas']:+.4%} "
            f"np={cl['cagr_numpy']:+.4%} Δ={cl['abs_diff_pp']:.4f} pp "
            f"(n_compared={cl['n_bars_compared']})"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
