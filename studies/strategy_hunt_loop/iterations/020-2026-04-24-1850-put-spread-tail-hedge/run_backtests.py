"""Iter 020 — Put-spread-hedged iter-016 stack on 3 datasets.

Single pre-committed cfg ``ntsx_vm_vt15_L21_cap20_pp5_10_1m``. No grid,
no sweep, no post-hoc selection. Adds a monthly-rolled 5%/10% OTM put
spread (priced via BS with VIX as IV) to iter 016's equity leg, then
runs the identical 60:40 × vol-target stack on the hedged stream.

Cumulative n_trials advance: 4264 → 4267 (+ 1 cfg × 3 ds).

Citations
---------
* `[volatility_trading, p.11, p.41]` — BSM pricing + SPX fat-tail.
* `[risk_parity, p.10-11, ch.1]` — iter 016 base stack.
* `[systematic_trading, p.40, ch.2]` — vol standardisation primitive.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_016_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / "016-2026-04-24-1729-static-stack-vm-hybrid"
sys.path.insert(0, str(ITER_DIR))
sys.path.insert(0, str(ITER_016_DIR))

from put_spread_hedge import apply_put_spread_hedged_stack  # noqa: E402

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"
VIX_PATH = ROOT / "data" / "external" / "macro" / "vix_daily.parquet"

# ---------------------------------------------------------------------------
# Pre-committed single config
# ---------------------------------------------------------------------------
CFG: dict = {
    "cfg_id": "ntsx_vm_vt15_L21_cap20_pp5_10_1m",
    # iter 016 inheritance (identical)
    "eq_weight": 0.6,
    "bd_weight": 0.4,
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
    # put-spread overlay (new)
    "k_long_pct": 0.95,
    "k_short_pct": 0.90,
    "dte_days": 21,
    "rf": 0.02,
    "cost_bps_per_roll": 5.0,
    "hedge_notional_ratio": 1.0,
    "rebalance": "daily",
    "funding_cost_modeled": False,
}
COST_BPS_PER_LEG = 0.0002

# ---------------------------------------------------------------------------
# Datasets — IEF-inception aligned (same as iter 016)
# ---------------------------------------------------------------------------
DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2006-01-03",
        "end": "2026-04-14",
        "role": "SPY+IEF ~20y (IEF-inception-aligned)",
        "iv_scale": 1.0,  # VIX = SPX IV proxy
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2009-06-25",
        "end": "2026-04-14",
        "role": "SPY+IEF 17y post-GFC",
        "iv_scale": 1.0,
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "IEF",
        "start": "2010-02-12",
        "end": "2026-04-14",
        "role": "QQQ+IEF 16y tech-heavy",
        "iv_scale": 1.1,  # NDX IV ~10% above SPX (VXN vs VIX)
    },
}


def load_pair_prices_and_returns(eq: str, bd: str, start: str, end: str):
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    p = pd.concat({
        "eq_price": df_eq.loc[m_eq, "adj_close"],
        "bd_price": df_bd.loc[m_bd, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd]
    # Preserve the equity price series for the options pricer, aligned
    # to the returns index.
    prices_eq = p["eq_price"].loc[r.index]
    return r, prices_eq


def load_vix_aligned(index: pd.DatetimeIndex) -> pd.Series:
    vix = pd.read_parquet(VIX_PATH)["VIX"]
    # VIX index is pandas DateTimeIndex at daily; reindex to our bars
    vix_aligned = vix.reindex(index).ffill()
    if vix_aligned.isna().any():
        n_na = int(vix_aligned.isna().sum())
        # Forward-fill leading NAs with the first valid; last resort
        vix_aligned = vix_aligned.fillna(method="bfill").fillna(method="ffill")
        if vix_aligned.isna().any():
            raise ValueError(f"VIX alignment left {n_na} NaN after ffill/bfill")
    return vix_aligned


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
    returns: pd.DataFrame, prices_eq: pd.Series,
    vix: pd.Series, iv_scale: float,
) -> tuple[dict, pd.Series, pd.Series, dict]:
    eq_col, bd_col = returns.columns
    net, pos_eq, pos_bd, scale, overlay = apply_put_spread_hedged_stack(
        returns[eq_col], returns[bd_col], prices_eq, vix,
        eq_weight=CFG["eq_weight"],
        bd_weight=CFG["bd_weight"],
        target_vol=CFG["target_vol"],
        lookback=CFG["lookback"],
        max_leverage=CFG["max_leverage"],
        k_long_pct=CFG["k_long_pct"],
        k_short_pct=CFG["k_short_pct"],
        dte_days=CFG["dte_days"],
        rf=CFG["rf"],
        iv_scale=iv_scale,
        cost_bps_per_roll=CFG["cost_bps_per_roll"],
        hedge_notional_ratio=CFG["hedge_notional_ratio"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq_curve = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(scale.to_numpy(float), CFG["max_leverage"], atol=1e-9).mean()
    )
    turnover_per_leg = {}
    for c_name, c_series in [("EQ", pos_eq), ("BD", pos_bd)]:
        dpos = c_series.diff().abs().fillna(c_series.iloc[0])
        turnover_per_leg[c_name] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    # Hedge diagnostics
    overlay_cum = float((1.0 + overlay).prod() - 1.0)
    overlay_cagr = float((1.0 + overlay).prod() ** (252.0 / len(overlay)) - 1.0)
    overlay_sharpe = float(_sharpe(overlay))
    # Fraction of bars with positive hedge return (sanity: expect < 50% since
    # most bars are theta drag).
    frac_positive = float((overlay > 0).mean())

    m = {
        "cfg_id": CFG["cfg_id"],
        "eq_weight": CFG["eq_weight"],
        "bd_weight": CFG["bd_weight"],
        "target_vol": CFG["target_vol"],
        "lookback": CFG["lookback"],
        "max_leverage": CFG["max_leverage"],
        "k_long_pct": CFG["k_long_pct"],
        "k_short_pct": CFG["k_short_pct"],
        "dte_days": CFG["dte_days"],
        "hedge_notional_ratio": CFG["hedge_notional_ratio"],
        "iv_scale": iv_scale,
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_min": float(scale.min()),
        "scale_max": float(scale.max()),
        "scale_cap_hit_frac": cap_hit,
        "scale_zero_frac": float((scale < 1e-6).mean()),
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
        "overlay_cum_return": overlay_cum,
        "overlay_annualized": overlay_cagr,
        "overlay_sharpe": overlay_sharpe,
        "overlay_frac_positive_bars": frac_positive,
    }
    return m, net, overlay, {"pos_eq": pos_eq, "pos_bd": pos_bd, "scale": scale}


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "overlay_series": {},
        "leg_correlations": {},
        "pre_committed": True,
        "iter_label": "020-2026-04-24-1850-put-spread-tail-hedge",
    }

    for ds_name, ds in DATASETS.items():
        r, prices_eq = load_pair_prices_and_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"],
        )
        vix = load_vix_aligned(r.index)
        bench_series = r.iloc[:, 0]
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr = r.corr().iloc[0, 1]
        all_results["leg_correlations"][ds_name] = {"eq_bd": float(corr)}
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} ρ(eq,bd)={corr:+.3f} "
            f"VIX[mean/med]={vix.mean():.1f}/{vix.median():.1f}"
        )

        print(f"\n=== {ds_name} ({len(r)} bars) — cfg {CFG['cfg_id']} ===")
        m, net, overlay, _ = run_single_cfg(r, prices_eq, vix, ds["iv_scale"])
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": net.round(10).tolist(),
            }
        }
        all_results["overlay_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in overlay.index],
                "overlay_returns": overlay.round(10).tolist(),
            }
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge = m["sharpe"] - bench_sharpe
        print(
            f"  {m['cfg_id']:34s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale[m/med]={m['scale_mean']:.2f}/{m['scale_median']:.2f} "
            f"cap_hit={m['scale_cap_hit_frac']:.1%}"
        )
        print(
            f"    overlay: annual={m['overlay_annualized']:+.2%} "
            f"Sharpe={m['overlay_sharpe']:+.3f} pos_bars={m['overlay_frac_positive_bars']:.1%} "
            f"| turnover/yr={m['turnover_annual_total']:.2f}"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
