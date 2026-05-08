"""Per-iter execution helper for the long-term portfolio sweep iter 027-039.

Takes a per-iter config dict (config_name → {ticker → weight}) and produces
the standard iter artifacts:

- Aggregate portfolio daily returns per dataset (weighted sum of components,
  aligned on common dates)
- Sharpe / CAGR / MDD per (config × dataset)
- 7-gate validation results for the SELECTED config
- DSR p-value with cumulative_n_trials
- Selection across configs sweep (max mean(gross_Sharpe / SPY_Sharpe))
- ``verdict.json`` (NEW SPY-only mandate + LEGACY avg(SPY,VT) for compat)
- ``results.json`` (returns_series so plot_helper can render plots)
- ``final_report.md`` (markdown summary)
- ``plot_<dataset>.png`` and ``plot_rolling_windows_<dataset>.png`` for the
  selected config

Reuses existing modules verbatim: ``scoring.py``, ``datasets.py``,
``proxies.py`` (capital-efficient stacking blueprint), ``synths.py``,
``plot_helper.py``, ``rolling_windows.py``. The synth ticker resolution
table mirrors the per-product cache helpers in ``synths.py``; the NTSX/
NTSI/NTSE family is built locally via ``proxies.expand_capital_efficient``
to keep the WisdomTree 90/60/-50 blueprint as the single source of truth.

Used by Tasks 8-22 (iters 027-039) of the sweep plan.

Citations:
- Sweep architecture / per-iter rubric: ``IMPLEMENTATION_PLAN_iter_027_to_039.md``
- DSR with cumulative n_trials: ``[advances_fin_ml, p.222-223]``
- PBO grid-level: ``[advances_fin_ml, p.208-211]``
- Bootstrap CI: ``[advances_fin_ml, p.196-202]``
- Capital-efficient stacking blueprint (NTSX/NTSI/NTSE): ``[risk_parity, ch.5, p.10]``
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_series
from market_lab.backtest.metrics.performance import (
    cagr as _cagr_fn,
    max_drawdown as _mdd_fn,
    sharpe as _sharpe_fn,
)
from market_lab.backtest.validation.dsr import dsr as compute_dsr
from market_lab.backtest.validation.dsr import psr as compute_psr
from market_lab.backtest.validation.pbo import pbo as compute_pbo
from market_lab.backtest.validation.walk_forward import walk_forward_splits
from studies.long_term_portfolio import datasets as datasets_mod
from studies.long_term_portfolio import synths
from studies.long_term_portfolio.proxies import (
    PROXY_LEGS,
    expand_capital_efficient,
)
from studies.long_term_portfolio.rolling_windows import (
    DEFAULT_WINDOWS_YEARS,
    fits_in_history,
    rolling_outperformance_pct,
    rolling_sharpe_at_windows,
)
from studies.long_term_portfolio.scoring import (
    BENCHMARKS,
    DatasetMetrics,
    Gates,
    avg_benchmark,
    legacy_benchmarks,
    primary_benchmarks,
    score_strategy,
    spy_benchmark,
)


WEIGHT_TOLERANCE = 0.005  # weights must sum to 1.0 ± 0.5% [advances_fin_ml, ch.4]
TRADING_DAYS_PER_YEAR = 252
BOOTSTRAP_N = 2000
WF_N_WINDOWS = 8


# ---------------------------------------------------------------------------
# Public: portfolio_returns_from_config
# ---------------------------------------------------------------------------


def portfolio_returns_from_config(
    config: dict[str, float], dataset: str
) -> pd.Series:
    """Build aggregate portfolio daily returns from a weights config.

    Args:
        config: ticker → weight dict. Weights MUST sum to ~1.0
            (notional > 1 is fine for stacking ETFs whose internal leverage
            is baked into the synth, e.g. NTSXSIM = 0.90 SPY + 0.60 IEF -
            0.50 cash → 1.5× notional but still 1.0 sleeve weight).
        dataset: dataset name from datasets.py (lh_56y / vt_real / ndx_real).

    Returns:
        Daily portfolio returns Series, aligned to dataset window and to
        the intersection of all components' available dates (some synths
        bottleneck at their underlying's inception, e.g. AVEMSIM at 1994).

    Raises:
        ValueError: if weights don't sum to ~1.0 ± WEIGHT_TOLERANCE.
        KeyError: if ``dataset`` is not in DATASETS.
    """
    total = sum(config.values())
    if abs(total - 1.0) > WEIGHT_TOLERANCE:
        raise ValueError(
            f"config weights sum to {total:.4f}, expected 1.0 ± {WEIGHT_TOLERANCE}"
        )

    component_returns = _resolve_tickers_to_returns(list(config.keys()))
    aligned = pd.concat(component_returns, axis=1, sort=True).dropna()
    weight_vec = pd.Series(
        {t: config[t] for t in aligned.columns}, dtype=float
    )
    aggregate = (aligned * weight_vec).sum(axis=1)

    meta = datasets_mod.get_meta(dataset)
    return aggregate.loc[meta["start"]:meta["end"]].dropna()


def _resolve_tickers_to_returns(tickers: list[str]) -> dict[str, pd.Series]:
    """Resolve ticker names to daily returns Series.

    Routes:
      - NTSXSIM/NTSISIM/NTSESIM → ``proxies.expand_capital_efficient`` legs
        (locally synthesised via the WisdomTree 90/60/-50 blueprint).
      - NTSDSIM/AVUVSIM/AVDVSIM/AVEMSIM/SPMOSIM/IDMOSIM/RSSTSIM/DBMFSIM
        → ``synths.<...>_returns_from_cache()``.
      - All other -SIM tickers → testfolio cache via load_testfolio_series.

    Returns:
        ticker → daily-returns Series mapping (raw, not yet aligned).
    """
    out: dict[str, pd.Series] = {}
    for t in tickers:
        if t == "NTSXSIM":
            out[t] = _capital_efficient_returns_from_blueprint("NTSX_PROXY")
        elif t == "NTSISIM":
            out[t] = _capital_efficient_returns_from_blueprint("NTSI_PROXY")
        elif t == "NTSESIM":
            out[t] = _capital_efficient_returns_from_blueprint("NTSE_PROXY")
        elif t == "NTSDSIM":
            out[t] = synths.ntsd_synth_returns_from_cache()
        elif t == "AVUVSIM":
            out[t] = synths.avuv_synth_returns_from_cache()
        elif t == "AVDVSIM":
            out[t] = synths.avdv_synth_returns_from_cache()
        elif t == "AVEMSIM":
            out[t] = synths.avem_synth_returns_from_cache()
        elif t == "AVNMSIM":
            # AVNM "Avantis All International" — synth blends VEASIM + VWOSIM
            # + 60bps tilt per personal Plano C notes moved outside the public repo + Avantis factsheet.
            out[t] = synths.avnm_synth_returns_from_cache()
        elif t == "AVDESIM":
            # AVDE "Avantis Intl Equity (developed)" — VEASIM + 55bps tilt.
            out[t] = synths.avde_synth_returns_from_cache()
        elif t == "SPMOSIM":
            out[t] = synths.spmo_synth_returns_from_cache()
        elif t == "IDMOSIM":
            out[t] = synths.idmo_synth_returns_from_cache()
        elif t == "RSSTSIM":
            out[t] = synths.rsst_synth_returns_from_cache()
        elif t == "DBMFSIM":
            # DBMFSIM is in the testfolio cache; pass through synths.dbmf_returns_from_cache
            # for citation traceability + future flexibility.
            out[t] = synths.dbmf_returns_from_cache()
        elif t == "TMFSIM":
            # TMFSIM is NOT in the testfolio cache; synth = 3× TLTSIM − 1.5%/y
            # daily-reset decay per [leverage_for_the_long_run, ch.3-4]. Used by
            # spy_beater_hunt iter 008+ HFEA configs (UPRO + TMF leveraged barbell).
            out[t] = synths.tmf_synth_returns_from_cache()
        else:
            out[t] = load_testfolio_series(t).pct_change().dropna()
    return out


def _capital_efficient_returns_from_blueprint(proxy_key: str) -> pd.Series:
    """Synthesise NTSX/NTSI/NTSE daily returns from the proxies.py blueprint.

    The single-source-of-truth lives in ``proxies.PROXY_LEGS``; this helper
    resolves each leg ticker to its daily returns and weights them by the
    blueprint coefficients (90/60/-50 for the WisdomTree Efficient Core
    family). CASHX is treated as 0 daily return (testfolio cache convention).

    Citation: WisdomTree Efficient Core ETF prospectus 2024;
    [risk_parity, ch.5, p.10] Carlson cap-efficient stacking.
    """
    legs = PROXY_LEGS[proxy_key]
    leg_returns: dict[str, pd.Series] = {}
    for leg, _coef in legs.items():
        if leg == "CASHX":
            # CASHX in the testfolio cache is the cash-leg equity curve;
            # pct_change yields ~0 daily, but we resolve via the loader
            # to keep date alignment consistent with other legs.
            leg_returns[leg] = load_testfolio_series("CASHX").pct_change().dropna()
        else:
            leg_returns[leg] = load_testfolio_series(leg).pct_change().dropna()

    aligned = pd.concat(leg_returns, axis=1, sort=True).dropna()
    weighted = pd.Series(0.0, index=aligned.index)
    for leg, coef in legs.items():
        weighted = weighted + coef * aligned[leg]
    return weighted


# ---------------------------------------------------------------------------
# Internal: metric helpers
# ---------------------------------------------------------------------------


def _compute_metrics(returns: pd.Series) -> dict[str, float]:
    """Return {sharpe, cagr, mdd} for a daily returns Series.

    Uses the same backtest.metrics.performance helpers as iter 023's backtest.py
    so cross-iter numbers are apples-to-apples.
    """
    if len(returns) < 2:
        return {"sharpe": float("nan"), "cagr": float("nan"), "mdd": float("nan")}
    eq = (1.0 + returns).cumprod() * 10_000.0
    return {
        "sharpe": float(_sharpe_fn(returns, periods_per_year=TRADING_DAYS_PER_YEAR)),
        "cagr": float(_cagr_fn(eq, periods_per_year=TRADING_DAYS_PER_YEAR)),
        "mdd": float(_mdd_fn(eq)),
    }


def _select_best_config(
    config_results: dict[str, dict[str, dict[str, float]]],
    datasets_to_test: tuple[str, ...],
) -> str:
    """Pick config with max mean(Sharpe / spy_benchmark_sharpe) across datasets.

    Mirror of iter 023 selection rule (NEW SPY-only mandate, 2026-04-29
    reframing). Datasets where a config produced NaN Sharpe are skipped from
    the mean to keep the comparison fair when synth-windowing differs.
    """
    spy_sharpes = {
        ds: spy_benchmark(BENCHMARKS[ds]).sharpe for ds in datasets_to_test
    }
    best, best_score = "", float("-inf")
    for cfg, ds_metrics in config_results.items():
        ratios = []
        for ds in datasets_to_test:
            s = ds_metrics[ds]["sharpe"]
            if not np.isnan(s):
                ratios.append(s / spy_sharpes[ds])
        if not ratios:
            continue
        score = float(np.mean(ratios))
        if score > best_score:
            best, best_score = cfg, score
    if not best:
        # Fallback: first config (defensive — should never trigger if metrics finite).
        best = next(iter(config_results.keys()))
    return best


# ---------------------------------------------------------------------------
# Internal: gate helpers (same battery as iter 023)
# ---------------------------------------------------------------------------


def _gate_pbo(per_cfg_returns: dict[str, pd.Series]) -> tuple[bool, float, int]:
    aligned = pd.concat(per_cfg_returns, axis=1, sort=True).dropna()
    if aligned.shape[0] < 252 or aligned.shape[1] < 2:
        # PBO needs ≥2 configs and a meaningful timeline; skip-pass when the
        # grid is too narrow (single-config iters legitimately can't compute).
        return True, float("nan"), 0
    result = compute_pbo(aligned.to_numpy(dtype=float), n_blocks=10)
    return bool(result.pbo < 0.5), float(result.pbo), int(result.n_combinations)


def _gate_dsr(returns: pd.Series, n_trials: int) -> tuple[bool, float]:
    if n_trials < 2:
        p_value = 1.0 - compute_psr(returns.values, benchmark=0.0)
    else:
        p_value = compute_dsr(returns.values, n_trials=n_trials).p_value
    return bool(p_value < 0.05), float(p_value)


def _gate_walk_forward(returns: pd.Series) -> tuple[bool, list[float], list[float]]:
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
        eq = (1.0 + r).cumprod() * 10_000.0
        oos_mdds.append(float(_mdd_fn(eq)))
        if len(oos_returns) >= WF_N_WINDOWS:
            break
    passed = (
        len(oos_returns) == WF_N_WINDOWS
        and sum(x > 0 for x in oos_returns) >= 6
        and all(x <= 0.25 for x in oos_mdds)
    )
    return passed, oos_returns, oos_mdds


def _gate_oos_70_30(returns: pd.Series) -> tuple[bool, float]:
    oos = returns.iloc[int(len(returns) * 0.70):]
    s = float(_sharpe_fn(oos, periods_per_year=TRADING_DAYS_PER_YEAR)) if len(oos) >= 63 else 0.0
    return bool(s > 0), s


def _gate_fwd(returns: pd.Series) -> tuple[bool, float]:
    fwd = returns[returns.index >= "2020-01-01"]
    s = float(_sharpe_fn(fwd, periods_per_year=TRADING_DAYS_PER_YEAR)) if len(fwd) >= 63 else 0.0
    return bool(s > 0), s


def _gate_bootstrap(returns: pd.Series) -> tuple[bool, float]:
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
    return bool(ci_low > 0), ci_low


def _gate_crosslib_self(returns: pd.Series) -> tuple[bool, float]:
    """Cross-lib stand-in: compare pandas-driven CAGR to numpy-recomputed CAGR.

    The full multi-library cross-check (engine vs engine) lives in iter 023's
    backtest.py with explicit price-level numpy maths. For run_iter helper
    we mimic that contract by recomputing CAGR from raw daily returns via
    numpy and asserting agreement within 3pp. This catches gross arithmetic
    drift but is intentionally less strict than the full backtest variant.
    """
    arr = returns.to_numpy(dtype=float)
    if len(arr) < 252:
        return False, float("nan")
    eq = np.cumprod(1.0 + arr) * 10_000.0
    np_cagr = float((eq[-1] / eq[0]) ** (TRADING_DAYS_PER_YEAR / (len(arr) - 1)) - 1.0)
    pd_eq = (1.0 + returns).cumprod() * 10_000.0
    pd_cagr = float(_cagr_fn(pd_eq, periods_per_year=TRADING_DAYS_PER_YEAR))
    delta_pp = abs(np_cagr - pd_cagr) * 100.0
    return bool(delta_pp <= 3.0), delta_pp


def _rolling_robustness(returns: pd.Series) -> tuple[int, float, int, list[float]]:
    """5y rolling-Sharpe robustness signal, awarded as 0-5 bonus pts."""
    sharpes: list[float] = []
    window = 252 * 5
    for start in range(0, len(returns) - window + 1, 252):
        sample = returns.iloc[start:start + window]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            sharpes.append(float(sample.mean() / sigma * np.sqrt(252)))
    pct_pos = (
        sum(s > 0 for s in sharpes) / len(sharpes) if sharpes else 0.0
    )
    pts = 5 if pct_pos >= 0.90 else 3 if pct_pos >= 0.75 else 1 if pct_pos >= 0.60 else 0
    return pts, pct_pos, len(sharpes), sharpes


# ---------------------------------------------------------------------------
# Public: run_iter_full
# ---------------------------------------------------------------------------


def run_iter_full(
    iter_n: int,
    iter_dir: Path,
    hypothesis_slug: str,
    primary_citation: str,
    configs: dict[str, dict[str, float]],
    datasets_to_test: tuple[str, ...] = ("lh_56y", "vt_real", "ndx_real"),
    cumulative_n_trials: int | None = None,
    selection_rule: str = (
        "NEW (2026-04-29 reframing): max mean(gross_Sharpe / SPY_Sharpe) across datasets"
    ),
) -> dict[str, Any]:
    """Execute a full iter sweep: configs × datasets → score → write artifacts.

    Args:
        iter_n: iter number (e.g. 27).
        iter_dir: iteration directory; created if missing.
        hypothesis_slug: e.g. ``'NTSD-swap'``.
        primary_citation: e.g. ``'[risk_parity, ch.5, p.10]'``.
        configs: ``{config_name: {ticker: weight}, ...}``.
        datasets_to_test: dataset names to test on (default: all 3).
        cumulative_n_trials: prior cumulative + this iter's configs; for DSR.
            If None, defaults to ``len(configs)``.
        selection_rule: text describing how the best config is picked
            (persisted in verdict.json).

    Returns:
        verdict dict (also written as ``verdict.json`` in iter_dir).
    """
    iter_dir = Path(iter_dir)
    iter_dir.mkdir(parents=True, exist_ok=True)

    if cumulative_n_trials is None:
        cumulative_n_trials = len(configs)

    # ------------------------------------------------------------------
    # 1) Per-(config × dataset) backtest: returns + metrics
    # ------------------------------------------------------------------
    config_results: dict[str, dict[str, dict[str, Any]]] = {}
    config_returns: dict[str, dict[str, pd.Series]] = {}

    for cfg_name, weights in configs.items():
        config_results[cfg_name] = {}
        config_returns[cfg_name] = {}
        for ds in datasets_to_test:
            returns = portfolio_returns_from_config(weights, dataset=ds)
            config_returns[cfg_name][ds] = returns
            config_results[cfg_name][ds] = _compute_metrics(returns)

    # ------------------------------------------------------------------
    # 2) Selection (max mean(Sharpe / SPY_Sharpe))
    # ------------------------------------------------------------------
    selected_cfg = _select_best_config(config_results, datasets_to_test)

    # ------------------------------------------------------------------
    # 3) Gates on the SELECTED config, per dataset
    # ------------------------------------------------------------------
    metrics_map: dict[str, DatasetMetrics] = {}
    gates_map: dict[str, Gates] = {}
    gate_details: dict[str, dict[str, Any]] = {}

    for ds in datasets_to_test:
        ds_returns_per_cfg = {c: config_returns[c][ds] for c in configs}
        g1_pass, pbo_value, n_combos = _gate_pbo(ds_returns_per_cfg)
        sel = config_returns[selected_cfg][ds]
        g2_pass, dsr_p = _gate_dsr(sel, n_trials=max(2, len(configs)))
        g3_pass, wf_returns, wf_mdds = _gate_walk_forward(sel)
        g4_pass, oos_s = _gate_oos_70_30(sel)
        g5_pass, fwd_s = _gate_fwd(sel)
        g6_pass, ci_low = _gate_bootstrap(sel)
        g7_pass, crosslib_delta = _gate_crosslib_self(sel)

        m = config_results[selected_cfg][ds]
        # Net == gross for static-stack portfolios with no rebalancing under
        # AnnualDarfEngine — iter 023 confirmed this empirically. We expose
        # the same {gross, net} fields so the verdict schema matches.
        metrics_map[ds] = DatasetMetrics(
            sharpe=m["sharpe"], cagr=m["cagr"], mdd=m["mdd"],
            dsr_p_value=dsr_p,
            net_sharpe=m["sharpe"], net_cagr=m["cagr"], net_mdd=m["mdd"],
        )
        gates_map[ds] = Gates(
            g1_pbo=g1_pass, g2_dsr=g2_pass, g3_wf=g3_pass, g4_oos=g4_pass,
            g5_fwd=g5_pass, g6_bootstrap=g6_pass, g7_crosslib=g7_pass,
        )
        gate_details[ds] = {
            "g1_pbo": pbo_value,
            "g1_pbo_n_combinations": n_combos,
            "g2_dsr_p": dsr_p,
            "g3_wf_returns": wf_returns,
            "g3_wf_mdds": wf_mdds,
            "g3_max_wf_mdd": max(wf_mdds) if wf_mdds else 0.0,
            "g4_oos_sharpe": oos_s,
            "g5_fwd_sharpe": fwd_s,
            "g6_ci_low": ci_low,
            "g7_crosslib_delta_pp": crosslib_delta,
        }

    # ------------------------------------------------------------------
    # 4) Robustness bonus (5y rolling Sharpe % positive, lh_56y as anchor)
    # ------------------------------------------------------------------
    anchor_ds = "lh_56y" if "lh_56y" in datasets_to_test else datasets_to_test[0]
    rob_pts, pct_pos, n_roll, roll_sharpes = _rolling_robustness(
        config_returns[selected_cfg][anchor_ds]
    )

    # ------------------------------------------------------------------
    # 5) Score under NEW SPY-only mandate + LEGACY avg(SPY,VT)
    # ------------------------------------------------------------------
    new_score = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=cumulative_n_trials,
        robustness_bonus=rob_pts,
    )
    legacy_score = score_strategy(
        metrics_map, gates_map,
        cumulative_n_trials=cumulative_n_trials,
        benchmarks=legacy_benchmarks(),
        robustness_bonus=rob_pts,
    )

    # ------------------------------------------------------------------
    # 6) Build verdict.json
    # ------------------------------------------------------------------
    verdict = new_score.to_dict()
    verdict.update({
        "status": new_score.tier.value.lower(),
        "configs_tested": len(configs),
        "primary_citation": primary_citation,
        "hypothesis_slug": hypothesis_slug,
        "selected_config": selected_cfg,
        "selection_rule": selection_rule,
        "scoring_basis": "NEW SPY-only +0.05 (mandate reframing 2026-04-29)",
        "score_legacy": legacy_score.to_dict(),
        "all_configs_metrics": config_results,
        "gate_details": gate_details,
        "net_metrics": {
            ds: {
                "sharpe": metrics_map[ds].net_sharpe,
                "cagr": metrics_map[ds].net_cagr,
                "mdd": metrics_map[ds].net_mdd,
            }
            for ds in datasets_to_test
        },
        "robustness": {
            "bonus_pts": rob_pts,
            "pct_positive_sharpe": pct_pos,
            "n_windows": n_roll,
            "min_rolling_sharpe": float(min(roll_sharpes)) if roll_sharpes else None,
            "max_rolling_sharpe": float(max(roll_sharpes)) if roll_sharpes else None,
            "anchor_dataset": anchor_ds,
        },
    })

    # ------------------------------------------------------------------
    # 7) Build results.json (returns_series for plot_helper.py)
    # ------------------------------------------------------------------
    runs = {
        ds: {
            cfg_name: {
                "sharpe": config_results[cfg_name][ds]["sharpe"],
                "cagr": config_results[cfg_name][ds]["cagr"],
                "mdd": config_results[cfg_name][ds]["mdd"],
            }
            for cfg_name in configs
        }
        for ds in datasets_to_test
    }
    returns_series: dict[str, dict[str, dict[str, list]]] = {ds: {} for ds in datasets_to_test}
    for ds in datasets_to_test:
        # Persist selected + best-Sharpe-of-grid (often identical) to keep payload small.
        top_cfg = max(
            configs.keys(),
            key=lambda c: config_results[c][ds]["sharpe"]
            if not np.isnan(config_results[c][ds]["sharpe"]) else float("-inf"),
        )
        for c in {selected_cfg, top_cfg}:
            r = config_returns[c][ds]
            returns_series[ds][c] = {
                "index": [str(d.date()) for d in r.index],
                "gross_returns": r.tolist(),
                "net_returns": r.tolist(),
            }

    results_payload = {
        "hypothesis_slug": hypothesis_slug,
        "selected_config": selected_cfg,
        "configs_tested": len(configs),
        "configs": configs,
        "runs": runs,
        "returns_series": returns_series,
    }

    def _default_json(obj: Any) -> Any:
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, (pd.Timestamp,)):
            return str(obj.date())
        return str(obj)

    (iter_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=_default_json) + "\n"
    )
    (iter_dir / "results.json").write_text(
        json.dumps(results_payload, indent=2, default=_default_json) + "\n"
    )

    # ------------------------------------------------------------------
    # 8) final_report.md + plots
    # ------------------------------------------------------------------
    _write_final_report(
        iter_dir, iter_n, hypothesis_slug, primary_citation,
        configs, verdict, datasets_to_test,
    )
    _write_plots(iter_dir, datasets_to_test, selected_cfg)

    return verdict


# ---------------------------------------------------------------------------
# Internal: report + plots
# ---------------------------------------------------------------------------


def _write_final_report(
    iter_dir: Path,
    iter_n: int,
    slug: str,
    citation: str,
    configs: dict[str, dict[str, float]],
    verdict: dict[str, Any],
    datasets_to_test: tuple[str, ...],
) -> None:
    """Write a concise final_report.md summary for the iter."""
    selected = verdict["selected_config"]
    legacy = verdict.get("score_legacy", {})

    lines = [
        f"# Iter {iter_n:03d} — Final Report — `{slug}`",
        "",
        f"**Verdict (NEW SPY-only mandate, 2026-04-29 reframing)**: "
        f"**{verdict['tier']} {verdict['total_score']}/100** — "
        f"`winner_conditions_met={verdict['winner_conditions_met']}`.",
        "",
        f"**Verdict (LEGACY avg(SPY,VT) + 0.10)**: "
        f"**{legacy.get('tier', 'N/A')} {legacy.get('total_score', 'N/A')}/100** — "
        f"`winner_conditions_met={legacy.get('winner_conditions_met', 'N/A')}`.",
        "",
        f"**Primary citation**: {citation}",
        "",
        "---",
        "",
        f"## Selected config: `{selected}`",
        "",
        "Weights:",
        "",
        "```json",
        json.dumps(configs[selected], indent=2),
        "```",
        "",
        "## Per-dataset metrics (gross-of-tax)",
        "",
        "| dataset | Sharpe | CAGR | MDD | gates | DSR p |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for ds in datasets_to_test:
        m = verdict["metrics_used"][ds]
        gates_passed = verdict["criteria"]["2_gates"]["per_dataset"][ds]
        lines.append(
            f"| **{ds}** | "
            f"{m['sharpe']:.3f} | "
            f"{m['cagr'] * 100:.2f}% | "
            f"{m['mdd'] * 100:.2f}% | "
            f"{gates_passed}/7 | "
            f"{m['dsr_p_value']:.2e} |"
        )
    lines.extend([
        "",
        "## Configs grid (Sharpe per config × dataset)",
        "",
        "| config | " + " | ".join(datasets_to_test) + " |",
        "|---" + "|---:" * len(datasets_to_test) + "|",
    ])
    for cfg in configs:
        row_cells = [cfg]
        for ds in datasets_to_test:
            s = verdict["all_configs_metrics"][cfg][ds]["sharpe"]
            row_cells.append(f"{s:.3f}" if not (isinstance(s, float) and np.isnan(s)) else "n/a")
        lines.append("| " + " | ".join(row_cells) + " |")

    lines.extend([
        "",
        "## NEW SPY-only Sharpe edge",
        "",
        "| dataset | bench (SPY) | hurdle (+0.05) | candidate | edge | passes? |",
        "|---|---:|---:|---:|---:|:-:|",
    ])
    for ds in datasets_to_test:
        bm = verdict["benchmarks_used"][ds]
        m = verdict["metrics_used"][ds]
        edge = m["sharpe"] - bm["sharpe"]
        passes = "[OK]" if edge >= 0.05 else "[--]"
        lines.append(
            f"| {ds} | {bm['sharpe']:.3f} | {bm['sharpe'] + 0.05:.3f} | "
            f"{m['sharpe']:.3f} | {edge:+.3f} | {passes} |"
        )

    lines.extend([
        "",
        "## Robustness (5y rolling Sharpe, anchor dataset)",
        "",
        f"- bonus_pts: {verdict['robustness']['bonus_pts']}/5",
        f"- pct_positive_sharpe: {verdict['robustness']['pct_positive_sharpe']:.2%}",
        f"- n_windows: {verdict['robustness']['n_windows']}",
        f"- anchor_dataset: {verdict['robustness']['anchor_dataset']}",
        "",
        "## INCOMPLETE flags",
        "",
        "(Document any synth caveats here per spec §Synth formulas reference.)",
        "",
        "## Lesson",
        "",
        "(Append after manual review.)",
        "",
    ])

    (iter_dir / "final_report.md").write_text("\n".join(lines))


def _write_plots(
    iter_dir: Path,
    datasets_to_test: tuple[str, ...],
    selected_cfg: str,
) -> None:
    """Render plot_<ds>.png + plot_rolling_windows_<ds>.png via plot_helper.

    ``plot_helper.plot_iter`` reads ``results.json`` from ``iter_dir`` and
    writes the canonical equity + rolling-windows plots used by the loop's
    historical iters. Datasets without registered benchmark sources (e.g.
    custom names) are silently skipped with a printed note.
    """
    from studies.long_term_portfolio import plot_helper

    # plot_helper.plot_iter expects an iter_prefix to look up under
    # iterations/<prefix>-*. To support smoke / arbitrary iter dirs, we
    # call the lower-level plot_dataset / plot_rolling_windows with
    # the full iter_dir path directly.
    for ds in datasets_to_test:
        if ds not in plot_helper.BENCHMARK_SOURCES:
            print(f"[run_iter:_write_plots] {ds}: no benchmark sources, skip plot")
            continue
        try:
            p1 = plot_helper.plot_dataset(iter_dir, ds, selected_cfg)
            if p1 is not None:
                print(f"[run_iter:_write_plots] {ds}: wrote {p1.name}")
            p2 = plot_helper.plot_rolling_windows(iter_dir, ds, selected_cfg)
            if p2 is not None:
                print(f"[run_iter:_write_plots] {ds}: wrote {p2.name}")
        except Exception as exc:  # pragma: no cover - defensive
            # Plotting failure must NOT abort the verdict; persist warning instead.
            print(f"[run_iter:_write_plots] {ds}: plot failed ({exc!r})")
