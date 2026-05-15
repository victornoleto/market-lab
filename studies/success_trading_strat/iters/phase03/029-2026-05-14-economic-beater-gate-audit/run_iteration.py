#!/usr/bin/env python3
"""Phase 3 iteration 029 consolidation audit.

This is an audit-only iteration: it parses prior Phase 3 artifacts and does not
create new strategy trials. Prior MCPT, PBO and DSR failures remain binding
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ITERATION = "029-2026-05-14-economic-beater-gate-audit"
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
    "prior_dsr",
    "rolling_3y_pass_rate_ge_90pct",
    "rolling_5y_pass_rate_ge_90pct",
}
PROMOTIONAL = {"strict_winner", "candidate_watchlist", "paper_trade_candidate"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def strict_gate_failures(result: dict[str, Any]) -> dict[str, bool]:
    gates = result.get("gates") or {}
    return {
        key: bool(value)
        for key, value in gates.items()
        if key in HARD_GATE_KEYS and isinstance(value, bool) and value is False
    }


def main() -> None:
    iteration_dirs = [p for p in sorted(PHASE_DIR.iterdir()) if p.is_dir() and p.name[:3].isdigit()]
    prior_dirs = [p for p in iteration_dirs if 1 <= int(p.name[:3]) <= 28]
    expected = {f"{i:03d}" for i in range(1, 29)}
    seen = {p.name[:3] for p in prior_dirs}
    missing_dirs = sorted(expected - seen)

    rows: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    status_counts: Counter[str] = Counter()
    n_trials_sum = 0
    economic_beater_blocked = 0
    promotional_with_failed_gates = 0
    winner_true_count = 0
    strict_winner_count = 0
    candidate_watchlist_count = 0
    paper_trade_candidate_count = 0

    for directory in prior_dirs:
        result_path = directory / "RESULTS.json"
        if not result_path.exists():
            parse_errors.append({"iteration": directory.name, "error": "missing RESULTS.json"})
            continue
        try:
            result = load_json(result_path)
        except Exception as exc:  # pragma: no cover - diagnostic artifact path
            parse_errors.append({"iteration": directory.name, "error": repr(exc)})
            continue

        status = str(result.get("status", "missing_status"))
        failures = strict_gate_failures(result)
        n_trials = int(result.get("n_trials") or 0)
        winner = bool(result.get("winner", False))
        blocked = bool(failures) or not winner

        status_counts[status] += 1
        n_trials_sum += n_trials
        winner_true_count += int(winner)
        strict_winner_count += int(status == "strict_winner")
        candidate_watchlist_count += int(status == "candidate_watchlist")
        paper_trade_candidate_count += int(status == "paper_trade_candidate")

        if status == "economic_beater_not_validated" and failures:
            economic_beater_blocked += 1
        if status in PROMOTIONAL and failures:
            promotional_with_failed_gates += 1

        rows.append(
            {
                "iteration": directory.name,
                "status": status,
                "winner": winner,
                "n_trials": n_trials,
                "failed_hard_gates": sorted(failures),
                "blocked_for_promotion": blocked,
            }
        )

    artifact_complete = not missing_dirs and not parse_errors and len(rows) == 28
    no_promotional_labels = (
        strict_winner_count == 0 and candidate_watchlist_count == 0 and paper_trade_candidate_count == 0
    )
    no_strict_winners = winner_true_count == 0 and strict_winner_count == 0
    all_economic_beaters_blocked = economic_beater_blocked == status_counts.get("economic_beater_not_validated", 0)
    status = "fail"

    audit = {
        "iteration": ITERATION,
        "parsed_iterations": len(rows),
        "missing_dirs": missing_dirs,
        "parse_errors": parse_errors,
        "status_counts": dict(sorted(status_counts.items())),
        "prior_n_trials_sum": n_trials_sum,
        "winner_true_count": winner_true_count,
        "strict_winner_count": strict_winner_count,
        "candidate_watchlist_count": candidate_watchlist_count,
        "paper_trade_candidate_count": paper_trade_candidate_count,
        "economic_beater_not_validated_count": status_counts.get("economic_beater_not_validated", 0),
        "economic_beater_blocked_by_failed_gates_count": economic_beater_blocked,
        "promotional_with_failed_gates_count": promotional_with_failed_gates,
        "rows": rows,
    }

    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": 0,
        "mcpt_reps": {},
        "best_config": None,
        "winner": False,
        "metrics": {
            "audit_type": "phase3_economic_beater_gate_audit",
            "parsed_iterations": len(rows),
            "status_counts": audit["status_counts"],
            "prior_n_trials_sum": n_trials_sum,
            "memory_cumulative_n_trials_before": 312,
            "memory_cumulative_n_trials_after": 312,
            "winner_true_count": winner_true_count,
            "strict_winner_count": strict_winner_count,
            "economic_beater_not_validated_count": status_counts.get("economic_beater_not_validated", 0),
            "economic_beater_blocked_by_failed_gates_count": economic_beater_blocked,
        },
        "benchmark": {
            "primary": "candidate_specific_phase3_primary_buy_hold_from_prior_results",
            "opportunity": "SPY_buy_hold_context_where_saved",
        },
        "gates": {
            "artifact_completeness": artifact_complete,
            "zero_winner_true": no_strict_winners,
            "zero_promotional_statuses": no_promotional_labels,
            "economic_beaters_all_blocked_by_failed_or_missing_strict_gates": all_economic_beaters_blocked,
            "trial_reconciliation_to_memory": n_trials_sum <= 312,
            "mcpt_recomputed": False,
            "pbo_recomputed": False,
            "dsr_recomputed": False,
        },
        "kill_switches": [
            "prior economic beaters remain blocked by failed strict gates",
            "audit-only iteration cannot create a promotional label",
        ],
        "artifacts": [
            str(OUT_DIR / "PRE_REG.md"),
            str(OUT_DIR / "run_iteration.py"),
            str(OUT_DIR / "audit.json"),
            str(OUT_DIR / "RESULTS.json"),
        ],
        "notes": (
            "Conservative audit-only iteration. Public docs contain pre-existing future-state "
            "lines, so this audit follows user-supplied MEMORY state and does not rewrite prior artifacts."
        ),
    }

    (OUT_DIR / "audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
