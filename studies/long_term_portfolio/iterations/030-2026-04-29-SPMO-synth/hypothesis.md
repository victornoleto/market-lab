# Iter 030 — SPMO synth add (US momentum sleeve, US category)

## Hypothesis (one paragraph)

Capture iter 016's UMD-academic +signal in **deployable form** via SPMO
synth. SPMO embeds SPY beta + cross-sectional momentum overlay. Per
Frazzini-Israel-Moskowitz 2018, real momentum ETFs capture ~60-70% of
UMD long-short premium due to long-only constraint + costs. Tests
whether ~60% UMD scaling delivers an isolable Sharpe edge vs iter 023
without inflating standalone (KILL #3).

## Primary citation

`[stocks_on_the_move, p.21-30]` Clenow time-series momentum;
Jegadeesh-Titman 1993 cross-sectional momentum.

## Configs tested (4)

| config | NTSX | GDE | KMLM | TLT | SPMOSIM |
|---|---:|---:|---:|---:|---:|
| spmo_lite  | 22.5% | 25% | 32.5% | 15% |  5% |
| spmo_mod   | 20.0% | 25% | 30.0% | 15% | 10% |
| spmo_med   | 17.5% | 25% | 27.5% | 15% | 15% |
| spmo_heavy | 15.0% | 25% | 25.0% | 15% | 20% |

NTSX + KMLM each absorb the SPMO cut equally.

## Synth used

SPMOSIM = `SPYSIM + 0.60 × UMD_KF − 35bps/y`. INCOMPLETE — UMD academic
capture coefficient (0.60) per Frazzini-Israel-Moskowitz 2018 is an
estimate; real SPMO may capture differently due to S&P 500 universe
restriction (top-100 cross-sectional momentum filter) vs Ken French's
full CRSP universe.

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: if best config doesn't beat iter
  023 mean Sharpe (lh_56y=1.189, vt_real=1.004, ndx_real=1.135) on
  >=1/3 datasets => sleeve closed.
- **KILL #2 (monotonic regression)**: if Sharpe monotonically falls
  with SPMO weight 5% -> 20% on all 3 datasets => sleeve closed.
- **KILL #3 (no-free-lunch synth)**: if SPMO_synth standalone Sharpe
  > 1.5 => synth has model artifact (UMD overlay double-dip), fix and
  rerun. Real SPMO has live Sharpe ~0.7-0.9 since 2015 inception;
  long-history synth should not exceed published academic UMD Sharpe
  (~0.4-0.6) plus equity beta blend.
