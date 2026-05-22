# studies/lrs — Spec

## Scope

`studies/lrs/` evaluates **Leveraged Rotation Strategies** — variations of
Gayed's SMA-regime filter on the S&P 500 with rotation into 2× and 3× LETF
proxies (SSO, UPRO). This SPEC is the canonical reference for the lrs
**scoring framework** that every phase uses.

Discovery-only under Investment Mandate §1 — no deploy, capital stays
100% in Plano C.

## Modern-era window

All scoring uses bars from **1980-01-01** onwards. Pre-1980 bars are kept
in the loaded data only for SMA-200 warmup; they never enter a window
score. Rationale:

- The 1929-32 Great Depression and the pre-Bretton-Woods monetary regime
  dominate any leveraged-strategy drawdown picture and are not
  representative of the post-1980 deep-and-liquid US equity market.
- 1980+ gives ~45 years of relevant history with major regime variations
  (1987 crash, dot-com, GFC, COVID) — enough for a 20-year rolling window
  to have ~25 non-overlapping observations and ~300 monthly-stepped
  windows.

## Strategies

| # | Name      | On-leg | Off-leg     | Signal                              |
|---|-----------|--------|-------------|-------------------------------------|
| 1 | B&H SPY   | SPYSIM | —           | always invested                     |
| 2 | B&H SSO   | SSOSIM | —           | always invested                     |
| 3 | B&H UPRO  | UPROSIM| —           | always invested                     |
| 4 | LRS-SSO   | SSOSIM | Cash (0%)   | SPY close > SMA200(SPY) at T → T+1  |
| 5 | LRS-UPRO  | UPROSIM| Cash (0%)   | SPY close > SMA200(SPY) at T → T+1  |

## Parameters

| Parameter            | Value                                            | Citation                                           |
|----------------------|--------------------------------------------------|----------------------------------------------------|
| Data source          | testfol.io synthetic (SPYSIM / SSOSIM / UPROSIM) | testfol.io merged via `scripts/extract_testfolio_json.py` |
| Scoring window       | 1980-01-01 onwards (full common history sliced)  | this SPEC                                          |
| Filter               | SMA                                              | `[leverage_for_the_long_run, p.8, p.13]`           |
| Lookback             | 200 trading days                                 | `[leverage_for_the_long_run, p.13, Table 6]`       |
| Hysteresis band      | 0% (strict cross)                                | `[leverage_for_the_long_run, p.13]`                |
| Off-leg yield        | 0% (literal cash)                                | `[leverage_for_the_long_run, p.21]`                |
| Execution lag        | Signal on close T → exposure on T+1              | Standard no-lookahead convention                   |
| Commission / spread  | 0 bps (phase-0 isolates signal)                  | Layered in later phases                            |
| Tax rate             | 15% on net annual realised gain                  | Lei 14.754/2023 art. 5°                            |
| Tax cadence          | Annual, debited at first bar of next calendar year | DARF anual (BR Receita Federal)                  |
| Loss carry-forward   | Indefinite across years                          | Lei 14.754/2023 art. 6°                            |
| Open-position M2M    | None (only closed lots taxed)                    | Matches BR realised-gain rule                      |

## Scoring framework

### Two parallel scenarios per strategy

Every strategy is scored **twice**:

1. **`tax_free`** — pretend world; uses the pre-tax equity curve.
2. **`br_lei_14754`** — Brazilian offshore-financial-asset regime under
   Lei 14.754/2023 art. 5° (15% rate) and art. 6° (indefinite loss
   carry-forward across years). Uses the post-tax equity curve.

This lets us answer "best in a frictionless world" and "best for a BR
investor with US-listed ETFs via Inter Internacional / IBKR" with one
run.

### Rolling windows

For each window length L ∈ {1, 3, 5, 10, 15, 20} years, sample
overlapping windows with a monthly step (~21 trading days). Within each
window:

- Both strategy and benchmark are **renormalised to 1.0** at the window
  start.
- The **benchmark is always B&H SPY (tax-free)** for every strategy —
  it's the universal long-only retail reference for "did we beat the
  market".

### Window-score components

Four signed components, each "positive ⇒ strategy beat benchmark on this
axis":

| Component             | Formula                                              | Weight | Squash |
|-----------------------|------------------------------------------------------|-------:|--------|
| `terminal_excess`     | `strategy_end / benchmark_end − 1`                   |   0.40 | `tanh` |
| `time_above_excess`   | `2 · (fraction of bars where strat > bench − 0.5)`   |   0.25 | none   |
| `sortino_excess`      | `Sortino(strat) − Sortino(bench)`                    |   0.20 | `tanh` |
| `calmar_excess`       | `Calmar(strat) − Calmar(bench)`                      |   0.15 | `tanh` |

Composite:
```
window_score = 0.40·tanh(terminal_excess)
             + 0.25·time_above_excess
             + 0.20·tanh(sortino_excess)
             + 0.15·tanh(calmar_excess)
```

