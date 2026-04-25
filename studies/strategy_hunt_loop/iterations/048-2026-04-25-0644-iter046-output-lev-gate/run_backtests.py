"""Iter 048 — VIX-regime OUTPUT leverage gate on iter 046 (single cfg).

Single pre-committed cfg:

    iter046_lev_calm14_stress10_vix20
        lev_calm = 1.4
        lev_stress = 1.0
        vix_threshold = 20.0
        (iter 041 + iter 039 sub-strategy params VERBATIM from iter 046)

The driver:

1. Loads SPY/IEF/GLD/QQQ/IWM prices + VIX exactly as iter 046's driver.
2. Computes iter 046's combined stream via the iter 046 engine VERBATIM.
3. Applies ``apply_output_lev_gate`` (this iter's contribution) to
   produce iter 048's daily net stream.
4. Computes Sharpe, CAGR, MDD, correlations.
5. Computes G7 cross-lib parity (pandas vs numpy reference).
6. Writes ``results.json`` with the same schema as iter 046/047.

Cumulative n_trials advance: 4314 → 4315 (+1).

Citations
---------
* `[risk_parity, ch.5]` — iter 041 base architecture.
* `[volatility_trading, p.218]` — iter 039 basket architecture.
* `[advances_fin_ml, ch.17-18]` — binary regime detection on VIX.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* Whaley (2009), JPM 35(3) — VIX as ex-ante risk regime indicator.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"

# Reuse iter 046's pandas engine + numpy reference verbatim.
sys.path.insert(0, str(ITER_046_DIR))
sys.path.insert(0, str(ITER_DIR))

from combined_041_039 import compute_combined_returns  # noqa: E402
from numpy_reference_combined_046 import compute_combined_returns_np  # noqa: E402
from output_lev_gate import apply_output_lev_gate  # noqa: E402
from numpy_reference_iter048 import apply_output_lev_gate_np  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"

# ---------------------------------------------------------------------------
# Single pre-committed cfg
# ---------------------------------------------------------------------------
CFG: dict = {
    "cfg_id": "iter046_lev_calm14_stress10_vix20",
    "lev_calm": 1.4,
    "lev_stress": 1.0,
    "vix_threshold_lev": 20.0,
    "note": (
        "Output-side leverage gate on iter 046 combined stream. "
        "1.4× when VIX[t-1]<20 (calm); 1.0× when VIX[t-1]≥20 (stress). "
        "iter 041 + iter 039 sub-params VERBATIM from iter 046 50/50."
    ),
}

# Sub-strategy params shared across iter 046/047 (VERBATIM).
SHARED_PARAMS = {
    # iter 046 50/50 weights
    "w_041": 0.50,
    "w_039": 0.50,
    "calm_weights":   {"eq_w": 0.70, "bd_w": 0.40, "gld_w": 0.40},  # 1.50× total
    "stress_weights": {"eq_w": 0.30, "bd_w": 0.55, "gld_w": 0.55},  # 1.40× total
    "vix_threshold_inner": 20.0,  # iter 041's input-gate threshold
    "cost_bps_per_leg": 0.0002,
    "rf": 0.02,
    "harvest_notional": 1.0,
    "weights_039": {"SPY": 1.0 / 3, "QQQ": 1.0 / 3, "IWM": 1.0 / 3},
    "iv_scales": {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25},
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "cost_bps_per_roll": 5.0,
}

# Datasets — match iter 046/047 verbatim (GLD-aligned + VIX-aligned).
DATASETS: dict[str, dict] = {
    "educational": {
        "stack_eq": "SPY", "stack_bd": "IEF", "stack_gld": "GLD",
        "basket_tickers": ("SPY", "QQQ", "IWM"),
        "bench_ticker": "SPY",
        "start": "2006-01-03", "end": "2026-04-15",
        "role": "20y combined; iter 041 stack + iter 039 basket; 2008+2020+2022 stress",
    },
    "spy_real": {
        "stack_eq": "SPY", "stack_bd": "IEF", "stack_gld": "GLD",
        "basket_tickers": ("SPY", "QQQ", "IWM"),
        "bench_ticker": "SPY",
        "start": "2009-06-25", "end": "2026-04-15",
        "role": "17y post-GFC combined",
    },
    "ndx_real": {
        "stack_eq": "SPY", "stack_bd": "IEF", "stack_gld": "GLD",
        "basket_tickers": ("SPY", "QQQ", "IWM"),
        "bench_ticker": "QQQ",
        "start": "2010-02-12", "end": "2026-04-15",
        "role": "16y; bench QQQ; iter 041 stack on SPY + iter 039 basket SPY/QQQ/IWM",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_vix_aligned(index: pd.DatetimeIndex) -> pd.Series:
    vix = pd.read_parquet(VIX_PATH)["VIX"]
    aligned = vix.reindex(index).ffill().bfill()
    if aligned.isna().any():
        raise ValueError("VIX alignment left NaN after ffill/bfill")
    return aligned.astype(float)


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


def run_one_dataset(
    stack_prices: dict[str, pd.Series],
    basket_prices: dict[str, pd.Series],
    vix: pd.Series,
) -> tuple[dict, pd.Series, pd.Series]:
    """Returns (metrics_dict, iter048_returns, iter046_baseline_returns)."""
    # iter 046 baseline (50/50 on the regime-gated stack + VRP basket).
    combined_046, r_041, r_039 = compute_combined_returns(
        stack_prices["eq"], stack_prices["bd"], stack_prices["gld"],
        basket_prices, vix,
        w_041=SHARED_PARAMS["w_041"], w_039=SHARED_PARAMS["w_039"],
        calm_weights=SHARED_PARAMS["calm_weights"],
        stress_weights=SHARED_PARAMS["stress_weights"],
        vix_threshold=SHARED_PARAMS["vix_threshold_inner"],
        cost_bps_per_leg=SHARED_PARAMS["cost_bps_per_leg"],
        rf=SHARED_PARAMS["rf"],
        harvest_notional=SHARED_PARAMS["harvest_notional"],
        weights=SHARED_PARAMS["weights_039"],
        iv_scales=SHARED_PARAMS["iv_scales"],
        k_long_pct=SHARED_PARAMS["k_long_pct"],
        k_short_pct=SHARED_PARAMS["k_short_pct"],
        dte_days=SHARED_PARAMS["dte_days"],
        cost_bps_per_roll=SHARED_PARAMS["cost_bps_per_roll"],
    )

    # iter 048: apply output-side VIX-regime leverage gate on combined_046.
    iter048_returns = apply_output_lev_gate(
        combined_046, vix,
        lev_calm=CFG["lev_calm"],
        lev_stress=CFG["lev_stress"],
        vix_threshold=CFG["vix_threshold_lev"],
    )
    eq_curve = (1.0 + iter048_returns).cumprod()

    spy = stack_prices["eq"]
    spy_ret = spy.pct_change().dropna()
    common = iter048_returns.index.intersection(spy_ret.index)
    corr_iter048_spy = float(iter048_returns.loc[common].corr(spy_ret.loc[common]))
    corr_iter048_046 = float(iter048_returns.corr(combined_046))

    # Calm/stress regime stats on the LAGGED VIX series (matches engine).
    vix_aligned = vix.reindex(combined_046.index).ffill().bfill()
    vix_lag = vix_aligned.shift(1).bfill()
    is_calm = (vix_lag < CFG["vix_threshold_lev"]).to_numpy()
    n_calm = int(is_calm.sum())
    n_stress = int(len(is_calm) - n_calm)
    frac_calm = float(n_calm / len(is_calm))

    rolling21_min = float(iter048_returns.rolling(21).sum().min())

    m = {
        "cfg_id": CFG["cfg_id"],
        "lev_calm": CFG["lev_calm"],
        "lev_stress": CFG["lev_stress"],
        "vix_threshold_lev": CFG["vix_threshold_lev"],
        "shared_params": SHARED_PARAMS,
        "bars": int(len(iter048_returns)),
        "n_calm_bars": n_calm,
        "n_stress_bars": n_stress,
        "frac_calm": frac_calm,
        # iter 048 (output-levered) metrics
        "sharpe": float(_sharpe(iter048_returns)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_iter048_spy": corr_iter048_spy,
        "corr_iter048_046": corr_iter048_046,
        # iter 046 baseline (for delta computations)
        "iter046_sharpe": float(_sharpe(combined_046)),
        "iter046_cagr": float(_cagr((1.0 + combined_046).cumprod())),
        "iter046_mdd": float(_max_drawdown((1.0 + combined_046).cumprod())),
        # Sub-components for diagnostic reuse
        "r_041_sharpe": float(_sharpe(r_041)),
        "r_041_cagr": float(_cagr((1.0 + r_041).cumprod())),
        "r_041_mdd": float(_max_drawdown((1.0 + r_041).cumprod())),
        "r_039_sharpe": float(_sharpe(r_039)),
        "r_039_cagr": float(_cagr((1.0 + r_039).cumprod())),
        "r_039_mdd": float(_max_drawdown((1.0 + r_039).cumprod())),
        "rolling21_worst": rolling21_min,
    }
    return m, iter048_returns, combined_046


def cross_lib_check(
    stack_prices: dict[str, pd.Series],
    basket_prices: dict[str, pd.Series],
    vix: pd.Series,
) -> dict:
    """G7 parity: pandas-engine iter 048 vs pure-numpy reference iter 048.

    Composes iter 046's numpy ref + iter 048's numpy ref and compares to
    the pandas pipeline (iter 046 pandas engine + iter 048 pandas gate).
    """
    # --- pandas pipeline ---
    combined_pd, _, _ = compute_combined_returns(
        stack_prices["eq"], stack_prices["bd"], stack_prices["gld"],
        basket_prices, vix,
        w_041=SHARED_PARAMS["w_041"], w_039=SHARED_PARAMS["w_039"],
        calm_weights=SHARED_PARAMS["calm_weights"],
        stress_weights=SHARED_PARAMS["stress_weights"],
        vix_threshold=SHARED_PARAMS["vix_threshold_inner"],
        cost_bps_per_leg=SHARED_PARAMS["cost_bps_per_leg"],
        rf=SHARED_PARAMS["rf"],
        harvest_notional=SHARED_PARAMS["harvest_notional"],
        weights=SHARED_PARAMS["weights_039"],
        iv_scales=SHARED_PARAMS["iv_scales"],
        k_long_pct=SHARED_PARAMS["k_long_pct"],
        k_short_pct=SHARED_PARAMS["k_short_pct"],
        dte_days=SHARED_PARAMS["dte_days"],
        cost_bps_per_roll=SHARED_PARAMS["cost_bps_per_roll"],
    )
    iter048_pd = apply_output_lev_gate(
        combined_pd, vix,
        lev_calm=CFG["lev_calm"],
        lev_stress=CFG["lev_stress"],
        vix_threshold=CFG["vix_threshold_lev"],
    )

    # --- numpy pipeline ---
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
    vix_for_regime_np = vix_aligned.iloc[1:].to_numpy(float)

    combined_np, _, _ = compute_combined_returns_np(
        r_eq_np, r_bd_np, r_gld_np,
        vix_for_regime_np,
        basket_np, vix_full_np,
        w_041=SHARED_PARAMS["w_041"], w_039=SHARED_PARAMS["w_039"],
        calm_weights=SHARED_PARAMS["calm_weights"],
        stress_weights=SHARED_PARAMS["stress_weights"],
        vix_threshold=SHARED_PARAMS["vix_threshold_inner"],
        cost_bps_per_leg=SHARED_PARAMS["cost_bps_per_leg"],
        rf=SHARED_PARAMS["rf"],
        harvest_notional=SHARED_PARAMS["harvest_notional"],
        weights=SHARED_PARAMS["weights_039"],
        iv_scales=SHARED_PARAMS["iv_scales"],
        k_long_pct=SHARED_PARAMS["k_long_pct"],
        k_short_pct=SHARED_PARAMS["k_short_pct"],
        dte_days=SHARED_PARAMS["dte_days"],
        cost_bps_per_roll=SHARED_PARAMS["cost_bps_per_roll"],
    )

    # Align numpy vix to combined_np length (combined_np is on the
    # iter 046 inner-join — which is shorter than the full common index
    # by the iter 039 warmup). Take the matching tail.
    n = len(combined_np)
    vix_for_lev = vix_full_np[-n:]
    iter048_np = apply_output_lev_gate_np(
        combined_np, vix_for_lev,
        lev_calm=CFG["lev_calm"],
        lev_stress=CFG["lev_stress"],
        vix_threshold=CFG["vix_threshold_lev"],
    )

    # Compare the tails of equal length.
    n_compare = min(len(iter048_pd), len(iter048_np))
    pd_arr = iter048_pd.values[-n_compare:]
    np_arr = iter048_np[-n_compare:]
    eq_pd = np.cumprod(1.0 + pd_arr)
    eq_np = np.cumprod(1.0 + np_arr)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n_compare) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n_compare) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_arr - np_arr))),
        "n_bars_compared": int(n_compare),
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "shared_params": SHARED_PARAMS,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "subcomponent_returns": {},
        "crosslib": {},
        "pre_committed": True,
        "iter_label": "048-2026-04-25-0644-iter046-output-lev-gate",
        "n_cfgs": 1,
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
            f"[{ds_name}] {ds['stack_eq']}+{ds['stack_bd']}+{ds['stack_gld']}; "
            f"basket={','.join(ds['basket_tickers'])}; bench={ds['bench_ticker']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

        all_results["runs"][ds_name] = {}
        all_results["returns_series"][ds_name] = {}
        all_results["subcomponent_returns"][ds_name] = {}
        all_results["crosslib"][ds_name] = {}

        cfg_id = CFG["cfg_id"]
        print(f"\n=== {ds_name} — cfg {cfg_id} ===")
        m, iter048_returns, combined_046 = run_one_dataset(
            {"eq": eq_p, "bd": bd_p, "gld": gld_p}, basket_p, vix,
        )
        all_results["runs"][ds_name][cfg_id] = m
        all_results["returns_series"][ds_name][cfg_id] = {
            "index": [str(t.date()) for t in iter048_returns.index],
            "net_returns": [round(float(x), 10) for x in iter048_returns.tolist()],
        }
        all_results["subcomponent_returns"][ds_name][cfg_id] = {
            "iter046_baseline": {
                "index": [str(t.date()) for t in combined_046.index],
                "net_returns": [round(float(x), 10) for x in combined_046.tolist()],
            },
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        edge_046 = m["sharpe"] - m["iter046_sharpe"]
        cagr_uplift = m["cagr"] - m["iter046_cagr"]
        print(
            f"  iter 048 Sharpe={m['sharpe']:+.4f} "
            f"(Δ frozen {edge_frozen:+.4f}, Δ046 {edge_046:+.4f}) "
            f"CAGR={m['cagr']:+.2%} (Δ046 {cagr_uplift:+.2%}) "
            f"MDD={m['mdd']:.2%} "
            f"corr_iter046={m['corr_iter048_046']:+.4f}"
        )
        print(
            f"  iter 046 baseline Sharpe={m['iter046_sharpe']:+.4f} "
            f"CAGR={m['iter046_cagr']:+.2%} MDD={m['iter046_mdd']:.2%} "
            f"| calm_frac={m['frac_calm']:.2%} "
            f"({m['n_calm_bars']}/{m['bars']} bars)"
        )

        cl = cross_lib_check(
            {"eq": eq_p, "bd": bd_p, "gld": gld_p}, basket_p, vix,
        )
        all_results["crosslib"][ds_name][cfg_id] = cl
        print(
            f"    G7 cross-lib: pd={cl['cagr_pandas']:+.4%} "
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
