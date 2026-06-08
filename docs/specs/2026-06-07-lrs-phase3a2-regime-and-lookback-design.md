# Design — LRS Phase 3A-2 (Alternative Regime Signals) + Phase 3C (Lookback Study)

- **Date:** 2026-06-07
- **Status:** Design approved (brainstorming). Research-only.
- **Scope:** Two sequential phases of the local `lrs/` restart. Phase 3A-2 first;
  Phase 3C depends on its result.
- **Mandate:** Maintenance mode. This design authorizes **no deploy, no
  paper-trade label, no mandate change, no capital allocation**. Overfit gates
  remain diagnostic during evolution; promotion would still require the full
  mandate gates `[advances_fin_ml, p.208-211]`.

---

## 1. Context & motivation

The `lrs/` restart has reached Phase 3A. Findings so far:

- **Phase 2** established the exposure geometry that actually drives drawdown
  control: target leverage (adjacent-ETF ladder) + diversified risk-off sleeve +
  realized-vol throttle. Best SPY: L2.00 / `50 ZROZ / 25 GLD / 25 CASH` /
  `RV21 ≤ 30%` → after-tax CAGR 15.44%, MDD −39.28%. Best QQQ: L1.75 /
  `40 ZROZ / 40 GLD / 20 IEF` / `RV63 ≤ 40%` → 19.46%, −42.58%.
- **Phase 3A** (sparse risk-on vote) tested confirmation filters **ANDed** onto
  the base `SMA200 & vol_gate`. Negative result: no filter beats the `none`
  control. Key structural insight: an SMA hysteresis band as an **AND-gate** is
  identical to `none` in 36/36 configs — ANDing onto `price > SMA200` can only
  further restrict risk-on, and its one distinct behaviour (holding through a dip
  below the SMA) lives precisely on days the SMA gate already blocks. **To test a
  trend-hold mechanism it must REPLACE the SMA gate, not AND onto it.**

This design covers the two follow-ups the user requested:

1. **Phase 3A-2** — test alternative regime signals as **replacements** for
   `price > SMA200`, head-to-head against the SMA200 baseline.
2. **Phase 3C** — answer *"why SMA 200?"*. The number 200 is community-popular
   (golden-cross folklore) but unexamined in this restart. We want a principled
   answer that avoids two opposite overfit traps: (a) blindly trusting 200, and
   (b) sweeping many windows and promoting the best.

### 1.1 Prior art (spin-off line `studies/lrs/`, now canonical in `letf-lab`)

Lookbacks WERE swept before, but in the spun-off line, with the exact
"sweep-and-pick-best" methodology this design rejects, and under different
mechanics (single-asset, synthetic LETFs). Relevant findings to cross-check
against (not to inherit blindly):

- A 97-window sweep (20–500) found **EMA > SMA universally for QQQ**, optimum
  ~220–255 (centre ~245).
- SMA optimum is **not universal**: SPY/GLD ~250–300, QQQ ~250, but small-cap /
  sector (IWM/XLK/DIA) ~100. The SPY empirical optimum sat **~250–295, not 200** —
  200 is not even the empirical best, just the round popular number.
- A prototype adaptive-lookback selector ("metamorfose") **won at 1× but LOST on
  leveraged sleeves (SSO/UPRO)** — "leverage amplifies the cost of lookback
  switches" (whipsaw). This is the central caution for the LRS, which is
  inherently leveraged.

---

## 2. Guardrails (apply to both phases)

- **Branches & geometry:** SPY and QQQ, each on its own 3 branch-specific bases
  from Phase 3A (Phase 2 top + 2 one-lever neighbours). Same DARF tax, weekly
  cadence, lag sweep `n = 0..5`.
- **Scoring:** Phase 2 `score`, `drawdown_tier`, and `practical_pass` kept
  **verbatim** for cross-phase comparability.
- **No-lookahead:** every signal `.shift(1)`-lagged; warmup/NaN ⇒ `False`
  (risk-off), matching `build_sma_signal` and the Phase 2 `vol_gate`.
- **Self-contained:** new indicators live in `lrs/lib/indicators.py`; no import
  from `studies/`.
- **Anti-overfit, pre-registered:** the lookback robustness map is a *diagnostic*
  that reports the whole surface; we pre-commit to NOT promoting the argmax.
  Adaptive complexity is gated on evidence of fragility `[advances_fin_ml,
  p.208-211]`, `[trading_systems_methods, p.27, p.939]`.

---

## 3. Phase 3A-2 — Alternative Regime Signals (replacement)

### 3.1 Mechanism

Replace the trend component of the Phase 2 base signal, keeping the vol throttle
and exposure geometry unchanged:

```
signal = G(underlying) & vol_gate(base.vol)
```

`G` is the regime signal. `SMA200` is the control and reproduces the Phase 2
result for that base+lag exactly (built-in sanity check vs
`lrs/results/phase02_target_leverage_vol.csv`).

