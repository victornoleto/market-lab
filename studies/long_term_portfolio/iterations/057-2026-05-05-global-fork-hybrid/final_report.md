# Iter 057 — `global-fork-hybrid-60-40-us-nonus`

**Engine:** long_term_portfolio internal (synths.py + portfolio_returns_from_config)
**Dataset:** lh_56y (lh_56y; per-config window clips to underlying inception)
**Selected:** `B4_us_only`

## Benchmarks (full lh_56y window, gross-of-tax)

| benchmark | window | CAGR | MDD | Sharpe |
|---|---|---:|---:|---:|
| SPY (1x) | 1986-01-03 → 2026-04-17 (40.3y) | 11.47% | 55.14% | 0.682 |
| VT (1x via VTSIM) | 1970-01-02 → 2026-04-24 (56.3y) | 9.97% | 58.35% | 0.663 |

## Ranking by Sharpe

| # | config | window | CAGR | MDD | Sharpe |
|---:|---|---|---:|---:|---:|
| 1 | `B4_us_only` | 1988-01-04 → 2026-04-17 (38.3y) | 14.62% | 28.38% | 1.027 |
| 2 | `70_30__NB1_factor40` | 1994-12-30 → 2026-02-27 (31.2y) | 12.92% | 35.95% | 0.925 |
| 3 | `70_30__NB2_factor30` | 1994-12-30 → 2026-02-27 (31.2y) | 12.87% | 35.99% | 0.919 |
| 4 | `70_30__NB3_avnm_only` | 1994-05-05 → 2026-04-17 (32.0y) | 12.56% | 36.38% | 0.896 |
| 5 | `60_40__NB1_factor40` | 1994-12-30 → 2026-02-27 (31.2y) | 12.30% | 38.78% | 0.874 |
| 6 | `60_40__NB2_factor30` | 1994-12-30 → 2026-02-27 (31.2y) | 12.23% | 38.95% | 0.866 |
| 7 | `55_45__NB1_factor40` | 1994-12-30 → 2026-02-27 (31.2y) | 11.98% | 40.30% | 0.845 |
| 8 | `60_40__NB3_avnm_only` | 1994-05-05 → 2026-04-17 (32.0y) | 11.87% | 39.47% | 0.837 |
| 9 | `55_45__NB2_factor30` | 1994-12-30 → 2026-02-27 (31.2y) | 11.90% | 40.51% | 0.837 |
| 10 | `55_45__NB3_avnm_only` | 1994-05-05 → 2026-04-17 (32.0y) | 11.52% | 41.14% | 0.806 |

## % rolling-windows beating SPY

| config | 3y | 5y | 10y | 15y |
|---|---:|---:|---:|---:|
| `B4_us_only` | 77.2% (n=8890) | 90.4% (n=8386) | 100.0% (n=7126) | 100.0% (n=5866) |
| `70_30__NB1_factor40` | 73.7% (n=7087) | 86.3% (n=6583) | 97.1% (n=5323) | 100.0% (n=4063) |
| `70_30__NB2_factor30` | 73.6% (n=7087) | 86.3% (n=6583) | 97.1% (n=5323) | 100.0% (n=4063) |
| `70_30__NB3_avnm_only` | 71.8% (n=7287) | 86.3% (n=6783) | 97.1% (n=5523) | 100.0% (n=4263) |
| `60_40__NB1_factor40` | 66.3% (n=7087) | 73.6% (n=6583) | 80.3% (n=5323) | 93.7% (n=4063) |
| `60_40__NB2_factor30` | 66.4% (n=7087) | 73.6% (n=6583) | 80.0% (n=5323) | 93.3% (n=4063) |
| `55_45__NB1_factor40` | 62.7% (n=7087) | 64.3% (n=6583) | 71.5% (n=5323) | 86.8% (n=4063) |
| `60_40__NB3_avnm_only` | 64.5% (n=7287) | 73.0% (n=6783) | 79.9% (n=5523) | 92.0% (n=4263) |
| `55_45__NB2_factor30` | 62.7% (n=7087) | 64.1% (n=6583) | 71.3% (n=5323) | 86.7% (n=4063) |
| `55_45__NB3_avnm_only` | 61.0% (n=7287) | 62.7% (n=6783) | 71.9% (n=5523) | 86.4% (n=4263) |

## % rolling-windows beating VT

