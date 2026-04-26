"""Stage 4 — Compute v2 score + hold-time gate + write verdict.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ITER_DIR.parents[1]))  # studies/gold_swing_loop/

from scoring import DatasetMetrics, Gates, score_strategy_v2  # noqa: E402


def main() -> None:
    results = json.loads((ITER_DIR / "results.json").read_text())
    gld = results["datasets"]["gld_long"]
    xau = results["datasets"]["xauusd_real"]

    metrics = {
        "gld_long": DatasetMetrics(
            sharpe=gld["metrics"]["sharpe"],
            cagr=gld["metrics"]["cagr"],
            mdd=gld["metrics"]["mdd"],
            dsr_p_value=gld["dsr_p_value"],
        ),
        "xauusd_real": DatasetMetrics(
            sharpe=xau["metrics"]["sharpe"],
            cagr=xau["metrics"]["cagr"],
            mdd=xau["metrics"]["mdd"],
            dsr_p_value=xau["dsr_p_value"],
        ),
    }
    gates = {
        "gld_long": Gates(**gld["gates"]),
        "xauusd_real": Gates(**xau["gates"]),
    }

    result = score_strategy_v2(
        metrics=metrics,
        gates=gates,
        cumulative_n_trials=results["cumulative_n_trials"],
        declared_primary="gld_long",
        declared_corroborating=["xauusd_real"],
    )

    # Hold-time gate (medium_swing 10-30 days)
    declared_track = results["cfg"]["hold_time_track"]
    bounds = {"intraday": (0.0, 1.0), "short_swing": (2.0, 10.0), "medium_swing": (10.0, 30.0)}
    lo, hi = bounds[declared_track]
    # Use weighted-avg of the two ds means (gld_long is primary, weight heavier)
    primary_hold = gld["metrics"]["mean_hold_days"]
    corr_hold = xau["metrics"]["mean_hold_days"]
    hold_gate_pass = lo <= primary_hold <= hi

    # Pre-committed kill criteria check
    kills = {
        "kill_1_no_standalone_edge": bool(gld["metrics"]["sharpe"] < 0.20),
        "kill_2_dsr_no_progress":   bool(gld["dsr_p_value"] > 0.30),
        "kill_3_not_ic7_eligible_vs_iter003": bool(
            (results["correlation_diagnostic"]["gld_long"]["iter003_rsi2_sma200"]["rho_static"] >= 0.50)
            or (results["correlation_diagnostic"]["gld_long"]["iter003_rsi2_sma200"]["rolling_exceed_frac"] >= 0.20)
        ),
    }
    n_kills_fired = sum(kills.values())

    # Build verdict.json
    rho_static_iter003 = results["correlation_diagnostic"]["gld_long"]["iter003_rsi2_sma200"]["rho_static"]
    rho_static_iter018 = results["correlation_diagnostic"]["gld_long"]["iter018_cot_zscore"]["rho_static"]
    verdict = result.to_dict()
    verdict.update({
        "iteration": "021",
        "hypothesis_slug": "dcot-mm-zscore",
        "configs_tested": 1,
        "primary_citation": "[trading_systems_methods, p.640]",
        "broker_track": "pepperstone_cfd",
        "universe": "single_xau",
        "timeframes_used": ["1d"],
        "hold_time_track": declared_track,
        "primary_mean_hold_days": primary_hold,
        "corroborating_mean_hold_days": corr_hold,
        "hold_time_gate_pass": hold_gate_pass,
        "pre_committed_kills_fired": kills,
        "n_kills_fired": n_kills_fired,
        "ic7_diagnostic_vs_iter003": {
            "rho_static_gld_long": rho_static_iter003,
            "rolling_60d_exceed_frac_gld_long": results["correlation_diagnostic"]["gld_long"]["iter003_rsi2_sma200"]["rolling_exceed_frac"],
            "rho_static_xauusd_real": results["correlation_diagnostic"]["xauusd_real"]["iter003_rsi2_sma200"]["rho_static"],
            "rolling_60d_exceed_frac_xauusd_real": results["correlation_diagnostic"]["xauusd_real"]["iter003_rsi2_sma200"]["rolling_exceed_frac"],
            "ic7_eligible_static_below_0_50": rho_static_iter003 < 0.50,
            "ic7_eligible_rolling_below_20pct": results["correlation_diagnostic"]["gld_long"]["iter003_rsi2_sma200"]["rolling_exceed_frac"] < 0.20,
        },
        "ic7_diagnostic_vs_iter018": {
            "rho_static_gld_long": rho_static_iter018,
            "rolling_60d_exceed_frac_gld_long": results["correlation_diagnostic"]["gld_long"]["iter018_cot_zscore"]["rolling_exceed_frac"],
            "interpretation": "MM bucket and legacy commercials bucket are highly correlated (>+0.85) on gold — same family signals",
        },
        "track_a_metrics": {
            "gld_long": gld["metrics"],
            "xauusd_real": xau["metrics"],
        },
        "bench_sliced_gld_long": results["bench_sliced_gld_long"],
    })

    out_path = ITER_DIR / "verdict.json"
    out_path.write_text(json.dumps(verdict, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        "score": result.total_score,
        "tier": result.tier.value,
        "winner_conditions_met": result.winner_conditions_met,
        "hold_time_gate_pass": hold_gate_pass,
        "n_kills_fired": n_kills_fired,
        "kills": kills,
        "criteria_breakdown": {k: v.get("points") for k, v in result.criteria.items() if isinstance(v, dict) and "points" in v},
    }, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
