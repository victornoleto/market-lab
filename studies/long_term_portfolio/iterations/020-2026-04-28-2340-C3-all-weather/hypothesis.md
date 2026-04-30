# Iter 020 — Hypothesis: C.3 — All-Weather Bridgewater-mimic (4 variants)

## Hypothesis

Bridgewater's All-Weather portfolio is designed for risk parity across 4
economic regimes (growth↑/↓ × inflation↑/↓). Test 4 variants of the
All-Weather family in this universe (DBC commodities unavailable in
testfolio → gold sub):

| config | recipe | citation |
|---|---|---|
| `aw_textbook_30_40_15_15` | 30% SPY + 40% TLT + 15% IEF + 15% GLD | Bridgewater 2009 white paper (gold sub for commodities) |
| `aw_browne_25252525` | 25% SPY + 25% TLT + 25% GLD + 25% CASH | Harry Browne *Fail-Safe Investing* (1999) |
| `aw_levered_NTSX_GDE_TLT` | 40% NTSX + 30% GDE + 15% KMLM + 15% TLT | iter 011 family + extra LT-bond sleeve |
| `aw_inv_vol_4asset` | inverse-60d-vol weighted SPY/TLT/IEF/GLD, monthly | risk parity via inverse-vol |

Hypothesis: at least one variant beats iter 011 by ≥ 0.10 Sharpe on ≥ 2/3
datasets. The `aw_levered` variant has the best chance (combines iter 011's
proven cap-efficient core with explicit duration sleeve).

## Pre-committed kill criteria

KILL #1: Best-of-grid loses iter 011 on ≥ 2/3 datasets.

## Citations

- Bridgewater 2009 white paper "Engineering Targeted Returns and Risks"
- Browne *Fail-Safe Investing* (1999) for permanent portfolio
- `[risk_parity, ch.5]` Carlson — cap-efficient stacking
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

## Probability assessment

- P(strict ADVANCE): ~10% — All-Weather is conservative by design (low CAGR target).
- P(positive signal but no advance): ~25%.
- P(STRONG/PROMISING): ~50%.
- P(FAIL): ~15%.

## Note on commodities

DBC/PDBC/GSG not in testfolio cache. Substituting with gold (raises gold sleeve
from 7.5% to 15% in textbook variant). Acceptable since gold is the primary
inflation hedge in the canonical All-Weather and commodities historically
correlate ~0.5-0.7 with gold during inflation regimes.
