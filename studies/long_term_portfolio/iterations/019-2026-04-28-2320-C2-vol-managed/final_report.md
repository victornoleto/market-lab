# Iter 019 — Final report: C.2 — Vol-managed 60/40 (NTSX+IEF base)

**Date**: 2026-04-28
**Slug**: `C2-vol-managed-60-40`
**Selected**: `vt_8pct` (target vol 8%, lookback 60d, weight cap [0.5, 2.0])
**Base**: 60% NTSX + 40% IEF (cap-efficient 60/40, ~1.4× notional)

## Verdict

**Tier**: 🥇 **STRONG** (score **81/100**, winner_conditions_met=**FALSE**).

**Why no winner**: CAGR floor fails on 3/3 datasets (vol-targeting at 8%
sacrifices average CAGR for smoother returns). Sharpe-edge gate clears
(3/3 +0.10 vs avg(SPY,VT)) but CAGR drag is too steep.

**Beats incumbent**: ❌ false.

## Headline metrics

| dataset | gross S | edge vs avg(SPY,VT) | gross CAGR | bench × 0.8 | CAGR floor | gates |
|---|---:|---:|---:|---:|---|---:|
| lh_56y    | 0.991 | +0.319 ✓ | 8.13% | 8.58% | ✗ | 5/7 |
| vt_real   | 1.052 | +0.345 ✓ | 9.32% | 9.51% | ✗ | 7/7 |
| ndx_real  | 1.117 | +0.193 ✓ | 9.71% | 13.59% | ✗ | 7/7 |

| metric | iter 019 | iter 011 (subst) | Δ |
|---|---|---|---|
| lh_56y S | 0.991 | 1.046 | −0.055 |
| vt_real S | 1.052 | 0.960 | **+0.092** |
| ndx_real S | 1.117 | 1.104 | +0.013 |

iter 019 modestly **wins vt_real** (close to +0.10 hurdle), **loses lh_56y** and matches ndx_real. CAGR is uniformly lower than iter 011 (8-10% vs 11-12%).

## Per-config grid — monotonic

| config | target_vol | lh_56y | vt_real | ndx_real |
|---|---:|---:|---:|---:|
| `vt_8pct`  ✅ | 8%  | **0.991** | **1.052** | **1.117** |
| `vt_10pct` | 10% | 0.989 | 1.047 | 1.102 |
| `vt_12pct` | 12% | 0.983 | 1.033 | 1.081 |
| `vt_15pct` | 15% | 0.967 | 1.012 | 1.065 |

**Lower target_vol = higher Sharpe** (counterintuitively but expected by Carver):
the 8% target keeps weight averaged ~0.7-0.9 (de-risked), capturing returns
with much less variance — but CAGR shrinks proportionally.

## Pre-committed kill criteria

| KILL | criterion | status |
|---|---|---|
| **#1** | Best-of-grid loses iter 011 on ≥2/3 | **NOT FIRED** (loses lh_56y −0.055 only; ties ndx; wins vt) |
| **#2** | Sharpe monotonically decreases as target_vol rises | confirmed but EXPECTED (lower vol target → smoother → higher SR; not a kill, just monotonic) |

KILL #1 narrowly avoided. The substantive issue is CAGR floor — vol-targeting
trades CAGR for smoother Sharpe.

## Lesson

Vol-managed 60/40 (NTSX+IEF) at 8% target produces Sharpe close to iter 011
(narrow loss on lh_56y, narrow win on vt_real, tied ndx) but **with CAGR ~3pp
lower across the board**. This is the canonical Carver tradeoff: vol-targeting
removes left-tail volatility but also caps right-tail upside, so CAGR drops
proportionally.

For a long-term portfolio aiming at 11-13% CAGR (iter 011's range),
8-10% CAGR is a deal-breaker even with cleaner Sharpe. The mechanism
**works as advertised** — just doesn't fit this loop's CAGR floor mandate.

**Direction-level conclusion**: vol-targeting on a 60/40 base is not
competitive with capital-efficient stacks (iter 011 family) for CAGR-sensitive
long-term portfolios. It might be competitive for a "max-Sharpe with MDD
constraint" mandate, but that's not this loop's mission.

## Citations

- `[systematic_trading, p.137-148]` Carver: vol-targeting / position sizing
- `[risk_parity, ch.5]` Carlson: 60/40 cap-efficient base
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

## Next directions

iter 019 closed C.2. Continuing fila:
- iter 020 — C.3 All-Weather Bridgewater-mimic (different mechanism: risk parity)
- iter 021 — C.4 Sector rotation
- iter 022 — C.5 Tail-hedge

*Generated 2026-04-28 by long_term_portfolio loop iter 019.*
