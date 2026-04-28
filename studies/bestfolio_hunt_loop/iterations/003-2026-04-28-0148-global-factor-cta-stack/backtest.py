"""Iter 003 Global Factor + CTA Stack.

Static capital-efficient portfolios with global/factor/CTA sleeves.

Citations:
- Risk-budget diversification and capital efficiency: [risk_parity, p.1-2, p.10]
- PBO/DSR/bootstrap/cross-lib gates:
  [advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]
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

from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_frame
from src.ai_trade.backtest.metrics.performance import cagr, max_drawdown, sharpe
from src.ai_trade.backtest.validation.dsr import dsr as compute_dsr
from src.ai_trade.backtest.validation.dsr import psr as compute_psr
from src.ai_trade.backtest.validation.pbo import pbo
from src.ai_trade.backtest.validation.walk_forward import walk_forward_splits


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GLOBAL_LOOP = REPO_ROOT / "studies" / "global_factor_tilt_loop"
BESTFOLIO_LOOP = REPO_ROOT / "studies" / "bestfolio_hunt_loop"
AnnualDarfEngine = _load_module("iter003_tax_engine_v2", GLOBAL_LOOP / "tax_engine_v2.py").AnnualDarfEngine
_scoring = _load_module("iter003_bestfolio_scoring", BESTFOLIO_LOOP / "scoring.py")
DatasetMetrics = _scoring.DatasetMetrics
Gates = _scoring.Gates
BENCHMARKS = _scoring.BENCHMARKS
score_strategy = _scoring.score_strategy

ITER_DIR = Path(__file__).parent
N_CONFIGS = 6
BOOTSTRAP_N = 2000
WF_N_WINDOWS = 8

DATASETS = {
    "educational": {"start": "1995-01-01", "end": "2026-04-24", "benchmark": "VTSIM"},
    "vt_real": {"start": "2008-06-01", "end": "2026-04-24", "benchmark": "VTSIM"},
    "ndx_real": {"start": "2010-02-01", "end": "2026-04-24", "benchmark": "QQQSIM"},
}

# Weight sleeves sum to 1.0 before expansion. RSSB/GDE are already stacked
# synths; RSST proxy expands to SPYSIM + KMLMSIM - CASHX.
CONFIGS: dict[str, dict[str, float]] = {
    "stack_balanced": {
        "RSSBSIM": 0.30, "GDESIM": 0.20, "KMLMSIM": 0.15, "VBRSIM": 0.12,
        "VSSSIM": 0.08, "VWOSIM": 0.05, "SPYSIM": 0.10,
    },
    "stack_cta_heavy": {
        "RSSBSIM": 0.25, "GDESIM": 0.18, "KMLMSIM": 0.22, "VBRSIM": 0.10,
        "VSSSIM": 0.08, "VWOSIM": 0.07, "SPYSIM": 0.10,
    },
    "stack_factor_heavy": {
        "RSSBSIM": 0.25, "GDESIM": 0.17, "KMLMSIM": 0.12, "VBRSIM": 0.18,
        "VSSSIM": 0.13, "VWOSIM": 0.07, "SPYSIM": 0.08,
    },
    "stack_gde_heavy": {
        "RSSBSIM": 0.25, "GDESIM": 0.30, "KMLMSIM": 0.15, "VBRSIM": 0.10,
        "VSSSIM": 0.06, "VWOSIM": 0.04, "SPYSIM": 0.10,
    },
    "stack_rssb_core": {
        "RSSBSIM": 0.40, "GDESIM": 0.18, "KMLMSIM": 0.15, "VBRSIM": 0.10,
        "VSSSIM": 0.07, "VWOSIM": 0.05, "SPYSIM": 0.05,
    },
    "stack_rsst_overlay": {
        "RSSBSIM": 0.25, "GDESIM": 0.18, "KMLMSIM": 0.10, "VBRSIM": 0.10,
        "VSSSIM": 0.07, "VWOSIM": 0.05, "SPYSIM": 0.05, "RSST_PROXY": 0.20,
    },
}


def expand_weights(weights: dict[str, float]) -> dict[str, float]:
    """Expand return-stacked proxies into testfolio legs. [risk_parity, p.10]"""
    out: dict[str, float] = {}
    for ticker, weight in weights.items():
        if ticker == "RSST_PROXY":
            out["SPYSIM"] = out.get("SPYSIM", 0.0) + weight
            out["KMLMSIM"] = out.get("KMLMSIM", 0.0) + weight
            out["CASHX"] = out.get("CASHX", 0.0) - weight
        else:
            out[ticker] = out.get(ticker, 0.0) + weight
    return out


EFF_CONFIGS = {cfg: expand_weights(weights) for cfg, weights in CONFIGS.items()}


def compute_equity(returns: pd.Series, start: float = 10_000.0) -> pd.Series:
    return (1.0 + returns).cumprod() * start


def gross_returns(prices: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    tickers = [t for t in weights if t in prices.columns]
    px = prices[tickers].ffill().dropna(how="all")
    rets = px.pct_change()
    w = pd.Series({t: weights[t] for t in tickers}, dtype=float)
    return (rets * w).sum(axis=1).dropna().iloc[1:]


def net_returns_annual_darf(gross: pd.Series, weights: dict[str, float]) -> tuple[pd.Series, dict]:
    """Apply AnnualDarfEngine to static returns.

    Static weights have no tactical sell trigger. We still route the path
    through AnnualDarfEngine so the legal annual settlement model remains the
    only tax engine in use.
    """
    engine = AnnualDarfEngine(initial_investment=10_000.0)
    prev_value = engine.port_value
    prev_weights = {k: 0.0 for k in weights}
    curr_weights = dict(weights)
    net: list[float] = []
    last_year: int | None = None

    for i, (date, ret) in enumerate(gross.items()):
        if i == 0:
            engine.record_trade(date, prev_weights, curr_weights)
            prev_weights = curr_weights
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


def metrics_from_returns(returns: pd.Series) -> dict[str, float]:
    eq = compute_equity(returns)
    return {
        "sharpe": float(sharpe(returns, periods_per_year=252)),
        "cagr": float(cagr(eq, periods_per_year=252)),
        "mdd": float(max_drawdown(eq)),
    }


def numpy_returns(prices: pd.DataFrame, weights: dict[str, float]) -> np.ndarray:
    tickers = [t for t in weights if t in prices.columns]
    px = prices[tickers].ffill().dropna(how="all").to_numpy(dtype=float)
    w = np.array([weights[t] for t in tickers], dtype=float)
    daily = np.diff(px, axis=0) / px[:-1]
    return (daily * w).sum(axis=1)[1:]


def gate_dsr(returns: pd.Series) -> tuple[bool, float]:
    if N_CONFIGS < 2:
        p_value = 1.0 - compute_psr(returns.values, benchmark=0.0)
    else:
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
    passed = len(oos_returns) == WF_N_WINDOWS and sum(x > 0 for x in oos_returns) >= 6 and all(x <= 0.25 for x in oos_mdds)
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


def run_dataset(ds: str, prices_full: pd.DataFrame) -> dict:
    cfg = DATASETS[ds]
    needed = sorted(set().union(*[set(w) for w in EFF_CONFIGS.values()], {cfg["benchmark"], "VTSIM"}))
    prices = prices_full[needed].loc[cfg["start"]:cfg["end"]].dropna(how="all").ffill()

    configs: dict[str, dict] = {}
    aligned: list[pd.Series] = []
    for cfg_id, weights in EFF_CONFIGS.items():
        gross = gross_returns(prices, weights)
        net, tax = net_returns_annual_darf(gross, weights)
        configs[cfg_id] = {
            "metrics": metrics_from_returns(net),
            "gross_metrics": metrics_from_returns(gross),
            "tax": tax,
            "net_returns": net,
            "gross_returns": gross,
        }
        aligned.append(net.rename(cfg_id))

    matrix_df = pd.concat(aligned, axis=1).dropna()
    pbo_result = pbo(matrix_df.to_numpy(dtype=float), n_blocks=10)
    g1_pass = pbo_result.pbo < 0.5
    return {
        "dataset": ds,
        "prices": prices,
        "configs": configs,
        "pbo": {"pbo": float(pbo_result.pbo), "n_combinations": pbo_result.n_combinations, "pass": g1_pass},
    }


def gate_selected(ds_result: dict, cfg_id: str) -> dict:
    prices = ds_result["prices"]
    weights = EFF_CONFIGS[cfg_id]
    net = ds_result["configs"][cfg_id]["net_returns"]
    metrics = ds_result["configs"][cfg_id]["metrics"]

    g2, pval = gate_dsr(net)
    g3, wf_returns, wf_mdds = gate_walk_forward(net)
    g4, oos_s = gate_oos_70_30(net)
    g5, fwd_s = gate_fwd(net)
    g6, ci_low = gate_bootstrap(net)
    np_rets = numpy_returns(prices, weights)
    np_eq = (1.0 + np_rets).cumprod() * 10_000.0
    np_cagr = float((np_eq[-1] / np_eq[0]) ** (252 / (len(np_rets) - 1)) - 1.0) if len(np_rets) > 252 else 0.0
    g7 = abs(np_cagr - metrics["cagr"]) * 100 <= 3.0
    gates = {
        "g1_pbo": ds_result["pbo"]["pass"],
        "g2_dsr": g2,
        "g3_wf": g3,
        "g4_oos": g4,
        "g5_fwd": g5,
        "g6_bootstrap": g6,
        "g7_crosslib": g7,
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
            "g7_np_cagr": np_cagr,
        },
    }


def main() -> None:
    prices_full = load_testfolio_frame(REPO_ROOT / "data/testfolio/cache/history.parquet")
    all_results = {ds: run_dataset(ds, prices_full) for ds in ["educational", "vt_real", "ndx_real"]}

    selection_scores: dict[str, float] = {}
    for cfg_id in CONFIGS:
        vals = []
        for ds in ["educational", "vt_real", "ndx_real"]:
            vals.append(all_results[ds]["configs"][cfg_id]["metrics"]["sharpe"] / BENCHMARKS[ds].sharpe)
        selection_scores[cfg_id] = float(np.mean(vals))
    selected_cfg = max(selection_scores, key=selection_scores.get)

    metrics_map: dict[str, DatasetMetrics] = {}
    gates_map: dict[str, Gates] = {}
    datasets_out: dict[str, dict] = {}
    returns_series: dict[str, dict] = {}
    for ds in ["educational", "vt_real", "ndx_real"]:
        gated = gate_selected(all_results[ds], selected_cfg)
        m = all_results[ds]["configs"][selected_cfg]["metrics"]
        gd = gated["gate_details"]
        g = gated["gates"]
        metrics_map[ds] = DatasetMetrics(m["sharpe"], m["cagr"], m["mdd"], dsr_p_value=gd["g2_dsr_p"])
        gates_map[ds] = Gates(g["g1_pbo"], g["g2_dsr"], g["g3_wf"], g["g4_oos"], g["g5_fwd"], g["g6_bootstrap"], g["g7_crosslib"])
        top_cfgs = sorted(
            all_results[ds]["configs"],
            key=lambda c: all_results[ds]["configs"][c]["metrics"]["sharpe"],
            reverse=True,
        )[:5]
        datasets_out[ds] = {
            "selected_config": selected_cfg,
            "selection_scores": selection_scores,
            "configs": {
                c: {
                    "metrics": all_results[ds]["configs"][c]["metrics"],
                    "gross_metrics": all_results[ds]["configs"][c]["gross_metrics"],
                }
                for c in CONFIGS
            },
            "top5_by_sharpe": top_cfgs,
            "selected": {"metrics": m, **gated, "tax": all_results[ds]["configs"][selected_cfg]["tax"]},
            "pbo": all_results[ds]["pbo"],
        }
        returns_series[ds] = {}
        for c in set([selected_cfg, top_cfgs[0]]):
            r = all_results[ds]["configs"][c]["net_returns"]
            returns_series[ds][c] = {"index": [str(d.date()) for d in r.index], "net_returns": r.tolist()}

    rob_pts, pct_pos, n_roll, roll_sharpes = rolling_robustness(all_results["educational"]["configs"][selected_cfg]["net_returns"])
    score = score_strategy(metrics_map, gates_map, cumulative_n_trials=2 + N_CONFIGS, robustness_bonus=rob_pts)

    verdict = score.to_dict()
    verdict.update({
        "status": score.tier.value.lower(),
        "configs_tested": N_CONFIGS,
        "primary_citation": "[risk_parity, p.1-2, p.10]",
        "hypothesis_slug": "global-factor-cta-stack",
        "selected_config": selected_cfg,
        "selection_rule": "max mean Sharpe / iter009 Sharpe across educational, vt_real, ndx_real",
        "robustness": {
            "bonus_pts": rob_pts,
            "pct_positive_sharpe": pct_pos,
            "n_windows": n_roll,
            "min_rolling_sharpe": float(min(roll_sharpes)) if roll_sharpes else None,
            "max_rolling_sharpe": float(max(roll_sharpes)) if roll_sharpes else None,
        },
    })

    def default(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return str(obj)

    (ITER_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2, default=default) + "\n")
    runs = {
        ds: {
            cfg_id: {
                "sharpe": all_results[ds]["configs"][cfg_id]["metrics"]["sharpe"],
                "cagr": all_results[ds]["configs"][cfg_id]["metrics"]["cagr"],
                "mdd": all_results[ds]["configs"][cfg_id]["metrics"]["mdd"],
            }
            for cfg_id in CONFIGS
        }
        for ds in ["educational", "vt_real", "ndx_real"]
    }

    (ITER_DIR / "results.json").write_text(json.dumps({
        "hypothesis_slug": "global-factor-cta-stack",
        "selected_config": selected_cfg,
        "configs_tested": N_CONFIGS,
        "runs": runs,
        "datasets": datasets_out,
        "returns_series": returns_series,
    }, indent=2, default=default) + "\n")

    print(f"Selected: {selected_cfg}")
    for ds in ["educational", "vt_real", "ndx_real"]:
        m = metrics_map[ds]
        print(f"{ds}: S={m.sharpe:.3f} CAGR={m.cagr:.2%} MDD={m.mdd:.2%} gates={gates_map[ds].n_passed}/7 DSRp={m.dsr_p_value:.2e}")
    print(f"Tier={score.tier.value} Score={score.total_score}/100 Winner={score.winner_conditions_met}")


if __name__ == "__main__":
    main()
