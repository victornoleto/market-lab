#!/usr/bin/env python3
"""Closure audit for success_trading_strat iteration 030.

This runner intentionally tests no new strategy. It preserves the anti-overfit
discipline by stopping at the planned cap instead of adding local trials after
failed families `[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
from pathlib import Path


ITERATION = "030-2026-05-14-study-closure-audit"
EXPECTED_PRIOR_TRIALS = 100
EXPECTED_TARGET_ITERATIONS = 30


def main() -> None:
    here = Path(__file__).resolve().parent
    iters_dir = here.parent
    iteration_dirs = sorted(p for p in iters_dir.iterdir() if p.is_dir() and p.name[:3].isdigit())
    prior_dirs = [p for p in iteration_dirs if p.name != ITERATION]

    status_counts: dict[str, int] = {}
    missing_artifacts: dict[str, list[str]] = {}
    winners: list[str] = []
    summed_trials = 0
    parsed_results = 0
    preregistered_all = True

    for path in prior_dirs:
        missing = [name for name in ("PRE_REG.md", "RESULTS.json", "SUMMARY.md") if not (path / name).exists()]
        if missing:
            missing_artifacts[path.name] = missing
            continue

        result = json.loads((path / "RESULTS.json").read_text())
        parsed_results += 1
        status = str(result.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
        summed_trials += int(result.get("n_trials", 0))
        preregistered_all = preregistered_all and bool(result.get("pre_registered"))
        if result.get("winner") is True:
            winners.append(path.name)

    audit_pass = (
        len(iteration_dirs) == EXPECTED_TARGET_ITERATIONS
        and parsed_results == EXPECTED_TARGET_ITERATIONS - 1
        and not missing_artifacts
        and not winners
        and preregistered_all
        and summed_trials == EXPECTED_PRIOR_TRIALS
    )

    audit = {
        "iteration": ITERATION,
        "audit_pass": audit_pass,
        "iteration_dirs_count": len(iteration_dirs),
        "prior_results_parsed": parsed_results,
        "status_counts_prior": status_counts,
        "missing_artifacts": missing_artifacts,
        "winners_prior": winners,
        "prior_preregistered_all": preregistered_all,
        "summed_prior_n_trials": summed_trials,
        "expected_prior_n_trials": EXPECTED_PRIOR_TRIALS,
        "target_total_iterations_after": EXPECTED_TARGET_ITERATIONS,
    }

    (here / "AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n")

    results = {
        "iteration": ITERATION,
        "status": "infrastructure_only" if audit_pass else "fail",
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {
            "iteration_dirs_count": len(iteration_dirs),
            "prior_results_parsed": parsed_results,
            "summed_prior_n_trials": summed_trials,
            "winner_count_prior": len(winners),
        },
        "benchmark": {},
        "gates": {
            "artifact_completeness": not missing_artifacts,
            "trial_accounting_matches_memory": summed_trials == EXPECTED_PRIOR_TRIALS,
            "no_prior_winners": not winners,
            "all_prior_pre_registered": preregistered_all,
            "target_iterations_reached": len(iteration_dirs) == EXPECTED_TARGET_ITERATIONS,
            "pbo": None,
            "dsr": None,
            "is_mcpt": None,
            "wf_mcpt": None,
        },
        "kill_switches": [] if audit_pass else ["closure_audit_inconsistent"],
        "artifacts": ["PRE_REG.md", "run.py", "AUDIT.json", "RESULTS.json", "SUMMARY.md"],
        "notes": "Closure audit only; no strategy claim, no deploy implication, capital remains 100% Plano C.",
    }
    (here / "RESULTS.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
