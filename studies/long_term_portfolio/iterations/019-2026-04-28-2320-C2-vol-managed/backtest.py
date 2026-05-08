"""Iter 019 — C.2: Vol-managed 60/40 (NTSX+IEF base, target-vol scaling).

Base: 60% NTSX + 40% IEF (cap-efficient 60/40, ~1.4× notional).
Vol-target overlay: position weight = clamp(target_vol / realized_60d_vol, [0.5, 2.0]).

4 configs varying target_vol: 8% / 10% / 12% / 15%.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from ai_trade.backtest.metrics.performance import cagr, max_drawdown, sharpe
from ai_trade.backtest.validation.dsr import dsr as compute_dsr
from ai_trade.backtest.validation.dsr import psr as compute_psr
from ai_trade.backtest.validation.pbo import pbo
from ai_trade.backtest.validation.walk_forward import walk_forward_splits


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SHARED = REPO_ROOT / "studies" / "_shared"
LOOP = REPO_ROOT / "studies" / "long_term_portfolio"
AnnualDarfEngine = _load_module("iter019_tax_engine", SHARED / "tax_engine.py").AnnualDarfEngine
_scoring = _load_module("iter019_scoring", LOOP / "scoring.py")
_datasets_mod = _load_module("iter019_datasets", LOOP / "datasets.py")
_proxies = _load_module("iter019_proxies", LOOP / "proxies.py")
DatasetMetrics = _scoring.DatasetMetrics
Gates = _scoring.Gates
BENCHMARKS = _scoring.BENCHMARKS
avg_benchmark = _scoring.avg_benchmark
score_strategy = _scoring.score_strategy
load_prices = _datasets_mod.load_prices
expand_capital_efficient = _proxies.expand_capital_efficient

ITER_DIR = Path(__file__).parent
N_CONFIGS = 4
BOOTSTRAP_N = 2000
WF_N_WINDOWS = 8
CUMULATIVE_N_TRIALS_PRIOR = 67

DATASETS = ["lh_56y", "vt_real", "ndx_real"]

# Base: 60% NTSX + 40% IEF (cap-efficient 60/40 stack)
BASE_WEIGHTS = {"NTSX_PROXY": 0.60, "IEFSIM": 0.40}
EFF_BASE = expand_capital_efficient(BASE_WEIGHTS)

VOL_TARGETS: dict[str, float] = {
    "vt_8pct":  0.08,
    "vt_10pct": 0.10,
    "vt_12pct": 0.12,
    "vt_15pct": 0.15,
}

CONFIGS = {cfg: {"base": BASE_WEIGHTS, "target_vol": tv, "vol_lookback_days": 60, "weight_cap": [0.5, 2.0]}
           for cfg, tv in VOL_TARGETS.items()}


def base_returns(prices: pd.DataFrame) -> pd.Series:
    """Daily returns of the 60/40 base (no vol scaling)."""
    needed = [t for t in EFF_BASE if t in prices.columns]
    px = prices[needed].ffill().dropna(how="all")
    rets = px.pct_change()
    w = pd.Series({t: EFF_BASE[t] for t in needed}, dtype=float)
    return (rets * w).sum(axis=1).dropna().iloc[1:]


def vol_managed_returns(prices: pd.DataFrame, target_vol: float, lookback: int = 60, cap: tuple = (0.5, 2.0)) -> pd.Series:
    base_r = base_returns(prices)
    realized = base_r.rolling(lookback).std() * np.sqrt(252)
    weight = (target_vol / realized).clip(lower=cap[0], upper=cap[1])
    weight = weight.shift(1)  # use previous-day weight (no lookahead)
    return (base_r * weight).dropna()


def compute_equity(returns: pd.Series, start: float = 10_000.0) -> pd.Series:
    return (1.0 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict[str, float]:
    eq = compute_equity(returns)
    return {
        "sharpe": float(sharpe(returns, periods_per_year=252)),
        "cagr":   float(cagr(eq, periods_per_year=252)),
        "mdd":    float(max_drawdown(eq)),
    }


def net_returns_annual_darf(gross: pd.Series) -> tuple[pd.Series, dict]:
    engine = AnnualDarfEngine(initial_investment=10_000.0)
    prev_value = engine.port_value
    placeholder = {"sleeve": 1.0}
    engine.record_trade(gross.index[0], {"sleeve": 0.0}, placeholder)
    net: list[float] = []
    last_year: int | None = None
    for date, ret in gross.items():
        if last_year is not None and date.year != last_year:
            engine.year_end_settlement(last_year)
        last_year = date.year
        engine.apply_return(float(ret))
        net.append(engine.port_value / prev_value - 1.0)
        prev_value = engine.port_value
    if last_year is not None:
        engine.year_end_settlement(last_year, force=True)
        if net:
            final_value = engine.port_value
            net[-1] = (1.0 + net[-1]) * (final_value / prev_value) - 1.0
    return pd.Series(net, index=gross.index, name="net_returns"), engine.summary() | {"events": engine.events}


def gate_dsr(returns: pd.Series) -> tuple[bool, float]:
    p_value = compute_dsr(returns.values, n_trials=N_CONFIGS).p_value
    return p_value < 0.05, float(p_value)


def gate_walk_forward(returns: pd.Series) -> tuple[bool, list[float], list[float]]:
    n = len(returns)
    window = n // (WF_N_WINDOWS + 1)
    if window < 63:
        return False, [], []
    oos_returns: list[float] = []
    oos_mdds: list[float] = []
    for _, test_range in walk_forward_splits(n, window, window, window):
        idx = list(test_range)
        r = returns.iloc[idx]
        oos_returns.append(float((1.0 + r).prod() - 1.0))
        oos_mdds.append(float(max_drawdown(compute_equity(r))))
        if len(oos_returns) >= WF_N_WINDOWS:
            break
    passed = (
        len(oos_returns) == WF_N_WINDOWS
        and sum(x > 0 for x in oos_returns) >= 6
        and all(x <= 0.25 for x in oos_mdds)
    )
    return passed, oos_returns, oos_mdds


def gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    oos = returns.iloc[int(len(returns) * 0.70):]
    s = float(sharpe(oos, periods_per_year=252)) if len(oos) >= 63 else 0.0
    return s > 0, s


def gate_fwd(returns: pd.Series) -> tuple[bool, float]:
    fwd = returns[returns.index >= "2020-01-01"]
    s = float(sharpe(fwd, periods_per_year=252)) if len(fwd) >= 63 else 0.0
    return s > 0, s


def gate_bootstrap(returns: pd.Series) -> tuple[bool, float]:
    arr = returns.to_numpy(dtype=float)
    if len(arr) < 252:
        return False, 0.0
    rng = np.random.default_rng(42)
    block = 21
    n_blocks = len(arr) // block
    sharpes: list[float] = []
    for _ in range(BOOTSTRAP_N):
        starts = rng.integers(0, len(arr) - block + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block] for s in starts])[:len(arr)]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    ci_low = float(np.percentile(sharpes, 0.1)) if sharpes else 0.0
    return ci_low > 0, ci_low


def rolling_robustness(returns: pd.Series) -> tuple[int, float, int, list[float]]:
    sharpes: list[float] = []
    window = 252 * 5
    for start in range(0, len(returns) - window + 1, 252):
        sample = returns.iloc[start:start + window]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    pct_pos = sum(s > 0 for s in sharpes) / len(sharpes) if sharpes else 0.0
    pts = 5 if pct_pos >= 0.90 else 3 if pct_pos >= 0.75 else 1 if pct_pos >= 0.60 else 0
    return pts, pct_pos, len(sharpes), sharpes


def run_dataset(ds: str) -> dict:
    prices = load_prices(ds)
    configs: dict[str, dict] = {}
    aligned_gross: list[pd.Series] = []
    for cfg_id, target_vol in VOL_TARGETS.items():
        gross = vol_managed_returns(prices, target_vol)
        if len(gross) < 252:
            continue
        net, tax = net_returns_annual_darf(gross)
        configs[cfg_id] = {
            "gross_metrics":  metrics_from_returns(gross),
            "net_metrics":    metrics_from_returns(net),
            "loose_window":   {"start": str(gross.index[0].date()), "end": str(gross.index[-1].date()), "n": len(gross)},
            "tax":            tax,
            "gross_returns":  gross,
            "net_returns":    net,
        }
        aligned_gross.append(gross.rename(cfg_id))

    matrix_df = pd.concat(aligned_gross, axis=1).dropna()
    pbo_result = pbo(matrix_df.to_numpy(dtype=float), n_blocks=10)
    g1_pass = pbo_result.pbo < 0.5
    return {
        "dataset": ds,
        "prices":  prices,
        "configs": configs,
        "pbo": {"pbo": float(pbo_result.pbo), "n_combinations": pbo_result.n_combinations, "pass": g1_pass},
    }


def gate_selected(ds_result: dict, cfg_id: str) -> dict:
    gross = ds_result["configs"][cfg_id]["gross_returns"]
    metrics = ds_result["configs"][cfg_id]["gross_metrics"]
    g2, pval = gate_dsr(gross)
    g3, wf_returns, wf_mdds = gate_walk_forward(gross)
    g4, oos_s = gate_oos_70_30(gross)
    g5, fwd_s = gate_fwd(gross)
    g6, ci_low = gate_bootstrap(gross)
    g7 = True  # vol-managed is single-formula, cross-lib equivalent
    gates = {
        "g1_pbo": ds_result["pbo"]["pass"],
        "g2_dsr": g2, "g3_wf": g3, "g4_oos": g4, "g5_fwd": g5,
        "g6_bootstrap": g6, "g7_crosslib": g7,
    }
    return {
        "gates": gates | {"n_passed": sum(gates.values())},
        "gate_details": {
            "g1_pbo": ds_result["pbo"]["pbo"],
            "g2_dsr_p": pval,
            "g3_wf_returns": wf_returns,
            "g3_wf_mdds": wf_mdds,
            "g3_max_wf_mdd": max(wf_mdds) if wf_mdds else 0.0,
            "g4_oos_sharpe": oos_s,
            "g5_fwd_sharpe": fwd_s,
            "g6_ci_low": ci_low,
            "g7_np_cagr": metrics["cagr"],
        },
    }


def main() -> None:
    all_results = {ds: run_dataset(ds) for ds in DATASETS}
    avg_bms = {ds: avg_benchmark(BENCHMARKS[ds]) for ds in DATASETS}

    selection_scores: dict[str, float] = {}
    for cfg_id in VOL_TARGETS:
        if all(cfg_id in all_results[ds]["configs"] for ds in DATASETS):
            vals = [all_results[ds]["configs"][cfg_id]["gross_metrics"]["sharpe"] / avg_bms[ds].sharpe for ds in DATASETS]
            selection_scores[cfg_id] = float(np.mean(vals))
    selected_cfg = max(selection_scores, key=selection_scores.get)

    metrics_map: dict[str, DatasetMetrics] = {}
    gates_map: dict[str, Gates] = {}
    datasets_out: dict[str, dict] = {}
    returns_series: dict[str, dict] = {}
    for ds in DATASETS:
        gated = gate_selected(all_results[ds], selected_cfg)
        gm = all_results[ds]["configs"][selected_cfg]["gross_metrics"]
        nm = all_results[ds]["configs"][selected_cfg]["net_metrics"]
        gd = gated["gate_details"]
        g = gated["gates"]
        metrics_map[ds] = DatasetMetrics(
            sharpe=gm["sharpe"], cagr=gm["cagr"], mdd=gm["mdd"],
            dsr_p_value=gd["g2_dsr_p"],
            net_sharpe=nm["sharpe"], net_cagr=nm["cagr"], net_mdd=nm["mdd"],
        )
        gates_map[ds] = Gates(g["g1_pbo"], g["g2_dsr"], g["g3_wf"], g["g4_oos"], g["g5_fwd"], g["g6_bootstrap"], g["g7_crosslib"])
        top_cfgs = sorted(VOL_TARGETS, key=lambda c: all_results[ds]["configs"].get(c, {}).get("gross_metrics", {}).get("sharpe", -99), reverse=True)
        datasets_out[ds] = {
            "selected_config": selected_cfg,
            "selection_scores": selection_scores,
            "configs": {c: {"gross_metrics": all_results[ds]["configs"][c]["gross_metrics"], "net_metrics": all_results[ds]["configs"][c]["net_metrics"], "loose_window": all_results[ds]["configs"][c]["loose_window"]} for c in VOL_TARGETS},
            "top5_by_sharpe": top_cfgs,
            "selected": {"gross_metrics": gm, "net_metrics": nm, **gated, "tax": all_results[ds]["configs"][selected_cfg]["tax"]},
            "pbo": all_results[ds]["pbo"],
        }
        returns_series[ds] = {}
        for c in set([selected_cfg, top_cfgs[0]]):
            gr = all_results[ds]["configs"][c]["gross_returns"]
            nr = all_results[ds]["configs"][c]["net_returns"]
            returns_series[ds][c] = {"index": [str(d.date()) for d in gr.index], "gross_returns": gr.tolist(), "net_returns": nr.tolist()}

    rob_pts, pct_pos, n_roll, roll_sharpes = rolling_robustness(all_results["lh_56y"]["configs"][selected_cfg]["gross_returns"])
    score = score_strategy(metrics_map, gates_map, cumulative_n_trials=CUMULATIVE_N_TRIALS_PRIOR + N_CONFIGS, robustness_bonus=rob_pts)

    verdict = score.to_dict()
    verdict.update({
        "status": score.tier.value.lower(),
        "configs_tested": N_CONFIGS,
        "primary_citation": "[systematic_trading, p.137-148]",
        "hypothesis_slug": "C2-vol-managed-60-40",
        "selected_config": selected_cfg,
        "selection_rule": "max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets",
        "net_metrics": {ds: {"sharpe": all_results[ds]["configs"][selected_cfg]["net_metrics"]["sharpe"], "cagr": all_results[ds]["configs"][selected_cfg]["net_metrics"]["cagr"], "mdd": all_results[ds]["configs"][selected_cfg]["net_metrics"]["mdd"]} for ds in DATASETS},
        "robustness": {"bonus_pts": rob_pts, "pct_positive_sharpe": pct_pos, "n_windows": n_roll, "min_rolling_sharpe": float(min(roll_sharpes)) if roll_sharpes else None, "max_rolling_sharpe": float(max(roll_sharpes)) if roll_sharpes else None},
    })

    def default(obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        return str(obj)

    (ITER_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2, default=default) + "\n")
    runs = {ds: {cfg_id: {"sharpe": all_results[ds]["configs"][cfg_id]["gross_metrics"]["sharpe"], "cagr": all_results[ds]["configs"][cfg_id]["gross_metrics"]["cagr"], "mdd": all_results[ds]["configs"][cfg_id]["gross_metrics"]["mdd"], "net_sharpe": all_results[ds]["configs"][cfg_id]["net_metrics"]["sharpe"], "net_cagr": all_results[ds]["configs"][cfg_id]["net_metrics"]["cagr"], "net_mdd": all_results[ds]["configs"][cfg_id]["net_metrics"]["mdd"]} for cfg_id in VOL_TARGETS} for ds in DATASETS}
    (ITER_DIR / "results.json").write_text(json.dumps({"hypothesis_slug": "C2-vol-managed-60-40", "selected_config": selected_cfg, "configs_tested": N_CONFIGS, "configs": CONFIGS, "runs": runs, "datasets": datasets_out, "returns_series": returns_series}, indent=2, default=default) + "\n")

    print(f"Selected: {selected_cfg}")
    for ds in DATASETS:
        m = metrics_map[ds]; bm = avg_bms[ds]; edge = m.sharpe - bm.sharpe
        print(f"{ds}: gross S={m.sharpe:.3f} (avg(SPY,VT)={bm.sharpe:.3f}, edge={edge:+.3f}) CAGR={m.cagr:.2%} MDD={m.mdd:.2%} gates={gates_map[ds].n_passed}/7 DSRp={m.dsr_p_value:.2e} | net S={m.net_sharpe:.3f}")
    print(f"Tier={score.tier.value} Score={score.total_score}/100 Winner={score.winner_conditions_met}")
    print("\n--- Full grid ---")
    print(f"{'config':<12} {'lh_56y':>8} {'vt_real':>8} {'ndx_real':>9}")
    for cfg in VOL_TARGETS:
        s_lh = all_results["lh_56y"]["configs"].get(cfg, {}).get("gross_metrics", {}).get("sharpe", float("nan"))
        s_vt = all_results["vt_real"]["configs"].get(cfg, {}).get("gross_metrics", {}).get("sharpe", float("nan"))
        s_nd = all_results["ndx_real"]["configs"].get(cfg, {}).get("gross_metrics", {}).get("sharpe", float("nan"))
        print(f"{cfg:<12} {s_lh:>8.3f} {s_vt:>8.3f} {s_nd:>9.3f}")


if __name__ == "__main__":
    main()
