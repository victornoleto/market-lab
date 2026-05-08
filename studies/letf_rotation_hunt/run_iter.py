"""Entry point for running ONE iteration of letf_rotation_hunt.

Usage:
    python -m studies.letf_rotation_hunt.run_iter --iter NNN --config configs/iter_NNN.yaml

Reads config YAML, dispatches to appropriate strategy, computes metrics + gates,
writes verdict.json + SUMMARY.md + plots, validates schema.

Idempotent via deterministic seed. Pausable mid-study.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "verdict_schema.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one letf_rotation_hunt iteration")
    parser.add_argument("--iter", required=True, help="Iter number (e.g. 001)")
    parser.add_argument("--config", required=True, type=Path, help="Path to iter config YAML")
    parser.add_argument("--out-dir", type=Path, default=None, help="Override output dir")
    args = parser.parse_args(argv)

    config_path: Path = args.config
    if not config_path.exists():
        print(f"ERROR: config not found: {config_path}", file=sys.stderr)
        return 1

    config = yaml.safe_load(config_path.read_text())
    np.random.seed(config.get("random_seed", 42))

    iter_id = config["iter"]
    out_dir = args.out_dir or (ROOT / "iterations" / iter_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "plots").mkdir(exist_ok=True)
    (out_dir / "tables").mkdir(exist_ok=True)
    (out_dir / "logs").mkdir(exist_ok=True)

    print(f"[run_iter] iter={iter_id} tier={config['tier']}")
    print(f"[run_iter] hypothesis: {config['hypothesis']}")
    print(f"[run_iter] output: {out_dir}")

    # Verdict scaffold (filled by tier dispatcher)
    verdict = {
        "iter": iter_id,
        "tier": config["tier"],
        "tier_inheritance": config.get("tier_inheritance"),
        "hypothesis": config["hypothesis"],
        "primary_citation": config["primary_citation"],
        "datetime_utc": datetime.now(timezone.utc).isoformat(),
        "engine_version": _get_git_sha(),
        "configs_tested": config["configs_tested"],
        "datasets": config["datasets"],
        "windows_used": config.get("windows_used", {}),
        "results": [],
        "best_config": "",
        "best_score": 0.0,
        "best_tier": "FAIL",
        "kill_rule_status": "N/A",
        "advance_to_next_tier": False,
        "cumulative_n_trials_at_iter": config.get("cumulative_n_trials_at_iter", 0),
        "cumulative_n_trials_local": len(config["configs_tested"]),
        "deploy_escalation_eligible": False,
        "synth_parity_pass": True,
    }

    # Dispatch by tier
    tier = config["tier"]
    if tier == "T0":
        try:
            from studies.letf_rotation_hunt.run_iter_t0 import run as run_t0
        except ImportError:
            print(f"[run_iter] tier {tier} dispatcher not implemented yet", file=sys.stderr)
            return 2
        verdict = run_t0(config, verdict, out_dir)
    elif tier.startswith("T1"):
        try:
            from studies.letf_rotation_hunt.run_iter_t1 import run as run_t1
        except ImportError:
            print(f"[run_iter] tier {tier} dispatcher not implemented yet", file=sys.stderr)
            return 2
        verdict = run_t1(config, verdict, out_dir)
    elif tier.startswith("T2"):
        try:
            from studies.letf_rotation_hunt.run_iter_t2 import run as run_t2
        except ImportError:
            print(f"[run_iter] tier {tier} dispatcher not implemented yet", file=sys.stderr)
            return 2
        verdict = run_t2(config, verdict, out_dir)
    elif tier.startswith("T3"):
        try:
            from studies.letf_rotation_hunt.run_iter_t3 import run as run_t3
        except ImportError:
            print(f"[run_iter] tier {tier} dispatcher not implemented yet", file=sys.stderr)
            return 2
        verdict = run_t3(config, verdict, out_dir)
    elif tier.startswith("T4"):
        try:
            from studies.letf_rotation_hunt.run_iter_t4 import run as run_t4
        except ImportError:
            print(f"[run_iter] tier {tier} dispatcher not implemented yet", file=sys.stderr)
            return 2
        verdict = run_t4(config, verdict, out_dir)
    elif tier.startswith("T5"):
        try:
            from studies.letf_rotation_hunt.run_iter_t5 import run as run_t5
        except ImportError:
            print(f"[run_iter] tier {tier} dispatcher not implemented yet", file=sys.stderr)
            return 2
        verdict = run_t5(config, verdict, out_dir)
    else:
        print(f"[run_iter] tier {tier} dispatcher not implemented (final tier T5)", file=sys.stderr)
        return 2

    # Validate verdict schema
    schema = json.loads(SCHEMA_PATH.read_text())
    try:
        jsonschema.validate(verdict, schema)
    except jsonschema.ValidationError as e:
        print(f"ERROR: verdict.json failed schema validation: {e.message}", file=sys.stderr)
        return 3

    # Write verdict.json
    verdict_path = out_dir / "verdict.json"
    verdict_path.write_text(json.dumps(verdict, indent=2, default=str))
    print(f"[run_iter] verdict written: {verdict_path}")

    return 0


def _get_git_sha() -> str:
    """Get current git SHA for engine_version field."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True, timeout=5,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"


if __name__ == "__main__":
    sys.exit(main())
