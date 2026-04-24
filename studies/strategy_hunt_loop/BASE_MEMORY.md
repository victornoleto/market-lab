---
mission: "beat SPY 1x buy-hold Sharpe risk-adjusted on real data (17y window)"
total_iterations: 7
winners_found: 0
status: iterating
latest_iteration: "007-2026-04-24-1047"
cumulative_n_trials: 4237
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
| 1 | **006** | 🥈 **PROMISING** | **67/100** | `vol_managed_60_40 vt15_L21_cap20 / vt15_L63_cap20` | `[risk_parity, p.10-11, ch.1]` + `[systematic_trading, p.170-171, ch.11]` + Moreira-Muir 2017 | **best hunt-loop result yet**. +0.10 Sharpe gate cleared on spy_real (1.000 exact) + educational (+0.268). MDD floor + CAGR floor = 15/15 × 15/15 (first time 3/3 × 3/3). **4/5 strict winner conditions met** — only DSR fails at n_trials=4228. Kill #3 triggered: spy_real PBO 0.690 (vs iter 005's 0.238), blend mechanism is overfit-sensitive on 12-config grid. See `iterations/006-*/final_report.md`. |
| 2 | 005 | 🥉 MARGINAL | 59/100 | `variance_managed_spy vt20_L21_cap15` | Moreira-Muir 2017 *JoF* 72(4) DOI 10.1111/jofi.12513 + `[systematic_trading, p.107-111]` | canonical `σ^{-2}` variance-scaling. **6/7 gates on ALL 3 datasets**, real-data PBO 0.147-0.238 (cleanest in hunt loop), G2 DSR passes on educational (p=0.044 at n_trials=4192). Falls short: Sharpe edge +0.081 spy / +0.097 ndx (both just below +0.10). |
| 3 | 004 | 🥉 MARGINAL | 51/100 | `vol_managed_spy tv20_L21_cap15` | `[systematic_trading, p.107-111, p.144 ch.9]` + Moreira-Muir 2017 | single-asset vol-scaling `σ^{-1}`. 6/7 gates on spy_real AND ndx_real, G6 bootstrap CI > 0 (first in hunt loop), MDD reduced 6-9pp vs bench, Sharpe edge +0.08-0.15. |
| 4 | 007 | 🥉 MARGINAL | 50/100 | `vol_managed_blend × mom252_skip21` | `[ml_for_algo_trading, ch.4 p.86]` + `[algo_trading_chan, p.133,164, ch.6]` + Moreira-Muir 2017 Table IV | 12-1 canonical momentum overlay on iter 006 blend base. **KILL #1 + KILL #3 triggered**. Sharpe REGRESSES vs iter 006: spy 0.941 (−0.059), ndx 0.872 (−0.149). MDD improves 2-5pp on all 3 (overlay finds regime info) but CAGR drop exceeds MDD gain → net Sharpe negative. G1 PBO 0.64-0.76 fail all 3 ds even on 3-config ex-ante grid. Main lesson: **momentum overlay redundant with variance-scaling** — both track same vol-regime information. Path forward: orthogonal signals (carry, macro) or meta-labeling, not correlated ones. |
| 5 | 001 | 📉 NEAR_FAIL | ~35/100 | `EMA_N150_th5_bL3_sL0 + sl30_rec10_cape05` | `[leverage_for_the_long_run, p.13, 16]` | top synth Sharpe but fails real-data; MDD too high on spy/ndx |

*(iter 001 approximate. See
`tests/test_strategy_scoring.py::TestNearMiss` for the back-filled
calculation.)*

---

## Iteration log (newest first, 6-line max per entry)

