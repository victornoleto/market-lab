"""BAA-G12 Balanced simulator for bestfolio_hunt_loop iter 001.

Rules:
- Canary: 13612W absolute momentum on SPYSIM/VEASIM/VWOSIM/BNDSIM.
- Offensive mode: top-6 offensive assets by SMA(12) relative momentum.
- Defensive mode: top-3 defensive assets by SMA(12), replacing assets
  below CASHX momentum with CASHX.

Citations:
- Rotation / momentum mechanism: [stocks_on_the_move, ch.6]
- PBO / DSR / bootstrap / cross-lib validation: [advances_fin_ml, p.208-211,
  p.222-223, p.196-202, p.31-34]
"""

from __future__ import annotations

import json
import sys
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_frame
from src.ai_trade.backtest.metrics.performance import cagr, max_drawdown, sharpe
from src.ai_trade.backtest.validation.dsr import dsr as compute_dsr
from src.ai_trade.backtest.validation.dsr import psr as compute_psr
from src.ai_trade.backtest.validation.pbo import MIN_HONEST_N_CONFIGS
from src.ai_trade.backtest.validation.walk_forward import walk_forward_splits

GLOBAL_LOOP = REPO_ROOT / "studies" / "global_factor_tilt_loop"
BESTFOLIO_LOOP = REPO_ROOT / "studies" / "bestfolio_hunt_loop"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_tax_engine = _load_module("bestfolio_iter001_tax_engine_v2", GLOBAL_LOOP / "tax_engine_v2.py")
_scoring = _load_module("bestfolio_iter001_scoring", BESTFOLIO_LOOP / "scoring.py")
AnnualDarfEngine = _tax_engine.AnnualDarfEngine
DatasetMetrics = _scoring.DatasetMetrics
Gates = _scoring.Gates
score_strategy = _scoring.score_strategy

ITER_DIR = Path(__file__).parent

N_CONFIGS = 1
CFG_ID = "BAA_G12_balanced_top6_def3_cash_replacement"
WF_N_WINDOWS = 8
BOOTSTRAP_N = 2000
NOTIONAL_FACTOR = 1.07

CANARY_ASSETS = ["SPYSIM", "VEASIM", "VWOSIM", "BNDSIM"]
OFFENSIVE_ASSETS = [
    "SPYSIM", "QQQSIM", "VBRSIM", "VEASIM", "VWOSIM", "VSSSIM",
    "EFVSIM", "GLDSIM", "TLTSIM", "BNDSIM", "GDESIM", "KMLMSIM",
]
DEFENSIVE_RISK_ASSETS = ["IEFSIM", "BNDSIM", "TLTSIM", "GLDSIM", "KMLMSIM"]
DEFENSIVE_ASSETS = ["CASHX", *DEFENSIVE_RISK_ASSETS]
RAW_TICKERS = sorted(set(CANARY_ASSETS + OFFENSIVE_ASSETS + DEFENSIVE_ASSETS + ["VTSIM"]))

DATASETS = {
    "educational": {
        "start": "1994-05-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM synth; start constrained by VWOSIM/VSSSIM history",
    },
    "vt_real": {
        "start": "2008-06-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM proxy 2008-06+; real VT not pulled",
    },
    "ndx_real": {
        "start": "2010-02-01",
        "end": "2026-04-24",
        "benchmark": "QQQSIM",
        "label": "QQQSIM stretch test 2010-02+",
    },
}


def momentum_13612w(monthly_prices: pd.DataFrame, assets: list[str]) -> pd.DataFrame:
    """Fast absolute momentum used by BAA canaries. [stocks_on_the_move, ch.6]"""
    scores = pd.DataFrame(index=monthly_prices.index, columns=assets, dtype=float)
    for asset in assets:
        p = monthly_prices[asset]
        r1 = p / p.shift(1) - 1
        r3 = p / p.shift(3) - 1
        r6 = p / p.shift(6) - 1
        r12 = p / p.shift(12) - 1
        scores[asset] = (12.0 * r1 + 4.0 * r3 + 2.0 * r6 + r12) / 19.0
    return scores


def sma12_momentum(monthly_prices: pd.DataFrame, assets: list[str]) -> pd.DataFrame:
    """Slow relative momentum: price / SMA(13 month-end prices) - 1."""
    scores = pd.DataFrame(index=monthly_prices.index, columns=assets, dtype=float)
    for asset in assets:
        p = monthly_prices[asset]
        scores[asset] = p / p.rolling(13).mean() - 1.0
    return scores


