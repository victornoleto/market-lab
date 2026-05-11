"""Threshold rebuild + new-winner detection for Sortino sub-study (spec §4).

This module implements the two-step post-recompute pipeline described in
STUDY_FINAL_REPORT.md §3.4:

1. ``rebuild_thresholds`` — sets anti-curve-fit thresholds per track by adding
   a fixed margin to the canonical strategy's Sortino (spec §4.1).
2. ``detect_new_winner`` — screens all strategies against Track A threshold and
   returns the best non-canonical challenger, if any (spec §4.3).

Citations
---------
- Anti-curve-fit margin of 0.05: analogous to CSCV multiple-testing adjustment
  for performance metrics `[advances_fin_ml, p.208-211]`.
- Track gate structure: spec §4.1, §4.3 (sortino_reanalysis sub-study).
- Parent study context: STUDY_FINAL_REPORT.md §3.4.
"""
from __future__ import annotations

import pandas as pd

CANONICAL_NAME = "qld_vote_k2_off_zroz"
ANTI_CURVE_FIT_MARGIN = 0.05  # spec §4.1, literal; analogous to CSCV PBO margin [advances_fin_ml, p.208-211]


def rebuild_thresholds(canonical_sortino_per_track: dict[str, float]) -> dict[str, float]:
    """Build Track A / B-M1 / B-M2 thresholds from canonical Sortino per track.

    Per spec §4.1: each threshold = canonical Sortino + 0.05 (literal margin,
    not scaled). The 0.05 margin is an anti-curve-fit buffer, analogous to the
    CSCV multiple-testing adjustment `[advances_fin_ml, p.208-211]`.

    Parameters
    ----------
    canonical_sortino_per_track:
        Mapping with keys ``"gross"``, ``"m1"``, ``"m2"`` containing the
        canonical strategy's annualised Sortino for each track.

    Returns
    -------
    dict with keys ``"track_a"``, ``"track_b_m1"``, ``"track_b_m2"``.
    """
    return {
        "track_a": canonical_sortino_per_track["gross"] + ANTI_CURVE_FIT_MARGIN,
        "track_b_m1": canonical_sortino_per_track["m1"] + ANTI_CURVE_FIT_MARGIN,
        "track_b_m2": canonical_sortino_per_track["m2"] + ANTI_CURVE_FIT_MARGIN,
    }


def detect_new_winner(metrics_df: pd.DataFrame) -> tuple[bool, str | None]:
    """Find new canonical winner under Sortino (spec §4.3).

    Filter: ``dataset == "lh_56y"`` AND ``track == "gross"`` AND
    ``track_a_pass_sortino == True``.  Pick the row with the highest
    ``sortino_edge_vs_canonical``.

    Per spec §4.3 and STUDY_FINAL_REPORT.md §3.4: a winner change is only
    declared when a *non-canonical* strategy clears Track A and posts a higher
    edge than the canonical baseline, avoiding false churn `[advances_fin_ml, p.208-211]`.

    Parameters
    ----------
    metrics_df:
        DataFrame produced by ``recompute.py`` Group E, containing at minimum
        columns: ``strategy``, ``dataset``, ``track``,
        ``sortino_edge_vs_canonical``, ``track_a_pass_sortino``.

    Returns
    -------
    (winner_changed, new_winner_name)
        * ``(False, None)`` — no Track A passers at all.
        * ``(False, CANONICAL_NAME)`` — canonical is still the best passer.
        * ``(True, "<name>")`` — a non-canonical strategy is the new winner.
    """
    candidates = metrics_df[
        (metrics_df["dataset"] == "lh_56y")
        & (metrics_df["track"] == "gross")
        & (metrics_df["track_a_pass_sortino"] == True)  # noqa: E712 (pandas boolean mask requires == True)
    ]
    if candidates.empty:
        return False, None
    best = candidates.sort_values("sortino_edge_vs_canonical", ascending=False).iloc[0]
    if best["strategy"] == CANONICAL_NAME:
        return False, CANONICAL_NAME
    return True, str(best["strategy"])
