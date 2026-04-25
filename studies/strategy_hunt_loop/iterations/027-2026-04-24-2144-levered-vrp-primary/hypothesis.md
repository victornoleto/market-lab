# Iteration 027 — Levered VRP-primary (`harvest_notional=3.5`)

## Hypothesis

Re-run iter 026's stand-alone VRP harvester (T-bill collateral + short
SPY/QQQ 5/10% OTM put credit spread, 21-DTE monthly roll) at
**`harvest_notional = 3.5`** instead of `1.0`. The strategy daily P&L
remains:

    r_strategy[t] = rf_daily + harvest_notional × (-overlay[t])

with `overlay[t]` = iter 020's BS-priced put-spread fractional return.
The change vs iter 026 is **a single parameter** — no new mechanism,
no new entry/exit logic, no new asset.

The hypothesis is a **CAGR-floor test**: leverage scales the harvest
portion linearly while leaving Sharpe (per criterion 1) and DSR p
(per criterion 3) approximately invariant (volatility-drag aside);
this should clear the structural CAGR-floor failure that bound iter
026 at 0/3 datasets, while preserving the +0.10 Sharpe-edge and DSR
breakthrough that earned iter 026 its STRONG/76 score.

## Primary citation

`[volatility_trading, ch.3]` — VRP mechanics. Sinclair (2013) frames
short-vol harvesting as a long-run premium for bearing tail-event
losses; the harvest is structurally bounded by the spread of IV vs
realised vol, not by the size of the position written. Linear leverage
on the harvest position therefore does not erode the per-unit Sharpe
ratio (variance scales 1:1 with leverage, mean scales 1:1).

## Additional citations

- `[volatility_trading, p.41]` — SPX kurtosis 21.3 → capped credit
  spread protects the lever-up against tail-event blow-up. Per-roll
  loss is bounded at `harvest_notional × (spread_width − net_credit)`
  ≈ `3.5 × 4-4.5%` ≈ `14-16%` per roll, well under the 30%-per-roll
  Kill B floor inherited from iter 026.
- `[volatility_trading, p.217]` — Sinclair's short-vol rule (VIX < 35).
  Iter 027 omits the VIX filter to keep the parameter advance to a
  single dimension; reserved for iter 028.
- `[volatility_trading, p.11]` — BSM pricing identity (used in pricer).
- `[risk_parity, p.5]` — Asness-Frazzini-Pedersen 2012 levered-low-vol
  argument: when an asset has high Sharpe but low absolute return,
  leverage is the natural extraction mechanism; here the asset is the
  VRP harvest, with iter 026 Sharpe 1.13-1.37 and CAGR 4.85-6.31%.
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
- `[advances_fin_ml, p.222-223]` — DSR with cumulative `n_trials`.

Web/papers (no new citation vs iter 026 — the mechanism is unchanged):

- **Bondarenko, O. (2014). "Why Are Put Options So Expensive?"**
  *Quarterly Journal of Finance* 4(3): 1450015. DOI:
  10.1142/S2010139214500153. Documents 2-3%/yr SPX put-writing VRP
  (with Sharpe ~1.0-1.5 for capped credit spreads). Iter 026 realised
  2.80-4.23%/yr harvest at notional 1.0; at 3.5× the realised harvest
  scales to 9.8-14.8%/yr per Bondarenko's linear-utility argument.
- **Carr, P. & Wu, L. (2009). "Variance Risk Premiums."** *RFS* 22(3):
  1311-1341. DOI: 10.1093/rfs/hhn038.
- **Coval, J. & Shumway, T. (2001). "Expected Option Returns."**
  *Journal of Finance* 56(3): 983-1009.

## Edge source

Same as iter 026 — VRP harvest. The hypothesis being tested is
specifically about **whether the harvest's Sharpe edge (which iter 026
established) survives the linear leverage required to clear CAGR
floor**. Theory says yes (Sharpe is leverage-invariant for the harvest
portion); this iter is the empirical confirmation on real data.

## Datasets

Identical to iter 026 — same windows, same instruments:

- **educational**: SPY + VIX, 2006-01-03 → 2026-04-15 (~20y, ~5050 bars).
- **spy_real**: SPY + VIX, 2009-06-25 → 2026-04-15 (~17y, ~4225 bars).
- **ndx_real**: QQQ + VIX×1.1, 2010-02-12 → 2026-04-15 (~16y, ~4065 bars).

