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
