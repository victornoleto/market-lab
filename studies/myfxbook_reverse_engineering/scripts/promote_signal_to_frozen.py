"""5R-1-hardening R1 helper — promote systems/<id>/signal_rule.md to frozen_rules/<id>.md.

Used after each R1 wave: takes the Opus output from each system and copies it to
the frozen_rules/ directory with chmod handling (u+w → write → a-w) and strict
taxonomy validation.

Usage:
    uv run python -m studies.myfxbook_reverse_engineering.scripts.promote_signal_to_frozen \
        --systems 10067081 10192401 10249298 10251631 10475089
    uv run python -m studies.myfxbook_reverse_engineering.scripts.promote_signal_to_frozen --all-r1-pool
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared.decoder_taxonomy import (  # noqa: E402
    TaxonomyError,
    validate_decoder_output,
)

R1_POOL = sorted([
    "10062918","10192401","10224499","10249298","10281851","10475089","10563761",
    "10734338","11155858","11171596","11206045","11207608","11355455","1152318",
    "11628637","1407880","1603276","2373850","2421356","6541963","8647517",
    "9375654","9912554","10067081","10251631","1612420","8577442","9830783",
    "9841939","9843883",
])


def _parse_yaml_field(block: str, key: str) -> str | None:
    m = re.search(rf"^{key}:\s*(\S+)", block, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    if val in ("null", "None", "~", '""', "''"):
        return None
    return val


def promote_one(system_id: str, base: Path, *, strict: bool) -> dict:
    sr = base / "systems" / system_id / "signal_rule.md"
    fr = base / "frozen_rules" / f"{system_id}.md"
    out = {"system_id": system_id, "status": "?", "family": None, "reason_code": None,
           "candidate_new_family": None, "sha256": None}
    if not sr.exists():
        out["status"] = "no_signal_rule"
        return out

    text = sr.read_text()
    m = re.search(r"^---\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    if not m:
        out["status"] = "malformed_yaml"
        return out
    block = m.group(1)
    family = _parse_yaml_field(block, "family")
    reason_code = _parse_yaml_field(block, "reason_code")
    candidate_new_family = _parse_yaml_field(block, "candidate_new_family")
    out.update(family=family, reason_code=reason_code, candidate_new_family=candidate_new_family)

    try:
        validate_decoder_output(
            family=family or "?",
            reason_code=reason_code,
            candidate_new_family=candidate_new_family,
            strict=strict,
        )
    except TaxonomyError as e:
        out["status"] = "taxonomy_violation"
        out["error"] = str(e).splitlines()[0][:200]
        return out

    # chmod u+w if existing read-only
    if fr.exists():
        os.chmod(fr, 0o644)
    shutil.copy2(sr, fr)
    os.chmod(fr, 0o444)
    out["sha256"] = hashlib.sha256(fr.read_bytes()).hexdigest()
    out["status"] = "promoted"
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--systems", nargs="*", help="Specific system_ids to promote.")
    ap.add_argument("--all-r1-pool", action="store_true", help="Promote all 30 R1 pool members.")
    ap.add_argument("--strict", action="store_true", default=True,
                    help="Strict taxonomy validation (default; R1 v3 contract).")
    ap.add_argument("--no-strict", action="store_false", dest="strict",
                    help="Permissive (legacy v2). Only used for retroactive ops.")
    args = ap.parse_args(argv)

    systems = args.systems or (R1_POOL if args.all_r1_pool else [])
    if not systems:
        ap.error("provide --systems IDs or --all-r1-pool")

    base = REPO_ROOT / "studies" / "myfxbook_reverse_engineering"
    print(f"Promoting {len(systems)} systems (strict={args.strict})...")
    print(f"{'system_id':<12} {'family':<28} {'reason_code':<22} {'cnf':<20} {'status':<22} sha256[:12]")
    print("-" * 120)
    n_promoted = n_failed = 0
    for sid in systems:
        r = promote_one(sid, base, strict=args.strict)
        sha_short = (r["sha256"] or "")[:12] if r["sha256"] else "—"
        err = r.get("error", "")
        print(
            f"{sid:<12} {(r['family'] or '?'):<28} {(r['reason_code'] or '—'):<22} "
            f"{(r['candidate_new_family'] or '—'):<20} {r['status']:<22} {sha_short} {err}"
        )
        if r["status"] == "promoted":
            n_promoted += 1
        else:
            n_failed += 1
    print()
    print(f"Promoted: {n_promoted}/{len(systems)}; failed: {n_failed}")
    return 0 if n_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
