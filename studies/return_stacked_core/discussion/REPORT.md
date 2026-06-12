# REPORT — discussion sub-study: answers to the original questions

Date: 2026-06-11. Status: **discovery-only research** (no deployment, no
mandate/capital change). All numbers simulated, gross of taxes/costs, monthly
rebalance, window 2000-01-04..2026-05-21 unless noted. Methodology and
limitations: `METHODS.md`. Numbers: `tables/`. Charts: `figures/`.

The study was chartered around three questions (user request, 2026-06-10):

1. **Is there anything better than our 35/40/25 GDE/RSST/ZROZ allocation?
   What is the best long-run proportion, and why?**
2. **How did these assets behave individually across bull/bear periods, and
   how decorrelated are they really?** (the property we are buying)
3. **What happens with other allocations — removing ZROZ, adding SSO/UPRO,
   and the other stacked ETFs (RSSX, RSSY, NTSX)?**

---

## Q1 — Is 35/40/25 the best allocation? **No single best exists; 35/40/25 sits on a robust plateau, and that is the better property.**

Scanning **all 231 possible 5%-step allocations** of {GDE, RSST, ZROZ}
(`tables/simplex_grid.csv`, figs 08-09):

- Full-window argmax: **45/25/30**, Sharpe 0.866. CORE 35/40/25: Sharpe 0.847
  (88th percentile of all mixes).
- The region within 95% of max Sharpe is a **contiguous plateau of 60 nodes**
  (roughly GDE 30-60% / RSST 10-45% / ZROZ 20-40%).
- Re-running the scan from 8 start dates (2000→2014,
  `tables/simplex_start_sensitivity.csv`): the **argmax wanders**
  (45/25/30 → 50/20/30 → 60/30/10…) while **35/40/25 stays inside the plateau
  in 8/8 windows** (Sharpe percentile 0.74-0.99 per window).

**Verdict:** declaring any single node "optimal" would be selection bias over
231 trials `[advances_fin_ml, p.208-211, p.222-223]`. The defensible long-run
claim is plateau membership `[testing_tuning, p.327-335]`: 35/40/25 is kept
**not because it wins, but because nothing near it meaningfully beats it and
it is robust to start-date choice.** Re-tuning weights (e.g. to 45/25/30)
is curve-fitting, not improvement. Equal-weight 33/33/33 performs the same
(Sharpe 0.860) — the plateau speaking.

**Why this mix works at all:** ~$1.68 of exposure per $1 across four return
streams (75% stocks, 32% gold, 40% managed futures, 25% long duration) with
leverage embedded in the funds `[leverage_for_the_long_run, p.13]`,
`[risk_parity, ch.5]`. The result vs SPY: **CAGR 12.52% vs 8.54%, MDD −30.76%
vs −55.14%, Sharpe 0.847 vs 0.522, terminal 22.5× vs 8.7×**.

## Q2 — Individual behavior across regimes + decorrelation: **three diversifiers, three different crises, near-zero average correlations and positive crisis capture — except BTC and carry, which crash with stocks.**

Per-episode components (`tables/episodes_components.csv`, figs 04-05):

| Episode | SPY | Gold | Managed futures | ZROZ |
|---|---|---|---|---|
| Dot-com bust 2000-02 | −47% | +12% | +44% | +50% |
| GFC 2007-09 | −55% | +25% | +34% | +50% |
| **2022 inflation shock** | −24% | −9% | **+38%** | **−40%** |
| AI bull 2022-26 | +118% | +177% | +5% | −19% |
| Stagflation 1973-74 (LOW fid.) | −45% | +139% | +65% | −30% |

The rotating-hero pattern is the core finding: duration+trend saved 2000-02,
everything-but-stocks saved 2008, **trend alone saved 2022** (bonds were the
second source of loss — exactly the year that killed single-diversifier
leverage like HFEA: −65% vs CORE −21%).

Decorrelation quantified (`tables/corr_full_monthly.csv`,
`tables/crisis_capture.csv`, figs 06-07):

- Monthly correlation vs SPY: **gold +0.06, managed futures −0.22,
  ZROZ −0.15**; all diversifier pairs ≤ +0.19.
- Rolling 252d correlations are NOT stable (SPY~ZROZ flipped positive in
  2022); the portfolio case rests on near-zero averages plus conditional
  behavior, not constant hedges.
