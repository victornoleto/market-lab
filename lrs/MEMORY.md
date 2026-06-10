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

## 2026-06-08/09 - Phase 5 RSC Overlay Rebuilt-Sleeve Diagnostic Executed

Runner: `uv run python -m lrs.phases.phase05_rsc_overlay_proxy.run`.

Outputs:

- `phases/phase05_rsc_overlay_proxy/REPORT.md`, `README.md`.
- `results/phase05_rsc_overlay_proxy.csv`.
- `phases/phase05_rsc_overlay_proxy/plots/`.
- New RSC sleeve artifact:
  `studies/return_stacked_core/us_core/series/return_stacked_core_sleeve_returns.parquet`
  plus `.meta.json`.
- New exporter: `studies/return_stacked_core/export_sleeve_returns.py`.
- New tests: `tests/test_lrs_phase05.py`,
  `tests/test_return_stacked_core_sleeve_returns.py`.
- Top-20 return-first ranking: `TOP20_BY_CAGR.md`,
  `results/top20_by_cagr.csv`; generator `lrs/top20_by_cagr.py`.

Purpose: answer whether the failed standalone LRS line has value as a small
satellite around RSC-US `35/40/25`, after the Reddit feedback emphasized
benchmarks, underwater/recovery and sizing. The first proxy pass used the saved
RSC curve; the follow-up found local `GDESIM`, `KMLMSIM`, `DBMFSIM` and related
remote prices in `studies/return_stacked_core/us_core/series/remote_prices.parquet`
and exported a RSC-US sleeve-return matrix. The first local formula matched the
saved RSC curve; the user then requested the Testfol.io tracking payload formula:
`RSSTSIM = SPYSIM + 0.70*DBMFSIM + 0.30*KMLMSIM - (CASHX + 0.0200/252)`, equivalent
to `100% SPY + 70% DBMF + 30% KMLM - 100% CASHX?E=-2`. A no-auth endpoint audit
over 2023-09-06..2026-06-08 showed terminal ratio `1.002547` and daily return
correlation `0.927530` versus live RSST. Because `DBMFSIM` starts in 2000, the
RSC diagnostic window is now 2000+ `[testing_tuning, p.327-335]`, `[risk_parity,
p.80-81]`, `[systematic_trading, p.185-188]`.

Candidate set: rebuilt `100% RSC` baseline plus `90/10`, `80/20`, `70/30` monthly
rebalanced overlays for three satellites: local `lrs_spy_headline`, local
`lrs_qqq_headline`, and saved `t3d_k2_saved`. Strict screen requires higher CAGR
than same-window RSC, no worse MDD, no worse Calmar, no worse time underwater and
no worse max recovery time. It is not a mandate gate.

Result summary:

- With the revised RSST proxy, `0/9` overlays pass the strict rebuilt-sleeve
  screen.
- Highest-CAGR overlay overall: `70% RSC / 30% T3d-K2`, CAGR `14.24%`, MDD
  `-48.65%`, Calmar `0.293`, vs rebuilt RSC CAGR `12.40%`, MDD `-30.76%`, Calmar
  `0.403`; this is a growth-for-drawdown trade-off, not strict improvement.
- Standalone references on the 2000+ common window: T3d-K2 CAGR `14.65%`, MDD
  `-84.04%`; local QQQ LRS CAGR `13.64%`, MDD `-42.56%`; local SPY LRS CAGR
  `12.09%`, MDD `-39.28%`.
- Top-20 CAGR-independent ranking scanned `4183` rows. Top row: `QQQ L3.00 / ZROZ /
  RV63<=40% / lag5`, after-tax CAGR `25.84%`, MDD `-71.05%`, Calmar `0.364`.

Interpretation: Phase 5 no longer supplies a strict overlay pass under the revised
RSST tracking proxy. The useful output is now diagnostic: an explicit RSST proxy,
the overlay table, and a return-first Top-20 for user selection. It does **not**
reverse Phase 4's standalone gate failure, and it does not promote anything. Any
future claim needs user-chosen pre-registration, account-level tax/friction plus
mandate gates with honest trial accounting that includes the prior LRS lineage
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

Validation status: rebuilt-sleeve diagnostic only; no PBO/DSR/WF/OOS/FWD/bootstrap/xlib
run for overlays; no deployment, no paper-trade label, no mandate allocation
change.

## 2026-06-09 - Phase 6 Round Executed (6C forensics, 6B vol-target, 6D inverse, 6A after-tax frontier)

User question driving the round: "is any LRS strategy interesting enough to be
worth giving up part of a 100%-static position?" User decisions: benchmarks =
RSC-US 35/40/25 + SSO B&H + SPY B&H; portfolio MDD floor `-50%`; all four
fronts approved. Run order 6C -> 6B -> 6D -> 6A (directory names sort
differently; READMEs are the authority).

Runners:

- `uv run python -m lrs.phases.phase06c_wf_forensics.run`
- `uv run python -m lrs.phases.phase06b_vol_target_continuous.run`
- `uv run python -m lrs.phases.phase06d_inverse_sleeve.run`
- `uv run python -m lrs.phases.phase06a_aftertax_frontier.run`

Outputs: per-phase `README.md` (pre-registration), `REPORT.md`, `plots/`, CSVs
in `lrs/results/phase06{a,b,c,d}_*.csv`, tests `tests/test_lrs_phase06{a,b,c,d}.py`.
Lib change (additive, regression-guarded): `force_rebalance_mask` parameter in
`lrs/lib/backtest.simulate_weight_frame` so a static core can be
monthly-rebalanced with its turnover taxed by `AnnualDarfEngine`.

### Phase 6C - WF forensics (+0 trials)

84 base-windows persisted (3x17 SPY + 3x11 QQQ; beat counts reproduce Phase 4
exactly). Pre-registered headline question (>=2/3 of failing windows in
`bull_low`): **NO** (48.5%). But 90.9% of failures are in `bull` cells, and the
regime table is sharply structured: `bear_high` beat rate 100% (mean rel ret
+154pp), `bear_mid` 0% (-18.8pp, leveraged whipsaw without a deep crash),
`bull` cells 59-75%. Reading: the edge is concentrated in deep-crisis regimes;
the WF miss is mostly the structural cost of timing in bull windows plus
mid-vol bear whipsaw `[leverage_for_the_long_run, p.7-8]`, `[testing_tuning,
p.318-320]`.

### Phase 6B - continuous vol-targeting (+72 trials -> 3948)

`L_t = clip(sigma_target / RV_t, 0, L_max)` quantized to the 0.25 ladder with
inertia, replacing the binary vol gate `[systematic_trading, p.137-148, p.159,
p.174]`. Screen (best row per branch by WF beats, tie Calmar): **SPY FAIL**
(WF 12/17 = baseline, not strictly greater; CAGR 14.55%, MDD -37.17%); **QQQ
SUCCESS** (sigma 40% / RV21 / lag 1: WF 7/11 vs baseline 6/11, CAGR 19.14%,
MDD -42.18%). Honest note: 7/11 equals what `qqq_alt_vol` already reached in
Phase 4 with a binary RV21<=30% gate, and is still far from the 9/11 gate
level. SUCCESS = diagnostic lead for 6A's satellite set only.

### Phase 6D - capped inverse sleeve (+36 trials -> 3984)

Inverse synthesized in memory (`r_inv = -r_u - 0.0095/252`, cache untouched)
`[leverage_for_the_long_run, p.16, fn.22-23]`; `risk_off' = (1-f)*risk_off +
f*{INV}`, f in {10%, 15%, 25%} `[trading_systems_methods, p.354]`. Sanity f=0
reproduces Phase 4 metrics (max abs dev ~5.6e-17). Screen at the committed
headline lag: **FAIL on both branches** - every f worsens CAGR AND MDD (SPY
best-f 10%: 14.85% / -40.26% vs headline 15.44% / -39.28%; QQQ best-f 10%:
18.59% / -43.19% vs 19.46% / -42.58%). Consistent with the low prior from
3A/3A-2: added mechanisms keep losing to the clean geometry.

### Phase 6A - after-tax frontier vs 3 benchmarks (+21 trials -> 4005)

Window 2000-01-04..2026-05-21. BOTH legs after-tax for unified-engine rows
(core monthly rebalance turnover taxed via `force_rebalance_mask`); T3d rows
are `two_account_approx` (legs already after-tax, inter-leg rebalance tax not
modeled). Satellites: `lrs_spy_headline` (binary, lag 3), `lrs_qqq_voltarget`
(6B winner), `t3d_k2_saved`. Benchmarks after-tax: RSC `11.25% / -30.76% /
Calmar 0.366`; SSO B&H `9.01% / -88.27% / 0.102`; SPY B&H `7.81% / -55.14% /
0.142`.

Key result: **18/18 mixes pass the MDD>=-50% constraint; 13 beat after-tax RSC
on BOTH CAGR and Calmar.** Top by Calmar: `mix_lrs_spy_headline_25` CAGR
`11.65%` (+0.40pp vs RSC), MDD `-26.32%` (+4.44pp better), Calmar `0.442`.
Best CAGR among unified-engine mixes: `mix_lrs_qqq_voltarget_30` `12.19%`
(+0.94pp), MDD `-28.31%` (still better than RSC). T3d mixes give the highest
CAGR (up to `13.43%` at 30%) but trade MDD down to `-48.66%` fast. The
once-gross RSC advantage shrinks after tax (12.40% gross -> 11.25% after-tax),
and small satellites add CAGR while REDUCING portfolio MDD via diversification
`[systematic_trading, p.185-188]`.

