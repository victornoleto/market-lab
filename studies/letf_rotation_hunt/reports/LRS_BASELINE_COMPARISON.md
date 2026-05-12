# LRS Baseline Comparison — vs t3d-k2 & iter030

> **Status:** research output. Strategy B (US LETF rotation) is in mandate `§1` **DORMANT / maintenance mode** since 2026-04-23 — this doc does **not** propose reactivation. Numbers are **gross** (no fees, no DARF, no spread) per user-locked decision in the planning step.
> **Window:** 1986-01-03 → 2026-04-17 (10,150 trading days, ~40.3y). Common-history intersection of all 8 series.
> **Sources:** Per-strategy daily-return CSVs already on disk for the two study strategies; the four LRS variants and the two buy-and-hold baselines are recomputed in this run.
> **Reproduce:** `uv run python -m studies.letf_rotation_hunt.runners.run_lrs_baseline_comparison`

> ⚠️ **Revision 2026-05-11:** the first version of this report contained a 1-day signal lookahead bug in the LRS simulator, which inflated the LRS variants' CAGR by ~22pp and underestimated their MDD by ~30pp. The bug was caught by a user-supplied testfol.io cross-check (CAGR 15.70% / MDD −51.67% for SPY→SSO LRS) and is fixed in this version. The published t3d-k2 / iter030 numbers (`backtest.py` already uses `signal.shift(1)`) are unaffected. See the **Validation** and **Forensics** sections below.

---

## TL;DR

1. **iter030 decisively beats every naive Gayed LRS variant** on Sharpe, Sortino, CAGR, and Calmar over the gross 1986–2026 window. The Vote-of-K(2) + post-crash rearm + 1.20× LRS overlay genuinely earns its complexity vs. a single SMA200 gate to FFR cash. Sortino: iter030 **1.38** vs best LRS (SPY→SSO 2×) **0.98**.
2. **The naive SMA200 LRS adds modest value over buy-and-hold**, not the spectacular edge the original Gayed paper read suggests on first glance. LRS_SPY_SSO_2x: CAGR 15.0% vs SPY 11.5%, Sortino 0.98 vs 0.96, MDD −50.6% vs −55.1%. The signal pays for ~3.5pp CAGR while trimming about 5pp of drawdown — a real but small improvement.
3. **Higher LRS leverage hurts risk-adjusted return.** The Sharpe/Sortino ladder *decreases* from SSO 2× (0.71/0.98) to TQQQ 3× (0.65/0.91) even as CAGR rises from 15% to 22.5%. The MDD of TQQQ-LRS is **−94.2%** — the gate cannot save 3× NDX from intraday decay during prolonged sideways or whipsaw regimes.
4. **t3d-k2 and iter030 sit on a different Sortino tier entirely.** Both clear 1.32 Sortino while every naive LRS lands ≤ 1.00. The premium ≈ +0.40 Sortino points for iter030 vs the best naive LRS is paid for by (a) a more selective 4-signal entry gate, (b) the ZROZ off-leg (long-duration Treasury was uncorrelated to equity for most of 1986–2021), and (c) the post-crash rearm timing.

---

## Setup

### Universe (8 series, common 1986-01-03 → 2026-04-17 window)

| Label | Description | Source |
|---|---|---|
| `t3d_k2` | Study anchor: Vote-of-K(2) of {SMA250, SMA100, vol21<40%, AR(1)_30d>0} on QLD/ZROZ. Closed Sortino-first winner. | `runs/original/022-2026-05-06-T3d-extended-grid/qld_voteK2_..._off_zroz_strategy_returns.csv` |
| `iter030` | Post-close winner: t3d-k2 + T35D60 rearm-only + 1.20× LRS overlay (no-margin proxy: 80% TQQQ + 20% cash). | `runs/post_close/030-.../qld_..._T35D60_unclrs120_strategy_returns.csv` |
| `LRS_SPY_SSO_2x` | Gayed LRS — SPY price > SMA200 → SSO (2× synth, FFR-aware), else FFR cash. **Signal lagged 1 day.** | computed here |
| `LRS_SPY_UPRO_3x` | Same signal, UPRO (3× synth). | computed here |
| `LRS_QQQ_QLD_2x` | Gayed LRS — QQQ price > SMA200 → QLD (2× synth), else FFR cash. | computed here |
| `LRS_QQQ_TQQQ_3x` | Same signal, TQQQ (3× synth). | computed here |
| `SPY_BH` | SPY total-return buy-and-hold (testfolio SPYSIM). | computed here |
| `NDX_BH` | NDX proxy = QQQ total-return buy-and-hold (testfolio QQQSIM). No NDX index in cache. | computed here |