| `G` | Family | Rule (all `.shift(1)`-lagged) | Citation |
|---|---|---|---|
| `SMA200` | control | `price > SMA(200)` | `[leverage_for_the_long_run, p.13]` |
| `EMA200` | responsive MA | `price > EMA(200)` | `[systematic_trading, p.283]` |
| `hyst200 band5%` | hysteresis | enter `price > SMA200`, hold until `price < SMA200×0.95` (state machine, REPLACES SMA gate) | `[trading_systems_methods, p.383]` |
| `hyst200 band8%` | hysteresis | same with `×0.92` | `[trading_systems_methods, p.383]` |
| `ROC200 > 0` | momentum | `price.pct_change(200) > 0` | `[stocks_on_the_move, p.58, p.60]` |
| `Clenow200 > 0` | trend quality | annualized slope×R² over 200d `> 0` | `[stocks_on_the_move, p.70-77, p.98]` |

**Lookback held fixed at 200 across all forms** to isolate signal *form* from
*lookback* — the window question is entirely Phase 3C's. (Clenow's canonical is
90 and momentum's is often 252; noted, but fixed at 200 here for a clean
form-only comparison.)

### 3.2 Grid & output

2 branches × 3 branch-specific bases × 6 regime forms × lag `0..5` = **216 rows**.

Output mirrors Phase 3A: `lrs/results/phase03b_regime_signals.csv`, `REPORT.md`,
`plots/`. Report sections: top overall, best by branch, best by regime form, a
**form-vs-SMA200 delta** table (does any form beat the control on *both*
branches and across lags?), rolling hit rates, turnover/tax, verdict.

### 3.3 Files

- `lrs/lib/indicators.py`: add `ema_gate(prices, span)`. Reuse existing
  `trend_hysteresis_gate`, `roc_gate`, `clenow_gate`.
- `lrs/phases/phase03b_regime_signals/` (`__init__.py`, `run.py`, `README.md`).
  `run.py` clones the Phase 3A runner; a `regime_gate(context, form_spec)`
  dispatch produces `G` (cached per `(branch, form)`); `desired_targets` uses
  `signal = G & vol_gate` (the SMA AND-gate is replaced, not augmented).
- `tests/test_lrs_phase03b.py`: `ema_gate` correctness/lag; hysteresis-as-gate
  can extend risk-on below the SMA (distinct from SMA200 now); `SMA200` form
  reproduces the Phase 2/3A base signal.

> Naming note: directory uses `phase03b_*` (the bear-sleeve "Phase 3B" is blocked
> — no inverse tickers in the cache — so the slug is reused for this regime
> phase; the REPORT title reads "Phase 3A-2").

### 3.4 Expected reading (honest prior)

Hysteresis-as-replacement is the likeliest to move anything (reduces whipsaw by
holding through dips). EMA may help QQQ. ROC/Clenow as a sole gate are noisier
than the MA level and will likely lose, but the test is cheap and conclusive.

---

## 4. Phase 3C — Lookback: Robustness, Theory Anchor & Gated Adaptive

Runs **after** Phase 3A-2, on the winning regime form(s) — minimum `SMA` and
`EMA`; if 3A-2 promotes hysteresis, include it too. Structure follows the
approved "gated" approach: diagnose → anchor → adapt-only-if-fragile.

### 4.1 Part 1 — Robustness map (diagnostic, not optimizer)

- Sweep windows `{50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400}`
  (13 points) on the Phase 2 geometry, across the 3 bases per branch, for the
  studied regime form(s). Grid for the default SMA+EMA study: 13 windows × 2
  forms × 3 bases × 2 branches × lag `0..5` = **936 rows**. The surface plots and
  plateau test use the **best-score lag per (form, base, window)** cell, so the
  window axis is read at each window's own best lag (consistent with how Phase
  3A/3A-2 report best per cell).
- Deliverable is the **full surface**: after-tax CAGR / MDD / Calmar / score vs
  window, one curve per branch, with cross-check markers for the spin-off
  findings (SPY ~250–295, QQQ ~245, "200 popular").
- **Pre-registered plateau rule** (prevents cherry-picking): a *robust plateau*
  exists if there is a contiguous band of windows ≥ 150 days wide within which
  Calmar stays within 10% of that band's best. If **200 ∈ plateau** → verdict
  *"200 is a robust adequate point, not magic."* If the surface is a narrow peak
  (best window beats neighbours by >10% with no qualifying plateau) → **fragile**
  → opens the Part 3 gate.
- Pre-committed: **do not promote the argmax**; the deliverable is the robustness
  verdict, not "the best window" `[trading_systems_methods, p.939]`,
  `[advances_fin_ml, p.208-211]`.

### 4.2 Part 2 — Theory anchor (ex-ante, no performance peeking)

Computed from the price/return series alone, before any backtest scoring:

- **Volatility half-life** — from the decay of squared-return autocorrelation /
  GARCH(1,1) persistence (`α+β`), giving the horizon over which a vol shock
  reverts `[volatility_trading, p.39, p.53-54]`. Informs the adaptive driver.
- **Return autocorrelation half-life** — the lag at which return autocorrelation
  decays, a proxy for trend-persistence horizon. Informs the trend window.
- Map the half-life(s) to a "natural" window (e.g. EWMA span↔decay
  `[systematic_trading, p.283]`) and check: does it land **inside the empirical
  plateau**? Near 200/250? This yields a **citable, non-arbitrary** justification
  for the window — the opposite of "200 because it's popular."

### 4.3 Part 3 — Adaptive lookback (gated on Part 1 = fragile)

Runs only if Part 1 finds no robust plateau.

- **Pre-registered mechanism (fixed before seeing results):** window varies
  ex-ante with the realized-vol regime —
  `w_t = clip(w_base × vol_target / realized_vol_t, w_min, w_max)` (high vol →
  shorter/more-responsive window; low vol → longer). Driver, `w_base`,
  `vol_target`, `w_min`, `w_max` fixed in advance.
- **Honest comparison** vs the best fixed window AND vs 200, **reporting turnover
  and the leveraged-sleeve result explicitly**, because the spin-off found
  lookback-switching cost is amplified by leverage. If the adaptive does not beat
  the fixed window net of turnover, it is recorded as a negative.
- If Part 1 says "robust", Part 3 does not run; the report concludes *"fixed
  window is robust; adaptive not warranted"*, honouring the prior-art caution.

### 4.4 Files & output

- `lrs/lib/indicators.py`: add `adaptive_vol_window` helper (Part 3 only).
- `lrs/phases/phase03c_lookback_study/` (`__init__.py`, `run.py`, `README.md`).
- Output: `lrs/results/phase03c_lookback_study.csv` (+ a half-life/theory table
  CSV), `REPORT.md`, `plots/` (surface per metric/branch, plateau annotation,
  adaptive comparison if triggered, spin-off cross-check).
- `tests/test_lrs_phase03c.py`: plateau-rule detection on synthetic flat vs
  peaked surfaces; half-life estimator on a series with known decay; adaptive
  window respects `clip` bounds and is `.shift(1)`-lagged.

---

## 5. Verification

```bash
# Phase 3A-2
uv run python -m lrs.phases.phase03b_regime_signals.run
uv run pytest tests/test_lrs_phase03b.py tests/test_lrs_phase00.py

# Phase 3C (after 3A-2)
uv run python -m lrs.phases.phase03c_lookback_study.run
uv run pytest tests/test_lrs_phase03c.py tests/test_lrs_phase00.py
```

Manual checks:
- 3A-2: `SMA200` form rows reproduce the Phase 2 base+lag numbers exactly.
- 3A-2: CSV has 216 rows; report + plots regenerated.
- 3C: the robustness surface and the pre-registered plateau verdict are reported;
  the spin-off markers appear on the plot; the theory window is compared to the
  plateau; Part 3 runs **iff** Part 1 = fragile.

Docs after each run: append a phase entry to `lrs/MEMORY.md`; update
`docs/CURRENT_STATE.md` (and `docs/PROJECT_HISTORY.md` only if the public
narrative shifts); record explicitly research-only / no deploy / no paper-trade /
no mandate change. Keep unrelated `studies/return_stacked_core/...` working-tree
changes untouched.

---

## 6. Sequencing & dependencies

1. Implement + run **Phase 3A-2**. Read the form-vs-SMA200 result.
2. Implement + run **Phase 3C**, studying SMA + EMA (+ hysteresis if 3A-2
   promoted it). Part 3 gated on Part 1.
3. Only after both: revisit whether to proceed to Phase 4 (mandate validation
   gates) or close the family.

Each phase gets its own implementation plan (writing-plans). This design doc
covers the arc; the immediate plan is Phase 3A-2.

---

## 7. Citations

- SMA200 Gayed regime; vol as enemy of leveraged compounding —
  `[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.4-7]`.
- EMA decay / EWMA span↔half-life — `[systematic_trading, p.283]`.
- Hysteresis / asymmetric whipsaw band — `[trading_systems_methods, p.383]`.
- Clenow slope×R² — `[stocks_on_the_move, p.70-77, p.98]`.
- ROC / momentum effect — `[stocks_on_the_move, p.58, p.60]`.
- Volatility mean-reversion & GARCH persistence (half-life) —
  `[volatility_trading, p.39, p.53-54]`.
- Parameter parsimony / robustness; IS-OOS discipline; never iterate after OOS —
  `[trading_systems_methods, p.939]`, `[trading_systems_methods, p.27, p.917-919]`.
- Overfit / deflated performance — `[advances_fin_ml, p.208-211]`.