## Pre-committed parameter choice — `harvest_notional = 3.5`

**Reason for choosing 3.5 over BASE_MEMORY's listed {2.0, 2.5}**: the
BASE_MEMORY V-2 candidate spec listed `harvest_notional ∈ {2.0, 2.5}`
based on iter 026's optimistic projection (8-10%/yr CAGR at 2.0×).
Empirical iter 026 measured `harvest_annualized` per dataset is:

| dataset | harvest_ann | rf | total | floor (0.8×bench) | clears? |
|---|---|---|---|---|---|
| educational | 2.80% | 2.00% | 4.85% (with vol drag) | 9.18% | NO |
| spy_real    | 2.92% | 2.00% | 4.97% | 11.98% | NO |
| ndx_real    | 4.23% | 2.00% | 6.31% | 15.35% | NO |

Linear projection at notional N (rf + N × harvest_ann), worst-case
volatility drag ≈ 0.5×σ² (small even at high N):

| N | edu | spy | ndx | clears |
|---|---|---|---|---|
| 1.0 (iter 026) | 4.85% | 4.97% | 6.31% | 0/3 |
| 2.0 | 7.60% | 7.84% | 10.46% | 0/3 |
| 2.5 | 9.00% | 9.30% | 12.58% | 0/3 (edu borderline) |
| 3.0 | 10.40% | 10.76% | 14.69% | 1/3 (edu only) |
| **3.5** | **11.80%** | **12.22%** | **16.81%** | **3/3** |
| 4.0 | 13.20% | 13.68% | 18.92% | 3/3 (but MDD risk) |

`harvest_notional = 3.5` is **the minimum integer-half value that
clears CAGR floor on all 3 datasets** under the linear-scaling
assumption proven by `tests/test_iter_026_vrp_primary.py::
test_harvest_scales_linearly`.

MDD ceiling check at 3.5× (linear scaling of iter 026 MDD):

| dataset | MDD@1.0 | MDD@3.5 (linear) | ceiling | clears? |
|---|---|---|---|---|
| educational | 16.82% | 58.87% | 60.14% | YES (1.27pp margin) |
| spy_real    | 6.35%  | 22.22% | 38.70% | YES |
| ndx_real    | 8.18%  | 28.63% | 40.12% | YES |

Per-roll worst-case loss: `3.5 × ~4-4.5% spread cap` = `14-16%` per
roll, well under the 30%-per-roll Kill B floor from iter 026.

## Kill criteria (pre-committed)

If ANY of the following is observable at end of Stage 3, the hypothesis
is falsified regardless of secondary metrics:

- **Kill A — Sharpe regresses materially vs iter 026** (any dataset
  Sharpe drop > 0.05). Means the leverage-neutrality assumption fails
  in practice (e.g., compounding artifact, transaction costs scaling
  non-linearly). Evidence against linear-leverage hypothesis.
- **Kill B — Catastrophic per-roll loss > 30%** on any dataset (same
  test as iter 026, scaled). Means the credit-spread cap fails under
  3.5× leverage (e.g., margin call mid-roll, structural break).
- **Kill C — MDD ceiling fails on ≥ 2 datasets**. Means leverage too
  aggressive for risk budget.
- **Kill D — CAGR floor still 0/3** despite leverage. Means the
  scaling math is wrong or harvest doesn't survive the leverage step.
- **Kill E — Engine dirty** (G7 cross-library CAGR diff > 3 pp).
  Means BS pricer drifts under leverage.

If only Kill A fires (no others), continue analysis: the boundary is
"leverage is not Sharpe-neutral on this strategy" which informs iter
028+. If Kill B/C/D fire together, the strategy collapses under
leverage and the iter 026 finding is **architecturally bounded** at
notional ≤ 1.0.

## Expected outcome (pre-registration)

If linear leverage holds (theory says yes; iter 026 test confirms
mathematically):

| metric | iter 026 (h=1.0) | iter 027 (h=3.5) | floor/ceiling |
|---|---|---|---|
| Sharpe edu/spy/ndx | 1.13/1.28/1.37 | 1.13/1.28/1.37 (~) | bench+0.10 cleared |
| CAGR edu/spy/ndx | 4.85%/4.97%/6.31% | ~11.8%/12.2%/16.8% | floors cleared |
| MDD edu/spy/ndx | 16.82%/6.35%/8.18% | ~58.9%/22.2%/28.6% | ceilings cleared |
| DSR p edu/spy/ndx | 0.083/0.070/0.038 | ~same | edu/spy still > 0.05 |

