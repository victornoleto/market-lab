"""Composite Momentum Standard simulator for long_term_portfolio iter 002.

Rules:
- Monthly SPYSIM 200-day SMA regime filter.
- Risk-on: top 4 assets by 8-month return after positive absolute momentum.
- Sizing: inverse 63-day volatility.
- Risk-off: 60% IEFSIM + 40% GLDSIM.

Citations:
- Cross-sectional momentum / strongest-assets selection:
  [stocks_on_the_move, p.21-30]
- PBO / DSR / bootstrap / cross-lib validation:
  [advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(REPO_ROOT))

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame
from market_lab.backtest.metrics.performance import cagr, max_drawdown, sharpe
from market_lab.backtest.validation.dsr import dsr as compute_dsr
from market_lab.backtest.validation.dsr import psr as compute_psr
from market_lab.backtest.validation.pbo import MIN_HONEST_N_CONFIGS
from market_lab.backtest.validation.walk_forward import walk_forward_splits

GLOBAL_LOOP = REPO_ROOT / "studies" / "return_stacked_core" / "history" / "global_factor_tilt"
BESTFOLIO_LOOP = REPO_ROOT / "studies" / "return_stacked_core"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_tax_engine = _load_module("bestfolio_iter002_tax_engine_v2", GLOBAL_LOOP / "tax_engine_v2.py")
_scoring = _load_module("bestfolio_iter002_scoring", BESTFOLIO_LOOP / "scoring.py")
AnnualDarfEngine = _tax_engine.AnnualDarfEngine
DatasetMetrics = _scoring.DatasetMetrics
Gates = _scoring.Gates
score_strategy = _scoring.score_strategy

ITER_DIR = Path(__file__).parent

N_CONFIGS = 1
CFG_ID = "CMS_spy200_top4_8m_invvol63_def_ief60_gld40"
WF_N_WINDOWS = 8
BOOTSTRAP_N = 2000

RISK_ASSETS = ["SPYSIM", "QQQSIM", "VEASIM", "TLTSIM", "IEFSIM", "GLDSIM", "KMLMSIM"]
DEFENSIVE_ASSETS = ["IEFSIM", "GLDSIM"]
RAW_TICKERS = sorted(set(RISK_ASSETS + DEFENSIVE_ASSETS + ["VTSIM"]))

DATASETS = {
    "educational": {
        "start": "1988-01-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM synth; start constrained by KMLMSIM/QQQSIM history",
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


def _inverse_vol_weights(vols: pd.Series) -> pd.Series:
    vols = vols.replace([np.inf, -np.inf], np.nan).dropna()
    vols = vols[vols > 1e-12]
    if vols.empty:
        return vols
    inv = 1.0 / vols
    return inv / inv.sum()


def composite_monthly_weights(prices: pd.DataFrame) -> pd.DataFrame:
    """Build month-end Composite Momentum weights. [stocks_on_the_move, p.21-30]"""
    assets = sorted(set(RISK_ASSETS + DEFENSIVE_ASSETS))
    px = prices[assets].dropna(how="all")
    month_ends = px.resample("ME").last().index
    daily_returns = px.pct_change()
    weights = pd.DataFrame(0.0, index=month_ends, columns=assets)

    for date in month_ends:
        loc = px.index.searchsorted(date, side="right") - 1
        if loc < 200 or loc < 168:
            continue
        current_date = px.index[loc]
        spy = px["SPYSIM"].iloc[: loc + 1]
        spy_sma200 = spy.iloc[-200:].mean()
        risk_on = bool(spy.iloc[-1] > spy_sma200)

        if not risk_on:
            weights.loc[date, "IEFSIM"] = 0.60
            weights.loc[date, "GLDSIM"] = 0.40
            continue

        lookback = px.iloc[loc] / px.iloc[loc - 168] - 1.0
        candidates = lookback[RISK_ASSETS].replace([np.inf, -np.inf], np.nan).dropna()
        candidates = candidates[candidates > 0.0].nlargest(min(4, len(candidates)))
        if candidates.empty:
            weights.loc[date, "IEFSIM"] = 0.60
            weights.loc[date, "GLDSIM"] = 0.40
            continue

        vols = daily_returns[candidates.index].iloc[max(0, loc - 62): loc + 1].std(ddof=0)
        inv_weights = _inverse_vol_weights(vols)
        if inv_weights.empty:
            for asset in candidates.index:
                weights.loc[date, asset] = 1.0 / len(candidates)
        else:
            for asset, weight in inv_weights.items():
                weights.loc[date, asset] = float(weight)

    return weights


def simulate_composite_gross(prices: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """Return gross daily returns and daily target weights."""
    assets = sorted(set(RISK_ASSETS + DEFENSIVE_ASSETS))
    px = prices[assets].dropna(how="all")
    monthly_weights = composite_monthly_weights(px)
    daily_weights = monthly_weights.reindex(px.index, method="ffill").fillna(0.0)
    daily_ret = px.pct_change()
    gross = (daily_weights.shift(1) * daily_ret).sum(axis=1).dropna()
    active = daily_weights.sum(axis=1) > 0
    if not active.any():
        return gross.iloc[0:0], daily_weights
    first_signal = active[active].index[0]
    return gross[gross.index >= first_signal], daily_weights


def simulate_composite_net(prices: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.DataFrame, dict]:
    """Return AnnualDarfEngine net returns plus gross returns and weights."""
    gross, weights = simulate_composite_gross(prices)
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
            final_value = engine.port_value
            pre_settle_value = prev_value
            net_returns[-1] = (1.0 + net_returns[-1]) * (final_value / pre_settle_value) - 1.0

    net = pd.Series(net_returns, index=gross.index, name="net_returns")
    return net, gross, weights, engine.summary() | {"events": engine.events}


def simulate_composite_numpy(prices: pd.DataFrame) -> np.ndarray:
    """Numpy-pure gross-return reference for G7. [advances_fin_ml, p.31-34]"""
    assets = sorted(set(RISK_ASSETS + DEFENSIVE_ASSETS))
    px = prices[assets].dropna(how="all")
    arr = px.to_numpy(dtype=float)
    dates = px.index
    asset_idx = {asset: i for i, asset in enumerate(assets)}
    periods = dates.to_period("M")
    month_ends = [i - 1 for i in range(1, len(dates)) if periods[i] != periods[i - 1]]
    if not month_ends or month_ends[-1] != len(dates) - 1:
        month_ends.append(len(dates) - 1)

    signal_weights = np.zeros((len(dates), len(assets)))
    for di in month_ends:
        if di < 200 or di < 168:
            continue
        spy_col = asset_idx["SPYSIM"]
        spy_now = arr[di, spy_col]
        spy_sma = np.nanmean(arr[di - 199:di + 1, spy_col])
        risk_on = bool(np.isfinite(spy_now) and np.isfinite(spy_sma) and spy_now > spy_sma)
        if not risk_on:
            signal_weights[di, asset_idx["IEFSIM"]] = 0.60
            signal_weights[di, asset_idx["GLDSIM"]] = 0.40
            continue

        scores = []
        for asset in RISK_ASSETS:
            col = asset_idx[asset]
            old = arr[di - 168, col]
            now = arr[di, col]
            score = now / old - 1.0 if old > 0 else np.nan
            if np.isfinite(score) and score > 0:
                scores.append((score, asset))
        chosen = [asset for _, asset in sorted(scores, reverse=True)[:4]]
        if not chosen:
            signal_weights[di, asset_idx["IEFSIM"]] = 0.60
            signal_weights[di, asset_idx["GLDSIM"]] = 0.40
            continue

        vols = []
        daily_window = arr[di - 63:di + 1, :]
        returns_window = np.diff(daily_window, axis=0) / daily_window[:-1]
        for asset in chosen:
            col = asset_idx[asset]
            vol = np.nanstd(returns_window[:, col])
            vols.append(vol if np.isfinite(vol) and vol > 1e-12 else np.nan)
        vols_arr = np.array(vols, dtype=float)
        if np.isfinite(vols_arr).all():
            inv = 1.0 / vols_arr
            chosen_weights = inv / inv.sum()
        else:
            chosen_weights = np.full(len(chosen), 1.0 / len(chosen))
        for asset, weight in zip(chosen, chosen_weights):
            signal_weights[di, asset_idx[asset]] = float(weight)

    filled = np.zeros_like(signal_weights)
    last = np.zeros(len(assets))
    for i in range(len(dates)):
        if signal_weights[i].sum() > 0:
            last = signal_weights[i].copy()
        filled[i] = last

    daily = np.diff(arr, axis=0) / np.where(arr[:-1] > 0, arr[:-1], np.nan)
    gross = np.nansum(filled[:-1] * daily, axis=1)
    active = np.where(filled.sum(axis=1) > 0)[0]
    if len(active) == 0:
        return np.array([], dtype=float)
    return gross[active[0]:]


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


def gate_walk_forward(returns: pd.Series) -> tuple[bool, list[float], list[float]]:
    """G3: WF 6/8 windows and per-window MDD < 25%. [advances_fin_ml, p.31-34]"""
    n = len(returns)
    window_size = n // (WF_N_WINDOWS + 1)
    if window_size < 63:
        return False, [], []
    oos_returns, oos_mdds = [], []
    for _, test_range in walk_forward_splits(n, window_size, window_size, window_size):
        idxs = list(test_range)
        oos = returns.iloc[idxs]
        oos_returns.append(float((1.0 + oos).prod() - 1.0))
        oos_mdds.append(float(max_drawdown(compute_equity(oos))))
        if len(oos_returns) >= WF_N_WINDOWS:
            break
    if len(oos_returns) < WF_N_WINDOWS:
        return False, oos_returns, oos_mdds
    passed = sum(r > 0 for r in oos_returns) >= 6 and all(m <= 0.25 for m in oos_mdds)
    return passed, oos_returns, oos_mdds


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
    """G7: numpy reference gross CAGR within +/-3pp. [advances_fin_ml, p.31-34]"""
    np_rets = simulate_composite_numpy(prices)
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

    net_ret, gross_ret, weights, tax_summary = simulate_composite_net(prices)
    metrics = metrics_from_returns(net_ret)
    gross_metrics = metrics_from_returns(gross_ret)
    print(f"  CMS net:   S={metrics['sharpe']:.4f} C={metrics['cagr']:.2%} MDD={metrics['mdd']:.2%}")
    print(f"  CMS gross: S={gross_metrics['sharpe']:.4f} C={gross_metrics['cagr']:.2%} MDD={gross_metrics['mdd']:.2%}")

    g1_pass = True
    g2_pass, g2_p = gate_dsr(net_ret, N_CONFIGS)
    g3_pass, wf_rets, wf_mdds = gate_walk_forward(net_ret)
    g4_pass, g4_sharpe = gate_oos_70_30(net_ret)
    g5_pass, g5_sharpe = gate_fwd_stress(net_ret)
    g6_pass, g6_ci_low = gate_bootstrap(net_ret)
    g7_pass, np_cagr, pd_gross_cagr = gate_crosslib(prices, gross_metrics["cagr"])
    gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass, g5_pass, g6_pass, g7_pass])

    print(f"  G1 PBO: single config < {MIN_HONEST_N_CONFIGS} -> PASS")
    print(f"  G2 DSR: p={g2_p:.2e} -> {'PASS' if g2_pass else 'FAIL'}")
    print(f"  G3 WF: {sum(r > 0 for r in wf_rets)}/{len(wf_rets)} profitable, max_mdd={max(wf_mdds) if wf_mdds else 0:.2%} -> {'PASS' if g3_pass else 'FAIL'}")
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
        },
        "gate_details": {
            "g1_note": f"single pre-committed config < MIN_HONEST_N_CONFIGS={MIN_HONEST_N_CONFIGS}",
            "g2_dsr_p": g2_p,
            "g3_wf_returns": wf_rets,
            "g3_wf_mdds": wf_mdds,
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
    edu_returns = pd.Series(
        results["educational"]["returns_series"][CFG_ID]["net_returns"],
        index=pd.to_datetime(results["educational"]["returns_series"][CFG_ID]["index"]),
    )
    rb_points, rb_pct, rb_n, rb_sharpes = rolling_window_robustness(edu_returns)
    score = score_strategy(metrics, gates, cumulative_n_trials=2, robustness_bonus=rb_points)
    verdict = score.to_dict()
    verdict.update({
        "status": score.tier.value.lower(),
        "configs_tested": N_CONFIGS,
        "primary_citation": "[stocks_on_the_move, p.21-30]",
        "hypothesis_slug": "composite-momentum-standard",
        "robustness": {"points": rb_points, "pct_positive": rb_pct, "n_windows": rb_n, "sharpes": rb_sharpes},
    })

    output = {
        "config": {
            "cfg_id": CFG_ID,
            "risk_assets": RISK_ASSETS,
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
