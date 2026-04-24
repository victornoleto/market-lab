# Iteration 002 — Final Report

## Verdict

**❌ FAIL (score 17/100, winner_conditions_met=False, tier=FAIL)**

Clenow's canonical cross-sectional momentum (ranking = annualized 90d
log-regression slope × R², ATR risk-parity sizing at 10 bps per position,
SPY 200d regime filter) transported from S&P 500 single stocks to the 11
SPDR sector ETFs **does not beat SPY** on risk-adjusted terms — on any of
the 3 datasets, for any of the 4 configs tested. The **kill criterion
pre-committed in `hypothesis.md` fires**: spy_real Sharpe at canonical
parameters is 0.27 (< 0.90 benchmark). Hypothesis falsified.

## Headline metrics (top candidate per dataset)

| dataset | cfg | Sharpe (bench Δ) | CAGR (bench Δ) | MDD (bench Δ) | gates |
|---|---|---|---|---|---|
| educational (sectors_long 2006-2026 SPY) | k3_L2 | 0.28 (−0.25 vs 0.54) | 1.57% (−7.30pp vs 8.87%) | 15.90% (−40.57pp vs 56.47%) | 4/7 |
| spy_real (sectors_spy 2009-2026 SPY) | k5_L2 | 0.27 (−0.53 vs 0.79) | 2.15% (−10.78pp vs 12.93%) | 20.00% (−14.10pp vs 34.10%) | 3/7 |
| ndx_real (sectors_ndx 2010-2026 QQQ) | k5_L2 | 0.27 (−0.64 vs 0.91) | 2.21% (−15.95pp vs 18.15%) | 19.72% (−15.90pp vs 35.62%) | 2/7 |

All 4 configs across all 3 datasets produced Sharpe 0.22-0.28 — well below
every benchmark. The configs are summarized in `results.json`.

## Score breakdown

Benchmarks were **overridden** from `scoring.BENCHMARKS` to reflect the
actually-measured SPY/QQQ over the same windows (see `benchmarks_used`
in `verdict.json`) — this iteration tests a cross-sectional strategy, so
the 40y SPYSIM-synth Sharpe 0.68 (default `educational` bench) does not
apply; instead `educational` = measured SPY 2006-2026 Sharpe 0.54.

| criterion | points | max | detail |
|---|---|---|---|
| 1 Sharpe edge | 0 | 25 | 0/3 datasets beat benchmark + 0.10 (candidate Sharpe ≈ 1/3 of bench) |
| 2 Gates | 2 | 25 | edu 4/7 (G3/G4/G5/G7) + spy 3/7 (G3/G5/G7) + ndx 2/7 (G5/G7); no cross-dataset bonus |
| 3 DSR | 0 | 15 | worst p=0.992 with n_trials=4024 (cumulative) — no significance |
| 4 CAGR floor | 0 | 15 | 0/3 datasets reach 0.8 × benchmark CAGR |
| 5 MDD ceiling | 15 | 15 | 3/3 datasets trivially pass — strategy is 63-75% in cash |
| 6 Robustness | 0 | 5 | not computed |
| **total** | **17** | **100+5** | tier: **❌ FAIL** |

## Gate detail (G1-G7)

Per top-candidate per dataset:

| gate | sectors_long | sectors_spy | sectors_ndx | meaning |
|---|---|---|---|---|
| G1 PBO grid-level < 0.5 | **FAIL** 0.516 | **FAIL** 0.540 | **FAIL** 0.567 | the 4-config grid is at the noise floor — PBO barely above 0.5 `[advances_fin_ml, p.208-211]` |
| G2 DSR p < 0.05 | **FAIL** 0.988 | **FAIL** 0.992 | **FAIL** 0.992 | with 4024 cumulative trials the Sharpe must clear a high bar; 0.27 is far below `[advances_fin_ml, p.222-223]` |
| G3 WF 6/8 windows | PASS 6/8 | PASS 7/8 | **FAIL** 5/8 | passes on 2/3 datasets because returns are near zero + stop-less = very few large drawdowns |
| G4 OOS 70/30 | PASS +0.31 | **FAIL** −0.02 | **FAIL** −0.11 | OOS Sharpe collapses in the real-data datasets |
| G5 FWD post-2020 | PASS +0.19 | PASS +0.10 | PASS +0.08 | barely positive but trivially above zero |
| G6 Bootstrap 99.9% CI low > 0 | **FAIL** −0.40 | **FAIL** −0.42 | **FAIL** −0.42 | bootstrap distribution straddles zero — no statistical edge |
| G7 Cross-lib ±3pp CAGR | PASS 1e-6pp | PASS 1e-6pp | PASS 1e-7pp | engine vs numpy reference agree to 1e-6 — no implementation bug |

G7 is clean (no silent arithmetic bug), so the failure is genuine
strategy behavior, not an engine artifact.

## Configuration tested (top candidate)

- `k5_L2`: top_k=5 sectors held, buy_leverage=2.0× notional
- Canonical Clenow rest: lookback_slope=90, lookback_trend=100,
  lookback_regime=200, lookback_atr=20, gap_threshold=0.15,
  risk_factor=0.001, rebalance=Wednesday weekly, position_rebalance=biweekly
- Universe: 11 SPDR sectors (XLK/XLF/XLV/XLY/XLP/XLE/XLI/XLU/XLB + XLRE + XLC)
- Regime: SPY > 200d SMA
- Execution: $0 commission (Inter zero-brokerage), half_spread=0.005 +
  slippage=0.005 per share (~1¢/share)

## What worked / what didn't

**What worked (partial credit):**

