"""CLI orchestrator for cross-lib validation runs.

Usage:
    python -m reports.phase_3_5c.cross_lib.run_wave --wave 1 --stage 1
    python -m reports.phase_3_5c.cross_lib.run_wave --wave 1 --stage 2 --libs bt,vectorbt
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from reports.phase_3_5c.cross_lib.adapters.backtrader_adapter import (
    BacktraderAdapter,
)
from reports.phase_3_5c.cross_lib.adapters.bt_adapter import BtAdapter
from reports.phase_3_5c.cross_lib.adapters.quantstats_adapter import (
    QuantstatsAdapter,
)
from reports.phase_3_5c.cross_lib.adapters.vectorbt_adapter import (
    VectorbtAdapter,
)
from reports.phase_3_5c.cross_lib.types import RunResult, VariantConfig
from reports.phase_3_5c.cross_lib.variants import (
    wave_1_variants,
    wave_2_variants,
    wave_3_variants,
)

RESULTS_DIR = Path("reports/phase_3_5c/cross_lib/results")

ALL_ADAPTERS = {
    "bt": BtAdapter(),
    "vectorbt": VectorbtAdapter(),
    "backtrader": BacktraderAdapter(),
}


def run_wave(wave: int, stage: int, libs: list[str]) -> list[RunResult]:
    if wave == 1:
        variants = wave_1_variants()
    elif wave == 2:
        variants = wave_2_variants()
    elif wave == 3:
        variants = wave_3_variants()
    else:
        raise ValueError(f"Unknown wave {wave}")

    selected_adapters = [ALL_ADAPTERS[name] for name in libs if name in ALL_ADAPTERS]
    all_results: list[RunResult] = []

    for variant in variants:
        windows = variant.windows
        for window in windows:
            # Stage 2 restrictions
            if stage == 2 and pd.Timestamp(window[0]) < pd.Timestamp("2009-01-01"):
                continue

            for adapter in selected_adapters:
                print(f"  {adapter.name} / {variant.variant_id} / {window} / stage {stage}")
                result = adapter.run(variant, window, stage)
                _persist_result(result)
                all_results.append(result)

                # quantstats cross-check: if this run is OK, also run quantstats on its equity
                if result.outcome == "OK" and "quantstats" in libs:
                    qs_result = QuantstatsAdapter().run_on_equity(
                        variant, window, stage, result.equity_curve, adapter.name
                    )
                    _persist_result(qs_result)
                    all_results.append(qs_result)

    return all_results


def _persist_result(result: RunResult) -> None:
    window_slug = f"{result.window[0]}_{result.window[1]}"
    path = (
        RESULTS_DIR
        / f"stage_{result.stage}"
        / result.lib.replace("(", "_").replace(")", "").replace("=", "_")
        / result.variant_id
        / window_slug
    )
    path.mkdir(parents=True, exist_ok=True)

    payload = {
        "variant_id": result.variant_id,
        "lib": result.lib,
        "window": list(result.window),
        "stage": result.stage,
        "cagr": result.cagr,
        "sharpe": result.sharpe,
        "max_dd": result.max_dd,
        "wf_splits_8": result.wf_splits_8,
        "dsr_pval": result.dsr_pval,
        "outcome": result.outcome,
        "error_detail": result.error_detail,
    }
    (path / "result.json").write_text(json.dumps(payload, indent=2, default=str))

    if len(result.equity_curve) > 0:
        result.equity_curve.to_frame("equity").to_parquet(path / "equity.parquet")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", type=int, required=True, choices=[1, 2, 3])
    parser.add_argument("--stage", type=int, required=True, choices=[1, 2])
    parser.add_argument(
        "--libs",
        default="bt,vectorbt,backtrader,quantstats",
        help="Comma-separated list of lib names.",
    )
    args = parser.parse_args()

    libs = args.libs.split(",")
    results = run_wave(args.wave, args.stage, libs)
    print(f"\nCompleted: {len(results)} runs")

    # Quick outcome summary
    by_outcome: dict[str, int] = {}
    for r in results:
        by_outcome[r.outcome] = by_outcome.get(r.outcome, 0) + 1
    print(f"Outcomes: {by_outcome}")


if __name__ == "__main__":
    main()
