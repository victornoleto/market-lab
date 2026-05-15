from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ITERATION = "026-2026-05-14-phase3-gate-consolidation"
ROOT = Path(__file__).resolve().parents[5]
PHASE_DIR = ROOT / "studies" / "success_trading_strat" / "iters" / "phase03"
OUT_DIR = Path(__file__).resolve().parent

STRICT_GATES = (
    "is_mcpt",
    "wf_mcpt",
    "pbo",
    "dsr",
    "wf_windows",
    "oos",
    "fwd_63d",
    "bootstrap",
    "cross_lib",
)
PROMOTIONAL_STATUSES = {
    "strict_winner",
    "candidate_watchlist",
    "paper_trade_candidate",
}
ECONOMIC_OR_PROMOTIONAL_STATUSES = PROMOTIONAL_STATUSES | {
    "economic_beater_not_validated",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def gate_failures(result: dict[str, Any]) -> list[str]:
    gates = result.get("gates") or {}
    failures: list[str] = []
    for gate in STRICT_GATES:
        value = gates.get(gate)
        if value is not True:
            failures.append(gate if gate in gates else f"{gate}:missing")
    return failures


def main() -> None:
    parsed = []
    missing_artifacts = []
    status_counts: Counter[str] = Counter()
    economic_blocked = []
    promotional_violations = []
    winner_true = []
    n_trials_sum = 0

    for idx in range(1, 26):
        prefix = f"{idx:03d}-"
        matches = sorted(p for p in PHASE_DIR.iterdir() if p.is_dir() and p.name.startswith(prefix))
        if len(matches) != 1:
            missing_artifacts.append({"iteration_prefix": prefix, "matches": [p.name for p in matches]})
            continue
        folder = matches[0]
        results_path = folder / "RESULTS.json"
        summary_path = folder / "SUMMARY.md"
        if not results_path.exists() or not summary_path.exists():
            missing_artifacts.append(
                {
                    "iteration": folder.name,
                    "has_results": results_path.exists(),
                    "has_summary": summary_path.exists(),
                }
            )
            continue

        result = load_json(results_path)
        status = str(result.get("status", "<missing>"))
        n_trials = int(result.get("n_trials", 0) or 0)
        status_counts[status] += 1
        n_trials_sum += n_trials

        item = {
            "iteration": folder.name,
            "status": status,
            "winner": bool(result.get("winner", False)),
            "n_trials": n_trials,
            "best_config": result.get("best_config"),
            "gate_failures": gate_failures(result) if status in ECONOMIC_OR_PROMOTIONAL_STATUSES else [],
        }
        parsed.append(item)

        if item["winner"]:
            winner_true.append(item)
        if status in ECONOMIC_OR_PROMOTIONAL_STATUSES and item["gate_failures"]:
            economic_blocked.append(item)
        if (status in PROMOTIONAL_STATUSES or item["winner"]) and item["gate_failures"]:
            promotional_violations.append(item)

    audit = {
        "iteration": ITERATION,
        "parsed_iterations": len(parsed),
        "expected_prior_iterations": 25,
        "missing_artifacts": missing_artifacts,
        "status_counts": dict(sorted(status_counts.items())),
        "n_trials_sum_from_prior_results": n_trials_sum,
        "memory_phase3_cumulative_before": 308,
        "memory_phase3_total_iterations_before": 25,
        "winner_true_count": len(winner_true),
        "promotional_violation_count": len(promotional_violations),
        "economic_or_promotional_blocked_count": len(economic_blocked),
        "economic_or_promotional_blocked": economic_blocked,
        "promotional_violations": promotional_violations,
        "winner_true": winner_true,
        "pre_existing_worktree_ambiguity": (
            "Public docs and phase03 artifacts beyond the supplied MEMORY state were already "
            "modified before this iteration; this audit used MEMORY total_iterations=25 and latest 025."
        ),
    }

    artifact_complete = len(missing_artifacts) == 0 and len(parsed) == 25
    no_promotional_violations = len(promotional_violations) == 0 and len(winner_true) == 0
    no_economic_blocked = len(economic_blocked) == 0
    status = "fail" if (not artifact_complete or not no_promotional_violations or not no_economic_blocked) else "infrastructure_only"

    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {
            "audit_type": "phase3_prior_result_gate_consolidation",
            "parsed_iterations": len(parsed),
            "status_counts": audit["status_counts"],
            "prior_n_trials_sum": n_trials_sum,
            "economic_or_promotional_blocked_count": len(economic_blocked),
        },
        "benchmark": {
            "primary": "candidate_specific_phase3_primary_buy_hold_from_prior_results",
            "opportunity": "SPY_buy_hold_context_where_saved",
        },
        "gates": {
            "artifact_completeness": artifact_complete,
            "trial_reconciliation": n_trials_sum == 92,
            "zero_winner_true": len(winner_true) == 0,
            "zero_promotional_statuses_with_failed_gates": len(promotional_violations) == 0,
            "zero_economic_beaters_with_failed_strict_gates": len(economic_blocked) == 0,
            "prior_validation_failures_binding": True,
            "mcpt_recomputed": False,
            "pbo_recomputed": False,
            "dsr_recomputed": False,
        },
        "kill_switches": [
            "prior economic beaters still have failed or missing strict gates"
        ]
        if economic_blocked
        else [],
        "artifacts": [
            str(OUT_DIR / "PRE_REG.md"),
            str(OUT_DIR / "run_iteration.py"),
            str(OUT_DIR / "audit.json"),
            str(OUT_DIR / "RESULTS.json"),
        ],
        "notes": (
            "Conservative consolidation audit only; no new strategy trials, no recomputation of MCPT/PBO/DSR, "
            "and no deploy implication. Prior failures remain binding."
        ),
    }

    (OUT_DIR / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"status": status, "parsed": len(parsed), "blocked": len(economic_blocked)}, indent=2))


if __name__ == "__main__":
    main()
