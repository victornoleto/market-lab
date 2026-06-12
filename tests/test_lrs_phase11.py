from __future__ import annotations

import pandas as pd

from lrs.phases.phase11_mix_final_gates.run import (
    BENCHMARK_ID,
    CANDIDATE_ID,
    N_TRIALS,
    PHASE6A_CSV,
    WF_IS_SIZE,
    WF_OOS_SIZE,
    WF_STEP,
)


def test_phase11_ledger_and_walk_forward_are_frozen() -> None:
    assert N_TRIALS == 4569
    assert WF_IS_SIZE == 252 * 5
    assert WF_OOS_SIZE == 252 * 2
    assert WF_STEP == 252 * 2


def test_phase11_candidate_matches_phase6a_decision_row() -> None:
    df = pd.read_csv(PHASE6A_CSV)
    rows = df[df["candidate_id"] == CANDIDATE_ID]

    assert len(rows) == 1
    row = rows.iloc[0]
    assert row["candidate_type"] == "mix"
    assert row["satellite"] == "lrs_spy_headline"
    assert float(row["satellite_share"]) == 0.20
    assert float(row["cagr"]) > float(df.loc[df["candidate_id"] == BENCHMARK_ID, "cagr"].iloc[0])
