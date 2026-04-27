"""
User Static Portfolio + G3' Adapted Gate — Iteration 007

Hypothesis (pre-committed, USER_DIRECTIVE iter 007 from BASE_MEMORY):
  EXACT same 9-sleeve portfolio as iter 003 (capital-efficient-static).
  Only change: G3 nominal (MDD ≤ 25%) replaced by G3' adapted (benchmark-
  comparative MDD gate), to determine whether iter 003's STRONG 84 was
  caused by gate miscalibration vs genuine drawdown.

G3' rule (BASE_MEMORY §§ G3' adapted gate):
  notional_factor = 1.45
  ref_mdd = max(VT_window_MDD × notional_factor, V_HYBRID_MF_overall_MDD)
  g3_prime_pass = portfolio_window_MDD ≤ ref_mdd
  (applied per window; ≥ 6/8 windows profitable still required)

Portfolio weights (EXACT — do NOT modify):
  RSSB  25%  → RSSBSIM
  RSST  15%  → SPYSIM + KMLMSIM − CASHX
  AVUV  10%  → VBRSIM
  AVDV   7%  → VSSSIM
  AVEM   8%  → VWOSIM
  SPMO   8%  → SPYSIM
  IDMO   7%  → VEASIM
  GDE   12%  → GDESIM
  KMLM   8%  → KMLMSIM

n_configs = 1 → G1 PBO trivially passes, DSR uses PSR (n_trials=1).

Citations:
  [risk_parity, ch.5] — return stacking / capital efficiency (primary)
  [leverage_for_the_long_run, p.40-60] — stacking justification
  [advances_fin_ml, ch.10] — SCV empirical evidence (Fama-French)
  [ilmanen_expected_returns, ch.19] — MF "free lunch"
  [stocks_on_the_move, p.21-30] — momentum factor
  [advances_fin_ml, p.196-202] — G6 bootstrap CI
  [advances_fin_ml, p.208-211] — G1 PBO (N/A n_configs=1)
  [advances_fin_ml, p.222-223] — G2 DSR/PSR n_trials=1
  [advances_fin_ml, p.31-34]   — G7 cross-lib ±3pp CAGR
  [testing_tuning, ch.5-6]     — G3' benchmark-comparative calibration

Run from repo root:
    uv run python studies/global_factor_tilt_loop/iterations/007-2026-04-27-0851-user-static-g3prime/backtest.py
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
from src.ai_trade.backtest.validation.dsr import psr as compute_psr
from src.ai_trade.backtest.validation.walk_forward import walk_forward_splits

LOOP_ROOT = REPO_ROOT / "studies" / "global_factor_tilt_loop"
sys.path.insert(0, str(LOOP_ROOT))
from scoring import score_strategy, DatasetMetrics, Gates, Benchmark, BENCHMARKS

ITER_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Fixed pre-committed weights (EXACT copy from iter 003 — DO NOT MODIFY)
# [risk_parity, ch.5]: return stacking via futures preserves 1× capital.
# ---------------------------------------------------------------------------

PORTFOLIO_LEGS = {
    "RSSBSIM": 0.25,    # RSSB: global eq + Treasury stacked
    # RSST expanded below
    "VBRSIM":  0.10,    # AVUV: US SCV proxy [advances_fin_ml, ch.10]
    "VSSSIM":  0.07,    # AVDV: intl dev SCV proxy
    "VWOSIM":  0.08,    # AVEM: EM proxy
    "GDESIM":  0.12,    # GDE: 90% S&P + 90% gold
    "KMLMSIM": 0.08,    # KMLM: managed futures [ilmanen_expected_returns, ch.19]
}
RSST_WEIGHT = 0.15      # RSST = SPYSIM + KMLMSIM − CASHX overlay
SPMO_PROXY  = ("SPYSIM",  0.08)   # US momentum [stocks_on_the_move, p.21-30]
IDMO_PROXY  = ("VEASIM",  0.07)   # intl momentum

NOTIONAL_FACTOR = 1.45
# V_HYBRID+MF overall MDD used as floor in G3' ref_mdd computation.
# Conservative: if per-window V_HYBRID MDD data unavailable, 44.71% floor
# ensures fair comparison vs the strongest benchmark. [testing_tuning, ch.5-6]
V_HYBRID_MF_OVERALL_MDD = 0.4471

N_CONFIGS  = 1
BOOTSTRAP_N = 2000
WF_N_WINDOWS = 8

# ---------------------------------------------------------------------------
# Datasets (identical to iter 003)
# ---------------------------------------------------------------------------

DATASETS = {
    "educational": {
        "start": "1995-01-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM proxy 1995-2026 (~31y; VSSSIM/VWOSIM binding)",
    },
    "vt_real": {
        "start": "2008-06-01",
        "end": "2026-04-24",
        "benchmark": "VTSIM",
        "label": "VTSIM proxy 2008-06+ (~17y)",
    },
    "ndx_real": {
        "start": "2010-02-01",
        "end": "2026-04-24",
        "benchmark": "QQQSIM",
        "label": "QQQ proxy 2010-02+ (16y)",
    },
}


def _compute_eff_weights() -> dict[str, float]:
    eff: dict[str, float] = {}
    for t, w in PORTFOLIO_LEGS.items():
        eff[t] = eff.get(t, 0.0) + w
    eff["SPYSIM"]  = eff.get("SPYSIM", 0.0)  + RSST_WEIGHT
    eff["KMLMSIM"] = eff.get("KMLMSIM", 0.0) + RSST_WEIGHT
    eff["CASHX"]   = eff.get("CASHX", 0.0)   - RSST_WEIGHT
    eff[SPMO_PROXY[0]] = eff.get(SPMO_PROXY[0], 0.0) + SPMO_PROXY[1]
    eff[IDMO_PROXY[0]] = eff.get(IDMO_PROXY[0], 0.0) + IDMO_PROXY[1]
    return eff


EFF_WEIGHTS = _compute_eff_weights()

# ---------------------------------------------------------------------------
# Portfolio simulator (static monthly rebalance — unchanged from iter 003)
# ---------------------------------------------------------------------------


def build_portfolio_returns(prices: pd.DataFrame) -> pd.Series:
    """Static capital-efficient portfolio with monthly rebalance."""
    needed = list(dict.fromkeys(list(EFF_WEIGHTS)))
    px = prices[needed].dropna(how="all").ffill()
    daily_ret = px.pct_change()

    weight_df = pd.DataFrame(
        {t: w for t, w in EFF_WEIGHTS.items() if t in daily_ret.columns},
        index=daily_ret.index, dtype=float,
    )
    shifted = weight_df.shift(1).fillna(0.0)
    port_ret = (shifted * daily_ret[list(weight_df.columns)]).sum(axis=1).dropna()
    return port_ret.iloc[1:]


def build_portfolio_returns_numpy(
    prices: pd.DataFrame, eff_weights: dict[str, float],
) -> np.ndarray:
    """Numpy-pure reference for G7 cross-lib check. [advances_fin_ml, p.31-34]"""
    tickers = [t for t in eff_weights if t in prices.columns]
    weights = np.array([eff_weights[t] for t in tickers], dtype=float)
    px = prices[tickers].dropna(how="all").ffill().values.astype(float)
    daily_rets = np.diff(px, axis=0) / px[:-1]
    return (daily_rets * weights).sum(axis=1)[1:]


# ---------------------------------------------------------------------------
# Metrics helpers
# ---------------------------------------------------------------------------


def compute_equity(returns: pd.Series, start: float = 10000.0) -> pd.Series:
    return (1 + returns).cumprod() * start


def metrics_from_returns(returns: pd.Series) -> dict:
    eq = compute_equity(returns)
    return {
        "sharpe": sharpe(returns, periods_per_year=252),
        "cagr":   cagr(eq, periods_per_year=252),
        "mdd":    max_drawdown(eq),
    }


# ---------------------------------------------------------------------------
# Rolling robustness (5-year windows, educational)
# ---------------------------------------------------------------------------


def rolling_window_robustness(
    returns: pd.Series,
    window_days: int = 252 * 5,
    step_days:   int = 252,
) -> tuple[int, float, int, list[float]]:
    arr = returns.values
    n   = len(arr)
    sharpes, start = [], 0
    while start + window_days <= n:
        w = arr[start:start + window_days]
        sigma = w.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(w.mean() / sigma * np.sqrt(252)))
        start += step_days
    if not sharpes:
        return 0, 0.0, 0, []
    pct_pos = sum(1 for s in sharpes if s > 0) / len(sharpes)
    pts = 5 if pct_pos >= 0.90 else 3 if pct_pos >= 0.75 else 1 if pct_pos >= 0.60 else 0
    return pts, pct_pos, len(sharpes), sharpes


# ---------------------------------------------------------------------------
# Gate battery
# ---------------------------------------------------------------------------


def gate_dsr_psr(returns: pd.Series) -> tuple[bool, float]:
    """G2: PSR (n_trials=1). [advances_fin_ml, p.222-223]"""
    arr = returns.values
    if len(arr) < 10:
        return False, 1.0
    p_value = 1.0 - compute_psr(arr, benchmark=0.0)
    return p_value < 0.05, p_value


def gate_walk_forward_g3prime(
    returns: pd.Series,
    vtsim_returns: pd.Series,
    n_windows: int = WF_N_WINDOWS,
    notional_factor: float = NOTIONAL_FACTOR,
    hybrid_mf_floor: float = V_HYBRID_MF_OVERALL_MDD,
) -> tuple[bool, bool, list[float], list[float], list[float]]:
    """G3: WF 6/8 windows, dual check: nominal (MDD≤25%) and G3' adapted.

    G3' adapted formula (BASE_MEMORY §§ G3' rule):
      ref_mdd = max(VT_window_MDD * notional_factor, hybrid_mf_floor)
      pass = portfolio_window_MDD <= ref_mdd

    Both g3_nominal and g3_prime reported; gate uses g3_prime for stacked
    portfolios (notional_factor > 1.05). [testing_tuning, ch.5-6]
    """
    n = len(returns)
    window_size = n // (n_windows + 1)
    if window_size < 63:
        return False, False, [], [], []

    oos_returns, oos_mdds, ref_mdds = [], [], []

    for _, test_range in walk_forward_splits(n, window_size, window_size, window_size):
        idxs    = list(test_range)
        oos_ret = returns.iloc[idxs]
        eq      = compute_equity(oos_ret)
        oos_returns.append(float((1 + oos_ret).prod() - 1))
        port_mdd = float(max_drawdown(eq))
        oos_mdds.append(port_mdd)

        oos_dates = returns.index[idxs]
        vt_window = vtsim_returns.loc[oos_dates[0]:oos_dates[-1]].dropna()
        if len(vt_window) > 5:
            vt_eq  = compute_equity(vt_window)
            vt_mdd = float(max_drawdown(vt_eq))
        else:
            vt_mdd = 0.50  # conservative fallback
        ref_mdds.append(max(vt_mdd * notional_factor, hybrid_mf_floor))

        if len(oos_returns) >= n_windows:
            break

    if len(oos_returns) < n_windows:
        return False, False, oos_returns, oos_mdds, ref_mdds

    n_profitable = sum(1 for r in oos_returns if r > 0)
    g3_nominal   = (n_profitable >= 6) and all(m <= 0.25 for m in oos_mdds)
    g3_prime     = (n_profitable >= 6) and all(m <= r for m, r in zip(oos_mdds, ref_mdds))
    return g3_nominal, g3_prime, oos_returns, oos_mdds, ref_mdds


def gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    """G4: 70/30 OOS Sharpe > 0."""
    split = int(len(returns) * 0.70)
    oos   = returns.iloc[split:]
    if len(oos) < 63:
        return False, 0.0
    s = float(sharpe(oos, periods_per_year=252))
    return s > 0, s


def gate_fwd_stress(returns: pd.Series, fwd_start: str = "2020-01-01") -> tuple[bool, float]:
    """G5: Post-2020 Sharpe > 0."""
    fwd = returns[returns.index >= fwd_start]
    if len(fwd) < 63:
        return False, 0.0
    s = float(sharpe(fwd, periods_per_year=252))
    return s > 0, s


def gate_bootstrap(returns: pd.Series) -> tuple[bool, float]:
    """G6: Block-bootstrap 99.9% CI low > 0. [advances_fin_ml, p.196-202]"""
    arr = returns.values
    if len(arr) < 252:
        return False, 0.0
    rng        = np.random.default_rng(42)
    block_size = 21
    n          = len(arr)
    n_blocks   = n // block_size
    bootstrapped = []
    for _ in range(BOOTSTRAP_N):
        starts = rng.integers(0, n - block_size + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block_size] for s in starts])[:n]
        sigma  = sample.std(ddof=0)
        if sigma > 1e-12:
            bootstrapped.append(sample.mean() / sigma * np.sqrt(252))
    if not bootstrapped:
        return False, 0.0
    ci_low = float(np.percentile(bootstrapped, 0.1))
    return ci_low > 0, ci_low


def gate_crosslib(
    prices: pd.DataFrame,
    eff_weights: dict[str, float],
    pandas_cagr: float,
) -> tuple[bool, float, float]:
    """G7: Numpy-pure cross-lib ±3pp CAGR. [advances_fin_ml, p.31-34]"""
    np_rets = build_portfolio_returns_numpy(prices, eff_weights)
    if len(np_rets) < 252:
        return False, 0.0, pandas_cagr
    np_eq   = (1 + np_rets).cumprod() * 10000.0
    n       = len(np_rets)
    np_cagr = float((np_eq[-1] / np_eq[0]) ** (252 / (n - 1)) - 1)
    if np.isnan(np_cagr):
        return False, float("nan"), pandas_cagr
    diff_pp = abs(np_cagr - pandas_cagr) * 100
    return diff_pp <= 3.0, np_cagr, pandas_cagr


# ---------------------------------------------------------------------------
# Full dataset run
# ---------------------------------------------------------------------------


def run_dataset(ds_name: str, prices_full: pd.DataFrame) -> dict:
    cfg   = DATASETS[ds_name]
    start, end = cfg["start"], cfg["end"]
    bm_ticker  = cfg["benchmark"]

    needed = list(dict.fromkeys(list(EFF_WEIGHTS) + [bm_ticker, "VTSIM"]))
    prices = prices_full[needed].loc[start:end].dropna(how="all").ffill()

    bm_ret    = prices[bm_ticker].pct_change().dropna()
    bm_eq     = compute_equity(bm_ret)
    bm_sharpe = float(sharpe(bm_ret, periods_per_year=252))
    bm_cagr   = float(cagr(bm_eq, periods_per_year=252))
    bm_mdd    = float(max_drawdown(bm_eq))

    print(f"\n{'='*60}")
    print(f"Dataset: {ds_name}  [{cfg['label']}]")
    print(f"  Period: {prices.index[0].date()} → {prices.index[-1].date()}")
    print(f"  Benchmark ({bm_ticker}): S={bm_sharpe:.4f} CAGR={bm_cagr:.2%} MDD={bm_mdd:.2%}")

    port_ret = build_portfolio_returns(prices)
    if len(port_ret) < 252:
        print(f"  ERROR: too short ({len(port_ret)} days)")
        return {"error": "too short"}

    m = metrics_from_returns(port_ret)
    vs_bm = "✓" if m["sharpe"] > bm_sharpe else "✗"
    print(f"  Portfolio: S={m['sharpe']:.4f} {vs_bm}  CAGR={m['cagr']:.2%}  MDD={m['mdd']:.2%}")

    # G1: PBO — trivially N/A (n_configs=1)
    g1_pass = True
    print(f"  G1 PBO: N/A (n_configs=1 < {MIN_HONEST_N_CONFIGS}) → PASS (trivial)")

    # G2: DSR/PSR (n_trials=1)
    g2_pass, g2_p = gate_dsr_psr(port_ret)
    print(f"  G2 DSR/PSR: p={g2_p:.2e} → {'PASS' if g2_pass else 'FAIL'}")

    # G3: Walk-forward (G3 nominal + G3' adapted)
    vtsim_ret = prices["VTSIM"].pct_change().dropna()
    g3_nominal, g3_prime, wf_rets, wf_mdds, ref_mdds = gate_walk_forward_g3prime(
        port_ret, vtsim_ret,
    )
    n_profitable = sum(1 for r in wf_rets if r > 0)
    max_wf_mdd   = max(wf_mdds) if wf_mdds else 0.0
    max_ref_mdd  = max(ref_mdds) if ref_mdds else 0.0
    print(f"  G3 nominal: {n_profitable}/{len(wf_rets)} profitable, "
          f"max_mdd={max_wf_mdd:.2%} (threshold=25%) → {'PASS' if g3_nominal else 'FAIL'}")
    print(f"  G3' adapted: max_ref={max_ref_mdd:.2%} (VT×{NOTIONAL_FACTOR} "
          f"floor={V_HYBRID_MF_OVERALL_MDD:.2%}) → {'PASS' if g3_prime else 'FAIL'}")

    # Use G3' for stacked portfolio (notional_factor=1.45 > 1.05)
    g3_pass = g3_prime

    # G4: OOS 70/30
    g4_pass, g4_s = gate_oos_70_30(port_ret)
    print(f"  G4 OOS: S={g4_s:.4f} → {'PASS' if g4_pass else 'FAIL'}")

    # G5: FWD stress
    g5_pass, g5_s = gate_fwd_stress(port_ret)
    print(f"  G5 FWD(post-2020): S={g5_s:.4f} → {'PASS' if g5_pass else 'FAIL'}")

    # G6: Bootstrap
    g6_pass, g6_ci = gate_bootstrap(port_ret)
    print(f"  G6 Bootstrap: CI_low={g6_ci:.4f} → {'PASS' if g6_pass else 'FAIL'}")

    # G7: Cross-lib
    g7_pass, np_c, pd_c = gate_crosslib(prices, EFF_WEIGHTS, m["cagr"])
    print(f"  G7 Cross-lib: np={np_c:.2%} pd={pd_c:.2%} "
          f"diff={abs(np_c-pd_c)*100:.2f}pp → {'PASS' if g7_pass else 'FAIL'}")

    gates_n = sum([g1_pass, g2_pass, g3_pass, g4_pass, g5_pass, g6_pass, g7_pass])
    print(f"  Gates (with G3'): {gates_n}/7  "
          f"[G3 nominal would give: {sum([g1_pass,g2_pass,g3_nominal,g4_pass,g5_pass,g6_pass,g7_pass])}/7]")

    return {
        "dataset": ds_name,
        "config":  "user-static-g3prime",
        "metrics": {"sharpe": m["sharpe"], "cagr": m["cagr"], "mdd": m["mdd"]},
        "benchmark": {
            "sharpe": bm_sharpe, "cagr": bm_cagr, "mdd": bm_mdd, "ticker": bm_ticker,
        },
        "gates": {
            "g1_pbo":        g1_pass,
            "g2_dsr":        g2_pass,
            "g3_wf":         g3_pass,   # uses G3' for stacked
            "g4_oos":        g4_pass,
            "g5_fwd":        g5_pass,
            "g6_bootstrap":  g6_pass,
            "g7_crosslib":   g7_pass,
            "n_passed":      gates_n,
        },
        "gate_details": {
            "g1_note":            f"N/A: n_configs=1 < MIN_HONEST={MIN_HONEST_N_CONFIGS}",
            "g2_dsr_p":           g2_p,
            "g3_nominal_pass":    g3_nominal,
            "g3_prime_pass":      g3_prime,
            "notional_factor":    NOTIONAL_FACTOR,
            "g3_wf_returns":      wf_rets,
            "g3_wf_mdds":         wf_mdds,
            "g3_ref_mdds":        ref_mdds,
            "g3_max_wf_mdd":      max_wf_mdd,
            "g3_max_ref_mdd":     max_ref_mdd,
            "g4_oos_sharpe":      g4_s,
            "g5_fwd_sharpe":      g5_s,
            "g6_ci_low":          g6_ci,
            "g7_np_cagr":         np_c,
        },
        "returns_series": {
            "user-static-g3prime": {
                "index":       [str(d.date()) for d in port_ret.index],
                "net_returns": port_ret.tolist(),
            }
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Loading testfolio price cache...")
    prices_full = load_testfolio_frame(
        REPO_ROOT / "data/testfolio/cache/history.parquet"
    )
    print(f"Loaded {len(prices_full.columns)} tickers, {len(prices_full)} days")

    print("\nEffective weights:")
    for t, w in sorted(EFF_WEIGHTS.items(), key=lambda x: -abs(x[1])):
        print(f"  {t}: {w:+.2f}")

    results: dict[str, dict] = {}
    for ds_name in ["educational", "vt_real", "ndx_real"]:
        results[ds_name] = run_dataset(ds_name, prices_full)

    # Rolling robustness on educational
    print("\n" + "=" * 60)
    print("ROLLING-WINDOW ROBUSTNESS (educational, 5-year windows)")
    edu_cfg = DATASETS["educational"]
    needed  = list(dict.fromkeys(list(EFF_WEIGHTS) + [edu_cfg["benchmark"]]))
    p_edu   = prices_full[needed].loc[edu_cfg["start"]:edu_cfg["end"]].dropna(how="all").ffill()
    edu_ret = build_portfolio_returns(p_edu)
    rob_pts, pct_pos, n_win, roll_sharpes = rolling_window_robustness(edu_ret)
    print(f"  Windows:  {n_win}")
    print(f"  % pos:    {pct_pos:.1%}")
    if roll_sharpes:
        print(f"  Min Sharpe: {min(roll_sharpes):.3f}")
        print(f"  Max Sharpe: {max(roll_sharpes):.3f}")
    print(f"  Bonus pts: {rob_pts}/5")

    # Scoring — dynamic benchmark for educational (1995-2026 VTSIM)
    print("\n" + "=" * 60)
    print("SCORING")

    edu_vt = prices_full["VTSIM"].loc[edu_cfg["start"]:edu_cfg["end"]].dropna()
    edu_bm_ret = edu_vt.pct_change().dropna()
    edu_bm_eq  = compute_equity(edu_bm_ret)
    edu_s  = float(sharpe(edu_bm_ret, periods_per_year=252))
    edu_c  = float(cagr(edu_bm_eq, periods_per_year=252))
    edu_m  = float(max_drawdown(edu_bm_eq))
    print(f"  VTSIM(1995-2026): S={edu_s:.4f} CAGR={edu_c:.2%} MDD={edu_m:.2%}")

    custom_benchmarks = {
        "educational": Benchmark(
            sharpe=edu_s, cagr=edu_c, mdd=edu_m,
            label="VTSIM b&h 1995-2026 (~31y; VSSSIM/VWOSIM binding)",
        ),
        "vt_real":  BENCHMARKS["vt_real"],
        "ndx_real": BENCHMARKS["ndx_real"],
    }

    metrics_map: dict[str, DatasetMetrics] = {}
    gates_map:   dict[str, Gates]          = {}
    for ds in ["educational", "vt_real", "ndx_real"]:
        r = results[ds]
        if "error" in r:
            metrics_map[ds] = DatasetMetrics(0.0, 0.0, 1.0, dsr_p_value=1.0)
            gates_map[ds]   = Gates(False, False, False, False, False, False, False)
            continue
        m, g, gd = r["metrics"], r["gates"], r["gate_details"]
        metrics_map[ds] = DatasetMetrics(
            sharpe=m["sharpe"], cagr=m["cagr"], mdd=m["mdd"],
            dsr_p_value=gd["g2_dsr_p"],
        )
        gates_map[ds] = Gates(
            g1_pbo=g["g1_pbo"],       g2_dsr=g["g2_dsr"],
            g3_wf=g["g3_wf"],         g4_oos=g["g4_oos"],
            g5_fwd=g["g5_fwd"],       g6_bootstrap=g["g6_bootstrap"],
            g7_crosslib=g["g7_crosslib"],
        )

    cumulative_n_trials = 23 + N_CONFIGS  # 23 through iter 006, +1 this iter
    score_result = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=cumulative_n_trials,
        benchmarks=custom_benchmarks,
        robustness_bonus=rob_pts,
    )

    print(f"\nTier:  {score_result.tier.value}")
    print(f"Score: {score_result.total_score}/100")
    print(f"Winner conditions met: {score_result.winner_conditions_met}")
    print("\nScore breakdown:")
    for k, v in score_result.criteria.items():
        print(f"  {k}: {v['points']}/{v['max']}")

    # ---------------------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------------------

    def _json_default(obj):
        if isinstance(obj, np.integer):   return int(obj)
        if isinstance(obj, np.floating):  return None if np.isnan(obj) else float(obj)
        if isinstance(obj, np.ndarray):   return obj.tolist()
        return str(obj)

    verdict = score_result.to_dict()
    verdict.update({
        "configs_tested":        N_CONFIGS,
        "primary_citation":      "[risk_parity, ch.5]",
        "hypothesis_slug":       "user-static-g3prime",
        "status":                score_result.tier.value.lower(),
        "notional_factor":       NOTIONAL_FACTOR,
        "v_hybrid_mf_floor":     V_HYBRID_MF_OVERALL_MDD,
        "g3_gate_used":          "g3_prime",
        "educational_benchmark_note": (
            "Educational benchmark uses VTSIM(1995-2026) not VTSIM(56y) "
            "because VSSSIM/VWOSIM are binding constraints from 1994-12."
        ),
        "robustness": {
            "n_windows":            n_win,
            "pct_positive_sharpe":  pct_pos,
            "min_rolling_sharpe":   float(min(roll_sharpes)) if roll_sharpes else None,
            "max_rolling_sharpe":   float(max(roll_sharpes)) if roll_sharpes else None,
            "bonus_pts":            rob_pts,
        },
        "custom_benchmarks": {
            ds: {"sharpe": b.sharpe, "cagr": b.cagr, "mdd": b.mdd, "label": b.label}
            for ds, b in custom_benchmarks.items()
        },
    })

    results_json = {
        "hypothesis_slug": "user-static-g3prime",
        "datasets": results,
        "returns_series": {
            ds: results[ds].get("returns_series", {})
            for ds in ["educational", "vt_real", "ndx_real"]
        },
    }

    verdict_path  = ITER_DIR / "verdict.json"
    results_path  = ITER_DIR / "results.json"

    with open(verdict_path, "w") as f:
        json.dump(verdict, f, indent=2, default=_json_default)
    with open(results_path, "w") as f:
        json.dump(results_json, f, indent=2, default=_json_default)

    print(f"\nSaved: {verdict_path}")
    print(f"Saved: {results_path}")
    return results, score_result, rob_pts, pct_pos, n_win, roll_sharpes


if __name__ == "__main__":
    main()
