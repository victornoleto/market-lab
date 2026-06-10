# Phase 7E — Managed-Futures Risk-Off Sleeve (PRE-REGISTRATION)

> Status: research-only / diagnostic. Nothing here authorizes deployment, paper
> trading or a mandate change. Mandate §1 (maintenance mode) unchanged.
> **Round order note:** Phase 7 round runs 7A → 7B → 7C → 7D → 7E → (7F) → 8.
> This phase runs LAST among the independents because the defensive side is
> NOT the binding WF bottleneck — it is a complement, declared low-power.

## Question

Phase 1 found risk-off diversification (ZROZ/GLD/IEF) to be a real driver. The
one cached defensive family never tested in `lrs/` is **managed futures /
trend-following**: a positive-expectancy risk premium earned for providing
liquidity/insurance to hedgers, systematically harvested by the MLM-style
12-month MA rule on commodities `[evidence_based_ta, p.380-384, p.398]`, and
the same sleeve class the RSC anchor stacks for crisis diversification
`[risk_parity, p.80-81]`. Local proxies exist in
`studies/return_stacked_core/us_core/series/remote_prices.parquet`
(`DBMFSIM`, `KMLMSIM`; read-only, testfolio cache untouched). Hypothesis under
test: replacing part of the bond/gold sleeve with managed futures improves the
defensive leg (MDD / WF on the truncated window) without hurting CAGR.

## Mechanism (one family — risk-off composition only)

- Headline bases per branch, verbatim (SPY `L2.00 / RV21<=30%`; QQQ
  `L1.75 / RV63<=40%`); ONLY the risk-off sleeve changes.
- Pre-registered sleeves (5):
  1. `control` — the branch headline sleeve, re-run on this phase's window;
  2. `100% DBMF`;
  3. `50% base + 50% DBMF` (headline sleeve scaled 0.5);
  4. `70% DBMF / 30% KMLM`;
  5. `50% base + 50% (70 DBMF / 30 KMLM)`.
- Weekly cadence, lag-through-CASHX, `AnnualDarfEngine` verbatim.

**Window (consequence of data, declared):** `DBMFSIM` starts 2000-01-03, so
ALL rows (including controls) run on the common 2000+ window — only ~6 WF
windows per branch. This is LOW-POWER evidence by construction; the phase can
only produce a weak lead or a weak negative. (`KMLMSIM` reaches back to 1988;
a KMLM-only longer-window variant is possible future work, not this grid.)

## Pre-registered grid — 60 rows (+60 to the n_trials ledger → 4293 + 60 = 4353)

| Axis | Values |
|---|---|
| Branch (headline geometry fixed) | SPY, QQQ |
| Risk-off sleeve | the 5 above (control included as a counted trial on the truncated window) |
| lag | `0..5` |

**Built-in sanity (non-trial):** the control sleeve at the committed headline
lag must match a direct `phase04.simulate_returns`-style rerun restricted to
the same 2000+ window (max abs diff reported).

## Pre-registered screen (per branch, on the best non-control row by WF beats, tie-break Calmar)

1. WF beat count (vs underlying after-tax, 2000+ splits) **strictly greater**
   than the best control row of the branch.
2. MDD **no worse** than the best control row.
3. MDD ≥ −50% (round constraint).

All three → diagnostic SUCCESS (weak lead; does NOT feed 7F — incompatible
window). Any miss → honest FAIL. No deployment, no paper-trade label, no
mandate change `[advances_fin_ml, p.208-211]`.

## Outputs

`lrs/results/phase07e_mf_risk_off.csv`, `REPORT.md`, plots (equity/DD vs
control, WF comparison, frontier by sleeve), `tests/test_lrs_phase07e.py`.
