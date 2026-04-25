"""Iter 061 — Run equity-overweight 3-leg stack (0.75/0.40/0.40)
+ HYG TSM (w=0.10) on 3 datasets.

Single pre-committed cfg ``iter037_eq075_plus_hyg_tsm_w010_lookback90``.
No grid sweep. cumulative_n_trials advance: 4330 → 4331 (+1).

The 3-leg base stream is computed FRESH per dataset from SPY/IEF/GLD
(or QQQ/IEF/GLD for ndx_real) at weights 0.75/0.40/0.40 (vs iter 037's
0.60/0.45/0.45). HYG TSM is computed from HYG prices (Tiingo window)
via the engine vendored from iter 058/059. The combiner is structurally
identical to iter 058/059's combiner — only the variable names change.

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 multi-leg
  risk-parity decomposition (eq075 base architecture).
* `[leverage_for_the_long_run, p.19-20]` — Hsiao & Williams 2017,
  preserved-leverage zone.
* Asvanunt-Richardson 2017 JPM 43(2) DOI 10.3905/jpm.2017.43.2.090 —
  credit risk premium third stream rationale.
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

from synth_stacked_etf_3leg_eq075 import apply_static_stack_3leg  # noqa: E402
from hyg_tsm import compute_hyg_tsm_returns  # noqa: E402
from numpy_reference_iter061 import compute_hyg_tsm_returns_np  # noqa: E402
from combined_eq075_plus_hyg import combine_eq075_plus_hyg  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "iter037_eq075_plus_hyg_tsm_w010_lookback90",
    "eq_w": 0.75,                 # equity-overweight (vs iter 037's 0.60)
    "bd_short_w": 0.40,           # IEF (vs iter 037's 0.45)
    "bd_long_w": 0.40,            # GLD (vs iter 037's 0.45)
    "total_lev_base": 1.55,       # 0.75 + 0.40 + 0.40
    "w_eq075": 0.9,               # eq075 anchor weight in the convex combo
    "w_hyg": 0.1,                 # HYG_TSM 3rd stream weight
    "hyg_ticker": "HYG",
    "lookback": 90,               # boolean trend on trailing 90d HYG return
    "rf": 0.02,
    "cost_bps": 5.0,              # HYG_TSM cost
    "cost_bps_per_leg_eq075": 0.0002,  # 2bps per-leg ∆position (matches iter 037)
    "rebalance": (
        "daily eq075 stack at fixed 0.75/0.40/0.40 + HYG TSM long iff "
        "trailing-90d return at t-1 > 0"
    ),
    "primary_citation": (
        "[risk_parity, ch.5] (eq075 base) + "
        "[leverage_for_the_long_run, p.19-20] (preserved-lev zone) + "
        "Asvanunt-Richardson 2017 JPM 43(2) DOI 10.3905/jpm.2017.43.2.090 + "
        "[systematic_trading] (Carver TSM)"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "SPY",
        "start": "2004-11-19",
        "end": "2026-04-15",
        "role": "SPY+IEF+GLD 21y (GLD-aligned start; HYG inner-join → 2007-04+)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+IEF+GLD 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+IEF+GLD 16y tech-heavy",
    },
}


def load_triple_returns(
    eq: str, bd: str, gld: str, start: str, end: str,
) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    df_gld = pd.read_parquet(TIINGO_DIR / f"{gld}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    m_gld = (df_gld.index >= start) & (df_gld.index <= end)
    p = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd": df_bd.loc[m_bd, "adj_close"],
        "gld": df_gld.loc[m_gld, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd, gld]
    return r


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
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
    triple: pd.DataFrame, hyg_prices: pd.Series,
) -> tuple[dict, pd.Series, pd.Series, pd.Series]:
    eq_col, bd_col, gld_col = triple.columns
    r_eq075, positions, scale = apply_static_stack_3leg(
        triple[eq_col],
        triple[bd_col],
        triple[gld_col],
        eq_w=CFG["eq_w"],
        bd_short_w=CFG["bd_short_w"],
        bd_long_w=CFG["bd_long_w"],
        cost_bps_per_leg=CFG["cost_bps_per_leg_eq075"],
    )
    r_hyg = compute_hyg_tsm_returns(
        hyg_prices,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    combined = combine_eq075_plus_hyg(
        r_eq075, r_hyg, w_eq075=CFG["w_eq075"], w_hyg=CFG["w_hyg"],
    )
    eq_curve = (1.0 + combined).cumprod()

    common = combined.index.intersection(r_eq075.index).intersection(r_hyg.index)
    r_eq075_aligned = r_eq075.loc[common]
    r_hyg_aligned = r_hyg.loc[common]

    corr_eq075_hyg = float(r_eq075_aligned.corr(r_hyg_aligned))
    corr_combined_eq075 = float(combined.loc[common].corr(r_eq075_aligned))

    obs_sharpe = float(_sharpe(combined))
    residual, mw_detail = markowitz_residual(
        r_eq075_aligned, r_hyg_aligned,
        w_a=CFG["w_eq075"], w_b=CFG["w_hyg"],
        observed_sharpe=obs_sharpe,
    )

    rf_d = (1.0 + CFG["rf"]) ** (1.0 / 252.0) - 1.0
    pct_long = float((r_hyg_aligned != rf_d).mean())

    m = {
        "cfg_id": CFG["cfg_id"],
        "eq_w": CFG["eq_w"], "bd_short_w": CFG["bd_short_w"],
        "bd_long_w": CFG["bd_long_w"],
        "total_lev_base": CFG["total_lev_base"],
        "w_eq075": CFG["w_eq075"], "w_hyg": CFG["w_hyg"],
        "lookback": CFG["lookback"],
        "rf": CFG["rf"], "cost_bps": CFG["cost_bps"],
        "bars": int(len(combined)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_eq075_hyg": corr_eq075_hyg,
        "corr_combined_eq075": corr_combined_eq075,
        "r_eq075_sharpe": float(_sharpe(r_eq075_aligned)),
        "r_eq075_cagr": float(_cagr((1.0 + r_eq075_aligned).cumprod())),
        "r_eq075_mdd": float(_max_drawdown((1.0 + r_eq075_aligned).cumprod())),
        "r_hyg_sharpe": float(_sharpe(r_hyg_aligned)),
        "r_hyg_cagr": float(_cagr((1.0 + r_hyg_aligned).cumprod())),
        "r_hyg_mdd": float(_max_drawdown((1.0 + r_hyg_aligned).cumprod())),
        "hyg_pct_long": pct_long,
        "markowitz_residual_sharpe": residual,
        "markowitz_detail": mw_detail,
        "scale_mean": float(scale.mean()),
    }
    return m, combined, r_eq075_aligned, r_hyg_aligned


def cross_lib_check(hyg_prices: pd.Series) -> dict:
    """G7 parity: pandas engine vs pure-numpy reference for HYG TSM."""
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
        "leg_correlations": {},
        "pre_committed": True,
        "iter_label": "061-2026-04-25-1154-iter037-eq075-plus-hyg-tsm",
    }

    for ds_name, ds in DATASETS.items():
        triple = load_triple_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"],
            ds["start"], ds["end"],
        )
        hyg_p = load_prices(CFG["hyg_ticker"], ds["start"], ds["end"])

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench

        eq_col, bd_col, gld_col = triple.columns
        corr_mat = triple.corr()
        all_results["leg_correlations"][ds_name] = {
            "eq_bd": float(corr_mat.loc[eq_col, bd_col]),
            "eq_gld": float(corr_mat.loc[eq_col, gld_col]),
            "bd_gld": float(corr_mat.loc[bd_col, gld_col]),
        }
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']}+{ds['gold_symbol']} "
            f"{triple.index[0].date()}→{triple.index[-1].date()} ({len(triple)} bars), "
            f"HYG {hyg_p.index[0].date()}→{hyg_p.index[-1].date()} ({len(hyg_p)} bars), "
            f"bench={ds['bench_ticker']} S={bench['sharpe']:.3f} "
            f"CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, combined, r_eq075, r_hyg = run_single_cfg(triple, hyg_p)

        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_eq075": {
                "index": [str(t.date()) for t in r_eq075.index],
                "net_returns": [round(float(x), 10) for x in r_eq075.tolist()],
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
            f"corr(eq075,hyg)={m['corr_eq075_hyg']:+.3f}"
        )
        print(
            f"  r_eq075 (anchor)  S={m['r_eq075_sharpe']:+.4f} "
            f"CAGR={m['r_eq075_cagr']:+.2%} MDD={m['r_eq075_mdd']:.2%}"
        )
        print(
            f"  r_hyg_tsm         S={m['r_hyg_sharpe']:+.4f} "
            f"CAGR={m['r_hyg_cagr']:+.2%} MDD={m['r_hyg_mdd']:.2%} "
            f"pct_long={m['hyg_pct_long']:.1%}"
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
            f"    G7 cross-lib (HYG TSM): CAGR pd={cl['cagr_pandas']:+.4%} "
            f"np={cl['cagr_numpy']:+.4%} Δ={cl['abs_diff_pp']:.4f} pp"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
