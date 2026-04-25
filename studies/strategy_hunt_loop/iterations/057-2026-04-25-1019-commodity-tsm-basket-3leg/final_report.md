# Iteration 057 — Final Report

## Verdict
🥈 **PROMISING** — score **64/100**, winner_conditions_met=**False**, **4/6 kills fired** → hypothesis **FALSIFIED**.

The diversification premise (corr<0.50 with iter 046) was vindicated
across all 3 datasets (corr 0.30/0.32/0.30 — even lower than iter 049's
gold-TSM corr ≈ 0.50). However, the multi-commodity TSM basket's
**absolute Sharpe is too low** to compound the iter 046 base at w=0.20:
basket Sharpe 0.13/0.16/0.29 vs iter 046's 1.32/1.38/1.18. Markowitz
dilution at unequal Sharpes drags the combined Sharpe by 0.16-0.24
across all datasets and CAGR by 1.0-1.6 pp, which collapses both DSR
worst-p (0.041 → 0.186-0.223; G2 fails on all 3) and CAGR floor
(c4 = 0/15 — same gap as iter 046). Net score regresses from iter 046's
85 STRONG to 64 PROMISING — even below iter 050's 78 (gold TSM at w=0.10).

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen, Δ046) | CAGR (Δ046) | MDD (Δ046) | gates | DSR p |
|---|---|---|---|---|---|
| educational | 1.0473 (+0.367, **−0.155**) | 8.10% (**−1.06pp**) | 15.78% (**−2.19pp** ✓) | 6/7 | 0.186 ❌ |
| spy_real    | 1.0820 (+0.182, **−0.241**) | 7.87% (**−1.58pp**) | 10.53% (**−4.69pp** ✓) | 6/7 | 0.223 ❌ |
| ndx_real    | 1.1440 (+0.189, **−0.237**) | 8.22% (**−1.54pp**) | 11.24% (**−3.33pp** ✓) | 6/7 | 0.178 ❌ |

Standalone commodity-TSM basket metrics (USO+UNG+SLV equal-weight,
boolean trend, 90d lookback): Sharpe 0.29/0.13/0.16, CAGR 3.47/0.86/1.31%,
MDD 49.8% (oil bear 2014-2020 dominates).

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | All 3 datasets beat frozen bench by ≥ 0.10 (Δ +0.367/+0.182/+0.189) |
| 2 Gates | **19** | 25 | 6/7 each (G2 DSR fails 3/3); cross-dataset bonus +4 |
| 3 DSR | **0** | 15 | Worst-p 0.223 ≥ 0.20 cutoff; n_trials=4327 |
| 4 CAGR floor | **0** | 15 | edu 8.10% < 9.18%; spy 7.87% < 11.98%; ndx 8.22% < 15.35% |
| 5 MDD ceiling | **15** | 15 | All 3 well under bench+5pp (15.78/10.53/11.24%) |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive (3-window split per dataset) |
| **total** | **64** | **100+5** | tier: **PROMISING** |

## Configuration tested

```python
CFG = {
    "cfg_id": "iter046_plus_commodity_tsm_w020",
    "w_046": 0.80,                       # iter 046 base = 0.5 iter 041 + 0.5 iter 039
    "w_csm": 0.20,                       # commodity TSM basket
    "tsm_universe": ["USO", "UNG", "SLV"],
    "lookback": 90,
    "rf": 0.02,
    "cost_bps": 5.0,
}
```

Effective top-level weights: 0.40 iter 041 + 0.40 iter 039 + 0.20
commodity-TSM-basket. All hyperparameters pre-committed; no grid sweep.
cumulative_n_trials advance: 4326 → 4327 (+1).

## Pre-committed kills

| # | kill | fired? | observation |
|---|---|---|---|
| A | Sharpe regress vs iter 046 by ≥0.05 on ≥2 datasets | ❌ **FIRED** | 3/3 datasets dropped (Δ −0.155/−0.241/−0.237) |
| B | DSR worst-p ≥ 0.041 (iter 046 edu baseline) | ❌ **FIRED** | iter 057 worst-p = 0.223 (5.4× iter 046 edu) |
| C | CAGR regress by ≥1.0pp on ≥2 datasets | ❌ **FIRED** | 3/3 datasets dropped (Δ −1.06/−1.58/−1.54 pp) |
| D | Score < 78 (iter 050 baseline) | ❌ **FIRED** | 64 < 78 — multi-commodity is strictly worse than gold TSM at this overlay weight |
| E | G7 cross-lib > 3 pp | ✓ clean | Δ = 0.0000 pp on all 3 (numpy ref ≡ pandas exact) |
| F | corr(r_csm, r_046) > 0.50 | ✓ clean | Max corr = 0.319 (orthogonality vindicated) |

