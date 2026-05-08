"""Per-iter execution helper for spy_beater_hunt.

Reuses gate functions from ``studies.long_term_portfolio.run_iter`` (PBO,
DSR, Walk-Forward, OOS70/30, FWD, Bootstrap, Cross-lib, Robustness) but
applies CAGR-anchored scoring per ``WINNER_AND_RANKING.md``.

Each config is a ``StrategySpec`` dict — one of:

  Static portfolio (same as long_term_portfolio):
    {"type": "static", "weights": {ticker: weight, ...}}

  LRS-gated rotation (Gayed 200d SMA gate):
    {
      "type": "lrs",
      "on_weights": {ticker: weight, ...},   # leveraged equity sleeve
      "off_weights": {ticker: weight, ...},  # defensive sleeve
      "signal_ticker": "SPYSIM",             # what to compute SMA on
      "sma_window": 200,
      "lag_days": 1,
    }

The wrapper:
1. Builds per (config × dataset) returns Series.
2. Computes metrics (Sharpe / CAGR / MDD).
3. Selects best config by max mean(Sharpe / SPY_Sharpe).
4. Runs 7-gate battery on selected config per dataset.
5. Computes CAGR-anchored score via spy_beater_hunt.scoring.
6. Persists verdict.json + final_report.md.

Citations:
  - [leverage_for_the_long_run, ch.3-4, p.40-60] Gayed LRS rationale.
  - [advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34] gate framework.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ai_trade.backtest.data.testfolio_loader import load_testfolio_series
from studies.long_term_portfolio import datasets as datasets_mod
from studies.long_term_portfolio.run_iter import (
    _compute_metrics,
    _gate_bootstrap,
    _gate_crosslib_self,
    _gate_dsr,
    _gate_fwd,
    _gate_oos_70_30,
    _gate_pbo,
    _gate_walk_forward,
    _rolling_robustness,
    portfolio_returns_from_config,
)
from studies.long_term_portfolio.scoring import (
    BENCHMARKS,
    DatasetMetrics,
    Gates,
    spy_benchmark,
)
from studies.spy_beater_hunt.lrs_engine import (
    ema_gate,
    gayed_200d_sma_gate,
    lrs_strategy_returns,
    momentum_gate,
    threshold_band_gate,
)
from studies.spy_beater_hunt.plot_helper import (
    plot_cagr_mdd_scatter,
    plot_gate_heatmap,
    plot_overlay_per_dataset,
    plot_rolling_cagr_mdd,
)
from studies.spy_beater_hunt.rolling_metrics import (
    DEFAULT_WINDOWS_YEARS as ROLLING_WINDOWS_YEARS,
    cagr_pass_rate_vs_benchmark,
    rolling_cagr_mdd_at_windows,
    worst_window_mdd,
)
from studies.spy_beater_hunt.scoring import score_strategy_spy_beater
from studies.spy_beater_hunt.tax_layer import net_returns_from_spec
from studies.spy_beater_hunt.vol_target_engine import (
    realized_vol,
    vol_target_strategy_returns,
    vol_target_weight,
)


TRADING_DAYS_PER_YEAR = 252


# ---------------------------------------------------------------------------
# Public: returns from a StrategySpec
# ---------------------------------------------------------------------------


def returns_from_spec(spec: dict, dataset: str) -> pd.Series:
    """Build daily portfolio returns from a StrategySpec dict.

    Supports four strategy types:
      - ``static``: delegate to :func:`portfolio_returns_from_config`
      - ``lrs``: Gayed 200d SMA gate rotation between
        ``on_weights`` and ``off_weights`` sleeves
      - ``vol_target``: Carver vol-targeted scaling of an
        ``underlying_weights`` sleeve against ``cash_weights``
      - ``blend``: meta-portfolio of strategies — weighted sum of
        sub-spec daily returns (iter 018+, see
        :func:`_blend_returns_from_spec`)
    """
    stype = spec.get("type", "static")
    if stype == "static":
        return portfolio_returns_from_config(spec["weights"], dataset)
    if stype == "lrs":
        return _lrs_returns_from_spec(spec, dataset)
    if stype == "vol_target":
        return _vol_target_returns_from_spec(spec, dataset)
    if stype == "blend":
        return _blend_returns_from_spec(spec, dataset)
    raise ValueError(f"unknown strategy type: {stype!r}")


def _blend_returns_from_spec(spec: dict, dataset: str) -> pd.Series:
    """Build meta-portfolio daily returns: weighted sum of sub-spec returns.

    Spec format::

        {
          "type": "blend",
          "constituents": [
            {"weight": 0.5, "spec": {...sub-spec...}},
            {"weight": 0.5, "spec": {...sub-spec...}},
          ],
        }

    Constituents may be any spec type (static / lrs / vol_target / blend);
    each sub-spec is resolved via :func:`returns_from_spec` recursively.
    Weights MUST sum to 1.0 within tolerance 1e-6.

    Aligns sub-spec returns via inner-join on date index; blend returns the
    intersection-of-dates daily weighted sum.

    Citation: ``[advances_fin_ml, ch.16, p.241-256]`` portfolio construction
    over multiple alpha streams; ``[risk_parity, ch.5, p.10]`` Carlson
    capital-efficient stacking generalized to strategy-level. Iter 018
    introduced this for H1 META-ENSEMBLE probe of KILL #33 architectural
    ceiling at meta-portfolio axis.
    """
    constituents = spec["constituents"]
    weights = [float(c["weight"]) for c in constituents]
    total_w = sum(weights)
    if abs(total_w - 1.0) > 1e-6:
        raise ValueError(
            f"blend constituent weights must sum to 1.0; got {total_w:.6f}"
        )

    sub_returns: list[pd.Series] = []
    for i, c in enumerate(constituents):
        r = returns_from_spec(c["spec"], dataset)
        sub_returns.append(r.rename(f"_blend_{i}"))

    aligned = pd.concat(sub_returns, axis=1).dropna()
    weighted = sum(
        weights[i] * aligned.iloc[:, i] for i in range(len(constituents))
    )
    return weighted


def _lrs_returns_from_spec(spec: dict, dataset: str) -> pd.Series:
    """Build LRS daily returns: rotate on_weights ↔ off_weights via regime gate.

    Supported gate types (via spec["filter"] field, default "sma"):
      - "sma": classical SMA cross (no buffer)
      - "ema": EMA cross (no buffer)
      - "sma_band" / "ema_band": hysteresis band around MA, requires
        spec["buffer_pct"] (default 0.02 = 2%)

    Backwards-compat: spec["sma_window"] is the window for any filter type.
    spec["filter"] absent → defaults to "sma" (matches iter 001 behavior).
    """
    on_returns = portfolio_returns_from_config(spec["on_weights"], dataset)
    off_returns = portfolio_returns_from_config(spec["off_weights"], dataset)

    signal_ticker = spec.get("signal_ticker", "SPYSIM")
    window = int(spec.get("sma_window", 200))
    lag_days = int(spec.get("lag_days", 1))
    filter_type = spec.get("filter", "sma").lower()
    buffer_pct = float(spec.get("buffer_pct", 0.0))

    signal_prices = load_testfolio_series(signal_ticker)

    if filter_type == "momentum":
        lookback_days = int(spec.get("lookback_days", 126))
        gate = momentum_gate(
            signal_prices, lookback_days=lookback_days, lag_days=lag_days,
        )
    elif filter_type == "sma" and buffer_pct == 0.0:
        gate = gayed_200d_sma_gate(signal_prices, window=window, lag_days=lag_days)
    elif filter_type == "ema" and buffer_pct == 0.0:
        gate = ema_gate(signal_prices, window=window, lag_days=lag_days)
    elif filter_type in ("sma", "sma_band"):
        gate = threshold_band_gate(
            signal_prices, window=window, buffer_pct=buffer_pct,
            lag_days=lag_days, filter_type="sma",
        )
    elif filter_type in ("ema", "ema_band"):
        gate = threshold_band_gate(
            signal_prices, window=window, buffer_pct=buffer_pct,
            lag_days=lag_days, filter_type="ema",
        )
    else:
        raise ValueError(
            f"unknown filter_type {filter_type!r}; "
            "choose 'sma', 'ema', 'sma_band', 'ema_band', or 'momentum'"
        )

    return lrs_strategy_returns(on_returns, off_returns, gate)


def _vol_target_returns_from_spec(spec: dict, dataset: str) -> pd.Series:
    """Build vol-targeted daily returns: weight × underlying + (1−w) × cash.

    Required spec fields:
      - ``underlying_weights``: dict[ticker, weight] for the leveraged sleeve
      - ``cash_weights``: dict[ticker, weight] for the cash sleeve
      - ``target_vol_annual``: target portfolio vol (e.g., 0.20 for 20%)

    Optional spec fields (with defaults):
      - ``signal_ticker`` (default ``'SPYSIM'``): asset whose realised vol
        drives weight scaling.
      - ``underlying_leverage_factor`` (default 1.0): SSO=2, UPRO=3, etc.
      - ``vol_window`` (default 60): rolling window for realised vol.
      - ``vol_lag_days`` (default 1): T+1 execution lag.
      - ``weight_min`` (default 0.0): minimum weight on underlying.
      - ``weight_max`` (default 1.0): maximum weight on underlying.
    """
    underlying_returns = portfolio_returns_from_config(
        spec["underlying_weights"], dataset
    )
    cash_returns = portfolio_returns_from_config(spec["cash_weights"], dataset)

    signal_ticker = spec.get("signal_ticker", "SPYSIM")
    target_vol = float(spec["target_vol_annual"])
    factor = float(spec.get("underlying_leverage_factor", 1.0))
    window = int(spec.get("vol_window", 60))
    lag_days = int(spec.get("vol_lag_days", 1))
    weight_min = float(spec.get("weight_min", 0.0))
    weight_max = float(spec.get("weight_max", 1.0))

    signal_prices = load_testfolio_series(signal_ticker)
    signal_returns = signal_prices.pct_change().dropna()

    rv = realized_vol(signal_returns, window=window)
    weight = vol_target_weight(
        rv,
        target_vol_annual=target_vol,
        underlying_factor=factor,
        weight_min=weight_min,
        weight_max=weight_max,
        lag_days=lag_days,
    )

    return vol_target_strategy_returns(underlying_returns, cash_returns, weight)


# ---------------------------------------------------------------------------
# Internal: best-config selection (mirror long_term_portfolio rule)
# ---------------------------------------------------------------------------


def _select_best_config(
    config_results: dict[str, dict[str, dict[str, float]]],
    datasets_to_test: tuple[str, ...],
) -> str:
    """Pick config with max mean(Sharpe / SPY_Sharpe)."""
    spy_sharpes = {ds: spy_benchmark(BENCHMARKS[ds]).sharpe for ds in datasets_to_test}
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
        best = next(iter(config_results.keys()))
    return best


# ---------------------------------------------------------------------------
# Public: run_iter_spy_beater
# ---------------------------------------------------------------------------


def run_iter_spy_beater(
    iter_n: int,
    iter_dir: Path,
    hypothesis_slug: str,
    primary_citation: str,
    configs: dict[str, dict],
    datasets_to_test: tuple[str, ...] = ("lh_56y", "spy_real"),
    cumulative_n_trials: int | None = None,
) -> dict[str, Any]:
    """Execute a spy_beater iter sweep: configs × datasets → score → artifacts.

    Args:
        iter_n: iter number.
        iter_dir: iteration directory; created if missing.
        hypothesis_slug: e.g. ``'A1-Gayed-LRS-UPRO'``.
        primary_citation: e.g. ``'[leverage_for_the_long_run, ch.3-4]'``.
        configs: ``{config_name: StrategySpec, ...}``.
        datasets_to_test: dataset names (default: all 3).
        cumulative_n_trials: prior + this iter's count; for DSR penalty.

    Returns:
        verdict dict (also written as ``verdict.json``).
    """
    iter_dir = Path(iter_dir)
    iter_dir.mkdir(parents=True, exist_ok=True)

    if cumulative_n_trials is None:
        cumulative_n_trials = len(configs)

    # ------------------------------------------------------------------
    # 1) Per (config × dataset) backtest
    # ------------------------------------------------------------------
    config_results: dict[str, dict[str, dict[str, Any]]] = {}
    config_returns: dict[str, dict[str, pd.Series]] = {}

    for cfg_name, spec in configs.items():
        config_results[cfg_name] = {}
        config_returns[cfg_name] = {}
        for ds in datasets_to_test:
            returns = returns_from_spec(spec, ds)
            config_returns[cfg_name][ds] = returns
            config_results[cfg_name][ds] = _compute_metrics(returns)

    # ------------------------------------------------------------------
    # 2) Best-config selection
    # ------------------------------------------------------------------
    selected_cfg = _select_best_config(config_results, datasets_to_test)

    # ------------------------------------------------------------------
    # 3) 7-gate battery on selected config per dataset
    # ------------------------------------------------------------------
    metrics_map: dict[str, DatasetMetrics] = {}
    gates_map: dict[str, Gates] = {}
    gate_details: dict[str, dict[str, Any]] = {}
    tax_summaries: dict[str, dict[str, Any]] = {}
    net_returns_per_ds: dict[str, pd.Series] = {}

    selected_spec = configs[selected_cfg]
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

        # Net-of-tax metrics (Lei 14.754/2023 — see tax_layer.py)
        net_r, tax_summary = net_returns_from_spec(selected_spec, sel)
        net_metrics = _compute_metrics(net_r)
        tax_summaries[ds] = tax_summary.to_dict()
        net_returns_per_ds[ds] = net_r

        m = config_results[selected_cfg][ds]
        metrics_map[ds] = DatasetMetrics(
            sharpe=m["sharpe"], cagr=m["cagr"], mdd=m["mdd"],
            dsr_p_value=dsr_p,
            net_sharpe=net_metrics["sharpe"],
            net_cagr=net_metrics["cagr"],
            net_mdd=net_metrics["mdd"],
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
    # 4) Robustness — multi-horizon rolling CAGR pass-rate vs SPY benchmark
    # ------------------------------------------------------------------
    anchor_ds = "lh_56y" if "lh_56y" in datasets_to_test else datasets_to_test[0]
    legacy_rob_pts_5, pct_pos, n_roll, roll_sharpes = _rolling_robustness(
        config_returns[selected_cfg][anchor_ds]
    )

    # Multi-window CAGR pass-rate per dataset → averaged across datasets
    selected_returns_per_ds = {
        ds: config_returns[selected_cfg][ds] for ds in datasets_to_test
    }
    spy_returns_per_ds = {
        ds: load_testfolio_series("SPYSIM").pct_change().dropna().loc[
            datasets_mod.get_meta(ds)["start"]:datasets_mod.get_meta(ds)["end"]
        ]
        for ds in datasets_to_test
    }

    rolling_pass_rates_per_window: dict[int, list[float]] = {
        w: [] for w in ROLLING_WINDOWS_YEARS
    }
    rolling_worst_mdd_per_window: dict[int, list[float]] = {
        w: [] for w in ROLLING_WINDOWS_YEARS
    }
    rolling_per_dataset: dict[str, dict] = {}

    for ds in datasets_to_test:
        strat_r = selected_returns_per_ds[ds]
        spy_r = spy_returns_per_ds[ds]
        strat_roll = rolling_cagr_mdd_at_windows(strat_r)
        spy_roll = rolling_cagr_mdd_at_windows(spy_r)
        per_ds_payload: dict[int, dict] = {}
        for w in ROLLING_WINDOWS_YEARS:
            pct, n_eval = cagr_pass_rate_vs_benchmark(
                strat_roll[w], spy_roll[w]
            )
            wmdd = worst_window_mdd(strat_roll[w])
            per_ds_payload[w] = {
                "pct_strat_beats_spy_cagr": pct,
                "n_windows": n_eval,
                "worst_strat_mdd": wmdd,
            }
            if pct == pct:  # not NaN
                rolling_pass_rates_per_window[w].append(pct)
            if wmdd == wmdd:
                rolling_worst_mdd_per_window[w].append(wmdd)
        rolling_per_dataset[ds] = per_ds_payload

    # Average pass-rate / worst-mdd across datasets per window
    rolling_pass_rates = {
        w: (
            float(np.mean(rolling_pass_rates_per_window[w]))
            if rolling_pass_rates_per_window[w] else float("nan")
        )
        for w in ROLLING_WINDOWS_YEARS
    }
    rolling_worst_mdd = {
        w: (
            float(np.max(rolling_worst_mdd_per_window[w]))
            if rolling_worst_mdd_per_window[w] else float("nan")
        )
        for w in ROLLING_WINDOWS_YEARS
    }

    # ------------------------------------------------------------------
    # 5) CAGR-anchored score (with multi-horizon robustness)
    # ------------------------------------------------------------------
    score_dict = score_strategy_spy_beater(
        metrics_map, gates_map,
        cumulative_n_trials=cumulative_n_trials,
        rolling_pass_rates=rolling_pass_rates,
        rolling_worst_mdd=rolling_worst_mdd,
    )

    # Net-of-tax score (parallel computation; same gates / DSR / robustness,
    # but using net_* metrics for CAGR/MDD/Sharpe sub-scores and bars).
    net_metrics_map = {
        ds: DatasetMetrics(
            sharpe=metrics_map[ds].net_sharpe or 0.0,
            cagr=metrics_map[ds].net_cagr or 0.0,
            mdd=metrics_map[ds].net_mdd or 0.0,
            dsr_p_value=metrics_map[ds].dsr_p_value,
        )
        for ds in datasets_to_test
    }
    net_score_dict = score_strategy_spy_beater(
        net_metrics_map, gates_map,
        cumulative_n_trials=cumulative_n_trials,
        rolling_pass_rates=rolling_pass_rates,
        rolling_worst_mdd=rolling_worst_mdd,
    )

    # ------------------------------------------------------------------
    # 6) Build verdict + artifacts
    # ------------------------------------------------------------------
    verdict = dict(score_dict)
    verdict.update({
        "configs_tested": len(configs),
        "primary_citation": primary_citation,
        "hypothesis_slug": hypothesis_slug,
        "selected_config": selected_cfg,
        "selection_rule": "max mean(Sharpe / SPY_Sharpe) across datasets",
        "scoring_basis": "CAGR-anchored (spy_beater_hunt rubric, WINNER_AND_RANKING.md)",
        "all_configs_metrics": config_results,
        "gate_details": gate_details,
        "robustness": {
            "legacy_5y_sharpe_pct_positive": pct_pos,
            "legacy_5y_sharpe_n_windows": n_roll,
            "rolling_pass_rates_avg_across_datasets": rolling_pass_rates,
            "rolling_worst_mdd_max_across_datasets": rolling_worst_mdd,
            "rolling_per_dataset": rolling_per_dataset,
            "anchor_dataset": anchor_ds,
        },
        "configs": _serialise_configs(configs),
        # Net-of-tax (Lei 14.754/2023 — DARF anual sobre ganho realizado)
        "net_total_score": net_score_dict["total_score"],
        "net_tier": net_score_dict["tier"],
        "net_winner_conditions_met": net_score_dict["winner_conditions_met"],
        "net_bars": net_score_dict["bars"],
        "net_criteria": net_score_dict["criteria"],
        "net_metrics_used": {
            ds: {
                "sharpe": metrics_map[ds].net_sharpe,
                "cagr": metrics_map[ds].net_cagr,
                "mdd": metrics_map[ds].net_mdd,
            }
            for ds in datasets_to_test
        },
        "tax_summary": tax_summaries,
    })

    # results.json (returns_series for plot rendering)
    # Selected config gets actual net-of-tax series; non-selected configs
    # store net == gross (computing tax for every config × ds is expensive
    # and they don't drive any deploy decision).
    returns_series: dict[str, dict[str, dict[str, list]]] = {ds: {} for ds in datasets_to_test}
    for ds in datasets_to_test:
        top_cfg = max(
            configs.keys(),
            key=lambda c: config_results[c][ds]["sharpe"]
            if not np.isnan(config_results[c][ds]["sharpe"]) else float("-inf"),
        )
        for c in {selected_cfg, top_cfg}:
            r = config_returns[c][ds]
            net_r = (
                net_returns_per_ds[ds] if c == selected_cfg
                else r
            )
            returns_series[ds][c] = {
                "index": [str(d.date()) for d in r.index],
                "gross_returns": r.tolist(),
                "net_returns": net_r.tolist(),
            }

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
    results_payload = {
        "hypothesis_slug": hypothesis_slug,
        "selected_config": selected_cfg,
        "configs_tested": len(configs),
        "configs": _serialise_configs(configs),
        "runs": runs,
        "returns_series": returns_series,
    }

    def _default_json(obj: Any) -> Any:
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, pd.Timestamp):
            return str(obj.date())
        return str(obj)

    (iter_dir / "verdict.json").write_text(
        json.dumps(verdict, indent=2, default=_default_json) + "\n"
    )
    (iter_dir / "results.json").write_text(
        json.dumps(results_payload, indent=2, default=_default_json) + "\n"
    )

    _write_final_report(
        iter_dir, iter_n, hypothesis_slug, primary_citation,
        configs, verdict, datasets_to_test,
    )

    # ------------------------------------------------------------------
    # 9) Comparative plots (overlay equity + drawdown, scatter, heatmap)
    # ------------------------------------------------------------------
    try:
        plot_overlay_per_dataset(iter_dir, config_returns, datasets_to_test)
        plot_cagr_mdd_scatter(iter_dir, config_results, datasets_to_test)
        plot_gate_heatmap(iter_dir, gate_details, config_results, datasets_to_test)
        plot_rolling_cagr_mdd(iter_dir, config_returns, datasets_to_test)
    except Exception as exc:  # pragma: no cover - plotting must not abort verdict
        print(f"[run_iter:plots] non-fatal plot error: {exc!r}")

    return verdict


# ---------------------------------------------------------------------------
# Internal: helpers
# ---------------------------------------------------------------------------


def _serialise_configs(configs: dict[str, dict]) -> dict[str, dict]:
    """Make StrategySpecs JSON-serialisable (no Series, all scalars)."""
    out: dict[str, dict] = {}
    for name, spec in configs.items():
        out[name] = dict(spec)  # shallow copy; weights dicts are already json-safe
    return out


def _write_final_report(
    iter_dir: Path,
    iter_n: int,
    slug: str,
    citation: str,
    configs: dict[str, dict],
    verdict: dict[str, Any],
    datasets_to_test: tuple[str, ...],
) -> None:
    """Write a concise final_report.md for the iter."""
    selected = verdict["selected_config"]
    bars = verdict["bars"]
    cri = verdict["criteria"]

    net_score = verdict.get("net_total_score")
    net_tier = verdict.get("net_tier")
    net_bars = verdict.get("net_bars", {})
    net_cri = verdict.get("net_criteria", {})
    net_metrics_used = verdict.get("net_metrics_used", {})
    tax_summary_per_ds = verdict.get("tax_summary", {})

    lines = [
        f"# spy_beater_hunt iter {iter_n:03d} — Final Report — `{slug}`",
        "",
        f"**Gross tier**: **{verdict['tier']}** — `gross_score={verdict['total_score']}/100`, "
        f"`gross_winner_met={verdict['winner_conditions_met']}`",
        "",
        f"**Net tier**: **{net_tier or 'n/a'}** — `net_score={net_score if net_score is not None else 'n/a'}/100`, "
        f"`net_winner_met={verdict.get('net_winner_conditions_met', 'n/a')}`",
        "",
        "**Strict bars (gross-of-tax, CAGR-anchored)**:",
        f"- CAGR bar (mean ≥ 11.21%): {'PASS' if bars['cagr_bar'] else 'FAIL'} "
        f"(mean = {cri['1_cagr']['mean_cagr'] * 100:.2f}%)",
        f"- MDD bar (mean ≤ 55.17%): {'PASS' if bars['mdd_bar'] else 'FAIL'} "
        f"(mean = {cri['2_mdd']['mean_mdd'] * 100:.2f}%)",
        f"- Gates bar (≥ 2/3 datasets at threshold): "
        f"{'PASS' if bars['gates_bar'] else 'FAIL'}",
        "",
        "**Strict bars (net-of-tax, Lei 14.754/2023 — DARF 15% anual)**:",
        f"- CAGR bar: {'PASS' if net_bars.get('cagr_bar') else 'FAIL'} "
        f"(mean = {net_cri.get('1_cagr', {}).get('mean_cagr', 0) * 100:.2f}%)",
        f"- MDD bar: {'PASS' if net_bars.get('mdd_bar') else 'FAIL'} "
        f"(mean = {net_cri.get('2_mdd', {}).get('mean_mdd', 0) * 100:.2f}%)",
        f"- Gates bar (same as gross): "
        f"{'PASS' if net_bars.get('gates_bar') else 'FAIL'}",
        "",
        f"**Primary citation**: {citation}",
        "",
        "---",
        "",
        f"## Selected config: `{selected}`",
        "",
        "Spec:",
        "",
        "```json",
        json.dumps(verdict["configs"][selected], indent=2),
        "```",
        "",
        "## Per-dataset metrics — pre vs post taxes",
        "",
        "| dataset | gross Sharpe | gross CAGR | gross MDD | net Sharpe | net CAGR | net MDD | drag (pp) | gates |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for ds in datasets_to_test:
        m = verdict["metrics_used"][ds]
        nm = net_metrics_used.get(ds, {})
        ts = tax_summary_per_ds.get(ds, {})
        gates_passed = cri["3_gates"]["per_dataset"][ds]
        net_sharpe = nm.get("sharpe", float("nan"))
        net_cagr = nm.get("cagr", float("nan"))
        net_mdd = nm.get("mdd", float("nan"))
        drag = ts.get("drag_pct_pts", float("nan"))
        lines.append(
            f"| **{ds}** | {m['sharpe']:.3f} | {m['cagr'] * 100:.2f}% | "
            f"{m['mdd'] * 100:.2f}% | {net_sharpe:.3f} | {net_cagr * 100:.2f}% | "
            f"{net_mdd * 100:.2f}% | {drag:.2f} | {gates_passed}/7 |"
        )

    lines.append("")
    lines.append("**Tax model** (`tax_layer.py` / Lei 14.754/2023):")
    for ds in datasets_to_test:
        ts = tax_summary_per_ds.get(ds, {})
        lines.append(
            f"- `{ds}` — {ts.get('classification', 'n/a')}, "
            f"{ts.get('n_year_end_settlements', 0)} year-end settlements, "
            f"total DARF ${ts.get('total_darf_paid', 0):,.0f} "
            f"(terminal ${ts.get('terminal_darf', 0):,.0f}), "
            f"drag {ts.get('drag_pct_pts', 0):.2f}pp"
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
            row_cells.append(
                f"{s:.3f}" if not (isinstance(s, float) and np.isnan(s)) else "n/a"
            )
        lines.append("| " + " | ".join(row_cells) + " |")

    lines.extend([
        "",
        "## CAGR-anchored scoring breakdown",
        "",
        "| criterion | points | max | detail |",
        "|---|---:|---:|---|",
        f"| 1. CAGR vs SPY | {cri['1_cagr']['points']} | 30 | "
        f"mean = {cri['1_cagr']['mean_cagr'] * 100:.2f}%, bar = "
        f"{cri['1_cagr']['spy_bar'] * 100:.2f}% |",
        f"| 2. MDD vs SPY | {cri['2_mdd']['points']} | 20 | "
        f"mean = {cri['2_mdd']['mean_mdd'] * 100:.2f}%, bar = "
        f"{cri['2_mdd']['spy_bar'] * 100:.2f}% |",
        f"| 3. Gates | {cri['3_gates']['points']} | 20 | "
        f"per_ds = {cri['3_gates']['per_dataset']}, "
        f"cross_met = {cri['3_gates']['cross_dataset_met']} |",
        f"| 4. DSR | {cri['4_dsr']['points']} | 10 | "
        f"worst_p = {cri['4_dsr']['worst_p_value']:.2e}, "
        f"n_trials = {cri['4_dsr']['cumulative_n_trials']} |",
        f"| 5. Sharpe | {cri['5_sharpe']['points']} | 10 | "
        f"mean = {cri['5_sharpe']['mean_sharpe']:.3f} |",
        f"| 6. Robustness | {cri['6_robustness']['points']} | 10 | "
        f"input_bonus = {cri['6_robustness']['input_bonus']} |",
        f"| 7. Extra bonus | {cri['7_extra_bonus']['points']} | 5 | — |",
        "",
        "## Robustness — multi-horizon CAGR pass-rate vs SPY benchmark",
        "",
        "| window | pass-rate (avg across datasets) | worst MDD across datasets |",
        "|---:|---:|---:|",
    ])
    rolling_pass = verdict["robustness"].get("rolling_pass_rates_avg_across_datasets", {})
    rolling_mdd = verdict["robustness"].get("rolling_worst_mdd_max_across_datasets", {})
    for w_str, pct in rolling_pass.items():
        try:
            w = int(w_str)
        except (TypeError, ValueError):
            w = w_str
        wmdd = rolling_mdd.get(w_str, float("nan"))
        pct_str = f"{pct*100:.1f}%" if isinstance(pct, (int, float)) and pct == pct else "n/a"
        wmdd_str = f"{wmdd*100:.2f}%" if isinstance(wmdd, (int, float)) and wmdd == wmdd else "n/a"
        lines.append(f"| {w}y | {pct_str} | {wmdd_str} |")
    lines.extend([
        "",
        f"Legacy 5y rolling-Sharpe (anchor `{verdict['robustness'].get('anchor_dataset', 'n/a')}`): "
        f"pct_positive = {verdict['robustness'].get('legacy_5y_sharpe_pct_positive', 0):.2%}, "
        f"n_windows = {verdict['robustness'].get('legacy_5y_sharpe_n_windows', 0)}",
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
