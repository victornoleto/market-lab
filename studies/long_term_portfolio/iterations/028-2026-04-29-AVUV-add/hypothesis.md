# Iter 028 — AVUV add (US small-cap value factor, US category)

## Hypothesis (one paragraph)

Avantis US Small-Cap Value adds factor exposure (size + value +
profitability) historically uncorrelated with US large-cap regime.
Tests whether **size factor at 1× notional** outside the wrapper
recovers what iter 013's VBRSIM tilt couldn't (post-2008 "death of
value" regime).

## Primary citation

`[risk_parity, ch.2, p.37-41]` Fama-French SCV factor framework;
`[advances_fin_ml, p.31-34]` factor cross-validation.

## Configs tested (4)

| config | NTSX | GDE | KMLM | TLT | AVUV |
|---|---:|---:|---:|---:|---:|
| avuv_lite  | 22.5% | 25% | 32.5% | 15% |  5% |
| avuv_mod   | 20.0% | 25% | 30.0% | 15% | 10% |
| avuv_med   | 17.5% | 25% | 27.5% | 15% | 15% |
| avuv_heavy | 15.0% | 25% | 25.0% | 15% | 20% |

NTSX + KMLM each absorb the AVUV cut equally.

## Synth used

AVUVSIM = `VBRSIM + 75bps/y tilt premium`. INCOMPLETE — proxy index
(Vanguard small-cap value) ≠ Avantis screening (size+value+profitability
combined); tilt premium estimated from Avantis published net-of-fee
returns vs benchmark.

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: if best config doesn't beat iter
  023 mean Sharpe (lh_56y=1.189, vt_real=1.004, ndx_real=1.135) on
  >=1/3 datasets => sleeve closed.
- **KILL #2 (monotonic regression)**: if Sharpe monotonically falls
  with AVUV weight 5% -> 20% on all 3 datasets => sleeve closed.
