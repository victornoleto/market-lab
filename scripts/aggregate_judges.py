"""
aggregate_judges.py — Layer 3 aggregation (deterministic).

Reads the latest JSON of each adversarial judge (1 and 2) from
books/summaries/.validation/<slug>_judge_{1,2}[_retryN].json, optionally cross-
checks against the layer-2 deterministic citation report
(/tmp/citecheck_<slug>.json), and applies the decision matrix from
.claude/commands/validate-summary.md (lines 91-97).

This script implements layer-3 aggregation as a deterministic step instead of
relying on the orchestrator LLM to apply the matrix in-prompt. This is what
makes the "fallback to disk" mitigation (Camada A) work: if the subagent tool
result is lost in transit (Claude Code issue #44068), the JSON written by the
judge is still readable from disk and aggregation proceeds normally.

Usage:
  python scripts/aggregate_judges.py <slug>
  python scripts/aggregate_judges.py <slug> --citecheck /tmp/citecheck_<slug>.json
  python scripts/aggregate_judges.py <slug> --json

Exit codes:
  0 — PASS
  1 — BORDERLINE
  2 — FAIL (any judge FAIL, or strong PASS/FAIL discordance, or layer-2 had failures while both judges PASSed)
  3 — MISSING_JSON (one or both judge JSONs not found on disk; orchestrator should retry)
  4 — I/O or parse error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALIDATION_DIR = Path("books/summaries/.validation")

# Pattern matches: <slug>_judge_<N>.json or <slug>_judge_<N>_retry<M>.json
JUDGE_FILE_RE = re.compile(r"^(?P<slug>.+)_judge_(?P<jid>[12])(?:_retry(?P<retry>\d+))?\.json$")


def find_latest_judge_jsons(slug: str) -> tuple[dict[int, Path | None], int | None, list[int]]:
    """Find the latest retry round where BOTH judges wrote a JSON.

    Returns:
      paths: {1: Path|None, 2: Path|None} — JSONs for the chosen round
      chosen_round: the retry number selected (0 = original, None if no aggregable round)
      missing_at_higher: list of judge_ids that have JSONs at higher retries with no pair
                        (signals the orchestrator that one judge was re-run but the other failed)
    """
    by_round: dict[int, dict[int, Path]] = {}
    if not VALIDATION_DIR.exists():
        return {1: None, 2: None}, None, []
    for p in VALIDATION_DIR.iterdir():
        if not p.is_file() or not p.name.endswith(".json"):
            continue
        m = JUDGE_FILE_RE.match(p.name)
        if not m or m.group("slug") != slug:
            continue
        jid = int(m.group("jid"))
        retry = int(m.group("retry")) if m.group("retry") else 0
        by_round.setdefault(retry, {})[jid] = p

    paired_rounds = sorted([r for r, jdict in by_round.items() if 1 in jdict and 2 in jdict])
    if not paired_rounds:
        # No round has both judges — return whatever we have for diagnostics
        latest = {1: None, 2: None}
        for r in sorted(by_round.keys(), reverse=True):
            for jid in (1, 2):
                if latest[jid] is None and jid in by_round[r]:
                    latest[jid] = by_round[r][jid]
        return latest, None, []

    chosen = paired_rounds[-1]
    paths = {1: by_round[chosen][1], 2: by_round[chosen][2]}

    # Detect higher rounds that have only one judge (orphan retry)
    missing_at_higher: list[int] = []
    for r in sorted(by_round.keys()):
        if r <= chosen:
            continue
        present = list(by_round[r].keys())
        if len(present) == 1:
            # The OTHER judge is missing at this higher round
            missing_jid = 2 if present[0] == 1 else 1
            missing_at_higher.append(missing_jid)

    return paths, chosen, missing_at_higher


def load_judge(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def layer2_has_failures(citecheck_path: Path | None) -> bool | None:
    """Read /tmp/citecheck_<slug>.json (output of `check_citations.py --json`).

    Returns True if any failures, False if clean, None if file missing.
    """
    if citecheck_path is None or not citecheck_path.exists():
        return None
    try:
        with citecheck_path.open() as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    fails = data.get("fail", data.get("failures"))
    if isinstance(fails, list):
        return len(fails) > 0
    if isinstance(fails, int):
        return fails > 0
    summary = data.get("summary", {})
    return summary.get("fail", 0) > 0


def decide(j1: dict, j2: dict, layer2_failed: bool | None) -> tuple[str, str]:
    """Apply the matrix from .claude/commands/validate-summary.md lines 91-97.

    Returns (verdict, reasoning).
    """
    v1 = j1["overall_verdict"].upper()
    v2 = j2["overall_verdict"].upper()
    verdicts = {v1, v2}

    if "FAIL" in verdicts and verdicts != {"FAIL"}:
        return "FAIL", f"Strong discordance: J1={v1}, J2={v2} (any FAIL → FAIL; self-consistency broken)"
    if verdicts == {"FAIL"}:
        return "FAIL", "Both judges FAIL"
    if verdicts == {"PASS"} and layer2_failed is True:
        return "FAIL", "Both judges PASS but layer-2 deterministic checker found failures (judges were too lenient)"
    if verdicts == {"PASS"}:
        return "PASS", "Both judges PASS, layer-2 clean"
    if verdicts == {"PASS", "BORDERLINE"}:
        return "BORDERLINE", "One PASS, one BORDERLINE — accepted with note"
    if verdicts == {"BORDERLINE"}:
        return "BORDERLINE", "Both judges BORDERLINE"
    return "FAIL", f"Unhandled combination J1={v1}, J2={v2}"


def build_retry_hint_structured(j1: dict, j2: dict) -> list[dict]:
    """Consolidate structured hallucinations from both judges into a
    dedup'd list suitable for the book-reader retry prompt.

    Handles both legacy (string) and structured (dict) hallucination formats.
    Strings are wrapped as {claim: str, action: "verify"}. Dedup key is the
    first 100 chars of claim.
    """
    merged: list[dict] = []
    seen_claims: set[str] = set()
    for jd in (j1, j2):
        for h in jd.get("hallucinations_found", []) or []:
            if isinstance(h, str):
                entry = {
                    "claim": h,
                    "cited_page": None,
                    "actual_page": None,
                    "evidence_quote": None,
                    "action": "verify",
                }
            elif isinstance(h, dict):
                entry = {
                    "claim": h.get("claim", ""),
                    "cited_page": h.get("cited_page"),
                    "actual_page": h.get("actual_page"),
                    "evidence_quote": h.get("evidence_quote"),
                    "action": h.get("action", "verify"),
                }
            else:
                continue
            key = entry["claim"][:100]
            if key in seen_claims:
                continue
            seen_claims.add(key)
            merged.append(entry)
    return merged


def render_human(slug: str, j1: dict, j2: dict, verdict: str, reasoning: str) -> str:
    lines = [f"=== Aggregation: {slug} → {verdict} ==="]
    lines.append(f"Reasoning: {reasoning}")
    for jid, jd in ((1, j1), (2, j2)):
        ratio = jd.get("support_ratio", 0) * 100
        n = jd.get("n_claims_checked", 0)
        halluc = jd.get("hallucinations_found", []) or []
        lines.append(
            f"  Judge #{jid}: {jd['overall_verdict']} ratio={ratio:.1f}% claims={n} halluc={len(halluc)}"
        )
        for h in halluc:
            lines.append(f"    - {h}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--citecheck", type=Path, default=None,
                    help="Path to /tmp/citecheck_<slug>.json from layer 2 (optional)")
    ap.add_argument("--json", action="store_true", help="Emit JSON to stdout instead of human format")
    args = ap.parse_args()

    paths, chosen_round, missing_at_higher = find_latest_judge_jsons(args.slug)
    missing = [jid for jid, p in paths.items() if p is None]
    if missing:
        msg = f"MISSING: no paired judge round found; absent judge_id(s)={missing} in {VALIDATION_DIR}"
        print(msg, file=sys.stderr)
        if args.json:
            print(json.dumps({"slug": args.slug, "verdict": "MISSING", "missing_judges": missing}))
        return 3
    if missing_at_higher:
        # A higher retry round has one judge but not the other — orphan retry
        msg = (f"MISSING: orphan retry detected — judge_id(s)={missing_at_higher} have no JSON "
               f"at retry round > {chosen_round}. Re-dispatch missing judge(s) before aggregating.")
        print(msg, file=sys.stderr)
        if args.json:
            print(json.dumps({"slug": args.slug, "verdict": "MISSING", "missing_judges": missing_at_higher,
                              "orphan_at_round_gt": chosen_round}))
        return 3

    try:
        j1 = load_judge(paths[1])
        j2 = load_judge(paths[2])
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR loading judge JSON: {e}", file=sys.stderr)
        return 4

    citecheck_path = args.citecheck or Path(f"/tmp/citecheck_{args.slug}.json")
    layer2_failed = layer2_has_failures(citecheck_path)

    verdict, reasoning = decide(j1, j2, layer2_failed)

    if args.json:
        all_halluc = list((j1.get("hallucinations_found") or [])) + list((j2.get("hallucinations_found") or []))
        structured = build_retry_hint_structured(j1, j2)
        out = {
            "slug": args.slug,
            "verdict": verdict,
            "reasoning": reasoning,
            "judge_1": {"verdict": j1["overall_verdict"], "ratio": j1.get("support_ratio"), "halluc": j1.get("hallucinations_found", [])},
            "judge_2": {"verdict": j2["overall_verdict"], "ratio": j2.get("support_ratio"), "halluc": j2.get("hallucinations_found", [])},
            "judge_paths": {"1": str(paths[1]), "2": str(paths[2])},
            "layer2_failed": layer2_failed,
            "hallucinations_consolidated": all_halluc,
            "retry_hint_structured": structured,
        }
        print(json.dumps(out, indent=2))
    else:
        print(render_human(args.slug, j1, j2, verdict, reasoning))
        print(f"Judge JSON paths: J1={paths[1]} J2={paths[2]}")
        if layer2_failed is True:
            print("Layer-2 deterministic check: FAILED (factored into verdict)")
        elif layer2_failed is False:
            print("Layer-2 deterministic check: clean")
        else:
            print(f"Layer-2 deterministic check: not provided ({citecheck_path} missing)")

    return {"PASS": 0, "BORDERLINE": 1, "FAIL": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
