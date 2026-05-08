"""Iter 079 — Run multi-asset top-K momentum on 3 datasets × 9 cfgs.

Architecture
------------
1. Load SPY/QQQ/EFA/TLT/GLD/AGG prices for each dataset window.
2. Compute monthly rebalance dates (last business day of each month).
3. Compute monthly trailing-return DataFrame for the 5 selectable
   assets (one column per asset, NaN warmup rows for short history).
4. Per cfg (lookback × top_k):
   a. top_k_signal → monthly weight DataFrame (6 columns including AGG).
   b. compute_topk_returns → daily net returns (T-1 lag + cost).
   c. cross-lib parity check (pandas vs numpy).
5. Save returns_series + per-cfg metrics + crosslib parity + signal
   diagnostics.

n_trials_per_iter = 9 (per-iteration v2 DSR convention).
cumulative_n_trials advance: 4546 → 4573 (+27 = 9 cfgs × 3 datasets).
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

from multi_asset_topk_momentum import (  # noqa: E402
    ALL_SLEEVES,
    SELECTABLE_ASSETS,
    compute_lookback_returns_multi,
    compute_topk_returns,
    top_k_signal,
)
from numpy_reference_iter079 import compute_topk_returns_np  # noqa: E402

from market_lab.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

ANNUALIZATION = 252
TRANS_COST_BPS = 5.0
ABS_THRESHOLD = 0.0  # fixed at 0% per hypothesis (drop iter 078's IEF variant)
LOOKBACKS = [3, 6, 12]
TOP_KS = [1, 2, 3]


def cfg_id_for(lb: int, k: int) -> str:
    return f"iter079_topk_lb{lb:02d}m_k{k}"


CONFIGS: list[dict] = [
    {
        "cfg_id": cfg_id_for(lb, k),
        "lookback_months": int(lb),
        "top_k": int(k),
        "abs_threshold": float(ABS_THRESHOLD),
        "trans_cost_bps": float(TRANS_COST_BPS),
        "primary_citation": (
            "[stocks_on_the_move, p.21-30, p.81] "
            "+ Antonacci (2014) Dual Momentum Investing ISBN 978-0071849449 "
            "+ Faber (2007) JWM 9(4) DOI 10.3905/jwm.2007.690606 "
            "+ Jegadeesh-Titman (1993) JoF 48(1) "
            "+ Asness-Moskowitz-Pedersen (2013) JoF 68(3) "
            "+ [systematic_trading, p.42 (ch.2)] "
            "+ [advances_fin_ml, p.162-164, p.31-34]"
        ),
    }
    for lb in LOOKBACKS for k in TOP_KS
]

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2007-01-03",
        "end": "2026-04-15",
        "role": "19y SPY-bench; spans 2008 GFC + 2011 EU debt + 2020 COVID + 2022 bear",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC bull; iter 078 failed CAGR floor 11.42% < 11.98% here",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; QQQ-bench (hostile test for any defensive overlay)",
    },
}

SYMBOLS = ALL_SLEEVES  # SPY, QQQ, EFA, TLT, GLD, AGG


def load_prices_window(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(ROOT / "data" / "tiingo" / "daily" / "prices" / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


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


def signal_diagnostics(signal_df: pd.DataFrame) -> dict:
    """Diagnostics for the multi-asset top-K signal.

    Computes:
      - n_signals: number of rebalance rows with any non-zero allocation
      - n_flips: number of rows where the weight vector changes from
        the previous row (any change in any sleeve)
      - frac_per_asset: average weight per sleeve across active rows
        (also counts as % of months that asset received non-zero weight)
      - frac_agg: aggregate AGG share averaged across rows
      - n_spy_qqq_combined_pct: spy+qqq combined weight (KILL A diagnostic)
    """
    s = signal_df.dropna(how="all")
    s = s[s.sum(axis=1) > 0.5]  # only count active rows
    n = len(s)
    if n == 0:
        return {"n_signals": 0}
    # Flips: any change row-to-row in any sleeve weight (vectorized)
    diffs = (s.values[1:] - s.values[:-1])
    flips = int((np.abs(diffs).sum(axis=1) > 1e-9).sum())
    frac_per_asset = {a: float(s[a].mean()) for a in ALL_SLEEVES}
    frac_active_per_asset = {a: float((s[a] > 1e-9).mean()) for a in ALL_SLEEVES}
    spy_qqq_combined_avg = float((s["SPY"] + s["QQQ"]).mean())
    return {
        "n_signals": n,
        "n_flips": flips,
        "frac_per_asset_avg_weight": frac_per_asset,
        "frac_active_per_asset": frac_active_per_asset,
        "frac_agg": frac_per_asset["AGG"],
        "spy_qqq_combined_avg_weight": spy_qqq_combined_avg,
    }


def cross_lib_check(
    daily_returns: dict[str, pd.Series],
    signal_df: pd.DataFrame,
    trans_cost_bps: float,
) -> dict:
    pd_out = compute_topk_returns(daily_returns, signal_df, trans_cost_bps=trans_cost_bps)
    daily_idx = daily_returns["SPY"].index
    sig_ordered = signal_df.reindex(columns=ALL_SLEEVES, fill_value=0.0).sort_index()
    np_out = compute_topk_returns_np(
        asset_returns={a: daily_returns[a].values for a in ALL_SLEEVES},
        asset_order=ALL_SLEEVES,
        daily_dates=daily_idx.values,
        signal_dates=sig_ordered.index.values,
        signal_weights=sig_ordered.values,
        trans_cost_bps=trans_cost_bps,
    )
    eq_pd = np.cumprod(1.0 + pd_out.values)
    eq_np = np.cumprod(1.0 + np_out)
    n = len(pd_out)
    cagr_pd = float(eq_pd[-1]) ** (ANNUALIZATION / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (ANNUALIZATION / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_out.values - np_out))),
        "n_bars_compared": n,
    }


def run_single_cfg(
    daily_rets: dict[str, pd.Series],
    monthly_prices: dict[str, pd.Series],
    bench_returns: pd.Series,
    cfg: dict,
) -> tuple[dict, pd.Series, pd.DataFrame]:
    lb = cfg["lookback_months"]
    k = cfg["top_k"]
    lookback_df = compute_lookback_returns_multi(monthly_prices, lookback_months=lb)
    sig_df = top_k_signal(
        lookback_df, top_k=k, abs_threshold=cfg["abs_threshold"],
    )
    diag = signal_diagnostics(sig_df)
    combined = compute_topk_returns(
        daily_rets, sig_df, trans_cost_bps=cfg["trans_cost_bps"],
    )
    eq_curve = (1.0 + combined).cumprod()
    bench_a = bench_returns.reindex(combined.index).fillna(0.0)
    corr_bench = float(combined.corr(bench_a))
    sleeve_sharpe_proxy = float(_sharpe(combined))
    m = {
        "cfg_id": cfg["cfg_id"],
        "lookback_months": lb,
        "top_k": k,
        "abs_threshold": cfg["abs_threshold"],
        "bars": int(len(combined)),
        "sharpe": sleeve_sharpe_proxy,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_strategy_bench": corr_bench,
        "signal_diagnostics": diag,
    }
    return m, combined, sig_df


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": CONFIGS,
        "params": {
            "trans_cost_bps": TRANS_COST_BPS,
            "abs_threshold": ABS_THRESHOLD,
            "lookbacks": LOOKBACKS,
            "top_ks": TOP_KS,
            "selectable_assets": SELECTABLE_ASSETS,
            "fallback_asset": "AGG",
        },
        "benchmarks": {},
        "runs": {ds: {} for ds in DATASETS},
        "returns_series": {ds: {} for ds in DATASETS},
        "crosslib": {ds: {} for ds in DATASETS},
        "signal_diagnostics": {ds: {} for ds in DATASETS},
        "pre_committed": True,
        "iter_label": "079-2026-04-26-1100-multi-asset-topk-momentum",
        "n_trials_per_iter": len(CONFIGS),
    }

    for ds_name, ds in DATASETS.items():
        # 24-month look-behind for 12-mo lookback warmup.
        load_start = (
            pd.Timestamp(ds["start"]) - pd.Timedelta(days=550)
        ).strftime("%Y-%m-%d")
        prices_full = {sym: load_prices_window(sym, load_start, ds["end"])
                       for sym in SYMBOLS}

        common_daily = prices_full["SPY"].index
        for sym in SYMBOLS[1:]:
            common_daily = common_daily.intersection(prices_full[sym].index)
        daily_idx = common_daily[
            (common_daily >= pd.Timestamp(ds["start"]))
            & (common_daily <= pd.Timestamp(ds["end"]))
        ]
        full_idx = common_daily[common_daily <= pd.Timestamp(ds["end"])]

        daily_rets: dict[str, pd.Series] = {}
        for sym in SYMBOLS:
            ret = prices_full[sym].pct_change()
            daily_rets[sym] = ret.reindex(daily_idx).fillna(0.0)

        monthly_prices: dict[str, pd.Series] = {}
        for sym in SYMBOLS:
            p = prices_full[sym].reindex(full_idx).ffill()
            mp = p.resample("ME").last().dropna()
            monthly_prices[sym] = mp

        bench_p = load_prices_window(ds["bench_ticker"], ds["start"], ds["end"])
        bench_p = bench_p.reindex(daily_idx).ffill()
        bench_series = bench_p.pct_change().fillna(0.0)
        bench_series = bench_series.iloc[1:] if len(bench_series) > 0 else bench_series
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench

        for cfg in CONFIGS:
            m, combined, sig_df = run_single_cfg(
                daily_rets, monthly_prices, bench_series, cfg,
            )
            all_results["runs"][ds_name][cfg["cfg_id"]] = m
            all_results["signal_diagnostics"][ds_name][cfg["cfg_id"]] = (
                m["signal_diagnostics"]
            )
            all_results["returns_series"][ds_name][cfg["cfg_id"]] = {
                "index": [d.isoformat() for d in combined.index],
                "net_returns": combined.values.tolist(),
            }

            xlib = cross_lib_check(daily_rets, sig_df, cfg["trans_cost_bps"])
            all_results["crosslib"][ds_name][cfg["cfg_id"]] = xlib

            diag = m["signal_diagnostics"]
            print(
                f"  {ds_name:>11s} {cfg['cfg_id']:>30s} "
                f"S={m['sharpe']:.3f} CAGR={m['cagr']*100:5.2f}% "
                f"MDD={m['mdd']*100:5.2f}% "
                f"flips={diag.get('n_flips', 0):3d} "
                f"agg={diag.get('frac_agg', 0)*100:5.1f}% "
                f"spyqqq={diag.get('spy_qqq_combined_avg_weight', 0)*100:5.1f}% "
                f"xlib={xlib['abs_diff_pp']:.4f}pp"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
