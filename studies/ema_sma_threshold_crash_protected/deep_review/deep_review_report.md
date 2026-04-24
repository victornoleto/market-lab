# Deep rolling-window review — Candidate vs SPY buy-hold

> Rigorous quantitative test of the *'quase sempre à frente do SPY 1x'* claim. 40y synth window 1986-01-03 → 2026-04-17. Candidate: `EMA_N150_th5_bL3_sL0` + `sl30_rec10_cape05`.

> ⚠️ This review does **NOT** validate live deployment. Gates failed (3/7 in SPY real 17y). This is a synth-only diagnostic.

## 1. Rolling-window CAGR vs SPY


**Is the candidate 'sempre' ahead of SPY?** Count rolling windows of each length and measure the fraction in which CAGR_cand > CAGR_SPY.

| window | # windows | **win rate** vs SPY | median excess (pp) | mean excess (pp) | % windows > +10pp ahead | % windows *behind* SPY |
|---|---|---|---|---|---|---|
| 1y | 9898 | **71.1%** | +13.59 | +16.16 | 56.8% | 28.9% |
| 3y | 9394 | **82.7%** | +12.19 | +13.10 | 55.7% | 17.3% |
| 5y | 8890 | **90.3%** | +13.67 | +12.73 | 60.0% | 9.7% |
| 10y | 7630 | **95.9%** | +14.71 | +12.80 | 70.0% | 4.1% |

**Reading the table**:

- Rolling 1y: candidate beats SPY in **71.1%** of windows (7036 of 9898). Lags SPY in 28.9% (2861 windows).

- Rolling 3y: candidate beats SPY in **82.7%** of windows (7770 of 9394). Lags SPY in 17.3% (1624 windows).

- Rolling 5y: candidate beats SPY in **90.3%** of windows (8032 of 8890). Lags SPY in 9.7% (858 windows).

- Rolling 10y: candidate beats SPY in **95.9%** of windows (7318 of 7630). Lags SPY in 4.1% (312 windows).


**Worst windows** (candidate vs SPY over rolling 3y and 5y):

| window | end date | cand CAGR | SPY CAGR | cand − SPY (pp) |
|---|---|---|---|---|
| 3y | 2018-05-03 | +0.29% | +9.81% | -9.53 |
| 3y | 2018-04-25 | +0.38% | +9.90% | -9.52 |
| 3y | 2018-04-24 | +0.41% | +9.89% | -9.48 |
| 3y | 2018-03-23 | +0.20% | +9.61% | -9.41 |
| 3y | 2020-06-11 | +0.11% | +9.51% | -9.40 |
| 3y | 2018-05-02 | +0.61% | +10.00% | -9.39 |
| 3y | 2020-06-26 | +0.12% | +9.44% | -9.32 |
| 3y | 2018-04-30 | +0.93% | +10.21% | -9.28 |
| 3y | 2018-05-29 | +1.22% | +10.50% | -9.28 |
| 3y | 2018-04-27 | +1.06% | +10.34% | -9.28 |

See `worst_windows.csv` for the full top-10 per window. Plots: `rolling_cagr_1y.png`, `rolling_cagr_3y.png`, `rolling_cagr_5y.png`, `rolling_cagr_10y.png`, `rolling_excess_vs_spy.png`.

## 2. Calendar year returns

Of 41 full calendar years in 1986-2025, the candidate beat SPY in **28 years** (68.3% of years).

