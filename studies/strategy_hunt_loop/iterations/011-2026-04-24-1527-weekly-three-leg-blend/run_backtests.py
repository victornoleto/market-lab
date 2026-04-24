"""Iter 011 — Weekly-rebalance 3-leg vol-managed SPY+TLT+GLD blend runner.

**Pre-committed cfg** ``vt15_Lw4_cap20_3leg_weekly`` (see hypothesis.md).
NO grid, NO sweep, NO post-hoc selection. Params are identical to
iter 010's 3-leg daily blend except rebalance cadence = weekly W-FRI
and ``lookback = 4 weeks`` (calendar equivalent of 21 trading days).

Cumulative n_trials advance after iter 011: 4246 → 4249.

Citations
---------
* `[systematic_trading, p.144, p.170-171, ch.11]` — target_vol / IDM cap,
  frequency-agnostic.
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity N-asset form.
* Moreira & Muir (2017), *JoF* 72(4) — variance-scaling canonical form
  (monthly data, ~12-mo lookback; weekly 4-wk lookback is midway
  between daily 21-bar and monthly 12-mo).
* `[advances_fin_ml, p.162-164, 208-211, 222-223, 31-34]`.
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
from weekly_three_leg_blend import apply_weekly_blend, resample_returns_weekly  # noqa: E402

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
    "cfg_id": "vt15_Lw4_cap20_3leg_weekly",
    "target_vol": 0.15,
    "lookback": 4,          # weeks
    "max_leverage": 2.0,
    "periods_per_year": 52,
    "rebalance_cadence": "W-FRI",
}
COST_BPS_PER_LEG = 0.0002  # 2 bps per unit of per-leg position change (weekly)

# ---------------------------------------------------------------------------
# Datasets — identical windows to iter 010 for like-for-like comparison
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2004-11-18",
        "end": "2026-04-15",
        "role": "SPY+TLT+GLD ~21y weekly (GLD-constrained start)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+TLT+GLD 17y weekly post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "TLT",
        "gold_symbol": "GLD",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+TLT+GLD 16y weekly tech-heavy",
    },
}


def load_triple_returns(eq: str, bd: str, gd: str, start: str, end: str) -> pd.DataFrame:
    """Load daily returns for 3 legs — same shape as iter 010."""
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    df_gd = pd.read_parquet(TIINGO_DIR / f"{gd}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    m_gd = (df_gd.index >= start) & (df_gd.index <= end)
    p = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd": df_bd.loc[m_bd, "adj_close"],
        "gd": df_gd.loc[m_gd, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd, gd]
    return r


def weekly_benchmark_metrics(weekly_returns: pd.Series) -> dict:
    """Benchmark metrics on weekly-resampled equity-leg returns.

    Uses ``periods_per_year=52`` for Sharpe and CAGR annualisation so
    the candidate-vs-benchmark comparison is apples-to-apples weekly.
    """
    eq = (1.0 + weekly_returns).cumprod()
    return {
        "sharpe": _sharpe(weekly_returns, periods_per_year=52),
        "cagr": _cagr(eq, periods_per_year=52),
        "mdd": _max_drawdown(eq),
        "n_bars_weekly": len(weekly_returns),
        "first": str(weekly_returns.index[0].date()),
        "last": str(weekly_returns.index[-1].date()),
    }


def run_single_cfg(returns_daily: pd.DataFrame) -> tuple[dict, pd.Series, pd.DataFrame, pd.Series]:
    eq_col, bd_col, gd_col = returns_daily.columns
    net, positions, scale = apply_weekly_blend(
        returns_daily[eq_col], returns_daily[bd_col], returns_daily[gd_col],
        target_vol=CFG["target_vol"],
        lookback=CFG["lookback"],
        max_leverage=CFG["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    eq = (1.0 + net).cumprod()
    cap_hit = float(
        np.isclose(scale.to_numpy(float), CFG["max_leverage"], rtol=1e-9, atol=1e-12).mean()
    )
    w = positions.div(scale.replace(0, np.nan), axis=0)
    w_medians = {c: float(w[c].median()) for c in positions.columns}
    turnover_per_leg = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(abs(positions[c].iloc[0]))
        turnover_per_leg[c] = float(dpos.sum() * 52.0 / len(dpos))
    turnover_total = sum(turnover_per_leg.values())

    m = {
        "cfg_id": CFG["cfg_id"],
        "target_vol": CFG["target_vol"],
        "lookback_weeks": CFG["lookback"],
        "max_leverage": CFG["max_leverage"],
        "periods_per_year": 52,
        "bars_weekly": len(net),
        "sharpe": float(_sharpe(net, periods_per_year=52)),
        "cagr": float(_cagr(eq, periods_per_year=52)),
        "mdd": float(_max_drawdown(eq)),
        "final_equity": float(eq.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_cap_hit_frac": cap_hit,
        "w_median": w_medians,
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
    }
    return m, net, positions, scale


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations_weekly": {},
        "pre_committed": True,
        "reference_iter": "010-2026-04-24-1506-three-asset-spy-tlt-gld-blend",
        "cadence": "weekly W-FRI",
    }

    daily_triples: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r_daily = load_triple_returns(
            ds["equity_symbol"], ds["bond_symbol"], ds["gold_symbol"],
            ds["start"], ds["end"],
        )
        daily_triples[ds_name] = r_daily
        # Compute weekly benchmark on the equity leg.
        weekly = resample_returns_weekly(r_daily)
        weekly_eq_ret = weekly.iloc[:, 0]
        bench = weekly_benchmark_metrics(weekly_eq_ret)
        all_results["benchmarks"][ds_name] = bench
        corr_mat_weekly = weekly.corr()
        all_results["leg_correlations_weekly"][ds_name] = {
            "eq_bd": float(corr_mat_weekly.iloc[0, 1]),
            "eq_gd": float(corr_mat_weekly.iloc[0, 2]),
            "bd_gd": float(corr_mat_weekly.iloc[1, 2]),
        }
        print(
            f"[{ds_name}] weekly-benchmark {ds['equity_symbol']} b&h "
            f"{bench['first']} → {bench['last']} ({bench['n_bars_weekly']} bars) "
            f"Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%} "
            f"ρ_w(eq,bd)={corr_mat_weekly.iloc[0, 1]:+.3f} "
            f"ρ_w(eq,gd)={corr_mat_weekly.iloc[0, 2]:+.3f} "
            f"ρ_w(bd,gd)={corr_mat_weekly.iloc[1, 2]:+.3f}"
        )

    for ds_name, r_daily in daily_triples.items():
        print(f"\n=== {ds_name} ({len(r_daily)} daily bars) — weekly cfg {CFG['cfg_id']} ===")
        m, net, positions, scale = run_single_cfg(r_daily)
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
            f"  {m['cfg_id']:32s} Sharpe={m['sharpe']:+.4f} (Δ={edge:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"scale_med={m['scale_median']:.2f} cap_hit={m['scale_cap_hit_frac']:.1%}"
        )
        w_str = " ".join(f"{c}:{m['w_median'][c]:.2f}" for c in positions.columns)
        print(f"    weight_median: {w_str}")
        print(f"    turnover/yr total={m['turnover_annual_total']:.2f} (weekly cadence)")

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
