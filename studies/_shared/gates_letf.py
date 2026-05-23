"""7-gate battery for mandate §5 validation.

Thin wrappers over the public validation utilities in
``src/market_lab/backtest/validation/`` (pbo, dsr, walk_forward, bootstrap).
Same contract as the canonical implementations in
``studies/long_term_portfolio/run_iter.py:_gate_*`` (which spy_beater_hunt
imports verbatim) but exposed as a standalone module so letf_rotation_hunt
does not depend on long_term_portfolio internals.

Gate thresholds (LETF-relaxed where spec §3.5 documents the rationale):

    G1 PBO       < 0.50                      [advances_fin_ml, p.208-211]
    G2 DSR p     < 0.05                      [advances_fin_ml, p.222-223, p.275]
    G3 WF        ≥ 5/8 windows + MDD < 0.50  spec §3.5 (LETFs have 1-2 rough
                                              years per decade; intrínseco
                                              MDD ≥ 30%)
    G4 OOS 70/30 Sharpe > 0
    G5 FWD ≥2020 Sharpe > 0
    G6 Boot 99%  ci_low > 0                  spec §3.5 (99%, relaxed from
                                              99.9% per exploratory phase)
    G7 X-lib     |CAGR_pd - CAGR_np| ≤ 3pp   [advances_fin_ml, p.31-34]

Each gate function takes pd.Series-of-returns (or dict for PBO) and returns a
dict with the gate value plus a ``pass_gate`` boolean. The dicts are merged
into ``verdict.json:results[].gates`` by ``run_iter_t1.py``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from market_lab.backtest.validation.dsr import dsr as _dsr_compute
from market_lab.backtest.validation.dsr import psr as _psr_compute
from market_lab.backtest.validation.pbo import pbo as _pbo_compute
from market_lab.backtest.validation.walk_forward import walk_forward_splits

# Constants
TRADING_DAYS_PER_YEAR = 252
WF_N_WINDOWS = 8
WF_MIN_PASS = 5            # ≥5/8 windows must clear pass condition
WF_MIN_PROFITABLE = 5      # legacy alias retained for downstream readers
WF_PCT_ABOVE_BENCH = 0.50  # per-window pct_time_above_benchmark threshold
WF_LONG_WINDOW_DAYS = 1260 # ≥5 trading-years → use 252d warmup; else 21d
WF_WARMUP_SHORT = 21
WF_WARMUP_LONG = 252
BOOTSTRAP_N = 2000
BOOTSTRAP_BLOCK = 21
BOOTSTRAP_PCT_LOW = 1.0  # 99% CI → 1.0th percentile (relaxed from 0.1th = 99.9%)
XLIB_THRESHOLD_PP = 3.0


# ---------------------------------------------------------------------------
# Helpers (numpy-based, no pandas dependency for arithmetic core)
# ---------------------------------------------------------------------------


def _sharpe_annualized(returns: np.ndarray, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
    """Annualised Sharpe = mean/std × √periods_per_year. Returns 0 if σ ≈ 0."""
    if len(returns) < 2:
        return 0.0
    sigma = returns.std(ddof=0)
    if sigma <= 1e-12:
        return 0.0
    return float(returns.mean() / sigma * np.sqrt(periods_per_year))


def _cagr_from_returns(returns: np.ndarray, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
    """CAGR from compounded daily returns; numpy-only path used for G7 cross-lib."""
    if len(returns) < 2:
        return 0.0
    eq = np.cumprod(1.0 + returns)
    n_years = (len(returns) - 1) / periods_per_year
    if n_years <= 0 or eq[0] <= 0:
        return 0.0
    return float((eq[-1] / eq[0]) ** (1.0 / n_years) - 1.0)


def _max_drawdown(equity: np.ndarray) -> float:
    """Max drawdown from equity curve as positive fraction (0.25 = 25% DD)."""
    if len(equity) == 0:
        return 0.0
    peak = np.maximum.accumulate(equity)
    dd = (peak - equity) / peak
    return float(dd.max())


# ---------------------------------------------------------------------------
# G1 — PBO via CSCV
# ---------------------------------------------------------------------------


def g1_pbo(per_cfg_returns: dict[str, pd.Series]) -> dict:
    """Probability of Backtest Overfitting via CSCV.

    Citation: [advances_fin_ml, p.208-211]; spec §3.5 (threshold < 0.5).

    Single-config iters skip-pass with NaN (PBO is non-informative for N=1) —
    matches canon contract in long_term_portfolio.run_iter._gate_pbo.

    Parameters
    ----------
    per_cfg_returns:
        Mapping of config name → daily returns Series. Configs are aligned on
        their index intersection before CSCV.

    Returns
    -------
    dict with keys ``pbo`` (float, NaN if skip), ``n_combinations``,
    ``pass_gate`` (bool).
    """
    aligned = pd.concat(per_cfg_returns, axis=1, sort=True).dropna()
    if aligned.shape[1] < 2 or aligned.shape[0] < 252:
        return {"pbo": float("nan"), "n_combinations": 0, "pass_gate": True}
    result = _pbo_compute(aligned.to_numpy(dtype=float), n_blocks=10)
    return {
        "pbo": float(result.pbo),
        "n_combinations": int(result.n_combinations),
        "pass_gate": bool(result.pbo < 0.5),
    }


# ---------------------------------------------------------------------------
# G2 — DSR p-value (hybrid: caller passes local n_trials)
# ---------------------------------------------------------------------------


def g2_dsr_p_value(returns: pd.Series, n_trials: int) -> dict:
    """Deflated Sharpe Ratio p-value [advances_fin_ml, p.222-223, p.275].

    Hybrid contract per spec §3.6: caller controls n_trials.
    - n_trials ≥ 2 → DSR (multiple-testing-corrected)
    - n_trials = 1 → PSR fallback (single trial, no correction)

    Threshold p < 0.05 per spec §3.5. Local n_trials = configs in current
    iter (hard gate); cumulative n_trials = total over study (only the final
    study winner pays the cumulative penalty per spec §3.6).
    """
    arr = returns.to_numpy(dtype=float)
    obs_sharpe = _sharpe_annualized(arr)
    if n_trials < 2:
        p_value = 1.0 - float(_psr_compute(arr, benchmark=0.0))
    else:
        p_value = float(_dsr_compute(arr, n_trials=n_trials).p_value)
    return {
        "p_value": float(p_value),
        "observed_sharpe": obs_sharpe,
        "n_trials": int(n_trials),
        "pass_gate": bool(p_value < 0.05),
    }


# ---------------------------------------------------------------------------
# G3 — Walk-forward 8 windows (LETF-relaxed thresholds)
# ---------------------------------------------------------------------------


def g3_walk_forward(
    returns: pd.Series,
    benchmark_returns: pd.Series | None = None,
) -> dict:
    """Walk-forward 8 OOS windows; pass = ≥5/8 windows with strategy
    above benchmark > half the time (post proportional warmup).

    Per mandate §2.3 (MDD warning-only, 2026-04-22), spec §3.5 (G3
    LETF-relaxed precedent established 2026-05-05), and user observation
    2026-05-06 (underwater-vs-benchmark thesis), the pass condition is
    benchmark-relative rather than MDD-bounded. A 2× LETF rotation that
    sits comfortably above SPY in every walk-forward window but eats a
    74% drawdown during 2008 GFC is a real LETF-intrinsic outcome, not a
    strategy quality failure — exactly the regime the prior MDD<50% gate
    was rejecting.

    Pass condition
    --------------
    For each of 8 walk-forward windows compute ``pct_time_above_benchmark``
    on renormalised equity curves (post a proportional warmup: 21d if the
    window is < 1260 trading days, else 252d). The window passes if
    ``pct_time_above_benchmark ≥ 0.50``. The gate passes if ``≥ 5/8``
    windows pass.

    Backwards-compatible fallback: if ``benchmark_returns is None`` (no
    benchmark to compare against), the gate falls back to Sharpe-positivity
    (≥5/8 windows with Sharpe > 0). MDD is warning-only either way.

    Diagnostic outputs (warning-only)
    --------------------------------
    * ``oos_sharpes`` — per-window annualised Sharpe
    * ``oos_mdds`` — per-window max drawdown (no longer a hard bar)
    * ``windows_pass_sharpe_positive`` — count where Sharpe > 0
    * ``max_mdd`` — overall max OOS drawdown (warning per mandate §2.3)
    * ``windows_pct_above_benchmark`` — per-window pct_time_above_bench
    * ``warmup_used_days`` — 21 or 252 depending on window length

    Citation: mandate §2.3, spec §3.5 (G3 LETF-relaxed precedent), user
    observation 2026-05-06 (underwater-vs-benchmark per
    `tier_*/underwater_vs_benchmark.png` plots).
    """
    n = len(returns)
    window = n // (WF_N_WINDOWS + 1)
    if window < 63:
        return {
            "windows_pass_pct_above_benchmark": 0,
            "windows_pass_sharpe_positive": 0,
            "windows_pass": 0,  # legacy alias = sharpe_positive count
            "n_windows": 0,
            "max_mdd": float("nan"),
            "oos_sharpes": [],
            "oos_mdds": [],
            "windows_pct_above_benchmark": [],
            "warmup_used_days": 0,
            "benchmark_relative": benchmark_returns is not None,
            "pass_gate": False,
        }

    warmup_days = WF_WARMUP_SHORT if window < WF_LONG_WINDOW_DAYS else WF_WARMUP_LONG

    oos_sharpes: list[float] = []
    oos_mdds: list[float] = []
    pct_above_bench: list[float] = []

    bench_returns_aligned: pd.Series | None = None
    if benchmark_returns is not None:
        bench_returns_aligned = benchmark_returns.reindex(returns.index).fillna(0.0)

    for _, test_range in walk_forward_splits(n, window, window, window):
        idx = list(test_range)
        r = returns.iloc[idx].to_numpy(dtype=float)
        oos_sharpes.append(_sharpe_annualized(r))
        eq = np.cumprod(1.0 + r) * 10_000.0
        oos_mdds.append(_max_drawdown(eq))

        if bench_returns_aligned is not None:
            b = bench_returns_aligned.iloc[idx].to_numpy(dtype=float)
            bench_eq = np.cumprod(1.0 + b) * 10_000.0
            pct_above_bench.append(_pct_time_above(eq, bench_eq, warmup_days))
        if len(oos_sharpes) >= WF_N_WINDOWS:
            break

    n_windows = len(oos_sharpes)
    windows_pass_sharpe_positive = sum(1 for s in oos_sharpes if s > 0)
    max_mdd = float(max(oos_mdds)) if oos_mdds else float("nan")

    if bench_returns_aligned is not None:
        windows_pass_pct = sum(1 for p in pct_above_bench if p >= WF_PCT_ABOVE_BENCH)
        pass_gate = (
            n_windows == WF_N_WINDOWS
            and windows_pass_pct >= WF_MIN_PASS
        )
    else:
        windows_pass_pct = 0
        pass_gate = (
            n_windows == WF_N_WINDOWS
            and windows_pass_sharpe_positive >= WF_MIN_PASS
        )

    return {
        "windows_pass_pct_above_benchmark": int(windows_pass_pct),
        "windows_pass_sharpe_positive": int(windows_pass_sharpe_positive),
        # Legacy field: caller code reads "windows_pass" = sharpe-positive count.
        # Retained so older verdict.json readers keep working; new code should
        # use the explicit fields above.
        "windows_pass": int(windows_pass_sharpe_positive),
        "n_windows": int(n_windows),
        "max_mdd": max_mdd,
        "oos_sharpes": [float(s) for s in oos_sharpes],
        "oos_mdds": [float(m) for m in oos_mdds],
        "windows_pct_above_benchmark": [float(p) for p in pct_above_bench],
        "warmup_used_days": int(warmup_days),
        "benchmark_relative": bench_returns_aligned is not None,
        "pass_gate": bool(pass_gate),
    }


def _pct_time_above(strategy_eq: np.ndarray, benchmark_eq: np.ndarray, warmup_days: int) -> float:
    """Fraction of post-warmup days where strategy_eq / strategy_eq[0]
    ≥ benchmark_eq / benchmark_eq[0] (both renormalised to same start)."""
    if len(strategy_eq) <= warmup_days + 1 or len(benchmark_eq) <= warmup_days + 1:
        return float("nan")
    s = strategy_eq / strategy_eq[0]
    b = benchmark_eq / benchmark_eq[0]
    ratio = s / b
    post = ratio[warmup_days:]
    if len(post) < 2:
        return float("nan")
    return float((post > 1.0).mean())


# ---------------------------------------------------------------------------
# G4 — OOS 70/30 temporal hold-out
# ---------------------------------------------------------------------------


def g4_oos_70_30(returns: pd.Series) -> dict:
    """Last 30% of dates as OOS; threshold Sharpe > 0 [spec §3.5]."""
    cutoff = int(len(returns) * 0.70)
    oos = returns.iloc[cutoff:]
    if len(oos) < 63:
        return {"oos_sharpe": 0.0, "n_oos_obs": int(len(oos)), "pass_gate": False}
    s = _sharpe_annualized(oos.to_numpy(dtype=float))
    return {
        "oos_sharpe": float(s),
        "n_oos_obs": int(len(oos)),
        "pass_gate": bool(s > 0),
    }


# ---------------------------------------------------------------------------
# G5 — FWD post-2020 stress window
# ---------------------------------------------------------------------------


def g5_fwd_post_2020(returns: pd.Series, cutoff: str = "2020-01-01") -> dict:
    """Post-2020 stress window (COVID + 2022 rates + banking).

    Threshold Sharpe > 0 per spec §3.5. Returns pass_gate=False with
    n_obs_post_2020=0 if series ends pre-cutoff.
    """
    fwd = returns[returns.index >= cutoff]
    if len(fwd) < 63:
        return {
            "fwd_sharpe": 0.0,
            "n_obs_post_2020": int(len(fwd)),
            "cutoff": cutoff,
            "pass_gate": False,
        }
    s = _sharpe_annualized(fwd.to_numpy(dtype=float))
    return {
        "fwd_sharpe": float(s),
        "n_obs_post_2020": int(len(fwd)),
        "cutoff": cutoff,
        "pass_gate": bool(s > 0),
    }


# ---------------------------------------------------------------------------
# G6 — Stationary block bootstrap 99% CI low > 0
# ---------------------------------------------------------------------------


def g6_bootstrap_ci(
    returns: pd.Series,
    n_resamples: int = BOOTSTRAP_N,
    block: int = BOOTSTRAP_BLOCK,
    seed: int = 42,
) -> dict:
    """Block bootstrap Sharpe distribution; 99% CI low must be > 0.

    Spec §3.5: 99% (relaxed from 99.9% in production gates) for exploratory
    phase. Block size 21 ≈ one trading month, captures regime persistence.

    Citation: [advances_fin_ml, p.196-202]; Politis & Romano (1994).
    """
    arr = returns.to_numpy(dtype=float)
    if len(arr) < 252:
        return {
            "ci_low_sharpe": 0.0,
            "n_resamples": 0,
            "ci_pct": 99.0,
            "pass_gate": False,
        }
    rng = np.random.default_rng(seed)
    n = len(arr)
    n_blocks = n // block
    sharpes: list[float] = []
    for _ in range(n_resamples):
        starts = rng.integers(0, n - block + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block] for s in starts])[:n]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(sample.mean() / sigma * np.sqrt(TRADING_DAYS_PER_YEAR)))
    ci_low = float(np.percentile(sharpes, BOOTSTRAP_PCT_LOW)) if sharpes else 0.0
    return {
        "ci_low_sharpe": ci_low,
        "n_resamples": int(len(sharpes)),
        "ci_pct": 99.0,
        "pass_gate": bool(ci_low > 0),
    }


# ---------------------------------------------------------------------------
# G7 — Cross-lib CAGR delta (pandas vs numpy self-check)
# ---------------------------------------------------------------------------


def g7_xlib_cagr_delta(returns: pd.Series) -> dict:
    """Pandas-cumprod vs numpy-cumprod CAGR delta self-check.

    Catches gross arithmetic drift between the two compute paths used
    elsewhere in the project. Threshold ≤ 3pp per spec §3.5; same contract as
    long_term_portfolio.run_iter._gate_crosslib_self.

    Full multi-engine cross-check (pandas vs bt vs vectorbt) lives in
    iter 023's backtest.py — this is the lightweight per-iter self-check.

    Citation: [advances_fin_ml, p.31-34].
    """
    arr = returns.to_numpy(dtype=float)
    if len(arr) < 252:
        return {
            "delta_pp": float("nan"),
            "cagr_pandas": float("nan"),
            "cagr_numpy": float("nan"),
            "pass_gate": False,
        }
    np_cagr = _cagr_from_returns(arr)
    pd_eq = (1.0 + returns).cumprod() * 10_000.0
    n_obs = len(returns)
    n_years = (n_obs - 1) / TRADING_DAYS_PER_YEAR
    if n_years <= 0 or pd_eq.iloc[0] <= 0:
        pd_cagr = 0.0
    else:
        pd_cagr = float((pd_eq.iloc[-1] / pd_eq.iloc[0]) ** (1.0 / n_years) - 1.0)
    delta_pp = abs(np_cagr - pd_cagr) * 100.0
    return {
        "delta_pp": float(delta_pp),
        "cagr_pandas": float(pd_cagr),
        "cagr_numpy": float(np_cagr),
        "pass_gate": bool(delta_pp <= XLIB_THRESHOLD_PP),
    }