### 007 — 2026-04-24 — Vol-managed 60/40 SPY+TLT × 12-1 time-series momentum overlay (🥉 MARGINAL, score 50/100)
- **Hypothesis:** Gate iter 006's blend by canonical 12-1 skip-a-month momentum on the equity leg. Expect +0.05-0.10 Sharpe uplift from adding an independent trend-timing axis on top of cross-asset diversification (per Moreira-Muir Table IV).
- **Citations:** `[ml_for_algo_trading, ch.4 p.86]` (12-month skip-a-month RULE); `[algo_trading_chan, p.133, 156-157, 164, ch.6]` (time-series momentum, lookback 252 from Moskowitz-Ooi-Pedersen); Moreira-Muir 2017 Table IV; Jegadeesh-Titman 1993.
- **Scope:** 3 overlay configs (mom252_skip21 / mom126_skip21 / mom378_skip21) × 1 fixed blend cfg (`vt15_L21_cap20`) × 3 datasets = 9 trials. Cumulative n_trials 4228 → 4237.
- **Result:** Top cfg `mom252_skip21` Sharpe edu 0.916 (Δ+0.254) / spy **0.941** (Δ+0.041, **regression vs iter 006's 1.000**) / ndx **0.872** (Δ−0.083, **regression vs iter 006's 1.021**). Gates edu 5/7, spy 5/7, ndx 4/7 (cross-dataset bonus applies). G1 PBO **0.643/0.762/0.746 FAIL ALL 3** (compound mechanism overfit-sensitive even on 3-cfg ex-ante grid). G6 boot CI ndx_real **−0.001 FAIL** (straddles zero). G7 xlib 0.03-0.07pp PASS. MDD reduced 2-5pp on all 3 (overlay DOES find regime info). **KILL #1 + #3 triggered.** Winner conditions 0/5.
- **Score breakdown:** 1:10/25 2:15/25 3:0/15 4:10/15 5:15/15 6:0/5
- **Lesson:** **Momentum overlay is REDUNDANT with variance-scaling** on a vol-managed blend. Both target equity-regime volatility (Gayed: SPY below-MA has 2-3× vol). Moreira-Muir Table IV's vol-managed × momentum uplift does NOT replicate on a vol-managed BLEND — the inverse-variance weighting + variance-scaling together already capture what momentum gates would add. Compounding needs ORTHOGONAL signals (carry, meta-labeling, macro state) not correlated ones. See `iterations/007-*/final_report.md`.