- **Crisis capture** (32 worst SPY months, avg −7.9%/mo): gold **+1.8%**,
  managed futures **+2.4%**, ZROZ **+3.8%** mean monthly return — vs
  **BTC −4.4%** and **carry −0.8%** (these two are *return* stacks, not
  *crisis* stacks).
- Honesty episodes: the core lags badly in pure melt-ups — taper tantrum
  2013: SPY +17.5%, CORE **−2.4%**; QE decade: HFEA +3,183% vs CORE +478%.

## Q3 — Other allocations: **ZROZ removal trades 1.4pp CAGR for 15pp deeper drawdowns; LETFs/HFEA are dominated at these horizons; RSSX is a BTC bet in a wrapper; RSSY (carry) made the portfolio worse.**

`tables/ablations_primary.csv` (fig 12), Δ vs CORE 12.52% / −30.76% / 0.847:

| Variant | CAGR | MDD | Sharpe | Reading |
|---|---|---|---|---|
| No ZROZ (47/53 renorm) | 13.89% | −45.45% | 0.737 | ZROZ's job is the left tail, not return |
| ZROZ → cash | 11.06% | −35.94% | 0.764 | it's duration, not "less stocks" |
| NTSX swap (gold→bonds) | 9.75% | −28.11% | 0.743 | gold > more bonds this window (gold-decade caveat) |
| DIY-SSO (35 SSO/20 GLD/25 MF/20 ZROZ) | 10.37% | −33.03% | 0.811 | explicit 2x leverage works but trails the embedded stack ~2pp |
| 100% SSO | 9.94% | −88.27% | 0.440 | vol drag |
| 100% UPRO | 7.21% | −98.31% | 0.412 | below unlevered SPY — path bet, not return multiplier |
| 60/40 SSO/ZROZ | 10.34% | −57.99% | 0.564 | leverage + one diversifier is not enough |
| HFEA 55/45 monthly | 12.11% | −69.42% | 0.526 | one hedge, levered 3x: −68% GFC, −65% 2022 |
| HFEA 55/45 quarterly | 15.34% | −69.09% | 0.619 | +3.2pp/yr vs monthly = rebalance-timing luck at 3x |

Extensions (separate windows, weaker evidence):

- **RSSX** (stocks+gold+BTC; 2010-07+ window, `tables/ablations_btc_window.csv`):
  GDE→RSSX swap lifts CAGR 15.0%→26.2% and Sharpe 1.04→1.47 — **entirely
  BTC's 2010s**; RSSX fell **−41% in 2022** (worse than SPY) and the BTC sim
  carries survivorship bias. Verdict: optional satellite (≤10%), not core.
- **RSSY** (stocks+carry; monthly AQR proxy, `tables/ablations_monthly_rssy.csv`):
  RSST→RSSY swap **reduces** Sharpe 0.956→0.882 and deepens MDD −24%→−33%;
  the 50/50 split lands between. Carry did not defend 2008/2022 the way trend
  did. Verdict: does not earn a core slot on this evidence.
- **1970+ extension** (LOW fidelity, `tables/extended_metrics.csv`, fig 11):
  core-style mix (haircut MF proxy) 13.9% CAGR / −39.7% MDD vs SPY 11.1% /
  −55.1%; HFEA reaches **−90.3%** in the Volcker years. The 1970s are the
  regime that bond-levered strategies cannot survive and gold/trend stacking
  is built for.

---

## Consolidated verdict

The portfolio's edge in this simulated history comes from **stacking four
lowly-correlated return streams on one dollar**, not from the specific
weights. 35/40/25 is retained as a robust plateau member; the only allocation
decisions that materially matter are **(a) keeping all three diversifiers**
(each was the sole hero in at least one major regime) and **(b) sizing ZROZ
by drawdown tolerance** (0-40% slides CAGR↔MDD along the frontier, fig 09).
Alternatives that lever fewer streams (HFEA, SSO/UPRO) earned their returns
with 2-3× the drawdown; alternatives that add non-defensive streams
(RSSX/BTC, RSSY/carry) either import equity-correlated crash risk or dilute
the trend sleeve.

**Caveat #1 (repeat in any external claim):** crisis magnitudes are
MF-proxy-sensitive — CORE's GFC return is −23.1% with the current tracking
proxy vs −13.8% on the old 1988 saved curve
(`tables/episodes_crosscheck.csv`). Directionally honest, not precise.

---

## Addendum (2026-06-11) — CORE vs unlevered "safe" portfolios