def baa_monthly_weights(prices: pd.DataFrame) -> pd.DataFrame:
    """Build month-end BAA-G12 target weights without tax side effects."""
    assets = sorted(set(CANARY_ASSETS + OFFENSIVE_ASSETS + DEFENSIVE_ASSETS))
    px = prices[assets].dropna(how="all")
    monthly = px.resample("ME").last()
    canary_mom = momentum_13612w(monthly, CANARY_ASSETS)
    off_mom = sma12_momentum(monthly, OFFENSIVE_ASSETS)
    def_mom = sma12_momentum(monthly, DEFENSIVE_RISK_ASSETS + ["CASHX"])

    weights = pd.DataFrame(0.0, index=monthly.index, columns=assets)
    for i in range(13, len(monthly)):
        date = monthly.index[i]
        canary_row = canary_mom.iloc[i].dropna()
        offensive_mode = (not canary_row.empty) and bool((canary_row > 0).all())

        if offensive_mode:
            row = off_mom.iloc[i].dropna()
            chosen = row.nlargest(min(6, len(row))).index.tolist()
            if not chosen:
                weights.loc[date, "CASHX"] = 1.0
            else:
                for asset in chosen:
                    weights.loc[date, asset] = 1.0 / len(chosen)
            continue

        row = def_mom.iloc[i].dropna()
        risk_row = row[[a for a in DEFENSIVE_RISK_ASSETS if a in row.index]].dropna()
        cash_mom = row.get("CASHX", 0.0)
        chosen = risk_row.nlargest(min(3, len(risk_row))).index.tolist()
        for asset in chosen:
            target = asset if row.get(asset, -np.inf) >= cash_mom else "CASHX"
            weights.loc[date, target] += 1.0 / len(chosen)
        if not chosen:
            weights.loc[date, "CASHX"] = 1.0

    return weights


