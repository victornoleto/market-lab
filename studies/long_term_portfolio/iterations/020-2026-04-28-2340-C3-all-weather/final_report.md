# Iter 020 — Final report: C.3 — All-Weather Bridgewater-mimic (4 variants)

**Date**: 2026-04-28
**Slug**: `C3-all-weather`
**Selected**: `aw_browne_25252525` (25% SPY + 25% TLT + 25% GLD + 25% CASH — Harry Browne permanent portfolio)

## Verdict

**Tier**: 🥇 **STRONG** (score **83/100**, **winner_conditions_met=FALSE**) — same failure mode as iter 019: Sharpe edge clears 3/3 vs avg(SPY,VT) but CAGR floor fails 3/3 (defensive mandate).

**Beats incumbent**: ❌ false.

## Headline metrics

| dataset | gross S | edge vs avg(SPY,VT) | CAGR | bench × 0.8 | CAGR floor | gates | Δ vs iter 011 |
|---|---:|---:|---:|---:|---|---:|---:|
| lh_56y    | 1.114 | +0.442 | 6.61% | 8.58% | ✗ | 7/7 | +0.068 |
| vt_real   | 0.984 | +0.277 | 7.35% | 9.51% | ✗ | 6/7 | +0.024 |
| ndx_real  | 1.097 | +0.173 | 7.65% | 13.59% | ✗ | 7/7 | −0.007 |

Excellent **MDD 17.15% across all datasets** (most defensive of any iter). Sharpe positive 3/3. CAGR is the deal-breaker.

## Per-config grid

| config | lh_56y | vt_real | ndx_real | note |
|---|---:|---:|---:|---|
| `aw_textbook_30_40_15_15`  | 0.997 | 0.875 | 0.959 | classic 30/40/15/15 (gold sub for commodities) |
| `aw_browne_25252525` ✅    | **1.114** | **0.984** | 1.097 | Browne permanent — selected by mean-S/bench |
| `aw_levered_NTSX_GDE_TLT`  | 0.987 | 0.947 | **1.120** ⭐ | iter 011 family + TLT — only to beat iter 011 ndx_real (1.120 > 1.104) |
| `aw_inv_vol_4asset`        | **1.143** ⭐ | 0.962 | 0.975 | inv-vol risk parity — highest lh_56y after iter 016 UMD |

**Two notable highlights**:
- `aw_inv_vol` lh_56y 1.143 is the highest **non-UMD** Sharpe in this loop.
- `aw_levered` ndx_real 1.120 is **the only iter so far to beat iter 011's
  ndx_real 1.104** (modest +0.016 win).

## Lesson

All-Weather family delivers **cleanest MDD profile (17%)** in the entire loop
and very strong Sharpe (1.0-1.14 range), but at **6.6-8.0% CAGR cost** which
fails the loop's CAGR floor mandate. Same structural conclusion as iter 019:
defensive portfolios are valid for max-Sharpe / min-MDD mandates but not
for the long-term-portfolio CAGR-target this loop is hunting.

**Caveat: `aw_levered_NTSX_GDE_TLT`** is interesting — combines iter 011's
proven core with a duration sleeve and modestly beats iter 011's ndx_real.
CAGR not reported above but expected ~10-11% (closer to iter 011 level
since it uses leveraged components). Worth a sub-iter follow-up if the user
wants to explore "iter 011 + TLT sleeve" specifically.

**Direction-level**: All-Weather is closed for the WINNER mandate but
preserves a useful **risk-parity perspective** for any future "balanced
sleeve" extension of iter 011.

## Citations

- Bridgewater 2009 white paper "Engineering Targeted Returns and Risks"
- Browne 1999 *Fail-Safe Investing*
- `[risk_parity, ch.5]` Carlson — cap-efficient stacking
- Gates: `[advances_fin_ml, p.208-211, p.222-223, p.196-202, p.31-34]`

## Next directions

- iter 021 — C.4 sector rotation (different mechanism, dynamic equity)
- iter 022 — C.5 tail-hedge

*Generated 2026-04-28 by long_term_portfolio loop iter 020.*
