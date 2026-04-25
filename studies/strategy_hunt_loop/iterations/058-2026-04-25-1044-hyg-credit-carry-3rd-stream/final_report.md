# Iteration 058 — Final Report

## Verdict
🥇 **STRONG** — score **85/100** (frozen) / **90/100** (custom-bench),
**winner_conditions_met=False** (CAGR floor 0/3 — same gap as iter 046),
**0/6 kills fired**.

This is a **clean, kill-free upgrade** of iter 046 along the
third-stream-Sharpe axis predicted by iter 057's structural finding.
Replacing the failed multi-commodity TSM basket (S 0.13-0.29, score 64
PROMISING) with HYG long-only + 90d boolean trend filter (S
0.87/0.99/0.99 standalone) at the same w=0.10 weight produces:

- **Sharpe up** on every dataset: 1.22/1.35/1.40 vs iter 046 frozen
  baseline 1.20/1.32/1.38 (Δ +0.020/+0.025/+0.021).
- **MDD down** on every dataset: 16.74/13.71/13.12% vs iter 046
  17.97/15.22/14.57% (Δ −1.23/−1.51/−1.45 pp).
- **DSR worst-p still under 0.05**: 0.0494/0.0337/0.0258 — narrowly
  cleared the cumulative-n_trials hurdle (4328) on edu (0.0494 vs
  0.05 cutoff), comfortably on spy/ndx.
- **CAGR drops** 0.4-0.5 pp (8.69/9.01/9.27% vs 9.07/9.45/9.76%) —
  HYG_TSM standalone CAGR (4.75-5.08%) is below iter 046's, so adding
  it at any weight strictly worsens combined CAGR. **CAGR floor 0/3
  remains the sole gap to WINNER.**
- **Score +7 vs iter 050** (gold-TSM at w=0.10 → 78), **= iter 046
  score 85** at TOP-K #1.
- **Markowitz residual = 0.0000** on all 3 datasets — closed-form
  composition is exact at this weight.

