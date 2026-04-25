"""Iter 063 — Run iter 058 with internal-LETF substitution on iter 041 leg.

Single pre-committed cfg ``iter058_with_internal_letf_iter041_only``.

Pipeline per dataset:

1. Load equity (SPY or QQQ) + IEF + GLD prices over [start, end].
2. Build LETF returns:
   - educational: real UPRO from 2009-06-25 + synth UPRO pre-2009.
   - spy_real: real UPRO from 2009-06-25 (entire window).
   - ndx_real: real TQQQ from 2010-02-12 (entire window).
3. Load VIX over the window with 10-day pad for prior-bar regime gate.
4. Compute ``iter_041_LETF`` via ``apply_regime_weights_3leg`` with
   iter 063 preserved-equity weights (calm 0.2333/0.6333/0.6333,
   stress 0.10/0.65/0.65).
5. Load ``iter_039`` saved stream from iter 046 results.json
   (subcomponent_returns[ds]["r_039"]).
6. Load ``HYG_TSM`` saved stream from iter 058 results.json
   (subcomponent_returns[ds]["r_hyg_tsm"]).
7. Compose ``r_046_LETF = 0.5 * iter_041_LETF + 0.5 * iter_039``.
8. Compose ``r_058_LETF = 0.9 * r_046_LETF + 0.1 * HYG_TSM``.
9. Compute metrics (Sharpe, CAGR, MDD, correlations, Markowitz residual,
   sub-window robustness, G7 cross-lib parity).

Cumulative n_trials advance: 4332 → 4333 (+1).

Citations
---------
* `[leverage_for_the_long_run, p.19-25]` — Hsiao-Williams daily-reset LETF.
* `[risk_parity, ch.5]` — multi-leg risk-parity with regime tilts.
* Asvanunt-Richardson 2017 JPM 43(2) — credit risk premium third stream.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
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

from iter041_letf import (  # noqa: E402
    ITER063_CALM_WEIGHTS,
    ITER063_STRESS_WEIGHTS,
    build_letf_returns,
    compute_iter041_letf_returns,
)
from combine_iter058_letf import (  # noqa: E402
    combine_iter046_letf,
    combine_iter058_letf,
)
from numpy_reference_iter063 import (  # noqa: E402
    apply_regime_weights_3leg_np,
    combine_three_streams_np,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_058_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "058-2026-04-25-1044-hyg-credit-carry-3rd-stream"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "iter058_with_internal_letf_iter041_only",
    "letf_leverage": 3.0,
    "expense_ratio": 0.0091,
    "calm_weights": dict(ITER063_CALM_WEIGHTS),
    "stress_weights": dict(ITER063_STRESS_WEIGHTS),
    "vix_threshold": 20.0,
    "cost_bps_per_leg": 0.0002,
    "w_041": 0.5,           # weight of LETF-substituted iter 041 within iter 046
    "w_039": 0.5,           # weight of (canonical) iter 039 within iter 046
    "w_046": 0.9,           # weight of LETF-substituted iter 046 within iter 058
    "w_hyg": 0.1,           # weight of HYG_TSM (canonical) within iter 058
    "rebalance": "daily; regime gate uses VIX[t-1]; total NAV calm 1.50 / stress 1.40",
    "primary_citation": (
        "[leverage_for_the_long_run, p.19-25] (Hsiao-Williams daily-reset LETF) + "
        "[risk_parity, ch.5] (multi-leg risk-parity) + "
        "Asvanunt-Richardson 2017 JPM 43(2) (credit carry HYG_TSM) + "
        "[advances_fin_ml, p.222-223] (DSR cumulative)"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "spy_symbol": "SPY",
        "letf_symbol": "UPRO",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "letf_inception": "2009-06-25",
        "synth_pre_inception": True,
        "letf_kind": "3x_spy",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter058_cfg_id": "iter046_plus_hyg_tsm_w010_lookback90",
        "role": (
            "21y joined UPRO (synth pre-2009 + real post) + IEF + GLD "
            "+ iter_039 + HYG_TSM; effective window starts at HYG inception"
        ),
    },
    "spy_real": {
        "spy_symbol": "SPY",
        "letf_symbol": "UPRO",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "letf_inception": "2009-06-25",
        "synth_pre_inception": False,
        "letf_kind": "3x_spy",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter058_cfg_id": "iter046_plus_hyg_tsm_w010_lookback90",
        "role": "17y real UPRO + IEF + GLD + iter_039 + HYG_TSM post-GFC",
    },
    "ndx_real": {
        "spy_symbol": "QQQ",
        "letf_symbol": "TQQQ",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "letf_inception": "2010-02-11",
        "synth_pre_inception": False,
        "letf_kind": "3x_qqq",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter058_cfg_id": "iter046_plus_hyg_tsm_w010_lookback90",
        "role": "16y real TQQQ + IEF + GLD + iter_039 + HYG_TSM tech-heavy",
    },
}

FROZEN_BENCH = {"educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_vix(start: str, end: str) -> pd.Series:
    df = pd.read_parquet(VIX_PATH)
    pad_start = (pd.Timestamp(start) - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    m = (df.index >= pad_start) & (df.index <= end)
    return df.loc[m, "VIX"]


def load_saved_stream(results_path: Path, ds_name: str, key: str) -> pd.Series:
    if not results_path.exists():
        raise FileNotFoundError(f"saved stream missing: {results_path}")
    with results_path.open() as f:
        results = json.load(f)
    series = results["subcomponent_returns"][ds_name][key]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name=key)


def load_saved_combined(results_path: Path, ds_name: str, cfg_id: str) -> pd.Series:
    with results_path.open() as f:
        results = json.load(f)
    series = results["returns_series"][ds_name][cfg_id]
    idx = pd.to_datetime(series["index"])
    vals = np.array(series["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name=f"combined_{cfg_id}")


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
    formula = (mu_p / sigma_p) * np.sqrt(252.0) if sigma_p > 1e-12 else 0.0
    return observed_sharpe - formula, {
        "formula_sharpe": float(formula),
        "observed_sharpe": float(observed_sharpe),
        "mu_a": mu_a, "mu_b": mu_b,
        "sigma_a": float(np.sqrt(var_a)),
        "sigma_b": float(np.sqrt(var_b)),
        "corr_ab": float(cov_ab / (np.sqrt(var_a * var_b) + 1e-18)),
        "n_bars_used": int(len(common)),
    }


def sub_window_metrics(returns: pd.Series, n_windows: int = 3) -> list[dict]:
    """Equal-bar splits — Sharpe per sub-window."""
    n = len(returns)
    if n < 60:
        return [{"sub_window": 0, "sharpe": float("nan"), "n_bars": n}]
    ws = n // n_windows
    out: list[dict] = []
    for i in range(n_windows):
        s = returns.iloc[i * ws : (i + 1) * ws if i < n_windows - 1 else n]
        out.append({
            "sub_window": i,
            "sharpe": float(_sharpe(s)),
            "n_bars": int(len(s)),
            "first": str(s.index[0].date()),
            "last": str(s.index[-1].date()),
        })
    return out


def build_iter041_letf_for_ds(ds: dict) -> tuple[pd.Series, pd.Series, dict]:
    """Build the LETF-substituted iter 041 stream for one dataset.

    Returns (r_041_letf, r_letf, meta) where r_letf is the standalone
    LETF stream (for diagnostic) and meta contains window stats.
    """
    spy_p = load_prices(ds["spy_symbol"], ds["start"], ds["end"])
    bd_p = load_prices(ds["bond_symbol"], ds["start"], ds["end"])
    gld_p = load_prices(ds["gold_symbol"], ds["start"], ds["end"])

    r_spy = spy_p.pct_change().dropna()
    r_bd = bd_p.pct_change().dropna()
    r_gld = gld_p.pct_change().dropna()

    if ds["synth_pre_inception"]:
        letf_p = load_prices(ds["letf_symbol"], ds["start"], ds["end"])
        r_real_letf = letf_p.pct_change().dropna()
        r_letf = build_letf_returns(
            r_spy, real_letf_returns=r_real_letf,
            leverage=CFG["letf_leverage"],
            expense_ratio=CFG["expense_ratio"],
        )
        n_synth = int((r_letf.index < r_real_letf.index[0]).sum())
        n_real = int((r_letf.index >= r_real_letf.index[0]).sum())
    else:
        letf_p = load_prices(ds["letf_symbol"], ds["start"], ds["end"])
        r_real_letf = letf_p.pct_change().dropna()
        r_letf = r_real_letf.copy()
        r_letf.name = "joined_LETF"
        n_synth = 0
        n_real = int(len(r_letf))

    # Inner-join LETF + IEF + GLD on common dates
    df = pd.concat({
        "letf": r_letf, "bd": r_bd, "gld": r_gld,
    }, axis=1, join="inner").dropna()

    # Load VIX padded around the window
    vix = load_vix(ds["start"], ds["end"])

    r_041_letf, _, _, regime = compute_iter041_letf_returns(
        df["letf"], df["bd"], df["gld"], vix,
        calm_weights=CFG["calm_weights"],
        stress_weights=CFG["stress_weights"],
        vix_threshold=CFG["vix_threshold"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
    )

    meta = {
        "letf_first": str(df.index[0].date()),
        "letf_last": str(df.index[-1].date()),
        "n_bars_letf_3leg": int(len(df)),
        "n_bars_synth_letf": n_synth,
        "n_bars_real_letf": n_real,
        "letf_inception_real": ds["letf_inception"],
        "letf_kind": ds["letf_kind"],
        "calm_frac": float((regime == 1).mean()),
        "stress_frac": float((regime == 0).mean()),
        "n_bars_iter041_letf": int(len(r_041_letf)),
    }
    return r_041_letf, df["letf"], meta


def cross_lib_check(
    df_letf_3leg: pd.DataFrame, vix: pd.Series, r_041_letf_pd: pd.Series,
    r_039_aligned: pd.Series, r_hyg_aligned: pd.Series,
    final_combined_pd: pd.Series,
) -> dict:
    """G7 parity: pandas full pipeline vs numpy reference. CAGR Δ ≤ 3 pp.

    Strategy: run the exact same composite pipeline through the numpy
    reference modules and compare CAGR on the FINAL combined stream.
    Ensure intermediate streams (iter_041_LETF) match exactly.
    """
    # 3-leg LETF stack (numpy)
    vix_aligned = vix.reindex(df_letf_3leg.index, method="ffill")
    if vix_aligned.isna().any():
        vix_aligned = vix_aligned.fillna(CFG["vix_threshold"])
    np_041_letf = apply_regime_weights_3leg_np(
        df_letf_3leg["letf"].values,
        df_letf_3leg["bd"].values,
        df_letf_3leg["gld"].values,
        vix_aligned.values,
        calm_weights=CFG["calm_weights"],
        stress_weights=CFG["stress_weights"],
        vix_threshold=CFG["vix_threshold"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
    )
    pd_041_letf_aligned = r_041_letf_pd.reindex(df_letf_3leg.index)
    pdv = pd_041_letf_aligned.values
    max_step1_diff = float(np.max(np.abs(pdv - np_041_letf)))

    # Inner-join everything for the final combine on the same axis
    common = (r_041_letf_pd.index
              .intersection(r_039_aligned.index)
              .intersection(r_hyg_aligned.index))
    a = r_041_letf_pd.loc[common].values
    b = r_039_aligned.loc[common].values
    c = r_hyg_aligned.loc[common].values

    np_combined = combine_three_streams_np(
        a, b, c,
        w_a=CFG["w_041"], w_b=CFG["w_039"],
        w_outer_ab=CFG["w_046"], w_outer_c=CFG["w_hyg"],
    )
    pd_combined = final_combined_pd.loc[common].values
    n = len(np_combined)
    eq_pd = np.cumprod(1.0 + pd_combined)
    eq_np = np.cumprod(1.0 + np_combined)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_combined_return_diff": float(np.max(np.abs(pd_combined - np_combined))),
        "max_abs_iter041_letf_return_diff": max_step1_diff,
        "n_bars_compared": int(n),
    }


def main() -> None:
    iter046_results = ITER_046_DIR / "results.json"
    iter058_results = ITER_058_DIR / "results.json"

    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "subcomponent_returns": {},
        "letf_meta": {},
        "leg_correlations": {},
        "crosslib": {},
        "iter058_canonical_metrics": {},
        "pre_committed": True,
        "iter_label": "063-2026-04-25-1246-iter058-internal-letf",
    }

    for ds_name, ds in DATASETS.items():
        print(f"\n=== {ds_name} ===")
        # Build LETF-substituted iter 041
        r_041_letf, r_letf, letf_meta = build_iter041_letf_for_ds(ds)
        all_results["letf_meta"][ds_name] = letf_meta

        # Load saved iter 039 stream (canonical, unchanged)
        r_039 = load_saved_stream(iter046_results, ds_name, "r_039")

        # Load saved HYG_TSM stream (canonical, unchanged)
        r_hyg = load_saved_stream(iter058_results, ds_name, "r_hyg_tsm")

        # Compose iter 046_LETF
        r_046_letf = combine_iter046_letf(
            r_041_letf, r_039, w_041=CFG["w_041"], w_039=CFG["w_039"],
        )

        # Compose iter 058_LETF
        r_058_letf = combine_iter058_letf(
            r_046_letf, r_hyg, w_046=CFG["w_046"], w_hyg=CFG["w_hyg"],
        )

        # Align all subcomponents to combined index for diagnostics
        common = r_058_letf.index
        r_041_letf_aligned = r_041_letf.loc[r_041_letf.index.intersection(common)]
        r_039_aligned = r_039.loc[r_039.index.intersection(common)]
        r_hyg_aligned = r_hyg.loc[r_hyg.index.intersection(common)]
        r_046_letf_aligned = r_046_letf.loc[r_046_letf.index.intersection(common)]
        r_letf_aligned = r_letf.loc[r_letf.index.intersection(common)]

        # Benchmarks: window-aligned + frozen reference
        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench_aligned = bench_series.loc[bench_series.index.isin(common)]
        bench = benchmark_metrics(bench_aligned)
        all_results["benchmarks"][ds_name] = bench

        # iter 058 canonical metrics (apples-to-apples comparison)
        iter058_combined = load_saved_combined(
            iter058_results, ds_name, ds["iter058_cfg_id"],
        )
        iter058_aligned = iter058_combined.loc[iter058_combined.index.isin(common)]
        eq_058 = (1.0 + iter058_aligned).cumprod()
        iter058_m = {
            "sharpe": float(_sharpe(iter058_aligned)),
            "cagr": float(_cagr(eq_058)),
            "mdd": float(_max_drawdown(eq_058)),
            "n_bars": int(len(iter058_aligned)),
        }
        all_results["iter058_canonical_metrics"][ds_name] = iter058_m

        # Combined metrics
        eq_curve = (1.0 + r_058_letf).cumprod()
        obs_sharpe = float(_sharpe(r_058_letf))
        # Markowitz residual treats the FINAL combine (0.9 r_046_letf + 0.1 r_hyg)
        residual_outer, mw_outer = markowitz_residual(
            r_046_letf_aligned, r_hyg_aligned,
            w_a=CFG["w_046"], w_b=CFG["w_hyg"],
            observed_sharpe=obs_sharpe,
        )
        # Inner Markowitz residual (0.5 iter_041_letf + 0.5 iter_039)
        obs_inner = float(_sharpe(r_046_letf))
        residual_inner, mw_inner = markowitz_residual(
            r_041_letf_aligned, r_039_aligned,
            w_a=CFG["w_041"], w_b=CFG["w_039"],
            observed_sharpe=obs_inner,
        )

        # Per-stream standalone metrics
        leg_metrics: dict[str, dict] = {}
        for name, r in [("r_041_letf", r_041_letf_aligned),
                        ("r_039", r_039_aligned),
                        ("r_046_letf", r_046_letf_aligned),
                        ("r_hyg_tsm", r_hyg_aligned),
                        ("r_letf_standalone", r_letf_aligned)]:
            eq = (1.0 + r).cumprod() if len(r) > 0 else pd.Series([1.0])
            leg_metrics[name] = {
                "sharpe": float(_sharpe(r)) if len(r) > 0 else float("nan"),
                "cagr": float(_cagr(eq)) if len(r) > 0 else float("nan"),
                "mdd": float(_max_drawdown(eq)) if len(r) > 0 else float("nan"),
                "n_bars": int(len(r)),
            }

        # Correlations
        corr_058_063 = float(r_058_letf.corr(iter058_aligned))
        corr_046_hyg_letf = float(r_046_letf_aligned.corr(r_hyg_aligned))
        corr_041letf_039 = float(r_041_letf_aligned.corr(r_039_aligned))

        # Sub-window metrics
        subw = sub_window_metrics(r_058_letf, n_windows=3)

        m = {
            "cfg_id": CFG["cfg_id"],
            "bars": int(len(r_058_letf)),
            "sharpe": obs_sharpe,
            "cagr": float(_cagr(eq_curve)),
            "mdd": float(_max_drawdown(eq_curve)),
            "final_equity": float(eq_curve.iloc[-1]),
            "frozen_bench_sharpe": FROZEN_BENCH[ds_name],
            "edge_frozen": obs_sharpe - FROZEN_BENCH[ds_name],
            "edge_window": obs_sharpe - bench["sharpe"],
            "iter058_canonical_sharpe": iter058_m["sharpe"],
            "iter058_canonical_cagr": iter058_m["cagr"],
            "iter058_canonical_mdd": iter058_m["mdd"],
            "delta_iter058_sharpe": obs_sharpe - iter058_m["sharpe"],
            "delta_iter058_cagr": float(_cagr(eq_curve)) - iter058_m["cagr"],
            "delta_iter058_mdd": float(_max_drawdown(eq_curve)) - iter058_m["mdd"],
            "corr_combined_iter058": corr_058_063,
            "corr_046_letf_hyg": corr_046_hyg_letf,
            "corr_iter041_letf_iter039": corr_041letf_039,
            "leg_metrics": leg_metrics,
            "markowitz_outer_residual": residual_outer,
            "markowitz_outer_detail": mw_outer,
            "markowitz_inner_residual": residual_inner,
            "markowitz_inner_detail": mw_inner,
            "sub_window_metrics": subw,
        }

        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["leg_correlations"][ds_name] = {
            "corr_combined_iter058": corr_058_063,
            "corr_046_letf_hyg": corr_046_hyg_letf,
            "corr_iter041_letf_iter039": corr_041letf_039,
        }
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in r_058_letf.index],
                "net_returns": [round(float(x), 10) for x in r_058_letf.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_041_letf": {
                "index": [str(t.date()) for t in r_041_letf_aligned.index],
                "net_returns": [round(float(x), 10) for x in r_041_letf_aligned.tolist()],
            },
            "r_039": {
                "index": [str(t.date()) for t in r_039_aligned.index],
                "net_returns": [round(float(x), 10) for x in r_039_aligned.tolist()],
            },
            "r_046_letf": {
                "index": [str(t.date()) for t in r_046_letf_aligned.index],
                "net_returns": [round(float(x), 10) for x in r_046_letf_aligned.tolist()],
            },
            "r_hyg_tsm": {
                "index": [str(t.date()) for t in r_hyg_aligned.index],
                "net_returns": [round(float(x), 10) for x in r_hyg_aligned.tolist()],
            },
        }

        print(
            f"  letf 3leg window {letf_meta['letf_first']}→{letf_meta['letf_last']} "
            f"({letf_meta['n_bars_letf_3leg']} bars; synth/real={letf_meta['n_bars_synth_letf']}/"
            f"{letf_meta['n_bars_real_letf']}); "
            f"calm/stress fracs={letf_meta['calm_frac']:.2%}/{letf_meta['stress_frac']:.2%}"
        )
        print(
            f"  bench S={bench['sharpe']:+.3f} CAGR={bench['cagr']:+.2%} "
            f"MDD={bench['mdd']:.2%} bars={bench['n_bars']}"
        )
        print(
            f"  iter058 canonical S={iter058_m['sharpe']:+.4f} "
            f"CAGR={iter058_m['cagr']:+.2%} MDD={iter058_m['mdd']:.2%} "
            f"bars={iter058_m['n_bars']}"
        )
        print(
            f"  iter063 (letf) S={obs_sharpe:+.4f} (Δ frozen={obs_sharpe - FROZEN_BENCH[ds_name]:+.4f}, "
            f"Δ iter058={obs_sharpe - iter058_m['sharpe']:+.4f}) "
            f"CAGR={float(_cagr(eq_curve)):+.2%} (Δ iter058={float(_cagr(eq_curve)) - iter058_m['cagr']:+.2%}) "
            f"MDD={float(_max_drawdown(eq_curve)):.2%} (Δ={float(_max_drawdown(eq_curve)) - iter058_m['mdd']:+.2%})"
        )
        for nm, lm in leg_metrics.items():
            print(
                f"    leg {nm} S={lm['sharpe']:+.4f} CAGR={lm['cagr']:+.2%} "
                f"MDD={lm['mdd']:.2%} bars={lm['n_bars']}"
            )
        print(
            f"    Markowitz outer residual={residual_outer:+.4f} (formula S={mw_outer['formula_sharpe']:+.4f}); "
            f"inner residual={residual_inner:+.4f} (formula S={mw_inner['formula_sharpe']:+.4f})"
        )
        print(
            f"    corr(combined,iter058)={corr_058_063:+.3f} "
            f"corr(046letf,hyg)={corr_046_hyg_letf:+.3f} "
            f"corr(041letf,039)={corr_041letf_039:+.3f}"
        )

        # G7 cross-lib parity (final composite)
        df_3leg = pd.concat({
            "letf": r_letf_aligned, "bd": load_prices(ds["bond_symbol"], ds["start"], ds["end"]).pct_change().dropna(),
            "gld": load_prices(ds["gold_symbol"], ds["start"], ds["end"]).pct_change().dropna(),
        }, axis=1, join="inner").dropna()
        vix_full = load_vix(ds["start"], ds["end"])
        cl = cross_lib_check(
            df_3leg, vix_full, r_041_letf, r_039_aligned, r_hyg_aligned,
            r_058_letf,
        )
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 (composite): CAGR pd={cl['cagr_pandas']:+.4%} np={cl['cagr_numpy']:+.4%} "
            f"Δ={cl['abs_diff_pp']:.6f} pp; max iter_041_letf return diff={cl['max_abs_iter041_letf_return_diff']:.2e}"
        )

        for sw in subw:
            print(
                f"    sub-window {sw['sub_window']}: S={sw['sharpe']:+.4f} "
                f"({sw['first']} → {sw['last']}, {sw['n_bars']} bars)"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