- G7 cross-lib parity to 1e-6 — the adjusted-slope primitive and the
  engine agree perfectly, so any negative result is **real strategy
  behavior**, not an implementation bug.
- Low MDD (7-24%) on all configs — the strategy is safe, but only in the
  degenerate sense that it barely deploys capital.
- Clenow's regime filter (SPY < 200d SMA → no new buys) mechanically
  trimmed bear-market exposure as designed.

**What didn't work (the main finding):**

- **Clenow's 10 bps ATR risk-parity was designed for individual stocks
  with daily ATR ~1-3% of price. Sector ETFs have daily ATR ~0.3-1% of
  price due to intra-sector diversification.** Shares = `100_000 × 0.001 /
  ATR20` at sector ETF prices $70-200 and ATR $1-3 gives positions of
  $5k-10k each. Top-5 positions × ~$7.5k = $37.5k deployed on a $100k
  account → **~63% in cash**. Top-3 × $7.5k = ~77% in cash.
- Buy leverage 2.0× doubles the above — still only 25-50% invested.
- The resulting Sharpe ≈ 0.25 is driven mostly by the cash drag, not by a
  broken signal. When sectors are up, the strategy captures little; when
  down, it loses little. This is under-deployed, not anti-signal.
- **G1 PBO ≈ 0.52-0.57** on the 4-config grid means the 4 configs are
  barely distinguishable from a random relabeling — they are all sitting
  in the same near-zero-return regime, so the "best IS" is just coin-flip
  vs the "worst OOS".
- **G6 bootstrap 99.9% CI low ≈ −0.40** on all datasets: the bootstrap
  distribution of Sharpe straddles zero. No statistical edge.
- **G4 OOS 70/30** fails on spy_real and ndx_real: the late period
  (post-2019) is even flatter for this strategy.

## Main lesson (for future iterations)

**Clenow's canonical parameters do NOT transport from S&P 500 single-stock
universe to sector-ETF universe without risk-budget recalibration.** The
10 bps per-position impact rate is tuned for assets with ATR ~1-3% of
price; sector ETFs have 3× lower per-bar volatility (diversification
inside the ETF), so the formula under-sizes every position by ~3× and
the portfolio ends up structurally 60-80% in cash.

This is **not** the same as the signal being bad. Whether the adjusted-
slope ranking has edge on sector ETFs is an **open question** — this
iteration can't answer it because the sizing dominates the result. A
future iteration testing equal-notional sizing (1/K equity per position,
ignoring ATR) on the same ranking rule would isolate the question of
signal edge from sizing calibration.

This generalizes to a broader principle: **when transporting a book
strategy across asset classes, you must recalibrate risk parameters to
match the new asset's volatility characteristics** — not as optimization
(forbidden `[p.219-220]`) but as *first-principles sizing*. The 10 bps
per position is a constraint on per-position VaR, which depends on the
asset's ATR/price ratio.

## Structural dead-ends discovered

Add to `DEAD_ENDS.md`:

1. **Clenow canonical (10 bps ATR-risk-parity) on sector-ETF universe
   with top-K=3-5** — under-deploys capital by ~3×; trivially safe but
   structurally sub-benchmark. Don't re-test without re-calibrated risk
   factor.
2. **4-config grid on a single strategy family** — when all 4 configs
   live in the same near-zero-return regime, G1 PBO will land at ~0.5
   (noise). Meaningful PBO requires the grid to span configs that
   produce materially different returns; if every config is under-
   deployed, PBO can't help.

## Citations used

- Primary:
  `[stocks_on_the_move, p.70-77, p.82, p.88-89, p.98-99]` — full ranking,
   sizing, and trading rules (Clenow 2015)
- Additional:
  - `[stocks_on_the_move, p.66-67]` — index regime filter (SPY 200d MA)
  - `[stocks_on_the_move, p.219-220]` — anti-optimization principle
    (respected — no parameter tune attempted)
  - `[stocks_on_the_move, p.221-223]` — risk-parity beats cap-weighting
  - `[stocks_on_the_move, p.228-230]` — risk factor calibration (the very
    page whose principle I violated by transporting 10 bps unchanged)
  - `[stocks_on_the_move, p.60]` — Jegadeesh & Titman (1993) cross-sectional
    momentum — the empirical foundation is valid; the implementation failed
  - `[advances_fin_ml, p.208-211]` — PBO gate
  - `[advances_fin_ml, p.222-223, 275]` — DSR with n_trials deflator
  - `[advances_fin_ml, p.196-202]` — bootstrap CI for trade returns
- External: Jegadeesh & Titman (1993), *Journal of Finance* 48(1) 65-91

## Next iteration suggestions

Three structurally different directions that this iteration's findings
point toward:

1. **Equal-notional sector rotation (1/K of equity per position) with
   same Clenow ranking signal.** Isolates signal edge from sizing
   calibration. If this also fails, sector momentum is dead. If it
   succeeds, the finding is that Clenow's sizing needs recalibration for
   ETF universes (a separate paper).

2. **Meta-labeling on trend signals (AFML ch.3)** — direction #3 in
   `BASE_MEMORY.md`. Use a secondary ML model to filter false signals on
   top of a primary LETF trend strategy. Structurally different mechanism
   (precision-over-recall).

3. **Return-stacked rotation NTSX/NTSI/NTSE** — direction #2 in
   `BASE_MEMORY.md`. 3-way rotation between US/International/EM stacked
   products. Different edge source (stacked structure + international
   diversification). Avoids the single-asset-class blind spot of both
   iter 001 and iter 002.

Pick one per future iteration. Do NOT mix.
