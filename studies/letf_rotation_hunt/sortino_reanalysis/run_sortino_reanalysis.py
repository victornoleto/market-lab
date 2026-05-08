"""CLI orchestrator for the sortino_reanalysis sub-study (spec §5.1).

Pipeline:
  1. Recompute Groups A-E (94 rows).
  2. Compute SPY/canonical Sortino-anchors → derive thresholds.
  3. Append edge_vs_spy, edge_vs_canonical, track_a/b_pass columns.
  4. Detect new winner.
  5. If winner_changed: run cohort extension → append Group F → CSV.
  6. Persist sortino_metrics.csv.
  7. Call plot module.
  8. Render report.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.sortino_reanalysis.cohort_extension import (
    extend_cohort_for_new_winner,
)
from studies.letf_rotation_hunt.sortino_reanalysis.recompute import (
    recompute_canonical,
    recompute_regime_medians,
    recompute_spy_anchors,
    recompute_threshold_variants,
    recompute_top10,
)
from studies.letf_rotation_hunt.sortino_reanalysis.winner_detection import (
    CANONICAL_NAME,
    detect_new_winner,
    rebuild_thresholds,
)


def _build_metrics_frame() -> pd.DataFrame:
    print("[sortino] Group A — SPY anchors")
    rows = recompute_spy_anchors()
    print(f"[sortino]   {len(rows)} rows")
    print("[sortino] Group B — canonical")
    rows += recompute_canonical()
    print(f"[sortino]   running total {len(rows)}")
    print("[sortino] Group C — top-10")
    rows += recompute_top10()
    print(f"[sortino]   running total {len(rows)}")
    print("[sortino] Group D — regime medians")
    rows += recompute_regime_medians()
    print(f"[sortino]   running total {len(rows)}")
    print("[sortino] Group E — threshold variants")
    rows += recompute_threshold_variants()
    print(f"[sortino]   running total {len(rows)}")
    return pd.DataFrame(rows)


def _enrich_with_edges_and_passes(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Add sortino_edge_vs_spy / sortino_edge_vs_canonical / track passes.

    Returns enriched df + canonical_sortino_per_track dict for threshold rebuild.
    """
    # SPY anchor per dataset
    spy_rows = df[df["group"] == "A_spy_anchor"]
    spy_sortino = dict(zip(spy_rows["dataset"], spy_rows["sortino"]))
    spy_sharpe = dict(zip(spy_rows["dataset"], spy_rows["sharpe"]))

    # Canonical anchor on lh_56y per track
    can_rows = df[(df["group"] == "B_canonical") & (df["dataset"] == "lh_56y")]
    canonical_sortino = dict(zip(can_rows["track"], can_rows["sortino"]))
    canonical_sharpe = dict(zip(can_rows["track"], can_rows["sharpe"]))

    thresholds = rebuild_thresholds(canonical_sortino)
    track_to_threshold = {
        "gross": thresholds["track_a"],
        "m1": thresholds["track_b_m1"],
        "m2": thresholds["track_b_m2"],
    }

    df = df.copy()
    df["sortino_edge_vs_spy"] = df.apply(
        lambda r: float(r["sortino"] - spy_sortino[r["dataset"]])
        if r["dataset"] in spy_sortino else float("nan"),
        axis=1,
    )
    df["sharpe_edge_vs_spy"] = df.apply(
        lambda r: float(r["sharpe"] - spy_sharpe[r["dataset"]])
        if r["dataset"] in spy_sharpe else float("nan"),
        axis=1,
    )
    df["sortino_edge_vs_canonical"] = df.apply(
        lambda r: float(r["sortino"] - canonical_sortino.get(r["track"], np.nan)),
        axis=1,
    )
    df["sharpe_edge_vs_canonical"] = df.apply(
        lambda r: float(r["sharpe"] - canonical_sharpe.get(r["track"], np.nan)),
        axis=1,
    )
    df["track_threshold_sortino"] = df["track"].map(track_to_threshold)
    df["track_a_pass_sortino"] = (
        (df["track"] == "gross")
        & (df["dataset"] == "lh_56y")
        & (df["sortino"] >= thresholds["track_a"])
    )
    df["track_b_m1_pass_sortino"] = (
        (df["track"] == "m1")
        & (df["dataset"] == "lh_56y")
        & (df["sortino"] >= thresholds["track_b_m1"])
    )
    df["track_b_m2_pass_sortino"] = (
        (df["track"] == "m2")
        & (df["dataset"] == "lh_56y")
        & (df["sortino"] >= thresholds["track_b_m2"])
    )
    return df, canonical_sortino


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sortino re-analysis sub-study")
    parser.add_argument(
        "--out-data-dir", type=Path,
        default=Path("data/sortino_reanalysis"),
    )
    parser.add_argument(
        "--out-report-dir", type=Path,
        default=Path("studies/letf_rotation_hunt/reports/sortino_reanalysis"),
    )
    args = parser.parse_args(argv)
    args.out_data_dir.mkdir(parents=True, exist_ok=True)
    args.out_report_dir.mkdir(parents=True, exist_ok=True)

    df = _build_metrics_frame()
    df, canonical_sortino = _enrich_with_edges_and_passes(df)

    metrics_path = args.out_data_dir / "sortino_metrics.csv"
    df.to_csv(metrics_path, index=False)
    print(f"[sortino] metrics CSV: {metrics_path} ({len(df)} rows)")

    # Winner detection
    changed, new_winner = detect_new_winner(df)
    print(f"[sortino] winner_changed={changed} new_winner={new_winner!r}")

    cohort_csv = args.out_data_dir / "cohort_extension.csv"
    if changed and new_winner is not None and new_winner != CANONICAL_NAME:
        print(f"[sortino] running cohort extension on {new_winner}")
        cohort_df = extend_cohort_for_new_winner(new_winner)
        cohort_df.to_csv(cohort_csv, index=False)
        print(f"[sortino] cohort extension CSV: {cohort_csv} ({len(cohort_df)} rows)")
    else:
        # Remove any stale cohort_extension.csv to keep state honest
        if cohort_csv.exists():
            cohort_csv.unlink()

    # Plots — lazy import so this module loads even before Task 9 ships
    from studies.letf_rotation_hunt.sortino_reanalysis.plot_sortino_reanalysis import (
        plot_sortino_vs_sharpe_scatter,
        plot_track_pass_comparison,
    )
    plot_sortino_vs_sharpe_scatter(df, args.out_report_dir / "sortino_vs_sharpe_scatter.png")
    plot_track_pass_comparison(df, args.out_report_dir / "track_pass_comparison.png")

    print(f"[sortino] DONE. New winner: {new_winner if changed else 'canonical retained'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
