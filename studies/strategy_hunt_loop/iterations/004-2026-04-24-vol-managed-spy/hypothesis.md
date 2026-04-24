# Iteration 004 — Volatility-managed SPY (single-asset ex-ante vol scaling)

## Hypothesis

Rescale SPY daily exposure by `target_vol / realised_vol_{t-1}` (clipped
to a leverage cap) so the portfolio targets a fixed annualised
volatility. The scaling is **continuous** (no binary on/off, no stop,
no ranking) and **single-asset** (SPY only). When realised vol is low,
the strategy levers up; when realised vol spikes, it delevers.
Moreira & Muir (2017, *Journal of Finance* 72(4) 1611-1644) show that
vol-managed market portfolios produce alphas of ~5% per year vs buy-and-
hold in US equities: the mechanism is that realised variance is
persistent but expected returns are not, so inverse-variance scaling
increases exposure in good (low-vol) regimes and reduces it during
crashes (2008, COVID). Carver's *Systematic Trading* pre-dates Moreira-
Muir but independently arrives at the same prescription for retail CTAs:
volatility standardisation is the most important single technique in
the framework `[systematic_trading, p.40, ch.2]`, and the target vol is
chosen as `SR_realistic / 2` (Half-Kelly) `[systematic_trading, p.144,
ch.9]`. This iteration tests the **simplest possible instantiation of
the mechanism** — no signal overlay, no cross-section, no regime
filter — to settle the question of whether single-asset vol scaling
alone produces a Sharpe edge on the 3 benchmark datasets.

## Primary citation

`[systematic_trading, p.107-111, p.144 ch.9, p.40 ch.2]` — volatility
standardisation as the core position-sizing primitive; target vol as
Half-Kelly proxy.

## Additional citations

- `[advances_fin_ml, p.162-164]` — position sizing from predicted target
  vs. realised variance; motivates the `σ̂_{t-1}` lag (no look-ahead).
- `[advances_fin_ml, p.298-299]` — 1/N as default Bayesian prior; the
  **kill criterion** is informed by this: if vol scaling can't beat 1.0×
  SPY by a margin that exceeds estimation noise (Sharpe +0.05 with DSR
  p<0.05), the simpler prior wins.
- `[advances_fin_ml, p.208-211]` — PBO via CSCV (G1 gate).
- `[advances_fin_ml, p.222-223, p.275]` — DSR with cumulative
  `n_trials` (G2 gate).
