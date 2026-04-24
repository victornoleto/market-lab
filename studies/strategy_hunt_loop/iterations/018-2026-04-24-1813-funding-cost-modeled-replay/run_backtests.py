"""Iter 018 — Funding-cost-modeled iter 016 replay on 3 datasets.

**Pre-committed cfg** ``ntsx_vm_vt15_L21_cap20`` — same as iter 016,
plus per-bar funding cost `(scale - 1) × r_Tbill`. No grid, no sweep,
no post-hoc selection. Zero new trials — `cumulative_n_trials` stays
at 4264.

Citations
---------
* `[risk_parity, p.80-84, ch.4]` — levered-return decomposition.
* `[systematic_trading, p.170-171, ch.11]` — IDM / margin cost.
* `[ilmanen_expected_returns, ch.3]` — risk-free rate as universal
  deflator.
* NTSX prospectus — synthetic 90/60 stack funding cost.
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
from funding_cost_wrapper import (  # noqa: E402
    PRE_SHV_PAD_ANNUAL,
    PRE_SHV_PAD_DAILY,
    apply_static_stack_vm_funded,
    load_shv_daily_return,
)

from ai_trade.backtest.metrics.performance import (  # noqa: E402
    cagr as _cagr,
    max_drawdown as _max_drawdown,
    sharpe as _sharpe,
)

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# ---------------------------------------------------------------------------
# Pre-committed single config (identical to iter 016)
# ---------------------------------------------------------------------------

CFG: dict = {
    "cfg_id": "ntsx_vm_vt15_L21_cap20_funded",
    "eq_weight": 0.6,
    "bd_weight": 0.4,
    "target_vol": 0.15,
    "lookback": 21,
    "max_leverage": 2.0,
    "rebalance": "daily",
    "funding_cost_modeled": True,       # <-- the iter 018 change
    "r_tbill_source": "SHV (Tiingo) + 4.75% pre-SHV pad for 2006",
    "pre_shv_pad_annual": PRE_SHV_PAD_ANNUAL,
    "pre_shv_pad_daily": PRE_SHV_PAD_DAILY,
}
COST_BPS_PER_LEG = 0.0002

# ---------------------------------------------------------------------------
# Datasets — identical to iter 016 for direct comparability
# ---------------------------------------------------------------------------

DATASETS: dict[str, dict] = {
    "educational": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2006-01-03",
        "end": "2026-04-15",
        "role": "SPY+IEF ~20y (IEF-inception-aligned)",
    },
    "spy_real": {
        "equity_symbol": "SPY",
        "bond_symbol": "IEF",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "role": "SPY+IEF 17y post-GFC",
    },
    "ndx_real": {
        "equity_symbol": "QQQ",
        "bond_symbol": "IEF",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "role": "QQQ+IEF 16y tech-heavy",
    },
}


def load_pair_returns(eq: str, bd: str, start: str, end: str) -> pd.DataFrame:
    df_eq = pd.read_parquet(TIINGO_DIR / f"{eq}.parquet")
    df_bd = pd.read_parquet(TIINGO_DIR / f"{bd}.parquet")
    m_eq = (df_eq.index >= start) & (df_eq.index <= end)
    m_bd = (df_bd.index >= start) & (df_bd.index <= end)
    p = pd.concat({
        "eq": df_eq.loc[m_eq, "adj_close"],
        "bd": df_bd.loc[m_bd, "adj_close"],
    }, axis=1, join="inner").dropna()
    r = p.pct_change().dropna()
    r.columns = [eq, bd]
    return r


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


def run_single_cfg(returns: pd.DataFrame) -> tuple[dict, pd.Series, pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    eq_col, bd_col = returns.columns
    r_tbill = load_shv_daily_return(returns.index)
    net_post, net_gross, pos_eq, pos_bd, scale, funding_cost = apply_static_stack_vm_funded(
        returns[eq_col],
        returns[bd_col],
        r_tbill,
        eq_weight=CFG["eq_weight"],
        bd_weight=CFG["bd_weight"],
        target_vol=CFG["target_vol"],
        lookback=CFG["lookback"],
        max_leverage=CFG["max_leverage"],
        cost_bps_per_leg=COST_BPS_PER_LEG,
    )
    positions = pd.DataFrame({"EQ": pos_eq, "BD": pos_bd})
    eq_curve_post = (1.0 + net_post).cumprod()
    eq_curve_gross = (1.0 + net_gross).cumprod()

    cap_hit = float(
        np.isclose(scale.to_numpy(float), CFG["max_leverage"], atol=1e-9).mean()
    )
    turnover_per_leg = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    # Decompose funding cost impact on annual.
    fc_annual_mean_bps = float(
        funding_cost.mean() * 252.0 * 10000.0
    )  # bps/year
    # Sharpe damage = (mean daily fc × 252) / (std daily returns × sqrt(252))
    sharpe_damage = float(
        funding_cost.mean() * 252.0
        / (net_gross.std() * np.sqrt(252.0))
    )

    m = {
        "cfg_id": CFG["cfg_id"],
        "eq_weight": CFG["eq_weight"],
        "bd_weight": CFG["bd_weight"],
        "target_vol": CFG["target_vol"],
        "lookback": CFG["lookback"],
        "max_leverage": CFG["max_leverage"],
        "bars": int(len(net_post)),
        # Post-funding-cost metrics (canonical)
        "sharpe": float(_sharpe(net_post)),
        "cagr": float(_cagr(eq_curve_post)),
        "mdd": float(_max_drawdown(eq_curve_post)),
        "final_equity": float(eq_curve_post.iloc[-1]),
        # Pre-funding-cost (iter 016 replication)
        "sharpe_gross": float(_sharpe(net_gross)),
        "cagr_gross": float(_cagr(eq_curve_gross)),
        "mdd_gross": float(_max_drawdown(eq_curve_gross)),
        # Scale / leverage statistics
        "scale_mean": float(scale.mean()),
        "scale_median": float(scale.median()),
        "scale_min": float(scale.min()),
        "scale_max": float(scale.max()),
        "scale_cap_hit_frac": cap_hit,
        "scale_zero_frac": float((scale < 1e-6).mean()),
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
        # Funding-cost decomposition
        "funding_cost_annual_bps": fc_annual_mean_bps,
        "funding_cost_sharpe_damage": sharpe_damage,
        "funding_cost_mean_per_bar": float(funding_cost.mean()),
        "funding_cost_std_per_bar": float(funding_cost.std()),
        "funding_cost_max_per_bar": float(funding_cost.max()),
        "excess_leverage_mean": float((scale - 1.0).clip(lower=0.0).mean()),
        "excess_leverage_frac_nonzero": float(((scale - 1.0) > 1e-9).mean()),
    }
    return m, net_post, net_gross, positions, scale, funding_cost


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "cost_bps_per_leg": COST_BPS_PER_LEG,
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "gross_returns_series": {},
        "leg_correlations": {},
        "pre_committed": True,
        "iter_label": "018-2026-04-24-1813-funding-cost-modeled-replay",
        "cumulative_n_trials_unchanged": 4264,
        "note": (
            "Same cfg as iter 016 — zero new trials. Only diff: "
            "per-bar funding cost = max(scale-1, 0) × r_Tbill (SHV)."
        ),
    }

    pairs: dict[str, pd.DataFrame] = {}
    for ds_name, ds in DATASETS.items():
        r = load_pair_returns(ds["equity_symbol"], ds["bond_symbol"], ds["start"], ds["end"])
        pairs[ds_name] = r
        bench_series = r.iloc[:, 0]
        bench = benchmark_metrics(bench_series)
        all_results["benchmarks"][ds_name] = bench
        corr = r.corr().iloc[0, 1]
        all_results["leg_correlations"][ds_name] = {"eq_bd": float(corr)}
        print(
            f"[{ds_name}] {ds['equity_symbol']}+{ds['bond_symbol']} "
            f"{bench['first']} → {bench['last']} ({bench['n_bars']} bars) "
            f"equity_bench Sharpe={bench['sharpe']:.3f} CAGR={bench['cagr']:.2%} "
            f"MDD={bench['mdd']:.2%} ρ(eq,bd)={corr:+.3f}"
        )

    for ds_name, r in pairs.items():
        print(f"\n=== {ds_name} ({len(r)} bars) — cfg {CFG['cfg_id']} ===")
        m, net_post, net_gross, positions, scale, funding_cost = run_single_cfg(r)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net_post.index],
                "net_returns": net_post.round(12).tolist(),
            }
        }
        all_results["gross_returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "net_returns": net_gross.round(12).tolist(),
                "funding_cost": funding_cost.round(12).tolist(),
                "scale": scale.round(8).tolist(),
            }
        }
        bench_sharpe = all_results["benchmarks"][ds_name]["sharpe"]
        edge_post = m["sharpe"] - bench_sharpe
        edge_gross = m["sharpe_gross"] - bench_sharpe
        print(
            f"  {m['cfg_id']:35s} Sharpe_post={m['sharpe']:+.4f} "
            f"(edge_post={edge_post:+.4f}) "
            f"Sharpe_gross={m['sharpe_gross']:+.4f} "
            f"(edge_gross={edge_gross:+.4f})"
        )
        print(
            f"    CAGR post/gross={m['cagr']:+.2%}/{m['cagr_gross']:+.2%} "
            f"MDD post/gross={m['mdd']:.2%}/{m['mdd_gross']:.2%}"
        )
        print(
            f"    funding_cost_annual={m['funding_cost_annual_bps']:+.1f} bps "
            f"sharpe_damage={-m['funding_cost_sharpe_damage']:+.4f} "
            f"excess_lev_mean={m['excess_leverage_mean']:.3f} "
            f"excess_lev_nonzero_frac={m['excess_leverage_frac_nonzero']:.1%}"
        )
        print(
            f"    scale[mean/med/min/max]={m['scale_mean']:.2f}/{m['scale_median']:.2f}/"
            f"{m['scale_min']:.2f}/{m['scale_max']:.2f} "
            f"cap_hit={m['scale_cap_hit_frac']:.2%}"
        )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(json.dumps(all_results, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
