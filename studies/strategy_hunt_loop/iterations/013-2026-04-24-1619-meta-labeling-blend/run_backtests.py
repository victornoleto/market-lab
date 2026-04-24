"""Iter 013 — Run meta-labeling pipeline on 3 datasets.

Mirrors iter 009's runner structure. Loads (SPY,TLT) or (QQQ,TLT) +
VIX, runs the meta-labeled blend pipeline, writes results.json.

Cumulative n_trials advance: 4252 → 4255 (1 cfg × 3 datasets).
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module=r"sklearn\..*",
)

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
sys.path.insert(0, str(ITER_DIR))

from meta_labeling import (  # noqa: E402
    META_CFG,
    apply_blend_with_meta,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
MACRO_DIR = ROOT / "data" / "external" / "macro"
VIX_PATH = MACRO_DIR / "vix_daily.parquet"


BLEND_CFG: dict = {
    "cfg_id": "vt15_L21_cap20",
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
}
COST_BPS_PER_LEG = 0.0002
COMBINED_CFG_ID = f"{BLEND_CFG['cfg_id']}+{META_CFG['cfg_id']}"


DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "start": "2002-07-26",
        "end": "2026-04-15",
        "role": "SPY+TLT 24y — longest TLT-available window",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+TLT 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "TLT",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+TLT 16y tech-heavy",
    },
}


def load_paired_returns(eq: str, bd: str, start: str, end: str) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    mask_eq = (df_eq.index >= start) & (df_eq.index <= end)
    mask_bd = (df_bd.index >= start) & (df_bd.index <= end)
    p_eq = df_eq.loc[mask_eq, "adj_close"]
    p_bd = df_bd.loc[mask_bd, "adj_close"]
    joined = pd.concat({"eq": p_eq, "bd": p_bd}, axis=1, join="inner").dropna()
    r = joined.pct_change().dropna()
    r.columns = [eq, bd]
    return r


def load_vix(align_index: pd.DatetimeIndex) -> pd.Series:
    df = pd.read_parquet(VIX_PATH)
    vix = df["VIX"].astype(float)
    vix_aligned = vix.reindex(align_index, method="ffill")
    return vix_aligned


def benchmark_metrics(returns: pd.Series) -> dict:
    eq = (1.0 + returns).cumprod()
    return {
        "sharpe": _sharpe(returns),
        "cagr": _cagr(eq),
        "mdd": _max_drawdown(eq),
        "n_bars": len(returns),
        "first": str(returns.index[0].date()),
        "last": str(returns.index[-1].date()),
    }


def run_single_dataset(
    returns: pd.DataFrame, vix: pd.Series
) -> tuple[dict, pd.Series, pd.DataFrame]:
    eq_col, bd_col = returns.columns
    net, pos_spy_g, pos_tlt_g, scale, meta_frame = apply_blend_with_meta(
        returns[eq_col], returns[bd_col], vix,
        target_vol=BLEND_CFG["target_vol"],
        lookback=BLEND_CFG["lookback"],
        max_leverage=BLEND_CFG["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
        train_window=META_CFG["train_window"],
        retrain_cadence=META_CFG["retrain_cadence"],
        warmup_bars=META_CFG["warmup_bars"],
        decision_threshold=META_CFG["decision_threshold"],
        random_state=META_CFG["random_state"],
    )
    eq = (1.0 + net).cumprod()

    # Diagnostics
    cap_hit = float(
        np.isclose(scale.to_numpy(float), BLEND_CFG["max_leverage"], rtol=1e-9, atol=1e-12).mean()
    )
    # Gate fire-rate (fraction of bars where the meta-gate is OFF).
    gate_fire_rate = float((meta_frame["gate"] < 1.0).mean())
    p_act_mean = float(meta_frame["p_act"].mean())
    p_act_std = float(meta_frame["p_act"].std())
    # Overlap diagnostic: gate-fire vs bottom-20% scale bars.
    s20 = scale.quantile(0.20)
    bottom20 = scale <= s20
    gate_off = meta_frame["gate"] < 1.0
    if int(gate_off.sum()) > 0 and int(bottom20.sum()) > 0:
        overlap_frac = float((bottom20 & gate_off).sum() / gate_off.sum())
    else:
        overlap_frac = float("nan")

    dpos_spy = pos_spy_g.diff().abs().fillna(pos_spy_g.iloc[0])
    dpos_tlt = pos_tlt_g.diff().abs().fillna(pos_tlt_g.iloc[0])
    turnover = float((dpos_spy + dpos_tlt).sum() * 252.0 / len(dpos_spy))

    m = {
        "cfg_id": COMBINED_CFG_ID,
        "blend_cfg": BLEND_CFG,
        "meta_cfg": META_CFG,
        "bars": len(net),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "scale_cap_hit_frac": cap_hit,
        "gate_fire_rate": gate_fire_rate,
        "p_act_mean": p_act_mean,
        "p_act_std": p_act_std,
        "gate_bottom20_overlap_frac": overlap_frac,
        "turnover_annual": turnover,
        "label_base_rate": float(meta_frame["label_realized"].mean()),
    }
    return m, net, meta_frame


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "blend_cfg": BLEND_CFG,
        "meta_cfg": META_CFG,
        "combined_cfg_id": COMBINED_CFG_ID,
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "meta_diagnostics": {},
        "leg_correlations": {},
        "pre_committed": True,
        "reference_iter": "008-2026-04-24-1411-single-cfg-ex-ante-blend",
        "vix_source": str(VIX_PATH.relative_to(ROOT)),
    }

    paired: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_paired_returns(ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"])
        paired[ds_name] = r
        bench_series = r.iloc[:, 0]  # equity-leg b&h benchmark
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr = float(r.corr().iloc[0, 1])
        all_results["leg_correlations"][ds_name] = corr
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} ρ_stockbond={corr:+.3f}"
        )

    for ds_name, r in paired.items():
        print(f"\n=== {ds_name} ({len(r)} bars) — {COMBINED_CFG_ID} ===")
        vix = load_vix(r.index)
        m, net, meta_frame = run_single_dataset(r, vix)
        all_results["runs"][ds_name] = {COMBINED_CFG_ID: m}
        all_results["returns_series"][ds_name] = {
            COMBINED_CFG_ID: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
        }
        all_results["meta_diagnostics"][ds_name] = {
            "index": [str(t.date()) for t in meta_frame.index],
            "p_act": meta_frame["p_act"].round(6).tolist(),
            "gate": meta_frame["gate"].round(4).tolist(),
            "rho_60": meta_frame["rho_60"].round(6).tolist(),
            "vix_z": meta_frame["vix_z"].round(6).tolist(),
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  {m['cfg_id']:60s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%}"
        )
        print(
            f"    gate_fire={m['gate_fire_rate']:.1%} "
            f"p_act mean/std={m['p_act_mean']:.3f}/{m['p_act_std']:.3f} "
            f"overlap_bottom20={m['gate_bottom20_overlap_frac']:.1%} "
            f"turnover={m['turnover_annual']:.1f}/yr"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