Score projection (criteria 1-6):

| criterion | iter 026 pts | iter 027 expected pts | reason |
|---|---|---|---|
| 1 Sharpe edge | 25 | 25 | leverage-neutral |
| 2 Gates | 21 | 21-25 | gates preserved (G3 WF risk at 3.5×) |
| 3 DSR | 10 | 10 | DSR p invariant under leverage |
| 4 CAGR floor | 0 | **15** | 3/3 clear after leverage |
| 5 MDD ceiling | 15 | 15 | 3/3 still clear at 3.5× |
| 6 Robustness | 5 | 5 | sub-window Sharpe sign invariant |
| **total** | **76** | **91-95** | tier likely STRONG (DSR caps WINNER) |

Strict winner conditions (4/5 expected):

| # | condition | iter 026 | iter 027 expected |
|---|---|---|---|
| 1 | Sharpe edge ≥ +0.10 on ≥ 2/3 | YES (3/3) | **YES (3/3)** |
| 2 | Gates: edu ≥5, spy ≥4, ndx ≥4 | YES | **likely YES** |
| 3 | DSR worst p < 0.05 | NO (0.083) | **NO (~0.083)** |
| 4 | CAGR floor 0.8×bench on ≥ 2/3 | NO (0/3) | **YES (3/3)** |
| 5 | MDD ceiling +5pp on ≥ 2/3 | YES (3/3) | **YES (3/3)** |

**Expected verdict: STRONG (score 91-95), 4/5 winner conditions, DSR
sole gap.** Sets a new top-K record (above iter 016/018/021 79).

## Expected budget

- Configs to test: **1** (single pre-committed cfg, no grid).
- Wall-time: ~25-30 minutes (3 datasets × monthly-roll BS pricing on
  ~5000 bars × gate battery — same as iter 026).
- New files to create:
  - `run_backtests.py` (modified copy of iter 026; cfg = `vrp_primary_h3_5_5_10_1m`)
  - `compute_gates_and_score.py` (modified copy; CUMULATIVE_N_TRIALS = 4280)
  - `tests/test_iter_027_levered_vrp.py` (new TDD spec — minimal)
- Reuses (no copy):
  - `vrp_primary.py` from iter 026 (function `compute_vrp_primary_returns`)
  - `numpy_reference_vrp.py` from iter 026
  - `put_spread_hedge.py` from iter 020 (BS pricer)
  - `compute_put_spread_daily_returns` from iter 020

## Implementation plan

1. **Write iter 027 TDD spec** (`tests/test_iter_027_levered_vrp.py`):
   - `test_iter027_h35_scales_h10_linearly` — verify
     `(r_h35 - rf_daily) ≈ 3.5 × (r_h10 - rf_daily)` on synthetic.
   - `test_iter027_sharpe_invariant_under_leverage` — verify
     `Sharpe(r_h35) ≈ Sharpe(r_h10)` on synthetic (leverage-neutral
     argument).
   - `test_iter027_volatility_drag_bounded` — verify CAGR loss vs
     `rf + 3.5×harvest_ann` is < 0.5%/yr on synthetic.
   - `test_iter027_per_roll_loss_capped` — verify single-roll loss
     stays bounded (no margin blow-up in the model).
2. **Run** iter 027 backtests on 3 datasets via modified
   `run_backtests.py` (single cfg `vrp_primary_h3_5_5_10_1m`).
3. **Compute** gates G1-G7 + score via modified
   `compute_gates_and_score.py` (`CUMULATIVE_N_TRIALS = 4280`).
4. **Plot** equity-vs-benchmark via plot_helper (mandatory).
5. **Write** `final_report.md`, `verdict.json`.
6. **Update** `BASE_MEMORY.md` with iter 027 entry, possibly new
   top-K #1 if score ≥ 80.

## Pre-registration of n_trials advance

`cumulative_n_trials`: 4279 → **4280** (+1 single pre-committed cfg ×
3 datasets = 1 trial unit per project convention from iter 015/016/
018/021/024/025/026).
