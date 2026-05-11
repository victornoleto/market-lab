"""Test verdict.json conforms to schema."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_verdict_schema_valid_minimal():
    """Minimal valid verdict passes schema."""
    import jsonschema

    schema_path = Path("studies/letf_rotation_hunt/core/verdict_schema.json")
    schema = json.loads(schema_path.read_text())

    minimal_verdict = {
        "iter": "001-2026-05-06-T1a-letf-sweep",
        "tier": "T1a",
        "tier_inheritance": None,
        "hypothesis": "Gayed replication on 6 LETFs",
        "primary_citation": "[leverage_for_the_long_run, p.13]",
        "datetime_utc": "2026-05-06T12:00:00Z",
        "engine_version": "abc123",
        "configs_tested": [{"name": "upro_sma200_off_bil"}],
        "datasets": ["lh_56y"],
        "windows_used": {"lh_56y": "1970-01-01..2026-04-30"},
        "results": [{"config_name": "upro_sma200_off_bil"}],
        "best_config": "upro_sma200_off_bil",
        "best_score": 75.0,
        "best_tier": "STRONG",
        "kill_rule_status": "PASS",
        "advance_to_next_tier": True,
        "cumulative_n_trials_at_iter": 6,
        "cumulative_n_trials_local": 6,
        "deploy_escalation_eligible": False,
        "synth_parity_pass": True,
    }

    jsonschema.validate(minimal_verdict, schema)  # raises if invalid


def test_verdict_schema_rejects_missing_field():
    """Missing required field → ValidationError."""
    import jsonschema

    schema_path = Path("studies/letf_rotation_hunt/core/verdict_schema.json")
    schema = json.loads(schema_path.read_text())

    invalid = {"iter": "001-2026-05-06-T1a-test"}  # missing most required fields

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(invalid, schema)
