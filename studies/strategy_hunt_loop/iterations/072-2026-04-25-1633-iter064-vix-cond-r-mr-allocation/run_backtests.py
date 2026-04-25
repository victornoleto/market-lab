"""Iter 072 — Run iter 064 base + regime-conditional r_mr (4 cfgs) on 3 datasets.

4-cfg sensitivity sweep: r_mr is the iter 071 best stream (RSI(2) th=10 +
Chan p.95 200d gate); regime classifier is binary VIX (Whaley 2009 thr=20):

  - cfg1: w_calm=0.10, w_stress=0.00 — primary; calm-only activation
  - cfg2: w_calm=0.15, w_stress=0.00 — aggressive calm
  - cfg3: w_calm=0.10, w_stress=0.05 — partial stress preservation
  - cfg4: w_calm=0.20, w_stress=0.00 — most aggressive calm

cumulative_n_trials advance: 4344 → 4348 (+4).

Citations
---------
* `[algo_trading_chan, p.95, p.153-154]` — momentum filter on MR + regime allocation.
* Whaley (2009) JPM 35(3) DOI 10.3905/JPM.2009.35.3.098 — VIX threshold 20.
* Bekaert-Hoerova (2014) SSRN 2294327 — VIX risk-aversion proxy.
* Connors-Alvarez (2009) ISBN 978-0-9755513-2-7 — RSI(2) + VIX timing.
* Faber (2007) SSRN 962461 + `[stocks_on_the_move, p.21-30]` — QQQ_TREND.
* `[risk_parity, ch.5]` + `[volatility_trading, p.218]` — iter 046 base.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX.
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

from regime_conditional_3leg import combine_regime_cond_3leg  # noqa: E402
from numpy_reference_iter072 import combine_regime_cond_3leg_np  # noqa: E402

# Reuse iter 064's QQQ_TREND module (Faber 2007 200d SMA filter)
ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
sys.path.insert(0, str(ITER_064_DIR))
from qqq_trend import compute_qqq_trend_returns  # noqa: E402

# Reuse iter 071's r_mr module (Connors-Alvarez RSI(2) SPY MR)
ITER_071_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "071-2026-04-25-1606-iter064-plus-spy-mr-rsi2"
sys.path.insert(0, str(ITER_071_DIR))
from spy_mr import compute_spy_mr_returns  # noqa: E402

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

DATASETS: dict[str, dict] = {
    "educational": {
        "bench_ticker": "SPY",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
    "spy_real": {
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
    "ndx_real": {
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "iter046_cfg_id": "iter039_on_iter041_50_50",
        "iter064_cfg_id": "iter046_plus_qqq_trend_w010_lookback200",
    },
}


def make_cfg(w_calm: float, w_stress: float, cfg_label: str) -> dict:
    return {
        "cfg_id": cfg_label,
        # r_mr params (fixed at iter 071 best)
        "rsi_period": 2,
        "rsi_threshold": 10.0,
        "sma_filter": 200,
        "exit_sma": 5,
        "rf": 0.02,
        "mr_cost_bps": 5.0,
        # qqqt params
        "qqqt_lookback": 200,
        "qqqt_rf": 0.02,
        "qqqt_cost_bps": 5.0,
        # regime-conditional 3-leg combiner params
        "w_mr_calm": float(w_calm),
        "w_mr_stress": float(w_stress),
        "vix_threshold": 20.0,
        "combiner_cost_bps": 5.0,
    }


CONFIGS: list[dict] = [
    make_cfg(0.10, 0.00, "iter064_vix_cond_calm010_stress000"),
    make_cfg(0.15, 0.00, "iter064_vix_cond_calm015_stress000"),
    make_cfg(0.10, 0.05, "iter064_vix_cond_calm010_stress005"),
    make_cfg(0.20, 0.00, "iter064_vix_cond_calm020_stress000"),
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


def load_vix() -> pd.Series:
    df = pd.read_parquet(VIX_PATH)
    df.index = pd.to_datetime(df.index)
    return df["VIX"].astype(float)


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


def load_iter064_returns(ds_name: str) -> pd.Series:
    if not ITER_064_RESULTS.exists():
        raise FileNotFoundError(f"missing {ITER_064_RESULTS}")
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
    series: pd.Series, gate_long: pd.Series
) -> dict:
    """Sharpe of `series` partitioned by a boolean gate (calm=True vs stress=False)."""
    common = series.index.intersection(gate_long.index)
    s = series.loc[common]
    g = gate_long.loc[common].astype(bool)
    n_calm = int(g.sum())
    n_stress = int((~g).sum())
    if n_calm < 30 or n_stress < 30:
        return {
            "calm_sharpe": float("nan"), "stress_sharpe": float("nan"),
            "calm_n": n_calm, "stress_n": n_stress,
        }
    calm = s[g]
    stress = s[~g]
    return {
        "calm_sharpe": float(_sharpe(calm)) if calm.std() > 0 else 0.0,
        "stress_sharpe": float(_sharpe(stress)) if stress.std() > 0 else 0.0,
        "calm_n": n_calm, "stress_n": n_stress,
    }


def cross_lib_check(
    r_046: pd.Series, r_qqqt: pd.Series, r_mr: pd.Series, vix: pd.Series, cfg: dict
) -> dict:
    """G7 parity: pandas vs numpy reference for the 3-leg regime-cond combiner."""
    pd_out = combine_regime_cond_3leg(
        r_046, r_qqqt, r_mr, vix,
        w_mr_calm=cfg["w_mr_calm"],
        w_mr_stress=cfg["w_mr_stress"],
        vix_threshold=cfg["vix_threshold"],
        cost_bps=cfg["combiner_cost_bps"],
    )
    common = pd_out.index
    a = r_046.loc[common].to_numpy()
    b = r_qqqt.loc[common].to_numpy()
    c = r_mr.loc[common].to_numpy()
    v = vix.reindex(common).ffill().bfill().to_numpy()

    np_out = combine_regime_cond_3leg_np(
        a, b, c, v,
        w_mr_calm=cfg["w_mr_calm"],
        w_mr_stress=cfg["w_mr_stress"],
        vix_threshold=cfg["vix_threshold"],
        cost_bps=cfg["combiner_cost_bps"],
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
        "configs": CONFIGS,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "subcomponent_returns": {},
        "crosslib": {},
        "pre_committed": True,
        "iter_label": "072-2026-04-25-1633-iter064-vix-cond-r-mr-allocation",
    }

    for ds_name, ds in DATASETS.items():
        r_046 = load_iter046_returns(ds_name)
        r_064 = load_iter064_returns(ds_name)
        qqq_ext = load_prices_with_warmup("QQQ", ds["start"], ds["end"], 250)
        spy_ext = load_prices_with_warmup("SPY", ds["start"], ds["end"], 250)

        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        print(
            f"\n[{ds_name}] r_046 {len(r_046)}b, r_064 {len(r_064)}b, "
            f"QQQ ext {len(qqq_ext)}b, SPY ext {len(spy_ext)}b, "
            f"bench={ds['bench_ticker']} S={bench['sharpe']:.3f} C={bench['cagr']:.2%}"
        )

        # Compute r_qqqt once (same across all 4 cfgs)
        r_qqqt_full = compute_qqq_trend_returns(
            qqq_ext, lookback=200, rf=0.02, cost_bps=5.0,
        )
        start_ts = pd.Timestamp(ds["start"])
        r_qqqt = r_qqqt_full[r_qqqt_full.index >= start_ts]

        # Compute r_mr once with iter 071 best params (RSI th=10)
        r_mr_full = compute_spy_mr_returns(
            spy_ext,
            rsi_period=CONFIGS[0]["rsi_period"],
            rsi_threshold=CONFIGS[0]["rsi_threshold"],
            sma_filter=CONFIGS[0]["sma_filter"],
            exit_sma=CONFIGS[0]["exit_sma"],
            rf=CONFIGS[0]["rf"],
            cost_bps=CONFIGS[0]["mr_cost_bps"],
        )
        r_mr = r_mr_full[r_mr_full.index >= start_ts]

        # SPY > 200d SMA gate (long-window) — used for r_mr conditional Sharpe diagnostic
        spy_pre = spy_ext.shift(1)
        spy_sma200_pre = spy_ext.rolling(200).mean().shift(1)
        gate_calm_spy = (spy_pre > spy_sma200_pre)
        gate_calm_spy = gate_calm_spy.reindex(spy_ext.index[1:]).fillna(False)
        gate_calm_spy = gate_calm_spy[gate_calm_spy.index >= start_ts]

        # VIX < 20 calm gate — used for r_072 / r_064 conditional Sharpe diagnostic
        vix_aligned_full = vix.reindex(r_046.index).ffill().bfill()
        vix_lag = vix_aligned_full.shift(1).bfill()
        gate_calm_vix = (vix_lag < 20.0)

        all_results["runs"][ds_name] = {}
        all_results["returns_series"][ds_name] = {}
        all_results["crosslib"][ds_name] = {}

        # Save subcomponents once
        all_results["subcomponent_returns"][ds_name] = {
            "r_046": {
                "index": [str(t.date()) for t in r_046.index],
                "net_returns": [round(float(x), 12) for x in r_046.tolist()],
            },
            "r_qqq_trend": {
                "index": [str(t.date()) for t in r_qqqt.index],
                "net_returns": [round(float(x), 12) for x in r_qqqt.tolist()],
            },
            "r_mr": {
                "index": [str(t.date()) for t in r_mr.index],
                "net_returns": [round(float(x), 12) for x in r_mr.tolist()],
            },
        }

        for cfg in CONFIGS:
            print(f"\n=== {ds_name} — {cfg['cfg_id']} ===")
            combined = combine_regime_cond_3leg(
                r_046, r_qqqt, r_mr, vix,
                w_mr_calm=cfg["w_mr_calm"],
                w_mr_stress=cfg["w_mr_stress"],
                vix_threshold=cfg["vix_threshold"],
                cost_bps=cfg["combiner_cost_bps"],
                return_diagnostics=True,
            )
            diag = combined.attrs["diagnostics"]
            eq_curve = (1.0 + combined).cumprod()

            common = combined.index
            r_046_a = r_046.loc[common]
            r_qqqt_a = r_qqqt.loc[common]
            r_mr_a = r_mr.loc[common]

            # Reference iter 064 static blend on the same bars
            iter064_static = 0.9 * r_046_a + 0.1 * r_qqqt_a
            corr_072_064 = float(combined.corr(iter064_static))

            # Reference iter 071 static blend (best cfg th10_w005)
            w_mr_071 = 0.05
            iter071_static = (
                (1 - w_mr_071) * 0.9 * r_046_a
                + (1 - w_mr_071) * 0.1 * r_qqqt_a
                + w_mr_071 * r_mr_a
            )
            corr_072_071 = float(combined.corr(iter071_static))

            # Δ vs iter 064 saved combined stream (most accurate)
            r_064_a = r_064.reindex(common).dropna()
            if len(r_064_a) >= len(common) * 0.99:
                delta_064_sharpe = float(_sharpe(combined)) - float(_sharpe(r_064_a))
                delta_064_cagr = float(_cagr(eq_curve)) - float(
                    _cagr((1 + r_064_a).cumprod())
                )
                delta_064_mdd = float(_max_drawdown(eq_curve)) - float(
                    _max_drawdown((1 + r_064_a).cumprod())
                )
                corr_072_064_saved = float(
                    combined.loc[r_064_a.index].corr(r_064_a)
                )
            else:
                delta_064_sharpe = float("nan")
                delta_064_cagr = float("nan")
                delta_064_mdd = float("nan")
                corr_072_064_saved = float("nan")

            # Combined metrics
            obs_sharpe = float(_sharpe(combined))
            cagr_combined = float(_cagr(eq_curve))
            mdd_combined = float(_max_drawdown(eq_curve))

            # r_mr standalone (same across cfgs but recompute on common index)
            eq_mr = (1.0 + r_mr_a).cumprod()
            r_mr_sharpe = float(_sharpe(r_mr_a))
            r_mr_cagr = float(_cagr(eq_mr))
            r_mr_mdd = float(_max_drawdown(eq_mr))
            rf_d = (1.0 + cfg["rf"]) ** (1.0 / 252.0) - 1.0
            time_in_market = float((np.abs(r_mr_a - rf_d) > 1e-9).mean())

            # r_mr conditional Sharpe (calm vs stress, SPY 200d gate)
            cond_mr = conditional_sharpe_split(r_mr_a, gate_calm_spy)
            # r_072 conditional Sharpe (calm vs stress, VIX gate)
            cond_072 = conditional_sharpe_split(combined, gate_calm_vix)
            # r_064 conditional Sharpe (calm vs stress, VIX gate) — for amplification check
            cond_064 = conditional_sharpe_split(iter064_static, gate_calm_vix)

            # Regime statistics
            is_stress = diag["is_stress"]
            pct_stress = float(is_stress.mean())
            n_flips = int((diag["delta_w_mr"] > 1e-12).sum())
            mean_w_mr = float(diag["w_mr"].mean())

            m = {
                **cfg,
                "bars": int(len(combined)),
                "sharpe": obs_sharpe,
                "cagr": cagr_combined,
                "mdd": mdd_combined,
                "final_equity": float(eq_curve.iloc[-1]),
                "delta_064_sharpe": delta_064_sharpe,
                "delta_064_cagr": delta_064_cagr,
                "delta_064_mdd": delta_064_mdd,
                "corr_072_064_static": corr_072_064,
                "corr_072_064_saved": corr_072_064_saved,
                "corr_072_071_static": corr_072_071,
                "r_mr_sharpe": r_mr_sharpe,
                "r_mr_cagr": r_mr_cagr,
                "r_mr_mdd": r_mr_mdd,
                "r_mr_time_in_market": time_in_market,
                "r_mr_cond_calm_sharpe": cond_mr["calm_sharpe"],
                "r_mr_cond_stress_sharpe": cond_mr["stress_sharpe"],
                "r_072_cond_calm_sharpe": cond_072["calm_sharpe"],
                "r_072_cond_stress_sharpe": cond_072["stress_sharpe"],
                "r_064_cond_calm_sharpe": cond_064["calm_sharpe"],
                "r_064_cond_stress_sharpe": cond_064["stress_sharpe"],
                "pct_stress_regime": pct_stress,
                "n_flips": n_flips,
                "mean_w_mr": mean_w_mr,
                # required for backwards-compat with iter 071's gate-evaluator pattern
                "corr_046_mr": float(r_046_a.corr(r_mr_a)),
                "corr_qqqt_mr": float(r_qqqt_a.corr(r_mr_a)),
                "corr_046_qqqt": float(r_046_a.corr(r_qqqt_a)),
                "r_mr_cond_calm_n": cond_mr["calm_n"],
                "r_mr_cond_stress_n": cond_mr["stress_n"],
            }
            all_results["runs"][ds_name][cfg["cfg_id"]] = m
            all_results["returns_series"][ds_name][cfg["cfg_id"]] = {
                "index": [str(t.date()) for t in combined.index],
                "net_returns": [round(float(x), 12) for x in combined.tolist()],
            }

            edge_frozen = obs_sharpe - {
                "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
            }[ds_name]
            print(
                f"  combined S={obs_sharpe:+.4f} (Δ frozen={edge_frozen:+.4f}, "
                f"Δ064={delta_064_sharpe:+.4f}) "
                f"CAGR={cagr_combined:+.2%} MDD={mdd_combined:.2%}"
            )
            print(
                f"  pct_stress={pct_stress:.1%} n_flips={n_flips} "
                f"mean_w_mr={mean_w_mr:.4f}"
            )
            print(
                f"  r_mr S={r_mr_sharpe:+.3f} TIM={time_in_market:.1%} "
                f"calm_S={cond_mr['calm_sharpe']:+.3f} "
                f"stress_S={cond_mr['stress_sharpe']:+.3f}"
            )
            print(
                f"  r_072 calm_S={cond_072['calm_sharpe']:+.3f} "
                f"stress_S={cond_072['stress_sharpe']:+.3f} "
                f"(r_064 calm={cond_064['calm_sharpe']:+.3f} "
                f"stress={cond_064['stress_sharpe']:+.3f})"
            )
            print(
                f"  corr(072,064_static)={corr_072_064:+.4f} "
                f"corr(072,071_static)={corr_072_071:+.4f}"
            )

            cl = cross_lib_check(r_046, r_qqqt, r_mr, vix, cfg)
            all_results["crosslib"][ds_name][cfg["cfg_id"]] = cl
            print(
                f"    G7 cross-lib: max_ret_diff={cl['max_abs_return_diff']:.2e} "
                f"|Δ CAGR|={cl['abs_diff_pp']:.4f}pp"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
