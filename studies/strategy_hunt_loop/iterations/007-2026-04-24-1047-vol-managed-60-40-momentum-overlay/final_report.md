# Iteration 007 — Final Report

## Verdict

**🥉 MARGINAL (score 50/100, winner_conditions_met=False, tier=MARGINAL)**

Adding a time-series momentum overlay (12-1 canonical, Jegadeesh-Titman
/ Moskowitz-Ooi-Pedersen) on top of iter 006's vol-managed SPY+TLT
blend **reduces** risk-adjusted performance on real data. The top
overlay candidate (`mom252_skip21`) scores Sharpe 0.941 on spy_real
(vs iter 006's 1.000, Δ−0.06) and 0.872 on ndx_real (vs iter 006's
1.021, Δ−0.15). The overlay DOES reduce MDD by 2-5 pp on all 3
datasets — but CAGR drops proportionally more, so net Sharpe is worse.
Score falls from iter 006's PROMISING 67/100 back to MARGINAL 50/100
(same tier as iter 004).

**Kill criteria check** (pre-committed):

- **Kill #1** (top-cfg Sharpe ≤ iter 006 on BOTH real-data slots):
  **TRIGGERED**. spy_real 0.941 < 1.000 AND ndx_real 0.872 < 1.021.
  The overlay is dead weight on top of variance-scaled blend —
  hypothesis falsified at the edge-compounding axis.
- **Kill #2** (gate_on < 20% or > 95%): **NOT triggered**. Gate
  fires on 78-93% of bars across datasets (`mom252_skip21` = 85-91%).
  Gate is active but most of the time agrees with "deploy".
