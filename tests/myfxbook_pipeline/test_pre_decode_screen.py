"""Unit tests for shared.pre_decode_screen (task 002).

Goldens (real systems on disk):
- 10281851 (Real, 652 trades, OVERLAP_NY_LONDON_RANGE, sanity OK) → GO
- 11504701 (Real, 314 trades, MARTINGALE_GRID, sanity FAIL) → STOP
- 1407880  (Demo, 3304 trades, LATE_NY_BREAKOUT, sanity OK) → GO with is_live=False

Citations:
- MCPT determinism: `[evidence_based_ta, p.325-328]` — same seed, same p-value
- PSR M=1: `[advances_fin_ml, p.260-263]` — track record p-value
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from studies.myfxbook_reverse_engineering.shared import pre_decode_screen as pds
from studies.myfxbook_reverse_engineering.shared import config

GOLDEN_PASS_REAL = "10281851"
GOLDEN_STOP_MARTINGALE = "11504701"
GOLDEN_DEMO_WARNING = "1407880"

# Smaller permutation count keeps the test fast; the real-system MCPT p-values
# come out at ~0.002 with 500 perms, well under the 0.05 threshold, so this
# does not affect the pass/fail outcome.
N_PERM_TEST = 500


def _golden_available(system_id: str) -> bool:
    return config.trades_parquet_path(system_id).exists() and config.system_info_json_path(system_id).exists()


@pytest.mark.skipif(not _golden_available(GOLDEN_PASS_REAL), reason=f"golden {GOLDEN_PASS_REAL} artifacts missing")
def test_golden_pass_real() -> None:
    r = pds.screen_system(GOLDEN_PASS_REAL, n_permutations=N_PERM_TEST)
    assert r.system_id == GOLDEN_PASS_REAL
    assert r.decision == "GO"
    assert r.k1_sanity_pass is True
    assert r.is_live is True
    assert r.mcpt_p < pds.MCPT_THRESHOLD
    assert r.psr_p < pds.PSR_THRESHOLD
    assert r.concentration_top5 < pds.CONCENTRATION_TOP5_THRESHOLD
    assert r.n_trades == 652


@pytest.mark.skipif(not _golden_available(GOLDEN_STOP_MARTINGALE), reason=f"golden {GOLDEN_STOP_MARTINGALE} artifacts missing")
def test_golden_stop_martingale() -> None:
    r = pds.screen_system(GOLDEN_STOP_MARTINGALE, n_permutations=N_PERM_TEST)
    assert r.decision == "STOP"
    assert r.k1_sanity_pass is False, "11504701 should trip K1 (MARTINGALE_GRID)"
    assert any("K1 sanity FAIL" in note for note in r.notes)


@pytest.mark.skipif(not _golden_available(GOLDEN_DEMO_WARNING), reason=f"golden {GOLDEN_DEMO_WARNING} artifacts missing")
def test_golden_demo_warning_only() -> None:
    """Demo accounts must NOT block decision='GO' — is_live is warning-only.

    DEAD_ENDS.md "is_live como hard gate (rejeitado em review GPT-5.5)" —
    blocking would discard 47/52 candidate systems arbitrarily.
    """
    r = pds.screen_system(GOLDEN_DEMO_WARNING, n_permutations=N_PERM_TEST)
    assert r.is_live is False, "1407880 is a Demo account"
    assert r.decision == "GO", "Demo flag must not block GO when other gates pass"
    assert r.k1_sanity_pass is True
    assert any("is_live=False" in note for note in r.notes)


def test_concentration_high_synthetic(tmp_path: Path) -> None:
    """Synthetic series where 5% of trades carry ~80% of |PnL| → STOP."""
    n = 200
    base = np.full(n, 1.0)
    # top 10 (5%) trades each carry ~40 pips of |return| → ~80% of total |PnL|
    base[-10:] = 40.0
    # spread 50/50 winners vs losers in the heavy bucket so PSR/MCPT also flag
    base[-5:] *= -1
    df = pd.DataFrame(
        {
            "is_trade": [True] * n,
            "pips": base,
            "lots": [0.10] * n,
            "open_dt_utc": pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC"),
            "close_dt_utc": pd.date_range("2024-01-01 00:30", periods=n, freq="1h", tz="UTC"),
            "duration_sec": [1800] * n,
            "is_deposit": [False] * n,
            "symbol": ["EURUSD"] * n,
            "action": ["Buy"] * n,
        }
    )
    r = pds.screen_system(
        "synthetic-conc",
        n_permutations=N_PERM_TEST,
        trades_df=df,
        account_type="Real",
    )
    assert r.concentration_top5 >= pds.CONCENTRATION_TOP5_THRESHOLD
    assert r.decision == "STOP"
    assert any("concentration top-5%" in note for note in r.notes)


def test_mcpt_determinism() -> None:
    """Same seed → same p-value (the MCPT must be reproducible).

    Use a weak signal (mean barely > 0) so different seeds actually disagree
    on the count of permuted Sharpes >= observed; with a strong signal
    almost every seed lands at the floor (count_better=0) and the test
    becomes trivial.
    """
    rng = np.random.default_rng(42)
    returns = rng.normal(loc=0.05, scale=1.0, size=200)
    p1 = pds._mcpt_p_value(returns, n_permutations=N_PERM_TEST, seed=20260503)
    p2 = pds._mcpt_p_value(returns, n_permutations=N_PERM_TEST, seed=20260503)
    p3 = pds._mcpt_p_value(returns, n_permutations=N_PERM_TEST, seed=20260504)
    assert p1 == p2
    assert p1 != p3, "different seeds should produce different p-values"
