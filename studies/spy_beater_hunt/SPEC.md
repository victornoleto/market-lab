# spy_beater_hunt — SPEC

**Created**: 2026-04-29  
**Mission**: Find ONE strategy with mean CAGR ≥ SPY (13.80%) AND mean MDD ≤ SPY (40.85%) AND surviving 7-gate battery on ≥2/3 datasets.

---

## Bar conditions (strict)

A strategy is a **WINNER** if and only if all three conditions hold simultaneously:

### Condition 1: CAGR bar (CAGR ≥ SPY mean)

`mean(CAGR_lh_56y, CAGR_vt_real, CAGR_ndx_real) ≥ 0.1380` (13.80%)

Per-dataset SPY CAGR reference:
- lh_56y: 11.47%
- vt_real: 14.97%
- ndx_real: 14.97%

### Condition 2: MDD bar (MDD ≤ SPY mean)

`mean(MDD_lh_56y, MDD_vt_real, MDD_ndx_real) ≤ 0.4085` (40.85%)

Per-dataset SPY MDD reference:
- lh_56y: 55.14%
- vt_real: 33.70%
- ndx_real: 33.70%

### Condition 3: 7-gate battery (≥ 2/3 datasets)

Same as long_term_portfolio:
- G1 PBO grid-level < 0.5 `[advances_fin_ml, p.208-211]`
- G2 DSR p-value < 0.05 with cumulative_n_trials `[p.222-223]`
- G3 Walk-Forward 6/8 windows, MDD < 25% per window `[ch.12]`
- G4 OOS 70/30 Sharpe > 0
- G5 FWD stress post-2020 Sharpe > 0
- G6 Bootstrap 99.9% CI low > 0 `[p.196-202]`
- G7 Cross-lib ±3 pp CAGR `[p.31-34]`

Pass thresholds:
- lh_56y: ≥ 5/7
- vt_real: ≥ 4/7
- ndx_real: ≥ 4/7

---

## Why this bar is hard

**Frame**: SPY 1× buy-hold has a **known impossibility** for unleveraged, bonds-included portfolios — you can't beat 100% equity in CAGR with anything that contains bonds (math).

So the strategy MUST involve one of:

1. **Leverage** (>100% notional via futures or LETFs)
2. **Concentration** in higher-CAGR equity (QQQ, AVUV, SPMO instead of broad SPY)
3. **Tactical timing** (in equity when bull, out when bear — Gayed LRS / 200d SMA)
4. **Stacking** (NTSX + GDE-style 130-150% notional, but Phase 1+1B showed this caps at ~10.7% CAGR)

The legitimate paths are 1+3 (leverage + regime gate) or 2+3 (concentration + regime gate). Pure stacking (4) is exhausted by long_term_portfolio.

---

## Anti-overfit discipline

**KILL conditions pre-committed** (same as long_term_portfolio):

- KILL #1 (no-positive-config): best config in iter doesn't beat SPY CAGR in ≥1/3 datasets → close direction
- KILL #2 (monotonic regression): leverage/weight increase monotonically degrades Sharpe → close
- KILL #3 (synth no-free-lunch): synth standalone Sharpe > 1.5 → broken synth
- KILL #4 (frankenstein degradation): combo Sharpe < mean of constituents → fall back
- **NEW KILL #6 (CAGR bar can't be reached even at extreme weights)**: if iter sweep at extreme weight (e.g., 100% UPRO, 100% TQQQ) cannot achieve CAGR ≥ 13.80% AND MDD ≤ 40.85%, the strategy class is structurally subordinate. Close direction.

**DSR cumulative inflation**: spy_beater_hunt starts fresh n_trials=0. As iters run, cumulative_n_trials grows. The DSR bar tightens accordingly per `[advances_fin_ml, p.222-223]`.

---

## Datasets (same as long_term_portfolio)

- **lh_56y** (40y synth): SPYSIM 1986+ + KMLMSIM (FF MoM proxy 1986-1988)
- **vt_real** (~17y real): VTSIM proxy + SPY Tiingo 2008-2024
- **ndx_real** (16y real): QQQ Tiingo + SPY Tiingo 2010-2024

Loaded via `studies/long_term_portfolio/datasets.py` `load_prices(name)`.

---

## Tier rubric (preview — see WINNER_AND_RANKING.md for full)

