---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 4
winners_found: 0
status: iterating
latest_iteration: "004-2026-04-24"
cumulative_n_trials: 4156
---

# Strategy Hunt Loop — BASE MEMORY

**Read this file FIRST in every iteration.** Your conversation history is
empty — this file + on-disk artifacts are your only continuity.

---

## Mission

Find ONE trading strategy that:

1. **Beats SPY 1x buy-hold Sharpe by ≥ 0.10** on real data
2. **Passes the 7-gate battery** per `WINNER_CRITERIA.md` cross-dataset
3. **Is not a minor variation** of a known dead-end

Winner criteria live in `studies/strategy_hunt_loop/WINNER_CRITERIA.md`.
Dead ends that must NOT be re-tried live in
`studies/strategy_hunt_loop/DEAD_ENDS.md`.

**Hard context**: project is in mandate §1 **MAINTENANCE 100% Plano C**.
Even if this loop finds a winner, deployment requires a separate signed
override per mandate §7. Loop produces CANDIDATES, not live positions.

---

## Winners found

None yet. When found, append:

```yaml
winner:
  iteration: NNN
  hypothesis: "<one-line hypothesis>"
  config: "<cfg_id>"
  score: 100  # 90+ AND winner_conditions_met=True
  datasets_passing:
    - spy_real: {sharpe: X, cagr: Y%, mdd: Z%, gates: N/7}
    - ndx_real: {...}
    - educational: {...}
  citation_primary: "[book.slug, p.X]"
  iteration_dir: "iterations/NNN-YYYY-MM-DD-HHMM-slug/"
```

---

## Top-K strategies ranked (best of all iterations, by score)

Track the top-5 strategies ever scored across all iterations. Even
non-winners may appear here — the point is to make "semi-optimal"
strategies visible for future research.

