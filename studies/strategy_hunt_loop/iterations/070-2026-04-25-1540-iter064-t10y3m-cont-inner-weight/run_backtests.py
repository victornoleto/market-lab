"""Iter 070 — Apply continuous T10Y3M z-score inner-weight blend on iter 064 streams.

Single pre-committed cfg ``iter064_t10y3m_cont_alpha025_lb1260_w005_020``
(N=1, no grid). cumulative_n_trials advance: 4339 → 4340 (+1).

Loads (per dataset):
* iter 046 saved combined return stream `r_046`
* QQQ adjusted-close prices (Tiingo) → Faber 2007 200d trend `r_qqqt`
* T10Y3M term spread (data/external/macro/t10y3m_daily.parquet)
* iter 064 saved combined stream (for Δ064 diagnostics)
* VIX (for KILL-J orthogonality diagnostic)

Saves daily net returns + sub-component returns + cross-lib parity +
KILL diagnostics to ``results.json``.

Citations
---------

* `[advances_fin_ml, ch.17-18]` — regime detection.
* `[regime_change, p.27, ch.3]` — continuous regime indicator.
* Faber (2007) SSRN 962461 — single-asset 200d SMA TAA.
* `[risk_parity, ch.5]` — iter 046 base preserved.
* Estrella & Mishkin (1998) RES 80(1):45-61 — T10Y3M as recession lead.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on regime signal.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
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

ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
ITER_069_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "069-2026-04-25-1518-iter064-vix-inner-weight-reverse"
sys.path.insert(0, str(ITER_064_DIR))

from t10y3m_cont_inner_weight import combine_with_t10y3m_cont_inner_weight  # noqa: E402
from numpy_reference_iter070 import combine_with_t10y3m_cont_inner_weight_np  # noqa: E402
from qqq_trend import compute_qqq_trend_returns  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
T10Y3M_PATH = ROOT / "data" / "external" / "macro" / "t10y3m_daily.parquet"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_046_RESULTS = ITER_046_DIR / "results.json"
ITER_064_RESULTS = ITER_064_DIR / "results.json"
ITER_069_RESULTS = ITER_069_DIR / "results.json"

CFG: dict = {
    "cfg_id": "iter064_t10y3m_cont_alpha025_lb1260_w005_020",
    "w_min": 0.05,
    "w_max": 0.20,
    "alpha": 0.25,
    "lookback_z": 1260,
    "cost_bps": 5.0,
    "qqqt_lookback": 200,
    "qqqt_rf": 0.02,
    "qqqt_cost_bps": 5.0,
    "rebalance": (
        "daily; z[t]=(T10Y3M[t-1]-rolling_mean_5y[t-1])/rolling_std_5y[t-1]; "
        "f(z)=clip(0.5-0.25z,0,1); w_qqqt[t]=0.05+0.15*f(z[t]); "
        "w_046[t]=1-w_qqqt[t]; flip_cost=5bp*|Δw_qqqt|"
    ),
    "primary_citation": (
        "[advances_fin_ml, ch.17-18] + [regime_change, p.27, ch.3] + "
        "Faber 2007 SSRN 962461 + [risk_parity, ch.5] + "
        "Estrella & Mishkin 1998 RES 80(1)"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; T10Y3M coverage 1982+ supports 5y warmup",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
        "iter069_cfg_id": "iter064_vix_inner_w_calm005_stress020_vix20",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC combined",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
        "iter069_cfg_id": "iter064_vix_inner_w_calm005_stress020_vix20",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; bench QQQ",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
        "iter069_cfg_id": "iter064_vix_inner_w_calm005_stress020_vix20",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_qqq_prices_with_warmup(start: str, end: str, warmup_days: int = 250) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / "QQQ.parquet")
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    extended_start = df.index[df.index <= start_ts]
    if len(extended_start) > warmup_days:
        extended_start = extended_start[-warmup_days]
    else:
        extended_start = df.index[0]
    m = (df.index >= extended_start) & (df.index <= end_ts)
    return df.loc[m, "adj_close"].astype(float)


def load_t10y3m() -> pd.Series:
    """Load T10Y3M term spread (FRED). 1982-01-04 onwards.

    NaNs (~480) are interspersed weekends/holidays — caller's
    ffill().bfill() inside the engine handles them.
    """
    df = pd.read_parquet(T10Y3M_PATH)
    df.index = pd.to_datetime(df.index)
    return df["term_spread"].astype(float)


def load_vix() -> pd.Series:
    """For KILL-J diagnostic only — confirm T10Y3M signal is orthogonal to VIX."""
    df = pd.read_parquet(VIX_PATH)
    df.index = pd.to_datetime(df.index)
    return df["VIX"].astype(float)


def load_iter046_returns(ds_name: str) -> pd.Series:
    if not ITER_046_RESULTS.exists():
        raise FileNotFoundError(f"iter 046 results.json not found at {ITER_046_RESULTS}")
    with ITER_046_RESULTS.open() as f:
        results = json.load(f)
    cfg_id = DATASETS[ds_name]["iter046_cfg_id"]
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name="r_046")


def load_iter064_returns(ds_name: str) -> pd.Series:
    if not ITER_064_RESULTS.exists():
        raise FileNotFoundError(f"iter 064 results.json not found at {ITER_064_RESULTS}")
    with ITER_064_RESULTS.open() as f:
        results = json.load(f)
    cfg_id = DATASETS[ds_name]["iter064_cfg_id"]
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name="r_064")


def load_iter069_returns(ds_name: str) -> pd.Series:
    if not ITER_069_RESULTS.exists():
        raise FileNotFoundError(f"iter 069 results.json not found at {ITER_069_RESULTS}")
    with ITER_069_RESULTS.open() as f:
        results = json.load(f)
    cfg_id = DATASETS[ds_name]["iter069_cfg_id"]
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name="r_069")


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
    r_046: pd.Series,
    qqq_prices_ext: pd.Series,
    spread: pd.Series,
    vix: pd.Series,
    r_064: pd.Series,
    r_069: pd.Series,
    window_start: str,
) -> tuple[dict, pd.Series, pd.Series]:
    r_qqqt_full = compute_qqq_trend_returns(
        qqq_prices_ext,
        lookback=CFG["qqqt_lookback"],
        rf=CFG["qqqt_rf"],
        cost_bps=CFG["qqqt_cost_bps"],
    )
    start_ts = pd.Timestamp(window_start)
    r_qqqt = r_qqqt_full[r_qqqt_full.index >= start_ts]

    out_diag = combine_with_t10y3m_cont_inner_weight(
        r_046, r_qqqt, spread,
        w_min=CFG["w_min"],
        w_max=CFG["w_max"],
        alpha=CFG["alpha"],
        lookback_z=CFG["lookback_z"],
        cost_bps=CFG["cost_bps"],
        return_diagnostics=True,
    )

    diag = out_diag.attrs["diagnostics"]
    w_qqqt = diag["w_qqqt"]
    delta_w = diag["delta_w"]
    z_arr = diag["z"]

    n_flips = int(np.sum(delta_w > 1e-12))
    years = len(out_diag) / 252.0
    flips_per_year = float(n_flips / years) if years > 0 else 0.0

    eq = (1.0 + out_diag).cumprod()

    obs_sharpe = float(_sharpe(out_diag))
    base_046_aligned = r_046.loc[out_diag.index]
    base_046_sharpe = float(_sharpe(base_046_aligned))
    base_046_cagr = float(_cagr((1 + base_046_aligned).cumprod()))

    base_064_aligned = r_064.reindex(out_diag.index).dropna()
    if len(base_064_aligned) >= len(out_diag) * 0.99:
        base_064_sharpe = float(_sharpe(base_064_aligned))
        base_064_cagr = float(_cagr((1 + base_064_aligned).cumprod()))
        base_064_mdd = float(_max_drawdown((1 + base_064_aligned).cumprod()))
        common_064 = out_diag.index.intersection(base_064_aligned.index)
        corr_070_064 = float(out_diag.loc[common_064].corr(base_064_aligned.loc[common_064]))
    else:
        base_064_sharpe = float("nan")
        base_064_cagr = float("nan")
        base_064_mdd = float("nan")
        corr_070_064 = float("nan")

    base_069_aligned = r_069.reindex(out_diag.index).dropna()
    if len(base_069_aligned) >= len(out_diag) * 0.99:
        base_069_sharpe = float(_sharpe(base_069_aligned))
        base_069_cagr = float(_cagr((1 + base_069_aligned).cumprod()))
        base_069_mdd = float(_max_drawdown((1 + base_069_aligned).cumprod()))
        common_069 = out_diag.index.intersection(base_069_aligned.index)
        corr_070_069 = float(out_diag.loc[common_069].corr(base_069_aligned.loc[common_069]))
    else:
        base_069_sharpe = float("nan")
        base_069_cagr = float("nan")
        base_069_mdd = float("nan")
        corr_070_069 = float("nan")

    # KILL-J diagnostic: T10Y3M signal vs VIX (orthogonality check).
    vix_aligned = vix.reindex(out_diag.index).ffill().bfill()
    vix_lag = vix_aligned.shift(1).bfill().to_numpy()
    spread_aligned = spread.reindex(out_diag.index).ffill().bfill()
    spread_lag = spread_aligned.shift(1).bfill().to_numpy()
    corr_z_vix = float(np.corrcoef(z_arr, vix_lag)[0, 1])
    corr_spread_vix = float(np.corrcoef(spread_lag, vix_lag)[0, 1])

    # z statistics — confirm regime activity.
    z_mean = float(np.mean(z_arr))
    z_std = float(np.std(z_arr, ddof=0))
    z_min = float(np.min(z_arr))
    z_max = float(np.max(z_arr))

    m = {
        "cfg_id": CFG["cfg_id"],
        "w_min": CFG["w_min"],
        "w_max": CFG["w_max"],
        "alpha": CFG["alpha"],
        "lookback_z": CFG["lookback_z"],
        "cost_bps": CFG["cost_bps"],
        "bars": int(len(out_diag)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "n_flips": n_flips,
        "flips_per_year": flips_per_year,
        "mean_w_qqqt": float(np.mean(w_qqqt)),
        "std_w_qqqt": float(np.std(w_qqqt, ddof=0)),
        "min_w_qqqt": float(np.min(w_qqqt)),
        "max_w_qqqt": float(np.max(w_qqqt)),
        "max_total_exposure_dev": float(np.max(np.abs(diag["w_046"] + w_qqqt - 1.0))),
        "z_mean": z_mean,
        "z_std": z_std,
        "z_min": z_min,
        "z_max": z_max,
        "corr_z_vix_lag": corr_z_vix,
        "corr_spread_vix_lag": corr_spread_vix,
        "base_046_sharpe": base_046_sharpe,
        "base_046_cagr": base_046_cagr,
        "base_064_sharpe": base_064_sharpe,
        "base_064_cagr": base_064_cagr,
        "base_064_mdd": base_064_mdd,
        "base_069_sharpe": base_069_sharpe,
        "base_069_cagr": base_069_cagr,
        "base_069_mdd": base_069_mdd,
        "sharpe_delta_064": (obs_sharpe - base_064_sharpe) if not np.isnan(base_064_sharpe) else float("nan"),
        "cagr_delta_064": (float(_cagr(eq)) - base_064_cagr) if not np.isnan(base_064_cagr) else float("nan"),
        "mdd_delta_064": (float(_max_drawdown(eq)) - base_064_mdd) if not np.isnan(base_064_mdd) else float("nan"),
        "sharpe_delta_069": (obs_sharpe - base_069_sharpe) if not np.isnan(base_069_sharpe) else float("nan"),
        "cagr_delta_069": (float(_cagr(eq)) - base_069_cagr) if not np.isnan(base_069_cagr) else float("nan"),
        "mdd_delta_069": (float(_max_drawdown(eq)) - base_069_mdd) if not np.isnan(base_069_mdd) else float("nan"),
        "corr_070_064": corr_070_064,
        "corr_070_069": corr_070_069,
    }
    return m, out_diag, r_qqqt


def cross_lib_check(
    r_046: pd.Series, qqq_prices_ext: pd.Series, spread: pd.Series, window_start: str
) -> dict:
    r_qqqt_full = compute_qqq_trend_returns(
        qqq_prices_ext,
        lookback=CFG["qqqt_lookback"],
        rf=CFG["qqqt_rf"],
        cost_bps=CFG["qqqt_cost_bps"],
    )
    start_ts = pd.Timestamp(window_start)
    r_qqqt = r_qqqt_full[r_qqqt_full.index >= start_ts]

    pd_out = combine_with_t10y3m_cont_inner_weight(
        r_046, r_qqqt, spread,
        w_min=CFG["w_min"], w_max=CFG["w_max"],
        alpha=CFG["alpha"], lookback_z=CFG["lookback_z"],
        cost_bps=CFG["cost_bps"],
    )
    common = pd_out.index
    a = r_046.loc[common].to_numpy()
    b = r_qqqt.loc[common].to_numpy()
    s_aligned = spread.reindex(common).ffill().bfill().to_numpy()

    np_out = combine_with_t10y3m_cont_inner_weight_np(
        a, b, s_aligned,
        w_min=CFG["w_min"], w_max=CFG["w_max"],
        alpha=CFG["alpha"], lookback_z=CFG["lookback_z"],
        cost_bps=CFG["cost_bps"],
    )

    eq_pd = np.cumprod(1.0 + pd_out.to_numpy())
    eq_np = np.cumprod(1.0 + np_out)
    n = len(eq_pd)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_out.to_numpy() - np_out))),
        "n_bars_compared": n,
    }


def main() -> None:
    spread = load_t10y3m()
    vix = load_vix()
    print(f"T10Y3M loaded: {spread.index[0].date()} → {spread.index[-1].date()} ({len(spread)} bars, {spread.isna().sum()} NaN)")
    print(f"VIX loaded:   {vix.index[0].date()} → {vix.index[-1].date()} ({len(vix)} bars)")

    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "subcomponent_returns": {},
        "crosslib": {},
        "pre_committed": True,
        "iter_label": "070-2026-04-25-1540-iter064-t10y3m-cont-inner-weight",
    }

    for ds_name, ds in DATASETS.items():
        r_046 = load_iter046_returns(ds_name)
        r_064 = load_iter064_returns(ds_name)
        r_069 = load_iter069_returns(ds_name)
        qqq_ext = load_qqq_prices_with_warmup(ds["start"], ds["end"], warmup_days=250)

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"\n[{ds_name}] r_046 {r_046.index[0].date()} → "
            f"{r_046.index[-1].date()} ({len(r_046)} bars), "
            f"r_064 {len(r_064)} bars, r_069 {len(r_069)} bars, "
            f"QQQ ext {len(qqq_ext)} bars, "
            f"bench={ds['bench_ticker']} S={bench['sharpe']:.3f} "
            f"CAGR={bench['cagr']:.2%}"
        )

        m, combined, r_qqqt = run_single_cfg(
            r_046, qqq_ext, spread, vix, r_064, r_069, ds["start"]
        )

        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 12) for x in combined.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_046": {
                "index": [str(t.date()) for t in r_046.index],
                "net_returns": [round(float(x), 12) for x in r_046.tolist()],
            },
            "r_qqq_trend": {
                "index": [str(t.date()) for t in r_qqqt.index],
                "net_returns": [round(float(x), 12) for x in r_qqqt.tolist()],
            },
        }

        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        print(
            f"  iter 070 S={m['sharpe']:+.4f} "
            f"(Δ frozen {edge_frozen:+.4f}, "
            f"Δ064 {m['sharpe_delta_064']:+.4f}, "
            f"Δ069 {m['sharpe_delta_069']:+.4f}) "
            f"CAGR={m['cagr']:+.2%} "
            f"(Δ064 {m['cagr_delta_064']:+.2%}, "
            f"Δ069 {m['cagr_delta_069']:+.2%}) "
            f"MDD={m['mdd']:.2%} "
            f"(Δ064 {m['mdd_delta_064']:+.2%}, "
            f"Δ069 {m['mdd_delta_069']:+.2%})"
        )
        print(
            f"  flips/yr={m['flips_per_year']:.1f}  "
            f"mean_w_qqqt={m['mean_w_qqqt']:.4f}  "
            f"std_w_qqqt={m['std_w_qqqt']:.4f}  "
            f"w_qqqt range=[{m['min_w_qqqt']:.4f}, {m['max_w_qqqt']:.4f}]  "
            f"max|Σw-1|={m['max_total_exposure_dev']:.2e}"
        )
        print(
            f"  z stats: mean={m['z_mean']:+.3f} std={m['z_std']:.3f} "
            f"range=[{m['z_min']:+.2f}, {m['z_max']:+.2f}]  "
            f"corr(z, VIX_lag)={m['corr_z_vix_lag']:+.3f}  "
            f"corr(spread_lag, VIX_lag)={m['corr_spread_vix_lag']:+.3f}"
        )
        print(
            f"  corr(070, 064)={m['corr_070_064']:+.4f}  "
            f"corr(070, 069)={m['corr_070_069']:+.4f}"
        )

        cl = cross_lib_check(r_046, qqq_ext, spread, ds["start"])
        all_results["crosslib"][ds_name] = cl
        print(
            f"  G7 cross-lib: CAGR pd={cl['cagr_pandas']:+.4%} "
            f"np={cl['cagr_numpy']:+.4%} Δ={cl['abs_diff_pp']:.4f} pp "
            f"(max ret diff {cl['max_abs_return_diff']:.2e})"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
