"""Iter 078 — Run Antonacci GEM standalone-base on 3 datasets × 8 cfgs.

Architecture
------------
1. Load SPY, EFA, AGG, IEF (T-bill proxy) prices for each dataset window.
2. Compute monthly rebalance dates (last business day of each month).
3. Compute monthly trailing-return per asset for the chosen lookback.
4. Per cfg (lookback × abs_threshold_source):
   a. Threshold series = 0.0 OR IEF trailing return.
   b. gem_signal → monthly allocation choice.
   c. compute_gem_returns → daily net returns.
   d. cross-lib parity check (pandas vs numpy).
5. Save returns_series + per-cfg metrics + crosslib parity.

n_trials_per_iter = 8 (per-iteration v2 DSR convention).
cumulative_n_trials advance: 4522 → 4546 (+24 = 8 cfgs × 3 datasets).
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

from antonacci_dual_momentum import (  # noqa: E402
    compute_gem_returns,
    compute_lookback_return,
    compute_monthly_rebalance_dates,
    gem_signal,
    load_price,
)
from numpy_reference_iter078 import compute_gem_returns_np  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

ANNUALIZATION = 252
TRANS_COST_BPS = 5.0
LOOKBACKS = [3, 6, 9, 12]
ABS_THRESHOLDS = ["zero", "ief"]


def cfg_id_for(lb: int, th: str) -> str:
    return f"iter078_gem_lb{lb:02d}m_th{th}"


CONFIGS: list[dict] = [
    {
        "cfg_id": cfg_id_for(lb, th),
        "lookback_months": int(lb),
        "abs_threshold_source": th,
        "trans_cost_bps": float(TRANS_COST_BPS),
        "primary_citation": (
            "Antonacci (2014) Dual Momentum Investing ISBN 978-0071849449 "
            "+ Antonacci (2017) JoPM 16(1) DOI 10.3905/joi.2017.16.1.027 "
            "+ Faber (2007) JWM 9(4) DOI 10.3905/jwm.2007.690606 "
            "+ Jegadeesh-Titman (1993) JoF 48(1) "
            "+ [stocks_on_the_move, p.21-30] "
            "+ [systematic_trading, p.42 (ch.2)] "
            "+ [advances_fin_ml, p.162-164, p.31-34]"
        ),
    }
    for lb in LOOKBACKS for th in ABS_THRESHOLDS
]

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2007-01-03",
        "end": "2026-04-15",
        "role": "19y SPY-bench; spans 2008 GFC + 2020 COVID + 2022 bear",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC bull-bias; defensive trigger less frequent",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; SPY/EFA/AGG universe vs QQQ bench (hostile test)",
    },
}


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


def signal_diagnostics(signal: pd.Series) -> dict:
    """Count signal flips, AGG-allocation pct, leg distribution."""
    s = signal.dropna()
    n = len(s)
    if n == 0:
        return {"n_signals": 0}
    flips = int((s.shift() != s).sum() - 1)  # subtract 1 for first NaN→val
    counts = s.value_counts().to_dict()
    return {
        "n_signals": n,
        "n_flips": max(flips, 0),
        "frac_spy": counts.get("SPY", 0) / n,
        "frac_efa": counts.get("EFA", 0) / n,
        "frac_agg": counts.get("AGG", 0) / n,
        "n_spy_efa_swaps": int(
            ((s == "SPY") & (s.shift() == "EFA")).sum()
            + ((s == "EFA") & (s.shift() == "SPY")).sum()
        ),
    }


def cross_lib_check(
    daily_returns: dict[str, pd.Series],
    signal: pd.Series,
    trans_cost_bps: float,
) -> dict:
    pd_out = compute_gem_returns(daily_returns, signal, trans_cost_bps=trans_cost_bps)
    daily_idx = daily_returns["SPY"].index
    np_out = compute_gem_returns_np(
        spy_returns=daily_returns["SPY"].values,
        efa_returns=daily_returns["EFA"].values,
        agg_returns=daily_returns["AGG"].values,
        daily_dates=daily_idx.values,
        signal_dates=signal.index.values,
        signal_choices=signal.values,
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
) -> tuple[dict, pd.Series, dict]:
    lb = cfg["lookback_months"]
    spy_lb = compute_lookback_return(monthly_prices["SPY"], lb)
    efa_lb = compute_lookback_return(monthly_prices["EFA"], lb)
    if cfg["abs_threshold_source"] == "ief":
        threshold = compute_lookback_return(monthly_prices["IEF"], lb)
    else:
        threshold = pd.Series(0.0, index=spy_lb.index)
    common = spy_lb.index.intersection(efa_lb.index).intersection(threshold.index)
    sig = gem_signal(
        spy_lb.loc[common], efa_lb.loc[common], threshold.loc[common],
    )
    diag = signal_diagnostics(sig)
    combined = compute_gem_returns(daily_rets, sig, trans_cost_bps=cfg["trans_cost_bps"])
    eq_curve = (1.0 + combined).cumprod()
    bench_a = bench_returns.reindex(combined.index).fillna(0.0)
    corr_bench = float(combined.corr(bench_a))
    sleeve_sharpe_proxy = float(_sharpe(combined))
    m = {
        "cfg_id": cfg["cfg_id"],
        "lookback_months": lb,
        "abs_threshold_source": cfg["abs_threshold_source"],
        "bars": int(len(combined)),
        "sharpe": sleeve_sharpe_proxy,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_strategy_bench": corr_bench,
        "signal_diagnostics": diag,
        # KILL B / kill diagnostics — track for compute_gates
        "r_sleeve_sharpe": sleeve_sharpe_proxy,
        "r_sleeve_cagr": float(_cagr(eq_curve)),
        "r_sleeve_mdd": float(_max_drawdown(eq_curve)),
        "corr_sleeve_bench": corr_bench,
    }
    return m, combined, diag


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": CONFIGS,
        "params": {
            "trans_cost_bps": TRANS_COST_BPS,
            "lookbacks": LOOKBACKS,
            "abs_threshold_sources": ABS_THRESHOLDS,
        },
        "benchmarks": {},
        "runs": {ds: {} for ds in DATASETS},
        "returns_series": {ds: {} for ds in DATASETS},
        "crosslib": {ds: {} for ds in DATASETS},
        "signal_diagnostics": {ds: {} for ds in DATASETS},
        "pre_committed": True,
        "iter_label": "078-2026-04-26-0210-antonacci-dual-momentum-base",
        "n_trials_per_iter": len(CONFIGS),
    }

    # We need a buffer pre-period to compute lookback returns at start date.
    # Load 18 months of pre-data per dataset to ensure 12-mo lookback warmup.
    SYMBOLS = ["SPY", "EFA", "AGG", "IEF"]

    for ds_name, ds in DATASETS.items():
        # Load asset prices with a 24-month look-behind so 12-mo lookback
        # is computable at the dataset's nominal start.
        load_start = (pd.Timestamp(ds["start"]) - pd.Timedelta(days=550)).strftime("%Y-%m-%d")
        prices_full = {sym: load_prices_window(sym, load_start, ds["end"]) for sym in SYMBOLS}

        # Daily returns aligned across SPY/EFA/AGG (trimmed to common dates).
        common_daily = (
            prices_full["SPY"].index
            .intersection(prices_full["EFA"].index)
            .intersection(prices_full["AGG"].index)
        )
        # Trim to dataset window (post-warmup, signals will start at first
        # rebalance date with valid lookback).
        daily_idx = common_daily[
            (common_daily >= pd.Timestamp(ds["start"]))
            & (common_daily <= pd.Timestamp(ds["end"]))
        ]
        # Pre-warm with the buffer period for monthly-price computation.
        full_idx = common_daily[common_daily <= pd.Timestamp(ds["end"])]

        # Daily returns (post-warmup window)
        daily_rets: dict[str, pd.Series] = {}
        for sym in ["SPY", "EFA", "AGG"]:
            ret = prices_full[sym].pct_change()
            daily_rets[sym] = ret.reindex(daily_idx).fillna(0.0)

        # Monthly prices (use the full pre-warm + post-warmup index, then
        # group by year-month and take last observation per month).
        monthly_prices: dict[str, pd.Series] = {}
        for sym in SYMBOLS:
            p = prices_full[sym].reindex(full_idx).ffill()
            mp = p.resample("ME").last().dropna()
            monthly_prices[sym] = mp

        # Benchmark returns on the dataset window.
        bench_p = load_prices_window(ds["bench_ticker"], ds["start"], ds["end"])
        # Align bench to the strategy's daily index so benchmark series and
        # strategy series live on identical dates (essential for the plot
        # helper and Markowitz consistency).
        bench_p = bench_p.reindex(daily_idx).ffill()
        bench_series = bench_p.pct_change().fillna(0.0)
        # Drop the leading day (no return).
        bench_series = bench_series.iloc[1:] if len(bench_series) > 0 else bench_series
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench

        for cfg in CONFIGS:
            m, combined, diag = run_single_cfg(
                daily_rets, monthly_prices, bench_series, cfg,
            )
            all_results["runs"][ds_name][cfg["cfg_id"]] = m
            all_results["signal_diagnostics"][ds_name][cfg["cfg_id"]] = diag
            all_results["returns_series"][ds_name][cfg["cfg_id"]] = {
                "index": [d.isoformat() for d in combined.index],
                "net_returns": combined.values.tolist(),
            }

            # Cross-lib parity (G7)
            lb = cfg["lookback_months"]
            spy_lb = compute_lookback_return(monthly_prices["SPY"], lb)
            efa_lb = compute_lookback_return(monthly_prices["EFA"], lb)
            if cfg["abs_threshold_source"] == "ief":
                threshold = compute_lookback_return(monthly_prices["IEF"], lb)
            else:
                threshold = pd.Series(0.0, index=spy_lb.index)
            common = spy_lb.index.intersection(efa_lb.index).intersection(threshold.index)
            sig = gem_signal(spy_lb.loc[common], efa_lb.loc[common], threshold.loc[common])
            xlib = cross_lib_check(daily_rets, sig, cfg["trans_cost_bps"])
            all_results["crosslib"][ds_name][cfg["cfg_id"]] = xlib

            print(
                f"  {ds_name:>11s} {cfg['cfg_id']:>30s} "
                f"S={m['sharpe']:.3f} CAGR={m['cagr']*100:5.2f}% "
                f"MDD={m['mdd']*100:5.2f}% "
                f"flips={diag['n_flips']:3d} agg={diag['frac_agg']*100:5.1f}% "
                f"xlib={xlib['abs_diff_pp']:.4f}pp"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
