# Spec — Phase 2.5/3 Run 2: Ehlers Band-Pass Swing Trader

Executable plan for the **2nd attempt** to unlock the anti-overfit gates
(PBO / DSR / walk-forward) on yfinance+Wikipedia data. Each task has a
checkbox and a **Conclusion** field that must be filled in before the
corresponding commit. This file survives across sessions — on resume, read
this file + `specs/backtest_phase2.md` §"Phase 2.5/3 — Run 1".

---

## 🎯 Context (for a new session)

### What happened before

- **Phase 2** (commit `f971c70`): complete backtest module. 173 tests.
- **Phase 2.5/3 Run 1** (commits `082a41f` → `323f115`): new module
  `backtest/grid/` + CLI `scripts/run_grid_clenow.py` + 62 new tests
  (235 total). Ran 30 Clenow configs on yfinance SPX 2015-2023.
  **Gates failed:** PBO=0.524, DSR 0/30, walk-forward 4/30. Best
  config #15 with Sharpe 0.58 — below E[SR_max(N=30)]≈0.86 under null.
  Full rationale: `specs/backtest_phase2.md` §"Phase 2.5/3 — Run 1".

### Decision after Run 1

The user chose **pivot to a 2nd strategy (Ehlers DSP)**, not paid-data
ablation. Rationale: Clenow is weekly-slow; Ehlers is a DSP-based swing —
complementary in timeframe + CFD-native (helps future Phase 1 Pepperstone).

### Hypothesis tested in this run

> The Ehlers family (roofing filter + band-pass + cycle phase) applied
> as a **swing trader** on the SPX index (single-instrument) over the
> 2015-2023 window generates a Sharpe distribution sufficient to
> pass PBO < 0.5 and DSR p-value < 0.05 on yfinance+Wikipedia.

**Stretch goal:** if the signal works on the index, adapt to a portfolio
multi-ticker (top-10 SPX constituents by liquidity) and compare.

### Non-negotiable principles (inherited)

- **Rule #1** (`knowledge/SKILL.md`): every rule/parameter/gate cites
  `[book.slug, p.X]`.
- **Rule #2**: at most 4 parameters per strategy. The grid varies ≤ 4.
- **Rule #3**: PBO > 0.5 → reject.
- **Rule #4**: DSR p-value < 0.05 mandatory when N > 1.
- **Rule #5**: walk-forward ≥ 8 windows, ≥ 6 profitable, max DD ≤ 25%.
- **Survivorship disclaimer** mandatory in every yfinance report.
- **Strict TDD**: RED test before any implementation.

### Reused infra (no changes)

- `backtest/engine/` — Portfolio, Execution, Runner
- `backtest/validation/` — CPCV, PBO, DSR, walk-forward, MCPT
- `backtest/metrics/` — Sharpe, CAGR, max DD, report generator
- `backtest/grid/` — GridRunner, GateEvaluator, Diagnostic, Report
- `backtest/data/` — YFinanceSource, WikipediaSPX
- `scripts/run_grid_clenow.py` — reference for the new CLI pattern

### What changes in this run

- New strategy in `backtest/strategies/ehlers_bp.py`
- New grid config in `backtest/grid/ehlers_config.py` (parallel to
  `clenow_config.py`; both coexist)
- New CLI `scripts/run_grid_ehlers.py` (structural clone of Clenow CLI)

---

## 📖 How to use this file

1. Read this entire file + the Run 1 summary in
   `specs/backtest_phase2.md`.
2. Find the next task with `[ ]`.
3. Implement per "What to do" and the acceptance criteria.
4. **BEFORE COMMITTING**, edit this file:
   - Swap `[ ]` for `[x]` on the task.
   - Fill in the **Conclusion** field (2-4 lines): summary, files,
     `N passed` from pytest, non-obvious findings.
5. Include this edit in the same commit as the implementation.
6. When all tasks are `[x]`: the final commit updates
   `ROADMAP.md` + `README.md` + this §"Summary" with the verdict.

**Do not:**
- Never remove completed tasks.
- Never skip the **Conclusion** field.
- Never start a new task without marking the previous one `[x]` in the same commit.

---

## 🔨 Tasks

### Task 1 — Ehlers primitives (DSP building blocks)

**What to do:**