User-chartered comparison against five classic low-drawdown unlevered mixes,
all computed by the same Testfol.io engine on the common window
**2000-01-03..2026-06-11** (26.4y; data: `tables/safe_portfolios_metrics.csv`,
curves: `series/safe_portfolios_equity.csv`, re-fetch:
`s08_safe_portfolios_fetch.py` — optional network step):

| Portfolio (yearly reb.) | CAGR | MDD | Vol | Sharpe | $1 → |
|---|---|---|---|---|---|
| B1 — 21 VUG/21 VBR/26 TLT/16 GLD/10 KMLM/6 cash | 8.46% | **−17.3%** | 8.5% | **1.000** | $8.6 |
| B2 — Golden Butterfly | 8.17% | −19.5% | 8.5% | 0.973 | $8.0 |
| B3 — Permanent Portfolio | 7.08% | **−16.8%** | 7.1% | **1.006** | $6.1 |
| B4 — All Weather | 6.85% | −23.4% | 7.9% | 0.884 | $5.8 |
| B5 — 25 REIT/25 BND/25 GLD + 25 equity | 8.65% | −33.9% | 11.2% | 0.800 | $9.0 |
| **CORE 35/40/25 (monthly reb.)** | **12.30%** | −30.2% | 15.3% | 0.835 | **$21.5** |
| 100% SPY | 8.33% | −55.1% | 19.3% | 0.512 | $8.3 |

What they teach:

1. **Same thesis, undiluted vs diluted.** Every safe mix holds our
   diversifiers (gold in all five, duration in all five, trend only in B1)
   with equity cut to 20-42%. Their −17/−23% MDDs come from 58-80% defensive
   ballast. They independently validate the RSC sleeve selection
   `[risk_parity, ch.5]`.
2. **Risk-efficiency is THEIR edge, not ours**: unlevered Sharpe 0.97-1.01
   (Permanent Portfolio is the king) vs CORE 0.835. The price is growth:
   CAGR ≈ SPY or below; $1 → $6-9 in 26 years vs CORE's $21.5.
3. **B5 is the cautionary row**: REITs are equity in disguise (−34% MDD,
   crushed in the GFC) — diversification by asset *name* is not
   decorrelation.
4. Episodes: GFC — Permanent −3.8%, B1 −11.7% vs CORE −23.2%; AI bull —
   safe mixes +43-64% vs CORE +96%, SPY +113%. 2022 compressed everyone to
   −15/−21% (gold+duration suffer together; only trend offsets).

**Is return stacking superior? Two decisive tests** (same table):

- **Dilution test (matched MDD)** — CORE blended with T-bills: at Golden
  Butterfly's −19.5%, diluted CORE earns 8.42% vs 8.17% (narrow win); at All
  Weather's −23.4%, 9.96% vs 6.85% (big win); at Permanent's −16.8%, ~7.6%
  vs 7.08% (win); at B1's −17.3%, 7.90% vs **8.46% — B1 wins**. At the
  deep-safety end, a well-built unlevered mix beats the diluted stack.
- **Leverage test (matched gross, 1.65×, financed at cash+2% — the repo
  payload convention)**: B1 × 1.65 = 11.04% / −30.1% / Sharpe 0.813 vs CORE
  12.30% / −30.2% / 0.835 → **CORE wins at the same risk and the same
  leverage**. B1's unlevered Sharpe edge evaporates once it pays real
  financing — which is exactly what return-stacked ETFs pay, embedded
  `[leverage_for_the_long_run, p.13]`.

**Conclusion: return stacking's superiority is conditional on the
objective.** For long-run compounding (~12% CAGR at MDD ≤ ~30%) none of the
safe mixes can get there unlevered, and at matched leverage our recipe still
wins. For a true MDD ≤ −20% objective, a B1/Golden-Butterfly-style unlevered
portfolio is the better tool than diluting CORE — simpler, no fund-stack
risk, higher Sharpe. Return stacking is not a Sharpe machine; it is a
**capital-efficiency technology**: it adds the diversifiers without giving
up the equity. The safe portfolios hold the same diversifiers by giving the
equity up — and the compounded difference over 26 years is $21.5 vs $8.

Caveats: all simulated; the 2000+ window contains the gold decade (every mix
here holds 16-25% gold); B1 is itself a backtest-discovered allocation, so
its Sharpe carries selection bias `[advances_fin_ml, p.208-211]`; yearly
rebalance for the safe mixes (their convention) vs monthly for CORE (ours).
