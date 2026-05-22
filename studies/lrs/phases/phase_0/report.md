# studies/lrs — Phase 0 Report

Generated: 2026-05-22T14:19:30.929820+00:00  ·  data: testfol.io (1885-03-20 → 2026-05-21, 35358 bars)

## Hypothesis

When SPY closes above its 200-day SMA, a 2× or 3× S&P-500 LETF outperforms unlevered SPY net of BR taxes; when SPY closes below, holding cash dominates riding the LETF down. `[leverage_for_the_long_run, p.13]`

## Parameters

| Parameter | Value |
|---|---|
| Data source | testfol.io synthetic (SPYSIM / SSOSIM / UPROSIM) |
| Period | 1885-12-31 → 2026-05-21 (35158 bars) |
| Filter / lookback / band | SMA / 200d / 0% |
| Execution | signal close T → exposure T+1 |
| Cash off-leg yield | 0% |
| Commission / spread | 0 bps |
| Tax rate / cadence | 15% / annual, first bar of next year |

## Metrics

| Curve | Start | End | Terminal× | CAGR | MDD | Sharpe | Sortino | Switches | Tax events | Tax drag |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B&H SPY | 1885-12-31 | 2026-05-21 | 333,553.5× | 9.54% | 83.65% | 0.61 | 0.87 | 0 | 0 | 0.00 |
| B&H SSO | 1885-12-31 | 2026-05-21 | 2,341,338.4× | 11.08% | 98.42% | 0.48 | 0.67 | 0 | 0 | 0.00 |
| B&H UPRO | 1885-12-31 | 2026-05-21 | 193,360.9× | 9.12% | 99.91% | 0.43 | 0.61 | 0 | 0 | 0.00 |
| LRS-SSO | 1885-12-31 | 2026-05-21 | 10,517,603.1× | 12.29% | 80.37% | 0.61 | 0.85 | 811 | 57 | 1558770.16 |
| LRS-UPRO | 1885-12-31 | 2026-05-21 | 410,768,608.1× | 15.28% | 92.80% | 0.58 | 0.81 | 811 | 53 | 57856496.09 |

## Plots

Equity overlay (log scale, normalised to 1.0 at start):

![equity overlay](plots/equity_overlay.png)

Ratio to B&H SPY (log scale):

![ratio to SPY](plots/ratio_to_spy.png)

## Observations

- LRS-SSO beats B&H SSO by 1.20% CAGR (post-BR-tax).
- LRS-SSO reduces the B&H SSO drawdown by 18.06% (80.37% vs 98.42%).
- LRS-UPRO beats B&H UPRO by 6.16% CAGR (post-BR-tax).
- LRS-UPRO reduces the B&H UPRO drawdown by 7.11% (92.80% vs 99.91%).
- LRS-SSO beats B&H SPY by 2.74% CAGR (post-BR-tax).
- LRS-UPRO beats B&H SPY by 5.73% CAGR (post-BR-tax).

## Sanity checks — all passed ✔

## Caveats

- Pre-2006/2009 SSO/UPRO bars are synthetic (Gayed `r = L·r_SPX − fee/252`), not measured.
- No commission / spread / slippage modelled. A whipsaw-heavy signal will look better here than in production.
- Single-window descriptive run — no walk-forward, no PBO/DSR. See SPEC.md out-of-scope section.
- Cash off-leg yields 0%, ignoring Fed Funds. Layer CASHX in phase-1+ if signal proves out.

## Suggestions for phase 1+

- Add CASHX as off-leg (Fed Funds proxy) and re-measure.
- Layer realistic frictions: Inter Internacional commission, ~5 bps spread per switch.
- Walk-forward + bootstrap CI on the regime-rule parameters (lookback, band).
- Tiingo real-ETF overlay (2009+) for SSO/UPRO post-inception OOS sanity check.
- Regime stratification: bull/bear/sideways performance attribution.
- Sweep MA window {50, 100, 125, 150, 200} per Gayed Table 6 `[leverage_for_the_long_run, p.14]`.

## Citations

- SMA200 regime signal: `[leverage_for_the_long_run, p.13]`
- 2× / 3× leverage tested in paper: `[leverage_for_the_long_run, p.17, Table 8]`
- Cash off-leg (not BIL): `[leverage_for_the_long_run, p.21]`
- Synthetic LETF formula: `[leverage_for_the_long_run, p.16]`
- BR 15% IR on US-listed ETF gains: `docs/investment-mandate.md` §1
- testfol.io as long-history source: Phase 3.5b Task 7a cross-check

