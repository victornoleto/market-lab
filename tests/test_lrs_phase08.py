from __future__ import annotations

import pandas as pd

from lrs.phases.phase08_final_gates.run import (
    N_TRIALS,
    PHASE7A_CSV,
    PHASE7D_CSV,
    QQQ_CONFIG,
    SPY_CONFIG,
)


def test_ledger_is_frozen_at_4377() -> None:
    assert N_TRIALS == 4377


def test_spy_config_matches_a_committed_phase7a_trial_row() -> None:
    df = pd.read_csv(PHASE7A_CSV)

    rows = df[
        (df["config_type"] == "ensemble")
        & (df["base_name"] == SPY_CONFIG["base_name"])
        & (df["window_set"] == SPY_CONFIG["window_set"])
        & (df["lag_days"] == SPY_CONFIG["lag"])
    ]

    assert len(rows) == 1
    # The chosen row is the 7A round survivor (WF 13/17).
    assert int(rows.iloc[0]["wf_beats"]) == 13
    assert int(rows.iloc[0]["wf_windows"]) == 17


def test_qqq_config_matches_a_committed_phase7d_trial_row() -> None:
    df = pd.read_csv(PHASE7D_CSV)

    rows = df[
        (df["config_type"] == "quadratic")
        & (df["branch"] == "QQQ")
        & (df["sigma_target"] == QQQ_CONFIG["sigma_target"])
        & (df["rv_window"] == QQQ_CONFIG["rv_window"])
        & (df["lag_days"] == QQQ_CONFIG["lag"])
    ]

    assert len(rows) == 1
    # The chosen row is the 7D round survivor (WF 8/11).
    assert int(rows.iloc[0]["wf_beats"]) == 8
    assert int(rows.iloc[0]["wf_windows"]) == 11
