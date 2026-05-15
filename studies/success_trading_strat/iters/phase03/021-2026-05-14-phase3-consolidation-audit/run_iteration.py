#!/usr/bin/env python3
"""Conservative Phase 3 consolidation audit.

No strategy parameters are changed here. The script only reconciles saved Phase 3
iteration artifacts and preserves prior validation verdicts as binding
`[testing_tuning, p.327-335]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
PHASE_DIR = ROOT / "studies" / "success_trading_strat" / "iters" / "phase03"
ITERATION = "021-2026-05-14-phase3-consolidation-audit"
OUT_DIR = PHASE_DIR / ITERATION
REQUIRED_FILES = ("PRE_REG.md", "RESULTS.json", "SUMMARY.md")
REQUIRED_FIELDS = (
    "iteration",
    "status",
    "pre_registered",
    "n_trials",
    "winner",
    "gates",
    "kill_switches",
    "artifacts",
)
PROMOTIONAL_STATUSES = {"strict_winner", "candidate_watchlist", "paper_trade_candidate"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    prior_dirs = sorted(
        p for p in PHASE_DIR.iterdir() if p.is_dir() and p.name[:3].isdigit() and p.name < ITERATION
    )

    missing_files: dict[str, list[str]] = {}
    missing_fields: dict[str, list[str]] = {}
    status_counts: Counter[str] = Counter()
    promotional_without_strict: list[str] = []
    winner_without_strict: list[str] = []
    unregistered: list[str] = []
    results: dict[str, dict[str, Any]] = {}
    n_trials_sum = 0

    for iteration_dir in prior_dirs:
        missing = [name for name in REQUIRED_FILES if not (iteration_dir / name).exists()]
        if missing:
            missing_files[iteration_dir.name] = missing
            continue

        result = load_json(iteration_dir / "RESULTS.json")
        results[iteration_dir.name] = result

        fields = [field for field in REQUIRED_FIELDS if field not in result]
        if fields:
            missing_fields[iteration_dir.name] = fields

        status = str(result.get("status", "<missing>"))
        status_counts[status] += 1
        n_trials_sum += int(result.get("n_trials") or 0)

        if not result.get("pre_registered"):
            unregistered.append(iteration_dir.name)
        if result.get("winner") and status != "strict_winner":
            winner_without_strict.append(iteration_dir.name)
        if status in PROMOTIONAL_STATUSES and status != "strict_winner":
            promotional_without_strict.append(iteration_dir.name)

    strict_winners = [name for name, result in results.items() if result.get("status") == "strict_winner"]
    winners = [name for name, result in results.items() if result.get("winner") is True]
    candidate_like = [
        name for name, result in results.items() if result.get("status") in PROMOTIONAL_STATUSES - {"strict_winner"}
    ]

    gates = {
        "expected_prior_iterations_20": len(prior_dirs) == 20,
        "artifact_completeness": not missing_files,
        "schema_completeness": not missing_fields,
        "all_pre_registered": not unregistered,
        "phase3_trial_sum_reconciled": n_trials_sum == 80,
        "cumulative_trials_reconciled_216_to_296": 216 + n_trials_sum == 296,
        "zero_winner_true": not winners,
        "zero_strict_winner": not strict_winners,
        "zero_candidate_or_paper_labels": not candidate_like,
        "no_promotional_label_without_strict": not promotional_without_strict,
        "prior_validation_failures_binding": True,
        "mcpt_recomputed": False,
        "pbo_recomputed": False,
        "dsr_recomputed": False,
    }

    kill_switches: list[str] = []
    if not gates["expected_prior_iterations_20"]:
        kill_switches.append(f"expected 20 prior Phase 3 iterations, found {len(prior_dirs)}")
    if missing_files:
        kill_switches.append("missing required artifacts in prior Phase 3 iterations")
    if missing_fields:
        kill_switches.append("missing required RESULTS.json fields in prior Phase 3 iterations")
    if unregistered:
        kill_switches.append("one or more prior Phase 3 iterations were not pre-registered")
    if n_trials_sum != 80:
        kill_switches.append(f"Phase 3 local n_trials sum {n_trials_sum} did not reconcile to expected 80")
    if winners or strict_winners:
        kill_switches.append("strict winner review required before any closure claim")
    if candidate_like:
        kill_switches.append("candidate/paper labels require explicit human decision")
    if not kill_switches:
        kill_switches.append("no strict winner found in 20 prior Phase 3 iterations")

    audit = {
        "iteration": ITERATION,
        "audit_type": "phase3_consolidation_after_20_iterations",
        "prior_iterations": [p.name for p in prior_dirs],
        "prior_iteration_count": len(prior_dirs),
        "status_counts": dict(sorted(status_counts.items())),
        "n_trials_sum": n_trials_sum,
        "cumulative_before_phase3": 216,
        "cumulative_after_prior_phase3": 216 + n_trials_sum,
        "missing_files": missing_files,
        "missing_fields": missing_fields,
        "unregistered": unregistered,
        "winners": winners,
        "strict_winners": strict_winners,
        "candidate_or_paper_labels": candidate_like,
        "promotional_without_strict": promotional_without_strict,
        "gates": gates,
        "kill_switches": kill_switches,
    }

    status = "fail"
    results_out = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": audit,
        "benchmark": {
            "primary": "prior_iteration_specific_buy_hold_benchmarks",
            "opportunity": "prior_iteration_specific_SPY_opportunity_context",
            "details": "No new market backtest; prior aligned B&H benchmarks remain binding.",
        },
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": [
            str(OUT_DIR / "PRE_REG.md"),
            str(OUT_DIR / "run_iteration.py"),
            str(OUT_DIR / "audit.json"),
            str(OUT_DIR / "RESULTS.json"),
        ],
        "notes": "Consolidation audit only; prior MCPT/PBO/DSR/economic failures remain binding; no deploy implication.",
    }

    (OUT_DIR / "audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / "RESULTS.json").write_text(
        json.dumps(results_out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
