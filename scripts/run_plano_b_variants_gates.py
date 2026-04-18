#!/usr/bin/env python3
"""Phase 3.5b — 5-gate evaluation for V1/V2/V3/V4 portfolio variants.

Tests the LETF-execution variants through the canonical 5-gate battery
used in Phase 3 b1c (LETF rotation) and a3d (3-leg portfolio):

1. **OOS Sharpe > 0** (out-of-sample, uncorrelated with selection).
2. **Stress Sharpe > 0** (post-cutoff regime).
3. **Walk-forward 6/8 + MaxDD ≤ 25%** per window
   (``walk_forward_verdict_from_returns``).
4. **Deflated Sharpe p < 0.05** with ``n_trials=4`` (the 4 variants).
5. **Stationary-bootstrap 99.9% CI lower bound > 0**
   (``bootstrap_sharpe_ci``).

Two windows evaluated, following Phase 3.5b supplementary-evidence
pattern:

* **Canonical 2004-2026** — authoritative verdict.
  IS 2004-11-18 → 2014-12-31 (~10y) /
  OOS 2015-01-01 → 2019-12-31 (~5y) /
  Stress 2020-01-01 → 2026-04-17 (~6.3y).
* **Extended 1986-2026 (supplementary)** — cross-check via testfol.io.
  IS 1986-01-02 → 2010-12-31 (~25y) /
  OOS 2011-01-01 → 2019-12-31 (~9y) /
  Stress 2020-01-01 → 2026-04-17 (~6.3y).

Emits under ``reports/phase3_5b/variants_letf_execution/``:

* ``gates_verdict.json`` — per-variant per-window per-gate results.
* ``gates_verdict.md`` — ordered best-to-worst table + narrative.

Citations
---------
* PBO/CSCV/DSR framework: ``[advances_fin_ml, p.208-211, p.273-275]``.
* Stationary block bootstrap: ``[advances_fin_ml, p.196-202]``.
* WF ≥ 6/8 gate: ``docs/investment-mandate.md`` §5.
* MaxDD ≤ 25%: mandate §5.
* testfol.io ground truth: Phase 3.5b Task 7a.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from ai_trade.backtest.data.testfolio_loader import load_testfolio_series
from ai_trade.backtest.grid.letf_rotation_b1c import (
    bootstrap_sharpe_ci,
    walk_forward_verdict_from_returns,
)
from ai_trade.backtest.metrics.rebalance_modes import apply_threshold_rebalance
from ai_trade.backtest.strategies.letf_rotation import compute_regime_signal
from ai_trade.backtest.strategies.tsmom import compute_donchian_signal
from ai_trade.backtest.validation.dsr import dsr

log = logging.getLogger("plano_b_variants_gates")

# Signal configs (identical to production winner).
LETF_LOOKBACK = 100
QQQ_ENTRY, QQQ_EXIT = 20, 10
GLD_ENTRY, GLD_EXIT = 40, 20
SWITCH_COST_PCT = (10.0 + 5.0) / 10_000.0
TAX_RATE = 0.15
THRESHOLD_PP = 10.0
PERIODS_PER_YEAR = 252

VARIANTS = {
    "V1_SSO_QQQ_GLD":  {"leg1": "SSOSIM", "leg2": "QQQSIM", "leg3": "GLDSIM"},
    "V2_SSO_QLD_GLD":  {"leg1": "SSOSIM", "leg2": "QLDSIM", "leg3": "GLDSIM"},
    "V3_SSO_QQQ_UGL":  {"leg1": "SSOSIM", "leg2": "QQQSIM", "leg3": "UGLSIM"},
    "V4_SSO_QLD_UGL":  {"leg1": "SSOSIM", "leg2": "QLDSIM", "leg3": "UGLSIM"},
}

# Gate thresholds (mandate §5).
GATE_WF_MIN_RATIO = 6 / 8
GATE_WF_MAX_DD = 0.25
GATE_DSR_ALPHA = 0.05
GATE_BOOTSTRAP_ALPHA = 0.001   # 99.9% CI
N_TRIALS_DSR = 4               # 4 portfolio variants tested

# Window splits.
WINDOWS = {
    "canonical_2004_2026": {
        "IS":     ("2004-11-18", "2014-12-31"),
        "OOS":    ("2015-01-01", "2019-12-31"),
        "Stress": ("2020-01-01", "2026-04-17"),
    },
    "extended_1986_2026": {
        "IS":     ("1986-01-02", "2010-12-31"),
        "OOS":    ("2011-01-01", "2019-12-31"),
        "Stress": ("2020-01-01", "2026-04-17"),
    },
}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output-dir", type=Path,
                    default=Path("reports/phase3_5b/variants_letf_execution"))
    ap.add_argument("--log-level", default="INFO")
    return ap.parse_args(argv)


def _apply_regime_to_execution(
    in_position: pd.Series,
    execution_returns: pd.Series,
    switch_cost_pct: float,
    tax_rate: float,
) -> pd.Series:
    """Daily net returns for a leg: execution gated by in_position.

    Switch costs deducted on every transition; 15% realized-gain tax on
    ``True → False`` (exit). Identical mechanic to the parent script
    ``run_plano_b_variants_letf_execution.py``.
    """
    if not in_position.index.equals(execution_returns.index):
        raise ValueError("index mismatch")
    daily_net = pd.Series(0.0, index=in_position.index)
    equity = 1.0
    entry_equity = 1.0
    prev_state = False
    for ts in in_position.index:
        now_state = bool(in_position.loc[ts])
        prev_equity = equity
        if now_state != prev_state:
            equity -= equity * switch_cost_pct
            if prev_state:
                gain = max(0.0, equity - entry_equity)
                equity -= gain * tax_rate
            if now_state:
                entry_equity = equity
            prev_state = now_state
        if now_state:
            r = float(execution_returns.loc[ts])
            equity *= (1.0 + r)
        daily_net.loc[ts] = (equity / prev_equity - 1.0) if prev_equity > 0 else 0.0
    return daily_net


def _build_portfolio_returns(
    variant_name: str, variant_legs: dict[str, str],
    spy: pd.Series, qqq: pd.Series, gld: pd.Series,
    leg_series: dict[str, pd.Series],
) -> pd.Series:
    """Build the 3-leg net returns for a variant, post-rebalance."""
    sso_ret = leg_series[variant_legs["leg1"]].pct_change().fillna(0.0)
    qqq_exec_ret = leg_series[variant_legs["leg2"]].pct_change().fillna(0.0)
    gld_exec_ret = leg_series[variant_legs["leg3"]].pct_change().fillna(0.0)

    # Leg 1 — SSO via EMA100 regime on SPYSIM.
    sso_regime = compute_regime_signal(
        spy, filter="EMA", lookback=LETF_LOOKBACK, band_pct=0.0,
    )
    in_sso = (sso_regime == "ON").astype(bool).reindex(
        sso_ret.index, fill_value=False,
    )
    leg_sso = _apply_regime_to_execution(
        in_sso, sso_ret, SWITCH_COST_PCT, TAX_RATE,
    )

    # Leg 2 — QQQ/QLD via Donchian 20/10 on QQQSIM.
    qqq_signal = compute_donchian_signal(
        qqq, qqq, qqq, QQQ_ENTRY, QQQ_EXIT,
    )
    in_qqq = (qqq_signal == "LONG").astype(bool).reindex(
        qqq_exec_ret.index, fill_value=False,
    )
    leg_qqq = _apply_regime_to_execution(
        in_qqq, qqq_exec_ret, SWITCH_COST_PCT, TAX_RATE,
    )

    # Leg 3 — GLD/UGL via Donchian 40/20 on GLDSIM.
    gld_signal = compute_donchian_signal(
        gld, gld, gld, GLD_ENTRY, GLD_EXIT,
    )
    in_gld = (gld_signal == "LONG").astype(bool).reindex(
        gld_exec_ret.index, fill_value=False,
    )
    leg_gld = _apply_regime_to_execution(
        in_gld, gld_exec_ret, SWITCH_COST_PCT, TAX_RATE,
    )

    rdf = pd.DataFrame({
        "leg1": leg_sso, "leg2": leg_qqq, "leg3": leg_gld,
    }).dropna()
    result = apply_threshold_rebalance(
        returns_df=rdf,
        target_weights={"leg1": 1 / 3, "leg2": 1 / 3, "leg3": 1 / 3},
        threshold_pp=THRESHOLD_PP,
        initial_capital=1.0,
        tax_rate=TAX_RATE,
    )
    return result.equity.pct_change().dropna()


def _annualized_sharpe(returns: pd.Series) -> float:
    r = returns.dropna()
    if len(r) < 2:
        return 0.0
    std = float(r.std())
    if std == 0:
        return 0.0
    return float(r.mean()) * PERIODS_PER_YEAR / (std * np.sqrt(PERIODS_PER_YEAR))


def _cagr(returns: pd.Series) -> float:
    if len(returns) < 2:
        return 0.0
    cum = float((1.0 + returns).prod())
    years = len(returns) / PERIODS_PER_YEAR
    return cum ** (1.0 / years) - 1.0 if years > 0 and cum > 0 else 0.0


def _max_drawdown(returns: pd.Series) -> float:
    eq = (1.0 + returns).cumprod()
    peak = eq.cummax()
    dd = (peak - eq) / peak
    return float(dd.max())


def _slice(returns: pd.Series, start: str, end: str) -> pd.Series:
    s = pd.Timestamp(start)
    e = pd.Timestamp(end)
    return returns.loc[(returns.index >= s) & (returns.index <= e)]


def _evaluate_variant_in_window(
    returns: pd.Series,
    window_spec: dict[str, tuple[str, str]],
    n_trials: int,
) -> dict:
    """Run the 5 gates on ``returns`` inside the given window_spec."""
    full_start, full_end = (
        window_spec["IS"][0], window_spec["Stress"][1],
    )
    full = _slice(returns, full_start, full_end)
    is_ret = _slice(returns, *window_spec["IS"])
    oos_ret = _slice(returns, *window_spec["OOS"])
    stress_ret = _slice(returns, *window_spec["Stress"])

    is_sharpe = _annualized_sharpe(is_ret)
    oos_sharpe = _annualized_sharpe(oos_ret)
    stress_sharpe = _annualized_sharpe(stress_ret)

    # Per-window metrics.
    per_window = {
        "IS":     {"sharpe": is_sharpe,
                   "cagr": _cagr(is_ret),
                   "max_dd": _max_drawdown(is_ret),
                   "bars": int(len(is_ret))},
        "OOS":    {"sharpe": oos_sharpe,
                   "cagr": _cagr(oos_ret),
                   "max_dd": _max_drawdown(oos_ret),
                   "bars": int(len(oos_ret))},
        "Stress": {"sharpe": stress_sharpe,
                   "cagr": _cagr(stress_ret),
                   "max_dd": _max_drawdown(stress_ret),
                   "bars": int(len(stress_ret))},
        "Full":   {"sharpe": _annualized_sharpe(full),
                   "cagr": _cagr(full),
                   "max_dd": _max_drawdown(full),
                   "bars": int(len(full))},
    }

    # Gate 3 — Walk-forward on full window (8 windows).
    wf_ratio, wf_max_dd, wf_pass = walk_forward_verdict_from_returns(
        full, n_windows=8,
        min_profitable_ratio=GATE_WF_MIN_RATIO,
        max_drawdown_cap=GATE_WF_MAX_DD,
    )

    # Gate 4 — DSR with n_trials.
    try:
        dsr_res = dsr(full.to_numpy(dtype=float), n_trials=n_trials)
        dsr_p = float(dsr_res.p_value)
    except Exception as exc:  # numerical degeneracies
        log.warning("DSR failed: %s", exc)
        dsr_p = float("nan")

    # Gate 5 — Stationary bootstrap 99.9% CI on OOS.
    boot_lo, boot_hi = bootstrap_sharpe_ci(
        oos_ret, alpha=GATE_BOOTSTRAP_ALPHA,
        block_mean=5, n_resamples=2000, seed=42,
    )

    gates = {
        "oos_sharpe_positive": {
            "value": oos_sharpe,
            "threshold": 0.0,
            "pass": bool(oos_sharpe > 0),
        },
        "stress_sharpe_positive": {
            "value": stress_sharpe,
            "threshold": 0.0,
            "pass": bool(stress_sharpe > 0),
        },
        "walk_forward": {
            "ratio": float(wf_ratio),
            "max_window_drawdown": float(wf_max_dd),
            "min_ratio": GATE_WF_MIN_RATIO,
            "max_dd_cap": GATE_WF_MAX_DD,
            "pass": bool(wf_pass),
        },
        "dsr": {
            "p_value": dsr_p,
            "alpha": GATE_DSR_ALPHA,
            "n_trials": n_trials,
            "pass": bool(not np.isnan(dsr_p) and dsr_p < GATE_DSR_ALPHA),
        },
        "bootstrap_ci_oos": {
            "alpha": GATE_BOOTSTRAP_ALPHA,
            "lower": float(boot_lo),
            "upper": float(boot_hi),
            "pass": bool(not np.isnan(boot_lo) and boot_lo > 0),
        },
    }

    all_pass = all(g["pass"] for g in gates.values())
    return {
        "window": window_spec,
        "metrics": per_window,
        "gates": gates,
        "verdict": "PASS" if all_pass else "FAIL",
        "failed_gates": [k for k, v in gates.items() if not v["pass"]],
    }


def _render_markdown(
    summary: dict, threshold_pp: float, output_path: Path,
) -> None:
    """Emit the human-readable verdict table ordered best-to-worst."""
    lines: list[str] = []
    lines.append("# Phase 3.5b — V1/V2/V3/V4 gate verdict\n")
    lines.append(f"**Threshold:** {threshold_pp:g}pp | **Tax:** 15% | "
                 "**Source:** testfol.io ground truth | "
                 "**Signals:** EMA100(SPY), Donchian 20/10 (QQQ), "
                 "Donchian 40/20 (GLD)\n")
    lines.append(f"**DSR n_trials:** {N_TRIALS_DSR} | "
                 "**WF windows:** 8 (≥6 profitable, ≤25% DD each) | "
                 "**Bootstrap:** 99.9% CI on OOS Sharpe (stationary block, "
                 "n_resamples=2000)\n")

    for win_key, win_results in summary["windows"].items():
        lines.append(f"\n## Window — `{win_key}`\n")
        win_spec = WINDOWS[win_key]
        lines.append(
            f"IS: `{win_spec['IS'][0]} → {win_spec['IS'][1]}`  |  "
            f"OOS: `{win_spec['OOS'][0]} → {win_spec['OOS'][1]}`  |  "
            f"Stress: `{win_spec['Stress'][0]} → {win_spec['Stress'][1]}`\n"
        )

        # Order variants by all_pass (PASS first) then by OOS Sharpe desc.
        ordered = sorted(
            win_results.items(),
            key=lambda kv: (
                kv[1]["verdict"] != "PASS",
                -kv[1]["metrics"]["OOS"]["sharpe"],
            ),
        )
        lines.append(
            "| Rank | Variant | Verdict | IS Sh | OOS Sh | Stress Sh | "
            "Full CAGR | Full MaxDD | WF ratio | WF max DD | DSR p | "
            "Boot 99.9% CI lo | Failed |"
        )
        lines.append(
            "|---:|---|:-:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
        )
        for rank, (vname, v) in enumerate(ordered, start=1):
            g = v["gates"]
            m = v["metrics"]
            failed = ", ".join(v["failed_gates"]) if v["failed_gates"] else "—"
            verdict_emoji = "✅ PASS" if v["verdict"] == "PASS" else "❌ FAIL"
            lines.append(
                f"| {rank} | {vname} | {verdict_emoji} "
                f"| {m['IS']['sharpe']:.3f} "
                f"| {m['OOS']['sharpe']:.3f} "
                f"| {m['Stress']['sharpe']:.3f} "
                f"| {m['Full']['cagr']*100:.2f}% "
                f"| {m['Full']['max_dd']*100:.2f}% "
                f"| {g['walk_forward']['ratio']:.2f} "
                f"| {g['walk_forward']['max_window_drawdown']*100:.2f}% "
                f"| {g['dsr']['p_value']:.4f} "
                f"| {g['bootstrap_ci_oos']['lower']:.3f} "
                f"| {failed} |"
            )
        lines.append("")

    lines.append("\n## Legend\n")
    lines.append(f"* **OOS Sharpe > 0** (gate 1) — simple sign test.")
    lines.append(f"* **Stress Sharpe > 0** (gate 2) — post-cutoff regime.")
    lines.append(f"* **WF ratio ≥ {GATE_WF_MIN_RATIO:.2f}** AND "
                 f"**per-window MaxDD ≤ {GATE_WF_MAX_DD*100:.0f}%** (gate 3) — "
                 f"8 windows over full range.")
    lines.append(f"* **DSR p < {GATE_DSR_ALPHA}** (gate 4) — "
                 f"multiple-testing adjusted Sharpe significance "
                 f"(n_trials={N_TRIALS_DSR}).")
    lines.append(f"* **Bootstrap 99.9% CI lower > 0** (gate 5) — "
                 f"stationary-block bootstrap on OOS returns.\n")

    lines.append("## Interpretação\n")
    lines.append("* Uma variante só é **promotable** se passar os 5 gates **no window canônico 2004-2026**.")
    lines.append("* O window supplementary 1986-2026 é **cross-check confirmatório** — PASS adicional eleva confiança; FAIL adicional é flag amarelo mas não bloqueio.")
    lines.append("* Ranking dentro do window ordena: (PASS > FAIL) e (OOS Sharpe desc).")
    lines.append("* **A decisão operacional vem do window canônico.**\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    log.info("loading testfol.io series …")
    spy = load_testfolio_series("SPYSIM")
    qqq = load_testfolio_series("QQQSIM")
    gld = load_testfolio_series("GLDSIM")
    sso = load_testfolio_series("SSOSIM")
    qld = load_testfolio_series("QLDSIM")
    ugl = load_testfolio_series("UGLSIM")
    leg_series = {"SSOSIM": sso, "QQQSIM": qqq, "QLDSIM": qld,
                  "GLDSIM": gld, "UGLSIM": ugl}

    # Build returns per variant.
    variant_returns: dict[str, pd.Series] = {}
    for name, legs in VARIANTS.items():
        log.info("building returns for %s …", name)
        variant_returns[name] = _build_portfolio_returns(
            name, legs, spy, qqq, gld, leg_series,
        )

    # Evaluate each variant in each window.
    summary = {
        "config": {
            "threshold_pp": THRESHOLD_PP,
            "tax_rate": TAX_RATE,
            "switch_cost_pct": SWITCH_COST_PCT,
            "n_trials_dsr": N_TRIALS_DSR,
            "data_source": "testfol.io (SSOSIM/QLDSIM/UGLSIM + SPYSIM/QQQSIM/GLDSIM)",
        },
        "windows": {},
    }

    for win_key, win_spec in WINDOWS.items():
        log.info("=== window %s ===", win_key)
        win_results: dict[str, dict] = {}
        for vname, rets in variant_returns.items():
            log.info("  evaluating %s …", vname)
            verdict = _evaluate_variant_in_window(rets, win_spec, n_trials=N_TRIALS_DSR)
            win_results[vname] = verdict
            failed = verdict["failed_gates"]
            log.info(
                "    verdict=%s | OOS Sh=%.3f | Stress Sh=%.3f | "
                "WF=%.2f/%.1f%% | DSR_p=%.4f | boot_lo=%.3f | failed=%s",
                verdict["verdict"],
                verdict["metrics"]["OOS"]["sharpe"],
                verdict["metrics"]["Stress"]["sharpe"],
                verdict["gates"]["walk_forward"]["ratio"],
                verdict["gates"]["walk_forward"]["max_window_drawdown"] * 100,
                verdict["gates"]["dsr"]["p_value"],
                verdict["gates"]["bootstrap_ci_oos"]["lower"],
                ",".join(failed) if failed else "—",
            )
        summary["windows"][win_key] = win_results

    json_path = args.output_dir / "gates_verdict.json"
    json_path.write_text(json.dumps(summary, indent=2, default=float),
                         encoding="utf-8")
    log.info("wrote JSON → %s", json_path)

    md_path = args.output_dir / "gates_verdict.md"
    _render_markdown(summary, THRESHOLD_PP, md_path)
    log.info("wrote MD   → %s", md_path)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