| year | Candidate | Baseline 3x | SPY | Cand − SPY (pp) |
|---|---|---|---|---|
| 1986 | -3.65% | -3.65% | +18.74% | -22.39 |
| 1987 | +85.08% | +56.55% | +5.15% | +79.94 |
| 1988 | +6.30% | +6.30% | +16.45% | -10.14 |
| 1989 | +113.51% | +113.51% | +31.49% | +82.02 |
| 1990 | -22.99% | -22.99% | -3.24% | -19.75 |
| 1991 | +87.24% | +87.24% | +30.32% | +56.92 |
| 1992 | +19.84% | +19.84% | +7.56% | +12.28 |
| 1993 | +27.82% | +27.82% | +9.75% | +18.07 |
| 1994 | -2.76% | -2.76% | +0.50% | -3.26 |
| 1995 | +155.31% | +155.31% | +38.16% | +117.16 |
| 1996 | +45.53% | +73.56% | +22.67% | +22.86 |
| 1997 | +54.31% | +108.67% | +33.60% | +20.71 |
| 1998 | +15.05% | +19.69% | +28.81% | -13.76 |
| 1999 | +32.00% | +57.15% | +20.50% | +11.50 |
| 2000 | -13.34% | -27.89% | -9.64% | -3.69 |
| 2001 | +0.00% | +0.00% | -11.67% | +11.67 |
| 2002 | +0.00% | +0.00% | -21.51% | +21.51 |
| 2003 | +64.68% | +65.86% | +28.30% | +36.38 |
| 2004 | +29.50% | +29.83% | +10.81% | +18.69 |
| 2005 | +10.89% | +10.83% | +4.92% | +5.97 |
| 2006 | +49.30% | +49.89% | +15.96% | +33.35 |
| 2007 | +7.18% | +6.95% | +5.23% | +1.94 |
| 2008 | -14.44% | -14.64% | -36.75% | +22.31 |
| 2009 | +60.82% | +61.07% | +26.49% | +34.33 |
| 2010 | +11.25% | +3.65% | +15.17% | -3.91 |
| 2011 | -13.51% | -14.04% | +1.98% | -15.49 |
| 2012 | +35.59% | +35.58% | +16.10% | +19.49 |
| 2013 | +112.57% | +121.59% | +32.43% | +80.14 |
| 2014 | +31.97% | +39.66% | +13.57% | +18.40 |
| 2015 | -16.93% | -22.77% | +1.35% | -18.27 |
| 2016 | -6.10% | +22.89% | +12.11% | -18.20 |
| 2017 | +40.72% | +76.57% | +21.81% | +18.90 |
| 2018 | -4.04% | -10.95% | -4.47% | +0.43 |
| 2019 | +31.51% | +44.49% | +31.35% | +0.16 |
| 2020 | +10.21% | +0.69% | +18.49% | -8.27 |
| 2021 | +48.14% | +101.39% | +28.87% | +19.28 |
| 2022 | -17.71% | -31.26% | -18.09% | +0.39 |
| 2023 | +14.09% | +47.52% | +26.31% | -12.22 |
| 2024 | +74.42% | +84.40% | +25.00% | +49.42 |
| 2025 | +12.96% | +13.24% | +17.83% | -4.86 |
| 2026 | +11.02% | +11.61% | +4.46% | +6.57 |

Plot: `calendar_year_returns.png`.

## 3. Entry-year sensitivity

For each possible start year, measure CAGR and MDD if you bought-and-held the candidate (vs baseline 3x vs SPY) from that year to 2026.