Caveats (explicit): satellites individually failed (or never ran) the mandate
gates; mix-level improvements are in-sample diagnostics built from configs
selected by the prior lineage; T3d rows carry the two-account approximation;
none of this is promotion. Any promotion claim requires the full mandate SS5
suite on the chosen mix with `n_trials >= 4005` `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.273-275]`.

Validation status: diagnostic round only; no PBO/DSR/WF/OOS/FWD/bootstrap/xlib
on mixes; no deployment, no paper-trade label, no mandate allocation change.

## 2026-06-09 - Phase 6A REVISED (user tax-model correction; supersedes the 6A numbers above)

User correction: static portfolios are rebalanced with **new contributions
(aportes), not sells** - the core realizes no gains along the way and pays no
intermediate DARF. The first 6A run (unified engine taxing the core's monthly
rebalance turnover) overstated the core's tax drag. Revised per-leg model:
core = gross monthly rebalance + 15% DARF at final liquidation only; LRS
satellites = full `AnnualDarfEngine` (weekly rotation genuinely sells); B&H
benchmarks = final DARF only; mixes = two-account convention with
contribution-funded (tax-free) re-truing, disclosed in `tax_method`
`[testing_tuning, p.327-335]`. The `force_rebalance_mask` lib extension stays
(generic, regression-guarded) but is no longer used by 6A.

Also added Part 2 per the user's request: contribution simulation - start
USD 10k, +USD 1k on the first trading day of each month, each month buying
ONLY the single most-underweight component (minimal-trades policy for
broker-cost/tax optimization), no sells, final DARF on gross components with
cost-basis tracking; satellite component exempt (its series is already
after-tax) `[systematic_trading, p.185-188]`. +0 trials (same mixes, different
accounting lens); ledger stays 4005.

Revised Part 1 (time-weighted, 2000-01-04..2026-05-21): RSC after-tax
`11.74% / -30.76% / Calmar 0.382` (vs 12.40% gross; the wrong v1 model said
11.25%); SSO B&H `9.01% / -88.27%`; SPY B&H `7.81% / -55.14%`. **18/18 mixes
pass MDD>=-50%; 13 beat RSC on BOTH CAGR and Calmar.** Top Calmar:
`mix_lrs_spy_headline_20` `12.12% / -25.18% / 0.481`. Best CAGR unified:
`mix_lrs_qqq_voltarget_30` `12.83% / -27.67% / 0.464`.

Part 2 (money-weighted, $326k contributed over 26.4y): **all 18 mixes beat
100% RSC on IRR** (RSC `13.72%`, terminal $2.96M). `mix_lrs_qqq_voltarget_30`
IRR `15.21%` ($3.87M) with path MDD `-28.4%` ~= RSC's `-27.6%`.
`mix_t3d_k2_saved_30` tops IRR `17.66%` ($6.00M) but path MDD `-50.3%`
(breaches the floor even with inflow softening). SSO B&H IRR `15.81%` ($4.31M)
- DCA flatters volatile B&H on IRR - but path MDD `-80.8%` is ruin-tier. SPY
B&H `10.72%` ($1.75M). Caveats: path MDD is mechanically softened by inflows;
the `final_tax` column excludes satellite-internal DARF (already in its
series); T3d remains a saved external curve.

Validation status unchanged: diagnostic decision-table only; no gates run on
mixes; no deployment, no paper-trade label, no mandate change. Any promotion
claim needs the full SS5 suite on the chosen mix with `n_trials >= 4005`
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.

## 2026-06-09 - Phase 7A Ensemble Multi-Lookback Fractional Position Executed

Phase 7 round opened (user approved all fronts + the GTT/UNRATE citation
exception): 7A ensemble -> 7B multi-asset portfolio -> 7C macro gate ->
7D vol^2 targeting -> 7E managed-futures risk-off -> 7F conditional
composition -> Phase 8 final gates on user-chosen configs. Round criterion is
WF beats vs paired control, not CAGR.

Runner: `uv run python -m lrs.phases.phase07a_ensemble_lookback.run`.

Outputs:

- `phases/phase07a_ensemble_lookback/README.md` (pre-registration), `REPORT.md`.
- `results/phase07a_ensemble_lookback.csv`.
- `phases/phase07a_ensemble_lookback/plots/`.
- New helper: `lrs/lib/indicators.sma_ensemble_fraction`. New tests:
  `tests/test_lrs_phase07a.py`.

Pre-registered grid (72 rows, ledger 4005 + 72 = 4077): 6 Phase 4 bases x 2
window sets (`narrow {150,175,200,225}`, `wide {100,150,200,250,300}`) x lag
0..5. Mechanism: fractional position `f_t = (1/N) sum_w 1[P>SMA_w]` (combined
forecast over rule speeds `[systematic_trading, p.118-119, p.129-133]`; equal
weights justified by the paper's own window-robustness table
`[leverage_for_the_long_run, p.14, Table 6]`), scaled by the base's binary vol
gate; geometry/cadence/tax verbatim. Built-in sanity PASSED: degenerate `{200}`
reproduces the binary base with max abs diff `0` on both branches.

