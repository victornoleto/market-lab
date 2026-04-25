"""Iter 064 — Run iter 046 + QQQ-200d-trend (w_046=0.9, w_qqqt=0.1) on 3 datasets.

Single pre-committed cfg `iter046_plus_qqq_trend_w010_lookback200`. No grid.
cumulative_n_trials advance: 4333 → 4334 (+1).

Loads the iter 046 saved combined return stream (from
`iterations/046-*/results.json`) and the QQQ adjusted-close prices
(Tiingo cache), computes QQQ_TREND via 200-day SMA filter, then forms
0.9·iter_046 + 0.1·QQQ_TREND inner-joined daily returns.

Citations
---------
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base
  preserved verbatim via its saved return stream.
* Faber (2007) SSRN 962461 — single-asset 200-day SMA TAA primitive.
* `[stocks_on_the_move, p.21-30]` (Clenow) — 200d SMA as regime gate.
* `[systematic_trading]` (Carver) — generic boolean TSM rule.
* Moskowitz-Ooi-Pedersen (2012) JFE 104(2) DOI 10.1016/j.jfineco.2011.11.003.
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

from qqq_trend import compute_qqq_trend_returns  # noqa: E402
from numpy_reference_iter064 import compute_qqq_trend_returns_np  # noqa: E402
from combined_046_plus_qqqt import combine_046_plus_qqqt  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_046_RESULTS = ITER_046_DIR / "results.json"

CFG: dict = {
    "cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    "w_046": 0.9,
    "w_qqqt": 0.1,
    "qqqt_ticker": "QQQ",
    "lookback": 200,
    "rf": 0.02,
    "cost_bps": 5.0,
    "rebalance": "daily; QQQ long iff price[t-1] > SMA_200(price)[t-1]",
    "primary_citation": (
        "Faber 2007 SSRN 962461 + [stocks_on_the_move, p.21-30] + "
        "[risk_parity, ch.5] + [volatility_trading, p.218]"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; QQQ available 2001+ so warmup absorbs 200d",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC combined",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; bench QQQ",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_qqq_prices_with_warmup(start: str, end: str, warmup_days: int = 250) -> pd.Series:
    """Load QQQ prices with extra warmup window so SMA is well-defined at start."""
    df = pd.read_parquet(TIINGO_DIR / "QQQ.parquet")
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    # Extend start backward by ~warmup_days trading days for SMA warmup
    extended_start = df.index[df.index <= start_ts]
    if len(extended_start) > warmup_days:
        extended_start = extended_start[-warmup_days]
    else:
        extended_start = df.index[0]
    m = (df.index >= extended_start) & (df.index <= end_ts)
    return df.loc[m, "adj_close"].astype(float)


def load_iter046_returns(ds_name: str) -> pd.Series:
    if not ITER_046_RESULTS.exists():
        raise FileNotFoundError(
            f"iter 046 results.json not found at {ITER_046_RESULTS}"
        )
    with ITER_046_RESULTS.open() as f:
        results = json.load(f)
    cfg_id = DATASETS[ds_name]["iter046_cfg_id"]
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name="r_046")


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


def markowitz_residual(
    r_a: pd.Series, r_b: pd.Series, *, w_a: float, w_b: float, observed_sharpe: float,
) -> tuple[float, dict]:
    """Closed-form Sharpe of convex combo, residual vs observed."""
    common = r_a.index.intersection(r_b.index)
    a = r_a.loc[common].values
    b = r_b.loc[common].values
    mu_a = float(np.mean(a))
    mu_b = float(np.mean(b))
    var_a = float(np.var(a, ddof=0))
    var_b = float(np.var(b, ddof=0))
    cov_ab = float(np.cov(a, b, ddof=0)[0, 1])
    mu_p = w_a * mu_a + w_b * mu_b
    var_p = (w_a ** 2) * var_a + (w_b ** 2) * var_b + 2 * w_a * w_b * cov_ab
    sigma_p = float(np.sqrt(var_p))
    formula_sharpe = (mu_p / sigma_p) * np.sqrt(252.0) if sigma_p > 1e-12 else 0.0
    return observed_sharpe - formula_sharpe, {
        "formula_sharpe": float(formula_sharpe),
        "observed_sharpe": float(observed_sharpe),
        "mu_a": mu_a, "mu_b": mu_b,
        "sigma_a": float(np.sqrt(var_a)), "sigma_b": float(np.sqrt(var_b)),
        "corr_ab": float(cov_ab / (np.sqrt(var_a * var_b) + 1e-18)),
        "n_bars_used": int(len(common)),
    }


def run_single_cfg(
    r_046: pd.Series,
    qqq_prices_ext: pd.Series,
    window_start: str,
) -> tuple[dict, pd.Series, pd.Series]:
    """Compute QQQ trend over the extended (warmup-included) window, then
    slice to the dataset window so warmup is fully absorbed before window_start."""
    r_qqqt_full = compute_qqq_trend_returns(
        qqq_prices_ext,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    # Slice qqq_trend to dataset window (warmup happened in extended pre-window)
    start_ts = pd.Timestamp(window_start)
    r_qqqt = r_qqqt_full[r_qqqt_full.index >= start_ts]

    combined = combine_046_plus_qqqt(
        r_046, r_qqqt, w_046=CFG["w_046"], w_qqqt=CFG["w_qqqt"],
    )
    eq_curve = (1.0 + combined).cumprod()

    common = combined.index.intersection(r_046.index).intersection(r_qqqt.index)
    r_046_aligned = r_046.loc[common]
    r_qqqt_aligned = r_qqqt.loc[common]

    corr_046_qqqt = float(r_046_aligned.corr(r_qqqt_aligned))
    corr_combined_046 = float(combined.loc[common].corr(r_046_aligned))

    rolling21_min = float(combined.rolling(21).sum().min())

    obs_sharpe = float(_sharpe(combined))
    residual, mw_detail = markowitz_residual(
        r_046_aligned, r_qqqt_aligned,
        w_a=CFG["w_046"], w_b=CFG["w_qqqt"],
        observed_sharpe=obs_sharpe,
    )

    rf_d = (1.0 + CFG["rf"]) ** (1 / 252.0) - 1.0
    pct_long = float((r_qqqt_aligned != rf_d).mean())

    m = {
        "cfg_id": CFG["cfg_id"],
        "w_046": CFG["w_046"], "w_qqqt": CFG["w_qqqt"],
        "lookback": CFG["lookback"],
        "rf": CFG["rf"], "cost_bps": CFG["cost_bps"],
        "bars": int(len(combined)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_046_qqqt": corr_046_qqqt,
        "corr_combined_046": corr_combined_046,
        "r_046_sharpe": float(_sharpe(r_046_aligned)),
        "r_046_cagr": float(_cagr((1.0 + r_046_aligned).cumprod())),
        "r_046_mdd": float(_max_drawdown((1.0 + r_046_aligned).cumprod())),
        "r_qqqt_sharpe": float(_sharpe(r_qqqt_aligned)),
        "r_qqqt_cagr": float(_cagr((1.0 + r_qqqt_aligned).cumprod())),
        "r_qqqt_mdd": float(_max_drawdown((1.0 + r_qqqt_aligned).cumprod())),
        "qqqt_pct_long": pct_long,
        "rolling21_worst": rolling21_min,
        "markowitz_residual_sharpe": residual,
        "markowitz_detail": mw_detail,
    }
    return m, combined, r_qqqt_aligned


def cross_lib_check(qqq_prices_ext: pd.Series, window_start: str) -> dict:
    """G7 parity: pandas engine vs pure-numpy reference CAGR Δ ≤ 3 pp.

    Both pandas and numpy run on the EXTENDED price array (warmup absorbed),
    then we slice the comparison to the dataset window before computing CAGR.
    """
    pd_out_full = compute_qqq_trend_returns(
        qqq_prices_ext,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    np_out_full = compute_qqq_trend_returns_np(
        qqq_prices_ext.values,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    # Slice both to dataset window
    start_ts = pd.Timestamp(window_start)
    mask_pd = pd_out_full.index >= start_ts
    pd_arr = pd_out_full.values[mask_pd]
    # numpy: align by index — pd_out_full.index[1:] but pct_change drops 1
    # pd_out_full has index = qqq_prices_ext.index[1:]
    # np_out_full has length = len(qqq_prices_ext)-1, same alignment
    np_full_idx = qqq_prices_ext.index[1:]
    mask_np = np_full_idx >= start_ts
    np_arr = np_out_full[mask_np]
    n = min(len(pd_arr), len(np_arr))
    pd_arr = pd_arr[-n:]
    np_arr = np_arr[-n:]
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
        "iter_label": "064-2026-04-25-1315-iter058-qqq-trend-substitution",
    }

    for ds_name, ds in DATASETS.items():
        r_046 = load_iter046_returns(ds_name)
        # Load QQQ with warmup window (~250 trading days back from start)
        qqq_ext = load_qqq_prices_with_warmup(ds["start"], ds["end"], warmup_days=250)

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] iter046 stream {r_046.index[0].date()} → "
            f"{r_046.index[-1].date()} ({len(r_046)} bars), "
            f"QQQ ext {qqq_ext.index[0].date()} → {qqq_ext.index[-1].date()} "
            f"({len(qqq_ext)} bars), bench={ds['bench_ticker']} "
            f"Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, combined, r_qqqt = run_single_cfg(r_046, qqq_ext, ds["start"])

        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_046": {
                "index": [str(t.date()) for t in r_046.index],
                "net_returns": [round(float(x), 10) for x in r_046.tolist()],
            },
            "r_qqq_trend": {
                "index": [str(t.date()) for t in r_qqqt.index],
                "net_returns": [round(float(x), 10) for x in r_qqqt.tolist()],
            },
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        print(
            f"  combined Sharpe={m['sharpe']:+.4f} (Δ frozen={edge_frozen:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr(046,qqqt)={m['corr_046_qqqt']:+.3f} "
            f"corr(combined,046)={m['corr_combined_046']:+.3f}"
        )
        print(
            f"  r_046 Sharpe={m['r_046_sharpe']:+.4f} CAGR={m['r_046_cagr']:+.2%} "
            f"MDD={m['r_046_mdd']:.2%} | "
            f"r_qqqt Sharpe={m['r_qqqt_sharpe']:+.4f} CAGR={m['r_qqqt_cagr']:+.2%} "
            f"MDD={m['r_qqqt_mdd']:.2%} pct_long={m['qqqt_pct_long']:.1%}"
        )
        mw = m["markowitz_detail"]
        print(
            f"  Markowitz: formula S={mw['formula_sharpe']:+.4f} "
            f"observed S={mw['observed_sharpe']:+.4f} "
            f"residual={m['markowitz_residual_sharpe']:+.4f} "
            f"corr_emp={mw['corr_ab']:+.3f}"
        )

        cl = cross_lib_check(qqq_ext, ds["start"])
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 cross-lib (QQQ TREND only): CAGR pd={cl['cagr_pandas']:+.4%} "
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
