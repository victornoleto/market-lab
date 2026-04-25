# Iteration 034 — Final Report

## Verdict
🥈 **PROMISING** (score **72/100**, winner_conditions_met=False, **1/6 KILLS — Kill C only**)

The bond-carry sleeve at α=0.2 (3-leg static stack 0.9 SPY + 0.4 IEF
+ 0.2 TLT, total bond notional preserved at iter 015's 0.6) **beats
iter 015 on Sharpe across all three datasets** (Δ +0.011/+0.014/+0.012)
and **beats iter 033 on Sharpe across spy_real and ndx_real** (Δ
−0.055/+0.021/+0.011), but the uplift is too small (~0.01) to move
DSR worst-p below the 0.20 kill threshold at n_trials = 4291. The
single kill that fired is the same one that bound iter 032 and iter
033 — DSR.

This iteration ties iter 032 and iter 033 byte-for-byte at score 72
from yet another bond-axis path: composition (032), substitution
(033), and now **zero-net-notional spread (034)**. Three different
mechanisms, three different DSR-bound 72/100 results. The iter 015
plateau at 77 is now **definitively confirmed** as the efficient
frontier of the bond-axis variation family on a static stack.

---

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen) | CAGR (Δ frozen) | MDD (Δ frozen) | gates |
|---|---|---|---|---|
| educational | 0.7948 (+0.115 vs 0.68) | 12.47% (+1.00pp vs 11.47%) | 43.78% (−11.36pp vs 55.14%) | **5/7** |
| spy_real | 1.0580 (+0.158 vs 0.90) | 15.71% (+0.74pp vs 14.97%) | 33.05% (−0.65pp vs 33.70%) | **6/7** |
| ndx_real | 1.0753 (+0.120 vs 0.955) | 19.48% (+0.30pp vs 19.18%) | 42.11% (+6.99pp vs 35.12%) | **6/7** |

| dataset | Δ vs iter 015 | Δ vs iter 033 |
|---|---|---|
| edu Sharpe | **+0.011** ✓ | −0.055 |
| spy Sharpe | **+0.014** ✓ | +0.021 |
| ndx Sharpe | **+0.012** ✓ | +0.011 |
| edu MDD | **−0.71pp** ✓ | +1.18pp |
| spy MDD | +2.73pp | **−5.42pp** ✓ |
| ndx MDD | +2.60pp | **−4.93pp** ✓ |

Cross-dataset Sharpe edge (frozen): **3/3 datasets ≥ +0.10** —
criterion 1 maxes out at 25/25.

---

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | edu/spy/ndx all beat frozen bench by ≥ +0.10 (Δ +0.115/+0.158/+0.120); 3/3 includes the +5 cross-dataset bonus |
| 2 Gates | **17** | 25 | edu 5/7 → 3 pts; spy 6/7 → 5 pts; ndx 6/7 → 5 pts; cross-dataset bonus +4 (all meet thresholds) |
| 3 DSR | **0** | 15 | worst-p **0.5291** (educational, n_trials=4291); spy 0.2500, ndx 0.2531 — Sharpe ~1.06 too low to clear DSR penalty at this n_trials |
| 4 CAGR floor | **15** | 15 | all 3 datasets ≥ 0.8 × frozen CAGR benchmark |
| 5 MDD ceiling | **10** | 15 | edu 43.78% ≤ 60.14% ✓; spy 33.05% ≤ 38.70% ✓; ndx 42.11% > 40.12% ✗ (breach +1.99pp) |
| 6 Robustness bonus | **5** | 5 | 9/9 sub-windows Sharpe > 0 across 3 datasets |
| **total** | **72** | **100** + 5 | tier: **🥈 PROMISING** |

Strict winner conditions: 4/5 met (Sharpe edge 3/3, CAGR floor 3/3,
MDD ceiling 2/3, gates cross-ds met). Only condition 3 (DSR p<0.05)
fails — same single missing condition as iter 015/032/033.

Pre-committed kills (iter 034 hypothesis): **1/6 fired** — Kill C
(DSR worst-p > 0.20). Kills A (Sharpe regress vs iter 015), B (ndx
MDD > 45%), D (G7 cross-lib), E (score < 60), F (robustness < 7/9)
all clean.

---

## Configuration tested

Single pre-committed cfg `ntsx_synth_90_spy_40_ief_20_tlt`:

