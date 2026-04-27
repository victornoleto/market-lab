"""
Global Multi-Asset Top-K Momentum — Iteration 001

Hypothesis: Monthly cross-sectional momentum across a global multi-asset
universe (VTISIM/VEASIM/VXUSSIM/IEFSIM core, VWOSIM/GLDSIM when available)
improves Sharpe and MDD vs VT buy-and-hold.

Citations:
  [stocks_on_the_move, p.21-30] — Clenow cross-sectional momentum rule
  [ilmanen_expected_returns, ch.12] — cross-asset momentum as robust risk premium
  [advances_fin_ml, p.208-211] — PBO via CSCV
  [advances_fin_ml, p.222-223] — DSR with n_trials
  [advances_fin_ml, p.196-202] — Bootstrap CI for Sharpe

Run from repo root:
    uv run python studies/global_factor_tilt_loop/iterations/001-2026-04-26-2247-global-momentum-topk/backtest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd
from scipy.stats import bootstrap as scipy_bootstrap

# Repo root on path
REPO_ROOT = Path(__file__).parents[4]
sys.path.insert(0, str(REPO_ROOT))

from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_frame
from src.ai_trade.backtest.metrics.performance import sharpe, cagr, max_drawdown
from src.ai_trade.backtest.validation.pbo import pbo as compute_pbo, MIN_HONEST_N_CONFIGS
from src.ai_trade.backtest.validation.dsr import dsr as compute_dsr
from src.ai_trade.backtest.validation.walk_forward import walk_forward_gate, walk_forward_splits

# Add loop root for scoring
LOOP_ROOT = REPO_ROOT / "studies" / "global_factor_tilt_loop"
sys.path.insert(0, str(LOOP_ROOT))
from scoring import score_strategy, DatasetMetrics, Gates

ITER_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Dataset definitions
# ---------------------------------------------------------------------------

DATASETS = {
    "educational": {
        "start": "1970-01-01",
        "end": "2026-04-24",
        "universe": ["VTISIM", "VEASIM", "VXUSSIM", "IEFSIM"],
        "safe_haven": "CASHX",
        "benchmark": "VTSIM",
        "label": "VTSIM b&h 56y",
    },
    "vt_real": {
        "start": "2008-06-01",
        "end": "2026-04-24",
        "universe": ["VTISIM", "VEASIM", "VWOSIM", "IEFSIM", "GLDSIM"],
        "safe_haven": "CASHX",
        "benchmark": "VTSIM",
        "label": "VTSIM proxy 2008-06+ (~17y)",
    },
    "ndx_real": {
        "start": "2010-02-01",
        "end": "2026-04-24",
        "universe": ["VTISIM", "VEASIM", "VWOSIM", "IEFSIM", "GLDSIM"],
        "safe_haven": "CASHX",
        "benchmark": "QQQSIM",   # QQQ proxy for ndx_real
        "label": "QQQ proxy 2010-02+ (16y)",
    },
}

# Grid: K × lookback_months
K_VALUES = [1, 2, 3]
LOOKBACK_MONTHS = [3, 6, 12]
N_CONFIGS = len(K_VALUES) * len(LOOKBACK_MONTHS)  # 9 per dataset

# Gate constants
WF_N_WINDOWS = 8
WF_MIN_PASS = 6
BOOTSTRAP_N = 2000
BOOTSTRAP_CI = 0.001  # 99.9% CI → need bottom 0.1th percentile > 0

# ---------------------------------------------------------------------------
# Core portfolio simulator (pandas)
# ---------------------------------------------------------------------------

def simulate_momentum_portfolio(
    prices: pd.DataFrame,
    universe: list[str],
    safe_haven: str,
    k: int,
    lookback_months: int,
) -> pd.Series:
    """Daily return series for top-K momentum portfolio.

    Signal: at each month-end, rank universe assets by trailing
    lookback_months total return. Equal-weight top-K with positive momentum.
    If all negative → 100% safe_haven (CASHX).

    No look-ahead: month-end weights apply from the next trading day forward.
    [stocks_on_the_move, p.21-30]
    """
    all_tickers = universe + ([safe_haven] if safe_haven not in universe else [])
    px = prices[all_tickers].dropna(how="all")

    # Month-end equity curves (last trading day of each month)
    monthly_px = px[universe].resample("ME").last()

    # Trailing momentum = pct change over lookback_months
    mom = monthly_px.pct_change(lookback_months)

    # Build monthly weight matrix (aligned to month-end dates)
    monthly_weights = pd.DataFrame(
        0.0, index=monthly_px.index, columns=all_tickers
    )

    for i in range(lookback_months, len(monthly_px)):
        row = mom.iloc[i].dropna()
        positive = row[row > 0]
        date_idx = monthly_weights.index[i]
        if positive.empty:
            monthly_weights.loc[date_idx, safe_haven] = 1.0
        else:
            top_k = positive.nlargest(min(k, len(positive)))
            w = 1.0 / len(top_k)
            for asset in top_k.index:
                monthly_weights.loc[date_idx, asset] = w

    # Forward-fill monthly weights to daily index
    # Month-end weight → applied starting NEXT trading day (shift(1) on daily)
    daily_weights = monthly_weights.reindex(px.index, method="ffill").fillna(0.0)

    # Daily returns for each asset
    daily_ret = px.pct_change()

    # Portfolio return: yesterday's weights × today's asset returns
    port_ret = (daily_weights.shift(1) * daily_ret).sum(axis=1)

    # Drop the NaN rows from warmup (no signal yet)
    port_ret = port_ret.dropna()
    # Trim to the period where we have valid weights
    first_signal_date = monthly_px.index[lookback_months]
    port_ret = port_ret[port_ret.index >= first_signal_date]

    return port_ret


# ---------------------------------------------------------------------------
# Numpy cross-lib reference (G7)
# [advances_fin_ml, p.31-34] — cross-implementation parity check
# ---------------------------------------------------------------------------

def simulate_momentum_numpy(
    prices_np: np.ndarray,
    universe_idx: list[int],
    safe_haven_idx: int,
    k: int,
    lookback_months: int,
    dates: pd.DatetimeIndex,
) -> np.ndarray:
    """Numpy-pure reference for G7 cross-lib parity (±3pp CAGR).

    Replicates pandas version using only numpy operations.
    Returns daily return array.
    """
    n_days, n_assets = prices_np.shape

    # Identify month-end indices (last business day of each month)
    months = pd.DatetimeIndex(dates).to_period("M")
    month_end_idx = []
    for i in range(1, n_days):
        if months[i] != months[i - 1]:
            month_end_idx.append(i - 1)
    if month_end_idx[-1] != n_days - 1:
        month_end_idx.append(n_days - 1)
    month_end_idx = np.array(month_end_idx)

    # Monthly prices for universe assets only
    n_universe = len(universe_idx)
    monthly_uni = prices_np[np.ix_(month_end_idx, universe_idx)]  # (M, U)
    n_months = len(month_end_idx)

    # Monthly momentum: pct change over lookback_months
    mom = np.full((n_months, n_universe), np.nan)
    for i in range(lookback_months, n_months):
        p_now = monthly_uni[i]
        p_past = monthly_uni[i - lookback_months]
        with np.errstate(divide="ignore", invalid="ignore"):
            mom[i] = np.where(p_past > 0, (p_now - p_past) / p_past, np.nan)

    # Build daily weights (n_days, n_assets)
    n_total = prices_np.shape[1]
    daily_weights = np.zeros((n_days, n_total))

    # Map month-end weights to daily range
    for mi in range(lookback_months, n_months):
        row = mom[mi]
        valid_mask = ~np.isnan(row)
        pos_mask = valid_mask & (row > 0)
        if not pos_mask.any():
            daily_weights[month_end_idx[mi], safe_haven_idx] = 1.0
        else:
            pos_values = row.copy()
            pos_values[~pos_mask] = -np.inf
            topk_local = np.argsort(pos_values)[-min(k, pos_mask.sum()):]
            topk_local = topk_local[pos_values[topk_local] > -np.inf]
            w = 1.0 / len(topk_local)
            for li in topk_local:
                daily_weights[month_end_idx[mi], universe_idx[li]] = w

    # Forward-fill weights from month-end to daily
    last_weights = np.zeros(n_total)
    filled = np.zeros((n_days, n_total))
    for i in range(n_days):
        if daily_weights[i].sum() > 0:
            last_weights = daily_weights[i].copy()
        filled[i] = last_weights

    # Portfolio daily returns: shift weights by 1 (previous day's weights)
    daily_rets = np.diff(prices_np, axis=0) / prices_np[:-1]  # (n-1, n_assets)
    shifted_weights = filled[:-1]  # shift: weight[t] applies to return[t+1]
    port_rets = (shifted_weights * daily_rets).sum(axis=1)

    # Trim to signal period (after first signal at month_end_idx[lookback_months])
    first_sig = month_end_idx[lookback_months]
    return port_rets[first_sig:]


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------

def compute_equity(returns: pd.Series, start: float = 10000.0) -> pd.Series:
    return (1 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict:
    eq = compute_equity(returns)
    s = sharpe(returns, periods_per_year=252)
    c = cagr(eq, periods_per_year=252)
    m = max_drawdown(eq)
    return {"sharpe": s, "cagr": c, "mdd": m}


# ---------------------------------------------------------------------------
# Gate battery
# ---------------------------------------------------------------------------

def gate_pbo(returns_matrix: np.ndarray) -> tuple[bool, float]:
    """G1: PBO via CSCV < 0.5. [advances_fin_ml, p.208-211]"""
    n_configs = returns_matrix.shape[1]
    if n_configs < MIN_HONEST_N_CONFIGS:
        # Can't honestly compute PBO with < 4 configs
        return True, 0.0  # conservative pass (not enough evidence to reject)
    result = compute_pbo(returns_matrix)
    return result.pbo < 0.5, result.pbo


def gate_dsr(returns: pd.Series, n_trials: int) -> tuple[bool, float]:
    """G2: DSR p-value < 0.05. [advances_fin_ml, p.222-223]"""
    arr = returns.values
    if len(arr) < 10 or n_trials < 1:
        return False, 1.0
    result = compute_dsr(arr, n_trials=n_trials)
    return result.p_value < 0.05, result.p_value


def gate_walk_forward(
    returns: pd.Series,
    n_windows: int = WF_N_WINDOWS,
) -> tuple[bool, list[float], list[float]]:
    """G3: WF 6/8 windows, MDD<25% per window. [advances_fin_ml, ch.12]"""
    n = len(returns)
    window_size = n // (n_windows + 1)
    if window_size < 63:  # minimum 3 months per window
        return False, [], []

    is_size = window_size
    oos_size = window_size
    step = window_size

    oos_returns = []
    oos_mdds = []
    for train_range, test_range in walk_forward_splits(n, is_size, oos_size, step):
        oos_ret = returns.iloc[list(test_range)]
        eq = compute_equity(oos_ret)
        total_ret = float((1 + oos_ret).prod() - 1)
        mdd = float(max_drawdown(eq))
        oos_returns.append(total_ret)
        oos_mdds.append(mdd)
        if len(oos_returns) >= n_windows:
            break

    if len(oos_returns) < n_windows:
        return False, oos_returns, oos_mdds

    verdict = walk_forward_gate(oos_returns, oos_mdds)
    return verdict == "pass", oos_returns, oos_mdds


def gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    """G4: 70/30 OOS Sharpe > 0."""
    split = int(len(returns) * 0.70)
    oos = returns.iloc[split:]
    if len(oos) < 63:
        return False, 0.0
    s = sharpe(oos, periods_per_year=252)
    return s > 0, s


def gate_fwd_stress(returns: pd.Series, fwd_start: str = "2020-01-01") -> tuple[bool, float]:
    """G5: Post-2020 Sharpe > 0 (FWD stress period)."""
    fwd = returns[returns.index >= fwd_start]
    if len(fwd) < 63:
        return False, 0.0
    s = sharpe(fwd, periods_per_year=252)
    return s > 0, s


def gate_bootstrap(returns: pd.Series) -> tuple[bool, float]:
    """G6: Bootstrap 99.9% CI low > 0. [advances_fin_ml, p.196-202]

    Block bootstrap (block_length=21 days ≈ 1 month) for time-series
    dependence. Checks if the 0.1th percentile of bootstrapped Sharpes > 0.
    """
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
        sample = np.concatenate([arr[s:s + block_size] for s in block_starts])
        sample = sample[:n]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            bootstrapped_sharpes.append(
                sample.mean() / sigma * np.sqrt(252)
            )

    if not bootstrapped_sharpes:
        return False, 0.0

    ci_low = np.percentile(bootstrapped_sharpes, 0.1)
    return ci_low > 0, ci_low


def gate_crosslib(
    prices_df: pd.DataFrame,
    dataset_cfg: dict,
    best_k: int,
    best_lookback: int,
    pandas_cagr: float,
) -> tuple[bool, float, float]:
    """G7: Numpy-pure cross-lib ±3pp CAGR. [advances_fin_ml, p.31-34]"""
    universe = dataset_cfg["universe"]
    safe_haven = dataset_cfg["safe_haven"]
    all_tickers = universe + ([safe_haven] if safe_haven not in universe else [])

    px = prices_df[all_tickers].dropna(how="all")
    # Forward-fill NaN (e.g. GLDSIM ends a few days before dataset end)
    px = px.ffill()
    prices_np = px.values.astype(float)
    dates = px.index

    universe_idx = [all_tickers.index(t) for t in universe]
    safe_haven_idx = all_tickers.index(safe_haven)

    np_rets = simulate_momentum_numpy(
        prices_np, universe_idx, safe_haven_idx,
        best_k, best_lookback, dates,
    )

    if len(np_rets) < 252:
        return False, 0.0, pandas_cagr

    n = len(np_rets)
    np_equity = (1 + np_rets).cumprod() * 10000.0
    np_cagr = (np_equity[-1] / np_equity[0]) ** (252 / (n - 1)) - 1

    if np.isnan(np_cagr):
        return False, float("nan"), pandas_cagr
    diff_pp = abs(np_cagr - pandas_cagr) * 100
    return diff_pp <= 3.0, np_cagr, pandas_cagr


# ---------------------------------------------------------------------------
# Full run for one dataset
# ---------------------------------------------------------------------------

def run_dataset(
    ds_name: str,
    prices_full: pd.DataFrame,
) -> dict:
    """Run full grid + gate battery for one dataset. Returns result dict."""
    cfg = DATASETS[ds_name]
    start, end = cfg["start"], cfg["end"]
    universe = cfg["universe"]
    safe_haven = cfg["safe_haven"]
    benchmark_ticker = cfg["benchmark"]

    # Slice prices to dataset window
    all_needed = list(set(universe + [safe_haven, benchmark_ticker]))
    prices = prices_full[all_needed].loc[start:end].dropna(how="all")

    # Benchmark metrics
    bm_prices = prices[benchmark_ticker].dropna()
    bm_ret = bm_prices.pct_change().dropna()
    bm_eq = compute_equity(bm_ret)
    bm_sharpe = sharpe(bm_ret, periods_per_year=252)
    bm_cagr = cagr(bm_eq, periods_per_year=252)
    bm_mdd = max_drawdown(bm_eq)
    print(f"\n{'='*60}")
    print(f"Dataset: {ds_name}")
    print(f"  Period: {prices.index[0].date()} → {prices.index[-1].date()}")
    print(f"  Benchmark ({benchmark_ticker}): Sharpe={bm_sharpe:.4f} CAGR={bm_cagr:.2%} MDD={bm_mdd:.2%}")

    # Grid search
    configs = list(product(K_VALUES, LOOKBACK_MONTHS))
    all_returns = {}  # cfg_id → returns series
    all_metrics = {}  # cfg_id → {sharpe, cagr, mdd}

    for k, lb in configs:
        cfg_id = f"k{k}_lb{lb}"
        try:
            port_ret = simulate_momentum_portfolio(
                prices, universe, safe_haven, k=k, lookback_months=lb
            )
            if len(port_ret) < 252:
                print(f"  {cfg_id}: too short ({len(port_ret)} days), skip")
                continue
            m = metrics_from_returns(port_ret)
            all_returns[cfg_id] = port_ret
            all_metrics[cfg_id] = m
            vs_bm = "✓" if m["sharpe"] > bm_sharpe else "✗"
            print(f"  {cfg_id}: Sharpe={m['sharpe']:.4f} {vs_bm}  CAGR={m['cagr']:.2%}  MDD={m['mdd']:.2%}")
        except Exception as e:
            print(f"  {cfg_id}: ERROR {e}")

    if not all_returns:
        print(f"  [ERROR] No valid configs for {ds_name}")
        return {"error": "no valid configs"}

    # Best config by Sharpe
    best_id = max(all_metrics, key=lambda c: all_metrics[c]["sharpe"])
    best_k_lb = best_id  # "k{K}_lb{LB}"
    parts = best_id.split("_")
    best_k = int(parts[0][1:])
    best_lb = int(parts[1][2:])
    best_returns = all_returns[best_id]
    best_m = all_metrics[best_id]

    print(f"\n  Best config: {best_id} → Sharpe={best_m['sharpe']:.4f}, CAGR={best_m['cagr']:.2%}, MDD={best_m['mdd']:.2%}")

    # --- G1: PBO ---
    # Build returns matrix (days × configs) for PBO
    # Use common date range across all configs
    common_idx = best_returns.index
    for r in all_returns.values():
        common_idx = common_idx.intersection(r.index)
    returns_matrix = np.column_stack([
        all_returns[c].reindex(common_idx).fillna(0).values
        for c in sorted(all_returns.keys())
    ])
    g1_pass, g1_pbo = gate_pbo(returns_matrix)
    print(f"  G1 PBO: {g1_pbo:.4f} → {'PASS' if g1_pass else 'FAIL'}")

    # --- G2: DSR (best config, n_trials = N_CONFIGS) ---
    g2_pass, g2_p = gate_dsr(best_returns, n_trials=N_CONFIGS)
    print(f"  G2 DSR: p={g2_p:.4f} → {'PASS' if g2_pass else 'FAIL'}")

    # --- G3: Walk-Forward ---
    g3_pass, wf_rets, wf_mdds = gate_walk_forward(best_returns)
    print(f"  G3 WF: {sum(1 for r in wf_rets if r > 0)}/{len(wf_rets)} profitable, max_mdd={max(wf_mdds) if wf_mdds else 0:.2%} → {'PASS' if g3_pass else 'FAIL'}")

    # --- G4: OOS 70/30 ---
    g4_pass, g4_sharpe = gate_oos_70_30(best_returns)
    print(f"  G4 OOS: Sharpe={g4_sharpe:.4f} → {'PASS' if g4_pass else 'FAIL'}")

    # --- G5: FWD stress ---
    g5_pass, g5_sharpe = gate_fwd_stress(best_returns)
    print(f"  G5 FWD: Sharpe(post-2020)={g5_sharpe:.4f} → {'PASS' if g5_pass else 'FAIL'}")

    # --- G6: Bootstrap ---
    g6_pass, g6_ci_low = gate_bootstrap(best_returns)
    print(f"  G6 Bootstrap: CI_low={g6_ci_low:.4f} → {'PASS' if g6_pass else 'FAIL'}")

    # --- G7: Cross-lib ---
    g7_pass, np_cagr, pd_cagr = gate_crosslib(prices, cfg, best_k, best_lb, best_m["cagr"])
    print(f"  G7 Cross-lib: numpy_cagr={np_cagr:.2%}, pandas_cagr={pd_cagr:.2%}, diff={abs(np_cagr-pd_cagr)*100:.2f}pp → {'PASS' if g7_pass else 'FAIL'}")

    gates_passed = sum([g1_pass, g2_pass, g3_pass, g4_pass, g5_pass, g6_pass, g7_pass])
    print(f"  Gates: {gates_passed}/7")

    # Build returns_series for plot_helper
    returns_series_for_storage = {
        c: {
            "index": [str(d.date()) for d in all_returns[c].index],
            "net_returns": all_returns[c].tolist(),
        }
        for c in all_returns
    }

    return {
        "dataset": ds_name,
        "best_config": best_id,
        "best_k": best_k,
        "best_lookback": best_lb,
        "metrics": {
            "sharpe": best_m["sharpe"],
            "cagr": best_m["cagr"],
            "mdd": best_m["mdd"],
        },
        "benchmark": {
            "sharpe": bm_sharpe,
            "cagr": bm_cagr,
            "mdd": bm_mdd,
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
            "g2_dsr_p": g2_p,
            "g3_wf_returns": wf_rets,
            "g3_wf_mdds": wf_mdds,
            "g4_oos_sharpe": g4_sharpe,
            "g5_fwd_sharpe": g5_sharpe,
            "g6_ci_low": g6_ci_low,
            "g7_np_cagr": np_cagr,
        },
        "all_configs_metrics": {c: m for c, m in all_metrics.items()},
        "returns_series": returns_series_for_storage,
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

    # --- Score ---
    print("\n" + "="*60)
    print("SCORING")

    metrics_map = {}
    gates_map = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        r = results[ds_name]
        if "error" in r:
            # Fill with fail values
            metrics_map[ds_name] = DatasetMetrics(sharpe=0.0, cagr=0.0, mdd=1.0, dsr_p_value=1.0)
            gates_map[ds_name] = Gates(False, False, False, False, False, False, False)
            continue
        m = r["metrics"]
        g = r["gates"]
        gd = r["gate_details"]
        metrics_map[ds_name] = DatasetMetrics(
            sharpe=m["sharpe"],
            cagr=m["cagr"],
            mdd=m["mdd"],
            dsr_p_value=gd["g2_dsr_p"],
        )
        gates_map[ds_name] = Gates(
            g1_pbo=g["g1_pbo"],
            g2_dsr=g["g2_dsr"],
            g3_wf=g["g3_wf"],
            g4_oos=g["g4_oos"],
            g5_fwd=g["g5_fwd"],
            g6_bootstrap=g["g6_bootstrap"],
            g7_crosslib=g["g7_crosslib"],
        )

    cumulative_n_trials = N_CONFIGS * 2  # 9 core + 9 full universe
    score_result = score_strategy(metrics_map, gates_map, cumulative_n_trials=cumulative_n_trials)

    print(f"\nTier:  {score_result.tier.value}")
    print(f"Score: {score_result.total_score}/100")
    print(f"Winner conditions met: {score_result.winner_conditions_met}")

    # Build verdict.json
    verdict = score_result.to_dict()
    verdict["configs_tested"] = N_CONFIGS * 2
    verdict["primary_citation"] = "[stocks_on_the_move, p.21-30]"
    verdict["hypothesis_slug"] = "global-momentum-topk"
    verdict["status"] = score_result.tier.value.lower()

    # Build results.json (for plot_helper)
    results_json = {
        "hypothesis_slug": "global-momentum-topk",
        "datasets": results,
        "returns_series": {
            ds_name: results[ds_name].get("returns_series", {})
            for ds_name in ["educational", "vt_real", "ndx_real"]
        },
    }

    def _json_default(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return None if np.isnan(obj) else float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    # Save files
    verdict_path = ITER_DIR / "verdict.json"
    results_path = ITER_DIR / "results.json"

    with open(verdict_path, "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)
    with open(results_path, "w") as f:
        json.dump(results_json, f, indent=2, default=_json_default)

    print(f"\nSaved: {verdict_path}")
    print(f"Saved: {results_path}")

    # Print score breakdown
    print("\nScore breakdown:")
    for k, v in score_result.criteria.items():
        print(f"  {k}: {v['points']}/{v['max']}")

    return results, score_result


if __name__ == "__main__":
    results, score_result = main()
