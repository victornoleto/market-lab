import json
from pathlib import Path

import pytest


def test_aggregate_propagates_structured_hallucinations(tmp_path, monkeypatch):
    """When judges emit structured hallucinations (dict with claim/action),
    aggregator must preserve the structure in a new `retry_hint_structured` field."""
    from scripts import aggregate_judges

    val_dir = tmp_path / ".validation"
    val_dir.mkdir()
    j1 = {
        "slug": "fake",
        "overall_verdict": "FAIL",
        "support_ratio": 0.80,
        "n_claims_checked": 10,
        "hallucinations_found": [
            {
                "claim": "Kelly fraction f/2, f/4 is recommended",
                "cited_page": "[p.100]",
                "actual_page": None,
                "evidence_quote": None,
                "action": "remove",
            },
        ],
    }
    j2 = {
        "slug": "fake",
        "overall_verdict": "FAIL",
        "support_ratio": 0.75,
        "n_claims_checked": 10,
        "hallucinations_found": [
            {
                "claim": "MPT is discussed on p.1129",
                "cited_page": "[p.1129]",
                "actual_page": 942,
                "evidence_quote": "modern portfolio theory appears on...",
                "action": "relocate_to_p_942",
            },
        ],
    }
    (val_dir / "fake_judge_1.json").write_text(json.dumps(j1))
    (val_dir / "fake_judge_2.json").write_text(json.dumps(j2))

    monkeypatch.setattr(aggregate_judges, "VALIDATION_DIR", val_dir)
    paths, r, m = aggregate_judges.find_latest_judge_jsons("fake")
    assert paths[1] is not None and paths[2] is not None

    out = aggregate_judges.build_retry_hint_structured(
        aggregate_judges.load_judge(paths[1]),
        aggregate_judges.load_judge(paths[2]),
    )
    assert len(out) == 2
    # Order: j1 items first, then j2
    assert out[0]["action"] == "remove"
    assert out[1]["action"] == "relocate_to_p_942"
    assert out[0]["claim"] == "Kelly fraction f/2, f/4 is recommended"


def test_legacy_string_hallucinations_wrapped_gracefully(tmp_path, monkeypatch):
    """Old judge JSONs had hallucinations_found as list[str] — aggregator
    must wrap them as {claim: str, action: 'verify'}."""
    from scripts import aggregate_judges

    val_dir = tmp_path / ".validation"
    val_dir.mkdir()
    j1 = {
        "slug": "legacy",
        "overall_verdict": "FAIL",
        "support_ratio": 0.70,
        "n_claims_checked": 5,
        "hallucinations_found": ["legacy string describing an unsupported claim"],
    }
    j2 = {
        "slug": "legacy",
        "overall_verdict": "PASS",
        "support_ratio": 0.95,
        "n_claims_checked": 5,
        "hallucinations_found": [],
    }
    (val_dir / "legacy_judge_1.json").write_text(json.dumps(j1))
    (val_dir / "legacy_judge_2.json").write_text(json.dumps(j2))

    monkeypatch.setattr(aggregate_judges, "VALIDATION_DIR", val_dir)
    paths, r, m = aggregate_judges.find_latest_judge_jsons("legacy")

    out = aggregate_judges.build_retry_hint_structured(
        aggregate_judges.load_judge(paths[1]),
        aggregate_judges.load_judge(paths[2]),
    )
    assert len(out) == 1
    assert out[0]["claim"] == "legacy string describing an unsupported claim"
    assert out[0]["action"] == "verify"


def test_dedup_same_claim_from_both_judges(tmp_path, monkeypatch):
    from scripts import aggregate_judges

    val_dir = tmp_path / ".validation"
    val_dir.mkdir()
    claim_text = "Same claim reported by both judges" + "x" * 20
    j1 = {
        "slug": "dup",
        "overall_verdict": "FAIL",
        "support_ratio": 0.80,
        "n_claims_checked": 5,
        "hallucinations_found": [{"claim": claim_text, "action": "remove"}],
    }
    j2 = {
        "slug": "dup",
        "overall_verdict": "FAIL",
        "support_ratio": 0.80,
        "n_claims_checked": 5,
        "hallucinations_found": [{"claim": claim_text, "action": "remove"}],
    }
    (val_dir / "dup_judge_1.json").write_text(json.dumps(j1))
    (val_dir / "dup_judge_2.json").write_text(json.dumps(j2))
    monkeypatch.setattr(aggregate_judges, "VALIDATION_DIR", val_dir)
    paths, _, _ = aggregate_judges.find_latest_judge_jsons("dup")

    out = aggregate_judges.build_retry_hint_structured(
        aggregate_judges.load_judge(paths[1]),
        aggregate_judges.load_judge(paths[2]),
    )
    assert len(out) == 1, f"expected dedup to 1, got {len(out)}"
