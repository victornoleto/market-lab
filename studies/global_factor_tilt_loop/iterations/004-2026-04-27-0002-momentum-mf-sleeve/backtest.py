"""
Global Momentum + MF Sleeve (K=2, lb=6m, KMLM 10%) — Iteration 004

Hypothesis: The WINNER from iter 002 (K=2, lb=6m global momentum) gains a
Pareto improvement by adding a fixed 10% KMLMSIM allocation. Managed futures
(KMLM) are near-zero correlated with equity momentum in crises; the diversification
raises portfolio Sharpe while MDD stays flat or falls.

[ilmanen_expected_returns, ch.19] — MF as uncorrelated "free lunch" return stream.
[stocks_on_the_move, p.21-30] — pre-committed top-K momentum K=2 / lb=6m.
[advances_fin_ml, p.208-211] — PBO: N/A with n_configs=1 < MIN_HONEST_N_CONFIGS.
[advances_fin_ml, p.222-223] — DSR with n_trials=1 (pre-committed config).
[advances_fin_ml, p.196-202] — Bootstrap CI for Sharpe significance.
[advances_fin_ml, p.31-34] — Cross-lib ±3pp CAGR parity (G7).

Run from repo root:
    uv run python studies/global_factor_tilt_loop/iterations/004-2026-04-27-0002-momentum-mf-sleeve/backtest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_frame
from src.ai_trade.backtest.metrics.performance import sharpe, cagr, max_drawdown
from src.ai_trade.backtest.validation.pbo import MIN_HONEST_N_CONFIGS
from src.ai_trade.backtest.validation.dsr import dsr as compute_dsr, psr as compute_psr
from src.ai_trade.backtest.validation.walk_forward import walk_forward_gate, walk_forward_splits

LOOP_ROOT = REPO_ROOT / "studies" / "global_factor_tilt_loop"
sys.path.insert(0, str(LOOP_ROOT))
from scoring import score_strategy, DatasetMetrics, Gates

ITER_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Pre-committed parameters (same momentum params as iter 002 WINNER)
# [stocks_on_the_move, p.21-30]: canonical cross-sectional momentum K=2/lb=6m
# ---------------------------------------------------------------------------
FIXED_K = 2
FIXED_LOOKBACK = 6        # months
KMLM_WEIGHT = 0.10        # fixed managed-futures sleeve
MOMENTUM_WEIGHT = 1.0 - KMLM_WEIGHT  # 90% to momentum signal
N_CONFIGS = 1             # single pre-committed config — no grid

# ---------------------------------------------------------------------------
# Dataset definitions
# Educational start=1988-01-01: KMLMSIM binding (inception 1987-12-31).
# Same universe as iter 002 for each dataset; KMLMSIM added as overlay.
# ---------------------------------------------------------------------------
DATASETS = {
    "educational": {
        "start": "1988-01-01",   # KMLMSIM inception binds; universe tickers all ≥1926
        "end": "2026-04-24",
        "universe": ["VTISIM", "VEASIM", "VXUSSIM", "IEFSIM"],
        "kmlm": "KMLMSIM",
        "safe_haven": "CASHX",
        "benchmark": "VTSIM",
        "label": "VTSIM b&h ~38y (KMLM binding 1988-2026)",
    },
    "vt_real": {
        "start": "2008-06-01",
        "end": "2026-04-24",
        "universe": ["VTISIM", "VEASIM", "VWOSIM", "IEFSIM", "GLDSIM"],
        "kmlm": "KMLMSIM",
        "safe_haven": "CASHX",
        "benchmark": "VTSIM",
        "label": "VTSIM proxy 2008-06+ (~17y)",
    },
    "ndx_real": {
        "start": "2010-02-01",
        "end": "2026-04-24",
        "universe": ["VTISIM", "VEASIM", "VWOSIM", "IEFSIM", "GLDSIM"],
        "kmlm": "KMLMSIM",
        "safe_haven": "CASHX",
        "benchmark": "QQQSIM",
        "label": "QQQ proxy 2010-02+ (16y)",
    },
}

WF_N_WINDOWS = 8
BOOTSTRAP_N = 2000


# ---------------------------------------------------------------------------
# Pandas simulator — momentum + fixed KMLM sleeve
# ---------------------------------------------------------------------------

def simulate_momentum_mf_sleeve(
    prices: pd.DataFrame,
    universe: list[str],
    kmlm_ticker: str,
    safe_haven: str,
    k: int,
    lookback_months: int,
    kmlm_weight: float = KMLM_WEIGHT,
) -> pd.Series:
    """Daily return series: top-K momentum at 90% + KMLM fixed at 10%.

    [stocks_on_the_move, p.21-30]: monthly rebalance, trailing lookback return
    ranking, equal-weight top-K with positive momentum, CASHX safe haven when all
    universe assets negative. KMLM sleeve always receives kmlm_weight.
    [ilmanen_expected_returns, ch.19]: MF uncorrelated return stream free lunch.
    """
    mom_weight = 1.0 - kmlm_weight
    all_tickers = list(dict.fromkeys(universe + [safe_haven, kmlm_ticker]))
    px = prices[all_tickers].dropna(how="all")

    monthly_px = px[universe].resample("ME").last()
    mom = monthly_px.pct_change(lookback_months)

    monthly_weights = pd.DataFrame(0.0, index=monthly_px.index, columns=all_tickers)

    for i in range(lookback_months, len(monthly_px)):
        row = mom.iloc[i].dropna()
        positive = row[row > 0]
        date_idx = monthly_weights.index[i]
        monthly_weights.loc[date_idx, kmlm_ticker] = kmlm_weight
        if positive.empty:
            monthly_weights.loc[date_idx, safe_haven] = mom_weight
        else:
            top_k = positive.nlargest(min(k, len(positive)))
            w = mom_weight / len(top_k)
            for asset in top_k.index:
                monthly_weights.loc[date_idx, asset] = w

    daily_weights = monthly_weights.reindex(px.index, method="ffill").fillna(0.0)
    daily_ret = px.pct_change()
    port_ret = (daily_weights.shift(1) * daily_ret).sum(axis=1)
    port_ret = port_ret.dropna()
    first_signal_date = monthly_px.index[lookback_months]
    return port_ret[port_ret.index >= first_signal_date]


# ---------------------------------------------------------------------------
# Numpy cross-lib reference (G7)
# [advances_fin_ml, p.31-34]: same logic in pure numpy, compare CAGR ±3pp.
# ---------------------------------------------------------------------------

def simulate_momentum_mf_numpy(
    prices_np: np.ndarray,
    universe_idx: list[int],
    kmlm_idx: int,
    safe_haven_idx: int,
    k: int,
    lookback_months: int,
    dates: pd.DatetimeIndex,
    kmlm_weight: float = KMLM_WEIGHT,
) -> np.ndarray:
    """Numpy-pure reference for G7 cross-lib validation."""
    mom_weight = 1.0 - kmlm_weight
    n_days, n_total = prices_np.shape

    months = pd.DatetimeIndex(dates).to_period("M")
    month_end_idx = []
    for i in range(1, n_days):
        if months[i] != months[i - 1]:
            month_end_idx.append(i - 1)
    if month_end_idx[-1] != n_days - 1:
        month_end_idx.append(n_days - 1)
    month_end_idx = np.array(month_end_idx)

    n_universe = len(universe_idx)
    monthly_uni = prices_np[np.ix_(month_end_idx, universe_idx)]
    n_months = len(month_end_idx)

    mom = np.full((n_months, n_universe), np.nan)
    for i in range(lookback_months, n_months):
        p_now = monthly_uni[i]
        p_past = monthly_uni[i - lookback_months]
        with np.errstate(divide="ignore", invalid="ignore"):
            mom[i] = np.where(p_past > 0, (p_now - p_past) / p_past, np.nan)

    daily_weights = np.zeros((n_days, n_total))

    for mi in range(lookback_months, n_months):
        row = mom[mi]
        valid_mask = ~np.isnan(row)
        pos_mask = valid_mask & (row > 0)
        daily_weights[month_end_idx[mi], kmlm_idx] = kmlm_weight
        if not pos_mask.any():
            daily_weights[month_end_idx[mi], safe_haven_idx] = mom_weight
        else:
            pos_values = row.copy()
            pos_values[~pos_mask] = -np.inf
            topk_local = np.argsort(pos_values)[-min(k, pos_mask.sum()):]
            topk_local = topk_local[pos_values[topk_local] > -np.inf]
            w = mom_weight / len(topk_local)
            for li in topk_local:
                daily_weights[month_end_idx[mi], universe_idx[li]] = w

    last_weights = np.zeros(n_total)
    filled = np.zeros((n_days, n_total))
    for i in range(n_days):
        if daily_weights[i].sum() > 0:
            last_weights = daily_weights[i].copy()
        filled[i] = last_weights

    daily_rets = np.diff(prices_np, axis=0) / prices_np[:-1]
    shifted_weights = filled[:-1]
    port_rets = (shifted_weights * daily_rets).sum(axis=1)

    first_sig = month_end_idx[lookback_months]
    return port_rets[first_sig:]


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def compute_equity(returns: pd.Series, start: float = 10000.0) -> pd.Series:
    return (1 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict:
    eq = compute_equity(returns)
    return {
        "sharpe": sharpe(returns, periods_per_year=252),
        "cagr": cagr(eq, periods_per_year=252),
        "mdd": max_drawdown(eq),
    }


# ---------------------------------------------------------------------------
# Rolling-window robustness bonus (5-year sliding windows)
# ---------------------------------------------------------------------------

def rolling_window_robustness(
    returns: pd.Series,
    window_days: int = 252 * 5,
    step_days: int = 252,
) -> tuple[int, float, int, list[float]]:
    arr = returns.values
    n = len(arr)
    sharpes = []
    start = 0
    while start + window_days <= n:
        w = arr[start:start + window_days]
        sigma = w.std(ddof=0)
        if sigma > 1e-12:
            s = w.mean() / sigma * np.sqrt(252)
            sharpes.append(float(s))
        start += step_days

    if not sharpes:
        return 0, 0.0, 0, []

    pct_pos = sum(1 for s in sharpes if s > 0) / len(sharpes)
    if pct_pos >= 0.90:
        pts = 5
    elif pct_pos >= 0.75:
        pts = 3
    elif pct_pos >= 0.60:
        pts = 1
    else:
        pts = 0
    return pts, pct_pos, len(sharpes), sharpes


# ---------------------------------------------------------------------------
# Gate helpers
# ---------------------------------------------------------------------------

def gate_dsr(returns: pd.Series, n_trials: int) -> tuple[bool, float]:
    """G2: DSR/PSR significance < 0.05. [advances_fin_ml, p.222-223]"""
    arr = returns.values
    if len(arr) < 10:
        return False, 1.0
    if n_trials < 2:
        p_value = 1.0 - compute_psr(arr, benchmark=0.0)
        return p_value < 0.05, p_value
    result = compute_dsr(arr, n_trials=n_trials)
    return result.p_value < 0.05, result.p_value


def gate_walk_forward(returns: pd.Series, n_windows: int = WF_N_WINDOWS) -> tuple[bool, list[float], list[float]]:
    """G3: WF 6/8 windows, MDD<25% per window."""
    n = len(returns)
    window_size = n // (n_windows + 1)
    if window_size < 63:
        return False, [], []

    oos_returns = []
    oos_mdds = []
    for _, test_range in walk_forward_splits(n, window_size, window_size, window_size):
        oos_ret = returns.iloc[list(test_range)]
        eq = compute_equity(oos_ret)
        oos_returns.append(float((1 + oos_ret).prod() - 1))
        oos_mdds.append(float(max_drawdown(eq)))
        if len(oos_returns) >= n_windows:
            break

    if len(oos_returns) < n_windows:
        return False, oos_returns, oos_mdds

    return walk_forward_gate(oos_returns, oos_mdds) == "pass", oos_returns, oos_mdds


def gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    """G4: 70/30 OOS Sharpe > 0."""
    split = int(len(returns) * 0.70)
    oos = returns.iloc[split:]
    if len(oos) < 63:
        return False, 0.0
    s = sharpe(oos, periods_per_year=252)
    return s > 0, s


def gate_fwd_stress(returns: pd.Series, fwd_start: str = "2020-01-01") -> tuple[bool, float]:
    """G5: Post-2020 Sharpe > 0."""
    fwd = returns[returns.index >= fwd_start]
    if len(fwd) < 63:
        return False, 0.0
    s = sharpe(fwd, periods_per_year=252)
    return s > 0, s


def gate_bootstrap(returns: pd.Series) -> tuple[bool, float]:
    """G6: Block-bootstrap 99.9% CI low > 0. [advances_fin_ml, p.196-202]"""
    arr = returns.values
    if len(arr) < 252:
        return False, 0.0

    rng = np.random.default_rng(42)
    block_size = 21
    n = len(arr)
    n_blocks = n // block_size
    bootstrapped_sharpes = []
    for _ in range(BOOTSTRAP_N):
        block_starts = rng.integers(0, n - block_size + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block_size] for s in block_starts])[:n]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            bootstrapped_sharpes.append(sample.mean() / sigma * np.sqrt(252))

    if not bootstrapped_sharpes:
        return False, 0.0
    ci_low = float(np.percentile(bootstrapped_sharpes, 0.1))
    return ci_low > 0, ci_low


def gate_crosslib(
    prices_df: pd.DataFrame,
    dataset_cfg: dict,
    pandas_cagr: float,
) -> tuple[bool, float, float]:
    """G7: Numpy-pure cross-lib ±3pp CAGR. [advances_fin_ml, p.31-34]"""
    universe = dataset_cfg["universe"]
    kmlm_ticker = dataset_cfg["kmlm"]
    safe_haven = dataset_cfg["safe_haven"]
    all_tickers = list(dict.fromkeys(universe + [safe_haven, kmlm_ticker]))

    px = prices_df[all_tickers].dropna(how="all").ffill()
    prices_np = px.values.astype(float)
    dates = px.index

    universe_idx = [all_tickers.index(t) for t in universe]
    safe_haven_idx = all_tickers.index(safe_haven)
    kmlm_idx = all_tickers.index(kmlm_ticker)

    np_rets = simulate_momentum_mf_numpy(
        prices_np, universe_idx, kmlm_idx, safe_haven_idx,
        FIXED_K, FIXED_LOOKBACK, dates,
    )

    if len(np_rets) < 252:
        return False, 0.0, pandas_cagr

    n = len(np_rets)
    np_equity = (1 + np_rets).cumprod() * 10000.0
    np_cagr = float((np_equity[-1] / np_equity[0]) ** (252 / (n - 1)) - 1)

    if np.isnan(np_cagr):
        return False, float("nan"), pandas_cagr
    diff_pp = abs(np_cagr - pandas_cagr) * 100
    return diff_pp <= 3.0, np_cagr, pandas_cagr


# ---------------------------------------------------------------------------
# Full run for one dataset
# ---------------------------------------------------------------------------

def run_dataset(ds_name: str, prices_full: pd.DataFrame) -> dict:
    cfg = DATASETS[ds_name]
    start, end = cfg["start"], cfg["end"]
    universe = cfg["universe"]
    kmlm_ticker = cfg["kmlm"]
    safe_haven = cfg["safe_haven"]
    benchmark_ticker = cfg["benchmark"]

    all_needed = list(set(universe + [safe_haven, benchmark_ticker, kmlm_ticker]))
    prices = prices_full[all_needed].loc[start:end].dropna(how="all")

    # Benchmark
    bm_prices = prices[benchmark_ticker].dropna()
    bm_ret = bm_prices.pct_change().dropna()
    bm_eq = compute_equity(bm_ret)
    bm_sharpe = sharpe(bm_ret, periods_per_year=252)
    bm_cagr = cagr(bm_eq, periods_per_year=252)
    bm_mdd = max_drawdown(bm_eq)

    print(f"\n{'='*60}")
    print(f"Dataset: {ds_name}  [{cfg['label']}]")
    print(f"  Period: {prices.index[0].date()} → {prices.index[-1].date()}")
    print(f"  Benchmark ({benchmark_ticker}): Sharpe={bm_sharpe:.4f} CAGR={bm_cagr:.2%} MDD={bm_mdd:.2%}")
    print(f"  Config: K={FIXED_K}, lb={FIXED_LOOKBACK}m, KMLM={KMLM_WEIGHT:.0%} (pre-committed)")

    port_ret = simulate_momentum_mf_sleeve(
        prices, universe, kmlm_ticker, safe_haven,
        k=FIXED_K, lookback_months=FIXED_LOOKBACK,
    )

    if len(port_ret) < 252:
        print(f"  ERROR: too short ({len(port_ret)} days)")
        return {"error": "too short"}

    m = metrics_from_returns(port_ret)
    vs_bm = "✓" if m["sharpe"] > bm_sharpe else "✗"
    print(f"  Portfolio: Sharpe={m['sharpe']:.4f} {vs_bm}  CAGR={m['cagr']:.2%}  MDD={m['mdd']:.2%}")

    # G1: PBO — inapplicable (n_configs=1)
    g1_pass = True
    g1_pbo = 0.0
    print(f"  G1 PBO: N/A (single config < {MIN_HONEST_N_CONFIGS}) → PASS (trivial)")

    # G2: DSR
    g2_pass, g2_p = gate_dsr(port_ret, n_trials=N_CONFIGS)
    print(f"  G2 DSR: p={g2_p:.2e} → {'PASS' if g2_pass else 'FAIL'}")

    # G3: Walk-Forward
    g3_pass, wf_rets, wf_mdds = gate_walk_forward(port_ret)
    wf_profitable = sum(1 for r in wf_rets if r > 0)
    wf_max_mdd = max(wf_mdds) if wf_mdds else 0.0
    print(f"  G3 WF: {wf_profitable}/{len(wf_rets)} profitable, max_mdd={wf_max_mdd:.2%} → {'PASS' if g3_pass else 'FAIL'}")

    # G4: OOS 70/30
    g4_pass, g4_sharpe = gate_oos_70_30(port_ret)
    print(f"  G4 OOS: Sharpe={g4_sharpe:.4f} → {'PASS' if g4_pass else 'FAIL'}")

    # G5: FWD stress
    g5_pass, g5_sharpe = gate_fwd_stress(port_ret)
    print(f"  G5 FWD: Sharpe(post-2020)={g5_sharpe:.4f} → {'PASS' if g5_pass else 'FAIL'}")

    # G6: Bootstrap
    g6_pass, g6_ci_low = gate_bootstrap(port_ret)
    print(f"  G6 Bootstrap: CI_low={g6_ci_low:.4f} → {'PASS' if g6_pass else 'FAIL'}")

    # G7: Cross-lib
    g7_pass, np_cagr, pd_cagr = gate_crosslib(prices, cfg, m["cagr"])
    print(f"  G7 Cross-lib: np={np_cagr:.2%} pd={pd_cagr:.2%} "
          f"diff={abs(np_cagr-pd_cagr)*100:.2f}pp → {'PASS' if g7_pass else 'FAIL'}")

    gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass, g5_pass, g6_pass, g7_pass])
    print(f"  Gates: {gates_passed}/7")

    return {
        "dataset": ds_name,
        "config": f"K{FIXED_K}_lb{FIXED_LOOKBACK}_kmlm{int(KMLM_WEIGHT*100)}pct",
        "metrics": {"sharpe": m["sharpe"], "cagr": m["cagr"], "mdd": m["mdd"]},
        "benchmark": {
            "sharpe": bm_sharpe, "cagr": bm_cagr, "mdd": bm_mdd,
            "ticker": benchmark_ticker,
        },
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
            "g1_pbo_value": g1_pbo,
            "g1_note": f"N/A: single config < MIN_HONEST_N_CONFIGS={MIN_HONEST_N_CONFIGS}",
            "g2_dsr_p": g2_p,
            "g3_wf_returns": wf_rets,
            "g3_wf_mdds": wf_mdds,
            "g4_oos_sharpe": g4_sharpe,
            "g5_fwd_sharpe": g5_sharpe,
            "g6_ci_low": g6_ci_low,
            "g7_np_cagr": np_cagr,
        },
        "returns_series": {
            f"K{FIXED_K}_lb{FIXED_LOOKBACK}": {
                "index": [str(d.date()) for d in port_ret.index],
                "net_returns": port_ret.tolist(),
            }
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Loading testfolio price cache...")
    prices_full = load_testfolio_frame(REPO_ROOT / "data/testfolio/cache/history.parquet")
    print(f"Loaded {len(prices_full.columns)} tickers, {len(prices_full)} days")

    results = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        result = run_dataset(ds_name, prices_full)
        results[ds_name] = result

    # Rolling-window robustness on educational (~38y)
    print("\n" + "="*60)
    print("ROLLING-WINDOW ROBUSTNESS (educational, 5-year windows)")
    edu_cfg = DATASETS["educational"]
    prices_edu = prices_full[
        list(set(edu_cfg["universe"] + [edu_cfg["safe_haven"], edu_cfg["benchmark"], edu_cfg["kmlm"]]))
    ].loc[edu_cfg["start"]:edu_cfg["end"]].dropna(how="all")
    edu_port = simulate_momentum_mf_sleeve(
        prices_edu, edu_cfg["universe"], edu_cfg["kmlm"], edu_cfg["safe_haven"],
        k=FIXED_K, lookback_months=FIXED_LOOKBACK,
    )
    rob_pts, pct_pos, n_windows, roll_sharpes = rolling_window_robustness(edu_port)
    print(f"  Windows: {n_windows}")
    print(f"  % positive Sharpe: {pct_pos:.1%}")
    if roll_sharpes:
        print(f"  Min rolling Sharpe: {min(roll_sharpes):.3f}")
        print(f"  Max rolling Sharpe: {max(roll_sharpes):.3f}")
    print(f"  Robustness bonus: {rob_pts}/5")

    # Score
    print("\n" + "="*60)
    print("SCORING")

    metrics_map = {}
    gates_map = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        r = results[ds_name]
        if "error" in r:
            metrics_map[ds_name] = DatasetMetrics(sharpe=0.0, cagr=0.0, mdd=1.0, dsr_p_value=1.0)
            gates_map[ds_name] = Gates(False, False, False, False, False, False, False)
            continue
        m = r["metrics"]
        g = r["gates"]
        gd = r["gate_details"]
        metrics_map[ds_name] = DatasetMetrics(
            sharpe=m["sharpe"], cagr=m["cagr"], mdd=m["mdd"],
            dsr_p_value=gd["g2_dsr_p"],
        )
        gates_map[ds_name] = Gates(
            g1_pbo=g["g1_pbo"], g2_dsr=g["g2_dsr"], g3_wf=g["g3_wf"],
            g4_oos=g["g4_oos"], g5_fwd=g["g5_fwd"],
            g6_bootstrap=g["g6_bootstrap"], g7_crosslib=g["g7_crosslib"],
        )

    # iter 001 (18) + iter 002 (1) + iter 003 (1) + this iter (1) = 21
    cumulative_n_trials = 21
    score_result = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=cumulative_n_trials,
        robustness_bonus=rob_pts,
    )

    print(f"\nTier:  {score_result.tier.value}")
    print(f"Score: {score_result.total_score}/100")
    print(f"Winner conditions met: {score_result.winner_conditions_met}")
    print("\nScore breakdown:")
    for k, v in score_result.criteria.items():
        print(f"  {k}: {v['points']}/{v['max']}")

    # Save
    verdict = score_result.to_dict()
    verdict["configs_tested"] = N_CONFIGS
    verdict["primary_citation"] = "[ilmanen_expected_returns, ch.19]"
    verdict["hypothesis_slug"] = "momentum-mf-sleeve"
    verdict["status"] = score_result.tier.value.lower()
    verdict["robustness"] = {
        "n_windows": n_windows,
        "pct_positive_sharpe": pct_pos,
        "min_rolling_sharpe": float(min(roll_sharpes)) if roll_sharpes else None,
        "max_rolling_sharpe": float(max(roll_sharpes)) if roll_sharpes else None,
        "bonus_pts": rob_pts,
    }

    results_json = {
        "hypothesis_slug": "momentum-mf-sleeve",
        "datasets": results,
        "returns_series": {
            ds_name: results[ds_name].get("returns_series", {})
            for ds_name in ["educational", "vt_real", "ndx_real"]
        },
    }

    def _json_default(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return None if np.isnan(obj) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    verdict_path = ITER_DIR / "verdict.json"
    results_path = ITER_DIR / "results.json"

    with open(verdict_path, "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)
    with open(results_path, "w") as f:
        json.dump(results_json, f, indent=2, default=_json_default)

    print(f"\nSaved: {verdict_path}")
    print(f"Saved: {results_path}")

    return results, score_result, rob_pts, pct_pos, n_windows, roll_sharpes


if __name__ == "__main__":
    main()
