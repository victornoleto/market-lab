"""Capital-efficient proxy synthesizers (NTSX / NTSI / NTSE family).

Centralizes the WisdomTree "Efficient Core" capital-efficient stacking
formula so every iteration of the long-term portfolio loop expands the
same legs the same way.

The three sister ETFs (NTSX US, NTSI intl-developed, NTSE EM) share the
same prospectus-level architecture: 90% spot equity + 60% Treasury bond
futures overlay − 50% financing leg, for 1.5× notional exposure with
zero retail margin requirement.

Synth formula (all three identical, equity sleeve swapped):

    NTSX = 0.90 SPYSIM + 0.60 IEFSIM − 0.50 CASHX
    NTSI = 0.90 VEASIM + 0.60 IEFSIM − 0.50 CASHX
    NTSE = 0.90 VWOSIM + 0.60 IEFSIM − 0.50 CASHX

NTSX coefficients were validated 2026-04-26 in `deploy_studies/` against
live NTSX (2018-09 → 2026-04) — daily-return correlation > 0.99 and
Sharpe within ±0.02 of live ETF. NTSI/NTSE assume the same coefficients
because the WisdomTree prospectus uses the identical 90/60/−50 blueprint
across the family (only the equity index differs).

Effective testfolio data ranges (`testfolio_loader`, 2026-04-28):

| proxy | bottleneck | start date  | iter eff window |
|-------|------------|-------------|-----------------|
| NTSX  | SPYSIM     | 1986-01-02  | 1986+ (40y eff) |
| NTSI  | VEASIM     | 1969-12-31  | 1970+ (full lh_56y) |
| NTSE  | VWOSIM     | 1994-05-04  | 1994+ (~32y eff) |

NTSE bottlenecks at 1994 because MSCI EM index inception was 1987 and
testfolio's testfolio-style backfill only goes back to ~1994. Iter 015
mixes 4-asset (no NTSE, full lh_56y) and 5-asset (with NTSE, 32y eff)
configs to preserve apples-to-apples comparison with iter 011.

Citations:
- Capital-efficient stacking architecture: [risk_parity, ch.5, p.10]
- WisdomTree Efficient Core ETF prospectus 2024 (90/60/−50 blueprint)
"""

from __future__ import annotations


# Single source of truth for the WisdomTree-style 90/60/−50 stack.
# Iterations should call expand_capital_efficient(weights) rather than
# inlining the formula, so any future correction propagates everywhere.
PROXY_LEGS: dict[str, dict[str, float]] = {
    "NTSX_PROXY": {"SPYSIM": 0.90, "IEFSIM": 0.60, "CASHX": -0.50},
    "NTSI_PROXY": {"VEASIM": 0.90, "IEFSIM": 0.60, "CASHX": -0.50},
    "NTSE_PROXY": {"VWOSIM": 0.90, "IEFSIM": 0.60, "CASHX": -0.50},
}


def expand_capital_efficient(weights: dict[str, float]) -> dict[str, float]:
    """Expand any NTSX/NTSI/NTSE proxy into its testfolio legs.

    Tickers not in PROXY_LEGS pass through unchanged (so callers can mix
    proxies with raw testfolio columns like GDESIM, KMLMSIM, VXUSSIM).

    Returns a new dict with summed leg weights.
    """
    out: dict[str, float] = {}
    for ticker, weight in weights.items():
        if ticker in PROXY_LEGS:
            for leg, coef in PROXY_LEGS[ticker].items():
                out[leg] = out.get(leg, 0.0) + coef * weight
        else:
            out[ticker] = out.get(ticker, 0.0) + weight
    return out
