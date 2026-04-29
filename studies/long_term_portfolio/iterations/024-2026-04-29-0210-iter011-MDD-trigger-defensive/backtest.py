"""Iter 024 — B.2: MDD-trigger defensive regime-conditional shift on iter 011.

When SPY trailing-21d return < threshold (drawdown signal), reduce NTSX 50%
and add TLT or CASH defensive sleeve. Forward-looking: signal observed HOJE,
action is next-day rebalance (no peek). Distinct from iter 017 (B.6 factor-
weight gated) and iter 022 (synthetic tail-hedge).

3 pre-committed configs (≤3 to limit DSR penalty per advances_fin_ml p.222):
  - mdd_trigger_10pct_TLT:  SPY 21d < -10% → 50% NTSX → +TLT 50%
  - mdd_trigger_15pct_TLT:  SPY 21d < -15% → 50% NTSX → +TLT 50%
  - mdd_trigger_15pct_CASH: SPY 21d < -15% → 50% NTSX → +CASHX 50%

Hypothesis: see ./hypothesis.md.
Mission NEW: Sharpe edge ≥0.05 vs SPY on ≥2/3 datasets, MDD ≤ SPY.

Citations:
- Capital-efficient stacking: [risk_parity, ch.5, p.10]
- Position sizing / regime-conditional weights: [systematic_trading, p.137-148]
- PBO/DSR multi-config discipline: [advances_fin_ml, p.208-211, p.222-223]
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


SHARED = REPO_ROOT / "studies" / "_shared"
LOOP = REPO_ROOT / "studies" / "long_term_portfolio"
AnnualDarfEngine = _load_module("iter024_tax_engine", SHARED / "tax_engine.py").AnnualDarfEngine
_scoring = _load_module("iter024_scoring", LOOP / "scoring.py")
_datasets_mod = _load_module("iter024_datasets", LOOP / "datasets.py")
_proxies = _load_module("iter024_proxies", LOOP / "proxies.py")
DatasetMetrics = _scoring.DatasetMetrics
Gates = _scoring.Gates
BENCHMARKS = _scoring.BENCHMARKS
spy_benchmark = _scoring.spy_benchmark
avg_benchmark = _scoring.avg_benchmark
legacy_benchmarks = _scoring.legacy_benchmarks
score_strategy = _scoring.score_strategy
load_prices = _datasets_mod.load_prices
DATASETS_META = _datasets_mod.DATASETS
expand_capital_efficient = _proxies.expand_capital_efficient
PROXY_LEGS = _proxies.PROXY_LEGS

ITER_DIR = Path(__file__).parent
N_CONFIGS = 3
BOOTSTRAP_N = 2000
WF_N_WINDOWS = 8
CUMULATIVE_N_TRIALS_PRIOR = 87  # iter 023's cumulative

DATASETS = ["lh_56y", "vt_real", "ndx_real"]

# Base weights ON (default iter 011 35/25/40 NTSX/GDE/KMLM); when trigger
# fires, replace 50% of NTSX with defensive sleeve.
WEIGHTS_BASE = {"NTSX_PROXY": 0.35, "GDESIM": 0.25, "KMLMSIM": 0.40}

CONFIGS: dict[str, dict] = {
    "mdd_trigger_10pct_TLT": {
        "threshold": -0.10,
        "defensive_asset": "TLTSIM",
        "weights_on":  WEIGHTS_BASE,
        "weights_off": {"NTSX_PROXY": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.40, "TLTSIM": 0.175},
    },
    "mdd_trigger_15pct_TLT": {
        "threshold": -0.15,
        "defensive_asset": "TLTSIM",
        "weights_on":  WEIGHTS_BASE,
        "weights_off": {"NTSX_PROXY": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.40, "TLTSIM": 0.175},
    },
    "mdd_trigger_15pct_CASH": {
        "threshold": -0.15,
        "defensive_asset": "CASHX",
        "weights_on":  WEIGHTS_BASE,
        "weights_off": {"NTSX_PROXY": 0.175, "GDESIM": 0.25, "KMLMSIM": 0.40, "CASHX": 0.175},
    },
}


def compute_signal(prices: pd.DataFrame, threshold: float) -> pd.Series:
    """Daily ON/OFF mask. ON=defensive (signal fires), OFF=base.

    Signal: SPY 21d return < threshold (negative). Forward-looking — signal
    on day t reflects close-of-day-t-1 21d return, action applied at close-
    of-day-t (i.e., position effective from day t+1 onwards). The .shift(1)
    below ensures no day-t lookahead.

    Returns a boolean Series aligned to `prices.index`. True = trigger fires
    (defensive); False = base (offensive).
    """
    spy = prices["SPYSIM"].dropna()
    ret_21d = spy.pct_change(21)
    sig = (ret_21d.shift(1) < threshold).fillna(False).astype(bool)
    return sig.reindex(prices.index, method="ffill").fillna(False).astype(bool)


def compute_equity(returns: pd.Series, start: float = 10_000.0) -> pd.Series:
    return (1.0 + returns).cumprod() * start


def gross_returns_dynamic(prices: pd.DataFrame, signal: pd.Series, weights_on: dict, weights_off: dict) -> pd.Series:
    eff_on  = expand_capital_efficient(weights_on)
    eff_off = expand_capital_efficient(weights_off)
    needed = sorted(set(eff_on) | set(eff_off))
    needed = [t for t in needed if t in prices.columns]
    px = prices[needed].ffill().dropna(how="all")
    rets = px.pct_change()
    w_on = pd.Series({t: eff_on.get(t, 0.0) for t in needed}, dtype=float)
    w_off = pd.Series({t: eff_off.get(t, 0.0) for t in needed}, dtype=float)
    rets_on = (rets * w_on).sum(axis=1)
    rets_off = (rets * w_off).sum(axis=1)
    sig_aligned = signal.reindex(rets.index).fillna(False).astype(bool)
    # signal=True → defensive (off state), signal=False → base (on state)
    return rets_off.where(sig_aligned, rets_on).dropna().iloc[1:]


def gross_returns_dynamic_strict(prices: pd.DataFrame, signal: pd.Series, weights_on: dict, weights_off: dict) -> pd.Series:
    eff_on  = expand_capital_efficient(weights_on)
    eff_off = expand_capital_efficient(weights_off)
    needed = sorted(set(eff_on) | set(eff_off))
    needed = [t for t in needed if t in prices.columns]
    px = prices[needed].dropna(how="any")
    rets = px.pct_change().dropna()
    w_on = pd.Series({t: eff_on.get(t, 0.0) for t in needed}, dtype=float)
    w_off = pd.Series({t: eff_off.get(t, 0.0) for t in needed}, dtype=float)
    rets_on = (rets * w_on).sum(axis=1)
    rets_off = (rets * w_off).sum(axis=1)
    sig_aligned = signal.reindex(rets.index).fillna(False).astype(bool)
    return rets_off.where(sig_aligned, rets_on)


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


def metrics_from_returns(returns: pd.Series) -> dict[str, float]:
    eq = compute_equity(returns)
    return {
        "sharpe": float(sharpe(returns, periods_per_year=252)),
        "cagr":   float(cagr(eq, periods_per_year=252)),
        "mdd":    float(max_drawdown(eq)),
    }


def numpy_returns_dynamic(prices: pd.DataFrame, signal: pd.Series, weights_on: dict, weights_off: dict) -> np.ndarray:
    eff_on  = expand_capital_efficient(weights_on)
    eff_off = expand_capital_efficient(weights_off)
    needed = sorted(set(eff_on) | set(eff_off))
    needed = [t for t in needed if t in prices.columns]
    px_df = prices[needed].ffill().dropna(how="any")
    px = px_df.to_numpy(dtype=float)
    if len(px) < 2:
        return np.array([], dtype=float)
    w_on = np.array([eff_on.get(t, 0.0) for t in needed])
    w_off = np.array([eff_off.get(t, 0.0) for t in needed])
    daily = np.diff(px, axis=0) / px[:-1]
    sig_aligned = signal.reindex(px_df.index[1:]).fillna(False).astype(bool).to_numpy()
    rets_on = (daily * w_on).sum(axis=1)
    rets_off = (daily * w_off).sum(axis=1)
    return np.where(sig_aligned, rets_off, rets_on)


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
    prices_full = load_prices(ds)
    eff_legs = set()
    for cfg_id in CONFIGS:
        eff_legs |= set(expand_capital_efficient(CONFIGS[cfg_id]["weights_on"]))
        eff_legs |= set(expand_capital_efficient(CONFIGS[cfg_id]["weights_off"]))
    needed = sorted(set(list(eff_legs) + ["VTSIM", "QQQSIM", "SPYSIM"]).intersection(prices_full.columns))
    prices = prices_full[needed].dropna(how="all").ffill()

    configs: dict[str, dict] = {}
    aligned_gross: list[pd.Series] = []
    for cfg_id, cfg in CONFIGS.items():
        signal = compute_signal(prices, cfg["threshold"])
        gross = gross_returns_dynamic(prices, signal, cfg["weights_on"], cfg["weights_off"])
        gross_strict = gross_returns_dynamic_strict(prices_full[needed].dropna(how="all"), signal, cfg["weights_on"], cfg["weights_off"])
        net, tax = net_returns_annual_darf(gross)
        pct_on = float(signal.reindex(gross.index).fillna(False).mean())
        configs[cfg_id] = {
            "gross_metrics":         metrics_from_returns(gross),
            "gross_metrics_strict":  metrics_from_returns(gross_strict) if len(gross_strict) > 0 else None,
            "loose_window":          {"start": str(gross.index[0].date()), "end": str(gross.index[-1].date()), "n": len(gross)},
            "strict_window":         {"start": str(gross_strict.index[0].date()) if len(gross_strict)>0 else None, "end": str(gross_strict.index[-1].date()) if len(gross_strict)>0 else None, "n": len(gross_strict)},
            "net_metrics":           metrics_from_returns(net),
            "tax":                   tax,
            "gross_returns":         gross,
            "net_returns":           net,
            "pct_on":                pct_on,
            "signal":                signal.reindex(gross.index).fillna(False),
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
    prices = ds_result["prices"]
    cfg = CONFIGS[cfg_id]
    signal = ds_result["configs"][cfg_id]["signal"]
    gross = ds_result["configs"][cfg_id]["gross_returns"]
    metrics = ds_result["configs"][cfg_id]["gross_metrics"]

    g2, pval = gate_dsr(gross)
    g3, wf_returns, wf_mdds = gate_walk_forward(gross)
    g4, oos_s = gate_oos_70_30(gross)
    g5, fwd_s = gate_fwd(gross)
    g6, ci_low = gate_bootstrap(gross)
    np_rets = numpy_returns_dynamic(prices, signal, cfg["weights_on"], cfg["weights_off"])
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
    spy_bms = {ds: spy_benchmark(BENCHMARKS[ds]) for ds in DATASETS}
    avg_bms = {ds: avg_benchmark(BENCHMARKS[ds]) for ds in DATASETS}

    selection_scores: dict[str, float] = {}
    for cfg_id in CONFIGS:
        vals = [
            all_results[ds]["configs"][cfg_id]["gross_metrics"]["sharpe"] / spy_bms[ds].sharpe
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
        top_cfgs = sorted(CONFIGS, key=lambda c: all_results[ds]["configs"][c]["gross_metrics"]["sharpe"], reverse=True)
        datasets_out[ds] = {
            "selected_config": selected_cfg,
            "selection_scores": selection_scores,
            "configs": {
                c: {
                    "gross_metrics":        all_results[ds]["configs"][c]["gross_metrics"],
                    "gross_metrics_strict": all_results[ds]["configs"][c]["gross_metrics_strict"],
                    "net_metrics":          all_results[ds]["configs"][c]["net_metrics"],
                    "pct_on":               all_results[ds]["configs"][c]["pct_on"],
                    "loose_window":         all_results[ds]["configs"][c]["loose_window"],
                    "strict_window":        all_results[ds]["configs"][c]["strict_window"],
                }
                for c in CONFIGS
            },
            "top5_by_sharpe": top_cfgs,
            "selected": {
                "gross_metrics": gm,
                "net_metrics":   nm,
                **gated,
                "tax": all_results[ds]["configs"][selected_cfg]["tax"],
                "pct_on": all_results[ds]["configs"][selected_cfg]["pct_on"],
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
    score = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=CUMULATIVE_N_TRIALS_PRIOR + N_CONFIGS,
        robustness_bonus=rob_pts,
    )
    score_legacy = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=CUMULATIVE_N_TRIALS_PRIOR + N_CONFIGS,
        benchmarks=legacy_benchmarks(),
        robustness_bonus=rob_pts,
    )

    verdict = score.to_dict()
    verdict.update({
        "status":           score.tier.value.lower(),
        "configs_tested":   N_CONFIGS,
        "primary_citation": "[systematic_trading, p.137-148]",
        "hypothesis_slug":  "iter011-MDD-trigger-defensive",
        "selected_config":  selected_cfg,
        "selection_rule":   "NEW (2026-04-29 reframing): max mean(gross_Sharpe / SPY_Sharpe) across 3 datasets",
        "scoring_basis":    "NEW SPY-only +0.05 (mandate reframing 2026-04-29)",
        "score_legacy":     score_legacy.to_dict(),
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
                "pct_on":     all_results[ds]["configs"][cfg_id]["pct_on"],
            }
            for cfg_id in CONFIGS
        }
        for ds in DATASETS
    }

    serializable_configs = {
        cfg_id: {
            "threshold":        cfg["threshold"],
            "defensive_asset":  cfg["defensive_asset"],
            "weights_on":       cfg["weights_on"],
            "weights_off":      cfg["weights_off"],
        }
        for cfg_id, cfg in CONFIGS.items()
    }
    (ITER_DIR / "results.json").write_text(json.dumps({
        "hypothesis_slug": "iter011-MDD-trigger-defensive",
        "selected_config": selected_cfg,
        "configs_tested":  N_CONFIGS,
        "configs":         serializable_configs,
        "runs":            runs,
        "datasets":        datasets_out,
        "returns_series":  returns_series,
    }, indent=2, default=default) + "\n")

    print(f"Selected: {selected_cfg}")
    print("--- Per-dataset metrics (under NEW SPY-only baseline) ---")
    for ds in DATASETS:
        m = metrics_map[ds]
        spy_b = spy_bms[ds]
        avg_b = avg_bms[ds]
        spy_edge = m.sharpe - spy_b.sharpe
        avg_edge = m.sharpe - avg_b.sharpe
        cfg_data = all_results[ds]["configs"][selected_cfg]
        strict_s = cfg_data["gross_metrics_strict"]["sharpe"] if cfg_data["gross_metrics_strict"] else None
        strict_str = f" [strict={strict_s:.3f}]" if strict_s is not None else ""
        print(
            f"{ds}: gross S={m.sharpe:.3f}{strict_str} "
            f"(SPY={spy_b.sharpe:.3f} edge={spy_edge:+.3f}) "
            f"(avg={avg_b.sharpe:.3f} edge={avg_edge:+.3f}) "
            f"CAGR={m.cagr:.2%} MDD={m.mdd:.2%} gates={gates_map[ds].n_passed}/7 "
            f"DSRp={m.dsr_p_value:.2e} pct_on={cfg_data['pct_on']:.0%} | net S={m.net_sharpe:.3f}"
        )
    print(f"NEW    Tier={score.tier.value} Score={score.total_score}/100 Winner={score.winner_conditions_met}")
    print(f"LEGACY Tier={score_legacy.tier.value} Score={score_legacy.total_score}/100 Winner={score_legacy.winner_conditions_met}")

    print("\n--- Full grid (Sharpe + pct_on per config × dataset) ---")
    print(f"{'config':<28} {'lh_56y':>8} {'pct_on':>7} {'vt_real':>8} {'pct_on':>7} {'ndx_real':>9} {'pct_on':>7}")
    for cfg in CONFIGS:
        s_lh = all_results["lh_56y"]["configs"][cfg]["gross_metrics"]["sharpe"]
        s_vt = all_results["vt_real"]["configs"][cfg]["gross_metrics"]["sharpe"]
        s_nd = all_results["ndx_real"]["configs"][cfg]["gross_metrics"]["sharpe"]
        p_lh = all_results["lh_56y"]["configs"][cfg]["pct_on"]
        p_vt = all_results["vt_real"]["configs"][cfg]["pct_on"]
        p_nd = all_results["ndx_real"]["configs"][cfg]["pct_on"]
        print(f"{cfg:<28} {s_lh:>8.3f} {p_lh:>6.0%} {s_vt:>8.3f} {p_vt:>6.0%} {s_nd:>9.3f} {p_nd:>6.0%}")


if __name__ == "__main__":
    main()