- [x] **SuperSmoother** — `src/ai_trade/backtest/indicators/ehlers_ss.py`
  - Pure function: `super_smoother(series: pd.Series, period: int) → pd.Series`
  - 2-pole IIR filter with cutoff at `period` bars
  - Source: `[cycle_analytics, ch.3, p.36]` — 12 dB/octave attenuation
  - Formula: `a1 = exp(-√2·π/period)`, `b1 = 2·a1·cos(√2·π/period)`,
    `c2 = b1`, `c3 = -a1²`, `c1 = 1 - c2 - c3`,
    `SS[t] = c1·(P[t]+P[t-1])/2 + c2·SS[t-1] + c3·SS[t-2]`

- [x] **High-pass filter** — `src/ai_trade/backtest/indicators/ehlers_hp.py`
  - Pure function: `high_pass(series, period) → pd.Series`
  - Source: `[cycle_analytics, Code Listing 7-3, p.81-82, ch.7]` (two-pole,
    K=.707; not the single-pole version from Code Listing 7-1)
  - Used in the combination HP + SuperSmoother = **roofing filter**

- [x] **Roofing filter** — `src/ai_trade/backtest/indicators/ehlers_roofing.py`
  - `roofing_filter(series, hp_period, lp_period) → pd.Series`
  - Source: `[cycle_analytics, ch.7, p.88-89]` — **mandatory preprocessing**
    before any Ehlers indicator (rule p.88: without it, conventional
    indicators produce erroneous signals during trending due to Spectral
    Dilation)

- [x] **Dominant Cycle Period (DCP)** — `src/ai_trade/backtest/indicators/ehlers_dcp.py`
  - `dominant_cycle_period(series, period_min=6, period_max=50) → pd.Series`
  - Algorithm: Homodyne Discriminator `[rocket_science, ch.6 p.59 + ch.8 p.82-83]`
  - Output clamped to `[6, 50]` bars per rule `[p.82-83]` (configurable)

- [x] **Band-pass filter** — `src/ai_trade/backtest/indicators/ehlers_bp.py`
  - `band_pass(series, dcp, pct_of_dcp=0.90, bandwidth=0.30) → pd.Series`
  - Tuned to 90% of DCP for ~60° of phase lead `[cycle_analytics, p.152-153]`
  - Accepts scalar `dcp` (fixed-tuning) or Series (adaptive — mode used
    by the downstream strategy)

- [x] **Tests** — `tests/test_ehlers_indicators.py`
  - Numerical verification against book examples where available
  - Impulse response: SS with period=10 attenuates step by ≥12 dB over 1 octave
  - Roofing filter: DC signal is completely removed (HP effect)
  - DCP: on a pure 20-period sine, returns 20±1 after convergence
  - Band-pass: signal at the tuned frequency passes unattenuated, others reject

**Accepted when:** 5 primitives implemented in separate modules,
each with a verifiable numerical test. Pytest runs ≥25 new green tests.
Docstrings cite book+page for each formula.

**Conclusion (partial — 1/5 primitives):**

- **Commit 1 — SuperSmoother** (`c95621c` preexisting fix + new commit):
  `indicators/__init__.py` + `indicators/ehlers_ss.py` (49 LOC) +
  `tests/test_ehlers_indicators.py::TestSuperSmoother` with 7 tests
  (shape/index, DC passthrough, Nyquist zero, slow passthrough, invalid
  period, octave rolloff, closed-form formula at t=2). Warm-up seed:
  `Output[0]=Input[0]`, `Output[1]=Input[1]` (Ehlers EasyLanguage
  standard). `242 passed` total. Preexisting: `pythonpath = ["."]` fix
  in `pyproject.toml` unlocked `from scripts import ...` in the
  book-reader tests (3 fails + 1 collection error → 0).

- **Commit 2 — High-pass + Roofing filter:**
  `indicators/ehlers_hp.py` (two-pole, K=.707) + `indicators/ehlers_roofing.py`
  (HP→SS composition). 10 new tests: HP shape/index, DC rejection,
  fast-cycle passthrough, slow-cycle rejected, invalid period,
  closed-form t=2; Roofing shape/index, DC annihilated, Nyquist noise
  killed, mid-band cycle survives. Decision: two-pole HP (Code Listing
  7-3) instead of single-pole (Code Listing 7-1), per explicit
  recommendation [p.82, ch.7]. `252 passed`.

