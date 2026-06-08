# LRS Restart Memory

## 2026-06-07 - Study Opened

User approved restarting the LRS research line in this repository under root
folder `lrs/`.

Fixed decisions:

- Start from the original Gayed SMA200 LRS baseline
  `[leverage_for_the_long_run, p.13]`.
- Focus on weekly execution, not daily execution.
- Evaluate settlement/operational lag `n = 0..5` daily bars.
- Use annual Brazilian DARF model: 15% on realized net gains, loss netting and
  carry-forward under Lei 14.754/2023.
- Keep overfit diagnostics as recorded evidence during evolution; do not use them
  to stop the study iteration process.
- Allow bear-market inverse ETF sleeves in later phases.

Phase plan:

1. Phase 0: original Gayed SMA200 baseline, `risk-off=CASHX`.
2. Phase 1: risk-off alternatives.
3. Phase 2: target leverage and realized-volatility throttle.
4. Phase 3: sparse risk-on filters using the Phase 2 exposure geometry.
5. Phase 4: bear-market inverse sleeve.

## 2026-06-07 - Phase 0 Baseline Executed

Runner: `uv run python -m lrs.phases.phase00_gayed_baseline.run`.

Outputs:

- `phases/phase00_gayed_baseline/REPORT.md`.
- `results/phase00_gayed_baseline.csv`.

Result summary:

- Evaluated 24 rows: SPY 2x/3x and QQQ 2x/3x, each with lag `n=0..5`.
- Top score row: `SPY_3x`, lag `2`, after-tax CAGR `16.91%`, MDD `-88.33%`,
  Calmar `0.191`, terminal `8798.16x` vs after-tax SPY and `9800.65x` vs
  after-tax UPRO buy-and-hold over the long SPY synthetic window.
- Best QQQ row: `QQQ_3x`, lag `0`, after-tax CAGR `21.34%`, MDD `-91.97%`,
  terminal `10.95x` vs after-tax QQQ and `21.70x` vs after-tax TQQQ buy-and-hold.
- All rows beat underlying terminal wealth after tax, but drawdowns remain in
  risk-of-ruin territory. Phase 1 should prioritize risk-off alternatives before
  adding risk-on indicators `[leverage_for_the_long_run, p.4-7]`,
  `[leverage_for_the_long_run, p.13]`.
- Report now includes `Test Windows` and generated plots under
  `phases/phase00_gayed_baseline/plots/`.
- Drawdown objective documented in `SPEC.md`: preferred `<=40%`, tolerable
  research target `40%..50%`, warning `50%..65%`, ruin territory `>65%`.

Validation status: not validated; overfit gates intentionally not run in this
kick-start phase.

## 2026-06-07 - Phase 1 Risk-Off Alternatives Executed

Runner: `uv run python -m lrs.phases.phase01_risk_off.run`.

Outputs:

- `phases/phase01_risk_off/REPORT.md`.
- `results/phase01_risk_off.csv`.
- `phases/phase01_risk_off/plots/`.

Result summary:

- Evaluated 264 rows: 4 branches x 11 risk-off sleeves x lag `n=0..5`.
- Phase 1 uses common branch windows including `GLDSIM`/`IEFSIM`/`ZROZSIM`, so
  SPY rows start `1968-04-02` instead of Phase 0's cash-only 1885 window.
- Top score row: `SPY_2x`, risk-off `40 ZROZ / 40 GLD / 20 IEF`, lag `5`,
  after-tax CAGR `15.23%`, MDD `-41.34%`, Calmar `0.368`, terminal `11.03x`
  vs after-tax SPY. This meets the restart's tolerable drawdown target.
- `34` rows met the `<=50%` MDD practical target while beating underlying after
  tax; all are SPY 2x rows in the current ranking surface.
- Best SPY 3x row: `50 ZROZ / 50 GLD`, lag `5`, after-tax CAGR `17.90%`, MDD
  `-61.04%`, warning tier.
- Best QQQ rows still remain in ruin territory: `QQQ_2x` + `ZROZ` lag `0`, MDD
  `-71.32%`; `QQQ_3x` + `ZROZ` lag `0`, MDD `-88.31%`.

Interpretation: risk-off matters enormously and can make SPY 2x psychologically
closer to usable. QQQ and 3x still require lower target leverage, volatility
throttle or a bear-market sleeve before broad indicator votes
`[leverage_for_the_long_run, p.4-7]`, `[systematic_trading, p.137-148]`.

