"""Iter 033 — TDD specs for NTSX long-duration variant (0.9 SPY + 0.6 TLT).

Iter 033 reuses iter 015's stacking primitive verbatim — only the bond
ticker and educational window change. These specs lock the iter-033-
specific configuration (NOT the math, which is already covered by
``test_synth_stacked_etf.py`` from iter 015).

Citations
---------
* Hypothesis: `iterations/033-2026-04-25-0056-ntsx-tlt-long-duration/hypothesis.md`
* `[risk_parity, p.5, p.10-11, ch.1]` — risk-parity static stack.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* Koijen-Moskowitz-Pedersen-Vrugt (2018), JFE 127(2) — bond carry premium.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
ITER033_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "033-2026-04-25-0056-ntsx-tlt-long-duration"
ITER015_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "015-2026-04-24-1704-return-stacked-static-ntsx"


# ---------------------------------------------------------------------------
# Configuration invariants
# ---------------------------------------------------------------------------


def test_iter033_loads_tlt_for_all_datasets():
    """All 3 datasets must use TLT as the bond leg (not IEF, not SHV)."""
    sys.path.insert(0, str(ITER033_DIR))
    from run_backtests import DATASETS  # noqa: WPS433
    for ds_name, ds in DATASETS.items():
        assert ds["bond_symbol"] == "TLT", (
            f"iter 033 must use TLT (long-duration); {ds_name} got {ds['bond_symbol']!r}"
        )


def test_iter033_edu_window_starts_at_tlt_inception():
    """educational window must align to TLT inception (2002-07-26),
    not iter 015's IEF-aligned 2006-01-03 — 4 years longer history."""
    sys.path.insert(0, str(ITER033_DIR))
    from run_backtests import DATASETS  # noqa: WPS433
    edu = DATASETS["educational"]
    assert edu["start"] == "2002-07-26", (
        f"educational window must align to TLT inception 2002-07-26; got {edu['start']!r}"
    )


def test_iter033_preserves_iter015_weights_verbatim():
    """0.9 / 0.6 weights are NTSX-prescribed; iter 033 must not tune them."""
    sys.path.insert(0, str(ITER033_DIR))
    from run_backtests import CFG  # noqa: WPS433
    assert CFG["eq_w"] == 0.90, f"equity weight must be 0.90 verbatim; got {CFG['eq_w']}"
    assert CFG["bd_w"] == 0.60, f"bond weight must be 0.60 verbatim; got {CFG['bd_w']}"
    assert CFG["cfg_id"] == "ntsx_synth_90_60_spy_tlt", \
        f"cfg_id must encode the SPY+TLT pair; got {CFG['cfg_id']!r}"


# ---------------------------------------------------------------------------
# Engine reuse — no duplicated math
# ---------------------------------------------------------------------------


def test_iter033_imports_iter015_stacking_engine():
    """iter 033's run_backtests.py must reuse iter 015's apply_static_stack
    (single source of truth — no duplicated stacking math across iters)."""
    sys.path.insert(0, str(ITER015_DIR))
    sys.path.insert(0, str(ITER033_DIR))
    from run_backtests import apply_static_stack as iter033_func  # noqa: WPS433
    from synth_stacked_etf import apply_static_stack as iter015_func  # noqa: WPS433
    assert iter033_func is iter015_func, (
        "iter 033 must import apply_static_stack from iter 015 (not redefine it); "
        "got distinct function objects"
    )


# ---------------------------------------------------------------------------
# Cross-lib parity smoke test on real TLT data
# ---------------------------------------------------------------------------


def test_iter033_cross_lib_parity_smoke_on_real_tlt():
    """Quick pandas-vs-numpy parity check on real SPY+TLT loaded slice
    (5pp tolerance, smoke; real G7 is 3pp on full 17y windows)."""
    sys.path.insert(0, str(ITER015_DIR))
    sys.path.insert(0, str(ITER033_DIR))
    from synth_stacked_etf import apply_static_stack
    from numpy_reference_stacked import apply_static_stack_np

    tiingo_dir = ROOT / "data" / "tiingo" / "daily" / "prices"
    spy = pd.read_parquet(tiingo_dir / "SPY.parquet")["adj_close"]
    tlt = pd.read_parquet(tiingo_dir / "TLT.parquet")["adj_close"]
    p = pd.concat({"SPY": spy, "TLT": tlt}, axis=1, join="inner").dropna()
    p = p.loc["2010-01-01":"2020-12-31"]
    r = p.pct_change().dropna()
    if len(r) < 1000:
        pytest.skip("insufficient real TLT data for smoke test")

    net_pd, _, _ = apply_static_stack(r["SPY"], r["TLT"], eq_w=0.9, bd_w=0.6,
                                      cost_bps_per_leg=0.0002)
    net_np, _, _ = apply_static_stack_np(r["SPY"].to_numpy(), r["TLT"].to_numpy(),
                                         eq_w=0.9, bd_w=0.6, cost_bps_per_leg=0.0002)
    np.testing.assert_allclose(net_pd.to_numpy(), net_np, atol=1e-12)


def test_iter033_load_pair_returns_returns_tlt_column():
    """load_pair_returns must produce a DataFrame with TLT as a column."""
    sys.path.insert(0, str(ITER033_DIR))
    from run_backtests import load_pair_returns  # noqa: WPS433
    r = load_pair_returns("SPY", "TLT", "2015-01-01", "2015-06-30")
    assert "TLT" in r.columns, f"expected TLT column, got {list(r.columns)}"
    assert "SPY" in r.columns, f"expected SPY column, got {list(r.columns)}"
    assert len(r) >= 100, f"expected ≥100 bars in 6 months; got {len(r)}"
