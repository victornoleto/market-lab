"""Regime-conditional ON-leg basket switching helper for iter 016.

Composes iter 014's two ON-leg endpoints (single QLD/TQQQ vs
basket3-invvol QLD/UPRO/UGL) into a regime-conditional switch:

  regime_gate(t) == 1  →  single ON-leg returns at t (high CAGR)
  regime_gate(t) != 1  →  basket3-invvol ON-leg returns at t (crisis cushion)

Both internal legs share the same upgrade_gate for QLD↔TQQQ swap, so:
  - regime_gate constant 1 → reduces to iter 014 single ON-leg bit-exactly
    (Sortino_lh56y 1.3951 anchor when wired with K4_AND_lv25 + g25 + rvp70 cashx)
  - regime_gate constant 0 → reduces to iter 014 basket3-invvol ON-leg
    bit-exactly (Sortino_lh56y 1.4689 anchor when wired with same compound)

Two regime-gate primitives are provided here:

  - ``regime_gate_lowvol_pct``: 1 when realised vol_window-day vol of
    a return series is below pct_threshold of its trailing pct_window-day
    distribution (Sinclair vol cone — `[volatility_trading, p.58-60]`).
    Default (vol_window=21, pct_window=1260, pct_threshold=0.50) defines
    the "lowvol50" regime (~50% steady-state activation).

  - ``regime_gate_K4``: 1 when all 4 individual signals (SMA250, SMA100,
    vol_21d<40%, AR(1)_30d>0) fire simultaneously — Clenow trend
    conviction (`[stocks_on_the_move, p.98]`). Lower steady-state
    activation (~20-25% per iter 011 stats).

The regime gate is applied lagged 1 day (no look-ahead, matches iter 011
conditional-leg convention).

Citations
---------
- [risk_parity, p.80-81, ch.4]: Qian RORO regime-conditional master-gate
  (PRIMARY for the iter — switch composition between two endpoints based
  on regime indicator instead of static weight-averaging).
- [risk_parity, p.110, ch.5]: Qian fixed-weight diversification return
  (frames dynamic switch as a strict generalisation of static eqtilt).
- [volatility_trading, p.58-60]: Sinclair vol cone (lowvol50 regime).
- [stocks_on_the_move, p.98]: Clenow trend-strength (K=4 vote regime).
- [advances_fin_ml, p.208-211]: PBO via CSCV (mechanism-mix-diversity).

Iter-local helper (`loop_iterations/016-.../`); does NOT modify shared
modules per LOOP_PROTOCOL §"Scope limits".
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Regime gates
# ---------------------------------------------------------------------------


def regime_gate_lowvol_pct(
    returns: pd.Series,
    vol_window: int = 21,
    pct_window: int = 1260,
    pct_threshold: float = 0.50,
) -> pd.Series:
    """Regime gate: 1 when realised vol is below pct_threshold of trailing
    pct_window distribution; 0 otherwise; NaN during warmup.

    `[volatility_trading, p.58-60]` Sinclair vol cone — low realised-vol
    percentile regimes are statistically distinct from high-vol regimes
    (mean-reversion vs trend-continuation behavior). The threshold 0.50
    splits the trailing distribution into two equal-mass regimes by
    construction.

    Parameters
    ----------
    returns:
        Daily simple returns of the underlying (e.g., QLD return).
    vol_window:
        Rolling sigma window in days. Default 21 (matches the lowvol25
        upgrade gate from iter 011 — same raw vol input, different threshold).
    pct_window:
        Trailing distribution window. Default 1260 (5y).
    pct_threshold:
        Percentile bound; gate fires when current vol < this percentile.
        Default 0.50 (lowvol50 regime).

    Returns
    -------
    pd.Series
        {0, 1, NaN}. NaN during warmup (vol_window + pct_window - 1 bars).
    """
    sigma = returns.rolling(vol_window, min_periods=vol_window).std() * np.sqrt(252.0)
    pct_rank = sigma.rolling(pct_window, min_periods=pct_window).rank(pct=True)
    gate = (pct_rank < pct_threshold).astype(float)
    gate[pct_rank.isna()] = np.nan
    return gate


def regime_gate_K4(individual_signals: list[pd.Series]) -> pd.Series:
    """Regime gate: 1 when ALL 4 individual signals fire (K=4 of 4).

    Same primitive as ``ITER011.upgrade_signal_K4`` (which calls
    ``vote_of_k(individual_signals, k=4)`` on the iter 022 winner's 4
    signals: SMA250, SMA100, vol_21d<40%, AR(1)_30d>0). Re-exposed here
    as a regime gate for clarity; arithmetic is identical.

    Parameters
    ----------
    individual_signals:
        List of 4 binary {0, 1, NaN} signals from
        ``ITER011._individual_signals(prices, returns)``.

    Returns
    -------
    pd.Series
        {0, 1, NaN}. NaN during warmup (max SMA period = 250 days).
    """
    from studies.letf_rotation_hunt.signals import vote_of_k
    return vote_of_k(individual_signals, k=4)


# ---------------------------------------------------------------------------
# Regime-switch ON-leg
# ---------------------------------------------------------------------------


def build_regime_switch_on_leg(
    single_on_leg: pd.Series,
    basket_on_leg: pd.Series,
    regime_gate: pd.Series,
) -> pd.Series:
    """Day-by-day select between single and basket ON-leg returns by regime.

    Behaviour (regime gate is lagged 1 day inside this function, so the
    caller passes the raw daily gate):

      regime_gate(t-1) == 1   → single_on_leg(t)
      regime_gate(t-1) != 1   → basket_on_leg(t)
      regime_gate(t-1) is NaN → basket_on_leg(t)  (defensive default during
                                                   regime warmup)

    Where single_on_leg(t) is NaN but basket_on_leg(t) is not (e.g. very
    early lh_56y window if single ever has a NaN row), we fall back to the
    basket leg. Where basket_on_leg(t) is NaN (pre-1985 basket3 inception),
    we fall back to single_on_leg. Index = union of valid rows from either
    leg, restricted to the regime-gate index.

    Edge equivalences (verified by KILL_LOOP replica anchors):
      - regime_gate constant 1 (always single) → returns ≡ single_on_leg
        on the index where single_on_leg is non-NaN. Used by iter 014's
        single K4lv25_g25_rvp70_cashx replica (slot 2).
      - regime_gate constant 0 (always basket) → returns ≡ basket_on_leg
        on the index where basket_on_leg is non-NaN. Used by iter 014's
        triple-stack basket3 K4lv25_g25_rvp70_cashx replica (slot 3).

    Parameters
    ----------
    single_on_leg:
        Output of ``ITER014.build_single_asset_on_leg`` (QLD/TQQQ swap).
    basket_on_leg:
        Output of ``ITER014.build_basket3_on_leg`` (QLD/UPRO/UGL invvol60
        with QLD/TQQQ swap).
    regime_gate:
        {0, 1, NaN} daily series. Will be shifted 1 day internally.

    Returns
    -------
    pd.Series
        Daily ON-leg return aligned to union(single, basket) index, then
        restricted to the regime-gate index. NaN rows dropped.
    """
    rg_lag = regime_gate.shift(1)
    aligned = pd.concat({
        "s": single_on_leg,
        "b": basket_on_leg,
        "r": rg_lag,
    }, axis=1)
    # Need at least one valid leg to produce output.
    aligned = aligned.dropna(subset=["s", "b"], how="all")

    use_single = (aligned["r"].fillna(0.0) == 1.0)
    out = pd.Series(np.nan, index=aligned.index)

    # Default: basket; fallback to single where basket is NaN.
    basket_valid = aligned["b"].notna()
    single_valid = aligned["s"].notna()

    out[basket_valid] = aligned.loc[basket_valid, "b"]
    fallback_to_single = (~basket_valid) & single_valid
    out[fallback_to_single] = aligned.loc[fallback_to_single, "s"]

    swap_to_single = use_single & single_valid
    out[swap_to_single] = aligned.loc[swap_to_single, "s"]

    return out.dropna()


def regime_switch_activation_pct(
    regime_gate: pd.Series,
    single_on_leg: pd.Series,
    basket_on_leg: pd.Series,
) -> dict:
    """Diagnostic: % of valid days the regime gate routes to single vs basket.

    Useful to verify the steady-state activation rate (lowvol50 ≈ 50%,
    K4 ≈ 20-25%) and confirm the regime gate is doing what we expect.

    Returns
    -------
    dict with keys:
      - "n_total_days": int
      - "n_single_days": int
      - "n_basket_days": int
      - "single_pct": float
      - "basket_pct": float
    """
    rg_lag = regime_gate.shift(1)
    aligned = pd.concat({
        "s": single_on_leg,
        "b": basket_on_leg,
        "r": rg_lag,
    }, axis=1).dropna(subset=["s", "b"], how="all")
    use_single = (aligned["r"].fillna(0.0) == 1.0) & aligned["s"].notna()
    use_basket = (~use_single) & aligned["b"].notna()
    n_total = int(use_single.sum() + use_basket.sum())
    if n_total == 0:
        return {"n_total_days": 0, "n_single_days": 0, "n_basket_days": 0,
                "single_pct": 0.0, "basket_pct": 0.0}
    n_single = int(use_single.sum())
    n_basket = int(use_basket.sum())
    return {
        "n_total_days": n_total,
        "n_single_days": n_single,
        "n_basket_days": n_basket,
        "single_pct": float(n_single) / n_total,
        "basket_pct": float(n_basket) / n_total,
    }