| start year | cand CAGR | cand MDD | SPY CAGR | SPY MDD | cand − SPY (pp) |
|---|---|---|---|---|---|
| 1986 | +24.01% | +44.55% | +11.47% | +55.14% | +12.54 |
| 1987 | +24.64% | +44.55% | +11.24% | +55.14% | +13.40 |
| 1988 | +23.53% | +44.55% | +11.36% | +55.14% | +12.18 |
| 1989 | +24.12% | +44.55% | +11.36% | +55.14% | +12.77 |
| 1990 | +22.02% | +44.55% | +10.77% | +55.14% | +11.25 |
| 1991 | +23.81% | +44.55% | +11.28% | +55.14% | +12.52 |
| 1992 | +22.32% | +44.55% | +10.74% | +55.14% | +11.58 |
| 1993 | +22.41% | +44.55% | +10.84% | +55.14% | +11.57 |
| 1994 | +22.27% | +44.55% | +10.88% | +55.14% | +11.39 |
| 1995 | +23.09% | +44.55% | +11.20% | +55.14% | +11.88 |
| 1996 | +20.08% | +44.55% | +10.39% | +55.14% | +9.69 |
| 1997 | +19.41% | +44.55% | +10.02% | +55.14% | +9.39 |
| 1998 | +18.32% | +44.55% | +9.26% | +55.14% | +9.06 |
| 1999 | +18.49% | +44.55% | +8.63% | +55.14% | +9.86 |
| 2000 | +18.06% | +44.55% | +8.24% | +55.14% | +9.83 |
| 2001 | +19.44% | +44.55% | +9.05% | +55.14% | +10.39 |
| 2002 | +20.31% | +44.55% | +9.86% | +55.14% | +10.44 |
| 2003 | +21.27% | +44.55% | +11.36% | +55.14% | +9.90 |
| 2004 | +19.62% | +44.55% | +10.82% | +55.14% | +8.80 |
| 2005 | +19.24% | +44.55% | +10.84% | +55.14% | +8.40 |
| 2006 | +19.29% | +44.55% | +11.02% | +55.14% | +8.27 |
| 2007 | +18.25% | +44.55% | +10.88% | +55.14% | +7.37 |
| 2008 | +19.02% | +39.75% | +11.23% | +51.83% | +7.78 |
| 2009 | +21.14% | +39.75% | +14.68% | +33.69% | +6.46 |
| 2010 | +18.68% | +39.75% | +14.08% | +33.69% | +4.60 |
| 2011 | +19.34% | +39.75% | +14.06% | +33.69% | +5.28 |
| 2012 | +22.32% | +39.75% | +14.91% | +33.69% | +7.41 |
| 2013 | +20.69% | +39.75% | +14.73% | +33.69% | +5.96 |
| 2014 | +16.18% | +39.75% | +13.72% | +33.69% | +2.45 |
| 2015 | +14.62% | +39.75% | +13.64% | +33.69% | +0.98 |
| 2016 | +18.26% | +39.75% | +15.07% | +33.69% | +3.19 |
| 2017 | +21.03% | +39.75% | +15.13% | +33.69% | +5.91 |
| 2018 | +18.90% | +39.75% | +14.34% | +33.69% | +4.56 |
| 2019 | +22.64% | +39.75% | +17.29% | +33.69% | +5.35 |
| 2020 | +20.91% | +39.75% | +15.04% | +33.69% | +5.86 |

**Of 35 possible start years, candidate beats SPY CAGR in 35 (100.0%).**
Plot: `entry_year_sensitivity.png`.

## 4. Time spent underwater

| strategy | % days > 5% below peak | % days > 20% below peak | % days > 40% below peak |
|---|---|---|---|
| Candidate | 62.6% | 21.6% | 0.2% |
| Baseline 3x | 66.6% | 36.4% | 4.8% |
| SPY | 43.6% | 15.3% | 2.4% |

Plot: `underwater.png`.

## 5. Verdict on the 'quase sempre à frente' claim

The candidate beats SPY **71.1%** of rolling 1y windows, **82.7%** of 3y, **90.3%** of 5y, **95.9%** of 10y. Longer horizons favor the candidate — the leverage + stop overlay's edge accumulates. But:

* At 1y: candidate loses to SPY in 28.9% of windows.
* Year-by-year: 13 of 41 calendar years had candidate behind SPY.
* 2020 COVID window specifically: candidate −13 % vs SPY +5 % — the kind of outcome that matters for live execution timing.
* **'Sempre' (100 %) is empirically false**. The claim that matches the data is: 'candidate wins on **long-horizon rolling CAGR** but underperforms SPY in short/medium windows around certain crash-recovery events'.

## 6. Critical caveats for live deployment

1. **This is 40 y synth**. Real UPRO has 2–3 pp/yr tracking drag vs perfect-leverage synth `[leverage_for_the_long_run, p.21, Table 12]`. Real CAGR ≈ 21–22 % instead of 24 %.
2. **Spec §0 fails in real data**. See `../phase3/cross_dataset_gates.md`. The same parameter set gives 3/7 gates on SPY real (17 y), not 6/7.
3. **CAPE stale at 2023-09** — for post-2024 live trading the risk signal degrades to constant 0 (no de-lever). Effectively reduces to stop-loss only.
4. **G3 Walk-Forward universal FAIL**. Window-local MDDs routinely exceed 25 %. A rolling review that slices the 40 y into overlapping 2.5 y train + 6 mo OOS periods shows the overlay can't keep individual windows clean.
5. **9 stops in 40 years** — roughly 1 per 4.5 y. Operationally, the user must commit to execute stop-reentry discipline for decades without drift.


---
*Next artifact: `PRE_DEPLOYMENT_README.md` — go/no-go checklist.*
*Citations: spec §0, §6.1, §6.2, §8.1-8.3. `[leverage_for_the_long_run, p.21, Table 12]` (synth vs real). `[advances_fin_ml, p.208-211, p.222-223, ch.12]` (gates).*
