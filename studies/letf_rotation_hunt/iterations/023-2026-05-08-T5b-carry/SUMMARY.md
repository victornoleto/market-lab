# 023-2026-05-08-T5b-carry — SUMMARY

**Tier:** T5b
**Hypothesis:** Per-asset carry forecast (Carver ch.9). Tests if (a) carry_only delivers
signal independent of EWMAC and (b) ewmac_carry composite (FDM=1.41)
outperforms EWMAC alone via diversified forecasts.

**Primary citation:** [systematic_trading, ch.9 p.180-190]; spec §2.6 T5b; T5-expansion §3.1
**Engine SHA:** `e7c432a`
**Datetime UTC:** 2026-05-08T14:24:05.957302+00:00
**Configs tested:** 4

## TL;DR

Best config: **`ewmac_carry_multi4_sigma025`** (PROMISING, score 72.5/100). lh_56y: Sortino 1.0673 (primary), Sharpe 0.752 (secondary), CAGR 18.66%, MDD -53.2%. **KILL T5-expansion:** FIRES (Sortino threshold 1.272).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `carry_only_qld_sigma025` | ? | ZROZ | ? | ? |
| `ewmac_carry_qld_sigma025` | ? | ZROZ | ? | ? |
| `carry_only_multi4_sigma025` | ? | ZROZ | ? | ? |
| `ewmac_carry_multi4_sigma025` | ? | ZROZ | ? | ? |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `carry_only_qld_sigma025` | 0.468 | 0.468 | 0.422 | 0.443 | 8.18% | 8.18% | 7.28% | 7.23% | -59.8% | -59.8% | -59.8% | -59.8% |
| `ewmac_carry_qld_sigma025` | 0.493 | 0.493 | 0.447 | 0.560 | 9.26% | 9.26% | 8.34% | 10.97% | -55.7% | -55.7% | -55.7% | -55.7% |
| `carry_only_multi4_sigma025` | 0.653 | 0.650 | 0.629 | 0.729 | 14.08% | 13.51% | 13.53% | 15.39% | -62.9% | -62.9% | -62.9% | -62.9% |
| `ewmac_carry_multi4_sigma025` | 0.752 | 0.741 | 0.784 | 1.043 | 18.66% | 18.15% | 20.92% | 29.30% | -53.2% | -53.2% | -53.2% | -46.5% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `carry_only_qld_sigma025` | 0.214 | 0.0865 | 3/8 >SPY (MDD 53% warn) | -0.013 | -0.183 | 0.034 | 0.00pp | NEAR_FAIL |
| `ewmac_carry_qld_sigma025` | 0.214 | 0.0690 | 4/8 >SPY (MDD 55% warn) | 0.177 | -0.005 | 0.063 | 0.00pp | NEAR_FAIL |
| `carry_only_multi4_sigma025` | 0.214 | 0.0009 | 5/8 >SPY (MDD 63% warn) | 0.346 | -0.079 | 0.307 | 0.00pp | MARGINAL |
| `ewmac_carry_multi4_sigma025` | 0.214 | 0.0001 | 6/8 >SPY (MDD 53% warn) | 0.924 | 0.933 | 0.401 | 0.00pp | PROMISING |

Hard-gate thresholds (spec §3.5): G1 PBO < 0.50, G2 DSR p < 0.05, G3 ≥5/8 windows + MDD < 50%, G4/G5 Sharpe > 0, G6 99% CI low > 0, G7 |Δ| ≤ 3pp.

## Plots

- `plots/01_equity_curves.png` — log-scale equity per config + SPY benchmark
- `plots/02_drawdown_curves.png` — peak-to-trough drawdown
- `plots/03_rolling_sharpe_5y.png` — 5y rolling Sharpe
- `plots/04_rolling_cagr_3y.png` — 3y rolling CAGR
- `plots/05_regime_attribution.png` — % of time signal=ON per config
- `plots/06_pct_beat_spy.png` — cumulative fraction of 3y windows where config beat SPY
- `plots/07_crisis_attribution.png` — MDD per crisis window vs SPY

## Tables

- `tables/per_config_metrics.csv` — one row per (config, dataset)
- `tables/gates_pass_fail.csv` — gate values + pass/fail flags

## Verdict

- **Best config:** `ewmac_carry_multi4_sigma025` (PROMISING, score 72.5)
- **KILL T5-expansion:** FIRES (Sortino 1.0673 < 1.272)
- **Advance to next tier:** no
- **Cumulative n_trials:** 415
- **Deploy escalation eligible:** no

## Conclusion

Carry improves the Carver family but not enough to displace T3d. The best carry composite remains below the Sortino threshold, so carry is useful diagnostic evidence rather than a winner.

## Next iter
