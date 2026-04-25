"""Iter 071 — Run iter 064 + SPY MR (RSI(2) + 200d gate, 4 cfgs) on 3 datasets.

4-cfg sensitivity sweep:
  - cfg1: th=5,  w_mr=0.05 — Connors canonical + small w
  - cfg2: th=5,  w_mr=0.10 — Connors canonical + moderate w
  - cfg3: th=3,  w_mr=0.05 — selective entries
  - cfg4: th=10, w_mr=0.05 — looser entries (more time-in-market)

cumulative_n_trials advance: 4340 → 4344 (+4).

Citations
---------
* `[algo_trading_chan, p.95, p.153-154]` — momentum filter on MR;
  MR + momentum complementarity.
* Connors-Alvarez (2009) ISBN 978-0-9755513-2-7 — RSI(2) canonical.
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base.
* Faber (2007) SSRN 962461 + `[stocks_on_the_move, p.21-30]` — QQQ_TREND.
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

from spy_mr import compute_spy_mr_returns  # noqa: E402
from numpy_reference_iter071 import compute_spy_mr_returns_np  # noqa: E402
from combined_046_qqqt_mr import combine_046_qqqt_mr  # noqa: E402

# Reuse iter 064's QQQ-trend module
ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
sys.path.insert(0, str(ITER_064_DIR))
from qqq_trend import compute_qqq_trend_returns  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
ITER_046_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "046-2026-04-25-0553-iter039-overlay-on-iter041"
ITER_046_RESULTS = ITER_046_DIR / "results.json"

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
    },
}

# Fixed iter-064 base structural ratio: 90:10 between r_046 and r_qqqt.
# When w_mr is added, w_046 and w_qqqt scale proportionally to (1-w_mr).
def make_cfg(rsi_th: float, w_mr: float, cfg_label: str) -> dict:
    w_046 = (1.0 - w_mr) * 0.90
    w_qqqt = (1.0 - w_mr) * 0.10
    return {
        "cfg_id": cfg_label,
        "rsi_period": 2,
        "rsi_threshold": float(rsi_th),
        "sma_filter": 200,
        "exit_sma": 5,
        "rf": 0.02,
        "cost_bps": 5.0,
        "w_046": float(w_046),
        "w_qqqt": float(w_qqqt),
        "w_mr": float(w_mr),
        "qqqt_lookback": 200,
        "qqqt_rf": 0.02,
        "qqqt_cost_bps": 5.0,
    }


CONFIGS: list[dict] = [
    make_cfg(5.0, 0.05, "iter064_plus_spy_mr_rsi2_th5_w005"),
    make_cfg(5.0, 0.10, "iter064_plus_spy_mr_rsi2_th5_w010"),
    make_cfg(3.0, 0.05, "iter064_plus_spy_mr_rsi2_th3_w005"),
    make_cfg(10.0, 0.05, "iter064_plus_spy_mr_rsi2_th10_w005"),
]


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_prices_with_warmup(
    symbol: str, start: str, end: str, warmup_days: int = 250
) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    extended_start = df.index[df.index <= start_ts]
    if len(extended_start) > warmup_days:
        extended_start = extended_start[-warmup_days]
    else:
        extended_start = df.index[0]
    m = (df.index >= extended_start) & (df.index <= end_ts)
    return df.loc[m, "adj_close"].astype(float)


def load_iter046_returns(ds_name: str) -> pd.Series:
    if not ITER_046_RESULTS.exists():
        raise FileNotFoundError(f"missing {ITER_046_RESULTS}")
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


def cross_lib_check_mr(
    spy_prices_ext: pd.Series, window_start: str, cfg: dict
) -> dict:
    """G7 parity: pandas vs numpy for r_mr only (the new module)."""
    pd_out = compute_spy_mr_returns(
        spy_prices_ext,
        rsi_period=cfg["rsi_period"],
        rsi_threshold=cfg["rsi_threshold"],
        sma_filter=cfg["sma_filter"],
        exit_sma=cfg["exit_sma"],
        rf=cfg["rf"],
        cost_bps=cfg["cost_bps"],
    )
    np_out = compute_spy_mr_returns_np(
        spy_prices_ext.values,
        rsi_period=cfg["rsi_period"],
        rsi_threshold=cfg["rsi_threshold"],
        sma_filter=cfg["sma_filter"],
        exit_sma=cfg["exit_sma"],
        rf=cfg["rf"],
        cost_bps=cfg["cost_bps"],
    )
    start_ts = pd.Timestamp(window_start)
    pd_arr = pd_out.values[pd_out.index >= start_ts]
    np_full_idx = spy_prices_ext.index[1:]
    mask_np = np_full_idx >= start_ts
    np_arr = np_out[mask_np]
    n = min(len(pd_arr), len(np_arr))
    pd_arr = pd_arr[-n:]
    np_arr = np_arr[-n:]
    if n < 2:
        return {
            "cagr_pandas": 0.0, "cagr_numpy": 0.0,
            "abs_diff_pp": 0.0, "max_abs_return_diff": 0.0,
            "n_bars_compared": n,
        }
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


def conditional_sharpe_split(
    r: pd.Series, gate_long: pd.Series
) -> dict:
    """Return Sharpe of `r` partitioned by a boolean gate (calm vs stress)."""
    common = r.index.intersection(gate_long.index)
    r_a = r.loc[common]
    g_a = gate_long.loc[common].astype(bool)
    if g_a.sum() < 10 or (~g_a).sum() < 10:
        return {"calm_sharpe": float("nan"), "stress_sharpe": float("nan"),
                "calm_n": int(g_a.sum()), "stress_n": int((~g_a).sum())}
    calm = r_a[g_a]
    stress = r_a[~g_a]
    return {
        "calm_sharpe": float(_sharpe(calm)) if calm.std() > 0 else 0.0,
        "stress_sharpe": float(_sharpe(stress)) if stress.std() > 0 else 0.0,
        "calm_n": int(g_a.sum()),
        "stress_n": int((~g_a).sum()),
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": CONFIGS,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "subcomponent_returns": {},
        "crosslib": {},
        "pre_committed": True,
        "iter_label": "071-2026-04-25-1606-iter064-plus-spy-mr-rsi2",
    }

    for ds_name, ds in DATASETS.items():
        r_046 = load_iter046_returns(ds_name)
        qqq_ext = load_prices_with_warmup("QQQ", ds["start"], ds["end"], 250)
        spy_ext = load_prices_with_warmup("SPY", ds["start"], ds["end"], 250)

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"\n[{ds_name}] iter046 stream {r_046.index[0].date()} → "
            f"{r_046.index[-1].date()} ({len(r_046)} bars), "
            f"QQQ ext {qqq_ext.index[0].date()}-{qqq_ext.index[-1].date()} "
            f"({len(qqq_ext)}), SPY ext {spy_ext.index[0].date()}-"
            f"{spy_ext.index[-1].date()} ({len(spy_ext)}), bench="
            f"{ds['bench_ticker']} S={bench['sharpe']:.3f} C={bench['cagr']:.2%}"
        )

        # Compute r_qqqt once (same across all 4 cfgs since cfg differs only on MR params)
        r_qqqt_full = compute_qqq_trend_returns(
            qqq_ext, lookback=200, rf=0.02, cost_bps=5.0,
        )
        start_ts = pd.Timestamp(ds["start"])
        r_qqqt = r_qqqt_full[r_qqqt_full.index >= start_ts]

        # SPY > 200d SMA gate (long-window) — used for conditional Sharpe diagnostic
        spy_pre = spy_ext.shift(1)
        spy_sma200_pre = spy_ext.rolling(200).mean().shift(1)
        gate_calm = (spy_pre > spy_sma200_pre)
        gate_calm = gate_calm.reindex(spy_ext.index[1:]).fillna(False)
        gate_calm = gate_calm[gate_calm.index >= start_ts]

        all_results["runs"][ds_name] = {}
        all_results["returns_series"][ds_name] = {}
        all_results["crosslib"][ds_name] = {}

        # Save subcomponents once (r_046, r_qqqt) — r_mr is per-cfg below
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

        for cfg in CONFIGS:
            print(f"\n=== {ds_name} — {cfg['cfg_id']} ===")
            r_mr_full = compute_spy_mr_returns(
                spy_ext,
                rsi_period=cfg["rsi_period"],
                rsi_threshold=cfg["rsi_threshold"],
                sma_filter=cfg["sma_filter"],
                exit_sma=cfg["exit_sma"],
                rf=cfg["rf"],
                cost_bps=cfg["cost_bps"],
            )
            r_mr = r_mr_full[r_mr_full.index >= start_ts]

            combined = combine_046_qqqt_mr(
                r_046, r_qqqt, r_mr,
                w_046=cfg["w_046"], w_qqqt=cfg["w_qqqt"], w_mr=cfg["w_mr"],
            )
            eq_curve = (1.0 + combined).cumprod()

            common = combined.index.intersection(r_046.index) \
                .intersection(r_qqqt.index).intersection(r_mr.index)
            r_046_a = r_046.loc[common]
            r_qqqt_a = r_qqqt.loc[common]
            r_mr_a = r_mr.loc[common]

            # r_mr standalone metrics
            eq_mr = (1.0 + r_mr_a).cumprod()
            r_mr_sharpe = float(_sharpe(r_mr_a))
            r_mr_cagr = float(_cagr(eq_mr))
            r_mr_mdd = float(_max_drawdown(eq_mr))
            rf_d = (1.0 + cfg["rf"]) ** (1.0 / 252.0) - 1.0
            time_in_market = float((np.abs(r_mr_a - rf_d) > 1e-9).mean())

            # Conditional Sharpe (calm vs stress) on r_mr
            cond = conditional_sharpe_split(r_mr_a, gate_calm)

            # Combined metrics
            obs_sharpe = float(_sharpe(combined))
            cagr_combined = float(_cagr(eq_curve))
            mdd_combined = float(_max_drawdown(eq_curve))

            # Cross-correlations
            corr_046_mr = float(r_046_a.corr(r_mr_a))
            corr_qqqt_mr = float(r_qqqt_a.corr(r_mr_a))
            corr_046_qqqt = float(r_046_a.corr(r_qqqt_a))

            # Diagnostic: corr to iter 064's static (recompute iter 064 base on common index)
            iter064_static = 0.9 * r_046_a + 0.1 * r_qqqt_a
            corr_071_064 = float(combined.loc[common].corr(iter064_static))

            m = {
                **cfg,
                "bars": int(len(combined)),
                "sharpe": obs_sharpe,
                "cagr": cagr_combined,
                "mdd": mdd_combined,
                "final_equity": float(eq_curve.iloc[-1]),
                "r_046_sharpe": float(_sharpe(r_046_a)),
                "r_046_cagr": float(_cagr((1.0 + r_046_a).cumprod())),
                "r_046_mdd": float(_max_drawdown((1.0 + r_046_a).cumprod())),
                "r_qqqt_sharpe": float(_sharpe(r_qqqt_a)),
                "r_qqqt_cagr": float(_cagr((1.0 + r_qqqt_a).cumprod())),
                "r_qqqt_mdd": float(_max_drawdown((1.0 + r_qqqt_a).cumprod())),
                "r_mr_sharpe": r_mr_sharpe,
                "r_mr_cagr": r_mr_cagr,
                "r_mr_mdd": r_mr_mdd,
                "r_mr_time_in_market": time_in_market,
                "r_mr_cond_calm_sharpe": cond["calm_sharpe"],
                "r_mr_cond_stress_sharpe": cond["stress_sharpe"],
                "r_mr_cond_calm_n": cond["calm_n"],
                "r_mr_cond_stress_n": cond["stress_n"],
                "corr_046_mr": corr_046_mr,
                "corr_qqqt_mr": corr_qqqt_mr,
                "corr_046_qqqt": corr_046_qqqt,
                "corr_071_064_static": corr_071_064,
            }
            all_results["runs"][ds_name][cfg["cfg_id"]] = m
            all_results["returns_series"][ds_name][cfg["cfg_id"]] = {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 10) for x in combined.tolist()],
            }

            edge_frozen = obs_sharpe - {
                "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
            }[ds_name]
            print(
                f"  combined S={obs_sharpe:+.4f} (Δ frozen={edge_frozen:+.4f}) "
                f"CAGR={cagr_combined:+.2%} MDD={mdd_combined:.2%}"
            )
            print(
                f"  r_mr S={r_mr_sharpe:+.4f} CAGR={r_mr_cagr:+.2%} "
                f"MDD={r_mr_mdd:.2%} TIM={time_in_market:.1%} "
                f"calm_S={cond['calm_sharpe']:+.3f} stress_S={cond['stress_sharpe']:+.3f}"
            )
            print(
                f"  corr(046,mr)={corr_046_mr:+.3f} "
                f"corr(qqqt,mr)={corr_qqqt_mr:+.3f} "
                f"corr(071,064_static)={corr_071_064:+.4f}"
            )

            cl = cross_lib_check_mr(spy_ext, ds["start"], cfg)
            all_results["crosslib"][ds_name][cfg["cfg_id"]] = cl
            print(
                f"    G7 cross-lib (r_mr only): max_ret_diff={cl['max_abs_return_diff']:.2e} "
                f"|Δ CAGR|={cl['abs_diff_pp']:.4f}pp"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