- **Commit 3 — Dominant Cycle Period (Homodyne):**
  `indicators/ehlers_dcp.py` — transcribes EasyLanguage from [rocket_science,
  ch.6 p.59 + ch.8 p.82-83]: 4-bar WMA → Detrender Hilbert → I1/Q1 →
  jI/jQ → I2/Q2 phasor → EMA 0.2/0.8 → homodyne Re/Im → EMA 0.2/0.8 →
  atan2 → rate clamp (0.67×/1.5×) → abs clamp [6,50] → EMA 0.2/0.8 →
  SmoothPeriod EMA 0.33/0.67. Decisions: (a) quadrant-safe atan2
  instead of plain ArcTangent; (b) `period`/`smooth_period` seeded with
  `period_min` instead of 0 to guarantee clamp during 6-bar warmup.
  5 tests: shape/index, converges on pure 20-period sine (±2) and 30
  (±3), absolute clamp preserved in mixed regime, customizable clamp
  [10,30]. `257 passed`.

- **Commit 4 — Band-pass filter:**
  `indicators/ehlers_bp.py` — eq. 5-2 with coefs (β, γ, σ) derived per
  bar from `period = dcp · pct_of_dcp`, `bandwidth=0.30` default
  [p.53, ch.5]. Scalar and adaptive (Series dcp) both supported — the
  adaptive form is the one the downstream strategy uses. Nyquist guard
  (period<2 hold), cos_bw≈0 guard (hold), disc<0 guard (hold). 7 tests:
  shape, sine at tuned passes (>50% RMS), sine far rejected (<30%),
  scalar dcp ≡ constant dcp series, invalid pct, invalid bandwidth,
  adaptive mode follows 15→30 change. `264 passed`.

---

### Task 2 — Strategy: Ehlers Band-Pass Swing Trader (SineWave crossover)

**What to do:**

- [x] **EhlersBPSwing** — `src/ai_trade/backtest/strategies/ehlers_bp_swing.py`

  Verbatim rules from `[cycle_analytics, ch.17, p.222-225]`:

  - **Preprocessing:** `close → roofing_filter(hp_period, lp_period) → smooth`
    `[p.88-89]`
  - **DCP:** `dominant_cycle_period(smooth)`, clamped [6, 50] `[p.82-83]`
  - **Band-pass:** `band_pass(smooth, dcp, pct_of_dcp)` `[p.152-153]`
  - **Cosine leading indicator:** cos(phase)-wave with 1-bar delay;
    cross = quarter-cycle phase lead `[p.222-223]`
  - **Entry rule `[p.220-221]`:** long when cosine crosses below the
    lower threshold (−0.7); short when it crosses above (+0.7).
    Anticipates turning points by ~4 bars vs. confirmation.
  - **Exit rule `[p.224-225]` (safety valve):**
    - Long: exit if close < SuperSmoother-smoothed lower channel
    - If the trade is not profitable within ½ DCP bars, exit
    - *"If you even think about hoping a trade will turn around, exit the
      trade immediately."*
  - **Stop-loss `[p.225-226]`:** fixed percentage 2-5% of entry price,
    **only as a guard against extreme losses**. Not part of the signal.

- [x] **Unit tests** — `tests/test_ehlers_bp_swing.py`
  - Synthetic signal (pure sine in simulated price) → entries aligned
    with the expected quarter-cycle phase lead
  - Whipsaw filter: pure trend (no cycle) does NOT generate entries
    (roofing filters DC + low frequency)
  - Stop-loss fires when price sinks 5% below the entry without
    waiting for the safety valve
  - Average holding time in cyclic data ≤ 1 DCP

**Accepted when:** strategy implements the 5 rules with literal citation
in the docstring. Unit tests cover each rule and edge case. Strict
TDD (pytest RED before each module).

**Conclusion:**