| rank | iter | tier | score | strategy slug | primary citation | notes |
|---|---|---|---|---|---|---|
| 1 | 004 | 🥉 MARGINAL | 51/100 | `vol_managed_spy tv20_L21_cap15` | `[systematic_trading, p.107-111, p.144 ch.9]` + Moreira-Muir 2017 | single-asset vol-scaling. **6/7 gates on spy_real AND ndx_real**, G6 bootstrap CI > 0 (first in hunt loop), MDD reduced 6-9pp vs bench, Sharpe edge +0.08-0.15. Narrowly misses winner: +0.08 < +0.10 Sharpe gate on real data, DSR p=0.30-0.36 at n_trials=4156 |
| 2 | 001 | 📉 NEAR_FAIL | ~35/100 | `EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05` | `[leverage_for_the_long_run, p.13, 16]` | top synth Sharpe but fails real-data; MDD too high on spy/ndx |
| 3 | 002 | ❌ FAIL | 17/100 | `sector_momentum_clenow k5_L2` | `[stocks_on_the_move, p.76-77, 88-89, 98-99]` | canonical Clenow on 11 SPDR sectors under-deploys capital (63-75% in cash) due to ATR sizing mismatch; Sharpe ≈ 1/3 of bench |
| 4 | 003 | ❌ FAIL | 7/100 | `sector_momentum_equal_notional k9_L20_lb90` | `[stocks_on_the_move, p.70-77, p.82]` | equal-notional fixes deployment (1.55-1.76 vs iter 002's 0.25-0.37); ranking signal confirmed absent on sector ETFs (top cfgs are k9 near-EW; PBO 0.63-0.91 overfit signature) |

*(iter 001 approximate. See
`tests/test_strategy_scoring.py::TestNearMiss` for the back-filled
calculation.)*

---

## Iteration log (newest first, 6-line max per entry)

### 004 — 2026-04-24 — Volatility-managed SPY (single-asset continuous vol scaling) (🥉 MARGINAL, score 51/100)
- **Hypothesis:** Rescale SPY exposure by `target_vol / σ̂_{t-1}` (Carver `[systematic_trading, p.107-111]` / Moreira-Muir 2017) — no signal, no cross-section, just continuous inverse-vol scaling. Tests the simplest instantiation of a canonical mechanism.
- **Citations:** `[systematic_trading, p.40 ch.2, p.107-111, p.144-146 ch.9]`, `[advances_fin_ml, p.162-164, p.208-211, p.222-223 p.275, p.196-202, p.31-34]`, Moreira & Muir (2017) *JoF* 72(4) 1611-1644 DOI 10.1111/jofi.12513.
- **Scope:** 36 configs (target_vol ∈ {0.10, 0.15, 0.20} × lookback ∈ {21, 63, 126, 252} × max_leverage ∈ {1.5, 2.0, 3.0}) × 3 datasets (SPYSIM synth 40y / SPY adj_close 17y / QQQ adj_close 16y). Cost model 2 bps/unit-scale-change.
- **Result:** Grand champion `tv20_L21_cap15` Sharpe edu 0.81 (Δ+0.13) / spy 0.98 (Δ+0.08) / ndx 1.04 (Δ+0.09). Gates edu 4/7, **spy 6/7**, **ndx 6/7**. G1 PBO 0.54/**0.31**/**0.35** (real-data clean). G6 bootstrap 99.9% CI low +0.33/+0.23/+0.22 (first iteration to clear G6). G7 cross-lib parity 0.02-0.04pp. DSR p 0.06/0.36/0.30 at n_trials=4156. MDD reduced 6-9pp on real data vs bench. Winner conditions 0/5 (fails strict Sharpe edge +0.10 on spy/ndx; DSR deflator penalty too large).
- **Score breakdown:** 1:10/25 2:11/25 3:0/15 4:15/15 5:15/15 6:0/5
- **Lesson:** **Vol-scaling mechanism is real and partially validated**: 6/7 gates pass on both real-data slots, MDD reduced while CAGR up, G6 (bootstrap) clears for the first time in the hunt loop. Falls 0.02 Sharpe short of the +0.10 strict gate and DSR headroom eroded by cumulative n_trials. The productive path is NOT more param sweeps but a compounding mechanism (variance-scaling per Moreira, or vol-managed 60/40 mix). See `iterations/004-2026-04-24-vol-managed-spy/final_report.md`.

### 003 — 2026-04-24 — Equal-notional sector rotation with Clenow ranking (❌ FAIL, score 7/100)
- **Hypothesis:** Replacing iter 002's 10bps ATR-risk-parity sizing with equal-notional 1/K sizing on the same 11 SPDR sectors + Clenow adjusted-slope×R² ranking isolates the signal-edge question from the sizing-calibration issue and should surface any real edge.
- **Citations:** `[stocks_on_the_move, p.70-77, p.82, p.60, p.66-67, p.98-99, p.81]`, `[advances_fin_ml, p.298-299, p.208-211, p.222-223, p.196-202]`, Jegadeesh-Titman 1993 (JofF 48(1) 65-91).
- **Scope:** 24 configs (top_k ∈ {3,5,7,9} × lookback_slope ∈ {60,90,120} × buy_leverage ∈ {1.0, 2.0}) × 3 datasets identical to iter 002 windows.
- **Result:** Top cfg k9_L20_lb90 Sharpe edu 0.30 / spy 0.26 / ndx 0.29 (all ≈ 1/3 of bench 0.54/0.79/0.91). Deployment medians 1.55-1.76 (vs iter 002's 0.25-0.37 — confirmed full deployment). Gates edu 4/7, spy 3/7, ndx 2/7. DSR p=0.982-0.992 with n_trials=4048. PBO 0.63-0.91 (textbook overfit signature). G7 cross-lib 0.000pp (engine clean). Winner conditions 0/5.
- **Score breakdown:** 1:0/25 2:2/25 3:0/15 4:0/15 5:5/15 6:0/5
- **Lesson:** Signal is genuinely absent on SPDR universe — top cfgs are k9 (hold nearly all sectors near-EW) which is evidence against the ranking. 11-asset ETF universe is structurally too homogeneous for cross-sectional ranking momentum; aggregate market factor dominates idiosyncratic score. This finding closes sector momentum as a direction regardless of sizing. See `iterations/003-2026-04-24-0927-sector-momentum-equal-notional/final_report.md`.

### 002 — 2026-04-24 — Clenow cross-sectional momentum on 11 SPDR sectors (❌ FAIL, score 17/100)
- **Hypothesis:** Clenow book-canonical (adjusted slope × R², ATR risk-parity 10bps, SPY 200d regime) transported from S&P 500 stocks to 11 SPDR sector ETFs beats SPY risk-adjusted
- **Citations:** `[stocks_on_the_move, p.66-67, 70-77, 82, 88-89, 98-99, 219-220, 228-230]`, `[advances_fin_ml, p.208-211, 222-223, 275, 196-202]`, Jegadeesh-Titman 1993
- **Scope:** 4 configs (top_k ∈ {3,5} × leverage ∈ {1×, 2×}) × 3 datasets (sectors_long 2006-2026 SPY / sectors_spy 2009-2026 SPY / sectors_ndx 2010-2026 QQQ)
- **Result:** Sharpe edu 0.28 / spy 0.27 / ndx 0.27 (all ≈ 1/3 of benchmark). Gates edu 4/7, spy 3/7, ndx 2/7. DSR worst p=0.992. CAGR 1.6-2.2% vs bench 8.9-18.2%. MDD 16-20% trivially under bench. Winner conditions 0/5.
- **Score breakdown:** 1:0/25 2:2/25 3:0/15 4:0/15 5:15/15 (trivially — under-invested) 6:0/5
- **Lesson:** Clenow's 10bps ATR risk-parity is calibrated for individual stocks (ATR ~1-3% of price); sector ETFs have ATR ~0.3-1% of price, so sizing under-deploys by ~3× → portfolio sits 63-75% in cash. Signal edge is not tested by this iteration — sizing dominates the result. G7 cross-lib 1e-6pp so not an engine bug. See `iterations/002-2026-04-24-0906-sector-momentum-clenow/final_report.md`.

### 001 — 2026-04-24 — Crash-protected LETF trend (📉 NEAR_FAIL, score ~35/100)
- **Hypothesis:** EMA/SMA threshold + LETF + drawdown stop + CAPE de-lever beats SPY risk-adjusted
- **Citations:** `[leverage_for_the_long_run, p.13, p.16, p.21]`, `[advances_fin_ml, p.208-211]`, Campbell-Shiller 1988
- **Scope:** 4 020 configs (Phase 1 2580 stop-sweep + Phase 2 1200 risk-signal + Phase 3 240 combined + 16 cross-dataset gates)
- **Result:** Top candidate: edu Sharpe 0.87 (6/7 gates) / spy 0.68 (3/7) / ndx ~0.70 (3/7). Top SPY-real Sharpe across ALL configs = 0.853 (vs SPY 0.900). Cross-dataset spec §0: 0/16 passes. winner_conditions_met=False.
- **Score breakdown:** 1:10/25 (only edu beats Sharpe+0.10) 2:5/25 (no cross-bonus; spy/ndx miss 4/7) 3:0/15 (DSR worst p > 0.20) 4:15/15 (CAGR floor all 3) 5:5/15 (only edu MDD passes) 6:0/5
- **Lesson:** Post-2009 SPY Sharpe 0.90 is structurally hard to beat with discrete LETF+stop+signal. 3× leverage MDD is inherent. CAPE z-score has 13-year dead zone (2002-2015). WF MDD<25% gate universally FAIL for leveraged trend. See `studies/ema_sma_threshold_crash_protected/phase3_FINAL.md` + `deep_review/`.

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

~~0. Equal-notional sector rotation (Clenow ranking signal, 1/K sizing)~~ — **CONSUMED iter 003, FAIL 7/100, moved to DEAD_ENDS**. Equal-notional fixes deployment but signal confirmed absent on SPDR universe. Sector momentum direction closed.

~~1. Cross-sectional momentum on US sector ETFs (Clenow canonical)~~ — **CONSUMED iter 002, FAIL 17/100, moved to DEAD_ENDS**.

~~4. Vol-targeting + leverage-control on SPY alone~~ — **PARTIALLY CONSUMED iter 004, MARGINAL 51/100**. Single-asset vol-scaling works (6/7 gates on real data + G6 bootstrap CI > 0 for first time) but falls 0.02 Sharpe short of +0.10 strict gate. Not a dead-end — next productive iteration is variance-scaling (Moreira-Muir canonical) or vol-managed 60/40 mix.

0a. **[ITER 005 RECOMMENDATION] Moreira-Muir canonical variance-scaling
   on SPY** — replace iter 004's `target_vol / σ̂_{t-1}` (vol-scaling,
   Carver form) with `c / σ̂²_{t-1}` (variance-scaling, Moreira-Muir
   2017 *JoF* 72(4) canonical). Paper reports stronger Sharpe gains
   for variance-scaling because realised variance is more persistent
   than realised vol. Expected +0.12 to +0.15 Sharpe uplift — enough
   to clear the +0.10 strict gate. Tighter grid (12 configs, not 36)
   to preserve DSR headroom.

0b. **[ITER 005+ ALTERNATE] Vol-managed 60/40 (SPY + TLT)** — apply
   vol-scaling to a SPY/TLT blend weighted by inverse-vol. Adds
   correlation-diversification on top of vol-adaptation. Both tickers
   cached 17y. Different enough from iter 004 to avoid DSR inflation
   on the same mechanism.

2. **Return-stacked rotation NTSX/NTSI/NTSE** —
   `[risk_parity, p.5, ch.1]` +
   `[leverage_for_the_long_run, p.19-20]`. 3-way rotation based on
   6-month momentum. Never tested in this project — different edge
   source (stacked structure + international).

3. **Meta-labeling on trend signals** — AFML `[advances_fin_ml, ch.3]`
   secondary model filters false signals from a primary LETF trend.
   Turns recall-heavy primary into precision-heavy combined.
   Structurally different mechanism.

4. **Vol-targeting + leverage-control on SPY alone** —
   `[systematic_trading, ch.11]`. No stop, no signal overlay; just
   scale position by inverse-vol to hit target portfolio volatility.
   Simpler baseline. If this can't beat SPY, strategy family is dead.

5. **Cross-asset carry (FX / commodities / bonds)** —
   `[ilmanen_expected_returns]`. Different asset class entirely.
   Low correlation with equity trend → potential diversification edge.

6. **Seasonality anomalies** — Turn-of-month, Sell-in-May, Santa rally.
   Low-hanging fruit. Tested but not via rigorous 7-gate pipeline yet.

7. **Options-based tail hedging (put spread collars)** — reduces MDD
   via explicit insurance cost instead of regime timing. Different
   risk-return mechanism.

8. **HMM regime-switching on stocks-bonds correlation** —
   `[regime_change, ch.2]`. Correlation flip (risk-on vs risk-off)
   as signal; rotate SPY ↔ TLT. Different regime definition than EMA.

9. **Meta-allocation between Plano C sleeves** — use
   `portfolio-aposentadoria.md v3.5` components (GDE, AVUV, AVDE,
   AVEM, BTGD) with dynamic weights based on volatility / momentum.
   Extension of existing Plano C, not replacement.

10. **Cross-sectional factor timing (value/momentum/quality/low-vol)** —
    Asness AQR 2024. Rotate factor exposures via z-score mean-reversion.

---

## Structural dead-ends (do NOT re-test; see `DEAD_ENDS.md` for detail)

- Daily EMA/SMA threshold on 3× LETF + any overlay (iter 001)
- Drawdown-based stop-loss as primary protection mechanism (iter 001)
- CAPE as standalone single-indicator de-lever (dead 2002-2015) (iter 001)
- Walk-Forward MDD<25% gate with leveraged trend (structural conflict) (iter 001)
- Parameter variations of iteration-001 base configs (iter 001)
- Clenow canonical (10 bps ATR-risk-parity) on sector-ETF universe with top-K=3-5 — under-deploys by ~3× (iter 002)
- 4-config single-strategy-family grid when all configs land in the same near-zero regime (G1 PBO noise floor ~0.5) (iter 002)
- Clenow adjusted-slope × R² ranking with equal-notional 1/K sizing on 11 SPDR sectors — full deployment confirmed, signal still absent (iter 003)
- Cross-sectional ranking momentum on any ≤20-asset universe of diversified baskets (sector/factor/country ETFs) — too homogeneous (iter 003)

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify mandate §1** (MAINTENANCE 100% Plano C)
- **Citations obrigatórias** (CLAUDE.md Regra 2): `[book.slug, p.X]`
- **7-gate battery** mandatory per spec §0 criterion
- **DSR n_trials cumulative** — increment `cumulative_n_trials` in this
  memory's frontmatter each iteration (add this iter's config count)
