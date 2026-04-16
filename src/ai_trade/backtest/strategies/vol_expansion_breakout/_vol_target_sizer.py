"""Carver volatility-targeting sizer [systematic_trading, p.144, p.159, ch.9-10]."""
from __future__ import annotations

import logging

logger = logging.getLogger("ai_trade.strategy.vol_expansion.sizer")

SIGMA_FLOOR = 1e-6


class VolTargetSizer:
    """Size a position so that its annualised P&L volatility matches target_vol_annual.

    Formula [systematic_trading, p.144, p.159]:
        notional = target_vol_annual * equity / sigma_yz_annual
        shares   = notional / entry_price

    Guard rails:
    - sigma_yz_annual below SIGMA_FLOOR → log WARNING, return (0, 0).
    - entry_price or equity <= 0 → return (0, 0).
    """

    def __init__(self, target_vol_annual: float) -> None:
        if not 0.0 < target_vol_annual < 1.0:
            raise ValueError("target_vol_annual must be in (0, 1)")
        self.target_vol_annual = target_vol_annual

    def size(
        self,
        equity: float,
        sigma_yz_annual: float,
        entry_price: float,
    ) -> tuple[float, float]:
        """Return (notional, shares) for a new position.

        Parameters
        ----------
        equity:           Current portfolio equity in account currency.
        sigma_yz_annual:  Yang-Zhang annualised vol of the instrument (fraction, e.g. 0.20).
        entry_price:      Entry price of the instrument in account currency.
        """
        if sigma_yz_annual < SIGMA_FLOOR:
            logger.warning(
                "sigma_yz_annual=%.3e below floor %.0e — sizing to 0",
                sigma_yz_annual,
                SIGMA_FLOOR,
            )
            return 0.0, 0.0
        if entry_price <= 0 or equity <= 0:
            return 0.0, 0.0
        notional = self.target_vol_annual * equity / sigma_yz_annual
        shares = notional / entry_price
        return notional, shares
