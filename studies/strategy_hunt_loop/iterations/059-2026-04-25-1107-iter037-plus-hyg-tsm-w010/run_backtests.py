"""Iter 059 — Run iter 037 + HYG TSM (w_037=0.9, w_hyg=0.1) on 3 datasets.

Single pre-committed cfg `iter037_plus_hyg_tsm_w010_lookback90`. No grid.
cumulative_n_trials advance: 4328 → 4329 (+1).

The HYG dataset begins 2007-04-12 in Tiingo. The educational dataset's
window (originally 2006-01-04 → 2026-04-15 in iter 037) is implicitly
shortened by the inner-join to HYG's first available date when the
combiner aligns indexes.

Citations
---------
* `[risk_parity, ch.5]` — iter 037 anchor (3-leg static stack) preserved
  verbatim via its saved return stream.
* Asvanunt-Richardson 2017 JPM 43(2) DOI 10.3905/jpm.2017.43.2.090 —
  credit risk premium thesis.
* `[systematic_trading]` (Carver) — TSM single-asset rule.
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

from hyg_tsm import compute_hyg_tsm_returns  # noqa: E402
from numpy_reference_iter059 import compute_hyg_tsm_returns_np  # noqa: E402
from combined_037_plus_hyg import combine_037_plus_hyg  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
ITER_037_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "037-2026-04-25-0224-ntsx-3leg-preserved-lev"
ITER_037_RESULTS = ITER_037_DIR / "results.json"

CFG: dict = {
    "cfg_id": "iter037_plus_hyg_tsm_w010_lookback90",
    "w_037": 0.9,
    "w_hyg": 0.1,
    "hyg_ticker": "HYG",
    "lookback": 90,
    "rf": 0.02,
    "cost_bps": 5.0,
    "rebalance": "daily; HYG TSM long iff trailing-90d return at t-1 > 0",
    "primary_citation": (
        "Asvanunt-Richardson 2017 JPM 43(2) DOI 10.3905/jpm.2017.43.2.090 + "
        "[risk_parity, ch.5] (iter 037 anchor preserved)"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-04",
        "end": "2026-04-15",
        "role": "20y combined; HYG limits effective start to ~2007-04",
        "iter037_cfg_id": "ntsx_3leg_preserved_60_45_45_spy_ief_gld",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-26",
        "end": "2026-04-15",
        "role": "17y post-GFC combined",
        "iter037_cfg_id": "ntsx_3leg_preserved_60_45_45_spy_ief_gld",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-16",
        "end": "2026-04-15",
        "role": "16y; bench QQQ",
        "iter037_cfg_id": "ntsx_3leg_preserved_60_45_45_spy_ief_gld",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_iter037_returns(ds_name: str) -> pd.Series:
    if not ITER_037_RESULTS.exists():
        raise FileNotFoundError(
            f"iter 037 results.json not found at {ITER_037_RESULTS}"
        )
    with ITER_037_RESULTS.open() as f:
        results = json.load(f)
    cfg_id = DATASETS[ds_name]["iter037_cfg_id"]
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name="r_037")


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
    r_037: pd.Series,
    hyg_prices: pd.Series,
) -> tuple[dict, pd.Series, pd.Series]:
    r_hyg = compute_hyg_tsm_returns(
        hyg_prices,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    combined = combine_037_plus_hyg(
        r_037, r_hyg, w_037=CFG["w_037"], w_hyg=CFG["w_hyg"],
    )
    eq_curve = (1.0 + combined).cumprod()

    common = combined.index.intersection(r_037.index).intersection(r_hyg.index)
    r_037_aligned = r_037.loc[common]
    r_hyg_aligned = r_hyg.loc[common]

    corr_037_hyg = float(r_037_aligned.corr(r_hyg_aligned))
    corr_combined_037 = float(combined.loc[common].corr(r_037_aligned))

    rolling21_min = float(combined.rolling(21).sum().min())

    obs_sharpe = float(_sharpe(combined))
    residual, mw_detail = markowitz_residual(
        r_037_aligned, r_hyg_aligned,
        w_a=CFG["w_037"], w_b=CFG["w_hyg"],
        observed_sharpe=obs_sharpe,
    )

    rf_d = (1.0 + CFG["rf"]) ** (1 / 252.0) - 1.0
    pct_long = float((r_hyg_aligned != rf_d).mean())

    m = {
        "cfg_id": CFG["cfg_id"],
        "w_037": CFG["w_037"], "w_hyg": CFG["w_hyg"],
        "lookback": CFG["lookback"],
        "rf": CFG["rf"], "cost_bps": CFG["cost_bps"],
        "bars": int(len(combined)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_037_hyg": corr_037_hyg,
        "corr_combined_037": corr_combined_037,
        "r_037_sharpe": float(_sharpe(r_037_aligned)),
        "r_037_cagr": float(_cagr((1.0 + r_037_aligned).cumprod())),
        "r_037_mdd": float(_max_drawdown((1.0 + r_037_aligned).cumprod())),
        "r_hyg_sharpe": float(_sharpe(r_hyg_aligned)),
        "r_hyg_cagr": float(_cagr((1.0 + r_hyg_aligned).cumprod())),
        "r_hyg_mdd": float(_max_drawdown((1.0 + r_hyg_aligned).cumprod())),
        "hyg_pct_long": pct_long,
        "rolling21_worst": rolling21_min,
        "markowitz_residual_sharpe": residual,
        "markowitz_detail": mw_detail,
    }
    return m, combined, r_hyg_aligned


def cross_lib_check(hyg_prices: pd.Series) -> dict:
    """G7 parity: pandas engine vs pure-numpy reference CAGR Δ ≤ 3 pp."""
    pd_out = compute_hyg_tsm_returns(
        hyg_prices,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    np_out = compute_hyg_tsm_returns_np(
        hyg_prices.values,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    n = min(len(pd_out), len(np_out))
    pd_arr = pd_out.values[-n:]
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
        "iter_label": "059-2026-04-25-1107-iter037-plus-hyg-tsm-w010",
    }

    for ds_name, ds in DATASETS.items():
        r_037 = load_iter037_returns(ds_name)
        hyg_p = load_prices(CFG["hyg_ticker"], ds["start"], ds["end"])

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] iter037 stream {r_037.index[0].date()} → "
            f"{r_037.index[-1].date()} ({len(r_037)} bars), "
            f"HYG prices {hyg_p.index[0].date()} → {hyg_p.index[-1].date()} "
            f"({len(hyg_p)} bars), bench={ds['bench_ticker']} "
            f"Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, combined, r_hyg = run_single_cfg(r_037, hyg_p)

        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_037": {
                "index": [str(t.date()) for t in r_037.index],
                "net_returns": [round(float(x), 10) for x in r_037.tolist()],
            },
            "r_hyg_tsm": {
                "index": [str(t.date()) for t in r_hyg.index],
                "net_returns": [round(float(x), 10) for x in r_hyg.tolist()],
            },
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        print(
            f"  combined Sharpe={m['sharpe']:+.4f} (Δ frozen={edge_frozen:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr(037,hyg)={m['corr_037_hyg']:+.3f} "
            f"corr(combined,037)={m['corr_combined_037']:+.3f}"
        )
        print(
            f"  r_037 Sharpe={m['r_037_sharpe']:+.4f} CAGR={m['r_037_cagr']:+.2%} "
            f"MDD={m['r_037_mdd']:.2%} | "
            f"r_hyg Sharpe={m['r_hyg_sharpe']:+.4f} CAGR={m['r_hyg_cagr']:+.2%} "
            f"MDD={m['r_hyg_mdd']:.2%} pct_long={m['hyg_pct_long']:.1%}"
        )
        mw = m["markowitz_detail"]
        print(
            f"  Markowitz: formula S={mw['formula_sharpe']:+.4f} "
            f"observed S={mw['observed_sharpe']:+.4f} "
            f"residual={m['markowitz_residual_sharpe']:+.4f} "
            f"corr_emp={mw['corr_ab']:+.3f}"
        )

        cl = cross_lib_check(hyg_p)
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 cross-lib (HYG TSM only): CAGR pd={cl['cagr_pandas']:+.4%} "
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
