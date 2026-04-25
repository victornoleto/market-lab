"""Iter 042 — Pure-numpy reference for combined regime modulation (G7 parity).

Re-exports iter 041's `apply_regime_weights_3leg_np` and `cagr_np` —
the arithmetic is identical, only the pre-committed CFG differs. The
G7 cross-library parity gate is satisfied by the *engine equivalence*
test in iter 041, propagated forward here. The TDD specs in
`tests/test_iter_042_combined_regime.py` re-validate the parity at
floating-point precision under iter 042's CFG values.
"""

from __future__ import annotations

import sys
from pathlib import Path

ITER042_DIR = Path(__file__).resolve().parent
ITER041_DIR = ITER042_DIR.parent / "041-2026-04-25-0358-regime-weights-vix-static-stack"
if str(ITER041_DIR) not in sys.path:
    sys.path.insert(0, str(ITER041_DIR))

from numpy_reference_regime_weights import (  # noqa: E402,F401
    apply_regime_weights_3leg_np,
    cagr_np,
)

__all__ = ["apply_regime_weights_3leg_np", "cagr_np"]