### 006 — 2026-04-24 — Vol-managed SPY+TLT blend with inverse-variance weighting (🥈 PROMISING, score 67/100)
- **Hypothesis:** Apply naïve risk parity (inverse-variance per leg) + Moreira-Muir portfolio-level variance-scaling to a 2-asset SPY+TLT (QQQ+TLT) blend. Cross-asset correlation diversification (ρ≈−0.25 to −0.31) adds an independent edge axis on top of single-asset vol-adaptation (iter 005).
- **Citations:** `[risk_parity, p.10-11, ch.1]` (naïve RP exact ERC for 2-asset); `[systematic_trading, p.170-171, ch.11]` (IDM ≤ 2.5); Moreira-Muir 2017 *JoF* 72(4) DOI 10.1111/jofi.12513; `[risk_parity, p.5, 16, 80-81, 109-110]` (60/40 variance decomposition, leverage rule, RORO, diversification return); Asness-Frazzini-Pedersen 2012 FAJ 68(1) SSRN 1728082.
- **Scope:** 12 configs (tv×L×cap = 2×3×2) × 3 datasets. Educational redefined to SPY+TLT 2002-2026 (24y, longest with TLT cache) with custom benchmark SPY b&h; spy_real/ndx_real keep frozen scoring.BENCHMARKS.
- **Result:** Top cfgs Sharpe edu 0.929 (Δ+0.268) / spy **1.000** (Δ+0.100 exact) / ndx 1.021 (Δ+0.066). Gates edu 5/7, spy 5/7, ndx 6/7 (all meet spec §0 minimums, +4 cross-ds bonus). CAGR floor **3/3**, MDD ceiling **3/3** (first time). G1 PBO **0.690/0.690/0.472** (degraded vs iter 005 0.238 on spy — Kill #3 TRIGGERED, blend grid overfit-sensitive). G2 DSR p=0.20-0.33 FAIL. G6 boot CI +0.175 to +0.286 all positive. G7 xlib 0.03-0.05pp PASS. ρ_stockbond −0.23/−0.30/−0.31 (diversification premise confirmed). Winner conditions **4/5** (only DSR fails).
- **Score breakdown:** 1:20/25 2:17/25 3:0/15 4:15/15 5:15/15 6:0/5
- **Lesson:** Cross-asset diversification as compounding mechanism WORKS — new hunt-loop high (67/100), first to clear +0.10 gate on 2 datasets AND clear both CAGR + MDD floors 3/3. Only structural cost: 12-config blend grid inflates PBO (0.69 vs 0.24 single-asset). Next iteration should pre-commit single cfg (no grid, no PBO issue) OR compound with momentum overlay (+0.05-0.10 expected). See final_report.md.

### 005 — 2026-04-24 — Moreira-Muir canonical variance-scaling on SPY/QQQ (🥉 MARGINAL, score 59/100)
- **Hypothesis:** Replace iter 004's `target_vol/σ̂_{t-1}` (vol-scaling) with `target_vol²/σ̂²_{t-1}` (variance-scaling, Moreira-Muir 2017 canonical). Paper argues `σ^{-2}` is sharper because variance is more persistent; expected +0.12-0.15 uplift.
- **Citations:** Moreira & Muir (2017) *JoF* 72(4) DOI 10.1111/jofi.12513; `[systematic_trading, p.107-111 ch.9]`; `[advances_fin_ml, p.162-164, 208-211, 222-223, 196-202, 31-34]`; Cederburg et al. (2020) *JFE* 138(1) counter.
- **Scope:** 12 configs (target_vol×lookback×cap = 2×3×2) × 3 datasets. 2 bps cost. 3× smaller grid than iter 004 to preserve DSR.
- **Result:** Grand champion `vt20_L21_cap15` Sharpe edu 0.849 (Δ+0.167 hunt-loop top) / spy 0.981 (Δ+0.081) / ndx 1.052 (Δ+0.097). Gates **6/7 on ALL 3 datasets** (first hunt-loop cross-dataset §0 meet). G1 PBO edu 0.571 FAIL, **spy 0.238** / **ndx 0.147** (cleanest). G2 DSR **edu PASS** (p=0.044) spy/ndx FAIL. G6 bootstrap CI +0.35/+0.21/+0.21 all pos. G7 xlib 0.02-0.04 pp. Winner 0/5 (ndx Δ+0.097 misses +0.10 by 0.003).
- **Score breakdown:** 1:10/25 2:19/25 3:0/15 4:15/15 5:15/15 6:0/5
- **Lesson:** Moreira-Muir +0.20-0.40 uplift does NOT replicate on single-asset SPY/QQQ (only +0.01 over iter 004). **Single-asset vol-adaptation family saturated at +0.08-0.10 regardless of exponent σ^{-1}/σ^{-2}**. Only path through is compounding mechanism (cross-asset or signal overlay). See final_report.md.

### 004 — 2026-04-24 — Volatility-managed SPY (single-asset continuous vol scaling) (🥉 MARGINAL, score 51/100)
- **Hypothesis:** Rescale SPY exposure by `target_vol / σ̂_{t-1}` (Carver `[systematic_trading, p.107-111]` / Moreira-Muir 2017) — no signal, no cross-section, just continuous inverse-vol scaling. Tests the simplest instantiation of a canonical mechanism.
- **Citations:** `[systematic_trading, p.40 ch.2, p.107-111, p.144-146 ch.9]`, `[advances_fin_ml, p.162-164, p.208-211, p.222-223 p.275, p.196-202, p.31-34]`, Moreira & Muir (2017) *JoF* 72(4) 1611-1644 DOI 10.1111/jofi.12513.
- **Scope:** 36 configs (target_vol ∈ {0.10, 0.15, 0.20} × lookback ∈ {21, 63, 126, 252} × max_leverage ∈ {1.5, 2.0, 3.0}) × 3 datasets (SPYSIM synth 40y / SPY adj_close 17y / QQQ adj_close 16y). Cost model 2 bps/unit-scale-change.
- **Result:** Grand champion `tv20_L21_cap15` Sharpe edu 0.81 (Δ+0.13) / spy 0.98 (Δ+0.08) / ndx 1.04 (Δ+0.09). Gates edu 4/7, **spy 6/7**, **ndx 6/7**. G1 PBO 0.54/**0.31**/**0.35** (real-data clean). G6 bootstrap 99.9% CI low +0.33/+0.23/+0.22 (first iteration to clear G6). G7 cross-lib parity 0.02-0.04pp. DSR p 0.06/0.36/0.30 at n_trials=4156. MDD reduced 6-9pp on real data vs bench. Winner conditions 0/5 (fails strict Sharpe edge +0.10 on spy/ndx; DSR deflator penalty too large).
- **Score breakdown:** 1:10/25 2:11/25 3:0/15 4:15/15 5:15/15 6:0/5
- **Lesson:** **Vol-scaling mechanism is real and partially validated**: 6/7 gates pass on both real-data slots, MDD reduced while CAGR up, G6 (bootstrap) clears for the first time in the hunt loop. Falls 0.02 Sharpe short of the +0.10 strict gate and DSR headroom eroded by cumulative n_trials. The productive path is NOT more param sweeps but a compounding mechanism (variance-scaling per Moreira, or vol-managed 60/40 mix). See `iterations/004-2026-04-24-vol-managed-spy/final_report.md`.

### 003 — 2026-04-24 — Equal-notional sector rotation with Clenow ranking (❌ FAIL, score 7/100)
Clenow adjusted-slope × R² ranking + equal-notional 1/K sizing on 11
SPDR sectors, 24 cfg grid. Sharpe 0.26-0.30 vs bench 0.54-0.91; top
cfgs land at k9 (near-EW, evidence against ranking). Full signal
failure — universe too homogeneous. See
`iterations/003-*/final_report.md` + `DEAD_ENDS.md`.

### 002 — 2026-04-24 — Clenow canonical on 11 SPDR sectors (❌ FAIL, score 17/100)
Clenow 10bps ATR-risk-parity on 11 SPDR sectors, 4 cfg grid. Sharpe
0.27-0.28 vs bench 0.54-0.91. Root cause: ATR sizing calibrated for
stocks (1-3% ATR) fails on sector ETFs (0.3-1% ATR) → 63-75% in cash.
See `iterations/002-*/final_report.md` + `DEAD_ENDS.md`.

### 001 — 2026-04-24 — Crash-protected LETF trend (📉 NEAR_FAIL, ~35/100)
EMA/SMA threshold + LETF + drawdown stop + CAPE de-lever. 4020 cfgs;
top cfg edu Sharpe 0.87 (6/7 gates) / spy 0.68 (3/7) / ndx ~0.70
(3/7). 0/16 cross-dataset winners. See
`studies/ema_sma_threshold_crash_protected/phase3_FINAL.md`.

---

## Promising unexplored directions (prioritized)

Pick ONE per iteration. Strict rule: structural novelty vs past iterations.

Consumed (moved to DEAD_ENDS or confirmed saturated): sector rotation
1/K + Clenow (iter 002/003 FAIL), single-asset vol-scaling (iter 004/005
saturated at +0.08-0.10), vol-managed 60/40 × momentum overlay (iter 007
redundant). See `DEAD_ENDS.md` for patterns to avoid.

### Iter 008 candidates (ranked by expected information gain)

0c. **[OPTION A — LOW-COST VERIFICATION] Single-config ex-ante
   vol-managed 60/40** — pre-commit `vt15_L21_cap20` (iter 006 spy/ndx
   top), no grid search, 1 cfg per dataset. Eliminates PBO entirely
   (undefined for N=1). Only +3 n_trials. Tests whether iter 006 edge
   is grid-selected or structural.

0e. **[OPTION B — ORTHOGONAL SIGNAL] Term-spread (T10Y3M) or
   credit-spread (EBP) overlay on iter 006 blend**. Macro spreads
   track bond/credit regime — structurally orthogonal to equity vol
   (iter 007's lesson: correlated signals don't compound). Data in
   `data/external/macro/`.

0f. **[OPTION C — STRUCTURALLY NOVEL] Meta-labeling (AFML ch.3)** on
   iter 006 blend. Secondary model predicts bar-level profitability
   using cross-sectional / macro features blend can't see. Most
   complex but most novel.

0g. **[OPTION D — STRUCTURAL EXTENSION] Vol-managed SPY+TLT+GLD
   3-asset blend** — gold adds real-asset / inflation factor with
   near-zero correlation to both. Widens diversification return.
   Requires IDM validation at cap ≤ 2.5.

### Deeper backlog (not yet designed as iter-next)

- Return-stacked rotation NTSX/NTSI/NTSE (`[risk_parity, p.5]` +
  `[leverage_for_the_long_run, p.19-20]`).
- Cross-asset carry (FX/commodities/bonds), `[ilmanen_expected_returns]`.
- Seasonality (turn-of-month / sell-in-May / Santa) — never through
  7-gate pipeline.
- Options tail-hedging (put-spread collars).
- HMM regime-switching on stock-bond correlation
  (`[regime_change, ch.2]`).
- Meta-allocation among Plano C sleeves (GDE/AVUV/AVDE/AVEM/BTGD).
- Cross-sectional factor timing (Asness AQR 2024).

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
- **Single-asset vol-adaptation on SPY/QQQ cannot clear +0.10 Sharpe gate regardless of exponent** (iter 004 `σ^{-1}` + iter 005 `σ^{-2}`) — family saturates at +0.08-0.10 real-data edge because SPY post-2009 Sharpe 0.90 is near the informational ceiling for signal-free vol-feedback. Only path through is compounding mechanism (cross-asset or signal overlay)
- **Time-series momentum overlay (12-1 / 6-1 / 18-1) on vol-managed 2-asset blend** REDUCES Sharpe by 0.01-0.15 on real data (iter 007) — momentum signal is redundant with variance-scaling's regime sensitivity; both track the same equity-vol information. Compounding needs ORTHOGONAL signals (carry, macro, meta-labeling), not correlated ones.

---

## Binding constraints (mandate §1, §5, §7)

- **NEVER modify mandate §1** (MAINTENANCE 100% Plano C)
- **Citations obrigatórias** (CLAUDE.md Regra 2): `[book.slug, p.X]`
- **7-gate battery** mandatory per spec §0 criterion
- **DSR n_trials cumulative** — increment `cumulative_n_trials` in this
  memory's frontmatter each iteration (add this iter's config count)
- **Real data > synth**: synth-only edge does NOT count as winner
- **Pytest baseline must stay green** (currently 770 collected: 765 pass + 5 skip, post iter 005 which added 10 variance-target specs; each iteration adds to this)
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