- `tanh` keeps each unbounded component in `(-1, +1)` so a single 20×
  outlier window can't dominate the average.
- `time_above` is the **winning fraction** (ties count as 0.5 — standard
  head-to-head convention). A series scored against itself thus
  contributes exactly 0 to the composite.
- `Sortino` uses the downside-only convention from
  `src/market_lab/backtest/metrics/performance.py::sortino` (`√(mean(min(r, 0)²))`),
  matching the rest of the codebase.

### Why these four, why these weights

- **`terminal_excess` (40%)** — primary: at the end of the window, are
  you richer than buying SPY? Direct answer to the user-stated goal "no
  final o importante é sempre bater o benchmark."
- **`time_above_excess` (25%)** — consistency: did you spend the window
  ahead? Catches strategies that beat the benchmark only at one moment
  and lag the rest of the time.
- **`sortino_excess` (20%)** — risk-adjusted return with **only
  downside** volatility penalised. User explicit preference: "podemos
  considerar Sortino em vez de Sharpe."
- **`calmar_excess` (15%)** — drawdown context, but discounted because
  leveraged assets by construction have ugly Calmar.

### Per-length aggregation

For each window length L, collect every window's `window_score`:
```
length_score(L) = 0.60 · mean(window_scores) + 0.40 · p25(window_scores)
```

Rewards typical performance (mean) while penalising the worst quartile of
regimes (p25) — heavier than median, lighter than absolute worst-case.

### Final score across window lengths

```
final_score = Σ_L  weight(L) · length_score(L)

where weight = {1y:0.05, 3y:0.10, 5y:0.15, 10y:0.20, 15y:0.25, 20y:0.25}
```

Long windows dominate (~70% combined) — they're the most informative
for a long-horizon allocator — but short windows still inform the
composite. The result lives in roughly `(-1, +1)`.

### Companion statistics (reported alongside, not part of the score)

- Full-window CAGR / Sortino / MDD / terminal multiple — context.
- Per-length: window count, % windows where `window_score > 0`,
  `mean / p25 / median / min` of `window_score`, `length_score`.
- Number of switches, tax events, total tax drag (rotation curves under
  the `br_lei_14754` scenario).

## Tax model detail (Lei 14.754/2023)

Implemented in `studies/lrs/scripts/tax.py`. Each `OFF→ON → ON→OFF`
round-trip realises a signed gain. At year-end:

1. `net_year_gain = year_realised_gain + loss_carry_forward_from_prior_years`
2. If `net_year_gain > 0`: tax = `0.15 × net_year_gain`, carry-forward
   resets to 0.
3. If `net_year_gain ≤ 0`: tax = 0, carry-forward = `net_year_gain` (a
   negative number rolled into the next year, indefinitely).

The tax is debited from equity at the first bar of the following calendar
year (or at the last bar of data for the trailing open year).

**B&H curves never close a lot during the window**, so they realise zero
gain and pay zero tax. Their `tax_free` and `br_lei_14754` curves are
**identical** — this matches a BR investor holding forever and deferring
tax until exit. The terminal-sale tax is not modelled because it would
apply identically to every strategy on exit and wouldn't change ranks.

### Caveats not modelled

- **FX gain on USD/BRL**: real BR investors pay IR on currency
  appreciation too. Strategy ranks are preserved under this approximation
  because all strategies see the same FX series.
- **Day-trade rule (20%)**: not applicable — swing/positional only.
- **R$ 35k/month exemption**: doesn't apply to US-listed ETFs.

## Outputs

Written under `studies/lrs/phases/phase_0/`:

* `results/scores.json` — aggregated per-(strategy × scenario × window-length)
  scores (small).
* `results/metrics.json` — companion full-window stats per
  (strategy × scenario).
* `results/equity.csv` — 10 curves (5 strategies × 2 scenarios), keyed by
  date.
* `results/manifest.json` — full runtime config (windows, weights, data hash).
* `plots/equity_overlay.png` — log-scale equity overlay (taxed scenario).
* `plots/ratio_to_spy.png` — strategy / SPY (log scale, taxed scenario).
* `plots/score_timeline.png` — score over time, one panel per window length,
  both scenarios overlaid.
* `plots/score_by_length.png` — window-score distribution by length and
  scenario (box plot).
* `report.md` — narrative report regenerated by `run.py`.

## Run command

```
uv run python -m studies.lrs.phases.phase_0.run
```

## Out of scope

These belong in later phases:

- Walk-forward / CPCV / PBO / DSR robustness panels.
- Commission, spread, slippage modelling.
- Alternative MA windows (50, 100, 125), EMA filter, hysteresis bands.
- Alternative off-leg assets (gold, treasuries, CASHX).
- Tiingo real-ETF OOS overlay (2009+ post-inception sanity).
- FX-gain tax modelling.
- Regime stratification (bull/bear/sideways attribution).
- Any deploy verdict or capital reallocation.
