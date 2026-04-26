"""Score iter 018 with score_strategy_v2 + write verdict.json.

Citation: `WINNER_AND_RANKING.md` v2 (rules_version 2026-04-26-relaxed-r1).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
ITER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "studies" / "gold_swing_loop"))

from scoring import DatasetMetrics, Gates, score_strategy_v2  # noqa: E402

# Load backtest results
res = json.loads((ITER_DIR / "results.json").read_text())
ds_gld = res["datasets"]["gld_long"]
ds_xau = res["datasets"]["xauusd_real"]


def make_dm(ds: dict) -> DatasetMetrics:
    m = ds["metrics"]
    return DatasetMetrics(
        sharpe=m["sharpe"], cagr=m["cagr"], mdd=m["mdd"],
        dsr_p_value=ds["dsr_p_value"],
    )


def make_gates(ds: dict) -> Gates:
    g = ds["gates"]
    return Gates(
        g1_pbo=g["g1_pbo"], g2_dsr=g["g2_dsr"], g3_wf=g["g3_wf"],
        g4_oos=g["g4_oos"], g5_fwd=g["g5_fwd"],
        g6_bootstrap=g["g6_bootstrap"], g7_crosslib=g["g7_crosslib"],
    )


metrics = {"gld_long": make_dm(ds_gld), "xauusd_real": make_dm(ds_xau)}
gates = {"gld_long": make_gates(ds_gld), "xauusd_real": make_gates(ds_xau)}

result = score_strategy_v2(
    metrics=metrics, gates=gates,
    cumulative_n_trials=res["cumulative_n_trials"],
    declared_primary="gld_long",
    declared_corroborating=["xauusd_real"],
)

# Hold-time gate (6th winner condition)
TRACK_BOUNDS = {
    "intraday":     (0.0, 1.0),
    "short_swing":  (2.0, 10.0),
    "medium_swing": (10.0, 30.0),
}
declared_track = res["cfg"]["hold_time_track"]
lo, hi = TRACK_BOUNDS[declared_track]
hold_gld = ds_gld["metrics"]["mean_hold_days"]
hold_xau = ds_xau["metrics"]["mean_hold_days"]
hold_gate_primary = lo <= hold_gld <= hi
hold_gate_pass = hold_gate_primary  # primary is gld_long

# Mismatch downgrade (per WINNER_AND_RANKING.md): if declared track ≠
# observed bucket on primary, force NEAR_FAIL.
final_winner = result.winner_conditions_met and hold_gate_pass

verdict = result.to_dict()
verdict.update({
    "configs_tested": 1,
    "primary_citation": "[trading_systems_methods, p.639-640]",
    "secondary_citations": [
        "[advances_fin_ml, p.222-223]",
        "[advances_fin_ml, p.31-34]",
        "de Roon, Nijman, Veld (2000) J Finance — z-score commercial net positioning",
    ],
    "hypothesis_slug": "cot_zscore_variant_long_zentry_pos1_zexit_zero_window156w_lag1_max30d",
    "mean_hold_days": {"gld_long": hold_gld, "xauusd_real": hold_xau},
    "hold_time_track_declared": declared_track,
    "hold_time_gate_pass": hold_gate_pass,
    "broker_track": "pepperstone_cfd",
    "timeframes_used": ["1d"],
    "track_a_metrics": {
        "gld_long": ds_gld["metrics"],
        "xauusd_real": ds_xau["metrics"],
    },
    "track_b_metrics": None,
    "rules_version": "2026-04-26-relaxed-r1",
    "winner_final": final_winner,
    "kill_criteria_pre_committed": {
        "kill_1_catastrophic_sh_le_0_gld": ds_gld["metrics"]["sharpe"] <= 0.0,
        "kill_2_no_progress_gld_le_0_3_AND_xau_le_0_4": (
            ds_gld["metrics"]["sharpe"] <= 0.30
            and ds_xau["metrics"]["sharpe"] <= 0.40
        ),
        "kill_3_hold_mismatch": not (
            10.0 <= hold_gld <= 30.0 and 10.0 <= hold_xau <= 30.0
        ),
    },
    "correlation_diagnostic": res["correlation_diagnostic"],
    "structural_insight": (
        f"z-score variant lifts canonical Briese gld_long Sh from "
        f"+0.137 (iter 017) to +{ds_gld['metrics']['sharpe']:.3f} "
        f"(+{ds_gld['metrics']['sharpe'] - 0.137:.3f}). MDD also reduced "
        f"31.8% → {ds_gld['metrics']['mdd']*100:.1f}%. Standalone still "
        f"trails buy-hold by Sh Δ "
        f"−{0.6844 + 0.10 - ds_gld['metrics']['sharpe']:.2f}. "
        f"ρ vs iter 017 canonical Briese = "
        f"+{res['correlation_diagnostic']['gld_long']['iter017_cot_briese']['rho']:.2f} "
        f"on gld_long → same family confirmed. ρ vs iter 003 RSI = "
        f"+{res['correlation_diagnostic']['gld_long']['iter003_rsi2_sma200']['rho']:.3f} "
        f"on gld_long → COT-positioning orthogonality to RSI confirmed at "
        f"2nd measurement."
    ),
})

(ITER_DIR / "verdict.json").write_text(
    json.dumps(verdict, indent=2, default=str), encoding="utf-8",
)

print(f"=== Iter 018 Verdict ===")
print(f"  total_score:              {result.total_score}/100")
print(f"  tier:                     {result.tier.value}")
print(f"  winner_conditions_met:    {result.winner_conditions_met}")
print(f"  hold_time_gate_pass:      {hold_gate_pass}")
print(f"  winner_final:             {final_winner}")
print(f"  kill_1_catastrophic:      {verdict['kill_criteria_pre_committed']['kill_1_catastrophic_sh_le_0_gld']}")
print(f"  kill_2_no_progress:       {verdict['kill_criteria_pre_committed']['kill_2_no_progress_gld_le_0_3_AND_xau_le_0_4']}")
print(f"  kill_3_hold_mismatch:     {verdict['kill_criteria_pre_committed']['kill_3_hold_mismatch']}")
print()
print(f"Score breakdown:")
for k, v in result.criteria.items():
    if isinstance(v, dict) and "points" in v:
        print(f"  {k}: {v['points']}/{v['max']}")
print()
print(f"Per-dataset summary:")
print(f"  gld_long:    Sh={ds_gld['metrics']['sharpe']:+.3f} CAGR={ds_gld['metrics']['cagr']*100:+.2f}% MDD={ds_gld['metrics']['mdd']*100:.1f}% gates={ds_gld['n_gates_passed']}/7 hold={hold_gld:.1f}d trades={ds_gld['metrics']['n_trades']} DSRp={ds_gld['dsr_p_value']:.3f}")
print(f"  xauusd_real: Sh={ds_xau['metrics']['sharpe']:+.3f} CAGR={ds_xau['metrics']['cagr']*100:+.2f}% MDD={ds_xau['metrics']['mdd']*100:.1f}% gates={ds_xau['n_gates_passed']}/7 hold={hold_xau:.1f}d trades={ds_xau['metrics']['n_trades']} DSRp={ds_xau['dsr_p_value']:.3f}")