- **Real data > synth**: synth-only edge does NOT count as winner
- **Pytest baseline must stay green** (currently 760 collected: 755 pass + 5 skip, post-cleanup 2026-04-24; each iteration adds to this)
- **Max 2h wall-time** per iteration (stop if running longer)
- **NEVER commit to git** — the shell `run_loop.sh` handles it

---

## Infrastructure available (reuse, don't rebuild)

Simulators:
- `src/ai_trade/backtest/strategies/ema_sma_threshold_educational.py`
- `src/ai_trade/backtest/strategies/stop_loss_and_risk_signals.py`
  (stop + risk + combined + numpy cross-lib)

Data loaders:
- `src/ai_trade/backtest/data/testfolio_loader.py` (SPYSIM synth 1986+)
- `src/ai_trade/backtest/data/macro_data_loader.py` (EBP/T10Y3M/CAPE/VIX)
- `src/ai_trade/backtest/grid/real_etf_regime_runner.py` (SPY/UPRO, QQQ/TQQQ bundles)

Validation:
- `src/ai_trade/backtest/validation/pbo.py` (PBO via CSCV)
- `src/ai_trade/backtest/validation/dsr.py` (Deflated Sharpe Ratio)
- `src/ai_trade/backtest/validation/walk_forward.py`
- `src/ai_trade/backtest/validation/cpcv.py`
- `src/ai_trade/backtest/validation/permutation.py`