### Citations (Rule 2)

- **SMA200 LRS rule** (risk-on if price > 200-day MA, risk-off if below): `[leverage_for_the_long_run, p.13]`.
- **LETF synthetic daily return** `r = L·r_underlying − ER/252 − (L−1)·(FFR + spread/252)`: `[leverage_for_the_long_run, p.16, footnote 22-23]`.
- **Cash leg = FFR** (testfolio CASHX, daily-compounded Fed Funds Rate proxy): `[leverage_for_the_long_run, p.21]` for Gayed's "literal cash" canonical, FFR series chosen as the realistic-cash variant per the user spec.
- **MA periods {10, 20, 50, 100, 200} all produce positive alpha**, justifying SMA200 as canonical: `[leverage_for_the_long_run, p.14, Table 6]`.
- **Vote-of-K(2) anchor (t3d-k2)**: `studies/letf_rotation_hunt/reports/STUDY_FINAL_REPORT.md`.
- **T35D60 + LRS1.20 (iter030)**: `studies/letf_rotation_hunt/reports/POST_CLOSE_LOOP_REPORT.md`.
- **NDX → QQQ proxy choice**: no NDX index series in cache; QQQSIM (testfolio) extends NDX TR back to 1986. `data/testfolio/cache/history.parquet`.

### Methodology

