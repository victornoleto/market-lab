"""Phase 3.6 Family I — cross-library concordance check (gate 9).

Reconciles the Family I ensemble daily returns against independent
``(prev_weight × return)`` reconstruction on OOS.

For Family I, the verdict is **FAIL-structural** — 0 candidate
indicators survived the Bonferroni-corrected MCPT screen at
p < 0.001. The ensemble cannot be formed, so there is no canonical
returns track to cross-lib-reconcile. Under plan §5 gate 9 rules,
cross-lib is mandatory only when the strategy is otherwise a winner;
here, the gate is **DEFERRED** with a formal note.

We still emit the `cross_lib_check.md` report so the artifact tree
matches the family template (A-H), documenting why full bt/vectorbt/
backtrader runs are not required.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path("/var/www/pessoal/ai-trade")
sys.path.insert(0, str(ROOT / "src"))

OUT_DIR = ROOT / "reports/phase_3_6/i_stat_sound_indicators"


def main() -> None:
    agg_path = OUT_DIR / "AGGREGATE.json"
    if not agg_path.exists():
        raise FileNotFoundError(
            f"{agg_path} missing. Run "
            "`scripts/run_phase3_6_i_stat_sound_indicators.py` first."
        )
    with agg_path.open() as f:
        agg = json.load(f)

    verdict = agg.get("verdict", "UNKNOWN")
    survivors = agg.get("survivors", [])
    n_survivors = len(survivors)
    n_candidates = len(agg.get("candidate_pool", []))

    report = [
        "# Phase 3.6 Family I — cross-lib concordance check",
        "",
        f"**Date:** 2026-04-23  |  **Verdict upstream:** {verdict}",
        "",
        "## Method",
        "",
        (
            f"Family I is a pure return-series strategy ({n_survivors} "
            f"survivor(s) / {n_candidates} candidates). For Families A-C "
            "(FAIL verdicts), the cross-lib protocol collapses to "
            "confirming that canonical daily returns equal "
            "`(prev_weight × ret).sum(axis=1)` — an arithmetic identity "
            "given the clean return-series engine pattern (see "
            "`letf_rotation.py`, `[advances_fin_ml, p.31-34]`). A full "
            "3-library replication (bt + vectorbt + backtrader) is "
            "reserved for strategies that clear the edge gates."
        ),
        "",
        "## Verdict on gate 9",
        "",
    ]
    if verdict.startswith("FAIL") and n_survivors == 0:
        report += [
            (
                "**DEFERRED / NOT EVALUATED** — 0 indicators survived the "
                "Bonferroni-corrected MCPT screen at p<0.001, so no "
                "ensemble exists to cross-lib reconcile. Under plan §5 gate "
                "9, cross-lib is mandatory only on winner candidacies; a "
                "**structural FAIL at the screening layer** (upstream of "
                "any engine arithmetic) cannot be cured by cross-lib "
                "replication, and we document the gate as non-applicable."
            ),
            "",
            "## Why a cross-lib run would not change the verdict",
            "",
            (
                "The FAIL is **upstream of any engine** — it happens at the "
                "statistical screening layer, before a trading simulation "
                "runs. The verdict says: even if we assume the "
                "best-possible engine arithmetic, the candidate indicators "
                "do not carry p<0.001 (Bonferroni) edge on the 5-ETF "
                "universe over IS 2004-2017. Cross-lib replication tests "
                "engine purity, not statistical significance."
            ),
            "",
        ]
    else:
        report += [
            (
                "**NOT EVALUATED** — family verdict is not WINNER; the "
                "arithmetic sanity check would show canon = "
                "(w × r).sum(axis=1) by construction for this clean "
                "return-series strategy, but that alone cannot upgrade "
                "the verdict."
            ),
            "",
        ]

    report += [
        "## Citations",
        "",
        "- Clean return-series engine pattern: `letf_rotation.py` docstring + "
        "`[advances_fin_ml, p.31-34]` (lookahead-bias timing).",
        "- Plan §5 gate 9 mandate for winner-only cross-lib: "
        "`docs/plans/2026-04-23-find-swing-winner-phase-3-6.md`.",
        "",
    ]
    (OUT_DIR / "cross_lib_check.md").write_text("\n".join(report))
    print(f"[write] {OUT_DIR / 'cross_lib_check.md'}")
    print(f"[verdict] {verdict} — cross-lib DEFERRED")


if __name__ == "__main__":
    main()
