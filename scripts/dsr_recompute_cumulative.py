"""Re-compute G2 DSR p-value cumulative across all study iterations.

Trigger: after T5 expansion (iter_025) completes, n_trials_cumulative
becomes 426. Walks every iter directory, reads stored strategy_returns,
re-runs g2_dsr_p_value with new N, and writes back under a v2 key.

Citation: spec §5.3 (docs/specs/2026-05-08-t5-expansion-design.md);
[advances_fin_ml, p.208-211].

NOTE: This script requires that each iter's verdict.json results have a
``_strategy_returns_csv`` key pointing to a CSV file with a ``ret`` column.
Existing iterations (000-024) do NOT have this key — ``_strategy_returns``
was stripped before writing verdict.json by ``_write_iter_artifacts``.
Results for iterations without this key are silently skipped. Future
iterations must persist strategy_returns.csv and add the key to benefit
from this script.
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from studies.letf_rotation_hunt.core.gates import g2_dsr_p_value

logger = logging.getLogger(__name__)


def recompute_all(
    iters_root: Path, n_trials_new: int,
    v2_key: str = "g2_dsr_p_cumulative_v2_post_t5_expansion",
) -> dict[str, dict]:
    """Walk every iter dir under iters_root, recompute G2 cumulative.

    Returns a dict {iter_name: {config_name: {old_p, new_p, flipped}}}.
    Writes new key into verdict.json in place; preserves old keys.
    """
    summary: dict[str, dict] = {}
    for iter_dir in sorted(iters_root.iterdir()):
        if not iter_dir.is_dir():
            continue
        verdict_path = iter_dir / "verdict.json"
        if not verdict_path.exists():
            continue
        verdict = json.loads(verdict_path.read_text())
        iter_summary: dict = {}
        changed = False
        for r in verdict.get("results", []):
            csv_rel = r.get("_strategy_returns_csv")
            if not csv_rel:
                continue
            rets = pd.read_csv(iter_dir / csv_rel, index_col=0)["ret"]
            new_p = float(g2_dsr_p_value(rets, n_trials=n_trials_new)["p_value"])
            old_p = float(r.get("gates", {}).get("g2_dsr_p_cumulative", float("nan")))
            r.setdefault("gates", {})[v2_key] = new_p
            iter_summary[r.get("config_name", "?")] = {
                "old_p": old_p, "new_p": new_p,
                "flipped_to_fail": (old_p < 0.05) and (new_p >= 0.05),
            }
            changed = True
        if changed:
            verdict_path.write_text(json.dumps(verdict, indent=2))
        if iter_summary:
            summary[iter_dir.name] = iter_summary
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters-root", type=Path,
                        default=Path("studies/letf_rotation_hunt/runs/original"))
    parser.add_argument("--n-trials-new", type=int, required=True)
    args = parser.parse_args()
    summary = recompute_all(args.iters_root, args.n_trials_new)
    flipped = [
        f"{i}/{c}" for i, configs in summary.items()
        for c, info in configs.items() if info["flipped_to_fail"]
    ]
    print(f"Re-computed DSR for {sum(len(v) for v in summary.values())} configs.")
    if flipped:
        print(f"WARNING: {len(flipped)} configs flipped PASS->FAIL: {flipped[:10]}")
    else:
        print("No configs flipped PASS->FAIL.")


if __name__ == "__main__":
    main()