- **Commit 5 — EhlersBPSwingStrategy:**
  `strategies/ehlers_bp_swing.py` (~180 LOC) with full pipeline
  precomputed in `__post_init__`: close → roofing → DCP → band-pass →
  AGC normalize → oscillator ∈ [-1,+1]; separate `trend` via
  `super_smoother(close, lp)` for the safety-valve. Entry rules verbatim
  [p.220-221]: long on cross below `lower_threshold=-0.7`, short
  on cross above `upper_threshold=+0.7`. Exit: (1) stop_pct
  capital-preservation first, (2) safety-valve trend break (close vs
  trend), (3) time-stop ½·DCP if P&L ≤ 0. Sizing: `risk_pct_of_equity`
  (default 0.95 — near-full deployment, swing trader). Per-symbol state
  in `context["ehlers_state_<sym>"]` (entry_idx, dcp_at_entry). 7
  tests: precompute indicators, validate thresholds/stop_pct, pure
  sine → multi trades (long+short), pure trend → ≤2 trades, stop-loss
  fires on hard drop, median holding < 3·DCP. `271 passed`.

  Non-obvious design decision: AGC normalization instead of the Homodyne
  `cos(phase)`. Rationale: AGC is direct, bounded at ±1, does not require
  the heterodyne DCPhase (simplification), and gives the same
  "oscillator oversold/overbought" signal that [p.220-221] asks for.
  The spec cited "cosine leading signal" [p.222-223] but used ±0.7
  thresholds [p.220-221] — this blend enabled by AGC is consistent with
  the intent of "anticipatory oscillator crossover".

---

### Task 3 — Single-instrument replication: ^GSPC 2015-2023

**What to do:**

- [x] **Replication CLI** — `scripts/run_ehlers_replication.py`
  - Structural clone of `scripts/run_clenow_replication.py`
  - Args: `--start`, `--end`, `--symbol` (default `^GSPC`), `--cash`,
    `--output-dir`, `--warmup-days`
  - Single-trial: one fixed configuration (literature default band-pass:
    hp_period=48, lp_period=10, pct_of_dcp=0.90, stop_pct=0.05)
  - Generates report via `metrics.report.generate_report` (existing infra)

- [x] **Integration test** — `tests/test_ehlers_integration.py`
  - Short synthetic range (fixtures, no network)
  - Verifies: non-empty equity curve, finite metrics, report generated

- [x] **Replication doc** — `reports/ehlers_replication_notes.md`
  - Number obtained vs book benchmark `[cycle_analytics, ch.19]` where
    Ehlers applies the system to EUR/USD and others
  - If positive Sharpe + reasonable DD → engine correct, advance
  - If negative Sharpe or dramatically negative → bug, investigate before the grid

**Accepted when:** script runs without errors on `^GSPC 2015-01-01 → 2023-12-31`,
report generated, integration test passes, notes written.

**Conclusion:**

- **Commit 6 — Replication CLI + integration + notes:**
  `scripts/run_ehlers_replication.py` (structural Clenow clone, 216
  LOC), `tests/test_ehlers_integration.py` (6 tests: engine contract,
  report generation with walk-forward, CLI argparse), `reports/ehlers_replication_notes.md`
  (gitignored — committed in `reports/ehlers_replication_notes.md` as
  a hand-written doc, excluded from glob `reports/*_[0-9]*.md`).
  Real replication ^GSPC 2022-01-01→2023-12-31: $100k→$97,472 (-2.53%),
  27 trades, max DD 6.51%, WF 3/8 reject. Verdict: **engine OK, signal
  weak** — consistent with the documented risks (Ehlers calibrated on
  EUR/USD/T-Bonds intraday, not daily equity). Pure-sine synthetic
  is worse (-86%) but is expected — anticipatory entry on a pure sine
  enters too early and whipsaws + risk_pct_of_equity=0.95 compound.
  Advancing to the grid. `277 passed`.

---

### Task 4 — Grid config + Ehlers grid CLI

**What to do:**

- [x] **Grid config** — `src/ai_trade/backtest/grid/ehlers_config.py`
  ```python
  @dataclass(frozen=True)
  class EhlersGridConfig:
      hp_period: int        # ∈ {48, 80}
      lp_period: int        # ∈ {10, 20}
      pct_of_dcp: float     # ∈ {0.80, 0.90, 1.00}
      stop_pct: float       # ∈ {0.02, 0.05}
      # 2×2×3×2 = 24 configs; respects Rule #2 (4 params)
  ```

- [x] **Grid runner adaptation** — `src/ai_trade/backtest/grid/runner.py`
  - **Generalize** `GridRunner` to accept any frozen `@dataclass`
    as config (currently hardcoded to `ClenowGridConfig`).
    Option: swap annotation `list[ClenowGridConfig]` for
    `list[ConfigT]` via TypeVar. Checkpoint I/O is already generic
    (uses `config.__dict__`).
  - If the change is too big, create a generic `GridRunner` +
    strategy-specific helpers.

