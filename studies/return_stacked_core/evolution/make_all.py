"""Deterministic rebuild of the evolution sub-study (e00 -> e04).

Usage:
    uv run python studies/return_stacked_core/evolution/make_all.py
    uv run python studies/return_stacked_core/evolution/make_all.py --only e01
"""
from __future__ import annotations

import argparse
import sys

from studies.return_stacked_core.evolution import (
    e00_anchor_gate,
    e01_grids,
    e02_gauntlet,
    e03_rebalance,
    e04_longwindow,
    e05_bands,
    e06_band_gauntlet,
    e07_band_simplex,
    e08_band_menus,
    e09_band_5asset,
    e10_ballast,
    e11_deep_validation,
)

STEPS = {
    "e00": e00_anchor_gate.main,
    "e01": e01_grids.main,
    "e02": e02_gauntlet.main,
    "e03": e03_rebalance.main,
    "e04": e04_longwindow.main,
    "e05": e05_bands.main,
    "e06": e06_band_gauntlet.main,
    "e07": e07_band_simplex.main,
    "e08": e08_band_menus.main,
    "e09": e09_band_5asset.main,
    "e10": e10_ballast.main,
    "e11": e11_deep_validation.main,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=sorted(STEPS), default=None)
    args = parser.parse_args()
    steps = [args.only] if args.only else list(STEPS)
    for name in steps:
        print(f"\n===== {name} =====")
        rc = STEPS[name]()
        if name == "e00" and rc:
            print("anchor gate failed — stopping.", file=sys.stderr)
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
