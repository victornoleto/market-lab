"""G7 cross-lib reference — pure-numpy asymmetric overlay.

Independent numpy re-implementation of
``asymmetric_term_spread_overlay.apply_blend_with_asymmetric_overlay``
for cross-library CAGR parity check per
`[advances_fin_ml, p.31-34]`.

Reuses iter 006's ``apply_blend_variance_target_np`` as the un-gated
base so only the asymmetric gate application is newly hand-rolled.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ITER006_DIR = Path(__file__).resolve().parent.parent / "006-2026-04-24-1027-vol-managed-60-40"
sys.path.insert(0, str(ITER006_DIR))

from numpy_reference import (  # noqa: E402
    apply_blend_variance_target_np,
    cagr_np,
    max_drawdown_np,
    sharpe_np,
)


def ema_np(x: np.ndarray, span: int) -> np.ndarray:
    """EMA with ``adjust=False`` semantics matching pandas ewm."""
    x = np.asarray(x, dtype=float)
    alpha = 2.0 / (span + 1.0)
    out = np.full_like(x, np.nan)
    for i, v in enumerate(x):
        if np.isnan(v):
            if i > 0 and not np.isnan(out[i - 1]):
                out[i] = out[i - 1]
            continue
        if i == 0 or np.isnan(out[i - 1]):
            out[i] = v
        else:
            out[i] = alpha * v + (1.0 - alpha) * out[i - 1]
    return out


def apply_blend_with_asymmetric_overlay_np(
    r_spy: np.ndarray,
    r_tlt: np.ndarray,
    term_spread_raw: np.ndarray,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    smoothing_window: int,
    threshold: float,
    haircut: float,
    lag_bars: int = 1,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pure-numpy reference for blend + asymmetric (equity-only) overlay.

    Parameters
    ----------
    r_spy, r_tlt : np.ndarray
        Daily return streams, aligned on the equity calendar.
    term_spread_raw : np.ndarray
        T10Y3M values aligned onto the SAME equity calendar as
        ``r_spy``/``r_tlt`` (caller ffilled over holidays).

    Returns
    -------
    (net, pos_spy_gated, pos_tlt_ungated, scale, gate) — all of length
    ``n - lookback``.
    """
    r_spy = np.asarray(r_spy, dtype=float)
    r_tlt = np.asarray(r_tlt, dtype=float)
    term_spread_raw = np.asarray(term_spread_raw, dtype=float)
    if not (r_spy.shape == r_tlt.shape == term_spread_raw.shape):
        raise ValueError(
            f"shape mismatch: r_spy={r_spy.shape} r_tlt={r_tlt.shape} "
            f"ts={term_spread_raw.shape}"
        )

    # Lag raw signal, then EMA-smooth (order must match pandas path).
    ts_lagged = np.concatenate(
        [np.full(lag_bars, np.nan), term_spread_raw[:-lag_bars]]
    )
    ts_ema = ema_np(ts_lagged, span=smoothing_window)

    # Un-gated blend (iter 006 numpy reference).
    _, pos_spy_base, pos_tlt_base, scale = apply_blend_variance_target_np(
        r_spy, r_tlt,
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,
    )

    n_full = len(r_spy)
    valid_start = n_full - len(scale)
    ts_valid = ts_ema[valid_start:]

    gate = np.ones_like(scale)
    mask_haircut = (~np.isnan(ts_valid)) & (ts_valid <= threshold)
    gate[mask_haircut] = haircut

    # ASYMMETRIC: haircut only on SPY leg.
    pos_spy_g = pos_spy_base * gate
    pos_tlt_g = pos_tlt_base  # no haircut on bond leg

    a_v = r_spy[valid_start:]
    b_v = r_tlt[valid_start:]
    gross = pos_spy_g * a_v + pos_tlt_g * b_v

    dpos_spy = np.empty_like(pos_spy_g)
    dpos_tlt = np.empty_like(pos_tlt_g)
    dpos_spy[0] = abs(pos_spy_g[0])
    dpos_tlt[0] = abs(pos_tlt_g[0])
    dpos_spy[1:] = np.abs(np.diff(pos_spy_g))
    dpos_tlt[1:] = np.abs(np.diff(pos_tlt_g))
    cost = (dpos_spy + dpos_tlt) * cost_bps_per_leg
    net = gross - cost

    return net, pos_spy_g, pos_tlt_g, scale, gate


__all__ = [
    "apply_blend_with_asymmetric_overlay_np",
    "ema_np",
    "cagr_np",
    "sharpe_np",
    "max_drawdown_np",
]
