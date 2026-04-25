"""Iter 051 — Run iter 037 + iter 026 80/20 combo on 3 datasets.

Single pre-committed cfg ``iter037_plus_iter026_w080``. The Markowitz
score-Pareto-optimum weight (3/3 Sharpe edge AND 3/3 CAGR floor pass).

cumulative_n_trials advance: 4317 → 4318 (+1).

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen risk-parity stack
  (iter 037 base preserved verbatim via saved return stream).
* `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP
  harvest (iter 026 base preserved verbatim via saved return stream).
* Markowitz (1952), JoF 7(1) — closed-form Sharpe identity for convex-
  combo of 2 risky assets (used to derive w_037 = 0.80).
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
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

from combined_037_026 import combine_037_plus_026  # noqa: E402
from numpy_reference_iter051 import combine_037_plus_026_np  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
ITER_037_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "037-2026-04-25-0224-ntsx-3leg-preserved-lev"
ITER_026_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "026-2026-04-24-2122-vrp-primary-portfolio"
ITER_037_RESULTS = ITER_037_DIR / "results.json"
ITER_026_RESULTS = ITER_026_DIR / "results.json"

# ---------------------------------------------------------------------------
# Pre-committed single config (Markowitz score-Pareto-optimum)
# ---------------------------------------------------------------------------
CFG: dict = {
    "cfg_id": "iter037_plus_iter026_w080",
    "w_037": 0.80,
    "w_026": 0.20,
    "iter_037_cfg_id": "ntsx_3leg_preserved_60_45_45_spy_ief_gld",
    "iter_026_cfg_id": "vrp_primary_h1_5_10_1m",
    "rebalance": "daily; fixed-weight 80/20 convex combo of saved iter 037 + iter 026 streams",
    "primary_citation": (
        "[risk_parity, ch.5] (iter 037 base) + "
        "[volatility_trading, p.218] (iter 026 base) + "
        "Markowitz (1952) JoF 7(1) (score-Pareto weight derivation) + "
        "[advances_fin_ml, p.222-223] (DSR cumulative)"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; iter 037 stack + iter 026 SPY VRP",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "17y post-GFC; primary validation window",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "16y; bench QQQ; iter 037+iter 026 streams (both SPY-driven)",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_iter_returns(results_path: Path, ds_name: str, cfg_id: str) -> pd.Series:
    """Load a saved combined return stream from a prior iteration's
    ``results.json``."""
    if not results_path.exists():
        raise FileNotFoundError(
            f"results.json not found at {results_path} — "
            f"run the source iteration first"
        )
    with results_path.open() as f:
        results = json.load(f)
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx)


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


def markowitz_predicted_combined_sharpe(
    a: pd.Series, b: pd.Series, w_a: float, w_b: float,
) -> dict:
    """Closed-form Markowitz Sharpe identity given empirical (mu, sigma, rho)."""
    common = a.index.intersection(b.index)
    a = a.loc[common]
    b = b.loc[common]
    mu_a, sigma_a = float(a.mean()), float(a.std(ddof=0))
    mu_b, sigma_b = float(b.mean()), float(b.std(ddof=0))
    rho = float(a.corr(b))
    sigma2 = (
        w_a ** 2 * sigma_a ** 2
        + w_b ** 2 * sigma_b ** 2
        + 2 * w_a * w_b * rho * sigma_a * sigma_b
    )
    sigma_c = float(np.sqrt(sigma2))
    mu_c = w_a * mu_a + w_b * mu_b
    sharpe_predicted = (mu_c / sigma_c) * np.sqrt(252) if sigma_c > 0 else 0.0
    return {
        "mu_a": mu_a, "sigma_a": sigma_a,
        "mu_b": mu_b, "sigma_b": sigma_b,
        "rho": rho,
        "mu_combined_predicted": mu_c,
        "sigma_combined_predicted": sigma_c,
        "sharpe_combined_predicted": float(sharpe_predicted),
    }


def run_single_cfg(
    r_037: pd.Series, r_026: pd.Series,
) -> tuple[dict, pd.Series]:
    combined = combine_037_plus_026(
        r_037, r_026, w_037=CFG["w_037"], w_026=CFG["w_026"],
    )
    eq_curve = (1.0 + combined).cumprod()

    common = combined.index.intersection(r_037.index).intersection(r_026.index)
    r_037_a = r_037.loc[common]
    r_026_a = r_026.loc[common]

    corr_037_026 = float(r_037_a.corr(r_026_a))
    corr_combined_037 = float(combined.loc[common].corr(r_037_a))
    rolling21_min = float(combined.rolling(21).sum().min())

    markowitz = markowitz_predicted_combined_sharpe(
        r_037_a, r_026_a, CFG["w_037"], CFG["w_026"],
    )
    sharpe_observed = float(_sharpe(combined))

    m = {
        "cfg_id": CFG["cfg_id"],
        "w_037": CFG["w_037"], "w_026": CFG["w_026"],
        "bars": int(len(combined)),
        "sharpe": sharpe_observed,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_037_026": corr_037_026,
        "corr_combined_037": corr_combined_037,
        "r_037_sharpe": float(_sharpe(r_037_a)),
        "r_037_cagr": float(_cagr((1.0 + r_037_a).cumprod())),
        "r_037_mdd": float(_max_drawdown((1.0 + r_037_a).cumprod())),
        "r_026_sharpe": float(_sharpe(r_026_a)),
        "r_026_cagr": float(_cagr((1.0 + r_026_a).cumprod())),
        "r_026_mdd": float(_max_drawdown((1.0 + r_026_a).cumprod())),
        "rolling21_worst": rolling21_min,
        "markowitz_predicted": markowitz,
        "markowitz_residual_sharpe": sharpe_observed - markowitz["sharpe_combined_predicted"],
    }
    return m, combined


def cross_lib_check(r_037: pd.Series, r_026: pd.Series) -> dict:
    """G7 parity: pandas combine vs numpy combine."""
    combined_pd = combine_037_plus_026(
        r_037, r_026, w_037=CFG["w_037"], w_026=CFG["w_026"],
    )
    common = r_037.index.intersection(r_026.index)
    np_out = combine_037_plus_026_np(
        r_037.loc[common].to_numpy(float),
        r_026.loc[common].to_numpy(float),
        w_037=CFG["w_037"], w_026=CFG["w_026"],
    )
    n = min(len(combined_pd), len(np_out))
    pd_arr = combined_pd.values[-n:]
    np_arr = np_out[-n:]
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
        "iter_label": "051-2026-04-25-0753-iter037-plus-iter026-w080",
    }

    for ds_name, ds in DATASETS.items():
        r_037 = load_iter_returns(ITER_037_RESULTS, ds_name, CFG["iter_037_cfg_id"])
        r_026 = load_iter_returns(ITER_026_RESULTS, ds_name, CFG["iter_026_cfg_id"])

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] iter037 stream {r_037.index[0].date()} → "
            f"{r_037.index[-1].date()} ({len(r_037)} bars), "
            f"iter026 stream {r_026.index[0].date()} → {r_026.index[-1].date()} "
            f"({len(r_026)} bars), bench={ds['bench_ticker']} "
            f"Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

        print(
            f"\n=== {ds_name} — cfg {CFG['cfg_id']} "
            f"(w_037={CFG['w_037']}, w_026={CFG['w_026']}) ==="
        )
        m, combined = run_single_cfg(r_037, r_026)

        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
        }
        common = r_037.index.intersection(r_026.index)
        all_results["subcomponent_returns"][ds_name] = {
            "r_037": {
                "index": [str(t.date()) for t in r_037.loc[common].index],
                "net_returns": [round(float(x), 10) for x in r_037.loc[common].tolist()],
            },
            "r_026": {
                "index": [str(t.date()) for t in r_026.loc[common].index],
                "net_returns": [round(float(x), 10) for x in r_026.loc[common].tolist()],
            },
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        markowitz = m["markowitz_predicted"]
        print(
            f"  combined Sharpe={m['sharpe']:+.4f} (Δ frozen={edge_frozen:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr(037,026)={m['corr_037_026']:+.3f}"
        )
        print(
            f"  Markowitz prediction: μ={markowitz['mu_combined_predicted']:.5f} "
            f"σ={markowitz['sigma_combined_predicted']:.5f} "
            f"S_predicted={markowitz['sharpe_combined_predicted']:+.4f} "
            f"residual={m['markowitz_residual_sharpe']:+.4f}"
        )
        print(
            f"  r_037 Sharpe={m['r_037_sharpe']:+.4f} CAGR={m['r_037_cagr']:+.2%} "
            f"MDD={m['r_037_mdd']:.2%} | "
            f"r_026 Sharpe={m['r_026_sharpe']:+.4f} CAGR={m['r_026_cagr']:+.2%} "
            f"MDD={m['r_026_mdd']:.2%}"
        )

        cl = cross_lib_check(r_037, r_026)
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