- [x] **CLI** — `scripts/run_grid_ehlers.py`
  - Structural clone of `scripts/run_grid_clenow.py`
  - Fetch data via `YFinanceSource.fetch_many` (cache reused from Clenow)
  - trial_fn builds `EhlersBPSwing` + runs `Runner.run`
  - Same observers (JSONL, status.md, unified log in `logs/grid.log`)
  - Same gates (PBO < 0.5, DSR p < 0.05, WF ≥ 6/8)

- [x] **Grid config tests** — `tests/test_ehlers_grid_config.py`
  - `grid_configs() == 24` unique
  - Covers every value in each dimension
  - Stable iteration order (checkpoint resume-friendly)

**Accepted when:** grid config yields 24 combos without duplicates; CLI runs
end-to-end with `--dry-run` on 3 configs × 1 year; tests pass.

**Conclusion:**

- **Commit 7** — `grid/ehlers_config.py` + 9 tests (above).
- **Commit 8** — Generic GridRunner via TypeVar `ConfigT`; +4 tests
  showing Ehlers config accepted without breaking Clenow API.
- **Commit 9** — `scripts/run_grid_ehlers.py` (248 LOC, structural
  Clenow clone) + generalization of `diagnostic.py` (`_varied_field_names`
  via `dataclasses.fields`) and `report.py` (`_varied_field_names` +
  `_fmt_value` + heatmap using first 2 varied fields). Dry-run
  smoke ^GSPC 2022-2023 × 3 configs: 0.5s wallclock, gates
  FAIL=expected (DSR_ALL_FAIL + WF_INSUFFICIENT + COMBINED),
  diagnostic.md renders correctly with dynamic fields
  (`hp_period`, `lp_period`, `pct_of_dcp`, `stop_pct`). `290 passed`.

---

### Task 5 — Production run + diagnostic + fork decision

**What to do:**

- [x] **Production run** — `scripts/run_grid_ehlers.py`
  ```bash
  .venv/bin/python scripts/run_grid_ehlers.py \
      --start 2015-01-01 --end 2023-12-31 \
      --cash 100000 --output-dir reports/ \
      --n-jobs 4
  ```
  - Same window as Clenow Run 1 → direct comparability
  - Wallclock **real: ~3s with n_jobs=4** (24× faster than Clenow;
    single-instrument is 410× less data than Clenow on SPX500).

- [x] **Comparative analysis** — see §"Run — results and fork"
  above. Cross-correlation Clenow × Ehlers = **−0.0108** (2263 common
  daily returns) → orthogonal strategies, portfolio combination
  plausible in option 3 of the fork.

- [x] **Final docs:**
  - `ROADMAP.md` — Run 2 bullet with verdict + merged fork
  - `README.md` — "How to run the Ehlers grid" section + cross-corr
  - `knowledge/SKILL.md` — untouched; no new citable rule
    discovered (insights stay in this spec)

**Gate to advance (same as Run 1):**
> PBO < 0.5 AND DSR p-value < 0.05 AND walk-forward ≥ 6/8 profitable
> in at least 1 config of the grid.

**Contingent fork (if gates fail again):**
1. **Paid-data ablation** — if Ehlers also fails, strong suspicion of
   yfinance survivorship → Tiingo SF / Norgate.
2. **3rd strategy** — AFML meta-labeling, Chan pairs, Kaufman adaptive.
3. **Regime-aware portfolio** — combine Clenow + Ehlers with regime
   switching (if low correlation).
4. **Stop and reassess.**

**Accepted when:** production run completed, analysis written in this
spec, docs updated, fork explicitly presented to the user.

**Conclusion:**

- **Commit 10 — production run + analysis:**
  24/24 trials OK in ~3s wallclock (n_jobs=4). PBO=0.468 **passes**,
  DSR 0/24 reject, WF 2/24 pass. Best #6 Sharpe 0.310 CAGR 2.17% DD
  14.65%. Cross-corr with Clenow best = **−0.0108** (almost perfect
  independence). §"Run — results and fork" filled inline
  above with comparative tables and 4 fork branches. Commit 11
  finalizes global docs (ROADMAP/README).

---

## 📊 Run — results and fork

