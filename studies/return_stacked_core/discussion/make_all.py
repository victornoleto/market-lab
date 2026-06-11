#!/usr/bin/env python3
"""Orchestrator for the discussion pipeline: runs s00..s07 in order, fail-fast.

Usage:
    uv run python studies/return_stacked_core/discussion/make_all.py
    uv run python studies/return_stacked_core/discussion/make_all.py --only s04
    uv run python studies/return_stacked_core/discussion/make_all.py --with-network

Network steps (s01b AQR fetch) are SKIPPED by default — the extracted CSV is
committed, so the offline pipeline is fully reproducible. Determinism: no RNG
anywhere; two consecutive runs must produce byte-identical tables/*.csv.
"""
from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PKG = "studies.return_stacked_core.discussion"
STEPS = [
    ("s00", "s00_verify_anchor"),
    ("s01", "s01_build_series"),
    ("s02", "s02_episodes"),
    ("s03", "s03_correlations"),
    ("s04", "s04_simplex"),
    ("s05", "s05_ablations"),
    ("s06", "s06_extended_1970"),
    ("s07", "s07_figures"),
]
NETWORK_STEPS = [("s01b", "s01b_fetch_aqr_carry")]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="run a single step (e.g. s04)")
    parser.add_argument("--with-network", action="store_true",
                        help="also run s01b (AQR fetch) before s01")
    args = parser.parse_args(argv)

    steps = list(STEPS)
    if args.with_network:
        steps = steps[:1] + NETWORK_STEPS + steps[1:]
    if args.only:
        steps = [(sid, mod) for sid, mod in steps if sid == args.only]
        if not steps:
            print(f"unknown step {args.only!r}", file=sys.stderr)
            return 2

    for sid, mod_name in steps:
        t0 = time.time()
        print(f"=== {sid}: {mod_name} ===")
        module = importlib.import_module(f"{PKG}.{mod_name}")
        rc = module.main()
        print(f"=== {sid} done in {time.time() - t0:.1f}s (rc={rc}) ===\n")
        if rc != 0:
            print(f"PIPELINE ABORTED at {sid} (rc={rc})", file=sys.stderr)
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