- **Kill #3** (grid-level PBO > 0.5 on 2+ datasets): **TRIGGERED**.
  PBO 0.643 / 0.762 / 0.746 — all 3 datasets fail. Compound
  mechanism remains overfit-sensitive even at a 3-config grid (same
  family of issue as iter 006's 12-config grid).
- **Kill #4** (turnover > 4×/year): **NOT triggered** on `mom252_skip21`
  (70 flips over 24y ≈ 2.9 flips/year). Would have triggered on
  `mom126_skip21` (163 flips / 24y = 6.8 flips/year) — confirming
  shorter lookbacks produce excessive false-signal churn.

Two of four kill criteria fire; the core hypothesis (momentum
compounds with vol-managed blend to raise Sharpe) is rejected.

## Headline metrics (top candidate per dataset)

Top overlay per dataset is `mom252_skip21` on all three (12-1 canonical
wins the Sharpe race among the 3 momentum configs). Fixed blend base:
`vt15_L21_cap20`.

| dataset | Sharpe (Δ) | CAGR (Δ) | MDD | iter 006 ref | Δ vs iter 006 Sharpe |
|---|---|---|---|---|---|
| educational (SPY+TLT 24y) | 0.916 (+0.254) | 12.93% (+1.84pp) | 35.15% | 0.929 | **−0.013** |
| spy_real (SPY+TLT 17y) | 0.941 (+0.041) | 14.19% (−0.78pp vs bench) | 35.15% | 1.000 | **−0.059** |
| ndx_real (QQQ+TLT 16y) | 0.872 (−0.083) | 14.33% (−4.85pp vs bench) | 35.84% | 1.021 | **−0.149** |

The *magnitude* of the Sharpe drop scales with the dataset's pre-overlay
Sharpe: educational (iter 006 Sharpe 0.929) loses only −0.013 while
ndx_real (iter 006 Sharpe 1.021) loses −0.149. The more the base blend
was earning, the more the overlay costs. This is a strong hint that
the overlay is **net-negative information**, not signal-free:
regime-skipping is adversarial to a variance-scaling mechanism that
already exits in high-vol regimes.

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **10** | 25 | 1/3 datasets beat bench + 0.10 (educational only, +0.254). spy +0.041 misses gate, ndx −0.083 NEGATIVE. |
| 2 Gates | **15** | 25 | edu 5/7 (5 pts min) + spy 5/7 (5 pts min+1) + ndx 4/7 (3 pts min) + **+4 cross-dataset bonus** (all meet spec §0 minimums). Clip to 25. |
| 3 DSR | **0** | 15 | worst p = 0.604 (ndx_real) at cumulative n_trials=4237 — far from p<0.20 threshold |
| 4 CAGR floor | **10** | 15 | edu 12.93% ≥ 8.87% ✓, spy 14.19% ≥ 11.98% ✓, ndx 14.33% < 15.35% ✗ (0.747× bench, under 0.8 floor) |
| 5 MDD ceiling | **15** | 15 | 3/3 within bench + 5pp (edu 35.15% ≤ 60.20%, spy 35.15% ≤ 38.70%, ndx 35.84% ≤ 40.12%) |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **50** | 100+5 | tier: **🥉 MARGINAL** (iter 006: PROMISING 67) |

**Regression from iter 006: −17 points.**

## Gate detail (G1-G7) per dataset

| gate | edu | spy | ndx |
|---|---|---|---|
| G1 PBO | **FAIL 0.643** | **FAIL 0.762** | **FAIL 0.746** |
| G2 DSR p | FAIL 0.241 | FAIL 0.468 | FAIL 0.604 |
| G3 WF | PASS 7/8 | PASS 7/8 | PASS 7/8 |
| G4 OOS Sh | PASS +0.562 | PASS +0.233 | PASS +0.181 |
| G5 FWD Sh | PASS +0.483 | PASS +0.483 | PASS +0.419 |
| G6 boot CI | PASS +0.250 | PASS +0.154 | **FAIL −0.001** |
| G7 xlib pp | PASS 0.071 | PASS 0.028 | PASS 0.037 |

**G1 PBO failure on ALL 3 datasets.** With only 3 configs, PBO has
high variance (library warns `N<4`), but the FAIL direction is
consistent. The momentum-overlay configs produce very different return
streams (gate_on 78-91%, transitions 44-163), so the IS-best vs
OOS-best rank-reversal is genuine, not grid-floor noise.

**G6 bootstrap ndx_real CI low = −0.001** — almost exactly at zero,
and fails narrowly. This is new: iter 006 ndx was +0.175 on G6. The
overlay shaves enough Sharpe off ndx that the bootstrap distribution
now straddles zero.

**G7 cross-lib parity 0.028-0.071 pp** on all 3 — engine is clean. The
compound (blend × overlay) numpy reference agrees with the pandas
engine within 7 bp of annualised CAGR. Well under the 3 pp gate.

## What worked

1. **TDD discipline held.** 11 new specs in
   `tests/test_momentum_overlay.py` covering gate canonical form,
   look-ahead protection, warmup, gate transitions, and overlay
   integration. All 11 passed on first green. Baseline pytest went
   from 718 pass + 5 skip (post iter 006) to 729 pass + 5 skip (post
   iter 007), no regressions.

2. **Engine cross-library parity (G7).** The compound mechanism's
   pandas engine matches the hand-rolled numpy reference within 0.03-
   0.07 pp CAGR across all 3 datasets — cleaner than iter 006 (which
   hit 0.03-0.05). The overlay bookkeeping (gate shift, zero-out
   positions on gate=0, cost recomputation on overlaid positions)
   is correctly implemented.

3. **MDD reduction on all 3 datasets.** The gate DOES sidestep some
   of the worst drawdown paths: 35.15% / 35.15% / 35.84% vs iter 006's
   40.10% / 37.21% / 37.21%. 2-5 pp improvement. This is the only
   positive finding — the overlay finds real regime information, but
   the volatility-feedback blend has already captured most of it.

## What didn't work (and why)

1. **Momentum overlay is redundant with variance-scaling on the blend**.
   The iter 006 blend already deploys less in high-vol regimes (by
   construction: `scale = target_vol² / σ²_port`). High-volatility
   regimes are correlated with trend-negative regimes (Gayed's
   volatility-regime finding, `[leverage_for_the_long_run, p.9]`: SPY
   below 200d MA exhibits 2-3× the above-MA volatility). So when the
   momentum gate turns OFF, the vol-scaling has already cut exposure
   30-70%. Adding a gate on top forces exposure to zero, giving up
   the residual positive expected return on the remaining small
   allocation, at the cost of transaction-cost churn on the gate
   flips. Net-negative.

2. **Transaction-cost friction on gate flips.** `mom252_skip21`
   produces 44-70 gate transitions per dataset. Each flip at full
   blend scale (~1.5-2.0 gross) costs 2 bps × 2 legs × 1.5-2.0 = 6-8
   bps. 70 flips × 7 bp = ~50 bp of CAGR over 24y. Small in absolute
   terms, but the marginal CAGR loss is NOT offset by a matching
   Sharpe gain because the overlay removes both good and bad regime
   information.

3. **Asset-class asymmetry: ndx_real hurts most.** QQQ+TLT loses
   −0.149 Sharpe vs iter 006 — 2.5× more damage than spy_real's
   −0.059 and 10× more than educational's −0.013. This suggests the
   momentum signal on QQQ (tech-heavy, higher idiosyncratic vol) is
   more noise-polluted than on SPY. Canonical 12-1 was validated on
   diversified indices; QQQ is effectively a sector bet and
   time-series momentum on sectors is known to be weaker than on
   market aggregates (`[stocks_on_the_move, p.70-77]` finds
   single-name momentum is stronger than sector-basket momentum).

4. **G1 PBO failed on all 3 datasets.** Even with the grid pre-committed
   to 3 ex-ante cfgs (not a sweep), the 3 return streams are different
   enough (gate_on 78%/81%/92% on spy) to let IS/OOS rank-reversal
   dominate PBO. This confirms iter 006's grid-design principle:
   blend-mechanism grids are intrinsically PBO-unstable.

5. **KILL #1 triggered on both real-data slots.** The pre-committed
   falsification condition (Sharpe ≤ iter 006 on BOTH spy and ndx)
   fires clearly. Hypothesis at the edge-compounding axis is rejected.

## Main lesson (for future iterations)

**Time-series momentum overlay is redundant with variance-scaling on a
vol-managed blend.** Both mechanisms target the same underlying
information — equity-regime volatility. Moreira-Muir Table IV's
vol-managed × momentum Sharpe uplift does NOT replicate when the base
mechanism is already a vol-managed BLEND (not a vol-managed single
asset). The 2-asset blend's inverse-variance weighting + portfolio
variance-scaling together capture the regime dimension that a 12-1
momentum gate would otherwise add.

**The productive path is orthogonal signals, not correlated signals.**
Anything that tracks volatility (EMA, SMA, VIX, time-series momentum,
drawdown filter) is already mostly captured by the iter 006 mechanism.
Candidates that *would* add a truly independent edge axis:

- **Cross-sectional momentum across BASKETS** (e.g., SPY vs TLT vs GLD
  vs commodities) — instead of gating a fixed blend, *rotate* weights
  toward the best-performing basket. Different mechanism.
- **Carry / yield curve state** — TLT's own roll yield and the
  term-spread slope are NOT captured by SPY's volatility. Adding a
  carry signal to the SPY-bond allocation is orthogonal to variance
  scaling.
- **Sentiment / flow data** — EBP spreads, options skew, survey data.
  These track credit-market and behavioural regimes, which are
  partially decoupled from realised volatility on price alone.
- **Meta-labeling** (AFML ch.3) — instead of adding a signal that
  *removes* a deploy decision, train a secondary model to predict
  *which bars the iter 006 blend signal will be profitable on*. This
  acts on the same decisions but from a different information source
  (e.g., cross-sectional features, macro regime features). This
  remains untested.

## Structural dead-ends discovered

Append to `DEAD_ENDS.md`:

- **Time-series momentum overlay (12-1 / 6-1 / 18-1) on vol-managed
  2-asset blend** reduces Sharpe by 0.01-0.15 on real data (educational
  / spy_real / ndx_real respectively). Redundant with
  variance-scaling's regime sensitivity. Do not re-test with different
  momentum lookbacks, thresholds, or skip values on the same base
  mechanism. The compounding path requires an *orthogonal* signal, not
  a correlated one.
- **G1 PBO instability on 3-config ex-ante grids of the vol-managed
  blend × signal family** — PBO 0.64-0.76 across all 3 datasets with
  3 pre-declared configs. The overfit-sensitivity is intrinsic to the
  compound, not to grid search. This confirms iter 006's insight
  that blend-mechanism grids have IS/OOS rank-reversal even when the
  grid is ex ante.

## Citations used

**Primary (hypothesis anchors)**:

- `[ml_for_algo_trading, ch.4 p.86]` — RULE: 12-month return EXCLUDING
  most recent month (skip-a-month) to avoid short-term reversal.
- `[algo_trading_chan, p.133, p.156-157, p.164, ch.6]` — time-series
  momentum; lookback=252 anchored to Moskowitz-Ooi-Pedersen (2012).

**Supporting**:

- `[leverage_for_the_long_run, p.7 footnote 12, p.9]` — Grinblatt-
  Moskowitz autocorrelation; SPY below-MA vol is 2-3× above-MA vol.
  Iteration 007's empirical finding confirms this asymmetry IS already
  captured by the iter 006 vol-scaling.
- `[evidence_based_ta, p.398]` — MLM Index uses 12-month MA on 25
  commodities; simple trend benchmark.
- `[risk_parity, p.10-11, ch.1]` — naïve risk parity (iter 006 base).
- `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 cap.
- `[advances_fin_ml, p.162-164, p.208-211, p.222-223, p.196-202,
  p.31-34]` — σ̂_{t-1} lag, G1 PBO, G2 DSR, G6 bootstrap, G7 cross-lib.
- `[stocks_on_the_move, p.70-77]` — single-stock momentum > sector
  momentum (informs the ndx_real > spy_real asymmetry).

**Web / external**:

- **Moreira & Muir (2017).** *JoF* 72(4), 1611-1644. DOI
  [10.1111/jofi.12513](https://onlinelibrary.wiley.com/doi/10.1111/jofi.12513).
  Table IV vol-managed × momentum Sharpe uplift **does NOT replicate**
  on a vol-managed blend — empirical finding of iter 007.
- **Moskowitz, Ooi & Pedersen (2012).** *JFE* 104(2), 228-250. DOI
  [10.1016/j.jfineco.2011.11.003](https://doi.org/10.1016/j.jfineco.2011.11.003).
  12-month canonical lookback validated across 58 instruments.
- **Jegadeesh & Titman (1993).** *JoF* 48(1), 65-91. DOI
  [10.1111/j.1540-6261.1993.tb04702.x](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x).
  Original momentum anomaly paper; skip-a-month protocol.

## Next iteration suggestions

Three structurally different directions, ordered by information gain:

1. **[PICK FIRST — cheapest verification] Single pre-committed iter
   006 blend cfg, no grid (Option A from iter 006 final_report)**.
   `vt15_L21_cap20` on all 3 datasets, zero overlay, zero sweep.
   Eliminates G1 PBO entirely (PBO undefined for N=1) and gives back
   the gate slot that iter 006 + iter 007 both lost. Only +3 n_trials.
   Tests whether the blend edge is grid-selected or structural. If
   blend edge survives without grid, score should climb to 75-85
   (STRONG tier) by recovering criterion 2's PBO points.

2. **Carry signal (term spread) overlay on the iter 006 blend**.
   Instead of a correlated signal (momentum), use term-spread slope
   as the regime signal (`[ilmanen_expected_returns]` if available,
   otherwise T10Y3M macro data in `data/external/macro/`). Term spread
   inversions historically precede recessions 6-18 months ahead —
   distinct information from realised volatility. Sharpe uplift is
   uncertain, but directly tests the "orthogonal signal" lesson.

3. **Meta-labeling on iter 006 blend signal (AFML ch.3)**.
   Train a secondary model to predict bar-level profitability of the
   iter 006 deploy decision using cross-sectional features (equity
   returns across sectors, bond sector spreads, macro state
   variables). This is structurally different from both iter 006
   (deploy always per blend rule) and iter 007 (deploy if trend > 0);
   the filter is data-driven, not rule-driven, and uses features the
   blend cannot see.

Option 1 is the verification step iter 006 explicitly pointed to;
Option 2 is the highest-information orthogonal-signal test; Option 3
is the most complex but also the most structurally novel.

## Baseline pytest

- Before iter 007: 718 passed + 5 skipped (after iter 006).
- After iter 007: **729 passed + 5 skipped** (added 11 TDD specs in
  `tests/test_momentum_overlay.py`, no other test changes). No
  regressions. Baseline green.

## Configuration tested (full grid)

- **Blend base (pre-committed)**: `vt15_L21_cap20` — target_vol=0.15,
  lookback=21, max_leverage=2.0 (iter 006 spy_real / ndx_real top).
- **Overlay grid**:

  | cfg_id | lookback | skip | semantics |
  |---|---|---|---|
  | `mom252_skip21` | 252 | 21 | 12-1 canonical (Jegadeesh-Titman / Moskowitz-Ooi-Pedersen) |
  | `mom126_skip21` | 126 | 21 | 6-1 shorter trend |
  | `mom378_skip21` | 378 | 21 | 18-1 longer trend |

- **Signal**: per-dataset equity leg adjusted close (SPY for
  educational + spy_real, QQQ for ndx_real).
- **Threshold**: 0 on all 3 (binary gate `mom > 0 → deploy, else cash`).
- **Cost model**: 2 bps per unit of per-leg position change
  (identical to iter 006).

**Grid size**: 3 configs × 3 datasets = **9 new trials**. Cumulative
n_trials advance: 4228 → **4237**.
