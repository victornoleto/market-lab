# Iter 009 — HAA SmartStack + 5% Gold Sleeve

## Hypothesis

**HAA SmartStack (iter 005 WINNER, Sharpe 1.112) + 5% fixed GLDSIM sleeve.**

Iter 005 left a 0.07 Sharpe gap to the bestfolio reference (1.18 on 33.4y). Gold is the
candidate to close it: gold has near-zero correlation to global equity and low correlation
to managed futures (KMLM), acting as an independent inflation hedge that adds Sharpe
through pure diversification, not return stacking.

The GDESIM asset in the offensive universe already embeds 90% gold via capital-efficient
structure. However, GDESIM is only selected when HAA momentum is positive — meaning
gold exposure is zero during risk-off regimes. A small fixed GLDSIM sleeve provides
persistent gold exposure regardless of regime.

**Config (pre-committed, n_trials=1):**

| sleeve | weight | asset |
|---|---|---|
| HAA dynamic | 85% | top-2 from [NTSXSIM, NTSI, NTSE, GDESIM] / top-1 defensive |
| KMLM fixed | 10% | KMLMSIM |
| Gold fixed  |  5% | GLDSIM |

Change from iter 005: `DYNAMIC_WEIGHT 0.90 → 0.85`, `GLD_WEIGHT = 0.05`.

## Mechanism

1. **HAA canary (VWOSIM)**: regime switch as iter 005. Risk-on = top-2 offensive; risk-off = top-1 defensive. `[stocks_on_the_move, ch.6]`
2. **KMLM free lunch (10%)**: unchanged from iter 005. `[ilmanen_expected_returns, ch.19]`
3. **Gold diversification (5%)**: gold is low-beta to both equity and bonds; persistent holding reduces MDD during equity/bond drawdowns. `[ilmanen_expected_returns, ch.fx-carry]`

## Edge source

- Sharpe improvement from gold: diversification benefit (correlation ~0 to equity, ~0.1 to bonds in stress periods).
- Gold serves as inflation hedge orthogonal to the HAA equity + bond dynamic allocation.
- 5% is small enough to not materially drag CAGR if gold underperforms, but large enough to partially hedge crisis periods.

## Kill criteria

- **Kill 1**: edu Sharpe ≤ 1.112 (must beat iter 005 WINNER) → discard
- **Kill 2**: any WF G3' window fails (MDD exceeds VT*notional benchmark-relative) → not WINNER

## Datasets

| dataset | window | binding ticker | label |
|---|---|---|---|
| educational | 1994-05-01 → 2026-04-24 | VWOSIM | VWOSIM binding 1995-2026 (~31y) |
| vt_real | 2008-06-01 → 2026-04-24 | — | VTSIM proxy (~17y) |
| ndx_real | 2010-02-01 → 2026-04-24 | — | QQQ proxy (16y) |

## Citations

- `[stocks_on_the_move, ch.6]` — HAA momentum mechanics (canary + multi-period lookback)
- `[ilmanen_expected_returns, ch.19]` — managed futures free-lunch sleeve
- `[ilmanen_expected_returns, ch.fx-carry]` — gold as inflation hedge, low-correlation diversifier
- `[leverage_for_the_long_run, p.40-60]` — return-stacking for offensive assets (NTSXSIM/NTSI/NTSE/GDESIM)
- `[advances_fin_ml, p.208-211]` — G1 PBO
- `[advances_fin_ml, p.222-223]` — G2 DSR
- `[advances_fin_ml, p.196-202]` — G6 Bootstrap
- `[advances_fin_ml, p.31-34]` — G7 cross-lib