| config | 3y | 5y | 10y | 15y |
|---|---:|---:|---:|---:|
| `B4_us_only` | 84.9% (n=8890) | 97.0% (n=8386) | 100.0% (n=7126) | 100.0% (n=5866) |
| `70_30__NB1_factor40` | 87.2% (n=7087) | 97.6% (n=6583) | 100.0% (n=5323) | 100.0% (n=4063) |
| `70_30__NB2_factor30` | 86.9% (n=7087) | 97.7% (n=6583) | 100.0% (n=5323) | 100.0% (n=4063) |
| `70_30__NB3_avnm_only` | 86.2% (n=7287) | 97.8% (n=6783) | 100.0% (n=5523) | 100.0% (n=4263) |
| `60_40__NB1_factor40` | 88.5% (n=7087) | 97.6% (n=6583) | 100.0% (n=5323) | 100.0% (n=4063) |
| `60_40__NB2_factor30` | 88.4% (n=7087) | 97.6% (n=6583) | 100.0% (n=5323) | 100.0% (n=4063) |
| `55_45__NB1_factor40` | 87.4% (n=7087) | 97.5% (n=6583) | 100.0% (n=5323) | 100.0% (n=4063) |
| `60_40__NB3_avnm_only` | 87.7% (n=7287) | 97.8% (n=6783) | 100.0% (n=5523) | 100.0% (n=4263) |
| `55_45__NB2_factor30` | 87.4% (n=7087) | 97.5% (n=6583) | 100.0% (n=5323) | 100.0% (n=4063) |
| `55_45__NB3_avnm_only` | 86.8% (n=7287) | 97.6% (n=6783) | 100.0% (n=5523) | 100.0% (n=4263) |

## Configs (US/non-US weight breakdown)

### `B4_us_only`

```json
{
  "NTSXSIM": 0.25,
  "GDESIM": 0.25,
  "RSSTSIM": 0.25,
  "ZROZSIM": 0.25
}
```

### `70_30__NB1_factor40`

```json
{
  "NTSXSIM": 0.175,
  "GDESIM": 0.175,
  "RSSTSIM": 0.175,
  "ZROZSIM": 0.175,
  "AVNMSIM": 0.18,
  "AVDVSIM": 0.042,
  "IDMOSIM": 0.042,
  "AVEMSIM": 0.036
}
```

### `70_30__NB2_factor30`

```json
{
  "NTSXSIM": 0.175,
  "GDESIM": 0.175,
  "RSSTSIM": 0.175,
  "ZROZSIM": 0.175,
  "AVNMSIM": 0.21,
  "AVDVSIM": 0.0315,
  "IDMOSIM": 0.0315,
  "AVEMSIM": 0.027
}
```

### `70_30__NB3_avnm_only`

```json
{
  "NTSXSIM": 0.175,
  "GDESIM": 0.175,
  "RSSTSIM": 0.175,
  "ZROZSIM": 0.175,
  "AVNMSIM": 0.3
}
```

### `60_40__NB1_factor40`

```json
{
  "NTSXSIM": 0.15,
  "GDESIM": 0.15,
  "RSSTSIM": 0.15,
  "ZROZSIM": 0.15,
  "AVNMSIM": 0.24,
  "AVDVSIM": 0.05600000000000001,
  "IDMOSIM": 0.05600000000000001,
  "AVEMSIM": 0.048
}
```

### `60_40__NB2_factor30`

```json
{
  "NTSXSIM": 0.15,
  "GDESIM": 0.15,
  "RSSTSIM": 0.15,
  "ZROZSIM": 0.15,
  "AVNMSIM": 0.27999999999999997,
  "AVDVSIM": 0.042,
  "IDMOSIM": 0.042,
  "AVEMSIM": 0.036
}
```

### `55_45__NB1_factor40`

```json
{
  "NTSXSIM": 0.1375,
  "GDESIM": 0.1375,
  "RSSTSIM": 0.1375,
  "ZROZSIM": 0.1375,
  "AVNMSIM": 0.27,
  "AVDVSIM": 0.06300000000000001,
  "IDMOSIM": 0.06300000000000001,
  "AVEMSIM": 0.054
}
```

### `60_40__NB3_avnm_only`

```json
{
  "NTSXSIM": 0.15,
  "GDESIM": 0.15,
  "RSSTSIM": 0.15,
  "ZROZSIM": 0.15,
  "AVNMSIM": 0.4
}
```

### `55_45__NB2_factor30`

```json
{
  "NTSXSIM": 0.1375,
  "GDESIM": 0.1375,
  "RSSTSIM": 0.1375,
  "ZROZSIM": 0.1375,
  "AVNMSIM": 0.315,
  "AVDVSIM": 0.04725,
  "IDMOSIM": 0.04725,
  "AVEMSIM": 0.0405
}
```

### `55_45__NB3_avnm_only`

```json
{
  "NTSXSIM": 0.1375,
  "GDESIM": 0.1375,
  "RSSTSIM": 0.1375,
  "ZROZSIM": 0.1375,
  "AVNMSIM": 0.45
}
```

## INCOMPLETE flags

- AVNM synth: ~78% VEASIM + ~22% VWOSIM + 60bps blended tilt premium (Avantis multi-factor screens proprietary; static premium is conservative midpoint).
- AVDV/AVEM tilt premiums (100/125bps) injected via flat annual drag; real Avantis ER + tilt may differ by regime.
- IDMO: real ETF history (2018-09+) used directly; synth path uses VEASIM + 0.6×US-UMD as proxy for intl momentum (US UMD ≠ intl momentum exactly).
- VWOSIM bottleneck: 1994+, so per-config window narrows when AVEM/AVNM/AVDV present.
- IDMO real ETF window: 2018-09+ (7.6y); rolling 10y/15y windows return n/a.

## Lesson

(Append after manual review.)
