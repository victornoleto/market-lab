"""Iter 068 — Apply VIX-conditional inner-weight blend on iter 046 + QQQ_TREND.

Single pre-committed cfg `iter064_vix_inner_w_calm020_stress005_vix20`,
no grid. cumulative_n_trials advance: 4337 → 4338 (+1).

Loads (per dataset):
* iter 046 saved combined return stream `r_046` (from iter 046 results.json)
* QQQ adjusted-close prices (Tiingo cache) → Faber 2007 200d trend `r_qqqt`
* VIX daily (data/external/macro/vix_daily.parquet)

Applies the iter 068 inner-weight combiner (see vix_inner_weight.py),
saves daily net returns + sub-component returns + cross-lib parity.

Citations
---------
* `[stocks_on_the_move, p.21-30]` — Clenow regime-conditional momentum.
* Faber (2007) SSRN 962461 — single-asset 200d SMA TAA.
* `[risk_parity, ch.5]` — iter 046 base preserved.
* Whaley 2009 / Bekaert-Hoerova 2014 — VIX threshold 20.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX.
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

# Reuse iter 064's QQQ_TREND module (Faber 2007 200d SMA filter)
ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
sys.path.insert(0, str(ITER_064_DIR))

from vix_inner_weight import combine_with_vix_inner_weight  # noqa: E402
from numpy_reference_iter068 import combine_with_vix_inner_weight_np  # noqa: E402
from qqq_trend import compute_qqq_trend_returns  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_046_RESULTS = ITER_046_DIR / "results.json"
ITER_064_RESULTS = ITER_064_DIR / "results.json"

CFG: dict = {
    "cfg_id": "iter064_vix_inner_w_calm020_stress005_vix20",
    "w_qqqt_calm": 0.20,
    "w_qqqt_stress": 0.05,
    "vix_threshold": 20.0,
    "cost_bps": 5.0,
    "qqqt_lookback": 200,
    "qqqt_rf": 0.02,
    "qqqt_cost_bps": 5.0,
    "rebalance": (
        "daily; w_qqqt[t]=0.20 if VIX[t-1]<20 else 0.05; "
        "w_046[t]=1-w_qqqt[t]; flip_cost=5bp*|Δw_qqqt|"
    ),
    "primary_citation": (
        "[stocks_on_the_move, p.21-30] + Faber 2007 SSRN 962461 + "
        "[risk_parity, ch.5] + Whaley 2009 JPM 35(3)"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; QQQ available 2001+ so warmup absorbs 200d",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC combined",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; bench QQQ",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
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


def load_vix() -> pd.Series:
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
    """Load iter 064's saved combined stream for Δ064 diagnostics."""
    if not ITER_064_RESULTS.exists():
        raise FileNotFoundError(f"iter 064 results.json not found at {ITER_064_RESULTS}")
    with ITER_064_RESULTS.open() as f:
        results = json.load(f)
    cfg_id = DATASETS[ds_name]["iter064_cfg_id"]
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name="r_064")


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


def conditional_sharpe_split(
    series: pd.Series, vix: pd.Series, threshold: float
) -> dict:
    """Compute Sharpe of `series` separately on calm vs stress bars
    (VIX[t-1] < threshold = calm). Useful diagnostic for KILL I."""
    vix_aligned = vix.reindex(series.index).ffill().bfill()
    vix_lag = vix_aligned.shift(1).bfill()
    calm_mask = (vix_lag < threshold).to_numpy()
    s = series.to_numpy()
    n_calm = int(calm_mask.sum())
    n_stress = int(len(s) - n_calm)
    if n_calm > 30:
        calm = s[calm_mask]
        sharpe_calm = float(np.mean(calm) / (np.std(calm, ddof=0) + 1e-18) * np.sqrt(252.0))
    else:
        sharpe_calm = float("nan")
    if n_stress > 30:
        stress = s[~calm_mask]
        sharpe_stress = float(np.mean(stress) / (np.std(stress, ddof=0) + 1e-18) * np.sqrt(252.0))
    else:
        sharpe_stress = float("nan")
    return {
        "n_calm": n_calm, "n_stress": n_stress,
        "pct_calm": float(n_calm / len(s)),
        "sharpe_calm": sharpe_calm, "sharpe_stress": sharpe_stress,
    }


