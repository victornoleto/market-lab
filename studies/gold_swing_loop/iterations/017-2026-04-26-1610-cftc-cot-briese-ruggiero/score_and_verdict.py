"""Compute v2 score + assemble verdict.json for iter 017."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "studies" / "gold_swing_loop"))

from scoring import DatasetMetrics, Gates, score_strategy_v2  # noqa: E402

ITER_DIR = Path(__file__).resolve().parent
RES = json.loads((ITER_DIR / "results.json").read_text())

ds_gld = RES["datasets"]["gld_long"]
ds_xau = RES["datasets"]["xauusd_real"]


def _to_metrics(d):
    return DatasetMetrics(
        sharpe=d["metrics"]["sharpe"],
        cagr=d["metrics"]["cagr"],
        mdd=d["metrics"]["mdd"],
        dsr_p_value=d["dsr_p_value"],
    )


def _to_gates(d):
    g = d["gates"]
    return Gates(
        g1_pbo=g["g1_pbo"],
        g2_dsr=g["g2_dsr"],
        g3_wf=g["g3_wf"],
        g4_oos=g["g4_oos"],
        g5_fwd=g["g5_fwd"],
        g6_bootstrap=g["g6_bootstrap"],
        g7_crosslib=g["g7_crosslib"],
    )


metrics = {
    "gld_long": _to_metrics(ds_gld),
    "xauusd_real": _to_metrics(ds_xau),
}
gates = {
    "gld_long": _to_gates(ds_gld),
    "xauusd_real": _to_gates(ds_xau),
}

result = score_strategy_v2(
    metrics=metrics,
    gates=gates,
    cumulative_n_trials=RES["cumulative_n_trials"],
    declared_primary="gld_long",
    declared_corroborating=["xauusd_real"],
)

# Hold-time gate (6th condition, separate from score)
mean_hold_primary = ds_gld["metrics"]["mean_hold_days"]
hold_track = "medium_swing"  # declared in hypothesis.md
track_bounds = {"intraday": (0.0, 1.0), "short_swing": (2.0, 10.0), "medium_swing": (10.0, 30.0)}
lo, hi = track_bounds[hold_track]
hold_gate_pass = lo <= mean_hold_primary <= hi

# Pre-committed kill criteria
n_trades_gld = ds_gld["metrics"]["n_trades"]
sharpe_gld = ds_gld["metrics"]["sharpe"]
rho_gld_v_iter003 = (
    RES["correlation_diagnostic"]["gld_long"].get("iter003_rsi2_sma200", {}).get("rho")
)
kill_criteria = {
    "1_n_trades_gte_10": n_trades_gld >= 10,
    "2_sharpe_gte_0_30": sharpe_gld >= 0.30,
    "3_rho_iter003_lt_0_50": (rho_gld_v_iter003 is None) or (abs(rho_gld_v_iter003) < 0.50),
}
any_kill_fired = not all(kill_criteria.values())

is_winner = (
    result.winner_conditions_met
    and hold_gate_pass
    and not any_kill_fired
    and result.total_score >= 90
)

verdict = result.to_dict()
verdict.update({
    "iteration": "017",
    "hypothesis_slug": "cftc-cot-briese-ruggiero",
    "primary_citation": "[trading_systems_methods, p.639-640]",
    "configs_tested": 1,
    "cumulative_n_trials_after_iter": RES["cumulative_n_trials"],
    "broker_track": "pepperstone_cfd",
    "universe": "single_xau",
    "cost_path": "pep_cfd",
    "hold_time_track_declared": hold_track,
    "mean_hold_days_observed": mean_hold_primary,
    "hold_time_gate_pass": hold_gate_pass,
    "kill_criteria": kill_criteria,
    "any_kill_criterion_fired": any_kill_fired,
    "is_winner": is_winner,
    "timeframes_used": ["weekly_cot", "1d"],
    "track_a_metrics": {
        "gld_long": ds_gld["metrics"],
        "xauusd_real": ds_xau["metrics"],
    },
    "structural_orthogonality_finding": {
        "rho_vs_iter003_rsi2_sma200_gld_long": rho_gld_v_iter003,
        "rho_vs_iter011_volregime_gld_long":
            RES["correlation_diagnostic"]["gld_long"].get("iter011_volregime", {}).get("rho"),
        "rho_vs_iter015_dxy_trend_gld_long":
            RES["correlation_diagnostic"]["gld_long"].get("iter015_dxy_trend", {}).get("rho"),
        "rho_vs_iter003_rsi2_sma200_xauusd_real":
            RES["correlation_diagnostic"]["xauusd_real"].get("iter003_rsi2_sma200", {}).get("rho"),
    },
    "status": "winner" if is_winner else "iterating",
})

(ITER_DIR / "verdict.json").write_text(
    json.dumps(verdict, indent=2, default=str), encoding="utf-8"
)

print(json.dumps({
    "tier": result.tier.value,
    "score": result.total_score,
    "winner_conditions_met": result.winner_conditions_met,
    "hold_time_gate": "pass" if hold_gate_pass else "fail",
    "kill_criteria": kill_criteria,
    "any_kill_fired": any_kill_fired,
    "criteria_breakdown": result.criteria,
}, indent=2, default=str))
