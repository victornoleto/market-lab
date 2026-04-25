"""Iter 066 — Tree-based meta-label gating on iter 064 saved combined stream.

Single pre-committed cfg `iter064_meta_rf_n200_d4_purged5_emb21`.
No grid, no in-sample tuning. cumulative_n_trials advance: 4335 → 4336.

Pipeline per dataset:

1. Load iter 064 combined returns from `iterations/064-*/results.json`.
2. Load benchmark prices (SPY for educational + spy_real, QQQ for
   ndx_real) for SMA200 distance feature.
3. Load VIX (CBOE) + T10Y3M (FRED) macro series.
4. Build 5-feature matrix shifted +1 (no peek).
5. Drop warmup rows where ANY feature is NaN.
6. Label: ``r_064[t] > 0`` (binary).
7. Purged k-fold (5 folds, embargo=21) → OOF probabilities.
8. Threshold 0.5 → binary trade/cash signal.
9. Apply ``gate_iter064_with_meta`` (cost 5 bps per flip) → r_066.
10. Compute Sharpe / CAGR / MDD + corr(iter066, iter064) + pct_traded
    + avg AUC across folds + Markowitz residual (vacuous, expect 0).
11. G6 bootstrap, G7 cross-lib parity (post-prediction transform).

Citations
---------
* `[advances_fin_ml, ch.3]` — meta-labeling.
* `[advances_fin_ml, ch.7]` — purged k-fold + embargo.
* `[advances_fin_ml, p.31-34]` — G7 cross-lib parity.
* Breiman (2001) DOI 10.1023/A:1010933404324 — Random Forest.
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

from feature_engineering import (  # noqa: E402
    FEATURE_COLS,
    build_feature_matrix,
    label_positive_return,
    warmup_drop,
)
from meta_label_rf import RF_PARAMS, fit_predict_purged_kfold  # noqa: E402
from combined_iter064_meta import (  # noqa: E402
    gate_iter064_with_meta,
    gate_iter064_with_meta_np,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
MACRO_DIR = ROOT / "data" / "external" / "macro"
ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
ITER_064_RESULTS = ITER_064_DIR / "results.json"

CFG: dict = {
    "cfg_id": "iter064_meta_rf_n200_d4_purged5_emb21",
    "rf_params": RF_PARAMS,
    "n_folds": 5,
    "embargo": 21,
    "threshold": 0.5,
    "cost_bps": 5.0,
    "feature_cols": list(FEATURE_COLS),
    "feature_windows": {
        "roll21_sharpe": 21,
        "roll63_mdd": 63,
        "vix": 0,
        "t10y3m": 0,
        "sma200_dist": 200,
    },
    "primary_citation": (
        "[advances_fin_ml, ch.3] (meta-labeling) + "
        "[advances_fin_ml, ch.7] (purged k-fold) + "
        "Breiman (2001) DOI 10.1023/A:1010933404324 + "
        "[risk_parity, ch.5] + [volatility_trading, p.218] (iter 064 base) + "
        "Faber 2007 SSRN 962461 + Whaley 2009 JPM 35(3)"
    ),
    "primary_label": "iter064 base preserved verbatim; RF meta-label gates entire stream",
}

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "feature_bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "feature_bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "feature_bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
}


def load_prices(symbol: str, start: str, end: str, *, warmup_days: int = 250) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    if warmup_days <= 0:
        ext_start = start_ts
    else:
        pre = df.index[df.index <= start_ts]
        if len(pre) > warmup_days:
            ext_start = pre[-warmup_days]
        else:
            ext_start = df.index[0]
    m = (df.index >= ext_start) & (df.index <= end_ts)
    return df.loc[m, "adj_close"].astype(float)


def load_vix() -> pd.Series:
    df = pd.read_parquet(MACRO_DIR / "vix_daily.parquet")
    return df["VIX"].astype(float)


def load_t10y3m() -> pd.Series:
    df = pd.read_parquet(MACRO_DIR / "t10y3m_daily.parquet")
    return df["term_spread"].astype(float)


def load_iter064_returns(ds_name: str) -> pd.Series:
    if not ITER_064_RESULTS.exists():
        raise FileNotFoundError(f"iter 064 results not found at {ITER_064_RESULTS}")
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


def run_single_cfg(
    r_064: pd.Series, bench_prices_ext: pd.Series, vix: pd.Series, t10y3m: pd.Series,
) -> tuple[dict, pd.Series, dict]:
    X = build_feature_matrix(
        r_064=r_064, bench_prices=bench_prices_ext, vix=vix, t10y3m=t10y3m,
    )
    y = label_positive_return(r_064)
    X_clean, y_clean = warmup_drop(X, y)

    n_warmup_dropped = len(X) - len(X_clean)

    res = fit_predict_purged_kfold(
        X_clean, y_clean,
        n_folds=CFG["n_folds"], embargo=CFG["embargo"],
        threshold=CFG["threshold"], rf_params=CFG["rf_params"],
    )

    r_064_clean = r_064.loc[X_clean.index]
    cost_per_flip = CFG["cost_bps"] / 1e4
    r_066 = gate_iter064_with_meta(
        r_064_clean, res.oof_pred, cost_per_flip=cost_per_flip,
    )

    eq_curve = (1.0 + r_066).cumprod()
    pct_traded = float((res.oof_pred == 1).mean())
    flips = int((res.oof_pred.diff().abs().fillna(0) > 0).sum())
    common_064 = r_066.index.intersection(r_064.index)
    corr_066_064 = float(r_066.loc[common_064].corr(r_064.loc[common_064]))

    obs_sharpe = float(_sharpe(r_066))
    metrics = {
        "cfg_id": CFG["cfg_id"],
        "n_folds": CFG["n_folds"],
        "embargo": CFG["embargo"],
        "threshold": CFG["threshold"],
        "cost_bps": CFG["cost_bps"],
        "n_features": len(FEATURE_COLS),
        "n_bars_total": int(len(r_064)),
        "n_bars_after_warmup_drop": int(len(X_clean)),
        "n_bars_warmup_dropped": int(n_warmup_dropped),
        "bars": int(len(r_066)),
        "sharpe": obs_sharpe,
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "pct_traded": pct_traded,
        "n_flips": flips,
        "corr_066_064": corr_066_064,
        "r_064_sharpe": float(_sharpe(r_064_clean)),
        "r_064_cagr": float(_cagr((1.0 + r_064_clean).cumprod())),
        "r_064_mdd": float(_max_drawdown((1.0 + r_064_clean).cumprod())),
        "fold_aucs": res.fold_aucs,
        "avg_auc": res.avg_auc,
        "feature_importance_avg": res.feature_importance_avg,
        # Markowitz residual is vacuous for a binary multiplier on existing stream.
        "markowitz_residual_sharpe": 0.0,
        "markowitz_detail": {
            "note": "binary gate is multiplicative not convex — Markowitz residual undefined; reported 0",
        },
        "rolling21_worst": float(r_066.rolling(21).sum().min()),
    }
    extra = {
        "oof_proba_index": [str(t.date()) for t in res.oof_proba.index],
        "oof_proba_values": [round(float(x), 8) for x in res.oof_proba.tolist()],
        "oof_pred_values": [int(x) for x in res.oof_pred.tolist()],
        "fold_assignments": [int(x) for x in res.fold_assignments.tolist()],
        "r_064_clean_index": [str(t.date()) for t in r_064_clean.index],
        "r_064_clean_values": [round(float(x), 10) for x in r_064_clean.tolist()],
    }
    return metrics, r_066, extra


def cross_lib_check(r_066_pd: pd.Series, r_064_aligned: pd.Series, oof_pred: pd.Series) -> dict:
    """G7 parity on the post-prediction deterministic transform."""
    r_arr = r_064_aligned.to_numpy()
    pred_arr = oof_pred.to_numpy().astype(np.float64)
    np_out = gate_iter064_with_meta_np(r_arr, pred_arr, cost_per_flip=CFG["cost_bps"] / 1e4)
    pd_arr = r_066_pd.to_numpy()
    n = min(len(np_out), len(pd_arr))
    pd_arr = pd_arr[-n:]
    np_arr = np_out[-n:]
    eq_pd = np.cumprod(1.0 + pd_arr)
    eq_np = np.cumprod(1.0 + np_arr)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np,
        "abs_diff_pp": abs(cagr_pd - cagr_np) * 100.0,
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
        "extra": {},
        "pre_committed": True,
        "iter_label": "066-2026-04-25-1411-meta-label-rf-iter064",
    }

    vix = load_vix()
    t10y3m = load_t10y3m()

    for ds_name, ds in DATASETS.items():
        r_064 = load_iter064_returns(ds_name)
        bench_ext = load_prices(ds["feature_bench_ticker"], ds["start"], ds["end"], warmup_days=300)
        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"], warmup_days=0)
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"[{ds_name}] iter064 stream {r_064.index[0].date()} → "
            f"{r_064.index[-1].date()} ({len(r_064)} bars), "
            f"bench={ds['bench_ticker']} S={bench['sharpe']:.3f} "
            f"CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%}"
        )

        m, r_066, extra = run_single_cfg(r_064, bench_ext, vix, t10y3m)

        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in r_066.index],
                "net_returns": [round(float(x), 10) for x in r_066.tolist()],
            }
        }
        all_results["subcomponent_returns"][ds_name] = {
            "r_064": {
                "index": extra["r_064_clean_index"],
                "net_returns": extra["r_064_clean_values"],
            },
        }
        all_results["extra"][ds_name] = {
            "oof_proba_index": extra["oof_proba_index"],
            "oof_proba_values": extra["oof_proba_values"],
            "oof_pred_values": extra["oof_pred_values"],
            "fold_assignments": extra["fold_assignments"],
        }

        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        edge_064 = m["sharpe"] - m["r_064_sharpe"]
        cagr_uplift_064 = m["cagr"] - m["r_064_cagr"]
        print(
            f"  iter066 S={m['sharpe']:+.4f} (Δ frozen={edge_frozen:+.4f}, Δ064={edge_064:+.4f}) "
            f"CAGR={m['cagr']:+.2%} (Δ064={cagr_uplift_064:+.2%}) MDD={m['mdd']:.2%} "
            f"corr(066,064)={m['corr_066_064']:+.3f} "
            f"pct_traded={m['pct_traded']:.1%} "
            f"AUC fold={['{:.3f}'.format(a) for a in m['fold_aucs']]} avg={m['avg_auc']:.3f} "
            f"flips={m['n_flips']}"
        )
        print(
            f"  feature_importance avg: "
            f"{ {k: round(v, 4) for k,v in m['feature_importance_avg'].items()} }"
        )

        # G7 parity on post-prediction transform.
        r_064_aligned = r_064.loc[r_066.index]
        oof_pred = pd.Series(extra["oof_pred_values"], index=r_066.index)
        cl = cross_lib_check(r_066, r_064_aligned, oof_pred)
        all_results["crosslib"][ds_name] = cl
        print(
            f"    G7 cross-lib (post-prediction): CAGR pd={cl['cagr_pandas']:+.4%} "
            f"np={cl['cagr_numpy']:+.4%} Δ={cl['abs_diff_pp']:.6f} pp "
            f"(n={cl['n_bars_compared']})"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