| param | value |
|---|---|
| equity weight | 0.90 (NTSX prospectus) |
| bond_short weight (IEF, 7-10y) | 0.40 |
| bond_long weight (TLT, 20-30y) | 0.20 |
| total bond notional | 0.60 (preserves iter 015 verbatim) |
| total leverage | 1.50 (preserves iter 015/033 verbatim) |
| rebalance | daily |
| cost_bps_per_leg | 0.0002 |
| funding cost | NOT modeled (synthetic) |
| α (TLT fraction of bond sleeve) | 0.20 (midpoint of {0.1, 0.2, 0.3}) |

Cross-library parity: ≤ 0.087 pp CAGR delta on all 3 datasets
(threshold 3 pp, max observed in ndx_real). G7 PASS 3/3.

Leg correlations (spy_real window):

- ρ(SPY, IEF) = −0.265
- ρ(SPY, TLT) = −0.295
- ρ(IEF, TLT) = +0.916 (high inter-treasury correlation as
  predicted; supports the spread-vol-low argument)

---

## What worked / what didn't

**What worked.** The variance-controlled sleeve hypothesis from
BASE_MEMORY's iter 033 lesson held empirically: sleeve bond-leg vol
(0.4 IEF + 0.2 TLT) lands at ~5.4% (vs iter 033's 8.4% for 0.6 TLT
alone), preserving iter 015's risk profile while still capturing
some long-end term premium. The MDD on **ndx_real improved from
47.04% (iter 033) to 42.11% (iter 034)** — a 4.93pp reduction — and
on **spy_real from 38.47% to 33.05%** (5.42pp). The Sharpe-Δ
relative to iter 015 is positive on ALL three datasets (no kill A
firing despite the Sharpe gain being small), confirming the spread
adds **non-negative** Sharpe value at this α.

**What didn't.** The Sharpe uplift from the spread is **too small**
(+0.011 / +0.014 / +0.012 — about a third of what would shift DSR).
DSR worst-p stays at 0.529 on educational, far above the 0.05
acceptance threshold and even further above iter 034's pre-committed
0.20 kill. The TLT slice contributes ~0.3pp of CAGR (per ndx Δ vs
iter 015) but absorbs proportional variance, so the per-trial
Sharpe is statistically indistinguishable from iter 015 at
n_trials=4291. The ndx MDD breaches the +5pp ceiling by ~2pp because
2022 was uniquely punishing for any bond exposure (rates spiked
+450bps while QQQ drew down 33%).

**A quiet structural win.** Three iterations on the bond axis
(032 composition, 033 substitution, 034 spread sleeve) all converge
at score 72 PROMISING with identical cause (DSR), via three
qualitatively different mechanisms. That coincidence is itself a
finding: at n_trials ≥ 4288 and Sharpe ≤ 1.10, **the bond-axis
variation family on a static iter 015 base is now empirically
exhausted on the DSR criterion**. No tweaking of bond duration,
bond mix, or bond carry sleeve will produce a winner without a
fundamentally different mechanism.

---

## Main lesson (for future iterations)

**Bond-axis variations on the static iter 015 base are CLOSED.**
Three structurally-distinct mechanisms (full-duration substitution,
layered VRP composition, zero-net-notional duration spread) each
extract roughly the same Sharpe-equivalent diversification per unit
of variance — converging to the same 72 PROMISING ceiling, all
DSR-bound. The variance-control argument that motivated iter 034
(sleeve vol < full-substitution vol) is **vindicated empirically**
(MDD improvements 5pp+ on real datasets) but **does not translate
into Sharpe gains big enough to move DSR** at the current n_trials
budget. Iter 015 plateau at 77 is the definitive bond-axis ceiling.

Future iterations must move to **distribution-orthogonal axes**:
FX carry (Lustig-Verdelhan 2007), cross-asset VRP on a different
underlying (IWM small-cap), commodity carry (KMPV 2018 §3.3), or
**non-static architectures** (regime-aware, ML meta-label,
cross-sectional factor timing). Within-bond-sleeve variations are
no longer worth iterating budget on — the marginal Sharpe gain is
exhausted.

---

## Structural dead-ends discovered

