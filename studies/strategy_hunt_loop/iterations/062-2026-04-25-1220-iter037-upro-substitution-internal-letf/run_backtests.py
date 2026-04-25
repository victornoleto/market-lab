"""Iter 062 — internal-LETF UPRO substitution preserving equity exposure.

Single pre-committed cfg ``iter037_upro_internal_letf_020_065_065``.

NO grid sweep, NO post-hoc selection. Single 3-leg stack at preserved
1.50× total NAV with UPRO/TQQQ replacing the cash equity leg in iter
037's framework, and bond/gold doubled-down from 0.45 each to 0.65
each (using the NAV freed by 0.40 less equity weight).

Datasets:

- educational (2004-11-19 → 2026-04-15): joined UPRO = synth UPRO
  pre-2009-06-25 + real UPRO from 2009-06-25 onward.
- spy_real (2009-06-25 → 2026-04-15): real UPRO only.
- ndx_real (2010-02-12 → 2026-04-15): real TQQQ only (replaces QQQ).

Cumulative n_trials advance: 4331 → 4332 (+1).

Citations
---------
* `[leverage_for_the_long_run, p.19-25]` — Hsiao-Williams 2017 daily-reset LETF.
* `[risk_parity, ch.5]` — multi-leg risk-parity preserved-NAV stack.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity discipline.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
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

from synth_letf_3leg import (  # noqa: E402
    apply_static_stack_3leg,
    join_real_and_synth_letf,
    synth_upro_returns,
)
from numpy_reference_iter062 import (  # noqa: E402
    apply_static_stack_3leg_np,
    synth_upro_returns_np,
)

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
    "cfg_id": "iter037_upro_internal_letf_020_065_065",
    "letf_w": 0.20,        # 0.20 UPRO ≈ 0.60 SPY-equiv equity exposure
    "bd_short_w": 0.65,    # IEF (vs iter 037's 0.45)
    "bd_long_w": 0.65,     # GLD (vs iter 037's 0.45)
    "total_lev": 1.50,     # 0.20 + 0.65 + 0.65 (matches iter 037)
    "letf_leverage": 3.0,  # UPRO / TQQQ daily-reset multiplier
    "expense_ratio": 0.0091,  # ProShares UPRO 2024-25 prospectus
    "cost_bps_per_leg": 0.0002,  # 2 bps per-leg ∆position (matches iter 037)
    "rebalance": "daily 0.20 LETF + 0.65 IEF + 0.65 GLD",
    "primary_citation": (
        "[leverage_for_the_long_run, p.19-25] (Hsiao-Williams daily-reset LETF) + "
        "[risk_parity, ch.5] (preserved-NAV multi-leg stack) + "
        "[advances_fin_ml, p.222-223] (DSR cumulative)"
    ),
}

DATASETS: dict[str, dict] = {
    "educational": {
        "spy_symbol": "SPY",                 # base for synth UPRO pre-2009
        "letf_symbol": "UPRO",               # real LETF 2009-06-25 onward
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "SPY",
        "start": "2004-11-19",
        "end": "2026-04-15",
        "letf_inception": "2009-06-25",
        "synth_pre_inception": True,
        "letf_kind": "3x_spy",
        "role": (
            "21y joined UPRO (synth pre-2009 + real post) + IEF + GLD; "
            "matches iter 037 educational window"
        ),
    },
    "spy_real": {
        "spy_symbol": "SPY",
        "letf_symbol": "UPRO",
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "SPY",
        "start": "2009-06-25",
        "end": "2026-04-15",
        "letf_inception": "2009-06-25",
        "synth_pre_inception": False,
        "letf_kind": "3x_spy",
        "role": "17y real UPRO + IEF + GLD post-GFC",
    },
    "ndx_real": {
        "spy_symbol": "QQQ",                 # base for synth TQQQ pre-2010
        "letf_symbol": "TQQQ",               # real LETF 2010-02-11 onward
        "bond_symbol": "IEF",
        "gold_symbol": "GLD",
        "bench_ticker": "QQQ",
        "start": "2010-02-12",
        "end": "2026-04-15",
        "letf_inception": "2010-02-11",
        "synth_pre_inception": False,        # window starts after inception
        "letf_kind": "3x_qqq",
        "role": "16y real TQQQ + IEF + GLD tech-heavy",
    },
}


def load_prices(symbol: str, start: str, end: str) -> pd.Series:
    df = pd.read_parquet(TIINGO_DIR / f"{symbol}.parquet")
    m = (df.index >= start) & (df.index <= end)
    return df.loc[m, "adj_close"].astype(float)


def load_letf_substituted_triple(ds: dict) -> tuple[pd.DataFrame, dict]:
    """Build the (LETF, IEF, GLD) daily-return triple for a dataset.

    For educational: real LETF data from inception forward, synth LETF
    from SPY pre-inception, joined into a single series spanning
    [start, end].

    For spy_real / ndx_real: real LETF only (window starts at/after
    real LETF inception).

    Returns (triple_df, meta) where meta has window stats for logging.
    """
    spy_sym = ds["spy_symbol"]
    letf_sym = ds["letf_symbol"]
    bd_sym = ds["bond_symbol"]
    gld_sym = ds["gold_symbol"]
    start, end = ds["start"], ds["end"]

    # Bond + gold returns
    bd_p = load_prices(bd_sym, start, end)
    gld_p = load_prices(gld_sym, start, end)

    # Real LETF returns: load from its inception or window-start, whichever later
    letf_p = load_prices(letf_sym, start, end)
    r_letf_real = letf_p.pct_change().dropna()

    # Compute base equity returns (for synth-pre-inception path)
    spy_p = load_prices(spy_sym, start, end)
    r_spy = spy_p.pct_change().dropna()

    if ds["synth_pre_inception"]:
        r_letf = join_real_and_synth_letf(
            r_spy, r_letf_real,
            leverage=CFG["letf_leverage"],
            expense_ratio=CFG["expense_ratio"],
        )
        n_synth = int(len(r_letf.loc[r_letf.index < r_letf_real.index[0]]))
        n_real = int(len(r_letf.loc[r_letf.index >= r_letf_real.index[0]]))
    else:
        # Window starts on/after real LETF inception → use real LETF only.
        r_letf = r_letf_real.copy()
        r_letf.name = "joined_LETF"
        n_synth = 0
        n_real = int(len(r_letf))

    r_bd = bd_p.pct_change().dropna()
    r_gld = gld_p.pct_change().dropna()

    # Inner-join all three on common dates
    df = pd.concat({
        letf_sym: r_letf,
        bd_sym: r_bd,
        gld_sym: r_gld,
    }, axis=1, join="inner").dropna()

    meta = {
        "letf_first": str(df.index[0].date()),
        "letf_last": str(df.index[-1].date()),
        "n_bars_total": int(len(df)),
        "n_bars_synth_letf": n_synth,
        "n_bars_real_letf": n_real,
        "letf_inception_real": ds["letf_inception"],
        "letf_kind": ds["letf_kind"],
    }
    return df, meta


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


def run_single_cfg(triple: pd.DataFrame) -> tuple[dict, pd.Series, pd.Series]:
    letf_col, bd_col, gld_col = triple.columns
    net, positions, scale = apply_static_stack_3leg(
        triple[letf_col],
        triple[bd_col],
        triple[gld_col],
        eq_w=CFG["letf_w"],
        bd_short_w=CFG["bd_short_w"],
        bd_long_w=CFG["bd_long_w"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
    )
    eq_curve = (1.0 + net).cumprod()
    cap_target = CFG["letf_w"] + CFG["bd_short_w"] + CFG["bd_long_w"]
    cap_hit = float(np.isclose(scale.to_numpy(float), cap_target, atol=1e-12).mean())

    turnover_per_leg: dict[str, float] = {}
    for c in positions.columns:
        dpos = positions[c].diff().abs().fillna(positions[c].iloc[0])
        turnover_per_leg[c] = float(dpos.sum() * 252.0 / len(dpos))
    turnover_total = float(sum(turnover_per_leg.values()))

    # Per-leg standalone metrics
    leg_metrics: dict[str, dict] = {}
    for col, w in [(letf_col, CFG["letf_w"]),
                   (bd_col, CFG["bd_short_w"]),
                   (gld_col, CFG["bd_long_w"])]:
        r = triple[col]
        eq_leg = (1.0 + r).cumprod()
        leg_metrics[col] = {
            "weight": w,
            "sharpe": float(_sharpe(r)),
            "cagr": float(_cagr(eq_leg)),
            "mdd": float(_max_drawdown(eq_leg)),
        }

    m = {
        "cfg_id": CFG["cfg_id"],
        "letf_w": CFG["letf_w"],
        "bd_short_w": CFG["bd_short_w"],
        "bd_long_w": CFG["bd_long_w"],
        "total_lev": cap_target,
        "bars": int(len(net)),
        "sharpe": float(_sharpe(net)),
        "cagr": float(_cagr(eq_curve)),
        "mdd": float(_max_drawdown(eq_curve)),
        "final_equity": float(eq_curve.iloc[-1]),
        "scale_mean": float(scale.mean()),
        "scale_cap_hit_frac": cap_hit,
        "turnover_annual_per_leg": turnover_per_leg,
        "turnover_annual_total": turnover_total,
        "leg_metrics": leg_metrics,
    }
    return m, net, scale


def cross_lib_check(triple: pd.DataFrame) -> dict:
    """G7 parity for the 3-leg static stack: pandas vs numpy reference."""
    letf_col, bd_col, gld_col = triple.columns
    pd_net, _, _ = apply_static_stack_3leg(
        triple[letf_col], triple[bd_col], triple[gld_col],
        eq_w=CFG["letf_w"], bd_short_w=CFG["bd_short_w"],
        bd_long_w=CFG["bd_long_w"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
    )
    np_net = apply_static_stack_3leg_np(
        triple[letf_col].values, triple[bd_col].values, triple[gld_col].values,
        eq_w=CFG["letf_w"], bd_short_w=CFG["bd_short_w"],
        bd_long_w=CFG["bd_long_w"],
        cost_bps_per_leg=CFG["cost_bps_per_leg"],
    )
    n = min(len(pd_net), len(np_net))
    pd_arr = pd_net.values[-n:]
    np_arr = np_net[-n:]
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


def synth_letf_parity_check(spy_returns: pd.Series) -> dict:
    """G7 parity for synth-UPRO formula: pandas vs numpy."""
    pd_synth = synth_upro_returns(
        spy_returns,
        leverage=CFG["letf_leverage"],
        expense_ratio=CFG["expense_ratio"],
    )
    np_synth = synth_upro_returns_np(
        spy_returns.values,
        leverage=CFG["letf_leverage"],
        expense_ratio=CFG["expense_ratio"],
    )
    n = len(pd_synth)
    eq_pd = np.cumprod(1.0 + pd_synth.values)
    eq_np = np.cumprod(1.0 + np_synth)
    cagr_pd = float(eq_pd[-1]) ** (252.0 / n) - 1.0
    cagr_np_val = float(eq_np[-1]) ** (252.0 / n) - 1.0
    return {
        "cagr_pandas": cagr_pd,
        "cagr_numpy": cagr_np_val,
        "abs_diff_pp": abs(cagr_pd - cagr_np_val) * 100.0,
        "max_abs_return_diff": float(np.max(np.abs(pd_synth.values - np_synth))),
        "n_bars_compared": n,
    }


def main() -> None:
    all_results: dict = {
        "datasets": DATASETS,
        "configs": [CFG],
        "benchmarks": {},
        "runs": {},
        "returns_series": {},
        "leg_correlations": {},
        "leg_metrics_per_dataset": {},
        "crosslib_3leg": {},
        "crosslib_synth_letf": {},
        "letf_meta": {},
        "pre_committed": True,
        "iter_label": "062-2026-04-25-1220-iter037-upro-substitution-internal-letf",
    }

    for ds_name, ds in DATASETS.items():
        triple, meta = load_letf_substituted_triple(ds)
        all_results["letf_meta"][ds_name] = meta

        # Benchmark = SPY/QQQ buy & hold on the SAME window as the cfg run
        bench_p = load_prices(ds["bench_ticker"], ds["start"], ds["end"])
        bench_series = bench_p.pct_change().dropna()
        bench_aligned = bench_series.loc[bench_series.index.isin(triple.index)]
        bench = benchmark_metrics(bench_aligned)
        all_results["benchmarks"][ds_name] = bench

        corr_mat = triple.corr()
        letf_col, bd_col, gld_col = triple.columns
        all_results["leg_correlations"][ds_name] = {
            "letf_bd": float(corr_mat.loc[letf_col, bd_col]),
            "letf_gld": float(corr_mat.loc[letf_col, gld_col]),
            "bd_gld": float(corr_mat.loc[bd_col, gld_col]),
        }
        print(
            f"[{ds_name}] {letf_col}+{bd_col}+{gld_col} "
            f"{meta['letf_first']}→{meta['letf_last']} "
            f"({meta['n_bars_total']} bars; synth/real LETF = "
            f"{meta['n_bars_synth_letf']}/{meta['n_bars_real_letf']}); "
            f"bench={ds['bench_ticker']} S={bench['sharpe']:.3f} "
            f"CAGR={bench['cagr']:.2%} MDD={bench['mdd']:.2%}"
        )
        print(
            f"  ρ(letf,bd)={all_results['leg_correlations'][ds_name]['letf_bd']:+.3f} "
            f"ρ(letf,gld)={all_results['leg_correlations'][ds_name]['letf_gld']:+.3f} "
            f"ρ(bd,gld)={all_results['leg_correlations'][ds_name]['bd_gld']:+.3f}"
        )

        print(f"\n=== {ds_name} — cfg {CFG['cfg_id']} ===")
        m, net, scale = run_single_cfg(triple)
        all_results["runs"][ds_name] = {CFG["cfg_id"]: m}
        all_results["leg_metrics_per_dataset"][ds_name] = m["leg_metrics"]
        all_results["returns_series"][ds_name] = {
            CFG["cfg_id"]: {
                "index": [str(t.date()) for t in net.index],
                "net_returns": [round(float(x), 10) for x in net.tolist()],
            }
        }

        edge_frozen = m["sharpe"] - {
            "educational": 0.68, "spy_real": 0.90, "ndx_real": 0.955,
        }[ds_name]
        edge_window = m["sharpe"] - bench["sharpe"]
        print(
            f"  combined Sharpe={m['sharpe']:+.4f} "
            f"(Δ frozen={edge_frozen:+.4f}, Δ window={edge_window:+.4f}) "
            f"CAGR={m['cagr']:+.2%} MDD={m['mdd']:.2%} "
            f"total_lev={m['total_lev']:.2f}"
        )
        for col, lm in m["leg_metrics"].items():
            print(
                f"    leg {col} w={lm['weight']:.2f}  S={lm['sharpe']:+.4f} "
                f"CAGR={lm['cagr']:+.2%} MDD={lm['mdd']:.2%}"
            )

        cl_3leg = cross_lib_check(triple)
        all_results["crosslib_3leg"][ds_name] = cl_3leg
        print(
            f"    G7 (3-leg): CAGR pd={cl_3leg['cagr_pandas']:+.4%} "
            f"np={cl_3leg['cagr_numpy']:+.4%} Δ={cl_3leg['abs_diff_pp']:.6f} pp"
        )

        if ds["synth_pre_inception"]:
            spy_p = load_prices(ds["spy_symbol"], ds["start"], ds["end"])
            r_spy = spy_p.pct_change().dropna()
            cl_synth = synth_letf_parity_check(r_spy)
            all_results["crosslib_synth_letf"][ds_name] = cl_synth
            print(
                f"    G7 (synth-LETF): CAGR pd={cl_synth['cagr_pandas']:+.4%} "
                f"np={cl_synth['cagr_numpy']:+.4%} "
                f"Δ={cl_synth['abs_diff_pp']:.6f} pp"
            )

    out_path = ITER_DIR / "results.json"
    out_path.write_text(
        json.dumps(all_results, indent=2, default=str), encoding="utf-8",
    )
    print(f"\nWrote {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
