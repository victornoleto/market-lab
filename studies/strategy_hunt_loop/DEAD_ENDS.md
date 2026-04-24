# Dead ends — structural failures to avoid

Read this before proposing a hypothesis. Any direction that matches
structurally with an entry below is **forbidden**.

---

## From iteration 001 — crash-protected LETF trend

Complete study: `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`
+ `deep_review/` + `cross_dataset_gates.md`.

### Exact configurations tested (1 340 × 3 datasets = 4 020 configs)

- **Bases**: SMA/EMA × lookback {50, 100, 150, 200} × threshold
  {0, 2, 5, 10}% × buy_leverage {1, 2, 3}× × sell_leverage {cash, −1, −2, −3}×
- **Overlays**:
  - stop_loss % ∈ {15, 20, 25, 30, 35, 40}
  - re-entry modes: next_signal, time_cooldown {21, 63, 126 days},
    recovery_trigger {5, 10, 15}%
  - risk signals: EBP, term_spread, CAPE, VIX, composite
  - λ ∈ {0.3, 0.5, 0.7}
  - combinations of stop + risk

### What failed (do NOT re-test)

1. **Daily EMA/SMA threshold + LETF + stop + risk signal** — no
   config combination produced Sharpe edge in real data. Top SPY-real
   Sharpe: 0.853 (vs SPY 0.900, gap −0.047).

2. **Drawdown-from-peak stop as primary protection** — mechanically
   saves MDD but proportionally costs CAGR; net Sharpe neutral. Stop
   trigger at 15-30% fires 9 times in 40y; overlay removes ~9 pp MDD
   at cost of ~3 pp CAGR.

3. **CAPE z-score sigmoid as single indicator** — chronically above
   threshold 2002-2015 (13-year dead zone); signal output ≈ 0 during
   entire decade, zero de-levering. Signal resumed 2017+ but too
   little of the sample.

4. **Sigmoid signal on EBP, term_spread, VIX individually** — each
   fires ≤ 30% of bars in bull regime; individual indicators don't
   move the needle.

5. **Composite equal-weight risk signal** — diversification didn't
   compound the edge; composite de-lever 0-6 pp MDD, net effect on
   Sharpe negligible.

6. **next_signal re-entry** — misses 60-70% of recovery in fast
   crashes (COVID-style). `time_cooldown` and `recovery_trigger` are
   marginally better but still leak 30-50% of post-crash rally.

7. **3× LETF (bL=3) with any overlay** — structural MDD floor ~44%
   (synth) / ~48% (real). Cannot reach spec target 40% within CAGR
   corridor. Leverage is destiny.

8. **Walk-Forward G3 gate with leveraged trend** — universally FAILS
   for bL≥2 configs. Each 6-month OOS window contains either a crash
   (MDD > 25%) or a rally (OK) but rarely both; 8 clean windows out of
   history is structurally incompatible with trend-follow on LETF.

9. **Cross-dataset consistency for top-1 CAGR bases** — 4 bases
   appear in all 3 top-20 lists; 16 (base, combo) pairs gated; **0/16**
   pass spec §0.

### Structural principles derived

- **Post-2009 SPY Sharpe 0.90 is hard to beat** with any discrete
  trend-follow + leverage + overlay in equity market alone.
- **3× leverage MDD is inherent**, not fixable by overlay.
- **Crash signals (CAPE/EBP/VIX/term) are feast-or-famine**: strong
  in 1996-2000 and 2017-2022, dead elsewhere. No signal works for
  all regimes.
- **Drawdown-based stops cost CAGR proportional to reduction**; at
  CAGR-neutral, MDD reduction is ~5-10pp (not 20+ pp).

---

## From iteration 002 — Clenow canonical on SPDR sector ETFs

Complete study: `studies/strategy_hunt_loop/iterations/002-2026-04-24-0906-sector-momentum-clenow/final_report.md`.

### What failed (do NOT re-test)

1. **Clenow canonical (10 bps ATR-risk-parity) on 11 SPDR sectors with
   top-K ∈ {3, 5} and leverage ∈ {1×, 2×}** — Sharpe 0.22-0.28 vs
   benchmark SPY/QQQ 0.54-0.91 on all 4 configs across all 3 datasets.
   Score 17/100 ❌ FAIL. Winner conditions 0/5.

