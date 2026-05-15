#!/usr/bin/env python3
"""Phase 3 iteration 030 final closure audit.

This audit consumes no strategy trials. It verifies saved Phase 3 artifacts and
keeps prior MCPT/PBO/DSR failures binding `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ITERATION = "030-2026-05-14-phase3-closure-audit"
ROOT = Path(__file__).resolve().parents[5]
PHASE_DIR = ROOT / "studies" / "success_trading_strat" / "iters" / "phase03"
OUT_DIR = Path(__file__).resolve().parent

HARD_GATE_KEYS = {
    "is_mcpt",
    "wf_mcpt",
    "pbo",
    "dsr",
    "wf_windows",
    "oos",
    "fwd_63d",
    "bootstrap",
    "cross_lib",
    "prior_is_mcpt",
    "prior_wf_mcpt",
    "prior_pbo",
    "prior_dsr",
    "prior_wf_windows",
    "prior_oos",
    "prior_fwd_63d",
    "prior_bootstrap",
    "prior_cross_lib",
    "rolling_3y_pass_rate_ge_90pct",
    "rolling_5y_pass_rate_ge_90pct",
    "mdd_guardrail_1_5x_primary",
}
PROMOTIONAL = {"strict_winner", "candidate_watchlist", "paper_trade_candidate"}
REQUIRED_ARTIFACTS = ("PRE_REG.md", "RESULTS.json", "SUMMARY.md")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def gate_failures(result: dict[str, Any]) -> list[str]:
    gates = result.get("gates") or {}
    failures: list[str] = []
    for key in HARD_GATE_KEYS:
        value = gates.get(key)
        if value is False:
            failures.append(key)
    return sorted(failures)


def main() -> None:
    prior_dirs = [
        p
        for p in sorted(PHASE_DIR.iterdir())
        if p.is_dir() and p.name[:3].isdigit() and 1 <= int(p.name[:3]) <= 29
    ]
    expected = {f"{i:03d}" for i in range(1, 30)}
    seen = {p.name[:3] for p in prior_dirs}
    missing_dirs = sorted(expected - seen)

    rows: list[dict[str, Any]] = []
    artifact_errors: list[dict[str, str]] = []
    parse_errors: list[dict[str, str]] = []
    status_counts: Counter[str] = Counter()
    n_trials_sum = 0
    winner_true_count = 0
    strict_winner_count = 0
    candidate_watchlist_count = 0
    paper_trade_candidate_count = 0
    economic_beater_count = 0
    economic_beater_blocked_count = 0
    promotional_with_failed_or_missing_gates = 0

    for directory in prior_dirs:
        missing_artifacts = [name for name in REQUIRED_ARTIFACTS if not (directory / name).exists()]
        if missing_artifacts:
            artifact_errors.append({"iteration": directory.name, "missing": ",".join(missing_artifacts)})

        result_path = directory / "RESULTS.json"
        if not result_path.exists():
            continue
        try:
            result = load_json(result_path)
        except Exception as exc:  # pragma: no cover - diagnostic artifact path
            parse_errors.append({"iteration": directory.name, "error": repr(exc)})
            continue

        status = str(result.get("status", "missing_status"))
        failures = gate_failures(result)
        n_trials = int(result.get("n_trials") or 0)
        winner = bool(result.get("winner", False))
        strict_gate_complete = not failures and status == "strict_winner" and winner
        blocked_for_promotion = status != "strict_winner" or bool(failures) or not winner

        status_counts[status] += 1
        n_trials_sum += n_trials
        winner_true_count += int(winner)
        strict_winner_count += int(status == "strict_winner")
        candidate_watchlist_count += int(status == "candidate_watchlist")
        paper_trade_candidate_count += int(status == "paper_trade_candidate")
        economic_beater_count += int(status == "economic_beater_not_validated")

        if status == "economic_beater_not_validated" and blocked_for_promotion:
            economic_beater_blocked_count += 1
        if status in PROMOTIONAL and not strict_gate_complete:
            promotional_with_failed_or_missing_gates += 1

        rows.append(
            {
                "iteration": directory.name,
                "status": status,
                "winner": winner,
                "n_trials": n_trials,
                "failed_hard_gates": failures,
                "blocked_for_promotion": blocked_for_promotion,
            }
        )

    artifact_complete = not missing_dirs and not artifact_errors and not parse_errors and len(rows) == 29
    zero_promotional = strict_winner_count == 0 and candidate_watchlist_count == 0 and paper_trade_candidate_count == 0
    zero_winners = winner_true_count == 0 and strict_winner_count == 0
    all_economic_beaters_blocked = economic_beater_blocked_count == economic_beater_count

    audit = {
        "iteration": ITERATION,
        "parsed_iterations": len(rows),
        "missing_dirs": missing_dirs,
        "artifact_errors": artifact_errors,
        "parse_errors": parse_errors,
        "status_counts": dict(sorted(status_counts.items())),
        "prior_phase3_n_trials_sum": n_trials_sum,
        "winner_true_count": winner_true_count,
        "strict_winner_count": strict_winner_count,
        "candidate_watchlist_count": candidate_watchlist_count,
        "paper_trade_candidate_count": paper_trade_candidate_count,
        "economic_beater_not_validated_count": economic_beater_count,
        "economic_beater_blocked_count": economic_beater_blocked_count,
        "promotional_with_failed_or_missing_gates": promotional_with_failed_or_missing_gates,
        "rows": rows,
    }

    results = {
        "iteration": ITERATION,
        "status": "fail",
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {
            "audit_type": "phase3_final_closure_audit",
            "parsed_iterations": len(rows),
            "status_counts": audit["status_counts"],
            "prior_phase3_n_trials_sum": n_trials_sum,
            "memory_cumulative_n_trials_before": 312,
            "memory_cumulative_n_trials_after": 312,
            "winner_true_count": winner_true_count,
            "strict_winner_count": strict_winner_count,
            "candidate_watchlist_count": candidate_watchlist_count,
            "paper_trade_candidate_count": paper_trade_candidate_count,
            "economic_beater_not_validated_count": economic_beater_count,
            "economic_beater_blocked_count": economic_beater_blocked_count,
        },
        "benchmark": {
            "primary": "candidate_specific_phase3_primary_buy_hold_from_prior_results",
            "same_asset_or_opportunity": "source_iteration_specific_where_saved",
            "spy_opportunity": "source_iteration_specific_where_saved",
        },
        "gates": {
            "artifact_completeness": artifact_complete,
            "zero_winner_true": zero_winners,
            "zero_promotional_statuses": zero_promotional,
            "economic_beaters_all_blocked": all_economic_beaters_blocked,
            "trial_reconciliation_to_memory": n_trials_sum <= 312,
            "mcpt_recomputed": False,
            "pbo_recomputed": False,
            "dsr_recomputed": False,
        },
        "kill_switches": [
            "final audit tests no executable strategy",
            "prior economic beaters remain blocked by failed or missing strict gates",
            "no automated promotion at Phase 3 cap",
        ],
        "artifacts": [
            str(OUT_DIR / "PRE_REG.md"),
            str(OUT_DIR / "run_iteration.py"),
            str(OUT_DIR / "audit.json"),
            str(OUT_DIR / "RESULTS.json"),
        ],
        "notes": "Final Phase 3 closure audit at 30/30 iterations. No new trials, no deploy implication.",
    }

    (OUT_DIR / "audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