Validation status: not validated; overfit gates intentionally recorded later as
diagnostics, not as an evolution stop-rule.

## 2026-06-07 - Phase 2 Target Leverage And Volatility Throttle Executed

Runner: `uv run python -m lrs.phases.phase02_target_leverage_vol.run`.

Outputs:

- `phases/phase02_target_leverage_vol/REPORT.md`.
- `results/phase02_target_leverage_vol.csv`.
- `phases/phase02_target_leverage_vol/plots/`.

Result summary:

- Evaluated 2,400 rows: SPY/QQQ x 8 target leverages x 5 risk-off sleeves x
  5 realized-volatility filters x lag `n=0..5`.
- Top score row: `SPY` target leverage `2.00`, risk-off
  `50 ZROZ / 25 GLD / 25 CASH`, vol filter `RV21 <= 30%`, lag `3`, after-tax
  CAGR `15.44%`, MDD `-39.28%`, Calmar `0.393`, terminal `12.28x` vs
  after-tax SPY. This is the first Phase 2 top-score row in the preferred
  `<=40%` drawdown tier.
- Practical-pass rows (`MDD >= -50%` and after-tax underlying outperformance):
  `875`.
- Preferred drawdown rows (`MDD >= -40%`): `394`.
- QQQ practical-pass rows: `303`.
- Best QQQ row: `QQQ` target leverage `1.75`, risk-off
  `40 ZROZ / 40 GLD / 20 IEF`, vol filter `RV63 <= 40%`, lag `0`, after-tax
  CAGR `19.46%`, MDD `-42.58%`, Calmar `0.457`, terminal `5.82x` vs
  after-tax QQQ.
- Best-by-leverage QQQ rows now leave ruin territory across the tested leverage
  ladder, but QQQ above `2.00x` remains warning-tier rather than practical.

Interpretation: target leverage and volatility throttling materially improve the
frontier before adding indicator complexity. The next phase should use the Phase
2 exposure geometry as the base for a small pre-registered risk-on filter vote,
or a separate bear-market sleeve if the priority becomes further drawdown
compression `[leverage_for_the_long_run, p.4-7]`, `[systematic_trading,
p.137-148]`, `[advances_fin_ml, p.208-211]`.

Validation status: not validated; this is exposure-geometry discovery only, with
no deployment, paper-trading label or mandate allocation change.

## 2026-06-07 - Phase 3A Sparse Risk-On Confirmation Vote Executed

Runner: `uv run python -m lrs.phases.phase03_sparse_risk_on_vote.run`.

Outputs:

- `phases/phase03_sparse_risk_on_vote/REPORT.md`.
- `results/phase03_sparse_risk_on_vote.csv`.
- `phases/phase03_sparse_risk_on_vote/plots/`.
- New helpers: `lrs/lib/indicators.py`; new tests: `tests/test_lrs_phase03.py`.

Pre-registered grid (324 rows): SPY/QQQ x 3 branch-specific bases (Phase 2 top +
2 one-lever neighbours) x 9 filters (`none` control + 4 families x 2 variants) x
lag `n=0..5`. Each row ANDs at most ONE confirmation filter onto the Phase 2 base
`signal = sma & vol_gate & confirm_gate`; filters tested independently, no
vote-of-K. Phase 2 scoring + `practical_pass` kept verbatim (cross-phase
comparability). Filter families and cites: Clenow slope x R^2
`[stocks_on_the_move, p.70-77, p.98]`; ROC momentum `[stocks_on_the_move, p.58,
p.60]`; SMA hysteresis band `[trading_systems_methods, p.383]`; close-only ADX
proxy `[trading_systems_methods, p.387]`.

Result summary (NEGATIVE / no-improvement finding):

- Top score row is the `none` control: `SPY` base `spy_top` L`2.00` lag `3`,
  after-tax CAGR `15.44%`, MDD `-39.28%`, Calmar `0.393`, terminal `12.28x` vs
  underlying - identical to the Phase 2 top (built-in sanity check passed:
  `none` rows reproduce Phase 2 byte-for-byte, max abs diff `0`).
- No non-`none` filter beats the control on either branch (SPY: no, QQQ: no).
- Clenow / ROC / ADX all diverge from `none` but REDUCE CAGR (they reject good
  risk-on days); ADX (degraded close-only proxy) is worst and not over-read.
- Structural insight: the SMA hysteresis band is IDENTICAL to `none` in all
  36/36 configs. As an AND-gate onto `price > SMA200` it can only further
  restrict risk-on; its one distinct behaviour (holding through a dip below the
  SMA) lives exactly on days the SMA gate already blocks, so the AND erases it.
  Testing hysteresis properly requires REPLACING the SMA gate, not ANDing onto
  it - deferred.