4 of 6 kills fired ⇒ hypothesis refuted by pre-committed criteria. The
two clean kills (E, F) are the **structural findings**: the engine is
correct AND the cross-asset orthogonality premise is real — non-gold
commodities truly have low correlation with the SPY/IEF/GLD regime
stack and short-equity-vol harvest. The failure mode is **absolute
Sharpe of the third stream**, not its correlation.

## What worked / what didn't

**Worked**:

- **Engine + numpy reference**: G7 = 0.0000 pp on all 3 datasets, exact
  parity between pandas and pure-numpy implementations
  (`[advances_fin_ml, p.31-34]`). 16/16 TDD tests pass.
- **Orthogonality premise**: corr(r_csm, r_046) ≈ 0.30 across all 3
  datasets — much lower than iter 049's gold-TSM corr ≈ 0.50. Removing
  gold from the basket DID make the stream more orthogonal as predicted
  (`[risk_parity, ch.5]` cross-asset diversification thesis).
- **MDD reduction**: combined MDD 15.78/10.53/11.24% vs iter 046's
  17.97/15.22/14.57% — improvements of −2.2/−4.7/−3.3 pp. The
  diversifier IS working at the variance-reduction layer; portfolio
  drawdowns shrink because commodity TSM's bear-market tail is
  uncorrelated with iter 041/039 stress.
- **Robustness 5/5**: 9/9 sub-windows positive (Sharpe > 0). The
  combined stream is positive in every third of every dataset.

**Didn't**:

- **Commodity-TSM Sharpe is structurally too low for this regime**:
  USO TSM 0.13-0.29, UNG TSM ≈ 0, SLV TSM 0.10-0.20. Post-2014 oil/gas
  bear market dominated; only silver had marginal positive trend
  (`[stocks_on_the_move, p.76-77]` — boolean trend is binary, can't
  exploit gentle reversals). MOP 2012's reported commodity TSM Sharpe
  0.30-0.50 was on a pre-2010 sample with strong trend regimes; our
  2007-2026 window is mostly chop.
- **Markowitz dilution at unequal Sharpes** (iter 049's lesson
  generalises): combined Sharpe = (w_46 × S_46 + w_csm × S_csm) /
  σ_combined. With S_46 ≈ 1.30 and S_csm ≈ 0.20, σ_combined ≈ 0.91
  (corr 0.30, w 0.80/0.20), so combined Sharpe ≈ (0.80×1.30 + 0.20×0.20)
  / 0.91 ≈ 1.16 — drag of −0.14 vs iter 046's 1.30. This matches the
  observed drag of 0.16-0.24.
- **DSR penalty inverts the diversification benefit**: iter 046 had
  DSR worst-p 0.041 because Sharpe was high relative to noise floor.
  iter 057's lower combined Sharpe (1.05-1.14) lands in the noise band
  at n_trials=4327, blowing up worst-p from 0.041 → 0.18-0.22. The
  variance-reduction win (lower σ) is overwhelmed by the mean-dilution
  loss — DSR is roughly Sharpe-monotonic at fixed n_trials.
- **CAGR drag closes the 90-target path**: iter 046's c4=0/15 was the
  sole gap to 90 (edu 0.02pp short of floor); adding commodity TSM
  pushes ALL THREE further below floor (8.10% vs 9.18% edu floor; spy
  7.87% vs 11.98%; ndx 8.22% vs 15.35%). The 90 ceiling on iter 046
  family is locked behind CAGR floor, and any weight allocated to a
  low-CAGR diversifier strictly worsens it.

## Main lesson (for future iterations)

**Out-of-family addition compounds DSR only when the third stream's
absolute Sharpe is comparable to the base's (not just its correlation
that matters).** iter 045 (corr 0.58, S_037 ≈ S_039) → 81. iter 046
(corr 0.41, S_041 ≈ S_039) → 85. iter 049/050 (gold TSM corr ≈ 0.50,
S_gold ≈ 0.45) → 59 at w=0.50, 78 at w=0.10. iter 057 (commodity-basket
corr ≈ 0.30, S_csm ≈ 0.20) → 64 at w=0.20.

The Pareto frontier across "third stream + iter 046" experiments shows:
**lower correlation alone does NOT compensate for lower absolute Sharpe**.
The rough rule emerging: third stream needs Sharpe ≥ 0.5 (preferably
≥ 0.7) for a Markowitz-positive contribution at any practical weight.
Commodity TSM in the post-2010 sample doesn't clear this bar.

