# Iter 032 — AVEM add (Emerging Markets factor, GLOBAL category)

## Hypothesis (one paragraph)

AVEM = Avantis Emerging Markets Equity (factor-tilted EM). Tests
whether EM factor sleeve adds Sharpe via low-correlation diversification
to iter 023's developed-market equity stack. EM factor exposure
historically uncorrelated with US large-cap regime; combined with
KMLM's crisis-alpha and GDE's gold-equity hybrid, AVEM at 1× notional
should deliver isolable diversification benefit.

## Primary citation

`[ilmanen_expected_returns, ch.19]` intl + EM diversification;
`[risk_parity, ch.2, p.37-41]` Fama-French factor framework.

## ⚠️ Window caveat — DOCUMENT PROMINENTLY

**VWOSIM (the EM equity proxy underlying AVEMSIM) starts 1994-05-04.**
This means AVEM-using configs **CANNOT run lh_56y fully** — the
intersection of all components (NTSXSIM 1986+, GDESIM 1987+, KMLMSIM
1987+, TLTSIM 1962+, AVEMSIM 1994+) bottlenecks at **AVEMSIM 1994+**.
Effective window: **1994-2026 = 32y**, not 56y. Comparisons vs iter 023
(56y) are on a **different time-window** — interpret cautiously.

The vt_real (2008+) and ndx_real (2010+) datasets are unaffected since
their start dates are well after 1994. Only the lh_56y comparison is
window-truncated (lh_56y in this iter effectively covers 1994-2026).

`run_iter_full`'s internal alignment uses dropna() across components —
it should automatically intersect on 1994+.

## Configs tested (4)

| config | NTSX | GDE | KMLM | TLT | AVEM |
|---|---:|---:|---:|---:|---:|
| avem_lite  | 22.5% | 25% | 32.5% | 15% |  5% |
| avem_mod   | 20.0% | 25% | 30.0% | 15% | 10% |
| avem_med   | 17.5% | 25% | 27.5% | 15% | 15% |
| avem_heavy | 15.0% | 25% | 25.0% | 15% | 20% |

NTSX + KMLM each absorb the AVEM cut equally.

## Synth used

AVEMSIM = `VWOSIM + 125bps/y tilt premium`. INCOMPLETE — VWOSIM is
Vanguard FTSE Emerging Markets (passive, market-cap weighted, no
quality screen); 125bps/y is the published Avantis EM tilt premium
estimate (highest of the AV* family, reflecting EM market inefficiency
and richer factor exposure).

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: if best config doesn't beat iter
  023 mean Sharpe (lh_56y=1.189, vt_real=1.004, ndx_real=1.135) on
  >=1/3 datasets => sleeve closed. **Window caveat**: lh_56y here is
  only 32y effective, so the comparison vs iter 023's 56y lh_56y
  Sharpe should be interpreted as approximate.
- **KILL #2 (monotonic regression)**: if Sharpe monotonically falls
  with AVEM weight 5% -> 20% on all 3 datasets => sleeve closed.
