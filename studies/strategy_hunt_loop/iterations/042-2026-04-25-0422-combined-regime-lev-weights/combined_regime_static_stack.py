"""Iter 042 — Combined regime modulation (leverage × weights) on iter 037 stack.

The arithmetic is **identical** to iter 041's
``apply_regime_weights_3leg`` (composition shift across a binary VIX-
regime gate with 1-day lag). What changes is the pre-committed CFG:
each regime's weight tuple is rescaled so that *total leverage* in
calm is **1.700×** (matching iter 038's lev_lo) and in stress is
**1.000×** (matching iter 038's lev_hi). The relative composition
within each regime — `eq:bd:gld` ratios — is preserved verbatim from
iter 041:

* calm   ≈ (0.467, 0.267, 0.267) · 1.700 = (0.79333, 0.45333, 0.45333)
* stress ≈ (0.214, 0.393, 0.393) · 1.000 = (0.21429, 0.39286, 0.39286)

This is a *parameter-level* superposition of two pre-existing positive
results — iter 041 (composition modulation) + iter 038 (leverage
modulation) — along orthogonal axes. The engine is unchanged; the
hypothesis is that the orthogonal axes compound DSR uplift.

Citations
---------
* `[risk_parity, ch.5]` — dual-axis regime modulation of risk-parity stack.
* `[advances_fin_ml, ch.17-18, p.162-164]` — regime detection + lag rule.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
* Whaley (2009) JPM 35(3); Bekaert-Hoerova (2014) J Econometrics 183(2).
* Erb-Harvey (2006) FAJ 62(2); Asness-Moskowitz-Pedersen (2013) JF 68(3).
"""

from __future__ import annotations

import sys
from pathlib import Path

ITER042_DIR = Path(__file__).resolve().parent
ITER041_DIR = ITER042_DIR.parent / "041-2026-04-25-0358-regime-weights-vix-static-stack"
if str(ITER041_DIR) not in sys.path:
    sys.path.insert(0, str(ITER041_DIR))

from regime_weights_static_stack import apply_regime_weights_3leg  # noqa: E402,F401

__all__ = ["apply_regime_weights_3leg"]