def simulate_baa_g12_gross(prices: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Return gross daily returns and daily target weights."""
    assets = sorted(set(CANARY_ASSETS + OFFENSIVE_ASSETS + DEFENSIVE_ASSETS))
    px = prices[assets].dropna(how="all")
    monthly_weights = baa_monthly_weights(px)
    daily_weights = monthly_weights.reindex(px.index, method="ffill").fillna(0.0)
    daily_ret = px.pct_change()
    gross = (daily_weights.shift(1) * daily_ret).sum(axis=1).dropna()
    first_signal = monthly_weights.index[13]
    return gross[gross.index >= first_signal], daily_weights


def simulate_baa_g12_net(prices: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.DataFrame, dict]:
    """Return AnnualDarfEngine net returns plus gross returns and weights."""
    gross, weights = simulate_baa_g12_gross(prices)
    engine = AnnualDarfEngine(initial_investment=10_000.0)
    prev_value = engine.port_value
    prev_weights = {k: 0.0 for k in weights.columns}
    net_returns: list[float] = []
    last_year = None

    for date, daily_return in gross.items():
        current_weights = weights.loc[date].to_dict()
        if any(abs(current_weights.get(k, 0.0) - prev_weights.get(k, 0.0)) > 1e-9 for k in set(current_weights) | set(prev_weights)):
            engine.record_trade(date, prev_weights, current_weights)
            prev_weights = current_weights

        if last_year is not None and date.year != last_year:
            engine.year_end_settlement(last_year)
        last_year = date.year

        engine.apply_return(float(daily_return))
        new_value = engine.port_value
        net_returns.append(new_value / prev_value - 1.0)
        prev_value = new_value

    if last_year is not None:
        engine.year_end_settlement(last_year, force=True)
        if net_returns:
            # Put final settlement into the last available trading day return.
            final_value = engine.port_value
            pre_settle_value = prev_value
            net_returns[-1] = (1.0 + net_returns[-1]) * (final_value / pre_settle_value) - 1.0

    net = pd.Series(net_returns, index=gross.index, name="net_returns")
    return net, gross, weights, engine.summary() | {"events": engine.events}


def simulate_baa_g12_numpy(prices: pd.DataFrame) -> np.ndarray:
    """Numpy-pure gross-return reference for G7. [advances_fin_ml, p.31-34]"""
    assets = sorted(set(CANARY_ASSETS + OFFENSIVE_ASSETS + DEFENSIVE_ASSETS))
    px = prices[assets].dropna(how="all")
    arr = px.to_numpy(dtype=float)
    dates = px.index
    asset_idx = {asset: i for i, asset in enumerate(assets)}
    periods = dates.to_period("M")
    month_ends = [i - 1 for i in range(1, len(dates)) if periods[i] != periods[i - 1]]
    if not month_ends or month_ends[-1] != len(dates) - 1:
        month_ends.append(len(dates) - 1)
    month_ends_arr = np.array(month_ends, dtype=int)
    monthly = arr[month_ends_arr]
    n_months, n_assets = monthly.shape

    def _mom13612(col: int) -> np.ndarray:
        out = np.full(n_months, np.nan)
        p = monthly[:, col]
        for i in range(12, n_months):
            vals = [(p[i] / p[i - 1] - 1, 12.0), (p[i] / p[i - 3] - 1, 4.0), (p[i] / p[i - 6] - 1, 2.0), (p[i] / p[i - 12] - 1, 1.0)]
            clean = [(v, w) for v, w in vals if np.isfinite(v)]
            if clean:
                out[i] = sum(v * w for v, w in clean) / sum(w for _, w in clean)
        return out

    def _sma12(col: int) -> np.ndarray:
        out = np.full(n_months, np.nan)
        p = monthly[:, col]
        for i in range(12, n_months):
            window = p[i - 12:i + 1]
            if np.isfinite(window).all():
                out[i] = p[i] / window.mean() - 1.0
        return out

    canary_scores = np.column_stack([_mom13612(asset_idx[a]) for a in CANARY_ASSETS])
    off_scores = np.column_stack([_sma12(asset_idx[a]) for a in OFFENSIVE_ASSETS])
    def_scores = np.column_stack([_sma12(asset_idx[a]) for a in DEFENSIVE_RISK_ASSETS])
    cash_scores = _sma12(asset_idx["CASHX"])
    off_indices = [asset_idx[a] for a in OFFENSIVE_ASSETS]
    def_indices = [asset_idx[a] for a in DEFENSIVE_RISK_ASSETS]
    cash_idx = asset_idx["CASHX"]

    signal_weights = np.zeros((len(dates), n_assets))
    for mi in range(13, n_months):
        di = month_ends_arr[mi]
        can = canary_scores[mi]
        offensive_mode = np.isfinite(can).all() and bool((can > 0).all())
        if offensive_mode:
            row = off_scores[mi]
            valid = np.isfinite(row)
            order = np.argsort(np.where(valid, row, -np.inf))[::-1]
            chosen = [off_indices[j] for j in order[:6] if valid[j]]
            if chosen:
                for ci in chosen:
                    signal_weights[di, ci] = 1.0 / len(chosen)
            else:
                signal_weights[di, cash_idx] = 1.0
        else:
            row = def_scores[mi]
            valid = np.isfinite(row)
            order = np.argsort(np.where(valid, row, -np.inf))[::-1]
            chosen = [j for j in order[:3] if valid[j]]
            cash_mom = cash_scores[mi] if np.isfinite(cash_scores[mi]) else 0.0
            if chosen:
                for j in chosen:
                    target = def_indices[j] if row[j] >= cash_mom else cash_idx
                    signal_weights[di, target] += 1.0 / len(chosen)
            else:
                signal_weights[di, cash_idx] = 1.0

    filled = np.zeros_like(signal_weights)
    last = np.zeros(n_assets)
    for i in range(len(dates)):
        if signal_weights[i].sum() > 0:
            last = signal_weights[i].copy()
        filled[i] = last

    daily = np.diff(arr, axis=0) / np.where(arr[:-1] > 0, arr[:-1], np.nan)
    gross = np.nansum(filled[:-1] * daily, axis=1)
    first_signal = month_ends_arr[13]
    return gross[first_signal:]


def compute_equity(returns: pd.Series, start: float = 10_000.0) -> pd.Series:
    return (1.0 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict:
    eq = compute_equity(returns)
    return {
        "sharpe": float(sharpe(returns, periods_per_year=252)),
        "cagr": float(cagr(eq, periods_per_year=252)),
        "mdd": float(max_drawdown(eq)),
    }


def rolling_window_robustness(returns: pd.Series, window_days: int = 252 * 5, step_days: int = 252) -> tuple[int, float, int, list[float]]:
    sharpes = []
    for start in range(0, len(returns) - window_days + 1, step_days):
        window = returns.iloc[start:start + window_days].to_numpy()
        sigma = window.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(window.mean() / sigma * np.sqrt(252)))
    if not sharpes:
        return 0, 0.0, 0, []
    pct_pos = sum(s > 0 for s in sharpes) / len(sharpes)
    points = 5 if pct_pos >= 0.90 else 3 if pct_pos >= 0.75 else 1 if pct_pos >= 0.60 else 0
    return points, pct_pos, len(sharpes), sharpes


def gate_dsr(returns: pd.Series, n_trials: int) -> tuple[bool, float]:
    """G2: DSR/PSR p-value < 0.05. [advances_fin_ml, p.222-223]"""
    arr = returns.to_numpy()
    if len(arr) < 10:
        return False, 1.0
    if n_trials < 2:
        p_value = 1.0 - float(compute_psr(arr, benchmark=0.0))
        return p_value < 0.05, p_value
    result = compute_dsr(arr, n_trials=n_trials)
    return result.p_value < 0.05, float(result.p_value)


def gate_walk_forward_g3prime(returns: pd.Series, vtsim_returns: pd.Series) -> tuple[bool, bool, list[float], list[float], list[float]]:
    """G3/G3': WF 6/8, nominal MDD<25%, adapted MDD for stacked holdings."""
    n = len(returns)
    window_size = n // (WF_N_WINDOWS + 1)
    if window_size < 63:
        return False, False, [], [], []
    oos_returns, oos_mdds, ref_mdds = [], [], []
    for _, test_range in walk_forward_splits(n, window_size, window_size, window_size):
        idxs = list(test_range)
        oos = returns.iloc[idxs]
        oos_returns.append(float((1.0 + oos).prod() - 1.0))
        oos_mdds.append(float(max_drawdown(compute_equity(oos))))
        oos_dates = returns.index[idxs]
        ref = vtsim_returns.loc[oos_dates[0]:oos_dates[-1]].dropna()
        ref_mdd = float(max_drawdown(compute_equity(ref))) if len(ref) > 5 else 0.50
        ref_mdds.append(ref_mdd * NOTIONAL_FACTOR)
        if len(oos_returns) >= WF_N_WINDOWS:
            break
    if len(oos_returns) < WF_N_WINDOWS:
        return False, False, oos_returns, oos_mdds, ref_mdds
    n_profitable = sum(r > 0 for r in oos_returns)
    nominal = n_profitable >= 6 and all(m <= 0.25 for m in oos_mdds)
    adapted = n_profitable >= 6 and all(m <= r for m, r in zip(oos_mdds, ref_mdds))
    return nominal, adapted, oos_returns, oos_mdds, ref_mdds


def gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    oos = returns.iloc[int(len(returns) * 0.70):]
    if len(oos) < 63:
        return False, 0.0
    value = float(sharpe(oos, periods_per_year=252))
    return value > 0, value


def gate_fwd_stress(returns: pd.Series, fwd_start: str = "2020-01-01") -> tuple[bool, float]:
    fwd = returns[returns.index >= fwd_start]
    if len(fwd) < 63:
        return False, 0.0
    value = float(sharpe(fwd, periods_per_year=252))
    return value > 0, value


def gate_bootstrap(returns: pd.Series) -> tuple[bool, float]:
    """G6: block-bootstrap 99.9% CI low > 0. [advances_fin_ml, p.196-202]"""
    arr = returns.to_numpy()
    if len(arr) < 252:
        return False, 0.0
    rng = np.random.default_rng(42)
    block_size = 21
    n_blocks = len(arr) // block_size
    sharpes = []
    for _ in range(BOOTSTRAP_N):
        starts = rng.integers(0, len(arr) - block_size + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block_size] for s in starts])[:len(arr)]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    if not sharpes:
        return False, 0.0
    ci_low = float(np.percentile(sharpes, 0.1))
    return ci_low > 0, ci_low