Result summary (SPY SUCCESS - first WF lift of the restart; QQQ FAIL):

- **SPY SUCCESS:** best row `spy_alt_off / narrow / lag 2` WF **13/17 (76.5%)**
  vs best binary baseline 12/17 - the first mechanism in the whole restart to
  reach the G3 walk-forward gate level (>=75%) on SPY. CAGR 14.49% (within the
  pre-registered 1pp tolerance of the 15.44% headline), MDD -43.16% (tolerable
  tier, worse than headline's -39.28%), turnover 13.7/y.
- **QQQ FAIL (honest):** best row `qqq_alt_vol / narrow / lag 0` WF 7/11 - ties
  the best binary baseline (`qqq_alt_vol` 7/11), not strictly greater. CAGR
  19.26%, MDD -43.76%.
- The narrow set beats the wide set on both branches (the 100/300 members hurt
  more than the diversification helps under leverage).

Interpretation: averaging window speeds is the first mechanism that moves the
binding WF gate on SPY, consistent with the 6C diagnosis that part of the WF
miss is window-luck/whipsaw. SPY's 13/17 SUCCESS feeds the 7F composition slot.
NOT a gate pass claim: G3 at the gate level would also require the full suite
(PBO/DSR/etc.) with the updated ledger; that is Phase 8's job on user-chosen
configs `[advances_fin_ml, p.208-211]`, `[trading_systems_methods, p.939]`.

Validation status: not validated; diagnostic phase only. No deployment, no
paper-trade label, no mandate change.

## 2026-06-09 - Phase 7B Multi-Asset Portfolio of SMA200 Rotations Executed

Runner: `uv run python -m lrs.phases.phase07b_multiasset_portfolio.run`.

Outputs: `phases/phase07b_multiasset_portfolio/{README.md,REPORT.md,plots/}`,
`results/phase07b_multiasset_portfolio.csv`, new helper
`lrs/lib/backtest.synth_leveraged_returns` (in-memory 2x synthesis,
`r = L*r_u - (L-1)*r_cash - 0.95%/252` `[leverage_for_the_long_run, p.16,
fn.22-23]`), tests `tests/test_lrs_phase07b.py`.

Pre-registered grid (72 rows, ledger 4077 + 72 = 4149): EW portfolio of
single-asset SMA200 rotations with UNIFORM grammar (shared L {1.75, 2.00},
ZROZ risk-off, shared vol gate {none, RV63<=40%}, lag 0..5), compositions
`EW5 {SPY,QQQ,IWM,XLK,GLD}`, `EW4 {SPY,IWM,XLK,GLD}`, `EW3 {SPY,QQQ,GLD}`
`[systematic_trading, p.42]`, `[systematic_trading, p.170-171]`, `[risk_parity,
p.80-81]`. IWM/XLK/GLD legs are synthetic-2x (disclosed limitation). Windows:
EW5/EW3 1986+ (11 WF windows), EW4 1979+ (13). Benchmark = EW underlying B&H
after-tax (final DARF only); controls = standalone legs vs their own
underlying. Built-in sanity PASSED after fix: degenerate {SPY} vs
`phase04.simulate_returns` rebuilt on the same window, max abs diff `0` (the
first sanity attempt compared different windows - a check bug, not a mechanism
bug; the DARF engine is path-dependent).

Result summary (honest FAIL 0/3 on the strict screen; structurally
informative):

- **EW5 best** (`L2.00/none/lag2`): WF **9/11 (81.8%)** vs EW bench - above
  the 75% G3 level - but TIES the best standalone leg (XLK 9/11, identifiable
  only ex-post) and MDD `-53.08%` breaches the -50% floor. FAIL (strict > and
  MDD).
- **EW3 best** (`L2.00/none/lag1`): WF 8/11 (72.7%) ties QQQ leg; CAGR 18.19%
  vs bench 12.16%; MDD `-47.50%` passes. FAIL (WF tie, not strict).
- **EW4 best**: WF 8/13 (61.5%), MDD -57.38%. FAIL.
- Structural reading: diversification across rotations does NOT lift WF above
  the best member, but it MATCHES the ex-post-best leg ex-ante while crushing
  leg-level MDD (portfolio -47..-57% vs legs -66..-86%). All best rows used
  vol gate `none`.

Interpretation: the EW-of-rotations family fails the pre-registered strict
screen and does not feed 7F on its own. The diversification benefit shows up
in MDD and in not having to pick the winning leg ex-ante - relevant context for
any future mix discussion, but not a WF unlock `[advances_fin_ml, p.208-211]`.

Validation status: not validated; diagnostic phase only. No deployment, no
paper-trade label, no mandate change.

## 2026-06-09 - Phase 7C Macro Growth-Trend-Timing Gate (UNRATE) Executed

Runner: `uv run python -m lrs.phases.phase07c_macro_gtt_gate.run`.

Outputs: `phases/phase07c_macro_gtt_gate/{README.md,REPORT.md,plots/}`,
`results/phase07c_macro_gtt_gate.csv`, new data ingest
`scripts/data_sprint/ingest_unrate_fred.py` ->
`data/external/macro/unrate_monthly.parquet` (FRED UNRATE 1948+, no auth),
loader extension `macro_data_loader.{UNRATE_LAG_TD,load_unrate_monthly}`,
tests `tests/test_lrs_phase07c.py`.

CITATION EXCEPTION (user-approved 2026-06-09): rule `UNRATE > SMA12m(UNRATE)`
from the Philosophical Economics "Growth-Trend Timing" essay (blog, no book
source); family anchored on `[leverage_for_the_long_run, p.9]` (S&P below
200dma 68.2% of recession time vs 19.4% of expansion time). Honest alignment:
publish lag committed at **25 trading days** (BLS first-Friday-next-month),
more conservative than the 10 td sketched in the round plan; FRED revised-data
vintage caveat recorded `[advances_fin_ml, p.31-34]`.

Pre-registered grid (72 rows, ledger 4149 + 72 = 4221): 6 bases x 2 override
scopes (`trend_only` keeps the vol gate alive in expansions; `trend_and_vol`
holds full target leverage) x lag 0..5. Sanity PASSED: macro_risk forced True
reproduces the binary base, max abs diff `0` both branches.

Result summary (honest FAIL 0/2 - MDD is the binding criterion, NOT WF):

- **Largest WF lift of the whole restart:** SPY best `spy_top/trend_only/lag0`
  WF **14/17 (82.4%)** vs baseline 12/17, CAGR 16.56% (> headline); QQQ best
  `qqq_lower_lev/trend_only/lag4` WF **10/11 (90.9%)** vs 7/11, CAGR 21.76%
  (> headline). Both clear the G3 75% level by a wide margin.
- **But the MDD floor breaks on both:** SPY -58.87%, QQQ -52.14% (< -50%).
  Sweep check: **zero rows in the entire 72-row grid combine WF > baseline
  with MDD >= -50%** - the trade-off is structural, exactly the pre-registered
  risk (non-recession crashes held at leverage; 1987-style windows).
- Screen verdict: FAIL on criterion 3 (MDD) for both branches.

Interpretation: the GTT mechanism does exactly what the 6C forensics predicted
(removing expansion-window timing cost fixes the WF gate) but reintroduces the
drawdown the SMA gate was protecting against. The obvious follow-up - macro
gate composed with a smoother in-expansion exposure (7A ensemble or
vol-target) - belongs to 7F only if the >=2-SUCCESS pre-condition is met;
otherwise it needs a fresh pre-registration in a future round.

Validation status: not validated; diagnostic phase only. No deployment, no
paper-trade label, no mandate change.

## 2026-06-09 - Phase 7D Quadratic Vol-Targeting sigma^2/RV^2 Executed

Runner: `uv run python -m lrs.phases.phase07d_vol_target_quadratic.run`.

Outputs: `phases/phase07d_vol_target_quadratic/{README.md,REPORT.md,plots/}`,
`results/phase07d_vol_target_quadratic.csv`, tests `tests/test_lrs_phase07d.py`.

Pre-registered grid (72 rows, ledger 4221 + 72 = 4293): single variation on
Phase 6B - leverage scalar squared to the continuous-Kelly inverse-variance
form `L_t = clip(sigma^2/RV^2, 0, L_max)` `[volatility_trading, p.135, p.138]`,
cap = fractional Kelly `[volatility_trading, p.139-140]`; 6B ladder/inertia/
gate/tax verbatim. 2 branches x sigma {30,35,40%} x RV {21,63} x lag 0..5.
Control per branch = better of {binary headline, 6B linear best}.

Result summary (QQQ SUCCESS - first QQQ WF lift of the restart; SPY FAIL):

- **QQQ SUCCESS:** best `sigma 40% / RV21 / lag 2` WF **8/11 (72.7%)** vs
  control 7/11, CAGR 19.53% (above the 19.46% headline), MDD -42.63% (within
  the floor). The harder vol response does flip an extra OOS window.
- **SPY FAIL (honest):** best `sigma 40% / RV21 / lag 3` WF 12/17 - ties the
  control, not strictly greater. CAGR 15.34%, MDD -39.28%.

Round status after 7D: 7A SPY SUCCESS + 7D QQQ SUCCESS = 2 successes among
{7A, 7B, 7C, 7D} -> the pre-registered 7F composition condition IS met
(compose the two winning mechanisms: 7A ensemble fraction x 7D quadratic
vol-target).

Validation status: not validated; diagnostic phase only. No deployment, no
paper-trade label, no mandate change.

## 2026-06-09 - Phase 7E Managed-Futures Risk-Off Sleeve Executed (LOW-POWER)

Runner: `uv run python -m lrs.phases.phase07e_mf_risk_off.run`.

Outputs: `phases/phase07e_mf_risk_off/{README.md,REPORT.md,plots/}`,
`results/phase07e_mf_risk_off.csv`, tests `tests/test_lrs_phase07e.py`.

Pre-registered grid (60 rows, ledger 4293 + 60 = 4353): headline bases with 5
risk-off sleeves (control / 100% DBMF / 50-50 / 70 DBMF-30 KMLM / 50 base-50
MF-blend) x lag 0..5, DBMFSIM/KMLMSIM read-only from the RSC sleeve matrix
`[evidence_based_ta, p.380-384, p.398]`, `[risk_parity, p.80-81]`. DECLARED
LOW-POWER: 2000+ window, only 6 WF windows. Sanity: control rerun max abs
diff 0 both branches.

Result summary (SPY weak SUCCESS; QQQ FAIL):

- **SPY SUCCESS (weak lead):** `100% DBMF / lag 4`: WF 5/6 vs control 4/6,
  CAGR 13.45%, MDD **-31.55%** vs control -39.28% - the MF sleeve materially
  compresses drawdown on the 2000+ window.
- **QQQ FAIL:** best `50 base / 50 DBMF / lag 3` WF 4/6 vs control 5/6.
- KMLMSIM reaches back to 1988; a KMLM-only longer-window variant is possible
  future work (not run - outside the pre-registered grid).

Interpretation: managed futures as risk-off is a promising defensive
complement on SPY (drawdown compression), but the 6-window evidence is weak by
construction and does NOT feed 7F (incompatible window). It is a candidate
ingredient for a future pre-registered round if the 7-round survivors go to
Phase 8 `[advances_fin_ml, p.208-211]`.

Validation status: not validated; diagnostic low-power phase only. No
deployment, no paper-trade label, no mandate change.

## 2026-06-09 - Phase 7F Composition Executed; Phase 7 Round CLOSED

Runner: `uv run python -m lrs.phases.phase07f_composition.run`.

Outputs: `phases/phase07f_composition/{README.md,REPORT.md,plots/}`,
`results/phase07f_composition.csv`, tests `tests/test_lrs_phase07f.py`.

Pre-registered grid (24 rows, ledger 4353 + 24 = **4377 final**): composition
of the two round winners with FROZEN parameters - 7A ensemble fraction
(narrow {150,175,200,225}) x 7D quadratic vol-target (sigma 40%/RV21) - in two
variants (`ens_x_quad`, `ens_x_quad_gated`), lag 0..5 only. Sanity PASSED
(f==1 reproduces the pure quadratic ladder pipeline, max abs diff 0).

Result (honest FAIL 0/2): SPY best `ens_x_quad_gated/lag2` WF 12/17 vs round
best 13/17; QQQ best `ens_x_quad/lag0` WF 6/11 vs round best 8/11. The two
mechanisms do NOT stack - smoothing the signal dilutes the sizing edge and
vice versa. The round survivors remain the SINGLE-mechanism winners.

### Phase 7 round consolidated verdict (ledger 4005 -> 4377)

| Phase | Mechanism | Screen | Key number |
|---|---|---|---|
| 7A | Ensemble multi-lookback fraction | **SPY SUCCESS** / QQQ FAIL | SPY WF **13/17 (76.5%)** vs 12/17 - first row at the G3 75% level in the restart; CAGR 14.49%, MDD -43.16% |
| 7B | EW multi-asset rotation portfolio | FAIL 0/3 | EW5 WF 9/11 but ties ex-post-best leg; MDD -53% |
| 7C | Macro GTT/UNRATE gate | FAIL 0/2 (MDD) | Biggest WF lift ever (SPY 14/17, QQQ 10/11) but zero rows hold MDD >= -50% |
| 7D | Quadratic vol-target sigma^2/RV^2 | SPY FAIL / **QQQ SUCCESS** | QQQ WF **8/11 (72.7%)** vs 7/11; CAGR 19.53% > headline; MDD -42.63% |
| 7E | Managed-futures risk-off (low-power) | **SPY weak SUCCESS** / QQQ FAIL | 100% DBMF: WF 5/6 vs 4/6, MDD -31.6% vs -39.3% (6 windows only) |
| 7F | Composition 7A x 7D (frozen params) | FAIL 0/2 | Mechanisms do not stack (SPY 12/17, QQQ 6/11) |

Round survivors for a possible Phase 8 (user must pick; NOT auto-promoted):

- **SPY candidate:** 7A ensemble `spy_alt_off / narrow {150,175,200,225} /
  lag 2` - after-tax CAGR 14.49%, MDD -43.16%, WF 13/17 (76.5%, nominally at
  the G3 level).
- **QQQ candidate:** 7D quadratic `sigma 40% / RV21 / lag 2` - after-tax CAGR
  19.53%, MDD -42.63%, WF 8/11 (72.7%, still below the 9/11 G3 level).

Phase 8 (pre-registered in the round plan): run the FULL mandate SS5 gate
suite (PBO matrix = winning family grid per branch, DSR n_trials = 4377, WF
identical to Phase 4, OOS/FWD/bootstrap/xlib) on at most 2 user-chosen
configs. QQQ at 8/11 would FAIL G3 as-is; SPY at 13/17 nominally clears G3 but
must survive the other six gates with the bigger ledger. Until then: nothing
is validated, nothing is promoted, mandate SS1 unchanged.

## 2026-06-10 - Phase 8 Final Gate Suite Executed (FAIL 0/2; family RE-CLOSED)

User decision (2026-06-10): validate the two natural survivors.

Runner: `uv run python -m lrs.phases.phase08_final_gates.run`.

Outputs: `phases/phase08_final_gates/{README.md,REPORT.md,plots/}`,
`results/phase08_final_gates.csv`, tests `tests/test_lrs_phase08.py`.

Setup (pre-registered): canonical SS5 suite via `lrs/lib/validation.
run_gate_suite`, Phase 4 WF geometry verbatim; PBO matrix = winning family
grid per branch (7A SPY grid 36 configs; 7D QQQ grid 36 configs); DSR
`n_trials = 4377` (full in-repo lineage through 7F; letf-lab excluded =
honest undercount). **+0 trials; ledger stays 4377.** Sanity PASSED: both
configs reproduce their committed Phase 7 CSV rows (max abs diff ~1e-17).

Result (FAIL 0/2 - per the pre-registered rule, both configs re-closed):

- **`spy_7a_ensemble` (spy_alt_off / narrow / lag 2): 6/7 - FAIL on G2 DSR
  only.** G1 PBO 0.397 PASS; **G2 DSR p = 0.052 vs alpha 0.05 FAIL** (the
  margin is 0.002, and the excluded letf-lab lineage means the honest p is
  HIGHER, not lower - this is a real fail, not noise); **G3 WF 13/17 PASS -
  the first time the restart's universal binding gate passes**; G4 OOS, G5
  FWD, G6 bootstrap (CI low > 0), G7 cross-lib all PASS.
- **`qqq_7d_quadratic` (sigma 40 / RV21 / lag 2): 4/7 - FAIL G1/G2/G3.** PBO
  0.651, DSR p 0.138, WF 8/11 (72.7% < 75%) - exactly the recorded honest
  prior. G4-G7 PASS.

Interpretation: the Phase 7 round genuinely moved the binding gate - the SPY
ensemble is the first config in the whole restart to clear the walk-forward
bar - but the Sharpe does not survive deflation against the 4377-trial search
that produced it. Per the mandate ("quase la" nao passa) and the
pre-registered verdict rule: no re-runs, no threshold adjustment, both configs
re-closed; the LRS line returns to the shelf pending genuinely new literature
or regime. The honest summary of the whole line: timing geometry is real but
its edge is too small to survive honest multiple-testing accounting
`[advances_fin_ml, p.273-275]`, `[advances_fin_ml, p.208-211]`,
`[testing_tuning, p.327-335]`.

Validation status: gates RUN on the two survivors; 0/2 pass; line CLOSED
again. No deployment, no paper-trade label, no mandate change.

## 2026-06-10 - Phase 9 Quadratic Vol-Targeting with 3x Ceiling (user-directed, return-first)

User request after the Phase 8 closure: "ganhos maiores" using TQQQ/UPRO.
Phase 9 is a user-directed, return-first exploration of ONE variation inside
the 7D family - it does NOT reverse Phase 8's verdict.

Runner: `uv run python -m lrs.phases.phase09_vol_target_3x_ceiling.run`.

Outputs: `phases/phase09_vol_target_3x_ceiling/{README.md,REPORT.md,plots/}`,
`results/phase09_vol_target_3x_ceiling.csv`, tests `tests/test_lrs_phase09.py`.

Pre-registered grid (48 rows, ledger 4377 + 48 = **4425**): 2 branches x
L_max {2.50, 3.00} x sigma {40%, 45%} x RV21 x lag 0..5; ladder rungs above
2x use the cached UPROSIM/TQQQSIM `[volatility_trading, p.135, p.138-140]`.
Return-first screen: best CAGR among MDD >= -50% rows; SUCCESS = CAGR > 7D
winner AND floor held AND WF not worse. Sanity PASSED (7D winners reproduced,
~2.8e-17).

Result (SPY SUCCESS / QQQ FAIL):

- **SPY SUCCESS:** `L_max 2.50 / sigma 40% / RV21 / lag 3` - CAGR **16.81%**
  (+1.47pp vs 7D winner 15.34%; +1.37pp vs binary headline), MDD **-47.47%**
  (tolerable tier, inside the floor), WF 12/17 (unchanged), Sharpe 0.675,
  Calmar 0.354, turnover 6.1/y. All L_max 3.00 SPY rows BREACH the floor
  (-53.8% to -64.2%).
- **QQQ FAIL:** ZERO rows inside the -50% floor (best floor-breacher: L3.00
  sigma40 lag1, 24.74% / -61.76%). Confirms the Phase 2 frontier: QQQ above
  ~2x effective leverage is ruin-adjacent under every variation tested.
  Diagnostic curiosity (NOT a candidate): L3.00/sigma45/lag2 reached WF 9/11
  (the G3 level) at -67% MDD.
- **Honest mechanical reading:** with sigma 40-45%, the quadratic scalar is
  PINNED at the cap ~99% of risk-on days (SPY RV21 rarely exceeds 40%), so
  the winning config behaves like constant-2.5x with crash de-leveraging.
  Versus the Phase 2 binary L2.50 best-Calmar row (17.38% / -48.54% / 0.358)
  it is roughly a wash (16.81% / -47.47% / 0.354) - the quadratic form adds
  no edge at this leverage on SPY, consistent with 7D's SPY FAIL. The CAGR
  gain comes from the LEVERAGE, not the sizing rule.

Status: return-first diagnostic lead only. The SPY 2.5x config would face the
full SS5 suite at ledger 4425 for any promotion-grade claim - where DSR
already killed a stronger risk-adjusted candidate (7A, p 0.052) - so its
realistic validation odds are LOW and recorded as such. No deployment, no
paper-trade label, no mandate change `[advances_fin_ml, p.273-275]`.

## 2026-06-10 - Phase 10 Drawdown-Contingent Leverage Ladder ("Buy the Dip") Executed (FAIL 0/2)

User-proposed family (2026-06-10): lower leverage most of the time, ESCALATE
leverage when the underlying's drawdown crosses a threshold, de-escalate on
recovery - the contrarian opposite of every mechanism tested so far.

Runner: `uv run python -m lrs.phases.phase10_dip_leverage_ladder.run`.

Outputs: `phases/phase10_dip_leverage_ladder/{README.md,REPORT.md,plots/}`,
`results/phase10_dip_leverage_ladder.csv`, tests `tests/test_lrs_phase10.py`.

Pre-registered grid (144 rows, ledger 4425 + 144 = **4569**): 2 branches x
2 profiles {(1.0->2.0), (1.5->3.0)} x triggers {-10%, -20%, -30%} x exits
{ath, half-recovery} x lag 0..5; DD measured on the underlying; no SMA/vol
gate (clean isolation). Citable tension recorded upfront: equity indices =
countertrend-matching `[trading_systems_methods, p.13]` VS dips = high-vol
regimes where leveraged compounding dies `[leverage_for_the_long_run,
p.7-9]`. Sanity PASSED (never-fires trigger == constant L_base, diff 0).

Result (honest FAIL 0/2 - the cleanest negative of the whole restart):

- **ZERO rows among 144 hold the -50% floor.** Trial MDD range: -69.8%
  (best: SPY -30%/1.0->2.0) to **-102.7%**; 8 configs are literal total ruin
  (terminal <= 0 via leveraged riding of long bears + DARF timing).
- **The CAGR does not pay for the risk either:** best SPY dip row 12.65% vs
  LRS headline 15.44% (-39.3% MDD); best QQQ dip row 14.86% (at -98.9% MDD!)
  vs plain QQQ B&H 14.36%. Most QQQ dip rows UNDERPERFORM unlevered B&H.
- Mechanism anatomy: the trigger escalates early in every long bear (1929-32
  SPY -86%, 1973-74, 2000-02 QQQ -83%, 2008) and rides max leverage to the
  bottom. Deeper triggers reduce episodes (6 vs 22) but cannot avoid the
  catastrophic ones - you cannot know ex-ante which -20% becomes -80%.
- Answer to the user's question "what dip level is interesting to buy with
  leverage?": **none on this grid.** The Gayed thesis survives its direct
  inversion test: dips are exactly when leverage must be LOW
  `[leverage_for_the_long_run, p.7-9]`.
- Nuance preserved: dip-buying DOES work in this repo's data in ONE form -
  contribution flows (6A Part 2 buy-most-underweight DCA), where new money
  buys dips with no path-risk on the existing position. What fails is
  escalating LEVERAGE on existing capital.

Validation status: return-first diagnostic; family FAIL and closed. No
deployment, no paper-trade label, no mandate change.