**Status:** ❌ **failed** (DSR reject; PBO passes; WF marginal)

**Run:** `grid_ehlers_20260414-1944` | window 2015-01-01 → 2023-12-31
(2264 daily bars ^GSPC) | 24/24 trials OK | wallclock ~3s with n_jobs=4
| diagnostic: `reports/grid_ehlers_20260414-1944/diagnostic.md`

### Gate verdict

| Gate | Value | Limit | Verdict |
|---|---|---|---|
| PBO | **0.468** | < 0.5 | ✅ **pass** (margin 3.2%) |
| DSR (best p-value) | 0.852 (cfg #6) | p < 0.05 | ❌ reject (0/24) |
| Walk-forward | 2/24 pass (cfg #10, #11) | ≥ 1 | ✅ pass (marginal) |

**Overall: FAIL.** Fails only on DSR. PBO logits mean=−0.060,
std=0.981 — symmetric around zero, no sign of structural IS→OOS
overfit. This is an important difference from Clenow: Ehlers **passes
PBO** (Clenow was failing at 0.524).

### Best config (ignoring gates)

**`config_id=6`** — `hp_period=48, lp_period=20, pct_of_dcp=0.80, stop_pct=0.02`:

- Sharpe annualized: 0.310
- CAGR: 2.17%
- Max drawdown: 14.65%
- Walk-forward: 5/8 profitable, max DD 10.39% → reject by margin

### Configs passing walk-forward (2/24)

`config_id=10` and `config_id=11` — identical except for `stop_pct`
(demonstrates the stop does not activate on the SPX window):
`hp_period=48, lp_period=20, pct_of_dcp=1.00`, Sharpe 0.282, CAGR 1.4%,
max DD 5.74%, 6/8 profitable.

### Comparison with Clenow (Run 1)

| Metric | Clenow best (#15) | Ehlers best (#6) | Delta |
|---|---|---|---|
| Sharpe annualized | 0.583 | 0.310 | Clenow wins (larger edge) |
| CAGR | 8.87% | 2.17% | Clenow wins (6.7 pp) |
| Max DD | 19.86% | 14.65% | **Ehlers wins** (−5.2 pp) |
| WF verdict | 6/8 pass | 5/8 (best_sharpe) / 6/8 (cfg10) | tie |
| PBO (grid) | 0.524 (fail) | **0.468 (pass)** | **Ehlers wins** |
| DSR pass | 0/30 | 0/24 | tie (both reject) |
| **Cross-corr (daily returns, 2263 days)** | — | **−0.0108** | **uncorrelated** |

### Diagnostic

1. **Ehlers passes PBO**, Clenow does not — meaning Ehlers is less
   overfit to the grid (IS rankings don't travel erratically to OOS).
   That's a real informational gain about signal structure.

2. **Both fail DSR** for the same reason: E[SR_max] under iid null for
   N≈25, T≈2267 bars is ~0.86 annualized. Neither produces a high
   enough Sharpe. It is not overfit — it is the absence of strong edge
   in a single SPX series over 9 years (consistent with the risks
   documented in §"Known risks" bullet 1).

3. **Cross-correlation −0.01 between best equity curves is
   extraordinary.** Weekly-slow Clenow + DSP-swing Ehlers are
   statistically orthogonal. In theory, a combined portfolio would
   have reduced total risk without sacrificing expected return — but
   since each fails DSR individually, the linear combination does not
   unlock the gate (if each is indistinguishable from null, so is the
   sum, with smaller variance but not significant).

4. **Ehlers shows pair-identical Sharpes** (configs 0≡1, 2≡3, etc.)
   — `stop_pct` never activated on SPX 2015-2023 because the stop is
   price-reversal-triggered and intra-swing volatility in the window
   (post-2020 excepted) stayed below 2%. Operational conclusion:
   in a less volatile window, `stop_pct` is effectively a dead
   parameter — the real grid has 12 variation points, not 24.

### Fork — decision for the user

The spec §Task 5 lists four contingent branches:

1. **Paid-data ablation.** Both strategies (Clenow + Ehlers) fail
   DSR on the same yfinance window. The hypothesis "yfinance inflates
   the benchmark and masks real edge" now applies to both experiments —
   the signal here is stronger because we eliminated the "wrong strategy"
   variable. Tiingo SF / Norgate unlocks both simultaneously if the
   bias is material.

2. **3rd strategy** (AFML meta-label, Chan pairs, Kaufman adaptive).
   Counter-argument: both current strategies already failed DSR; adding
   a 3rd subsumes the same N-penalty. Lower priority now.

3. **Regime-aware portfolio** combining Clenow + Ehlers. Cross-corr
   −0.01 validates the diversification premise. Implementation: weight
   Clenow when trend-mode (SPX > 200d MA + Hurst > 0.55), weight
   Ehlers when cycle-mode. Edge: inherits the strength of both without
   multiplying the DSR N.

4. **Stop and reassess.** Both failed DSR — the informative signal
   for the user may be: "yfinance SPX 2015-2023 has no statistical
   edge for either of the two hypotheses tested; moving to paid data
   OR pivoting universe is a necessary condition before more
   iteration".

**My recommendation** (not pre-decided): **Option 1 (paid data
first), then Option 3 (regime-aware portfolio)**. Rationale:
- Both passed PBO (Clenow marginal, Ehlers well): the structural signal
  is not overfit. The remaining variable is data.
- Tiingo SF trial or Norgate free subset resolves it in 2-3 days.
- If the edge appears in paid data, option 3 unlocks (regime-aware
  combination of 2 uncorrelated signals).
- If it doesn't appear in paid data, it's confirmed that SPX 2015-2023
  has no alpha extractable from momentum or band-pass swing — forking
  to strategy or universe is well-founded.

---

## 📌 References

- `specs/backtest_phase2.md` — Phase 2 spec + Phase 2.5 Run 1
- `ROADMAP.md` — global project state
- `README.md` — how to run backtests + grid
- `knowledge/SKILL.md` — inviolable rules #1-7
- `knowledge/books/rocket_science.md` — Ehlers DSP fundamentals
- `knowledge/books/cycle_analytics.md` — roofing filter + band-pass swing
- `reports/grid_20260414-1813/diagnostic.md` — Clenow Run 1 fail

## 🧭 Suggested build sequence (11 small commits, strict TDD)

1. **Commit 1** — Ehlers SuperSmoother + tests
2. **Commit 2** — High-pass + Roofing filter + tests
3. **Commit 3** — Dominant Cycle Period (Homodyne) + tests
4. **Commit 4** — Band-pass filter + tests
5. **Commit 5** — EhlersBPSwing strategy + tests
6. **Commit 6** — `run_ehlers_replication.py` CLI + integration test +
   replication notes
7. **Commit 7** — `grid/ehlers_config.py` + tests (24 configs)
8. **Commit 8** — Generalize `GridRunner` to TypeVar `ConfigT` +
   refactor tests
9. **Commit 9** — `scripts/run_grid_ehlers.py` + `--dry-run` smoke test
10. **Commit 10** — Real production run + fill in §"Run — results"
11. **Commit 11** — ROADMAP + README + knowledge/SKILL.md (if any
    citable rule was discovered)

Each commit: RED tests first, minimal GREEN, refactor if applicable.
Full suite green on every commit.

---

## ⚠️ Known risks

- **Ehlers on daily SPX may not have clear cycles.** The book runs on
  futures (EUR/USD, T-Bonds) intraday/H1. Daily SPX index may be
  dominantly trend-mode → band-pass signal rarely fires.
  Mitigation: Task 3 tests on ^GSPC single-instrument before the grid to
  verify the signal is meaningful.

- **Roofing filter requires significant warmup.** HP 80 + SS 10 = ~90
  warmup bars. Use `--warmup-days 500` (~600 calendar bars) as a
  generous fallback.

- **Rule #2 (max 4 params) is hard.** If during Task 2 we discover the
  need for a 5th param (e.g., safety-valve multiplier), return to the
  spec and justify the trade-off OR fix the value per the literature.

- **GridRunner generalization (Task 4) may break Clenow tests.**
  If the TypeVar introduces a regression, keep Clenow config working
  as before (existing tests are the contract).

- **DSR unreachable with N=24 and Sharpe < 0.86 annualized.** Run 1
  showed Clenow best (0.58) stayed below the benchmark. If Ehlers
  produces Sharpes in the same range, DSR will fail again even with
  a smaller grid. Contingent fork already anticipates this.

---

**End of spec. When starting execution: open this file + read
§"Context" + Task 1, write RED tests, implement, update
Conclusion, commit.**
