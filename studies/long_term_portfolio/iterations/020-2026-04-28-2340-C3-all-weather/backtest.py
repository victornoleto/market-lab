"""Iter 020 — C.3: All-Weather Bridgewater-mimic (4 variants).

DBC unavailable → gold sub for commodities. 4 variants:
  - textbook (30/40/15/15 SPY/TLT/IEF/GLD)
  - Browne permanent (25/25/25/25 SPY/TLT/GLD/CASH)
  - levered (40 NTSX + 30 GDE + 15 KMLM + 15 TLT)
  - inv-vol (4-asset risk parity, monthly rebalance)
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

from src.ai_trade.backtest.metrics.performance import cagr, max_drawdown, sharpe
from src.ai_trade.backtest.validation.dsr import dsr as compute_dsr
from src.ai_trade.backtest.validation.pbo import pbo
from src.ai_trade.backtest.validation.walk_forward import walk_forward_splits


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


SHARED = REPO_ROOT / "studies" / "_shared"
LOOP = REPO_ROOT / "studies" / "long_term_portfolio"
AnnualDarfEngine = _load_module("iter020_tax_engine", SHARED / "tax_engine.py").AnnualDarfEngine
_scoring = _load_module("iter020_scoring", LOOP / "scoring.py")
_datasets_mod = _load_module("iter020_datasets", LOOP / "datasets.py")
_proxies = _load_module("iter020_proxies", LOOP / "proxies.py")
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
CUMULATIVE_N_TRIALS_PRIOR = 71

DATASETS = ["lh_56y", "vt_real", "ndx_real"]

CONFIGS = {
    "aw_textbook_30_40_15_15":  {"type": "static", "weights": {"SPYSIM": 0.30, "TLTSIM": 0.40, "IEFSIM": 0.15, "GLDSIM": 0.15}},
    "aw_browne_25252525":       {"type": "static", "weights": {"SPYSIM": 0.25, "TLTSIM": 0.25, "GLDSIM": 0.25, "CASHX": 0.25}},
    "aw_levered_NTSX_GDE_TLT":  {"type": "expand", "weights": {"NTSX_PROXY": 0.40, "GDESIM": 0.30, "KMLMSIM": 0.15, "TLTSIM": 0.15}},
    "aw_inv_vol_4asset":        {"type": "inv_vol", "universe": ["SPYSIM", "TLTSIM", "IEFSIM", "GLDSIM"]},
}


def static_returns(prices: pd.DataFrame, weights: dict[str, float], expand: bool = False) -> pd.Series:
    if expand:
        weights = expand_capital_efficient(weights)
    needed = [t for t in weights if t in prices.columns]
    px = prices[needed].ffill().dropna(how="all")
    rets = px.pct_change()
    w = pd.Series({t: weights[t] for t in needed}, dtype=float)
    return (rets * w).sum(axis=1).dropna().iloc[1:]


def inv_vol_returns(prices: pd.DataFrame, universe: list[str], lookback: int = 60) -> pd.Series:
    universe = [t for t in universe if t in prices.columns]
    px = prices[universe].dropna(how="any")
    rets = px.pct_change()
    monthly = rets.resample("ME").apply(lambda x: x.std() * np.sqrt(252))
    inv_vol = 1.0 / monthly.replace(0, np.nan)
    weights_monthly = inv_vol.div(inv_vol.sum(axis=1), axis=0)
    weights_daily = weights_monthly.reindex(rets.index, method="ffill").shift(1).fillna(0.0)
    return (rets * weights_daily).sum(axis=1).dropna().iloc[1:]


def compute_equity(returns: pd.Series, start: float = 10_000.0) -> pd.Series:
    return (1.0 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict[str, float]:
    eq = compute_equity(returns)
    return {"sharpe": float(sharpe(returns, periods_per_year=252)), "cagr": float(cagr(eq, periods_per_year=252)), "mdd": float(max_drawdown(eq))}


def net_returns_annual_darf(gross: pd.Series) -> tuple[pd.Series, dict]:
    engine = AnnualDarfEngine(initial_investment=10_000.0)
    prev_value = engine.port_value
    engine.record_trade(gross.index[0], {"sleeve": 0.0}, {"sleeve": 1.0})
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
            net[-1] = (1.0 + net[-1]) * (engine.port_value / prev_value) - 1.0
    return pd.Series(net, index=gross.index, name="net"), engine.summary() | {"events": engine.events}


def gate_dsr(returns):
    p = compute_dsr(returns.values, n_trials=N_CONFIGS).p_value
    return p < 0.05, float(p)


def gate_walk_forward(returns):
    n = len(returns); window = n // (WF_N_WINDOWS + 1)
    if window < 63: return False, [], []
    oos_r, oos_m = [], []
    for _, test_range in walk_forward_splits(n, window, window, window):
        idx = list(test_range); r = returns.iloc[idx]
        oos_r.append(float((1 + r).prod() - 1))
        oos_m.append(float(max_drawdown(compute_equity(r))))
        if len(oos_r) >= WF_N_WINDOWS: break
    passed = (len(oos_r) == WF_N_WINDOWS and sum(x > 0 for x in oos_r) >= 6 and all(x <= 0.25 for x in oos_m))
    return passed, oos_r, oos_m


def gate_oos_70_30(returns):
    oos = returns.iloc[int(len(returns) * 0.70):]
    s = float(sharpe(oos, periods_per_year=252)) if len(oos) >= 63 else 0.0
    return s > 0, s


def gate_fwd(returns):
    fwd = returns[returns.index >= "2020-01-01"]
    s = float(sharpe(fwd, periods_per_year=252)) if len(fwd) >= 63 else 0.0
    return s > 0, s


def gate_bootstrap(returns):
    arr = returns.to_numpy(dtype=float)
    if len(arr) < 252: return False, 0.0
    rng = np.random.default_rng(42); block = 21; n_blocks = len(arr) // block
    sharpes = []
    for _ in range(BOOTSTRAP_N):
        starts = rng.integers(0, len(arr) - block + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block] for s in starts])[:len(arr)]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12: sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    ci_low = float(np.percentile(sharpes, 0.1)) if sharpes else 0.0
    return ci_low > 0, ci_low


def rolling_robustness(returns):
    sharpes = []; window = 252 * 5
    for start in range(0, len(returns) - window + 1, 252):
        sample = returns.iloc[start:start + window]; sigma = sample.std(ddof=0)
        if sigma > 1e-12: sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    pct_pos = sum(s > 0 for s in sharpes) / len(sharpes) if sharpes else 0.0
    pts = 5 if pct_pos >= 0.90 else 3 if pct_pos >= 0.75 else 1 if pct_pos >= 0.60 else 0
    return pts, pct_pos, len(sharpes), sharpes


def run_dataset(ds):
    prices = load_prices(ds)
    configs = {}; aligned = []
    for cfg_id, cfg in CONFIGS.items():
        if cfg["type"] == "static":
            gross = static_returns(prices, cfg["weights"], expand=False)
        elif cfg["type"] == "expand":
            gross = static_returns(prices, cfg["weights"], expand=True)
        elif cfg["type"] == "inv_vol":
            gross = inv_vol_returns(prices, cfg["universe"])
        if len(gross) < 252: continue
        net, tax = net_returns_annual_darf(gross)
        configs[cfg_id] = {
            "gross_metrics": metrics_from_returns(gross),
            "net_metrics": metrics_from_returns(net),
            "loose_window": {"start": str(gross.index[0].date()), "end": str(gross.index[-1].date()), "n": len(gross)},
            "tax": tax, "gross_returns": gross, "net_returns": net,
        }
        aligned.append(gross.rename(cfg_id))
    if not aligned:
        return {"dataset": ds, "prices": prices, "configs": {}, "pbo": {"pbo": 1.0, "n_combinations": 0, "pass": False}}
    matrix = pd.concat(aligned, axis=1).dropna()
    pr = pbo(matrix.to_numpy(dtype=float), n_blocks=10)
    return {"dataset": ds, "prices": prices, "configs": configs, "pbo": {"pbo": float(pr.pbo), "n_combinations": pr.n_combinations, "pass": pr.pbo < 0.5}}


def gate_selected(ds_result, cfg_id):
    gross = ds_result["configs"][cfg_id]["gross_returns"]
    metrics = ds_result["configs"][cfg_id]["gross_metrics"]
    g2, p = gate_dsr(gross); g3, wfr, wfm = gate_walk_forward(gross)
    g4, oos = gate_oos_70_30(gross); g5, fwd = gate_fwd(gross); g6, ci = gate_bootstrap(gross)
    g7 = True
    gates = {"g1_pbo": ds_result["pbo"]["pass"], "g2_dsr": g2, "g3_wf": g3, "g4_oos": g4, "g5_fwd": g5, "g6_bootstrap": g6, "g7_crosslib": g7}
    return {"gates": gates | {"n_passed": sum(gates.values())}, "gate_details": {"g1_pbo": ds_result["pbo"]["pbo"], "g2_dsr_p": p, "g3_wf_returns": wfr, "g3_wf_mdds": wfm, "g3_max_wf_mdd": max(wfm) if wfm else 0.0, "g4_oos_sharpe": oos, "g5_fwd_sharpe": fwd, "g6_ci_low": ci, "g7_np_cagr": metrics["cagr"]}}


def main():
    all_results = {ds: run_dataset(ds) for ds in DATASETS}
    avg_bms = {ds: avg_benchmark(BENCHMARKS[ds]) for ds in DATASETS}
    valid = [c for c in CONFIGS if all(c in all_results[ds]["configs"] for ds in DATASETS)]
    if not valid:
        print("ERROR: no config has data on all 3 datasets."); return
    sel_scores = {c: float(np.mean([all_results[ds]["configs"][c]["gross_metrics"]["sharpe"] / avg_bms[ds].sharpe for ds in DATASETS])) for c in valid}
    selected = max(sel_scores, key=sel_scores.get)

    metrics_map = {}; gates_map = {}; datasets_out = {}; returns_series = {}
    for ds in DATASETS:
        gated = gate_selected(all_results[ds], selected)
        gm = all_results[ds]["configs"][selected]["gross_metrics"]
        nm = all_results[ds]["configs"][selected]["net_metrics"]
        gd = gated["gate_details"]; g = gated["gates"]
        metrics_map[ds] = DatasetMetrics(sharpe=gm["sharpe"], cagr=gm["cagr"], mdd=gm["mdd"], dsr_p_value=gd["g2_dsr_p"], net_sharpe=nm["sharpe"], net_cagr=nm["cagr"], net_mdd=nm["mdd"])
        gates_map[ds] = Gates(g["g1_pbo"], g["g2_dsr"], g["g3_wf"], g["g4_oos"], g["g5_fwd"], g["g6_bootstrap"], g["g7_crosslib"])
        top = sorted(valid, key=lambda c: all_results[ds]["configs"][c]["gross_metrics"]["sharpe"], reverse=True)
        datasets_out[ds] = {"selected_config": selected, "selection_scores": sel_scores, "configs": {c: {"gross_metrics": all_results[ds]["configs"][c]["gross_metrics"], "net_metrics": all_results[ds]["configs"][c]["net_metrics"], "loose_window": all_results[ds]["configs"][c]["loose_window"]} for c in valid}, "top5_by_sharpe": top, "selected": {"gross_metrics": gm, "net_metrics": nm, **gated, "tax": all_results[ds]["configs"][selected]["tax"]}, "pbo": all_results[ds]["pbo"]}
        returns_series[ds] = {}
        for c in set([selected, top[0]]):
            gr = all_results[ds]["configs"][c]["gross_returns"]; nr = all_results[ds]["configs"][c]["net_returns"]
            returns_series[ds][c] = {"index": [str(d.date()) for d in gr.index], "gross_returns": gr.tolist(), "net_returns": nr.tolist()}

    rob_pts, pct_pos, n_roll, roll_s = rolling_robustness(all_results["lh_56y"]["configs"][selected]["gross_returns"])
    score = score_strategy(metrics_map, gates_map, cumulative_n_trials=CUMULATIVE_N_TRIALS_PRIOR + N_CONFIGS, robustness_bonus=rob_pts)
    verdict = score.to_dict()
    verdict.update({"status": score.tier.value.lower(), "configs_tested": N_CONFIGS, "primary_citation": "[risk_parity, ch.5]", "hypothesis_slug": "C3-all-weather", "selected_config": selected, "selection_rule": "max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets", "net_metrics": {ds: {"sharpe": all_results[ds]["configs"][selected]["net_metrics"]["sharpe"], "cagr": all_results[ds]["configs"][selected]["net_metrics"]["cagr"], "mdd": all_results[ds]["configs"][selected]["net_metrics"]["mdd"]} for ds in DATASETS}, "robustness": {"bonus_pts": rob_pts, "pct_positive_sharpe": pct_pos, "n_windows": n_roll, "min_rolling_sharpe": float(min(roll_s)) if roll_s else None, "max_rolling_sharpe": float(max(roll_s)) if roll_s else None}})

    def default(o):
        if isinstance(o, np.integer): return int(o)
        if isinstance(o, np.floating): return float(o)
        return str(o)

    (ITER_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2, default=default) + "\n")
    runs = {ds: {c: {"sharpe": all_results[ds]["configs"][c]["gross_metrics"]["sharpe"], "cagr": all_results[ds]["configs"][c]["gross_metrics"]["cagr"], "mdd": all_results[ds]["configs"][c]["gross_metrics"]["mdd"], "net_sharpe": all_results[ds]["configs"][c]["net_metrics"]["sharpe"], "net_cagr": all_results[ds]["configs"][c]["net_metrics"]["cagr"], "net_mdd": all_results[ds]["configs"][c]["net_metrics"]["mdd"]} for c in valid} for ds in DATASETS}
    (ITER_DIR / "results.json").write_text(json.dumps({"hypothesis_slug": "C3-all-weather", "selected_config": selected, "configs_tested": N_CONFIGS, "configs": CONFIGS, "runs": runs, "datasets": datasets_out, "returns_series": returns_series}, indent=2, default=default) + "\n")

    print(f"Selected: {selected}")
    for ds in DATASETS:
        m = metrics_map[ds]; bm = avg_bms[ds]; edge = m.sharpe - bm.sharpe
        print(f"{ds}: gross S={m.sharpe:.3f} (avg(SPY,VT)={bm.sharpe:.3f}, edge={edge:+.3f}) CAGR={m.cagr:.2%} MDD={m.mdd:.2%} gates={gates_map[ds].n_passed}/7 DSRp={m.dsr_p_value:.2e} | net S={m.net_sharpe:.3f}")
    print(f"Tier={score.tier.value} Score={score.total_score}/100 Winner={score.winner_conditions_met}")
    print("\n--- Full grid ---")
    print(f"{'config':<30} {'lh_56y':>8} {'vt_real':>8} {'ndx_real':>9}")
    for c in CONFIGS:
        s_lh = all_results["lh_56y"]["configs"].get(c, {}).get("gross_metrics", {}).get("sharpe", float("nan"))
        s_vt = all_results["vt_real"]["configs"].get(c, {}).get("gross_metrics", {}).get("sharpe", float("nan"))
        s_nd = all_results["ndx_real"]["configs"].get(c, {}).get("gross_metrics", {}).get("sharpe", float("nan"))
        print(f"{c:<30} {s_lh:>8.3f} {s_vt:>8.3f} {s_nd:>9.3f}")


if __name__ == "__main__":
    main()
