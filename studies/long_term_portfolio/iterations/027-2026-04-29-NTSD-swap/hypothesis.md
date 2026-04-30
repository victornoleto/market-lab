# Iter 027 — NTSD swap (ex-US developed equity stack, GLOBAL category)

## Hypothesis (one paragraph)

NTSD adds intl-developed equity inside a 1.5x levered wrapper (90% US +
60% EAFE futures). Reduces home-country bias without sacrificing
leverage. Tests whether iter 014/015's failed intl-equity overlay
attempts work when **stacked inside** the wrapper instead of added
outside.

## Primary citation

`[risk_parity, ch.5, p.10]` Carlson cap-efficient stacking + WisdomTree
NTSD prospectus 2026-03-19.

## Configs tested (4)

| config | NTSX | NTSD | GDE | KMLM | TLT |
|---|---:|---:|---:|---:|---:|
| ntsd_lite_2055   | 20% |  5% | 25% | 35% | 15% |
| ntsd_mod_15105   | 15% | 10% | 25% | 35% | 15% |
| ntsd_med_10155   | 10% | 15% | 25% | 35% | 15% |
| ntsd_heavy_5205  |  5% | 20% | 25% | 35% | 15% |

## Synth used

NTSDSIM = `0.90 SPYSIM + 0.60 VEASIM - 75bps/y`. INCOMPLETE — active
management unmodeled.

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: if best config doesn't beat iter
  023 mean Sharpe (lh_56y=1.189, vt_real=1.004, ndx_real=1.135;
  mean=1.109) on >=1/3 datasets => sleeve closed.
- **KILL #2 (monotonic regression)**: if Sharpe monotonically falls
  with NTSD weight (5% -> 20%) across the 4 configs => sleeve closed.
