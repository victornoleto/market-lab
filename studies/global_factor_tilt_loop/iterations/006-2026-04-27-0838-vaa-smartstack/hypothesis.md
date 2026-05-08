# Iter 006 — VAA-G4 SmartStack — Hypothesis

**Date:** 2026-04-27  
**Slug:** vaa-smartstack  
**Tier-0 queue entry:** "iter 006 — VAA-G4 SmartStack equivalent"

---

## Hypothesis

Vigilant Asset Allocation (Keller & Keuning 2017, SSRN 3002624) applied to a
stacked-ETF global universe outperforms both buy-and-hold VT and the HAA
SmartStack (iter 005) by providing **finer-grained regime detection** through
breadth momentum. Rather than a single canary asset triggering a binary
risk-on/off switch, VAA's breadth rule counts how many of 4 offensive assets
show positive 13612W momentum — if B=2 of 4 are positive, exactly 50% of the
dynamic portfolio moves to defensive. This continuous defensive scaling reduces
drawdown in partial-market crises (e.g., US holds up while EM/Intl sell off)
that a single global canary would miss.

The 13612W signal (`(12·r1 + 4·r3 + 2·r6 + r12) / 19`) weights recent
1-month returns 12× more than 12-month returns, making the signal more
responsive to regime changes while retaining long-horizon context. Combined
with the stacked offensive universe (capital efficiency via 90/60 structures)
and a fixed 15% MF+gold sleeve, the hypothesis is that VAA-G4 SmartStack
matches or exceeds HAA SmartStack on Sharpe while maintaining superior
drawdown control vs all three mandated benchmarks.

---

## Primary citation

`[stocks_on_the_move, ch.6]` — breadth momentum mechanics (Clenow; multi-asset
momentum breadth as regime signal). Supplementary: VAA SSRN 3002624 (Keller &
Keuning 2017).

---

## Edge source

**What VT / Plano C / V_HYBRID miss**: Single-canary approaches (HAA, iter 005)
use one global asset (VWOSIM) as the sole risk barometer. When regional crises
are geographically isolated — US equity holds while EM/Intl collapse — the
VWOSIM canary may not fire until global contagion spreads. VAA's breadth rule
provides regional independent early warnings: NTSE (EM stack) going negative
reduces defensive allocation by 25% even if NTSXSIM (US stack) is still up.

**What HAA SmartStack misses vs this hypothesis**: HAA allocates equal weight
(45% each) to top-2 offensive regardless of their relative momentum scores.
VAA concentrates into top-1 when breadth is maximum (B=4 → 100% dynamic to
top-1), potentially boosting CAGR in strong risk-on regimes.

---

## Datasets

- `educational`: VTSIM binding 1994-05 (VWOSIM canary), effective 1995-05+ (~31y)
- `vt_real`: VTSIM proxy 2008-06+ (~17y)
- `ndx_real`: QQQ proxy 2010-02+ (16y) — stretch benchmark

---

## Universe

**Offensive G4 (stacked):**
| asset | construction | notional |
|---|---|---|
| NTSXSIM | 0.90 SPYSIM + 0.60 IEFSIM − 0.50 CASHX | ~1.5× |
| NTSI | 0.90 VEASIM + 0.60 IEFSIM − 0.50 CASHX | ~1.5× |
| NTSE | 0.90 VWOSIM + 0.60 IEFSIM − 0.50 CASHX | ~1.5× |
| BNDSIM | 1× aggregate bond (testfolio cache) | 1.0× |

**Defensive G3:**
| asset | role |
|---|---|
| IEFSIM | 7-10y Treasury |
| CASHX | T-bill collateral |
| BNDSIM | Aggregate bond (LQD proxy) |

**Fixed sleeve (always-on):**
| asset | weight | role |
|---|---|---|
| KMLMSIM | 10% | Managed futures (crisis hedge) |
| GLDSIM | 5% | Gold (inflation / tail hedge) |

Total sleeve = 15%. Dynamic allocation = 85%.

---

## VAA-G4 allocation rule

Signal: `vaa_score(a) = (12·r1 + 4·r3 + 2·r6 + r12) / 19` for each asset a.

Each month:
1. Compute 13612W score for all 4 offensive assets.
2. `B = count(offensive assets with vaa_score > 0)`.
3. Compute defensive fraction `d = (4 - B) / 4`, offensive fraction `o = B / 4`.
4. If `B == 0`: 100% dynamic to top-1 defensive by vaa_score.
5. If `B > 0`:
   - Rank offensive by vaa_score descending; allocate `o × 85%` equally to top-B.
   - Rank defensive by vaa_score descending; allocate `d × 85%` to top-1 defensive.
6. Always: 10% KMLMSIM + 5% GLDSIM (fixed).

Total notional (B=4 case): top-1 offensive (stacked ~1.5×) × 85% + KMLMSIM 1× × 10% + GLDSIM 1× × 5% ≈ 1.40× average.

---

## Pre-committed kill criteria

- **Kill 1**: edu Sharpe ≤ 1.112 (HAA iter 005 result) → structurally subordinate to HAA; still rank but not a new structural advance.
- **Kill 2**: any WF window G3' fails → structural MDD failure.

Both kills observed → append to DEAD_ENDS.md.

---

## Expected budget

- `N_CONFIGS = 1` (pre-committed single config, no grid)
- `n_trials = 1` → DSR penalty minimal
- Wall-time: ~15 min (data load + 3 datasets × gate battery)

---

## Implementation plan

1. Adapt `iterations/005-*/backtest.py`:
   - Replace `haa_momentum` with `vaa_13612w` signal
   - Replace `simulate_haa_smartstack` with `simulate_vaa_smartstack` (breadth rule)
   - Replace `simulate_haa_smartstack_numpy` with `simulate_vaa_smartstack_numpy`
   - Offensive: remove GDESIM, add BNDSIM (4th asset)
   - Sleeve: add GLDSIM 5%, reduce dynamic from 90% to 85%
2. Run 3 datasets, gate battery identical to iter 005
3. Score via `scoring.py`
4. Write `results.json`, `verdict.json`, `final_report.md`
5. Update `BASE_MEMORY.md`
