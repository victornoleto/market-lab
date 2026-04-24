"""Iter 008 — Single-config ex-ante vol-managed SPY+TLT blend.

**Pre-committed cfg** ``vt15_L21_cap20`` (literature-anchored) — see
``hypothesis.md``. NO grid, NO sweep, NO post-hoc selection.

Reuses iter 006's simulator (`../006-*/stock_bond_blend.py`) verbatim.
Reuses iter 006's dataset definitions (SPY+TLT edu/spy, QQQ+TLT ndx).

Cumulative n_trials advance after iter 008: 4237 → 4240.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity.
* `[systematic_trading, p.144, p.170-171, ch.11]` — target_vol / IDM cap.
* Moreira & Muir (2017), *JoF* 72(4) — variance-scaling form.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER006_DIR = ITER_DIR.parent / "006-2026-04-24-1027-vol-managed-60-40"
ROOT = ITER_DIR.parents[3]

# Reuse iter 006's simulator (no copy).
sys.path.insert(0, str(ITER006_DIR))
from stock_bond_blend import apply_blend_variance_target  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# ---------------------------------------------------------------------------
# Pre-committed single config (see hypothesis.md § Pre-committed configuration)
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "vt15_L21_cap20",
    "target_vol": 0.15,    # [systematic_trading, p.144] mid-institutional equity
    "lookback": 21,        # Moreira-Muir 2017 canonical 1-month vol window
    "max_leverage": 2.0,   # ≤ 2.5 IDM cap [systematic_trading, p.170-171]
}
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit of per-leg position change

# ---------------------------------------------------------------------------
# Datasets (identical to iter 006)
# ---------------------------------------------------------------------------

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


def run_single_cfg(returns: pd.DataFrame) -> tuple[dict, pd.Series]:
    eq_col, bd_col = returns.columns
    net, pos_spy, pos_tlt, scale = apply_blend_variance_target(
        returns[eq_col], returns[bd_col],
        target_vol=CFG["target_vol"],
        lookback=CFG["lookback"],
        max_leverage=CFG["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(scale.to_numpy(float), CFG["max_leverage"], rtol=1e-9, atol=1e-12).mean()
    )
    w_spy_median = float((pos_spy / scale).median())
    dpos_spy = pos_spy.diff().abs().fillna(pos_spy.iloc[0])
    dpos_tlt = pos_tlt.diff().abs().fillna(pos_tlt.iloc[0])
    turnover = float((dpos_spy + dpos_tlt).sum() * 252.0 / len(dpos_spy))

    m = {
        "cfg_id": CFG["cfg_id"],
        "target_vol": CFG["target_vol"],
        "lookback": CFG["lookback"],
        "max_leverage": CFG["max_leverage"],
        "bars": len(net),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_cap_hit_frac": cap_hit,
        "w_spy_median": w_spy_median,
        "turnover_annual": turnover,
    }
    return m, net


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
        "pre_committed": True,
        "reference_iter": "006-2026-04-24-1027-vol-managed-60-40",
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
        print(f"\n=== {ds_name} ({len(r)} bars) — single cfg {CFG['cfg_id']} ===")
        m, net = run_single_cfg(r)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  {m['cfg_id']:16s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale_med={m['scale_median']:.2f} cap_hit={m['scale_cap_hit_frac']:.1%} "
            f"w_spy_med={m['w_spy_median']:.2f}"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
