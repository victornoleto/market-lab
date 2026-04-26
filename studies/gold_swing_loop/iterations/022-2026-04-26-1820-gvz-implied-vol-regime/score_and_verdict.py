"""Score iter 022 + write verdict.json (uses score_strategy_v2 from scoring.py)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ITER_DIR = Path(__file__).resolve().parent
LOOP_DIR = ITER_DIR.parents[1]
sys.path.insert(0, str(LOOP_DIR))

from scoring import DatasetMetrics, Gates, score_strategy_v2  # noqa: E402


def main() -> None:
    results = json.loads((ITER_DIR / "results.json").read_text())
    cfg = results["cfg"]
    cum_n_trials = results["cumulative_n_trials"]
    ds = results["datasets"]

    metrics = {
        "gld_long": DatasetMetrics(
            sharpe=ds["gld_long"]["metrics"]["sharpe"],
            cagr=ds["gld_long"]["metrics"]["cagr"],
            mdd=ds["gld_long"]["metrics"]["mdd"],
            dsr_p_value=ds["gld_long"]["dsr_p_value"],
        ),
        "xauusd_real": DatasetMetrics(
            sharpe=ds["xauusd_real"]["metrics"]["sharpe"],
            cagr=ds["xauusd_real"]["metrics"]["cagr"],
            mdd=ds["xauusd_real"]["metrics"]["mdd"],
            dsr_p_value=ds["xauusd_real"]["dsr_p_value"],
        ),
    }

    def _gates(d: dict) -> Gates:
        g = d["gates"]
        return Gates(
            g1_pbo=g["g1_pbo"], g2_dsr=g["g2_dsr"], g3_wf=g["g3_wf"],
            g4_oos=g["g4_oos"], g5_fwd=g["g5_fwd"],
            g6_bootstrap=g["g6_bootstrap"], g7_crosslib=g["g7_crosslib"],
        )

    gates = {
        "gld_long": _gates(ds["gld_long"]),
        "xauusd_real": _gates(ds["xauusd_real"]),
    }

    res = score_strategy_v2(
        metrics=metrics,
        gates=gates,
        cumulative_n_trials=cum_n_trials,
        declared_primary=cfg["declared_primary"],
        declared_corroborating=cfg["declared_corroborating"],
    )

    # 6th condition: hold-time bucket match (medium_swing: 10 ≤ mean ≤ 30)
    primary_hold = ds["gld_long"]["metrics"]["mean_hold_days"]
    track = cfg["hold_time_track"]
    bounds = {"intraday": (0.0, 1.0), "short_swing": (2.0, 10.0), "medium_swing": (10.0, 30.0)}
    lo, hi = bounds[track]
    hold_pass = lo <= primary_hold <= hi

    # Pre-committed kill criteria from hypothesis.md
    primary = ds["gld_long"]
    rho_iter011 = (
        results["correlation_diagnostic"]["gld_long"]["iter011_volregime"]
        .get("rolling_exceed_frac")
    )
    kills = {
        "kill1_primary_sharpe_below_0p20": primary["metrics"]["sharpe"] < 0.20,
        "kill2_primary_dsr_above_0p30":   primary["dsr_p_value"] > 0.30,
        "kill3_ic6_rho_vs_iter011_above_30pct": (rho_iter011 is not None and rho_iter011 > 0.30),
        "kill4_primary_g6_boot_failed": primary["bootstrap_ci_low"] <= 0,
    }
    kills_fired = [k for k, v in kills.items() if v]

    verdict = res.to_dict()
    verdict["configs_tested"] = 1
    verdict["primary_citation"] = "[volatility_trading, p.32-37]"
    verdict["additional_citations"] = [
        "[trading_systems_methods, p.13-14]",
        "[advances_fin_ml, p.222-223]",
        "[advances_fin_ml, p.31-34]",
        "CBOE GVZ methodology white paper",
        "Bollerslev, Tauchen, Zhou (2009) RFS — VRP-as-predictor",
    ]
    verdict["hypothesis_slug"] = "gvz_zscore_long_zentry_neg1_zexit_zero_window252d_lag1d_max30d"
    verdict["mean_hold_days"] = primary_hold
    verdict["hold_time_gate_pass"] = bool(hold_pass)
    verdict["broker_track"] = "pepperstone_cfd"
    verdict["timeframes_used"] = ["1d"]
    verdict["track_a_metrics"] = {
        ds_name: {
            "sharpe": ds[ds_name]["metrics"]["sharpe"],
            "cagr": ds[ds_name]["metrics"]["cagr"],
            "mdd": ds[ds_name]["metrics"]["mdd"],
            "n_trades": ds[ds_name]["metrics"]["n_trades"],
            "mean_hold_days": ds[ds_name]["metrics"]["mean_hold_days"],
            "dsr_p_value": ds[ds_name]["dsr_p_value"],
            "bootstrap_ci_low": ds[ds_name]["bootstrap_ci_low"],
            "n_gates_passed": ds[ds_name]["n_gates_passed"],
            "wf_passed": ds[ds_name]["walk_forward"]["passed"],
        }
        for ds_name in ("gld_long", "xauusd_real")
    }
    verdict["track_b_metrics"] = None  # not run; long-only XAU CFD only path declared
    verdict["pre_committed_kills"] = kills
    verdict["kills_fired"] = kills_fired
    verdict["bench_sliced_gld_long"] = results["bench_sliced_gld_long"]
    verdict["correlation_diagnostic_summary"] = {
        ds_name: {
            ref: {
                "rho_static": v.get("rho_static"),
                "rolling_exceed_frac": v.get("rolling_exceed_frac"),
                "rolling_n_windows": v.get("rolling_n_windows"),
            }
            for ref, v in results["correlation_diagnostic"][ds_name].items()
        }
        for ds_name in ("gld_long", "xauusd_real")
    }

    out_path = ITER_DIR / "verdict.json"
    out_path.write_text(json.dumps(verdict, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        "tier": verdict["tier"],
        "total_score": verdict["total_score"],
        "winner_conditions_met": verdict["winner_conditions_met"],
        "hold_time_gate_pass": verdict["hold_time_gate_pass"],
        "kills_fired": kills_fired,
    }, indent=2))


if __name__ == "__main__":
    main()