Metrics:
- `src/ai_trade/backtest/metrics/performance.py` (cagr/sharpe/mdd/etc)

Signals:
- `src/ai_trade/backtest/signals/risk_score.py` (z-score sigmoid composite)

Data cache:
- `data/tiingo/daily/prices/*.parquet` — SPY, SSO, UPRO, QQQ, QLD, TQQQ,
  sector ETFs, factor ETFs, bonds
- `data/external/macro/*.parquet` — EBP/T10Y3M/CAPE/VIX
- `data/testfolio/cache/history.parquet` — SPYSIM synth 40y+

Knowledge base:
- `books/summaries/` — 33 books (see `books/MAPPING.md` for slug ↔ title)
- `knowledge/SKILL.md` — aggregated quick-reference

---

## Tips for proposing hypothesis

1. **Keep it structurally new** (not params of old) — refer to
   `DEAD_ENDS.md`
2. **Cite ≥ 1 book** from `books/summaries/` as primary source
3. **Start simplest version** (Occam razor) — if simple version can't
   beat SPY, no amount of complexity will
4. **Think about what SPY doesn't capture** — sector rotation? factor
   tilt? non-equity? timing? regime?
5. **Fail-fast criterion**: hypothesis should include a kill condition
   (e.g., "if rolling 5y Sharpe < SPY in synth, abort")
6. **Test on 3 datasets** (educational + spy_real + ndx_real) from
   the start — cross-dataset is non-negotiable

---

## How to update this file at end of iteration

After your iteration completes:

1. Bump `total_iterations` in frontmatter
2. Update `latest_iteration`
3. Update `cumulative_n_trials` (add configs tested this iteration)
4. Append 5-line entry to `## Iteration log` (newest first)
5. If dead-ends discovered, append to `DEAD_ENDS.md` (don't bloat this file)
6. If WINNER: set `status: winner` in frontmatter AND populate
   `## Winners found` section
7. If not winner: set `status: iterating`, and move the tried direction
   from `## Promising unexplored directions` to `DEAD_ENDS.md` (or
   keep it with a note if it's partially useful for future)
8. **Keep this file < 15 KB.** If it grows too long, prune old
   iteration log entries (keep latest 10 + all winners).