2. **The specific root cause: ATR sizing mismatch.** Clenow's 10 bps risk
   factor `[stocks_on_the_move, p.88-89, 228-230]` was calibrated for
   individual S&P 500 stocks with ATR20 ~1-3% of price. Sector ETFs have
   ATR20 ~0.3-1% of price (intra-sector diversification lowers per-bar
   volatility). Shares = equity × 0.001 / ATR at ATR $1-3 and price
   $70-200 gives $5k-10k per position. Top-K=3 × $7.5k = ~$22k deployed
   on $100k → **77% in cash**. Top-K=5 × $7.5k = ~$37k deployed → **63%
   in cash**. Even at buy_leverage=2.0×, portfolio is still 25-50% in
   cash. The strategy is structurally under-deployed; the signal edge (if
   any) is masked by cash drag.

3. **4-config single-family grid on a near-zero-return regime** — G1 PBO
   lands at 0.52-0.57 (barely above the 0.5 noise floor). When every
   config in the grid produces similar near-zero returns, IS-best vs
   OOS-best is effectively a coin flip. PBO cannot distinguish skill
   from noise in this regime.

4. **Bootstrap 99.9% CI low of −0.40** on all 3 datasets means the
   stationary bootstrap distribution of Sharpe straddles zero with wide
   margin — **no evidence of statistical edge even under favorable
   resampling**.

### Don't re-test

- Clenow canonical 10 bps ATR-risk-parity on sector ETFs at top-K ≤ 5.
- Small grid (≤ 4 configs) on a single strategy family when the family
  is under-deployed — PBO is uninformative.

### Structural principles

- **Transporting a book strategy across asset classes requires risk-
  budget recalibration per universe.** Clenow's 10 bps is a per-position
  VaR constraint that depends on asset ATR/price. Moving from 1-3% ATR
  stocks to 0.3-1% ATR sector ETFs requires ~3× larger risk factor
  (e.g., 30 bps) to achieve the same portfolio utilization. This is NOT
  optimization in Clenow's sense `[p.219-220]` — it's first-principles
  calibration to match a new universe's volatility.

- **Unlevered equal-risk sizing breaks with < 20 assets.** Clenow's
  portfolio math `[p.228-230]` assumes 20-50 positions at 10 bps each
  gives ~20-50% daily-impact budget. With only 3-5 sectors at 10 bps, the
  portfolio only uses 3-5% daily-impact budget → most capital sits idle.

- **G1 PBO needs a grid with return dispersion.** A grid where all
  configs produce similar near-zero returns gives PBO ≈ 0.5 by construction
  (coin flip), regardless of whether the strategy has real edge. Before
  gating on PBO, verify the grid spans configs with materially different
  returns.

---

## Structural dead-end categories

Any new hypothesis that falls into one of these is automatically
rejected — require qualitatively different mechanism:

- [ ] Daily timeframe + leveraged ETF + discrete stop
- [ ] Single-indicator de-lever on CAPE / EBP / VIX / term spread
- [ ] Equal-weight composite of the above 4 indicators
- [ ] SMA/EMA crossover filter on SPY with leverage
- [ ] Drawdown-based stop-loss as the primary risk control
- [ ] Parameter variations of (lookback, threshold, buy_L, sell_L,
      stop%, re-entry_param, λ) on any of the above
- [ ] Clenow canonical 10 bps ATR-risk-parity on sector-ETF universe
      with top-K ≤ 5 (iter 002 — capital under-deployed by ~3×)
- [ ] Small grids (≤ 4 configs) of a single strategy family where every
      config lives in the same near-zero-return regime (G1 PBO = 0.5
      noise floor, uninformative)

---

## Things that might still work (in principle)

These are NOT dead-ends, just untested:

- Weekly/monthly timeframe (not daily)
- Cross-sectional (not time-series)
- Different asset class (FX / commodities / bonds) or multi-asset
- Factor rotation (value/momentum/quality/low-vol dynamic weights)
- Options overlay (put spreads as tail insurance)
- ML-based meta-labeling on top of primary signal
- Regime-switching HMM on correlation or macro state
- Seasonality-based entries/exits
- Dynamic vol-targeting (Carver) without any leverage
- Return-stacked ETFs (NTSX/NTSI/NTSE) with rotation

The `## Promising unexplored directions` section of `BASE_MEMORY.md`
prioritizes these.

---

## How to add to this file

At end of each iteration that FAILED, append a section:

```markdown
## From iteration NNN — <short hypothesis>

### What failed
- (5-line summary)

### Don't re-test
- (exact patterns to avoid)

### Structural principles
- (1-2 lessons learned)
```

If the failure is a minor variation of an earlier dead-end, just
append a bullet to the relevant section instead of a full section.