- Practical-pass rows: `242`; preferred `<=40%` MDD rows: `55`; QQQ
  practical-pass: `120`.

Interpretation: added risk-on filter complexity is not justified - the Phase 2
exposure geometry (leverage + risk-off + vol throttle) is the real driver, and a
plain SMA200 entry is as good as the tested confirmations
`[trading_systems_methods, p.939]`, `[advances_fin_ml, p.208-211]`. If a
trend-hold mechanism is still wanted, test hysteresis as a replacement signal;
otherwise revisit risk-off / bear-sleeve mechanisms (bear sleeve currently
BLOCKED - no inverse tickers in the cache) or close the family pending the
mandate validation gates.

Validation status: not validated; diagnostic confirmation-vote phase only. No
deployment, no paper-trade label, no mandate allocation change.

## 2026-06-07 - Phase 3A-2 Alternative Regime Signals (Replacement) Executed

Runner: `uv run python -m lrs.phases.phase03b_regime_signals.run`.

Outputs:

- `phases/phase03b_regime_signals/REPORT.md`, `README.md`.
- `results/phase03b_regime_signals.csv`.
- `phases/phase03b_regime_signals/plots/`.
- New helper: `lrs/lib/indicators.ema_gate`. New tests:
  `tests/test_lrs_phase03b.py`.