def gate_crosslib(prices: pd.DataFrame, pandas_gross_cagr: float) -> tuple[bool, float, float]:
    """G7: numpy reference gross CAGR within ±3pp. [advances_fin_ml, p.31-34]"""
    np_rets = simulate_baa_g12_numpy(prices)
    if len(np_rets) < 252:
        return False, 0.0, pandas_gross_cagr
    np_eq = (1.0 + np_rets).cumprod() * 10_000.0
    np_cagr = float((np_eq[-1] / np_eq[0]) ** (252 / (len(np_rets) - 1)) - 1.0)
    diff_pp = abs(np_cagr - pandas_gross_cagr) * 100.0
    return diff_pp <= 3.0, np_cagr, pandas_gross_cagr


def run_dataset(ds_name: str, prices_full: pd.DataFrame) -> dict:
    cfg = DATASETS[ds_name]
    prices = prices_full.loc[cfg["start"]:cfg["end"], RAW_TICKERS].dropna(how="all")
    benchmark_ret = prices[cfg["benchmark"]].pct_change().dropna()
    benchmark_metrics = metrics_from_returns(benchmark_ret)
    print(f"\n{'=' * 60}")
    print(f"Dataset: {ds_name} [{cfg['label']}]")
    print(f"  Period: {prices.index[0].date()} -> {prices.index[-1].date()}")
    print(f"  Benchmark {cfg['benchmark']}: S={benchmark_metrics['sharpe']:.4f} C={benchmark_metrics['cagr']:.2%} MDD={benchmark_metrics['mdd']:.2%}")

    net_ret, gross_ret, weights, tax_summary = simulate_baa_g12_net(prices)
    metrics = metrics_from_returns(net_ret)
    gross_metrics = metrics_from_returns(gross_ret)
    print(f"  BAA-G12 net:   S={metrics['sharpe']:.4f} C={metrics['cagr']:.2%} MDD={metrics['mdd']:.2%}")
    print(f"  BAA-G12 gross: S={gross_metrics['sharpe']:.4f} C={gross_metrics['cagr']:.2%} MDD={gross_metrics['mdd']:.2%}")

    g1_pass = True
    g2_pass, g2_p = gate_dsr(net_ret, N_CONFIGS)
    vtsim_ret = prices["VTSIM"].pct_change().dropna()
    g3_nominal, g3_prime, wf_rets, wf_mdds, ref_mdds = gate_walk_forward_g3prime(net_ret, vtsim_ret)
    g3_pass = g3_prime
    g4_pass, g4_sharpe = gate_oos_70_30(net_ret)
    g5_pass, g5_sharpe = gate_fwd_stress(net_ret)
    g6_pass, g6_ci_low = gate_bootstrap(net_ret)
    g7_pass, np_cagr, pd_gross_cagr = gate_crosslib(prices, gross_metrics["cagr"])
    gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass, g5_pass, g6_pass, g7_pass])

    print(f"  G1 PBO: single config < {MIN_HONEST_N_CONFIGS} -> PASS")
    print(f"  G2 DSR: p={g2_p:.2e} -> {'PASS' if g2_pass else 'FAIL'}")
    print(f"  G3/G3': {sum(r > 0 for r in wf_rets)}/{len(wf_rets)} profitable, max_mdd={max(wf_mdds) if wf_mdds else 0:.2%}, adapted_ref={max(ref_mdds) if ref_mdds else 0:.2%} -> {'PASS' if g3_pass else 'FAIL'}")
    print(f"  G4 OOS: S={g4_sharpe:.4f} -> {'PASS' if g4_pass else 'FAIL'}")
    print(f"  G5 FWD: S={g5_sharpe:.4f} -> {'PASS' if g5_pass else 'FAIL'}")
    print(f"  G6 Bootstrap: CI_low={g6_ci_low:.4f} -> {'PASS' if g6_pass else 'FAIL'}")
    print(f"  G7 Cross-lib gross: np={np_cagr:.2%} pd={pd_gross_cagr:.2%} -> {'PASS' if g7_pass else 'FAIL'}")
    print(f"  Gates: {gates_passed}/7")

    return {
        "dataset": ds_name,
        "config": CFG_ID,
        "metrics": metrics,
        "gross_metrics": gross_metrics,
        "benchmark": {"ticker": cfg["benchmark"], **benchmark_metrics},
        "tax_summary": tax_summary,
        "gates": {
            "g1_pbo": g1_pass,
            "g2_dsr": g2_pass,
            "g3_wf": g3_pass,
            "g4_oos": g4_pass,
            "g5_fwd": g5_pass,
            "g6_bootstrap": g6_pass,
            "g7_crosslib": g7_pass,
            "n_passed": gates_passed,
            "g3_nominal_pass": g3_nominal,
            "g3_prime_pass": g3_prime,
            "notional_factor": NOTIONAL_FACTOR,
        },
        "gate_details": {
            "g1_note": f"single pre-committed config < MIN_HONEST_N_CONFIGS={MIN_HONEST_N_CONFIGS}",
            "g2_dsr_p": g2_p,
            "g3_wf_returns": wf_rets,
            "g3_wf_mdds": wf_mdds,
            "g3_ref_mdds": ref_mdds,
            "g4_oos_sharpe": g4_sharpe,
            "g5_fwd_sharpe": g5_sharpe,
            "g6_ci_low": g6_ci_low,
            "g7_np_cagr": np_cagr,
            "g7_pd_gross_cagr": pd_gross_cagr,
        },
        "returns_series": {
            CFG_ID: {
                "index": [str(d.date()) for d in net_ret.index],
                "net_returns": [float(x) for x in net_ret],
            }
        },
    }