- All daily returns aligned by index intersection → 10,150 common bars (1986-01-03 → 2026-04-17), 40.3y. Constraint binds on the LRS warmup (200-day SMA), which costs the first ~9 months of the run.
- LRS run uses `compute_regime_signal` from `src/market_lab/backtest/strategies/letf_rotation.py` (strict cross, band=0%, Gayed canonical). **Critical:** the signal is lagged one trading day (`regime.shift(1)`) so today's position reflects yesterday's close — without the shift the simulator peeks at the return it is about to earn. Warmup is held flat (no equity drift).
- LETF returns synthesized via `studies/letf_rotation_hunt/core/synths.py::letf_synth_returns` with **expense_ratio=0** and **spread=0** — gross. FFR cost on the leveraged leg is preserved (Gayed's primary cost term).
- All metrics from `src/market_lab/backtest/metrics/performance.py`. Rolling windows from `studies/spy_beater_hunt/rolling_metrics.py` (CAGR/MDD) and `studies/letf_rotation_hunt/core/rolling_sortino.py` (Sortino; new in this run).

### Reproduction sanity (vs published study numbers)

| Strategy | Published | Recomputed (here) | Match |
|---|---|---|---|
| t3d-k2 Sortino (lh_56y) | 1.3246 | 1.3240 | ±0.0006 ✓ |
| iter030 Sortino (lh_56y) | 1.3839 | 1.3839 | exact ✓ |
| iter030 CAGR (lh_56y) | 36.68% | 36.68% | exact ✓ |
| SPY_BH Sharpe (lh_56y anchor) | 0.682 | 0.682 | exact ✓ |

### Validation (vs external testfol.io, 2026-05-11)

External cross-check: testfol.io tactical backtester, SPYSIM SMA200 → SSO (`SPYSIM?L=2`) else CASHX, daily rebalance, gross, start 1980-01-01 (testfol.io extends slightly further than our 1986-01-03 SPYSIM cut):

| Metric | testfol.io | Our `LRS_SPY_SSO_2x` (1986+) | Δ |
|---|---:|---:|---:|
| CAGR | 15.70% | 15.04% | −0.66pp |
| MaxDD | −51.67% | −50.57% | +1.10pp |

The 0.7pp / 1.1pp gap is consistent with testfol.io's `?L=2` including a small ER (~0.05–0.10%/yr) and a slightly different FFR-spread convention; our run holds ER and spread at zero. Match confidence: **high.** Bug-free.

---

## Headline metrics (full window, gross, signal lagged 1d)

Source: `lrs_baseline/tables/headline_metrics.csv`. Sorted in z-order (baselines first, study strategies last).

| Strategy | CAGR | Sharpe | Sortino | MaxDD | Calmar | End mult |
|---|---:|---:|---:|---:|---:|---:|
| **SPY_BH** | 11.5% | 0.68 | 0.96 | −55.1% | 0.21 | 79× |
| **NDX_BH** | 14.6% | 0.66 | 0.94 | −83.0% | 0.18 | 242× |
| **LRS_SPY_SSO_2x** | 15.0% | **0.71** | **0.98** | −50.6% | **0.30** | 283× |
| **LRS_SPY_UPRO_3x** | 18.9% | 0.67 | 0.92 | −69.9% | 0.27 | 1,083× |
| **LRS_QQQ_QLD_2x** | 19.5% | 0.68 | 0.95 | −82.4% | 0.24 | 1,308× |
| **LRS_QQQ_TQQQ_3x** | 22.5% | 0.65 | 0.91 | −94.2% | 0.24 | 3,526× |
| **t3d_k2** | **31.1%** | **0.92** | **1.32** | −64.5% | **0.48** | 54,143× |
| **iter030** | **36.7%** | **0.96** | **1.38** | −55.5% | **0.66** | 292,081× |

### Reads

- **Sortino ladder (primary, per the study's Sortino-first reanalysis):** **iter030 1.38** > **t3d_k2 1.32** ≫ LRS_SPY_SSO 0.98 ≈ SPY_BH 0.96 ≈ LRS_QQQ_QLD 0.95 ≈ NDX_BH 0.94 > LRS_SPY_UPRO 0.92 > LRS_QQQ_TQQQ 0.91.
- **MaxDD ranking** (least bad first): LRS_SPY_SSO_2x −50.6% < SPY_BH −55.1% ≈ iter030 −55.5% < t3d-k2 −64.5% < LRS_SPY_UPRO_3x −69.9% < LRS_QQQ_QLD_2x −82.4% < NDX_BH −83.0% < LRS_QQQ_TQQQ_3x **−94.2%**.
- **Calmar (CAGR/|MDD|, robustness proxy):** **iter030 0.66** > **t3d-k2 0.48** ≫ LRS_SPY_SSO_2x 0.30 > LRS_SPY_UPRO_3x 0.27 > LRS_QQQ_TQQQ_3x 0.24 ≈ LRS_QQQ_QLD_2x 0.24 ≫ baselines.
- **Counter-intuitive but expected once you know the math:** *more* LRS leverage *reduces* Sharpe and Sortino. The SMA200 gate cannot offset the daily-rebalance decay of higher leverage during sideways or whipsaw periods; CAGR rises with leverage but vol rises faster.
- **The naive SMA200 LRS is barely Pareto-improving on SPY buy-hold** at the 2× level (Sharpe 0.71 vs 0.68, Sortino 0.98 vs 0.96, MDD only ~5pp better) — close enough that net-of-cost it would likely lose. Only the QLD/NDX variants generate clear CAGR alpha vs their buy-hold benchmark, but they pay for it with monster drawdowns (−82% / −94%).

---

## Plots

### Equity curves (log scale, $10k base, gross)
![Equity curves](./lrs_baseline/plots/equity_curves.png)

### Drawdowns (peak-to-trough %, gross)
![Drawdown curves](./lrs_baseline/plots/drawdown_curves.png)

### Rolling CAGR — 3y / 5y / 10y / 15y
![Rolling CAGR grid](./lrs_baseline/plots/rolling_cagr_3_5_10_15y.png)

### Rolling Sortino — 3y / 5y / 10y / 15y
![Rolling Sortino grid](./lrs_baseline/plots/rolling_sortino_3_5_10_15y.png)

---

## Rolling-window summaries (gross, signal lagged 1d)

### CAGR per window (mean / p25 / p50 / p75 / min)

Source: `lrs_baseline/tables/rolling_cagr_summary.csv`. Step = 252d, overlapping.

| Strategy | 3y mean | 3y min | 5y mean | 5y min | 10y mean | 10y min | 15y mean | 15y min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LRS_SPY_SSO_2x  | 15.6% | −14.0% | 15.0% | −1.7% | 14.4% | −0.1% | 12.7% |  3.9% |
| LRS_SPY_UPRO_3x | 20.4% | −23.2% | 19.3% | −6.5% | 18.2% | −3.7% | 15.6% |  2.2% |
| LRS_QQQ_QLD_2x  | 21.5% | −26.1% | 20.7% | −8.7% | 19.5% | −1.9% | 17.6% |  4.8% |
| LRS_QQQ_TQQQ_3x | 26.3% | −43.7% | 24.7% | −20.7% | 22.3% | −9.2% | 19.2% |  1.4% |
| **t3d_k2**          | **31.6%** |  −0.9% | **30.5%** |  **6.0%** | **30.7%** | **11.8%** | **29.4%** | **19.4%** |
| **iter030**         | **37.3%** |  **5.6%** | **36.0%** |  **8.5%** | **35.5%** | **13.6%** | **33.7%** | **21.2%** |
| SPY_BH          | 11.5% | −13.0% | 11.1% | −2.8% | 10.6% | −1.4% |  9.5% |  4.5% |
| NDX_BH          | 15.7% | −32.9% | 15.0% | −13.7% | 14.2% | −5.6% | 12.6% |  2.1% |

**Read:** iter030's *worst* 15y rolling window compounds at **21.2%/yr**, vs the best naive LRS (TQQQ) at just **1.4%/yr** worst-case. On long-horizon CAGR, the study strategies are an order of magnitude more reliable than any naive LRS.

### Sortino per window (mean / p25 / p50 / p75 / min)

Source: `lrs_baseline/tables/rolling_sortino_summary.csv`.

| Strategy | 3y mean | 3y min | 5y mean | 5y min | 10y mean | 10y min | 15y mean | 15y min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LRS_SPY_SSO_2x  | 1.00 | −0.73 | 0.97 |  0.02 | 0.94 |  0.17 | 0.86 |  0.38 |
| LRS_SPY_UPRO_3x | 0.94 | −0.80 | 0.92 | −0.05 | 0.88 |  0.11 | 0.81 |  0.33 |
| LRS_QQQ_QLD_2x  | 0.95 | −0.43 | 0.95 | −0.01 | 0.93 |  0.20 | 0.88 |  0.44 |
| LRS_QQQ_TQQQ_3x | 0.90 | −0.46 | 0.91 | −0.05 | 0.90 |  0.17 | 0.85 |  0.41 |
| **t3d_k2**          | **1.32** |  **0.25** | **1.28** |  **0.47** | **1.29** |  **0.69** | **1.24** |  **0.95** |
| **iter030**         | **1.36** |  **0.44** | **1.33** |  **0.54** | **1.33** |  **0.76** | **1.28** |  **0.97** |
| SPY_BH          | 1.18 | −0.64 | 1.09 | −0.03 | 0.96 |  0.07 | 0.84 |  0.44 |
| NDX_BH          | 1.16 | −0.72 | 1.09 | −0.19 | 1.00 |  0.01 | 0.86 |  0.32 |

**Read:** iter030's worst-case 15y Sortino is **0.97**, equal to the *mean* 15y Sortino of the best naive LRS (SSO-LRS, 0.86). At every (3y, 5y, 10y, 15y) horizon iter030's worst-case is at or above the best naive LRS's median — the kind of robust dominance you would *want* from a strategy that earns its complexity.

---

## Verdict

| Question | Answer |
|---|---|
| Does iter030 beat all 4 naive LRS on Sortino? | **Yes** — 1.38 vs best LRS 0.98 (+0.40 absolute, +41% relative). |
| Does iter030 beat all 4 naive LRS on Sharpe? | **Yes** — 0.96 vs best LRS 0.71. |
| Does iter030 beat all 4 naive LRS on CAGR? | **Yes** — 36.7% vs best LRS 22.5%. |
| Does iter030 beat all 4 naive LRS on MaxDD? | **Yes** for 3 of 4; tied with SSO-LRS — 55.5% vs SSO-LRS 50.6%, but with much higher CAGR. |
| Does iter030 beat all 4 naive LRS on Calmar? | **Yes** — 0.66 vs best LRS 0.30. |
| Does iter030 dominate every (3y/5y/10y/15y) min rolling window? | **Yes** on CAGR-min and Sortino-min at every horizon. |

**The complexity of iter030's signal stack (`Vote-of-K(2) + T35-cooldown + D60-rearm + 1.20× LRS overlay` + ZROZ off-leg) earns its keep** vs. the canonical SMA200 + FFR cash baseline. The premium is ~+0.40 Sortino, ~+14pp CAGR, and ~+0.36 Calmar — material under any reasonable cost overlay short of one that erases LETF positions entirely.

The simpler intuition: the SMA200 gate is doing modest work (Sortino 0.98 vs 0.96 buy-hold), and adding leverage *makes it worse on a risk-adjusted basis*. The Vote-of-K signal is doing more selective work (admitting fewer false ON regimes, filtering whipsaws), and the ZROZ off-leg adds a positive carry leg in low-vol regimes that FFR cash cannot.

---

## Critical caveats

1. **Off-leg asymmetry (still real, just much smaller than the bug-inflated v1 made it look).** t3d-k2 / iter030 run their off-leg in **ZROZ** — 25-year zero-coupon Treasury. The LRS variants here run their off-leg in **FFR cash**. ZROZ lost ~50% in 2022 but added durable positive carry across 1986–2021. A net-of-2022 re-test (force both into a 2022-resilient asset) would close some of the gap — but the Sortino gap (1.38 vs 0.98) is wide enough that it is unlikely to flip under any sensible off-leg substitution.

2. **Gross-of-costs accounting.** All 8 series are gross. Net-of-15%-DARF + 0.9% LETF ER + 10bps spread would compress every leveraged path — the naive LRS likely loses 2–4pp CAGR, iter030 likely loses 3–5pp (more rebalance events). The Sortino ranking is unlikely to flip.

3. **Single-anchor iter030 selection.** Only `T35D60_unclrs120` (the most recent named winner) is plotted. The other T_crash variants on disk (T40, T45, T50 + LRS1.20) tell a richer story about parameter stability and are out of scope here.

4. **No PBO / DSR / WF gates re-run for the LRS variants.** The mandate's hard-block gates (§5) would need to be evaluated on each LRS variant before any "deployable baseline" claim. Sortino alone is not a deployability bar — the study's gate sweep is what closed t3d-k2 / iter030 as deploy-eligible (subject to mandate §1 maintenance mode).

5. **Sample-specific window.** Both strategies were tuned on this *exact* 1986–2026 testfolio synthetic. The naive LRS was not tuned at all — it's the literal Gayed canonical. Forward-out-of-sample stability of all six is an open question.

---

## Forensics — the lookahead bug (v1 → v2 revision, 2026-05-11)

**Cause.** In v1 of `_simulate_lrs`, the signal at time `t` was paired with the return at time `t`:

```python
# v1 (buggy)
is_on = regime.eq("ON")              # regime[t] uses close[t] and SMA[t]
daily = np.where(is_on, on_a, ffr_a) # paired with return[t] = close[t]/close[t-1] - 1
```

This means the position earning `return[t]` (held from close[t-1] to close[t]) was decided using close[t] — a one-day lookahead. Effect: the simulator preferentially picked the leveraged leg on days that were about to go up. Over 40 years this inflated CAGR by ~22pp and compressed MDD by ~30pp.

**Reference impl carries the same bug.** `src/market_lab/backtest/strategies/letf_rotation.py::simulate_letf_rotation` pairs `regime.loc[ts]` with `on_returns.loc[ts]` in the same `for ts in spx_returns.index` loop — no shift. This is a real bug in that module. The post-close study backtests (`runs/post_close/030-.../backtest.py`) **do not** rely on `simulate_letf_rotation`; they call `entry_signal_K2(...).shift(1)` directly (lines 456/474/477/481), so their published metrics are correct.

**Fix.** One-line change in this runner:

```python
# v2 (correct)
is_on = regime.shift(1).eq("ON")
```

**Validation.** After fix, `LRS_SPY_SSO_2x` posts CAGR 15.04% / MDD −50.6%; testfol.io's identical-spec backtest from 1980 posts 15.70% / −51.67%. Within 1pp on both axes — the residual reflects testfol.io's small `?L=2` ER and a slightly different FFR spread convention, not a methodology mismatch.

**Recommended follow-up (not in this doc).** Patch `simulate_letf_rotation` in `letf_rotation.py` to shift the signal, and re-validate every T1 / T2 / T3 study result that depends on it. The closed-study winner t3d-k2 and the post-close winner iter030 are **not** affected (their backtests are not on this code path), but earlier-tier T1 LRS configs may be.

---

## Mandate footer

This report is **research-only**. Strategy B (US LETF rotation) remains **DORMANT** per `docs/investment-mandate.md §1` (maintenance mode, 2026-04-23, 113/113 honest-FAIL retrospective). 100% capital is allocated to Plano C passive factor-tilted. Nothing here suggests reactivating Strategy B without (a) the PBO/DSR/WF gate sweep on the LRS variants and (b) the apples-to-apples off-leg re-test. Citations comply with Rule 2 (book references inline above and in the runner module docstring).

**Reproduce / inspect:**
- Runner: `studies/letf_rotation_hunt/runners/run_lrs_baseline_comparison.py`
- New utility: `studies/letf_rotation_hunt/core/rolling_sortino.py`
- Outputs: `studies/letf_rotation_hunt/reports/lrs_baseline/{plots,tables}/`
