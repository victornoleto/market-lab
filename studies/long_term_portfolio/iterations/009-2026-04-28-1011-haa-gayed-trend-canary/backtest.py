"""Iter 009 HAA Gayed Trend Canary.

Keep iter 009 HAA+Gold assets unchanged and test whether a simple
Gayed-style broad-market trend input improves the binary HAA canary.

Citations:
- Gayed trend filter: [leverage_for_the_long_run, p.40-60]
- HAA momentum architecture: [stocks_on_the_move, ch.6]
- Gate battery: [advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]
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

from ai_trade.backtest.data.testfolio_loader import load_testfolio_frame
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


GLOBAL_LOOP = REPO_ROOT / "studies" / "global_factor_tilt_loop"
BESTFOLIO_LOOP = REPO_ROOT / "studies" / "long_term_portfolio"
AnnualDarfEngine = _load_module("iter009_tax_engine_v2", GLOBAL_LOOP / "tax_engine_v2.py").AnnualDarfEngine
_scoring = _load_module("iter009_bestfolio_scoring", BESTFOLIO_LOOP / "scoring.py")
DatasetMetrics = _scoring.DatasetMetrics
Gates = _scoring.Gates
BENCHMARKS = _scoring.BENCHMARKS
score_strategy = _scoring.score_strategy

ITER_DIR = Path(__file__).parent

N_CONFIGS = 4
CUMULATIVE_N_TRIALS_BEFORE = 28
KMLM_WEIGHT = 0.10
GLD_WEIGHT = 0.05
DYNAMIC_WEIGHT = 0.85
TOP_K_OFFENSIVE = 2
NOTIONAL_FACTOR = 1.45
WF_N_WINDOWS = 8
BOOTSTRAP_N = 2000

STACK_EQ = 0.90
STACK_BD = 0.60
STACK_CASH = 0.50

DATASETS = {
    "educational": {"start": "1995-01-01", "end": "2026-04-24", "benchmark": "VTSIM"},
    "vt_real": {"start": "2008-06-01", "end": "2026-04-24", "benchmark": "VTSIM"},
    "ndx_real": {"start": "2010-02-01", "end": "2026-04-24", "benchmark": "QQQSIM"},
}

OFFENSIVE = ["NTSXSIM", "NTSI", "NTSE", "GDESIM"]
DEFENSIVE = ["IEFSIM", "BNDSIM", "CASHX"]
CONFIGS: dict[str, str] = {
    "vwo_original": "vwo_original",
    "spy_trend": "spy_trend",
    "vt_trend": "vt_trend",
    "vwo_and_spy_trend": "vwo_and_spy_trend",
}


def compute_equity(returns: pd.Series, start: float = 10_000.0) -> pd.Series:
    return (1.0 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict[str, float]:
    eq = compute_equity(returns)
    return {
        "sharpe": float(sharpe(returns, periods_per_year=252)),
        "cagr": float(cagr(eq, periods_per_year=252)),
        "mdd": float(max_drawdown(eq)),
    }


def build_prices(raw: pd.DataFrame) -> pd.DataFrame:
    """Build iter 009 stacked offensive columns. [risk_parity, ch.5]"""
    out = raw.copy()
    ret = raw.pct_change()
    out["NTSXSIM"] = (1.0 + (STACK_EQ * ret["SPYSIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]).dropna()).cumprod() * 100.0
    out["NTSI"] = (1.0 + (STACK_EQ * ret["VEASIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]).dropna()).cumprod() * 100.0
    out["NTSE"] = (1.0 + (STACK_EQ * ret["VWOSIM"] + STACK_BD * ret["IEFSIM"] - STACK_CASH * ret["CASHX"]).dropna()).cumprod() * 100.0
    return out


def haa_momentum(monthly_prices: pd.DataFrame, assets: list[str]) -> pd.DataFrame:
    """HAA score = average 1/3/6/12 month return. [stocks_on_the_move, ch.6]"""
    scores = pd.DataFrame(index=monthly_prices.index, columns=assets, dtype=float)
    for asset in assets:
        p = monthly_prices[asset]
        scores[asset] = ((p / p.shift(1) - 1.0) + (p / p.shift(3) - 1.0) + (p / p.shift(6) - 1.0) + (p / p.shift(12) - 1.0)) / 4.0
    return scores


def trend_on(monthly_prices: pd.DataFrame, asset: str, i: int, lookback: int = 10) -> bool:
    """Monthly 10-month trend state. [leverage_for_the_long_run, p.40-60]"""
    p = monthly_prices[asset].iloc[i]
    ma = monthly_prices[asset].rolling(lookback).mean().iloc[i]
    return bool(np.isfinite(p) and np.isfinite(ma) and p > ma)


def monthly_weights(prices: pd.DataFrame, cfg_id: str) -> pd.DataFrame:
    offensive = OFFENSIVE
    defensive = DEFENSIVE
    all_assets = list(dict.fromkeys(offensive + defensive + ["VWOSIM", "SPYSIM", "VTSIM", "KMLMSIM", "GLDSIM"]))
    px = prices[all_assets].dropna(how="all")
    monthly = px.resample("ME").last()
    off_mom = haa_momentum(monthly, offensive)
    def_mom = haa_momentum(monthly, defensive)
    can_mom = haa_momentum(monthly, ["VWOSIM"])
    weights = pd.DataFrame(0.0, index=monthly.index, columns=all_assets)

    for i in range(12, len(monthly)):
        date = monthly.index[i]
        weights.loc[date, "KMLMSIM"] = KMLM_WEIGHT
        weights.loc[date, "GLDSIM"] = GLD_WEIGHT
        vwo_on = can_mom["VWOSIM"].iloc[i] > 0
        spy_on = trend_on(monthly, "SPYSIM", i)
        vt_on = trend_on(monthly, "VTSIM", i)
        mode = CONFIGS[cfg_id]
        if mode == "vwo_original":
            risk_on = vwo_on
        elif mode == "spy_trend":
            risk_on = spy_on
        elif mode == "vt_trend":
            risk_on = vt_on
        elif mode == "vwo_and_spy_trend":
            risk_on = vwo_on and spy_on
        else:
            raise ValueError(f"Unknown canary mode: {mode}")
        if risk_on:
            row = off_mom.iloc[i].dropna()
            chosen = row.nlargest(min(TOP_K_OFFENSIVE, len(row))).index.tolist()
            if chosen:
                for asset in chosen:
                    weights.loc[date, asset] = DYNAMIC_WEIGHT / len(chosen)
            else:
                weights.loc[date, "CASHX"] = DYNAMIC_WEIGHT
        else:
            row = def_mom.iloc[i].dropna()
            weights.loc[date, row.idxmax() if not row.empty else "CASHX"] += DYNAMIC_WEIGHT
    return weights


def simulate_gross(prices: pd.DataFrame, cfg_id: str) -> tuple[pd.Series, pd.DataFrame]:
    weights_m = monthly_weights(prices, cfg_id)
    assets = list(weights_m.columns)
    px = prices[assets].dropna(how="all")
    weights_d = weights_m.reindex(px.index, method="ffill").fillna(0.0)
    gross = (weights_d.shift(1) * px.pct_change()).sum(axis=1).dropna()
    active = weights_d.sum(axis=1) > 0
    if not active.any():
        return gross.iloc[0:0], weights_d
    return gross[gross.index >= active[active].index[0]], weights_d


def simulate_net(prices: pd.DataFrame, cfg_id: str) -> tuple[pd.Series, pd.Series, pd.DataFrame, dict]:
    """Apply AnnualDarfEngine to the tactical HAA path."""
    gross, weights = simulate_gross(prices, cfg_id)
    engine = AnnualDarfEngine(initial_investment=10_000.0)
    prev_value = engine.port_value
    prev_weights = {col: 0.0 for col in weights.columns}
    net_returns: list[float] = []
    last_year: int | None = None

    for date, daily_return in gross.items():
        current_weights = weights.loc[date].to_dict()
        if any(abs(current_weights.get(k, 0.0) - prev_weights.get(k, 0.0)) > 1e-9 for k in set(current_weights) | set(prev_weights)):
            engine.record_trade(date, prev_weights, current_weights)
            prev_weights = current_weights
        if last_year is not None and date.year != last_year:
            engine.year_end_settlement(last_year)
        last_year = date.year
        engine.apply_return(float(daily_return))
        net_returns.append(engine.port_value / prev_value - 1.0)
        prev_value = engine.port_value

    if last_year is not None:
        engine.year_end_settlement(last_year, force=True)
        if net_returns:
            net_returns[-1] = (1.0 + net_returns[-1]) * (engine.port_value / prev_value) - 1.0
    return pd.Series(net_returns, index=gross.index, name="net_returns"), gross, weights, engine.summary() | {"events": engine.events}


def simulate_numpy(prices: pd.DataFrame, cfg_id: str) -> np.ndarray:
    """Numpy-pure gross-return HAA reference for G7. [advances_fin_ml, p.31-34]"""
    offensive = OFFENSIVE
    defensive = DEFENSIVE
    assets = list(dict.fromkeys(offensive + defensive + ["VWOSIM", "SPYSIM", "VTSIM", "KMLMSIM", "GLDSIM"]))
    px = prices[assets].dropna(how="all")
    arr = px.to_numpy(dtype=float)
    periods = px.index.to_period("M")
    month_ends = [i - 1 for i in range(1, len(px)) if periods[i] != periods[i - 1]]
    if not month_ends or month_ends[-1] != len(px) - 1:
        month_ends.append(len(px) - 1)
    month_ends = np.array(month_ends, dtype=int)
    monthly = arr[month_ends]
    idx = {asset: i for i, asset in enumerate(assets)}

    def mom(col: int) -> np.ndarray:
        out = np.full(len(month_ends), np.nan)
        p = monthly[:, col]
        for i in range(12, len(month_ends)):
            vals = [p[i] / p[i - lag] - 1.0 for lag in (1, 3, 6, 12) if p[i - lag] > 0]
            if vals:
                out[i] = float(np.mean(vals))
        return out

    def ma_on(col: int, mi: int, lookback: int = 10) -> bool:
        if mi < lookback - 1:
            return False
        p = monthly[mi, col]
        ma = np.nanmean(monthly[mi - lookback + 1:mi + 1, col])
        return bool(np.isfinite(p) and np.isfinite(ma) and p > ma)

    off_scores = np.column_stack([mom(idx[a]) for a in offensive])
    def_scores = np.column_stack([mom(idx[a]) for a in defensive])
    vwo_scores = mom(idx["VWOSIM"])
    signal_weights = np.zeros((len(px), len(assets)))

    for mi in range(12, len(month_ends)):
        di = month_ends[mi]
        signal_weights[di, idx["KMLMSIM"]] = KMLM_WEIGHT
        signal_weights[di, idx["GLDSIM"]] = GLD_WEIGHT
        vwo_on = np.isfinite(vwo_scores[mi]) and vwo_scores[mi] > 0
        spy_on = ma_on(idx["SPYSIM"], mi)
        vt_on = ma_on(idx["VTSIM"], mi)
        mode = CONFIGS[cfg_id]
        if mode == "vwo_original":
            risk_on = vwo_on
        elif mode == "spy_trend":
            risk_on = spy_on
        elif mode == "vt_trend":
            risk_on = vt_on
        elif mode == "vwo_and_spy_trend":
            risk_on = vwo_on and spy_on
        else:
            raise ValueError(f"Unknown canary mode: {mode}")
        if risk_on:
            row = off_scores[mi]
            valid = np.where(np.isfinite(row))[0]
            chosen = valid[np.argsort(row[valid])[::-1][:TOP_K_OFFENSIVE]]
            if len(chosen):
                for local_i in chosen:
                    signal_weights[di, idx[offensive[int(local_i)]]] = DYNAMIC_WEIGHT / len(chosen)
            else:
                signal_weights[di, idx["CASHX"]] = DYNAMIC_WEIGHT
        else:
            row = def_scores[mi]
            valid = np.where(np.isfinite(row))[0]
            signal_weights[di, idx[defensive[int(valid[np.argmax(row[valid])])]] if len(valid) else idx["CASHX"]] += DYNAMIC_WEIGHT

    filled = np.zeros_like(signal_weights)
    last = np.zeros(len(assets))
    for i in range(len(px)):
        if signal_weights[i].sum() > 0:
            last = signal_weights[i].copy()
        filled[i] = last
    daily = np.diff(arr, axis=0) / arr[:-1]
    gross = np.nansum(filled[:-1] * daily, axis=1)
    first = np.where(filled.sum(axis=1) > 0)[0][0]
    return gross[first:]


def gate_dsr(returns: pd.Series) -> tuple[bool, float]:
    p_value = compute_dsr(returns.values, n_trials=N_CONFIGS).p_value if N_CONFIGS >= 2 else 1.0 - compute_psr(returns.values, benchmark=0.0)
    return p_value < 0.05, float(p_value)


def gate_walk_forward(returns: pd.Series, vtsim_returns: pd.Series) -> tuple[bool, bool, list[float], list[float], list[float]]:
    n = len(returns)
    window = n // (WF_N_WINDOWS + 1)
    if window < 63:
        return False, False, [], [], []
    wf_returns: list[float] = []
    wf_mdds: list[float] = []
    ref_mdds: list[float] = []
    for _, test_range in walk_forward_splits(n, window, window, window):
        idxs = list(test_range)
        sample = returns.iloc[idxs]
        wf_returns.append(float((1.0 + sample).prod() - 1.0))
        wf_mdds.append(float(max_drawdown(compute_equity(sample))))
        dates = returns.index[idxs]
        ref = vtsim_returns.loc[dates[0]:dates[-1]]
        ref_mdds.append(float(max_drawdown(compute_equity(ref))) * NOTIONAL_FACTOR if len(ref) > 5 else 0.50)
        if len(wf_returns) >= WF_N_WINDOWS:
            break
    n_pos = sum(x > 0 for x in wf_returns)
    nominal = len(wf_returns) == WF_N_WINDOWS and n_pos >= 6 and all(x <= 0.25 for x in wf_mdds)
    g3prime = len(wf_returns) == WF_N_WINDOWS and n_pos >= 6 and all(m <= r for m, r in zip(wf_mdds, ref_mdds))
    return nominal, g3prime, wf_returns, wf_mdds, ref_mdds


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
    for start in range(0, len(returns) - 252 * 5 + 1, 252):
        sample = returns.iloc[start:start + 252 * 5]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    pct = sum(s > 0 for s in sharpes) / len(sharpes) if sharpes else 0.0
    pts = 5 if pct >= 0.90 else 3 if pct >= 0.75 else 1 if pct >= 0.60 else 0
    return pts, pct, len(sharpes), sharpes


def run_dataset(ds: str, prices_full: pd.DataFrame) -> dict:
    cfg = DATASETS[ds]
    needed = ["SPYSIM", "VEASIM", "VWOSIM", "VTSIM", "IEFSIM", "CASHX", "KMLMSIM", "GLDSIM", "GDESIM", "BNDSIM", "QQQSIM"]
    prices = prices_full[needed].loc[cfg["start"]:cfg["end"]].ffill().dropna(how="all")
    prices = build_prices(prices)
    configs: dict[str, dict] = {}
    aligned: list[pd.Series] = []
    for cfg_id in CONFIGS:
        net, gross, weights, tax = simulate_net(prices, cfg_id)
        configs[cfg_id] = {
            "metrics": metrics_from_returns(net),
            "gross_metrics": metrics_from_returns(gross),
            "tax": tax,
            "net_returns": net,
            "gross_returns": gross,
            "weights": weights,
        }
        aligned.append(net.rename(cfg_id))
    matrix = pd.concat(aligned, axis=1).dropna()
    pbo_result = pbo(matrix.to_numpy(dtype=float), n_blocks=10)
    return {
        "dataset": ds,
        "prices": prices,
        "configs": configs,
        "pbo": {"pbo": float(pbo_result.pbo), "n_combinations": pbo_result.n_combinations, "pass": bool(pbo_result.pbo < 0.5)},
    }


def gate_selected(ds_result: dict, cfg_id: str) -> dict:
    prices = ds_result["prices"]
    net = ds_result["configs"][cfg_id]["net_returns"]
    metrics = ds_result["configs"][cfg_id]["metrics"]
    gross_metrics = ds_result["configs"][cfg_id]["gross_metrics"]
    g2, pval = gate_dsr(net)
    vtsim_ret = prices["VTSIM"].pct_change().dropna()
    g3_nominal, g3_prime, wf_returns, wf_mdds, ref_mdds = gate_walk_forward(net, vtsim_ret)
    g4, oos_s = gate_oos_70_30(net)
    g5, fwd_s = gate_fwd(net)
    g6, ci_low = gate_bootstrap(net)
    np_rets = simulate_numpy(prices, cfg_id)
    np_eq = (1.0 + np_rets).cumprod() * 10_000.0
    np_cagr = float((np_eq[-1] / np_eq[0]) ** (252 / (len(np_rets) - 1)) - 1.0) if len(np_rets) > 252 else 0.0
    g7 = abs(np_cagr - gross_metrics["cagr"]) * 100 <= 3.0
    gates = {
        "g1_pbo": ds_result["pbo"]["pass"],
        "g2_dsr": g2,
        "g3_wf": g3_prime,
        "g4_oos": g4,
        "g5_fwd": g5,
        "g6_bootstrap": g6,
        "g7_crosslib": g7,
    }
    return {
        "gates": gates | {"n_passed": sum(gates.values()), "g3_nominal_pass": g3_nominal, "g3_prime_pass": g3_prime},
        "gate_details": {
            "g1_pbo": ds_result["pbo"]["pbo"],
            "g2_dsr_p": pval,
            "g3_wf_returns": wf_returns,
            "g3_wf_mdds": wf_mdds,
            "g3_ref_mdds": ref_mdds,
            "g3_max_wf_mdd": max(wf_mdds) if wf_mdds else 0.0,
            "g4_oos_sharpe": oos_s,
            "g5_fwd_sharpe": fwd_s,
            "g6_ci_low": ci_low,
            "g7_np_cagr": np_cagr,
            "g7_pandas_gross_cagr": gross_metrics["cagr"],
        },
    }


def main() -> None:
    raw = load_testfolio_frame(REPO_ROOT / "data/testfolio/cache/history.parquet")
    all_results = {ds: run_dataset(ds, raw) for ds in ["educational", "vt_real", "ndx_real"]}

    selection_scores: dict[str, float] = {}
    for cfg_id in CONFIGS:
        selection_scores[cfg_id] = float(np.mean([
            all_results[ds]["configs"][cfg_id]["metrics"]["sharpe"] / BENCHMARKS[ds].sharpe
            for ds in ["educational", "vt_real", "ndx_real"]
        ]))
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
        top_cfgs = sorted(CONFIGS, key=lambda c: all_results[ds]["configs"][c]["metrics"]["sharpe"], reverse=True)[:5]
        datasets_out[ds] = {
            "selected_config": selected_cfg,
            "selection_scores": selection_scores,
            "configs": {c: {"metrics": all_results[ds]["configs"][c]["metrics"], "gross_metrics": all_results[ds]["configs"][c]["gross_metrics"]} for c in CONFIGS},
            "top5_by_sharpe": top_cfgs,
            "selected": {"metrics": m, **gated, "tax": all_results[ds]["configs"][selected_cfg]["tax"]},
            "pbo": all_results[ds]["pbo"],
        }
        returns_series[ds] = {}
        for cfg_for_series in top_cfgs:
            r = all_results[ds]["configs"][cfg_for_series]["net_returns"]
            returns_series[ds][cfg_for_series] = {
                "index": [str(d.date()) for d in r.index],
                "net_returns": r.tolist(),
            }

    rob_pts, pct_pos, n_roll, roll_sharpes = rolling_robustness(all_results["educational"]["configs"][selected_cfg]["net_returns"])
    score = score_strategy(metrics_map, gates_map, cumulative_n_trials=CUMULATIVE_N_TRIALS_BEFORE + N_CONFIGS, robustness_bonus=rob_pts)

    verdict = score.to_dict()
    verdict.update({
        "status": score.tier.value.lower(),
        "configs_tested": N_CONFIGS,
        "primary_citation": "[leverage_for_the_long_run, p.40-60]",
        "hypothesis_slug": "haa-gayed-trend-canary",
        "selected_config": selected_cfg,
        "selection_rule": "max mean Sharpe / iter009 Sharpe across educational, vt_real, ndx_real",
        "tax_model": "AnnualDarfEngine",
        "notional_factor": NOTIONAL_FACTOR,
        "canary_configs": CONFIGS,
        "defensive_universe": DEFENSIVE,
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
    (ITER_DIR / "results.json").write_text(json.dumps({
        "hypothesis_slug": "haa-gayed-trend-canary",
        "selected_config": selected_cfg,
        "configs_tested": N_CONFIGS,
        "tax_model": "AnnualDarfEngine",
        "canary_configs": CONFIGS,
        "defensive_universe": DEFENSIVE,
        "offensive_universe": OFFENSIVE,
        "runs": {ds: {cfg_id: all_results[ds]["configs"][cfg_id]["metrics"] for cfg_id in CONFIGS} for ds in ["educational", "vt_real", "ndx_real"]},
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
