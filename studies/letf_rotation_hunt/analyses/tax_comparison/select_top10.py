"""Top-10 swing-rotation selection from `runs/original/*/verdict.json`.

Selection rule per spec §2.2:
  1. Walk every verdict.json under iterations_root.
  2. Drop configs whose tier starts with "T2" (static fixed-weight basket).
  3. For each config_name, keep only the most recent iter (latest datetime_utc).
  4. Rank by score_breakdown.total desc; ties broken by lh_56y Sharpe desc.
  5. Take top 10.
"""
from __future__ import annotations

import json
from pathlib import Path

EXCLUDED_TIER_PREFIX = "T2"  # static HFEA-style baskets — not swing rotation
TOP_N = 10


def select_top10(iterations_root: Path) -> list[dict]:
    """Return the top-10 swing-rotation configs.

    Each element is a dict with keys:
        config_name, tier, iter_id, score, sharpe_lh_56y, datetime_utc, source_iter_path

    Parameters
    ----------
    iterations_root : Path
        Directory containing one subdir per iter, each with a verdict.json.

    Returns
    -------
    list[dict]
        Up to TOP_N configs. Empty list if no eligible verdicts found.
    """
    candidates: dict[str, dict] = {}  # config_name → best (latest-iter) record

    for iter_dir in sorted(p for p in iterations_root.iterdir() if p.is_dir()):
        verdict_path = iter_dir / "verdict.json"
        if not verdict_path.exists():
            continue
        try:
            verdict = json.loads(verdict_path.read_text())
        except json.JSONDecodeError:
            continue

        tier = str(verdict.get("tier", ""))
        if tier.startswith(EXCLUDED_TIER_PREFIX):
            continue
        datetime_utc = verdict.get("datetime_utc", "")

        for r in verdict.get("results", []):
            name = r.get("config_name", "")
            if not name:
                continue
            score = float(r.get("score_breakdown", {}).get("total", 0.0))
            sharpe = float(
                r.get("metrics_gross", {})
                 .get("lh_56y", {})
                 .get("sharpe", float("-inf"))
            )
            record = {
                "config_name": name,
                "tier": tier,
                "iter_id": iter_dir.name,
                "score": score,
                "sharpe_lh_56y": sharpe,
                "datetime_utc": datetime_utc,
                "source_iter_path": str(iter_dir),
            }
            prior = candidates.get(name)
            if prior is None or datetime_utc > prior["datetime_utc"]:
                candidates[name] = record

    ranked = sorted(
        candidates.values(),
        key=lambda r: (-r["score"], -r["sharpe_lh_56y"]),
    )
    return ranked[:TOP_N]