The **structural finding from iter 049/050/057** ("3rd-stream Sharpe
≥ ~0.5 is the binding constraint, not correlation") is **vindicated
in the constructive direction**: HYG_TSM standalone Sharpe (~0.9 on
real data) is **higher than the iter 046 base**, and the addition is
Sharpe- and MDD-positive even though the correlation (0.38-0.48) is
worse than iter 057's commodity basket (0.30).

## Headline metrics (top candidate)

| dataset | Sharpe (Δ frozen, Δ046) | CAGR (Δ046) | MDD (Δ046) | DSR p | gates |
|---|---|---|---|---|---|
| educational | 1.2225 (+0.5425, **+0.0200**) | 8.69% (**−0.46pp**) | 16.74% (**−1.23pp** ✓) | **0.0494** ✓ | **7/7** |
| spy_real    | 1.3474 (+0.4474, **+0.0246**) | 9.01% (**−0.44pp**) | 13.71% (**−1.51pp** ✓) | **0.0337** ✓ | **7/7** |
| ndx_real    | 1.4027 (+0.4477, **+0.0213**) | 9.27% (**−0.49pp**) | 13.12% (**−1.45pp** ✓) | **0.0258** ✓ | **7/7** |

Standalone HYG_TSM metrics (for comparison): Sharpe 0.872/0.992/0.986,
CAGR 5.08/4.93/4.75%, MDD 17.64/6.72/6.72%, pct_long 73.6/76.2/75.6%
(stress periods correctly trimmed by the 90d trend filter).

## Score breakdown

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | **25** | 25 | All 3 datasets beat frozen bench by ≥ 0.10 (Δ +0.5425/+0.4474/+0.4477) |
| 2 Gates | **25** | 25 | 7/7 each (G1 PBO N=1 vacuous PASS) + cross-ds bonus +4 capped at 25 |
| 3 DSR | **15** | 15 | Worst-p 0.0494 < 0.05 cutoff; n_trials=4328 (vs iter 046's 0.042 at n=4311) |
| 4 CAGR floor | **0** | 15 | edu 8.69% < 9.18%; spy 9.01% < 11.98%; ndx 9.27% < 15.35% (HYG drag worsens vs iter 046) |
| 5 MDD ceiling | **15** | 15 | All 3 well under bench+5pp; **lower than iter 046 by 1.2-1.5 pp on each** |
| 6 Robustness | **5** | 5 | 9/9 sub-windows positive; min sub-window Sharpe 1.140 |
| **total** | **85** | **100+5** | tier: **STRONG** |

Custom-bench score: **90/100** (using HYG-aligned 2007+ benchmarks
where edu SPY Sharpe drops to 0.629 and CAGR to 10.82%, easing the
floor). Custom score still doesn't unlock WINNER tier because winner
conditions check uses the frozen benchmarks (per `scoring.py` strict
test), and CAGR floor 5pts still 0/15 on those.

## Configuration tested

```python
CFG = {
    "cfg_id": "iter046_plus_hyg_tsm_w010_lookback90",
    "w_046": 0.9,                       # iter 046 base = 0.5 iter 041 + 0.5 iter 039
    "w_hyg": 0.1,                       # HYG TSM long-only
    "hyg_ticker": "HYG",
    "lookback": 90,                     # boolean trend on trailing 90d return
    "rf": 0.02,
    "cost_bps": 5.0,
}
```

Effective top-level weights: 0.45 iter 041 + 0.45 iter 039 + 0.10
HYG_TSM. All hyperparameters pre-committed; no grid sweep.
cumulative_n_trials advance: 4327 → **4328** (+1).

## Pre-committed kills

| # | kill | fired? | observation |
|---|---|---|---|
| A | Sharpe regress vs iter 046 by ≥ 0.10 on ≥ 2 datasets | ✓ clean | Sharpe **UP** on all 3 (+0.020/+0.025/+0.021); inverse direction of kill |
| B | DSR worst-p ≥ 0.088 (2× iter 050's 0.0438) | ✓ clean | 0.0494 < 0.088 (within margin); barely clears 0.05 cutoff on edu |
| C | Score < 78 (iter 050 baseline) | ✓ clean | 85 ≥ 78; +7 over gold-TSM at same w=0.10 |
| D | Markowitz residual ≥ 0.05 on ≥ 2 datasets | ✓ clean | residuals −0.0000/+0.0000/−0.0000 (perfect closed-form) |
| E | G7 cross-lib > 3 pp | ✓ clean | 0.0000 pp on all 3 datasets |
| F | corr(r_hyg, r_046) > 0.85 | ✓ clean | avg 0.443 (max 0.477); HYG is genuinely diversifying |

**0/6 kills fired** ⇒ hypothesis fully supported. This is the
**first iter-046-family addition (047-058) where every kill fired
clean**: iter 047 fired 2/6, iter 048 3/6, iter 049 4/6, iter 050
1/6, iter 057 4/6.

## What worked / what didn't

**Worked**:

- **Higher-Sharpe 3rd stream IS the key** (iter 049/050/057 thesis
  vindicated): HYG_TSM Sharpe 0.87-0.99 vs gold-TSM 0.39-0.45 vs
  commodity basket 0.13-0.29 → score 85 vs 78 vs 64. Linear
  relationship between standalone 3rd-stream Sharpe and combined-
  stream score at fixed w=0.10.
- **Markowitz closed-form is empirically exact at this scale**
  (residual = 0.0000 across all 3 datasets, 4787-bar sample). The
  Sharpe identity from `[risk_parity, ch.5]` and Markowitz (1952)
  predicts the combined Sharpe to 4 decimal places given empirical
  μ, σ, ρ — no non-stationarity penalty observed.
- **MDD reduction holds AT a higher Sharpe**: combined MDD drops
  1.2-1.5 pp on every dataset while combined Sharpe rises. iter
  057 (commodity basket) achieved bigger MDD drops (2-5 pp) but at
  a Sharpe cost; iter 058 gets MDD drop **and** Sharpe up — the
  natural Pareto improvement we couldn't get with low-Sharpe
  diversifiers.
- **Trend filter avoids the 2008 + 2020 stress** as predicted by
  Asvanunt-Richardson 2017 §3: HYG_TSM pct_long is 73-76% on real
  data, with the 24-27% cash periods coinciding with credit-spread
  spikes (2008 Q4-2009 Q1, 2020 Q1, 2022 H2). Standalone HYG_TSM
  CAGR 4.75-5.08% (net of cost + cash drag) preserves the credit
  carry premium.
- **Engine + numpy reference**: G7 = 0.0000 pp on all 3 datasets,
  exact parity (`[advances_fin_ml, p.31-34]`). 15/15 TDD tests pass
  in 0.34s. Baseline pytest preserved (existing 92 collection
  errors are pre-iter-058, unaffected).

**Didn't**:

- **CAGR floor remains 0/15** — adding HYG_TSM at any positive weight
  strictly **lowers** combined CAGR because HYG_TSM standalone CAGR
  (4.75-5.08%) is below iter 046's CAGR (9.07-9.76%). Path to
  WINNER on the iter-046-family **requires a 3rd stream with
  standalone CAGR ≥ iter 046's (~9.5%/yr)** AND Sharpe ≥ 0.5. That
  combination is rare — most diversifying assets either have lower
  CAGR (bonds, gold, credit) or much higher correlation with equity.
- **Edu DSR p sits at 0.0494 (1.2% margin from cutoff)**: at
  cumulative_n_trials = 4328 the deflated p just clears, but a
  single additional grid-search trial in iter 059+ would push it
  back over 0.05 unless Sharpe rises further. The DSR runway on
  edu is the tightest constraint for follow-ups.
- **Custom-bench score 90 is a ceiling artefact, not a real
  WINNER**: the windowed SPY benchmark on edu (2007-04 → 2026-04)
  has a much lower Sharpe (0.629) than the frozen edu benchmark
  (0.68 on 1986-2026 SPYSIM synth) because it includes the 2008
  GFC drawdown in the sample. The custom-bench would mark iter
  046 itself as 85+5=90 too if HYG-windowing were applied to it.
  The strict-test scoring wisely uses frozen benchmarks for tier
  determination.

## Main lesson (for future iterations)

**The 3rd-stream-Sharpe binding constraint discovered by iter 049/
050/057 is now confirmed in the constructive direction**: when a
single-asset trend-filtered stream clears Sharpe ≥ ~0.7 and
correlation < 0.5, adding it at w=0.10 is a Pareto improvement on
every metric except CAGR (where the additive's standalone CAGR
matters more than its Sharpe).

The iter-046-family score-frontier is **bounded above by iter 046's
85 along the Sharpe/Gates/DSR/MDD axes** until a 3rd stream with
**both standalone Sharpe ≥ 0.7 AND standalone CAGR ≥ iter-046's
9.5%/yr** is found. Candidates from the literature:

- Levered HYG (3× borrow at retail rates 3-4%): doubles standalone
  Sharpe and roughly doubles CAGR but adds 3-4% drag (iter 056
  closure pattern). Net Sharpe gain is small.
- Equity-carry sleeves (SPY put-credit-spread VRP at higher
  notional, iter 026 family): Sharpe ~0.7 BUT correlation with iter
  041's calm-regime 70/40/40 stack is high (~0.7+).
- Levered duration carry (TLT/EDV trend): Sharpe < 0.5 in 2007-2026
  sample (Treasury bear market in 2022 dominated; iter 023/033
  closures).
- AQR/JPM-replication-style style premium portfolios (multi-factor
  long-short composites): require external data not in Tiingo cache
  AND structurally different; not blocked by iter 046 ceiling per
  se.

The likely **outcome of further iter-046-family experiments** is
score plateau at 85 (Pareto improvements within Sharpe/MDD axes,
no CAGR breakthrough). To score 90 from this base, the **next
iteration should pivot to a structurally different anchor** —
either iter 037-anchor with stronger CAGR base, or a fresh
4-stream composite where the 4th stream (CAGR-additive) raises
edu CAGR ≥ 9.18% without breaking the corr<0.85 kill F.

## Structural dead-ends discovered

None — iter 058 is a STRONG positive result with 0 kills fired.
The closure that this iteration **falsifies** (in the friendly
direction) is the implicit hypothesis "lower correlation alone
beats higher Sharpe in 3rd-stream selection" — clearly false: HYG
(corr 0.44) beats commodity basket (corr 0.30) by +21 score points
purely because of higher absolute Sharpe.

The iter-046-family CAGR-floor structural ceiling (already noted
post-iter-051) is **reinforced**: HYG drops CAGR 0.4-0.5 pp on each
dataset, confirming that CAGR floor cannot be unlocked by any
diversifier with standalone CAGR < iter 046's CAGR, regardless of
diversification quality.

## Citations used

- `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 risk-parity
  stack (iter 041 base architecture, preserved verbatim via iter 046
  saved stream)
- `[volatility_trading, p.218]` — Sinclair 2013 cross-asset VRP
  (iter 039 base architecture, preserved verbatim via iter 046)
- `[systematic_trading]` — Carver TSM single-asset boolean trend rule
  (applied to HYG)
- `[stocks_on_the_move, p.76-77]` — Clenow boolean trend on log price
- `[advances_fin_ml, p.222-223]` — DSR with cumulative n_trials (4328)
- `[advances_fin_ml, p.31-34]` — G7 cross-library parity (numpy ref)
- `[advances_fin_ml, p.196-202]` — bootstrap CI gate G6
- `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (vacuous at N=1)
- `[advances_fin_ml, ch.17-18]` — regime detection (iter 041 VIX gate)
- Asvanunt, A. & Richardson, S. 2017, "The Credit Risk Premium",
  JPM 43(2), DOI 10.3905/jpm.2017.43.2.090 — credit risk premium
  quantification, trend filter for stress avoidance (primary citation)
- Markowitz (1952), JoF 7(1) 77-91 — convex combination Sharpe
  identity (closed-form residual = 0.0000)
- Asness, C., Moskowitz, T. & Pedersen, L. 2013, "Value and Momentum
  Everywhere", JoF 68(3) 929-985, DOI 10.1111/jofi.12021 — credit TSM
  positive Sharpe (Table III)
- Moskowitz, Ooi & Pedersen 2012, JFE 104(2) 228-250,
  DOI 10.1016/j.jfineco.2011.11.003 — TSM canonical reference

## Next iteration suggestions

iter 058 closes the third-stream-Sharpe-axis question on iter 046
constructively. The next binding constraint is the CAGR-floor 0/15.
Three structurally distinct directions point at this constraint:

1. **Levered HYG_TSM at 1.3× external borrow** (analog of iter 056
   on iter 046): doubles HYG_TSM CAGR from 5% → ~9-10% which would
   lift combined CAGR back near iter 046's, but at 3-4% retail
   borrow drag the Sharpe gain may evaporate. This is iter 056's
   pattern applied to the 3rd stream alone (not the combined
   stream). Predicted 78-85.

2. **Higher-CAGR 3rd stream from non-equity asset class** —
   QQQ-1y-trend (Sharpe ~0.8, CAGR ~12% but corr with iter 046 ~0.7
   — kill F risk), EFA + EEM equal-weight TSM (Sharpe ~0.5, CAGR
   ~7% — too low), SPGSCITR commodity index TSM (futures-roll
   adjusted, ETF GSG has 2007+ coverage). Cite Erb-Harvey 2006 +
   Asness-Moskowitz-Pedersen 2013. Predicted 78-85.

3. **Fresh 4-stream composite anchored on iter 037 (not iter
   046)**: iter 037 base CAGR is 12.4-15.5% (from iter 051 result),
   higher than iter 046's 9.07-9.76%. Adding HYG_TSM at w=0.10 to
   iter 037 stream may unlock CAGR floor while preserving Sharpe.
   This re-uses the proven HYG_TSM engine on a different anchor.
   Predicted 80-87.

Direction #3 is the most promising path to WINNER (90+ frozen) — it
combines HYG_TSM (proven 3rd-stream-positive) with iter 037 (proven
higher-CAGR anchor than iter 046), addressing both the Sharpe and
CAGR axes simultaneously.
