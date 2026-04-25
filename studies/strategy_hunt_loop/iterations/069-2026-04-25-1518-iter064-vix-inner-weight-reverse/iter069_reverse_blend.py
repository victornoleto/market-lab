"""Iter 069 — REVERSE VIX-conditional INNER weight swap on iter 064 sub-streams.

Mechanism (engine bit-identical to iter 068; ONLY weight defaults flip)
----------------------------------------------------------------------

iter 068 tested the canonical "calm-trend, stress-defensive" direction:
``w_qqqt_calm = 0.20``, ``w_qqqt_stress = 0.05``. Score 79 STRONG;
KILL I fired with 3/3 datasets showing QQQ_TREND Sharpe(stress) >
Sharpe(calm) — the directional intuition was empirically falsified.

iter 069 directly tests the REVERSE direction:
``w_qqqt_calm = 0.05``, ``w_qqqt_stress = 0.20``. Same combiner, same
shift(1) VIX no-look-ahead, same flip-cost convention, same total-
exposure invariant ≡ 1.0, same Whaley 2009 threshold = 20. The ONLY
change is the directional assignment of weights to regimes. The
engine is therefore *bit-identical* (we re-export iter 068's combiner
without modification) — any score delta vs iter 068 is purely due to
the directional flip.

Predicted result (per iter 068 final report)
--------------------------------------------

If iter 068's per-stream conditional-Sharpe finding (KILL I) generalises
to the BLENDED return path with realistic flip costs and OOS bars,
iter 069 should lift Sharpe by +0.04 to +0.07 vs iter 064 → potential
break into the 85-90 STRONG band. If the ordering is sample-dependent
(KILL I on iter 069 fires in the OPPOSITE direction), the inner-weight-
swap axis closes BOTH directions and iter 070 must pivot to a
structurally novel anchor / regime / cadence.

Citations (preserved from iter 068; iter 069 adds iter 068 as data point)
-------------------------------------------------------------------------

* `[stocks_on_the_move, p.21-30]` — Clenow regime-conditional momentum.
* Faber (2007) SSRN 962461 — single-asset 200d SMA TAA.
* `[risk_parity, ch.5]` — iter 046 base preserved.
* `[volatility_trading, p.218]` — Sinclair σ⁻² scaling.
* Whaley (2009) JPM 35(3): VIX threshold 20.
* Bekaert & Hoerova (2014) — VIX uncertainty/risk-aversion.
* Moskowitz, Ooi & Pedersen (2012) — TSM regime conditionality.
* `[advances_fin_ml, p.162-164]` — strict shift(1) on VIX.
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, ch.17-18]` — regime detection.
* `[systematic_trading, ch.11]` — Carver IDM ≤ 2.5.
* iter 068 final report — empirical conditional-Sharpe ordering KILL I.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Re-export iter 068's combiner verbatim — bit-identical engine.
ITER_068_DIR = Path(__file__).resolve().parents[1] / \
    "068-2026-04-25-1758-iter064-vix-inner-weight-swap"
if str(ITER_068_DIR) not in sys.path:
    sys.path.insert(0, str(ITER_068_DIR))

from vix_inner_weight import combine_with_vix_inner_weight  # noqa: E402


def combine_reverse(
    r_046: pd.Series,
    r_qqqt: pd.Series,
    vix: pd.Series,
    *,
    w_qqqt_calm: float = 0.05,
    w_qqqt_stress: float = 0.20,
    vix_threshold: float = 20.0,
    cost_bps: float = 5.0,
    return_diagnostics: bool = False,
) -> pd.Series:
    """Reverse-direction VIX-conditional inner-weight blend.

    Parameters
    ----------
    r_046 : pd.Series
        Iter 046 daily net combined returns (saved in iter 046's
        ``returns_series``).
    r_qqqt : pd.Series
        Faber 2007 200d-SMA QQQ-trend daily net returns (computed via
        ``iter064.qqq_trend.compute_qqq_trend_returns``).
    vix : pd.Series
        VIX series; reindexed to combined.index with ffill().bfill().
    w_qqqt_calm : float, default 0.05
        QQQ_TREND weight when VIX[t-1] < ``vix_threshold`` (calm regime).
        REVERSED from iter 068's 0.20.
    w_qqqt_stress : float, default 0.20
        QQQ_TREND weight when VIX[t-1] >= ``vix_threshold`` (stress).
        REVERSED from iter 068's 0.05.
    vix_threshold : float, default 20.0
        Whaley 2009 long-run median.
    cost_bps : float, default 5.0
        Bps charged on bar of flip per |Δw_qqqt|.
    return_diagnostics : bool, default False
        Attach intermediate arrays in ``out.attrs["diagnostics"]``.

    Returns
    -------
    pd.Series
        Daily net returns indexed on inner-join of ``r_046`` and
        ``r_qqqt``, named ``iter069_vix_inner_reverse``.
    """
    out = combine_with_vix_inner_weight(
        r_046, r_qqqt, vix,
        w_qqqt_calm=w_qqqt_calm,
        w_qqqt_stress=w_qqqt_stress,
        vix_threshold=vix_threshold,
        cost_bps=cost_bps,
        return_diagnostics=return_diagnostics,
    )
    out.name = "iter069_vix_inner_reverse"
    return out
