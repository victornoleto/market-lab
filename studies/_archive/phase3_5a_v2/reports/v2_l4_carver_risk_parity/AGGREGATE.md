# Lead V2-L4 — Carver risk-parity multi-strategy blend (aggregate)

**Phase:** phase3_5a_v2 | **Lead:** V2-L4 | **Status:** ❌ DEAD (blend fails winner criteria)
**Period:** 2003-08-20 → 2026-04-14 (longest common window — XLF first bar gates the start)
**Method:** Carver vol-target + equal-weight `[systematic_trading, p.~280-310]`
**Aggregation iter:** 58
**Path tag:** [SHORT-HOLD CFD]

## Summary

V2-L4 mechanically follows §4 of the V2 spec: take the best-Sharpe-OOS
non-NaN candidate from each of V2-L1 (TSMOM), V2-L2 (Gayed transported
CFD) and V2-L3 (AFML triple-barrier + meta), scale each to a common
15% annualised vol target using the IS window only
(`[systematic_trading, p.~280-310]`, no look-ahead), then equal-weight
the scaled series into a single daily-returns track. Gates, winner
criteria, PBO, DSR, stationary-bootstrap 99.9% CI and IR-vs-SPY are
applied on the blended series.

**Inputs (best-Sharpe-OOS per lead):**
| Lead | Config | OOS Sharpe | OOS CAGR | OOS MDD |
|------|--------|-----------:|---------:|--------:|
| L1   | `tsmom_lb12m_vt10`           | **−0.212** | −0.49% | −10.24% |
| L2   | `gayed_ema100_L3_off_gld`    | **+2.294** | 128.93% | −30.04% |
| L3   | `XLF` (AFML tb+meta)         | **+1.213** | 2.50%  | −0.76% |

**IS-derived scaling (σ_target / σ_i):**
| Leg | Scale | Implied risk weight |
|-----|------:|--------------------:|
| L1 TSMOM  | 2.59 | 29.2% |
| L2 Gayed  | 0.44 | 4.9% |
| L3 XLF    | 5.85 | 65.9% |

L3 (AFML XLF) dominates the risk budget because its IS vol is
unnaturally low (flat-hold days from the meta filter drop raw σ). L2,
the only real alpha in the bunch, is pushed to a **4.9%** implied
weight — i.e. the Carver recipe essentially *dilutes* the winning
strategy under the L1+L2+L3 basket that the spec dictates.

## Blend performance (3-leg per spec)

| Split | Sharpe | CAGR | MaxDD | n |
|-------|-------:|-----:|------:|---:|
| IS (2003-08→2017-12)   | 0.703 | 6.95% | −23.78% | 3617 |
| OOS (2018→2023)        | **1.856** | 16.14% | −8.44%  | 1509 |
| FWD (2024→2026-04)     | 0.594 | 4.54% | −6.87%  | 572 |
| FULL                    | 0.900 | 8.35% | −23.78% | 5698 |

**Core AFML gates (all PASS):**
- PBO = **0.000** (10-block CSCV over 4-col matrix `[L1, L2, L3, blend]`) `[advances_fin_ml, p.208-211]`
- DSR p-value = **0.001355** (OOS, n_trials = 4) `[advances_fin_ml, p.273-275]`
- Walk-forward 7/8 profitable, max-window MDD 23.78% ≤ 25% → PASS `[advances_fin_ml, ch.11]`
- Stationary bootstrap 99.9% CI low = **0.489** > 0 `[advances_fin_ml, p.196-202]`

**V2 winner criteria (§6 of `specs/phase_3_5a_v2.md`):**
| Criterion | Threshold | Blend | Pass |
|-----------|-----------|------:|:----:|
| PBO | < 0.5 | 0.000 | ✅ |
| DSR p-value | < 0.05 | 0.0014 | ✅ |
| WF | ≥ 6/8 | 7/8 | ✅ |
| Bootstrap 99.9% CI low | > 0 | 0.489 | ✅ |
| OOS CAGR net | ≥ 30% | **16.14%** | ❌ |
| OOS Sharpe net | ≥ 2.0 | **1.856** | ❌ |
| OOS MaxDD | ≤ 25% | −8.44% | ✅ |
| IR vs SPY (OOS) | ≥ 0.5 | **0.106** | ❌ |

