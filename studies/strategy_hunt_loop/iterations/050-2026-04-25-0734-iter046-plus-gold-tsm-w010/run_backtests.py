"""Iter 050 — Run iter 046 + gold TSM 90/10 combo on 3 datasets.

Single pre-committed cfg `iter046_plus_gold_tsm_w010_lookback90`.
The Markowitz-rounded optimum weight (iter 049 post-mortem: w*_gold ≈ 0.09).

cumulative_n_trials advance: 4316 → 4317 (+1).

Citations
---------
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base
  preserved verbatim via its saved return stream.
* `[systematic_trading]` (Carver) — TSM single-asset rule (gold TSM).
* Markowitz (1952), JoF 7(1) — closed-form Sharpe identity for
  convex-combo of 2 risky assets; w*_gold ≈ 0.09 derived in iter 049.
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

from gold_tsm import compute_gold_tsm_returns  # noqa: E402
from numpy_reference_iter050 import compute_gold_tsm_returns_np  # noqa: E402
from combined_046_plus_gold import combine_046_plus_gold  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_046_RESULTS = ITER_046_DIR / "results.json"

# ---------------------------------------------------------------------------
# Pre-committed single config (Markowitz-rounded optimum w_gold ≈ 0.09)
# ---------------------------------------------------------------------------
CFG: dict = {
    "cfg_id": "iter046_plus_gold_tsm_w010_lookback90",
    "w_046": 0.90,
    "w_gold": 0.10,
    "gold_ticker": "GLD",
    "lookback": 90,
    "rf": 0.02,
    "cost_bps": 5.0,
    "rebalance": "daily; gold TSM long iff trailing-90d return at t-1 > 0",
    "primary_citation": (
        "[advances_fin_ml, p.222-223] (DSR cumulative) + "
        "Markowitz (1952) JoF 7(1) (closed-form combo) + "
        "[risk_parity, ch.5] + [volatility_trading, p.218] (iter 046 base)"
    ),
}

# Match iter 049's exact dataset windows for apples-to-apples comparison.
DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "20y combined; iter 046 + gold TSM",
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


def load_iter046_returns(ds_name: str) -> pd.Series:
    """Load iter 046's combined return stream for the given dataset."""
    if not ITER_046_RESULTS.exists():
        raise FileNotFoundError(
            f"iter 046 results.json not found at {ITER_046_RESULTS} — "
            f"run iter 046 first"
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
    r_046: pd.Series,
    gld_prices: pd.Series,
) -> tuple[dict, pd.Series, pd.Series]:
    r_gold = compute_gold_tsm_returns(
        gld_prices,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    combined = combine_046_plus_gold(
        r_046, r_gold, w_046=CFG["w_046"], w_gold=CFG["w_gold"],
    )
    eq_curve = (1.0 + combined).cumprod()

    common = combined.index.intersection(r_046.index).intersection(r_gold.index)
    r_046_aligned = r_046.loc[common]
    r_gold_aligned = r_gold.loc[common]

    corr_046_gold = float(r_046_aligned.corr(r_gold_aligned))
    corr_combined_046 = float(combined.loc[common].corr(r_046_aligned))

    rolling21_min = float(combined.rolling(21).sum().min())

    markowitz = markowitz_predicted_combined_sharpe(
        r_046_aligned, r_gold_aligned, CFG["w_046"], CFG["w_gold"],
    )
    sharpe_observed = float(_sharpe(combined))

    m = {
        "cfg_id": CFG["cfg_id"],
        "w_046": CFG["w_046"], "w_gold": CFG["w_gold"],
        "lookback": CFG["lookback"],
        "rf": CFG["rf"], "cost_bps": CFG["cost_bps"],
        "bars": int(len(combined)),
        "sharpe": sharpe_observed,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "corr_046_gold": corr_046_gold,
        "corr_combined_046": corr_combined_046,
        "r_046_sharpe": float(_sharpe(r_046_aligned)),
        "r_046_cagr": float(_cagr((1.0 + r_046_aligned).cumprod())),
        "r_046_mdd": float(_max_drawdown((1.0 + r_046_aligned).cumprod())),
        "r_gold_sharpe": float(_sharpe(r_gold_aligned)),
        "r_gold_cagr": float(_cagr((1.0 + r_gold_aligned).cumprod())),
        "r_gold_mdd": float(_max_drawdown((1.0 + r_gold_aligned).cumprod())),
        "gold_pct_long": float(
            (r_gold_aligned != ((1.0 + CFG["rf"]) ** (1 / 252) - 1.0)).mean()
        ),
        "rolling21_worst": rolling21_min,
        "markowitz_predicted": markowitz,
        "markowitz_residual_sharpe": sharpe_observed - markowitz["sharpe_combined_predicted"],
    }
    return m, combined, r_gold_aligned


def cross_lib_check(gld_prices: pd.Series) -> dict:
    """G7 parity: pandas engine vs pure-numpy reference CAGR Δ ≤ 3 pp."""
    pd_out = compute_gold_tsm_returns(
        gld_prices,
        lookback=CFG["lookback"],
        rf=CFG["rf"],
        cost_bps=CFG["cost_bps"],
    )
    np_out = compute_gold_tsm_returns_np(
        gld_prices.values,
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
        "iter_label": "050-2026-04-25-0734-iter046-plus-gold-tsm-w010",
    }

    for ds_name, ds in DATASETS.items():
        r_046 = load_iter046_returns(ds_name)
        gld_p = load_prices(CFG["gold_ticker"], ds["start"], ds["end"])

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] iter046 stream {r_046.index[0].date()} → "
            f"{r_046.index[-1].date()} ({len(r_046)} bars), "
            f"GLD prices {gld_p.index[0].date()} → {gld_p.index[-1].date()} "
            f"({len(gld_p)} bars), bench={ds['bench_ticker']} "
            f"Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} (w_046={CFG['w_046']}, w_gold={CFG['w_gold']}) ===")
        m, combined, r_gold = run_single_cfg(r_046, gld_p)

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
            "r_gold_tsm": {
                "index": [str(t.date()) for t in r_gold.index],
                "net_returns": [round(float(x), 10) for x in r_gold.tolist()],
            },
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        markowitz = m["markowitz_predicted"]
        print(
            f"  combined Sharpe={m['sharpe']:+.4f} (Δ frozen={edge_frozen:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"corr(046,gold)={m['corr_046_gold']:+.3f}"
        )
        print(
            f"  Markowitz prediction: μ={markowitz['mu_combined_predicted']:.5f} "
            f"σ={markowitz['sigma_combined_predicted']:.5f} "
            f"S_predicted={markowitz['sharpe_combined_predicted']:+.4f} "
            f"residual={m['markowitz_residual_sharpe']:+.4f}"
        )
        print(
            f"  r_046 Sharpe={m['r_046_sharpe']:+.4f} CAGR={m['r_046_cagr']:+.2%} "
            f"MDD={m['r_046_mdd']:.2%} | "
            f"r_gold Sharpe={m['r_gold_sharpe']:+.4f} CAGR={m['r_gold_cagr']:+.2%} "
            f"MDD={m['r_gold_mdd']:.2%} pct_long={m['gold_pct_long']:.1%}"
        )

        cl = cross_lib_check(gld_p)
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 cross-lib (gold TSM only): CAGR pd={cl['cagr_pandas']:+.4%} "
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