- `[advances_fin_ml, p.196-202]` — stationary bootstrap CI (G6 gate).
- External: **Moreira, A., & Muir, T. (2017). "Volatility-Managed
  Portfolios."** *Journal of Finance* 72(4), 1611-1644. DOI
  10.1111/jofi.12513. Claim: inverse-variance scaling of the market
  portfolio produces alphas of ~5% / year vs buy-and-hold across US
  equity factor portfolios, 1926-2015. Their formula is
  `s_t = c · (1 / σ̂²_{t-1})` (variance-scaled, not vol-scaled); the
  Carver form `target_vol / σ̂_{t-1}` is the **vol-scaled** analog and
  is more common in retail CTA practice. **We test vol-scaling
  (Carver's form)** because it has a cleaner leverage interpretation
  and matches the existing `vol_target.py` primitive. If the result is
  positive, a follow-up iteration can test Moreira's variance-scaling.

## Edge source

SPY 1× buy-hold has time-varying realised volatility (range ~9-45% ann
across the 1986-2026 window) but earns roughly the same expected
return per unit of time regardless of regime. Inverse-vol scaling
shifts exposure **away** from high-vol periods (which are empirically
below-average return on a forward basis, per Moreira-Muir) and
**toward** low-vol periods. The result is a higher Sharpe portfolio
without a signal-based market-timing call — just risk parity across
time.

## Datasets

- **educational** (SPYSIM synth 1986-2026, 40 years, n~10 151 bars):
  contains 1987 crash, dot-com, 2008 GFC, COVID. The longest out-of-
  sample window; Moreira-Muir themselves operate on 1926-2015 CRSP
  data so the effect should manifest if real.
- **spy_real** (Tiingo SPY 2009-06-25 → 2026-04-20, ~17 y): post-GFC
  bull regime with low realised vol for much of 2011-2019. Vol scaling
  at `target_vol=0.15` with `cap=2.0` would lever ~1.5-2.0× for long
  stretches. Hardest benchmark to beat (SPY Sharpe 0.90).
- **ndx_real** (Tiingo QQQ 2010-02-12 → 2026-04-20, ~16 y): QQQ has
  higher realised vol and tail events (2022 tech crash) — gives vol-
  scaling more to react to. Toughest Sharpe benchmark (0.955).

## Kill criteria (pre-committed)

**Hypothesis is falsified if ANY of the following occurs at end of
Stage 3:**

1. **Signal is absent.** Best-config annualised Sharpe does NOT exceed
   the buy-hold benchmark by ≥ 0.05 on at least 2 of 3 datasets.
   (Moreira-Muir report Sharpe gains of +0.20 to +0.40 on market
   factors; we require a much weaker +0.05 just to keep the hypothesis
   alive. If we don't even clear +0.05, single-asset vol scaling
   doesn't work and we move on.)
2. **Overfit signature.** G1 PBO > 0.6 across all 3 datasets (iter 003
   style overfit: IS-best / OOS-best rank reversal severe; grid is
   gaming noise rather than expressing a robust mechanism).
3. **Leverage-cap artefact.** The top-scoring config only wins because
   it's pinned against `max_leverage` > 95% of the time — this means
   the "vol-target" is degenerate (pure leverage, no adaptation).
   If the best config's `scale_cap_hit_frac` > 0.95, the edge is not
   from vol scaling.

If NONE of these fire, the hypothesis stays alive and goes to Stage 4
for full gate battery + scoring.

## Expected budget

- **Configs to test:** 36 (target_vol × lookback × max_leverage grid)
- **Wall-time:** ~5 min (returns-level computation, no Runner overhead)
- **Files to create:**
  - `run_backtests.py` — load SPY/QQQ/SPYSIM returns, apply 36 vol-
    target configs, write `results.json` with per-(dataset, config)
    Sharpe/CAGR/MDD + scaled-returns series for gate computation.
  - `compute_gates_and_score.py` — compute G1-G7 from `results.json`
    and call `scoring.score_strategy(...)` to produce `verdict.json`.
  - `numpy_reference.py` — hand-rolled numpy vol-target + Sharpe
    computation for G7 cross-lib parity (±3 pp CAGR).
  - `final_report.md` — full verdict prose + score breakdown.
  - `verdict.json` — machine-readable scoring result.
  - `tests/test_iter_004_vol_managed_spy.py` (in project tests dir) —
    G7 parity test + per-config determinism test.

## Implementation plan

### Grid design

36 configs = target_vol × lookback × max_leverage:

- `target_vol ∈ {0.10, 0.15, 0.20}` — Carver's Half-Kelly gives ~10%
  for SR~0.5, scaling up to ~20% for aggressive regimes
  `[systematic_trading, p.144-146, ch.9]`.
- `lookback ∈ {21, 63, 126, 252}` — Moreira-Muir use 21 (monthly);
  Carver uses 25-50 typical; project canonicals are 63/126/252. Span
  all four to test signal stability across sampling windows.
- `max_leverage ∈ {1.5, 2.0, 3.0}` — 1.5× is retail conservative;
  2.0× is SSO-like; 3.0× is UPRO-like (hits the "leverage is destiny"
  MDD floor from iter 001).

This is large enough that PBO is not stuck at 0.5 noise floor (iter
002 lesson) but not so large that DSR n_trials dominates.

### Execution cost model

Per bar, if scale `s_t ≠ s_{t-1}` (which happens every bar because
`σ̂_{t-1}` changes continuously), there's a rebalance cost. Model as:

```
turnover_t = |s_t - s_{t-1}| * price_{t-1}
cost_bps = turnover_t * 0.02  # 2 bps round-trip for SPY (tight)
```

2 bps is Inter-style tight — SPY half-spread on the listed exchange is
~0.3 bps mid-day, and Inter charges zero commission for equity
`[project_plano_b_broker_inter memory]`. This is conservative enough
that if the strategy still produces an edge it's not hiding behind
zero-cost assumptions.

### Datasets + loaders

- `educational`: `data/testfolio/cache/history.parquet`, column
  `SPYSIM`, take `pct_change()` → daily returns.
- `spy_real`: `data/tiingo/daily/prices/SPY.parquet`, filter to
  2009-06-25 → 2026-04-20, use `close.pct_change()`.
- `ndx_real`: same but QQQ, 2010-02-12 → 2026-04-20.

### G7 cross-lib reference

Hand-rolled numpy implementation in `numpy_reference.py`:

```python
def apply_vol_target_np(returns, target_vol, lookback, max_leverage):
    r = np.asarray(returns, dtype=float)
    n = len(r)
    scales = np.full(n, np.nan)
    for t in range(lookback + 1, n):
        window = r[t - lookback:t]
        std = window.std(ddof=0) * np.sqrt(252)
        if std > 0:
            s = target_vol / std
        else:
            s = max_leverage
        scales[t] = min(max(s, 0.0), max_leverage)
    scaled = scales * r
    return scaled[lookback + 1:]
```

Compare final equity + annualised Sharpe + CAGR against the pandas-
based `apply_vol_target` on all 36 × 3 = 108 config/dataset pairs.
Expect ±3 pp CAGR parity per G7 `[advances_fin_ml, p.31-34]`.

### Gate battery

- **G1 PBO** (CSCV on the 36-config grid per dataset, `n_splits=16`).
- **G2 DSR** using cumulative `n_trials = 4048 + 108 = 4156` (iter 003
  cumulative + this iter configs × datasets).
- **G3 WF 6/8** — each dataset split into 8 equal chronological
  windows; top cfg runs in each; require ≥ 6 with positive Sharpe and
  MDD < 25%. (Note: with `max_leverage=3.0`, MDD<25% per window is
  likely to FAIL — iter 001 structural finding; we still test it.)
- **G4 OOS 70/30** — re-pick the in-sample best on the first 70% of
  bars, apply to last 30%, require OOS Sharpe > 0.
- **G5 FWD post-2020** — stress window 2020-01-01 → end; require
  Sharpe > 0.
- **G6 Bootstrap 99.9% CI low > 0** — stationary bootstrap on daily
  returns of best cfg, `n_boot=2000`, block length via `pbb` rule.
- **G7 Cross-lib ±3 pp CAGR** — numpy reference agreement per above.

### Scoring

Call `scoring.score_strategy(metrics, gates, cumulative_n_trials=4156)`.
Use `BENCHMARKS` defaults from `scoring.py` (matches the
`WINNER_AND_RANKING.md` table exactly): educational Sharpe 0.68 / CAGR
11.47% / MDD 55.14%; spy_real 0.90 / 14.97% / 33.70%; ndx_real 0.955 /
19.18% / 35.12%.
