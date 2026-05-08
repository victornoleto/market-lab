"""T1 (Gayed replication) tier dispatcher per spec §2.2.

Dispatches T1a / T1b / T1c iterations.  Each config specifies one (on_asset,
off_asset, signal, period) combination.  The dispatcher:

  1. Loads underlying and synthesises LETF returns.
  2. Applies the SMA/EMA gate signal.
  3. Builds positions via single_letf_gayed.build_positions.
  4. Computes equity + metrics.
  5. Stubs gate values (real PBO/DSR/WF in later tiers).
  6. Scores with scoring.score_strategy.

LETF_UNDERLYING maps each on/off-asset to the testfolio ticker that best
approximates its daily returns.  Two approaches used:

  * Direct synth already in cache  → use as-is (e.g. UPROSIM for UPRO).
  * Not in cache → load nearest underlying + re-synth via letf_synth_by_ticker
    (e.g. TMF uses TLTSIM as the 20yr-treasury proxy).

Citations
---------
* Gayed canonical LRS signal: [leverage_for_the_long_run, p.13]
* LETF daily-return formula: [leverage_for_the_long_run, p.16, footnote 22-23]
* SPY Sharpe anchor lh_56y=0.682 from testfolio full-history backtest.
* SPY MDD anchor lh_56y=-0.5514 from testfolio full-history backtest.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.data_loader import (
    load_ffr_daily,
    load_testfolio_series,
    load_tiingo_real_etf,
)
from studies.letf_rotation_hunt.gates import (
    g1_pbo,
    g2_dsr_p_value,
    g3_walk_forward,
    g4_oos_70_30,
    g5_fwd_post_2020,
    g6_bootstrap_ci,
    g7_xlib_cagr_delta,
)
from studies.letf_rotation_hunt.plot_helper import (
    plot_crisis_attribution,
    plot_drawdown_curves,
    plot_equity_curves,
    plot_pct_beat_spy,
    plot_regime_attribution,
    plot_rolling_cagr,
    plot_rolling_sharpe,
    plot_sharpe_heatmap,
)
from studies.letf_rotation_hunt.scoring import (
    compute_metrics, crisis_beats_benchmark, score_strategy,
)
from studies.letf_rotation_hunt.signals import ema_gate, sma_gate
from studies.letf_rotation_hunt.strategies.single_letf_gayed import build_positions
from studies.letf_rotation_hunt.synths import letf_synth_by_ticker

# SPY anchor Sharpe per dataset — T1 competes against raw SPY [leverage_for_the_long_run, p.13]
# modern_1990 anchor measured 2026-05-06 from SPYSIM 1990-01-01..2026-04-30.
SPY_ANCHOR_SHARPE: dict[str, float] = {
    "lh_56y":      0.682,
    "modern_1990": 0.653,
    "spy_real":    0.671,   # corrected from prior 0.900 placeholder via SPYSIM 2003+
    "ndx_real":    0.900,   # NDX (QQQSIM) 2010+ — tech-heavy, high Sharpe
}

# SPY MDD per dataset (mandate §2.2/§2.3 — MDD warning-only).
SPY_MDD: dict[str, float] = {
    "lh_56y":      -0.5514,
    "modern_1990": -0.5514,
    "spy_real":    -0.5520,
    "ndx_real":    -0.3370,
}

# Dataset date windows. caller slices equity/returns by these bounds so
# per-dataset metrics reflect the actual benchmark window.
#
# - lh_56y: spec §2.2 canonical full-history (effective start 1986 via SPYSIM)
# - modern_1990: post-1987-crash, post-S&L, Fed-credible-era reference window
#   added 2026-05-06 at user request to test modern-era robustness; per the
#   empirical SPY survey, 1990 cutoff DOES NOT make SPY look better (Sharpe
#   0.653 vs 0.682 lh_56y) — but does make SPY-LETF rotation look better
#   (QLD lh_56y 0.678 → spy_real 0.816). Reported as additional informational
#   axis; KILL T0 still evaluates on lh_56y per spec §3.4 (canonical).
# - spy_real: Tiingo real SPY post-inception
# - ndx_real: Tiingo real QQQ post-inception
DATASET_WINDOWS: dict[str, tuple[str, str]] = {
    "lh_56y":      ("1970-01-01", "2026-04-30"),
    "modern_1990": ("1990-01-01", "2026-04-30"),
    "spy_real":    ("2003-01-01", "2026-04-30"),
    "ndx_real":    ("2010-02-01", "2026-04-30"),
}

# Sentinel metrics returned when a dataset window has insufficient data.
_NAN_METRICS: dict[str, float] = {
    "cagr": float("nan"),
    "mdd": float("nan"),
    "sharpe": float("nan"),
    "calmar": float("nan"),
    "vol_annual": float("nan"),
    "skew": float("nan"),
    "kurt": float("nan"),
    "turnover_annual": float("nan"),
    "pct_time_above_benchmark": float("nan"),
    "min_relative_equity": float("nan"),
}

# Mapping: on/off asset ticker → testfolio cache ticker
#
# Strategy:
#   - Direct LETF synths in cache: UPROSIM, SSOSIM, TQQQSIM, QLDSIM, UGLSIM
#     → use directly as LETF returns (no re-synthesis needed)
#   - SOXL not in cache → synthesise from QQQSIM underlying (best proxy)
#   - TMF not in cache → synthesise from TLTSIM underlying (20yr treasury)
#   - BIL → CASHX (FFR proxy in testfolio)
#   - IEF, TLT, ZROZ, EDV → IEF/TLT/ZROZ sim from cache
#
# "DIRECT" sentinel: use the cache ticker itself as already-synthesised LETF returns.
_DIRECT = "DIRECT"

# (on/off asset) → (testfolio_ticker, is_direct_letf)
# is_direct_letf=True: testfolio series already is a LETF synth; no re-synthesis
# is_direct_letf=False: testfolio series is an underlying; call letf_synth_by_ticker
LETF_TESTFOLIO: dict[str, tuple[str, bool]] = {
    # --- leveraged long equity ---
    "UPRO":  ("UPROSIM", True),   # 3x SPY — direct synth in cache
    "SSO":   ("SSOSIM",  True),   # 2x SPY — direct synth in cache
    "TQQQ":  ("TQQQSIM", True),   # 3x QQQ — direct synth in cache
    "QLD":   ("QLDSIM",  True),   # 2x QQQ — direct synth in cache
    # UGL: was direct UGLSIM, switched to GLDSIM resynth after iter 000 v2
    # calibration (UGLSIM under-models gold-LETF tracking drag by ~3pp/yr).
    # synths.LETF_EXPENSE_RATIOS["UGL"]=0.030 calibrates real UGL 2008-2026.
    "UGL":   ("GLDSIM",  False),  # 2x Gold — re-synth from GLDSIM (calibrated)
    # SOXL (3x SOX): no SOXSIM in cache; QQQSIM is nearest proxy per spec §4.4 note
    "SOXL":  ("QQQSIM",  False),  # re-synth 3x from QQQSIM underlying
    # --- leveraged treasury ---
    # TMF (3x 20yr): no TMFSIM in cache; use TLTSIM (20yr proxy)
    "TMF":   ("TLTSIM",  False),  # re-synth 3x from TLTSIM underlying
    # --- unlevered bonds / defensive ---
    "ZROZ":  ("ZROZSIM", True),   # 25yr strip — direct sim in cache (leverage=1)
    "IEF":   ("IEFSIM",  True),   # 7-10yr — direct sim in cache
    "TLT":   ("TLTSIM",  True),   # 20yr — direct sim in cache
    "EDV":   ("TLTSIM",  True),   # vanguard extended duration ≈ TLTSIM (best proxy)
    # --- cash proxy ---
    "BIL":   ("CASHX",   True),   # T-bill proxy = CASHX (daily FFR compound)
}


def run(config: dict, verdict: dict, out_dir: Path) -> dict:
    """Run T1 sub-fase iteration (a/b/c).

    Parameters
    ----------
    config:
        Loaded iter config YAML dict (tier must be T1a/T1b/T1c).
    verdict:
        Scaffold verdict dict to fill and return.
    out_dir:
        Output directory (plots/, tables/, logs/ already created by run_iter.py).

    Returns
    -------
    dict
        Updated verdict dict (schema-compliant).
    """
    tier = config["tier"]
    if tier not in ("T1a", "T1b", "T1c", "T1d"):
        raise ValueError(f"run_iter_t1 expects T1a/T1b/T1c/T1d, got {tier!r}")

    ffr_daily = load_ffr_daily()
    results: list[dict] = []
    n_trials_local = len(config["configs_tested"])
    n_trials_cumulative = max(
        1,
        int(config.get("cumulative_n_trials_at_iter", 0)) + n_trials_local,
    )

    for cfg in config["configs_tested"]:
        try:
            result = _run_single_config(
                cfg, config["datasets"], ffr_daily, n_trials_local=n_trials_local,
            )
            results.append(result)
        except Exception as exc:
            results.append({
                "config_name": cfg.get("name", "unknown"),
                "error": str(exc),
                "metrics_gross": {},
                "metrics_net": {},
                "score_breakdown": {},
                "tier_label": "ERROR",
            })

    # G1 PBO is a cross-config gate — compute once over all valid configs and
    # stamp onto each result. G2 cumulative DSR is recomputed per-config with
    # the cumulative trial count (spec §3.6 hybrid contract). Then re-score
    # each config so tier_label reflects the cross-config-aware gates.
    valid_results = [r for r in results if "error" not in r]
    per_cfg_returns = {
        r["config_name"]: r["_strategy_returns"]
        for r in valid_results
        if "_strategy_returns" in r
    }
    g1_result = g1_pbo(per_cfg_returns) if per_cfg_returns else {
        "pbo": float("nan"), "n_combinations": 0, "pass_gate": True,
    }
    for r in valid_results:
        r["gates"]["g1_pbo"] = float(g1_result["pbo"])
        r["gates"]["g1_pbo_n_combinations"] = int(g1_result["n_combinations"])
        if "_strategy_returns" in r:
            g2_cum = g2_dsr_p_value(
                r["_strategy_returns"], n_trials=max(2, n_trials_cumulative),
            )
            r["gates"]["g2_dsr_p_cumulative"] = float(g2_cum["p_value"])

        # Re-score with the now-populated G1 / G2-cumulative.
        cached = r.pop("_score_inputs")
        score = score_strategy(
            cached["metrics"], cached["anchors"], cached["spy_mdds"],
            r["gates"], cached["crisis"],
        )
        r["score_breakdown"] = score
        r["tier_label"] = score["tier_label"]
        r["winner_conditions_met"] = bool(score.get("winner_conditions_met", False))

    # Pick best config by Sharpe on lh_56y (primary dataset)
    if not valid_results:
        verdict["best_config"] = ""
        verdict["best_score"] = 0.0
        verdict["best_tier"] = "FAIL"
    else:
        best = max(
            valid_results,
            key=lambda r: r["metrics_gross"].get("lh_56y", {}).get("sharpe", -999),
        )
        verdict["best_config"] = best["config_name"]
        verdict["best_score"] = best.get("score_breakdown", {}).get("total", 0.0)
        verdict["best_tier"] = best.get("tier_label", "FAIL")

    # KILL T0 evaluation (per spec §3.4 + KILL_RULES.md): single-LETF rotation
    # must beat SPY+0.05 on lh_56y or the study is effectively non-viable.
    kill_t0_status = _evaluate_kill_t0(verdict, valid_results)
    verdict["kill_rule_status"] = kill_t0_status

    # T1 always advances per spec §3.4 (KILL is informational, loop continues).
    verdict["advance_to_next_tier"] = True

    # Write artifacts (SUMMARY.md, plots, CSVs) BEFORE stripping internal keys.
    if valid_results:
        _write_iter_artifacts(config, verdict, valid_results, out_dir, kill_t0_status)

    # Strip internal-only fields (not JSON-serializable / verdict.json hygiene).
    for r in valid_results:
        r.pop("_strategy_returns", None)
        r.pop("_equity", None)
        r.pop("_signal", None)
        r.pop("_positions", None)
        r.pop("_asset_returns_aligned", None)

    verdict["results"] = results
    return verdict


def _evaluate_kill_t0(verdict: dict, valid_results: list[dict]) -> str:
    """KILL T0: T1-best Sharpe on lh_56y vs SPY anchor + 0.05 threshold.

    Returns ``"PASS"`` / ``"FIRES"`` / ``"N/A"`` per KILL_RULES.md.
    Informational only — loop continues; result drives BASE_MEMORY tag.
    """
    if not valid_results:
        return "N/A"
    best_sharpe = max(
        r["metrics_gross"].get("lh_56y", {}).get("sharpe", float("-inf"))
        for r in valid_results
    )
    spy_anchor = SPY_ANCHOR_SHARPE.get("lh_56y", 0.682)
    edge = best_sharpe - spy_anchor
    return "PASS" if edge >= 0.05 else "FIRES"


def _write_iter_artifacts(
    config: dict, verdict: dict, valid_results: list[dict],
    out_dir: Path, kill_t0_status: str,
) -> None:
    """Write SUMMARY.md, plots/01-07.png, tables/*.csv per spec §5.1+§5.3."""
    plots_dir = out_dir / "plots"
    tables_dir = out_dir / "tables"
    plots_dir.mkdir(exist_ok=True)
    tables_dir.mkdir(exist_ok=True)

    equity_curves: dict[str, pd.Series] = {
        r["config_name"]: r["_equity"]
        for r in valid_results if "_equity" in r
    }
    signal_per_config: dict[str, pd.Series] = {
        r["config_name"]: r["_signal"]
        for r in valid_results if "_signal" in r
    }

    # SPY benchmark for plots that need it (lh_56y window via SPYSIM)
    spy_equity = load_testfolio_series("SPYSIM").dropna()

    iter_id = config["iter"]
    title_base = f"{iter_id} — {config.get('tier', 'T1')}"

    # For large grids (e.g. T1d 360 configs) line plots become illegible.
    # Filter to top-15 configs by lh_56y Sharpe; plot the rest only as heatmap.
    PLOT_LIMIT = 15
    if len(equity_curves) > PLOT_LIMIT:
        top_names = [
            r["config_name"] for r in
            sorted(valid_results,
                   key=lambda r: r["metrics_gross"].get("lh_56y", {}).get("sharpe", -999),
                   reverse=True)[:PLOT_LIMIT]
        ]
        equity_curves_for_lines = {n: equity_curves[n] for n in top_names if n in equity_curves}
        signal_for_lines = {n: signal_per_config[n] for n in top_names if n in signal_per_config}
        line_title_suffix = f" (top {PLOT_LIMIT} by Sharpe)"
    else:
        equity_curves_for_lines = equity_curves
        signal_for_lines = signal_per_config
        line_title_suffix = ""

    plot_curves_with_spy = {**equity_curves_for_lines, "SPY 1× b&h": spy_equity}

    plot_equity_curves(plot_curves_with_spy, plots_dir / "01_equity_curves.png",
                       title=f"{title_base} — Equity curves (log){line_title_suffix}")
    plot_drawdown_curves(plot_curves_with_spy, plots_dir / "02_drawdown_curves.png",
                         title=f"{title_base} — Drawdown{line_title_suffix}")
    plot_rolling_sharpe(plot_curves_with_spy, plots_dir / "03_rolling_sharpe_5y.png",
                        title=f"{title_base} — Rolling 5y Sharpe{line_title_suffix}")
    plot_rolling_cagr(plot_curves_with_spy, plots_dir / "04_rolling_cagr_3y.png",
                      title=f"{title_base} — Rolling 3y CAGR{line_title_suffix}")
    plot_regime_attribution(equity_curves_for_lines, signal_for_lines,
                            plots_dir / "05_regime_attribution.png",
                            title=f"{title_base} — % time signal=ON{line_title_suffix}")
    plot_pct_beat_spy(equity_curves_for_lines, spy_equity,
                      plots_dir / "06_pct_beat_spy.png",
                      title=f"{title_base} — % 3y windows beating SPY{line_title_suffix}")
    plot_crisis_attribution(equity_curves_for_lines, spy_equity,
                            plots_dir / "07_crisis_attribution.png",
                            title=f"{title_base} — Drawdown per crisis vs SPY{line_title_suffix}")

    # For grid sweeps (T1d-style), add 08_sharpe_heatmap.png — the full N-config
    # picture by (on, period, signal) × off rows-and-cols.
    if len(valid_results) > PLOT_LIMIT:
        heatmap_df = _build_sharpe_heatmap_df(valid_results)
        if heatmap_df is not None and not heatmap_df.empty:
            plot_sharpe_heatmap(
                heatmap_df, plots_dir / "08_sharpe_heatmap.png",
                title=f"{title_base} — Sharpe (lh_56y) heatmap, full grid",
            )

    _write_metrics_csv(valid_results, tables_dir / "per_config_metrics.csv")
    _write_gates_csv(valid_results, tables_dir / "gates_pass_fail.csv")

    summary_path = out_dir / "SUMMARY.md"
    summary_path.write_text(_render_summary(config, verdict, valid_results, kill_t0_status))


def _build_sharpe_heatmap_df(valid_results: list[dict]) -> pd.DataFrame | None:
    """Reshape per-config Sharpes into a (on×signal×period) × off matrix.

    Used by plot_sharpe_heatmap for T1d-style large grids. Each config is
    expected to have keys ``config_name`` and gates+metrics; the grouping is
    inferred from the config_name format ``<on>_<sig><period>_off_<off>``
    (the convention used in iter_004 T1d configs).

    Returns None if any name fails to parse.
    """
    rows = []
    for r in valid_results:
        name = r["config_name"]
        m = r["metrics_gross"].get("lh_56y", {})
        sharpe = m.get("sharpe", float("nan"))
        # Parse name like "qld_sma200_off_zroz" → on=qld, sig=sma, period=200, off=zroz
        try:
            on, sigp, _off_lit, off = name.split("_")
            sig = "sma" if sigp.startswith("sma") else "ema" if sigp.startswith("ema") else "?"
            period = int(sigp.replace("sma", "").replace("ema", ""))
        except (ValueError, AttributeError):
            return None
        rows.append({
            "row_label": f"{on.upper()} {sig.upper()}{period}",
            "off": off.upper(),
            "sharpe": sharpe,
        })
    if not rows:
        return None
    df = pd.DataFrame(rows)
    pivot = df.pivot(index="row_label", columns="off", values="sharpe")
    # Sort rows: group by on then period for readable layout
    pivot = pivot.sort_index()
    return pivot


def _write_metrics_csv(valid_results: list[dict], out_path: Path) -> None:
    """One row per (config, dataset) with cagr/mdd/sharpe/calmar/vol/skew/kurt."""
    rows = []
    for r in valid_results:
        for ds, m in r["metrics_gross"].items():
            rows.append({
                "config": r["config_name"], "dataset": ds,
                "cagr": m.get("cagr"), "mdd": m.get("mdd"),
                "sharpe": m.get("sharpe"), "calmar": m.get("calmar"),
                "vol_annual": m.get("vol_annual"),
                "skew": m.get("skew"), "kurt": m.get("kurt"),
            })
    pd.DataFrame(rows).to_csv(out_path, index=False)


def _write_gates_csv(valid_results: list[dict], out_path: Path) -> None:
    """One row per config with all gate values + pass/fail flags.

    G3 pass logic uses the new benchmark-relative field
    ``g3_wf_windows_pass_pct_above_benchmark`` when present; falls back
    to legacy Sharpe-positivity + MDD<50% otherwise.
    """
    rows = []
    for r in valid_results:
        g = r["gates"]
        g3_pct_field = g.get("g3_wf_windows_pass_pct_above_benchmark")
        if g3_pct_field is not None:
            g3_pass = int(g3_pct_field) >= 5
        else:
            g3_pass = (
                int(g.get("g3_wf_windows_pass", 0)) >= 5
                and float(g.get("g3_wf_max_mdd", 1.0)) < 0.50
            )
        rows.append({
            "config": r["config_name"],
            "g1_pbo": g.get("g1_pbo"), "g1_pass": float(g.get("g1_pbo", 1.0)) < 0.5,
            "g2_dsr_p_local": g.get("g2_dsr_p_local"),
            "g2_pass": float(g.get("g2_dsr_p_local", 1.0)) < 0.05,
            "g2_dsr_p_cumulative": g.get("g2_dsr_p_cumulative"),
            "g3_wf_windows_pass_pct_above_benchmark": g3_pct_field,
            "g3_wf_windows_pass_sharpe_positive": g.get("g3_wf_windows_pass_sharpe_positive"),
            "g3_wf_max_mdd": g.get("g3_wf_max_mdd"),  # warning-only diagnostic
            "g3_pass": g3_pass,
            "g4_oos_sharpe": g.get("g4_oos_sharpe"),
            "g4_pass": float(g.get("g4_oos_sharpe", -1)) > 0,
            "g5_fwd_post2020_sharpe": g.get("g5_fwd_post2020_sharpe"),
            "g5_pass": float(g.get("g5_fwd_post2020_sharpe", -1)) > 0,
            "g6_bootstrap_99_low": g.get("g6_bootstrap_99_low"),
            "g6_pass": float(g.get("g6_bootstrap_99_low", -1)) > 0,
            "g7_xlib_cagr_delta": g.get("g7_xlib_cagr_delta"),
            "g7_pass": abs(float(g.get("g7_xlib_cagr_delta", 1))) <= 0.03,
        })
    pd.DataFrame(rows).to_csv(out_path, index=False)


def _render_summary(
    config: dict, verdict: dict, valid_results: list[dict], kill_t0_status: str,
) -> str:
    """SUMMARY.md per spec §5.3 — header, TL;DR, configs, results, gates, plots, verdict."""
    iter_id = config["iter"]
    tier = config["tier"]
    hypothesis = config.get("hypothesis", "")
    citation = config.get("primary_citation", "")
    engine_sha = verdict.get("engine_version", "unknown")
    n_configs = len(config.get("configs_tested", []))

    if valid_results:
        best_cfg = verdict.get("best_config", "")
        best_score = verdict.get("best_score", 0.0)
        best_tier_label = verdict.get("best_tier", "FAIL")
        best_lh = next(
            (r["metrics_gross"].get("lh_56y", {})
             for r in valid_results if r["config_name"] == best_cfg),
            {},
        )
        best_sharpe_lh = best_lh.get("sharpe", float("nan"))
        best_cagr_lh = best_lh.get("cagr", float("nan"))
        best_mdd_lh = best_lh.get("mdd", float("nan"))
    else:
        best_cfg = ""
        best_score = 0.0
        best_tier_label = "FAIL"
        best_sharpe_lh = best_cagr_lh = best_mdd_lh = float("nan")

    spy_anchor = SPY_ANCHOR_SHARPE.get("lh_56y", 0.682)
    edge_vs_spy = best_sharpe_lh - spy_anchor if best_sharpe_lh == best_sharpe_lh else float("nan")

    lines: list[str] = [
        f"# {iter_id} — SUMMARY",
        "",
        f"**Tier:** {tier}",
        f"**Hypothesis:** {hypothesis}",
        f"**Primary citation:** {citation}",
        f"**Engine SHA:** `{engine_sha}`",
        f"**Datetime UTC:** {verdict.get('datetime_utc', '')}",
        f"**Configs tested:** {n_configs}",
        "",
        "## TL;DR",
        "",
        f"Best config: **`{best_cfg}`** ({best_tier_label}, score {best_score:.1f}/100). "
        f"lh_56y: Sharpe {best_sharpe_lh:.3f} (edge vs SPY {edge_vs_spy:+.3f}), "
        f"CAGR {best_cagr_lh*100:.2f}%, MDD {best_mdd_lh*100:.1f}%.  "
        f"**KILL T0:** {kill_t0_status} "
        f"(threshold: T1-best Sharpe ≥ SPY+0.05 = {spy_anchor + 0.05:.3f}).",
        "",
        "## Configs tested",
        "",
        "| Name | on_asset | off_asset | signal | period |",
        "|------|---------|----------|--------|-------:|",
    ]
    for cfg in config.get("configs_tested", []):
        lines.append(
            f"| `{cfg.get('name', '?')}` | {cfg.get('on_asset', '?')} | "
            f"{cfg.get('off_asset', '?')} | {cfg.get('signal', '?')} | "
            f"{cfg.get('period', '?')} |"
        )
    lines += ["", "## Results — gross metrics per dataset", ""]

    datasets = config.get("datasets", ["lh_56y"])
    header_cells = ["Config"] + [f"{ds} Sharpe" for ds in datasets] + [f"{ds} CAGR" for ds in datasets] + [f"{ds} MDD" for ds in datasets]
    lines.append("| " + " | ".join(header_cells) + " |")
    lines.append("|" + "|".join(["---"] * len(header_cells)) + "|")
    for r in valid_results:
        row = [f"`{r['config_name']}`"]
        for ds in datasets:
            m = r["metrics_gross"].get(ds, {})
            v = m.get("sharpe", float("nan"))
            row.append(f"{v:.3f}" if v == v else "—")
        for ds in datasets:
            m = r["metrics_gross"].get(ds, {})
            v = m.get("cagr", float("nan"))
            row.append(f"{v*100:.2f}%" if v == v else "—")
        for ds in datasets:
            m = r["metrics_gross"].get(ds, {})
            v = m.get("mdd", float("nan"))
            row.append(f"{v*100:.1f}%" if v == v else "—")
        lines.append("| " + " | ".join(row) + " |")

    lines += [
        "",
        f"**SPY anchor (lh_56y):** Sharpe {spy_anchor:.3f}, MDD {SPY_MDD['lh_56y']*100:.1f}% "
        f"(mandate §2.2/§2.3 — MDD warning-only).",
        "",
        "## Gates per config",
        "",
        "| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |",
        "|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|",
    ]
    for r in valid_results:
        g = r["gates"]
        g3_pct = g.get("g3_wf_windows_pass_pct_above_benchmark")
        g3_n = g.get("g3_wf_n_windows", 8)
        g3_mdd = g.get("g3_wf_max_mdd", float("nan"))
        if g3_pct is not None:
            g3_str = (
                f"{g3_pct}/{g3_n} >SPY (MDD {g3_mdd*100:.0f}% warn)"
            )
        else:
            g3_str = f"{g.get('g3_wf_windows_pass', 0)}/{g3_n} (MDD {g3_mdd*100:.0f}%)"
        lines.append(
            f"| `{r['config_name']}` | "
            f"{g.get('g1_pbo', float('nan')):.3f} | "
            f"{g.get('g2_dsr_p_local', float('nan')):.4f} | "
            f"{g3_str} | "
            f"{g.get('g4_oos_sharpe', float('nan')):.3f} | "
            f"{g.get('g5_fwd_post2020_sharpe', float('nan')):.3f} | "
            f"{g.get('g6_bootstrap_99_low', float('nan')):.3f} | "
            f"{g.get('g7_xlib_cagr_delta', float('nan'))*100:.2f}pp | "
            f"{r.get('tier_label', '?')} |"
        )
    lines += [
        "",
        "Hard-gate thresholds (spec §3.5): G1 PBO < 0.50, G2 DSR p < 0.05, "
        "G3 ≥5/8 windows + MDD < 50%, G4/G5 Sharpe > 0, G6 99% CI low > 0, "
        "G7 |Δ| ≤ 3pp.",
        "",
        "## Plots",
        "",
        "- `plots/01_equity_curves.png` — log-scale equity per config + SPY benchmark",
        "- `plots/02_drawdown_curves.png` — peak-to-trough drawdown",
        "- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe",
        "- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR",
        "- `plots/05_regime_attribution.png` — % of time signal=ON per config",
        "- `plots/06_pct_beat_spy.png` — cumulative fraction of 3y windows where "
        "config beat SPY",
        "- `plots/07_crisis_attribution.png` — MDD per crisis window vs SPY",
        "",
        "## Tables",
        "",
        "- `tables/per_config_metrics.csv` — one row per (config, dataset)",
        "- `tables/gates_pass_fail.csv` — gate values + pass/fail flags",
        "",
        "## Verdict",
        "",
        f"- **Best config:** `{best_cfg}` ({best_tier_label}, score {best_score:.1f})",
        f"- **KILL T0:** {kill_t0_status} "
        f"({'edge < 0.05 → tag CLOSE_NO_VALUE' if kill_t0_status == 'FIRES' else 'study viable'})",
        f"- **Advance to next tier:** {'yes' if verdict.get('advance_to_next_tier') else 'no'}",
        f"- **Cumulative n_trials:** {verdict.get('cumulative_n_trials_at_iter', 0) + n_configs}",
        f"- **Deploy escalation eligible:** "
        f"{'yes' if verdict.get('deploy_escalation_eligible') else 'no'}",
        "",
        "## Conclusion",
        "",
    ]
    if kill_t0_status == "FIRES":
        lines.append(
            f"T1-best Sharpe {best_sharpe_lh:.3f} (lh_56y) sits below SPY+0.05 "
            f"= {spy_anchor + 0.05:.3f} — single-LETF Gayed rotation does not "
            "produce risk-adjusted edge over passive SPY in this universe. "
            "Per spec §3.4, KILL T0 is informational: T1b/T1c continue but "
            "tagged `CLOSE_NO_VALUE`; T2+ inheritance falls back to T1-best "
            "(spec §3.4 inheritance fallback)."
        )
    else:
        lines.append(
            f"T1-best Sharpe {best_sharpe_lh:.3f} (lh_56y) clears SPY+0.05 — "
            f"single-LETF Gayed rotation has prima-facie edge in this universe. "
            "Proceeding to T1b period sweep."
        )
    lines += ["", "## Next iter", ""]
    if tier == "T1a":
        lines.append(
            f"**T1b** — period sweep on best LETF (`{best_cfg.split('_')[0].upper() if best_cfg else 'tbd'}`): "
            "{SMA, EMA} × {50, 100, 150, 200, 250} = 10 configs. "
            "Anti-curve-fit: SMA200 is reference; alt period only \"wins\" if Sharpe > SMA200 + 0.05."
        )
    elif tier == "T1b":
        lines.append(
            "**T1c** — OFF-state sweep on best (LETF, period): "
            "{BIL, IEF, TLT, TMF, ZROZ, EDV} = 6 configs. "
            "Anti-curve-fit: BIL is reference; leveraged OFF (TMF) only wins if "
            "Sharpe > BIL_OFF + 0.10 AND MDD ≤ TMF_buy-hold_MDD/2."
        )
    elif tier == "T1c":
        lines.append("**T2** — HFEA-binary basket per spec §2.3.")
    return "\n".join(lines) + "\n"


def _run_single_config(
    cfg: dict, datasets: list[str], ffr_daily: pd.Series, n_trials_local: int = 1,
) -> dict:
    """Run a single (on_asset × signal × off_asset) config on each dataset.

    Parameters
    ----------
    cfg:
        Config dict with keys: name, on_asset, off_asset, signal, period.
    datasets:
        List of dataset labels (e.g. ["lh_56y"]).
    ffr_daily:
        Daily FFR return series (CASHX.pct_change()).

    Returns
    -------
    dict
        Result dict per verdict schema results[] item.

    Raises
    ------
    ValueError
        If on_asset/off_asset is not in LETF_TESTFOLIO.
    KeyError
        If testfolio ticker is missing from cache.
    """
    on_asset: str = cfg["on_asset"]
    off_asset: str = cfg["off_asset"]
    signal_name: str = cfg["signal"]
    period: int = cfg.get("period", 200)

    # --- resolve on_asset returns ---
    if on_asset not in LETF_TESTFOLIO:
        raise ValueError(
            f"No testfolio mapping for on_asset={on_asset!r}. "
            f"Known: {sorted(LETF_TESTFOLIO)}"
        )
    on_tf_ticker, on_is_direct = LETF_TESTFOLIO[on_asset]
    on_series = load_testfolio_series(on_tf_ticker)

    if on_is_direct:
        # Already a synthesised LETF — use pct_change directly
        on_returns = on_series.pct_change().dropna()
    else:
        # Underlying series → re-synthesise via FFR-aware formula
        underlying_returns = on_series.pct_change().dropna()
        on_returns = letf_synth_by_ticker(on_asset, underlying_returns, ffr_daily)

    # --- resolve off_asset returns ---
    if off_asset not in LETF_TESTFOLIO:
        raise ValueError(
            f"No testfolio mapping for off_asset={off_asset!r}. "
            f"Known: {sorted(LETF_TESTFOLIO)}"
        )
    off_tf_ticker, off_is_direct = LETF_TESTFOLIO[off_asset]
    off_series = load_testfolio_series(off_tf_ticker)

    if off_is_direct:
        off_returns = off_series.pct_change().dropna()
    else:
        off_under_returns = off_series.pct_change().dropna()
        off_returns = letf_synth_by_ticker(off_asset, off_under_returns, ffr_daily)

    # --- signal: computed on the UNDERLYING price of on_asset ---
    # Per [leverage_for_the_long_run, p.13]: Gayed applies SMA200 to SPY (not UPRO)
    underlying_prices = on_series  # use testfolio ticker of on_asset as price input
    if signal_name == "sma":
        signal = sma_gate(underlying_prices, period=period)
    elif signal_name == "ema":
        signal = ema_gate(underlying_prices, period=period)
    else:
        raise ValueError(f"Unknown signal: {signal_name!r}")

    # --- positions + equity ---
    positions = build_positions(signal, on_asset, off_asset)

    asset_returns = pd.DataFrame({on_asset: on_returns, off_asset: off_returns})
    # Inner join: all three (positions, on_returns, off_returns) must be present
    aligned = positions.join(asset_returns, lsuffix="_w", rsuffix="_r", how="inner").dropna()
    if len(aligned) < 252:
        raise ValueError(
            f"Insufficient aligned data after join: {len(aligned)} rows "
            f"(need >= 252 for {on_asset}/{off_asset})"
        )

    strategy_returns = (
        aligned[f"{on_asset}_w"].shift(1) * aligned[f"{on_asset}_r"]
        + aligned[f"{off_asset}_w"].shift(1) * aligned[f"{off_asset}_r"]
    ).dropna()

    equity = (1 + strategy_returns).cumprod() * 10_000

    # --- metrics per dataset (sliced by DATASET_WINDOWS) ---
    # SPY benchmark loaded once per call; sliced to each dataset window.
    # Used to populate underwater-vs-benchmark metrics (scoring v2 §3.2).
    spy_full = load_testfolio_series("SPYSIM").dropna()
    metrics_per_dataset: dict[str, dict] = {}
    for ds in datasets:
        win = DATASET_WINDOWS.get(ds)
        if win is None:
            ds_eq, ds_ret = equity, strategy_returns
            ds_bench = spy_full
        else:
            start, end = win
            mask_eq = (equity.index >= start) & (equity.index <= end)
            mask_ret = (strategy_returns.index >= start) & (strategy_returns.index <= end)
            mask_bench = (spy_full.index >= start) & (spy_full.index <= end)
            ds_eq = equity[mask_eq]
            ds_ret = strategy_returns[mask_ret]
            ds_bench = spy_full[mask_bench]
        if len(ds_ret) < 252 or len(ds_eq) < 2:
            metrics_per_dataset[ds] = dict(_NAN_METRICS)
        else:
            metrics_per_dataset[ds] = compute_metrics(ds_eq, ds_ret, benchmark_equity=ds_bench)

    # --- real gates (G2-G7 per-config; G1 + G2-cumulative stamped in run()) ---
    # Spec §3.5 + §3.6 hybrid: local n_trials for hard gate, cumulative for
    # study-winner reporting. G1 PBO needs cross-config alignment (run-level).
    g2 = g2_dsr_p_value(strategy_returns, n_trials=max(2, n_trials_local))
    spy_returns_full = spy_full.pct_change().dropna()
    g3 = g3_walk_forward(strategy_returns, benchmark_returns=spy_returns_full)
    g4 = g4_oos_70_30(strategy_returns)
    g5 = g5_fwd_post_2020(strategy_returns)
    g6 = g6_bootstrap_ci(strategy_returns)
    g7 = g7_xlib_cagr_delta(strategy_returns)
    gates = {
        "g1_pbo": float("nan"),                 # filled by run() after all configs
        "g1_pbo_n_combinations": 0,             # filled by run()
        "g2_dsr_p_local": float(g2["p_value"]),
        "g2_dsr_p_cumulative": float("nan"),    # filled by run() with cumulative n_trials
        "g2_observed_sharpe": float(g2["observed_sharpe"]),
        "g3_wf_windows_pass": int(g3["windows_pass"]),
        "g3_wf_windows_pass_pct_above_benchmark": int(g3["windows_pass_pct_above_benchmark"]),
        "g3_wf_windows_pass_sharpe_positive": int(g3["windows_pass_sharpe_positive"]),
        "g3_wf_n_windows": int(g3["n_windows"]),
        "g3_wf_max_mdd": float(g3["max_mdd"]) if not pd.isna(g3["max_mdd"]) else float("nan"),
        "g3_wf_warmup_used_days": int(g3.get("warmup_used_days", 0)),
        "g3_wf_benchmark_relative": bool(g3.get("benchmark_relative", False)),
        "g4_oos_sharpe": float(g4["oos_sharpe"]),
        "g5_fwd_post2020_sharpe": float(g5["fwd_sharpe"]),
        "g5_fwd_n_obs": int(g5["n_obs_post_2020"]),
        "g6_bootstrap_99_low": float(g6["ci_low_sharpe"]),
        "g7_xlib_cagr_delta": float(g7["delta_pp"] / 100.0),  # pp→fraction (scoring contract)
    }

    # Crisis attribution — per-crisis pct_time_above_SPY (renormalised within
    # each crisis window). Mirrors underwater-vs-benchmark thesis at the
    # crisis-window level per user observation 2026-05-06.
    crisis = crisis_beats_benchmark(equity, spy_full)

    anchors = {ds: SPY_ANCHOR_SHARPE.get(ds, 0.7) for ds in datasets}
    spy_mdds = {ds: SPY_MDD.get(ds, -0.50) for ds in datasets}
    # Initial score (with NaN G1) — re-scored at run() level after G1 known
    score_result = score_strategy(metrics_per_dataset, anchors, spy_mdds, gates, crisis)

    # Aligned positions + per-asset returns for tax_comparison sub-study reuse.
    asset_returns_aligned = pd.DataFrame(
        {c: aligned[f"{c}_r"] for c in positions.columns}
    ).reindex(strategy_returns.index).dropna()
    positions_aligned = positions.reindex(strategy_returns.index).dropna()

    return {
        "config_name": cfg["name"],
        "metrics_gross": metrics_per_dataset,
        "metrics_net": {},
        "rolling_pct_beat_spy": {"3y": None, "5y": None, "10y": None},
        "crisis_mdd": {}, "crisis_beats_benchmark": dict(crisis),
        "gates": gates,
        "score_breakdown": score_result,
        "tier_label": score_result["tier_label"],
        "winner_conditions_met": score_result.get("winner_conditions_met", False),
        # Internal: stripped before verdict.json serialization in run()
        "_positions": positions_aligned,
        "_asset_returns_aligned": asset_returns_aligned,
        "_strategy_returns": strategy_returns,
        "_equity": equity,
        "_signal": signal.reindex(strategy_returns.index).fillna(0).astype(float),
        "_score_inputs": {
            "metrics": metrics_per_dataset,
            "anchors": anchors,
            "spy_mdds": spy_mdds,
            "crisis": crisis,
        },
    }