| score | tier (CAGR≥SPY met) | tier (CAGR<SPY) |
|---|---|---|
| ≥ 90 | 🏆 **WINNER** | 🥇 STRONG |
| 75-89 | 🥇 STRONG | 🥈 PROMISING |
| 60-74 | 🥈 PROMISING | 🥉 MARGINAL |
| < 60 | 🥉 MARGINAL | 📉 NEAR_FAIL / FAIL |

WINNER tier requires ALL THREE strict bars met (CAGR ≥ SPY, MDD ≤ SPY, gates ≥ 2/3) AND score ≥ 90. Anything else is just ranking.

---

## Methodology

### Iteration template (reuse from long_term_portfolio)

Each iter:
1. Pre-commit hypothesis (sleeve/strategy + 4 weight configs)
2. Build synth via `studies/long_term_portfolio/synths.py` (NTSX/AVUV/SPMO/RSST/UPRO/TQQQ/etc) + `proxies.py`
3. Run on 3 datasets via `run_iter.py` adapted scoring
4. Apply 7-gate battery
5. Score against bar conditions (CAGR + MDD + gates)
6. Update BASE_MEMORY frontmatter + iteration log
7. Commit

### Synths required (most already in long_term_portfolio/synths.py)

Already implemented:
- NTSXSIM, GDESIM, KMLMSIM, DBMFSIM, TLTSIM, RSSTSIM, AVUVSIM, AVDVSIM, AVEMSIM, SPMOSIM, IDMOSIM

NEEDED for spy_beater (NEW synths to implement in early iters):
- **UPROSIM**: 3× SPY synth (testfolio cache likely has UPROSIM directly)
- **SSOSIM**: 2× SPY synth (testfolio cache: SSOSIM)
- **TQQQSIM**: 3× QQQ synth (cache: TQQQSIM)
- **QLDSIM**: 2× QQQ (cache: QLDSIM)
- **TMFSIM**: 3× LTT synth — may not exist; synth via TLTSIM × 3 with daily-reset decay

The testfolio cache from prior session exploration showed:
`['BNDSIM', 'CASHX', 'DBMFSIM', 'EFVSIM', 'GDESIM', 'GLDSIM', 'IEFSIM', 'KMLMSIM', 'QLDSIM', 'QQQSIM', 'RSSBSIM', 'SPYSIM', 'SSOSIM', 'TLTSIM', 'TQQQSIM', 'UGLSIM', 'UPROSIM', 'VBRSIM', 'VEASIM', 'VSSSIM', 'VTISIM', 'VTSIM', 'VWOSIM', 'VXUSSIM', 'ZROZSIM']`

UPROSIM, SSOSIM, TQQQSIM, QLDSIM, UGLSIM all DIRECT in cache — no synth needed.

Missing: TMFSIM (3× LTT for HFEA). Synth path: `TLTSIM × 3 - daily-reset decay (~1.5%/y for 3× LETF)`.

### Regime gate implementation (Gayed LRS)

200-day SMA gate applies to SPY (or QQQ): when SPY > 200d MA → in equity, else → cash/bonds.
- Signal data: `SPYSIM` for SPY, `QQQSIM` for QQQ
- Lag: 1 trading day (no peek-ahead)
- Off-regime asset: `IEFSIM` (7-10y Treasury, 0% vol baseline) or `CASHX` (T-bill)

### Stress periods (validation)

Critical regimes to backtest:
- **2008 GFC** (peak equity drawdown ~55%) — leveraged longs catastrophic
- **2020 COVID** (fast crash, fast recovery) — regime gate may whipsaw
- **2022 inflation** (60/40 worst year ever) — LTT-heavy strategies got destroyed
- **2000-02 dot-com** (NASDAQ -78%) — TQQQ-style strategies wiped
- **1973-74 stagflation** (sintético only via ZROZSIM/GLDSIM)

Strategies that perform well in 2010-2024 may fail catastrophically in 2008/2022 — explicit stress test required.

---

## Conclusion

spy_beater_hunt is a CAGR-anchored hunt for a strategy that beats SPY in BOTH CAGR and MDD. The most defensible directions are leveraged equity + regime gate (Gayed LRS) and HFEA-style leveraged barbells. We accept "winner" only if all three strict bars are met.

If the hunt fails to find a winner in 6-12 iters, **F1+SPLIT remains the deploy recommendation** — the failure to find better itself is valuable knowledge.
