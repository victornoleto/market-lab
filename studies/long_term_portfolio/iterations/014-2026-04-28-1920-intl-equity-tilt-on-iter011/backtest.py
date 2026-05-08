"""Iter 014 — International equity tilt on iter 011 base (NTSX + VXUSSIM + GDE + KMLM).

Adds a broad ex-US international equity sleeve (VXUSSIM, the testfolio
synth analog of Vanguard VXUS — Total International ex-US Stock Market)
to iter 011's NTSX + GDE + KMLM stack at 10/20/25/30% intensities. Tests
Direction A.3 from BASE_MEMORY (intl tilt on iter 011) — the residual
clean axis after iter 012 closed RSSB-style intl exposure (Treasury
overlap with NTSX, DE-013) and iter 013 closed constant-weight US
small-cap value (post-2008 "death of value", DE-014).

VXUSSIM is qualitatively different from both prior failure modes:
  - vs iter 012 (RSSB): VXUSSIM is 1× notional with ZERO Treasury → no
    duplication of NTSX's IEFSIM exposure.
  - vs iter 013 (VBRSIM): VXUSSIM is broad-market intl beta, not a US
    factor sleeve, so the 2009-2024 "death of value" regime doesn't
    apply.

Hypothesis: see ./hypothesis.md.

Mission: gross-of-tax Sharpe edge ≥0.10 vs avg(SPY, VT) per dataset on
≥2 of 3 datasets. Net-of-tax via `_shared/tax_engine.py`
(AnnualDarfEngine, Lei 14.754/2023) reported as informational only.

Citations:
- Capital-efficient stacking core (NTSX/GDE retained): [risk_parity, ch.5, p.10]
- Global equity diversification: [ilmanen, ch.19]
- Crisis-alpha (KMLM retained): [stocks_on_the_move, p.21-30]
- Gates G1 PBO / G2 DSR / G6 bootstrap / G7 cross-lib:
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

from market_lab.backtest.metrics.performance import cagr, max_drawdown, sharpe
from market_lab.backtest.validation.dsr import dsr as compute_dsr
from market_lab.backtest.validation.dsr import psr as compute_psr
from market_lab.backtest.validation.pbo import pbo
from market_lab.backtest.validation.walk_forward import walk_forward_splits


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
AnnualDarfEngine = _load_module("iter014_tax_engine", SHARED / "tax_engine.py").AnnualDarfEngine
_scoring = _load_module("iter014_scoring", LOOP / "scoring.py")
_datasets_mod = _load_module("iter014_datasets", LOOP / "datasets.py")
DatasetMetrics = _scoring.DatasetMetrics
Gates = _scoring.Gates
BENCHMARKS = _scoring.BENCHMARKS
avg_benchmark = _scoring.avg_benchmark
score_strategy = _scoring.score_strategy
load_prices = _datasets_mod.load_prices
DATASETS_META = _datasets_mod.DATASETS

ITER_DIR = Path(__file__).parent
N_CONFIGS = 4
BOOTSTRAP_N = 2000
WF_N_WINDOWS = 8

DATASETS = ["lh_56y", "vt_real", "ndx_real"]

# Pre-committed grid: VXUSSIM intensity sweep on iter 011 base.
# All configs keep NTSX_PROXY ≥ 25% (cap-efficient core) + KMLMSIM ≥ 25%
# (crisis-alpha). VXUSSIM 10/20/25/30% tests if intl-equity diversification
# adds Sharpe at the portfolio level. NTSX_PROXY expands in expand_weights.
CONFIGS: dict[str, dict[str, float]] = {
    "intl_lite_35253010":     {"NTSX_PROXY": 0.35, "VXUSSIM": 0.10, "GDESIM": 0.25, "KMLMSIM": 0.30},
    "intl_moderate_30202525": {"NTSX_PROXY": 0.30, "VXUSSIM": 0.20, "GDESIM": 0.25, "KMLMSIM": 0.25},
    "intl_balanced_25252525": {"NTSX_PROXY": 0.25, "VXUSSIM": 0.25, "GDESIM": 0.25, "KMLMSIM": 0.25},
    "intl_heavy_25302025":    {"NTSX_PROXY": 0.25, "VXUSSIM": 0.30, "GDESIM": 0.20, "KMLMSIM": 0.25},
}


def expand_weights(weights: dict[str, float]) -> dict[str, float]:
    """Expand NTSX_PROXY into testfolio legs.

    NTSX synth (validated 2026-04-26 in deploy_studies):
      NTSX = 0.90 SPYSIM + 0.60 IEFSIM − 0.50 CASHX
    [risk_parity, p.10]
    """
    out: dict[str, float] = {}
    for ticker, weight in weights.items():
        if ticker == "NTSX_PROXY":
            out["SPYSIM"] = out.get("SPYSIM", 0.0) + 0.90 * weight
            out["IEFSIM"] = out.get("IEFSIM", 0.0) + 0.60 * weight
            out["CASHX"] = out.get("CASHX", 0.0) - 0.50 * weight
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
    """Apply AnnualDarfEngine to static returns (Lei 14.754/2023)."""
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
        "cagr":   float(cagr(eq, periods_per_year=252)),
        "mdd":    float(max_drawdown(eq)),
    }


def numpy_returns(prices: pd.DataFrame, weights: dict[str, float]) -> np.ndarray:
    """Numpy-pure reference for G7 cross-lib parity."""
    tickers = [t for t in weights if t in prices.columns]
    px_df = prices[tickers].ffill()
    px_df = px_df.dropna(how="any")
    px = px_df.to_numpy(dtype=float)
    if len(px) < 2:
        return np.array([], dtype=float)
    w = np.array([weights[t] for t in tickers], dtype=float)
    daily = np.diff(px, axis=0) / px[:-1]
    return (daily * w).sum(axis=1)


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
    """Run all configs on a single dataset, returning per-config metrics + PBO."""
    prices_full = load_prices(ds)
    needed_legs = sorted(set().union(*[set(w) for w in EFF_CONFIGS.values()]))
    needed = sorted(set(needed_legs + ["VTSIM", "QQQSIM", "SPYSIM"]).intersection(prices_full.columns))
    prices = prices_full[needed].dropna(how="all").ffill()

    configs: dict[str, dict] = {}
    aligned_gross: list[pd.Series] = []
    for cfg_id, weights in EFF_CONFIGS.items():
        gross = gross_returns(prices, weights)
        net, tax = net_returns_annual_darf(gross, weights)
        configs[cfg_id] = {
            "gross_metrics": metrics_from_returns(gross),
            "net_metrics":   metrics_from_returns(net),
            "tax": tax,
            "gross_returns": gross,
            "net_returns":   net,
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
    """7-gate battery on GROSS returns (mission-aligned)."""
    prices = ds_result["prices"]
    weights = EFF_CONFIGS[cfg_id]
    gross = ds_result["configs"][cfg_id]["gross_returns"]
    metrics = ds_result["configs"][cfg_id]["gross_metrics"]

    g2, pval = gate_dsr(gross)
    g3, wf_returns, wf_mdds = gate_walk_forward(gross)
    g4, oos_s = gate_oos_70_30(gross)
    g5, fwd_s = gate_fwd(gross)
    g6, ci_low = gate_bootstrap(gross)
    np_rets = numpy_returns(prices, weights)
    np_eq = (1.0 + np_rets).cumprod() * 10_000.0
    np_cagr = (
        float((np_eq[-1] / np_eq[0]) ** (252 / (len(np_rets) - 1)) - 1.0)
        if len(np_rets) > 252
        else 0.0
    )
    g7 = abs(np_cagr - metrics["cagr"]) * 100 <= 3.0
    gates = {
        "g1_pbo":       ds_result["pbo"]["pass"],
        "g2_dsr":       g2,
        "g3_wf":        g3,
        "g4_oos":       g4,
        "g5_fwd":       g5,
        "g6_bootstrap": g6,
        "g7_crosslib":  g7,
    }
    return {
        "gates": gates | {"n_passed": sum(gates.values())},
        "gate_details": {
            "g1_pbo":         ds_result["pbo"]["pbo"],
            "g2_dsr_p":       pval,
            "g3_wf_returns":  wf_returns,
            "g3_wf_mdds":     wf_mdds,
            "g3_max_wf_mdd":  max(wf_mdds) if wf_mdds else 0.0,
            "g4_oos_sharpe":  oos_s,
            "g5_fwd_sharpe":  fwd_s,
            "g6_ci_low":      ci_low,
            "g7_np_cagr":     np_cagr,
        },
    }


def main() -> None:
    all_results = {ds: run_dataset(ds) for ds in DATASETS}

    avg_bms = {ds: avg_benchmark(BENCHMARKS[ds]) for ds in DATASETS}

    selection_scores: dict[str, float] = {}
    for cfg_id in CONFIGS:
        vals = [
            all_results[ds]["configs"][cfg_id]["gross_metrics"]["sharpe"] / avg_bms[ds].sharpe
            for ds in DATASETS
        ]
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
        top_cfgs = sorted(
            all_results[ds]["configs"],
            key=lambda c: all_results[ds]["configs"][c]["gross_metrics"]["sharpe"],
            reverse=True,
        )[:5]
        datasets_out[ds] = {
            "selected_config": selected_cfg,
            "selection_scores": selection_scores,
            "configs": {
                c: {
                    "gross_metrics": all_results[ds]["configs"][c]["gross_metrics"],
                    "net_metrics":   all_results[ds]["configs"][c]["net_metrics"],
                }
                for c in CONFIGS
            },
            "top5_by_sharpe": top_cfgs,
            "selected": {
                "gross_metrics": gm,
                "net_metrics":   nm,
                **gated,
                "tax": all_results[ds]["configs"][selected_cfg]["tax"],
            },
            "pbo": all_results[ds]["pbo"],
        }
        returns_series[ds] = {}
        for c in set([selected_cfg, top_cfgs[0]]):
            gr = all_results[ds]["configs"][c]["gross_returns"]
            nr = all_results[ds]["configs"][c]["net_returns"]
            returns_series[ds][c] = {
                "index":         [str(d.date()) for d in gr.index],
                "gross_returns": gr.tolist(),
                "net_returns":   nr.tolist(),
            }

    rob_pts, pct_pos, n_roll, roll_sharpes = rolling_robustness(
        all_results["lh_56y"]["configs"][selected_cfg]["gross_returns"]
    )
    score = score_strategy(metrics_map, gates_map, cumulative_n_trials=48 + N_CONFIGS, robustness_bonus=rob_pts)

    verdict = score.to_dict()
    verdict.update({
        "status":           score.tier.value.lower(),
        "configs_tested":   N_CONFIGS,
        "primary_citation": "[risk_parity, ch.5, p.10]",
        "hypothesis_slug":  "intl-equity-tilt-on-iter011",
        "selected_config":  selected_cfg,
        "selection_rule":   "max mean(gross_Sharpe / avg(SPY,VT)_Sharpe) across 3 datasets",
        "net_metrics": {
            ds: {
                "sharpe": all_results[ds]["configs"][selected_cfg]["net_metrics"]["sharpe"],
                "cagr":   all_results[ds]["configs"][selected_cfg]["net_metrics"]["cagr"],
                "mdd":    all_results[ds]["configs"][selected_cfg]["net_metrics"]["mdd"],
            }
            for ds in DATASETS
        },
        "robustness": {
            "bonus_pts":            rob_pts,
            "pct_positive_sharpe":  pct_pos,
            "n_windows":            n_roll,
            "min_rolling_sharpe":   float(min(roll_sharpes)) if roll_sharpes else None,
            "max_rolling_sharpe":   float(max(roll_sharpes)) if roll_sharpes else None,
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
                "sharpe":     all_results[ds]["configs"][cfg_id]["gross_metrics"]["sharpe"],
                "cagr":       all_results[ds]["configs"][cfg_id]["gross_metrics"]["cagr"],
                "mdd":        all_results[ds]["configs"][cfg_id]["gross_metrics"]["mdd"],
                "net_sharpe": all_results[ds]["configs"][cfg_id]["net_metrics"]["sharpe"],
                "net_cagr":   all_results[ds]["configs"][cfg_id]["net_metrics"]["cagr"],
                "net_mdd":    all_results[ds]["configs"][cfg_id]["net_metrics"]["mdd"],
            }
            for cfg_id in CONFIGS
        }
        for ds in DATASETS
    }

    (ITER_DIR / "results.json").write_text(json.dumps({
        "hypothesis_slug": "intl-equity-tilt-on-iter011",
        "selected_config": selected_cfg,
        "configs_tested":  N_CONFIGS,
        "configs":         CONFIGS,
        "eff_configs":     EFF_CONFIGS,
        "runs":            runs,
        "datasets":        datasets_out,
        "returns_series":  returns_series,
    }, indent=2, default=default) + "\n")

    print(f"Selected: {selected_cfg}")
    for ds in DATASETS:
        m = metrics_map[ds]
        bm = avg_bms[ds]
        edge = m.sharpe - bm.sharpe
        print(
            f"{ds}: gross S={m.sharpe:.3f} (avg(SPY,VT)={bm.sharpe:.3f}, edge={edge:+.3f}) "
            f"CAGR={m.cagr:.2%} MDD={m.mdd:.2%} gates={gates_map[ds].n_passed}/7 DSRp={m.dsr_p_value:.2e} "
            f"| net S={m.net_sharpe:.3f}"
        )
    print(f"Tier={score.tier.value} Score={score.total_score}/100 Winner={score.winner_conditions_met}")


if __name__ == "__main__":
    main()
