"""Closure audit for success_trading_strat Phase 2.

No new strategy is tested here. The audit checks artifact completeness and trial
accounting at the planned Phase 2 cap, avoiding extra data-mining after repeated
family failures [testing_tuning, p.327-335], [advances_fin_ml, p.222-223].
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ITERATION = "030-2026-05-14-phase2-closure-audit"
EXPECTED_PRIOR_TRIALS = 216
EXPECTED_PHASE2_PRIOR_TRIALS = 116
ROOT = Path(__file__).resolve().parents[5]
PHASE_DIR = ROOT / "studies" / "success_trading_strat" / "iters" / "phase02"
OUT_DIR = PHASE_DIR / ITERATION


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    prior_dirs = sorted(
        path for path in PHASE_DIR.iterdir() if path.is_dir() and path.name[:3].isdigit() and path.name < ITERATION
    )

    rows: list[dict[str, Any]] = []
    missing_artifacts: list[str] = []
    parse_errors: list[str] = []
    total_trials = 0
    winners: list[str] = []
    promotional: list[str] = []
    statuses: dict[str, int] = {}

    for path in prior_dirs:
        required = ["PRE_REG.md", "RESULTS.json", "SUMMARY.md"]
        missing = [name for name in required if not (path / name).exists()]
        if missing:
            missing_artifacts.append(f"{path.name}: {', '.join(missing)}")

        result_path = path / "RESULTS.json"
        if not result_path.exists():
            continue

        try:
            result = load_json(result_path)
        except Exception as exc:  # pragma: no cover - audit script records details.
            parse_errors.append(f"{path.name}: {exc}")
            continue

        n_trials = int(result.get("n_trials", 0) or result.get("n_strategy_trials", 0) or 0)
        status = str(result.get("status") or result.get("verdict") or "unknown")
        winner = bool(result.get("winner", False))
        best_config = result.get("best_config")
        if isinstance(best_config, dict):
            best_config_name = best_config.get("name")
        else:
            best_config_name = best_config

        total_trials += n_trials
        statuses[status] = statuses.get(status, 0) + 1
        if winner or status == "strict_winner":
            winners.append(path.name)
        if status in {"candidate_watchlist", "paper_trade_candidate"}:
            promotional.append(path.name)

        rows.append(
            {
                "iteration": path.name,
                "status": status,
                "winner": winner,
                "n_trials": n_trials,
                "best_config": best_config_name,
            }
        )

    trial_accounting_ok = total_trials == EXPECTED_PHASE2_PRIOR_TRIALS
    artifact_complete = not missing_artifacts and not parse_errors
    no_promotion = not winners and not promotional

    status = "fail"
    notes = (
        "Phase 2 closure audit: no strict winners or watchlist promotions found. "
        "Closed as fail because the phase objective was strategy discovery and no strategy cleared the gates."
    )
    kill_switches = ["zero strict winners at planned phase cap"]
    if not artifact_complete:
        kill_switches.append("artifact or parse gap found")
    if not trial_accounting_ok:
        kill_switches.append("trial accounting mismatch")
    if not no_promotion:
        kill_switches.append("unexpected promotional status found")

    audit = {
        "iteration": ITERATION,
        "prior_iteration_count": len(prior_dirs),
        "expected_prior_iteration_count": 29,
        "total_prior_trials": total_trials,
        "expected_phase2_prior_trials": EXPECTED_PHASE2_PRIOR_TRIALS,
        "cumulative_trials_before": EXPECTED_PRIOR_TRIALS,
        "cumulative_trials_after": EXPECTED_PRIOR_TRIALS,
        "trial_accounting_ok": trial_accounting_ok,
        "artifact_complete": artifact_complete,
        "missing_artifacts": missing_artifacts,
        "parse_errors": parse_errors,
        "statuses": statuses,
        "winners": winners,
        "promotional_statuses": promotional,
        "rows": rows,
    }

    (OUT_DIR / "audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "phase2_audit_table.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")

    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {
            "prior_iteration_count": len(prior_dirs),
            "phase2_prior_trials": total_trials,
            "cumulative_trials_before": EXPECTED_PRIOR_TRIALS,
            "cumulative_trials_after": EXPECTED_PRIOR_TRIALS,
            "strict_winners": len(winners),
            "promotional_statuses": len(promotional),
        },
        "benchmark": {
            "primary": "not_applicable_closure_audit",
            "phase2_rule": "prior strategy iterations required same-asset buy-and-hold CAGR outperformance",
        },
        "gates": {
            "artifact_complete": artifact_complete,
            "trial_accounting_ok": trial_accounting_ok,
            "no_strict_winners": not winners,
            "no_promotional_statuses": not promotional,
            "strategy_gates_recomputed": False,
        },
        "kill_switches": kill_switches,
        "artifacts": [
            str(OUT_DIR / "PRE_REG.md"),
            str(OUT_DIR / "run_iteration.py"),
            str(OUT_DIR / "audit.json"),
            str(OUT_DIR / "phase2_audit_table.json"),
            str(OUT_DIR / "RESULTS.json"),
        ],
        "notes": notes,
    }
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
