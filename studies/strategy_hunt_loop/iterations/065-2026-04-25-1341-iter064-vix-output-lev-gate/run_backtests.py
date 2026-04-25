"""Iter 065 — Apply VIX-conditional output leverage gate to iter 064 saved combined stream.

Single pre-committed cfg (lev_calm=1.5, lev_stress=1.0, vix_threshold=20,
borrow_annual=0.0225). cumulative_n_trials advance: 4334 → 4335 (+1).

Loads:
- iter 064 combined stream from `iterations/064-*/results.json`
  `returns_series` per dataset (preserves the QQQ_TREND substitution
  on iter 046 anchor verbatim).
- VIX from `data/external/macro/vix_daily.parquet` (Tiingo macro cache,
  1990-2026).

Citations
---------
* `[leverage_for_the_long_run, ch.5]` — Hsiao-Williams 2017 NTSX
  futures-financing rationale.
* Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098 — VIX threshold 20.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* iter 064 saved stream — Faber 2007 SSRN 962461 + [risk_parity, ch.5]
  + [volatility_trading, p.218] + Markowitz (1952) JoF 7(1).
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

from output_lev_gate import apply_vix_lev_gate  # noqa: E402
from numpy_reference_iter065 import apply_vix_lev_gate_np  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
ITER_064_RESULTS = ITER_064_DIR / "results.json"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"
TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

CFG: dict = {
    "cfg_id": "iter064_vix_lev_calm15_stress10_vix20_borrow0225",
    "lev_calm": 1.5,
    "lev_stress": 1.0,
    "vix_threshold": 20.0,
    "borrow_annual": 0.0225,
    "days_per_year": 252,
    "rebalance": "daily; lev[t]=1.5 if VIX[t-1]<20 else 1.0; drag=(lev-1)*borrow/252",
    "primary_citation": (
        "[leverage_for_the_long_run, ch.5] (Hsiao-Williams 2017 NTSX) + "
        "Whaley 2009 JPM 35(3) (VIX threshold 20) + "
        "[risk_parity, ch.5] + [volatility_trading, p.218] (iter 046 base) + "
        "Faber 2007 SSRN 962461 (QQQ_TREND in iter 064)"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
}


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


def load_vix() -> pd.Series:
    df = pd.read_parquet(VIX_PATH)
    df.index = pd.to_datetime(df.index)
    return df["VIX"].astype(float)


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


def run_single_cfg(r_064: pd.Series, vix: pd.Series) -> tuple[dict, pd.Series]:
    levered = apply_vix_lev_gate(
        r_064, vix,
        lev_calm=CFG["lev_calm"], lev_stress=CFG["lev_stress"],
        vix_threshold=CFG["vix_threshold"],
        borrow_annual=CFG["borrow_annual"],
        days_per_year=CFG["days_per_year"],
    )
    eq = (1.0 + levered).cumprod()

    # Recompute lev fraction stats for diagnostics
    vix_aligned = vix.reindex(r_064.index).ffill().bfill()
    vix_lag = vix_aligned.shift(1).bfill()
    pct_calm = float((vix_lag < CFG["vix_threshold"]).mean())
    avg_lev = (
        pct_calm * CFG["lev_calm"] + (1 - pct_calm) * CFG["lev_stress"]
    )

    obs_sharpe = float(_sharpe(levered))
    base_sharpe = float(_sharpe(r_064))
    base_cagr = float(_cagr((1 + r_064).cumprod()))
    base_mdd = float(_max_drawdown((1 + r_064).cumprod()))

    m = {
        "cfg_id": CFG["cfg_id"],
        "lev_calm": CFG["lev_calm"], "lev_stress": CFG["lev_stress"],
        "vix_threshold": CFG["vix_threshold"],
        "borrow_annual": CFG["borrow_annual"],
        "bars": int(len(levered)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "pct_calm": pct_calm,
        "avg_lev": float(avg_lev),
        "base_sharpe": base_sharpe,
        "base_cagr": base_cagr,
        "base_mdd": base_mdd,
        "sharpe_delta_064": obs_sharpe - base_sharpe,
        "cagr_delta_064": float(_cagr(eq) - base_cagr),
        "mdd_delta_064": float(_max_drawdown(eq) - base_mdd),
    }
    return m, levered


def cross_lib_check(r_064: pd.Series, vix: pd.Series) -> dict:
    """G7 parity: pandas vs numpy reference CAGR Δ ≤ 3 pp."""
    pd_out = apply_vix_lev_gate(
        r_064, vix,
        lev_calm=CFG["lev_calm"], lev_stress=CFG["lev_stress"],
        vix_threshold=CFG["vix_threshold"],
        borrow_annual=CFG["borrow_annual"],
        days_per_year=CFG["days_per_year"],
    )
    vix_aligned = vix.reindex(r_064.index).ffill().bfill().to_numpy()
    np_out = apply_vix_lev_gate_np(
        r_064.to_numpy(), vix_aligned,
        lev_calm=CFG["lev_calm"], lev_stress=CFG["lev_stress"],
        vix_threshold=CFG["vix_threshold"],
        borrow_annual=CFG["borrow_annual"],
        days_per_year=CFG["days_per_year"],
    )
    eq_pd = np.cumprod(1.0 + pd_out.values)
    eq_np = np.cumprod(1.0 + np_out)
    n = len(eq_pd)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_out.values - np_out))),
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
        "iter_label": "065-2026-04-25-1341-iter064-vix-output-lev-gate",
    }

    for ds_name, ds in DATASETS.items():
        r_064 = load_iter064_returns(ds_name)
        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"\n[{ds_name}] iter 064 stream {r_064.index[0].date()} → "
            f"{r_064.index[-1].date()} ({len(r_064)} bars), "
            f"bench={ds['bench_ticker']} S={bench['sharpe']:.3f} "
            f"CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%}"
        )

        m, levered = run_single_cfg(r_064, vix)

        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in levered.index],
                "net_returns": [round(float(x), 12) for x in levered.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_064": {
                "index": [str(t.date()) for t in r_064.index],
                "net_returns": [round(float(x), 12) for x in r_064.tolist()],
            }
        }
        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        print(
            f"  iter 065 Sharpe={m['sharpe']:+.4f} "
            f"(Δ frozen {edge_frozen:+.4f}, Δ064 {m['sharpe_delta_064']:+.4f}) "
            f"CAGR={m['cagr']:+.2%} (Δ064 {m['cagr_delta_064']:+.2%}) "
            f"MDD={m['mdd']:.2%} (Δ064 {m['mdd_delta_064']:+.2%})"
        )
        print(
            f"  pct_calm={m['pct_calm']:.1%}  avg_lev={m['avg_lev']:.3f}  "
            f"base iter 064 S={m['base_sharpe']:.4f} CAGR={m['base_cagr']:.2%}"
        )

        cl = cross_lib_check(r_064, vix)
        all_results["crosslib"][ds_name] = cl
        print(
            f"  G7 cross-lib: CAGR pd={cl['cagr_pandas']:+.4%} "
            f"np={cl['cagr_numpy']:+.4%} Δ={cl['abs_diff_pp']:.4f} pp "
            f"(max return diff {cl['max_abs_return_diff']:.2e})"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
