"""Iter 010 — Three-leg vol-managed blend with inverse-variance weighting.

Generalises iter 006/008's 2-leg blend (`stock_bond_blend.py`) to N=3
legs (equity + bond + commodity). Inverse-variance weighting is the
exact equal-risk-contribution solution for diagonal Σ; when
off-diagonal cross-correlations are non-zero the weights are still the
naïve risk-parity anchor, with the full covariance matrix entering
the portfolio-level variance used by Moreira-Muir scaling.

Formulation (at each bar ``t``, using returns from ``[t-L, t-1]``):

    σ²_i = var(r_i[t-L:t]) · 252          for i ∈ {spy, tlt, gld}
    cov_ij = cov(r_i, r_j) · 252

    # Naïve risk parity weights [risk_parity, p.10-11, ch.1]:
    w_i = (1/σ²_i) / Σ_j (1/σ²_j)

    # Portfolio variance (full 3×3 matrix form):
    σ²_port = wᵀ Σ w

    # Moreira-Muir portfolio scaling:
    s_t = clip(target_vol² / σ²_port, 0, max_leverage)

    # Final leg positions:
    pos_i = s_t · w_i

    # Net returns + linear cost:
    gross = Σ_i pos_i · r_i
    cost  = Σ_i |Δpos_i| · cost_bps_per_leg
    net   = gross − cost

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity, N-asset case.
* `[risk_parity, p.80-81, ch.4]` — SPY-TLT diversification;
  SPY-TLT-GLD adds the commodity factor.
* `[systematic_trading, p.144, ch.9]` — target_vol calibration.
* `[systematic_trading, p.170-171, ch.11]` — IDM cap ≤ 2.5.
* Moreira & Muir (2017), *JoF* 72(4), 1611-1644 — portfolio-level
  variance-scaling.
* Asness, Frazzini & Pedersen (2012), *FAJ* 68(1), SSRN 1728082 —
  cross-asset risk-parity argument.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead).

The 2-leg degenerate limit (σ²_gld → ∞ so w_gld → 0) recovers iter 006
exactly modulo the 3-column cost structure.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_blend_variance_target_3leg(
    r_spy: pd.Series,
    r_tlt: pd.Series,
    r_gld: pd.Series,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Three-leg inverse-variance-weighted + Moreira-Muir portfolio scaling.

    Parameters
    ----------
    r_spy, r_tlt, r_gld : pd.Series
        Aligned daily return streams for the three legs. Must share the
        same index.
    target_vol : float
        Target annualised portfolio volatility (e.g. 0.15). ``c = target_vol²``.
    lookback : int
        Rolling window length in bars. Must be ≥ 2.
    max_leverage : float
        Upper bound on total gross exposure (``s_t``).
    periods_per_year : int
        Annualisation factor. Default 252.
    cost_bps_per_leg : float
        Cost per unit of per-leg position change. Default 0.0002 (2 bps).

    Returns
    -------
    (net_returns, positions_df, scale)
        ``net_returns`` : pd.Series of net daily returns.
        ``positions_df`` : pd.DataFrame with columns ["SPY","TLT","GLD"]
        (but the column names actually track the ``.name`` of the input
        series — normalised to these three logical slots).
        ``scale`` : pd.Series of total gross exposure (0..max_leverage).
    """
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be >= 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")
    if not r_spy.index.equals(r_tlt.index) or not r_spy.index.equals(r_gld.index):
        raise ValueError(
            "r_spy, r_tlt, r_gld must share the same index "
            f"(spy {len(r_spy)} tlt {len(r_tlt)} gld {len(r_gld)})"
        )

    a = r_spy.astype(float)
    b = r_tlt.astype(float)
    c = r_gld.astype(float)
    mask = a.notna() & b.notna() & c.notna()
    a = a.loc[mask]
    b = b.loc[mask]
    c = c.loc[mask]
    if len(a) <= lookback:
        raise ValueError(f"need > {lookback} overlapping bars, got {len(a)}")

    L = lookback
    # Rolling annualised variance per leg, lagged by 1 bar (σ̂²_{t-1}).
    ann_var_a = (a.rolling(L, min_periods=L).std(ddof=0) ** 2 * periods_per_year).shift(1)
    ann_var_b = (b.rolling(L, min_periods=L).std(ddof=0) ** 2 * periods_per_year).shift(1)
    ann_var_c = (c.rolling(L, min_periods=L).std(ddof=0) ** 2 * periods_per_year).shift(1)

    # Rolling annualised covariances (3 pairs), lagged by 1 bar.
    cov_ab = (a.rolling(L, min_periods=L).cov(b, ddof=0) * periods_per_year).shift(1)
    cov_ac = (a.rolling(L, min_periods=L).cov(c, ddof=0) * periods_per_year).shift(1)
    cov_bc = (b.rolling(L, min_periods=L).cov(c, ddof=0) * periods_per_year).shift(1)

    # Naïve risk parity weights: w_i ∝ 1/σ²_i, normalised to sum=1.
    # Handle zero-variance legs: if σ²_i == 0, treat 1/σ²_i as +∞ →
    # that leg gets 100% weight (others 0). If multiple zero → split evenly.
    idx = a.index
    w_a = pd.Series(np.nan, index=idx, dtype=float)
    w_b = pd.Series(np.nan, index=idx, dtype=float)
    w_c = pd.Series(np.nan, index=idx, dtype=float)

    va = ann_var_a.to_numpy()
    vb = ann_var_b.to_numpy()
    vc = ann_var_c.to_numpy()
    valid = ~(np.isnan(va) | np.isnan(vb) | np.isnan(vc))

    # Counts of zero-variance legs per bar (only among valid bars).
    za = (va == 0) & valid
    zb = (vb == 0) & valid
    zc = (vc == 0) & valid
    n_zero = za.astype(int) + zb.astype(int) + zc.astype(int)

    # Normal path: all three σ² > 0.
    all_pos = valid & ~(za | zb | zc)
    inv_a = np.where(all_pos, 1.0 / np.where(all_pos, va, 1.0), 0.0)
    inv_b = np.where(all_pos, 1.0 / np.where(all_pos, vb, 1.0), 0.0)
    inv_c = np.where(all_pos, 1.0 / np.where(all_pos, vc, 1.0), 0.0)
    denom = inv_a + inv_b + inv_c
    wa_arr = np.full_like(va, np.nan)
    wb_arr = np.full_like(vb, np.nan)
    wc_arr = np.full_like(vc, np.nan)
    np.putmask(wa_arr, all_pos, inv_a / np.where(denom > 0, denom, 1.0))
    np.putmask(wb_arr, all_pos, inv_b / np.where(denom > 0, denom, 1.0))
    np.putmask(wc_arr, all_pos, inv_c / np.where(denom > 0, denom, 1.0))

    # Exactly one zero: that leg gets weight 1, others 0.
    one_zero_a = valid & (n_zero == 1) & za
    one_zero_b = valid & (n_zero == 1) & zb
    one_zero_c = valid & (n_zero == 1) & zc
    np.putmask(wa_arr, one_zero_a, 1.0); np.putmask(wb_arr, one_zero_a, 0.0); np.putmask(wc_arr, one_zero_a, 0.0)
    np.putmask(wa_arr, one_zero_b, 0.0); np.putmask(wb_arr, one_zero_b, 1.0); np.putmask(wc_arr, one_zero_b, 0.0)
    np.putmask(wa_arr, one_zero_c, 0.0); np.putmask(wb_arr, one_zero_c, 0.0); np.putmask(wc_arr, one_zero_c, 1.0)

    # Two zeros: split 1/2 across the two zero-vol legs (finite-vol leg → 0).
    two_zero_ab = valid & (n_zero == 2) & za & zb
    two_zero_ac = valid & (n_zero == 2) & za & zc
    two_zero_bc = valid & (n_zero == 2) & zb & zc
    np.putmask(wa_arr, two_zero_ab, 0.5); np.putmask(wb_arr, two_zero_ab, 0.5); np.putmask(wc_arr, two_zero_ab, 0.0)
    np.putmask(wa_arr, two_zero_ac, 0.5); np.putmask(wb_arr, two_zero_ac, 0.0); np.putmask(wc_arr, two_zero_ac, 0.5)
    np.putmask(wa_arr, two_zero_bc, 0.0); np.putmask(wb_arr, two_zero_bc, 0.5); np.putmask(wc_arr, two_zero_bc, 0.5)

    # All three zero: 1/3 each.
    three_zero = valid & (n_zero == 3)
    np.putmask(wa_arr, three_zero, 1.0 / 3.0)
    np.putmask(wb_arr, three_zero, 1.0 / 3.0)
    np.putmask(wc_arr, three_zero, 1.0 / 3.0)

    w_a = pd.Series(wa_arr, index=idx)
    w_b = pd.Series(wb_arr, index=idx)
    w_c = pd.Series(wc_arr, index=idx)

    # Portfolio variance via full 3×3 quadratic form.
    # σ²_port = w² · σ² + 2 Σ_{i<j} w_i w_j cov_ij
    ann_var_port = (
        w_a ** 2 * ann_var_a
        + w_b ** 2 * ann_var_b
        + w_c ** 2 * ann_var_c
        + 2.0 * w_a * w_b * cov_ab
        + 2.0 * w_a * w_c * cov_ac
        + 2.0 * w_b * w_c * cov_bc
    )
    # Clip to zero to absorb finite-sample negatives.
    ann_var_port = ann_var_port.clip(lower=0.0)

    target_var = target_vol ** 2
    raw_scale = pd.Series(np.nan, index=idx, dtype=float)
    mask_valid = ann_var_port.notna()
    pos_mask = mask_valid & (ann_var_port > 0)
    zero_mask = mask_valid & (ann_var_port == 0)
    raw_scale.loc[pos_mask] = target_var / ann_var_port.loc[pos_mask]
    raw_scale.loc[zero_mask] = max_leverage

    scale = raw_scale.clip(lower=0.0, upper=max_leverage).dropna()
    w_a_v = w_a.loc[scale.index]
    w_b_v = w_b.loc[scale.index]
    w_c_v = w_c.loc[scale.index]
    pos_a = (scale * w_a_v).astype(float)
    pos_b = (scale * w_b_v).astype(float)
    pos_c = (scale * w_c_v).astype(float)

    a_v = a.loc[scale.index]
    b_v = b.loc[scale.index]
    c_v = c.loc[scale.index]
    gross = pos_a * a_v + pos_b * b_v + pos_c * c_v

    dpos_a = pos_a.diff().abs().fillna(pos_a.iloc[0])
    dpos_b = pos_b.diff().abs().fillna(pos_b.iloc[0])
    dpos_c = pos_c.diff().abs().fillna(pos_c.iloc[0])
    cost = (dpos_a + dpos_b + dpos_c) * cost_bps_per_leg
    net = (gross - cost).astype(float)
    net.name = "net"

    positions = pd.DataFrame({
        "SPY": pos_a.rename(None).values,
        "TLT": pos_b.rename(None).values,
        "GLD": pos_c.rename(None).values,
    }, index=scale.index)
    scale.name = "scale"
    return net, positions, scale
