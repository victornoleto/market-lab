# Iter 021 — Final report: C.4 — Sector rotation top-K monthly momentum (4-sector universe)

**Date**: 2026-04-29
**Slug**: `C4-sector-rotation`
**Selected**: `sec4_K2_TLT` (XLE/XLF/XLK/XLU, K=2, abs-mom fallback TLT)

## Verdict

**Tier**: 🥈 **PROMISING** (score **69/100**, **winner_conditions_met=FALSE**) — Sharpe edges fail 3/3 (max +0.056 vs avg(SPY,VT)).

**KILL #1 fired hard**: best-of-grid loses iter 011 substantively on 3/3 (−0.34 / −0.20 / −0.32).

## Headline

| dataset | gross S | edge vs avg(SPY,VT) | gross CAGR | gross MDD | gates |
|---|---:|---:|---:|---:|---:|
| lh_56y    | 0.708 | +0.037 ✗ | 12.58% | 42.79% | 6/7 |
| vt_real   | 0.762 | +0.056 ✗ | 13.13% | 34.30% | 5/7 |
| ndx_real  | 0.788 | −0.136 ✗ | 13.61% | 34.30% | 5/7 |

CAGR is decent (~13%) but Sharpe is poor due to high vol (sector concentrations) and MDD is 34-43% — far worse than any other iter.

## Per-config grid

| config | universe | K | fallback | lh_56y | vt_real | ndx_real |
|---|---|---:|---|---:|---:|---:|
| `sec4_K1_TLT`  | XLE/XLF/XLK/XLU | 1 | TLTSIM | 0.672 | 0.721 | 0.730 |
| `sec4_K2_TLT` ✅ | XLE/XLF/XLK/XLU | 2 | TLTSIM | **0.708** | **0.762** | **0.788** |
| `sec4_K2_KMLM` | XLE/XLF/XLK/XLU | 2 | KMLMSIM | 0.636 | 0.635 | 0.720 |
| `sec4_K3_TLT`  | XLE/XLF/XLK/XLU | 3 | TLTSIM | 0.611 | 0.661 | 0.679 |

## Lesson

**Sector rotation in a 4-sector universe is too narrow** to deliver meaningful
diversification benefit. XLE/XLF/XLK/XLU all share strong equity beta during
crises (2008, 2020 March), so the rotation can't escape drawdown by switching
within the universe. The TLT fallback only triggers when ALL 4 sectors have
negative momentum — typically only 2009 / 2020 brief windows.

**Data limitation**: 9-sector full universe (incl XLP/XLV/XLY/XLB/XLI staples
+ defensive sectors) would be the proper test, but those start 2014-01 in our
Tiingo cache. Backfilling to 1998 (XL* SPDR inception) via Yahoo Finance is
deferred infra (~1-2h work).

**Family-level conclusion**: sector momentum is plausible with full 9-sector
universe + longer history; the 4-sector test here is **inconclusive but
biased toward fail** (universe too narrow). Logging as DE-021 with caveat
that the test is data-limited.

## Citations

- `[stocks_on_the_move, ch.6]` Clenow sector momentum
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

## Next directions

- iter 022 — C.5 tail-hedge (last in fila 016-022)

*Generated 2026-04-29 by long_term_portfolio loop iter 021.*