This closes the **multi-commodity TSM as 3rd-stream** axis on iter 046
family at the data-availability level: USO/UNG/SLV are the only
commodity ETFs with full 2007+ coverage, none individually clear S=0.5,
and the basket's diversification doesn't lift the mean.

## Structural dead-ends discovered

- **Multi-commodity TSM basket (USO+UNG+SLV) at w=0.20 as 3rd stream
  on iter 046 (closed by iter 057 at score 64 PROMISING vs iter 046's 85)**:
  Combined Sharpe 1.05/1.08/1.14 (Δ046 −0.155/−0.241/−0.237 pp); DSR
  worst-p 0.186/0.223/0.178 (vs iter 046 0.041/0.042/0.031, 4-7×
  regression); CAGR 8.10/7.87/8.22% (Δ046 −1.06/−1.58/−1.54 pp); MDD
  improves 2-5pp. Correlation premise vindicated (corr 0.30 average,
  much lower than gold-TSM's 0.50) but absolute Sharpe of standalone
  commodity-TSM basket (0.13-0.29) is too low to add value at any
  practical weight — Markowitz dilution at unequal Sharpes dominates
  variance-reduction benefit. Closes axis on diversified non-gold
  commodity TSM at iter 046 base; confirms iter 049/050's lesson that
  3rd-stream-Sharpe is the binding constraint, not correlation.

## Citations used

- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 risk-parity
  stack (iter 041 base architecture, preserved verbatim)
- `[volatility_trading, p.218]` — Sinclair 2013 cross-asset VRP
  (iter 039 base architecture, preserved verbatim)
- `[systematic_trading]` — Carver TSM single-asset boolean trend rule
- `[stocks_on_the_move, p.76-77]` — Clenow boolean trend filter
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (4327)
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (numpy ref)
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1)
- `[advances_fin_ml, ch.17-18]` — regime detection (iter 041 VIX gate)
- Moskowitz-Ooi-Pedersen (2012), JFE 104(2) 228-250,
  DOI 10.1016/j.jfineco.2011.11.003 — TSM canonical reference
- Asness-Moskowitz-Pedersen (2013), JoF 68(3) 929-985,
  DOI 10.1111/jofi.12021 — value/momentum everywhere; commodity TSM
- Erb-Harvey (2006), FAJ 62(2) 69-97,
  DOI 10.2469/faj.v62.n2.4084 — commodity premia / roll yield
- Markowitz (1952), JoF 7(1) 77-91 — convex combination minimum-variance
- Whaley (2009), JPM 35(3), DOI 10.3905/JPM.2009.35.3.098 — VIX
- Bondarenko (2014), QJF 4(3) 1450015 — empirical SPX VRP

## Next iteration suggestions

Three structurally distinct directions (the current iter 057 closure
points at the **third-stream-Sharpe** axis as the next binding
constraint):

1. **Higher-Sharpe credit-carry third stream (HYG long-only with
   trend filter)**: HYG has 2007+ coverage, ~6-7% gross yield, and
   structurally positive Sharpe in non-stress regimes. A 60d boolean
   trend filter avoids the 2008/2020 stress drawdowns. Expected S_csm
   ≈ 0.5-0.7, corr with iter 046 ≈ 0.5-0.7 (HYG is somewhat equity-
   correlated). At w=0.10-0.15 may unlock CAGR floor ≥ 9.18% on edu.
   Cite Asvanunt-Richardson 2017 JPM 43(2) "The Credit Risk Premium" +
   `[risk_parity, ch.5]`. Predicted 75-85.

2. **T10Y3M-only regime gate as iter 041 alternative (BASE_MEMORY
   direction #2)**: single-feature forward-looking regime gate
   (12-month lead-time per Estrella-Mishkin 1998 NBER 6649) on the
   SPY+IEF+GLD stack at preserved 1.4-1.5× leverage. Distinct from
   iter 044 (closed 2-feature composite VIX+T10Y3M). Building a fresh
   84-ceiling family with different timing properties opens a new
   composition stream pair: iter 041_VIX + iter 057_T10Y3M may have
   even lower correlation than iter 041 + iter 039. Predicted 76-84.

3. **Minimum-variance weights on iter 041 + iter 039 + low-vol
   stream**: take iter 046's saved (r_041, r_039) pair and solve for
   w_041, w_039, w_third Markowitz min-variance using the empirical
   covariance, with constraint Σw = 1, w ≥ 0. The third stream
   candidate must be SELECTED post-hoc to minimise estimated worst-p
   (n_trials=4327). Risk: implicit grid search across third-stream
   universe inflates n_trials → DSR penalty. Cite `[advances_fin_ml,
   p.31-34]` for the n_trials accounting discipline. Predicted only
   meaningful if a proper out-of-sample validation is built in.