Pre-registered grid (216 rows): SPY/QQQ x 3 branch-specific bases (identical to
Phase 3A) x 6 regime forms x lag `0..5`. Each form REPLACES the SMA200 trend gate
(`signal = G & vol_gate`), not ANDed onto it - the direct follow-up to the Phase
3A insight that an AND-gate can only further restrict risk-on. Lookback held
FIXED at 200 across all forms to isolate signal *form* from *window* (the window
question is Phase 3C's). Forms: SMA200 control `[leverage_for_the_long_run,
p.13]`, EMA200 `[systematic_trading, p.283]`, hyst200 band5%/8%
`[trading_systems_methods, p.383]`, ROC200>0 `[stocks_on_the_move, p.58, p.60]`,
Clenow200>0 `[stocks_on_the_move, p.70-77, p.98]`. Phase 2 scoring +
`practical_pass` kept verbatim.

Result summary (NEGATIVE for beats-both; EMA200 a QQQ-only near-tie):

- Built-in sanity PASSED: SMA200 control reproduces Phase 2 across `36` matched
  base+lag rows, max abs diff in after-tax CAGR/MDD `8.33e-17` (~0) vs
  `lrs/results/phase02_target_leverage_vol.csv`.
- Top score row is the SMA200 control: `SPY spy_top` L`2.00` lag `3`, after-tax
  CAGR `15.44%`, MDD `-39.28%`, Calmar `0.393`, terminal `12.28x` - identical to
  the Phase 2 / Phase 3A top.
- Does any non-control form beat SMA200 on BOTH branches (by score)? NO
  (QQQ: no, SPY: no).
- EMA200 is the only competitive alternative, and only on QQQ: best-by-form score
  `3.828` vs SMA200 `3.830` (near-tie). On `qqq_top` lag `0` EMA200 lifts CAGR
  `+1.36pp` (20.82%) but worsens MDD `-3.57pp` (-46.15%), so score nets slightly
  below the control. On SPY, EMA200 is clearly worse (`-1.59pp` CAGR AND
  `-8.86pp` MDD on `spy_top`).
- Hysteresis / ROC / Clenow as REPLACEMENT gates badly worsen drawdown on both
  branches (best-by-form MDD `-50%` to `-74%`, warning/ruin tiers) while not
  lifting CAGR - the leveraged-whipsaw cost: a noisier/stickier trend gate holds
  levered exposure into drawdowns that the clean SMA200 level exits. This matches
  the spin-off caution that leverage amplifies lookback/trend-switch cost
  `[leverage_for_the_long_run, p.4-7]`.
- Practical-pass rows: `64`; preferred `<=40%` MDD rows: `7`; QQQ practical-pass:
  `36`.

Interpretation: the SMA200 *level* is a robust regime gate for this leveraged
geometry; no alternative *form* (at fixed window 200) beats it on both branches.
Hysteresis is NOT promoted (it worsened MDD, not held risk-on usefully). Per the
approved design, Phase 3C studies SMA + EMA only (hysteresis excluded), with the
SMA200 level as control - answering "why 200?" via robustness map + theory anchor
+ gated adaptive `[trading_systems_methods, p.939]`, `[advances_fin_ml,
p.208-211]`.

Validation status: not validated; diagnostic regime-form phase only. No
deployment, no paper-trade label, no mandate allocation change.

## 2026-06-07 - Phase 3C Lookback Study Executed

Runner: `uv run python -m lrs.phases.phase03c_lookback_study.run`.

Outputs:

- `phases/phase03c_lookback_study/REPORT.md`, `README.md`.
- `results/phase03c_lookback_study.csv` (936 rows),
  `results/phase03c_theory_anchor.csv`.
- `phases/phase03c_lookback_study/plots/` (SPY/QQQ surfaces, score surface,
  adaptive comparison).
- New helpers: `lrs/lib/indicators.{autocorr,acf_decay_half_life,
  ewma_span_from_half_life,adaptive_vol_window}`. New tests:
  `tests/test_lrs_phase03c.py`.

Question: *why SMA 200?* Pre-registered to avoid both overfit traps (blind trust
vs sweep-and-pick-argmax). Studies SMA + EMA only (hysteresis not promoted in
3A-2). Grid (936 rows): 13 windows `50..400` x {SMA, EMA} x 6 bases x lag `0..5`.
Mechanism unchanged from 3A-2 (gate replaces SMA, `signal = G & vol_gate`, Phase 2
scoring verbatim). Pre-registered plateau rule: contiguous Calmar band within 10%
of band-best, width `>= 150` days, read at best-score lag per window. We did NOT
promote the argmax `[trading_systems_methods, p.939]`, `[advances_fin_ml,
p.208-211]`.

Result summary (nuanced - fragile by strict rule, but adaptivity does NOT help):

- **Part 1 robustness:** by the strict rule, BOTH primary SMA curves are narrow
  peaks (fragile): SPY band `200-225` (width 25), QQQ band `175-225` (width 50);
  both below the 150-day plateau threshold. EMA is even peakier (argmax 100).
  Driver of the fragility is MDD/Calmar sensitivity on the leveraged sleeve: long
  windows collapse to ~`-59%` MDD (SPY `>=275`, QQQ `>=250`) because a too-long
  window exits the regime late into crashes. There IS a broad *adequate* region
  (~`150-250`, tolerable/preferred MDD); within it, 200 is at/near the Calmar-best
  (SPY argmax `200`; QQQ argmax `175`, with `225` ~tied) - but it is not a wide
  flat plateau.
- **Part 2 theory anchor (ex-ante):** vol-persistence half-life (squared-return
  ACF decay ~ GARCH `alpha+beta`) is SHORT: SPY `10.9d`, QQQ `14.3d` -> EWMA span
  ~`32/41`, `2xHL` ~`22/29` - far below the empirical adequate region. Signed-
  return autocorrelation half-life is `n/a` (near-white): no daily momentum
  horizon. So 200 is NOT a persistence-matched horizon; it is a slow regime/level
  filter much longer than any autocorrelation timescale `[volatility_trading,
  p.39, p.53-54]`, `[systematic_trading, p.283]`, `[stocks_on_the_move, p.58,
  p.60]`.
- **Part 3 adaptive (gated ON by fragility):** vol-scaled window
  `w_t = clip(round(200 * 0.15 / RV63), 50, 400)`, `.shift(1)`-lagged. It does NOT
  beat the fixed window net of turnover on either branch: SPY adaptive (mean W
  234.5) CAGR `15.01%` / MDD `-52.84%` / Calmar `0.284` vs fixed-200
  `15.44%`/`-39.28%`/`0.393`; QQQ adaptive (mean W 162.2) `20.13%`/`-46.18%`/
  `0.436` vs fixed-200 `19.46%`/`-42.58%`/`0.457` and best-fixed-175
  `20.92%`/`-43.32%`/`0.483`. This directly confirms the spin-off caution that
  leverage amplifies lookback-switch cost `[leverage_for_the_long_run, p.4-7]`.
- **Spin-off cross-check** (markers only, not inherited): single-asset optima SPY
  ~`250-295`, QQQ ~`245`; 200 is the round popular number, not the empirical best
  `[trading_systems_methods, p.27, p.917-919]`.

Interpretation / "why 200?": 200 is a sound FIXED default sitting at/near the
Calmar-best inside a broad adequate region `~175-225`; it is empirically adequate
but neither a wide flat plateau nor theoretically anchored by persistence (those
suggest ~3-6 weeks). Keep a fixed window in `~175-225`, AVOID windows `>=250`
(late-exit MDD blowups under leverage), treat the Phase 2 exposure geometry as the
real driver, and do NOT adopt adaptive windowing despite the fragility flag (it
loses net of turnover). The pre-registered argmax was NOT promoted.

Validation status: not validated; diagnostic lookback study only. No deployment,
no paper-trade label, no mandate allocation change.

## 2026-06-07 - Phase 4 Mandate Validation Gates Executed (DIAGNOSTIC; family closed)

Runner: `uv run python -m lrs.phases.phase04_validation_gates.run`.

Outputs:

- `phases/phase04_validation_gates/REPORT.md`, `README.md`.
- `results/phase04_validation_gates.csv`.
- `phases/phase04_validation_gates/plots/` (gate heatmap, WF OOS spread).
- New module `lrs/lib/validation.py` (thin wrappers over canonical
  `market_lab.backtest.validation`; no `studies/` import). New tests:
  `tests/test_lrs_phase04.py`.

Diagnostic, not a promotion (per NEXT_STEPS). Ran the canonical mandate §5 gate
suite on the 6 SMA200 bases (3 SPY + 3 QQQ, each at its best-score lag). DSR
`n_trials = 3876` (direct lineage Phase 2 2400 + 3A 324 + 3A-2 216 + 3C 936; the
spin-off `letf-lab` sweeps excluded, so the true count is higher). PBO trial
matrix = the Phase 2 geometry grid at SMA200 (8 lev x 5 risk-off x 5 vol = 200
configs/branch, fixed lag). WF: is 1764d / oos 756d / step 756d, >=8 windows,
>=6/8 OOS windows must beat the underlying after-tax (per-window MDD diagnostic,
no cap, per user decision).

Result (NEGATIVE - family does NOT clear the gates):

- **0/6 bases pass all seven gates.** Verdict: the LRS family does not clear the
  mandate validation gates; recorded as research-only, negative-leaning, and
  closed/shelved pending new literature or regime. No mandate change.
- **G3 walk-forward is the universal binding gate (fails 6/6):** >=6/8 = >=75% of
  rolling ~3y OOS windows must beat the underlying after-tax. Best is SPY
  `spy_top`/`spy_alt_off` at `12/17` (70.6%), just below 75%; `spy_lower_lev`
  `10/17`; QQQ `6-7/11`. The strategy beats the underlying most of the time, but
  not in >=75% of long-horizon OOS windows.
- **SPY is the least-rejected:** all 3 SPY bases PASS G1 PBO (`0.016`, very low)
  AND G2 DSR (p `0.024-0.034 < 0.05`) even at n_trials=3876 - the 58y track
  record is long enough that the Sharpe survives deflation. SPY's only failures
  are G3 (WF, narrow) and `spy_lower_lev` also G4 (OOS).
- **QQQ is clearly rejected:** fails G1 PBO (`0.643 > 0.5`), G2 DSR
  (p `0.145-0.164`) AND G3 WF. Shorter (40y) history, higher overfit
  susceptibility - consistent with QQQ's ruin-tier history and 3C fragility.
- **G4-G7 broadly pass:** G5 FWD (post-2020) Sharpe>0 pass; G6 bootstrap 99.9% CI
  low of annualized Sharpe `0.28-0.34 > 0` pass; G7 cross-lib CAGR delta ~`0` pass;
  G4 OOS passes except `spy_lower_lev`.
- Metrics (warning-only tiers, NOT gates): SPY `spy_top` CAGR `15.44%`, MDD
  `-39.28%`, Sharpe `0.718`, Calmar `0.393`; QQQ `qqq_top` CAGR `19.46%`, MDD
  `-42.58%`, Sharpe `0.725`.

Interpretation: across the whole restart, exposure geometry (Phase 2) is the
driver; no filter (3A), form (3A-2) or window/adaptive (3C) beats the SMA200-level
base, and the base itself does not clear the mandate gates (binding: walk-forward
robustness; QQQ also PBO/DSR). The LRS restart joins the repo's honest-FAIL ledger
as a research-only line. SPY is the closest to validation (6/7 gates) but the
walk-forward robustness gate is not met `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`, `[testing_tuning, p.318-320]`,
`[leverage_for_the_long_run, p.4-7]`.

Validation status: gates RUN; family does not pass; closed/shelved. No deployment,
no paper-trade label, no mandate allocation change.