def run_single_cfg(
    r_046: pd.Series,
    qqq_prices_ext: pd.Series,
    vix: pd.Series,
    r_064: pd.Series,
    window_start: str,
) -> tuple[dict, pd.Series, pd.Series]:
    """Apply iter 068 inner-weight gate to r_046 + r_qqqt; report
    diagnostics including Δ064, regime split, conditional Sharpes."""
    r_qqqt_full = compute_qqq_trend_returns(
        qqq_prices_ext,
        lookback=CFG["qqqt_lookback"],
        rf=CFG["qqqt_rf"],
        cost_bps=CFG["qqqt_cost_bps"],
    )
    start_ts = pd.Timestamp(window_start)
    r_qqqt = r_qqqt_full[r_qqqt_full.index >= start_ts]

    out_diag = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=CFG["w_qqqt_calm"],
        w_qqqt_stress=CFG["w_qqqt_stress"],
        vix_threshold=CFG["vix_threshold"],
        cost_bps=CFG["cost_bps"],
        return_diagnostics=True,
    )

    diag = out_diag.attrs["diagnostics"]
    w_qqqt = diag["w_qqqt"]
    delta_w = diag["delta_w"]

    n_flips = int(np.sum(delta_w > 0))
    years = len(out_diag) / 252.0
    flips_per_year = float(n_flips / years) if years > 0 else 0.0

    eq = (1.0 + out_diag).cumprod()

    obs_sharpe = float(_sharpe(out_diag))
    base_046_sharpe = float(_sharpe(r_046.loc[out_diag.index]))
    base_046_cagr = float(_cagr((1 + r_046.loc[out_diag.index]).cumprod()))
    base_064_aligned = r_064.reindex(out_diag.index).dropna()

    if len(base_064_aligned) >= len(out_diag) * 0.99:
        base_064_sharpe = float(_sharpe(base_064_aligned))
        base_064_cagr = float(_cagr((1 + base_064_aligned).cumprod()))
        base_064_mdd = float(_max_drawdown((1 + base_064_aligned).cumprod()))
        common_064 = out_diag.index.intersection(base_064_aligned.index)
        corr_068_064 = float(out_diag.loc[common_064].corr(base_064_aligned.loc[common_064]))
    else:
        base_064_sharpe = float("nan")
        base_064_cagr = float("nan")
        base_064_mdd = float("nan")
        corr_068_064 = float("nan")

    cs_046 = conditional_sharpe_split(r_046.loc[out_diag.index], vix, CFG["vix_threshold"])
    cs_qqqt = conditional_sharpe_split(r_qqqt.loc[out_diag.index], vix, CFG["vix_threshold"])

    m = {
        "cfg_id": CFG["cfg_id"],
        "w_qqqt_calm": CFG["w_qqqt_calm"],
        "w_qqqt_stress": CFG["w_qqqt_stress"],
        "vix_threshold": CFG["vix_threshold"],
        "cost_bps": CFG["cost_bps"],
        "bars": int(len(out_diag)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "pct_calm": float((w_qqqt == CFG["w_qqqt_calm"]).mean()),
        "n_flips": n_flips,
        "flips_per_year": flips_per_year,
        "mean_w_qqqt": float(np.mean(w_qqqt)),
        "max_total_exposure_dev": float(np.max(np.abs(diag["w_046"] + w_qqqt - 1.0))),
        "base_046_sharpe": base_046_sharpe,
        "base_046_cagr": base_046_cagr,
        "base_064_sharpe": base_064_sharpe,
        "base_064_cagr": base_064_cagr,
        "base_064_mdd": base_064_mdd,
        "sharpe_delta_064": (obs_sharpe - base_064_sharpe) if not np.isnan(base_064_sharpe) else float("nan"),
        "cagr_delta_064": (float(_cagr(eq)) - base_064_cagr) if not np.isnan(base_064_cagr) else float("nan"),
        "mdd_delta_064": (float(_max_drawdown(eq)) - base_064_mdd) if not np.isnan(base_064_mdd) else float("nan"),
        "corr_068_064": corr_068_064,
        "conditional_sharpe_046": cs_046,
        "conditional_sharpe_qqqt": cs_qqqt,
    }
    return m, out_diag, r_qqqt


def cross_lib_check(
    r_046: pd.Series, qqq_prices_ext: pd.Series, vix: pd.Series, window_start: str
) -> dict:
    """G7 parity: pandas vs numpy reference CAGR Δ ≤ 3 pp."""
    r_qqqt_full = compute_qqq_trend_returns(
        qqq_prices_ext,
        lookback=CFG["qqqt_lookback"],
        rf=CFG["qqqt_rf"],
        cost_bps=CFG["qqqt_cost_bps"],
    )
    start_ts = pd.Timestamp(window_start)
    r_qqqt = r_qqqt_full[r_qqqt_full.index >= start_ts]

    pd_out = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=CFG["w_qqqt_calm"],
        w_qqqt_stress=CFG["w_qqqt_stress"],
        vix_threshold=CFG["vix_threshold"],
        cost_bps=CFG["cost_bps"],
    )
    common = pd_out.index
    a = r_046.loc[common].to_numpy()
    b = r_qqqt.loc[common].to_numpy()
    v_aligned = vix.reindex(common).ffill().bfill().to_numpy()

    np_out = combine_with_vix_inner_weight_np(
        a, b, v_aligned,
        w_qqqt_calm=CFG["w_qqqt_calm"],
        w_qqqt_stress=CFG["w_qqqt_stress"],
        vix_threshold=CFG["vix_threshold"],
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
    vix = load_vix()
    print(f"VIX loaded: {vix.index[0].date()} → {vix.index[-1].date()} ({len(vix)} bars)")

    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "subcomponent_returns": {},
        "crosslib": {},
        "pre_committed": True,
        "iter_label": "068-2026-04-25-1758-iter064-vix-inner-weight-swap",
    }

    for ds_name, ds in DATASETS.items():
        r_046 = load_iter046_returns(ds_name)
        r_064 = load_iter064_returns(ds_name)
        qqq_ext = load_qqq_prices_with_warmup(ds["start"], ds["end"], warmup_days=250)

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"\n[{ds_name}] r_046 {r_046.index[0].date()} → "
            f"{r_046.index[-1].date()} ({len(r_046)} bars), "
            f"r_064 {len(r_064)} bars, QQQ ext {len(qqq_ext)} bars, "
            f"bench={ds['bench_ticker']} S={bench['sharpe']:.3f} "
            f"CAGR={bench['cagr']:.2%}"
        )

        m, combined, r_qqqt = run_single_cfg(r_046, qqq_ext, vix, r_064, ds["start"])

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
            f"  iter 068 S={m['sharpe']:+.4f} "
            f"(Δ frozen {edge_frozen:+.4f}, Δ064 {m['sharpe_delta_064']:+.4f}) "
            f"CAGR={m['cagr']:+.2%} (Δ064 {m['cagr_delta_064']:+.2%}) "
            f"MDD={m['mdd']:.2%} (Δ064 {m['mdd_delta_064']:+.2%}) "
            f"corr(068,064)={m['corr_068_064']:+.4f}"
        )
        print(
            f"  pct_calm={m['pct_calm']:.1%}  flips/yr={m['flips_per_year']:.1f}  "
            f"mean_w_qqqt={m['mean_w_qqqt']:.4f}  "
            f"max|Σw-1|={m['max_total_exposure_dev']:.2e}"
        )
        print(
            f"  cond Sharpe r_046:   calm={m['conditional_sharpe_046']['sharpe_calm']:+.3f}  "
            f"stress={m['conditional_sharpe_046']['sharpe_stress']:+.3f}"
        )
        print(
            f"  cond Sharpe r_qqqt:  calm={m['conditional_sharpe_qqqt']['sharpe_calm']:+.3f}  "
            f"stress={m['conditional_sharpe_qqqt']['sharpe_stress']:+.3f}"
        )

        cl = cross_lib_check(r_046, qqq_ext, vix, ds["start"])
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
