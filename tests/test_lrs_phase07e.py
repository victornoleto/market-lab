from __future__ import annotations

import numpy as np
import pytest

from lrs.phases.phase07e_mf_risk_off.run import sleeve_specs


def test_sleeve_specs_names_and_count() -> None:
    base = {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25}

    sleeves = sleeve_specs(base)

    assert [s["name"] for s in sleeves] == [
        "control",
        "100% DBMF",
        "50 base / 50 DBMF",
        "70 DBMF / 30 KMLM",
        "50 base / 50 MF-blend",
    ]


def test_sleeve_specs_weights_sum_to_one() -> None:
    base = {"ZROZSIM": 0.40, "GLDSIM": 0.40, "IEFSIM": 0.20}

    for sleeve in sleeve_specs(base):
        total = sum(sleeve["weights"].values())
        assert total == pytest.approx(1.0), sleeve["name"]


def test_half_base_sleeve_scales_base_correctly() -> None:
    base = {"ZROZSIM": 0.50, "GLDSIM": 0.25, "CASHX": 0.25}

    sleeves = {s["name"]: s["weights"] for s in sleeve_specs(base)}

    half_dbmf = sleeves["50 base / 50 DBMF"]
    assert half_dbmf["ZROZSIM"] == pytest.approx(0.25)
    assert half_dbmf["DBMFSIM"] == pytest.approx(0.50)
    blend = sleeves["50 base / 50 MF-blend"]
    assert blend["DBMFSIM"] == pytest.approx(0.35)
    assert blend["KMLMSIM"] == pytest.approx(0.15)
    assert np.isclose(sum(blend.values()), 1.0)
