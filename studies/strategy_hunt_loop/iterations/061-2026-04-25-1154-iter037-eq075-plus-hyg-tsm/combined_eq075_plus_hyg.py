"""Iter 061 — Convex combo of equity-overweight 3-leg stream + HYG TSM.

Structurally identical to iter 058/059's combiner — only the source
streams change. The eq075 stream is built fresh each call from the
SPY/IEF/GLD (or QQQ/IEF/GLD) returns via
``synth_stacked_etf_3leg_eq075.apply_static_stack_3leg`` with weights
0.75 / 0.40 / 0.40 (total 1.55×). The HYG TSM stream is computed via
``hyg_tsm.compute_hyg_tsm_returns`` with iter 058/059's vendored
defaults (lookback=90, rf=0.02, cost_bps=5.0).

Citations
---------
* `[risk_parity, ch.5]` — multi-leg risk-parity (eq075 base).
* Asvanunt-Richardson 2017 JPM 43(2) DOI 10.3905/jpm.2017.43.2.090 —
  credit risk premium third-stream rationale.
* Markowitz (1952) JoF 7(1) — closed-form Sharpe identity.
* `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials.
"""

from __future__ import annotations

import pandas as pd


def combine_eq075_plus_hyg(
    r_eq075: pd.Series,
    r_hyg: pd.Series,
    *,
    w_eq075: float = 0.9,
    w_hyg: float = 0.1,
) -> pd.Series:
    """Convex combo of equity-overweight 3-leg stream and HYG TSM.

    Parameters
    ----------
    r_eq075 : pd.Series
        Daily net returns of the 0.75/0.40/0.40 SPY+IEF+GLD (or
        QQQ+IEF+GLD) static stack from
        ``synth_stacked_etf_3leg_eq075.apply_static_stack_3leg``.
    r_hyg : pd.Series
        HYG TSM daily net returns from
        ``hyg_tsm.compute_hyg_tsm_returns``.
    w_eq075, w_hyg : float, default 0.9 / 0.1
        Convex combination weights. Each must be ≥ 0; their sum
        is not enforced to 1 (caller may pass non-normalised weights
        for sensitivity runs, mirroring iter 058/059).

    Returns
    -------
    pd.Series
        Combined daily net returns indexed on the inner-join of the
        two input series.

    Raises
    ------
    ValueError
        If w_eq075 < 0 or w_hyg < 0 or both are 0, or if the two
        return series have < 2 overlapping bars.
    """
    if w_eq075 < 0:
        raise ValueError(f"w_eq075 must be >= 0; got {w_eq075}")
    if w_hyg < 0:
        raise ValueError(f"w_hyg must be >= 0; got {w_hyg}")
    if (w_eq075 + w_hyg) <= 0:
        raise ValueError(
            f"w_eq075 + w_hyg must be > 0; got {w_eq075 + w_hyg}"
        )

    common = r_eq075.index.intersection(r_hyg.index)
    if len(common) < 2:
        raise ValueError(
            f"r_eq075 and r_hyg have <2 overlapping bars "
            f"(eq075={len(r_eq075)}, hyg={len(r_hyg)})"
        )
    a = r_eq075.loc[common]
    b = r_hyg.loc[common]
    combined = w_eq075 * a + w_hyg * b
    combined.name = "combined_eq075_plus_hyg"
    return combined
