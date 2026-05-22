"""Binary regime rotation simulator (no tax, no costs).

Given a daily ``"ON"``/``"OFF"`` regime signal and a target asset's daily
returns, produce the strategy's daily returns assuming we hold the on-leg
when ``signal == "ON"`` and an off-leg (cash by default, or another
asset's returns) otherwise.

Execution convention: signal observed at close of day ``T`` → exposure on
``T+1``. The shift is applied inside this function so callers pass the
raw signal series (e.g. straight from
:func:`market_lab.backtest.strategies.letf_rotation.compute_regime_signal`).

Citations
---------
* Next-bar execution (no lookahead): ``[leverage_for_the_long_run, p.13]``
  describes daily close-to-close decisions on the SPX signal.
* Cash (not BIL) for RISK_OFF: ``[leverage_for_the_long_run, p.21]``.
  Phase-1 widens this to test gold / IEF / ZROZ as off-leg alternatives.
"""
from __future__ import annotations

import pandas as pd


def binary_rotation(
    signal: pd.Series,
    asset_returns: pd.Series,
    *,
    off_leg_returns: pd.Series | None = None,
) -> pd.Series:
    """Return the strategy's per-day returns for a 2-state rotation.

    Parameters
    ----------
    signal : pd.Series
        Object-dtype series with values in ``{"ON", "OFF", NaN}``. NaN is
        treated as ``"OFF"`` (warmup). Indexed by date.
    asset_returns : pd.Series
        Daily returns of the on-leg asset (e.g. SSO returns for an
        LRS-SSO strategy). Indexed by date.
    off_leg_returns : pd.Series, optional
        Daily returns of the off-leg asset (e.g. GLD returns for a
        rotation that exits SSO into gold). ``None`` (default) means
        literal cash with 0% yield.

    Returns
    -------
    pd.Series
        Daily strategy returns, indexed by the intersection of all input
        series' dates. First bar is effectively the off-leg return (or 0
        if cash) because the first signal isn't yet shifted in.
    """
    common = signal.index.intersection(asset_returns.index)
    if off_leg_returns is not None:
        common = common.intersection(off_leg_returns.index)
    sig = signal.reindex(common)
    on_ret = asset_returns.reindex(common).astype(float)
    exposed = sig.shift(1).eq("ON")
    if off_leg_returns is None:
        return on_ret.where(exposed, 0.0)
    off_ret = off_leg_returns.reindex(common).astype(float)
    return on_ret.where(exposed, off_ret)


def exposure_from_signal(signal: pd.Series) -> pd.Series:
    """Boolean exposure series derived from ``signal`` (T-close → T+1 exposure).

    Useful for tax-aware simulators that need to detect ``OFF→ON`` /
    ``ON→OFF`` transitions on the exposure timeline (not the signal one).
    """
    return signal.shift(1).eq("ON")
