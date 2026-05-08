# Iter 031 — IDMO synth add (intl developed momentum sleeve, GLOBAL category)

## Hypothesis (one paragraph)

IDMO is the intl mirror of SPMO (Invesco S&P International Developed
Momentum). Tests whether the cross-sectional momentum factor in
ex-US developed equity adds Sharpe vs iter 023 — combined factor +
geographic axis. Per Jegadeesh-Titman 1993, momentum is empirically
strongest globally, not just US; per Asness-Moskowitz-Pedersen 2013,
intl momentum has lower correlation with US momentum than passive
intl-equity has with US-equity.

## Primary citation

`[ilmanen_expected_returns, ch.19]` intl factor diversification +
`[stocks_on_the_move, p.21-30]` Clenow time-series momentum +
Jegadeesh-Titman 1993 cross-sectional momentum.

## Configs tested (4)

| config | NTSX | GDE | KMLM | TLT | IDMOSIM |
|---|---:|---:|---:|---:|---:|
| idmo_lite  | 22.5% | 25% | 32.5% | 15% |  5% |
| idmo_mod   | 20.0% | 25% | 30.0% | 15% | 10% |
| idmo_med   | 17.5% | 25% | 27.5% | 15% | 15% |
| idmo_heavy | 15.0% | 25% | 25.0% | 15% | 20% |

NTSX + KMLM each absorb the IDMO cut equally (mirrors iter 028/029/030).

## Synth used

IDMOSIM = `VEASIM + 0.60 × UMD_KF − 60bps/y`. INCOMPLETE — uses **US
UMD_KF** as proxy for intl momentum factor (academic intl UMD data
not in our cache); 0.60 capture coefficient per Frazzini-Israel-
Moskowitz 2018; 60bps/y reflects IDMO's higher TER vs SPMO (intl
market-microstructure costs). The US-UMD-as-intl-proxy is the iter's
biggest synth caveat — real intl momentum factor has ~0.5-0.7
correlation with US UMD per AMP 2013, so the synth may overstate
IDMO's Sharpe contribution by 10-30%.

## KILLs pre-committed

- **KILL #1 (no-positive-config)**: if best config doesn't beat iter
  023 mean Sharpe (lh_56y=1.189, vt_real=1.004, ndx_real=1.135) on
  >=1/3 datasets => sleeve closed.
- **KILL #2 (monotonic regression)**: if Sharpe monotonically falls
  with IDMO weight 5% -> 20% on all 3 datasets => sleeve closed.
- **KILL #3 (no-free-lunch synth)**: if IDMO_synth standalone Sharpe
  > 1.5 => synth artifact (US UMD proxy double-dipping into VEA
  beta), fix and rerun. Real IDMO live Sharpe ~0.5-0.7 since 2017
  inception (smaller AUM, less factor capture).
