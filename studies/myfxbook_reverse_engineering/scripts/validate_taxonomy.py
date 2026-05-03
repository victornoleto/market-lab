"""5R-1-hardening Wave B item 2 — taxonomy validator.

Scans `frozen_rules/<id>.md` and checks each entry against the closed taxonomy
in `shared/decoder_taxonomy.py`. Reports per-system status and a summary table.

Two modes:
- default (legacy v2 audit): runs strict=False, classifies entries as PASS / WARN
  (legacy missing reason_code) / FAIL (family outside enum). Useful pre-R1.
- --strict: runs strict=True, raises on any v2 entry that violates new rules.
  Use after R1 v3 to confirm every frozen_rule satisfies the contract.

Usage:
    uv run python -m studies.myfxbook_reverse_engineering.scripts.validate_taxonomy
    uv run python -m studies.myfxbook_reverse_engineering.scripts.validate_taxonomy --strict
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from studies.myfxbook_reverse_engineering.shared.decoder_taxonomy import (  # noqa: E402
    Family,
    TaxonomyError,
    family_names,
    provisional_families,
    reason_code_values,
    validate_decoder_output,
)


@dataclass
class Row:
    system_id: str
    family: str
    reason_code: str | None
    candidate_new_family: str | None
    status: str  # PASS / WARN / FAIL
    note: str


def _parse_yaml_field(block: str, key: str) -> str | None:
    m = re.search(rf"^{key}:\s*(\S+)", block, re.MULTILINE)
    if not m:
        return None
    val = m.group(1).strip()
    if val in ("null", "None", "~", '""', "''"):
        return None
    return val


def audit(strict: bool) -> tuple[list[Row], dict[str, int]]:
    base = REPO_ROOT / "studies" / "myfxbook_reverse_engineering" / "frozen_rules"
    rows: list[Row] = []
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}

    files = sorted(p for p in base.glob("*.md") if p.name not in ("CHANGELOG.md", "README.md"))
    for p in files:
        text = p.read_text()
        m = re.search(r"^---\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
        if not m:
            rows.append(Row(p.stem, "?", None, None, "FAIL", "no YAML front-matter"))
            counts["FAIL"] += 1
            continue
        block = m.group(1)
        family = _parse_yaml_field(block, "family") or "?"
        reason_code = _parse_yaml_field(block, "reason_code")
        candidate_new_family = _parse_yaml_field(block, "candidate_new_family")
        try:
            validate_decoder_output(
                family=family,
                reason_code=reason_code,
                candidate_new_family=candidate_new_family,
                strict=True,  # always check strict here; if strict mode, raise on any
            )
            status = "PASS"
            note = ""
        except TaxonomyError as e:
            if strict:
                raise
            status = "WARN" if family in family_names() else "FAIL"
            note = str(e).splitlines()[0][:100]
        counts[status] += 1
        rows.append(Row(p.stem, family, reason_code, candidate_new_family, status, note))
    return rows, counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit frozen_rules/ against decoder_taxonomy.py.")
    ap.add_argument("--strict", action="store_true",
                    help="Raise on any v2 entry that violates the new contract (use post-R1).")
    args = ap.parse_args(argv)

    print("=" * 80)
    print(f"Taxonomy snapshot — {len(family_names())} families ({len(provisional_families())} provisional)")
    print("Provisional:", ", ".join(f.value for f in provisional_families()))
    print("UNCAT reason_codes:", ", ".join(reason_code_values()))
    print("=" * 80)
    print()

    try:
        rows, counts = audit(strict=args.strict)
    except TaxonomyError as e:
        print(f"❌ STRICT FAIL: {e}")
        return 1

    print(f"{'system_id':<12} {'family':<28} {'reason_code':<22} {'candidate_new':<20} {'status':<6} note")
    print("-" * 120)
    for r in rows:
        print(
            f"{r.system_id:<12} {r.family:<28} {(r.reason_code or '—'):<22} "
            f"{(r.candidate_new_family or '—'):<20} {r.status:<6} {r.note}"
        )
    print()
    print(f"Summary: PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']} (total {sum(counts.values())})")
    if counts["FAIL"] and not args.strict:
        print("⚠ FAIL count > 0 — non-enum families present. Investigate before R1.")
        return 2
    if counts["WARN"] and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