**iter 034 (PROMISING 72) — bond-carry sleeve at preserved notional**:
3-leg static stack `0.9 SPY + 0.4 IEF + 0.2 TLT` (zero-net-notional
duration spread inside iter 015's 0.6 bond sleeve). Variance
hypothesis vindicated (MDD ndx improves 5pp vs iter 033, spy
improves 5pp vs iter 033) but Sharpe uplift +0.011/+0.014/+0.012 vs
iter 015 too small (~0.3 of DSR-shifting magnitude) to move DSR
worst-p below 0.20 at n_trials=4291. Score-tied byte-for-byte with
iter 032 (composition) and iter 033 (full substitution). Closes:
**all bond-axis static-stack variations** at preserved or perturbed
total bond notional. Open: cross-asset axes (FX, equity index VRP,
commodity carry), non-static architectures.

---

## Citations used

**Primary**: `[risk_parity, ch.5]` — bond term-premium decomposition
for the diversifying leg of a levered stack.

**Supporting**:
- `[risk_parity, p.5, p.10-11, ch.1]` — Asness-Frazzini-Pedersen
  (2012) risk-parity static stack (preserved from iter 015).
- `[leverage_for_the_long_run, p.19-20]` — leverage on diversified
  base captures duration risk-premium without market-timing.
- `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
- `[advances_fin_ml, p.222-223]` — DSR cumulative n_trials.
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6.
- Asness, Frazzini & Pedersen (2012). *FAJ* 68(1). SSRN 1728082.
- **Koijen-Moskowitz-Pedersen-Vrugt (2018). "Carry."** *JFE*
  127(2): 197-225. DOI 10.1016/j.jfineco.2017.11.002. Cross-sectional
  bond carry within asset class — the canonical primary citation
  for the spread (TLT − IEF) framing.
- **Cochrane & Piazzesi (2005). "Bond Risk Premia."** *AER* 95(1).
  DOI 10.1257/0002828053828581. Forward-rate-loading concentration
  in long end of yield curve.
- **Ilmanen (2011). *Expected Returns.*** Wiley, ch.6-7. Term
  premium and bond carry empirical magnitudes.
- WisdomTree NTSX prospectus — 90/60 weights (preserved verbatim).

---

## Next iteration suggestions

The bond axis is now empirically closed at PROMISING 72 from three
different mechanism paths. Iter 035 should pivot to a structurally
new axis. Three candidate directions, ordered by expected
information yield:

1. **F-FX FX carry overlay** on iter 015 base (`AUDUSD long, USDJPY
   short`). FX carry is **distribution-orthogonal to equity beta** —
   it has its own crash pattern (carry trade unwinds in risk-off,
   but not synchronous with bond duration). Available data:
   `audusd.parquet` and `usdjpy.parquet` already in cache. Citation:
   Lustig-Verdelhan (2007), JFE 102(1); Burnside et al. (2011) RFS
   24(3). This is the most distribution-orthogonal mechanism that
   hasn't been touched yet.

2. **C-VRP IWM** (cross-asset VRP). Replace SPY 5/10% put credit
   spread (iter 026/031 architecture) with **IWM** (Russell 2000)
   put credit spread. Small-cap stress decorrelates from large-cap
   in some regimes (2022 IWM −36% vs SPY −25%); composite corr_SPY
   should drop from iter 032's 0.97. Citation: KMPV 2018 + AMP 2013.

3. **Non-static architecture** — required to clear DSR at this
   n_trials. Candidates: ML meta-label on iter 026 base
   `[advances_fin_ml, ch.3]`; HMM regime-aware leverage scaling on
   iter 015 base; cross-sectional factor timing across 5+ ETFs.
   Higher implementation cost but only path to Sharpe ≥ 1.30 cross-ds.

**Strongly de-prioritized**: any further bond-axis variation
(allocation timing, additional bond durations, ZROZ/EDV ultra-long,
bond spread α-sweep). The 72-score ceiling on this axis is now
established by three independent mechanisms — additional iterations
would only inflate n_trials without adding informational value.

**Implementation cost ranking** (lowest → highest):
- F-FX overlay: ~30-45 min (well-trodden iter-015-style adaptation
  with two new return streams; data already cached)
- C-VRP IWM: ~60-90 min (needs iter 026 architecture + IWM-specific
  put-spread modeling)
- Non-static: ~2-4 h depending on chosen architecture (regime/ML/CS)

Recommended pick for iter 035: **F-FX overlay** as the lowest-cost,
highest-orthogonality test. If F-FX scores ≥ 75 STRONG it opens a
new axis; if it scores < 65 PROMISING it joins the bond-axis lesson
and we move to non-static architectures with higher confidence in
the structural diagnosis.
