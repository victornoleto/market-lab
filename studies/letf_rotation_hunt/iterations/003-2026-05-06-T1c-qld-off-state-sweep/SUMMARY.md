# 003-2026-05-06-T1c-qld-off-state-sweep — SUMMARY

**Tier:** T1c
**Hypothesis:** QLD SMA200 rotation OFF-state: BIL is reference. Leveraged OFF (TMF) only wins if Sharpe > BIL_OFF + 0.10 AND MDD ≤ TMF_buy-hold_MDD/2. Treasury duration (IEF/TLT/ZROZ/EDV) tested for crisis-alpha contribution.
**Primary citation:** [leverage_for_the_long_run, p.17 Table 8 (BIL OFF baseline); ilmanen_expected_returns, ch.19 (treasury crisis-alpha)]
**Engine SHA:** `ad8bab2`
**Datetime UTC:** 2026-05-06T18:10:29.683689+00:00
**Configs tested:** 6

## TL;DR

Best config: **`qld_sma200_off_zroz`** (PROMISING, score 67.5/100). lh_56y: Sharpe 0.752 (edge vs SPY +0.070), CAGR 23.43%, MDD -75.0%.  **KILL T0:** PASS (threshold: T1-best Sharpe ≥ SPY+0.05 = 0.732).

## Configs tested

| Name | on_asset | off_asset | signal | period |
|------|---------|----------|--------|-------:|
| `qld_sma200_off_bil` | QLD | BIL | sma | 200 |
| `qld_sma200_off_ief` | QLD | IEF | sma | 200 |
| `qld_sma200_off_tlt` | QLD | TLT | sma | 200 |
| `qld_sma200_off_tmf` | QLD | TMF | sma | 200 |
| `qld_sma200_off_zroz` | QLD | ZROZ | sma | 200 |
| `qld_sma200_off_edv` | QLD | EDV | sma | 200 |

## Results — gross metrics per dataset

| Config | lh_56y Sharpe | modern_1990 Sharpe | spy_real Sharpe | ndx_real Sharpe | lh_56y CAGR | modern_1990 CAGR | spy_real CAGR | ndx_real CAGR | lh_56y MDD | modern_1990 MDD | spy_real MDD | ndx_real MDD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `qld_sma200_off_bil` | 0.678 | 0.687 | 0.816 | 0.904 | 18.63% | 19.34% | 21.78% | 25.24% | -75.6% | -75.6% | -44.5% | -44.5% |
| `qld_sma200_off_ief` | 0.724 | 0.718 | 0.829 | 0.897 | 20.61% | 20.73% | 22.53% | 25.15% | -75.0% | -75.0% | -44.3% | -44.3% |
| `qld_sma200_off_tlt` | 0.719 | 0.699 | 0.799 | 0.854 | 20.74% | 20.25% | 22.11% | 24.21% | -75.3% | -75.3% | -47.7% | -47.7% |
| `qld_sma200_off_tmf` | 0.683 | 0.627 | 0.638 | 0.640 | 21.84% | 19.04% | 19.40% | 18.98% | -78.9% | -78.9% | -78.9% | -78.9% |
| `qld_sma200_off_zroz` | 0.752 | 0.695 | 0.771 | 0.812 | 23.43% | 20.88% | 22.31% | 23.50% | -75.0% | -75.0% | -54.7% | -54.7% |
| `qld_sma200_off_edv` | 0.719 | 0.699 | 0.799 | 0.854 | 20.74% | 20.25% | 22.11% | 24.21% | -75.3% | -75.3% | -47.7% | -47.7% |

**SPY anchor (lh_56y):** Sharpe 0.682, MDD -55.1% (mandate §2.2/§2.3 — MDD warning-only).

## Gates per config

| Config | G1 PBO | G2 DSR p (local) | G3 WF | G4 OOS S | G5 FWD S | G6 99% low | G7 Δ pp | Tier |
|--------|-------:|-----------------:|------:|---------:|---------:|-----------:|--------:|------|
| `qld_sma200_off_bil` | 0.607 | 0.0015 | 7/8 >SPY (MDD 76% warn) | 0.947 | 0.936 | 0.296 | 0.00pp | MARGINAL |
| `qld_sma200_off_ief` | 0.607 | 0.0006 | 7/8 >SPY (MDD 75% warn) | 0.939 | 0.870 | 0.350 | 0.00pp | PROMISING |
| `qld_sma200_off_tlt` | 0.607 | 0.0006 | 7/8 >SPY (MDD 75% warn) | 0.887 | 0.755 | 0.350 | 0.00pp | MARGINAL |
| `qld_sma200_off_tmf` | 0.607 | 0.0013 | 6/8 >SPY (MDD 79% warn) | 0.655 | 0.357 | 0.322 | 0.00pp | MARGINAL |
| `qld_sma200_off_zroz` | 0.607 | 0.0003 | 6/8 >SPY (MDD 75% warn) | 0.833 | 0.652 | 0.389 | 0.00pp | PROMISING |
| `qld_sma200_off_edv` | 0.607 | 0.0006 | 7/8 >SPY (MDD 75% warn) | 0.887 | 0.755 | 0.350 | 0.00pp | MARGINAL |

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

- **Best config:** `qld_sma200_off_zroz` (PROMISING, score 67.5)
- **KILL T0:** PASS (study viable)
- **Advance to next tier:** yes
- **Cumulative n_trials:** 22
- **Deploy escalation eligible:** no

## Conclusion

T1-best Sharpe 0.752 (lh_56y) clears SPY+0.05 — single-LETF Gayed rotation has prima-facie edge in this universe. Proceeding to T1b period sweep.

## Next iter

**T2** — HFEA-binary basket per spec §2.3.
