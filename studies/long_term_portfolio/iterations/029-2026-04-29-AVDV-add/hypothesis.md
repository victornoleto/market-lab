# Iter 029 — AVDV add (intl developed SCV factor, GLOBAL category)

## Hypothesis (one paragraph)

AVDV is the intl mirror of AVUV (Avantis International Small-Cap Value).
User confirms ~40% 2025 return — intl SCV regime cycle is inverted vs
US 2025. Tests **factor + geographic** combined axis: does intl SCV
recover what US SCV (iter 028) and intl-equity overlay (iter 014) each
failed to deliver in isolation?

## Primary citation

`[ilmanen_expected_returns, ch.19]` intl factor diversification;
`[risk_parity, ch.2, p.37-41]` Fama-French SCV factor framework.

## Configs tested (4)

| config | NTSX | GDE | KMLM | TLT | AVDV |
|---|---:|---:|---:|---:|---:|
| avdv_lite  | 22.5% | 25% | 32.5% | 15% |  5% |
| avdv_mod   | 20.0% | 25% | 30.0% | 15% | 10% |
| avdv_med   | 17.5% | 25% | 27.5% | 15% | 15% |
| avdv_heavy | 15.0% | 25% | 25.0% | 15% | 20% |

NTSX + KMLM each absorb the AVDV cut equally (mirrors iter 028 AVUV
structure).

## Synth used

AVDVSIM = `VSSSIM + 100bps/y tilt premium`. INCOMPLETE — VSSSIM is
Vanguard FTSE All-World ex-US Small-Cap (passive); 100bps tilt premium
is Avantis published net-of-fee estimate (intl SCV historically richer
than US SCV due to less crowded factor exposure).

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: if best config doesn't beat iter
  023 mean Sharpe (lh_56y=1.189, vt_real=1.004, ndx_real=1.135) on
  >=1/3 datasets => sleeve closed.
- **KILL #2 (monotonic regression)**: if Sharpe monotonically falls
  with AVDV weight 5% -> 20% on all 3 datasets => sleeve closed.