**Verdict: ❌ DEAD.** The blend passes every statistical robustness
check but misses three hard winner thresholds — CAGR below the Plano B
benchmark (25.56%), Sharpe below 2.0, and SPY IR too low to justify
the overlay over a simple long-SPY allocation. Forward-window Sharpe
0.59 is positive but weak.

## Diagnostic — why the blend dilutes the L2 winner

Under Carver risk parity each leg contributes equal variance. That is
the right recipe when the constituent strategies are all positive-edge
and roughly uncorrelated. In this blend:

- **L1 TSMOM** has an OOS Sharpe of **−0.21** — the multi-asset TSMOM
  canonical (ch.8 Carver) simply did not survive the V2 cost model
  (AGGREGATE in `v2_l1_tsmom_multi_asset_daily/`). Feeding it into a
  risk-parity blend contributes drag, not diversification.
- **L3 AFML XLF** is technically positive (Sharpe 1.21) but with a
  2.5%/yr CAGR — its variance is so small that vol-target scaling
  *inflates* its weight to 66% of the blend. The blend's risk profile
  ends up dominated by a CAGR-starved leg.
- **L2 Gayed `L3_off_gld`** is the only real alpha (Sharpe 2.29, CAGR
  129%). After 15% vol-target scaling and equal weighting it carries
  only 4.9% of the blend risk — not enough for its alpha to survive
  the dilution from L1 and L3.

The finding is consistent with AFML ch.16 and Carver ch.9: a
risk-parity stack only improves risk-adjusted returns when **every
input carries a positive expected edge at its own vol target**. Two of
the three candidates here do not, so the theoretical benefit reverses.

## Diagnostic 2-leg (L2 + L3, drops negative L1)

For reference, a cleaner 2-leg vol-target equal-weight of just L2 and
L3 (drops the OOS-negative L1) gives:

| Metric | L2 standalone | Blend 2-leg (L2 + L3) | Delta |
|--------|--------------:|----------------------:|------:|
| OOS Sharpe | 2.294 | 2.021 | −0.27 |
| OOS CAGR   | 128.93% | 25.77% | −103.2 pp |
| OOS MaxDD  | −30.04% | −12.66% | +17.4 pp |
| WF         | 8/8 | 8/8 | 0 |
| IR vs SPY (OOS) | ~2.16 | 0.574 | −1.58 |

Half of L2's CAGR is lost for a two-thirds cut in MDD, but the result
still **fails** the V2 CAGR ≥ 30% threshold. **The standalone
`gayed_ema100_L2_off_gld` winner (Sharpe 2.285, CAGR 79%, MDD −21%)
remains the Plano A answer; no blend improves on it under V2 criteria.**

## V2-L4 consumed — move on

V2-L4 is atomic: 1 iter, 1 decision. The decision is DEAD at the
winner-criteria layer, with the L2 standalone winner preserved as the
unique Plano A candidate. Next iter proceeds to V2-L5 (equity pairs,
Kalman dynamic beta on 6 pre-selected pairs).

## Artifacts

- `AGGREGATE.json` — full numeric detail (winner checks, split
  metrics, PBO/DSR/bootstrap, diagnostic 2-leg).
- `carver_rp_blend_daily_returns.parquet` — per-day blend return,
  vol-target 15% + equal-weight, for any downstream transport test.

## Citations

- Carver S. (2015) *Systematic Trading*, ch.8-9 — risk budgeting / vol target / inverse vol.
- López de Prado (2018) *Advances in Financial Machine Learning*, ch.16 — portfolio construction;
  p.208-211 PBO/CSCV; p.273-275 DSR; p.196-202 stationary bootstrap CI.
- Memory anchor: `docs/self_improvement/memory.md` iter 57 → 58 transition.
- Spec: `specs/phase_3_5a_v2.md` §4 V2-L4 atomic definition.