def main() -> None:
    print("Loading testfolio cache...")
    raw = load_testfolio_frame(REPO_ROOT / "data/testfolio/cache/history.parquet")
    missing = [ticker for ticker in RAW_TICKERS if ticker not in raw.columns]
    if missing:
        raise RuntimeError(f"Missing testfolio tickers: {missing}")
    results = {ds: run_dataset(ds, raw) for ds in ["educational", "vt_real", "ndx_real"]}

    metrics = {
        ds: DatasetMetrics(
            sharpe=results[ds]["metrics"]["sharpe"],
            cagr=results[ds]["metrics"]["cagr"],
            mdd=results[ds]["metrics"]["mdd"],
            dsr_p_value=results[ds]["gate_details"]["g2_dsr_p"],
        )
        for ds in results
    }
    gates = {
        ds: Gates(
            g1_pbo=results[ds]["gates"]["g1_pbo"],
            g2_dsr=results[ds]["gates"]["g2_dsr"],
            g3_wf=results[ds]["gates"]["g3_wf"],
            g4_oos=results[ds]["gates"]["g4_oos"],
            g5_fwd=results[ds]["gates"]["g5_fwd"],
            g6_bootstrap=results[ds]["gates"]["g6_bootstrap"],
            g7_crosslib=results[ds]["gates"]["g7_crosslib"],
        )
        for ds in results
    }
    rb_points, rb_pct, rb_n, rb_sharpes = rolling_window_robustness(pd.Series(results["educational"]["returns_series"][CFG_ID]["net_returns"]))
    score = score_strategy(metrics, gates, cumulative_n_trials=N_CONFIGS, robustness_bonus=rb_points)
    verdict = score.to_dict()
    verdict.update({
        "status": score.tier.value.lower(),
        "configs_tested": N_CONFIGS,
        "primary_citation": "[stocks_on_the_move, ch.6]",
        "hypothesis_slug": "baa-g12-balanced",
        "robustness": {"points": rb_points, "pct_positive": rb_pct, "n_windows": rb_n, "sharpes": rb_sharpes},
    })

    output = {
        "config": {
            "cfg_id": CFG_ID,
            "canary_assets": CANARY_ASSETS,
            "offensive_assets": OFFENSIVE_ASSETS,
            "defensive_assets": DEFENSIVE_ASSETS,
            "n_configs": N_CONFIGS,
            "tax_model": "AnnualDarfEngine",
        },
        "runs": {
            ds: {
                CFG_ID: {
                    "sharpe": results[ds]["metrics"]["sharpe"],
                    "cagr": results[ds]["metrics"]["cagr"],
                    "mdd": results[ds]["metrics"]["mdd"],
                }
            }
            for ds in results
        },
        "datasets": results,
        "returns_series": {ds: results[ds]["returns_series"] for ds in results},
        "score": verdict,
    }
    (ITER_DIR / "results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    (ITER_DIR / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    print(f"\nScore: {score.total_score}/100 {score.tier.value} winner={score.winner_conditions_met}")
    print(f"Wrote {(ITER_DIR / 'results.json').relative_to(REPO_ROOT)}")
    print(f"Wrote {(ITER_DIR / 'verdict.json').relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
